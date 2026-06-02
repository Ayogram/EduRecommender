"""
Programmatic course curriculum seeder generator.
Generates 595 courses spanning all 14 categories and 119 departments.
"""

import json

CATEGORIES_METADATA = {
    "Computing & Technology": {
        "departments": [
            "Computer Science", "Software Engineering", "Cybersecurity", 
            "Data Science", "Artificial Intelligence", "Information Technology", 
            "Information Systems", "Computer Engineering", "Cloud Computing", 
            "Robotics", "Game Development", "Blockchain Technology", 
            "Network Engineering", "Digital Forensics"
        ],
        "topics": [
            "Programming", "Data Structures", "Algorithms", "Databases", 
            "Operating Systems", "Computer Networks", "Cybersecurity", 
            "Machine Learning", "AI", "Software Design", "Cloud Computing", 
            "Mathematics", "Statistics", "Computer Architecture"
        ]
    },
    "Engineering": {
        "departments": [
            "Civil Engineering", "Mechanical Engineering", "Electrical Engineering", 
            "Electronic Engineering", "Chemical Engineering", "Petroleum Engineering", 
            "Aerospace Engineering", "Mechatronics Engineering", "Agricultural Engineering", 
            "Biomedical Engineering", "Environmental Engineering", "Marine Engineering", 
            "Industrial Engineering"
        ],
        "topics": [
            "Engineering Mathematics", "Engineering Drawing", "Mechanics", 
            "Thermodynamics", "Fluid Mechanics", "Circuit Theory", "Electronics", 
            "Structural Analysis", "Control Systems", "Materials Science", 
            "Manufacturing", "Design Projects"
        ]
    },
    "Medicine & Health Sciences": {
        "departments": [
            "Medicine", "Nursing", "Pharmacy", "Dentistry", "Physiotherapy", 
            "Medical Laboratory Science", "Anatomy", "Physiology", "Public Health", 
            "Radiography", "Optometry"
        ],
        "topics": [
            "Human Anatomy", "Physiology", "Biochemistry", "Pathology", 
            "Pharmacology", "Microbiology", "Clinical Medicine", "Surgery", 
            "Pediatrics", "Community Health", "Diagnostics"
        ]
    },
    "Business & Finance": {
        "departments": [
            "Accounting", "Economics", "Finance", "Banking & Finance", 
            "Business Administration", "Marketing", "Human Resource Management", 
            "Entrepreneurship", "International Business", "Supply Chain Management"
        ],
        "topics": [
            "Financial Accounting", "Cost Accounting", "Auditing", "Taxation", 
            "Economics", "Statistics", "Business Law", "Financial Management", 
            "Investments", "Marketing", "Human Resources"
        ]
    },
    "Law & Governance": {
        "departments": [
            "Law", "International Law", "Political Science", "Public Administration", 
            "International Relations", "Peace & Conflict Studies"
        ],
        "topics": [
            "Constitutional Law", "Criminal Law", "Commercial Law", "International Law", 
            "Jurisprudence", "Political Theory", "Public Policy", "Governance"
        ]
    },
    "Social Sciences": {
        "departments": [
            "Psychology", "Sociology", "Criminology", "Anthropology", 
            "Social Work", "Development Studies"
        ],
        "topics": [
            "Human Behaviour", "Research Methods", "Statistics", "Social Theory", 
            "Criminology", "Counselling", "Community Development"
        ]
    },
    "Natural Sciences": {
        "departments": [
            "Physics", "Chemistry", "Biochemistry", "Microbiology", 
            "Biotechnology", "Biology", "Geology", "Geophysics", "Environmental Science"
        ],
        "topics": [
            "Organic Chemistry", "Physical Chemistry", "Genetics", "Molecular Biology", 
            "Microbiology", "Ecology", "Environmental Analysis", "Laboratory Techniques"
        ]
    },
    "Mathematics & Statistics": {
        "departments": [
            "Mathematics", "Statistics", "Applied Mathematics", "Actuarial Science", 
            "Financial Mathematics"
        ],
        "topics": [
            "Calculus", "Linear Algebra", "Probability", "Statistics", 
            "Numerical Analysis", "Mathematical Modelling", "Data Analysis"
        ]
    },
    "Agriculture": {
        "departments": [
            "Agriculture", "Animal Science", "Crop Science", "Agronomy", 
            "Fisheries", "Forestry", "Horticulture", "Soil Science", "Agricultural Economics"
        ],
        "topics": [
            "Crop Production", "Animal Production", "Soil Science", 
            "Agricultural Engineering", "Farm Management", "Agricultural Economics"
        ]
    },
    "Education": {
        "departments": [
            "Education", "Mathematics Education", "English Education", 
            "Science Education", "Business Education", "Technical Education", 
            "Guidance & Counselling"
        ],
        "topics": [
            "Teaching Methods", "Curriculum Development", "Educational Psychology", 
            "Classroom Management", "Assessment Techniques"
        ]
    },
    "Arts & Humanities": {
        "departments": [
            "English", "Linguistics", "History", "Philosophy", 
            "Religious Studies", "Theology", "Archaeology"
        ],
        "topics": [
            "Literature", "Language Analysis", "Historical Research", "Ethics", 
            "Philosophy", "Religious Texts"
        ]
    },
    "Communication & Media": {
        "departments": [
            "Mass Communication", "Journalism", "Public Relations", "Advertising", 
            "Broadcasting", "Media Studies"
        ],
        "topics": [
            "News Writing", "Public Relations", "Media Ethics", "Broadcasting", 
            "Digital Media", "Communication Theory"
        ]
    },
    "Creative Arts": {
        "departments": [
            "Architecture", "Fine Arts", "Graphic Design", "Fashion Design", 
            "Industrial Design", "Music", "Theatre Arts", "Film Production"
        ],
        "topics": [
            "Design Principles", "Drawing", "Architecture Studio", "Fashion Technology", 
            "Photography", "Film Production", "Music Theory"
        ]
    },
    "Emerging Technologies": {
        "departments": [
            "Artificial Intelligence", "FinTech", "Bioinformatics", "Health Informatics", 
            "Renewable Energy Engineering", "Smart Systems Engineering", "Quantum Computing", 
            "Nanotechnology"
        ],
        "topics": [
            "Machine Learning", "Deep Learning", "Financial Systems", "Genomics", 
            "Renewable Energy Systems", "Smart Automation", "Quantum Algorithms"
        ]
    }
}

def generate_all_courses():
    """Returns a list of tuples representing 595 generated courses."""
    courses = []
    for cat_name, info in CATEGORIES_METADATA.items():
        depts = info["departments"]
        topics = info["topics"]
        for dept in depts:
            # Course 1: Introduction (Beginner, 3 Credits)
            c1_title = f"Introduction to {dept}"
            c1_desc = f"An introductory course covering the foundational principles, core concepts, and basic methodologies of {dept}."
            c1_diff = "beginner"
            c1_prereq = "None"
            c1_credits = 3
            c1_tags = [dept.lower(), cat_name.lower(), "introduction"] + [t.lower() for t in topics[:2]]
            courses.append((c1_title, c1_desc, dept, cat_name, c1_diff, c1_prereq, c1_credits, c1_tags))

            # Course 2: Principles & Applications (Intermediate, 3 Credits)
            c2_title = f"Principles and Applications of {dept}"
            c2_desc = f"Exploring active practices, industrial tools, and technical methodologies utilized in the field of {dept}."
            c2_diff = "intermediate"
            c2_prereq = f"Introduction to {dept}"
            c2_credits = 3
            c2_tags = [dept.lower(), "principles", "methods"] + [t.lower() for t in topics[2:4]]
            courses.append((c2_title, c2_desc, dept, cat_name, c2_diff, c2_prereq, c2_credits, c2_tags))

            # Course 3: Systems & Technology (Intermediate, 3 Credits)
            c3_title = f"{dept} Systems & Infrastructure"
            c3_desc = f"Detailed examination of structural components, computational architecture, and implementation frameworks in {dept}."
            c3_diff = "intermediate"
            c3_prereq = f"Introduction to {dept}"
            c3_credits = 3
            c3_tags = [dept.lower(), "systems", "infrastructure"] + [t.lower() for t in topics[4:6]]
            courses.append((c3_title, c3_desc, dept, cat_name, c3_diff, c3_prereq, c3_credits, c3_tags))

            # Course 4: Advanced Systems (Advanced, 4 Credits)
            c4_title = f"Advanced {dept} Analysis"
            c4_desc = f"Deep dive into advanced theoretical paradigms, complex design patterns, and case study assessments in {dept}."
            c4_diff = "advanced"
            c4_prereq = f"Principles and Applications of {dept}"
            c4_credits = 4
            c4_tags = [dept.lower(), "advanced", "analysis"] + [t.lower() for t in topics[6:8]]
            courses.append((c4_title, c4_desc, dept, cat_name, c4_diff, c4_prereq, c4_credits, c4_tags))

            # Course 5: Capstone / Research (Advanced, 4 Credits)
            c5_title = f"{dept} Research & Capstone Project"
            c5_desc = f"Synthesizing prior concepts to design, implement, and validate a comprehensive real-world research project or dissertation in {dept}."
            c5_diff = "advanced"
            c5_prereq = f"Advanced {dept} Analysis"
            c5_credits = 4
            c5_tags = [dept.lower(), "capstone", "research", "project"] + [t.lower() for t in topics[8:10]]
            courses.append((c5_title, c5_desc, dept, cat_name, c5_diff, c5_prereq, c5_credits, c5_tags))
            
    return courses
