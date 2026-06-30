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

def align_roster():
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
                "lc": handles[0].strip() if handles else "",
                "cc": handles[1].strip() if len(handles) > 1 else "",
                "cf": handles[2].strip() if len(handles) > 2 else "",
                "gh": handles[3].strip() if len(handles) > 3 else ""
            })

    n = len(all_rows)
    # States:
    # 0: Normal (student i gets handle i)
    # 1: Shift Up (student i gets handle i+1)
    # -1: Shift Down (student i gets handle i-1)
    
    # DP table: dp[i][state] = (score, prev_state)
    # Penalize state transitions (to keep shift regions contiguous)
    TRANSITION_PENALTY = -5
    MATCH_SCORE = 10
    MISMATCH_SCORE = 0
    
    states = [0, 1, -1]
    dp = [{} for _ in range(n)]
    
    # Initialize base case (i = 0)
    for s in states:
        if s == -1:
            dp[0][s] = (-9999, None) # row 0 can't get handle -1
        elif s == 0:
            match = is_name_handle_match(all_rows[0]["name"], all_rows[0]["lc"])
            score = MATCH_SCORE if match else MISMATCH_SCORE
            dp[0][s] = (score, None)
        elif s == 1:
            match = is_name_handle_match(all_rows[0]["name"], all_rows[1]["lc"])
            score = MATCH_SCORE if match else MISMATCH_SCORE
            dp[0][s] = (score + TRANSITION_PENALTY, None)
            
    for i in range(1, n):
        for s in states:
            best_score = -9999
            best_prev = None
            
            # Determine match score for student i in state s
            handle_idx = i + s
            if 0 <= handle_idx < n:
                match = is_name_handle_match(all_rows[i]["name"], all_rows[handle_idx]["lc"])
                current_match_score = MATCH_SCORE if match else MISMATCH_SCORE
            else:
                current_match_score = -9999
                
            for prev_s in states:
                prev_score, _ = dp[i-1][prev_s]
                penalty = 0 if s == prev_s else TRANSITION_PENALTY
                total = prev_score + penalty + current_match_score
                if total > best_score:
                    best_score = total
                    best_prev = prev_s
                    
            dp[i][s] = (best_score, best_prev)
            
    # Backtrack
    optimal_path = []
    # Find best state at n-1
    best_score = -9999
    best_state = None
    for s in states:
        score, _ = dp[n-1][s]
        if score > best_score:
            best_score = score
            best_state = s
            
    curr_state = best_state
    for i in range(n-1, -1, -1):
        optimal_path.append(curr_state)
        _, prev_state = dp[i][curr_state]
        curr_state = prev_state
        
    optimal_path.reverse()
    
    # Identify and print shift regions
    i = 0
    while i < n:
        state = optimal_path[i]
        if state != 0:
            start = i
            while i < n - 1 and optimal_path[i+1] == state:
                i += 1
            end = i
            length = end - start + 1
            print(f"Optimal Alignment Region: rows {start}-{end} (length {length}) | State: {state} | Sno {all_rows[start]['sno']}-{all_rows[end]['sno']}")
            print(f"  First: {all_rows[start]['name']} (LC: {all_rows[start]['lc']})")
            print(f"  Last:  {all_rows[end]['name']} (LC: {all_rows[end]['lc']})")
        i += 1

if __name__ == "__main__":
    align_roster()
