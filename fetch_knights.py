import json
import time
from serpapi import GoogleSearch

API_KEY = "432806e0fc541323776fa174bf6d5ebabb0f3358002df1c9419db63179dfc2cb"

def fetch_results():
    params = {
        "engine": "google",
        "q": 'site:linkedin.com "Chennai Institute of Technology" "LeetCode" "Knight"',
        "api_key": API_KEY,
        "num": 100,
        "start": 0
    }
    
    all_posts = []
    page = 1
    
    while True:
        print(f"Fetching page {page}...")
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            print(f"Error encountered: {results['error']}")
            break
            
        organic = results.get("organic_results", [])
        if not organic:
            print("No organic results found on this page.")
            break
            
        all_posts.extend(organic)
        print(f"Retrieved {len(organic)} posts from page {page}.")
        
        if "next" in results.get("serpapi_pagination", {}):
            params["start"] += 100
            page += 1
            # Add a small delay to respect rate limits
            time.sleep(1)
        else:
            break
            
    print(f"Total posts retrieved: {len(all_posts)}")
    return all_posts

def main():
    posts = fetch_results()
    
    # Save the raw results
    with open("knights_raw.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)
        
    print("Raw search results saved to knights_raw.json")

if __name__ == "__main__":
    main()
