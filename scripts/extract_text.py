import os
from pdfminer.high_level import extract_text
from concurrent.futures import ThreadPoolExecutor

def process(path):
    text = extract_text(path)
    out = "processed_text/" + os.path.basename(path) + ".txt"

    os.makedirs("processed_text", exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(text)

    print("📄", path)

paths = []
for root, _, files in os.walk("raw_ncert"):
    for f in files:
        if f.endswith(".pdf"):
            paths.append(os.path.join(root, f))

with ThreadPoolExecutor(max_workers=6) as ex:
    ex.map(process, paths)
