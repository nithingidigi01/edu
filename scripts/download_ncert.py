# scripts/download_ncert.py

import os
import requests
import time

BASE_URL = "https://ncert.nic.in/textbook/pdf/"
OUTPUT_DIR = "raw_ncert"

BOOKS = {
    "geography": "fess1dd.zip",
    "history": "fess2dd.zip",
    "polity": "fess3dd.zip"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

MAX_RETRIES = 5
TIMEOUT = 20


def download_file(url, path):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"⬇️ Attempt {attempt}: {url}")

            with requests.get(url, headers=HEADERS, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()

                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            print(f"✅ Downloaded: {path}")
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                wait_time = attempt * 5
                print(f"⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed permanently: {url}")
                return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for subject, file in BOOKS.items():
        url = BASE_URL + file
        path = os.path.join(OUTPUT_DIR, file)

        # skip if already exists
        if os.path.exists(path):
            print(f"⏩ Skipping (already exists): {file}")
            continue

        print(f"\n📘 Downloading {subject}...")
        success = download_file(url, path)

        if not success:
            raise Exception(f"Download failed for {subject}")


if __name__ == "__main__":
    main()
