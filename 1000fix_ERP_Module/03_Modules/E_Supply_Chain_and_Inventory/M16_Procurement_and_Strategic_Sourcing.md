---
id: FIX-ERP2-M16
module_id: M16
module_code: PRO
module_name: Procurement & Strategic Sourcing
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Procurement Manager
system_owner: Supply Chain Squad
priority: P1
wave: W3
---

# M16 — Procurement & Strategic Sourcing
### Category E · Code `PRO` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M16 |
| **Module code** | `PRO` *(the v1.0 code `SCM` is retired — see `02-02` §5)* |
| **Category** | E — Supply Chain & Inventory |
| **Status** | Existing (re-scoped in v2.1 — supplier relationship moved to M42, import and landed cost to M44, planning to M43) |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Procurement Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo `purchase` · L2 OCA `purchase-workflow` · L5 custom requisition, sourcing-event and match engines |
| **Custom modules** | `cd_requisition`, `cd_rfq`, `cd_sourcing_event`, `cd_three_way_match` |
| **Requirement range** | FR-PRO-001 … FR-PRO-038 |
| **Requirement count** | **38** *(measured — supersedes the 32 estimate in `02-02`)* |
| **Effort estimate** | **18 person-weeks** *(measured — supersedes the 16 PW estimate)* |
| **Depends on** | **M42 Supplier Relationship** · M15 Inventory · M37 Catalogue · M33 Party Master · M19 Financial Accounting · M52 Accounts Payable · M29 Identity · M28 Integration |
| **Depended on by** | M15, M41, M42, M43, M44, M52, M19, M23, M25, M45, M47, M31, M18, M46, M66 |

---

## 2. Purpose

M16 owns **the transaction of buying**: someone needs something, it is approved, it is sourced,
an order is placed, goods arrive, and the invoice is proved correct before anyone pays it.

Today that chain runs on phone calls. A branch runs out of a part; the store keeper calls
procurement; procurement calls a supplier they have used before; the part arrives with a
delivery challan; an invoice appears weeks later and is paid because someone remembers agreeing
to it. There is no requisition, no competitive quotation, no record of the agreed price, and no
mechanical check that what was invoiced is what was ordered and what was received.

The result is not usually fraud. It is quieter than that: prices drift upward unchallenged,
the same part is bought at three prices in the same month, urgent buying becomes the norm
rather than the exception, and the Company cannot answer what it spends with whom.

M16 makes the chain explicit and auditable, and it enforces one structural control that
changes the economics of buying: **no purchase order may be raised to a supplier M42 has not
qualified and activated.**

### Why It Exists

Three things force procurement to become a system rather than a practice.

**Volume.** 10,000 SKUs across 51+ branches, plus tools, consumables, facilities and IT.
Replenishment alone will generate thousands of requisitions a year once M15 makes consumption
visible.

**Money.** Parts are the largest cost of goods sold in a repair business. A 3–5% improvement
in purchase price on the parts base is worth more than most operational efficiency programmes,
and it is unreachable without competitive sourcing and price history.

**Control.** SOD-02 in `05-04` — the same person must not raise a purchase order, receive the
goods and approve the invoice. That control cannot exist without a system that knows which
document is which.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-SCM-002 | "Purchase requisition with approval workflow" |
| ERP BRD BR-SCM-003 | "Auto-generate purchase orders from approved replenishment alerts" |
| ERP BRD BR-SCM-004 | "Record goods receipt with quality inspection before stocking" |
| ERP BRD BR-SCM-005 | "Perform 3-way matching: PO + GRN + Vendor Invoice" |
| ERP BRD BR-SCM-006 | "Manage return-to-vendor (RTV) for defective or incorrect parts" |
| ERP BRD BR-INV-006 | "Automatically generate replenishment alerts when stock falls below configured minimum levels" — the primary demand signal into M16 |
| ERP BRD BR-INV-012 | "Goods receipt with quality inspection step before stocking" |
| ERP BRD BR-INV-014 | "Track defective parts returns to vendor (RTV)" |
| `05-04` §7 Approval Authority Matrix | Purchase requisition thresholds: ≤ BDT 50,000 Inventory Manager · ≤ BDT 500,000 Procurement Manager · ≤ BDT 2,000,000 CFO · above that CEO |
| `05-04` §6 SOD-01, SOD-02 | Create vendor + approve vendor invoice is blocked; raise PO + receive goods + approve invoice is blocked in combination |
| `_CATEGORY_OVERVIEW.md` §4 | The M16/M42 split: M16 owns the daily transaction, M42 owns the quarterly relationship |
| `_CATEGORY_OVERVIEW.md` §7 | Targets: PO cycle time < 24 h · three-way match exceptions < 5% · goods inspection rejection < 2% · emergency purchases < 8% of spend |
| Exec Summary §6.2 | Inventory cost reduction BDT 34 lac/year depends on buying the right quantity at the right price |

---

## 3. Scope Boundary

> **The M16/M42 boundary is the second most important in Category E.** M16 is *transactional
> and daily*; M42 is *relational and quarterly*. The test: if the artefact has a document
> number and a value, it is M16. If it describes what kind of supplier this is, it is M42.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Demand intake from every source: replenishment alerts, branch requests, job-driven backorders, project and capital demand, facilities and IT demand |
| 2 | Purchase requisition with line detail, cost centre, justification and budget reference |
| 3 | Requisition approval routing against the authority matrix, with delegation and escalation |
| 4 | Requisition consolidation across branches into a single sourcing or ordering event |
| 5 | Request for quotation to multiple qualified suppliers, with a defined response window |
| 6 | Bid comparison on a normalised basis — price, lead time, warranty, MOQ, incoterm and landed estimate |
| 7 | Award decision with recorded rationale, including the reason for not choosing the lowest price |
| 8 | Reverse-auction and sealed-bid sourcing events for high-value categories |
| 9 | Purchase order creation, amendment, cancellation, acknowledgement and close |
| 10 | Blanket and call-off orders against a framework agreement held by M42 |
| 11 | Catalogue-based (punchout-style) ordering from agreed price lists |
| 12 | Purchase order dispatch to the supplier and status tracking through P05 Vendor Portal |
| 13 | Expediting: chasing acknowledgement, dispatch and overdue delivery |
| 14 | Goods receipt initiation and reconciliation, including partial, over- and under-delivery |
| 15 | Inbound quality inspection outcome capture and acceptance decision |
| 16 | **Three-way match** — purchase order, goods receipt note and vendor invoice — with tolerance bands and exception routing |
| 17 | Return to vendor: RMA raising, dispatch coordination, credit note tracking and closure |
| 18 | Purchase price history, price variance analysis and price-change alerting |
| 19 | Emergency and spot purchase with post-hoc approval, tracked as a controlled exception |
| 20 | Non-stock and services procurement: subcontract repair, facilities, IT, marketing |
| 21 | Spend analysis by category, supplier, branch and business line |
| 22 | Procurement compliance: maverick-spend detection, single-source reporting, contract-coverage measurement |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Supplier qualification, onboarding, activation and de-activation | **M42** | A supplier's right to be traded with is a relationship decision, not a transaction |
| Supplier contract, framework agreement, rebate and consignment terms | **M42** | The agreement governs many orders; M16 calls off against it |
| Supplier scorecard, risk assessment, development plan, category strategy | **M42** | Quarterly and strategic |
| Supplier master data record | **M42** (with **M33** for the party) | One supplier record, owned once |
| How much to buy and when — reorder point, safety stock, forecast | **M43** Demand Planning | M16 buys the quantity the plan asks for; it does not decide the quantity |
| Import documentation, LC, shipping, customs, duty, clearing | **M44** | An imported PO is a domestic transaction until it crosses a border, at which point M44 takes over |
| Landed cost calculation and allocation | **M44** | M16 knows the purchase price; M44 knows the true cost |
| Stock quantity, ownership class, valuation | **M15** | M16 causes stock to exist; M15 records it |
| Physical receiving, inspection execution, put-away | **M41** (at WMS locations) / **M15** (elsewhere) | M16 owns the receipt as a *document*; the floor owns it as an *event* |
| Inspection standard, sampling plan, non-conformance record | **M23** Quality | M16 records the outcome; M23 defines the test |
| Vendor invoice posting, payment run, ageing, remittance | **M52** Accounts Payable | M16 proves the invoice correct; M52 pays it |
| Journal posting of GRN accruals, purchase price variance | **M19** Financial Accounting | Only Category G posts |
| VAT, withholding tax and Mushak treatment of a purchase | **M51** Tax & Regulatory Compliance | Tax is a compliance domain |
| Budget definition and budget-holder accountability | **M54** Cost Accounting, Budgeting & FP&A | M16 checks against the budget; M54 owns it |
| Physical transport of purchased goods | **M03** Logistics | — |
| Tools and test equipment as assets after receipt | **M45** | M16 buys them; M45 owns them thereafter |
| Marketplace seller sourcing of labour | **M12** | Buying capacity is not buying goods |

### 3.3 Shared Concepts

| Concept | M16's Role | Owning Module |
|---|---|---|
| Supplier | Transacts with; reads qualification status as a gate | M42 (with M33) |
| Supplier agreement / price list | Calls off against; reads pricing | M42 |
| Part | Buys; reads specification, MOQ and approved-source list | M37 |
| Purchase requisition | **Owns** | M16 |
| Purchase order | **Owns** | M16 |
| Goods receipt note | **Owns** the document; M41/M15 own the physical event | M16 |
| Three-way match | **Owns** | M16 |
| Vendor invoice | Matches; does not post or pay | M52 |
| Return to vendor | Raises the RMA and tracks the credit; M15 quarantines, M03 moves | M16 / M15 / M03 |
| Import order | Raises the PO; hands the cross-border execution to M44 | M16 / M44 |
| Supplier performance data | **Produces** the delivery and quality facts; M42 interprets them | M16 / M42 |
| Spend | Owns transactional spend; M54 owns budget and cost accounting | M16 / M54 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Purchasing (MM-PUR)** | Purchase requisition, source determination, source list, quota arrangement, RFQ/quotation, PO, outline agreement with call-off, goods receipt, invoice verification with tolerance keys | **Tolerance-key-based invoice verification is the direct model for our three-way match**: match within tolerance auto-approves; outside tolerance blocks and routes. Also adopted: the source list (approved sources per part) and outline agreements with call-off | SAP's release-strategy configuration matrix and quota arrangements — over-engineered for a single-country, single-entity buyer |
| **Oracle Fusion Cloud — Procurement** | Self-service requisitioning, approval routing by spend and risk, negotiation (RFQ/auction), agreements, receipt accounting, match options and tolerance percentages | **Approval segmentation by spend threshold and risk level, with low-value routine requisitions auto-approved.** Best practice is explicit that more than three approval tiers create friction rather than control — our matrix has four, mandated by `05-04` §7, and we compensate by auto-approving low-value catalogue lines | Oracle's full negotiation module depth; we implement RFQ and sealed-bid, and reverse auction only for high-value categories |
| **Microsoft Dynamics 365 — Procurement and Sourcing** | Purchase requisition workflow, purchase agreements, vendor collaboration portal, receipt and invoice matching | The **vendor collaboration portal** pattern — a supplier confirms the PO, uploads dispatch details and submits the invoice themselves. Delivered as P05 | — |
| **SAP Ariba / Coupa (P2P practice)** | Guided buying, catalogue-based purchasing, maverick-spend control, first-time match rate as the headline metric | **Two ideas adopted directly.** First, *guided buying*: the easiest path must be the compliant path, because maverick spend is defeated by convenience, not by policy. Second, **first-time match rate as the primary procurement health metric** — best-in-class is 90%+, and our < 5% exception target sits inside that | Full spend-management suite; the cost is unjustifiable at our spend volume |
| **P2P automation practice (2025–26)** | Three-way match automation with tolerance thresholds, exception root-cause elimination (missing GRN, poor PO management, supplier data gaps) | **Root-cause elimination rather than exception-handling capacity.** We instrument *why* a match fails, not merely that it failed, and report the causes monthly | AI-driven invoice ingestion at W3; deferred to M52 and M26 |
| **Odoo 19 CE `purchase` + OCA `purchase-workflow`** | RFQ, vendor pricelists, POs, reordering rules, three-way matching, receipt control, requisition modules | The transactional substrate. Odoo 19 covers RFQ→PO→receipt→bill natively and OCA adds requisition, approval and tender workflow | Odoo's native reordering rules as the *planning* mechanism — that responsibility belongs to M43; M16 consumes its output |

**Design position.** Four deliberate differences.

First, **qualification is a hard gate, not a warning**. In most ERPs a buyer can create a
vendor and raise an order in the same session. In 1000FiX that path does not exist: M42 must
have qualified and activated the supplier before M16 will accept it on a purchase order. This
is the structural defence against the two frauds the authority matrix already anticipates
(SOD-01) and against the counterfeit-parts risk that threatens brand authorisation.

Second, **the requisition is mandatory and the emergency path is a measured exception, not a
loophole**. Every purchase begins as a requisition. Emergency purchase exists — a job-stopping
part at 9pm is a real event — but it creates a requisition retrospectively, requires named
post-hoc approval, and is counted. The target is **under 8% of spend**; a business that cannot
see its emergency spend cannot reduce it.

Third, **procurement produces supplier performance facts but does not judge them**. Every
receipt records promised versus actual date, quantity and inspection outcome. Those facts flow
to M42, which owns the scorecard, the conversation and the consequence. This prevents the
common failure where the buyer who chose the supplier also grades them.

Fourth, **the Bangladesh reality of the parts market is designed for, not designed around**.
A significant share of spend will be with local distributors on short lead times and informal
terms, and another significant share will be imports with 6–12 week lead times, LC exposure
and duty. M16 treats both as first-class: catalogue call-off for the former, and a clean
hand-off to M44 for the latter, at the moment the PO becomes an import.

---

## 5. Functional Areas & Features

### 5.1 Demand Intake & Purchase Requisition

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRO-001 | Multi-source demand intake | Accept purchase demand from M15 replenishment alerts, M43 planned orders, branch requests, job-driven backorders, project and capital demand, and facilities, IT and marketing requests | **P0** | L5 |
| FR-PRO-002 | Purchase requisition | Create a requisition with part or free-text lines, quantity, required-by date, delivery location, cost centre, business line, justification and budget reference | **P0** | L2/L5 |
| FR-PRO-003 | Approval routing | Route for approval against the authority matrix — ≤ BDT 50,000 Inventory Manager, ≤ BDT 500,000 Procurement Manager, ≤ BDT 2,000,000 CFO, above that CEO — with delegation, escalation on delay and full audit | **P0** | L2/L5 |
| FR-PRO-004 | Low-value auto-approval | Auto-approve requisition lines below a configured value that call off an existing agreement at an agreed price, to keep routine buying frictionless | P1 | L5 |
| FR-PRO-005 | Budget check | Check the requisition against the cost-centre budget held by M54 and warn or block per policy | P2 | L5 |
| FR-PRO-006 | Requisition consolidation | Consolidate open requisitions for the same part across branches into one sourcing or ordering event, preserving per-branch delivery destinations | P1 | L5 |
| FR-PRO-007 | Requisition tracking | Show the requester the live state of their request through to delivery, including the purchase order and expected date | P1 | L5 |
| FR-PRO-008 | Auto-requisition from replenishment | Generate a draft requisition automatically from an M15 replenishment alert or an M43 planned order, pre-populated with the recommended source and quantity (BR-SCM-003) | P1 | L5 |

### 5.2 Sourcing, RFQ & Award

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRO-009 | Approved-source list | Hold, per part, the suppliers approved to supply it, with priority, agreed price and lead time, sourced from M37 and M42 | **P0** | L5 |
| FR-PRO-010 | Sourcing decision | Determine whether a requisition is sourced by direct call-off against an agreement, by RFQ, or by a formal sourcing event, using value and category thresholds | **P0** | L5 |
| FR-PRO-011 | Request for quotation | Issue an RFQ to multiple qualified suppliers with a specification, quantity, delivery requirement and response deadline, through P05 or by email | **P0** | L1/L5 |
| FR-PRO-012 | Quotation capture | Capture supplier responses through P05 or by manual entry, with attachments and validity periods | **P0** | L1 |
| FR-PRO-013 | Normalised bid comparison | Compare bids on a common basis: unit price, lead time, warranty, minimum order quantity, payment terms, incoterm and — for imports — an estimated landed cost from M44 | **P0** | L5 |
| FR-PRO-014 | Award with rationale | Award to a supplier with a recorded rationale, mandatory where the award is not to the lowest price, and notify unsuccessful bidders | **P0** | L5 |
| FR-PRO-015 | Sealed bid and reverse auction | Run sealed-bid events where bids are invisible until the deadline, and reverse auctions for high-value repeat categories | P2 | L5 |
| FR-PRO-016 | Sourcing event audit | Retain the complete event record — invitees, responses, comparison, award, rationale, approver — as an immutable audit artefact | **P0** | L5 |

### 5.3 Purchase Orders & Agreements

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRO-017 | Purchase order | Create a purchase order from an award or a direct call-off, carrying part, quantity, agreed price, delivery location and date, incoterm, currency and payment terms | **P0** | L1 |
| FR-PRO-018 | **Qualification gate** | Reject creation of a purchase order to any supplier that M42 has not qualified and activated, for the category concerned, with no override below CEO authority | **P0** | L5 |
| FR-PRO-019 | Blanket order and call-off | Create call-off orders against a framework agreement held by M42, drawing down the committed value and quantity | P1 | L1/L5 |
| FR-PRO-020 | Catalogue ordering | Order directly from an agreed supplier price list at agreed prices, without an RFQ, for parts under contract | P1 | L1 |
| FR-PRO-021 | PO dispatch and acknowledgement | Send the purchase order to the supplier through P05 or email and record acknowledgement with a confirmed delivery date | **P0** | L5 |
| FR-PRO-022 | Amendment and cancellation | Amend or cancel a purchase order with version control, re-approval where value increases beyond tolerance, and supplier notification | **P0** | L5 |
| FR-PRO-023 | Import hand-off | Where a purchase order is cross-border, hand execution to M44 at confirmation, retaining the PO as the commercial record | **P0** | L5 |
| FR-PRO-024 | Expediting | Track acknowledgement, dispatch and delivery against commitments; chase overdue lines automatically and escalate by age and criticality | P1 | L5 |
| FR-PRO-025 | Supplier portal visibility | Give the supplier a portal view of their open orders, requested acknowledgements, delivery status, receipts and invoice status | P1 | L5 |

### 5.4 Receipt, Inspection & Three-Way Match

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRO-026 | Goods receipt note | Create a goods receipt against a purchase order, recording received quantity, date, condition and discrepancy, sourced from M41 at WMS locations and from M15 elsewhere (BR-SCM-004) | **P0** | L1/L5 |
| FR-PRO-027 | Partial, over and under receipt | Handle partial deliveries, over-delivery within tolerance, and short delivery with a decision to await, close short or cancel the balance | **P0** | L1/L5 |
| FR-PRO-028 | Inspection outcome | Record the inbound inspection result against the receipt, and accept, reject or conditionally accept the line (BR-INV-012) | **P0** | L5 |
| FR-PRO-029 | **Three-way match** | Match purchase order, goods receipt and vendor invoice on quantity, price and total, within configurable tolerance bands by category and value, auto-clearing matches and routing exceptions (BR-SCM-005) | **P0** | L5 |
| FR-PRO-030 | Match exception handling | Present each exception with its cause — price variance, quantity variance, missing receipt, unordered line, duplicate invoice — and route to the accountable role for resolution | **P0** | L5 |
| FR-PRO-031 | Match root-cause analytics | Classify and report exception causes monthly so that the causes are eliminated rather than merely processed | P1 | L5 |
| FR-PRO-032 | Invoice readiness release | Release a matched invoice to M52 for posting and payment, and never permit payment of an unmatched invoice without documented override | **P0** | L5 |

### 5.5 Returns, Claims & Commercial Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRO-033 | Return to vendor | Raise an RTV against a supplier with an RMA reference, dispatch coordination through M03, and tracking to credit note or replacement (BR-SCM-006, BR-INV-014) | **P0** | L5 |
| FR-PRO-034 | Credit recovery tracking | Age outstanding supplier credits, escalate overdue recoveries and report value at risk | P1 | L5 |
| FR-PRO-035 | Purchase price history and variance | Retain every price paid per part per supplier, alert on price increases beyond a threshold, and report purchase price variance against the agreed or standard price | P1 | L5 |
| FR-PRO-036 | Emergency and spot purchase | Permit an urgent purchase outside the normal path, creating the requisition retrospectively, requiring named post-hoc approval within a fixed window, and counting it toward the emergency-spend measure | **P0** | L5 |
| FR-PRO-037 | Non-stock and services procurement | Procure services and non-stock items — subcontract repair, facilities, IT, marketing — through the same requisition, approval and match discipline, with service-entry confirmation replacing goods receipt | P1 | L5 |
| FR-PRO-038 | Spend analysis and compliance | Analyse spend by category, supplier, branch, business line and buyer, and report maverick spend, single-source dependence and contract-coverage rate | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Qualification gate at write time** | The supplier-qualification check executes on the PO write path, not in the UI. A PO created by API, import or automation is subject to the identical gate |
| T-02 | **Match determinism and explainability** | A match result stores the tolerance set applied, the three document versions compared, and every field-level variance. Any match or exception can be explained months later without recomputation |
| T-03 | **Document version integrity** | Purchase orders are versioned. A match always states which PO version it matched, so a post-receipt amendment cannot silently validate a previously failing invoice |
| T-04 | **Duplicate invoice detection** | Invoice matching detects duplicates by supplier, invoice number, date and amount, including near-duplicates differing only in formatting |
| T-05 | **Approval integrity** | Approval decisions are immutable records carrying approver identity, authority basis, timestamp and the exact document version approved; a document changed after approval re-enters approval |
| T-06 | **Idempotent supplier-portal ingestion** | Acknowledgements, dispatch notices and invoices submitted through P05 are idempotent and replay-safe |
| T-07 | **Currency and rate handling** | Foreign-currency purchase orders store the currency, the rate source and the rate date; all money uses `Monetary` with explicit currency (AS-10) |
| T-08 | **Event emission via outbox** | Requisition, approval, award, PO, receipt, match and RTV state changes emit through the transactional outbox (AS-08) |
| T-09 | **SoD enforcement in the engine** | SOD-01 and SOD-02 are evaluated by the permission engine at role assignment and re-checked at transaction time; the runtime check is the authoritative one |
| T-10 | **Performance** | Requisition creation ≤ 400 ms; bid comparison across 8 suppliers × 50 lines ≤ 2 s; nightly match run over 5,000 invoices ≤ 20 min |
| T-11 | **Attachment integrity** | Quotations, acknowledgements, challans and invoices are hashed at capture and retained through M24 under the procurement retention class |
| T-12 | **Multi-entity readiness** | Requisitions, orders and matches carry `company_id`, `operating_unit_id` and `cost_center_id` (AS-03) |
| T-13 | **Bengali document rendering** | Purchase orders and RTV documents render correctly in Bengali and English for local suppliers (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M16 |
|---|---|---|
| **Branch store keeper** | Phones procurement and hopes | Raises a requisition; sees its approval, order and expected delivery date |
| **Procurement officer** | Works from memory and a phone; every purchase is bespoke | Works a queue of approved requisitions; routine lines call off automatically; effort concentrates on genuine sourcing |
| **Procurement manager** | Cannot say what the Company spends, with whom, or at what price | Spend by category and supplier; price history per part; emergency spend measured |
| **Inventory manager** | Buying decisions are made without them | Replenishment alerts become requisitions automatically; they approve within their authority |
| **Warehouse / branch receiving** | Signs a challan | Receives against a purchase order; discrepancies recorded at the point of receipt, not discovered at invoicing |
| **Finance / AP** | Pays invoices on the strength of someone's recollection | Receives only matched invoices; exceptions arrive with their cause already identified |
| **CFO** | Approves what is put in front of them | Authority matrix enforced by the system; SOD-02 mechanically impossible to breach |
| **Supplier** | Chases by phone for order status and payment | Sees orders, acknowledges, submits invoices and tracks payment status in P05 |
| **Internal audit** | Reconstructs procurement from documents | Complete, immutable requisition-to-payment trail |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Purchase price improvement** | Competitive RFQ on non-catalogue spend, price history visibility, price-increase alerting, consolidated volume across 51+ branches | A **3–5% reduction on the addressable parts spend**, the largest single component of the BDT 34 lac/year inventory benefit |
| **Emergency-spend reduction** | Emergency purchases measured and attributed; planned replenishment from M43 removes the cause | From an unknown baseline to **< 8% of spend**; emergency buying typically carries a 15–30% price premium |
| **Invoice processing cost** | Three-way match auto-clears the majority of invoices | Exception rate **< 5%**, against a manual process where effectively 100% require human review |
| **Duplicate and erroneous payment avoidance** | Duplicate detection, tolerance-bound matching, no payment without a match | Removes an entire class of quiet loss |
| **Credit recovery** | RTV tracked to credit rather than forgotten | Recovers value currently written off silently when defective parts are returned |
| **PO cycle time** | Requisition → approval → order automated end to end | **< 24 hours** from approved requisition to placed order, against days today; directly shortens the parts-wait component of TAT |
| **Inspection quality** | Rejection captured against the receipt and fed to the supplier scorecard | Rejection rate **< 2%**, achieved by supplier consequence rather than by inspection effort |
| **Working capital** | Payment terms enforced from the agreement rather than from the invoice | Extends effective days payable without damaging supplier relationships |
| **Audit and compliance** | Complete trail, enforced authority, mechanical SoD | Removes a recurring audit finding and supports BO-10 (zero compliance findings) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Fraud resistance** | SOD-01 and SOD-02 become structural rather than procedural. In a business buying from a fragmented local market, this is a material control |
| **Counterfeit defence** | The qualification gate means parts can only enter the estate through a supplier M42 has vetted — the first line of defence for 17+ brand authorisations |
| **ISO 9001 conformance** | Purchasing control, supplier evaluation and verification of purchased product are explicit clauses; M16 with M42 satisfies them with evidence |
| **Negotiating position** | A supplier who can see their own on-time and quality record, and knows the buyer can too, negotiates differently |
| **Institutional memory** | Price and sourcing history survives the departure of the person who remembered it |
| **Budget discipline** | Spend visible against cost centre and business line at the moment of commitment, not at month end |
| **Scalability** | Branch growth multiplies requisition volume; without M16 procurement headcount scales with branch count |

---

## 8. Lifecycle & State Models

### 8.1 Requisition-to-Order Lifecycle

```
   Demand: M15 replenishment · M43 planned order · branch request ·
           job backorder · project · facilities / IT
              │
        ┌─────▼──────┐
        │   DRAFT    │
        └─────┬──────┘
              │ submitted with cost centre, justification, budget ref
        ┌─────▼──────────┐
        │ PENDING        │  routed by the authority matrix (05-04 §7)
        │ APPROVAL       │  ── rejected ──► REJECTED (reason recorded)
        └─────┬──────────┘
              │ approved (or auto-approved under the low-value rule)
        ┌─────▼──────┐
        │  APPROVED  │
        └─────┬──────┘
              │ sourcing decision
      ┌───────┴────────┬─────────────────┐
      │                │                 │
┌─────▼─────┐   ┌──────▼──────┐   ┌──────▼───────┐
│ DIRECT    │   │  IN RFQ     │   │  SOURCING    │
│ CALL-OFF  │   │             │   │  EVENT       │
└─────┬─────┘   └──────┬──────┘   └──────┬───────┘
      │                │ bids received   │ sealed / auction closed
      │         ┌──────▼──────┐   ┌──────▼───────┐
      │         │  AWARDED    │◄──┤  AWARDED     │
      │         └──────┬──────┘   └──────────────┘
      │                │
      └────────┬───────┘
               │  ✖ blocked if supplier not qualified (BRU-PRO-02)
        ┌──────▼──────┐
        │ PO ISSUED   │
        └──────┬──────┘
               │ supplier confirms
        ┌──────▼──────────┐
        │ ACKNOWLEDGED    │  confirmed delivery date recorded
        └──────┬──────────┘
               │              ┌──────────────┐
               ├─────────────►│  OVERDUE     │ expediting, escalation
               │              └──────┬───────┘
        ┌──────▼──────────┐         │
        │ PARTIALLY       │◄────────┘
        │ RECEIVED        │
        └──────┬──────────┘
               │ all lines received (or balance closed short)
        ┌──────▼──────┐
        │  RECEIVED   │
        └──────┬──────┘
               │ invoice arrives, three-way match runs
      ┌────────┴────────┐
┌─────▼──────┐   ┌──────▼────────┐
│  MATCHED   │   │ MATCH         │ price · quantity · missing GRN ·
│            │   │ EXCEPTION     │ unordered line · duplicate
└─────┬──────┘   └──────┬────────┘
      │                 │ resolved
      │◄────────────────┘
┌─────▼──────┐
│  RELEASED  │ ──► M52 Accounts Payable
│  TO AP     │
└─────┬──────┘
      │ payment confirmed by M52, no open balance
┌─────▼──────┐
│   CLOSED   │
└────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | Pending approval | Cost centre, justification and required-by date present | Requester |
| Pending approval | Approved | Approver holds authority for the value band (`05-04` §7) | Approver per matrix |
| Approved | Direct call-off | An active agreement covers the part at an agreed price | System |
| Approved | In RFQ | Value or category threshold requires competition | Procurement officer |
| Approved | Sourcing event | High-value or strategic category | Procurement manager |
| Awarded / call-off | PO issued | **Supplier qualified and active in M42 for the category** (BRU-PRO-02) | Procurement officer |
| PO issued | Acknowledged | Supplier confirms with a delivery date | Supplier via P05 |
| Any open state | Overdue | Confirmed date passed without receipt | System |
| Acknowledged | Partially received / Received | Goods receipt posted by M41 or M15 | Receiving location |
| Received | Matched | PO, GRN and invoice agree within tolerance | System |
| Received | Match exception | Any variance outside tolerance | System |
| Match exception | Matched | Variance resolved and documented | Procurement officer / Finance |
| Matched | Released to AP | Match complete; no open quality hold | System |
| Released to AP | Closed | M52 confirms payment; no open RTV or credit | System |

### 8.2 Return-to-Vendor Lifecycle

```
  Defect found at inspection (M41/M23) or in service (M15 quarantine)
              │
        ┌─────▼──────┐
        │  RTV DRAFT │  part, quantity, evidence, original PO and GRN
        └─────┬──────┘
              │ raised with the supplier
        ┌─────▼──────────┐
        │ RMA REQUESTED  │
        └─────┬──────────┘
              │ supplier issues RMA reference
        ┌─────▼──────────┐
        │ RMA ISSUED     │
        └─────┬──────────┘
              │ consignment created (M03)
        ┌─────▼──────────┐
        │ DISPATCHED     │
        └─────┬──────────┘
              │ supplier confirms receipt
        ┌─────▼──────────┐
        │ AWAITING       │  ── aged ──► ESCALATED
        │ CREDIT         │
        └─────┬──────────┘
              │ credit note or replacement received
        ┌─────▼──────────┐
        │   CLOSED       │
        └────────────────┘
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PRO-01 | Every purchase begins as a requisition; a purchase order cannot exist without one | **H** | Procurement Manager |
| BRU-PRO-02 | **A purchase order cannot be raised to a supplier that M42 has not qualified and activated for the relevant category** | **H** | Procurement Manager |
| BRU-PRO-03 | Requisition approval follows the authority matrix in `05-04` §7 without exception | **H** | CFO |
| BRU-PRO-04 | The same user may not raise a purchase order, receive the goods and approve the invoice; any two are permitted, all three are blocked (SOD-02) | **H** | CFO |
| BRU-PRO-05 | The user who creates a supplier may not approve that supplier's invoice (SOD-01) | **H** | CFO |
| BRU-PRO-06 | A purchase order above the competitive threshold requires at least three quotations, or a documented single-source justification approved one level above the normal authority | **H** | Procurement Manager |
| BRU-PRO-07 | An award to other than the lowest-priced compliant bid requires a recorded rationale | **H** | Procurement Manager |
| BRU-PRO-08 | An invoice cannot be released for payment without a successful three-way match, or a documented override approved by the Finance Manager | **H** | CFO |
| BRU-PRO-09 | Match tolerance bands are configured by category and value and are changed only by the CFO | **C** | CFO |
| BRU-PRO-10 | A duplicate invoice — same supplier, number and amount — is rejected automatically | **H** | Finance Manager |
| BRU-PRO-11 | Goods are not accepted into available stock before the inspection result is recorded | **H** | Quality Manager |
| BRU-PRO-12 | An emergency purchase requires named post-hoc approval within 48 hours; failure to approve escalates to the CFO and blocks the requester from further emergency purchases | **H** | Procurement Manager |
| BRU-PRO-13 | A purchase order amendment increasing value beyond tolerance re-enters approval at the band of the new total | **H** | CFO |
| BRU-PRO-14 | A cross-border purchase order is handed to M44 at confirmation; M16 retains the commercial record and does not manage the shipment | **C** | Procurement Manager |
| BRU-PRO-15 | Purchase price paid is recorded against the part and the supplier on every receipt, and a price increase beyond the configured threshold raises an alert | **C** | Procurement Manager |
| BRU-PRO-16 | A defective or incorrect receipt is quarantined by M15 and an RTV is raised within the agreed return window; a missed window is reported as recoverable value lost | **H** | Procurement Manager |
| BRU-PRO-17 | Every receipt records the promised date against the actual date; these facts flow to M42 and are not editable by procurement | **H** | Supply Chain Director |
| BRU-PRO-18 | Purchase order cancellation after supplier acknowledgement requires Procurement Manager approval and supplier notification | **A** | Procurement Manager |
| BRU-PRO-19 | Services and non-stock purchases require a service-entry confirmation by the requesting cost-centre owner before match | **H** | Finance Manager |
| BRU-PRO-20 | Foreign-currency purchase orders record the rate source and rate date; the rate is never re-derived at match time | **C** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.purchase.requisition` | `fix_purchase_requisition` | The demand record | number, requester_id, origin (replenishment/plan/branch/job/project/facility), operating_unit_id, cost_center_id, business_line_id, required_by, budget_ref, state, total_estimated |
| `fix.purchase.requisition.line` | `fix_purchase_requisition_line` | One requested line | requisition_id, part_id, description, quantity, uom, estimated_price, delivery_location_id, justification, sourcing_route, po_line_id |
| `fix.purchase.approval` | `fix_purchase_approval` | Immutable approval record | document_type, document_id, document_version, approver_id, authority_band, decision, reason, decided_at, delegated_from |
| `fix.sourcing.event` | `fix_sourcing_event` | RFQ, sealed bid or auction | number, type, requisition_ids, category, invited_supplier_ids, opens_at, closes_at, state, award_rationale, awarded_supplier_id, approver_id |
| `fix.sourcing.bid` | `fix_sourcing_bid` | One supplier's response | event_id, supplier_id, submitted_at, validity_until, lines, incoterm, payment_terms, lead_time_days, attachments, normalised_total, rank |
| `fix.approved.source` | `fix_approved_source` | Approved supplier per part | part_id, supplier_id, priority, agreed_price, currency, lead_time_days, moq, agreement_id, effective_from, effective_to |
| `fix.purchase.order` | `fix_purchase_order` | The order | number, version, supplier_id, agreement_id, currency, rate, rate_date, incoterm, payment_terms, delivery_location_id, state, is_import, import_consignment_id, total, acknowledged_at, confirmed_delivery_date |
| `fix.purchase.order.line` | `fix_purchase_order_line` | One ordered line | po_id, part_id, description, quantity, unit_price, tax_code, required_by, received_qty, invoiced_qty, state |
| `fix.goods.receipt` | `fix_goods_receipt` | The receipt document | number, po_id, location_id, received_by, received_at, source (M41/M15/manual), challan_ref, state |
| `fix.goods.receipt.line` | `fix_goods_receipt_line` | One received line | grn_id, po_line_id, part_id, ordered_qty, received_qty, accepted_qty, rejected_qty, inspection_result, discrepancy_reason, lot_id, serials |
| `fix.invoice.match` | `fix_invoice_match` | The three-way match | supplier_invoice_ref, supplier_id, po_id, po_version, grn_ids, invoice_amount, matched_amount, tolerance_set, result, exception_type, exception_cause, resolved_by, released_to_ap_at |
| `fix.match.tolerance` | `fix_match_tolerance` | Tolerance configuration | category, value_band, price_tolerance_pct, price_tolerance_amount, quantity_tolerance_pct, effective_from, set_by |
| `fix.purchase.rtv` | `fix_purchase_rtv` | Return to vendor | number, supplier_id, po_id, grn_id, part_id, quantity, reason, evidence_ids, rma_reference, consignment_id, credit_expected, credit_received, state, aged_days |
| `fix.purchase.price.history` | `fix_purchase_price_history` | Price paid, per part per supplier | part_id, supplier_id, po_id, unit_price, currency, quantity, received_at, variance_vs_previous, variance_vs_agreement |
| `fix.emergency.purchase` | `fix_emergency_purchase` | Controlled exception record | requisition_id, po_id, raised_by, reason, job_id, post_hoc_approver_id, approved_at, within_window, value |
| `fix.spend.category` | `fix_spend_category` | Spend taxonomy | code, name, parent_id, competitive_threshold, sourcing_rule, owning_role |
| `fix.service.entry` | `fix_service_entry` | Confirmation for non-stock purchases | po_line_id, confirmed_by, confirmed_at, quantity_or_milestone, evidence_ids |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.supplier.profile`, `fix.supplier.qualification`, `fix.supplier.agreement` | M42 | Read; qualification status is a hard gate |
| `fix.party` | M33 | Read |
| `fix.catalogue.item` (specification, MOQ, approved-source hints) | M37 | Read |
| `fix.stock.quant`, `fix.stock.rtv` | M15 | Read; RTV initiation coordinated |
| `fix.replenishment.parameter`, `fix.planned.order` | M43 | Read as demand |
| `fix.wh.inbound`, `fix.wh.inbound.line` | M41 | Read as the physical receipt event |
| `fix.import.consignment`, `fix.landed.cost` | M44 | Read; hand off cross-border execution |
| `fix.checklist.template`, `fix.nonconformance` | M23 | Read the plan; raise the non-conformance |
| `fix.ap.invoice`, `fix.ap.payment.run` | M52 | Read status; release matched invoices |
| `fix.budget`, `fix.cost.center` | M54 / M30 | Read for budget check |
| `fix.document` | M24 | Store quotations, acknowledgements, challans, invoices |
| `fix.consignment` | M03 | RTV movement |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PRO-01 | M15 raises a replenishment alert, or M43 releases a planned order | Create a draft requisition pre-populated with the recommended source, quantity and price | Alert the procurement officer to create manually |
| AUT-PRO-02 | Requisition submitted | Route for approval by value band, notify the approver, escalate on delay, auto-approve where the low-value catalogue rule applies | Hold in pending and escalate after the SLA |
| AUT-PRO-03 | Requisition approved | Apply the sourcing decision rule and create the call-off, RFQ or sourcing event | Present the sourcing choice to the officer |
| AUT-PRO-04 | Open requisitions exist for the same part across branches | Propose consolidation into a single order with split delivery destinations | Proceed individually |
| AUT-PRO-05 | RFQ deadline reached | Close the event, normalise bids, produce the comparison, and notify the officer | Extend the deadline with notification |
| AUT-PRO-06 | Award confirmed | Verify supplier qualification with M42, create the purchase order, dispatch it, and request acknowledgement | **Hard block** if unqualified; notify Procurement Manager |
| AUT-PRO-07 | PO not acknowledged within the window | Chase the supplier, escalate by age, and flag on the supplier's delivery record for M42 | Alert only |
| AUT-PRO-08 | Confirmed delivery date passes without receipt | Move the line to overdue, expedite, notify the requester, and record the delay fact for M42 | Alert only |
| AUT-PRO-09 | PO confirmed and flagged cross-border | Hand execution to M44, creating the import consignment and linking it to the PO | Manual import creation |
| AUT-PRO-10 | Goods receipt posted by M41 or M15 | Update PO line receipt quantities, record promised-versus-actual, and trigger the inspection where a plan exists | Manual receipt reconciliation |
| AUT-PRO-11 | Inspection result recorded | Accept, reject or conditionally accept; on rejection, quarantine via M15, raise the RTV and notify M42 | Hold and escalate to Quality Manager |
| AUT-PRO-12 | Vendor invoice received (P05 or M52) | Run the three-way match against the tolerance set; auto-clear on match; classify and route on exception | Route to manual review |
| AUT-PRO-13 | Match succeeds | Release the invoice to M52 for posting and payment | Queue and retry |
| AUT-PRO-14 | Match fails | Classify the cause, route to the accountable role, notify the supplier where the cause is theirs | Escalate after the SLA |
| AUT-PRO-15 | Duplicate invoice detected | Reject automatically and notify the supplier and Finance | Hard reject |
| AUT-PRO-16 | RTV credit not received within the agreed window | Escalate to the procurement officer, then to the Procurement Manager, and add to the value-at-risk report | Report only |
| AUT-PRO-17 | Purchase price increases beyond the alert threshold | Notify the procurement officer and Procurement Manager with the price history | Report only |
| AUT-PRO-18 | Emergency purchase raised | Create the retrospective requisition, notify the approver, start the 48-hour clock, and count it toward the emergency-spend measure | Escalate to CFO at expiry |
| AUT-PRO-19 | Monthly | Produce spend analysis, maverick-spend detection, contract-coverage rate and match-exception root-cause analysis | Report generation retry |

---

## 12. Interfaces

### 12.1 Upstream — M16 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M42 Supplier Relationship** | Supplier qualification status, category approval, agreements, price lists, payment terms | REST (synchronous gate) |
| M15 Inventory | Replenishment alerts, stock positions, RTV initiation, consumption history | Events + REST |
| M43 Demand Planning | Planned orders, recommended quantities and timing | REST |
| M37 Catalogue | Part specification, MOQ, unit of measure, approved-source hints | REST |
| M41 Warehouse Management | Physical receipt and inspection confirmation at WMS locations | Events |
| M23 Quality | Inspection plans and sampling rules | REST |
| M44 Import | Import consignment status, cleared quantities, final landed cost | Events |
| M52 Accounts Payable | Vendor invoices for matching; payment confirmation | Events |
| M54 FP&A | Cost-centre budget availability | REST |
| M33 Party Master | Supplier party identity and addresses | REST |
| M01 / M31 | Job-driven part backorders | Events |
| M45 / M47 / M66 | Tools, facilities and IT demand | Commands |

### 12.2 Downstream — M16 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M42 Supplier Relationship** | Delivery performance facts, quality rejection facts, spend by supplier, price behaviour | Events + warehouse extract |
| M15 Inventory | Purchase orders as expected receipts; goods receipts as stock inflow; RTV dispatch | Commands + events |
| M41 Warehouse Management | Expected inbound lines for receiving | Events |
| M44 Import | The confirmed cross-border purchase order to be executed | Commands |
| M52 Accounts Payable | Matched invoices released for posting and payment | Events |
| M19 Financial Accounting | GRN accrual and purchase price variance signals | Events |
| M43 Demand Planning | Actual lead times, order status, supply commitments | Warehouse extract |
| M23 Quality | Inspection outcomes and supplier non-conformances | Events |
| M54 FP&A | Committed spend against budget | Events |
| M25 BI / M62 Data Platform | Requisition, order, receipt, match and spend facts | Warehouse extract |
| P05 Vendor Portal | Orders, acknowledgement requests, receipt status, invoice status | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `requisition.created` | requisition, lines, origin, cost centre, value | M54, M43 |
| `requisition.approved` | requisition, approver, authority band | M43, M54 |
| `requisition.rejected` | requisition, approver, reason | requester |
| `sourcing.event_opened` | event, category, invited suppliers, deadline | M42, P05 |
| `sourcing.awarded` | event, supplier, value, rationale | M42, M54 |
| `po.issued` | order, supplier, lines, value, currency, required date | M15, M41, M42, M52, P05 |
| `po.acknowledged` | order, supplier, confirmed delivery date | M15, M43 |
| `po.amended` | order, version, changes, re-approval | M15, M52, P05 |
| `po.cancelled` | order, reason, approver | M15, M43, P05 |
| `po.overdue` | order, line, days late, criticality | M42, M43, M01 |
| `po.import_handoff` | order, incoterm, supplier, expected shipment | M44 |
| `goods.received` | receipt, lines, quantities, discrepancies, promised vs actual date | M15, M19, M42, M52 |
| `goods.inspection_recorded` | receipt line, result, rejected quantity, cause | M15, M23, M42 |
| `invoice.matched` | invoice, order, receipts, amount, tolerance applied | M52, M19 |
| `invoice.match_failed` | invoice, exception type, cause, variance detail | M52, M42 |
| `rtv.raised` | supplier, part, quantity, reason, RMA | M15, M03, M42, M52 |
| `rtv.credit_received` | RTV, credit amount, reference | M52, M19 |
| `purchase.price_changed` | part, supplier, old price, new price, variance | M42, M43, M11 |
| `emergency.purchase_raised` | requisition, order, reason, value, approver status | M54, M42 |
| `po.confirmed` | PO id, vendor, lines, quantities, expected receipt dates, delivery premises, currency | M41, M15, M52, M42 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-PRO-01 | Supplier email (order dispatch, RFQ, acknowledgement chase) | Outbound | The fallback channel for suppliers not using P05 |
| INT-PRO-02 | P05 Vendor & Supplier Portal | Bidirectional | Order acknowledgement, dispatch advice, invoice submission, RFQ response |
| INT-PRO-03 | Brand partner parts-ordering portals | Bidirectional | Warranty parts ordering where a brand mandates its own portal; order reference reconciled back to the M16 PO |
| INT-PRO-04 | Supplier price-list files (CSV/Excel) | Inbound | Periodic agreed price-list refresh, validated against M42 agreements |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/requisitions` | POST | Raise a purchase requisition | P03, M15, M43, M45, M47 |
| `/api/v1/requisitions/{id}/submit` | POST | Submit for approval | P03 |
| `/api/v1/requisitions/{id}/approve` | POST | Approve or reject within authority | P03 |
| `/api/v1/sourcing/events` | POST | Create an RFQ or sourcing event | P03 |
| `/api/v1/sourcing/events/{id}/bids` | POST | Submit a bid | P05 |
| `/api/v1/sourcing/events/{id}/compare` | GET | Normalised bid comparison | P03 |
| `/api/v1/sourcing/events/{id}/award` | POST | Award with rationale | P03 |
| `/api/v1/purchase-orders` | POST | Create a purchase order (qualification-gated) | P03 |
| `/api/v1/purchase-orders/{id}` | GET | Order detail and status | P03, P05 |
| `/api/v1/purchase-orders/{id}/acknowledge` | POST | Supplier acknowledgement with delivery date | P05 |
| `/api/v1/purchase-orders/{id}/amend` | POST | Amend with version control | P03 |
| `/api/v1/goods-receipts` | POST | Record a receipt against an order | M41, M15, P03 |
| `/api/v1/goods-receipts/{id}/inspect` | POST | Record the inspection outcome | M41, P03 |
| `/api/v1/invoices/match` | POST | Run the three-way match for an invoice | M52 |
| `/api/v1/invoices/{id}/exception` | POST | Resolve a match exception | P03 |
| `/api/v1/rtv` | POST | Raise a return to vendor | P03, M15 |
| `/api/v1/spend/analysis` | GET | Spend by category, supplier, branch, business line | P03, P06 |
| `/api/v1/parts/{id}/price-history` | GET | Purchase price history and variance | P03, M11, M43 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R19 Procurement Officer | C R U D A | Central procurement — all categories |
| R17 Inventory Manager | C R A | Requisitions; approves ≤ BDT 50,000 |
| R18 Branch Store Keeper | C R | Own branch requisitions only |
| R06 Branch Manager | C R A | Own branch requisitions; approves within branch authority |
| R20 Warehouse Operative | R U | Goods receipt at own warehouse only |
| R26 Finance Manager | R A | Match exceptions, override approval, RTV credit |
| R27 Finance Officer | R | Match and invoice status |
| R03 Chief Financial Officer | R A | All; approves ≤ BDT 2,000,000 and all tolerance changes |
| R01 Chief Executive Officer | R A | Approves above BDT 2,000,000 |
| R32 Quality Manager / ISO Coordinator | R U | Inspection outcomes, rejections, RTV quality grounds |
| R05 Operations Director | R | All |
| R15 Logistics Coordinator | R | RTV dispatch coordination |
| R33 IT / System Administrator | R | Configuration; no transactional or approval rights |
| R38 Vendor | R U | Own purchase orders, own RFQs, own invoices only (P05) |

**Procurement Manager rights.** Exercised through R19 with an elevated grant covering sourcing
events above the competitive threshold, award approval, tolerance-band proposals, emergency
purchase approval and requisition approval to BDT 500,000.

**Field-level restrictions.** `vendor_price` and price history are visible to R17, R19, R26,
R27 and R03 only (`05-04` §5). Branch requesters see their own requisition value, never the
supplier's price to other branches. Vendors see only their own pricing.

**Segregation of duties.**
- **SOD-01 enforced:** a user who creates a supplier record cannot approve that supplier's invoice — hard block.
- **SOD-02 enforced:** raise PO + receive goods + approve invoice — any two permitted, all three blocked.
- A requester cannot approve their own requisition at any value.
- A user cannot both award a sourcing event and approve the resulting purchase order above the competitive threshold.
- The user who resolves a match exception cannot be the user who raised the purchase order.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Procurement pipeline** | Procurement Manager, Procurement Officer | Real time | Requisitions by state, ageing, orders in flight, overdue lines |
| PO cycle time | Procurement Manager, Operations Director | Weekly | Approved requisition → placed order, against the < 24 h target, by category and buyer |
| **Three-way match health** | Finance Manager, Procurement Manager, CFO | Weekly | First-time match rate, exception rate against < 5%, exceptions by cause |
| Match exception root cause | Procurement Manager, Finance Manager | Monthly | Causes ranked — price, quantity, missing GRN, unordered line, duplicate — with elimination actions |
| Spend analysis | Procurement Manager, CFO | Monthly | Spend by category, supplier, branch, business line and buyer; concentration |
| **Emergency and maverick spend** | Procurement Manager, CFO | Monthly | Emergency purchases against < 8% of spend; off-contract spend; single-source dependence |
| Purchase price variance | Procurement Manager, CFO, Inventory Manager | Monthly | Price paid vs agreement and vs prior period, by part and supplier |
| Delivery performance (source data) | Procurement Manager, M42 | Weekly | Promised vs actual by order and supplier — the raw facts the M42 scorecard consumes |
| Inspection rejection | Quality Manager, Procurement Manager | Monthly | Rejection rate against < 2%, by supplier, part and defect type |
| RTV and credit recovery | Procurement Manager, Finance Manager | Monthly | Returns raised, RMAs outstanding, credits aged, value at risk |
| Sourcing event register | Procurement Manager, Internal Audit | Quarterly | Every event, invitees, responses, award and rationale |
| Contract coverage | Procurement Manager, CFO | Quarterly | Share of spend under an M42 agreement vs spot |
| Approval compliance | Internal Audit, CFO | Quarterly | Every approval against the authority matrix; exceptions and SoD near-misses |
| Committed spend vs budget | Cost-centre owners, CFO | Monthly | Commitment at requisition and order, against M54 budgets |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-048** | Vendor on-time delivery *(measured by M16, owned as a relationship metric by M42 — see the note below)* | unmeasured | 88% | **92%** |
| **KPI-049** | Three-way match exception rate | n/a | < 8% | **< 5%** |
| — | PO cycle time (approved requisition → placed order) | unmeasured | < 48 h | **< 24 h** |
| — | Goods inspection rejection rate | unmeasured | < 4% | **< 2%** |
| — | Emergency / spot purchases as % of spend | unmeasured | < 15% | **< 8%** |
| — | First-time match rate (inverse of exception rate) | n/a | > 92% | **> 95%** |
| — | Requisitions approved within SLA | n/a | 90% | **97%** |
| — | Spend under contract (contract coverage) | unknown | 55% | **75%** |
| — | Purchase price variance against agreement | unmeasured | ± 3% | **± 1%** |
| — | RTV credits recovered as % of value raised | unknown | 80% | **95%** |
| — | Duplicate invoices reaching payment | unknown | **0** | **0** |
| — | Purchase orders to unqualified suppliers | unknown | **0** | **0** |

> **Register conflict — audit action.** `06-02` §2.6 assigns **KPI-048 Vendor on-time delivery**
> to **M16**, while `_CATEGORY_OVERVIEW.md` §7 assigns the same metric to **M42**. Both are
> partly right and the conflict is resolved here as follows: **M16 produces the measurement**
> (promised versus actual date on every receipt line, per BRU-PRO-17) and **M42 owns the metric
> as a relationship outcome** — the scorecard, the review conversation and the corrective action.
> The metric appears in both module files with this note. `06-02` should be amended to name
> M16 as source and M42 as owner. Four further metrics above are unregistered and require
> `KPI-0nn` allocation.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `purchase` — RFQ, vendor pricelists, purchase orders, receipt control, vendor bills, three-way match foundation | 38% |
| L2 | OCA `purchase-workflow` — requisition, tender, approval, order amendment, receipt discrepancy | 22% |
| L5 | `cd_requisition`, `cd_rfq`, `cd_sourcing_event`, `cd_three_way_match` | 40% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 1 of 4 identifiers below are claimed by another module: **CD-073** also claimed by M55. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-146** | `cd_requisition` — multi-source demand intake, authority-matrix routing, delegation and escalation, low-value auto-approval, consolidation, budget check | Odoo module | 5 PW |
| CD-073 | `cd_rfq` — RFQ issue, portal response capture, normalised bid comparison, award with rationale | Odoo module | 4 PW |
| **CD-147** | `cd_sourcing_event` — sealed bid, reverse auction, approved-source list, sourcing decision rules, immutable event audit | Odoo module | 3 PW |
| **CD-148** | `cd_three_way_match` — tolerance sets, match engine, exception classification and routing, duplicate detection, root-cause analytics, AP release | Odoo module + service | 6 PW |

> CD-073 retains its allocation from `02-05` §5.2. CD-146…148 are claimed from the extension
> block for modules M31–M67. `cd_vendor_ext` (CD-072) moves to **M42** and `cd_import_order`
> (CD-074) moves to **M44** under the v2.1 re-scope. **All CD IDs remain provisional** pending
> the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M16 is scheduled in **W3** (P1) but declares a dependency on 1 module(s) that land later: **M42** (W4). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M16 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M16 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M42 Supplier Relationship** | The qualification gate is structural. M42 is scheduled W4, one wave *after* M16 — see the sequencing risk below |
| M15 Inventory (W2) | Replenishment alerts are the primary demand signal; goods receipt lands in stock |
| M37 Catalogue | Parts must be defined before they can be ordered |
| M33 Party Master | Supplier parties must exist |
| M19 Financial Accounting (W3) | GRN accrual and PPV consumers |
| M52 Accounts Payable (W3) | The recipient of matched invoices |
| M23 Quality | Inspection plans; may be stubbed with a default plan in W3 |
| M41 Warehouse Management (W3) | Physical receipt at WMS locations; non-WMS receipt through M15 works without it |
| M44 Import (W6) | Until W6, imported purchase orders are managed as long-lead domestic orders. **How they are costed in W3–W5 is an open decision** — see the note below |

> **Sequencing risk — must be resolved before W3 build.** M16 lands in **W3** and M42 in **W4**,
> yet BRU-PRO-02 makes M16 dependent on M42's qualification register. Two options exist:
> (a) deliver a **minimal supplier qualification register as a W3 slice of M42** — a supplier
> status field, a category approval and an activation decision — deferring scorecards, risk and
> development to W4; or (b) accept a soft warning instead of a hard block for one wave.
> **Option (a) is recommended and is assumed by this specification**; option (b) leaves the
> counterfeit and SOD-01 exposure open for a wave. Raised as Q-01.
>
> ---
>
> **Second sequencing risk — how imports are costed in W3–W5.** M16 goes live in W3 and will
> place cross-border orders immediately, but M44 does not deliver landed cost until **W6**. For
> three waves, imported parts would otherwise be received at **invoice price**, which is the
> exact error M44 exists to correct and which `_CATEGORY_OVERVIEW.md` §9 rates as a high-impact
> risk. `M44_Import_Trade_Compliance_and_Landed_Cost.md` §16.3 sets out the two options — a
> **W3 landed-cost slice** (≈4 PW of CD-071 pulled forward, giving cost capture, allocation and
> provisional/final publication to M15) or **retrospective revaluation at W6** — and recommends
> the slice. **M16 does not own this decision** and makes no assumption about it; the M16-side
> consequence is only that a cross-border purchase order must carry its incoterm, currency and
> expected non-invoice costs from W3 so that whichever option is chosen has the data it needs.
> Tracked as Q-01 in M44.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open purchase orders | Current only, ~150–400 lines | `fix.purchase.order` | W3 cutover |
| Supplier price lists | 40–120 suppliers | `fix.approved.source` | W3 |
| Historical purchase prices | 24 months where recoverable | `fix.purchase.price.history` | W3, best-effort |
| Open RTVs and outstanding credits | Current only | `fix.purchase.rtv` | W3 |
| Spend category taxonomy | Authored, not migrated | `fix.spend.category` | W3 |

No requisition, RFQ or match history exists. **The spend category taxonomy, the competitive
thresholds and the match tolerance bands must be authored before W3 build** — they are policy
decisions, not data.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A purchase order cannot be raised to an unqualified or inactive supplier through the UI, the API, or automation | Negative test on all three paths |
| AC-02 | Every purchase order in production traces to an approved requisition | Full-population assertion query over four weeks |
| AC-03 | Requisition approval routing matches the `05-04` §7 authority matrix at every band | Test matrix across all four bands |
| AC-04 | A requester cannot approve their own requisition at any value | Negative test |
| AC-05 | SOD-02 is enforced: no user can raise a PO, receive its goods and approve its invoice | SoD negative test |
| AC-06 | SOD-01 is enforced: the creator of a supplier cannot approve that supplier's invoice | SoD negative test |
| AC-07 | Three-way match auto-clears at least 95% of invoices within tolerance | Twelve weeks of production invoices |
| AC-08 | Match exception rate is below 5% at Wave 8, with causes classified on every exception | Twelve weeks of measurement |
| AC-09 | A duplicate invoice is rejected automatically, including near-duplicates differing only in formatting | Negative test suite |
| AC-10 | An unmatched invoice cannot be released to M52 without a documented Finance Manager override | Negative test |
| AC-11 | PO cycle time from approved requisition to placed order is under 24 hours at p90 | Four weeks of measurement |
| AC-12 | A PO amendment increasing value beyond tolerance re-enters approval at the new band | Scripted scenario |
| AC-13 | A cross-border PO hands off to M44 at confirmation with the linkage retained both ways | Integration test (from W6) |
| AC-14 | Promised-versus-actual delivery facts are recorded on every receipt and are not editable by procurement | Negative test plus a four-week data audit |
| AC-15 | An inspection rejection quarantines stock in M15, raises an RTV and records a quality event for M42 | End-to-end scripted scenario |
| AC-16 | An emergency purchase creates a retrospective requisition and escalates to the CFO if unapproved within 48 hours | Scripted scenario |
| AC-17 | A sourcing event above the competitive threshold cannot be awarded with fewer than three bids without a documented single-source justification approved one level up | Negative test |
| AC-18 | An award to other than the lowest compliant bid cannot be saved without a rationale | Negative test |
| AC-19 | A supplier can acknowledge an order, submit a dispatch advice and submit an invoice through P05, idempotently | Portal test with replay |
| AC-20 | Purchase orders and RTV documents render correctly in Bengali | Translation and rendering review (AS-12) |
| AC-21 | Procurement Manager and Finance Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 21 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is the minimal W3 qualification slice of M42 approved?** Without it, BRU-PRO-02 cannot be enforced in W3. | Procurement Manager / CTO | W3 minus 3 months |
| Q-02 | What is the competitive threshold above which three quotations are mandatory, and does it vary by category? | Procurement Manager / CFO | W3 build |
| Q-03 | What are the three-way match tolerance bands — price and quantity, by category and value? | CFO | W3 build |
| Q-04 | Which suppliers will use P05, and which must be served by email? What is the realistic adoption path in the Bangladesh parts market? | Procurement Manager | W3 design |
| Q-05 | Do any brand partners mandate their own parts-ordering portal, and can the order reference be reconciled back to an M16 purchase order? | Procurement Manager / Warehouse Manager | W3 build |
| Q-06 | Is the emergency post-hoc approval window 48 hours, and what is the consequence of a missed approval beyond escalation? | Procurement Manager / CFO | W3 build |
| Q-07 | What is the spend category taxonomy, and who owns each category? | Procurement Manager | W3 minus 2 months |
| Q-08 | Are subcontracted repairs procured through M16 or handled as marketplace capacity through M12? Both paths currently look plausible. | CCO / Procurement Manager | W3 design |
| Q-09 | Is budget checking at requisition a warning or a block, and does it differ by cost-centre type? M54 lands in W6 — what happens in W3–W5? | CFO | W3 build |
| Q-10 | Who resolves a price-variance match exception — procurement or finance? The SoD rule requires it not be the PO raiser. | CFO / Procurement Manager | W3 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §4 (why procurement and supplier management are separate), §6, §7 ·
`M42_Supplier_Relationship_and_Performance.md` §3 (the reciprocal boundary and the
qualification gate) · `M15_Spare_Parts_and_Inventory_Management.md` (replenishment and RTV) ·
`M41_Warehouse_Management.md` (physical receipt and inspection) ·
`M43_Demand_Planning_and_Replenishment.md` (planned orders) ·
`M44_Import_Trade_Compliance_and_Landed_Cost.md` (cross-border hand-off) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E, §5 (retired code `SCM`) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5, §6 SOD-01/SOD-02, §7 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.6 (KPI-048, KPI-049) ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P05

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-SCM-001 … BR-SCM-007,
BR-INV-006, BR-INV-012, BR-INV-014

**External benchmark**
SAP S/4HANA Purchasing — source list, outline agreement with call-off, tolerance-key invoice
verification · [Oracle Fusion Procurement — match options and tolerance thresholds](https://docs.oracle.com/cd/E15586_01/fusionapps.1111/e20383/F274737AN35998.htm) ·
[Oracle procure-to-pay best practices](https://www.oracle.com/webfolder/s/delivery_production/docs/FY15h1/doc4/Procure-Pay.pdf) ·
[Optimising purchase requisition approval in Oracle Fusion](https://processmind.com/continuous-process-improvement/purchase-to-pay-requisition/oracle-fusion) —
approval segmentation by spend and risk; more than three tiers create friction ·
[P2P best practice — three-way match automation, 90%+ first-time match, exception root-cause elimination](https://www.ivalua.com/blog/procure-to-pay-best-practice/) ·
[Maverick-spend control through self-service and guided buying](https://qxglobalgroup.com/fa/us/blog/procure-to-pay-services-reduce-maverick-spending) ·
Microsoft Dynamics 365 Procurement and Sourcing — vendor collaboration portal ·
Odoo 19 CE `purchase` — RFQ, vendor pricelists, three-way matching, receipt control ·
OCA `purchase-workflow` — requisition, tender and approval extensions

---

*Module M16 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
