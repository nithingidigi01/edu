import os, json, itertools
from ai_engine import extract_facts

BASE = "data/ncert/class6"

def generate_mcqs(facts):
    mcqs = []

    for fact in facts:
        others = [f for f in facts if f != fact]

        for combo in itertools.combinations(others, min(3, len(others))):
            options = [fact] + list(combo)

            # ALL patterns
            mcqs.append({
                "question": "Which is correct?",
                "options": options,
                "answer": 0,
                "explanation": fact
            })

            mcqs.append({
                "question": "Which is NOT correct?",
                "options": options,
                "answer": 1,
                "explanation": fact
            })

    return mcqs

for root, _, files in os.walk(BASE):
    for f in files:
        if f.endswith(".json"):
            path = os.path.join(root, f)
            data = json.load(open(path))

            facts = extract_facts(data["content"])
            mcqs = generate_mcqs(facts)

            data["facts"] = facts
            data["mcqs"] = mcqs

            json.dump(data, open(path, "w"))

print("🔥 FULL COVERAGE GENERATED")
