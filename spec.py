import streamlit as st
import streamlit.components.v1 as components
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
    f'<img src="data:image/png;base64,{logo_b64}" style="height:40px;width:auto;max-width:160px;object-fit:contain;display:block;">'
    if logo_b64 else '<span style="font-size:18px;font-weight:900;color:#FF8C00;">한진철관</span>'
)
BG_B64 = "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"

if "page" not in st.session_state:
    st.session_state.page = "home"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }

.stApp > header { display: none !important; height: 0 !important; }
#stDecoration   { display: none !important; }
.stApp          { overflow-x: hidden; }
[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
    margin-top:  0 !important;
}
[data-testid="stAppViewContainer"] > .main {
    padding-top: 0 !important;
    background: #f0f2f6;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > div:first-child > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* 들어가기 버튼 */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #FF8C00 0%, #E65100 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 0 0 14px 14px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    height: 44px !important;
    transition: opacity .15s !important;
    box-shadow: 0 3px 10px rgba(255,140,0,0.28) !important;
    margin-top: 0 !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.85 !important;
}

/* 홈 버튼 바 */
.home-bar {
    background: #fff;
    border-bottom: 1px solid #e8eaed;
    padding: 8px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: nowrap;
    overflow: visible;
}
.home-bar img {
    height: 36px;
    width: auto;
    max-width: 140px;
    object-fit: contain;
    flex-shrink: 0;
}

/* 숨겨진 네비게이션 트리거 버튼 완전 숨김 */
button[data-hj-page] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    position: absolute !important;
    pointer-events: none !important;
}
/* 숨긴 버튼 감싸는 컬럼 여백도 제거 */
[data-testid="stHorizontalBlock"]:has(button[data-hj-page]) {
    margin: 0 !important;
    padding: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    gap: 0 !important;
}
</style>
""", unsafe_allow_html=True)


def show_home():
    st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }
/* iframe(components.html) 감싸는 div 여백 제거 */
[data-testid="stVerticalBlock"] iframe { display: block; }
div[data-testid="stCustomComponentV1"] { line-height: 0; }
</style>
""", unsafe_allow_html=True)

    # ── 배너 (st.markdown으로 렌더) ──
    st.markdown(f"""
<div style="
    position:relative; width:100%; min-height:220px; overflow:hidden;
    background:#0d0d0d; display:flex; flex-direction:column;
    justify-content:space-between; padding:40px 24px 24px 24px;
    box-sizing:border-box; margin:0; line-height:1;">
  <div style="position:absolute;inset:0;
    background-image:url('data:image/jpeg;base64,{BG_B64}');
    background-size:cover;background-position:center 30%;
    opacity:0.32;filter:grayscale(15%);"></div>
  <div style="position:absolute;inset:0;
    background:linear-gradient(140deg,rgba(10,10,10,0.92) 0%,rgba(20,20,20,0.68) 55%,rgba(255,140,0,0.10) 100%);
  "></div>
  <div style="position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;flex-wrap:nowrap;gap:8px;">
    <div style="flex-shrink:0;">{logo_tag}</div>
    <div style="background:rgba(255,140,0,0.2);border:1px solid rgba(255,140,0,0.5);
      color:#FFB347;font-size:clamp(9px,2.5vw,11px);font-weight:700;
      padding:4px 10px;border-radius:20px;letter-spacing:0.06em;white-space:nowrap;flex-shrink:0;">품질기술팀</div>
  </div>
  <div style="position:relative;z-index:2;margin-top:14px;">
    <div style="font-size:clamp(8px,2vw,10px);font-weight:700;color:#FF8C00;letter-spacing:0.2em;
      text-transform:uppercase;margin-bottom:6px;">Quality Management System</div>
    <div style="font-size:clamp(1.2rem,3.5vw,2rem);font-weight:900;color:#fff;
      line-height:1.25;margin-bottom:6px;letter-spacing:-0.02em;word-break:keep-all;">
      품질 통합 <span style="color:#FF8C00;">관리 시스템</span></div>
    <div style="font-size:clamp(10px,2.5vw,12px);color:rgba(255,255,255,0.5);">아래에서 사용할 앱을 선택하세요</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 카드+버튼 완전 HTML 블록 (components.html → postMessage) ──
    card_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800;900&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Noto Sans KR', sans-serif; }
body { background: #f0f2f6; padding: 20px 24px 28px 24px; }

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

/* ── 카드 단위 (카드 + 버튼 묶음) ── */
.card-wrap {
    display: flex;
    flex-direction: column;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.card-wrap.disabled {
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    opacity: 0.72;
}

/* 카드 본체 */
.card-body {
    background: #fff;
    border: 1.5px solid #e8eaed;
    border-bottom: none;
    padding: 20px 18px 16px 18px;
    flex: 1;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.card-wrap.disabled .card-body {
    background: #f8f9fa;
    border-color: #e2e5e9;
}

.badge {
    background: #FFF3E0; color: #E65100;
    font-size: 10px; font-weight: 800;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.06em; margin-bottom: 11px;
}
.badge-disabled {
    background: #f0f0f0; color: #9ca3af;
    font-size: 10px; font-weight: 800;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.06em; margin-bottom: 11px;
}
.coming-badge {
    position: absolute; top: 12px; right: 12px;
    background: #f3f4f6; color: #9ca3af;
    font-size: 9px; font-weight: 800;
    padding: 2px 7px; border-radius: 20px;
    letter-spacing: 0.08em; border: 1px solid #e5e7eb;
}
.card-icon { font-size: 1.8rem; margin-bottom: 8px; line-height: 1; }
.card-title { font-size: 1rem; font-weight: 800; color: #1a1a2e; margin-bottom: 5px; }
.card-title-disabled { font-size: 1rem; font-weight: 800; color: #9ca3af; margin-bottom: 5px; }
.card-desc { font-size: 0.75rem; color: #6b7280; line-height: 1.6; }
.card-desc-disabled { font-size: 0.75rem; color: #b0b7c0; line-height: 1.6; }

/* 버튼 (카드 바로 아래 밀착) */
.card-btn {
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 44px;
    background: linear-gradient(135deg, #FF8C00 0%, #E65100 100%);
    color: #fff; font-size: 13px; font-weight: 700;
    border: none; cursor: pointer;
    transition: opacity 0.15s;
    letter-spacing: 0.01em;
    flex-shrink: 0;
}
.card-btn:hover { opacity: 0.85; }
.card-btn:active { opacity: 0.7; }

.card-btn-disabled {
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 44px;
    background: #e9ecef; color: #adb5bd;
    font-size: 13px; font-weight: 700;
    border: none; cursor: not-allowed;
    letter-spacing: 0.01em;
    flex-shrink: 0;
    pointer-events: none;
}

/* 모바일: 2열 */
@media (max-width: 700px) {
    body { padding: 14px 14px 22px 14px; }
    .grid { grid-template-columns: 1fr 1fr; gap: 12px; }
    .card-body { padding: 14px 12px 12px 12px; }
    .card-title, .card-title-disabled { font-size: 0.88rem; }
    .card-icon { font-size: 1.5rem; margin-bottom: 6px; }
    .card-desc, .card-desc-disabled { font-size: 0.7rem; }
    .card-btn, .card-btn-disabled { height: 40px; font-size: 12px; }
}

@media (max-width: 400px) {
    body { padding: 10px 10px 18px 10px; }
    .grid { gap: 9px; }
    .card-body { padding: 12px 10px 10px 10px; }
    .card-title, .card-title-disabled { font-size: 0.82rem; }
    .card-desc, .card-desc-disabled { display: none; }
    .card-btn, .card-btn-disabled { height: 38px; font-size: 11px; }
}
</style>
</head>
<body>
<div class="grid">

  <!-- 카드 1 -->
  <div class="card-wrap">
    <div class="card-body">
      <div class="badge">INSPECTION</div>
      <div class="card-icon">📐</div>
      <div class="card-title">중간검사성적서</div>
      <div class="card-desc">재단일별 코일 실두께 측정 데이터<br>조회 및 현황 파악</div>
    </div>
    <button class="card-btn" onclick="go('coil')">📐 중간검사성적서 들어가기</button>
  </div>

  <!-- 카드 2 -->
  <div class="card-wrap">
    <div class="card-body">
      <div class="badge">QUALITY</div>
      <div class="card-icon">📋</div>
      <div class="card-title">품질통합관리</div>
      <div class="card-desc">고객 사양서 · 품질 보증 기준<br>부적합 관리 대장</div>
    </div>
    <button class="card-btn" onclick="go('cutting')">📋 품질통합관리 들어가기</button>
  </div>

  <!-- 카드 3 준비중 -->
  <div class="card-wrap disabled">
    <div class="card-body">
      <span class="coming-badge">COMING SOON</span>
      <div class="badge-disabled">SYSTEM</div>
      <div class="card-icon" style="filter:grayscale(1);opacity:0.35;">🔧</div>
      <div class="card-title-disabled">준비 중</div>
      <div class="card-desc-disabled">서비스 준비 중입니다</div>
    </div>
    <div class="card-btn-disabled">🔧 준비 중</div>
  </div>

  <!-- 카드 4 준비중 -->
  <div class="card-wrap disabled">
    <div class="card-body">
      <span class="coming-badge">COMING SOON</span>
      <div class="badge-disabled">SYSTEM</div>
      <div class="card-icon" style="filter:grayscale(1);opacity:0.35;">📊</div>
      <div class="card-title-disabled">준비 중</div>
      <div class="card-desc-disabled">서비스 준비 중입니다</div>
    </div>
    <div class="card-btn-disabled">📊 준비 중</div>
  </div>

</div>
<script>
function go(page) {
    window.parent.postMessage({type: 'hj_nav', page: page}, '*');
}
</script>
</body>
</html>
"""
    # components.html 높이: 카드 높이에 충분한 여유
    clicked = components.html(card_html, height=340, scrolling=False)

    # postMessage 수신 → session_state 전환
    nav_js = """
<script>
window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'hj_nav') {
        const page = e.data.page;
        // Streamlit의 hidden input trick으로 session_state 변경
        const inputs = window.parent.document.querySelectorAll('input[type=text]');
        // postMessage를 Streamlit query param 방식으로 전달
        const url = new URL(window.parent.location.href);
        url.searchParams.set('hj_page', page);
        window.parent.history.replaceState({}, '', url.toString());
        // Streamlit에 직접 접근 가능한 방법: 숨겨진 버튼 클릭
        const btn = window.parent.document.querySelector('button[data-hj-page="' + page + '"]');
        if (btn) btn.click();
    }
}, false);
</script>
"""
    st.markdown(nav_js, unsafe_allow_html=True)

    # 숨겨진 트리거 버튼들 (postMessage에서 클릭됨)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        if st.button("__coil__", key="hidden_coil"):
            st.session_state.page = "coil"
            st.rerun()
    with col_h2:
        if st.button("__cutting__", key="hidden_cutting"):
            st.session_state.page = "cutting"
            st.rerun()

    # 버튼에 data-hj-page 속성 주입
    st.markdown("""
<script>
(function() {
    function tagBtns() {
        const btns = window.parent.document.querySelectorAll('button');
        btns.forEach(function(b) {
            if (b.innerText.trim() === '__coil__') {
                b.setAttribute('data-hj-page', 'coil');
                b.style.display = 'none';
            }
            if (b.innerText.trim() === '__cutting__') {
                b.setAttribute('data-hj-page', 'cutting');
                b.style.display = 'none';
            }
        });
    }
    tagBtns();
    setTimeout(tagBtns, 500);
    setTimeout(tagBtns, 1500);
})();
</script>
""", unsafe_allow_html=True)


def _render_home_btn():
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
