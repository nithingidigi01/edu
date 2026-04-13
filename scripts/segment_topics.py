import os, json
from utils import clean_text, split_chapters, split_topics

INPUT = "processed_text"
BASE = "data/ncert/class6"

for file in os.listdir(INPUT):
    if not file.endswith(".txt"):
        continue

    subject = "unknown"
    if "geo" in file: subject = "geography"
    elif "hist" in file: subject = "history"
    elif "sci" in file: subject = "science"
    elif "pol" in file: subject = "polity"

    text = clean_text(open(f"{INPUT}/{file}", encoding="utf-8").read())

    chapters = split_chapters(text)

    for ci, ch in enumerate(chapters, 1):
        topics = split_topics(ch)

        for ti, topic in enumerate(topics, 1):
            if len(topic) < 300:
                continue

            out = f"{BASE}/{subject}/chapter{ci}"
            os.makedirs(out, exist_ok=True)

            json.dump({
                "class": 6,
                "subject": subject,
                "chapter": ci,
                "topic": ti,
                "content": topic
            }, open(f"{out}/topic{ti}.json", "w"))
