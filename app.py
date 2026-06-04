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

    # Register admin memory log handler
    try:
        from backend.admin import BufferLogHandler
        import logging
        log_handler = BufferLogHandler()
        log_handler.setLevel(logging.INFO)
        app.logger.addHandler(log_handler)
        logging.getLogger().addHandler(log_handler)
    except Exception as log_ex:
        app.logger.error(f"Error registering admin log buffer handler: {log_ex}")

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
        try:
            from models.user import User
            from flask import session
            import json
            
            try:
                uid = int(user_id)
                user = User.get_by_id(uid)
            except (ValueError, TypeError):
                user = None
            
            # Prevent DB-reset crossover: if ID exists but email doesn't match the secure cookie, ignore it
            if user and session.get('user_email') and user.email != session.get('user_email'):
                user = None
                
            # If the ephemeral SQLite database was wiped on Vercel cold-start,
            # but the secure signed session cookie is present, auto-restore the user
            if not user and session.get('user_email'):
                # First check if they exist by email or google_id under a different ID in the new DB
                user = User.get_by_email(session.get('user_email'))
                if not user and session.get('user_google_id'):
                    user = User.get_by_google_id(session.get('user_google_id'))
                    
                if user:
                    # Update session to point to the correct, restored user ID
                    session['_user_id'] = str(user.id)
                else:
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
                        name=session.get('user_name') or session.get('user_email').split('@')[0],
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
                    
                    if user:
                        # Update session to point to the correct, restored user ID
                        session['_user_id'] = str(user.id)
                        
                        # Restore GPA, nickname, profile_completed flag, and past_grades
                        from models.database import get_db
                        db = get_db()
                        past_grades_raw = session.get('user_past_grades', {})
                        past_grades_val = json.dumps(past_grades_raw) if isinstance(past_grades_raw, dict) else (past_grades_raw or '{}')
                        db.execute(
                            "UPDATE users SET gpa = ?, nickname = ?, profile_completed = ?, past_grades = ? WHERE id = ?",
                            (
                                session.get('user_gpa', 0.0),
                                session.get('user_nickname'),
                                session.get('user_profile_completed', 0),
                                past_grades_val,
                                user.id
                            )
                        )
                        db.commit()
                        # Re-fetch again
                        user = User.get_by_id(user.id)
            return user
        except Exception as e:
            import traceback
            import logging
            logging.error(f"CRITICAL error in load_user: {e}\n{traceback.format_exc()}")
            return None

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

    # Custom Jinja filters
    @app.template_filter('fromjson_safe')
    def fromjson_safe_filter(s):
        import json
        if not s:
            return {}
        try:
            return json.loads(s)
        except (ValueError, TypeError):
            # If it's a plain string override, wrap it in the expected format
            return {"verdict": s}

    @app.template_filter('date_format')
    def date_format_filter(value, format='%Y-%m-%d'):
        if not value:
            return 'N/A'
        if isinstance(value, str):
            import datetime
            parsed_val = None
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%d'):
                try:
                    parsed_val = datetime.datetime.strptime(value.split('.')[0], fmt)
                    break
                except ValueError:
                    continue
            if parsed_val:
                value = parsed_val
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return str(value)

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
        from models.database import get_db
        import json
        db = get_db()
        all_courses = db.execute("SELECT * FROM courses ORDER BY title ASC").fetchall()
        
        # Load fields map from database JSON file
        fields_file = os.path.join(app.root_path, "database", "fields_and_interests.json")
        try:
            with open(fields_file, "r") as f:
                fields_map = json.load(f)
        except Exception:
            fields_map = {}
            
        return render_template("landing.html", all_courses=all_courses, fields_map=fields_map)

    @main_bp.route("/architecture")
    @login_required
    def architecture():
        from flask import flash
        if not current_user.is_admin:
            flash("Access denied. Administrator privileges required.", "error")
            return redirect(url_for("main.dashboard"))
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

    @main_bp.route("/leaderboard")
    @login_required
    def leaderboard():
        db = get_db()
        # Query students ranked by average best_score
        rankings = db.execute(
            """SELECT u.id, u.name, u.nickname, u.academic_field, u.department, u.profile_picture,
                      COUNT(er.id) as exams_taken,
                      AVG(er.best_score) as avg_score
               FROM users u
               LEFT JOIN exam_results er ON u.id = er.user_id
               WHERE u.role = 'user'
               GROUP BY u.id, u.name, u.nickname, u.academic_field, u.department, u.profile_picture
               ORDER BY COALESCE(AVG(er.best_score), 0) DESC, exams_taken DESC"""
        ).fetchall()
        
        # Convert to list of dicts and calculate rank
        ranking_list = []
        for i, row in enumerate(rankings):
            d = dict(row)
            d['rank'] = i + 1
            d['avg_score'] = round(d['avg_score'], 1) if d['avg_score'] is not None else 0.0
            ranking_list.append(d)
            
        return render_template("leaderboard.html", rankings=ranking_list)

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

    @main_bp.route("/api/backup-data")
    @login_required
    def backup_data():
        from flask import jsonify
        db = get_db()
        user_id = current_user.id
        
        # 1. Fetch user profile
        user_row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        user_data = dict(user_row) if user_row else {}
        if "password_hash" in user_data:
            del user_data["password_hash"]
            
        # 2. Fetch enrolled courses
        enrolled = db.execute("SELECT * FROM student_courses WHERE user_id = ?", (user_id,)).fetchall()
        enrolled_list = [dict(r) for r in enrolled]
        
        # 3. Fetch exam results
        exams = db.execute("SELECT * FROM exam_results WHERE user_id = ?", (user_id,)).fetchall()
        exams_list = [dict(r) for r in exams]
        
        # 4. Fetch complaints
        complaints = db.execute("SELECT * FROM complaints WHERE user_id = ?", (user_id,)).fetchall()
        complaints_list = [dict(r) for r in complaints]
        
        # 5. Fetch notifications
        notifications = db.execute("SELECT * FROM notifications WHERE user_id = ?", (user_id,)).fetchall()
        notifications_list = [dict(r) for r in notifications]
        
        return jsonify({
            "email": current_user.email,
            "user": user_data,
            "enrolled": enrolled_list,
            "exams": exams_list,
            "complaints": complaints_list,
            "notifications": notifications_list
        })

    @main_bp.route("/api/sync-restore", methods=["POST"])
    @login_required
    def sync_restore():
        from flask import request, jsonify
        import json
        db = get_db()
        user_id = current_user.id
        data = request.get_json() or {}
        
        if not data or data.get("email") != current_user.email:
            return jsonify({"status": "error", "message": "Invalid backup data"}), 400
            
        # Restore user profile fields (gpa, nickname, academic_field, department, interests, past_grades)
        profile = data.get("user", {})
        if profile:
            interests_val = json.dumps(profile.get("interests", [])) if isinstance(profile.get("interests"), list) else (profile.get("interests") or '[]')
            past_grades_val = json.dumps(profile.get("past_grades", {})) if isinstance(profile.get("past_grades"), dict) else (profile.get("past_grades") or '{}')
            
            db.execute(
                """UPDATE users SET 
                   nickname = ?, 
                   academic_field = ?, 
                   department = ?, 
                   gpa = ?, 
                   interests = ?, 
                   past_grades = ?, 
                   profile_completed = ?
                   WHERE id = ?""",
                (
                    profile.get("nickname"),
                    profile.get("academic_field"),
                    profile.get("department"),
                    profile.get("gpa") or 0.0,
                    interests_val,
                    past_grades_val,
                    profile.get("profile_completed") or 0,
                    user_id
                )
            )
            
        # Restore enrolled courses (student_courses)
        enrolled = data.get("enrolled", [])
        for c in enrolled:
            try:
                db.execute(
                    """INSERT INTO student_courses 
                       (user_id, course_id, rating, grade, completed, current_module_id, current_lesson_id, progress, enrolled_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, c["course_id"], c.get("rating", 0.0), c.get("grade", "N/A"),
                        c.get("completed", 0), c.get("current_module_id"), c.get("current_lesson_id"),
                        c.get("progress", 0.0), c.get("enrolled_at")
                    )
                )
            except Exception:
                db.execute(
                    """UPDATE student_courses SET
                       rating = ?, grade = ?, completed = ?, current_module_id = ?, 
                       current_lesson_id = ?, progress = ?
                       WHERE user_id = ? AND course_id = ?""",
                    (
                        c.get("rating", 0.0), c.get("grade", "N/A"), c.get("completed", 0), 
                        c.get("current_module_id"), c.get("current_lesson_id"), c.get("progress", 0.0),
                        user_id, c["course_id"]
                    )
                )
                
        # Restore exam results
        exams = data.get("exams", [])
        for e in exams:
            try:
                history_val = json.dumps(e.get("history", [])) if isinstance(e.get("history"), list) else (e.get("history") or '[]')
                db.execute(
                    """INSERT INTO exam_results 
                       (user_id, module_id, score, attempts, best_score, history, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, e["module_id"], e.get("score") or 0.0, e.get("attempts") or 1,
                        e.get("best_score") or 0.0, history_val, e.get("updated_at")
                    )
                )
            except Exception:
                history_val = json.dumps(e.get("history", [])) if isinstance(e.get("history"), list) else (e.get("history") or '[]')
                db.execute(
                    """UPDATE exam_results SET
                       score = ?, attempts = ?, best_score = ?, history = ?
                       WHERE user_id = ? AND module_id = ?""",
                    (
                        e.get("score") or 0.0, e.get("attempts") or 1, e.get("best_score") or 0.0,
                        history_val, user_id, e["module_id"]
                    )
                )
                
        # Restore complaints
        complaints = data.get("complaints", [])
        for c in complaints:
            try:
                db.execute(
                    """INSERT INTO complaints 
                       (user_id, subject, message, status, admin_response, created_at, resolved_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, c["subject"], c["message"], c.get("status", "pending"),
                        c.get("admin_response"), c.get("created_at"), c.get("resolved_at")
                    )
                )
            except Exception:
                pass
                
        # Restore notifications
        notifications = data.get("notifications", [])
        for n in notifications:
            try:
                db.execute(
                    """INSERT INTO notifications 
                       (user_id, message, is_read, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (
                        user_id, n["message"], n.get("is_read", 0), n.get("created_at")
                    )
                )
            except Exception:
                pass
                
        db.commit()
        return jsonify({"status": "success", "message": "State synchronized successfully"})

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
        try:
            from patch_db import patch_db
            patch_db()
        except Exception as e:
            app.logger.error(f"Error auto-running patch_db: {e}")

    # ── Error Handlers ──────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        import logging
        tb = traceback.format_exc()
        logging.error(f"500 Internal Server Error: {e}\n{tb}")
        print(f"500 Internal Server Error: {e}\n{tb}", flush=True)
        return render_template("errors/500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
