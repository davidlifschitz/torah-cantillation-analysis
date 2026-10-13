"""Require deterministic analytical tables when rebuilding a saved snapshot."""
import argparse
from pathlib import Path

from torah_cantillation.analysis import run
from torah_cantillation.io import read_json, safe_snapshot
from torah_cantillation.parse import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    snapshot = safe_snapshot(args.snapshot)
    before = read_json(args.root / "reports" / snapshot / "summary.json")
    build(args.root, snapshot)
    after = run(args.root, snapshot, permutations=before["permutations"])
    if before["table_sha256"] != after["table_sha256"]:
        raise RuntimeError("Reproduction changed one or more analytical tables")
    print(f"Verified deterministic regeneration of {len(after['table_sha256'])} tables")


if __name__ == "__main__":
    main()
