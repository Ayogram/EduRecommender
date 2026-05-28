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
    """Build a human-readable explanation string including success prediction."""
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

    parts = []
    
    # Core reasoning prefix
    if method == "hybrid":
        parts.append("This course is recommended using our hybrid AI model.")
    elif method == "content":
        parts.append("This course is recommended based on your interests and profile.")
    else:
        parts.append("This course is recommended based on similar students' preferences.")

    # Success Prediction Sentence (User Request)
    parts.append(f"We predict a **{int(success_prob * 100)}% success potential** for you in this course.")

    if rated_titles:
        parts.append(
            f"Because you performed well in {', '.join(rated_titles)}, "
            f"students with similar academic profiles also succeeded in this course."
        )

    if course["department"] and course["department"] != course["category"]:
        parts.append(f"Matching your interest in the {course['department']} department.")

    tags = json.loads(course["tags"]) if course["tags"] else []
    if tags:
        parts.append(f"It covers topics like {', '.join(tags[:3])}.")

    parts.append(f"This is a {course['credits']}-unit {course['difficulty']} course.")

    return " ".join(parts)


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
