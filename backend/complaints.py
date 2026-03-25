"""
Complaints blueprint – users submit and track complaints.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.complaint import Complaint

complaints_bp = Blueprint("complaints", __name__)


@complaints_bp.route("/complaints")
@login_required
def my_complaints():
    """View the current user's complaints."""
    user_complaints = Complaint.get_for_user(current_user.id)
    return render_template("complaints.html", complaints=user_complaints)


@complaints_bp.route("/submit-complaint", methods=["GET", "POST"])
@login_required
def submit_complaint():
    """Submit a new complaint or question."""
    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not subject or not message:
            flash("Subject and message are required.", "error")
            return render_template("submit_complaint.html", subject=subject, message=message)

        if len(subject) > 200:
            flash("Subject must be less than 200 characters.", "error")
            return render_template("submit_complaint.html", subject=subject, message=message)

        Complaint.create(current_user.id, subject, message)
        flash("Your complaint has been submitted. We'll get back to you soon!", "success")
        return redirect(url_for("complaints.my_complaints"))

    return render_template("submit_complaint.html")
