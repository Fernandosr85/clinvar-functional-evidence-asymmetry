# 06_published_pipeline_impact.py
#
# Section 6 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `subs`, `classify`, `CLAIM`, `DENIAL`, and the panel constants
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 4cb508c3d316bfdc74d6c2e71f86eaa86625961c19abb5342f09d85a2c39fb7c

"""
How much do the defects found by the two independent reviews change the
PUBLISHED panel counts? Measure before correcting anything.

Run at the end of the classifier notebook (are-functional-evidence-claims-in-
clinvar-auditabl), in the same kernel, after its first four code cells. It
needs `subs`, `classify`, the classifier's regexes and `_blank`, and re-reads
the cached submission_summary.txt.gz; nothing is downloaded.

Four defects, each measured separately against the published counts:

  A. load_panel keeps a row only if ITS gene field names a panel gene, so
     submissions filed with gene "-" on panel variants are dropped.
     (Found by review 1.) Variants on which EVERY submission has gene "-" are
     not recoverable this way and remain missing.
  B. _SENT splits only before a capital letter or "(", so "... . - No
     published functional evidence ..." stays one sentence, and inside
     classify() a denial then suppresses a claim in the same span.
     (Review 1.) Measured by re-running classify() with a splitter that also
     breaks at bullets; the unchanged splitter must first reproduce the
     published flags exactly, or the comparison means nothing.
  C. Negated or prospective sentences read as claims: "No prior functional
     evidence has been identified", "PS3 was not applied", "A zebrafish model
     is needed". (Review 2.) A submission is counted only if EVERY sentence
     that produced its claim carries such a cue. Tier 1 uses three narrow
     patterns; tier 2 any negation word. Both are candidates to READ, not
     corrections: "functional studies showed the variant did not bind" is a
     genuine claim with "not" in it.
  D. Missed denials such as "Functional studies have not yet been performed".
     (Review 2.) One narrow pattern, qualifier REQUIRED: the bare "has not
     been reported" is the literature-absence phrase that broke version 1 of
     this classifier and must not come back.

Every candidate is written to CSV with the sentence that triggered it.
"""

import csv
import glob
import re
from pathlib import Path

import pandas as pd

need = ["subs", "classify", "CLAIM", "DENIAL", "CODE_PS3", "CONDITIONAL",
        "VENDOR_MODEL", "_SENT", "_mend", "_blank", "read_header", "WANTED",
        "PANEL"]
missing = [n for n in need if n not in globals()]
if missing:
    raise RuntimeError(f"not in this kernel: {', '.join(missing)}. Run the "
                       "classifier notebook's first four code cells first.")

OUTDIR = Path("published_pipeline_impact")
OUTDIR.mkdir(exist_ok=True)


def counts(claim, denial):
    claim, denial = pd.Series(claim).astype(bool), pd.Series(denial).astype(bool)
    return dict(claims=int(claim.sum()), denials=int(denial.sum()),
                both=int((claim & denial).sum()))


def classify_with(text, splitter):
    """classify()'s claim/denial logic with the sentence splitter swapped."""
    t = _mend(str(text or ""))
    t = VENDOR_MODEL.sub(" ", t)
    claim = denial = False
    for s in splitter.split(t):
        if not s or not s.strip() or CONDITIONAL.search(s):
            continue
        d = bool(DENIAL.search(s))
        c = (bool(CLAIM.search(s)) or bool(CODE_PS3.search(s))) and not d
        claim, denial = claim or c, denial or d
    return claim, denial


def claim_sentences(text):
    """The sentences that produced a claim, as classify() reads them."""
    t = _mend(str(text or ""))
    t = VENDOR_MODEL.sub(" ", t)
    out = []
    for s in _SENT.split(t):
        if not s or not s.strip() or CONDITIONAL.search(s):
            continue
        if DENIAL.search(s):
            continue
        if CLAIM.search(s) or CODE_PS3.search(s):
            out.append(" ".join(s.split()))
    return out


base = counts(subs["claim"], subs["denial"])
rows = [("published", base)]
print("=" * 78)
print("PUBLISHED COUNTS (this kernel)")
print("=" * 78)
print(f"submissions {len(subs):,} | claims {base['claims']:,} | denials "
      f"{base['denials']:,} | both {base['both']:,} | claims/denials "
      f"{base['claims']/max(1, base['denials']):.3f}")

# --------------------------------------------------------------------------
# A. Rows dropped by the per-row gene filter.
# --------------------------------------------------------------------------
path = Path("submission_summary.txt.gz")
if not path.exists():
    hits = glob.glob("/kaggle/**/submission_summary.txt.gz", recursive=True)
    path = Path(hits[0]) if hits else path
print()
print("=" * 78)
print("A. SUBMISSIONS ON PANEL VARIANTS DROPPED BY THE GENE-FIELD FILTER")
print("=" * 78)
if not path.exists():
    print("cached submission_summary.txt.gz not found; section A skipped.")
    dropped = pd.DataFrame()
else:
    skip, names = read_header(path)
    keep = [c for c in WANTED if c in names]
    vids = set(subs["VariationID"].astype(str))
    want = {g.upper() for g in PANEL}
    parts = []
    for ch in pd.read_csv(path, sep="\t", header=None, names=names,
                          skiprows=skip, usecols=keep, dtype=str,
                          quoting=csv.QUOTE_NONE, engine="c", na_filter=False,
                          on_bad_lines="skip", chunksize=200_000):
        sym = ch["SubmittedGeneSymbol"].astype(str).str.strip().str.upper()
        sel = ch["VariationID"].astype(str).isin(vids) & ~sym.isin(want)
        if sel.any():
            parts.append(ch[sel].copy())
    dropped = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

if len(dropped):
    txt = _blank(dropped["Description"])
    if "ExplanationOfInterpretation" in dropped.columns:
        txt = txt + " " + _blank(dropped["ExplanationOfInterpretation"])
    dropped["text"] = txt.str.strip()
    fl = dropped["text"].apply(classify).apply(pd.Series)
    dropped["claim"], dropped["denial"] = fl["claim"], fl["denial"]
    a = counts(dropped["claim"], dropped["denial"])
    print(f"dropped rows on panel variants : {len(dropped):,} "
          f"({dropped['VariationID'].nunique():,} variants)")
    print(f"  with a prose comment (>=20)  : {int((dropped['text'].str.len() >= 20).sum()):,}")
    print(f"  claims {a['claims']:,} | denials {a['denials']:,} | both {a['both']:,}")
    print("  gene field on the dropped rows:")
    print(dropped["SubmittedGeneSymbol"].value_counts().head(6).to_string())
    dropped.to_csv(OUTDIR / "A_dropped_rows_classified.csv", index=False)
    rows.append(("A. dropped rows restored",
                 dict(claims=base["claims"] + a["claims"],
                      denials=base["denials"] + a["denials"],
                      both=base["both"] + a["both"])))
else:
    print("no dropped rows found.")

# --------------------------------------------------------------------------
# B. Sentence splitter.
# --------------------------------------------------------------------------
_SENT_FIX = re.compile(r"(?<=[.;])\s+(?=[A-Z(])"
                       r"|(?<=[.;])\s*[-•·�]\s+")
print()
print("=" * 78)
print("B. SPLITTER THAT ALSO BREAKS AT BULLETS  ('. - ', '. • ', '. � ')")
print("=" * 78)
same = subs["text"].apply(lambda t: classify_with(t, _SENT))
repro = ((same.str[0] == subs["claim"].astype(bool)) &
         (same.str[1] == subs["denial"].astype(bool))).mean()
print(f"unchanged splitter reproduces the published flags: {100*repro:.2f}%")
if repro < 1:
    print("  NOT 100%: this cell's copy of the logic differs from classify();")
    print("  section B is not interpretable until that is resolved.")
fixed = subs["text"].apply(lambda t: classify_with(t, _SENT_FIX))
fc, fd = fixed.str[0], fixed.str[1]
flip = (fc != subs["claim"].astype(bool)) | (fd != subs["denial"].astype(bool))
b = counts(fc, fd)
print(f"submissions whose flags change : {int(flip.sum()):,}")
print(f"  claims {base['claims']:,} -> {b['claims']:,} | denials "
      f"{base['denials']:,} -> {b['denials']:,} | both {base['both']:,} -> {b['both']:,}")
flips = subs.loc[flip, ["VariationID", "gene", "Submitter", "claim", "denial",
                        "text"]].copy()
flips["claim_fixed"], flips["denial_fixed"] = fc[flip], fd[flip]
flips.to_csv(OUTDIR / "B_splitter_flips.csv", index=False)
rows.append(("B. bullet-aware splitter", b))

# --------------------------------------------------------------------------
# C. Claims whose every claim sentence is negated or prospective.
# --------------------------------------------------------------------------
TIER1 = re.compile(
    r"\bno\s+(?:\w+\s+){0,3}(?:functional|experimental|in[ -]?vitro|in[ -]?vivo)\b"
    r"|\bPS3\b[^.;]{0,40}\bnot\b|\bnot\b[^.;]{0,20}\bPS3\b"
    r"|\b(?:is|are|would be|will be)\s+(?:needed|required|warranted)\b", re.I)
TIER2 = re.compile(r"\b(?:no|not|nor|without|lack(?:s|ing)?|absent|absence|"
                   r"unknown|unclear|needed|required|yet)\b", re.I)

cl = subs[subs["claim"].astype(bool)].copy()
cl["claim_sents"] = cl["text"].map(claim_sentences)
cl = cl[cl["claim_sents"].map(len) > 0]
cl["tier1"] = cl["claim_sents"].map(lambda ss: all(TIER1.search(s) for s in ss))
cl["tier2"] = cl["claim_sents"].map(lambda ss: all(TIER2.search(s) for s in ss))
n1, n2 = int(cl["tier1"].sum()), int(cl["tier2"].sum())
print()
print("=" * 78)
print("C. CLAIMS WHOSE EVERY CLAIM SENTENCE IS NEGATED OR PROSPECTIVE")
print("=" * 78)
print(f"claim submissions with a claim sentence : {len(cl):,}")
print(f"  tier 1 (three narrow patterns)        : {n1:,}   <- likely false claims")
print(f"  tier 2 (any negation word)            : {n2:,}   <- candidates to read")
for _, r in cl[cl["tier1"]].head(12).iterrows():
    print(f"   [{r['gene']}] {r['Submitter'][:40]}: \"{r['claim_sents'][0][:150]}\"")
out = cl[cl["tier2"]][["VariationID", "gene", "Submitter", "tier1",
                       "claim_sents"]]
out.to_csv(OUTDIR / "C_candidate_false_claims.csv", index=False)
rows.append(("C. minus tier-1 false claims (estimate)",
             dict(claims=base["claims"] - n1, denials=base["denials"],
                  both=base["both"])))

# --------------------------------------------------------------------------
# D. Missed denials, one narrow pattern.
# --------------------------------------------------------------------------
MISSED_DENIAL = re.compile(
    r"\b(?:functional|experimental|in[ -]?vitro|in[ -]?vivo)\s+"
    r"(?:studies|data|evidence|assays?|analys[ie]s|experiments)\s+"
    r"(?:have|has)\s+not\s+(?:yet\s+)?been\s+"
    r"(?:performed|conducted|done|carried out|reported)\b", re.I)
nd = subs[~subs["denial"].astype(bool)].copy()
nd["hit"] = nd["text"].map(lambda t: bool(MISSED_DENIAL.search(str(t))))
n_d = int(nd["hit"].sum())
print()
print("=" * 78)
print("D. MISSED DENIALS  ('<functional> studies have not (yet) been performed')")
print("=" * 78)
print(f"submissions not flagged as denial that match : {n_d:,}")
for _, r in nd[nd["hit"]].head(8).iterrows():
    m = MISSED_DENIAL.search(r["text"])
    s = r["text"][max(0, m.start() - 60):m.end() + 40]
    print(f"   [{r['gene']}] {r['Submitter'][:40]}: \"...{' '.join(s.split())}...\"")
nd[nd["hit"]][["VariationID", "gene", "Submitter", "claim", "text"]] \
    .to_csv(OUTDIR / "D_candidate_missed_denials.csv", index=False)
rows.append(("D. plus missed denials (estimate)",
             dict(claims=base["claims"], denials=base["denials"] + n_d,
                  both=base["both"])))

# --------------------------------------------------------------------------
# Summary. A-B are recomputations; C-D are pattern-based estimates until the
# CSVs have been read.
# --------------------------------------------------------------------------
print()
print("=" * 78)
print("SUMMARY  (each row changes ONE thing relative to the published counts)")
print("=" * 78)
print(f"{'':40s} {'claims':>8s} {'denials':>8s} {'both':>6s} {'ratio':>7s}")
for name, c in rows:
    print(f"{name:40s} {c['claims']:>8,} {c['denials']:>8,} {c['both']:>6,} "
          f"{c['claims']/max(1, c['denials']):>7.3f}")
print()
print("A and B are recomputations. C and D are pattern-based estimates: read")
print(f"the CSVs in {OUTDIR}/ before quoting any of them.")