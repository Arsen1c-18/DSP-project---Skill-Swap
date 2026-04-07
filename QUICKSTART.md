# 🚀 Quick Start Guide - Skill Swap Platform

## Start the Application

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

## Explore Features

### 🏠 Landing Page
- View platform statistics
- Learn about features
- Navigate to different sections

### 🤝 Recommendations (`/home`)
- See mutual skill matches
- View bidirectional exchange opportunities
- Click profiles to learn more

### 🔍 Task Search (`/task-search`)
**Try these example searches:**
- "I need help with financial analysis and creating Excel dashboards"
- "Looking for someone to help me improve my content writing for blogs"
- "Need a Spanish tutor to practice conversational skills"
- "Want to learn UI/UX design and master Figma"
- "Help me with digital marketing strategy and SEO optimization"
- "Looking for a mentor in business strategy and entrepreneurship"

### 📊 Analytics Dashboard (`/dashboard`)
- Interactive Plotly charts
- Most offered/required skills
- Supply vs demand comparison
- Skill gap analysis (what to learn!)

### 👥 Browse Users (`/browse`)
- Search all 200 users
- Filter by skills or name
- View detailed profiles

## Testing the Platform

### Test Recommendation Engine
```bash
cd modules
python recommendation_engine.py
```

### Test NLP Matcher
```bash
cd modules
python nlp_matcher.py
```

### Test Analytics
```bash
cd modules
python analytics.py
```

### Test Skill Graph
```bash
cd modules
python skill_graph.py
```

## Troubleshooting

**Issue: Module not found error**
```bash
pip install -r requirements.txt
```

**Issue: Port 5000 already in use**
Edit `config.py` and change PORT to a different number (e.g., 5001)

**Issue: Data files not found**
Run setup script:
```bash
python setup_project.py
```

## Key Files to Explore

- `app.py` - Flask routes and API endpoints
- `modules/recommendation_engine.py` - Mutual matching algorithm
- `modules/nlp_matcher.py` - TF-IDF and cosine similarity
- `modules/analytics.py` - Statistical calculations
- `modules/skill_graph.py` - Relationship graph
- `templates/` - HTML pages
- `static/css/style.css` - All styling

## Project Highlights

✅ **200 synthetic users** with diverse skill profiles  
✅ **110 skills** across 12 categories:
   - Programming & Web Development
   - Data Science & Analytics
   - Design & Creative
   - Content & Writing
   - Marketing & Communication
   - Business & Finance
   - Teaching & Training
   - Languages
   - Research & Academic
   - Mobile Development
   - DevOps & Cloud
   - Other Professional Skills  
✅ **81+ skill relationships** for smart recommendations  
✅ **NLP-powered** task matching  
✅ **Interactive analytics** with Plotly  
✅ **No authentication needed** - demo mode!

---

Enjoy exploring! 🎉
