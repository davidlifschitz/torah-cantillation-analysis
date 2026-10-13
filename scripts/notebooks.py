"""Generate or execute the explanatory notebook collection against a named snapshot."""
import argparse
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

NOTEBOOKS = [
    ("01_corpus_audit", "Corpus audit", ["audit", "quality_flags"], "Check reference coverage, excluded sequences and checksums first."),
    ("02_mark_inventory", "Encoded-mark inventory", ["inventory", "all_signs", "rare_occurrences"], "Count code points, not assumed musical functions. Rare means <=20 signs per edition."),
    ("03_distributions", "Book and chapter distributions", ["books", "chapters"], "Compare counts with rates per 1,000 lexical tokens. True zeros are retained."),
    ("04_sequences", "Sequences and null model", ["bigrams", "trigrams", "transition_null"], "N-grams never cross verses. Within-verse shuffles preserve lengths and multiplicities."),
    ("05_verse_structure", "Position and verse profiles", ["positions", "verse_profiles"], "Position and entropy describe notation, not syntactic trees or musical complexity."),
    ("06_parashah_comparison", "Parashah comparison", ["parashahs"], "Membership comes from the source index, not the current reading calendar."),
    ("07_clustering", "Verse similarity", ["cluster_diagnostics", "clusters"], "K-means uses normalized proportions. Inspect silhouette and seed stability; clusters are not genres."),
    ("08_anomalies", "Unusual patterns", ["anomalies", "rare_occurrences"], "Surprise uses a model trained outside the verse's book; high surprise is not textual error."),
    ("09_edition_comparison", "Edition sensitivity", ["edition_comparison"], "A single-edition run cannot establish edition robustness. not_run does not mean no differences."),
    ("10_predictive_models", "Held-out baselines", ["model_evaluation"], "Compare uniform, unigram and bigram log loss. Hold out books intact and remove duplicated consonantal verses from training."),
    ("11_synthesis", "Evidence and limitations", ["audit", "transition_null", "model_evaluation"], "Distinguish observations, exploratory patterns and explanations requiring further evidence."),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--snapshot", default="published")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    for name, title, tables, note in NOTEBOOKS:
        setup = f'''from pathlib import Path
import json
import pandas as pd
from IPython.display import display, Markdown
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists())
SNAPSHOT = {args.snapshot!r}
REPORT = ROOT / "reports" / SNAPSHOT
assert (REPORT / "summary.json").exists(), "Run fetch, build and analyze for this snapshot first."
summary = json.loads((REPORT / "summary.json").read_text())
display(Markdown("**PILOT ONLY**" if summary["pilot"] else "Validated full reference coverage"))
print("Snapshot:", summary["snapshot"])
'''
        cells = [nbf.v4.new_markdown_cell(f"# {title}\n\n{note}\n\nComputational logic is in `src/torah_cantillation/`. These notebooks inspect generated evidence, not live API responses."),
                 nbf.v4.new_code_cell(setup)]
        for table in tables:
            cells += [nbf.v4.new_markdown_cell(f"## {table.replace('_', ' ').title()}"),
                      nbf.v4.new_code_cell(f'values = json.loads((REPORT / "tables" / "{table}.json").read_text())\nframe = pd.DataFrame(values if isinstance(values, list) else [values])\nprint("Total rows:", len(frame))\ndisplay(frame.head(40))')]
        cells += [nbf.v4.new_markdown_cell("## Interpretation\n\nCheck denominators, exclusions and edition scope. A truncated notebook display is not the complete occurrence catalog. See `summary.json` for checksums and environment versions."),
                  nbf.v4.new_code_cell('display(Markdown((REPORT / "findings.md").read_text()))')]
        notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
        for i, cell in enumerate(notebook.cells):
            cell["id"] = f"{name}-{i}"
        path = root / "notebooks" / (name + ".ipynb")
        path.parent.mkdir(exist_ok=True)
        if args.execute:
            NotebookClient(notebook, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(root)}}).execute()
        nbf.write(notebook, path)
        print(path.name, "executed" if args.execute else "created", flush=True)


if __name__ == "__main__":
    main()
