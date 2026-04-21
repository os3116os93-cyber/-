import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 다크 모드 대응 및 주황색 포인트 가독성 최적화 CSS
st.markdown("""
    <style>
    /* 1. 상단 메인 제목 글자 색상을 주황색으로 고정 */
    .stApp header[data-testid="stHeader"] + div .st-emotion-cache-1avcm0n h1 {
        color: #FF8C00 !important; /* 다크오렌지 */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        font-weight: 800;
    }
    
    /* 2. 하단 업체명(Subheader) 글자 색상을 주황색으로 고정 */
    .stApp header[data-testid="stHeader"] + div .st-emotion-cache-1avcm0n h3 {
        color: #FF7F50 !important; /* 코랄/주황 계열 */
        font-weight: bold;
    }

    /* 3. 사이드바 내부 텍스트 가독성 조정 */
    .stSidebar .st-emotion-cache-17l7u9j {
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    file_candidates = ['고객 사양서.xlsx', 'test.xlsx', '고객사양서.xlsx']
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

# 3. 메인 실행 로직
def main():
    # 메인 제목 (주황색 적용)
    st.title("📋 고객사양서 관리")
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
            
            # 업체명 표시 (주황색 적용)
            st.subheader(f"■ {selected_customer}")
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹"])
                
                # 표 스타일링: 항목명(좌측)은 회색 배경, 내용은 흰색 배경 고정
                bg_color = "#F8F9FA" 
                text_color = "black" 
                
                # 강조 대상(특이사항 등)은 빨간색으로 유지하여 시인성 확보
                item_label_color = "#E63946" if is_special else "#495057"

                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px; font-size: 14px;">
                        <div style="background-color: {bg_color}; width: 100px; min-width: 100px; padding: 10px 5px; font-weight: bold; color: {item_label_color}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 10px; color: {text_color}; font-weight: 500; background-color: white; word-break: break-all;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
            st.markdown("<br><br>", unsafe_allow_html=True)
            
        else:
            st.info("왼쪽 목록에서 업체를 선택해 주세요.")
    else:
        st.error("데이터 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

