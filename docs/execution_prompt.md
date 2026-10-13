# ChatGPT Work master execution prompt — Torah Cantillation Analysis

## Mission and working context

Continue and substantially advance the **existing** public repository: https://github.com/davidlifschitz/torah-cantillation-analysis (`davidlifschitz/torah-cantillation-analysis`). **Do not create a replacement repository.** Deliver both (a) a comprehensive, reproducible statistical atlas of cantillation throughout the five books of the Torah and (b) substantive discovery of sequential, structural, comparative and predictive patterns. Aim for a credible public computational-research resource, not merely a code scaffold or a set of decorative charts.

The repository already has a primary-edition research pipeline, tests, notebooks and reported outputs. **Verify its live state before believing any status described in this prompt.** Treat the repo, commits, manifests, CI logs and saved snapshots as the source of truth. Respect existing contributions. Do not force-push, discard results, or recreate work that is already validated.

## Operating policy: anti-stall, controlled effort and durable progress

**A localized failure must not become a project-wide blocker unless it genuinely compromises a shared prerequisite or scientific integrity.** Operate as a research lead coordinating independent tracks, not as a debugger who spends the whole run on one edge case.

1. **Classify every blocker before escalating effort.**
   - **Critical / shared prerequisite:** source integrity, incomplete or mixed-edition corpus, irreproducible core totals, compromised credentials, incompatible redistribution terms, or a parsing defect that invalidates all affected findings. Do not publish affected results until corrected. Where possible continue *unaffected* research tracks.
   - **Localized / important:** failure in one notebook, model, language interpretation, visualization, passage subset, edition comparison or deployment. Isolate and explicitly mark dependent outputs incomplete; continue independent tracks.
   - **Noncritical:** cosmetic formatting, optional tooling changes, warnings without material impact or marginal optimizations. Document/defer rather than consuming the run.
2. **Bound debugging.** For a localized problem, isolate the smallest reproduction and try **at most three distinct evidence-based remedies**, unless a new diagnosis materially changes the problem. Do not run identical failing commands repeatedly or make speculative config changes. Preserve logs and a reproducible failing case, open/update a GitHub Issue, record impact and alternatives, then move to unaffected tasks. A critical problem may require more effort, but still create checkpoints and reassess what can proceed independently.
3. **Use a dependency-aware progress ledger** in `docs/research_log.md` or an appropriate project file. For each workstream track status (`verified`, `in_progress`, `blocked`, `deferred`, `not_started`), dependencies, evidence URL/path, owner if applicable, exact next action, and blocker severity. Update it at meaningful milestones—not after every trivial command.
4. **Work across multiple viable tracks.** Include acquisition/provenance, encoded-character validation, linguistic interpretation, descriptive statistics, sequence/verse structure, clustering/anomalies, predictive modeling, edition sensitivity, and documentation/publication. Switch to another independent track when one stalls. Parallelize genuinely independent tasks where supported, but avoid simultaneous writes to the same snapshots, reports, branches or Git history.
5. **Checkpoint continuously.** After each meaningful validated milestone, commit reproducible code and documentation, capture source/output hashes, link CI results, and update outstanding issues. Prefer reviewable increments/PRs over a single giant uncommitted change. Never overwrite a verified prior snapshot with a new download.
6. **Choose routine reversible decisions autonomously.** Do not ask for approval on standard libraries, plot layout, implementation organization or bounded statistical-method choices. Escalate only decisions with significant scientific, licensing, security, irreversible or scope implications.
7. **Avoid premature completion.** Passing CI, opening a few issues, or producing initial frequency charts is not completion of the requested research. Conversely, one unresolved rare edge case does not justify abandoning all other analyses. Maximize **scientifically defensible** progress, not ticket closure or superficial green status.
8. **Be transparent about limitations.** Never invent data, silently omit exceptions, convert missing values to zero, substitute an edition without explicit provenance, report unexecuted notebooks as done, or describe provisional linguistic classification as verified. Report what was excluded and why.
9. **Manage execution time by milestones, not endless polish.** Prioritize reproducibility and breadth of substantive results first; pursue deeper investigations next; then presentation. Stop optional refinements when they threaten delivery of working artifacts. Preserve a useful, testable result even if not every research question can be completed in a single run.

## First actions: inspect and create the baseline

Read `AGENTS.md` if present, `README.md`, `DATA_LICENSES.md`, `docs/methodology.md`, `docs/data_dictionary.md`, `docs/research_log.md`, `docs/roadmap.md`, and open research issues. Inspect branch heads, recent commits, lockfile, CI and research-workflow history, notebooks, current findings, report directories, source archives and manifests. Identify precisely which work is implemented, executed and independently reproducible; which is provisional; and which is unstarted.

Record an initial progress ledger and a prioritized, dependency-aware plan. Do not spend the whole run planning: move promptly to reproducible execution, then substantive research.

## Reproduce existing results before altering interpretations

Install the locked environment with `uv sync --locked --extra dev` (adapt to the actual repo and document deviations). Run Ruff and pytest. Restore a verified snapshot using the repo-supported command, currently expected to resemble:

```bash
uv run python scripts/snapshot_archive.py restore --snapshot <existing-id>
uv run torah-cantillation reproduce --snapshot <existing-id>
uv run python scripts/notebooks.py --snapshot <existing-id> --execute
```

Verify reference coverage, edition, input hashes, source and table reconciliation, reproducible output digests and notebook execution. Investigate substantive mismatches and preserve their evidence; do not replace missing files or values with fabricated results. If no approved raw snapshot exists, acquire a **new explicitly named** snapshot and record the change. Notebook execution must not silently fetch new text.

## Source-data contract: Sefaria and edition isolation

Use the documented Sefaria API and confirm current behavior with small live requests before bulk acquisition:

- `GET /api/v3/texts/{book}.{chapter}` with **exact** `version=hebrew|<versionTitle>`, `fill_in_missing_segments=0`, `return_format=default`.
- `GET /api/shape/{book}` for expected chapter/verse coverage.
- `GET /api/v2/raw/index/{book}` for index structure and static parashah/aliyah boundaries; do **not** infer static membership from the weekly calendar.
- Verify available Hebrew editions, their actual language, metadata, reported licensing and warnings rather than assuming defaults.

Primary source candidate: **`Tanach with Ta'amei Hamikra`**. Independent comparison: **`Miqra according to the Masorah` (MAM)**. Never fill one edition's missing verses from another without an explicit, separately labeled experimental dataset; do not do so for the canonical corpus. Respect Sefaria rate limits using sequential or modestly paced requests, bounded retries/backoff, resume and caching. Preserve raw response bytes, raw Unicode, verse references, retrieval time, endpoint/parameters, license/source notes, source hashes and versioned manifests. Audit source-specific differences and verse segmentation.

Useful reference documentation:
- https://developers.sefaria.org/reference/get-v3-texts
- https://developers.sefaria.org/reference/get-shape
- https://developers.sefaria.org/reference/get-versions
- https://developers.sefaria.org/docs/alternate-structures
- https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt

## Linguistic and Unicode correctness

Preserve **two distinct analytical layers**: (1) literal Unicode occurrence data, and (2) interpreted cantillation units with documented rules, source spans, uncertainty and reversible mappings. Do not equate codepoint counts with functional accents. Examine real source verses and primary edition/linguistic documentation for meteg versus silluq (`U+05BD`), paseq and legarmeh, repeated prepositive/postpositive accents, maqaf-linked groups, qere/ketiv, paragraph markers, and alternate Decalogue accentuation. Add manually reviewed real-verse regression fixtures, documenting exact edition, verse, underlying code points and justification. Until rules are verified, leave functional classifications provisional and keep raw results available.

If an unresolved case affects only a subset of verses, make its inclusion/exclusion effect measurable and continue analyses valid on the rest. If it compromises a total or inference, block publication **of that affected claim**, not every independent analysis. Explain all changes relative to prior conservative counts and denominators.

## Full analytical program — both atlas and discovery

**Descriptive statistical atlas:** complete observed code-point inventory and every rare occurrence; denominators and frequencies (raw and normalized); book, chapter, parashah, aliyah where grounded; zero-frequency cases; length and verse-position profiles; visual distributions and drill-downs to actual references.

**Pattern and structural discovery:** verse-bounded bigrams, trigrams and longer supported n-grams; transitions and null/shuffle comparisons; typical and unusual local configurations; accent position versus verse length; recurrence and concentration across sections; sequence similarity, clustering and its stability; conservative anomaly detection; exploratory conditional prediction with meaningful baselines and grouped held-out evaluation; and inspection of original Hebrew examples behind major findings.

**Robustness and deeper explanation:** compare literal and interpreted representations; check length-conditioned section effects, repeated passages, localized concentrations, exclusion sensitivity and potential information leakage; compare appropriate null models and multiple-testing/exploration concerns. Validate major findings separately by edition where feasible, clearly attributing differences to textual/encoding/editorial choices where warranted. Generate further research questions from the data, including negative results, without imposing an arbitrary quota of plots or papers.

For **each** substantive finding, record: question/hypothesis, exact snapshot and code commit, representation and selection rules, denominator, method/comparison/null, computed numeric outcome, supporting verse references, robustness checks, plausible alternatives and limitations. A complete chosen digital Torah corpus is a census of that edition, not a random sample. Do not claim genre, authorship, compositional history, causation or textual error from clusters/correlations alone.

## Repository architecture and deliverables

Work inside the existing Python package, tests, scripts, `notebooks/`, `data/`, `reports/`, `docs/` and `.github/` layout. Keep reusable logic in `src/`; notebooks import it and explain methods/results. Produce executed notebooks (preferably the existing eleven, enhanced where justified), exact-source manifests, machine-readable tables, clear publication figures, independently reproducible reports, updated findings and research log, and an accessible verse explorer if feasible. Generate a new report/snapshot directory for revised research rather than rewriting published evidence without traceability.

Software remains separately licensed from text and derived datasets. **Before redistribution of MAM**, verify its exact upstream license version and share-alike/attribution requirements; do not infer version numbers from the Sefaria `CC-BY-SA` label. Review text-bearing exports and explorers for redistribution compliance. Publish only permitted material and carry attribution/license documentation into releases.

Use feature branches/PRs where practical for substantial changes, protect `main`, require passing tests, and preserve previous valid commits. Do not commit authentication secrets, raw credentials, private unrelated files, or fabricated summary data. GitHub Pages is not live merely because an HTML file exists: verify actual deployment before claiming a site. Do not label a release as scientifically final until reproduction, review, rights and coverage checks pass.

## Acceptance and final response contract

Before declaring work complete or handing off, validate and report:

1. Actual repository URL, branch, relevant commits/PR links and CI/research-workflow status.
2. Primary and comparison edition statuses; exact snapshot IDs, acquisition timestamps, source and result hashes; coverage including missing/excluded/flagged verses.
3. Which notebooks and analytical tracks **executed**; locations of raw/processed permitted data, scripts, tables, figures, findings, reports and explorer.
4. Important results with computed numbers, exact supporting references, method, denominators, caveats and comparisons; separate exploratory observations from supported conclusions.
5. Reproduction commands tested from a fresh environment and whether they succeed offline.
6. Open/blocking GitHub issues with severity, impact, attempted remedies and next action; list deferred noncritical work separately.
7. Verified live site/release links **only if they actually exist**, and remaining publication gates otherwise.
8. Updated progress ledger showing verified, in-progress, blocked, deferred and not-started tracks. State what is *not* done just as clearly as what is done.

**Final directive:** Pursue broad, deep and reproducible research. Do not let a small issue consume the whole execution; do not let momentum override scientific integrity. Commit the maximum verified value achievable and leave a transparent, actionable record of everything unresolved.