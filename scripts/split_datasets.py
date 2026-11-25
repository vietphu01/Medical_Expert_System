"""Write the seed-42 holdout and CV manifest for verified dataset releases."""

import argparse
import json
from pathlib import Path

from medical_expert.data.pipeline import make_manifest
from medical_expert.data.registry import DATASETS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for dataset, (_, description) in DATASETS.items():
        parser.add_argument(f"--{dataset}", type=Path, help=description)
    parser.add_argument("--output", type=Path, required=True, help="output manifest JSON")
    args = parser.parse_args()
    if not any(getattr(args, name) is not None for name in DATASETS):
        parser.error("provide at least one dataset")

    manifests = {}
    try:
        for name, (load, _) in DATASETS.items():
            path = getattr(args, name)
            if path is not None:
                samples, metadata = load(path)
                if not metadata["source"]["matches_verified_release"]:
                    parser.error(f"{name}: source SHA-256 does not match the verified release")
                manifests[name] = make_manifest(samples, metadata)
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(manifests, output, indent=2)
            output.write("\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
