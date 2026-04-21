import streamlit as st
import pandas as pd
import os
import base64

# [1] 페이지 설정
st.set_page_config(page_title="고객사양서 - 품질기술팀", page_icon="📋", layout="wide")

# [2] 데이터 로드 및 전처리
@st.cache_data
def load_data(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = None
    
    # 파일명 매칭 (공백 제거 및 소문자화하여 호환성 확보)
    search_name = file_name.replace(" ", "").lower()
    if not search_name.endswith(".xlsx"):
        search_name += ".xlsx"

    all_files = os.listdir(current_dir)
    for f in all_files:
        if f.replace(" ", "").lower() == search_name:
            target_path = os.path.join(current_dir, f)
            break
    
    if not target_path or not os.path.exists(target_path):
        return None
    
    try:
        # [수정] "품질보증기준" 파일의 경우 상단 5행 스킵 (기존 11.xlsx 로직)
        skip = 5 if "품질보증기준" in file_name else 0
        df = pd.read_excel(target_path, engine='openpyxl', skiprows=skip)
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.astype(str).apply(lambda x: x.str.strip())
        
        # [수정] 품질보증기준 전용 전처리 logic
        if "품질보증기준" in file_name:
            df = df.replace(['nan', 'None', ""], None)
            mask = df.iloc[:, 0].str.contains("수요가 요청사항", na=False)
            df = df[~mask] 
            df = df.ffill() 
        
        if "사양서" in file_name:
            df = df[df.iloc[:, 0] != "nan"]
            df = df[df.iloc[:, 0] != ""]
            
        return df.replace('nan', '-')
    except:
        return None

# [3] 로고 이미지 변환
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path): return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

# [4] 품질보증기준 전용 테이블 render 함수
def render_qc_table(df):
    if df is None or df.empty: return ""
    
    def get_all_spans(df):
        spans_dict = {}
        for c_idx in range(len(df.columns)):
            data_list = df.iloc[:, c_idx].tolist()
            spans = []
            n = len(data_list)
            i = 0
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
            val = df.iloc[r_idx, c_idx]
            span = all_spans[c_idx][r_idx]
            
            # 괄호 내용을 다음 줄로 (<br> 삽입)
            if "(" in val and ")" in val:
                val = val.replace("(", "<br>(")
            
            if span > 0:
                # 1, 2열은 텍스트 줄바꿈 방지(nowrap)
                style = "white-space: nowrap;" if c_idx < 2 else ""
                html += f"<td rowspan='{span}' style='{style}'>{val}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

# --- 초기 설정 및 로고 ---
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# --- CSS 스타일 ---
st.markdown(f"""
    <style>
    .header-wrapper {{ position: relative; width: 100%; padding-top: 10px; }}
    .brand-logo {{ height: 65px; width: auto; display: block; }}
    .team-name-fixed {{ position: absolute; right: 0; bottom: 5px; color: rgba(255, 255, 255, 0.6) !important; font-size: 14px; font-weight: 600; }}
    .main-title {{ color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; margin-top: 15px; }}
    .customer-title {{ color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }}
    
    .qc-table {{ width: auto; border-collapse: collapse; font-size: 12px; border: 1px solid #DEE2E6; margin-left: 0; }}
    .qc-table th, .qc-table td {{ padding: 8px 10px; border: 1px solid #DEE2E6; text-align: center !important; vertical-align: middle !important; background-color: white; line-height: 1.4; }}
    .qc-table th {{ background-color: #F8F9FA; font-weight: bold; white-space: nowrap; }}
    
    .qc-table td:nth-child(1) {{ min-width: 60px; }}
    .qc-table td:nth-child(2) {{ min-width: 80px; }}
    .qc-table td:nth-child(3) {{ min-width: 150px; max-width: 250px; }}
    .qc-table td:nth-child(4) {{ min-width: 150px; max-width: 250px; }}

    .note-box {{ background-color: #FFF3CD; border-left: 5px solid #FFA000; padding: 12px; margin-top: 15px; font-weight: bold; color: #856404; font-size: 13.5px; }}
    .stSidebar [data-testid="stWidgetLabel"] p {{ font-size: 15px !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

def main():
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f'<div class="header-wrapper">{logo_html}<div class="team-name-fixed">품질기술팀</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">📋 품질관리 통합 시스템</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    # --- TAB 1: 고객 사양서 ---
    with tab1:
        df1 = load_data("고객 사양서.xlsx")
        if df1 is not None:
            st.sidebar.header("🏢 고객사 목록")
            sel_idx = st.sidebar.radio("업체를 선택하세요:", range(len(df1)), format_func=lambda i: df1.iloc[i, 0], index=None, key="t1")
            if sel_idx is not None:
                if st.session_state.sidebar_state == "expanded":
                    st.session_state.sidebar_state = "collapsed"; st.rerun()
                row = df1.iloc[sel_idx]
                st.markdown(f'<div class="customer-title">■ {row.iloc[0]}</div>', unsafe_allow_html=True)
                for i in range(1, len(row.index)):
                    col, val = row.index[i], str(row[i])
                    is_sp = any(k in str(col) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"
                    st.markdown(f"""
                        <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                            <div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2; word-break: keep-all;">{col}</div>
                            <div style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; line-height: 1.4; color: #212529; font-weight: 500; word-break: break-all;">{val}</div>
                        </div>
                    """, unsafe_allow_html=True)
                if st.button("⬅️ 목록 보기", key="b_back"): st.session_state.sidebar_state = "expanded"; st.rerun()
        else: st.error("고객 사양서 파일을 찾을 수 없습니다.")

    # --- TAB 2: 품질 보증 기준 ---
    with tab2:
        df2 = load_data("품질보증기준.xlsx")
        if df2 is not None:
            st.markdown('<div class="customer-title">⚖️ 항목별 품질 보증 기준</div>', unsafe_allow_html=True)
            st.markdown(render_qc_table(df2), unsafe_allow_html=True)
            st.markdown('<div class="note-box">※ 기타 수요가 요청사항은 별도 협의에 따른다</div>', unsafe_allow_html=True)
        else: st.error("품질보증기준 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

    
