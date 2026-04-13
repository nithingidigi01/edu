import re

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_chapters(text):
    return re.split(r'(?:CHAPTER|Chapter)\s+\d+', text)

def split_topics(text):
    return re.split(r'\n[A-Z][A-Za-z\s]{3,60}\n', text)
