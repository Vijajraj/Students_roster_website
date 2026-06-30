import json
import os
import re
from pypdf import PdfReader

def cross_check():
    # Load the saved badge holders
    with open("knights.json", "r", encoding="utf-8") as f:
        badge_holders = json.load(f)
    
    # Build a lookup: (name, dept, sec) -> leetcode_username
    holder_lookup = {}
    for b in badge_holders:
        holder_lookup[(b["name"], b["dept"], b["sec"])] = b["leetcode_username"]
    
    # Now scan the PDF and for each badge holder, print the full original line
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    print("=== Cross-checking badge holders against original PDF lines ===\n")
    
    mismatches = []
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout")
        if not text:
            continue
        
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            match = row_pattern.match(stripped)
            if not match:
                continue
            
            parts = re.split(r'\s{2,}', stripped)
            if len(parts) < 7:
                continue
            
            name = parts[2]
            
            # Find dept_idx
            dept_idx = -1
            for idx, part in enumerate(parts):
                if part.upper() in depts:
                    dept_idx = idx
                    break
            
            if dept_idx == -1:
                continue
                
            dept = parts[dept_idx]
            sec = parts[dept_idx + 1] if dept_idx + 1 < len(parts) else ""
            
            key = (name, dept, sec)
            if key in holder_lookup:
                handles = parts[dept_idx + 3:]
                lc_from_pdf = handles[0].strip() if len(handles) > 0 else ""
                lc_saved = holder_lookup[key]
                
                # Clean the PDF handle same way as our parser
                lc_cleaned = lc_from_pdf.strip(" ·-*()@").replace(":", "")
                if "leetcode.com" in lc_cleaned.lower():
                    url_match = re.search(r"leetcode\.com/u?/?([\w_-]+)", lc_cleaned)
                    if url_match:
                        lc_cleaned = url_match.group(1)
                
                # If the handle was changed by the alignment/healing engine
                if lc_cleaned != lc_saved:
                    # Let's verify if the newly assigned handle matches the name
                    # We can use a simple name check: first name or initial overlap
                    name_words = name.lower().split()
                    first_name = name_words[0] if name_words else ""
                    handle_lower = lc_saved.lower()
                    
                    is_suspicious = False
                    # If the aligned handle doesn't seem to match the name at all
                    if len(first_name) >= 3 and first_name[:3] not in handle_lower and handle_lower[:3] not in first_name:
                        is_suspicious = True
                        
                    mismatches.append({
                        "name": name,
                        "dept": dept,
                        "sec": sec,
                        "page": page_num + 1,
                        "saved_lc": lc_saved,
                        "pdf_lc": lc_from_pdf,
                        "is_suspicious": is_suspicious,
                        "parts": parts
                    })
    
    # Print all mismatches
    suspicious_mismatches = [m for m in mismatches if m["is_suspicious"]]
    plausible_alignments = [m for m in mismatches if not m["is_suspicious"]]
    
    print(f"Total alignments performed: {len(mismatches)}")
    print(f"  Suspicious alignments (unresolved): {len(suspicious_mismatches)}")
    print(f"  Plausible alignments (aligned successfully): {len(plausible_alignments)}\n")
    
    if suspicious_mismatches:
        print("=== SUSPICIOUS ALIGNMENTS (Needs human check) ===")
        for m in suspicious_mismatches[:30]:
            print(f"  Name: {m['name']} ({m['dept']} Sec {m['sec']}, page {m['page']})")
            print(f"    Saved LC: {m['saved_lc']} (suspicious!)")
            print(f"    PDF LC:   {m['pdf_lc']}")
            print(f"    Parts:    {m['parts']}")
            print()
            
    if plausible_alignments:
        print("=== PLAUSIBLE ALIGNMENTS (Correctly shifted) ===")
        for m in plausible_alignments[:10]:
            print(f"  Name: {m['name']} ({m['dept']} Sec {m['sec']}, page {m['page']})")
            print(f"    Saved LC: {m['saved_lc']} (plausible)")
            print(f"    PDF LC:   {m['pdf_lc']}")
            print()

if __name__ == "__main__":
    cross_check()
