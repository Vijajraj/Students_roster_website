import os
import re
from pypdf import PdfReader

def extract_full_roster():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
        
    print(f"Reading PDF from {pdf_path}...")
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    all_lines = []
    
    # Regex to identify a student row: e.g., starts with a serial number, then a registration number
    # Example: "1283          24AD0001"
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    
    for page_num in range(total_pages):
        print(f"Extracting page {page_num + 1}/{total_pages}...")
        try:
            page = reader.pages[page_num]
            text = page.extract_text(extraction_mode="layout")
            if not text:
                continue
                
            lines = text.split("\n")
            page_rows = 0
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                match = row_pattern.match(stripped_line)
                if match:
                    tokens = stripped_line.split()
                    if len(tokens) >= 5:
                        # Append the original line with all padding spaces preserved
                        all_lines.append(line)
                        page_rows += 1
            print(f"  -> Found {page_rows} student rows on page {page_num + 1}")
        except Exception as e:
            print(f"  -> Error on page {page_num + 1}: {e}")
            
    # Save the full extracted roster
    with open("raw_ocr.txt", "w", encoding="utf-8") as f:
        for line in all_lines:
            f.write(line + "\n")
            
    print(f"\nSuccessfully extracted {len(all_lines)} student rows across all {total_pages} pages and saved to raw_ocr.txt!")

if __name__ == "__main__":
    extract_full_roster()
