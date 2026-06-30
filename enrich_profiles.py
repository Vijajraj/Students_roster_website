import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_codeforces_info(handles):
    # Codeforces allows querying multiple handles separated by semicolon
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "OK":
                result = data.get("result", [])
                cf_map = {}
                for u in result:
                    handle = u.get("handle")
                    cf_map[handle.lower()] = {
                        "rating": u.get("rating", 0),
                        "rank": u.get("rank", "unrated").title(),
                        "maxRating": u.get("maxRating", 0),
                        "maxRank": u.get("maxRank", "unrated").title()
                    }
                return cf_map
    except Exception as e:
        print(f"Codeforces API error: {e}")
    return {}

def get_github_repos(username):
    url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            data = r.json()
            return data.get("public_repos", 0)
    except Exception:
        pass
    return None

def main():
    print("Enriching profiles from Codeforces and GitHub API...")
    
    with open("knights.json", "r", encoding="utf-8") as f:
        students = json.load(f)
        
    # 1. Collect all Codeforces handles (filter out Nil/empty)
    cf_handles = []
    cf_to_student = {}
    for s in students:
        cf_user = s.get("codeforces_username", "").strip()
        if cf_user and cf_user.lower() not in {"nil", "none", "url", "-"}:
            cf_handles.append(cf_user)
            cf_to_student[cf_user.lower()] = s
            
    print(f"Querying Codeforces API for {len(cf_handles)} handles...")
    # Query in chunks of 50 handles to be safe
    cf_map = {}
    chunk_size = 50
    for i in range(0, len(cf_handles), chunk_size):
        chunk = cf_handles[i:i+chunk_size]
        res = get_codeforces_info(chunk)
        cf_map.update(res)
        
    # Apply Codeforces updates
    for handle, info in cf_map.items():
        if handle in cf_to_student:
            student = cf_to_student[handle]
            student["codeforces_rating"] = info["rating"]
            student["codeforces_rank"] = info["rank"]
            if info["rating"] > 0:
                print(f"-> Codeforces match: {student['name']} is a {info['rank']} (Rating: {info['rating']})")

    # 2. Query GitHub repo counts in parallel
    print("\nQuerying GitHub API for repository counts...")
    
    def process_github(s):
        gh_user = s.get("github_username", "").strip()
        if gh_user and gh_user.lower() not in {"nil", "none", "url", "-"}:
            repos = get_github_repos(gh_user)
            if repos is not None:
                return s, repos
        return None
        
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_github, s) for s in students]
        for future in as_completed(futures):
            res = future.result()
            if res:
                student, repos = res
                student["github_repos"] = repos
                
    # Save the enriched data back to files
    with open("knights.json", "w", encoding="utf-8") as f:
        json.dump(students, f, indent=4, ensure_ascii=False)
        
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(f"window.knightsData = {json.dumps(students, indent=4, ensure_ascii=False)};")
        
    print("\nSuccessfully enriched database with live Codeforces and GitHub statistics!")

if __name__ == "__main__":
    main()
