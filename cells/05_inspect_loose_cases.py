# 05_inspect_loose_cases.py
#
# Section 5 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# `cit` and `flags` (written by cell 04)
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 101ce300bdf8e6899fa8c881a6c6bd146523cc3b4a027e735addeb015868acd9

"""
Read the loose-match cases one by one before any count of them is reported.

Run in the same kernel, after citation_sentence_attribution.py (needs `cit`
and `flags`). The addendum states that 4 variants show the SOS1 I437T pattern:
one submitter cites a paper in a sentence asserting functional evidence, while
another cites the same paper in a submission that denies it. That number came
from a mechanical count and only I437T has been read. A count is not a case
series until each case has been looked at.

For each variant this prints the ClinVar link, and for every submitter that
cites one of the flagged papers: the sentence carrying the paper, plus - for
denial submissions - the denial sentence itself, so the two can be compared.
"""

need = ["cit", "flags"]
missing = [n for n in need if n not in globals()]
if missing:
    raise RuntimeError(f"not in this kernel: {', '.join(missing)}. Run "
                       "citation_sentence_attribution.py first.")

hit = flags[flags["loose"]].reset_index()
print(f"{hit.VariationID.nunique()} variants, {len(hit)} (variant, paper) cells\n")

for vid, g in hit.groupby("VariationID"):
    papers = set(g.pmid)
    rows = cit[cit.VariationID.astype(str) == str(vid)]
    gene = rows.gene.iloc[0] if len(rows) else "?"
    print("=" * 78)
    print(f"{gene}  VariationID {vid}   flagged papers: {sorted(papers)}")
    print(f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{vid}/")
    print("=" * 78)
    for _, r in rows.iterrows():
        rel = [(role, pm & papers, s) for role, pm, s in r["roles"]
               if (pm & papers) or role == "denial"]
        if not any(pm for _, pm, _ in rel):
            continue
        print(f"\n  {r['Submitter'][:70]}   [submission: {r['label']}]"
              f"   {r.get('DateLastEvaluated', '')}")
        for role, pm, s in rel:
            flat = " ".join(s.split())
            tag = str(sorted(pm)) if pm else "(no flagged paper)"
            print(f"    {role:9s} {tag}")
            print(f"        \"{flat[:260]}{'...' if len(flat) > 260 else ''}\"")
    print()

print("For each variant, check three things before counting it:")
print("  1. the claim sentence says functional evidence exists FOR THIS variant;")
print("  2. the denial is about THIS variant's function, not another criterion;")
print("  3. both submissions cite the paper as evidence about this variant,")
print("     not for population data, gene-level mechanism, or a different allele.")