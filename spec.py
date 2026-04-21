import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 모바일 최적화를 위한 커스텀 CSS (글자 색상 및 테이블 스타일)
st.markdown("""
    <style>
    /* 기본 글자 색상을 검정으로 고정 */
    .stApp {
        color: black;
    }
    /* 사이드바 라디오 버튼 글자 크기 조정 */
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
            st.subheader(f"■ {selected_customer}")
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                # 강조 키워드
                is_special = any(k in str(col_name) for k in ["특이사항", "주의", "마킹"])
                
                # 모바일 최적화 스타일링
                # 항목명(좌측) 너비를 100px로 축소하여 내용 공간 확보
                bg_color = "#F8F9FA" 
                text_color = "#E63946" if is_special else "#212529" # 강조는 빨강, 기본은 진한 회색(검정)
                font_weight = "bold" if is_special else "500"

                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px; font-size: 14px;">
                        <div style="background-color: {bg_color}; width: 90px; min-width: 90px; padding: 10px 5px; font-weight: bold; color: #495057; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 10px; color: {text_color}; font-weight: {font_weight}; background-color: white; word-break: break-all;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.info("왼쪽 목록에서 업체를 선택해 주세요.")
    else:
        st.error("데이터 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

