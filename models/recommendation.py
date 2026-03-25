"""Recommendation model."""

from models.database import get_db


class Recommendation:
    def __init__(self, row):
        self.id = row["id"]
        self.user_id = row["user_id"]
        self.course_id = row["course_id"]
        self.score = row["score"]
        self.explanation = row["explanation"]
        self.method = row["method"]
        self.created_at = row["created_at"]

    @staticmethod
    def save(user_id, course_id, score, explanation, method):
        db = get_db()
        db.execute(
            """INSERT INTO recommendations (user_id, course_id, score, explanation, method)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, course_id, score, explanation, method),
        )
        db.commit()

    @staticmethod
    def get_for_user(user_id, limit=10):
        rows = get_db().execute(
            """SELECT r.*, c.title as course_title, c.category, c.difficulty, c.description, 
                       c.department, c.prerequisites, c.credits
               FROM recommendations r
               JOIN courses c ON r.course_id = c.id
               WHERE r.user_id = ?
               ORDER BY r.score DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()
        return rows

    @staticmethod
    def clear_for_user(user_id):
        db = get_db()
        db.execute("DELETE FROM recommendations WHERE user_id = ?", (user_id,))
        db.commit()

    @staticmethod
    def count():
        return get_db().execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
