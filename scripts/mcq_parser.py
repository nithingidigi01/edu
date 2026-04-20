# scripts/mcq_parser.py

import re


# -----------------------------
# PARSE MCQ BLOCK
# -----------------------------
def parse_mcq_block(text):

    mcqs = []

    if not text:
        return mcqs

    # split by question numbers
    parts = re.split(r'\n?\d+\.', text)

    for part in parts:

        lines = [l.strip() for l in part.split("\n") if l.strip()]

        if len(lines) < 5:
            continue

        try:
            question = lines[0]

            options = []
            answer = None
            explanation = ""

            # extract options
            for line in lines[1:5]:
                if line.startswith(("A", "B", "C", "D")):
                    options.append(line[2:].strip())

            # extract answer
            for line in lines:
                if "answer" in line.lower():
                    ans = re.findall(r'[ABCD]', line.upper())
                    if ans:
                        answer = ord(ans[0]) - ord('A')

            # extract explanation
            for line in lines:
                if "explanation" in line.lower():
                    explanation = line.split(":", 1)[-1].strip()

            if len(options) == 4:
                mcqs.append({
                    "question": question,
                    "options": options,
                    "answer": answer if answer is not None else 0,
                    "explanation": explanation
                })

        except:
            continue

    return mcqs
