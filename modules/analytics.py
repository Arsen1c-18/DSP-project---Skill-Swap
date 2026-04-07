"""
Analytics Module for Skill Swap Platform
Computes skill supply/demand statistics and insights
"""
import pandas as pd
from typing import Dict, List, Tuple
from collections import Counter
import config


class SkillAnalytics:
    def __init__(self):
        """Initialize analytics with data"""
        self.users_df = pd.read_csv(config.USERS_FILE)
        self.skills_df = pd.read_csv(config.SKILLS_FILE)
        
        # Parse skill lists
        self.users_df['skills_offered'] = self.users_df['skills_offered'].apply(lambda x: x.split(','))
        self.users_df['skills_required'] = self.users_df['skills_required'].apply(lambda x: x.split(','))
        
        # Create skill mappings
        self.skill_id_to_name = dict(zip(self.skills_df['skill_id'], self.skills_df['skill_name']))
        self.skill_id_to_category = dict(zip(self.skills_df['skill_id'], self.skills_df['category']))
    
    def get_most_offered_skills(self, top_n: int = 15) -> List[Dict]:
        """
        Get most offered skills (supply)
        Returns list of {skill_name, count, category}
        """
        all_offered = []
        for skills in self.users_df['skills_offered']:
            all_offered.extend(skills)
        
        skill_counts = Counter(all_offered)
        
        results = []
        for skill_id, count in skill_counts.most_common(top_n):
            results.append({
                'skill_id': skill_id,
                'skill_name': self.skill_id_to_name.get(skill_id, skill_id),
                'category': self.skill_id_to_category.get(skill_id, 'Other'),
                'count': count
            })
        
        return results
    
    def get_most_required_skills(self, top_n: int = 15) -> List[Dict]:
        """
        Get most requested skills (demand)
        Returns list of {skill_name, count, category}
        """
        all_required = []
        for skills in self.users_df['skills_required']:
            all_required.extend(skills)
        
        skill_counts = Counter(all_required)
        
        results = []
        for skill_id, count in skill_counts.most_common(top_n):
            results.append({
                'skill_id': skill_id,
                'skill_name': self.skill_id_to_name.get(skill_id, skill_id),
                'category': self.skill_id_to_category.get(skill_id, 'Other'),
                'count': count
            })
        
        return results
    
    def get_supply_demand_comparison(self, top_n: int = 15) -> List[Dict]:
        """
        Compare supply vs demand for skills
        Returns list with both supply and demand counts
        """
        # Get all skills that appear in either offered or required
        all_offered = []
        all_required = []
        
        for skills in self.users_df['skills_offered']:
            all_offered.extend(skills)
        
        for skills in self.users_df['skills_required']:
            all_required.extend(skills)
        
        offered_counts = Counter(all_offered)
        required_counts = Counter(all_required)
        
        # Get unique skills
        all_skills = set(all_offered + all_required)
        
        comparison = []
        for skill_id in all_skills:
            supply = offered_counts.get(skill_id, 0)
            demand = required_counts.get(skill_id, 0)
            
            comparison.append({
                'skill_id': skill_id,
                'skill_name': self.skill_id_to_name.get(skill_id, skill_id),
                'category': self.skill_id_to_category.get(skill_id, 'Other'),
                'supply': supply,
                'demand': demand,
                'total': supply + demand
            })
        
        # Sort by total (most active skills)
        comparison.sort(key=lambda x: x['total'], reverse=True)
        
        return comparison[:top_n]
    
    def get_skill_gaps(self, top_n: int = 10) -> List[Dict]:
        """
        Calculate skill gap scores (Demand - Supply)
        Positive gap means high demand, low supply
        Returns skills you may consider learning
        """
        comparison = self.get_supply_demand_comparison(top_n=50)
        
        gaps = []
        for item in comparison:
            gap_score = item['demand'] - item['supply']
            
            if gap_score > 0:  # Only show skills in demand
                gaps.append({
                    'skill_id': item['skill_id'],
                    'skill_name': item['skill_name'],
                    'category': item['category'],
                    'demand': item['demand'],
                    'supply': item['supply'],
                    'gap_score': gap_score
                })
        
        # Sort by gap score
        gaps.sort(key=lambda x: x['gap_score'], reverse=True)
        
        return gaps[:top_n]
    
    def get_category_distribution(self) -> Dict:
        """
        Get distribution of skills by category
        Returns category counts for offered and required
        """
        offered_categories = []
        required_categories = []
        
        for skills in self.users_df['skills_offered']:
            for skill_id in skills:
                category = self.skill_id_to_category.get(skill_id, 'Other')
                offered_categories.append(category)
        
        for skills in self.users_df['skills_required']:
            for skill_id in skills:
                category = self.skill_id_to_category.get(skill_id, 'Other')
                required_categories.append(category)
        
        return {
            'offered': dict(Counter(offered_categories)),
            'required': dict(Counter(required_categories))
        }
    
    def get_summary_stats(self) -> Dict:
        """Get overall platform statistics"""
        total_users = len(self.users_df)
        total_skills = len(self.skills_df)
        
        avg_offered = self.users_df['skills_offered'].apply(len).mean()
        avg_required = self.users_df['skills_required'].apply(len).mean()
        
        return {
            'total_users': total_users,
            'total_skills': total_skills,
            'avg_skills_offered': round(avg_offered, 1),
            'avg_skills_required': round(avg_required, 1)
        }


if __name__ == "__main__":
    # Test analytics
    analytics = SkillAnalytics()
    
    print("=== Platform Statistics ===")
    stats = analytics.get_summary_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Top 10 Most Offered Skills ===")
    for i, skill in enumerate(analytics.get_most_offered_skills(10), 1):
        print(f"{i}. {skill['skill_name']} ({skill['category']}): {skill['count']}")
    
    print("\n=== Top 10 Most Requested Skills ===")
    for i, skill in enumerate(analytics.get_most_required_skills(10), 1):
        print(f"{i}. {skill['skill_name']} ({skill['category']}): {skill['count']}")
    
    print("\n=== Top 10 Skill Gaps ===")
    for i, gap in enumerate(analytics.get_skill_gaps(10), 1):
        print(f"{i}. {gap['skill_name']}: Gap={gap['gap_score']} (Demand={gap['demand']}, Supply={gap['supply']})")
