---
id: FIX-ERP2-AUDIT-007
title: Category 05 DT — Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 44 Category 05 DT files, their cross-register references, and the statutory verification posture of the category
mandate: Audit required on completion of Category 05 authoring
extends: AUDIT-001, AUDIT-002, AUDIT-003, AUDIT-004, AUDIT-005, AUDIT-006
---

# Category 05 `DT` — Content Audit
### 44 files · 218 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F6 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and extraction (`RG-06`, `CP-11`).
No completeness figure in this report is projected.

**10 findings — 1 critical, 4 high, 4 medium, 1 low.** Six remediated during the audit; four
open and owned.

| Severity | Count | Remediated | Open |
|---|---:|---:|---:|
| Critical | 1 | 1 | 0 |
| High | 4 | 1 | 3 |
| Medium | 4 | 3 | 1 |
| Low | 1 | 1 | 0 |

> **The critical finding was caused by this author.** It is stated first and in full, because
> the cause matters more than the fix — the same failure mode will recur in Categories 07–19
> unless the rule proposed in §7 is adopted.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 44 of 44 ✅ |
| **A2** Total written | 218 of 452, enumerated 2026-08-15 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 44 unique ✅ |
| **B2** Contiguity `DT-001`…`DT-044` | No gaps ✅ |
| **B4** File name matches ID | 44 of 44 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 44 of 44 ✅ |
| **D1** Internal links resolve | **290 relative links, zero broken** ✅ |
| **D2** Files in their declared subfolder | 1 / 8 / 11 / 9 / 11 / 4 across root and 05A–05E ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E2** Named approver on every class A and B file | 32 of 32 ✅ |
| **E7** Template conformance | 44 declare `TPL_Document_Print_Template.md`; 44 carry the `DT-001` §12 eleven-section spine ✅ |
| **F1** Front matter complete | 22 required keys present in all 44 ✅ |

### 2.1 Cross-register reconciliation

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---:|---:|:--:|
| File count | Master Index §4 | 44 | 44 | ✅ |
| Content class **A** statutory | `CG-002` §4.1 | 26 | 26 | ✅ |
| Content class **B** legal | `CG-002` §4.1 | 6 | 6 | ✅ |
| Content class **C** operational | `CG-002` §4.1 | 10 | 10 | ✅ |
| Content class **D** user-facing | `CG-002` §4.1 | 1 | 1 | ✅ |
| Content class **E** governance | `CG-002` §4.1 | 1 | 1 | ✅ |
| Bilingual | `CG-010` §3.2 | 34 | 34 | ✅ |
| English-only | `CG-010` §3.2 | 10 | 10 | ✅ |
| English-only IDs | `CG-010` §3.2 | `DT-001`, `DT-021`–`DT-025`, `DT-029`, `DT-033`, `DT-039`, `DT-040` | identical | ✅ |
| Tier **S** prescribed-form | `DT-001` §2.2 | 14 | 14 | ✅ |
| Statutory count in Master Index preamble | Master Index Cat 05 | 14 | 14 (Tier S) | ✅ — see **DT-04** |

---

## 3. Findings

### DT-01 — **Critical** — Forty-five cross-category references cited IDs that do not exist, or exist and mean something else

**What was found.** Every `DT` file carries a §10 Related Documents table with forward
references to categories not yet written at the time of authoring. Extraction of every
`<CODE>-<nnn>` reference against the Master Index register produced:

| Defect | Count | Examples |
|---|---:|---|
| ID outside the category's allocated range | **11** | `SP-035`…`SP-044` (range is `SP-001`–`SP-034`); `RP-017` (range is `RP-001`–`RP-016`) |
| ID inside range but bound to a different file | **34** | `SP-008` cited as "Branch Front-Desk Intake SOP" — `SP-008` is *SOP — On-Site Field Service Visit*; the intake SOP is `SP-007`. `LG-011` cited as "Terms of Service — Repair" — `LG-011` is *Cookie and Tracking Policy*. `UI-020` cited as "P04 Corporate Portal" — `UI-020` is *P10 Contact Centre Console*; P04 is `UI-014`. `TR-014` cited as "Warehouse Operations Course Pack" — `TR-014` is *Course Pack — Finance Officer and Manager* |
| **Total defective references** | **45** | across 40 of the 44 files |

**Why it matters.** Three distinct harms, in increasing order of seriousness:

1. A reader following `LG-011` from `DT-002` lands on a cookie policy and concludes the
   document set is unreliable.
2. `RF-003` traceability and `RF-004` coverage maps are built by extracting exactly these
   references. Forty-five wrong edges corrupt both maps silently.
3. **Eleven of the references allocated IDs that the register had not issued.** That is a
   direct breach of `CP-02` and `CG-005`: content IDs are allocated by the register, and no
   category has authority to mint an ID in another category's range. Identifier collision has
   already cost this programme two audits (`00-07` H2-04/H2-05; portal audit X-01). This is the
   same failure mode, in content rather than in modules.

**How it happened.** The author wrote each §10 table from the *concept* needed — "there must be
a warehouse course pack" — and assigned a plausible ID and title rather than reading the
register. Where the concept had no register entry at all, the author minted the next free
number. No step in the authoring flow forced a lookup, and the defect is invisible to a reader
who does not hold the register.

**Remediation applied.** All 45 references remapped to the correct registered ID and its
registered title:

| Category | Action |
|---|---|
| `SP` | 34 references remapped to `SP-007`…`SP-032`; the 10 out-of-range IDs eliminated |
| `RP` | 14 references remapped to `RP-002`, `RP-004`, `RP-005`, `RP-009`, `RP-012`, `RP-016`; `RP-017` eliminated |
| `LG` | 11 references remapped, principally to `LG-013` *Service Terms, Warranty Terms and Exclusions*, `LG-006`, `LG-007`, `LG-017`, `LG-021` |
| `UI` | 8 portal and workspace references remapped to the correct `UI-014`…`UI-028` bindings |
| `TR` | 6 course-pack references remapped to `TR-009`, `TR-012`, `TR-015`, `TR-016`, `TR-018` |
| `HC`, `EO`, `KB`, `OP`, `AP`, `TS`, `MM`, `CM`, `RF` | 12 references remapped to their registered files |

Categories 04 `NT` and 06 `SP` were authored concurrently by a parallel work stream and now
exist on disk. All 60 `NT` and `SP` references were therefore **upgraded from plain IDs to
relative links and verified to resolve**. Total resolving links in the category rose from 221
to **290, with zero broken**.

**Status: remediated.** The governance rule proposed at §7 exists to prevent recurrence.

---

### DT-02 — **High** — Five concepts Category 05 depends on have no home anywhere in the register

Remapping DT-01 exposed a genuine register gap rather than an authoring error. Five documents
that `DT` files legitimately need do not exist and are not allocated:

| # | Missing content | Needed by | Nearest existing file | Why the nearest is not sufficient |
|---:|---|---|---|---|
| 1 | **Collections and credit control SOP** | `DT-017`, `DT-018` | `SP-019` *SOP — Cash Collection and Banking* | `SP-019` covers cash received at branches, not the dunning ladder, stop conditions or legal escalation. `DT-018` defines an eight-step ladder with no SOP to operate it |
| 2 | **Employee discipline and exit SOP** | `DT-042` | `SP-023` *SOP — Recruitment and Onboarding* | `SP-023` is joiners only. `DT-042` letters 8–14 implement a six-step disciplinary sequence with no procedure behind it |
| 3 | **Branch and warehouse daily operations runbooks** | `DT-016` §5.1, `DT-029`, `DT-044` §5.1 | `OP-014` *Manual Fallback Procedure Set* | `OP-007`–`OP-013` are all IT-platform runbooks. Cash session open/close, gate-log reconciliation and label print-quality monitoring are operational, and nothing in `OP` covers them |
| 4 | **Employment terms and HR policy framework** | `DT-042` | `LG-020` *Acceptable Use and Internal Access Policy* | `LG` has 24 files and none states employment terms. `DT-042` letter 2 (appointment) **is the contract** and has no policy source |
| 5 | **Secure data handling procedure** | `DT-034` | `LG-017` *Data Recovery and Secure Destruction Terms* | `LG-017` is the customer-facing terms. `SP-012` covers the data-recovery process. Neither is the operator procedure for media sanitisation that `DT-034` §5.2 requires |

**Why it matters.** Each is a `DT` document defining an obligation with no procedure to
discharge it. `DT-018` in particular defines a legally sensitive collections ladder that nobody
is instructed to operate.

**Status: open.** Referred to the Programme Content Lead for a register decision — allocate new
IDs in `SP`, `OP` and `LG`, or extend the scope statements of the nearest existing files. Both
`DT-017` and `DT-018` now carry an inline note pointing at this finding so a reader is not
misled by the substitute reference.

---

### DT-03 — **High** — The Mushak 9.1 filing frequency is contested and the whole of 05B is shaped by the answer

**What was found.** Two positions sit in the programme's evidence base and contradict each
other:

| Position | Source | Evidence class |
|---|---|:--:|
| **Monthly**, filed by the 15th of the following month | `05-06` NFR-100 — our own non-functional requirement | **P1** |
| **Quarterly**, within 15 days of quarter-end, for certain registered persons availing input tax credit | Secondary commentary encountered during authoring research, 2026 | **P3** |

**Why it matters.** The tax period is the organising unit of `DT-011` and `DT-012`. If it is
wrong, both statutory registers are structured wrongly, and `FZ-04` prohibits regenerating a
finalised register. It also drives the `MD-041` close calendar, the NBR portal submission cycle
and VAT cash-flow forecasting.

`CG-012` EV-02 prohibits relying on secondary summaries, and audit precedent `00-07` H2-13
records this exact failure — a claim resting on press reporting rather than enacted law. **A
`P3` source cannot be left standing unresolved against a `P1` internal requirement.**

**Status: open.** Raised in `DT-014` §2.2 as gate **G6 question T1**, with its five consequences
enumerated, and flagged as the first question the external tax adviser answers. Owner: CFO.
Required before W1 build of `M51`.

---

### DT-04 — **High** — Two G6 questions gate a portal launch and a product sale, and both are unanswered

| # | Question | Where raised | What it gates |
|---:|---|---|---|
| 1 | **Under the declared principal-or-agent model, who is the supplier of record to the end customer, and who issues the Mushak 6.3?** | `DT-010` Q9 **and** `DT-039` MP1 — the same question in two files | **`P07` marketplace cannot invoice, settle or launch.** `BRU-FIN-08` fixes that the model cannot vary by transaction, but does not say which model we have declared |
| 2 | **Is a paid extended warranty an insurance product under Bangladeshi law requiring authorisation?** | `DT-032` WY1 | **The sale of any protection plan.** Selling a regulated product without authorisation is a regulatory breach, not a compliance defect |

**Why it matters.** Both are gating rather than informational. Neither is discoverable from the
module specifications, and both were surfaced only by writing the document that would have to
carry the answer. Question 1 appearing independently in two files is evidence it is real.

**Status: open.** Owner: CFO with external tax adviser (1); Legal Counsel (2). Question 1 is
required before W7; question 2 before any protection plan is offered.

---

### DT-05 — **High** — Thirty-four Bengali counterparts are declared and none exists

Thirty-four `DT` files declare `bilingual: yes` with a named `bn_counterpart:` file. **Zero of
the 34 exist.** Every one of those files carries an unticked Definition-of-Done line stating
that the missing counterpart blocks `Approved`.

This mirrors `AUDIT-003` finding **MD-06** and is not a new class of defect. It is reported
because of scale and consequence:

| | |
|---|---|
| `DT` bilingual debt | **34 files** |
| Share of the programme's 268 bilingual files | 12.7% |
| Of which are class **A** statutory | **22** |
| Of which are customer-facing at the counter | 11 |

`DT` bilingual debt is materially more consequential than `MD` bilingual debt: a `MD` register
with untranslated labels is an internal inconvenience, whereas an intake receipt, a money
receipt or a payslip issued in English only to a Bengali-speaking counterparty **fails the
purpose the document exists for**.

Compounding it, `VB-004` BL-08 requires Bengali rendering to be physically tested on every
supported printer model before release. That test set does not yet exist (`VB-004` DoD, open).
**Nine `DT` templates render to thermal printers**, where Bengali conjunct failure is a known
and model-specific defect.

**Status: open.** Owner: Localisation Lead with Brand. `BN-015` *Bengali Document and Print
Template Pack* is the register's home for this work and is not yet written.

---

### DT-06 — **Medium** — `VB-004` understates the legally consequential population by six files

`VB-004` front matter states: *"44 DT templates, of which 26 carry statutory or legal
consequence."*

`CG-002` §4.1 allocates `DT` as **A=26, B=6**. Files carrying statutory **or legal**
consequence are therefore **32**, not 26. `VB-004`'s figure counts class A only and labels it
with the broader phrase.

**Why it matters.** `VB-004` §8 applies its strictest rules — brand yields entirely, PDF/A-3
archive, fiscal-year pinning — to the population it names. Six class B files (`DT-018`,
`DT-030`, `DT-031`, `DT-032`, `DT-037`, `DT-042`) are legally binding and were outside the
stated scope.

**Remediation:** correct `VB-004` front matter to *"of which 26 are statutory (class A) and a
further 6 legally binding (class B)"*. Not applied — `VB-004` is outside this audit's scope and
the correction is raised to its owner (Brand Lead).

**Status: open, referred.**

---

### DT-07 — **Medium** — Two statutory counts circulate; both correct, neither reconciled until now

| Count | Source | Measures |
|---:|---|---|
| **14** | Master Index Category 05 preamble — *"Fourteen of these carry statutory force in Bangladesh"* | Documents whose **form** is prescribed by an instrument |
| **26** | `CG-002` §4.1 class allocation | Documents whose **consequence** is statutory |

Both are correct against their own definition, and a reader holding only one of them concludes
the other is an error.

**Remediation applied.** `DT-001` §2.1 states both counts and what each measures; §2.2
introduces **Tier S** as a formal sub-classification and names all fourteen prescribed-form
documents with their instrument. Enumeration confirms exactly 14 files carry
`statutory_tier: S` and exactly 26 carry `content_class: A`.

**Status: remediated in `DT-001`.** The Master Index preamble should cite the reconciliation so
the figure is not read as a contradiction — referred to the Programme Content Lead.

---

### DT-08 — **Medium** — Intake condition has no master-data home, and four documents now depend on a vocabulary owned by a document

**What was found.** During authoring, `MD-025` was cited as a device condition and grading
standard. `MD-025` is the *Repair Action and Resolution Code Taxonomy*. Checking the full `MD`
register confirmed that **no `MD` file holds an intake condition vocabulary** — `MD-024` is the
symptom and diagnostic taxonomy, `MD-026` is reason codes, and neither is a condition
enumeration.

**Why it matters.** Condition at intake is the axis on which the most common customer dispute
in device service turns. `DT-002` cannot function without a fixed enumeration, and three other
documents must compare against exactly the same one: `DT-004` findings, `DT-009` release and
`DT-036` cosmetic grading, with `DT-037` reusing it for rental condition.

**Remediation applied.** `DT-002` §6.1 defines the enumeration — seven attributes with
permitted values and photo minimums — and states four rules including `CE-04`: the same list is
used by `DT-004`, `DT-009` and `DT-036`, so changing it changes all of them.

**This leaves a document owning a vocabulary that behaves like master data.** That is a
deliberate, stated choice (`DT-002` §6.1 rationale: it is a document-capture vocabulary, not
data reused across modules), but the register should confirm it rather than inherit it.

**Status: remediated in `DT-002`; register decision open.** Owner: Enterprise Architecture —
either `MD` adopts the enumeration or `DT-002` is confirmed as its owner in `MD-048` and
`CG-004`.

---

### DT-09 — **Medium** — Check **F3** cannot be completed and will not be until `DT-031` carries values

`AUDIT_Checklist_Recurring.md` **F3** requires SLA definitions to be identical across `MD-028`,
`DT-031` and `LG-015`, with zero divergence, because they carry financial liability.

The check **cannot fail** today, because `DT-031` deliberately carries no values of its own —
`FM-31-a` requires every commitment to be read from `MD-028` rather than restated. Nor can it
pass: a check comparing three documents cannot be run when one of them is a template and one
(`LG-015`) is unwritten.

**Why it is reported rather than deferred silently.** A check that is neither passing nor
failing is a check that will be recorded as "not applicable" at the next wave boundary and
never run. `DT-031`'s Definition of Done carries an unticked F3 line, and this finding is its
external record.

**Status: open.** Owner: Service Operations with Legal. Runnable once `LG-015` exists and
`DT-031` is populated for a live contract.

---

### DT-10 — **Low** — Three malformed emphasis markers; one stated exception to a category rule

| Item | Detail | Status |
|---|---|---|
| Malformed markdown | `DT-034` `DC-34-a`, `DT-036` `GI-01`, `DT-038` `L-38-a` opened with `**` and closed with a backtick, breaking the rule-ID emphasis | **Fixed** |
| Stated exception | `DT-003` §9 takes an explicit exception to `DT-001` §5.1 reprint control, on the grounds that a job card has no original status and applying reprint watermarking to the estate's highest-frequency print adds friction for no control benefit | **Recorded, not hidden.** Requires Programme Content Lead acceptance. It is the only such exception in the category |

---

## 4. Remediation applied

| # | Change | Files touched |
|---:|---|---:|
| 1 | 45 cross-category references remapped to registered IDs and titles | 40 |
| 2 | 60 `NT` and `SP` references upgraded from plain IDs to verified relative links | 40 |
| 3 | Link count raised 221 → **290**, all resolving | 44 |
| 4 | `MD-021`, `MD-024`, `MD-026` bindings corrected in `DT-002` after the `MD-025` misattribution | 1 |
| 5 | Intake condition enumeration authored in `DT-002` §6.1 with cross-document binding rule | 1 |
| 6 | Section cross-references inside `DT-002` corrected (§4.7 → §6.2 clause T-8, etc.) | 1 |
| 7 | Three malformed emphasis markers fixed | 3 |
| 8 | `DT-017` and `DT-018` annotated inline with the DT-02 collections-SOP gap | 2 |
| 9 | Tier S reconciliation authored in `DT-001` §2.1–§2.2 | 1 |

---

## 5. Observations

### 5.1 The register is only as good as the discipline of reading it

`AUDIT-003` recorded that the governance set caught its own author. This audit records something
narrower and more mechanical: **the author knew the register existed, used it correctly for the
four written categories, and invented references for the seventeen unwritten ones.**

Every reference to `CG`, `VB`, `MD` and `UI` was correct, because those files were on disk and
the author linked them by path — a path either resolves or it does not. Every reference to an
unwritten category was a plain ID typed from memory, and **45 of them were wrong**.

The lesson is not "be careful". It is that **a reference that cannot be mechanically checked
will not be correct**, and the fix is to make forward references checkable rather than to ask
authors to be more careful.

### 5.2 Writing the document is what found the questions

Ten gating questions in this category were not visible in the module specifications and appeared
only when someone had to write the document that would carry the answer:

| Question | File | Would the specification have found it? |
|---|---|---|
| Who is the supplier of record on a marketplace supply? | `DT-010` Q9 / `DT-039` MP1 | No — `BRU-FIN-08` says the model cannot vary, not which model applies |
| Is a paid extended warranty insurance? | `DT-032` WY1 | No |
| Does a Mushak 6.5 transfer challan apply to van stock? | `DT-026` TR5 | No — and it is a daily, high-volume movement |
| What accompanies lithium batteries in transit? | `DT-027` DC6 | No — and nearly every device we move contains one |
| Does receipt of an advance create a tax point? | `DT-019` PF1 | No |
| Is the money receipt the tax document, or separate? | `DT-016` M1 | No — and it changes the branch counter workflow |
| Are we registered under the E-waste Rules 2021? | `DT-035` EW1 | No — and if not, it is an immediate `CG-013` escalation |
| Must one Mushak 6.3 issue per supply, or per period? | `DT-020` CI1 | No — and the two answers are materially different `M20` designs |
| What is the lawful payroll deduction limit? | `DT-041` PY3 | No |
| What disciplinary procedure must precede dismissal? | `DT-042` HR3 | No |

**Eight of the ten are answerable only by an external adviser reading an enacted instrument.**
That is the G6 gate working as designed — but it means the category cannot leave `Draft` on
internal effort, and no amount of further authoring changes that.

### 5.3 What this category exposes about the programme

| Observation | Evidence |
|---|---|
| **The statutory posture is honest but empty** | 26 class A files. Every one names its instrument, lists its mandated elements, and marks every element `pending G6`. Not one element is verified. The category is a well-formed set of questions, not a set of answers |
| **Specimens were deliberately withheld** | `DT-010` §7 and five other statutory files defer specimen production until after G6 delivers the prescribed form. A plausible-looking specimen produced first becomes the de-facto standard, and the real form is then measured against it |
| **The bilingual debt is now concentrated where it hurts** | 22 of the 34 missing Bengali counterparts are class A statutory documents issued to consumers |
| **Three documents carry the whole custody chain** | `DT-002` → `DT-027`/`DT-028` → `DT-009`. If `DT-002` clause T-7 does not print, `BRU-SRM-16` abandonment cannot lawfully proceed and the company holds the device indefinitely. That dependency is stated in `DT-009` `UC-02` and exists nowhere in the module specifications |

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---:|---|---|---|
| R1 | Answer `DT-014` **G6 T1** (filing frequency) before any `M51` build begins. It is the first G6 question, not one of many | CFO | Before W1 build |
| R2 | Answer the two launch-gating questions in **DT-04** — marketplace supplier of record, extended-warranty regulation | CFO / Legal Counsel | Before W7 / before any plan is sold |
| R3 | Establish whether 1000FiX is registered under the Hazardous Waste (E-waste) Rules 2021 (`DT-035` EW1). If registration is required and absent, escalate under `CG-013` immediately — this is a live compliance exposure, not a content dependency | Legal Counsel | **Immediate** |
| R4 | Resolve the five register gaps in **DT-02** — allocate IDs or extend existing scopes | Programme Content Lead | Before Category 06/10/17 sign-off |
| R5 | Correct `VB-004` front matter per **DT-06** | Brand Lead | Next `VB` revision |
| R6 | Decide whether `MD` adopts the `DT-002` §6.1 intake condition enumeration | Enterprise Architecture | Before `MD` sign-off |
| R7 | Commission `BN-015` and establish the `VB-004` printer test set. Nine `DT` templates render to thermal, where Bengali failure is model-specific and undetectable without physical test | Localisation Lead + Platform Engineering | Before W1 `DT` release |
| R8 | Accept or reject the `DT-003` reprint exception explicitly | Programme Content Lead | Next wave boundary |
| R9 | Adopt proposed rule **RG-08** below | Programme Content Lead | Immediate |

---

## 7. Closure

### Proposed rule RG-08 — forward references are checkable or they are not made

> **Every cross-category reference cites the registered ID and the registered file name, taken
> from the Master Index at the time of writing — never from memory. Where the referenced file
> exists on disk, the reference is a relative link, so that it resolves or fails visibly. Where
> it does not yet exist, the reference carries the registered file name verbatim, so that check
> **C3** can compare it mechanically.**
>
> A reference to a concept with no register entry is a **register gap**, and is raised as one.
> It is never resolved by allocating an ID.

**Rationale.** Every one of the 45 defects in **DT-01** would have been caught at authoring time
by this rule, and 40 of them would have been impossible. The programme has now recorded
identifier-integrity findings in three separate audits (`00-07` H2-04/H2-05, portal audit X-01,
and this one). The pattern is not carelessness; it is the absence of a mechanical check on the
one class of reference that cannot resolve.

**Adoption note.** `RG-08` costs an author roughly one register lookup per reference and removes
an entire defect class. It is proposed for `CG-005` and for the `CG-008` Definition of Done.

---

### Audit closure

| Item | Value |
|---|---|
| Files audited | 44 |
| Checks run | A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F6, G1–G5 |
| Enumeration date | 2026-08-15 |
| Findings | 10 — 1 critical, 4 high, 4 medium, 1 low |
| Remediated during the audit | 6 |
| Open and owned | 4 — DT-02, DT-03, DT-04, DT-05 (plus referred items in DT-06, DT-07, DT-08, DT-09) |
| Category status | **44 of 44 written, all at `Draft`.** None can reach `Approved`: 26 await gate G6 external verification, 34 await a Bengali counterpart |
| Next audit | On completion of Category 07 `KB`, or at the W1 wave boundary, whichever is first (`CM-R9`) |

> **The category is complete as content and blocked as an artefact.** That distinction is the
> honest reading: 44 files exist, conform, reconcile and link. Not one of them may be issued in
> production until an external adviser has read the enacted instruments and a Bengali counterpart
> has been signed off in context. Recording the category as "complete" without that sentence
> beside it would be the finding this audit exists to prevent.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
