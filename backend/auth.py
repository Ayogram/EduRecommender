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


def send_verification_email(user):
    """Generates and sends a dark-themed HTML verification email to the user."""
    from app import mail
    token = user.get_verification_token()
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    # Mail sender info
    sender_name = "EduRecommender AI Advisor"
    sender_email = current_app.config.get('MAIL_USERNAME', 'ajumobiayomipo@gmail.com')
    sender = (sender_name, sender_email)
    
    msg = Message(
        "Verify Your EduRecommender Account",
        recipients=[user.email],
        sender=sender
    )
    
    # Plain text fallback body
    msg.body = (
        f"Welcome {user.name}!\n\n"
        f"Thank you for joining EduRecommender. Please verify your email by clicking the link:\n"
        f"{verify_url}\n\n"
        f"If you did not register, please ignore this email."
    )
    
    # Dark themed HTML body
    msg.html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Verify Your EduRecommender Account</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #0f0f15;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{
      max-width: 540px;
      margin: 40px auto;
      background-color: #161622;
      border-radius: 16px;
      border: 1px solid #2a2a3c;
      padding: 40px;
      color: #e2e8f0;
      text-align: center;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }}

    h1 {{
      font-size: 24px;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 12px 0;
      letter-spacing: -0.02em;
    }}
    p {{
      font-size: 15px;
      line-height: 1.6;
      color: #94a3b8;
      margin: 0 0 28px 0;
    }}
    .btn {{
      display: inline-block;
      background-color: #6366f1;
      color: #ffffff !important;
      text-decoration: none;
      padding: 14px 32px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 15px;
      transition: background-color 0.2s ease;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}
    .btn:hover {{
      background-color: #4f46e5;
    }}
    .link-alt {{
      font-size: 13px;
      color: #64748b;
      margin-top: 30px;
      word-break: break-all;
    }}
    .link-alt a {{
      color: #6366f1;
      text-decoration: none;
    }}
    .footer {{
      font-size: 12px;
      color: #475569;
      border-top: 1px solid #2a2a3c;
      padding-top: 24px;
      margin-top: 32px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <table align="center" border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto 28px auto; text-align: center;">
      <tr>
        <td style="padding-right: 10px; vertical-align: middle;">
          <span style="display: inline-block; background-color: #6366f1; width: 30px; height: 30px; line-height: 30px; border-radius: 50%; text-align: center; color: #ffffff; font-size: 16px; font-weight: bold; font-family: sans-serif;">✓</span>
        </td>
        <td style="vertical-align: middle; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 22px; font-weight: 500; color: #ffffff; letter-spacing: -0.02em;">
          Edu<strong style="color: #6366f1; font-weight: 800;">Recommender</strong>
        </td>
      </tr>
    </table>
    <h1>Verify Your Account</h1>
    <p>Welcome, {user.name}! Thank you for signing up for <strong>EduRecommender</strong>. Please click the button below to verify your email address and activate your student portal profile.</p>
    <div>
      <a href="{verify_url}" class="btn">Verify Email Address</a>
    </div>
    <div class="link-alt">
      Or copy and paste this link in your web browser:<br>
      <a href="{verify_url}">{verify_url}</a>
    </div>
    <div class="footer">
      This is an automated security email from EduRecommender AI. If you did not sign up for an account, you can safely ignore this email.
    </div>
  </div>
</body>
</html>"""
    mail.send(msg)


# ── Registration ────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    # Load field mappings for the template
    fields_file = os.path.join(current_app.root_path, "database", "fields_and_interests.json")
    with open(fields_file, "r") as f:
        fields_map = json.load(f)

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
            return render_template("auth/register.html", name=name, email=email, fields_map=fields_map)

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
            send_verification_email(user)
            flash("Registration successful! Please check your email to verify your account.", "info")
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {e}")
            flash("Account created, but we couldn't send a verification email. Please try logging in to resend it.", "warning")

        return redirect(url_for("auth.verify_please", email=user.email))

    return render_template("auth/register.html", fields_map=fields_map)


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
                return redirect(url_for('auth.login'))
            else:
                try:
                    send_verification_email(user)
                    flash("Verification email resent. Please check your inbox.", "success")
                except Exception as e:
                    flash("Could not send email. Please try again later.", "error")
                    return redirect(url_for('auth.login'))
        else:
            flash("No account found with that email.", "error")
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.verify_please', email=email))
    return render_template("auth/resend_verification.html")


@auth_bp.route("/verify-please")
def verify_please():
    email = request.args.get("email")
    if not email:
        return redirect(url_for("auth.login"))
    return render_template("auth/verify_please.html", email=email)


@auth_bp.route("/api/check-verified")
def check_verified():
    email = request.args.get("email")
    if not email:
        return jsonify({"verified": False}), 400
    user = User.get_by_email(email)
    if user and user.is_verified == 1:
        return jsonify({"verified": True})
    return jsonify({"verified": False})


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

    if request.args.get("verified") == "true":
        flash("Your account has been verified! You can now log in.", "success")
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
    override_uri = current_app.config.get("GOOGLE_OVERRIDE_REDIRECT_URI")
    if override_uri:
        redirect_uri = override_uri
    else:
        redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/login/google/callback")
def google_callback():
    try:
        override_uri = current_app.config.get("GOOGLE_OVERRIDE_REDIRECT_URI")
        if override_uri:
            token = oauth.google.authorize_access_token(redirect_uri=override_uri)
        else:
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
        # Unified Interest Parsing for new chip-based UI (handles list or comma-separated)
        raw_interests = request.form.getlist("interests")
        interests_list = []
        for val in raw_interests:
            if "," in val:
                interests_list.extend([i.strip() for i in val.split(",") if i.strip()])
            elif val.strip():
                interests_list.append(val.strip())
        
        custom_interests = request.form.get("custom_interests", "").split(",")
        custom_list = [i.strip() for i in custom_interests if i.strip()]
        
        all_interests = list(set(interests_list + custom_list))
        
        # 1. Update Profile Text Data
        department = request.form.get("department", "").strip()
        gpa = request.form.get("gpa", 0.0)
        try:
            gpa = float(gpa)
        except ValueError:
            gpa = 0.0

        if name:
            User.update_profile(current_user.id, name, nickname, academic_field, all_interests, department=department, gpa=gpa)
            # Automatically regenerate recommendations to reflect profile updates immediately
            try:
                from engine.hybrid import get_recommendations
                get_recommendations(current_user.id, top_n=12)
            except Exception:
                pass
            
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
        # Unified Interest Parsing
        raw_interests = request.form.get("interests", "")
        interests_list = [i.strip() for i in raw_interests.split(",") if i.strip()]
        
        custom_interests = request.form.get("custom_interests", "").split(",")
        custom_list = [i.strip() for i in custom_interests if i.strip()]
        
        all_interests = list(set(interests_list + custom_list))
        
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
