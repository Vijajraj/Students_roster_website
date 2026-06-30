import os
import sys

# Define artifact directory paths
artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
pdf_files = [
    os.path.join(artifact_dir, "media__1781338552404.pdf"),
    os.path.join(artifact_dir, "media__1782053115214.pdf"),
    os.path.join(artifact_dir, "media__1782748014324.pdf")
]

print("Python version:", sys.version)
print("Listing PDF artifacts and checking files:")

for pdf_path in pdf_files:
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"- {os.path.basename(pdf_path)}: EXISTS ({size} bytes)")
    else:
        print(f"- {os.path.basename(pdf_path)}: NOT FOUND")

# Try to import PDF libraries to see what is available
for lib in ["pypdf", "pdfplumber", "fitz", "PyPDF2", "pdfminer"]:
    try:
        __import__(lib)
        print(f"Library '{lib}' is AVAILABLE.")
    except ImportError:
        print(f"Library '{lib}' is NOT available.")
