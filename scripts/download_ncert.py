# scripts/download_ncert.py

import os
import requests

BASE_URL = "https://ncert.nic.in/textbook/pdf/"
OUTPUT_DIR = "raw_ncert"

# Class 6 sample books (we expand later)
BOOKS = {
    "geography": "fess1dd.zip",  # The Earth Our Habitat
    "history": "fess2dd.zip",
    "polity": "fess3dd.zip"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_file(url, path):
    r = requests.get(url, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

for subject, file in BOOKS.items():
    url = BASE_URL + file
    path = os.path.join(OUTPUT_DIR, file)

    print(f"Downloading {subject}...")
    download_file(url, path)

print("Download complete")
