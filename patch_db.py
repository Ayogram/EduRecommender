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

    # 8. Check and seed courses if empty, < 110, or >= 500, or if database contains old course codes
    cursor.execute("SELECT COUNT(*) FROM courses WHERE title LIKE 'CSC %' OR title LIKE 'MAT %'")
    has_codes = cursor.fetchone()[0] > 0

    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    if count < 110 or count >= 500 or has_codes:
        print("Migrating to the custom 112 course catalog without course codes...")
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

        CS_COURSES = [
            ("Introduction to Computing", "History, hardware, software, and basic logic.", "Computer Science", "Computer Science", "beginner", "None", 3, ["Basics", "Intro"]),
            ("Programming in Python", "Introductory programming concepts using Python.", "Computer Science", "Computer Science", "beginner", "None", 4, ["Python", "Programming"]),
            ("Algebra and Trigonometry", "Fundamental math for scientists.", "Others", "Others", "beginner", "None", 3, ["Math", "Algebra"]),
            ("Data Structures", "Arrays, Linked Lists, Stacks, Queues, and Trees.", "Computer Science", "Computer Science", "intermediate", "Programming in Python", 4, ["Data Structures", "Algorithms"]),
            ("Java Programming", "Classes, inheritance, and polymorphism in Java.", "Computer Science", "Computer Science", "intermediate", "Programming in Python", 4, ["Java", "OOP"]),
            ("Computer Architecture", "Digital logic, CPU design, and assembly language.", "Computer Science", "Computer Science", "intermediate", "Introduction to Computing", 3, ["Hardware", "Digital Logic"]),
            ("Discrete Mathematics", "Sets, graphs, and combinatorics for CS.", "Others", "Others", "intermediate", "Algebra and Trigonometry", 3, ["Math", "Discrete"]),
            ("Operating Systems", "Kernels, processes, memory management, and file systems.", "Computer Science", "Computer Science", "intermediate", "Data Structures, Computer Architecture", 4, ["OS", "Systems"]),
            ("Database Management Systems", "Relational algebra, SQL, and database design.", "Computer Science", "Computer Science", "intermediate", "Data Structures", 4, ["SQL", "Databases"]),
            ("Software Engineering I", "SDLC, requirements, and system design.", "Computer Science", "Computer Science", "intermediate", "Java Programming", 3, ["SE", "Design"]),
            ("Algorithm Design & Analysis", "Big O notation, sorting, and dynamic programming.", "Computer Science", "Computer Science", "intermediate", "Data Structures", 3, ["Algorithms", "Logic"]),
            ("Theory of Computation", "Automata, formal languages, and computability.", "Computer Science", "Computer Science", "intermediate", "Discrete Mathematics", 3, ["Theory", "Automata"]),
            ("Computer Networks", "OSI model, TCP/IP, and network security.", "Computer Science", "Computer Science", "intermediate", "Operating Systems", 3, ["Networking", "TCP/IP"]),
            ("Artificial Intelligence", "Search algorithms, expert systems, and ML basics.", "Computer Science", "Computer Science", "advanced", "Algorithm Design & Analysis, Algebra and Trigonometry", 4, ["AI", "Intelligence"]),
            ("Human Computer Interaction", "UI/UX design principles and user testing.", "Computer Science", "Computer Science", "advanced", "Software Engineering I", 3, ["UI", "UX"]),
            ("Compiler Construction", "Lexical analysis, parsing, and code generation.", "Computer Science", "Computer Science", "advanced", "Theory of Computation", 3, ["Compilers", "Languages"]),
            ("Machine Learning", "Supervised, unsupervised and deep learning.", "Computer Science", "Computer Science", "advanced", "Artificial Intelligence, Algebra and Trigonometry", 4, ["ML", "Data Science"]),
            ("Project Management", "Agile, Waterfall, and project tracking.", "Computer Science", "Computer Science", "advanced", "Software Engineering I", 3, ["Management", "PM"]),
            ("Final Year Project", "Independent research and development.", "Computer Science", "Computer Science", "advanced", "Operating Systems, Database Management Systems, Software Engineering I, Algorithm Design & Analysis, Theory of Computation, Computer Networks", 6, ["Research", "Development"])
        ]
        for title, desc, dept, cat, diff, prereq, creds, tags in CS_COURSES:
            cursor.execute(
                """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
            )
        print(f"Successfully seeded {len(COURSES) + len(CS_COURSES)} courses.")

    conn.commit()
    conn.close()
    print("Database patched successfully.")

if __name__ == "__main__":
    patch_db()
