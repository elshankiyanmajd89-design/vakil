import streamlit as st
import os
from openai import OpenAI
import fitz
from pdf2image import convert_from_path
import pytesseract

# ---------------- CONFIG ----------------
MODEL = "gpt-4o-mini"
MAX_CONTEXT_TOKENS = 120000  # کمتر از 128k
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 100
MAX_CHUNKS_PER_STAGE = 1
MAX_CHUNKS_DIRECT = 5
SUMMARY_SIZE = 1500

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

API_KEY = st.secrets["general"]["GAPGPT_API_KEY"]
client = OpenAI(base_url="https://api.gapgpt.app/v1", api_key=API_KEY)

# ---------------- UTILS ----------------
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

def extract_text_from_scanned_pdf(file_path):
    images = convert_from_path(file_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang='fas+eng') + "\n"
    return text

def load_local_sources():
    sources = {}
    for folder in ["sources", "books"]:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            try:
                if fname.endswith(".txt"):
                    with open(path, "r", encoding="utf-8") as f:
                        text = f.read()
                elif fname.endswith(".pdf"):
                    if folder == "books":
                        with open(path, "rb") as f:
                            text = extract_text_from_pdf(f)
                    else:
                        text = extract_text_from_scanned_pdf(path)
                else:
                    continue
                sources[f"{folder}/{fname}"] = text
            except Exception as e:
                st.error(f"خطا در پردازش {path}: {e}")
    return sources

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks, current = [], []
    for w in words:
        current.append(w)
        if len(current) >= chunk_size:
            chunks.append(" ".join(current))
            current = current[-overlap:]
    if current:
        chunks.append(" ".join(current))
    return chunks

def ask_gapgpt(prompt, max_tokens=SUMMARY_SIZE):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"مشکل در اتصال به GapGPT API: {e}")
        return ""

def summarize_chunks(chunks, question):
    summaries = []
    for i, chunk in enumerate(chunks[:MAX_CHUNKS_PER_STAGE]):
        if st.session_state.stop_flag:
            st.warning("پردازش توسط کاربر متوقف شد!")
            break
        st.info(f"خلاصه‌سازی chunk {i+1}/{len(chunks[:MAX_CHUNKS_PER_STAGE])}")
        prompt = f"این متن را بر اساس درخواست کاربر خلاصه کن:\n\n{chunk}\n\nسوال: {question}\nخلاصه:"
        summary = ask_gapgpt(prompt)
        summaries.append(summary)
    return summaries

# ---------------- UI ----------------
st.set_page_config(page_title="مشاور وکیل", layout="centered")
st.title("📄 مشاور حقوقی")

# Reset stop flag at the start
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

# ON/OFF منابع محلی
use_local = st.checkbox("استفاده از منابع محلی روی لپ‌تاپ")

# آپلود PDF اختیاری
uploaded_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
question = st.text_area("سوال خود را وارد کنید:", placeholder="مثلاً: پاسخ بده / خلاصه کن")

# دکمه‌ها
col1, col2, col3 = st.columns(3)
with col1:
    direct_api_btn = st.button("پاسخ مستقیم از GapGPT API")
with col2:
    summary_btn = st.button("خلاصه‌سازی")
with col3:
    stop_btn = st.button("Stop")
    if stop_btn:
        st.session_state.stop_flag = True
        st.warning("پردازش متوقف شد!")

# ---------------- بارگذاری منابع ----------------
sources = load_local_sources() if use_local else {}
selected_texts = list(sources.values())

context_chunks = []

# فایل آپلود شده
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    if len(text.strip()) < 50:  # احتمال اسکن
        tmp_path = f"temp_{uploaded_file.name}"
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        text = extract_text_from_scanned_pdf(tmp_path)
        os.remove(tmp_path)
    context_chunks.extend(chunk_text(text))

# منابع محلی
if use_local:
    for t in selected_texts:
        context_chunks.extend(chunk_text(t))

# ---------------- پاسخ مستقیم ----------------
if direct_api_btn and question.strip():
    st.session_state.stop_flag = False  # Reset stop flag
    st.info("در حال پاسخ مستقیم به سوال بدون خلاصه‌سازی...")
    if context_chunks:
        total_chunks = min(len(context_chunks), MAX_CHUNKS_DIRECT)
        combined_text = "\n".join(context_chunks[:total_chunks])
        prompt = f"{combined_text}\n\nسوال: {question}\nجواب بده:"
    else:
        prompt = question  # فقط خود سوال بدون منابع
    answer = ask_gapgpt(prompt)
    st.subheader("📌 پاسخ مستقیم")
    st.write(answer)

# ---------------- خلاصه‌سازی ----------------
if summary_btn and question.strip():
    st.session_state.stop_flag = False  # Reset stop flag
    st.info(f"تعداد نهایی chunks برای پردازش: {len(context_chunks[:MAX_CHUNKS_PER_STAGE])}")
    if context_chunks:
        summaries = summarize_chunks(context_chunks, question)
        final_answer = "\n".join(summaries)
        st.subheader("📌 نتیجه نهایی")
        st.write(final_answer)
    else:
        st.warning("هیچ متنی برای پردازش پیدا نشد!")

st.caption("⚠️ این ابزار جایگزین مشاوره رسمی حقوقی نیست.")
