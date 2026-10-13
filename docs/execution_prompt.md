# Execution prompt: continue the Torah cantillation research project

Work in the existing public GitHub repository `davidlifschitz/torah-cantillation-analysis`. Do not create another repository. Deliver both a comprehensive statistical atlas and substantive pattern discovery. Treat the repository's actual current state, successful workflow evidence and saved snapshots as the starting point; do not assume that this prompt's description guarantees completion.

## Inspect first

Read `AGENTS.md`, `README.md`, `DATA_LICENSES.md`, `docs/methodology.md`, `docs/data_dictionary.md`, `docs/research_log.md` and the open research issues. Inspect the current branch, code commit, dependency lock, most recent CI/research runs, published report directories, source manifests and notebooks. Distinguish implemented code, executed results and unresolved research tasks. Preserve existing work and do not force-push or overwrite other contributors' changes.

## Reproduce the current result

Install the locked development environment with `uv sync --locked --extra dev`. Run Ruff and pytest. Restore the approved source archive with `uv run python scripts/snapshot_archive.py restore --snapshot <existing-id>`. Run `uv run torah-cantillation reproduce --snapshot <existing-id>` and `uv run python scripts/notebooks.py --snapshot <existing-id> --execute`. Verify input hashes, edition-specific coverage, output reconciliation and deterministic table regeneration. Report exact failures rather than replacing missing values with zero.

If an approved raw snapshot is unavailable, acquire a new explicitly named snapshot. Use a new snapshot ID when refreshing source data. Never silently redownload during notebook execution. The primary edition is `Tanach with Ta'amei Hamikra`; MAM is an additional comparison edition, never a source for filling gaps in the primary corpus.

## Source contract

Use Sefaria's `/api/v3/texts/{book}.{chapter}` endpoint, explicitly requesting `version=hebrew|<exact versionTitle>`, `fill_in_missing_segments=0` and `return_format=default`. Discover and record chapter lengths via `/api/shape/{book}`. Use `/api/v2/raw/index/{book}` and its alternate structures for static parashah boundaries. Validate response refs, selected edition, actual language, warnings, license and segment counts. Do not use the weekly calendar to reconstruct static corpus membership. Preserve original response bytes, raw verse strings, timestamps, metadata and hashes. Keep network requests paced with bounded retries.

Reference documentation:
- https://developers.sefaria.org/reference/get-v3-texts
- https://developers.sefaria.org/reference/get-shape
- https://developers.sefaria.org/reference/get-versions
- https://developers.sefaria.org/docs/alternate-structures
- https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt

## Improve the linguistic representation

Maintain separate raw-codepoint and interpreted-unit layers. Review actual source cases and primary linguistic/edition documentation before classifying meteg/silluq, paseq/legarmeh, repeated prepositive/postpositive accents, maqaf-linked groups, qere/ketiv and alternative Decalogue accentuation. Add manually checked real-verse fixtures for each rule. Every interpreted unit must link to its source evidence. Keep ambiguous and conflicting readings explicit. Do not claim a functional hierarchy merely because code points have been counted. Compare updated outputs against the existing conservative representation and explain every changed inclusion/counting rule.

## Research breadth and depth

Retain the complete inventory, all occurrence evidence, normalized book/chapter/parashah distributions, zero counts, rare contexts, positional profiles and verse-length descriptions. Extend sequence and structural investigations beyond frequency charts. Study recurring and unusual combinations, longer sequences, clustering, similarity, held-out predictability and robust outliers. Inspect the original Hebrew for examples driving major findings.

Use initial results to generate further questions. For differences across sections, examine verse length, repeated passages, localized concentrations and source/encoding effects. Compare alternative representations and null models. Evaluate cluster stability and predictive leakage. Do not restrict the number of useful analyses arbitrarily, but prioritize evidence and interpretability rather than accumulating decorative charts.

Every investigation must state its question, source snapshot, representation, inclusion rules, denominator, comparison or null model, computed result, exact supporting references, alternative explanations and limitations. Use grouped held-out evaluation where appropriate. Account for multiple pattern searches. Corpus descriptive counts are a census of the chosen edition, not sample estimates from an unspecified population. Record negative findings and failed hypotheses. Do not infer genre, authorship, historical development, textual error or causation from an unexplained cluster or correlation.

## Edition comparison and publication

Verify MAM's precise upstream license version, attribution and share-alike requirements before publishing its raw text, quotations or text-bearing derived outputs. The API's generic `CC-BY-SA` label is not permission to invent a license version. Align references and explicitly audit segmentation disagreements. Re-run substantive findings separately by edition and distinguish robust results from editorial/encoding artifacts.

Keep reusable logic in `src/` and explanatory notebooks in `notebooks/`. Publish executed notebooks, generated tables/figures, an evidence-based findings report, source manifests, permitted raw archives, code/environment provenance and updated research logs. Improve the verse explorer only after the underlying representation is stable. A generated HTML file is not a deployed website; verify deployment before supplying a live-site claim.

Use reviewable commits and pull requests for substantive extensions. Never commit secrets, auth headers or unrelated private data. Do not edit upstream Sefaria text. Do not create a final research release until coverage, reproduction, notebook execution, licensing and scientific-review gates pass.

## Final handoff

Provide the actual GitHub commit/PR URLs, CI and research run outcomes, snapshot ID, coverage and exclusion totals, verified findings, notebook/report locations, any deployed site or release identifiers, and specific remaining limitations. Never report an unexecuted analysis as completed or a proposed finding as established.
