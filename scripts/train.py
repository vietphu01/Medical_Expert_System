"""Train and compare the handwritten models using only CV development data."""

import argparse
import csv
import json
import shutil
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from medical_expert.data.pipeline import DEFAULT_SEED, fit_preprocessor, prepare_fold
from medical_expert.data.registry import DATASETS
from medical_expert.ml.metrics import aggregate_metrics, binary_metrics
from medical_expert.ml.runtime import CONFIG, NAMES, model_state, new_model


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = "t06-cv-seed42"
SOURCE_FILES = {
    "cleveland": "processed.cleveland.data",
    "pima": "diabetes.arff",
    "ilpd": "Indian Liver Patient Dataset (ILPD).csv",
    "ckd": "data.csv",
}
METRIC_FIELDS = ("dataset", "experiment", "variant", "split", "subset", "n", "metric", "value", "std")
PREDICTION_FIELDS = ("dataset", "sample_id", "split", "experiment", "variant", "y_true", "y_pred", "score", "covered")
COUNT_METRICS = {"tn", "fp", "fn", "tp"}
THRESHOLD = 0.5


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def manifests():
    return (
        read_json(ROOT / "manifests/t04_split_manifest.json")
        | read_json(ROOT / "manifests/t05_split_manifest.json")
    )


def load_source(dataset, path, manifest):
    rows, metadata = DATASETS[dataset][0](path)
    if not metadata["source"]["matches_verified_release"]:
        raise ValueError(f"{dataset}: source SHA-256 differs from the verified release")
    if (metadata["source"]["sha256"] != manifest["source_sha256"]
            or metadata["feature_order"] != manifest["feature_order"]):
        raise ValueError(f"{dataset}: manifest does not match source and feature schema")
    ids = [row.sample_id for row in rows]
    train, test = set(manifest["train_ids"]), set(manifest["test_ids"])
    if (len(ids) != len(set(ids)) or train & test or train | test != set(ids)
            or len(train) != len(manifest["train_ids"]) or len(test) != len(manifest["test_ids"])):
        raise ValueError(f"{dataset}: manifest IDs do not partition the source")
    folds = manifest["folds"]
    validation_counts = Counter(sid for fold in folds for sid in fold["validation_ids"])
    if [fold["fold"] for fold in folds] != list(range(1, 6)) or validation_counts != dict.fromkeys(train, 1):
        raise ValueError(f"{dataset}: expected five folds with disjoint validation IDs")
    return rows, metadata


def metric_rows(dataset, variant, split, n, metrics, *, experiment="ml", subset="all"):
    for key, (value, std) in metrics.items():
        yield (dataset, experiment, variant, split, subset, n, key, value, std)


def fit_models(samples, feature_order):
    preprocessor = fit_preprocessor(samples, feature_order)
    X = preprocessor.transform(samples)
    y = np.array([sample.y for sample in samples], dtype=int)
    models = {variant: new_model(variant).fit(X, y) for variant in CONFIG}
    return preprocessor, models


def train_dataset(dataset, train, manifest):
    all_metrics = {variant: [] for variant in CONFIG}
    metric_output, prediction_output, undefined = [], [], {}
    for fold in manifest["folds"]:
        number = fold["fold"]
        parts = prepare_fold(train, manifest, number)
        X, y = parts.train.X, parts.train.y
        validation = parts.validation
        for variant in CONFIG:
            model = new_model(variant).fit(X, y)
            scores = model.predict_proba(validation.X)
            labels = (scores >= THRESHOLD).astype(int)
            metrics, reasons = binary_metrics(validation.y, labels, scores)
            all_metrics[variant].append(metrics)
            fold_split = f"cv_fold_{number}"
            if reasons:
                undefined.setdefault(variant, {})[fold_split] = reasons
            metric_output.extend(metric_rows(
                dataset, variant, fold_split, len(scores),
                {name: (value, None) for name, value in metrics.items()} | {"coverage": (1.0, None)},
            ))
            prediction_output.extend(
                (dataset, sid, "validation", "ml", variant, int(truth), int(label), float(score), 1)
                for sid, truth, label, score in zip(validation.sample_ids, validation.y, labels, scores, strict=True)
            )

    summary = {variant: aggregate_metrics(values) for variant, values in all_metrics.items()}
    selected = max((name for name in CONFIG if name != "majority"), key=lambda name: summary[name]["f1"][0])
    stats = []
    for variant, metrics in summary.items():
        # CV scalar metrics are macro averages across folds. Confusion cells sum
        # the disjoint validation folds to preserve integer out-of-fold counts.
        means = {name: values for name, values in metrics.items() if name not in COUNT_METRICS}
        pooled_counts = {name: (sum(f[name] for f in all_metrics[variant]), None) for name in sorted(COUNT_METRICS)}
        metric_output.extend(metric_rows(
            dataset, variant, "cv", len(train), means | pooled_counts | {"coverage": (1.0, 0.0)},
        ))
        view = {"name": NAMES[variant]}
        for name in ("accuracy", "precision", "recall", "f1", "roc_auc"):
            value = means[name][0]
            view[name] = None if value is None else round(100 * value, 2)
        view["cv_mean"] = view["f1"]
        view["cv_std"] = round(100 * means["f1"][1], 2)
        stats.append(view)

    feature_order = manifest["feature_order"]
    prep, models = fit_models(train, feature_order)
    state = {
        "feature_order": feature_order,
        "selected": selected,
        "preprocessor": {name: getattr(prep, name).tolist() for name in ("medians", "means", "scales")},
        "models": {name: model_state(name, model) for name, model in models.items()},
        "stats": stats,
        "tree_rules": models["tree"].export_rules(feature_order),
    }
    return state, metric_output, prediction_output, undefined


def write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def run_training(source_paths, output, seed):
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    # The committed manifests define this experiment. No alternative split is
    # regenerated in the trainer.
    splits = manifests()
    meta = {
        "run_id": output.name, "trained_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed, "stage": "cv", "model_configs": CONFIG, "threshold": THRESHOLD,
        "preprocessing": "median then population standardization, fitted only on train",
        "select_by": "mean positive-class F1; ties use model configuration order; baseline excluded",
        "cv_aggregation": "mean/std across defined folds; confusion counts summed over validation",
        "datasets": {}, "undefined_metrics": {}, "split_manifest": "split_manifest.json",
    }
    artifact = {"version": 1, "datasets": {}}
    metrics, predictions = [], []
    for dataset, path in source_paths.items():
        split = splits[dataset]
        if split["seed"] != seed:
            raise ValueError(f"{dataset}: seed must match the committed manifest ({split['seed']})")
        rows, source = load_source(dataset, path, split)
        by_id = {row.sample_id: row for row in rows}
        train = [by_id[sid] for sid in split["train_ids"]]
        state, metric_part, prediction_part, undefined = train_dataset(dataset, train, split)
        artifact["datasets"][dataset] = state
        meta["datasets"][dataset] = {
            "source_metadata": source, "n_train": len(train), "n_holdout": len(split["test_ids"]),
            "fold_sizes": [len(fold["validation_ids"]) for fold in split["folds"]],
            "selected": state["selected"],
        }
        meta["undefined_metrics"][dataset] = undefined
        metrics.extend(metric_part)
        predictions.extend(prediction_part)
        print(f"{dataset}: {state['selected']} selected by mean CV F1 ({len(train)} validation predictions/model)")

    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".run-", dir=output.parent))
    try:
        write_json(temp / "metadata.json", meta)
        write_json(temp / "models.json", artifact)
        write_json(temp / "split_manifest.json", {dataset: splits[dataset] for dataset in source_paths})
        write_csv(temp / "metrics.csv", METRIC_FIELDS, metrics)
        write_csv(temp / "predictions.csv", PREDICTION_FIELDS, predictions)
        temp.rename(output)
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("all", *DATASETS), default="all")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--run-id", default=DEFAULT_RUN)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    for name, (_, description) in DATASETS.items():
        parser.add_argument(f"--{name}", type=Path, help=description)
    args = parser.parse_args()
    if args.run_id in {"", ".", ".."} or Path(args.run_id).name != args.run_id:
        parser.error("run ID must be a single directory name")
    names = tuple(DATASETS) if args.dataset == "all" else (args.dataset,)
    paths = {name: getattr(args, name) or args.data_dir / SOURCE_FILES[name] for name in names}
    try:
        run_training(paths, ROOT / "results" / args.run_id, args.seed)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
