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
    ("Research Methodology", "Master the scientific research process. Learn how to formulate research problems, construct conceptual frameworks, conduct literature reviews, write academic proposals, and analyze qualitative and quantitative data.", "Computer Science", "Research", "intermediate", "None", 3, ["research", "methodology", "writing", "data analysis", "ethics"]),
    ("Final Year Research Project", "Apply your computer science and academic knowledge to solve a real-world research problem. Culminates in a comprehensive dissertation, implementation, and oral defense.", "Computer Science", "Research", "advanced", "Research Methodology", 6, ["research", "dissertation", "project", "thesis", "defense"]),

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

    # Mechanical Engineering
    ("Mechanical Engineering Principles", "Statics, dynamics, and thermodynamics.", "Mechanical Engineering", "Mechanical Engineering", "beginner", "None", 4, ["physics", "machines", "engineering"]),
    ("Fluid Mechanics & Heat Transfer", "Calculations of fluid flow rate and convection/conduction heat grids.", "Mechanical Engineering", "Fluid Dynamics", "intermediate", "Mechanical Engineering Principles", 4, ["fluids", "mechanics", "heat"]),

    # Petroleum Engineering
    ("Introduction to Reservoir Engineering", "Calculations of reservoir fluid flow, geology, and volume estimation.", "Petroleum Engineering", "Reservoir Engineering", "beginner", "None", 3, ["reservoir", "oil", "gas", "geology"]),
    ("Drilling Engineering & Operations", "Techniques of deep well design, petrophysics, and drilling.", "Petroleum Engineering", "Drilling", "advanced", "Introduction to Reservoir Engineering", 4, ["drilling", "petrophysics", "engineering"]),

    # Electrical Engineering
    ("Electrical Circuits", "AC and DC circuit analysis.", "Electrical Engineering", "Electrical Engineering", "intermediate", "None", 3, ["electricity", "circuits", "engineering"]),
    ("Power Systems & Renewable Energy", "Design of high-voltage transmission lines, power grids, and solar inputs.", "Electrical Engineering", "Power Engineering", "advanced", "Electrical Circuits", 4, ["power", "grid", "electricity", "renewable"]),

    # Information and Computer Engineering
    ("Computer Network Architectures", "Principles of OSI layers, TCP/UDP routing, and network design.", "Information and Computer Engineering", "Networks", "intermediate", "None", 3, ["networks", "routing", "tcp"]),
    ("Embedded Systems Design", "Programming microcontrollers and designing hardware interfaces.", "Information and Computer Engineering", "Embedded Systems", "intermediate", "None", 3, ["embedded", "microcontrollers", "hardware"]),

    # Industrial Mathematics
    ("Applied Mathematics", "Mathematical methods used in science and engineering.", "Industrial Mathematics", "Mathematics", "advanced", "None", 3, ["math", "science", "logic"]),
    ("Mathematical Modeling & Simulation", "Using differential equations to simulate physical and industrial processes.", "Industrial Mathematics", "Mathematics", "advanced", "Applied Mathematics", 4, ["modeling", "differential equations", "simulation"]),
    ("Linear Optimization & Operations Research", "Solving resource allocation problems with linear programming.", "Industrial Mathematics", "Operations Research", "intermediate", "None", 3, ["optimization", "programming", "operations"]),

    # Industrial Physics
    ("Fundamentals of Thermodynamics", "Statics and dynamics of heat transfer and power cycles.", "Industrial Physics", "Thermodynamics", "beginner", "None", 3, ["thermodynamics", "physics", "heat"]),
    ("Quantum Mechanics for Engineers", "Principles of quantum computing, solid state physics, and lasers.", "Industrial Physics", "Quantum Physics", "advanced", "None", 4, ["quantum", "physics", "lasers"]),

    # Psychology
    ("Introduction to Psychology", "Study of human behavior and mental processes.", "Psychology", "Psychology", "beginner", "None", 3, ["mind", "behavior", "psychology"]),
    ("Cognitive Psychology", "Exploring human memory, perception, and reasoning.", "Psychology", "Cognitive Science", "intermediate", "Introduction to Psychology", 3, ["cognitive", "memory", "mind"]),
    ("Clinical Psychology Methods", "Theory and clinical assessment models.", "Psychology", "Clinical", "advanced", "Introduction to Psychology", 4, ["clinical", "therapy", "assessment"]),

    # Economics
    ("Microeconomics", "Economic behavior of individuals and firms.", "Economics", "Economics", "intermediate", "None", 3, ["economy", "money", "markets"]),
    ("Macroeconomics & Public Policy", "Aggregate demand, inflation, monetary policy, and public finance.", "Economics", "Economics", "intermediate", "Microeconomics", 3, ["macroeconomics", "policy", "finance"]),

    # Fintech
    ("Blockchain & Cryptocurrencies", "Decentralized ledgers, consensus algorithms, smart contracts, and Ethereum.", "Fintech", "Blockchain", "intermediate", "None", 3, ["blockchain", "crypto", "bitcoin"]),
    ("Algorithmic Trading & Quantitative Finance", "Mathematical models and python scripts for algorithmic trading and portfolio optimization.", "Fintech", "Quantitative Finance", "advanced", "None", 4, ["trading", "algorithms", "finance"]),

    # Business
    ("Principles of Management", "Core management theories and practices.", "Business Administration", "Management", "beginner", "None", 3, ["management", "business", "leadership"]),
    ("Management Information", "Study of the design, implementation, and strategic management of information systems (MIS) in corporate organizations to support business decision-making, operational control, and competitive advantage.", "Business Administration", "Management", "intermediate", "Principles of Management (3 Units)", 3, ["management", "information systems", "business", "technology", "database"]),
    ("Strategic Marketing", "Advanced marketing strategies for global brands.", "Business Administration", "Marketing", "advanced", "Principles of Management", 3, ["marketing", "strategy", "branding"]),
    ("Business Ethics", "Moral principles in the world of business.", "Business Administration", "Business Ethics", "intermediate", "None", 2, ["ethics", "philosophy", "business"]),

    # Accounting
    ("Financial Accounting", "Recording and reporting financial transactions.", "Accounting", "Financial Accounting", "beginner", "None", 3, ["finance", "numbers", "accounting"]),
    ("Forensic Accounting", "Investigating financial crimes and fraud.", "Accounting", "Forensic Accounting", "advanced", "Financial Accounting", 4, ["fraud", "investigation", "accounting"]),

    # Social Sciences
    ("International Relations", "The interaction of states and international organizations.", "Social Sciences", "International Relations", "intermediate", "None", 3, ["politics", "global", "diplomacy"]),

    # Arts
    ("Graphic Design Basics", "Visual communication using typography and imagery.", "Arts", "Graphic Design", "beginner", "None", 3, ["design", "art", "creative"]),
    ("History of Modern Art", "Art movements from the 19th century to today.", "Arts", "History of Art", "intermediate", "None", 3, ["art", "history", "culture"]),

    # Others
    ("Introduction to Architecture", "Basic principles of architectural design.", "Others", "Architecture", "beginner", "None", 4, ["design", "building", "architecture"])
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
