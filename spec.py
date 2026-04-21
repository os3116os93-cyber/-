import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

BASE_DIR = os.getcwd()

# -----------------------------
# 파일 로드 (완전 방어형)
# -----------------------------
def load_data(file_name):
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        st.error(f"파일 없음: {file_name}")
        st.stop()

    try:
        df = pd.read_excel(file_path, header=None)  # ⭐ 핵심 (헤더 강제 제거)
    except Exception as e:
        st.error(f"엑셀 로드 실패: {e}")
        st.stop()

    # NaN 제거
    df = df.fillna("")

    return df


# -----------------------------
# 병합 계산 (완전 안전)
# -----------------------------
def calc_spans(df):
    spans_all = []

    for col in range(df.shape[1]):
        col_data = df.iloc[:, col].astype(str).tolist()

        spans = []
        i = 0

        while i < len(col_data):
            curr = col_data[i].strip()
            count = 1

            if curr != "":
                while i + count < len(col_data):
                    if col_data[i + count].strip() != "":
                        break
                    count += 1

            spans.append(count)
            spans.extend([0] * (count - 1))
            i += count

        spans_all.append(spans)

    return spans_all


# -----------------------------
# 테이블 출력 (절대 안터짐)
# -----------------------------
def draw_table(df):
    spans = calc_spans(df)

    html = "<table style='border-collapse:collapse; width:100%; text-align:center;'>"

    for r in range(len(df)):
        html += "<tr>"

        for c in range(df.shape[1]):
            span = spans[c][r]

            if span == 0:
                continue

            val = str(df.iloc[r, c]).strip()

            html += f"<td rowspan='{span}' style='border:1px solid #ddd; padding:6px;'>{val}</td>"

        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)


# -----------------------------
# UI
# -----------------------------
st.title("품질 통합 관리 시스템")

# 디버그 (필요하면 켜)
# st.write(os.listdir())

tab1, tab2 = st.tabs(["고객사양서", "품질보증기준"])

with tab1:
    st.subheader("고객사양서")
    df1 = load_data("customer.xlsx")
    draw_table(df1)

with tab2:
    st.subheader("품질보증기준")
    df2 = load_data("standard.xlsx")
    draw_table(df2)

