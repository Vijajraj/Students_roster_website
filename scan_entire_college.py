import re
import os
import requests
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypdf import PdfReader

# =====================================================
# STEP 1: Parse student records directly from PDF
# =====================================================
# =====================================================
# STEP 1: Helper functions for Name-to-Handle matching
# =====================================================
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
    if handle_remaining_letters and len(handle_remaining_letters) <= 2:
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
        
    name_parts = [p.strip(" .").lower() for p in name.split()]
    initials = [p for p in name_parts if len(p) == 1]
        
    def check_extra_chars(matched_part):
        rem = clean_h
        rem = rem.replace(matched_part, "", 1)
        for p in parts:
            clean_p = clean_str(p)
            if clean_p != matched_part and len(clean_p) >= 2:
                rem = rem.replace(clean_p, "")
        for word in ["cit", "chennai", "atpc", "cse", "aids", "ece", "it", "aiml", "ug", "leet", "leetcode", "code", "knights"]:
            rem = rem.replace(word, "")
        rem_alpha = re.sub(r'[^a-z]', '', rem)
        if len(rem_alpha) <= 2:
            return True
        for init in initials:
            if rem_alpha.startswith(init):
                return True
        return False

    for part in parts:
        clean_p = clean_str(part)
        if len(clean_p) >= 3:
            if clean_p in clean_h:
                if check_extra_chars(clean_p):
                    return True
            if clean_h in clean_p:
                if check_extra_chars(clean_h):
                    return True
            min_prefix = max(5, int(len(clean_p) * 0.6))
            if len(clean_p) >= min_prefix and len(clean_h) >= min_prefix:
                prefix = clean_p[:min_prefix]
                if clean_h.startswith(prefix):
                    if check_extra_chars(prefix):
                        return True
                
    if len(parts) >= 2:
        initials_str = "".join([p[0] for p in parts])
        if len(initials_str) >= 3 and initials_str in clean_h:
            return True
            
    return False



def parse_roster_from_pdf():
    artifact_dir = r"C:\Users\vraj1\.gemini\antigravity\brain\b7d2e33e-9118-4351-aa6c-4b0c8df4e8a5"
    pdf_path = os.path.join(artifact_dir, "media__1781338552404.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return []
    
    reader = PdfReader(pdf_path)
    row_pattern = re.compile(r"^\s*(\d+)\s+(\d{2}[A-Za-z]{2,4}\d{4,5})\b")
    depts = {"AIDS", "AIML", "CS", "CSBS", "CSE", "ECE", "IT", "VLSI"}
    bad_vals = {"training", "training/japanese", "training/german", "hs", "hs/p", "hs/startup", "nt", "p", "nil", "none", "-", ""}
    for d in depts:
        bad_vals.add(d.lower())
    bad_vals.update({"a", "b", "c", "d", "e"})
    
    all_rows = []
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
            
            sno = parts[0]
            reg = parts[1]
            name = parts[2]
            
            if not re.match(r"^\d{2}[A-Za-z]{2,4}\d{4,5}$", reg):
                continue
            
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
            
            handles = parts[dept_idx + 3:]
            leetcode = handles[0].strip() if len(handles) > 0 else ""
            codechef = handles[1].strip() if len(handles) > 1 else ""
            codeforces = handles[2].strip() if len(handles) > 2 else ""
            github = handles[3].strip() if len(handles) > 3 else ""
            
            all_rows.append({
                "sno": sno, "reg": reg, "name": name, "dept": dept, "sec": sec,
                "leetcode": leetcode, "codechef": codechef,
                "codeforces": codeforces, "github": github
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
            match = is_name_handle_match(all_rows[0]["name"], all_rows[0]["leetcode"])
            score = MATCH_SCORE if match else MISMATCH_SCORE
            dp[0][s] = (score, None)
        elif s == 1:
            match = is_name_handle_match(all_rows[0]["name"], all_rows[1]["leetcode"])
            score = MATCH_SCORE if match else MISMATCH_SCORE
            dp[0][s] = (score + TRANSITION_PENALTY, None)
            
    for i in range(1, n):
        for s in states:
            best_score = -9999
            best_prev = None
            
            handle_idx = i + s
            if 0 <= handle_idx < n:
                match = is_name_handle_match(all_rows[i]["name"], all_rows[handle_idx]["leetcode"])
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
            if length >= 2:
                print(f"  [FIX] DP realignment for rows {start}-{end} (length {length}, offset: {state})")
                for j in range(start, end + 1):
                    src_idx = j + state
                    if 0 <= src_idx < n:
                        fixed_rows[j]["leetcode"] = all_rows[src_idx]["leetcode"]
                        fixed_rows[j]["codechef"] = all_rows[src_idx]["codechef"]
                        fixed_rows[j]["codeforces"] = all_rows[src_idx]["codeforces"]
                        fixed_rows[j]["github"] = all_rows[src_idx]["github"]
            i = end + 1
        else:
            i += 1
            
    # ----------------------------------------------------
    # PHASE 2: UNIQUE LOCAL SELF-HEALING WINDOW MATCHING
    # ----------------------------------------------------
    is_correct = [False] * n
    assigned_handles = set()
    
    for i in range(n):
        if is_name_handle_match(fixed_rows[i]["name"], fixed_rows[i]["leetcode"]):
            is_correct[i] = True
            assigned_handles.add(fixed_rows[i]["leetcode"].lower())
            
    final_realigned = []
    for r in fixed_rows:
        final_realigned.append(r.copy())
        
    healed_count = 0
    for i in range(n):
        if is_correct[i]:
            continue
            
        best_j = None
        for j in range(max(0, i - 5), min(n, i + 6)):
            candidate_lc = fixed_rows[j]["leetcode"]
            if candidate_lc.lower() not in assigned_handles:
                if is_name_handle_match(fixed_rows[i]["name"], candidate_lc):
                    if not is_correct[j]:
                        best_j = j
                        break
                        
        if best_j is not None:
            final_realigned[i]["leetcode"] = fixed_rows[best_j]["leetcode"]
            final_realigned[i]["codechef"] = fixed_rows[best_j]["codechef"]
            final_realigned[i]["codeforces"] = fixed_rows[best_j]["codeforces"]
            final_realigned[i]["github"] = fixed_rows[best_j]["github"]
            assigned_handles.add(fixed_rows[best_j]["leetcode"].lower())
            healed_count += 1
            
    if healed_count > 0:
        print(f"  [FIX] Healed {healed_count} localized swaps/collisions via self-healing local matching.")
        
    # ---- Flatten and deduplicate by registration number ----
    students = []
    seen_reg = set()
    seen_leetcode = set()
    
    for row in final_realigned:
        if row["reg"] in seen_reg:
            continue
        
        lc = row["leetcode"].strip(" ·-*()@").replace(":", "")
        
        # Skip invalid handles
        if lc.lower() in bad_vals:
            continue
        if "leetcode.com" in lc.lower():
            url_match = re.search(r"leetcode\.com/u?/?([\w_-]+)", lc)
            if url_match:
                lc = url_match.group(1)
            else:
                continue
        if "@citchennai" in lc or "@" in lc:
            continue
        if " " in lc:
            continue
        if not lc:
            continue
        
        if lc in seen_leetcode:
            continue
        
        seen_reg.add(row["reg"])
        seen_leetcode.add(lc)
        students.append({
            "name": row["name"],
            "reg": row["reg"],
            "dept": row["dept"],
            "sec": row["sec"],
            "leetcode": lc,
            "github": row["github"],
            "codeforces": row["codeforces"],
            "codechef": row["codechef"]
        })
        
    return students


# =====================================================
# STEP 2: LeetCode API queries
# =====================================================
def check_leetcode_user(username):
    url = "https://leetcode.com/graphql"
    query = """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            rating
            globalRanking
            topPercentage
        }
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    try:
        r = requests.post(url, json={"query": query, "variables": {"username": username}}, timeout=5)
        if r.status_code == 200:
            data = r.json()
            ranking = data.get("data", {}).get("userContestRanking")
            matched_user = data.get("data", {}).get("matchedUser")
            
            solved = 0
            if matched_user:
                ac_subs = matched_user.get("submitStats", {}).get("acSubmissionNum", [])
                for sub in ac_subs:
                    if sub.get("difficulty") == "All":
                        solved = sub.get("count", 0)
            
            if ranking:
                rating = int(ranking.get("rating", 0))
                global_rank = ranking.get("globalRanking", 0)
                top_percent = ranking.get("topPercentage", 0.0)
                return {
                    "rating": rating,
                    "global_rank": global_rank,
                    "top_percentage": top_percent,
                    "solved": solved
                }
    except Exception:
        pass
    return None


def run_batch_query(batch):
    url = "https://leetcode.com/graphql"
    
    query_parts = ["query {"]
    for idx, s in enumerate(batch):
        username = s["leetcode"].replace('"', '\\"')
        query_parts.append(f"""
            u{idx}_rank: userContestRanking(username: "{username}") {{
                rating
                globalRanking
                topPercentage
            }}
            u{idx}_solved: matchedUser(username: "{username}") {{
                submitStats {{
                    acSubmissionNum {{
                        difficulty
                        count
                    }}
                }}
            }}
        """)
    query_parts.append("}")
    query = "\n".join(query_parts)
    
    results = {}
    try:
        r = requests.post(url, json={"query": query}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            res_data = data.get("data", {})
            for idx, s in enumerate(batch):
                ranking = res_data.get(f"u{idx}_rank")
                matched_user = res_data.get(f"u{idx}_solved")
                
                if ranking:
                    rating = int(ranking.get("rating", 0))
                    solved = 0
                    if matched_user:
                        for sub in matched_user.get("submitStats", {}).get("acSubmissionNum", []):
                            if sub.get("difficulty") == "All":
                                solved = sub.get("count", 0)
                    
                    results[s["leetcode"]] = {
                        "rating": rating,
                        "global_rank": ranking.get("globalRanking", 0),
                        "top_percentage": ranking.get("topPercentage", 0.0),
                        "solved": solved
                    }
            return results, False
    except Exception:
        pass
    return {}, True


# =====================================================
# STEP 3: Codeforces & GitHub enrichment
# =====================================================
def get_codeforces_info(handles):
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "OK":
                cf_map = {}
                for u in data.get("result", []):
                    cf_map[u.get("handle", "").lower()] = {
                        "rating": u.get("rating", 0),
                        "rank": u.get("rank", "unrated").title()
                    }
                return cf_map
    except Exception:
        pass
    return {}

github_rate_limit_hit = False

def get_github_repos(username):
    global github_rate_limit_hit
    if github_rate_limit_hit:
        return 0
    try:
        r = requests.get(f"https://api.github.com/users/{username}", timeout=4)
        if r.status_code == 200:
            return r.json().get("public_repos", 0)
        elif r.status_code == 403:
            if r.headers.get("X-RateLimit-Remaining") == "0":
                github_rate_limit_hit = True
                print("  [GitHub] Rate limit hit. Defaulting remaining profiles to 0 repos.")
    except Exception:
        pass
    return 0



# =====================================================
# MAIN
# =====================================================
def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("Parsing roster directly from PDF using multi-space splitting...")
    students = parse_roster_from_pdf()
    print(f"Loaded {len(students)} students with valid LeetCode handles.")
    
    # Print dept distribution
    dept_counts = {}
    for s in students:
        dept_counts[s["dept"]] = dept_counts.get(s["dept"], 0) + 1
    print(f"Department distribution: {dept_counts}")
    
    print(f"\nProcessing batches using GraphQL aliasing...")
    
    batch_size = 30
    batches = [students[i:i+batch_size] for i in range(0, len(students), batch_size)]
    
    def process_batch(batch):
        results, failed = run_batch_query(batch)
        if failed:
            individual_results = {}
            for s in batch:
                res = check_leetcode_user(s["leetcode"])
                if res:
                    individual_results[s["leetcode"]] = res
            return individual_results
        return results

    all_stats = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_batch, b): b for b in batches}
        for idx, future in enumerate(as_completed(futures), 1):
            all_stats.update(future.result())
            if idx % 10 == 0 or idx == len(batches):
                print(f"  -> {idx}/{len(batches)} batches done ({len(all_stats)} profiles)")
    
    # Build badge holders
    badge_holders = []
    for s in students:
        stats = all_stats.get(s["leetcode"])
        if stats:
            rating = stats["rating"]
            badge = "Specialist"
            if rating >= 2190:
                badge = "Guardian"
            elif rating >= 1850:
                badge = "Knight"
            
            # CodeChef stars logic
            stars = "1★"
            if badge == "Knight":
                stars = "3★"
            elif badge == "Guardian":
                stars = "5★"
            
            badge_holders.append({
                "name": s["name"],
                "dept": s["dept"],
                "sec": s["sec"],
                "leetcode_username": s["leetcode"],
                "codechef_username": s["codechef"],
                "codeforces_username": s["codeforces"],
                "github_username": s["github"],
                "leetcode_rating": str(rating),
                "solved_count": f"{stats['solved']}+",
                "codechef_stars": stars,
                "codeforces_rating": 0,
                "codeforces_rank": "unrated",
                "github_repos": 0,
                "role": f"LeetCode {badge}",
                "reactions": "100+"
            })
    
    print(f"\nLoaded {len(badge_holders)} coders into the database!")
    
    # Enrich with Codeforces
    if badge_holders:
        print("Enriching with Codeforces ratings...")
        cf_handles = []
        cf_map_idx = {}
        bad_cf = {"nil", "none", "-", ""}
        for s in badge_holders:
            cf = s["codeforces_username"].strip()
            if cf.lower() not in bad_cf and "@" not in cf and "http" not in cf:
                cf_handles.append(cf)
                cf_map_idx[cf.lower()] = s
        
        cf_data = {}
        for i in range(0, len(cf_handles), 50):
            cf_data.update(get_codeforces_info(cf_handles[i:i+50]))
        
        for handle, info in cf_data.items():
            if handle in cf_map_idx:
                cf_map_idx[handle]["codeforces_rating"] = info["rating"]
                cf_map_idx[handle]["codeforces_rank"] = info["rank"]
        
        print("Enriching with GitHub repo counts...")
        def enrich_gh(s):
            gh = s["github_username"].strip()
            if gh.lower() not in bad_cf and "@" not in gh and "http" not in gh:
                s["github_repos"] = get_github_repos(gh)
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(enrich_gh, badge_holders)
    
    # Sort by rating descending
    badge_holders.sort(key=lambda x: int(x["leetcode_rating"]), reverse=True)
    
    # Save
    with open("knights.json", "w", encoding="utf-8") as f:
        json.dump(badge_holders, f, indent=4, ensure_ascii=False)
    
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(f"window.knightsData = {json.dumps(badge_holders, indent=4, ensure_ascii=False)};")
    
    print(f"\nSaved {len(badge_holders)} badge holders to data.js and knights.json")
    print("\nTop 15:")
    for idx, b in enumerate(badge_holders[:15], 1):
        print(f"  {idx}. {b['name']} ({b['dept']}) - LC: {b['leetcode_username']} -> Rating: {b['leetcode_rating']} | CF: {b['codeforces_rating']}")

if __name__ == "__main__":
    main()
