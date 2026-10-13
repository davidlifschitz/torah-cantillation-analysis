# API and encoding references

Documentation reviewed 2026-10-13. The live service may change; immutable response snapshots, not a URL alone, identify a corpus.

## Primary documentation

- Sefaria v3 text retrieval: https://developers.sefaria.org/reference/get-v3-texts
- Version discovery: https://developers.sefaria.org/reference/get-versions
- Shape and chapter lengths: https://developers.sefaria.org/reference/get-shape
- Raw index: https://developers.sefaria.org/reference/get-v2-index
- Alternate structures: https://developers.sefaria.org/docs/alternate-structures
- Getting started: https://developers.sefaria.org/reference/getting-started
- Unicode Hebrew block: https://www.unicode.org/charts/PDF/U0590.pdf
- Unicode character database: https://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt

## Acquisition contract

```bash
curl --fail --silent --show-error --get \
  'https://www.sefaria.org/api/v3/texts/Genesis.1' \
  --data-urlencode "version=hebrew|Tanach with Ta'amei Hamikra" \
  --data-urlencode 'fill_in_missing_segments=0' \
  --data-urlencode 'return_format=default'
```

`version` uses the full language name plus the exact edition title. The v3 response has a `versions` array, not the legacy API's top-level Hebrew-text shape. `return_format=default` preserves the stored representation. `fill_in_missing_segments=0` prevents borrowing text from another edition. API warnings, wrong editions, missing segments and unexpected license labels are errors.

Requesting `Genesis` does not return all of Genesis: v3 resolves a non-bottom-level reference to its first bottom-level section. The client discovers chapter lengths from `/api/shape/{book}` and fetches each chapter explicitly. It requests `/api/v2/raw/index/{book}` for `alt_structs.Parasha` ranges. Node names may use `titles` or `sharedTitle`.

Client pacing is one second per live attempt with at most five attempts. HTTP 429, transient server errors and network timeouts have bounded retry delays. Response bytes, endpoint/query parameters, timestamps, status, ETag and Last-Modified are cached. Reusing a named snapshot checks hashes. A new extraction requires a new ID when content or configuration changes.

No calendar endpoint is used for static parashah membership. No English translation is requested. `available_versions` metadata may still appear inside raw API responses and is not itself analyzed as Hebrew text.
