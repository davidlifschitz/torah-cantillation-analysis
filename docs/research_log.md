# Research log

## 2026-10-13 - Project initialization

Decision: deliver a complete descriptive atlas and deeper pattern discovery in the same project. Source acquisition uses explicitly named editions rather than Sefaria's changing default. Raw and interpreted counts remain separate.

Implementation: reusable Python pipeline, conservative parser, provenance/coverage checks, synthetic tests, descriptive and exploratory analyses, eleven-notebook generator and GitHub workflows.

Evidence status: synthetic tests validate code behavior only. They are not findings about the Torah. Full-corpus claims must cite successful run outputs. Code-point-level analysis is implemented; complete linguistic accent classification is not yet validated.

Licensing decision: automatic publication initially uses only the public-domain-labeled Tanach edition. MAM is available as an explicit local comparison pending precise license/attribution review.

Open methodological issues: qere/ketiv alternatives, repeated editorial signs, Decalogue accent systems, silluq/meteg and paseq/legarmeh. Exclusions remain visible and raw evidence is preserved.

Future entries must distinguish computed observations from hypotheses and explain changes to counting rules or source snapshots.

## 2026-10-14 - Reproduction, robustness follow-up and execution ledger

### Verified baseline

- Repository baseline: `main` at `6618506` when this run began; execution branch `work/execution-20261014`.
- `uv sync --locked --extra dev` succeeded. Restoring `primary-20261013`, running `torah-cantillation reproduce`, and running `scripts/check_reproduction.py` succeeded; all 18 saved report-table hashes matched.
- Primary snapshot: `Tanach with Ta'amei Hamikra`, Sefaria label `Public Domain`, upstream `http://www.tanach.us/Tanach.xml`; acquisition ran from `2026-10-13T17:05:24.836820+00:00` to `2026-10-13T17:09:35.180035+00:00` across 197 requests. It covers all 5,846 references in 187 chapters with no missing verses. The corpus verse-data SHA-256 is `fbce1f74013821d7a5bc40b3276413e2a75c451cdb5b4553c67e56e932225dba`; manifest SHA-256 is `a0467181216eaa45919a389e3f1ba473f053dc664e471e6b6ff1fe06b910cc44`; archived response ZIP SHA-256 is `a555628678a1de1f7962d4c90a43721fb614951eec1753c1288771b984d1ea59`.
- 4,686 verses are sequence-eligible and 1,160 are excluded by the conservative rules. Overlapping blocker counts are: bracketed alternatives 736, multiple distinct accents on a token 479, nonstandard sof-pasuq count 18. The original report also flags 5,823 non-NFC verses without normalizing the source text.
- The original report was created with Python 3.13.16 / Unicode 15.1.0; this Work Mode run used Python 3.12.14 / Unicode 15.0.0. Despite that runtime difference, the rebuilt analytical table hashes matched exactly. Dependency installation requires network access unless packages are cached; restore, reproduce, and comparison of existing raw data do not fetch Sefaria.
- Ruff and compileall passed. The first pytest run exposed that offline `SefariaClient` initialization still read an inherited SOCKS proxy even though no request could be made. Offline clients now set `trust_env=False`, and a regression test supplies a SOCKS proxy while checking the cached offline response. `uv run pytest -q` passes all 54 tests with the normal environment intact; online acquisition continues to honor environment proxy settings. Fix commit: `452a2ff`.
- All 11 saved notebooks contain executed code-cell counts and outputs; the prior hosted Research Pipeline run succeeded. Local re-execution is blocked because this runtime denies both TCP and IPC socket binding; see [the reproduction record](../reports/primary-20261013-followup-20261014/local-notebook-execution.md) and [issue #5](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/5).

### Follow-up findings

The new analysis-only report at `reports/primary-20261013-followup-20261014/` reuses the archived source snapshot and records its own table hashes, code commit, acquisition window, source hashes, coverage, flags, exclusion counts and parameters.

- The token-distinct four-mark sequence `U+05A3 U+0594 U+05A5 U+0596` occurs 1,024 times in 966 distinct eligible verses across all five books. Five raw Hebrew examples were inspected; the report records them and avoids treating the repeated encoding as a shared phrase or functional unit.
- After centering normalized verse profiles within exact lexical-token counts, pseudo-F is 3.003 for literal and 3.049 for token-distinct profiles; residual R² is 0.00256 and 0.00260, respectively. Both restricted tests reached the 999-permutation floor (p=0.001; Bonferroni p=0.002 across two representations). The small effect size, corpus-census scope and verse-level exchangeability assumption limit interpretation.
- With k fixed at 2, 100 chapter-block bootstrap fits gave median adjusted Rand index 0.968 (5th–95th percentiles 0.902–0.993). This measures partition stability under chapter resampling, not linguistic validity.
- The follow-up has complete 4- and 5-mark pattern tables for both representations, preserving within-verse boundaries and reporting unique-verse support and book rates.

### Dependency-aware progress ledger

| Workstream | Status | Dependencies | Evidence | Exact next action / owner | Blocker severity |
|---|---|---|---|---|---|
| Primary acquisition and provenance | verified | Archived primary snapshot | Manifest, source archive, full coverage and reproducibility hashes above | Keep `primary-20261013` immutable; give any new acquisition a new ID after a small current API check / project | none |
| Encoded-mark atlas | verified | Validated primary snapshot | `reports/primary-20261013/` | Review rare-occurrence references and figures for publication / project | localized, important |
| Functional linguistic interpretation | blocked | Primary edition documentation and domain review | `docs/methodology.md`, [issue #1](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/1) | Add reviewed real-verse fixtures for U+05BD, duplicated signs, paseq/legarmeh, maqaf, qere/ketiv and Decalogue variants; retain unassigned labels until sourced / domain reviewer | localized, important |
| Sequential and structural discovery | in_progress | Validated primary snapshot | [Follow-up report](../reports/primary-20261013-followup-20261014/); draft [PR #6](https://github.com/davidlifschitz/torah-cantillation-analysis/pull/6); [issue #3](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/3) | Compare additional similarity representations; measure localized concentration and exclusion-rule sensitivity; add interpretable predictors with grouped held-out evaluation; inspect remaining unusual passages / project | localized, important |
| MAM edition sensitivity | blocked | Exact upstream license/version and attribution | `DATA_LICENSES.md`, `edition_comparison.json`, [issue #2](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/2) | Verify upstream terms first; only then acquire a separate MAM snapshot and publish permitted comparisons / project | localized, important |
| Notebook execution in this runtime | blocked | Local TCP/IPC socket support | Saved execution outputs, prior successful [Research Pipeline run](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/runs/38435753641), [issue #5](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/5) | If notebook code changes, execute on a socket-capable hosted runner / environment | localized, important |
| PR CI for this follow-up | verified | Draft PR and hosted checks | [Draft PR #6](https://github.com/davidlifschitz/torah-cantillation-analysis/pull/6); [CI run #38557487440](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/runs/38557487440) passed on report commit `e92955d` | Await domain and repository review; address review feedback before any merge / project | none |
| Public website and versioned release | not_started | Scientific review, licensing review, PR/CI evidence | [issue #4](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/4); README does not claim a live site | After remaining review gates pass, verify Pages deployment and create an appropriately versioned release / project | publication gate |

### Open issues and deferred scope

Open research issues #1–#4 remain open because their acceptance criteria are not met. Issue #5 records the managed-runtime notebook socket restriction. No MAM text was fetched or redistributed; no functional classification was promoted; no release or live Pages site is claimed. The follow-up is not a final scholarly result.
