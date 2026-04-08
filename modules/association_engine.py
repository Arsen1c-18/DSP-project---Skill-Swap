"""
Association Rule Mining Engine for Skill Swap Platform
Uses Apriori algorithm to find frequent skill co-occurrence patterns.
No changes to dataset needed – reads existing users.csv.
"""
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
import config


class AssociationEngine:
    def __init__(self):
        self.users_df = pd.read_csv(config.USERS_FILE)
        self.skills_df = pd.read_csv(config.SKILLS_FILE)
        self.skill_id_to_name = dict(zip(self.skills_df['skill_id'], self.skills_df['skill_name']))

        # Parse skill lists
        self.users_df['skills_offered'] = self.users_df['skills_offered'].apply(
            lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
        )
        self.users_df['skills_required'] = self.users_df['skills_required'].apply(
            lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
        )

        # Pre-compute rules on first load
        self._offer_rules = None
        self._require_rules = None
        self._cooccurrence = None

    # ── Internal helpers ────────────────────────────────────────────
    def _compute_rules(self, transactions, min_support=0.01, min_confidence=0.15):
        """
        Simple Apriori using manual pair-counting (no extra deps).
        transactions: list of lists (each list = one user's skills)
        Returns list of {antecedent, consequent, support, confidence, lift}
        """
        n = len(transactions)
        # 1-item frequencies
        item_counts = Counter()
        for t in transactions:
            item_counts.update(set(t))

        # For small datasets, use at least 2 occurrences as threshold
        min_cnt = max(2, int(min_support * n))
        frequent_items = {item for item, cnt in item_counts.items() if cnt >= min_cnt}

        # 2-item pair frequencies
        pair_counts = Counter()
        for t in transactions:
            filtered = [s for s in set(t) if s in frequent_items]
            for pair in combinations(sorted(filtered), 2):
                pair_counts[pair] += 1

        # Generate rules
        rules = []
        for (a, b), cnt in pair_counts.items():
            pair_support = cnt / n
            if pair_support < min_support:
                continue
            # A → B
            conf_ab = cnt / item_counts[a]
            if conf_ab >= min_confidence:
                lift = conf_ab / (item_counts[b] / n)
                rules.append({
                    'antecedent': a,
                    'consequent': b,
                    'antecedent_name': self.skill_id_to_name.get(a, a),
                    'consequent_name': self.skill_id_to_name.get(b, b),
                    'support': round(pair_support, 4),
                    'confidence': round(conf_ab, 4),
                    'lift': round(lift, 4),
                })
            # B → A
            conf_ba = cnt / item_counts[b]
            if conf_ba >= min_confidence:
                lift = conf_ba / (item_counts[a] / n)
                rules.append({
                    'antecedent': b,
                    'consequent': a,
                    'antecedent_name': self.skill_id_to_name.get(b, b),
                    'consequent_name': self.skill_id_to_name.get(a, a),
                    'support': round(pair_support, 4),
                    'confidence': round(conf_ba, 4),
                    'lift': round(lift, 4),
                })

        rules.sort(key=lambda r: r['lift'], reverse=True)
        return rules

    def _ensure_rules(self):
        if self._offer_rules is None:
            offer_txns = self.users_df['skills_offered'].tolist()
            require_txns = self.users_df['skills_required'].tolist()
            self._offer_rules = self._compute_rules(offer_txns)
            self._require_rules = self._compute_rules(require_txns)

    def _ensure_cooccurrence(self):
        """Build co-occurrence matrix from skills_offered across all users."""
        if self._cooccurrence is not None:
            return
        pair_counts = Counter()
        item_counts = Counter()
        n = len(self.users_df)
        for skills in self.users_df['skills_offered']:
            skill_set = list(set(skills))
            item_counts.update(skill_set)
            for pair in combinations(sorted(skill_set), 2):
                pair_counts[pair] += 1
        self._cooccurrence = {'pairs': pair_counts, 'items': item_counts, 'n': n}

    # ── Public API ──────────────────────────────────────────────────
    def get_top_offer_rules(self, top_n=15):
        """Top association rules from Skills Offered (what people want to give)."""
        self._ensure_rules()
        return self._offer_rules[:top_n]

    def get_top_require_rules(self, top_n=15):
        """Top association rules from Skills Required (what people want to receive)."""
        self._ensure_rules()
        return self._require_rules[:top_n]

    def get_suggestions_for_skill(self, skill_id: str, context='offer', top_n=5):
        """
        Given a skill, return other skills frequently paired with it.
        context: 'offer' or 'require'
        Returns list of {skill_id, skill_name, confidence, lift}
        """
        self._ensure_rules()
        rules = self._offer_rules if context == 'offer' else self._require_rules
        matching = [r for r in rules if r['antecedent'] == skill_id]
        matching.sort(key=lambda r: r['lift'], reverse=True)
        return [
            {
                'skill_id': r['consequent'],
                'skill_name': r['consequent_name'],
                'confidence': r['confidence'],
                'lift': r['lift'],
            }
            for r in matching[:top_n]
        ]

    def get_network_graph_data(self, top_edges=80):
        """
        Returns nodes and edges for a skill co-occurrence network graph.
        Edges represent skills frequently offered together.
        """
        self._ensure_cooccurrence()
        pairs = self._cooccurrence['pairs']
        items = self._cooccurrence['items']
        n = self._cooccurrence['n']

        # Use at least 2 co-occurrences
        min_count = 2

        # Filter and sort edges
        edges_raw = [(a, b, cnt) for (a, b), cnt in pairs.items() if cnt >= min_count]
        edges_raw.sort(key=lambda x: x[2], reverse=True)
        edges_raw = edges_raw[:top_edges]

        # Collect involved skills
        involved_skills = set()
        for a, b, _ in edges_raw:
            involved_skills.add(a)
            involved_skills.add(b)

        # Build node list
        nodes = []
        for sid in involved_skills:
            nodes.append({
                'id': sid,
                'label': self.skill_id_to_name.get(sid, sid),
                'frequency': items.get(sid, 0),
            })

        # Build edge list
        max_cnt = max(cnt for _, _, cnt in edges_raw) if edges_raw else 1
        edges = []
        for a, b, cnt in edges_raw:
            edges.append({
                'from': a,
                'to': b,
                'weight': cnt,
                'normalized': round(cnt / max_cnt, 3),
            })

        return {'nodes': nodes, 'edges': edges}


if __name__ == '__main__':
    engine = AssociationEngine()
    print('Top Offer Rules:')
    for r in engine.get_top_offer_rules(10):
        print(f"  {r['antecedent_name']} → {r['consequent_name']}  "
              f"conf={r['confidence']:.2f}  lift={r['lift']:.2f}")
    print('\nNetwork graph nodes:', len(engine.get_network_graph_data()['nodes']))
    print('Network graph edges:', len(engine.get_network_graph_data()['edges']))
