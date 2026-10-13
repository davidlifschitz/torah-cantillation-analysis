# Computed findings

Snapshot: `primary-20261013`. **Full selected reference coverage validated.**

Encoded accents U+0591-U+05AE; all_signs separately audits U+05BD and other signs

## Corpus inventory

- `tanach`: 5,846 verses; 80,742 lexical tokens; 64,234 encoded accent signs in 26 code points; 4,686 verses eligible for sequence analysis.
  Most frequent encoded accents: HEBREW ACCENT TIPEHA (11,290); HEBREW ACCENT MUNAH (9,462); HEBREW ACCENT MERKHA (9,120); HEBREW ACCENT ZAQEF QATAN (6,998); HEBREW ACCENT PASHTA (6,378).

## Sequential dependence

- `tanach` / `literal`: observed adjacent-mark mutual information 1.6635 bits; within-verse shuffle mean 0.0562 bits; exploratory p=0.01; Bonferroni-adjusted p=0.02 (99 shuffles).
- `tanach` / `token_distinct`: observed adjacent-mark mutual information 1.6950 bits; within-verse shuffle mean 0.0576 bits; exploratory p=0.01; Bonferroni-adjusted p=0.02 (99 shuffles).

## Predictability

Leave-one-book-out log losses are in `tables/model_evaluation.json`. Unigram and bigram baselines use add-one smoothing and a fixed 30-symbol Unicode alphabet. Repeated consonantal verse texts in held-out books are removed from training.

## Interpretation limits

- Counts describe the encoded source snapshot, not every manuscript or chanting tradition.
- Literal inventory includes text in unresolved readings; inspect quality flags before claiming lexical or linguistic counts.
- Repeated signs remain in the literal layer. Token-distinct collapse is a sensitivity representation, not a linguistic truth.
- Markup, bracketed readings, orphan accents, multiple distinct accents on a token, and nonstandard verse endings exclude verses from sequence/model analysis, not the raw audit.
- Clusters and high-surprise verses are exploratory, not inferred genres, textual errors, or historical explanations.
- The shuffle tests one explicit null model. Descriptive counts are a corpus census, not sample estimates.
- Edition comparison is unrun unless two editions were acquired; inspect its status table.
- Silluq candidates are audited separately and excluded from accent-codepoint sequences.

## Evidence

All tables are under `tables/`. `summary.json` records provenance, environment versions, code and table checksums. `rare_occurrences.json` lists every occurrence of an encoded accent with total frequency <=20 in an edition. The complete occurrence inventory, including common signs, is `data/processed/<snapshot>/marks.jsonl`.
