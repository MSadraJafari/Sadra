#!/usr/bin/env python3
"""
git_hourly_heatmap_en.py
Generate an HTML heatmap showing number of commits per hour of week
based on your local git log.
Run it inside a git repo:
    python3 git_hourly_heatmap_en.py > heatmap.html
Then open heatmap.html in your browser.
"""
import subprocess, sys
from datetime import datetime

SINCE = "1 year ago"  # or None for all history

# Get commit timestamps
git_cmd = ["git", "log", "--pretty=%ad", "--date=format:%Y-%m-%d %H"]
if SINCE:
    git_cmd.insert(2, f"--since={SINCE}")

try:
    output = subprocess.check_output(git_cmd, stderr=subprocess.DEVNULL, text=True)
except subprocess.CalledProcessError:
    print("Error: make sure you're inside a git repository.", file=sys.stderr)
    sys.exit(1)

# Initialize 7x24 matrix
counts = [[0]*24 for _ in range(7)]
total = 0

for line in output.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        dt = datetime.strptime(line, "%Y-%m-%d %H")
    except ValueError:
        continue
    weekday = dt.weekday()  # Monday=0
    hour = dt.hour
    counts[weekday][hour] += 1
    total += 1

max_count = max((c for row in counts for c in row), default=0)

# HTML output
print("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Git Commit Hourly Heatmap</title>
<style>
  body { font-family: sans-serif; padding: 20px; }
  table { border-collapse: collapse; }
  td { width: 28px; height: 20px; border:1px solid #eee; }
  th, td.label { font-size: 12px; text-align:center; padding: 3px; }
  .cell { transition: background-color 0.2s; }
  .legend { margin-top: 20px; }
</style>
</head>
<body>
<h2>Git Commit Hourly Heatmap</h2>
<p>Period: <strong>{}</strong> — Total commits: {}</p>
<table>
  <thead>
    <tr><th>Day \\ Hour</th>""".format(SINCE if SINCE else "All time", total))

for h in range(24):
    print(f"<th>{h:02d}</th>")
print("</tr></thead><tbody>")

day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

for d_idx, dname in enumerate(day_names):
    print(f"<tr><td class='label'>{dname}</td>")
    for h in range(24):
        c = counts[d_idx][h]
        if max_count > 0:
            intensity = int((c / max_count) * 255)
        else:
            intensity = 0
        r = 240 - int(intensity * 0.4)
        g = 240
        b = 240 - intensity
        bgcolor = f"rgb({r},{g},{b})"
        print(f"<td class='cell' title='{c} commits' style='background:{bgcolor}'></td>")
    print("</tr>")

print("""</tbody></table>
<div class='legend'>
  <p>⬜ = no commits &nbsp;&nbsp; 🟩 = more commits</p>
</div>
</body>
</html>""")
