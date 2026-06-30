import re
import os

def test_parsing():
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    
    # Read the first 25 lines of the PDF to see the exact layout mode spacing
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text(extraction_mode="layout")
    lines = text.split("\n")
    
    print("--- Parsing using re.split(r'\\s{2,}', line) ---")
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    
    count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = row_pattern.match(line)
        if match:
            # Split by 2 or more spaces
            parts = re.split(r'\s{2,}', line)
            
            sno = parts[0]
            reg = parts[1]
            name = parts[2]
            
            # Find department index
            dept_idx = -1
            for idx, part in enumerate(parts):
                if part.upper() in depts:
                    dept_idx = idx
                    break
            
            if dept_idx != -1:
                dept = parts[dept_idx]
                sec = parts[dept_idx + 1] if dept_idx + 1 < len(parts) else ""
                training = parts[dept_idx + 2] if dept_idx + 2 < len(parts) else ""
                
                # The remaining parts after training should contain handles
                handles = parts[dept_idx + 3:]
                
                print(f"Sno: {sno} | Reg: {reg} | Name: {name} | Dept: {dept} | Sec: {sec} | Training: {training}")
                print(f"  Handles parsed: {handles}")
                
                count += 1
                if count >= 8:
                    break

if __name__ == "__main__":
    test_parsing()
