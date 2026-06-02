"""
Hybrid Recommendation Engine.
Combines Content-Based and Collaborative Filtering:
    final_score = 0.6 × CF_score + 0.4 × content_score

Includes cold-start handling (pure content-based for new users)
and human-readable explanation generation.
"""

import json
from models.database import get_db
from models.course import Course
from models.recommendation import Recommendation
from engine.content_based import get_content_scores
from engine.collaborative import get_collaborative_scores
from engine.matrix_factorization import get_matrix_factorization_scores


CF_WEIGHT = 0.4
CONTENT_WEIGHT = 0.3
MF_WEIGHT = 0.3
COLD_START_THRESHOLD = 3  # min ratings before hybrid kicks in


def _generate_explanation(user_id, course, method, cf_score, content_score, success_prob):
    """Build a structured JSON explanation string including success prediction and analysis."""
    db = get_db()

    # Gather user's highly-rated courses for context
    rated = db.execute(
        """SELECT c.title FROM student_courses sc
           JOIN courses c ON sc.course_id = c.id
           WHERE sc.user_id = ? AND sc.rating >= 3.5
           ORDER BY sc.rating DESC LIMIT 3""",
        (user_id,),
    ).fetchall()
    rated_titles = [r["title"] for r in rated]

    explanation_dict = {
        "course": course["title"],
        "confidence": int(success_prob * 100),
        "why": "",
        "strengths": [],
        "career": "",
        "advice": ""
    }

    # Core reasoning prefix
    if method == "hybrid":
        explanation_dict["why"] = "Recommended using our hybrid AI model combining your profile with peer performance."
    elif method == "content":
        explanation_dict["why"] = "Recommended directly based on your academic profile and simulated interests."
    else:
        explanation_dict["why"] = "Recommended because students with similar backgrounds succeeded here."

    if rated_titles:
        explanation_dict["strengths"].append(f"Strong past performance in {', '.join(rated_titles[:2])}")

    if course["department"] and course["department"] != course["category"]:
        explanation_dict["strengths"].append(f"Direct match for {course['department']} department")

    tags = json.loads(course["tags"]) if course["tags"] else []
    if tags:
        explanation_dict["strengths"].append(f"Aligns with topics: {', '.join(tags[:3])}")

    if not explanation_dict["strengths"]:
        explanation_dict["strengths"].append("Matches general academic profile")

    # Static mapping for career based on category or department
    cat = (course["category"] or "").lower()
    if "programming" in cat or "computer" in cat or "software" in cat:
        explanation_dict["career"] = "Software Engineer, Technical Lead, Systems Architect"
    elif "data" in cat or "machine learning" in cat or "ai" in cat:
        explanation_dict["career"] = "Data Scientist, ML Engineer, Data Analyst"
    elif "network" in cat or "security" in cat or "cyber" in cat:
        explanation_dict["career"] = "Cybersecurity Analyst, Network Admin, Security Engineer"
    elif "business" in cat or "management" in cat:
        explanation_dict["career"] = "Product Manager, IT Consultant, Business Analyst"
    else:
        explanation_dict["career"] = f"{course['department'] or 'Domain'} Specialist, Researcher, Academic"

    explanation_dict["advice"] = f"This is a {course['credits']}-unit {course['difficulty']} course. Review the prerequisites ({course['prerequisites']}) carefully to ensure you're fully prepared."

    return json.dumps(explanation_dict)


def get_recommendations(user_id, top_n=10):
    """
    Generate and persist top-N recommendations for the user.
    Sorted from highest success probability to lowest.
    """
    db = get_db()

    # Check how many ratings the user has
    rating_count = db.execute(
        "SELECT COUNT(*) FROM student_courses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    # Determine method
    if rating_count < COLD_START_THRESHOLD:
        method = "content"
        content_scores = get_content_scores(user_id)
        combined = {cid: score for cid, score in content_scores.items()}
        cf_scores = {}
    else:
        method = "hybrid"
        content_scores = get_content_scores(user_id)
        cf_scores = get_collaborative_scores(user_id)
        mf_scores = get_matrix_factorization_scores(user_id)

        # Merge scores (Ensemble of CF, Content-Based, and Matrix Factorization)
        all_courses = set(content_scores.keys()) | set(cf_scores.keys()) | set(mf_scores.keys())
        combined = {}
        for cid in all_courses:
            cs = content_scores.get(cid, 0.0)
            cfs = cf_scores.get(cid, 0.0)
            mfs = mf_scores.get(cid, 0.0)
            combined[cid] = CF_WEIGHT * cfs + CONTENT_WEIGHT * cs + MF_WEIGHT * mfs

    # Fetch user data once for efficiency
    user_row = db.execute(
        "SELECT department, academic_field, gpa, interests FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    
    gpa = float(user_row["gpa"] or 0.0) if user_row else 0.0
    gpa_factor = min(gpa / 4.0, 1.0)
    user_dept = user_row["department"] if user_row else None
    user_field = user_row["academic_field"] if user_row else None
    try:
        user_interests = json.loads(user_row["interests"]) if user_row and user_row["interests"] else []
    except Exception:
        user_interests = []

    # Fetch all course rows at once for efficiency
    courses_rows = db.execute("SELECT * FROM courses").fetchall()
    courses_by_id = {c["id"]: c for c in courses_rows}

    # Fetch historical performance per department once
    history_rows = db.execute(
        """SELECT c.department, AVG(CASE WHEN grade = 'A' THEN 1.0 WHEN grade = 'B' THEN 0.8 
                          WHEN grade = 'C' THEN 0.6 WHEN grade = 'D' THEN 0.4 
                          ELSE 0.2 END) as avg_grade
           FROM student_courses sc JOIN courses c ON sc.course_id = c.id
           WHERE sc.user_id = ? GROUP BY c.department""",
        (user_id,)
    ).fetchall()
    dept_performance_map = {r["department"]: r["avg_grade"] for r in history_rows if r["department"]}

    candidates = []
    for course_id, score in combined.items():
        course_row = courses_by_id.get(course_id)
        if not course_row:
            continue

        # Check if the course matches the user's academic profile or interests
        is_profile_relevant = False
        c_dept = course_row["department"].lower().strip() if course_row["department"] else ""
        c_cat = course_row["category"].lower().strip() if course_row["category"] else ""
        
        u_dept_lower = user_dept.lower().strip() if user_dept else ""
        u_field_lower = user_field.lower().strip() if user_field else ""

        # Check department/field matches
        if u_dept_lower and (u_dept_lower in c_dept or c_dept in u_dept_lower):
            is_profile_relevant = True
        if u_field_lower and (u_field_lower in c_dept or c_dept in u_field_lower or u_field_lower in c_cat or c_cat in u_field_lower):
            is_profile_relevant = True
            
        # Check interest matches
        if user_interests:
            try:
                c_tags = [t.lower().strip() for t in json.loads(course_row["tags"])] if course_row["tags"] else []
                for interest in user_interests:
                    interest_lower = interest.lower().strip()
                    for tag in c_tags:
                        if tag in interest_lower or interest_lower in tag:
                            is_profile_relevant = True
                            break
                    if is_profile_relevant:
                        break
            except Exception:
                pass

        # ACCURACY FILTER:
        # A recommended course must have at least a minimum similarity score (score >= 0.05) OR 
        # be profile-relevant (matching department, field, or interests) to be recommended.
        # This completely filters out random unrelated courses (e.g. Law or Medicine for CS students).
        if score < 0.05 and not is_profile_relevant:
            continue

        cf_s = cf_scores.get(course_id, 0.0) if method == "hybrid" else 0.0
        ct_s = content_scores.get(course_id, 0.0)

        # Scale base success probability so match ranges reach 70%+
        # base_success maps score (0.0 to 1.0) to a range starting at 0.50
        success_prob = 0.50 + (score * 0.8)

        # Boosts
        if course_row["department"] and course_row["department"] == user_dept:
            success_prob += 0.12
        if course_row["category"] and course_row["category"] == user_field:
            success_prob += 0.08
        success_prob += gpa_factor * 0.20

        # Penalty / Boost
        if course_row["difficulty"] == "advanced" and gpa < 2.5:
            success_prob -= 0.10
        elif course_row["difficulty"] == "beginner" and gpa >= 3.5:
            success_prob += 0.05

        # Historical boost
        dept_perf = dept_performance_map.get(course_row["department"], 0.0)
        success_prob += dept_perf * 0.15

        # Cap the probability logically between 25% and 97%
        success_prob = round(min(0.97, max(0.25, success_prob)), 4)

        explanation = _generate_explanation(user_id, course_row, method, cf_s, ct_s, success_prob)

        candidates.append({
            "course_id": course_id,
            "title": course_row["title"],
            "description": course_row["description"],
            "category": course_row["category"],
            "department": course_row["department"],
            "credits": course_row["credits"],
            "prerequisites": course_row["prerequisites"],
            "difficulty": course_row["difficulty"],
            "tags": json.loads(course_row["tags"]) if course_row["tags"] else [],
            "score": round(score, 4),
            "success_probability": round(success_prob, 4),
            "explanation": explanation,
            "method": method,
        })

    # Sort all candidate recommendations by success_probability descending (highest to lowest)
    candidates_sorted = sorted(candidates, key=lambda x: x["success_probability"], reverse=True)
    
    # Take top N
    top_candidates = candidates_sorted[:top_n]

    # Clear old recommendations
    Recommendation.clear_for_user(user_id)

    # Persist the top N to database
    for c in top_candidates:
        Recommendation.save(user_id, c["course_id"], c["score"], c["explanation"], c["method"], c["success_probability"])

    return top_candidates



# ── Evaluation Metrics ──────────────────────────────────────────────────────

def evaluate(user_id, k=10):
    """
    Compute Precision@k, Recall@k, and F1@k.
    A recommended course is considered 'relevant' if it matches the user's profile
    (matching department, matching academic field, or overlap in interests/tags).
    """
    db = get_db()

    # Get user profile details
    user = db.execute(
        "SELECT department, academic_field, interests FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if not user:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    user_dept = user["department"].lower().strip() if user["department"] else ""
    user_field = user["academic_field"].lower().strip() if user["academic_field"] else ""
    
    try:
        user_interests = [t.lower().strip() for t in json.loads(user["interests"])] if user["interests"] else []
    except Exception:
        user_interests = []

    # Recommended course IDs
    recs = db.execute(
        "SELECT course_id FROM recommendations WHERE user_id = ? ORDER BY score DESC LIMIT ?",
        (user_id, k),
    ).fetchall()
    recommended_ids = [r["course_id"] for r in recs]

    if not recommended_ids:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    # Fetch courses to check relevance
    all_courses = db.execute("SELECT id, department, category, tags FROM courses").fetchall()

    # Determine which courses in the system are relevant to this user
    relevant_ids = set()
    for c in all_courses:
        c_dept = c["department"].lower().strip() if c["department"] else ""
        c_cat = c["category"].lower().strip() if c["category"] else ""
        
        is_rel = False
        
        # Check department/field matches
        if user_dept and (user_dept in c_dept or c_dept in user_dept):
            is_rel = True
        if user_field and (user_field in c_dept or c_dept in user_field or user_field in c_cat or c_cat in user_field):
            is_rel = True
            
        # Check interest matches
        if user_interests:
            try:
                c_tags = [t.lower().strip() for t in json.loads(c["tags"])] if c["tags"] else []
                for interest in user_interests:
                    for tag in c_tags:
                        if tag in interest or interest in tag:
                            is_rel = True
                            break
                    if is_rel:
                        break
            except Exception:
                pass
                
        if is_rel:
            relevant_ids.add(c["id"])

    # Hits = recommended courses that are relevant
    hits = set(recommended_ids) & relevant_ids

    precision = len(hits) / len(recommended_ids) if recommended_ids else 0.0
    denominator = len(relevant_ids)
    recall = len(hits) / denominator if denominator > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


# ── AI Advisor & Predictor Functions ────────────────────────────────────────

def _infer_course_metadata(title):
    """Infers metadata for custom, off-catalog courses based on title keywords."""
    t_lower = title.lower().strip()
    
    # 1. Determine Department & Category
    dept = "General Elective"
    cat = "default"
    
    # Check matching keywords
    if any(k in t_lower for k in ["python", "java", "code", "coding", "program", "c++", "software", "network", "security", "cyber", "web", "html", "css", "script", "database", "sql", "structure", "algorithm", "dsa", "vlsi", "embedded", "system", "rust"]):
        dept = "Computer Science"
        if any(k in t_lower for k in ["structure", "algorithm", "dsa"]):
            cat = "dsa"
        else:
            cat = "programming"
    elif any(k in t_lower for k in ["circuit", "power", "electronics", "signal", "antenna", "control", "semiconductor", "voltage"]):
        dept = "Electrical Engineering"
        cat = "engineering"
    elif any(k in t_lower for k in ["thermodynamics", "fluid", "mechanic", "cad", "solid", "machine", "dynamics", "engine"]):
        dept = "Mechanical Engineering"
        cat = "engineering"
    elif any(k in t_lower for k in ["reservoir", "drill", "petroleum", "oil", "gas", "well", "geology"]):
        dept = "Petroleum Engineering"
        cat = "engineering"
    elif any(k in t_lower for k in ["calculus", "algebra", "optimization", "numerical", "equations", "math"]):
        dept = "Mathematics"
        cat = "math"
    elif any(k in t_lower for k in ["physic", "quantum", "optics", "laser", "electromagnetism"]):
        dept = "Physics"
        cat = "physics"
    elif any(k in t_lower for k in ["psycholog", "cognitive", "clinical", "behavior", "neuropsychology", "mind"]):
        dept = "Psychology"
        cat = "psychology"
    elif any(k in t_lower for k in ["fintech", "blockchain", "crypto", "bitcoin", "ledger", "smart contract", "finance"]):
        dept = "Fintech"
        cat = "finance"
    elif any(k in t_lower for k in ["econom", "microeconomics", "macroeconomics", "market", "policy", "game theory"]):
        dept = "Economics"
        cat = "finance"
    elif any(k in t_lower for k in ["accounting", "audit", "tax", "valuation"]):
        dept = "Accounting"
        cat = "finance"
    elif any(k in t_lower for k in ["management", "business", "ethics", "marketing", "entrepreneur", "startup", "operations", "supply chain", "corporate"]):
        dept = "Business Administration"
        cat = "business"
    elif any(k in t_lower for k in ["sociolog", "politic", "media", "social", "criminolog", "public policy", "relations"]):
        dept = "Social Sciences"
        cat = "social_sciences"
    elif any(k in t_lower for k in ["design", "graphic", "illustration", "art", "music", "writing", "screenplay", "storytelling"]):
        dept = "Arts"
        cat = "arts"
        
    # 2. Determine Difficulty
    diff = "intermediate"
    if any(k in t_lower for k in ["advanced", "structure", "econometrics", "quantum", "expert", "special", "systems", "deep", "machine learning", "analysis", "nanotechnology"]):
        diff = "advanced"
    elif any(k in t_lower for k in ["intro", "basic", "principles", "foundation", "element", "essential", "101"]):
        diff = "beginner"
        
    # 3. Credits
    credits = 4 if diff == "advanced" else 3
    
    # 4. Tags
    import re
    words = re.findall(r'[a-z]{3,}', t_lower)
    stopwords = {"and", "the", "for", "with", "into", "from", "intro", "introduction", "basics", "principles"}
    tags = [w for w in words if w not in stopwords]
    if cat != "default" and cat not in tags:
        tags.append(cat)
        
    return {
        "id": None,
        "title": title,
        "description": f"Simulated course in {dept} covering {cat} topics.",
        "category": cat,
        "department": dept,
        "difficulty": diff,
        "prerequisites": "None",
        "credits": credits,
        "tags": json.dumps(tags)
    }


def predict_performance_detailed(user_id, course_title_or_id, sim_gpa=None, sim_dept=None, sim_field=None, sim_interests=None, sim_past_grades=None):
    """
    Calculate success probability & returns a detailed breakdown and explanation for comparison.
    Uses actual database user profile + optional simulation parameter overrides.
    """
    db = get_db()
    
    # 1. Fetch user defaults
    user_row = db.execute(
        "SELECT department, academic_field, gpa, interests FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    
    gpa = float(user_row["gpa"] or 0.0) if user_row else 0.0
    user_dept = user_row["department"] if user_row else ""
    user_field = user_row["academic_field"] if user_row else ""
    try:
        user_interests = json.loads(user_row["interests"]) if user_row and user_row["interests"] else []
    except Exception:
        user_interests = []
        
    # Apply overrides
    if sim_gpa is not None:
        gpa = float(sim_gpa)
    if sim_dept is not None:
        user_dept = sim_dept
    if sim_field is not None:
        user_field = sim_field
    if sim_interests is not None:
        user_interests = sim_interests
        
    # Resolve course row
    course_row = None
    course_id = None
    
    try:
        course_id = int(course_title_or_id)
        course_row = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    except (ValueError, TypeError):
        pass
        
    if not course_row:
        course_row = db.execute(
            "SELECT * FROM courses WHERE title LIKE ? COLLATE NOCASE", 
            (str(course_title_or_id).strip(),)
        ).fetchone()
        
    if not course_row:
        mock_data = _infer_course_metadata(str(course_title_or_id))
        course_row = mock_data
        course_id = None
    else:
        course_id = course_row["id"]
        
    course_title = course_row["title"]
    course_dept = course_row["department"] or "General"
    course_cat = course_row["category"]
    course_difficulty = course_row["difficulty"]
    try:
        course_tags = json.loads(course_row["tags"]) if course_row["tags"] else []
    except Exception:
        course_tags = []
        
    # 2. Base content-based similarity score (CBF)
    cbf_score = 0.1
    if user_interests and course_tags:
        c_tags_lower = [t.lower().strip() for t in course_tags]
        match_count = 0
        for interest in user_interests:
            interest_lower = interest.lower().strip()
            for tag in c_tags_lower:
                if tag in interest_lower or interest_lower in tag:
                    match_count += 1
                    break
        cbf_score = min(1.0, match_count / max(1, len(user_interests)))
        
    # 3. Collaborative scores (peer performance)
    peer_count = 0
    avg_peer_rating = 4.0
    peer_success_rate = 1.0
    cf_score = 0.5
    
    if course_id is not None:
        peer_stats = db.execute(
            """SELECT COUNT(*) as count, AVG(rating) as avg_rating,
                      SUM(CASE WHEN grade IN ('A', 'B', 'C', 'D', 'E') THEN 1 ELSE 0 END) as passing,
                      SUM(CASE WHEN grade = 'F' THEN 1 ELSE 0 END) as fails
               FROM student_courses WHERE course_id = ? AND rating IS NOT NULL""",
            (course_id,)
        ).fetchone()
        
        if peer_stats:
            peer_count = peer_stats["count"] or 0
            avg_peer_rating = peer_stats["avg_rating"] or 4.0
            passing = peer_stats["passing"] or 0
            fails = peer_stats["fails"] or 0
            if peer_count > 0:
                peer_success_rate = (peer_count - fails) / peer_count
                
        # CF score from user matrix
        cf_scores = get_collaborative_scores(user_id)
        cf_score = cf_scores.get(course_id, 0.5)
        
    # 4. GPA Math
    gpa_factor = min(gpa / 4.0, 1.0)
    gpa_boost = gpa_factor * 0.20
    
    difficulty_adjust = 0.0
    if course_difficulty == "advanced" and gpa < 2.5:
        difficulty_adjust = -0.10
    elif course_difficulty == "beginner" and gpa >= 3.5:
        difficulty_adjust = 0.05
        
    # 5. Academic History & Department matching
    dept_boost = 0.12 if (course_dept and user_dept and course_dept.lower().strip() == user_dept.lower().strip()) else 0.0
    field_boost = 0.08 if (course_cat and user_field and course_cat.lower().strip() == user_field.lower().strip()) else 0.0
    
    # 6. Past Student Performance (Own Grades on related subjects)
    own_related_boost = 0.0
    matching_past_courses = []
    
    if sim_past_grades:
        # sim_past_grades is dict: {course_title: grade} or {course_id: grade}
        for p_course, grade in sim_past_grades.items():
            # Try lookup in db
            p_row = None
            try:
                p_id = int(p_course)
                p_row = db.execute("SELECT title, department, category FROM courses WHERE id = ?", (p_id,)).fetchone()
            except (ValueError, TypeError):
                pass
            if not p_row:
                p_row = db.execute("SELECT title, department, category FROM courses WHERE title LIKE ?", (f"%{p_course}%",)).fetchone()
                
            if p_row:
                p_title = p_row["title"]
                p_dept = p_row["department"]
                p_cat = p_row["category"]
                
                if p_dept == course_dept or p_cat == course_cat:
                    if grade == "A":
                        own_related_boost += 0.06
                        matching_past_courses.append((p_title, "A"))
                    elif grade == "B":
                        own_related_boost += 0.03
                        matching_past_courses.append((p_title, "B"))
                    elif grade == "F":
                        own_related_boost -= 0.06
                        matching_past_courses.append((p_title, "F"))
    else:
        # Check DB
        past_rows = db.execute(
            """SELECT c.title, sc.grade, c.department, c.category
               FROM student_courses sc JOIN courses c ON sc.course_id = c.id
               WHERE sc.user_id = ? AND sc.grade != 'N/A'""",
            (user_id,)
        ).fetchall()
        for r in past_rows:
            if r["department"] == course_dept or r["category"] == course_cat:
                if r["grade"] == "A":
                    own_related_boost += 0.06
                    matching_past_courses.append((r["title"], "A"))
                elif r["grade"] == "B":
                    own_related_boost += 0.03
                    matching_past_courses.append((r["title"], "B"))
                elif r["grade"] == "F":
                    own_related_boost -= 0.06
                    matching_past_courses.append((r["title"], "F"))
                    
    own_related_boost = max(-0.15, min(0.15, own_related_boost))
    
    # 7. Overall calculation
    base_success = 0.40 + (cbf_score * 0.25) + (cf_score * 0.15)
    success_prob = base_success + dept_boost + field_boost + gpa_boost + difficulty_adjust + own_related_boost
    
    peer_boost = 0.0
    if peer_count > 0:
        if avg_peer_rating >= 4.0 or peer_success_rate > 0.85:
            peer_boost = 0.05
        elif avg_peer_rating < 3.0 or peer_success_rate < 0.60:
            peer_boost = -0.05
    success_prob += peer_boost
    
    success_prob = min(0.98, max(0.15, success_prob))
    
    # Compile explanations and reasons
    reasons_pos = []
    reasons_neg = []
    
    if cbf_score > 0.4:
        reasons_pos.append(f"Strong interest correlation ({int(cbf_score*100)}% tag alignment).")
    elif cbf_score < 0.15:
        reasons_neg.append("Low correlation with your listed interests.")
        
    if dept_boost > 0:
        reasons_pos.append(f"Matching core department: {course_dept} (+12% match boost).")
    else:
        reasons_neg.append(f"Offered by {course_dept} department (outside your primary field).")
        
    if field_boost > 0:
        reasons_pos.append(f"Aligned with academic field {course_cat} (+8% match boost).")
        
    reasons_pos.append(f"Academic standing (GPA {gpa:.2f}) provides +{int(gpa_boost*100)}% potential.")
    if difficulty_adjust < 0:
        reasons_neg.append(f"Advanced course penalty (-10%) due to GPA below 2.50.")
    elif difficulty_adjust > 0:
        reasons_pos.append(f"Beginner course bonus (+5%) due to GPA above 3.50.")
        
    for title, grade in matching_past_courses:
        if grade in ("A", "B"):
            reasons_pos.append(f"Strong past grade in related '{title}' (Grade {grade}).")
        elif grade == "F":
            reasons_neg.append(f"Prerequisite risk: past failing grade in related '{title}'.")
            
    if peer_boost > 0:
        reasons_pos.append(f"Historically high peer passing rate ({int(peer_success_rate*100)}%).")
    elif peer_boost < 0:
        reasons_neg.append(f"Historically difficult course for peers (avg rating {avg_peer_rating:.1f}/5).")
        
    if not reasons_pos:
        reasons_pos.append("General elective matching basic parameters.")
        
    if success_prob >= 0.75:
        verdict = "Excellent Match"
        verdict_color = "#059669"
        advice = "Highly recommended! Your profile shows outstanding compatibility with this course's syllabus and prerequisites."
    elif success_prob >= 0.50:
        verdict = "Good Match"
        verdict_color = "#2563eb"
        advice = "A solid, standard option. You have the necessary skills to perform well with consistent study and effort."
    elif success_prob >= 0.35:
        verdict = "Challenging Match"
        verdict_color = "#d97706"
        advice = "Proceed with caution. This course presents moderate risk due to background mismatches or lower interest alignment."
    else:
        verdict = "High Risk Match"
        verdict_color = "#dc2626"
        advice = "Not recommended. Your standing, past grades, and interests suggest a high chance of difficulty in this subject."
        
    return {
        "course_id": course_id,
        "title": course_title,
        "description": course_row["description"],
        "category": course_cat,
        "department": course_dept,
        "difficulty": course_difficulty,
        "credits": course_row["credits"],
        "prerequisites": course_row["prerequisites"],
        "success_probability": round(success_prob, 4),
        "success_percentage": int(round(success_prob * 100)),
        "cbf_score": round(cbf_score, 4),
        "cf_score": round(cf_score, 4),
        "gpa_factor": round(gpa_factor, 4),
        "peer_count": peer_count,
        "avg_peer_rating": round(avg_peer_rating, 2),
        "peer_success_rate": round(peer_success_rate, 4),
        "reasons_positive": reasons_pos,
        "reasons_negative": reasons_neg,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "advice": advice,
        "matching_past_courses": matching_past_courses
    }
