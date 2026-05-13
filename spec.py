import streamlit as st
import os
import base64

st.set_page_config(
    page_title="한진철관 품질기술팀",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="auto"
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
    f'<img src="data:image/png;base64,{logo_b64}" style="height:40px;width:auto;max-width:160px;object-fit:contain;display:block;">'
    if logo_b64 else '<span style="font-size:18px;font-weight:900;color:#FF8C00;">한진철관</span>'
)
BG_B64 = "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"

if "page" not in st.session_state:
    st.session_state.page = "home"

# ── 전역 CSS (f-string 없이 — 중괄호 충돌 없음) ──
# ── 공통 CSS (폰트·헤더 숨김만 — 사이드바/레이아웃 영향 없는 것만) ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }
.stApp > header { display: none !important; }
#stDecoration   { display: none !important; }
.stApp          { overflow-x: hidden; }
[data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }

/* ── 홈 바 ── */
.home-bar {
    background: #fff; border-bottom: 1px solid #e8eaed;
    padding: 8px 20px; display: flex; align-items: center; gap: 10px;
}

/* ════════════════════════════════════════
   카드 + 버튼 레이아웃
   .hj-home 클래스로 스코프 제한 → app_coil 등 서브페이지에 영향 없음
   ════════════════════════════════════════ */

/* 카드 본문 */
.hj-card {
    background: #fff;
    border: 1.5px solid #e8eaed;
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 18px 18px 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    margin-bottom: 0;
}
.hj-card-dis {
    background: #f8f9fa;
    border: 1.5px solid #e2e5e9;
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 18px 18px 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    margin-bottom: 0;
    opacity: 0.72;
}

/* 배지 */
.hj-badge     { background: #FFF3E0; color: #E65100; font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 20px; letter-spacing: .06em; width: fit-content; }
.hj-badge-dis { background: #f0f0f0; color: #9ca3af;  font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 20px; letter-spacing: .06em; width: fit-content; }
.hj-soon      { background: #f3f4f6; color: #9ca3af;  font-size: 9px;  font-weight: 800; padding: 3px 8px;  border-radius: 20px; border: 1px solid #e5e7eb; letter-spacing: .08em; width: fit-content; }
.hj-badge-row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.hj-icon      { font-size: 1.75rem; margin: 4px 0; }
.hj-icon-dis  { font-size: 1.75rem; margin: 4px 0; filter: grayscale(1); opacity: .35; }
.hj-ttl       { font-size: 1rem;  font-weight: 800; color: #1a1a2e; }
.hj-ttl-dis   { font-size: 1rem;  font-weight: 800; color: #9ca3af; }
.hj-desc      { font-size: .76rem; color: #6b7280;  line-height: 1.6; }
.hj-desc-dis  { font-size: .76rem; color: #b0b7c0;  line-height: 1.6; }

/* 비활성 버튼 div */
.hj-btn-dis {
    display: flex; align-items: center; justify-content: center; gap: 6px;
    width: 100%; height: 46px;
    background: #e9ecef; color: #adb5bd;
    font-size: 1rem; font-weight: 700;
    border: none; border-radius: 0 0 14px 14px;
    cursor: not-allowed; pointer-events: none;
    box-sizing: border-box; margin: 0;
    opacity: 0.72;
}

/* ══ 홈 전용: :has(.hj-home-marker) 로 스코프 제한
      → 홈 페이지에서만 stHorizontalBlock 스타일 적용
      → app_coil 등 서브페이지 필터에 영향 없음 ══ */
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] {
    gap: 16px !important;
    padding: 0 28px 28px 28px !important;
    background: #f0f2f6 !important;
    margin-top: 0 !important;
    align-items: stretch !important;
}
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] > div {
    padding: 0 !important;
    margin: 0 !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #FF8C00 0%, #E65100 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 0 14px 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    height: 48px !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-shadow: 0 3px 10px rgba(255,140,0,.22) !important;
    transition: opacity .15s !important;
}
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover { opacity: .85 !important; }
.stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button p { margin: 0 !important; padding: 0 !important; }

/* ══ 모바일 ══ */
@media (max-width: 720px) {
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 12px !important;
        padding: 0 14px 22px 14px !important;
    }
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] > div {
        width: calc(50% - 6px) !important;
        flex: 0 0 calc(50% - 6px) !important;
    }
    .hj-card, .hj-card-dis { padding: 14px 13px 12px 13px; }
    .hj-ttl, .hj-ttl-dis   { font-size: .9rem; }
    .hj-icon, .hj-icon-dis  { font-size: 1.4rem; }
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button { height: 46px !important; font-size: .9rem !important; }
    .hj-btn-dis { height: 46px; font-size: .9rem; }
}
@media (max-width: 400px) {
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] {
        gap: 10px !important;
        padding: 0 10px 18px 10px !important;
    }
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] > div {
        width: calc(50% - 5px) !important;
        flex: 0 0 calc(50% - 5px) !important;
    }
    .hj-card, .hj-card-dis { padding: 12px 10px 10px 10px; gap: 3px; }
    .hj-desc, .hj-desc-dis  { display: none; }
    .hj-ttl, .hj-ttl-dis    { font-size: .82rem; }
    .hj-icon, .hj-icon-dis   { font-size: 1.2rem; margin: 2px 0; }
    .hj-badge, .hj-badge-dis, .hj-soon { font-size: 9px; padding: 2px 7px; }
    .stApp:has(.hj-home-marker) [data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button { height: 44px !important; font-size: .82rem !important; }
    .hj-btn-dis { height: 44px; font-size: .82rem; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  홈 화면
# ═══════════════════════════════════════
def show_home():
    # 홈 전용 CSS: display:none 대신 width/opacity로 숨김 → 서브페이지 복원 가능
    st.markdown("""
<style>
[data-testid="stSidebar"] {
    width: 0 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
    padding: 0 !important;
}
[data-testid="stSidebarCollapsedControl"] {
    width: 0 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
}
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; background: #f0f2f6; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] > div:first-child > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

    # 홈 페이지 마커
    st.markdown('<div class="hj-home-marker"></div>', unsafe_allow_html=True)

    # ── 1) 배너 HTML (f-string — BG_B64, logo_tag 변수 사용) ──
    # CSS는 위 전역 블록에 있으므로 여기선 HTML만
    banner_html = f"""
<div style="
    position:relative; width:100%; min-height:210px; overflow:hidden;
    background:#0d0d0d; display:flex; flex-direction:column;
    justify-content:space-between; padding:38px 24px 24px 24px;
    box-sizing:border-box; line-height:1;
">
  <div style="position:absolute;inset:0;
    background-image:url('data:image/jpeg;base64,{BG_B64}');
    background-size:cover;background-position:center 30%;
    opacity:.32;filter:grayscale(15%);"></div>
  <div style="position:absolute;inset:0;
    background:linear-gradient(140deg,rgba(10,10,10,.92) 0%,rgba(20,20,20,.68) 55%,rgba(255,140,0,.10) 100%);
  "></div>
  <div style="position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;gap:8px;">
    <div style="flex-shrink:0;">{logo_tag}</div>
    <div style="background:rgba(255,140,0,.2);border:1px solid rgba(255,140,0,.5);color:#FFB347;
      font-size:clamp(9px,2.5vw,11px);font-weight:700;padding:4px 10px;border-radius:20px;
      letter-spacing:.06em;white-space:nowrap;">품질기술팀</div>
  </div>
  <div style="position:relative;z-index:2;margin-top:14px;">
    <div style="font-size:clamp(8px,2vw,10px);font-weight:700;color:#FF8C00;
      letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px;">Quality Management System</div>
    <div style="font-size:clamp(1.2rem,4vw,2rem);font-weight:900;color:#fff;
      line-height:1.25;margin-bottom:6px;letter-spacing:-.02em;word-break:keep-all;">
      품질 통합 <span style="color:#FF8C00;">관리 시스템</span>
    </div>
    <div style="font-size:clamp(10px,2.5vw,12px);color:rgba(255,255,255,.5);">아래에서 사용할 앱을 선택하세요</div>
  </div>
</div>
"""
    st.markdown(banner_html, unsafe_allow_html=True)

    # ── 2) 카드 HTML (f-string 없이 — 중괄호 충돌 위험 없음) ──
    # 각 카드를 st.columns 열 안에 개별 st.markdown으로 렌더링
    # → 카드 바로 아래에 st.button이 위치 → CSS로 완벽히 밀착
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
<div class="hj-card">
  <span class="hj-badge">INSPECTION</span>
  <div class="hj-icon">📐</div>
  <div class="hj-ttl">중간검사성적서</div>
  <div class="hj-desc">재단일별 코일 실두께 측정 데이터<br>조회 및 현황 파악</div>
</div>
""", unsafe_allow_html=True)
        if st.button("📐 중간검사성적서 들어가기", key="btn_coil", use_container_width=True):
            st.session_state.page = "coil"
            st.rerun()

    with col2:
        st.markdown("""
<div class="hj-card">
  <span class="hj-badge">QUALITY</span>
  <div class="hj-icon">📋</div>
  <div class="hj-ttl">품질통합관리</div>
  <div class="hj-desc">고객 사양서 · 품질 보증 기준<br>부적합 관리 대장</div>
</div>
""", unsafe_allow_html=True)
        if st.button("📋 품질통합관리 들어가기", key="btn_cutting", use_container_width=True):
            st.session_state.page = "cutting"
            st.rerun()

    with col3:
        st.markdown("""
<div class="hj-card-dis">
  <div class="hj-badge-row">
    <span class="hj-badge-dis">SYSTEM</span>
    <span class="hj-soon">COMING SOON</span>
  </div>
  <div class="hj-icon-dis">🔧</div>
  <div class="hj-ttl-dis">준비 중</div>
  <div class="hj-desc-dis">서비스 준비 중입니다</div>
</div>
<div class="hj-btn-dis">🔧&nbsp;준비 중</div>
""", unsafe_allow_html=True)

    with col4:
        st.markdown("""
<div class="hj-card-dis">
  <div class="hj-badge-row">
    <span class="hj-badge-dis">SYSTEM</span>
    <span class="hj-soon">COMING SOON</span>
  </div>
  <div class="hj-icon-dis">📊</div>
  <div class="hj-ttl-dis">준비 중</div>
  <div class="hj-desc-dis">서비스 준비 중입니다</div>
</div>
<div class="hj-btn-dis">📊&nbsp;준비 중</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  서브페이지 헤더
# ═══════════════════════════════════════
def _render_home_btn():
    # 서브페이지: 홈에서 주입된 CSS를 덮어써서 사이드바·레이아웃 완전 복원
    st.markdown("""
<style>
[data-testid="stSidebar"] {
    width: auto !important;
    min-width: 0 !important;
    overflow: visible !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapsedControl"] {
    width: auto !important;
    min-width: 0 !important;
    overflow: visible !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
button[data-testid="baseButton-headerNoPadding"] svg {
    display: inline !important;
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)
    st.markdown(f"""
<div class="home-bar">
  {logo_tag}
  <span style="font-size:12px;color:#d1d5db;">|</span>
  <span style="font-size:12px;color:#6b7280;font-weight:600;white-space:nowrap;">품질기술팀</span>
</div>
""", unsafe_allow_html=True)
    if st.button("← 홈으로 돌아가기", key="home_back_btn"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  라우팅
# ═══════════════════════════════════════
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
