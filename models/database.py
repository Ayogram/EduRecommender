"""
Database helper – thin wrapper around sqlite3 for the application.
Provides get_db() for per-request connections and init_db() for schema creation.
"""

import os
import sqlite3
import json
from flask import g, current_app

# ── Schema DDL ──────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    password_hash   TEXT,
    google_id       TEXT    UNIQUE,
    profile_picture TEXT    DEFAULT '/static/img/default_avatar.png',
    role            TEXT    NOT NULL DEFAULT 'user'  CHECK(role IN ('user','admin','super_admin')),
    status          TEXT    NOT NULL DEFAULT 'active' CHECK(status IN ('active','suspended')),
    interests       TEXT    DEFAULT '[]',
    nickname        TEXT,
    academic_field  TEXT,
    department      TEXT,
    gpa             REAL    DEFAULT 0.0,
    is_verified     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    department    TEXT,
    category      TEXT NOT NULL,
    difficulty    TEXT NOT NULL CHECK(difficulty IN ('beginner','intermediate','advanced')),
    prerequisites TEXT DEFAULT 'None',
    credits       INTEGER DEFAULT 3,
    tags          TEXT DEFAULT '[]',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_courses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rating      REAL    DEFAULT 0 CHECK(rating >= 0 AND rating <= 5),
    grade       TEXT    DEFAULT 'N/A',
    completed   INTEGER DEFAULT 0,
    current_module_id INTEGER,
    current_lesson_id INTEGER,
    progress    REAL    DEFAULT 0.0,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);

CREATE TABLE IF NOT EXISTS course_modules (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id   INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    description TEXT,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS module_lessons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    content     TEXT,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS module_exams (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    questions   TEXT    NOT NULL,  -- JSON string of MCQs
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exam_results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id   INTEGER NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    score       REAL    NOT NULL,
    attempts    INTEGER DEFAULT 1,
    best_score  REAL    NOT NULL,
    history     TEXT    DEFAULT '[]', -- JSON string of scores
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id           INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    score               REAL    NOT NULL,
    success_probability REAL    DEFAULT 0.0,
    explanation         TEXT,
    method              TEXT    CHECK(method IN ('content','collaborative','hybrid')),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject         TEXT    NOT NULL,
    message         TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','resolved')),
    admin_response  TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message     TEXT    NOT NULL,
    is_read     INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    """Return the per-request database connection (stored on Flask `g`)."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


COURSES_SEED = [
    # Computer Science
    ("Introduction to Python", "Learn the basics of programming with Python.", "Computer Science", "Programming", "beginner", "None", 3, ["python", "coding", "basics"]),
    ("Data Structures & Algorithms", "Fundamental concepts of algorithms and data organization.", "Computer Science", "Software Engineering", "intermediate", "Introduction to Python", 4, ["algorithms", "data structures", "performance"]),
    ("Artificial Intelligence", "Concepts of machine learning, neural networks, and AI.", "Computer Science", "Artificial Intelligence", "advanced", "Data Structures & Algorithms", 4, ["ai", "machine learning", "neural networks"]),
    ("Web Development Boot Camp", "Full stack development with HTML, CSS, and JS.", "Computer Science", "Web Development", "beginner", "None", 3, ["web", "html", "css", "javascript"]),
    ("Cybersecurity Fundamentals", "Protecting systems and networks from digital attacks.", "Computer Science", "Cybersecurity", "intermediate", "Introduction to Python", 3, ["security", "networking", "hacking"]),
    ("Research Methodology", "Master the scientific research process. Learn how to formulate research problems, construct conceptual frameworks, conduct literature reviews, write academic proposals, and analyze qualitative and quantitative data.", "Computer Science", "Research", "intermediate", "None", 3, ["research", "methodology", "writing", "data analysis", "ethics"]),
    ("Final Year Research Project", "Apply your computer science and academic knowledge to solve a real-world research problem. Culminates in a comprehensive dissertation, implementation, and oral defense.", "Computer Science", "Research", "advanced", "Research Methodology", 6, ["research", "dissertation", "project", "thesis", "defense"]),
    ("Machine Learning Specialization", "Master fundamental machine learning concepts including supervised and unsupervised learning, regression, classification, and neural networks.", "Computer Science", "Machine Learning", "intermediate", "Introduction to Python", 4, ["ml", "algorithms", "neural networks", "regression"]),
    ("Deep Learning Specialization", "Build and train deep neural networks, understand convolutional networks, sequence models, and transform architectures.", "Computer Science", "Deep Learning", "advanced", "Machine Learning Specialization", 4, ["deep learning", "neural networks", "ai", "computer vision"]),
    ("Cloud Computing Architecture", "Learn how to design, deploy, and manage highly scalable and resilient application grids on modern cloud environments.", "Computer Science", "Cloud Computing", "intermediate", "None", 3, ["cloud", "aws", "devops", "infrastructure"]),

    # Law
    ("Criminal Law 101", "Introduction to criminal justice and legal systems.", "Law", "Criminal Law", "beginner", "None", 3, ["law", "justice", "court"]),
    ("Corporate Law", "Legal aspects of business organizations and transactions.", "Law", "Corporate Law", "intermediate", "Criminal Law 101", 3, ["business", "contracts", "law"]),
    ("International Human Rights", "Evolution and enforcement of human rights globally.", "Law", "Human Rights", "advanced", "Criminal Law 101", 3, ["human rights", "un", "law"]),
    ("Intellectual Property Law", "Patents, trademarks, and copyright law.", "Law", "IP Law", "intermediate", "None", 3, ["copyright", "patents", "law"]),
    ("Constitutional Law & Governance", "Analyzing checks and balances, federal powers, and civil liberty guarantees outlined in constitutional codes.", "Law", "Constitutional Law", "beginner", "None", 3, ["constitution", "civil liberties", "courts", "power"]),
    ("Intellectual Property & Digital Rights", "Protecting copy-rights, patents, trademarks, and user data privacy within the modern digital software landscape.", "Law", "IP Law", "intermediate", "None", 3, ["copyright", "patents", "privacy", "digital"]),
    ("International Law & Treaty Arbitration", "Legal frameworks governing global trade, human rights treaties, boundary disputes, and international court proceedings.", "Law", "Human Rights", "advanced", "Criminal Law 101", 3, ["treaty", "un", "arbitration", "international"]),

    # Medicine
    ("Human Anatomy", "Detailed study of human body structures.", "Medicine", "Anatomy", "beginner", "None", 4, ["anatomy", "biology", "body"]),
    ("General Surgery", "Surgical principles and techniques.", "Medicine", "Surgery", "advanced", "Human Anatomy", 5, ["surgery", "medical", "hospital"]),
    ("Pharmacology", "Study of drugs and their actions on biological systems.", "Medicine", "Pharmacology", "intermediate", "None", 3, ["drugs", "medicine", "biology"]),
    ("Public Health Global Trends", "Exploring health challenges in the modern world.", "Medicine", "Public Health", "beginner", "None", 3, ["health", "policy", "global"]),
    ("Human Anatomy & Physiology", "Systematic biological study of skeletal, muscular, cardiovascular, respiratory, and nervous networks in the human body.", "Medicine", "Anatomy", "beginner", "None", 4, ["anatomy", "physiology", "body", "biology"]),
    ("Medical Ethics & Professionalism", "Autonomy, beneficence, non-maleficence, and legal duties governing patient-clinician fiduciary relationships.", "Medicine", "Ethics", "beginner", "None", 3, ["ethics", "patient", "clinical", "legal"]),
    ("Clinical Research & Epidemiology", "Designing human clinical trials, gathering health data, tracking virus outbreaks, and evaluating treatment metrics.", "Medicine", "Public Health", "intermediate", "None", 3, ["clinical", "trials", "epidemiology", "data"]),

    # Mechanical Engineering
    ("Mechanical Engineering Principles", "Statics, dynamics, and thermodynamics.", "Mechanical Engineering", "Mechanical Engineering", "beginner", "None", 4, ["physics", "machines", "engineering"]),
    ("Fluid Mechanics & Heat Transfer", "Calculations of fluid flow rate and convection/conduction heat grids.", "Mechanical Engineering", "Fluid Dynamics", "intermediate", "Mechanical Engineering Principles", 4, ["fluids", "mechanics", "heat"]),
    ("Introduction to CAD and 3D Printing", "Learn to design 3D models using Computer-Aided Design software and manufacture physical prototypes using additive manufacturing methods.", "Mechanical Engineering", "CAD", "beginner", "None", 3, ["cad", "design", "3d printing", "prototyping"]),
    ("Robotics & Control Systems", "Mathematical modeling of robotic joints, kinematics, feedback loops, and automated motion planning algorithms.", "Mechanical Engineering", "Robotics", "advanced", "Mechanical Engineering Principles", 4, ["robotics", "automation", "controls", "kinematics"]),
    ("Applied Materials Science", "Physical and chemical properties of engineering metals, polymers, ceramics, and structural composite materials.", "Mechanical Engineering", "Materials", "intermediate", "None", 3, ["materials", "alloys", "stress", "composites"]),

    # Petroleum Engineering
    ("Introduction to Reservoir Engineering", "Calculations of reservoir fluid flow, geology, and volume estimation.", "Petroleum Engineering", "Reservoir Engineering", "beginner", "None", 3, ["reservoir", "oil", "gas", "geology"]),
    ("Drilling Engineering & Operations", "Techniques of deep well design, petrophysics, and drilling.", "Petroleum Engineering", "Drilling", "advanced", "Introduction to Reservoir Engineering", 4, ["drilling", "petrophysics", "engineering"]),
    ("Enhanced Oil Recovery Methods", "Advanced chemical, thermal, and gas injection methods used to maximize crude oil extraction from aging reservoirs.", "Petroleum Engineering", "Reservoir", "advanced", "Introduction to Reservoir Engineering", 4, ["eor", "injection", "oil", "gas"]),
    ("Reservoir Simulation & Modeling", "Constructing numerical computer grids to simulate subsurface fluid flows, pressure changes, and oil depletion routes.", "Petroleum Engineering", "Simulation", "advanced", "Introduction to Reservoir Engineering", 4, ["simulation", "subsurface", "modeling", "fluids"]),
    ("Well Test Analysis & Logging", "Interpreting pressure transient tests and petrophysical logs to evaluate subsurface formation boundaries.", "Petroleum Engineering", "Well Logging", "intermediate", "None", 3, ["well logging", "pressure", "petrophysics", "geology"]),

    # Electrical Engineering
    ("Electrical Circuits", "AC and DC circuit analysis.", "Electrical Engineering", "Electrical Engineering", "intermediate", "None", 3, ["electricity", "circuits", "engineering"]),
    ("Power Systems & Renewable Energy", "Design of high-voltage transmission lines, power grids, and solar inputs.", "Electrical Engineering", "Power Engineering", "advanced", "Electrical Circuits", 4, ["power", "grid", "electricity", "renewable"]),
    ("AC/DC Circuits & Power Transmission", "Analyzing power transmission lines, transformer operations, active/reactive grids, and short-circuit faults.", "Electrical Engineering", "Power Systems", "intermediate", "Electrical Circuits", 4, ["ac", "transmission", "transformer", "grids"]),
    ("Digital Signal Processing", "Discrete-time signals, Fourier transforms, digital filters, spectral analysis, and real-time audio/video processing algorithms.", "Electrical Engineering", "DSP", "advanced", "None", 4, ["dsp", "fourier", "signals", "filters"]),
    ("Renewable Energy Grid Integration", "Connecting solar solar panels, wind turbine generators, and storage battery systems into national power distribution grids.", "Electrical Engineering", "Renewable Energy", "intermediate", "None", 3, ["solar", "wind", "grids", "clean energy"]),

    # Information and Computer Engineering
    ("Computer Network Architectures", "Principles of OSI layers, TCP/UDP routing, and network design.", "Information and Computer Engineering", "Networks", "intermediate", "None", 3, ["networks", "routing", "tcp"]),
    ("Embedded Systems Design", "Programming microcontrollers and designing hardware interfaces.", "Information and Computer Engineering", "Embedded Systems", "intermediate", "None", 3, ["embedded", "microcontrollers", "hardware"]),
    ("Advanced Computer Architecture", "In-depth study of high-performance processor design, pipelining, cache hierarchies, memory systems, and instruction-level parallelism.", "Information and Computer Engineering", "Hardware", "advanced", "Embedded Systems Design", 4, ["cpu", "architecture", "hardware", "pipelining"]),
    ("Operating Systems Principles", "Explore CPU scheduling, process synchronization, memory management, file systems, and kernel protection mechanisms.", "Information and Computer Engineering", "Operating Systems", "intermediate", "None", 4, ["kernel", "linux", "threads", "memory"]),
    ("VLSI Design & Microprocessors", "Design principles of Very Large Scale Integration circuits, microprocessors, and hardware description languages.", "Information and Computer Engineering", "VLSI", "advanced", "Embedded Systems Design", 4, ["vlsi", "transistors", "circuits", "hardware"]),

    # Industrial Mathematics
    ("Applied Mathematics", "Mathematical methods used in science and engineering.", "Industrial Mathematics", "Mathematics", "advanced", "None", 3, ["math", "science", "logic"]),
    ("Mathematical Modeling & Simulation", "Using differential equations to simulate physical and industrial processes.", "Industrial Mathematics", "Mathematics", "advanced", "Applied Mathematics", 4, ["modeling", "differential equations", "simulation"]),
    ("Linear Optimization & Operations Research", "Solving resource allocation problems with linear programming.", "Industrial Mathematics", "Operations Research", "intermediate", "None", 3, ["optimization", "programming", "operations"]),
    ("Calculus & Differential Equations", "Limits, derivatives, multivariable integrals, and boundary value differential equations for engineering applications.", "Industrial Mathematics", "Mathematics", "beginner", "None", 4, ["calculus", "integrals", "math", "equations"]),
    ("Numerical Analysis & Computation", "Iterative mathematical algorithms to approximate root values, integrals, and differential equations.", "Industrial Mathematics", "Numerical Analysis", "intermediate", "None", 3, ["numerical", "algorithms", "approximation", "math"]),
    ("Probability & Mathematical Statistics", "Random variables, continuous probability densities, Bayesian inference, regression analysis, and hypothesis testing.", "Industrial Mathematics", "Statistics", "intermediate", "None", 3, ["probability", "statistics", "bayes", "regression"]),

    # Industrial Physics
    ("Fundamentals of Thermodynamics", "Statics and dynamics of heat transfer and power cycles.", "Industrial Physics", "Thermodynamics", "beginner", "None", 3, ["thermodynamics", "physics", "heat"]),
    ("Quantum Mechanics for Engineers", "Principles of quantum computing, solid state physics, and lasers.", "Industrial Physics", "Quantum Physics", "advanced", "None", 4, ["quantum", "physics", "lasers"]),
    ("Solid State Physics & Semiconductor Devices", "Crystalline lattices, quantum band theory, and physical workings of p-n junction diodes, transistors, and solar cells.", "Industrial Physics", "Solid State", "advanced", "Quantum Mechanics for Engineers", 4, ["solid state", "semiconductor", "diodes", "crystals"]),
    ("Laser Physics & Fiber Optics", "Atomic excitation, population inversion, optical resonators, laser coherence, and data propagation through fiber cables.", "Industrial Physics", "Optics", "intermediate", "None", 3, ["lasers", "optics", "fiber", "light"]),
    ("Classical Electromagnetism", "Maxwell's equations, electrostatic forces, magnetic fields, electromagnetic waves, and propagation in physical media.", "Industrial Physics", "Electromagnetism", "advanced", "None", 4, ["electromagnetism", "maxwell", "fields", "waves"]),

    # Psychology
    ("Introduction to Psychology", "Study of human behavior and mental processes.", "Psychology", "Psychology", "beginner", "None", 3, ["mind", "behavior", "psychology"]),
    ("Cognitive Psychology", "Exploring human memory, perception, and reasoning.", "Psychology", "Cognitive Science", "intermediate", "Introduction to Psychology", 3, ["cognitive", "memory", "mind"]),
    ("Clinical Psychology Methods", "Theory and clinical assessment models.", "Psychology", "Clinical", "advanced", "Introduction to Psychology", 4, ["clinical", "therapy", "assessment"]),
    ("Social Psychology and Group Behavior", "How individual thoughts, feelings, and actions are shaped by peer interactions, group conformity, and social networks.", "Psychology", "Social Psychology", "beginner", "None", 3, ["social", "conformity", "groups", "interaction"]),
    ("Neuropsychology & Brain Functions", "Biological structure of brain lobes, neurotransmitter pathways, and how brain trauma impacts cognitive behavior.", "Psychology", "Neuropsychology", "advanced", "Introduction to Psychology", 4, ["brain", "neurology", "biology", "synapses"]),
    ("Forensic Psychology & Criminology", "Evaluating witness credibility, psychological profiling, and applying clinical metrics within the criminal justice system.", "Psychology", "Clinical", "intermediate", "None", 3, ["forensic", "court", "criminology", "profiling"]),

    # Economics
    ("Microeconomics", "Economic behavior of individuals and firms.", "Economics", "Economics", "intermediate", "None", 3, ["economy", "money", "markets"]),
    ("Macroeconomics & Public Policy", "Aggregate demand, inflation, monetary policy, and public finance.", "Economics", "Economics", "intermediate", "Microeconomics", 3, ["macroeconomics", "policy", "finance"]),
    ("Game Theory for Economists", "Mathematical modeling of strategic scenarios where choices depend on other competitors. Covers Nash equilibrium.", "Economics", "Economics", "intermediate", "None", 3, ["game theory", "nash", "strategy", "decisions"]),
    ("Econometrics & Data Analysis", "Using statistical regression models to verify economic theories, analyze price elasticity, and forecast market rates.", "Economics", "Econometrics", "advanced", "Microeconomics", 4, ["econometrics", "regression", "statistics", "data"]),
    ("Behavioral Economics & Decision Making", "Psychological drivers behind financial choice, analyzing market anomalies, cognitive biases, and consumer utility.", "Economics", "Economics", "intermediate", "Microeconomics", 3, ["behavioral", "utility", "cognitive", "biases"]),

    # Fintech
    ("Blockchain & Cryptocurrencies", "Decentralized ledgers, consensus algorithms, smart contracts, and Ethereum.", "Fintech", "Blockchain", "intermediate", "None", 3, ["blockchain", "crypto", "bitcoin"]),
    ("Algorithmic Trading & Quantitative Finance", "Mathematical models and python scripts for algorithmic trading and portfolio optimization.", "Fintech", "Quantitative Finance", "advanced", "None", 4, ["trading", "algorithms", "finance"]),
    ("Blockchain, Cryptocurrencies and Decentralized Finance", "Decentralized consensus ledgers, cryptography, digital wallet transactions, and Ethereum smart contract programming.", "Fintech", "Blockchain", "intermediate", "None", 3, ["blockchain", "crypto", "defi", "bitcoin"]),
    ("Algorithmic Trading & Financial Modeling", "Designing automated trading strategies in Python, analyzing price indices, and calculating risk exposure metrics.", "Fintech", "Quantitative Finance", "advanced", "None", 4, ["trading", "algorithms", "finance", "python"]),
    ("Payment Systems & Digital Banking", "Technical security protocols governing credit gateway transactions, mobile banking apps, and online payment rails.", "Fintech", "Security", "intermediate", "None", 3, ["payments", "banking", "security", "gateways"]),

    # Business Administration
    ("Principles of Management", "Core management theories and practices.", "Business Administration", "Management", "beginner", "None", 3, ["management", "business", "leadership"]),
    ("Management Information", "Study of the design, implementation, and strategic management of information systems (MIS) in corporate organizations to support business decision-making, operational control, and competitive advantage.", "Business Administration", "Management", "intermediate", "Principles of Management (3 Units)", 3, ["management", "information systems", "business", "technology", "database"]),
    ("Strategic Marketing", "Advanced marketing strategies for global brands.", "Business Administration", "Marketing", "advanced", "Principles of Management", 3, ["marketing", "strategy", "branding"]),
    ("Business Ethics", "Moral principles in the world of business.", "Business Administration", "Business Ethics", "intermediate", "None", 2, ["ethics", "philosophy", "business"]),
    ("Strategic Management & Leadership", "Analyzing market environments, mapping competitive advantages, setting corporate goals, and leading organizational growth.", "Business Administration", "Management", "beginner", "None", 3, ["strategy", "leadership", "management", "corporate"]),
    ("Entrepreneurship: Launching a Startup", "Building business models, finding product-market fit, raising venture capital, and managing early-stage startup growth.", "Business Administration", "Entrepreneurship", "beginner", "None", 3, ["startup", "venture", "business model", "marketing"]),
    ("Operations & Supply Chain Management", "Optimizing logistics flow, managing factory inventory levels, reducing delivery delays, and evaluating vendor networks.", "Business Administration", "Operations", "intermediate", "Principles of Management", 3, ["supply chain", "logistics", "operations", "inventory"]),

    # Accounting
    ("Financial Accounting", "Recording and reporting financial transactions.", "Accounting", "Financial Accounting", "beginner", "None", 3, ["finance", "numbers", "accounting"]),
    ("Forensic Accounting", "Investigating financial crimes and fraud.", "Accounting", "Forensic Accounting", "advanced", "Financial Accounting", 4, ["fraud", "investigation", "accounting"]),
    ("Auditing Principles & Standards", "Structured procedures used to verify corporate accounts, assess internal controls, and prevent material fraud.", "Accounting", "Auditing", "intermediate", "Financial Accounting", 3, ["audit", "controls", "fraud", "reports"]),
    ("Corporate Finance & Valuation", "Calculating capital structures, evaluating mergers, and pricing businesses using discounted cash flow models.", "Accounting", "Corporate Finance", "advanced", "Financial Accounting", 4, ["valuation", "dcf", "mergers", "corporate"]),
    ("Taxation Systems & Compliance", "Corporate and individual income tax regulations, deduction codes, asset write-offs, and compliance auditing standards.", "Accounting", "Taxation", "intermediate", "None", 3, ["tax", "compliance", "deductions", "government"]),

    # Social Sciences
    ("International Relations", "The interaction of states and international organizations.", "Social Sciences", "International Relations", "intermediate", "None", 3, ["politics", "global", "diplomacy"]),
    ("Sociology & Social Institutions", "Analyzing group structures, cultural norms, social stratification, and inequality across modern communities.", "Social Sciences", "Sociology", "beginner", "None", 3, ["sociology", "norms", "inequality", "culture"]),
    ("Political Science & Global Politics", "Comparing democratic systems, legislative voting processes, policy draft pipelines, and international balance of power.", "Social Sciences", "Political Science", "beginner", "None", 3, ["politics", "democracy", "policy", "voting"]),
    ("Public Policy Analysis", "Evaluating how local and federal policies are drafted, modeled statistically, and audited to check program impacts.", "Social Sciences", "Public Policy", "intermediate", "None", 3, ["public policy", "impact", "audits", "evaluation"]),

    # Arts
    ("Graphic Design Basics", "Visual communication using typography and imagery.", "Arts", "Graphic Design", "beginner", "None", 3, ["design", "art", "creative"]),
    ("History of Modern Art", "Art movements from the 19th century to today.", "Arts", "History of Art", "intermediate", "None", 3, ["art", "history", "culture"]),
    ("Graphic Design & Visual Communication", "Creating typography layouts, using visual scale, and mapping brand standards across digital and print media.", "Arts", "Graphic Design", "beginner", "None", 3, ["design", "brand", "typography", "layout"]),
    ("History of Art & Architecture", "A chronological survey of creative visual arts and architecture from classical structures to contemporary styles.", "Arts", "Art History", "beginner", "None", 3, ["art history", "architecture", "paintings", "sculptures"]),
    ("Creative Writing & Storytelling", "Drafting screenplays, storyboard plotting, character arc development, and writing descriptive narrative arcs.", "Arts", "Creative Writing", "beginner", "None", 3, ["writing", "storyboard", "screenplay", "narrative"]),

    # Others
    ("Introduction to Architecture", "Basic principles of architectural design.", "Others", "Architecture", "beginner", "None", 4, ["design", "building", "architecture"])
]


def init_db():
    """Create all tables if they don't exist and auto-seed if empty."""
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    
    # Check if courses are empty
    count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    if count == 0:
        for title, desc, dept, cat, diff, prereq, creds, tags in COURSES_SEED:
            db.execute(
                """INSERT INTO courses (title, description, department, category, difficulty, prerequisites, credits, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, desc, dept, cat, diff, prereq, creds, json.dumps(tags))
            )
        db.commit()


def init_app(app):
    """Register teardown and CLI hooks."""
    app.teardown_appcontext(close_db)
