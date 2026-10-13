# Research notebooks

Run `uv run python scripts/notebooks.py --snapshot <id>` to generate the eleven notebook files. Add `--execute` after building and analyzing the same snapshot to execute every notebook in a clean kernel. The research workflow does this automatically and commits successfully executed notebooks.

01 corpus audit; 02 mark inventory; 03 distributions; 04 sequences; 05 verse structure; 06 parashah comparison; 07 clustering; 08 anomalies; 09 edition comparison; 10 predictive baselines; 11 synthesis.

Do not mistake an unexecuted notebook for a computed finding. A single-edition run explicitly marks comparison results as not run. Analytical logic lives in the tested package, while notebooks explain and inspect the generated evidence.
