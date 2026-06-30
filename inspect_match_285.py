import re, os
from pypdf import PdfReader

def get_significant_name(name):
    words = [w.strip(" .") for w in name.lower().split()]
    for w in words:
        if len(w) >= 3 and w not in {"aids", "aiml", "csbs", "ece", "vlsi"}:
            return w
    return words[0] if words else ""

def inspect_match_285():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}

    all_rows = []
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout")
        if not text:
            continue
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
            all_rows.append({
                "sno": parts[0],
                "name": parts[2],
                "lc": handles[0].strip() if handles else ""
            })

    # Let's inspect index 284, 285, 286
    for i in [284, 285, 286]:
        curr_sig = get_significant_name(all_rows[i]["name"])
        next_sig = get_significant_name(all_rows[i+1]["name"])
        handle = all_rows[i]["lc"].lower()
        
        curr_match = curr_sig in handle or handle in curr_sig
        next_match = next_sig in handle or handle in next_sig
        
        print(f"Index {i} (Sno {all_rows[i]['sno']}): {all_rows[i]['name']:25s} | Handle: {handle:20s}")
        print(f"  curr_sig: {curr_sig} | next_sig: {next_sig}")
        print(f"  curr_match: {curr_match} | next_match: {next_match}")

if __name__ == "__main__":
    inspect_match_285()
