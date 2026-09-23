import json, os, urllib.request

USER = os.environ.get("GH_USER", "RohitManvar")
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionCount date weekday}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = cal["weeks"]
total = cal["totalContributions"]

THEMES = {
    "light": {"bg": "#ffffff", "text": "#59636e", "levels": ["#eff2f5", "#b6d6f8", "#6aa7ec", "#2f7fdd", "#0969da"]},
    "dark": {"bg": "#0d1117", "text": "#9198a1", "levels": ["#151b23", "#0d2d5c", "#1158a8", "#2f81f7", "#79c0ff"]},
}

CELL, GAP, LEFT, TOP = 11, 3, 32, 22
STEP = CELL + GAP
W = LEFT + len(weeks) * STEP + 8
H = TOP + 7 * STEP + 26
DUR = 2.4  # seconds for the full sweep

counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
peak = max(counts) or 1

def level(c):
    if c == 0:
        return 0
    r = c / peak
    return 1 if r <= 0.25 else 2 if r <= 0.5 else 3 if r <= 0.75 else 4

def build(theme):
    t = THEMES[theme]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,sans-serif">',
        "<style>.c{opacity:0;animation:in .45s ease-out forwards}@keyframes in{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:none}}"
        ".l{opacity:0;animation:in .6s ease-out forwards}</style>",
        f'<rect width="{W}" height="{H}" rx="8" fill="{t["bg"]}"/>',
    ]
    last_month = None
    for i, w in enumerate(weeks):
        m = w["contributionDays"][0]["date"][5:7]
        if m != last_month and i < len(weeks) - 2:
            name = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(m) - 1]
            out.append(f'<text class="l" style="animation-delay:{i / len(weeks) * DUR:.2f}s" x="{LEFT + i * STEP}" y="14" font-size="10" fill="{t["text"]}">{name}</text>')
            last_month = m
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        out.append(f'<text x="0" y="{TOP + row * STEP + 9}" font-size="9" fill="{t["text"]}">{label}</text>')
    for i, w in enumerate(weeks):
        delay = i / len(weeks) * DUR
        for d in w["contributionDays"]:
            x, y = LEFT + i * STEP, TOP + d["weekday"] * STEP
            out.append(
                f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{t["levels"][level(d["contributionCount"])]}"><title>{d["date"]}: {d["contributionCount"]}</title></rect>'
            )
    out.append(
        f'<text class="l" style="animation-delay:{DUR:.2f}s" x="{LEFT}" y="{H - 8}" font-size="10" fill="{t["text"]}">'
        f"{total:,} contributions in the last year</text>"
    )
    out.append("</svg>")
    return "\n".join(out)

os.makedirs("dist", exist_ok=True)
for theme in THEMES:
    with open(f"dist/contributions-{theme}.svg", "w") as f:
        f.write(build(theme))
