import os
import re
from pypdf import PdfReader

def check_alignment():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    
    # We will test slicing offsets on all pages
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    total_parsed = 0
    mismatches = []
    
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout")
        if not text:
            continue
            
        for line_idx, line in enumerate(text.split("\n"), 1):
            if not line.strip():
                continue
                
            # Check if this line starts with a Sno and RegNo
            # In layout mode, the line might have leading spaces
            match = row_pattern.match(line)
            if not match:
                # Let's try matching after stripping leading spaces
                stripped = line.strip()
                match = row_pattern.match(stripped)
                if not match:
                    continue
            
            # Since layout mode pads the line with spaces, let's look at the slices:
            # We slice the line based on our offsets:
            sno = line[0:14].strip()
            reg = line[14:29].strip()
            name = line[29:77].strip()
            dept = line[77:97].strip()
            sec = line[97:116].strip()
            training = line[116:135].strip()
            leetcode = line[135:167].strip()
            codechef = line[167:206].strip()
            codeforces = line[206:246].strip()
            github = line[246:].strip()
            
            # Validation
            # 1. RegNo should match the pattern
            if not re.match(r"^\d{2}[A-Za-z]{2,4}\d{4,5}$", reg):
                # If reg doesn't match, maybe there are leading spaces in the line which shifted it
                # Let's log it
                mismatches.append((page_num+1, line_idx, "REG_MISMATCH", line))
                continue
                
            # 2. Dept should be in our depts set
            if dept.upper() not in depts:
                mismatches.append((page_num+1, line_idx, f"DEPT_MISMATCH ({dept})", line))
                continue
                
            total_parsed += 1
            
            # Print a few samples from different pages
            if total_parsed % 300 == 0:
                print(f"Page {page_num+1} | Sno: {sno} | Reg: {reg} | Name: {name} | Dept: {dept} | Leetcode: {leetcode} | CF: {codeforces}")
                
    print(f"\nTotal parsed successfully using fixed slices: {total_parsed}")
    print(f"Total alignment mismatches: {len(mismatches)}")
    if mismatches:
        print("First 5 mismatches:")
        for m in mismatches[:5]:
            print(f"  Page {m[0]}, Line {m[1]} ({m[2]}):\n    Original: {m[3]}")
            
if __name__ == "__main__":
    check_alignment()
