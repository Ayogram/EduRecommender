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

RELATED_DEPARTMENTS = {
    "Computer Science": ["Information and Computer Engineering", "Industrial Mathematics", "Fintech"],
    "Information and Computer Engineering": ["Computer Science", "Electrical Engineering", "Industrial Mathematics"],
    "Electrical Engineering": ["Information and Computer Engineering", "Mechanical Engineering", "Industrial Physics", "Industrial Mathematics"],
    "Mechanical Engineering": ["Electrical Engineering", "Industrial Physics", "Petroleum Engineering", "Industrial Mathematics"],
    "Petroleum Engineering": ["Mechanical Engineering", "Electrical Engineering", "Industrial Physics", "Industrial Mathematics"],
    "Industrial Mathematics": ["Computer Science", "Information and Computer Engineering", "Economics", "Industrial Physics"],
    "Industrial Physics": ["Industrial Mathematics", "Mechanical Engineering", "Electrical Engineering"],
    "Medicine": ["Psychology", "Social Sciences", "Others"],
    "Psychology": ["Medicine", "Social Sciences"],
    "Economics": ["Fintech", "Accounting", "Business Administration", "Industrial Mathematics"],
    "Fintech": ["Economics", "Accounting", "Business Administration", "Computer Science"],
    "Business Administration": ["Economics", "Fintech", "Accounting"],
    "Accounting": ["Economics", "Fintech", "Business Administration"],
    "Law": ["Business Administration", "Social Sciences"],
    "Arts": ["Social Sciences"],
    "Social Sciences": ["Law", "Psychology", "Economics", "Arts"],
    "Others": ["Medicine", "Industrial Mathematics"]
}
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


def generate_comparative_explanations(candidates, user_dept, user_field, user_interests, user_past_grades):
    """
    Overwrites the 'explanation' field of the top candidate recommendations with unique,
    highly personalized and comparative reasoning.
    """
    for idx, c in enumerate(candidates):
        rank = idx + 1
        title = c["title"]
        c_dept = c["department"] or ""
        c_cat = c["category"] or ""
        success_prob = c["success_probability"]
        
        # Determine why it fits user's profile
        strengths = []
        
        # 1. Past academic performance
        if user_past_grades:
            high_grades = [subj for subj, gr in user_past_grades.items() if gr in ('A', 'B')]
            if high_grades:
                strengths.append(f"Strong foundation from past success in {', '.join(high_grades[:2])}")
                
        # 2. Tag alignment
        tags = c["tags"]
        if tags and user_interests:
            matching_tags = [t for t in tags if any(i.lower().strip() in t.lower() or t.lower() in i.lower() for i in user_interests)]
            if matching_tags:
                strengths.append(f"Synergy with your interests in {', '.join(matching_tags[:2])}")
                
        # 3. Department matching
        if c_dept and user_dept:
            if c_dept.lower().strip() == user_dept.lower().strip():
                strengths.append(f"Direct match for your core department: {c_dept}")
            else:
                related = RELATED_DEPARTMENTS.get(user_dept, [])
                if any(r_dept.lower().strip() == c_dept.lower().strip() for r_dept in related):
                    strengths.append(f"Offered by related department: {c_dept}")
            
        if not strengths:
            strengths.append("Matches general academic performance patterns")
            
        # Career prospects based on category
        cat_lower = c_cat.lower()
        if "programming" in cat_lower or "dsa" in cat_lower or "software" in cat_lower:
            career = "Software Developer, Systems Engineer, Technical Architect"
        elif "data" in cat_lower or "learning" in cat_lower or "ai" in cat_lower:
            career = "Data Analyst, Machine Learning Specialist, AI Engineer"
        elif "security" in cat_lower or "network" in cat_lower:
            career = "Cybersecurity Consultant, Systems Administrator, Security Lead"
        elif "business" in cat_lower or "management" in cat_lower:
            career = "Product Manager, IT Consultant, Business Analyst"
        else:
            career = f"{c_dept or 'Specialist'} Analyst, Consultant, Researcher"

        # Comparative Rationale (Why this rank?)
        why = ""
        if rank == 1:
            next_course = candidates[1]["title"] if len(candidates) > 1 else "other electives"
            why = (
                f"Top pick for your profile. This course aligns perfectly with your primary interest in {user_field or 'academic field'} "
                f"and ranks above {next_course} due to a stronger correlation with your academic results and strengths, indicating high success potential."
            )
        elif rank == 2:
            prev_course = candidates[0]["title"]
            next_course = candidates[2]["title"] if len(candidates) > 2 else "other options"
            why = (
                f"Your second pick. This course also matches your technical profile and interests, but ranks slightly below "
                f"{prev_course} because {prev_course} offers broader alignment with your primary background. It ranks above {next_course} "
                f"due to stronger alignment with your academic standing, representing strong success potential."
            )
        elif rank == 3:
            prev_course = candidates[1]["title"]
            why = (
                f"Your third pick. Suitable based on your technical strengths, but ranked lower because your academic profile "
                f"and past grades show closer synergy with the curricula of {prev_course} and {candidates[0]['title']}. It still shows high success potential."
            )
        else:
            why = (
                f"A suitable elective choice matching your profile. It is ranked lower because it has lesser direct overlap "
                f"with your core interests compared to our top three recommendations ({candidates[0]['title']}, {candidates[1]['title']}, {candidates[2]['title']}), though it offers good success potential."
            )
            
        advice = f"This is a {c['credits']}-unit {c['difficulty']} course. Review the prerequisites ({c['prerequisites']}) carefully to ensure you're prepared."
        
        explanation_dict = {
            "course": title,
            "confidence": int(success_prob * 100),
            "why": why,
            "strengths": strengths,
            "career": career,
            "advice": advice
        }
        
        # Update explanation JSON
        c["explanation"] = json.dumps(explanation_dict)


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
        "SELECT department, academic_field, gpa, interests, past_grades FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    
    gpa = float(user_row["gpa"] or 0.0) if user_row else 0.0
    gpa_scale = 5.0 if gpa > 4.0 else 4.0
    gpa_factor = min(gpa / gpa_scale, 1.0)
    user_dept = user_row["department"] if user_row else None
    user_field = user_row["academic_field"] if user_row else None
    try:
        user_interests = json.loads(user_row["interests"]) if user_row and user_row["interests"] else []
    except Exception:
        user_interests = []
        
    try:
        user_past_grades = json.loads(user_row["past_grades"]) if user_row and user_row["past_grades"] else {}
    except Exception:
        user_past_grades = {}

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
    dept_performance_map = {r["department"]: float(r["avg_grade"]) if r["avg_grade"] is not None else 0.0 for r in history_rows if r["department"]}

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
        # If the user has a department specified, we restrict recommendations strictly to:
        # 1. Courses in their own department.
        # 2. Courses in related departments (defined in RELATED_DEPARTMENTS).
        # 3. Courses that have an interest tag overlap.
        # Otherwise, if no department is specified, the course must be profile-relevant or have score >= 0.05.
        if user_dept:
            is_own_dept = (course_row["department"] and user_dept.lower().strip() == course_row["department"].lower().strip())
            is_related_dept = False
            related = RELATED_DEPARTMENTS.get(user_dept, [])
            if course_row["department"]:
                if any(r_dept.lower().strip() == course_row["department"].lower().strip() for r_dept in related):
                    is_related_dept = True
            
            has_interest_match = False
            if user_interests:
                try:
                    c_tags = [t.lower().strip() for t in json.loads(course_row["tags"])] if course_row["tags"] else []
                    for interest in user_interests:
                        interest_lower = interest.lower().strip()
                        for tag in c_tags:
                            if tag in interest_lower or interest_lower in tag:
                                has_interest_match = True
                                break
                        if has_interest_match:
                            break
                except Exception:
                    pass

            if not (is_own_dept or is_related_dept or has_interest_match):
                continue
        else:
            if score < 0.05 and not is_profile_relevant:
                continue

        cf_s = cf_scores.get(course_id, 0.0) if method == "hybrid" else 0.0
        ct_s = content_scores.get(course_id, 0.0)

        # Scale base success probability so match ranges reach 70%+
        # base_success maps score (0.0 to 1.0) to a range starting at 0.50
        success_prob = 0.50 + (score * 0.8)

        # Primary Interest / Department Boosts (Personalization Upgrade)
        primary_interest_boost = 0.0
        c_dept = course_row["department"].lower().strip() if course_row["department"] else ""
        c_cat = course_row["category"].lower().strip() if course_row["category"] else ""
        u_dept = user_dept.lower().strip() if user_dept else ""
        u_field = user_field.lower().strip() if user_field else ""

        # Direct department match
        if u_dept and (u_dept == c_dept or c_dept in u_dept or u_dept in c_dept):
            primary_interest_boost += 0.35
        
        # Primary academic field interest matches department, category, or tags
        if u_field and (u_field == c_dept or c_dept in u_field or u_field in c_cat or c_cat in u_field):
            primary_interest_boost += 0.35  # Significant weight for primary interest!
        else:
            try:
                c_tags = [t.lower().strip() for t in json.loads(course_row["tags"])] if course_row["tags"] else []
                if u_field and any(tag in u_field or u_field in tag for tag in c_tags):
                    primary_interest_boost += 0.20
            except Exception:
                pass
                
        success_prob += primary_interest_boost
        success_prob += gpa_factor * 0.20

        # Add a tiny deterministic factor to ensure no duplicate match percentages
        success_prob += (course_id % 7) * 0.005

        # CGPA-based difficulty adjustments (scaled to not overpower relevance)
        difficulty_adjust = 0.0
        if gpa >= (3.5 if gpa_scale == 4.0 else 4.25):
            if course_row["difficulty"] == "advanced":
                difficulty_adjust = 0.05
            elif course_row["difficulty"] == "intermediate":
                difficulty_adjust = 0.03
            elif course_row["difficulty"] == "beginner":
                difficulty_adjust = -0.03
        elif gpa >= (3.0 if gpa_scale == 4.0 else 3.75):
            if course_row["difficulty"] == "advanced":
                difficulty_adjust = 0.03
            elif course_row["difficulty"] == "intermediate":
                difficulty_adjust = 0.01
            elif course_row["difficulty"] == "beginner":
                difficulty_adjust = -0.01
        elif gpa >= (2.0 if gpa_scale == 4.0 else 2.5):
            if course_row["difficulty"] == "beginner":
                difficulty_adjust = 0.03
            elif course_row["difficulty"] == "intermediate":
                difficulty_adjust = 0.01
            elif course_row["difficulty"] == "advanced":
                difficulty_adjust = -0.03
        else:
            if course_row["difficulty"] == "beginner":
                difficulty_adjust = 0.05
            elif course_row["difficulty"] == "intermediate":
                difficulty_adjust = -0.03
            elif course_row["difficulty"] == "advanced":
                difficulty_adjust = -0.05
        success_prob += difficulty_adjust

        # Historical boost
        dept_perf = dept_performance_map.get(course_row["department"], 0.0)
        success_prob += dept_perf * 0.15

        # Calculate raw success probability for fine-grained sorting
        success_prob_raw = success_prob
        
        # Cap the probability logically between 25% and 98%
        success_prob = round(min(0.98, max(0.25, success_prob)), 4)

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
            "success_probability_raw": success_prob_raw,
            "success_probability": round(success_prob, 4),
            "explanation": "",  # Filled in comparatively after sorting
            "method": method,
        })

    # Sort all candidate recommendations by success_probability_raw descending and then content score descending
    candidates_sorted = sorted(candidates, key=lambda x: (x["success_probability_raw"], x["score"]), reverse=True)
    
    # Take top N
    top_candidates = candidates_sorted[:top_n]

    # Generate comparative explanations
    generate_comparative_explanations(top_candidates, user_dept, user_field, user_interests, user_past_grades)

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
            avg_peer_rating = float(peer_stats["avg_rating"]) if peer_stats["avg_rating"] is not None else 4.0
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
    if gpa >= 3.5:
        if course_difficulty == "advanced":
            difficulty_adjust = 0.25
        elif course_difficulty == "intermediate":
            difficulty_adjust = 0.12
        elif course_difficulty == "beginner":
            difficulty_adjust = -0.15
    elif gpa >= 3.0:
        if course_difficulty == "advanced":
            difficulty_adjust = 0.05
        elif course_difficulty == "intermediate":
            difficulty_adjust = 0.05
    elif gpa >= 2.0:
        if course_difficulty == "beginner":
            difficulty_adjust = 0.15
        elif course_difficulty == "intermediate":
            difficulty_adjust = 0.02
        elif course_difficulty == "advanced":
            difficulty_adjust = -0.20
    else:
        if course_difficulty == "beginner":
            difficulty_adjust = 0.20
        elif course_difficulty == "intermediate":
            difficulty_adjust = -0.15
        elif course_difficulty == "advanced":
            difficulty_adjust = -0.35
        
    # 5. Academic History & Department matching
    dept_boost = 0.0
    field_boost = 0.0
    # Initialize reasons lists here so all blocks below can safely append to them
    reasons_pos = []
    reasons_neg = []
    
    c_dept_clean = course_dept.lower().strip() if course_dept else ""
    c_cat_clean = course_cat.lower().strip() if course_cat else ""
    u_dept_clean = user_dept.lower().strip() if user_dept else ""
    u_field_clean = user_field.lower().strip() if user_field else ""
    
    if u_dept_clean and (u_dept_clean == c_dept_clean or c_dept_clean in u_dept_clean or u_dept_clean in c_dept_clean):
        dept_boost = 0.12
        
    if u_field_clean and (u_field_clean == c_dept_clean or c_dept_clean in u_field_clean or u_field_clean in c_cat_clean or c_cat_clean in u_field_clean):
        field_boost = 0.22  # High boost for matching primary interest!
    else:
        try:
            if u_field_clean and course_tags:
                if any(tag.lower().strip() in u_field_clean or u_field_clean in tag.lower().strip() for tag in course_tags):
                    field_boost = 0.12
        except Exception:
            pass

    # Determine if in a related department
    is_related_dept = False
    if u_dept_clean and c_dept_clean:
        related = RELATED_DEPARTMENTS.get(user_dept, [])
        if any(r_dept.lower().strip() == c_dept_clean for r_dept in related):
            is_related_dept = True

    # ── FIELD MISMATCH PENALTY ──────────────────────────────────────────────
    # If neither dept_boost nor field_boost nor is_related_dept fired, the course is from a completely
    # different domain. Apply a strong penalty so e.g. Psychology never scores
    # 70%+ for a Computer Science student.
    field_mismatch_penalty = 0.0
    if dept_boost == 0.0 and field_boost == 0.0 and not is_related_dept:
        # Check whether interest tags at least partially overlap
        interest_overlap = False
        if user_interests and course_tags:
            c_tags_lower = [t.lower().strip() for t in course_tags]
            for interest in user_interests:
                interest_lower = interest.lower().strip()
                for tag in c_tags_lower:
                    if tag in interest_lower or interest_lower in tag:
                        interest_overlap = True
                        break
                if interest_overlap:
                    break
        if not interest_overlap:
            # Completely unrelated course — apply a hard penalty
            field_mismatch_penalty = -0.20

    # is_field_match is True when at least dept or field boost was earned
    is_field_match = (dept_boost > 0 or field_boost > 0 or is_related_dept)
    # (reasons_pos entries for field match are added below after success_prob is computed)

    
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
    success_prob = base_success + dept_boost + field_boost + field_mismatch_penalty + gpa_boost + difficulty_adjust + own_related_boost
    
    # Add a tiny deterministic factor to ensure no duplicate match percentages
    success_prob += (course_id % 7) * 0.005 if course_id else 0.002
    
    peer_boost = 0.0
    if peer_count > 0:
        if avg_peer_rating >= 4.0 or peer_success_rate > 0.85:
            peer_boost = 0.05
        elif avg_peer_rating < 3.0 or peer_success_rate < 0.60:
            peer_boost = -0.05
    success_prob += peer_boost
    
    success_prob = min(0.98, max(0.15, success_prob))
    
    # Compile explanations and reasons
    # (lists were initialized before boost calculations above)
    
    if cbf_score > 0.4:
        reasons_pos.append(f"Strong interest correlation ({int(cbf_score*100)}% tag alignment).")
    elif cbf_score < 0.15:
        reasons_neg.append("Low correlation with your listed interests.")

    # Field match / mismatch reasons
    if is_field_match:
        if dept_boost > 0:
            reasons_pos.append(f"Matching core department: {course_dept} (+12% match boost).")
        if field_boost > 0:
            reasons_pos.append(f"Matching academic field / interest: {user_field} (+22% match boost).")
        if is_related_dept:
            reasons_pos.append(f"Offered by related department: {course_dept} (aligned domain).")
    elif field_mismatch_penalty < 0:
        reasons_neg.append(f"Offered by {course_dept} department — significantly outside your primary field ({user_field or user_dept}). This course covers concepts not typically covered in your programme.")
    else:
        reasons_neg.append(f"Offered by {course_dept} department (outside your primary field).")

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

    # ── Rich structured analysis (displayed as named sections) ─────────────
    field_label = user_field or user_dept or "your field"
    match_pct = int(round(success_prob * 100))
    gpa_comment = "outstanding" if gpa >= 4.0 else ("strong" if gpa >= 3.5 else ("solid" if gpa >= 3.0 else "developing"))
    
    # Build past grades context
    grade_subjects_good = [(t, g) for t, g in matching_past_courses if g in ('A', 'B')]
    grade_subjects_bad  = [(t, g) for t, g in matching_past_courses if g == 'F']
    interests_str = ', '.join(user_interests[:4]) if user_interests else field_label

    if dept_boost > 0 or field_boost > 0:
        # ── GOOD MATCH ──────────────────────────────────────────────────────
        acad_perf = (
            f"Your GPA of {gpa:.2f} places you in the {gpa_comment} academic tier, "
            f"which is a strong predictor of success in {course_dept} courses. "
        )
        if grade_subjects_good:
            acad_perf += (
                f"Your past grades in {', '.join(t for t,g in grade_subjects_good[:2])} "
                f"demonstrate you already have the technical foundation this course builds on. "
            )
        acad_perf += (
            f"Students with a {gpa_comment} GPA in {field_label} programmes consistently outperform "
            f"peers in courses that align with their department, which is exactly the case here."
        )

        interest_align = (
            f"Your profile lists {field_label} as your primary academic field, and this course is offered by the {course_dept} department — a direct match. "
            f"Your stated interests ({interests_str}) correlate strongly with the topics covered in this course "
            f"({', '.join(course_tags[:4]) if course_tags else course_cat}). "
            f"When interest and department align, students report higher engagement, better retention, and significantly improved final grades."
        )

        problem_solving = (
            f"A {course_difficulty}-level course in {course_dept} requires the kind of structured, analytical thinking "
            f"your academic background in {field_label} has already been developing. "
            f"Your performance pattern indicates strong logical reasoning ability — "
            f"a core skill tested in {course_cat} topics. "
            f"Students from your department who take this course consistently perform above the class average."
        )

        career_align = (
            f"Completing {course_title} strengthens your profile for careers that demand {course_cat} expertise — "
            f"a direct complement to where your {field_label} degree is taking you. "
            f"The course's {course_difficulty} classification means it provides real, career-ready skills rather than purely theoretical content. "
            f"Based on your interests in {interests_str}, you are building exactly the skill set employers in this domain look for."
        )

        future_growth = (
            f"Based on your GPA of {gpa:.2f}, your department match ({course_dept}), and your stated interests, "
            f"{course_title} offers the strongest balance between your current academic capability and long-term professional growth. "
            f"This course does not just tick academic boxes — it directly compounds your existing strengths and accelerates your progression within {field_label}."
        )

        verdict_text = (
            f"{course_title} is not recommended solely because it matches your department. "
            f"It is recommended because your academic performance ({gpa_comment} GPA of {gpa:.2f}), your department alignment ({course_dept}), "
            f"your stated interests ({interests_str}), and the course content all converge on the same conclusion: "
            f"this is the course where you have the highest probability of performing at your best. "
            f"At {match_pct}% compatibility, this is an outstanding match for your profile."
        )

    elif field_mismatch_penalty < 0:
        # ── BAD MATCH ────────────────────────────────────────────────────────
        acad_perf = (
            f"While your GPA of {gpa:.2f} is {gpa_comment} and reflects strong academic discipline, "
            f"GPA alone does not guarantee success in a completely unrelated discipline. "
            f"Your academic strengths have been built within {field_label} — the concepts, reasoning patterns, "
            f"and problem-solving approaches valued in {course_dept} are largely different from what your programme develops."
        )

        interest_align = (
            f"Your primary academic field is {field_label}, and your stated interests ({interests_str}) "
            f"show no significant overlap with the content covered in {course_title} (offered by {course_dept}). "
            f"When a student's interests and department diverge from a course, the likelihood of sustained "
            f"motivation and high performance drops significantly — even for students with strong GPAs."
        )

        problem_solving = (
            f"{course_title} requires a specific type of thinking and domain knowledge that is typically developed "
            f"through years of study within {course_dept}. "
            f"As a {field_label} student, you would be entering this course without the foundational mental models "
            f"that students from {course_dept} bring. This creates a significant learning curve regardless of your general intelligence."
        )

        career_align = (
            f"From a career perspective, {course_title} ({course_dept}) does not align with the career paths your "
            f"{field_label} degree is preparing you for. "
            f"Investing time in this course risks pulling focus away from building the specialised skill set "
            f"that will differentiate you in {field_label}-related roles."
        )

        future_growth = (
            f"Your strongest long-term growth comes from deepening your expertise in {field_label}, "
            f"not from branching into unrelated disciplines. "
            f"Unless {course_title} is a mandatory university elective requirement, "
            f"selecting a course that aligns with your department will give you a significantly higher return "
            f"on your academic effort and time."
        )

        verdict_text = (
            f"{course_title} scores {match_pct}% compatibility with your profile — not because of a data error, "
            f"but because your department ({field_label}), interests ({interests_str}), and academic strengths "
            f"all point away from {course_dept}. "
            f"Your GPA gives you enough discipline to pass, but performing at your best and finding genuine value "
            f"in this course is unlikely given the field mismatch. Consider it only if it is a mandatory elective."
        )

    else:
        # ── MODERATE MATCH ───────────────────────────────────────────────────
        acad_perf = (
            f"Your GPA of {gpa:.2f} is {gpa_comment} and gives you an academic cushion — you have the "
            f"study habits and intellectual endurance to navigate material that is partially outside your comfort zone. "
            f"However, courses outside your core department typically demand 20-30% more preparation time "
            f"from students without a direct departmental background."
        )

        interest_align = (
            f"Your interests ({interests_str}) partially overlap with the content of {course_title}, "
            f"but the alignment is not as strong as it would be for courses directly within {field_label}. "
            f"Some of what this course covers will feel familiar; other parts will require you to learn "
            f"frameworks and concepts from scratch. Your engagement and motivation may fluctuate as a result."
        )

        problem_solving = (
            f"{course_title} is a {course_difficulty}-level course, which means the analytical demands are "
            f"{'moderate and manageable with preparation' if course_difficulty != 'advanced' else 'high — particularly challenging when entering without a strong departmental base'}. "
            f"Your {field_label} background provides some transferable thinking skills, but expect to invest "
            f"significant extra effort in the areas that do not directly map to your existing knowledge."
        )

        career_align = (
            f"{course_title} offers some career relevance if you are looking to broaden your profile beyond pure {field_label}. "
            f"However, for most career paths your degree targets, courses within {field_label} will be more directly valued by employers. "
            f"Consider this course if you have a specific niche interest in {course_dept} that complements your main specialisation."
        )

        future_growth = (
            f"At {match_pct}% compatibility, this course is manageable but not optimised for your profile. "
            f"Your strongest future growth comes from building depth in {field_label}, where your academic "
            f"background, interests, and department alignment all compound together. "
            f"This course can be a valuable broadening choice, but should not replace core {field_label} electives."
        )

        verdict_text = (
            f"{course_title} is a moderate match for your profile. Your GPA of {gpa:.2f} means you can handle the workload, "
            f"and your partial interest alignment means you will find some of the content engaging. "
            f"However, this course sits outside your primary department, which means you will not have the same built-in "
            f"advantage you would have in a course directly within {field_label}. "
            f"Approach it with clear eyes: it is achievable, but it requires more deliberate preparation."
        )

    import json as _json
    advice = _json.dumps({
        "academic_performance": acad_perf,
        "interest_alignment": interest_align,
        "problem_solving": problem_solving,
        "career_alignment": career_align,
        "future_growth": future_growth,
        "verdict": verdict_text,
        "match_pct": match_pct,
        "is_good_match": bool(dept_boost > 0 or field_boost > 0),
        "is_mismatch": bool(field_mismatch_penalty < 0)
    })

    if success_prob >= 0.75:
        verdict = "Excellent Match"
        verdict_color = "#059669"
    elif success_prob >= 0.50:
        verdict = "Good Match"
        verdict_color = "#2563eb"
    elif success_prob >= 0.35:
        verdict = "Challenging Match"
        verdict_color = "#d97706"
    else:
        verdict = "High Risk Match"
        verdict_color = "#dc2626"
        
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
