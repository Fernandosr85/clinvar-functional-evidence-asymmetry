# 01_bibliography_overlap_diagnostic.py
#
# Section 1 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `subs`, `classify`
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 03feaed33ada38154acb02373e46605be95c7a758513f54f0edbb6a7dd385087

"""
Feasibility diagnostic for an Interpretation-Divergence-under-Fixed-Evidence
study, over the 13-gene RASopathy panel.

Run this BEFORE computing any divergence metric. It answers one question:
is "two submitters citing the same evidence" common enough, and independent
enough, to support a rate — or is it a case series?

WHERE THIS BELONGS
    Appendix cell for the classifier notebook (panel_functional_claims_v6).
    It needs `subs` and `classify`, built by that notebook's first four code
    cells. If the kernel is empty it bootstraps itself by executing those
    cells from a copy of that notebook found on disk — on Kaggle, attach it
    with Add Input → Notebooks. Set BOOTSTRAP = False to forbid that.

    Bootstrapping re-executes the real cells rather than reimplementing them.
    A second copy of the classifier would drift from the validated one and
    the numbers would stop matching the study.

    The bootstrap must never execute THIS cell; two guards below make that
    impossible. See the comment on _CELL_SIGNATURE.

WHAT IT REUSES, AND WHY IT DOES NOT RECOMPUTE
    After the fourth code cell, `subs` already carries `text` (Description +
    ExplanationOfInterpretation, placeholder-stripped) and the boolean flags
    `claim` / `denial`. This cell reads those columns instead of re-deriving
    them, so the label basis is identical to the published figures.
    Rebuilding the text here would silently classify a different string.

    Note the contract: the classifier returns {"claim", "denial",
    "prediction", "lit_absence"} — booleans, not a label. The four strata
    below are derived from the claim/denial pair, matching POP_STRATA in the
    notebook.

OUTPUT, in order of what it decides
    1. coverage     — how many submissions cite anything at all
    2. pairs        — variants where two submitters cite an equivalent set,
                      counted at BOTH the variant level and the submitter-pair
                      level, because the clustering is what decides whether a
                      panel-wide rate means anything
    3. divergence   — reported at both levels, so the inflation is visible
    4. propagation  — independently curated bibliographies, or inherited ones?
    5. sensitivity  — the headline must not rest on one arbitrary threshold

    Printing is deliberately terse. The full pair-level data goes to
    bibliography_pairs.csv and divergence_by_submitter_pair.csv, and the
    bootstrapped cells' own output is kept in `_bootstrap_log`.
"""

import contextlib
import glob
import io
import itertools
import json
import os
import re

import pandas as pd

# --------------------------------------------------------------------------
# Parameters. MIN_CITES is the one that matters: two submissions each citing a
# single identical PMID score Jaccard 1.0, a far weaker control than the 11-of-11
# seen on SOS1 VCV000045345. Section 5 sweeps both; do not report one cell of it.
# --------------------------------------------------------------------------
MIN_CITES = 3
JACCARD_EQUIV = 0.80

BOOTSTRAP = True
BOOTSTRAP_CELLS = 4          # cells 0-3: constants, regexes, classifier, load

# --------------------------------------------------------------------------
# Finding the classifier notebook.
#
# Match on content, not filename: the notebook is saved locally as
# panel_functional_claims_v6.ipynb and on Kaggle as the slug of its title, so
# a filename match picks the wrong copy or none. The markers below appear
# together only in that classifier. Verified across six downloaded Kaggle
# copies: code cells 0-2 are byte-identical in all of them, and cell 3 differs
# only in the stratum-weighting fix, so any copy bootstraps to the same
# contract.
#
# The marker strings are ASSEMBLED here and never appear as literals in this
# cell. Written out in full, they made this cell match its own marker list:
# the newest "classifier" on disk became the notebook containing this cell,
# and the bootstrap exec'd the bootstrapper. Kaggle hits that the moment Save
# & Run All writes /kaggle/working/__notebook__.ipynb — RecursionError, not at
# run time but at save time. The description of a thing was read as the thing;
# same failure as reading a domain annotation as the molecule.
# --------------------------------------------------------------------------
BOOTSTRAP_MARKERS = ("def " + "load_panel", "def " + "classify(",
                     "LITERATURE" + "_ABSENCE", "VENDOR" + "_MODEL")

# Second guard, independent of the first: any code cell whose source contains
# this identifier belongs to this appendix and is never executed by the
# bootstrap. The identifier is its own signature, so it survives editing and
# keeps the documented "paste this cell at the end of the classifier notebook"
# arrangement safe.
_CELL_SIGNATURE = "_CELL" + "_SIGNATURE"

# Third guard: a re-entry flag. It lives in os.environ rather than in globals()
# because the bootstrap exec's into globals(), so a global sentinel could be
# reset by the very cell it is meant to stop.
_BOOTSTRAP_FLAG = "CLINVAR_BOOTSTRAP_ACTIVE"

# --------------------------------------------------------------------------
# Submitters write citation lists two ways, and a pattern that handles only one
# of them silently undercounts — which would make sets look disjoint and inflate
# apparent divergence, i.e. manufacture the result the hypothesis predicts:
#   Dasa    "(PMID: 21387466; PMID: 24803665; PMID: 30541462)"   anchor each
#   GeneDx  "(PMID: 24803665, 30541462, 30039904, 24451042)"     anchor once
# A naive r"PMID:?\s*(\d{7,8})" returns 3 and 1. Anchor on PMID, then consume the
# whole delimited run. The structural test below fails if this regresses.
# --------------------------------------------------------------------------
PMID_BLOCK = re.compile(
    r"PMIDs?\s*:?\s*(\d{7,9}(?:\s*(?:,|;|and|&|/)\s*(?:PMIDs?\s*:?\s*)?\d{7,9})*)",
    re.I)
PMID_NUM = re.compile(r"\d{7,9}")


def cited_pmids(text):
    out = set()
    for m in PMID_BLOCK.finditer(text or ""):
        out.update(PMID_NUM.findall(m.group(1)))
    return frozenset(out)


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _test_pmid_parsing():
    """Both list styles must yield the same set; a year is never a PMID.

    Silent on success — the assertions are the report.
    """
    cases = [
        ("(PMID: 24803665, 30541462, 30039904, 24451042, 21387466)",
         {"24803665", "30541462", "30039904", "24451042", "21387466"}),
        ("(PMID: 21387466; PMID: 24803665; PMID: 30541462; PMID: 30039904; "
         "PMID: 24451042).",
         {"21387466", "24803665", "30541462", "30039904", "24451042"}),
        ("reported in 2018 and 2021 by several groups", set()),
        ("PMIDs 12628188 and 17143282", {"12628188", "17143282"}),
        ("no citation here", set()),
    ]
    for text, want in cases:
        got = set(cited_pmids(text))
        assert got == want, f"PMID parsing broke on {text!r}: {got} != {want}"
    assert cases[0][1] == cases[1][1], "the two styles must agree"


_test_pmid_parsing()


# --------------------------------------------------------------------------
# Bootstrap + preflight.
# --------------------------------------------------------------------------
def _notebook_code(path):
    """Code cells of a notebook, with this appendix's own cells removed.

    Returns None if the file is not a notebook. `source` is a string in some
    notebooks and a list of lines in others; both are normalised here.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            nb = json.load(fh)
    except Exception:
        return None
    cells = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        src = c.get("source", "")
        if not isinstance(src, str):
            src = "".join(src)
        if _CELL_SIGNATURE in src:
            continue                     # this appendix — never bootstrap it
        cells.append(src)
    return cells


def _find_classifier_notebook():
    """Newest .ipynb whose remaining code carries every marker."""
    seen, found = set(), []
    for pattern in ("/kaggle/input/**/*.ipynb", "/kaggle/working/**/*.ipynb",
                    "./**/*.ipynb"):
        for p in glob.glob(pattern, recursive=True):
            rp = os.path.realpath(p)
            if rp in seen or not os.path.isfile(rp):
                continue
            seen.add(rp)
            code = _notebook_code(rp)
            if not code:
                continue
            src = "\n".join(code)
            if all(m in src for m in BOOTSTRAP_MARKERS):
                found.append((os.path.getmtime(rp), rp, code))
    if not found:
        return None, None
    found.sort(reverse=True)
    return found[0][1], found[0][2]


def _label(path):
    """Kaggle names every notebook __notebook__.ipynb; show its directory."""
    return os.path.join(os.path.basename(os.path.dirname(path)),
                        os.path.basename(path))


def _bootstrap():
    if os.environ.get(_BOOTSTRAP_FLAG):
        raise RuntimeError(
            "bootstrap re-entered — the notebook selected for bootstrapping "
            "contains this appendix cell, which should have been filtered by "
            "_CELL_SIGNATURE. Check that both guards above are intact.")
    path, code = _find_classifier_notebook()
    if path is None:
        raise RuntimeError(
            "no notebook carrying the classifier was found under "
            "/kaggle/input, /kaggle/working or the working directory. On "
            "Kaggle the running notebook is not on disk, so attach the "
            "classifier notebook as an input (Add Input → Notebooks), or "
            "paste this cell at the END of that notebook instead — then "
            "`subs` and the classifier already exist and no bootstrap is "
            "needed.")
    os.environ[_BOOTSTRAP_FLAG] = "1"
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            for i, src in enumerate(code[:BOOTSTRAP_CELLS]):
                exec(compile(src, f"{_label(path)}[code cell {i}]", "exec"),
                     globals())
    except Exception:
        print(buf.getvalue()[-2000:])    # the suppressed output explains it
        raise
    finally:
        os.environ.pop(_BOOTSTRAP_FLAG, None)
        globals()["_bootstrap_log"] = buf.getvalue()
    print(f"bootstrap: code cells 0-{BOOTSTRAP_CELLS - 1} of {_label(path)} "
          f"({len(buf.getvalue().splitlines())} lines of their output held in "
          "_bootstrap_log)")


def _preflight():
    """Silent on success. Every check below failed at least once in drafting."""
    if "subs" not in globals() or "classify" not in globals():
        missing = [n for n in ("subs", "classify") if n not in globals()]
        if not BOOTSTRAP:
            raise RuntimeError(
                f"not defined in this kernel: {', '.join(missing)}. Run the "
                "first four code cells of the classifier notebook, or set "
                "BOOTSTRAP = True.")
        _bootstrap()

    df = globals()["subs"]
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"`subs` is a {type(df).__name__}, expected a DataFrame")

    required = {"VariationID", "Submitter", "gene", "DateLastEvaluated"}
    absent = required - set(df.columns)
    if absent:
        raise KeyError(f"`subs` is missing {sorted(absent)}. "
                       f"Present: {list(df.columns)}")

    # The classifier returns booleans, not a label. Assert the real contract:
    # an earlier draft of this cell assumed a "label" key and its own test
    # agreed with it, because the test's stub was written from the same
    # assumption.
    probe = globals()["classify"]("functional studies demonstrate a damaging effect")
    if not isinstance(probe, dict) or "claim" not in probe or "denial" not in probe:
        raise TypeError("the classifier must return a dict with 'claim' and "
                        f"'denial' keys; got {probe!r}")

    return {"text", "claim", "denial"} <= set(df.columns)


_have_flags = _preflight()


# --------------------------------------------------------------------------
# One row per submission: who, when, what they cited, what they asserted.
# --------------------------------------------------------------------------
work = subs.copy()

if not _have_flags:
    # Fallback only. Mirrors cell 3's basis exactly: Description joined with
    # ExplanationOfInterpretation, ClinVar's "-" placeholder treated as empty.
    ph = re.compile(r"^\s*[-–—.·]?\s*$")

    def _blank_local(s):
        s = s.fillna("").astype(str)
        return s.mask(s.str.match(ph), "")

    txt = _blank_local(work["Description"])
    if "ExplanationOfInterpretation" in work.columns:
        txt = txt + " " + _blank_local(work["ExplanationOfInterpretation"])
    work["text"] = txt.str.strip()
    flags = work["text"].apply(classify).apply(pd.Series)
    for c in ("claim", "denial"):
        work[c] = flags[c]


def _stratum(row):
    if row["claim"] and row["denial"]:
        return "both"
    if row["claim"]:
        return "claim"
    if row["denial"]:
        return "denial"
    return "neither"


work["label"] = work.apply(_stratum, axis=1)
work["pmids"] = work["text"].map(cited_pmids)
work["n_cites"] = work["pmids"].map(len)
work["date"] = pd.to_datetime(work["DateLastEvaluated"], errors="coerce",
                              format="mixed")


def _counts(vc):
    return "  ".join(f"{vc.get(k, 0):,} {k}"
                     for k in ("claim", "denial", "both", "neither"))


n_sub = len(work)
n_any = int((work.n_cites > 0).sum())
n_min = int((work.n_cites >= MIN_CITES).sum())
sizes = work.loc[work.n_cites > 0, "n_cites"]

print("1. COVERAGE")
print(f"  submissions in panel        : {n_sub:,}")
print(f"    labels                    : {_counts(work.label.value_counts())}")
print(f"  citing >= 1 PMID            : {n_any:,} ({100*n_any/n_sub:.1f}%)")
print(f"    labels                    : "
      f"{_counts(work.loc[work.n_cites > 0, 'label'].value_counts())}")
print(f"  citing >= {MIN_CITES} PMIDs           : {n_min:,} ({100*n_min/n_sub:.1f}%)")
print(f"  set size where non-zero     : median {sizes.median():.0f}, "
      f"90th pct {sizes.quantile(.9):.0f}, max {sizes.max():.0f}")

# --------------------------------------------------------------------------
# Pair submissions within each variant.
# --------------------------------------------------------------------------
elig = work[work.n_cites >= MIN_CITES]
rows = []
for vid, grp in elig.groupby("VariationID", sort=False):
    if len(grp) < 2:
        continue
    recs = grp.to_dict("records")
    for a, b in itertools.combinations(recs, 2):
        if a["Submitter"] == b["Submitter"]:
            continue
        j = jaccard(a["pmids"], b["pmids"])
        if j < JACCARD_EQUIV:
            continue
        first, second = sorted([a, b],
                               key=lambda r: (pd.isna(r["date"]), r["date"]))
        rows.append({
            "VariationID": vid, "gene": a["gene"],
            "sub_a": first["Submitter"], "sub_b": second["Submitter"],
            "label_a": first["label"], "label_b": second["label"],
            "n_a": len(first["pmids"]), "n_b": len(second["pmids"]),
            "jaccard": j,
            "identical": first["pmids"] == second["pmids"],
            "later_superset": first["pmids"] < second["pmids"],
            "date_a": first["date"], "date_b": second["date"],
            "gap_days": (second["date"] - first["date"]).days
                        if pd.notna(first["date"]) and pd.notna(second["date"])
                        else None,
        })

pairs = pd.DataFrame(rows)

print()
print(f"2. EQUIVALENT-BIBLIOGRAPHY PAIRS  "
      f"(both >= {MIN_CITES} cites, Jaccard >= {JACCARD_EQUIV:.2f})")
if pairs.empty:
    print("  none at these thresholds. IDFE is not computable on this panel;")
    print("  see the sweep in section 5 before concluding anything.")
else:
    # ----------------------------------------------------------------------
    # A submitter's wording is a house template, not a per-variant judgement.
    # If two labs coincide on hundreds of variants, every one contributes a
    # pair, and a mean over pairs reports two templates replicated, dressed as
    # a population rate. Same clustering that forced the per-laboratory split
    # in the original study — so the submitter-pair count below is the number
    # that decides whether any panel-wide rate means anything.
    # ----------------------------------------------------------------------
    pairs["lab_pair"] = [" | ".join(sorted([a, b]))
                         for a, b in zip(pairs.sub_a, pairs.sub_b)]
    n_lab_pairs = pairs.lab_pair.nunique()
    top = pairs.lab_pair.value_counts()

    print(f"  variant-level pairs         : {len(pairs):,}  "
          f"({int(pairs.identical.sum()):,} with identical citation sets)")
    print(f"  distinct variants           : {pairs.VariationID.nunique():,}")
    print(f"  distinct submitter pairs    : {n_lab_pairs:,}  -> "
          f"{len(pairs)/n_lab_pairs:.1f} variant-pairs each; largest "
          f"{100*top.iloc[0]/len(pairs):.0f}%, top 3 "
          f"{100*top.head(3).sum()/len(pairs):.0f}% of all pairs")

    disc = pairs[pairs.label_a != pairs.label_b]
    hard = pairs[((pairs.label_a == "claim") & (pairs.label_b == "denial")) |
                 ((pairs.label_a == "denial") & (pairs.label_b == "claim"))]
    by_lab = (pairs.assign(diff=pairs.label_a != pairs.label_b)
                   .groupby("lab_pair")["diff"].agg(["mean", "size"])
                   .sort_values("size", ascending=False))

    print()
    print("3. DIVERGENCE UNDER FIXED EVIDENCE")
    print(f"  variant-level, any difference   : {100*len(disc)/len(pairs):5.1f}%"
          "   <- inflated by clustering")
    print(f"  variant-level, claim vs denial  : {100*len(hard)/len(pairs):5.1f}%")
    print(f"  submitter-pair level, unweighted: {100*by_lab['mean'].mean():5.1f}%"
          f"   (n={n_lab_pairs} pairs)")
    print(f"  submitter pairs that ever differ: "
          f"{int((by_lab['mean'] > 0).sum()):,} / {n_lab_pairs:,}")
    print("  busiest submitter pairs:")
    for name, r in by_lab.head(3).iterrows():
        print(f"    {100*r['mean']:5.1f}% of {int(r['size']):>3}   {name}")

    # ----------------------------------------------------------------------
    # Identical bibliographies across independent labs would be a remarkable
    # coincidence; a shared upstream source (HGMD, a commercial annotation
    # pipeline, or ClinVar itself) is likelier. If the citations were inherited
    # then "same evidence, different label" is really "inherited citations,
    # different template" — a different claim, and not the one IDFE names.
    # ----------------------------------------------------------------------
    print()
    print("4. PROPAGATION CHECK")
    dated = pairs[pairs.gap_days.notna()]
    if len(dated):
        non_ident = dated[~dated.identical]
        sup = (f"{100*non_ident.later_superset.mean():.0f}%"
               if len(non_ident) else "n/a")
        med = (dated.assign(diff=dated.label_a != dated.label_b)
                    .groupby("diff")["gap_days"].median())
        print(f"  pairs with both dates       : {len(dated):,}")
        print(f"  identical sets              : {100*dated.identical.mean():.0f}%")
        print(f"  later a strict superset     : {sup}  "
              f"(of the {len(non_ident):,} non-identical)")
        print(f"  median gap                  : {dated.gap_days.median():.0f} days"
              f"   (agreeing {med.get(False, float('nan')):.0f}, "
              f"differing {med.get(True, float('nan')):.0f})")
    else:
        print("  no pairs with both dates parsed.")

    pairs.to_csv("bibliography_pairs.csv", index=False)
    by_lab.to_csv("divergence_by_submitter_pair.csv")
    print("  wrote bibliography_pairs.csv, divergence_by_submitter_pair.csv")

# --------------------------------------------------------------------------
# Sensitivity. Precomputed per threshold so the sweep is not quadratic in rows.
# --------------------------------------------------------------------------
print()
print("5. SENSITIVITY TO THRESHOLDS")
print(f"  {'min_cites':>9} {'jaccard':>8} {'var_pairs':>10} {'lab_pairs':>10} "
      f"{'differ%':>8}")
for mc in (1, 2, 3, 5):
    e = work[work.n_cites >= mc]
    cand = []
    for vid, grp in e.groupby("VariationID", sort=False):
        if len(grp) < 2:
            continue
        recs = grp.to_dict("records")
        for a, b in itertools.combinations(recs, 2):
            if a["Submitter"] != b["Submitter"]:
                cand.append((jaccard(a["pmids"], b["pmids"]),
                             a["Submitter"], b["Submitter"],
                             a["label"] != b["label"]))
    for jt in (0.5, 0.8, 1.0):
        sel = [c for c in cand if c[0] >= jt]
        labs = {" | ".join(sorted([c[1], c[2]])) for c in sel}
        pct = f"{100*sum(c[3] for c in sel)/len(sel):.1f}" if sel else "-"
        print(f"  {mc:>9} {jt:>8.2f} {len(sel):>10,} {len(labs):>10,} {pct:>8}")