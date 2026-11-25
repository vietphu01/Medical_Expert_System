"""Check fusion formulas and trace behavior with invented facts and rules."""

import json
import unittest

from medical_expert.expert.fusion import fusion_scores, make_trace


def fired_rule(rule_id, target, cf):
    return {
        "id": rule_id,
        "conditions": ["high_marker"],
        "target": target,
        "conclusion": "Marker elevation",
        "cf": cf,
    }


class FusionTest(unittest.TestCase):
    def test_single_target_rule_uses_ml_once_in_both_variants(self):
        scores = fusion_scores(0.4, [0.6])
        self.assertEqual(scores["ml"], 0.4)
        self.assertEqual(scores["rule"], 0.6)
        self.assertAlmostEqual(scores["combined_new"], 0.76)
        self.assertEqual(scores["combined_new"], scores["combined_old"])

    def test_multiple_rules_with_shared_premise_make_old_score_higher(self):
        rules = [fired_rule("RULE_01", "cleveland", 0.2),
                 fired_rule("RULE_02", "cleveland", 0.3)]
        scores = fusion_scores(0.4, [rule["cf"] for rule in rules])
        self.assertAlmostEqual(scores["rule"], 0.44)
        self.assertAlmostEqual(scores["combined_new"], 0.664)
        self.assertAlmostEqual(scores["combined_old"], 0.7984)
        trace = make_trace("cleveland", "Logistic Regression", 0.4, [], rules)
        self.assertEqual(trace["result"]["combined_score"], scores["combined_new"])
        self.assertEqual([rule["used_in_fusion"] for rule in trace["fired_rules"]], [True, True])

    def test_trace_retains_unknown_fact_and_excludes_unrelated_rules_from_fusion(self):
        facts = [
            {
                "feature": "marker", "value": 30, "unit": "unit", "membership": 0.75,
                "key": "high_marker", "value_boolean": True,
            },
            {
                "feature": "other", "value": None, "unit": "unit", "membership": None,
                "key": "high_other", "value_boolean": None,
            },
        ]
        rules = [fired_rule("RULE_01", "cleveland", 0.5), fired_rule("RULE_02", None, 0.9),
                 fired_rule("RULE_03", "pima", 1.0)]
        trace = make_trace("cleveland", "Logistic Regression", 0.0, facts, rules)
        self.assertEqual(json.loads(json.dumps(trace)), {
            "target": "cleveland",
            "ml": {"model": "Logistic Regression", "score": 0.0},
            "facts": facts,
            "fired_rules": [
                {**rule, "used_in_fusion": rule["target"] == "cleveland"} for rule in rules
            ],
            "result": {
                "rule_status": "matched",
                "rule_score": 0.5,
                "combined_score": 0.5,
                "predicted_label": 1,
            },
        })
        self.assertTrue(all("used_in_fusion" not in rule for rule in rules))

    def test_no_target_rule_falls_back_to_ml(self):
        self.assertEqual(fusion_scores(0.49, []), {
            "ml": 0.49, "rule": None, "combined_new": 0.49, "combined_old": 0.49,
        })
        for rules in ([], [fired_rule("RULE_01", None, 1.0)]):
            with self.subTest(rules=rules):
                trace = make_trace("cleveland", "Logistic Regression", 0.49, [], rules)
                self.assertEqual(trace["result"], {
                    "rule_status": "no_matching_target_rule",
                    "rule_score": None,
                    "combined_score": 0.49,
                    "predicted_label": 0,
                })

    def test_rejects_invalid_scores_and_rule_cfs(self):
        for value in (-0.01, 1.01, float("nan"), float("inf"), "0.5", None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "ML score"):
                    fusion_scores(value, [])
                with self.assertRaisesRegex(ValueError, "rule CF"):
                    fusion_scores(0.5, [value])


if __name__ == "__main__":
    unittest.main()
