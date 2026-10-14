"""Run length-conditioned and chapter-resampled analyses on an approved snapshot."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import platform
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

from torah_cantillation.analysis import sequence_rows
from torah_cantillation.io import canonical, read_json, read_rows, write_json
from torah_cantillation.parse import validate
from torah_cantillation.robustness import (
    chapter_bootstrap_cluster_stability,
    length_conditioned_book_test,
    longer_ngram_tables,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_top_pattern(verses: list[dict], sequences: list[dict], ngrams: dict) -> list[dict]:
    top = next(row for row in ngrams["patterns"]
               if row["representation"] == "token_distinct" and row["n"] == 4)
    target = tuple(top["sequence"])
    verse_by_id = {verse["verse_id"]: verse for verse in verses}
    examples = {}
    for row in sequences:
        if row["representation"] != "token_distinct" or not row["eligible"] or row["book"] in examples:
            continue
        sequence = row["sequence"]
        if any(tuple(sequence[start:start + len(target)]) == target
               for start in range(len(sequence) - len(target) + 1)):
            verse = verse_by_id[row["verse_id"]]
            examples[row["book"]] = {
                "book": row["book"],
                "reference": row["reference"],
                "raw_hebrew": verse["raw_hebrew"],
                "sequence": list(target),
                "inspection_scope": "literal source string from the approved public-domain-labeled primary edition",
            }
    return [examples[book] for book in sorted(examples)]


def build_findings(summary: dict, long_ngrams: dict, conditioned: list[dict],
                   cluster_stability: dict, examples: list[dict]) -> str:
    lines = [
        "# Follow-up robustness findings",
        "",
        f"Analysis: {summary['analysis_id']}",
        f"Source snapshot: {summary['source_snapshot']} ({summary['source_edition']})",
        f"Analysis code commit: {summary['analysis_code_commit']}",
        "",
        "This report reuses the named primary snapshot and writes a separate analysis directory. It does not fetch or modify source text.",
        "The counts are encoded Unicode marks. Token-distinct units remain a sensitivity representation, not a verified functional accent parser.",
        "",
        "## Longer within-verse sequences",
        "",
        "Four- and five-mark sequences are counted within eligible verses; windows never cross a verse boundary. Occurrences can overlap. The support screen is at least 20 occurrences in at least 10 distinct verses; all observed sequences remain in the gzip-compressed UTF-8 JSON table tables/long_ngrams.json.gz.",
        "",
    ]
    for row in long_ngrams["summaries"]:
        lines.append(
            f"- {row['representation']}, n={row['n']}: {row['distinct_patterns']:,} observed patterns across "
            f"{row['within_verse_windows']:,} windows; {row['patterns_at_least_threshold']:,} meet the stated support screen."
        )
    top = next(row for row in long_ngrams["patterns"]
               if row["representation"] == "token_distinct" and row["n"] == 4)
    code_string = " ".join(top["sequence"])
    names = "; ".join(top["unicode_names"])
    lines += [
        "",
        "### Inspected frequent four-mark sequence",
        "",
        f"The most frequent token-distinct four-mark sequence is {code_string} ({names}): "
        f"{top['occurrences']:,} overlapping occurrences in {top['distinct_verse_support']:,} distinct eligible verses "
        f"across {top['book_support']} books. This is an encoded-pattern count, not a functional or musical unit.",
        "",
        "Representative raw source verses were inspected across the five books:",
        "",
    ]
    for example in examples:
        lines.append(f"- {example['reference']}: {example['raw_hebrew']}")
    lines += [
        "",
        "The examples show the mark sequence in different verse contexts. Their recurrence alone does not establish a shared phrase, syntax, genre, or historical explanation.",
        "",
        "## Book profiles after exact verse-length conditioning",
        "",
        "Each eligible verse contributes an equally weighted accent-proportion vector. For each representation, the vector is centered against the mean for verses with the exact same lexical-token count. Token-count strata represented by only one book are excluded. The test statistic is a multivariate pseudo-F; book labels are permuted within exact token-count strata.",
        "",
    ]
    for row in conditioned:
        test = row["length_conditioned"]
        raw = row["unadjusted"]
        lines.append(
            f"- {row['representation']}: {row['comparable_verses']:,} verses in "
            f"{row['comparable_exact_token_count_strata']} comparable token-count strata; unadjusted R²="
            f"{raw['r_squared']:.5f}, exact-length residual R²={test['r_squared']:.5f}, "
            f"pseudo-F={test['pseudo_f']:.3f}, restricted-permutation p={test['permutation_p_exploratory']:.4g} "
            f"(Bonferroni across two representations={test['permutation_p_bonferroni_two_representations']:.4g}; "
            f"{row['permutations']} permutations)."
        )
    lines += [
        "",
        "This is a descriptive association within one complete digital edition. The verse-level permutation assumes exchangeability within exact lengths and does not model dependence among neighboring verses in a chapter. The p-value is exploratory; it does not support genre, authorship, causation, or historical claims. See tables/length_conditioned_books.json for per-codepoint offsets and exact references at the largest verse-level deviations.",
        "",
        "## Chapter-resampled clustering stability",
        "",
    ]
    if cluster_stability.get("status") == "computed":
        lines.append(
            f"With k fixed at {cluster_stability['clusters']} (the published silhouette-selected value), "
            f"{cluster_stability['successful_fits']} chapter bootstrap fits gave a median adjusted Rand index of "
            f"{cluster_stability['ari_median']:.3f} against the full-snapshot partition "
            f"(5th–95th percentiles {cluster_stability['ari_05_percentile']:.3f}–{cluster_stability['ari_95_percentile']:.3f})."
        )
        lines.append(
            "The bootstrap resamples chapters with replacement within each book and retains all eligible verses in each sampled chapter. This measures sensitivity to chapter composition while holding k fixed; it does not validate clusters as linguistic or literary classes."
        )
    else:
        lines.append(f"Cluster stability was not computed: {cluster_stability.get('reason', 'unavailable')}.")
    lines += [
        "",
        "## Reproduction and scope",
        "",
        f"The primary snapshot has {summary['coverage']['verses']:,} validated verses across "
        f"{summary['coverage']['chapters']} chapters, with {summary['coverage']['missing_verses']} missing verses. "
        f"There are {summary['coverage']['sequence_eligible_verses']:,} sequence-eligible and "
        f"{summary['coverage']['sequence_excluded_verses']:,} sequence-excluded verses. Quality-flag counts may overlap: "
        + "; ".join(f"{row['flag']}={row['verse_count']:,}" for row in summary["coverage"]["quality_flags"])
        + ". Sequence-exclusion blockers also overlap: "
        + "; ".join(f"{row['reason']}={row['verse_count']:,}" for row in summary["coverage"]["sequence_exclusion_reasons"])
        + ".",
        f"The source acquisition window was {summary['acquisition']['first_response_at']} to "
        f"{summary['acquisition']['last_response_at']} across {summary['acquisition']['response_count']} requests. "
        f"The corpus verse-data SHA-256 is {summary['corpus_verse_data_sha256']}; the source-manifest SHA-256 is "
        f"{summary['source_manifest_sha256']}; the archived response ZIP SHA-256 is {summary['source_archive_sha256']}.",
        "",
        "Run from the repository root after restoring the approved archive:",
        "",
        "```bash",
        f"uv run python scripts/snapshot_archive.py restore --snapshot {summary['source_snapshot']}",
        f"uv run python scripts/extended_robustness.py --source-snapshot {summary['source_snapshot']} --report-id {summary['analysis_id']} --permutations {summary['parameters']['permutations']} --cluster-bootstrap {summary['parameters']['cluster_bootstrap_iterations']}",
        "```",
        "",
        "This analysis reuses the primary public-domain-labeled Tanach with Ta'amei Hamikra snapshot. It does not provide MAM comparison results, resolve linguistic classifications, or establish a live website or final scholarly release.",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--source-snapshot", default="primary-20261013")
    parser.add_argument("--report-id", default="primary-20261013-followup-20261014")
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--cluster-bootstrap", type=int, default=100)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    source_snapshot = args.source_snapshot
    report_id = args.report_id
    audit = validate(root, source_snapshot)
    if not audit["passed"] or audit["pilot"] or not audit["coverage_complete"]:
        raise SystemExit("Follow-up analysis requires a validated full-coverage snapshot")
    source = root / "data" / "processed" / source_snapshot
    report = root / "reports" / report_id
    report.mkdir(parents=True, exist_ok=True)
    verses, tokens, marks, units = (
        read_rows(source / f"{name}.jsonl") for name in ("verses", "tokens", "marks", "accent_units")
    )
    sequences = sequence_rows(verses, marks, units)
    long_ngrams = longer_ngram_tables(sequences)
    conditioned = [
        length_conditioned_book_test(verses, sequences, representation,
                                    permutations=args.permutations, seed=42)
        for representation in ("literal", "token_distinct")
    ]
    cluster_stability = chapter_bootstrap_cluster_stability(
        verses, sequences, clusters=2, iterations=args.cluster_bootstrap, seed=42
    )
    examples = inspect_top_pattern(verses, sequences, long_ngrams)
    manifest_path = root / "data" / "manifests" / f"{source_snapshot}.json"
    archive_path = root / "data" / "snapshots" / f"{source_snapshot}.zip"
    manifest = read_json(manifest_path)
    source_summary = read_json(root / "reports" / source_snapshot / "summary.json")
    source_quality_flags = read_json(root / "reports" / source_snapshot / "tables" / "quality_flags.json")
    blockers = {"markup_unresolved", "bracketed_reading_unresolved", "orphan_accent",
                "multiple_distinct_accents_on_token", "nonstandard_sof_pasuq_count", "no_encoded_accents"}
    exclusion_counts = Counter(
        flag for verse in verses for flag in set(verse["flags"]) & blockers
    )
    timestamps = sorted(record["retrieved_at"] for record in manifest["requests"].values())
    source_metadata = next(item for item in manifest["sources"] if item["edition_id"] == "tanach")
    try:
        code_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        code_commit = "unavailable"
    table_values = {
        "long_ngrams": long_ngrams,
        "length_conditioned_books": conditioned,
        "cluster_bootstrap": cluster_stability,
        "inspected_examples": examples,
    }
    for name, value in table_values.items():
        if name == "long_ngrams":
            path = report / "tables" / "long_ngrams.json.gz"
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_bytes(gzip.compress((canonical(value) + "\n").encode("utf-8"), mtime=0))
            temporary.replace(path)
        else:
            write_json(report / "tables" / f"{name}.json", value)
    summary = {
        "analysis_id": report_id,
        "source_snapshot": source_snapshot,
        "source_commit": source_summary.get("source_commit"),
        "analysis_code_commit": code_commit,
        "source_edition": "Tanach with Ta'amei Hamikra",
        "source_license_label": "Public Domain",
        "coverage": {
            "verses": audit["rows"]["verses"],
            "chapters": sum(len(chapters) for chapters in manifest["shapes"].values()),
            "missing_verses": 0 if audit["coverage_complete"] else None,
            "sequence_eligible_verses": audit["sequence_eligible_verses"],
            "sequence_excluded_verses": audit["rows"]["verses"] - audit["sequence_eligible_verses"],
            "quality_flags": [
                {"flag": row["flags"], "verse_count": row["verse_count"]}
                for row in source_quality_flags if row["edition_id"] == "tanach"
            ],
            "sequence_exclusion_reasons": [
                {"reason": reason, "verse_count": exclusion_counts[reason]}
                for reason in sorted(exclusion_counts)
            ],
            "coverage_complete": audit["coverage_complete"],
        },
        "acquisition": {
            "first_response_at": min(timestamps),
            "last_response_at": max(timestamps),
            "response_count": len(timestamps),
        },
        "source_metadata": source_metadata,
        "corpus_verse_data_sha256": manifest["verse_data_sha256"],
        "source_manifest_sha256": sha256(manifest_path),
        "source_archive_sha256": sha256(archive_path),
        "processed_provenance_sha256": sha256(source / "provenance.json"),
        "analysis_source_sha256": {
            str(path.relative_to(root)): sha256(path)
            for path in sorted((root / "src" / "torah_cantillation").glob("*.py"))
        },
        "analysis_script_sha256": sha256(Path(__file__).resolve()),
        "parameters": {
            "permutations": args.permutations,
            "cluster_bootstrap_iterations": args.cluster_bootstrap,
            "seed": 42,
            "long_ngram_lengths": [4, 5],
            "long_ngram_minimum_occurrences": 20,
            "long_ngram_minimum_distinct_verse_support": 10,
        },
        "python": platform.python_version(),
        "unicode_database": unicodedata.unidata_version,
        "table_sha256": {},
    }
    summary["table_sha256"] = {
        path.name: sha256(path) for path in sorted((report / "tables").glob("*")) if path.is_file()
    }
    write_json(report / "summary.json", summary)
    (report / "findings.md").write_text(
        build_findings(summary, long_ngrams, conditioned, cluster_stability, examples), encoding="utf-8"
    )
    print(f"Wrote {report.relative_to(root)}")
    print(f"Validated source: {source_snapshot}; report tables: {len(table_values)}")


if __name__ == "__main__":
    main()
