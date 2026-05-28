"""
Database helper – thin wrapper around sqlite3 for the application.
Provides get_db() for per-request connections and init_db() for schema creation.
"""

import os
import sqlite3
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


def init_db():
    """Create all tables if they don't exist."""
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


def init_app(app):
    """Register teardown and CLI hooks."""
    app.teardown_appcontext(close_db)
