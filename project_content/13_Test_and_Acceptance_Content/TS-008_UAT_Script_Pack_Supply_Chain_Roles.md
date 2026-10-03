---
id: TS-008
title: UAT Script Pack — Supply Chain Roles
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Owners Forum with QA Lead
author: QA Lead with Inventory Manager, Procurement Officer, Logistics Manager and Content Design
reviewers: [Inventory Manager, Procurement Officer, Logistics Manager, Warehouse representatives, Branch Store Keeper representatives, Finance Manager, Localisation Lead]
approver: QA Lead with Inventory Manager
content_class: E
purpose: >
  The acceptance scripts executed by the roles that hold custody of physical value — inventory,
  branch stores, procurement, warehouse, logistics coordination and riders. Stock and custody errors
  compound daily until they are detected: a storekeeper who can post an adjustment without a count,
  a rider who can close a consignment without a signature, or a warehouse operative who can release
  quarantined goods produces a stock position that diverges from reality by a little every day and
  is discovered at a physical count months later, by which time neither the cause nor the value can
  be established.
traces_to: [M15, M16, M03, M41, M42, M43, M44, M19, M20, 05-04, 05-04 §7, 05-05, 06-02 §4, MD-004, MD-005, MD-022, MD-023, SP-009, SP-016, SP-017, SP-018, TR-012, TR-013, TR-020, DT-021, DT-023, DT-024, DT-025, DT-026, DT-027, DT-028, DT-029, DT-044, UI-009, UI-015, UI-019, UI-027, UI-028, UI-041, TS-001, TS-002, TS-004, TS-006, TS-012, TS-015, TS-018]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: TS-008_UAT_Script_Pack_Supply_Chain_Roles_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.3 Logistics and Supply Chain (R15 10–25, R16 50–150, R17 5–10, R18 51+, R19 4–8, R20 15–30); §3.3 Pillar C permission matrix with (o)/(b)/(own loc) scopes; §7 requisition and write-off bands; §6 SOD-02, SOD-05
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §4 BRU-LOG-01…08, §6 BRU-INV-01…08 and BRU-SCM-01…05, §12.3 AUT-031…AUT-040
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 2 G2-06 (inventory accuracy ≥ 95% at migrated locations, verified by count), G2-07 (van stock reconciling daily, variance < 2%); Gate 3 G3-06, G3-07 (unbroken chain of custody, zero exceptions); §2.6 KPI-042…049
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — Supply Chain Roles

| Item | Value |
|---|---|
| Test level | **UAT** — method in [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 |
| Roles executing | `R15` `R16` `R17` `R18` `R19` `R20` — **6 roles, 135–274 people** |
| Modules covered | `M15` `M16` `M03` `M41` `M42` `M43` `M44`, with `M19` `M20` as touchpoints |
| Portals covered | `P03` (Inventory, Procurement consoles), `P05`, `P09` |
| Environment | `UAT` — frozen for the cycle |
| Test data set | `TS-002` — personas 5, 8; sets `M-01`, `D-10`, `A-01`…`A-08` |
| Wave | W3 · **but `G2-06` and `G2-07` are W2 criteria** — open item `O-01` |

> **Template conformance.** As `TS-006`: `TPL_Test_Script.md` at pack level, all six sections
> retained in order with pack-level interpretation.

> **Method by reference.** `UA-01`…`UA-18` and the seven-phase pattern are in
> [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2. `UA-19` and `UA-20`
> from [`TS-007`](TS-007_UAT_Script_Pack_Commercial_and_Contract_Roles.md) §2.1 apply to valuation
> scripts. This pack adds `UA-23`…`UA-26` (§2.1).

---

## 1. Traceability

### 1.1 Why physical verification is part of the script

Every other UAT pack can be executed entirely on a screen. **This one cannot.** A stock script that
does not touch stock proves that the system will record whatever it is told, which is the opposite
of what needs proving.

| Screen-only script proves | Physical script proves |
|---|---|
| The count screen accepts a quantity | The quantity on the shelf equals the quantity in the system |
| The scan field accepts a barcode | The label on the part scans, on the scanner the branch actually owns (`DT-044`) |
| Custody was recorded | Both parties were present and identified, and the seal number matched |
| The adjustment posted | The adjustment could not have been posted without a count behind it |

`06-02` `G2-06` makes this explicit: inventory accuracy ≥ 95% at migrated locations, **verified by
count**. That is a physical activity written into an acceptance gate, and `UA-23` binds it into the
scripts.

### 1.2 Traceability obligation

Per `TS-006` §1.2 and `TS-007` `UA-20`, with two required columns added:

| Field | Source |
|---|---|
| **Location** | `MD-004` warehouse and storage location — a stock script without a location is untestable, because scope in this pack is `(b)`, `(own loc)` or `(a)` and the refusal case depends on it |
| **Valuation effect** | The expected effect on quantity **and** value, from `MD-023` UoM and the valuation basis — `SL-19` applied to UAT |

### 1.3 Role coverage

| Role | Headcount | Scripts | `P0` | Language | Portal | Scope | SOP | Course pack |
|---|---:|---:|---:|---|---|---|---|---|
| `R17` Inventory Manager | 5–10 | **12** | 6 | English | `P03`, `P05`, `P06` | all locations | `SP-016`, `SP-018` | `TR-012` |
| `R18` Branch Store Keeper | **51+** | 10 | 5 | **Bengali** | `P03` | own branch stock `(b)` | `SP-016` | `TR-012` |
| `R19` Procurement Officer | 4–8 | 10 | 6 | English | `P03`, `P05` | central procurement | `SP-017` | `TR-013` |
| `R15` Logistics Coordinator | 10–25 | 10 | 5 | Bengali or English | `P03`, `P05`, `P09` | own area or central | `SP-009` | `TR-020` |
| `R16` Rider / Delivery Agent | 50–150 | 8 | 5 | **Bengali** | `P09` | own manifest `(o)` | `SP-009` | `TR-020` |
| `R20` Warehouse Operative | 15–30 | 8 | 4 | **Bengali** | `P03` | own location | `SP-018` | `TR-012` |
| **Total** | **135–274** | **58** | **31** | | | | | |

**Three of the six roles are Bengali-first and together they are 116–231 of the 135–274 people.**
That is why this pack is bilingual while `TS-007` is not: `CG-010` §3.3's test is met by
storekeepers, riders and warehouse operatives, not by the inventory manager.

---

## 2. Preconditions

### 2.1 Additional rules for custody and stock scripts

| # | Rule |
|---|---|
| **UA-23** | **A stock or custody script is executed against physical goods** — real parts, real labels, the branch's own scanner, a real vehicle where the script requires one. A simulated scan is recorded as a simulation and does not count towards `G2-06` |
| **UA-24** | Every stock script asserts **quantity, location and value** together (`SL-19`). A quantity-only assertion passes on a valuation defect |
| **UA-25** | Every custody script requires **both parties present** and captures what each contributed — scan, identity, OTP, signature, seal number. A custody step performed by one person is a custody defect, not a shortcut |
| **UA-26** | Every script that could allow the same person to both **cause** and **justify** a stock movement exercises the segregation refusal (`SOD-05`, `SOD-02`) |

### 2.2 Additional preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-006` preconditions 1–4, 7, 9, 11; `TS-004` SIT exit on the same release | Exit records |
| 2 | `MD-004` locations configured for the branches and warehouses under test, **including a quarantine location** | `BRU-INV-07` |
| 3 | `MD-005` dispatch zones configured, including a cross-zone boundary address (`TS-002` `A-08`) | `MD-048` |
| 4 | `MD-022` part catalogue and compatibility matrix loaded; `MD-023` UoM and packaging | `TD-04` |
| 5 | **Physical stock staged**: at least 40 real parts across 3 locations, with `DT-044` labels applied, one serialised, one with an expired shelf life, one hazardous (`TS-002` `D-10`) | `UA-23` — **no owner allocated**, `O-02` |
| 6 | The branch's own barcode scanner, label printer and a vehicle for the custody scripts | `05-06` §10; `UA-23` |
| 7 | Vendor master with one active, one inactive and one unapproved vendor; `P05` access for persona 5 | `BRU-SCM-02` |
| 8 | Two distinct user accounts per SoD rule under test | `UA-26`; `TS-002` `O-04` |
| 9 | Opening stock control total signed, so variance is measurable rather than arguable | `G2-06`; `DM-007` — **unwritten**, `O-05` |
| 10 | Riders' devices: mid-range Android 11, 3 GB RAM, with the `P09` build | `05-06` §10 |

---

## 3. Scripts

### 3.1 Block A — `R17` Inventory Manager · 12 scripts

`SP-016`, `SP-018` · `TR-012` · all locations

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R17-001` | See network stock, identify a stockout risk, and act before it delays a job | `AUT-031`; `KPI-044` | **P0** |
| `UAT-R17-002` | Approve an inter-branch transfer and confirm in-transit stock is valued and visible at neither end as available | `BRU-INV-02`(H); `UA-24` | **P0** |
| `UAT-R17-003` | **Try to post a stock adjustment above threshold without a reason code and approval, and be refused** | `BRU-INV-06`(H); `05-04` §7 | **P0** |
| `UAT-R17-004` | **Try to post an adjustment justified by a count you performed yourself, and be refused** | `SOD-05`; `UA-26` | **P0** |
| `UAT-R17-005` | Confirm brand consignment stock is excluded from own-stock valuation and reported separately | `BRU-INV-04`(C); `UA-24` | **P0** |
| `UAT-R17-006` | Run a cycle count generated by ABC class and location, and reconcile the variance | `AUT-036`; `G2-06` `UA-23` | **P0** |
| `UAT-R17-007` | Raise a requisition up to `BDT 50,000`, and **be refused above it** | `05-04` §7; `UA-10` | P1 |
| `UAT-R17-008` | Confirm van-stock variance across all technicians is under 2% after a shift-end reconciliation | `AUT-035`; `G2-07`; `KPI-047` | P1 |
| `UAT-R17-009` | Act on a dead-stock disposition recommendation | `AUT-037`; `KPI-046` | P1 |
| `UAT-R17-010` | **Try to raise a PO for an item already above network maximum, and be refused; then override with a reason** | `BRU-INV-03`(A); `UA-10` | P1 |
| `UAT-R17-011` | Confirm inventory accuracy for the period against a physical count | `KPI-042`; `G2-06` | P1 |
| `UAT-R17-012` | Confirm you can see all locations and that a store keeper cannot see yours | `05-04` §3.3 scope | P2 |

### 3.2 Block B — `R18` Branch Store Keeper · 10 scripts

`SP-016` · `TR-012` · **Bengali** · 51+ people · own branch stock only

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R18-001` | Receive a transfer into the branch, scan it in, and confirm the quantity and value landed | `BRU-INV-02`(H); `UA-23` `UA-24` | **P0** |
| `UAT-R18-002` | Issue a part to a job by scanning the label on the part | `BRU-INV-01`(H); `DT-044`; `UA-23` | **P0** |
| `UAT-R18-003` | **Try to issue a part against an unapproved paid repair, and be refused** | `BRU-SRM-11`(H) `BRU-INV-01`(H) | **P0** |
| `UAT-R18-004` | **Try to issue a part whose shelf life has expired, and be refused** | `BRU-INV-05`(H) | **P0** |
| `UAT-R18-005` | Issue a serialised part and confirm the serial was captured | `BRU-INV-08`(H) | **P0** |
| `UAT-R18-006` | Receive a part returned unused from a technician's van and confirm valuation restored | `AUT-035`; `UA-24` | P1 |
| `UAT-R18-007` | Count your own bin locations and submit the count | `AUT-036`; `UA-23` | P1 |
| `UAT-R18-008` | **Try to see or move another branch's stock, and be refused** | `05-04` §3.3 `(b)`; `NFR-015` | P1 |
| `UAT-R18-009` | Handle a part that scans as incompatible with the device | `MD-022`; `PS-09` | P1 |
| `UAT-R18-010` | Do all of the above in Bengali, on the branch's own scanner and laptop | `PS-03`; `UA-09` `UA-23` | P2 |

### 3.3 Block C — `R19` Procurement Officer · 10 scripts

`SP-017` · `TR-013`

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R19-001` | Take an approved requisition to a transmitted PO and track the vendor's acknowledgement | `AUT-032`; `DT-023` | **P0** |
| `UAT-R19-002` | **Try to issue a PO to an inactive or unapproved vendor, and be refused** | `BRU-SCM-02`(H) | **P0** |
| `UAT-R19-003` | Run an RFQ, receive quotations through `P05`, and award on price, lead time and validity | `DT-022`; `P05` | **P0** |
| `UAT-R19-004` | Confirm a three-way match within tolerance releases the invoice to the payment schedule | `BRU-SCM-01`(H) `AUT-034`; `G3-06` | **P0** |
| `UAT-R19-005` | **Confirm a match outside tolerance is blocked, and see the difference stated** | `BRU-SCM-01`(H); `TS-004` `SIT-E-010` | **P0** |
| `UAT-R19-006` | **Try to raise the PO, receive the goods and approve the invoice yourself, and be refused at the third** | `SOD-02`; `UA-26` | **P0** |
| `UAT-R19-007` | Raise a requisition up to `BDT 500,000`, and **be refused above it** | `05-04` §7 | P1 |
| `UAT-R19-008` | Handle a return to vendor with a debit advice | `DT-025` | P1 |
| `UAT-R19-009` | Confirm landed cost allocated before imported stock is valued as final | `BRU-SCM-04`(C); `UA-24` | P1 |
| `UAT-R19-010` | Review a vendor scorecard and confirm it reflects the delivery and quality events you know occurred | `KPI-048`; `SL-26` | P2 |

### 3.4 Block D — `R15` Logistics Coordinator · 10 scripts

`SP-009` · `TR-020`

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R15-001` | Book a pick-and-drop collection, assign a rider, and see it on their manifest | `M03`; `P09` coordinator view | **P0** |
| `UAT-R15-002` | **Try to close a consignment without proof of delivery, and be refused** | `BRU-LOG-02`(H) | **P0** |
| `UAT-R15-003` | Handle a seal break: confirm an incident is raised automatically and onward movement is blocked | `BRU-LOG-04`(H); `G3-07` | **P0** |
| `UAT-R15-004` | **Try to assign a restricted item to a rider not certified for it, and be refused** | `BRU-LOG-05`(H); `TS-002` `D-10` | **P0** |
| `UAT-R15-005` | Confirm a consignment above the declared-value threshold requires dual signature and insurance flagging | `BRU-LOG-03`(H) | **P0** |
| `UAT-R15-006` | Handle a failed delivery through re-attempt and return to origin with charges applied | `BRU-LOG-08`(C) | P1 |
| `UAT-R15-007` | Confirm logistics charges waived automatically where contract, warranty or Privilege tier entitles it | `BRU-LOG-07`(C); `UA-19` | P1 |
| `UAT-R15-008` | Reconcile cash collected on delivery per rider per shift, **with zero tolerance for unexplained variance** | `BRU-LOG-06`(H) | P1 |
| `UAT-R15-009` | Reassign between an internal rider and a courier partner mid-day | `P09`; `EA-07` | P1 |
| `UAT-R15-010` | Confirm on-time collection and delivery for the period | `KPI-018`; `G3-07` | P2 |

### 3.5 Block E — `R16` Rider / Delivery Agent · 8 scripts

`SP-009` · `TR-020` · **Bengali** · 50–150 people · own manifest only

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R16-001` | Work a manifest: collect, verify items against it, photograph, enter the seal number | `BRU-LOG-01`(H); `UA-23` `UA-25` | **P0** |
| `UAT-R16-002` | **Complete a handover with the customer's OTP and signature — and be unable to complete it without them** | `BRU-LOG-01`(H); `UA-25` | **P0** |
| `UAT-R16-003` | Record a delivery where the recipient is not the customer, with identity verified | `M03`; `UA-25` | **P0** |
| `UAT-R16-004` | Collect cash on delivery and reconcile it at shift end | `BRU-LOG-06`(H) | **P0** |
| `UAT-R16-005` | Record an exception — customer absent, address wrong, refused, damaged — with evidence | `BRU-LOG-08`(C) | **P0** |
| `UAT-R16-006` | **Try to see a consignment not on your manifest, and be refused** | `05-04` §3.1 `(o)`; `EA-07` | P1 |
| `UAT-R16-007` | Issue a collection receipt the customer accepts, in Bengali | `DT-028`; `UA-09` | P1 |
| `UAT-R16-008` | Do the whole manifest on a mid-range Android device, in Bengali | `PS-03`; `NFR-017` | P1 |

> **Offline conditions are in `TS-015`.** `P09` is an offline-capable surface (`PS-08`) and every
> no-signal, queued-sync and conflict case for `R16` is in
> [`TS-015_Offline_and_Field_Condition_Test_Scripts.md`](TS-015_Offline_and_Field_Condition_Test_Scripts.md)
> (`CP-01`).

### 3.6 Block F — `R20` Warehouse Operative · 8 scripts

`SP-018` · `TR-012` · **Bengali** · own location only

| Script | The job | Rules and expected effect | Pri |
|---|---|---|:--:|
| `UAT-R20-001` | Receive, inspect and put away against a GRN | `DT-024`; `AUT-033`; `UA-23` | **P0** |
| `UAT-R20-002` | **Send failing goods to quarantine, and confirm they cannot be issued from there** | `BRU-INV-07`(H) | **P0** |
| `UAT-R20-003` | Pick, pack and dispatch a transfer with a gate pass | `DT-026`; `UA-24` | **P0** |
| `UAT-R20-004` | Perform a bin count and submit it | `AUT-036`; `UA-23` | **P0** |
| `UAT-R20-005` | Handle a hazardous item per its storage and handling rules | `BRU-ESG-04`(H); `KB-013` | P1 |
| `UAT-R20-006` | **Try to act on a location that is not yours, and be refused** | `05-04` §3.3 `(own loc)` | P1 |
| `UAT-R20-007` | Print and apply a compliant part label and confirm it scans | `DT-044`; `UA-23` | P1 |
| `UAT-R20-008` | Do all of the above in Bengali on the warehouse's own hardware | `PS-03`; `UA-09` | P2 |

**Pack total: 58 scripts · 31 at `P0` · 22 at `P1` · 5 at `P2`.**

### 3.7 Negative and edge cases

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | Negative stock attempted at a location | Refused; and refused through the API too (`SL-04`) |
| N-02 | Two storekeepers issue the last unit simultaneously | One succeeds; the other is told the stock is gone, not given a negative balance |
| N-03 | Part scanned that does not exist in `MD-022` | Rejected with a clear next step, never created silently |
| N-04 | Transfer dispatched and the receiving branch never confirms | In-transit ageing report raises it; the value is not lost from both sides |
| N-05 | Count submitted for a location with an open transaction | Count variance excludes the in-flight quantity (`TS-004` `F-07`) |
| N-06 | Rider's device loses the seal-number entry before sync | Queued locally and idempotent on the server (`DI-04`, `AS-13`) — verified in `TS-015` |
| N-07 | Consignment closed by a coordinator instead of the rider | Permitted only with an exception reason; the custody record shows who closed it |
| N-08 | Label prints but does not scan on the branch's scanner | `DT-044` defect, not a training issue (`UA-23`) |
| N-09 | Vendor invoice arrives before the goods | Held; three-way match not partially satisfied (`BRU-SCM-01`) |

### 3.8 Bilingual check

**Bilingual pack.** Bengali is the execution language for `R18`, `R16` and `R20` — 116–231 of the
135–274 people in scope. All 31 `P0` scripts are executed in Bengali by a Bengali-reading executor
(`UA-09`).

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| Inventory and Procurement console labels (`UI-027`, `UI-028`), `P05` (`UI-015`) and `P09` rider labels (`UI-019`) | ● | ● | ● on a 5-inch device |
| Offline and sync state copy encountered (`UI-009`) | ● | ● | ● |
| Part and UoM names (`MD-022`, `MD-023`) | ● | ● | ● |
| Delivery challan, POD and gate pass as printed (`DT-026`, `DT-027`, `DT-028`) | ● | ● | ● |
| Reason codes for exceptions (`MD-026`) | ● | ● | ● |
| Hazard warnings on restricted items | ● | ● | **● — a truncated hazard warning is a safety defect, not a layout defect** |

---

## 4. Exit Criteria

`TS-006` §4 applies. Additional:

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100%** |
| `P1` scripts passed | ≥ 98% |
| Scripts executed against **physical** goods where `UA-23` requires it | 100%; simulations recorded and excluded |
| Quantity-location-value assertions | 100% of stock scripts (`UA-24`) |
| Custody scripts with both parties and all four capture elements | 100% (`UA-25`) |
| SoD refusals (`SOD-02`, `SOD-05`) | 2 of 2 blocked, with two distinct users |
| **`G2-06` inventory accuracy at migrated locations** | **≥ 95%, verified by count** |
| **`G2-07` van-stock variance** | **< 2%, daily reconciliation** |
| **`G3-07` chain-of-custody exceptions** | **Zero** |
| Bengali execution of the `P0` set | 100% (`UA-09`) |
| Roles with a signature | 6 of 6 |
| Open Critical defects | Zero |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Automatic escalation:** any defect that allows **stock to move without a corresponding valuation
effect**, or **custody to transfer without both parties recorded**, is **Critical**, to the CFO and
the Operations Director. Both are cumulative and neither is self-announcing — `KPI-019` sets
chain-of-custody exceptions at zero, which means the first one is the finding.

---

## 6. Sign-off

| Role | Super-user name | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|
| `R17` Inventory Manager | | | | | |
| `R18` Branch Store Keeper | | | | | |
| `R19` Procurement Officer | | | | | |
| `R15` Logistics Coordinator | | | | | |
| `R16` Rider / Delivery Agent | | | | | |
| `R20` Warehouse Operative | | | | | |
| **Pack acceptance** — Inventory Manager | | | | | |
| **Counter-signature** — Finance Manager (valuation effects) | | | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack is registered at W3 and two of its exit criteria are W2 gate criteria.** `06-02` `G2-06` (inventory accuracy ≥ 95% verified by count) and `G2-07` (van-stock variance < 2%) fall at Month 8; `G3-06`/`G3-07` fall at Month 13. **The `R17` and `R18` blocks are consumed a wave before the pack exists** — the same shape as `TS-003` `O-01`, `TS-005` `O-01` and `TS-006` `O-01` | Programme Content Lead with QA Lead | **W2 — register correction** |
| **O-02** | **`UA-23` requires physical goods, hardware and a vehicle, and nothing allocates them.** Forty labelled parts across three locations, a serialised part, an expired-shelf-life part, a hazardous item, the branch's own scanner and label printer, and a vehicle for the custody scripts. `TS-006` `O-04` records the same gap for counter hardware; **this pack cannot be executed at all without it** | Programme Manager with Inventory Manager | **W2** |
| **O-03** | **`UA-25` requires a real second party.** Custody scripts need a customer or a counterparty, not a colleague standing in — `BRU-LOG-01` captures identity from *both* parties, and a colleague's identity proves the field accepts input. Whether a pilot-branch customer can be asked to participate is a decision nobody has taken | Logistics Manager with Legal Counsel | **W3** |
| **O-04** | **`R18` is a 51+-headcount Bengali-first role and the Bengali counterpart of this pack must exist before the cycle** (`UA-04`, `UA-09`). Bengali authoring is unresourced — `TS-002` `O-06`, `TS-006` `O-03` | Localisation Lead | **W2** |
| **O-05** | **`DM-007` inventory and parts mapping workbook is unwritten** (Category 12 unstarted), so precondition 9 — a signed opening-stock control total — has no derivation. `G2-06` measures accuracy *against* an opening position; **without it, "95% accurate" has no denominator**, which is the same defect `TS-001` `O-04` records for requirements | Data Migration Lead with Inventory Manager | **W2 — before `G2`** |
| **O-06** | **`MD-022` part compatibility and `DT-044` label, barcode and QR formats are cited by `UAT-R18-009`, `UAT-R20-007` and `N-08`, and no pack verifies that a printed label scans on the scanner models the 51+ branches actually own.** No hardware inventory exists to test against | IT Administrator (`R33`) with Inventory Manager | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **Method taken by reference from `TS-006` and `TS-007` rather than restated (`CP-01`)**
- [x] Four additional rules stated, all binding physical verification into the script
- [x] **The screen-only versus physical distinction stated, and traced to `G2-06`'s "verified by count"**
- [x] 58 scripts enumerated across 6 roles with rules, expected effect and priority
- [x] Role coverage reconciles to `05-04` §1.3 headcounts, with data scope per role
- [x] Every `SP` and `TR` identifier verified against the files on disk
- [x] Offline conditions deliberately excluded and delegated to `TS-015` (`CP-01`)
- [x] Nine supply-chain edge cases stated, including concurrent last-unit issue and invoice-before-goods
- [x] **Bilingual status justified by headcount — 116–231 of 135–274 people are Bengali-first**
- [x] Truncated hazard warning classified as a safety defect rather than a layout defect
- [x] Automatic Critical escalation for value-less stock movement and single-party custody
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 58 per-step grids — outstanding**
- [ ] **`O-01` W2 gate criteria against a W3 pack — outstanding**
- [ ] **`O-02` no physical goods or hardware allocated — outstanding; the pack is unexecutable without it**
- [ ] **`O-05` no signed opening-stock position — outstanding; `G2-06` has no denominator**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending QA Lead and Inventory Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
