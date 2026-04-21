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

# 2. 이미지를 웹 표시용으로 변환하는 함수 (오류 해결 핵심)
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- 파일명은 반드시 깃허브와 동일해야 합니다 ---
LOGO_FILENAME = "hanjin_logo.png" 
# --------------------------------------------

logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 최적화 CSS (주황색 테마 및 레이아웃)
st.markdown(f"""
    <style>
    /* 상단 헤더 (로고 & 품질기술팀) */
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        margin-bottom: 10px;
    }}
    .brand-logo {{ height: 38px; width: auto; }}
    .team-name {{
        color: #CCCCCC !important;
        font-size: 14px; /* 1pt 키움 */
        font-weight: 600;
    }}

    /* 메인 타이틀 주황색 */
    .main-title {{
        color: #FF8C00 !important;
        font-weight: 800;
        font-size: 1.8rem;
        margin-top: 10px;
    }}

    /* 업체명 주황색 */
    .customer-title {{
        color: #FF7F50 !important;
        font-weight: bold;
        font-size: 1.4rem;
        margin-top: 25px;
        margin-bottom: 15px;
    }}

    /* 사이드바 글자 크기 */
    .stSidebar [data-testid="stWidgetLabel"] p {{
        font-size: 15px !important;
        font-weight: bold;
    }}
    
    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 함수 (중복 처리 포함)
@st.cache_data
def load_data():
    file_candidates = ['고객 사양서.xlsx', '고객사양서.xlsx', 'spec.xlsx', 'test.xlsx']
    target_file = None
    for f in file_candidates:
        if os.path.exists(f):
            target_file = f
            break
    
    if not target_file:
        return None
    
    try:
        df = pd.read_excel(target_file, engine='openpyxl')
        # 모든 컬럼명 공백 제거
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        # 첫 번째 열(업체명)의 데이터 공백 제거
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()
        return df.fillna("-")
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 실행
def main():
    # 상단 헤더 출력 (로고 + 품질기술팀)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f"""
        <div class="header-container">
            {logo_html}
            <div class="team-name">품질기술팀</div>
        </div>
        """, unsafe_allow_html=True)

    # 메인 제목 (주황색)
    st.markdown('<div class="main-title">📋 고객사양서 관리</div>', unsafe_allow_html=True)
    st.markdown("---")

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        # 중복 제거 및 가나다순 정렬 (에스비엔티 문제 해결)
        customer_list = sorted(list(set(df.iloc[:, 0].tolist())))
        
        selected_customer = st.sidebar.radio(
            "업체를 선택하세요:",
            customer_list,
            index=None
        )

        if selected_customer:
            # 선택된 업체 데이터 필터링
            row_data = df[df.iloc[:, 0] == selected_customer].iloc[0]
            
            # 업체명 표시 (주황색)
            st.markdown(f'<div class="customer-title">■ {selected_customer}</div>', unsafe_allow_html=True)
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹", "포장"])
                
                bg_color = "#F8F9FA" 
                item_label_color = "#E63946" if is_special else "#495057"

                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: {bg_color}; width: 85px; min-width: 85px; padding: 10px 4px; 
                                    font-weight: bold; color: {item_label_color}; border-right: 1px solid #DEE2E6; 
                                    display: flex; align-items: center; justify-content: center; text-align: center; 
                                    font-size: 12px; line-height: 1.2; word-break: keep-all;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 10px; color: #212529; font-weight: 500; 
                                    background-color: white; word-break: break-all; font-size: 13px; line-height: 1.4;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
            st.markdown("<br><br>", unsafe_allow_html=True)
        else:
            st.info("왼쪽 사이드바에서 업체를 선택해 주세요.")
    else:
        st.error("엑셀 파일을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해 주세요.")

if __name__ == "__main__":
    main()


