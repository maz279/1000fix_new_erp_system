---
id: DM-007
title: Field Mapping Workbook — Inventory and Parts
project: 1000FiX ERP System v2.0
content_type: Master data specification
template: TPL_Master_Data_Specification.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with Inventory
author: Data Migration analysts with the Warehouse Manager
reviewers: [Warehouse Manager, Procurement Manager, CFO, Branch Operations Lead, Master Data Owner, QA Lead]
approver: Warehouse Manager with CFO
content_class: C
purpose: >
  Maps the cutover physical count, brand consignment confirmations, open returns and open purchase
  commitments to the ERP inventory model, and states explicitly that the 51-plus branch stock
  spreadsheets are not the source of opening balances. Opening stock that does not reconcile to the
  general ledger blocks financial go-live, and opening stock loaded from a 75-per-cent-accurate
  spreadsheet guarantees that inventory accuracy never recovers, because every later variance is
  contaminated by an unknown opening error.
traces_to: [M15, M41, M16, M42, M44, M37, M43, M19, MD-022, MD-019, MD-023, MD-004, MD-017, DM-001, DM-002, DM-003, DM-008, DM-011, DM-013, DM-014]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
data_file: DM-007_Field_Mapping_Inventory_and_Parts.xlsx
effective_dated: no
sources:
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15 §16.4 — migration position non-negotiable; opening balances established by a full physical count at cutover, not by loading the spreadsheets, which are 75% accurate; 51+ locations counted, van stock recalled and counted, consignment balances confirmed with each brand inside the cutover window
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 §Gate 2 — G2-06 inventory accuracy ≥ 95% at migrated locations, verified by count; G2-07 van stock reconciling daily with variance < 2%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M16 §16.4 and M41 §16.4 and M43 §16.4 — open POs current only; bin master authored and bin-level opening positions counted; pre-ERP consumption records explicitly not migrated into the demand series
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md §2 — part_code, manufacturer_part_no, part_class, is_consignment, hazard_class, uom_code
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.3 — inventory accuracy baseline ~75% against a 95–99% benchmark; §6.2 process 6 van stock entirely untracked
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-007 — Field Mapping Workbook: Inventory and Parts

> Governs `DM-007_Field_Mapping_Inventory_and_Parts.xlsx`. The markdown governs; the workbook loads.
>
> **Template conformance note.** As `DM-004`: `TPL_Master_Data_Specification.md` retained in full;
> the `CG-009` source-to-target column set is inherited from `DM-004` §2.1 (`CP-01`).
>
> **Identifier note (`CG-005` §3.3).** `DM-007` is a **content** identifier; `05-02` `DM-07`
> (modelling standard — monetary fields) is cited with its document prefix.

---

## 1. Purpose and ownership

| Item | Value |
|---|---|
| Data domain | Inventory, spare parts and purchase commitment |
| Owning module | `M15` INV; `M41` WMS; `M16` PRO for open commitments |
| Data steward | Warehouse Manager |
| Golden source | **The signed cutover count sheet** — not `SRC-006` or `SRC-007` |
| Refresh cadence | Once per wave at cutover; cycle counting thereafter (`M15`) |
| Environments | Dev · SIT · UAT · Prod |
| Content class | C — Operational-critical |
| Effective-dated | no |
| **Build wave** | **W1** *(the register wave — `MS-22`)* |
| **Load wave** | **W2** — `M15` §16.4 cutover, `06-01` W2; warehouse bins **W3** (`M41`); open POs **W3** (`M16`) |

**Consequence of absence (`CP-03`).** `M15` §16.4 records the programme's clearest migration
position and this workbook exists to implement it:

> *"**Migration position — non-negotiable.** Opening balances are established by a **full physical
> count at cutover**, not by loading the spreadsheets. The spreadsheets are 75% accurate; loading
> them guarantees that inventory accuracy never recovers, because every subsequent variance is
> contaminated by an unknown opening error."*

**The mapping in this file is therefore mostly a mapping from a count sheet, not from a system.**
That is unusual, and it is the whole point. `G2-06` requires **inventory accuracy ≥ 95% at migrated
locations, verified by count** against a `~75%` baseline (BRD §6.3). An opening balance taken from
the 75%-accurate source makes that gate unmeasurable rather than merely unmet.

Without this file:

| Failure | Consequence |
|---|---|
| Branch spreadsheets loaded as opening stock | `G2-06` is permanently unverifiable; every future variance is unattributable |
| Van stock omitted | 200–400 vans hold *"entirely untracked"* stock (BRD §6.2). Omitting it makes the first van reconciliation a 100% variance |
| Consignment stock loaded as owned | **Brand-owned inventory recorded as a company asset** — a balance-sheet misstatement and a brand dispute |
| Opening value not reconciled to the GL | `G3-08` and the `M19` stock control account fail at W3 |
| Reserved and in-transit quantities loaded as free stock | Availability lookups over-promise from day one |
| Open POs omitted | Goods arrive against a commitment the system has no record of; three-way match cannot function |

---

## 2. Record structure

Target structures are `05-02` §5 (`M15` — 17 entities) and `MD-022` §2 for the part master. Not
restated (`CP-01`). Mapping column set: `DM-004` §2.1.

### 2.1 What is counted, what is confirmed, what is extracted

**`IV-01`: every inventory figure entering the system at cutover carries an `origin`, and the
`origin` determines who signs it.**

| `origin` | Population | Evidence | Signed by |
|---|---|---|---|
| **`counted`** | Stock on hand at 51+ branches, central warehouse, workshop | Count sheet, two counters, variance sheet | Branch manager **and** Warehouse Manager |
| **`counted_van`** | Van stock, after **recall** of the van | Van count sheet | Technician **and** branch manager |
| **`brand_confirmed`** | Consignment balances per brand | **The brand's own written confirmation** | Brand partner **and** Finance Director |
| **`extracted`** | Open RTVs, open POs, open credits, supplier price lists | Source extract plus profiling report | Procurement Manager |
| **`authored`** | Bin master, initial slotting, replenishment parameters | Design document | Warehouse Manager |
| **`derived`** | Historical consumption *(warehouse only)* | Best-effort extract | Warehouse Manager, **advisory only** |

> **`IV-02`.** The branch spreadsheets (`SRC-006`, `SRC-007`) are **never** an `origin`. They may be
> used as a **count-preparation aid** — a pick list telling counters where to look — and as a
> post-count variance comparison that quantifies the opening error for the record. They are not
> loaded.

> **`IV-03` — the variance is a deliverable.** Counting against the spreadsheets produces, for the
> first time, a measured figure for how wrong the old estate was. `M15` and BRD §6.3 both assert
> ~75%; nobody has measured it. The variance report is filed with the reconciliation (`DM-013`) and
> is the baseline `RP-016` data-quality scorecard starts from.

### 2.2 Map A — `fix.stock.quant` opening positions

| Source field *(count sheet)* | Target | Transform | Note |
|---|---|---|---|
| `Part Code` / OEM number written by the counter | `product_id` → `fix.part` | `I-01` — resolve against `MD-022` `part_code` then `manufacturer_part_no` then cross-reference | **Unresolved → quarantine location, not rejection.** See `IV-04` |
| `Location` / branch, store, bin | `location_id` | `T-05` → `MD-004` warehouse/storage locations; bins only where `M41` is enabled (W3) | |
| `Counted Qty` | `quantity` | Integer or decimal per `MD-023` UoM; **the counted number, never an adjusted one** | |
| `UoM` | *(validation)* | Must equal `MD-022` `uom_code` for the part; a mismatch is a **count error**, escalated | Piece / metre / litre confusion is common |
| `Condition` | `lot_id` / quality state | `T-05` — good / damaged / expired / quarantine | Damaged stock is **not** free stock |
| `Batch` / `Lot` | `lot_id` | Where the part is lot-tracked | |
| `Ownership` | `owner_party_id` | **`IV-05`** — company or brand. Consignment is brand-owned | |
| `Count Date/Time` | `inventory_date` | Exact `Asia/Dhaka` instant, matching the freeze window (`DM-014`) | |
| `Counter 1` / `Counter 2` | Count evidence document | Both names recorded; a single-counter sheet is not accepted for high-value classes | |
| *(computed)* | `unit_cost` / valuation | **§2.5 — not supplied by the count** | |
| *(control)* | `legacy_source_system`, `legacy_record_id`, `migration_batch_id` | `MS-18` — for counts, `legacy_record_id` is the count-sheet line reference | |

> **`IV-04` — the quarantine rule.** A counted item whose part cannot be resolved is **real physical
> stock**; rejecting it means the system says the shelf is empty when it is not. It loads to a
> `MIGRATION-QUARANTINE` location with its written description verbatim, and clears through the
> `M64` stewardship queue. This is the inverse of the customer-data rule, and the reason is that a
> customer record with no key is unusable, whereas a part with no key is still on the shelf.

> **`IV-05` — consignment ownership.** `MD-022` carries `is_consignment` and `brand_code`. A
> consignment part counted at a branch loads with the **brand as owner**, into a consignment
> location, and is excluded from company stock valuation. `M15` requires the balance to be
> *brand-confirmed*; where the brand's confirmation and the count disagree, **neither is loaded
> until reconciled** — the difference is a commercial exposure, not a data-entry variance.

### 2.3 Map B — van stock

| Rule | Detail |
|---|---|
| **`IV-06`** | Van stock is established by **recalling the van and counting it**, not by asking the technician what is on board |
| Target | `fix.van.stock` at a van-class `fix.stock.location`, one per technician vehicle |
| Volume | 200–400 vans, *"unrecorded today"* (`M15` §16.4) |
| Gate | `G2-07` requires van stock reconciling **daily** with variance < 2%. That is unachievable from an unmeasured opening position |
| Consequence if skipped | The first daily reconciliation shows a 100% variance and the control is abandoned in week one |
| Scheduling | Vans cannot all be recalled at once without stopping field service. `DM-014` must sequence van recall across the cutover window by zone |

### 2.4 Map C — open commitments and returns

| Target | Source | Rule | Wave |
|---|---|---|:--:|
| `fix.stock.rtv` | Open RTVs and pending credits | **Current only.** Each carries its original supplier reference and the credit expected | W2 (`M15`), W3 (`M16`) |
| `purchase.order` (ext) | Open purchase orders | **Current only, ~150–400 lines.** Each line carries ordered, received and outstanding quantities — an order without its receipt history cannot three-way match | W3 |
| `fix.approved.source` | Supplier price lists | 40–120 suppliers; party resolved through `DM-004` | W3 |
| `fix.purchase.price.history` | Historical purchase prices | 24 months **where recoverable**, best-effort | W3 |
| `fix.consignment.balance` | Brand consignment records | `brand_confirmed` only (`IV-05`) | W2 |
| `fix.letter.of.credit`, `fix.import.consignment` | Open LCs and in-flight imports | Current only, 5–20 LCs | W6 |
| `fix.stock.reservation` | — | **Not migrated.** No source records reservations; reservations begin at go-live | — |
| `fix.cycle.count`, `fix.count.variance` | **The cutover count itself** | The cutover count is loaded as the **first cycle count**, so that the variance history begins with an honest, signed measurement | W2 |

### 2.5 Valuation — and the two-wave problem

| Rule | Detail |
|---|---|
| **`IV-07`** | The count establishes **quantity**. Valuation is applied separately, from an agreed basis, and is a **Finance** decision |
| Valuation basis | Weighted average cost at cutover, from the last known purchase price per part; parts with no recoverable price are valued at a Finance-approved deemed cost |
| Currency | Explicit `BDT` on every value (`05-02` `DM-07`, `MD-039`) |
| Landed cost | Imported parts carry landed cost where `M44` data exists; otherwise purchase price, flagged |
| **The problem** | **Stock loads at W2. The general ledger loads at W3.** There is no stock control account to reconcile to at the moment the stock is counted |
| **`IV-08` — the resolution** | The W2 opening stock value is computed, **signed by the Warehouse Manager and the CFO**, and **frozen**. At W3 the `M19` opening trial balance must carry that exact figure as the stock control account balance. A difference at W3 is a **finance reconciliation exception**, never a silent restatement of the W2 count |

> Without `IV-08`, the W3 trial balance simply adopts whatever the system holds, and the count's
> evidentiary value — the thing the entire non-negotiable position was defending — is lost at the
> first close.

### 2.6 What is not migrated, and why

| Not migrated | Reason | Source |
|---|---|---|
| Branch stock spreadsheet balances | 75% accurate; loading them destroys the accuracy baseline | `M15` §16.4 |
| **Pre-ERP consumption history into the demand series** | *"produced by a 75%-accurate inventory process and would contaminate the very history the readiness gate exists to protect"* | `M43` §16.4 — **non-negotiable** |
| Requisition, RFQ and match history | None exists | `M16` §16.4 |
| Warehouse execution data | None exists; the bin master is **authored** | `M41` §16.4 |
| Supplier delivery and quality performance | Not recorded; scorecards start from `M16` go-live and first publish at end of W4 | `M42` §16.4 |
| Stock reservations | No source | — |

> **`IV-09`.** Historical consumption **may** be loaded into the warehouse (`M62`) as a separate,
> clearly labelled reference set for human comparison, 24 months where recoverable. It is **never**
> an input to a forecast (`M43`). The two statements are not in tension and both must be
> implemented, or the labelled reference set will be picked up by the first person who needs a
> baseline.

---

## 3. Keys and identifiers

| Item | Rule |
|---|---|
| Natural key | `part_code` + `location_id` + `lot_id` + `owner_party_id` |
| Part resolution order | `MD-022` `part_code` → `manufacturer_part_no` → brand cross-reference → **quarantine** (`IV-04`) |
| Surrogate key | System-generated quant id |
| Legacy key | Count-sheet line reference; for extracted rows, the source document number |
| Reuse policy | Count sheets are never re-used or re-signed; a recount produces a new sheet with a new reference |
| Uniqueness | One quant per part × location × lot × owner. A second count of the same cell is a **recount**, and only the latest signed recount loads |

---

## 4. Validation rules

> Class: **H** hard (blocks) · **A** approved override · **S** soft (warns) · **C** computed
> (`05-05` §1). Every message ID resolves in `UI-004`.

| # | Rule | Class | Message ID |
|---|---|:--:|---|
| `IV-01` | Every opening figure carries an `origin` and the signature that `origin` requires | **H** | `ERR-INV-001` |
| `IV-02` | Branch stock spreadsheets may not be an `origin` for any opening balance | **H** | `ERR-INV-002` |
| `IV-03` | The count-versus-spreadsheet variance report is produced and filed with the reconciliation | **H** | `ERR-INV-003` |
| `IV-04` | An unresolvable counted part loads to quarantine; it is never dropped | **H** | `ERR-INV-004` |
| `IV-05` | Consignment stock loads brand-owned, excluded from company valuation; an unreconciled brand difference blocks the load | **H** | `ERR-INV-005` |
| `IV-06` | Van stock loads only from a recall-and-count sheet | **H** | `ERR-INV-006` |
| `IV-07` | Valuation is applied separately from quantity, on a Finance-approved basis, with explicit currency | **H** | `ERR-INV-007` |
| `IV-08` | The W2 opening stock value is frozen and must appear unchanged in the W3 opening trial balance | **H** | `ERR-INV-008` |
| `IV-09` | Historical consumption never enters the demand series; a labelled warehouse reference set is permitted | **H** | `ERR-INV-009` |
| `IV-10` | A UoM mismatch between the count sheet and `MD-022` is a count error and is escalated, never coerced | **H** | `ERR-INV-010` |
| `IV-11` | Damaged, expired and quarantined stock loads to a non-available state; it is never free stock | **H** | `ERR-INV-011` |
| `IV-12` | An open PO line loads with ordered, received and outstanding quantities, or it does not load | **H** | `ERR-INV-012` |
| `IV-13` | High-value classes require two named counters on the sheet | **H** | `ERR-INV-013` |
| `IV-14` | The count instant matches the declared freeze window (`DM-014`); a count taken outside it is void | **H** | `ERR-INV-014` |
| `IV-15` | The cutover count loads as the first cycle count, establishing the variance history | **C** | `WRN-INV-015` |
| `IV-16` | Bin-level positions load only at `M41`-enabled sites, after the bin master is authored | **H** | `ERR-INV-016` |
| `IV-17` | Profiling reported and accepted for every `extracted` origin before load (`MS-04`) | **H** | `ERR-INV-017` |
| `IV-18` | Every loaded row carries the three control values (`MS-18`) | **H** | `ERR-INV-018` |

---

## 5. Relationships and load dependencies

| Depends on | Cardinality | Load order |
|---|---|---|
| `MD-022` part catalogue, `MD-019` item catalogue, `MD-023` UoM | N:1 | Seed tier 5, **before** — `I-01` cannot resolve without them |
| `MD-004` warehouse and storage locations, `MD-003` branch | N:1 | Seed tier 2, before |
| `MD-017` brand register | N:1 | Seed tier 7 — consignment ownership |
| `DM-004` party | N:1 | Tier `X1` — suppliers and brands as parties |
| `DM-005` asset | — | Independent; van locations relate to `MD-045` fleet |
| **The signed count sheets** | 1:1 | **The count must be complete and signed before the load starts** (`IV-01`) |

| Depended on by |
|---|
| `DM-008` stock control account at W3 (`IV-08`) · `M43` replenishment parameters *(from live consumption only)* · `M41` bin occupancy · `G2-06`, `G2-07`, `G3-08` |

---

## 6. Source of truth and acquisition

| Item | Value |
|---|---|
| Where it comes from | **The cutover physical count** · brand written confirmations · `SRC-016` supplier records · open PO files |
| Who supplies it | Warehouse Manager (count) · Finance Director (brand confirmations) · Procurement Manager (commitments) |
| Collection method | **Physical count and van recall** · written brand confirmation · document extract |
| Known quality issues | Baseline inventory accuracy ~75%; van stock entirely untracked; consignment balances held **by each brand**, not by 1000FiX; part identity written by hand on count sheets; UoM confusion |
| Cleansing rules applied | `DM-011` |
| Re-verification | Cycle counting from go-live (`M15`); `RP-016` scorecard |

---

## 7. Volumes

| Population | Rows | Origin | Wave |
|---|---:|---|:--:|
| Branch stock positions | **~10,000 SKUs × up to 51 locations** | `counted` | W2 |
| Central warehouse | ~10,000 SKUs | `counted` | W2 |
| **Van stock** | **200–400 vans** | `counted_van` | W2 |
| Brand consignment balances | 17+ brands | `brand_confirmed` | W2 |
| Open RTVs and credits | Current only | `extracted` | W2–W3 |
| Open purchase orders | ~150–400 lines | `extracted` | W3 |
| Supplier price lists | 40–120 suppliers | `extracted` | W3 |
| Warehouse bins | ~6,000 at W3, ~20,000 at full build | `authored` | W3 |
| Initial slotting | ~10,000 parts × enabled warehouses | `authored` | W3 |
| Historical consumption *(warehouse only)* | 24 months where recoverable | `derived` | W2–W3 |
| Open LCs and in-flight imports | 5–20 | `extracted` | W6 |

> **The count is the constraint, not the load.** Counting 10,000 SKUs across 51 locations, recalling
> and counting 200–400 vans, and obtaining 17+ brand confirmations **inside a cutover window** is
> the single largest operational commitment `M15` asks of the business. `DM-014` must sequence it;
> this workbook only says what a completed count must contain.

---

## 8. Change control

| Item | Value |
|---|---|
| Who may add a mapping row | Migration analyst |
| Who may set `business_confirmed` | Warehouse Manager; Procurement Manager for commitments |
| Who may set `signed_off` | Warehouse Manager with CFO |
| Approval required | **CFO for the valuation basis and any deemed cost**; Finance Director for consignment treatment; Warehouse Manager for count procedure changes |
| Effective dating | Not effective-dated; the count instant is the effective moment |
| Archive rule | Records archived (`active = FALSE`), never deleted (`05-02` `DM-06`) |
| Logged in | `RF-006`; count sheets retained as `M24` documents with the reconciliation |

---

## 9. Sample rows

```csv
map_id,source_id,source_field,source_type,source_example,target_entity,target_field,transform_rule,default_value,required_at_target,sensitivity,residency_restricted,dq_rule,unmapped_disposition,owner,status
IMAP-000401,COUNT,Part Code,text,PRT-004182,fix.stock.quant,product_id,I-01 resolve MD-022 part_code then manufacturer_part_no then brand cross-reference; unresolved loads to MIGRATION-QUARANTINE per IV-04,,TRUE,S1,FALSE,DQ-INV-001,,Warehouse Manager,proposed
IMAP-000404,COUNT,Counted Qty,decimal,37,fix.stock.quant,quantity,The counted number verbatim; never adjusted to agree with the spreadsheet,,TRUE,S1,FALSE,DQ-INV-004,,Warehouse Manager,proposed
IMAP-000408,COUNT,Ownership,enum,BRAND-SAMSUNG,fix.stock.quant,owner_party_id,IV-05 consignment loads brand-owned into a consignment location and is excluded from company valuation,COMPANY,TRUE,S1,FALSE,DQ-INV-008,,Finance Director,proposed
IMAP-000412,SRC-006,Spreadsheet Qty,decimal,44,,,IV-02 not an origin; used only as a count-preparation aid and for the IV-03 variance report,,FALSE,S1,FALSE,,carried_to_legacy_payload,Warehouse Manager,proposed
IMAP-000420,SRC-016,PO Outstanding Qty,decimal,12,purchase.order.line,product_qty_outstanding,IV-12 ordered received and outstanding all required or the line does not load,,TRUE,S1,FALSE,DQ-INV-020,,Procurement Manager,proposed
```

---

## 10. Migration notes

**This workbook carries two wave gates directly.**

| Gate | Criterion | How this workbook serves it |
|---|---|---|
| `G2-06` | Inventory accuracy ≥ 95% at migrated locations, **verified by count** | The opening position *is* the count (`IV-01`, `IV-02`), so the first accuracy measurement is honest |
| `G2-07` | Van stock reconciling daily with variance < 2% | `IV-06` gives the daily reconciliation a real starting point |
| `G3-08` *(shared with `DM-008`)* | Financial history migrated and reconciled to the trial balance | `IV-08` freezes the W2 stock value so W3 has something to tie to |

**The 75% figure should be verified, not repeated.** `M15` §16.4 and BRD §6.3 both assert ~75%
accuracy; neither cites a measurement. `IV-03` turns the cutover count into that measurement. Under
`CG-012` `EV-05`, a quantitative claim about the business cites its system of record — and here
there is none, which is itself the finding.

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Part resolution, consignment flag, hazard class, UoM |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-023_Unit_of_Measure_and_Packaging_Register.md) | The UoM every count line validates against |
| [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) | The stock control account `IV-08` freezes a value for |
| [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | The freeze window the count instant must fall inside |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The variance report and the signed reconciliation |
| `M15` §16.4 · `M41` §16.4 · `M43` §16.4 · `M16` §16.4 | The migration positions implemented here |
| `RP-016` Data Quality Scorecard | Starts from the `IV-03` variance baseline |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-18 | Initial issue. Six origins with their signing authority, spreadsheets excluded as an origin, quarantine rule for unresolvable counted stock, consignment ownership separated, the W2/W3 valuation freeze introduced | Warehouse Manager (pending) |

---

## 13. Open items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The cutover count is not scheduled or resourced.** 51+ locations, 200–400 van recalls and 17+ brand confirmations inside one window, without stopping field service. `M15` calls it *"the single largest operational commitment M15 asks of the business"*; no plan exists | Warehouse Manager with Programme Director | **W2 minus 3 months** |
| **`O-02`** | **The valuation basis is not approved.** `IV-07` requires a Finance-approved basis and a deemed-cost rule for parts with no recoverable price. Neither exists, and the W2 stock value cannot be frozen (`IV-08`) without them | CFO | **W2 minus 1 month** |
| **`O-03`** | **`MD-022` coverage against the counted estate is unmeasured.** ~18,000 legacy parts rows with an estimated 30–40% duplication (`M37` §16.4) resolve into a catalogue whose completeness is unknown. The quarantine population could be large | Master Data Owner with Warehouse Manager | **W2 minus 2 months** |
| **`O-04`** | **Brand consignment confirmation has no agreed process.** `IV-05` blocks the load on an unreconciled difference; obtaining 17+ written confirmations inside the cutover window has no owner and no lead time | Finance Director | **W2 minus 2 months** |
| **`O-05`** | **`M37` catalogue migration has no workbook** (`DM-001` `O-05`). This workbook maps *stock against parts*; the ~18,000-row part catalogue itself is a `M37` W1 migration nobody owns in Category 12 | Programme Content Lead with CCO | **W1** |
| **`O-06`** | Van recall sequencing conflicts with field service continuity. `DM-014` must sequence by zone; the operational impact of taking 200–400 technicians off the road, even in waves, has not been assessed | Service Ops Director with Warehouse Manager | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Master_Data_Specification.md`; mapping column set inherited from `DM-004` §2.1 (`CP-01`)
- [x] **`M15`'s non-negotiable position implemented literally** — spreadsheets excluded as an origin (`IV-02`)
- [x] Six origins defined, each with the signature it requires (`IV-01`)
- [x] The count-versus-spreadsheet variance made a deliverable rather than a by-product (`IV-03`)
- [x] Quarantine rule for unresolvable counted stock, with the reasoning contrasted against the customer-data rule
- [x] Consignment ownership separated from company stock, with the unreconciled-difference block
- [x] Van stock made a recall-and-count, bound to `G2-07`
- [x] **The W2 stock / W3 ledger two-wave problem identified and resolved by a frozen, signed value** (`IV-08`)
- [x] Everything not migrated listed with its reason, including the `M43` non-negotiable
- [x] The labelled-reference-set loophole closed (`IV-09`)
- [x] Volumes stated, with the count identified as the constraint
- [x] Sample rows included and parse as CSV
- [x] Archive rule states records are archived, never deleted (`05-02` `DM-06`)
- [x] The unmeasured 75% claim flagged under `CG-012` `EV-05` rather than repeated as fact
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` the cutover count is unscheduled and unresourced**
- [ ] **`O-02` valuation basis unapproved — `IV-08` cannot execute**
- [ ] Named approver recorded — **pending Warehouse Manager with CFO**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
