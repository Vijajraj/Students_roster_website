import os

def check_offsets():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text(extraction_mode="layout")
    lines = text.split("\n")
    
    print("--- Printing lines with character column markers ---")
    header_marker = "0123456789" * 26
    print(header_marker)
    
    # We inspect the first 10 lines
    count = 0
    for line in lines:
        if len(line.strip()) > 50:
            print(line)
            count += 1
            if count >= 10:
                break

if __name__ == "__main__":
    check_offsets()
