# How functional evidence is recorded in ClinVar

An audit of the 13-gene RASopathy panel

Sep 29, 2026 · @Fernando dos Santos Rodrigues

## The question

In ClinVar, whether a variant "has functional evidence" is recorded as a property of the submission, not of the variant.

Submitters write a free-text interpretation comment. Some assert that functional studies support a damaging effect on the gene product. Others state that, to their knowledge, no experimental evidence has been reported. Both sentences are written about the same variants, sometimes by laboratories citing overlapping literature.

That matters because PS3 and BS3 turn on whether a validated assay exists and can be applied to the variant being classified. A free-text sentence asserting functional evidence cannot be told apart from one backed by an assay without reading what it cites. A curation process — human or automated — that records the phrase without checking the citations inherits the submitter's categorisation.

This audit asks three things of the 13-gene RASopathy panel:

1. How are the two kinds of statement distributed across the corpus?
2. Is a bibliography-controlled comparison — two laboratories, one variant, the same papers — even possible at the scale needed to report a rate?
3. When the two statements collide on one record, what is actually cited?

It does not ask which laboratory is right. Nothing here measures whether any reading of the literature is correct.

## Corpus and method

One ClinVar release, scanned end to end: 6,738,642 rows of `submission_summary.txt`, reduced to 32,562 submissions on 17,369 variants across 13 RASopathy genes.

The unit of analysis is the submission, not the variant. Its text is `Description` joined with `ExplanationOfInterpretation`, with ClinVar's `-` placeholder treated as empty — that placeholder is the first trap, because read as text it makes every empty comment look like content.

| Comment content | Submissions | Share |
| --- | --- | --- |
| Prose comment | 21,249 | 65.3% |
| No comment at all | 10,541 | 32.4% |
| Codes or stub only | 772 | 2.4% |

A sentence-level classifier reads each comment and returns four booleans — `claim`, `denial`, `prediction`, `lit_absence` — not a label. The four strata used below (claim, denial, both, neither) are derived from the claim/denial pair.

Three things about the classifier are load-bearing:

- **Literature absence is not a denial.** 5,926 submissions say a variant has not been reported in the literature. Version 1 of this pipeline counted them as denials of functional evidence and was wrong by roughly six-fold. They are excluded here, and four literature probes confirm none leaks into the denial patterns.
- **A predictor is not an assay.** 12,505 submissions mention a computational predictor. The classifier's regression set includes vendor-model text, in-silico framing and predictor scores as negative cases.
- **Validation is partial in this run.** All 24 regression cases pass. The three labelled CSVs were not attached to the stored run, so it produces no held-out accuracy figure and prints `NOT FOUND` instead. Two known weaknesses remain unquantified: an inserted adjective can break a denial pattern (*"no variant specific experimental evidence … has been reported"* reads as a claim), and a submission stating that an assay exists but is not a VCEP-approved assay has no label at all.

One scope limit runs through everything below: **citations here are PMIDs in comment text**. References given by author and year, and references in ClinVar's structured citation field, are invisible to this pipeline. The section Where the citations live measures what that costs.

## Finding 1 — denials outnumber claims

Across the panel, denials outnumber claims: 1,513 submissions carry a denial sentence against 1,218 that carry a claim sentence, a ratio of **0.805**.

| Stratum (mutually exclusive) | Submissions | Share of corpus |
| --- | --- | --- |
| Claim only | 1,200 | 3.685% |
| Denial only | 1,495 | 4.591% |
| Both | 18 | 0.055% |
| Neither | 29,849 | 91.668% |

Two bases run through this report, and they differ by those 18 submissions. The **flag counts** — 1,218 and 1,513 — count a submission on both sides when its text does both; they are the basis of the 0.805 ratio and of the robustness table. The **disjoint strata** above exclude them, and are the basis of the citation rates in Finding 3 (692 of 1,200 claims; 189 of 1,495 denials). On the disjoint basis the ratio is 0.803. Nothing in this report turns on which basis is used, provided each figure says which one it is.

The claim rate is 3.7% over all submissions and 5.5% over commented submissions. The second is the meaningful one: a third of the corpus carries no comment, and a submission with no comment is not a statement about evidence either way.

Two readings of the ratio are worth separating. It is consistent with functional data genuinely being scarce for these genes — which is the RASopathy VCEP's own position, since it caps PS3 at Moderate for SOS1 and does not apply BS3. It is equally consistent with denial being the cheaper sentence to write: a claim obliges you to name a study, a denial does not. Finding 3 tests the second reading directly.

The 18 submissions flagged as both are not noise. Each asserts experimental evidence in one sentence and carries a standard caveat in another — usually *"however, these predictions have yet to be confirmed by functional studies"*. They are counted on both sides of the 0.805 ratio and held out of the disjoint strata above, and the worked example below shows what happens when a search forgets to handle them.

## Finding 2 — this is a case series, not a rate

A bibliography-controlled comparison is possible on this panel, but only 29 laboratory pairs deep. Any percentage computed over variant pairs is a percentage over templates.

Only 4,012 of 32,562 submissions (12.3%) cite at least one PMID in comment text, and 1,849 (5.7%) cite three or more. Pairing submissions on the same variant, from different submitters, both citing at least three PMIDs with Jaccard overlap of 0.80 or higher, yields:

- **60** variant-level pairs, 24 of them with identical citation sets
- over **43** distinct variants
- from **29** distinct submitter pairs — 2.1 variant-pairs each

The clustering is severe. A single submitter pair supplies 21.7% of all pairs, and the top three supply 36.7%.

| Submitter pair | Variant pairs | Divergence |
| --- | --- | --- |
| 3billion × ClinGen RASopathy VCEP | 13 | 7.7% |
| 3billion × Dasa | 5 | 20.0% |
| Dasa × Labcorp Genetics (formerly Invitae) | 4 | 0.0% |
| Labcorp Genetics × Rady Children's Institute | 4 | 0.0% |
| GeneDx × Labcorp Genetics (formerly Invitae) | 4 | 0.0% |

A submitter's wording is a house template, not a per-variant judgement. When two laboratories coincide on many variants, every coincidence contributes a pair, and a mean over pairs reports two templates replicated — dressed as a population rate. This is the same clustering that forces a per-laboratory split in the parent study.

Both denominators, side by side:

| Measure | Value |
| --- | --- |
| Variant-level, any label difference | 21.7% |
| Variant-level, claim versus denial only | 0.0% |
| Submitter-pair level, unweighted mean | 34.9% (n = 29) |
| Submitter pairs that ever differ | 13 of 29 |

The headline does not rest on the thresholds. Sweeping minimum citations over 1, 2, 3 and 5, and Jaccard over 0.50, 0.80 and 1.00, divergence runs between 8.3% and 37.5%, and the submitter-pair count peaks at 131 in the loosest cell. No setting turns 29 pairs into a population.

And the pairs may not be independent. Of the 55 pairs with both dates, 43.6% have identical citation sets; among the non-identical, 48.4% have the later submission as a strict superset of the earlier; the median gap between submissions is 926 days. Identical bibliographies across independent laboratories would be a remarkable coincidence. A shared upstream source — HGMD, a commercial annotation pipeline, or ClinVar itself — is likelier. If the citations were inherited, then "same evidence, different label" is really "inherited citations, different template", which is a different claim.

## Finding 3 — a claim cites literature 4.6× more often than a denial

Across the corpus, 57.7% of claims cite at least one PMID (692 of 1,200; 95% CI 54.9–60.4) against 12.6% of denials (189 of 1,495; 95% CI 11.1–14.4).

Some gap is expected from the shape of the sentence alone: a claim points at a study, a denial has no study to point at. The question is whether the gap survives *inside* laboratories that write both kinds of statement — the check that would expose it as one house style counted many times.

It does, in four of the five laboratories that write at least ten of each.

| Laboratory | Claims | Cite rate | Denials | Cite rate | Difference |
| --- | --- | --- | --- | --- | --- |
| Labcorp Genetics (formerly Invitae) | 228 | 100.0% | 282 | 7.4% | +92.6 pp |
| GeneDx | 162 | 88.3% | 72 | 15.3% | +73.0 pp |
| Women's Health and Genetics, LabCorp | 102 | 31.4% | 927 | 9.7% | +21.7 pp |
| Victorian Clinical Genetics Services | 17 | 82.4% | 57 | 77.2% | +5.2 pp |
| Ambry Genetics | 171 | 0.0% | 61 | 0.0% | 0.0 pp |

The median within-laboratory difference is +21.7 percentage points. Ambry's zero is not an absence of citation — Ambry cites by author and year, which this pipeline cannot see at all.

Two qualifications belong with the 4.6×. Removing the single largest contributor (Women's Health and Genetics, LabCorp) still leaves 3.45×, so the effect is not one laboratory alone. But the five laboratories tested here account for 77.1% of all claim-plus-denial submissions; the rest come from laboratories that assert only one side. Much of the corpus-level asymmetry may therefore be **who writes claims versus who writes denials**, rather than how either is written.

The sharpest version of the result is at sentence level. Of the citation-carrying sentences in the corpus, 963 are claim sentences and **2** are denial sentences. A denial sentence essentially never names what was reviewed; on the records where LabCorp denies, the citations sit in a separate sentence — *"the following publications have been ascertained in the context of this evaluation"* — which says nothing about which of them bear on function. One qualification, from a review of this report: both of those two sentences are themselves splitter artefacts — in each, the citation belongs to the clause on the other side of a bullet marker. Under the bullet-aware splitter of Defect B the true count is zero, which strengthens the finding but means Defect B changes no submission-level flag while changing this sentence-level count.

## The worked example — SOS1 c.1310T>C (p.Ile437Thr)

On [VCV000045345](https://www.ncbi.nlm.nih.gov/clinvar/variation/45345/), Dasa states that functional evidence supports a deleterious effect; LabCorp states that no experimental evidence has been reported. Eighteen submissions sit on the record; sixteen are visible to this pipeline, and seven of those cite a PMID. The two that are missing are dropped by the gene-field filter documented below as Defect A, which makes this record its own small demonstration of that defect.

> **Dasa** (SCV007599104.1, 22 Jan 2026): "De novo occurrence has been reported in an individual with related phenotype. Functional evidence supports a deleterious effect on the gene or gene product (PMID: 21387466; PMID: 24803665; PMID: 30541462; PMID: 30039904; PMID: 24451042)."

> **LabCorp, Women's Health and Genetics** (SCV000918268.3, 13 Nov 2023): "To our knowledge, no experimental evidence demonstrating an impact on protein function has been reported."

Dasa attaches the same five references to two different evidence lines — functional evidence, and recurrent observation in patients. None of the five reports a functional assay of p.Ile437Thr.

| PMID | Study | Design | Assay of I437T? |
| --- | --- | --- | --- |
| 21387466 | Lepri et al. 2011, *Hum Mutat* | Cohort mutation scanning; reports I437T as de novo | No |
| 24803665 | Kiel & Serrano 2014, *Mol Syst Biol* | Structure-energy computation | No |
| 30541462 | Yang et al. 2018, *BMC Med Genet* | Targeted NGS; its variant table lists PS3 for this variant with no assay reported | No |
| 30039904 | Prasad et al. 2018, *Pediatr Blood Cancer* | Case report with WGS | No |
| 24451042 | Lepri et al. 2014, *BMC Med Genet* | Diagnostic sequencing; reports p.Ile437**Asn** at this codon | No |

One of those papers assigns PS3 to the variant in its own table without reporting an assay. The record does not show whether that is where Dasa's reading comes from, but it is a route by which a code applied in a publication reaches a submission as "functional evidence".

Lepri et al. 2011 is cited on this record by nine submitters. Eight cite it for something that is not functional evidence — most as a report of affected individuals, several singling out the de novo case; GeneDx lists it among associated publications with no role stated, 3billion cites it as a prior report of the same change, and Ambry names it in its comment by author and journal, and again in its structured citation field. Dasa alone also gives it a functional-evidence role. LabCorp's denial sentence carries no citation at all.

### Why the panel-wide search cannot see this record

The clearest contradiction in the corpus produces **zero** equivalent-bibliography pairs. Dasa and LabCorp overlap at Jaccard 0.33 on two shared PMIDs — below any threshold worth using — and LabCorp cites only three papers. The strongest overlap on the record is Dasa × GeneDx at 0.45, and GeneDx asserts nothing either way.

This is the methodological point behind Finding 2. A submitter citing nothing never enters the pairing, whatever it asserts. The bibliography-controlled search and the contradictions people actually care about are not the same set.

### The second confirmed case, and two that fail

A panel-wide search for a paper cited in a claim sentence by one submitter and in a denying submission by another flagged four variants. Reading each confirmed two.

| Variant | Asserts functional evidence | Denies it | Verdict |
| --- | --- | --- | --- |
| SOS1 p.Ile437Thr, VCV000045345 | Dasa, SCV007599104.1 | LabCorp (WH&G), SCV000918268.3 | Holds |
| PTPN11 p.Ala72Gly, VCV000013325 | Dasa, SCV007599168.1 | LabCorp (WH&G), SCV000698071.2 | Holds |
| RIT1, VCV000183401 | 3billion, GeneDx, Labcorp Genetics | — | Fails |
| SOS1, VCV000040728 | Labcorp Genetics, GeneDx | — | Fails |

The two that fail do so for one reason: the search counted *both*-labelled submissions on the denial side. On each, LabCorp asserts experimental evidence in one sentence and carries the caveat *"however, these predictions have yet to be confirmed by functional studies"* in another. No submitter on either record denies functional evidence. A count without reading would have reported four.

And the two that hold are the same submitter pair. Dasa asserts and LabCorp (Women's Health and Genetics) denies, on SOS1 p.Ile437Thr and again on PTPN11 p.Ala72Gly — one pair observed twice, not two independent observations. That is as consistent with a mismatch between two house templates as with anything wider. What would make it wider is the 39 variants across 24 submitter pairs found by dropping the shared-paper requirement, and none of those has been read.

## Where the citations live

ClinVar stores a submission's references in two places, and this pipeline sees one of them.

The free-text comment is what `submission_summary.txt` carries. The structured citation field is distributed per submission in the XML release (`ClinVarVCVRelease`) and per submitting organisation in `var_citations.txt`. The record page merges both, which is why a reader on the website and a reader of the TSV see different bibliographies for the same submission.

On SOS1 p.Ile437Thr:

| Submitter | PMIDs in comment text | Structured citations |
| --- | --- | --- |
| GeneDx | 11 | none |
| Dasa | 5 | 11 |
| LabCorp (Women's Health and Genetics) | 3 | 3 |

The "same eleven references" that GeneDx and Dasa appear to share are GeneDx's comment and Dasa's structured list. An analysis restricted to comment text sees 5 of Dasa's 11.

A second channel is invisible for a different reason: references given by author and year. LabCorp, the Laboratory for Molecular Medicine, Neuberg Centre and Ambry Genetics all cite Lepri et al. 2011 that way; LabCorp also gives the PMID in another sentence, so only three of the nine are reachable by author and year alone. Ambry's comment gives it as "Lepri F et al. Hum Mutat, 2011 Jul;32:760-72", and the paper appears in Ambry's structured list as well. That is why Ambry shows a 0.0% citation rate in Finding 3 — not silence, but a citation format this pipeline cannot parse.

The cost is measurable. An independent review re-ran the search with the missing channels:

| Search | Variants flagged |
| --- | --- |
| Claim sentence × denying submission, comment PMIDs only (this pipeline) | 4 |
| Same, symmetric in both directions | 7 |
| Same, adding structured citations | 10 |
| Conflicting statements without requiring a shared paper | 39 (24 submitter pairs) |

The largest conflicting pair in that last row — Ambry Genetics and LabCorp (Women's Health and Genetics), on 12 variants — cannot be found by PMID matching at all, because Ambry cites by author and year. None of those additional variants has been read, and no rate is claimed from them.

## Robustness — do the pipeline's own defects change the answer?

Two independent code reviews found four defects in the pipeline that produced the counts. Measured one at a time against the published numbers, denials outnumber claims in every scenario.

| Scenario | Claims | Denials | Ratio | Basis |
| --- | --- | --- | --- | --- |
| Published, as released | 1,218 | 1,513 | 0.805 | — |
| A · gene-field filter restored | 1,329 | 1,536 | 0.865 | Recomputed |
| B · bullet-aware sentence splitter | 1,218 | 1,513 | 0.805 | Recomputed |
| C · negated claims removed | 1,201 | 1,513 | 0.794 | Estimate, upper bound |
| D · missed denials added | 1,218 | 1,513 | 0.805 | Estimate |

**A is the only defect that moves the number, and the dropped rows are not a random sample.** The gene-field filter discarded 4,007 submissions on panel variants across 2,737 variants, almost all because ClinVar's `SubmittedGeneSymbol` is `-` on those rows. Among the 354 that carry a prose comment, the split is 111 claims to 23 denials — roughly six times more claim-rich than the corpus. That is why restoring them moves the ratio to 0.865, and it belongs in any correction note.

**B is real in principle and empty in practice.** A splitter that also breaks at bullet markers changes the flags on 0 of 32,562 submissions.

**C over-counts, and this is the weakest number in the audit.** The tier-1 pattern flags 17 claim submissions whose every claim sentence looks negated or prospective. Reading the printed examples, most are genuine claims that happen to carry a caveat — *"functional studies suggest the variant had kinase activities that were mildly increased; however, additional evidence is needed"*. The honest figure is closer to 3–5 than to 17, and it requires reading `C_candidate_false_claims.csv` rather than quoting the pattern count.

**D found nothing.** No unflagged submission matches *"functional studies have not (yet) been performed"*.

One independent check sits alongside these. Re-deriving the labels from sentence-level citation attribution reproduces the published classifier's flags on all 4,012 citing submissions — 100%, not approximately.

## What the independent reviews contributed

The analysis was reviewed twice, by two AI coding assistants from different model families — Claude Code and OpenAI Codex — run separately and given the notebook, the data and the draft. Each was asked to re-execute the pipeline and open the cited sources, not to comment on the text.

Both reproduced the counts exactly on the same ClinVar release: 395 MB file, 6,738,642 rows, 32,562 panel submissions. Both confirmed every quotation character for character against the live record pages, and both read all four mechanically flagged variants and reached the same two-of-four verdict.

### What they found that the analysis had not

| Finding | Where it lands in this report | Reviews |
| --- | --- | --- |
| The gene-field filter drops 4,007 submissions on panel variants | Defect A, Robustness | Both |
| The sentence splitter does not break at bullet markers | Defect B, Robustness | Both |
| Some claim sentences are negated or prospective | Defect C, Robustness | Both |
| Structured citations are distributed per submission in the XML release, and per organisation in `var_citations.txt` | Where the citations live | Both |
| A symmetric search flags 7 variants; adding structured citations, 10; dropping the shared-paper requirement, 39 across 24 submitter pairs | Where the citations live | One |
| Ambry Genetics and LabCorp conflict on 12 variants, invisible to PMID matching because Ambry cites by author and year | Where the citations live, Finding 3 | One |
| Table 3 of Yang et al. 2018 lists PS3 for I437T in patient P4 with no assay reported | The worked example | One |
| PMID 24451042 reports p.Ile437Asn at this codon, not p.Ile437Thr | The worked example | One |

The PMID parser carried a fifth defect — it captured only the first number in a comma-separated list, which would have made citation sets look disjoint and inflated apparent divergence. That one was caught by the appendix code's own structural test, not by a reviewer.

### What they corrected

Five statements in earlier drafts were wrong and have been removed. They are listed because each shows the same failure mode, and because a reader should know what the review round changed.

1. **That LabCorp's comment lists no citations.** It cites three PMIDs. The error came from a summary of the record page rather than the comment itself.
2. **That Lepri et al. 2011 is cited by six submitters on the record.** It is nine: six give the PMID in their comment, and three are reachable only by author and year.
3. **That the pattern is confined to two laboratories and their templates.** The unrestricted search contradicts this.
4. **That roughly 87% of denials give no way to check what was reviewed.** The underlying count is right — two denial sentences in the whole corpus carry a citation, and a later pass showed even those two to be artefacts of the splitter defect — but the inference was not: denials cite in a separate sentence. Finding 3 states the corrected version.
5. **That the full text of Lepri et al. 2011 could not be retrieved.** The paper is openly available; the drafting analysis had been blocked by rate limits and read a summary instead.

### What this kind of review does and does not buy

It buys re-execution and source retrieval, which is where every error above was caught. It does not buy independent curation: neither reviewer is a clinical geneticist, and nothing here substitutes for the VCEP's own reading of the literature.

It also has a characteristic failure of its own. Earlier in this project, an automated review asserted a conflict between two versions of the RASopathy specification that do not in fact conflict — because both documents had been read through automated summaries rather than opened. Both reviews were subsequently required to state which sources they opened themselves, and the single-sourced rows in the table above should be read as exactly that: one review, not independently confirmed.

### A third round, on this report

This report was then reviewed itself, against the notebook's stored outputs and the primary sources. Across two passes it found four errors and three imprecisions, all corrected above:

1. **The strata table double-counted.** It paired the flag counts (1,218 and 1,513, which include the 18 both-flagged submissions) with the shares of the disjoint strata (which exclude them), and derived Neither by subtraction — 29,813 instead of 29,849. Finding 1 now states both bases and which figure uses which. This is the report's own version of the failure it documents: a count read on the wrong basis.
2. **PMID 24451042 was attributed to "Lee et al."** It is Lepri et al. 2014, from the same group as Lepri et al. 2011 — which is why Neuberg's comment on the record cites *"Lepri et al., 2011; Lepri et al., 2014"*. The wrong name severed that link.
3. **"Sixteen submissions sit on the record"** presented a pipeline artefact as a property of the record. ClinVar holds eighteen; two are dropped by Defect A.
4. **Ambry Genetics was said to cite Lepri et al. 2011 only in its structured field.** Its comment cites the paper as well, by author and journal rather than by PMID. As written, those passages contradicted the report's own explanation of Ambry's 0.0% citation rate, which was the correct explanation.

The three imprecisions were the two denial sentences, the reading of Lepri et al. 2011 by the other eight submitters, and "match exactly" for the reproductions.

## What this establishes, and what it does not

### Establishes

- Denials outnumber claims across the panel, and the direction survives every measured pipeline defect. The largest single effect moves the ratio from 0.805 to 0.865.
- A claim cites literature 4.6× more often than a denial, and the gap survives inside four of the five laboratories that write both. Denial sentences themselves carry a citation twice in the whole corpus, and under a bullet-aware splitter, never.
- A bibliography-controlled comparison exists on this panel but rests on 29 laboratory pairs. It is a case series, and no threshold in the sweep makes it a rate.
- Two variants carry the pattern the study is about, confirmed by reading, out of four flagged mechanically.
- Sentence-level citation attribution reproduces the published classifier's flags on all 4,012 citing submissions.

### Does not establish

- **No rate of disagreement.** Any percentage here is over templates, not over independent judgements, and the pairs may share upstream bibliographies.
- **No claim about which laboratories the pattern involves.** Both confirmed cases are one submitter pair, Dasa against LabCorp (Women's Health and Genetics), observed twice. Two house templates that disagree would produce exactly this. The 39 variants across 24 submitter pairs that could distinguish the two explanations are unread, and the largest of those pairs is invisible to this pipeline.
- **The tier-1 false-claim estimate over-counts.** It needs reading, not quoting.
- **Two classifier weaknesses remain unquantified.** An inserted adjective can break a denial pattern, and a submission stating that an assay exists but is not VCEP-approved has no label.
- **Nothing about correctness.** No laboratory's reading of the literature is evaluated. The internal criteria each applies to "functional evidence" are not published, and a laboratory may legitimately use the term more broadly than ACMG/AMP uses PS3.

### What would settle it

Three things, in order of cost:

1. **Parse the other two citation channels** — the structured field from the XML release, and author-year references. Both are mechanical and would move the flagged set from 4 variants to at least 10.
2. **Read the 39 variants** where conflicting statements exist without requiring a shared paper. That is a curation task, not a code task, and it is the only route to saying anything about frequency.
3. **Separate the four kinds of evidence a submission might mean by "functional"** — computational prediction, observation in patients, assays of neighbouring variants, and an assay of this variant. Dasa's sentence echoes the ACMG wording for PS3, which concerns the fourth; the papers attached to it belong to the first two.

### Reproducing this

The analysis is a Kaggle notebook that bootstraps the classifier notebook and re-runs its first four cells, so the label basis is identical to the published figures rather than a second implementation of them. It needs `submission_summary.txt.gz` (395 MB) and the classifier notebook attached as an input.

The stored run is from 26–29 September 2026. Four independent reproductions on the same ClinVar release reproduce every reported number: two code reviews, one re-run by the author, and one after the notebook was restructured. One reviewer noted that the printed list of the ten busiest submitter pairs can differ in the tie-break among pairs of count 1; the reported figures do not.

## Sources

- [ClinVar VCV000045345 — SOS1 c.1310T>C (p.Ile437Thr)](https://www.ncbi.nlm.nih.gov/clinvar/variation/45345/)
- [ClinVar VCV000013325 — PTPN11 c.215C>G (p.Ala72Gly)](https://www.ncbi.nlm.nih.gov/clinvar/variation/13325/)
- [ClinVar data downloads — submission\_summary.txt, var\_citations.txt, XML release](https://www.ncbi.nlm.nih.gov/clinvar/docs/downloads/)
- [Lepri et al. 2011, *Hum Mutat*](https://pmc.ncbi.nlm.nih.gov/articles/PMC3118925)
- [Kiel & Serrano 2014, *Mol Syst Biol*](https://www.embopress.org/doi/full/10.1002/msb.20145092)
- [Yang et al. 2018, *BMC Med Genet*](https://link.springer.com/article/10.1186/s12881-018-0730-6)
- [Lepri et al. 2014, *BMC Med Genet*](https://link.springer.com/article/10.1186/1471-2350-15-14)
- [Updated ACMG/AMP specifications for the ClinGen RASopathy expert panels, 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12151217/)
- [ClinGen RASopathy VCEP specification for SOS1, GN041 v2.3.0](https://cspec.genome.network/cspec/ui/svi/doc/GN041)

Submitter text is quoted verbatim from ClinVar, retrieved 26 September 2026. Quotations and accessions were confirmed character for character by two independent reviews against the live record page, the TSV and the XML release.
