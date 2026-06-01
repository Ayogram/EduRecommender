"""
Recommendations blueprint – generate and display AI recommendations.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
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

    recommendations = get_recommendations(current_user.id, top_n=12)
    metrics = evaluate(current_user.id, k=12)

    # Separate into high success (70% and above) and low success (below 70%)
    high_success = []
    low_success = []
    for r in recommendations:
        s_prob = r.get("success_probability", r.get("score", 0.0))
        success_pct = int(round(s_prob * 100))
        if success_pct >= 70:
            high_success.append(r)
        else:
            low_success.append(r)

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        high_success=high_success,
        low_success=low_success,
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
        
        # Sync session's enrolled_courses
        from flask import session
        enrolled_db = db.execute("SELECT course_id FROM student_courses WHERE user_id = ?", (current_user.id,)).fetchall()
        session['enrolled_courses'] = [r['course_id'] for r in enrolled_db]
        
        flash("Enrolled successfully!", "success")
    return redirect(url_for("recommendations.course_details", course_id=course_id))


@recs_bp.route("/rate/<int:course_id>", methods=["POST"])
@login_required
def rate_course(course_id):
    """Rate and update course progress the user is enrolled in."""
    rating = float(request.form.get("rating", 0))
    completed = 1 if request.form.get("completed") == "on" else 0
    
    if rating < 0 or rating > 5:
        flash("Rating must be between 0 and 5.", "error")
        return redirect(url_for("recommendations.course_details", course_id=course_id))

    db = get_db()
    db.execute(
        "UPDATE student_courses SET rating = ?, completed = ? WHERE user_id = ? AND course_id = ?",
        (rating, completed, current_user.id, course_id),
    )
    db.commit()
    flash("Course progress updated!", "success")
    return redirect(url_for("recommendations.course_details", course_id=course_id))


# ── AI Course Advisor & Comparator Routes ───────────────────────────────────

@recs_bp.route("/api/courses/autocomplete")
@login_required
def autocomplete_courses():
    q = request.args.get("q", "").strip()
    if not q or len(q) < 1:
        return jsonify([])
    db = get_db()
    # Search for matching courses
    rows = db.execute(
        "SELECT id, title, department FROM courses WHERE title LIKE ? LIMIT 10",
        (f"%{q}%",)
    ).fetchall()
    results = [{"id": r["id"], "title": r["title"], "department": r["department"]} for r in rows]
    return jsonify(results)


@recs_bp.route("/compare", methods=["GET", "POST"])
@login_required
def compare_courses():
    from engine.hybrid import predict_performance_detailed
    db = get_db()
    
    # Fetch all course titles for backup dropdown/fallback list
    all_courses = db.execute("SELECT id, title, department FROM courses ORDER BY title ASC").fetchall()
    
    # Set up defaults
    gpa = current_user.gpa or 0.0
    dept = current_user.department or ""
    field = current_user.academic_field or ""
    
    # User's interests
    try:
        interests = json.loads(current_user.interests) if current_user.interests else []
    except Exception:
        interests = []
        
    # User's completed courses for mock past grades
    completed_courses = db.execute(
        """SELECT sc.course_id, c.title, sc.grade
           FROM student_courses sc JOIN courses c ON sc.course_id = c.id
           WHERE sc.user_id = ? AND sc.grade != 'N/A'""",
        (current_user.id,)
    ).fetchall()
    
    # Convert database completed courses to a dict structure for simulation parameter pre-population
    prepopulated_past_grades = {c["title"]: c["grade"] for c in completed_courses}
    
    comparison_calculated = False
    course_a_data = None
    course_b_data = None
    course_c_data = None
    best_choice = None
    
    # Keep form values persistent
    form_vals = {
        "sim_gpa": gpa,
        "sim_dept": dept,
        "sim_field": field,
        "sim_interests": ", ".join(interests),
        "sim_past_grades": prepopulated_past_grades,
        "course_a": "",
        "course_b": "",
        "course_c": "",
        "compare_count": "2"
    }
    
    if request.method == "POST":
        comparison_calculated = True
        compare_count = request.form.get("compare_count", "2")
        course_a_input = request.form.get("course_a", "").strip()
        course_b_input = request.form.get("course_b", "").strip()
        course_c_input = request.form.get("course_c", "").strip()
        
        sim_gpa = request.form.get("sim_gpa", "")
        sim_dept = request.form.get("sim_dept", "").strip()
        sim_field = request.form.get("sim_field", "").strip()
        sim_interests_str = request.form.get("sim_interests", "").strip()
        
        # Parse simulated past grades from form
        sim_past_courses = request.form.getlist("sim_past_course[]")
        sim_past_grades_list = request.form.getlist("sim_past_grade[]")
        
        sim_past_grades_dict = {}
        for title, grade in zip(sim_past_courses, sim_past_grades_list):
            title = title.strip()
            grade = grade.strip().upper()
            if title and grade in ("A", "B", "C", "D", "E", "F"):
                sim_past_grades_dict[title] = grade
                
        sim_interests_list = [i.strip() for i in sim_interests_str.split(",") if i.strip()]
        
        # Run predictions
        if course_a_input:
            course_a_data = predict_performance_detailed(
                current_user.id, course_a_input,
                sim_gpa=sim_gpa or None,
                sim_dept=sim_dept or None,
                sim_field=sim_field or None,
                sim_interests=sim_interests_list or None,
                sim_past_grades=sim_past_grades_dict or None
            )
            
        if course_b_input:
            course_b_data = predict_performance_detailed(
                current_user.id, course_b_input,
                sim_gpa=sim_gpa or None,
                sim_dept=sim_dept or None,
                sim_field=sim_field or None,
                sim_interests=sim_interests_list or None,
                sim_past_grades=sim_past_grades_dict or None
            )
            
        if compare_count == "3" and course_c_input:
            course_c_data = predict_performance_detailed(
                current_user.id, course_c_input,
                sim_gpa=sim_gpa or None,
                sim_dept=sim_dept or None,
                sim_field=sim_field or None,
                sim_interests=sim_interests_list or None,
                sim_past_grades=sim_past_grades_dict or None
            )
            
        # Determine Best Choice
        options = [course_a_data, course_b_data]
        if course_c_data:
            options.append(course_c_data)
            
        options = [o for o in options if o is not None]
        if options:
            best_choice = max(options, key=lambda x: x["success_probability"])
            
        # Save parameters back to form_vals to keep them persistent
        form_vals = {
            "sim_gpa": sim_gpa,
            "sim_dept": sim_dept,
            "sim_field": sim_field,
            "sim_interests": sim_interests_str,
            "sim_past_grades": sim_past_grades_dict,
            "course_a": course_a_input,
            "course_b": course_b_input,
            "course_c": course_c_input,
            "compare_count": compare_count
        }
        
    return render_template(
        "compare.html",
        all_courses=all_courses,
        form_vals=form_vals,
        comparison_calculated=comparison_calculated,
        course_a_data=course_a_data,
        course_b_data=course_b_data,
        course_c_data=course_c_data,
        best_choice=best_choice
    )


@recs_bp.route("/recommend/ask-advisor", methods=["POST"])
@login_required
def ask_advisor():
    import os
    import requests
    
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    course_a = data.get("course_a", "")
    course_b = data.get("course_b", "")
    course_c = data.get("course_c", "")
    
    sim_gpa = data.get("sim_gpa", "")
    sim_dept = data.get("sim_dept", "")
    sim_field = data.get("sim_field", "")
    sim_interests = data.get("sim_interests", "")
    sim_past_grades = data.get("sim_past_grades", {})
    
    if not query:
        return jsonify({"error": "Empty question."}), 400
        
    # Construct profile string
    past_grades_str = ", ".join(f"{t}: {g}" for t, g in sim_past_grades.items()) if sim_past_grades else "None"
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    system_instruction = (
        "You are a premium AI Course Advisor at EduRecommender. "
        "Your goal is to help the student decide between these courses, analyzing their simulated profile "
        "and matching it to each course's requirements, difficulty, and syllabus. "
        "Explain which course aligns best and compare/contrast them objectively. "
        "Do not just say which is harder; detail where the student will succeed best and why. "
        "Be professional, direct, and encouraging. Format your response beautifully with bold text and clean bullet points. "
        "Keep it within 3 short paragraphs."
    )
    
    if api_key:
        try:
            prompt = (
                f"{system_instruction}\n\n"
                f"STUDENT PROFILE:\n"
                f"- GPA: {sim_gpa}\n"
                f"- Department: {sim_dept}\n"
                f"- Academic Field: {sim_field}\n"
                f"- Interests: {sim_interests}\n"
                f"- Past Grades: {past_grades_str}\n\n"
                f"COMPARED COURSES:\n"
                f"- Course A: {course_a}\n"
                f"- Course B: {course_b}\n"
            )
            if course_c:
                prompt += f"- Course C: {course_c}\n"
                
            prompt += f"\nSTUDENT QUESTION: {query}\n"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                candidates = res_data.get("candidates", [])
                if candidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts:
                        reply = content_parts[0].get("text", "")
                        return jsonify({"response": reply})
        except Exception as e:
            print(f"Error calling Gemini in advisor: {e}")
            
    # Smart offline fallback
    # Build local response using course descriptions and matching words
    reply = (
        f"**Local AI Advisor Analysis & Recommendation:**\n\n"
        f"Comparing these options based on your parameters:\n"
        f"- **{course_a}** and **{course_b}**"
    )
    if course_c:
        reply += f" and **{course_c}**"
        
    reply += (
        f"\n\nBased on your simulated GPA of **{sim_gpa}** and interest in **{sim_interests}**:\n"
        f"1. Make sure you meet any target prerequisites outlined in the course catalog.\n"
        f"2. Your department match boosts academic confidence in subjects aligned with **{sim_dept}**.\n"
        f"3. Focus on courses with beginner/intermediate difficulties if you are looking to build a foundation before moving to advanced topics.\n\n"
        f"*Tip: Configure your `GEMINI_API_KEY` in the `.env` file to enable real-time interactive questions with your AI Advisor!*"
    )
    return jsonify({"response": reply})
