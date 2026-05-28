import sqlite3
import json
import os

db_path = r"c:\Users\USER\Documents\Ayo's work\My FYP(Course Recommennder System)\database\edurecommender.db"

COURSES = [
    # Computer Science
    ("Introduction to Python", "Learn the basics of programming with Python.", "Computer Science", "Programming", "beginner", "None", 3, ["python", "coding", "basics"]),
    ("Data Structures & Algorithms", "Fundamental concepts of algorithms and data organization.", "Computer Science", "Software Engineering", "intermediate", "Introduction to Python", 4, ["algorithms", "data structures", "performance"]),
    ("Artificial Intelligence", "Concepts of machine learning, neural networks, and AI.", "Computer Science", "Artificial Intelligence", "advanced", "Data Structures & Algorithms", 4, ["ai", "machine learning", "neural networks"]),
    ("Web Development Boot Camp", "Full stack development with HTML, CSS, and JS.", "Computer Science", "Web Development", "beginner", "None", 3, ["web", "html", "css", "javascript"]),
    ("Cybersecurity Fundamentals", "Protecting systems and networks from digital attacks.", "Computer Science", "Cybersecurity", "intermediate", "Introduction to Python", 3, ["security", "networking", "hacking"]),

    # Law
    ("Criminal Law 101", "Introduction to criminal justice and legal systems.", "Law", "Criminal Law", "beginner", "None", 3, ["law", "justice", "court"]),
    ("Corporate Law", "Legal aspects of business organizations and transactions.", "Law", "Corporate Law", "intermediate", "Criminal Law 101", 3, ["business", "contracts", "law"]),
    ("International Human Rights", "Evolution and enforcement of human rights globally.", "Law", "Human Rights", "advanced", "Criminal Law 101", 3, ["human rights", "un", "law"]),
    ("Intellectual Property Law", "Patents, trademarks, and copyright law.", "Law", "IP Law", "intermediate", "None", 3, ["copyright", "patents", "law"]),

    # Medicine
    ("Human Anatomy", "Detailed study of human body structures.", "Medicine", "Anatomy", "beginner", "None", 4, ["anatomy", "biology", "body"]),
    ("General Surgery", "Surgical principles and techniques.", "Medicine", "Surgery", "advanced", "Human Anatomy", 5, ["surgery", "medical", "hospital"]),
    ("Pharmacology", "Study of drugs and their actions on biological systems.", "Medicine", "Pharmacology", "intermediate", "None", 3, ["drugs", "medicine", "biology"]),
    ("Public Health Global Trends", "Exploring health challenges in the modern world.", "Medicine", "Public Health", "beginner", "None", 3, ["health", "policy", "global"]),

    # Engineering
    ("Mechanical Engineering Principles", "Statics, dynamics, and thermodynamics.", "Engineering", "Mechanical Engineering", "beginner", "None", 4, ["physics", "machines", "engineering"]),
    ("Robotics & Automation", "Design and control of robotic systems.", "Engineering", "Robotics", "advanced", "Mechanical Engineering Principles", 4, ["robotics", "ai", "hardware"]),
    ("Electrical Circuits", "AC and DC circuit analysis.", "Engineering", "Electrical Engineering", "intermediate", "None", 3, ["electricity", "circuits", "engineering"]),

    # Business
    ("Principles of Management", "Core management theories and practices.", "Business Administration", "Management", "beginner", "None", 3, ["management", "business", "leadership"]),
    ("Management Information", "Study of the design, implementation, and strategic management of information systems (MIS) in corporate organizations to support business decision-making, operational control, and competitive advantage.", "Business Administration", "Management", "intermediate", "Principles of Management (3 Units)", 3, ["management", "information systems", "business", "technology", "database"]),
    ("Strategic Marketing", "Advanced marketing strategies for global brands.", "Business Administration", "Marketing", "advanced", "Principles of Management", 3, ["marketing", "strategy", "branding"]),
    ("Business Ethics", "Moral principles in the world of business.", "Business Administration", "Business Ethics", "intermediate", "None", 2, ["ethics", "philosophy", "business"]),

    # Accounting
    ("Financial Accounting", "Recording and reporting financial transactions.", "Accounting", "Financial Accounting", "beginner", "None", 3, ["finance", "numbers", "accounting"]),
    ("Forensic Accounting", "Investigating financial crimes and fraud.", "Accounting", "Forensic Accounting", "advanced", "Financial Accounting", 4, ["fraud", "investigation", "accounting"]),

    # Social Sciences
    ("Introduction to Psychology", "Study of human behavior and mental processes.", "Social Sciences", "Psychology", "beginner", "None", 3, ["mind", "behavior", "psychology"]),
    ("International Relations", "The interaction of states and international organizations.", "Social Sciences", "International Relations", "intermediate", "None", 3, ["politics", "global", "diplomacy"]),
    ("Microeconomics", "Economic behavior of individuals and firms.", "Social Sciences", "Economics", "intermediate", "None", 3, ["economy", "money", "markets"]),

    # Arts & Others
    ("Graphic Design Basics", "Visual communication using typography and imagery.", "Arts", "Graphic Design", "beginner", "None", 3, ["design", "art", "creative"]),
    ("History of Modern Art", "Art movements from the 19th century to today.", "Arts", "History of Art", "intermediate", "None", 3, ["art", "history", "culture"]),
    ("Introduction to Architecture", "Basic principles of architectural design.", "Others", "Architecture", "beginner", "None", 4, ["design", "building", "architecture"]),
    ("Applied Mathematics", "Mathematical methods used in science and engineering.", "Others", "Mathematics", "advanced", "None", 3, ["math", "science", "logic"]),
    
    # Research & Academic Projects
    ("Research Methodology", "Master the scientific research process. Learn how to formulate research problems, construct conceptual frameworks, conduct literature reviews, write academic proposals, and analyze qualitative and quantitative data.", "Computer Science", "Research", "intermediate", "None", 3, ["research", "methodology", "writing", "data analysis", "ethics"]),
    ("Final Year Research Project", "Apply your computer science and academic knowledge to solve a real-world research problem. Culminates in a comprehensive dissertation, implementation, and oral defense.", "Computer Science", "Research", "advanced", "Research Methodology", 6, ["research", "dissertation", "project", "thesis", "defense"])
]

def seed():
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing courses to avoid duplicates during testing
    cursor.execute("DELETE FROM courses")

    for title, desc, dept, cat, diff, prereq, creds, tags in COURSES:
        cursor.execute(
            """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(COURSES)} courses successfully.")

if __name__ == "__main__":
    seed()
