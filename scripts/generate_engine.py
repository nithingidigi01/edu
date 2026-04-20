# scripts/generate_engine.py

import sys
import os
import json
import itertools
from concurrent.futures import ThreadPoolExecutor

# FIX IMPORT PATH (CI SAFE)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.ai_engine import extract_facts

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = "data/ncert"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)

# LIMITS (VERY IMPORTANT FOR PERFORMANCE)
MAX_FACTS = 25          # limit facts per topic
MAX_COMBINATIONS = 40   # limit combinations per fact


# -----------------------------
# FAST JSON WRITE
# -----------------------------
def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


# -----------------------------
# GENERATE PATTERNS (FAST)
# -----------------------------
def generate_patterns(fact, distractors):

    return [
        {
            "type": "direct",
            "question": "Which of the following statements is correct?",
            "options": [fact] + distractors,
            "answer": 0,
            "explanation": fact
        },
        {
            "type": "negative",
            "question": "Which of the following statements is NOT correct?",
            "options": distractors + [fact],
            "answer": len(distractors),
            "explanation": fact
        },
        {
            "type": "statement",
            "question": f"Consider the following statement:\n{fact}\nWhich is correct?",
            "options": ["Correct", "Incorrect"],
            "answer": 0,
            "explanation": fact
        }
    ]


# -----------------------------
# GENERATE MCQs (CONTROLLED)
# -----------------------------
def generate_mcqs(facts):

    mcqs = []

    # LIMIT facts (critical for speed)
    facts = facts[:MAX_FACTS]

    for i, fact in enumerate(facts):

        others = [f for j, f in enumerate(facts) if j != i]

        if not others:
            continue

        # LIMIT combinations (prevents explosion)
        combos = itertools.islice(
            itertools.combinations(others, min(3, len(others))),
            MAX_COMBINATIONS
        )

        for combo in combos:
            mcqs.extend(generate_patterns(fact, list(combo)))

    return mcqs


# -----------------------------
# PROCESS ONE FILE
# -----------------------------
def process_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # SKIP if already processed (huge speed boost)
        if "mcqs" in data and len(data["mcqs"]) > 0:
            return

        content = data.get("content", "")

        if not content:
            return

        # -----------------------------
        # FACT EXTRACTION (CACHED)
        # -----------------------------
        facts = data.get("facts")

        if not facts:
            facts = extract_facts(content)
            facts = list(set(facts))  # dedupe

        if not facts:
            return

        # -----------------------------
        # MCQ GENERATION
        # -----------------------------
        mcqs = generate_mcqs(facts)

        # -----------------------------
        # UPDATE DATA
        # -----------------------------
        data["facts"] = facts
        data["mcqs"] = mcqs

        write_json(path, data)

        print(f"✅ {path} ({len(mcqs)} MCQs)")

    except Exception as e:
        print(f"❌ {path} | {e}")


# -----------------------------
# COLLECT FILES (FAST)
# -----------------------------
def collect_files():

    files = []

    for root, _, filenames in os.walk(BASE_DIR):
        for f in filenames:
            if f.endswith(".json"):
                files.append(os.path.join(root, f))

    return files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 MCQ ENGINE START")

    files = collect_files()

    print(f"📚 Topics: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        executor.map(process_file, files)

    print("🔥 MCQ ENGINE COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
