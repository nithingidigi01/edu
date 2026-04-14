# scripts/ai_engine.py

import threading
from transformers import pipeline

_model = None
_lock = threading.Lock()

def get_model():
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                _model = pipeline(
                    "text-generation",   # ✅ FIXED
                    model="google/flan-t5-small",
                    device=-1
                )
    return _model


def extract_facts(text):

    if not text:
        return []

    model = get_model()

    text = text[:1200]

    prompt = f"Extract key facts:\n{text}"

    try:
        out = model(prompt, max_length=200)[0]["generated_text"]

        facts = []
        seen = set()

        for line in out.split("\n"):
            line = line.strip()

            if len(line) > 20 and line not in seen:
                facts.append(line)
                seen.add(line)

        return facts

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return []
