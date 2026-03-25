import sys
import os
from werkzeug.security import generate_password_hash

# Add project root to sys.path
project_root = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)"
sys.path.append(project_root)

from app import create_app
app = create_app()
from models.database import get_db

def reset_creds():
    with app.app_context():
        db = get_db()
        hashed = generate_password_hash("password123")
        
        # Reset main user/admin
        db.execute("UPDATE users SET password_hash = ?, is_verified = 1, status = 'active' WHERE email = ?", 
                   (hashed, "aajumobi.2202540@stu.cu.edu.ng"))
        
        # Reset AI test users
        db.execute("UPDATE users SET password_hash = ?, is_verified = 1, status = 'active' WHERE email = ?", 
                   (hashed, "test_ai_cs@example.com"))
        db.execute("UPDATE users SET password_hash = ?, is_verified = 1, status = 'active' WHERE email = ?", 
                   (hashed, "test_ai_law@example.com"))
        
        db.commit()
        print("Credentials reset to 'password123' for test users.")

if __name__ == "__main__":
    reset_creds()
