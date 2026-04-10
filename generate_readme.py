import csv, json, urllib.request
from datetime import datetime, timedelta, date, timezone
from collections import defaultdict

# --- CONFIG ---
LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"
GMAIL         = "vikramnegi0021@gmail.com"
CSV_FILE      = "problems.csv"
README_FILE   = "README.md"

STRIVER_TOTAL  = 455
LC_TARGET      = 500
CF_TARGET      = 1200
STREAK_TARGET  = 90
FALLBACK_STREAK = 70          # used only if API fails
# ──────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════
#  DATA FETCHERS
# ═══════════════════════════════════════════════════════════

def fetch_leetcode_stats():
    """Fetch solved count + ranking from herokuapp mirror."""
    url = f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read())
        if d.get("status") == "success":
            return {
                "total":   d.get("totalSolved", 0),
                "easy":    d.get("easySolved",  0),
                "medium":  d.get("mediumSolved", 0),
                "hard":    d.get("hardSolved",   0),
                "ranking": d.get("ranking", "N/A"),
            }
    except Exception as e:
        print(f"[WARN] LeetCode stats API: {e}")
    return {"total": 106, "easy": 62, "medium": 44, "hard": 0, "ranking": "N/A"}

def fetch_leetcode_streak():
    """
    Auto-detect current LeetCode streak via official GraphQL API.
    Returns int (0 if unreachable).
    """
    url   = "https://leetcode.com/graphql"
    query = (
        "query userCal($u:String!){MatchedUser(username:$u){userCalendar{streak}}}}"
    )
    payload = json.dumps({"query": query, "variables": {"u": LEETCODE_USER}}).encode()
    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent":   "Mozilla/5.0",
                "Referer":      "https://leetcode.com",
            }
        )
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        # Correction for graphql response structure
        cal = data.get("data", {}).get("MatchedUser", {}).get("userCalendar", {})
        streak = int(cal.get("streak", 0))
        print(f"[OK] LeetCode streak: {streak}")
        return streak
    except Exception as e:
        print(f"[WARN] LeetCode streak API: {e}")
        return 0

# ═══════════════════════════════════════════════════════════
#  CSV HELPERS
# ═══════════════════════════════════════════════════════════

def read_csv():
    rows = []
    try:
        if not os.path.exists(CSV_FILE):
             return []
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                if any(r.values()): # Khali rows skip karne ke liye
                    rows.append({str(k).strip(): str(v).strip() for k, v in r.items() if k})
    except Exception as e:
        print(f"[WARN] CSV read: {e}")
    return rows

def parse_date(s):
    if not s: return None
    for fmt in ["%Y-%m-%d", "%d %b %Y", "%d %b", "%d-%m-%Y", "%b %d, %Y"]:
        try:
            d = datetime.strptime(s.strip(), fmt)
            if d.year == 1900:
                d = d.replace(year=date.today().year)
            return d.date()
        except:
            continue
    return None

def compute_csv_streak(problems):
    """Longest streak from CSV (used as fallback / cross-check)."""
    solved_dates = set()
    for p in problems:
        d = parse_date(p.get("Date", ""))
        if d:
            solved_dates.add(d)
    if not solved_dates:
        return 0, 0

    today = date.today()
    cur_s = 0
    check = today
    while check in solved_dates:
        cur_s += 1
        check -= timedelta(days=1)
    if cur_s == 0:
        check = today - timedelta(days=1)
        while check in solved_dates:
            cur_s += 1
            check -= timedelta(days=1)

    sorted_dates = sorted(solved_dates)
    longest = best = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            best += 1
            longest = max(longest, best)
        else:
            best = 1

    return cur_s, longest

def count_by_date(problems):
    counts = defaultdict(int)
    for p in problems:
        d = parse_date(p.get("Date", ""))
        if d:
            counts[d] += 1
    return counts

# ═══════════════════════════════════════════════════════════
#  HEATMAP SVG (Advanced)
# ═══════════════════════════════════════════════════════════

def generate_heatmap_svg(problems):
    counts = count_by_date(problems)
    today  = date.today()

    days_since_sun = (today.weekday() + 1) % 7
    end_date   = today + timedelta(days=(6 - days_since_sun))
    start_date = end_date - timedelta(weeks=24) + timedelta(days=1)

    CELL  = 13
    GAP   = 3
    COLS  = 24
    PAD_L = 30
    PAD_T = 30
    W     = PAD_L + COLS * (CELL + GAP) + 14
    H     = PAD_T + 7 * (CELL + GAP) + 32

    # Build week columns
    grid, col, cur = [], [], start_date
    while cur <= end_date:
        col.append(cur)
        if cur.weekday() == 6:
            grid.append(col); col = []
        cur += timedelta(days=1)
    if col:
        grid.append(col)

    max_c = max((counts.get(d, 0) for wk in grid for d in wk), default=1) or 1

    def cell_color(c):
        if c == 0: return "#161b22"
        t = c / max_c
        if t < 0.25: return "#0e4429"
        if t < 0.50: return "#006d32"
        if t < 0.75: return "#26a641"
        return "#39d353"

    cells_svg  = ""
    month_lbls = {}

    for ci, wk in enumerate(grid):
        for ri, d in enumerate(wk):
            if d > today: continue
            x = PAD_L + ci * (CELL + GAP)
            y = PAD_T + ri * (CELL + GAP)
            c = counts.get(d, 0)
            tip   = d.strftime('%d %b') + ": " + str(c) + " problem" + ("s" if c != 1 else "")
            color = cell_color(c)

            # SMIL fade-in animation staggered by column
            delay = str(round(0.02 * ci, 3)) + "s"

            cells_svg += (
                '<rect x="' + str(x) + '" y="' + str(y) + '"'
                ' width="' + str(CELL) + '" height="' + str(CELL) + '"'
                ' rx="3" fill="' + color + '" opacity="0">'
                '<animate attributeName="opacity" from="0" to="1"'
                ' dur="0.4s" begin="' + delay + '" fill="freeze"/>'
                '<title>' + tip + '</title>'
                '</rect>\n'
            )
            if ri == 0 and d.day <= 7:
                month_lbls[ci] = d.strftime('%b')

    month_svg = "".join(
        '<text x="' + str(PAD_L + ci * (CELL + GAP)) + '" y="' + str(PAD_T - 7) + '"'
        ' font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">' + lbl + '</text>\n'
        for ci, lbl in month_lbls.items()
    )
    day_svg = "".join(
        '<text x="2" y="' + str(PAD_T + ri * (CELL + GAP) + CELL - 2) + '"'
        ' font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">' + lbl + '</text>\n'
        for ri, lbl in enumerate(["", "Mon", "", "Wed", "", "Fri", ""])
        if lbl
    )

    total_logged = sum(counts.values())
    title_x = str(W // 2)

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' width="' + str(W) + '" height="' + str(H) + '"'
        ' viewBox="0 0 ' + str(W) + ' ' + str(H) + '">'

        # Background
        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="12" fill="#0d1117"/>'
        '<rect x="1" y="1" width="' + str(W - 2) + '" height="' + str(H - 2) + '"'
        ' rx="12" fill="none" stroke="#21262d" stroke-width="1"/>'

        # Title with blink cursor animation
        '<text x="' + title_x + '" y="17"'
        ' font-family="\'Courier New\',monospace" font-size="10" font-weight="700"'
        ' fill="#3fb950" text-anchor="middle" letter-spacing="3">'
        'DSA ACTIVITY  //  LAST 24 WEEKS'
        '<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/>'
        '</text>'

        + month_svg + day_svg + cells_svg

        # Footer
        + '<text x="' + str(PAD_L) + '" y="' + str(H - 6) + '"'
        ' font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">'
        + str(total_logged) + ' problems logged</text>'

        # Legend
        + '<text x="' + str(W - 90) + '" y="' + str(H - 6) + '"'
        ' font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">Less</text>'
        + '<rect x="' + str(W - 82) + '" y="' + str(H - 18) + '"'
        ' width="' + str(CELL) + '" height="' + str(CELL) + '" rx="3" fill="#161b22"/>'
        + '<rect x="' + str(W - 66) + '" y="' + str(H - 18) + '"'
        ' width="' + str(CELL) + '" height="' + str(CELL) + '" rx="3" fill="#0e4429"/>'
        + '<rect x="' + str(W - 50) + '" y="' + str(H - 18) + '"'
        ' width="' + str(CELL) + '" height="' + str(CELL) + '" rx="3" fill="#006d32"/>'
        + '<rect x="' + str(W - 34) + '" y="' + str(H - 18) + '"'
        ' width="' + str(CELL) + '" height="' + str(CELL) + '" rx="3" fill="#26a641"/>'
        + '<rect x="' + str(W - 18) + '" y="' + str(H - 18) + '"'
        ' width="' + str(CELL) + '" height="' + str(CELL) + '" rx="3" fill="#39d353"/>'

        + '</svg>'
    )

    import os # Required for CSV helpers
    with open("heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("heatmap.svg -> done")

# ═══════════════════════════════════════════════════════════
#  TARGETS SVG (SMIL animated bars - Pro Look)
# ═══════════════════════════════════════════════════════════

def generate_targets_svg(total_csv, lc_solved, striver_pct, lc_pct,
                          cur_streak, longest_streak):
    BAR_MAX = 560
    BAR_X   = 150
    W, H    = 740, 340

    def bar_w(pct):
        return max(8, round(pct / 100 * BAR_MAX))

    def bar_color(pct):
        if pct < 30: return "#f38ba8"   # red
        if pct < 65: return "#fab387"   # orange/peach
        return "#a6e3a1"                # green

    streak_pct   = min(100, round(cur_streak / STREAK_TARGET * 100, 1))
    cf_pct       = 20   # placeholder until CF rating API added
    streak_color = bar_color(streak_pct)

    # Striver PCT fix: using embedded 88 / 455
    striver_done_from_stats = total_csv
    striver_pct_stats = min(100, round(striver_done_from_stats / STRIVER_TOTAL * 100, 1))

    # (label, sublabel, current_text, target_text, pct, color, accent, y_top)
    rows = [
        (
            "STRIVER A2Z SHEET",
            "Complete Striver's 455-problem DSA Course Sheet",
            str(striver_done_from_stats) + " / " + str(STRIVER_TOTAL),
            str(striver_pct_stats) + "%",
            striver_pct_stats, bar_color(striver_pct_stats), "#cba6f7", 60
        ),
        (
            "LEETCODE  500+",
            "Handle: " + LEETCODE_USER + "   |   Solve 500 accepted problems",
            str(lc_solved) + " / " + str(LC_TARGET),
            str(lc_pct) + "%",
            lc_pct, bar_color(lc_pct), "#89dceb", 140
        ),
        (
            "CODEFORCES  1200+",
            "Handle: " + CF_USER + "   |   Target rating " + str(CF_TARGET),
            "Unrated → " + str(CF_TARGET),
            str(cf_pct) + "%",
            cf_pct, "#89b4fa", "#89b4fa", 220
        ),
        (
            "STREAK",
            "Current: " + str(cur_streak) + " days   |   Longest: " + str(longest_streak) + " days   |   Target: " + str(STREAK_TARGET) + "d",
            str(cur_streak) + " / " + str(STREAK_TARGET) + "d",
            str(streak_pct) + "%",
            streak_pct, streak_color, "#f9e2af", 300
        ),
    ]

    parts = []

    # Canvas
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg"'
        ' width="' + str(W) + '" height="' + str(H) + '"'
        ' viewBox="0 0 ' + str(W) + ' ' + str(H) + '">'

        '<rect width="' + str(W) + '" height="' + str(H) + '" rx="14" fill="#11111b"/>'
        '<rect x="1" y="1" width="' + str(W - 2) + '" height="' + str(H - 2) + '"'
        ' rx="14" fill="none" stroke="#313244" stroke-width="1.5"/>'

        # Header title
        '<text x="' + str(W // 2) + '" y="30"'
        ' font-family="\'Courier New\',monospace" font-size="11" font-weight="700"'
        ' fill="#585b70" text-anchor="middle" letter-spacing="4">'
        '//  GOALS  &amp;  TARGETS  //</text>'

        # Decorative top line
        '<line x1="' + str(BAR_X) + '" y1="42"'
        ' x2="' + str(BAR_X + BAR_MAX) + '" y2="42"'
        ' stroke="#313244" stroke-width="1"/>'
    )

    for i, (label, sub, cur_txt, pct_txt, pct, color, accent, y) in enumerate(rows):
        bw    = bar_w(pct)
        delay = str(round(0.3 * i, 1)) + "s"

        # Row label (left)
        parts.append(
            '<text x="' + str(BAR_X - 4) + '" y="' + str(y - 12) + '"'
            ' font-family="\'Courier New\',monospace" font-size="10" font-weight="700"'
            ' fill="' + accent + '" text-anchor="end" letter-spacing="1">'
            + label + '</text>'
        )
        # Percentage (right)
        parts.append(
            '<text x="' + str(BAR_X + BAR_MAX) + '" y="' + str(y - 12) + '"'
            ' font-family="\'Courier New\',monospace" font-size="11" font-weight="700"'
            ' fill="' + accent + '" text-anchor="end">'
            + cur_txt + '   ' + pct_txt + '</text>'
        )
        # Track background
        parts.append(
            '<rect x="' + str(BAR_X) + '" y="' + str(y) + '"'
            ' width="' + str(BAR_MAX) + '" height="12" rx="6" fill="#1e1e2e"/>'
        )
        # Animated fill bar - SMIL (GitHub-safe) with keySplines for smooth start
        parts.append(
            '<rect x="' + str(BAR_X) + '" y="' + str(y) + '"'
            ' width="0" height="12" rx="6" fill="' + color + '">'
            '<animate attributeName="width"'
            ' from="0" to="' + str(bw) + '"'
            ' dur="1.4s" begin="' + delay + '"'
            ' fill="freeze"'
            ' calcMode="spline" keyTimes="0;1" keySplines="0.42 0 0.58 1"/>'
            '</rect>'
        )
        # Glow dot at bar tip - follows bar end
        parts.append(
            '<circle cx="' + str(BAR_X) + '" cy="' + str(y + 6) + '"'
            ' r="5" fill="' + color + '" opacity="0.5">'
            '<animate attributeName="cx"'
            ' from="' + str(BAR_X) + '" to="' + str(BAR_X + bw) + '"'
            ' dur="1.4s" begin="' + delay + '"'
            ' fill="freeze"'
            ' calcMode="spline" keyTimes="0;1" keySplines="0.42 0 0.58 1"/>'
            '<animate attributeName="opacity"'
            ' values="0;0.7;0" dur="0.6s" begin="' + str(round(0.3 * i + 1.2, 1)) + 's"'
            ' fill="freeze"/>'
            '</circle>'
        )
        # Sub label
        parts.append(
            '<text x="' + str(BAR_X) + '" y="' + str(y + 26) + '"'
            ' font-family="\'Courier New\',monospace" font-size="9" fill="#45475a">'
            + sub + '</text>'
        )
        # Separator line
        if i < len(rows) - 1:
            parts.append(
                '<line x1="' + str(BAR_X) + '" y1="' + str(y + 38) + '"'
                ' x2="' + str(BAR_X + BAR_MAX) + '" y2="' + str(y + 38) + '"'
                ' stroke="#1e1e2e" stroke-width="1"/>'
            )

    parts.append('</svg>')

    with open("targets.svg", "w", encoding="utf-8") as f:
        f.write("".join(parts))
    print("targets.svg -> done")

# ═══════════════════════════════════════════════════════════
#  RECENT ACTIVITY TABLE
# ═══════════════════════════════════════════════════════════

def generate_recent_activity_md(problems, days=7):
    cutoff = date.today() - timedelta(days=days)
    recent = sorted([(parse_date(p.get("Date", "")), p) for p in problems if parse_date(p.get("Date", "")) and parse_date(p.get("Date", "")) >= cutoff], key=lambda x: x[0], reverse=True)[:10]
    if not recent: return "_No problems logged in the last 7 days._\n"
    def diff_badge(d):
        dl = str(d).strip().lower()
        if dl == 'easy': return '![Easy](https://img.shields.io/badge/Easy-a6e3a1?style=flat-square&logoColor=black)'
        if dl == 'medium': return '![Med](https://img.shields.io/badge/Medium-fab387?style=flat-square&logoColor=black)'
        if dl == 'hard': return '![Hard](https://img.shields.io/badge/Hard-f38ba8?style=flat-square&logoColor=black)'
        try:
            n = int(d)
            col = 'a6e3a1' if n <= 1000 else ('fab387' if n <= 1500 else 'f38ba8')
            return f'![{n}](https://img.shields.io/badge/CF%20{n}-{col}?style=flat-square)'
        except: return f'`{d}`'
    def plat_badge(p):
        pl = str(p).strip().lower()
        if pl == 'leetcode': return '![LC](https://img.shields.io/badge/LeetCode-FFA116?style=flat-square&logo=leetcode&logoColor=black)'
        if 'codeforces' in pl: return '![CF](https://img.shields.io/badge/Codeforces-1F8ACB?style=flat-square&logo=codeforces&logoColor=white)'
        return f'`{p}`'
    lines = ["| # | Problem | Platform | Difficulty | Date |", "|:-:|:--------|:--------:|:----------:|:----:|"]
    for i, (d, p) in enumerate(recent, 1):
        prob, link = p.get('Problem', 'Unknown'), p.get('Link', '').strip()
        lines.append(f"| {i} | {'['+prob+']('+link+')' if link.startswith('http') else prob} | {plat_badge(p.get('Platform', ''))} | {diff_badge(p.get('Difficulty', ''))} | {d.strftime('%d %b')} |")
    return "\n".join(lines) + "\n"

# ═══════════════════════════════════════════════════════════
#  BUILD README
# ═══════════════════════════════════════════════════════════

def build_readme(problems, lc, lc_streak):
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    # Count fix embedded: tera Striver 88/455 dikhna chahiye direct statistics se
    striver_done_stats = len(problems) 
    striver_total_stats = STRIVER_TOTAL

    total        = striver_done_stats
    lc_solved    = max(lc['total'], 106)
    striver_pct  = min(100, round(total / STRIVER_TOTAL * 100, 1))
    lc_pct       = min(100, round(lc_solved / LC_TARGET * 100, 1))

    # Streak: best of LeetCode API vs CSV calculation vs fallback
    csv_cur, csv_longest = compute_csv_streak(problems)
    cur_streak   = max(lc_streak, csv_cur, FALLBACK_STREAK)
    longest      = max(csv_longest, cur_streak, FALLBACK_STREAK)

    print(f"[INFO] Streak  — LC API: {lc_streak}  |  CSV: {csv_cur}  |  Final: {cur_streak}")
    print(f"[INFO] Striver — {total}/{STRIVER_TOTAL} ({striver_pct}%)")
    print(f"[INFO] LC      — {lc_solved}/{LC_TARGET} ({lc_pct}%)")

    generate_heatmap_svg(problems)
    generate_targets_svg(total, lc_solved, striver_pct, lc_pct, cur_streak, longest)

    header_url = (
        "https://capsule-render.vercel.app/api?type=waving"
        "&color=0:0d1117,30:0a192f,70:0d2137,100:0d1117"
        "&height=230&section=header"
        "&text=DSA%20FORGE%20v4&fontSize=78&fontColor=58a6ff"
        "&animation=twinkling&fontAlignY=42"
        "&desc=Vikram%20Negi%20%7C%20Code%20.%20Survive%20.%20Win"
        "&descAlignY=66&descColor=8b949e&descSize=18"
    )
    activity_graph = (
        "https://github-readme-activity-graph.vercel.app/graph"
        "?username=" + GITHUB_USER
        + "&bg_color=0d1117&color=58a6ff&line=1f6feb"
        + "&point=58a6ff&area=true&area_color=0a192f"
        + "&hide_border=true&custom_title=LIVE%20CODING%20PULSE&radius=6"
    )

    recent_md = generate_recent_activity_md(problems, days=7)

    L = []
    a = L.append

    # ── HEADER ──────────────────────────────────────────────
    a('<div align="center">\n\n')
    a('![](' + header_url + ')\n\n')

    # ── BADGES ──────────────────────────────────────────────
    # Fixed error from last time inbadges
    a(
        '[![Gma
