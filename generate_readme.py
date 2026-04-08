import csv, json, urllib.request
from datetime import datetime, timedelta, date
from collections import defaultdict

# Config
LEETCODE_USER = "vikramnegi21"
GITHUB_USER   = "vikramnegi21"
CSV_FILE      = "problems.csv"
README_FILE   = "README.md"
HEATMAP_FILE  = "heatmap.svg"

def fetch_leetcode():
    url = f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        if d.get("status") == "success":
            return {
                "total": d.get("totalSolved", 0),
                "easy": d.get("easySolved", 0),
                "medium": d.get("mediumSolved", 0),
                "hard": d.get("hardSolved", 0),
                "ranking": d.get("ranking", "N/A"),
            }
    except: pass
    return {"total":0,"easy":0,"medium":0,"hard":0,"ranking":"N/A"}

def read_csv():
    rows = []
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                rows.append({k: v.strip() for k, v in r.items()})
    except FileNotFoundError: print("CSV not found")
    return rows

def parse_date(s):
    for fmt in ["%Y-%m-%d","%d %b %Y","%d-%m-%Y"]:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except: continue
    return None

def calc_streak(problems):
    dates = set(filter(None, (parse_date(p["Date"]) for p in problems)))
    if not dates: return 0, 0
    today = date.today()
    cur = 0
    d = today
    while d in dates:
        cur += 1
        d -= timedelta(days=1)
    if cur == 0:
        d = today - timedelta(days=1)
        while d in dates:
            cur += 1
            d -= timedelta(days=1)
    
    slist = sorted(dates)
    best = cur2 = 1
    for i in range(1, len(slist)):
        if (slist[i] - slist[i-1]).days == 1:
            cur2 += 1
            best = max(best, cur2)
        else: cur2 = 1
    return cur, max(best, cur)

def pbar(done, total_goal):
    percent = min(round(done / total_goal * 100, 1), 100)
    filled = int(percent / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"`{bar}` **{percent}%** ({done}/{total_goal})"

def build_readme(problems, lc):
    now = datetime.now().strftime("%d %b %Y | %H:%M IST")
    cur_streak, best_streak = calc_streak(problems)
    topics = dict(sorted(defaultdict(int, {p["Topic"]: 0 for p in problems if p.get("Topic")}).items()))
    for p in problems: 
        if p.get("Topic"): topics[p["Topic"]] += 1
    
    plat = defaultdict(int)
    for p in problems: plat[p["Platform"]] += 1
    
    # UI Elements
    header = f"https://capsule-render.vercel.app/api?type=waving&color=auto&height=200&section=header&text=DSA%20FORGE&fontSize=80&animation=fadeIn&fontColor=ffffff&desc=Vikram%20Negi%20|%20Solving%20the%20Future&descSize=20"
    
    L = [
        f'<div align="center">\n\n![]({header})\n\n',
        f'![LeetCode](https://img.shields.io/badge/LeetCode-{lc["total"]}-FFA116?style=for-the-badge&logo=leetcode&logoColor=white)',
        f'![Streak](https://img.shields.io/badge/Streak-{cur_streak}-FF7B00?style=for-the-badge&logo=github-sponsors&logoColor=white)',
        f'![Total](https://img.shields.io/badge/Solved-{len(problems)}-2ea44f?style=for-the-badge)\n\n',
        "</div>\n\n---",
        "## 📊 Technical Stats",
        '<div align="center">',
        f' <img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true" height="170" />',
        f' <img src="https://github-readme-streak-stats.herokuapp.com/?user={GITHUB_USER}&theme=tokyonight&hide_border=true" height="170" />',
        "</div>\n",
        "## 🏆 LeetCode Progress",
        f'<div align="center">\n <img src="https://leetcard.jacoblin.cool/{LEETCODE_USER}?theme=dark&font=Recursive&ext=heatmap" alt="LeetCode Card" />\n</div>\n',
        "## 🎯 Current Goals",
        "| Goal | Progress | Status |",
        "| :--- | :--- | :--- |",
        f"| **Striver A2Z Sheet** | {pbar(len(problems), 455)} | 🚀 Grinding |",
        f"| **LeetCode 500+** | {pbar(lc['total'], 500)} | 🧩 Solving |",
        f"| **30 Days Streak** | {pbar(cur_streak, 30)} | {'🔥 Active' if cur_streak > 0 else '🧊 Start'} |",
        "\n## 🧩 Problem Breakdown",
        "| Topic | Solved | Difficulty Split |",
        "| :--- | :---: | :--- |"
    ]
    
    for t, c in sorted(topics.items(), key=lambda x: -x[1]):
        L.append(f"| {t} | `{c}` | {'🟢'*(c//5) if c>0 else '⚪'} |")
    
    L.append("\n## 📅 Recent Activity")
    L.append("| Date | Problem | Platform | Difficulty |")
    L.append("| :--- | :--- | :--- | :---: |")
    for p in sorted(problems, key=lambda x: parse_date(x["Date"]) or date.min, reverse=True)[:5]:
        L.append(f"| `{p['Date']}` | [{p['Problem']}]({p['Link']}) | {p['Platform']} | `{p['Difficulty']}` |")

    L.append(f'\n<br/><div align="center">**Last Updated:** {now}</div>')
    return "\n".join(L)

def main():
    lc = fetch_leetcode()
    problems = read_csv()
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(build_readme(problems, lc))
    print("README Updated Successfully!")

if __name__ == "__main__":
    main()
        
