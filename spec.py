import streamlit as st
import pandas as pd
import os
import base64
import gspread
from google.oauth2.service_account import Credentials

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin1234")
SHEET_ID = st.secrets.get("SHEET_ID", "")
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

st.set_page_config(
    page_title="고객사양서 - 품질기술팀",
    page_icon="📋",
    layout="wide"
)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False


@st.cache_data(ttl=300)
def get_image_base64(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"이미지 로드 오류: {e}")
        return None


def get_gsheet():
    """Google Sheets 연결"""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet


@st.cache_data(ttl=300)
def load_customer_data():
    """Google Sheets에서 고객사 데이터 로드"""
    try:
        sheet = get_gsheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty:
            return df
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        df = df.dropna(subset=[df.columns[0]])
        df = df[df.iloc[:, 0].astype(str).str.strip() != ""]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Google Sheets 로드 오류: {e}")
        return None


@st.cache_data(ttl=300)
def load_standard_data():
    """standard.xlsx 로컬 파일 로드 (품질보증 기준은 그대로 유지)"""
    file_path = os.path.join(BASE_DIR, "standard.xlsx")
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: standard.xlsx")
        return None
    try:
        df = pd.read_excel(file_path, engine="openpyxl", skiprows=5)
        df = df[~df.iloc[:, 0].astype(str).str.contains("※", na=False)]
        return df
    except Exception as e:
        st.error(f"standard.xlsx 로드 오류: {e}")
        return None


def save_to_gsheet(df):
    """전체 데이터프레임을 Google Sheets에 저장"""
    try:
        sheet = get_gsheet()
        sheet.clear()
        # 헤더 + 데이터 업로드
        values = [df.columns.tolist()] + df.fillna("").values.tolist()
        sheet.update(values)
        load_customer_data.clear()
        return True
    except Exception as e:
        st.error(f"저장 오류: {e}")
        return False


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
.admin-badge {
    background-color: #FF8C00;
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    margin-left: 10px;
}
.qc-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    width: 100%;
}
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


def render_header():
    if logo_base64:
        logo_img_html = f"<img src=data:image/png;base64,{logo_base64} class=brand-logo>"
    else:
        logo_img_html = "<div style=color:#ccc; font-size:12px;>[한진철관 로고 미검출]</div>"
    admin_badge = "<span class=admin-badge>🔓 관리자 모드</span>" if st.session_state.is_admin else ""
    st.markdown(f"""
    <div class="header-wrapper">
        <div class="logo-container">{logo_img_html}</div>
        <div class="team-name-fixed">품질기술팀{admin_badge}</div>
    </div>
    """, unsafe_allow_html=True)


def render_admin_login():
    st.sidebar.markdown("---")
    if not st.session_state.is_admin:
        with st.sidebar.expander("🔐 관리자 로그인"):
            pw = st.text_input("비밀번호", type="password", key="admin_pw_input")
            if st.button("로그인", key="admin_login_btn"):
                if pw == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("비밀번호가 틀렸습니다.")
    else:
        if st.sidebar.button("🔒 관리자 로그아웃"):
            st.session_state.is_admin = False
            st.session_state.edit_idx = None
            st.session_state.show_add_form = False
            st.rerun()


def render_add_form(df):
    st.markdown("### ➕ 고객사 추가")
    cols = df.columns.tolist()
    new_values = {}
    col_pairs = [cols[i:i+2] for i in range(0, len(cols), 2)]
    for pair in col_pairs:
        form_cols = st.columns(2)
        for j, col_name in enumerate(pair):
            new_values[col_name] = form_cols[j].text_input(col_name, key=f"add_{col_name}")
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="add_save"):
        if not new_values.get(cols[0], "").strip():
            st.error("고객사명은 필수 입력입니다.")
        else:
            new_row = pd.DataFrame([new_values])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            if save_to_gsheet(updated_df):
                st.session_state.show_add_form = False
                st.success(f"{new_values[cols[0]]} 고객사가 추가되었습니다!")
                st.rerun()
    if c2.button("취소", key="add_cancel"):
        st.session_state.show_add_form = False
        st.rerun()


def render_edit_form(df, idx):
    row = df.iloc[idx]
    st.markdown(f"### ✏️ 수정 중: {row.iloc[0]}")
    cols = df.columns.tolist()
    updated_values = {}
    col_pairs = [cols[i:i+2] for i in range(0, len(cols), 2)]
    for pair in col_pairs:
        form_cols = st.columns(2)
        for j, col_name in enumerate(pair):
            current_val = str(row[col_name]) if str(row[col_name]) not in ("", "nan") else ""
            updated_values[col_name] = form_cols[j].text_input(col_name, value=current_val, key=f"edit_{col_name}")
    c1, c2 = st.columns([1, 5])
    if c1.button("저장", key="edit_save"):
        for col_name, val in updated_values.items():
            df.at[idx, col_name] = val
        if save_to_gsheet(df):
            st.session_state.edit_idx = None
            st.success("수정이 완료되었습니다!")
            st.rerun()
    if c2.button("취소", key="edit_cancel"):
        st.session_state.edit_idx = None
        st.rerun()


def main():
    render_header()
    st.markdown("<div class=main-title>📋 품질 통합 관리 시스템</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 고객 사양서", "⚖️ 품질 보증 기준"])

    with tab1:
        df_cust = load_customer_data()

        if df_cust is not None and not df_cust.empty:
            customer_list = df_cust.iloc[:, 0].tolist()

            st.sidebar.header("🏢 고객사 목록")

            if st.session_state.is_admin:
                if st.sidebar.button("➕ 고객사 추가", key="open_add_form"):
                    st.session_state.show_add_form = True
                    st.session_state.edit_idx = None

            sel_idx = st.sidebar.radio(
                "업체를 선택하세요:",
                options=list(range(len(df_cust))),
                format_func=lambda i: customer_list[i],
                index=None,
                key="customer_radio"
            )

            if st.session_state.is_admin and st.session_state.show_add_form:
                render_add_form(df_cust)

            elif st.session_state.is_admin and st.session_state.edit_idx is not None:
                render_edit_form(df_cust, st.session_state.edit_idx)

            elif sel_idx is not None:
                row = df_cust.iloc[sel_idx]
                st.markdown(f"<div class=customer-title>■ {row.iloc[0]}</div>", unsafe_allow_html=True)

                if st.session_state.is_admin:
                    a1, a2, _ = st.columns([1, 1, 8])
                    if a1.button("✏️ 수정", key="edit_btn"):
                        st.session_state.edit_idx = sel_idx
                        st.session_state.show_add_form = False
                        st.rerun()
                    if a2.button("🗑️ 삭제", key="delete_btn"):
                        st.session_state[f"confirm_delete_{sel_idx}"] = True

                    if st.session_state.get(f"confirm_delete_{sel_idx}", False):
                        st.warning(f"{row.iloc[0]} 고객사를 정말 삭제하시겠습니까?")
                        d1, d2 = st.columns([1, 5])
                        if d1.button("확인 삭제", key="confirm_del"):
                            updated_df = df_cust.drop(index=sel_idx).reset_index(drop=True)
                            if save_to_gsheet(updated_df):
                                st.session_state[f"confirm_delete_{sel_idx}"] = False
                                st.success("삭제되었습니다.")
                                st.rerun()
                        if d2.button("취소", key="cancel_del"):
                            st.session_state[f"confirm_delete_{sel_idx}"] = False
                            st.rerun()

                for i in range(1, len(row.index)):
                    col_n = row.index[i]
                    raw = row.iloc[i]
                    val = str(raw).strip() if str(raw).strip() not in ("", "nan") else "-"
                    is_sp = any(k in str(col_n) for k in ["특이사항", "주의", "마킹", "포장"])
                    c = "#E63946" if is_sp else "#495057"
                    st.markdown(f"""
                    <div class="notranslate" translate="no" style="display: flex; border: 1px solid #DEE2E6; margin-bottom: -1px;">
                        <div style="background-color: #F8F9FA; width: 85px; min-width: 85px; padding: 10px 4px; font-weight: bold; color: {c}; border-right: 1px solid #DEE2E6; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 12px; line-height: 1.2; word-break: keep-all;">{col_n}</div>
                        <div class="notranslate" translate="no" style="flex: 1; padding: 10px; background-color: white; font-size: 13.5px; line-height: 1.4; color: #212529; font-weight: 500; word-break: break-all;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

        render_admin_login()

    with tab2:
        st.markdown("<div class=customer-title>⚖️ 품질 보증 표준 가이드</div>", unsafe_allow_html=True)
        df_qc = load_standard_data()

        if df_qc is not None:
            col_count = len(df_qc.columns)
            row_count = len(df_qc)
            all_spans = []
            for c in range(col_count):
                col_data = df_qc.iloc[:, c].fillna("").astype(str).tolist()
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

            table_html = "<div class=qc-table-wrapper><table class=qc-table><thead><tr>"
            for col in df_qc.columns:
                table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"
            for r in range(row_count):
                table_html += "<tr>"
                for c in range(col_count):
                    span_val = all_spans[c][r]
                    if span_val > 0:
                        cell_content = str(df_qc.iloc[r, c]).replace("nan", "").replace("(", "<br>(")
                        table_html += f"<td rowspan={span_val}>{cell_content}</td>"
                table_html += "</tr>"
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown("<div class=footer-note>※ 기타 수요가 요청사항은 별도 협의에 따른다.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
