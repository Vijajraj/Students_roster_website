"""Print the actual row data around shift boundaries to verify shift direction."""
import re, os
from pypdf import PdfReader

artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
reader = PdfReader(pdf_path)
row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}

# Check pages 3 and 4 (0-indexed: pages 2 and 3)
for page_idx in [2, 3]:
    page = reader.pages[page_idx]
    text = page.extract_text(extraction_mode="layout")
    if not text:
        continue
    
    rows = []
    for line in text.split("\n"):
        stripped = line.strip()
        match = row_pattern.match(stripped)
        if not match:
            continue
        parts = re.split(r'\s{2,}', stripped)
        if len(parts) < 7:
            continue
        dept_idx = -1
        for idx, part in enumerate(parts):
            if part.upper() in depts:
                dept_idx = idx
                break
        if dept_idx == -1:
            continue
        handles = parts[dept_idx + 3:]
        rows.append({
            "sno": parts[0],
            "name": parts[2],
            "lc": handles[0].strip() if handles else ""
        })
    
    print(f"\n=== PAGE {page_idx+1} ({len(rows)} rows) ===")
    # Print first 15 and last 15 rows
    for i, r in enumerate(rows[:15]):
        print(f"  Row {i:3d}: {r['sno']:5s} {r['name'][:25]:<25s} -> LC: {r['lc']}")
    if len(rows) > 30:
        print(f"  ... (rows 15-{len(rows)-16} omitted) ...")
    for i, r in enumerate(rows[-15:], len(rows)-15):
        print(f"  Row {i:3d}: {r['sno']:5s} {r['name'][:25]:<25s} -> LC: {r['lc']}")
