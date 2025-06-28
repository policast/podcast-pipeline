"""Extract text from PDF files.

This script converts all PDF files in the specified PDF directory to text files
and saves them in the TXT directory.
"""

# %%
from pathlib import Path

import pymupdf
from tqdm import tqdm

from llm_podcast.settings import PDF_DIR, TXT_DIR

# %%
# EXTRACT TEXT FROM PDFs

pdf_files: list[Path] = list(PDF_DIR.glob("*.pdf"))

TXT_DIR.mkdir(parents=True, exist_ok=True)

for pdf_file in tqdm(pdf_files):
    print(f"Extracting text from {pdf_file} ...")
    with pymupdf.open(pdf_file) as doc:
        text = "".join(page.get_text() for page in doc)
    filename = (TXT_DIR / pdf_file.stem).with_suffix(".txt")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

# %%
