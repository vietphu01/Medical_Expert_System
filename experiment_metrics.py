"""Compute binary classification metrics for NumPy experiments."""

from itertools import groupby
from math import sqrt
from statistics import fmean

import numpy as np


def _roc_auc(y_true, scores, positives, negatives):
    """Count positive-negative pairs ranked correctly, with half credit for ties."""
    negatives_below = 0
    agreements = 0.0
    for _, rows in groupby(sorted(zip(scores, y_true)), key=lambda row: row[0]):
        labels = [label for _, label in rows]
        positives_here = labels.count(1)
        negatives_here = len(labels) - positives_here
        agreements += positives_here * (negatives_below + 0.5 * negatives_here)
        negatives_below += negatives_here
    return agreements / (positives * negatives)


def binary_metrics(y_true, y_pred, scores):
    """Return class-1 metrics and an explanation for each undefined result."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    scores = np.asarray(scores, dtype=float)
    if y_true.ndim != 1 or y_pred.shape != y_true.shape or scores.shape != y_true.shape:
        raise ValueError("labels, predictions and scores must be equally sized 1D arrays")
    if not np.isin(y_true, [0, 1]).all() or not np.isin(y_pred, [0, 1]).all():
        raise ValueError("labels and predictions must be binary")
    if not np.isfinite(scores).all():
        raise ValueError("scores must be finite")

    positive = y_true == 1
    predicted_positive = y_pred == 1
    tp = int(np.count_nonzero(positive & predicted_positive))
    tn = int(np.count_nonzero(~positive & ~predicted_positive))
    fp = int(np.count_nonzero(~positive & predicted_positive))
    fn = int(np.count_nonzero(positive & ~predicted_positive))
    actual_positives = tp + fn
    actual_negatives = tn + fp

    metrics = {}
    undefined = {}
    ratios = {
        "accuracy": (tp + tn, len(y_true), "no samples"),
        "precision": (tp, tp + fp, "no predicted positives"),
        "recall": (tp, actual_positives, "no actual positives"),
        "f1": (2 * tp, 2 * tp + fp + fn, "no actual or predicted positives"),
    }
    for name, (numerator, denominator, reason) in ratios.items():
        if denominator:
            metrics[name] = numerator / denominator
        else:
            metrics[name] = None
            undefined[name] = reason

    if actual_positives and actual_negatives:
        metrics["roc_auc"] = _roc_auc(y_true, scores, actual_positives, actual_negatives)
    else:
        metrics["roc_auc"] = None
        undefined["roc_auc"] = "requires actual positives and negatives"
    metrics.update(tn=tn, fp=fp, fn=fn, tp=tp)
    return metrics, undefined


def aggregate_metrics(folds):
    """Return (mean, population standard deviation) across defined fold values."""
    values_by_metric = {}
    for metrics in folds:
        for name, value in metrics.items():
            values = values_by_metric.setdefault(name, [])
            if value is not None:
                values.append(value)

    summary = {}
    for name, values in values_by_metric.items():
        if values:
            mean = fmean(values)
            std = sqrt(fmean((value - mean) ** 2 for value in values))
            summary[name] = mean, std
        else:
            summary[name] = None, None
    return summary
