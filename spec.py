import streamlit as st
import pandas as pd
import os
import base64

# 1. 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 2. 이미지 변환 함수 (성능 최적화)
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- [필독] 깃허브 파일명과 100% 일치해야 함 ---
LOGO_FILENAME = "한진철관CI 누끼.png" 
# --------------------------------------------

logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. CSS 스타일 (주황색 테마 및 품질기술팀 14px 적용)
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        margin-bottom: 10px;
    }}
    .brand-logo {{ height: 40px; width: auto; }}
    .team-name {{
        color: #CCCCCC !important;
        font-size: 14px; /* 1포인트 키움 */
        font-weight: 600;
    }}
    .main-title {{
        color: #FF8C00 !important; /* 주황색 */
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }}
    .customer-title {{
        color: #FF7F50 !important; /* 업체명 주황색 */
        font-weight: bold;
        font-size: 1.4rem;
        margin: 20px 0;
    }}
    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 (중복 제거 로직 추가)
@st.cache_data
def load_data():
    file_candidates = ['고객 사양서.xlsx', '고객사양서.xlsx', 'spec.xlsx']
    target_file = None
    for f in file_candidates:
        if os.path.exists(f):
            target_file = f
            break
    
    if not target_file:
        return None
    
    try:
        df = pd.read_excel(target_file, engine='openpyxl')
        # 양끝 공백 제거 (에스비엔티 중복 방지용)
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        return df.fillna("-")
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 로직
def main():
    # 로고 및 팀명 배치
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f'<div class="header-container">{logo_html}<div class="team-name">품질기술팀</div></div>', unsafe_allow_html=True)

    # 주황색 메인 타이틀
    st.markdown('<div class="main-title">📋 고객사양서 관리</div>', unsafe_allow_html=True)
    st.markdown("---")

    df = load_data()
    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        # 중복된 업체명을 제거하고 고유값만 추출
        customer_list = sorted(list(set(df.iloc[:, 0].astype(str).str.strip().tolist())))
        
        selected_customer = st.sidebar.radio("업체 선택:", customer_list, index=None)

        if selected_customer:
            st.markdown(f'<div class="customer-title">■ {selected_customer}</div>', unsafe_allow_html=True)
            # 선택된 업체 정보 필터링
            row_data = df[df.iloc[:, 0].astype(str).str.strip() == selected_customer].iloc[0]
            
            for col_name in row_data.index[1:]:
                val = str(row_data[col_name])
                bg_color = "#f9f9f9"
                st.markdown(f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: {bg_color}; width: 85px; padding: 10px 5px; font-weight: bold; font-size: 12px; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center;">{col_name}</div>
                        <div style="flex: 1; padding: 10px; background-color: white; font-size: 13px; color: #212529;">{val}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.error("엑셀 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

