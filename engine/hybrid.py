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


CF_WEIGHT = 0.6
CONTENT_WEIGHT = 0.4
COLD_START_THRESHOLD = 3  # min ratings before hybrid kicks in


def _generate_explanation(user_id, course, method, cf_score, content_score):
    """Build a human-readable explanation string."""
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
    if method == "hybrid":
        parts.append("This course is recommended using our hybrid AI model.")
    elif method == "content":
        parts.append("This course is recommended based on your interests and profile.")
    else:
        parts.append("This course is recommended based on similar students' preferences.")

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
    Returns list of dicts with course info, score, and explanation.
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
    else:
        method = "hybrid"
        content_scores = get_content_scores(user_id)
        cf_scores = get_collaborative_scores(user_id)

        # Merge scores
        all_courses = set(content_scores.keys()) | set(cf_scores.keys())
        combined = {}
        for cid in all_courses:
            cs = content_scores.get(cid, 0.0)
            cfs = cf_scores.get(cid, 0.0)
            # If CF is unavailable (no similar users), rely more on content
            if not cf_scores:
                combined[cid] = cs
            else:
                combined[cid] = CF_WEIGHT * cfs + CONTENT_WEIGHT * cs

    # Sort by score descending
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Clear old recommendations
    Recommendation.clear_for_user(user_id)

    results = []
    for course_id, score in ranked:
        course_row = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        if not course_row:
            continue

        cf_s = cf_scores.get(course_id, 0.0) if method == "hybrid" else 0.0
        ct_s = content_scores.get(course_id, 0.0)

        explanation = _generate_explanation(user_id, course_row, method, cf_s, ct_s)

        # Persist
        Recommendation.save(user_id, course_id, round(score, 4), explanation, method)

        results.append({
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
            "explanation": explanation,
            "method": method,
        })

    return results


# ── Evaluation Metrics ──────────────────────────────────────────────────────

def evaluate(user_id, k=10):
    """
    Compute Precision@k, Recall@k, and F1@k.
    Relevant = courses the user rated >= 3.5 that were NOT in the training set.
    """
    db = get_db()

    # All courses user rated highly
    relevant = set(
        r["course_id"]
        for r in db.execute(
            "SELECT course_id FROM student_courses WHERE user_id = ? AND rating >= 3.5",
            (user_id,),
        ).fetchall()
    )

    # Recommended course IDs
    recs = db.execute(
        "SELECT course_id FROM recommendations WHERE user_id = ? ORDER BY score DESC LIMIT ?",
        (user_id, k),
    ).fetchall()
    recommended = set(r["course_id"] for r in recs)

    if not recommended:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    hits = relevant & recommended
    precision = len(hits) / len(recommended) if recommended else 0.0
    recall = len(hits) / len(relevant) if relevant else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
