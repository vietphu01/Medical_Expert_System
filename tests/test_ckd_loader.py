"""Contract tests use invented records, never the final holdout."""
import tempfile
import unittest
from pathlib import Path

from medical_expert.data.ckd import CKD_COLUMNS, CKD_SOURCE, load_ckd


class CKDLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fixture.csv"
        self.row = ["41", "80", "1.020", "0", "0", "normal", "normal",
                    "notpresent", "notpresent", "100", "30", "1.1", "140",
                    "4.0", "13", "40", "7000", "4.5", "no", "no", "no",
                    "good", "no", "no", "ckd"]

    def load(self, rows, header=CKD_COLUMNS):
        self.path.write_text(",".join(header) + "\n" + "\n".join(",".join(r) for r in rows) + "\n", encoding="utf-8")
        return load_ckd(self.path)

    def test_whitespace_missing_and_metadata(self):
        second = self.row.copy()
        second[0], second[1], second[11], second[19], second[-1] = "?", "NaN", "", "\tno ", " notckd\t"
        samples, metadata = self.load([self.row, second])
        self.assertEqual(samples[0].features, {"creatinine": 1.1, "bp": 80.0, "age": 41})
        self.assertEqual(samples[1].features, {"creatinine": None, "bp": None, "age": None})
        self.assertEqual([s.y for s in samples], [1, 0])
        self.assertEqual(metadata["missing_by_feature"], {"creatinine": 1, "bp": 1, "age": 1})
        self.assertEqual(metadata["feature_units"]["bp"], "mmHg")
        self.assertIn("not specified", metadata["source"]["bp_measurement"])
        self.assertEqual(metadata["source"]["download_url"], CKD_SOURCE["download_url"])

    def test_duplicates_use_entire_source_record(self):
        different = self.row.copy()
        different[5] = "abnormal"
        spaced = self.row.copy()
        spaced[5] = "  normal\t"
        samples, metadata = self.load([self.row, different, spaced])
        self.assertEqual(len(samples), 2)
        self.assertEqual(metadata["duplicate_rows"], 1)
        self.assertEqual([s.sample_id for s in samples], ["ckd:0001", "ckd:0002"])

    def test_rejects_bad_schema_label_nominal_and_nonfinite(self):
        header = list(CKD_COLUMNS)
        header[0], header[1] = header[1], header[0]
        with self.assertRaisesRegex(ValueError, "unexpected columns"):
            self.load([self.row], header)
        with self.assertRaisesRegex(ValueError, "expected 25 columns"):
            self.load([self.row[1:]])
        for column, value in (
            ("class", "unknown"), ("rbc", "other"), ("sg", "1.023"),
            ("sc", "inf"), ("age", "41.5"),
        ):
            with self.subTest(column=column), self.assertRaisesRegex(ValueError, column):
                row = self.row.copy()
                row[CKD_COLUMNS.index(column)] = value
                self.load([row])


if __name__ == "__main__":
    unittest.main()
