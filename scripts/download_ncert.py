# scripts/download_ncert.py

import os
import requests

BASE_DIR = "raw_ncert"

# 🔥 REAL STRUCTURE (START — EXPANDABLE)
DATA = {
    "class6": {
        "geography": [
            "https://ncert.nic.in/textbook/pdf/fess101.pdf",
            "https://ncert.nic.in/textbook/pdf/fess102.pdf",
            "https://ncert.nic.in/textbook/pdf/fess103.pdf"
        ],
        "history": [
            "https://ncert.nic.in/textbook/pdf/fess201.pdf"
        ],
        "science": [
            "https://ncert.nic.in/textbook/pdf/fesc101.pdf"
        ]
    },
    "class7": {
        "geography": [
            "https://ncert.nic.in/textbook/pdf/gesc101.pdf"
        ]
    }
}


def download(url, path):
    if os.path.exists(path):
        return

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()

        with open(path, "wb") as f:
            f.write(r.content)

        print(f"✅ {path}")

    except Exception as e:
        print(f"❌ {url} | {e}")


def main():

    print("🚀 DOWNLOAD START")

    for cls, subjects in DATA.items():
        for subject, urls in subjects.items():

            folder = os.path.join(BASE_DIR, cls, subject)
            os.makedirs(folder, exist_ok=True)

            for i, url in enumerate(urls, 1):
                path = os.path.join(folder, f"chapter{i}.pdf")
                download(url, path)

    print("🔥 DOWNLOAD COMPLETE")


if __name__ == "__main__":
    main()
