# scripts/segment_topics.py

import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

# FIX IMPORT PATH (CI SAFE)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.utils import clean_text, split_chapters, split_topics

# -----------------------------
# CONFIG
# -----------------------------
INPUT_DIR = "processed_text"
OUTPUT_DIR = "data/ncert"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)  # dynamic scaling


# -----------------------------
# FAST PATH PARSER (NO SPLIT COST)
# -----------------------------
def parse_path(path):
    parts = path.replace("\\", "/").split("/")

    # expected: processed_text/class6/subject/chapter1.txt
    try:
        return parts[-3], parts[-2], parts[-1]
    except:
        return None, None, None


# -----------------------------
# WRITE JSON (FAST)
# -----------------------------
def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


# -----------------------------
# PROCESS ONE FILE
# -----------------------------
def process_file(txt_path):

    try:
        class_name, subject, file_name = parse_path(txt_path)

        if not class_name:
            return

        chapter_name = file_name[:-4]  # remove .txt

        # FAST READ
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = clean_text(text)

        if len(text) < 200:
            return

        # -----------------------------
        # SPLIT CHAPTERS
        # -----------------------------
        chapters = split_chapters(text) or [text]

        base_dir = os.path.join(OUTPUT_DIR, class_name, subject)

        # -----------------------------
        # PROCESS CHAPTERS
        # -----------------------------
        for ci, ch in enumerate(chapters, 1):

            topics = split_topics(ch) or [ch]

            out_dir = os.path.join(base_dir, f"chapter{ci}")
            os.makedirs(out_dir, exist_ok=True)

            # -----------------------------
            # PROCESS TOPICS
            # -----------------------------
            for ti, topic in enumerate(topics, 1):

                topic = clean_text(topic)

                if len(topic) < 150:
                    continue

                out_path = os.path.join(out_dir, f"topic{ti}.json")

                # SKIP if already exists (huge speed boost in reruns)
                if os.path.exists(out_path):
                    continue

                data = {
                    "class": class_name,
                    "subject": subject,
                    "chapter": ci,
                    "topic": ti,
                    "content": topic
                }

                write_json(out_path, data)

        print(f"✅ {class_name}/{subject}/{chapter_name}")

    except Exception as e:
        print(f"❌ {txt_path} | {e}")


# -----------------------------
# COLLECT FILES (FAST)
# -----------------------------
def collect_files():
    files = []

    for root, _, filenames in os.walk(INPUT_DIR):
        for f in filenames:
            if f.endswith(".txt"):
                files.append(os.path.join(root, f))

    return files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 SEGMENTATION START")

    files = collect_files()

    print(f"📚 Total files: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        executor.map(process_file, files)

    print("🔥 SEGMENTATION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
