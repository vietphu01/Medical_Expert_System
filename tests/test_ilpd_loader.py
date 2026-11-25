import tempfile
import unittest
from pathlib import Path

from medical_expert.data.ilpd import load_ilpd


class IlpdLoaderTests(unittest.TestCase):
    def load(self, *rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Indian Liver Patient Dataset (ILPD).csv"
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            return load_ilpd(path)

    def test_projects_features_and_preserves_label_mapping(self):
        samples, metadata = self.load(
            "55,Female,1.3,0.4,168,24,39,6.9,3.3,0.9,1",
            "38,Male,0.7,0.2,195,16,28,7.4,4.2,1.3,2",
        )
        self.assertEqual([sample.y for sample in samples], [1, 0])
        self.assertEqual(samples[0].features, {"bilirubin": 1.3, "albumin": 3.3, "age": 55})
        self.assertIs(type(samples[0].features["age"]), int)
        self.assertEqual(metadata["feature_order"], ["bilirubin", "albumin", "age"])
        self.assertEqual(metadata["feature_units"], {"bilirubin": None, "albumin": None, "age": "years"})
        self.assertEqual(metadata["raw_label_counts"], {"1": 1, "2": 1})
        self.assertFalse(metadata["source"]["matches_verified_release"])

    def test_counts_missing_and_deduplicates_by_full_source_row(self):
        row = "58,Male,?,0.5,167,35,31,6.6,3.4,,1"
        samples, metadata = self.load(
            row,
            row,
            "58,Female,?,0.5,167,35,31,6.6,3.4,,1",
        )
        self.assertEqual([sample.sample_id for sample in samples], ["ilpd:0001", "ilpd:0003"])
        self.assertEqual(samples[0].features, {"bilirubin": None, "albumin": 3.4, "age": 58})
        self.assertEqual(samples[0].features, samples[1].features)
        self.assertEqual(metadata["duplicate_rows"], 1)
        self.assertEqual(metadata["source_missing_by_column"]["A/G Ratio"], 3)
        self.assertEqual(metadata["missing_by_feature"]["bilirubin"], 2)

    def test_rejects_invalid_schema_and_label(self):
        invalid = (
            ("51,Female,0.6,0.2,165,15,20,6.3,3.2,1.0", "expected 11 columns"),
            ("51,Female,0.6,0.2,165,15,20,6.3,3.2,1.0,0", "invalid label in Selector"),
            ("51,Other,0.6,0.2,165,15,20,6.3,3.2,1.0,1", "Gender"),
            ("51,Female,0.6,0.2,165,high,20,6.3,3.2,1.0,1", "Sgpt must be numeric"),
            ("51.5,Female,0.6,0.2,165,15,20,6.3,3.2,1.0,1", "age must be an integer"),
        )
        for row, message in invalid:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    self.load(row)
