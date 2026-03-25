"""
Seed the database with sample courses and test users for development.
Run:  python seed_data.py [admin_email] [admin_password]
"""

import os
import sys
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash

def seed(admin_email=None, admin_password=None):
    from app import create_app
    app = create_app()

    with app.app_context():
        from models.database import get_db, init_db

        init_db()
        db = get_db()

        # ── Sample Courses ──────────────────────────────────────────
        courses = [
            ("Introduction to Python", "Learn Python programming from scratch. Covers variables, loops, functions, and OOP.", "Programming", "beginner", '["python","programming","beginner"]'),
            ("Data Structures & Algorithms", "Master arrays, linked lists, trees, graphs, sorting, and searching algorithms.", "Computer Science", "intermediate", '["dsa","algorithms","data structures"]'),
            ("Machine Learning Fundamentals", "Understand supervised and unsupervised learning, regression, classification, and clustering.", "AI & ML", "intermediate", '["machine learning","ai","scikit-learn"]'),
            ("Web Development with Flask", "Build modern web applications using Python Flask, templates, and REST APIs.", "Web Development", "intermediate", '["flask","web","python","backend"]'),
            ("Database Systems", "Learn relational databases, SQL, normalization, and transaction management.", "Computer Science", "intermediate", '["database","sql","relational"]'),
            ("Deep Learning with TensorFlow", "Neural networks, CNNs, RNNs, and transfer learning with TensorFlow.", "AI & ML", "advanced", '["deep learning","tensorflow","neural networks"]'),
            ("Cybersecurity Essentials", "Network security, cryptography, ethical hacking, and vulnerability assessment.", "Security", "intermediate", '["security","hacking","cryptography"]'),
            ("Cloud Computing", "AWS, Azure, GCP fundamentals, deployment, containerization with Docker.", "Cloud", "intermediate", '["cloud","aws","docker","devops"]'),
            ("Statistics for Data Science", "Probability, distributions, hypothesis testing, and Bayesian statistics.", "Mathematics", "beginner", '["statistics","math","data science"]'),
            ("Natural Language Processing", "Text processing, sentiment analysis, word embeddings, and transformers.", "AI & ML", "advanced", '["nlp","text","transformers","ai"]'),
            ("JavaScript Essentials", "Modern JavaScript ES6+, DOM manipulation, async programming, and APIs.", "Programming", "beginner", '["javascript","web","frontend"]'),
            ("Operating Systems", "Processes, threads, memory management, file systems, and scheduling.", "Computer Science", "advanced", '["os","systems","kernel"]'),
            ("Computer Networks", "TCP/IP, DNS, HTTP, routing, and network security fundamentals.", "Computer Science", "intermediate", '["networking","tcp","protocols"]'),
            ("Software Engineering", "Software development lifecycle, agile, testing, design patterns, and UML.", "Computer Science", "intermediate", '["software engineering","agile","design patterns"]'),
            ("Mobile App Development", "Build cross-platform mobile apps using React Native and Flutter.", "Mobile", "intermediate", '["mobile","react native","flutter"]'),
            ("Data Visualization", "Create compelling visualizations with Matplotlib, Seaborn, and D3.js.", "Data Science", "beginner", '["visualization","matplotlib","d3"]'),
            ("Artificial Intelligence", "Search algorithms, knowledge representation, planning, and AI ethics.", "AI & ML", "advanced", '["ai","search","planning"]'),
            ("Linux Administration", "Linux commands, shell scripting, user management, and server configuration.", "Systems", "beginner", '["linux","bash","sysadmin"]'),
            ("Discrete Mathematics", "Logic, sets, combinatorics, graph theory, and number theory.", "Mathematics", "beginner", '["math","logic","discrete"]'),
            ("Big Data Analytics", "Hadoop, Spark, MapReduce, and large-scale data processing techniques.", "Data Science", "advanced", '["big data","spark","hadoop"]'),
        ]

        if db.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO courses (title, description, category, difficulty, tags) VALUES (?, ?, ?, ?, ?)",
                courses,
            )
            print(f"[OK] Inserted {len(courses)} courses.")
        else:
            print("[INFO] Courses already seeded.")

        # ── Admin Account ───────────────────────────────────────────
        if admin_email:
            existing_admin = db.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
            if not existing_admin:
                db.execute(
                    """INSERT INTO users (name, email, password_hash, role, interests)
                       VALUES (?, ?, ?, 'admin', '[]')""",
                    (
                        "Administrator",
                        admin_email,
                        generate_password_hash(admin_password or "Admin@123"),
                    ),
                )
                print(f"[OK] Created admin account: {admin_email}")
            else:
                print(f"[INFO] Admin account {admin_email} already exists.")
        else:
            if db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0] == 0:
                 print("[WARNING] No admin credentials provided. Skipping admin initialization.")
            else:
                print("[INFO] Admin account already exists.")

        # ── Sample Students ─────────────────────────────────────────
        if db.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0] == 0:
            students = [
                ("Alice Johnson", "alice@example.com", "User@123", '["python","machine learning","statistics"]'),
                ("Bob Smith", "bob@example.com", "User@123", '["web","javascript","flask"]'),
                ("Charlie Brown", "charlie@example.com", "User@123", '["security","networking","linux"]'),
                ("Diana Prince", "diana@example.com", "User@123", '["ai","deep learning","nlp"]'),
                ("Eve Adams", "eve@example.com", "User@123", '["data science","visualization","big data"]'),
            ]
            for name, email, pwd, interests in students:
                db.execute(
                    """INSERT INTO users (name, email, password_hash, role, interests)
                       VALUES (?, ?, ?, 'user', ?)""",
                    (name, email, generate_password_hash(pwd), interests),
                )
            print(f"[OK] Created {len(students)} sample students.")

            # ── Sample Enrollments & Ratings ────────────────────────
            enrollments = [
                (1, 1, 4.5, 1), (1, 3, 4.0, 1), (1, 9, 3.5, 1), (1, 6, 4.2, 0),
                (2, 1, 3.0, 1), (2, 4, 4.5, 1), (2, 11, 4.0, 1), (2, 14, 3.8, 0),
                (3, 7, 4.5, 1), (3, 13, 4.0, 1), (3, 18, 3.5, 1), (3, 12, 3.0, 0),
                (4, 3, 4.5, 1), (4, 6, 4.8, 1), (4, 10, 4.2, 1), (4, 17, 4.0, 0),
                (5, 9, 4.0, 1), (5, 16, 4.5, 1), (5, 20, 3.8, 1), (5, 3, 3.5, 0),
            ]
            admin_count = db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
            for uid, cid, rating, completed in enrollments:
                db.execute(
                    "INSERT INTO student_courses (user_id, course_id, rating, completed) VALUES (?, ?, ?, ?)",
                    (uid + admin_count, cid, rating, completed),
                )
            print(f"[OK] Created {len(enrollments)} sample enrollments.")
        else:
            print("[INFO] Sample students already exist.")

        db.commit()
        print("\n[DONE] Database seeded successfully!")

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else None
    password = sys.argv[2] if len(sys.argv) > 2 else "Admin@123"
    seed(email, password)
