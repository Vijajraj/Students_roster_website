import os
from pypdf import PdfReader

artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")

reader = PdfReader(pdf_path)
page = reader.pages[0]
text = page.extract_text(extraction_mode="layout")

print("--- Printing first 15 lines of PDF text (including headers) ---")
lines = text.split("\n")
for idx, line in enumerate(lines[:25]):
    print(f"[{idx}] {line.strip()}")
