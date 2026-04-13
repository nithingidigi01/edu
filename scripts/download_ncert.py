import os, requests
from concurrent.futures import ThreadPoolExecutor

BASE = "raw_ncert/class6"

DATA = {
    "geography": [
        "https://raw.githubusercontent.com/vidhwaan-data/ncert/main/class6/geography/ch1.pdf",
        "https://raw.githubusercontent.com/vidhwaan-data/ncert/main/class6/geography/ch2.pdf"
    ],
    "history": [
        "https://raw.githubusercontent.com/vidhwaan-data/ncert/main/class6/history/ch1.pdf"
    ],
    "science": [
        "https://raw.githubusercontent.com/vidhwaan-data/ncert/main/class6/science/ch1.pdf"
    ],
    "polity": [
        "https://raw.githubusercontent.com/vidhwaan-data/ncert/main/class6/polity/ch1.pdf"
    ]
}

def download(subject, idx, url):
    path = f"{BASE}/{subject}/chapter{idx}.pdf"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        return

    r = requests.get(url, timeout=30)
    with open(path, "wb") as f:
        f.write(r.content)

    print("✅", path)

def main():
    with ThreadPoolExecutor(max_workers=8) as ex:
        for subject, urls in DATA.items():
            for i, url in enumerate(urls, 1):
                ex.submit(download, subject, i, url)

if __name__ == "__main__":
    main()
