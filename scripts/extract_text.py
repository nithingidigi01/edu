# scripts/extract_text.py

import sys
import os
from concurrent.futures import ThreadPoolExecutor
from pdfminer.high_level import extract_text

# -----------------------------
# CONFIG
# -----------------------------
INPUT_DIR = "raw_ncert"
OUTPUT_DIR = "processed_text"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)


# -----------------------------
# FAST PATH PARSER
# -----------------------------
def parse_path(path):
    parts = path.replace("\\", "/").split("/")

    # expected: raw_ncert/class6/subject/chapter1.pdf
    try:
        return parts[-3], parts[-2], parts[-1]
    except:
        return None, None, None


# -----------------------------
# FAST WRITE
# -----------------------------
def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# -----------------------------
# PROCESS ONE PDF
# -----------------------------
def process_pdf(pdf_path):

    try:
        class_name, subject, file_name = parse_path(pdf_path)

        if not class_name:
            return

        chapter_name = file_name[:-4]  # remove .pdf

        out_dir = os.path.join(OUTPUT_DIR, class_name, subject)
        os.makedirs(out_dir, exist_ok=True)

        out_path = os.path.join(out_dir, f"{chapter_name}.txt")

        # 🚀 SKIP if already processed
        if os.path.exists(out_path):
            return

        # -----------------------------
        # EXTRACT TEXT
        # -----------------------------
        text = extract_text(pdf_path)

        if not text or len(text.strip()) < 50:
            print(f"⚠️ Weak: {pdf_path}")
            return

        # -----------------------------
        # SAVE
        # -----------------------------
        write_text(out_path, text)

        print(f"📄 {class_name}/{subject}/{chapter_name}")

    except Exception as e:
        print(f"❌ {pdf_path} | {e}")


# -----------------------------
# COLLECT FILES (FAST)
# -----------------------------
def collect_pdfs():

    files = []

    for root, _, filenames in os.walk(INPUT_DIR):
        for f in filenames:
            if f.endswith(".pdf"):
                files.append(os.path.join(root, f))

    return files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 EXTRACTION START")

    files = collect_pdfs()

    print(f"📚 PDFs: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    # 🚀 PARALLEL EXECUTION
    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        executor.map(process_pdf, files)

    print("🔥 EXTRACTION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
