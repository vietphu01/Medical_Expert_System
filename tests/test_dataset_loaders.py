"""Regression tests using invented rows, never project data or held-out samples."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from medical_expert.data.loaders import load_cleveland, load_pima


PIMA_HEADER = """% Fixture with the schema of the selected OpenML release
@relation pima_diabetes
@attribute 'preg' real
@attribute 'plas' real
@attribute 'pres' real
@attribute 'skin' real
@attribute 'insu' real
@attribute 'mass' real
@attribute 'pedi' real
@attribute 'age' real
@attribute 'class' { tested_negative, tested_positive}
@data
"""


class LoaderTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "fixture.data"

    def load(self, loader, text):
        self.path.write_text(text, encoding="utf-8")
        return loader(self.path)

    def assert_bad(self, loader, text, column):
        with self.assertRaises(ValueError) as error:
            self.load(loader, text)
        self.assertIn(column.lower(), str(error.exception).lower())

    def test_cleveland_projection_duplicates_labels_missing_and_metadata(self):
        first = "45,1,2,120,200,0,1,150,0,1.0,2,?,3,0"
        # Same projection, but different unselected source feature or raw label.
        other = "45,0,2,120,200,0,1,150,0,1.0,2,?,3,1"
        other_label = "45,0,2,120,200,0,1,150,0,1.0,2,?,3,4"
        missing = "?,1,2,,210,0,1,150,0,1.0,2,0,3,2"
        content = "\n".join([first, first, other, other_label, missing]) + "\n"
        samples, metadata = self.load(load_cleveland, content)
        self.assertEqual([s.sample_id for s in samples],
                         ["cleveland:0001", "cleveland:0003", "cleveland:0004", "cleveland:0005"])
        self.assertEqual([s.y for s in samples], [0, 1, 1, 1])
        self.assertEqual(list(samples[0].features), ["age", "bp", "chol"])
        self.assertEqual(samples[0].features, {"age": 45, "bp": 120, "chol": 200})
        self.assertIsInstance(samples[0].features["age"], int)
        self.assertEqual(samples[-1].features, {"age": None, "bp": None, "chol": 210})
        self.assertEqual(metadata["raw_rows"], 5)
        self.assertEqual(metadata["n_samples"], 4)
        self.assertEqual(metadata["duplicate_rows"], 1)
        self.assertEqual(metadata["label_counts"], {"0": 1, "1": 3})
        self.assertEqual(metadata["raw_label_counts"], {"0": 2, "1": 1, "2": 1, "3": 0, "4": 1})
        self.assertEqual(metadata["source_missing_by_column"]["ca"], 4)
        self.assertEqual(metadata["source_missing_by_column"]["age"], 1)
        self.assertEqual(metadata["source_missing_by_column"]["trestbps"], 1)
        self.assertEqual(metadata["missing_by_feature"]["age"], 1)
        self.assertEqual(metadata["missing_by_feature"]["bp"], 1)
        self.assertEqual(metadata["source"]["sha256"], hashlib.sha256(content.encode()).hexdigest())
        again, _ = load_cleveland(self.path)
        self.assertEqual([s.sample_id for s in again], [s.sample_id for s in samples])

    def test_cleveland_all_documented_label_codes(self):
        rows = [f"45,1,2,120,200,0,1,150,0,1.0,2,0,3,{label}"
                for label in range(5)]
        samples, _ = self.load(load_cleveland, "\n".join(rows) + "\n")
        self.assertEqual([s.y for s in samples], [0, 1, 1, 1, 1])

    def test_cleveland_rejects_invalid_rows(self):
        base = "45,1,2,120,200,0,1,150,0,1.0,2,0,3,0".split(",")
        for index, value, column in [(0, "45.5", "age"), (3, "nan", "trestbps"),
                                     (4, "inf", "chol"), (1, "bad", "sex"),
                                     (13, "5", "num"), (13, "?", "num")]:
            with self.subTest(column=column, value=value):
                row = base.copy()
                row[index] = value
                self.assert_bad(load_cleveland, ",".join(row) + "\n", column)
        self.assert_bad(load_cleveland, ",".join(base[:-1]) + "\n", "column")

    def test_pima_sentinel_duplicates_labels_missing_and_metadata(self):
        first = "0,0,70,20,80,0,0.5,30,tested_negative"
        # Differ in an unselected field or raw sentinel representation; no dedup.
        other = "1,0,70,20,80,0,0.5,30,tested_negative"
        native_missing = "0,?,70,20,80,,0.5,30,tested_negative"
        positive = "2,130,?,20,80,25,0.5,40,tested_positive"
        content = PIMA_HEADER + "\n".join([first, first, other, native_missing, positive]) + "\n"
        samples, metadata = self.load(load_pima, content)
        self.assertEqual([s.sample_id for s in samples],
                         ["pima:0001", "pima:0003", "pima:0004", "pima:0005"])
        self.assertEqual([s.y for s in samples], [0, 0, 0, 1])
        self.assertEqual(list(samples[0].features), ["glucose", "bmi", "age"])
        self.assertEqual(samples[0].features, {"glucose": None, "bmi": None, "age": 30})
        self.assertIsInstance(samples[0].features["age"], int)
        self.assertEqual(samples[-1].features, {"glucose": 130, "bmi": 25, "age": 40})
        self.assertEqual(metadata["raw_rows"], 5)
        self.assertEqual(metadata["n_samples"], 4)
        self.assertEqual(metadata["duplicate_rows"], 1)
        self.assertEqual(metadata["label_counts"], {"0": 3, "1": 1})
        self.assertEqual(metadata["raw_label_counts"], {"tested_negative": 4, "tested_positive": 1})
        self.assertEqual(metadata["source_missing_by_column"]["plas"], 1)
        self.assertEqual(metadata["source_missing_by_column"]["mass"], 1)
        self.assertEqual(metadata["source_missing_by_column"]["pres"], 1)
        self.assertEqual(metadata["zero_sentinel_by_column"]["plas"], 3)
        self.assertEqual(metadata["zero_sentinel_by_column"]["mass"], 3)
        self.assertEqual(metadata["missing_by_feature"]["glucose"], 3)
        self.assertEqual(metadata["missing_by_feature"]["bmi"], 3)
        self.assertEqual(metadata["source"]["sha256"], hashlib.sha256(content.encode()).hexdigest())
        again, _ = load_pima(self.path)
        self.assertEqual([s.sample_id for s in again], [s.sample_id for s in samples])

    def test_pima_canonicalizes_values_before_comparing_full_rows(self):
        text = (PIMA_HEADER + "0,100,70,20,80,25,?,30,tested_negative\n"
                + "% A full-line comment between records\n\n"
                + "0.0,100.0,70,20,80,25,,30.0,tested_negative\n")
        samples, metadata = self.load(load_pima, text)
        self.assertEqual([sample.sample_id for sample in samples], ["pima:0001"])
        self.assertEqual(metadata["raw_rows"], 2)
        self.assertEqual(metadata["duplicate_rows"], 1)
        self.assertEqual(metadata["source_missing_by_column"]["pedi"], 2)

    def test_pima_rejects_schema_and_bad_values(self):
        row = "0,100,70,20,80,25,0.5,30,tested_negative"
        for bad_header in [PIMA_HEADER.replace("pima_diabetes", "other"),
                           PIMA_HEADER.replace("'preg'", "'other'"),
                           PIMA_HEADER.replace("'plas' real", "'plas' string"),
                           PIMA_HEADER.replace("tested_negative, tested_positive", "no, yes")]:
            with self.subTest(header=bad_header):
                self.assert_bad(load_pima, bad_header + row + "\n", "header")
        base = row.split(",")
        for index, value, column in [(0, "nan", "preg"), (1, "inf", "plas"),
                                     (5, "bad", "mass"), (7, "30.5", "age"),
                                     (8, "1", "class"), (8, "?", "class")]:
            with self.subTest(column=column, value=value):
                fields = base.copy()
                fields[index] = value
                self.assert_bad(load_pima, PIMA_HEADER + ",".join(fields) + "\n", column)
        self.assert_bad(load_pima, PIMA_HEADER + ",".join(base[:-1]) + "\n", "column")
        self.assert_bad(load_pima, PIMA_HEADER + "{0 1, 8 tested_positive}\n", "column")


if __name__ == "__main__":
    unittest.main()
