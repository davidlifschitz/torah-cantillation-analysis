# Contributing

Open a research-question or bug issue with a precise reference, edition and snapshot. For a parsing change, show the raw characters/code points, cite a primary linguistic or edition source, describe the proposed rule, and add a regression test.

Development setup: `uv sync --locked --extra dev` after the initial lock exists. Run `uv run ruff check src tests scripts` and `uv run pytest -q`. The tests require no Sefaria network access. Keep computational logic in `src/` and explanatory analysis in notebooks. Use a pull request for substantive changes.

A research contribution should state its question, representation, denominator, exclusions, comparison model, results, limitations and source references. Include negative results. Domain review is particularly useful for qere/ketiv, repeated prepositive/postpositive accents, meteg/silluq, paseq/legarmeh and dual-accented passages.

Do not publish new source-text editions before their licenses have been reviewed. Do not commit secrets or large unreviewed downloads. Source API credentials are not needed for public reads.
