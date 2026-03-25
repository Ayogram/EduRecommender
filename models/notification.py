from models.database import get_db

class Notification:
    def __init__(self, row):
        self.id = row["id"]
        self.user_id = row["user_id"]
        self.message = row["message"]
        self.is_read = row["is_read"]
        self.created_at = row["created_at"]

    @staticmethod
    def create(user_id, message):
        db = get_db()
        db.execute(
            "INSERT INTO notifications (user_id, message) VALUES (?, ?)",
            (user_id, message)
        )
        db.commit()

    @staticmethod
    def get_unread_count(user_id):
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
            (user_id,)
        ).fetchone()
        return row[0] if row else 0

    @staticmethod
    def get_for_user(user_id, limit=10):
        db = get_db()
        rows = db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()
        return [Notification(r) for r in rows]

    @staticmethod
    def mark_as_read(notification_id):
        db = get_db()
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notification_id,)
        )
        db.commit()
