---
id: FIX-ERP2-AUDIT-006
title: Category 06 SP — Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 34 Category 06 SP files, their citations into the module repository, and register integrity across the affected registers
mandate: Audit required on completion of Category 06 authoring (rule CM-R9)
extends: AUDIT-001, AUDIT-002, AUDIT-003, AUDIT-004, AUDIT-005
---

# Category 06 `SP` — Content Audit
### 34 files · 218 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F6 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration and by extraction, never by reading
what a document says about itself (`RG-06`, `CP-11`). Enumeration date **2026-08-15**.

In addition to the standard checklist, four category-specific extractions were run, because
Category 06 cites the module repository more heavily than any prior category:

| Extraction | What was compared |
|---|---|
| X1 | Every `SOD-nn` cited in an `SP` file against the register in `SP-006` |
| X2 | Every `SP-004` approval band `A-nn` cited in an SOP against the definitions in `SP-004` |
| X3 | Every `BRU-`, `AUT-` and `KPI-` identifier cited against `05-05` and `06-02` |
| X4 | Every content ID cited against the 452 rows of the Master Index register |

**Eight findings — 1 critical, 3 high, 2 medium, 2 low.** Three were remediated during the
audit; five are open and owned outside the content function.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| Critical | 1 | 1 | 0 |
| High | 3 | 0 | 3 |
| Medium | 2 | 2 | 0 |
| Low | 2 | 0 | 2 |

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 34 of 34 ✅ |
| **A2** Total written | **218 of 452**, enumerated 2026-08-15 ✅ |
| **A5** Files on disk with no register entry | Zero ✅ |
| **B1** ID uniqueness | 34 unique ✅ |
| **B2** Contiguity `SP-001`…`SP-034` | No gaps ✅ |
| **B4** File name matches ID | 34 of 34 ✅ |
| **C1/C2** `purpose:` and `traces_to:` present | 34 of 34 ✅ |
| **D1** Internal links resolve | **198 relative links, zero broken** ✅ |
| **D2** Files in their declared subfolder | 6 in `06A`, 28 in `06B` ✅ |
| **D3** No spaces or ampersands in any path | Zero ✅ |
| **E7** Template conformance | 28 declare `TPL_SOP.md`, 6 declare `TPL_Content_File_Front_Matter.md`, exactly as `CG-009` §3 requires ✅ |
| **F1** Front matter complete | All 24 required keys present in all 34 ✅ |
| **X1** `SOD-` citations | 49 distinct identifiers cited, **all 49 registered** in `SP-006` ✅ |
| **X2** `A-nn` approval bands | 79 distinct bands cited, **all 79 defined** in `SP-004` ✅ |
| **X3** `KPI-` and `AUT-` citations | 82 `KPI-` and 46 `AUT-` cited, **all resolve** in `06-02` and `05-05` ✅ |
| **Role integrity** | Only `R05`–`R38` used operationally. `R39`/`R50` appear solely as quotations of audit finding `00-07` H2-07, never as role assignments ✅ |

### 2.1 Cross-register reconciliation

Every dimension the governance set constrains for this category was extracted and compared.
**All five reconcile exactly.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---:|---:|:--:|
| File count | Master Index §4 | 34 | 34 | ✅ |
| Priority `P0`/`P1`/`P2`/`P3` | Master Index §1 (as corrected by `AUDIT-003` MD-01) | 2 / 21 / 11 / 0 | 2 / 21 / 11 / 0 | ✅ |
| Wave per file | Master Index §4 rows | 34 rows | All 34 match | ✅ |
| Content class A/B/C/D/E | `CG-002` §4.1 | 2 / 1 / 28 / 0 / 3 | 2 / 1 / 28 / 0 / 3 | ✅ |
| Bilingual / English-only | `CG-010` §3.2 | 28 / 6 | 28 / 6 | ✅ |
| Subfolder allocation | Master Index §3.2 | 6 / 28 | 6 / 28 | ✅ |
| Template allocation | `CG-009` §3 | 28 SOP / 6 generic | 28 / 6 | ✅ |

`CG-010` §3.2 states that the six English-only files are *"`SP-001`–`SP-006`, architecture and
matrices for head office"*. Those are exactly the six marked `bilingual: no`. ✅

---

## 3. Findings

### SP-01 — Twenty-nine `TR` citations were wrong; seven pointed at content IDs that cannot exist

**Severity: CRITICAL · Status: FIXED · Owner: Programme Content Lead**

**What was found.** Extraction X4 compared every content identifier cited in the 34 files against
the 452 rows of the Master Index register. Seven identifiers were not in the register at all:

`TR-025` · `TR-026` · `TR-027` · `TR-028` · `TR-029` · `TR-030` · `TR-031`

Category 08 `TR` contains **24 files**, `TR-001`…`TR-024`. There is no `TR-025` and there never
can be one at that position without a register change.

Inspection then showed the problem was wider than the seven out-of-range identifiers. **Every one
of the 28 SOPs carried a "Trains this SOP" row, and all 28 were wrong** — either out of range, or
in range but pointing at a different course than the one named. For example `SP-007` (walk-in
intake, performed by R08 Service Centre Agent) cited *"`TR-008` Service Centre Agent course
pack"*; `TR-008` is the **Dispatch Manager** pack. The Service Centre Agent pack is `TR-007`.
`SP-001` compounded it with a twenty-ninth error, citing `TR-005` for "role-based curriculum
design" when `TR-005` is a technician question bank.

**Why it matters.** This is not a typographical defect. It is **exactly the failure mode this
programme has now recorded in six separate audits** — an author minting or mis-citing an
identifier in a register they do not own. `00-07` H2-04/H2-05 recorded it for custom-development
and KPI identifiers; the portal audit recorded it as X-01; `SP-006` §3.2 in this very category
records nine `SOD-` collisions caused by it. Left in place, seven of these citations would have
become "requirements" for `TR` files that the training workstream would have discovered it was
expected to produce and could not number.

**Why it happened — reported openly.** I wrote the Related Documents table of each SOP while
authoring that SOP, allocating a plausible `TR` number from memory of the sequence rather than
extracting the register. The numbers looked orderly because they ascended with the SOP number,
which is precisely what made the error invisible on review. **`SP-003` `PD-14`, which I wrote in
this same category, prohibits exactly this.** I broke a rule three files after writing it.

**Fixed.** All 29 citations were replaced by extraction from the `TR` register rows, mapping each
SOP to the course pack for the role that actually performs it. The mapping is now:

| SOP | Corrected citation |
|---|---|
| `SP-007`, `SP-013` | `TR-007` Service Centre Agent |
| `SP-008`, `SP-033` | `TR-009` Field Technician |
| `SP-009` | `TR-020` Rider and Logistics |
| `SP-010`, `SP-013` | `TR-010` Workshop Supervisor |
| `SP-015` | `TR-018` Account and Contract Manager |
| `SP-016`, `SP-018` | `TR-012` Inventory and Store Keeper |
| `SP-017` | `TR-013` Procurement Officer · `TR-014` Finance |
| `SP-014`, `SP-019`, `SP-020` | `TR-014` Finance Officer and Manager |
| `SP-021`, `SP-022`, `SP-023` | `TR-015` HR and Payroll |
| `SP-024` | `TR-019` Marketplace and Seller Operations |
| `SP-028`, `SP-034` | `TR-017` Contact Centre Agent |
| `SP-029` | `TR-016` Quality and Field Auditor |
| `SP-031` | `TR-021` System Administrator |
| `SP-032` | `TR-011` Branch Manager · `TR-022` Job Aid Library |
| `SP-011`, `SP-012`, `SP-025`, `SP-026`, `SP-027`, `SP-030` | `TR-002` Role-Based Curriculum Map — **no pack exists**, see SP-02 |

X4 was re-run after the fix: **zero identifiers outside the register.** It was then run a third
time against Categories 04 `NT` and 05 `DT` once those files were issued during this audit,
comparing every cited **title** against the issued filename. All 46 `DT` citations and 3 of 4 `NT`
citations matched; one title error was found and corrected (remediation item 7b).

---

### SP-02 — Six SOPs have no training course pack in Category 08, including health and safety

**Severity: HIGH · Status: OPEN · Owner: Training Lead with HR Director**

**What was found.** Correcting SP-01 exposed a coverage gap. The `TR` register contains fifteen
role-based course packs (`TR-007`…`TR-021`). Six SOPs describe work performed by roles with **no
pack at all**:

| SOP | Role performing | Consequence of no pack |
|---|---|---|
| `SP-011` Remote support and managed services | `R13` Remote Support Engineer (15–40 people) | Privileged access to customer estates, trained informally |
| `SP-012` Data recovery and secure data handling | `R14` Data Services Technician (5–12) | The most sensitive data the company handles, trained informally |
| `SP-025` Trade-in, refurbishment and resale | `R25` Retail / Refurbishment Officer (5–15) | Data-erasure and consumer-disclosure obligations, trained informally |
| `SP-026` E-waste collection and disposal | Sustainability | Regulatory duty under the 2021 Rules, trained informally |
| `SP-027` Rental and equipment-as-a-service | Rental Operations | Company assets in customer hands, trained informally |
| **`SP-030` Health, safety and incident reporting** | **Every employee** | **No HSE course pack exists in a 452-file content register** |

**Why it matters.** The last row is the one that should stop a reader. `SP-030` states that
safety overrides every performance target in the register, and `BRU-LMS-01` restricts work types
when mandatory training is overdue — but there is no safety course to be overdue on. `KPI-064`
targets 95% mandatory-training completion against a curriculum that does not include safety.

**Instruction.** The Training Lead should either add the missing packs to the `TR` register — which
changes Category 08 from 24 files to approximately 30 and changes the 452 total — or record in
`TR-002` the explicit decision that these roles are trained through another named route. **The
HSE gap should be closed before W2 field rollout, not before W5**, because `SP-008` puts
technicians in customers' homes in W2.

---

### SP-03 — Three SOPs are scheduled after the wave that first needs them

**Severity: HIGH · Status: OPEN · Owner: PMO with Business Process Lead**

**What was found.** Wave assignments were taken from the Master Index register and match it
exactly (§2.1). Comparing each SOP's wave against the wave in which its dependants go live
produces three conflicts:

| SOP | Its wave | First needed | Conflict |
|---|:--:|:--:|---|
| `SP-030` Health, safety and incident reporting | **W5** | **W2** | `SP-008` puts field technicians in customers' premises in W2. The risk assessments and safety training that `SP-008` §4 lists as preconditions are produced by `SP-030`. Raised in `SP-030` O-03 |
| `SP-031` IT service desk and change management | **W5** | **W1** | The change control this SOP defines governs the W1 build and every wave after it. A programme running W1–W5 with no change process leaves five waves of production configuration untraceable. Raised in `SP-031` O-01 |
| `SP-002` As-Is process baseline register | W0 | W0 | Not a wave conflict, but a **closing-window** conflict — the baseline for each site becomes unobtainable at that site's cutover (`SP-002` §4.6). W1 pilot baselines are due at W1 gate − 6 weeks and no observer is appointed |

**Why it matters.** A wave assignment in a content register answers *"when is this file
produced?"* It does not answer *"when is it first depended upon?"* For most content those are the
same. For safety and change control they are not, and the register's wave column gives no signal
that they diverge.

**Instruction.** Three options, and the PMO must pick one per row: move the SOP earlier; produce
an interim subset (risk assessments and safety induction for W2; a programme change process for
W1); or accept the exposure explicitly at Steering Committee. **Silence is not one of the three.**

---

### SP-04 — `05-05` is not the complete business rule register it is treated as

**Severity: HIGH · Status: OPEN · Owner: Enterprise Architecture**

**What was found.** Extraction X3 checked all 139 distinct `BRU-` identifiers cited across the 34
files. All 139 exist. **Nine exist only inside a module file and are absent from the
cross-cutting catalogue `05-05`:**

`BRU-CAT-05` · `BRU-DTS-01` · `BRU-EAM-12` · `BRU-FIN-11` · `BRU-FIN-25` · `BRU-FRD-11` ·
`BRU-MKP-03` · `BRU-MKP-18` · `BRU-RMS-08`

Widening the extraction to the whole module repository shows the scale:

| | Count |
|---|---:|
| `BRU-` identifiers in `05-05` | 140 |
| Distinct `BRU-` identifiers across the 67 module files | **1,321** |
| In module files but **not** in `05-05` | **1,198** |

**Why it matters.** `05-05` presents itself as *the* Business Rules and Automation Catalogue, and
every `SP` file, every test script and every configuration engineer will treat it that way. It
contains **11%** of the rules the modules actually specify. Two of the nine cited above are load-
bearing controls in this category: `BRU-FIN-11` (a journal preparer can never be its approver) is
the hard block behind `SP-020` §11 and `SOD-41`; `BRU-DTS-01` (destruction operator cannot be the
witness) is the hard block behind `SP-012` and `SOD-58`. Both would be missed by anyone
configuring from `05-05` alone.

This is the same defect class as `SP-006` finding SD-02 — a register that is authoritative in
name and partial in fact — and it is **not fixable from the content side**. The `SP` files cite
correctly; the register is incomplete.

**Instruction.** Enterprise Architecture must either extend `05-05` to the full rule set, or
restate it explicitly as a **selected** catalogue with the module files named as authoritative.
The second option is cheaper and honest; the first is what every downstream consumer currently
assumes. Needed before W1 build.

---

### SP-05 — `SP-004` and `SP-006` are now second registers for spaces they do not own

**Severity: MEDIUM · Status: FIXED (disclosed, not resolved) · Owner: CFO, CTO, Enterprise Architecture**

**What was found.** Two of the six `06A` files necessarily became registers:

- `SP-004` §4.2 defines **97 approval authorities**. `05-04` §7 contains **28**. Sixty-four are new, and in 41 of those the rule exists in `05-05` or a module file while the **approver was never named**.
- `SP-006` registers **60 segregation-of-duties controls**. `05-04` §6 contains **12**.

**Why it matters.** Two registers for one identifier space is the precondition for every
collision this programme has recorded. `SP-006` §3.2 documents nine such collisions in the `SOD-`
space caused by exactly that.

**Fixed — by disclosure and instruction, not by silence.** Both files open with a banner stating
the tension and carry explicit registration actions: `SP-004` RA-01 and `SP-006` RA-05/RA-06,
each requiring that **one register be made authoritative and the other reduced to a pointer,
before W1 build**. The Master Index designates `SP-006` as *"the register that closes that
finding"*, which supports making `SP-006` authoritative; `SP-004` has no such designation and the
decision is genuinely open.

The audit records this as fixed **to the extent content can fix it**: the condition is documented,
owned and dated. The decision belongs to CFO, CTO and Enterprise Architecture jointly.

---

### SP-06 — `M60` acceptance criterion AC-07 will test 20% of the SoD controls and report a pass

**Severity: MEDIUM · Status: FIXED (raised as an action) · Owner: Quality Manager with CTO**

**What was found.** `M60` AC-07 reads *"All twelve SoD rules from `05-04` §6 are tested, including
by controlled violation attempt."* With `SP-006` registering 60 controls, that criterion tests
**12 of 60** and reports green.

**Why it matters.** This is the *false assurance* pattern that `SP-006` §3.2 identifies for
collided identifiers, reproduced at register scale. A green control-testing report covering a
fifth of the control set is worse than no report, because it stops anyone looking.

**Fixed.** `SP-006` §4.8 names the gap and raises **RA-09**: restate AC-07 to reference the
register rather than a count, so it cannot go stale again when the register grows.

---

### SP-07 — Twenty-eight Bengali counterparts are outstanding, and one class is more urgent than the rest

**Severity: LOW · Status: OPEN · Owner: Localisation Lead**

**What was found.** 28 of 34 files declare `bilingual: yes` (correct per `CG-010` §3.2). **Zero
Bengali counterparts exist.** Every affected file records this in its Definition of Done as
blocking `Approved`, so the position is disclosed rather than hidden — but the volume is now
material and two items need separating from the rest:

| Item | Why it is not just another translation |
|---|---|
| `SP-032` Operational Checklist Library | These are the forms front-line staff complete every shift at 51+ sites. They are used in Bengali, on paper, under time pressure |
| `SP-034` Call and Conversation Script Library | `CG-010` §5 requires Bengali **authored for speech**, not translated — a distinct skill from translation, and currently unresourced (`SP-034` O-01) |

**Instruction.** Localisation should sequence `SP-032` and the W1/W2 SOPs first, and should treat
`SP-034` as an authoring commission rather than a translation task.

---

### SP-08 — Two `06B` files are specifications for content that does not exist yet

**Severity: LOW · Status: OPEN · Owner: PMO**

**What was found.** `SP-033` and `SP-034` are libraries. Each specifies structure, governing rules
and quality gates — and each states plainly that its actual content is unwritten:

| File | Deliverable behind it | Volume |
|---|---|---:|
| `SP-033` Diagnostic and Triage Decision Tree Library | Decision trees, 12 device families × 3 depths | **36 trees** |
| `SP-034` Call and Conversation Script Library | Scripts, 7 groups | **22 scripts** |

Both require specialist authors — R12 technical specialists and a Bengali speech author — neither
of which is in the content plan.

**Why it is Low and not High.** Both files disclose it prominently, in §14 open items and in the
Definition of Done. The register counts them as written because the specification *is* the
registered file. Nothing is being misrepresented. It is recorded so that the PMO does not read
"Category 06 complete" as "diagnostic trees exist".

---

## 4. Remediation applied during the audit

| # | Change | Files touched |
|---|---|---|
| 1 | 28 SOP `TR` citations replaced by extraction from the `TR` register | `SP-007` … `SP-034` |
| 2 | `SP-001` `TR-005` corrected to `TR-002` in two places | `SP-001` |
| 3 | Six SOPs with no course pack annotated with the gap and a pointer to this audit | `SP-011`, `SP-012`, `SP-025`, `SP-026`, `SP-027`, `SP-030` |
| 4 | `SP-004` §4.2.4 extended with `A-97` vendor bank-detail change, closing a dangling reference from `SP-017` §7; counts reconciled from 96/63 to 97/64 throughout | `SP-004`, `SP-017` |
| 5 | `SP-004` header, purpose and finding text corrected from "33 rows" to the enumerated **28 rows** of `05-04` §7 | `SP-004` |
| 6 | `SP-002` §1 KPI baseline table replaced by direct extraction of the `06-02` baseline column — from an estimated "34 measured / 61 unmeasured" to the enumerated **24 measured / 71 without a usable baseline**, with the 27 KPIs that have no baseline field at all raised as escalation E-04 | `SP-002` |
| 7 | Master Index §1 and README completeness figures re-enumerated from the filesystem: **140 → 218 of 452**. Both had drifted because Categories 04 and 05 completed during this category's authoring | `1000FiX_ERP_Content_Master_Index.md`, `README.md` |
| 7b | `NT-019` cited by title as "IVR and Voice Message Library"; the issued file is `NT-019_IVR_and_Voice_Prompt_Scripts.md`. ID correct, title corrected. Found by the same X4 extraction re-run against Categories 04 and 05 once they were issued | `SP-034` |
| 8 | This audit renumbered `AUDIT-005` → `AUDIT-006`. `AUDIT-005` was already allocated to the Category 04 `NT` audit by another owner. Caught before issue; a second instance of the identifier-collision pattern in finding SP-01, this time in the `AUDIT-` space | `_AUDIT/` |

Changes 5 and 6 are the same defect as `AUDIT-003` MD-01 and this audit's SP-01: a figure written
from intention rather than from enumeration. Both were caught by running the extraction rather
than by re-reading the text.

---

## 5. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| R-01 | Decide and record whether `SP-004` §4.2 or `05-04` §7 is the authoritative approval register, and reduce the other to a pointer (`SP-004` RA-01) | CFO + Enterprise Architecture | Before W1 build |
| R-02 | Ratify `SP-006` as the authoritative SoD register and reduce `05-04` §6 to a pointer (`SP-006` RA-05/RA-06) | CFO + CTO | Before W1 build |
| R-03 | Correct the nine module files citing collided `SOD-` identifiers to `SOD-31`…`SOD-39` (`SP-006` RA-07) — **false assurance persists until done** | Enterprise Architecture | Before W1 build |
| R-04 | Resolve `05-05` completeness: extend it, or restate it as a selected catalogue (finding SP-04) | Enterprise Architecture | Before W1 build |
| R-05 | Restate `M60` AC-07 against the register rather than a count (`SP-006` RA-09) | Quality Manager + CTO | Before W1 build |
| R-06 | Add the six missing course packs to the `TR` register, or record the alternative training route — **HSE first, before W2** | Training Lead + HR Director | HSE before W2; remainder before W5 |
| R-07 | Decide the `SP-030` and `SP-031` wave conflicts: move, subset, or accept explicitly (finding SP-03) | PMO | Before W1 build |
| R-08 | Appoint a baseline observer and resource the `SP-002` field work; **the VS-1 window closes at W1 gate − 6 weeks** | PMO | Immediate |
| R-09 | Resource the `SP-033` tree authoring (R12 specialists) and the `SP-034` Bengali speech authoring | PMO + Localisation Lead | P0 trees before W2; scripts before W4 |
| R-10 | Answer the statutory open items carried by the two Class A files and the regulated Class C files as a single legal work package: `SP-020` O-01, `SP-021` O-01, `SP-026` O-01, `SP-030` O-01, `SP-005` O-01, `SP-025` O-01 | Legal Counsel + Tax Lead | Before the affected files leave `Draft` |

> **R-10 is deliberately bundled.** Six files carry statutory citations at source class **P2** or
> **P3** — secondary commentary rather than the enacted instrument, which `CG-012` does not accept
> for content of this consequence. Answering them file by file will produce six partial legal
> reviews. They are one work package: VAT filing, employment and wage law, e-waste regulation, and
> accident notification.

---

## 6. Closure and proposed governance rule

**Repository position at issue.** Categories 04 `NT` (26) and 05 `DT` (44) were completed by
another owner while this category was being authored. The enumerated position is now
**218 of 452 (48%)**, not the 140 stated in the README and the Master Index at the start of this
audit. Both were corrected as part of remediation item 7. Category 05 `DT` has not yet been
audited; this audit does not cover it.

Category 06 is **written**: 34 of 34, all at `Draft`, all conforming to their template, all
reconciling with every register dimension the governance set constrains. None may reach
`Approved`: 28 await Bengali counterparts, 6 await statutory verification, all 28 SOPs await the
`PD-19` UAT walk, and every one awaits a named approver — because **no Content Lead has been
appointed** (`AUDIT-001` R-07, still open).

**Proposed rule `CM-R11`, for `CG-002` §6.**

> **A content file may cite an identifier from another category's register only after extracting
> it from that register. Citing from memory or by sequence is prohibited, and is treated as a
> register breach rather than a typographical error.**

This is `RG-01` register-first, applied to *citation* rather than to *creation*. `RG-01` and
`PD-14` already prohibit an author **minting** an identifier they do not own. Finding SP-01 shows
that is not sufficient: I did not mint `TR-025`, I *cited* it — and a wrong citation into a
register propagates just as far as a wrong creation, while looking far more innocent on review.
Six audits have now recorded some version of this failure. The seventh should not.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
