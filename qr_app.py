import streamlit as st
import fitz  # PyMuPDF
import qrcode
import io
import requests
import hashlib
import os

# ── [중요] 페이지 설정은 반드시 최상단에 위치해야 합니다 ─────────────────
st.set_page_config(page_title="한진철관 품질기술팀 QR 시스템", layout="wide")

# ── Supabase 설정 ─────────────────────────────────────────────────
# Secrets가 없을 경우를 대비한 안전장치
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    BUCKET = "cert-images"
except Exception:
    st.error("⚠️ Streamlit Secrets에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
    st.stop()

def upload_to_supabase(png_bytes: bytes, img_key: str) -> tuple[bool, str]:
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{img_key}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/png",
        "x-upsert": "true",
    }
    try:
        res = requests.post(url, headers=headers, data=png_bytes, timeout=30)
        if res.status_code in (200, 201):
            return True, ""
        else:
            return False, f"상태코드: {res.status_code} / {res.text}"
    except Exception as e:
        return False, str(e)

def get_public_url(img_key: str) -> str:
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{img_key}"

def make_qr_png(url: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def calc_qr_rect(page_width, page_height, size, position, margin=5, custom_x=0, custom_y=0):
    if position == "bottom-right":
        x0, y0 = page_width - size - margin, page_height - size - margin
    elif position == "bottom-left":
        x0, y0 = margin, page_height - size - margin
    elif position == "top-right":
        x0, y0 = page_width - size - margin, margin
    elif position == "top-left":
        x0, y0 = margin, margin
    else:  # custom
        x0, y0 = custom_x, custom_y
    return fitz.Rect(x0, y0, x0 + size, y0 + size)

# ── 메인 UI ──────────────────────────────────────────────────────
st.title("🛡️ 검사증명서 QR 자동 삽입 도구")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ 설정")
    pos_mode = st.radio("위치 설정 모드", ["기본 위치 선택", "좌표 직접 입력"])
    
    if pos_mode == "기본 위치 선택":
        qr_position = st.selectbox(
            "QR 위치",
            ["bottom-right", "bottom-left", "top-right", "top-left"],
            format_func=lambda x: {"bottom-right":"우하단","bottom-left":"좌하단","top-right":"우상단","top-left":"좌상단"}[x]
        )
        c_x, c_y = 0, 0
    else:
        qr_position = "custom"
        c_x = st.number_input("X 좌표 (가로)", value=500, step=5)
        c_y = st.number_input("Y 좌표 (세로)", value=750, step=5)

    qr_size = st.slider("QR 크기 (pt)", 40, 150, 55)
    dpi = st.slider("이미지 해상도 (DPI)", 72, 300, 300)
    
    st.markdown("---")
    st.header("📂 로컬 저장 (PC 실행 전용)")
    auto_save = st.checkbox("처리 후 지정 폴더에 자동 저장")
    save_path = st.text_input("저장 경로", value=os.getcwd())

# ── 파일 업로드 및 처리 ───────────────────────────────────────────
uploaded_file = st.file_uploader("검사증명서 PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    # PDF 읽기
    pdf_bytes = uploaded_file.read()
    
    # 미리보기용 섹션
    st.subheader("🔍 위치 미리보기")
    doc_preview = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc_preview[0]
    
    # 미리보기용 가상 QR 배치
    rect = calc_qr_rect(page.rect.width, page.rect.height, qr_size, qr_position, custom_x=c_x, custom_y=c_y)
    qr_preview_bytes = make_qr_png("https://preview.url")
    page.insert_image(rect, stream=qr_preview_bytes)
    
    # 화면 표시
    pix = page.get_pixmap(dpi=100)
    st.image(pix.tobytes("png"), caption="첫 페이지 QR 배치 예시", use_container_width=True)
    doc_preview.close()

    if st.button("🚀 모든 페이지에 QR 삽입 실행"):
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        progress_bar = st.progress(0)
        status_text = st.empty()
        total = len(doc)
        fail_count = 0

        for i in range(total):
            page = doc[i]
            status_text.text(f"처리 중... {i + 1} / {total} 페이지")

            # 1. 이미지화 및 고유 키 생성
            pix = page.get_pixmap(dpi=dpi)
            png_data = pix.tobytes("png")
            img_key = hashlib.md5(f"{uploaded_file.name}_{i}".encode()).hexdigest()[:16] + ".png"

            # 2. Supabase 업로드
            success, err_msg = upload_to_supabase(png_data, img_key)
            if not success:
                st.error(f"❌ {i+1}페이지 업로드 실패: {err_msg}")
                fail_count += 1
                continue

            # 3. 실제 QR 생성 및 삽입
            qr_url = get_public_url(img_key)
            qr_final_png = make_qr_png(qr_url)
            qr_rect = calc_qr_rect(page.rect.width, page.rect.height, qr_size, qr_position, custom_x=c_x, custom_y=c_y)
            page.insert_image(qr_rect, stream=qr_final_png, overlay=True)

            progress_bar.progress((i + 1) / total)

        # 결과물 저장
        final_pdf_bytes = doc.write()
        doc.close()

        if fail_count == 0:
            st.success("✅ 모든 작업 완료!")
            st.download_button("📥 QR 완료 PDF 다운로드", data=final_pdf_bytes, file_name=f"QR_{uploaded_file.name}", mime="application/pdf")
            
            if auto_save:
                try:
                    if not os.path.exists(save_path): os.makedirs(save_path)
                    f_path = os.path.join(save_path, f"QR_{uploaded_file.name}")
                    with open(f_path, "wb") as f: f.write(final_pdf_bytes)
                    st.info(f"📂 로컬 저장 완료: {f_path}")
                except Exception as e:
                    st.error(f"로컬 저장 중 오류: {e}")
        else:
            st.warning(f"⚠️ {fail_count}개 페이지 처리 중 오류 발생")

st.markdown("---")
st.caption("품질기술팀 내부 업무용 | PyMuPDF & Streamlit")
