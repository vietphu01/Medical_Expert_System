"""Create stratified ID manifests and fit NumPy preprocessing on training rows."""

from dataclasses import dataclass

import numpy as np


N_FOLDS = 5
DEFAULT_SEED = 42


def make_manifest(samples, metadata, *, seed=DEFAULT_SEED):
    """Split binary labels into a 20% holdout and five CV folds on the rest."""
    by_label = {0: [], 1: []}
    seen_ids = set()
    for sample in samples:
        if sample.y not in by_label:
            raise ValueError("expected binary labels")
        if sample.sample_id in seen_ids:
            raise ValueError(f"duplicate sample ID: {sample.sample_id}")
        seen_ids.add(sample.sample_id)
        by_label[sample.y].append(sample.sample_id)

    n = len(seen_ids)
    n_test = (n + 4) // 5  # ceil(n * 0.20)
    # Round the proportional allocation, keeping both classes in holdout and
    # enough training examples per class to populate all validation folds.
    lower = max(1, n_test - (len(by_label[1]) - N_FOLDS))
    upper = min(n_test - 1, len(by_label[0]) - N_FOLDS)
    if lower > upper:
        raise ValueError("need both classes in holdout and all five validation folds")
    target = (2 * n_test * len(by_label[0]) + n) // (2 * n)
    n_test_zero = min(max(target, lower), upper)

    rng = np.random.Generator(np.random.PCG64(seed))
    holdout = []
    validation = [[] for _ in range(N_FOLDS)]
    offset = 0
    for label, size in ((0, n_test_zero), (1, n_test - n_test_zero)):
        ids = sorted(by_label[label])
        rng.shuffle(ids)
        holdout.extend(ids[:size])
        for i, sample_id in enumerate(ids[size:]):
            validation[(offset + i) % N_FOLDS].append(sample_id)
        offset += len(ids) - size

    train_ids = sorted(sample_id for fold in validation for sample_id in fold)
    folds = []
    for number, ids in enumerate(validation, 1):
        val_ids = set(ids)
        folds.append({
            "fold": number,
            "train_ids": [sample_id for sample_id in train_ids if sample_id not in val_ids],
            "validation_ids": sorted(ids),
        })
    return {
        "dataset": metadata["dataset"],
        "source_sha256": metadata["source"]["sha256"],
        "feature_order": metadata["feature_order"].copy(),
        "seed": seed,
        "train_ids": train_ids,
        "test_ids": sorted(holdout),
        "folds": folds,
    }


def _feature_matrix(samples, feature_order):
    # None (missing in the loader) becomes NaN in the ML-only matrix.
    return np.array(
        [[sample.features[name] for name in feature_order] for sample in samples],
        dtype=np.float64,
    ).reshape(len(samples), len(feature_order))


@dataclass(frozen=True)
class Preprocessor:
    feature_order: tuple[str, ...]
    medians: np.ndarray
    means: np.ndarray
    scales: np.ndarray

    def transform(self, samples):
        X = _feature_matrix(samples, self.feature_order)
        filled = np.where(np.isnan(X), self.medians, X)
        return (filled - self.means) / self.scales


def fit_preprocessor(train_samples, feature_order):
    """Learn median imputation and population standardization from train only."""
    feature_order = tuple(feature_order)
    if not train_samples or not feature_order:
        raise ValueError("need training samples and features to fit the preprocessor")
    X = _feature_matrix(train_samples, feature_order)
    missing = np.isnan(X)
    empty = [name for name, flag in zip(feature_order, missing.all(axis=0)) if flag]
    if empty:
        raise ValueError(f"all training values are missing for: {', '.join(empty)}")
    medians = np.nanmedian(X, axis=0)
    filled = np.where(missing, medians, X)
    means = filled.mean(axis=0)
    scales = filled.std(axis=0, ddof=0)
    # Check constant values directly: std can round above zero for a
    # constant non-integer column when the sum used for its mean rounds.
    constant = (filled == filled[0]).all(axis=0)
    means[constant] = filled[0, constant]
    scales[constant | (scales == 0)] = 1
    return Preprocessor(feature_order, medians, means, scales)


@dataclass(frozen=True)
class PreparedPartition:
    sample_ids: tuple[str, ...]
    X: np.ndarray
    y: np.ndarray


@dataclass(frozen=True)
class PreparedFold:
    train: PreparedPartition
    validation: PreparedPartition
    preprocessor: Preprocessor


def prepare_fold(samples, manifest, fold):
    """Apply the same training-fitted transform to both parts of one CV fold."""
    spec = next((spec for spec in manifest["folds"] if spec["fold"] == fold), None)
    if spec is None:
        raise ValueError(f"unknown fold: {fold}")
    train_ids = set(spec["train_ids"])
    val_ids = set(spec["validation_ids"])
    if (train_ids & val_ids or (train_ids | val_ids) & set(manifest["test_ids"])
            or train_ids | val_ids != set(manifest["train_ids"])
            or len(train_ids) != len(spec["train_ids"])
            or len(val_ids) != len(spec["validation_ids"])):
        raise ValueError("fold must partition training IDs without overlap or holdout IDs")
    by_id = {sample.sample_id: sample for sample in samples}
    train = [by_id[sample_id] for sample_id in spec["train_ids"]]
    val = [by_id[sample_id] for sample_id in spec["validation_ids"]]
    preprocessor = fit_preprocessor(train, manifest["feature_order"])

    def transform(rows):
        return PreparedPartition(
            tuple(row.sample_id for row in rows),
            preprocessor.transform(rows),
            np.array([row.y for row in rows], dtype=np.int64),
        )

    return PreparedFold(transform(train), transform(val), preprocessor)
