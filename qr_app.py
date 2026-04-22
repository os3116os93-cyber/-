import streamlit as st
import fitz  # PyMuPDF
import qrcode
import io
import hashlib
from supabase import create_client, Client

# ── 페이지 설정 ───────────────────────────────────────────────────
st.set_page_config(page_title="한진철관 품질기술팀 QR 시스템", layout="centered")

# ── Supabase 연결 ─────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
BUCKET = "cert-images"

# ── 이미지 뷰어 페이지 (?view=key 파라미터) ───────────────────────
query_params = st.query_params
if "view" in query_params:
    img_key = query_params["view"]
    try:
        # Supabase Storage에서 공개 URL 가져오기
        res = supabase.storage.from_(BUCKET).get_public_url(img_key)
        st.markdown(
            f"""
            <div style='text-align:center; padding: 10px;'>
                <img src='{res}' style='max-width:100%; border: 1px solid #ddd; border-radius: 8px;'/>
                <p style='color:gray; margin-top:10px; font-size:13px;'>한진철관 품질기술팀 검사증명서</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"❌ 이미지를 불러올 수 없습니다. ({e})")
    st.stop()

# ── 메인 화면 ─────────────────────────────────────────────────────
st.title("🛡️ 검사증명서 QR 자동 삽입 도구")
st.markdown("---")

# 앱 공개 URL 입력 (Streamlit Cloud 배포 후 설정)
try:
    base_url = st.secrets.get("APP_URL", "").rstrip("/")
except Exception:
    base_url = ""

if not base_url:
    st.warning("⚙️ 앱 URL이 설정되지 않았습니다. 아래에 직접 입력해주세요.")
    base_url = st.text_input(
        "앱 URL 입력",
        placeholder="https://your-app-name.streamlit.app",
    ).rstrip("/")

if not base_url:
    st.info("👆 앱 URL을 입력해야 QR 코드를 생성할 수 있습니다.")
    st.stop()

uploaded_file = st.file_uploader("검사증명서 PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(len(doc)):
        page = doc[i]
        status_text.text(f"처리 중... {i + 1} / {len(doc)} 페이지")

        # 1. 페이지 → PNG 이미지 변환 (300dpi)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")

        # 2. 고유 파일명 생성
        raw_key = f"{uploaded_file.name}_page{i}"
        img_key = hashlib.md5(raw_key.encode()).hexdigest()[:16] + ".png"

        # 3. Supabase Storage에 업로드
        try:
            supabase.storage.from_(BUCKET).upload(
                path=img_key,
                file=img_bytes,
                file_options={"content-type": "image/png", "upsert": "true"},
            )
        except Exception as e:
            st.error(f"업로드 실패 (페이지 {i+1}): {e}")
            continue

        # 4. QR 코드 생성 (앱 URL + ?view=파일명)
        qr_url = f"{base_url}/?view={img_key}"
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

        # 6. PDF에 QR 삽입 (우측 하단)
        page_width = page.rect.width
        page_height = page.rect.height

        qr_size = 55
        x0 = page_width - 85
        y0 = page_height - 140
        x1 = x0 + qr_size
        y1 = y0 + qr_size

        qr_rect = fitz.Rect(x0, y0, x1, y1)
        page.insert_image(qr_rect, stream=qr_io.getvalue(), overlay=True)

        progress_bar.progress((i + 1) / len(doc))

    status_text.text("✅ 모든 페이지 처리 완료!")

    # 결과 PDF 저장
    output_pdf = doc.write()
    doc.close()

    st.success("✅ QR 코드 삽입이 완료되었습니다!")
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
