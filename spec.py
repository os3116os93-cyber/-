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

def _img_b64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = _img_b64(os.path.join(BASE_DIR, "hanjin_logo.png"))
logo_tag = (
    f\'<img src="data:image/png;base64,{logo_b64}" style="height:44px;width:auto;">\' 
    if logo_b64 else \'<span style="font-size:18px;font-weight:900;color:#FF8C00;">한진철관</span>\'
)

BG_B64 = "''' + bg_b64 + '''"

if "page" not in st.session_state:
    st.session_state.page = "home"

st.markdown("""
<style>
@import url(\'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap\');
* { font-family: \'Noto Sans KR\', sans-serif !important; }
[data-testid="stAppViewContainer"] > .main { background:#f0f2f6; }
[data-testid="stSidebar"] { display:none !important; }
.block-container {
    padding-top:0 !important; padding-bottom:0 !important;
    padding-left:0 !important; padding-right:0 !important;
    max-width:100% !important;
}
</style>
""", unsafe_allow_html=True)


def show_home():
    st.markdown(f"""
<style>
.hj-outer {{ background:#f0f2f6; min-height:100vh; }}
.hj-hero {{
    position:relative; width:100%;
    min-height:270px; overflow:hidden; background:#0d0d0d;
    display:flex; flex-direction:column;
    justify-content:space-between;
    padding:24px 36px 32px 36px; box-sizing:border-box;
}}
.hj-hero-bg {{
    position:absolute; inset:0;
    background-image:url("data:image/jpeg;base64,{BG_B64}");
    background-size:cover; background-position:center 30%;
    opacity:0.32; filter:grayscale(15%);
}}
.hj-hero-overlay {{
    position:absolute; inset:0;
    background:linear-gradient(140deg,rgba(10,10,10,0.9) 0%,rgba(20,20,20,0.65) 55%,rgba(255,140,0,0.12) 100%);
}}
.hj-hero-top {{
    position:relative; z-index:2;
    display:flex; justify-content:space-between; align-items:center;
}}
.hj-team-pill {{
    background:rgba(255,140,0,0.2); border:1px solid rgba(255,140,0,0.5);
    color:#FFB347; font-size:11px; font-weight:700;
    padding:4px 14px; border-radius:20px; letter-spacing:0.08em; white-space:nowrap;
}}
.hj-hero-body {{ position:relative; z-index:2; margin-top:16px; }}
.hj-hero-eyebrow {{
    font-size:10px; font-weight:700; color:#FF8C00;
    letter-spacing:0.2em; text-transform:uppercase; margin-bottom:8px;
}}
.hj-hero-title {{
    font-size:clamp(1.35rem,3.2vw,2.1rem); font-weight:900;
    color:#fff; line-height:1.2; margin-bottom:8px;
    letter-spacing:-0.02em; word-break:keep-all;
}}
.hj-hero-title span {{ color:#FF8C00; }}
.hj-hero-sub {{ font-size:12px; color:rgba(255,255,255,0.5); }}

/* 카드 */
.hj-grid {{
    display:grid; grid-template-columns:1fr 1fr;
    gap:18px; padding:22px 36px 8px 36px; box-sizing:border-box;
    max-width:860px;
}}
.hj-card {{
    background:#fff; border-radius:14px;
    border:1.5px solid #e8eaed;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
    padding:22px 20px 18px 20px;
    display:flex; flex-direction:column; align-items:flex-start;
    position:relative; overflow:hidden;
}}
.hj-card::after {{
    content:\'\'; position:absolute; bottom:0; left:0; right:0;
    height:3px; background:linear-gradient(90deg,#FF8C00,#FFB347);
    transform:scaleX(0); transform-origin:left; transition:transform .22s;
}}
.hj-card:hover::after {{ transform:scaleX(1); }}
.hj-card-badge {{
    background:#FFF3E0; color:#E65100; font-size:10px; font-weight:800;
    padding:3px 10px; border-radius:20px; letter-spacing:0.06em; margin-bottom:12px;
}}
.hj-card-icon {{ font-size:1.9rem; margin-bottom:9px; }}
.hj-card-title {{ font-size:1.05rem; font-weight:800; color:#1a1a2e; margin-bottom:5px; }}
.hj-card-desc {{ font-size:0.78rem; color:#6b7280; line-height:1.6; margin:0; }}

/* 버튼 그리드 */
.hj-btn-grid {{
    display:grid; grid-template-columns:1fr 1fr;
    gap:18px; padding:10px 36px 36px 36px;
    box-sizing:border-box; max-width:860px;
}}

@media(max-width:640px) {{
    .hj-hero {{ min-height:210px; padding:18px 18px 22px 18px; }}
    .hj-hero-title {{ font-size:1.25rem; }}
    .hj-grid {{ grid-template-columns:1fr; padding:16px 16px 6px 16px; gap:12px; max-width:100%; }}
    .hj-btn-grid {{ grid-template-columns:1fr; padding:6px 16px 24px 16px; gap:10px; max-width:100%; }}
    .hj-card {{ padding:18px 16px 14px 16px; }}
}}
</style>

<div class="hj-outer">
  <div class="hj-hero">
    <div class="hj-hero-bg"></div>
    <div class="hj-hero-overlay"></div>
    <div class="hj-hero-top">
      <div>{logo_tag}</div>
      <div class="hj-team-pill">품질기술팀</div>
    </div>
    <div class="hj-hero-body">
      <div class="hj-hero-eyebrow">Quality Management System</div>
      <div class="hj-hero-title">품질 통합<span> 관리 시스템</span></div>
      <div class="hj-hero-sub">아래에서 사용할 앱을 선택하세요</div>
    </div>
  </div>

  <div class="hj-grid">
    <div class="hj-card">
      <div class="hj-card-badge">INSPECTION</div>
      <div class="hj-card-icon">📐</div>
      <div class="hj-card-title">중간검사성적서</div>
      <div class="hj-card-desc">재단일별 코일 실두께 측정 데이터<br>조회 및 현황 파악</div>
    </div>
    <div class="hj-card">
      <div class="hj-card-badge">QUALITY</div>
      <div class="hj-card-icon">📋</div>
      <div class="hj-card-title">품질통합관리</div>
      <div class="hj-card-desc">고객 사양서 · 품질 보증 기준<br>부적합 관리 대장</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📐 중간검사성적서 열기", key="btn_coil", use_container_width=True, type="primary"):
            st.session_state.page = "coil"
            st.rerun()
    with col2:
        if st.button("📋 품질통합관리 열기", key="btn_cutting", use_container_width=True, type="primary"):
            st.session_state.page = "cutting"
            st.rerun()


def _render_home_btn():
    st.markdown(f"""
<div style="background:#fff;border-bottom:1px solid #e8eaed;padding:10px 20px;
            display:flex;align-items:center;gap:10px;margin-bottom:8px;">
  {logo_tag}
  <span style="font-size:12px;color:#d1d5db;">|</span>
  <span style="font-size:12px;color:#6b7280;font-weight:600;">품질기술팀</span>
</div>
""", unsafe_allow_html=True)
    if st.button("← 홈으로 돌아가기", key="home_back_btn"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("<div style=\'height:4px\'></div>", unsafe_allow_html=True)


# ── 라우팅 ────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    show_home()

elif st.session_state.page == "coil":
    _render_home_btn()
    import app_coil
    app_coil.run()

elif st.session_state.page == "cutting":
    _render_home_btn()
    import app_cutting
    app_cutting.run()
'''

with open('/home/claude/streamlit_project/streamlit_app.py', 'w') as f:
    f.write(content)
print("streamlit_app.py 완료, 길이:", len(content))
