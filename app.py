"""
Skill Swap Platform - Flask Application
Main application with routes for all features
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pandas as pd
import json
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
print("✓ All modules loaded successfully!")

# Load data for templates
skills_df = pd.read_csv(config.SKILLS_FILE)
users_df = pd.read_csv(config.USERS_FILE)


@app.route('/')
def index():
    """Landing page"""
    stats = analytics.get_summary_stats()
    return render_template('index.html', stats=stats)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'demo' and password == 'demo':
            session['user_id'] = 'user_001'
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials. Try demo/demo.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = recommendation_engine.get_user_by_id(user_id)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if recommendation_engine.update_user(user_id, name, description):
            return redirect(url_for('profile', user_id=user_id))
    
    return render_template('edit_profile.html', user=user)


@app.route('/home')
def home():
    """Home page with recommendations"""
    sample_user_id = session.get('user_id')
    
    if not sample_user_id:
        return redirect(url_for('login'))

    user = recommendation_engine.get_user_by_id(sample_user_id)
    
    if not user:
        return redirect(url_for('login'))
    
    # Get recommendations
    matches = recommendation_engine.find_mutual_matches(sample_user_id, top_n=10)
    
    # Convert skill IDs to names
    user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
    user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
    
    for match in matches:
        match['can_teach_you_names'] = recommendation_engine.get_skill_names(match['can_teach_you'])
        match['you_can_teach_names'] = recommendation_engine.get_skill_names(match['you_can_teach'])
    
    return render_template('home.html', user=user, matches=matches)


@app.route('/profile/<user_id>')
def profile(user_id):
    """View detailed user profile"""
    user = recommendation_engine.get_user_by_id(user_id)
    
    if not user:
        return "User not found", 404
    
    # Convert skill IDs to names
    user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
    user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
    
    # Get recommendations for this user
    matches = recommendation_engine.find_mutual_matches(user_id, top_n=5)
    for match in matches:
        match['can_teach_you_names'] = recommendation_engine.get_skill_names(match['can_teach_you'])
        match['you_can_teach_names'] = recommendation_engine.get_skill_names(match['you_can_teach'])
    
    return render_template('profile.html', user=user, matches=matches)


@app.route('/task-search')
def task_search():
    """Task-based search page"""
    return render_template('task_search.html')


@app.route('/api/search-task', methods=['POST'])
def api_search_task():
    """API endpoint for task-based search"""
    data = request.get_json()
    task_description = data.get('task_description', '')
    
    if not task_description:
        return jsonify({'error': 'Task description is required'}), 400
    
    # Find matches
    matches = nlp_matcher.find_matches_for_task(task_description, top_n=10)
    
    # Convert skill IDs to names
    for match in matches:
        match['matched_skills_names'] = nlp_matcher.get_skill_names(match['matched_skills'])
        match['skills_offered_names'] = nlp_matcher.get_skill_names(match['skills_offered'])
    
    return jsonify({
        'task': task_description,
        'matches': matches
    })


@app.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    # Get analytics data
    most_offered = analytics.get_most_offered_skills(15)
    most_required = analytics.get_most_required_skills(15)
    supply_demand = analytics.get_supply_demand_comparison(15)
    skill_gaps = analytics.get_skill_gaps(10)
    stats = analytics.get_summary_stats()
    category_dist = analytics.get_category_distribution()
    
    return render_template('dashboard.html',
                         most_offered=most_offered,
                         most_required=most_required,
                         supply_demand=supply_demand,
                         skill_gaps=skill_gaps,
                         stats=stats,
                         category_dist=category_dist)


@app.route('/api/analytics/most-offered')
def api_most_offered():
    """API for most offered skills"""
    top_n = request.args.get('top_n', 15, type=int)
    data = analytics.get_most_offered_skills(top_n)
    return jsonify(data)


@app.route('/api/analytics/most-required')
def api_most_required():
    """API for most required skills"""
    top_n = request.args.get('top_n', 15, type=int)
    data = analytics.get_most_required_skills(top_n)
    return jsonify(data)


@app.route('/api/analytics/supply-demand')
def api_supply_demand():
    """API for supply vs demand comparison"""
    top_n = request.args.get('top_n', 15, type=int)
    data = analytics.get_supply_demand_comparison(top_n)
    return jsonify(data)


@app.route('/api/analytics/skill-gaps')
def api_skill_gaps():
    """API for skill gaps"""
    top_n = request.args.get('top_n', 10, type=int)
    data = analytics.get_skill_gaps(top_n)
    return jsonify(data)


@app.route('/api/user/<user_id>')
def api_get_user(user_id):
    """API to get user profile"""
    user = recommendation_engine.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Convert skill IDs to names
    user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
    user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
    
    return jsonify(user)


@app.route('/api/recommendations/<user_id>')
def api_get_recommendations(user_id):
    """API to get recommendations for a user"""
    top_n = request.args.get('top_n', 10, type=int)
    matches = recommendation_engine.find_mutual_matches(user_id, top_n)
    
    # Convert skill IDs to names
    for match in matches:
        match['can_teach_you_names'] = recommendation_engine.get_skill_names(match['can_teach_you'])
        match['you_can_teach_names'] = recommendation_engine.get_skill_names(match['you_can_teach'])
    
    return jsonify(matches)


@app.route('/browse')
def browse_users():
    """Browse all users"""
    users = recommendation_engine.get_all_users()
    
    # Convert skill IDs to names for display
    for user in users:
        user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
        user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
    
    return render_template('browse.html', users=users)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Skill Swap Platform")
    print("="*60)
    print(f"Server running at: http://localhost:{config.PORT}")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
