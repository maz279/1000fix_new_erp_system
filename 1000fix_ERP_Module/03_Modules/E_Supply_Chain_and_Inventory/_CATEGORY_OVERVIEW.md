---
id: FIX-ERP2-CAT-E
category: E
category_name: Supply Chain & Inventory
module_count: 6
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category E — Supply Chain & Inventory

**6 modules · Category owner: Supply Chain Director**

---

## 1. What Belongs in This Category

Materials in, materials stored, materials consumed, and the suppliers behind them.

If a capability answers *"do we have the part, where is it, what did it cost, and who
supplies it"*, it belongs here. If it answers *"is this a customer's device"*, it belongs to
Category F.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M15** | Spare Parts & Inventory Management | Re-scoped | P0 | W2 | Owns stock: what exists, where, in what condition, under whose ownership, and what it is worth |
| **M41** | Warehouse Management ★ | New | P1 | W3 | Owns physical warehouse execution: bins, put-away, picking strategies, waves, cross-dock, cycle counting on the floor |
| **M16** | Procurement & Strategic Sourcing | Re-scoped | P1 | W3 | Owns buying: requisition, RFQ, purchase order, receipt, three-way match |
| **M42** | Supplier Relationship & Performance ★ | New | P1 | W4 | Owns the supplier as a relationship: qualification, contracts, scorecards, risk, development |
| **M43** | Demand Planning & Replenishment ★ | New | P2 | W6 | Owns *how much to hold and when to order*: forecast consumption, safety stock, reorder parameters, network balancing |
| **M44** | Import, Trade Compliance & Landed Cost ★ | New | P2 | W6 | Owns cross-border supply: proforma, LC, shipment, customs, duty, clearing, true landed cost |

★ = new in v2.1 after enterprise benchmarking.

---

## 3. Why Inventory and Warehouse Are Separate

Every tier-one ERP separates the **inventory ledger** from **warehouse execution**. The v2.0
draft merged them; at 51+ branches plus central warehouses plus 200–400 vans, that merge
does not survive contact with reality.

| | M15 Inventory | M41 Warehouse Management |
|---|---|---|
| **Owns** | Quantity, ownership, valuation, reservation, classification, compatibility, network availability | Physical location to bin level, put-away strategy, pick paths, wave and batch picking, cross-dock, floor-level counting, dock and staging |
| **Question** | "Do we have it, whose is it, what is it worth?" | "Where exactly is it and how do I get it out efficiently?" |
| **Analogue** | SAP *MM/Inventory Management* · Oracle *Inventory Management* | SAP *EWM* · Oracle *Warehouse Management* · Dynamics *Warehouse Management* |
| **Applies to** | All 51+ branches, vans, consignment, refurb, rental pool | Central warehouses and large branch stores only |
| **Changes when** | Ownership or valuation policy changes | Physical layout or throughput changes |

**Rule:** M15 is the ledger; M41 is the floor. A branch with a single stockroom uses M15
only. A central warehouse uses both.

---

## 4. Why Procurement and Supplier Management Are Separate

| | M16 Procurement | M42 Supplier Relationship |
|---|---|---|
| **Owns** | The transaction: requisition → RFQ → PO → receipt → match | The relationship: qualification, contracts, scorecards, risk, development, category strategy |
| **Cadence** | Daily, transactional | Quarterly, strategic |
| **Analogue** | SAP *Purchasing* · Oracle *Purchasing* | SAP *Ariba SLP* · Oracle *Supplier Management* |
| **Owner** | Procurement Officer | Procurement Manager / Supply Chain Director |

**Rule:** M16 cannot raise a purchase order to a supplier that M42 has not qualified and
activated.

---

## 5. The Six Ownership Classes of Stock

This is the distinguishing complexity of an authorised service business, and the reason
M15 cannot be a plain inventory module.

| Class | Owner | Can Be Used For | Valued In Our Books | Owning Rule |
|---|---|---|---|---|
| **Own commercial stock** | 1000FiX | Any paid repair or sale | Yes | Standard |
| **Brand consignment stock** | Brand partner | That brand's warranty work only | **No** | Hard block on non-warranty use (BRU-WTY-04) |
| **Customer-supplied parts** | Customer | That customer's job only | No | Returned or consumed, never absorbed |
| **Refurbished / harvested parts** | 1000FiX | Out-of-warranty repair and refurbishment; disclosed to the customer | Yes, at recovery value | Never used on warranty work |
| **Rental pool assets** | 1000FiX (capitalised) | Rental only | Yes, as a fixed asset (M49) | Not consumable stock |
| **Marketplace seller stock** | Seller | Seller's own jobs | **No** | Visibility only, no reservation |

Getting this wrong is how service companies lose money invisibly. Every stock movement in
M15 carries its ownership class, and the class governs what may be done with it.

---

## 6. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Part definition, compatibility, supersession | **M37** Catalogue | M15 (references) |
| Stock quantity, ownership, valuation | **M15** | M41 (moves it), M19 (posts it) |
| Bin location and pick strategy | **M41** | M15 |
| Van stock par levels and replenishment | **M15** | M02 (consumes) |
| Purchase requisition, PO, receipt, match | **M16** | M42 |
| Supplier qualification, scorecard, contract | **M42** | M16 |
| Reorder point, safety stock, forecast | **M43** | M15 (executes the alert) |
| Forecast model itself | **M26** AI/ML | M43 (owns the planning process) |
| Import documentation, LC, customs | **M44** | M16 |
| Landed cost calculation | **M44** | M15 (receives the value), M19 (posts it) |
| Physical movement between sites | **M03** Logistics | M15, M41 (both request) |
| Vendor invoice posting and payment | **M52** AP | M16 (matches) |
| Return to vendor | **M15** raises, **M03** moves, **M16** credits | — |
| Tool and test equipment issue | **M45** | M15 (not consumable stock) |

---

## 7. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Inventory accuracy | 75% | 98%+ | M15 |
| Part availability at first request | unmeasured | > 93% | M15 |
| Stockout-caused job delays | unmeasured | < 3% | M15 |
| Inventory turns per year | unmeasured | > 6 | M15 |
| Dead stock as % of value | unmeasured | < 5% | M15 |
| Van stock variance | untracked | < 1% | M15 |
| Warehouse pick accuracy | unmeasured | > 99.5% | M41 |
| Lines picked per hour | unmeasured | baseline +35% | M41 |
| Put-away cycle time | unmeasured | < 2 h from receipt | M41 |
| Vendor on-time delivery | unmeasured | > 92% | M42 |
| Goods inspection rejection rate | unmeasured | < 2% | M16 |
| PO cycle time (requisition to PO) | unmeasured | < 24 h | M16 |
| Three-way match exception rate | n/a | < 5% | M16 |
| Emergency / spot purchases as % of spend | unmeasured | < 8% | M16 |
| Forecast accuracy (MAPE, A-class parts) | n/a | < 22% | M43 |
| Import clearance cycle time | unmeasured | baseline −20% | M44 |
| Landed cost accuracy vs actual | unmeasured | within 2% | M44 |

---

## 8. Category Delivery Sequence

```
W2   M15 Inventory ─────────────► stock visible, van stock controlled
W3   M41 Warehouse ──┐
     M16 Procurement ┴──────────► floor execution and buying
W4   M42 Supplier Relationship ─► qualification and scorecards
W6   M43 Demand Planning ──┐
     M44 Import & Landed Cost ┴─► planned replenishment and true cost
```

M43 is deliberately late: demand forecasting requires two years of clean consumption history,
which only exists after M15 has been live through W2–W5.

---

## 9. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Brand consignment stock consumed on paid repairs | **Critical** — brand relationship and financial misstatement | Hard block by ownership class; reconciliation reported to the brand monthly | M15 |
| Van stock becomes an untracked black hole | High — the single largest shrinkage source | Daily reconciliation; variance escalation; par levels enforced | M15 |
| Migration of 10,000 SKUs × 51 locations is wrong | High — inventory accuracy never recovers | Full physical count at cutover, not a spreadsheet load | M15 |
| Warehouse module deployed where it is not needed | Medium — cost and complexity at small branches | M41 applies to central warehouses and large stores only, by configuration | M41 |
| Forecasting deployed before there is history | Medium — bad forecasts destroy trust | M43 deferred to W6 deliberately | M43 |
| Import duty and clearing costs never reach unit cost | High — margins overstated on imported parts | Landed cost allocation is mandatory before stock is valued as final | M44 |

---

*Category E · 1000FiX ERP System v2.0*
