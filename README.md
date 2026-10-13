# Torah Cantillation Analysis

[![CI](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/workflows/ci.yml)

**A reproducible, edition-aware study of Torah cantillation: both a complete statistical atlas and deeper pattern discovery.**

The corpus covers Genesis, Exodus, Leviticus, Numbers and Deuteronomy. Sefaria supplies the source texts; this project preserves edition metadata and raw code points, validates extraction, and generates its findings with reusable Python code.

## Status and findings

This is research software, not an authoritative linguistic edition. Initial publication includes the runnable pipeline, tests, methodology and notebook generator. **Only completed workflow outputs count as findings.** No result is claimed merely because a notebook or repository exists.

The **Research pipeline** workflow acquires a full primary-edition snapshot, executes the analysis and all eleven notebooks, verifies deterministic table regeneration, and publishes successful outputs to `reports/<snapshot>/`. Run status is visible in [Actions](https://github.com/davidlifschitz/torah-cantillation-analysis/actions). If a run fails, read its error instead of treating missing results as zero counts.

## Research scope

| Track | Implemented outputs |
| --- | --- |
| Inventory | Encoded accent frequencies, all-sign audit, rare-occurrence references |
| Distribution | Book, chapter and parashah rates per 1,000 lexical tokens, including zeros |
| Sequences | Verse-bounded bigrams/trigrams, conditional probabilities, shuffle-null dependence |
| Structure | Relative token positions, verse lengths and entropy profiles |
| Similarity | Normalized-profile clustering, silhouette diagnostics and seed stability |
| Anomalies | Rare contexts and out-of-book model surprise, with exact references |
| Prediction | Uniform, unigram and bigram baselines evaluated by held-out book |
| Robustness | Literal versus token-distinct representations; optional cross-edition comparison |

Functional accent hierarchies, resolved qere/ketiv readings, dual-accented Decalogue passages and a full silluq classifier remain explicit linguistic-review tasks. They are not silently guessed. See [methodology](docs/methodology.md) and [roadmap](docs/roadmap.md).

## Quick start

Python 3.12+ is required; CI uses Python 3.13. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
git clone https://github.com/davidlifschitz/torah-cantillation-analysis.git
cd torah-cantillation-analysis
# The first successful automation run commits uv.lock.
# Before that initial lock exists, use: uv sync --extra dev
uv sync --locked --extra dev
uv run torah-cantillation sources
uv run torah-cantillation fetch --snapshot my-first-snapshot
uv run torah-cantillation build --snapshot my-first-snapshot
uv run torah-cantillation validate --snapshot my-first-snapshot
uv run torah-cantillation analyze --snapshot my-first-snapshot
uv run python scripts/notebooks.py --snapshot my-first-snapshot --execute
```

Fetch is sequential, paced and resumable. It does not require a Sefaria API key. `--pilot` fetches chapter 1 of each book and labels every report as a pilot. `--comparison` additionally requests MAM; review [data licensing](DATA_LICENSES.md) before redistribution.

### Offline reproduction

Preserve `data/raw/<snapshot>/`, `data/manifests/<snapshot>.json`, the code commit and `uv.lock`. Then:

```bash
uv run torah-cantillation reproduce --snapshot my-first-snapshot
uv run python scripts/notebooks.py --snapshot my-first-snapshot --execute
uv run pytest -q
```

`reproduce` never fetches live text. New acquisitions use a **new snapshot ID**; existing snapshots are checksum-verified and not silently replaced. Optional Parquet output: install `uv sync --locked --extra parquet`, then add `--parquet` to `build` or `reproduce`.

## Repository map

- `src/torah_cantillation/`: acquisition, evidence tables, validation, analysis and CLI.
- `scripts/notebooks.py`: generates and optionally executes eleven explanatory notebooks.
- `notebooks/`: generated notebooks; outputs are real only after successful execution.
- `data/raw/`, `data/manifests/`, `data/processed/`: snapshots, provenance and evidence tables.
- `reports/<snapshot>/`: machine-readable tables, figures, findings, environment and a local verse explorer.
- `docs/`: API sources, counting rules, data dictionary, research log and roadmap.
- `tests/`: offline unit and synthetic end-to-end tests; synthetic fixtures are never research findings.

Analytical logic belongs in `src/`, not hidden notebook cells. Canonical analytical data uses UTF-8 JSONL; Parquet is optional. Every mark keeps a source-verse offset and every provisional unit links to its underlying marks.

## Important interpretation boundary

An encoded sign is not necessarily one functional cantillation unit. The literal layer preserves repeated signs. The provisional token-distinct layer collapses identical signs on a token for sensitivity analysis, but does **not** claim to resolve all linguistic roles. U+05BD is audited separately as meteg-or-silluq; a positional silluq candidate is explicitly a candidate. Unresolved markup and reading alternatives are flagged, not normalized away.

Counts describe a selected digital edition, not all manuscripts or melodies. Clusters are not inferred genres; unusual passages are not errors; no historical or causal claims follow from exploratory statistics.

## License, citation and contributions

Original software: [MIT](LICENSE). Text and text-derived outputs: [DATA_LICENSES.md](DATA_LICENSES.md), **not automatically MIT**. Upstream attribution is retained in source manifests. Cite with [CITATION.cff](CITATION.cff).

Read [CONTRIBUTING.md](CONTRIBUTING.md). Research questions, domain review and reproducibility improvements are welcome. Do not commit credentials or present manually entered numbers as computed findings.
