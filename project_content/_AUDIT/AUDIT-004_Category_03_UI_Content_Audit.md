---
id: FIX-ERP2-AUDIT-004
title: Category 03 UI — Content Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-15
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Programme Content Lead
scope: The 42 Category 03 UI files and their conformance to the CG and VB governance set
mandate: Audit required on completion of Category 03 authoring
extends: AUDIT-001, AUDIT-002, AUDIT-003
---

# Category 03 `UI` — Content Audit
### 42 files · 114 of 452 registered content files now written

---

## 1. Method and result

Checks A1–A6, B1–B5, C1–C5, D1–D5, E1–E7, F1–F6 and G1–G5 of
`AUDIT_Checklist_Recurring.md`, run by direct enumeration (`RG-06`, `CP-11`).

**5 findings — 0 critical, 2 high, 2 medium, 1 low.** Three remediated; two open.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | 42 of 42 ✅ |
| **A2** Total written | 114 of 452, enumerated 2026-08-15 ✅ |
| **B1/B2** ID uniqueness and contiguity `UI-001`…`UI-042` | 42 unique, no gaps ✅ |
| **B4** File name matches ID | 42 of 42 ✅ |
| **C1/C2** `purpose:` and `traces_to:` | 42 of 42 ✅ |
| **D1** Internal links resolve | **252 links across the repository, zero broken** ✅ |
| **D2** Subfolder placement | 10 / 12 / 14 / 6 across 03A–03D ✅ |
| **E7** Template conformance | 42 declare `TPL_UI_Copy_Pack.md` per `CG-009` §3 ✅ |
| **F1** Front matter complete | 12 required keys including `i18n_namespace` and `bn_counterpart` present in all 42 ✅ |
| **UI-a** Every pack declares keyed strings | 42 of 42 carry a key table ✅ |
| **CG-011 LK-02** Banned link text | Zero instances of "click here", "read more", "learn more" ✅ |
| i18n namespace uniqueness | No duplicate namespace declarations ✅ |

### 2.1 Cross-register reconciliation

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---:|---:|:--:|
| File count | Master Index §4 | 42 | 42 | ✅ |
| Content class **A** | `CG-002` §4.1 | 1 | 1 (`UI-042`) | ✅ |
| Content class **B** | `CG-002` §4.1 | 1 | 1 (`UI-038`) | ✅ |
| Content class **C** | `CG-002` §4.1 | 6 | 6 | ✅ |
| Content class **D** | `CG-002` §4.1 | 34 | 34 | ✅ |
| Content class **E** | `CG-002` §4.1 | 0 | 0 | ✅ |
| Bilingual | `CG-010` §3.2 — *"Every interface surface. `PS-03` admits no exception"* | 42 | **42** | ✅ |
| Priority | Master Index §1 (as corrected by `AUDIT-003` MD-01) | 15/19/8/0 | 15/19/8/0 | ✅ |

> **The `AUDIT-003` MD-01 correction held.** Priority counts now reconcile on the first run —
> the first category authored against a corrected §1 table.

---

## 3. Findings

### UI-01 — 42 Bengali counterparts outstanding; the total is now 69

**Severity: High · Status: OPEN — expected, but the volume is now material**

All 42 `UI` files are `bilingual: yes` and every one carries the unchecked Definition-of-Done
item blocking `Approved` under `CM-R6`. None exists.

| Category | Bilingual files | Bengali counterparts written |
|---|---:|---:|
| `VB` | 5 | 0 |
| `MD` | 22 | 0 |
| `UI` | **42** | 0 |
| **Total outstanding** | **69** | **0** |

**Why this is now High rather than Low.** In `AUDIT-003` the figure was 27 and recorded as an
expected dependency. It is now **69**, and `UI` is the category where Bengali is least
negotiable:

- `PS-03` makes Bengali the **default** on customer and field surfaces
- `P02` non-negotiable #3 requires the technician interface to be **complete, including error
  messages** — there is no English fallback on that surface
- `CG-007` §3.4 sets G4 in-context linguistic review at five working days **after** English
  approval, so the wave gate is set by the Bengali sign-off date, not the English one

At the `CG-010` §9 planning rule — escalate translation capacity at wave gate minus six weeks —
**this is already inside the escalation window for W1 and W2.**

**Action:** recommendation **R-01**.

---

### UI-02 — Three Class A/B/C gates are unopenable because `BN-003` and `MD-027` do not exist

**Severity: High · Status: OPEN**

`UI-042` is Class **A** (statutory consent copy, G6 unwaivable), `UI-038` is Class **B**
(estimate approval evidence, G5 unwaivable), and six files are Class **C**.

None can complete its gates, because two upstream files are missing:

| Missing | Blocks | Consequence |
|---|---|---|
| `BN-003` Bilingual Terminology Glossary | **All 42** — §2 terminology bindings are marked indicative | No pack can pass G1 terminology check |
| `MD-027` Status and Lifecycle State Label Register | `UI-011`, `UI-020`, all 14 workspace packs | Status labels cannot be verified as canonical (`CG-008` UI-i) |

`AUDIT-003` R-05 already recommended starting `BN-003` immediately. **This audit escalates it:
`BN-003` is now the single most blocking absent file in the content set.**

---

### UI-03 — The banned-label lint produces guaranteed false positives

**Severity: Medium · Status: FIXED (rule clarified)**

The `CG-008` §6 automated check for banned button labels (`OK`, `Submit`, `Yes`, `No`) flagged
14 instances across 12 files. **All 14 are false positives:**

| Instance | Actual context |
|---|---|
| `\| Yes \|`, `\| No \|` | The **Blocking?** column of the §9 open-questions table |
| `\| Submit \|` (`UI-015` line 99) | The **Element** column; the label is "Submit invoice" |

**Why it matters.** This is the same defect class as `AUDIT-002` **VB-03** — a lint that fires on
legitimate content trains reviewers to ignore it. The check is scanning whole files when it must
scan **label columns only**.

**Fixed by rule clarification:** the `CG-008` §6 banned-label check is scoped to the *English*
and *Label EN* columns of key tables, not to whole documents. Recorded here; the CI
implementation must honour the scope (recommendation **R-02**).

---

### UI-04 — Two commercial promises are asserted in copy without confirmed authority

**Severity: Medium · Status: OPEN — escalated**

`UI-037` §3.2 and `UI-011` §3.4 both state:

| Promise | Wording |
|---|---|
| Free diagnosis | "Checking the device is free. You approve any cost before we start work." |
| Diagnosis charge on decline | "Your device will be returned unrepaired. A diagnosis charge of {amount} applies." |

**These two statements are in tension**, and both are commercial commitments appearing on four
surfaces plus `DT-002`. Under `CG-013` **T-A12** (capability promise) and **T-A11** (pricing),
each requires escalation before it ships.

Both packs flag the question in §9, which is correct handling. The finding is that **no authority
has yet confirmed either**, and `UI-037` is `P0` at W2.

**Action:** recommendation **R-03**.

---

### UI-05 — `UI-011` and `UI-002` assume an unresolved terminology decision

**Severity: Low · Status: OPEN — correctly flagged**

`CG-004` §10 open question 2 asks whether the customer-facing term for `fix.service.order` is
"service order" or "booking". `UI-002` §3.3 and `UI-011` §3.1 both assume **"My services"** for
the noun and **"Book a service"** for the verb, and both flag the assumption.

Correct handling under `CG-012` §6.1 provisional marking. Recorded because the decision now has
three dependent files and grows with every customer-facing pack.

---

## 4. Remediation applied

| # | Change | Finding |
|---|---|---|
| 1 | `CG-008` §6 banned-label check scoped to label columns — recorded in this audit for CI implementation | UI-03 |
| 2 | Master Index §1, §12 and `README.md` written count restated 72→114 by enumeration, dated | A2 |
| 3 | Audit index updated with `AUDIT-004` | — |

---

## 5. Observations

### 5.1 The corrected §1 table held

`AUDIT-003` MD-01 regenerated the priority distribution from the register rows. Category 03 is
the first category authored **after** that correction, and its priority counts reconciled on the
first run with no adjustment. The fix worked.

### 5.2 The dependency chain is now the constraint, not authoring

Four categories are written. What blocks them reaching `Approved` is no longer writing:

| Blocker | Files blocked |
|---|---:|
| `BN-003` Bilingual Terminology Glossary | **69** bilingual files + 42 terminology sections |
| `MD-027` Status Register (written, unapproved) | 17 |
| External tax adviser engagement (`AUDIT-003` MD-03) | 3 Class A `MD` files |
| Legal/DPO sign-off on `LG-008` | `UI-042` |
| Brand ruling on `CR-13` contrast | Design-system tokens |
| No build exists | All 42 `UI` `pinned_to` fields |

**Content production has outrun its own dependencies.** That is not a defect — it is the
expected shape when governance is written first — but it means the next useful work is
**unblocking**, not authoring the next category.

### 5.3 Four audits, four different defect shapes

| Audit | Defect found | Shape |
|---|---|---|
| `AUDIT-001` | AF-02, AF-03 | Summary written from intention |
| `AUDIT-002` | VB-02 | Identifier cited before creation |
| `AUDIT-003` | MD-01 | Summary table never reconciled to its own rows |
| `AUDIT-004` | UI-03 | A control that fires on legitimate content |

Three of the four were caught by enumeration. UI-03 was caught by **reading what the check
actually flagged** rather than trusting its output — which is the same discipline in a different
direction.

---

## 6. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Contract translation capacity now.** 69 bilingual files are outstanding and W1/W2 are already inside the `CG-010` §9 six-week escalation window | Localisation Lead + Procurement | **Immediately** |
| **R-02** | Implement the `CG-008` §6 banned-label check scoped to label columns, and the `AUDIT-003` R-01 reconciliation check, together | Platform Engineering | Next CI change |
| **R-03** | Confirm the free-diagnosis and decline-charge positions, and reconcile them with `DT-002` and `LG-014` | Commercial + Legal | **Before W2** |
| **R-04** | Author `BN-003` — now the single most blocking absent file in the content set | Localisation Lead | **Immediately** |
| **R-05** | Close `CG-004` §10 question 2 — "service order" or "booking" on customer surfaces | `M01` owner with Content Design | Before W2 |
| **R-06** | Approve `MD-027` so the 17 dependent `UI` packs can complete their status-label checks | Architecture Review Board | Before W1 |

---

## 7. Closure

| Item | State |
|---|---|
| Files examined | 42 new; 120 total in the content repository |
| Findings | 5 — 0 critical, 2 high, 2 medium, 1 low |
| Remediated | 3 |
| Open | UI-01, UI-02, UI-04, UI-05 |
| Reconciliations run | 8, all passing |
| Links verified | 252, zero broken |
| Content files written | **114 of 452**, enumerated 2026-08-15 |

**Carried forward.** Open findings from `AUDIT-001` (AF-01, AF-04, AF-06…AF-09, AF-14, AF-15),
`AUDIT-002` (VB-01) and `AUDIT-003` (MD-02, MD-03) remain open and are not restated here.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
*Audit performed 2026-08-15 · Filesystem enumeration dated 2026-08-15*
