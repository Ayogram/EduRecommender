import sqlite3
import os

db_path = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)\database\edurecommender.db"

def patch_db():
    if not os.path.exists(db_path):
        print("Database not found. init_db() will handle it on next launch.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Helper to check if column exists
    def column_exists(table, column):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row['name'] for row in cursor.fetchall()]
        return column in columns

    # 1. Patch Users
    user_patches = [
        ("nickname", "TEXT"),
        ("department", "TEXT"),
        ("gpa", "REAL DEFAULT 0.0")
    ]
    for col, dtype in user_patches:
        if not column_exists("users", col):
            print(f"Adding column {col} to users...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")

    # 2. Patch Courses
    course_patches = [
        ("department", "TEXT"),
        ("prerequisites", "TEXT DEFAULT 'None'"),
        ("credits", "INTEGER DEFAULT 3")
    ]
    for col, dtype in course_patches:
        if not column_exists("courses", col):
            print(f"Adding column {col} to courses...")
            cursor.execute(f"ALTER TABLE courses ADD COLUMN {col} {dtype}")

    # 3. Patch Student Courses
    if not column_exists("student_courses", col := "grade"):
        print(f"Adding column {col} to student_courses...")
        cursor.execute(f"ALTER TABLE student_courses ADD COLUMN {col} TEXT DEFAULT 'N/A'")

    # 4. Ensure Notifications table (manually handled just in case)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        message     TEXT    NOT NULL,
        is_read     INTEGER DEFAULT 0,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Patch Recommendations
    if not column_exists("recommendations", col := "success_probability"):
        print(f"Adding column {col} to recommendations...")
        cursor.execute(f"ALTER TABLE recommendations ADD COLUMN {col} REAL DEFAULT 0.0")

    conn.commit()
    conn.close()
    print("Database patched successfully.")

if __name__ == "__main__":
    patch_db()
