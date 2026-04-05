#!/usr/bin/env python3
import csv
import requests
import os
from datetime import datetime, timedelta, date
from collections import defaultdict

# --- CONFIG ---
LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"

# --- DATE PARSE ---
def parse_date(raw):
    raw = raw.strip()
    if not raw:
        return None
    today = date.today()
    # CSV format assumed: "27 Mar"
    # Hum current year add karke parse karenge
    for year in [today.year, today.year - 1]:
        try:
            d = datetime.strptime(f"{raw} {year}", "%d %b %Y").date()
            if d <= today:
                return d
        except:
            pass
    return None

# --- LOAD CSV ---
def load_problems():
    rows = []
    if not os.path.exists("problems.csv"):
        print("❌ ERROR: problems.csv file nahi mili!")
        return rows
        
    with open("problems.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = parse_date(row.get("Date", ""))
            if d:
                row["parsed_date"] = d
                rows.append(row)
    return rows

# --- STREAK CALCULATION ---
def calc_streak(problems):
    dates = {p["parsed_date"] for p in problems}
    if not dates:
        return 0
    cur = 0
    d = date.today()
    # Agar aaj problem nahi ki, toh kal se check karo (grace period)
    if d not in dates:
        d -= timedelta(days=1)
        
    while d in dates:
        cur += 1
        d -= timedelta(days=1)
    return cur

# --- GITHUB STATS ---
def github_contributions():
    token = os.getenv("GH_TOKEN")
    if not token:
        print("⚠️ Warning: GH_TOKEN nahi mila, GitHub stats 0 aayenge.")
        return 0

    query = f"""
    query {{
      user(login: "{GITHUB_USER}") {{
        contributionsCollection {{
          contributionCalendar {{
            totalContributions
          }}
        }}
      }}
    }}
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.post("https://api.github.com/graphql",
                            json={"query": query}, headers=headers)
        return res.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except:
        return 0

# --- LEETCODE STATS ---
def leetcode_stats():
    try:
        res = requests.get(f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}")
        return res.json().get("totalSolved", 0)
    except:
        return 0

# --- CODEFORCES RATING ---
def cf_rating():
    try:
        res = requests.get(f"https://codeforces.com/api/user.info?handles={CF_USER}")
        return res.json()["result"][0].get("rating", 0)
    except:
        return 0

# --- HEATMAP GENERATOR ---
def generate_heatmap(problems):
    date_counts = defaultdict(int)
    for p in problems:
        date_counts[p["parsed_date"]] += 1

    today = date.today()
    start = today - timedelta(days=90)

    rects = ""
    d = start
    i = 0
    while d <= today:
        cnt = date_counts.get(d, 0)
        x = (i // 7) * 15
        y = (i % 7) * 15
        # Green color if solved, else dark grey
        color = "#39d353" if cnt > 0 else "#161b22"
        rects += f'<rect x="{x}" y="{y}" width="10" height="10" fill="{color}" rx="2" ry="2"/>'
        d += timedelta(days=1)
        i += 1

    return f'<svg width="450" height="110" xmlns="http://www.w3.org/2000/svg">{rects}</svg>'

# --- BUILD README ---
def build_readme(problems):
    total = len(problems)
    streak = calc_streak(problems)
    lc = leetcode_stats()
    cf = cf_rating()
    gh = github_contributions()
    
    # SVG Heatmap save karna
    heatmap_svg = generate_heatmap(problems)
    with open("heatmap.svg", "w") as f:
        f.write(heatmap_svg)

    now_ist = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d %b %Y, %I:%M %p")

    content = f"""# 🚀 DSA Dashboard

> Last updated: {now_ist} (IST)

## 👨‍💻 Stats

- 🧠 LeetCode: **{lc} problems**
- ⚔️ Codeforces Rating: **{cf}**
- 🟩 GitHub Contributions: **{gh}**
- 🔥 Current Streak: **{streak} days**
- 📊 Total Problems Logged: **{total}**

---

## 📊 Last 90 Days Activity
![Heatmap](heatmap.svg)

---

## 📁 Recent Problem Log

| Date | Problem | Platform |
|------|--------|----------|
"""
    # Sirf top 10 recent problems dikhane ke liye
    recent_problems = sorted(problems, key=lambda x: x['parsed_date'], reverse=True)[:10]
    for p in recent_problems:
        content += f"| {p['Date']} | {p['Problem']} | {p['Platform']} |\n"
    
    return content

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- 🛠️ Starting README Update Script ---")
    
    problems = load_problems()
    print(f"DEBUG: CSV se total {len(problems)} problems mili hain.")
    
    if len(problems) == 0:
        print("⚠️ WARNING: 0 problems mili! Apni CSV mein 'Date' format check karein (Ex: 27 Mar).")

    readme_content = build_readme(problems)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("✅ SUCCESS: README.md aur heatmap.svg update ho gaye hain.")
    
