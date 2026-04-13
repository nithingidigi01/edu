# scripts/download_ncert.py

import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time

BASE_URL = "https://ncert.nic.in/textbook.php"
DOWNLOAD_BASE = "raw_ncert"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_WORKERS = 10
RETRIES = 3


# -----------------------------
# FETCH PAGE
# -----------------------------
def fetch(url):
    for i in range(RETRIES):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.text
        except:
            time.sleep(2)
    return None


# -----------------------------
# GET ALL BOOK CODES
# -----------------------------
def get_book_codes():
    html = fetch(BASE_URL)
    soup = BeautifulSoup(html, "lxml")

    codes = []

    for option in soup.find_all("option"):
        val = option.get("value")

        if val and val[0].isdigit():
            cls = int(val[0])
            if 6 <= cls <= 12:
                codes.append(val)

    return list(set(codes))


# -----------------------------
# GET PDF LINKS FROM BOOK
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
# DOWNLOAD FILE
# -----------------------------
def download(url, path):
    try:
        for i in range(RETRIES):
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                r.raise_for_status()

                with open(path, "wb") as f:
                    f.write(r.content)

                print(f"✅ {path}")
                return
            except:
                time.sleep(2)

        print(f"❌ Failed: {url}")

    except Exception as e:
        print(f"❌ Error: {e}")


# -----------------------------
# PROCESS BOOK
# -----------------------------
def process_book(code):

    cls = code[0]

    print(f"📘 Processing Book: {code}")

    pdfs = get_pdfs(code)

    if not pdfs:
        return

    subject = code

    for i, pdf in enumerate(pdfs, 1):
        folder = f"{DOWNLOAD_BASE}/class{cls}/{subject}"
        os.makedirs(folder, exist_ok=True)

        path = f"{folder}/chapter{i}.pdf"

        if os.path.exists(path):
            continue

        download(pdf, path)


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 Fetching all NCERT books...")

    codes = get_book_codes()

    print(f"📚 Found {len(codes)} books")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        ex.map(process_book, codes)

    print("🔥 ALL NCERT DOWNLOAD COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
