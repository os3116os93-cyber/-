"""
app_coil.py — 코일 실두께 데이터 뷰어
구글 시트 통합뷰 탭에서 직접 읽어 표시
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

# 항상 표시할 전체 컬럼 순서 (중복 rename 후 이름 기준)
DISPLAY_COLS = [
    "재단일", "제강사", "강종", "재질", "두께", "폭", "중량",
    "S(L)_1", "C_1", "S(R)_1",
    "S(L)_2", "C_2", "S(R)_2",
    "S(L)_3", "C_3", "S(R)_3",
    "전산두께", "실두께평균", "차이", "최소실두께", "최대실두께", "범위차이",
]

TEXT_COLS = {"재단일", "제강사", "강종", "재질"}


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
    """통합뷰 시트에서 데이터 로드"""
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
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()


def run():
    st.title("📏 코일 실두께 데이터")

    # 새로고침
    if st.button("🔄 데이터 새로고침", use_container_width=False):
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

    # ── 날짜 필터 ─────────────────────────────────────────────────
    st.markdown("#### 📅 조회 기간 설정")
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("시작일", value=total_min,
                                  min_value=total_min, max_value=total_max,
                                  key="coil_date_from")
    with col2:
        date_to = st.date_input("종료일", value=total_max,
                                min_value=total_min, max_value=total_max,
                                key="coil_date_to")

    # 날짜 순서 오류 방지
    if date_from > date_to:
        st.warning("시작일이 종료일보다 늦습니다.")
        return

    # ── 필터 적용 ─────────────────────────────────────────────────
    mask = (
        (df["재단일"].dt.date >= date_from) &
        (df["재단일"].dt.date <= date_to)
    )
    filtered = df[mask].copy()
    filtered = filtered.sort_values("재단일", ascending=False)
    filtered["재단일"] = filtered["재단일"].dt.strftime("%Y-%m-%d")

    st.caption(f"총 **{len(filtered):,}건** | {date_from} ~ {date_to}  *(전체 데이터: {len(df):,}건)*")

    # ── 전체 컬럼 표시 ─────────────────────────────────────────────
    show_cols = [c for c in DISPLAY_COLS if c in filtered.columns]

    # 차이값 색상 강조
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

    st.dataframe(styled, use_container_width=True, height=600, hide_index=True)

    # 다운로드
    csv = display_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ CSV 다운로드", data=csv,
        file_name=f"코일실두께_{date_from}_{date_to}.csv",
        mime="text/csv"
    )
