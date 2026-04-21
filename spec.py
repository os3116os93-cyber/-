import streamlit as st
import pandas as pd
import os
import base64

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

@st.cache_data
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"이미지 로드 오류: {e}")
        return None

LOGO_FILENAME = os.path.join(BASE_DIR, "hanjin_logo.png")
logo_base64 = get_image_base64(LOGO_FILENAME)

st.markdown("""
<style>
.header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    width: 100%;
    padding: 10px 0;
    border-bottom: 1px solid #f0f2f6;
    margin-bottom: 20px;
}
.logo-container { height: 65px; }
.brand-logo { height: 65px; width: auto; }
.team-name-fixed {
    font-size: 14px;
    font-weight: 600;
    color: rgba(0, 0, 0, 0.5);
    margin-bottom: 5px;
}
.main-title { color: #FF8C00 !important; font-weight: 800; font-size: 1.85rem; }
.customer-title { color: #FF7F50 !important; font-weight: bold; font-size: 1.45rem; margin-top: 30px; margin-bottom: 15px; }

/* ── 품질보증 테이블 wrapper: 모바일 터치 스크롤 ── */
.qc-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
}

/* ── 품질보증 테이블: 셀 내용에 핏하게 + 모바일 대응 ── */
.qc-table {
    border-collapse: collapse;
    margin-top: 10px;
    font-size: clamp(10px, 2.2vw, 12px);
    border: 1px solid #DEE2E6;
    table-layout: auto;
    white-space: nowrap;
}
.qc-table th {
    padding: clamp(4px, 1.5vw, 8px) clamp(6px, 2vw, 12px);
    border: 1px solid #DEE2E6;
    text-align: center !important;
    vertical-align: middle !important;
    background-color: #F8F9FA !important;
    color: #000000 !important;
    font-weight: bold !important;
    white-space: nowrap;
}
.qc-table td {
    padding: clamp(4px, 1.5vw, 8px) clamp(6px, 2vw, 12px);
    border: 1px solid #DEE2E6;
    text-align: center !important;
    vertical-align: middle !important;
    background-color: white !important;
    color: #000000 !important;
    font-weight: normal !important;
    white-space: nowrap;
}

.footer-note { font-size: 12.5px; color: #666; margin-top: 15px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_name, skip=0):
    file_path = os.path.join(BASE_DIR, file_name)
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_name} (경로: {file_path})")
        return None
    try:
        df = pd.read_excel(file_path, engine='openpyxl', skiprows=skip)
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        return df
    except Exception as e:
        st.error(f"{file_name} 로드 오류: {e}")
        return None


def main():
    if logo_base64:
        logo_img_html = f'<img src="data:image/png;base64,{logo_base64}" class="brand-logo">'
    else:
        logo_img_html = '<div style="color:#ccc; font-size:12px;">[한진철관 로고 미검출]</div>'

    st.markdown(f"""
    <div class="header-wrapper">
        <div class="logo-container">{logo_img_html}</div>
        <div class="team-name-fixed">품질기술팀</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">📋 품질 통합 관리 시스템</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    # ── 고객 사양서: 원안 그대로 ──
    with tab1:
        df_cust = load_data("customer.xlsx")

        if df_cust is not None:
            df_cust = df_cust.dropna(subset=[df_cust.columns[0]])
            for col in df_cust.columns:
                df_cust[col] = df_cust[col].astype(str).str.strip()

            customer_list = df_cust.iloc[:, 0].tolist()

            st.sidebar.header("🏢 고객사 목록")
            sel_idx = st.sidebar.radio(
                "업체를 선택하세요:",
                options=list(range(len(df_cust))),
                format_func=lambda i: customer_list[i],
                index=None,
                key="customer_radio"
            )

            if sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown(f'<div class="customer-title">■ {row.iloc[0]}</div>', unsafe_allow_html=True)

                for i in range(1, len(row.index)):
                    col_n, val = row.index[i], str(row.iloc[i])
                    is_sp = any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"

                    st.markdown(f"""
                    <div style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2; word-break: keep-all;">{col_n}</div>
                        <div style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; line-height: 1.4; color: #212529; font-weight: 500; word-break: break-all;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── 품질보증 기준: 모바일 최적화 ──
    with tab2:
        st.markdown('<div class="customer-title">⚖️ 품질 보증 표준 가이드</div>', unsafe_allow_html=True)

        df_qc = load_data("standard.xlsx", skip=5)

        if df_qc is not None:
            col_count = len(df_qc.columns)
            row_count = len(df_qc)

            all_spans = []
            for c in range(col_count):
                col_data = df_qc.iloc[:, c].fillna('').astype(str).tolist()
                spans = []
                i = 0
                while i < row_count:
                    curr = col_data[i].strip()
                    count = 1
                    if curr != "":
                        while i + count < row_count and col_data[i + count].strip() == "":
                            count += 1
                    spans.append(count)
                    for _ in range(count - 1):
                        spans.append(0)
                    i += count
                all_spans.append(spans)

            # ✅ wrapper로 감싸서 모바일 가로 스크롤 지원
            table_html = '<div class="qc-table-wrapper"><table class="qc-table"><thead><tr>'
            for col in df_qc.columns:
                table_html += f'<th>{col}</th>'
            table_html += '</tr></thead><tbody>'

            for r in range(row_count):
                table_html += '<tr>'
                for c in range(col_count):
                    span_val = all_spans[c][r]
                    if span_val > 0:
                        cell_content = str(df_qc.iloc[r, c]).replace("nan", "").replace("(", "<br>(")
                        table_html += f'<td rowspan="{span_val}">{cell_content}</td>'
                table_html += '</tr>'

            table_html += '</tbody></table></div>'

            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown('<div class="footer-note">※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

    
