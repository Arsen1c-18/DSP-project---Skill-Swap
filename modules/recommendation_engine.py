"""
Recommendation Engine for Skill Swap Platform
Implements mutual skill matching algorithm
"""
import pandas as pd
from typing import List, Dict, Tuple
import config


class RecommendationEngine:
    def __init__(self):
        """Initialize recommendation engine with user data"""
        self.users_df = pd.read_csv(config.USERS_FILE)
        self.skills_df = pd.read_csv(config.SKILLS_FILE)
        
        # Parse skill lists
        self.users_df['skills_offered'] = self.users_df['skills_offered'].apply(lambda x: x.split(','))
        self.users_df['skills_required'] = self.users_df['skills_required'].apply(lambda x: x.split(','))
    
    def get_user_by_id(self, user_id: str) -> Dict:
        """Get user profile by ID"""
        user_row = self.users_df[self.users_df['user_id'] == user_id]
        if user_row.empty:
            return None
        
        user = user_row.iloc[0].to_dict()
        return user
    
    def update_user(self, user_id: str, name: str, description: str) -> bool:
        """Update user details and save to CSV"""
        idx = self.users_df.index[self.users_df['user_id'] == user_id]
        if not idx.empty:
            self.users_df.loc[idx, 'name'] = name
            self.users_df.loc[idx, 'description'] = description
            # Convert back lists to comma separated strings before saving
            df_to_save = self.users_df.copy()
            df_to_save['skills_offered'] = df_to_save['skills_offered'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
            df_to_save['skills_required'] = df_to_save['skills_required'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)
            df_to_save.to_csv(config.USERS_FILE, index=False)
            return True
        return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all user profiles"""
        return self.users_df.to_dict('records')
    
    def find_mutual_matches(self, user_id: str, top_n: int = None) -> List[Dict]:
        """
        Find mutual skill matches for a user
        Returns users where there's a bidirectional skill exchange opportunity
        """
        if top_n is None:
            top_n = config.TOP_RECOMMENDATIONS
        
        current_user = self.get_user_by_id(user_id)
        if not current_user:
            return []
        
        current_offered = set(current_user['skills_offered'])
        current_required = set(current_user['skills_required'])
        
        matches = []
        
        for _, other_user in self.users_df.iterrows():
            if other_user['user_id'] == user_id:
                continue
            
            other_offered = set(other_user['skills_offered'])
            other_required = set(other_user['skills_required'])
            
            # Check mutual exchange potential
            # What current user needs and other offers
            skills_other_can_teach = current_required.intersection(other_offered)
            
            # What current user offers and other needs
            skills_current_can_teach = current_offered.intersection(other_required)
            
            # Calculate match score
            if skills_other_can_teach or skills_current_can_teach:
                # Bidirectional match is stronger
                bidirectional_score = len(skills_other_can_teach.intersection(skills_current_can_teach))
                
                # Total skills matched
                total_matched = len(skills_other_can_teach) + len(skills_current_can_teach)
                
                # Perfect match: both can teach each other
                is_perfect_match = len(skills_other_can_teach) > 0 and len(skills_current_can_teach) > 0
                
                # Calculate final score (0-1 scale)
                score = (total_matched * 0.4) + (bidirectional_score * 0.6) + (1.0 if is_perfect_match else 0)
                
                if score >= config.MIN_MATCH_SCORE:
                    matches.append({
                        'user_id': other_user['user_id'],
                        'name': other_user['name'],
                        'description': other_user['description'],
                        'skills_offered': other_user['skills_offered'],
                        'skills_required': other_user['skills_required'],
                        'match_score': round(score, 2),
                        'can_teach_you': list(skills_other_can_teach),
                        'you_can_teach': list(skills_current_can_teach),
                        'is_perfect_match': is_perfect_match
                    })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
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
    
    def get_random_users(self, n: int = 10) -> List[Dict]:
        """Get random sample of users for demo purposes"""
        sample = self.users_df.sample(n=min(n, len(self.users_df)))
        return sample.to_dict('records')


if __name__ == "__main__":
    # Test the recommendation engine
    engine = RecommendationEngine()
    
    # Test with first user
    test_user_id = 'user_001'
    matches = engine.find_mutual_matches(test_user_id, top_n=5)
    
    print(f"Top 5 matches for {test_user_id}:")
    for i, match in enumerate(matches, 1):
        print(f"\n{i}. {match['name']} (Score: {match['match_score']})")
        print(f"   Can teach you: {engine.get_skill_names(match['can_teach_you'])}")
        print(f"   You can teach: {engine.get_skill_names(match['you_can_teach'])}")
        print(f"   Perfect match: {match['is_perfect_match']}")
