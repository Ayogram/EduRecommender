import sqlite3
import os

db_path = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)\database\edurecommender.db"

def check_db():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables = ["users", "courses", "student_courses", "recommendations"]
    for table in tables:
        try:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Table {table}: {count} rows")
        except Exception as e:
            print(f"Error reading table {table}: {e}")

    # Check for courses with missing tags or descriptions
    try:
        no_tags = cursor.execute("SELECT COUNT(*) FROM courses WHERE tags IS NULL OR tags = '' OR tags = '[]'").fetchone()[0]
        print(f"Courses without tags: {no_tags}")
    except:
        pass

    conn.close()

if __name__ == "__main__":
    check_db()
