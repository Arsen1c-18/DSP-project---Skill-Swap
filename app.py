"""
Skill Swap Platform - Flask Application
Main application with routes for all features
"""
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import config
from modules.recommendation_engine import RecommendationEngine
from modules.nlp_matcher import NLPTaskMatcher
from modules.analytics import SkillAnalytics
from modules.skill_graph import SkillGraph

app = Flask(__name__)

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
    """Landing page with integrated analytics dashboard"""
    # Get analytics data
    stats = analytics.get_summary_stats()
    most_offered = analytics.get_most_offered_skills(10)
    most_required = analytics.get_most_required_skills(10)
    skill_gaps = analytics.get_skill_gaps(5)
    
    return render_template('index.html', 
                         stats=stats,
                         most_offered=most_offered,
                         most_required=most_required,
                         skill_gaps=skill_gaps)


@app.route('/home')
def home():
    """Home page with recommendations (demo: showing recommendations for a sample user)"""
    # For demo, use first user or random user
    sample_user_id = 'user_001'
    user = recommendation_engine.get_user_by_id(sample_user_id)
    
    if not user:
        # Get random user
        users = recommendation_engine.get_random_users(1)
        if users:
            user = users[0]
            sample_user_id = user['user_id']
    
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
    
    # Get all skills grouped by category for the dropdown
    # We group by category and get a list of skill names for each
    skills_by_cat = skills_df.groupby('category')['skill_name'].apply(list).to_dict()
    
    # Convert skill IDs to names for display and categories for filtering
    for user in users:
        # Get skill names
        user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
        user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
        
        # Get categories for offered skills to enable category filtering
        # Filter skills_df for the IDs this user offers and get unique categories
        user_offered_ids = user['skills_offered']
        user['skills_offered_categories'] = list(set(skills_df[skills_df['skill_id'].isin(user_offered_ids)]['category'].tolist()))
    
    return render_template('browse.html', users=users, skills_by_cat=skills_by_cat)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Skill Swap Platform")
    print("="*60)
    print(f"Server running at: http://localhost:{config.PORT}")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
