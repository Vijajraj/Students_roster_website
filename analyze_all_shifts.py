import re, os
from pypdf import PdfReader

def analyze_all_shifts():
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
                "lc": handles[0].strip() if handles else "",
                "page": page_num + 1
            })

    # Let's compute shift votes for each row
    is_shifted = [False] * len(all_rows)
    for i in range(len(all_rows) - 1):
        curr_name_words = all_rows[i]["name"].lower().split()
        next_name_words = all_rows[i+1]["name"].lower().split()
        
        curr_first = curr_name_words[0] if curr_name_words else ""
        next_first = next_name_words[0] if next_name_words else ""
        handle = all_rows[i]["lc"].lower()
        
        if len(curr_first) < 3 or len(next_first) < 3 or len(handle) < 3:
            continue
            
        curr_match = curr_first[:3] in handle or handle[:3] in curr_first
        next_match = next_first[:4] in handle or handle[:4] in next_first
        
        if next_match and not curr_match:
            is_shifted[i] = True

    # Print any consecutive True sequences of length >= 2
    i = 0
    while i < len(all_rows):
        if is_shifted[i]:
            start = i
            while i < len(all_rows) - 1 and is_shifted[i+1]:
                i += 1
            end = i
            length = end - start + 1
            if length >= 2:
                print(f"Shift Region: index {start}-{end} (length {length}) | Sno {all_rows[start]['sno']}-{all_rows[end+1]['sno']} | Page {all_rows[start]['page']}")
                print(f"  Start student: {all_rows[start]['name']} (LC: {all_rows[start]['lc']})")
                print(f"  Next student:  {all_rows[start+1]['name']} (LC: {all_rows[start+1]['lc']})")
                print(f"  End student:   {all_rows[end+1]['name']} (LC: {all_rows[end+1]['lc']})")
        i += 1

if __name__ == "__main__":
    analyze_all_shifts()
