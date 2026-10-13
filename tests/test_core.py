"""Offline synthetic parser fixtures: these are not Torah findings."""
from unittest.mock import patch

import httpx
import pytest

from torah_cantillation.analysis import entropy, mutual_information, ngrams, sequence_rows
from torah_cantillation.fetch import EDITIONS, SefariaClient, chapter_lengths, parashah_ranges, retry_delay, select_version
from torah_cantillation.io import digest, safe_snapshot
from torah_cantillation.parse import in_range, parse_verse


def source(text, name="synthetic:Genesis:1:1"):
    return {"verse_id": name, "edition_id": "synthetic", "book": "Genesis", "chapter": 1,
            "verse": 1, "reference": "Genesis 1:1", "raw_hebrew": text, "text_sha256": digest(text),
            "request_id": "synthetic-not-a-network-response"}


@pytest.mark.parametrize("bad", ["../x", "/tmp/x", "", "x y", "x/y", ".", "a" * 81])
def test_snapshot_paths(bad):
    with pytest.raises(ValueError):
        safe_snapshot(bad)


def test_valid_snapshot():
    assert safe_snapshot("20261013_tanach-v1") == "20261013_tanach-v1"


def test_offsets_and_raw_preservation():
    raw = "\u05d0\u05b8\u0591 \u05d1\u05b7\u05bd\u05c3"
    verse, tokens, marks, units = parse_verse(source(raw))
    assert verse["raw_hebrew"] == raw
    assert verse["accent_count"] == 1
    assert len(tokens) == 2
    assert len(units) == 1
    assert any(m["interpretation"] == "silluq_candidate" for m in marks)
    for mark in marks:
        assert mark["codepoint"] == f"U+{ord(raw[mark['char_offset']]):04X}"
    for token in tokens:
        assert raw[token["start"]:token["end"]] == token["raw_token"]


def test_meteg_not_counted_as_accent():
    _, _, marks, units = parse_verse(source("\u05d0\u05bd \u05d1\u0591\u05c3"))
    assert next(m for m in marks if m["codepoint"] == "U+05BD")["interpretation"] == "meteg_or_silluq"
    assert len(units) == 1


def test_repeated_same_mark_preserved_and_linked():
    verse, _, marks, units = parse_verse(source("\u05d0\u0599\u05d1\u0599\u05c3"))
    assert verse["accent_count"] == 2
    assert len(units) == 1 and units[0]["repeat_count"] == 2
    assert len(units[0]["evidence_mark_ids"]) == 2
    assert len([m for m in marks if m["category"] == "accent"]) == 2


def test_distinct_multiple_accents_flagged_not_collapsed():
    verse, _, _, units = parse_verse(source("\u05d0\u0591\u0592\u05c3"))
    assert len(units) == 2
    assert not verse["sequence_eligible"]
    assert "multiple_distinct_accents_on_token" in verse["flags"]


def test_maqaf_keeps_lexical_tokens_and_groups():
    verse, tokens, _, _ = parse_verse(source("\u05d0\u05be\u05d1\u0591 \u05d2\u05bd\u05c3"))
    assert verse["token_count"] == 3
    assert verse["maqaf_group_count"] == 2
    assert tokens[0]["maqaf_group"] == tokens[1]["maqaf_group"]
    assert tokens[2]["maqaf_group"] != tokens[1]["maqaf_group"]


def test_vowels_and_dagesh_not_accents():
    verse, _, marks, _ = parse_verse(source("\u05d0\u05b0\u05b7\u05bc\u05c1\u05c3"))
    assert verse["accent_count"] == 0
    assert all(m["category"] != "accent" for m in marks)


def test_masora_circle_not_accent():
    verse, _, marks, _ = parse_verse(source("\u05d0\u05af\u05c3"))
    assert verse["accent_count"] == 0
    assert any(m["category"] == "masora_circle" for m in marks)


def test_paragraph_marker_not_a_word():
    verse, tokens, _, _ = parse_verse(source("\u05d0\u0591\u05c3 {\u05e4}"))
    assert verse["token_count"] == 1
    assert len(tokens) == 1


def test_markup_flag_and_original_offsets():
    verse, tokens, marks, _ = parse_verse(source('<b title="\u0592">\u05d0\u0591</b>\u05c3'))
    assert not verse["sequence_eligible"]
    assert "markup_unresolved" in verse["flags"]
    assert verse["accent_count"] == 1
    assert any(m["region"] == "masked" for m in marks)
    assert tokens[0]["start"] > 0


def test_bracketed_reading_excluded_from_sequences():
    verse, _, _, _ = parse_verse(source("[\u05d0\u0591] (\u05d1\u0592)\u05c3"))
    assert not verse["sequence_eligible"]
    assert "bracketed_reading_unresolved" in verse["flags"]


def test_orphan_accent_flagged():
    verse, _, _, _ = parse_verse(source("\u0591 \u05d0\u05c3"))
    assert "orphan_accent" in verse["flags"]


def test_missing_verse_end_flagged():
    verse, _, _, _ = parse_verse(source("\u05d0\u0591"))
    assert "nonstandard_sof_pasuq_count" in verse["flags"]


def test_two_verse_ends_not_silently_resolved():
    verse, _, marks, _ = parse_verse(source("\u05d0\u05bd\u05c3 \u05d1\u05bd\u05c3"))
    assert not verse["sequence_eligible"]
    assert not any(m["interpretation"] == "silluq_candidate" for m in marks)


def test_checksum_corruption_rejected():
    value = source("\u05d0\u0591\u05c3")
    value["raw_hebrew"] += "x"
    with pytest.raises(ValueError, match="checksum"):
        parse_verse(value)


@pytest.mark.parametrize("payload", [{"title": "Genesis", "chapters": [31, 25]}, [{"title": "Genesis", "chapters": [31, 25]}]])
def test_shape(payload):
    assert chapter_lengths(payload, "Genesis") == [31, 25]


@pytest.mark.parametrize("chapters", [[], [0], [-1], [True], [[1]], ["31"]])
def test_invalid_shapes(chapters):
    with pytest.raises(ValueError):
        chapter_lengths({"title": "Genesis", "chapters": chapters}, "Genesis")


def good_response():
    return {"ref": "Genesis 1", "warnings": [], "versions": [
        {"versionTitle": EDITIONS["tanach"], "actualLanguage": "he", "license": "Public Domain", "text": ["a", "b"]}
    ]}


def test_explicit_edition():
    assert select_version(good_response(), "tanach", "Genesis 1", 2)["versionTitle"] == EDITIONS["tanach"]


@pytest.mark.parametrize("field,value", [("versionTitle", "Wrong"), ("actualLanguage", "en"),
                                         ("license", "unknown"), ("text", ["a", ""]), ("text", ["a"])])
def test_edition_errors(field, value):
    response = good_response()
    response["versions"][0][field] = value
    with pytest.raises(ValueError):
        select_version(response, "tanach", "Genesis 1", 2)


def test_warning_rejected():
    response = good_response()
    response["warnings"] = ["missing requested version"]
    with pytest.raises(ValueError):
        select_version(response, "tanach", "Genesis 1", 2)


def test_wrong_ref_rejected():
    with pytest.raises(ValueError):
        select_version(good_response(), "tanach", "Exodus 1", 2)


def test_shared_title_structure():
    payload = {"alt_structs": {"Parasha": {"nodes": [{"sharedTitle": "Shemot", "wholeRef": "Exodus 1:1-6:1"}]}}}
    assert parashah_ranges(payload)[0]["name"] == "Shemot"


def test_cache_and_offline_integrity(tmp_path):
    hits = []

    def handler(request):
        hits.append(request)
        return httpx.Response(200, json={"ok": True})

    with SefariaClient(tmp_path, pace=0, transport=httpx.MockTransport(handler)) as client:
        assert client.get("/test")[0] == {"ok": True}
        assert client.get("/test")[0] == {"ok": True}
    assert len(hits) == 1
    with SefariaClient(tmp_path, offline=True) as client:
        assert client.get("/test")[0] == {"ok": True}
        with pytest.raises(FileNotFoundError):
            client.get("/not-cached")
    body = next(p for p in tmp_path.glob("*.json") if not p.name.endswith(".meta.json"))
    body.write_text("{}")
    with SefariaClient(tmp_path, offline=True) as client:
        with pytest.raises(ValueError, match="checksum"):
            client.get("/test")


def test_retry_429(tmp_path):
    attempts = []

    def handler(request):
        attempts.append(request)
        return httpx.Response(429, headers={"Retry-After": "1"}) if len(attempts) == 1 else httpx.Response(200, json={"ok": True})

    with patch("torah_cantillation.fetch.time.sleep"), SefariaClient(tmp_path, pace=0, transport=httpx.MockTransport(handler)) as client:
        assert client.get("/retry")[0]["ok"]
    assert len(attempts) == 2


def test_retry_delay_clamped():
    assert retry_delay("10000", 0) == 60
    assert retry_delay("0", 0) == 1


def test_parashah_ranges():
    assert in_range("Genesis 2:3", "Genesis 1:1-6:8", "Genesis")
    assert in_range("Genesis 6:8", "Genesis 1:1-6:8", "Genesis")
    assert not in_range("Genesis 6:9", "Genesis 1:1-6:8", "Genesis")
    assert in_range("Genesis 1:3", "Genesis 1:1-5", "Genesis")
    with pytest.raises(ValueError):
        in_range("Genesis 1:3", "an unknown range", "Genesis")


def test_ngrams_never_cross_verse_boundary():
    rows = [{"edition_id": "e", "representation": "literal", "reference": str(i), "eligible": True, "sequence": seq}
            for i, seq in enumerate((["a", "b"], ["c", "d"]))]
    output = ngrams(rows, 2)
    assert {tuple(r["sequence"]) for r in output} == {("a", "b"), ("c", "d")}


def test_ineligible_sequences_excluded():
    rows = [{"edition_id": "e", "representation": "literal", "reference": "x", "eligible": False, "sequence": ["a", "b"]}]
    assert ngrams(rows, 2) == []


def test_literal_and_distinct_differ():
    verse, _, marks, units = parse_verse(source("\u05d0\u0599\u05d1\u0599\u05c3"))
    rows = sequence_rows([verse], marks, units)
    assert len(rows[0]["sequence"]) == 2
    assert len(rows[1]["sequence"]) == 1


def test_entropy_and_mutual_information():
    assert entropy(["a", "a"]) == 0
    assert entropy(["a", "b"]) == 1
    assert entropy([]) == 0
    assert mutual_information([]) == 0
    assert mutual_information([["a", "b"]] * 10) == 0
