# scripts/segment_topics.py

import os
import json
import re

INPUT_DIR = "processed_text"
BASE_OUTPUT_DIR = "data/ncert/class6"

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -----------------------------
# DETECT CHAPTERS
# NCERT pattern: "Chapter 1", "CHAPTER 1"
# -----------------------------
def split_chapters(text):
    chapters = re.split(r'(?:CHAPTER|Chapter)\s+\d+', text)

    # remove empty
    return [c.strip() for c in chapters if len(c.strip()) > 500]


# -----------------------------
# DETECT TOPICS (SMART HEADING DETECTION)
# NCERT headings are usually:
# - Title Case
# - Short lines
# -----------------------------
def split_topics(chapter_text):
    lines = chapter_text.split("\n")

    topics = []
    current_topic = []

    for line in lines:
        line_clean = line.strip()

        # detect heading
        if (
            len(line_clean) > 3 and
            len(line_clean) < 80 and
            line_clean == line_clean.title() and
            not line_clean.endswith(".")
        ):
            # save previous topic
            if current_topic:
                topics.append(" ".join(current_topic))
                current_topic = []

        current_topic.append(line_clean)

    if current_topic:
        topics.append(" ".join(current_topic))

    return topics


# -----------------------------
# MAIN PROCESS
# -----------------------------
def process_file(file_path, subject_name):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = clean_text(text)

    chapters = split_chapters(text)

    print(f"📘 {subject_name}: {len(chapters)} chapters detected")

    for ci, chapter in enumerate(chapters, start=1):

        topics = split_topics(chapter)

        print(f"  ├─ Chapter {ci}: {len(topics)} topics")

        for ti, topic in enumerate(topics, start=1):

            topic_clean = clean_text(topic)

            if len(topic_clean) < 300:
                continue  # skip weak content

            out_dir = os.path.join(
                BASE_OUTPUT_DIR,
                subject_name,
                f"chapter{ci}"
            )

            os.makedirs(out_dir, exist_ok=True)

            data = {
                "class": 6,
                "subject": subject_name,
                "chapter": ci,
                "topic": ti,
                "content": topic_clean
            }

            file_name = f"topic{ti}.json"
            out_path = os.path.join(out_dir, file_name)

            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False)

    print(f"✅ Done: {subject_name}")


# -----------------------------
# ENTRY POINT
# -----------------------------
def main():

    if not os.path.exists(INPUT_DIR):
        raise Exception("❌ processed_text folder not found. Extraction step failed.")

    files = os.listdir(INPUT_DIR)

    if not files:
        raise Exception("❌ No text files found in processed_text")

    for file in files:
        if not file.endswith(".txt"):
            continue

        file_path = os.path.join(INPUT_DIR, file)

        # subject name from file
        subject_name = file.replace(".txt", "").lower()

        process_file(file_path, subject_name)


if __name__ == "__main__":
    main()
