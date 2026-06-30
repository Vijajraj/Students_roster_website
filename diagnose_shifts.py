import os
import re
from pypdf import PdfReader

def diagnose_shifts():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    shifted_count = 0
    ok_count = 0
    total = 0
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout")
        if not text:
            continue
        
        page_rows = []
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
            
            dept_idx = -1
            for idx, part in enumerate(parts):
                if part.upper() in depts:
                    dept_idx = idx
                    break
            if dept_idx == -1:
                continue
            
            name = parts[2]
            handles = parts[dept_idx + 3:]
            lc = handles[0].strip() if len(handles) > 0 else ""
            
            page_rows.append({
                "sno": parts[0],
                "reg": parts[1],
                "name": name,
                "lc": lc
            })
        
        # Check for shift: if name N's handle looks like name N+1
        for i in range(len(page_rows) - 1):
            total += 1
            curr_name = page_rows[i]["name"].lower().split()
            next_name = page_rows[i+1]["name"].lower().split()
            handle = page_rows[i]["lc"].lower()
            
            curr_first = curr_name[0] if curr_name else ""
            next_first = next_name[0] if next_name else ""
            
            # Check if handle matches NEXT student's name better than current
            curr_match = (len(curr_first) >= 3 and curr_first[:3] in handle) or (len(handle) >= 3 and handle[:3] in curr_first)
            next_match = (len(next_first) >= 3 and next_first[:4] in handle) or (len(handle) >= 4 and handle[:4] in next_first)
            
            if next_match and not curr_match and len(next_first) >= 3:
                shifted_count += 1
                if shifted_count <= 20:
                    print(f"SHIFTED page {page_num+1}: {page_rows[i]['name']} has LC '{page_rows[i]['lc']}' (looks like it belongs to '{page_rows[i+1]['name']}')")
            else:
                ok_count += 1
        
        if page_rows:
            total += 1  # last row
            ok_count += 1
    
    print(f"\nTotal rows: {total}")
    print(f"Rows with matching handles: {ok_count}")
    print(f"Rows with shifted handles: {shifted_count}")
    print(f"Shift rate: {shifted_count/total*100:.1f}%")

if __name__ == "__main__":
    diagnose_shifts()
