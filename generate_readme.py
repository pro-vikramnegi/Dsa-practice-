#!/usr/bin/env python3
import csv
import requests
import os
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

# --- CONFIG ---
LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"

def parse_date(raw):
    raw = raw.strip()
    if not raw: return None
    today = date.today()
    for year in [today.year, today.year - 1]:
        try:
            d = datetime.strptime(f"{raw} {year}", "%d %b %Y").date()
            if d <= today: return d
        except: pass
    return None

def load_problems():
    rows = []
    if not os.path.exists("problems.csv"): return rows
    with open("problems.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = parse_date(row.get("Date", ""))
            if d:
                row["parsed_date"] = d
                rows.append(row)
    return rows

def calc_streak(problems):
    dates = {p["parsed_date"] for p in problems}
    if not dates: return 0
    cur, d = 0, date.today()
    if d not in dates: d -= timedelta(days=1)
    while d in dates:
        cur += 1
        d -= timedelta(days=1)
    return cur

def get_stats():
    # LeetCode stats
    lc_solved = 0
    try:
        res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}").json()
        lc_solved = res.get("totalSolved", 0)
    except: pass
    
    # Codeforces stats
    cf_rating = 0
    try:
        res = requests.get(f"https://codeforces.com/api/user.info?handles={CF_USER}").json()
        cf_rating = res["result"][0].get("rating", 0)
    except: pass

    # GitHub contributions
    gh_contributions = 0
    token = os.getenv("GH_TOKEN")
    if token:
        query = f'query {{ user(login: "{GITHUB_USER}") {{ contributionsCollection {{ contributionCalendar {{ totalContributions }} }} }} }}'
        try:
            res = requests.post("https://api.github.com/graphql", json={"query": query}, headers={"Authorization": f"Bearer {token}"})
            gh_contributions = res.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        except: pass
        
    return lc_solved, cf_rating, gh_contributions

def generate_heatmap(problems):
    date_counts = defaultdict(int)
    for p in problems: date_counts[p["parsed_date"]] += 1
    today = date.today()
    start = today - timedelta(days=90)
    rects = ""
    d, i = start, 0
    while d <= today:
        cnt = date_counts.get(d, 0)
        x, y = (i // 7) * 15, (i % 7) * 15
        color = "#39d353" if cnt > 0 else "#161b22"
        rects += f'<rect x="{x}" y="{y}" width="11" height="11" fill="{color}" rx="2"/>'
        d += timedelta(days=1)
        i += 1
    return f'<svg width="450" height="110" xmlns="http://www.w3.org/2000/svg">{rects}</svg>'

def build_readme(problems):
    lc, cf, gh = get_stats()
    total = len(problems)
    streak = calc_streak(problems)
    consistency = min(round((streak / 30) * 100, 1), 100.0)
    
    topics = Counter(p.get("Topic", "Unknown") for p in problems)
    difficulty = Counter(p.get("Difficulty", "Unknown") for p in problems)
    
    heatmap_svg = generate_heatmap(problems)
    with open("heatmap.svg", "w") as f: f.write(heatmap_svg)

    now_ist = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | %I:%M %p")

    return f"""# 🚀 My DSA Journey

<p align="center">
  <img src="https://img.shields.io/badge/LeetCode-{lc}-FFA116?style=for-the-badge&logo=leetcode&logoColor=black">
  <img src="https://img.shields.io/badge/Codeforces-{cf}-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white">
  <img src="https://img.shields.io/badge/Streak-{streak}_Days-FF4B4B?style=for-the-badge&logo=github-actions&logoColor=white">
  <img src="https://img.shields.io/badge/Consistency-{consistency}%25-2EA043?style=for-the-badge">
</p>

---

### 📊 Personal Stats
| Metric | Value |
| :--- | :--- |
| 🧠 **Total Solved** | `{total}` Problems |
| 🟩 **GH Contributions** | `{gh}` |
| 📅 **Last Updated** | `{now_ist} IST` |

### 🟩 Activity Heatmap (Last 90 Days)
![Heatmap](heatmap.svg)

---

### 🧠 Topics Covered
{" ".join([f"`{k}({v})`" for k, v in topics.items()])}

### 📉 Difficulty Breakdown
{" ".join([f"`{k}: {v}`" for k, v in difficulty.items()])}

---

### 📁 Recent Submissions
| Date | Problem | Platform |
| :--- | :--- | :--- |
""" + "\n".join([f"| {p['Date']} | **{p['Problem']}** | `{p['Platform']}` |" for p in sorted(problems, key=lambda x: x['parsed_date'], reverse=True)[:10]])

if __name__ == "__main__":
    data = load_problems()
    readme = build_readme(data)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("✅ Best of both worlds updated!")
                
