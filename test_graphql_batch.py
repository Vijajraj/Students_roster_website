import requests

def test_batch():
    url = "https://leetcode.com/graphql"
    
    # We query two active handles as a test
    query = """
    query {
        u0_rank: userContestRanking(username: "AKASSH_M") {
            rating
            globalRanking
        }
        u0_solved: matchedUser(username: "AKASSH_M") {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
        u1_rank: userContestRanking(username: "Salmankhan007x") {
            rating
            globalRanking
        }
        u1_solved: matchedUser(username: "Salmankhan007x") {
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
        r = requests.post(url, json={"query": query}, timeout=10)
        print("Status code:", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("Response Keys:", list(data.get("data", {}).keys()))
            print("AKASSH_M rating:", data.get("data", {}).get("u0_rank"))
            # print("Salmankhan007x rating:", data.get("data", {}).get("u1_rank"))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_batch()
