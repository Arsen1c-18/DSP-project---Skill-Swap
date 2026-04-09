"""
generate_extended_data.py
Generates clustered user data that enables meaningful 3-item Apriori rules.
Each archetype = a profession with tightly co-occurring skill bundles.
Run once: python generate_extended_data.py
"""

import pandas as pd
import random
import os

random.seed(42)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# ── Archetype definitions ──────────────────────────────────────────────────────
# core: EVERY user in this archetype offers ALL these skills (creates strong k-item support)
# extra: user picks 1 random extra from this list (variation)
# wants: what this archetype typically wants to learn (from other clusters)
# count: how many users to generate
# descriptions: pool of realistic bios

ARCHETYPES = {
    'data_scientist': {
        'core': ['skill_001', 'skill_021', 'skill_023', 'skill_024', 'skill_026'],
        # Python, Machine Learning, Data Analysis, Statistics, Data Visualization
        'extra': ['skill_025', 'skill_022', 'skill_028', 'skill_031', 'skill_029'],
        # SQL, Deep Learning, Tableau, Predictive Analytics, Power BI
        'wants': ['skill_011', 'skill_033', 'skill_059', 'skill_035', 'skill_064'],
        'count': 80,
        'descriptions': [
            "Data scientist leveraging Python and statistical modeling to drive insights.",
            "Building ML pipelines and turning raw data into actionable recommendations.",
            "Passionate about predictive analytics, data visualization, and storytelling with data.",
            "Research-driven data scientist focused on machine learning and statistical inference.",
            "Experienced in end-to-end data science workflows from EDA to model deployment.",
        ]
    },
    'ml_engineer': {
        'core': ['skill_001', 'skill_021', 'skill_022', 'skill_025', 'skill_099'],
        # Python, Machine Learning, Deep Learning, SQL, Docker
        'extra': ['skill_023', 'skill_024', 'skill_100', 'skill_031', 'skill_098'],
        # Data Analysis, Statistics, Kubernetes, Predictive Analytics, AWS
        'wants': ['skill_011', 'skill_014', 'skill_033', 'skill_102'],
        'count': 70,
        'descriptions': [
            "ML engineer deploying production-grade models with Python, PyTorch, and Docker.",
            "Building and fine-tuning deep learning architectures for real-world applications.",
            "End-to-end ML pipelines: data ingestion, model training, and containerized deployment.",
            "Focused on scalable ML infrastructure using Docker and cloud platforms.",
            "Machine learning practitioner with deep expertise in model optimization and SQL-based data prep.",
        ]
    },
    'js_fullstack': {
        'core': ['skill_002', 'skill_011', 'skill_014', 'skill_017', 'skill_010'],
        # JavaScript, React, Node.js, HTML/CSS, TypeScript
        'extra': ['skill_025', 'skill_099', 'skill_102', 'skill_019', 'skill_012'],
        # SQL, Docker, Git, Tailwind CSS, Vue.js
        'wants': ['skill_021', 'skill_033', 'skill_055', 'skill_023'],
        'count': 75,
        'descriptions': [
            "Full-stack JavaScript developer building scalable web apps with React and Node.js.",
            "TypeScript enthusiast shipping clean, well-typed frontend and backend code.",
            "React + Node.js developer with a love for modern UI and API architecture.",
            "Building fast, accessible web experiences using TypeScript and Node.js.",
            "Full-stack engineer comfortable across the entire JS ecosystem from HTML/CSS to REST APIs.",
        ]
    },
    'devops_engineer': {
        'core': ['skill_098', 'skill_099', 'skill_100', 'skill_101', 'skill_102'],
        # AWS, Docker, Kubernetes, CI/CD, Git
        'extra': ['skill_001', 'skill_105', 'skill_007', 'skill_003'],
        # Python, Cybersecurity, Go, Java
        'wants': ['skill_065', 'skill_059', 'skill_064', 'skill_023'],
        'count': 60,
        'descriptions': [
            "DevOps engineer automating infrastructure with Docker, Kubernetes, and AWS.",
            "Building robust CI/CD pipelines and managing cloud-native infrastructure.",
            "Platform reliability engineer focused on uptime, scalability, and GitOps workflows.",
            "Kubernetes and AWS specialist streamlining software delivery with CI/CD automation.",
            "Infrastructure engineer passionate about reliability, observability, and continuous delivery.",
        ]
    },
    'ui_ux_designer': {
        'core': ['skill_033', 'skill_035', 'skill_037', 'skill_034', 'skill_038'],
        # UI/UX Design, Figma, Photoshop, Graphic Design, Illustrator
        'extra': ['skill_036', 'skill_039', 'skill_040', 'skill_043', 'skill_041'],
        # Adobe XD, 3D Modeling, Animation, Brand Design, Video Editing
        'wants': ['skill_002', 'skill_011', 'skill_001', 'skill_017'],
        'count': 65,
        'descriptions': [
            "UI/UX designer crafting pixel-perfect, user-centered digital interfaces.",
            "Figma-first designer with a strong eye for visual design and brand consistency.",
            "Creating brand identities and digital experiences that convert and delight.",
            "Graphic and UX designer specializing in Figma prototyping and Photoshop compositing.",
            "Design systems thinker who bridges aesthetics with usability in every project.",
        ]
    },
    'digital_marketer': {
        'core': ['skill_054', 'skill_055', 'skill_056', 'skill_057', 'skill_030'],
        # Digital Marketing, SEO, Social Media Marketing, Content Marketing, Google Analytics
        'extra': ['skill_061', 'skill_062', 'skill_063', 'skill_032', 'skill_051'],
        # Influencer Marketing, Brand Strategy, Community Mgmt, A/B Testing, Email Marketing
        'wants': ['skill_023', 'skill_026', 'skill_001', 'skill_027'],
        'count': 60,
        'descriptions': [
            "Growth-focused digital marketer driving traffic through SEO and content strategy.",
            "Building brand presence with data-driven digital marketing and social media campaigns.",
            "Performance marketer specializing in organic growth via SEO and content marketing.",
            "Digital marketing strategist with expertise in Google Analytics and brand storytelling.",
            "Social media and SEO specialist helping brands grow their digital footprint.",
        ]
    },
    'content_writer': {
        'core': ['skill_044', 'skill_045', 'skill_047', 'skill_055', 'skill_046'],
        # Content Writing, Copywriting, Blogging, SEO, Technical Writing
        'extra': ['skill_051', 'skill_052', 'skill_048', 'skill_049', 'skill_050'],
        # Email Marketing, Storytelling, Creative Writing, Scriptwriting, Editing & Proofreading
        'wants': ['skill_054', 'skill_033', 'skill_035', 'skill_002'],
        'count': 50,
        'descriptions': [
            "Content writer crafting SEO-optimized articles and copy that drive engagement.",
            "Versatile writer covering technical documentation, blogs, and marketing copy.",
            "Storyteller and blogger building loyal audiences through compelling written content.",
            "Copywriter and content strategist with a strong command of SEO and technical writing.",
            "Creative writer turned content professional specializing in blogging and brand voice.",
        ]
    },
    'python_backend': {
        'core': ['skill_001', 'skill_016', 'skill_025', 'skill_102', 'skill_104'],
        # Python, Flask, SQL, Git, Testing/QA
        'extra': ['skill_015', 'skill_099', 'skill_098', 'skill_003'],
        # Django, Docker, AWS, Java
        'wants': ['skill_011', 'skill_017', 'skill_002', 'skill_033'],
        'count': 65,
        'descriptions': [
            "Python backend developer building clean, testable APIs with Flask and Django.",
            "Server-side engineer focused on robust Python code, SQL databases, and Git workflows.",
            "Backend developer with strong Flask/Django experience and a test-driven approach.",
            "API developer using Python and SQL to build scalable, maintainable services.",
            "Python engineer with deep expertise in Flask, SQL schema design, and QA practices.",
        ]
    },
    'business_analyst': {
        'core': ['skill_065', 'skill_027', 'skill_026', 'skill_064', 'skill_025'],
        # Business Analysis, Excel, Data Visualization, Project Management, SQL
        'extra': ['skill_029', 'skill_028', 'skill_032', 'skill_070', 'skill_030'],
        # Power BI, Tableau, A/B Testing, Business Strategy, Google Analytics
        'wants': ['skill_001', 'skill_021', 'skill_023', 'skill_066'],
        'count': 50,
        'descriptions': [
            "Business analyst transforming data into strategic recommendations for stakeholders.",
            "Bridging business and technology through data analysis and project management.",
            "Experienced in requirements gathering, Excel dashboards, and SQL-based reporting.",
            "Data-driven business analyst with expertise in visualization tools and KPI tracking.",
            "Analyst specializing in SQL, Excel, and cross-functional project coordination.",
        ]
    },
    'educator': {
        'core': ['skill_075', 'skill_076', 'skill_078', 'skill_079', 'skill_059'],
        # Teaching, Curriculum Development, Coaching, Mentoring, Public Speaking
        'extra': ['skill_080', 'skill_077', 'skill_060', 'skill_052'],
        # E-Learning Development, Training & Development, Presentation Skills, Storytelling
        'wants': ['skill_044', 'skill_047', 'skill_002', 'skill_033'],
        'count': 45,
        'descriptions': [
            "Educator and coach helping professionals grow technical and soft skills.",
            "Curriculum designer with experience building structured learning programs.",
            "Teaching, coaching, and mentoring the next generation of professionals.",
            "Passionate educator who combines public speaking with strong curriculum development.",
            "Learning & development specialist focused on impactful training delivery.",
        ]
    },
}

# ── Name pools ─────────────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Arjun", "Priya", "Rahul", "Sneha", "Vikram", "Anika", "Rohan", "Pooja",
    "Karan", "Neha", "Amit", "Divya", "Siddharth", "Meera", "Raj", "Tara",
    "Kabir", "Ishaan", "Anaya", "Dev", "Zara", "Ayaan", "Riya", "Aditya",
    "Naina", "Vihaan", "Saanvi", "Jay", "Kiara", "Rehan", "Myra", "Aryan",
    "Sara", "Dhruv", "Avni", "Yash", "Anjali", "Nikhil", "Ira", "Manav",
    "Shreya", "Om", "Kavya", "Tarun", "Leela", "Harsh", "Simran", "Kunal",
    "Bhavya", "Rishabh", "Alex", "Maria", "James", "Sofia", "Lucas", "Emma",
    "Noah", "Olivia", "Liam", "Ava", "Mason", "Isabella", "Ethan", "Mia",
    "Oliver", "Charlotte", "William", "Amelia", "Jacob", "Harper", "Logan",
    "Evelyn", "Zoe", "Benjamin", "Chloe", "Sebastian", "Lily", "Daniel", "Ella",
]

LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Kumar", "Patel", "Gupta", "Mehta", "Joshi",
    "Shah", "Khan", "Reddy", "Rao", "Nair", "Pillai", "Iyer", "Bose",
    "Chatterjee", "Das", "Roy", "Ghosh", "Malhotra", "Kapoor", "Arora", "Chopra",
    "Srivastava", "Mishra", "Tiwari", "Pandey", "Dubey", "Saxena",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Jackson", "White",
    "Harris", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King",
]


def generate_users():
    existing_df = pd.read_csv(os.path.join(DATA_DIR, 'users.csv'))
    existing_count = len(existing_df)
    print(f"Existing users: {existing_count}")

    new_rows = []
    user_counter = existing_count + 1

    # Build a set of already-used names from existing data to avoid duplicates
    existing_names = set(existing_df['name'].tolist())

    for archetype_name, cfg in ARCHETYPES.items():
        core = cfg['core']
        extra_pool = cfg['extra']
        wants_pool = cfg['wants']
        count = cfg['count']
        descs = cfg['descriptions']

        print(f"  Generating {count} users for archetype: {archetype_name}")

        for _ in range(count):
            # Pick a unique name
            attempts = 0
            while True:
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
                if name not in existing_names:
                    existing_names.add(name)
                    break
                attempts += 1
                if attempts > 100:
                    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {random.randint(1,99)}"
                    break

            # Skills offered = all core + 1 random extra
            offered = core[:]  # all core skills — this creates the strong clustering
            if extra_pool:
                offered.append(random.choice(extra_pool))

            # Skills required = 2–3 from the wants pool
            num_wants = random.randint(2, min(3, len(wants_pool)))
            required = random.sample(wants_pool, num_wants)

            description = random.choice(descs)
            user_id = f"user_{user_counter:03d}"
            user_counter += 1

            new_rows.append({
                'user_id': user_id,
                'name': name,
                'description': description,
                'skills_offered': ','.join(offered),
                'skills_required': ','.join(required),
            })

    new_df = pd.DataFrame(new_rows)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(os.path.join(DATA_DIR, 'users.csv'), index=False)

    total = len(combined_df)
    print(f"\n✅ Done! Added {len(new_rows)} users. Total users: {total}")
    return total


if __name__ == '__main__':
    print("=" * 55)
    print("  Skill Swap — Clustered Data Generator")
    print("=" * 55)
    total = generate_users()
    print(f"\nRe-run Apriori verification:")
    print(f"  python -c \"from modules.association_engine import AssociationEngine; e=AssociationEngine(); rules=e.get_top_offer_rules(10); [print(r['antecedent_name'],'→',r['consequent_name'],'lift=',r['lift']) for r in rules]\"")
