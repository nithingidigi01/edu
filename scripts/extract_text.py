# scripts/extract_text.py

import os
import fitz  # PyMuPDF
import re
from concurrent.futures import ThreadPoolExecutor

# ✅ USE YOUR MANUAL NCERT FOLDER
INPUT_DIR = "ncert"

# OUTPUT
OUTPUT_DIR = "processed_text"

# PERFORMANCE
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -----------------------------
# PARSE PATH (IMPORTANT FIX)
# -----------------------------
def parse(path):
    parts = path.replace("\\", "/").split("/")

    try:
        cls_raw = parts[-3]      # "6th"
        subject = parts[-2]      # "mathematics"
        file_name = parts[-1]    # "fegp101.pdf"

        # convert "6th" → "class6"
        cls_num = ''.join(filter(str.isdigit, cls_raw))
        class_name = f"class{cls_num}"

        return class_name, subject, file_name

    except:
        return None, None, None


# -----------------------------
# EXTRACT TEXT FROM PDF
# -----------------------------
def extract(pdf_path):
    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            text += page.get_text()

    except Exception as e:
        print(f"❌ Extract fail: {pdf_path} | {e}")

    return text


# -----------------------------
# PROCESS SINGLE PDF
# -----------------------------
def process(pdf_path):

    try:
        class_name, subject, file_name = parse(pdf_path)

        if not class_name:
            return

        # OUTPUT PATH
        out_dir = os.path.join(OUTPUT_DIR, class_name, subject)
        os.makedirs(out_dir, exist_ok=True)

        chapter_name = file_name.replace(".pdf", "")
        out_path = os.path.join(out_dir, f"{chapter_name}.txt")

        # SKIP IF EXISTS
        if os.path.exists(out_path):
            return

        # EXTRACT
        text = extract(pdf_path)
        text = clean(text)

        if len(text) < 200:
            print(f"⚠️ Weak text: {pdf_path}")
            return

        # SAVE
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ {class_name}/{subject}/{chapter_name}")

    except Exception as e:
        print(f"❌ Error: {pdf_path} | {e}")


# -----------------------------
# COLLECT ALL PDFs
# -----------------------------
def collect():
    files = []

    for root, _, fs in os.walk(INPUT_DIR):
        for f in fs:
            if f.endswith(".pdf"):
                files.append(os.path.join(root, f))

    return files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 EXTRACTION START")

    files = collect()

    print(f"📚 PDFs Found: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        ex.map(process, files)

    print("🔥 EXTRACTION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
