import streamlit as st
import fitz  # PyMuPDF
import qrcode
import io
import hashlib
import requests

# ── 페이지 설정 ───────────────────────────────────────────────────
st.set_page_config(page_title="한진철관 품질기술팀 QR 시스템", layout="centered")

# ── Supabase 설정 ─────────────────────────────────────────────────
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
APP_URL      = st.secrets["APP_URL"].rstrip("/")
BUCKET       = "cert-images"

def upload_to_supabase(img_bytes: bytes, img_key: str) -> bool:
    """Supabase Storage에 이미지 업로드 (requests 직접 호출)"""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{img_key}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/png",
        "x-upsert": "true",
    }
    res = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    return res.status_code in (200, 201)

def get_public_url(img_key: str) -> str:
    """Supabase Storage 공개 URL 반환"""
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{img_key}"

# ── 이미지 뷰어 페이지 (?view=key 파라미터) ───────────────────────
query_params = st.query_params
if "view" in query_params:
    img_key = query_params["view"]
    img_url = get_public_url(img_key)
    st.markdown(
        f"""
        <div style='text-align:center; padding: 10px;'>
            <img src='{img_url}' style='max-width:100%; border: 1px solid #ddd; border-radius: 8px;'/>
            <p style='color:gray; margin-top:10px; font-size:13px;'>한진철관 품질기술팀 검사증명서</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── 메인 화면 ─────────────────────────────────────────────────────
st.title("🛡️ 검사증명서 QR 자동 삽입 도구")
st.markdown("---")

# ── 사이드바: QR 삽입 옵션 ────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ QR 삽입 옵션")

    qr_position = st.selectbox(
        "QR 코드 위치",
        options=["bottom-right", "bottom-left", "top-right", "top-left"],
        format_func=lambda x: {
            "bottom-right": "우하단 ↘ (기본)",
            "bottom-left":  "좌하단 ↙",
            "top-right":    "우상단 ↗",
            "top-left":     "좌상단 ↖",
        }[x],
        index=0,
    )

    qr_size = st.slider("QR 코드 크기 (pt)", min_value=40, max_value=100, value=55, step=5)
    dpi     = st.slider("이미지 해상도 (DPI)", min_value=72, max_value=300, value=300, step=1,
                        help="높을수록 선명하나 처리 시간 증가")

def calc_qr_position(page_width: float, page_height: float, size: int, position: str, margin: int = 15):
    """QR 코드 삽입 좌표 계산 (fitz.Rect 기준)"""
    if position == "bottom-right":
        x0 = page_width  - size - margin
        y0 = page_height - size - margin
    elif position == "bottom-left":
        x0 = margin
        y0 = page_height - size - margin
    elif position == "top-right":
        x0 = page_width  - size - margin
        y0 = margin
    else:  # top-left
        x0 = margin
        y0 = margin
    return fitz.Rect(x0, y0, x0 + size, y0 + size)

# ── 파일 업로드 ───────────────────────────────────────────────────
uploaded_file = st.file_uploader("검사증명서 PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    progress_bar = st.progress(0)
    status_text  = st.empty()
    fail_count   = 0

    for i in range(len(doc)):
        page = doc[i]
        status_text.text(f"처리 중... {i + 1} / {len(doc)} 페이지")

        # 1. 페이지 → PNG 이미지 변환
        pix       = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")

        # 2. 고유 파일명 생성
        raw_key = f"{uploaded_file.name}_page{i}"
        img_key = hashlib.md5(raw_key.encode()).hexdigest()[:16] + ".png"

        # 3. Supabase Storage에 업로드
        success = upload_to_supabase(img_bytes, img_key)
        if not success:
            st.error(f"❌ 업로드 실패 (페이지 {i+1})")
            fail_count += 1
            continue

        # 4. QR 코드 생성
        qr_url = f"{APP_URL}/?view={img_key}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # 5. QR 이미지 메모리 저장
        qr_io = io.BytesIO()
        qr_img.save(qr_io, format="PNG")

        # 6. PDF에 QR 삽입 (위치 옵션 반영)
        qr_rect = calc_qr_position(
            page.rect.width, page.rect.height,
            size=qr_size,
            position=qr_position,
        )
        page.insert_image(qr_rect, stream=qr_io.getvalue(), overlay=True)

        progress_bar.progress((i + 1) / len(doc))

    status_text.text("✅ 모든 페이지 처리 완료!")

    # 결과 PDF 저장
    output_pdf = doc.write()
    doc.close()

    if fail_count == 0:
        st.success("✅ QR 코드 삽입이 완료되었습니다!")
    else:
        st.warning(f"⚠️ {fail_count}개 페이지 업로드 실패. 나머지는 정상 처리되었습니다.")

    st.download_button(
        label="📥 QR 삽입된 PDF 다운로드",
        data=output_pdf,
        file_name=f"QR_Certified_{uploaded_file.name}",
        mime="application/pdf",
    )
    st.info("📱 QR 코드는 인터넷이 되는 환경이라면 언제 어디서든 스캔 가능합니다.")

# 하단 정보
st.markdown("---")
st.caption("품질기술팀 내부 업무용 자동화 도구 | PyMuPDF & Streamlit & Supabase 기반")

