# Source-text licensing and attribution

The repository's MIT license applies to original software. It is not a blanket license for Sefaria's library, third-party texts, notebook quotations or derivative corpora.

## Primary acquisition

- Exact edition: **Tanach with Ta'amei Hamikra**.
- Distributor/API host: Sefaria.
- Upstream source reported by Sefaria: `http://www.tanach.us/Tanach.xml`.
- Expected Sefaria license label: `Public Domain` (or `PD`).

The client verifies the license label in every chapter response and saves the returned `versionTitle`, `versionSource`, `versionNotes` and license with the acquisition manifest. A different or missing license label stops the run for review. The label is recorded as source metadata, not an independent legal determination. Credit both Sefaria and the upstream transcription project.

## Optional comparison edition

- Exact edition: **Miqra according to the Masorah** (MAM).
- Upstream project: Hebrew Wikisource, Miqra al pi ha-Masorah.
- Expected Sefaria label: `CC-BY-SA`.

This unversioned API label is not enough to invent a specific Creative Commons license version. Before publicly redistributing a MAM snapshot or text-bearing derived dataset, verify the actual upstream license/version, attribution and share-alike requirements and add them here. Until that review is complete, the automatic publication workflow fetches **only the public-domain-labeled primary edition**. Local `--comparison` processing is supported, but local files should not be blindly uploaded.

## Publication rules

Keep code, source texts and derived datasets distinguishable. Preserve original source metadata, retrieval timestamps, hashes and notices. Record modifications to redistributed text. Do not relabel third-party material as MIT. A new edition requires an explicit license review; an unknown license is a publication blocker.

Resources:
- https://help.sefaria.org/hc/en-us/articles/18490043237148-How-to-Find-and-Understand-Licensing-Information
- https://developers.sefaria.org/reference/get-versions
- https://www.tanach.us/
- https://he.wikisource.org/wiki/משתמש:Dovi/מקרא_על_פי_המסורה
