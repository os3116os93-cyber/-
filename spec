import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 2. 데이터 로드 함수
@st.cache_data
def load_data():
    # 깃허브 및 배포 환경 호환성을 위해 파일명 후보 설정
    # 데이터 파일명도 되도록 영문(test.xlsx 등)을 포함하는 것이 안전합니다.
    file_candidates = ['test.xlsx', 'test.csv', '고객 사양서.xlsx', '고객 사양서.csv']
    target_file = next((f for f in file_candidates if os.path.exists(f)), None)
    
    if not target_file:
        return None
    
    try:
        if target_file.endswith('.csv'):
            try:
                # 깃허브 환경에서는 utf-8-sig가 표준입니다.
                df = pd.read_csv(target_file, encoding='utf-8-sig')
            except:
                # 로컬 작업 파일이 cp949(EUC-KR)일 경우 대비
                df = pd.read_csv(target_file, encoding='cp949')
        else:
            df = pd.read_excel(target_file)
        
        # 첫 번째 컬럼(고객사명)의 공백 제거 및 결측치 처리
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        return df.fillna("-")
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None

# 3. 메인 실행 로직
def main():
    # 앱 상단 제목 (한글 사용 가능)
    st.title("📋 고객사양서 관리 시스템")
    st.markdown("---")

    df = load_data()

    # 자동으로 파일을 찾지 못한 경우 (파일명 불일치 등)
    if df is None:
        st.warning("데이터 파일(test.xlsx 또는 test.csv)을 찾을 수 없습니다.")
        st.info("파일명을 'test.xlsx'로 변경하여 업로드하거나 아래 버튼을 통해 직접 선택하세요.")
        uploaded_file = st.file_uploader("엑셀 또는 CSV 파일을 업로드해주세요.", type=['xlsx', 'csv'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                df = df.fillna("-")
            except Exception as e:
                st.error(f"파일 읽기 실패: {e}")

    if df is not None:
        # 좌측 사이드바: 고객사 목록 구성
        st.sidebar.header("🏢 고객사 목록")
        
        # 첫 번째 열을 기준으로 고객사 리스트 생성
        customer_list = df.iloc[:, 0].astype(str).tolist()
        
        selected_customer = st.sidebar.radio(
            "조회할 업체를 선택하세요:",
            customer_list,
            index=None,
            help="목록에서 업체를 클릭하면 상세 사양이 표시됩니다."
        )

        # 우측 메인 화면: 상세 사양 표시 섹션
        if selected_customer:
            # 선택된 고객사의 행 데이터 추출
            row_data = df[df.iloc[:, 0].astype(str) == selected_customer].iloc[0]
            
            st.subheader(f"■ {selected_customer} 상세 사양")
            
            # 사양 항목들 (첫 번째 컬럼 제외)
            cols = row_data.index[1:]
            
            for col_name in cols:
                val = str(row_data[col_name])
                
                # 특이사항/주의사항/마킹 키워드 강조 로직
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹"])
                
                # 시각적 구분을 위한 HTML 스타일링
                bg_color = "#F2F2F2"  # 항목 배경색
                text_color = "red" if is_special else "black"
                font_weight = "bold" if is_special else "normal"

                # 표 형태의 레이아웃 구현
                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #CCCCCC; margin-bottom: -1px;">
                        <div style="background-color: {bg_color}; width: 220px; padding: 12px; font-weight: bold; color: #333333; border-right: 1px solid #CCCCCC; display: flex; align-items: center;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 12px; color: {text_color}; font-weight: {font_weight}; background-color: white; line-height: 1.5;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
            
            # 하단 여백 추가
            st.markdown("<br><br>", unsafe_allow_html=True)
            
        else:
            # 초기 상태 안내
            st.info("왼쪽 사이드바의 목록에서 사양을 조회할 고객사를 선택하세요.")
            
    else:
        st.info("데이터 파일이 로드되지 않았습니다. 파일을 확인해 주세요.")

if __name__ == "__main__":
    main()



    
