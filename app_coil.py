"""
app_coil.py — 중간검사성적서 (코일 실두께 데이터 뷰어)
"""
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import date

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_ID = st.secrets.get("SHEET_ID", "")
SHEET_MERGED   = "통합뷰"
TEXT_COLS      = {"재단일", "제강사", "강종", "재질"}

MEASURE_GROUPS = {
    "S(L)평균": ["S(L)_1", "S(L)_2", "S(L)_3"],
    "C평균":    ["C_1",    "C_2",    "C_3"],
    "S(R)평균": ["S(R)_1", "S(R)_2", "S(R)_3"],
}

DISPLAY_COLS = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "전산두께",
    "S(L)평균", "C평균", "S(R)평균",
    "실두께평균", "최소실두께", "최대실두께", "범위차이", "차이",
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
        df["재단일"] = pd.to_datetime(df["재단일"], errors="coerce")
        df = df[df["재단일"].notna()].copy()
        for c in df.columns:
            if c not in TEXT_COLS and c != "재단일":
                df[c] = pd.to_numeric(df[c], errors="coerce")
        # 측정값 평균 계산
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
/* 날짜 피커 언어 강제 (Streamlit은 브라우저 locale 따름 → JS로 보완) */
input[type="text"][aria-label*="일"] { ime-mode: active; }

.coil-title {
    font-size:1.45rem; font-weight:800; color:#1a1a2e; margin-bottom:2px;
}
.coil-sub { font-size:13px; color:#6b7280; margin-bottom:16px; }

.filter-wrap {
    background:#fff; border:1.5px solid #e8eaed; border-radius:12px;
    padding:16px 18px 10px 18px; margin-bottom:16px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.filter-label {
    font-size:12px; font-weight:700; color:#374151;
    margin-bottom:10px; letter-spacing:0.03em;
}

/* 검색 입력 드롭다운 느낌 */
[data-testid="stTextInput"] input {
    border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

    st.markdown('<div class="coil-title">📐 중간검사성적서</div>', unsafe_allow_html=True)
    st.markdown('<div class="coil-sub">코일 실두께 측정 데이터 조회</div>', unsafe_allow_html=True)

    if st.button("🔄 데이터 새로고침", key="coil_refresh"):
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
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="filter-label">🔍 조회 조건</div>', unsafe_allow_html=True)

    # 날짜 — 한 줄에 시작일 / 종료일 (모바일/PC 공통)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        date_from = st.date_input(
            "시작일",
            value=total_min,
            min_value=date(2020, 1, 1),   # 연도 제한 없음
            max_value=date(2099, 12, 31),
            key="coil_from",
            format="YYYY/MM/DD",           # 한국식 포맷 (영문월 방지)
        )
    with d_col2:
        date_to = st.date_input(
            "종료일",
            value=total_max,
            min_value=date(2020, 1, 1),
            max_value=date(2099, 12, 31),
            key="coil_to",
            format="YYYY/MM/DD",
        )

    # 텍스트 검색 필터 — 제강사 / 강종 / 재질 (타이핑 → 자동 후보 표시)
    s_col1, s_col2, s_col3 = st.columns(3)

    def _search_input(label, col_name, key, all_vals):
        """타이핑하면 후보를 expander로 보여주는 검색 위젯"""
        query = col.text_input(label, placeholder=f"예: {all_vals[0] if all_vals else ''}", key=key)
        if query:
            hits = [v for v in all_vals if query.lower() in v.lower()]
            if hits and hits != all_vals:
                with col.expander(f"후보 {len(hits)}건", expanded=True):
                    chosen = st.radio("선택", hits, key=key+"_pick", label_visibility="collapsed")
                    if chosen:
                        return chosen
            return query
        return ""

    # 제강사
    with s_col1:
        maker_vals = sorted(df["제강사"].dropna().unique().tolist()) if "제강사" in df.columns else []
        maker_q = st.text_input("제강사 검색", placeholder=f"예: {maker_vals[0] if maker_vals else 'PSC'}", key="coil_maker_q")
        if maker_q:
            maker_hits = [v for v in maker_vals if maker_q.lower() in v.lower()]
            if maker_hits:
                maker_sel = st.selectbox("→ 선택", ["(전체)"] + maker_hits, key="coil_maker_sel")
            else:
                maker_sel = "(전체)"
                st.caption("일치하는 제강사 없음")
        else:
            maker_sel = "(전체)"

    # 강종
    with s_col2:
        grade_vals = sorted(df["강종"].dropna().unique().tolist()) if "강종" in df.columns else []
        grade_q = st.text_input("강종 검색", placeholder=f"예: {grade_vals[0] if grade_vals else 'GI'}", key="coil_grade_q")
        if grade_q:
            grade_hits = [v for v in grade_vals if grade_q.lower() in v.lower()]
            if grade_hits:
                grade_sel = st.selectbox("→ 선택", ["(전체)"] + grade_hits, key="coil_grade_sel")
            else:
                grade_sel = "(전체)"
                st.caption("일치하는 강종 없음")
        else:
            grade_sel = "(전체)"

    # 재질
    with s_col3:
        mat_vals = sorted(df["재질"].dropna().unique().tolist()) if "재질" in df.columns else []
        mat_q = st.text_input("재질 검색", placeholder=f"예: {mat_vals[0] if mat_vals else 'SGC'}", key="coil_mat_q")
        if mat_q:
            mat_hits = [v for v in mat_vals if mat_q.lower() in v.lower()]
            if mat_hits:
                mat_sel = st.selectbox("→ 선택", ["(전체)"] + mat_hits, key="coil_mat_sel")
            else:
                mat_sel = "(전체)"
                st.caption("일치하는 재질 없음")
        else:
            mat_sel = "(전체)"

    st.markdown('</div>', unsafe_allow_html=True)

    if date_from > date_to:
        st.warning("시작일이 종료일보다 늦습니다.")
        return

    # ── 필터 적용 ─────────────────────────────────────────────────
    mask = (
        (df["재단일"].dt.date >= date_from) &
        (df["재단일"].dt.date <= date_to)
    )
    if maker_sel not in ("(전체)", ""):
        mask &= (df["제강사"] == maker_sel)
    if grade_sel not in ("(전체)", ""):
        mask &= (df["강종"] == grade_sel)
    if mat_sel not in ("(전체)", ""):
        mask &= (df["재질"] == mat_sel)

    filtered = df[mask].copy()
    filtered = filtered.sort_values("재단일", ascending=False)
    filtered["재단일"] = filtered["재단일"].dt.strftime("%Y-%m-%d")

    st.caption(f"총 **{len(filtered):,}건** | {date_from} ~ {date_to}  *(전체: {len(df):,}건)*")

    show_cols = [c for c in DISPLAY_COLS if c in filtered.columns]
    display_df = filtered[[c for c in show_cols if c in filtered.columns]]

    # 차이값 색상
    def color_diff(val):
        try:
            v = float(val)
            if v < -0.05:   return "color:#1565C0;font-weight:600"
            elif v > 0.05:  return "color:#C62828;font-weight:600"
        except: pass
        return ""

    styled = display_df.style
    if "차이" in display_df.columns:
        styled = styled.applymap(color_diff, subset=["차이"])

    # 소수점 포맷
    fmt = {}
    for c in display_df.columns:
        if c in ("두께", "폭", "중량"):
            fmt[c] = "{:.0f}"
        elif c not in TEXT_COLS and c != "재단일":
            fmt[c] = "{:.2f}"
    styled = styled.format(fmt, na_rep="-")

    st.dataframe(styled, use_container_width=True, height=560, hide_index=True)

    csv = display_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ CSV 다운로드", data=csv,
        file_name=f"중간검사성적서_{date_from}_{date_to}.csv",
        mime="text/csv"
    )
