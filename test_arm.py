import sys
sys.path.insert(0, 'modules')
from association_engine import AssociationEngine
e = AssociationEngine()
rules = e.get_top_offer_rules(10)
print(f'Total offer rules: {len(rules)}')
for r in rules:
    print(f"  {r['antecedent_name']} -> {r['consequent_name']}  conf={r['confidence']}  lift={r['lift']}")

print()
rules2 = e.get_top_require_rules(5)
print(f'Total require rules: {len(rules2)}')
for r in rules2:
    print(f"  {r['antecedent_name']} -> {r['consequent_name']}  conf={r['confidence']}  lift={r['lift']}")

g = e.get_network_graph_data()
print(f"\nNetwork: {len(g['nodes'])} nodes, {len(g['edges'])} edges")
