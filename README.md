# Functional-evidence statements in ClinVar

**How often do laboratories say a functional experiment exists — and how often do they say one
is missing?** A count across 32,569 ClinVar submissions for a 13-gene RASopathy panel, and an
account of what the count could not settle.

The full write-up is [`report.md`](report.md). This README says what is in the repository, how to
verify it, and — the part that matters most — how a curator can take part.

---

## The finding, in four lines

- Statements that functional evidence **exists** and statements that it is **absent** occur at
  about the same rate: **1,216 against 1,512**. That aggregate is close to meaningless, because a
  single submitter files 62% of the absence statements.
- Per laboratory it is not symmetric. Of the **26** laboratories that file at least 30
  submissions and make at least one claim about functional evidence, **19 never once record an
  absence**. The median laboratory files zero absence statements per claim.
- The asymmetry is structural rather than careless. **PS3** gives a laboratory a compact,
  machine-readable way to assert that an assay exists — **147** submissions here assert it through
  the code alone, with no prose sentence doing so. There is no counterpart for having searched and
  found nothing: that takes free text, and **32.4%** of submissions carry no comment field at all.
  So a missing PS3 carries no information — the laboratory may have looked and found nothing, or
  never looked.
- A blind re-read of 50 submissions put reader agreement at **40.4%** (Cohen's κ = 0.104),
  concentrated in one class: separating *"no functional studies have been performed"* from *"not
  reported in the literature"*. Those are PS3 and PS4. Every figure derived from the three classes
  should be read with that beside it.

---

## How the labels were made, and why that matters

**The 450 validation labels in [`labels/`](labels) were produced by a language model adjudicating
each submission against a written rubric. No human curator read them.**

That is the limitation this work is most exposed to, so it is stated here and not only in the
report. The rubric, every verdict and the free-text reasoning behind each one are published, so a
reader can disagree line by line rather than take the classification on trust — but disagreeing
line by line is work, and nobody has done it. The blind re-read described below is the only human
reading anywhere in this work, and it was done by the author, who is not a trained variant
curator. One untrained reader is a weak test. It is also the only test these labels have ever had.

That is the whole reason for the section that follows.

---

## Take part: read fifty submissions and score your own reading

If you curate variants professionally, an hour of your reading is worth more to this than
anything further I can compute. A notebook in this repository displays fifty ClinVar submissions,
you type fifty characters, and it scores your reading against two others: the automated
adjudication, and the author's.

**The second comparison is the one worth having.** If two human readers agree with each other far
more than either agrees with the automated adjudication, the instability is in the adjudication.
If they do not, it is in the category itself — and that is worth knowing before anyone writes a
specification around it. This work cannot settle which, because it has only one reader.

Nothing is uploaded anywhere. The notebook runs offline in about a minute and writes its results
next to itself.

### Step by step

You do not need to have opened a Jupyter notebook before.

**1. Install Python and Jupyter.** Install Python 3 from
[python.org](https://www.python.org/downloads/) if you do not already have it. Then open a
terminal — Command Prompt on Windows, Terminal on macOS — and run:

```bash
pip install pandas numpy notebook
```

**2. Get this repository.** Either clone it:

```bash
git clone https://github.com/Fernandosr85/clinvar-functional-evidence-asymmetry.git
```

or use the green **Code** button at the top of this page → **Download ZIP**, and unzip it.

**3. Open the notebook.** In the terminal, change into that folder and run:

```bash
jupyter notebook notebooks/blind_interrater_check.ipynb
```

A browser tab opens showing the notebook: a column of text blocks and grey code blocks. You run a
code block by clicking on it and pressing **Shift+Enter**.

**4. One-time fix — tell it where the labels are.** This notebook is committed exactly as it was
executed, on a platform where the label files are an attached dataset, so its path points there
rather than at this repository. It has not been edited after its run, which means you have to
edit one line. In the **first code block**, find:

```python
BASE = Path("/kaggle/input/datasets/fernandosr85/clinvar-claim-audit-labels")
```

and change it to:

```python
BASE = Path("../labels")
```

Run that block with Shift+Enter. It should print `450 labelled rows, from 5 samples`. It then
draws the same fifty rows every time, from a fixed seed — the draw was checked against the
published `labels/blind_comparison.csv` and reproduces it in the same order.

**5. Read the fifty submissions.** Run the next two code blocks. They render the fifty
submissions as numbered cards, twenty-five at a time, with assay vocabulary highlighted in red,
prediction vocabulary in blue and absence wording in amber. The highlighting is a reading aid and
decides nothing: several of the hardest rows carry experiment vocabulary and are still *neither* —
a vendor model citing in-vitro data, an and/or list that never says which was done, or an assay
performed on a neighbouring variant.

For each submission, decide which of these it is doing:

| | | |
|---|---|---|
| `c` | **claim** | says an experiment was performed, bearing on **this** variant |
| `d` | **denial** | says such evidence is absent, lacking, or unconfirmed |
| `n` | **neither** | a predictor score, a vendor model, a structural inference, a clinical observation, or silence on the question |
| `?` | **unsure** | the text does not decide it |

Rows where either reader answers `?` are counted separately rather than scored as disagreements,
since they are disagreements about whether the text decides at all.

**6. Replace one string with your fifty verdicts.** In the code block below the cards, find:

```python
MY_READ = AUTHOR_READ
```

and replace it with your own fifty characters, in reading order. Spaces and line breaks are
ignored, so group them however is easiest to keep your place:

```python
MY_READ = """
cndcn ndccd nnncd dcnnc ccdnn
ndccd cnnnd dccnn cnndc ddncc
"""
```

Leave the `AUTHOR_READ` string above it alone. It is kept separate precisely so that your reading
can be scored against it instead of overwriting it.

**7. Run the whole notebook.** From the menu: **Kernel → Restart & Run All**. Two scored tables
print at the bottom — your reading against the adjudicator, and your reading against the author's
— each with a confusion matrix, observed agreement with a 95% interval, chance agreement computed
from the marginals, Cohen's κ, and agreement broken down by class. Every row where you disagreed
with the adjudicator is printed with its text so you can look again. All three readings are saved
side by side to `blind_comparison.csv`.

If you are willing to share the outcome, open an issue or a pull request with your fifty
characters. A second trained reading is the thing this work is missing.

### If you would rather read away from a screen full of code

Step 4 also writes `blind_read.csv` — the fifty submissions with an empty `my_verdict` column —
which opens in any spreadsheet. Nothing reads that file back in: the string in the notebook is the
reading of record, so that it lives in the notebook and anyone can re-check it later.

---

## What is in this repository

```
report.md                                  the full write-up
notebooks/
  panel_classification.ipynb               classifies 32,569 submissions — the executed run
  blind_interrater_check.ipynb             the 50-submission blind read — the executed run
labels/
  panel_claims_audit_sample130_rev.csv     130 adjudicated submissions   TRAINING
  panel_claims_v2_heldout_110_rev.csv      110 adjudicated submissions   TRAINING
  panel_claims_v3_heldout_90_rev.csv        90 adjudicated submissions   EVALUATION
  panel_claims_v4_negatives_60.csv          60 negative-class sample     SPENT
  panel_claims_v5_negatives_60.csv          60 negative-class sample     SPENT
  blind_comparison.csv                      50 rows, three readings side by side
results/2026-09-14/                        the frozen snapshot, plus run_manifest.json
```

Each label file carries the classifier's output, the adjudicated verdict, and a free-text reason
for that verdict.

The role matters more than the count. A sample stops being held out the moment a pattern is
written from one of its rows, and scoring it afterwards measures the repair rather than the
classifier. **Only the 90-row set has never had a pattern written from it.** The accuracy to
quote — 97% precision for claims, 100% for denials — is that one; it sits in
`results/2026-09-14/accuracy_by_sample.csv` next to the training-fit figures so the gap is visible
rather than hidden.

---

## The frozen snapshot

`results/2026-09-14/` holds the derived tables from the run of **14 September 2026**, which is the
run every figure in `report.md` comes from. ClinVar is a live resource: re-running the notebook
against a later release produces different counts, which is why these tables are read out of the
executed notebook rather than regenerated.

| file | what it is |
|---|---|
| `summary.json` | the headline counts, as the run printed them |
| `by_gene.csv` | all 13 genes, submission-weighted and laboratory-weighted rates |
| `by_laboratory_top20.csv` | the 20 most active submitters — the source of Table 2 in the report |
| `accuracy_by_sample.csv` | precision and recall per sample, evaluation and training fit alike |
| `regression_tests.csv` | the 24 classifier probes and the verdict each is required to give |
| `optional_group_audit.csv` | optional regex groups that hold a meaning-bearing word |
| `adjective_insertion_audit_top12.csv` | positions where an inserted adjective breaks a branch |

The last two are the test that would have caught the original error. Version 1 of this analysis
reported **5.9 absence statements per claim**. Its denial pattern contained
`(has|have) not been (functionally )?(characterized|studied|reported)`, and because `functionally`
was optional it fired on *"has not been reported in the literature in individuals affected
with…"* — a statement about case reports, PS4 territory, not about experiments at all. That single
alternative produced 87.7% of all denial matches, and the word never appeared in one of them. The
corrected figure is 1.24 and has not moved across six audits.

### Verifying it

Every file in `results/`, both notebooks and all six label files are hashed in
`results/2026-09-14/run_manifest.json`. Save this as `verify.py` in the repository root and run
`python verify.py`:

```python
import hashlib, io, json

m = json.load(io.open("results/2026-09-14/run_manifest.json", encoding="utf-8"))
bad = 0
for e in m["files"] + m["inputs"] + m["notebooks"]:
    h = hashlib.sha256(io.open(e["file"], "rb").read()).hexdigest()
    ok = h == e["sha256"]
    bad += not ok
    print(("ok   " if ok else "BAD  ") + e["file"])
print("%d file(s) checked, %d mismatch(es)" % (
    len(m["files"]) + len(m["inputs"]) + len(m["notebooks"]), bad))
```

`.gitattributes` marks `results/**`, `labels/**` and `*.ipynb` as `-text`, so a checkout on
Windows with `core.autocrlf=true` cannot rewrite line endings underneath the hashes. Verification
was run in a fresh clone with that setting before this repository was published.

### What the snapshot does not let you check

Being straight about the boundary is cheaper than being caught at it.

- **`by_laboratory_top20.csv` is 20 rows of the 46 over threshold, out of 278 submitters.** The
  executed notebook printed only the top 20, and the full `by_submitter.csv` it wrote at run time
  was not retained. Every row of Table 2 in the report is inside those 20, so the report is
  checkable against it; a reader who wants the other 258 has to re-run the notebook and will get a
  later ClinVar snapshot.
- **The per-submission table is not here.** `classified.csv` is 32,569 rows and was not retained
  either. Figures computed straight from it — the 44 variants carrying both a claim and an absence
  statement from different submitters, and the 2,523-row and/or block — cannot be verified from
  this repository alone.
- **Nothing here establishes that any claim is true.** That needs the cited publications read, and
  a feasibility check found only 26% of the PMIDs behind these claims have open full text.

### Known inconsistencies, listed rather than tidied

The notebooks are committed as executed and `report.md` as written, so a few stale figures survive
in their prose. They are listed here rather than quietly corrected, because editing a notebook
after its run is the failure this repository is organised against.

- **The snapshot date.** `report.md` and this folder name both say the ClinVar data was retrieved
  on **14 September 2026**. The papermill block embedded in `panel_classification.ipynb` records
  the executed run as **2026-09-11T02:38:40Z to 02:41:35Z**, and that run is the one every table
  in `results/` was read out of. The machine-attested date is the 11th. `run_manifest.json` carries
  both.
- `panel_classification.ipynb` is headed **Version 6** while the `summary.json` that same run
  wrote records `"version": 5`.
- Its header says **155** submissions assert functional evidence through the bare code. The report
  says 147, and 147 is the figure to use.
- Its limitations section quotes **1,167 claims** and a ratio of **1.18**, from an earlier run.
  The run committed here counted 1,216 claims and 1,512 denials — a ratio of 1.24.
- Its section 9 prints *"Across 26 laboratories with at least 30 submissions"*. 46 laboratories
  clear that threshold; 26 of them make at least one claim and therefore have a ratio at all. The
  `summary.json` in `results/` records both numbers and names the denominator explicitly.

None of these touch the tables in `results/`, which come from the run itself rather than from its
prose.

---

## Running the classifier notebook

`notebooks/panel_classification.ipynb` is self-contained. Run from the repository root it finds
the label files in `labels/` by itself, downloads ClinVar's `submission_summary.txt.gz` (388 MB)
if it is not already present, and writes its tables into `panel_claims_v2/`.

That download is deliberately untracked. A copy fetched today is a different snapshot from the one
behind `results/2026-09-14/`, and passing one off as the other is the provenance failure this
repository is built to avoid.

---

## Related work

[**rasopathy-evidence-audits**](https://github.com/Fernandosr85/rasopathy-evidence-audits) — the
companion repository. Same gene panel, different subject: it asks whether the *evidence* behind a
classification holds up — whether a clinical variant is matched to the right multiplexed assay at
all (PS3/BS3), and whether the reference data support the evidence strength being assigned
(PP3/BP4). This repository asks something prior to both: whether a statement about functional
evidence is recorded in ClinVar at all, and whether the category is stable enough to count.

[**rasopathy-functional-evidence-atlas**](https://github.com/Fernandosr85/rasopathy-functional-evidence-atlas)
— the curation audit those two grew out of.

## Citing

Rodrigues, F. dos S. (2026). *There is a code for finding functional evidence, and none for not
finding it.* https://github.com/Fernandosr85/clinvar-functional-evidence-asymmetry

## License

CC0. ClinVar submission records remain subject to the terms of that resource.
