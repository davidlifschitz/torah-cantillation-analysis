"""End-to-end synthetic checks. Synthetic output is never published as research."""
from pathlib import Path

import pytest

from torah_cantillation.analysis import run
from torah_cantillation.fetch import BOOKS
from torah_cantillation.io import canonical, digest, read_json, write_json, write_rows
from torah_cantillation.parse import build, validate


def synthetic_snapshot(root: Path):
    rows, shapes, sections = [], {}, {}
    for book_i, book in enumerate(BOOKS):
        shapes[book] = [12]
        sections[book] = [{"name": "Synthetic " + book, "whole_ref": f"{book} 1:1-12"}]
        for v in range(1, 13):
            codes = [0x0591 + (v + book_i + j * j) % 14 for j in range(2 + v % 7)]
            text = " ".join(chr(0x05D0 + (j + book_i + v) % 22) + chr(c) for j, c in enumerate(codes)) + "\u05c3"
            rows.append({"verse_id": f"tanach:{book}:1:{v}", "edition_id": "tanach", "book": book,
                         "chapter": 1, "verse": v, "reference": f"{book} 1:{v}", "raw_hebrew": text,
                         "text_sha256": digest(text), "request_id": "synthetic"})
    path = root / "data" / "raw" / "synthetic" / "verses.jsonl"
    write_rows(path, rows)
    manifest = {"schema_version": 1, "snapshot": "synthetic", "editions": ["tanach"],
                "pilot": True, "coverage_complete": False, "shapes": shapes, "sections": sections,
                "sources": [], "requests": {}, "verse_count": len(rows),
                "verse_data_sha256": digest("\n".join(canonical(r) for r in rows) + "\n")}
    write_json(root / "data" / "manifests" / "synthetic.json", manifest)
    return path


def test_build_validate_and_reconcile(tmp_path):
    synthetic_snapshot(tmp_path)
    audit = build(tmp_path, "synthetic")
    assert audit["passed"] and audit["pilot"]
    assert not audit["coverage_complete"]
    assert audit["rows"]["verses"] == 60
    assert validate(tmp_path, "synthetic") == audit


def test_tampered_processed_table_rejected(tmp_path):
    synthetic_snapshot(tmp_path)
    build(tmp_path, "synthetic")
    path = tmp_path / "data/processed/synthetic/marks.jsonl"
    path.write_text(path.read_text() + "{}\n")
    with pytest.raises(ValueError, match="checksum"):
        validate(tmp_path, "synthetic")


def test_tampered_raw_rejected(tmp_path):
    raw = synthetic_snapshot(tmp_path)
    raw.write_text(raw.read_text() + "{}\n")
    with pytest.raises(ValueError, match="checksum"):
        build(tmp_path, "synthetic")


def test_full_analysis_and_determinism(tmp_path):
    synthetic_snapshot(tmp_path)
    build(tmp_path, "synthetic")
    result = run(tmp_path, "synthetic", permutations=3)
    assert result["pilot"] and result["results"][0]["verses"] == 60
    target = tmp_path / "reports/synthetic"
    assert (target / "index.html").exists()
    assert (target / "figures/tanach-inventory.png").exists()
    assert read_json(target / "tables/edition_comparison.json")[0]["status"] == "not_run"
    assert len(read_json(target / "tables/model_evaluation.json")) == 15
    old = result["table_sha256"]
    assert run(tmp_path, "synthetic", permutations=3)["table_sha256"] == old
