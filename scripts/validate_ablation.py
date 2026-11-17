"""Run the Cleveland/Pima ablation on T06 out-of-fold scores."""

import argparse
import csv
from hashlib import sha256
from pathlib import Path

from scripts.ablation import compare
from scripts.train import (
    DEFAULT_RUN, METRIC_FIELDS, PREDICTION_FIELDS, ROOT, SOURCE_FILES, load_source,
    manifests, read_json, write_csv, write_json,
)


ABLATION_DATASETS = ("cleveland", "pima")


def validation_scores(path, selected):
    by_dataset = {name: {} for name in selected}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            dataset = row["dataset"]
            if dataset not in selected or row["variant"] != selected[dataset]:
                continue
            sample_id = row["sample_id"]
            if row["split"] != "validation" or row["experiment"] != "ml" or sample_id in by_dataset[dataset]:
                raise ValueError(f"{dataset}: expected one T06 out-of-fold score per train ID")
            by_dataset[dataset][sample_id] = (int(row["y_true"]), float(row["score"]))
    return by_dataset


def validate_ablation(cv_dir, paths, output):
    cv_dir, output = Path(cv_dir), Path(output)
    cv_meta = read_json(cv_dir / "metadata.json")
    if cv_meta["stage"] != "cv" or cv_meta["seed"] != 42:
        raise ValueError("expected a seed-42 T06 CV run")
    splits = manifests()
    cv_splits = read_json(cv_dir / "split_manifest.json")
    selected = {name: cv_meta["datasets"][name]["selected"] for name in ABLATION_DATASETS}
    prediction_file = cv_dir / "predictions.csv"
    scores = validation_scores(prediction_file, selected)
    summaries, metric_out, prediction_out = {}, [], []
    for dataset in ABLATION_DATASETS:
        split = splits[dataset]
        if split != cv_splits.get(dataset) or set(scores[dataset]) != set(split["train_ids"]):
            raise ValueError(f"{dataset}: T06 predictions do not cover exactly the manifest train IDs")
        rows, _ = load_source(dataset, paths[dataset], split)
        by_id = {row.sample_id: row for row in rows}
        observations = []
        for sample_id in split["train_ids"]:
            sample = by_id[sample_id]
            label, score = scores[dataset][sample_id]
            if label != sample.y:
                raise ValueError(f"{dataset}: label mismatch in T06 validation predictions")
            observations.append((sample_id, label, score, sample.features))
        metrics, predictions, summary = compare(dataset, observations, split="validation")
        metric_out.extend(metrics)
        prediction_out.extend(predictions)
        summaries[dataset] = summary

    output.mkdir(parents=True)
    write_csv(output / "metrics.csv", METRIC_FIELDS, metric_out)
    write_csv(output / "predictions.csv", PREDICTION_FIELDS, prediction_out)
    write_json(output / "split_manifest.json", {name: splits[name] for name in ABLATION_DATASETS})
    write_json(output / "metadata.json", {
        "run_id": output.name, "stage": "validation", "seed": 42,
        "cv_run": cv_meta["run_id"], "cv_predictions_sha256": sha256(prediction_file.read_bytes()).hexdigest(),
        "split_manifest": "split_manifest.json", "threshold": 0.5,
        "selected": selected, "datasets": summaries,
        "sources": {name: cv_meta["datasets"][name]["source_metadata"] for name in ABLATION_DATASETS},
    })
    for name, summary in summaries.items():
        print(f"{name}: {summary['n_covered']}/{summary['n']} covered; "
              f"{summary['old_new']['n_label_changes']} label changes")
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cv-run", type=Path, default=ROOT / "results" / DEFAULT_RUN)
    parser.add_argument("--output", type=Path, default=ROOT / "results/t09-validation-seed42")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    for dataset in ABLATION_DATASETS:
        parser.add_argument(f"--{dataset}", type=Path)
    args = parser.parse_args()
    paths = {name: getattr(args, name) or args.data_dir / SOURCE_FILES[name] for name in ABLATION_DATASETS}
    try:
        validate_ablation(args.cv_run, paths, args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
