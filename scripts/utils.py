# scripts/utils.py

import re


# -----------------------------
# CLEAN TEXT (VERY IMPORTANT)
# -----------------------------
def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text.
    - Removes extra spaces
    - Fixes broken lines
    - Normalizes structure
    """

    # remove weird unicode spaces
    text = re.sub(r'\xa0', ' ', text)

    # collapse multiple newlines
    text = re.sub(r'\n+', '\n', text)

    # collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -----------------------------
# SPLIT CHAPTERS (NCERT STYLE)
# -----------------------------
def split_chapters(text: str):
    """
    Splits text into chapters using NCERT patterns.

    Handles:
    - CHAPTER 1
    - Chapter 1
    """

    parts = re.split(r'(?:CHAPTER|Chapter)\s+\d+', text)

    # remove empty / small garbage
    chapters = [p.strip() for p in parts if len(p.strip()) > 500]

    return chapters


# -----------------------------
# DETECT HEADINGS (CORE LOGIC)
# -----------------------------
def is_heading(line: str) -> bool:
    """
    Detect if a line is a topic heading.

    Rules:
    - Short line
    - Title case
    - No punctuation ending
    """

    line = line.strip()

    if len(line) < 5 or len(line) > 80:
        return False

    if line.endswith('.'):
        return False

    # Title Case check
    if line == line.title():
        return True

    return False


# -----------------------------
# SPLIT TOPICS (SMART)
# -----------------------------
def split_topics(chapter_text: str):
    """
    Splits chapter into topics using heading detection.
    This is CRITICAL for creating thousands of JSONs.
    """

    lines = chapter_text.split('\n')

    topics = []
    current = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # if heading → start new topic
        if is_heading(line) and current:
            topics.append(" ".join(current))
            current = []

        current.append(line)

    if current:
        topics.append(" ".join(current))

    # remove very small topics
    topics = [t for t in topics if len(t) > 200]

    return topics


# -----------------------------
# EXTRA: SAFE FILE NAME
# -----------------------------
def safe_name(text: str) -> str:
    """
    Converts text to safe folder/file name
    """

    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)

    return text.strip('_')
