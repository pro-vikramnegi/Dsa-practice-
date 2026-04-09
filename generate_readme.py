import csv, json, urllib.request
from datetime import datetime, timedelta, date, timezone
from collections import defaultdict

# ─── CONFIG ───────────────────────────────────────────────
LEETCODE_USER  = "__vikram21"
CF_USER        = "__vikram21"
GITHUB_USER    = "vikramnegi21"
GMAIL          = "vikramnegi0021@gmail.com"
CSV_FILE       = "problems.csv"
README_FILE    = "README.md"

STRIVER_TOTAL  = 455
LC_TARGET      = 500
CF_TARGET      = 1200
# ──────────────────────────────────────────────────────────


def fetch_leetcode_stats():
    url = f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        if d.get("status") == "success":
            return {
                "total":  d.get("totalSolved", 0),
                "easy":   d.get("easySolved",  0),
                "medium": d.get("mediumSolved", 0),
                "hard":   d.get("hardSolved",   0),
                "ranking": d.get("ranking", "N/A"),
            }
    except Exception as e:
        print(f"LeetCode API error: {e}")
    return {"total": 106, "easy": 62, "medium": 44, "hard": 0, "ranking": "N/A"}


def read_csv():
    rows = []
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({str(k).strip(): str(v).strip() for k, v in r.items() if k})
    except Exception as e:
        print(f"CSV read error: {e}")
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


def compute_streak(problems):
    solved_dates = set()
    for p in problems:
        d = parse_date(p.get("Date", ""))
        if d:
            solved_dates.add(d)
    if not solved_dates:
        return 0, 0

    today = date.today()

    # Current streak
    streak = 0
    check = today
    while check in solved_dates:
        streak += 1
        check -= timedelta(days=1)
    if streak == 0:
        check = today - timedelta(days=1)
        while check in solved_dates:
            streak += 1
            check -= timedelta(days=1)

    # Longest streak
    sorted_dates = sorted(solved_dates)
    longest = cur = 1
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 1

    return streak, longest


# ─── ANIMATED TARGETS SVG ─────────────────────────────────
def generate_targets_svg(total_csv, lc_solved, striver_pct, lc_pct):

    def bar_w(pct, max_w=622):
        return max(10, round(pct / 100 * max_w))

    def grad_color(pct):
        if pct < 30: return ("#e74c3c", "#c0392b")
        if pct < 65: return ("#f39c12", "#e67e22")
        return ("#2ecc71", "#27ae60")

    s_c1, s_c2 = grad_color(striver_pct)
    l_c1, l_c2 = grad_color(lc_pct)
    s_w = bar_w(striver_pct)
    l_w = bar_w(lc_pct)
    cf_w = bar_w(30)   # static visual indicator for CF

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="230" viewBox="0 0 700 230">
  <defs>
    <style>
      text {{ font-family: 'Segoe UI', Arial, sans-serif; }}
      @keyframes bar1 {{ from {{ width:0 }} to {{ width:{s_w}px }} }}
      @keyframes bar2 {{ from {{ width:0 }} to {{ width:{l_w}px }} }}
      @keyframes bar3 {{ from {{ width:0 }} to {{ width:{cf_w}px }} }}
      .b1 {{ animation: bar1 1.5s cubic-bezier(.4,0,.2,1) 0.1s both; }}
      .b2 {{ animation: bar2 1.5s cubic-bezier(.4,0,.2,1) 0.25s both; }}
      .b3 {{ animation: bar3 1.5s cubic-bezier(.4,0,.2,1) 0.4s both; }}
    </style>
    <linearGradient id="g1" x1="0" x2="1"><stop offset="0%" stop-color="{s_c1}"/><stop offset="100%" stop-color="{s_c2}"/></linearGradient>
    <linearGradient id="g2" x1="0" x2="1"><stop offset="0%" stop-color="{l_c1}"/><stop offset="100%" stop-color="{l_c2}"/></linearGradient>
    <linearGradient id="g3" x1="0" x2="1"><stop offset="0%" stop-color="#89b4fa"/><stop offset="100%" stop-color="#74c7ec"/></linearGradient>
    <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#1e1e2e"/><stop offset="100%" stop-color="#181825"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>

  <rect width="700" height="230" rx="14" fill="url(#bg)"/>
  <rect x="1" y="1" width="698" height="228" rx="14" fill="none" stroke="#313244" stroke-width="1.5"/>

  <!-- STRIVER A2Z -->
  <text x="24" y="34" font-size="12" font-weight="600" fill="#a6adc8">STRIVER A2Z SHEET</text>
  <text x="676" y="34" font-size="12" font-weight="700" fill="#cba6f7" text-anchor="end">{total_csv} / {STRIVER_TOTAL}   {striver_pct}%</text>
  <rect x="24" y="42" width="652" height="13" rx="6.5" fill="#313244"/>
  <rect x="24" y="42" width="0"   height="13" rx="6.5" fill="url(#g1)" class="b1" filter="url(#glow)"/>
  <text x="24" y="72" font-size="10" fill="#45475a">Complete Striver's A2Z DSA Sheet — 455 problems</text>

  <!-- LEETCODE -->
  <text x="24" y="100" font-size="12" font-weight="600" fill="#a6adc8">LEETCODE 500+</text>
  <text x="676" y="100" font-size="12" font-weight="700" fill="#cba6f7" text-anchor="end">{lc_solved} / {LC_TARGET}   {lc_pct}%</text>
  <rect x="24" y="108" width="652" height="13" rx="6.5" fill="#313244"/>
  <rect x="24" y="108" width="0"   height="13" rx="6.5" fill="url(#g2)" class="b2" filter="url(#glow)"/>
  <text x="24" y="138" font-size="10" fill="#45475a">Reach 500 LeetCode solves — handle: {LEETCODE_USER}</text>

  <!-- CODEFORCES -->
  <text x="24" y="166" font-size="12" font-weight="600" fill="#a6adc8">CODEFORCES RATING 1200+</text>
  <text x="676" y="166" font-size="12" font-weight="700" fill="#cba6f7" text-anchor="end">Targeting {CF_TARGET}</text>
  <rect x="24" y="174" width="652" height="13" rx="6.5" fill="#313244"/>
  <rect x="24" y="174" width="0"   height="13" rx="6.5" fill="url(#g3)" class="b3" filter="url(#glow)"/>
  <text x="24" y="204" font-size="10" fill="#45475a">Active on Codeforces — handle: {CF_USER}</text>
</svg>"""

    with open("targets.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("targets.svg -> done")


# ─── ANIMATED RECENT ACTIVITY SVG ─────────────────────────
def generate_recent_activity_svg(problems, days=7):
    today = date.today()
    cutoff = today - timedelta(days=days)

    recent = []
    for p in problems:
        d = parse_date(p.get("Date", ""))
        if d and d >= cutoff:
            recent.append((d, p))
    recent.sort(key=lambda x: x[0], reverse=True)
    recent = recent[:8]

    if not recent:
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="700" height="80">
  <rect width="700" height="80" rx="12" fill="#1e1e2e"/>
  <text x="350" y="46" font-family="Segoe UI" font-size="13" fill="#585b70" text-anchor="middle">No problems logged in the last 7 days.</text>
</svg>"""
        with open("recent_activity.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        return

    ROW_H = 40
    H = 52 + len(recent) * ROW_H + 12

    def diff_col(d):
        d = d.lower().strip()
        if d == 'easy':   return '#a6e3a1', '#1e3a2f'
        if d == 'medium': return '#fab387', '#3a2a1e'
        if d == 'hard':   return '#f38ba8', '#3a1e24'
        return '#89b4fa', '#1e2a3a'

    rows_svg = ""
    for i, (d, p) in enumerate(recent):
        y_base = 58 + i * ROW_H
        bg = "#181825" if i % 2 == 0 else "#1e1e2e"
        prob = p.get('Problem', 'Unknown')[:42]
        plat = p.get('Platform', '')
        diff = p.get('Difficulty', '')
        dc, dbc = diff_col(diff)
        date_str = d.strftime('%d %b')

        # Fade-in animation per row
        delay = i * 0.08

        rows_svg += f"""
  <g style="animation: fadeIn 0.4s ease {delay:.2f}s both">
    <rect x="0" y="{y_base - 14}" width="700" height="{ROW_H}" fill="{bg}"/>
    <text x="16" y="{y_base + 7}" font-family="Segoe UI" font-size="12" fill="#cdd6f4">{i+1}.  {prob}</text>
    <text x="430" y="{y_base + 7}" font-family="Segoe UI" font-size="11" fill="#89b4fa">{plat}</text>
    <rect x="538" y="{y_base - 8}" width="68" height="20" rx="10" fill="{dbc}"/>
    <text x="572" y="{y_base + 7}" font-family="Segoe UI" font-size="11" fill="{dc}" text-anchor="middle">{diff}</text>
    <text x="682" y="{y_base + 7}" font-family="Segoe UI" font-size="11" fill="#6c7086" text-anchor="end">{date_str}</text>
  </g>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="{H}" viewBox="0 0 700 {H}">
  <defs>
    <style>
      @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(6px) }} to {{ opacity:1; transform:translateY(0) }} }}
    </style>
    <linearGradient id="hbg" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#1e1e2e"/>
      <stop offset="100%" stop-color="#181825"/>
    </linearGradient>
  </defs>
  <rect width="700" height="{H}" rx="14" fill="url(#hbg)"/>
  <rect x="1" y="1" width="698" height="{H-2}" rx="14" fill="none" stroke="#313244" stroke-width="1.5"/>
  <text x="16"  y="28" font-family="Segoe UI" font-size="10" font-weight="700" fill="#45475a" letter-spacing="1">PROBLEM</text>
  <text x="430" y="28" font-family="Segoe UI" font-size="10" font-weight="700" fill="#45475a" letter-spacing="1">PLATFORM</text>
  <text x="572" y="28" font-family="Segoe UI" font-size="10" font-weight="700" fill="#45475a" text-anchor="middle" letter-spacing="1">DIFF</text>
  <text x="682" y="28" font-family="Segoe UI" font-size="10" font-weight="700" fill="#45475a" text-anchor="end" letter-spacing="1">DATE</text>
  <line x1="0" y1="36" x2="700" y2="36" stroke="#313244" stroke-width="1"/>
  {rows_svg}
</svg>"""

    with open("recent_activity.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("recent_activity.svg -> done")


# ─── BUILD README ──────────────────────────────────────────
def build_readme(problems, lc):
    now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

    total         = len(problems)
    lc_solved     = max(lc['total'], 106)
    striver_pct   = min(100, round(total / STRIVER_TOTAL * 100, 1))
    lc_pct        = min(100, round(lc_solved / LC_TARGET * 100, 1))
    cur_streak, _ = compute_streak(problems)

    # Generate animated SVG files
    generate_targets_svg(total, lc_solved, striver_pct, lc_pct)
    generate_recent_activity_svg(problems, days=7)

    header_url = (
        "https://capsule-render.vercel.app/api?type=waving"
        "&color=0:0d1117,50:1a2332,100:0d1117"
        "&height=220&section=header"
        "&text=DSA%20FORGE%20v4&fontSize=72&fontColor=58a6ff"
        "&animation=twinkling&fontAlignY=40"
        "&desc=Vikram%20Negi%20%7C%20Code%20.%20Survive%20.%20Win"
        "&descAlignY=65&descColor=c9d1d9"
    )
    anim_graph = (
        f"https://github-readme-activity-graph.vercel.app/graph"
        f"?username={GITHUB_USER}"
        f"&bg_color=0d1117&color=58a6ff&line=58a6ff"
        f"&point=ffffff&area=true&area_color=121d2f"
        f"&hide_border=true&custom_title=LIVE%20CODING%20PULSE"
    )

    lines = []
    a = lines.append   # shorthand

    # ── HEADER ──
    a('<div align="center">\n')
    a(f'![]({header_url})\n')

    # ── BADGES ──
    a(
        f'[![Gmail](https://img.shields.io/badge/GMAIL-vikramnegi0021-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{GMAIL})  '
        f'[![LeetCode](https://img.shields.io/badge/LEETCODE-{LEETCODE_USER}-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/{LEETCODE_USER})  \n'
        f'[![Codeforces](https://img.shields.io/badge/CODEFORCES-{CF_USER}-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white)](https://codeforces.com/profile/{CF_USER})  '
        f'[![Streak](https://img.shields.io/badge/STREAK-{cur_streak}_DAYS-FF7B00?style=for-the-badge&logo=fire&logoColor=white)](https://leetcode.com/{LEETCODE_USER})\n'
    )
    a('</div>\n\n---\n')

    # ── SYSTEM PERFORMANCE ──
    a('## System Performance\n')
    a('<div align="center">\n')
    a(f'<img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true" height="175" />  ')
    a(f'<img src="https://github-readme-streak-stats.herokuapp.com/?user={GITHUB_USER}&theme=tokyonight&hide_border=true" height="175" />\n')
    a('</div>\n\n---\n')

    # ── ACTIVITY GRAPH ──
    a('## Activity Flow\n')
    a('<div align="center">\n')
    a(f'<img src="{anim_graph}" width="100%" />\n')
    a('</div>\n\n---\n')

    # ── LEETCODE CARD ──
    a('## LeetCode\n')
    a('<div align="center">\n')
    a(f'<img src="https://leetcard.jacoblin.cool/{LEETCODE_USER}?theme=dark&font=Karma&ext=heatmap&border=0" width="100%" />\n')
    a('</div>\n\n---\n')

    # ── TARGETS SVG ──
    a('## Targets\n')
    a('<div align="center">\n')
    a('<img src="targets.svg" width="700" />\n')
    a('</div>\n\n---\n')

    # ── RECENT ACTIVITY SVG ──
    a('## Recent Activity\n')
    a('<div align="center">\n')
    a('<img src="recent_activity.svg" width="700" />\n')
    a('</div>\n\n---\n')

    # ── FOOTER ──
    a(f'<div align="center">\n\n`Last Sync: {now_ist.strftime("%d %b %Y  |  %I:%M %p IST")}`\n\n</div>\n')

    return "\n".join(lines)


def main():
    print("DSA Forge — starting sync...")
    lc_stats      = fetch_leetcode_stats()
    problems_data = read_csv()
    readme        = build_readme(problems_data, lc_stats)
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme)
    print("Done — README.md + targets.svg + recent_activity.svg updated.")

if __name__ == "__main__":
    main()
    
