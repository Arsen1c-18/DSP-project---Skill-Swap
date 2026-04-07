# 🔄 Skill Swap Platform

A **data science-powered skill exchange platform** where users can connect with others to exchange skills through intelligent matching, NLP-based task search, and analytics-driven insights.

![Platform Type](https://img.shields.io/badge/Platform-Web-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Science Components](#data-science-components)
- [Screenshots](#screenshots)
- [Future Enhancements](#future-enhancements)

## 🎯 Overview

The Skill Swap Platform demonstrates the practical application of data science concepts in a real-world web application. Users can:
- Exchange skills with others through intelligent mutual matching
- Find help for specific tasks using natural language processing
- Discover skill trends and market gaps through interactive analytics
- Connect with users who have related (not just exact) skills

**Demo Mode**: No authentication required - explore all features immediately!

## ✨ Features

### 1. 🤝 Mutual Skill Matching
- **Bidirectional Recommendation Engine**: Finds users where both parties can teach and learn from each other
- **Smart Scoring Algorithm**: Prioritizes perfect matches (mutual exchange) over one-way matches
- **Match Quality Metrics**: Clear visualization of what skills can be exchanged
- **Diverse Skills**: Covers tech, creative, business, content, language, and academic skills

### 2. 🔍 NLP-Powered Task Search
- **Natural Language Input**: Describe your project in plain English
- **TF-IDF Vectorization**: Extracts relevant skills from task descriptions
- **Cosine Similarity Ranking**: Combines skill matching + text similarity for optimal results
- **Smart Matching**: Finds users based on both exact and contextual skill relevance
- **Cross-Domain Support**: Works for technical, creative, business, and content tasks

### 3. 📊 Interactive Analytics Dashboard
- **Supply Analysis**: Most offered skills across the platform
- **Demand Analysis**: Most requested skills by users
- **Gap Analysis**: Skills with high demand but low supply (skills you should learn!)
- **Visual Insights**: Interactive Plotly charts with hover details and zoom

### 4. 🔗 Skill Relationship Graph
- **Related Skill Recommendations**: Python → Machine Learning → Data Science
- **Graph Traversal**: Finds connections between seemingly unrelated skills
- **Enhanced Matching**: Suggests users with related skills, not just exact matches

### 5. 👥 User Browsing
- **Search & Filter**: Find users by name, skills, or category
- **Profile Pages**: Detailed view of user skills and recommendations
- **200 Synthetic Users**: Pre-populated with realistic, diverse skill combinations

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 3.0**: Lightweight web framework
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: TF-IDF vectorization and cosine similarity
- **NumPy**: Numerical computations

### Frontend
- **HTML5/CSS3**: Structure and styling
- **JavaScript (Vanilla)**: Interactive features
- **Plotly.js**: Interactive data visualizations
- **Responsive Design**: Mobile-friendly interface

### Data Storage
- **CSV Files**: Simple, portable data storage
  - `skills.csv`: **110 skills** across **12 categories**
  - `users.csv`: 200 synthetic user profiles
  - `skill_relationships.csv`: 81+ skill connections

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download
```bash
cd "path/to/DSP NEW PROJECT"
```

### Step 2: Set Up Project Structure
```bash
python setup_project.py
```

This creates directories and generates:
- ✅ **110 skills** across 12 diverse categories:
  - Programming (10 skills)
  - Web Development (10 skills)
  - Data Science & Analytics (12 skills)
  - Design & Creative (11 skills)
  - Content & Writing (10 skills)
  - Marketing & Communication (10 skills)
  - Business & Finance (11 skills)
  - Teaching & Training (6 skills)
  - Languages (7 skills)
  - Research & Academic (6 skills)
  - Mobile Development (4 skills)
  - DevOps & Cloud (5 skills)
  - Other Professional Skills (8 skills)
- ✅ 200 synthetic user profiles with diverse backgrounds
- ✅ 81 skill relationship mappings for intelligent recommendations

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Dependencies installed:
- Flask (web framework)
- pandas (data processing)
- numpy (numerical operations)
- scikit-learn (NLP & ML algorithms)
- nltk (natural language processing)
- plotly (interactive visualizations)

### Step 4: Run the Application
```bash
python app.py
```

The server will start at: **http://localhost:5000**

## 💻 Usage

### Navigate the Platform

1. **Landing Page** (`/`)
   - Overview of platform features and statistics
   - Quick access to all features

2. **Recommendations** (`/home`)
   - View skill exchange matches for a demo user
   - See mutual exchange opportunities
   - Click to view detailed profiles

3. **Task Search** (`/task-search`)
   - Enter a task description (e.g., "build a React website")
   - Get ranked results based on skill + text similarity
   - Example searches provided for quick testing

4. **Analytics Dashboard** (`/dashboard`)
   - Interactive Plotly charts
   - Most offered/requested skills
   - Supply vs demand comparison
   - Skill gap analysis (learn these skills!)

5. **Browse Users** (`/browse`)
   - Search all 200 users
   - Filter by skills or categories
   - View detailed profiles

### Example Workflows

**Find a Skill Partner:**
1. Go to `/home`
2. View recommendations for demo user
3. Click "View Profile" on any match
4. See what you can teach each other

**Search for Project Help:**
1. Go to `/task-search`
2. Enter examples like:
   - "I need help with financial analysis and Excel dashboards"
   - "Looking for someone to help with content writing and SEO"
   - "Need a Spanish tutor to improve my conversational skills"
   - "Want to learn UI/UX design with Figma"
3. View ranked experts with relevant skills
4. Check their profiles

**Discover Trending Skills:**
1. Go to `/dashboard`
2. Review "Skill Gap Analysis" chart
3. Identify high-demand, low-supply skills
4. Plan your learning path

## 📁 Project Structure

```
DSP NEW PROJECT/
├── app.py                          # Flask application (main entry point)
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── setup_project.py                # Setup script (run once)
│
├── data/                           # Data files (CSV)
│   ├── skills.csv                  # 75 skills with categories
│   ├── users.csv                   # 200 user profiles
│   └── skill_relationships.csv     # Skill connection graph
│
├── modules/                        # Core Python modules
│   ├── __init__.py
│   ├── recommendation_engine.py    # Mutual skill matching
│   ├── nlp_matcher.py              # NLP task search
│   ├── analytics.py                # Statistics & insights
│   └── skill_graph.py              # Skill relationships
│
├── templates/                      # HTML templates
│   ├── index.html                  # Landing page
│   ├── home.html                   # Recommendations
│   ├── profile.html                # User profile
│   ├── task_search.html            # Task search
│   ├── dashboard.html              # Analytics
│   └── browse.html                 # User browser
│
└── static/                         # Static assets
    ├── css/
    │   └── style.css               # Main stylesheet
    └── js/
        └── (inline JS in templates)
```

## 🧠 Data Science Components

### 1. Recommendation Engine (`modules/recommendation_engine.py`)
**Algorithm:**
```python
match_score = (total_matched_skills × 0.4) + (bidirectional_skills × 0.6) + perfect_match_bonus
```

**Features:**
- Finds users where A can teach B AND B can teach A
- Prioritizes mutual exchange (bidirectional matches)
- Configurable minimum match threshold

### 2. NLP Task Matcher (`modules/nlp_matcher.py`)
**Techniques:**
- **TF-IDF Vectorization**: Converts text to numerical vectors
- **Keyword Extraction**: Identifies skills in task descriptions
- **Cosine Similarity**: Measures text similarity (0-1 scale)

**Combined Score:**
```python
final_score = (skill_match × 0.6) + (text_similarity × 0.4)
```

### 3. Analytics Engine (`modules/analytics.py`)
**Metrics Computed:**
- **Supply**: Count of users offering each skill
- **Demand**: Count of users requesting each skill
- **Gap Score**: Demand - Supply (identifies learning opportunities)
- **Category Distribution**: Skills grouped by category

**Use Cases:**
- Identify trending skills
- Find underserved skill areas
- Guide learning decisions

### 4. Skill Graph (`modules/skill_graph.py`)
**Graph Structure:**
- Nodes: Skills
- Edges: Relationships with similarity weights (0-1)
- Bidirectional connections

**Features:**
- **Graph Traversal**: Find related skills (BFS)
- **Skill Expansion**: Include similar skills in searches
- **Path Finding**: Discover skill progression paths

## 🖼️ Screenshots

### Landing Page
Clean, modern interface with platform statistics and feature overview.

### Recommendations Page
Mutual match cards showing bidirectional skill exchange opportunities.

### Task Search
NLP-powered search with example prompts and ranked results.

### Analytics Dashboard
Interactive Plotly charts with supply/demand insights and skill gaps.

## 🎓 Educational Value

This project demonstrates:
- **Recommendation Systems**: Collaborative filtering concepts
- **NLP Techniques**: TF-IDF, vectorization, similarity metrics
- **Data Analytics**: Aggregation, statistical analysis
- **Graph Algorithms**: BFS, relationship mapping
- **Full-Stack Integration**: Backend AI + frontend visualization
- **Data Pipeline**: CSV → Pandas → Scikit-learn → Plotly

## 🔮 Future Enhancements

### Short-term
- [ ] User authentication (sign up/login)
- [ ] Real-time skill matching notifications
- [ ] User ratings and skill endorsements
- [ ] Direct messaging between matches

### Long-term
- [ ] Machine learning-based match prediction
- [ ] Collaborative filtering for recommendations
- [ ] Skill progress tracking
- [ ] Integration with online learning platforms
- [ ] Mobile app (React Native/Flutter)
- [ ] Database migration (PostgreSQL/MongoDB)

## 📄 License

This project is created for educational purposes. Feel free to use and modify for learning.

## 👨‍💻 About

Created as a demonstration of data science concepts in web applications:
- Recommendation systems
- Natural language processing
- Data visualization
- Graph algorithms
- Full-stack development

---

**Questions or Feedback?**
This is a demo project showcasing data science + web development integration. Explore the code to understand how recommendation engines, NLP, and analytics work together!

🚀 **Start exploring**: `python app.py` and visit http://localhost:5000
