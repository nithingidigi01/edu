# scripts/extract_text.py

import os
import fitz
import re
from concurrent.futures import ThreadPoolExecutor

INPUT_DIR = "raw_ncert"
OUTPUT_DIR = "processed_text"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)

def clean(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse(path):
    p = path.replace("\\", "/").split("/")
    return p[-3], p[-2], p[-1]

def extract(pdf):
    doc = fitz.open(pdf)
    return " ".join([page.get_text() for page in doc])

def process(pdf):
    try:
        cls, sub, name = parse(pdf)
        out_dir = os.path.join(OUTPUT_DIR, cls, sub)
        os.makedirs(out_dir, exist_ok=True)

        out = os.path.join(out_dir, name.replace(".pdf", ".txt"))

        if os.path.exists(out):
            return

        text = extract(pdf)
        text = clean(text)

        if len(text) < 200:
            print(f"❌ Bad: {pdf}")
            return

        with open(out, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"✅ {cls}/{sub}/{name}")

    except Exception as e:
        print(f"❌ {pdf} | {e}")

def main():
    files = []
    for r,_,fs in os.walk(INPUT_DIR):
        for f in fs:
            if f.endswith(".pdf"):
                files.append(os.path.join(r,f))

    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        ex.map(process, files)

if __name__ == "__main__":
    main()
