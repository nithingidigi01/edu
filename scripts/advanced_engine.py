# scripts/advanced_engine.py

import os
import json
import random
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = "data/ncert"
MAX_WORKERS = 4


# -----------------------------
# ASSERTION-REASON
# -----------------------------
def assertion_reason(facts):

    questions = []

    for i in range(len(facts)):
        for j in range(len(facts)):

            if i == j:
                continue

            A = facts[i]
            R = facts[j]

            questions.append({
                "type": "assertion_reason",
                "question": f"Assertion (A): {A}\nReason (R): {R}\nSelect the correct answer:",
                "options": [
                    "Both A and R are true and R explains A",
                    "Both A and R are true but R does not explain A",
                    "A is true but R is false",
                    "A is false but R is true"
                ],
                "answer": 1,
                "explanation": A
            })

    return questions


# -----------------------------
# MULTI-STATEMENT
# -----------------------------
def multi_statement(facts):

    questions = []

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

    return questions


# -----------------------------
# ELIMINATION TYPE
# -----------------------------
def elimination(facts):

    questions = []

    for fact in facts:

        wrong = random.sample(facts, min(3, len(facts)))

        options = [fact] + wrong

        questions.append({
            "type": "elimination",
            "question": "Which of the following is most appropriate?",
            "options": options,
            "answer": 0,
            "explanation": fact
        })

    return questions


# -----------------------------
# PROCESS FILE
# -----------------------------
def process_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        facts = data.get("facts", [])

        if not facts:
            return

        adv = []

        adv.extend(assertion_reason(facts))
        adv.extend(multi_statement(facts))
        adv.extend(elimination(facts))

        data["advanced_mcqs"] = adv

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        print(f"🔥 Advanced: {path}")

    except Exception as e:
        print(f"❌ Failed: {path} | {e}")


# -----------------------------
# COLLECT FILES
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

    print("🚀 Advanced engine starting...")

    files = collect()

    print(f"📚 Topics: {len(files)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        ex.map(process_file, files)

    print("🔥 ADVANCED ENGINE COMPLETE")


if __name__ == "__main__":
    main()
