"""Check DecisionTreeScratch leaf tie-breaking and fuzzy_membership bounds."""

import unittest

import numpy as np

from medical_expert.expert.fuzzy import fuzzy_membership
from medical_expert.ml.algorithms import DecisionTreeScratch


class DecisionTreeAndFuzzyTests(unittest.TestCase):
    def test_tied_leaf_class_matches_predict_threshold(self):
        # Two identical points with opposite labels force a [1, 1] tied leaf.
        X = np.array([[0.0], [0.0]])
        y = np.array([0, 1])
        tree = DecisionTreeScratch(max_depth=2, min_samples_split=2).fit(X, y)
        self.assertTrue(tree.tree['leaf'])
        self.assertEqual(tree.tree['dist'], [1, 1])
        self.assertEqual(tree.tree['class'], 1)
        self.assertEqual(int(tree.predict(np.array([[0.0]]))[0]), 1)
        self.assertIn('Class=1', tree.export_rules(['x']))

    def test_fuzzy_membership_rejects_invalid_bounds_or_direction(self):
        with self.assertRaises(ValueError):
            fuzzy_membership(10, 20, 20)
        with self.assertRaises(ValueError):
            fuzzy_membership(10, 20, 10)
        with self.assertRaises(ValueError):
            fuzzy_membership(10, 0, 20, direction='sideways')
        self.assertAlmostEqual(fuzzy_membership(15, 10, 20, direction='desc'), 0.5)


if __name__ == '__main__':
    unittest.main()
