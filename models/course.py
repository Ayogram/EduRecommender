"""Course model."""

import json
from models.database import get_db


class Course:
    def __init__(self, row):
        self.id = row["id"]
        self.title = row["title"]
        self.description = row["description"]
        self.department = row["department"]
        self.category = row["category"]
        self.difficulty = row["difficulty"]
        self.prerequisites = row["prerequisites"] if row["prerequisites"] else "None"
        self.credits = row["credits"] if row["credits"] else 3
        self.tags = json.loads(row["tags"]) if row["tags"] else []
        self.created_at = row["created_at"]

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "department": self.department,
            "category": self.category,
            "difficulty": self.difficulty,
            "prerequisites": self.prerequisites,
            "credits": self.credits,
            "tags": self.tags,
        }

    # ── Lookups ──────────────────────────────────────────────────

    @staticmethod
    def get_by_id(course_id):
        row = get_db().execute(
            "SELECT * FROM courses WHERE id = ?", (course_id,)
        ).fetchone()
        return Course(row) if row else None

    @staticmethod
    def get_all():
        rows = get_db().execute(
            "SELECT * FROM courses ORDER BY title"
        ).fetchall()
        return [Course(r) for r in rows]

    @staticmethod
    def count():
        return get_db().execute("SELECT COUNT(*) FROM courses").fetchone()[0]

    @staticmethod
    def get_categories():
        rows = get_db().execute(
            "SELECT DISTINCT category FROM courses ORDER BY category"
        ).fetchall()
        return [r["category"] for r in rows]

    @staticmethod
    def search(query):
        rows = get_db().execute(
            "SELECT * FROM courses WHERE title LIKE ? OR description LIKE ? OR category LIKE ? OR department LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"),
        ).fetchall()
        return [Course(r) for r in rows]
