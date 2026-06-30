import re, os, json
from pypdf import PdfReader

def clean_str(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def check_initial_mismatch(name, handle):
    name_parts = [p.strip(" .").lower() for p in name.split()]
    initials = [p for p in name_parts if len(p) == 1]
    if not initials:
        return False
    initial = initials[0]
    
    handle_clean = clean_str(handle)
    for p in name_parts:
        clean_p = clean_str(p)
        if len(clean_p) >= 3:
            if clean_p in handle_clean:
                handle_clean = handle_clean.replace(clean_p, "")
            elif handle_clean.startswith(clean_p[:4]):
                handle_clean = handle_clean[len(clean_p[:4]):]
            elif handle_clean.startswith(clean_p[:3]):
                handle_clean = handle_clean[len(clean_p[:3]):]
            elif clean_p.startswith(handle_clean):
                handle_clean = ""
            
    handle_remaining_letters = re.sub(r'[^a-z]', '', handle_clean)
    if handle_remaining_letters:
        first_letter = handle_remaining_letters[0]
        if first_letter != initial:
            return True
    return False

def is_name_handle_match(name, handle):
    if check_initial_mismatch(name, handle):
        return False
        
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

def hybrid_alignment():
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
                "dept": parts[dept_idx],
                "sec": parts[dept_idx + 1] if dept_idx + 1 < len(parts) else "",
                "lc": handles[0].strip() if handles else "",
                "cc": handles[1].strip() if len(handles) > 1 else "",
                "cf": handles[2].strip() if len(handles) > 2 else "",
                "gh": handles[3].strip() if len(handles) > 3 else ""
            })

    n = len(all_rows)
    
    # ----------------------------------------------------
    # PHASE 1: DP ALIGNMENT FOR MAJOR STRUCTURAL SHIFTS
    # ----------------------------------------------------
    TRANSITION_PENALTY = -6
    MATCH_SCORE = 10
    MISMATCH_SCORE = 0
    states = [0, 1, -1]
    dp = [{} for _ in range(n)]
    
    for s in states:
        if s == -1:
            dp[0][s] = (-9999, None)
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
            
    best_score = -9999
    best_state = None
    for s in states:
        score, _ = dp[n-1][s]
        if score > best_score:
            best_score = score
            best_state = s
            
    curr_state = best_state
    optimal_path = []
    for i in range(n-1, -1, -1):
        optimal_path.append(curr_state)
        _, prev_state = dp[i][curr_state]
        curr_state = prev_state
    optimal_path.reverse()
    
    fixed_rows = []
    for r in all_rows:
        fixed_rows.append(r.copy())
        
    i = 0
    while i < n:
        state = optimal_path[i]
        if state != 0:
            start = i
            while i < n - 1 and optimal_path[i+1] == state:
                i += 1
            end = i
            length = end - start + 1
            if length >= 8:
                print(f"Applying DP Realignment for rows {start}-{end} (length {length}, offset: {state})")
                for j in range(start, end + 1):
                    src_idx = j + state
                    if 0 <= src_idx < n:
                        fixed_rows[j]["lc"] = all_rows[src_idx]["lc"]
                        fixed_rows[j]["cc"] = all_rows[src_idx]["cc"]
                        fixed_rows[j]["cf"] = all_rows[src_idx]["cf"]
                        fixed_rows[j]["gh"] = all_rows[src_idx]["gh"]
            i = end + 1
        else:
            i += 1
            
    # ----------------------------------------------------
    # PHASE 2: UNIQUE LOCAL SELF-HEALING WINDOW MATCHING
    # ----------------------------------------------------
    is_correct = [False] * n
    assigned_handles = set()
    
    for i in range(n):
        if is_name_handle_match(fixed_rows[i]["name"], fixed_rows[i]["lc"]):
            is_correct[i] = True
            assigned_handles.add(fixed_rows[i]["lc"].lower())
            
    final_realigned = []
    for r in fixed_rows:
        final_realigned.append(r.copy())
        
    for i in range(n):
        if is_correct[i]:
            continue
            
        best_j = None
        for j in range(max(0, i - 15), min(n, i + 16)):
            candidate_lc = fixed_rows[j]["lc"]
            if candidate_lc.lower() not in assigned_handles:
                if is_name_handle_match(fixed_rows[i]["name"], candidate_lc):
                    if not is_correct[j]:
                        best_j = j
                        break
                        
        if best_j is not None:
            final_realigned[i]["lc"] = fixed_rows[best_j]["lc"]
            final_realigned[i]["cc"] = fixed_rows[best_j]["cc"]
            final_realigned[i]["cf"] = fixed_rows[best_j]["cf"]
            final_realigned[i]["gh"] = fixed_rows[best_j]["gh"]
            assigned_handles.add(fixed_rows[best_j]["lc"].lower())
            print(f"Healed unique swap: {fixed_rows[i]['name']:25s} (Sno {fixed_rows[i]['sno']}) -> Got handle from {fixed_rows[best_j]['name']:25s} (Sno {fixed_rows[best_j]['sno']}): {fixed_rows[best_j]['lc']}")
            
    targets = {"Gajalakshmi S", "Ganesh Kumar R", "Gayathri R", "Gayathri S", "Gogul S", "Gokul D"}
    print("\n--- Target Verification ---")
    for s in final_realigned:
        if s["name"] in targets:
            print(f"Student: {s['name']:25s} | Reg: {s['reg']} | LC: {s['lc']:20s} | CF: {s['cf']}")

if __name__ == "__main__":
    hybrid_alignment()
