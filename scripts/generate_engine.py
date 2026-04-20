# scripts/generate_engine.py

import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor

# -----------------------------
# FIX IMPORT PATH (CI SAFE)
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.ai_engine import generate_mcqs_from_topic


# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = "data/ncert"
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)


# -----------------------------
# FAST JSON WRITE
# -----------------------------
def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False))


# -----------------------------
# PROCESS ONE FILE
# -----------------------------
def process_file(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🚀 SKIP if already processed
        if "mcqs" in data and len(data["mcqs"]) > 0:
            return

        content = data.get("content", "")

        if not content:
            return

        # -----------------------------
        # GENERATE MCQs FROM TOPIC
        # -----------------------------
        mcqs = generate_mcqs_from_topic(content)

        if not mcqs:
            return

        # -----------------------------
        # UPDATE DATA
        # -----------------------------
        data["mcqs"] = mcqs

        write_json(path, data)

        print(f"✅ MCQs Generated: {path}")

    except Exception as e:
        print(f"❌ Failed: {path} | {e}")


# -----------------------------
# COLLECT ALL JSON FILES
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

    print(f"📚 Topics Found: {len(files)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        executor.map(process_file, files)

    print("🔥 MCQ ENGINE COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
