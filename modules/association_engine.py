"""
Association Rule Mining Engine for Skill Swap Platform
Full Apriori algorithm supporting k-itemsets (k = 2, 3, ...).
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

        # Lazy-computed rule sets
        self._offer_rules = None
        self._require_rules = None
        self._cooccurrence = None

    # ── Apriori k-itemset implementation ────────────────────────────────────────
    def _compute_rules(self, transactions, min_support=0.03, min_confidence=0.3, max_k=3):
        """
        Full Apriori algorithm supporting itemsets up to size max_k.

        Steps:
          1. Find frequent 1-itemsets (L1) by counting item frequencies.
          2. For k = 2 .. max_k:
               a. Generate candidate k-itemsets from L(k-1) pairs.
               b. Prune: discard candidates where any (k-1)-subset is infrequent
                  (anti-monotone / Apriori property).
               c. Count support of remaining candidates by scanning transactions.
               d. Keep candidates meeting min_support → Lk.
          3. For every frequent itemset of size >= 2, generate rules of the form
             {antecedent} → consequent (single-item consequent).
             Compute confidence, lift; keep rules meeting min_confidence.
          4. Sort by lift descending.

        Parameters:
            transactions  : list of lists — each inner list is one user's skills
            min_support   : minimum fraction of transactions an itemset must appear in
            min_confidence: minimum P(consequent | antecedent) for a rule to be kept
            max_k         : largest itemset size to mine (2 = pairs only, 3 = triplets, etc.)

        Returns:
            list of rule dicts with keys:
              antecedent      (list of skill_ids)
              consequent      (skill_id string)
              antecedent_name (human-readable, joined with ' + ')
              consequent_name (human-readable)
              support         (float)
              confidence      (float)
              lift            (float)
              k               (int — size of the source itemset)
        """
        n = len(transactions)
        if n == 0:
            return []

        min_cnt = max(2, int(min_support * n))

        # ── Step 1: Frequent 1-itemsets ──────────────────────────────────────
        item_counts = Counter()
        for t in transactions:
            item_counts.update(set(t))

        L_prev = {frozenset([item])
                  for item, cnt in item_counts.items() if cnt >= min_cnt}
        frequent = {}  # frozenset -> count
        for fs in L_prev:
            frequent[fs] = item_counts[next(iter(fs))]

        # ── Steps 2a-2d: Grow itemsets up to max_k ──────────────────────────
        for k in range(2, max_k + 1):
            if not L_prev:
                break

            # 2a: Generate candidates by joining (k-1)-itemsets
            L_prev_list = list(L_prev)
            candidates = set()
            for i in range(len(L_prev_list)):
                for j in range(i + 1, len(L_prev_list)):
                    union = L_prev_list[i] | L_prev_list[j]
                    if len(union) == k:
                        # 2b: Prune — every (k-1)-subset must be in L_prev
                        all_subsets_frequent = all(
                            (union - {item}) in L_prev
                            for item in union
                        )
                        if all_subsets_frequent:
                            candidates.add(union)

            if not candidates:
                break

            # 2c: Count candidate support
            cand_counts = Counter()
            for t in transactions:
                t_set = frozenset(t)
                for cand in candidates:
                    if cand.issubset(t_set):
                        cand_counts[cand] += 1

            # 2d: Keep candidates with sufficient support
            Lk = {cand for cand, cnt in cand_counts.items() if cnt >= min_cnt}
            for fs in Lk:
                frequent[fs] = cand_counts[fs]

            L_prev = Lk

        # ── Step 3: Generate rules from all frequent itemsets of size >= 2 ──
        rules = []
        for itemset, cnt in frequent.items():
            if len(itemset) < 2:
                continue

            itemset_support = cnt / n

            # Generate one rule per item as consequent (single-consequent rules)
            for consequent in itemset:
                antecedent = itemset - {consequent}

                # Get antecedent count from our frequent table or from 1-item counts
                if len(antecedent) == 1:
                    ant_item = next(iter(antecedent))
                    ant_cnt = item_counts.get(ant_item, 0)
                elif antecedent in frequent:
                    ant_cnt = frequent[antecedent]
                else:
                    continue  # antecedent support unknown — skip

                if ant_cnt == 0:
                    continue

                confidence = cnt / ant_cnt
                if confidence < min_confidence:
                    continue

                cons_cnt = item_counts.get(consequent, 0)
                lift = confidence / (cons_cnt / n) if cons_cnt > 0 else 0.0

                ant_list = sorted(list(antecedent))
                ant_names = [self.skill_id_to_name.get(a, a) for a in ant_list]

                rules.append({
                    'antecedent': ant_list,                         # list of skill_ids
                    'consequent': consequent,                       # single skill_id
                    'antecedent_name': ' + '.join(ant_names),      # e.g. "Python + SQL"
                    'consequent_name': self.skill_id_to_name.get(consequent, consequent),
                    'support': round(itemset_support, 4),
                    'confidence': round(confidence, 4),
                    'lift': round(lift, 4),
                    'k': len(itemset),                              # rule complexity
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

    # ── Public API ──────────────────────────────────────────────────────────────
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
        Given a skill, return other skills frequently paired with it (2-item rules only,
        so antecedent is exactly [skill_id]).
        context: 'offer' or 'require'
        Returns list of {skill_id, skill_name, confidence, lift}
        """
        self._ensure_rules()
        rules = self._offer_rules if context == 'offer' else self._require_rules

        # Only use single-antecedent rules (k=2) for per-skill suggestions
        matching = [
            r for r in rules
            if r['antecedent'] == [skill_id]
        ]
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

        min_count = 2

        edges_raw = [(a, b, cnt) for (a, b), cnt in pairs.items() if cnt >= min_count]
        edges_raw.sort(key=lambda x: x[2], reverse=True)
        edges_raw = edges_raw[:top_edges]

        involved_skills = set()
        for a, b, _ in edges_raw:
            involved_skills.add(a)
            involved_skills.add(b)

        nodes = [
            {
                'id': sid,
                'label': self.skill_id_to_name.get(sid, sid),
                'frequency': items.get(sid, 0),
            }
            for sid in involved_skills
        ]

        max_cnt = max(cnt for _, _, cnt in edges_raw) if edges_raw else 1
        edges = [
            {
                'from': a,
                'to': b,
                'weight': cnt,
                'normalized': round(cnt / max_cnt, 3),
            }
            for a, b, cnt in edges_raw
        ]

        return {'nodes': nodes, 'edges': edges}


if __name__ == '__main__':
    engine = AssociationEngine()
    engine._ensure_rules()
    offer_rules = engine._offer_rules

    total = len(offer_rules)
    k2 = sum(1 for r in offer_rules if r['k'] == 2)
    k3 = sum(1 for r in offer_rules if r['k'] == 3)

    print(f"Total offer rules: {total}  (2-item: {k2}, 3-item: {k3})")
    print("\nTop 10 Offer Rules (by lift):")
    for r in engine.get_top_offer_rules(10):
        print(f"  [{r['k']}-item]  {r['antecedent_name']} → {r['consequent_name']}"
              f"  conf={r['confidence']:.2f}  lift={r['lift']:.2f}  supp={r['support']:.3f}")

    print('\nNetwork graph nodes:', len(engine.get_network_graph_data()['nodes']))
    print('Network graph edges:', len(engine.get_network_graph_data()['edges']))
