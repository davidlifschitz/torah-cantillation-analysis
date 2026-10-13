# Data dictionary

Canonical tables are UTF-8 JSONL under `data/processed/<snapshot>/`; optional Parquet encodes the same rows. One line is one row. IDs are edition-specific. Null means unresolved or inapplicable, never zero. Source response byte offsets are not used; character offsets refer to Python Unicode code points in `raw_hebrew`.

| Table | Grain and main fields |
| --- | --- |
| verses | One edition/reference: verse_id, edition_id, book, chapter, verse, reference, raw_hebrew, text_sha256, request_id, parashah, token_count, maqaf_group_count, accent_count, flags, sequence_eligible, rule_id |
| tokens | One lexical token: token_id, verse_id, edition_id, position (1-based), raw_token, start (inclusive), end (exclusive), maqaf_group, rule_id |
| marks | One encoded relevant sign: mark_id, verse_id, token_id (nullable), edition_id, codepoint, unicode_name, char_offset (0-based), category, interpretation, region (text/masked) |
| accent_units | One provisional distinct accent code point per token: unit_id, token_id, verse_id, edition_id, codepoint, evidence_mark_ids, repeat_count, function_class (unassigned), interpretation_status, rule_id |

`provenance.json` stores table checksums, manifest hash, parser rule version and Unicode database version. `validation.json` records coverage and integrity checks.

The acquisition manifest contains exact chapter shapes, static parashah ranges, request metadata, source-edition/license metadata, corpus hash, edition list and pilot/full status. `data/raw/<snapshot>/responses/` preserves every response byte-for-byte with companion metadata. `verses.jsonl` is the derived raw-verse index and has a manifest checksum.

Report tables under `reports/<snapshot>/tables/` include inventory, all_signs, books, chapters, parashahs, quality_flags, rare_occurrences, positions, verse_profiles, bigrams, trigrams, transition_null, clusters, cluster_diagnostics, model_evaluation, anomalies and edition_comparison. `summary.json` identifies environment, source code, parser, seeds and table hashes. Refer to the code and methodology for formulas and exclusion rules.
