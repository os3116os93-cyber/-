import streamlit as st
import pandas as pd
import os
import base64

# 1. 경로 설정 (PC 및 서버 공용)
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

# 설정값
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin1234")
EXCEL_FILE = "customer.xlsx"
ORIGIN_FILE = "경희.xlsx"  # 원산지 데이터 파일명 정의

st.set_page_config(
    page_title="품질관리 시스템 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 세션 상태 초기화 (기존 코드 유지)
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# --- 공통 함수 영역 (기존 유지 및 개선) ---

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
def load_data(file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        # 경희.xlsx는 첫 줄이 제목이므로 2번째 줄(index 1)부터 헤더로 읽음
        if file_name == ORIGIN_FILE:
            return pd.read_excel(file_path, skiprows=1)
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"파일 로드 오류 ({file_name}): {e}")
        return pd.DataFrame()

# CSS 스타일 (기존 스타일 보존 및 원산지 탭용 추가)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .qc-table-wrapper { overflow-x: auto; margin: 10px 0; border: 1px solid #dee2e6; border-radius: 4px; }
    .qc-table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 600px; }
    .qc-table th { background-color: #f1f3f5; font-weight: bold; padding: 10px; border: 1px solid #dee2e6; text-align: center; }
    .qc-table td { padding: 10px; border: 1px solid #dee2e6; text-align: center; vertical-align: middle; background-color: white; }
    .footer-note { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📋 품질기술팀 통합 관리 시스템")

# --- 탭 구성: 기존 기능과 신규 기능의 분리 ---
tab1, tab2 = st.tabs(["📑 고객 사양서 조회", "🌍 제강사 원산지 분류"])

# [TAB 1] 기존 고객 사양서 관리 로직 (원본 코드 그대로 유지)
with tab1:
    df = load_data(EXCEL_FILE)
    if df.empty:
        st.warning(f"'{EXCEL_FILE}' 파일을 찾을 수 없습니다.")
    else:
        # 검색 필터
        search_term = st.text_input("고객사명 또는 품명 검색", "")
        if search_term:
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        else:
            filtered_df = df

        # 데이터 리스트 렌더링
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🏢 {row['고객사']} - {row['품명']}"):
                col1, col2 = st.columns([1, 2])
                
                # 이미지 처리
                with col1:
                    img_path = os.path.join(BASE_DIR, "images", f"{row['고객사']}.png")
                    img_base64 = get_image_base64(img_path)
                    if img_base64:
                        st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:5px;">', unsafe_allow_html=True)
                    else:
                        st.info("등록된 이미지가 없습니다.")

                # 상세 테이블 생성 (원본의 복잡한 HTML 렌더링 로직 그대로 적용)
                with col2:
                    df_qc = pd.DataFrame([row]) # 행 데이터 프레임화
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

# [TAB 2] 신규 제강사 원산지 정보 (경희.xlsx 연동)
with tab2:
    st.subheader("🌍 제강사 원산지 분류 정보")
    origin_df = load_data(ORIGIN_FILE)
    
    if origin_df.empty:
        st.info("원산지 데이터(경희.xlsx)가 없거나 형식이 맞지 않습니다.")
    else:
        # 검색 기능 (PC/모바일 공용)
        search_maker = st.text_input("제강사 코드 검색 (예: PSC, ZHJ)", "").upper()
        
        if search_maker:
            # '제강사' 컬럼에서 검색
            display_df = origin_df[origin_df['제강사'].astype(str).str.contains(search_maker, case=False)]
        else:
            display_df = origin_df

        # 결과 테이블 표시 (모바일에서 보기 편한 구성)
        if not display_df.empty:
            # 필요한 열만 선택하여 깔끔하게 표시
            st.table(display_df[['제강사', '구분', '원산지']].reset_index(drop=True))
        else:
            st.warning("검색 결과가 없습니다.")
        
        st.caption("💡 해당 데이터는 '경희.xlsx' 파일을 기준으로 실시간 업데이트됩니다.")

# 관리자 로그인 기능 (기존 사이드바 로직 유지)
with st.sidebar:
    st.header("🔐 시스템 관리")
    if not st.session_state.is_admin:
        pwd = st.text_input("관리자 비밀번호", type="password")
        if st.button("로그인"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    else:
        st.success("관리자 모드 실행 중")
        if st.button("로그아웃"):
            st.session_state.is_admin = False
            st.rerun()
