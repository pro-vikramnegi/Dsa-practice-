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
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            return data["data"]["matchedUser"]["userCalendar"]["streak"]
    except: return 0

def get_csv_stats():
    problems = []
    if os.path.exists("problems.csv"):
        with open("problems.csv", mode="r", encoding="utf-8") as f:
            # Skip empty lines and count real data
            reader = csv.DictReader(f)
            for row in reader:
                if any(row.values()): # Only add if row is not empty
                    problems.append({k.strip(): v.strip() for k, v in row.items() if k})
    return problems

def main():
    problems = get_csv_stats()
    striver_done = len(problems) # Ye tere 88 questions ginega automatically
    streak = fetch_leetcode_streak()
    
    stats = {
        "striver_done": striver_done,
        "striver_total": STRIVER_TOTAL,
        "lc_streak": streak,
        "last_updated": datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime("%d %b %Y | %I:%M %p"),
        "recent": problems[-8:][::-1] # Latest 8 for the table
    }
    
    with open("data.json", "w") as f:
        json.dump(stats, f, indent=4)
    print(f"Success! {striver_done} questions synced.")

if __name__ == "__main__":
    main()
    
