"""
app_coil.py — 중간검사성적서 (코일 실두께 데이터 뷰어)
구글 시트 통합뷰에서 직접 읽어 표시
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

# 9칸 측정값 → 3칸 평균으로 통합
MEASURE_GROUPS = {
    "L 평균": ["S(L)_1", "S(L)_2", "S(L)_3"],
    "C 평균": ["C_1",    "C_2",    "C_3"],
    "R 평균": ["S(R)_1", "S(R)_2", "S(R)_3"],
}

# 최종 표시 컬럼 순서
DISPLAY_COLS = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "전산두께", "L 평균", "C 평균", "R 평균",
    "실두께평균", "최소실두께", "최대실두께", "차이",
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
    """워크시트 → DataFrame. 중복 헤더 자동 _1/_2/_3 처리."""
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
        # 측정값 평균 계산 (L/C/R)
        for avg_col, src_cols in MEASURE_GROUPS.items():
            exist = [c for c in src_cols if c in df.columns]
            df[avg_col] = df[exist].mean(axis=1).round(2) if exist else None
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()


def run():
    st.markdown("""
<style>
.coil-title { font-size:1.4rem; font-weight:800; color:#1a1a2e; margin-bottom:2px; }
.coil-sub   { font-size:13px; color:#6b7280; margin-bottom:14px; }
.filter-wrap {
    background:#fff; border:1.5px solid #e8eaed; border-radius:12px;
    padding:14px 18px 12px 18px; margin-bottom:14px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.filter-label { font-size:12px; font-weight:700; color:#374151; margin-bottom:8px; }
/* 좌우 여백 */
.block-container { padding-left:2rem !important; padding-right:2rem !important; }
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

    # 날짜: 시작일 / 종료일 한 줄 (YYYY/MM/DD 포맷으로 영문 월 방지)
    d1, d2 = st.columns(2)
    with d1:
        date_from = st.date_input(
            "시작일", value=total_min,
            min_value=date(2020, 1, 1), max_value=date(2099, 12, 31),
            format="YYYY/MM/DD", key="coil_from"
        )
    with d2:
        date_to = st.date_input(
            "종료일", value=total_max,
            min_value=date(2020, 1, 1), max_value=date(2099, 12, 31),
            format="YYYY/MM/DD", key="coil_to"
        )

    # 제강사 / 강종 / 재질: 타이핑 → 즉시 필터 (selectbox 없이 한 단계로)
    s1, s2, s3 = st.columns(3)

    maker_vals = sorted(df["제강사"].dropna().unique().tolist()) if "제강사" in df.columns else []
    grade_vals = sorted(df["강종"].dropna().unique().tolist())   if "강종"   in df.columns else []
    mat_vals   = sorted(df["재질"].dropna().unique().tolist())   if "재질"   in df.columns else []

    with s1:
        maker_q = st.text_input("제강사", placeholder=f"예: {maker_vals[0] if maker_vals else 'ANF'}", key="coil_maker")
    with s2:
        grade_q = st.text_input("강종",   placeholder=f"예: {grade_vals[0] if grade_vals else 'GI'}",  key="coil_grade")
    with s3:
        mat_q   = st.text_input("재질",   placeholder=f"예: {mat_vals[0]   if mat_vals   else 'SGC'}", key="coil_mat")

    # 입력 중 후보 미리보기 (선택 단계 없이 자동 필터)
    if maker_q:
        hits = [v for v in maker_vals if maker_q.lower() in v.lower()]
        if hits:
            st.caption("제강사 후보: " + " / ".join(hits[:8]))
    if grade_q:
        hits = [v for v in grade_vals if grade_q.lower() in v.lower()]
        if hits:
            st.caption("강종 후보: " + " / ".join(hits[:8]))
    if mat_q:
        hits = [v for v in mat_vals if mat_q.lower() in v.lower()]
        if hits:
            st.caption("재질 후보: " + " / ".join(hits[:8]))

    st.markdown('</div>', unsafe_allow_html=True)

    if date_from > date_to:
        st.warning("시작일이 종료일보다 늦습니다.")
        return

    # ── 필터 적용 ─────────────────────────────────────────────────
    mask = (
        (df["재단일"].dt.date >= date_from) &
        (df["재단일"].dt.date <= date_to)
    )
    # 제강사: 부분일치
    if maker_q:
        maker_hits = [v for v in maker_vals if maker_q.lower() in v.lower()]
        if maker_hits:
            mask &= df["제강사"].isin(maker_hits)
        else:
            mask &= df["제강사"].str.contains(maker_q, case=False, na=False)
    # 강종: 부분일치
    if grade_q:
        grade_hits = [v for v in grade_vals if grade_q.lower() in v.lower()]
        if grade_hits:
            mask &= df["강종"].isin(grade_hits)
        else:
            mask &= df["강종"].str.contains(grade_q, case=False, na=False)
    # 재질: 부분일치
    if mat_q:
        mat_hits = [v for v in mat_vals if mat_q.lower() in v.lower()]
        if mat_hits:
            mask &= df["재질"].isin(mat_hits)
        else:
            mask &= df["재질"].str.contains(mat_q, case=False, na=False)

    filtered = df[mask].copy()
    filtered = filtered.sort_values("재단일", ascending=False)
    filtered["재단일"] = filtered["재단일"].dt.strftime("%Y-%m-%d")

    st.caption(f"총 **{len(filtered):,}건** | {date_from} ~ {date_to}  *(전체: {len(df):,}건)*")

    # ── 표시 컬럼 ────────────────────────────────────────────────
    show_cols  = [c for c in DISPLAY_COLS if c in filtered.columns]
    display_df = filtered[show_cols].copy()

    # 차이값 색상
    def color_diff(val):
        try:
            v = float(val)
            if v < -0.05:  return "color:#1565C0;font-weight:600"
            elif v > 0.05: return "color:#C62828;font-weight:600"
        except:
            pass
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

    st.dataframe(
        styled,
        use_container_width=True,
        height=560,
        hide_index=True,
        column_config={c: st.column_config.NumberColumn(c, width="small")
                       for c in show_cols if c not in TEXT_COLS and c != "재단일"}
    )

    csv = display_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ CSV 다운로드", data=csv,
        file_name=f"중간검사성적서_{date_from}_{date_to}.csv",
        mime="text/csv"
    )
