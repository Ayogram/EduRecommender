"""
Matrix Factorization Engine.
Implements Funk SVD via Stochastic Gradient Descent (SGD)
to learn latent factors for students and courses.
"""

import numpy as np
import random
from models.database import get_db

def get_matrix_factorization_scores(user_id, latent_factors=5, lr=0.05, reg=0.02, epochs=50):
    """
    Stochastic Gradient Descent (SGD) Matrix Factorization (Funk SVD)
    to learn latent features for students and courses and predict affinity.
    """
    db = get_db()
    
    # 1. Gather all student-course interactions (implicit/explicit ratings)
    rows = db.execute(
        "SELECT user_id, course_id, rating, completed FROM student_courses"
    ).fetchall()
    
    if not rows:
        return {}
        
    all_users = sorted(list(set(r["user_id"] for r in rows)))
    all_courses = sorted(list(set(r["course_id"] for r in rows)))
    
    # If the current user has no history, return empty (handled by content-based)
    if user_id not in all_users:
        return {}
        
    u_map = {uid: i for i, uid in enumerate(all_users)}
    c_map = {cid: j for j, cid in enumerate(all_courses)}
    
    # 2. Extract observed ratings for training (explicit ratings or implicit enrollments)
    ratings = []
    for r in rows:
        rating = r["rating"]
        # If rating is 0 (implicit feedback - enrolled but not rated), assign default score
        if not rating or rating == 0:
            rating = 3.0
            if r["completed"] == 1:
                rating = 4.0
        ratings.append((u_map[r["user_id"]], c_map[r["course_id"]], float(rating)))
        
    num_users = len(all_users)
    num_items = len(all_courses)
    
    # Initialize biases and latent matrices
    global_mean = np.mean([r[2] for r in ratings]) if ratings else 3.0
    user_biases = np.zeros(num_users)
    item_biases = np.zeros(num_items)
    
    # Initialize user and item latent matrices with random small values
    np.random.seed(42)
    P = np.random.normal(0, 0.1, (num_users, latent_factors))
    Q = np.random.normal(0, 0.1, (num_items, latent_factors))
    
    # 3. Train Funk SVD model via SGD
    for epoch in range(epochs):
        # Shuffle ratings for random gradient updates
        random.shuffle(ratings)
        for u, i, r_val in ratings:
            prediction = global_mean + user_biases[u] + item_biases[i] + np.dot(P[u], Q[i])
            err = r_val - prediction
            
            # Update biases
            user_biases[u] += lr * (err - reg * user_biases[u])
            item_biases[i] += lr * (err - reg * item_biases[i])
            
            # Update latent matrices
            P_u_old = P[u].copy()
            P[u] += lr * (err * Q[i] - reg * P[u])
            Q[i] += lr * (err * P_u_old - reg * Q[i])
            
    # 4. Predict affinity scores for courses the target user has NOT interacted with
    target_u_idx = u_map[user_id]
    
    # Get courses the user has already interacted with
    enrolled_courses = set(r["course_id"] for r in rows if r["user_id"] == user_id)
    
    scores = {}
    for cid in all_courses:
        if cid in enrolled_courses:
            continue
            
        i_idx = c_map[cid]
        pred_rating = global_mean + user_biases[target_u_idx] + item_biases[i_idx] + np.dot(P[target_u_idx], Q[i_idx])
        # Normalize score to 0.0 - 1.0 range
        scores[cid] = float(np.clip(pred_rating / 5.0, 0.0, 1.0))
        
    return scores
