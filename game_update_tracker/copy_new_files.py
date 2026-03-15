from bs4 import BeautifulSoup
import os
import shutil
import sys

def process_bundles(html_file, source_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    bundle_files = []

    for row in soup.select("tr.modified td, tr.added td"):
        text = row.text.strip()
        if text.lower().endswith(".bundle"):
            bundle_files.append(text)

    print(f"Found {len(bundle_files)} .bundle files.")

    for file in bundle_files:
        src_path = os.path.join(source_dir, file)
        dest_path = os.path.join(dest_dir, os.path.basename(file))

        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"Copied: {file}")
        else:
            print(f"⚠️ Missing: {file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <html_file> <source_dir> <dest_dir>")
        sys.exit(1)

    process_bundles(sys.argv[1], sys.argv[2], sys.argv[3])