"""Load the UCI #336 published CSV without imputing measurements."""

import csv

from medical_expert.data.loaders import _load

CKD_COLUMNS = (
    "age", "bp", "sg", "al", "su", "rbc", "pc", "pcc", "ba", "bgr",
    "bu", "sc", "sod", "pot", "hemo", "pcv", "wbcc", "rbcc", "htn",
    "dm", "cad", "appet", "pe", "ane", "class",
)
CKD_NOMINAL = {
    "rbc": ("normal", "abnormal"), "pc": ("normal", "abnormal"),
    "pcc": ("present", "notpresent"), "ba": ("present", "notpresent"),
    "htn": ("yes", "no"), "dm": ("yes", "no"), "cad": ("yes", "no"),
    "appet": ("good", "poor"), "pe": ("yes", "no"), "ane": ("yes", "no"),
}
CKD_NUMERIC_CATEGORIES = {
    "sg": (1.005, 1.010, 1.015, 1.020, 1.025),
    "al": range(6),
    "su": range(6),
}
CKD_SOURCE = {
    "record_url": "https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease",
    "metadata_url": "https://archive.ics.uci.edu/api/dataset?id=336",
    "doi": "10.24432/C5G020",
    "release": "UCI Chronic Kidney Disease #336, created 2015, metadata updated 2024-03-04",
    "download_url": "https://archive.ics.uci.edu/static/public/336/data.csv",
    "license": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "terms_status": "verified",
    "verified_sha256": "0eeea8d17f5ad8792d854999d6ddf1602ec4e116616f6ccdfdaef0ba8109e694",
    "bp_measurement": "blood pressure; systolic versus diastolic not specified by UCI",
}


def _csv_header(lines):
    try:
        line_number, line = next(lines)
        header = next(csv.reader([line], strict=True))
    except (StopIteration, csv.Error) as error:
        raise ValueError("CKD header: expected 25 columns") from error
    if tuple(field.strip() for field in header) != CKD_COLUMNS:
        raise ValueError(f"CKD header, line {line_number}: unexpected columns or order")
    return lines


def load_ckd(path):
    """Read UCI's published data.csv; preserve source missing values as None."""
    return _load(
        path, "ckd", CKD_COLUMNS,
        {"sc": "creatinine", "bp": "bp", "age": "age"},
        {"ckd": 1, "notckd": 0},
        units={"creatinine": "mg/dL", "bp": "mmHg", "age": "years"},
        header_parser=_csv_header,
        numeric_columns=set(CKD_COLUMNS[:-1]) - set(CKD_NOMINAL),
        nominal_values={**CKD_NOMINAL, **CKD_NUMERIC_CATEGORIES},
        missing_tokens=("", "?", "NaN"),
        source_info=CKD_SOURCE,
    )
