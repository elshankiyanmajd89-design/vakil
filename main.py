import streamlit as st
import os
from openai import OpenAI
import fitz
from pdf2image import convert_from_path
import pytesseract

# ================= CONFIG =================
MODEL = "gpt-4o-mini"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
MAX_CHUNKS_DIRECT = 3
MAX_CHUNKS_SUMMARY = 5
SUMMARY_TOKENS = 1200

# فقط برای لوکال (روی سرور Streamlit Cloud حذف می‌شود)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= STREAMLIT =================
st.set_page_config(page_title="مشاور وکیل", layout="centered")
st.title("⚖️ مشاور حقوقی")

# ================= API =================
API_KEY = st.secrets.get("GAPGPT_API_KEY")
if not API_KEY:
    st.error("❌ API Key پیدا نشد (GAPGPT_API_KEY)")
    st.stop()

client = OpenAI(
    base_url="https://api.gapgpt.app/v1",
    api_key=API_KEY
)

# ================= UTILS =================
def extract_text_pdf_bytes(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return " ".join([p.get_text() for p in doc])

def extract_text_scanned_pdf(path):
    images = convert_from_path(path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="fas+eng") + "\n"
    return text

def chunk_text(text):
    words = text.split()
    chunks, buf = [], []
    for w in words:
        buf.append(w)
        if len(buf) >= CHUNK_SIZE:
            chunks.append(" ".join(buf))
            buf = buf[-CHUNK_OVERLAP:]
    if buf:
        chunks.append(" ".join(buf))
    return chunks

def ask_gapgpt(prompt, max_tokens=800):
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional Iranian legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return r.choices[0].message.content
    except Exception as e:
        st.error(f"خطای API: {e}")
        return ""

def load_sources():
    texts = []
    for folder in ["sources", "books"]:
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            try:
                if f.endswith(".txt"):
                    texts.append(open(path, encoding="utf-8").read())
                elif f.endswith(".pdf"):
                    if folder == "books":
                        texts.append(extract_text_pdf_bytes(open(path, "rb").read()))
                    else:
                        texts.append(extract_text_scanned_pdf(path))
            except:
                pass
    return texts

# ================= UI =================
use_local = st.checkbox("استفاده از منابع حقوقی لپ‌تاپ")

uploaded_file = st.file_uploader("PDF (اختیاری)", type=["pdf"])
question = st.text_area("سؤال حقوقی:", placeholder="مثلاً: تصرف عدوانی چیست؟")

col1, col2, col3 = st.columns(3)
btn_answer = col1.button("پاسخ مستقیم")
btn_summary = col2.button("خلاصه‌سازی")
btn_stop = col3.button("Stop")

if "stop" not in st.session_state:
    st.session_state.stop = False

if btn_stop:
    st.session_state.stop = True
    st.warning("⛔ پردازش متوقف شد")
    st.stop()

# ================= پردازش =================
def build_context():
    chunks = []

    if uploaded_file:
        text = extract_text_pdf_bytes(uploaded_file.getvalue())
        if len(text.strip()) < 50:
            tmp = "temp.pdf"
            open(tmp, "wb").write(uploaded_file.getvalue())
            text = extract_text_scanned_pdf(tmp)
            os.remove(tmp)
        chunks += chunk_text(text)

    if use_local:
        for t in load_sources():
            chunks += chunk_text(t)

    return chunks

# ---------- پاسخ مستقیم ----------
if btn_answer and question.strip():
    st.session_state.stop = False
    st.info("در حال پاسخ مستقیم...")

    chunks = build_context()
    if chunks:
        ctx = "\n".join(chunks[:MAX_CHUNKS_DIRECT])
        prompt = f"{ctx}\n\nسؤال: {question}\nپاسخ بده:"
    else:
        prompt = question

    answer = ask_gapgpt(prompt)
    st.subheader("✅ پاسخ")
    st.write(answer)

# ---------- خلاصه‌سازی ----------
if btn_summary and question.strip():
    st.session_state.stop = False
    st.info("در حال خلاصه‌سازی...")

    chunks = build_context()
    chunks = chunks[:MAX_CHUNKS_SUMMARY]

    results = []
    for i, ch in enumerate(chunks):
        if st.session_state.stop:
            break
        st.write(f"پردازش بخش {i+1}/{len(chunks)}")
        p = f"این متن را متناسب با سؤال خلاصه کن:\n{ch}\nسؤال: {question}"
        results.append(ask_gapgpt(p, SUMMARY_TOKENS))

    st.subheader("📌 خلاصه نهایی")
    st.write("\n".join(results))

st.caption("⚠️ جایگزین مشاوره رسمی وکیل نیست")
