"""Explicit-edition Sefaria acquisition with verified, resumable response caches."""
from __future__ import annotations

import datetime as dt
import email.utils
import json
import time
from pathlib import Path
from urllib.parse import quote, urlencode

import httpx

from .io import canonical, digest, read_json, safe_snapshot, write_json, write_rows

BASE = "https://www.sefaria.org/api"
BOOKS = ("Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy")
EDITIONS = {
    "tanach": "Tanach with Ta'amei Hamikra",
    "mam": "Miqra according to the Masorah",
}
LICENSE_LABELS = {"tanach": {"Public Domain", "PD"}, "mam": {"CC-BY-SA"}}


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def retry_delay(value: str | None, attempt: int) -> float:
    try:
        seconds = float(value) if value else 2 ** attempt
    except ValueError:
        try:
            when = email.utils.parsedate_to_datetime(value)
            seconds = (when - dt.datetime.now(dt.timezone.utc)).total_seconds()
        except (TypeError, ValueError):
            seconds = 2 ** attempt
    return max(1.0, min(60.0, seconds))


class SefariaClient:
    def __init__(self, cache: Path, *, offline: bool = False, pace: float = 1.0,
                 transport: httpx.BaseTransport | None = None):
        self.cache = cache
        self.offline = offline
        self.pace = max(0.0, pace)
        self.http = httpx.Client(
            timeout=60, follow_redirects=True, transport=transport,
            headers={"User-Agent": "torah-cantillation-analysis/0.1 (+https://github.com/davidlifschitz/torah-cantillation-analysis)"},
        )
        self.records: dict[str, dict] = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.http.close()

    def get(self, endpoint: str, params: dict | None = None):
        if not endpoint.startswith("/") or ".." in endpoint:
            raise ValueError("Invalid endpoint")
        params = params or {}
        url = BASE + endpoint
        key = digest(url + "?" + urlencode(sorted(params.items())))
        body_path = self.cache / f"{key}.json"
        meta_path = self.cache / f"{key}.meta.json"
        if body_path.exists() or meta_path.exists():
            if not (body_path.exists() and meta_path.exists()):
                raise ValueError(f"Incomplete response cache: {key}")
            body = body_path.read_bytes()
            meta = read_json(meta_path)
            if digest(body) != meta["sha256"]:
                raise ValueError(f"Response checksum mismatch: {key}")
        else:
            if self.offline:
                raise FileNotFoundError(f"Offline cache miss: {url}")
            self.cache.mkdir(parents=True, exist_ok=True)
            for attempt in range(5):
                time.sleep(self.pace)
                try:
                    response = self.http.get(url, params=params)
                except (httpx.TimeoutException, httpx.NetworkError):
                    if attempt == 4:
                        raise
                    time.sleep(2 ** attempt)
                    continue
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt == 4:
                        response.raise_for_status()
                    time.sleep(retry_delay(response.headers.get("Retry-After"), attempt))
                    continue
                response.raise_for_status()
                body = response.content
                decoded = json.loads(body)
                if isinstance(decoded, dict) and decoded.get("error"):
                    raise ValueError(f"Sefaria API error: {decoded['error']}")
                meta = {"url": str(response.url), "parameters": params, "sha256": digest(body),
                        "retrieved_at": utcnow(), "status": response.status_code,
                        "etag": response.headers.get("etag"),
                        "last_modified": response.headers.get("last-modified")}
                body_path.write_bytes(body)
                write_json(meta_path, meta)
                break
            else:
                raise RuntimeError(f"Retries exhausted: {url}")
        self.records[key] = meta
        result = json.loads(body)
        if isinstance(result, dict) and result.get("error"):
            raise ValueError(f"Sefaria error at {url}: {result['error']}")
        return result, key


def chapter_lengths(payload, book: str) -> list[int]:
    candidates = payload if isinstance(payload, list) else [payload]
    matches = [item for item in candidates if isinstance(item, dict)
               and item.get("title", item.get("section")) == book]
    if len(matches) != 1:
        raise ValueError(f"Cannot identify shape for {book}")
    lengths = matches[0].get("chapters")
    if not isinstance(lengths, list) or not lengths or not all(
        isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in lengths
    ):
        raise ValueError(f"Unexpected chapter shape for {book}")
    return lengths


def select_version(payload: dict, edition: str, expected_ref: str, count: int) -> dict:
    if payload.get("warnings"):
        raise ValueError(f"API warnings for {expected_ref}: {payload['warnings']}")
    if payload.get("ref") != expected_ref:
        raise ValueError(f"Reference mismatch: expected {expected_ref}, got {payload.get('ref')}")
    versions = payload.get("versions", [])
    if len(versions) != 1 or versions[0].get("versionTitle") != EDITIONS[edition]:
        raise ValueError("Wrong edition returned; fallback is forbidden")
    version = versions[0]
    if version.get("actualLanguage", version.get("language")) != "he":
        raise ValueError("Requested Hebrew source was not returned")
    if version.get("license") not in LICENSE_LABELS[edition]:
        raise ValueError(f"Unreviewed license label: {version.get('license')}")
    text = version.get("text")
    if not isinstance(text, list) or len(text) != count or not all(
        isinstance(value, str) and value.strip() for value in text
    ):
        raise ValueError(f"Missing/invalid segments for {expected_ref}")
    return version


def parashah_ranges(index: dict) -> list[dict]:
    structure = index.get("alt_structs", {}).get("Parasha", {})
    result = []

    def walk(node):
        if node.get("wholeRef"):
            name = next((title["text"] for title in node.get("titles", [])
                         if title.get("lang") == "en" and title.get("primary")), None)
            name = name or node.get("sharedTitle")
            if name:
                result.append({"name": name, "whole_ref": node["wholeRef"]})
        for child in node.get("nodes", []):
            walk(child)

    walk(structure)
    if not result:
        raise ValueError("Parasha alternate structure is missing; do not invent boundaries")
    return result


def acquire(root: Path, snapshot: str, *, editions: tuple[str, ...] = ("tanach",),
            offline: bool = False, pilot: bool = False) -> dict:
    snapshot = safe_snapshot(snapshot)
    raw = root / "data" / "raw" / snapshot
    manifest_path = root / "data" / "manifests" / f"{snapshot}.json"
    if manifest_path.exists():
        existing = read_json(manifest_path)
        if existing["editions"] != list(editions) or existing["pilot"] != pilot:
            raise ValueError("Snapshot configuration is immutable; choose a new snapshot ID")
    verses, sources, shapes, sections = [], [], {}, {}
    with SefariaClient(raw / "responses", offline=offline) as client:
        for book in BOOKS:
            payload, _ = client.get("/shape/" + quote(book))
            shapes[book] = chapter_lengths(payload, book)
            index, _ = client.get("/v2/raw/index/" + quote(book))
            sections[book] = parashah_ranges(index)
            for edition in editions:
                for chapter, expected_count in enumerate(shapes[book], 1):
                    if pilot and chapter != 1:
                        continue
                    ref = f"{book} {chapter}"
                    payload, key = client.get("/v3/texts/" + quote(f"{book}.{chapter}"), {
                        "version": "hebrew|" + EDITIONS[edition],
                        "fill_in_missing_segments": "0", "return_format": "default",
                    })
                    version = select_version(payload, edition, ref, expected_count)
                    meta = {k: version.get(k) for k in (
                        "versionTitle", "versionSource", "license", "versionNotes", "actualLanguage")}
                    sources.append({"book": book, "chapter": chapter, "edition_id": edition,
                                    "request_id": key, **meta})
                    for number, text in enumerate(version["text"], 1):
                        reference = f"{book} {chapter}:{number}"
                        verses.append({"verse_id": f"{edition}:{book}:{chapter}:{number}",
                                       "edition_id": edition, "book": book, "chapter": chapter,
                                       "verse": number, "reference": reference, "raw_hebrew": text,
                                       "text_sha256": digest(text), "request_id": key})
                    print(f"Fetched {edition}: {ref} ({expected_count} verses)", flush=True)
        manifest = {"schema_version": 1, "snapshot": snapshot, "editions": list(editions),
                    "pilot": pilot, "coverage_complete": not pilot, "shapes": shapes,
                    "sections": sections, "sources": sources, "requests": client.records,
                    "verse_count": len(verses),
                    "verse_data_sha256": digest("\n".join(canonical(v) for v in verses) + "\n")}
    if manifest_path.exists() and manifest != read_json(manifest_path):
        raise ValueError("An existing snapshot would change; select a new snapshot ID")
    write_rows(raw / "verses.jsonl", verses)
    write_json(manifest_path, manifest)
    return manifest
