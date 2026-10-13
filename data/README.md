# Data snapshots

`raw/<snapshot>/responses/` stores original API response bytes plus metadata; `raw/<snapshot>/verses.jsonl` indexes raw verses. `manifests/<snapshot>.json` identifies the edition, requests, licenses, shapes, parashah ranges and checksums. `processed/<snapshot>/` contains JSONL evidence tables and integrity reports.

Raw/processed data are ignored by default to prevent accidental publication of unreviewed editions. Approved primary-edition archives are published by the research workflow. Keep the full archive for offline reproducibility; it is not enough to save charts. Never overwrite a named snapshot with fresh live data.
