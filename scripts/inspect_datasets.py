"""Print reproducible source metadata without exporting individual records."""

import argparse
import json
from pathlib import Path

from medical_expert.data.registry import DATASETS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for dataset, (_, description) in DATASETS.items():
        parser.add_argument(f"--{dataset}", type=Path, help=description)
    args = parser.parse_args()
    if not any(getattr(args, name) is not None for name in DATASETS):
        parser.error("provide at least one dataset")

    metadata = {}
    for dataset, (load, _) in DATASETS.items():
        path = getattr(args, dataset)
        if path is not None:
            try:
                _, metadata[dataset] = load(path)
            except (OSError, ValueError) as error:
                parser.error(str(error))
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
