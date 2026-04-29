"""
app_coil.py — 코일 실두께 데이터 뷰어
구글 시트 연동: A팀시트 + B팀시트 → 통합시트 자동 병합
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import date

# ── 구글 시트 설정 ────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = st.secrets.get("SHEET_ID", "")

SHEET_A      = "A팀_입력"
SHEET_B      = "B팀_입력"
SHEET_MERGED = "통합뷰"

PASSWORD_A = "aaaa"   # ← 실제 비밀번호로 변경
PASSWORD_B = "bbbb"   # ← 실제 비밀번호로 변경

COLUMNS_NEW = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "S(L)_1", "C_1", "S(R)_1",
    "S(L)_2", "C_2", "S(R)_2",
    "S(L)_3", "C_3", "S(R)_3",
    "전산두께", "실두께평균", "차이", "최소실두께", "최대실두께", "범위차이"
]

DISPLAY_COLS_DEFAULT = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "전산두께", "실두께평균", "차이", "최소실두께", "최대실두께", "범위차이"
]

DISPLAY_COLS_MOBILE = [
    "재단일", "제강사", "재질", "두께", "실두께평균", "차이"
]

TEXT_COLS = {"재단일", "제강사", "강종", "재질", "팀구분"}


# ── 구글 시트 연결 ────────────────────────────────────────────────────
@st.cache_resource(ttl=300)
def get_gsheet_client():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None


def _ws_to_df(ws):
    """워크시트 → DataFrame. 중복 헤더는 _1/_2/_3 suffix로 자동 처리."""
    all_values = ws.get_all_values()
    if not all_values or len(all_values) < 2:
        return pd.DataFrame()

    raw_headers = [h.strip() for h in all_values[0]]
    raw_count = Counter(raw_headers)
    seen = {}
    headers = []
    for h in raw_headers:
        if raw_count[h] > 1:
            seen[h] = seen.get(h, 0) + 1
            headers.append(f"{h}_{seen[h]}")
        else:
            headers.append(h)

    df = pd.DataFrame(all_values[1:], columns=headers)
    df = df[df.iloc[:, 0].str.strip() != ""].copy()
    return df


def load_merged_data():
    """통합뷰 시트에서 데이터 로드 (중복 헤더 대응)"""
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_MERGED)
        df = _ws_to_df(ws)
        if df.empty:
            return df
        df["재단일"] = pd.to_datetime(df["재단일"], errors="coerce")
        for c in df.columns:
            if c not in TEXT_COLS:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()


def append_row(sheet_name, row_data):
    client = get_gsheet_client()
    if not client:
        return False
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(sheet_name)
        headers = ws.row_values(1)
        if not headers:
            ws.append_row(COLUMNS_NEW + ["팀구분"])
            headers = COLUMNS_NEW + ["팀구분"]
        row = [str(row_data.get(h, "")) for h in headers]
        ws.append_row(row)
        return True
    except Exception as e:
        st.error(f"데이터 저장 실패: {e}")
        return False


def merge_sheets():
    client = get_gsheet_client()
    if not client:
        return False
    try:
        sh = client.open_by_key(SPREADSHEET_ID)

        def read_team(name):
            df = _ws_to_df(sh.worksheet(name))
            if df.empty:
                return df
            df["재단일"] = pd.to_datetime(df["재단일"], errors="coerce")
            return df

        df_a = read_team(SHEET_A)
        df_b = read_team(SHEET_B)
        if not df_a.empty:
            df_a["팀구분"] = "A팀"
        if not df_b.empty:
            df_b["팀구분"] = "B팀"

        all_dates = set()
        if not df_a.empty:
            all_dates.update(df_a["재단일"].dropna().unique())
        if not df_b.empty:
            all_dates.update(df_b["재단일"].dropna().unique())

        frames = []
        for d in sorted(all_dates, reverse=True):
            if not df_a.empty:
                frames.append(df_a[df_a["재단일"] == d])
            if not df_b.empty:
                frames.append(df_b[df_b["재단일"] == d])

        if not frames:
            st.warning("병합할 데이터가 없습니다.")
            return False

        merged = pd.concat(frames, ignore_index=True)
        merged["재단일"] = merged["재단일"].dt.strftime("%Y-%m-%d")
        ws_merged = sh.worksheet(SHEET_MERGED)
        ws_merged.clear()
        ws_merged.update([merged.columns.tolist()] + merged.fillna("").values.tolist())
        return True
    except Exception as e:
        st.error(f"병합 실패: {e}")
        return False


# ── UI ───────────────────────────────────────────────────────────────
def run():
    st.title("📏 코일 실두께 데이터")
    tab_view, tab_input = st.tabs(["📊 데이터 조회", "✏️ 데이터 입력"])
    with tab_view:
        _show_viewer()
    with tab_input:
        _show_input_form()


def _show_viewer():
    col_load, col_merge = st.columns([3, 1])
    with col_load:
        if st.button("🔄 데이터 새로고침", use_container_width=True):
            st.cache_resource.clear()
    with col_merge:
        if st.button("🔗 시트 병합", use_container_width=True,
                     help="A팀·B팀 데이터를 통합시트에 합칩니다"):
            with st.spinner("병합 중..."):
                if merge_sheets():
                    st.success("병합 완료!")
                    st.cache_resource.clear()

    with st.spinner("데이터 불러오는 중..."):
        df = load_merged_data()

    if df.empty:
        st.info("데이터가 없습니다.")
        return

    with st.expander("🔍 필터", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            min_d = df["재단일"].min().date()
            max_d = df["재단일"].max().date()
            date_from = st.date_input("시작일", value=min_d, key="cf_from")
            date_to   = st.date_input("종료일", value=max_d, key="cf_to")
        with f2:
            makers = ["전체"] + sorted(df["제강사"].dropna().unique().tolist()) if "제강사" in df.columns else ["전체"]
            maker = st.selectbox("제강사", makers)
        with f3:
            grades = ["전체"] + sorted(df["강종"].dropna().unique().tolist()) if "강종" in df.columns else ["전체"]
            grade = st.selectbox("강종", grades)
        with f4:
            teams = ["전체"] + sorted(df["팀구분"].dropna().unique().tolist()) if "팀구분" in df.columns else ["전체"]
            team = st.selectbox("팀구분", teams)

    mask = (
        (df["재단일"].dt.date >= date_from) &
        (df["재단일"].dt.date <= date_to)
    )
    if maker != "전체":
        mask &= (df["제강사"] == maker)
    if grade != "전체":
        mask &= (df["강종"] == grade)
    if team != "전체" and "팀구분" in df.columns:
        mask &= (df["팀구분"] == team)

    filtered = df[mask].copy()
    filtered = filtered.sort_values("재단일", ascending=False)
    filtered["재단일"] = filtered["재단일"].dt.strftime("%Y-%m-%d")

    st.caption(f"총 {len(filtered):,}건 | {date_from} ~ {date_to}")

    is_mobile = st.checkbox("📱 모바일 보기 (컬럼 축소)", value=False)
    if is_mobile:
        show_cols = [c for c in DISPLAY_COLS_MOBILE if c in filtered.columns]
    else:
        show_cols = [c for c in DISPLAY_COLS_DEFAULT if c in filtered.columns]
        if "팀구분" in filtered.columns:
            show_cols = ["팀구분"] + show_cols

    def color_diff(val):
        try:
            v = float(val)
            if v < -0.05:
                return "color: #1565C0; font-weight:600"
            elif v > 0.05:
                return "color: #C62828; font-weight:600"
        except:
            pass
        return ""

    display_df = filtered[[c for c in show_cols if c in filtered.columns]]
    styled = display_df.style
    if "차이" in display_df.columns:
        styled = styled.applymap(color_diff, subset=["차이"])

    st.dataframe(styled, use_container_width=True, height=600, hide_index=True)

    csv = display_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ CSV 다운로드", data=csv,
                       file_name=f"코일실두께_{date_from}_{date_to}.csv",
                       mime="text/csv")


def _show_input_form():
    st.subheader("데이터 입력")
    team_choice = st.radio("입력 팀 선택", ["A팀", "B팀"], horizontal=True)

    if "coil_auth_team" not in st.session_state:
        st.session_state.coil_auth_team = None

    pw = st.text_input("비밀번호", type="password", key="coil_pw_input")
    if st.button("인증", key="coil_auth_btn"):
        expected = PASSWORD_A if team_choice == "A팀" else PASSWORD_B
        if pw == expected:
            st.session_state.coil_auth_team = team_choice
            st.success(f"{team_choice} 인증 완료!")
        else:
            st.error("비밀번호가 틀렸습니다.")
            st.session_state.coil_auth_team = None

    if st.session_state.coil_auth_team != team_choice:
        st.info("인증 후 입력 폼이 표시됩니다.")
        return

    st.markdown(f"**{team_choice} 데이터 입력**")

    with st.form("coil_input_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_date     = st.date_input("재단일", value=date.today())
            f_maker    = st.text_input("제강사")
        with c2:
            f_type     = st.text_input("강종")
            f_grade    = st.text_input("재질")
        with c3:
            f_thick    = st.number_input("두께",    min_value=0.0, step=0.001, format="%.3f")
            f_width    = st.number_input("폭",      min_value=0.0, step=1.0,   format="%.1f")
        with c4:
            f_weight   = st.number_input("중량",    min_value=0.0, step=1.0,   format="%.0f")
            f_pc_thick = st.number_input("전산두께", min_value=0.0, step=0.001, format="%.3f")

        st.markdown("**측정값 입력** (S(L) / C / S(R) × 3회)")
        m1, m2, m3 = st.columns(3)
        measures = {}
        for i, (col, label) in enumerate(zip([m1, m2, m3], ["1차", "2차", "3차"])):
            with col:
                st.caption(label)
                measures[f"S(L)_{i+1}"] = st.number_input(f"S(L) {label}", step=0.001, format="%.3f", key=f"sl{i}")
                measures[f"C_{i+1}"]    = st.number_input(f"C {label}",    step=0.001, format="%.3f", key=f"c{i}")
                measures[f"S(R)_{i+1}"] = st.number_input(f"S(R) {label}", step=0.001, format="%.3f", key=f"sr{i}")

        submitted = st.form_submit_button("💾 저장", use_container_width=True, type="primary")

    if submitted:
        all_vals = list(measures.values())
        if any(v != 0 for v in all_vals):
            avg        = sum(all_vals) / len(all_vals)
            min_v      = min(all_vals)
            max_v      = max(all_vals)
            diff       = avg - f_pc_thick
            range_diff = max_v - min_v
            row = {
                "재단일":     str(f_date),
                "제강사":     f_maker,
                "강종":       f_type,
                "재질":       f_grade,
                "두께":       f_thick,
                "폭":         f_width,
                "중량":       f_weight,
                "전산두께":   f_pc_thick,
                "실두께평균": round(avg, 6),
                "차이":       round(diff, 6),
                "최소실두께": round(min_v, 3),
                "최대실두께": round(max_v, 3),
                "범위차이":   round(range_diff, 3),
                "팀구분":     st.session_state.coil_auth_team,
                **measures,
            }
            sheet_name = SHEET_A if st.session_state.coil_auth_team == "A팀" else SHEET_B
            with st.spinner("저장 중..."):
                if append_row(sheet_name, row):
                    st.success("저장 완료! '시트 병합' 버튼을 눌러 통합뷰를 업데이트하세요.")
        else:
            st.warning("측정값을 입력해주세요.")
            
