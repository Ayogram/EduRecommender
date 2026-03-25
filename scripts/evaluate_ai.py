import sys
import os
import json
import sqlite3

# Add project root to sys.path
project_root = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)"
sys.path.append(project_root)

from flask import Flask
from models.database import init_db, get_db
from engine.hybrid import get_recommendations, evaluate
from models.user import User

# Mock Flask App for DB Context
app = Flask(__name__)
app.config["DATABASE_PATH"] = os.path.join(project_root, "database", "edurecommender.db")

def run_evaluation():
    with app.app_context():
        db = get_db()
        
        # 1. Setup Test Case: Computer Science Student
        print("--- SCENARIO 1: Computer Science Student ---")
        # Ensure we have a test user
        user = User.get_by_email("test_ai_cs@example.com")
        if not user:
            user = User.create(
                name="AI Tester (CS)",
                email="test_ai_cs@example.com",
                academic_field="Computer Science",
                interests=["Python", "Web Development"],
                is_verified=1
            )
            # Update department and GPA
            db.execute("UPDATE users SET department = 'Computer Science', gpa = 3.5 WHERE id = ?", (user.id,))
            db.commit()
            user = User.get_by_id(user.id)

        # Generate recommendations
        recs = get_recommendations(user.id, top_n=5)
        print(f"Top 5 Recommendations for {user.name}:")
        for r in recs:
            print(f" - [{r['score']*100:.0f}%] {r['title']} ({r['category']})")

        # Basic Check: How many are actually CS or Programming?
        matches = [r for r in recs if "Computer Science" in r['explanation'] or r['category'] in ["Programming", "Software Engineering", "Web Development"]]
        print(f"Relevancy Count: {len(matches)}/5")
        
        # 2. Setup Test Case: Law Student
        print("\n--- SCENARIO 2: Law Student ---")
        user_law = User.get_by_email("test_ai_law@example.com")
        if not user_law:
            user_law = User.create(
                name="AI Tester (Law)",
                email="test_ai_law@example.com",
                academic_field="Law",
                interests=["Justice", "Human Rights"],
                is_verified=1
            )
            db.execute("UPDATE users SET department = 'Law', gpa = 3.8 WHERE id = ?", (user_law.id,))
            db.commit()
            user_law = User.get_by_id(user_law.id)

        recs_law = get_recommendations(user_law.id, top_n=5)
        print(f"Top 5 Recommendations for {user_law.name}:")
        for r in recs_law:
            print(f" - [{r['score']*100:.0f}%] {r['title']} ({r['category']})")

        matches_law = [r for r in recs_law if "Law" in r['explanation'] or r['category'] in ["Criminal Law", "Corporate Law", "Human Rights"]]
        print(f"Relevancy Count: {len(matches_law)}/5")

        print("\n--- PERFORMANCE SUMMARY ---")
        precision_cs = len(matches) / 5
        precision_law = len(matches_law) / 5
        print(f"CS Avg Precision@5: {precision_cs:.2f}")
        print(f"Law Avg Precision@5: {precision_law:.2f}")
        print(f"Overall AI Accuracy: {(precision_cs + precision_law) / 2 * 100:.1f}%")

if __name__ == "__main__":
    run_evaluation()
