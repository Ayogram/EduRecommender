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


def generate_advisor_summary(user, top_recommendations):
    if not top_recommendations:
        return "Please complete your academic onboarding and configure past grades to generate your personalized AI recommendation summary."
        
    top_pick = top_recommendations[0]["title"]
    field = user.academic_field or "your field of interest"
    gpa = user.gpa or 0.0
    
    # Extract strengths and weaknesses from user.past_grades
    strengths = []
    weaknesses = []
    if user.past_grades:
        for course, grade in user.past_grades.items():
            if grade in ("A", "B"):
                strengths.append(course)
            elif grade in ("D", "E", "F"):
                weaknesses.append(course)
                
    strength_str = f"strong performance in {', '.join(strengths[:2])}" if strengths else "a solid academic foundation"
    weakness_str = f" while addressing areas of potential improvement like {', '.join(weaknesses[:1])}" if weaknesses else ""
    
    gpa_text = f"excellent CGPA of {gpa:.2f}" if gpa >= 3.5 else (f"good CGPA of {gpa:.2f}" if gpa >= 2.5 else f"CGPA of {gpa:.2f}")
    
    summary = (
        f"**{top_pick}** received the highest recommendation score because your profile demonstrated **{strength_str}**{weakness_str}, "
        f"matching your declared primary interest in **{field}** and your current **{gpa_text}**."
    )
    return summary


@recs_bp.route("/recommend")
@login_required
def recommend():
    """Generate and display recommendations for the current user."""
    recommendations = get_recommendations(current_user.id, top_n=12)
    
    # Parse JSON explanations
    for r in recommendations:
        try:
            r["explanation_data"] = json.loads(r["explanation"])
        except Exception:
            r["explanation_data"] = {
                "why": r.get("explanation", ""),
                "strengths": [],
                "career": "",
                "advice": ""
            }
            
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

    advisor_summary = generate_advisor_summary(current_user, recommendations)

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        high_success=high_success,
        low_success=low_success,
        metrics=metrics,
        advisor_summary=advisor_summary,
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
    interests = current_user.interests if isinstance(current_user.interests, list) else []
        
    # User's completed courses for mock past grades
    completed_courses = db.execute(
        """SELECT sc.course_id, c.title, sc.grade
           FROM student_courses sc JOIN courses c ON sc.course_id = c.id
           WHERE sc.user_id = ? AND sc.grade != 'N/A'""",
        (current_user.id,)
    ).fetchall()
    
    # Convert database completed courses to a dict structure for simulation parameter pre-population
    prepopulated_past_grades = {c["title"]: c["grade"] for c in completed_courses}
    
    # Merge with user's saved manual past grades from the users table
    if current_user.past_grades:
        for c_title, c_grade in current_user.past_grades.items():
            if c_title not in prepopulated_past_grades:
                prepopulated_past_grades[c_title] = c_grade
    
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
            
            # Smart comparison engine overrides for the simulator compared options
            if len(options) >= 2:
                # Sort options by success probability descending
                sorted_options = sorted(options, key=lambda x: x["success_probability"], reverse=True)
                
                # For each option, set comparative text
                for idx, opt in enumerate(sorted_options):
                    rank = idx + 1
                    if rank == 1:
                        second_title = sorted_options[1]["title"]
                        opt["advice"] = (
                            f"Highly recommended as your best option! It matches your primary interest and academic results. "
                            f"It ranks above '{second_title}' because it offers a closer match to your academic standing and interests."
                        )
                    elif rank == 2:
                        first_title = sorted_options[0]["title"]
                        third_text = f" and ranks above '{sorted_options[2]['title']}' due to better prerequisite alignment" if len(sorted_options) > 2 else ""
                        opt["advice"] = (
                            f"A solid second choice. It aligns well with your interests, but is ranked below '{first_title}' "
                            f"because '{first_title}' offers broader opportunities and a closer match to your academic standing{third_text}."
                        )
                    elif rank == 3:
                        first_title = sorted_options[0]["title"]
                        second_title = sorted_options[1]["title"]
                        opt["advice"] = (
                            f"Ranked lowest of the compared options. While suitable based on your strengths, your academic profile "
                            f"shows stronger alignment and success probability in '{first_title}' and '{second_title}'."
                        )
            
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
        
        # Update user's profile database record with these simulation parameters so they are saved permanently
        db = get_db()
        try:
            gpa_float = float(sim_gpa) if sim_gpa else 0.0
        except ValueError:
            gpa_float = 0.0
            
        db.execute(
            """UPDATE users SET gpa = ?, department = ?, academic_field = ?, interests = ? WHERE id = ?""",
            (gpa_float, sim_dept, sim_field, json.dumps(sim_interests_list), current_user.id)
        )
        db.commit()
        
        # Persist the simulated grades to the user's profile
        if sim_past_grades_dict:
            User.update_past_grades(current_user.id, sim_past_grades_dict)
            
        # Synchronise current_user state with session variables
        user = User.get_by_id(current_user.id)
        if user:
            from backend.auth import save_user_to_session
            save_user_to_session(user)
        
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




@recs_bp.route("/recommend/analyze-result", methods=["POST"])
@login_required
def analyze_result():
    """Receive a result-sheet image via AJAX multipart and return AI Vision analysis."""
    import os, base64
    import requests as req_lib

    result_file = request.files.get("result_file")
    if not result_file or not result_file.filename:
        return jsonify({"error": "No file received."}), 400

    file_bytes = result_file.read()
    if len(file_bytes) > 3 * 1024 * 1024:
        return jsonify({"error": "File too large. Please upload an image under 3 MB."}), 400

    mime_type = result_file.content_type or "image/jpeg"
    if not (mime_type.startswith("image/") or mime_type == "application/pdf"):
        return jsonify({"error": "Please upload an image or PDF file."}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"response": "**Result Sheet Uploaded** - AI reading is offline (no API key). Please manually add your grades using the Simulated Past Grades section."})

    vision_prompt = (
        "You are an expert academic result analyser for a university course recommender. "
        "The student uploaded their result sheet or transcript. "
        "Please read it carefully and extract all completed courses and their grades. "
        "Identify course codes and course titles (e.g., 'CSC313 Object-Oriented Programming') and map them to their corresponding letter grades (A, B, C, D, E, F). "
        "Please return ONLY a valid JSON object. The JSON must have the following keys:\n"
        "- \"gpa\": estimated or extracted GPA (float, default 0.0)\n"
        "- \"department\": estimated or extracted department string (e.g. 'Computer Science')\n"
        "- \"field\": estimated academic field (e.g. 'programming, IT')\n"
        "- \"interests\": estimated interests based on best grades (e.g. 'Web Dev, AI')\n"
        "- \"past_grades\": a dictionary mapping course names (Course Code + Course Title, e.g. 'CSC313 Object-Oriented Programming') to string grades (A, B, C, D, E, F). Do not skip any courses listed in the transcript.\n"
        "- \"analysis\": 2-3 encouraging sentences explaining which academic fields this student is best suited for and why based on their strong and weak subjects. Format with basic markdown.\n"
        "Return ONLY the raw JSON object, no markdown code block wrappers around it."
    )

    try:
        vision_payload = {"contents": [{"parts": []}]}
        
        if mime_type == "application/pdf":
            # Extract text from PDF using pypdf (pure python, avoids Vercel shared library crashes)
            import io
            import pypdf
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pdf_text = ""
            for page in pdf_reader.pages:
                try:
                    pdf_text += page.extract_text(extraction_mode="layout") + "\n"
                except TypeError:
                    pdf_text += page.extract_text() + "\n"
                
            pdf_prompt = (
                vision_prompt + 
                "\n\nHere is the raw text extracted from the PDF transcript. "
                "Because it was extracted as text, some columns might be slightly misaligned or scrambled. "
                "Please carefully scan the text to match the Course Codes/Titles with their exact corresponding letter grades (A, B, C, D, E, F). "
                "Do not hallucinate or guess. Rely strictly on the text provided below:\n"
                f"{pdf_text}"
            )
            vision_payload["contents"][0]["parts"].append({"text": pdf_prompt})
        else:
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            
        vision_payload["contents"][0]["parts"].append({"text": vision_prompt})
        vision_payload["contents"][0]["parts"].append({"inline_data": {"mime_type": mime_type, "data": b64_data}})

        vision_url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-2.5-flash:generateContent?key={api_key}"
        )
        vision_resp = req_lib.post(vision_url, json=vision_payload, timeout=25)
        if vision_resp.status_code == 200:
            candidates = vision_resp.json().get("candidates", [])
            if candidates:
                parts_list = candidates[0].get("content", {}).get("parts", [])
                if parts_list:
                    raw_text = parts_list[0].get("text", "").strip()
                    
                    # Robust extraction of JSON object
                    json_str = raw_text
                    start_idx = raw_text.find('{')
                    end_idx = raw_text.rfind('}')
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = raw_text[start_idx:end_idx+1]
                    
                    try:
                        import json
                        data = json.loads(json_str)
                        return jsonify(data)
                    except Exception as e:
                        current_app.logger.error(f"JSON parsing error: {e}. Raw text was: {raw_text}")
                        return jsonify({"response": raw_text, "error_parsing": str(e)})
        return jsonify({"error": f"AI service returned status {vision_resp.status_code}."}), 502
    except Exception as ex:
        current_app.logger.error(f"analyze_result error: {ex}")
        return jsonify({"error": "AI result reading timed out. Try a smaller or clearer image."}), 504
@recs_bp.route("/recommend/ask-advisor", methods=["POST"])
@login_required
def ask_advisor():
    import os
    import requests
    
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    history = data.get("history", [])
    course_a = data.get("course_a", "")
    course_b = data.get("course_b", "")
    course_c = data.get("course_c", "")
    
    sim_gpa = data.get("sim_gpa", "")
    sim_dept = data.get("sim_dept", "")
    sim_field = data.get("sim_field", "")
    sim_interests = data.get("sim_interests", "")
    sim_past_grades = data.get("sim_past_grades", {})
    
    if not query and not history:
        return jsonify({"error": "Empty question."}), 400
        
    # Construct profile string
    past_grades_str = ", ".join(f"{t}: {g}" for t, g in sim_past_grades.items()) if sim_past_grades else "None"
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    system_instruction = (
        "You are a premium AI Course Advisor at EduRecommender. "
        "The student is deciding between the provided courses. Use their simulated profile to offer tailored advice. "
        "If this is the first message, analyze which course aligns best. If this is a follow-up question, answer it directly and conversationally. "
        "Be professional, direct, and encouraging. Format your response beautifully with bold text and clean bullet points. "
        "Keep your responses concise."
    )
    
    if api_key:
        try:
            # Base context to inject into the FIRST message
            base_context = (
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
                base_context += f"- Course C: {course_c}\n"
                
            contents = []
            if not history:
                # Fallback if history missing
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"{base_context}\nSTUDENT QUESTION: {query}"}]
                })
            else:
                for i, msg in enumerate(history):
                    role = "user" if msg.get("role") == "user" else "model"
                    text = msg.get("text", "")
                    
                    if i == 0 and role == "user":
                        text = f"{base_context}\nSTUDENT QUESTION: {text}"
                        
                    contents.append({
                        "role": role,
                        "parts": [{"text": text}]
                    })
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": contents
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=25)
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
            
    # Smart offline fallback — generate a useful response from the student's profile data
    courses_compared = [c for c in [course_a, course_b, course_c] if c]
    courses_str = " vs. ".join(f"**{c}**" for c in courses_compared)
    
    reply = (
        f"**AI Course Advisor — Profile Analysis**\n\n"
        f"Comparing {courses_str} based on your academic profile:\n\n"
        f"**Your Profile Summary:**\n"
        f"- Department: {sim_dept or 'Not specified'}\n"
        f"- Academic Field: {sim_field or 'Not specified'}\n"
        f"- Simulated GPA: {sim_gpa or 'Not specified'}\n"
        f"- Interests: {sim_interests or 'Not specified'}\n\n"
    )
    
    # Give specific advice for each course
    for course in courses_compared:
        course_lower = course.lower()
        # Detect if the course matches the student's field
        dept_words = (sim_dept or "").lower().split()
        field_words = (sim_field or "").lower().split()
        course_matches = any(w in course_lower for w in dept_words + field_words if len(w) > 3)
        
        if course_matches:
            reply += f"✅ **{course}:** Strong alignment with your {sim_dept or sim_field} background. This course builds on knowledge you are already developing in your programme, making it a high-value choice.\n\n"
        else:
            reply += f"⚠️ **{course}:** This course appears to be outside your primary field. Your GPA shows academic capability, but expect to invest extra preparation time since this covers unfamiliar concepts.\n\n"
    
    if sim_gpa:
        try:
            gpa_val = float(sim_gpa)
            if gpa_val >= 3.5:
                reply += f"**GPA Note:** Your GPA of {sim_gpa} is excellent — you have the academic discipline to succeed in whichever course you choose, though staying within your field maximises your performance edge.\n\n"
            elif gpa_val >= 2.5:
                reply += f"**GPA Note:** Your GPA of {sim_gpa} is solid. Stick to courses within your department for the best results, as they complement your existing knowledge base.\n\n"
            else:
                reply += f"**GPA Note:** With a GPA of {sim_gpa}, focus on courses that align tightly with your core field. This reduces cognitive load and gives you the best chance of improving your standing.\n\n"
        except Exception:
            pass
    
    reply += f"**Final Recommendation:** Choose the course that most directly matches your {sim_dept or 'primary'} department. Depth in your core field is more valuable than breadth across unrelated subjects."
    
    return jsonify({"response": reply})
