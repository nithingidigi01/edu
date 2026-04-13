# scripts/download_ncert.py

import os
import requests
from bs4 import BeautifulSoup
import time

BASE_PAGE = "https://ncert.nic.in/textbook.php"
OUTPUT_DIR = "raw_ncert"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TARGET_CLASS = "6"   # we start with class 6


def get_books():
    print("🔍 Fetching NCERT book list...")

    r = requests.get(BASE_PAGE, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    books = []

    for option in soup.find_all("option"):
        val = option.get("value")

        if val and val.startswith(TARGET_CLASS):
            books.append(val)

    return books


def get_pdf_links(book_code):
    url = f"https://ncert.nic.in/textbook.php?{book_code}"
    r = requests.get(url, headers=HEADERS, timeout=20)

    soup = BeautifulSoup(r.text, "lxml")

    pdf_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if ".pdf" in href:
            if not href.startswith("http"):
                href = "https://ncert.nic.in/" + href

            pdf_links.append(href)

    return pdf_links


def download_file(url, path):
    for attempt in range(5):
        try:
            print(f"⬇️ {url}")

            with requests.get(url, headers=HEADERS, stream=True, timeout=30) as r:
                r.raise_for_status()

                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)

            print(f"✅ Saved: {path}")
            return

        except Exception as e:
            print(f"⚠️ Retry {attempt+1}: {e}")
            time.sleep(5)

    raise Exception(f"❌ Failed download: {url}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    books = get_books()

    print(f"📚 Found {len(books)} books for class {TARGET_CLASS}")

    for book in books:
        print(f"\n📘 Processing book: {book}")

        pdfs = get_pdf_links(book)

        for i, pdf in enumerate(pdfs):
            file_name = f"{book}_chapter_{i+1}.pdf"
            path = os.path.join(OUTPUT_DIR, file_name)

            if os.path.exists(path):
                print(f"⏩ Skip: {file_name}")
                continue

            download_file(pdf, path)


if __name__ == "__main__":
    main()
