"""
EduRecommender – Flask Application Factory
"""

import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Load Environment Variables from .env
load_dotenv()

# Enable insecure transport for local development (when not hosted on Vercel)
if not (os.environ.get('VERCEL') or os.environ.get('NOW_REGION')):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask_login import LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from config import Config
from models.database import init_app as db_init_app, init_db, get_db

# Define a global mail object
mail = Mail()

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(Config)

    # Support proxy headers (like X-Forwarded-Proto) under Vercel
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # ── CSRF Protection ─────────────────────────────────────────
    csrf = CSRFProtect(app)
    mail.init_app(app)

    # ── Database ────────────────────────────────────────────────
    db_init_app(app)

    # ── Flask-Login ─────────────────────────────────────────────
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        from flask import session
        import json
        user = User.get_by_id(int(user_id))
        
        # If the ephemeral SQLite database was wiped on Vercel cold-start,
        # but the secure signed session cookie is present, auto-restore the user
        if not user and session.get('user_email'):
            interests_raw = session.get('user_interests', [])
            if isinstance(interests_raw, str):
                try:
                    interests_list = json.loads(interests_raw)
                except Exception:
                    interests_list = []
            else:
                interests_list = list(interests_raw) if interests_raw else []

            # Re-create the user in the database
            user = User.create(
                name=session.get('user_name'),
                email=session.get('user_email'),
                google_id=session.get('user_google_id'),
                profile_picture=session.get('user_profile_picture'),
                role=session.get('user_role', 'user'),
                interests=interests_list,
                academic_field=session.get('user_academic_field'),
                department=session.get('user_department'),
                is_verified=1
            )
            # Re-fetch user to get the full object with generated ID
            user = User.get_by_email(session.get('user_email'))
            
            # Restore GPA
            if user:
                from models.database import get_db
                db = get_db()
                db.execute("UPDATE users SET gpa = ? WHERE id = ?", (session.get('user_gpa', 0.0), user.id))
                db.commit()
                # Re-fetch again
                user = User.get_by_id(user.id)
                
            # Restore course enrollments if saved in session
            enrolled_ids = session.get('enrolled_courses', [])
            if user and enrolled_ids:
                from models.database import get_db
                db = get_db()
                for c_id in enrolled_ids:
                    try:
                        db.execute(
                            "INSERT OR IGNORE INTO student_courses (user_id, course_id, enrolled_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                            (user.id, c_id)
                        )
                    except Exception:
                        pass
                db.commit()

        return user

    # ── Register Blueprints ─────────────────────────────────────
    from backend.auth import auth_bp, init_oauth
    from backend.admin import admin_bp
    from backend.recommendations import recs_bp
    from backend.complaints import complaints_bp

    from backend.learning import learning_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(recs_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(learning_bp)

    # Initialise Google OAuth
    init_oauth(app)

    # ── Main Routes ─────────────────────────────────────────────
    from flask import Blueprint
    main_bp = Blueprint("main", __name__)

    @main_bp.route("/favicon.ico")
    def favicon():
        from flask import send_from_directory
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.svg",
            mimetype="image/svg+xml",
        )

    @main_bp.route("/")
    def index():
        return render_template("landing.html")

    @main_bp.route("/architecture")
    @login_required
    def architecture():
        return render_template("architecture.html")

    @main_bp.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        enrolled = db.execute(
            """SELECT sc.*, c.title, c.category, c.difficulty, c.description
               FROM student_courses sc
               JOIN courses c ON sc.course_id = c.id
               WHERE sc.user_id = ?
               ORDER BY sc.enrolled_at DESC""",
            (current_user.id,),
        ).fetchall()

        recent_recs = db.execute(
            """SELECT r.*, c.title, c.category, c.difficulty
               FROM recommendations r
               JOIN courses c ON r.course_id = c.id
               WHERE r.user_id = ?
               ORDER BY r.success_probability DESC, r.score DESC LIMIT 5""",
            (current_user.id,),
        ).fetchall()

        # Auto-generate recommendations if empty but profile is complete
        if not recent_recs and current_user.interests and current_user.academic_field:
            try:
                from engine.hybrid import get_recommendations
                get_recommendations(current_user.id, top_n=12)
                recent_recs = db.execute(
                    """SELECT r.*, c.title, c.category, c.difficulty
                       FROM recommendations r
                       JOIN courses c ON r.course_id = c.id
                       WHERE r.user_id = ?
                       ORDER BY r.success_probability DESC, r.score DESC LIMIT 5""",
                    (current_user.id,),
                ).fetchall()
            except Exception:
                pass

        # Get all exam results for the user, joining with course title and module details
        exam_results = db.execute(
            """SELECT er.*, cm.title AS module_title, c.title AS course_title
               FROM exam_results er
               JOIN course_modules cm ON er.module_id = cm.id
               JOIN courses c ON cm.course_id = c.id
               WHERE er.user_id = ?
               ORDER BY er.updated_at DESC""",
            (current_user.id,),
        ).fetchall()

        return render_template(
            "dashboard.html",
            enrolled_courses=enrolled,
            recent_recs=recent_recs,
            exam_results=exam_results,
        )

    @main_bp.route("/notifications")
    @login_required
    def notifications():
        from models.notification import Notification
        user_notifications = Notification.get_for_user(current_user.id)
        # Mark all as read when viewing
        for n in user_notifications:
            Notification.mark_as_read(n.id)
        return render_template("notifications.html", notifications=user_notifications)

    @main_bp.route("/api/dashboard")
    def api_dashboard():
        from flask import jsonify
        if not current_user.is_authenticated:
            return jsonify({"error": "unauthorized"}), 401
            
        db = get_db()
        enrolled = db.execute(
            """SELECT sc.*, c.title, c.category, c.difficulty, c.description
               FROM student_courses sc
               JOIN courses c ON sc.course_id = c.id
               WHERE sc.user_id = ?
               ORDER BY sc.enrolled_at DESC""",
            (current_user.id,),
        ).fetchall()

        recent_recs = db.execute(
            """SELECT r.*, c.title, c.category, c.difficulty
               FROM recommendations r
               JOIN courses c ON r.course_id = c.id
               WHERE r.user_id = ?
               ORDER BY r.success_probability DESC, r.score DESC LIMIT 5""",
            (current_user.id,),
        ).fetchall()

        # Auto-generate recommendations if empty but profile is complete
        if not recent_recs and current_user.interests and current_user.academic_field:
            try:
                from engine.hybrid import get_recommendations
                get_recommendations(current_user.id, top_n=12)
                recent_recs = db.execute(
                    """SELECT r.*, c.title, c.category, c.difficulty
                       FROM recommendations r
                       JOIN courses c ON r.course_id = c.id
                       WHERE r.user_id = ?
                       ORDER BY r.success_probability DESC, r.score DESC LIMIT 5""",
                    (current_user.id,),
                ).fetchall()
            except Exception:
                pass

        return jsonify({
            "user": {
                "name": current_user.name,
                "email": current_user.email,
                "gpa": current_user.gpa,
                "department": current_user.department,
            },
            "enrolled": [dict(r) for r in enrolled],
            "recommendations": [dict(r) for r in recent_recs]
        })

    app.register_blueprint(main_bp)

    # ── Context Processors ──────────────────────────────────────
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            from models.notification import Notification
            count = Notification.get_unread_count(current_user.id)
            return dict(unread_notification_count=count)
        return dict(unread_notification_count=0)

    # ── Initialise DB on first request ──────────────────────────
    with app.app_context():
        init_db()

    # ── Error Handlers ──────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
