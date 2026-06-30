import requests
import json
import time

# Selection of prominent LeetCode handles from the provided CIT roster OCR
HANDLES = [
    "HarshanAlagarsamy", "Reth-331", "srinidhi918", "AbdulAzim77", "Abdulhafeel_10", 
    "Abinaya6662422", "Abi_KinJoy", "ryoUaQAKNN", "abishe_k2006", "ABIVARMAN1", 
    "ajiesh_eniyan", "Akalya0512", "AKASSH_M", "Akshaya450", "AkshayaCrest", 
    "Ariharasudan", "arthiganapathi", "Aravindarul", "Arunadevi-A", "Arv+D25+C2:D32", 
    "Saintjesus", "ash_vish3", "k8WLsF3kDJ", "ACHU_ASWIN1230", "athirai__Arulkumar08", 
    "Pavithra080406", "Badhri_Prasath_D_R", "Badrinath_TV", "BALAMURUGANK_07", 
    "Bharkavi_12", "Bhavana_R2006", "itzsudarshan_07", "charshavardhanaleetcode", 
    "fuzail_4116", "Abishek_K_07", "abrxxr", "ajai-26", "Ak", "amizh_than", 
    "Ananya_ibhan", "Arul_Aravind", "Adarrsh7", "Akashinoxd10", "AKSHITA-B", 
    "Sonia_26", "Ash_REXIT", "BL ROSHAN", "afnansharmeencsbs", "Klency_Antony", 
    "samfrancis95", "_aarya_", "abishekag", "Adithya-05", "gayaa835", "UZnxAiBa9a", 
    "Mohitha_annamalai", "Nehashree22", "Ramkarthick18", "Aadhirsha_s", "yescode4534as", 
    "Mastlikesh", "Aberlin2006", "_Abishek_1", "Abrar Ahamed N", "Rishi_06", 
    "chenthilashwin", "_Abarna_19_", "ABHIJEETH-VN", "am_adi", "adithya-ajay", 
    "aishu_1215", "ABISHEK_J07", "abishek_vlsi", "EpicAmy", "akhilesh_marimuthu",
    "aswinnath123", "sujan-p", "gokul-kishore", "deblina-boral", "sarguru02"
]

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
            
            # Fetch solved count
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
                
                # LeetCode Guardian threshold is top 5% of active users, practically rating 2190+
                # Knight threshold is top 25%, practically rating 1850+
                badge = "Standard User"
                if rating >= 2190:
                    badge = "Guardian"
                elif rating >= 1850:
                    badge = "Knight"
                    
                return {
                    "username": username,
                    "rating": rating,
                    "global_rank": global_rank,
                    "top_percentage": top_percent,
                    "solved": solved,
                    "badge": badge
                }
    except Exception as e:
        pass
    return None

def main():
    print("Scanning LeetCode API for CIT student achievements...\n")
    guardians = []
    knights = []
    others = []
    
    for handle in HANDLES:
        print(f"Checking: {handle}...")
        info = check_leetcode_user(handle)
        if info:
            if info["badge"] == "Guardian":
                guardians.append(info)
                print(f"--> FOUND GUARDIAN! Rating: {info['rating']}")
            elif info["badge"] == "Knight":
                knights.append(info)
                print(f"--> Found Knight! Rating: {info['rating']}")
            else:
                others.append(info)
        time.sleep(0.2) # sleep to avoid rate limits
        
    print("\n" + "="*50)
    print("CIT LEETCODE ARENA RESULTS")
    print("="*50)
    
    print(f"\nGuardian Badge Holders ({len(guardians)}):")
    for g in guardians:
        print(f"- {g['username']} | Rating: {g['rating']} | Global Rank: {g['global_rank']} | Solved: {g['solved']}")
        
    print(f"\nKnight Badge Holders ({len(knights)}):")
    for k in knights:
        print(f"- {k['username']} | Rating: {k['rating']} | Top Percentage: {k['top_percentage']}% | Solved: {k['solved']}")

if __name__ == "__main__":
    main()
