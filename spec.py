import streamlit as st
import pandas as pd
import os
import base64
import gspread
from google.oauth2.service_account import Credentials

# 1. 경로 설정
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# 2. Secrets 및 상수 설정
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin1234")
SHEET_ID       = st.secrets.get("SHEET_ID", "")
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
NC_COLS = ["NO", "접수일", "고객사", "이슈유형", "제품규격", "생산라인",
           "생산일", "출고일", "출고수량", "출고중량(kg)",
           "클레임수량", "클레임중량(kg)", "손실비용(원)", "이슈상세", "원인", "조치대책"]
NC_NUM_COLS  = ["출고수량", "출고중량(kg)", "클레임수량", "클레임중량(kg)", "손실비용(원)"]

st.set_page_config(page_title="고객사양서 - 품질기술팀", page_icon="📋", layout="wide")

# 3. 세션 상태 초기화
for k, v in {"is_admin": False, "edit_idx": None, "show_add_form": False,
             "nc_edit_idx": None, "nc_show_add": False, "nc_sel_idx": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Google Sheets 연결 ────────────────────────────────────────────
def get_gsheet(sheet_index=0):
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPE)
    return gspread.authorize(creds).open_by_key(SHEET_ID).get_worksheet(sheet_index)

# ── 탭1: 고객사 데이터 처리 ─────────────────────────────────────────
@st.cache_data(ttl=300)
def load_customer_data():
    try:
        df = pd.DataFrame(get_gsheet(0).get_all_records())
        if df.empty:
            return df
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0].astype(str).str.strip() != ""]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"고객사 데이터 로드 오류: {e}")
        return None

def save_customer_data(df):
    try:
        sh = get_gsheet(0)
        sh.clear()
        sh.update([df.columns.tolist()] + df.fillna("").values.tolist())
        load_customer_data.clear()
        return True
    except Exception as e:
        st.error(f"저장 오류: {e}")
        return False

# ── 탭4: 부적합관리 데이터 처리 ──────────────────────────────────────
@st.cache_data(ttl=300)
def load_nc_data():
    try:
        sh = get_gsheet(1)
        all_vals = sh.get_all_values()
        if not all_vals or len(all_vals) < 2:
            return pd.DataFrame(columns=NC_COLS)
        
        # 헤더 판별 로직
        first_row = all_vals[0]
        if any(str(v).strip().isdigit() for v in first_row[:3]):
            data_rows = all_vals
        else:
            data_rows = all_vals[1:]
            
        n = len(NC_COLS)
        normalized = [r[:n] + [""] * max(0, n - len(r)) for r in data_rows]
        df = pd.DataFrame(normalized, columns=NC_COLS)
        df = df[df["NO"].astype(str).str.match(r"^\d+$", na=False)].copy()
        df["NO"] = df["NO"].astype(int)
        
        for col in NC_NUM_COLS:
            df[col] = df[col].astype(str).str.replace(",", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"부적합관리 로드 오류: {e}")
        return None

def save_nc_data(df):
    try:
        sh = get_gsheet(1)
        save_df = df.copy()
        for col in save_df.columns:
            save_df[col] = save_df[col].fillna("").astype(str)
            save_df[col] = save_df[col].replace(["nan", "NaT", "<NA>"], "")
        rows = [save_df.columns.tolist()] + save_df.values.tolist()
        sh.clear()
        sh.update(rows)
        load_nc_data.clear()
        return True
    except Exception as e:
        st.error(f"저장 오류: {e}")
        return False

def nc_df_set_row(df, idx, updated_dict):
    for col in df.columns:
        df[col] = df[col].astype(object)
    for col, val in updated_dict.items():
        df.at[idx, col] = val
    df["NO"] = pd.to_numeric(df["NO"], errors="coerce").fillna(0).astype(int)
    for col in NC_NUM_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# ── 유틸리티 ──────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        st.error(f"이미지 로드 오류: {e}")
        return None

def fmt_num(val, unit=""):
    try:
        if pd.isna(val): return "-"
        n = float(val)
        if n == int(n): return f"{int(n):,}{unit}"
        return f"{n:,.1f}{unit}"
    except:
        s = str(val).strip()
        return s if s not in ("nan", "", "None") else "-"

def safe_str(val):
    s = str(val).strip()
    return s if s not in ("nan", "None", "") else "-"

def normalize_search(text):
    return str(text).replace(" ", "").lower()

def nc_search_match(row, query):
    q = normalize_search(query)
    targets = ["고객사", "이슈유형", "제품규격", "생산라인", "이슈상세", "원인", "조치대책", "접수일", "생산일", "출고일"]
    return any(q in normalize_search(str(row[c])) for c in targets)

# ── 품질보증 테이블 생성 ─────────────────────────────────────────────
def build_standard_table():
    td = "padding:8px 12px;border:1px solid #DEE2E6;text-align:center;vertical-align:middle;background:white;color:#000;font-size:12px;white-space:pre-wrap;"
    th = "padding:8px 12px;border:1px solid #DEE2E6;text-align:center;vertical-align:middle;background:#F8F9FA;color:#000;font-weight:bold;font-size:12px;"
    def c(content, rs=1, cs=1):
        r = f' rowspan="{rs}"' if rs > 1 else ""
        s = f' colspan="{cs}"' if cs > 1 else ""
        return f'<td style="{td}"{r}{s}>{content}</td>'
    rows = [
        f"<tr><th style='{th}'>구분</th><th style='{th}'>항목</th><th style='{th}'>사내 검사 기준</th><th style='{th}'>KS 검사 기준</th></tr>",
        "<tr>" + c("겉모양", rs=2) + c("외관 상태") + c("사용상 해로운 결점이 없어야 한다.") + c("사용상 해로운 결점이 없어야 한다.", rs=2) + "</tr>",
        "<tr>" + c("마킹") + c("수요가 요청한 마킹 준수") + "</tr>",
        "<tr>" + c("용접", rs=2) + c("편평시험") + c("외경 대비 80%이상 누를것") + c("KS 평균 수준: 외경 대비: 30%이상 누를것", rs=2) + "</tr>",
        "<tr>" + c("용접 위치") + c("가구용 : 모서리 2mm이내") + "</tr>",
        "<tr>" + c("치수", rs=17) + c("외경", rs=8) + c("각형관") + c("각형관 KS D3568 기준") + "</tr>",
        "<tr>" + c("100mm 미만: ±0.25 mm") + c("100mm 미만: ±1.5mm") + "</tr>",
        "<tr>" + c("100mm 초과: ± 0.5mm") + c("100mm 초과: ±1.5%", rs=2) + "</tr>",
        "<tr>" + c("※ 가구용: ±0.1mm") + "</tr>",
        "<tr>" + c("") + c("") + "</tr>",
        "<tr>" + c("원형관\n(강제전선관 제외)") + c("원형관 KS D3566 기준") + "</tr>",
        "<tr>" + c("50mm 미만: ±0.25 mm") + c("50mm 미만: ±0.25 mm") + "</tr>",
        "<tr>" + c("50mm 이상: ±0.5 mm") + c("50mm 이상: ±0.5%") + "</tr>",
        "<tr>" + c("요철", rs=2) + c("100mm 미만: ±1.0mm") + c("100mm 미만: ±1.5mm") + "</tr>",
        "<tr>" + c("100mm 초과: ±1.5mm") + c("100mm 초과: ±1.5%") + "</tr>",
        "<tr>" + c("직진도", rs=2) + c("전체 길이의 0.15% 이내\n(6000mm 기준 9mm 이하)") + c("전체 길이의 0.3% 이내\n(6000mm 기준 18mm 이하)", rs=2) + "</tr>",
        "<tr>" + c("1.8t 미만: 2 t 이하\n(예:1.8x2=3.6R 이하)") + "</tr>",
        "<tr>" + c("R값", rs=2) + c("1.8t 이상: 2.5 t 이하") + c("3 t 이하", rs=2) + "</tr>",
        "<tr>" + c("가구용: 2.0R 이하") + "</tr>",
        "<tr>" + c("각도") + c("±1.0˚") + c("±1.5˚") + "</tr>",
        "<tr>" + c("길이", rs=2) + c("각관: +3mm ~ +10mm") + c("주문 길이 이상 일것", rs=2) + "</tr>",
        "<tr>" + c("원형관: +5mm ~ +20mm") + "</tr>",
    ]
    return f"<div class='qc-table-wrapper notranslate' translate='no'><table class='qc-table' style='border-collapse:collapse;width:100%;'><thead>{rows[0]}</thead><tbody>{''.join(rows[1:])}</tbody></table></div>"

logo_base64 = get_image_base64(os.path.join(BASE_DIR, "hanjin_logo.png"))

# ── 디자인 (CSS) ──────────────────────────────────────────────────
st.markdown("""
<style>
.header-wrapper{display:flex;justify-content:space-between;align-items:flex-end;width:100%;padding:10px 0;border-bottom:1px solid #f0f2f6;margin-bottom:20px;}
.brand-logo{height:65px;width:auto;}
.team-name-fixed{font-size:14px;font-weight:600;color:rgba(0,0,0,0.5);margin-bottom:5px;}
.main-title{color:#FF8C00!important;font-weight:800;font-size:1.85rem;}
.customer-title{color:#FF7F50!important;font-weight:bold;font-size:1.45rem;margin-top:30px;margin-bottom:15px;}
.admin-badge{background:#FF8C00;color:white;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:bold;margin-left:10px;}
.qc-table-wrapper{overflow-x:auto;-webkit-overflow-scrolling:touch;width:100%;}
.qc-table{border-collapse:collapse;margin-top:10px;font-size:clamp(10px,2.2vw,12px);border:1px solid #DEE2E6;table-layout:auto;width:100%;}
.qc-table th{padding:clamp(4px,1.5vw,8px) clamp(6px,2vw,12px);border:1px solid #DEE2E6;text-align:center!important;vertical-align:middle!important;background-color:#F8F9FA!important;color:#000!important;font-weight:bold!important;}
.qc-table td{padding:clamp(4px,1.5vw,8px) clamp(6px,2vw,12px);border:1px solid #DEE2E6;text-align:center!important;vertical-align:middle!important;background-color:white!important;color:#000!important;}
.nc-card{border:1px solid #DEE2E6;border-radius:10px;padding:12px 16px;margin-bottom:4px;background:white;cursor:pointer;transition:box-shadow 0.15s;}
.nc-card:hover{box-shadow:0 2px 10px rgba(0,0,0,0.08);}
.nc-card-selected{border-color:#FF8C00!important;border-width:2px!important;box-shadow:0 2px 10px rgba(255,140,0,0.25)!important;}
.nc-badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:bold;background:#FFF3E0;color:#E65100;margin-right:4px;}
.nc-badge-line{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:bold;background:#E8F5E9;color:#2E7D32;margin-right:4px;}
.nc-detail-box{background:white;border:1px solid #DEE2E6;border-radius:10px;overflow:hidden;margin:8px 0 16px 0;}
.nc-detail-row{display:flex;border-bottom:1px solid #F0F0F0;}
.nc-detail-label{background:#F8F9FA;width:95px;min-width:95px;padding:9px 6px;font-weight:bold;color:#495057;border-right:1px solid #DEE2E6;display:flex;align-items:center;justify-content:center;text-align:center;font-size:11px;line-height:1.3;word-break:keep-all;}
.nc-detail-value{flex:1;padding:9px 12px;background:white;font-size:13px;line-height:1.6;color:#212529;word-break:break-all;white-space:pre-wrap;}
.nc-loss{color:#E63946;font-weight:bold;}
.footer-note{font-size:12.5px;color:#666;margin-top:15px;font-weight:500;}
.guide-text{display:none;}
@media(max-width:768px){
  .guide-text{display:block;font-size:15px;font-weight:bold;color:#333;margin:15px 0;padding:15px;background:#fff4e6;border-radius:8px;border-left:5px solid #FF8C00;line-height:1.4;}
  .nc-detail-label{width:75px;min-width:75px;font-size:10px;}
}
</style>
""", unsafe_allow_html=True)

# ── 공통 UI 렌더링 ─────────────────────────────────────────────────
def render_header():
    logo = f"<img src='data:image/png;base64,{logo_base64}' class='brand-logo'>" if logo_base64 else "<span style='color:#ccc;font-size:12px;'>[로고 미검출]</span>"
    badge = "<span class='admin-badge'>🔓 관리자 모드</span>" if st.session_state.is_admin else ""
    st.markdown(f"<div class='header-wrapper'><div>{logo}</div><div class='team-name-fixed'>품질기술팀{badge}</div></div>", unsafe_allow_html=True)

def render_admin_login():
    st.sidebar.markdown("---")
    if not st.session_state.is_admin:
        auto_key = st.query_params.get("auto_admin", "")
        if auto_key == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.rerun()
        with st.sidebar.expander("🔐 관리자 로그인"):
            pw = st.text_input("비밀번호", type="password", key="admin_pw_input")
            remember = st.checkbox("자동 로그인 설정", key="admin_remember")
            if st.button("로그인", key="admin_login_btn") or (pw == ADMIN_PASSWORD and st.session_state.get("_pw_enter") != pw):
                if pw == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    if remember: st.query_params["auto_admin"] = ADMIN_PASSWORD
                    st.session_state["_pw_enter"] = pw
                    st.rerun()
                elif pw: st.error("비밀번호가 틀렸습니다.")
    else:
        if st.sidebar.button("🔒 관리자 로그아웃"):
            for k in ["is_admin", "edit_idx", "show_add_form", "nc_edit_idx", "nc_show_add", "nc_sel_idx"]:
                st.session_state[k] = False if k == "is_admin" else None
            if "auto_admin" in st.query_params: del st.query_params["auto_admin"]
            st.rerun()

# ── 탭1 렌더링 ────────────────────────────────────────────────────
def render_add_form(df):
    st.markdown("### ➕ 고객사 추가")
    cols = df.columns.tolist()
    new_values = {}
    for pair in [cols[i:i+2] for i in range(0, len(cols), 2)]:
        fcols = st.columns(2)
        for j, cn in enumerate(pair):
            new_values[cn] = fcols[j].text_input(cn, key=f"add_{cn}")
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="add_save"):
        if not new_values.get(cols[0], "").strip(): st.error("고객사명은 필수 입력입니다.")
        else:
            updated = pd.concat([df, pd.DataFrame([new_values])], ignore_index=True)
            if save_customer_data(updated):
                st.session_state.show_add_form = False
                st.success(f"'{new_values[cols[0]]}' 고객사가 추가되었습니다!"); st.rerun()
    if c2.button("취소", key="add_cancel"):
        st.session_state.show_add_form = False; st.rerun()

def render_edit_form(df, idx):
    row = df.iloc[idx]
    st.markdown(f"### 수정 중: {row.iloc[0]}")
    cols = df.columns.tolist()
    updated_values = {}
    for pair in [cols[i:i+2] for i in range(0, len(cols), 2)]:
        fcols = st.columns(2)
        for j, cn in enumerate(pair):
            cur = str(row[cn]) if str(row[cn]) not in ("", "nan") else ""
            updated_values[cn] = fcols[j].text_input(cn, value=cur, key=f"edit_{cn}")
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="edit_save"):
        for cn, val in updated_values.items(): df.at[idx, cn] = val
        if save_customer_data(df):
            st.session_state.edit_idx = None
            st.success("수정이 완료되었습니다!"); st.rerun()
    if c2.button("취소", key="edit_cancel"):
        st.session_state.edit_idx = None; st.rerun()

# ── 탭4 렌더링 ────────────────────────────────────────────────────
def render_nc_detail(row, idx, df_nc):
    def dr(label, value, loss=False):
        v_cls = " nc-loss" if loss else ""
        return f"<div class='nc-detail-row'><div class='nc-detail-label'>{label}</div><div class='nc-detail-value{v_cls}'>{safe_str(value)}</div></div>"
    html = f"<div class='nc-detail-box'>{dr('NO', int(row['NO']))}{dr('접수일', row['접수일'])}{dr('고객사', row['고객사'])}{dr('이슈유형', f'<span class=nc-badge>{safe_str(row[3])}</span>')}{dr('제품규격', row[4])}{dr('생산라인', f'<span class=nc-badge-line>{safe_str(row[5])}</span>')}{dr('생산일', row[6])}{dr('출고일', row[7])}{dr('출고수량', fmt_num(row[8], '본'))}{dr('출고중량', fmt_num(row[9], ' kg'))}{dr('클레임수량', fmt_num(row[10], '본'))}{dr('클레임중량', fmt_num(row[11], ' kg'))}{dr('손실비용', fmt_num(row[12], ' 원'), loss=True)}{dr('이슈상세', safe_str(row[13]).replace('\\n', '<br>'))}{dr('원인', safe_str(row[14]).replace('\\n', '<br>'))}{dr('조치대책', safe_str(row[15]).replace('\\n', '<br>'))}</div>"
    st.markdown(html, unsafe_allow_html=True)
    if st.session_state.is_admin:
        a1, a2 = st.columns([1, 1])
        if a1.button("✏️ 수정", key=f"nc_edit_btn_{idx}"):
            st.session_state.nc_edit_idx = idx; st.session_state.nc_sel_idx = None; st.rerun()
        if a2.button("🗑️ 삭제", key=f"nc_del_btn_{idx}"):
            st.session_state[f"nc_confirm_del_{idx}"] = True
        if st.session_state.get(f"nc_confirm_del_{idx}", False):
            st.warning(f"**NO.{int(row['NO'])} - {safe_str(row['고객사'])}** 를 정말 삭제하시겠습니까?")
            d1, d2 = st.columns([1, 5])
            if d1.button("확인 삭제", key=f"nc_confirm_del_btn_{idx}"):
                updated = df_nc.drop(index=idx).reset_index(drop=True)
                if save_nc_data(updated): st.success("삭제되었습니다."); st.rerun()
            if d2.button("취소", key=f"nc_cancel_del_btn_{idx}"):
                st.session_state[f"nc_confirm_del_{idx}"] = False; st.rerun()

def render_nc_add_form(df):
    st.markdown("### ➕ 부적합 이력 추가")
    new_no = int(df["NO"].max()) + 1 if not df.empty else 1
    new_vals = {"NO": new_no}
    st.markdown("**기본 정보**")
    c1, c2, c3 = st.columns(3)
    new_vals["접수일"] = c1.text_input("접수일 (YYYY-MM-DD)", key="nc_add_접수일")
    new_vals["생산일"] = c2.text_input("생산일 (YYYY-MM-DD)", key="nc_add_생산일")
    new_vals["출고일"] = c3.text_input("출고일 (YYYY-MM-DD)", key="nc_add_출고일")
    c1, c2, c3, c4 = st.columns(4)
    new_vals["고객사"]=c1.text_input("고객사",key="nc_add_고객사"); new_vals["이슈유형"]=c2.text_input("이슈유형",key="nc_add_이슈유형")
    new_vals["제품규격"]=c3.text_input("제품규격",key="nc_add_제품규격"); new_vals["생산라인"]=c4.text_input("생산라인",key="nc_add_생산라인")
    st.markdown("**수량 / 손실**")
    c1, c2, c3, c4, c5 = st.columns(5)
    new_vals["출고수량"]=c1.text_input("출고수량",key="nc_add_출고수량"); new_vals["출고중량(kg)"]=c2.text_input("출고중량(kg)",key="nc_add_출고중량")
    new_vals["클레임수량"]=c3.text_input("클레임수량",key="nc_add_클레임수량"); new_vals["클레임중량(kg)"]=c4.text_input("클레임중량(kg)",key="nc_add_클레임중량")
    new_vals["손실비용(원)"]=c5.text_input("손실비용(원)",key="nc_add_손실비용")
    st.markdown("**상세 내용**")
    new_vals["이슈상세"]=st.text_area("이슈상세",height=100,key="nc_add_이슈상세"); new_vals["원인"]=st.text_area("원인",height=80,key="nc_add_원인"); new_vals["조치대책"]=st.text_area("조치대책",height=80,key="nc_add_조치대책")
    b1, b2 = st.columns([1, 5])
    if b1.button("저장", key="nc_add_save"):
        if not str(new_vals.get("고객사", "")).strip(): st.error("고객사는 필수 입력입니다.")
        else:
            row_data = {col: new_vals.get(col, "") for col in NC_COLS}
            new_row = pd.DataFrame([row_data])
            for col in NC_NUM_COLS: new_row[col] = pd.to_numeric(new_row[col], errors="coerce")
            updated = pd.concat([df, new_row], ignore_index=True)
            if save_nc_data(updated): st.session_state.nc_show_add = False; st.rerun()
    if b2.button("취소", key="nc_add_cancel"): st.session_state.nc_show_add = False; st.rerun()

def render_nc_edit_form(df, idx):
    row = df.iloc[idx]
    st.markdown(f"### ✏️ 수정 중: NO.{int(row['NO'])} - {safe_str(row['고객사'])}")
    updated = {}
    st.markdown("**기본 정보**")
    c1, c2, c3 = st.columns(3)
    updated["접수일"]=c1.text_input("접수일",value=safe_str(row["접수일"]),key="nc_edit_접수일")
    updated["생산일"]=c2.text_input("생산일",value=safe_str(row["생산일"]),key="nc_edit_생산일")
    updated["출고일"]=c3.text_input("출고일",value=safe_str(row["출고일"]),key="nc_edit_출고일")
    c1, c2, c3, c4 = st.columns(4)
    updated["고객사"]=c1.text_input("고객사",value=safe_str(row["고객사"]),key="nc_edit_고객사")
    updated["이슈유형"]=c2.text_input("이슈유형",value=safe_str(row["이슈유형"]),key="nc_edit_이슈유형")
    updated["제품규격"]=c3.text_input("제품규격",value=safe_str(row["제품규격"]),key="nc_edit_제품규격")
    updated["생산라인"]=c4.text_input("생산라인",value=safe_str(row["생산라인"]),key="nc_edit_생산라인")
    st.markdown("**수량 / 손실**")
    c1, c2, c3, c4, c5 = st.columns(5)
    updated["출고수량"]=c1.text_input("출고수량",value=fmt_num(row[8]).replace(",",""),key="nc_edit_출고수량")
    updated["출고중량(kg)"]=c2.text_input("출고중량(kg)",value=fmt_num(row[9]).replace(",",""),key="nc_edit_출고중량")
    updated["클레임수량"]=c3.text_input("클레임수량",value=fmt_num(row[10]).replace(",",""),key="nc_edit_클레임수량")
    updated["클레임중량(kg)"]=c4.text_input("클레임중량(kg)",value=fmt_num(row[11]).replace(",",""),key="nc_edit_클레임중량")
    updated["손실비용(원)"]=c5.text_input("손실비용(원)",value=fmt_num(row[12]).replace(",",""),key="nc_edit_손실비용")
    st.markdown("**상세 내용**")
    updated["이슈상세"]=st.text_area("이슈상세",value=safe_str(row[13]),height=100,key="nc_edit_이슈상세")
    updated["원인"]=st.text_area("원인",value=safe_str(row[14]),height=80,key="nc_edit_원인")
    updated["조치대책"]=st.text_area("조치대책",value=safe_str(row[15]),height=80,key="nc_edit_조치대책")
    b1, b2 = st.columns([1, 5])
    if b1.button("저장", key="nc_edit_save"):
        df = nc_df_set_row(df, idx, updated)
        if save_nc_data(df): st.session_state.nc_edit_idx = None; st.rerun()
    if b2.button("취소", key="nc_edit_cancel"): st.session_state.nc_edit_idx = None; st.rerun()

# ── 메인 함수 ─────────────────────────────────────────────────────
def main():
    render_header()
    st.markdown("<div class='main-title'>📋 품질 통합 관리 시스템</div>", unsafe_allow_html=True)
    
    tabs = ["📄 고객 사양서", "⚖️ 품질 보증 기준", "🏭 제강사 정보"]
    if st.session_state.is_admin: tabs.append("🚨 부적합 관리")
    
    selected_tabs = st.tabs(tabs)
    
    with selected_tabs[0]:
        df_cust = load_customer_data()
        if df_cust is not None:
            customer_list = df_cust.iloc[:, 0].tolist()
            st.sidebar.header("🏢 고객사 목록")
            if st.session_state.is_admin:
                if st.sidebar.button("➕ 고객사 추가", key="open_add_form"):
                    st.session_state.show_add_form = True; st.session_state.edit_idx = None
            sel_idx = st.sidebar.radio("업체를 선택하세요:", options=list(range(len(df_cust))), format_func=lambda i: customer_list[i], index=None, key="customer_radio")
            if sel_idx is None and not st.session_state.show_add_form and st.session_state.edit_idx is None:
                st.markdown("<div class='guide-text'>좌상단 >> 화살표를 눌러 고객사를 선택 하십시오.</div>", unsafe_allow_html=True)
            if st.session_state.is_admin and st.session_state.show_add_form: render_add_form(df_cust)
            elif st.session_state.is_admin and st.session_state.edit_idx is not None: render_edit_form(df_cust, st.session_state.edit_idx)
            elif sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown(f"<div class='customer-title'>■ {row.iloc[0]}</div>", unsafe_allow_html=True)
                if st.session_state.is_admin:
                    a1, a2, _ = st.columns([1, 1, 8])
                    if a1.button("수정", key="edit_btn"): st.session_state.edit_idx = sel_idx; st.rerun()
                    if a2.button("삭제", key="delete_btn"): st.session_state[f"confirm_delete_{sel_idx}"] = True
                    if st.session_state.get(f"confirm_delete_{sel_idx}", False):
                        st.warning(f"**'{row.iloc[0]}'** 고객사를 정말 삭제하시겠습니까?")
                        d1, d2 = st.columns([1, 5])
                        if d1.button("확인 삭제", key="confirm_del"):
                            updated = df_cust.drop(index=sel_idx).reset_index(drop=True)
                            if save_customer_data(updated): st.rerun()
                        if d2.button("취소", key="cancel_del"): st.session_state[f"confirm_delete_{sel_idx}"] = False; st.rerun()
                for i in range(1, len(row.index)):
                    col_n, raw = row.index[i], row.iloc[i]
                    val = str(raw).strip() if str(raw).strip() not in ("", "nan") else "-"
                    col_c = "#E63946" if any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"]) else "#495057"
                    st.markdown(f"<div class='notranslate' style='display:flex;border:1px solid #DEE2E6;margin-bottom:-1px;'><div style='background:#F8F9FA;width:85px;min-width:85px;padding:10px 4px;font-weight:bold;color:{col_c};border-right:1px solid #DEE2E6;display:flex;align-items:center;justify-content:center;text-align:center;font-size:12px;line-height:1.2;word-break:keep-all;'>{col_n}</div><div class='notranslate' style='flex:1;padding:10px;background:white;font-size:13.5px;line-height:1.4;color:#212529;font-weight:500;word-break:break-all;'>{val}</div></div>", unsafe_allow_html=True)
        render_admin_login()

    with selected_tabs[1]:
        st.markdown("<div class='customer-title'>⚖️ 품질 보증 표준 가이드</div>", unsafe_allow_html=True)
        st.markdown(build_standard_table(), unsafe_allow_html=True)
        st.markdown("<div class='footer-note'>※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>", unsafe_allow_html=True)

    with selected_tabs[2]:
        st.markdown("<div class='customer-title'>🏭 제강사 원산지 분류표</div>", unsafe_allow_html=True)
        mill_data = [{"코드":"PSC","제강사":"포스코","원산지":"대한민국"},{"코드":"HDS","제강사":"현대제철","원산지":"대한민국"},{"코드":"DBS","제강사":"동부제철","원산지":"대한민국"},{"코드":"DKS","제강사":"동국씨엠","원산지":"대한민국"},{"코드":"SEAH","제강사":"세아씨엠","원산지":"대한민국"},{"코드":"TKS","제강사":"도쿄","원산지":"일본"},{"코드":"NSC","제강사":"닛테츠","원산지":"일본"},{"코드":"FMS","제강사":"포모사","원산지":"베트남"},{"코드":"HOA","제강사":"호아팟","원산지":"베트남"},{"코드":"CHS","제강사":"중홍","원산지":"대만"},{"코드":"ANF","제강사":"안펑","원산지":"중국"},{"코드":"BAO","제강사":"포두","원산지":"중국"},{"코드":"JYE","제강사":"징예","원산지":"중국"},{"코드":"RSC","제강사":"일조강철","원산지":"중국"},{"코드":"AGS","제강사":"안강","원산지":"중국"},{"코드":"DGH","제강사":"동화","원산지":"중국"},{"코드":"DSH","제강사":"딩셩","원산지":"중국"},{"코드":"GUF","제강사":"국풍","원산지":"중국"},{"코드":"HAN","제강사":"한단","원산지":"중국"},{"코드":"JER","제강사":"지룬","원산지":"중국"},{"코드":"MSH","제강사":"보산","원산지":"중국"},{"코드":"SDG","제강사":"산동","원산지":"중국"},{"코드":"SDS","제강사":"승덕","원산지":"중국"},{"코드":"SGS","제강사":"수도","원산지":"중국"},{"코드":"ZHJ","제강사":"조건","원산지":"중국"},{"코드":"KGM","제강사":"카이징","원산지":"중국"},{"코드":"LYN","제강사":"롄강","원산지":"중국"},{"코드":"NTS","제강사":"신청강","원산지":"중국"},{"코드":"TNT","제강사":"천철","원산지":"중국"},{"코드":"TSS","제강사":"당산강철","원산지":"중국"},{"코드":"YAN","제강사":"연산강철","원산지":"중국"}]
        df_mill = pd.DataFrame(mill_data)
        sq = st.text_input("🔍 제강사 명칭 또는 코드 검색", placeholder="예: PSC, 포스코, 중국...", key="mill_search")
        if sq: df_mill = df_mill[df_mill.apply(lambda r: sq.lower() in r["코드"].lower() or sq in r["제강사"] or sq in r["원산지"], axis=1)]
        mill_html = "<div class='qc-table-wrapper notranslate'><table class='qc-table'><thead><tr><th>코드</th><th>제강사</th><th>원산지</th></tr></thead><tbody>"
        for _, r in df_mill.iterrows():
            os2 = " style='color:#007BFF;font-weight:bold;'" if r["원산지"] == "대한민국" else ""
            mill_html += f"<tr><td style='font-weight:bold;'>{r['코드']}</td><td>{r['제강사']}</td><td{os2}>{r['원산지']}</td></tr>"
        st.markdown(mill_html + "</tbody></table></div>", unsafe_allow_html=True)

    if st.session_state.is_admin:
        with selected_tabs[3]:
            st.markdown("<div class='customer-title'>🚨 부적합 통합 관리 대장</div>", unsafe_allow_html=True)
            df_nc = load_nc_data()
            if df_nc is not None:
                if st.session_state.nc_show_add: render_nc_add_form(df_nc); st.stop()
                if st.session_state.nc_edit_idx is not None: render_nc_edit_form(df_nc, st.session_state.nc_edit_idx); st.stop()
                col_s, col_b = st.columns([5, 1])
                search = col_s.text_input("🔍 통합 검색", placeholder="예: 백청, 조관1...", key="nc_search")
                if col_b.button("➕ 추가", key="nc_add_btn"): st.session_state.nc_show_add = True; st.rerun()
                df_view = df_nc.copy()
                if search: df_view = df_view[df_view.apply(lambda r: nc_search_match(r, search), axis=1)]
                if df_view.empty: st.info("검색 결과가 없습니다.")
                else:
                    total_loss = pd.to_numeric(df_view["손실비용(원)"], errors="coerce").sum()
                    st.markdown(f"<div style='display:flex;justify-content:space-between;'><b>총 {len(df_view)}건</b><b style='color:#E63946;'>손실 합계: {fmt_num(total_loss, ' 원')}</b></div>", unsafe_allow_html=True)
                    st.markdown("---")
                    for orig_idx, row in df_view.iterrows():
                        is_sel = (st.session_state.nc_sel_idx == orig_idx)
                        card_class = "nc-card nc-card-selected" if is_sel else "nc-card"
                        st.markdown(f"<div class='{card_class}'><div style='display:flex;justify-content:space-between;'><div><span style='font-weight:bold;'>NO.{int(row['NO'])}</span> <span class='nc-badge'>{safe_str(row[3])}</span> <span class='nc-badge-line'>{safe_str(row[5])}</span></div><div style='color:#E63946;font-weight:bold;'>{fmt_num(row[12], ' 원')}</div></div><div style='margin-top:5px;font-weight:bold;'>{safe_str(row['고객사'])}</div><div style='margin-top:4px;font-size:12px;color:#666;'>📅 {safe_str(row['접수일'])}  📦 {safe_str(row[4])}</div></div>", unsafe_allow_html=True)
                        if st.button("▲ 닫기" if is_sel else "▼ 열기", key=f"nc_sel_{orig_idx}", use_container_width=True):
                            st.session_state.nc_sel_idx = None if is_sel else orig_idx; st.rerun()
                        if is_sel: render_nc_detail(df_nc.loc[orig_idx], orig_idx, df_nc)
            st.markdown("<div class='footer-note'>※ 부적합 관리 대장은 관리자만 열람 가능합니다.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

