import os
from pypdf import PdfReader

def check_raw_line():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    # Sno 1377 is on page 0 (the first page)
    page = reader.pages[0]
    text = page.extract_text(extraction_mode="layout")
    lines = text.split("\n")
    
    for idx, line in enumerate(lines):
        if "1377" in line:
            print(f"Index: {idx}")
            print(f"Line length: {len(line)}")
            print("Raw text line:")
            print(repr(line))
            print("Layout representation:")
            print(line)

if __name__ == "__main__":
    check_raw_line()
