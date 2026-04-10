import csv, json, urllib.request, os
from datetime import datetime, timedelta, timezone

# --- CONFIG ---
LEETCODE_USER = "__vikram21"
STRIVER_TOTAL = 455 

def fetch_leetcode_streak():
    url = "https://leetcode.com/graphql"
    query = "query userCal($u:String!){matchedUser(username:$u){userCalendar{streak}}}"
    payload = json.dumps({"query": query, "variables": {"u": LEETCODE_USER}}).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
            return data["data"]["matchedUser"]["userCalendar"]["streak"]
    except: return 0

def get_csv_stats():
    problems = []
    if os.path.exists("problems.csv"):
        with open("problems.csv", mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean keys just in case
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                problems.append(clean_row)
    return problems

def main():
    problems = get_csv_stats()
    # Striver Fix: Counts every row in your CSV
    striver_done = len(problems) 
    streak = fetch_leetcode_streak()
    
    stats = {
        "striver_done": striver_done,
        "striver_total": STRIVER_TOTAL,
        "lc_streak": streak,
        "last_updated": datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y | %I:%M %p IST"),
        "recent": problems[-10:][::-1] 
    }
    
    with open("data.json", "w") as f:
        json.dump(stats, f, indent=4)
    print(f"Stats Saved: {striver_done} problems found in CSV.")

if __name__ == "__main__":
    main()
  
