# 03_i437t_citation_sets.py
#
# Section 3 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `work`
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 94c378a411780ded2904487ff78a9e48e2d5c18d31fced8e2cc879d1188fd499

"""
Which references does each submitter on SOS1 p.Ile437Thr (VariationID 45345)
name in its comment text, and how do the sets overlap?

Run in the same kernel as the bibliography-overlap diagnostic (reads `work`).

Why this is needed: the ClinVar web page lists 11 PMIDs for both GeneDx and
Dasa, but the pipeline, which reads only the free-text comment in
submission_summary.txt, sees 11 for GeneDx, 5 for Dasa and 3 for LabCorp. The
web page merges the comment with the submission's structured citation field;
the tab-delimited file carries only the comment. This prints what the pipeline
sees, which is the only view a text-mining study of ClinVar can rely on.
"""

import itertools

VID = "45345"

# The 11 PMIDs the ClinVar web page lists for both GeneDx and Dasa.
RECORD_11 = {"12628188", "17143282", "20648242", "21387466", "24451042",
             "24803665", "29493581", "30039904", "30541462", "31785789",
             "33042901"}

v = work[work.VariationID.astype(str) == VID]
sets = {}
for _, r in v.iterrows():
    if len(r["pmids"]):
        sets[r["Submitter"]] = (r["label"], set(r["pmids"]))

print(f"SOS1 p.Ile437Thr, VariationID {VID}: PMIDs named in the COMMENT TEXT\n")
for sub, (lab, s) in sorted(sets.items(), key=lambda kv: -len(kv[1][1])):
    outside = s - RECORD_11
    print(f"{sub[:62]:62s} {lab:8s} n={len(s):2d}")
    print(f"    {sorted(s)}")
    if outside:
        print(f"    not among the 11 on the record page: {sorted(outside)}")
    print()

print("pairwise overlap (Jaccard | shared PMIDs):")
for (a, (la, sa)), (b, (lb, sb)) in itertools.combinations(sets.items(), 2):
    inter = sa & sb
    j = len(inter) / len(sa | sb)
    print(f"  {a[:30]:30s} x {b[:30]:30s}  J={j:.2f}  "
          f"shared={len(inter)}  labels {la}/{lb}")