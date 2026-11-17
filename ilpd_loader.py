"""Load the original headerless UCI Indian Liver Patient Dataset."""

from dataset_loaders import _load


ILPD_COLUMNS = (
    "Age", "Gender", "TB", "DB", "Alkphos", "Sgpt", "Sgot", "TP", "ALB",
    "A/G Ratio", "Selector",
)
ILPD_SOURCE = {
    "record_url": "https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset",
    "metadata_url": "https://archive.ics.uci.edu/api/dataset?id=225",
    "doi": "10.24432/C5D02C",
    "release": "UCI ILPD #225, original CSV (donated 2012-05-20)",
    "download_url": "https://archive.ics.uci.edu/static/public/225/ilpd+indian+liver+patient+dataset.zip",
    "archive_member": "Indian Liver Patient Dataset (ILPD).csv",
    "license": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "terms_status": "verified",
    "verified_sha256": "84feac16488de5cf89bd22bd802c77f25841fe93e9ddd32355683e94d46c3425",
}


def load_ilpd(path):
    """Return samples and metadata for the UCI archive member."""
    return _load(
        path, "ilpd", ILPD_COLUMNS,
        {"TB": "bilirubin", "ALB": "albumin", "Age": "age"},
        {"1": 1, "2": 0},
        units={"bilirubin": None, "albumin": None, "age": "years"},
        numeric_columns=set(ILPD_COLUMNS) - {"Gender", "Selector"},
        nominal_values={"Gender": ("Female", "Male")},
        source_info=ILPD_SOURCE,
    )
