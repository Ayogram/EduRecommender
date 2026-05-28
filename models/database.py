"""
Database helper – thin wrapper around sqlite3 for the application.
Provides get_db() for per-request connections and init_db() for schema creation.
"""

import os
import sqlite3
import json
from flask import g, current_app

# ── Schema DDL ──────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    password_hash   TEXT,
    google_id       TEXT    UNIQUE,
    profile_picture TEXT    DEFAULT '/static/img/default_avatar.png',
    role            TEXT    NOT NULL DEFAULT 'user'  CHECK(role IN ('user','admin','super_admin')),
    status          TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('active','suspended')),
    interests       TEXT    DEFAULT '[]',
    nickname        TEXT,
    academic_field  TEXT,
    department      TEXT,
    gpa             REAL    DEFAULT 0.0,
    is_verified     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    department    TEXT,
    category      TEXT NOT NULL,
    difficulty    TEXT NOT NULL CHECK(difficulty IN ('beginner','intermediate','advanced')),
    prerequisites TEXT DEFAULT 'None',
    credits       INTEGER DEFAULT 3,
    tags          TEXT DEFAULT '[]',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_courses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rating      REAL    DEFAULT 0 CHECK(rating >= 0 AND rating <= 5),
    grade       TEXT    DEFAULT 'N/A',
    completed   INTEGER DEFAULT 0,
    current_module_id INTEGER,
    current_lesson_id INTEGER,
    progress    REAL    DEFAULT 0.0,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);

CREATE TABLE IF NOT EXISTS course_modules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    description TEXT,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS module_lessons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    content     TEXT,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS module_exams (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    questions   TEXT    NOT NULL,  -- JSON string of MCQs
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exam_results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    score       REAL    NOT NULL,
    attempts    INTEGER DEFAULT 1,
    best_score  REAL    NOT NULL,
    history     TEXT    DEFAULT '[]', -- JSON string of scores
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    score               REAL    NOT NULL,
    success_probability REAL    DEFAULT 0.0,
    explanation         TEXT,
    method              TEXT    CHECK(method IN ('content','collaborative','hybrid')),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject         TEXT    NOT NULL,
    message         TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','resolved')),
    admin_response  TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message     TEXT    NOT NULL,
    is_read     INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Return the per-request database connection (stored on Flask `g`)."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


COURSES_SEED = [
    # Computer Science
    ("Introduction to Python", "Learn the basics of programming with Python.", "Computer Science", "Programming", "beginner", "None", 3, ["python", "coding", "basics"]),
    ("Data Structures & Algorithms", "Fundamental concepts of algorithms and data organization.", "Computer Science", "Software Engineering", "intermediate", "Introduction to Python", 4, ["algorithms", "data structures", "performance"]),
    ("Artificial Intelligence", "Concepts of machine learning, neural networks, and AI.", "Computer Science", "Artificial Intelligence", "advanced", "Data Structures & Algorithms", 4, ["ai", "machine learning", "neural networks"]),
    ("Web Development Boot Camp", "Full stack development with HTML, CSS, and JS.", "Computer Science", "Web Development", "beginner", "None", 3, ["web", "html", "css", "javascript"]),
    ("Cybersecurity Fundamentals", "Protecting systems and networks from digital attacks.", "Computer Science", "Cybersecurity", "intermediate", "Introduction to Python", 3, ["security", "networking", "hacking"]),

    # Law
    ("Criminal Law 101", "Introduction to criminal justice and legal systems.", "Law", "Criminal Law", "beginner", "None", 3, ["law", "justice", "court"]),
    ("Corporate Law", "Legal aspects of business organizations and transactions.", "Law", "Corporate Law", "intermediate", "Criminal Law 101", 3, ["business", "contracts", "law"]),
    ("International Human Rights", "Evolution and enforcement of human rights globally.", "Law", "Human Rights", "advanced", "Criminal Law 101", 3, ["human rights", "un", "law"]),
    ("Intellectual Property Law", "Patents, trademarks, and copyright law.", "Law", "IP Law", "intermediate", "None", 3, ["copyright", "patents", "law"]),

    # Medicine
    ("Human Anatomy", "Detailed study of human body structures.", "Medicine", "Anatomy", "beginner", "None", 4, ["anatomy", "biology", "body"]),
    ("General Surgery", "Surgical principles and techniques.", "Medicine", "Surgery", "advanced", "Human Anatomy", 5, ["surgery", "medical", "hospital"]),
    ("Pharmacology", "Study of drugs and their actions on biological systems.", "Medicine", "Pharmacology", "intermediate", "None", 3, ["drugs", "medicine", "biology"]),
    ("Public Health Global Trends", "Exploring health challenges in the modern world.", "Medicine", "Public Health", "beginner", "None", 3, ["health", "policy", "global"]),

    # Engineering
    ("Mechanical Engineering Principles", "Statics, dynamics, and thermodynamics.", "Engineering", "Mechanical Engineering", "beginner", "None", 4, ["physics", "machines", "engineering"]),
    ("Robotics & Automation", "Design and control of robotic systems.", "Engineering", "Robotics", "advanced", "Mechanical Engineering Principles", 4, ["robotics", "ai", "hardware"]),
    ("Electrical Circuits", "AC and DC circuit analysis.", "Engineering", "Electrical Engineering", "intermediate", "None", 3, ["electricity", "circuits", "engineering"]),

    # Business
    ("Principles of Management", "Core management theories and practices.", "Business Administration", "Management", "beginner", "None", 3, ["management", "business", "leadership"]),
    ("Management Information", "Study of the design, implementation, and strategic management of information systems (MIS) in corporate organizations to support business decision-making, operational control, and competitive advantage.", "Business Administration", "Management", "intermediate", "Principles of Management (3 Units)", 3, ["management", "information systems", "business", "technology", "database"]),
    ("Strategic Marketing", "Advanced marketing strategies for global brands.", "Business Administration", "Marketing", "advanced", "Principles of Management", 3, ["marketing", "strategy", "branding"]),
    ("Business Ethics", "Moral principles in the world of business.", "Business Administration", "Business Ethics", "intermediate", "None", 2, ["ethics", "philosophy", "business"]),

    # Accounting
    ("Financial Accounting", "Recording and reporting financial transactions.", "Accounting", "Financial Accounting", "beginner", "None", 3, ["finance", "numbers", "accounting"]),
    ("Forensic Accounting", "Investigating financial crimes and fraud.", "Accounting", "Forensic Accounting", "advanced", "Financial Accounting", 4, ["fraud", "investigation", "accounting"]),

    # Social Sciences
    ("Introduction to Psychology", "Study of human behavior and mental processes.", "Social Sciences", "Psychology", "beginner", "None", 3, ["mind", "behavior", "psychology"]),
    ("International Relations", "The interaction of states and international organizations.", "Social Sciences", "International Relations", "intermediate", "None", 3, ["politics", "global", "diplomacy"]),
    ("Microeconomics", "Economic behavior of individuals and firms.", "Social Sciences", "Economics", "intermediate", "None", 3, ["economy", "money", "markets"]),

    # Arts & Others
    ("Graphic Design Basics", "Visual communication using typography and imagery.", "Arts", "Graphic Design", "beginner", "None", 3, ["design", "art", "creative"]),
    ("History of Modern Art", "Art movements from the 19th century to today.", "Arts", "History of Art", "intermediate", "None", 3, ["art", "history", "culture"]),
    ("Introduction to Architecture", "Basic principles of architectural design.", "Others", "Architecture", "beginner", "None", 4, ["design", "building", "architecture"]),
    ("Applied Mathematics", "Mathematical methods used in science and engineering.", "Others", "Mathematics", "advanced", "None", 3, ["math", "science", "logic"]),
    
    # Research & Academic Projects
    ("Research Methodology", "Master the scientific research process. Learn how to formulate research problems, construct conceptual frameworks, conduct literature reviews, write academic proposals, and analyze qualitative and quantitative data.", "Computer Science", "Research", "intermediate", "None", 3, ["research", "methodology", "writing", "data analysis", "ethics"]),
    ("Final Year Research Project", "Apply your computer science and academic knowledge to solve a real-world research problem. Culminates in a comprehensive dissertation, implementation, and oral defense.", "Computer Science", "Research", "advanced", "Research Methodology", 6, ["research", "dissertation", "project", "thesis", "defense"])
]


def init_db():
    """Create all tables if they don't exist and auto-seed if empty."""
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    
    # Check if courses are empty
    count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count == 0:
        for title, desc, dept, cat, diff, prereq, creds, tags in COURSES_SEED:
            db.execute(
                """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
            )
        db.commit()


def init_app(app):
    """Register teardown and CLI hooks."""
    app.teardown_appcontext(close_db)
