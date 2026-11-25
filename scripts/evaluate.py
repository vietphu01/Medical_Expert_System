"""Evaluate the predeclared test run after checking the configuration lock."""

import argparse
import shutil
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from medical_expert.ml.metrics import binary_metrics
from medical_expert.ml.runtime import CONFIG, _restore_model, load_run
from scripts.ablation import compare
from scripts.train import (
    METRIC_FIELDS, PREDICTION_FIELDS, ROOT, SOURCE_FILES, THRESHOLD, load_source,
    manifests, metric_rows, read_json, write_csv, write_json,
)


LOCK_PATH = ROOT / "manifests/t10_lock.json"
METHOD_FILES = (
    "medical_expert/data/pipeline.py", "medical_expert/data/loaders.py", "medical_expert/data/registry.py",
    "medical_expert/data/ilpd.py", "medical_expert/data/ckd.py", "medical_expert/ml/metrics.py",
    "medical_expert/ml/algorithms.py", "medical_expert/ml/runtime.py", "medical_expert/expert/fuzzy.py",
    "medical_expert/expert/rules.py", "medical_expert/expert/fusion.py", "scripts/train.py",
    "scripts/ablation.py", "scripts/validate_ablation.py", "scripts/evaluate.py",
    "manifests/t04_split_manifest.json", "manifests/t05_split_manifest.json",
)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def verify_lock(lock, run_id, root=ROOT):
    if (lock["run_id"] != run_id or lock["seed"] != 42
            or lock["threshold"] != THRESHOLD or lock["model_configs"] != CONFIG
            or lock["fuzzy_mode"] != "boolean_membership_gt_0.5"):
        raise ValueError("run ID or configuration does not match the T10 lock")
    current = {name: digest(root / name) for name in METHOD_FILES}
    if current != lock["method_sha256"]:
        mismatched = sorted(k for k in current if current[k] != lock["method_sha256"].get(k))
        raise ValueError("method files differ from the T10 lock: " + ", ".join(mismatched))
    cv_dir = root / "results" / lock["cv_run"]
    validation_dir = root / "results" / lock["validation_run"]
    if {name: digest(cv_dir / name) for name in ("models.json", "split_manifest.json", "predictions.csv")} != lock["cv_sha256"]:
        raise ValueError("T06 model state, manifest or CV predictions differ from the T10 lock")
    if digest(validation_dir / "metadata.json") != lock["validation_metadata_sha256"]:
        raise ValueError("T09 validation evidence differs from the T10 lock")
    return cv_dir


def evaluate(run_id, paths, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"test run already exists: {output}")
    lock = read_json(LOCK_PATH)
    cv_dir = verify_lock(lock, run_id)
    splits = manifests()
    if read_json(cv_dir / "split_manifest.json") != splits:
        raise ValueError("CV manifest and committed manifests differ")
    runtime = load_run(cv_dir)
    artifact = read_json(cv_dir / "models.json")["datasets"]
    if {dataset: model.variant for dataset, model in runtime.items()} != lock["selected"]:
        raise ValueError("model selection differs from the T10 lock")

    metrics, predictions = [], []
    summaries, undefined, sources = {}, {}, {}
    for dataset, split in splits.items():
        if split["source_sha256"] != lock["source_sha256"][dataset]:
            raise ValueError(f"{dataset}: source digest differs from the T10 lock")
        rows, source = load_source(dataset, paths[dataset], split)
        sources[dataset] = source
        by_id = {sample.sample_id: sample for sample in rows}
        test = [by_id[sid] for sid in split["test_ids"]]
        y = [sample.y for sample in test]
        trained = runtime[dataset]
        X = trained.preprocessor.transform(test)
        selected_scores = None
        dataset_undefined = {}
        for variant in CONFIG:
            model = _restore_model(variant, artifact[dataset]["models"][variant], X.shape[1])
            scores = model.predict_proba(X)
            labels = (scores >= THRESHOLD).astype(int)
            values, reasons = binary_metrics(y, labels, scores)
            values["coverage"] = 1.0
            metrics.extend(metric_rows(dataset, variant, "test", len(test),
                                       {name: (value, None) for name, value in values.items()}))
            predictions.extend(
                (dataset, sample.sample_id, "test", "ml", variant, sample.y, int(label), float(score), 1)
                for sample, label, score in zip(test, labels, scores, strict=True)
            )
            if reasons:
                dataset_undefined[variant] = reasons
            if variant == trained.variant:
                selected_scores = scores
        undefined[dataset] = dataset_undefined
        if dataset in ("cleveland", "pima"):
            ab_metrics, ab_predictions, summary = compare(
                dataset, ((s.sample_id, s.y, score, s.features)
                          for s, score in zip(test, selected_scores, strict=True)), split="test",
            )
            metrics.extend(ab_metrics)
            predictions.extend(ab_predictions)
            summaries[dataset] = summary

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".test-", dir=output.parent))
    try:
        write_csv(temporary / "metrics.csv", METRIC_FIELDS, metrics)
        write_csv(temporary / "predictions.csv", PREDICTION_FIELDS, predictions)
        write_json(temporary / "split_manifest.json", splits)
        write_json(temporary / "metadata.json", {
            "run_id": run_id, "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "stage": "test", "seed": lock["seed"], "threshold": lock["threshold"],
            "cv_run": lock["cv_run"], "configuration_lock": lock,
            "trained_at": read_json(cv_dir / "metadata.json")["trained_at"],
            "sources": sources, "split_manifest": "split_manifest.json",
            "split_sizes": {dataset: {"train": len(s["train_ids"]), "test": len(s["test_ids"])}
                            for dataset, s in splits.items()},
            "ablation": summaries, "undefined_ml_metrics": undefined,
        })
        temporary.rename(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    print(f"Test results saved to {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--split", choices=("test",), required=True)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    for name in SOURCE_FILES:
        parser.add_argument(f"--{name}", type=Path)
    args = parser.parse_args()
    if args.run_id in {"", ".", ".."} or Path(args.run_id).name != args.run_id:
        parser.error("run ID must be a single directory name")
    paths = {name: getattr(args, name) or args.data_dir / filename
             for name, filename in SOURCE_FILES.items()}
    try:
        evaluate(args.run_id, paths, ROOT / "results" / args.run_id)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
