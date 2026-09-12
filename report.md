# There is a code for finding functional evidence, and none for not finding it

*A count of what laboratories write about functional evidence across a
13-gene RASopathy panel in ClinVar, and what the count could not settle.*

Fernando dos Santos Rodrigues · September 2026
Data retrieved 14 September 2026 · code and labels linked at the end

---

## Summary

Across 32,569 ClinVar submissions for 13 RAS-MAPK genes, submissions that assert
functional evidence exists and submissions that assert it is absent occur at
roughly the same rate — 1,216 against 1,512. The aggregate is not informative,
because a single submitter accounts for 62% of the absence statements.

The per-laboratory picture is more useful, and it is asymmetric. **Nineteen of
the 26 laboratories that make at least one claim about functional evidence never
record an absence.** The median laboratory files zero absence statements per
claim.

This is not carelessness. The ACMG/AMP framework provides a code for asserting
that functional evidence exists — PS3, and 147 submissions in this panel assert
it through the code alone, with no prose sentence doing so. It provides no code
for having searched and found nothing. Recording an absence requires free text,
and free text is optional: **32.4% of submissions in this panel carry no comment
field**.

A second finding qualifies the first. A blinded re-read of 50 submissions by one
untrained reader agreed with the automated classification on 40.4% of cases
(Cohen's κ = 0.104), and the disagreement was concentrated in one class:
agreement was 50% for claims, 44% for neither, and **27% for denials**. The
boundary between *"no functional studies have been performed"* and *"this
variant has not been reported in the literature"* does not survive two
independent readings — and under the framework those are PS3 and PS4, different
criteria entirely.

---

## 1. Why this was measured

A ClinVar submission may state in free text that functional evidence supports
its classification. Nothing links that statement to an assay, and nothing checks
it.

The question came from assembling assay columns for this panel: how often is such
evidence said to be absent, as opposed to present? What makes it hard to answer
shows up wherever two laboratories disagree about the same variant. Forty-four
variants here carry both a claim and an absence statement, from different
submitters.

One of the forty-four, quoted as an illustration rather than as a
representative case: SOS1 c.1310T>C (p.Ile437Thr), VCV000045345, is called
pathogenic or likely pathogenic by all 16 submissions in this snapshot — 14
Pathogenic, 2 Likely pathogenic — and eight of them describe a de novo
occurrence. Two submitters describe its functional evidence in opposite terms:

> *"To our knowledge, no experimental evidence demonstrating an impact on protein
> function has been reported."* — Women's Health and Genetics / LabCorp,
> SCV000918268.3, November 2023

> *"Functional evidence supports a deleterious effect on the gene or gene
> product"* — Dasa, SCV007599104.1, January 2026

Two PMIDs appear in both submissions — 21387466 and 30039904 — and the methods
of each were read for this report. Lepri et al. (*Human Mutation* 2011) is a
mutation-scanning study: DHPLC and Sanger sequencing, parental genotyping, more
than 300 population-matched controls, SIFT and PolyPhen, and modelling of residue
positions onto an existing crystal structure with electrostatic-potential
calculations. For c.1310T>C it records a confirmed de novo occurrence and a
predicted effect, and its structural reading is hedged — the substitution
*"might"* perturb the PH domain and *"possibly"* reorient the histone-fold
domain. Prasad et al. (*Pediatric Blood & Cancer* 2018) is a case report of
colorectal cancer in a child with Noonan syndrome; its methods state that
*"pathogenicity of germline variants was determined through a review of the
published literature and databases"*, and it cites Lepri for this variant.

Neither shared citation contains an experiment on p.Ile437Thr. What they support
is PS2, PM2 and PP3, and arguably PM1 — not PS3. So the two laboratories are not
reading the same experiment differently: there is no experiment in the papers
they share. They are disagreeing about whether structural modelling and
computational prediction count as functional evidence at all. That is a statement
about the two citations held in common and nothing more — this analysis reads
comment text, not the full reference list behind a submission. The question it
raises is not about one variant: how often does either statement appear, and is
the distinction between them stable?

*(Two Labcorp entities submit on this variant and they are separate submitters
throughout this report: Women's Health and Genetics / LabCorp, quoted above, and
Labcorp Genetics (formerly Invitae). They behave differently — see Table 2.)*

## 2. What was counted

Every ClinVar submission for BRAF, HRAS, KRAS, LZTR1, MAP2K1, MAP2K2, NRAS,
PTPN11, RAF1, RIT1, SHOC2, SOS1 and SOS2 — 32,569 submissions on 17,368
variants, from 278 submitters.

Each comment was classified into three mutually informative flags:

- **claim** — asserts an experiment was performed bearing on this variant
- **denial** — asserts such evidence is absent, lacking, or unconfirmed
- **neither** — a predictor score, a vendor model, a structural inference, a
  clinical observation, or silence on the question

The third class matters. A submission stating that in-silico tools predict a
damaging effect is making a PP3 statement, not a PS3 one, and treating the two
as equivalent is the error this work exists to avoid.

**Table 1. What the panel's submissions say.**

| | n | share |
|---|---:|---:|
| submissions | 32,569 | |
| no comment field at all | 10,556 | 32.4% |
| codes or stub only | 771 | 2.4% |
| prose comment | 21,242 | 65.2% |
| — asserting functional evidence exists | 1,216 | 3.7% |
| — asserting it is absent | 1,512 | 4.6% |
| — both | 18 | |
| stating absence from the case-report literature | 5,922 | 18.2% |

The last row is separated deliberately. *"This variant has not been reported in
the literature in individuals affected with…"* is a statement about case reports.
An earlier version of this analysis counted those as denials of functional
evidence and reported a ratio of 5.9 absence statements per claim. That number
was wrong by roughly a factor of six, and the correction is the reason the
literature row is now counted apart.

## 3. The asymmetry

**Table 2. The most active submitters, by what they write.**

| submitter | submissions | claims | denials | per claim |
|---|---:|---:|---:|---:|
| Labcorp Genetics (Invitae) | 11,478 | 228 | 282 | 1.24 |
| Ambry Genetics | 6,784 | 178 | 68 | 0.38 |
| GeneDx | 3,590 | 164 | 73 | 0.45 |
| Women's Health and Genetics / LabCorp | 1,695 | 109 | 934 | 8.57 |
| CeGaT | 812 | 28 | 0 | 0.00 |
| Laboratory for Molecular Medicine | 718 | 51 | 0 | 0.00 |
| PreventionGenetics | 644 | 42 | 0 | 0.00 |
| ClinGen RASopathy VCEP | 369 | 76 | 0 | 0.00 |
| Mayo Clinic Laboratories | 274 | 28 | 0 | 0.00 |
| 3billion | 207 | 35 | 0 | 0.00 |
| Dasa | 176 | 42 | 0 | 0.00 |

Two things are visible here that the aggregate hides.

**One laboratory carries the absence statements.** Women's Health and Genetics
produces 62% of every absence statement in the panel, from 5% of its
submissions. Any panel-wide ratio is a statement about that laboratory's
template, not about the field. The earlier 5.9 figure was this effect compounded
by the literature-sentence error.

**Nineteen of 26 vocal laboratories never record an absence.** They file claims
— some of them frequently — and never the converse. This includes the RASopathy
VCEP's own submissions: 76 claims, no absence statements.

The denominator is worth stating precisely: 46 laboratories filed at least 30
submissions, and 26 of those made at least one claim. Nineteen of those 26 never
filed an absence statement. No laboratory in this panel files absence statements
without also filing claims, so the ordering is not an artefact of the cutoff.

## 4. Why the asymmetry is structural

The framework is not symmetric, and the submissions show it.

PS3 exists, it is machine-readable, and **147 submissions in this panel assert
functional evidence through the code alone** — the comment carries the criterion
and no prose sentence asserting an experiment. Most are short strings of ACMG
codes; the median is about fifty characters. A laboratory that has functional
data has a compact, structured way to say so.

There is no counterpart. A laboratory that searched and found nothing has only
free text, and free text is optional — a third of this panel's submissions have
none. The two situations are not equally recordable, so they are not equally
recorded.

The consequence for a curator is concrete: the absence of a PS3 code carries no
information. It may mean the submitter looked and found nothing, or looked and
found something that did not meet their threshold, or never looked. Those are
different states and the record does not distinguish them.

## 5. What could not be settled

### The distinction is not stable between readers

Fifty submissions were drawn at random from the labelled set, stripped of their
classification, and read blind against the same written rubric by the author,
who is not a trained variant curator. That is the only human reading in this
work, and one untrained reader is a weak test — but it is a test the labels had
not previously had at all.

**Table 3. Blind re-read, 47 submissions where both readers committed.**

| | |
|---|---:|
| observed agreement | 40.4% (95% CI 27.6–54.7%) |
| chance agreement, from the marginals | 33.5% |
| Cohen's κ | 0.104 |

Agreement was not uniform across classes:

| class assigned | agreement |
|---|---:|
| claim | 8 of 16 (50%) |
| neither | 7 of 16 (44%) |
| **denial** | **4 of 15 (27%)** |

The unstable class is denial, and the submissions themselves show why.
*"Has not been previously published as pathogenic or benign"*, *"not observed at
significant frequency"* and *"functional studies have not been performed"* can
all be read as denying functional evidence, and only the third is one. Under the
framework the first two bear on PS4 and BS1.

These figures include one correction. The key contained a label the audit trail
had already identified as wrong: a submission reading *"A functional assay has
been performed on c.775T>G (p.Ser259Ala), but … it has not been assessed for PS3
at this time"* was recorded as a denial, when an assay plainly exists. The human
reader called it a claim. Scoring against the uncorrected key gives 38.3%
agreement and κ = 0.076; the figures above use the corrected label. The
correction moves the result in the classifier's favour and is reported here for
that reason.

This bears on every figure derived from the three classes — the rates in Table 1,
the per-laboratory ratios in Table 2. It does not bear on the 32.4% with no
comment, the 147 bare PS3 assertions, or the structural asymmetry, which come
from the record rather than from the classification.

### Provenance of the labels

The classifier was scored against 450 labelled submissions across five
sequential samples. Only some of those are evaluation. Each sample was drawn
after the version it first tested had been frozen, but two of the five were
later used to write patterns and became training sets; the distinction is
recorded per sample in the published ledger. On a sample from which no pattern
has ever been written, the classifier reached 97% precision for claims and 100%
for denials.

**Those 450 labels were produced by a language model adjudicating each
submission against a written rubric. No human curator read them.** The rubric,
every verdict and the free-text reasoning behind each are published, so any
reader can disagree line by line. The blind re-read in Table 3 is the only human
reading in the work.

### One reading decision moves the result more than any defect

One laboratory files 2,523 submissions with an and/or boilerplate: *"intact
protein function and/or RNA analysis and/or in silico models"*. The sentence
never says which was done. All 2,523 are currently classified as neither.

If a reviewer decides they are claims, claims rise from 1,216 to 3,739 and the
panel ratio falls from 1.24 to 0.40. **That single judgement moves the figure
more than every classifier defect found across six audits combined**, and no
pattern settles it — the ambiguity is in the source sentence. The figures above
exclude them, and a reader who disagrees can recompute.

### Not measured at all

Whether any claim is true. That requires reading the cited publications, and a
feasibility check found that only 26% of the PMIDs behind these claims have open
full text — a functional assay is described in Methods, not in the abstract. The
two publications shared by the submissions quoted in section 1 were read; no
others were.

Whether an assay was performed on the variant in hand or on a neighbouring one
at the same codon. That distinction is PS3 against PM5, and deciding it requires
reading the sentence rather than matching it.

## 6. What this might be worth to the panel

Three observations, offered as data rather than as recommendations. The
adjudication is the panel's.

**The absence of PS3 is not evidence of absence.** Nineteen of 26 vocal
laboratories never record having searched. A curator reading a ClinVar record
with no PS3 cannot distinguish "searched, found nothing" from "did not search",
and this analysis suggests the second is far more common than the record implies.

**A structured way to record a negative search would be cheap.** The asymmetry
is in the submission format, not in laboratory practice. If a submitter could
record that a search was performed and returned nothing — as a code rather than
as prose — the information would survive into the record, and the 32.4% of
submissions with no comment field would not be silent by default.

**If the panel considers a specification change here, the denial category needs
a definition before it needs a code.** This work found 27% inter-reader agreement
on what counts as denying functional evidence. A code inherits whatever
ambiguity its definition carries, and the distinction from *"not reported in the
literature"* — PS4 territory — is where the disagreement concentrates.

## 7. Data and code

Both notebooks run end to end from public sources and write every intermediate
table.

- Panel classification, 32,569 submissions — `are-functional-evidence-claims-in-clinvar-auditable`
- Blind inter-rater check, 50 submissions — `is-a-functional-evidence-claim-a-stable-category`
- The five labelled samples, with every verdict and its reasoning — dataset `clinvar-claim-audit-labels`

Source: ClinVar `submission_summary.txt.gz`, retrieved 14 September 2026.
ClinVar is a live resource; these counts are a snapshot, and submission counts
for a given variant may differ from the figure shown on the ClinVar website,
which is not filtered to the panel's gene symbols.

**An invitation.** The same fifty submissions are in the second notebook, in the
order they were read. Replacing one string with your own fifty verdicts scores
you against the adjudicator and against the author's reading, and saves all three
readings side by side. The second comparison is the one worth having: if two
readers agree with each other far more than either agrees with the automated
adjudication, the instability is in the adjudication rather than in the category,
and the κ above should be read differently. This work cannot settle which of
those it is, because it has only one reader. A panel that does this
professionally can.
