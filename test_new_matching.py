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
            # 1. Direct substring
            if clean_p in clean_h or clean_h in clean_p:
                return True
            # 2. Tight prefix match (require length >= 4)
            if len(clean_p) >= 5 and clean_h.startswith(clean_p[:4]):
                return True
            if len(clean_h) >= 5 and clean_p.startswith(clean_h[:4]):
                return True
                
    if len(parts) >= 2:
        initials = "".join([p[0] for p in parts])
        if len(initials) >= 3 and initials in clean_h:
            return True
            
    return False

def test_new_matching():
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

    state = [0] * len(all_rows)
    for i in range(len(all_rows) - 1):
        curr_name = all_rows[i]["name"]
        next_name = all_rows[i+1]["name"]
        handle = all_rows[i]["lc"]
        
        curr_match = is_name_handle_match(curr_name, handle)
        next_match = is_name_handle_match(next_name, handle)
        
        if curr_match:
            state[i] = -1  # definitely correct
        elif next_match:
            state[i] = 1   # shifted
        else:
            state[i] = 0   # uncertain

    # Now let's see where the shifts are detected
    i = 0
    while i < len(all_rows):
        if state[i] == 1:
            shift_start = i
            while shift_start > 0 and state[shift_start - 1] == 0:
                shift_start -= 1
            for k in range(shift_start, i):
                if state[k] == -1:
                    shift_start = k + 1
                    break
            
            shift_end = i
            while shift_end < len(all_rows) - 1:
                if state[shift_end + 1] == -1:
                    break
                elif state[shift_end + 1] == 1:
                    shift_end += 1
                else:
                    found_next = False
                    for k in range(shift_end + 1, min(shift_end + 6, len(all_rows))):
                        if state[k] == 1:
                            shift_end = k
                            found_next = True
                            break
                        elif state[k] == -1:
                            break
                    if not found_next:
                        break
            
            shift_count = shift_end - shift_start + 1
            if shift_count >= 3:
                print(f"Shift Region: {shift_start}-{shift_end} ({shift_count} rows) | Sno {all_rows[shift_start]['sno']}-{all_rows[shift_end+1]['sno']}")
                print(f"  First: {all_rows[shift_start]['name']} (LC: {all_rows[shift_start]['lc']})")
                print(f"  Last:  {all_rows[shift_end+1]['name']} (LC: {all_rows[shift_end+1]['lc']})")
            i = shift_end + 1
        else:
            i += 1

if __name__ == "__main__":
    test_new_matching()
