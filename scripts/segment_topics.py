# scripts/segment_topics.py

import os
import json
from concurrent.futures import ThreadPoolExecutor

from scripts.utils import clean_text, split_chapters, split_topics

# -----------------------------
# CONFIG
# -----------------------------
INPUT_DIR = "processed_text"
OUTPUT_DIR = "data/ncert"
MAX_WORKERS = 6


# -----------------------------
# PROCESS ONE FILE
# -----------------------------
def process_file(txt_path):

    try:
        # -----------------------------
        # EXTRACT STRUCTURE
        # processed_text/class6/subject/chapter1.txt
        # -----------------------------
        parts = txt_path.split(os.sep)

        class_name = parts[1]     # class6
        subject = parts[2]        # geography
        file_name = parts[3]      # chapter1.txt

        chapter_name = file_name.replace(".txt", "")

        # -----------------------------
        # READ TEXT
        # -----------------------------
        with open(txt_path, "r", encoding="utf-8") as f:
            text = clean_text(f.read())

        if len(text) < 200:
            print(f"⚠️ Skipping weak file: {txt_path}")
            return

        # -----------------------------
        # SPLIT CHAPTERS (safety)
        # -----------------------------
        chapters = split_chapters(text)

        # if split fails → fallback
        if not chapters:
            chapters = [text]

        # -----------------------------
        # PROCESS CHAPTERS
        # -----------------------------
        for ci, ch in enumerate(chapters, start=1):

            topics = split_topics(ch)

            if not topics:
                topics = [ch]

            # -----------------------------
            # SAVE TOPICS
            # -----------------------------
            for ti, topic in enumerate(topics, start=1):

                topic = clean_text(topic)

                if len(topic) < 150:
                    continue

                out_dir = os.path.join(
                    OUTPUT_DIR,
                    class_name,
                    subject,
                    f"chapter{ci}"
                )

                os.makedirs(out_dir, exist_ok=True)

                out_path = os.path.join(out_dir, f"topic{ti}.json")

                data = {
                    "class": class_name,
                    "subject": subject,
                    "chapter": ci,
                    "topic": ti,
                    "content": topic
                }

                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(data, out, ensure_ascii=False)

        print(f"✅ Processed: {class_name}/{subject}/{chapter_name}")

    except Exception as e:
        print(f"❌ Failed: {txt_path} | {e}")


# -----------------------------
# COLLECT ALL TXT FILES
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

    print("🚀 Starting topic segmentation...")

    files = collect_files()

    print(f"📚 Total chapters: {len(files)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_file, files)

    print("🔥 SEGMENTATION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
