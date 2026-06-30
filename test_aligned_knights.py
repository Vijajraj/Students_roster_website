import re, os, json, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypdf import PdfReader

# 1. Matching function
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

# 2. DP Alignment
def parse_and_align_roster():
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
            
    # Backtrack
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
    
    # Realign all student handles based on the optimal path
    students = []
    bad_vals = {"training", "training/japanese", "training/german", "hs", "hs/p", "hs/startup", "nt", "p", "nil", "none", "-", ""}
    for d in depts:
        bad_vals.add(d.lower())
    bad_vals.update({"a", "b", "c", "d", "e"})
    
    seen_leetcode = set()
    seen_reg = set()
    
    for i in range(n):
        s = optimal_path[i]
        handle_idx = i + s
        
        row = all_rows[i]
        if 0 <= handle_idx < n:
            lc = all_rows[handle_idx]["lc"]
            cc = all_rows[handle_idx]["cc"]
            cf = all_rows[handle_idx]["cf"]
            gh = all_rows[handle_idx]["gh"]
        else:
            lc, cc, cf, gh = "", "", "", ""
            
        lc_clean = lc.strip(" ·-*()@").replace(":", "")
        if lc_clean.lower() in bad_vals or not lc_clean:
            continue
        if "leetcode.com" in lc_clean.lower():
            url_match = re.search(r"leetcode\.com/u?/?([\w_-]+)", lc_clean)
            if url_match:
                lc_clean = url_match.group(1)
            else:
                continue
        if "@citchennai" in lc_clean or "@" in lc_clean or " " in lc_clean:
            continue
            
        if lc_clean in seen_leetcode or row["reg"] in seen_reg:
            continue
            
        seen_leetcode.add(lc_clean)
        seen_reg.add(row["reg"])
        
        students.append({
            "name": row["name"],
            "reg": row["reg"],
            "dept": row["dept"],
            "sec": row["sec"],
            "leetcode": lc_clean,
            "codechef": cc,
            "codeforces": cf,
            "github": gh
        })
        
    return students

def test_aligned_knights():
    students = parse_and_align_roster()
    # Print specific students we know were shifted/wrong
    targets = {"Gajalakshmi S", "Ganesh Kumar R", "Gayathri R", "Gayathri S", "Gogul S", "Gokul D"}
    for s in students:
        if s["name"] in targets:
            print(f"Student: {s['name']:20s} | Reg: {s['reg']} | LC: {s['leetcode']:20s} | CF: {s['codeforces']}")

if __name__ == "__main__":
    test_aligned_knights()
