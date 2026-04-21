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

# --- 로고 파일명 설정 ---
LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 정밀 조정 CSS (사용자 요청 사양 100% 반영)
st.markdown(f"""
    <style>
    /* 상단 전체 레이아웃 */
    .header-wrapper {{
        position: relative;
        width: 100%;
        padding-top: 10px;
    }}
    
    /* 로고 크기 및 위치 (좌상단 65px) */
    .brand-logo {{
        height: 65px; 
        width: auto;
        display: block;
    }}
    
    /* 품질기술팀 위치 (우측 하단 고정) */
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
        font-size: 15px !important;
        font-weight: bold;
    }}
    
    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 및 전처리 (빈 행 제거 및 경로 최적화)
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
        
        # [품목 늘리기 대응 및 빈 줄 제거 핵심 로직]
        # 1. 첫 번째 열(고객사명)이 비어있는(NaN) 행을 제거합니다.
        df = df.dropna(subset=[df.columns[0]])
        
        # 2. 모든 데이터를 문자열로 변환하고 앞뒤 공백을 제거합니다.
        df = df.astype(str).apply(lambda x: x.str.strip())
        
        # 3. 업체명이 비어있거나 "-"만 있는 행은 메뉴에서 제외합니다.
        df = df[df.iloc[:, 0] != ""]
        df = df[df.iloc[:, 0] != "nan"]
        df = df[df.iloc[:, 0] != "-"]
        
        return df.replace('nan', '-')
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 로직
def main():
    # --- 헤더 구성 ---
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
        
        # 중복 방지 및 튕김 해결을 위해 인덱스 기반으로 라디오 버튼 생성
        row_indices = list(range(len(df)))

        selected_idx = st.sidebar.radio(
            "업체를 선택하세요:",
            row_indices,
            # 사이드바에는 엑셀 첫 번째 열의 업체명을 그대로 보여줌
            format_func=lambda i: df.iloc[i, 0],
            index=None
        )

        if selected_idx is not None:
            # 선택된 번호의 데이터를 정확히 추출
            row_data = df.iloc[selected_idx]
            customer_name = row_data.iloc[0]
            
            st.markdown(f'<div class="customer-title">■ {customer_name}</div>', unsafe_allow_html=True)
            
            # 상세 내용 테이블 출력
            cols = row_data.index
            for i in range(1, len(cols)):
                col_name = cols[i]
                val = str(row_data[col_name])
                
                # 특이사항/주의/마킹/포장 키워드 강조 (빨간색)
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
            st.markdown("<br><br>", unsafe_allow_html=True)
        else:
            st.info("왼쪽 사이드바에서 업체를 선택해 주세요.")
    else:
        st.error("엑셀 파일을 찾을 수 없습니다. [test.py]와 [고객 사양서.xlsx]가 같은 폴더에 있는지 확인해 주세요.")

if __name__ == "__main__":
    main()

    
