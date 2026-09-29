# The notebook's cells, as standalone files

These are the code cells of [`../notebooks/one_paper_two_readings.ipynb`](../notebooks/one_paper_two_readings.ipynb),
extracted verbatim from the stored run of 26–29 September 2026. Each carries the SHA-256 of
its own body so it can be diffed against the notebook.

**None of them runs on its own.** They are notebook cells: they execute in order, in one
kernel, and cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
Each file's header states what it expects to already exist. To reproduce the analysis, run
the notebook — these files are here to be read, diffed and quoted.

| File | Section | Expects in the kernel |
| --- | --- | --- |
| `01_bibliography_overlap_diagnostic.py` | 1 | `subs`, `classify` |
| `02_citation_asymmetry_check.py` | 2 | `work` |
| `03_i437t_citation_sets.py` | 3 | `work` |
| `04_citation_sentence_attribution.py` | 4 | `work`, the classifier's regexes, `cited_pmids` |
| `05_inspect_loose_cases.py` | 5 | `cit`, `flags` |
| `06_published_pipeline_impact.py` | 6 | `subs`, `classify`, `CLAIM`, `DENIAL` |
| `07_robustness_figures.py` | 7 | nothing — the measured values are constants |

The notebook's first code cell is the Kaggle boilerplate that lists `/kaggle/input`. It is
not analysis and is not extracted here, which is why the numbering starts at 01.
