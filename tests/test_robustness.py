from torah_cantillation.robustness import (
    chapter_bootstrap_cluster_stability,
    length_conditioned_book_test,
    longer_ngram_tables,
)


def _verse(verse_id, book, chapter, token_count):
    return {"verse_id": verse_id, "book": book, "chapter": chapter,
            "token_count": token_count, "reference": f"{book} {chapter}:{verse_id}"}


def _sequence(verse, representation, symbols):
    return {"verse_id": verse["verse_id"], "book": verse["book"],
            "chapter": verse["chapter"], "reference": verse["reference"],
            "representation": representation, "eligible": True, "sequence": symbols}


def test_exact_length_conditioning_removes_length_only_book_difference():
    verses = []
    sequences = []
    profiles = {1: ["U+0591"], 2: ["U+0592"]}
    sizes = {"Genesis": {1: 10, 2: 2}, "Exodus": {1: 2, 2: 10}}
    for book, counts in sizes.items():
        verse_number = 0
        for token_count, count in counts.items():
            for _ in range(count):
                verse_number += 1
                verse = _verse(f"{book}-{verse_number}", book, 1, token_count)
                verses.append(verse)
                sequences.append(_sequence(verse, "token_distinct", profiles[token_count]))

    result = length_conditioned_book_test(verses, sequences, "token_distinct", permutations=19)

    assert result["status"] == "computed"
    assert result["unadjusted"]["r_squared"] > 0
    assert result["length_conditioned"]["r_squared"] == 0
    assert result["length_conditioned"]["permutation_p_exploratory"] == 1
    assert result["comparable_exact_token_count_strata"] == 2


def test_longer_ngrams_report_distinct_verse_and_book_support():
    verses = [
        _verse("g1", "Genesis", 1, 4),
        _verse("g2", "Genesis", 1, 4),
        _verse("e1", "Exodus", 1, 4),
    ]
    pattern = ["U+0591", "U+0592", "U+0591", "U+0592"]
    sequences = [
        _sequence(verse, representation, pattern)
        for verse in verses for representation in ("literal", "token_distinct")
    ]

    result = longer_ngram_tables(sequences, lengths=(4,), minimum_occurrences=3)

    literal = next(row for row in result["patterns"]
                   if row["representation"] == "literal" and row["sequence"] == pattern)
    assert literal["occurrences"] == 3
    assert literal["distinct_verse_support"] == 3
    assert literal["book_support"] == 2
    assert literal["per_book_counts"] == {"Exodus": 1, "Genesis": 2}
    assert literal["at_support_threshold"] is False


def test_chapter_bootstrap_cluster_stability_is_seeded_and_chapter_blocked():
    verses = []
    sequences = []
    for book, symbol in (("Genesis", "U+0591"), ("Exodus", "U+0592")):
        for chapter in (1, 2):
            for verse_number in (1, 2):
                verse = _verse(f"{book}-{chapter}-{verse_number}", book, chapter, 3)
                verses.append(verse)
                sequences.append(_sequence(verse, "token_distinct", [symbol]))

    first = chapter_bootstrap_cluster_stability(verses, sequences, iterations=5, seed=7)
    second = chapter_bootstrap_cluster_stability(verses, sequences, iterations=5, seed=7)

    assert first["status"] == "computed"
    assert first["chapters_with_eligible_verses_by_book"] == {"Exodus": 2, "Genesis": 2}
    assert first["ari_values"] == second["ari_values"]
    assert first["ari_median"] == 1
