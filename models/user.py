"""User model with Flask-Login integration."""

from flask_login import UserMixin
from models.database import get_db
import json
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


class User(UserMixin):
    """Wraps a database row to satisfy Flask-Login's interface."""

    def __init__(self, row):
        # Convert sqlite3.Row to dict to use .get() safely
        row_dict = dict(row)
        self.id = row_dict["id"]
        self.name = row_dict["name"]
        self.email = row_dict["email"]
        self.password_hash = row_dict["password_hash"]
        self.google_id = row_dict["google_id"]
        self.profile_picture = row_dict["profile_picture"]
        self.role = row_dict["role"]
        self.status = row_dict["status"]
        self.is_verified = row_dict.get("is_verified", 0)
        self.interests = json.loads(row_dict["interests"]) if row_dict["interests"] else []
        self.nickname = row_dict.get("nickname")
        self.academic_field = row_dict.get("academic_field")
        self.department = row_dict.get("department")
        self.gpa = row_dict.get("gpa", 0.0)
        self.created_at = row_dict["created_at"]
        if hasattr(self.created_at, 'strftime'):
            self.created_at = self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def is_active(self):
        """Verified and non-suspended users can log in."""
        return self.status == "active" and self.is_verified == 1

    @property
    def is_admin(self):
        return self.role in ("admin", "super_admin")

    @property
    def is_super_admin(self):
        return self.role == "super_admin"

    def get_verification_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='email-confirm-salt')

    @staticmethod
    def verify_token(token, expires_sec=86400): # 24 hours
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='email-confirm-salt', max_age=expires_sec)
        except Exception:
            return None
        return User.get_by_id(data.get('user_id'))

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except Exception:
            return None
        return User.get_by_id(data.get('user_id'))

    # ── Lookup helpers ──────────────────────────────────────────

    @staticmethod
    def get_by_id(user_id):
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_email(email):
        row = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_google_id(google_id):
        row = get_db().execute(
            "SELECT * FROM users WHERE google_id = ?", (google_id,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_all(search=None, status=None, verified=None):
        db = get_db()
        sql = "SELECT * FROM users WHERE 1=1"
        params = []

        if search:
            sql += " AND (name LIKE ? OR email LIKE ? OR academic_field LIKE ?)"
            q = f"%{search}%"
            params.extend([q, q, q])
        
        if status and status != 'all':
            sql += " AND status = ?"
            params.append(status)
            
        if verified and verified != 'all':
            sql += " AND is_verified = ?"
            params.append(1 if verified == 'verified' else 0)

        sql += " ORDER BY created_at DESC"
        rows = db.execute(sql, params).fetchall()
        return [User(r) for r in rows]

    # ── Mutation helpers ────────────────────────────────────────

    @staticmethod
    def create(name, email, password_hash=None, google_id=None,
               profile_picture=None, role=None, interests=None, academic_field=None, is_verified=0):
        db = get_db()
        
        # Determine role if not specified
        if role is None:
            super_admin_email = current_app.config.get('SUPER_ADMIN_EMAIL')
            if email == super_admin_email:
                role = "super_admin"
                is_verified = 1
            else:
                role = "user"

        db.execute(
            """INSERT INTO users
               (name, email, password_hash, google_id, profile_picture, role, interests, academic_field, is_verified)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                email,
                password_hash,
                google_id,
                profile_picture or "/static/img/default_avatar.png",
                role,
                json.dumps(interests or []),
                academic_field,
                is_verified
            ),
        )
        db.commit()
        return User.get_by_email(email)

    @staticmethod
    def update_status(user_id, status):
        db = get_db()
        db.execute(
            "UPDATE users SET status = ? WHERE id = ?", (status, user_id)
        )
        db.commit()

    @staticmethod
    def update_password(user_id, new_password_hash):
        db = get_db()
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_password_hash, user_id),
        )
        db.commit()

    @staticmethod
    def update_profile(user_id, name, nickname, academic_field, interests, **kwargs):
        db = get_db()
        db.execute(
            """UPDATE users SET name = ?, nickname = ?, academic_field = ?, interests = ?, department = ?, gpa = ?
               WHERE id = ?""",
            (name, nickname, academic_field, json.dumps(interests), kwargs.get('department'), kwargs.get('gpa'), user_id)
        )
        db.commit()

    @staticmethod
    def update_avatar(user_id, avatar_url):
        db = get_db()
        db.execute(
            "UPDATE users SET profile_picture = ? WHERE id = ?",
            (avatar_url, user_id)
        )
        db.commit()

    @staticmethod
    def update_interests(user_id, interests):
        db = get_db()
        db.execute(
            "UPDATE users SET interests = ? WHERE id = ?",
            (json.dumps(interests), user_id),
        )
        db.commit()

    @staticmethod
    def delete(user_id):
        db = get_db()
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()

    @staticmethod
    def count():
        return get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0]
