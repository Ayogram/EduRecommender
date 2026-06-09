import sqlite3
import os

def patch_db(db_path=None):
    if not db_path:
        try:
            from flask import current_app
            db_path = current_app.config["DATABASE_PATH"]
        except Exception:
            # Fallback to local default path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "database", "edurecommender.db")

    if not os.path.exists(db_path):
        print(f"Database not found at '{db_path}'. init_db() will handle it on next launch.")
        return

    print(f"Patching database at: {db_path}")
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
        ("gpa", "REAL DEFAULT 0.0"),
        ("past_grades", "TEXT DEFAULT '{}'"),
        ("profile_completed", "INTEGER DEFAULT 0")
    ]
    for col, dtype in user_patches:
        if not column_exists("users", col):
            print(f"Adding column {col} to users...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")

    # 2. Patch Courses
    course_patches = [
        ("department", "TEXT"),
        ("prerequisites", "TEXT DEFAULT 'None'"),
        ("credits", "INTEGER DEFAULT 3"),
        ("tags", "TEXT DEFAULT '[]'")
    ]
    for col, dtype in course_patches:
        if not column_exists("courses", col):
            print(f"Adding column {col} to courses...")
            cursor.execute(f"ALTER TABLE courses ADD COLUMN {col} {dtype}")

    # 3. Patch Student Courses
    if not column_exists("student_courses", "grade"):
        print("Adding column grade to student_courses...")
        cursor.execute("ALTER TABLE student_courses ADD COLUMN grade TEXT DEFAULT 'N/A'")

    # 4. Ensure Notifications table
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
    if not column_exists("recommendations", "success_probability"):
        print("Adding column success_probability to recommendations...")
        cursor.execute("ALTER TABLE recommendations ADD COLUMN success_probability REAL DEFAULT 0.0")

    # 6. Backfill profile_completed for existing users who already filled in their profile
    #    This ensures no returning user is incorrectly sent back to onboarding
    if column_exists("users", "profile_completed"):
        print("Backfilling profile_completed for existing users with academic_field + department set...")
        cursor.execute("""
            UPDATE users
            SET profile_completed = 1
            WHERE profile_completed = 0
              AND academic_field IS NOT NULL AND academic_field != ''
              AND department IS NOT NULL AND department != ''
        """)
        updated = cursor.rowcount
        if updated:
            print(f"  Backfilled {updated} user(s).")

    # 7. Patch Module Lessons
    if not column_exists("module_lessons", "video_url"):
        print("Adding column video_url to module_lessons...")
        cursor.execute("ALTER TABLE module_lessons ADD COLUMN video_url TEXT")

    # 8. Check and seed courses if empty or >= 500 (migrating back to custom courses)
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    if count >= 500 or count == 0:
        print("Migrating back to the custom 134 course catalog from seed_data_v2.py...")
        cursor.execute("DELETE FROM courses")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'courses'")
        except Exception:
            pass
        # Clear student_courses, recommendations, and modules
        cursor.execute("DELETE FROM student_courses")
        cursor.execute("DELETE FROM recommendations")
        cursor.execute("DELETE FROM course_modules")
        
        import sys
        root_dir = os.path.dirname(os.path.abspath(__file__))
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        import json
        from seed_data_v2 import COURSES
        for title, desc, dept, cat, diff, prereq, creds, tags in COURSES:
            cursor.execute(
                """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
            )

    conn.commit()
    conn.close()
    print("Database patched successfully.")

if __name__ == "__main__":
    patch_db()
