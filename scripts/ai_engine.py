# scripts/ai_engine.py

import threading
from transformers import pipeline

_model = None
_lock = threading.Lock()


# -----------------------------
# LOAD MODEL (ONCE)
# -----------------------------
def get_model():
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                _model = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-base",   # better quality
                    device=-1
                )
    return _model


# -----------------------------
# GENERATE MCQs FROM TOPIC
# -----------------------------
def generate_mcqs_from_topic(text):

    if not text:
        return []

    model = get_model()

    text = text[:2000]  # limit for performance

    prompt = f"""
You are an expert UPSC exam question paper setter.

From the below topic, generate a large number of high-quality MCQs.

Rules:
- Cover ALL concepts in the topic
- Include:
    - conceptual questions
    - logical reasoning
    - pattern-based questions
    - tricky questions
    - application-based questions
- Each question must have:
    - 4 options
    - correct answer
    - clear explanation

Topic:
{text}
"""

    try:
        result = model(
            prompt,
            max_length=512,
            do_sample=False
        )[0]["generated_text"]

        return [result]

    except Exception as e:
        print("❌ AI Error:", e)
        return []
