"""Check continuous fuzzy rules, non-overlapping Pima rules, and rule schema."""

import unittest

from medical_expert.expert.rules import evaluate_rules, rule_schema


class ResearchRulesTest(unittest.TestCase):
    def test_cleveland_continuous_fuzzy_scaling_and_secondary_rule(self):
        # At or below 180, chol membership is 0 so no rule fires.
        facts, fired = evaluate_rules("cleveland", {"age": 55, "bp": 160, "chol": 180})
        self.assertEqual(fired, [])
        self.assertEqual(next(f for f in facts if f["feature"] == "chol")["membership"], 0.0)

        # At chol = 200 (mu = 0.5), continuous fuzzy scales CF by 0.5 instead of hard cliff.
        facts, fired = evaluate_rules("cleveland", {"age": 55, "bp": 160, "chol": 200})
        self.assertEqual(next(f for f in facts if f["feature"] == "chol")["membership"], 0.5)
        by_id = {rule["id"]: rule for rule in fired}
        self.assertEqual(set(by_id), {"CLEV_TARGET_01", "CLEV_SECONDARY_01"})
        self.assertAlmostEqual(by_id["CLEV_TARGET_01"]["degree"], 0.5)
        self.assertAlmostEqual(by_id["CLEV_TARGET_01"]["cf"], 0.175)
        self.assertAlmostEqual(by_id["CLEV_SECONDARY_01"]["cf"], 0.15)

        # Age < 55 fires only secondary rule.
        _, fired = evaluate_rules("cleveland", {"age": 54, "chol": 220})
        self.assertEqual([rule["target"] for rule in fired], [None])
        self.assertAlmostEqual(fired[0]["cf"], 0.30)

        # Full membership at chol >= 220 gives base CF (0.35 < 0.5 so ML is not vetoed).
        _, fired = evaluate_rules("cleveland", {"age": 55, "chol": 240})
        self.assertEqual([rule["target"] for rule in fired], ["cleveland", None])
        self.assertAlmostEqual(fired[0]["cf"], 0.35)

    def test_pima_single_continuous_rule_without_age_70_cap_and_missing_bmi(self):
        facts, fired = evaluate_rules("pima", {"age": 35, "glucose": 190, "bmi": None})
        self.assertEqual(fired, [])
        self.assertTrue(all(f["membership"] is None for f in facts if f["feature"] == "bmi"))

        # BMI <= 25 does not fire.
        _, fired = evaluate_rules("pima", {"age": 45, "bmi": 25.0})
        self.assertEqual(fired, [])

        # Mild overweight BMI = 26 gives small proportional CF (no veto over low ML).
        _, fired = evaluate_rules("pima", {"age": 45, "bmi": 26.0})
        self.assertEqual([rule["id"] for rule in fired], ["PIMA_TARGET_01"])
        self.assertAlmostEqual(fired[0]["degree"], 1.0 / 7.0)
        self.assertAlmostEqual(fired[0]["cf"], 0.35 / 7.0)

        # Elderly patients (> 70) with elevated BMI are covered (no artificial age-70 cap)
        # and only one non-overlapping rule fires.
        _, fired = evaluate_rules("pima", {"age": 75, "bmi": 32.0})
        self.assertEqual([rule["id"] for rule in fired], ["PIMA_TARGET_01"])
        self.assertAlmostEqual(fired[0]["degree"], 1.0)
        self.assertAlmostEqual(fired[0]["cf"], 0.35)

    def test_rule_schema_matches_backend_definitions(self):
        pima = rule_schema("pima")
        self.assertEqual(pima["target_rules"], [["age_at_least_35", "bmi_elevated"]])
        self.assertEqual(pima["fact_specs"]["bmi"], [{"key": "bmi_elevated", "kind": "ramp", "bounds": [25, 32]}])
        self.assertEqual(rule_schema("ckd"), {"fact_specs": {}, "target_rules": []})

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
