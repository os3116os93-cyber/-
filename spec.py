import streamlit as st
import pandas as pd
import os
import base64

# 1. 환경 설정 및 경로 정의
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin1234")
EXCEL_FILE = "customer.xlsx"
STANDARD_FILE = "standard.xlsx" # 기존 탭2용
ORIGIN_FILE = "경희.xlsx"     # 신규 탭3용

st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 세션 상태 초기화
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# --- 헬퍼 함수 ---

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

@st.cache_data(ttl=300)
def load_data(file_name, skip=0):
    file_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        return pd.read_excel(file_path, skiprows=skip)
    except Exception as e:
        st.error(f"파일 로드 오류 ({file_name}): {e}")
        return pd.DataFrame()

def save_data(df, file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    try:
        df.to_excel(file_path, index=False)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")
        return False

# CSS (원본 스타일 보존)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .qc-table-wrapper { overflow-x: auto; margin: 10px 0; border: 1px solid #dee2e6; border-radius: 4px; }
    .qc-table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 800px; }
    .qc-table th { background-color: #f1f3f5; font-weight: bold; padding: 10px; border: 1px solid #dee2e6; text-align: center; }
    .qc-table td { padding: 10px; border: 1px solid #dee2e6; text-align: center; vertical-align: middle; background-color: white; }
    .footer-note { font-size: 12px; color: #666; margin-top: 5px; }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 품질기술팀 통합 관리 시스템")

# --- 탭 구성 (기존 1, 2탭 유지 + 3탭 추가) ---
tab1, tab2, tab3 = st.tabs(["📑 고객사별 조회", "📏 검사기준(Standard)", "🌍 원산지 정보"])

# [TAB 1] 고객사별 조회
with tab1:
    df = load_data(EXCEL_FILE)
    if df.empty:
        st.warning(f"'{EXCEL_FILE}' 파일이 없습니다.")
    else:
        # 검색 및 필터링
        search_term = st.text_input("고객사명 또는 품명 검색", "")
        if search_term:
            filtered_df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
        else:
            filtered_df = df

        # 데이터 표시 루프
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🏢 {row['고객사']} - {row['품명']}"):
                # 관리자 수정 기능 (원본 유지)
                if st.session_state.is_admin:
                    c1, c2 = st.columns(2)
                    if c1.button(f"수정하기", key=f"edit_{idx}"):
                        st.session_state.edit_idx = idx
                        st.rerun()
                    if c2.button(f"삭제하기", key=f"del_{idx}"):
                        new_df = df.drop(idx)
                        if save_data(new_df, EXCEL_FILE):
                            st.success("삭제 완료")
                            st.rerun()

                col1, col2 = st.columns([1, 2])
                with col1:
                    img_path = os.path.join(BASE_DIR, "images", f"{row['고객사']}.png")
                    img_base64 = get_image_base64(img_path)
                    if img_base64:
                        st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:5px;">', unsafe_allow_html=True)
                    else:
                        st.info("이미지 없음")

                with col2:
                    # 원본의 정밀한 HTML 테이블 생성 로직
                    df_qc = pd.DataFrame([row])
                    row_count = len(df_qc)
                    col_count = len(df_qc.columns)
                    
                    all_spans = []
                    for c in range(col_count):
                        col_data = df_qc.iloc[:, c].astype(str).tolist()
                        spans = []
                        i = 0
                        while i < row_count:
                            curr = col_data[i].strip()
                            count = 1
                            if curr != "":
                                while i + count < row_count and col_data[i + count].strip() == "":
                                    count += 1
                            spans.append(count)
                            for _ in range(count - 1): spans.append(0)
                            i += count
                        all_spans.append(spans)

                    table_html = '<div class="qc-table-wrapper"><table class="qc-table"><thead><tr>'
                    for col in df_qc.columns:
                        table_html += f'<th>{col}</th>'
                    table_html += '</tr></thead><tbody>'
                    for r in range(row_count):
                        table_html += '<tr>'
                        for c in range(col_count):
                            span_val = all_spans[c][r]
                            if span_val > 0:
                                cell_content = str(df_qc.iloc[r, c]).replace("nan", "").replace("(", "<br>(")
                                table_html += f'<td rowspan="{span_val}">{cell_content}</td>'
                        table_html += '</tr>'
                    table_html += '</tbody></table></div>'
                    st.markdown(table_html, unsafe_allow_html=True)
                    st.markdown('<div class="footer-note">※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>', unsafe_allow_html=True)

# [TAB 2] 검사기준(Standard)
with tab2:
    st.subheader("📏 제품별 검사 표준 규격")
    st_df = load_data(STANDARD_FILE)
    if not st_df.empty:
        st.dataframe(st_df, use_container_width=True, hide_index=True)
    else:
        st.info("표준 규격 데이터가 없습니다.")

# [TAB 3] 신규 원산지 정보 (경희.xlsx)
with tab3:
    st.subheader("🌍 제강사 원산지 분류 정보")
    # 원본 파일 특성상 제목 줄 제외 (skiprows=1)
    origin_df = load_data(ORIGIN_FILE, skip=1)
    
    if not origin_df.empty:
        search_m = st.text_input("제강사 코드 검색 (예: PSC, ZHJ)", key="origin_search").upper()
        if search_m:
            origin_df = origin_df[origin_df['제강사'].astype(str).str.contains(search_m)]
        
        # 모바일 가독성을 위해 st.table 사용
        st.table(origin_df[['제강사', '구분', '원산지']].reset_index(drop=True))
    else:
        st.info("원산지 데이터 파일(경희.xlsx)을 찾을 수 없습니다.")

# [관리자 모드 전용 UI 영역]
if st.session_state.is_admin:
    st.divider()
    st.subheader("⚙️ 데이터 추가/수정")
    
    # 수정 폼 또는 추가 폼 렌더링 (원본 로직 완벽 복구)
    if st.session_state.edit_idx is not None:
        st.write("### 데이터 수정")
        idx = st.session_state.edit_idx
        with st.form("edit_form"):
            edited_data = {}
            cols = st.columns(3)
            for i, col_name in enumerate(df.columns):
                edited_data[col_name] = cols[i % 3].text_input(col_name, value=str(df.loc[idx, col_name]))
            
            if st.form_submit_button("수정 완료"):
                for col_name in df.columns:
                    df.loc[idx, col_name] = edited_data[col_name]
                if save_data(df, EXCEL_FILE):
                    st.success("수정되었습니다.")
                    st.session_state.edit_idx = None
                    st.rerun()
    
    elif st.button("신규 사양 추가"):
        st.session_state.show_add_form = not st.session_state.show_add_form

    if st.session_state.show_add_form:
        with st.form("add_form"):
            new_data = {}
            cols = st.columns(3)
            for i, col_name in enumerate(df.columns):
                new_data[col_name] = cols[i % 3].text_input(col_name)
            
            if st.form_submit_button("저장하기"):
                new_row = pd.DataFrame([new_data])
                df = pd.concat([df, new_row], ignore_index=True)
                if save_data(df, EXCEL_FILE):
                    st.success("추가되었습니다.")
                    st.session_state.show_add_form = False
                    st.rerun()

# 사이드바 (로그인)
with st.sidebar:
    st.header("🔐 관리자 인증")
    if not st.session_state.is_admin:
        pwd = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("비밀번호 오류")
    else:
        st.success("관리자 권한 실행 중")
        if st.button("로그아웃"):
            st.session_state.is_admin = False
            st.rerun()

