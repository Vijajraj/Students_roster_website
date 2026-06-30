import os
import re
from pypdf import PdfReader

def test_ranges():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    reader = PdfReader(pdf_path)
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
                
            match = row_pattern.match(line.strip())
            if not match:
                continue
                
            # Extract basic info
            tokens = line.strip().split()
            dept_idx = -1
            for idx, token in enumerate(tokens):
                if token.upper() in depts:
                    dept_idx = idx
                    break
            
            if dept_idx == -1:
                mismatches.append((page_num+1, line_idx, "NO_DEPT", line))
                continue
                
            sno = tokens[0]
            reg = tokens[1]
            name = " ".join(tokens[2:dept_idx])
            dept = tokens[dept_idx]
            
            # Find the handles by looking at words starting after character index 120
            # Initialize all as empty
            leetcode = ""
            codechef = ""
            codeforces = ""
            github = ""
            
            # Find all non-space segments in the line
            for m in re.finditer(r"\S+", line):
                start = m.start()
                word = m.group()
                
                # Check ranges
                if 120 <= start <= 155:
                    leetcode = word
                elif 156 <= start <= 190:
                    codechef = word
                elif 191 <= start <= 230:
                    codeforces = word
                elif 231 <= start:
                    github = word
                    
            # Let's inspect some parsed records to see if they are 100% correct
            total_parsed += 1
            
            # Print a few samples that had mismatches earlier
            # Sno 1377 should have leetcode='harishv06', codechef='...', codeforces='harishv06', github=''
            if sno == "1377":
                print(f"[Match Sno 1377] Name: {name} | LC: {leetcode} | CC: {codechef} | CF: {codeforces} | GH: {github}")
            elif sno == "1324":
                print(f"[Match Sno 1324] Name: {name} | LC: {leetcode} | CC: {codechef} | CF: {codeforces} | GH: {github}")
            elif sno == "1704":
                print(f"[Match Sno 1704] Name: {name} | LC: {leetcode} | CC: {codechef} | CF: {codeforces} | GH: {github}")
                
    print(f"\nTotal parsed successfully: {total_parsed}")
    print(f"Total alignment mismatches: {len(mismatches)}")

if __name__ == "__main__":
    test_ranges()
