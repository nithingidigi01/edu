# scripts/advanced_engine.py

import sys
import os
import json
import random
from concurrent.futures import ThreadPoolExecutor

# FIX IMPORT PATH (CI SAFE)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = "data/ncert"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)

# LIMITS (CRITICAL FOR SPEED)
MAX_FACTS = 20
MAX_AR = 40
MAX_MULTI = 25
MAX_ELIM = 40


# -----------------------------
# FAST JSON WRITE
# -----------------------------
def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


# -----------------------------
# ASSERTION-REASON (CONTROLLED)
# -----------------------------
def assertion_reason(facts):

    questions = []

    facts = facts[:MAX_FACTS]

    count = 0

    for i in range(len(facts)):
        for j in range(len(facts)):

            if i == j:
                continue

            A = facts[i]
            R = facts[j]

            questions.append({
                "type": "assertion_reason",
                "question": f"Assertion (A): {A}\nReason (R): {R}",
                "options": [
                    "Both A and R are true and R explains A",
                    "Both A and R are true but R does not explain A",
                    "A is true but R is false",
                    "A is false but R is true"
                ],
                "answer": 1,
                "explanation": A
            })

            count += 1
            if count >= MAX_AR:
                return questions

    return questions


# -----------------------------
# MULTI-STATEMENT (CONTROLLED)
# -----------------------------
def multi_statement(facts):

    questions = []

    facts = facts[:MAX_FACTS]

    if len(facts) < 4:
        return questions

    for i in range(len(facts) - 3):

        stmts = facts[i:i+4]

        questions.append({
            "type": "multi_statement",
            "question": "Consider the following statements:\n" +
                        "\n".join([f"{idx+1}. {s}" for idx, s in enumerate(stmts)]) +
                        "\nWhich are correct?",
            "options": [
                "1 and 2",
                "2 and 3",
                "1, 2 and 3",
                "All of the above"
            ],
            "answer": 3,
            "explanation": stmts[0]
        })

        if len(questions) >= MAX_MULTI:
            break

    return questions


# -----------------------------
# ELIMINATION (CONTROLLED)
# -----------------------------
def elimination(facts):

    questions = []

    facts = facts[:MAX_FACTS]

    for fact in facts:

        if len(facts) < 2:
            continue

        wrong = random.sample(facts, min(3, len(facts)))

        options = [fact] + wrong

        questions.append({
            "type": "elimination",
            "question": "Which of the following is most appropriate?",
            "options": options,
            "answer": 0,
            "explanation": fact
        })

        if len(questions) >= MAX_ELIM:
            break

    return questions


# -----------------------------
# PROCESS FILE
# -----------------------------
def process_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🚀 SKIP if already processed
        if "advanced_mcqs" in data and len(data["advanced_mcqs"]) > 0:
            return

        facts = data.get("facts", [])

        if not facts:
            return

        adv = []

        adv.extend(assertion_reason(facts))
        adv.extend(multi_statement(facts))
        adv.extend(elimination(facts))

        data["advanced_mcqs"] = adv

        write_json(path, data)

        print(f"🔥 {path} ({len(adv)} advanced)")

    except Exception as e:
        print(f"❌ {path} | {e}")


# -----------------------------
# COLLECT FILES (FAST)
# -----------------------------
def collect():

    files = []

    for root, _, fs in os.walk(BASE_DIR):
        for f in fs:
            if f.endswith(".json"):
                files.append(os.path.join(root, f))

    return files


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 ADVANCED ENGINE START")

    files = collect()

    print(f"📚 Topics: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        ex.map(process_file, files)

    print("🔥 ADVANCED ENGINE COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
