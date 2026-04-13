# scripts/extract_text.py

from pdfminer.high_level import extract_text
import os

INPUT_DIR = "raw_ncert"
OUTPUT_DIR = "processed_text"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.endswith(".pdf"):
        path = os.path.join(INPUT_DIR, file)
        text = extract_text(path)

        out_file = file.replace(".pdf", ".txt")
        with open(os.path.join(OUTPUT_DIR, out_file), "w", encoding="utf-8") as f:
            f.write(text)

print("Text extraction complete")
