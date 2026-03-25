"""
Recommendations blueprint – generate and display AI recommendations.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from engine.hybrid import get_recommendations, evaluate
from models.user import User
from models.course import Course
from models.database import get_db

recs_bp = Blueprint("recommendations", __name__)


@recs_bp.route("/recommend")
@login_required
def recommend():
    """Generate and display recommendations for the current user."""
    # Check if user has academic background set (cold-start)
    if not current_user.interests or not current_user.academic_field:
        return redirect(url_for('auth.complete_profile'))
        categories = Course.get_categories()
        return render_template(
            "interests.html",
            categories=categories,
            message="Please select your interests to get personalised recommendations.",
        )

    recommendations = get_recommendations(current_user.id, top_n=10)
    metrics = evaluate(current_user.id, k=10)

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        metrics=metrics,
    )


@recs_bp.route("/set-interests", methods=["POST"])
@login_required
def set_interests():
    """Save user interests (cold-start onboarding)."""
    interests = request.form.getlist("interests")
    if not interests:
        flash("Please select at least one interest.", "error")
        return redirect(url_for("recommendations.recommend"))

    User.update_interests(current_user.id, interests)
    flash("Interests saved! Generating your recommendations...", "success")
    return redirect(url_for("recommendations.recommend"))


@recs_bp.route("/courses")
@login_required
def browse_courses():
    """Browse all available courses with search and filtering."""
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "all")
    
    if query:
        courses = Course.search(query)
    else:
        courses = Course.get_all()
        
    if category and category != 'all':
        courses = [c for c in courses if c.category == category]
        
    categories = Course.get_categories()
    
    return render_template(
        "courses.html", 
        courses=courses, 
        categories=categories,
        search_query=query,
        selected_category=category
    )


@recs_bp.route("/course/<int:course_id>")
@login_required
def course_details(course_id):
    """View detailed information about a course, including enrollment status."""
    db = get_db()
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('recommendations.browse_courses'))

    # Check enrollment
    enrollment = db.execute(
        "SELECT * FROM student_courses WHERE user_id = ? AND course_id = ?",
        (current_user.id, course_id),
    ).fetchone()

    return render_template(
        "course_details.html",
        course=course,
        enrollment=enrollment
    )


@recs_bp.route("/enroll/<int:course_id>", methods=["POST"])
@login_required
def enroll(course_id):
    """Enroll the current user in a course."""
    db = get_db()
    existing = db.execute(
        "SELECT id FROM student_courses WHERE user_id = ? AND course_id = ?",
        (current_user.id, course_id),
    ).fetchone()
    if existing:
        flash("You are already enrolled in this course.", "info")
    else:
        db.execute(
            "INSERT INTO student_courses (user_id, course_id, enrolled_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (current_user.id, course_id),
        )
        db.commit()
        
        # Trigger notification
        course = Course.get_by_id(course_id)
        db.execute(
            "INSERT INTO notifications (user_id, message) VALUES (?, ?)",
            (current_user.id, f"Successfully enrolled in {course.title}! Start learning now.")
        )
        db.commit()
        
        flash("Enrolled successfully!", "success")
    return redirect(url_for("recommendations.course_details", course_id=course_id))


@recs_bp.route("/rate/<int:course_id>", methods=["POST"])
@login_required
def rate_course(course_id):
    """Rate and update grade for a course the user is enrolled in."""
    rating = float(request.form.get("rating", 0))
    grade = request.form.get("grade", "N/A")
    completed = 1 if request.form.get("completed") == "on" else 0
    
    if rating < 0 or rating > 5:
        flash("Rating must be between 0 and 5.", "error")
        return redirect(url_for("recommendations.course_details", course_id=course_id))

    db = get_db()
    db.execute(
        "UPDATE student_courses SET rating = ?, grade = ?, completed = ? WHERE user_id = ? AND course_id = ?",
        (rating, grade, completed, current_user.id, course_id),
    )
    db.commit()
    flash("Course progress updated!", "success")
    return redirect(url_for("recommendations.course_details", course_id=course_id))
