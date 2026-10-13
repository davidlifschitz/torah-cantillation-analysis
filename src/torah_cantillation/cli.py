"""Command-line interface. Fetching is always explicit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .fetch import EDITIONS, acquire
from .parse import build, validate


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("sources", help="Print exact supported edition selectors")
    for name in ("fetch", "build", "validate", "analyze", "reproduce"):
        command = subs.add_parser(name)
        command.add_argument("--snapshot", required=True)
        if name == "fetch":
            command.add_argument("--comparison", action="store_true", help="Also acquire MAM; see DATA_LICENSES.md")
            command.add_argument("--pilot", action="store_true", help="Chapter 1 in each book only; never label full corpus")
            command.add_argument("--offline", action="store_true")
        if name in {"analyze", "reproduce"}:
            command.add_argument("--permutations", type=int, default=99)
        if name in {"build", "reproduce"}:
            command.add_argument("--parquet", action="store_true", help="Requires the parquet extra")
    args = parser.parse_args(argv)
    if args.command == "sources":
        result = EDITIONS
    elif args.command == "fetch":
        result = acquire(args.root, args.snapshot, editions=("tanach", "mam") if args.comparison else ("tanach",),
                         offline=args.offline, pilot=args.pilot)
        result = {k: result[k] for k in ("snapshot", "verse_count", "pilot", "coverage_complete", "editions")}
    elif args.command == "build":
        result = build(args.root, args.snapshot, parquet=args.parquet)
    elif args.command == "validate":
        result = validate(args.root, args.snapshot)
    else:
        from .analysis import run
        if args.command == "reproduce":
            build(args.root, args.snapshot, parquet=args.parquet)
        result = run(args.root, args.snapshot, permutations=args.permutations)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
