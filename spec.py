import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 다크 모드 대응 및 UI 최적화 CSS
st.markdown("""
    <style>
    /* 1. 상단 메인 제목 주황색 고정 */
    .stApp h1 {
        color: #FF8C00 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        font-weight: 800;
        font-size: 1.8rem !important;
    }
    
    /* 2. 하단 업체명 주황색 고정 */
    .stApp h3 {
        color: #FF7F50 !important;
        font-weight: bold;
        font-size: 1.4rem !important;
    }

    /* 3. 사이드바 라디오 버튼 글자 크기 조정 */
    .stSidebar [data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
        font-weight: bold;
    }
    
    /* 브라우저 번역 방지 */
    .notranslate { translate: no !important; }
    </style>
    <script>
        document.documentElement.classList.add('notranslate');
    </script>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 함수 (파일 확장자 통합 대응)
@st.cache_data
def load_data():
    # 깃허브에 올릴 가능성이 있는 파일명들
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

# 3. 메인 실행 로직
def main():
    st.title("📋 고객사양서 관리")
    st.markdown("---")

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        # 첫 번째 열이 업체명이라고 가정
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
                # 특이사항 키워드 강조용
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹", "포장"])
                
                # 가독성을 위한 배경색 설정
                bg_color = "#F8F9FA" 
                text_color = "#212529" 
                item_label_color = "#E63946" if is_special else "#495057"

                # --- 모바일 최적화 표 레이아웃 ---
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
        st.error("데이터 파일(엑셀)을 찾을 수 없습니다. GitHub에 엑셀 파일이 있는지 확인해 주세요.")

if __name__ == "__main__":
    main()




