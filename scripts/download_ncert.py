# scripts/download_ncert.py

import os
import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE = "https://ncert.nic.in/textbook.php"
OUT = "raw_ncert"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_WORKERS = min(16, (os.cpu_count() or 4))
RETRIES = 5
TIMEOUT = 20

session = requests.Session()
session.headers.update(HEADERS)


# -----------------------------
# SAFE FETCH (FIXED)
# -----------------------------
def fetch(url):

    for i in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)

            if r.status_code == 200 and r.text:
                return r.text

        except Exception:
            pass

        time.sleep(2 + i)

    print(f"❌ Failed to fetch: {url}")
    return None


# -----------------------------
# GET BOOK CODES (SAFE)
# -----------------------------
def get_books():

    html = fetch(BASE)

    if not html:
        print("❌ Cannot load NCERT base page")
        return []

    soup = BeautifulSoup(html, "lxml")

    codes = set()

    for opt in soup.find_all("option"):
        val = opt.get("value")

        if val and val[0].isdigit():
            cls = int(val[0])
            if 6 <= cls <= 12:
                codes.add(val)

    return list(codes)


# -----------------------------
# GET PDF LINKS (SAFE)
# -----------------------------
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


# -----------------------------
# DOWNLOAD FILE
# -----------------------------
def download(url, path):

    if os.path.exists(path):
        return

    for i in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)

            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)

                print(f"✅ {path}")
                return

        except:
            pass

        time.sleep(2 + i)

    print(f"❌ Failed: {url}")


# -----------------------------
# PROCESS BOOK
# -----------------------------
def process(code):

    try:
        cls = f"class{code[0]}"
        subject = code

        pdfs = get_pdfs(code)

        if not pdfs:
            print(f"⚠️ No PDFs for {code}")
            return

        folder = os.path.join(OUT, cls, subject)
        os.makedirs(folder, exist_ok=True)

        for i, pdf in enumerate(pdfs, 1):
            path = os.path.join(folder, f"chapter{i}.pdf")
            download(pdf, path)

    except Exception as e:
        print(f"❌ Book error: {code} | {e}")


# -----------------------------
# MAIN
# -----------------------------
def main():

    print("🚀 NCERT DOWNLOAD START")

    codes = get_books()

    if not codes:
        print("❌ No books found — stopping")
        return

    print(f"📚 Books found: {len(codes)}")

    with ThreadPoolExecutor(MAX_WORKERS) as ex:
        ex.map(process, codes)

    print("🔥 DOWNLOAD COMPLETE")


# -----------------------------
# ENTRY
# -----------------------------
if __name__ == "__main__":
    main()
