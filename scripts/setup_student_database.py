"""
Setup Student Database - Convert Excel to SQLite
Creates a queryable SQL database from student_dataset.xlsx
"""
import sqlite3
import pandas as pd
import sys
import io

# Fix Windows encoding
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*70)
print("STUDENT DATABASE SETUP")
print("="*70 + "\n")

# Load Excel file
print("Loading student_dataset.xlsx...")
df = pd.read_excel('data/rawdata/student_dataset.xlsx')
print(f"✓ Loaded {len(df)} student records")
print(f"✓ Columns: {list(df.columns)}\n")

# Create SQLite database
print("Creating SQLite database...")
conn = sqlite3.connect('app/database/students.db')

# Save to database
df.to_sql('students', conn, if_exists='replace', index=False)
print(f"✓ Created 'students' table with {len(df)} rows\n")

# Create indices for fast queries
print("Creating indices...")
cursor = conn.cursor()

# Get column names dynamically
columns = df.columns.tolist()

# Create indices on common query columns
if 'student_id' in [c.lower() for c in columns]:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id)")
    print("✓ Index on student_id")

if 'name' in [c.lower() for c in columns]:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON students(name)")
    print("✓ Index on name")

if 'department' in [c.lower() for c in columns]:
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_department ON students(department)")
    print("✓ Index on department")

conn.commit()

# Test query
print("\nTesting database...")
test_query = "SELECT * FROM students LIMIT 3"
result = pd.read_sql_query(test_query, conn)
print(f"✓ Test query successful")
print(f"\nSample data:")
print(result.to_string())

conn.close()

print("\n" + "="*70)
print("DATABASE SETUP COMPLETE!")
print("="*70)
print(f"\nDatabase location: app/database/students.db")
print(f"Total records: {len(df)}")
print(f"Ready for SQL queries!")
