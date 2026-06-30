import os
from pypdf import PdfReader

artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")

reader = PdfReader(pdf_path)
page = reader.pages[0]

# Try layout mode
text_layout = page.extract_text(extraction_mode="layout")
print("--- LAYOUT MODE FIRST 600 CHARS ---")
print(text_layout[:600])

# Try normal mode
text_normal = page.extract_text()
print("\n--- NORMAL MODE FIRST 300 CHARS ---")
print(text_normal[:300])
