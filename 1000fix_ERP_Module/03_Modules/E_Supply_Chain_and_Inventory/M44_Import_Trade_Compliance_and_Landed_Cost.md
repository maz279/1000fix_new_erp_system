---
id: FIX-ERP2-M44
module_id: M44
module_code: ITC
module_name: Import, Trade Compliance & Landed Cost
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Procurement Manager
system_owner: Supply Chain Squad
priority: P2
wave: W6
---

# M44 — Import, Trade Compliance & Landed Cost
### Category E · Code `ITC` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M44 |
| **Module code** | `ITC` |
| **Category** | E — Supply Chain & Inventory |
| **Status** | ★ **New** — split out of M16 after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | **W6** (Months 23–26) |
| **Business owner** | Procurement Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo `stock_landed_costs` · L2 OCA `purchase_landed_cost` · L5 custom import lifecycle, trade compliance, duty engine and cost allocator |
| **Custom modules** | `cd_import_order`, `cd_trade_compliance`, `cd_customs_clearance`, `cd_landed_cost` |
| **Requirement range** | FR-ITC-001 … FR-ITC-036 |
| **Requirement count** | **36** *(measured — supersedes the 28 estimate in `02-02`)* |
| **Effort estimate** | **19 person-weeks** *(measured — supersedes the 15 PW estimate)* |
| **Depends on** | M16 Procurement · M42 Supplier Relationship · M15 Inventory · M41 Warehouse · M50 Treasury · M51 Tax & Regulatory Compliance · M52 Accounts Payable · M19 Financial Accounting · M24 Documents |
| **Depended on by** | M15, M16, M41, M43, M19, M51, M52, M54, M11, M25 |

---

## 2. Purpose

M44 owns **everything that happens to a purchase between the supplier's warehouse abroad and
the moment the part is valued correctly in 1000FiX's books**.

A motherboard bought from a supplier in Shenzhen at USD 82 does not cost BDT 9,800. It costs
that plus ocean or air freight, plus insurance, plus a 1% landing charge, plus customs duty,
plus regulatory duty, plus supplementary duty where applicable, plus the C&F agent's fee, plus
port and demurrage charges, plus LC opening commission and bank charges, plus inland transport
from Chittagong to Dhaka. Depending on the HS classification, the true landed cost can be
**25–60% above the invoice price**.

Today none of that reaches the unit cost of the part. The invoice price is what the system
knows, and every margin calculated on an imported part is therefore overstated. The Company is
selling some repairs at a loss and does not know which ones.

M44 also owns the **compliance** half of the problem, which is not optional. Importing into
Bangladesh means an Import Registration Certificate, an LCA form lodged with an authorised
dealer bank, a letter of credit or an approved alternative payment route under Bangladesh Bank's
Foreign Exchange Guidelines, correct HS classification, a Bill of Entry filed through ASYCUDA
World, and a document set that must be retained and must reconcile. Getting it wrong produces
detained cargo, demurrage, penalties and — at the extreme — loss of import privileges.

### Why It Exists

**Margin truth.** Landed cost is the single largest source of hidden margin error in an
after-sales business that imports its parts. The category overview records it as a high-impact
risk: *"Import duty and clearing costs never reach unit cost — margins overstated on imported
parts."*

**Cash and lead time.** An LC ties up cash or credit line for weeks before goods ship. Import
lead time and its variability are the dominant term in M43's reorder-point calculation for the
imported base. Neither is currently measured.

**Compliance exposure.** A misclassified HS code is a customs dispute; a lapsed IRC is a
stopped supply chain; an unreconciled LCA form is a regulatory finding at the bank. These are
low-frequency, high-consequence events, and they are currently managed entirely in the head of
whoever deals with the C&F agent.

**It is a distinct discipline.** M16 knows how to place an order and match an invoice. It has
no business knowing what a Bill of Entry is. Separating M44 keeps M16 simple and gives the
import process the specialised model it needs.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §2 | M44 "owns cross-border supply: proforma, LC, shipment, customs, duty, clearing, true landed cost" |
| `_CATEGORY_OVERVIEW.md` §6 | "Import documentation, LC, customs → M44, not M16" and "Landed cost calculation → M44; M15 receives the value, M19 posts it" |
| `_CATEGORY_OVERVIEW.md` §7 | Targets: **import clearance cycle time −20%** against baseline; **landed cost accuracy within 2%** of actual |
| `_CATEGORY_OVERVIEW.md` §9 | Risk: "Import duty and clearing costs never reach unit cost — margins overstated on imported parts." Mitigation: "Landed cost allocation is mandatory before stock is valued as final" |
| ERP BRD BR-INV-011 | "FIFO and weighted average stock valuation methods" — both require a correct unit cost to be meaningful |
| ERP BRD BR-SCM-005 | "3-way matching: PO + GRN + Vendor Invoice" — the supplier invoice is only one of several cost documents on an import |
| Company Profile §Authorized Service Partnerships | Genuine OEM parts for 17+ brands are predominantly imported, often from brand-designated sources |
| `02-05` §8.3 | Foreign-currency exposure and rate handling are already recognised in the technology stack |
| Bangladesh Bank Foreign Exchange Guidelines, Vol. 1, Ch. 7 §II | Letters of credit and remittances against imports; LCA forms retained by authorised dealers for five years |
| NBR / Bangladesh Customs | Bill of Entry filed through **ASYCUDA World** in Single Administrative Document format; an L/C is required for release of goods for all types of imports |

---

## 3. Scope Boundary

> **The rule:** M16 owns the *commercial* transaction — what we agreed to buy, from whom, at
> what price. M44 owns the *cross-border execution and the true cost* — how it gets here, what
> it costs to get here, and what the law requires along the way.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Import order lifecycle from confirmed cross-border purchase order to costed, released stock |
| 2 | Proforma invoice management and its reconciliation to the purchase order |
| 3 | Incoterm modelling and the cost and risk responsibilities each implies |
| 4 | **HS code classification** per part, with rate lookup, classification rationale and change control |
| 5 | Import eligibility and restriction checks: prohibited, restricted and permit-requiring goods |
| 6 | Import Registration Certificate and other trade-licence validity monitoring |
| 7 | **LCA form** preparation, lodgement with the authorised dealer bank, and tracking |
| 8 | **Letter of credit**: application, opening, amendment, expiry, negotiation, discrepancy handling, retirement |
| 9 | Alternative payment routes: telegraphic transfer, documentary collection, and open account where permitted |
| 10 | Bank charge capture: LC opening commission, amendment charges, negotiation and acceptance charges, SWIFT charges |
| 11 | Foreign-currency exposure per import, rate at commitment and rate at settlement, and exchange difference |
| 12 | Freight forwarder and shipping-line coordination, booking and shipment tracking |
| 13 | Shipping document set: bill of lading or airway bill, commercial invoice, packing list, certificate of origin, insurance certificate |
| 14 | Marine and air cargo insurance placement, cover verification and claims initiation |
| 15 | Arrival, manifest, port and airport handling, and demurrage/detention exposure tracking |
| 16 | **Bill of Entry** preparation and lodgement through the C&F agent into ASYCUDA World |
| 17 | Customs assessment tracking, assessment queries, examination, and release |
| 18 | **Duty and tax computation**: assessable value, CD, RD, SD, VAT, AT and AIT, in the correct cascading sequence |
| 19 | Recoverable versus non-recoverable tax separation for landed-cost purposes |
| 20 | C&F agent instruction, cost capture, performance measurement and reconciliation |
| 21 | Port charges, storage, demurrage, examination and handling cost capture |
| 22 | Inland transport from port to warehouse, coordinated with M03 |
| 23 | **Landed cost calculation** — the assembly of every cost element into a true unit cost |
| 24 | **Landed cost allocation** across consignment lines by value, weight, volume or quantity |
| 25 | Provisional versus final cost, and revaluation when late costs arrive |
| 26 | Import document register, retention and regulatory reconciliation |
| 27 | Import cycle-time measurement, cost analytics and landed-cost accuracy measurement |
| 28 | Duty drawback and bond facility handling where applicable |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Purchase requisition, sourcing, award, purchase order, three-way match | **M16** | The commercial transaction. M44 executes the cross-border half of an order M16 owns |
| Supplier qualification, agreements and scorecards — including for forwarders and C&F agents | **M42** | M44 *uses* qualified forwarders and agents; M42 qualifies and scores them |
| Stock quantity, ownership class, reservation, valuation posting | **M15** | M44 publishes the landed unit cost; M15 values stock at it |
| Physical receipt, inspection and put-away | **M41** / **M15** | M44's responsibility ends when cleared goods reach the warehouse gate |
| How much to import and when | **M43** Demand Planning | M44 models and reports import lead time; M43 uses it to decide quantity and timing |
| Journal posting of import costs, duty, exchange differences and revaluation | **M19** Financial Accounting | Only Category G posts. M44 raises cost events |
| **VAT, AT and AIT credit, rebate and return filing** | **M51** Tax & Regulatory Compliance | M44 computes them at import to determine what is *recoverable* and therefore excluded from landed cost; M51 owns claiming and filing |
| Payment of the supplier, the bank, the agent and the forwarder | **M52** Accounts Payable | — |
| LC facility limits, credit lines, margin deposits and bank relationships | **M50** Treasury, Cash & Banking | M44 consumes the facility; M50 manages it |
| FX hedging policy and instruments | **M50** Treasury | M44 records exposure and rate outcomes |
| Domestic transport execution and custody | **M03** Logistics | M44 requests the port-to-warehouse movement |
| Document storage, retention schedule and e-signature | **M24** Documents | M44 owns the import document *register* and its completeness rules |
| Import of capital equipment as fixed assets after receipt | **M49** Fixed Assets | M44 lands the cost; M49 capitalises it |
| Export and re-export | *(not in scope for v2.0)* | 1000FiX does not currently export. The model does not preclude it |

### 3.3 Shared Concepts

| Concept | M44's Role | Owning Module |
|---|---|---|
| Purchase order | Executes its cross-border half; retains the linkage both ways | M16 |
| Import consignment | **Owns** | M44 |
| HS code | **Owns** the classification and its rationale; M37 holds it as a part attribute | M44 / M37 |
| Landed cost | **Owns** the calculation and allocation; M15 adopts the unit cost; M19 posts it | M44 |
| Duty and import taxes | **Owns** the computation at import; M51 owns credit, rebate and filing | M44 / M51 |
| Letter of credit | **Owns** the instrument's trade lifecycle; M50 owns the facility and cash | M44 / M50 |
| Freight forwarder, shipping line, C&F agent | Uses and instructs; M42 qualifies and scores | M44 / M42 |
| Import lead time | **Produces** the actuals; M43 models and plans with them | M44 / M43 |
| Exchange rate and difference | Records exposure and outcome; M19 posts, M50 manages | M44 / M19 / M50 |
| Goods receipt of imported stock | Authorises against the cleared consignment; M41 or M15 executes | M44 / M41 / M15 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Global Trade Services (GTS) and Landed Cost / Import Management** | Product classification with legal control, sanctioned-party and restriction screening, customs declaration management, and a landed-cost object that accrues planned cost at PO and actualises at invoice | **The planned-versus-actual landed-cost pattern is the primary reference.** A landed cost is *estimated* at order (so the buying decision uses a true cost), *accrued* at receipt, and *actualised* as each cost document arrives, with the difference posted as a variance rather than hidden. Also adopted: classification as a controlled master-data act with a recorded rationale, not a free-text field | SAP GTS's full legal-control, embargo and licence-determination stack. Bangladesh's regime is narrower and the C&F agent carries the filing expertise |
| **Oracle Fusion Cloud — Landed Cost Management** | Charge names, cost factors, charge allocation by value/weight/volume/quantity, trade operation as the container for a shipment's costs | **The "trade operation" container and the cost-factor model adopted almost directly.** A cost factor declares its allocation basis and whether it is inventoriable; an import consignment accumulates cost factors and allocates them on their declared basis. This is exactly the abstraction the problem needs | Oracle's multi-organisation trade-operation depth |
| **Microsoft Dynamics 365 — Landed Cost module** | Voyage and shipping container model, costs applied to a voyage and apportioned to items, estimated versus actual with variance | The **voyage/consignment as the unit of cost accumulation** rather than the purchase order — because one shipment routinely carries lines from several orders and one order can split across shipments | The container and voyage granularity; our volumes are consolidated shipments, not fleet operations |
| **Odoo 19 CE `stock_landed_costs`** | Landed-cost record applied to receipts, split methods Equal / By Quantity / By Current Cost, landed-cost products flagged on vendor bills | The **execution substrate**. Odoo's split methods are the mechanical layer beneath our cost-factor model; the landed-cost document applies the allocation to the receiving stock layers | Odoo's split methods alone are insufficient: they lack allocation by weight and volume, they cannot separate recoverable from non-recoverable tax, and they have no concept of provisional cost or late revaluation. Extended in `cd_landed_cost` |
| **OCA `purchase_landed_cost` / `stock_landed_costs_delivery`** | Landed cost anticipated from the purchase order; delivery-based cost allocation | Anticipating landed cost at the purchase order, so the sourcing comparison in M16 uses landed cost rather than invoice price | — |
| **Bangladesh Customs / NBR practice (ASYCUDA World)** | Bill of Entry in Single Administrative Document format filed through ASYCUDA World by the importer or C&F agent; assessment, examination and release; assessable value based on CIF plus a 1% landing charge; the cascading CD → RD → SD → VAT → AT → AIT computation | **The Bangladesh duty computation is implemented natively and precisely** (see §5.6). The C&F agent files; M44 mirrors the declaration, tracks its state, and independently computes the expected duty so that the agent's figure can be checked rather than accepted | Direct ASYCUDA World integration in v2.0. The agent-mediated model is the market reality; the design keeps a clean seam for direct lodgement if it becomes available |
| **Bangladesh Bank Foreign Exchange Guidelines, Vol. 1, Ch. 7 §II** | LCA form and its five-year retention by the authorised dealer; letters of credit and remittances against imports; L/C requirement for release of goods | **The LCA form and the LC lifecycle are modelled as first-class objects with their own states**, not as attachments on a purchase order — because they have regulatory lives independent of the commercial order | — |

**Design position.** Five deliberate differences.

First, **recoverable taxes are excluded from landed cost, and this is the single most important
accounting decision in the module**. Customs duty, regulatory duty, supplementary duty, the
landing charge, freight, insurance, C&F fees, port charges and bank charges are *costs* and
belong in the unit cost of the part. Import VAT, Advance Tax and Advance Income Tax are, in the
normal case, **recoverable against output tax or income tax liability** and are *not* costs —
adding them to inventory value overstates both stock and cost of sales, and then understates
them again when the credit is claimed. M44 computes all seven, tags each as inventoriable or
recoverable, sends the inventoriable ones to landed cost and the recoverable ones to M51.
Getting this wrong is a common and expensive error, and it is designed out.

Second, **provisional cost is explicit and visible, never silent**. Duty is assessed days after
arrival and the C&F agent's final bill can arrive weeks later. Stock cannot wait. M44 therefore
publishes a *provisional* landed cost at receipt, M15 values at it and flags it provisional
(BRU-INV-15), and M44 publishes a *final* cost when the last document lands, triggering
revaluation of remaining stock and a COGS adjustment for what has already been consumed. The
target is that fewer than 1% of lines remain provisional beyond 30 days.

Third, **duty is independently computed, not merely recorded**. The C&F agent produces the
Bill of Entry and the duty figure. M44 computes what the duty *should* be from the HS code,
the assessable value and the current rate schedule, and compares. An agent's arithmetic error,
a misclassification, or an unexpected rate change surfaces as a variance rather than as an
unexplained cost. This is the practical value of holding the rate schedule internally.

Fourth, **landed cost is estimated before the order, not discovered after it**. M16's bid
comparison for a cross-border award calls M44 for an estimated landed cost per bid. Comparing
a Shenzhen FOB price against a Dhaka distributor's delivered price on invoice value alone is
not a comparison at all. This makes M44 useful at Wave 6 to a process that runs from Wave 3 —
and it is why the estimation service is specified separately from the actualisation engine.

Fifth, **the C&F agent is inside the system, not outside it**. The agent is a qualified
supplier (M42), receives instructions, is measured on clearance cycle time and cost accuracy,
and reconciles its bill against captured charges. The most common failure in Bangladeshi import
operations is that the agent is the only party who knows what happened.

---

## 5. Functional Areas & Features

### 5.1 Import Order & Proforma

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-001 | Import consignment | Create an import consignment from one or more confirmed cross-border purchase orders handed over by M16, as the container for all shipment, compliance and cost activity | **P0** | L5 |
| FR-ITC-002 | Proforma invoice | Record the supplier's proforma invoice and reconcile it line by line against the purchase order, blocking progression on unexplained variance | **P0** | L5 |
| FR-ITC-003 | Incoterm model | Record the incoterm and derive from it which cost elements and risks fall to 1000FiX and from which point | **P0** | L5 |
| FR-ITC-004 | Consolidation | Consolidate lines from multiple purchase orders and suppliers into one shipment where economics permit, preserving per-order traceability | P1 | L5 |
| FR-ITC-005 | **Landed cost estimation service** | Estimate landed cost for a prospective purchase — by HS code, incoterm, origin, mode, weight and value — and expose it to M16's bid comparison and M43's planning | **P0** | L5 |
| FR-ITC-006 | Import lead-time model | Record actual elapsed time at every stage and publish the mean and variability of the end-to-end import lead time to M43 | **P0** | L5 |

### 5.2 Trade Compliance & Classification

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-007 | **HS classification** | Hold an HS code per part with the classification rationale, the classifier's identity, the effective date and a change-control history; treat reclassification as a controlled master-data act | **P0** | L5 |
| FR-ITC-008 | Tariff rate schedule | Hold the applicable CD, RD, SD, VAT, AT and AIT rates per HS code with effective dates, maintained against the NBR tariff schedule | **P0** | L5 |
| FR-ITC-009 | Import eligibility check | Check every import line against prohibited, restricted and permit-requiring classifications, and block a consignment carrying a restricted item without its permit | **P0** | L5 |
| FR-ITC-010 | Restricted-goods handling | Flag lithium batteries, refrigerants and other dangerous goods, enforce the documentation and packing declarations they require, and pass the restriction to M03 and M41 | P1 | L5 |
| FR-ITC-011 | Trade licence validity | Monitor the Import Registration Certificate, VAT/BIN registration and any category-specific import permits, warning ahead of expiry and blocking new consignments on lapse | **P0** | L5 |
| FR-ITC-012 | Country of origin | Record and evidence country of origin, and apply preferential rates where a trade agreement and a valid certificate of origin permit | P2 | L5 |
| FR-ITC-013 | Compliance document completeness | Enforce a document checklist per consignment by mode and incoterm, and prevent lodgement where a mandatory document is missing | **P0** | L5 |

### 5.3 Payment Instruments — LCA, LC & Remittance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-014 | **LCA form** | Prepare the Letter of Credit Authorization form, lodge it with the authorised dealer bank, record its reference and status, and retain it for the regulatory five-year period | **P0** | L5 |
| FR-ITC-015 | **Letter of credit lifecycle** | Manage the LC through application, bank approval, opening, transmission, amendment, shipment, document presentation, discrepancy handling, acceptance, negotiation, retirement and expiry, with a state at every point | **P0** | L5 |
| FR-ITC-016 | LC discrepancy handling | Record discrepancies raised by the negotiating bank, the decision to accept or refuse, and the cost and delay consequences | P1 | L5 |
| FR-ITC-017 | Alternative payment routes | Support telegraphic transfer, documentary collection and open account where the regulatory framework and the supplier relationship permit, with the same document and cost discipline | P1 | L5 |
| FR-ITC-018 | Bank charge capture | Capture LC opening commission, amendment, acceptance, negotiation, SWIFT and handling charges against the consignment as cost factors | **P0** | L5 |
| FR-ITC-019 | FX exposure and settlement | Record the rate and rate source at commitment and at settlement, compute the exchange difference, and raise it to M19 | **P0** | L5 |
| FR-ITC-020 | Treasury interface | Reserve and release LC facility capacity and margin deposits against M50's limits, and block an LC application that exceeds available facility | P1 | L5 |

### 5.4 Shipment, Freight & Insurance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-021 | Freight booking | Instruct a qualified freight forwarder, record the booking, mode, carrier, vessel or flight, and the expected dates | **P0** | L5 |
| FR-ITC-022 | Shipment tracking | Track the shipment through departure, transhipment and arrival, recording actual dates against expected | **P0** | L5 |
| FR-ITC-023 | Shipping document set | Register the bill of lading or airway bill, commercial invoice, packing list, certificate of origin and insurance certificate, with completeness validation before lodgement | **P0** | L5 |
| FR-ITC-024 | Cargo insurance | Record the marine or air insurance policy, verify that cover matches consignment value and incoterm responsibility, and initiate a claim on loss or damage | P1 | L5 |
| FR-ITC-025 | Arrival and port handling | Record vessel or flight arrival, manifest submission, and the start of the free-time clock | **P0** | L5 |
| FR-ITC-026 | Demurrage exposure | Track free-time expiry and accruing demurrage and detention, alerting daily once exposure begins | P1 | L5 |

### 5.5 Customs Clearance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-027 | **Bill of Entry** | Prepare the Bill of Entry data set in Single Administrative Document structure, transmit it to the C&F agent for lodgement into ASYCUDA World, and record the resulting B/E number and date | **P0** | L5 |
| FR-ITC-028 | Assessment tracking | Track the declaration through assessment, query, examination and release, recording each state change, its date and any query raised | **P0** | L5 |
| FR-ITC-029 | **Duty verification** | Independently compute expected duty and taxes from the HS code, assessable value and rate schedule, compare against the assessed figure, and raise a variance for investigation before payment | **P0** | L5 |
| FR-ITC-030 | C&F agent instruction and reconciliation | Instruct the agent, capture their charges, reconcile their bill against captured charges and the agreed tariff, and measure their clearance cycle time and cost accuracy for M42 | **P0** | L5 |
| FR-ITC-031 | Port and clearance cost capture | Capture port charges, storage, demurrage, examination, handling and inland transport as cost factors against the consignment | **P0** | L5 |
| FR-ITC-032 | Release and inland movement | Record customs release, request the port-to-warehouse movement from M03, and authorise receipt against the cleared consignment in M41 or M15 | **P0** | L5 |

### 5.6 Duty & Tax Computation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-033 | **Assessable value and cascading computation** | Compute the assessable value and every import levy in the correct cascading sequence, per line, per HS code: `AV = CIF + 1% landing charge` · `CD = AV × cd_rate` · `RD = AV × rd_rate` · `SD = (AV + CD + RD) × sd_rate` · `VAT = (AV + CD + RD + SD) × vat_rate` · `AT = (AV + CD + SD) × at_rate` · `AIT = AV × ait_rate` — with the rate set and formula version stored on the computation | **P0** | L5 |
| FR-ITC-034 | **Recoverable / inventoriable separation** | Tag every computed levy as inventoriable (customs duty, regulatory duty, supplementary duty, landing charge) or recoverable (VAT, AT, AIT), include only inventoriable levies in landed cost, and publish recoverable amounts to M51 for credit and filing | **P0** | L5 |

### 5.7 Landed Cost Calculation & Allocation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ITC-035 | **Cost factor model and allocation** | Model every cost element as a cost factor declaring its allocation basis (value, weight, volume, quantity or direct), its inventoriable status and its expected timing; allocate each factor across consignment lines on its declared basis; and compute a true landed unit cost per line | **P0** | L1/L5 |
| FR-ITC-036 | **Provisional and final cost with revaluation** | Publish a provisional landed unit cost at receipt so that stock can be valued and used, publish the final cost when the last cost document arrives, revalue remaining stock, raise a cost-of-sales adjustment for quantities already consumed, and measure the provisional-to-final variance as the landed-cost accuracy KPI | **P0** | L5 |

> **Worked example — the cascade in practice.** A consignment line: CIF USD 1,000 at BDT 120 =
> BDT 120,000. Landing charge 1% = BDT 1,200, so **AV = BDT 121,200**. At CD 10%, RD 3%, SD 0%,
> VAT 15%, AT 5%, AIT 5%: CD = 12,120 · RD = 3,636 · SD = 0 · VAT = (121,200 + 12,120 + 3,636)
> × 15% = 20,543 · AT = (121,200 + 12,120 + 0) × 5% = 6,666 · AIT = 6,060.
> **Inventoriable** = AV + CD + RD + SD = **BDT 136,956**, plus the consignment's allocated
> share of freight already inside CIF, C&F fee, port charges and bank charges.
> **Recoverable** = VAT + AT + AIT = **BDT 33,269**, which goes to M51 and **never** to unit
> cost. On the invoice value alone the line looks like BDT 120,000; the true inventoriable cost
> before clearance charges is already **14% higher**.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Duty computation determinism and versioning** | Every duty computation stores the HS code, the rate set version, the formula version, the assessable value and each intermediate result. A computation is reproducible years later, which is what a customs dispute requires |
| T-02 | **Rate schedule as versioned reference data** | Tariff rates are effective-dated. A computation uses the rates in force on the Bill of Entry date, never the current ones |
| T-03 | **Allocation correctness and rounding** | Cost-factor allocation is exhaustive and lossless: allocated amounts sum exactly to the factor total, with rounding differences assigned deterministically to a designated line rather than dropped |
| T-04 | **Provisional-to-final integrity** | A final cost publication is idempotent and traceable: it identifies the provisional value it replaces, the delta per line, the remaining quantity revalued and the consumed quantity adjusted |
| T-05 | **Currency discipline** | All money uses `Monetary` with explicit currency (AS-10). Foreign amounts store the original currency, the rate, the rate source and the rate date; base-currency amounts are derived, never re-derived at a later rate |
| T-06 | **Document completeness gate** | The checklist engine is data-driven by mode, incoterm and classification, and evaluates at lodgement rather than at save |
| T-07 | **Regulatory retention** | LCA forms, LC documents and Bills of Entry are retained through M24 under a **five-year minimum** retention class aligned to the Bangladesh Bank requirement, with immutability and hash verification |
| T-08 | **Event emission via outbox** | Consignment, LC, clearance, cost and revaluation state changes emit through the transactional outbox (AS-08) |
| T-09 | **Estimation service latency** | The landed-cost estimation service used by M16 bid comparison returns in ≤ 300 ms at p95 for a 50-line estimate |
| T-10 | **Seam for direct ASYCUDA lodgement** | The Bill of Entry data set is produced in a structured, transport-agnostic form. The agent channel is one adapter; a direct lodgement adapter can be added without changing the model |
| T-11 | **Cost-document reconciliation** | Agent, forwarder, port and bank invoices are matched against captured cost factors with tolerance, and variances are classified rather than absorbed |
| T-12 | **Multi-entity readiness** | Consignments, declarations and costs carry `company_id`; a second country's import regime is a rate-schedule and formula configuration, not a code change (AS-03, BO-18) |
| T-13 | **Performance** | Landed-cost allocation over a 500-line consignment with 12 cost factors completes in ≤ 5 s; revaluation of a consignment's remaining stock in ≤ 30 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M44 |
|---|---|---|
| **Import / procurement officer** | Coordinates the bank, the forwarder and the agent by phone and email; holds the whole process in their head | One consignment record with every state, document, cost and date; exceptions surfaced rather than remembered |
| **Procurement manager** | Compares an import price against a local price on invoice value | Compares landed cost against landed cost — the only comparison that means anything |
| **CFO** | Inventory value and margin on imported parts are wrong by an unknown amount | Landed cost within 2% of actual; recoverable taxes correctly excluded and claimed |
| **Finance officer** | Reconciles agent and bank bills against nothing | Reconciles against captured cost factors with a tolerance and a variance reason |
| **Inventory manager** | Unit cost of an imported part is the invoice price | Unit cost is the true cost, provisional then final, with revaluation visible |
| **Demand planner (M43)** | Import lead time is "six to eight weeks, usually" | Mean and variability measured per supplier, mode and route, feeding the reorder point |
| **Warehouse** | An arriving consignment is a surprise | Arrival, clearance and expected receipt dates visible ahead of time |
| **C&F agent** | The only party who knows what happened | Instructed through the system, measured on cycle time and cost accuracy, reconciled against an agreed tariff |
| **Auditor / regulator** | Import documentation is a filing cabinet | A complete, retained, reconcilable register |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Margin truth on imported parts** | Duty, freight, clearing and bank charges reach unit cost; recoverable taxes correctly excluded | **The primary benefit.** Imported parts can carry 25–60% cost above invoice value. Pricing and profitability on the imported base are currently overstated by an unknown margin; M44 makes them correct, which corrects M11 pricing, M20 invoicing and M54 profitability |
| **Landed cost accuracy** | Estimation at order, provisional at receipt, final at document completion, variance measured | **Within 2% of actual** — the category target |
| **Import clearance cycle time** | Document completeness enforced before lodgement, agent instructed and measured, demurrage exposure alerted daily | **−20% against baseline** — the category target. Each day saved is a day of demurrage avoided and a day off the lead time M43 must cover with safety stock |
| **Demurrage and detention avoidance** | Free-time clock tracked, exposure alerted from day one, document gaps caught before arrival not after | Demurrage is pure loss and is entirely avoidable with visibility |
| **Duty error recovery** | Independent computation checks the assessed figure before payment | Recovers overpayment and prevents underpayment penalties; a single misclassification on a repeat-import part compounds across every future consignment |
| **Recoverable tax capture** | VAT, AT and AIT identified at import and published to M51 for credit | Recovers tax credit currently at risk of being absorbed into cost and never claimed |
| **Safety stock reduction** | Import lead-time variability measured rather than assumed | Contributes to the **BDT 34 lac/year** inventory benefit; lead-time variability is the dominant term in safety stock for imported parts |
| **Sourcing decision quality** | Landed-cost estimation inside M16's bid comparison | Prevents the systematic bias toward imports that invoice-price comparison creates |
| **FX exposure visibility** | Rate at commitment versus rate at settlement per consignment | Makes an unmanaged exposure visible and hedgeable (M50) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Regulatory defensibility** | LCA forms, LC documents and Bills of Entry retained for the five-year period with a reproducible duty computation behind each. A customs or Bangladesh Bank query becomes a query, not an incident |
| **Continuity of import capability** | IRC and permit expiry monitored. A lapsed registration stops the parts supply for the entire business, and it is the kind of failure that happens because nobody owned the renewal |
| **Key-person risk removed** | Import knowledge is currently held by one or two people. It becomes institutional |
| **Brand relationship protection** | Genuine OEM parts for 17+ brands are predominantly imported, often from brand-designated sources. Reliable, compliant, documented import is a condition of maintaining authorisation |
| **Anti-counterfeit chain** | Country of origin, certificate of origin and supplier provenance recorded per consignment and carried into M15's serial provenance |
| **Negotiating position with agents and forwarders** | Cycle time and cost accuracy measured per agent and fed to M42's scorecard |
| **Second-country readiness** | The duty engine is formula-and-rate configuration. A different regime is a configuration exercise, supporting BO-18 |

---

## 8. Lifecycle & State Models

### 8.1 Import Consignment Lifecycle

```
   M16 confirms a cross-border purchase order
              │
        ┌─────▼──────────┐
        │   INITIATED    │  consignment created, incoterm recorded
        └─────┬──────────┘
              │ proforma received and reconciled to the PO
        ┌─────▼──────────┐
        │  PROFORMA      │  ✖ blocked on unexplained PO variance
        │  CONFIRMED     │  ✖ blocked if IRC/permit lapsed (BRU-ITC-03)
        └─────┬──────────┘
              │ HS classified, eligibility checked, LCA lodged
        ┌─────▼──────────┐
        │  LCA LODGED    │
        └─────┬──────────┘
              │ payment instrument arranged
      ┌───────┴────────┬──────────────────┐
┌─────▼──────┐  ┌──────▼──────┐   ┌───────▼──────┐
│ LC OPENED  │  │  TT / OPEN  │   │ DOCUMENTARY  │
│            │  │  ACCOUNT    │   │  COLLECTION  │
└─────┬──────┘  └──────┬──────┘   └───────┬──────┘
      └────────────────┴──────────────────┘
              │ supplier ships
        ┌─────▼──────────┐
        │   SHIPPED      │  B/L or AWB registered, ETA recorded
        └─────┬──────────┘
              │ vessel / flight arrives, manifest submitted
        ┌─────▼──────────┐
        │   ARRIVED      │  ◄── free-time clock starts;
        └─────┬──────────┘      demurrage exposure tracked daily
              │ document set complete (BRU-ITC-05)
        ┌─────▼──────────┐
        │ B/E LODGED     │  filed by the C&F agent into ASYCUDA World
        └─────┬──────────┘
              │
        ┌─────▼──────────┐      ┌──────────────┐
        │ UNDER          │─────►│  QUERY /     │ classification or valuation
        │ ASSESSMENT     │◄─────│  EXAMINATION │ dispute; response recorded
        └─────┬──────────┘      └──────────────┘
              │ duty assessed
        ┌─────▼──────────┐
        │ DUTY VERIFIED  │  ◄── independent computation compared;
        └─────┬──────────┘      ✖ variance blocks payment (BRU-ITC-07)
              │ duty paid
        ┌─────▼──────────┐
        │   RELEASED     │
        └─────┬──────────┘
              │ inland movement requested from M03
        ┌─────▼──────────┐
        │ RECEIVED AT    │  ──► M41 / M15 receive against the consignment
        │ WAREHOUSE      │  ──► PROVISIONAL landed cost published to M15
        └─────┬──────────┘
              │ all cost documents received and reconciled
        ┌─────▼──────────┐
        │ COST FINALISED │  ──► FINAL landed cost published;
        └─────┬──────────┘      remaining stock revalued;
              │                 consumed quantities COGS-adjusted
        ┌─────▼──────────┐
        │     CLOSED     │
        └────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Initiated | M16 hands over a confirmed cross-border purchase order | M16 |
| Initiated | Proforma confirmed | Proforma reconciles to the PO within tolerance; **IRC and permits valid** | Import officer |
| Proforma confirmed | LCA lodged | HS classified for every line; eligibility and restriction checks passed | Import officer |
| LCA lodged | LC opened | Bank approves; **M50 facility available** (BRU-ITC-06) | Bank / Treasury |
| LC opened / TT / collection | Shipped | Supplier ships; bill of lading or airway bill registered | Supplier / forwarder |
| Shipped | Arrived | Vessel or flight arrival confirmed; manifest submitted | Forwarder |
| Arrived | B/E lodged | **Document checklist complete** (BRU-ITC-05) | C&F agent |
| B/E lodged | Under assessment | Declaration accepted by customs | Customs |
| Under assessment | Query / examination | Customs raises a valuation or classification query | Customs |
| Under assessment | Duty verified | Assessed duty compared against M44's independent computation | Import officer |
| Duty verified | Released | Duty and taxes paid; customs release issued; **variance resolved** | Customs / Finance |
| Released | Received at warehouse | Inland movement complete; goods receipted against the consignment | M03 → M41 / M15 |
| Received | Cost finalised | Every expected cost document received and reconciled | Import officer / Finance |
| Cost finalised | Closed | Final cost published; revaluation and COGS adjustment posted by M19 | System |

### 8.2 Letter of Credit Lifecycle

```
   APPLIED ──► bank review ──► APPROVED ──► OPENED ──► TRANSMITTED
      │                          │            │
      │ rejected                 │            ├──► AMENDED ──┐
      ▼                          ▼            │              │
   WITHDRAWN                  DECLINED        │◄─────────────┘
                                              │
                              shipment ──► DOCUMENTS PRESENTED
                                              │
                              ┌───────────────┴───────────────┐
                              │                               │
                        DISCREPANT                       COMPLIANT
                              │                               │
                    ┌─────────┴─────────┐                     │
                    │                   │                     │
              accepted by us       refused                    │
                    │                   │                     │
                    └─────────┬─────────┘                     │
                              │                     ┌─────────┘
                              ▼                     ▼
                          ACCEPTED  ────────►  NEGOTIATED
                                                    │
                                                    ▼
                                                 RETIRED  ──► CLOSED
                                                    │
                                            (or EXPIRED unused
                                             ──► CANCELLED, charges captured)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ITC-01 | **Imported stock is not valued as final until M44 publishes the final landed cost.** Interim value is provisional and is flagged as such in M15 (reciprocal of BRU-INV-15) | **H** | CFO |
| BRU-ITC-02 | **Recoverable taxes — import VAT, Advance Tax and Advance Income Tax — are never included in landed cost.** They are published to M51 for credit | **H** | CFO |
| BRU-ITC-03 | A consignment cannot progress beyond proforma confirmation if the Import Registration Certificate or any required permit is expired | **H** | Procurement Manager |
| BRU-ITC-04 | Every import line carries an HS code with a recorded classification rationale; reclassification is a controlled act requiring approval | **H** | Procurement Manager |
| BRU-ITC-05 | A Bill of Entry cannot be lodged until the mandatory document checklist for the mode, incoterm and classification is complete | **H** | Procurement Manager |
| BRU-ITC-06 | An LC application exceeding the available facility or margin held by M50 is blocked | **H** | CFO |
| BRU-ITC-07 | Where the assessed duty differs from M44's independent computation beyond tolerance, payment is blocked pending investigation and either correction or documented acceptance | **H** | CFO |
| BRU-ITC-08 | Duty is computed using the rate schedule in force on the Bill of Entry date, never the current schedule | **C** | Procurement Manager |
| BRU-ITC-09 | Cost-factor allocation is exhaustive: allocated amounts must sum exactly to the factor total, with rounding assigned deterministically | **H** | CTO |
| BRU-ITC-10 | A prohibited item is blocked outright; a restricted item is blocked without its valid permit attached to the consignment | **H** | Quality Manager |
| BRU-ITC-11 | LCA forms, LC documents and Bills of Entry are retained for a minimum of five years and are immutable once lodged | **H** | CFO |
| BRU-ITC-12 | A freight forwarder or C&F agent must be qualified and active in M42 before it can be instructed | **H** | Procurement Manager |
| BRU-ITC-13 | Cargo insurance cover must equal or exceed consignment value where the incoterm places the risk on 1000FiX; a shortfall blocks shipment authorisation | **H** | CFO |
| BRU-ITC-14 | The exchange rate at commitment and at settlement is recorded with its source and date; base-currency amounts are never re-derived at a later rate | **H** | CFO |
| BRU-ITC-15 | Final cost publication revalues remaining stock and raises a cost-of-sales adjustment for quantities already consumed; the difference is never absorbed silently | **H** | CFO |
| BRU-ITC-16 | Agent, forwarder, port and bank invoices are reconciled against captured cost factors within tolerance; a variance is classified, not absorbed | **H** | Finance Manager |
| BRU-ITC-17 | Demurrage incurred is recorded against the consignment with an attributed cause and appears on a standing report | **C** | Procurement Manager |
| BRU-ITC-18 | A consignment cannot close with an unreconciled cost document or an unresolved duty variance | **H** | Finance Manager |
| BRU-ITC-19 | Import lead-time actuals are recorded at every stage and published to M43; they are not editable | **H** | Supply Chain Director |
| BRU-ITC-20 | An LC amendment increasing value beyond tolerance requires re-approval at the authority band of the new total (`05-04` §7) | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.import.consignment` | `fix_import_consignment` | The container for a cross-border movement | number, po_ids, supplier_id, origin_country, incoterm, mode (sea/air/land), forwarder_id, cf_agent_id, currency, commercial_value, state, eta, ata, cost_state (provisional/final), company_id |
| `fix.import.line` | `fix_import_line` | One line within the consignment | consignment_id, po_line_id, part_id, quantity, unit_price, currency, hs_code, net_weight, gross_weight, volume, country_of_origin, assessable_value, landed_unit_cost_provisional, landed_unit_cost_final |
| `fix.hs.classification` | `fix_hs_classification` | HS code per part, controlled | part_id, hs_code, description, rationale, classified_by, approved_by, effective_from, effective_to, supersedes_id |
| `fix.tariff.rate` | `fix_tariff_rate` | The NBR rate schedule | hs_code, cd_rate, rd_rate, sd_rate, vat_rate, at_rate, ait_rate, effective_from, effective_to, source_reference, loaded_by |
| `fix.import.restriction` | `fix_import_restriction` | Prohibited, restricted and permit-requiring classifications | hs_code_pattern, restriction_type, permit_type, issuing_authority, notes, effective_from |
| `fix.import.permit` | `fix_import_permit` | A held permit or registration | type (IRC/permit/authorisation), reference, holder_entity_id, scope, issued_on, expires_on, document_id, status |
| `fix.lca.form` | `fix_lca_form` | Letter of Credit Authorization | consignment_id, ad_bank_id, reference, lodged_on, value, currency, state, document_id, retention_until |
| `fix.letter.of.credit` | `fix_letter_of_credit` | The LC instrument | consignment_id, lc_number, issuing_bank_id, advising_bank_id, beneficiary_id, value, currency, tenor, latest_shipment_date, expiry_date, state, facility_ref (M50), margin_deposit |
| `fix.lc.amendment` | `fix_lc_amendment` | An LC change | lc_id, sequence, change_type, old_value, new_value, reason, charge_amount, approved_by, effective_on |
| `fix.lc.discrepancy` | `fix_lc_discrepancy` | A presentation defect | lc_id, raised_by_bank, description, raised_on, decision (accept/refuse), decided_by, cost_impact, delay_days |
| `fix.import.shipment` | `fix_import_shipment` | The physical movement | consignment_id, forwarder_id, carrier, vessel_or_flight, bl_awb_number, port_of_loading, port_of_discharge, etd, atd, eta, ata, container_refs |
| `fix.import.document` | `fix_import_document` | The document register | consignment_id, doc_type (proforma/commercial_invoice/packing_list/bl_awb/coo/insurance/lca/lc/boe/release), reference, issued_on, received_on, document_id (M24), mandatory, verified_by, retention_class |
| `fix.cargo.insurance` | `fix_cargo_insurance` | Cover for the consignment | consignment_id, insurer_id, policy_number, cover_value, currency, premium, cover_from, cover_to, claim_ref |
| `fix.bill.of.entry` | `fix_bill_of_entry` | The customs declaration | consignment_id, be_number, be_date, customs_house, cf_agent_id, sad_payload_ref, state, assessment_date, query_raised, examination_result, release_date |
| `fix.duty.computation` | `fix_duty_computation` | The levy calculation, per line | import_line_id, be_id, hs_code, rate_set_version, formula_version, cif_value, landing_charge, assessable_value, cd, rd, sd, vat, at, ait, inventoriable_total, recoverable_total, computed_at |
| `fix.duty.variance` | `fix_duty_variance` | Independent check against assessment | duty_computation_id, assessed_amount, computed_amount, variance, variance_pct, cause, investigated_by, resolution, resolved_at |
| `fix.cost.factor` | `fix_cost_factor` | A cost element definition | code, name, category (freight/insurance/duty/clearing/port/bank/inland/other), allocation_basis (value/weight/volume/quantity/direct), inventoriable, expected_timing, default_supplier_type |
| `fix.consignment.cost` | `fix_consignment_cost` | An actual cost incurred | consignment_id, cost_factor_id, supplier_id, amount, currency, rate, base_amount, document_ref, incurred_on, received_on, estimated, reconciled, variance_reason |
| `fix.landed.cost` | `fix_landed_cost` | The allocation result | consignment_id, version (provisional/final), import_line_id, base_value, allocated_costs_json, inventoriable_total, landed_unit_cost, published_at, published_to_m15_at, supersedes_version |
| `fix.landed.cost.revaluation` | `fix_landed_cost_revaluation` | The provisional-to-final adjustment | landed_cost_id, part_id, provisional_unit_cost, final_unit_cost, delta_per_unit, qty_remaining, revaluation_value, qty_consumed, cogs_adjustment_value, raised_to_m19_at |
| `fix.demurrage.exposure` | `fix_demurrage_exposure` | Free-time and accruing charges | consignment_id, free_time_expires_on, days_incurred, daily_rate, accrued_amount, cause, attributed_to, closed_on |
| `fix.import.cycle.time` | `fix_import_cycle_time` | Stage-by-stage actuals | consignment_id, stage, entered_at, exited_at, elapsed_hours, target_hours, variance |
| `fix.fx.exposure` | `fix_fx_exposure` | Currency outcome per consignment | consignment_id, currency, committed_amount, committed_rate, committed_on, settled_amount, settled_rate, settled_on, exchange_difference |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.purchase.order`, `fix.purchase.order.line` | M16 | Read; bidirectional linkage retained |
| `fix.supplier.profile`, activation status (supplier, forwarder, C&F agent, insurer) | M42 | Read; activation is a hard gate |
| `fix.catalogue.item` (weight, volume, description, hazard class) | M37 | Read |
| `fix.stock.quant`, `fix.stock.move` | M15 | Read; publish landed cost, trigger revaluation |
| `fix.wh.inbound` | M41 | Authorise receipt against the cleared consignment |
| `fix.bank.facility`, LC limits, margin deposits | M50 | Read and reserve |
| Tax credit and return positions | M51 | Publish recoverable amounts |
| `fix.ap.invoice`, payments to supplier, bank, agent, forwarder | M52 | Read for cost reconciliation |
| `fix.document` | M24 | Store with the five-year retention class |
| `fix.consignment` (inland movement) | M03 | Command |
| `fix.planned.order`, consolidated import demand | M43 | Read; publish lead-time actuals |
| `fix.entity`, `fix.entity` | M30 | Read for IRC and registration scope |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ITC-01 | M16 confirms a cross-border purchase order | Create the import consignment, derive incoterm responsibilities, open the document checklist, and check IRC and permit validity | Manual consignment creation; block if registrations lapsed |
| AUT-ITC-02 | Proforma invoice received | Reconcile line by line against the purchase order; block on unexplained variance and notify procurement | Route to manual reconciliation |
| AUT-ITC-03 | Consignment lines classified | Look up rates from the schedule in force, compute estimated duty and estimated landed cost, and publish the estimate to M16 and M43 | Estimate flagged unavailable; sourcing comparison warns |
| AUT-ITC-04 | Restricted or prohibited classification detected | Block progression, notify Quality Manager and Procurement Manager, and require the permit before release | Hard block |
| AUT-ITC-05 | IRC, permit or registration nears expiry (90 / 60 / 30 days) | Notify the Procurement Manager and CFO; on lapse, block new consignments | Hard block at lapse |
| AUT-ITC-06 | LC application raised | Check facility availability with M50, reserve capacity and margin, and route for approval at the authority band | Block if facility unavailable |
| AUT-ITC-07 | LC opened, amended or negotiated | Capture the bank charge as a cost factor against the consignment and update the FX exposure | Manual charge entry; flagged incomplete |
| AUT-ITC-08 | Latest shipment date or LC expiry approaches | Alert the import officer and procurement with the days remaining and the amendment option | Alert only |
| AUT-ITC-09 | Shipment departure or arrival recorded | Update the consignment state, recompute the ETA, notify the warehouse and the planner, and record the stage cycle time | Manual status update |
| AUT-ITC-10 | Arrival recorded | Start the free-time clock and begin daily demurrage exposure tracking | Alert only |
| AUT-ITC-11 | Free time expires | Alert daily with the accruing amount, escalating by value to the Procurement Manager and CFO | Escalate |
| AUT-ITC-12 | Document checklist complete | Generate the Bill of Entry data set and transmit it to the C&F agent for lodgement | Hold; report the missing documents |
| AUT-ITC-13 | Assessed duty received from the agent | Independently compute expected duty from the HS code, assessable value and in-force rates; compare; **block payment on variance beyond tolerance** | Hard block pending investigation |
| AUT-ITC-14 | Customs release recorded | Request the inland movement from M03 and authorise receipt against the consignment in M41 or M15 | Manual movement request |
| AUT-ITC-15 | Goods received at the warehouse | Allocate all known cost factors, compute the **provisional** landed unit cost, publish it to M15, and flag the stock provisional | Block receipt valuation and escalate |
| AUT-ITC-16 | A cost document arrives (agent, forwarder, port, bank) | Reconcile against captured cost factors within tolerance, classify any variance, and update the allocation | Route to manual reconciliation |
| AUT-ITC-17 | All expected cost documents received and reconciled | Compute and publish the **final** landed cost; trigger M15 revaluation of remaining stock and a COGS adjustment for consumed quantities; raise the events to M19 | Retry; consignment remains provisional and reportable |
| AUT-ITC-18 | Duty and tax computed | Publish recoverable VAT, AT and AIT amounts to M51 for credit and return filing | Queue and retry; report unclaimed exposure |
| AUT-ITC-19 | Consignment closes | Publish stage-by-stage lead-time actuals to M43 and agent and forwarder performance to M42 | Retry |
| AUT-ITC-20 | Provisional line ages beyond 30 days | Escalate to the Procurement Manager and Finance Manager with the value at stake | Report on the standing exception list |
| AUT-ITC-21 | Tariff schedule update published by NBR | Load as a new effective-dated rate version, recompute open estimates, and report parts whose duty materially changes | Alert; continue on the prior version |

---

## 12. Interfaces

### 12.1 Upstream — M44 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M16 Procurement** | Confirmed cross-border purchase orders and their lines | Command `po.import_handoff` |
| **M42 Supplier Relationship** | Activation status for suppliers, freight forwarders, C&F agents and insurers; agreed tariffs | REST (gate) |
| M37 Catalogue | Part description, weight, volume, hazard class | REST |
| M50 Treasury | LC facility limits, availability, margin deposits, exchange rates and their source | REST |
| M52 Accounts Payable | Supplier, bank, agent, forwarder and port invoices for cost reconciliation | Events |
| M41 / M15 | Physical receipt confirmation against the cleared consignment | Events |
| M03 Logistics | Inland movement status from port to warehouse | Events |
| M43 Demand Planning | Consolidated import demand and required-by dates | REST |
| M24 Documents | Document storage under the five-year retention class | Command |
| M30 / M64 | Legal entity, registrations and configuration | REST |

### 12.2 Downstream — M44 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M15 Inventory** | **Provisional and final landed unit cost; revaluation instruction** | Events + REST |
| **M16 Procurement** | Estimated landed cost for bid comparison; import execution status against the purchase order | REST + events |
| **M51 Tax & Regulatory Compliance** | Recoverable import VAT, AT and AIT for credit and return filing | Events |
| **M19 Financial Accounting** | Import cost events, duty, exchange differences, revaluation and COGS adjustment | Events |
| **M43 Demand Planning** | Import lead time by stage, with mean and variability | Warehouse extract + REST |
| M41 Warehouse Management | Expected inbound consignments, cleared quantities, restricted-item handling requirements | Events |
| M42 Supplier Relationship | Forwarder, C&F agent and insurer performance facts | Events |
| M52 Accounts Payable | Approved agent, forwarder, port and bank charges for payment | Events |
| M50 Treasury | LC facility utilisation and FX exposure | Events |
| M54 FP&A | True landed cost as an input to product and service profitability | Warehouse extract |
| M11 Pricing | True cost basis for imported parts | REST |
| M25 BI / M62 | Consignment, duty, cost, cycle-time and accuracy facts | Warehouse extract |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `import.consignment_created` | consignment, purchase orders, supplier, incoterm, mode | M15, M41, M43, M50 |
| `import.estimate_published` | consignment or prospective line, estimated landed cost, basis | **M16**, M43 |
| `import.lca_lodged` | consignment, AD bank, reference, value | M50, M52 |
| `import.lc_opened` | LC number, value, tenor, expiry, facility reference | M50, M52 |
| `import.lc_amended` | LC, change, charge, new value | M50, M52 |
| `import.shipped` | consignment, carrier, B/L or AWB, ETD, ETA | M41, M43, M15 |
| `import.arrived` | consignment, arrival date, free time expiry | M41, M03 |
| `import.boe_lodged` | consignment, B/E number and date, customs house | M51, M52 |
| `import.duty_assessed` | consignment, assessed amounts by levy | M51, M52, M19 |
| `import.duty_variance` | consignment, assessed, computed, variance, cause | M52, M19, M42 |
| **`import.cleared`** | consignment, release date, cleared quantities | **M41**, **M15**, M03 |
| **`landed_cost.provisional`** | consignment, per-line provisional unit cost | **M15**, M19 |
| **`landed_cost.finalised`** | consignment, per-line final unit cost, delta from provisional | **M15**, M19, M11, M54 |
| `landed_cost.revaluation_required` | part, layer, delta, remaining quantity, consumed quantity | **M15**, M19 |
| `import.recoverable_tax` | consignment, VAT, AT, AIT amounts, B/E reference | **M51** |
| `import.fx_settled` | consignment, committed rate, settled rate, exchange difference | M19, M50 |
| `import.demurrage_incurred` | consignment, days, amount, attributed cause | M19, M42, M54 |
| `import.cycle_time_recorded` | consignment, stage actuals, total elapsed | **M43**, M42 |
| `import.permit_expiring` | permit type, reference, expiry, consequence | M16, CFO |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ITC-01 | **C&F agent** (email, file exchange, or agent portal) | Bidirectional | Bill of Entry data set out; B/E number, assessment, query, examination and release status in. **The agent lodges into ASYCUDA World; M44 does not integrate with ASYCUDA directly in v2.0** |
| INT-ITC-02 | Authorised dealer bank | Bidirectional | LCA lodgement, LC application, amendment, document presentation, discrepancy notice, charges. File or portal-based; SWIFT MT7xx ingestion is a future option |
| INT-ITC-03 | Freight forwarder / shipping line tracking | Inbound | Booking confirmation, departure, transhipment and arrival milestones |
| INT-ITC-04 | **NBR tariff schedule** | Inbound | Effective-dated CD, RD, SD, VAT, AT and AIT rates per HS code; file-based load with version control |
| INT-ITC-05 | Cargo insurer | Bidirectional | Policy placement, cover confirmation, claim initiation |
| INT-ITC-06 | Port / terminal charge statements | Inbound | Storage, demurrage, handling and examination charges for cost reconciliation |
| INT-ITC-07 | Exchange rate source (Bangladesh Bank / AD bank rates) | Inbound | Rates with source and date for commitment and settlement recording |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| **`/api/v1/import/estimate`** | **POST** | **Estimated landed cost for a prospective purchase — the M16 bid-comparison service** | **M16**, M43, P03 |
| `/api/v1/import/consignments` | POST | Create an import consignment from purchase orders | M16, P03 |
| `/api/v1/import/consignments/{id}` | GET | Full consignment: state, documents, costs, dates | P03, P06 |
| `/api/v1/import/consignments/{id}/proforma` | POST | Record and reconcile the proforma | P03 |
| `/api/v1/import/consignments/{id}/lca` | POST | Lodge the LCA form | P03 |
| `/api/v1/import/consignments/{id}/lc` | POST | Apply for or amend a letter of credit | P03 |
| `/api/v1/import/consignments/{id}/shipment` | POST | Record booking, departure and arrival | P03, forwarder adapter |
| `/api/v1/import/consignments/{id}/documents` | POST | Register a document against the checklist | P03, agent adapter |
| `/api/v1/import/consignments/{id}/boe` | POST | Produce and transmit the Bill of Entry data set | P03, agent adapter |
| `/api/v1/import/consignments/{id}/assessment` | POST | Record assessment, query, examination and release | Agent adapter, P03 |
| `/api/v1/import/consignments/{id}/duty` | GET | Computed duty, assessed duty and variance | P03, M51, M52 |
| `/api/v1/import/consignments/{id}/costs` | POST | Record an actual cost against a cost factor | P03, M52 |
| `/api/v1/import/consignments/{id}/landed-cost` | GET | Provisional or final landed unit cost per line | **M15**, P03 |
| `/api/v1/import/consignments/{id}/finalise` | POST | Publish the final cost and trigger revaluation | P03 |
| `/api/v1/import/hs-codes/{part}` | GET/POST | Read or change an HS classification (controlled) | P03, M37 |
| `/api/v1/import/tariff` | GET | Rate schedule for an HS code on a given date | P03, M16 |
| `/api/v1/import/lead-times` | GET | Import lead time by stage, supplier, mode and route | **M43**, P03 |
| `/api/v1/import/cycle-time` | GET | Clearance cycle time and demurrage exposure | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R19 Procurement Officer | C R U | Import consignments, documents, shipments, agent instruction |
| R26 Finance Manager | R U A | LC applications, cost reconciliation, duty variance resolution, final cost approval |
| R27 Finance Officer | C R U | Cost capture, document registration, bank charge entry |
| R03 Chief Financial Officer | R A | All; approves LC above threshold, duty variance acceptance, final cost publication above threshold |
| R17 Inventory Manager | R | Landed cost, expected arrivals, provisional-cost exposure |
| R20 Warehouse Operative | R | Expected inbound consignments only |
| R32 Quality Manager / ISO Coordinator | R U | Restricted and dangerous-goods classification and permits |
| R05 Operations Director | R | Cycle time and supply continuity |
| R15 Logistics Coordinator | R U | Inland movement from port to warehouse |
| R33 IT / System Administrator | R U | Tariff schedule loading, adapter configuration; no transactional or approval rights |
| R38 External Party (C&F agent, freight forwarder) | R U | **Own assigned consignments only**, minimum necessary data (P05, EA-01, EA-07) |

**Import Officer function.** Exercised as an elevated grant on R19 covering LCA lodgement, LC
application, Bill of Entry production, agent instruction and provisional cost publication.

**Field-level restrictions.** Unit cost and landed cost follow the `05-04` §5 restriction on
`unit_cost` and `total_cost`. The C&F agent and forwarder see quantities, weights,
classifications and their own charges — never 1000FiX's purchase price, margin or other
suppliers' rates (EA-02).

**Segregation of duties.**
- The user who records an assessed duty figure cannot be the sole approver of a duty variance acceptance.
- The user who captures a cost document cannot approve the final landed-cost publication above the value threshold.
- LC application and LC approval are separate roles (`05-04` §7 authority bands apply to LC value).
- HS reclassification requires an approver distinct from the classifier.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Import pipeline** | Procurement Manager, Inventory Manager | Real time | Every consignment by state, with ETA, days in stage, blocking issues and value |
| **Import clearance cycle time** | Procurement Manager, Operations Director | Monthly | Stage-by-stage elapsed time, against the **−20%** target; bottleneck analysis by agent, port and mode |
| **Landed cost accuracy** | CFO, Procurement Manager | Monthly | Provisional versus final variance per consignment and per line, against the **within 2%** target |
| Provisional cost exposure | CFO, Inventory Manager | Weekly | Lines still provisional, their age and value; **against the < 1% beyond 30 days target** |
| **Landed cost composition** | CFO, Procurement Manager, Inventory Manager | Monthly | Cost build-up by factor — invoice, freight, insurance, duty, clearing, port, bank, inland — as a percentage of invoice value, by category and origin |
| Duty variance register | CFO, Finance Manager, Internal Audit | Monthly | Assessed versus computed, variances, causes, resolutions, recovered amounts |
| **Recoverable tax register** | CFO, M51 | Monthly | VAT, AT and AIT computed at import, published for credit, and claimed — with any gap |
| Demurrage and detention | Procurement Manager, CFO | Monthly | Incurred amount, days, attributed cause, avoidable share |
| LC and facility utilisation | CFO, Treasury (M50) | Monthly | LCs open, value, facility utilisation, margin held, expiring instruments |
| FX exposure and outcome | CFO, Treasury | Monthly | Committed versus settled rates, exchange differences by consignment and currency |
| Import lead time for planning | Inventory Manager, Demand Planner | Quarterly | Mean and variability by supplier, mode, origin and route — the M43 input |
| **C&F agent and forwarder scorecard** | Procurement Manager, M42 | Quarterly | Clearance cycle time, cost accuracy, query rate, document quality, bill variance |
| Compliance status | CFO, Procurement Manager, Internal Audit | Quarterly | IRC and permit validity, document completeness rate, retention compliance, open customs queries |
| HS classification register | Procurement Manager, Internal Audit | Annually | Classifications, rationales, changes and their duty impact |
| Import spend and origin analysis | CFO, Procurement Manager | Quarterly | Value by origin country, supplier, mode and category; concentration and route dependency |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8+ Target |
|---|---|---|---|---|
| — | **Import clearance cycle time** *(arrival → warehouse receipt)* | unmeasured | baseline −10% | **baseline −20%** |
| — | **Landed cost accuracy** *(final vs provisional variance)* | unmeasured | within 4% | **within 2%** |
| — | Provisional-cost lines outstanding beyond 30 days | n/a | < 5% | **< 1%** |
| — | Imported stock valued at true landed cost | 0% | **100%** | **100%** |
| — | Duty variances detected before payment | 0% | 95% | **100%** |
| — | Recoverable tax published to M51 and claimed | unknown | 95% | **100%** |
| — | Demurrage as % of import cost | unmeasured | < 1.5% | **< 0.5%** |
| — | Document checklist complete before B/E lodgement | unmeasured | 95% | **100%** |
| — | Consignments delayed by a document gap | unmeasured | < 8% | **< 2%** |
| — | Import lead-time variability (standard deviation, days) | unmeasured | baselined | **−25%** |
| — | LC amendments per consignment | unmeasured | < 0.4 | **< 0.2** |
| — | Cost documents reconciled within tolerance | unmeasured | 90% | **97%** |
| — | IRC or permit lapses causing a supply interruption | unknown | **0** | **0** |
| — | Landed-cost estimate accuracy at order *(estimate vs final)* | n/a | within 8% | **within 4%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §7 names **import clearance cycle time (−20%)** and
> **landed cost accuracy (within 2%)** as the category KPIs owned by M44. Neither has a canonical
> `KPI-0nn` identifier in `06-02` §2.6, which stops at KPI-049. **Allocation of identifiers for
> all fourteen metrics above is an audit action.**

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `stock_landed_costs` — landed-cost document, split methods, application to receipt layers | 12% |
| L2 | OCA `purchase_landed_cost`, `stock_landed_costs_delivery` — cost anticipated from the purchase order, delivery-based allocation | 10% |
| L5 | `cd_import_order`, `cd_trade_compliance`, `cd_customs_clearance`, `cd_landed_cost` | 78% |

The custom share is high because nothing in the open-source ecosystem models a Bangladeshi
import: the LCA form, the cascading NBR duty computation, the recoverable/inventoriable
distinction, provisional-to-final revaluation and the C&F agent workflow have no equivalent.
Odoo and OCA supply the allocation mechanics only.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 4 identifiers below are claimed by another module: **CD-071** also claimed by M55; **CD-074** also claimed by M55. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-074 | `cd_import_order` — import consignment lifecycle, proforma reconciliation, incoterm model, shipment and document register, insurance, demurrage tracking, cycle-time capture | Odoo module | 5 PW |
| **CD-155** | `cd_trade_compliance` — HS classification with change control, tariff rate schedule, restriction and permit checks, IRC monitoring, country of origin, document checklist engine | Odoo module | 4 PW |
| **CD-156** | `cd_customs_clearance` — LCA form, letter of credit lifecycle with amendments and discrepancies, alternative payment routes, bank charge capture, FX exposure, Bill of Entry production, assessment tracking, **duty computation and independent verification**, C&F agent instruction and reconciliation | Odoo module + service | 6 PW |
| CD-071 | `cd_landed_cost` — cost factor model, allocation by value/weight/volume/quantity/direct, **recoverable/inventoriable separation**, provisional and final publication, revaluation and COGS adjustment, estimation service | Odoo module + service | 4 PW |

> CD-071 and CD-074 are reallocated from M15 and M16 respectively, where `02-05` §5.2 originally
> placed `cd_landed_cost` and `cd_import_order`. CD-155…156 are claimed from the extension block
> for modules M31–M67. **All CD IDs remain provisional** pending the unified CD register
> required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M16 Procurement (W3) | The cross-border purchase order is the trigger; M16 must hand over |
| M42 Supplier Relationship (W4) | Freight forwarders, C&F agents and insurers must be qualified before instruction (BRU-ITC-12) |
| M15 Inventory (W2) | The recipient of landed cost and the subject of revaluation |
| M19 Financial Accounting (W3) | Cost, duty, exchange-difference and revaluation postings |
| M52 Accounts Payable (W3) | Payment of supplier, bank, agent, forwarder and port |
| **M50 Treasury (W3)** | LC facility, margin deposits and exchange rates |
| **M51 Tax & Regulatory Compliance (W4)** | The recipient of recoverable VAT, AT and AIT |
| M41 Warehouse (W3) | Receipt of cleared consignments |
| M24 Documents (W3) | Five-year retention |
| M43 Demand Planning (W6) | Same wave; M44 supplies lead-time actuals and M43 supplies consolidated import demand — sequence M44's cycle-time capture ahead of M43's lead-time modelling within the wave |

> **The W3–W5 interim, and why it needs a decision.** M16 goes live in W3 and will place
> cross-border orders immediately, but M44 does not arrive until W6. For three waves, imported
> parts will be received with **invoice price as unit cost** — precisely the error M44 exists to
> correct — and M15 will hold provisional values it has no mechanism to finalise.
>
> Two mitigations are available and one must be chosen (Q-01):
> **(a)** a **W3 landed-cost slice** — the cost-factor model, manual cost capture, allocation,
> and the provisional/final publication to M15 (≈4 PW of CD-071 pulled forward), leaving
> compliance, LC and duty automation to W6; or
> **(b)** accept invoice-price valuation for three waves and **retrospectively revalue** when
> M44 lands, which is possible because M15 flags provisional cost — but which leaves margin
> reporting wrong for the intervening period and creates a large one-time revaluation.
>
> **Option (a) is recommended.** The category risk register already rates "import duty and
> clearing costs never reach unit cost" as high-impact, and three waves is long enough for that
> impact to be material.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open letters of credit | Current only, ~5–20 | `fix.letter.of.credit` | W6 cutover |
| In-flight consignments | Current only | `fix.import.consignment` | W6 cutover |
| HS classifications | Held by the C&F agent, not by 1000FiX | `fix.hs.classification` | **W6 — collected and authored, not migrated** |
| NBR tariff schedule | Full schedule for relevant chapters | `fix.tariff.rate` | W6, loaded from the published schedule |
| Historical import costs and cycle times | Fragmentary; agent files | `fix.import.cycle.time` (reference only) | W6, best-effort |
| IRC, permits and registrations | Held on paper | `fix.import.permit` | W6 |
| C&F agent and forwarder agreed tariffs | Informal | `fix.supplier.agreement` (M42) | W4–W6 |

> **Position on HS classification.** The most significant data task in M44 is not a migration —
> it is the **collection and internal ratification of the HS classification for every imported
> part**. Today those codes live with the C&F agent, are not visible to 1000FiX, and are not
> validated. Building the classification register is a multi-week effort requiring the agent's
> cooperation, and it is on the critical path for the duty-verification capability that gives
> M44 much of its value. It should begin **before W6 build**, not during it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every imported part in stock is valued at a landed cost, never at invoice price | Full-population assertion query |
| AC-02 | **Recoverable taxes — VAT, AT and AIT — never appear in any landed cost or inventory value** | Negative test plus a full-population assertion on the valuation extract |
| AC-03 | Recoverable amounts are published to M51 for every cleared consignment | Reconciliation of M44 computations against M51 receipts |
| AC-04 | The duty cascade computes correctly for a test matrix covering zero and non-zero CD, RD, SD, VAT, AT and AIT combinations | Test matrix verified against manually computed Bills of Entry |
| AC-05 | Duty is computed using the rate schedule in force on the Bill of Entry date | Time-shifted test with two rate versions |
| AC-06 | A duty variance beyond tolerance blocks payment until investigated and resolved | Negative test |
| AC-07 | Cost-factor allocation sums exactly to the factor total, with rounding assigned deterministically | Arithmetic test over a 500-line consignment with 12 factors |
| AC-08 | Provisional landed cost is published at receipt and M15 flags the stock provisional | Integration test with M15 |
| AC-09 | Final cost publication revalues remaining stock and raises a COGS adjustment for consumed quantities | Scripted scenario with partial consumption before finalisation |
| AC-10 | Fewer than 1% of lines remain provisional beyond 30 days at Wave 8 | Six months of measurement |
| AC-11 | Landed cost accuracy — final versus provisional — is within 2% at Wave 8 | Six months of measurement |
| AC-12 | A Bill of Entry cannot be lodged with an incomplete mandatory document checklist | Negative test |
| AC-13 | A restricted item cannot be released without its valid permit attached | Negative test |
| AC-14 | A consignment cannot progress past proforma confirmation with a lapsed IRC or permit | Negative test |
| AC-15 | An LC application exceeding the M50 facility is blocked | Negative test |
| AC-16 | A forwarder or C&F agent not active in M42 cannot be instructed | Negative test |
| AC-17 | The landed-cost estimation service returns in ≤ 300 ms at p95 for a 50-line estimate and is consumed by M16's bid comparison | Performance and integration test |
| AC-18 | Import lead-time actuals are recorded at every stage, are not editable, and reach M43 | Negative test plus integration test |
| AC-19 | LCA forms, LC documents and Bills of Entry are retained immutably for five years with hash verification | Retention configuration audit |
| AC-20 | An HS reclassification requires an approver distinct from the classifier and records a rationale | Negative test |
| AC-21 | A duty computation from twelve months prior is reproducible from its stored inputs | Historical recomputation test |
| AC-22 | Clearance cycle time improves 20% against the W6 baseline | Six months of measurement |
| AC-23 | Procurement Manager and CFO sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is the W3 landed-cost slice approved** (≈4 PW of CD-071 pulled forward), or is retrospective revaluation at W6 accepted for three waves of imports? | CFO / CTO | W3 minus 3 months |
| Q-02 | **Who collects and ratifies the HS classification for every imported part**, and will the C&F agent cooperate? This is on the critical path. | Procurement Manager | W6 minus 6 months |
| Q-03 | Which C&F agents and freight forwarders are used, on what agreed tariff, and will they accept instruction and reconciliation through the system? | Procurement Manager | W6 minus 4 months |
| Q-04 | Is direct ASYCUDA World lodgement available to 1000FiX as an importer, or is agent-mediated filing the only practical route? | Procurement Manager / CFO | W6 design |
| Q-05 | Which authorised dealer banks are used, and do they offer any electronic channel for LCA and LC status, or is it entirely document-based? | CFO / Treasury | W6 design |
| Q-06 | What is the duty-variance tolerance above which payment is blocked — a percentage, an absolute amount, or both? | CFO | W6 build |
| Q-07 | Are import VAT, AT and AIT fully recoverable in 1000FiX's circumstances, or are some partly non-recoverable? **This single answer determines what enters inventory value.** | CFO / Tax adviser | **W6 minus 3 months — and it affects the W3 slice** |
| Q-08 | What is the cost-factor tolerance for reconciling agent, forwarder and port bills? | Finance Manager | W6 build |
| Q-09 | Does 1000FiX hold or need a bond facility or duty-drawback entitlement for any part category? | CFO | W6 design |
| Q-10 | Do any brand partners ship consignment stock cross-border, and if so, who is the importer of record and who bears the duty? **This interacts directly with M15's consignment ownership class.** | CCO / CFO | W6 design |
| Q-11 | What is the FX policy — is exposure hedged, and does M44 need to record hedge references against a consignment? | CFO / Treasury | W6 build |
| Q-12 | Is the tariff schedule obtainable in a machine-readable form, and who owns keeping it current when NBR revises it? | Procurement Manager / IT Administrator | W6 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (M44 definition), §6 (import and landed-cost ownership), §7
(clearance cycle time, landed cost accuracy), §9 (the margin-overstatement risk) ·
`M15_Spare_Parts_and_Inventory_Management.md` §5.6 FR-INV-042, §9 BRU-INV-15 (the reciprocal
provisional-cost rule) · `M16_Procurement_and_Strategic_Sourcing.md` §5.3 FR-PRO-023, §9
BRU-PRO-14 (the cross-border hand-off) · `M42_Supplier_Relationship_and_Performance.md`
(forwarder, agent and insurer qualification; Q-11 there is the reciprocal of Q-03 here) ·
`M43_Demand_Planning_and_Replenishment.md` §5.3 FR-DPL-019 (import lead-time modelling) ·
`M41_Warehouse_Management.md` §5.2 (receipt against a cleared consignment) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 (CD-071, CD-074), §8.3 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5, §7, §8 EA-01/EA-02/EA-07 ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` (retention, AS-10)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-INV-011, BR-SCM-005 ·
`1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships (imported genuine OEM parts)

**External benchmark and regulatory basis**
[Bangladesh Customs (NBR) — customs clearance procedure](http://www.bangladeshcustoms.gov.bd/index.php/trade_info/customs_clearance) —
Bill of Entry filed through **ASYCUDA World** in Single Administrative Document format by the
importer or C&F agent; L/C required for release of goods ·
[Bangladesh Customs — import procedures](https://bangladeshcustoms.gov.bd/procedures/p_import/123) ·
[Bangladesh Bank Foreign Exchange Guidelines, Vol. 1, Ch. 7 §II — letters of credit and remittances against imports](https://www.bb.org.bd/aboutus/regulationguideline/foreignexchange/feguidevol1/7_b.pdf) —
LCA forms retained by authorised dealers for five years ·
[Bill of Entry Bangladesh — field-by-field guide](https://rakibhassan.eu/bill-of-entry-bangladesh-guide/) ·
[Import VAT and duty calculation in Bangladesh](https://rakibhassan.eu/import-vat-tax-calculation-bangladesh/) —
the cascading AV → CD → RD → SD → VAT → AT → AIT sequence and the 1% landing charge ·
[Bangladesh Customs — assessable value](http://bangladeshcustoms.gov.bd/nep/home/enquiry/81/) ·
SAP S/4HANA Global Trade Services and Import Management — classification as controlled master
data; planned versus actual landed cost ·
Oracle Fusion Cloud Landed Cost Management — trade operations, charge names, cost factors and
allocation bases · Microsoft Dynamics 365 Landed Cost — the voyage as the unit of cost
accumulation, estimated versus actual variance ·
[Odoo 19 landed costs — split methods and landed-cost products](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/landed_costs.html) ·
[OCA `purchase_landed_cost`](https://apps.odoo-community.org/modules/purchase_landed_cost) ·
[OCA `stock_landed_costs_delivery`](https://apps.odoo-community.org/shop/stock-landed-costs-delivery-10039)

---

*Module M44 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
