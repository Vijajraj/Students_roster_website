import re, os
from pypdf import PdfReader

def inspect_around_suspicious():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}

    # Target specific pages and names that were flagged as suspicious
    targets = {
        "Abishek K": [1, 4],
        "Mithra B": [2],
        "Mohamed Askar S": [2],
        "Gayathri R": [9],
        "Harish E": [9],
        "Sanjay S": [14],
    }

    for page_idx in range(len(reader.pages)):
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
                "reg": parts[1],
                "name": parts[2],
                "lc": handles[0].strip() if handles else "",
                "line": stripped
            })
        
        # Check if any target is in this page
        for i, r in enumerate(rows):
            for t_name, t_pages in targets.items():
                if t_name in r["name"] and (page_idx + 1) in t_pages:
                    print(f"\n--- Context on Page {page_idx + 1} for '{r['name']}' (sno {r['sno']}) ---")
                    start_i = max(0, i - 3)
                    end_i = min(len(rows), i + 4)
                    for idx in range(start_i, end_i):
                        prefix = ">>> " if idx == i else "    "
                        print(f"{prefix}Row {idx:3d}: {rows[idx]['sno']:5s} {rows[idx]['name'][:25]:<25s} -> LC: {rows[idx]['lc']}")
                        print(f"        Raw: {rows[idx]['line']}")

if __name__ == "__main__":
    inspect_around_suspicious()
