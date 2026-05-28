"""
Content-Based Filtering engine.
Uses TF-IDF on course descriptions + tags and cosine similarity
to match courses to a user's interest profile.
"""

import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.database import get_db


def _build_corpus():
    """Return (course_ids, corpus) where each corpus entry is
    title + description + category + tags concatenated."""
    db = get_db()
    rows = db.execute("SELECT id, title, description, category, department, tags FROM courses").fetchall()
    ids = []
    texts = []
    for r in rows:
        tags = " ".join(json.loads(r["tags"])) if r["tags"] else ""
        # Include department and category in the text blob
        dept = r['department'] if r['department'] else ""
        text = f"{r['title']} {r['description']} {r['category']} {dept} {tags}"
        ids.append(r["id"])
        texts.append(text)
    return ids, texts


def _user_profile_text(user_id):
    """Build a pseudo-document from the user's interests and highly-rated courses."""
    db = get_db()

    # Interests, Academic Field, and Department
    user = db.execute("SELECT interests, academic_field, department FROM users WHERE id = ?", (user_id,)).fetchone()
    interests = json.loads(user["interests"]) if user and user["interests"] else []
    academic_field = user["academic_field"] if user and user["academic_field"] else ""
    department = user["department"] if user and user["department"] else ""

    # Highly rated courses
    rows = db.execute(
        """SELECT c.title, c.description, c.category, c.tags, sc.grade
           FROM student_courses sc JOIN courses c ON sc.course_id = c.id
           WHERE sc.user_id = ? AND (sc.rating >= 3.0 OR sc.grade IN ('A', 'B'))
           ORDER BY sc.enrolled_at DESC LIMIT 15""",
        (user_id,),
    ).fetchall()

    parts = list(interests)
    # Give academic field and department triple weight in the profile text
    if academic_field:
        parts.extend([academic_field] * 3)
    if department:
        parts.extend([department] * 3)
    for r in rows:
        tags = " ".join(json.loads(r["tags"])) if r["tags"] else ""
        text = f"{r['title']} {r['description']} {r['category']} {tags}"
        # Condition 1: Performance Match (Heavily weight 'A' grades)
        weight = 3 if r["grade"] == "A" else (2 if r["grade"] == "B" else 1)
        parts.extend([text] * weight)

    return " ".join(parts) if parts else ""


def get_content_scores(user_id):
    """Return dict  {course_id: score}  where score is 0-1 cosine similarity."""
    course_ids, corpus = _build_corpus()
    if not corpus:
        return {}

    profile = _user_profile_text(user_id)
    if not profile:
        return {}

    # Fit TF-IDF on corpus + profile (last entry)
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus + [profile])

    profile_vec = tfidf_matrix[-1]
    course_vecs = tfidf_matrix[:-1]

    similarities = cosine_similarity(profile_vec, course_vecs).flatten()

    # Exclude courses the user already enrolled in
    db = get_db()
    enrolled = set(
        r["course_id"]
        for r in db.execute(
            "SELECT course_id FROM student_courses WHERE user_id = ?", (user_id,)
        ).fetchall()
    )

    scores = {}
    for cid, sim in zip(course_ids, similarities):
        if cid not in enrolled:
            scores[cid] = float(sim)

    return scores
