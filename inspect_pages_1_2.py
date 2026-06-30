import re, os
from pypdf import PdfReader

def inspect_pages_1_2():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}

    for page_idx in [0, 1]:  # page 1 and 2
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
        
        print(f"\n=== PAGE {page_idx + 1} ===")
        # Print target contexts specifically
        for i, r in enumerate(rows):
            if "Abishek" in r["name"] or "Mithra" in r["name"] or "Mohamed Askar" in r["name"]:
                print(f"\nTarget row: {r['name']} (sno {r['sno']})")
                start_i = max(0, i - 2)
                end_i = min(len(rows), i + 3)
                for idx in range(start_i, end_i):
                    prefix = ">>> " if idx == i else "    "
                    print(f"{prefix}{rows[idx]['sno']:5s} {rows[idx]['name'][:25]:<25s} -> LC: {rows[idx]['lc']}")
                    print(f"        Raw: {rows[idx]['line']}")

if __name__ == "__main__":
    inspect_pages_1_2()
