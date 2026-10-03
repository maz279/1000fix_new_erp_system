---
id: AUDIT-005
title: Category 04 NT — Notification & Messaging Content Audit
project: 1000FiX ERP System v2.0
content_type: Audit Report
version: 1.0
date: 2026-08-15
status: Final
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [Content Design Lead, Localisation Lead, CRM & Communications Lead, Enterprise Architecture]
approver: ERP Steering Committee
purpose: >
  Records the mandatory post-authoring audit of Category 04 — NT Notification & Messaging
  Content (26 files), performed on completion of the category. Reports four findings, two
  of them Major, and the reconciliations that passed. Two findings are corrected in this
  pass; one is referred to another owner; one remains open as a delivery risk.
traces_to: [CP-11, CM-R2, CM-R7, CG-002 §4.1, CG-008, CG-009 §3, CG-010 §3.2, CG-012 EX-03]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
content_class: E
template: TPL_Content_File_Front_Matter.md
supersedes: none
review_due: 2026-11-15
---

# AUDIT-005 — Category 04 `NT` Notification & Messaging Content Audit

**Scope.** The 26 files of Category 04 (`NT-001`…`NT-026`), plus the repository-wide
integrity checks that `AUDIT_Checklist_Recurring.md` requires on every category completion.

**Method.** Enumeration, not reading. Every figure below is produced by counting files and
parsing front matter, per `CP-11` — *completeness is counted, never estimated*. The prose
review that preceded it found nothing; both Major findings came from the counts.

---

## 1. Result

| | |
|---|---|
| Files audited | **26** |
| Findings | **4** — 2 Major, 1 Minor, 1 Advisory |
| Corrected in this pass | **2** (`NT-01`, `NT-03`) |
| Referred to another owner | **1** (`NT-02`) |
| Open as delivery risk | **1** (`NT-04`) |
| Reconciliations run | **9** |
| Reconciliations passed | **8** |

---

## 2. Findings

### NT-01 — `CG-010` contradicted itself on Bengali coverage for Category 04 — **Major, corrected**

**What was found.** `CG-010` §3.2 declared Category `NT` as **22 bilingual / 4 English-only**,
naming `NT-001`, `NT-003`, `NT-021` and `NT-026` as the only English-only files. The files as
authored are **20 bilingual / 6 English-only** — `NT-011` (vendor and supplier email library)
and `NT-013` (brand-partner claim correspondence) were additionally set English-only.

That was not an authoring slip. It was the direct application of **`CG-010` §3.3**, the audience
rule in the same file, whose table sets *Vendors and suppliers: No* and *Brand partners: No*.
Two clauses of one ratified policy gave different answers for the same two files.

**Which clause governs.** §3.3 is the **rule**; §3.2 is a **count derived from it**. Where a
derivation and its summary disagree, the derivation governs — the same disposition taken for
`CG-002` §4.1 in `AUDIT-002`. The count was wrong, not the files.

**Why the exception is right on the merits, not merely on precedence.** `PS-03` compels Bengali
on *interface surfaces*, and `CG-010` §3.2 says so explicitly for Category `UI` — "every
interface surface, `PS-03` admits no exception". Outbound business correspondence to a
counterparty that contracts in English is not an interface surface. This is why the vendor
portal UI pack (`UI-015`) is bilingual while the vendor email library (`NT-011`) is not: the
portal is a surface the vendor operates, the email is a letter between two businesses. The same
line is already drawn in `CG-010` §3.2 for Categories `DT` and `LG`, where vendor-, brand- and
B2B-facing documents are English-only.

**Correction applied.**

| File | Change |
|---|---|
| `CG-010` §3.2 | `NT` row `22 / 4` → **`20 / 6`**; rationale rewritten to name `NT-011` and `NT-013` and to cite the §3.3 audience rule as their basis |
| `CG-010` §3.1 | Bilingual total `268` → **`266`**; English-only `184` → **`186`** |
| `1000FiX_ERP_Content_Master_Index.md` §1 | "Files requiring a Bengali version" `268` → **`266`** |

No `NT` file was changed. **266** is now the programme-wide Bengali volume figure and supersedes
`268` wherever it appears in planning material.

**And then the correction was itself found incomplete.** A verification sweep run immediately
after A1 found `268` still asserted in **eleven further places**, including — in the very file
just corrected — `CG-010` §3.2's own **total row**, which read `452 | 268 | 184` beneath a
category table whose `NT` row now said `20 / 6`. The file contradicted itself in adjacent lines.
The other ten were downstream restatements: `CG-002` §RACI (Localisation Lead scope), `CG-007`
§G4 twice (workflow scope and the review-lead-time table), `CG-013` `CR-04` (translation-capacity
risk), the Master Index `CG-010` register row, and five more inside `CG-010` (purpose block,
§6 machine-translation scope, §8 metrics, §9 wave-audit check, changelog and completion
checklist). All eleven are corrected, and `CG-010` §3.2 now reconciles by computation: **21
category rows summing to 452 / 266 / 186**, equal to the §3.1 headline.

The lesson is sharper than the original finding. A single figure had been restated in twelve
places across four files, so correcting the source of truth left eleven live contradictions —
each of which would have read as authoritative to whoever found it first. Derived figures must
be **swept repository-wide after correction**, never corrected only where the audit noticed
them. This is added to A3.

*Closed audits are not amended:* `AUDIT-001` §effort still cites 268. That is the historical
record of what was true when it was written (`CM-R7`), and this report supersedes it.

**Root cause — a repeat.** This is the third instance of one failure mode: *a summary table
written before the derivation it summarises, and never reconciled against it*. `AUDIT-002`
found it in `CG-002` §4 and `CG-009`; `AUDIT-003` found it in the Master Index priority
distribution (`MD-01`, 20 of 21 categories wrong); it is here again. All three were authored by
me, and all three breach `CP-11` and `CM-R2` — rules stated in files I wrote.

**Preventive action.** The category-completion reconciliation script (§3) is now the gate, not a
check. It is added to `AUDIT_Checklist_Recurring.md` as a **blocking** step: no category may be
declared complete until every derived count in `CG-002` §4.1, `CG-009` §3 and `CG-010` §3.2
reconciles against the files on disk. Summary tables for Categories 05–20 must be **regenerated
from the register rows after authoring**, never written ahead of it.

---

### NT-02 — 13 broken links in Categories 05 and 06 — **Major, referred, not corrected**

**What was found.** The repository-wide link check returned **13 unresolvable relative links** at
the enumeration timestamp. None is in a Category 04 file — `NT` links resolve **27 of 27**. All
13 are in the `DT` and `SP` files that have appeared on disk during and between this
workstream's turns and are under active authorship by another owner.

| Source file | Links to (not yet written) |
|---|---|
| `DT-001` | `DT-044` |
| `DT-002` | `DT-009`, `DT-016`, `DT-044` |
| `DT-003` | `DT-007`, `DT-008`, `DT-044` |
| `DT-004` | `DT-007`, `DT-033` |
| `DT-005` | `DT-006`, `DT-010`, `DT-019` |
| `SP-001` | `SP-003` |

> **The number is not the finding — the pattern is.** A re-run twenty minutes later, after
> `DT-006` and `SP-004` were written, returned **15**. The defect is being introduced at the
> rate the category is being authored, so any count quoted here is stale on arrival. The
> receiving owner should re-run the check rather than work from this table.

Every one is a **forward reference to a planned sibling**, hyperlinked as though it existed.
That is the exact prohibition in `CG-012` **EX-03** — *never link to a planned document as
though it were written*. A reader who clicks gets a dead path and no signal that the target is
scheduled rather than missing.

**Why it is not corrected here.** These files are outside Category 04 and are being written
now — `DT-004` and `DT-005` did not exist when this audit began and appeared during it.
Editing a file under another author's hand would collide with their work and could silently
revert it. The same restraint was applied to `AF-03` in `AUDIT-001`.

**Referred action** (`DT` owner, `SP` owner). Replace each hyperlink with the plain-text form
`CG-012` EX-03 prescribes — the identifier in backticks with no link target, e.g.
``DT-044` (planned, Wave 3)`` — and restore the hyperlink when the target is written. The
Category 05 and 06 completion audits must run the link check before declaring complete.

---

### NT-03 — Master Index remaining-work line was stale — **Minor, corrected**

`1000FiX_ERP_Content_Master_Index.md` §12 carried `Categories 04–99 | 0 of 338 written`, true
when written and false on completion of Category 04. Replaced with a Category 04 completion row
and a Categories 05–99 row that states the partial `DT`/`SP` files and their enumeration date.
Written totals in §1, §12 and `README.md` raised **114 → 140** by enumeration, dated 2026-08-15.

---

### NT-04 — Six WhatsApp templates unsubmitted, and Wave 2 depends on them — **Advisory, open**

`NT-008` §2.3 records all six WhatsApp Business templates at status *pending submission*. Meta
approval is typically under 24 hours and up to 48 for Marketing category, so the lead time is
not the risk. Two things are:

1. **Recategorisation without notice.** Since April 2025 Meta may reclassify a template
   submitted as Utility to Marketing with no advance warning. A Marketing-categorised template
   is billed differently and is subject to marketing opt-out — a job-status update that
   recategorises stops reaching customers who opted out of marketing. `NT-008` carries the
   mitigation; it is not yet exercised against a live submission.
2. **No template is proven until submitted.** Wave 2 job-status messaging is designed against
   six templates whose approved wording is unknown. Wording changes forced at approval
   invalidate the Bengali translations commissioned against them.

**Recommended action.** Submit all six for approval in Wave 1, ahead of need, and treat approved
wording as the input to Bengali translation rather than translating the drafts.

**Related standing risk.** Of the 140 files now written, **89 declare `bilingual: yes`** —
5 `VB`, 22 `MD`, 42 `UI`, 20 `NT` — and **zero Bengali counterparts exist**. `CM-R6` blocks
`Approved` on any of them until the pair is signed off. `BN-003` (the Bengali terminology
glossary) remains the single most blocking absent file in the repository: every one of the 89
must be translated against it, and translating before it exists guarantees rework.

---

## 3. Reconciliations

| # | Check | Expected | Found | Result |
|---|---|---|---|---|
| 1 | File count | 26 (`CG-002`, Master Index §4) | 26 | **Pass** |
| 2 | Identifier contiguity | `NT-001`…`NT-026`, no gaps, no duplicates | contiguous | **Pass** |
| 3 | Subfolder placement | root 7, `04A` 4, `04B` 4, `04C` 6, `04D` 5 | as declared | **Pass** |
| 4 | Content class split | `CG-002` §4.1 — A 1 / B 2 / C 5 / D 15 / E 3 | 1 / 2 / 5 / 15 / 3 | **Pass** |
| 5 | Priority distribution | Master Index §4 — P0 4 / P1 12 / P2 10 | 4 / 12 / 10 | **Pass** |
| 6 | Wave assignment | sums to 26, no file before its consuming module | W1 3, W2 13, W3 3, W4 4, W5 1, W6 1, W7 1 = 26 | **Pass** |
| 7 | Template declaration | `CG-009` §3 — `TPL_Notification_Template` 23, front-matter-only 3 | 23 / 3 | **Pass** |
| 8 | Link resolution within `NT` | all resolve | 27 of 27 | **Pass** |
| 9 | Bilingual split | `CG-010` §3.2 — 22 / 4 | 20 / 6 | **Fail → `NT-01`** |

Status is `Draft` on all 26, correctly: none has passed G4 in-context review, and the 20
bilingual files cannot reach `Approved` before their Bengali counterparts exist (`CM-R6`).

---

## 4. Substantive matters confirmed sound

These were checked because getting them wrong is expensive, and they hold.

| Area | Confirmed |
|---|---|
| **BD SMS routing** | `NT-001` §3.1 BD-01…BD-05 correctly separate masking (alphanumeric, transactional and OTP, reaches DND numbers) from non-masking (numeric, promotional, DND-blocked, time-restricted). BD-03 correctly identifies the rule most likely to be broken in practice: a transactional message carrying a promotional rider — *"Your device is ready — and get 20% off"* — is promotional, and routing it on the masking route risks route suspension for the whole programme |
| **Bengali SMS economics** | `NT-004` §2.3 records UCS-2 segmentation at **70 characters**, not 160. Nine of fifteen Bengali templates run to two segments and one to three; Bengali send cost averages **1.9×** English. This is a budget line, and it is now stated where a budget owner will find it |
| **OTP security** | `NT-007` §2.3 sets eight rules, of which OT-03 — *no link in any OTP message, ever* — is the one that makes the message set unusable as a phishing template. Correct and non-negotiable |
| **Class A / B gates** | The one Class A file and two Class B files each carry an unwaivable outstanding gate (`WV-02`), stated as outstanding rather than assumed clear |

---

## 5. Actions

| # | Action | Owner | Status |
|---|---|---|---|
| A1 | Correct `CG-010` §3.1–§3.2 and Master Index §1 to 266 / 186 | Programme Content Lead | **Done** |
| A2 | Raise written count 114 → 140 by enumeration; add Category 04 row | Programme Content Lead | **Done** |
| A3 | Make the reconciliation script a blocking gate in `AUDIT_Checklist_Recurring.md` (`F7`), including the repository-wide sweep for restated figures | Programme Content Lead | **Done** |
| A4 | De-hyperlink 13 forward references per `CG-012` EX-03 | `DT` owner, `SP` owner | **Referred** |
| A5 | Submit six WhatsApp templates for Meta approval in Wave 1 | CRM & Communications Lead | **Open** |
| A6 | Commission `BN-003` — blocks Bengali work on all 89 bilingual files | Localisation Lead | **Open, escalated** |

---

*Enumerated 2026-08-15. Every count in this report is reproducible from the files on disk.*
