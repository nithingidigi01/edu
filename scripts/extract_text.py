# scripts/extract_text.py

import os
from pdfminer.high_level import extract_text
from concurrent.futures import ThreadPoolExecutor

# -----------------------------
# CONFIG
# -----------------------------
INPUT_DIR = "raw_ncert"
OUTPUT_DIR = "processed_text"
MAX_WORKERS = 6


# -----------------------------
# EXTRACT SINGLE PDF
# -----------------------------
def process_pdf(pdf_path):
    try:
        # extract text
        text = extract_text(pdf_path)

        if not text or len(text.strip()) < 50:
            print(f"⚠️ Weak text: {pdf_path}")
            return

        # -----------------------------
        # EXTRACT STRUCTURE FROM PATH
        # raw_ncert/class6/subject/chapter1.pdf
        # -----------------------------
        parts = pdf_path.split(os.sep)

        try:
            class_name = parts[1]     # class6
            subject = parts[2]        # geography
            file_name = parts[3]      # chapter1.pdf
        except:
            print(f"❌ Invalid path structure: {pdf_path}")
            return

        chapter_name = file_name.replace(".pdf", "")

        # -----------------------------
        # CREATE OUTPUT STRUCTURE
        # -----------------------------
        out_dir = os.path.join(OUTPUT_DIR, class_name, subject)
        os.makedirs(out_dir, exist_ok=True)

        out_path = os.path.join(out_dir, f"{chapter_name}.txt")

        # -----------------------------
        # SAVE
        # -----------------------------
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"📄 {class_name}/{subject}/{chapter_name}")

    except Exception as e:
        print(f"❌ Failed: {pdf_path} | {e}")


# -----------------------------
# COLLECT ALL PDFs
# -----------------------------
def collect_pdfs():
    pdf_files = []

    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))

    return pdf_files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 Starting structured extraction...")

    pdf_files = collect_pdfs()

    print(f"📚 Total PDFs: {len(pdf_files)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_pdf, pdf_files)

    print("🔥 EXTRACTION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
