import re, os
from pypdf import PdfReader

def check_all_potential_shifts():
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

    # Let's check for each row:
    # Does the NEXT row's handle match this row's name?
    # Does the PREVIOUS row's handle match this row's name?
    # Does the CURRENT handle match this row's name?
    
    print("Checking for potential shifts across the entire student list...")
    
    shifted_next_votes = 0
    shifted_prev_votes = 0
    
    for i in range(1, len(all_rows) - 1):
        curr_name = all_rows[i]["name"].lower()
        curr_words = curr_name.split()
        if not curr_words:
            continue
        first_word = curr_words[0]
        if len(first_word) < 3:
            continue
            
        curr_lc = all_rows[i]["lc"].lower()
        prev_lc = all_rows[i-1]["lc"].lower()
        next_lc = all_rows[i+1]["lc"].lower()
        
        curr_match = first_word[:3] in curr_lc or curr_lc[:3] in first_word
        prev_match = first_word[:3] in prev_lc or prev_lc[:3] in first_word
        next_match = first_word[:3] in next_lc or next_lc[:3] in first_word
        
        # If prev_lc matches better than curr_lc
        if prev_match and not curr_match:
            # This indicates the handle was shifted DOWN (so student gets the previous row's handle)
            # wait, if handles shifted down: row[i] gets handles from row[i-1]
            print(f"Index {i:4d} (Sno {all_rows[i]['sno']}): {all_rows[i]['name']:25s} | Curr: {curr_lc:20s} | Prev: {prev_lc:20s} (Matches prev!)")
            shifted_prev_votes += 1
            
        # If next_lc matches better than curr_lc
        if next_match and not curr_match:
            # This indicates the handle was shifted UP (so student gets the next row's handle)
            # i.e., row[i] gets handles from row[i+1]
            print(f"Index {i:4d} (Sno {all_rows[i]['sno']}): {all_rows[i]['name']:25s} | Curr: {curr_lc:20s} | Next: {next_lc:20s} (Matches next!)")
            shifted_next_votes += 1

    print(f"\nTotal potential 'shifted to next' matches: {shifted_next_votes}")
    print(f"Total potential 'shifted to prev' matches: {shifted_prev_votes}")

if __name__ == "__main__":
    check_all_potential_shifts()
