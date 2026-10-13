"""Computed atlas and exploratory models. No fabricated findings or live API calls."""
from __future__ import annotations

import html
import math
import os
import platform
import random
import re
from collections import Counter, defaultdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import pandas as pd

from .io import canonical, digest, read_json, read_rows, safe_snapshot, write_json
from .parse import ACCENTS, validate

SEED = 42


def entropy(values) -> float:
    counts = Counter(values)
    total = sum(counts.values())
    return -sum((n / total) * math.log2(n / total) for n in counts.values()) if total else 0.0


def mutual_information(sequences: list[list[str]]) -> float:
    pairs = Counter((a, b) for seq in sequences for a, b in zip(seq, seq[1:]))
    left, right = Counter(), Counter()
    total = sum(pairs.values())
    for (a, b), count in pairs.items():
        left[a] += count
        right[b] += count
    return sum((count / total) * math.log2(count * total / (left[a] * right[b]))
               for (a, b), count in pairs.items()) if total else 0.0


def sequence_rows(verses: list[dict], marks: list[dict], units: list[dict]) -> list[dict]:
    literal, distinct = defaultdict(list), defaultdict(list)
    for mark in marks:
        if mark["category"] == "accent" and mark["region"] == "text":
            literal[mark["verse_id"]].append(mark["codepoint"])
    for unit in units:
        distinct[unit["verse_id"]].append(unit["codepoint"])
    result = []
    for verse in verses:
        for name, lookup in (("literal", literal), ("token_distinct", distinct)):
            result.append({"verse_id": verse["verse_id"], "edition_id": verse["edition_id"],
                           "reference": verse["reference"], "book": verse["book"],
                           "chapter": verse["chapter"], "representation": name,
                           "eligible": verse["sequence_eligible"],
                           "sequence": lookup[verse["verse_id"]]})
    return result


def ngrams(rows: list[dict], n: int) -> list[dict]:
    counts, examples = Counter(), defaultdict(list)
    for row in rows:
        if not row["eligible"]:
            continue
        seq = row["sequence"]
        for start in range(len(seq) - n + 1):
            key = (row["edition_id"], row["representation"], tuple(seq[start:start + n]))
            counts[key] += 1
            if len(examples[key]) < 5 and row["reference"] not in examples[key]:
                examples[key].append(row["reference"])
    totals = Counter()
    for (edition, representation, seq), count in counts.items():
        totals[(edition, representation, seq[:-1])] += count
    return [{"edition_id": edition, "representation": representation,
             "sequence": list(seq), "n": n, "count": count,
             "conditional_probability": count / totals[(edition, representation, seq[:-1])],
             "example_refs": examples[(edition, representation, seq)]}
            for (edition, representation, seq), count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def transition_null(rows: list[dict], permutations: int) -> list[dict]:
    rng = random.Random(SEED)
    groups = defaultdict(list)
    for row in rows:
        if row["eligible"] and len(row["sequence"]) >= 2:
            groups[(row["edition_id"], row["representation"])].append(row["sequence"])
    results = []
    for (edition, representation), sequences in sorted(groups.items()):
        observed = mutual_information(sequences)
        simulated = []
        for _ in range(permutations):
            shuffled = []
            for seq in sequences:
                value = list(seq)
                rng.shuffle(value)
                shuffled.append(value)
            simulated.append(mutual_information(shuffled))
        results.append({"edition_id": edition, "representation": representation,
                        "observed_mi_bits": observed, "null_mean_mi_bits": float(np.mean(simulated)),
                        "permutations": permutations, "seed": SEED,
                        "permutation_p_exploratory": (1 + sum(v >= observed for v in simulated)) / (permutations + 1),
                        "null": "shuffle within each verse; preserve lengths and mark multiplicities",
                        "eligible_verses": len(sequences), "null_values_bits": simulated})
    for row in results:
        row["p_bonferroni_across_reported_tests"] = min(1.0, row["permutation_p_exploratory"] * len(results))
    return results


def clusters(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import adjusted_rand_score, silhouette_score
    labels, diagnostics = [], []
    alphabet = [f"U+{code:04X}" for code in sorted(ACCENTS)]
    for edition in sorted({r["edition_id"] for r in rows}):
        selected = [r for r in rows if r["edition_id"] == edition and r["representation"] == "token_distinct"
                    and r["eligible"] and r["sequence"]]
        if len(selected) < 30:
            diagnostics.append({"edition_id": edition, "status": "skipped", "reason": "fewer than 30 eligible verses"})
            continue
        counts = [Counter(r["sequence"]) for r in selected]
        x = np.array([[count[c] / sum(count.values()) for c in alphabet] for count in counts])
        unique_count = len(np.unique(x, axis=0))
        if unique_count < 3:
            diagnostics.append({"edition_id": edition, "status": "skipped", "reason": "fewer than 3 distinct profiles"})
            continue
        fits = []
        for k in range(2, min(6, unique_count - 1, len(selected) - 1) + 1):
            fitted = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit_predict(x)
            score = silhouette_score(x, fitted, sample_size=min(1000, len(x)), random_state=SEED)
            alternate = KMeans(n_clusters=k, n_init=10, random_state=SEED + 1).fit_predict(x)
            fits.append((float(score), k, fitted))
            diagnostics.append({"edition_id": edition, "k": k, "silhouette": float(score),
                                "seed_stability_adjusted_rand": float(adjusted_rand_score(fitted, alternate)),
                                "features": "within-verse token-distinct accent proportions", "status": "computed"})
        _, best_k, assignment = max(fits, key=lambda item: item[0])
        projected = PCA(n_components=2, random_state=SEED).fit_transform(x)
        for row, group, xy in zip(selected, assignment, projected):
            labels.append({"edition_id": edition, "reference": row["reference"], "book": row["book"],
                           "cluster": int(group), "selected_k": best_k,
                           "pca_1": float(xy[0]), "pca_2": float(xy[1])})
    return labels, diagnostics


def predictive_models(rows: list[dict], verses: list[dict]) -> tuple[list[dict], list[dict]]:
    """Leave-one-book-out next-accent evaluation; no verse is split across folds."""
    outcomes, surprises = [], []
    text_keys = {v["verse_id"]: re.sub(r"[^\u05d0-\u05ea]", "", v["raw_hebrew"]) for v in verses}
    alphabet = [f"U+{c:04X}" for c in sorted(ACCENTS)]
    size = len(alphabet)
    for edition in sorted({r["edition_id"] for r in rows}):
        selected = [r for r in rows if r["edition_id"] == edition and r["eligible"]
                    and r["representation"] == "token_distinct" and len(r["sequence"]) >= 2]
        books = sorted({r["book"] for r in selected})
        if len(books) < 2:
            outcomes.append({"edition_id": edition, "status": "skipped", "reason": "need at least two books"})
            continue
        for held_out in books:
            test = [r for r in selected if r["book"] == held_out]
            test_texts = {text_keys[r["verse_id"]] for r in test}
            train = [r for r in selected if r["book"] != held_out and text_keys[r["verse_id"]] not in test_texts]
            if not train:
                outcomes.append({"edition_id": edition, "held_out_book": held_out, "status": "skipped", "reason": "no nonduplicate training verses"})
                continue
            uni = Counter(c for r in train for c in r["sequence"])
            bi = Counter((a, b) for r in train for a, b in zip(r["sequence"], r["sequence"][1:]))
            prev = Counter()
            for (a, _), count in bi.items():
                prev[a] += count
            total = sum(uni.values())
            loss = Counter()
            events = 0
            for row in test:
                verse_loss = 0.0
                for a, b in zip(row["sequence"], row["sequence"][1:]):
                    loss["uniform"] += math.log2(size)
                    loss["unigram"] -= math.log2((uni[b] + 1) / (total + size))
                    value = -math.log2((bi[(a, b)] + 1) / (prev[a] + size))
                    loss["bigram"] += value
                    verse_loss += value
                    events += 1
                surprises.append({"edition_id": edition, "reference": row["reference"],
                                  "held_out_book": held_out, "sequence": row["sequence"],
                                  "mean_surprisal_bits": verse_loss / (len(row["sequence"]) - 1),
                                  "transitions": len(row["sequence"]) - 1,
                                  "interpretation": "out-of-book model surprise, not textual error"})
            for model, value in loss.items():
                outcomes.append({"edition_id": edition, "held_out_book": held_out, "model": model,
                                 "mean_log_loss_bits": value / events, "events": events,
                                 "train_verses": len(train), "test_verses": len(test),
                                 "smoothing_alpha": 1, "fixed_alphabet_size": size, "status": "computed"})
    return outcomes, sorted(surprises, key=lambda row: -row["mean_surprisal_bits"])


def edition_comparison(verses: list[dict], sequences: list[dict]) -> list[dict]:
    editions = sorted({v["edition_id"] for v in verses})
    if len(editions) < 2:
        return [{"status": "not_run", "reason": "Only one edition acquired; no edition-robustness claim is justified"}]
    lookup = {(s["verse_id"], s["representation"]): s["sequence"] for s in sequences}
    by_ref = defaultdict(dict)
    for verse in verses:
        by_ref[verse["reference"]][verse["edition_id"]] = verse
    output = []
    for ref, versions in by_ref.items():
        if not all(e in versions for e in editions):
            output.append({"reference": ref, "status": "unaligned_missing_edition"})
            continue
        a, b = (versions[e] for e in editions[:2])
        ca = re.sub(r"[^\u05d0-\u05ea]", "", a["raw_hebrew"])
        cb = re.sub(r"[^\u05d0-\u05ea]", "", b["raw_hebrew"])
        output.append({"reference": ref, "edition_a": a["edition_id"], "edition_b": b["edition_id"],
                       "raw_equal": a["raw_hebrew"] == b["raw_hebrew"], "consonants_equal": ca == cb,
                       "literal_sequence_equal": lookup[(a["verse_id"], "literal")] == lookup[(b["verse_id"], "literal")],
                       "token_distinct_sequence_equal": lookup[(a["verse_id"], "token_distinct")] == lookup[(b["verse_id"], "token_distinct")],
                       "accent_count_delta_b_minus_a": b["accent_count"] - a["accent_count"],
                       "status": "compared"})
    return output


def json_records(frame: pd.DataFrame) -> list[dict]:
    import json
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def run(root: Path, snapshot: str, *, permutations: int = 99) -> dict:
    if permutations < 1:
        raise ValueError("At least one permutation is required")
    snapshot = safe_snapshot(snapshot)
    audit = validate(root, snapshot)
    source = root / "data" / "processed" / snapshot
    verses, tokens, marks, units = (read_rows(source / f"{n}.jsonl")
                                  for n in ("verses", "tokens", "marks", "accent_units"))
    target = root / "reports" / snapshot
    target.mkdir(parents=True, exist_ok=True)
    vdf, mdf = pd.DataFrame(verses), pd.DataFrame(marks)
    meta = vdf[["verse_id", "book", "chapter", "parashah"]]
    accent = mdf[(mdf.category == "accent") & (mdf.region == "text")].merge(meta, on="verse_id", validate="many_to_one")
    if accent.empty:
        raise ValueError("No encoded accents found; refuse to publish an empty accent atlas")
    tables = {}
    tables["inventory"] = accent.groupby(["edition_id", "codepoint", "unicode_name"]).size().rename("count").reset_index()
    tables["all_signs"] = mdf.groupby(["edition_id", "codepoint", "unicode_name", "interpretation", "region"]).size().rename("count").reset_index()
    for level, group in (("books", ["book"]), ("chapters", ["book", "chapter"]), ("parashahs", ["book", "parashah"])):
        by = ["edition_id"] + group
        denominator = vdf.groupby(by).agg(verses=("verse_id", "size"), lexical_tokens=("token_count", "sum")).reset_index()
        counts = accent.groupby(by + ["codepoint"]).size().rename("count").reset_index()
        codes = tables["inventory"][["edition_id", "codepoint"]].drop_duplicates()
        grid = denominator.merge(codes, on="edition_id", validate="many_to_many")
        frame = grid.merge(counts, on=by + ["codepoint"], how="left", validate="one_to_one")
        frame["count"] = frame["count"].fillna(0).astype(int)
        frame["per_1000_lexical_tokens"] = 1000 * frame["count"] / frame["lexical_tokens"]
        tables[level] = frame
    tables["quality_flags"] = vdf.explode("flags").dropna(subset=["flags"]).groupby(["edition_id", "flags"]).size().rename("verse_count").reset_index()
    token_map = {t["token_id"]: t for t in tokens}
    verse_map = {v["verse_id"]: v for v in verses}
    positions = []
    for mark in marks:
        if mark["category"] != "accent" or not mark["token_id"] or mark["region"] != "text":
            continue
        token = token_map[mark["token_id"]]
        verse = verse_map[mark["verse_id"]]
        positions.append({"edition_id": mark["edition_id"], "reference": verse["reference"],
                          "codepoint": mark["codepoint"], "token_position": token["position"],
                          "relative_position": (token["position"] - 1) / max(1, verse["token_count"] - 1),
                          "sequence_eligible": verse["sequence_eligible"]})
    sequences = sequence_rows(verses, marks, units)
    profiles = [{"edition_id": s["edition_id"], "reference": s["reference"],
                 "book": s["book"], "representation": s["representation"], "eligible": s["eligible"],
                 "length": len(s["sequence"]), "entropy_bits": entropy(s["sequence"])} for s in sequences]
    cluster_labels, cluster_diagnostics = clusters(sequences)
    models, anomalies = predictive_models(sequences, verses)
    payloads = {
        **{name: json_records(df) for name, df in tables.items()},
        "audit": audit, "positions": positions, "verse_profiles": profiles,
        "bigrams": ngrams(sequences, 2), "trigrams": ngrams(sequences, 3),
        "transition_null": transition_null(sequences, permutations),
        "clusters": cluster_labels, "cluster_diagnostics": cluster_diagnostics,
        "model_evaluation": models, "anomalies": anomalies,
        "edition_comparison": edition_comparison(verses, sequences),
    }
    inventory = tables["inventory"]
    rare = inventory[inventory["count"] <= 20][["edition_id", "codepoint"]]
    rare_rows = accent.merge(rare, on=["edition_id", "codepoint"], validate="many_to_one")
    rare_rows["reference"] = rare_rows["verse_id"].map({v["verse_id"]: v["reference"] for v in verses})
    payloads["rare_occurrences"] = json_records(rare_rows[["edition_id", "reference", "codepoint", "unicode_name", "char_offset", "mark_id"]])
    for name, value in payloads.items():
        write_json(target / "tables" / f"{name}.json", value)
    per_edition = []
    for edition in audit["edition_ids"]:
        selected = vdf[vdf.edition_id == edition]
        per_edition.append({"edition_id": edition, "verses": len(selected),
                            "lexical_tokens": int(selected.token_count.sum()),
                            "encoded_accent_signs": int(selected.accent_count.sum()),
                            "distinct_accent_codepoints": int((inventory.edition_id == edition).sum()),
                            "sequence_eligible_verses": int(selected.sequence_eligible.sum())})
    packages = {}
    for package in ("pandas", "numpy", "scipy", "scikit-learn", "matplotlib", "httpx", "nbclient"):
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            packages[package] = "not installed"
    summary = {"snapshot": snapshot, "pilot": audit["pilot"], "coverage_complete": audit["coverage_complete"],
               "results": per_edition, "parser": read_json(source / "provenance.json"),
               "python": platform.python_version(), "packages": packages, "seed": SEED,
               "source_commit": os.environ.get("GITHUB_SHA"),
               "source_file_sha256": {str(p.relative_to(root)): digest(p.read_bytes()) for p in sorted((root / "src").rglob("*.py"))},
               "permutations": permutations,
               "scope": "Encoded accents U+0591-U+05AE; all_signs separately audits U+05BD and other signs",
               "interpretation": "Token-distinct units are provisional; no complete linguistic accent parser is claimed",
               "table_sha256": {p.name: digest(p.read_bytes()) for p in sorted((target / "tables").glob("*.json"))}}
    write_json(target / "summary.json", summary)
    write_findings(target, summary, payloads)
    make_figures(target, payloads)
    make_site(target, summary, verses)
    return summary


def write_findings(target: Path, summary: dict, payloads: dict) -> None:
    scope = "PILOT ONLY - not a full-Torah result" if summary["pilot"] else "Full selected reference coverage validated"
    lines = ["# Computed findings", "", f"Snapshot: `{summary['snapshot']}`. **{scope}.**", "",
             summary["scope"], "", "## Corpus inventory", ""]
    for result in summary["results"]:
        lines.append(f"- `{result['edition_id']}`: {result['verses']:,} verses; {result['lexical_tokens']:,} lexical tokens; "
                     f"{result['encoded_accent_signs']:,} encoded accent signs in {result['distinct_accent_codepoints']} code points; "
                     f"{result['sequence_eligible_verses']:,} verses eligible for sequence analysis.")
        top = sorted((r for r in payloads["inventory"] if r["edition_id"] == result["edition_id"]), key=lambda r: -r["count"])[:5]
        lines.append("  Most frequent encoded accents: " + "; ".join(f"{r['unicode_name']} ({r['count']:,})" for r in top) + ".")
    lines += ["", "## Sequential dependence", ""]
    for row in payloads["transition_null"]:
        lines.append(f"- `{row['edition_id']}` / `{row['representation']}`: observed adjacent-mark mutual information "
                     f"{row['observed_mi_bits']:.4f} bits; within-verse shuffle mean {row['null_mean_mi_bits']:.4f} bits; "
                     f"exploratory p={row['permutation_p_exploratory']:.4g}; Bonferroni-adjusted p="
                     f"{row['p_bonferroni_across_reported_tests']:.4g} ({row['permutations']} shuffles).")
    lines += ["", "## Predictability", "", "Leave-one-book-out log losses are in `tables/model_evaluation.json`. "
              "Unigram and bigram baselines use add-one smoothing and a fixed 30-symbol Unicode alphabet. "
              "Repeated consonantal verse texts in held-out books are removed from training.", "",
              "## Interpretation limits", "", "- Counts describe the encoded source snapshot, not every manuscript or chanting tradition.",
              "- Literal inventory includes text in unresolved readings; inspect quality flags before claiming lexical or linguistic counts.",
              "- Repeated signs remain in the literal layer. Token-distinct collapse is a sensitivity representation, not a linguistic truth.",
              "- Markup, bracketed readings, orphan accents, multiple distinct accents on a token, and nonstandard verse endings exclude verses from sequence/model analysis, not the raw audit.",
              "- Clusters and high-surprise verses are exploratory, not inferred genres, textual errors, or historical explanations.",
              "- The shuffle tests one explicit null model. Descriptive counts are a corpus census, not sample estimates.",
              "- Edition comparison is unrun unless two editions were acquired; inspect its status table.",
              "- Silluq candidates are audited separately and excluded from accent-codepoint sequences.", "",
              "## Evidence", "", "All tables are under `tables/`. `summary.json` records provenance, environment versions, code and table checksums. "
              "`rare_occurrences.json` lists every occurrence of an encoded accent with total frequency <=20 in an edition. "
              "The complete occurrence inventory, including common signs, is `data/processed/<snapshot>/marks.jsonl`."]
    (target / "findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_figures(target: Path, payloads: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figures = target / "figures"
    figures.mkdir(exist_ok=True)
    inventory = pd.DataFrame(payloads["inventory"])
    for edition in inventory.edition_id.unique():
        data = inventory[inventory.edition_id == edition].sort_values("count")
        fig, ax = plt.subplots(figsize=(10, 9))
        ax.barh(data.unicode_name.str.replace("HEBREW ACCENT ", "", regex=False), data["count"])
        ax.set(xlabel="Encoded accent signs", title=f"Accent inventory - {edition}")
        fig.tight_layout()
        fig.savefig(figures / f"{edition}-inventory.png", dpi=150)
        plt.close(fig)
        books = pd.DataFrame(payloads["books"])
        pivot = books[books.edition_id == edition].pivot(index="codepoint", columns="book", values="per_1000_lexical_tokens")
        fig, ax = plt.subplots(figsize=(8, 10))
        image = ax.imshow(pivot.values, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=30)
        ax.set_yticks(range(len(pivot.index)), pivot.index)
        ax.set_title(f"Signs per 1,000 lexical tokens - {edition}")
        fig.colorbar(image, ax=ax, label="Signs / 1,000 lexical tokens")
        fig.tight_layout()
        fig.savefig(figures / f"{edition}-books.png", dpi=150)
        plt.close(fig)
        points = [p for p in payloads["clusters"] if p["edition_id"] == edition]
        if points:
            frame = pd.DataFrame(points)
            fig, ax = plt.subplots(figsize=(9, 6))
            for label, group in frame.groupby("cluster"):
                ax.scatter(group.pca_1, group.pca_2, s=9, alpha=0.5, label=f"Cluster {label}")
            ax.set(title=f"Exploratory verse profiles - {edition}", xlabel="Principal component 1", ylabel="Principal component 2")
            ax.legend()
            fig.tight_layout()
            fig.savefig(figures / f"{edition}-clusters.png", dpi=150)
            plt.close(fig)


def make_site(target: Path, summary: dict, verses: list[dict]) -> None:
    corpus = [{"reference": v["reference"], "edition": v["edition_id"], "text": v["raw_hebrew"],
               "flags": v["flags"], "accents": v["accent_count"]} for v in verses]
    embedded = canonical(corpus).replace("<", "\\u003c").replace("&", "\\u0026")
    images = "".join(f'<figure><img width="800" src="figures/{html.escape(p.name)}" alt="{html.escape(p.stem)}"></figure>'
                     for p in sorted((target / "figures").glob("*.png")))
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Torah cantillation research</title><style>body{{font:18px system-ui;max-width:1000px;margin:40px auto;padding:0 20px;line-height:1.6}}img{{max-width:100%;height:auto}}input{{font:inherit;width:95%;padding:10px}}article{{border-bottom:1px solid;padding:16px 0}}.he{{font-size:26px}}pre{{white-space:pre-wrap}}</style>
<h1>Torah cantillation research</h1><p>Snapshot <code>{html.escape(summary['snapshot'])}</code>. {'PILOT ONLY' if summary['pilot'] else 'Full reference coverage validated'}.</p>
<p><a href="findings.md">Computed findings</a> | <a href="summary.json">Provenance and environment</a></p>
<p>These are encoded-mark analyses, not a reconstruction of musical performance. Token-distinct interpretation is provisional. See DATA_LICENSES.md in the repository for attribution.</p>{images}
<h2>Verse explorer</h2><label for="q">Reference search (for example, Genesis 1:2)</label><input id="q" placeholder="Enter a reference"><p id="status"></p><div id="verses"></div>
<script id="corpus" type="application/json">{embedded}</script><script>
const rows=JSON.parse(document.getElementById('corpus').textContent);
function render(){{const query=document.getElementById('q').value.toLowerCase();const matches=rows.filter(r=>r.reference.toLowerCase().includes(query));const out=document.getElementById('verses');out.replaceChildren();document.getElementById('status').textContent=matches.length+' matches; showing first 30.';for(const row of matches.slice(0,30)){{const article=document.createElement('article');const heading=document.createElement('strong');heading.textContent=row.reference+' ['+row.edition+']';const text=document.createElement('p');text.className='he';text.dir='rtl';text.lang='he';text.textContent=row.text;const flags=document.createElement('p');flags.textContent='Encoded accents: '+row.accents+'; flags: '+(row.flags.join(', ')||'none');article.append(heading,text,flags);out.append(article);}}}}
document.getElementById('q').addEventListener('input',render);render();</script></html>'''
    (target / "index.html").write_text(page, encoding="utf-8")
