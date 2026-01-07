import pandas as pd
import sqlite3

# ====== 1. Excel File Path ======
EXCEL_PATH = "data\datasets\student_dataset.xlsx"   # <-- change if needed

# ====== 2. Load Excel ======
print("Loading Excel file...")
df = pd.read_excel(EXCEL_PATH)

# Clean column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# ====== 3. Connect SQLite DB ======
DB_PATH = "students.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ====== 4. Create Students Table ======
print("Creating table if not exists...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no TEXT PRIMARY KEY,
    name TEXT,
    gender TEXT,
    branch TEXT,
    credits INTEGER,
    cgpa REAL,
    result TEXT,
    degree_name TEXT,
    email_id TEXT,
    joining_year INTEGER,
    passed_year INTEGER,
    admission TEXT,
    company_placed TEXT
);
""")

# ====== 5. Insert Data ======
print("Inserting records...")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR REPLACE INTO students
        (roll_no, name, gender, branch, credits, cgpa, result,
         degree_name, email_id, joining_year, passed_year,
         admission, company_placed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(row["roll_no"]),
        str(row["name"]),
        str(row["gender"]),
        str(row["branch"]),
        int(row["credits"]),
        float(row["cgpa"]),
        str(row["result"]),
        str(row["degree_name"]),
        str(row["email_id"]),
        int(row["joining_year"]),
        int(row["passed_year"]),
        str(row["admission"]),
        str(row["company_placed"])
    ))

conn.commit()
conn.close()

print("🎉 Student Database Created Successfully!")
print("Database file saved as: students.db")
