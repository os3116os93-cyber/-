import streamlit as st
import pandas as pd
import os

# 1. 페이지 기본 설정 및 브라우저 번역 오류 방지
st.set_page_config(
    page_title="한진철관 사양 관리 시스템",
    page_icon="📋",
    layout="wide"
)

# 브라우저 번역기 작동 시 발생하는 'removeChild' 에러 방지 태그
st.markdown("""
    <html lang="ko">
    <style>
        /* 폰트 및 배경 설정 */
        .main { background-color: #f8f9fa; }
        .stAlert { margin-top: 10px; }
        /* 번역 방지 클래스 */
        .notranslate { translate: no !important; }
    </style>
    <script>
        document.documentElement.classList.add('notranslate');
    </script>
    """, unsafe_allow_html=True)

# 2. 데이터 불러오기 함수 (인코딩 완벽 대응)
def load_data():
    file_candidates = ['고객 사양서.xlsx - Sheet1.csv', '고객 사양서.xlsx', '고객 사양서.csv']
    target_file = next((f for f in file_candidates if os.path.exists(f)), None)
    
    if not target_file:
        st.error("❌ 폴더 내에서 데이터 파일(CSV 또는 엑셀)을 찾을 수 없습니다.")
        return None
    
    try:
        if target_file.endswith('.csv'):
            # 엑셀용 CSV(cp949) -> 일반 CSV(utf-8) 순서로 시도
            try:
                df = pd.read_csv(target_file, encoding='cp949')
            except:
                df = pd.read_csv(target_file, encoding='utf-8-sig')
        else:
            df = pd.read_excel(target_file)
        
        # 모든 데이터를 문자열로 변환하고 빈칸 채우기
        return df.fillna("-").astype(str)
    except Exception as e:
        st.error(f"⚠️ 파일 로드 중 오류 발생: {e}")
        return None

# 3. 메인 화면 구성
st.title("🏭 한진철관 사양 관리 (모바일)")

df = load_data()

if df is not None:
    # 사이드바: 고객사 선택
    st.sidebar.header("고객사 목록")
    customer_list = df.iloc[:, 0].tolist()
    selected_customer = st.sidebar.selectbox("업체를 선택하세요", customer_list)

    if selected_customer:
        # 선택된 데이터 추출
        row_data = df[df.iloc[:, 0] == selected_customer].iloc[0]
        
        st.subheader(f"🔍 {selected_customer} 상세 정보")
        st.divider()

        # 스마트폰 세로 화면에 최적화하여 나열
        cols = df.columns[1:]
        for col_name in cols:
            val = row_data[col_name]
            
            # 특이사항, 주의, 마킹 단어가 포함되면 빨간색 강조
            is_special = any(k in col_name for k in ["특이사항", "주의", "마킹"])
            
            if is_special:
                st.error(f"🚨 **{col_name}**\n\n{val}")
            else:
                # 일반 항목은 확장 가능 상자로 표시 (가독성)
                with st.expander(f"📌 {col_name}", expanded=True):
                    st.write(val)

                    