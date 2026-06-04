"""
Learning blueprint – handles course modules, lessons, and AI-driven classroom content.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import get_db, ensure_enrollment
import json
import urllib.request
import urllib.parse
import re

learning_bp = Blueprint("learning", __name__, url_prefix="/learning")

def search_youtube_video(query):
    try:
        # Clean query to prevent search parsing issues
        clean_query = re.sub(r'[^\w\s-]', '', query).strip()
        search_term = f"{clean_query} tutorial lecture"
        encoded_query = urllib.parse.quote(search_term)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # Request with user-agent to bypass blockages
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8')
            
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if video_ids:
            # Get the first unique video id
            seen = set()
            unique_ids = [x for x in video_ids if not (x in seen or seen.add(x))]
            if unique_ids:
                return f"https://www.youtube.com/embed/{unique_ids[0]}"
    except Exception as e:
        print(f"Error searching YouTube for '{query}': {e}")
        
    # Categorized fallback high-quality course playlist videos
    query_lower = query.lower()
    if any(k in query_lower for k in ["research", "methodology", "thesis", "academic writing"]):
        return "https://www.youtube.com/embed/nJza2kfI8GU"
    elif any(k in query_lower for k in ["mis", "information system", "management information"]):
        return "https://www.youtube.com/embed/rN9e8-p56H0"
    elif any(k in query_lower for k in ["programming", "code", "python", "java", "script"]):
        return "https://www.youtube.com/embed/rfscVS0vtbw"
    elif any(k in query_lower for k in ["structure", "algorithm", "dsa"]):
        return "https://www.youtube.com/embed/8hly31xKjhc"
    elif any(k in query_lower for k in ["database", "sql"]):
        return "https://www.youtube.com/embed/HXV3zeQKqGY"
    elif any(k in query_lower for k in ["ethic", "philosophy", "justice"]):
        return "https://www.youtube.com/embed/kBdfcR-8hEY"
    elif any(k in query_lower for k in ["business", "management", "finance", "accounting", "marketing"]):
        return "https://www.youtube.com/embed/rN9e8-p56H0"
    elif any(k in query_lower for k in ["anatomy", "medicine", "health"]):
        return "https://www.youtube.com/embed/uBGl2BujkPQ"
    elif any(k in query_lower for k in ["law", "rights", "legal"]):
        return "https://www.youtube.com/embed/sTz5L_O5ZGU"
    return "https://www.youtube.com/embed/rN9e8-p56H0"

def update_course_grade_if_completed(db, user_id, course_id):
    # 1. Get all module IDs for this course
    modules = db.execute(
        "SELECT id FROM course_modules WHERE course_id = ? ORDER BY sort_order",
        (course_id,)
    ).fetchall()
    module_ids = [m['id'] for m in modules]
    
    if not module_ids:
        return
        
    # 2. Get exam results for these modules
    placeholders = ",".join("?" for _ in module_ids)
    results = db.execute(
        f"SELECT module_id, best_score FROM exam_results WHERE user_id = ? AND module_id IN ({placeholders})",
        [user_id] + module_ids
    ).fetchall()
    
    # Check if they have completed exams for all modules
    completed_module_ids = {r['module_id'] for r in results}
    if len(completed_module_ids) == len(module_ids):
        # Calculate average of best scores
        avg_score = sum(r['best_score'] for r in results) / len(results)
        
        # Map average to letter grade
        if avg_score >= 70:
            grade = "A"
        elif avg_score >= 60:
            grade = "B"
        elif avg_score >= 50:
            grade = "C"
        elif avg_score >= 45:
            grade = "D"
        elif avg_score >= 40:
            grade = "E"
        else:
            grade = "F"
            
        # Update student_courses
        db.execute(
            "UPDATE student_courses SET grade = ?, completed = 1 WHERE user_id = ? AND course_id = ?",
            (grade, user_id, course_id)
        )
        db.commit()

@learning_bp.route("/course/<int:course_id>/module/<int:module_id>")
@login_required
def view_lesson(course_id, module_id):
    db = get_db()
    
    # 1. Check enrollment
    enrollment = ensure_enrollment(db, current_user.id, course_id)
    
    if not enrollment:
        flash("Please enroll in the course to start learning.", "warning")
        return redirect(url_for('recommendations.course_details', course_id=course_id))

    # 2. Get/Generate Module Data
    # Fetch all modules for this course to see if they are initialized
    modules = db.execute(
        "SELECT * FROM course_modules WHERE course_id = ? ORDER BY sort_order",
        (course_id,)
    ).fetchall()
    
    if not modules:
        # Lazy Initialization: If no modules exist for this course in the DB
        course = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        if course:
            titles = ["Foundational Principles", "Intermediate Methodologies", "Final Assessment & Capstone"]
            for i, title in enumerate(titles):
                db.execute(
                    "INSERT INTO course_modules (course_id, title, sort_order) VALUES (?, ?, ?)",
                    (course_id, title, i+1)
                )
            db.commit()
            modules = db.execute(
                "SELECT * FROM course_modules WHERE course_id = ? ORDER BY sort_order",
                (course_id,)
            ).fetchall()
            
    # Locate the active module from the list
    module = None
    for m in modules:
        if m['id'] == module_id:
            module = m
            break
            
    if not module:
        # Fallback: treat module_id as a 1-indexed sort order (1, 2, or 3)
        for m in modules:
            if m['sort_order'] == module_id:
                module = m
                break
                
    if not module:
        # Final fallback: default to the first module
        module = modules[0]

    # 3. Get/Generate Lessons for this module
    lessons = db.execute(
        "SELECT * FROM module_lessons WHERE module_id = ? ORDER BY sort_order",
        (module['id'],)
    ).fetchall()
    
    course = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()

    if not lessons:
        # Generate initial AI content placeholder if no lessons exist
        from engine.tutor import TutorEngine
        
        # In a real app, this would be an async call. Here we do it sync for simplicity
        tutor = TutorEngine()
        new_lessons = tutor.generate_module_content(course['title'], module['title'])
        
        for i, l in enumerate(new_lessons):
            video_query = f"{course['title']} - {l['title']}"
            video_url = search_youtube_video(video_query)
            db.execute(
                "INSERT INTO module_lessons (module_id, title, content, video_url, sort_order) VALUES (?, ?, ?, ?, ?)",
                (module['id'], l['title'], l['content'], video_url, i+1)
            )
        db.commit()
        lessons = db.execute(
            "SELECT * FROM module_lessons WHERE module_id = ? ORDER BY sort_order",
            (module['id'],)
        ).fetchall()

    # 4. Get active lesson (or first one)
    lesson_id = request.args.get('lesson_id', type=int)
    current_lesson = None
    if lesson_id:
        current_lesson = next((l for l in lessons if l['id'] == lesson_id), lessons[0])
    else:
        current_lesson = lessons[0]

    # Convert to dict to allow adding video_url on the fly
    current_lesson_dict = dict(current_lesson)
    
    if not current_lesson_dict.get('video_url'):
        video_query = f"{course['title']} - {current_lesson_dict['title']}"
        video_url = search_youtube_video(video_query)
        db.execute(
            "UPDATE module_lessons SET video_url = ? WHERE id = ?",
            (video_url, current_lesson_dict['id'])
        )
        db.commit()
        current_lesson_dict['video_url'] = video_url

    # 5. Update progress
    db.execute(
        "UPDATE student_courses SET current_module_id = ?, current_lesson_id = ? WHERE user_id = ? AND course_id = ?",
        (module['id'], current_lesson_dict['id'], current_user.id, course_id)
    )
    db.commit()

    # 6. Get all modules for sidebar navigation
    all_modules = db.execute(
        "SELECT * FROM course_modules WHERE course_id = ? ORDER BY sort_order",
        (course_id,)
    ).fetchall()

    # Find current lesson index to enable prev/next navigation
    current_idx = 0
    for idx, l in enumerate(lessons):
        if l['id'] == current_lesson_dict['id']:
            current_idx = idx
            break

    prev_lesson = lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = lessons[current_idx + 1] if current_idx < len(lessons) - 1 else None
    progress_pct = int(((current_idx + 1) / len(lessons)) * 100) if lessons else 0

    return render_template(
        "learning/classroom.html",
        course_id=course_id,
        course=course,
        module=module,
        lessons=lessons,
        current_lesson=current_lesson_dict,
        all_modules=all_modules,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        progress_pct=progress_pct
    )

@learning_bp.route("/course/<int:course_id>/download-syllabus")
@login_required
def download_syllabus(course_id):
    db = get_db()
    course = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('main.dashboard'))
        
    modules = db.execute(
        "SELECT * FROM course_modules WHERE course_id = ? ORDER BY sort_order",
        (course_id,)
    ).fetchall()
    
    if not modules:
        modules = [
            {"id": None, "title": "Foundational Principles"},
            {"id": None, "title": "Intermediate Methodologies"},
            {"id": None, "title": "Final Assessment & Capstone"}
        ]
    
    syllabus_text = []
    syllabus_text.append("======================================================================")
    syllabus_text.append(f"                    EDU RECOMMENDER COURSE SYLLABUS")
    syllabus_text.append("======================================================================")
    syllabus_text.append(f"Course Title  : {course['title']}")
    syllabus_text.append(f"Department    : {course['department']}")
    syllabus_text.append(f"Category      : {course['category']}")
    syllabus_text.append(f"Credits       : {course['credits']} units")
    syllabus_text.append(f"Difficulty    : {course['difficulty'].capitalize()}")
    syllabus_text.append(f"Prerequisites : {course['prerequisites']}")
    syllabus_text.append("\nCourse Description:")
    syllabus_text.append(course['description'])
    syllabus_text.append("\n======================================================================")
    syllabus_text.append("                            CURRICULUM OUTLINE")
    syllabus_text.append("======================================================================")
    
    for i, mod in enumerate(modules):
        syllabus_text.append(f"\nModule {i+1}: {mod['title']}")
        syllabus_text.append("-" * (len(mod['title']) + 10))
        
        lessons = db.execute(
            "SELECT * FROM module_lessons WHERE module_id = ? ORDER BY sort_order",
            (mod['id'],)
        ).fetchall()
        
        if lessons:
            for j, lesson in enumerate(lessons):
                syllabus_text.append(f"  Week {(i*4) + j + 1}: {lesson['title']}")
            syllabus_text.append(f"  Week {(i*4) + 4}: Module Quiz / Assessment")
        else:
            # Fallback list if lessons aren't generated yet
            from engine.tutor import TutorEngine
            tutor = TutorEngine()
            category = tutor._determine_category(course['title'], "")
            curriculum = tutor.curriculum_data.get(category, tutor.default_category)
            
            if i == 0:
                lessons_pool = curriculum.get("Foundational Principles", [])
            elif i == 1:
                lessons_pool = curriculum.get("Intermediate Methodologies", [])
            else:
                lessons_pool = curriculum.get("Final Assessment & Capstone", [])
                
            for j, l in enumerate(lessons_pool):
                title_clean = l['title'].replace("{course_title}", course['title']).replace("{module_title}", mod['title'])
                syllabus_text.append(f"  Week {(i*4) + j + 1}: {title_clean}")
            syllabus_text.append(f"  Week {(i*4) + 4}: Module Quiz / Assessment")
                
    syllabus_text.append("\n======================================================================")
    syllabus_text.append("Generated automatically by EduRecommender AI Advisor.")
    syllabus_text.append("======================================================================")
    
    file_content = "\n".join(syllabus_text)
    
    from flask import Response
    response = Response(file_content, mimetype="text/plain")
    clean_title = re.sub(r'[^\w\s-]', '', course['title']).strip().replace(' ', '_')
    response.headers["Content-Disposition"] = f"attachment; filename=syllabus_{clean_title}.txt"
    return response

@learning_bp.route("/module/<int:module_id>/quiz-preview")
@login_required
def quiz_preview(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM course_modules WHERE id = ?", (module_id,)).fetchone()
    if not module:
        flash("Module not found.", "error")
        return redirect(url_for('main.dashboard'))
        
    course_id = module['course_id']
    course = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    
    enrollment = ensure_enrollment(db, current_user.id, course_id)
    if not enrollment:
        flash("Please enroll in this course before taking assessments.", "warning")
        return redirect(url_for('recommendations.course_details', course_id=course_id))
        
    exam = db.execute("SELECT * FROM module_exams WHERE module_id = ?", (module_id,)).fetchone()
    if not exam:
        from engine.tutor import TutorEngine
        tutor = TutorEngine()
        # Fetch actual lessons to align MCQ generation with lesson videos
        lessons_rows = db.execute(
            "SELECT title, video_url FROM module_lessons WHERE module_id = ? ORDER BY sort_order",
            (module_id,)
        ).fetchall()
        lessons_list = [dict(l) for l in lessons_rows]
        questions = tutor.generate_mcqs(course['title'], module['title'], lessons_info=lessons_list)
        db.execute(
            "INSERT INTO module_exams (module_id, questions) VALUES (?, ?)",
            (module_id, json.dumps(questions))
        )
        db.commit()
        exam = db.execute("SELECT * FROM module_exams WHERE module_id = ?", (module_id,)).fetchone()

    questions = json.loads(exam['questions'])
    question_count = len(questions)
    time_limit = question_count * 2
    
    result = db.execute(
        "SELECT attempts, best_score FROM exam_results WHERE user_id = ? AND module_id = ?",
        (current_user.id, module_id)
    ).fetchone()
    attempts = result['attempts'] if result else 0
    best_score = result['best_score'] if result else None
    
    return render_template(
        "learning/quiz_preview.html",
        module=module,
        course=course,
        question_count=question_count,
        time_limit=time_limit,
        attempts=attempts,
        best_score=best_score
    )

@learning_bp.route("/module/<int:module_id>/exam")
@login_required
def start_exam(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM course_modules WHERE id = ?", (module_id,)).fetchone()
    if not module:
        flash("Module not found.", "error")
        return redirect(url_for('main.dashboard'))

    # Check/Generate Exam
    exam = db.execute("SELECT * FROM module_exams WHERE module_id = ?", (module_id,)).fetchone()
    if not exam:
        from engine.tutor import TutorEngine
        tutor = TutorEngine()
        course = db.execute("SELECT title FROM courses WHERE id = ?", (module['course_id'],)).fetchone()
        questions = tutor.generate_mcqs(course['title'], module['title'])
        db.execute(
            "INSERT INTO module_exams (module_id, questions) VALUES (?, ?)",
            (module_id, json.dumps(questions))
        )
        db.commit()
        exam = db.execute("SELECT * FROM module_exams WHERE module_id = ?", (module_id,)).fetchone()

    questions = json.loads(exam['questions'])
    return render_template("learning/exam.html", module=module, questions=questions)

@learning_bp.route("/module/<int:module_id>/submit-exam", methods=["POST"])
@login_required
def submit_exam(module_id):
    db = get_db()
    exam = db.execute("SELECT * FROM module_exams WHERE module_id = ?", (module_id,)).fetchone()
    if not exam:
        return jsonify({"error": "Exam not found"}), 404
        
    questions = json.loads(exam['questions'])
    user_answers = request.form.to_dict()
    
    score = 0
    total = len(questions)
    results = []
    
    for i, q in enumerate(questions):
        # Key in form is usually 'q_0', 'q_1', etc.
        user_ans = user_answers.get(f"q_{i}")
        is_correct = (user_ans == q['correct_answer'])
        if is_correct:
            score += 1
        results.append({
            "question": q['question'],
            "your_answer": user_ans,
            "correct_answer": q['correct_answer'],
            "is_correct": is_correct
        })
    
    percentage = (score / total) * 100
    
    # Save results
    existing = db.execute(
        "SELECT * FROM exam_results WHERE user_id = ? AND module_id = ?",
        (current_user.id, module_id)
    ).fetchone()
    
    from datetime import datetime
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if existing:
        history = json.loads(existing['history'])
        history.append({"score": percentage, "date": now_str})
        best = max(existing['best_score'], percentage)
        db.execute(
            "UPDATE exam_results SET score = ?, attempts = attempts + 1, best_score = ?, history = ? WHERE id = ?",
            (percentage, best, json.dumps(history), existing['id'])
        )
        attempts = existing['attempts'] + 1
        best_score = best
    else:
        db.execute(
            "INSERT INTO exam_results (user_id, module_id, score, best_score, history) VALUES (?, ?, ?, ?, ?)",
            (current_user.id, module_id, percentage, percentage, json.dumps([{"score": percentage, "date": now_str}]))
        )
        attempts = 1
        best_score = percentage
    db.commit()
    
    # Auto-calculate and update course grade
    module_info = db.execute("SELECT course_id FROM course_modules WHERE id = ?", (module_id,)).fetchone()
    if module_info:
        update_course_grade_if_completed(db, current_user.id, module_info['course_id'])
    
    return render_template("learning/exam_result.html", score=percentage, total=total, results=results, module_id=module_id, attempts=attempts, best_score=best_score)

@learning_bp.route("/ask-tutor", methods=["POST"])
@login_required
def ask_tutor():
    import os
    import requests
    
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    lesson_title = data.get("lesson_title", "")
    lesson_content = data.get("lesson_content", "")
    
    if not query:
        return jsonify({"error": "Query is empty"}), 400
        
    api_key = os.environ.get("GEMINI_API_KEY")
    
    system_instruction = (
        "You are an encouraging and expert AI Study Companion on the EduRecommender platform. "
        "Your goal is to help the student understand the current lesson content effectively. "
        "Keep your explanation concise (max 3 short paragraphs), clear, and highly educational. "
        "Use bullet points, bold text, and code blocks (if applicable) to format your response beautifully. "
        "Only answer questions that are related to the lesson context. If the question is off-topic, "
        "politely guide the student back to the lesson."
    )
    
    if api_key:
        try:
            # Construct API payload
            prompt = (
                f"{system_instruction}\n\n"
                f"CURRENT LESSON CONTEXT:\n"
                f"Title: {lesson_title}\n"
                f"Content:\n{lesson_content}\n\n"
                f"STUDENT QUESTION: {query}\n"
            )
            
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
                # Parse output text from Gemini response structure
                candidates = res_data.get("candidates", [])
                if candidates:
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if content_parts:
                        reply = content_parts[0].get("text", "")
                        return jsonify({"response": reply})
            
            # If API call succeeds but returns an error status or empty candidate
            print(f"Gemini API returned error or empty response: {response.text}")
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            
    # Fallback to local intelligent response (offline/no API key)
    # Search for keywords in the lesson content
    query_lower = query.lower()
    found_section = None
    
    # Split lesson content by markdown headers
    sections = re.split(r'(###\s+)', lesson_content)
    assembled_sections = []
    i = 0
    while i < len(sections):
        if sections[i] == "### ":
            if i + 1 < len(sections):
                assembled_sections.append("### " + sections[i+1])
                i += 2
            else:
                i += 1
        else:
            assembled_sections.append(sections[i])
            i += 1
            
    # Search for a matching section
    for section in assembled_sections:
        if any(word in section.lower() for word in query_lower.split() if len(word) > 3):
            found_section = section.strip()
            break
            
    if found_section:
        reply = (
            f"Here is what the lesson says about that:\n\n"
            f"{found_section}\n\n"
            f"*Tip: Add your `GEMINI_API_KEY` to the `.env` file to enable real-time interactive questions with your AI Tutor!*"
        )
    else:
        # Default response listing the lesson sections
        headers = [line.strip() for line in lesson_content.split("\n") if line.strip().startswith("###")]
        headers_str = "\n".join(f"- {h.replace('###', '').strip()}" for h in headers)
        
        reply = (
            f"I am here to help you study **{lesson_title}**!\n\n"
            f"This lesson covers the following main topics:\n"
            f"{headers_str}\n\n"
            f"What specific part would you like to review? (Note: Add a `GEMINI_API_KEY` in `.env` to enable full real-time conversations!)"
        )
        
    return jsonify({"response": reply})
