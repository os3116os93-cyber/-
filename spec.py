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
    except Exception:
        return ""

# --- 설정된 영문 파일명 (hanjin_logo.png) ---
LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 정밀 조정 CSS (디자인 사양 복구)
st.markdown(f"""
    <style>
    /* 상단 전체 레이아웃 */
    .header-wrapper {{
        position: relative;
        width: 100%;
        padding-top: 10px;
    }}
    
    /* 로고 크기 확대 (65px 유지) */
    .brand-logo {{
        height: 65px; 
        width: auto;
        display: block;
    }}
    
    /* 품질기술팀 문구 위치 (사용자 지정 우측 하단 박스 위치) */
    .team-name-fixed {{
        position: absolute;
        right: 0;
        bottom: 5px;
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }}

    /* 메인 타이틀 (주황색 강조) */
    .main-title {{
        color: #FF8C00 !important;
        font-weight: 800;
        font-size: 1.85rem;
        margin-top: 15px;
        margin-bottom: 5px;
    }}

    /* 업체명 (주황색 강조) */
    .customer-title {{
        color: #FF7F50 !important;
        font-weight: bold;
        font-size: 1.45rem;
        margin-top: 30px;
        margin-bottom: 15px;
    }}

    /* 사이드바 글자 크기 조정 */
    .stSidebar [data-testid="stWidgetLabel"] p {{
        font-size: 15px !important;
        font-weight: bold;
    }}
    
    /* 구글 번역 방지 */
    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 함수 (파일 탐색 및 정제)
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
        # 엔진 지정 및 로드
        df = pd.read_excel(target_file, engine='openpyxl')
        # 모든 컬럼명 공백 제거
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        # 첫 번째 열(고객사명) 데이터 타입 통일 및 공백 제거
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()
        # 결측치 처리
        return df.fillna("-")
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

# 5. 메인 실행 로직
def main():
    # --- 헤더 영역 (로고 좌측 / 팀명 우측 하단 고정) ---
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f"""
        <div class="header-wrapper">
            {logo_html}
            <div class="team-name-fixed">품질기술팀</div>
        </div>
        """, unsafe_allow_html=True)

    # 타이틀
    st.markdown('<div class="main-title">📋 고객사양서 관리</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 10px 0; border: 0.5px solid rgba(250,250,250,0.1);'>", unsafe_allow_html=True)

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        
        # --- [중복 데이터 해결 핵심 로직] ---
        # 단순히 이름을 리스트로 넣으면 중복 발생 시 하나로 합쳐지므로,
        # '행 인덱스(0, 1, 2...)'를 옵션으로 사용합니다.
        row_indices = list(range(len(df)))

        selected_idx = st.sidebar.radio(
            "업체를 선택하세요:",
            row_indices,
            # format_func를 통해 화면에는 '업체명'만 깔끔하게 나오게 합니다.
            format_func=lambda i: df.iloc[i, 0],
            index=None
        )

        if selected_idx is not None:
            # 선택된 인덱스의 데이터를 정확하게 가져옵니다.
            row_data = df.iloc[selected_idx]
            customer_name = row_data.iloc[0]
            
            st.markdown(f'<div class="customer-title">■ {customer_name}</div>', unsafe_allow_html=True)
            
            # 상세 내용 테이블 출력
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                # 핵심 키워드 강조 (빨간색 텍스트)
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
        st.error("엑셀 데이터를 불러올 수 없습니다. 파일명을 확인해 주세요.")

if __name__ == "__main__":
    main()

