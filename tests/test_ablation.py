import unittest
from unittest.mock import patch

from scripts.ablation import compare


def rule_fixtures(dataset, features):
    secondary = {"target": None, "cf": 0.95}
    matching = [{"target": dataset, "cf": 0.15}] * features["matched"]
    return [], [secondary, *matching]


@patch("scripts.ablation.evaluate_rules", side_effect=rule_fixtures)
class AblationTests(unittest.TestCase):
    def test_same_covered_ids_for_every_variant_and_label_change(self, _rules):
        metrics, predictions, summary = compare("pima", [
            ("pima:0001", 1, "0.25", {"matched": 2}),
            ("pima:0002", 0, 0.2, {"matched": 0}),
        ], split="validation")

        self.assertEqual(len(predictions), 8)
        self.assertTrue(all(row[2:4] == ("validation", "ablation") for row in predictions))
        by_id_variant = {(row[1], row[4]): row[5:] for row in predictions}
        self.assertEqual(by_id_variant["pima:0002", "rule"], (0, None, None, 0))
        self.assertEqual(by_id_variant["pima:0002", "combined_new"], (0, 0, 0.2, 0))
        self.assertEqual(by_id_variant["pima:0002", "combined_old"], (0, 0, 0.2, 0))
        self.assertEqual(by_id_variant["pima:0001", "combined_new"][1], 0)
        self.assertEqual(by_id_variant["pima:0001", "combined_old"][1], 1)
        self.assertEqual(summary["n_covered"], 1)
        self.assertEqual(summary["coverage"], 0.5)
        self.assertEqual(summary["covered_label_counts"], {"0": 0, "1": 1})
        self.assertEqual(summary["old_new"]["n_label_changes"], 1)
        delta = (by_id_variant["pima:0001", "combined_new"][2]
                 - by_id_variant["pima:0001", "combined_old"][2])
        self.assertAlmostEqual(summary["old_new"]["mean_new_minus_old"], delta / 2)
        self.assertAlmostEqual(summary["old_new"]["max_abs_delta"], abs(delta))
        by_variant = {(row[4], row[2], row[6]): (row[5], row[7]) for row in metrics}
        self.assertNotIn(("all", "rule", "accuracy"), by_variant)
        self.assertEqual(by_variant["all", "ml", "accuracy"], (2, 0.5))
        self.assertEqual(by_variant["covered", "ml", "accuracy"], (1, 0.0))
        self.assertEqual(by_variant["covered", "combined_old", "accuracy"], (1, 1.0))
        self.assertEqual(by_variant["covered", "rule", "roc_auc"], (1, None))
        self.assertIn("roc_auc", summary["undefined_metrics"]["covered"]["rule"])

    def test_retains_metrics_when_no_target_rules_match(self, _rules):
        metrics, _, summary = compare("cleveland", [
            ("cleveland:0001", 0, 0.4, {"matched": 0}),
        ], split="validation")
        self.assertEqual(summary["coverage"], 0.0)
        self.assertEqual(summary["n_covered"], 0)
        self.assertEqual(summary["covered_label_counts"], {"0": 0, "1": 0})
        self.assertEqual(summary["old_new"]["n_label_changes"], 0)
        rule_accuracy = next(row for row in metrics if row[2] == "rule" and row[6] == "accuracy")
        self.assertEqual(rule_accuracy[4:], ("covered", 0, "accuracy", None, None))
        self.assertEqual(summary["undefined_metrics"]["covered"]["rule"]["accuracy"], "no samples")
