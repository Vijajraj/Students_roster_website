import re, os
from pypdf import PdfReader

def clean_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def is_name_handle_match(name, handle):
    name = name.lower()
    handle = handle.lower()
    parts = [p.strip(" .") for p in name.split()]
    parts = [p for p in parts if len(p) >= 2 and p not in {"sri", "sai", "mr", "ms", "dr"}]
    
    clean_h = clean_str(handle)
    if not clean_h:
        return False
        
    for part in parts:
        clean_p = clean_str(part)
        if len(clean_p) >= 3:
            if clean_p in clean_h or clean_h in clean_p:
                print(f"    -> matched: '{clean_p}' in/contains '{clean_h}'")
                return True
            if len(clean_p) >= 4 and clean_h.startswith(clean_p[:3]):
                print(f"    -> matched: '{clean_h}' starts with prefix '{clean_p[:3]}'")
                return True
            if len(clean_h) >= 4 and clean_p.startswith(clean_h[:3]):
                print(f"    -> matched: '{clean_p}' starts with prefix '{clean_h[:3]}'")
                return True
                
    if len(parts) >= 2:
        initials = "".join([p[0] for p in parts])
        if len(initials) >= 3 and initials in clean_h:
            print(f"    -> matched initials: '{initials}' in '{clean_h}'")
            return True
            
    return False

def debug_306_309():
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

    for i in range(306, 310):
        print(f"\nIndex {i} (Sno {all_rows[i]['sno']}): {all_rows[i]['name']}")
        print(f"  Handle: {all_rows[i]['lc']}")
        print("  Checking current match:")
        curr_match = is_name_handle_match(all_rows[i]["name"], all_rows[i]["lc"])
        print(f"  Result: {curr_match}")
        
        print("  Checking next match:")
        next_match = is_name_handle_match(all_rows[i+1]["name"], all_rows[i]["lc"])
        print(f"  Result: {next_match}")

if __name__ == "__main__":
    debug_306_309()
