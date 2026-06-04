"""
Admin blueprint – user management, stats, complaint management.
"""

import logging
import json
import os
import datetime
from collections import deque
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.course import Course
from models.complaint import Complaint
from models.recommendation import Recommendation
from models.database import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# A thread-safe buffer for recent log messages
log_buffer = deque(maxlen=50)

class BufferLogHandler(logging.Handler):
    def emit(self, record):
        try:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_buffer.append({
                "timestamp": now_str,
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name
            })
        except Exception:
            pass


def admin_required(f):
    """Decorator that restricts access to admin users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied. Administrator privileges required.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    """Decorator that restricts access to super admin users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_super_admin:
            flash("Unauthorized: Only Super Admin can perform this action.", "error")
            return redirect(url_for("admin.dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ───────────────────────────────────────────────────────────────

@admin_bp.route("/")
@admin_required
def dashboard():
    db = get_db()
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")
    verified_filter = request.args.get("verified", "all")

    # 1. Base counts from database
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_courses = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    total_recommendations = db.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
    pending_complaints = db.execute("SELECT COUNT(*) FROM complaints WHERE status = 'pending'").fetchone()[0]
    total_complaints = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    total_notifications = db.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]

    # 2. Active users (users with at least one course enrollment)
    active_users = db.execute("SELECT COUNT(DISTINCT user_id) FROM student_courses").fetchone()[0]

    # 3. Uploaded results (users who have non-empty past_grades)
    uploaded_results = db.execute(
        "SELECT COUNT(*) FROM users WHERE past_grades IS NOT NULL AND past_grades != '{}' AND past_grades != ''"
    ).fetchone()[0]

    # 4. Department Statistics
    dept_rows = db.execute(
        "SELECT department, COUNT(*) as count FROM users WHERE department IS NOT NULL AND department != '' GROUP BY department"
    ).fetchall()
    dept_stats = {r["department"]: r["count"] for r in dept_rows}

    # 5. Course Statistics (enrollments)
    course_enrollment_rows = db.execute(
        """SELECT c.title, COUNT(*) as count 
           FROM student_courses sc 
           JOIN courses c ON sc.course_id = c.id 
           GROUP BY c.title 
           ORDER BY count DESC LIMIT 5"""
    ).fetchall()
    course_enrollments = {r["title"]: r["count"] for r in course_enrollment_rows}

    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "total_courses": total_courses,
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "total_recommendations": total_recommendations,
        "uploaded_results": uploaded_results,
        "total_notifications": total_notifications,
        "dept_stats": dept_stats,
        "course_enrollments": course_enrollments
    }

    # 6. Diagnostics
    gemini_key = os.environ.get("GEMINI_API_KEY")
    mail_server = os.environ.get("MAIL_SERVER")
    
    diagnostics = {
        "db_status": "Online",
        "db_type": "PostgreSQL" if db.is_postgres else "SQLite",
        "gemini_api": "Configured & Active" if gemini_key else "Offline / Missing API Key",
        "mail_server": "Configured" if mail_server else "Not configured",
        "env_state": "Production (Vercel)" if os.environ.get("VERCEL") else "Development (Local)"
    }

    # 7. Recent logs
    recent_logs = list(log_buffer)
    
    users = User.get_all(
        search=search_query, 
        status=status_filter, 
        verified=verified_filter
    )
    
    return render_template(
        "admin/dashboard.html", 
        stats=stats, 
        users=users[:5],  # Only show latest 5 on overview
        diagnostics=diagnostics,
        recent_logs=recent_logs,
        search_query=search_query,
        status_filter=status_filter,
        verified_filter=verified_filter
    )


@admin_bp.route("/users")
@admin_required
def manage_users():
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "all")
    verified_filter = request.args.get("verified", "all")

    users = User.get_all(search=search_query, status=status_filter, verified=verified_filter)
    
    return render_template(
        "admin/manage_users.html",
        users=users,
        search_query=search_query,
        status_filter=status_filter,
        verified_filter=verified_filter,
    )


@admin_bp.route("/admins")
@super_admin_required
def manage_admins():
    search_query = request.args.get("q", "").strip()
    admins = User.get_all(search=search_query)
    admins = [u for u in admins if u.is_admin]
    
    return render_template(
        "admin/manage_admins.html",
        admins=admins,
        search_query=search_query,
    )


@admin_bp.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.dashboard"))
    
    from models.complaint import Complaint
    from models.recommendation import Recommendation
    user_complaints = Complaint.get_for_user(user_id)
    user_recs = Recommendation.get_for_user(user_id)
    
    return render_template(
        "admin/user_detail.html",
        user=user,
        complaints=user_complaints,
        recommendations=user_recs
    )


# ── User Management ────────────────────────────────────────────────────────

@admin_bp.route("/suspend/<int:user_id>", methods=["POST"])
@admin_required
def suspend_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "error")
    elif user.is_admin and not current_user.is_super_admin:
        flash("Unauthorized: Only Super Admin can manage other admins.", "error")
    elif user.is_super_admin:
        flash("Cannot suspend the Super Admin.", "error")
    else:
        User.update_status(user_id, "suspended")
        flash(f"User {user.name} has been suspended.", "warning")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/reactivate/<int:user_id>", methods=["POST"])
@admin_required
def reactivate_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "error")
    else:
        User.update_status(user_id, "active")
        flash(f"User {user.name} has been reactivated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/delete/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "error")
    elif user.is_admin and not current_user.is_super_admin:
        flash("Unauthorized: Only Super Admin can delete other admins.", "error")
    elif user.is_super_admin:
        flash("Cannot delete the Super Admin.", "error")
    else:
        User.delete(user_id)
        flash(f"User {user.name} has been deleted.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/invite-admin", methods=["GET", "POST"])
@super_admin_required
def invite_admin():
    from flask_mail import Message
    from app import mail
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Email is required.", "error")
        else:
            user = User.get_by_email(email)
            if user:
                if user.role == "user":
                    from models.database import get_db
                    db = get_db()
                    db.execute("UPDATE users SET role = 'admin', is_verified = 1 WHERE id = ?", (user.id,))
                    db.commit()
                    flash(f"Existing user {email} has been promoted to Admin.", "success")
                else:
                    flash(f"User {email} is already an {user.role}.", "info")
            else:
                # Invite new user (Simplified for now: User just registers with this email and gets admin role if implemented in User.create check or similar)
                # Better: I'll create the user with role='admin' immediately
                User.create(name=email.split('@')[0], email=email, role='admin', is_verified=1)
                flash(f"Account for {email} created with Admin privileges.", "success")
            
            # Send invitation email
            try:
                msg = Message("Admin Invitation – EduRecommender", recipients=[email])
                msg.body = f"You have been invited to be an Administrator on EduRecommender.\n\nPlease log in at {url_for('auth.login', _external=True)}"
                mail.send(msg)
            except Exception:
                flash("Admin role assigned, but invitation email failed.", "warning")

        return redirect(url_for("admin.dashboard"))
    return render_template("admin/invite.html")


# ── Complaint Management ────────────────────────────────────────────────────

@admin_bp.route("/complaints")
@admin_required
def complaints():
    all_complaints = Complaint.get_all()
    return render_template("admin/complaints.html", complaints=all_complaints)


@admin_bp.route("/complaints/respond/<int:complaint_id>", methods=["POST"])
@admin_required
def respond_complaint(complaint_id):
    response = request.form.get("response", "").strip()
    if not response:
        flash("Response cannot be empty.", "error")
    else:
        Complaint.respond(complaint_id, response)
        
        # 🔔 NOTIFICATION SYSTEM
        complaint = Complaint.get_by_id(complaint_id)
        if complaint:
            try:
                from models.database import get_db
                db = get_db()
                db.execute(
                    "INSERT INTO notifications (user_id, message) VALUES (?, ?)",
                    (complaint.user_id, f"An administrator has responded to your complaint '{complaint.subject}': '{response}'")
                )
                db.commit()
            except Exception as e:
                print(f"Notification error: {e}")
        
        flash("Complaint resolved and user notified.", "success")
    return redirect(url_for("admin.complaints"))


# ── Course Management ───────────────────────────────────────────────────────

@admin_bp.route("/courses")
@admin_required
def manage_courses():
    search_query = request.args.get("q", "").strip()
    courses = Course.search(search_query) if search_query else Course.get_all()
    return render_template(
        "admin/manage_courses.html",
        courses=courses,
        search_query=search_query
    )


@admin_bp.route("/course/add", methods=["GET", "POST"])
@admin_required
def add_course():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        difficulty = request.form.get("difficulty")
        description = request.form.get("description")
        department = request.form.get("department")
        prerequisites = request.form.get("prerequisites", "None")
        credits = request.form.get("credits", 3)
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        
        db = get_db()
        db.execute(
            """INSERT INTO courses (title, category, difficulty, description, department, prerequisites, credits, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, category, difficulty, description, department, prerequisites, credits, json.dumps(tags))
        )
        db.commit()
        flash("Course added successfully!", "success")
        return redirect(url_for("admin.manage_courses"))
        
    return render_template("admin/edit_course.html", course=None)


@admin_bp.route("/course/edit/<int:course_id>", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for("admin.manage_courses"))
        
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        difficulty = request.form.get("difficulty")
        description = request.form.get("description")
        department = request.form.get("department")
        prerequisites = request.form.get("prerequisites", "None")
        credits = request.form.get("credits", 3)
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        
        db = get_db()
        db.execute(
            """UPDATE courses SET title = ?, category = ?, difficulty = ?, description = ?, 
                               department = ?, prerequisites = ?, credits = ?, tags = ?
               WHERE id = ?""",
            (title, category, difficulty, description, department, prerequisites, credits, json.dumps(tags), course_id)
        )
        db.commit()
        flash("Course updated successfully!", "success")
        return redirect(url_for("admin.manage_courses"))
        
    return render_template("admin/edit_course.html", course=course)


@admin_bp.route("/course/delete/<int:course_id>", methods=["POST"])
@admin_required
def delete_course(course_id):
    db = get_db()
    db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    db.commit()
    flash("Course deleted successfully.", "info")
    return redirect(url_for("admin.manage_courses"))
