"""
app_coil.py — 중간검사성적서 (코일 실두께 데이터 뷰어)
구글 시트 통합뷰에서 직접 읽어 표시
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import date, timedelta

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = st.secrets.get("SHEET_ID", "")
SHEET_MERGED   = "통합뷰"

TEXT_COLS = {"재단일", "제강사", "강종", "재질"}

# S(L)/C/S(R) 3회 측정 컬럼 — 평균 계산 후 표시할 컬럼 정의
MEASURE_GROUPS = {
    "S(L)평균": ["S(L)_1", "S(L)_2", "S(L)_3"],
    "C평균":    ["C_1",    "C_2",    "C_3"],
    "S(R)평균": ["S(R)_1", "S(R)_2", "S(R)_3"],
}

# 최종 표시 컬럼 순서
DISPLAY_COLS = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "전산두께",
    "S(L)평균", "C평균", "S(R)평균",
    "실두께평균", "차이", "최소실두께", "최대실두께", "범위차이",
]


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
    all_values = ws.get_all_values()
    if not all_values or len(all_values) < 2:
        return pd.DataFrame()
    raw = [h.strip() for h in all_values[0]]
    cnt = Counter(raw)
    seen = {}
    headers = []
    for h in raw:
        if cnt[h] > 1:
            seen[h] = seen.get(h, 0) + 1
            headers.append(f"{h}_{seen[h]}")
        else:
            headers.append(h)
    df = pd.DataFrame(all_values[1:], columns=headers)
    df = df[df.iloc[:, 0].str.strip() != ""].copy()
    return df


@st.cache_data(ttl=300)
def load_data():
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet(SHEET_MERGED)
        df = _ws_to_df(ws)
        if df.empty:
            return df
        # 날짜 파싱
        df["재단일"] = pd.to_datetime(df["재단일"], errors="coerce")
        df = df[df["재단일"].notna()].copy()
        # 숫자 변환
        for c in df.columns:
            if c not in TEXT_COLS and c != "재단일":
                df[c] = pd.to_numeric(df[c], errors="coerce")
        # 측정값 평균 컬럼 계산
        for avg_col, src_cols in MEASURE_GROUPS.items():
            exist = [c for c in src_cols if c in df.columns]
            if exist:
                df[avg_col] = df[exist].mean(axis=1).round(2)
            else:
                df[avg_col] = None
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()


def run():
    st.markdown("""
<style>
.coil-header {
    font-size:1.5rem; font-weight:800; color:#1a1a2e;
    margin-bottom:4px;
}
.coil-sub {
    font-size:13px; color:#6b7280; margin-bottom:20px;
}
.filter-box {
    background:#ffffff; border:1.5px solid #e8eaed;
    border-radius:12px; padding:18px 20px 12px 20px;
    margin-bottom:18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

    st.markdown('<div class="coil-header">📐 중간검사성적서</div>', unsafe_allow_html=True)
    st.markdown('<div class="coil-sub">코일 실두께 측정 데이터 조회</div>', unsafe_allow_html=True)

    if st.button("🔄 데이터 새로고침"):
        load_data.clear()
        st.cache_resource.clear()
        st.rerun()

    with st.spinner("데이터 불러오는 중..."):
        df = load_data()

    if df.empty:
        st.info("통합뷰 시트에 데이터가 없습니다.")
        return

    total_min = df["재단일"].min().date()
    total_max = df["재단일"].max().date()

    # ── 필터 박스 ─────────────────────────────────────────────────
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.markdown("**🔍 조회 조건**")

    fc1, fc2 = st.columns(2)
    with fc1:
        date_from = st.date_input(
            "시작일",
            value=total_min,
            min_value=total_min,
            max_value=total_max,
            key="coil_from"
        )
    with fc2:
        date_to = st.date_input(
            "종료일",
            value=total_max,
            min_value=total_min,
            max_value=total_max,
            key="coil_to"
        )

    fa1, fa2, fa3 = st.columns(3)
    with fa1:
        makers = ["전체"] + sorted(df["제강사"].dropna().unique().tolist()) if "제강사" in df.columns else ["전체"]
        maker = st.selectbox("제강사", makers, key="coil_maker")
    with fa2:
        grades = ["전체"] + sorted(df["강종"].dropna().unique().tolist()) if "강종" in df.columns else ["전체"]
        grade = st.selectbox("강종", grades, key="coil_grade")
    with fa3:
        mats = ["전체"] + sorted(df["재질"].dropna().unique().tolist()) if "재질" in df.columns else ["전체"]
        mat = st.selectbox("재질", mats, key="coil_mat")

    st.markdown('</div>', unsafe_allow_html=True)

    if date_from > date_to:
        st.warning("시작일이 종료일보다 늦습니다.")
        return

    # ── 필터 적용 ─────────────────────────────────────────────────
    mask = (
        (df["재단일"].dt.date >= date_from) &
        (df["재단일"].dt.date <= date_to)
    )
    if maker != "전체":
        mask &= (df["제강사"] == maker)
    if grade != "전체":
        mask &= (df["강종"] == grade)
    if mat != "전체":
        mask &= (df["재질"] == mat)

    filtered = df[mask].copy()
    filtered = filtered.sort_values("재단일", ascending=False)
    filtered["재단일"] = filtered["재단일"].dt.strftime("%Y-%m-%d")

    st.caption(f"총 **{len(filtered):,}건** | {date_from} ~ {date_to}  *(전체: {len(df):,}건)*")

    # ── 표시 컬럼 선택 ────────────────────────────────────────────
    show_cols = [c for c in DISPLAY_COLS if c in filtered.columns]

    # ── 차이값 색상 ───────────────────────────────────────────────
    def color_diff(val):
        try:
            v = float(val)
            if v < -0.05:
                return "color:#1565C0;font-weight:600"
            elif v > 0.05:
                return "color:#C62828;font-weight:600"
        except:
            pass
        return ""

    display_df = filtered[[c for c in show_cols if c in filtered.columns]]
    styled = display_df.style
    if "차이" in display_df.columns:
        styled = styled.applymap(color_diff, subset=["차이"])

    # 숫자 소수점 2자리 포맷
    num_cols = [c for c in display_df.columns if c not in TEXT_COLS and c != "재단일"]
    fmt = {c: "{:.2f}" for c in num_cols if c in display_df.columns}
    int_cols = [c for c in ["두께", "폭", "중량"] if c in display_df.columns]
    for c in int_cols:
        fmt[c] = "{:.0f}"
    styled = styled.format(fmt, na_rep="-")

    st.dataframe(styled, use_container_width=True, height=580, hide_index=True)

    csv = display_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ CSV 다운로드", data=csv,
        file_name=f"중간검사성적서_{date_from}_{date_to}.csv",
        mime="text/csv"
    )
