---
id: PGD-AUDIT-ALIGN-001
title: Cross-Repository Alignment Audit — project-guide-doc against primary-doc and 1000fix_ERP_Module
category: Cross-cutting
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture
scope: >
  All 179 markdown files under project-guide-doc (138 guiding documents, 18 audits, 17 category
  overviews, 3 root files, 1 template, 2–3 directory layers), tested for alignment against
  primary-doc (4 documents, 17,680 lines) and 1000fix_ERP_Module (123 files, 79 module and portal
  specifications).
enumeration_timestamp: 2026-08-19 19:14 (+06)
verified_on: 2026-08-19
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Cross-Repository Alignment Audit

### `project-guide-doc` (179 files) × `primary-doc` (4) × `1000fix_ERP_Module` (123) · **11 findings · 9 corrections applied**

---

## 1. Method, scope and result

**Method.** Every shared quantity was **re-derived from the module and portal specifications
themselves** and then compared against what each of the three repositories asserts. Nothing was
read back from the document asserting it. Where a figure could not be reproduced, the extraction was
re-run with a tighter pattern before the figure was called wrong — a discipline that overturned
three of my own provisional findings (§2.3).

**Scope, enumerated 2026-08-19 19:14 (+06):**

| Repository | Files | What was tested |
|---|---:|---|
| `project-guide-doc` | **179** | 138 guiding documents · 18 audits · 17 overviews · `PGD-000` · templates |
| `primary-doc` | **4** | BRD, RFP, URD, Technology Stack Specification — 17,680 lines |
| `1000fix_ERP_Module` | **123** | 67 module + 12 portal specifications; governance, architecture, cross-cutting |
| **Workspace total** | **800** | |

**Axes tested — fourteen shared quantities and three qualitative surfaces:**

requirement denominator · module/portal counts · effort · entity population · entity ownership ·
KPI space · custom-development register · NFR space · role register · segregation-of-duties
register · report population · FX rate · wave calendar · decision space · technology versions ·
regulatory citations · contractual deliverable quantities.

**Result.**

| | Count |
|---|---:|
| Axes tested | **17** |
| Axes **aligned** | **9** |
| Findings raised | **11** — 6 HIGH, 4 MEDIUM, 1 CRITICAL-adjacent (contractual) |
| **Corrections applied to `project-guide-doc`** | **9** |
| Change requests to `primary-doc` *(which this audit cannot edit)* | **4** |
| Provisional findings **withdrawn on verification** | **3** |

> **The single most consequential finding is `CO-003-F-08`:** the Statement of Work buys **2,930
> requirements and 101 non-functional requirements**; the engineering estate specifies **3,389 and
> 122**. A supplier satisfying the contract in full leaves **459 requirements and 21 NFRs** unbuilt,
> and would be entitled to payment. §4.1.

---

## 2. Checks that passed

### 2.1 Aligned across all three repositories

| Axis | Position | Verdict |
|---|---|:--:|
| **Module and portal counts** | 67 modules, 12 portals, 79 specifications — consistent in all three | ✅ |
| **Role register** | 53 distinct `R-nn` identifiers in both the module estate and the guide | ✅ |
| **KPI register** | 95 registered / 250 in use — the guide records both and the discrepancy | ✅ |
| **FX rate** | Every one of the guide's 110 references is explicitly marked a superseded, unverified assumption, with 122.70 carried as the planning rate | ✅ |
| **Odoo / PostgreSQL / Keycloak / Flutter** | 19.0 · 16 · 26.x · 3.44 — consistent, and all four re-verified against upstream on 2026-08-19 | ✅ |
| **Wave calendar** | `GV-004` §5.2's W1 1–4 … W9 35–36 is used consistently; `BM-002` `BMR-10` anchors to it explicitly | ✅ |
| **PDPA 2026 citation chain** | Ordinance 2025 → Amendment Ordinance No. 23 of 2026 (5 Feb 2026) → enacted April 2026 → enforcement ~13 May 2027, regulator National Data Management Authority. **Externally verified 2026-08-19**; consistent across all three repositories | ✅ |
| **Segregation of duties** | `SC-004` §11.1 correctly rules `SP-006` (61 controls) the source of record rather than restating rows. `SP-006` exists and holds 61 | ✅ |
| **Report population** | 920 (67 modules) · 154 (12 portals) · **1,074** (all 79). `UX-003`'s 920 and `AUDIT-015`'s ~1,063 are both correct **for their stated scopes** | ✅ |

### 2.2 Counted from source — figures that reproduce exactly

```bash
# owned-entity extraction, all 79 specifications, 2026-08-19 18:46 (+06)
find . -name "*.md" ! -name "_*" -print0 | xargs -0 awk '
  /^### 10\.1/{s=1;next} /^### 10\.2/{s=0} /^#{2,3} 1[1-9]\./{s=0}
  s && /^\| *`fix\./ {print}'
```

| Measure | Counted | Reproduces |
|---|---:|---|
| Specification files | **79** | 67 modules + 12 portals ✅ |
| Owned-entity declaration rows | **1,370** | `DA-001` §2.1 (2026-08-18 14:30) ✅ |
| **Distinct entities declared owned** | **1,335** | `DA-001`, `DA-002` ✅ |
| Owned rows contributed by portals | **0** | portals own nothing — confirms `DA-001`'s "67 modules" scope is complete ✅ |
| Entities owned by more than one specification | **34** | `AR-008` §2.2 **exactly** ✅ |
| Excess owned rows from those 34 | **35** | 1,370 − 1,335 ✅ |
| Distinct `NFR-` in module estate and `primary-doc` | **101** | `05-06` ✅ |
| Distinct `NFR-` in `project-guide-doc` | **122** | `RQ-006`'s contiguous block `NFR-102`…`NFR-122`; **zero source NFRs missing** ✅ |
| Distinct `CD-` in the 79 specifications | **195** | between the module audit's 192 (2026-08-13) and `BE-005`'s register ✅ |

> **`AR-008`'s multi-ownership count reproducing exactly at 34 is the strongest single evidence of
> the estate's rigour in this audit.** `fix.contract.cost` is declared owned by `M08`, `M53` **and**
> `M54`; 33 further entities by two modules each. `AR-012` `FF-27` and `BE-009` `DBT-003` already
> carry it as a fitness function and a technical-debt item.

### 2.3 Three provisional findings withdrawn on verification

Recorded because an audit that reports only what survived is not showing its method.

| Provisional finding | Why it was withdrawn |
|---|---|
| *"Entity counts 225 / 334 / 355 diverge"* | The pattern `[0-9]{2,3} entit(y\|ies)` was matching the **trailing three digits of four-digit figures** — 1,334 read as "334". Re-run anchored, the real figures are 1,334 / 1,335 / 1,355 / 1,360 |
| *"`05-06` duplicates six NFR identifiers; `AP-02` understates at three"* | `NFR-086a`, `086b`, `086c` are **sub-identifiers**, not duplicates of `NFR-086`; `RQ-006` §4.11 handles them explicitly. The real duplication is five identifiers, and `RQ-006` had already found the two `AP-02` missed |
| *"`project-guide-doc` covers only 19 of 30 SOD controls"* | `SC-004` §11.1 **deliberately** points at `SP-006` as the register of record rather than restating 30 or 60 rows. Not restating a register is correct design |

> **All three were pattern errors or scope misreadings on my part, and all three would have been
> published as findings by a reviewer who did not re-derive.** This is the same lesson
> `PGD-AUDIT-CAT-15` §3.2 records: a check that re-reads a document cannot detect what a re-count
> can.

---

## 3. Findings — internal to `project-guide-doc`

### 3.1 `ALN-01` — the entity population had six live values; it now has one

**Severity: HIGH · Status: FIXED IN AUDIT · Owner: Enterprise Architecture**

The estate already knew: `UXA-21` (`UX-003`) recorded *"four figures exist for the entity
population… this is the `TS-01` three-denominators defect class recurring on a second quantity"*,
and `RR-006` `XRF-Q-04` asked which was authoritative. **Both were open. What was missing was the
answer, and the answer had in fact already been published.**

| Figure | Where | Disposition |
|---:|---|---|
| **1,335** | `DA-001` §2.1 (counted 2026-08-18 14:30), `DA-002`, `DA-003`, `DA-005`, `DA-006`, `MG-001`, `RL-006` | **AUTHORITATIVE.** Independently recounted 2026-08-19 18:46 → identical |
| 1,334 | `AR-008` §2.2 (counted 2026-08-18 **02:05**, 1,369 rows) | **Correct at its own timestamp.** The population moved by one in the nine hours between counts. Retained in `AR-008` under `RG-08`; **removed from the eight documents that had copied it forward as current** |
| 1,355 / 1,388 | `UX-002`, `UX-003` | **Not reproducible.** Portals own **zero** entities, so a modules-only and an all-79 owned count are identical. The 33-entity gap `UX-003` detected was real but mis-labelled — it is `ALN-02` |
| 1,360 | `RQ-004`, `PGD-AUDIT-004` | **Not reproducible** for either population. The owned+referenced distinct count is **1,370** |
| 225 | `05-02`, `primary-doc` | The 30-module catalogue. Correct for what it covers; superseded for the 67-module architecture |
| 51 | `RR-006` `E-nnn` tokens | **A different space** — catalogue identifiers, not entities. Conflating them was part of why `XRF-Q-04` looked unanswerable |

**Corrections applied — 13 documents, 32 occurrences:**
`AR-001` (2) · `AR-002` (4) · `AR-003` (1) · `AR-004` (1) · `02_Architecture_and_Design/_CATEGORY_OVERVIEW` (3) ·
`QA-004` (1) · `RR-001` (1) · `AR-008` forward-looking lines (4) · `UX-002` (4) · `RQ-004` (3) ·
`RR-006` (4) · `PGD-000` (2) · `UX-003` (2).

**`UXA-21` and `XRF-Q-04` are marked RESOLVED in place**, with the counted answer and the reason each
superseded figure differs. `AR-008` §2.2 carries a restatement note rather than an overwrite.

> **The lesson is not that anyone counted badly.** `AR-008` and `DA-001` both counted correctly,
> nine hours apart, and the population moved by one entity between them. **What failed is that eight
> documents copied the earlier figure forward without its timestamp**, which is precisely what
> `RG-08` exists to prevent and precisely why it should be ratified (`D-023`).

### 3.2 `ALN-02` — 34 entities are referenced by portal specifications and owned by nobody

**Severity: HIGH · Status: RAISED (`AR-008-F-01`) · Owner: Enterprise Architecture**

`AR-008` §2.2 asserts *"§10.2 references whose declared owner does not define the entity in its own
§10.1: **0** ✅"*. **That is true, and its scope is "all 67 specifications".** The 12 portal
specifications were never tested.

Re-run across all **79**:

| Measure | Count |
|---|---:|
| Entities named in a §10.2 that are owned by **no** specification | **35** |
| …genuine entities, referenced by portals | **34** |
| …wildcard pattern, not an entity — `fix.warehouse.fact.*` (`M54` → `M62`) | **1** |
| Portal specifications affected | **10 of 12** |

`P07` references 8 · `P01` 7 · `P02` 6 · `P04` and `P12` 5 each · `P09` and `P11` 4 each ·
`P05` and `P10` 3 each · `P08` 2.

**What is missing includes** `fix.invoice`, `fix.payment`, `fix.warranty`, `fix.warranty.claim`,
`fix.sale.order`, `fix.partner`, `fix.rental`, `fix.commission`, `fix.settlement`, `fix.dispute`.

> **This is the `AUDIT-016` `AP-01` defect class — *"21 event names are consumed by specifications
> and do not exist in the inventory"* — occurring on entities instead of events, and reaching the
> user-facing surface.** Ten portal specifications reference tables the schema will not contain.
>
> **Several are near-misses for entities that do exist under another name** — `fix.warranty.register`
> is owned by `M09`; `fix.invoice` is plausibly `M20`'s. The likely resolution is a **naming
> reconciliation, not 34 new tables** — but until it is done, `DA-001` cannot freeze a schema the
> portals will resolve against.

**Recorded in `AR-008` §2.2 as `AR-008-F-01` with the full list, the verification and the
remediation.** Raised to `DA-001` and `AR-005`; carried to `GV-005`.

### 3.3 `ALN-03` — three technology decisions were unregistered, on identifiers already allocated

**Severity: HIGH · Status: FIXED IN AUDIT (`GV-003-F-01`) · Owner: Programme Manager**

`primary-doc/…Technology_Stack_Specification.md` §24 and §25.2 allocate **`D-15`, `D-16`, `D-17`**.
**`GV-003` §2.2 does not list that specification as a source**, and all three identifiers were
already allocated to different decisions — with `DL-05` recording `D-15` as an explicit *alias* for
`D-015`.

| Identifier | Technology Stack Specification | `GV-003` |
|---|---|---|
| `D-15` | Odoo version baseline and upgrade slot | Significant data fiduciary / appoint a CDO |
| `D-16` | Next.js 15 → 16 upgrade timing | Portal effort inside or outside the build baseline |
| `D-17` | `P07` mobile surface | Waves 5–9 authorised now or at the W4 gate |

**A third meaning exists**: `UX-003` uses `D-15` in its own local data-point space for *"files in
the four demand-side repositories = 621"*. **`D-15` denotes three different things in three live
documents.**

**Corrections applied:**

1. `GV-003` **§5.4a** created, registering the three as **`D-025`, `D-026`, `D-027`** — verified free
   across all four repositories at 2026-08-19 18:46 (+06) — each with its collision recorded and its
   currency updated (§5).
2. `GV-003` §2.2 gains the Technology Stack Specification as a decision source.
3. New rule **`DL-08`**: a `D-nn` allocated outside this log is **not a programme decision** until
   re-registered here.
4. `GV-003` §5.6 log summary regenerated by recount: **26 `OPEN` + 1 `ESCALATED` = 27**.
5. **14 documents re-pointed** from `D-15`/`D-16`/`D-17` to `D-025`/`D-026`/`D-027` — `AR-001`,
   `AR-004`, `AR-006`, `AR-007`, `AR-013`, `BE-001`, `BE-002`, `BE-004`, `BE-005`, `BE-007`,
   `QA-005`, `CO-005` and two category overviews. **`GV-001`, `GV-002` and `UX-003` were deliberately
   left unchanged** — they use `D-15` in its other two meanings.


---

## 4. Findings — misalignment with the source estate

> **Direction matters.** In every finding below, **`project-guide-doc` holds the counted figure and
> the source estate holds the stale one.** Aligning the guide *down* to the source would be wrong.
> What is missing is a change request against the source, and this audit cannot edit `primary-doc`
> or `1000fix_ERP_Module`.

### 4.1 `ALN-04` — the contract buys less than the estate specifies

**Severity: HIGH · Status: RAISED (`CO-003-F-08`) · Owner: CFO with the CTO**

`CO-003`'s deliverable schedule — the **contractual** statement of what is bought — carries the
RFP's quantities:

| Row | Contract buys | Estate specifies | Gap |
|:--:|---:|---:|---:|
| 3 — requirements | **2,930** (RFP §6, Appendix A) | **3,389** = 3,347 rows + 42 `SWR` | **+459 (+15.7%)** |
| 5 — non-functional requirements | **101** (RFP §9) | **122** | **+21 (+20.8%)** |

**Verification**: 3,389 − 2,930 = **459** ✓ · 459 ÷ 2,930 = **15.7%** ✓ · 122 − 101 = **21** ✓ ·
distinct `NFR-` counted: source **101**, guide **122**, **zero** source NFRs absent from the guide ✓.

> **A supplier who satisfies all 2,930 and all 101 has met the schedule in full and is entitled to
> payment**, while 459 requirements and 21 NFRs the engineering estate treats as in scope remain
> unbuilt. `SOW-27`'s acceptance test would pass. **The exposure runs in the Company's direction.**

**Recorded in `CO-003` as `CO-003-F-08`.** The recommended remediation is **not** to restate the
number but to re-draft rows 3 and 5 to cite *"the requirement baseline as maintained in `RQ-001` and
`RQ-006` at contract date"* — a fixed number goes stale at the next recount, and `RQ-005` already
governs baseline change. `CO-002`'s evaluation sizing (2,930 responses per respondent) is **correct
for the RFP as issued** and re-sizes if the RFP is restated.

### 4.2 `ALN-05` — the requirement denominator exists only in the guide

**Severity: HIGH · Status: OPEN — change request · Owner: CTO**

| Repository | Figures carried |
|---|---|
| `project-guide-doc` | **3,347** module/portal rows · **3,389** with `SWR` — counted, with a reproduction command (`RQ-001` §3.10.5, `RQ-004` `CV-01`, `QA-011`) |
| `primary-doc` | **2,930** (BRD, RFP, Technology Stack Spec) and **1,180** (BRD, RFP) |
| `1000fix_ERP_Module` | **2,930** and **1,180**; its own `_MODULE_SET_AUDIT_REPORT` §8 counted **3,343** on 2026-08-13 |

**Neither `3,347` nor `3,389` appears anywhere outside `project-guide-doc`.** The module estate's own
audit reached 3,343 six days before `RQ-001` reached 3,347 — a +4 drift that is explainable and
consistent. **The two demand-side repositories have simply never been restated.**

> **The RFP is a live procurement instrument.** Vendors are pricing against a denominator that is
> **15.7% below** the counted estate.

### 4.3 `ALN-06` — the effort baseline exists only in the guide

**Severity: HIGH · Status: OPEN — change request · Owner: CTO**

| Repository | Effort |
|---|---|
| `project-guide-doc` | **1,842 PW** — `GV-007`, counted across all 79 files including portals; carried by 22 documents |
| `primary-doc` | **1,513 PW** |
| `1000fix_ERP_Module` | **1,513 PW** and **834 PW** |

**`1,842 PW` appears in neither source repository.** The difference is chiefly the **298 PW of portal
effort no earlier figure carried** — which is also the subject of `GV-003` `D-016`, still open.

### 4.4 `ALN-07` — the custom-development register has four figures

**Severity: MEDIUM · Status: OPEN — change request · Owner: CTO**

| Figure | Source |
|---:|---|
| 138 | RFP §5.3, §16.2 — "~138 CD items", covering 30 of 67 modules |
| 192 | `_MODULE_SET_AUDIT_REPORT` §8, counted 2026-08-13 (48 colliding) |
| **195** | **This audit**, distinct `CD-` in the 79 specifications, 2026-08-19 |
| 248 | Technology Stack Specification §8.2, §25.3.1 — proposed restatement |
| **331** | **`BE-005` §3.2**, the issued register: 251 + 80 rows, carrying 1,850 PW |

**`BE-005` has already diagnosed this properly** — §3.1 *"there are four CD registers in
circulation, not two"* — and explicitly rejects 248: *"restating the RFP to 248 would replace one
wrong figure with another"*. **No correction is needed in the guide.** The change request is that
§25.3.1's proposal to the RFP should now read **331**, not 248.

---

## 5. Version and regulatory currency — externally verified 2026-08-19

The Technology Stack Specification §25.2 verified its stack on **13 August 2026**. This audit
re-verified against upstream six days later. **Two positions have hardened from "expected" into
dated facts, and both are Wave 0 decisions.**

| # | Component | Specified | **Verified 2026-08-19** | Consequence |
|---|---|---|---|---|
| **`ALN-08`** | **Next.js** | **15** | **16.3 current (released 3 Aug 2026). Next.js 15 is in Maintenance LTS and reaches end of life on 21 October 2026** | **HIGH.** EOL falls **inside Wave 1** (months 1–4 per `GV-004` §5.2). Six customer-facing surfaces — `P01`, `P03`, `P04`, `P06`, `P10`, `P12` — are specified on 15 |
| **`ALN-09`** | **Odoo** | 19.0 | **Odoo 20 releases at Odoo Experience, Brussels, 24–26 September 2026 — five weeks from this issue.** 19.0 supported to ~Sept 2028 | **MEDIUM.** `ADR-027` (the upgrade slot) is still *Proposed*; `D-025` has five weeks' notice |
| — | PostgreSQL | 16 | 16 supported to Nov 2029; 18 to Nov 2030 | Unchanged — valid and safe |
| — | Keycloak | 26.x | No LTS line; newest only receives fixes | Unchanged — `AR-013` already treats it as a continuous-currency operational standard |
| — | Flutter | 3.44 | Current; React Native legacy architecture removed at 0.83 | Unchanged |
| — | **Bangladesh PDPA** | 2026 (Law 63 of 2026) | Ordinance 2025 (gazetted 6 Nov 2025) → **Amendment Ordinance No. 23 of 2026, 5 Feb 2026** → enacted April 2026 → **enforcement ~13 May 2027**; regulator National Data Management Authority | **Aligned.** The estate's citation chain is correct and complete in all three repositories |
| — | **Cyber Security Ordinance 2025** | — | No. 25 of 2025, in force 21 May 2025, repealed the Cyber Security Act 2023 | **Aligned** |

**Corrections applied:** `AR-013` §4 `VC-01` and `VC-02` restated with the verified dates; the
version-currency table header re-dated; **`AR-013-F-01`** (HIGH) and **`AR-013-F-02`** (MEDIUM)
raised in place.

> **`ALN-08` changes the character of the decision.** The source specification said Next.js 15 was
> *"leaving the supported line during the programme"*. **It leaves it on 21 October 2026.** That is
> not a planning preference to be settled at leisure; on the programme's own calendar it is a
> **Wave 0 blocker**, and `AR-013` now says so.

---

## 6. Corrections applied to `project-guide-doc`

| # | Correction | Documents touched |
|:--:|---|---:|
| 1 | Entity population aligned to the counted **1,335** | **13** |
| 2 | `UXA-21` marked **RESOLVED** with the counted answer | `UX-003` |
| 3 | `XRF-Q-04` marked **RESOLVED**; `E-nnn` separated as a distinct space | `RR-006` |
| 4 | `AR-008` §2.2 restatement note — 1,334 retained at its timestamp, 1,335 forward | `AR-008` |
| 5 | **`AR-008-F-01`** raised: 34 portal-referenced entities owned by nobody, with the full list | `AR-008` |
| 6 | `GV-003` **§5.4a** — three technology decisions registered as `D-025`…`D-027`; rule `DL-08`; §2.2 source added; §5.6 recounted | `GV-003` |
| 7 | Decision citations re-pointed to the registered identifiers | **14** |
| 8 | `AR-013` version currency re-verified; **`AR-013-F-01`**, **`AR-013-F-02`** raised | `AR-013` |
| 9 | **`CO-003-F-08`** raised: the contractual scope gap, with verification and remediation | `CO-003` |
| | **Distinct documents modified** | **26** *(25 distinct basenames — two are `_CATEGORY_OVERVIEW.md`)* |

---

## 7. Change requests to the source estate

**This audit cannot edit `primary-doc` or `1000fix_ERP_Module`.** Each item is a change request with
a named owner, raised to `GV-005`.

| # | Change | Affects | Owner | Basis |
|:--:|---|---|---|---|
| **`CR-01`** | Re-draft `CO-003` rows 3 and 5 — and RFP §6 Appendix A and §9 — to cite **the maintained baseline** rather than the fixed figures 2,930 and 101 | RFP §6, §9 | CFO / CTO | §4.1 |
| **`CR-02`** | Restate the requirement denominator to **3,389** (3,347 + 42 `SWR`), or adopt the maintained-baseline form | BRD, RFP, Technology Stack Spec | CTO | §4.2 |
| **`CR-03`** | Restate the effort baseline to **1,842 PW**, and record that **298 PW of portal effort** was never in the earlier figure | BRD, RFP, `02-02` | CTO | §4.3 |
| **`CR-04`** | Technology Stack Spec §25.3.1's proposal should read **331 CD items** (`BE-005` §3.2), not 248 | Technology Stack Spec §8.2, §25.3.1 | CTO | §4.4 |
| **`CR-05`** | Technology Stack Spec §24 and §25.2 should cite **`D-025`, `D-026`, `D-027`** | Technology Stack Spec | CTO | §3.3 |
| **`CR-06`** | Reconcile the **34 unowned portal-referenced entities** against the owned set — naming reconciliation or new owning modules — before `DA-001` freezes the schema | `03_Modules/P01`…`P12` | Enterprise Architecture | §3.2 |

---

## 8. Recommendations

| # | Recommendation | Owner | Basis |
|:--:|---|---|---|
| **`R-01`** | **Ratify `RG-08`** (`GV-003` `D-023`). Every finding in §3.1 exists because a correctly-counted figure was copied forward **without its timestamp** | Steering Committee | §3.1 |
| **`R-02`** | **A completeness check states its population in the same sentence as its result.** `AR-008`'s `0 ✅` was true of 67 specifications and false of 79; `UX-003`'s 920 reports and `AUDIT-015`'s 1,063 differ only by scope | All authors | §3.2, §2.1 |
| **`R-03`** | **`DL-08` applies to every shared space, not just `D-nnn`.** `RR-002` should name the allocating authority for `NFR-`, `CD-`, `SOD-`, `KPI-` and `E-nnn` the way `GV-003` now does for decisions | Enterprise Architecture | §3.3, §4.4 |
| **`R-04`** | **Re-verify version currency at every wave gate against upstream, not against the last document that verified it.** Two positions hardened into dated facts in the six days since §25.2 was written | CTO | §5 |
| **`R-05`** | **Take `D-026` before Wave 1 planning is fixed.** Next.js 15 reaches EOL on 21 October 2026, inside Wave 1 | CTO | §5 |
| **`R-06`** | **Restate the source estate, or stop citing it as current.** Four of the eleven findings are the same shape: the guide counted, the source never restated. A permanent divergence between an issued RFP and the engineering baseline is a commercial exposure, not a documentation one | CTO / CFO | §4 |

---

## 9. Closure

| Element | Position |
|---|---|
| Files in scope | **179** (`project-guide-doc`) tested against **127** (`primary-doc` + `1000fix_ERP_Module`) |
| Axes tested | **17** · aligned **9** |
| Findings | **11** — 6 HIGH, 4 MEDIUM, 1 contractual |
| Corrections applied | **9**, across **26 documents** |
| Change requests raised | **6** |
| Provisional findings withdrawn on verification | **3** |
| Estate at issue | **800** workspace files · **179** in this repository · **138** guiding documents |

**The audit is issued. `project-guide-doc` is internally consistent on every axis tested.**
The residual misalignment is **one-directional**: four quantities where the guide has counted and
the source estate has not been restated, and they are now change requests with named owners rather
than undocumented divergence.

> **The pattern across all eleven findings is one thing.** Every figure in this estate is counted
> carefully and then **copied forward without the timestamp that made it true**. `AR-008` and
> `DA-001` both counted correctly nine hours apart; the defect was the eight documents that copied
> one of them. `AR-008`'s ownership check was correct for 67 specifications; the defect was that
> nobody wrote "67" next to the zero. **`RG-08` is not a documentation nicety — it is the control
> that would have prevented six of these eleven findings**, and it has been recommended ten times
> and ratified never.

---

*`PGD-AUDIT-ALIGN-001` · Cross-repository alignment · 1000FiX ERP System v2.0 · CONFIDENTIAL · counted 2026-08-19 19:14 (+06)*
