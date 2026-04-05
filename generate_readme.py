#!/usr/bin/env python3
"""
DSA Forge — README Generator
problems.csv → README.md + heatmap.svg
"""

import csv
from datetime import datetime, timedelta, date
from collections import defaultdict

# ── Config ─────────────────────────────────────────────────────────────────

LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"
REPO_NAME     = "Dsa-practice-"
HEATMAP_DAYS  = 90

# ── Date Parsing ───────────────────────────────────────────────────────────

def parse_date(raw: str):
    raw = raw.strip()
    if not raw:
        return None
    today = date.today()
    for year in [today.year, today.year - 1]:
        try:
            d = datetime.strptime(f"{raw} {year}", "%d %b %Y").date()
            if d <= today:
                return d
        except ValueError:
            continue
    return None

# ── Load CSV ───────────────────────────────────────────────────────────────

def load_problems(path="problems.csv"):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            d = parse_date(row.get("Date", ""))
            if d:
                row["parsed_date"] = d
                rows.append(row)
    return rows

# ── Streaks ────────────────────────────────────────────────────────────────

def calc_streaks(problems):
    date_set = {p["parsed_date"] for p in problems}
    if not date_set:
        return 0, 0
    sorted_dates = sorted(date_set)
    max_s = cur_s = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            cur_s += 1
            max_s = max(max_s, cur_s)
        else:
            cur_s = 1
    today = date.today()
    cur = 0
    d = today
    while d in date_set:
        cur += 1
        d -= timedelta(days=1)
    if cur == 0:
        d = today - timedelta(days=1)
        while d in date_set:
            cur += 1
            d -= timedelta(days=1)
    return cur, max_s

# ── Heatmap SVG ────────────────────────────────────────────────────────────

def generate_heatmap(problems, days=90):
    date_counts = defaultdict(int)
    for p in problems:
        date_counts[p["parsed_date"]] += 1

    today = date.today()
    start = today - timedelta(days=days - 1)
    start_sun = start - timedelta(days=(start.weekday() + 1) % 7)

    cells = []
    d = start_sun
    while d <= today:
        cells.append((d, date_counts.get(d, 0)))
        d += timedelta(days=1)

    num_cols = (len(cells) + 6) // 7
    CS, GAP, ML, MT = 13, 3, 26, 22
    W = ML + num_cols * (CS + GAP) + 10
    H = MT + 7 * (CS + GAP) + 18

    def color(cnt, in_range):
        if not in_range: return "#0d1117"
        if cnt == 0:     return "#161b22"
        if cnt == 1:     return "#0e4429"
        if cnt == 2:     return "#006d32"
        if cnt == 3:     return "#26a641"
        return "#39d353"

    rects, month_labels, prev_month = [], [], None
    for i, (dt, cnt) in enumerate(cells):
        col, row = i // 7, i % 7
        in_range = start <= dt <= today
        x = ML + col * (CS + GAP)
        y = MT + row * (CS + GAP)
        tip = f"{dt.strftime('%d %b')}: {cnt} problem{'s' if cnt != 1 else ''}"
        rects.append(
            f'<rect x="{x}" y="{y}" width="{CS}" height="{CS}" rx="2" '
            f'fill="{color(cnt, in_range)}"><title>{tip}</title></rect>'
        )
        if in_range and dt.month != prev_month:
            month_labels.append(
                f'<text x="{x}" y="{MT-6}" fill="#8b949e" font-size="10" '
                f'font-family="monospace">{dt.strftime("%b")}</text>'
            )
            prev_month = dt.month

    day_svgs = [
        f'<text x="{ML-4}" y="{MT+r*(CS+GAP)+CS-2}" fill="#8b949e" '
        f'font-size="9" font-family="monospace" text-anchor="end">{lb}</text>'
        for r, lb in [(0,"Sun"),(2,"Tue"),(4,"Thu"),(6,"Sat")]
    ]
    lx = W - 5*(CS+GAP) - 10
    ly = H - CS - 4
    legend = "".join(
        f'<rect x="{lx+i*(CS+GAP)}" y="{ly}" width="{CS}" height="{CS}" rx="2" fill="{c}"/>'
        for i, c in enumerate(["#161b22","#0e4429","#006d32","#26a641","#39d353"])
    )
    legend += (
        f'<text x="{lx-4}" y="{ly+CS-2}" fill="#8b949e" font-size="9" '
        f'font-family="monospace" text-anchor="end">Less</text>'
        f'<text x="{lx+5*(CS+GAP)}" y="{ly+CS-2}" fill="#8b949e" '
        f'font-size="9" font-family="monospace">More</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'style="background:#0d1117;border-radius:6px;padding:4px">'
        f'{"".join(month_labels)}{"".join(day_svgs)}{"".join(rects)}{legend}</svg>'
    )

# ── README Builder ─────────────────────────────────────────────────────────

def build_readme(problems):
    today = date.today()

    total  = len(problems)
    lc     = [p for p in problems if p["Platform"] == "LeetCode"]
    cf     = [p for p in problems if p["Platform"] == "Codeforces"]
    easy   = sum(1 for p in lc if p["Difficulty"] == "Easy")
    medium = sum(1 for p in lc if p["Difficulty"] == "Medium")
    hard   = sum(1 for p in lc if p["Difficulty"] == "Hard")
    done   = sum(1 for p in problems if p["Status"] == "Done")
    rev    = [p for p in problems if p["Status"] == "Revision"]

    topic_counts = defaultdict(int)
    for p in problems:
        topic_counts[p["Topic"]] += 1

    cf_by_rating = defaultdict(int)
    for p in cf:
        cf_by_rating[p["Difficulty"]] += 1

    cur_streak, max_streak = calc_streaks(problems)

    svg = generate_heatmap(problems, HEATMAP_DAYS)
    with open("heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    L = []
    def line(s=""): L.append(s)

    # ── Title ──────────────────────────────────────────────────────────────
    line("# DSA Practice")
    line()
    line(
        f"[![LeetCode](https://img.shields.io/badge/LeetCode-{LEETCODE_USER}-FFA116?style=flat-square&logo=leetcode&logoColor=black)]"
        f"(https://leetcode.com/u/{LEETCODE_USER}/) "
        f"[![Codeforces](https://img.shields.io/badge/Codeforces-{CF_USER}-1F8ACB?style=flat-square&logo=codeforces&logoColor=white)]"
        f"(https://codeforces.com/profile/{CF_USER}) "
        f"[![Problems](https://img.shields.io/badge/Problems%20Solved-{total}-success?style=flat-square)]"
        f"(https://github.com/{GITHUB_USER}/{REPO_NAME}) "
        f"[![Streak](https://img.shields.io/badge/Current%20Streak-{cur_streak}%20days-orange?style=flat-square)](https://github.com/{GITHUB_USER}/{REPO_NAME})"
    )
    line()
    line("Documenting my daily DSA practice. Solving problems from Striver's A2Z Sheet on LeetCode and building competitive programming skills on Codeforces — consistently, every day.")
    line()
    line("---")
    line()

    # ── Stats ──────────────────────────────────────────────────────────────
    line("## Stats")
    line()
    line("| | LeetCode | Codeforces | Total |")
    line("|---|:---:|:---:|:---:|")
    line(f"| **Problems Solved** | {len(lc)} | {len(cf)} | **{total}** |")
    line(f"| **Easy / Medium / Hard** | {easy} / {medium} / {hard} | — | — |")
    line(f"| **Current Streak** | — | — | **{cur_streak} days** |")
    line(f"| **Longest Streak** | — | — | **{max_streak} days** |")
    line(f"| **Pending Revision** | — | — | {len(rev)} |")
    line()
    if cf_by_rating:
        ratings = sorted(cf_by_rating.keys())
        line("**Codeforces breakdown:** " + " · ".join(
            f"Rating {r}: {cf_by_rating[r]}" for r in ratings
        ))
        line()

    # ── Activity ───────────────────────────────────────────────────────────
    line("## Activity")
    line()
    line("![Heatmap](heatmap.svg)")
    line()

    # ── Goals ──────────────────────────────────────────────────────────────
    line("## Goals")
    line()
    goals = [
        ("Complete Striver's A2Z DSA Sheet",     455,  len(lc)),
        ("Solve 500+ problems on LeetCode",       500,  len(lc)),
        ("Reach 1000+ rating on Codeforces",     1000,  None),
        ("Maintain a 30-day solve streak",          30,  cur_streak),
    ]
    line("| Goal | Progress | Status |")
    line("|------|----------|--------|")
    for label, target, val in goals:
        if val is None:
            line(f"| {label} | Tracked manually | — |")
            continue
        pct = min(int(val / target * 100), 100)
        filled = round(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        status = "✓ Done" if pct >= 100 else f"{pct}%"
        line(f"| {label} | `{bar}` {val}/{target} | {status} |")
    line()

    # ── Revision ───────────────────────────────────────────────────────────
    if rev:
        line("## Pending Revision")
        line()
        line("| # | Problem | Platform | Topic |")
        line("|---|---------|----------|-------|")
        for i, p in enumerate(rev, 1):
            line(f"| {i} | {p['Problem']} | {p['Platform']} | {p['Topic']} |")
        line()

    # ── Problem Log ────────────────────────────────────────────────────────
    line("## Problem Log")
    line()
    line(f"<details>")
    line(f"<summary>All {total} problems</summary>")
    line()
    line("| Date | Problem | Platform | Difficulty | Topic | Status |")
    line("|------|---------|----------|------------|-------|--------|")
    for p in sorted(problems, key=lambda x: x["parsed_date"], reverse=True):
        status = "Done" if p["Status"] == "Done" else "Revision"
        line(
            f"| {p['Date']} | {p['Problem']} | {p['Platform']} "
            f"| {p['Difficulty']} | {p['Topic']} | {status} |"
        )
    line()
    line("</details>")
    line()
    line("---")
    line()
    line(f"*Last updated: {today.strftime('%d %b %Y')} · Auto-generated via GitHub Actions*")

    return "\n".join(L)

# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    problems = load_problems()
    readme   = build_readme(problems)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"Done — {len(problems)} problems · README.md + heatmap.svg updated")
