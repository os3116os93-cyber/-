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

# 2. 로고 이미지 변환 함수
@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path): return ""
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

# --- 로고 파일명 및 데이터 로드 ---
LOGO_FILENAME = "hanjin_logo.png" 
logo_base64 = get_image_base64(LOGO_FILENAME)

# 3. UI 스타일 (로고/팀명 복구 및 품질표 스타일 유지)
st.markdown(f"""
    <style>
    /* [복구] 상단 헤더 영역 레이아웃 */
    .header-wrapper {{
        position: relative;
        width: 100%;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }}
    
    /* [복구] 좌측 한진철관 로고 */
    .brand-logo {{
        height: 65px; 
        width: auto;
    }}
    
    /* [복구] 우측 품질기술팀 문구 */
    .team-name-fixed {{
        font-size: 14px;
        font-weight: 600;
        color: rgba(0, 0, 0, 0.5) !important; /* 가독성을 위해 반투명 검정 */
        letter-spacing: -0.5px;
        align-self: flex-end;
        padding-bottom: 10px;
    }}

    .main-title {{ color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; margin-top: 10px; }}
    .customer-title {{ color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }}
    
    /* 품질보증기준 테이블 스타일 (중앙정렬, 배경제거, 일반두께, 검정글씨) */
    .qc-table {{ 
        width: auto; 
        min-width: 600px; 
        border-collapse: collapse; 
        margin-top: 10px; 
        font-size: 12px; 
        border: 1px solid #DEE2E6; 
    }}
    .qc-table th, .qc-table td {{ 
        padding: 8px 12px; 
        border: 1px solid #DEE2E6; 
        text-align: center !important;
        vertical-align: middle !important;
        background-color: white !important;
        color: #000000 !important;
        font-weight: normal !important;
        white-space: nowrap; 
    }}
    .qc-table td:nth-child(3), .qc-table td:nth-child(4) {{
        white-space: normal; 
        min-width: 220px;
        max-width: 450px;
    }}
    
    .footer-note {{ font-size: 12.5px; color: #666; margin-top: 15px; font-weight: 500; }}
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드 및 병합 로직
def get_rowspan_data(df):
    col_count = len(df.columns)
    row_count = len(df)
    all_spans = []
    for c in range(col_count):
        col_data = df.iloc[:, c].astype(str).replace('nan', '').tolist()
        spans = []
        i = 0
        while i < row_count:
            curr = col_data[i].strip()
            count = 1
            if curr != "":
                while i + count < row_count and col_data[i+count].strip() == "":
                    count += 1
            spans.append(count)
            for _ in range(count - 1): spans.append(0)
            i += count
        all_spans.append(spans)
    return all_spans

@st.cache_data
def load_excel_data(file_name, skip_rows=0):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(current_dir, file_name)
    if not os.path.exists(target_path): return None
    try:
        df = pd.read_excel(target_path, engine='openpyxl', skiprows=skip_rows)
        # ※ 행 제거
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        return df
    except: return None

def main():
    # [복구] 로고와 팀명을 포함한 헤더 렌더링
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">' if logo_base64 else '<div></div>'
    st.markdown(f"""
        <div class="header-wrapper">
            {logo_html}
            <div class="team-name-fixed">품질기술팀</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    # --- TAB 1: 고객 사양서 ---
    with tab1:
        df_cust = load_excel_data("고객 사양서.xlsx")
        if df_cust is not None:
            df_cust = df_cust.dropna(subset=[df_cust.columns[0]]).astype(str).apply(lambda x: x.str.strip())
            st.sidebar.header("🏢 고객사 목록")
            sel_idx = st.sidebar.radio("업체를 선택하세요:", range(len(df_cust)), format_func=lambda i: df_cust.iloc[i, 0], index=None)
            if sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown(f'<div class="customer-title">■ {row.iloc[0]}</div>', unsafe_allow_html=True)
                for i in range(1, len(row.index)):
                    col_n, val = row.index[i], str(row[i])
                    is_sp = any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"
                    st.markdown(f"""
                        <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                            <div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2; word-break: keep-all;">{col_n}</div>
                            <div style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; line-height: 1.4; color: #212529; font-weight: 500; word-break: break-all;">{val}</div>
                        </div>""", unsafe_allow_html=True)

    # --- TAB 2: 품질 보증 기준 ---
    with tab2:
        st.markdown('<div class="customer-title">⚖️ 품질 보증 표준 가이드</div>', unsafe_allow_html=True)
        df_qc = load_excel_data("품질보증기준.xlsx", skip_rows=5)
        
        if df_qc is not None:
            all_spans = get_rowspan_data(df_qc)
            table_html = '<table class="qc-table"><thead><tr>'
            for col in df_qc.columns:
                table_html += f'<th>{col}</th>'
            table_html += '</tr></thead><tbody>'
            
            for r in range(len(df_qc)):
                table_html += '<tr>'
                for c in range(len(df_qc.columns)):
                    span_val = all_spans[c][r]
                    if span_val > 0:
                        cell_content = str(df_qc.iloc[r, c]).replace("nan", "").replace("(", "<br>(")
                        table_html += f'<td rowspan="{span_val}">{cell_content}</td>'
                table_html += '</tr>'
            table_html += '</tbody></table>'
            
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown('<div class="footer-note">※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

    
