"""Length-conditioned comparisons and deeper sequence robustness checks."""
from __future__ import annotations

import unicodedata
from collections import Counter, defaultdict

import numpy as np

from .parse import ACCENTS


def _profile_rows(verses: list[dict], sequences: list[dict], representation: str) -> tuple[list[dict], list[str]]:
    alphabet = [f"U+{code:04X}" for code in sorted(ACCENTS)]
    column = {code: i for i, code in enumerate(alphabet)}
    verse_by_id = {verse["verse_id"]: verse for verse in verses}
    rows = []
    for sequence in sequences:
        if sequence["representation"] != representation or not sequence["eligible"]:
            continue
        counts = Counter(sequence["sequence"])
        if not counts:
            continue
        total = sum(counts.values())
        profile = np.zeros(len(alphabet), dtype=float)
        for codepoint, count in counts.items():
            profile[column[codepoint]] = count / total
        verse = verse_by_id[sequence["verse_id"]]
        rows.append({"book": verse["book"], "chapter": verse["chapter"],
                     "token_count": verse["token_count"], "reference": verse["reference"],
                     "profile": profile})
    return rows, alphabet


def _pseudo_f(features: np.ndarray, labels: np.ndarray) -> dict:
    groups = sorted(set(labels))
    if len(groups) < 2 or len(features) <= len(groups):
        return {"pseudo_f": 0.0, "r_squared": 0.0, "groups": len(groups)}
    grand = features.mean(axis=0)
    total = float(((features - grand) ** 2).sum())
    between = 0.0
    for group in groups:
        values = features[labels == group]
        between += len(values) * float(((values.mean(axis=0) - grand) ** 2).sum())
    if total <= 1e-15:
        return {"pseudo_f": 0.0, "r_squared": 0.0, "groups": len(groups)}
    within = max(0.0, total - between)
    if within <= 1e-15:
        value = float(np.finfo(np.float64).max)
    else:
        value = (between / (len(groups) - 1)) / (within / (len(features) - len(groups)))
    return {"pseudo_f": float(value), "r_squared": float(between / total), "groups": len(groups)}


def length_conditioned_book_test(
    verses: list[dict], sequences: list[dict], representation: str,
    *, permutations: int = 999, seed: int = 42,
) -> dict:
    """Compare per-verse accent profiles after centering within exact token counts.

    Book labels are permuted only among verses with the same lexical-token count.
    Token-count strata represented by only one book are excluded because they
    provide no cross-book comparison.
    """
    if permutations < 1:
        raise ValueError("At least one permutation is required")
    rows, alphabet = _profile_rows(verses, sequences, representation)
    if not rows:
        return {"representation": representation, "status": "skipped", "reason": "no eligible verse profiles"}
    all_features = np.stack([row["profile"] for row in rows])
    all_labels = np.array([row["book"] for row in rows])
    all_lengths = np.array([row["token_count"] for row in rows])
    all_strata = defaultdict(list)
    for index, length in enumerate(all_lengths):
        all_strata[int(length)].append(index)
    comparable = {length: indices for length, indices in sorted(all_strata.items())
                  if len({all_labels[index] for index in indices}) > 1}
    included_indices = sorted(index for indices in comparable.values() for index in indices)
    if len(included_indices) <= len(set(all_labels[included_indices])):
        return {"representation": representation, "status": "skipped", "reason": "too few comparable verses"}

    features = all_features[included_indices]
    labels = all_labels[included_indices]
    lengths = all_lengths[included_indices]
    refs = [rows[index]["reference"] for index in included_indices]
    adjusted = features.copy()
    strata = {}
    for length in sorted(set(lengths)):
        indices = np.flatnonzero(lengths == length)
        adjusted[indices] -= features[indices].mean(axis=0)
        strata[int(length)] = indices

    raw_result = _pseudo_f(features, labels)
    observed = _pseudo_f(adjusted, labels)
    rng = np.random.default_rng(seed)
    null_values = []
    for _ in range(permutations):
        shuffled_labels = labels.copy()
        for indices in strata.values():
            shuffled_labels[indices] = rng.permutation(labels[indices])
        null_values.append(_pseudo_f(adjusted, shuffled_labels)["pseudo_f"])
    p_value = (1 + sum(value >= observed["pseudo_f"] for value in null_values)) / (permutations + 1)

    offsets = []
    for book in sorted(set(labels)):
        indices = np.flatnonzero(labels == book)
        mean_offset = adjusted[indices].mean(axis=0)
        for feature_index, codepoint in enumerate(alphabet):
            local = adjusted[indices, feature_index]
            positive = int(indices[int(np.argmax(local))])
            negative = int(indices[int(np.argmin(local))])
            offsets.append({
                "book": book,
                "codepoint": codepoint,
                "unicode_name": unicodedata.name(chr(int(codepoint[2:], 16))),
                "mean_profile_offset": float(mean_offset[feature_index]),
                "largest_positive_deviation_reference": refs[positive],
                "largest_negative_deviation_reference": refs[negative],
            })
    return {
        "representation": representation,
        "status": "computed",
        "eligible_verses_before_length_overlap": len(rows),
        "comparable_verses": len(included_indices),
        "excluded_verses_in_single_book_length_strata": len(rows) - len(included_indices),
        "comparable_exact_token_count_strata": len(strata),
        "exact_token_count_strata_total": len(all_strata),
        "null": "permute whole verse book labels within exact lexical-token counts",
        "seed": seed,
        "permutations": permutations,
        "unadjusted": raw_result,
        "length_conditioned": {
            **observed,
            "permutation_p_exploratory": float(p_value),
            "permutation_p_bonferroni_two_representations": float(min(1.0, p_value * 2)),
            "null_mean_pseudo_f": float(np.mean(null_values)),
            "null_95th_percentile_pseudo_f": float(np.quantile(null_values, 0.95)),
        },
        "book_codepoint_offsets": offsets,
    }


def chapter_bootstrap_cluster_stability(
    verses: list[dict], sequences: list[dict], *, clusters: int = 2,
    iterations: int = 100, seed: int = 42,
) -> dict:
    """Refit the fixed k-means solution on chapter-resampled training corpora."""
    if iterations < 1:
        raise ValueError("At least one bootstrap iteration is required")
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score

    rows, _ = _profile_rows(verses, sequences, "token_distinct")
    if len(rows) <= clusters:
        return {"status": "skipped", "reason": "too few eligible verses"}
    features = np.stack([row["profile"] for row in rows])
    if len(np.unique(features, axis=0)) < clusters:
        return {"status": "skipped", "reason": "too few distinct verse profiles"}
    chapter_indices = defaultdict(list)
    book_chapters = defaultdict(list)
    for index, row in enumerate(rows):
        key = (row["book"], row["chapter"])
        chapter_indices[key].append(index)
    for book, chapter in sorted(chapter_indices):
        book_chapters[book].append(chapter)

    baseline = KMeans(n_clusters=clusters, n_init=10, random_state=seed).fit(features)
    reference_labels = baseline.labels_
    rng = np.random.default_rng(seed)
    scores = []
    skipped = 0
    for iteration in range(iterations):
        sample = []
        for book in sorted(book_chapters):
            chapters = book_chapters[book]
            selected = rng.integers(0, len(chapters), size=len(chapters))
            for chapter_index in selected:
                sample.extend(chapter_indices[(book, chapters[int(chapter_index)])])
        model = KMeans(n_clusters=clusters, n_init=10, random_state=seed + iteration + 1)
        try:
            model.fit(features[sample])
            predicted = model.predict(features)
        except ValueError:
            skipped += 1
            continue
        scores.append(float(adjusted_rand_score(reference_labels, predicted)))
    if not scores:
        return {"status": "skipped", "reason": "all chapter bootstrap fits failed", "skipped_fits": skipped}
    return {
        "status": "computed",
        "representation": "token-distinct per-verse accent proportions",
        "clusters": clusters,
        "fixed_k_reason": "k=2 was selected by the published silhouette search",
        "eligible_verses": len(rows),
        "chapters_with_eligible_verses_by_book": {book: len(chapters) for book, chapters in sorted(book_chapters.items())},
        "bootstrap_sampling": "sample chapters with replacement within each book; retain all eligible verses in each draw",
        "stability_measure": "adjusted Rand index against the full-snapshot k-means assignment on all eligible verses",
        "seed": seed,
        "iterations_requested": iterations,
        "successful_fits": len(scores),
        "skipped_fits": skipped,
        "ari_median": float(np.median(scores)),
        "ari_05_percentile": float(np.quantile(scores, 0.05)),
        "ari_95_percentile": float(np.quantile(scores, 0.95)),
        "fraction_ari_at_least_0_8": float(np.mean(np.array(scores) >= 0.8)),
        "ari_values": scores,
        "baseline_cluster_sizes": dict(sorted(Counter(reference_labels.tolist()).items())),
    }


def longer_ngram_tables(
    sequences: list[dict], *, lengths: tuple[int, ...] = (4, 5), minimum_occurrences: int = 20,
) -> dict:
    """Count verse-bounded longer n-grams with per-book and verse support."""
    if any(length < 2 for length in lengths):
        raise ValueError("N-gram lengths must be at least two")
    if minimum_occurrences < 1:
        raise ValueError("The occurrence threshold must be positive")
    patterns = []
    summaries = []
    books = sorted({row["book"] for row in sequences})
    for representation in ("literal", "token_distinct"):
        selected = [row for row in sequences if row["representation"] == representation and row["eligible"]]
        for length in lengths:
            counts = Counter()
            refs = defaultdict(set)
            per_book = defaultdict(Counter)
            windows_by_book = Counter()
            for row in selected:
                sequence = row["sequence"]
                windows = max(0, len(sequence) - length + 1)
                windows_by_book[row["book"]] += windows
                for start in range(windows):
                    pattern = tuple(sequence[start:start + length])
                    counts[pattern] += 1
                    refs[pattern].add(row["reference"])
                    per_book[pattern][row["book"]] += 1
            ordered = sorted(counts, key=lambda pattern: (-counts[pattern], pattern))
            qualifying = [pattern for pattern in ordered
                          if counts[pattern] >= minimum_occurrences and len(refs[pattern]) >= 10]
            qualifying_set = set(qualifying)
            summaries.append({
                "representation": representation,
                "n": length,
                "eligible_verses": len(selected),
                "within_verse_windows": int(sum(windows_by_book.values())),
                "distinct_patterns": len(counts),
                "patterns_at_least_threshold": len(qualifying),
                "minimum_occurrences": minimum_occurrences,
                "minimum_distinct_verse_support": 10,
            })
            for pattern in ordered:
                patterns.append({
                    "representation": representation,
                    "n": length,
                    "sequence": list(pattern),
                    "unicode_names": [unicodedata.name(chr(int(codepoint[2:], 16))) for codepoint in pattern],
                    "occurrences": counts[pattern],
                    "distinct_verse_support": len(refs[pattern]),
                    "book_support": len(per_book[pattern]),
                    "per_book_counts": {book: per_book[pattern][book] for book in books},
                    "per_book_per_1000_windows": {
                        book: (1000 * per_book[pattern][book] / windows_by_book[book]
                               if windows_by_book[book] else 0.0) for book in books
                    },
                    "example_references": sorted(refs[pattern])[:5],
                    "at_support_threshold": pattern in qualifying_set,
                })
    return {"summaries": summaries, "patterns": patterns}
