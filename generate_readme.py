#!/usr/bin/env python3
"""
DSA Forge — Auto README Generator
Reads problems.csv → generates README.md + heatmap.svg
"""

import csv
from datetime import datetime, timedelta, date
from collections import defaultdict


# ─── Config ────────────────────────────────────────────────────────────────

LEETCODE_USER  = "__vikram21"
CF_USER        = "__vikram21"
GITHUB_USER    = "Vikram-353"
REPO_NAME      = "Dsa-practice"
HEATMAP_DAYS   = 90

# Goals — edit as you progress
GOALS = [
    ("150 LeetCode problems",        150, "lc_total"),
    ("50 Codeforces problems",        50, "cf_total"),
    ("Complete Linked List topic",    15, "topic_Linked_List"),
    ("Complete Array topic",          20, "topic_Array"),
    ("Complete Matrix topic",         10, "topic_Matrix"),
    ("Reach 30-day streak",           30, "streak"),
]


# ─── Date Parsing ──────────────────────────────────────────────────────────

def parse_date(raw: str) -> date | None:
    raw = raw.strip()
    if not raw:
        return None
    today = date.today()
    for year in [today.year, today.year - 1]:
        try:
            d = datetime.strptime(f"{raw} {year}", "%d %b %Y").date()
            if d <= today:          # never return a future date
                return d
        except ValueError:
            continue
    return None


# ─── Load CSV ──────────────────────────────────────────────────────────────

def load_problems(path="problems.csv") -> list[dict]:
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


# ─── Streak ────────────────────────────────────────────────────────────────

def calc_streaks(problems: list[dict]) -> tuple[int, int]:
    date_set = {p["parsed_date"] for p in problems}
    if not date_set:
        return 0, 0

    sorted_dates = sorted(date_set)

    # longest streak
    max_s = cur_s = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            cur_s += 1
            max_s = max(max_s, cur_s)
        else:
            cur_s = 1

    # current streak (allow yesterday as "alive")
    today = date.today()
    cur_streak = 0
    d = today
    while d in date_set:
        cur_streak += 1
        d -= timedelta(days=1)
    if cur_streak == 0:           # nothing today — try from yesterday
        d = today - timedelta(days=1)
        while d in date_set:
            cur_streak += 1
            d -= timedelta(days=1)

    return cur_streak, max_s


# ─── Heatmap SVG ───────────────────────────────────────────────────────────

def generate_heatmap(problems: list[dict], days: int = 90) -> str:
    date_counts: dict[date, int] = defaultdict(int)
    for p in problems:
        date_counts[p["parsed_date"]] += 1

    today = date.today()
    start = today - timedelta(days=days - 1)

    # align to the Sunday before start
    # Python weekday(): Mon=0 … Sun=6  →  Sunday offset: (weekday+1)%7
    start_sun = start - timedelta(days=(start.weekday() + 1) % 7)

    cells: list[tuple[date, int]] = []
    d = start_sun
    while d <= today:
        cells.append((d, date_counts.get(d, 0)))
        d += timedelta(days=1)

    num_cols = (len(cells) + 6) // 7
    CS = 13        # cell size
    GAP = 3        # gap
    ML = 26        # margin left (day labels)
    MT = 22        # margin top (month labels)

    W = ML + num_cols * (CS + GAP) + 10
    H = MT + 7 * (CS + GAP) + 14

    def cell_color(count: int, in_range: bool) -> str:
        if not in_range:
            return "#0d1117"
        if count == 0: return "#161b22"
        if count == 1: return "#0e4429"
        if count == 2: return "#006d32"
        if count == 3: return "#26a641"
        return "#39d353"

    rects = []
    prev_month = None
    month_labels = []

    for i, (dt, cnt) in enumerate(cells):
        col = i // 7
        row = i % 7
        in_range = start <= dt <= today
        x = ML + col * (CS + GAP)
        y = MT + row * (CS + GAP)
        c = cell_color(cnt, in_range)
        tip = f"{dt.strftime('%d %b')}: {cnt} problem{'s' if cnt != 1 else ''}"
        rects.append(
            f'<rect x="{x}" y="{y}" width="{CS}" height="{CS}" rx="2" '
            f'fill="{c}"><title>{tip}</title></rect>'
        )
        if in_range and dt.month != prev_month:
            month_labels.append(
                f'<text x="{x}" y="{MT - 6}" fill="#8b949e" '
                f'font-size="10" font-family="monospace">'
                f'{dt.strftime("%b")}</text>'
            )
            prev_month = dt.month

    day_labels = [
        (0, "Sun"), (2, "Tue"), (4, "Thu"), (6, "Sat")
    ]
    day_svgs = [
        f'<text x="{ML - 4}" y="{MT + r*(CS+GAP) + CS - 2}" fill="#8b949e" '
        f'font-size="9" font-family="monospace" text-anchor="end">{lbl}</text>'
        for r, lbl in day_labels
    ]

    # legend
    legend_x = W - 5 * (CS + GAP) - 10
    legend_y = H - CS - 4
    legend_colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    legend_rects = "".join(
        f'<rect x="{legend_x + i*(CS+GAP)}" y="{legend_y}" width="{CS}" '
        f'height="{CS}" rx="2" fill="{c}"/>'
        for i, c in enumerate(legend_colors)
    )
    legend_labels = (
        f'<text x="{legend_x - 4}" y="{legend_y + CS - 2}" fill="#8b949e" '
        f'font-size="9" font-family="monospace" text-anchor="end">Less</text>'
        f'<text x="{legend_x + 5*(CS+GAP)}" y="{legend_y + CS - 2}" '
        f'fill="#8b949e" font-size="9" font-family="monospace">More</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'style="background:#0d1117;border-radius:8px;padding:4px">\n'
        f'{"".join(month_labels)}\n'
        f'{"".join(day_svgs)}\n'
        f'{"".join(rects)}\n'
        f'{legend_rects}{legend_labels}\n'
        f'</svg>'
    )


# ─── Progress Bar ──────────────────────────────────────────────────────────

def progress_bar(value: int, goal: int, width: int = 20) -> str:
    pct  = min(value / goal, 1.0) if goal else 0
    done = round(pct * width)
    bar  = "█" * done + "░" * (width - done)
    return f"`{bar}` {value}/{goal} ({int(pct*100)}%)"


# ─── README Builder ────────────────────────────────────────────────────────

def build_readme(problems: list[dict]) -> str:
    today = date.today()

    # ── aggregate ──────────────────────────────────────────────────────────
    total  = len(problems)
    lc     = [p for p in problems if p["Platform"] == "LeetCode"]
    cf     = [p for p in problems if p["Platform"] == "Codeforces"]
    easy   = sum(1 for p in lc if p["Difficulty"] == "Easy")
    medium = sum(1 for p in lc if p["Difficulty"] == "Medium")
    hard   = sum(1 for p in lc if p["Difficulty"] == "Hard")
    done   = sum(1 for p in problems if p["Status"] == "Done")
    rev    = [p for p in problems if p["Status"] == "Revision"]

    cf_by_rating: dict[str, int] = defaultdict(int)
    for p in cf:
        cf_by_rating[p["Difficulty"]] += 1

    topic_counts: dict[str, int] = defaultdict(int)
    for p in problems:
        topic_counts[p["Topic"]] += 1

    cur_streak, max_streak = calc_streaks(problems)

    # context dict for goals
    ctx = {
        "lc_total"           : len(lc),
        "cf_total"           : len(cf),
        "streak"             : cur_streak,
        **{f"topic_{k}": v for k, v in topic_counts.items()},
    }

    # ── heatmap ────────────────────────────────────────────────────────────
    svg = generate_heatmap(problems, HEATMAP_DAYS)
    with open("heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    # ── build lines ────────────────────────────────────────────────────────
    L: list[str] = []

    def line(s=""):
        L.append(s)

    # Header
    line(f"# 🔥 DSA Forge")
    line()
    line(
        f"[![LeetCode](https://img.shields.io/badge/LeetCode-{LEETCODE_USER}-FFA116?style=flat&logo=leetcode&logoColor=black)]"
        f"(https://leetcode.com/u/{LEETCODE_USER}/)  "
        f"[![Codeforces](https://img.shields.io/badge/Codeforces-{CF_USER}-1F8ACB?style=flat&logo=codeforces&logoColor=white)]"
        f"(https://codeforces.com/profile/{CF_USER})  "
        f"[![GitHub](https://img.shields.io/badge/GitHub-{REPO_NAME}-181717?style=flat&logo=github)]"
        f"(https://github.com/{GITHUB_USER}/{REPO_NAME})  "
        f"![Problems](https://img.shields.io/badge/Solved-{total}%20problems-brightgreen?style=flat)  "
        f"![Streak](https://img.shields.io/badge/🔥%20Streak-{cur_streak}%20days-orange?style=flat)"
    )
    line()

    # Summary stats
    line("## 📊 Stats")
    line()
    line("| 🎯 Total Solved | ✅ Done | 🔄 Revision | 🔥 Current Streak | 🏆 Longest Streak |")
    line("|:-:|:-:|:-:|:-:|:-:|")
    line(f"| **{total}** | **{done}** | **{len(rev)}** | **{cur_streak} days** | **{max_streak} days** |")
    line()
    line("| 💛 LeetCode | ⚡ Codeforces | 🟢 Easy | 🟡 Medium | 🔴 Hard |")
    line("|:-:|:-:|:-:|:-:|:-:|")
    line(f"| **{len(lc)}** | **{len(cf)}** | **{easy}** | **{medium}** | **{hard}** |")
    line()

    # CF ratings table
    if cf_by_rating:
        ratings = sorted(cf_by_rating.keys())
        line("**Codeforces by Rating:**  " + "  ".join(
            f"`{r}` × {cf_by_rating[r]}" for r in ratings
        ))
        line()

    # Activity heatmap
    line("## 📅 Activity — Last 90 Days")
    line()
    line("![Activity Heatmap](heatmap.svg)")
    line()

    # Topic progress
    line("## 🧩 Topics")
    line()
    max_topic_count = max(topic_counts.values(), default=1)
    topic_sorted = sorted(topic_counts.items(), key=lambda x: -x[1])
    line("| Topic | Progress | Count |")
    line("|-------|----------|-------|")
    for topic, count in topic_sorted:
        bar = progress_bar(count, max_topic_count, 15)
        line(f"| `{topic}` | {bar} | **{count}** |")
    line()

    # Goals
    line("## 🎯 Goals")
    line()
    for label, target, key in GOALS:
        val = ctx.get(key, 0)
        pct = min(int(val / target * 100), 100) if target else 100
        done_mark = "✅" if pct >= 100 else "🔲"
        bar = progress_bar(val, target, 12)
        line(f"- {done_mark} **{label}** — {bar}")
    line()

    # Revision list
    if rev:
        line("## 🔄 Needs Revision")
        line()
        line("| # | Problem | Platform | Difficulty | Topic |")
        line("|---|---------|----------|------------|-------|")
        for i, p in enumerate(rev, 1):
            line(f"| {i} | {p['Problem']} | {p['Platform']} | {p['Difficulty']} | `{p['Topic']}` |")
        line()

    # Full problems table (newest first)
    line("## 📋 All Problems")
    line()
    line(f"<details><summary>Click to expand ({total} problems)</summary>")
    line()
    line("| Date | Problem | Platform | Difficulty | Topic | Status |")
    line("|------|---------|----------|------------|-------|--------|")
    for p in sorted(problems, key=lambda x: x["parsed_date"], reverse=True):
        emoji = "✅" if p["Status"] == "Done" else "🔄"
        line(
            f"| {p['Date']} | {p['Problem']} | {p['Platform']} "
            f"| {p['Difficulty']} | `{p['Topic']}` | {emoji} |"
        )
    line()
    line("</details>")
    line()

    # Footer
    line("---")
    line(
        f"*Last updated: **{today.strftime('%d %b %Y')}** · "
        f"Auto-generated from [problems.csv](problems.csv) via GitHub Actions*"
    )

    return "\n".join(L)


# ─── Main ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    problems = load_problems()
    readme   = build_readme(problems)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"✅  README.md generated  ({len(problems)} problems)")
    print(f"✅  heatmap.svg generated")
