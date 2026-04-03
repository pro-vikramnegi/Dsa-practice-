import csv

rows = []
with open("problems.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        rows.append(row)

table = "| Date | Problem | Platform | Difficulty | Topic | Status |\n"
table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

for r in rows:
    status_raw = r["Status"].strip().lower()
    if status_raw in ["done", "solved"]:
        status = "✅ Done"
    elif status_raw == "revision":
        status = "🔁 Revision"
    elif status_raw == "not clear":
        status = "❌ Not Clear"
    else:
        status = r["Status"]
    table += f"| {r['Date']} | {r['Problem']} | {r['Platform']} | {r['Difficulty']} | {r['Topic']} | {status} |\n"

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

start_marker = "| Date"
start = content.find(start_marker)

if start != -1:
    new_content = content[:start] + table
else:
    new_content = content + "\n\n" + table

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ README updated successfully!")
