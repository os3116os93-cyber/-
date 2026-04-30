import streamlit as st
import os
import base64

st.set_page_config(
    page_title="한진철관 품질기술팀",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

def get_image_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = get_image_base64(os.path.join(BASE_DIR, "hanjin_logo.png"))
bg_b64   = get_image_base64(os.path.join(BASE_DIR, "banner_bg.png"))

logo_tag = (f'<img src="data:image/png;base64,{logo_b64}" style="height:52px;width:auto;">'
            if logo_b64 else '<span style="font-size:22px;font-weight:900;color:#FF8C00;">한진철관</span>')

bg_style = (f'background-image:url("data:image/png;base64,{bg_b64}");background-size:cover;background-position:center;'
            if bg_b64 else 'background:#111;')

if "page" not in st.session_state:
    st.session_state.page = "home"

st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] > .main {{ background:#f5f6fa; }}
  [data-testid="stSidebar"] {{ display:none; }}
  .block-container {{ padding-top:0 !important; max-width:100% !important; }}

  /* ── 배너 ── */
  .hj-banner {{
    {bg_style}
    width:100%; min-height:260px;
    display:flex; flex-direction:column;
    justify-content:space-between;
    padding:22px 32px 28px 32px;
    box-sizing:border-box;
    position:relative;
  }}
  .hj-banner::before {{
    content:""; position:absolute; inset:0;
    background:rgba(0,0,0,0.52);
  }}
  .hj-banner-top {{
    position:relative; z-index:1;
    display:flex; justify-content:space-between; align-items:flex-start;
  }}
  .hj-team-label {{
    font-size:13px; font-weight:600; color:rgba(255,255,255,0.75);
    letter-spacing:0.05em;
  }}
  .hj-banner-bottom {{
    position:relative; z-index:1;
  }}
  .hj-banner-title {{
    font-size:clamp(1.3rem,3vw,2rem); font-weight:800;
    color:#ffffff; line-height:1.2; margin-bottom:4px;
  }}
  .hj-banner-sub {{
    font-size:13px; color:rgba(255,255,255,0.65);
  }}

  /* ── 카드 영역 ── */
  .hj-cards {{
    display:grid; grid-template-columns:1fr 1fr;
    gap:20px; padding:28px 28px 32px 28px;
    max-width:960px; margin:0 auto;
    box-sizing:border-box;
  }}
  .hj-card {{
    background:#ffffff; border-radius:14px;
    border:1.5px solid #e8eaf0;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);
    padding:28px 24px 20px 24px;
    display:flex; flex-direction:column;
    align-items:center; text-align:center;
    transition:transform .18s, box-shadow .18s;
    cursor:pointer;
  }}
  .hj-card:hover {{
    transform:translateY(-4px);
    box-shadow:0 8px 28px rgba(0,0,0,0.13);
    border-color:#FF8C00;
  }}
  .hj-card-icon {{ font-size:2.6rem; margin-bottom:14px; }}
  .hj-card-title {{
    font-size:1.1rem; font-weight:800;
    color:#1a1a2e; margin-bottom:8px;
  }}
  .hj-card-desc {{
    font-size:0.82rem; color:#6b7280;
    line-height:1.55; margin-bottom:0;
  }}

  /* 뒤로가기 버튼 */
  .stButton > button {{
    border-radius:8px; font-weight:600;
  }}

  @media(max-width:600px) {{
    .hj-cards {{ grid-template-columns:1fr; padding:18px; }}
    .hj-banner {{ min-height:200px; padding:18px; }}
  }}
</style>
""", unsafe_allow_html=True)


def show_home():
    st.markdown(f"""
    <div class="hj-banner">
      <div class="hj-banner-top">
        <div>{logo_tag}</div>
        <div class="hj-team-label">품질기술팀</div>
      </div>
      <div class="hj-banner-bottom">
        <div class="hj-banner-title">품질 통합 관리 시스템</div>
        <div class="hj-banner-sub">사용할 앱을 선택하세요</div>
      </div>
    </div>
    <div class="hj-cards">
      <div class="hj-card">
        <div class="hj-card-icon">📏</div>
        <div class="hj-card-title">코일 실두께 데이터</div>
        <div class="hj-card-desc">재단일별 코일 실두께 측정 데이터<br>조회 및 관리</div>
      </div>
      <div class="hj-card">
        <div class="hj-card-icon">📋</div>
        <div class="hj-card-title">품질통합관리</div>
        <div class="hj-card-desc">고객 사양서 · 품질 보증 기준<br>부적합 관리 대장</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 투명 버튼으로 카드 클릭 처리
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='height:0'></div>", unsafe_allow_html=True)
        if st.button("📏 코일 실두께 데이터 열기", key="btn_coil", use_container_width=True):
            st.session_state.page = "coil"
            st.rerun()
    with col2:
        st.markdown("<div style='height:0'></div>", unsafe_allow_html=True)
        if st.button("📋 품질통합관리 열기", key="btn_cutting", use_container_width=True):
            st.session_state.page = "cutting"
            st.rerun()


if st.session_state.page == "home":
    show_home()

elif st.session_state.page == "coil":
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    import app_coil
    app_coil.run()

elif st.session_state.page == "cutting":
    if st.button("← 홈으로"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    import app_cutting
    app_cutting.run()
