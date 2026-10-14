# Research roadmap

Both descriptive atlas and deeper discovery are required; implementation order is not a restriction on scope.

## Foundation implemented

Explicit-edition acquisition; checksummed raw cache and manifest; chapter coverage validation; character/token/evidence tables; conservative ambiguity flags; book/chapter/parashah distributions; verse-bounded n-grams; positional/entropy profiles; shuffle-null dependence; exploratory clusters; held-out prediction and surprise; optional edition comparison; notebook execution and generated reports.

## Verified 2026-10-14 follow-up

The primary snapshot `primary-20261013` was restored and deterministically reproduced with all 18 report-table hashes matching the saved report. A separate follow-up report adds four- and five-mark sequence mining, exact-length-conditioned book-profile comparisons, and 100 chapter-block bootstrap fits for the fixed k=2 cluster solution. See [computed follow-up findings](../reports/primary-20261013-followup-20261014/findings.md) and the detailed [research log](research_log.md).

## Remaining acceptance gates

- Independently review all rare-mark occurrences, figures, high-surprise verses and the exclusion rules before calling the public study publication-ready.
- Create manually verified real-verse fixtures for duplicated accents, meteg/silluq, paseq/legarmeh, maqaf, qere/ketiv and dual-accented Decalogue passages. Keep lexical alternatives separate and documented.
- Verify MAM's precise upstream license/version and attribution; then publish a comparison run and assess whether the substantive findings change.
- Extend interpreted units to a sourced functional taxonomy and validated hierarchy, retaining uncertain cases.
- Continue discovery with alternative similarity measures, grouped held-out evaluation and exclusion/edition sensitivity. The current length-conditioned test and cluster bootstrap remain exploratory and do not resolve chapter-level dependence.
- Improve the explorer with mark highlighting, sequence inspection and occurrence search after the representation is validated.
- Publish an archived release and optional GitHub Pages site after research and licensing review. Do not label a prototype a final scholarly result.

Each investigation should record: question; motivation; source snapshot; representation; inclusion criteria; method/null model; computed result; inspected examples; alternatives; limitations; next decision. Continue promising questions that emerge from the data instead of stopping at this list.
