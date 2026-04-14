# scripts/ai_engine.py

import threading
from transformers import pipeline

# -----------------------------
# GLOBAL MODEL (LOAD ONCE)
# -----------------------------
_model = None
_lock = threading.Lock()

# CONFIG
MODEL_NAME = "google/flan-t5-small"
MAX_INPUT_CHARS = 1500   # safe for CI
MAX_OUTPUT_TOKENS = 256


# -----------------------------
# LOAD MODEL (THREAD SAFE)
# -----------------------------
def get_model():
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                _model = pipeline(
                    "text2text-generation",
                    model=MODEL_NAME,
                    device=-1  # CPU (CI safe)
                )

    return _model


# -----------------------------
# BUILD PROMPT (FAST)
# -----------------------------
def build_prompt(text: str) -> str:
    return (
        "Extract all important factual statements from the text below.\n"
        "Return each fact in a new line.\n\n"
        + text
    )


# -----------------------------
# CLEAN OUTPUT (FAST)
# -----------------------------
def parse_output(output_text: str):

    lines = output_text.split("\n")

    facts = []
    seen = set()

    for line in lines:
        line = line.strip()

        if len(line) < 15:
            continue

        if line in seen:
            continue

        seen.add(line)
        facts.append(line)

    return facts


# -----------------------------
# SINGLE TEXT EXTRACTION
# -----------------------------
def extract_facts(text: str):

    if not text:
        return []

    model = get_model()

    # limit input size (VERY IMPORTANT)
    text = text[:MAX_INPUT_CHARS]

    prompt = build_prompt(text)

    try:
        result = model(
            prompt,
            max_length=MAX_OUTPUT_TOKENS,
            do_sample=False
        )

        output = result[0]["generated_text"]

        return parse_output(output)

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return []


# -----------------------------
# BATCH PROCESSING (10x SPEED)
# -----------------------------
def extract_facts_batch(texts):
    """
    Process multiple topics at once (much faster)
    """

    if not texts:
        return []

    model = get_model()

    prompts = []

    for text in texts:
        text = text[:MAX_INPUT_CHARS]
        prompts.append(build_prompt(text))

    try:
        results = model(
            prompts,
            max_length=MAX_OUTPUT_TOKENS,
            do_sample=False
        )

        all_facts = []

        for res in results:
            output = res["generated_text"]
            all_facts.append(parse_output(output))

        return all_facts

    except Exception as e:
        print(f"❌ Batch AI Error: {e}")
        return [[] for _ in texts]
