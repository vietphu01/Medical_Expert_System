"""Load the pinned Cleveland and Pima source formats without imputing features."""

import csv
import re
from dataclasses import dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path


CLEVELAND_COLUMNS = (
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
    "exang", "oldpeak", "slope", "ca", "thal", "num",
)
PIMA_COLUMNS = ("preg", "plas", "pres", "skin", "insu", "mass", "pedi", "age", "class")
PIMA_LABELS = {"tested_negative": 0, "tested_positive": 1}

SOURCES = {
    "cleveland": {
        "record_url": "https://archive.ics.uci.edu/dataset/45/heart+disease",
        "doi": "10.24432/C52P4X",
        "release": "UCI Heart Disease #45, processed Cleveland subset (citation year 1989)",
        "download_url": "https://archive.ics.uci.edu/static/public/45/heart+disease.zip",
        "archive_member": "processed.cleveland.data",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "terms_status": "verified",
        "verified_sha256": "a74b7efa387bc9d108d7d0115d831fe9b414b29ae7124f331b622b4efa0427c8",
    },
    "pima": {
        "record_url": "https://www.openml.org/d/37",
        "metadata_url": "https://www.openml.org/api/v1/json/data/37",
        "release": "OpenML diabetes #37, version 1 (2014-04-06)",
        "download_url": "https://openml.org/data/v1/download/37/diabetes.arff",
        "license": "Public (OpenML metadata label)",
        "terms_url": "https://docs.openml.org/intro/terms/",
        "terms_status": "upstream rights unverified",
        "terms_reference": "https://cran.r-project.org/web/packages/mlbench/refman/mlbench.html#SynthDiabetes",
        "verified_sha256": "4eddd5b2b64679e8888348e306520a393d6a28e1ddc9643cfb76fc5d912d6d40",
    },
}


@dataclass(frozen=True)
class Sample:
    sample_id: str
    features: dict[str, int | float | None]
    y: int


def load_cleveland(path):
    """Load processed.cleveland.data and return samples plus source metadata."""
    return _load(
        path, "cleveland", CLEVELAND_COLUMNS,
        {"age": "age", "trestbps": "bp", "chol": "chol"},
        {"0": 0, "1": 1, "2": 1, "3": 1, "4": 1},
        units={"age": "years", "bp": "mmHg", "chol": "mg/dL"},
    )


def load_pima(path):
    """Load the dense ARFF distributed as OpenML diabetes #37 version 1."""
    return _load(
        path, "pima", PIMA_COLUMNS,
        {"plas": "glucose", "mass": "bmi", "age": "age"},
        PIMA_LABELS, units={"glucose": None, "bmi": "kg/m²", "age": "years"},
        zero_sentinels=("plas", "mass"),
    )


def _pima_data_section(lines):
    header = []
    for _, text in lines:
        if text.lower() == "@data":
            break
        header.append(text)
    else:
        raise ValueError("Pima header: expected @data")

    relation = r"""@relation\s+(?:pima_diabetes|'pima_diabetes'|"pima_diabetes")"""
    if len(header) != len(PIMA_COLUMNS) + 1 or not re.fullmatch(relation, header[0], re.I):
        raise ValueError("Pima header: expected pima_diabetes and nine attributes")

    for column, declaration in zip(PIMA_COLUMNS, header[1:]):
        attribute = rf"""@attribute\s+(?:{column}|'{column}'|"{column}")\s+"""
        declared_type = (
            r"\{\s*tested_negative\s*,\s*tested_positive\s*\}" if column == "class" else "real"
        )
        if not re.fullmatch(attribute + declared_type, declaration, re.I):
            raise ValueError(f"Pima header: unexpected attribute declaration for {column}")

    return lines


def _parse_number(token, column, location):
    if token in ("", "?"):
        return None
    try:
        number = float(token)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{location}: {column} must be numeric") from error
    if not isfinite(number):
        raise ValueError(f"{location}: {column} must be finite")
    if column == "age":
        if not number.is_integer():
            raise ValueError(f"{location}: age must be an integer")
        return int(number)
    return number


def _load(path, dataset, columns, feature_columns, label_map, *, units, zero_sentinels=()):
    raw = Path(path).read_bytes()
    content = raw.decode("utf-8-sig")
    lines = (
        (line_number, line.strip())
        for line_number, line in enumerate(content.splitlines(), 1)
        if line.strip() and not (dataset == "pima" and line.lstrip().startswith("%"))
    )
    if dataset == "pima":
        lines = _pima_data_section(lines)

    samples = []
    seen = set()
    source_missing = dict.fromkeys(columns, 0)
    zero_counts = dict.fromkeys(zero_sentinels, 0)
    feature_missing = dict.fromkeys(feature_columns.values(), 0)
    raw_label_counts = dict.fromkeys(label_map, 0)
    label_counts = {"0": 0, "1": 0}
    raw_rows = 0
    for raw_rows, (line_number, line) in enumerate(lines, 1):
        location = f"{dataset}, line {line_number}"
        try:
            fields = next(csv.reader([line], strict=True))
        except csv.Error as error:
            raise ValueError(f"{location}: invalid comma-delimited row") from error
        if len(fields) != len(columns):
            raise ValueError(f"{location}: expected {len(columns)} columns, got {len(fields)}")

        raw_label = fields[-1].strip()
        if raw_label not in label_map:
            raise ValueError(f"{location}: invalid label in {columns[-1]}")
        y = label_map[raw_label]
        values = {
            column: _parse_number(token.strip(), column, location)
            for column, token in zip(columns[:-1], fields[:-1])
        }
        raw_label_counts[raw_label] += 1
        for column, value in values.items():
            if value is None:
                source_missing[column] += 1
            elif column in zero_counts and value == 0:
                zero_counts[column] += 1

        # Use all original columns and the original label before projection or zero handling.
        source_row = (*values.values(), raw_label)
        if source_row in seen:
            continue
        seen.add(source_row)

        features = {}
        for column, feature in feature_columns.items():
            value = values[column]
            if column in zero_counts and value == 0:
                value = None
            features[feature] = value
            if value is None:
                feature_missing[feature] += 1
        label_counts[str(y)] += 1
        samples.append(Sample(f"{dataset}:{raw_rows:04d}", features, y))

    if not samples:
        raise ValueError(f"{dataset}: expected at least one data row")

    fingerprint = sha256(raw).hexdigest()
    source = {
        **SOURCES[dataset],
        "sha256": fingerprint,
        "matches_verified_release": fingerprint == SOURCES[dataset]["verified_sha256"],
    }
    metadata = {
        "dataset": dataset,
        "source": source,
        "source_columns": list(columns),
        "feature_order": list(feature_columns.values()),
        "feature_sources": {feature: column for column, feature in feature_columns.items()},
        "feature_units": units,
        "raw_rows": raw_rows,
        "n_samples": len(samples),
        "duplicate_rows": raw_rows - len(samples),
        "raw_label_counts": raw_label_counts,
        "label_counts": label_counts,
        "source_missing_by_column": source_missing,
        "zero_sentinel_by_column": zero_counts,
        "missing_by_feature": feature_missing,
    }
    return samples, metadata
