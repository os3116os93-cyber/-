import streamlit as st
import pandas as pd
import os
import base64

# 1. 초기 환경 설정
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# 사용자 DB (ID/PW/Role)
USER_DB = {
    "admin": {"pw": st.secrets.get("ADMIN_PASSWORD", "admin1234"), "role": "admin", "name": "관리자"},
    "worker": {"pw": "1234", "role": "worker", "name": "현장작업자"}
}
EXCEL_FILE = "customer.xlsx"

st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 2. 세션 상태 초기화
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# 3. 유틸리티 함수
@st.cache_data(ttl=300)
def get_image_base64(file_path):
    if not os.path.exists(file_path): return None
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

@st.cache_data(ttl=300)
def load_data(file_name, skip=0):
    file_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(file_path): return None
    try:
        df = pd.read_excel(file_path, engine='openpyxl', skiprows=skip)
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        return df
    except Exception as e:
        st.error(f"{file_name} 로드 오류: {e}")
        return None

def save_customer_data(df):
    file_path = os.path.join(BASE_DIR, EXCEL_FILE)
    df.to_excel(file_path, index=False)
    load_data.clear()

# 4. CSS (기존 디자인 유지)
st.markdown("""
<style>
.header-wrapper { display: flex; justify-content: space-between; align-items: flex-end; width: 100%; padding: 10px 0; border-bottom: 1px solid #f0f2f6; margin-bottom: 20px; }
.brand-logo { height: 65px; width: auto; }
.team-name-fixed { font-size: 14px; font-weight: 600; color: rgba(0, 0, 0, 0.5); margin-bottom: 5px; }
.main-title { color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; }
.customer-title { color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }
.role-badge { background-color: #FF8C00; color: white; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-left: 10px; }
.qc-table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; width: 100%; }
.qc-table { border-collapse: collapse; margin-top: 10px; font-size: 12px; border: 1px solid #DEE2E6; width: 100%; table-layout: auto; white-space: nowrap; }
.qc-table th { padding: 8px; border: 1px solid #DEE2E6; text-align: center; background-color: #F8F9FA; color: black; font-weight: bold; }
.qc-table td { padding: 8px; border: 1px solid #DEE2E6; text-align: center; background-color: white; color: black; }
.guide-text { display: block; font-size: 15px; font-weight: bold; color: #333; margin: 15px 0; padding: 15px; background-color: #fff4e6; border-radius: 8px; border-left: 5px solid #FF8C00; }
</style>
""", unsafe_allow_html=True)

# 5. UI 렌더링 함수
def render_header():
    logo_path = os.path.join(BASE_DIR, "hanjin_logo.png")
    logo_base64 = get_image_base64(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '[한진철관]'
    badge = f'<span class="role-badge">{st.session_state.user_name}</span>' if st.session_state.user_role else ""
    st.markdown(f'<div class="header-wrapper"><div class="logo-container">{logo_html}</div><div class="team-name-fixed">품질기술팀{badge}</div></div>', unsafe_allow_html=True)

def render_auth_sidebar():
    st.sidebar.markdown("---")
    if st.session_state.user_role is None:
        with st.sidebar.expander("🔐 시스템 로그인", expanded=True):
            user_id = st.text_input("아이디", key="id_in")
            user_pw = st.text_input("비밀번호", type="password", key="pw_in")
            if st.button("로그인", use_container_width=True):
                if user_id in USER_DB and USER_DB[user_id]["pw"] == user_pw:
                    st.session_state.user_role = USER_DB[user_id]["role"]
                    st.session_state.user_name = USER_DB[user_id]["name"]
                    st.rerun()
                else: st.error("정보 불일치")
    else:
        st.sidebar.success(f"현재 접속: {st.session_state.user_name}")
        if st.sidebar.button("🔒 로그아웃", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

# 6. 관리용 폼
def render_add_form(df):
    st.markdown("### ➕ 고객사 추가")
    cols = df.columns.tolist()
    new_values = {}
    for i in range(0, len(cols), 2):
        pair = cols[i:i+2]
        c_cols = st.columns(2)
        for j, c_name in enumerate(pair):
            new_values[c_name] = c_cols[j].text_input(c_name, key=f"add_{c_name}")
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", type="primary"):
        if not new_values.get(cols[0]): st.error("고객사명 필수")
        else:
            save_customer_data(pd.concat([df, pd.DataFrame([new_values])], ignore_index=True))
            st.session_state.show_add_form = False
            st.rerun()
    if c2.button("취소"): 
        st.session_state.show_add_form = False
        st.rerun()

def render_edit_form(df, idx):
    row = df.iloc[idx]
    st.markdown(f"### 📝 수정: {row.iloc[0]}")
    cols = df.columns.tolist()
    updated = {}
    for i in range(0, len(cols), 2):
        pair = cols[i:i+2]
        c_cols = st.columns(2)
        for j, c_name in enumerate(pair):
            val = str(row[c_name]) if pd.notna(row[c_name]) and str(row[c_name]) != "nan" else ""
            updated[c_name] = c_cols[j].text_input(c_name, value=val, key=f"ed_{c_name}")
    c1, c2 = st.columns([1, 5])
    if c1.button("수정 완료", type="primary"):
        for k, v in updated.items(): df.at[idx, k] = v
        save_customer_data(df)
        st.session_state.edit_idx = None
        st.rerun()
    if c2.button("취소"): 
        st.session_state.edit_idx = None
        st.rerun()

# 7. 메인 실행부
def main():
    render_header()
    render_auth_sidebar()

    if st.session_state.user_role is None:
        st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)
        st.warning("왼쪽 사이드바에서 로그인 후 이용해 주시기 바랍니다.")
        return

    st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)

    # 권한 설정
    is_admin = (st.session_state.user_role == "admin")
    
    # 탭 구성 (권한에 따라 다름)
    if is_admin:
        tab1, tab2, tab3 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준", "🏭 제강사 정보"])
    else:
        tab1, tab3 = st.tabs(["📄 고객 사양서", "🏭 제강사 정보"])

    # --- TAB 1: 고객 사양서 (공용이나 기능 차별화) ---
    with tab1:
        df_cust = load_data(EXCEL_FILE)
        if df_cust is not None:
            df_cust = df_cust.dropna(subset=[df_cust.columns[0]])
            for col in df_cust.columns: df_cust[col] = df_cust[col].astype(str).str.strip()
            
            st.sidebar.header("🏢 고객사 목록")
            if is_admin and st.sidebar.button("➕ 고객사 추가"):
                st.session_state.show_add_form = True
                st.session_state.edit_idx = None
                st.rerun()
            
            customer_list = df_cust.iloc[:, 0].tolist()
            sel_idx = st.sidebar.radio("선택:", range(len(df_cust)), format_func=lambda i: customer_list[i], index=None)

            # 관리자 전용 폼 출력
            if is_admin and st.session_state.show_add_form:
                render_add_form(df_cust)
            elif is_admin and st.session_state.edit_idx is not None:
                render_edit_form(df_cust, st.session_state.edit_idx)
            elif sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown(f'<div class="customer-title">■ {row.iloc[0]}</div>', unsafe_allow_html=True)
                
                if is_admin:
                    a1, a2, _ = st.columns([1, 1, 8])
                    if a1.button("수정", key="btn_edit"): 
                        st.session_state.edit_idx = sel_idx
                        st.session_state.show_add_form = False
                        st.rerun()
                    if a2.button("삭제", key="btn_del"):
                        updated_df = df_cust.drop(index=sel_idx).reset_index(drop=True)
                        save_customer_data(updated_df)
                        st.success("삭제되었습니다.")
                        st.rerun()

                # 상세 데이터 렌더링
                for i in range(1, len(row.index)):
                    col_n, raw = row.index[i], row.iloc[i]
                    val = str(raw) if pd.notna(raw) and str(raw) != "nan" else "-"
                    c = "#E63946" if any(k in col_n for k in ["특이사항", "주의", "마킹", "포장"]) else "#495057"
                    st.markdown(f'<div class="notranslate" style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;"><div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2;">{col_n}</div><div style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; font-weight: 500;">{val}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="guide-text">좌측 사이드바에서 고객사를 선택하십시오.</div>', unsafe_allow_html=True)

    # --- TAB 2: 품질 보증 기준 (관리자 전용) ---
    if is_admin:
        with tab2:
            st.markdown('<div class="customer-title">⚖️ 품질 보증 표준 가이드</div>', unsafe_allow_html=True)
            df_qc = load_data("standard.xlsx", skip=5)
            if df_qc is not None:
                col_count, row_count = len(df_qc.columns), len(df_qc)
                all_spans = []
                for c in range(col_count):
                    col_data, spans, i = df_qc.iloc[:, c].fillna('').astype(str).tolist(), [], 0
                    while i < row_count:
                        curr, count = col_data[i].strip(), 1
                        if curr != "":
                            while i + count < row_count and col_data[i + count].strip() == "": count += 1
                        spans.append(count); [spans.append(0) for _ in range(count - 1)]; i += count
                    all_spans.append(spans)
                
                table_html = '<div class="qc-table-wrapper"><table class="qc-table"><thead><tr>'
                for col in df_qc.columns: table_html += f'<th>{col}</th>'
                table_html += '</tr></thead><tbody>'
                for r in range(row_count):
                    table_html += '<tr>'
                    for c in range(col_count):
                        span = all_spans[c][r]
                        if span > 0:
                            cell = str(df_qc.iloc[r, c]).replace("nan", "").replace("(", "<br>(")
                            table_html += f'<td rowspan="{span}">{cell}</td>'
                    table_html += '</tr>'
                st.markdown(table_html + '</tbody></table></div>', unsafe_allow_html=True)

    # --- TAB 3: 제강사 정보 (공용) ---
    with tab3:
        st.markdown('<div class="customer-title">🏭 제강사 원산지 분류표</div>', unsafe_allow_html=True)
        mill_data = [
            {"코드": "PSC", "제강사": "포스코", "원산지": "대한민국"}, {"코드": "HDS", "제강사": "현대제철", "원산지": "대한민국"},
            {"코드": "DBS", "제강사": "동부제철", "원산지": "대한민국"}, {"코드": "DKS", "제강사": "동국씨엠", "원산지": "대한민국"},
            {"코드": "TKS", "제강사": "도쿄", "원산지": "일본"}, {"코드": "FMS", "제강사": "포모사", "원산지": "베트남"},
            {"코드": "HOA", "제강사": "호아팟", "원산지": "베트남"}, {"코드": "CHS", "제강사": "중홍", "원산지": "대만"},
            {"코드": "AGS", "제강사": "안강", "원산지": "중국"}, {"코드": "DGH", "제강사": "동화", "원산지": "중국"},
            {"코드": "DSH", "제강사": "딩셩", "원산지": "중국"}, {"코드": "GUF", "제강사": "국풍", "원산지": "중국"},
            {"코드": "HAN", "제강사": "한단", "원산지": "중국"}, {"코드": "JER", "제강사": "지룬", "원산지": "중국"},
            {"코드": "MSH", "제강사": "보산", "원산지": "중국"}, {"코드": "SDG", "제강사": "산동", "원산지": "중국"},
            {"코드": "SDS", "제강사": "승덕", "원산지": "중국"}, {"코드": "SGS", "제강사": "수도", "원산지": "중국"},
            {"코드": "ZHJ", "제강사": "자오지엔", "원산지": "중국"}
        ]
        df_mill = pd.DataFrame(mill_data)
        q = st.text_input("🔍 제강사/코드 검색", key="mill_srch")
        if q: df_mill = df_mill[df_mill.apply(lambda r: q.lower() in r.astype(str).str.lower().values, axis=1)]
        
        html = '<div class="qc-table-wrapper"><table class="qc-table"><thead><tr><th>코드</th><th>제강사</th><th>원산지</th></tr></thead><tbody>'
        for _, r in df_mill.iterrows():
            style = 'style="color:#007BFF; font-weight:bold;"' if r['원산지'] == "대한민국" else ""
            html += f'<tr><td style="font-weight:bold;">{r["코드"]}</td><td>{r["제강사"]}</td><td {style}>{r["원산지"]}</td></tr>'
        st.markdown(html + '</tbody></table></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
