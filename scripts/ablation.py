"""Compare ML and rule support on a caller-supplied set of predictions."""

from collections import Counter
from statistics import fmean

from experiment_metrics import binary_metrics
from fusion import fusion_scores
from research_rules import evaluate_rules
from scripts.train import THRESHOLD, metric_rows


VARIANTS = ("ml", "rule", "combined_new", "combined_old")
SUBSET_VARIANTS = {
    "all": ("ml", "combined_new", "combined_old"),
    "covered": VARIANTS,
}


def compare(dataset, observations, *, split):
    """Return metric tuples, prediction tuples and a JSON-compatible summary.

    Each observation is (sample_id, true label, ML score, raw features).
    The caller aligns predictions with the designated split before comparison.
    """
    predictions = []
    by_subset = {
        subset: {variant: [] for variant in variants}
        for subset, variants in SUBSET_VARIANTS.items()
    }
    seen = set()
    covered_labels = Counter()
    deltas = []
    label_changes = 0
    for sample_id, y_true, ml_score, raw_features in observations:
        if sample_id in seen:
            raise ValueError(f"{dataset}: duplicate sample ID {sample_id}")
        if y_true not in (0, 1):
            raise ValueError(f"{dataset}: nonbinary label for {sample_id}")
        seen.add(sample_id)
        y_true = int(y_true)
        _, fired = evaluate_rules(dataset, raw_features)
        scores = fusion_scores(float(ml_score), [rule["cf"] for rule in fired if rule["target"] == dataset])
        covered = scores["rule"] is not None
        if covered:
            covered_labels[y_true] += 1

        labels = {variant: None if scores[variant] is None else int(scores[variant] >= THRESHOLD)
                  for variant in VARIANTS}
        deltas.append(scores["combined_new"] - scores["combined_old"])
        label_changes += labels["combined_new"] != labels["combined_old"]
        for variant in VARIANTS:
            score, label = scores[variant], labels[variant]
            predictions.append(
                (dataset, sample_id, split, "ablation", variant, y_true, label, score, int(covered))
            )
            outcome = (y_true, label, score)
            if variant in by_subset["all"]:
                by_subset["all"][variant].append(outcome)
            if covered:
                by_subset["covered"][variant].append(outcome)

    n = len(seen)
    n_covered = sum(covered_labels.values())
    coverage = n_covered / n if n else None
    metrics, undefined = [], {}
    for subset, variants in by_subset.items():
        subset_coverage = coverage if subset == "all" else (1.0 if n_covered else None)
        for variant, outcomes in variants.items():
            truth, labels, scores = zip(*outcomes) if outcomes else ((), (), ())
            values, reasons = binary_metrics(truth, labels, scores)
            values["coverage"] = subset_coverage
            if subset_coverage is None:
                reasons["coverage"] = "no samples"
            if reasons:
                undefined.setdefault(subset, {})[variant] = reasons
            metrics.extend(metric_rows(
                dataset, variant, split, len(outcomes), {key: (value, None) for key, value in values.items()},
                experiment="ablation", subset=subset,
            ))

    summary = {
        "n": n,
        "n_covered": n_covered,
        "coverage": coverage,
        "covered_label_counts": {str(label): covered_labels[label] for label in (0, 1)},
        "old_new": {
            "mean_new_minus_old": fmean(deltas) if deltas else None,
            "max_abs_delta": max(map(abs, deltas), default=None),
            "n_label_changes": label_changes,
        },
        "undefined_metrics": undefined,
    }
    return metrics, predictions, summary
