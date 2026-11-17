"""Write the seed-42 holdout and CV manifest for the verified T03 releases."""

import argparse
import json
from pathlib import Path

from data_pipeline import make_manifest
from dataset_loaders import load_cleveland, load_pima


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cleveland", type=Path, help="UCI processed.cleveland.data")
    parser.add_argument("--pima", type=Path, help="OpenML #37 diabetes.arff")
    parser.add_argument("--output", type=Path, required=True, help="output manifest JSON")
    args = parser.parse_args()
    if args.cleveland is None and args.pima is None:
        parser.error("provide --cleveland and/or --pima")

    manifests = {}
    try:
        for name, path, load in (
            ("cleveland", args.cleveland, load_cleveland),
            ("pima", args.pima, load_pima),
        ):
            if path is not None:
                samples, metadata = load(path)
                if not metadata["source"]["matches_verified_release"]:
                    parser.error(f"{name}: source SHA-256 does not match the verified T03 release")
                manifests[name] = make_manifest(samples, metadata)
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(manifests, output, indent=2)
            output.write("\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
