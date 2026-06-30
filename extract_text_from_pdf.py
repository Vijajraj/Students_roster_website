import os
from pypdf import PdfReader

artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
pdf_files = [
    os.path.join(artifact_dir, "media__1781338552404.pdf"),
    os.path.join(artifact_dir, "media__1782053115214.pdf"),
    os.path.join(artifact_dir, "media__1782748014324.pdf")
]

for pdf_path in pdf_files:
    if os.path.exists(pdf_path):
        print(f"\n--- Checking {os.path.basename(pdf_path)} ---")
        try:
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            print(f"Total pages: {num_pages}")
            
            # Extract text from page 1
            page_text = reader.pages[0].extract_text()
            print(f"Page 1 Text Length: {len(page_text) if page_text else 0}")
            if page_text:
                print("First 300 characters of Page 1 text:")
                print(page_text[:300])
            else:
                print("Page 1 text is empty (might be scanned image PDF)")
        except Exception as e:
            print(f"Error reading PDF: {e}")
