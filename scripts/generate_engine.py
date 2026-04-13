# scripts/generate_engine.py

import os
import json
import itertools
from concurrent.futures import ThreadPoolExecutor

from scripts.ai_engine import extract_facts

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = "data/ncert"
MAX_WORKERS = 4


# -----------------------------
# GENERATE OPTIONS
# -----------------------------
def build_options(correct, others):
    options = [correct] + others[:3]
    return options


# -----------------------------
# QUESTION PATTERNS
# -----------------------------
def generate_patterns(fact, distractors):

    patterns = []

    # 1. Direct
    patterns.append({
        "type": "direct",
        "question": "Which of the following statements is correct?",
        "options": [fact] + distractors,
        "answer": 0,
        "explanation": fact
    })

    # 2. Negative
    patterns.append({
        "type": "negative",
        "question": "Which of the following statements is NOT correct?",
        "options": distractors + [fact],
        "answer": len(distractors),
        "explanation": fact
    })

    # 3. Statement type
    patterns.append({
        "type": "statement",
        "question": f"Consider the following statement:\n{fact}\nWhich is correct?",
        "options": ["Correct", "Incorrect"],
        "answer": 0,
        "explanation": fact
    })

    return patterns


# -----------------------------
# GENERATE MCQs
# -----------------------------
def generate_mcqs(facts):

    mcqs = []

    for i, fact in enumerate(facts):

        others = [f for j, f in enumerate(facts) if j != i]

        combos = list(itertools.combinations(others, min(3, len(others))))

        for combo in combos:

            distractors = list(combo)

            patterns = generate_patterns(fact, distractors)

            mcqs.extend(patterns)

    return mcqs


# -----------------------------
# PROCESS ONE FILE
# -----------------------------
def process_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        content = data.get("content", "")

        if not content:
            return

        # -----------------------------
        # FACT EXTRACTION
        # -----------------------------
        facts = extract_facts(content)

        if not facts:
            return

        # -----------------------------
        # GENERATE MCQs
        # -----------------------------
        mcqs = generate_mcqs(facts)

        # -----------------------------
        # UPDATE JSON
        # -----------------------------
        data["facts"] = facts
        data["mcqs"] = mcqs

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        print(f"✅ MCQs: {path}")

    except Exception as e:
        print(f"❌ Failed: {path} | {e}")


# -----------------------------
# COLLECT FILES
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

    print("🚀 Generating MCQs...")

    files = collect_files()

    print(f"📚 Total topics: {len(files)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_file, files)

    print("🔥 MCQ GENERATION COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
