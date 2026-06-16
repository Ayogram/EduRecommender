"""
Database helper – thin wrapper around sqlite3 for the application.
Provides get_db() for per-request connections and init_db() for schema creation.
"""

import os
import sqlite3
import json
import re
from flask import g, current_app

try:
    import psycopg2
    from psycopg2.extras import DictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# Safe timestamp converter to prevent sqlite3 ValueError: too many values to unpack (expected 2)
# on Vercel environment where backup restores can write ISO-8601 strings (containing "T").
def convert_timestamp_safe(val):
    if not val:
        return None
    try:
        val_str = val.decode('utf-8').strip()
        # Clean timezone indicators
        clean_val = val_str.replace('Z', '').split('+')[0]
        
        # Try split by space or 'T'
        for separator in (' ', 'T'):
            if separator in clean_val:
                parts = clean_val.split(separator)
                if len(parts) == 2:
                    date_part, time_part = parts
                    import datetime
                    time_fmt = '%H:%M:%S.%f' if '.' in time_part else '%H:%M:%S'
                    try:
                        return datetime.datetime.strptime(f"{date_part} {time_part}", f"%Y-%m-%d {time_fmt}")
                    except ValueError:
                        continue
        
        # Fallback to general parsing
        import datetime
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d'):
            try:
                return datetime.datetime.strptime(clean_val.split('.')[0], fmt)
            except ValueError:
                continue
                
        return val_str
    except Exception:
        try:
            return val.decode('utf-8', errors='ignore')
        except Exception:
            return str(val)

sqlite3.register_converter("timestamp", convert_timestamp_safe)
sqlite3.register_converter("TIMESTAMP", convert_timestamp_safe)

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
    past_grades     TEXT    DEFAULT '{}',
    profile_completed INTEGER DEFAULT 0,
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
    video_url   TEXT,
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


class DBWrapper:
    def __init__(self, is_postgres, conn):
        self.is_postgres = is_postgres
        self.conn = conn

    def _convert_query(self, query):
        if self.is_postgres:
            # Avoid replacing ? inside simple strings by just doing a naive replace for now, 
            # since most queries don't have ? in string literals.
            return query.replace('?', '%s')
        return query

    def execute(self, query, params=()):
        q = self._convert_query(query)
        cursor = self.conn.conn.cursor() if hasattr(self.conn, 'conn') else self.conn.cursor()
        if params:
            cursor.execute(q, params)
        else:
            cursor.execute(q)
        return cursor

    def executescript(self, script):
        if self.is_postgres:
            cursor = self.conn.cursor()
            cursor.execute(script)
            return cursor
        else:
            return self.conn.executescript(script)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db():
    """Return the per-request database connection (stored on Flask `g`)."""
    if "db" not in g:
        pg_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
        if HAS_PSYCOPG2 and pg_url:
            conn = psycopg2.connect(pg_url, cursor_factory=DictCursor)
            g.db = DBWrapper(True, conn)
        else:
            conn = sqlite3.connect(
                current_app.config["DATABASE_PATH"],
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = DBWrapper(False, conn)
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist and auto-seed if empty."""
    db = get_db()
    db_schema = SCHEMA
    
    if db.is_postgres:
        db_schema = db_schema.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    else:
        db_path = current_app.config["DATABASE_PATH"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
    db.executescript(db_schema)
    db.commit()
    
    # Restore the custom course catalog of 134 courses from seed_data_v2.py
    count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count >= 500 or count == 0:
        db.execute("DELETE FROM courses")
        if not db.is_postgres:
            try:
                db.execute("DELETE FROM sqlite_sequence WHERE name = 'courses'")
            except Exception:
                pass
        else:
            try:
                db.execute("ALTER SEQUENCE courses_id_seq RESTART WITH 1")
            except Exception:
                pass
        db.commit()
        
        # Clear student_courses and recommendations to prevent invalid foreign keys pointing to deleted courses
        db.execute("DELETE FROM student_courses")
        db.execute("DELETE FROM recommendations")
        db.execute("DELETE FROM course_modules")
        db.commit()
        
        import sys
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        from seed_data_v2 import COURSES
        for title, desc, dept, cat, diff, prereq, creds, tags in COURSES:
            db.execute(
                """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
            )
        db.commit()


def init_app(app):
    """Register teardown and CLI hooks."""
    app.teardown_appcontext(close_db)


def ensure_enrollment(db, user_id, course_id):
    """Ensure user is enrolled in the database if they are in the session's enrolled list."""
    enrollment = db.execute(
        "SELECT * FROM student_courses WHERE user_id = ? AND course_id = ?",
        (user_id, course_id)
    ).fetchone()
    if not enrollment:
        from flask import session
        enrolled_session = session.get('enrolled_courses', [])
        if enrolled_session and course_id in enrolled_session:
            try:
                if db.is_postgres:
                    db.execute(
                        "INSERT INTO student_courses (user_id, course_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
                        (user_id, course_id)
                    )
                else:
                    db.execute(
                        "INSERT OR IGNORE INTO student_courses (user_id, course_id) VALUES (?, ?)",
                        (user_id, course_id)
                    )
                db.commit()
                enrollment = db.execute(
                    "SELECT * FROM student_courses WHERE user_id = ? AND course_id = ?",
                    (user_id, course_id)
                ).fetchone()
            except Exception as e:
                print(f"Error auto-healing enrollment record for course {course_id}: {e}", flush=True)
    return enrollment


def update_course_progress(db, user_id, course_id):
    """Dynamically compute and update the overall course progress (0-100) based on completed modules and lessons."""
    try:
        # Get all modules for this course
        modules = db.execute(
            "SELECT id, sort_order FROM course_modules WHERE course_id = ? ORDER BY sort_order",
            (course_id,)
        ).fetchall()
        
        if not modules:
            return
            
        # Get the user's enrollment record
        enrollment = db.execute(
            "SELECT current_module_id, current_lesson_id, completed FROM student_courses WHERE user_id = ? AND course_id = ?",
            (user_id, course_id)
        ).fetchone()
        
        if not enrollment:
            return
            
        if enrollment['completed']:
            db.execute(
                "UPDATE student_courses SET progress = 100.0 WHERE user_id = ? AND course_id = ?",
                (user_id, course_id)
            )
            db.commit()
            return

        # Let's count how many modules/lessons/exams the user has completed.
        module_ids = [m['id'] for m in modules]
        placeholders = ",".join("?" for _ in module_ids)
        all_lessons = db.execute(
            f"SELECT id, module_id, sort_order FROM module_lessons WHERE module_id IN ({placeholders}) ORDER BY module_id, sort_order",
            module_ids
        ).fetchall()
        
        # Group lessons by module_id
        lessons_by_module = {}
        for l in all_lessons:
            lessons_by_module.setdefault(l['module_id'], []).append(l)
            
        # Get all exam results for the user on these modules
        exam_results = db.execute(
            f"SELECT module_id FROM exam_results WHERE user_id = ? AND module_id IN ({placeholders})",
            [user_id] + module_ids
        ).fetchall()
        completed_exam_module_ids = {r['module_id'] for r in exam_results}
        
        current_mod_id = enrollment['current_module_id'] or modules[0]['id']
        current_les_id = enrollment['current_lesson_id']
        
        # Find current module sort order
        curr_mod_order = 1
        for m in modules:
            if m['id'] == current_mod_id:
                curr_mod_order = m['sort_order']
                break
                
        total_items = 0
        completed_items = 0
        
        for m in modules:
            m_id = m['id']
            m_lessons = lessons_by_module.get(m_id, [])
            m_lesson_count = len(m_lessons)
            
            # Each module has lessons + 1 exam
            total_items += m_lesson_count + 1
            
            if m_id in completed_exam_module_ids:
                completed_items += m_lesson_count + 1
            elif m['sort_order'] < curr_mod_order:
                completed_items += m_lesson_count + 1
            elif m_id == current_mod_id:
                if current_les_id:
                    curr_les_order = 1
                    for l in m_lessons:
                        if l['id'] == current_les_id:
                            curr_les_order = l['sort_order']
                            break
                    completed_items += max(0, curr_les_order - 1)
                else:
                    pass
                    
        progress_percent = min(100.0, round((completed_items / total_items) * 100, 1)) if total_items > 0 else 0.0
        
        if progress_percent >= 100.0:
            db.execute(
                "UPDATE student_courses SET progress = 100.0, completed = 1 WHERE user_id = ? AND course_id = ?",
                (user_id, course_id)
            )
        else:
            db.execute(
                "UPDATE student_courses SET progress = ? WHERE user_id = ? AND course_id = ?",
                (progress_percent, user_id, course_id)
            )
        db.commit()
    except Exception as e:
        print(f"Error updating course progress for course {course_id}: {e}", flush=True)


