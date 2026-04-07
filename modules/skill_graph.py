"""
Skill Relationship Graph for Skill Swap Platform
Processes skill relationships for enhanced recommendations
"""
import pandas as pd
from typing import List, Dict, Set
import config


class SkillGraph:
    def __init__(self):
        """Initialize skill graph with relationship data"""
        self.skills_df = pd.read_csv(config.SKILLS_FILE)
        self.relationships_df = pd.read_csv(config.SKILL_RELATIONSHIPS_FILE)
        
        # Create skill mappings
        self.skill_id_to_name = dict(zip(self.skills_df['skill_id'], self.skills_df['skill_name']))
        self.skill_name_to_id = dict(zip(self.skills_df['skill_name'], self.skills_df['skill_id']))
        
        # Build adjacency graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Dict[str, List[Dict]]:
        """
        Build bidirectional graph from relationships
        Returns: {skill_id: [{related_skill, weight}, ...]}
        """
        graph = {skill_id: [] for skill_id in self.skills_df['skill_id']}
        
        for _, row in self.relationships_df.iterrows():
            skill_from = row['skill_from']
            skill_to = row['skill_to']
            weight = row['similarity_weight']
            
            # Add bidirectional edges
            graph[skill_from].append({'skill_id': skill_to, 'weight': weight})
            graph[skill_to].append({'skill_id': skill_from, 'weight': weight})
        
        return graph
    
    def get_related_skills(self, skill_id: str, max_distance: int = 2, min_weight: float = 0.5) -> List[Dict]:
        """
        Get skills related to a given skill
        Uses graph traversal up to max_distance hops
        Returns list of {skill_id, skill_name, weight, distance}
        """
        if skill_id not in self.graph:
            return []
        
        related = {}
        visited = set()
        queue = [(skill_id, 0, 1.0)]  # (current_skill, distance, cumulative_weight)
        
        while queue:
            current, distance, cum_weight = queue.pop(0)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Don't include the original skill
            if current != skill_id and cum_weight >= min_weight:
                if current not in related or cum_weight > related[current]['weight']:
                    related[current] = {
                        'skill_id': current,
                        'skill_name': self.skill_id_to_name.get(current, current),
                        'weight': round(cum_weight, 2),
                        'distance': distance
                    }
            
            # Explore neighbors if within distance limit
            if distance < max_distance:
                for neighbor in self.graph.get(current, []):
                    neighbor_id = neighbor['skill_id']
                    neighbor_weight = neighbor['weight']
                    new_weight = cum_weight * neighbor_weight
                    
                    if neighbor_id not in visited and new_weight >= min_weight:
                        queue.append((neighbor_id, distance + 1, new_weight))
        
        # Convert to list and sort by weight
        related_list = list(related.values())
        related_list.sort(key=lambda x: x['weight'], reverse=True)
        
        return related_list
    
    def expand_skill_list(self, skill_ids: List[str], max_related: int = 3) -> List[str]:
        """
        Expand a list of skills to include related skills
        Useful for finding matches with similar (not just exact) skills
        """
        expanded = set(skill_ids)
        
        for skill_id in skill_ids:
            related = self.get_related_skills(skill_id, max_distance=1, min_weight=0.7)
            
            # Add top related skills
            for rel in related[:max_related]:
                expanded.add(rel['skill_id'])
        
        return list(expanded)
    
    def find_skill_path(self, skill_from: str, skill_to: str, max_depth: int = 3) -> List[str]:
        """
        Find path between two skills (BFS)
        Returns list of skill IDs representing the path, or empty if no path
        """
        if skill_from == skill_to:
            return [skill_from]
        
        if skill_from not in self.graph or skill_to not in self.graph:
            return []
        
        queue = [(skill_from, [skill_from])]
        visited = set([skill_from])
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            for neighbor in self.graph.get(current, []):
                neighbor_id = neighbor['skill_id']
                
                if neighbor_id == skill_to:
                    return path + [neighbor_id]
                
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []
    
    def get_skill_name(self, skill_id: str) -> str:
        """Convert skill ID to readable name"""
        return self.skill_id_to_name.get(skill_id, skill_id)
    
    def get_skill_names(self, skill_ids: List[str]) -> List[str]:
        """Convert list of skill IDs to readable names"""
        return [self.get_skill_name(sid) for sid in skill_ids]


if __name__ == "__main__":
    # Test skill graph
    graph = SkillGraph()
    
    # Test related skills
    test_skill = 'skill_001'  # Python
    print(f"Skills related to {graph.get_skill_name(test_skill)}:")
    related = graph.get_related_skills(test_skill, max_distance=2)
    for rel in related[:10]:
        print(f"  - {rel['skill_name']} (weight: {rel['weight']}, distance: {rel['distance']})")
    
    # Test skill path
    print(f"\nPath from Python to React:")
    path = graph.find_skill_path('skill_001', 'skill_013')
    if path:
        print(" -> ".join([graph.get_skill_name(s) for s in path]))
    else:
        print("No path found")
