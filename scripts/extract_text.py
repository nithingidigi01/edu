# scripts/extract_text.py

import os
import fitz  # PyMuPDF
import re

INPUT_DIR = "ncert"
OUTPUT_DIR = "processed_text"

# 🔥 IMPORTANT: reduce workers to avoid crash
MAX_WORKERS = 1


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -----------------------------
# PARSE PATH
# -----------------------------
def parse(path):
    parts = path.replace("\\", "/").split("/")

    try:
        cls_raw = parts[-3]
        subject = parts[-2]
        file_name = parts[-1]

        cls_num = ''.join(filter(str.isdigit, cls_raw))
        class_name = f"class{cls_num}"

        return class_name, subject, file_name

    except:
        return None, None, None


# -----------------------------
# SAFE PDF EXTRACTION
# -----------------------------
def extract(pdf_path):

    text = ""

    try:
        doc = fitz.open(pdf_path)

        for page in doc:
            try:
                text += page.get_text()
            except:
                continue

        doc.close()

    except Exception as e:
        print(f"❌ Failed PDF: {pdf_path} | {e}")

    return text


# -----------------------------
# PROCESS FILE (NO PARALLEL)
# -----------------------------
def process(pdf_path):

    class_name, subject, file_name = parse(pdf_path)

    if not class_name:
        return

    out_dir = os.path.join(OUTPUT_DIR, class_name, subject)
    os.makedirs(out_dir, exist_ok=True)

    chapter_name = file_name.replace(".pdf", "")
    out_path = os.path.join(out_dir, f"{chapter_name}.txt")

    if os.path.exists(out_path):
        return

    text = extract(pdf_path)
    text = clean(text)

    if len(text) < 200:
        print(f"⚠️ Weak: {pdf_path}")
        return

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ {class_name}/{subject}/{chapter_name}")


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 SAFE EXTRACTION START")

    files = []

    for root, _, fs in os.walk(INPUT_DIR):
        for f in fs:
            if f.endswith(".pdf"):
                files.append(os.path.join(root, f))

    print(f"📚 PDFs: {len(files)}")

    for f in files:
        process(f)

    print("🔥 EXTRACTION COMPLETE")


if __name__ == "__main__":
    main()
