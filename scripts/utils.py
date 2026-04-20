# scripts/utils.py

import re

# -----------------------------
# PRECOMPILED REGEX (FAST)
# -----------------------------
RE_MULTI_NEWLINE = re.compile(r'\n+')
RE_MULTI_SPACE = re.compile(r'\s+')
RE_UNICODE_SPACE = re.compile(r'\xa0')
RE_CHAPTER = re.compile(r'(?:CHAPTER|Chapter)\s+\d+')
RE_SAFE_NAME = re.compile(r'[^a-z0-9]+')


# -----------------------------
# CLEAN TEXT (OPTIMIZED)
# -----------------------------
def clean_text(text: str) -> str:
    """
    Fast text normalization:
    - removes unicode junk
    - collapses spaces/newlines
    """

    if not text:
        return ""

    text = RE_UNICODE_SPACE.sub(' ', text)
    text = RE_MULTI_NEWLINE.sub('\n', text)
    text = RE_MULTI_SPACE.sub(' ', text)

    return text.strip()


# -----------------------------
# SPLIT CHAPTERS (FAST)
# -----------------------------
def split_chapters(text: str):
    """
    Fast chapter split using precompiled regex
    """

    parts = RE_CHAPTER.split(text)

    # fast filtering
    return [p.strip() for p in parts if len(p) > 500]


# -----------------------------
# HEADING DETECTION (IMPROVED + FAST)
# -----------------------------
def is_heading(line: str) -> bool:
    """
    Fast + smarter heading detection
    """

    if not line:
        return False

    line = line.strip()

    length = len(line)

    # quick filters (fast exit)
    if length < 5 or length > 80:
        return False

    if line[-1] == '.':
        return False

    # avoid numbers-heavy lines
    if sum(c.isdigit() for c in line) > 3:
        return False

    # Title Case OR UPPER CASE headings
    if line == line.title() or line.isupper():
        return True

    return False


# -----------------------------
# SPLIT TOPICS (OPTIMIZED)
# -----------------------------
def split_topics(chapter_text: str):
    """
    High-speed topic segmentation
    """

    if not chapter_text:
        return []

    lines = chapter_text.split('\n')

    topics = []
    current = []
    append_topic = topics.append

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # heading triggers new topic
        if is_heading(line) and current:
            append_topic(" ".join(current))
            current = []

        current.append(line)

    if current:
        append_topic(" ".join(current))

    # filter small topics (fast)
    return [t for t in topics if len(t) > 200]


# -----------------------------
# SAFE FILE NAME (FAST)
# -----------------------------
def safe_name(text: str) -> str:
    """
    Fast safe filename generator
    """

    if not text:
        return ""

    text = text.lower()
    text = RE_SAFE_NAME.sub('_', text)

    return text.strip('_')
