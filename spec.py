import streamlit as st

st.set_page_config(
    page_title="품질 관리 시스템",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* 전체 배경 */
  .stApp { background: #f0f2f6; }

  /* 메인 배너 */
  .banner-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    color: #1a1a2e;
    padding: 1.5rem 0 0.3rem 0;
  }
  .banner-sub {
    text-align: center;
    color: #555;
    font-size: 0.95rem;
    margin-bottom: 2rem;
  }

  /* 카드 박스 */
  .app-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    border: 2px solid transparent;
    min-height: 220px;
  }
  .app-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    border-color: #4f8ef7;
  }
  .app-card .icon { font-size: 3rem; margin-bottom: 0.8rem; }
  .app-card h3 { font-size: 1.3rem; font-weight: 700; margin: 0.5rem 0; color: #1a1a2e; }
  .app-card p  { color: #666; font-size: 0.88rem; line-height: 1.5; margin: 0; }

  /* 뒤로가기 버튼 */
  .stButton > button {
    border-radius: 8px;
    font-weight: 600;
  }

  /* 구분선 */
  hr { border-color: #e0e0e0; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ── 세션 초기화 ───────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"


# ── 홈 화면 ───────────────────────────────────────────────────────────
def show_home():
    st.markdown('<div class="banner-title">🏭 품질 관리 시스템</div>', unsafe_allow_html=True)
    st.markdown('<div class="banner-sub">사용할 앱을 선택하세요</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="app-card">
          <div class="icon">📏</div>
          <h3>코일 실두께 데이터</h3>
          <p>재단일별 코일 실두께 측정 데이터 조회<br>A팀·B팀 데이터 통합 뷰어</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📏 코일 실두께 앱 열기", key="btn_coil", use_container_width=True):
            st.session_state.page = "coil"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="app-card">
          <div class="icon">✂️</div>
          <h3>재단 실적 관리</h3>
          <p>재단 작업 실적 입력 및 현황 조회<br>구글 시트 연동 실시간 업데이트</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✂️ 재단 실적 앱 열기", key="btn_cutting", use_container_width=True):
            st.session_state.page = "cutting"
            st.rerun()

    st.markdown("---")
    st.caption("© 품질관리팀 | 문의: 담당자에게 연락하세요")


# ── 페이지 라우팅 ─────────────────────────────────────────────────────
if st.session_state.page == "home":
    show_home()

elif st.session_state.page == "coil":
    if st.button("← 홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    # 코일 실두께 앱 임포트
    import app_coil
    app_coil.run()

elif st.session_state.page == "cutting":
    if st.button("← 홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("---")
    # 기존 재단 실적 앱 임포트
    import app_cutting
    app_cutting.run()
