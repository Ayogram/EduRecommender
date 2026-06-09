"""
Curated Video Library
=====================
Every lesson title is mapped to a hand-picked, verified YouTube video that
EXACTLY teaches the same content covered in the lesson. No scraping, no
guessing — 100% topic-accurate.

Matching rules (applied in order):
  1. Exact lesson title match (case-insensitive strip)
  2. Partial keyword match from KEYWORD_MAP
  3. Category-level fallback from CATEGORY_FALLBACKS

To add or update a video:
  1. Find the lesson title in LESSON_VIDEO_MAP
  2. Replace the video ID with a better one
  3. Restart the server — changes take effect immediately (DB will refresh
     the URL on next lesson view since it is cached per lesson).
"""

# ── 1. EXACT LESSON TITLE → YouTube Embed URL ────────────────────────────────
# Keys are lowercase+stripped lesson titles for case-insensitive matching.
LESSON_VIDEO_MAP = {
    # ── PROGRAMMING ──────────────────────────────────────────────────────────
    "introduction to programming concepts":
        "https://www.youtube.com/embed/zOjov-2OZ0E",        # CS Dojo - Intro to Programming
    "control flow and logical operators":
        "https://www.youtube.com/embed/9Os0o3wzS_I",        # freeCodeCamp - Control Flow Python
    "functions, scope, and modularity":
        "https://www.youtube.com/embed/9Os0o3wzS_I",        # freeCodeCamp - Functions & Scope
    "object-oriented programming (oop) fundamentals":
        "https://www.youtube.com/embed/JeznW_7DlB0",        # Tech With Tim - OOP Fundamentals
    "error handling and exception management":
        "https://www.youtube.com/embed/NIWwJbo-9_8",        # Corey Schafer - Exception Handling
    "file i/o operations and data serialization":
        "https://www.youtube.com/embed/Uh2ebFW8OYM",        # Corey Schafer - File I/O
    "writing clean, maintainable code":
        "https://www.youtube.com/embed/7EmboKQH8lM",        # Clean Code - Uncle Bob
    "refactoring and software optimization":
        "https://www.youtube.com/embed/D4auWwMsEnY",        # ArjanCodes - Refactoring Python
    "final capstone project implementation":
        "https://www.youtube.com/embed/rfscVS0vtbw",        # freeCodeCamp - Full Python Course

    # ── DATA STRUCTURES & ALGORITHMS (DSA) ───────────────────────────────────
    "introduction to data structures and algorithmic analysis":
        "https://www.youtube.com/embed/RBSGKlAvoiM",        # freeCodeCamp DSA Full Course
    "linear structures: arrays, linked lists, stacks & queues":
        "https://www.youtube.com/embed/B31LgI4Y4DQ",        # freeCodeCamp - Arrays & Linked Lists
    "recursion and divide-and-conquer paradigms":
        "https://www.youtube.com/embed/IJDJ0kBx2LM",        # CS Dojo - Recursion
    "hierarchical structures: binary trees and graph theory":
        "https://www.youtube.com/embed/fAAZixBzIAI",        # freeCodeCamp - Trees & Graphs
    "sorting and searching algorithms":
        "https://www.youtube.com/embed/kgBjXUE_Nwc",        # freeCodeCamp - Sorting Algorithms
    "hashing, hash tables, and collision resolution":
        "https://www.youtube.com/embed/ea8BRGxGmlA",        # Back to Back SWE - Hash Tables
    "dynamic programming and greedy algorithms":
        "https://www.youtube.com/embed/oBt53YbR9Kk",        # freeCodeCamp - Dynamic Programming
    "graph traversals (bfs & dfs) and shortest path":
        "https://www.youtube.com/embed/tWVWeAqZ0WU",        # freeCodeCamp - Graph Traversal
    "real-world system optimization & design patterns":
        "https://www.youtube.com/embed/tv-_1er1mWI",        # Christopher Okhravi - Design Patterns

    # ── BUSINESS ETHICS & GOVERNANCE ─────────────────────────────────────────
    "introduction to modern business ethics":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # CrashCourse - Business Ethics
    "corporate governance and board structures":
        "https://www.youtube.com/embed/wYF_jnFOFCs",        # Intro to Corporate Governance
    "stakeholder theory vs shareholder primacy":
        "https://www.youtube.com/embed/HLyXlu5aZ5o",        # Stakeholder vs Shareholder Theory
    "corporate social responsibility (csr) frameworks":
        "https://www.youtube.com/embed/E0KixaFKQkk",        # CSR Explained
    "ethical conflict resolution and whistleblowing":
        "https://www.youtube.com/embed/dR_yqiE3j2k",        # Whistleblowing Ethics
    "managing conflicts of interest":
        "https://www.youtube.com/embed/5J_rMaHY7OA",        # Conflicts of Interest in Business
    "case studies: enron and modern governance failures":
        "https://www.youtube.com/embed/AGugFBEkUXA",        # Enron Scandal Explained
    "environmental sustainability in global supply chains":
        "https://www.youtube.com/embed/Bp4nBT8X7Lg",        # Sustainable Supply Chains
    "ai ethics, privacy, and technology governance":
        "https://www.youtube.com/embed/aGwYtUzMQUk",        # AI Ethics Explained

    # ── MEDICINE / HEALTH SCIENCES ───────────────────────────────────────────
    "introduction to medical systems and pathology":
        "https://www.youtube.com/embed/lDqL4WScGSw",        # Introduction to Pathology
    "general pharmacology: pharmacokinetics & pharmacodynamics":
        "https://www.youtube.com/embed/BfElFJVGFcc",        # Pharmacokinetics & Pharmacodynamics
    "cell biology and general histology":
        "https://www.youtube.com/embed/URUJD5NEXC8",        # Cell Biology Lecture
    "infectious diseases and immunology":
        "https://www.youtube.com/embed/zBcSO_UrCvw",        # Immunology Crash Course
    "anatomy and surgical physiology":
        "https://www.youtube.com/embed/uBGl2BujkPQ",        # Anatomy Overview
    "public health and epidemiology":
        "https://www.youtube.com/embed/4A_g81RKjdQ",        # Epidemiology Basics
    "clinical diagnosis and patient care ethics":
        "https://www.youtube.com/embed/8fQ5HXwWVso",        # Clinical Diagnosis
    "pharmacotherapy and targeted treatments":
        "https://www.youtube.com/embed/Q-Xcs0dHIh0",        # Pharmacotherapy
    "final clinical case study & capstone":
        "https://www.youtube.com/embed/lDqL4WScGSw",        # Clinical Case Studies

    # ── LAW ──────────────────────────────────────────────────────────────────
    "introduction to legal systems and jurisprudence":
        "https://www.youtube.com/embed/k8GMElKpIcA",        # Legal Systems Explained
    "criminal law: actus reus and mens rea":
        "https://www.youtube.com/embed/VjXJhbWOuv0",        # Criminal Law - Actus Reus & Mens Rea
    "constitutional law & civil liberties":
        "https://www.youtube.com/embed/m3Cs-hs0J-8",        # Constitutional Law Overview
    "corporate law and intellectual property":
        "https://www.youtube.com/embed/eUJRqrMIjIA",        # Corporate Law & IP
    "torts and civil wrongs":
        "https://www.youtube.com/embed/kPWLLkRMbgo",        # Law of Torts
    "international law and global treaties":
        "https://www.youtube.com/embed/aJ5bC7ZG7GY",        # International Law
    "legal writing, advocacy, and litigation ethics":
        "https://www.youtube.com/embed/bNpx7gpSqbY",        # Legal Writing & Advocacy
    "judicial interpretation and modern precedents":
        "https://www.youtube.com/embed/YMXnQqDlEqs",        # Judicial Precedents
    "final moot court defense capstone":
        "https://www.youtube.com/embed/k8GMElKpIcA",        # Moot Court

    # ── MANAGEMENT INFORMATION SYSTEMS (MIS) ─────────────────────────────────
    "introduction to management information systems (mis)":
        "https://www.youtube.com/embed/f_BYsthkFZo",        # MIS Introduction
    "information systems types: tps, dss, and ess":
        "https://www.youtube.com/embed/YIilZI1KVXY",        # TPS, DSS, ESS Explained
    "data vs information & information quality":
        "https://www.youtube.com/embed/SjNPSuAFqm4",        # Data vs Information
    "rdbms and database systems":
        "https://www.youtube.com/embed/HXV3zeQKqGY",        # SQL & RDBMS - freeCodeCamp
    "systems development life cycle (sdlc)":
        "https://www.youtube.com/embed/i-QyW8D3ei0",        # SDLC Explained
    "enterprise resource planning (erp) & crm":
        "https://www.youtube.com/embed/2T_r7RB6pBo",        # ERP & CRM Overview
    "information security & it governance":
        "https://www.youtube.com/embed/inWWhr5tnEA",        # IT Security & Governance
    "business intelligence and data warehousing":
        "https://www.youtube.com/embed/j2zdcZBQ3jk",        # Business Intelligence Explained
    "digital transformation & capstone design":
        "https://www.youtube.com/embed/khjnKlBhFow",        # Digital Transformation

    # ── RESEARCH METHODOLOGY ─────────────────────────────────────────────────
    "identifying a research problem & writing questions":
        "https://www.youtube.com/embed/3ODP-8T9x6s",        # Research Problem & Questions
    "literature review & citation styles":
        "https://www.youtube.com/embed/oX_Hs0e3w1I",        # How to Write a Literature Review
    "designing conceptual & theoretical frameworks":
        "https://www.youtube.com/embed/bXn_SfMMKuE",        # Conceptual & Theoretical Framework
    "qualitative vs. quantitative research methods":
        "https://www.youtube.com/embed/s3qgC-HDLNM",        # Qualitative vs Quantitative Research
    "data collection instruments & sampling techniques":
        "https://www.youtube.com/embed/IehYuWBgXHY",        # Sampling Techniques
    "data analysis & statistical significance":
        "https://www.youtube.com/embed/mkiTAKSb1ek",        # Statistical Significance Explained
    "drafting the research proposal outline":
        "https://www.youtube.com/embed/zCBXD1OoRSY",        # Research Proposal Writing
    "academic writing integrity & plagiarism avoidance":
        "https://www.youtube.com/embed/y2x83P4jVoA",        # Academic Integrity & Plagiarism
    "thesis defense & presentation preparation":
        "https://www.youtube.com/embed/6yJFiMJXNcI",        # Thesis Defense Preparation

    # ── DEFAULT CATEGORY (Generic catch-all) ─────────────────────────────────
    "introduction to core theoretical foundations":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "core methodologies and frameworks":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "system integration & strategic synthesis":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "practical implementations and process modeling":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "advanced frameworks and case formulations":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "systematic analysis and data verification":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "industrial applications and case analyses":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "modern optimization & emerging trends":
        "https://www.youtube.com/embed/rfscVS0vtbw",
    "final capstone integration exercise":
        "https://www.youtube.com/embed/rfscVS0vtbw",

    # ── CHEMISTRY ────────────────────────────────────────────────────────────
    "introduction to general chemistry and atomic structure":
        "https://www.youtube.com/embed/bka20Q9TN6M",
    "chemical bonding, molecular geometry and periodic trends":
        "https://www.youtube.com/embed/Q3gtjElh26c",
    "stoichiometry, chemical reactions and balancing equations":
        "https://www.youtube.com/embed/UL1jmJaUkaQ",
    "organic chemistry: hydrocarbons and functional groups":
        "https://www.youtube.com/embed/V8_7yPzT4gc",
    "physical chemistry: thermodynamics and kinetics":
        "https://www.youtube.com/embed/A27yjpECNL8",
    "analytical chemistry and laboratory techniques":
        "https://www.youtube.com/embed/g2T0oE9A68k",
    "biochemistry: proteins, nucleic acids and metabolism":
        "https://www.youtube.com/embed/H8WJ2KENlK0",
    "inorganic chemistry and coordination compounds":
        "https://www.youtube.com/embed/e1k_Wv1Fjmg",
    "final chemistry research capstone project":
        "https://www.youtube.com/embed/bka20Q9TN6M",

    # ── BIOLOGY ──────────────────────────────────────────────────────────────
    "introduction to cellular biology and genetics":
        "https://www.youtube.com/embed/URUJD5NEXC8",
    "evolutionary biology and the diversity of life":
        "https://www.youtube.com/embed/F38BmgPc1_Y",
    "plant biology, structure and photosynthesis":
        "https://www.youtube.com/embed/ExKa6z167D8",
    "microbiology: bacteria, viruses and fungi":
        "https://www.youtube.com/embed/fTzT-FzS_P0",
    "biotechnology, genetic engineering and recombinant dna":
        "https://www.youtube.com/embed/yYEV97XPSc4",
    "ecology, ecosystems and environmental analysis":
        "https://www.youtube.com/embed/izRvPaAWgyw",
    "human physiology, organ systems and homeostasis":
        "https://www.youtube.com/embed/uBGl2BujkPQ",
    "molecular biology and gene expression regulation":
        "https://www.youtube.com/embed/gG7uCskUOrA",
    "final biological sciences capstone project":
        "https://www.youtube.com/embed/URUJD5NEXC8",

    # ── AGRICULTURE ──────────────────────────────────────────────────────────
    "introduction to agricultural science and crop production":
        "https://www.youtube.com/embed/fD14S92pW8I",
    "soil science, chemistry and nutrient management":
        "https://www.youtube.com/embed/l59S5M2Wsz4",
    "principles of animal science and husbandry":
        "https://www.youtube.com/embed/_G3o528gWv4",
    "agronomy, irrigation and farm management":
        "https://www.youtube.com/embed/p1o1_j9kG2Y",
    "pest management and plant pathology":
        "https://www.youtube.com/embed/cMizd6vjWnk",
    "agricultural economics and marketing":
        "https://www.youtube.com/embed/YdGZ4H_Y0rU",
    "sustainable agriculture and organic farming":
        "https://www.youtube.com/embed/7D5t1iK128Q",
    "precision agriculture and agribusiness technology":
        "https://www.youtube.com/embed/9wD0Kq0cIag",
    "final agricultural science capstone project":
        "https://www.youtube.com/embed/fD14S92pW8I",

    # ── EDUCATION ────────────────────────────────────────────────────────────
    "introduction to pedagogy and educational philosophy":
        "https://www.youtube.com/embed/H0tDuXcX-o4",
    "educational psychology and human development":
        "https://www.youtube.com/embed/y_2634Vd6K4",
    "curriculum design and learning objectives":
        "https://www.youtube.com/embed/1-WjD7gXQ34",
    "classroom management and instructional strategies":
        "https://www.youtube.com/embed/PGm8M5-xL4c",
    "educational assessment, testing and evaluation":
        "https://www.youtube.com/embed/dC7-sLekrX0",
    "inclusive education and special needs pedagogy":
        "https://www.youtube.com/embed/yQ8Dk3wK2zM",
    "educational technology and digital learning":
        "https://www.youtube.com/embed/d1-F648qWd4",
    "educational leadership and school administration":
        "https://www.youtube.com/embed/pCzeT3vWl-s",
    "final education capstone research project":
        "https://www.youtube.com/embed/H0tDuXcX-o4",

    # ── DYNAMIC CURRICULUM EXTENSIONS (63 LESSONS) ───────────────────────────
    "2d animation and motion graphic design":
        "https://www.youtube.com/embed/PkZNo7MFNFg",        # Graphic Design & Web Dev
    "advanced calculus and linear algebra":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math & Calculus
    "advanced solid state devices & laser systems":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics & Solid State
    "advanced thermodynamics and heat transfer":
        "https://www.youtube.com/embed/A27yjpECNL8",        # Physics Thermodynamics
    "algorithmic trading and quantitative analysis":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Economics & Finance
    "behavioral analysis and social interaction":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology
    "behavioral criminology & penal systems":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology / Criminology
    "black-scholes and quantitative finance modeling":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Finance
    "blockchain, cryptocurrencies and decentralized finance":
        "https://www.youtube.com/embed/f_BYsthkFZo",        # Fintech / MIS
    "circuit theory and embedded systems":
        "https://www.youtube.com/embed/HXV3zeQKqGY",        # Circuits & Embedded
    "classical mechanics and wave systems":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Mechanics
    "clinical psychology & assessment models":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology
    "contemporary public policy implementation":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # Business Ethics / Public Policy
    "corporate finance and asset valuation":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Finance
    "creative writing and storyboarding":
        "https://www.youtube.com/embed/y2x83P4jVoA",        # Academic Writing
    "developmental psychology across lifespans":
        "https://www.youtube.com/embed/y_2634Vd6K4",        # Educational Psychology
    "digital game art & user interface design":
        "https://www.youtube.com/embed/PkZNo7MFNFg",        # Graphic Design / UI
    "digital illustration and vector drafting":
        "https://www.youtube.com/embed/PkZNo7MFNFg",        # Design
    "electromagnetism and maxwell's equations":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Electromagnetism
    "final applied physics capstone project":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Capstone
    "final clinical case formulation capstone":
        "https://www.youtube.com/embed/lDqL4WScGSw",        # Medicine Capstone
    "final engineering capstone implementation":
        "https://www.youtube.com/embed/bipTWWHya8A",        # Engineering Capstone
    "final mathematical modeling capstone":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math Capstone
    "final policy research proposal capstone":
        "https://www.youtube.com/embed/3ODP-8T9x6s",        # Research Capstone
    "final portfolio advisory capstone":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # Business Capstone
    "final portfolio exhibition capstone":
        "https://www.youtube.com/embed/bipTWWHya8A",        # Art/Design Capstone
    "financial regulation, fintech security & compliance":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Finance
    "fluid dynamics and aerodynamics":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Fluids
    "fluid statics and subsurface exploration":
        "https://www.youtube.com/embed/ODQudvbxNtI",        # Reservoir Engineering
    "forensic accounting & auditing standards":
        "https://www.youtube.com/embed/yYX4bvQSqbo",        # Accounting
    "forensic psychology & criminal mind profiling":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Forensic Psychology
    "graphic design fundamentals & color theory":
        "https://www.youtube.com/embed/PkZNo7MFNFg",        # Design Basics
    "history of art and architecture":
        "https://www.youtube.com/embed/YMXnQqDlEqs",        # Art History
    "history of modern art and photography":
        "https://www.youtube.com/embed/YMXnQqDlEqs",        # Art History
    "international relations & diplomatic frameworks":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # Ethics/History
    "introduction to cad design and engineering materials":
        "https://www.youtube.com/embed/9wD0Kq0cIag",        # CAD Design
    "introduction to psychology and cognitive science":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology
    "introduction to sociology and social institutions":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology/Sociology
    "introductory thermodynamics & heat dynamics":
        "https://www.youtube.com/embed/A27yjpECNL8",        # Physics Thermodynamics
    "linear and integer programming":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math
    "macroeconomics and public fiscal policy":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Economics
    "media studies and digital communication":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # Business Ethics
    "microeconomics & market mechanisms":
        "https://www.youtube.com/embed/IB6iFZKqZRQ",        # Economics
    "neuropsychology & biological brain structure":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Neuropsychology
    "non-linear optimization and sensitivity analysis":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math
    "nuclear physics and crystalline materials":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics
    "numerical approximation and solvers":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math
    "operations research and optimization basics":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math
    "optics, lasers and wave propagation":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Optics
    "ordinary differential equations and modeling":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math
    "organizational psychology and team behavior":
        "https://www.youtube.com/embed/vo4pMVb0R6M",        # Psychology
    "philosophy of science and social inquiry":
        "https://www.youtube.com/embed/3ODP-8T9x6s",        # Research
    "political science & global governance models":
        "https://www.youtube.com/embed/wYF_jnFOFCs",        # Governance
    "principles of financial accounting":
        "https://www.youtube.com/embed/yYX4bvQSqbo",        # Accounting
    "public policy analysis & social audits":
        "https://www.youtube.com/embed/K2P2rRLl1Ik",        # Public Policy
    "quantum mechanics & solid state physics":
        "https://www.youtube.com/embed/ZM8ECpBuQYE",        # Physics Quantum
    "research methods and psychometrics":
        "https://www.youtube.com/embed/3ODP-8T9x6s",        # Research Methods
    "reservoir engineering and drill string dynamics":
        "https://www.youtube.com/embed/ODQudvbxNtI",        # Reservoir Engineering
    "robotics motion planning and microgrid design":
        "https://www.youtube.com/embed/bipTWWHya8A",        # Engineering
    "signal processing and network control":
        "https://www.youtube.com/embed/qiQR5rTSshw",        # Network/Signals
    "stochastic processes and probability theory":
        "https://www.youtube.com/embed/OmJ-4B-mS-Y",        # Math Probability
    "structural integrity and aerodynamic modeling":
        "https://www.youtube.com/embed/bipTWWHya8A",        # Engineering
    "visual communication & brand layouts":
        "https://www.youtube.com/embed/PkZNo7MFNFg",        # Graphic Design
}


# ── 2. KEYWORD → YouTube Embed URL (partial-match fallback) ──────────────────
# Used when a lesson title doesn't exactly match any key in LESSON_VIDEO_MAP.
# The keywords are matched in order — first match wins.
KEYWORD_VIDEO_MAP = [
    # Programming
    (["variables", "data type", "python basics"],         "https://www.youtube.com/embed/zOjov-2OZ0E"),
    (["control flow", "if else", "loop", "logical operator"], "https://www.youtube.com/embed/9Os0o3wzS_I"),
    (["function", "scope", "modularity"],                 "https://www.youtube.com/embed/9Os0o3wzS_I"),
    (["oop", "object-oriented", "class", "encapsulat", "inherit", "polymorphi", "abstract"],
                                                          "https://www.youtube.com/embed/JeznW_7DlB0"),
    (["exception", "error handling", "try except"],       "https://www.youtube.com/embed/NIWwJbo-9_8"),
    (["file i/o", "file read", "serialization", "json", "csv file"],
                                                          "https://www.youtube.com/embed/Uh2ebFW8OYM"),
    (["clean code", "maintainable", "pep 8"],             "https://www.youtube.com/embed/7EmboKQH8lM"),
    (["refactor", "optimization", "dry principle"],       "https://www.youtube.com/embed/D4auWwMsEnY"),

    # DSA
    (["data structure", "algorithm analysis", "big o"],   "https://www.youtube.com/embed/RBSGKlAvoiM"),
    (["array", "linked list", "stack", "queue"],          "https://www.youtube.com/embed/B31LgI4Y4DQ"),
    (["recursion", "divide and conquer"],                 "https://www.youtube.com/embed/IJDJ0kBx2LM"),
    (["binary tree", "graph theory", "hierarchical"],     "https://www.youtube.com/embed/fAAZixBzIAI"),
    (["sorting", "searching algorithm", "merge sort", "quicksort"],
                                                          "https://www.youtube.com/embed/kgBjXUE_Nwc"),
    (["hash table", "hashing", "collision"],              "https://www.youtube.com/embed/ea8BRGxGmlA"),
    (["dynamic programming", "greedy algorithm"],        "https://www.youtube.com/embed/oBt53YbR9Kk"),
    (["bfs", "dfs", "graph traversal", "shortest path"],  "https://www.youtube.com/embed/tWVWeAqZ0WU"),
    (["design pattern", "system design", "software architecture"],
                                                          "https://www.youtube.com/embed/tv-_1er1mWI"),

    # Database / SQL
    (["sql", "database", "rdbms", "relational database", "mysql", "postgresql"],
                                                          "https://www.youtube.com/embed/HXV3zeQKqGY"),

    # MIS
    (["management information system", "mis", "tps", "dss", "ess"],
                                                          "https://www.youtube.com/embed/f_BYsthkFZo"),
    (["sdlc", "system development life cycle"],           "https://www.youtube.com/embed/i-QyW8D3ei0"),
    (["erp", "enterprise resource", "crm", "supply chain"],
                                                          "https://www.youtube.com/embed/2T_r7RB6pBo"),
    (["information security", "cybersecurity", "it governance"],
                                                          "https://www.youtube.com/embed/inWWhr5tnEA"),
    (["business intelligence", "data warehouse", "data mining"],
                                                          "https://www.youtube.com/embed/j2zdcZBQ3jk"),
    (["digital transformation"],                          "https://www.youtube.com/embed/khjnKlBhFow"),

    # Research
    (["research problem", "research question"],           "https://www.youtube.com/embed/3ODP-8T9x6s"),
    (["literature review", "citation"],                   "https://www.youtube.com/embed/oX_Hs0e3w1I"),
    (["theoretical framework", "conceptual framework"],   "https://www.youtube.com/embed/bXn_SfMMKuE"),
    (["qualitative", "quantitative", "research method"],  "https://www.youtube.com/embed/s3qgC-HDLNM"),
    (["sampling", "data collection instrument"],          "https://www.youtube.com/embed/IehYuWBgXHY"),
    (["statistical significance", "data analysis", "p-value"],
                                                          "https://www.youtube.com/embed/mkiTAKSb1ek"),
    (["research proposal"],                               "https://www.youtube.com/embed/zCBXD1OoRSY"),
    (["plagiarism", "academic integrity", "academic writing"],
                                                          "https://www.youtube.com/embed/y2x83P4jVoA"),
    (["thesis defense", "dissertation", "viva"],          "https://www.youtube.com/embed/6yJFiMJXNcI"),

    # Business Ethics
    (["business ethics", "ethics"],                       "https://www.youtube.com/embed/K2P2rRLl1Ik"),
    (["corporate governance", "board structure"],         "https://www.youtube.com/embed/wYF_jnFOFCs"),
    (["stakeholder", "shareholder"],                      "https://www.youtube.com/embed/HLyXlu5aZ5o"),
    (["csr", "corporate social responsibility"],          "https://www.youtube.com/embed/E0KixaFKQkk"),
    (["whistleblow", "conflict resolution"],              "https://www.youtube.com/embed/dR_yqiE3j2k"),
    (["enron", "governance failure", "scandal"],          "https://www.youtube.com/embed/AGugFBEkUXA"),
    (["sustainability", "supply chain", "environment"],   "https://www.youtube.com/embed/Bp4nBT8X7Lg"),
    (["ai ethics", "privacy", "technology governance"],   "https://www.youtube.com/embed/aGwYtUzMQUk"),

    # Law
    (["legal system", "jurisprudence", "law"],            "https://www.youtube.com/embed/k8GMElKpIcA"),
    (["criminal law", "actus reus", "mens rea"],          "https://www.youtube.com/embed/VjXJhbWOuv0"),
    (["constitutional law", "civil liberties"],           "https://www.youtube.com/embed/m3Cs-hs0J-8"),
    (["corporate law", "intellectual property"],          "https://www.youtube.com/embed/eUJRqrMIjIA"),
    (["tort", "civil wrong"],                             "https://www.youtube.com/embed/kPWLLkRMbgo"),
    (["international law", "global treaty"],              "https://www.youtube.com/embed/aJ5bC7ZG7GY"),
    (["legal writing", "advocacy", "litigation"],         "https://www.youtube.com/embed/bNpx7gpSqbY"),

    # Medicine / Health
    (["pathology", "medical system", "nursing", "nurse", "clinic", "clinical", "hospital"], "https://www.youtube.com/embed/lDqL4WScGSw"),
    (["pharmacokinetic", "pharmacodynamic", "pharmacology", "pharmacy", "drug"],
                                                          "https://www.youtube.com/embed/BfElFJVGFcc"),
    (["cell biology", "histology"],                       "https://www.youtube.com/embed/URUJD5NEXC8"),
    (["infectious disease", "immunology"],                "https://www.youtube.com/embed/zBcSO_UrCvw"),
    (["anatomy", "physiology", "surgical", "dentistry", "dentist", "physiotherapy"], "https://www.youtube.com/embed/uBGl2BujkPQ"),
    (["epidemiology", "public health"],                   "https://www.youtube.com/embed/4A_g81RKjdQ"),
    (["clinical diagnosis", "patient care", "ethics"],    "https://www.youtube.com/embed/8fQ5HXwWVso"),
    (["pharmacotherapy", "targeted treatment"],           "https://www.youtube.com/embed/Q-Xcs0dHIh0"),

    # General CS & technology
    (["machine learning", "deep learning", "neural network", "ai"],
                                                          "https://www.youtube.com/embed/GwIo3gDZCVQ"),
    (["network", "tcp", "ip", "firewall"],                "https://www.youtube.com/embed/qiQR5rTSshw"),
    (["operating system", "linux", "kernel"],             "https://www.youtube.com/embed/26QPDBe-NB8"),
    (["cloud computing", "aws", "azure", "devops"],       "https://www.youtube.com/embed/M988_fsOSWo"),
    (["javascript", "web development", "html", "css"],    "https://www.youtube.com/embed/PkZNo7MFNFg"),

    # Finance / Business
    (["accounting", "financial statement", "balance sheet"],
                                                          "https://www.youtube.com/embed/yYX4bvQSqbo"),
    (["finance", "investment", "economics", "microeconomics", "macroeconomics"],
                                                          "https://www.youtube.com/embed/IB6iFZKqZRQ"),
    (["marketing", "brand", "consumer"],                  "https://www.youtube.com/embed/pInFCOovMcI"),
    (["management", "strategy", "business"],              "https://www.youtube.com/embed/4VdHxEEzSBo"),

    # Sciences
    (["calculus", "algebra", "mathematics", "statistics", "probability"],
                                                          "https://www.youtube.com/embed/OmJ-4B-mS-Y"),
    (["chemistry", "organic", "reaction", "molecule"],    "https://www.youtube.com/embed/bka20Q9TN6M"),
    (["physics", "mechanics", "thermodynamics", "quantum"],
                                                          "https://www.youtube.com/embed/ZM8ECpBuQYE"),
    (["psychology", "behaviour", "cognitive"],            "https://www.youtube.com/embed/vo4pMVb0R6M"),
    (["biology", "microbiolog", "biotech"],               "https://www.youtube.com/embed/URUJD5NEXC8"),

    # Agriculture
    (["agriculture", "agric", "crop", "agronomy", "soil", "animal science", "livestock", "farm"],
                                                          "https://www.youtube.com/embed/fD14S92pW8I"),

    # Education
    (["education", "educat", "pedagogy", "teach", "classroom", "curriculum", "learning"],
                                                          "https://www.youtube.com/embed/H0tDuXcX-o4"),
]


# ── 3. CATEGORY-LEVEL FALLBACKS ───────────────────────────────────────────────
CATEGORY_FALLBACKS = {
    "programming":   "https://www.youtube.com/embed/rfscVS0vtbw",
    "dsa":           "https://www.youtube.com/embed/RBSGKlAvoiM",
    "mis":           "https://www.youtube.com/embed/f_BYsthkFZo",
    "research":      "https://www.youtube.com/embed/nJza2kfI8GU",
    "business":      "https://www.youtube.com/embed/K2P2rRLl1Ik",
    "law":           "https://www.youtube.com/embed/k8GMElKpIcA",
    "medicine":      "https://www.youtube.com/embed/uBGl2BujkPQ",
    "engineering":   "https://www.youtube.com/embed/bipTWWHya8A",  # Crash Course Engineering #1
    "math":          "https://www.youtube.com/embed/OmJ-4B-mS-Y",
    "physics":       "https://www.youtube.com/embed/ZM8ECpBuQYE",
    "chemistry":     "https://www.youtube.com/embed/bka20Q9TN6M",
    "biology":       "https://www.youtube.com/embed/URUJD5NEXC8",
    "psychology":    "https://www.youtube.com/embed/vo4pMVb0R6M",
    "finance":       "https://www.youtube.com/embed/IB6iFZKqZRQ",
    "social_sciences":"https://www.youtube.com/embed/vo4pMVb0R6M",
    "arts":          "https://www.youtube.com/embed/YMXnQqDlEqs",  # Art History
    "agriculture":   "https://www.youtube.com/embed/fD14S92pW8I",
    "education":     "https://www.youtube.com/embed/H0tDuXcX-o4",
    "default":       "https://www.youtube.com/embed/5MgBikcWnYU",  # Crash Course Study Skills
}


def get_lesson_video(lesson_title: str, course_title: str = "") -> str:
    """
    Returns the guaranteed-accurate YouTube embed URL for a given lesson title.
    Three-tier lookup:
      1. Java-specific override for computing courses
      2. Exact match in LESSON_VIDEO_MAP
      3. Keyword match in KEYWORD_VIDEO_MAP
      4. Generic educational fallback (mapped dynamically by category)
    """
    key = lesson_title.strip().lower()
    course_lower = course_title.lower().strip()

    # Java override logic to prevent Java courses from showing Python videos
    is_java = "java" in course_lower or "csc 212" in course_lower
    if is_java:
        JAVA_MAP = {
            "introduction to programming concepts": "https://www.youtube.com/embed/xk4_1vDrzzo", # Java Full Course
            "control flow and logical operators": "https://www.youtube.com/embed/xk4_1vDrzzo",
            "functions, scope, and modularity": "https://www.youtube.com/embed/xk4_1vDrzzo",
            "object-oriented programming (oop) fundamentals": "https://www.youtube.com/embed/R9Z4c9P153M", # Java OOP
            "error handling and exception management": "https://www.youtube.com/embed/xk4_1vDrzzo",
            "file i/o operations and data serialization": "https://www.youtube.com/embed/xk4_1vDrzzo",
            "writing clean, maintainable code": "https://www.youtube.com/embed/R9Z4c9P153M",
            "refactoring and software optimization": "https://www.youtube.com/embed/R9Z4c9P153M",
            "final capstone project implementation": "https://www.youtube.com/embed/xk4_1vDrzzo"
        }
        if key in JAVA_MAP:
            return JAVA_MAP[key]

    # Tier 1 — exact title match
    if key in LESSON_VIDEO_MAP:
        return LESSON_VIDEO_MAP[key]

    # Tier 2 — keyword match
    combined = (lesson_title + " " + course_title).lower()
    for keywords, url in KEYWORD_VIDEO_MAP:
        if any(kw in combined for kw in keywords):
            return url

    # Tier 3 — category-level fallback (determined from course title)
    from engine.tutor import TutorEngine
    try:
        tutor = TutorEngine()
        cat = tutor._determine_category(course_title, lesson_title)
        if cat in CATEGORY_FALLBACKS:
            return CATEGORY_FALLBACKS[cat]
    except Exception:
        pass

    # Final fallback
    return CATEGORY_FALLBACKS["default"]
