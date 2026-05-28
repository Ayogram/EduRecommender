"""Complaint model."""

from datetime import datetime
from models.database import get_db


class Complaint:
    def __init__(self, row):
        self.id = row["id"]
        self.user_id = row["user_id"]
        self.subject = row["subject"]
        self.message = row["message"]
        self.status = row["status"]
        self.admin_response = row["admin_response"]
        self.created_at = row["created_at"]
        self.resolved_at = row["resolved_at"]

    @staticmethod
    def create(user_id, subject, message):
        db = get_db()
        db.execute(
            "INSERT INTO complaints (user_id, subject, message) VALUES (?, ?, ?)",
            (user_id, subject, message),
        )
        db.commit()

    @staticmethod
    def get_for_user(user_id):
        rows = get_db().execute(
            """SELECT c.*, u.name as user_name, u.email as user_email
               FROM complaints c JOIN users u ON c.user_id = u.id
               WHERE c.user_id = ? ORDER BY c.created_at DESC""",
            (user_id,),
        ).fetchall()
        return rows

    @staticmethod
    def get_all():
        rows = get_db().execute(
            """SELECT c.*, u.name as user_name, u.email as user_email
               FROM complaints c JOIN users u ON c.user_id = u.id
               ORDER BY c.created_at DESC"""
        ).fetchall()
        return rows

    @staticmethod
    def get_by_id(complaint_id):
        row = get_db().execute(
            "SELECT * FROM complaints WHERE id = ?",
            (complaint_id,),
        ).fetchone()
        return Complaint(row) if row else None

    @staticmethod
    def respond(complaint_id, admin_response):
        db = get_db()
        db.execute(
            """UPDATE complaints
               SET admin_response = ?, status = 'resolved', resolved_at = ?
               WHERE id = ?""",
            (admin_response, datetime.utcnow(), complaint_id),
        )
        db.commit()

    @staticmethod
    def count(status=None):
        if status:
            return get_db().execute(
                "SELECT COUNT(*) FROM complaints WHERE status = ?", (status,)
            ).fetchone()[0]
        return get_db().execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
