# Generated research outputs

Each successful snapshot run writes `reports/<snapshot>/summary.json`, `findings.md`, `tables/`, `figures/`, and `index.html`. The HTML file is a local, self-contained reference explorer with generated figures; deployment to GitHub Pages is a separate publication action.

An analysis-only follow-up may use a separate directory such as `reports/<source-snapshot>-followup-<date>/`. Its summary must identify the unchanged source snapshot, exact source and result hashes, methods and parameters. The follow-up report does not replace or refresh the original snapshot report.

No numerical research findings should be added manually. Synthetic test outputs live only in temporary test directories. A pilot is explicitly labeled as a pilot. The workflow validates, reproduces and executes notebooks before committing approved primary-edition results.
