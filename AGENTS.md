# Instructions for contributors and coding agents

Deliver both descriptive coverage and substantive pattern discovery. Do not reduce the project to frequency charts or replace research with unexecuted placeholder notebooks.

1. Read docs/methodology.md and DATA_LICENSES.md before changing acquisition or parsing.
2. Preserve source response bytes, raw verse strings, exact edition names, hashes, offsets and provenance. Never merge source editions or enable fallback filling without a separately reviewed research design.
3. Keep encoded marks distinct from provisional functional interpretations. Do not silently classify meteg as silluq, paseq as legarmeh, repeated display signs as multiple functions, or qere/ketiv alternatives as a single reading.
4. Put reusable logic in src/. Add offline regression tests for every new parsing rule. Run ruff and pytest before committing.
5. Run notebooks top-to-bottom in a clean kernel. All published results must be calculated from a named validated snapshot. Synthetic fixtures must never appear as Torah findings.
6. Use explicit denominators, verse boundaries, held-out evaluation and stated null models. Label exploratory patterns and avoid unsupported historical or causal claims.
7. Update docs/research_log.md with questions, changes, negative results, evidence and limitations. New questions are welcome; no arbitrary cap on meaningful analyses.
8. Network acquisition is explicit and paced. Offline reproduction must not refresh data. Never commit credentials, environment files, auth headers or personal information.
9. Preserve user changes; use non-force updates and inspect conflicts. Do not publish a release, change repository access, or enable unrelated infrastructure as a side effect.
10. Report actual test, coverage, run and publication status. Do not call scaffold creation a finished study.
