import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "edurecommender.db")

if os.path.exists(DB_PATH):
    print(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys so ON DELETE CASCADE deletes children
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    print("Clearing course_modules (will cascade delete lessons, exams, and exam results)...")
    cursor.execute("DELETE FROM course_modules;")
    
    print("Clearing recommendations...")
    cursor.execute("DELETE FROM recommendations;")
    
    conn.commit()
    conn.close()
    print("Classroom cache cleared successfully!")
else:
    print(f"Database not found at: {DB_PATH}")
