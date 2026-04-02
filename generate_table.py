import csv

# 1. Read CSV (Yaqeen karlein ki aapki CSV mein 'Topic' aur 'Status' column hai)
rows = []
try:
    with open("problems.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)  # Header skip kar rahe hain
        for row in reader:
            if row: # Khali rows check karne ke liye
                rows.append(row)
except FileNotFoundError:
    print("Error: problems.csv file nahi mili!")
    exit()

# 2. Create Markdown Table (Naya Topic column add kiya hai)
table = "| Date | Topic | Problem | Platform | Difficulty | Status |\n"
table += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

for r in rows:
    # CSV order: Date, Problem, Platform, Difficulty, Topic, Status
    if len(r) >= 6:
        # Check status to add emoji for better look
        status = r[5]
        if "Done" in status or "Solved" in status:
            status = "✅ Done"
        elif "Revision" in status:
            status = "🔁 Revision"
            
        table += f"| {r[0]} | {r[4]} | {r[1]} | {r[2]} | {r[3]} | {status} |\n"

# 3. Read existing README
try:
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("Error: README.md file nahi mili!")
    exit()

# 4. Find table section markers
# Yaad rakhein ki README mein 'Repository Structure' wali heading honi chahiye
start = content.find("| Date")
end = content.find("## Repository Structure") # Heading ka pura naam match karein

if start == -1 or end == -1:
    print("Markers (| Date ya Repository Structure) nahi mile! Check README markers.")
    exit()

# 5. Replace table
new_content = content[:start] + table + "\n" + content[end:]

# 6. Write back to README
with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("README.md successfully update ho gaya!")
