"""Archive/restore approved primary-edition raw snapshots for offline reproduction."""
import argparse
from pathlib import Path
import zipfile

from torah_cantillation.io import read_json, safe_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["pack", "restore"])
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    snapshot = safe_snapshot(args.snapshot)
    root = args.root.resolve()
    path = root / "data" / "snapshots" / f"{snapshot}.zip"
    manifest_path = root / "data" / "manifests" / f"{snapshot}.json"
    if args.mode == "restore":
        if not path.exists():
            print("No archived snapshot exists; explicit acquisition is required.")
            return
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > 10000 or sum(i.file_size for i in entries) > 600_000_000:
                raise ValueError("Archive exceeds expected limits")
            for item in entries:
                relative = Path(item.filename)
                if relative.is_absolute() or ".." in relative.parts or "\\" in item.filename:
                    raise ValueError("Unsafe archive path")
                allowed = relative.parts[:3] == ("data", "raw", snapshot) or relative == Path(f"data/manifests/{snapshot}.json")
                if not allowed or ((item.external_attr >> 16) & 0o170000) == 0o120000:
                    raise ValueError("Unexpected archive entry")
            archive.extractall(root)
        print(f"Restored {path.name}")
        return
    manifest = read_json(manifest_path)
    if manifest["editions"] != ["tanach"] or not manifest["sources"]:
        raise ValueError("Automatic redistribution is limited to reviewed primary-edition snapshots")
    if any(s.get("license") not in {"Public Domain", "PD"} for s in manifest["sources"]):
        raise ValueError("Source license requires review")
    path.parent.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in (root / "data" / "raw" / snapshot).rglob("*") if p.is_file()) + [manifest_path]
    tmp = path.with_suffix(".tmp.zip")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sources:
            archive.write(source, str(source.relative_to(root)))
    tmp.replace(path)
    print(f"Archived {len(sources)} files in {path}")


if __name__ == "__main__":
    main()
