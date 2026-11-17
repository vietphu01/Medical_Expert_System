"""Portable JSON state for the NumPy models and their fitted preprocessing."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from data_pipeline import Preprocessor
from dataset_loaders import Sample
from math_ml_from_scratch import (
    DecisionTreeScratch, EnsembleVotingScratch, GaussianNBScratch,
    KNNScratch, LogisticRegressionScratch,
)


CONFIG = {
    "logistic": {"lr": 0.1, "epochs": 300},
    "knn": {"k": 7},
    "gaussian_nb": {},
    "tree": {"max_depth": 4, "min_samples_split": 5, "criterion": "entropy"},
    "ensemble": {"members": ["logistic", "knn", "gaussian_nb", "tree"]},
    "majority": {"tie_label": 0},
}
NAMES = {
    "logistic": "Logistic Regression",
    "knn": "K-Nearest Neighbors",
    "gaussian_nb": "Gaussian Naive Bayes",
    "tree": "Decision Tree (ID3)",
    "ensemble": "Ensemble Voting",
    "majority": "Baseline lớp phổ biến",
}


class Majority:
    def fit(self, X, y):
        self.label = int(np.argmax(np.bincount(y, minlength=2)))
        return self

    def predict_proba(self, X):
        return np.full(len(X), self.label, dtype=float)


def new_model(variant, config=CONFIG):
    options = config[variant]
    if variant == "ensemble":
        return EnsembleVotingScratch([new_model(name, config) for name in options["members"]])
    if variant == "majority":
        return Majority()
    classes = {
        "logistic": LogisticRegressionScratch, "knn": KNNScratch,
        "gaussian_nb": GaussianNBScratch, "tree": DecisionTreeScratch,
    }
    return classes[variant](**options)


def model_state(variant, model):
    if variant == "logistic":
        return {"weights": model.weights.tolist(), "bias": float(model.bias)}
    if variant == "knn":
        return {"k": model.k, "X": model.X_train.tolist(), "y": model.y_train.tolist()}
    if variant == "gaussian_nb":
        return {
            "means": [model.means[i].tolist() for i in (0, 1)],
            "vars": [model.vars[i].tolist() for i in (0, 1)],
            "priors": [model.priors[i] for i in (0, 1)],
        }
    if variant == "tree":
        return {"tree": model.tree}
    if variant == "ensemble":
        return {"members": {
            name: model_state(name, member)
            for name, member in zip(CONFIG["ensemble"]["members"], model.models, strict=True)
        }}
    if variant == "majority":
        return {"label": model.label}
    raise ValueError(f"unknown model variant: {variant}")


def _array(value, shape):
    array = np.asarray(value, dtype=float)
    if array.shape != shape or not np.isfinite(array).all():
        raise ValueError("invalid shape or non-finite model state")
    return array


def _validate_tree(node, width):
    if node["leaf"] is True:
        counts = _array(node["dist"], (2,))
        if (counts < 0).any() or counts.sum() <= 0:
            raise ValueError("invalid tree leaf")
        return
    if (node["leaf"] is not False or type(node["feature"]) is not int
            or not 0 <= node["feature"] < width):
        raise ValueError("invalid tree split")
    _array(node["threshold"], ())
    _validate_tree(node["left"], width)
    _validate_tree(node["right"], width)


def _restore_model(variant, state, width):
    model = new_model(variant)
    if variant == "logistic":
        model.weights = _array(state["weights"], (width,))
        model.bias = float(_array(state["bias"], ()))
    elif variant == "knn":
        size = len(state["y"])
        model.k = state["k"]
        model.X_train = _array(state["X"], (size, width))
        model.y_train = _array(state["y"], (size,))
        if (type(model.k) is not int or not 0 < model.k <= size
                or not np.isin(model.y_train, (0, 1)).all()):
            raise ValueError("invalid KNN state")
    elif variant == "gaussian_nb":
        model.classes = (0, 1)
        model.means = _array(state["means"], (2, width))
        model.vars = _array(state["vars"], (2, width))
        model.priors = _array(state["priors"], (2,))
        if (model.vars <= 0).any() or (model.priors <= 0).any():
            raise ValueError("invalid Gaussian NB state")
    elif variant == "tree":
        _validate_tree(state["tree"], width)
        model.tree = state["tree"]
    elif variant == "ensemble":
        model.models = [
            _restore_model(name, state["members"][name], width)
            for name in CONFIG["ensemble"]["members"]
        ]
    elif variant == "majority":
        model.label = state["label"]
        if model.label not in (0, 1):
            raise ValueError("invalid majority label")
    return model


@dataclass(frozen=True)
class RuntimeModel:
    feature_order: tuple
    variant: str
    preprocessor: Preprocessor
    model: object
    stats: list
    tree_rules: str

    def score(self, values):
        features = {key: values.get(key) for key in self.feature_order}
        X = self.preprocessor.transform([Sample("", features, 0)])
        return float(self.model.predict_proba(X)[0])


def load_run(path):
    state = json.loads((Path(path) / "models.json").read_text(encoding="utf-8"))
    try:
        if state["version"] != 1:
            raise ValueError("unsupported model artifact version")
        result = {}
        for dataset, entry in state["datasets"].items():
            features = tuple(entry["feature_order"])
            width = len(features)
            if not width or len(set(features)) != width or not all(isinstance(f, str) for f in features):
                raise ValueError("invalid model feature order")
            variant = entry["selected"]
            transform = entry["preprocessor"]
            scaler = Preprocessor(
                features, _array(transform["medians"], (width,)),
                _array(transform["means"], (width,)), _array(transform["scales"], (width,)),
            )
            if (scaler.scales <= 0).any():
                raise ValueError("invalid scaler")
            estimator = _restore_model(variant, entry["models"][variant], width)
            result[dataset] = RuntimeModel(
                features, variant, scaler, estimator, entry["stats"], entry["tree_rules"],
            )
        return result
    except (AttributeError, KeyError, TypeError, OverflowError, RecursionError) as error:
        raise ValueError("invalid model artifact") from error
