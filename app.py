"""
Skill Swap Platform - Flask Application
Simplified: Landing, Login, Onboarding, Dashboard
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import config
from modules.recommendation_engine import RecommendationEngine
from modules.nlp_matcher import NLPTaskMatcher
from modules.analytics import SkillAnalytics
from modules.skill_graph import SkillGraph

app = Flask(__name__)
app.secret_key = 'skill_swap_demo_secret'

# Initialize modules at startup
print("Initializing Skill Swap Platform...")
recommendation_engine = RecommendationEngine()
nlp_matcher = NLPTaskMatcher()
analytics = SkillAnalytics()
skill_graph = SkillGraph()
print("All modules loaded successfully!")

# Load data for templates
skills_df = pd.read_csv(config.SKILLS_FILE)


# ── Public landing page ──────────────────────────────────────
@app.route('/')
def index():
    """Landing page with skill demand analytics"""
    stats = analytics.get_summary_stats()
    most_offered = analytics.get_most_offered_skills(10)
    most_required = analytics.get_most_required_skills(10)
    skill_gaps = analytics.get_skill_gaps(5)
    return render_template('index.html',
                           stats=stats,
                           most_offered=most_offered,
                           most_required=most_required,
                           skill_gaps=skill_gaps)


# ── Auth ─────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'demo' and password == 'demo':
            session['user_id'] = 'user_001'
            return redirect(url_for('onboarding'))
        else:
            return render_template('login.html', error='Invalid credentials. Try demo/demo.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ── Onboarding (select skills) ──────────────────────────────
@app.route('/onboarding')
def onboarding():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = recommendation_engine.get_user_by_id(user_id)
    if not user:
        return redirect(url_for('login'))
    skills_payload = skills_df[['skill_id', 'skill_name', 'category']].to_dict('records')
    return render_template('onboarding.html', user=user, skills=skills_payload)


@app.route('/api/save-onboarding', methods=['POST'])
def api_save_onboarding():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    skills_offered = data.get('skills_offered', [])
    skills_required = data.get('skills_required', [])
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    ok = recommendation_engine.update_user_full(
        user_id, name, description, skills_offered, skills_required
    )
    if not ok:
        return jsonify({'error': 'Failed to save'}), 500
    return jsonify({'redirect': '/dashboard'})


# ── Dashboard (everything after login) ──────────────────────
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = recommendation_engine.get_user_by_id(user_id)
    if not user:
        return redirect(url_for('login'))

    # Skill names for display
    user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
    user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])

    # Mutual matches
    matches = recommendation_engine.find_mutual_matches(user_id, top_n=10)
    for match in matches:
        match['can_teach_you_names'] = recommendation_engine.get_skill_names(match['can_teach_you'])
        match['you_can_teach_names'] = recommendation_engine.get_skill_names(match['you_can_teach'])

    # Analytics
    stats = analytics.get_summary_stats()
    most_offered = analytics.get_most_offered_skills(10)
    most_required = analytics.get_most_required_skills(10)
    skill_gaps = analytics.get_skill_gaps(5)

    return render_template('dashboard.html',
                           user=user, matches=matches,
                           stats=stats,
                           most_offered=most_offered,
                           most_required=most_required,
                           skill_gaps=skill_gaps)


# ── Task search API (used by dashboard AJAX) ────────────────
@app.route('/api/search-task', methods=['POST'])
def api_search_task():
    data = request.get_json()
    task_description = data.get('task_description', '')
    if not task_description:
        return jsonify({'error': 'Task description is required'}), 400
    matches = nlp_matcher.find_matches_for_task(task_description, top_n=10)
    for match in matches:
        match['matched_skills_names'] = nlp_matcher.get_skill_names(match['matched_skills'])
        match['skills_offered_names'] = nlp_matcher.get_skill_names(match['skills_offered'])
    return jsonify({'task': task_description, 'matches': matches})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Skill Swap Platform")
    print("="*60)
    print(f"Server running at: http://localhost:{config.PORT}")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
