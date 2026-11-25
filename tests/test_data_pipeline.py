"""Integration tests using invented Cleveland CSV and Pima ARFF records."""

import json
import tempfile
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

from medical_expert.data.pipeline import make_manifest, prepare_fold
from medical_expert.data.loaders import load_cleveland, load_pima
from test_dataset_loaders import PIMA_HEADER


class DataPipelineTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "fixture.data"

    def load_cleveland_fixture(self):
        # Adjacent pairs share their projection but differ in sex.
        rows = [
            f"{40 + index // 2},{index % 2},2,120,200,0,1,150,0,1,2,"
            f"{'?' if index == 0 else 0},{'?' if index == 1 else 3},"
            f"{0 if index < 32 else (4 if index == 54 else 1 + index % 3)}"
            for index in range(55)
        ]
        self.path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return load_cleveland(self.path)

    def load_pima_fixture(self):
        rows = []
        for index in range(41):
            label = "tested_negative" if index < 27 else "tested_positive"
            glucose = 0 if index < 2 else 100 + index // 2
            bmi = 0 if index < 2 else 25 + index // 2
            rows.append(f"{index % 2},{glucose},70,20,80,{bmi},0.5,30,{label}")
        self.path.write_text(PIMA_HEADER + "\n".join(rows) + "\n", encoding="utf-8")
        return load_pima(self.path)

    def test_stratified_manifests_are_reproducible_complete_and_disjoint(self):
        for loader, holdout_counts in [
            (self.load_cleveland_fixture, {0: 6, 1: 5}),
            (self.load_pima_fixture, {0: 6, 1: 3}),
        ]:
            samples, metadata = loader()
            with self.subTest(dataset=metadata["dataset"]):
                by_id = {sample.sample_id: sample for sample in samples}
                self.assertEqual(len(by_id), metadata["raw_rows"])
                self.assertEqual(samples[0].features, samples[1].features)
                if metadata["dataset"] == "cleveland":
                    self.assertEqual(metadata["raw_label_counts"]["4"], 1)
                    self.assertEqual(samples[-1].y, 1)
                    self.assertEqual(metadata["source_missing_by_column"]["ca"], 1)
                    self.assertEqual(metadata["source_missing_by_column"]["thal"], 1)
                manifest = make_manifest(samples, metadata)
                regenerated = make_manifest(list(reversed(samples)), metadata, seed=42)
                self.assertEqual(json.dumps(manifest), json.dumps(regenerated))
                self.assertEqual(json.loads(json.dumps(manifest)), manifest)
                self.assertEqual(manifest["seed"], 42)
                self.assertEqual(manifest["dataset"], metadata["dataset"])
                self.assertEqual(manifest["source_sha256"], metadata["source"]["sha256"])
                self.assertEqual(manifest["feature_order"], metadata["feature_order"])

                train_ids = set(manifest["train_ids"])
                test_ids = set(manifest["test_ids"])
                self.assertEqual(len(train_ids), len(manifest["train_ids"]))
                self.assertEqual(len(test_ids), len(manifest["test_ids"]))
                self.assertTrue(train_ids.isdisjoint(test_ids))
                self.assertEqual(train_ids | test_ids, set(by_id))
                self.assertEqual(Counter(by_id[sid].y for sid in test_ids), holdout_counts)

                seen = Counter()
                sizes = []
                class_sizes = {0: [], 1: []}
                self.assertEqual([fold["fold"] for fold in manifest["folds"]], list(range(1, 6)))
                for fold in manifest["folds"]:
                    validation = fold["validation_ids"]
                    fold_train = set(fold["train_ids"])
                    self.assertEqual(len(fold_train), len(fold["train_ids"]))
                    self.assertTrue(fold_train.isdisjoint(validation))
                    self.assertEqual(fold_train | set(validation), train_ids)
                    self.assertEqual({by_id[sid].y for sid in fold_train}, {0, 1})
                    seen.update(validation)
                    sizes.append(len(validation))
                    counts = Counter(by_id[sid].y for sid in validation)
                    self.assertEqual(set(counts), {0, 1})
                    for label in class_sizes:
                        class_sizes[label].append(counts[label])
                self.assertEqual(seen, dict.fromkeys(train_ids, 1))
                for counts in [sizes, *class_sizes.values()]:
                    self.assertLessEqual(max(counts) - min(counts), 1)

    def test_fold_imputes_and_scales_with_train_statistics_only(self):
        samples, metadata = self.load_pima_fixture()
        self.assertIsNone(samples[0].features["glucose"])
        self.assertIsNone(samples[0].features["bmi"])
        manifest = make_manifest(samples, metadata)
        fold = manifest["folds"][0]
        # An even number of observed glucose values gives median 140. Each
        # remaining training value is missing and must be imputed before scaling.
        observed_glucose = [100, 120, 160, 240]
        glucose_by_id = dict(zip(fold["train_ids"], observed_glucose))
        train_ids = set(fold["train_ids"])
        missing_validation_id = fold["validation_ids"][0]
        samples = [
            replace(sample, features={
                "glucose": glucose_by_id.get(sample.sample_id), "bmi": 24.9, "age": 30,
            }) if sample.sample_id in train_ids or sample.sample_id == missing_validation_id
            else sample
            for sample in samples
        ]
        originals = {sample.sample_id: dict(sample.features) for sample in samples}
        baseline = prepare_fold(samples, manifest, fold["fold"])
        train_count = len(train_ids)
        missing_count = train_count - len(observed_glucose)
        mean = (sum(observed_glucose) + missing_count * 140) / train_count
        variance = (
            sum((value - mean) ** 2 for value in observed_glucose)
            + missing_count * (140 - mean) ** 2
        ) / train_count
        scale = variance ** 0.5

        targets = {sample.sample_id: sample.y for sample in samples}
        for partition, ids in [
            (baseline.train, fold["train_ids"]),
            (baseline.validation, fold["validation_ids"]),
        ]:
            self.assertEqual(partition.sample_ids, tuple(ids))
            np.testing.assert_array_equal(partition.y, [targets[sid] for sid in ids])
            self.assertTrue(np.isfinite(partition.X).all())
        expected = [[(glucose_by_id.get(sid, 140) - mean) / scale, 0, 0]
                    for sid in baseline.train.sample_ids]
        np.testing.assert_allclose(baseline.train.X, expected)
        np.testing.assert_allclose(baseline.validation.X[0], [(140 - mean) / scale, 0, 0])

        for excluded_ids in (fold["validation_ids"], manifest["test_ids"]):
            with self.subTest(excluded_ids=excluded_ids):
                excluded = set(excluded_ids)
                perturbed = [
                    replace(sample, features={"glucose": 100_000, "bmi": 20_000, "age": 5_000})
                    if sample.sample_id in excluded else sample
                    for sample in samples
                ]
                prepared = prepare_fold(perturbed, manifest, fold["fold"])
                for result in [baseline, prepared]:
                    np.testing.assert_allclose(result.preprocessor.medians, [140, 24.9, 30])
                    np.testing.assert_allclose(result.preprocessor.means, [mean, 24.9, 30])
                    np.testing.assert_allclose(result.preprocessor.scales, [scale, 1, 1])
                np.testing.assert_array_equal(prepared.train.X, baseline.train.X)
                if excluded == set(fold["validation_ids"]):
                    expected_validation = [(100_000 - mean) / scale, 20_000 - 24.9, 5_000 - 30]
                    np.testing.assert_allclose(
                        prepared.validation.X, [expected_validation] * len(excluded),
                    )
                else:
                    np.testing.assert_array_equal(prepared.validation.X, baseline.validation.X)
        self.assertEqual({sample.sample_id: sample.features for sample in samples}, originals)

    def test_fold_rejects_feature_missing_throughout_train(self):
        samples, metadata = self.load_pima_fixture()
        manifest = make_manifest(samples, metadata)
        fold = manifest["folds"][0]
        train_ids = set(fold["train_ids"])
        samples = [
            replace(sample, features={**sample.features, "glucose": None})
            if sample.sample_id in train_ids else sample
            for sample in samples
        ]
        with self.assertRaisesRegex(ValueError, "glucose"):
            prepare_fold(samples, manifest, fold["fold"])


if __name__ == "__main__":
    unittest.main()
