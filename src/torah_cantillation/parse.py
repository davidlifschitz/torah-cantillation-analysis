"""Lossless evidence tables; conservative, explicitly provisional interpretations."""
from __future__ import annotations

import re
import unicodedata as ud
from collections import defaultdict
from pathlib import Path

from .io import canonical, digest, read_json, read_rows, safe_snapshot, write_json, write_rows

ACCENTS = set(range(0x0591, 0x05AF))
SPECIALS = {0x05AF: "masora_circle", 0x05BD: "meteg_or_silluq", 0x05BE: "maqaf",
            0x05C0: "paseq", 0x05C3: "sof_pasuq", 0x05C4: "upper_dot",
            0x05C5: "lower_dot", 0x05C6: "nun_hafukha"}
TOKEN = re.compile(r"[\u05d0-\u05ea][\u05d0-\u05ea\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]*")
MASK = re.compile(r"<[^>]*>|\{[^{}]*\}")
RULE_VERSION = "conservative-v1"


def in_range(reference: str, whole_ref: str, book: str) -> bool:
    prefix = re.escape(book) + r" (\d+):(\d+)(?:-(?:(\d+):)?(\d+))?"
    match = re.fullmatch(prefix, whole_ref)
    if not match:
        raise ValueError(f"Unsupported parashah range: {whole_ref}")
    c1, v1 = int(match[1]), int(match[2])
    c2, v2 = (int(match[3] or c1), int(match[4])) if match[4] else (c1, v1)
    position = tuple(map(int, reference.removeprefix(book + " ").split(":")))
    return (c1, v1) <= position <= (c2, v2)


def parse_verse(source: dict) -> tuple[dict, list[dict], list[dict], list[dict]]:
    raw = source["raw_hebrew"]
    if digest(raw) != source["text_sha256"]:
        raise ValueError(f"Text checksum mismatch: {source['reference']}")
    visible = list(raw)
    masked = set()
    for match in MASK.finditer(raw):
        masked.update(range(match.start(), match.end()))
        visible[match.start():match.end()] = " " * (match.end() - match.start())
    visible = "".join(visible)
    flags = []
    if "<" in raw or ">" in raw or "&" in raw:
        flags.append("markup_unresolved")
    if any(char in visible for char in "[]()"):
        flags.append("bracketed_reading_unresolved")
    if ud.normalize("NFC", raw) != raw:
        flags.append("non_nfc_source_preserved")
    if not any(ord(c) in ACCENTS for c in visible):
        flags.append("no_encoded_accents")
    tokens, marks, units = [], [], []
    position_to_token = {}
    group = 0
    previous_end = 0
    for ordinal, match in enumerate(TOKEN.finditer(visible), 1):
        if not (tokens and re.fullmatch(r"\s*\u05be\s*", visible[previous_end:match.start()])):
            group += 1
        token = {"token_id": f"{source['verse_id']}:t{ordinal}", "verse_id": source["verse_id"],
                 "edition_id": source["edition_id"], "position": ordinal,
                 "raw_token": raw[match.start():match.end()], "start": match.start(),
                 "end": match.end(), "maqaf_group": group, "rule_id": RULE_VERSION}
        tokens.append(token)
        for offset in range(match.start(), match.end()):
            position_to_token[offset] = token
        previous_end = match.end()
    punctuation = [i for i, char in enumerate(raw) if char == "\u05c3" and i not in masked]
    silluq_offset = None
    if len(punctuation) == 1 and tokens:
        final = tokens[-1]
        possible = [i for i in range(final["start"], final["end"]) if raw[i] == "\u05bd"]
        if possible and final["end"] <= punctuation[0] and not visible[final["end"]:punctuation[0]].strip():
            silluq_offset = possible[-1]
    per_token = defaultdict(lambda: defaultdict(list))
    for offset, char in enumerate(raw):
        code = ord(char)
        if code not in ACCENTS and code not in SPECIALS:
            continue
        token = position_to_token.get(offset)
        category = "accent" if code in ACCENTS else SPECIALS[code]
        interpretation = "silluq_candidate" if offset == silluq_offset else category
        mark = {"mark_id": f"{source['verse_id']}:m{offset}", "verse_id": source["verse_id"],
                "edition_id": source["edition_id"], "token_id": token["token_id"] if token else None,
                "codepoint": f"U+{code:04X}", "unicode_name": ud.name(char), "char_offset": offset,
                "category": category, "interpretation": interpretation,
                "region": "masked" if offset in masked else "text"}
        marks.append(mark)
        if category == "accent" and offset not in masked and token:
            per_token[token["token_id"]][mark["codepoint"]].append(mark["mark_id"])
    for token_id, codes in per_token.items():
        if len(codes) > 1:
            flags.append("multiple_distinct_accents_on_token")
        for code, evidence in codes.items():
            units.append({"unit_id": f"{token_id}:{code}", "verse_id": source["verse_id"],
                          "token_id": token_id, "edition_id": source["edition_id"],
                          "codepoint": code, "evidence_mark_ids": evidence,
                          "repeat_count": len(evidence), "function_class": "unassigned",
                          "interpretation_status": "provisional_token_distinct",
                          "rule_id": RULE_VERSION})
    if any(m["category"] == "accent" and m["region"] == "text" and not m["token_id"] for m in marks):
        flags.append("orphan_accent")
    if len(punctuation) != 1:
        flags.append("nonstandard_sof_pasuq_count")
    blockers = {"markup_unresolved", "bracketed_reading_unresolved", "orphan_accent",
                "multiple_distinct_accents_on_token", "nonstandard_sof_pasuq_count", "no_encoded_accents"}
    verse = {**source, "token_count": len(tokens), "maqaf_group_count": group,
             "accent_count": sum(m["category"] == "accent" and m["region"] == "text" for m in marks),
             "token_distinct_count": len(units), "flags": sorted(set(flags)),
             "sequence_eligible": not bool(set(flags) & blockers), "rule_id": RULE_VERSION}
    return verse, tokens, marks, units


def build(root: Path, snapshot: str, *, parquet: bool = False) -> dict:
    snapshot = safe_snapshot(snapshot)
    manifest = read_json(root / "data" / "manifests" / f"{snapshot}.json")
    raw_path = root / "data" / "raw" / snapshot / "verses.jsonl"
    if digest(raw_path.read_bytes()) != manifest["verse_data_sha256"]:
        raise ValueError("Raw corpus checksum mismatch")
    tables = {name: [] for name in ("verses", "tokens", "marks", "accent_units")}
    for source in read_rows(raw_path):
        parsed = parse_verse(source)
        matches = [s["name"] for s in manifest["sections"][source["book"]]
                   if in_range(source["reference"], s["whole_ref"], source["book"])]
        if len(matches) != 1:
            raise ValueError(f"Parashah membership is not unique: {source['reference']}")
        parsed[0]["parashah"] = matches[0]
        for name, value in zip(tables, parsed):
            tables[name].extend(value if isinstance(value, list) else [value])
    target = root / "data" / "processed" / snapshot
    hashes = {}
    for name, rows in tables.items():
        path = target / f"{name}.jsonl"
        write_rows(path, rows)
        hashes[name] = digest(path.read_bytes())
        if parquet:
            import pandas as pd
            pd.DataFrame(rows).to_parquet(target / f"{name}.parquet", index=False)
    provenance = {"snapshot": snapshot, "manifest_sha256": digest(canonical(manifest)),
                  "rule_version": RULE_VERSION, "unicode_version": ud.unidata_version,
                  "tables_sha256": hashes}
    write_json(target / "provenance.json", provenance)
    return validate(root, snapshot)


def validate(root: Path, snapshot: str) -> dict:
    snapshot = safe_snapshot(snapshot)
    manifest = read_json(root / "data" / "manifests" / f"{snapshot}.json")
    raw_path = root / "data" / "raw" / snapshot / "verses.jsonl"
    if digest(raw_path.read_bytes()) != manifest["verse_data_sha256"]:
        raise ValueError("Raw corpus checksum mismatch")
    path = root / "data" / "processed" / snapshot
    provenance = read_json(path / "provenance.json")
    if digest(canonical(manifest)) != provenance["manifest_sha256"]:
        raise ValueError("Manifest has changed since the build")
    tables = {}
    for name, expected in provenance["tables_sha256"].items():
        file = path / f"{name}.jsonl"
        if digest(file.read_bytes()) != expected:
            raise ValueError(f"Processed checksum mismatch: {name}")
        tables[name] = read_rows(file)
    for name, key in (("verses", "verse_id"), ("tokens", "token_id"),
                      ("marks", "mark_id"), ("accent_units", "unit_id")):
        ids = [row[key] for row in tables[name]]
        if len(set(ids)) != len(ids):
            raise ValueError(f"Duplicate {key}")
    verses = {v["verse_id"]: v for v in tables["verses"]}
    tokens = {t["token_id"]: t for t in tables["tokens"]}
    marks = {m["mark_id"]: m for m in tables["marks"]}
    expected = set()
    for edition in manifest["editions"]:
        for book, counts in manifest["shapes"].items():
            for chapter, count in enumerate(counts, 1):
                if manifest["pilot"] and chapter != 1:
                    continue
                expected.update(f"{edition}:{book}:{chapter}:{v}" for v in range(1, count + 1))
    if set(verses) != expected:
        raise ValueError("Verse coverage mismatch")
    counts = defaultdict(int)
    for mark in marks.values():
        if mark["verse_id"] not in verses or (mark["token_id"] and mark["token_id"] not in tokens):
            raise ValueError("Broken mark foreign key")
        raw = verses[mark["verse_id"]]["raw_hebrew"]
        if f"U+{ord(raw[mark['char_offset']]):04X}" != mark["codepoint"]:
            raise ValueError("Mark offset does not reconstruct source character")
        if mark["category"] == "accent" and mark["region"] == "text":
            counts[mark["verse_id"]] += 1
    for verse in verses.values():
        if digest(verse["raw_hebrew"]) != verse["text_sha256"]:
            raise ValueError("Verse text checksum mismatch")
        if counts[verse["verse_id"]] != verse["accent_count"]:
            raise ValueError("Accent totals do not reconcile")
    for token in tokens.values():
        verse = verses[token["verse_id"]]
        if verse["raw_hebrew"][token["start"]:token["end"]] != token["raw_token"]:
            raise ValueError("Token span does not reconstruct source text")
    for unit in tables["accent_units"]:
        if unit["token_id"] not in tokens or not set(unit["evidence_mark_ids"]) <= marks.keys():
            raise ValueError("Broken interpreted-unit evidence link")
        for mark_id in unit["evidence_mark_ids"]:
            mark = marks[mark_id]
            if (mark["token_id"], mark["verse_id"], mark["codepoint"]) != (unit["token_id"], unit["verse_id"], unit["codepoint"]):
                raise ValueError("Interpreted-unit evidence mismatch")
    result = {"snapshot": snapshot, "passed": True, "pilot": manifest["pilot"],
              "coverage_complete": manifest["coverage_complete"],
              "rows": {name: len(rows) for name, rows in tables.items()},
              "sequence_eligible_verses": sum(v["sequence_eligible"] for v in verses.values()),
              "edition_ids": manifest["editions"]}
    write_json(path / "validation.json", result)
    return result
