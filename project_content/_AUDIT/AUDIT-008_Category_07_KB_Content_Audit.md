---
id: FIX-ERP2-AUDIT-008
title: Category 07 KB — Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-16
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 16 Category 07 KB files, their citations into the module repository and the content register, and cross-register integrity across CG-002, CG-009, CG-010 and the Master Index
mandate: Audit required on completion of Category 07 authoring (rule CM-R9)
extends: AUDIT-001, AUDIT-002, AUDIT-003, AUDIT-004, AUDIT-005, AUDIT-006, AUDIT-007
---

# Category 07 `KB` — Content Audit
### 16 files · 234 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F7 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction, never by reading what a
document says about itself (`RG-06`, `CP-11`). **Enumeration date 2026-08-16.**

Six category-specific extractions were run in addition to the standard checklist, because Category
07 cites both the module repository and the content register more densely than any prior category
— 93 distinct content identifiers and 40 distinct business-rule identifiers across 16 files:

| Extraction | What was compared |
|---|---|
| **X1** | Every content identifier (`CG-` … `RF-`) cited in a `KB` file against the 452 register rows |
| **X2** | Every `BRU-` identifier cited against `05-05`, with `BRU-KMS-*` separated and checked against `M61` §9 |
| **X3** | Every `KPI-` identifier cited against `06-02`, with `KPI-C61-*` separated and checked against `M61` §15 |
| **X4** | Every `FR-KMS-` identifier cited against `M61` §5 |
| **X5** | Every `Rnn`, `Mnn` and `Pnn` identifier against `05-04`, `02-02` and `04-00` |
| **X6** | Every inbound `KB-013 §n` section reference against `KB-013`'s actual section numbering |

**Eleven findings — 1 critical, 4 high, 5 medium, 1 low.** Two were remediated during the audit;
nine are open and seven of those are owned outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | 1 | 0 |
| High | 4 | 0 | 4 |
| Medium | 5 | 1 | 4 |
| Low | 1 | 0 | 1 |

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 16 of 16 ✅ |
| **A2** Total written | **234 of 452**, enumerated 2026-08-16 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **A6** Register entries with no file | Zero ✅ |
| **B1** ID uniqueness | 16 unique ✅ |
| **B2** Contiguity `KB-001`…`KB-016` | No gaps ✅ |
| **B4** File name matches ID | 16 of 16, byte-identical to the register rows ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 16 of 16 ✅ |
| **D1** Internal links resolve | **279 relative links, zero broken** ✅ |
| **D2** Files in their declared folder | 16 of 16 flat in `07_Knowledge_Base_and_Technical_Library/`, no subfolders, matching Master Index §3.2 ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | All 11 `TPL_Knowledge_Article.md` sections present in all 13 article files; all 6 `TPL_Content_File_Front_Matter.md` sections present in all 3 governance files ✅ *(ordering exception in `KB-013` — see finding KB-10)* |
| **F1** Front matter complete | **All 24 required keys present in all 16** ✅ |
| **X1** Content-ID citations | **93 distinct identifiers cited, all 93 registered** ✅ |
| **X2** `BRU-` citations | 40 distinct; 24 resolve in `05-05`, **16 `BRU-KMS-*` resolve in `M61` §9 and are cited as module rules throughout** ✅ |
| **X3** `KPI-` citations | `KPI-004`, `-010`, `-013`, `-025`, `-026` resolve in `06-02`; 8 `KPI-C61-*` resolve in `M61` §15 ✅ |
| **X4** `FR-KMS-` citations | All resolve in `M61` §5 ✅ |
| **X5** Role, module and portal integrity | `R09`–`R38` all within the `05-04` register; `M01`–`M66` all within `M01`–`M67`; `P01`–`P11` all valid ✅ |
| **X6** `KB-013` section references | **31 inbound references from 11 files, all resolving to existing sections** ✅ |

### 2.1 Cross-register reconciliation — gate F7

Every dimension the governance set constrains for this category was regenerated from the files on
disk and compared. **All seven reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---:|---:|:--:|
| File count | Master Index §4 | 16 | 16 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 | 0 / 4 / 11 / 1 | 0 / 4 / 11 / 1 | ✅ |
| Wave per file | Master Index §4 rows | 16 rows | All 16 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 1 / 0 / 12 / 1 / 2 | 1 / 0 / 12 / 1 / 2 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 13 / 3 | 13 / 3 | ✅ |
| Template allocation | `CG-009` §3 | 13 Knowledge Article / 3 generic | 13 / 3 | ✅ |
| Subfolder allocation | Master Index §3.2 | 16 flat | 16 flat | ✅ |

`CG-009` §3 and `CG-010` §3.2 both name **`KB-001`, `KB-002`, `KB-015`** as the three governance
files taking template 1 and English-only status. Those are exactly the three marked
`bilingual: no` with `template: TPL_Content_File_Front_Matter.md`. ✅

> **A reconciliation worth stating explicitly, because it looks like a contradiction and is not.**
> `CG-009` and `CG-010` group `KB-001`, `KB-002` and `KB-015` together as "governance". `CG-002`
> §4.1 allows only **two** class-`E` files in this category. These are different dimensions —
> template and language versus consequence-if-wrong — and they do not have to agree. `KB-002`
> governs the shape of safety-bearing repair procedures authored by 80–150 technicians, which is
> operational-critical (`C`), while being English-only governance content for template purposes.
> `KB-016` is class `D` because it is the technician-facing surface. Both allocations were made
> deliberately to satisfy `CG-002` §4.1 exactly, and the reasoning is recorded here so that a
> future auditor does not "correct" one of them into a divergence.

---

## 3. Findings

### KB-01 — Two `LG` identifiers were invented from plausible-sounding titles

**Severity: CRITICAL · Status: FIXED · Owner: Programme Content Lead**

**What was found.** While authoring `KB-003` and `KB-010` I cited two Category 10 files by
identifier *and title*:

| Cited as | Actually is |
|---|---|
| `LG-020` Intellectual Property and Content Licensing | **`LG-020` Acceptable Use and Internal Access Policy** |
| `LG-014` Product Safety and Recall Handling | **`LG-014` Refund, Cancellation and Compensation Policy** |

Neither title exists anywhere in the register. Both were constructed because a file with that
purpose *ought* to exist, and a number was attached to make the citation look resolved.

**Why it matters.** This is the **seventh recorded occurrence of the same failure mode in this
programme**: `00-07` H2-04/H2-05 for custom-development and KPI identifiers; the portal audit as
X-01; `SP-006` §3.2 for nine `SOD-` collisions; and `AUDIT-006` **SP-01**, where 29 `TR-` citations
were wrong and 7 pointed at identifiers that cannot exist. It is the failure mode the register
governance in `CG-005` and rule `RG-01` exist to prevent.

The consequence here would have been worse than a broken link. `KB-003` `LB-01` makes licence
classification a **hard gate** operated by Legal Counsel, and it cited a non-existent IP policy as
the thing Legal would classify against. `KB-010` §2 states a recall liability and cited a
non-existent recall policy as its legal framing. **Both files would have shipped asserting legal
cover that does not exist** — which is precisely "a required artefact assumed present when absent",
the definition of Critical in `AUDIT_Checklist_Recurring.md`.

**Why it happened — reported openly.** I wrote the Related Documents tables while authoring each
file, allocating an `LG` number from an impression of the register's shape rather than extracting
it. The `KB-010` citation carried an "*(if registered)*" hedge, which is worse than no hedge: it
records that I knew I had not checked and cited it anyway.

**Fixed.** The 24-row `LG` register was extracted and read row by row. Both citations were replaced
with the correct nearest artefacts, and — more importantly — **the absence each wrong citation was
papering over was promoted into a finding in its own right** (KB-02 and KB-03) and into an open
item in the affected file. X1 was then re-run across all 16 files against all 452 register rows:
**93 identifiers cited, zero outside the register.**

**Governance consequence.** `CP-04` requires every file to trace to a specification, and `CM-R1`
makes the register authoritative. Neither rule prevented this, because both are checks on whether
a citation *exists*, applied after authoring. **Proposed rule `RG-08`, for `CG-005`: a citation to
a file in a category that has not yet been authored must be extracted from the register at the
moment of writing, and the file's title must be quoted from the register row, never paraphrased.**
A paraphrased title is unfalsifiable at review; a quoted one fails immediately.

---

### KB-02 — No registered `LG` file covers third-party intellectual property or content licensing

**Severity: HIGH · Status: OPEN · Owner: Legal Counsel with Programme Content Lead**

**What was found.** Correcting KB-01 exposed a real gap. The `LG` register contains 24 files
covering portal terms, privacy, data retention, service and warranty terms, SLA, managed services,
data destruction, e-waste EPR, e-signature, acceptable use, ISMS, quality policy, ethics and
regulatory disclosure. **None addresses the company's use of third-party intellectual property.**

`KB-003` requires Legal Counsel to assign a `licence_class` to every manual, diagram and schematic
the company holds — a hard gate (`LB-01`) — and that classification propagates to every knowledge
article citing the entry (`LB-03`, `KA-09`). **There is no policy for Legal to classify against.**

**Why it matters.** `M61` §9 `BRU-KMS-16` makes brand-agreement compliance a hard rule and `M61`
Q-03 already flags brand documentation rights as unresolved and blocking. The technical library
cannot be built lawfully on ad-hoc per-entry judgements, and the exposure compounds with every
ingestion. `KB-003`'s `restricted_pending_confirmation` class is a deliberate holding position, not
a resolution — and a register that is predominantly "pending confirmation" does not support the
offline distribution `P02` requires.

**Remediation instruction.** Legal Counsel to determine whether the obligation belongs in a new
`LG` file — which requires a register change under `CP-02`, since `LG` IDs are permanent and the
category is declared at 24 — or as a scoped extension to `LG-020`. Recorded as `KB-003` `O-06`.

---

### KB-03 — No registered `LG` file covers product safety or recall handling

**Severity: HIGH · Status: OPEN · Owner: Legal Counsel with Quality Manager**

**What was found.** The same row-by-row check found no `LG` artefact addressing recall liability,
the company's duty on receipt of a manufacturer recall, or customer-notification obligations.
`LG-013` covers service and warranty terms and exclusions; `LG-014` covers refunds, cancellation
and compensation; `LG-024` is a statutory notice register. None reaches recall.

**Why it matters.** `KB-010` §2 states, as a `DANGER`-class control, that failing to act on a
recall notification is a serious liability that can put brand authorisation at risk. `M61` §9
`BRU-KMS-15` routes recalls to `M09` and `M01` for execution. **The content file is currently
carrying that legal obligation on its own**, with an acknowledgement-tracking regime and an
escalation ladder it designed itself, and no legal artefact behind it.

**Compounding factor.** `KB-010` is `P1`/`W4` and `M61` is `W6`, so between now and W6 there is no
system support for bulletin distribution or acknowledgement tracking — while brand relationships
and recalls exist from day one. This is recorded as `KB-010` `O-01` and it interacts directly with
finding KB-05.

**Remediation instruction.** Legal Counsel with Quality Manager to establish the recall-handling
legal position and decide where it lives. `CG-013` escalation applies. Recorded as `KB-010` `O-05`.

---

### KB-04 — `KB-013` is scheduled at W5 but is the cited safety source for files needed at W2

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead with HSE Lead and Operations Director**

**What was found.** Extraction X6 counted **31 inbound section references to `KB-013` from 11 of
the other 15 files in the category**. `KB-002` `AU-06e` makes the link mandatory: every article with
a `hazard_class` other than `none` must carry a safety block *and* link to `KB-013`.

The register places `KB-013` at **`P1`/`W5`**. Of the eleven files citing it, **eight are scheduled
at `W2`** — including all four troubleshooting guide sets, which between them enumerate 160
articles covering lithium cells, refrigerants, mains isolation, microwave high-voltage capacitors
and ESD control.

| | |
|---|---|
| Files citing `KB-013` | 11 |
| Of those, at `W2` | 8 |
| Inbound section references | 31 |
| `KB-013` wave | **W5** |

**Why it matters.** The hazards are present from the first day a technician opens a device. A
safety data source arriving three waves after the work it governs is not a late document — it is a
control that does not exist when it is needed, and the articles that depend on it either ship
without their mandated safety linkage or do not ship at all. `CG-002` §4.1 classifies `KB-013` as
the category's only class-**A** file, requiring external verification before approval, which makes
it the *slowest* file in the category as well as the earliest needed.

**Remediation instruction.** Either amend the register row to `W1`/`W2`, or split the file so that
the ESD, battery and refrigerant sections issue at W2 with the remainder at W5. **The content
function cannot make this change unilaterally** — `CM-R1` makes the register authoritative.
Recorded as `KB-013` `O-01`.

---

### KB-05 — `M61` lands at W6; eight `KB` files depend on capabilities that do not exist until then

**Severity: HIGH · Status: OPEN · Owner: Quality Manager with Operations Director and CTO**

**What was found.** `M61` is `P2`/`W6`. Category 07 content is required from `W2` — twelve of the
sixteen files carry `wave: W2`. Eight files specify controls that are **operated by `M61`
capabilities**, not by people:

| File | Depends on | `M61` reference |
|---|---|---|
| `KB-001` | Context surfacing, offline pack computation, corpus boundary | T-01, T-07, FR-KMS-015/017 |
| `KB-002` | Improvement queue, completeness scoring, review gating | FR-KMS-011/027, `BRU-KMS-02` |
| `KB-003` | Library entries, OCR indexing, extract distribution | FR-KMS-004/012, T-13 |
| `KB-008` | Corpus admission by confidence | `BRU-KMS-12` |
| `KB-010` | Bulletin distribution and **acknowledgement tracking** | FR-KMS-034, AUT-KMS-12/13/14 |
| `KB-011` | Signature matching and occurrence counting | FR-KMS-033 |
| `KB-015` | Computed health, visible overdue marking, automatic purge | FR-KMS-031/032, `BRU-KMS-05`/`-06` |
| `KB-016` | Offline pack computation, sync, purge propagation | FR-KMS-017/018, T-01/T-03 |

**Why it matters.** `M61` §16.3 already records this in its own words, and it is worth quoting
because the module authors reached the same conclusion independently:

> *"M61 is P2/W6, but the capability risk it addresses is rated **High** and exists from day one.
> If a senior specialist leaves in Wave 2, nothing in the programme captures what they knew."*

`M61` Q-02 asks whether a manual capture programme should start in Wave 2. **This audit extends
that question with measured scope**: it is not only capture that is unsupported for four waves —
it is bulletin acknowledgement (a liability control, KB-03), staleness marking (`BRU-KMS-06`),
corpus purging (`BRU-KMS-05`) and offline pack currency (`KPI-C61-08`, target zero stale articles).

**Remediation instruction.** Decide whether Category 07 content is (a) authored to W2 and operated
manually until W6, (b) deferred to W6 and `P02` ships without its knowledge layer, or (c) `M61` is
partially pulled forward. **Option (b) contradicts a `P02` non-negotiable requirement.** Each file
records an interim-control open item; there is no interim control for acknowledgement tracking.

---

### KB-06 — The register descriptions for `KB-004` and `KB-007` both claim server and storage

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Technical Director**

**What was found.** Master Index §4 describes `KB-004` as *"Laptop, desktop, printer, **server,
storage** and peripheral diagnostic and repair guidance"* and `KB-007` as *"**Rack server, RAID/NAS**,
networking, UPS and surveillance system guidance"*. Read literally, both own the same device class.

**Why it matters.** Two authoring teams working to these descriptions produce either a gap or a
duplicate, and `CP-01` prohibits authoring content in two places. The two files also sit in
different waves (W2 and W4) and carry different approval regimes — `KB-007` requires dual HSE and
CTO approval because of the irreversible-data-loss class of harm.

**Resolved in-file, pending register correction.** `KB-004` §1 and `KB-007` §1 adopt a **blast-radius
rule**: a device that takes down one user belongs to `KB-004`; a device that takes down a business
belongs to `KB-007`. The rule is stated identically in both files and cross-referenced. It has not
been applied to the register rows, because `CM-R1` makes the register authoritative and a content
file may not amend it.

**Remediation instruction.** Amend the two Master Index §4 description cells. Recorded as `KB-004`
`O-02`.

---

### KB-07 — `KB-012` is `P3`/`W5`, but five of its twenty-two guides are needed at W1

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Technical Director and HSE Lead**

**What was found.** `KB-012` carries the lowest priority in the category. Its guide inventory
contains five electrical-safety guides — digital multimeter, clamp meter, insulation tester, bench
power supply and ESD station — whose content is the measurement-category rule and the
current-range rule. Both are hazards from the first week a technician holds a meter.

`KB-012` §12 splits the set by actual need: 5 guides at W1, 5 at W2 with the refrigerant set, 4 at
W2 with the rework set, 3 at W4, and 5 at W5 matching the register placement.

**Why it matters.** `KB-012` §2 records the arc-flash mechanism as a `DANGER`-class hazard. A
`P3` priority on the file that carries it means it is the first thing deprioritised when authoring
capacity is short — which is exactly when technicians are busiest.

**Remediation instruction.** Either amend the register row, or record a documented exception
allowing the safety subset to be issued ahead of the file's stated wave. Recorded as `KB-012`
`O-01`. **Not resolved in-file** — the file explicitly declines to rewrite its own priority.

---

### KB-08 — `KB-014` is `W5`, but norm seeding is required at W1 for costing and quoting

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with Operations Director and Finance Manager**

**What was found.** `MD-025` is `P0`/`W1` and carries `standard_minutes` as a **mandatory** column
on every resolution code, explicitly identified as the labour norm feeding `KB-014` and costing.
`KB-014` — which defines what those numbers mean, how they are set and what they may be used for —
is `P2`/`W5`.

`KB-014` §12 phases the rollout: every code seeded with an honest `estimate`-basis norm at W1 so
that `M54` can cost a job and `M36` can quote one, with `RT-15` barring provisional norms from
incentive calculation until they are validated.

**Why it matters.** Either `MD-025` ships at W1 with `standard_minutes` populated and no governing
policy — in which case the numbers are set by whoever needs them, which §1.1 of `KB-014` identifies
as the mechanism by which norms are quietly corrupted — or it ships with the column empty, and
`M54` cannot cost a job for four waves.

**Remediation instruction.** Bring the `KB-014` phase-1 seeding rules forward to W1, or record why
not. Recorded as `KB-014` `O-01`.

---

### KB-09 — `KB-016` and `TR-022` may be the same artefact produced by two workstreams

**Severity: MEDIUM · Status: OPEN · Owner: Programme Content Lead with L&D and Content Design**

**What was found.** `TR-022` is registered as *"Job Aid and Quick Reference Library — one-page task
references for the twenty most frequent tasks per role"*, `P1`/`W1`, owned by L&D. `KB-016` is
registered as *"the offline-packaged quick-reference set shipped inside `P02`"*, `P2`/`W2`, owned by
Technical with Content Design.

For a field technician — the largest single audience for both — these are plausibly the same
artefact: a short, task-focused reference used at the point of work. Neither register row states a
boundary against the other.

**Why it matters.** `CP-01` states that no content is authored in two places, and a file that would
duplicate another references it instead. Two workstreams in different waves with different owners
producing overlapping reference content for the same audience is the exact condition `CP-01`
prohibits. It is cheaper to resolve now than after both are authored.

**Remediation instruction.** Define the boundary before either is authored. A defensible split is
that `TR-022` covers **system tasks** ("how do I record a resolution in `P02`") while `KB-016`
covers **technical and safety decisions** ("is this battery safe to handle") — but that is a
proposal, not a decision. Recorded as `KB-016` `O-05`.

---

### KB-10 — `TPL_Knowledge_Article.md` has no register or hazard-data variant

**Severity: MEDIUM · Status: FIXED (declared and contained) · Owner: Content Design with Programme Content Lead**

**What was found.** `CG-009` §3 allocates template 7, `TPL_Knowledge_Article.md`, to all thirteen
non-governance `KB` files. That template is designed for a single troubleshooting article: Safety,
Symptoms, Likely Causes, Diagnostic Procedure, Repair Procedure, Parts, Verification and QC,
Resolution Coding, Escalation.

Six of the thirteen files are **registers**, not articles — `KB-003`, `KB-008`, `KB-009`, `KB-010`,
`KB-011`, `KB-014` — and one, `KB-013`, is a hazard-data reference cited by section number from
eleven other files.

**How it was contained.** The template's own header table declares four article types —
Procedure, Reference, Troubleshooting, **Bulletin** — which accommodates registers directly. All
thirteen files retain every template section in template order, with register-level interpretation
stated in the heading where a section has no procedural meaning, and additions justified where they
appear. **E7 passes on all thirteen.**

`KB-013` is the single exception on *ordering*. Extraction X6 found **31 inbound references to its
§3–§6** — ESD, battery, refrigerant, chemicals — from eleven files. Renumbering to place Symptoms
at §3 would have broken thirty of those references inside a safety document. The file therefore
places its four hazard-data sections at §3–§6 and the template's remaining sections at §7–§14, in
template order, with no section removed. **The adaptation is declared in the file's header block
with its reason.**

**Why it is reported rather than silently accepted.** `CP-09` states that templates are enforced
and that files which do not conform fail the `CG-008` Definition of Done. A file that adapts a
template without saying so is drift; one that declares the adaptation and routes the underlying
defect to the template's owner is not. **The defect is in the template set, not in the file.**

**Remediation instruction.** Content Design to add either a register variant and a hazard-data
variant to `_templates/`, or a documented conformance note in `CG-009` §3 permitting the two
adaptations. Until then, `KB-013` carries the exception explicitly.

---

### KB-11 — Symptom-code bindings across four guide sets are placeholders, not registered codes

**Severity: LOW · Status: OPEN · Owner: Technical analyst (MDM)**

**What was found.** `KB-004`, `KB-005`, `KB-006` and `KB-007` each carry a §3 symptom index binding
customer-reported symptoms to `MD-024` `SYM-` codes. `MD-024` is authored but **not populated** —
its §7 states an expected 1,500–4,000 codes and its sample rows contain four. Most bindings in the
four guide sets are therefore shown descriptively (`SYM-` display-blank, `SYM-` thermal) rather
than as allocated codes.

**Why it is Low and not higher.** The correct behaviour was followed: `KA-02` and `MD-024` `FLT-05`
prohibit minting codes outside the owning register, and all four files record the gap as a blocking
open item rather than inventing codes to make the tables look complete. **This is the KB-01 failure
mode correctly avoided**, four files in a row, and it is recorded here as evidence that the control
works when it is applied at the point of writing.

**Remediation instruction.** `MD-024` population must precede article authoring in all four sets.
Recorded as `KB-004` `O-04`, `KB-005` `O-03`, `KB-006` `O-03`, `KB-007` `O-07`.

---

## 4. Remediation applied during this audit

| # | Change | File |
|---|---|---|
| 1 | `LG-020` citation corrected from an invented title to *Acceptable Use and Internal Access Policy*, with its actual relevance stated and its inapplicability to IP licensing recorded | `KB-003` §1, §14 |
| 2 | New open item `O-06` added recording the absence of any IP-licensing legal artefact, cross-referenced to finding KB-02 | `KB-003` |
| 3 | `LG-014` citation replaced with `LG-013` and `LG-024`, with an explicit statement that neither covers recall handling | `KB-010` §12 |
| 4 | `KB-010` `O-05` rewritten to record that the 24-row `LG` register was checked row by row, naming the three nearest files and what each actually covers | `KB-010` |
| 5 | `LG-016` title corrected from *Remote Access and Managed Services Terms* to the registered *Managed Services and Remote Access Consent Terms* | `KB-007` §13 |
| 6 | X1 re-run across all 16 files after correction: **93 identifiers, zero outside the register** | — |

---

## 5. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | Adopt proposed rule **`RG-08`** into `CG-005`: a citation to a file in an unauthored category must be extracted from the register at the moment of writing, and its title **quoted**, never paraphrased. Seven recorded occurrences of this failure mode is enough | Programme Content Lead | **Before Category 08 authoring begins** |
| **R-02** | Resolve the two `LG` gaps (KB-02, KB-03). Both require a register change if new files are needed, since `LG` is declared at 24 and IDs are permanent (`CP-02`) | Legal Counsel | W2 |
| **R-03** | Take a single decision on the `M61` sequencing exposure (KB-05) rather than eight file-level interim controls. The decision belongs at Steering Committee | Quality Manager with Operations Director | **Next Steering Committee** |
| **R-04** | Amend the four register rows identified in KB-04, KB-06, KB-07 and KB-08, or record documented exceptions | Programme Content Lead | W1 |
| **R-05** | Add register and hazard-data variants to `_templates/`, or amend `CG-009` §3 (KB-10) | Content Design | W2 |
| **R-06** | Resolve the `KB-016` / `TR-022` boundary before either is authored (KB-09) | Programme Content Lead with L&D | **W1** |
| **R-07** | **Quantify the specialist authoring load before Category 08.** The four guide sets, the tool guides and the card set enumerate **160 articles, 22 guides and 48 cards**, estimated at **775–1,545 hours** of R12/R13 specialist time — drawn from a population `05-04` sizes at 15–30 L3 specialists and 15–40 remote support engineers, who are simultaneously the people doing the hardest work. `M61` Q-01 asks the same question. **No file in this category is deliverable content; every one is a specification for content that is not resourced** | Technical Director with PMO | **W2 — it is a budget question, not a content one** |
| **R-08** | Establish the Technical Library Owner position. Seven files assign it operational duties and it does not exist | Quality Manager with HR Director | W5 |

---

## 6. Closure

Category 07 is **complete as specified**: 16 of 16 files written, all seven cross-register
dimensions reconciling exactly, 279 internal links resolving, and 93 content identifiers plus 40
business-rule identifiers all resolving to their owning registers.

**It is not complete as content, and the distinction is the most important thing in this report.**
Every file in this category is a governing specification for knowledge that does not yet exist. The
four troubleshooting guide sets enumerate 160 articles of which zero are written; `KB-012`
enumerates 22 guides, `KB-016` enumerates 48 cards, and `KB-003`, `KB-008`, `KB-009`, `KB-010`,
`KB-011` and `KB-014` are empty registers awaiting operating data. `M61` §16.4 states the position
without hedging: *"a knowledge module delivered empty will be judged a failure regardless of how
well it works."*

Three findings — KB-04, KB-05 and KB-08 — share one root cause worth naming for the Steering
Committee: **the register's wave assignments for this category were set against when each file's
subject matter matures, not against when the files that cite it are needed.** `KB-013` safety data
at W5 feeding W2 guide sets, `KB-014` norms at W5 feeding W1 costing, and `M61` at W6 operating W2
content are the same error in three places.

| Rule | Status |
|---|---|
| `CM-R1` register-first | ✅ All 16 registered before authoring; zero divergence both directions |
| `CM-R9` audit on category completion | ✅ This report |
| `CP-11` counted, not estimated | ✅ All figures enumerated 2026-08-16 |
| `RG-06` never read what a document says about itself | ✅ Every check by extraction |
| Gate **F7** category-completion reconciliation | ✅ **Seven dimensions, zero divergence** |

**Proposed new rule for `CG-005`: `RG-08`** — see R-01.

> **Index note.** `AUDIT_Checklist_Recurring.md` requires each audit to be indexed in `RF-012`
> Content Audit Report Archive Index. `RF-012` is not yet authored — Category 99 `RF` is
> unstarted. This report, and `AUDIT-001` through `AUDIT-007`, must be indexed when it is.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
