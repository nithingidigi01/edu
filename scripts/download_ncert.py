# scripts/download_ncert.py

import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "https://ncert.nic.in/textbook.php"
DOWNLOAD_BASE = "raw_ncert"

MAX_WORKERS = min(32, (os.cpu_count() or 4) * 2)
RETRIES = 3
TIMEOUT = 20

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Connection": "keep-alive"
}

# 🔥 GLOBAL SESSION (10x faster)
session = requests.Session()
session.headers.update(HEADERS)


# -----------------------------
# FETCH WITH RETRY
# -----------------------------
def fetch(url):
    for i in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except Exception:
            time.sleep(1 + i)
    return None


# -----------------------------
# GET ALL BOOK CODES
# -----------------------------
def get_book_codes():

    html = fetch(BASE_URL)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    codes = set()

    for option in soup.find_all("option"):
        val = option.get("value")

        if val and val[0].isdigit():
            cls = int(val[0])
            if 6 <= cls <= 12:
                codes.add(val)

    return list(codes)


# -----------------------------
# GET PDF LINKS
# -----------------------------
def get_pdfs(book_code):

    url = f"{BASE_URL}?{book_code}"

    html = fetch(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    pdfs = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if ".pdf" in href:
            if not href.startswith("http"):
                href = "https://ncert.nic.in/" + href

            pdfs.append(href)

    return pdfs


# -----------------------------
# DOWNLOAD FILE (FAST)
# -----------------------------
def download_file(url, path):

    if os.path.exists(path):
        return

    for i in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)
            r.raise_for_status()

            with open(path, "wb") as f:
                f.write(r.content)

            print(f"✅ {path}")
            return

        except Exception:
            time.sleep(1 + i)

    print(f"❌ Failed: {url}")


# -----------------------------
# PROCESS BOOK (PARALLEL INSIDE)
# -----------------------------
def process_book(code):

    try:
        cls = code[0]

        pdfs = get_pdfs(code)

        if not pdfs:
            return

        subject = code
        folder = os.path.join(DOWNLOAD_BASE, f"class{cls}", subject)
        os.makedirs(folder, exist_ok=True)

        tasks = []

        # 🔥 parallel per chapter
        with ThreadPoolExecutor(max_workers=6) as ex:
            for i, pdf in enumerate(pdfs, 1):

                path = os.path.join(folder, f"chapter{i}.pdf")

                tasks.append(ex.submit(download_file, pdf, path))

            for t in tasks:
                t.result()

    except Exception as e:
        print(f"❌ Book failed: {code} | {e}")


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 NCERT DOWNLOAD START")

    codes = get_book_codes()

    print(f"📚 Books: {len(codes)}")
    print(f"⚡ Workers: {MAX_WORKERS}")

    # 🔥 parallel per book
    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        ex.map(process_book, codes)

    print("🔥 NCERT DOWNLOAD COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
