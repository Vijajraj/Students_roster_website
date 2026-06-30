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
                return True
            if len(clean_p) >= 5 and clean_h.startswith(clean_p[:4]):
                return True
            if len(clean_h) >= 5 and clean_p.startswith(clean_h[:4]):
                return True
                
    if len(parts) >= 2:
        initials = "".join([p[0] for p in parts])
        if len(initials) >= 3 and initials in clean_h:
            return True
            
    return False

def self_healing_alignment():
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
                "reg": parts[1],
                "name": parts[2],
                "lc": handles[0].strip() if handles else "",
                "cc": handles[1].strip() if len(handles) > 1 else "",
                "cf": handles[2].strip() if len(handles) > 2 else "",
                "gh": handles[3].strip() if len(handles) > 3 else "",
                "original_idx": len(all_rows)
            })

    n = len(all_rows)
    
    # First, identify which rows are "correct" (match their current handle)
    is_correct = [False] * n
    for i in range(n):
        if is_name_handle_match(all_rows[i]["name"], all_rows[i]["lc"]):
            is_correct[i] = True

    # Now, for every incorrect row, try to find a matching handle in the vicinity (window of 50 rows)
    # that is currently assigned to an incorrect row.
    reassigned = [None] * n
    
    for i in range(n):
        if is_correct[i]:
            reassigned[i] = all_rows[i]["original_idx"]
            continue
            
        # Search window of 50 rows before and after
        best_j = None
        for j in range(max(0, i - 50), min(n, i + 51)):
            # If the handle at j matches student i
            if is_name_handle_match(all_rows[i]["name"], all_rows[j]["lc"]):
                # And handle at j does NOT match student j (or student j is not correct)
                if not is_correct[j]:
                    best_j = j
                    break
                    
        if best_j is not None:
            reassigned[i] = best_j
            print(f"Healed: {all_rows[i]['name']:25s} (Sno {all_rows[i]['sno']}) -> Got handle of {all_rows[best_j]['name']:25s} (Sno {all_rows[best_j]['sno']}): {all_rows[best_j]['lc']}")
        else:
            # Fallback to current if nothing found (or it's just a random handle that is correct but doesn't match name)
            reassigned[i] = i

    # Count mismatch stats after healing
    mismatches = 0
    for i in range(n):
        j = reassigned[i]
        final_lc = all_rows[j]["lc"]
        if not is_name_handle_match(all_rows[i]["name"], final_lc):
            mismatches += 1
            
    print(f"\nMismatches remaining after self-healing: {mismatches} / {n} ({mismatches/n*100:.1f}%)")

if __name__ == "__main__":
    self_healing_alignment()
