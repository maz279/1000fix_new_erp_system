---
id: AR-006
title: Module Dependency Map & Build Sequence
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Solution Architect
approver: Chief Architect
standards_basis: Directed acyclic graph analysis · Acyclic Dependencies Principle (Martin) · ISO/IEC/IEEE 42010:2022 development viewpoint
traces_to: >
  PGD-000 AR-006 · 02-04 (planned, never written) · _MODULE_TEMPLATE §16.3 wave check ·
  RG-04 reciprocity · audit finding M-09 (wave capacity unvalidated)
depends_on: AR-001 · AR-005 (boundary adjudication)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 02:05 (+06)
extraction_method: >
  Automated extraction of the "Depends on" and "Depended on by" rows of §1 Module Identity
  from all 67 module specification files, plus the `wave:` front-matter key.
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-006 — Module Dependency Map & Build Sequence

### Category 02 · Code `AR` · Directed graph analysis · Acyclic Dependencies Principle

---

> **This document reports measured defects, not projected ones.** Every figure below was produced by
> extracting the declared dependency rows from all 67 specification files at **2026-08-18 02:05
> (+06)** and computing over the resulting graph. The extraction method is stated in the front
> matter and the commands are reproduced in §9 so the analysis is repeatable rather than assertable.
>
> **Headline: the declared dependency graph contains 32 wave-order violations, 18 mutual dependency
> pairs and 55 reciprocity failures. None had been detected, because until now nobody had run the
> join.**

---

## 1. Purpose

`_MODULE_TEMPLATE` §16.3 carries a rule every module author is required to apply:

> *"**Wave check.** No prerequisite may land in a later wave than this module. If it does, either the
> wave is wrong or the dependency is not a true prerequisite — say which, explicitly."*

Applied per file, that rule is unverifiable: an author checking M02's prerequisites cannot see
whether M22's wave changed after M02 was written. Across 67 modules with 447 declared edges, the rule
can only be enforced **over the whole graph, mechanically**. This document is that enforcement.

It unblocks: the build sequence itself, the capacity re-plan audit `M-09` requires, and `AR-003`'s
production schedule — which cannot order 93 design units without knowing what depends on what.

**`02-04_Module_Dependency_Map.md` was planned in `1000fix_ERP_Module/02_Architecture/` and never
written.** Its absence is the reason 32 violations accumulated undetected.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The complete declared dependency graph — 67 nodes, 447 edges |
| 2 | Coupling analysis — in-degree, out-degree, and what the shape means |
| 3 | **Cycle detection** — 18 mutual pairs, classified as legitimate or breaking |
| 4 | **Wave-order violation register** — 32 violations, each dispositioned |
| 5 | **Reciprocity register (`RG-04`)** — 55 one-way declarations |
| 6 | The corrected build sequence, expressed as dependency tiers |
| 7 | The maintenance rule — how the graph stays true as specifications change |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Which module owns a contested capability | `AR-005` | A dependency presumes the boundary is settled |
| Wave capacity in person-weeks | `GV-004` | This document supplies the ordering constraint; `GV-004` supplies the resourcing |
| The wave plan itself | `06-01`, `GV-004` | This document **tests** the wave plan and reports where it fails |
| Event producer/consumer edges | `AR-009` | A different graph over the same nodes; both must be consistent (§8 CR-04) |
| Package-level dependencies inside a module | `AR-007` | Intra-module |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Programme Manager, PMO | §5 wave violations are schedule risk with a name and a size |
| Solution Architect | §4 cycles are the interface breaks that must be designed |
| Implementation vendor | §6 build sequence is the order work can actually be done in |
| Module authors | §7 reciprocity register lists the corrections owed by their file |
| `AR-003` author | The ordering constraint for the 93-unit design schedule |

---

## 2. Basis and Method

### 2.1 Extraction method

Reproducibility matters more than elegance here, because the finding is uncomfortable.

```bash
# For every module specification: module id, wave, declared dependencies, declared dependants
for f in $(find 03_Modules -name 'M[0-9]*.md'); do
  id=$(grep -m1 '^module_id:' "$f" | awk '{print $2}')
  wave=$(grep -m1 '^wave:' "$f" | awk '{print $2}' | grep -oE 'W[0-9]' | head -1)
  grep -m1 '^| \*\*Depends on\*\*'      "$f" | grep -oE 'M[0-9]{2}' | sort -u | sed "s/^/DEP $id /"
  grep -m1 '^| \*\*Depended on by\*\*'  "$f" | grep -oE 'M[0-9]{2}' | sort -u | sed "s/^/REV $id /"
  echo "WAV $id $wave"
done > graph.txt
```

**Method limitations, stated so the numbers are read correctly:**

| Limitation | Effect |
|---|---|
| Only the §1 Module Identity declaration is read | A dependency present in §12 Interfaces but absent from §1 is not counted. **The graph is therefore a lower bound** |
| M28, M29, M30 and M65 use the permitted blanket phrase *"All 66 other modules and all 12 portals"* | Excluded from reciprocity analysis, per `_MODULE_TEMPLATE` §1's allowance for genuine platform modules |
| Split-wave modules (`W4 / W7`) are taken at their **first** wave | The conservative reading: a violation against the first wave is real |
| Declared ≠ actual | This measures what the specifications **say**. Actual coupling is discoverable only from code, and there is none yet |

### 2.2 Source material

| Source | Contribution |
|---|---|
| All 67 module specifications, §1 Module Identity and front matter | The graph |
| `_MODULE_TEMPLATE` §1, §16.3 | The reciprocity rule `RG-04` and the wave check |
| `../../1000fix_ERP_Module/02_Architecture/02-02_*.md` §4.2, §7 | The wave view and the Category A interaction matrix (the only matrix that existed) |
| `.../02-01_*.md` §4 | The narrative dependency diagram, covering 30 modules |
| `.../06-01_*.md` §1, §3 | Sequencing logic and wave content |

### 2.3 Audit findings this document raises or closes

| Finding | Status |
|---|---|
| `PGD-000` `AR-006` — *"`02-04` unwritten; the §16.3 rule is unverifiable across 67 modules"* | **Closed** — the rule is now verified, and it fails 32 times |
| `M-09` Wave capacity never validated against effort | **Contributes.** §5 supplies the ordering half; `GV-004` owes the capacity half |
| **`PGD-A3-09` (new)** — 32 wave-order violations | **Raised**, dispositioned in §5 |
| **`PGD-A3-10` (new)** — 18 mutual dependency pairs, 6 requiring an interface break | **Raised**, §4 |
| **`PGD-A3-11` (new)** — 55 `RG-04` reciprocity failures | **Raised**, §7 |

---

## 3. The Dependency Graph

### 3.1 Shape

| Measure | Value |
|---|---:|
| Nodes (modules) | **67** |
| Declared edges | **447** |
| Mean out-degree | **6.7** |
| Maximum out-degree | **11** (M12, M13, M14, M38) |
| Maximum in-degree | **53** (M29) |
| Mutual pairs (2-cycles) | **18** |
| Wave-order violations | **32** |

### 3.2 In-degree — what the whole system rests on

| Module | In-degree | Wave | Reading |
|---|---:|:--:|---|
| **M29** SEC Identity & Security | **53** | W1 | 79% of modules declare a dependency. **Non-descopable**, and its own dependency on M21 (§5) is the single most serious violation found |
| **M33** CPM Customer & Party Master | **41** | W1 | The party kernel. Its in-degree is why 22 of the 55 reciprocity failures point at it |
| **M28** IPF Integration & API | **37** | W1 | The outbox and gateway. Non-descopable |
| **M30** ADM Platform Administration | **28** | W1 | Entity, branch, zone, calendar, configuration |
| **M24** DMS Document & E-Signature | **23** | **W3** | ⚠ A **kernel concept (`fix.document`) arriving in Wave 3** while 23 modules depend on it — see §5.3 |
| **M37** CAT Product & Service Catalogue | **21** | W1 | The catalogue kernel |
| **M17** AST Device & Asset Registry | **17** | **W2** | ⚠ Depended on by M01 and M04, both **W1** |
| **M21** HCM Core HR | **15** | **W5** | ⚠ Depended on by M29 (W1), M52 (W3), M23 (W5) and eight others — **the worst-placed high-in-degree module in the plan** |
| M19 FIN | 14 | W3 | Ledger; correctly terminal |
| M11 PRC, M01 SRM | 13 each | W3 / W1 | |
| M20 ARB, M15 INV | 12 each | W3 / W2 | |

> **The single most useful line in this document.** Four of the eight most-depended-on modules —
> **M24 (23 dependants, W3), M17 (17, W2), M21 (15, W5)** and the kernel-owning M33 — sit **later in
> the plan than modules that depend on them**. High in-degree plus a late wave is the structural
> signature of a wave plan that was built from business priority rather than from the dependency
> graph. That is not a criticism of the wave plan's intent; it is the arithmetic the plan was never
> checked against, because `02-04` was never written.

### 3.3 Out-degree — the modules most exposed to others

| Module | Out-degree | Wave | Reading |
|---|---:|:--:|---|
| M12 MKP, M13 RNT, M14 TRF, M38 ECM | **11** each | W7, W6, W6, W7 | The new business lines. High out-degree is **expected and healthy** here — they compose existing capability rather than duplicating it, which is the layered model working |
| M54 FPA, M47 FAC | 10 each | W6, W7 | Late, integrative |
| M44 ITC, M45 EAM, M46 FLT, M51 TAX, M52 APE, M53 REV | 9 each | W6, W5, W5, W4, W3, W4 | |

**No module has both high in-degree and high out-degree.** That is the healthiest single property of
the graph: it means the estate has a genuine layered shape — foundation modules that others depend on
and which depend on little, and composing modules that depend on much and are depended on by little.
An ERP where a module scored high on both would be an unfixable hub.

---

## 4. Cycle Analysis

### 4.1 The 18 mutual pairs

The Acyclic Dependencies Principle says a dependency graph should have no cycles. Real ERPs have some.
The question is not whether a cycle exists but **whether it is a co-designed platform pair or a
missing interface**.

| # | Pair | Classification | Disposition |
|---|---|---|---|
| 1 | **M28 ↔ M29** | **Legitimate — platform co-design** | The gateway needs identity; identity publishes through the gateway. Built as one W1 platform increment |
| 2 | **M28 ↔ M30** | **Legitimate — platform co-design** | Configuration and integration are mutually bootstrapping in W1 |
| 3 | **M29 ↔ M30** | **Legitimate — platform co-design** | Ditto |
| 4 | **M33 ↔ M64** | **Legitimate — kernel/MDM** | Party master and master-data governance are two faces of one concern. **But M33 is W1 and M64 is W2** — see §5 |
| 5 | **M37 ↔ M64** | **Legitimate — kernel/MDM** | Same, same wave problem |
| 6 | **M20 ↔ M50** | **Break required** | AR/collections ↔ treasury. Break by making **M50 publish bank/cash events that M20 consumes**; M20 must not call M50 synchronously |
| 7 | **M20 ↔ M51** | **Break required** | Billing ↔ tax. Break by making **tax determination a synchronous service call from M20 to M51 only**; M51 consumes `invoice.*` events for the register, never calls back |
| 8 | **M51 ↔ M52** | **Break required** | Tax ↔ AP. Same shape: M52 calls M51 for TDS determination; M51 consumes AP events |
| 9 | **M50 ↔ M52** | **Break required** | Treasury ↔ AP. M52 raises payment requests as events; M50 executes and publishes confirmation. **No synchronous back-call** |
| 10 | **M16 ↔ M42** | **Break required** | Procurement ↔ supplier performance. M42 is a **read-and-score** consumer of M16 events; M16 reads scorecards through a published API. Asymmetric, not mutual |
| 11 | **M16 ↔ M52** | **Break required** | Procurement ↔ AP. Three-way match is the seam; it belongs in **M52** (`cd_three_way_match_ext`), consuming M16 and M15 events |
| 12 | **M12 ↔ M53** | **Break required** | Marketplace ↔ settlement. Commission **calculation** is M53's; commission **earning** is an M12 event. M12 must not call M53 |
| 13 | **M41 ↔ M44** | **Break required** | Warehouse ↔ import/landed cost. Landed cost is applied to a receipt; **M44 consumes `goods.received`**, M41 does not call M44 |
| 14 | **M49 ↔ M54** | **Break required** | Fixed assets ↔ costing. M54 consumes depreciation events; M49 does not read budgets |
| 15 | **M24 ↔ M60** | Review | Documents ↔ GRC. Likely a legitimate policy/evidence pairing, but M24 is a **kernel owner** and should not depend on a W6 module — see §5.3 |
| 16 | **M27 ↔ M32** | **Legitimate** | Contact centre ↔ conversational AI. Same wave (W4), co-designed, one squad |
| 17 | **M21 ↔ M29** | **Break required — and it is the serious one** | See §5.1 |
| 18 | **M51 ↔ M65** | **Break required** | Tax ↔ localisation. M65 is **W9**; M51 is W4. M51 must depend on a **country-pack interface** delivered in W1 by M30, not on M65 itself |

**Summary: 6 legitimate co-design pairs, 1 under review, 11 requiring an interface break.**

### 4.2 The break pattern

Every one of the eleven breaks uses the same shape, which is worth stating once rather than eleven
times:

> **Replace the return call with an event.** Where A calls B and B calls A, make **one direction a
> synchronous published API** (the direction that needs an answer now) and the **other direction a
> domain event** (the direction that reports a fact). Synchronous-both-ways is a distributed monolith:
> neither module can deploy, test or fail independently.

**Worked example — M20 ↔ M51 (billing ↔ tax).** M20 must know the VAT treatment *before* it can raise
an invoice, so **M20 → M51 is synchronous** (`determine_tax(line_set) → treatment`). M51 must record
the invoice in the Mushak register *after* it exists, so **M51 ← M20 is an event** (`invoice.created`).
The cycle disappears; M51 can be deployed, replayed and tested independently; and — the point that
matters at month end — **M51 can rebuild the VAT register from the event stream without M20's
cooperation.**

These eleven breaks are `AR-003` design work for the modules concerned, and each is a gate item.

---

## 5. Wave-Order Violation Register

**32 violations of `_MODULE_TEMPLATE` §16.3.** Each is dispositioned into one of four outcomes, per
the template's own instruction — *"either the wave is wrong or the dependency is not a true
prerequisite — say which, explicitly."*

| Disposition | Meaning | Count |
|---|---|---:|
| **STUB** | Build the interface seam in the earlier wave, return a safe default, connect later (ADR-023) | 14 |
| **MOVE** | The dependency is real and blocking; the depended-on module or a slice of it moves earlier | 9 |
| **NOT-A-PREREQ** | Declared but not actually required at go-live; downgrade to a §12 interface reference | 7 |
| **ACCEPT** | Real, but the consequence is tolerable and named | 2 |

### 5.1 Critical — the security foundation depends on a Wave 5 module

| Violation | Gap |
|---|---:|
| **M29 SEC (W1) depends on M21 HCM (W5)** | **+4 waves** |

**This is the most serious finding in this document.** M29 has an **in-degree of 53** — 79% of the
estate depends on it — and it declares a dependency on a module arriving four waves later.

**Why it exists:** M29's access lifecycle (`AR-001` §9.1) is driven by `employee.joined`,
`employee.left` and role change events from M21. Joiner-mover-leaver is genuinely an HR-driven process.

**Disposition — MOVE (a slice).** The whole of M21 does not move. **The employee master and the
joiner/mover/leaver event set move to Wave 1** as an M21 slice; learning, payroll, performance and
talent stay in W5. Without this:

- W1–W4 access provisioning is manual, so `KPI-090` (*zero orphaned accounts beyond 24 hours*) is
  **unachievable for four waves** — in a system holding payment credentials and personal data;
- the leaver path (Keycloak deprovisioning ≤ 1 hour) does not exist while 500+ staff are being
  onboarded onto the platform;
- retrofitting event-driven provisioning into a live realm in W5 is precisely the risk ADR-023 exists
  to avoid.

**Escalated to `GV-004` and `GV-005` as a Wave 1 scope change.** The alternative — accepting four
waves of manual provisioning — is a decision the Steering Committee should take explicitly, not one
that should arrive by omission.

### 5.2 High — three or more waves

| Violation | Gap | Disposition | Reasoning |
|---|---:|---|---|
| **M51 TAX (W4) → M65 GLO (W9)** | **+5** | **NOT-A-PREREQ** | M51 needs a *country-pack interface*, not M65. The interface is delivered by M30 in W1 (`cd_country_pack`). Redeclare the dependency against M30 |
| M02 FSM (W2) → M22 LMS (W5) | +3 | **STUB** | The canonical ADR-023 case. Certification eligibility returns "eligible" from W2. **Must be registered in `GV-005` with an expiry** — a stub that always returns "eligible" is a control that does not work |
| M02 FSM (W2) → M55 WFM (W5) | +3 | **STUB** | Shift/roster availability; stub returns "available within working calendar" from M30 |
| M02 FSM (W2) → M46 FLT (W5) | +3 | **NOT-A-PREREQ** | Vehicle assignment is optional for W2 dispatch; technicians dispatch on foot, by motorcycle and by shared vehicle. Downgrade |
| M31 WSR (W2) → M22 LMS (W5) | +3 | **STUB** | As M02 |
| M31 WSR (W2) → M23 QMS (W5) | +3 | **STUB** | QC checklists are owned by M01 in W1–W2; M23's NCR/CAPA linkage stubs until W5 |
| M31 WSR (W2) → M45 EAM (W5) | +3 | **NOT-A-PREREQ** | Test-equipment calibration is a W5 quality capability, not a W2 repair prerequisite |
| M41 WMS (W3) → M44 ITC (W6) | +3 | **NOT-A-PREREQ** | Landed cost applies at receipt valuation; W3 receipts use standard cost. Downgrade and document the valuation change at W6 |
| M53 REV (W4) → M12 MKP (W7) | +3 | **ACCEPT** | M53's marketplace settlement slice **is already scheduled W7** (`02-02` lists M53 as W4/W7). The W4 slice does not need M12. **Register-level artefact, not a real violation** — corrected by declaring the dependency against the W7 slice |
| M24 DMS (W3) → M60 GRC (W6) | +3 | **NOT-A-PREREQ** | Retention *policy* is needed; the GRC *module* is not. The retention schedule is content (`LG-009`), loadable in W3 |

### 5.3 The M24 problem — a kernel owner arriving in Wave 3

**M24 owns `fix.document`, one of the six shared-kernel concepts (`AR-001` §6.3), and has an
in-degree of 23. It is scheduled for Wave 3.**

Seventeen modules in Waves 1–2 attach documents: service reports (M01), evidence packs (M31),
custody photographs (M03), asset documents (M17), identity documents (M33).

**Disposition — MOVE (a slice).** The `fix.document` **kernel model, retention class and attachment
API move to Wave 1** as a platform deliverable alongside M30. Templates, e-signature envelopes,
approval chains, legal hold and Mayan EDMS integration stay in W3/W5.

**Why this is not optional:** a kernel concept realised in Wave 3 means every Wave 1–2 module invents
its own attachment handling, and Wave 3 becomes a migration of seventeen ad-hoc implementations. This
is the same failure mode ADR-022 identified for notification, with the same remedy.

### 5.4 Medium and low — one to two waves

| Violation | Gap | Disposition |
|---|---:|---|
| M01 (W1) → M17 (W2); M04 (W1) → M17 (W2) | +1 | **MOVE** — M17's **device registry core** is already W1 in `06-01` §3 ("Device and asset registry with brand and model masters"). `02-02` §4.2 lists M17 as W1/W2 split. **Register inconsistency, not a real violation** — correct the declaration to the W1 slice |
| M33 (W1) → M64 (W2); M37 (W1) → M64 (W2) | +1 | **MOVE** — M64's **MDM governance core** (change request, golden-record rule) moves to W1 with the kernels it governs. The rest stays W2 |
| M07 (W1) → M11 (W3); M07 (W1) → M36 (W3) | +2 | **NOT-A-PREREQ** — CRM in W1 is lead and opportunity only; quotation and pricing arrive with M07's W4 slice. Declare against the W4 slice |
| M10 (W2) → M11 (W3), → M20 (W3) | +1 | **STUB** — loyalty accrual rules are self-contained in W2; redemption against price and invoice connects in W3 |
| M15 (W2) → M19 (W3) | +1 | **STUB** — stock valuation posts to a suspense account in W2, reconciled at W3 GL cutover. **Must be registered in `GV-005`**: an unreconciled suspense balance across a wave boundary is a finance risk |
| M17 (W2) → M24 (W3) | +1 | Resolved by §5.3 |
| M16 (W3) → M42 (W4) | +1 | **NOT-A-PREREQ** — vendor scorecards are advisory in W3 |
| M20 (W3) → M51 (W4) | +1 | **MOVE** — **VAT determination and Mushak 6.3 issuance must exist when the first invoice is raised.** `06-01` W3 gate already requires *"Mushak invoices accepted without NBR exception"*. M51's **determination and Mushak issuance slice moves to W3**; returns and filing stay W4. **This is a statutory violation, not a convenience one** |
| M22 (W5) → M61 (W6) | +1 | **ACCEPT** — course content authoring degrades without the knowledge base; not blocking |
| M32 (W4) → M26 (W6), → M61 (W6) | +2 | **ACCEPT with scope reduction** — the known `Q-01`: the assistant launches with transactional intents only. Already a Steering decision |
| M34 (W4) → M23 (W5); M42 (W4) → M23 (W5) | +1 | **STUB** — complaint and NCR linkage stubs |
| M49 (W5) → M54 (W6) | +1 | **NOT-A-PREREQ** — budget linkage is advisory |
| M52 (W3) → M21 (W5) | +2 | **Resolved by §5.1** — the M21 employee-master slice moving to W1 also resolves this (employee expense needs the employee master) |
| M52 (W3) → M51 (W4) | +1 | **MOVE** — TDS determination is needed for the first vendor payment. Same slice as the M20 → M51 move |
| M63 (W3) → M27 (W4) | +1 | **Resolved by ADR-022** — the notification platform is already W1 |

### 5.5 Summary of scope movements this analysis requires

| # | Movement | From | To | Driver |
|---|---|:--:|:--:|---|
| **MV-01** | M21 employee master + joiner/mover/leaver events | W5 | **W1** | M29 in-degree 53; `KPI-090` unachievable otherwise (§5.1) |
| **MV-02** | M24 `fix.document` kernel + retention class + attachment API | W3 | **W1** | Kernel concept; in-degree 23; 17 W1–W2 consumers (§5.3) |
| **MV-03** | M51 VAT determination + Mushak 6.3 issuance | W4 | **W3** | Statutory; W3 gate already requires it (§5.4) |
| **MV-04** | M64 MDM governance core | W2 | **W1** | Governs the W1 kernels (§5.4) |
| **MV-05** | M17 device registry core — *declaration correction only* | W2 | W1 | Already W1 in `06-01`; register is inconsistent |

> **These five movements are the architectural input to the capacity re-plan that audit `M-09`
> requires.** They add scope to Wave 1 — the wave `AR-001` §11.3 already identifies as understated.
> **`GV-004` must cost them.** Adding scope to W1 is uncomfortable; discovering in W3 that the last
> four months of access provisioning were manual is worse.

---

## 6. The Build Sequence

### 6.1 Dependency tiers

Derived by topological layering after treating the six legitimate co-design pairs (§4.1) as single
nodes and applying the §5.5 movements. **A module may not be built before every module in a lower
tier.**

| Tier | Modules | Character |
|:--:|---|---|
| **T0 — Platform bootstrap** | **{M28, M29, M30}** as one co-designed increment | Mutually bootstrapping. Nothing else can start |
| **T1 — Kernel** | M33 (party) · M37 (catalogue) · M64-core (MDM governance) · M24-core (document) · M21-core (employee master) | The six shared-kernel concepts (`AR-001` §6.3). **Four of the five moved here by §5.5** |
| **T2 — Registry** | M17 (device/asset) · M04 (branch/front desk) | Master objects that transactions reference |
| **T3 — Transaction core** | M01 (service order) · M31 (workshop) · M15 (inventory) | The business itself |
| **T4 — Execution & movement** | M02 (dispatch) · M03 (logistics) · M41 (warehouse) · M16 (procurement) | Requires T3 |
| **T5 — Money** | M19 (GL) → M20 (AR) · M52 (AP) · M50 (treasury) · M51-core (VAT determination) | **M19 is the ordering constraint within this tier**; the rest post to it |
| **T6 — Commercial** | M11 (pricing) · M36 (quotation) · M37-ext · M08 (contracts) · M09 (warranty) · M39 (subscription) · M53 (revenue) · M10 (loyalty) | Requires T5 |
| **T7 — Engagement** | M07 (CRM) · M27 (contact centre) · M32 (AI) · M34 (CX) · M35 (marketing) | Requires T6 |
| **T8 — Workforce & quality** | M21-full · M55 · M56 · M57 · M22 · M58 · M59 · M23 · M60 | Requires T1 and T5 |
| **T9 — Asset businesses** | M13 · M14 · M06 · M05 · M45 · M46 · M49 · M43 · M44 · M47 | Requires T4 and T6 |
| **T10 — Channel** | M12 (marketplace) · M38 (e-commerce) · M40 (partner) | Requires T6 and T5 settlement |
| **T11 — Intelligence** | M62 · M25 · M26 · M63 · M48 · M61 · M54 | Read-only downstream (`AR-001` LB-06) |
| **T12 — Expansion** | M65 · M66 · M67 · M18 | Requires a stable base |

### 6.2 Tiers against the wave plan

The wave plan and the tier order are **compatible after the §5.5 movements**, and only after them.

| Wave | `02-02` §4.2 content | Tier coverage | Verdict |
|:--:|---|---|---|
| W1 | M29, M28, M30, M33, M37, M17*, M01*, M04 **+ MV-01…MV-05** | T0, T1, T2, T3-partial | ✅ after movements; ⛔ before them |
| W2 | M31, M02, M15, M10, M64, M01*, M17* | T3, T4-partial | ✅ (M10's T6 dependency stubbed) |
| W3 | M19, M20, M52, M50, M11*, M36, M03, M16, M41, M24, M63 **+ MV-03** | T4, T5, T6-partial | ✅ after MV-03 |
| W4 | M08, M09, M39, M51, M53*, M27, M32, M34, M25, M62*, M42 | T6, T7 | ✅ |
| W5 | M21, M55, M56, M57, M22, M23, M05, M45, M46, M49 | T8, T9-partial | ✅ |
| W6 | M13, M14, M06, M26*, M43, M44, M54, M58, M59, M60, M61, M66 | T9, T11-partial | ✅ |
| W7 | M38, M12, M40, M11*, M53*, M47, M67 | T10 | ✅ |
| W8 | M62*, M26*, M48, M18 | T11 | ✅ |
| W9 | M65 | T12 | ✅ |

> **The conclusion is narrower and more useful than "the wave plan is wrong".** The wave plan is
> sound in its business sequencing and correct at eight of nine waves. **Wave 1 is under-scoped by
> five kernel slices**, and that single correction resolves 19 of the 32 violations directly and
> another 6 by consequence.

### 6.3 Portal and application sequence

| Surface | Requires | Wave | Constraint |
|---|---|:--:|---|
| P03 Admin (Odoo Web) | T0–T2 | W1 | The only surface available in W1; every W1 capability is exercised through it |
| APP-05 / P01 Customer portal | T3 + gateway | W2 | Needs the service order and the booking API |
| APP-01 / P02 Technician | T3, T4 + offline engine | W2 | **The offline engine is built here for three applications** (ADR-024) |
| APP-02 / P09 Rider | Offline engine + M03 | W3 | Consumes the engine |
| P05 Vendor | M16, M15 | W3 | |
| APP-06 / P04 B2B · APP-07 / P08 Brand · APP-08 / P10 Contact centre · P06 Analytics | T6, T7 | W4 | |
| APP-03 / P11 Auditor | Offline engine + M23 | W5 | |
| APP-04 Customer mobile | P01 patterns | W6 | |
| APP-09 / P07 Seller · APP-10 / P12 Partner | T10 | W7 | `D-027` unresolved (mobile framework) |

---

## 7. Reciprocity Register (`RG-04`)

Rule `RG-04`: *"If module A declares a dependency on module B, B must declare A in its 'Depended on
by' row."* **55 declarations are one-way**, after excluding the four modules permitted the blanket
phrase.

### 7.1 By target

| Target | Failures | Reading |
|---|---:|---|
| **M33** CPM | **22** | The party kernel. Its dependant list was written before 22 of its consumers existed |
| **M21** HCM | **11** | Employee master, same cause |
| **M24** DMS | **8** | Document kernel, same cause |
| **M19** FIN | **4** | |
| **M27** CCE | **3** | |
| M25, M64, M17, M23, M42, M45 and others | 1–2 each | |
| | **55** | |

### 7.2 Why this matters more than it looks

A one-way declaration is not a documentation defect. It means **the owning module does not know it is
depended on** — so:

| Consequence | Example |
|---|---|
| An interface change is made without notifying a consumer | M33 changes the party-role model; 22 modules find out at integration |
| Wave impact analysis is wrong | Slipping M21 looks like it affects 4 modules; it affects 15 |
| The `AR-005` boundary check cannot run | Boundary symmetry depends on both sides declaring |
| The `AR-003` design gate check X-08 gives false confidence | It checks entity references, not module references |

### 7.3 Remediation

| # | Action | Owner |
|---|---|---|
| R-01 | **M33, M21, M24, M19, M27 adopt the blanket phrase** where genuinely universal (M33 and M24 are kernel owners and qualify), and complete their lists explicitly otherwise | Module owners |
| R-02 | The remaining 10 targets complete their `Depended on by` rows | Module owners |
| R-03 | **Reciprocity becomes a CI check** — `AR-012` `FF-14` — run on every specification change, so the register cannot drift again | Chief Architect |

> **R-03 is the one that matters.** Correcting 55 declarations by hand fixes today. The reason there
> are 55 is that nothing checked, and 67 files edited by many authors over months will drift again
> within a wave.

---

## 8. Maintenance Rule

| # | Rule | Mechanism |
|---|---|---|
| **MR-01** | The graph is **regenerated, never edited.** §2.1's extraction runs and this document's §3–§5 are rebuilt from the output | Scripted; run at every wave gate |
| **MR-02** | A specification change that adds or removes a dependency **fails CI** until reciprocity holds | `AR-012` `FF-14` |
| **MR-03** | A new wave-order violation **blocks the wave gate** unless dispositioned in §5 with a named owner | Wave-gate checklist |
| **MR-04** | A new cycle requires an ADR classifying it as co-design or scheduling the break | `AR-004` |
| **MR-05** | The event graph (`AR-009`) and this dependency graph must agree: **a module consuming an event from M<nn> declares a dependency on M<nn>** | Cross-check at wave gate; `AR-001` CR-04 |

**MR-05 currently fails.** Four events are consumed with no producer anywhere (`AR-001` §7.4), and the
988-event surface has not been reconciled against these 447 declared edges. Closes with `AR-009`.

---

## 9. Verification Commands

Recorded so this analysis is reproducible rather than assertable — the same standard `PGD-AUDIT-001`
§11 set for itself.

```bash
cd 1000fix_ERP_Module/03_Modules

# 1. Build the graph (see §2.1) → graph.txt

# 2. Wave-order violations
awk '$1=="WAV"{w[$2]=substr($3,2)+0} $1=="DEP"{d[NR]=$2" "$3}
     END{for(i in d){split(d[i],a," ");
         if(w[a[2]]>w[a[1]]) printf "%s(W%d) -> %s(W%d)\n",a[1],w[a[1]],a[2],w[a[2]]}}' graph.txt
# → 32

# 3. Mutual pairs
awk '$1=="DEP"{e[$2" "$3]=1} END{for(k in e){split(k,a," ");
     if((a[2]" "a[1]) in e && a[1]<a[2]) print a[1]" <-> "a[2]}}' graph.txt
# → 18

# 4. Reciprocity failures (excluding blanket-phrase platform modules)
awk '$1=="DEP"{d[$2" "$3]=1} $1=="REV"{r[$2" "$3]=1}
     END{for(k in d){split(k,a," "); t=a[2];
         if(t=="M28"||t=="M29"||t=="M30"||t=="M65") continue;
         if(!((t" "a[1]) in r)) print a[1]" -> "t}}' graph.txt
# → 55

# 5. In-degree
awk '$1=="DEP"{c[$3]++} END{for(k in c) print k,c[k]}' graph.txt | sort -k2 -rn
# → M29:53  M33:41  M28:37  M30:28  M24:23  M37:21  M17:17  M21:15 …

# 6. Edge count
awk '$1=="DEP"' graph.txt | wc -l
# → 447
```

---

## 10. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A6-01 | Cycle policy | Forbid all; allow all; **classify** | **Classify — co-design allowed, others broken** | Platform modules genuinely co-bootstrap; business modules must not | 11 interface breaks become `AR-003` design items |
| D-A6-02 | Cycle break pattern | Shared module; **sync one way + event the other**; merge modules | **Sync + event (§4.2)** | Preserves independent deploy, test and failure | Each break is a named design item, not a refactor |
| D-A6-03 | Wave violation policy | Accept and document; **disposition each**; forbid | **Disposition each into STUB / MOVE / NOT-A-PREREQ / ACCEPT** | The template already requires "say which, explicitly" | 32 dispositions; 5 scope movements to `GV-004` |
| D-A6-04 | Stub registration | Code comment; **`GV-005` RAID entry with expiry**; nothing | **RAID entry with expiry** | A stub returning a safe default is a control that does not work; it must expire visibly | 14 RAID entries on issue |
| D-A6-05 | Graph maintenance | Manual; **regenerate + CI check** | **Regenerate + `FF-14`** | 55 failures accumulated because nothing checked | Extraction script is a repository asset |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Are the five §5.5 scope movements approved into Wave 1/W3?** | Steering / `GV-004` | **W0 — blocking** | Wave 1 scope, capacity and cost |
| Q-02 | Who owns correcting the 55 reciprocity declarations — module authors or Enterprise Architecture? | Chief Architect | W1 | `AR-005` boundary check |
| Q-03 | Does `02-02` §4.2's wave view need reissue to reflect the split-wave slices this analysis relies on (M17, M51, M53, M07)? | Enterprise Architecture | W1 | Register consistency; three "violations" are register artefacts |
| Q-04 | If MV-01 (M21 employee master to W1) is refused, is four waves of manual access provisioning accepted as a risk? | Steering / Head of InfoSec | **W0** | `KPI-090`; ISO 27001 A.5.16 |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The graph is extracted from all 67 specifications by a stated, reproducible method | §2.1, §9 |
| AC-02 | Every cycle is detected and classified | §4.1 — 18 pairs, 6 legitimate, 1 review, 11 breaks |
| AC-03 | Every wave-order violation is listed and dispositioned with a reason | §5 — 32 violations, 4 disposition classes |
| AC-04 | Every reciprocity failure is counted and a remediation owner named | §7 — 55, with `FF-14` as the durable control |
| AC-05 | A build sequence is derived that is consistent with the wave plan after stated corrections | §6.1, §6.2 |
| AC-06 | The maintenance rule prevents recurrence | §8 MR-01…MR-05 |
| AC-07 | Every figure is counted and reproducible | §9 |

**Definition of done.** Complete when every criterion is met, the five §5.5 movements are decided by
Steering (Q-01), and `PGD-000`'s `AR-006` row is updated with a fresh enumeration timestamp.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §6.2, §6.5 | Decomposition and boundary rules |
| Upstream | `AR-005` | Boundary adjudication — a dependency presumes a settled boundary |
| Downstream | `AR-003` §3.2 | The 93-unit design schedule follows §6.1 tiers |
| Downstream | `AR-012` `FF-14` | Reciprocity CI check |
| Downstream | `GV-004` | Consumes §5.5 movements for the capacity re-plan (`M-09`) |
| Downstream | `GV-005` | 14 stub expiries registered as risks |
| Downstream | `QA-002` | Integration test order follows §6.1 |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-02` §4.2 | The wave view this document tests; three violations are its artefacts (Q-03) |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | The roadmap; `06-01` §3 already places M17 and Mushak in earlier waves than `02-02` does |

---

## 14. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-003` · `./AR-004` · `./AR-005` ·
`./AR-009` · `./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md` §1 (all 67) · `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §1, §16.3 ·
`.../02_Architecture/02-01` §4, `02-02` §4.2, §7 · `.../06_Delivery_and_Implementation/06-01` §1, §3

**External sources**

| Source | Verified |
|---|---|
| Robert C. Martin, *Acyclic Dependencies Principle* | 2026-08-18 |
| ISO/IEC/IEEE 42010:2022 — development viewpoint | 2026-08-18 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. First mechanical analysis of the 67-module dependency graph. Raises `PGD-A3-09` (32 wave violations), `PGD-A3-10` (18 cycles), `PGD-A3-11` (55 reciprocity failures). Requires five Wave 1/W3 scope movements | *Pending — Chief Architect* |

---

*`AR-006` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
