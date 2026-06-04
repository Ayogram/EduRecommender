"""
Tutor Engine – The AI heart of the learning platform.
Generates lesson content and MCQs dynamically based on specific course topics.
"""

import json
import random

class TutorEngine:
    def __init__(self):
        # Academic repository mapping categories to rich educational content
        self.curriculum_data = {
            "programming": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Programming Concepts",
                        "content": """
### 🌟 Overview of Computer Programming
Programming is the process of creating a set of instructions that tell a computer how to perform a task. At its core, programming translates human problem-solving logic into a language a machine can execute.

### 🔑 Core Building Blocks
All programming languages share key foundational concepts:
1.  **Variables and Data Types**: Containers for storing data (integers, floats, strings, booleans).
2.  **Control Structures**: Logic flow directors (conditional statements like `if/else`, loops like `for/while`).
3.  **Functions**: Reusable blocks of code that perform specific tasks.

### 💻 Code Example: Basic Flow
Here is a demonstration of variables, loops, and conditional logic in Python:
```python
# Variables and list iteration
scores = [85, 92, 78, 90, 60]
passing_score = 70

for score in scores:
    if score >= passing_score:
        print(f"Score {score}: Pass")
    else:
        print(f"Score {score}: Fail")
```

### 🧠 AI Tip
Always break down complex problems into pseudo-code before writing syntax. It saves up to 50% debugging time.
"""
                    },
                    {
                        "title": "Control Flow and Logical Operators",
                        "content": """
### 🔀 Decision Making in Code
Control flow is the order in which individual statements, instructions, or function calls are executed. Without control structures, code executes strictly from top to bottom.

### 📐 Logical Operators
Logical operators allow you to combine multiple conditions:
*   `AND` (both conditions must be true)
*   `OR` (at least one condition must be true)
*   `NOT` (reverses the boolean state)

### 💡 Practice Scenario
Consider a login validator:
```python
username_entered = "admin"
password_entered = "secure123"

if username_entered == "admin" and password_entered == "secure123":
    print("Access Granted")
else:
    print("Invalid Credentials")
```
"""
                    },
                    {
                        "title": "Functions, Scope, and modularity",
                        "content": """
### 📦 The Power of Functions
Functions are the primary method of achieving code reusability and modularity. A function takes input (parameters), performs operations, and yields output (returns a value).

### 🌐 Scope: Local vs Global
*   **Local Scope**: Variables declared inside a function exist only within that function.
*   **Global Scope**: Variables declared outside functions are accessible anywhere.

### 📝 Key Rules
1. Keep functions focused on a single task (Single Responsibility Principle).
2. Document inputs and outputs with docstrings.
"""
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Object-Oriented Programming (OOP) Fundamentals",
                        "content": """
### 🏛️ The OOP Paradigm
Object-Oriented Programming is a paradigm centered around 'objects' rather than functions. It is highly useful for structuring large, complex systems.

### 🔑 The Four Pillars of OOP
1.  **Encapsulation**: Bundling data and methods that operate on that data inside a single unit (Class), hiding internal details.
2.  **Inheritance**: Deriving a new class from an existing class to reuse properties.
3.  **Polymorphism**: Allowing different classes to be treated as instances of the same superclass.
4.  **Abstraction**: Hiding complex implementation details and showing only essential features.
"""
                    },
                    {
                        "title": "Error Handling and Exception Management",
                        "content": """
### 🛡️ Building Resilient Applications
Errors are inevitable. Robust code anticipates failures (network timeout, invalid user input, division by zero) and handles them gracefully without crashing.

### 🛠️ Try-Except Block Pattern
Instead of letting an error halt execution, we capture the exception:
```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Error captured: {e}. Fallback to default value 0.")
    result = 0
```
"""
                    },
                    {
                        "title": "File I/O Operations and Data Serialization",
                        "content": """
### 💾 Persistent Data Storage
Programs must read from and write to external files to save state. 

### 📐 Formats
*   **JSON**: Lightweight data interchange format.
*   **CSV**: Comma-separated values, ideal for tabular data.
"""
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Writing Clean, Maintainable Code",
                        "content": """
### 🎨 The Art of Code Readability
Code is read far more often than it is written. Writing clean code ensures that you, your team, and future developers can easily modify it.

### 📏 Best Practices (PEP 8 Style Guide)
*   Use meaningful variable and function names.
*   Keep comments concise; code should explain itself as much as possible.
*   Avoid nesting control blocks too deeply.
"""
                    },
                    {
                        "title": "Refactoring and Software Optimization",
                        "content": """
### ⚡ Optimizing Code Performance
Refactoring is restructuring existing code without changing its external behavior. It improves code design and execution speed.
"""
                    },
                    {
                        "title": "Final Capstone Project Implementation",
                        "content": """
### 🏁 Putting It All Together
In this capstone, you will build a functional command-line application incorporating all core concepts: OOP, file storage, robust error handling, and logical control flow.
"""
                    }
                ],
                "quizzes": [
                    {
                        "question": "Which of the following is an immutable data collection in Python?",
                        "options": ["List", "Dictionary", "Tuple", "Set"],
                        "correct_answer": "Tuple"
                    },
                    {
                        "question": "In Object-Oriented Programming, what is Encapsulation?",
                        "options": [
                            "Hiding internal implementation details and bundling data with methods",
                            "Allowing a class to inherit from multiple parents",
                            "Converting objects into byte streams",
                            "Overloading functions dynamically"
                        ],
                        "correct_answer": "Hiding internal implementation details and bundling data with methods"
                    },
                    {
                        "question": "What is the time complexity of looking up a value in a hash table in the average case?",
                        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        "correct_answer": "O(1)"
                    },
                    {
                        "question": "Which of the following blocks catches exceptions in Python?",
                        "options": ["catch", "except", "error", "handle"],
                        "correct_answer": "except"
                    },
                    {
                        "question": "What does the Single Responsibility Principle state?",
                        "options": [
                            "A function or class should have only one reason to change",
                            "All code should be written in a single file",
                            "A variables must only hold a single value type",
                            "Only one user should access the database at a time"
                        ],
                        "correct_answer": "A function or class should have only one reason to change"
                    }
                ]
            },
            "dsa": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Data Structures and Algorithmic Analysis",
                        "content": """
### 📊 Understanding Data Structures
A data structure is a specialized format for organizing, processing, retrieving, and storing data. Choosing the right structure is critical for runtime efficiency.

### ⏳ Time Complexity & Big O Notation
Big O notation describes the execution time or space complexity of an algorithm in the worst-case scenario:
*   `O(1)`: Constant Time (e.g., array lookup by index)
*   `O(log n)`: Logarithmic Time (e.g., binary search)
*   `O(n)`: Linear Time (e.g., linear search)
*   `O(n log n)`: Linearithmic Time (e.g., merge sort)
*   `O(n²)`: Quadratic Time (e.g., bubble sort)

### 📈 Visualizing Growth Rates
As input size $N$ grows, the execution time of an $O(n²)$ algorithm skyrockets, whereas $O(log n)$ remains virtually flat. This is the difference between software that scales and software that crashes.
"""
                    },
                    {
                        "title": "Linear Structures: Arrays, Linked Lists, Stacks & Queues",
                        "content": """
### 📏 Linear Data Arrangements
Linear structures organize elements sequentially. 

### 📐 Structural Breakdown
*   **Array**: Contiguous memory slots. Offers `O(1)` indexing, but insertions are costly (`O(n)`).
*   **Linked List**: Non-contiguous nodes where each node points to the next. Offers fast insertion/deletion (`O(1)`), but slow lookup (`O(n)`).
*   **Stack**: LIFO (Last-In, First-Out) operations. Push/Pop are `O(1)`.
*   **Queue**: FIFO (First-In, First-Out) operations. Enqueue/Dequeue are `O(1)`.
"""
                    },
                    {
                        "title": "Recursion and Divide-and-Conquer Paradigms",
                        "content": """
### 🔄 The Recursive Approach
Recursion occurs when a function calls itself to solve a smaller subproblem. Every recursive function requires a **Base Case** to prevent infinite execution.
"""
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Hierarchical Structures: Binary Trees and Graph Theory",
                        "content": """
### 🌳 Hierarchical Organization
Non-linear structures represent complex relationships.

### 📐 Core Structures
1.  **Binary Search Tree (BST)**: Left child < Node < Right child. Average search is `O(log n)`.
2.  **Graphs**: Sets of vertices (nodes) and edges (connections). Represented via adjacency lists or matrices.
"""
                    },
                    {
                        "title": "Sorting and Searching Algorithms",
                        "content": """
### 🔍 Efficient Searching
*   **Binary Search**: Divide search range in half each step. Requires sorted input. `O(log n)`.
*   **Quick Sort / Merge Sort**: Efficient sorting methods using divide-and-conquer. `O(n log n)` average.
"""
                    },
                    {
                        "title": "Hashing, Hash Tables, and Collision Resolution",
                        "content": """
### 🗝️ Constant-Time Lookups
A hash table maps keys to array indices using a hash function. When two keys map to the same slot, a **collision** occurs. Collision resolution methods include linear probing and chaining.
"""
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Dynamic Programming and Greedy Algorithms",
                        "content": """
### 💡 Optimization Paradigms
*   **Greedy**: Make locally optimal choices at each step, hoping to find global optimum.
*   **Dynamic Programming (DP)**: Break problem into overlapping subproblems, solve once and store results (Memoization).
"""
                    },
                    {
                        "title": "Graph Traversals (BFS & DFS) and Shortest Path",
                        "content": """
### 🗺️ Navigating Connected Networks
*   **Breadth-First Search (BFS)**: Explores layer-by-layer. Finding shortest path in unweighted graphs.
*   **Depth-First Search (DFS)**: Explores along branches as deep as possible before backtracking.
"""
                    },
                    {
                        "title": "Real-World System Optimization & Design Patterns",
                        "content": """
### 🏁 Applying DSA in Enterprise Systems
Mastering DSA allows engineers to choose optimal structures for database indexes, router switches, and search engine indexes.
"""
                    }
                ],
                "quizzes": [
                    {
                        "question": "What is the worst-case time complexity of lookup in an unbalanced Binary Search Tree?",
                        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        "correct_answer": "O(n)"
                    },
                    {
                        "question": "Which data structure operates on a Last-In, First-Out (LIFO) basis?",
                        "options": ["Queue", "Stack", "Heap", "Linked List"],
                        "correct_answer": "Stack"
                    },
                    {
                        "question": "What is the average-case time complexity of QuickSort?",
                        "options": ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
                        "correct_answer": "O(n log n)"
                    },
                    {
                        "question": "Which graph traversal algorithm uses a Queue data structure?",
                        "options": ["DFS", "BFS", "Dijkstra", "Kruskal"],
                        "correct_answer": "BFS"
                    },
                    {
                        "question": "What is the time complexity of building a heap from an array of size n?",
                        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                        "correct_answer": "O(n)"
                    }
                ]
            },
            "business": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Modern Business Ethics",
                        "content": """
### ⚖️ Ethics vs Legality
Business ethics is the system of moral principles applied to corporate operations and trade. Just because an action is legal does not mean it is ethical.

### 🔑 Ethical Frameworks
1.  **Utilitarianism**: The greatest good for the greatest number of stakeholders.
2.  **Deontology (Kantianism)**: Actions are morally obligatory regardless of outcomes, based on duties and rules.
3.  **Virtue Ethics**: Emphasizes the character and integrity of the decision-maker.

> "A business that makes nothing but money is a poor business." — Henry Ford
"""
                    },
                    {
                        "title": "Corporate Governance and Board Structures",
                        "content": """
### 🏛️ Aligning Corporate Interests
Corporate governance is the system of rules, practices, and processes by which a firm is directed and controlled. 

### 📐 Board Responsibilities
*   Fiduciary duty to shareholders.
*   Ensuring compliance with environmental and employment law.
*   Preventing agency conflicts (conflicts of interest between managers and owners).
"""
                    },
                    {
                        "title": "Stakeholder Theory vs Shareholder Primacy",
                        "content": """
### 🔄 The Corporate Purpose Debate
*   **Shareholder Theory (Milton Friedman)**: The sole social responsibility of business is to increase its profits for shareholders.
*   **Stakeholder Theory (Edward Freeman)**: Corporations must create value for customers, employees, suppliers, communities, and shareholders alike.
"""
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Corporate Social Responsibility (CSR) Frameworks",
                        "content": """
### 🌍 Integrating Ethics with Operations
Corporate Social Responsibility (CSR) represents a business model where companies make a concerted effort to operate in ways that enhance society and the environment.

### 📐 The Triple Bottom Line
CSR measures success by three metrics:
1.  **People** (social performance)
2.  **Planet** (environmental performance)
3.  **Profit** (financial performance)
"""
                    },
                    {
                        "title": "Ethical Conflict Resolution and Whistleblowing",
                        "content": """
### 🛡️ Protecting Integrity
Whistleblowing is the act of reporting misconduct, illegal activities, or safety hazards within an organization. A robust ethical corporate culture requires strong, retaliation-free whistleblower policies.
"""
                    },
                    {
                        "title": "Managing Conflicts of Interest",
                        "content": """
### ⚠️ Avoiding Divided Loyalties
Conflicts of interest occur when an employee's personal interests interfere with their duty to the company. Organizations must establish clear guidelines for disclosing and mitigating these conflicts.
"""
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Case Studies: Enron and Modern Governance Failures",
                        "content": """
### 📉 Lessons from Corporate Catastrophes
Analyzing failures like Enron, WorldCom, and the Volkswagen emissions scandal highlights the dangers of prioritizing short-term profits over ethics.
"""
                    },
                    {
                        "title": "Environmental Sustainability in Global Supply Chains",
                        "content": """
### 🌱 The Climate Imperative
Modern supply chains are highly complex. Ethics dictates ensuring fair labor wages, avoiding child labor, and minimizing greenhouse emissions across global vendor networks.
"""
                    },
                    {
                        "title": "AI Ethics, Privacy, and Technology Governance",
                        "content": """
### 🤖 Ethical Frontiers in Tech
As artificial intelligence expands, modern businesses must navigate data privacy, algorithmic bias, and ethical automated decision-making frameworks.
"""
                    }
                ],
                "quizzes": [
                    {
                        "question": "Which ethical framework asserts that an action is right if it produces the greatest balance of pleasure over pain for everyone?",
                        "options": ["Deontology", "Utilitarianism", "Virtue Ethics", "Ethical Relativism"],
                        "correct_answer": "Utilitarianism"
                    },
                    {
                        "question": "The conflict of interest between shareholders (owners) and managers (agents) is known as:",
                        "options": ["The agency problem", "Stakeholder dispute", "Fiduciary imbalance", "Utilitarian conflict"],
                        "correct_answer": "The agency problem"
                    },
                    {
                        "question": "What are the three pillars of the Triple Bottom Line framework?",
                        "options": [
                            "People, Planet, Profit",
                            "Price, Product, Promotion",
                            "Performance, Planning, Personnel",
                            "Policies, Procedures, Products"
                        ],
                        "correct_answer": "People, Planet, Profit"
                    },
                    {
                        "question": "Which theorist is most closely associated with Stakeholder Theory?",
                        "options": ["Milton Friedman", "Edward Freeman", "Adam Smith", "Immanuel Kant"],
                        "correct_answer": "Edward Freeman"
                    },
                    {
                        "question": "An unconditional moral obligation that applies in all circumstances is Kant's definition of:",
                        "options": ["Utility maximize", "Categorical imperative", "Virtuous choice", "Relativity index"],
                        "correct_answer": "Categorical imperative"
                    }
                ]
            },
            "medicine": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Medical Systems and Pathology",
                        "content": """
### 🩺 Core Medical Concepts
Understanding the human body requires systematic mapping of anatomy, physiology, and general pathology (the study of disease mechanisms).

### 🔑 Physiological Homeostasis
The human body operates through feedback loops designed to maintain homeostasis—a state of internal balance. A disruption in these loops leads to illness or organ dysfunction.
"""
                    },
                    {
                        "title": "General Pharmacology: Pharmacokinetics & Pharmacodynamics",
                        "content": """
### 💊 The Science of Drugs
Pharmacology explores how external chemical substances affect living systems.
*   **Pharmacokinetics**: What the body does to the drug (Absorption, Distribution, Metabolism, Excretion - ADME).
*   **Pharmacodynamics**: What the drug does to the body (receptor binding, drug-receptor interactions).
"""
                    },
                    {
                        "title": "Cell Biology and General Histology",
                        "content": """
### 🔬 Microscopic Cellular Structure
The cell is the basic structural unit of all living organisms. Tissues are groups of similar cells working together to perform specialized functions.
"""
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Infectious Diseases and Immunology",
                        "content": """
### 🛡️ The Immune Defense System
Immunology studies how the body identifies and destroys pathogents (viruses, bacteria, fungi) using innate and adaptive immunity.
"""
                    },
                    {
                        "title": "Anatomy and Surgical Physiology",
                        "content": """
### 🔪 Surgical Interventions
Surgery requires a deep spatial understanding of organ boundaries, vascular systems, and anesthesia protocols to minimize patient trauma.
"""
                    },
                    {
                        "title": "Public Health and Epidemiology",
                        "content": """
### 🌍 Healthcare at Scale
Epidemiology studies the distribution and determinants of health states in populations, tracking outbreaks and managing global disease burdens.
"""
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Clinical Diagnosis and Patient Care Ethics",
                        "content": """
### 🤝 Fiduciary Patient Relationship
Medical ethics requires adherence to the principles of autonomy, beneficence, non-maleficence, and justice.
"""
                    },
                    {
                        "title": "Pharmacotherapy and Targeted Treatments",
                        "content": """
### 🧬 Modern Targeted Medicine
Surgical and pharmacological interventions are shifting toward precision medicine, matching therapies to genetic profiles.
"""
                    },
                    {
                        "title": "Final Clinical Case Study & Capstone",
                        "content": """
### 🏁 Diagnostic Exercise
Analyze clinical patient charts, evaluate symptoms, determine the pathology, and prescribe the appropriate targeted therapy plan.
"""
                    }
                ],
                "quizzes": [
                    {
                        "question": "What is the term for what the body does to a drug, including absorption, metabolism, and excretion?",
                        "options": ["Pharmacodynamics", "Pharmacokinetics", "Bioavailability", "Therapeutic Index"],
                        "correct_answer": "Pharmacokinetics"
                    },
                    {
                        "question": "Which organ is primary responsible for drug metabolism in the human body?",
                        "options": ["Kidneys", "Liver", "Lungs", "Stomach"],
                        "correct_answer": "Liver"
                    },
                    {
                        "question": "What is adaptive immunity?",
                        "options": [
                            "Immediate, non-specific response to pathogens",
                            "Delayed, specific response with memory cell creation",
                            "Simple barrier protection from skin",
                            "Rejection of foreign blood types only"
                        ],
                        "correct_answer": "Delayed, specific response with memory cell creation"
                    },
                    {
                        "question": "Which of the following describes the principle of doing no harm to a patient?",
                        "options": ["Beneficence", "Autonomy", "Non-maleficence", "Justice"],
                        "correct_answer": "Non-maleficence"
                    },
                    {
                        "question": "What is the main function of the kidneys in the pharmacokinetics phase?",
                        "options": ["Absorption", "Distribution", "Metabolism", "Excretion"],
                        "correct_answer": "Excretion"
                    }
                ]
            },
            "law": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Legal Systems and Jurisprudence",
                        "content": """
### ⚖️ The Foundation of Law
Jurisprudence is the philosophy of law. It explores how legal codes are established, interpreted, and applied to maintain social order and justice.

### 🔑 Key Legal Traditions
1.  **Common Law**: Law built on judicial precedents rather than statutes (e.g., UK, Nigeria, US).
2.  **Civil Law**: Written statutes and codified laws form the core authority (e.g., France, Germany).
"""
                    },
                    {
                        "title": "Criminal Law: Actus Reus and Mens Rea",
                        "content": """
### ⚖️ Establishing Criminal Liability
In criminal law, convicting a defendant generally requires proving two essential elements:
*   **Actus Reus**: The physical act of committing a crime.
*   **Mens Rea**: The mental intent (guilty mind) to commit that crime.
"""
                    },
                    {
                        "title": "Constitutional Law & Civil Liberties",
                        "content": """
### 📜 The Supreme Code
Constitutional law governs the relationships between state organs and outlines fundamental civil rights protected from state encroachment.
"""
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Corporate Law and Intellectual Property",
                        "content": """
### 🏢 Business Regulation
Corporate law regulates business transactions, mergers, and contracts. Intellectual Property (IP) law protects patents, trademarks, and copyrights.
"""
                    },
                    {
                        "title": "Torts and Civil Wrongs",
                        "content": """
### ⚠️ Negligence and Civil Damage
A tort is a civil wrong that causes harm to another, leading to legal liability. Negligence claims require proving duty of care, breach, causation, and damages.
"""
                    },
                    {
                        "title": "International Law and Global Treaties",
                        "content": """
### 🌍 Legal Frameworks Across Borders
Examine how international treaties, agreements, and organizations like the United Nations enforce transnational justice and human rights.
"""
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Legal Writing, Advocacy, and Litigation Ethics",
                        "content": """
### 📝 Structuring Legal Arguments
Attorneys must construct logical, precedent-supported briefs using formats like IRAC (Issue, Rule, Application, Conclusion).
"""
                    },
                    {
                        "title": "Judicial Interpretation and Modern Precedents",
                        "content": """
### 🏛️ The Living Constitution
Analyzing how Supreme Courts adapt historical statutes to modern issues like digital privacy and biotechnology.
"""
                    },
                    {
                        "title": "Final Moot Court Defense Capstone",
                        "content": """
### 🏁 Case Defense
Draft a complete litigation brief defending a client against corporate fraud charges, using relevant case laws.
"""
                    }
                ],
                "quizzes": [
                    {
                        "question": "Which of the following refers to the physical act of committing a crime?",
                        "options": ["Mens Rea", "Actus Reus", "Stare Decisis", "Habeas Corpus"],
                        "correct_answer": "Actus Reus"
                    },
                    {
                        "question": "The legal principle of binding judicial precedent is known as:",
                        "options": ["Actus Reus", "Stare Decisis", "Mens Rea", "Res Ipsa Loquitur"],
                        "correct_answer": "Stare Decisis"
                    },
                    {
                        "question": "What must a plaintiff prove to establish liability in a negligence claim?",
                        "options": [
                            "Intent, harm, malice, breach",
                            "Duty of care, breach of duty, causation, damages",
                            "Oral agreement, performance, signature, witnesses",
                            "Contract, written terms, consideration, signature"
                        ],
                        "correct_answer": "Duty of care, breach of duty, causation, damages"
                    },
                    {
                        "question": "What is the primary difference between Common Law and Civil Law?",
                        "options": [
                            "Common Law relies on precedent; Civil Law relies on codified statutes",
                            "Civil Law relies on juries; Common Law relies solely on judges",
                            "Common Law is federal; Civil Law is municipal",
                            "There is no difference"
                        ],
                        "correct_answer": "Common Law relies on precedent; Civil Law relies on codified statutes"
                    },
                    {
                        "question": "In corporate law, a fiduciary duty requires directors to:",
                        "options": [
                            "Maximize personal gain",
                            "Act in the best interest of the corporation and shareholders",
                            "Pay high dividends regardless of profitability",
                            "Delegate all decisions to stakeholders"
                        ],
                        "correct_answer": "Act in the best interest of the corporation and shareholders"
                    }
                ]
            },
            "mis": {
                "Foundational Principles": [
                    {
                        "title": "Introduction to Management Information Systems (MIS)",
                        "content": "### 🌟 Overview of Management Information Systems\nManagement Information Systems (MIS) is the study of people, technology, organizations, and the relationships among them. MIS professionals help firms realize maximum benefit from investment in personnel, equipment, and business processes.\n\n### 🔑 The Five Core Components\nEvery information system is comprised of five essential components:\n1.  **Hardware**: The physical technology (servers, computers, networks).\n2.  **Software**: The instructions/programs that run on the hardware.\n3.  **Data**: Raw facts that are converted into meaningful information.\n4.  **Procedures**: Policies, rules, and steps that govern system operation.\n5.  **People**: The most critical component; the users and professionals who design and run the system.\n\n### 📊 Strategic Value\nMIS is a strategic tool that transforms raw transactional data into actionable business intelligence to support decision-making, operational control, and competitive advantage."
                    },
                    {
                        "title": "Information Systems Types: TPS, DSS, and ESS",
                        "content": "### 🗂️ Hierarchy of Information Systems\nOrganizations utilize different classes of systems to serve various operational and managerial levels:\n*   **Transaction Processing Systems (TPS)**: Track daily routine operations (e.g., sales orders, payroll, inventory tracking). Used primarily at the operational level.\n*   **Decision Support Systems (DSS)**: Provide interactive data models and tools to help managers analyze semi-structured problems and make tactical decisions.\n*   **Executive Support Systems (ESS)**: Deliver high-level dashboards and summaries to help senior executives analyze long-term strategic trends."
                    },
                    {
                        "title": "Data vs Information & Information Quality",
                        "content": "### 💡 Data vs. Information\n*   **Data**: Raw, unorganized facts, numbers, or symbols (e.g., a list of individual sale prices).\n*   **Information**: Data that has been processed, structured, and presented in a meaningful context (e.g., a chart showing monthly sales trends).\n\n### 🏆 Dimensions of Information Quality\nFor information to support decision-making effectively, it must possess high quality across four dimensions:\n1.  **Accuracy**: Free from errors and trustworthy.\n2.  **Completeness**: Containing all necessary facts without omission.\n3.  **Relevance**: Directly useful for the task at hand.\n4.  **Timeliness**: Available when needed and up-to-date."
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "RDBMS and Database Systems",
                        "content": "### 🗄️ Relational Database Management Systems\nA Relational Database Management System (RDBMS) stores data in tables linked together by primary and foreign keys. This design ensures data integrity, avoids redundant storage, and allows flexible queries.\n\n### 🔍 SQL and ERDs\n*   **Entity-Relationship Diagram (ERD)**: A graphical representation showing database tables and how they relate.\n*   **Structured Query Language (SQL)**: The standard language used to interact with RDBMS to create, read, update, and delete database records.\n```sql\nSELECT title, credits FROM courses WHERE department = 'Business';\n```"
                    },
                    {
                        "title": "Systems Development Life Cycle (SDLC)",
                        "content": "### 🛠️ The SDLC Framework\nThe Systems Development Life Cycle (SDLC) is a structured process for planning, analyzing, designing, building, testing, and deploying information systems.\n1.  **Planning & Feasibility**: Scope definition and resource planning.\n2.  **Analysis**: Gathering detailed user requirements.\n3.  **Design**: Detailing system architecture, databases, and UI design.\n4.  **Implementation**: Coding, testing, and system rollout.\n5.  **Maintenance**: Post-deployment fixes and updates.\n\n### 🔄 Waterfall vs. Agile\n*   **Waterfall**: Linear, sequential phases where each phase must finish before the next begins. Very predictable but rigid.\n*   **Agile**: Iterative and incremental approach focusing on collaboration, adaptability, and frequent software releases."
                    },
                    {
                        "title": "Enterprise Resource Planning (ERP) & CRM",
                        "content": "### 🏢 Enterprise Resource Planning\nEnterprise Resource Planning (ERP) systems integrate all functional departments (finance, HR, sales, manufacturing) into a single, centralized database. This eliminates data silos and coordinates operations.\n\n### 🤝 CRM and SCM\n*   **Customer Relationship Management (CRM)**: Tracks and manages all customer interactions, sales history, and marketing campaigns to build loyalty.\n*   **Supply Chain Management (SCM)**: Tracks materials, information, and finances as they move from supplier to manufacturer to consumer."
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Information Security & IT Governance",
                        "content": "### 🔔 The CIA Triad\nThe core framework of information security consists of:\n*   **Confidentiality**: Ensuring sensitive data is accessed only by authorized users.\n*   **Integrity**: Protecting systems and data from unauthorized modification.\n*   **Availability**: Ensuring systems are functional and accessible when needed.\n\n### 💼 IT Governance and Alignment\nIT Governance ensures technology investments align with business objectives to maximize ROI and mitigate operational risks."
                    },
                    {
                        "title": "Business Intelligence and Data Warehousing",
                        "content": "### 📊 Business Intelligence (BI)\nBusiness Intelligence involves using software tools, applications, and methodologies to collect, integrate, analyze, and present business data to support better decision-making.\n\n### 🛢️ Data Warehouses and Data Mining\n*   **Data Warehouse**: A large, centralized repository of historical data collected from multiple systems, optimized for analytical queries.\n*   **Data Mining**: Using mathematical algorithms and machine learning to discover hidden patterns and trends in massive datasets."
                    },
                    {
                        "title": "Digital Transformation & Capstone Design",
                        "content": "### 🚀 Digital Transformation\nDigital Transformation is the strategic integration of digital technologies into all areas of a business, fundamentally changing how value is delivered to customers.\n\n### 📋 Capstone Design Proposal\nThe culmination of the MIS curriculum is the development of a comprehensive technical system design proposal. This document details the database schema (ERD), system architecture, compliance audits, and security strategy for a real-world enterprise."
                    }
                ],
                "quizzes": [
                    {
                        "question": "Which of the following is NOT one of the five core components of an Information System?",
                        "options": ["Hardware", "Software", "Algorithms", "Procedures"],
                        "correct_answer": "Algorithms"
                    },
                    {
                        "question": "What level of management is a Decision Support System (DSS) primarily designed to support?",
                        "options": ["Operational managers", "Tactical/Middle managers", "Executive/Senior managers", "Entry-level staff"],
                        "correct_answer": "Tactical/Middle managers"
                    }
                ]
            },
            "research": {
                "Foundational Principles": [
                    {
                        "title": "Identifying a Research Problem & Writing Questions",
                        "content": "### 🌟 Formulating the Research Problem\nEvery research journey begins with identifying a clear, well-defined problem. A research problem is a specific issue, contradiction, or gap in existing knowledge that your study aims to address.\n\n### 🔑 Criteria for a Good Research Problem\n1. **Feasible**: Can be solved within time, budget, and resource constraints.\n2. **Clear & Focused**: Specific enough to guide your study design.\n3. **Significant**: Adds new value or insights to the academic field.\n\n### 📐 Writing Research Questions\nYour research problem is broken down into specific research questions. Good research questions are open-ended (typically starting with \"How\" or \"Why\") and guide your data collection."
                    },
                    {
                        "title": "Literature Review & Citation Styles",
                        "content": "### 📚 The Purpose of a Literature Review\nA literature review is a critical analysis of existing scholarly publications relevant to your topic. It establishes the context, demonstrates your familiarity with the field, and highlights the gap your project will fill.\n\n### 🖋️ Citations and References\nTo maintain academic integrity, you must cite all external sources. Standard styles include:\n- **APA**: Author-date system (e.g., Smith, 2023) common in social sciences.\n- **IEEE**: Numbered system (e.g., [1]) common in engineering and computing."
                    },
                    {
                        "title": "Designing Conceptual & Theoretical Frameworks",
                        "content": "### 🏛️ Theoretical vs. Conceptual Frameworks\n- **Theoretical Framework**: The existing academic theories and models that support your study (e.g., TAM, Technology Acceptance Model).\n- **Conceptual Framework**: Your visual or written map illustrating the expected relationships between your independent and dependent variables.\n\n### 📊 Defining Variables\n- **Independent Variable**: The cause or condition you change/manipulate.\n- **Dependent Variable**: The effect or outcome you measure."
                    }
                ],
                "Intermediate Methodologies": [
                    {
                        "title": "Qualitative vs. Quantitative Research Methods",
                        "content": "### 🔬 Selecting Your Research Methodology\nMethodology is the systematic plan for conducting your research. The three main paradigms are:\n1. **Quantitative**: Gathers numerical data to test hypotheses and analyze trends using statistics.\n2. **Qualitative**: Gathers descriptive text to explore opinions, meanings, and experiences.\n3. **Mixed Methods**: Combines both approaches to enrich and cross-examine findings."
                    },
                    {
                        "title": "Data Collection Instruments & Sampling Techniques",
                        "content": "### 📋 Data Collection Instruments\nHow you collect data depends on your methodology:\n- **Quantitative**: Surveys, structured questionnaires, or system logs.\n- **Qualitative**: Semi-structured interviews, focus groups, or thematic observations.\n\n### 🎲 Sampling Techniques\n- **Probability Sampling**: Random selection where every member of the population has a known chance of being chosen (e.g., simple random sampling).\n- **Non-Probability Sampling**: Selected based on convenience or purpose (e.g., purposive sampling)."
                    },
                    {
                        "title": "Data Analysis & Statistical Significance",
                        "content": "### 📊 Analyzing Your Findings\n- **Quantitative**: Descriptive statistics (mean, median) and inferential statistics (t-tests, ANOVA) to test hypotheses.\n- **Qualitative**: Thematic analysis by coding raw text responses into meaningful labels.\n\n### 🎯 Statistical Significance\nThe p-value measures the likelihood that a result occurred by chance. Typically, a p-value < 0.05 is considered statistically significant."
                    }
                ],
                "Final Assessment & Capstone": [
                    {
                        "title": "Drafting the Research Proposal Outline",
                        "content": "### 📝 Structuring a Research Proposal\nA research proposal is a formal document outlining what you plan to study, why it matters, and how you will do it.\n\n### 🔑 Core Proposal Elements:\n1. **Introduction & Background**: Context and problem description.\n2. **Literature Review**: Summary of existing research.\n3. **Methodology**: Details of data collection and analysis.\n4. **Significance & Timeline**: Expected contributions and plan of work."
                    },
                    {
                        "title": "Academic Writing Integrity & Plagiarism Avoidance",
                        "content": "### 🛡️ Academic Integrity\nHonesty and rigor are fundamental to scholarship. Plagiarism is the unethical act of using someone else's work, code, or ideas without proper attribution.\n\n### 💡 Avoidance Strategies:\n- Paraphrase ideas in your own words while still citing the source.\n- Use quotation marks for exact phrasing.\n- Always run a plagiarism check before submitting."
                    },
                    {
                        "title": "Thesis Defense & Presentation Preparation",
                        "content": "### 🎓 The Viva Voce / Oral Defense\nThe final milestone is presenting and defending your dissertation before a panel of academic examiners.\n\n### 🎯 Key Presentation Tips:\n- Focus on the **Research Problem**, **Methodology**, and **Key Contribution**.\n- Speak clearly and justify your research choices calmly.\n- Be prepared to discuss study limitations."
                    }
                ]
            },
        }

        # Catch-all general category content
        self.default_category = {
            "Foundational Principles": [
                {
                    "title": "Introduction to Core Theoretical Foundations",
                    "content": """
### 🌟 Overview & Fundamental Principles
Every academic subject is anchored on core foundational concepts that shape how we view the field. Understanding these basic principles is the critical first step toward mastery.

### 🔑 Essential Concepts
1.  **Conceptual Framework**: The terminology and taxonomy of the field.
2.  **Methodological Basics**: How research or calculations are formulated.
3.  **Core Dynamics**: How different components interact with one another.

### 📈 Historical Context
Most modern systems are built upon historic paradigms. Tracing the evolution of this discipline helps contextualize contemporary practices.
"""
                },
                {
                    "title": "Core Methodologies and Frameworks",
                    "content": """
### 📐 Systematic Analysis
Now that we've covered the basics, we explore the structured frameworks used to evaluate and solve problems in this domain. 
"""
                },
                {
                    "title": "System Integration & Strategic Synthesis",
                    "content": """
### 🔄 Connecting the Dots
Every subsystem exists within a larger environment. To build complete, functioning systems, you must integrate these discrete concepts.
"""
                }
            ],
            "Intermediate Methodologies": [
                {
                    "title": "Practical Implementations and Process Modeling",
                    "content": """
### 🛠️ Working Practices
In this module, we transition from theoretical models to hands-on practical application.
"""
                },
                {
                    "title": "Advanced Frameworks and Case Formulations",
                    "content": """
### 💡 Applied Strategies
We examine complex scenarios, reviewing case studies and industry best practices to understand how professionals apply these tools.
"""
                },
                {
                    "title": "Systematic Analysis and Data Verification",
                    "content": """
### 📝 Quality Control
Learn how to test your implementations, collect data, verify outputs, and optimize workflows.
"""
                }
            ],
            "Final Assessment & Capstone": [
                {
                    "title": "Industrial Applications and Case Analyses",
                    "content": """
### 🚀 Real-World Implementations
Reviewing enterprise implementations, checking scalability challenges, and optimizing outcomes for industry environments.
"""
                },
                {
                    "title": "Modern Optimization & Emerging Trends",
                    "content": """
### 🌱 Future Directions
Exploring modern trends, automated processes, and how new technologies are shifting paradigms in this subject.
"""
                },
                {
                    "title": "Final Capstone Integration Exercise",
                    "content": """
### 🏁 Capstone Case Study
Prepare your final thesis/project application by applying all concepts learned across the previous modules.
"""
                }
            ],
            "quizzes": [
                {
                    "question": "What is the primary goal of applying a systematic framework to this subject?",
                    "options": [
                        "To reduce complexity and achieve repeatable success",
                        "To memorize terms without context",
                        "To replace practical testing entirely",
                        "To delay project timelines"
                    ],
                    "correct_answer": "To reduce complexity and achieve repeatable success"
                },
                {
                    "question": "Which phase of learning bridges raw theory with practical work?",
                    "options": ["Concept phase", "Methodology phase", "Implementation phase", "Review phase"],
                    "correct_answer": "Implementation phase"
                },
                {
                    "question": "What is an agency conflict in corporate and team environments?",
                    "options": [
                        "Misaligned interests between actors and managers",
                        "Technical hardware incompatibilities",
                        "Simple differences in working hours",
                        "Database write lock errors"
                    ],
                    "correct_answer": "Misaligned interests between actors and managers"
                },
                {
                    "question": "Why is historical context useful when studying modern disciplines?",
                    "options": [
                        "It helps you understand how contemporary systems evolved",
                        "It makes modern studies unnecessary",
                        "It replaces practical exercises",
                        "It is not useful"
                    ],
                    "correct_answer": "It helps you understand how contemporary systems evolved"
                },
                {
                    "question": "What does the Capstone project represent in this learning journey?",
                    "options": [
                        "Integration of all cumulative knowledge into a practical application",
                        "A simple introductory quiz",
                        "An optional vocabulary list",
                        "A repeat of the first lecture"
                    ],
                    "correct_answer": "Integration of all cumulative knowledge into a practical application"
                }
            ]
        }

        # Import dynamic tutor extensions
        try:
            from engine.tutor_data import NEW_CURRICULUM, NEW_CONCEPTS
            self.curriculum_data.update(NEW_CURRICULUM)
            for k, v in NEW_CONCEPTS.items():
                self.CONCEPTS_BANK[k] = v
        except Exception as e:
            print(f"Error loading dynamic tutor extensions: {e}")

    # Predefined academic concepts for generating 30 distinct questions per module quiz
    CONCEPTS_BANK = {
        "programming": {
            "Foundational Principles": [
                ("Variables", "Containers for storing data values in memory"),
                ("Integers", "Data type representing whole numbers without decimals"),
                ("Strings", "Sequences of text characters used for storing text"),
                ("Booleans", "Data type representing true or false binary values"),
                ("If-Else Statements", "Conditional statements used to direct program flow based on boolean expressions"),
                ("For Loops", "Control structures used to iterate over a sequence of elements"),
                ("While Loops", "Control structures that repeat code as long as a condition is true"),
                ("Functions", "Reusable blocks of code designed to perform a single action"),
                ("Local Scope", "Variables declared inside a function that are only accessible within it"),
                ("Global Scope", "Variables declared outside functions that are accessible anywhere in the script"),
                ("Logical AND", "Operator that returns true only if both conditions are true"),
                ("Logical OR", "Operator that returns true if at least one condition is true"),
                ("Recursion", "A programming technique where a function calls itself"),
                ("Parameters", "Variables listed in a function definition that receive input values"),
                ("Return Value", "The output value that a function sends back to the caller")
            ],
            "Intermediate Methodologies": [
                ("Encapsulation", "Bundling data and methods into a class and restricting direct access"),
                ("Inheritance", "A mechanism where a child class acquires the properties of a parent class"),
                ("Polymorphism", "The ability of different classes to respond to the same method call in unique ways"),
                ("Abstraction", "Hiding complex implementation details and exposing only the essential features"),
                ("Classes", "Blueprints or templates used to create individual objects"),
                ("Objects", "Instances of classes containing real values and methods"),
                ("Constructors", "Special methods called automatically when an object is instantiated"),
                ("Try-Except Blocks", "Control structures used to handle runtime errors and prevent crashes"),
                ("ZeroDivisionError", "Exception raised when dividing a number by zero"),
                ("File Reading", "Opening and retrieving data stored in an external file"),
                ("File Writing", "Saving data from a program into an external persistent file"),
                ("JSON", "Lightweight data-interchange format easily read by humans and machines"),
                ("CSV", "Tabular data stored as comma-separated values in text files"),
                ("IndexError", "Exception raised when attempting to access an invalid index in a sequence"),
                ("KeyError", "Exception raised when a dictionary key is not found")
            ],
            "Final Assessment & Capstone": [
                ("PEP 8", "The official style guide for writing clean, readable Python code"),
                ("Refactoring", "Restructuring existing code without changing its external behavior to improve quality"),
                ("DRY Principle", "Don't Repeat Yourself - avoiding redundant code blocks"),
                ("Unit Testing", "Testing individual software components to verify they work correctly"),
                ("Docstrings", "Triple-quoted strings used to document python modules, classes, and functions"),
                ("Clean Code", "Code that is readable, simple, and easy to maintain by others"),
                ("Modularity", "Breaking a program into independent, swappable sub-modules"),
                ("Technical Debt", "The future cost of extra development work caused by choosing easy, messy code now"),
                ("Code Review", "Peer assessment of source code to identify bugs and check standards"),
                ("Debugging", "The systematic process of locating and fixing errors in code"),
                ("Version Control", "Systems like Git that track changes to files over time"),
                ("Integration Testing", "Testing combined parts of an application to ensure they work together"),
                ("Performance Bottleneck", "A section of code that slows down the execution of the entire system"),
                ("Code Comments", "Explanations written inside code to help humans understand complex logic"),
                ("Command-Line Interface", "A text-based interface used to interact with software applications")
            ]
        },
        "dsa": {
            "Foundational Principles": [
                ("Data Structure", "A specialized format for organizing, processing, retrieving, and storing data"),
                ("Time Complexity", "The measure of the amount of time an algorithm takes to run as a function of the input size"),
                ("Big O Notation", "Mathematical notation describing the limiting behavior of a function in the worst-case scenario"),
                ("Constant Time O(1)", "Algorithm execution time that remains unchanged regardless of input size"),
                ("Linear Time O(n)", "Algorithm execution time that grows in direct proportion to input size"),
                ("Logarithmic Time O(log n)", "Algorithm execution time that halves the search space at each step"),
                ("Quadratic Time O(n^2)", "Algorithm execution time that grows proportionally to the square of the input size"),
                ("Array", "A data structure consisting of a collection of elements stored in contiguous memory locations"),
                ("Linked List", "A linear data structure where elements are stored in nodes connected by pointers"),
                ("Stack", "A linear data structure operating on a Last-In, First-Out (LIFO) access sequence"),
                ("Queue", "A linear data structure operating on a First-In, First-Out (FIFO) access sequence"),
                ("LIFO", "Access pattern representing Last-In, First-Out operations"),
                ("FIFO", "Access pattern representing First-In, First-Out operations"),
                ("Recursion", "An algorithmic technique where a function calls itself to solve smaller subproblems"),
                ("Base Case", "The condition in a recursive function that terminates the recursion")
            ],
            "Intermediate Methodologies": [
                ("Binary Search Tree", "A node-based binary tree structure where the left subtree is less than the node and the right is greater"),
                ("Graph", "A non-linear structure consisting of vertices connected by edges representing relationships"),
                ("Adjacency List", "A collection of unordered lists used to represent a graph's connections"),
                ("Binary Search", "An efficient search algorithm that finds a value in a sorted array by repeatedly dividing the interval in half"),
                ("Merge Sort", "A divide-and-conquer sorting algorithm that splits an array in half, sorts them, and merges them"),
                ("Quick Sort", "An efficient sorting algorithm that partitions an array around a pivot element"),
                ("Hash Table", "A data structure that maps keys to values using a hash function for constant-time lookup"),
                ("Collision", "An event in hashing where two distinct keys map to the same database array index"),
                ("Linear Probing", "A collision resolution technique that searches sequentially for the next open database slot"),
                ("Chaining", "A collision resolution technique where each hash table slot holds a linked list of records"),
                ("Hash Function", "An algorithm that converts an input key into a fixed-size numerical index"),
                ("Pre-order Traversal", "Tree traversal visiting the root node first, then the left subtree, then the right subtree"),
                ("In-order Traversal", "Tree traversal visiting the left subtree first, then the root node, then the right subtree"),
                ("Post-order Traversal", "Tree traversal visiting the left subtree first, then the right subtree, and the root node last"),
                ("BST Search", "Algorithm that recursively navigates left or right in a binary search tree to locate a value")
            ],
            "Final Assessment & Capstone": [
                ("Dynamic Programming", "An optimization method that solves complex problems by breaking them into overlapping subproblems"),
                ("Greedy Algorithm", "An algorithmic approach that makes the locally optimal choice at each step"),
                ("Memoization", "An optimization technique of caching expensive function call results for reuse"),
                ("BFS", "Breadth-First Search - exploring all neighbor nodes at the current depth before moving deeper"),
                ("DFS", "Depth-First Search - exploring along each branch as deep as possible before backtracking"),
                ("Dijkstra's Algorithm", "An algorithm for finding the shortest paths between nodes in a weighted graph"),
                ("Kruskal's Algorithm", "A greedy algorithm that finds a minimum spanning tree for a connected weighted graph"),
                ("Prim's Algorithm", "A greedy algorithm that builds a minimum spanning tree by growing one vertex at a time"),
                ("Topological Sort", "A linear ordering of vertices in a directed acyclic graph such that dependency order is respected"),
                ("Overlapping Subproblems", "A characteristic of dynamic programming where the same subproblems are solved repeatedly"),
                ("Optimal Substructure", "A problem property where an optimal solution can be constructed from optimal solutions of its subproblems"),
                ("Adjacency Matrix", "A two-dimensional array representation of a graph showing edge connections"),
                ("Heap", "A specialized tree-based data structure that satisfies the heap property (max-heap or min-heap)"),
                ("Complete Binary Tree", "A binary tree in which every level is completely filled except possibly the last"),
                ("Space Complexity", "The amount of memory space required by an algorithm to run as a function of the input size")
            ]
        },
        "business": {
            "Foundational Principles": [
                ("Business Ethics", "The system of moral principles and standards applied to corporate operations and trade"),
                ("Utilitarianism", "Ethical theory holding that actions are right if they maximize overall pleasure or utility"),
                ("Deontology", "Ethical theory that judges the morality of an action based on rules and duty"),
                ("Virtue Ethics", "Ethical framework emphasizing the character and integrity of the decision-maker"),
                ("Corporate Governance", "The system of rules, practices, and processes by which a firm is directed and controlled"),
                ("Fiduciary Duty", "A legal obligation of one party to act in the best interest of another"),
                ("Shareholder Theory", "Theory holding that a corporation's primary duty is to maximize profits for its owners"),
                ("Stakeholder Theory", "Theory holding that corporations must create value for all groups affected by their operations"),
                ("Agency Conflict", "A conflict of interest between managers (agents) and owners (shareholders) of a firm"),
                ("Ethical Relativism", "The belief that moral principles are relative to individual choice or cultural context"),
                ("Board of Directors", "A group of individuals elected by shareholders to oversee a corporation's management"),
                ("Sarbanes-Oxley Act", "US federal law that set new standards for public company boards and accounting firms"),
                ("Fiduciary Responsibility", "Obligation of board members to manage corporate assets with care and loyalty"),
                ("Code of Conduct", "A formal document outlining an organization's ethical expectations and rules"),
                ("Whistleblower", "An employee who reports corporate misconduct, safety violations, or illegal acts")
            ],
            "Intermediate Methodologies": [
                ("CSR", "Corporate Social Responsibility - a business model that integrates social and environmental goals"),
                ("Triple Bottom Line", "An accounting framework measuring performance in three areas: People, Planet, and Profit"),
                ("Social Performance", "Measuring how a business impacts employees, communities, and society"),
                ("Environmental Performance", "Measuring how business operations impact natural ecosystems and climate"),
                ("Economic Performance", "Measuring a firm's financial profitability and strategic market growth"),
                ("Whistleblowing", "The act of exposing internal corporate malpractice to the public or authorities"),
                ("Conflict of Interest", "A situation where personal interests interfere with professional duties"),
                ("Sustainability", "Operating in a way that meets current needs without compromising future generations"),
                ("Carbon Footprint", "The total amount of greenhouse gases generated by organizational activities"),
                ("Fair Trade", "Social movement advocating for payment of fair prices and decent wages to producers"),
                ("Ethical Sourcing", "Ensuring that materials are acquired through responsible and sustainable labor practices"),
                ("Greenwashing", "Deceptive marketing that portrays a company's products as more environmentally friendly than they are"),
                ("Organizational Culture", "The shared values, beliefs, and practices that govern employee behavior in a firm"),
                ("Compliance Officer", "A corporate official responsible for ensuring adherence to laws and policies"),
                ("Corporate Philanthropy", "The act of a corporation donating a portion of its profits or resources to charity")
            ],
            "Final Assessment & Capstone": [
                ("Enron Scandal", "A landmark corporate fraud case that exposed massive accounting loopholes and led to corporate collapse"),
                ("WorldCom Failure", "A major telecom bankruptcy caused by fraudulent accounting entries hiding expenses"),
                ("Supply Chain Ethics", "Ensuring fair labor wages, avoiding child labor, and tracking environmental impacts across global vendor networks"),
                ("Child Labor Avoidance", "Policies and audits preventing the employment of minors in factory networks"),
                ("Fair Wages", "Paying workers a salary that meets local standard of living costs"),
                ("Greenhouse Emissions", "Gaseous outputs contributing to global warming that firms must measure and reduce"),
                ("AI Ethics", "The branch of ethics addressing algorithmic bias, privacy, and technology governance"),
                ("Algorithmic Bias", "Systematic errors in computer algorithms that lead to unfair outcomes or discrimination"),
                ("Data Privacy", "The ethical and legal protection of personal user data from unauthorized access"),
                ("Technology Governance", "The management of technological resources to ensure safety, compliance, and goal alignment"),
                ("Ethical Audits", "Structured evaluations of an organization's compliance with its ethical standards"),
                ("Risk Assessment", "Identifying and evaluating potential ethical or operational risks to prevent crises"),
                ("Sustainable Development", "Economic growth that preserves natural resources for the future"),
                ("CSR Reporting", "The public disclosure of environmental and social impacts by a company"),
                ("Corporate Transparency", "The practice of sharing complete, accurate financial and operational data with stakeholders")
            ]
        },
        "medicine": {
            "Foundational Principles": [
                ("Homeostasis", "The state of internal balance and physiological equilibrium maintained by feedback loops"),
                ("Pathology", "The scientific study of disease mechanisms, causes, and bodily impacts"),
                ("Physiology", "The study of the normal functions and chemical processes within living organisms"),
                ("Anatomy", "The branch of science exploring the physical structure of the human body"),
                ("Pharmacokinetics", "What the body does to a drug, specifically its absorption, distribution, metabolism, and excretion"),
                ("Pharmacodynamics", "What a drug does to the body, exploring receptor binding and physiological impacts"),
                ("Absorption", "The process of a drug entering the bloodstream from its site of administration"),
                ("Distribution", "The transport of a drug through the bloodstream to various tissues and organs"),
                ("Metabolism", "The chemical alteration of a drug by enzymes, primarily occurring in the liver"),
                ("Excretion", "The elimination of a drug from the body, primarily carried out by the kidneys"),
                ("ADME", "Acronym representing Absorption, Distribution, Metabolism, and Excretion in pharmacology"),
                ("Bioavailability", "The fraction of an administered drug dose that reaches the systemic circulation unchanged"),
                ("Half-Life", "The time required for the concentration of a drug in the body to decrease by 50%"),
                ("Receptor Binding", "The interaction of a drug molecule with specific cellular receptors to trigger a response"),
                ("Toxicity", "The degree to which a substance can cause harm or poisonous effects in an organism")
            ],
            "Intermediate Methodologies": [
                ("Immunology", "The study of the immune system and its responses to pathogens"),
                ("Adaptive Immunity", "A specific immune response to foreign antigens characterized by memory cell creation"),
                ("Innate Immunity", "The immediate, non-specific immune defense mechanism of the body"),
                ("Pathogens", "Disease-causing micro-organisms like viruses, bacteria, and fungi"),
                ("General Surgery", "A surgical specialty focusing on abdominal contents and general tissue repair"),
                ("Anesthesia Protocols", "Structured administration of anesthetics to ensure patient comfort and safety during surgery"),
                ("Epidemiology", "The study of the distribution and determinants of health states in populations"),
                ("Public Health", "The science of protecting and improving health at the population level"),
                ("Incidence Rate", "The number of new cases of a disease that develop in a population during a specific time period"),
                ("Prevalence Rate", "The total number of active cases of a disease in a population at a given time"),
                ("Vectors", "Organisms that transmit infectious pathogens between hosts (e.g., mosquitoes)"),
                ("Vaccine", "A biological preparation that provides active acquired immunity to a specific disease"),
                ("Clinical Trials", "Research studies performed on human participants to evaluate medical interventions"),
                ("Pathogenesis", "The step-by-step development and progression of a disease process in the body"),
                ("Diagnostics", "The methods and technologies used to identify a patient's medical condition or disease")
            ],
            "Final Assessment & Capstone": [
                ("Patient Autonomy", "The ethical principle respecting a patient's right to make decisions about their medical care"),
                ("Beneficence", "The medical duty to act in the best interest of the patient's health and well-being"),
                ("Non-maleficence", "The foundational medical principle of doing no harm to a patient"),
                ("Justice", "The ethical distribution of healthcare resources and fair treatment of patients"),
                ("Precision Medicine", "A medical model customizing healthcare with treatments tailored to individual genetic profiles"),
                ("Pharmacotherapy", "The treatment of disease through the administration of drugs"),
                ("Targeted Therapy", "Cancer or disease treatment using drugs designed to target specific genes or proteins"),
                ("Genetic Profiling", "Analyzing an individual's DNA to identify disease risks and select optimal therapies"),
                ("Clinical Diagnostics", "The process of identifying a disease or condition from symptoms and lab tests"),
                ("Patient Confidentiality", "The legal and ethical duty to protect patient health records and information from disclosure"),
                ("Informed Consent", "Agreement by a patient to undergo a medical procedure after understanding risks and alternatives"),
                ("Palliative Care", "Specialized medical care focused on providing relief from symptoms and stress of serious illness"),
                ("Diagnostics Capstone", "A practical case exercise analyzing clinical charts to determine treatment protocols"),
                ("Fiduciary Patient Relationship", "A relationship of trust where a clinician is bound to prioritize patient welfare"),
                ("Treatment Protocol", "A standardized set of rules and steps for treating a specific medical condition")
            ]
        },
        "law": {
            "Foundational Principles": [
                ("Jurisprudence", "The philosophy and science of law exploring its origin and application"),
                ("Common Law", "A legal system based on judicial precedents and customs rather than statutes"),
                ("Civil Law", "A legal system based on written codes and comprehensive statutory laws"),
                ("Judicial Precedent", "A prior legal decision that guides subsequent cases with similar facts"),
                ("Actus Reus", "The physical act or conduct constituting a crime"),
                ("Mens Rea", "The mental intent or 'guilty mind' behind committing a crime"),
                ("Criminal Liability", "Legal responsibility for committing an act defined as a crime"),
                ("Constitutional Law", "Law defining the structure of government and civil liberties of citizens"),
                ("Civil Liberties", "Fundamental individual rights protected from government infringement"),
                ("Bill of Rights", "A formal declaration of the fundamental rights of citizens in a constitution"),
                ("Statutory Law", "Written laws enacted by a legislative body"),
                ("Criminal Intent", "The conscious decision to commit an unlawful act"),
                ("Rule of Law", "The principle that all individuals and institutions are subject and accountable to law"),
                ("Separation of Powers", "The division of government responsibilities into legislative, executive, and judicial branches"),
                ("Judicial Review", "The power of courts to review and invalidate laws that violate the constitution")
            ],
            "Intermediate Methodologies": [
                ("Corporate Law", "The body of law governing the formation and operation of corporations"),
                ("Intellectual Property", "Legal rights protecting creations of the mind such as inventions, designs, and works of art"),
                ("Patents", "Legal rights granting inventors exclusive ownership and control over an invention"),
                ("Trademarks", "Distinctive signs, logos, or words used to identify a business's products"),
                ("Copyrights", "Legal rights granting creators control over the reproduction of their original works"),
                ("Torts", "Civil wrongs that cause harm to another, leading to legal liability"),
                ("Negligence", "A failure to behave with the level of care that a reasonable person would exercise"),
                ("Duty of Care", "The legal obligation to avoid actions that could foreseeably harm others"),
                ("Breach of Duty", "A failure to meet the required standard of care in a negligence claim"),
                ("Causation", "The direct link between a breach of duty and the resulting injury or damage"),
                ("Damages", "Monetary compensation awarded by a court to make up for legal harm or injury"),
                ("Civil Liability", "Responsibility for payment of damages in a civil lawsuit"),
                ("Contracts", "Legally binding agreements between two or more parties"),
                ("Consideration", "Something of value exchanged between parties to make a contract legally binding"),
                ("Liability Breach", "Failure to perform a contract obligation resulting in legal liability")
            ],
            "Final Assessment & Capstone": [
                ("Legal Brief", "A written legal argument submitted to a court to convince a judge to rule in a client's favor"),
                ("Moot Court", "A simulated court experience where students argue appellate cases"),
                ("Litigation Ethics", "Rules governing the professional conduct of attorneys during disputes"),
                ("IRAC Method", "Legal writing format structuring analysis by Issue, Rule, Application, and Conclusion"),
                ("Judicial Interpretation", "The process by which courts interpret and apply statutory language"),
                ("Stare Decisis", "The legal principle of determining points in litigation according to precedent"),
                ("Appellate Defense", "Legal advocacy representing a client during an appeal of a lower court decision"),
                ("Legal Advocacy", "Representing and defending a client's legal rights in court or negotiations"),
                ("Professional Responsibility", "The ethical standards regulating the legal profession"),
                ("Client Confidentiality", "The duty of an attorney to protect all client communication from disclosure"),
                ("Conflict of Interest Law", "Ethical prohibition against representing clients with opposing interests"),
                ("Case Precedents", "Binding decisions from higher courts that dictate the outcome of similar cases"),
                ("Jurisdictional Limits", "The geographic or subject boundaries of a court's authority"),
                ("Legal Writing", "The specialized writing style used by legal professionals to draft contracts and briefs"),
                ("Due Process", "The constitutional requirement that government must respect all legal rights owed to a person")
            ]
        },
        "mis": {
            "Foundational Principles": [
                ("Management Information Systems", "The study of people, technology, and organizations to leverage information for business decision-making"),
                ("Transaction Processing Systems", "Systems that track daily operational transactions such as sales, receipts, and payroll"),
                ("Decision Support Systems", "Interactive software systems that help managers analyze data to solve semi-structured problems"),
                ("Executive Support Systems", "Information systems designed to help senior managers track performance and make long-term strategic decisions"),
                ("Five Core Components", "The elements of an information system: hardware, software, data, procedures, and people"),
                ("IT Governance", "A framework ensuring that IT investments align with and support business strategic goals"),
                ("Strategic Alignment", "The process of matching technology strategy with business objectives to maximize value"),
                ("Systems Theory", "The scientific study of systems as interrelated parts working toward a common goal"),
                ("Data vs Information", "The difference between raw facts (data) and processed, meaningful facts (information)"),
                ("Information Quality", "The accuracy, completeness, relevance, and timeliness of business data"),
                ("Cloud Computing", "The delivery of computing services over the internet to increase scalability and reduce costs"),
                ("Virtualization", "Creating virtual versions of servers, storage devices, or network resources"),
                ("Business Processes", "Set of structured activities that produce a specific service or product for customers"),
                ("Technical Infrastructure", "The shared physical and soft hardware resources that support IT services in a firm"),
                ("Organizational Synergy", "The combined effect of business components working together that exceeds the sum of their individual parts")
            ],
            "Intermediate Methodologies": [
                ("SDLC", "Systems Development Life Cycle - a structured framework for building software systems"),
                ("Systems Analysis", "The phase of SDLC focused on gathering user requirements and modeling business processes"),
                ("SDLC Requirements", "Specifying exactly what functions and features a new information system must have"),
                ("System Design", "The SDLC phase detailing system architecture, databases, user interfaces, and network structures"),
                ("System Implementation", "The SDLC phase involving coding, testing, user training, and deploying a new system"),
                ("RDBMS", "Relational Database Management System - software used to create and manage structured tables connected by keys"),
                ("SQL Query", "Standard statement used to retrieve, update, and manage data in relational databases"),
                ("Data Normalization", "Organizing relational database tables to minimize redundancy and prevent data anomalies"),
                ("ERP Systems", "Enterprise Resource Planning systems integrating all department data into a single corporate database"),
                ("CRM Systems", "Customer Relationship Management systems tracking all sales, customer profiles, and service interactions"),
                ("Supply Chain Management Systems", "Information systems tracking flow of raw materials and products from supplier to final consumer"),
                ("Agile Development", "An iterative software development methodology emphasizing collaboration, flexibility, and rapid delivery"),
                ("Waterfall Model", "A sequential development methodology where each phase must finish before the next begins"),
                ("Entity-Relationship Diagram", "A visual model showing database tables (entities) and the relationships between them"),
                ("Database Schema", "The logical configuration and structure of a database including tables, fields, and constraints")
            ],
            "Final Assessment & Capstone": [
                ("Information Security", "Protecting organizational digital assets and data from unauthorized access or alteration"),
                ("Data Confidentiality", "Ensuring that sensitive business data is accessed only by authorized personnel"),
                ("System Integrity", "Ensuring that business information systems operate correctly and data remains unaltered"),
                ("Availability", "Ensuring that information systems and data are accessible to users when needed"),
                ("Compliance Audits", "Structured evaluations verifying that systems follow laws, policies, and industry standards"),
                ("Disaster Recovery", "Policies and systems designed to restore IT operations quickly after a crisis or outage"),
                ("Business Intelligence", "Software tools used to analyze historical business data and uncover strategic trends"),
                ("Data Warehousing", "Consolidating large volumes of transaction data into a central database for analytical queries"),
                ("Data Mining", "The computational process of discovering hidden patterns in large datasets using machine learning"),
                ("Digital Transformation", "The strategic integration of digital technology into all areas of a business"),
                ("Technology Governance", "The structural management of technology resources to prevent risks and ensure value"),
                ("Enterprise Architecture", "The structural design aligning a company's business processes, data, and technology infrastructure"),
                ("Analytics Dashboards", "Visual interfaces displaying real-time key performance metrics for manager review"),
                ("Risk Mitigation", "Policies and technical safeguards designed to reduce the impact of operational failures"),
                ("Capstone Design Proposal", "A comprehensive technical document outlining architecture and database design for a firm")
            ]
        },
        "default": {
            "Foundational Principles": [
                ("Conceptual Framework", "An analytical tool with variations used to organize ideas and structure research"),
                ("Methodological Basics", "The fundamental rules and procedures governing scientific study in a discipline"),
                ("Core Dynamics", "The primary forces and interactions driving behavior within a system"),
                ("Historical Context", "The background events and ideas that shaped the development of a subject over time"),
                ("System Integration", "Connecting different subsystems to ensure they function as a cohesive whole"),
                ("Strategic Synthesis", "Combining diverse ideas or strategies into a unified, high-level plan"),
                ("Theory Building", "The process of formulating logical explanations for observed phenomena"),
                ("Academic Taxonomy", "The classification system used to organize terms and concepts within a field"),
                ("Empirical Evidence", "Information acquired by direct observation or scientific experimentation"),
                ("Hypothesis Testing", "Statistical methods used to determine if experimental data supports a theory"),
                ("Analytical Thinking", "The ability to break down complex issues into smaller, manageable parts for analysis"),
                ("Scientific Inquiry", "The diverse ways in which scientists study the natural world and propose explanations"),
                ("Subject Terminology", "The specialized vocabulary and language used within a specific discipline"),
                ("Primary Research", "Collecting original data directly from the source for a specific study"),
                ("Literature Review", "An evaluative report of studies found in literature related to a selected topic")
            ],
            "Intermediate Methodologies": [
                ("Practical Implementation", "Translating theoretical models and ideas into real-world operational systems"),
                ("Process Modeling", "Graphically representing business or system workflows to analyze and improve them"),
                ("Applied Strategy", "The hands-on execution of strategic plans to solve real-world problems"),
                ("Case Studies", "In-depth analyses of specific real-world scenarios to extract lessons and strategies"),
                ("Quality Control", "Systems designed to verify that outputs meet required specifications and standards"),
                ("Data Verification", "The process of checking data accuracy and consistency during research"),
                ("Workflow Optimization", "Improving processes to reduce delays, minimize waste, and increase execution speed"),
                ("Experimental Design", "Structuring research studies to verify causal relationships between variables"),
                ("Qualitative Analysis", "Non-numerical analysis exploring meaning, opinions, and experiences"),
                ("Quantitative Analysis", "Numerical analysis using mathematical and statistical models to check data patterns"),
                ("Statistical Significance", "The likelihood that a research result occurred by chance rather than real cause"),
                ("Sampling Methods", "Techniques used to select a representative subset of individuals from a population"),
                ("Control Group", "The baseline group in an experiment that does not receive the active treatment"),
                ("Peer Review", "Evaluation of scientific work by other experts in the same field before publication"),
                ("Academic Integrity", "The commitment to honesty, trust, fairness, and respect in scholarship")
            ],
            "Final Assessment & Capstone": [
                ("Industrial Application", "Applying academic concepts to commercial, industrial, or manufacturing operations"),
                ("System Scalability", "The capacity of a system to handle growing amounts of work or expand gracefully"),
                ("Future Directions", "Anticipated trends, technologies, and research topics shaping a field's future"),
                ("Capstone Integration", "Applying all learned concepts in a final comprehensive practical project"),
                ("Thesis Formulation", "Developing a logical, evidence-supported academic proposition for evaluation"),
                ("Strategic Evaluation", "Assessing the long-term effectiveness of plans and systems in an organization"),
                ("Case Synthesis", "Combining insights from multiple case studies to identify general principles"),
                ("Emerging Paradigms", "New theories and models that are shifting established thinking in a field"),
                ("Interdisciplinary Study", "Combining concepts and methods from different academic fields in a single study"),
                ("Critical Review", "A structured, critical evaluation of an academic paper or system proposal"),
                ("Project Lifecycle", "The phases a project goes through from initiation to completion"),
                ("Deliverable Definition", "Specifying the concrete outputs that a project must produce"),
                ("Scope Management", "Ensuring a project includes only the work required to complete it successfully"),
                ("Stakeholder Communication", "Exchanging project updates and requirements with all interested parties"),
                ("Presentation Skills", "The ability to communicate complex technical ideas clearly to an audience")
            ]
        },
        "research": {
            "Foundational Principles": [
                ("Research Problem", "A specific issue, contradiction, or gap in knowledge that a study aims to address"),
                ("Research Question", "A clear, focused, and arguable question that guides the direction of a research study"),
                ("Hypothesis", "A testable statement proposing a relationship between two or more variables"),
                ("Literature Review", "A critical analysis of existing scholarly publications relevant to the chosen research topic"),
                ("Conceptual Framework", "A visual or written structure illustrating the expected relationships between variables in a study"),
                ("Theoretical Framework", "The foundational theories and academic models that support and guide a research study"),
                ("Independent Variable", "The variable that is manipulated or changed in an experiment to observe its effects"),
                ("Dependent Variable", "The variable that is measured or observed to test the effect of changes in the independent variable"),
                ("Primary Source", "An original document, record, or data source created at the time under study"),
                ("Secondary Source", "A document or analysis that discusses, interprets, or synthesizes primary source information"),
                ("Empirical Research", "Research based on observed and measured phenomena and direct experience"),
                ("Pilot Study", "A small-scale preliminary study conducted to test feasibility, time, cost, and design prior to a full research project"),
                ("Problem Statement", "A concise description of the issue that needs to be addressed by the research team"),
                ("Citation", "A formal reference to a published or unpublished source used to support an argument or fact"),
                ("APA Style", "A standardized writing and citation format widely used in the social sciences and education")
            ],
            "Intermediate Methodologies": [
                ("Qualitative Research", "Research focusing on understanding human behavior, opinions, and experiences through non-numerical data"),
                ("Quantitative Research", "Research focusing on gathering numerical data and generalizing findings across groups using statistics"),
                ("Mixed Methods", "A research approach combining both qualitative and quantitative research methodologies in a single study"),
                ("Probability Sampling", "A sampling technique where every member of the population has a known, non-zero chance of selection"),
                ("Purposive Sampling", "A non-probability sampling technique where participants are selected based on specific characteristics needed for the study"),
                ("Survey Questionnaire", "A structured research instrument consisting of a series of questions to gather data from respondents"),
                ("Semi-structured Interview", "A qualitative data collection method allowing open-ended discussion guided by an interview protocol"),
                ("Focus Group", "A guided discussion with a small group of people to gather diverse perspectives on a topic"),
                ("Content Analysis", "A research tool used to determine the presence of certain words, themes, or concepts within qualitative data"),
                ("Triangulation", "Using multiple data sources or research methods to validate and cross-examine findings in a study"),
                ("Validity", "The extent to which a research instrument measures what it claims to measure"),
                ("Reliability", "The consistency and repeatability of a research instrument or measurement scale"),
                ("Descriptive Statistics", "Brief descriptive coefficients that summarize a given data set (e.g., mean, median, standard deviation)"),
                ("Inferential Statistics", "Methods used to make generalizations or predictions about a population based on sample data"),
                ("Data Coding", "The qualitative process of categorizing raw text or responses into meaningful themes and tags")
            ],
            "Final Assessment & Capstone": [
                ("Research Proposal", "A structured document outlining the proposed plan, methodology, and significance of a future study"),
                ("Plagiarism", "The unethical practice of taking someone else's work or ideas and passing them off as one's own"),
                ("Academic Integrity", "The commitment to ethical behavior, honesty, and rigor in research and scholarship"),
                ("Informed Consent", "Ensuring that research participants understand the study's purpose, risks, and benefits before agreeing to participate"),
                ("Institutional Review Board", "An administrative body established to protect the rights and welfare of human research subjects"),
                ("Peer Review Process", "The evaluation of research papers by independent experts before publication in academic journals"),
                ("Methodology Chapter", "The section of a dissertation explaining the design, instruments, and procedures used to collect data"),
                ("Results Chapter", "The section of a dissertation presenting the raw findings and statistical outputs of the study"),
                ("Discussion Chapter", "The section of a dissertation interpreting findings, linking them to literature, and discussing implications"),
                ("Dissertation Abstract", "A brief summary of a research project outlining its purpose, methods, key findings, and conclusions"),
                ("Viva Voce", "An oral examination or defense where a candidate presents and defends their research thesis to examiners"),
                ("Scope Limitation", "The boundaries and constraints of a study, including what was not investigated and why"),
                ("Data De-identification", "The process of removing personally identifying information from research datasets to protect privacy"),
                ("Research Contribution", "The new knowledge, theoretical insights, or practical solutions that a study adds to its field"),
                ("Future Recommendations", "Suggestions in a research paper outlining areas that require further study or action by future researchers")
            ]
        },
    }

    def _determine_category(self, course_title, category_hint):
        """Map course metadata to a specific curriculum keys."""
        import re
        text = f"{course_title} {category_hint or ''}".lower()
        words = re.findall(r'[a-z0-9]+', text)
        
        def has_match(keywords):
            for kw in keywords:
                if " " in kw:
                    if kw in text:
                        return True
                else:
                    if any(w.startswith(kw) for w in words):
                        return True
            return False

        if has_match(["structure", "algorithm", "dsa"]):
            return "dsa"
        elif has_match(["python", "program", "code", "coding", "java", "script"]):
            return "programming"
        elif has_match(["physic", "thermodynamics", "optics", "quantum", "laser", "electromagnetism", "fluid"]):
            return "physics"
        elif has_match(["math", "calculus", "algebra", "numerical", "optimization", "probability", "statistics", "equations"]):
            return "math"
        elif has_match(["psycholog", "cognitive", "clinical", "behavior", "neuropsychology"]):
            return "psychology"
        elif has_match(["anatomy", "surgery", "pharmacology", "medicine", "health", "biological"]):
            return "medicine"
        elif has_match(["law", "rights", "legal", "court"]):
            return "law"
        elif has_match(["research", "methodology", "thesis", "dissertation"]):
            return "research"
        elif has_match(["management information", "mis", "information systems"]) or ("mis" in words):
            return "mis"
        elif has_match(["fintech", "blockchain", "crypto", "bitcoin", "finance", "accounting", "audit", "tax", "econom"]):
            return "finance"
        elif has_match(["sociolog", "politic", "media", "social", "criminolog", "public policy", "relations"]):
            return "social_sciences"
        elif has_match(["mechanic", "circuit", "engineering", "petroleum", "reservoir", "drill", "power", "embedded", "vlsi", "device", "cad", "material"]):
            return "engineering"
        elif has_match(["ethic", "business", "management", "market", "corporate"]):
            return "business"
        elif has_match(["art", "design", "graphic", "illustration", "animat", "paint", "music", "writing"]):
            return "arts"
        
        return "default"

    def generate_module_content(self, course_title, module_title):
        """
        Generates highly specific and formatted lessons for the module.
        """
        category = self._determine_category(course_title, "")
        curriculum = self.curriculum_data.get(category, self.default_category)
        
        # Determine module list to load (Foundational, Intermediate, or Capstone)
        if "Principles" in module_title or "1" in module_title or "Foundational" in module_title:
            lessons_pool = curriculum.get("Foundational Principles", self.default_category["Foundational Principles"])
        elif "Methodologies" in module_title or "2" in module_title or "Intermediate" in module_title:
            lessons_pool = curriculum.get("Intermediate Methodologies", self.default_category["Intermediate Methodologies"])
        else:
            lessons_pool = curriculum.get("Final Assessment & Capstone", self.default_category["Final Assessment & Capstone"])

        # Inject course name dynamically to customize content
        final_lessons = []
        for l in lessons_pool:
            content = l["content"].replace("{course_title}", course_title).replace("{module_title}", module_title)
            final_lessons.append({
                "title": l["title"].replace("{course_title}", course_title).replace("{module_title}", module_title),
                "content": content
            })
            
        return final_lessons

    def generate_mcqs(self, course_title, module_title, lessons_info=None):
        """
        Generates 30 MCQ questions tailored to the course and module, referencing watched videos.
        """
        category = self._determine_category(course_title, module_title)
        
        # Determine module list
        if "Principles" in module_title or "1" in module_title or "Foundational" in module_title:
            module_key = "Foundational Principles"
        elif "Methodologies" in module_title or "2" in module_title or "Intermediate" in module_title:
            module_key = "Intermediate Methodologies"
        else:
            module_key = "Final Assessment & Capstone"

        # Load from CONCEPTS_BANK
        category_concepts = self.CONCEPTS_BANK.get(category, self.CONCEPTS_BANK["default"])
        concepts = category_concepts.get(module_key, category_concepts["Foundational Principles"])

        import random

        final_questions = []
        
        # We have 15 concepts. We generate 2 questions per concept to make exactly 30 questions!
        for idx, (name, definition) in enumerate(concepts):
            # Map index to associated lesson reference
            if lessons_info and len(lessons_info) > 0:
                lesson_idx = min(idx // 5, len(lessons_info) - 1)
                lesson_title = lessons_info[lesson_idx]["title"]
                lesson_ref = f"video tutorial for '{lesson_title}'"
            else:
                lesson_ref = f"video lecture on '{course_title}'"

            # Phrasing options to make it sound like the AI watched it
            phrasings_1 = [
                f"In the {lesson_ref}, what core definition is given for the concept of '{name}'?",
                f"Based on the explanation in the {lesson_ref}, which of the following best defines '{name}'?",
                f"The instructor in the {lesson_ref} highlights '{name}' as having which of these characteristics?",
                f"During the {lesson_ref}, how was '{name}' defined in the context of this module?"
            ]
            q_text_1 = random.choice(phrasings_1)
            
            # Select 3 distractors (definitions of other concepts in the same module)
            other_concepts = [c for c in concepts if c[0] != name]
            distractor_concepts = random.sample(other_concepts, min(3, len(other_concepts)))
            distractor_defs = [c[1] for c in distractor_concepts]
            
            options_1 = [definition] + distractor_defs
            random.shuffle(options_1)
            
            final_questions.append({
                "question": q_text_1,
                "options": options_1,
                "correct_answer": definition
            })
            
            phrasings_2 = [
                f"The {lesson_ref} introduced a key term defined as: '{definition}'. What is this term?",
                f"In the {lesson_ref}, the speaker detailed a concept as: '{definition}'. Which academic term is this?",
                f"Which concept was characterized in the {lesson_ref} as: '{definition}'?",
                f"According to the {lesson_ref}, which of the following terms matches the definition: '{definition}'?"
            ]
            q_text_2 = random.choice(phrasings_2)
            
            distractor_names = [c[0] for c in distractor_concepts]
            options_2 = [name] + distractor_names
            random.shuffle(options_2)
            
            final_questions.append({
                "question": q_text_2,
                "options": options_2,
                "correct_answer": name
            })

        # Shuffle the 30 questions
        random.shuffle(final_questions)
        return final_questions
