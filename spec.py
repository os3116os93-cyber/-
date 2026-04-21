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
    # 깃허브 환경에서 한글 파일명을 인식하기 위한 리스트
    # 공백이나 인코딩 문제가 생길 수 있어 여러 후보를 넣었습니다.
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
            # 엔진을 openpyxl로 명시하여 엑셀 로딩 안정성 확보
            df = pd.read_excel(target_file, engine='openpyxl')
        
        # 첫 번째 컬럼(고객사명) 공백 제거
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
        return df.fillna("-")
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None

# 3. 메인 실행 로직
def main():
    st.title("📋 고객사양서 관리 시스템")
    st.markdown("---")

    df = load_data()

    if df is not None:
        st.sidebar.header("🏢 고객사 목록")
        customer_list = df.iloc[:, 0].astype(str).tolist()
        
        selected_customer = st.sidebar.radio(
            "조회할 업체를 선택하세요:",
            customer_list,
            index=None
        )

        if selected_customer:
            row_data = df[df.iloc[:, 0].astype(str) == selected_customer].iloc[0]
            st.subheader(f"■ {selected_customer} 상세 사양")
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                is_special = any(k in str(col_name) for k in ["특이사항", "주의", "마킹"])
                
                text_color = "red" if is_special else "black"
                font_weight = "bold" if is_special else "normal"

                st.markdown(
                    f"""
                    <div style="display: flex; border: 1px solid #CCCCCC; margin-bottom: -1px;">
                        <div style="background-color: #F2F2F2; width: 220px; padding: 12px; font-weight: bold; border-right: 1px solid #CCCCCC;">
                            {col_name}
                        </div>
                        <div style="flex: 1; padding: 12px; color: {text_color}; font-weight: {font_weight}; background-color: white;">
                            {val}
                        </div>
                    </div>
                    """, unsafe_allow_html=True
                )
        else:
            st.info("왼쪽 목록에서 업체를 선택해 주세요.")
    else:
        # 파일이 없을 때 메시지
        st.error("데이터 파일('고객 사양서.xlsx')을 찾을 수 없습니다.")
        st.info("팁: 깃허브의 엑셀 파일 이름을 'test.xlsx'로 바꾸면 더 잘 인식됩니다.")

if __name__ == "__main__":
    main()

