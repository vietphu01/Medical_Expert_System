"""Print reproducible source metadata without exporting individual records."""

import argparse
import json
from pathlib import Path

from dataset_loaders import load_cleveland, load_pima


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleveland", type=Path, help="UCI processed.cleveland.data")
    parser.add_argument("--pima", type=Path, help="OpenML #37 diabetes.arff")
    args = parser.parse_args()
    if args.cleveland is None and args.pima is None:
        parser.error("provide --cleveland and/or --pima")

    metadata = {}
    for dataset, path, load in (
        ("cleveland", args.cleveland, load_cleveland),
        ("pima", args.pima, load_pima),
    ):
        if path is not None:
            try:
                _, metadata[dataset] = load(path)
            except (OSError, ValueError) as error:
                parser.error(str(error))
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
