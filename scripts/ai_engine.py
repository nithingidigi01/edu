# scripts/ai_engine.py

import threading
import json
from transformers import pipeline

_model = None
_lock = threading.Lock()


# -----------------------------
# LOAD MODEL
# -----------------------------
def get_model():
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                _model = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-base",
                    device=-1
                )
    return _model


# -----------------------------
# GENERATE STRUCTURED MCQs
# -----------------------------
def generate_mcqs_from_topic(text):

    if not text:
        return []

    model = get_model()

    text = text[:2000]

    prompt = f"""
You are an expert UPSC exam paper setter.

From the topic below, generate multiple high-quality MCQs.

STRICT RULES:
- Output ONLY valid JSON
- No extra text
- Format EXACTLY like this:

[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "answer": 0,
    "explanation": "..."
  }}
]

RULES:
- Cover ALL concepts
- Include logical, conceptual, tricky questions
- Answer must be index (0-3)

Topic:
{text}
"""

    try:
        result = model(
            prompt,
            max_length=1024,
            do_sample=False
        )[0]["generated_text"]

        # -----------------------------
        # CLEAN + PARSE JSON
        # -----------------------------
        result = result.strip()

        # fix common issues
        if result.startswith("```"):
            result = result.strip("```")

        # attempt parse
        data = json.loads(result)

        if isinstance(data, list):
            return data

        return []

    except Exception as e:
        print("❌ JSON Parse Failed:", e)
        return []
