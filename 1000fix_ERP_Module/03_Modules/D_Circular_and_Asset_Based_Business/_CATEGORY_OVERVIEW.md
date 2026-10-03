---
id: FIX-ERP2-CAT-D
category: D
category_name: Circular & Asset-Based Business
module_count: 3
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category D — Circular & Asset-Based Business

**3 modules · Category owner: Corporate Services Head / Retail Operations Head**

---

## 1. What Belongs in This Category

The business lines where **1000FiX owns or takes possession of the asset itself**, rather
than servicing an asset the customer owns.

This is a fundamentally different economic model from repair. Repair sells labour and parts.
These modules sell — or monetise — the asset. That means utilisation, condition, valuation,
depreciation, deposits, damage recovery and end-of-life all become first-class concerns.

They are grouped together because they form a **single circular flow**: a device is bought
in, refurbished, sold or rented, returned, refurbished again, and eventually recycled.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M13** | Rental & Equipment-as-a-Service | Retained | P2 | W6 | Rents eight asset categories with reservation, agreement, tariff, deposit, condition, damage and return |
| **M14** | Trade-In, Refurbishment & Resale | Retained | P2 | W6 | Buys used devices, grades and refurbishes them, and resells them with controlled warranty |
| **M18** | E-Waste, Recycling & Circular Economy | Retained | P3 | W8 | Collects end-of-life devices, certifies destruction and disposal, and recovers materials |

---

## 3. The Circular Flow

```
      CUSTOMER DEVICE                       1000FiX OWNED ASSET
            │                                      │
            │ trade-in / buy-back                  │ purchase / capitalise
            ▼                                      ▼
     ┌──────────────┐                      ┌──────────────┐
     │  M14 INTAKE  │                      │  M13 RENTAL  │
     │  & VALUATION │                      │     POOL     │
     └──────┬───────┘                      └──────┬───────┘
            │                                     │  rent out ──► return
            │ mandatory                           │  condition report both ends
            ▼                                     │  damage assessment
     ┌──────────────┐                             │
     │ M06 CERTIFIED│◄────────────────────────────┘  (on retirement)
     │ DATA WIPE    │
     └──────┬───────┘
            │  no unit proceeds without a certificate
            ▼
     ┌──────────────┐        pass         ┌──────────────┐
     │ M14 REFURB   │────────────────────►│ M38 / M12    │
     │ & GRADING    │   A / B / C grade   │ RESALE       │
     └──────┬───────┘                     └──────────────┘
            │ fail / parts-only
            ▼
     ┌──────────────┐   harvest    ┌──────────────┐
     │ M14 HARVEST  │─────────────►│ M15 PARTS    │
     └──────┬───────┘              │  (harvested) │
            │ unusable             └──────────────┘
            ▼
     ┌──────────────┐
     │ M18 RECYCLE  │──► certified partner ──► disposal certificate ──► M24
     └──────────────┘                          material recovery ──► M20
```

---

## 4. The Non-Negotiable Gate

> **No device moves from M14 or M18 to any downstream destination without a certified data
> destruction record from M06.**

This is a hard block, not a warning. It is the single control that protects the Company from
its largest latent liability: reselling or recycling a device that still holds a customer's
data.

| Gate | Enforced By | Bypass |
|---|---|---|
| Refurbishment cannot start | M14 state machine | None |
| Resale listing cannot publish | M14 state machine | None |
| Recycling transfer cannot execute | M18 state machine | None |
| Parts harvesting from a storage device | M14 state machine | None |

---

## 5. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Asset identity, serial, history | **M17** | M13, M14, M18 (all reference) |
| Rental asset condition and utilisation | **M13** | M17 (holds identity only) |
| Fixed asset capitalisation and depreciation | **M49** | M13 (operational view only) |
| Certified data destruction | **M06** | M14, M18 (both require it, neither performs it) |
| Physical movement and custody | **M03** | M13, M14, M18 (all request consignments) |
| Refurbished parts entering stock | **M15** | M14 (produces them) |
| Resale listing and checkout | **M38** / **M12** | M14 (supplies the graded unit and its price) |
| Trade-in valuation model | **M26** provides; **M14** decides | — |
| Deposit accounting and refund | **M20** | M13 (calculates the amount) |
| Damage charge invoicing | **M20** | M13 (assesses the damage) |
| Disposal certificates as records | **M24** | M18 (obtains them) |
| ESG and sustainability reporting | **M18** | M25 (visualises) |

---

## 6. Why These Are Real Business Lines, Not Aspirations

| Business Line | Evidence in the Workspace |
|---|---|
| Rental | Business Plan §Rental Services — eight asset categories: laptops, cameras, projectors, tablets, audiovisual, servers, networking, electronic test equipment. Company Profile §Laptop Rental Service. Service App SOW lists rental as a purchasable service type. |
| Trade-in & refurbishment | Business Plan §Refurbishment and Resale — refurbishment, data wiping, QA testing, resale and distribution, warranty on refurbished units. Company Profile §Exchange Offer. Service App SOW describes the customer-facing trade-in quotation flow in detail. |
| E-waste & recycling | Business Plan §Device Recycling and Responsible Disposal — collection points, triage, certified partners, data destruction, secure disposal, regulatory compliance, component recovery, awareness. |

None of these is a new idea. All three are documented commitments with no system behind them.

---

## 7. Category KPIs

| KPI | Target | Owning Module |
|---|---|---|
| Rental fleet utilisation | > 68% | M13 |
| Rental revenue per asset per month | Category targets set at launch | M13 |
| On-time rental return rate | > 90% | M13 |
| Damage recovery rate | > 85% of assessed damage | M13 |
| Rental asset loss rate | < 0.5% per year | M13 |
| Rental gross margin | > 55% | M13 |
| Trade-in offer acceptance rate | > 55% | M14 |
| Refurbishment cycle time | < 5 days | M14 |
| Refurbishment yield (units sellable) | > 88% | M14 |
| Gross margin per refurbished unit | > 22% | M14 |
| Refurbished return rate | < 4% | M14 |
| Refurbished stock ageing > 90 days | < 12% | M14 |
| Devices collected for recycling per year | 25,000 | M18 |
| Diversion from landfill | > 92% | M18 |
| Data destruction before disposal | **100%** | M06 / M14 / M18 |
| Disposal certificates on file | **100%** | M18 |

---

## 8. Category Delivery Sequence

```
W6   M13 Rental ────┐
     M14 Trade-in & Refurbishment ┴──► asset businesses live
                                       (both depend on M06 Data Services, same wave)
W8   M18 E-Waste ──────────────────► circular loop closed
```

M06 Data Services must go live **in or before** Wave 6. If it slips, M14 cannot launch,
because the destruction gate cannot be satisfied.

---

## 9. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| A resold device still holds customer data | **Critical** — regulatory, reputational, contractual | Hard state-machine gate; certificate required; no override | M14 / M06 |
| Handling stolen goods through trade-in | **Critical** — criminal exposure | Seller identity verification; provenance record; IMEI/serial blocklist screening where available | M14 |
| Rental assets untracked, written off | High — direct capital loss | Condition reports at both ends; deposits; utilisation monitoring; loss rate KPI | M13 |
| Refurbished warranty liability exceeds provision | Medium | Rigorous grading; QA protocol; disclosed condition; actuarial reserve | M14 |
| Uncertified e-waste partner used | High — regulatory | Certification currency checked at transfer; expired certification blocks transfer | M18 |
| Rental and resale operated in the wrong legal entity | High — tax and accounting rework | Entity decision required three months before Wave 6 (decision D-04) | CFO |

---

*Category D · 1000FiX ERP System v2.0*
