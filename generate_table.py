import csv

# 1. Read CSV
rows = []
try:
    with open("problems.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # header skip
        for row in reader:
            if row:
                rows.append(row)
except FileNotFoundError:
    print("Error: problems.csv nahi mili!")
    exit()

# 2. Create Table Structure (Sahi Column Order ke saath)
table = "| Date | Topic | Problem | Platform | Difficulty | Status |\n"
table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

for r in rows:
    # CSV Order: Date(0), Topic(1), Problem(2), Platform(3), Difficulty(4), Status(5)
    date = r[0]
    topic = r[1]
    problem = r[2]
    platform = r[3]
    difficulty = r[4]
    status_raw = r[5].strip()

    # Status Emoji Logic
    if "Done" in status_raw or "Solved" in status_raw:
        status = "✅ Done"
    elif "Revision" in status_raw:
        status = "🔁 Revision"
    else:
        status = status_raw

    # Table mein columns sahi sequence mein set kiye hain
    table += f"| {date} | {topic} | {problem} | {platform} | {difficulty} | {status} |\n"

# 3. Read README
try:
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: README.md nahi mili!")
    exit()

# 4. Markers dhundna
start = content.find("| Date")
# Check karein ki README mein exact yehi heading hai ya nahi
end = content.find("## Repository Structure") 

if start == -1 or end == -1:
    print("Markers nahi mile! Check karein README mein '| Date' aur '## Repository Structure' hai.")
    exit()

# 5. Replace and Write
new_content = content[:start] + table + "\n" + content[end:]
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("README.md successfully update ho gaya!")
