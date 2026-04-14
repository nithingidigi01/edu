# scripts/download_ncert.py

import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE = "https://ncert.nic.in/textbook.php"
OUT = "raw_ncert"
HEAD = {"User-Agent": "Mozilla/5.0"}

session = requests.Session()
session.headers.update(HEAD)

def fetch(url):
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except:
        return None

def get_books():
    html = fetch(BASE)
    soup = BeautifulSoup(html, "lxml")

    codes = []

    for opt in soup.find_all("option"):
        val = opt.get("value")
        if val and val[0].isdigit():
            cls = int(val[0])
            if 6 <= cls <= 12:
                codes.append(val)

    return list(set(codes))

def get_pdfs(code):
    html = fetch(f"{BASE}?{code}")
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    pdfs = []

    for a in soup.find_all("a", href=True):
        h = a["href"]
        if ".pdf" in h:
            if not h.startswith("http"):
                h = "https://ncert.nic.in/" + h
            pdfs.append(h)

    return pdfs

def download(url, path):
    if os.path.exists(path):
        return
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print("✅", path)
    except:
        print("❌", url)

def process(code):
    cls = f"class{code[0]}"
    sub = code

    pdfs = get_pdfs(code)
    if not pdfs:
        return

    folder = os.path.join(OUT, cls, sub)
    os.makedirs(folder, exist_ok=True)

    for i, pdf in enumerate(pdfs, 1):
        path = os.path.join(folder, f"chapter{i}.pdf")
        download(pdf, path)

def main():
    codes = get_books()

    print("Books:", len(codes))

    with ThreadPoolExecutor(16) as ex:
        ex.map(process, codes)

if __name__ == "__main__":
    main()
