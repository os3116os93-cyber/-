import streamlit as st
import pandas as pd
import os
import base64

# 1. 페이지 설정 (title은 브라우저 탭에 뜹니다)
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# 2. 로컬 이미지를 웹용으로 변환하는 함수 (성공률 100%)
@st.cache_data
def get_image_base64(file_path):
    # 만약 이미지 파일이 없으면 에러 없이 빈 문자열 반환
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# --- 여기에 로고 파일명을 적으세요 (깃허브에 같이 올려야 함) ---
LOGO_FILENAME = "logo.png" 
# ---------------------------------------------------------

# 로고 이미지 가져오기
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. 다크 모드 대응 및 로고/팀명 레이아웃 CSS 최적화
st.markdown(f"""
    <style>
    /* 기본 스타일 최적화 (가독성 향상) */
    .stApp {{
        background-color: #0E1117; /* 다크 모드 배경색 고정 */
        color: #FFFFFF !important;
    }}
    
    /* 상단 헤더 영역 (로고 + 팀명) 레이아웃 */
    /* 사진 속 도형 위치를 정밀하게 재현합니다. */
    .brand-logo {{
        height: 30px; /* 로고 이미지 크기 최적화 */
        width: auto;
        vertical-align: middle;
        margin-right: 15px; /* 로고와 텍스트 사이 간격 */
    }}
    
    .team-name {{
        color: rgba(250, 250, 250, 0.6) !important;
        font-size: 13px;
        font-weight: 500;
        vertical-align: middle;
        display: inline-block;
        padding-top: 5px;
    }}

    /* 번역 방지 */
    .notranslate {{ translate: no !important; }}
    </style>
    <script>
        document.documentElement.classList.add('notranslate');
    </script>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 함수 (파일 확장자 통합 대응)
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

# 5. 메인 실행 로직
def main():
    # --- 좌상단 이미지 + 우상단 팀명 HTML 적용 ---
    if logo_base64:
        # 로고 파일이 있을 때 (보내주신 이미지 적용)
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; margin-bottom: 20px; border-bottom: 1px solid rgba(250, 250, 250, 0.1);">
                <div>
                    <img src="data:image/png;base64,{logo_base64}" class="brand-logo" alt="logo">
                </div>
                <div class="team-name">품질기술팀</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # 로고 파일이 없을 때 (팀명만 우측 배치)
        st.markdown("""
            <div style="display: flex; justify-content: flex-end; align-items: center; padding: 10px 0; margin-bottom: 20px; border-bottom: 1px solid rgba(250, 250, 250, 0.1);">
                <div class="team-name">품질기술팀</div>
            </div>
            """, unsafe_allow_html=True)
    # ---------------------------------------------

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
            
            # 업체명 표시 (subheader 대신 markdown으로 색상 제어)
            st.markdown(f"""<h3 style="color: #FF7F50 !important; font-weight: bold; margin-bottom: 20px;">■ {selected_customer}</h3>""", unsafe_allow_html=True)
            
            cols = row_data.index[1:]
            for col_name in cols:
                val = str(row_data[col_name])
                # 특이사항 키워드 강조용
                is_special = any(keyword in str(col_name) for keyword in ["특이사항", "주의", "마킹", "포장"])
                
                # 표 스타일링 (다크 모드에서도 가독성 확보)
                bg_color = "#f9f9f9" # 아주 연한 회색 (항목명 배경)
                text_color = "#212529" # 검은색 계열 (내용 글자)
                item_label_color = "#E63946" if is_special else "#495057" # 빨간색 강조

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

