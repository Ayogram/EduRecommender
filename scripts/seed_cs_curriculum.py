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
            ("Introduction to Computing", "History, hardware, software, and basic logic.", "Computer Science", "Computer Science", 3, "None", ["Basics", "Intro"], "beginner"),
            ("Programming in Python", "Introductory programming concepts using Python.", "Computer Science", "Computer Science", 4, "None", ["Python", "Programming"], "beginner"),
            ("Algebra and Trigonometry", "Fundamental math for scientists.", "Others", "Others", 3, "None", ["Math", "Algebra"], "beginner"),
            
            # 200 Level
            ("Data Structures", "Arrays, Linked Lists, Stacks, Queues, and Trees.", "Computer Science", "Computer Science", 4, "Programming in Python", ["Data Structures", "Algorithms"], "intermediate"),
            ("Java Programming", "Classes, inheritance, and polymorphism in Java.", "Computer Science", "Computer Science", 4, "Programming in Python", ["Java", "OOP"], "intermediate"),
            ("Computer Architecture", "Digital logic, CPU design, and assembly language.", "Computer Science", "Computer Science", 3, "Introduction to Computing", ["Hardware", "Digital Logic"], "intermediate"),
            ("Discrete Mathematics", "Sets, graphs, and combinatorics for CS.", "Others", "Others", 3, "Algebra and Trigonometry", ["Math", "Discrete"], "intermediate"),
            
            # 300 Level
            ("Operating Systems", "Kernels, processes, memory management, and file systems.", "Computer Science", "Computer Science", 4, "Data Structures, Computer Architecture", ["OS", "Systems"], "intermediate"),
            ("Database Management Systems", "Relational algebra, SQL, and database design.", "Computer Science", "Computer Science", 4, "Data Structures", ["SQL", "Databases"], "intermediate"),
            ("Software Engineering I", "SDLC, requirements, and system design.", "Computer Science", "Computer Science", 3, "Java Programming", ["SE", "Design"], "intermediate"),
            ("Algorithm Design & Analysis", "Big O notation, sorting, and dynamic programming.", "Computer Science", "Computer Science", 3, "Data Structures", ["Algorithms", "Logic"], "intermediate"),
            ("Theory of Computation", "Automata, formal languages, and computability.", "Computer Science", "Computer Science", 3, "Discrete Mathematics", ["Theory", "Automata"], "intermediate"),
            ("Computer Networks", "OSI model, TCP/IP, and network security.", "Computer Science", "Computer Science", 3, "Operating Systems", ["Networking", "TCP/IP"], "intermediate"),
            
            # 400 Level
            ("Artificial Intelligence", "Search algorithms, expert systems, and ML basics.", "Computer Science", "Computer Science", 4, "Algorithm Design & Analysis, Algebra and Trigonometry", ["AI", "Intelligence"], "advanced"),
            ("Human Computer Interaction", "UI/UX design principles and user testing.", "Computer Science", "Computer Science", 3, "Software Engineering I", ["UI", "UX"], "advanced"),
            ("Compiler Construction", "Lexical analysis, parsing, and code generation.", "Computer Science", "Computer Science", 3, "Theory of Computation", ["Compilers", "Languages"], "advanced"),
            ("Machine Learning", "Supervised, unsupervised and deep learning.", "Computer Science", "Computer Science", 4, "Artificial Intelligence, Algebra and Trigonometry", ["ML", "Data Science"], "advanced"),
            ("Project Management", "Agile, Waterfall, and project tracking.", "Computer Science", "Computer Science", 3, "Software Engineering I", ["Management", "PM"], "advanced"),
            ("Final Year Project", "Independent research and development.", "Computer Science", "Computer Science", 6, "Operating Systems, Database Management Systems, Software Engineering I, Algorithm Design & Analysis, Theory of Computation, Computer Networks", ["Research", "Development"], "advanced")
        ]
        
        for title, desc, cat, dept, credits, prereq, tags, difficulty in courses:
            # Check if exists
            existing = db.execute("SELECT id FROM courses WHERE title = ?", (title,)).fetchone()
            if not existing:
                db.execute(
                    "INSERT INTO courses (title, description, category, department, credits, prerequisites, tags, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (title, desc, cat, dept, credits, prereq, json.dumps(tags), difficulty)
                )
        
        db.commit()
        print(f"Seeded {len(courses)} curriculum courses.")

if __name__ == "__main__":
    seed_cs()
