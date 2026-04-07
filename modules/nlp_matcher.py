"""
NLP-based Task Matcher for Skill Swap Platform
Uses TF-IDF and cosine similarity to match task descriptions with user profiles
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import re
import config


class NLPTaskMatcher:
    def __init__(self):
        """Initialize NLP matcher with user and skill data"""
        self.users_df = pd.read_csv(config.USERS_FILE)
        self.skills_df = pd.read_csv(config.SKILLS_FILE)
        
        # Parse skill lists
        self.users_df['skills_offered'] = self.users_df['skills_offered'].apply(lambda x: x.split(','))
        self.users_df['skills_required'] = self.users_df['skills_required'].apply(lambda x: x.split(','))
        
        # Create skill name to ID mapping
        self.skill_name_to_id = dict(zip(
            self.skills_df['skill_name'].str.lower(),
            self.skills_df['skill_id']
        ))
        
        # Prepare TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2)
        )
        
        # Fit on all user descriptions
        self.vectorizer.fit(self.users_df['description'].tolist())
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skill keywords from text
        Returns list of skill IDs found in the text
        """
        text_lower = text.lower()
        found_skills = []
        
        # Check for each skill in the text
        for skill_name, skill_id in self.skill_name_to_id.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill_name) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill_id)
        
        return found_skills
    
    def calculate_text_similarity(self, task_description: str, user_description: str) -> float:
        """
        Calculate cosine similarity between task and user descriptions
        Returns similarity score (0-1)
        """
        try:
            vectors = self.vectorizer.transform([task_description, user_description])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def find_matches_for_task(self, task_description: str, top_n: int = 10) -> List[Dict]:
        """
        Find best user matches for a given task description
        Combines skill matching and text similarity
        """
        # Extract skills from task description
        required_skills = self.extract_skills_from_text(task_description)
        
        matches = []
        
        for _, user in self.users_df.iterrows():
            user_offered = set(user['skills_offered'])
            
            # Calculate skill match score
            matched_skills = set(required_skills).intersection(user_offered)
            skill_match_score = len(matched_skills) / max(len(required_skills), 1) if required_skills else 0
            
            # Calculate text similarity
            text_similarity = self.calculate_text_similarity(task_description, user['description'])
            
            # Combined score (weighted)
            combined_score = (
                config.SKILL_MATCH_WEIGHT * skill_match_score +
                config.TEXT_SIMILARITY_WEIGHT * text_similarity
            )
            
            # Only include users with some relevance
            if combined_score > 0.1 or len(matched_skills) > 0:
                matches.append({
                    'user_id': user['user_id'],
                    'name': user['name'],
                    'description': user['description'],
                    'skills_offered': user['skills_offered'],
                    'matched_skills': list(matched_skills),
                    'skill_match_score': round(skill_match_score, 2),
                    'text_similarity': round(text_similarity, 2),
                    'combined_score': round(combined_score, 2)
                })
        
        # Sort by combined score
        matches.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return matches[:top_n]
    
    def get_skill_name(self, skill_id: str) -> str:
        """Convert skill ID to readable name"""
        skill = self.skills_df[self.skills_df['skill_id'] == skill_id]
        if skill.empty:
            return skill_id
        return skill.iloc[0]['skill_name']
    
    def get_skill_names(self, skill_ids: List[str]) -> List[str]:
        """Convert list of skill IDs to readable names"""
        return [self.get_skill_name(sid) for sid in skill_ids]


if __name__ == "__main__":
    # Test the NLP matcher
    matcher = NLPTaskMatcher()
    
    # Test task descriptions
    test_tasks = [
        "I need help building a React website with authentication and a modern UI",
        "Looking for someone to help me analyze data using Python and create visualizations",
        "Need assistance setting up AWS infrastructure with Docker containers"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        print("=" * 60)
        
        matches = matcher.find_matches_for_task(task, top_n=3)
        
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match['name']} (Score: {match['combined_score']})")
            print(f"   Skills: {matcher.get_skill_names(match['matched_skills'])}")
            print(f"   Skill Match: {match['skill_match_score']}, Text Sim: {match['text_similarity']}")
