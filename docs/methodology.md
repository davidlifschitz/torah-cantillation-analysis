# Methodology and interpretation boundaries

## Corpus

The target is one explicitly selected Hebrew edition of the five books, using Sefaria's chapter/verse reference scheme. Chapter lengths are recorded at acquisition and checked against every returned chapter. The coverage claim concerns this reference scheme, not a universal traditional verse total. Pilot mode covers only chapter 1 of each book and is always labeled incomplete.

## Evidence layers

1. **Raw response and verse text:** preserved unchanged, with SHA-256 hashes and source metadata.
2. **Encoded marks:** U+0591-U+05AE are the accent-codepoint class. U+05AF is audited as Masora circle. U+05BD, maqaf, paseq, sof pasuq, upper/lower dots and nun hafukha are tracked separately. An offset is a zero-based Python Unicode-code-point offset in the original verse, not a byte, UTF-16 or visual RTL coordinate.
3. **Provisional token-distinct units:** each distinct accent code point per lexical token has a row linked to all its encoded occurrences. Repeated signs are collapsed only in this sensitivity representation. `function_class=unassigned` is intentional; this is not a complete linguistic parser.

Hebrew letter runs with combining marks form lexical tokens. Maqaf splits lexical tokens but links them with a verse-local group ID. Paragraph markers inside braces and HTML tag syntax are masked with equal-length spaces so offsets remain stable. Source strings are not normalized in place. Non-NFC sources are flagged.

HTML content, entities and bracketed readings are not silently converted into an authoritative reading. Such verses remain in the raw encoding audit but are excluded from sequence and model analysis. The raw atlas must therefore be interpreted as encoded-text counts; it is not a claim that all unresolved material represents spoken words.

A final U+05BD in the last token immediately preceding a unique sof pasuq may be marked `silluq_candidate`. This is a diagnostic heuristic, not a scholarly disambiguation rule. All U+05BD occurrences appear in the all-sign audit, and none is silently added to accent-codepoint sequences.

## Sequence eligibility

Exclude verses with unresolved markup/entities, bracketed alternatives, orphan accent signs, multiple distinct accents on one token, no encoded accents, or a nonstandard number of sof-pasuq marks. Retain their raw data and report exclusion counts. A future reviewed rule may resolve them without deleting evidence. Qere/ketiv and the Decalogue's alternative accentuations require dedicated fixtures and review.

Sequences use source token order, never visual RTL reversal. N-grams never cross verse boundaries. Literal sequences retain repetitions; token-distinct sequences collapse identical signs per token. Multi-distinct-token verses are excluded rather than arbitrarily ordering competing functions.

## Descriptive analysis

Counts and zero-inclusive book/chapter/parashah rates use **1,000 lexical tokens** as the stated denominator. The inventory is a census of the chosen snapshot, not a sample from an unspecified population. Rare-mark catalogs use a configurable-in-code initial threshold of 20 encoded occurrences per edition. All occurrences remain available in the mark table regardless of threshold.

Token-relative positions use `(position-1)/max(1, token_count-1)`. Entropy is descriptive Shannon entropy of accent-codepoint frequencies per verse, not linguistic or musical complexity.

## Exploratory discovery

- Adjacent-mark mutual information is compared with seeded within-verse random shuffles that preserve lengths and multiplicities. The plus-one permutation p-value and a Bonferroni adjustment across reported edition/representation tests are recorded. With 99 shuffles, the smallest unadjusted p-value is 0.01. This is one explicit null model, not proof of an explanatory theory.
- K-means uses normalized token-distinct accent proportions. Candidate k=2..6 values are assessed by silhouette; agreement between two seeds is reported. PCA plots aid inspection. Clusters are descriptive and not inferred genres or authorship classes.
- Uniform, add-one unigram and add-one bigram baselines predict the next encoded accent. Entire books are held out. Training verses with the same consonantal text as a held-out verse are removed. The alphabet is fixed to the 30 accent code points; evaluation uses mean log loss in bits.
- High-surprise verses are ranked by held-out mean transition surprise. This does not establish rarity under every model, textual error, historical change, or causation.
- Cross-edition comparisons align explicit verse references and compare raw text, consonants and both sequence representations. `not_run` is used when only one edition was acquired; that is not evidence of agreement.

### Follow-up robustness checks

The 2026-10-14 follow-up centers each eligible verse's normalized accent-profile vector within its exact lexical-token count. A multivariate pseudo-F summarizes the remaining book association. Book labels are permuted only among verses of the same exact length; length strata represented by only one book do not enter this comparison. Literal and token-distinct representations are reported separately, with a Bonferroni adjustment across those two tests. The verse-level permutation is exploratory and does not model dependence among verses in a chapter; effect size and the chapter-bootstrap check should be reported alongside its p-value.

Longer four- and five-mark sequences are mined within eligible verse boundaries, never across verses. Counts are overlapping window occurrences and are accompanied by distinct-verse support, book support, and per-book rates per 1,000 eligible windows. The screen of at least 20 occurrences in at least 10 verses is descriptive, not a significance threshold. A chapter-block bootstrap resamples chapters with replacement within each book and refits the fixed published k=2 solution; adjusted Rand index measures sensitivity of the full-snapshot assignment to chapter composition, not the validity of clusters as linguistic categories.

## Reproducibility

Record source snapshot, code commit/file checksums, dependency lock, Python/Unicode/package versions, seeds, parameters, inclusion rules and output checksums. Rebuild from saved raw bytes; do not redownload on notebook execution. Test deterministic table regeneration. Floating-point differences across platforms may require documented tolerances; image and notebook metadata need not be byte-identical.

## Not yet resolved

Functional conjunctive/disjunctive hierarchy, paseq versus legarmeh, all duplicated-display conventions, full qere/ketiv resolution, competing Decalogue systems, and a scholarly silluq classifier require primary-source rules and manually checked cases. The first implementation exposes those limitations instead of inventing answers. Both descriptive and deeper discovery tracks remain in scope.
