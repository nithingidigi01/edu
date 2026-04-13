# scripts/segment_topics.py

import os
import json
import re

INPUT_DIR = "processed_text"
OUTPUT_DIR = "data/ncert/class6"

def split_chapters(text):
    return re.split(r"Chapter\s+\d+", text)

def split_topics(chapter_text):
    return re.split(r"\n[A-Z][A-Za-z\s]+\n", chapter_text)

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".txt"):
        continue

    with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
        text = f.read()

    chapters = split_chapters(text)

    for i, ch in enumerate(chapters):
        topics = split_topics(ch)

        for j, topic in enumerate(topics):
            if len(topic.strip()) < 200:
                continue

            out_dir = os.path.join(OUTPUT_DIR, f"chapter{i+1}")
            os.makedirs(out_dir, exist_ok=True)

            data = {
                "class": 6,
                "chapter": i + 1,
                "topic": j + 1,
                "content": topic.strip()
            }

            with open(os.path.join(out_dir, f"topic{j+1}.json"), "w", encoding="utf-8") as out:
                json.dump(data, out, ensure_ascii=False)

print("Segmentation complete")
