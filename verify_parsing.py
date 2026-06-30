import os
import re
from pypdf import PdfReader

def verify_parsing():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    total = 0
    problems = 0
    
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
            
            # Split by 2+ spaces - this preserves multi-word names as single tokens
            parts = re.split(r'\s{2,}', stripped)
            
            if len(parts) < 7:
                continue
            
            sno = parts[0]
            reg = parts[1]
            name = parts[2]
            
            # Find dept
            dept_idx = -1
            for idx, part in enumerate(parts):
                if part.upper() in depts:
                    dept_idx = idx
                    break
            
            if dept_idx == -1:
                continue
            
            dept = parts[dept_idx]
            sec = parts[dept_idx + 1] if dept_idx + 1 < len(parts) else ""
            training = parts[dept_idx + 2] if dept_idx + 2 < len(parts) else ""
            
            # Handles are everything after the training field
            handles = parts[dept_idx + 3:]
            
            # Assign: LeetCode, CodeChef, Codeforces, GitHub
            leetcode = handles[0] if len(handles) > 0 else ""
            codechef = handles[1] if len(handles) > 1 else ""
            codeforces = handles[2] if len(handles) > 2 else ""
            github = handles[3] if len(handles) > 3 else ""
            
            total += 1
            
            # Detect problems: if any handle looks like a dept, section, or training type
            bad_vals = {"training", "training/japanese", "training/german", "hs", "hs/p", "hs/startup", "nt", "p"}
            for d in depts:
                bad_vals.add(d.lower())
            bad_vals.update({"a", "b", "c", "d", "e"})
            
            if leetcode.lower() in bad_vals or codeforces.lower() in bad_vals or github.lower() in bad_vals:
                problems += 1
                if problems <= 10:
                    print(f"PROBLEM on page {page_num+1}: Sno={sno} Name={name}")
                    print(f"  Parts: {parts}")
                    print(f"  -> LC={leetcode} | CC={codechef} | CF={codeforces} | GH={github}")
                    print()
            
            # Also print some samples from different pages
            if total in {1, 107, 214, 500, 1000, 1500, 2000}:
                print(f"SAMPLE page {page_num+1}: Sno={sno} Name={name} Dept={dept}")
                print(f"  -> LC={leetcode} | CC={codechef} | CF={codeforces} | GH={github}")
                print()
    
    print(f"Total parsed: {total}")
    print(f"Problems detected: {problems}")

if __name__ == "__main__":
    verify_parsing()
