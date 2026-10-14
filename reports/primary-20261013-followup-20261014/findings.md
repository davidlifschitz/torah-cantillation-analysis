# Follow-up robustness findings

Analysis: primary-20261013-followup-20261014
Source snapshot: primary-20261013 (Tanach with Ta'amei Hamikra)
Analysis code commit: d62a014fda85e5cfed8b3bf7f6f152b27ced6c24

This report reuses the named primary snapshot and writes a separate analysis directory. It does not fetch or modify source text.
The counts are encoded Unicode marks. Token-distinct units remain a sensitivity representation, not a verified functional accent parser.

## Longer within-verse sequences

Four- and five-mark sequences are counted within eligible verses; windows never cross a verse boundary. Occurrences can overlap. The support screen is at least 20 occurrences in at least 10 distinct verses; all observed sequences remain in the gzip-compressed UTF-8 JSON table tables/long_ngrams.json.gz.

- literal, n=4: 1,565 observed patterns across 36,704 windows; 303 meet the stated support screen.
- literal, n=5: 3,160 observed patterns across 32,210 windows; 352 meet the stated support screen.
- token_distinct, n=4: 1,511 observed patterns across 35,951 windows; 293 meet the stated support screen.
- token_distinct, n=5: 3,004 observed patterns across 31,459 windows; 341 meet the stated support screen.

### Inspected frequent four-mark sequence

The most frequent token-distinct four-mark sequence is U+05A3 U+0594 U+05A5 U+0596 (HEBREW ACCENT MUNAH; HEBREW ACCENT ZAQEF QATAN; HEBREW ACCENT MERKHA; HEBREW ACCENT TIPEHA): 1,024 overlapping occurrences in 966 distinct eligible verses across 5 books. This is an encoded-pattern count, not a functional or musical unit.

Representative raw source verses were inspected across the five books:

- Deuteronomy 1:3: וַיְהִי֙ בְּאַרְבָּעִ֣ים שָׁנָ֔ה בְּעַשְׁתֵּֽי־עָשָׂ֥ר חֹ֖דֶשׁ בְּאֶחָ֣ד לַחֹ֑דֶשׁ דִּבֶּ֤ר מֹשֶׁה֙ אֶל־בְּנֵ֣י יִשְׂרָאֵ֔ל כְּ֠כֹל אֲשֶׁ֨ר צִוָּ֧ה יְהוָ֛ה אֹת֖וֹ אֲלֵהֶֽם׃
- Exodus 1:1: וְאֵ֗לֶּה שְׁמוֹת֙ בְּנֵ֣י יִשְׂרָאֵ֔ל הַבָּאִ֖ים מִצְרָ֑יְמָה אֵ֣ת יַעֲקֹ֔ב אִ֥ישׁ וּבֵית֖וֹ בָּֽאוּ׃
- Genesis 1:4: וַיַּ֧רְא אֱלֹהִ֛ים אֶת־הָא֖וֹר כִּי־ט֑וֹב וַיַּבְדֵּ֣ל אֱלֹהִ֔ים בֵּ֥ין הָא֖וֹר וּבֵ֥ין הַחֹֽשֶׁךְ׃
- Leviticus 3:9: וְהִקְרִ֨יב מִזֶּ֣בַח הַשְּׁלָמִים֮ אִשֶּׁ֣ה לַיהוָה֒ חֶלְבּוֹ֙ הָאַלְיָ֣ה תְמִימָ֔ה לְעֻמַּ֥ת הֶעָצֶ֖ה יְסִירֶ֑נָּה וְאֶת־הַחֵ֙לֶב֙ הַֽמְכַסֶּ֣ה אֶת־הַקֶּ֔רֶב וְאֵת֙ כָּל־הַחֵ֔לֶב אֲשֶׁ֖ר עַל־הַקֶּֽרֶב׃
- Numbers 1:4: וְאִתְּכֶ֣ם יִהְי֔וּ אִ֥ישׁ אִ֖ישׁ לַמַּטֶּ֑ה אִ֛ישׁ רֹ֥אשׁ לְבֵית־אֲבֹתָ֖יו הֽוּא׃

The examples show the mark sequence in different verse contexts. Their recurrence alone does not establish a shared phrase, syntax, genre, or historical explanation.

## Book profiles after exact verse-length conditioning

Each eligible verse contributes an equally weighted accent-proportion vector. For each representation, the vector is centered against the mean for verses with the exact same lexical-token count. Token-count strata represented by only one book are excluded. The test statistic is a multivariate pseudo-F; book labels are permuted within exact token-count strata.

- literal: 4,683 verses in 30 comparable token-count strata; unadjusted R²=0.00485, exact-length residual R²=0.00256, pseudo-F=3.003, restricted-permutation p=0.001 (Bonferroni across two representations=0.002; 999 permutations).
- token_distinct: 4,683 verses in 30 comparable token-count strata; unadjusted R²=0.00486, exact-length residual R²=0.00260, pseudo-F=3.049, restricted-permutation p=0.001 (Bonferroni across two representations=0.002; 999 permutations).

This is a descriptive association within one complete digital edition. The verse-level permutation assumes exchangeability within exact lengths and does not model dependence among neighboring verses in a chapter. The p-value is exploratory; it does not support genre, authorship, causation, or historical claims. See tables/length_conditioned_books.json for per-codepoint offsets and exact references at the largest verse-level deviations.

## Chapter-resampled clustering stability

With k fixed at 2 (the published silhouette-selected value), 100 chapter bootstrap fits gave a median adjusted Rand index of 0.968 against the full-snapshot partition (5th–95th percentiles 0.902–0.993).
The bootstrap resamples chapters with replacement within each book and retains all eligible verses in each sampled chapter. This measures sensitivity to chapter composition while holding k fixed; it does not validate clusters as linguistic or literary classes.

## Reproduction and scope

The primary snapshot has 5,846 validated verses across 187 chapters, with 0 missing verses. There are 4,686 sequence-eligible and 1,160 sequence-excluded verses. Quality-flag counts may overlap: bracketed_reading_unresolved=736; multiple_distinct_accents_on_token=479; non_nfc_source_preserved=5,823; nonstandard_sof_pasuq_count=18. Sequence-exclusion blockers also overlap: bracketed_reading_unresolved=736; multiple_distinct_accents_on_token=479; nonstandard_sof_pasuq_count=18.
The source acquisition window was 2026-10-13T17:05:24.836820+00:00 to 2026-10-13T17:09:35.180035+00:00 across 197 requests. The corpus verse-data SHA-256 is fbce1f74013821d7a5bc40b3276413e2a75c451cdb5b4553c67e56e932225dba; the source-manifest SHA-256 is a0467181216eaa45919a389e3f1ba473f053dc664e471e6b6ff1fe06b910cc44; the archived response ZIP SHA-256 is a555628678a1de1f7962d4c90a43721fb614951eec1753c1288771b984d1ea59.

Run from the repository root after restoring the approved archive:

```bash
uv run python scripts/snapshot_archive.py restore --snapshot primary-20261013
uv run python scripts/extended_robustness.py --source-snapshot primary-20261013 --report-id primary-20261013-followup-20261014 --permutations 999 --cluster-bootstrap 100
```

This analysis reuses the primary public-domain-labeled Tanach with Ta'amei Hamikra snapshot. It does not provide MAM comparison results, resolve linguistic classifications, or establish a live website or final scholarly release.
