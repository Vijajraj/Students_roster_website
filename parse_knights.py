import json
import re

def clean_name(source):
    if source and "LinkedIn" in source:
        name = source.replace("LinkedIn", "").strip()
        name = re.sub(r"^[^a-zA-Z0-9\s]+", "", name).strip()
        name = re.sub(r"^[\s\·\-\•\u00b7\u00a0\W]+", "", name).strip()
        return name
    return None

def extract_stats(text):
    stats = {
        "leetcode_rating": None,
        "solved_count": None,
        "codechef_stars": None,
        "other_badges": []
    }
    
    if not text:
        return stats
        
    rating_match = re.search(r"Rating\s*[:\-–]?\s*(\d{4})|Knight\s*\(?(\d{4})\+?\)?", text, re.IGNORECASE)
    if rating_match:
        stats["leetcode_rating"] = rating_match.group(1) or rating_match.group(2)
        
    solved_match = re.search(r"(\d{3,4}\+?)\s*(?:problems|questions|solutions)?\s*solved|solved\s*(\d{3,4}\+?)", text, re.IGNORECASE)
    if solved_match:
        stats["solved_count"] = solved_match.group(1) or solved_match.group(2)
        
    cc_match = re.search(r"(\d\s*★|★\s*\d|\d-star|\d\s*Star)\s*@?\s*CodeChef", text, re.IGNORECASE)
    if cc_match:
        stats["codechef_stars"] = cc_match.group(1).strip()
        
    cf_match = re.search(r"Codeforces\s+(\w+)", text, re.IGNORECASE)
    if cf_match:
        stats["other_badges"].append(f"Codeforces {cf_match.group(1)}")
        
    return stats

def parse_posts():
    with open("knights_raw.json", "r", encoding="utf-8") as f:
        posts = json.load(f)
        
    parsed_knights = []
    seen_profiles = set()
    
    blacklist = {
        "india", "ecuador", "guatemala", "bolivia", "pakistan", "nepal", "bangladesh", 
        "sri lanka", "linkedin", "posts", "post", "chennai", "chennai institute of technology", 
        "cit", "coimbatore", "tamil nadu", "united states", "united kingdom", "canada", "australia"
    }
    
    for p in posts:
        link = p.get("link", "")
        if "linkedin.com" not in link:
            continue
            
        source = p.get("source", "")
        author_name = clean_name(source)
        
        title = p.get("title", "")
        snippet = p.get("snippet", "")
        
        if not author_name or author_name.lower() in ["posts", "post", "linkedin"]:
            if "'s Post" in title:
                author_name = title.split("'s Post")[0].strip()
            elif " | " in title:
                author_name = title.split(" | ")[0].strip()
            elif " - " in title:
                author_name = title.split(" - ")[0].strip()
            else:
                author_name = "CIT LeetCoder"
        
        # Clean author name from extra text
        author_name = re.sub(r"\s*-\s*.*$", "", author_name)
        author_name = re.sub(r"\s*\|\s*.*$", "", author_name)
        author_name = author_name.split(" posted on ")[0].strip()
        
        # Filter out blacklisted or generic names
        if author_name.lower() in blacklist or len(author_name) < 3:
            continue
            
        combined_text = f"{title} | {snippet}"
        stats = extract_stats(combined_text)
        
        # Determine reactions
        reactions = "0"
        displayed_link = p.get("displayed_link", "")
        reactions_match = re.search(r"([\d\.\w\+]+)\s*reactions", displayed_link)
        if reactions_match:
            reactions = reactions_match.group(1)
            
        time_ago = "Recently"
        time_match = re.search(r"·\s*([\d\w\s]+ago)", displayed_link)
        if time_match:
            time_ago = time_match.group(1)
            
        role = "LeetCode Knight"
        if "Guardian" in combined_text:
            role = "LeetCode Guardian"
            
        # De-duplicate profiles by name
        if author_name in seen_profiles:
            for existing in parsed_knights:
                if existing["name"] == author_name:
                    if not existing["leetcode_rating"] and stats["leetcode_rating"]:
                        existing["leetcode_rating"] = stats["leetcode_rating"]
                    if not existing["solved_count"] and stats["solved_count"]:
                        existing["solved_count"] = stats["solved_count"]
                    if len(existing["other_badges"]) < len(stats["other_badges"]):
                        existing["other_badges"] = stats["other_badges"]
            continue
            
        seen_profiles.add(author_name)
        
        parsed_knights.append({
            "name": author_name,
            "post_title": title,
            "link": link,
            "snippet": snippet,
            "reactions": reactions,
            "time_ago": time_ago,
            "leetcode_rating": stats["leetcode_rating"] or "1850+",
            "solved_count": stats["solved_count"] or "500+",
            "codechef_stars": stats["codechef_stars"],
            "other_badges": stats["other_badges"],
            "role": role
        })
        
    with open("knights.json", "w", encoding="utf-8") as f:
        json.dump(parsed_knights, f, indent=4, ensure_ascii=False)
        
    # Write to data.js for CORS-free local usage
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(f"window.knightsData = {json.dumps(parsed_knights, indent=4, ensure_ascii=False)};")
        
    print(f"Parsed {len(parsed_knights)} unique knights and saved to knights.json and data.js")
    for k in parsed_knights:
        print(f"- {k['name']} | Rating: {k['leetcode_rating']} | Solved: {k['solved_count']} | Reactions: {k['reactions']}")

if __name__ == "__main__":
    parse_posts()
