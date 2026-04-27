import streamlit as st
import pandas as pd
import os
import base64
import gspread
from google.oauth2.service_account import Credentials

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# ---------------------------------------------------------
# [수정됨] 구글 시트 및 관리자 설정 (st.secrets 활용)
# ---------------------------------------------------------
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin1234")
SHEET_URL = st.secrets.get("SHEET_URL", "") # secrets.toml에 구글 시트 주소 입력

st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False


@st.cache_data(ttl=300)
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"이미지 로드 오류: {e}")
        return None

# ---------------------------------------------------------
# [추가됨] 구글 시트 인증 함수
# ---------------------------------------------------------
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # secrets.toml에 등록된 [gcp_service_account] 정보를 불러옵니다.
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

# ---------------------------------------------------------
# [수정됨] 구글 시트 데이터 로드
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def load_data():
    try:
        client = get_gsheet_client()
        sh = client.open_by_url(SHEET_URL)
        worksheet = sh.get_worksheet(0) # 첫 번째 시트 탭 가져오기
        data = worksheet.get_all_values()
        
        if not data:
            return None
            
        # 첫 번째 행을 컬럼명으로 사용하여 데이터프레임 생성
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # 기존 로직 유지: ※가 포함된 주석 행 제외
        if not df.empty and len(df.columns) > 0:
            df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
            
        return df
    except Exception as e:
        st.error(f"구글 시트 로드 오류: {e}")
        return None

# ---------------------------------------------------------
# [수정됨] 구글 시트 데이터 저장
# ---------------------------------------------------------
def save_customer_data(df):
    try:
        client = get_gsheet_client()
        sh = client.open_by_url(SHEET_URL)
        worksheet = sh.get_worksheet(0)
        
        # 시트 데이터 초기화 후 새 데이터 덮어쓰기
        worksheet.clear()
        
        # NaN 등 결측치를 빈 문자열로 바꾸고 전체를 문자열로 변환 (오류 방지)
        save_data = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
        worksheet.update(save_data)
        
        # 저장 후 캐시 초기화하여 즉시 반영
        load_data.clear()
        return True
    except Exception as e:
        st.error(f"구글 시트 저장 오류: {e}")
        return False


def build_standard_table():
    """
    이미지와 엑셀 구조를 정확히 분석하여 병합셀 HTML 테이블 생성.
    엑셀 row 6=헤더, row 7~27=데이터, row 28=※주석(제외)
    컬럼: 구분 | 항목 | 사내 검사 기준 | KS 검사 기준
    """
    td = 'style="padding:8px 12px; border:1px solid #DEE2E6; text-align:center; vertical-align:middle; background:white; color:#000; font-size:12px; white-space:pre-wrap;"'
    th = 'style="padding:8px 12px; border:1px solid #DEE2E6; text-align:center; vertical-align:middle; background:#F8F9FA; color:#000; font-weight:bold; font-size:12px;"'

    def cell(content, rs=1, cs=1):
        r = f' rowspan="{rs}"' if rs > 1 else ""
        c = f' colspan="{cs}"' if cs > 1 else ""
        return f"<td {td}{r}{c}>{content}</td>"

    rows = []

    # 헤더
    rows.append(f"<tr><th {th}>구분</th><th {th}>항목</th><th {th}>사내 검사 기준</th><th {th}>KS 검사 기준</th></tr>")

    # ── 겉모양 (2행) ──────────────────────────────────────
    rows.append(
        "<tr>"
        + cell("겉모양", rs=2)
        + cell("외관 상태")
        + cell("사용상 해로운 결점이 없어야 한다.")
        + cell("사용상 해로운 결점이 없어야 한다.", rs=2)
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("마킹")
        + cell("수요가 요청한 마킹 준수")
        + "</tr>"
    )

    # ── 용접 (2행) ────────────────────────────────────────
    rows.append(
        "<tr>"
        + cell("용접", rs=2)
        + cell("편평시험")
        + cell("외경 대비 80%이상 누를것")
        + cell("KS 평균 수준: 외경 대비: 30%이상 누를것", rs=2)
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("용접 위치")
        + cell("가구용 : 모서리 2mm이내")
        + "</tr>"
    )

    # ── 치수 - 외경 (8행, row11~18) ──────────────────────
    # 구분: 치수는 row11~27 (17행) 전체 병합
    # 항목: 외경은 row11~18 (8행) 병합
    rows.append(
        "<tr>"
        + cell("치수", rs=17)          # row11~27
        + cell("외경", rs=8)            # row11~18
        + cell("각형관")
        + cell("각형관 KS D3568 기준")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("100mm 미만: ±0.25 mm")
        + cell("100mm 미만: ±1.5mm")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("100mm 초과: ± 0.5mm")
        + cell("100mm 초과: ±1.5%", rs=2)   # row13~14 병합
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("※ 가구용: ±0.1mm")
        # KS 기준 셀은 위 row13에서 rowspan=2로 처리됨
        + "</tr>"
    )
    # row15: 빈 행 (구분/항목 이미 병합 중)
    rows.append(
        "<tr>"
        + cell("")
        + cell("")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("원형관\n(강제전선관 제외)")
        + cell("원형관 KS D3566 기준")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("50mm 미만: ±0.25 mm")
        + cell("50mm 미만: ±0.25 mm")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("50mm 이상: ±0.5 mm")
        + cell("50mm 이상: ±0.5%")
        + "</tr>"
    )

    # ── 치수 - 요철 (2행, row19~20) ─────────────────────
    rows.append(
        "<tr>"
        + cell("요철", rs=2)
        + cell("100mm 미만: ±1.0mm")
        + cell("100mm 미만: ±1.5mm")
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("100mm 초과: ±1.5mm")
        + cell("100mm 초과: ±1.5%")
        + "</tr>"
    )

    # ── 치수 - 직진도 (2행, row21~22) ───────────────────
    rows.append(
        "<tr>"
        + cell("직진도", rs=2)
        + cell("전체 길이의 0.15% 이내\n(6000mm 기준 9mm 이하)")
        + cell("전체 길이의 0.3% 이내\n(6000mm 기준 18mm 이하)", rs=2)
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("1.8t 미만: 2 t 이하\n(예:1.8x2=3.6R 이하)")
        + "</tr>"
    )

    # ── 치수 - R값 (2행, row23~24) ──────────────────────
    rows.append(
        "<tr>"
        + cell("R값", rs=2)
        + cell("1.8t 이상: 2.5 t 이하")
        + cell("3 t 이하", rs=2)
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("가구용: 2.0R 이하")
        + "</tr>"
    )

    # ── 치수 - 각도 (1행, row25) ────────────────────────
    rows.append(
        "<tr>"
        + cell("각도")
        + cell("±1.0˚")
        + cell("±1.5˚")
        + "</tr>"
    )

    # ── 치수 - 길이 (2행, row26~27) ─────────────────────
    rows.append(
        "<tr>"
        + cell("길이", rs=2)
        + cell("각관: +3mm ~ +10mm")
        + cell("주문 길이 이상 일것", rs=2)
        + "</tr>"
    )
    rows.append(
        "<tr>"
        + cell("원형관: +5mm ~ +20mm")
        + "</tr>"
    )

    table_html = (
        '<div class="qc-table-wrapper notranslate" translate="no">'
        '<table class="qc-table" style="border-collapse:collapse; width:100%;">'
        "<thead>" + rows[0] + "</thead>"
        "<tbody>" + "".join(rows[1:]) + "</tbody>"
        "</table></div>"
    )
    return table_html


LOGO_FILENAME = os.path.join(BASE_DIR, "hanjin_logo.png")
logo_base64 = get_image_base64(LOGO_FILENAME)

st.markdown("""
<style>
.header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    width: 100%;
    padding: 10px 0;
    border-bottom: 1px solid #f0f2f6;
    margin-bottom: 20px;
}
.logo-container { height: 65px; }
.brand-logo { height: 65px; width: auto; }
.team-name-fixed {
    font-size: 14px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.5);
    margin-bottom: 5px;
}
.main-title { color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; }
.customer-title { color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }
.admin-badge {
    background-color: #FF8C00;
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    margin-left: 10px;
}
.qc-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
}
.qc-table {
    border-collapse: collapse;
    margin-top: 10px;
    font-size: clamp(10px, 2.2vw, 12px);
    border: 1px solid #DEE2E6;
    table-layout: auto;
    width: 100%;
}
.qc-table th {
    padding: clamp(4px, 1.5vw, 8px) clamp(6px, 2vw, 12px);
    border: 1px solid #DEE2E6;
    text-align: center !important;
    vertical-align: middle !important;
    background-color: #F8F9FA !important;
    color: #000000 !important;
    font-weight: bold !important;
}
.qc-table td {
    padding: clamp(4px, 1.5vw, 8px) clamp(6px, 2vw, 12px);
    border: 1px solid #DEE2E6;
    text-align: center !important;
    vertical-align: middle !important;
    background-color: white !important;
    color: #000000 !important;
}
.footer-note { font-size: 12.5px; color: #666; margin-top: 15px; font-weight: 500; }
.guide-text { display: none; }
@media (max-width: 768px) {
    .guide-text {
        display: block;
        font-size: 15px;
        font-weight: bold;
        color: #333;
        margin: 15px 0;
        padding: 15px;
        background-color: #fff4e6;
        border-radius: 8px;
        border-left: 5px solid #FF8C00;
        line-height: 1.4;
    }
}
</style>
""", unsafe_allow_html=True)


def render_header():
    if logo_base64:
        logo_img_html = '<img src="data:image/png;base64,' + logo_base64 + '" class="brand-logo">'
    else:
        logo_img_html = '<div style="color:#ccc; font-size:12px;">[한진철관 로고 미검출]</div>'
    admin_badge = '<span class="admin-badge">🔓 관리자 모드</span>' if st.session_state.is_admin else ""
    st.markdown(
        '<div class="header-wrapper">'
        '<div class="logo-container">' + logo_img_html + '</div>'
        '<div class="team-name-fixed">품질기술팀' + admin_badge + '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def render_admin_login():
    st.sidebar.markdown("---")
    if not st.session_state.is_admin:
        with st.sidebar.expander("🔐 관리자 로그인"):
            pw = st.text_input("비밀번호", type="password", key="admin_pw_input")
            if st.button("로그인", key="admin_login_btn"):
                if pw == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
    else:
        if st.sidebar.button("🔒 관리자 로그아웃"):
            st.session_state.is_admin = False
            st.session_state.edit_idx = None
            st.session_state.show_add_form = False
            st.rerun()


def render_add_form(df):
    st.markdown("### ➕ 고객사 추가")
    cols = df.columns.tolist()
    new_values = {}
    col_pairs = [cols[i:i+2] for i in range(0, len(cols), 2)]
    for pair in col_pairs:
        form_cols = st.columns(2)
        for j, col_name in enumerate(pair):
            new_values[col_name] = form_cols[j].text_input(col_name, key="add_" + col_name)
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="add_save"):
        if not new_values.get(cols[0], "").strip():
            st.error("고객사명은 필수 입력입니다.")
        else:
            new_row = pd.DataFrame([new_values])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            save_customer_data(updated_df)
            st.session_state.show_add_form = False
            st.success("'" + new_values[cols[0]] + "' 고객사가 추가되었습니다!")
            st.rerun()
    if c2.button("취소", key="add_cancel"):
        st.session_state.show_add_form = False
        st.rerun()


def render_edit_form(df, idx):
    row = df.iloc[idx]
    st.markdown("### 수정 중: " + str(row.iloc[0]))
    cols = df.columns.tolist()
    updated_values = {}
    col_pairs = [cols[i:i+2] for i in range(0, len(cols), 2)]
    for pair in col_pairs:
        form_cols = st.columns(2)
        for j, col_name in enumerate(pair):
            current_val = str(row[col_name]) if pd.notna(row[col_name]) and str(row[col_name]) != "nan" else ""
            updated_values[col_name] = form_cols[j].text_input(col_name, value=current_val, key="edit_" + col_name)
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="edit_save"):
        for col_name, val in updated_values.items():
            df.at[idx, col_name] = val
        save_customer_data(df)
        st.session_state.edit_idx = None
        st.success("수정이 완료되었습니다!")
        st.rerun()
    if c2.button("취소", key="edit_cancel"):
        st.session_state.edit_idx = None
        st.rerun()


def main():
    render_header()
    st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준", "🏭 제강사 정보"])

    # ── 탭1: 고객 사양서 (데이터 로드 함수만 변경됨) ───────────
    with tab1:
        df_cust = load_data() # 변경: EXCEL_FILE 파라미터 제거
        if df_cust is not None:
            df_cust = df_cust.dropna(subset=[df_cust.columns[0]])
            for col in df_cust.columns:
                df_cust[col] = df_cust[col].astype(str).str.strip()
            customer_list = df_cust.iloc[:, 0].tolist()
            st.sidebar.header("🏢 고객사 목록")
            if st.session_state.is_admin:
                if st.sidebar.button("➕ 고객사 추가", key="open_add_form"):
                    st.session_state.show_add_form = True
                    st.session_state.edit_idx = None
            sel_idx = st.sidebar.radio(
                "업체를 선택하세요:",
                options=list(range(len(df_cust))),
                format_func=lambda i: customer_list[i],
                index=None,
                key="customer_radio"
            )
            if sel_idx is None and not st.session_state.show_add_form and st.session_state.edit_idx is None:
                st.markdown('<div class="guide-text">좌상단 >> 화살표를 눌러 고객사를 선택 하십시오.</div>', unsafe_allow_html=True)
            if st.session_state.is_admin and st.session_state.show_add_form:
                render_add_form(df_cust)
            elif st.session_state.is_admin and st.session_state.edit_idx is not None:
                render_edit_form(df_cust, st.session_state.edit_idx)
            elif sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown('<div class="customer-title">■ ' + str(row.iloc[0]) + '</div>', unsafe_allow_html=True)
                if st.session_state.is_admin:
                    a1, a2, _ = st.columns([1, 1, 8])
                    if a1.button("수정", key="edit_btn"):
                        st.session_state.edit_idx = sel_idx
                        st.session_state.show_add_form = False
                        st.rerun()
                    if a2.button("삭제", key="delete_btn"):
                        st.session_state["confirm_delete_" + str(sel_idx)] = True
                    if st.session_state.get("confirm_delete_" + str(sel_idx), False):
                        st.warning("**'" + str(row.iloc[0]) + "'** 고객사를 정말 삭제하시겠습니까?")
                        d1, d2 = st.columns([1, 5])
                        if d1.button("확인 삭제", key="confirm_del"):
                            updated_df = df_cust.drop(index=sel_idx).reset_index(drop=True)
                            save_customer_data(updated_df)
                            st.session_state["confirm_delete_" + str(sel_idx)] = False
                            st.success("삭제되었습니다.")
                            st.rerun()
                        if d2.button("취소", key="cancel_del"):
                            st.session_state["confirm_delete_" + str(sel_idx)] = False
                            st.rerun()
                for i in range(1, len(row.index)):
                    col_n = row.index[i]
                    raw = row.iloc[i]
                    val = str(raw).strip() if pd.notna(raw) and str(raw).strip() not in ("", "nan") else "-"
                    is_sp = any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"
                    st.markdown(
                        '<div class="notranslate" translate="no" style="display:flex; border:1px solid #DEE2E6; margin-bottom:-1px;">'
                        '<div style="background-color:#F8F9FA; width:85px; min-width:85px; padding:10px 4px; font-weight:bold; color:' + c + '; border-right:1px solid #DEE2E6; display:flex; align-items:center; justify-content:center; text-align:center; font-size:12px; line-height:1.2; word-break:keep-all;">' + str(col_n) + '</div>'
                        '<div class="notranslate" translate="no" style="flex:1; padding:10px; background-color:white; font-size:13.5px; line-height:1.4; color:#212529; font-weight:500; word-break:break-all;">' + val + '</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )
        render_admin_login()

    # ── 탭2: 품질 보증 기준 ──────────────────────────────────
    with tab2:
        st.markdown('<div class="customer-title">⚖️ 품질 보증 표준 가이드</div>', unsafe_allow_html=True)
        st.markdown(build_standard_table(), unsafe_allow_html=True)
        st.markdown('<div class="footer-note">※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>', unsafe_allow_html=True)

    # ── 탭3: 제강사 정보 ──────────────────────────────────
    with tab3:
        st.markdown('<div class="customer-title">🏭 제강사 원산지 분류표</div>', unsafe_allow_html=True)
        mill_data = [
            {"코드": "PSC", "제강사": "포스코", "원산지": "대한민국"},
            {"코드": "HDS", "제강사": "현대제철", "원산지": "대한민국"},
            {"코드": "DBS", "제강사": "동부제철", "원산지": "대한민국"},
            {"코드": "DKS", "제강사": "동국씨엠", "원산지": "대한민국"},
            {"코드": "SEAH", "제강사": "세아씨엠", "원산지": "대한민국"},
            {"코드": "TKS", "제강사": "도쿄", "원산지": "일본"},
            {"코드": "NSC", "제강사": "닛테츠", "원산지": "일본"},
            {"코드": "FMS", "제강사": "포모사", "원산지": "베트남"},
            {"코드": "HOA", "제강사": "호아팟", "원산지": "베트남"},
            {"코드": "CHS", "제강사": "중홍", "원산지": "대만"},
            {"코드": "ANF", "제강사": "안펑", "원산지": "중국"},
            {"코드": "BAO", "제강사": "포두", "원산지": "중국"},
            {"코드": "JYE", "제강사": "징예", "원산지": "중국"},
            {"코드": "RSC", "제강사": "일조강철", "원산지": "중국"},
            {"코드": "AGS", "제강사": "안강", "원산지": "중국"},
            {"코드": "DGH", "제강사": "동화", "원산지": "중국"},
            {"코드": "DSH", "제강사": "딩셩", "원산지": "중국"},
            {"코드": "GUF", "제강사": "국풍", "원산지": "중국"},
            {"코드": "HAN", "제강사": "한단", "원산지": "중국"},
            {"코드": "JER", "제강사": "지룬", "원산지": "중국"},
            {"코드": "MSH", "제강사": "보산", "원산지": "중국"},
            {"코드": "SDG", "제강사": "산동", "원산지": "중국"},
            {"코드": "SDS", "제강사": "승덕", "원산지": "중국"},
            {"코드": "SGS", "제강사": "수도", "원산지": "중국"},
            {"코드": "ZHJ", "제강사": "조건", "원산지": "중국"},
            {"코드": "KGM", "제강사": "카이징", "원산지": "중국"},
            {"코드": "LYN", "제강사": "롄강", "원산지": "중국"},
            {"코드": "NTS", "제강사": "신청강", "원산지": "중국"},
            {"코드": "TNT", "제강사": "천철", "원산지": "중국"},
            {"코드": "TSS", "제강사": "당산강철", "원산지": "중국"},
            {"코드": "YAN", "제강사": "연산강철", "원산지": "중국"},
        ]
        df_mill = pd.DataFrame(mill_data)
        search_q = st.text_input("🔍 제강사 명칭 또는 코드 검색", placeholder="예: PSC, 포스코, 중국...", key="mill_search")
        if search_q:
            df_mill = df_mill[
                df_mill["코드"].str.contains(search_q, case=False, na=False) |
                df_mill["제강사"].str.contains(search_q, case=False, na=False) |
                df_mill["원산지"].str.contains(search_q, case=False, na=False)
            ]
        mill_html = '<div class="qc-table-wrapper notranslate" translate="no"><table class="qc-table"><thead><tr><th>코드</th><th>제강사</th><th>원산지</th></tr></thead><tbody>'
        for _, r in df_mill.iterrows():
            o_style = ' style="color:#007BFF; font-weight:bold;"' if r["원산지"] == "대한민국" else ""
            mill_html += '<tr><td style="font-weight:bold;">' + r["코드"] + '</td><td>' + r["제강사"] + '</td><td' + o_style + '>' + r["원산지"] + '</td></tr>'
        mill_html += '</tbody></table></div>'
        st.markdown(mill_html, unsafe_allow_html=True)
        st.markdown('<div class="footer-note">※ 제강사 정보는 검색으로 손쉬운 확인이 가능합니다.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

