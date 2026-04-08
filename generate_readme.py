import csv, json, urllib.request
from datetime import datetime, timedelta, date
from collections import defaultdict

LEETCODE_USER = "vikramnegi21"
GITHUB_USER   = "vikramnegi21"
CSV_FILE      = "problems.csv"
README_FILE   = "README.md"
HEATMAP_FILE  = "heatmap.svg"

# ─────────────────────────────────────────────
# LEETCODE API
# ─────────────────────────────────────────────
def fetch_leetcode():
    url = "https://leetcode-stats-api.herokuapp.com/" + LEETCODE_USER
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        if d.get("status") == "success":
            return {
                "total":   d.get("totalSolved", 0),
                "easy":    d.get("easySolved",  0),
                "medium":  d.get("mediumSolved",0),
                "hard":    d.get("hardSolved",  0),
                "ranking": d.get("ranking",    "N/A"),
            }
    except Exception as e:
        print("LeetCode API error: " + str(e))
    return {"total":0,"easy":0,"medium":0,"hard":0,"ranking":"N/A"}

# ─────────────────────────────────────────────
# CSV
# ─────────────────────────────────────────────
def read_csv():
    rows = []
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                rows.append({k: v.strip() for k, v in r.items()})
    except FileNotFoundError:
        print("problems.csv not found")
    return rows

def parse_date(s):
    for fmt in ["%Y-%m-%d","%d %b %Y","%d %b","%d-%m-%Y","%b %d, %Y"]:
        try:
            d = datetime.strptime(s.strip(), fmt)
            if d.year == 1900:
                d = d.replace(year=datetime.now().year)
            return d.date()
        except:
            continue
    return None

# ─────────────────────────────────────────────
# STREAK
# ─────────────────────────────────────────────
def calc_streak(problems):
    dates = set(filter(None, (parse_date(p["Date"]) for p in problems)))
    if not dates:
        return 0, 0
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
            if cur2 > best:
                best = cur2
        else:
            cur2 = 1
    if cur > best:
        best = cur
    return cur, best

def last_n_days(problems, n=7):
    cutoff = date.today() - timedelta(days=n)
    res = [p for p in problems
           if (parse_date(p["Date"]) or date.min) > cutoff]
    return sorted(res,
                  key=lambda x: parse_date(x["Date"]) or date.min,
                  reverse=True)

def count_by(problems, key):
    c = defaultdict(int)
    for p in problems:
        v = p.get(key, "").strip()
        if v:
            c[v] += 1
    return dict(c)

# ─────────────────────────────────────────────
# HEATMAP SVG
# ─────────────────────────────────────────────
def make_heatmap(problems, weeks=18):
    date_counts = defaultdict(int)
    for p in problems:
        d = parse_date(p["Date"])
        if d:
            date_counts[d] += 1

    today = date.today()
    start = today - timedelta(days=today.weekday()+1+(weeks-1)*7)
    cell, gap = 13, 3
    step = cell + gap
    w = weeks * step + 52
    h = 7 * step + 52

    cells = []
    month_labels = {}

    for week in range(weeks):
        for dow in range(7):
            day = start + timedelta(weeks=week, days=dow)
            x = 38 + week * step
            y = 22 + dow * step
            if day > today:
                cells.append(
                    '<rect x="' + str(x) + '" y="' + str(y) +
                    '" width="' + str(cell) + '" height="' + str(cell) +
                    '" rx="3" fill="#0d1117" opacity="0.4"/>'
                )
            else:
                cnt = date_counts.get(day, 0)
                if cnt == 0:
                    color = "#161b22"
                elif cnt == 1:
                    color = "#0e4429"
                elif cnt == 2:
                    color = "#006d32"
                elif cnt <= 4:
                    color = "#26a641"
                else:
                    color = "#39d353"
                label = day.strftime("%d %b %Y")
                ps = "problems" if cnt != 1 else "problem"
                cells.append(
                    '<rect x="' + str(x) + '" y="' + str(y) +
                    '" width="' + str(cell) + '" height="' + str(cell) +
                    '" rx="3" fill="' + color + '">' +
                    '<title>' + label + ': ' + str(cnt) + ' ' + ps +
                    '</title></rect>'
                )
            if dow == 0 and day.day <= 7:
                month_labels[week] = day.strftime("%b")

    month_svg = ""
    for w_, m in month_labels.items():
        month_svg += (
            '<text x="' + str(38 + w_ * step) + '" y="14"'
            ' fill="#58a6ff" font-size="10" font-family="monospace">' +
            m + '</text>'
        )

    day_names = ["S","M","T","W","T","F","S"]
    day_svg = ""
    for i in range(7):
        day_svg += (
            '<text x="4" y="' + str(22 + i * step + 10) + '"'
            ' fill="#8b949e" font-size="9" font-family="monospace">' +
            day_names[i] + '</text>'
        )

    legend_colors = ["#161b22","#0e4429","#006d32","#26a641","#39d353"]
    legend_svg = (
        '<text x="' + str(w-110) + '" y="' + str(h-6) + '"'
        ' fill="#8b949e" font-size="9" font-family="monospace">Less</text>'
    )
    for i, col in enumerate(legend_colors):
        legend_svg += (
            '<rect x="' + str(w-85+i*16) + '" y="' + str(h-18) +
            '" width="12" height="12" rx="3" fill="' + col + '"/>'
        )
    legend_svg += (
        '<text x="' + str(w-2) + '" y="' + str(h-6) + '"'
        ' fill="#8b949e" font-size="9" font-family="monospace"'
        ' text-anchor="end">More</text>'
    )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' width="' + str(w) + '" height="' + str(h) + '">'
        '<rect width="' + str(w) + '" height="' + str(h) +
        '" rx="10" fill="#0d1117"/>'
        '<rect width="' + str(w) + '" height="' + str(h) +
        '" rx="10" fill="none" stroke="#21262d" stroke-width="1"/>' +
        month_svg + day_svg + "".join(cells) + legend_svg +
        '</svg>'
    )
    return svg

# ─────────────────────────────────────────────
# PROGRESS BAR (text-based)
# ─────────────────────────────────────────────
def pbar(done, total_goal, width=20):
    filled = int(done / total_goal * width) if total_goal > 0 else 0
    filled = min(filled, width)
    pct = round(done / total_goal * 100, 1) if total_goal > 0 else 0
    bar = "`" + "█" * filled + "░" * (width - filled) + "`"
    return bar + " " + str(done) + "/" + str(total_goal) + " (" + str(pct) + "%)"

# ─────────────────────────────────────────────
# README BUILDER
# ─────────────────────────────────────────────
def build_readme(problems, lc):
    now = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    cur_streak, best_streak = calc_streak(problems)
    topics  = dict(sorted(count_by(problems,"Topic").items(), key=lambda x: -x[1]))
    diff    = count_by(problems, "Difficulty")
    plat    = count_by(problems, "Platform")
    total   = len(problems)
    recent  = last_n_days(problems, 7)

    local_lc = plat.get("LeetCode",   0)
    local_cf = plat.get("Codeforces", 0)

    lc_total  = lc["total"]  if lc["total"]  > 0 else local_lc
    lc_easy   = lc["easy"]   if lc["total"]  > 0 else diff.get("Easy",   0)
    lc_medium = lc["medium"] if lc["total"]  > 0 else diff.get("Medium", 0)
    lc_hard   = lc["hard"]   if lc["total"]  > 0 else diff.get("Hard",   0)
    lc_rank   = lc["ranking"]

    cutoff30 = date.today() - timedelta(days=30)
    active_days = len(set(
        parse_date(p["Date"]) for p in problems
        if parse_date(p["Date"]) and parse_date(p["Date"]) > cutoff30
    ))
    consistency = round(active_days / 30 * 100, 1)

    now_b = now.replace(" ","%20").replace(",","%2C").replace(":","%3A")

    # ── URLS ──
    cap_header = (
        "https://capsule-render.vercel.app/api?type=rect"
        "&color=0:0d1117,50:0d2137,100:0d1117"
        "&height=180&section=header"
        "&text=DSA%20Forge&fontSize=60"
        "&fontColor=58a6ff&animation=fadeIn"
        "&fontAlignY=40"
        "&desc=%E2%9A%94%EF%B8%8F%20vikramnegi21%20%7C%20CSE%20B.Tech%20%7C%20Building%20in%20Public"
        "&descAlignY=62&descColor=c9d1d9"
        "&stroke=21262d&strokeWidth=1"
    )
    cap_footer = (
        "https://capsule-render.vercel.app/api?type=rect"
        "&color=0:0d1117,50:0d2137,100:0d1117"
        "&height=80&section=footer&reversal=true"
    )
    gh_stats = (
        "https://github-readme-stats.vercel.app/api"
        "?username=" + GITHUB_USER +
        "&show_icons=true&theme=github_dark_dimmed"
        "&hide_border=true&count_private=true"
        "&rank_icon=percentile&include_all_commits=true"
    )
    streak_card = (
        "https://streak-stats.demolab.com"
        "?user=" + GITHUB_USER +
        "&theme=github-dark-blue&hide_border=true"
        "&background=0d1117&ring=58a6ff&fire=ff7b00"
        "&currStreakLabel=58a6ff"
    )
    lc_card = (
        "https://leetcard.jacoblin.cool/" + LEETCODE_USER +
        "?theme=dark&font=Karma&ext=heatmap&border=0&radius=10"
    )
    activity_graph = (
        "https://github-readme-activity-graph.vercel.app/graph"
        "?username=" + GITHUB_USER +
        "&bg_color=0d1117&color=58a6ff&line=1f6feb"
        "&point=58a6ff&area=true&area_color=1f3358"
        "&hide_border=true&custom_title=Contribution%20Graph"
    )
    views_badge = (
        "https://komarev.com/ghpvc/?username=" + GITHUB_USER +
        "&color=1f6feb&style=for-the-badge&label=PROFILE+VIEWS"
    )
    lc_badge = (
        "https://img.shields.io/badge/LEETCODE-" +
        str(lc_total) + "%20SOLVED" +
        "-FFA116?style=for-the-badge&logo=leetcode&logoColor=white"
    )
    cf_badge = (
        "https://img.shields.io/badge/CODEFORCES-" +
        str(local_cf) + "%20SOLVED" +
        "-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white"
    )
    streak_badge = (
        "https://img.shields.io/badge/STREAK-" +
        str(cur_streak) + "%20DAYS" +
        "-ff7b00?style=for-the-badge"
    )
    total_badge = (
        "https://img.shields.io/badge/TOTAL-" +
        str(total) + "%20PROBLEMS" +
        "-6e40c9?style=for-the-badge"
    )
    upd_badge = (
        "https://img.shields.io/badge/UPDATED-" +
        now_b + "-21262d?style=flat-square"
    )

    L = []

    # ══ HEADER ══════════════════════════════════════
    L.append('<div align="center">')
    L.append("")
    L.append("![](" + cap_header + ")")
    L.append("")
    L.append("![](" + views_badge + ")")
    L.append("![](" + lc_badge + ")")
    L.append("![](" + cf_badge + ")")
    L.append("![](" + streak_badge + ")")
    L.append("![](" + total_badge + ")")
    L.append("")
    L.append("![](" + upd_badge + ")")
    L.append("")
    L.append("</div>")
    L.append("")
    L.append("---")
    L.append("")

    # ══ ABOUT ═══════════════════════════════════════
    L.append("> **4th sem CSE undergrad** grinding DSA daily.")
    L.append("> Following **Striver's A2Z Sheet** + active on **LeetCode** & **Codeforces**.")
    L.append("> Goal: crack a web dev internship. Building everything in public.")
    L.append("")
    L.append("---")
    L.append("")

    # ══ GITHUB STATS ════════════════════════════════
    L.append("## GitHub Stats")
    L.append("")
    L.append('<div align="center">')
    L.append("")
    L.append(
        '<img src="' + gh_stats + '" height="170"/>' +
        "&nbsp;" +
        '<img src="' + streak_card + '" height="170"/>'
    )
    L.append("")
    L.append("</div>")
    L.append("")

    # ══ LEETCODE CARD ════════════════════════════════
    L.append("## LeetCode Progress")
    L.append("")
    L.append('<div align="center">')
    L.append("")
    L.append("![](" + lc_card + ")")
    L.append("")
    L.append("</div>")
    L.append("")

    # ══ AT A GLANCE ══════════════════════════════════
    L.append("## At a Glance")
    L.append("")
    L.append("| | Metric | Value |")
    L.append("|--|--------|-------|")
    L.append("| 🟢 | LeetCode Easy     | **" + str(lc_easy)     + "** |")
    L.append("| 🟡 | LeetCode Medium   | **" + str(lc_medium)   + "** |")
    L.append("| 🔴 | LeetCode Hard     | **" + str(lc_hard)     + "** |")
    L.append("| 🏅 | LeetCode Rank     | **" + str(lc_rank)     + "** |")
    L.append("| ⚡ | Codeforces Solved | **" + str(local_cf)    + "** |")
    L.append("| 🔥 | Current Streak    | **" + str(cur_streak)  + " days** |")
    L.append("| 🏆 | Best Streak       | **" + str(best_streak) + " days** |")
    L.append("| 📅 | 30d Consistency   | **" + str(consistency) + "%** |")
    L.append("| 📚 | Total Problems    | **" + str(total)       + "** |")
    L.append("")

    # ══ HEATMAP ══════════════════════════════════════
    L.append("## Practice Heatmap")
    L.append("")
    L.append('<div align="center">')
    L.append("")
    L.append("![Heatmap](heatmap.svg)")
    L.append("")
    L.append("</div>")
    L.append("")

    # ══ ACTIVITY GRAPH ════════════════════════════════
    L.append("## Activity Graph")
    L.append("")
    L.append('<div align="center">')
    L.append("")
    L.append("![](" + activity_graph + ")")
    L.append("")
    L.append("</div>")
    L.append("")

    # ══ LAST 7 DAYS ══════════════════════════════════
    L.append("## Last 7 Days &nbsp;`" + str(len(recent)) + " problems`")
    L.append("")
    L.append("| Date | Problem | Platform | Difficulty |")
    L.append("|------|---------|----------|:----------:|")
    for p in recent:
        d    = parse_date(p["Date"])
        ds   = d.strftime("%d %b") if d else p["Date"]
        name = p.get("Problem","").strip()
        link = p.get("Link","").strip()
        pv   = p.get("Platform","").strip()
        dv   = p.get("Difficulty","").strip()
        if link and link != "-":
            cell = "[" + name + "](" + link + ")"
        else:
            cell = name
        L.append("| `" + ds + "` | " + cell + " | " + pv + " | `" + dv + "` |")
    L.append("")

    # ══ TOPICS ════════════════════════════════════════
    L.append("## Topics Mastered")
    L.append("")
    badges = []
    for t, c in topics.items():
        b = (
            "https://img.shields.io/badge/" +
            t.replace(" ","_") + "-" + str(c) +
            "-1f6feb?style=flat-square"
        )
        badges.append("![](" + b + ")")
    L.append("  ".join(badges))
    L.append("")
    L.append("| Topic | Solved |")
    L.append("|-------|:------:|")
    for t, c in topics.items():
        L.append("| " + t + " | **" + str(c) + "** |")
    L.append("")

    # ══ GOALS ═════════════════════════════════════════
    L.append("## Goals")
    L.append("")
    L.append("| Goal | Progress |")
    L.append("|------|---------|")
    L.append("| Striver A2Z Sheet (455) | " + pbar(total,      455) + " |")
    L.append("| LeetCode 500+ Solves    | " + pbar(lc_total,   500) + " |")
    L.append("| CF Rating 1000+         | In Progress |")
    L.append("| 30-Day Streak           | " + pbar(cur_streak,  30) + " |")
    L.append("")

    # ══ PLATFORM SPLIT ════════════════════════════════
    L.append("## Platform Split")
    L.append("")
    L.append("| Platform | Solved |")
    L.append("|----------|:------:|")
    for platform, cnt in sorted(plat.items(), key=lambda x: -x[1]):
        L.append("| " + platform + " | **" + str(cnt) + "** |")
    L.append("")

    # ══ ALL PROBLEMS ══════════════════════════════════
    L.append("## All Problems &nbsp;`" + str(total) + " total`")
    L.append("")
    L.append("| Date | Problem | Platform | Topic | Difficulty |")
    L.append("|------|---------|----------|-------|:----------:|")
    sorted_p = sorted(problems,
                      key=lambda x: parse_date(x["Date"]) or date.min,
                      reverse=True)
    for p in sorted_p:
        d    = parse_date(p["Date"])
        ds   = d.strftime("%d %b") if d else p["Date"]
        name = p.get("Problem","").strip()
        link = p.get("Link","").strip()
        pv   = p.get("Platform","").strip()
        tv   = p.get("Topic","").strip()
        dv   = p.get("Difficulty","").strip()
        if link and link != "-":
            cell = "[" + name + "](" + link + ")"
        else:
            cell = name
        L.append("| `" + ds + "` | " + cell + " | " + pv + " | " + tv + " | `" + dv + "` |")
    L.append("")

    # ══ FOOTER ════════════════════════════════════════
    L.append('<div align="center">')
    L.append("")
    L.append("![](" + cap_footer + ")")
    L.append("")
    L.append("*Auto-updated by GitHub Actions — last run: " + now + "*")
    L.append("")
    L.append("</div>")

    return "\n".join(L)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("Fetching LeetCode stats...")
    lc = fetch_leetcode()
    print(
        "  total=" + str(lc["total"]) +
        " easy="   + str(lc["easy"]) +
        " medium=" + str(lc["medium"]) +
        " hard="   + str(lc["hard"]) +
        " rank="   + str(lc["ranking"])
    )

    print("Reading problems.csv...")
    problems = read_csv()
    print("  " + str(len(problems)) + " problems loaded")

    print("Generating heatmap.svg...")
    with open(HEATMAP_FILE, "w", encoding="utf-8") as f:
        f.write(make_heatmap(problems))

    print("Building README.md...")
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(build_readme(problems, lc))

    print("Done!")

if __name__ == "__main__":
    main()
    
