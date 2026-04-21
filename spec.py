import streamlit as st
import pandas as pd
import os

# ---------------------------------
# 기본 설정
# ---------------------------------
st.set_page_config(layout="wide")

BASE_DIR = os.getcwd()

# ---------------------------------
# 파일 로드 (안정화)
# ---------------------------------
def load_data(file_name, skip=0):
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        st.error(f"❌ 파일 없음: {file_name}")
        st.stop()

    try:
        df = pd.read_excel(file_path, skiprows=skip)
    except Exception as e:
        st.error(f"엑셀 로드 실패: {e}")
        st.stop()

    # 컬럼명 정리 (KeyError 방지)
    df.columns = [str(c).strip() for c in df.columns]

    return df


# ---------------------------------
# 병합(span) 계산 (NaN 완벽 대응)
# ---------------------------------
def calc_row_spans(df):
    row_count = len(df)
    col_count = len(df.columns)

    all_spans = []

    for c in range(col_count):
        col_data = df.iloc[:, c].tolist()

        spans = []
        i = 0

        while i < row_count:
            curr = "" if pd.isna(col_data[i]) else str(col_data[i]).strip()
            count = 1

            if curr != "":
                while i + count < row_count:
                    next_val = col_data[i + count]
                    next_val = "" if pd.isna(next_val) else str(next_val).strip()

                    if next_val != "":
                        break
                    count += 1

            spans.append(count)

            for _ in range(count - 1):
                spans.append(0)

            i += count

        all_spans.append(spans)

    return all_spans


# ---------------------------------
# 테이블 출력 (KeyError 완전 차단)
# ---------------------------------
def draw_table(df):
    spans = calc_row_spans(df)

    html = """
    <table style='border-collapse: collapse; width:100%; text-align:center;'>
    """

    # 헤더
    html += "<tr>"
    for col in df.columns:
        html += f"<th style='border:1px solid #ddd; padding:6px; background:#f2f2f2;'>{col}</th>"
    html += "</tr>"

    # 본문
    for r in range(len(df)):
        html += "<tr>"

        row = df.iloc[r]

        for c in range(len(df.columns)):
            span = spans[c][r]

            if span == 0:
                continue

            val = "" if pd.isna(row.iloc[c]) else str(row.iloc[c])

            html += f"<td rowspan='{span}' style='border:1px solid #ddd; padding:6px;'>{val}</td>"

        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------
# UI
# ---------------------------------
st.title("📊 품질 통합 관리 시스템")

# 디버깅 (문제 있으면 켜라)
# st.write("현재 경로:", BASE_DIR)
# st.write("파일 목록:", os.listdir())

tab1, tab2 = st.tabs(["고객사양서", "품질보증기준"])


# ---------------------------------
# 고객사양서 탭
# ---------------------------------
with tab1:
    st.subheader("고객사양서")

    df_customer = load_data("customer.xlsx")
    draw_table(df_customer)


# ---------------------------------
# 품질보증기준 탭
# ---------------------------------
with tab2:
    st.subheader("품질보증기준")

    df_standard = load_data("standard.xlsx")
    draw_table(df_standard)

