"""
Collaborative Filtering engine.
User-based CF using cosine similarity on the user-item rating matrix.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models.database import get_db


def _build_rating_matrix():
    """Return (user_ids, course_ids, matrix) from student_courses."""
    db = get_db()
    rows = db.execute(
        "SELECT user_id, course_id, rating FROM student_courses"
    ).fetchall()

    if not rows:
        return [], [], np.array([])

    user_ids_set = sorted(set(r["user_id"] for r in rows))
    course_ids_set = sorted(set(r["course_id"] for r in rows))

    uid_idx = {uid: i for i, uid in enumerate(user_ids_set)}
    cid_idx = {cid: i for i, cid in enumerate(course_ids_set)}

    matrix = np.zeros((len(user_ids_set), len(course_ids_set)))
    for r in rows:
        matrix[uid_idx[r["user_id"]], cid_idx[r["course_id"]]] = r["rating"]

    return user_ids_set, course_ids_set, matrix


def get_collaborative_scores(user_id):
    """Return dict  {course_id: predicted_rating_normalised}  for un-rated courses."""
    user_ids, course_ids, matrix = _build_rating_matrix()

    if matrix.size == 0 or user_id not in user_ids:
        return {}

    user_idx = user_ids.index(user_id)

    # Cosine similarity between target user and all others
    sim_matrix = cosine_similarity(matrix)
    user_sim = sim_matrix[user_idx]

    # Predict ratings for courses the user has NOT rated
    scores = {}
    for j, cid in enumerate(course_ids):
        if matrix[user_idx, j] > 0:
            continue  # already rated

        # Weighted average of other users' ratings
        numerator = 0.0
        denominator = 0.0
        for i, uid in enumerate(user_ids):
            if i == user_idx or matrix[i, j] == 0:
                continue
            numerator += user_sim[i] * matrix[i, j]
            denominator += abs(user_sim[i])

        if denominator > 0:
            predicted = numerator / denominator
            scores[cid] = float(predicted / 5.0)  # normalise to 0-1

    return scores
