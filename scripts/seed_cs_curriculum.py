import sys
import os
import json

# Add project root to sys.path
project_root = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)"
sys.path.append(project_root)

from app import create_app
from models.database import get_db

app = create_app()

def seed_cs():
    with app.app_context():
        db = get_db()
        
        # Comprehensive CS Curriculum
        courses = [
            # 100 Level
            ("CSC 111", "Introduction to Computing", "History, hardware, software, and basic logic.", "Computer Science", 3, "None", ["Basics", "Intro"], "beginner"),
            ("CSC 121", "Programming in Python", "Introductory programming concepts using Python.", "Computer Science", 4, "None", ["Python", "Programming"], "beginner"),
            ("MAT 111", "Algebra and Trigonometry", "Fundamental math for scientists.", "Others", 3, "None", ["Math", "Algebra"], "beginner"),
            
            # 200 Level
            ("CSC 211", "Data Structures", "Arrays, Linked Lists, Stacks, Queues, and Trees.", "Computer Science", 4, "CSC 121", ["Data Structures", "Algorithms"], "intermediate"),
            ("CSC 212", "Object Oriented Programming", "Classes, inheritance, and polymorphism in Java.", "Computer Science", 4, "CSC 121", ["Java", "OOP"], "intermediate"),
            ("CSC 221", "Computer Architecture", "Digital logic, CPU design, and assembly language.", "Computer Science", 3, "CSC 111", ["Hardware", "Digital Logic"], "intermediate"),
            ("CSC 222", "Discrete Mathematics", "Sets, graphs, and combinatorics for CS.", "Others", 3, "MAT 111", ["Math", "Discrete"], "intermediate"),
            
            # 300 Level
            ("CSC 311", "Operating Systems", "Kernels, processes, memory management, and file systems.", "Computer Science", 4, "CSC 211, CSC 221", ["OS", "Systems"], "intermediate"),
            ("CSC 312", "Database Management Systems", "Relational algebra, SQL, and database design.", "Computer Science", 4, "CSC 211", ["SQL", "Databases"], "intermediate"),
            ("CSC 313", "Software Engineering I", "SDLC, requirements, and system design.", "Computer Science", 3, "CSC 212", ["SE", "Design"], "intermediate"),
            ("CSC 321", "Algorithm Design & Analysis", "Big O notation, sorting, and dynamic programming.", "Computer Science", 3, "CSC 211", ["Algorithms", "Logic"], "intermediate"),
            ("CSC 322", "Theory of Computation", "Automata, formal languages, and computability.", "Computer Science", 3, "CSC 222", ["Theory", "Automata"], "intermediate"),
            ("CSC 323", "Computer Networks", "OSI model, TCP/IP, and network security.", "Computer Science", 3, "CSC 311", ["Networking", "TCP/IP"], "intermediate"),
            
            # 400 Level
            ("CSC 411", "Artificial Intelligence", "Search algorithms, expert systems, and ML basics.", "Computer Science", 4, "CSC 321, MAT 111", ["AI", "Intelligence"], "advanced"),
            ("CSC 412", "Human Computer Interaction", "UI/UX design principles and user testing.", "Computer Science", 3, "CSC 313", ["UI", "UX"], "advanced"),
            ("CSC 413", "Compiler Construction", "Lexical analysis, parsing, and code generation.", "Computer Science", 3, "CSC 322", ["Compilers", "Languages"], "advanced"),
            ("CSC 421", "Machine Learning", "Supervised, unsupervised and deep learning.", "Computer Science", 4, "CSC 411, MAT 111", ["ML", "Data Science"], "advanced"),
            ("CSC 422", "Project Management", "Agile, Waterfall, and project tracking.", "Computer Science", 3, "CSC 313", ["Management", "PM"], "advanced"),
            ("CSC 499", "Final Year Project", "Independent research and development.", "Computer Science", 6, "All 300 Level", ["Research", "Development"], "advanced")
        ]
        
        for title, desc, details, dept, credits, prereq, tags, difficulty in courses:
            # Check if exists
            existing = db.execute("SELECT id FROM courses WHERE title = ?", (title,)).fetchone()
            if not existing:
                db.execute(
                    "INSERT INTO courses (title, description, category, department, credits, prerequisites, tags, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (title, details, dept, dept, credits, prereq, json.dumps(tags), difficulty)
                )
        
        db.commit()
        print(f"Seeded {len(courses)} curriculum courses.")

if __name__ == "__main__":
    seed_cs()
