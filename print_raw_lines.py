import os
from pypdf import PdfReader

def print_raw_layout_lines():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    reader = PdfReader(pdf_path)
    # Page 3 is index 2
    page = reader.pages[2]
    text = page.extract_text(extraction_mode="layout")
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        if "Sriram R" in line or "Srivarshini R" in line or "Sudharsan" in line:
            print(f"Line {idx}: {line}")

if __name__ == "__main__":
    print_raw_layout_lines()
