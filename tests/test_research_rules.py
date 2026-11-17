"""Check the reviewed rule mappings using invented cases."""

import unittest

from research_rules import evaluate_rules


class ResearchRulesTest(unittest.TestCase):
    def test_cleveland_threshold_and_secondary_rule(self):
        facts, fired = evaluate_rules("cleveland", {"age": 55, "bp": 160, "chol": 200})
        self.assertEqual(fired, [])
        self.assertEqual(next(f for f in facts if f["feature"] == "chol")["membership"], 0.5)
        _, fired = evaluate_rules("cleveland", {"age": 54, "chol": 201})
        self.assertEqual([rule["target"] for rule in fired], [None])
        _, fired = evaluate_rules("cleveland", {"age": 55, "chol": 201})
        self.assertEqual([rule["target"] for rule in fired], ["cleveland", None])

    def test_pima_overlap_and_missing_bmi(self):
        facts, fired = evaluate_rules("pima", {"age": 35, "glucose": 190, "bmi": None})
        self.assertEqual(fired, [])
        self.assertTrue(all(f["membership"] is None for f in facts if f["feature"] == "bmi"))
        _, fired = evaluate_rules("pima", {"age": 70, "bmi": 30.1})
        self.assertEqual([rule["id"] for rule in fired], ["PIMA_TARGET_01", "PIMA_TARGET_02"])
        _, fired = evaluate_rules("pima", {"age": 71, "bmi": 32})
        self.assertEqual(fired, [])

    def test_unverified_measurements_are_only_visible_as_values(self):
        for dataset, inputs, unit in [
            ("ilpd", {"bilirubin": 8}, None),
            ("ckd", {"bp": 180}, "mmHg"),
        ]:
            with self.subTest(dataset=dataset):
                facts, fired = evaluate_rules(dataset, inputs)
                self.assertEqual(fired, [])
                feature = next(iter(inputs))
                fact = next(f for f in facts if f["feature"] == feature)
                self.assertIsNone(fact["key"])
                self.assertIsNone(fact["value_boolean"])
                self.assertEqual(fact["unit"], unit)
