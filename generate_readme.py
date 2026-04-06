#!/usr/bin/env python3
import csv
import requests
import os
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter

LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"


def load_problems():
    rows = []
    with open("problems.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def parse_date(date_str):
    today = date.today()
    for year in [today.year, today.year - 1]:
        try:
            d = datetime.strptime(str(date_str) + " " + str(year), "%d %b %Y").date()
            if d <= today:
                return d
        except ValueError:
            pass
    return None


def calc_streaks(problems):
    dates = set()
    for p in problems:
        d = parse_date(p["Date"])
        if d:
            dates.add(d)
    today = date.today()
    cur = 0
    start = today if today in dates else today - timedelta(days=1)
    d = start
    while d in dates:
        cur += 1
        d -= timedelta(days=1)
    best = 0
    run = 0
    prev = None
    for d in sorted(dates):
        if prev and (d - prev).days == 1:
            run += 1
        else:
            run = 1
        best = max(best, run)
        prev = d
    return cur, best


def weekly_digest(problems):
    cutoff = date.today() - timedelta(days=7)
    recent = []
    for p in problems:
        d = parse_date(p["Date"])
        if d and d >= cutoff:
            recent.append((d, p))
    recent.sort(key=lambda x: x[0], reverse=True)
    return recent


def platform_breakdown(problems):
    return Counter(p.get("Platform", "Unknown") for p in problems)


def diff_bar(easy, medium, hard):
    total = easy + medium + hard or 1
    e_pct = round((easy / total) * 10)
    m_pct = round((medium / total) * 10)
    h_pct = round((hard / total) * 10)
    return "🟢" * e_pct + "🟡" * m_pct + "🔴" * h_pct


def generate_heatmap(problems):
    counter = defaultdict(int)
    for p in problems:
        d = parse_date(p["Date"])
        if d:
            counter[d] += 1
    today = date.today()
    start = today - timedelta(days=90)
    palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
    rects = []
    d = start
    i = 0
    while d <= today:
        cnt = counter.get(d, 0)
        level = min(cnt, 4)
        x = (i // 7) * 13
        y = (i % 7) * 13
        color = palette[level]
        tip = d.strftime("%b %d")
        rects.append(
            '<rect x="' + str(x) + '" y="' + str(y) + '" width="10" height="10" '
            'fill="' + color + '" rx="2"><title>' + tip + ': ' + str(cnt) + '</title></rect>'
        )
        d += timedelta(days=1)
        i += 1
    width = ((i // 7) + 1) * 13
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="' + str(width) + '" height="104" '
        'style="background:#0d1117;padding:4px;border-radius:6px">'
        + "".join(rects)
        + "</svg>"
    )
    with open("heatmap.svg", "w") as f:
        f.write(svg)


def leetcode_stats():
    try:
        r = requests.get(
            "https://leetcode-stats-api.herokuapp.com/" + LEETCODE_USER,
            timeout=8
        )
        data = r.json()
        return {
            "total":  data.get("totalSolved",  0),
            "easy":   data.get("easySolved",   0),
            "medium": data.get("mediumSolved", 0),
            "hard":   data.get("hardSolved",   0),
            "rank":   data.get("ranking",      "N/A"),
        }
    except Exception:
        return {"total": 0, "easy": 0, "medium": 0, "hard": 0, "rank": "N/A"}


def cf_info():
    try:
        r = requests.get(
            "https://codeforces.com/api/user.info?handles=" + CF_USER,
            timeout=8
        )
        u = r.json()["result"][0]
        return {
            "rating":     u.get("rating",    0),
            "max_rating": u.get("maxRating", 0),
            "rank":       u.get("rank",      "unrated"),
        }
    except Exception:
        return {"rating": 0, "max_rating": 0, "rank": "unrated"}


def github_contributions():
    token = os.getenv("GH_TOKEN")
    if not token:
        return 0
    query = "query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar { totalContributions } } } }"
    try:
        r = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"login": GITHUB_USER}},
            headers={"Authorization": "Bearer " + token},
            timeout=8,
        )
        return r.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception:
        return 0


def img(alt, url):
    return "![" + alt + "](" + url + ")"


def build_readme(problems):
    total = len(problems)
    cur_streak, best = calc_streaks(problems)
    lc = leetcode_stats()
    cf = cf_info()
    gh = github_contributions()
    topics = Counter(p.get("Topic", "Other") for p in problems)
    difficulty = Counter(p.get("Difficulty", "Unknown") for p in problems)
    platforms = platform_breakdown(problems)
    recent = weekly_digest(problems)
    consistency = round((cur_streak / 30) * 100, 1)

    generate_heatmap(problems)

    easy = difficulty.get("Easy", 0)
    medium = difficulty.get("Medium", 0)
    hard = difficulty.get("Hard", 0)
    bar = diff_bar(easy, medium, hard)

    badges = (
        img("LeetCode", "https://img.shields.io/badge/LeetCode-" + str(lc["total"]) + "-FFA116?logo=leetcode&logoColor=white") + " "
        + img("CF", "https://img.shields.io/badge/Codeforces-" + str(cf["rating"]) + "-1F8ACB?logo=codeforces&logoColor=white") + " "
        + img("Streak", "https://img.shields.io/badge/Streak-" + str(cur_streak) + "%20days-39d353?logo=github") + " "
        + img("Total", "https://img.shields.io/badge/Problems-" + str(total) + "-blueviolet")
    )

    graph = img("Graph", "https://github-readme-activity-graph.vercel.app/graph?username=" + GITHUB_USER + "&theme=github-dark&hide_border=true")
    heatmap = img("Heatmap", "heatmap.svg")

    table_rows = "\n".join(
        "| " + p.get("Date", "-") + " | " + p.get("Problem", "-") +
        " | " + p.get("Platform", "-") + " | " + p.get("Topic", "-") +
        " | " + p.get("Difficulty", "-") + " | " + p.get("Link", "-") + " |"
        for p in reversed(problems)
    )

    if recent:
        recent_rows = "\n".join(
            "| " + d.strftime("%d %b") + " | " + p.get("Problem", "-") +
            " | " + p.get("Platform", "-") + " | " + p.get("Difficulty", "-") + " |"
            for d, p in recent
        )
        recent_section = (
            "## Last 7 Days (" + str(len(recent)) + " problems)\n"
            "| Date | Problem | Platform | Difficulty |\n"
            "|------|---------|----------|------------|\n"
            + recent_rows + "\n\n---"
        )
    else:
        recent_section = "## Last 7 Days\n_No problems this week yet._\n\n---"

    topic_badges = "  ".join(
        img(k, "https://img.shields.io/badge/" + k.replace(" ", "%20") + "-" + str(v) + "-0a84ff")
        for k, v in topics.most_common()
    )

    topic_rows = "".join(
        "| " + k + " | " + str(v) + " |\n"
        for k, v in topics.most_common()
    )

    platform_rows = "\n".join(
        "| " + plat + " | " + str(cnt) + " | " + ("X" * min(cnt, 20)) + " |"
        for plat, cnt in platforms.most_common()
    )

    updated = datetime.now().strftime("%d %b %Y, %H:%M")

    readme = (
        "# DSA Forge - " + GITHUB_USER + "\n\n"
        "> Last updated: " + updated + " UTC\n\n"
        + badges + "\n\n"
        "---\n\n"
        "## Overview\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        "| LeetCode Solved | **" + str(lc["total"]) + "** (E:" + str(lc["easy"]) + " M:" + str(lc["medium"]) + " H:" + str(lc["hard"]) + ") |\n"
        "| LeetCode Rank | **" + str(lc["rank"]) + "** |\n"
        "| Codeforces Rating | **" + str(cf["rating"]) + "** (peak: " + str(cf["max_rating"]) + ") |\n"
        "| CF Rank | **" + str(cf["rank"]) + "** |\n"
        "| GitHub Contributions | **" + str(gh) + "** |\n"
        "| Current Streak | **" + str(cur_streak) + " days** |\n"
        "| Best Streak | **" + str(best) + " days** |\n"
        "| 30-day Consistency | **" + str(consistency) + "%** |\n"
        "| Total Problems | **" + str(total) + "** |\n\n"
        "---\n\n"
        "## Difficulty Breakdown\n"
        "| Level | Count |\n"
        "|-------|-------|\n"
        "| Easy | " + str(easy) + " |\n"
        "| Medium | " + str(medium) + " |\n"
        "| Hard | " + str(hard) + " |\n\n"
        + bar + "\n\n"
        "---\n\n"
        "## Activity Graph\n"
        + graph + "\n\n"
        "---\n\n"
        "## Heatmap (last 90 days)\n"
        + heatmap + "\n\n"
        "---\n\n"
        + recent_section + "\n\n"
        "## Topics Covered\n"
        + topic_badges + "\n\n"
        "| Topic | Count |\n"
        "|-------|-------|\n"
        + topic_rows
        + "\n---\n\n"
        "## Platform Split\n"
        "| Platform | Count | Bar |\n"
        "|----------|-------|-----|\n"
        + platform_rows + "\n\n"
        "---\n\n"
        "## All Problems (" + str(total) + " total)\n"
        "| Date | Problem | Platform | Topic | Difficulty | Link |\n"
        "|------|---------|----------|-------|------------|------|\n"
        + table_rows + "\n"
    )

    return readme


if __name__ == "__main__":
    data = load_problems()
    readme = build_readme(data)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)
    print("README.md updated")
    print("heatmap.svg written")
