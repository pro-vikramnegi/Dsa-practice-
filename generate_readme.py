import csv, json, urllib.request, os
from datetime import datetime, timedelta, date, timezone
from collections import defaultdict

# ─── CONFIG ───────────────────────────────────────────────
LEETCODE_USER = "__vikram21"
CF_USER       = "__vikram21"
GITHUB_USER   = "vikramnegi21"
GMAIL         = "vikramnegi0021@gmail.com"
CSV_FILE      = "problems.csv"
README_FILE   = "README.md"

LC_TARGET      = 500
CF_TARGET      = 1200
STREAK_TARGET  = 90
FALLBACK_STREAK = 70 
# ──────────────────────────────────────────────────────────

def fetch_leetcode_stats():
    url = f"https://leetcode-stats-api.herokuapp.com/{LEETCODE_USER}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            d = json.loads(r.read())
        if d.get("status") == "success":
            return {"total": d.get("totalSolved", 0), "easy": d.get("easySolved", 0), "medium": d.get("mediumSolved", 0)}
    except: pass
    return {"total": 109, "easy": 64, "medium": 45}

def fetch_leetcode_streak():
    url = "https://leetcode.com/graphql"
    query = "query userCal($u:String!){matchedUser(username:$u){userCalendar{streak}}}"
    payload = json.dumps({"query": query, "variables": {"u": LEETCODE_USER}}).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "Referer": "https://leetcode.com"})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())
        s = int(data["data"]["matchedUser"]["userCalendar"]["streak"])
        print(f"[OK] LC Streak: {s}")
        return s
    except: return 0

def read_csv():
    rows = []
    if not os.path.exists(CSV_FILE): 
        print(f"[ERR] {CSV_FILE} not found!")
        return []
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                clean_r = {str(k).strip(): str(v).strip() for k, v in r.items() if k}
                if any(clean_r.values()): rows.append(clean_r)
        print(f"[OK] Read {len(rows)} problems from CSV.")
    except Exception as e: print(f"[ERR] CSV: {e}")
    return rows

def parse_date(s):
    if not s: return None
    for fmt in ["%Y-%m-%d", "%d %b %Y", "%d %b", "%d-%m-%Y", "%b %d, %Y"]:
        try: return datetime.strptime(s.strip(), fmt).date()
        except: continue
    return None

def generate_heatmap_svg(problems):
    counts = defaultdict(int)
    for p in problems:
        # Aggressive Date Column Detection
        dt_val = None
        for key in p.keys():
            if 'date' in key.lower():
                dt_val = p[key]
                break
        
        d = parse_date(dt_val)
        if d: counts[d] += 1
    
    if not counts: print("[WARN] No valid dates found for Heatmap!")
    else: print(f"[OK] Heatmap found {len(counts)} active days.")

    today = date.today()
    end_date = today + timedelta(days=((6 - (today.weekday() + 1) % 7)))
    start_date = end_date - timedelta(weeks=24) + timedelta(days=1)
    
    CELL, GAP, PAD_L, PAD_T = 13, 3, 30, 30
    W, H = PAD_L + 24 * (CELL + GAP) + 14, PAD_T + 7 * (CELL + GAP) + 32
    
    grid, col, cur = [], [], start_date
    while cur <= end_date:
        col.append(cur)
        if cur.weekday() == 6:
            grid.append(col); col = []
        cur += timedelta(days=1)
    if col: grid.append(col)
    
    max_c = max(counts.values(), default=1) or 1
    cells = ""
    for ci, wk in enumerate(grid):
        delay = f"{round(0.02 * ci, 3)}s"
        for ri, d in enumerate(wk):
            if d > today: continue
            x, y, c = PAD_L + ci*(CELL+GAP), PAD_T + ri*(CELL+GAP), counts.get(d, 0)
            color = "#161b22" if c == 0 else ("#0e4429" if (c/max_c) < 0.25 else "#006d32" if (c/max_c) < 0.5 else "#26a641" if (c/max_c) < 0.75 else "#39d353")
            cells += f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{color}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay}" fill="freeze"/><title>{d}: {c} solved</title></rect>\n'

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" rx="12" fill="#0d1117"/><text x="{W//2}" y="17" font-family="monospace" font-size="10" fill="#3fb950" text-anchor="middle">DSA ACTIVITY // LAST 24 WEEKS</text>{cells}</svg>'
    with open("heatmap.svg", "w", encoding="utf-8") as f: f.write(svg)

def generate_targets_svg(lc_solved, cur_streak):
    W, H, BAR_X, BAR_MAX = 740, 260, 150, 560
    lc_pct = min(100, round(lc_solved/LC_TARGET*100, 1))
    s_pct = min(100, round(cur_streak/STREAK_TARGET*100, 1))

    rows = [
        ("LEETCODE 500+", f"{lc_solved}/{LC_TARGET}", lc_pct, "#89dceb", 70),
        ("CODEFORCES", "1200 Target", 20, "#89b4fa", 140),
        ("STREAK", f"{cur_streak}/{STREAK_TARGET}d", s_pct, "#f9e2af", 210)
    ]
    
    bars = ""
    for i, (lab, txt, pct, clr, y) in enumerate(rows):
        bw, delay = max(8, round(pct/100*BAR_MAX)), f"{round(0.3*i, 1)}s"
        bars += f'<text x="{BAR_X-5}" y="{y-12}" font-family="monospace" font-size="10" fill="{clr}" text-anchor="end">{lab}</text>'
        bars += f'<text x="{BAR_X+BAR_MAX}" y="{y-12}" font-family="monospace" font-size="11" fill="{clr}" text-anchor="end">{txt} ({pct}%)</text>'
        bars += f'<rect x="{BAR_X}" y="{y}" width="{BAR_MAX}" height="12" rx="6" fill="#1e1e2e"/>'
        bars += f'<rect x="{BAR_X}" y="{y}" width="0" height="12" rx="6" fill="{clr}"><animate attributeName="width" from="0" to="{bw}" dur="1.4s" begin="{delay}" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.6 1"/></rect>'

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" rx="14" fill="#11111b"/><text x="{W//2}" y="30" font-family="monospace" font-size="11" fill="#585b70" text-anchor="middle">// GOALS &amp; TARGETS //</text>{bars}</svg>'
    with open("targets.svg", "w", encoding="utf-8") as f: f.write(svg)

def main():
    problems = read_csv()
    lc = fetch_leetcode_stats()
    streak = max(fetch_leetcode_streak(), FALLBACK_STREAK)
    
    generate_heatmap_svg(problems)
    generate_targets_svg(lc['total'], streak)

    now = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).strftime("%d %b %Y | %I:%M %p IST")
    header = f"https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,100:0d1117&height=230&section=header&text=DSA%20FORGE%20v4&fontSize=78&fontColor=58a6ff&animation=twinkling&desc=Vikram%20Negi%20%7C%20Code%20.%20Survive%20.%20Win&descSize=18"
    
    content = [
        f'<div align="center">\n\n![]({header})\n\n',
        f'[![Gmail](https://img.shields.io/badge/GMAIL-{GMAIL.split("@")[0]}-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:{GMAIL})&nbsp;&nbsp;',
        f'[![LeetCode](https://img.shields.io/badge/LEETCODE-{LEETCODE_USER}-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/{LEETCODE_USER})\n\n',
        f'[![Codeforces](https://img.shields.io/badge/CODEFORCES-{CF_USER}-1F8ACB?style=for-the-badge&logo=codeforces&logoColor=white)](https://codeforces.com/profile/{CF_USER})&nbsp;&nbsp;',
        f'[![Streak](https://img.shields.io/badge/STREAK-{streak}%20DAYS-FF7B00?style=for-the-badge&logo=fire&logoColor=white)](https://leetcode.com/{LEETCODE_USER})\n\n',
        '</div>\n\n---\n\n## System Performance\n<div align="center">\n',
        f'<img src="https://github-readme-stats.vercel.app/api?username={GITHUB_USER}&show_icons=true&theme=tokyonight&hide_border=true" height="170" />&nbsp;',
        f'<img src="https://github-readme-streak-stats.herokuapp.com/?user={GITHUB_USER}&theme=tokyonight&hide_border=true" height="170" />\n</div>\n\n',
        f'---\n\n## Activity Flow\n<div align="center"><img src="https://github-readme-activity-graph.vercel.app/graph?username={GITHUB_USER}&bg_color=0d1117&color=58a6ff&line=1f6feb&point=58a6ff&area=true&hide_border=true" width="100%" /></div>\n\n',
        f'---\n\n## LeetCode Stats\n<div align="center"><img src="https://leetcard.jacoblin.cool/{LEETCODE_USER}?theme=dark&font=Karma&ext=heatmap&border=0&radius=12" width="96%" /></div>\n\n',
        '---\n\n## DSA Heatmap\n<div align="center"><img src="heatmap.svg" width="100%" /></div>\n\n',
        '---\n\n## Goals & Targets\n<div align="center"><img src="targets.svg" width="100%" /></div>\n\n',
        f'---\n<div align="center">`Last Sync : {now}`</div>'
    ]
    
    with open(README_FILE, "w", encoding="utf-8") as f: f.write("".join(content))

if __name__ == "__main__": main()
    
