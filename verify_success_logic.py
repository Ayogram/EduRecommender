
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from engine.hybrid import get_recommendations
from models.database import get_db
from models.recommendation import Recommendation

from app import create_app

def verify():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # Get a test user (ideally a student)
        user = db.execute("SELECT id, name, department, academic_field FROM users WHERE role = 'user' LIMIT 1").fetchone()
        if not user:
            print("No student user found in database for testing.")
            return

        print(f"Testing for User: {user['name']} (ID: {user['id']}, Dept: {user['department']})")
        
        # Generate recommendations
        recs = get_recommendations(user['id'], top_n=3)
        
        if not recs:
            print("No recommendations generated. Check if courses exist and user has interests.")
            return

        for i, rec in enumerate(recs):
            print(f"\n--- Recommendation {i+1}: {rec['title']} ---")
            print(f"Match Score: {rec['score'] * 100}%")
            print(f"Success Probability: {rec.get('success_probability', 0.0) * 100}%")
            print(f"Explanation: {rec['explanation']}")
            
            # Verify persistence
            saved = db.execute("SELECT success_probability, explanation FROM recommendations WHERE user_id = ? AND course_id = ?", 
                              (user['id'], rec['course_id'])).fetchone()
            if saved:
                print(f"Persisted Success Prob: {saved['success_probability'] * 100}%")
                if "success potential" in saved['explanation'].lower():
                    print("Explanation contains success potential mention: YES")
                else:
                    print("Explanation contains success potential mention: NO (FAILED)")
            else:
                print("FAILED: Recommendation not found in database.")

if __name__ == "__main__":
    verify()
