"""Check metric definitions with small labels and scores calculated by hand."""

import unittest

from medical_expert.ml.metrics import aggregate_metrics, binary_metrics


class BinaryMetricsTest(unittest.TestCase):
    def test_confusion_metrics_and_score_based_auc_with_ties(self):
        metric, undefined = binary_metrics(
            [1, 1, 0, 0, 0], [1, 0, 1, 0, 0], [0.9, 0.3, 0.5, 0.3, 0.1],
        )
        self.assertEqual(undefined, {})
        self.assertEqual(metric, {
            "accuracy": 3 / 5,
            "precision": 1 / 2,
            "recall": 1 / 2,
            "f1": 1 / 2,
            "roc_auc": 4.5 / 6,
            "tn": 2,
            "fp": 1,
            "fn": 1,
            "tp": 1,
        })

    def test_constant_majority_scores_and_no_predicted_positives(self):
        metric, undefined = binary_metrics([0, 1, 0], [0, 0, 0], [0.25, 0.25, 0.25])
        self.assertIsNone(metric["precision"])
        self.assertEqual(metric["recall"], 0)
        self.assertEqual(metric["f1"], 0)
        self.assertEqual(metric["roc_auc"], 0.5)
        self.assertEqual(set(undefined), {"precision"})

    def test_undefined_metrics_for_one_class_and_empty_subsets(self):
        metric, undefined = binary_metrics([0], [0], [0])
        self.assertEqual(metric["accuracy"], 1)
        self.assertEqual(set(undefined), {"precision", "recall", "f1", "roc_auc"})
        self.assertTrue(all(metric[name] is None for name in undefined))
        metric, undefined = binary_metrics([0], [1], [1])
        self.assertEqual(metric["f1"], 0)
        self.assertEqual(set(undefined), {"recall", "roc_auc"})
        metric, undefined = binary_metrics([], [], [])
        self.assertEqual(set(undefined), {"accuracy", "precision", "recall", "f1", "roc_auc"})
        self.assertTrue(all(metric[name] is None for name in undefined))
        self.assertEqual([metric[name] for name in ("tn", "fp", "fn", "tp")], [0] * 4)

    def test_aggregate_ignores_undefined_values_and_uses_population_std(self):
        result = aggregate_metrics([
            {"f1": 0.25, "precision": None, "recall": 0.5},
            {"f1": 0.75, "precision": None, "recall": None},
            {"f1": None, "precision": None, "recall": None},
        ])
        self.assertEqual(result, {
            "f1": (0.5, 0.25), "precision": (None, None), "recall": (0.5, 0.0),
        })


if __name__ == "__main__":
    unittest.main()
