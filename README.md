# Torah Cantillation Analysis

[![CI](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/workflows/ci.yml)

**A reproducible, edition-aware study of Torah cantillation: both a statistical atlas and deeper pattern discovery.**

The corpus covers Genesis, Exodus, Leviticus, Numbers and Deuteronomy. Sefaria supplies the source texts; this project preserves edition metadata and raw code points, validates extraction, and generates findings with reusable Python code.

## Complete research results

This section summarizes the computed results for the approved primary snapshot and its analysis-only follow-up. Detailed JSON tables preserve every record; the links below point to the exact outputs. Findings describe encoded marks in one digital edition, not a complete linguistic or musical interpretation.

### Snapshot, coverage and denominators

The primary snapshot is primary-20261013, the Tanach with Ta'amei Hamikra edition. The source reports the license label Public Domain and identifies http://www.tanach.us/Tanach.xml as the upstream source. Acquisition ran from 2026-10-13T17:05:24.836820+00:00 through 2026-10-13T17:09:35.180035+00:00 over 197 requests. The historical [Research Pipeline run](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/runs/38435753641) completed the full-corpus workflow and notebook execution.

| Book | Verses | Lexical tokens | Encoded accents | Accents per 1,000 tokens | Three most frequent marks |
| --- | ---: | ---: | ---: | ---: | --- |
| Genesis | 1,533 | 20,721 | 16,509 | 796.73 | TIPEHA 2,970; MERKHA 2,411; MUNAH 2,404 |
| Exodus | 1,210 | 16,890 | 13,425 | 794.85 | TIPEHA 2,350; MUNAH 2,002; MERKHA 1,882 |
| Leviticus | 859 | 12,060 | 9,406 | 779.93 | TIPEHA 1,668; MERKHA 1,373; MUNAH 1,353 |
| Numbers | 1,288 | 16,581 | 13,125 | 791.57 | TIPEHA 2,437; MUNAH 1,889; MERKHA 1,854 |
| Deuteronomy | 956 | 14,490 | 11,769 | 812.22 | TIPEHA 1,865; MUNAH 1,814; MERKHA 1,600 |
| **Total** | **5,846** | **80,742** | **64,234** | **795.55** | |

There are no missing verse references. Of the 5,846 verses, 4,686 are eligible for sequence analysis and 1,160 are excluded under the conservative rules. Overlapping quality flags are: unresolved bracketed readings, 736; multiple distinct accents on a token, 479; nonstandard sof-pasuq count, 18; and non-NFC source text preserved unchanged, 5,823. Exclusion counts overlap; the non-NFC flag is not itself an exclusion. See [coverage summary](reports/primary-20261013/summary.json) and [quality flags](reports/primary-20261013/tables/quality_flags.json).

### Complete accent inventory

The table lists all 26 observed accent code points and counts. Names are Unicode character names, not a verified traditional taxonomy.

| Code point | Unicode name | Count |
| --- | --- | ---: |
| U+0591 | Etnahta | 5,491 |
| U+0592 | Segol | 372 |
| U+0593 | Shalshelet | 4 |
| U+0594 | Zaqef Qatan | 6,998 |
| U+0595 | Zaqef Gadol | 526 |
| U+0596 | Tipeha | 11,290 |
| U+0597 | Revia | 2,441 |
| U+0598 | Zarqa | 10 |
| U+0599 | Pashta | 6,378 |
| U+059A | Yetiv | 356 |
| U+059B | Tevir | 2,679 |
| U+059C | Geresh | 1,120 |
| U+059D | Geresh Muqdam | 1 |
| U+059E | Gershayim | 511 |
| U+059F | Qarney Para | 1 |
| U+05A0 | Telisha Gedola | 269 |
| U+05A1 | Pazer | 159 |
| U+05A3 | Munah | 9,462 |
| U+05A4 | Mahapakh | 3,050 |
| U+05A5 | Merkha | 9,120 |
| U+05A6 | Merkha Kefula | 5 |
| U+05A7 | Darga | 1,091 |
| U+05A8 | Qadma | 2,074 |
| U+05A9 | Telisha Qetana | 460 |
| U+05AA | Yerah Ben Yomo | 1 |
| U+05AE | Zinor | 365 |

The separate all-sign audit also records U+05BD meteg-or-silluq (5,049 records) and positional silluq candidates (5,148 records), U+05BE maqaf (11,477), U+05C0 paseq (387), U+05C3 sof pasuq (5,836), U+05C4 upper dot (32), and U+05C6 nun hafukha (2). The U+05BD labels remain distinct provisional audits. The 22 rare accent occurrences, defined by total count at most 20, are all linked here: [rare-occurrence table](reports/primary-20261013/tables/rare_occurrences.json). They comprise Shalshelet (4: Genesis 19:16, 24:12, 39:8; Leviticus 8:23); Zarqa (10: Genesis 17:20, 47:29; Exodus 6:6, 30:12, 36:2; Leviticus 4:2, 20:2; Numbers 20:19; Deuteronomy 14:24, 31:7); Geresh Muqdam (1: Leviticus 1:3); Qarney Para (1: Numbers 35:5); Merkha Kefula (5: Genesis 27:25; Exodus 5:15; Leviticus 10:1; Numbers 14:3, 32:42); and Yerah Ben Yomo (1: Numbers 35:5).

### Section distributions and verse profiles

Counts and rates per 1,000 lexical tokens are computed for every observed accent by book, chapter and parashah; zero-count combinations are retained. The exhaustive tables contain 130 book rows, 4,862 chapter rows and 1,404 parashah rows: [books](reports/primary-20261013/tables/books.json), [chapters](reports/primary-20261013/tables/chapters.json), and [parashahs](reports/primary-20261013/tables/parashahs.json). The position table preserves all 64,234 accent positions and token-relative positions; the formula is documented in the [methodology](docs/methodology.md).

Across the 4,686 eligible verses, accent-profile length has median 10 marks and ranges from 1 to 28. Mean profile entropy is 2.6433 bits for literal marks and 2.6463 for token-distinct marks; the median is 2.7255 bits for each. Both representations remain encoded-mark summaries. See the full [position](reports/primary-20261013/tables/positions.json) and [verse-profile](reports/primary-20261013/tables/verse_profiles.json) tables.

### Sequences and within-verse dependence

All sequence windows stay within verse boundaries. The largest observed bigram count is U+05A5 → U+0596 (MERKHA → TIPEHA): 4,697 occurrences, with conditional probability 0.8677. Another frequent pair is U+05A3 → U+0594 (MUNAH → ZAQEF QATAN): 3,321 occurrences, conditional probability 0.4512. A frequent trigram is U+0599 U+05A3 U+0594 (PASHTA, MUNAH, ZAQEF QATAN): 2,089 occurrences, conditional probability 0.9785. Example references and all 369 bigram and 1,265 trigram rows are in the [bigram](reports/primary-20261013/tables/bigrams.json) and [trigram](reports/primary-20261013/tables/trigrams.json) tables.

Adjacent-mark mutual information was compared with 99 within-verse shuffles preserving sequence lengths and mark multiplicities. The permutation p-value resolution is 0.01.

| Representation | Eligible verses with transitions | Observed MI (bits) | Shuffle mean (bits) | Exploratory p | Bonferroni p |
| --- | ---: | ---: | ---: | ---: | ---: |
| Literal | 4,685 | 1.6635 | 0.0562 | 0.01 | 0.02 |
| Token-distinct | 4,685 | 1.6950 | 0.0576 | 0.01 | 0.02 |

These are results under one shuffle null, not tests of historical, causal, or linguistic explanations. Full null distributions are in [transition_null.json](reports/primary-20261013/tables/transition_null.json).

### Clustering and high-surprise verses

The exploratory clustering uses token-distinct within-verse accent proportions. Among the tested k values, k=2 has the highest silhouette. Seed stability and silhouette for each tested value are:

| k | Silhouette | Seed stability ARI |
| ---: | ---: | ---: |
| 2 | 0.3134 | 0.9964 |
| 3 | 0.2077 | 0.9321 |
| 4 | 0.1780 | 0.6820 |
| 5 | 0.1611 | 0.9951 |
| 6 | 0.1544 | 0.7111 |

The selected k=2 assignment contains 1,196 verses in cluster 0 and 3,490 in cluster 1. A follow-up chapter-block bootstrap is reported below. Neither clustering result validates a linguistic, literary, or genre classification. See [cluster assignments](reports/primary-20261013/tables/clusters.json) and [diagnostics](reports/primary-20261013/tables/cluster_diagnostics.json).

The highest held-out-book model-surprise values include Numbers 29:18, 21, 24, 27, 30 and 33 (3.563 bits each; the same recurring sequence), Deuteronomy 6:10 (3.538), Genesis 43:7 (3.335), Leviticus 4:3 (3.326), Genesis 27:33 (3.271), and Leviticus 14:21 (3.269). These are out-of-book model-surprise observations, not evidence of textual errors. The [anomaly table](reports/primary-20261013/tables/anomalies.json) contains all 4,685 eligible verse records.

### Held-out prediction

Unigram and bigram baselines use add-one smoothing, a fixed 30-symbol alphabet and leave-one-book-out evaluation. Repeated consonantal verse texts in held-out books are removed from training.

| Held-out book | Train verses | Test verses | Uniform loss (bits/event) | Unigram loss | Bigram loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| Genesis | 3,345 | 1,340 | 4.9069 | 3.4056 | 1.7356 |
| Exodus | 3,682 | 941 | 4.9069 | 3.4544 | 1.7674 |
| Leviticus | 3,938 | 697 | 4.9069 | 3.4535 | 1.7694 |
| Numbers | 3,621 | 1,023 | 4.9069 | 3.4777 | 1.8127 |
| Deuteronomy | 4,000 | 684 | 4.9069 | 3.5271 | 1.8462 |

The lower bigram loss shows predictive dependence under this held-out-book setup; it does not establish a functional accent grammar. All 15 model rows are in [model_evaluation.json](reports/primary-20261013/tables/model_evaluation.json).

### Follow-up robustness results

Analysis-only follow-up primary-20261013-followup-20261014 reuses the same source snapshot and does not reacquire or modify text. The full report records the analysis code commit, source provenance, hashes, examples and caveats.

Within-verse four- and five-mark windows may overlap. The support screen is at least 20 occurrences in at least 10 distinct verses.

| Representation | n | Patterns | Windows | Patterns meeting support screen |
| --- | ---: | ---: | ---: | ---: |
| Literal | 4 | 1,565 | 36,704 | 303 |
| Literal | 5 | 3,160 | 32,210 | 352 |
| Token-distinct | 4 | 1,511 | 35,951 | 293 |
| Token-distinct | 5 | 3,004 | 31,459 | 341 |

The most frequent token-distinct four-mark sequence, U+05A3 U+0594 U+05A5 U+0596 (MUNAH, ZAQEF QATAN, MERKHA, TIPEHA), occurs 1,024 times in 966 eligible verses across all five books. Inspected source examples are Genesis 1:4, Exodus 1:1, Leviticus 3:9, Numbers 1:4, and Deuteronomy 1:3. Different contexts do not establish one shared phrase or function.

For the exact-length-conditioned book-profile test, each verse contributes an equally weighted accent-proportion vector centered within its exact lexical-token count. Length strata represented by only one book are excluded; book labels are permuted within the comparable strata. Both representations use 4,683 verses in 30 strata and 999 permutations.

| Representation | Unadjusted R² | Exact-length residual R² | Pseudo-F | Exploratory p | Bonferroni p |
| --- | ---: | ---: | ---: | ---: | ---: |
| Literal | 0.00485 | 0.00256 | 3.003 | 0.001 | 0.002 |
| Token-distinct | 0.00486 | 0.00260 | 3.049 | 0.001 | 0.002 |

The residual association is small. Verse-level permutations do not model dependence among verses in chapters; these p-values are exploratory.

With k fixed at 2, 100 chapter-resampled fits gave median ARI 0.968 against the full-snapshot assignment (5th–95th percentiles 0.902–0.993). This measures sensitivity to chapter composition, not cluster validity.

### Complete result files and limits

- Primary report: [computed findings](reports/primary-20261013/findings.md), [summary and provenance](reports/primary-20261013/summary.json), and [figures](reports/primary-20261013/figures/).
- Primary audit tables: [inventory](reports/primary-20261013/tables/inventory.json), [all signs](reports/primary-20261013/tables/all_signs.json), [rare occurrences](reports/primary-20261013/tables/rare_occurrences.json), [quality flags](reports/primary-20261013/tables/quality_flags.json), and [audit](reports/primary-20261013/tables/audit.json).
- Primary distribution tables: [books](reports/primary-20261013/tables/books.json), [chapters](reports/primary-20261013/tables/chapters.json), [parashahs](reports/primary-20261013/tables/parashahs.json), [positions](reports/primary-20261013/tables/positions.json), and [verse profiles](reports/primary-20261013/tables/verse_profiles.json).
- Primary sequence and model tables: [bigrams](reports/primary-20261013/tables/bigrams.json), [trigrams](reports/primary-20261013/tables/trigrams.json), [transition nulls](reports/primary-20261013/tables/transition_null.json), [cluster assignments](reports/primary-20261013/tables/clusters.json), [cluster diagnostics](reports/primary-20261013/tables/cluster_diagnostics.json), [anomalies](reports/primary-20261013/tables/anomalies.json), [model evaluation](reports/primary-20261013/tables/model_evaluation.json), and [edition comparison status](reports/primary-20261013/tables/edition_comparison.json).
- Follow-up report: [findings](reports/primary-20261013-followup-20261014/findings.md), [summary and hashes](reports/primary-20261013-followup-20261014/summary.json), [all long n-grams](reports/primary-20261013-followup-20261014/tables/long_ngrams.json.gz), [length-conditioned profiles](reports/primary-20261013-followup-20261014/tables/length_conditioned_books.json), [cluster bootstrap](reports/primary-20261013-followup-20261014/tables/cluster_bootstrap.json), and [inspected examples](reports/primary-20261013-followup-20261014/tables/inspected_examples.json).
The recorded input and follow-up output fingerprints are:

| Artifact | SHA-256 |
| --- | --- |
| Source archive | a555628678a1de1f7962d4c90a43721fb614951eec1753c1288771b984d1ea59 |
| Source manifest | a0467181216eaa45919a389e3f1ba473f053dc664e471e6b6ff1fe06b910cc44 |
| Corpus verse data | fbce1f74013821d7a5bc40b3276413e2a75c451cdb5b4553c67e56e932225dba |
| Follow-up long_ngrams.json.gz | 2c3ef7ed5e915080d19f071c71f113bfc264279f8f382776aae20a4b410e15d1 |
| Follow-up length_conditioned_books.json | b060793628eff08e8bfae8cb7a205ec5015594ac9555fa9534dd9f1bcf50e823 |
| Follow-up cluster_bootstrap.json | 32c5e9d4af7daad3acab1509f61de7939829f1c0c33ccbab4421dd426cd943df |
| Follow-up inspected_examples.json | cdfbfded26b3aab4f48a745c91ac2c97f9f86bbe1a034dabc303fb05c4a1cf1f |

The 18 primary-table hashes are in the primary summary; the four follow-up table hashes are in the follow-up summary. Follow-up analysis code commit: d62a014fda85e5cfed8b3bf7f6f152b27ced6c24. The work is under [draft PR #6](https://github.com/davidlifschitz/torah-cantillation-analysis/pull/6); the latest hosted [CI run passed](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/runs/38557896995).

The eleven notebooks retain executed outputs, and the historical hosted run linked above succeeded. Notebook re-execution in this managed runtime is blocked by its local TCP/IPC socket restrictions; see [issue #5](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/5).

Edition comparison is explicitly not run: only one edition was acquired. MAM text was not fetched; verify its exact upstream terms before acquisition or redistribution. Functional accent classifications, linguistic fixtures, alternative similarity methods, exclusion sensitivity and localized concentration analyses remain open work. This is an exploratory analysis, not a final scholarly result or deployed website.


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

The MAM comparison has **not** been run in the published snapshot; its output explicitly says `not_run`. Functional accent hierarchies, resolved qere/ketiv, dual-accented Decalogue passages and a full silluq classifier remain linguistic-review tasks. See [research issues](https://github.com/davidlifschitz/torah-cantillation-analysis/issues) and the [roadmap](docs/roadmap.md).

## Reproduce the published result

Python 3.12+ is required; the first successful CI/research run used Python 3.13.16. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
git clone https://github.com/davidlifschitz/torah-cantillation-analysis.git
cd torah-cantillation-analysis
uv sync --locked --extra dev
uv run python scripts/snapshot_archive.py restore --snapshot primary-20261013
uv run torah-cantillation reproduce --snapshot primary-20261013
uv run python scripts/check_reproduction.py --snapshot primary-20261013
uv run python scripts/notebooks.py --snapshot primary-20261013 --execute
uv run pytest -q
```

The approved raw response archive is committed at `data/snapshots/primary-20261013.zip`; the extracted raw and rebuilt processed tables are intentionally ignored by Git. Restoration followed by reproduction does **not** contact Sefaria. Installing dependencies still requires network access unless packages are already cached. Save the source commit, snapshot and `uv.lock` when citing results.

The notebook execution command below worked in the historical hosted research workflow. In this managed runtime, re-execution is blocked by local socket permissions (issue #5); no notebook code was changed in the follow-up.

The generated reference explorer is `reports/primary-20261013/index.html`; open it locally after cloning. **GitHub Pages has not been deployed.**

### Acquire a new snapshot

```bash
uv run torah-cantillation sources
uv run torah-cantillation fetch --snapshot my-new-snapshot
uv run torah-cantillation build --snapshot my-new-snapshot
uv run torah-cantillation validate --snapshot my-new-snapshot
uv run torah-cantillation analyze --snapshot my-new-snapshot
uv run python scripts/notebooks.py --snapshot my-new-snapshot --execute
```

Fetch is sequential, paced and resumable and does not require a Sefaria API key. `--pilot` fetches chapter 1 in each book and labels reports as a pilot. `--comparison` additionally requests MAM; review [data licensing](DATA_LICENSES.md) before redistribution. Existing snapshots are checksum-verified, never silently refreshed. Use a new snapshot ID when acquiring new source content.

Optional Parquet output: install `uv sync --locked --extra dev --extra parquet`, then add `--parquet` to `build` or `reproduce`. UTF-8 JSONL is the canonical analytical representation.

## Repository map

- `src/torah_cantillation/`: acquisition, evidence tables, validation, analysis and CLI.
- `scripts/`: notebook execution, approved source archiving and deterministic reproduction checks.
- `notebooks/`: eleven executed, explanatory research notebooks.
- `data/snapshots/`, `data/manifests/`: approved raw-source archive and provenance.
- `data/raw/`, `data/processed/`: restored and rebuilt local evidence, ignored by Git.
- `reports/<snapshot>/`: findings, tables, figures, environment records and local verse explorer.
- `docs/`: API sources, counting rules, data dictionary, research log and roadmap.
- `tests/`: offline unit and synthetic end-to-end tests; synthetic fixtures are never findings.

Analytical logic belongs in the tested package, not hidden notebook cells. Every encoded mark preserves its source position; every provisional unit links to its supporting marks. Work-mode continuation instructions are in [docs/execution_prompt.md](docs/execution_prompt.md).

## Interpretation boundary

An encoded sign is not necessarily one functional cantillation unit. The literal layer preserves repetitions. The provisional token-distinct layer collapses identical signs on a token for sensitivity analysis, but does not resolve every linguistic role. U+05BD is audited as meteg-or-silluq; a positional silluq candidate remains a candidate. Unresolved markup and reading alternatives are flagged rather than normalized away.

Counts describe one digital edition, not all manuscripts or melodies. Clusters are not inferred genres; unusual passages are not errors. No historical or causal claim follows merely from an exploratory statistical association. This is a reproducible first research pass, not a final scholarly edition.

## License, citation and contributions

Original software: [MIT](LICENSE). Source text and derived outputs: [DATA_LICENSES.md](DATA_LICENSES.md), not automatically MIT. Upstream attribution remains in the manifest. Cite with [CITATION.cff](CITATION.cff), including the exact source snapshot and code commit.

Read [CONTRIBUTING.md](CONTRIBUTING.md). Research questions, domain review and reproducibility improvements are welcome. Do not commit credentials or manually entered numbers presented as computed findings.
