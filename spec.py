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

# 2. 이미지를 웹 표시용으로 변환하는 함수 (로컬/깃허브 공용)
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

# --- 파일명 설정 (바탕화면에 함께 두시면 됩니다) ---
LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 디자인 CSS (사용자 요청 사양 정밀 고정)
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

# 4. 데이터 로드 함수 (로컬 바탕화면 및 깃허브 호환)
@st.cache_data
def load_data():
    # 파일명 후보 (사용자님이 사용 중인 파일명 포함)
    file_candidates = ['고객 사양서.xlsx', '고객사양서.xlsx', 'spec.xlsx']
    target_file = None
    
    # 현재 실행 경로에서 파일 찾기
    for f in file_candidates:
        if os.path.exists(f):
            target_file = f
            break
    
    if not target_file:
        return None
    
    try:
        # 엑셀 로드 (엔진 지정으로 호환성 확보)
        df = pd.read_excel(target_file, engine='openpyxl')
        
        # 컬럼 및 데이터 정제 (공백 제거)
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        df = df.astype(str).apply(lambda x: x.str.strip())
        
        return df.replace('nan', '-')
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 실행 로직
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
        
        # [중복 방지 핵심 로직]
        # 업체명 리스트 대신 '행 인덱스'를 사용하여 메뉴를 생성합니다.
        # 에스비엔티(규격A), 에스비엔티(규격B)가 이름이 같더라도 각각 고유하게 인식합니다.
        row_indices = list(range(len(df)))

        selected_idx = st.sidebar.radio(
            "업체를 선택하세요:",
            row_indices,
            # 화면에는 엑셀의 첫 번째 열(업체명)만 보여줍니다.
            format_func=lambda i: df.iloc[i, 0],
            index=None
        )

        if selected_idx is not None:
            # 선택된 인덱스의 데이터를 정확히 추출 (튕김 현상 없음)
            row_data = df.iloc[selected_idx]
            customer_name = row_data.iloc[0]
            
            st.markdown(f'<div class="customer-title">■ {customer_name}</div>', unsafe_allow_html=True)
            
            # 상세 내용 테이블 출력
            cols = row_data.index
            for i in range(1, len(cols)):
                col_name = cols[i]
                val = str(row_data[col_name])
                
                # 특이사항/주의 등 강조 키워드 체크
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
        st.error("바탕화면에서 엑셀 파일을 찾을 수 없습니다. 파일명을 확인해 주세요.")

if __name__ == "__main__":
    main()

    

