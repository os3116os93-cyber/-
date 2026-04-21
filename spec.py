import streamlit as st
import pandas as pd
import os
import base64

# 1. 페이지 설정 (모바일 최적화를 위해 sidebar_state를 auto로 설정)
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. 이미지를 웹 표시용으로 변환하는 함수
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- 로고 파일명 설정 (바탕화면에 함께 두세요) ---
LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 정밀 조정 CSS (디자인 사양 유지 및 모바일 가독성 강화)
st.markdown(f"""
    <style>
    /* 상단 전체 레이아웃 */
    .header-wrapper {{
        position: relative;
        width: 100%;
        padding-top: 10px;
    }}
    
    /* 로고 크기 65px 및 좌상단 배치 */
    .brand-logo {{
        height: 65px; 
        width: auto;
        display: block;
    }}
    
    /* 품질기술팀 우측 하단 고정 */
    .team-name-fixed {{
        position: absolute;
        right: 0;
        bottom: 5px;
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }}

    /* 메인 타이틀 주황색 */
    .main-title {{
        color: #FF8C00 !important;
        font-weight: 800;
        font-size: 1.85rem;
        margin-top: 15px;
        margin-bottom: 5px;
    }}

    /* 업체명 주황색 */
    .customer-title {{
        color: #FF7F50 !important;
        font-weight: bold;
        font-size: 1.45rem;
        margin-top: 30px;
        margin-bottom: 15px;
    }}

    /* 사이드바 글자 강조 */
    .stSidebar [data-testid="stWidgetLabel"] p {{
        font-size: 16px !important;
        font-weight: bold;
    }}
    
    /* 모바일에서 테이블 텍스트가 너무 깨지지 않도록 조정 */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem; }}
        .customer-title {{ font-size: 1.25rem; }}
    }}

    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 및 전처리 (빈 줄 제거 및 경로 최적화)
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_candidates = ['고객 사양서.xlsx', '고객사양서.xlsx', 'spec.xlsx']
    target_path = None

    for f in file_candidates:
        if os.path.exists(f):
            target_path = f
            break
        full_path = os.path.join(current_dir, f)
        if os.path.exists(full_path):
            target_path = full_path
            break
    
    if not target_path:
        return None
    
    try:
        # 데이터 로드
        df = pd.read_excel(target_path, engine='openpyxl')
        
        # [전처리] 첫 번째 열(고객사명) 기준 빈 행 및 무의미한 행 완전 제거
        df = df.dropna(subset=[df.columns[0]])
        df = df.astype(str).apply(lambda x: x.str.strip())
        df = df[~df.iloc[:, 0].isin(["", "nan", "-", "None"])]
        
        return df.replace('nan', '-')
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 로직
def main():
    # --- 상단 헤더 영역 ---
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f"""
        <div class="header-wrapper">
            {logo_html}
            <div class="team-name-fixed">품질기술팀</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">📋 고객사양서 관리</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 10px 0; border: 0.5px solid rgba(250,250,250,0.1);'>", unsafe_allow_html=True)

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        
        # 중복 방지를 위한 인덱스 기반 라디오 버튼
        row_indices = list(range(len(df)))

        selected_idx = st.sidebar.radio(
            "업체를 선택하세요:",
            row_indices,
            format_func=lambda i: df.iloc[i, 0],
            index=None
        )

        if selected_idx is not None:
            # 선택 시 모바일 사용자를 위한 안내 (사이드바 수동 조작 안내)
            row_data = df.iloc[selected_idx]
            customer_name = row_data.iloc[0]
            
            st.markdown(f'<div class="customer-title">■ {customer_name}</div>', unsafe_allow_html=True)
            
            # 상세 내용 테이블 출력
            cols = row_data.index
            for i in range(1, len(cols)):
                col_name = cols[i]
                val = str(row_data[col_name])
                
                # 핵심 키워드 빨간색 강조
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
                                    background-color: white; word-break: break-all; font-size: 13.5px; line-height: 1.4;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
            
            # 하단 안내 문구 (모바일 가독성 보조)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("💡 다른 업체를 찾으려면 왼쪽 상단 화살표( > )를 눌러 메뉴를 다시 열어주세요.")
            st.markdown("<br><br>", unsafe_allow_html=True)
        else:
            st.info("왼쪽 사이드바에서 업체를 선택해 주세요.")
    else:
        st.error("엑셀 파일을 찾을 수 없습니다. [test.py]가 있는 위치에 [고객 사양서.xlsx]가 있는지 확인해 주세요.")

if __name__ == "__main__":
    main()

    
