# 02_citation_asymmetry_check.py
#
# Section 2 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `work` (written by cell 01)
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 5420160d1831d8ffe963ad4d5e8f49a683f99c7d2bebf4ba1079e4b3468dded8

"""
Follow-up to the bibliography-overlap diagnostic. Run in the SAME kernel,
after that cell: it reads `work` (one row per submission, with `label`,
`n_cites`, `Submitter`, `VariationID`).

The diagnostic's headline was not the one it was built for. Equivalent-
bibliography pairs turned out too few to support a rate, and its
claim-vs-denial line (0.0%) has no power: denials so rarely cite literature
that ~1 such pair is expected by chance in 60, and seeing zero happens 37% of
the time. What it did surface is that claims and denials differ in whether
they cite anything at all. This cell tests that properly.

Three questions, in the order that could overturn the result:
  1. Does the asymmetry hold on the corpus directly, with intervals?
  2. Does it hold INSIDE laboratories, or is it one lab's template counted
     many times? A house style replicated across thousands of submissions
     produces an aggregate that no individual laboratory shows.
  3. Why does the SOS1 I437T LabCorp/Dasa contrast not appear in the pairs?
"""

import math

import pandas as pd

MIN_PER_LAB = 10          # claims AND denials a lab needs for a within-lab rate
I437T_VARIATION = "45345"


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


if "work" not in globals():
    raise RuntimeError("`work` not in this kernel. Run the bibliography-overlap "
                       "diagnostic cell first, in the same session.")

w = work[work["label"].isin(["claim", "denial"])].copy()
w["cites"] = w["n_cites"] > 0

# --------------------------------------------------------------------------
# 1. Corpus level.
# --------------------------------------------------------------------------
print("=" * 78)
print("1. DOES A CLAIM CITE LITERATURE MORE OFTEN THAN A DENIAL?  (corpus)")
print("=" * 78)
rates = {}
for lab in ("claim", "denial"):
    s = w[w.label == lab]
    k, n = int(s.cites.sum()), len(s)
    p, lo, hi = wilson(k, n)
    rates[lab] = p
    print(f"  {lab:7s}: {k:5,} of {n:5,} cite >= 1 PMID  = {100*p:5.1f}%  "
          f"[95% CI {100*lo:4.1f}-{100*hi:4.1f}]")
print(f"\n  ratio claim/denial: {rates['claim']/rates['denial']:.2f}x")
print("  (both-flagged submissions excluded; 'neither' is not a claim about "
      "evidence at all)")

# --------------------------------------------------------------------------
# 2. Within laboratories. The test that could overturn section 1.
# --------------------------------------------------------------------------
per = (w.groupby(["Submitter", "label"])["cites"]
         .agg(["sum", "size"]).unstack("label"))
per.columns = [f"{a}_{b}" for a, b in per.columns]
for c in ("sum_claim", "size_claim", "sum_denial", "size_denial"):
    if c not in per.columns:
        per[c] = 0
per = per.fillna(0)
both_sides = per[(per.size_claim >= MIN_PER_LAB) &
                 (per.size_denial >= MIN_PER_LAB)].copy()
both_sides["cite_rate_claim"] = both_sides.sum_claim / both_sides.size_claim
both_sides["cite_rate_denial"] = both_sides.sum_denial / both_sides.size_denial
both_sides["diff_pp"] = 100 * (both_sides.cite_rate_claim -
                               both_sides.cite_rate_denial)
both_sides = both_sides.sort_values("size_claim", ascending=False)

print()
print("=" * 78)
print(f"2. WITHIN LABORATORIES  (labs with >= {MIN_PER_LAB} claims AND "
      f">= {MIN_PER_LAB} denials)")
print("=" * 78)
if both_sides.empty:
    print("  no laboratory submits enough of both. The asymmetry cannot be")
    print("  tested within labs, so section 1 may be a between-lab effect -")
    print("  claims and denials written by different laboratories with")
    print("  different citation habits. Report it that way, not as a")
    print("  property of how evidence is asserted.")
else:
    show = both_sides[["size_claim", "cite_rate_claim",
                       "size_denial", "cite_rate_denial", "diff_pp"]]
    print(show.to_string(float_format=lambda x: f"{x:.3f}"))
    n_labs = len(both_sides)
    n_pos = int((both_sides.diff_pp > 0).sum())
    print(f"\n  labs where claims cite more often than denials : "
          f"{n_pos} of {n_labs}")
    print(f"  median within-lab difference                   : "
          f"{both_sides.diff_pp.median():+.1f} percentage points")

    # How much of the corpus-level gap do these labs carry, and does the gap
    # survive removing the single largest contributor?
    top = per.size_claim.add(per.size_denial).idxmax()
    rest = w[w.Submitter != top]
    rc = rest[rest.label == "claim"].cites.mean()
    rd = rest[rest.label == "denial"].cites.mean()
    print(f"\n  largest contributor overall                    : {top}")
    print(f"  corpus ratio WITHOUT it                        : "
          f"{rc/rd:.2f}x  (claim {100*rc:.1f}% vs denial {100*rd:.1f}%)")

cover = w.Submitter.isin(both_sides.index).mean() if len(both_sides) else 0
print(f"\n  share of claim+denial submissions from labs tested here: "
      f"{100*cover:.1f}%")
print("  The rest come from labs that assert only one side - which is itself")
print("  part of the answer: much of the asymmetry may be WHO writes claims")
print("  versus who writes denials, not how either is written.")

# --------------------------------------------------------------------------
# 3. The worked example.
# --------------------------------------------------------------------------
print()
print("=" * 78)
print(f"3. SOS1 p.Ile437Thr  (VariationID {I437T_VARIATION})")
print("=" * 78)
v = work[work.VariationID.astype(str) == I437T_VARIATION]
if v.empty:
    print("  not in this panel's submissions.")
else:
    cols = ["Submitter", "label", "n_cites", "DateLastEvaluated"]
    print(v[cols].sort_values("n_cites", ascending=False)
                 .to_string(index=False))
    in_pairs = (pairs.VariationID.astype(str) == I437T_VARIATION).sum() \
        if "pairs" in globals() and not pairs.empty else 0
    print(f"\n  equivalent-bibliography pairs from this variant: {in_pairs}")
    print("  A submitter with 0 citations never enters the pairing, whatever")
    print("  its label. If LabCorp's denial cites nothing, then LabCorp x Dasa")
    print("  is a real contradiction on this record but NOT a comparison under")
    print("  fixed evidence - only GeneDx x Dasa is.")