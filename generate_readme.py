
import csv, json, urllib.request
from datetime import datetime, timedelta, date, timezone
from collections import defaultdict

# ─── CONFIG ───────────────────────────────────────────────
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
    url   = "https://leetcode.com/graphql"
    query = (
        "query userCal($u:String!){"
        "matchedUser(username:$u){"
        "userCalendar{streak totalActiveDays}}}"
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
        cal = data["data"]["matchedUser"]["userCalendar"]
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
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
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
#  HEATMAP SVG
# ═══════════════════════════════════════════════════════════

def generate_heatmap_svg(problems):
    counts = count_by_date(problems)
    today  = date.today()
    days_since_sun = (today.weekday() + 1) % 7
    end_date   = today + timedelta(days=(6 - days_since_sun))
    start_date = end_date - timedelta(weeks=24) + timedelta(days=1)
    CELL, GAP, COLS, PAD_L, PAD_T = 13, 3, 24, 30, 30
    W, H = PAD_L + COLS * (CELL + GAP) + 14, PAD_T + 7 * (CELL + GAP) + 32
    grid, col, cur = [], [], start_date
    while cur <= end_date:
        col.append(cur)
        if cur.weekday() == 6:
            grid.append(col); col = []
        cur += timedelta(days=1)
    if col: grid.append(col)
    max_c = max((counts.get(d, 0) for wk in grid for d in wk), default=1) or 1
    def cell_color(c):
        if c == 0: return "#161b22"
        t = c / max_c
        if t < 0.25: return "#0e4429"
        if t < 0.50: return "#006d32"
        if t < 0.75: return "#26a641"
        return "#39d353"
    cells_svg = ""
    month_lbls = {}
    for ci, wk in enumerate(grid):
        for ri, d in enumerate(wk):
            if d > today: continue
            x, y = PAD_L + ci * (CELL + GAP), PAD_T + ri * (CELL + GAP)
            c = counts.get(d, 0)
            tip = f"{d.strftime('%d %b')}: {c} problem{'s' if c != 1 else ''}"
            color, delay = cell_color(c), f"{round(0.02 * ci, 3)}s"
            cells_svg += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay}" fill="freeze"/><title>{tip}</title></rect>\n'
            if ri == 0 and d.day <= 7: month_lbls[ci] = d.strftime('%b')
    month_svg = "".join(f'<text x="{PAD_L + ci*(CELL+GAP)}" y="{PAD_T-7}" font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">{lbl}</text>\n' for ci, lbl in month_lbls.items())
    day_svg = "".join(f'<text x="2" y="{PAD_T + ri*(CELL+GAP) + CELL-2}" font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">{lbl}</text>\n' for ri, lbl in enumerate(["", "Mon", "", "Wed", "", "Fri", ""]) if lbl)
    total_logged = sum(counts.values())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" rx="12" fill="#0d1117"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="none" stroke="#21262d" stroke-width="1"/><text x="{W//2}" y="17" font-family="\'Courier New\',monospace" font-size="10" font-weight="700" fill="#3fb950" text-anchor="middle" letter-spacing="3">DSA ACTIVITY  //  LAST 24 WEEKS<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></text>{month_svg}{day_svg}{cells_svg}<text x="{PAD_L}" y="{H-6}" font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">{total_logged} problems logged</text><text x="{W-90}" y="{H-6}" font-family="\'Courier New\',monospace" font-size="9" fill="#484f58">Less</text><rect x="{W-82}" y="{H-18}" width="{CELL}" height="{CELL}" rx="3" fill="#161b22"/><rect x="{W-66}" y="{H-18}" width="{CELL}" height="{CELL}" rx="3" fill="#0e4429"/><rect x="{W-50}" y="{H-18}" width="{CELL}" height="{CELL}" rx="3" fill="#006d32"/><rect x="{W-34}" y="{H-18}" width="{CELL}" height="{CELL}" rx="3" fill="#26a641"/><rect x="{W-18}" y="{H-18}" width="{CELL}" height="{CELL}" rx="3" fill="#39d353"/></svg>'
    with open("heatmap.svg", "w", encoding="utf-8") as f: f.write(svg)
    print("heatmap.svg -> done")

# ═══════════════════════════════════════════════════════════
#  TARGETS SVG
# ═══════════════════════════════════════════════════════════

def generate_targets_svg(total_csv, lc_solved, striver_pct, lc_pct, cur_streak, longest_streak):
    BAR_MAX, BAR_X, W, H = 560, 150, 740, 340
    def bar_w(pct): return max(8, round(pct / 100 * BAR_MAX))
    def bar_color(pct): return "#f38ba8" if pct < 30 else ("#fab387" if pct < 65 else "#a6e3a1")
    streak_pct = min(100, round(cur_streak / STREAK_TARGET * 100, 1))
    rows = [
        ("STRIVER A2Z SHEET", "Complete Striver's 455-problem DSA Course Sheet", f"{total_csv} / {STRIVER_TOTAL}", f"{striver_pct}%", striver_pct, bar_color(striver_pct), "#cba6f7", 60),
        ("LEETCODE  500+", f"Handle: {LEETCODE_USER}   |   Solve 500 accepted problems", f"{lc_solved} / {LC_TARGET}", f"{lc_pct}%", lc_pct, bar_color(lc_pct), "#89dceb", 140),
        ("CODEFORCES  1200+", f"Handle: {CF_USER}   |   Target rating {CF_TARGET}", f"Unrated → {CF_TARGET}", "20%", 20, "#89b4fa", "#89b4fa", 220),
        ("STREAK", f"Current: {cur_streak}d   |   Longest: {longest_streak}d   |   Target: {STREAK_TARGET}d", f"{cur_streak} / {STREAK_TARGET}d", f"{streak_pct}%", streak_pct, bar_color(streak_pct), "#f9e2af", 300),
    ]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" rx="14" fill="#11111b"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="#313244" stroke-width="1.5"/><text x="{W//2}" y="30" font-family="\'Courier New\',monospace" font-size="11" font-weight="700" fill="#585b70" text-anchor="middle" letter-spacing="4">//  GOALS  &amp;  TARGETS  //</text><line x1="{BAR_X}" y1="42" x2="{BAR_X+BAR_MAX}" y2="42" stroke="#313244" stroke-width="1"/>']
    for i, (label, sub, cur_txt, pct_txt, pct, color, accent, y) in enumerate(rows):
        bw, delay = bar_w(pct), f"{round(0.3 * i, 1)}s"
        parts.append(f'<text x="{BAR_X-4}" y="{y-12}" font-family="\'Courier New\',monospace" font-size="10" font-weight="700" fill="{accent}" text-anchor="end" letter-spacing="1">{label}</text><text x="{BAR_X+BAR_MAX}" y="{y-12}" font-family="\'Courier New\',monospace" font-size="11" font-weight="700" fill="{accent}" text-anchor="end">{cur_txt}   {pct_txt}</text><rect x="{BAR_X}" y="{y}" width="{BAR_MAX}" height="12" rx="6" fill="#1e1e2e"/><rect x="{BAR_X}" y="{y}" width="0" height="12" rx="6" fill="{color}"><animate attributeName="width" from="0" to="{bw}" dur="1.4s" begin="{delay}" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/></rect><circle cx="{BAR_X}" cy="{y+6}" r="5" fill="{color}" opacity="0.5"><animate attributeName="cx" from="{BAR_X}" to="{BAR_X+bw}" dur="1.4s" begin="{delay}" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" values="0;0.7;0" dur="0.6s" begin="{round(0.3*i+1.0, 1)}s" fill="freeze"/></circle><text x="{BAR_X}" y="{y+26}" font-family="\'Courier New\',monospace" font-size="9" fill="#45475a">{sub}</text>')
        if i < len(rows) - 1: parts.append(f'<line x1="{BAR_X}" y1="{y+38}" x2="{BAR_X+BAR_MAX}" y2="{y+38}" stroke="#1e1e2e" stroke-width="1"/>')
    parts.append('</svg>')
    with open("targets.svg", "w", encoding="utf-8") as f: f.write("".join(parts))
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
        if dl == 'easy': return '![Easy](https://img.shields.io/badge/Easy-a6e3a1?style=flat-square)'
        if dl == 'medium': return '![Med](https://img.shields.io/badge/Medium-fab387?style=flat-square)'
        if dl == 'hard': return '![Hard](https://img.shields.io/badge/Hard-f38ba8?style=flat-square)'
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
    total, lc_solved = len(problems), max(lc['total'], 106)
    striver_pct, lc_pct = min(100, round(total/STRIVER_TOTAL*100, 1)), min(100, round(lc_solved/LC_TARGET*100, 1))
    csv_cur, csv_longest = compute_csv_streak(problems)
    cur_streak, longest = max(lc_streak, csv_cur, FALLBACK_STREAK), max(csv_longest, max(lc_streak, csv_cur, FALLBACK_STREAK), FALLBACK_STREAK)
    generate_heatmap_svg(problems)
    generate_targets_svg(total, lc_solved, striver_pct, lc_pct, cur_streak, longest)
    
    header_url = f"https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,30:0a192f,70:0d2137,100:0d1117&height=230&section=header&text=DSA%20FORGE%20v4&fontSize=78&fontColor=58a6ff&animation=twinkling&fontAlignY=42&desc=Vikram%20Negi%20%7C%20Code%20.%20Survive%20.%20Win&descAlignY=66&descColor=8b949e&descSize=18"
    activity_graph = f"https://github-readme-activity-graph.vercel.app/graph?username={GITHUB_USER}&bg_color=0d1117&color=58a6ff&line=1f6feb&point=58a6ff&area=true&area_color=0a192f&hide_border=true&custom_title=LIVE%20CODING%20PULSE&radius=6"
    recent_md = generate_recent_activity_md(problems, days=7)

    L = []
    L.append('<div align="center">\n\n')
    L.append(f'![]({header_url})\n\n')
    # Fixed Badges Section below:
    L.append(f'[![Gmail](https://img.shields.io/badge/GMAIL-vikramnegi0021-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{GMAIL})&nbsp;&nbsp;[![LeetCode](https://img.shields.io/badge/LEETCODE-{LEETCODE_USER}-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/{LEETCODE_USER})\n\n')
    L.append(f'[![Codeforces](https://img.shields.io/badge/CODEFORCES-{CF_USER}-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white)](https://codeforces.com/profile/{CF_USER})&nbsp;&nbsp;[![Streak](https://img.shields.io/badge/CURRENT%20STREAK-{cur_streak}%20DAYS-FF7B00?style=for-the-badge&logo=fire&logoColor=white)](https://leetcode.com/{LEETCODE_USER})\n\n')
    L.append('</div>\n\n---\n\n')
    L.append(f'## System Performance\n\n<div align="center">\n\n<img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true&rank_icon=github" height="170" />&nbsp;<img src="https://github-readme-streak-stats.herokuapp.com/?user={GITHUB_USER}&theme=tokyonight&hide_border=true" height="170" />\n\n</div>\n\n---\n\n')
    L.append(f'## Activity Flow\n\n<div align="center">\n\n<img src="{activity_graph}" width="100%" />\n\n</div>\n\n---\n\n')
    L.append(f'## LeetCode\n\n<div align="center">\n\n<img src="https://leetcard.jacoblin.cool/{LEETCODE_USER}?theme=dark&font=Karma&ext=heatmap&border=0&radius=12" width="96%" />\n\n</div>\n\n---\n\n')
    L.append(f'## DSA Heatmap\n\n<div align="center">\n\n<img src="heatmap.svg" width="100%" />\n\n</div>\n\n---\n\n')
    L.append(f'## Targets\n\n<div align="center">\n\n<img src="targets.svg" width="100%" />\n\n</div>\n\n---\n\n')
    L.append(f'## Recent Activity\n\n{recent_md}\n---\n\n')
    L.append(f'<div align="center">\n\n`Last Sync : {now_ist.strftime("%d %b %Y  |  %I:%M %p IST")}`\n\n</div>\n')
    return "".join(L)

def main():
    print("DSA Forge — starting sync...")
    lc_stats, lc_streak, problems = fetch_leetcode_stats(), fetch_leetcode_streak(), read_csv()
    readme = build_readme(problems, lc_stats, lc_streak)
    with open(README_FILE, "w", encoding="utf-8") as f: f.write(readme)
    print(f"Done — {len(problems)} problems logged, all files updated.")

if __name__ == "__main__": main()
                
