# 04_citation_sentence_attribution.py
#
# Section 4 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `work`, plus the classifier's `_mend`, `_SENT`, `VENDOR_MODEL`, `CONDITIONAL`, `DENIAL`, `CLAIM`, `CODE_PS3`, and `cited_pmids` from cell 01
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# f6ddea9423b1a29bb3da49b2e56022cf5b383929a95d9af76c70bb64e92349eb

"""
Sentence-level citation attribution: in which sentence is each PMID cited,
and what does that sentence assert?

Run in the same kernel as the bibliography-overlap diagnostic. Needs `work`
and the classifier's own regexes from panel_functional_claims_v6 / the Kaggle
notebook: _mend, _SENT, VENDOR_MODEL, CONDITIONAL, DENIAL, CLAIM, CODE_PS3.

WHY SENTENCE LEVEL
    Whole-bibliography overlap (Jaccard) was the wrong unit: on SOS1 I437T it
    missed the case entirely. The sharper unit is the single citation - one
    paper, cited on one variant, read one way by one submitter and another way
    by another. But a PMID being somewhere in a submission is not the same as
    being cited FOR that submission's claim or denial: a comment that denies
    functional evidence will often cite case reports in a different sentence.
    So each PMID is attributed to the sentence it sits in, and the sentence is
    classified with exactly the per-sentence logic classify() uses.

SENTENCE SPLITTING
    Uses v6's own _SENT, which splits after '.' or ';' before an uppercase
    letter or '('. That orphans citations written as "... effect. (PMID: 1)" or
    "...; PMID: 1": the fragment becomes its own sentence. A fragment holding
    nothing but a citation is attached to the sentence before it.

RECONCILIATION
    Section 0 re-derives each submission's claim/denial flags from the
    sentence roles and compares them with `work`. Anything below 100% agreement
    means this cell and the published classifier read some submissions
    differently, and those rows are counted before any result is shown.
"""

import itertools
import re
from collections import defaultdict

import pandas as pd

VID_EXAMPLE = "45345"

need = ["work", "_mend", "_SENT", "VENDOR_MODEL", "CONDITIONAL", "DENIAL",
        "CLAIM", "CODE_PS3", "cited_pmids"]
missing = [n for n in need if n not in globals()]
if missing:
    raise RuntimeError(f"not in this kernel: {', '.join(missing)}. Run the "
                       "classifier notebook's first cells and the "
                       "bibliography-overlap diagnostic first.")

CITE_ONLY = re.compile(
    r"^\s*\(?\s*(?:PMIDs?\s*:?\s*)?[\d\s,;:&/and()PMID.]*\)?\s*[.;]?\s*$", re.I)


def sentence_roles(text):
    """[(role, frozenset(pmids), sentence)] mirroring classify()'s logic."""
    t = _mend(str(text or ""))
    raw = [s for s in _SENT.split(t) if s.strip()]
    merged = []
    for s in raw:
        if merged and cited_pmids(s) and CITE_ONLY.match(s):
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    out = []
    for s in merged:
        pm = cited_pmids(s)
        if VENDOR_MODEL.search(s):
            role = "vendor-model"
        elif CONDITIONAL.search(s):
            role = "conditional"
        else:
            d = bool(DENIAL.search(s))
            c = (bool(CLAIM.search(s)) or bool(CODE_PS3.search(s))) and not d
            role = "denial" if d else ("claim" if c else "other")
        out.append((role, pm, s))
    return out


# --------------------------------------------------------------------------
# 0. Reconciliation against the published flags.
# --------------------------------------------------------------------------
cit = work[work.n_cites > 0].copy()
cit["roles"] = cit["text"].map(sentence_roles)
cit["claim_s"] = cit.roles.map(lambda rs: any(r == "claim" for r, _, _ in rs))
cit["denial_s"] = cit.roles.map(lambda rs: any(r == "denial" for r, _, _ in rs))
agree = ((cit.claim_s == cit.claim.astype(bool)) &
         (cit.denial_s == cit.denial.astype(bool)))

print("=" * 78)
print("0. RECONCILIATION  (sentence roles vs published classify() flags)")
print("=" * 78)
print(f"citing submissions                     : {len(cit):,}")
print(f"  flags reproduced exactly             : {int(agree.sum()):,} "
      f"({100*agree.mean():.2f}%)")
if (~agree).any():
    print(f"  disagree                             : {int((~agree).sum()):,}"
          "  - these read differently here than in the published run;")
    print("    the vendor-model sentence is the likely source (classify() strips")
    print("    it by span before splitting, this cell tests it per sentence).")

# long form: one row per (submission, PMID, sentence role)
rows = []
for _, r in cit.iterrows():
    attached = set()
    for role, pm, _s in r["roles"]:
        for p in pm:
            rows.append(dict(VariationID=str(r["VariationID"]), gene=r["gene"],
                             Submitter=r["Submitter"], pmid=p,
                             sent_role=role, sub_label=r["label"]))
            attached.add(p)
    for p in set(r["pmids"]) - attached:          # parsed from the joined text
        rows.append(dict(VariationID=str(r["VariationID"]), gene=r["gene"],
                         Submitter=r["Submitter"], pmid=p,
                         sent_role="unattached", sub_label=r["label"]))
cites = (pd.DataFrame(rows)
           .drop_duplicates(["VariationID", "Submitter", "pmid", "sent_role"]))

# --------------------------------------------------------------------------
# 1. The worked example.
# --------------------------------------------------------------------------
print()
print("=" * 78)
print(f"1. SOS1 p.Ile437Thr (VariationID {VID_EXAMPLE}): the sentence each "
      "PMID sits in")
print("=" * 78)
ex = cit[cit.VariationID.astype(str) == VID_EXAMPLE]
for _, r in ex.iterrows():
    print(f"\n{r['Submitter'][:70]}   [submission: {r['label']}]")
    for role, pm, s in r["roles"]:
        if pm or role in ("claim", "denial"):
            flat = " ".join(s.split())
            print(f"  {role:12s} {str(sorted(pm)) if pm else '(no citation)'}")
            print(f"      \"{flat[:150]}{'...' if len(flat) > 150 else ''}\"")

# --------------------------------------------------------------------------
# 2. Panel-wide: one paper, one variant, read differently.
# --------------------------------------------------------------------------
cell = cites.groupby(["VariationID", "pmid"])
multi = cell.Submitter.nunique()
multi = multi[multi >= 2]

def cell_flags(g):
    subs_claim_sent = set(g.loc[g.sent_role == "claim", "Submitter"])
    subs_den_sent = set(g.loc[g.sent_role == "denial", "Submitter"])
    subs_den_sub = set(g.loc[g.sub_label.isin(["denial", "both"]), "Submitter"])
    strict = any(a != b for a in subs_claim_sent for b in subs_den_sent)
    loose = any(a != b for a in subs_claim_sent for b in subs_den_sub)
    return pd.Series(dict(strict=strict, loose=loose,
                          claim_sent=len(subs_claim_sent),
                          den_sub=len(subs_den_sub)))

keyed = cites.set_index(["VariationID", "pmid"]).loc[multi.index].reset_index()
flags = (keyed.groupby(["VariationID", "pmid"])[["Submitter", "sent_role",
                                                  "sub_label"]]
              .apply(cell_flags))

print()
print("=" * 78)
print("2. ONE PAPER, ONE VARIANT, TWO READINGS  (panel-wide)")
print("=" * 78)
print(f"(variant, PMID) cells cited by >= 2 submitters     : {len(flags):,}")
print(f"  ...where some submitter cites it in a CLAIM sentence: "
      f"{int((flags.claim_sent > 0).sum()):,}")
print(f"  ...where some DENIAL-labelled submission cites it : "
      f"{int((flags.den_sub > 0).sum()):,}   <- ceiling on both counts below")
print()
print(f"claim sentence  x  denial SENTENCE, same paper     : "
      f"{int(flags.strict.sum()):,} cells  (strict)")
print(f"claim sentence  x  denial SUBMISSION, same paper   : "
      f"{int(flags.loose.sum()):,} cells  (loose)")

for name, col in (("strict", "strict"), ("loose", "loose")):
    hit = flags[flags[col]].reset_index()
    if hit.empty:
        continue
    k = keyed.merge(hit[["VariationID", "pmid"]], on=["VariationID", "pmid"])
    pairs_ = set()
    for (vid, p), g in k.groupby(["VariationID", "pmid"]):
        a = set(g.loc[g.sent_role == "claim", "Submitter"])
        b = (set(g.loc[g.sent_role == "denial", "Submitter"]) if col == "strict"
             else set(g.loc[g.sub_label.isin(["denial", "both"]), "Submitter"]))
        for x, y in itertools.product(a, b):
            if x != y:
                pairs_.add(" | ".join(sorted([x, y])))
    print(f"\n  {name}: {hit.VariationID.nunique():,} variants, "
          f"{hit.pmid.nunique():,} distinct papers, "
          f"{len(pairs_):,} distinct submitter pairs")
    top_p = hit.pmid.value_counts().head(8)
    print(f"  papers most often read both ways ({name}):")
    for p, n in top_p.items():
        print(f"    PMID {p}: {n} variant(s)")

cites.to_csv("citations_by_sentence.csv", index=False)
flags.reset_index().to_csv("paper_variant_readings.csv", index=False)
print("\nwrote citations_by_sentence.csv, paper_variant_readings.csv")

# --------------------------------------------------------------------------
# 3. Where citations sit, by what the sentence asserts. If denial sentences
#    almost never carry a PMID, the strict count above is bounded near zero by
#    writing convention, not by agreement between laboratories.
# --------------------------------------------------------------------------
print()
print("=" * 78)
print("3. WHICH SENTENCES CARRY CITATIONS")
print("=" * 78)
print(cites.sent_role.value_counts().to_string())