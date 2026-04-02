import csv

# =======================
# 1. Read CSV
# =======================
rows = []
with open("problems.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        rows.append(row)

# =======================
# 2. Generate Table
# =======================
table = "| Date | Problem | Platform | Difficulty | Topic | Status |\n"
table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

for r in rows:
    status_raw = r["Status"].strip().lower()

    # Emoji logic
    if status_raw in ["done", "solved"]:
        status = "✅ Done"
    elif status_raw == "revision":
        status = "🔁 Revision"
    elif status_raw == "not clear":
        status = "❌ Not Clear"
    else:
        status = r["Status"]

    table += f"| {r['Date']} | {r['Problem']} | {r['Platform']} | {r['Difficulty']} | {r['Topic']} | {status} |\n"

# =======================
# 3. Update README (NO END MARKER NEEDED)
# =======================
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "| Date"

start = content.find(start_marker)

if start != -1:
    new_content = content[:start] + table
else:
    # agar table nahi mila toh end me add kar de
    new_content = content + "\n\n" + table

# write back
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ README updated successfully!")
