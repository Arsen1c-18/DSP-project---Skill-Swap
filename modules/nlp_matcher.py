"""
NLP-based Task Matcher for Skill Swap Platform
Uses TF-IDF + cosine similarity + keyword expansion to match task
descriptions with user profiles. Always returns results for any input.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import re
import config


# ── Keyword → skill_id expansion map ─────────────────────────────────────────
# Maps everyday task words (not formal skill names) to relevant skill IDs.
# This is the layer that makes "website", "login", "payment" produce results.
TASK_KEYWORDS = {
    # Web / frontend
    'website':        ['skill_011', 'skill_017', 'skill_002', 'skill_019'],
    'web':            ['skill_011', 'skill_017', 'skill_002', 'skill_014'],
    'webpage':        ['skill_011', 'skill_017', 'skill_002'],
    'frontend':       ['skill_011', 'skill_017', 'skill_019', 'skill_033'],
    'front end':      ['skill_011', 'skill_017', 'skill_019'],
    'ui':             ['skill_033', 'skill_035', 'skill_017'],
    'ux':             ['skill_033', 'skill_035'],
    'interface':      ['skill_033', 'skill_017', 'skill_011'],
    'responsive':     ['skill_017', 'skill_019', 'skill_011'],
    'dynamic':        ['skill_002', 'skill_011', 'skill_014'],
    'landing page':   ['skill_017', 'skill_011', 'skill_019'],
    'portfolio':      ['skill_017', 'skill_011', 'skill_033'],

    # Backend / auth / payments
    'backend':        ['skill_001', 'skill_016', 'skill_014', 'skill_025'],
    'back end':       ['skill_001', 'skill_016', 'skill_025'],
    'server':         ['skill_001', 'skill_016', 'skill_014'],
    'api':            ['skill_001', 'skill_016', 'skill_014', 'skill_002'],
    'rest':           ['skill_001', 'skill_016', 'skill_014'],
    'login':          ['skill_001', 'skill_016', 'skill_002', 'skill_011'],
    'authentication': ['skill_001', 'skill_016', 'skill_102'],
    'signup':         ['skill_001', 'skill_016', 'skill_011'],
    'register':       ['skill_001', 'skill_016', 'skill_011'],
    'user account':   ['skill_001', 'skill_016', 'skill_011'],
    'payment':        ['skill_002', 'skill_011', 'skill_016', 'skill_001'],
    'ecommerce':      ['skill_011', 'skill_002', 'skill_025', 'skill_016'],
    'e-commerce':     ['skill_011', 'skill_002', 'skill_025'],
    'checkout':       ['skill_011', 'skill_016', 'skill_002'],
    'database':       ['skill_025', 'skill_001', 'skill_015'],
    'sql':            ['skill_025'],
    'crud':           ['skill_001', 'skill_025', 'skill_016'],

    # Mobile
    'app':            ['skill_094', 'skill_095', 'skill_096', 'skill_097'],
    'mobile':         ['skill_094', 'skill_095', 'skill_096', 'skill_097'],
    'android':        ['skill_095', 'skill_097'],
    'ios':            ['skill_094', 'skill_096'],
    'flutter':        ['skill_097'],
    'react native':   ['skill_096'],

    # Data / ML / AI
    'data':           ['skill_023', 'skill_025', 'skill_026', 'skill_001'],
    'analytics':      ['skill_023', 'skill_030', 'skill_026', 'skill_028'],
    'analysis':       ['skill_023', 'skill_027', 'skill_026'],
    'dashboard':      ['skill_026', 'skill_028', 'skill_029', 'skill_023'],
    'visualization':  ['skill_026', 'skill_028', 'skill_029'],
    'predict':        ['skill_021', 'skill_031', 'skill_024'],
    'machine learning': ['skill_021', 'skill_001'],
    'deep learning':  ['skill_022', 'skill_021', 'skill_001'],
    'ai':             ['skill_021', 'skill_022', 'skill_001'],
    'nlp':            ['skill_021', 'skill_022', 'skill_001'],
    'model':          ['skill_021', 'skill_022', 'skill_024'],
    'statistics':     ['skill_024', 'skill_023'],
    'excel':          ['skill_027'],
    'spreadsheet':    ['skill_027'],
    'report':         ['skill_027', 'skill_026', 'skill_029'],

    # Design
    'design':         ['skill_033', 'skill_034', 'skill_035'],
    'figma':          ['skill_035'],
    'logo':           ['skill_034', 'skill_043', 'skill_038'],
    'graphic':        ['skill_034', 'skill_038', 'skill_037'],
    'branding':       ['skill_043', 'skill_062', 'skill_034'],
    'illustration':   ['skill_038', 'skill_034'],
    'animation':      ['skill_040', 'skill_039'],
    'video':          ['skill_041', 'skill_040'],
    'photo':          ['skill_042', 'skill_037'],

    # Marketing
    'marketing':      ['skill_054', 'skill_055', 'skill_056', 'skill_057'],
    'seo':            ['skill_055', 'skill_054'],
    'social media':   ['skill_056', 'skill_054', 'skill_063'],
    'content':        ['skill_044', 'skill_045', 'skill_057'],
    'blog':           ['skill_047', 'skill_044', 'skill_055'],
    'email':          ['skill_051', 'skill_044'],
    'campaign':       ['skill_054', 'skill_056', 'skill_051'],
    'ads':            ['skill_054', 'skill_056'],
    'brand':          ['skill_062', 'skill_043', 'skill_054'],

    # Writing
    'writing':        ['skill_044', 'skill_045', 'skill_046'],
    'copywriting':    ['skill_045'],
    'technical writing': ['skill_046'],
    'script':         ['skill_049', 'skill_044'],
    'proofread':      ['skill_050'],
    'edit':           ['skill_050', 'skill_044'],

    # DevOps / Cloud
    'cloud':          ['skill_098', 'skill_099', 'skill_100'],
    'aws':            ['skill_098'],
    'docker':         ['skill_099'],
    'kubernetes':     ['skill_100'],
    'devops':         ['skill_098', 'skill_099', 'skill_100', 'skill_101'],
    'deploy':         ['skill_098', 'skill_099', 'skill_101'],
    'infrastructure': ['skill_098', 'skill_100', 'skill_101'],
    'ci cd':          ['skill_101'],
    'pipeline':       ['skill_101', 'skill_099'],

    # Business
    'business':       ['skill_065', 'skill_070', 'skill_064'],
    'project':        ['skill_064', 'skill_065'],
    'finance':        ['skill_066', 'skill_067', 'skill_074'],
    'accounting':     ['skill_067', 'skill_068'],
    'strategy':       ['skill_070', 'skill_062', 'skill_065'],
    'presentation':   ['skill_060', 'skill_059', 'skill_076'],

    # Teaching
    'teach':          ['skill_075', 'skill_078', 'skill_079'],
    'tutor':          ['skill_075', 'skill_078'],
    'course':         ['skill_076', 'skill_080', 'skill_075'],
    'training':       ['skill_077', 'skill_075'],
    'mentor':         ['skill_079', 'skill_078'],

    # Programming languages
    'python':         ['skill_001'],
    'javascript':     ['skill_002'],
    'java':           ['skill_003'],
    'typescript':     ['skill_010'],
    'react':          ['skill_011'],
    'node':           ['skill_014'],
    'django':         ['skill_015'],
    'flask':          ['skill_016'],
}


class NLPTaskMatcher:
    def __init__(self):
        """Initialize NLP matcher with user and skill data"""
        self.users_df = pd.read_csv(config.USERS_FILE)
        self.skills_df = pd.read_csv(config.SKILLS_FILE)

        # Parse skill lists
        self.users_df['skills_offered'] = self.users_df['skills_offered'].apply(
            lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
        )
        self.users_df['skills_required'] = self.users_df['skills_required'].apply(
            lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
        )

        # Lookup maps
        self.skill_name_to_id = dict(zip(
            self.skills_df['skill_name'].str.lower(),
            self.skills_df['skill_id']
        ))
        self.skill_id_to_name = dict(zip(
            self.skills_df['skill_id'],
            self.skills_df['skill_name']
        ))

        # Build a combined corpus = skill names + user descriptions
        # This gives the vectorizer vocabulary that covers both domain terms
        # and natural language descriptors.
        skill_docs = self.skills_df['skill_name'].tolist()
        user_docs = self.users_df['description'].tolist()
        corpus = skill_docs + user_docs

        self.vectorizer = TfidfVectorizer(
            max_features=500,       # larger vocab → better coverage of domain terms
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,      # dampens very frequent terms
        )
        self.vectorizer.fit(corpus)

        # Pre-compute user description vectors (avoid recomputing on every search)
        self._user_vectors = self.vectorizer.transform(
            self.users_df['description'].tolist()
        )

    # ── Skill extraction ────────────────────────────────────────────────────────
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract relevant skill IDs from a free-text task description.
        Two passes:
          1. Exact skill name matching (e.g. "React", "SQL")
          2. Keyword expansion (e.g. "website" → React, HTML/CSS, JS)
        Returns deduplicated list of skill_ids.
        """
        text_lower = text.lower()
        found = set()

        # Pass 1: Exact skill name match (word-boundary)
        for skill_name, skill_id in self.skill_name_to_id.items():
            pattern = r'\b' + re.escape(skill_name) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill_id)

        # Pass 2: Keyword expansion — catches "website", "login", "payment", etc.
        for keyword, skill_ids in TASK_KEYWORDS.items():
            if keyword in text_lower:
                found.update(skill_ids)

        return list(found)

    # ── Text similarity ─────────────────────────────────────────────────────────
    def calculate_text_similarity_batch(self, task_description: str) -> np.ndarray:
        """
        Compute cosine similarity between the task and ALL user descriptions at once.
        Returns 1-D numpy array of shape (n_users,).
        """
        try:
            task_vec = self.vectorizer.transform([task_description])
            sims = cosine_similarity(task_vec, self._user_vectors)[0]
            return sims
        except Exception:
            return np.zeros(len(self.users_df))

    # ── Main matching ───────────────────────────────────────────────────────────
    def find_matches_for_task(self, task_description: str, top_n: int = 10) -> List[Dict]:
        """
        Find best user matches for a given task description.

        Strategy:
          - Extract skills from task (exact names + keyword expansion).
          - Score every user: weighted skill-match (60%) + TF-IDF text similarity (40%).
          - If skill extraction produced nothing, rely purely on text similarity.
          - ALWAYS return top_n results — guaranteed non-empty as long as there are users.
        """
        required_skills = set(self.extract_skills_from_text(task_description))
        has_skill_signal = len(required_skills) > 0

        # Batch compute text similarities (fast)
        text_sims = self.calculate_text_similarity_batch(task_description)

        matches = []
        for i, (_, user) in enumerate(self.users_df.iterrows()):
            user_offered = set(user['skills_offered'])

            # Skill match score
            if has_skill_signal:
                matched_skills = required_skills.intersection(user_offered)
                skill_match_score = len(matched_skills) / len(required_skills)
            else:
                # No skill signal → treat all users as 0 skill match;
                # ranking will be driven purely by text similarity.
                matched_skills = set()
                skill_match_score = 0.0

            text_sim = float(text_sims[i])

            if has_skill_signal:
                combined_score = (
                    config.SKILL_MATCH_WEIGHT * skill_match_score +
                    config.TEXT_SIMILARITY_WEIGHT * text_sim
                )
            else:
                # Pure text-similarity mode
                combined_score = text_sim

            matches.append({
                'user_id': user['user_id'],
                'name': user['name'],
                'description': user['description'],
                'skills_offered': list(user_offered),
                'matched_skills': list(matched_skills),
                'skill_match_score': round(skill_match_score, 2),
                'text_similarity': round(text_sim, 2),
                'combined_score': round(combined_score, 3),
            })

        # Sort by score descending; guarantee top_n results regardless of threshold
        matches.sort(key=lambda x: x['combined_score'], reverse=True)
        return matches[:top_n]

    def get_skill_name(self, skill_id: str) -> str:
        return self.skill_id_to_name.get(skill_id, skill_id)

    def get_skill_names(self, skill_ids: List[str]) -> List[str]:
        return [self.get_skill_name(sid) for sid in skill_ids]


if __name__ == '__main__':
    matcher = NLPTaskMatcher()

    test_tasks = [
        "I want to make a dynamic website with proper login and payment",
        "Looking for someone to help me analyze data using Python and create visualizations",
        "Need assistance setting up AWS infrastructure with Docker containers",
        "I need a logo and brand identity for my startup",
        "Help me write SEO content for my blog",
    ]

    for task in test_tasks:
        print(f"\nTask: {task}")
        print("=" * 65)
        matches = matcher.find_matches_for_task(task, top_n=3)
        for i, m in enumerate(matches, 1):
            skills = matcher.get_skill_names(m['matched_skills'])
            print(f"  {i}. {m['name']}  score={m['combined_score']}  "
                  f"skill_match={m['skill_match_score']}  text_sim={m['text_similarity']}")
            print(f"     Matched: {skills}")
