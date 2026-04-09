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
from modules.association_engine import AssociationEngine

app = Flask(__name__)
app.secret_key = 'skill_swap_demo_secret'

# Initialize modules at startup
print("Initializing Skill Swap Platform...")
recommendation_engine = RecommendationEngine()
nlp_matcher = NLPTaskMatcher()
analytics = SkillAnalytics()
skill_graph = SkillGraph()
association_engine = AssociationEngine()
print("All modules loaded successfully!")

# Load data for templates
skills_df = pd.read_csv(config.SKILLS_FILE)


# ── Public landing page ──────────────────────────────────────
@app.route('/')
def index():
    """Landing page with skill demand analytics and ARM graph"""
    stats = analytics.get_summary_stats()
    most_offered = analytics.get_most_offered_skills(10)
    most_required = analytics.get_most_required_skills(10)
    skill_gaps = analytics.get_skill_gaps(5)
    arm_rules = association_engine.get_top_offer_rules(10)
    return render_template('index.html',
                           stats=stats,
                           most_offered=most_offered,
                           most_required=most_required,
                           skill_gaps=skill_gaps,
                           arm_rules=arm_rules)


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
    skill_gaps = analytics.get_skill_gaps(10)

    # ── Skill Suggestions (ARM + Demand) ───────────────────────
    user_offered_set = set(user['skills_offered'])
    user_required_set = set(user['skills_required'])
    already_known = user_offered_set | user_required_set

    # 1) ARM: for each skill user offers, find what usually co-occurs
    arm_suggestions = {}  # skill_id -> {name, reason, score}
    for sid in user['skills_offered']:
        for sug in association_engine.get_suggestions_for_skill(sid, context='offer', top_n=3):
            if sug['skill_id'] not in already_known and sug['skill_id'] not in arm_suggestions:
                offered_name = recommendation_engine.get_skill_name(sid)
                arm_suggestions[sug['skill_id']] = {
                    'skill_id': sug['skill_id'],
                    'skill_name': sug['skill_name'],
                    'reason': f"Often offered alongside {offered_name}",
                    'source': 'arm',
                    'score': sug['lift']
                }

    # 2) Demand: top gapped skills not already known by the user
    demand_suggestions = []
    for gap in skill_gaps:
        if gap['skill_id'] not in already_known and gap['skill_id'] not in arm_suggestions:
            demand_suggestions.append({
                'skill_id': gap['skill_id'],
                'skill_name': gap['skill_name'],
                'reason': f"{gap['demand']} users need it, only {gap['supply']} offer it",
                'source': 'demand',
                'score': gap['gap_score']
            })
        if len(demand_suggestions) >= 4:
            break

    # Combine: ARM first, then unmet demand, cap at 8
    all_suggestions = list(arm_suggestions.values())[:4] + demand_suggestions[:4]
    all_suggestions = all_suggestions[:8]

    skills_payload = skills_df[['skill_id', 'skill_name', 'category']].to_dict('records')

    return render_template('dashboard.html',
                           user=user, matches=matches,
                           stats=stats,
                           most_offered=most_offered,
                           most_required=most_required,
                           skill_gaps=skill_gaps,
                           skills_list=skills_payload,
                           suggestions=all_suggestions)


# ── Association Rule Mining APIs ─────────────────────────────
@app.route('/api/skill-network')
def api_skill_network():
    """Returns skill co-occurrence network graph data"""
    graph = association_engine.get_network_graph_data()
    return jsonify(graph)


@app.route('/api/arm-rules')
def api_arm_rules():
    """Returns top association rules for offer and require contexts"""
    return jsonify({
        'offer_rules': association_engine.get_top_offer_rules(15),
        'require_rules': association_engine.get_top_require_rules(15),
    })


@app.route('/api/arm-suggest/<skill_id>')
def api_arm_suggest(skill_id):
    """Suggest related skills based on ARM for a given skill"""
    context = request.args.get('context', 'offer')
    suggestions = association_engine.get_suggestions_for_skill(skill_id, context=context)
    return jsonify(suggestions)


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


# ── Profile page ─────────────────────────────────────────────
@app.route('/profile/<user_id>')
def profile(user_id):
    user = recommendation_engine.get_user_by_id(user_id)
    if not user:
        return "User not found", 404
    user['skills_offered_names'] = recommendation_engine.get_skill_names(user['skills_offered'])
    user['skills_required_names'] = recommendation_engine.get_skill_names(user['skills_required'])
    matches = recommendation_engine.find_mutual_matches(user_id, top_n=5)
    for match in matches:
        match['can_teach_you_names'] = recommendation_engine.get_skill_names(match['can_teach_you'])
        match['you_can_teach_names'] = recommendation_engine.get_skill_names(match['you_can_teach'])
    return render_template('profile.html', user=user, matches=matches)


# ── Browse users ──────────────────────────────────────────────
@app.route('/browse')
def browse():
    users_df = pd.read_csv(config.USERS_FILE)
    users = []
    for _, row in users_df.iterrows():
        u = row.to_dict()
        offered_ids = [s.strip() for s in str(u.get('skills_offered', '')).split(',') if s.strip()]
        required_ids = [s.strip() for s in str(u.get('skills_required', '')).split(',') if s.strip()]
        u['skills_offered_names'] = recommendation_engine.get_skill_names(offered_ids)
        u['skills_required_names'] = recommendation_engine.get_skill_names(required_ids)
        u['skills_offered_categories'] = list(set(
            skills_df[skills_df['skill_id'].isin(offered_ids)]['category'].tolist()
        ))
        users.append(u)
    skills_by_cat = {}
    for _, row in skills_df.iterrows():
        cat = row['category']
        if cat not in skills_by_cat:
            skills_by_cat[cat] = []
        skills_by_cat[cat].append(row['skill_name'])
    return render_template('browse.html', users=users, skills_by_cat=skills_by_cat)


# ── Skill-based search (dropdown selection) ──────────────────
@app.route('/api/search-skill', methods=['POST'])
def api_search_skill():
    data = request.get_json()
    skill_ids = data.get('skill_ids', [])  # list of skill_ids to search for
    if not skill_ids:
        return jsonify({'error': 'No skills provided'}), 400
    users_df = pd.read_csv(config.USERS_FILE)
    users_df['skills_offered'] = users_df['skills_offered'].apply(
        lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
    )
    skill_set = set(skill_ids)
    results = []
    for _, row in users_df.iterrows():
        offered = set(row['skills_offered'])
        matched = skill_set.intersection(offered)
        if matched:
            skill_names = [skills_df[skills_df['skill_id'] == sid]['skill_name'].values[0]
                           if not skills_df[skills_df['skill_id'] == sid].empty else sid
                           for sid in matched]
            results.append({
                'user_id': row['user_id'],
                'name': row['name'],
                'description': row['description'],
                'matched_count': len(matched),
                'matched_skills': list(matched),
                'matched_skill_names': skill_names,
            })
    results.sort(key=lambda r: r['matched_count'], reverse=True)
    return jsonify({'matches': results[:15]})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Skill Swap Platform")
    print("="*60)
    print(f"Server running at: http://localhost:{config.PORT}")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
