"""
Complete setup script for Skill Swap Platform
Creates directories, generates data files, and sets up the project
"""
import os
import csv
import random
import json

print("=" * 60)
print("Skill Swap Platform - Setup Script")
print("=" * 60)

# Step 1: Create directories
print("\n[1/5] Creating project structure...")
dirs = ['data', 'modules', 'templates', 'static', 'static/css', 'static/js']
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"  ✓ {d}/")

# Step 2: Create modules/__init__.py
print("\n[2/5] Creating module files...")
with open('modules/__init__.py', 'w') as f:
    f.write('# Skill Swap Platform - Modules Package\n')
print("  ✓ modules/__init__.py")

# Step 3: Generate skills.csv
print("\n[3/5] Generating skills dataset...")
skills_data = [
    # Programming Languages
    ('skill_001', 'Python', 'Programming'),
    ('skill_002', 'JavaScript', 'Programming'),
    ('skill_003', 'Java', 'Programming'),
    ('skill_004', 'C++', 'Programming'),
    ('skill_005', 'C#', 'Programming'),
    ('skill_006', 'Ruby', 'Programming'),
    ('skill_007', 'Go', 'Programming'),
    ('skill_008', 'Rust', 'Programming'),
    ('skill_009', 'PHP', 'Programming'),
    ('skill_010', 'TypeScript', 'Programming'),
    
    # Web Development
    ('skill_011', 'React', 'Web Development'),
    ('skill_012', 'Vue.js', 'Web Development'),
    ('skill_013', 'Angular', 'Web Development'),
    ('skill_014', 'Node.js', 'Web Development'),
    ('skill_015', 'Django', 'Web Development'),
    ('skill_016', 'Flask', 'Web Development'),
    ('skill_017', 'HTML/CSS', 'Web Development'),
    ('skill_018', 'WordPress', 'Web Development'),
    ('skill_019', 'Tailwind CSS', 'Web Development'),
    ('skill_020', 'Bootstrap', 'Web Development'),
    
    # Data Science & Analytics
    ('skill_021', 'Machine Learning', 'Data Science & Analytics'),
    ('skill_022', 'Deep Learning', 'Data Science & Analytics'),
    ('skill_023', 'Data Analysis', 'Data Science & Analytics'),
    ('skill_024', 'Statistics', 'Data Science & Analytics'),
    ('skill_025', 'SQL', 'Data Science & Analytics'),
    ('skill_026', 'Data Visualization', 'Data Science & Analytics'),
    ('skill_027', 'Excel', 'Data Science & Analytics'),
    ('skill_028', 'Tableau', 'Data Science & Analytics'),
    ('skill_029', 'Power BI', 'Data Science & Analytics'),
    ('skill_030', 'Google Analytics', 'Data Science & Analytics'),
    ('skill_031', 'Predictive Analytics', 'Data Science & Analytics'),
    ('skill_032', 'A/B Testing', 'Data Science & Analytics'),
    
    # Design & Creative
    ('skill_033', 'UI/UX Design', 'Design & Creative'),
    ('skill_034', 'Graphic Design', 'Design & Creative'),
    ('skill_035', 'Figma', 'Design & Creative'),
    ('skill_036', 'Adobe XD', 'Design & Creative'),
    ('skill_037', 'Photoshop', 'Design & Creative'),
    ('skill_038', 'Illustrator', 'Design & Creative'),
    ('skill_039', '3D Modeling', 'Design & Creative'),
    ('skill_040', 'Animation', 'Design & Creative'),
    ('skill_041', 'Video Editing', 'Design & Creative'),
    ('skill_042', 'Photography', 'Design & Creative'),
    ('skill_043', 'Brand Design', 'Design & Creative'),
    
    # Content Creation & Writing
    ('skill_044', 'Content Writing', 'Content & Writing'),
    ('skill_045', 'Copywriting', 'Content & Writing'),
    ('skill_046', 'Technical Writing', 'Content & Writing'),
    ('skill_047', 'Blogging', 'Content & Writing'),
    ('skill_048', 'Creative Writing', 'Content & Writing'),
    ('skill_049', 'Scriptwriting', 'Content & Writing'),
    ('skill_050', 'Editing & Proofreading', 'Content & Writing'),
    ('skill_051', 'Email Marketing', 'Content & Writing'),
    ('skill_052', 'Storytelling', 'Content & Writing'),
    ('skill_053', 'Journalism', 'Content & Writing'),
    
    # Marketing & Communication
    ('skill_054', 'Digital Marketing', 'Marketing & Communication'),
    ('skill_055', 'SEO', 'Marketing & Communication'),
    ('skill_056', 'Social Media Marketing', 'Marketing & Communication'),
    ('skill_057', 'Content Marketing', 'Marketing & Communication'),
    ('skill_058', 'Public Relations', 'Marketing & Communication'),
    ('skill_059', 'Public Speaking', 'Marketing & Communication'),
    ('skill_060', 'Presentation Skills', 'Marketing & Communication'),
    ('skill_061', 'Influencer Marketing', 'Marketing & Communication'),
    ('skill_062', 'Brand Strategy', 'Marketing & Communication'),
    ('skill_063', 'Community Management', 'Marketing & Communication'),
    
    # Business & Finance
    ('skill_064', 'Project Management', 'Business & Finance'),
    ('skill_065', 'Business Analysis', 'Business & Finance'),
    ('skill_066', 'Financial Analysis', 'Business & Finance'),
    ('skill_067', 'Accounting', 'Business & Finance'),
    ('skill_068', 'Budgeting', 'Business & Finance'),
    ('skill_069', 'Investment Analysis', 'Business & Finance'),
    ('skill_070', 'Business Strategy', 'Business & Finance'),
    ('skill_071', 'Entrepreneurship', 'Business & Finance'),
    ('skill_072', 'Sales', 'Business & Finance'),
    ('skill_073', 'Negotiation', 'Business & Finance'),
    ('skill_074', 'Financial Modeling', 'Business & Finance'),
    
    # Teaching & Training
    ('skill_075', 'Teaching', 'Teaching & Training'),
    ('skill_076', 'Curriculum Development', 'Teaching & Training'),
    ('skill_077', 'Training & Development', 'Teaching & Training'),
    ('skill_078', 'Coaching', 'Teaching & Training'),
    ('skill_079', 'Mentoring', 'Teaching & Training'),
    ('skill_080', 'E-Learning Development', 'Teaching & Training'),
    
    # Languages
    ('skill_081', 'Spanish', 'Languages'),
    ('skill_082', 'French', 'Languages'),
    ('skill_083', 'German', 'Languages'),
    ('skill_084', 'Mandarin Chinese', 'Languages'),
    ('skill_085', 'Japanese', 'Languages'),
    ('skill_086', 'Arabic', 'Languages'),
    ('skill_087', 'Translation', 'Languages'),
    
    # Research & Academic
    ('skill_088', 'Research Methodology', 'Research & Academic'),
    ('skill_089', 'Academic Writing', 'Research & Academic'),
    ('skill_090', 'Literature Review', 'Research & Academic'),
    ('skill_091', 'Survey Design', 'Research & Academic'),
    ('skill_092', 'Qualitative Research', 'Research & Academic'),
    ('skill_093', 'Quantitative Research', 'Research & Academic'),
    
    # Mobile & Tech
    ('skill_094', 'iOS Development', 'Mobile Development'),
    ('skill_095', 'Android Development', 'Mobile Development'),
    ('skill_096', 'React Native', 'Mobile Development'),
    ('skill_097', 'Flutter', 'Mobile Development'),
    
    # DevOps & Cloud
    ('skill_098', 'AWS', 'DevOps & Cloud'),
    ('skill_099', 'Docker', 'DevOps & Cloud'),
    ('skill_100', 'Kubernetes', 'DevOps & Cloud'),
    ('skill_101', 'CI/CD', 'DevOps & Cloud'),
    ('skill_102', 'Git', 'DevOps & Cloud'),
    
    # Other Professional Skills
    ('skill_103', 'Agile/Scrum', 'Other'),
    ('skill_104', 'Testing/QA', 'Other'),
    ('skill_105', 'Cybersecurity', 'Other'),
    ('skill_106', 'Game Development', 'Other'),
    ('skill_107', 'Blockchain', 'Other'),
    ('skill_108', 'HR Management', 'Other'),
    ('skill_109', 'Customer Service', 'Other'),
    ('skill_110', 'Event Planning', 'Other'),
]

with open('data/skills.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['skill_id', 'skill_name', 'category'])
    writer.writerows(skills_data)

print(f"  ✓ Generated {len(skills_data)} skills in data/skills.csv")

# Step 4: Generate skill relationships
print("\n[4/5] Generating skill relationships...")
relationships = [
    # Programming relationships
    ('skill_002', 'skill_011', 0.9),  # JavaScript -> React
    ('skill_002', 'skill_012', 0.9),  # JavaScript -> Vue.js
    ('skill_002', 'skill_013', 0.9),  # JavaScript -> Angular
    ('skill_002', 'skill_014', 0.95), # JavaScript -> Node.js
    ('skill_010', 'skill_002', 0.85), # TypeScript -> JavaScript
    ('skill_011', 'skill_096', 0.85), # React -> React Native
    
    # Python relationships
    ('skill_001', 'skill_015', 0.85), # Python -> Django
    ('skill_001', 'skill_016', 0.85), # Python -> Flask
    ('skill_001', 'skill_021', 0.9),  # Python -> Machine Learning
    ('skill_001', 'skill_023', 0.85), # Python -> Data Analysis
    
    # Data Science & Analytics relationships
    ('skill_021', 'skill_022', 0.85), # ML -> Deep Learning
    ('skill_023', 'skill_024', 0.9),  # Data Analysis -> Statistics
    ('skill_023', 'skill_026', 0.9),  # Data Analysis -> Visualization
    ('skill_023', 'skill_025', 0.95), # Data Analysis -> SQL
    ('skill_023', 'skill_027', 0.85), # Data Analysis -> Excel
    ('skill_026', 'skill_028', 0.85), # Visualization -> Tableau
    ('skill_026', 'skill_029', 0.85), # Visualization -> Power BI
    ('skill_027', 'skill_028', 0.75), # Excel -> Tableau
    ('skill_027', 'skill_029', 0.75), # Excel -> Power BI
    ('skill_030', 'skill_032', 0.8),  # Google Analytics -> A/B Testing
    ('skill_024', 'skill_031', 0.8),  # Statistics -> Predictive Analytics
    
    # Design relationships
    ('skill_033', 'skill_035', 0.95), # UI/UX -> Figma
    ('skill_033', 'skill_036', 0.9),  # UI/UX -> Adobe XD
    ('skill_034', 'skill_037', 0.9),  # Graphic Design -> Photoshop
    ('skill_034', 'skill_038', 0.9),  # Graphic Design -> Illustrator
    ('skill_034', 'skill_043', 0.85), # Graphic Design -> Brand Design
    ('skill_041', 'skill_042', 0.8),  # Video Editing -> Photography
    
    # Content & Writing relationships
    ('skill_044', 'skill_045', 0.85), # Content Writing -> Copywriting
    ('skill_044', 'skill_047', 0.9),  # Content Writing -> Blogging
    ('skill_044', 'skill_050', 0.8),  # Content Writing -> Editing
    ('skill_045', 'skill_051', 0.85), # Copywriting -> Email Marketing
    ('skill_045', 'skill_052', 0.8),  # Copywriting -> Storytelling
    ('skill_046', 'skill_050', 0.85), # Technical Writing -> Editing
    ('skill_047', 'skill_057', 0.85), # Blogging -> Content Marketing
    ('skill_048', 'skill_049', 0.8),  # Creative Writing -> Scriptwriting
    ('skill_053', 'skill_044', 0.75), # Journalism -> Content Writing
    
    # Marketing & Communication relationships
    ('skill_054', 'skill_055', 0.9),  # Digital Marketing -> SEO
    ('skill_054', 'skill_056', 0.9),  # Digital Marketing -> Social Media
    ('skill_054', 'skill_057', 0.9),  # Digital Marketing -> Content Marketing
    ('skill_055', 'skill_057', 0.85), # SEO -> Content Marketing
    ('skill_056', 'skill_063', 0.8),  # Social Media -> Community Management
    ('skill_057', 'skill_044', 0.85), # Content Marketing -> Content Writing
    ('skill_058', 'skill_059', 0.8),  # PR -> Public Speaking
    ('skill_059', 'skill_060', 0.85), # Public Speaking -> Presentations
    ('skill_061', 'skill_056', 0.8),  # Influencer Marketing -> Social Media
    ('skill_062', 'skill_043', 0.8),  # Brand Strategy -> Brand Design
    
    # Business & Finance relationships
    ('skill_064', 'skill_065', 0.85), # Project Management -> Business Analysis
    ('skill_064', 'skill_103', 0.9),  # Project Management -> Agile/Scrum
    ('skill_065', 'skill_023', 0.8),  # Business Analysis -> Data Analysis
    ('skill_066', 'skill_067', 0.85), # Financial Analysis -> Accounting
    ('skill_066', 'skill_074', 0.9),  # Financial Analysis -> Financial Modeling
    ('skill_067', 'skill_068', 0.9),  # Accounting -> Budgeting
    ('skill_068', 'skill_074', 0.8),  # Budgeting -> Financial Modeling
    ('skill_069', 'skill_074', 0.85), # Investment Analysis -> Financial Modeling
    ('skill_070', 'skill_071', 0.85), # Business Strategy -> Entrepreneurship
    ('skill_072', 'skill_073', 0.8),  # Sales -> Negotiation
    
    # Teaching & Training relationships
    ('skill_075', 'skill_076', 0.85), # Teaching -> Curriculum Development
    ('skill_075', 'skill_078', 0.8),  # Teaching -> Coaching
    ('skill_076', 'skill_080', 0.85), # Curriculum Dev -> E-Learning
    ('skill_077', 'skill_078', 0.85), # Training -> Coaching
    ('skill_078', 'skill_079', 0.9),  # Coaching -> Mentoring
    
    # Languages relationships
    ('skill_081', 'skill_087', 0.7),  # Spanish -> Translation
    ('skill_082', 'skill_087', 0.7),  # French -> Translation
    ('skill_083', 'skill_087', 0.7),  # German -> Translation
    ('skill_084', 'skill_087', 0.7),  # Mandarin -> Translation
    
    # Research relationships
    ('skill_088', 'skill_089', 0.85), # Research -> Academic Writing
    ('skill_088', 'skill_090', 0.9),  # Research -> Literature Review
    ('skill_088', 'skill_091', 0.85), # Research -> Survey Design
    ('skill_092', 'skill_093', 0.75), # Qualitative -> Quantitative
    ('skill_089', 'skill_046', 0.75), # Academic Writing -> Technical Writing
    
    # Mobile relationships
    ('skill_002', 'skill_096', 0.85), # JavaScript -> React Native
    ('skill_011', 'skill_096', 0.9),  # React -> React Native
    
    # DevOps relationships
    ('skill_099', 'skill_100', 0.85), # Docker -> Kubernetes
    ('skill_098', 'skill_099', 0.8),  # AWS -> Docker
    ('skill_101', 'skill_102', 0.85), # CI/CD -> Git
    
    # Web Development relationships
    ('skill_017', 'skill_019', 0.8),  # HTML/CSS -> Tailwind
    ('skill_017', 'skill_020', 0.8),  # HTML/CSS -> Bootstrap
    
    # Cross-category relationships
    ('skill_030', 'skill_054', 0.75), # Google Analytics -> Digital Marketing
    ('skill_032', 'skill_054', 0.7),  # A/B Testing -> Digital Marketing
    ('skill_042', 'skill_043', 0.8),  # Photography -> Brand Design
    ('skill_051', 'skill_054', 0.8),  # Email Marketing -> Digital Marketing
]

with open('data/skill_relationships.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['skill_from', 'skill_to', 'similarity_weight'])
    writer.writerows(relationships)

print(f"  ✓ Generated {len(relationships)} relationships in data/skill_relationships.csv")

# Step 5: Generate synthetic user data (200 users)
print("\n[5/5] Generating 200 synthetic user profiles...")

first_names = [
    'Alex', 'Sarah', 'Michael', 'Emily', 'David', 'Jessica', 'James', 'Emma',
    'John', 'Sophia', 'Robert', 'Olivia', 'William', 'Ava', 'Richard', 'Isabella',
    'Thomas', 'Mia', 'Charles', 'Charlotte', 'Daniel', 'Amelia', 'Matthew', 'Harper',
    'Christopher', 'Evelyn', 'Andrew', 'Abigail', 'Joshua', 'Ella', 'Ryan', 'Scarlett',
    'Kevin', 'Grace', 'Brian', 'Chloe', 'Steven', 'Victoria', 'Timothy', 'Madison',
    'Jason', 'Luna', 'Eric', 'Hannah', 'Jeffrey', 'Lily', 'Jacob', 'Zoe',
    'Nicholas', 'Layla', 'Brandon', 'Penelope', 'Samuel', 'Aria', 'Benjamin', 'Ellie'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas',
    'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris',
    'Clark', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright',
    'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson',
    'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts', 'Gomez'
]

descriptions_templates = [
    "Passionate {category} professional with {years} years of experience. Love teaching and collaborating on projects.",
    "Enthusiastic learner exploring {category}. Seeking to expand my skillset through knowledge exchange.",
    "Experienced in {category} and eager to share what I know while learning new skills.",
    "Self-taught {category} specialist. Believe in the power of community learning and skill sharing.",
    "{category} expert looking to diversify skills. Open to teaching and mentoring.",
    "Career changer passionate about {category}. Excited to learn from and teach others.",
    "Freelancer specializing in {category}. Always looking to expand my toolkit.",
    "Creative professional with background in {category}. Love collaborative learning.",
    "Professional with interest in {category}. Enjoy helping others grow their skills.",
    "Problem solver focused on {category}. Keen to exchange knowledge with like-minded individuals.",
    "Consultant in {category} field. Dedicated to continuous learning and skill development.",
    "Educator specializing in {category}. Passionate about sharing knowledge and learning from others.",
]

skill_ids = [s[0] for s in skills_data]
skill_names = {s[0]: s[1] for s in skills_data}
skill_categories = {s[0]: s[2] for s in skills_data}

users = []
for i in range(1, 201):
    user_id = f'user_{i:03d}'
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Select 2-5 skills to offer
    num_offered = random.randint(2, 5)
    skills_offered = random.sample(skill_ids, num_offered)
    
    # Select 2-4 skills to learn (ensure no overlap with offered)
    available_to_learn = [s for s in skill_ids if s not in skills_offered]
    num_required = random.randint(2, 4)
    skills_required = random.sample(available_to_learn, num_required)
    
    # Create description
    primary_category = skill_categories[skills_offered[0]]
    years = random.choice([2, 3, 4, 5, 7, 10])
    description = random.choice(descriptions_templates).format(
        category=primary_category,
        years=years
    )
    
    users.append({
        'user_id': user_id,
        'name': name,
        'description': description,
        'skills_offered': ','.join(skills_offered),
        'skills_required': ','.join(skills_required)
    })

with open('data/users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id', 'name', 'description', 'skills_offered', 'skills_required'])
    writer.writeheader()
    writer.writerows(users)

print(f"  ✓ Generated 200 user profiles in data/users.csv")

print("\n" + "=" * 60)
print("✓ Setup Complete!")
print("=" * 60)
print("\nProject structure:")
print("  ├── data/")
print("  │   ├── skills.csv (75 skills)")
print("  │   ├── skill_relationships.csv (38 relationships)")
print("  │   └── users.csv (200 users)")
print("  ├── modules/")
print("  ├── templates/")
print("  ├── static/css/")
print("  ├── static/js/")
print("  ├── config.py")
print("  └── requirements.txt")
print("\nNext: Install dependencies with: pip install -r requirements.txt")
