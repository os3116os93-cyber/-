import streamlit as st
import pandas as pd
import os
import base64

# [1] 페이지 설정
st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

# [2] 데이터 로드 및 전처리 (안정성 강화)
@st.cache_data
def load_data(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = None
    
    # 파일명 매칭 (공백 무시 및 소문자 변환)
    search_name = file_name.replace(" ", "").lower()
    if not search_name.endswith(".xlsx"):
        search_name += ".xlsx"

    try:
        all_files = os.listdir(current_dir)
        for f in all_files:
            if f.replace(" ", "").lower() == search_name:
                target_path = os.path.join(current_dir, f)
                break
                
        if not target_path or not os.path.exists(target_path):
            return None
        
        # 파일별 스킵 행 설정 (품질보증기준만 5행 스킵)
        skip = 5 if "품질보증기준" in file_name else 0
        df = pd.read_excel(target_path, engine='openpyxl', skiprows=skip)
        
        # 기본 클렌징: 전체 빈 행 제거
        df = df.dropna(how='all')
        
        if not df.empty:
            # 첫 번째 열이 비어있는 데이터는 유효하지 않은 것으로 간주
            df = df.dropna(subset=[df.columns[0]])
            
            # 모든 데이터를 문자열로 변환 및 앞뒤 공백 제거
            df.columns = [str(c).strip() for c in df.columns]
            df = df.astype(str).replace(['nan', 'None', 'nan '], '').apply(lambda x: x.str.strip())
            
            # 품질보증기준 전용: ffill 및 불필요 행 제거
            if "품질보증기준" in file_name:
                mask = df.iloc[:, 0].str.contains("수요가 요청사항", na=False)
                df = df[~mask]
                df = df.replace('', None).ffill()
            
            # 고객사양서 전용: 유효 업체명 필터링
            if "사양서" in file_name:
                df = df[~df.iloc[:, 0].isin(["", "-", "None", "nan"])]
                
            return df.replace([None, ''], '-')
        return None
    except Exception as e:
        return None

# [3] 로고 이미지 Base64 변환
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path): return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

# [4] 품질보증기준 테이블 렌더링 (병합 로직)
def render_qc_table(df):
    if df is None or df.empty: return ""
    
    def get_all_spans(df):
        spans_dict = {}
        for c_idx in range(len(df.columns)):
            data_list = df.iloc[:, c_idx].tolist()
            spans, n, i = [], len(data_list), 0
            while i < n:
                count = 1
                while i + count < n and data_list[i + count] == data_list[i]:
                    count += 1
                spans.append(count)
                for _ in range(count - 1): spans.append(0)
                i += count
            spans_dict[c_idx] = spans
        return spans_dict

    all_spans = get_all_spans(df)
    html = "<table class='qc-table'><thead><tr>"
    for col in df.columns: html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"
    
    for r_idx in range(len(df)):
        html += "<tr>"
        for c_idx in range(len(df.columns)):
            val = str(df.iloc[r_idx, c_idx])
            span = all_spans[c_idx][r_idx]
            # 괄호 내용 줄바꿈
            if "(" in val and ")" in val:
                val = val.replace("(", "<br>(")
            if span > 0:
                style = "white-space: nowrap;" if c_idx < 2 else ""
                html += f"<td rowspan='{span}' style='{style}'>{val}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

# --- 세션 상태 및 스타일 ---
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

st.markdown(f"""
    <style>
    .header-wrapper {{ position: relative; width: 100%; padding-top: 10px; }}
    .brand-logo {{ height: 65px; width: auto; display: block; }}
    .team-name-fixed {{ position: absolute; right: 0; bottom: 5px; color: rgba(255, 255, 255, 0.6) !important; font-size: 14px; font-weight: 600; }}
    .main-title {{ color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; margin-top: 15px; }}
    .customer-title {{ color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }}
    .qc-table {{ width: auto; border-collapse: collapse; font-size: 12px; border: 1px solid #DEE2E6; }}
    .qc-table th, .qc-table td {{ padding: 8px 10px; border: 1px solid #DEE2E6; text-align: center !important; vertical-align: middle !important; background-color: white; }}
    .qc-table th {{ background-color: #F8F9FA; font-weight: bold; white-space: nowrap; }}
    .stSidebar [data-testid="stWidgetLabel"] p {{ font-size: 15px !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

def main():
    # 상단 헤더
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f'<div class="header-wrapper">{logo_html}<div class="team-name-fixed">품질기술팀</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">📋 품질관리 통합 시스템</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    # --- TAB 1: 고객 사양서 ---
    with tab1:
        df1 = load_data("고객 사양서.xlsx")
        if df1 is not None and not df1.empty:
            # [TypeError 해결 핵심] 명확한 문자열 리스트로 변환하여 위젯에 전달
            customer_options = df1.iloc[:, 0].unique().tolist()
            
            st.sidebar.header("🏢 고객사 목록")
            selected_name = st.sidebar.radio(
                "업체를 선택하세요:", 
                options=customer_options,
                index=None, 
                key="radio_customer_select"
            )
            
            if selected_name:
                if st.session_state.sidebar_state == "expanded":
                    st.session_state.sidebar_state = "collapsed"
                    st.rerun()
                
                # 선택된 업체명에 해당하는 행 추출
                row_data = df1[df1.iloc[:, 0] == selected_name].iloc[0]
                st.markdown(f'<div class="customer-title">■ {selected_name}</div>', unsafe_allow_html=True)
                
                # 상세 레이아웃 렌더링
                cols = row_data.index
                for i in range(1, len(cols)):
                    col_name, val = cols[i], str(row_data[i])
                    is_sp = any(k in str(col_name) for k in ["특이사항", "주의", "마킹", "포장"])
                    l_color = "#E63946" if is_sp else "#495057"
                    
                    st.markdown(f"""
                        <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                            <div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {l_color}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2; word-break: keep-all;">{col_name}</div>
                            <div style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; line-height: 1.4; color: #212529; font-weight: 500; word-break: break-all;">{val}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.button("⬅️ 목록 보기", key="btn_go_back"):
                    st.session_state.sidebar_state = "expanded"
                    st.rerun()
        else:
            st.warning("고객 사양서 데이터를 로드할 수 없습니다. 파일명을 확인해 주세요.")

    # --- TAB 2: 품질 보증 기준 ---
    with tab2:
        df2 = load_data("품질보증기준.xlsx")
        if df2 is not None:
            st.markdown('<div class="customer-title">⚖️ 항목별 품질 보증 기준</div>', unsafe_allow_html=True)
            st.markdown(render_qc_table(df2), unsafe_allow_html=True)
            st.markdown('<div class="note-box">※ 기타 수요가 요청사항은 별도 협의에 따른다</div>', unsafe_allow_html=True)
        else:
            st.error("품질보증기준 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()


    
