"""
Authentication blueprint – registration, login, logout, Google OAuth.
"""

import json
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, session, current_app, jsonify
)
import os
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from flask_mail import Message
from werkzeug.utils import secure_filename
from models.user import User
from models.database import get_db

auth_bp = Blueprint("auth", __name__)

# Google OAuth will be initialised when the blueprint is registered
oauth = OAuth()


def init_oauth(app):
    """Bind OAuth to the Flask app and register Google provider."""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
        client_kwargs={"scope": "openid email profile"},
    )


# ── Registration ────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        interests = request.form.getlist("interests")

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters.")
        if not email or "@" not in email:
            errors.append("Please enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.get_by_email(email):
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/register.html", name=name, email=email)

        # Handle academic data
        academic_field = request.form.get("academic_field")
        interests = request.form.getlist("interests")
        custom_interests = request.form.get("custom_interests", "").split(",")
        all_interests = list(set([i.strip() for i in interests + custom_interests if i.strip()]))


        user = User.create(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            interests=all_interests,
            academic_field=academic_field,
            is_verified=0
        )
        
        # Send verification email
        try:
            from app import mail
            token = user.get_verification_token()
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            msg = Message("Verify Your EduRecommender Account", recipients=[user.email])
            msg.body = f"Welcome {user.name}!\n\nPlease verify your account by clicking the link: {verify_url}\n\nIf you didn't register, please ignore this email."
            mail.send(msg)
            flash("Registration successful! Please check your email to verify your account.", "info")
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {e}")
            flash("Account created, but we couldn't send a verification email. Please try logging in to resend it.", "warning")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/verify/<token>")
def verify_email(token):
    user = User.verify_token(token)
    if not user:
        flash("The verification link is invalid or has expired.", "error")
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash("Account already verified. Please log in.", "info")
    else:
        # Update user to be verified
        from models.database import get_db
        db = get_db()
        db.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (user.id,))
        db.commit()
        flash("Your account has been verified! You can now log in.", "success")
    
    return redirect(url_for('auth.login'))


@auth_bp.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.get_by_email(email)
        if user:
            if user.is_verified:
                flash("This account is already verified.", "info")
            else:
                try:
                    from app import mail
                    token = user.get_verification_token()
                    verify_url = url_for('auth.verify_email', token=token, _external=True)
                    msg = Message("Verify Your EduRecommender Account", recipients=[user.email])
                    msg.body = f"Hello {user.name},\n\nPlease verify your account by clicking: {verify_url}"
                    mail.send(msg)
                    flash("Verification email resent. Please check your inbox.", "success")
                except Exception as e:
                    flash("Could not send email. Please try again later.", "error")
        else:
            flash("No account found with that email.", "error")
        return redirect(url_for('auth.login'))
    return render_template("auth/resend_verification.html")


# ── Login ───────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.get_by_email(email)
        if not user or not user.password_hash:
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", email=email)

        if not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", email=email)

        if user.status == "suspended":
            flash("Your account has been suspended. Please contact an administrator.", "error")
            return render_template("auth/login.html", email=email)

        if not user.is_verified:
            flash("Please verify your email address before logging in.", "warning")
            return render_template("auth/login.html", email=email, show_resend=True)

        # Escalation check for Super Admin
        super_admin_email = current_app.config.get('SUPER_ADMIN_EMAIL')
        if email == super_admin_email and user.role != 'super_admin':
            db = get_db()
            db.execute("UPDATE users SET role = 'super_admin', is_verified = 1 WHERE id = ?", (user.id,))
            db.commit()
            user = User.get_by_id(user.id)

        login_user(user, remember=True)
        session.permanent = True
        flash(f"Welcome back, {user.name}!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html")


# ── Logout ──────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── Google OAuth ────────────────────────────────────────────────────────────

@auth_bp.route("/login/google")
def google_login():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            user_info = oauth.google.userinfo()

        google_id = user_info["sub"]
        email = user_info["email"].lower()
        name = user_info.get("name", email.split("@")[0])
        picture = user_info.get("picture", "/static/img/default_avatar.png")

        # Check if user exists
        user = User.get_by_google_id(google_id)
        if not user:
            user = User.get_by_email(email)

        if user:
            # Escalation check for Super Admin
            super_admin_email = current_app.config.get('SUPER_ADMIN_EMAIL')
            if email == super_admin_email and user.role != 'super_admin':
                db = get_db()
                db.execute("UPDATE users SET role = 'super_admin', is_verified = 1 WHERE id = ?", (user.id,))
                db.commit()
                # Re-fetch user to reflect new role
                user = User.get_by_id(user.id)

            if user.status == "suspended":
                flash("Your account has been suspended.", "error")
                return redirect(url_for("auth.login"))
            login_user(user, remember=True)
            # If returning user lacks academic field, prompt completion
            if not user.academic_field:
                return redirect(url_for("auth.complete_profile"))
        else:
            user = User.create(
                name=name, email=email, google_id=google_id,
                profile_picture=picture, is_verified=1 # Google users are verified
            )
            login_user(user, remember=True)
            # New Google users MUST complete profile
            return redirect(url_for("auth.complete_profile"))

        session.permanent = True
        flash(f"Welcome, {user.name}!", "success")
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {e}")
        flash("Google login failed. Please try again.", "error")
        return redirect(url_for("auth.login"))

# ── Password Recovery & Profile ──────────────────────────────────────────

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    from app import mail
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("Email is required.", "error")
            return render_template("auth/forgot_password.html")
            
        user = User.get_by_email(email)
        if user:
            token = user.get_reset_token()
            msg = Message("Password Reset Request", recipients=[user.email])
            link = url_for('auth.reset_password', token=token, _external=True)
            msg.body = f"To reset your password, visit: {link}\nIf you didn't request this, ignore this email."
            mail.send(msg)
            flash("An email has been sent with instructions to reset your password.", "info")
            return redirect(url_for('auth.login'))
        else:
            flash("If an account exists with that email, a reset link has been sent.", "info")
            return redirect(url_for('auth.login'))
    return render_template("auth/forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        if not password or password != confirm:
            flash("Passwords do not match or are empty.", "error")
            return render_template("auth/reset_password.html")
            
        hashed_password = generate_password_hash(password)
        User.update_password(user.id, hashed_password)
        flash("Your password has been updated! You can now log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template("auth/reset_password.html")

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        nickname = request.form.get("nickname", "").strip()
        academic_field = request.form.get("academic_field")
        interests = request.form.getlist("interests")
        custom_interests = request.form.get("custom_interests", "").split(",")
        
        # Merge predefined and custom interests
        all_interests = list(set([i.strip() for i in interests + custom_interests if i.strip()]))
        
        # 1. Update Profile Text Data
        department = request.form.get("department", "").strip()
        gpa = request.form.get("gpa", 0.0)
        try:
            gpa = float(gpa)
        except ValueError:
            gpa = 0.0

        if name:
            User.update_profile(current_user.id, name, nickname, academic_field, all_interests, department=department, gpa=gpa)
            
        # 2. Handle Avatar Upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                # Ensure upload directory exists
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
                os.makedirs(upload_path, exist_ok=True)
                
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                
                # Update DB
                avatar_url = f"/static/uploads/avatars/{filename}"
                User.update_avatar(current_user.id, avatar_url)

        # 3. Handle Password Update (optional)
        new_password = request.form.get("password")
        if new_password and len(new_password) >= 8:
            hashed = generate_password_hash(new_password)
            User.update_password(current_user.id, hashed)
            flash("Profile and password updated successfully!", "success")
        else:
            flash("Profile updated successfully!", "success")
            
        return redirect(url_for('auth.profile'))
    
    # Load field mappings for the template
    fields_file = os.path.join(current_app.root_path, "database", "fields_and_interests.json")
    with open(fields_file, "r") as f:
        fields_map = json.load(f)
        
    return render_template("auth/profile.html", fields_map=fields_map)

# ── Academic Overhaul Endpoints ──────────────────────────────────────────

@auth_bp.route("/api/sub-interests/<field>")
def get_sub_interests(field):
    fields_file = os.path.join(current_app.root_path, "database", "fields_and_interests.json")
    try:
        with open(fields_file, "r") as f:
            fields_map = json.load(f)
        return {"sub_interests": fields_map.get(field, [])}
    except Exception:
        return {"sub_interests": []}

@auth_bp.route("/complete-profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    if request.method == "POST":
        academic_field = request.form.get("academic_field")
        interests = request.form.getlist("interests")
        custom_interests = request.form.get("custom_interests", "").split(",")
        
        all_interests = list(set([i.strip() for i in interests + custom_interests if i.strip()]))
        
        if not academic_field:
            flash("Please select your academic field.", "error")
            return redirect(url_for('auth.complete_profile'))

        department = request.form.get("department")
        gpa = request.form.get("gpa", 0.0)
        try:
            gpa = float(gpa)
        except ValueError:
            gpa = 0.0

        db = get_db()
        db.execute(
            "UPDATE users SET academic_field = ?, department = ?, gpa = ?, interests = ? WHERE id = ?",
            (academic_field, department, gpa, json.dumps(all_interests), current_user.id)
        )
        db.commit()
        
        flash("Profile completed! Welcome to EduRecommender.", "success")
        return redirect(url_for("main.dashboard"))

    fields_file = os.path.join(current_app.root_path, "database", "fields_and_interests.json")
    with open(fields_file, "r") as f:
        fields_map = json.load(f)
        
    return render_template("auth/complete_profile.html", fields_map=fields_map)
