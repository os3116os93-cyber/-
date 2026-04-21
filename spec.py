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

# 2. 로컬 이미지를 웹용으로 변환하는 함수
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- 깃허브에 올린 로고 파일명 (실제 파일명과 똑같이 수정하세요) ---
LOGO_FILENAME = "한진철관CI 누끼.png" 
# ---------------------------------------------------------

logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. CSS 스타일 (주황색 타이틀 및 레이아웃 조정)
st.markdown(f"""
    <style>
    /* 상단 헤더 영역 레이아웃 */
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid rgba(250, 250, 250, 0.1);
        margin-bottom: 20px;
    }}
    
    .brand-logo {{
        height: 35px;
        width: auto;
    }}
    
    /* 품질기술팀 문구: 기존보다 1포인트 키움 (14px) */
    .team-name {{
        color: rgba(250, 250, 250, 0.8) !important;
        font-size: 14px;
        font-weight: 600;
    }}

    /* 메인 타이틀: 주황색 고정 */
    .main-title {{
        color: #FF8C00 !important;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }}
    
    /* 업체명 타이틀: 주황색 고정 */
    .customer-title {{
        color: #FF7F50 !important;
        font-weight: bold;
        font-size: 1.4rem;
        margin-top: 20px;
        margin-bottom: 15px;
    }}

    /* 번역 방지 */
    .notranslate {{ translate: no !important; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 함수
@st.cache_data
def load_data():
    file_candidates = ['고객 사양서.xlsx', '고객사양서.xlsx', 'test.xlsx', '고객 사양서.csv']
    target_file = None
    for f in file_candidates:
        if os.path.exists(f):
            target_file = f
            break
    
    if not target_file:
        return None
    
    try:
        if target_file.endswith('.csv'):
            try:
                df = pd.read_csv(target_file, encoding='utf-8-sig')
            except:
                df = pd.read_csv(target_file, encoding='cp949')
        else:
            df = pd.read_excel(target_file, engine='openpyxl')
        
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        return df.fillna("-")
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None

# 5. 메인 실행 로직
def main():
    # --- 최상단 로고 및 품질기술팀 배치 ---
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f"""
        <div class="header-container">
            {logo_html}
            <div class="team-name">품질기술팀</div>
        </div>
        """, unsafe_allow_html=True)

    # --- 메인 타이틀 (주황색) ---
    st.markdown('<div class="main-title">📋 고객사양서 관리</div>', unsafe_allow_html=True)
    st.markdown("---")

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        customer_list = df.iloc[:, 0].astype(str).tolist()
        
        selected_customer = st.sidebar.radio(
            "업체를 선택하세요:",
            customer_list,
            index=None
        )

        if selected_customer:
            row_data = df[df.iloc[:, 0].astype(str) == selected_customer].iloc[0]
            
            # --- 업체명 표시 (주황색) ---
            st.markdown(f'<div class="customer-title">■ {selected_customer}</div>', unsafe_allow_html=True)
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹", "포장"])
                
                bg_color = "#f9f9f9" 
                text_color = "#212529" 
                item_label_color = "#E63946" if is_special else "#495057"

                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: {bg_color}; width: 80px; min-width: 80px; padding: 10px 4px; 
                                    font-weight: bold; color: {item_label_color}; border-right: 1px solid #DEE2E6; 
                                    display: flex; align-items: center; justify-content: center; text-align: center; 
                                    font-size: 12px; line-height: 1.2; word-break: keep-all;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 10px; color: {text_color}; font-weight: 500; 
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
        # 엑셀 파일이 없을 때 메시지
        st.error("데이터 파일(엑셀)을 찾을 수 없습니다. 파일명이 '고객 사양서.xlsx'인지 확인해 주세요.")

if __name__ == "__main__":
    main()

