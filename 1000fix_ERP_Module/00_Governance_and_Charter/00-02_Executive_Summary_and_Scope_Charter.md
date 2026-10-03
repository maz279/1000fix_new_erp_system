---
id: FIX-ERP2-001
title: Executive Summary & Expanded Scope Charter
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Executive Summary & Expanded Scope Charter
# 1000FiX ERP System v2.0

---

## 1. The Decision Being Documented

In March 2026 the Company approved an ERP programme covering **11 modules and 6 portals**,
scoped to digitise the existing repair business — service orders, field dispatch, inventory,
CRM, finance, HR, contracts, procurement, BI, documents and quality.

That plan solved the *operational* problem. It did not solve the *strategic* one.

A review of the Company's own business plan, the Service App Scope of Work, and the
Integrated Portal technical roadmap shows that 1000FiX has committed — on paper — to a set
of businesses the approved ERP cannot run:

- **Rental and equipment-as-a-service** across eight asset categories
- **Data recovery, backup and secure destruction** as billable service lines
- **Refurbishment, trade-in and resale** of consumer and IT devices
- **Managed IT services (MSP)** with proactive monitoring, patching and 24/7 support desks
- **E-waste recycling and certified disposal** with compliance documentation
- **A marketplace** where external engineers and shops transact under the 1000FiX brand,
  with bidding, commissions, ratings, paid promotion and settlement
- **Multi-country expansion** with multi-entity finance and localisation

Running these on spreadsheets alongside a modern ERP would recreate, in three years, exactly
the fragmentation the ERP was bought to remove.

**The decision: expand the ERP scope now, before build starts, from 11 modules to 30 —
so that every revenue stream the Company intends to operate has a system of record from day one.**

---

## 2. What Changes

> **Revision 2.1 — audit findings C-01 and H-02.** The figures below were restated after the
> documentation audit. The module architecture was expanded from 30 to **67 modules in 11
> categories** following enterprise benchmarking against SAP S/4HANA, Oracle Fusion, Microsoft
> Dynamics 365, IFS Cloud and Odoo 19. The cost line is **provisional** and must not be
> presented to the Board as final until all 67 module specifications are written.

| Dimension | v1.0 Approved | v2.1 Proposed | Change |
|---|---|---|---|
| ERP modules | 11 | **67** | +56 |
| Module categories | — | 11 | Structural |
| Portals & applications | 6 | 12 | +6 |
| Custom development items | 20 | ~138 | +118 |
| Functional requirements | ~405 | **~2,352** *(388 measured, remainder estimated)* | +~1,947 |
| Revenue streams supported | 5 | 14 | +9 |
| User roles modelled | 20 | 38 | +18 |
| Integrations | 15 | 47 | +32 |
| Build effort | not stated | **~1,302 PW** *(206 measured, remainder estimated)* | — |
| Delivery horizon | 18 months, 6 phases | 36 months, 9 waves | +18 months |
| Core team | 6 | 11 (peak 19) | +13 at peak |
| **3-year TCO** | $182K – $342K | **$620K – $1,050K** *(provisional)* | +$438K – $708K |
| Legal-entity model | Single (Bangladesh) | Multi-entity, multi-country ready | Structural |
| Data residency model | Single region (Singapore) | **Split residency** — Bangladesh-resident store for sensitive personal data | Structural, driven by PDPA 2026 |

### Why the Cost Estimate Moved

The v2.0 figure of $455K–$780K was modelled on 834 person-weeks across 30 modules. The
67-module architecture is estimated at **~1,302 person-weeks**. Category A, the only category
with completed specifications, came in at 206 PW against an original estimate of 168 PW for
the same scope — an under-estimate of 23%, which has been applied as a correction factor to
the remaining categories.

**This figure will move again.** It should be re-baselined at the end of each category's
specification work, and only presented as final when all 67 files exist.

The first 18 months of v2.0 deliver **everything v1.0 promised, on the same dates**.
The expansion is additive and back-loaded: Waves 1–4 are the v1.0 scope plus the
low-cost, high-return additions; Waves 5–9 are the new business lines.

---

## 3. The Fourteen Revenue Streams the ERP Must Run

| # | Revenue Stream | v1.0 | v2.0 | Owning Module |
|---|---|---|---|---|
| 1 | Authorized brand warranty service | ✓ | ✓ | M09 Warranty & Claims |
| 2 | Out-of-warranty paid repair | ✓ | ✓ | M01 SRM |
| 3 | AMC / RAMC subscriptions | ✓ | ✓ | M08 Contract Lifecycle |
| 4 | Warranty extension products | ✓ | ✓ | M09 Warranty & Claims |
| 5 | Spare parts & accessories | ✓ | ✓ | M15 Inventory |
| 6 | **Corporate managed IT services (MSP)** | — | ✓ | M05 Remote Support & Managed Services |
| 7 | **Equipment rental / EaaS** | — | ✓ | M13 Rental |
| 8 | **Data recovery** | — | ✓ | M06 Data Services |
| 9 | **Data backup & archival subscriptions** | — | ✓ | M06 Data Services |
| 10 | **Refurbished device resale** | — | ✓ | M14 Trade-In & Refurbishment |
| 11 | **Trade-in / exchange margin** | — | ✓ | M14 Trade-In & Refurbishment |
| 12 | **E-waste recycling & material recovery** | — | ✓ | M18 E-Waste & Sustainability |
| 13 | **Marketplace commission & settlement** | — | ✓ | M12 E-Commerce & Marketplace |
| 14 | **Advertising, boost & lead placement** | — | ✓ | M12 + M10 Loyalty & Campaigns |

Streams 6–14 are already described in the Company's own business plan and Service App SOW.
They are not new business ideas; they are **existing commitments without a system**.

---

## 4. The Five Pillars

> **Revision 2.1 — audit finding M-05.** The five-pillar grouping below was the v2.0
> organisation of 30 modules. The architecture now uses **11 categories** covering 67 modules.
> The category definitions are held in `02_Architecture/02-02` §2 and each category's
> `_CATEGORY_OVERVIEW.md`. The pillar descriptions are retained here only as a narrative of
> the business domains; they are **not** the organising structure.

**The 11 categories:**

| Cat | Name | Modules | Accountable Executive |
|---|---|---:|---|
| A | Service Delivery & Operations | 7 | Service Operations Director |
| B | Customer Engagement & Experience | 7 | Chief Commercial Officer |
| C | Commercial, Pricing & Revenue | 9 | Chief Commercial Officer |
| D | Circular & Asset-Based Business | 3 | Corporate Services / Retail Operations Head |
| E | Supply Chain & Inventory | 6 | Supply Chain Director |
| F | Asset, Equipment & Facilities | 5 | Service Operations Director / CTO |
| G | Finance & Treasury | 8 | CFO |
| H | People & Workforce | 7 | HR Director |
| I | Governance, Risk, Quality & Knowledge | 4 | Quality Manager / CFO |
| J | Data, Analytics & Intelligence | 4 | CTO |
| K | Platform & Technology | 7 | CTO |

The business domains these categories serve are described below.

### Pillar A — Core Service Operations (M01–M06)
*Owner: Service Operations Director*

Everything that happens to a customer's device or IT estate. Extends the v1.0 service
order and dispatch core with logistics, front-desk queue management, remote/managed
services and data services.

### Pillar B — Customer, Commercial & Revenue (M07–M14)
*Owner: Chief Commercial Officer*

Who the customer is, what they have agreed to, what they are charged, and every route to
market — direct, contract, e-commerce, marketplace, rental and resale.

### Pillar C — Supply Chain & Assets (M15–M18)
*Owner: Supply Chain Director*

Parts, vendors, the device and asset registry including IoT telemetry, and the end-of-life
recycling chain.

### Pillar D — Finance, People & Governance (M19–M24)
*Owner: CFO (finance) / HR Director (people) / Quality Manager (governance)*

Money, compliance, workforce, competency, quality systems and records.

### Pillar E — Intelligence & Platform (M25–M30)
*Owner: CTO*

Analytics, machine learning, conversational AI and contact centre, integration, identity
and platform administration — the layer that makes the other four pillars intelligent
and connected.

---

## 5. The Thirty Modules at a Glance

| Pillar | # | Module | New in v2.0 | Priority | Wave |
|---|---|---|:--:|:--:|:--:|
| **A** | M01 | Service & Repair Management | Expanded | P0 | W1–W2 |
| A | M02 | Field Service & Dispatch Management | Expanded | P0 | W2 |
| A | M03 | Logistics, Pick & Drop & Reverse Logistics | ★ New | P1 | W3 |
| A | M04 | Front Desk, Queue & Branch Operations | Expanded | P1 | W1 |
| A | M05 | Remote Support & Managed Services (MSP/RMM) | ★ New | P1 | W5 |
| A | M06 | Data Services — Recovery, Backup & Destruction | ★ New | P2 | W6 |
| **B** | M07 | Customer Relationship Management & Customer 360 | Expanded | P0 | W1 |
| B | M08 | Contract Lifecycle Management (AMC/RAMC/MSP/SLA) | Expanded | P1 | W4 |
| B | M09 | Warranty & Claims Management | Expanded | P0 | W4 |
| B | M10 | Loyalty, Referral & Campaign Management | Expanded | P1 | W2 |
| B | M11 | Sales, Quotation & Dynamic Pricing | ★ New | P1 | W3 |
| B | M12 | E-Commerce, Parts Retail & Marketplace | ★ New | P1 | W7 |
| B | M13 | Rental & Asset-as-a-Service | ★ New | P2 | W6 |
| B | M14 | Trade-In, Refurbishment & Resale | ★ New | P2 | W6 |
| **C** | M15 | Inventory & Spare Parts Management | Expanded | P0 | W2 |
| C | M16 | Procurement, Vendor & Supplier Management | Expanded | P1 | W3 |
| C | M17 | Asset, Device Registry & IoT Telemetry | Expanded | P1 | W2 / W8 |
| C | M18 | E-Waste, Recycling & Sustainability (ESG) | ★ New | P3 | W8 |
| **D** | M19 | Financial Management & Bangladesh Compliance | Expanded | P0 | W3 |
| D | M20 | Billing, Revenue Recognition & Settlement | ★ New | P1 | W4 / W7 |
| D | M21 | HR, Payroll & Workforce Management | Expanded | P1 | W5 |
| D | M22 | Learning, Certification & Technician Competency | ★ New | P2 | W5 |
| D | M23 | Quality, ISO & Compliance Management | Expanded | P1 | W5 |
| D | M24 | Document Management, E-Signature & Records | Expanded | P1 | W3 |
| **E** | M25 | Business Intelligence & Data Platform | Expanded | P1 | W4 / W8 |
| E | M26 | AI/ML Services | ★ New | P2 | W6–W8 |
| E | M27 | Conversational AI & Omnichannel Contact Centre | ★ New | P1 | W4 |
| E | M28 | Integration, API & Event Platform | Expanded | P0 | W1 |
| E | M29 | Identity, Security, Access & Audit | Expanded | P0 | W1 |
| E | M30 | Platform Administration & Multi-Entity/Multi-Country | ★ New | P2 | W9 |

★ = module that did not exist in the v1.0 plan.

---

## 6. Business Case

### 6.1 Investment

| Category | v1.0 (3-yr) | v2.0 (3-yr) | Delta |
|---|---|---|---|
| Software licensing | $0 | $0 – $36,000 | +$36K (optional L6 SaaS: telephony, RMM agent, e-sign) |
| Implementation & custom development | $111K – $200K | $290K – $470K | +$179K – $270K |
| Infrastructure / hosting | $17K – $30K | $52K – $96K | +$35K – $66K |
| Third-party APIs | $16K – $38K | $41K – $95K | +$25K – $57K |
| Training & change management | $8K – $15K | $22K – $43K | +$14K – $28K |
| Support & maintenance (Yr 2–3) | $30K – $60K | $50K – $110K | +$20K – $50K |
| **3-Year TCO** | **$182K – $342K** | **$455K – $780K** | **+$273K – $438K** |

Software licensing remains at or near zero: the stack is Odoo 19 Community Edition,
OCA modules and self-hosted open source. The increase is almost entirely **people and
infrastructure**, both of which scale down cleanly if waves are deferred.

### 6.2 Return

Annual steady-state benefit, base case, three years after Wave 1 go-live:

| Benefit | v1.0 Base Case | v2.0 Base Case | Source |
|---|---|---|---|
| Warranty revenue recovery | BDT 100 lac | BDT 100 lac | M09 |
| Technician productivity | BDT 90 lac | BDT 130 lac | M02 + M26 AI dispatch |
| Inventory cost reduction | BDT 20 lac | BDT 34 lac | M15 + M26 demand forecasting |
| Administrative labour savings | BDT 35 lac | BDT 62 lac | Cross-module automation |
| Customer retention | BDT 55 lac | BDT 78 lac | M07 + M10 + M27 |
| AMC/RAMC renewal uplift | BDT 50 lac | BDT 72 lac | M08 |
| Financial close & cash flow | BDT 18 lac | BDT 26 lac | M19 + M20 |
| **New: Managed services (MSP) contribution** | — | BDT 95 lac | M05 |
| **New: Rental gross margin** | — | BDT 48 lac | M13 |
| **New: Refurbishment & resale margin** | — | BDT 65 lac | M14 |
| **New: Marketplace commission & ads** | — | BDT 84 lac | M12 |
| **New: Data services** | — | BDT 30 lac | M06 |
| **New: E-waste material recovery** | — | BDT 12 lac | M18 |
| **New: Dynamic pricing margin uplift** | — | BDT 40 lac | M11 |
| **Total annual benefit (BDT)** | **368 lac** | **876 lac** | |
| **Total annual benefit (USD @110)** | **~$335K** | **~$797K** | |

### 6.3 Payback

| Scenario | 3-Year Benefit | 3-Year Cost | Net | ROI | Payback |
|---|---|---|---|---|---|
| Conservative | $1.24M | $780K | $460K | 59% | 24 months |
| Base case | $1.96M | $610K | $1.35M | 221% | 17 months |
| Optimistic | $2.61M | $455K | $2.16M | 475% | 12 months |

Benefit realisation is deliberately lagged: new business lines (Waves 5–8) contribute
nothing until they go live, so the first two years of the v2.0 case are close to the v1.0
case. The step change occurs in Year 3.

### 6.4 The Cost of Not Expanding

| If deferred | Consequence |
|---|---|
| Managed services without a system | MSP contracts sold but delivered manually; SLA credits leak; the segment stays sub-scale |
| Rental without a system | No utilisation tracking, no damage recovery, no depreciation discipline — asset write-offs |
| Marketplace without a system | Cannot onboard external capacity; growth capped at owned technician headcount |
| Refurb & trade-in without a system | No device provenance, no grading consistency, warranty exposure on resold units |
| Multi-country deferred to a v3.0 rebuild | Retrofitting multi-entity into a live single-entity ERP typically costs 3–5× the cost of designing for it |
| Second ERP for new lines | Guaranteed reconstruction of today's fragmentation |

---

## 7. Guiding Principles for v2.0

| # | Principle | What It Means In Practice |
|---|---|---|
| 1 | **One system of record** | Every business object with a lifecycle or financial consequence is mastered in the ERP. Portals and apps hold no authoritative state. |
| 2 | **Zero licence cost by default** | Odoo 19 CE + OCA + self-hosted open source. Commercial components (L6) require CFO approval and a documented open-source alternative assessment. |
| 3 | **Configure before extend, extend before fork** | Selection hierarchy L1→L2→L3→L4→L5. Forking an OCA module requires architectural review. |
| 4 | **API-first and event-driven** | Every module exposes documented APIs and emits domain events. No module reads another module's tables. |
| 5 | **Bengali-first for field and customer surfaces** | Bengali is the primary language for technician and customer interfaces; English for back office. |
| 6 | **Offline-capable where the work is offline** | Technician, logistics and field-audit applications must operate 24 hours without connectivity. |
| 7 | **Multi-entity and multi-currency from the schema up** | Even while operating one entity in one country, the data model carries entity, branch, currency and locale dimensions. |
| 8 | **Compliance is a feature, not a project** | ISO 9001:2015, ISO 27001, NBR VAT/TDS, Bangladesh Labour Act and e-waste rules are modelled as enforced system behaviour. |
| 9 | **Every module is measurable** | No module ships without its KPI set instrumented and visible in M25. |
| 10 | **Automate to 85%** | v1.0 targeted 70% automation of routine work. v2.0 targets 85% by Wave 8, using M26 AI services. |

---

## 8. What Remains Out of Scope

| # | Excluded | Rationale |
|---|---|---|
| OOS-01 | Development of the corporate website and Next.js portal platform | Separate programme; ERP integrates, does not replace |
| OOS-02 | Manufacturing or assembly of devices | Not a 1000FiX business |
| OOS-03 | Consumer lending / instalment underwriting | Regulated activity; partner-provided, ERP records only the receivable |
| OOS-04 | Full-scope Enterprise Asset Management for client-owned plant machinery | M17 covers IT, mobile, appliance and rental assets only |
| OOS-05 | Building a proprietary payment switch | Uses bKash / Nagad / SSLCOMMERZ |
| OOS-06 | Replacement of brand partners' internal warranty systems | Integration and portal only |
| OOS-07 | Physical logistics fleet telematics hardware manufacture | Commercial GPS units + Traccar |
| OOS-08 | Custom hardware (kiosks, scanners, RMM appliances) | Standard commercial hardware |
| OOS-09 | Human capital ATS / recruitment marketing | Standard Odoo recruitment only |
| OOS-10 | Country-specific tax engines beyond Bangladesh in Waves 1–8 | M30 provides the framework; country packs are separate projects |

---

## 9. Success Criteria for the Programme

The programme is successful if, 36 months from kickoff:

1. All 14 revenue streams transact end-to-end inside the ERP with no shadow spreadsheets.
2. 85% of routine operational tasks execute without manual intervention.
3. Month-end close completes in ≤ 3 days across all entities and business lines.
4. 95%+ of eligible warranty claims are submitted within 72 hours of service completion.
5. Marketplace external capacity delivers ≥ 25% of total job volume.
6. Managed services and rental together contribute ≥ 20% of revenue.
7. ISO 9001:2015 surveillance audit passes with zero major non-conformances traced to systems.
8. The platform supports a second country entity without core code change.
9. Executive decisions are made on live dashboards, not compiled spreadsheets.
10. Customer CSAT ≥ 4.7/5 and technician app daily active usage ≥ 95%.

---

## 10. Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Chief Executive Officer | | Approve / Approve with conditions / Reject | |
| Chief Technology Officer | | | |
| Chief Financial Officer | | | |
| Service Operations Director | | | |
| Chief Commercial Officer | | | |
| HR Director | | | |
| Quality Manager | | | |

**Conditions of approval to be recorded here:**

---

*Next document: `02_Scope_Expansion_Delta_v1_to_v2.md` — the line-by-line delta and evidence trail.*
