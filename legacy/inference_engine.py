import json

class ExpertEngine:
    def __init__(self, kb_file='knowledge_base.json'):
        with open(kb_file, 'r', encoding='utf-8') as f:
            self.knowledge_base = json.load(f)['rules']

    def combine_cf(self, cf1, cf2):
        if cf1 > 0 and cf2 > 0: return cf1 + cf2 * (1 - cf1)
        if cf1 < 0 and cf2 < 0: return cf1 + cf2 * (1 + cf1)
        return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))

    def forward_chaining(self, disease_prefix, facts, ml_cf):
        conclusions, fired = {}, []
        for rule in self.knowledge_base:
            if not rule['id'].startswith(disease_prefix): continue
            if all(facts.get(k) == v for k, v in rule['conditions'].items()):
                fired.append(rule['id'])
                conc, rule_cf = rule['conclusion'], rule['cf']
                final_cf = self.combine_cf(rule_cf, ml_cf)
                if conc in conclusions:
                    conclusions[conc]['cf'] = self.combine_cf(conclusions[conc]['cf'], final_cf)
                    conclusions[conc]['rules'].append(rule['id'])
                else:
                    conclusions[conc] = {'cf': final_cf, 'rules': [rule['id']]}
        return conclusions, fired