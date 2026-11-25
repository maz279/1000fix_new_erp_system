---
id: 1000FIX-ERP-RFP-2026-002
title: Request for Proposal — Enterprise Resource Planning System & Digital Platform Suite (v2.0 Expanded Scope)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-13
status: DRAFT FOR ISSUE
classification: CONFIDENTIAL
supersedes: 1000FIX-ERP-RFP-2026-001 (v1.0, 17 March 2026)
owner: Chief Technology Officer, 1000FiX Services Limited
---

# REQUEST FOR PROPOSAL (RFP)

# Enterprise Resource Planning System & Digital Platform Suite

# 67 Modules · 11 Categories · 12 Portals · 36 Months

## 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Request for Proposal — Enterprise Resource Planning System & Digital Platform Suite (v2.0 Expanded Scope) |
| **Issuing Organisation** | 1000FiX Services Limited |
| **Document Version** | 2.0 |
| **Date of Issue** | 13 August 2026 |
| **RFP Reference Number** | 1000FIX-ERP-RFP-2026-002 |
| **Supersedes** | 1000FIX-ERP-RFP-2026-001 (v1.0, 17 March 2026) |
| **Submission Deadline** | 30 October 2026, 17:00 (BST, UTC+6) |
| **Contact Person** | Chief Technology Officer, 1000FiX Services Limited |
| **Contact Email** | info@1000fix.com |
| **Contact Phone** | +880 9644-300600 |
| **Hotline** | 16743 |
| **Address** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |
| **Governing Law** | People's Republic of Bangladesh |

---

**CONFIDENTIALITY NOTICE**

This Request for Proposal and all accompanying materials are the confidential property of
1000FiX Services Limited. The information contained herein is intended solely for the use of
prospective respondents invited to submit proposals. Recipients must not disclose, reproduce or
distribute any part of this RFP, or any annexed specification, without the prior written consent
of 1000FiX Services Limited. All information provided by respondents will be treated as
confidential and used solely for the purpose of evaluating proposals. A Non-Disclosure Agreement
must be executed before the detailed module specification set (Annex 1) is released.

---

## HOW THIS DOCUMENT DIFFERS FROM VERSION 1.0

Version 1.0 of this RFP was issued on 17 March 2026 and invited proposals for an ERP covering
**11 modules and 6 portals**, approximately **405 requirements**, over **18 months**, within an
indicative envelope of **USD 150,000–350,000**.

Between March and August 2026 the Company completed a full specification of its business,
benchmarked against SAP S/4HANA Service, Oracle Fusion Cloud, Microsoft Dynamics 365, IFS Cloud
and Odoo 19, and audited the resulting document set twice. The outcome is a materially larger and
materially better-evidenced programme.

| Dimension | RFP v1.0 (Mar 2026) | **RFP v2.0 (Aug 2026)** | Change |
|---|---|---|---|
| ERP modules | 11 | **67 in 11 categories** | +56 |
| Portals & applications | 6 | **12** | +6 |
| Catalogued functional requirements | ~405 *(estimated)* | **2,930 measured, ~2,978 projected** | +~2,573 |
| Revenue streams supported | 5 | **14** | +9 |
| External integrations | 15 | **47** | +32 |
| Data entities | ~40 | **225** | +185 |
| User roles modelled | 20 | **38 registered (46 in use — see §20)** | +18 |
| Non-functional requirements | 30 | **101** | +71 |
| Custom development items | 20 | **~138** | +118 |
| Build effort | not stated | **1,513 person-weeks measured** | — |
| Delivery horizon | 18 months, 6 phases | **36 months, 9 waves** | +18 months |
| Delivery team | 6 | **11 core, 19 at peak** | +13 at peak |
| Indicative 3-year TCO | $150K–350K | **$690K–1,150K** *(restated, see §16.1)* | +$540K–800K |
| Technology position | Vendor-proposed, product-agnostic | **Reference architecture specified** (Odoo 19 CE + OCA + open source + custom), with a permitted alternative-architecture response | Structural |
| Legal-entity model | Single (Bangladesh) | **Multi-entity, multi-country ready** | Structural |
| Data residency | Single region (Singapore) | **Split residency** — Bangladesh-resident store for sensitive personal data | Structural, driven by PDPA 2026 |
| Governing data protection law | Digital Security Act 2018 | **Personal Data Protection Act 2026** + Cyber Security Ordinance 2025 | Corrected — the DSA 2018 has been repealed twice |

**Nothing in v1.0 has been deleted.** Every v1.0 requirement is carried forward into the v2.0
register; four are formally superseded by stronger requirements and are listed in §20.4. The
first 18 months of the v2.0 plan deliver everything v1.0 promised, on substantially the original
dates.

**Respondents who submitted against v1.0** are invited to re-submit against this document. No
part of a v1.0 submission will be carried forward automatically.

---

## TABLE OF CONTENTS

**Part A — Context**
1. [Executive Summary](#1-executive-summary)
2. [Company Background & Market Position](#2-company-background--market-position)
3. [Programme Scope & Business Objectives](#3-programme-scope--business-objectives)
4. [Current Landscape, Pain Points & Legacy Decommissioning](#4-current-landscape-pain-points--legacy-decommissioning)

**Part B — What Is Being Procured**
5. [Reference Architecture & Technology Position](#5-reference-architecture--technology-position)
6. [Functional Requirements — 67 Modules in 11 Categories](#6-functional-requirements--67-modules-in-11-categories)
7. [Portal & Application Suite — P01 to P12](#7-portal--application-suite--p01-to-p12)
8. [Cross-Cutting Specifications](#8-cross-cutting-specifications)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Security, Data Protection & Regulatory Compliance](#10-security-data-protection--regulatory-compliance)
11. [Data Migration & Legacy Cutover](#11-data-migration--legacy-cutover)

**Part C — How It Will Be Delivered**
12. [Implementation Approach — 9 Waves Over 36 Months](#12-implementation-approach--9-waves-over-36-months)
13. [Training, Change Management & Adoption](#13-training-change-management--adoption)
14. [Support, Maintenance, Hypercare & Warranty](#14-support-maintenance-hypercare--warranty)

**Part D — Commercial & Procurement**
15. [Respondent Qualification Requirements](#15-respondent-qualification-requirements)
16. [Commercial Structure & Pricing Response](#16-commercial-structure--pricing-response)
17. [Evaluation Methodology & Scoring](#17-evaluation-methodology--scoring)
18. [Submission Instructions & Procurement Timetable](#18-submission-instructions--procurement-timetable)
19. [Contractual Terms & Conditions](#19-contractual-terms--conditions)

**Part E — Disclosure & Reference**
20. [Disclosed Open Items, Known Defects & Programme Risks](#20-disclosed-open-items-known-defects--programme-risks)
21. [Appendices](#21-appendices)

---
---

# PART A — CONTEXT

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose of This RFP

1000FiX Services Limited ("1000FiX" or "the Company") invites proposals from qualified
systems integrators, ERP implementation partners and software engineering firms for the
**design, build, integration, data migration, deployment, training and ongoing support** of a
comprehensive Enterprise Resource Planning system and a twelve-surface digital platform suite.

This is a **build-and-integrate procurement, not a product-selection procurement.** The Company
has completed its own architecture, build-versus-buy analysis and module specification. The
reference architecture is defined in §5. Respondents are being asked to deliver against a
specification the Company owns — not to sell a product and fit the business to it.

Respondents may nonetheless propose an **alternative architecture** under the terms of §5.7. Such
proposals will be evaluated, but must demonstrate a materially better outcome against the same
requirement set, the same regulatory constraints and the same total cost of ownership horizon.

### 1.2 What Is Being Bought

| # | Deliverable | Scale |
|---|---|---|
| 1 | ERP system of record | **67 modules** across 11 categories |
| 2 | Digital platform suite | **12 portals and applications** |
| 3 | Functional delivery | **2,930 measured functional requirements** (~2,978 projected on completion of the final two specifications) |
| 4 | Non-functional compliance | **101 non-functional requirements** across performance, availability, scalability, security, usability, compliance, operability, data integrity and localisation |
| 5 | Integration | **47 external integrations**, plus the contracted API and event contract with the existing Next.js portal platform |
| 6 | Data model | **225 entities** with dimensional context, residency classification and audit |
| 7 | Access model | **38 registered roles**, 6 data isolation tiers, 30 segregation-of-duties controls, field-level permissions |
| 8 | Data migration | 9 source domains; 800,000+ transactional records; 3+ years of financial history |
| 9 | Delivery | **9 waves over 36 months**, each with a formal gate |
| 10 | Adoption | 500–900 internal users across 51+ locations; 250,000+ monthly external users; 1,000–3,000 external party users |
| 11 | Support | Hypercare per wave, then a steady-state support agreement |

### 1.3 Strategic Rationale

The Company has committed — in its board-approved business plan, its Service App scope of work
and its portal technology roadmap — to operating **fourteen distinct revenue streams**. The
originally approved ERP could run five of them. The remaining nine are existing commitments
without a system of record:

| # | Revenue Stream | In v1.0 ERP scope | Owning Module |
|---|---|:--:|---|
| 1 | Authorised brand warranty service | ✓ | M09 |
| 2 | Out-of-warranty paid repair | ✓ | M01 / M31 |
| 3 | AMC / RAMC maintenance contracts | ✓ | M08 |
| 4 | Warranty extension & protection products | ✓ | M09 |
| 5 | Spare parts & accessories | ✓ | M15 / M38 |
| 6 | **Corporate managed IT services (MSP)** | — | M05 |
| 7 | **Equipment rental / Equipment-as-a-Service** | — | M13 |
| 8 | **Data recovery** | — | M06 |
| 9 | **Data backup & archival subscriptions** | — | M06 / M39 |
| 10 | **Refurbished device resale** | — | M14 |
| 11 | **Trade-in / exchange margin** | — | M14 |
| 12 | **E-waste recycling & material recovery** | — | M18 |
| 13 | **Marketplace commission & settlement** | — | M12 |
| 14 | **Advertising, boost & lead placement** | — | M12 / M35 |

Running streams 6–14 on spreadsheets alongside a modern ERP would recreate, within three years,
exactly the fragmentation the ERP is being bought to remove. The scope was therefore expanded
**before build starts**, so that every revenue stream the Company intends to operate has a system
of record from the day it launches.

### 1.4 Expected Business Outcomes

Eighteen business objectives are defined, each measurable, owned and traced to modules. The
headline set:

| ID | Objective | Baseline | Target | By Month |
|---|---|---|---|:--:|
| BO-01 | Automate the service order lifecycle | 20% | **85%** | 34 |
| BO-02 | Maximise field technician productivity | 4–5 jobs/day | **8–9 jobs/day** | 26 |
| BO-03 | Inventory accuracy across all locations | 75% | **98%+** | 18 |
| BO-04 | Recover all eligible warranty revenue (claims within 72 h) | ~50% at 30–90 days | **95%+** | 18 |
| BO-05 | Customer satisfaction and turnaround | CSAT 3.8/5 | **4.7/5**, <24 h IT, <4 h appliance | 22 |
| BO-06 | Compress the financial close | 15–20 days | **≤ 3 days** | 20 |
| BO-07 | Real-time management visibility | Days | **Real-time** | 18 |
| BO-08 | Grow contract subscriptions | 60% renewal | **88% renewal, 2.5× base** | 30 |
| BO-09 | Remove capacity constraints on growth | Baseline | **+87% revenue over 18 months post-W4** | 36 |
| BO-10 | Full Bangladesh regulatory compliance | Manual, error-prone | **Zero findings, zero late filings** | 18 |
| BO-11 | Managed services as a material revenue line | 0% | **≥ 12% of revenue** | 34 |
| BO-12 | Scale delivery beyond owned headcount | 0% | **≥ 25% of jobs via marketplace** | 34 |
| BO-13 | Rental as a profitable asset business | n/a | **68% utilisation, 55% gross margin** | 32 |
| BO-14 | Build a circular device business | 0 | **12,000 refurbished units/yr at 22% margin** | 34 |
| BO-15 | Competency as an enforced control | Unknown | **Zero claims rejected for uncertified technician** | 24 |
| BO-16 | Every customer conversation in the system | ~0% | **100%** | 20 |
| BO-17 | Decisions made on live data | 100% manual packs | **Zero manual packs** | 34 |
| BO-18 | Readiness to operate in a second country | Not possible | **Country pack in ≤ 12 weeks** | 36 |

### 1.5 Business Case Summary

| Scenario | 3-Year Benefit | 3-Year Cost | Net | ROI | Payback |
|---|---:|---:|---:|---:|---|
| Conservative | $1.24M | $1.15M | $90K | 8% | 32 months |
| **Base case** | **$1.96M** | **$0.92M** | **$1.04M** | **113%** | **22 months** |
| Optimistic | $2.61M | $0.69M | $1.92M | 278% | 15 months |

Annual steady-state benefit at Year 3+ is modelled at **BDT 876 lac (~USD 797K)** in the base
case, of which BDT 334 lac derives from the nine new revenue streams. The cost line above uses
the **restated** TCO of §16.1; the return figures in the Company's internal charter documents
were computed against the superseded cost line and are being re-baselined.

### 1.6 What This RFP Is Not

| Out of scope | Rationale |
|---|---|
| Development or replacement of the corporate website and the Next.js portal platform | Separate programme; the ERP integrates with it and does not replace it (constraint CON-03) |
| Manufacturing or assembly of devices | Not a 1000FiX business |
| Consumer lending or instalment underwriting | Regulated activity; partner-provided. The ERP records the receivable only |
| Full-scope Enterprise Asset Management for client-owned plant machinery | M17/M45 cover IT, mobile, appliance, test and rental assets only |
| Building a proprietary payment switch | Integrates with bKash, Nagad, SSLCOMMERZ |
| Replacement of brand partners' internal warranty systems | Integration and portal only |
| Manufacture of telematics or custom hardware (kiosks, scanners, RMM appliances) | Standard commercial hardware |
| Country-specific tax engines beyond Bangladesh in Waves 1–8 | M65 provides the framework; country packs are separate projects |

---

## 2. COMPANY BACKGROUND & MARKET POSITION

### 2.1 Company Profile

| Attribute | Details |
|---|---|
| **Legal name** | 1000FiX Services Limited |
| **Trading name** | 1000FiX |
| **Industry** | After-sales service — IT, electronics, mobile devices, home appliances |
| **Founded** | 29 August 2017 |
| **Head office** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |
| **Hotline** | 16743 (16 + "Fix" on the Bangla keypad) |
| **Phone** | +880 9644-300600 |
| **WhatsApp** | +880 1904 095968 |
| **Email** | info@1000fix.com |
| **Website** | https://1000fix.com |
| **Certification** | ISO 9001:2015 — Bangladesh's first and only ISO-certified IT service provider |
| **Service centres** | 51+ across all 8 administrative divisions |
| **Employees** | 500+, including 200–400 field technicians |
| **Customers served** | 250,000+ per month |
| **Brand partnerships** | 17+ authorised warranty service agreements *(figure under verification — see §20.2)* |

### 2.2 Market Position

- **Largest** after-sales ICT, electronics and home-appliance service provider in Bangladesh
- **Only** ISO 9001:2015 certified IT service provider in the country
- **Authorised warranty service partner** for 17+ international brands
- **Most extensive service network** — 51+ centres covering all 8 administrative divisions
- **Multi-channel delivery** — on-site, pick & drop, walk-in, workshop/depot and remote

### 2.3 Authorised Brand Partnerships

| Category | Brands |
|---|---|
| Computers & laptops | Dell, HP, Lenovo, Acer, Toshiba, Gigabyte, Microsoft (Surface) |
| Consumer electronics | Samsung, Sony, BenQ |
| Mobile devices | Xiaomi, Huawei, Honor |
| Components | Intel, TwinMOS, Delux |
| Printers & peripherals | Epson |
| Other | PNS |

The full brand matrix, with product categories serviced and warranty type, is at Appendix C.
Each brand partner has its own claim format, evidence requirements, rate card and certification
requirements — a core driver of module M09 and portal P08.

### 2.4 Service Portfolio

#### 2.4.1 IT equipment
Laptop and notebook repair (Level 1–3) · desktop repair (brand and clone) · MacBook and Apple
products · server repair and maintenance · printer, photocopier and plotter · motherboard-level
diagnostics and repair · monitor and display · projector · UPS · router and networking · CCTV and
surveillance · Microsoft Surface.

#### 2.4.2 Home appliances
Air conditioning — installation, jet wash, hydraulic service, dismantling, gas refill, leakage
repair, basic servicing · refrigerator — service, repair, cleaning, gas refill, installation ·
television — all types, display and technical repair · washing machine — overhaul, repair,
maintenance · microwave and oven · geyser and water heater · treadmill and fitness equipment ·
combination service packages.

#### 2.4.3 Mobile & tablet
Mobile phone repair (Samsung, Xiaomi, Huawei, Honor and others) · tablet repair · speaker repair ·
warranty and out-of-warranty support.

#### 2.4.4 New and expanded service lines (v2.0)
Managed IT services and 24/7 remote support · data recovery (HDD, SSD, RAID, USB, memory card,
mobile, email/database) · data backup and archival subscriptions (cloud, on-site, hybrid,
continuous data protection) · certified data destruction · equipment rental across eight asset
categories · trade-in, refurbishment, grading and resale · e-waste collection, recycling and
certified disposal · marketplace intermediation for external engineers and shops.

#### 2.4.5 Service delivery modes
1. **On-site / home service** — technician visits the customer
2. **Pick & drop** — collection, workshop repair, return delivery
3. **Walk-in** — direct visit to any of 51+ centres
4. **Workshop / depot** — bench repair with WIP and bench management
5. **Remote support** — remote diagnostics, software support, managed monitoring

#### 2.4.6 Value-added programmes
Privilege Program (Silver, Gold, Diamond) · Residential Annual Maintenance Contract (RAMC — 6
packages) · Corporate AMC · IT Infrastructure AMC · Healthcare Equipment AMC with calibration ·
Specialty Equipment AMC · Managed Service Contracts (6 types) · Warranty extension and protection
products (7 families) · Partner Alliance Program · laptop and equipment rental · device exchange
and trade-in · referral programme.

### 2.5 Organisation, User Population & Roles

| Category | Population | Primary Surface |
|---|---:|---|
| Executive & management | 5–10 | P03, P06 |
| Service operations (agents, dispatchers, workshop supervisors) | 180–300 | P03 |
| Field technicians | 200–400 | P02 |
| Logistics coordinators & riders | 60–175 | P09, P03 |
| Inventory, warehouse & procurement | 75–125 | P03, P05 |
| Finance & accounting | 15–30 | P03, P06 |
| Human resources | 10–15 | P03 |
| Sales, marketing & account management | 15–30 | P03, P06 |
| Contact centre agents & supervisors | 34–70 | P10 |
| Quality, audit & compliance | 5–15 | P03, P06, P11 |
| IT administration | 4–8 | P03 |
| **Total internal users** | **500–900** | |
| Individual customers | **250,000+/month** | P01 |
| Corporate B2B portal users | 500–2,000 | P04 |
| External parties (vendors, sellers, brands, couriers, partners) | 1,000–3,000 | P05, P07, P08, P09, P12 |

The formal role register defines **38 roles (R01–R38)**, mapped to portals, MFA requirements and
data isolation tiers. Eight further roles are in active use in the module specifications and are
being formalised — see §8.3 and §20.2.

### 2.6 Geographic Coverage

| Division | Key cities | Network role |
|---|---|---|
| **Dhaka** | Dhaka, Gazipur, Narayanganj, Savar, Tangail, Manikganj | HQ + central warehouse + ~20 centres |
| **Chittagong** | Chittagong, Cox's Bazar, Comilla, Noakhali | Regional hub + centres |
| **Rajshahi** | Rajshahi, Bogra, Pabna | Regional hub + centres |
| **Khulna** | Khulna, Jessore, Satkhira | Regional hub + centres |
| **Sylhet** | Sylhet, Moulvibazar | Centres |
| **Barisal** | Barisal, Patuakhali | Centres |
| **Rangpur** | Rangpur, Dinajpur | Centres |
| **Mymensingh** | Mymensingh, Jamalpur | Centres |

The address model in the ERP is **Division → District → Upazila/Thana → Union/Ward → Postcode**
across 8 divisions and 64 districts. The platform must support **200 branches without
configuration redesign** (NFR-058).

---

## 3. PROGRAMME SCOPE & BUSINESS OBJECTIVES

### 3.1 Scope at a Glance

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     1000FiX DIGITAL ESTATE (v2.0)                            │
│                                                                              │
│   ┌────────────────────────┐        ┌──────────────────────────────┐        │
│   │  CORPORATE WEBSITE     │        │  EXPERIENCE LAYER            │        │
│   │  (Next.js + Payload)   │◄──────►│  12 portals & applications   │        │
│   │  OUT OF SCOPE          │        │  P01 … P12   IN SCOPE        │        │
│   └───────────┬────────────┘        └──────────────┬───────────────┘        │
│               │      REST / JSON-2 / GraphQL / Webhooks / Events            │
│               └──────────────────┬─────────────────┘                        │
│                                  ▼                                          │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │           1000FiX ERP v2.0 — SYSTEM OF RECORD    IN SCOPE            │  │
│   │  67 modules · 11 categories · 2,930 requirements · 225 entities      │  │
│   │  Odoo 19 CE + OCA + open source + custom development                 │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│   ┌──────────────────────────────▼───────────────────────────────────────┐  │
│   │  DATA & INTELLIGENCE PLATFORM                       IN SCOPE         │  │
│   │  PostgreSQL 16 · TimescaleDB · ClickHouse · Metabase · MLflow        │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule.** The ERP owns *state and truth*; the portals own *experience and reach*. Any
business object that has a lifecycle, a financial consequence or an audit obligation is mastered
in the ERP. **Portals never hold authoritative state.** Respondents must design to this rule; a
proposal that places business logic in a portal will be marked down under §17.

### 3.2 The Eleven Module Categories

| Cat | Category | Modules | Requirements | Effort (PW) | Accountable Executive |
|---|---|---:|---:|---:|---|
| **A** | Service Delivery & Operations | 7 | 362 | 206 | Service Operations Director |
| **B** | Customer Engagement & Experience | 7 | 320 | 148 | Chief Commercial Officer |
| **C** | Commercial, Pricing & Revenue | 9 | 494 | 262 | Chief Commercial Officer |
| **D** | Circular & Asset-Based Business | 3 | 109 | 60 | Corporate Services / Retail Ops Head |
| **E** | Supply Chain & Inventory | 6 | 235 | 119 | Supply Chain Director |
| **F** | Asset, Equipment & Facilities | 5 | 232 | 114 | Service Ops Director / CTO |
| **G** | Finance & Treasury | 8 | 333 | 185 | Chief Financial Officer |
| **H** | People & Workforce | 7 | 310 | 124 | HR Director |
| **I** | Governance, Risk, Quality & Knowledge | 4 | 170 | 78 | Quality Manager / CFO |
| **J** | Data, Analytics & Intelligence | 4 | 146 | 97 | Chief Technology Officer |
| **K** | Platform & Technology | 7 | 219 *(5 of 7 specified)* | 120 | Chief Technology Officer |
| | **Total** | **67** | **2,930 measured** | **1,513** | |

*Figures counted by direct enumeration of the module specification files on 13 August 2026. Two
Category K specifications (M66, M67) remain outstanding; their estimated 48 requirements and
25 PW bring the projected total to ~2,978 requirements and ~1,538 PW. See §20.1.*

### 3.3 Priority Model

| Priority | Count | Definition | Descope authority |
|---|---:|---|---|
| **P0** | 13 modules | Regulatory, safety or go-live blocking | Cannot be descoped |
| **P1** | 31 modules | Must-have — core business capability | CEO approval only |
| **P2** | 21 modules | Important — significant value, deferrable one wave | PMO change control |
| **P3** | 2 modules | Desirable — enhances experience or efficiency | Backlog, opportunistic |

At requirement level the distribution is approximately **P0 23% · P1 43% · P2 27% · P3 7%**.

**P0 modules:** M01, M02, M09, M15, M19, M20, M28, M29, M30, M33, M37, M51, M56.

### 3.4 Business Objectives — Full Register

| ID | Objective | Metric | Baseline | Target | By | Owner | Modules |
|---|---|---|---|---|:--:|---|---|
| BO-01 | Automate the service order lifecycle | % processed without manual intervention | 20% | 85% | M34 | Ops Director | M01, M02, M20 |
| BO-02 | Maximise field technician productivity | Jobs per technician per day | 4–5 | 8–9 | M26 | Ops Director | M02, M26 |
| BO-03 | Inventory accuracy across all locations | Accuracy rate | 75% | 98%+ | M18 | Inventory Manager | M15 |
| BO-04 | Recover all eligible warranty revenue | % claims submitted within 72 h | ~50% at 30–90 d | 95%+ | M18 | Finance Director | M09 |
| BO-05 | Improve satisfaction, reduce turnaround | CSAT · TAT | 3.8/5 · unmeasured | 4.7/5 · <24 h IT, <4 h appliance | M22 | Customer Service Manager | M01, M07, M27 |
| BO-06 | Compress the financial close | Days to close | 15–20 | ≤ 3 | M20 | CFO | M19, M20 |
| BO-07 | Real-time management visibility | Time to branch performance data | Days | Real-time | M18 | CEO | M25 |
| BO-08 | Grow contract subscriptions | Renewal rate · contract base | 60% · baseline | 88% · 2.5× | M30 | CCO | M08, M10 |
| BO-09 | Remove capacity constraints on growth | Annual revenue growth | Baseline | +87% over 18 months post-W4 | M36 | CEO | All |
| BO-10 | Full Bangladesh regulatory compliance | Findings · late filings | Manual, error-prone | Zero | M18 | CFO / HR Director | M19, M51, M56, M23 |
| BO-11 | Managed services as a material revenue line | MSP revenue share | 0% | ≥ 12% | M34 | Corporate Services Head | M05, M08 |
| BO-12 | Scale beyond owned headcount | Marketplace share of job volume | 0% | ≥ 25% | M34 | CCO | M12 |
| BO-13 | Rental as a profitable asset business | Utilisation · gross margin | n/a | 68% · 55% | M32 | Corporate Services Head | M13 |
| BO-14 | Build a circular device business | Refurbished units/yr · margin | 0 | 12,000 · 22% | M34 | Retail Operations Head | M14, M18 |
| BO-15 | Competency as an enforced control | Claims rejected for uncertified technician | Unknown | Zero | M24 | Quality Manager | M22 |
| BO-16 | Every conversation in the system | Conversations captured | ~0% | 100% | M20 | Customer Service Manager | M27 |
| BO-17 | Decisions on live data | Manual reporting packs | 100% | Zero | M34 | CTO | M25, M62 |
| BO-18 | Second-country readiness | Time to stand up a country pack | Not possible | ≤ 12 weeks | M36 | CTO | M65 |

### 3.5 Programme Success Criteria

The programme is successful if, at Month 36:

1. All 14 revenue streams transact end-to-end inside the ERP with **no shadow spreadsheets**.
2. **85%** of routine operational tasks execute without manual intervention.
3. Month-end close completes in **≤ 3 days** across all entities and business lines.
4. **95%+** of eligible warranty claims are submitted within 72 hours of service completion.
5. Marketplace external capacity delivers **≥ 25%** of total job volume.
6. Managed services and rental together contribute **≥ 20%** of revenue.
7. ISO 9001:2015 surveillance audit passes with **zero major non-conformances** traced to systems.
8. The platform supports a **second country entity without core code change**.
9. Executive decisions are made on live dashboards, not compiled spreadsheets.
10. Customer CSAT **≥ 4.7/5** and technician app daily active usage **≥ 95%**.

### 3.6 Guiding Principles the Solution Must Honour

| # | Principle | What it means in practice |
|---|---|---|
| 1 | **One system of record** | Every business object with a lifecycle or financial consequence is mastered in the ERP. Portals and apps hold no authoritative state. |
| 2 | **Zero licence cost by default** | Odoo 19 CE + OCA + self-hosted open source. Commercial components require CFO approval and a documented open-source alternative assessment. |
| 3 | **Configure before extend, extend before fork** | Selection hierarchy L1→L2→L3→L4→L5→L6. Forking an OCA module requires architecture-board approval. |
| 4 | **API-first and event-driven** | Every module exposes documented APIs and emits domain events. No module reads another module's tables. |
| 5 | **Bengali-first for field and customer surfaces** | Bengali is primary for technician and customer interfaces; English for back office. |
| 6 | **Offline-capable where the work is offline** | Technician, logistics and field-audit applications operate 24 hours without connectivity. |
| 7 | **Multi-entity and multi-currency from the schema up** | Even while operating one entity in one country, every record carries entity, branch, currency and locale dimensions. |
| 8 | **Compliance is a feature, not a project** | ISO 9001:2015, ISO 27001, NBR VAT/TDS, Bangladesh Labour Act, PDPA 2026 and e-waste rules are modelled as enforced system behaviour. |
| 9 | **Every module is measurable** | No module ships without its KPI set instrumented and visible in M25. |
| 10 | **Automate to 85%** | v1.0 targeted 70% automation of routine work. v2.0 targets 85% by Wave 8, using M26 AI services. |

---

## 4. CURRENT LANDSCAPE, PAIN POINTS & LEGACY DECOMMISSIONING

### 4.1 Current Systems

| System / practice | Description | Limitation |
|---|---|---|
| WordPress website | Public web presence | 5–7 s load, limited functionality, poor mobile experience |
| `station.1000fix.com` | Order tracking | Standalone; no ERP linkage |
| Legacy tracker `123.0.26.238/orderTracking` | Order tracking | Unsupported, unsecured, no integration |
| Per-branch spreadsheets | Service order tracking | No real-time visibility, error-prone, not scalable |
| Workshop whiteboards & paper job cards | WIP management | No WIP ageing, no bench utilisation data |
| WhatsApp / phone dispatch | Technician assignment | No optimisation, no tracking, no performance data |
| Standalone accounting software | Financial management | No integration with operations; manual re-keying |
| Branch inventory spreadsheets | Stock control | No network visibility; stockouts alongside excess |
| Email / paper warranty claims | Brand partner claims | Slow processing, revenue leakage, no tracking |
| Attendance sign-in books | Attendance | Manual, unverifiable |
| Manual payroll in Excel | Payroll | 3-day cycle, error-prone, no statutory automation |
| Paper ISO records | Quality management | Audit evidence assembled manually |
| No CRM | Customer data | No 360° view, no service history, no segmentation |
| Ad-hoc remote support tools | Remote assistance | No session record, no billing linkage |

### 4.2 Key Pain Points

| # | Pain point | Business impact |
|---|---|---|
| 1 | No unified system | Data silos; decisions on incomplete information |
| 2 | Manual service order processing | Slow turnaround, errors, customer dissatisfaction |
| 3 | Inefficient dispatch | 4–5 jobs/technician/day; ~35% of the day in travel |
| 4 | Poor inventory visibility | Stockouts at one location while excess sits at another |
| 5 | Delayed warranty billing | 15–20% revenue leakage; 60–120 days to reimbursement |
| 6 | No real-time tracking | Customers and management cannot see status |
| 7 | Manual financial processes | 15–20 day close; reconciliation errors |
| 8 | No performance analytics | Technician, branch and service quality unmeasurable |
| 9 | Scalability constraints | Current processes cannot support planned growth |
| 10 | Customer retention risk | No loyalty management, no proactive engagement |
| 11 | **New business lines with no system** | MSP, rental, refurbishment, marketplace, data services and recycling have been committed commercially but have no system of record |
| 12 | **Competency lapses invisible** | Brand certification expiry is discovered when a claim is rejected |
| 13 | **Conversations outside the system** | The hotline 16743 and WhatsApp traffic leave no record |

### 4.3 Legacy Decommission Map

The successful respondent is accountable for the **complete withdrawal** of each legacy practice
at the wave stated. A wave gate is not passed while its legacy process is still running in
parallel beyond the agreed parallel-run period (§12.6).

| Legacy system / practice | Replaced by | Wave |
|---|---|:--:|
| Service order spreadsheets (per branch) | M01 + M04 | W2 |
| Workshop whiteboards and paper job cards | M31 | W2 |
| WhatsApp / phone dispatch | M02 + M27 | W2 |
| Paper service forms and QC checklists | M01 + M02 + M23 | W2 |
| Branch inventory spreadsheets | M15 | W2 |
| `station.1000fix.com` order tracking | P01 Customer Portal | W2 |
| Legacy tracker `123.0.26.238/orderTracking` | P01 Customer Portal | W2 |
| Phone-coordinated pick & drop | M03 | W3 |
| Standalone accounting software | M19 + M20 + M52 | W3 |
| Manual invoice preparation | M20 | W3 |
| Email-based warranty claims | M09 + P08 | W4 |
| AMC tracking spreadsheets | M08 | W4 |
| Manual payroll in Excel | M56 | W5 |
| Attendance sign-in books | M55 | W5 |
| Paper ISO records | M23 + M24 | W5 |
| Ad-hoc remote support tools | M05 | W5 |
| Data recovery job cards | M06 | W6 |
| Rental log books | M13 | W6 |
| Refurbishment tally sheets | M14 | W6 |
| Manual partner commission calculation | M53 | W7 |
| Excel management reporting packs | M25 + M62 | W8 |

---
---

# PART B — WHAT IS BEING PROCURED

---

## 5. REFERENCE ARCHITECTURE & TECHNOLOGY POSITION

### 5.1 Architectural Position

```
                          ┌─────────────────────────────────────┐
                          │        EXPERIENCE LAYER             │
                          │  12 portals & applications (P01–P12)│
                          │  Next.js 15 · Flutter · Odoo Web    │
                          └──────────────────┬──────────────────┘
                                             │
                          ┌──────────────────▼──────────────────┐
                          │      EXPERIENCE API GATEWAY         │
                          │  Kong · OAuth2/OIDC · Rate limiting │
                          │  BFF per portal · GraphQL federation│
                          └──────────────────┬──────────────────┘
                                             │
   ┌─────────────────────────────────────────▼─────────────────────────────────┐
   │                  1000FiX ERP v2.0 — SYSTEM OF RECORD                      │
   │   11 categories · 67 modules                                              │
   │  ┌─────────────────────────────────────────────────────────────────────┐  │
   │  │ SHARED KERNEL — party · product · location · entity · document ·    │  │
   │  │                 event                                                │  │
   │  └─────────────────────────────────────────────────────────────────────┘  │
   └───────────────────────────────────┬───────────────────────────────────────┘
                                       │
   ┌───────────────────────────────────▼───────────────────────────────────────┐
   │                     DATA & INTELLIGENCE PLATFORM                          │
   │  PostgreSQL 16 (OLTP) · TimescaleDB (telemetry) · ClickHouse (OLAP)       │
   │  Redis · Object storage · MLflow · Metabase · Grafana                     │
   └───────────────────────────────────────────────────────────────────────────┘
```

### 5.2 The Shared Kernel

Six concepts are modelled once, in a shared kernel owned by the platform team. Changing a kernel
concept requires architecture-board review.

| Kernel concept | Odoo basis | Extended by | Used by |
|---|---|---|---|
| **Party** (customer, employee, vendor, seller, partner, brand) | `res.partner` | `fix.party.role`, `fix.party.hierarchy` | All |
| **Product & service catalogue** | `product.template` / `product.product` | `fix.catalogue.item`, service kits, rental SKUs, refurb grades | M01, M11, M12, M13, M14, M15, M37 |
| **Location & geography** | `res.country`, `res.country.state`, `res.city` | `fix.bd.address` (8 divisions / 64 districts / upazilas), `fix.zone`, `fix.geofence` | M02, M03, M04, M12, M65 |
| **Legal entity & operating unit** | `res.company`, OCA `operating.unit` | `fix.entity`, `fix.branch`, `fix.cost.center` | All |
| **Document & attachment** | `ir.attachment`, OCA `dms` | `fix.document`, retention class, e-signature envelope | All |
| **Event** | — | `fix.domain.event` (transactional outbox) | All |

A single party may hold multiple roles simultaneously. This is essential: a marketplace seller
can also be a customer; a corporate client can also be a referral partner. Respondents must not
propose a design that models these as separate master records.

### 5.3 The Layered Delivery Model (L1–L6)

Every capability is delivered at the cheapest viable layer. **This selection hierarchy is
mandatory** and every requirement in the respondent's functional response (Appendix A) must be
mapped to a layer.

| Layer | Description | Licence | Target share of requirements |
|---|---|---|---:|
| **L1** | Odoo 19 Community Edition native | LGPL-3, $0 | ~28% |
| **L2** | OCA community modules (140+ across 18 repositories) | LGPL/AGPL-3, $0 | ~24% |
| **L3** | Free third-party Odoo modules | Various, $0 | ~4% |
| **L4** | Standalone open-source systems (24 in the reference stack) | Apache/MIT/BSD/AGPL, $0 | ~17% |
| **L5** | Custom development (~138 CD items) | Proprietary, development cost | ~25% |
| **L6** | Commercial SaaS where no viable open source exists | Subscription | ~2% |

```
For each requirement:
  1. Can Odoo 19 CE do it out of the box?            → L1
  2. Is there a production-grade OCA module?          → L2
  3. Is there a maintained free third-party module?   → L3
  4. Is there a mature standalone OSS system?         → L4
  5. Must it be built?                                → L5
  6. Only if 1–5 all fail AND the CFO approves        → L6
```

**A respondent whose functional response places materially more than 25% of requirements at L5
must justify each such classification.** Over-classification to L5 will be treated as either a
capability gap or a commercial inflation and scored accordingly.

### 5.4 The Reference Stack

#### 5.4.1 Layer 1 — Odoo 19 Community Edition

| Attribute | Specification |
|---|---|
| Version | 19.0 (released 18 September 2025), patched to current 19.x |
| Licence | LGPL v3 — $0 |
| Runtime | Python 3.12+ |
| Database | PostgreSQL 16 |
| Frontend | OWL 2 (TypeScript component framework) |
| Primary API | JSON-2 (RESTful, token-authenticated) |

Odoo modules deployed: `base`, `web`, `mail`, `contacts`, `crm`, `sale`, `sale_management`,
`product`, `stock`, `purchase`, `account`, `hr`, `hr_attendance`, `hr_holidays`, `hr_expense`,
`project`, `calendar`, `fleet`, `website`, `portal`, `maintenance`, `repair`, `sale_renting`.

#### 5.4.2 Layer 2 — OCA repositories

| Repository | Modules used | Serves | v19 migration risk |
|---|---:|---|---|
| `OCA/field-service` | 33 | M01, M02 | **Medium** — ~25 of 33 migrated |
| `OCA/helpdesk` | 28 | M01, M05, M27 | **Medium** — ~20 of 28 migrated |
| `OCA/management-system` | 33 | M23, M60 | Low |
| `OCA/operating-unit` | 15 | All | Low |
| `OCA/hr` + `OCA/payroll` | 50+ | M21, M22, M55, M56, M57 | Low |
| `OCA/account-financial-tools` | 40+ | M19, M49 | Low |
| `OCA/account-financial-reporting` | 20+ | M19, M25 | Low |
| `OCA/reporting-engine` + `OCA/mis-builder` | 20+ | M19, M25, M54 | Low |
| `OCA/stock-logistics-workflow` | 25+ | M15, M41 | Low |
| `OCA/stock-logistics-barcode` | 10 | M15, M02, M41 | Low |
| `OCA/stock-logistics-warehouse` | 20+ | M15, M41 | Low |
| `OCA/purchase-workflow` | 25+ | M16, M42 | Low |
| `OCA/partner-contact` | 30+ | M07, M33 | Low |
| `OCA/contract` | 12 | M08, M39 | Low |
| `OCA/dms` | 5 | M24 | Low |
| `OCA/server-tools` | 30+ | M29, M30 | Low |
| `OCA/web` | 40+ | UI, Keycloak auth | Low |
| `OCA/l10n-bangladesh` | 2 | M19, M51 | Low |

**Standing obligation.** Where the successful respondent migrates an OCA module to v19, the work
must be contributed back upstream. This is a contractual condition, not a preference.

#### 5.4.3 Layer 4 — Standalone open-source systems

| System | Version | Licence | Serves | Wave |
|---|---|---|---|:--:|
| Keycloak | 26.x | Apache-2.0 | M29 — identity, SSO, MFA, federation | W1 |
| Kong Gateway | 3.x | Apache-2.0 | M28 — API gateway | W1 |
| n8n | 1.x | Sustainable Use (self-hosted) | M28, M63 — workflow automation | W1 |
| Novu | 2.x | MIT | M27 — notification orchestration | W1 |
| Redis | 7.x | BSD-3 | Cache, sessions, queues, locks | W1 |
| MinIO | latest | AGPL-3 | Object storage | W1 |
| PostgreSQL | 16 | PostgreSQL Licence | Primary datastore | W1 |
| PgBouncer | latest | ISC | Connection pooling | W1 |
| Nginx | 1.27+ | BSD-2 | Reverse proxy | W1 |
| Docker / K3s | current | Apache-2.0 | Containerisation & orchestration | W1 |
| Traccar | 6.x | Apache-2.0 | M02 — GPS tracking | W2 |
| OSRM | 5.x | BSD-2 | M02, M03 — road routing | W2 |
| VROOM | 1.14+ | BSD-2 | M02, M03 — vehicle routing optimisation | W2 |
| TimescaleDB | 2.x | Apache-2.0 | M02, M05, M17, M48 — time series | W2 |
| Grafana | 11.x | AGPL-3 | M25, M28 — operational monitoring | W2 |
| OpenTelemetry + Prometheus + Loki + Tempo | latest | Apache-2.0 | Observability | W3 |
| Metabase | 0.52+ | AGPL-3 | M25 — BI and dashboards | W4 |
| Mayan EDMS | 4.10 | Apache-2.0 | M24 — document management at scale | W5 |
| MeshCentral / RustDesk | latest | Apache-2.0 / AGPL-3 | M05 — remote support sessions | W5 |
| Wazuh / osquery | latest | GPL-2 / Apache-2.0 | M05 — endpoint monitoring | W5 |
| Redpanda / Kafka | latest | BSL / Apache-2.0 | M28 — event bus at scale | W6 |
| MLflow | 2.x | Apache-2.0 | M26 — model registry and tracking | W6 |
| Ollama | 0.5+ | MIT | M26, M32 — self-hosted LLM inference | W6 |
| ClickHouse | 24.x | Apache-2.0 | M25, M62 — analytical warehouse | W8 |

**Licence compliance is a contractual obligation.** AGPL-3 components (Metabase, Grafana, MinIO,
RustDesk) are deployed unmodified; any modification must be published. LGPL-3 extensions must be
separate modules, never modifications to core. The n8n Sustainable Use Licence permits internal
business use only. A licence register is maintained in M30 and reviewed annually.

#### 5.4.4 Layer 6 — Commercial components (the only permitted licence cost)

| Component | Purpose | Module | Estimated cost | Open-source alternative assessed |
|---|---|---|---|---|
| Cloud telephony / CPaaS | Inbound IVR, routing, recording on hotline 16743 | M27 | $200–600/month | Asterisk/FreePBX viable but requires carrier interconnect and in-house telecom expertise |
| Qualified e-signature | Legally binding signatures on AMC, MSP, rental and seller agreements | M24 | $100–400/month | OSS signing works technically but lacks accredited trust-service status |
| Identity verification / KYC | Marketplace seller and high-value customer verification | M12 | $0.30–0.80 per check | Requires accredited data source; no OSS equivalent |
| Endpoint RMM agent *(conditional)* | Patch management at scale on client Windows/macOS estates | M05 | $2–5 per endpoint/month | Wazuh + osquery cover monitoring; **decision deferred to Wave 5 after pilot** |

**Total L6 exposure: $0–36K over three years.** Any additional L6 component proposed by a
respondent requires CFO approval and a written open-source alternative assessment, and must be
priced separately in the commercial response.

### 5.5 Non-Negotiable Architecture Standards

Every standard below is verifiable in continuous integration or at architecture review. They form
part of the definition of done and will be contractually binding.

| # | Standard | How it is verified |
|---|---|---|
| AS-01 | No module accesses another module's tables directly | Static analysis in CI; architecture review |
| AS-02 | All custom models inherit `mail.thread` + `mail.activity.mixin` | Model registry check in CI |
| AS-03 | All custom models carry `operating_unit_id` and `company_id` | Model registry check in CI |
| AS-04 | All custom tables prefixed `fix_`; models prefixed `fix.` | Linter rule |
| AS-05 | OCA modules extended via `_inherit`, never forked without architecture-board approval | Repository review |
| AS-06 | Every state machine is explicit, with allowed transitions declared in one place | Code review checklist |
| AS-07 | Every API is versioned (`/v1/`) and documented in OpenAPI 3.1 | CI validation against the specification |
| AS-08 | Every write path emits a domain event via the transactional outbox | Event coverage test |
| AS-09 | No business logic in views, controllers or portal code | Code review checklist; portal contract test |
| AS-10 | All money uses `Monetary` with explicit currency; no floats | Linter rule; financial test suite |
| AS-11 | All timestamps stored UTC, presented in Asia/Dhaka | Schema check |
| AS-12 | All user-facing strings translatable; Bengali translation is a definition-of-done item | Translation coverage report at 100% |
| AS-13 | Offline-capable apps use an append-only local journal with server-authoritative conflict resolution | Offline test suite |
| AS-14 | Personally identifiable and recovered customer data encrypted at field level | Security test suite |
| AS-15 | Every module ships with unit tests ≥ 80% and its KPI instrumentation | Definition-of-done gate |

### 5.6 Build-versus-Buy Decisions Already Taken

These decisions are settled. Respondents may challenge them in their Exceptions schedule
(§18.4), but must price the reference position as their primary bid.

| # | Capability | Decision | Rationale |
|---|---|---|---|
| 1 | ERP core | **Build on Odoo 19 CE** | $0 licence; full extensibility; local talent availability |
| 2 | Field service management | **OCA + custom** | OCA `field-service` covers the majority; Odoo Enterprise FSM would cost $45–90K over 3 years for less flexibility |
| 3 | Technician mobile app | **Build (Flutter)** | 24-hour offline, Bengali-first, deep ERP integration — no commercial product meets all three |
| 4 | Dispatch optimisation | **Build on VROOM/OSRM** | Commercial routing APIs cost $200–400/month and cannot embed skill, certification and van-stock constraints |
| 5 | Marketplace platform | **Build** | Commission and settlement must live in the ledger; SaaS marketplaces cannot be the system of record |
| 6 | Managed services PSA | **Build on Odoo + OSS monitoring** | Commercial PSA licensing scales badly at 400 technicians and still needs ERP integration |
| 7 | RMM agent | **Conditional buy (L6)** | OSS covers monitoring; patch orchestration at scale piloted in Wave 5 |
| 8 | Contact centre | **Build the console, buy the telephony** | Agent experience must be inside the ERP; carrier interconnect must be licensed |
| 9 | Business intelligence | **Metabase (OSS)** | Mature, free, self-hosted, embeds cleanly |
| 10 | Data warehouse | **ClickHouse (OSS)** | Handles analytical volume at a fraction of managed-warehouse cost |
| 11 | Identity provider | **Keycloak (OSS)** | Standards-compliant; supports federation with corporate clients |
| 12 | API gateway | **Kong (OSS)** | Proven at scale; free tier sufficient |
| 13 | Document management | **OCA `dms` → Mayan EDMS** | OCA sufficient through Wave 4; Mayan for volume, OCR and retention from Wave 5 |
| 14 | E-signature | **Buy (L6) for binding contracts; build for operational signatures** | Operational signatures need no accreditation; contracts do |
| 15 | Conversational AI | **Build on self-hosted LLM** | Customer data must not leave the Company; Bengali capability available in open-weight models; no per-query cost |
| 16 | ML platform | **Build on MLflow (OSS)** | Managed ML platforms add cost and data-egress exposure |
| 17 | Payment processing | **Integrate, never build** | Regulated; bKash, Nagad, SSLCOMMERZ |
| 18 | Accounting engine | **Odoo `account` + custom Bangladesh compliance** | Double-entry is solved; Bangladesh compliance is not |
| 19 | Payroll engine | **OCA base + custom Bangladesh rules** | Tax slabs, PF, gratuity and BEFTN are Bangladesh-specific |
| 20 | E-commerce storefront | **Build in Next.js** | Must share identity, catalogue, stock and settlement with the ERP |

### 5.7 Alternative-Architecture Proposals

Respondents may submit **one** alternative-architecture proposal alongside the primary
(reference-architecture) response. An alternative proposal is admissible only if it:

| # | Condition |
|---|---|
| ALT-01 | Is submitted **in addition to**, not instead of, a compliant primary response |
| ALT-02 | Addresses the same 2,930 requirements, mapped requirement by requirement |
| ALT-03 | Meets every non-functional requirement in §9 and every compliance obligation in §10 without exception |
| ALT-04 | Honours constraint CON-03 — the Next.js 15 + Payload CMS portal platform cannot be replaced |
| ALT-05 | States full 5-year TCO including licences, and demonstrates it does not exceed the reference architecture's 5-year TCO |
| ALT-06 | States the exit position: data export format, escrow, and what the Company owns at termination |
| ALT-07 | Identifies the Bangladesh-resident data store satisfying NFR-086 |
| ALT-08 | Declares any per-user, per-technician or per-transaction licence metric and models it at 5× current volume |

Alternative proposals are scored under the same matrix (§17) with a mandatory adjustment for
lock-in risk and licence-scaling exposure.

### 5.8 Runtime Topology & Environments

```
┌─── PRODUCTION — split residency: regional primary + Bangladesh-resident sensitive store ───┐
│  EDGE — CDN · WAF · DDoS · bot management                                                  │
│  INGRESS — Kong API Gateway + Nginx · TLS 1.3 · OAuth2 introspection · rate limits          │
│  ┌───────────────┬──────────────────┬─────────────────┬────────────────┐                   │
│  │ ODOO 19 CE    │ NEXT.JS PLATFORM │ DOMAIN SERVICES │ SUPPORTING     │                   │
│  │ 4× app nodes  │ P01,P04,P07,P08, │ Dispatch AI ·   │ Keycloak · n8n │                   │
│  │ 12 workers ea │ P10,P12          │ Pricing engine ·│ Novu · Traccar │                   │
│  │ 2× cron nodes │ React 19         │ ML inference ·  │ Mayan · MinIO  │                   │
│  │ 2× longpoll   │ Payload CMS 3    │ Route (VROOM/   │ Metabase ·     │                   │
│  │ 67 modules ·  │                  │ OSRM) ·         │ Grafana        │                   │
│  │ ~138 CD items │                  │ Settlement ·    │                │                   │
│  │ 140+ OCA      │                  │ RMM · OCR/STT   │                │                   │
│  └───────────────┴──────────────────┴─────────────────┴────────────────┘                   │
│  MESSAGING — Redis Streams (intra) · Redpanda/Kafka (inter-system, W6+)                     │
│              transactional outbox → event bus → idempotent consumers                        │
│  DATA — PostgreSQL 16 primary + 2 read replicas + PgBouncer · TimescaleDB · ClickHouse ·    │
│         Redis 7 · object storage · Bangladesh-resident sensitive-data store (NFR-086)       │
│  OBSERVABILITY — OpenTelemetry → Prometheus + Loki + Tempo → Grafana                        │
│  BACKUP — hourly WAL · daily full (30 d) · weekly (1 y) · monthly (7 y), AES-256            │
│  DR — warm standby · RPO ≤ 15 min · RTO ≤ 2 h                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Environment ladder** (all six must be delivered and maintained by the respondent):

| Environment | Purpose | Data | Refresh |
|---|---|---|---|
| `local` | Developer workstation, Docker Compose | Synthetic fixtures | On demand |
| `dev` | Continuous integration target | Synthetic + anonymised sample | Every merge to `develop` |
| `staging` | UAT, performance and security testing | Production clone, PII-masked | Weekly |
| `training` | Super-user and end-user training | Curated scenario data | Per training cycle |
| `prod` | Live | Live | — |
| `dr` | Warm standby | Streaming replica | Continuous |

### 5.9 Production Sizing (Steady State, Wave 8)

| Component | Specification |
|---|---|
| Odoo application nodes | 4 × 8 vCPU / 32 GB, 12 workers each |
| Odoo cron nodes | 2 × 4 vCPU / 16 GB |
| Next.js portal nodes | 3 × 4 vCPU / 8 GB (or serverless equivalent) |
| Domain services | 4 × 4 vCPU / 16 GB |
| PostgreSQL primary | 16 vCPU / 64 GB / 2 TB NVMe, partitioned and tuned |
| PostgreSQL replicas | 2 × 8 vCPU / 32 GB / 2 TB |
| TimescaleDB | 8 vCPU / 32 GB / 4 TB with compression |
| ClickHouse | 8 vCPU / 32 GB / 4 TB |
| Redis | 4 vCPU / 16 GB |
| Event bus | 3 × 4 vCPU / 16 GB |
| Supporting services | 3 × 8 vCPU / 32 GB |
| ML inference | 1 × 8 vCPU / 32 GB, GPU optional |
| Object storage | 20 TB growing |

Indicative monthly infrastructure cost progresses from **$450–700 (W1)** to **$4,000–5,800 (W9)**.
Third-party API costs at scale are estimated at **$1,890–5,230/month**. Respondents must validate
and re-cost these in their commercial response.

### 5.10 Engineering Practice Required

| Aspect | Standard |
|---|---|
| Repository | Monorepo with Odoo as a pinned submodule, OCA as subtrees, custom modules and services as first-class directories |
| Branching | `main` (production) ← `release/*` ← `develop` ← `feature/*`, `fix/*`; `hotfix/*` from `main` |
| Commit convention | `<type>(<scope>): <subject>` — feat, fix, docs, style, refactor, test, chore, perf |
| Code review | Every change reviewed by a second engineer; architecture changes reviewed by the solution architect |
| Pre-commit | Formatting, linting, Odoo-specific checks, secret scanning |
| CI | Lint, type check, unit tests, integration tests, OpenAPI validation, SAST, dependency scan, build verification on every pull request |
| CD | Automatic to `dev` on merge to `develop`; manual gate to staging and production |
| Documentation | Every module ships with a README, an operational runbook and its OpenAPI specification — a definition-of-done item |
| Secrets | Vault-managed; never in the repository; rotation scheduled |
| Dependencies | Pinned versions; automated vulnerability alerts; monthly update cycle |
| Ownership | All source code, configuration, migrations, test suites and documentation are the property of 1000FiX and are delivered to a Company-controlled repository continuously, not at milestones |

---

## 6. FUNCTIONAL REQUIREMENTS — 67 MODULES IN 11 CATEGORIES

### 6.1 How to Respond to This Section

The full requirement set — **2,930 individually numbered, individually acceptance-criteria'd
functional requirements** — is held in the module specification files released as **Annex 1**
under NDA. This section states the module scope, priority, wave, requirement volume and effort
so that respondents can size and sequence the work.

**Respondents must complete Appendix A (Requirement Response Matrix) at the individual
requirement level** for every requirement in Annex 1. Module-level responses are not acceptable
and will render a submission non-compliant.

**Response codes** — for each requirement, state one:

| Code | Meaning |
|---|---|
| **N** | Delivered by **native** Odoo 19 CE capability (L1) with no code change |
| **O** | Delivered by an **OCA** module (L2) — state the repository and module name |
| **T** | Delivered by a free **third-party** Odoo module (L3) — state the module and its maintenance status |
| **S** | Delivered by a standalone open-**source** system (L4) — state the system |
| **C** | Requires **custom** development (L5) — state the CD deliverable and effort in person-days |
| **X** | Requires a commercial component (L6) — state the product, licence metric and annual cost |
| **G** | **Gap** — cannot be delivered as specified. State the nearest achievable alternative |

Each response must additionally carry: **effort (person-days)**, **wave**, **dependencies**, and
**risk flag (H/M/L)**. Requirements answered **G** must be summarised in the Exceptions schedule.

> ### Reconciliation notice — read before using the per-module figures
>
> **The category totals below are measured; several of the per-module figures are not.**
>
> Requirement and effort figures were originally *estimated* per module, then the specification
> files were written, and in August 2026 every category was **recounted by direct enumeration of
> the files**. The recount produced the category totals used throughout this RFP —
> **2,930 requirements and 1,513 person-weeks**. Those totals are authoritative.
>
> The per-module figures in the tables that follow are, for **Categories A, C, E, F, G, I, J and
> K**, the *original estimates*. They have not yet been redistributed to match the measured
> category totals, because the redistribution requires a per-module recount that is still in
> progress. The gap is material and is disclosed here rather than smoothed over:
>
> | Category | Sum of per-module figures | **Measured category total** | Variance |
> |---|---:|---:|---:|
> | A — Service Delivery & Operations | 389 *(allocated IDs)* | **362** | −27 *(28 allocated-but-unused IDs; see §20.1.2)* |
> | B — Customer Engagement | 320 | **320** | ✓ reconciled |
> | C — Commercial, Pricing & Revenue | 356 | **494** | **+138** |
> | D — Circular & Asset-Based | 109 | **109** | ✓ reconciled |
> | E — Supply Chain & Inventory | 192 | **235** | +43 |
> | F — Asset, Equipment & Facilities | 134 | **232** | **+98** |
> | G — Finance & Treasury | 258 | **333** | +75 |
> | H — People & Workforce | 310 | **310** | ✓ reconciled |
> | I — Governance, Risk, Quality | 118 | **170** | +52 |
> | J — Data, Analytics & Intelligence | 130 | **146** | +16 |
> | K — Platform & Technology | 220 *(incl. unwritten M66, M67)* | **219** *(5 written specs)* + 48 est. | — |
>
> **What this means for respondents.** Use the per-module figures for **relative sizing between
> modules within a category**. Use the **measured category total** for absolute sizing, effort
> estimation and pricing. Where a category's measured total exceeds the sum of its parts, the
> additional requirements are real and are present in the Annex 1 specification files — **price
> against Annex 1, not against the summary tables in this section.**
>
> The pattern is explicable: requirement counts were under-estimated wherever a category carries
> statutory, contractual or master-data obligations (F +73%, H +52%, I +44%, C +39%, G +29%) and
> were accurate where the category is purely operational (D 0%, J +12%). Effort tracked far
> closer than count — **+15% against +21%** — because statutory requirements are numerous but
> individually small, most resolving to configuration in a versioned rule pack rather than new
> code. Respondents should reflect that asymmetry in their effort model. See §20.3.2.

### 6.1a Reconciliation Note — Measured vs Estimated Figures

**Read this before adding the columns in §6.3–§6.13. Two different measurements appear and they do
not sum to each other.** This is inherited from the Company's source register and is disclosed
rather than smoothed over.

| Figure | Basis |
|---|---|
| **Category totals** (in each category heading and in §3.2) | **Measured** by direct enumeration of the module specification files on 13 August 2026 |
| **Per-module requirement and effort figures** (in each table row) | **Measured** for Categories A, B and H; **estimated** for C, D, E, F, G, I, J, K |

| Category | Per-module rows sum to | Measured total | Variance |
|---|---:|---:|---:|
| A — Service Delivery | 389 *(includes 28 allocated-but-unused IDs — §20.1.2)* | **362** | −7% |
| B — Customer Engagement | 320 | **320** | 0% |
| C — Commercial | 356 *(est.)* | **494** | **+39%** |
| D — Circular | 109 *(est.)* | **109** | 0% |
| E — Supply Chain | 192 *(est.)* | **235** | **+22%** |
| F — Asset & Facilities | 134 *(est.)* | **232** | **+73%** |
| G — Finance & Treasury | 258 *(est.)* | **333** | **+29%** |
| H — People & Workforce | 310 | **310** | 0% |
| I — Governance & Quality | 118 *(est.)* | **170** | **+44%** |
| J — Data & Analytics | 130 *(est.)* | **146** | **+12%** |
| K — Platform (5 of 7 written) | 220 *(est., 7 modules)* | **219** *(5 modules)* | — |

**Respondents must price against the measured category totals and against Annex 1 at requirement
level.** Per-module rows in the eight estimated categories indicate relative size only and **must
not be treated as a contractual scope statement** (register rule RG-05). A respondent who prices
only the per-module rows will under-quote Categories C, F, G and I materially.

### 6.2 Requirement Identifier Convention

```
FR-<CODE>-nnn        Functional requirement       e.g. FR-SRM-014
FN-<CODE>-nnn.m      Function within a feature    e.g. FN-RNT-007.2
E-<CODE>-nn          Data entity                  e.g. E-CTR-03
INT-nnn              Integration                  e.g. INT-042
EVT-<domain>.<verb>  Domain event                 e.g. EVT-service_order.completed
R01–R38              User role                    e.g. R14 Logistics Coordinator
BRU-<CODE>-nn        Business rule                e.g. BRU-SRM-09
AUT-<CODE>-nn        Automation / workflow
NFR-nnn              Non-functional requirement
KPI-nnn              Key performance indicator
CD-nnn               Custom development deliverable
W1–W9                Delivery wave
```

Identifiers are **permanent**. A withdrawn requirement's ID is retired, never reused. The
successful respondent must quote these identifiers in every sprint ticket, test case, commit
message and deliverable.

---

### 6.3 Category A — Service Delivery & Operations

**7 modules · 362 requirements · 206 PW · Owner: Service Operations Director**
*Per-module requirement figures below are allocated ID ranges, not counts — 28 IDs are allocated
but unused. See the reconciliation notice in §6.1 and the disclosure in §20.1.2.*

Everything that happens to a customer's device or IT estate — from intake through diagnosis,
repair, quality control and handover, across all five delivery modes.

| ID | Module | Code | Pri | Wave | Reqs | PW | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M01** | Service Request & Order Management | `SRM` | **P0** | W1–W2 | 88 | 46 | Multi-channel intake; service order and work order lifecycle; classification by 14 business lines; diagnosis; estimate and approval loop; SLA definition, clocks, holds and escalation; quality control; rework detection; job cost roll-up; templates; bulk operations; legacy order lookup | |
| **M31** | Workshop & Depot Repair Management ★ | `WSR` | P1 | W2 | 58 | 30 | Bench assignment and WIP board; Level 1/2/3 board-level repair routing; parts-hold management; multi-job handling; depot receipt and dispatch; workshop capacity and utilisation | |
| **M02** | Field Service & Dispatch Management | `FSM` | **P0** | W2 | 74 | 40 | Dispatch engine and board; skill, certification, location, workload and van-stock scoring; route optimisation and re-optimisation; GPS tracking; geofencing; zones and territories; capacity and slot management; standby rota; offline mobile execution; assignment explanation and override logging; dispatch analytics and API | |
| **M03** | Service Logistics & Reverse Logistics | `LOG` | P1 | W3 | 42 | 22 | Consignments and legs; chain of custody with GPS, timestamp and dual identity; pick & drop; courier partner integration; rider manifests and load planning; cash on delivery; loss and damage claims; restricted-item control; logistics cost allocation; carrier performance | |
| **M04** | Branch & Front-Desk Operations | `FRD` | P1 | W1 | 32 | 13 | Token queue and wait-time estimation; walk-in intake in under 3 minutes; handover; counter cash drawer and shift control; multi-counter configuration; receipt, job-sheet, label and gate-pass printing; self-service kiosk; counter analytics | |
| **M05** | Remote Support & Managed Services | `RMS` | P1 | W5 | 61 | 37 | MSP contracts and estates; agent and agentless monitoring; alerting and noise reduction; MSP ticketing and SLA; patch management; remote sessions; runbooks and automation library; client onboarding and offboarding; DR/BC plan register; licence and warranty tracking across client estates; per-client profitability | |
| **M06** | Data Services & Secure Data Handling | `DTS` | P2 | W6 | 34 | 18 | Data recovery cases; media chain of custody with dual control; cleanroom scheduling; partner lab referral; backup plans and restore testing; certified destruction with IEEE 2883 technique standard; access restriction and compliance reporting | |

**Category A critical controls the solution must enforce:**

- A service order cannot be created without an identified device (BRU-SRM-01)
- A warranty-type order requires an active warranty at the request date (BRU-SRM-02)
- A service order cannot reach Completed without a passed quality checklist (BRU-SRM-04)
- Estimates above BDT 5,000 require documented customer approval before work begins (BRU-SRM-07)
- **A service order cannot be assigned to a technician lacking current certification for that brand's warranty work** (BRU-SRM-09) — this is a hard block, enforced at the model layer
- Before/after photographs are mandatory on every warranty job (BRU-SRM-17)
- Independent second-person QC is mandatory above BDT 25,000 (BRU-SRM-18)
- A device uncollected 30 days after Ready enters the abandonment process with statutory notice (BRU-SRM-16)

---

### 6.4 Category B — Customer Engagement & Experience

**7 modules · 320 requirements · 148 PW · Owner: Chief Commercial Officer**

| ID | Module | Code | Pri | Wave | Reqs | PW | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M33** | Customer & Party Master Management ★ | `CPM` | **P0** | W1 | 52 | 24 | The single party master: individual, corporate, dealer, government, employee, vendor, seller, brand, partner — with multi-role capability; Bangladesh address hierarchy; identity documents with residency classification; **PDPA 2026 consent, transparency notice and data-subject rights**; duplicate detection and merge with reversal; data quality management | |
| **M07** | CRM, Sales Pipeline & Account Management | `CRM` | P1 | W1 / W4 | 46 | 22 | Customer 360; segmentation; corporate hierarchy and contact roles; approval chain configuration; lead and opportunity pipeline; account team assignment; blacklist and fraud flags; win-back segmentation; referral attribution; CRM analytics | |
| **M10** | Loyalty, Membership & Rewards | `LOY` | P1 | W2 | 44 | 18 | Privilege Program (Silver/Gold/Diamond) enrolment, renewal, upgrade; points earning and redemption; vouchers and coupon codes; referral programme; tier-based automatic entitlements; loyalty cost accounting | |
| **M34** | Customer Experience, Feedback & Complaints ★ | `CXM` | P1 | W4 | 42 | 17 | CSAT/NPS instrumentation across every touchpoint; multi-parameter service and technician rating; review capture and publication; complaint intake, taxonomy, escalation and closure; voice-of-customer analytics | |
| **M27** | Omnichannel Contact Centre & Communications | `CCE` | P1 | W4 *(see note)* | 58 | 32 | Unified queue across voice, chat, WhatsApp, email, SMS and social; hotline 16743 telephony integration; screen-pop on identification; notification orchestration and templating across all channels; conversation history; disposition coding; recording, quality scoring and coaching; supervision | |
| **M32** | Conversational AI & Virtual Assistant ★ | `CAI` | P1 | W4 | 38 | 18 | Bengali and English assistant on self-hosted LLM; intent handling over live ERP data; knowledge-grounded answers; agent handoff with context; suggested responses and next-best-action; guard rails and fallback to rules | |
| **M35** | Marketing, Campaigns & Demand Generation ★ | `MKT` | P2 | W5 | 40 | 17 | Campaign definition, segmentation and execution; multi-channel journeys; promotional offers; lead capture and attribution; advertising and boost placement; campaign performance and cost attribution | |

> **Sequencing decision required (Q-05).** M27's **notification service** should move from Wave 4
> to Wave 1 or Wave 2. Every module from Wave 1 onward needs to notify customers; if M27 arrives
> at W4, each earlier module builds its own send path — recreating the fragmentation the
> programme exists to remove. **Respondents must state their recommended position and price it.**

> **Dependency decision required (Q-01).** M32 depends on M61 Knowledge Management, currently
> scheduled two waves later (W6). Either M61 core content moves to W4, or M32 launches with a
> reduced intent scope. **Respondents must state their recommendation.**

---

### 6.5 Category C — Commercial, Pricing & Revenue

**9 modules · 494 requirements · 262 PW · Owner: Chief Commercial Officer**

What the Company sells, what it charges, what it agrees to, and every route to market. This is
the largest category by both requirement count and effort.

```
   M37 CATALOGUE ──► M11 PRICING ──► M36 QUOTATION ──┬──► M08 CONTRACT
   "What can we      "What does it    "What did we    ├──► M09 WARRANTY
    sell?"            cost?"           offer?"        ├──► M39 SUBSCRIPTION
                                                      ├──► M38 E-COMMERCE
                                                      └──► M12 MARKETPLACE
                                                              │
                                                              ▼
                                          M53 REVENUE & SETTLEMENT · M20 RECEIVABLES
```

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M37** | Product & Service Catalogue Management ★ | `CAT` | **P0** | W1 | 34 | 18 | The definition of everything sellable: services, service kits, parts, protection plans, rental SKUs, refurbished grades, subscription plans — with repair bills of material and standard times. **A price never lives on a catalogue item** | |
| **M11** | Pricing, Rate Cards & Dynamic Pricing | `PRC` | P1 | W3 / W7 | 36 | 20 | Every price in the business: rate cards by device category, brand, model and repair type; warranty vs out-of-warranty pricing; price books; customer-specific and segment pricing; discount governance and approval thresholds; NTE limits; dynamic pricing with guard rails and full decision audit; price revision history | |
| **M36** | Quotation, Estimation & Tender Management ★ | `QTE` | P1 | W3 | 32 | 17 | Estimate build-up (labour + parts + transport + tax); versioning; customer approval loop with part-approval and decline; validity and expiry; competitive bidding; corporate tenders and RFP response; quotation-to-invoice integrity | |
| **M08** | Contract Lifecycle Management | `CTR` | P1 | W4 | 44 | 24 | A contract **engine**, not an AMC table — must model **14 contract product families** without code change: RAMC (6 packages), Commercial AMC, IT Infrastructure AMC, Healthcare Equipment AMC with mandatory calibration, Specialty Equipment AMC, Managed Services (6 types), Mobile & Appliance Service (5 types), rental master agreements, marketplace seller agreements, brand partner agreements. Entitlement definition and consumption; SLA terms; preventive schedule generation; amendment; renewal; contract profitability | |
| **M09** | Warranty, Protection Plans & Claims | `WTY` | **P0** | W4 | 48 | 28 | Warranty registration and automated entitlement verification by serial and purchase date; **7 protection product families** (Standard Extension, Accidental Damage, Extended Repair, Mobile Device, Home Appliance, Computer & Laptop Care, Customised); brand claim automation for 17+ partners with per-brand rule engines and evidence packs; claim lifecycle to reimbursement; reconciliation with brand remittances; recall campaign handling | |
| **M39** | Subscription & Recurring Revenue ★ | `SUB` | P1 | W4 | 30 | 17 | Recurring and usage-based billing mechanics; billing cycles and proration; plan change; MRR/ARR; dunning triggers; churn measurement | |
| **M38** | E-Commerce & Digital Storefront ★ | `ECM` | P1 | W7 | 40 | 24 | Selling 1000FiX's own products and services online: catalogue browse, cart, checkout, fulfilment, returns — sharing identity, catalogue, stock and settlement with the ERP | |
| **M12** | Marketplace & Seller Ecosystem | `MKP` | P1 | W7 | 62 | 40 | The aggregator: seller registration and KYC; listings; job broadcast; competitive bidding and counter-bidding; ratings and reviews; disputes; seller wallets, commission and payouts; escrow; paid boost and advertising; performance scoring with automatic visibility reduction and suspension | |
| **M40** | Partner, Channel, Alliance & Franchise ★ | `PCM` | P2 | W7 | 30 | 16 | Relationship management for brand partners, alliance partners, referral partners, resellers and franchise branches; partner agreements; commission schemes; co-marketing; partner performance | |

**Boundaries that must not blur:**

| Boundary | Rule |
|---|---|
| M37 Catalogue vs M11 Pricing | A price never lives on a catalogue item. A catalogue item never carries a discount. |
| M08 Contract vs M39 Subscription | M08 defines entitlement ("what did we promise?"); M39 turns it into money owed ("what do we bill, when, how much?"). A subscription always has an M08 contract behind it. |
| M38 E-Commerce vs M12 Marketplace | One storefront, two supply models. 1000FiX as principal vs third-party seller. The customer sees one experience; the ledger sees two revenue treatments. |

> **Critical open decision (D-03, RSK-022).** The marketplace **principal-versus-agent VAT and
> liability model** is not yet settled. External tax and legal opinion is required three months
> before Wave 7 build. Respondents must design M12 and M53 so that the revenue treatment is
> **configurable**, not hard-coded, and must price both treatments.

---

### 6.6 Category D — Circular & Asset-Based Business

**3 modules · 109 requirements · 60 PW · Owner: Corporate Services Head / Retail Operations Head**

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M13** | Rental & Equipment-as-a-Service | `RNT` | P2 | W6 | 44 | 25 | Rental asset pool across eight asset categories (laptop, camera, projector, tablet, AV, server, networking, electronic test equipment); reservations and availability; rental agreements and master framework agreements with call-off; tariffs (period + usage); deposits; condition reports at dispatch and return; damage assessment and recovery; utilisation and depreciation discipline; rental billing; subscription rental | |
| **M14** | Trade-In, Refurbishment & Resale | `TRF` | P2 | W6 | 39 | 22 | Trade-in request with photos and condition declaration; indicative and firm valuation; IMEI/stolen-device screening; intake; **certified data wipe before any refurbishment**; refurbishment work orders; grading against published criteria; provenance record; resale lots and channel allocation; refurbished warranty terms and reserve; market price feeds | |
| **M18** | E-Waste, Recycling & Circular Economy | `ESG` | P3 | W8 | 26 | 13 | Collection events and drop-off points; triage and disposition; certified destruction; recycling batches to certified partners; material recovery credit; disposal certificates; statutory e-waste reporting; ESG reporting; refrigerant recovery logs; donation programme | |

**Non-negotiable control:** zero refurbished units may be released without a **data destruction
certificate** (Gate 6 criterion G6-02). The wipe certificate, the grading report and the
provenance record are inseparable from the resale record.

---

### 6.7 Category E — Supply Chain & Inventory

**6 modules · 235 requirements · 119 PW · Owner: Supply Chain Director**
*Per-module figures are the original estimates; the category total is measured. See §6.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M15** | Spare Parts & Inventory Management | `INV` | **P0** | W2 | 48 | 24 | Multi-warehouse inventory across 51+ locations plus central and regional hubs; **technician van stock**; real-time network stock visibility; barcode and QR; serial and batch tracking; parts catalogue with brand/model cross-reference; genuine vs compatible classification; substitution mapping; warranty-parts segregation; **consignment stock owned by brand partners**; three-tier parts pricing; goods receipt with inspection; inter-branch transfer with approval; requisition and reservation from service orders; automatic replenishment; cycle counting; dead stock; RTV; FIFO and weighted-average valuation | |
| **M41** | Warehouse Management ★ | `WMS` | P1 | W3 | 34 | 20 | Bin and location management; put-away strategy; picking waves; packing; hazardous-material handling; warehouse mobile operations; bin optimisation | |
| **M16** | Procurement & Strategic Sourcing | `PRO` | P1 | W3 | 32 | 16 | Purchase requisition with branch and central approval; RFQ and quotation comparison; purchase orders; blanket orders; goods receipt and inspection; **three-way matching that blocks unmatched invoices**; budget control; catalogue punch-out; import order and LC tracking | |
| **M42** | Supplier Relationship & Performance ★ | `SRM2` | P1 | W4 | 26 | 13 | Vendor master with classification (OEM, authorised distributor, local supplier); qualification and onboarding; document management with expiry (trade licence, TIN, VAT registration, insurance); performance scorecards on delivery, quality, pricing and responsiveness; supplier contracts and pricing agreements; **flow-down of PDPA processor obligations by contract** | |
| **M43** | Demand Planning & Replenishment ★ | `DPL` | P2 | W6 | 24 | 14 | Demand forecasting by part, location and season; replenishment planning; safety stock optimisation; supplier lead-time modelling; forecast accuracy measurement | |
| **M44** | Import, Trade Compliance & Landed Cost ★ | `ITC` | P2 | W6 | 28 | 15 | Import orders; letters of credit; customs documentation; duty and tariff calculation; **landed cost allocation to inventory valuation**; trade compliance screening; freight forwarder integration | |

*Code note: M42 carries `SRM2` because `SRM` is permanently allocated to M01 under register rule
RG-02. Respondents must use the codes exactly as allocated.*

---

### 6.8 Category F — Asset, Equipment & Facilities

**5 modules · 232 requirements · 114 PW · Owner: Service Operations Director / CTO**
*Per-module figures are the original estimates and understate this category by the widest margin
in the programme (+73% on recount). The category total is measured. See §6.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M17** | Device & Customer Asset Registry | `AST` | P1 | W2 / W8 | 34 | 18 | The registry of every device the Company touches: brand, model, serial, IMEI, purchase date, warranty status, ownership and transfer; customer asset estates for corporate clients (bulk upload, site/department/user assignment, retirement); full service history per device; device photo library; asset health index; asset APIs for portals | |
| **M45** | Enterprise Asset & Test Equipment ★ | `EAM` | P2 | W5 | 26 | 14 | The Company's own equipment: test instruments, workshop equipment, tools; **calibration schedules and certificates** (required by Healthcare Equipment AMC); maintenance plans; equipment assignment and custody | |
| **M46** | Fleet & Vehicle Management ★ | `FLT` | P2 | W5 | 24 | 12 | Vehicle master; assignment to technicians and riders; fuel, servicing and repair; licence, insurance and fitness expiry; utilisation and cost per kilometre; incident recording | |
| **M47** | Facility, Branch Infrastructure & Workplace ★ | `FAC` | P3 | W7 | 22 | 11 | Branch premises register; leases and renewals; utilities; facility maintenance; workplace equipment; branch readiness assessment | |
| **M48** | IoT Telemetry & Predictive Maintenance ★ | `IOT` | P2 | W8 | 28 | 18 | Telemetry ingestion at 50,000 points/minute; device and estate health scoring; alert rules; **predictive maintenance with ≥ 70% precision on the pilot estate**; model cards and drift monitoring | |

---

### 6.9 Category G — Finance & Treasury

**8 modules · 333 requirements · 185 PW · Owner: Chief Financial Officer**

This category carries the heaviest statutory density in the programme. Requirement counts here
ran **+29% above estimate** for exactly that reason. *Per-module figures below are the original
estimates; the category total is measured. See §6.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M19** | Financial Accounting & General Ledger | `FIN` | **P0** | W3 | 40 | 24 | Multi-entity, multi-branch chart of accounts with the full dimensional model (entity, branch, cost centre, business line, zone); general ledger with drill-down to transaction; manual and automated journals; **Bangladesh fiscal year July–June**; period-end close with automated checks; inter-company reconciliation and consolidation; audit support; financial controls testing | |
| **M20** | Accounts Receivable, Invoicing & Collections | `ARB` | **P0** | W3 | 36 | 20 | Automatic invoice generation from closed jobs (**≤ 5 s, 100% of jobs**); warranty claim invoicing to brand partners; corporate consolidated invoicing on configurable cycles; multi-method payment recording (cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer); advance and deposit management; credit notes and refunds; ageing; automated dunning; collections workflow; revenue assurance controls | |
| **M52** | Accounts Payable & Employee Expense ★ | `APE` | P1 | W3 | 28 | 14 | Vendor invoice processing with three-way matching; payment scheduling and batch processing; approval workflows by threshold; technician and employee expense capture, approval and reimbursement; vendor ageing | |
| **M50** | Treasury, Cash & Banking ★ | `TRE` | P1 | W3 | 30 | 16 | Branch cash drawers and daily reconciliation across 51+ counters; bank accounts and statement import; **automated reconciliation ≥ 90% auto-match**; cash position and forecasting; BEFTN disbursement files; payment gateway settlement reconciliation | |
| **M51** | Tax & Regulatory Compliance (Bangladesh) ★ | `TAX` | **P0** | W4 | 34 | 20 | **Mushak 6.3 tax invoice** per the VAT and Supplementary Duty Act 2012; VAT sub-ledgers; **Mushak 9.1 monthly return filed by the 15th via vat.gov.bd**; input VAT credit blocked without a valid Mushak 6.3 invoice; TDS/withholding at source with quarterly returns (25 Oct / 25 Jan / 25 Apr / 25 Jul); BIN/TIN validation; NBR e-VAT submission; statutory tax reporting and audit trail | |
| **M53** | Revenue Recognition, Commission & Settlement ★ | `REV` | P1 | W4 / W7 | 38 | 24 | Revenue recognition schedules across all 14 revenue streams; **marketplace commission calculation and seller settlement**; partner and referral commission; escrow; payout runs with 100% accuracy and zero unexplained variance; advertising billing; deposit accounting | |
| **M49** | Fixed Assets & Capital Investment ★ | `FXA` | P2 | W5 | 22 | 11 | Fixed asset register; depreciation; capital investment approval; asset disposal; rental fleet capitalisation and depreciation discipline | |
| **M54** | Cost Accounting, Budgeting & FP&A ★ | `FPA` | P2 | W6 | 30 | 17 | Cost per service order (labour + parts + logistics + sub-contract + overhead); branch, business-line and contract profitability; budgets and variance analysis; forecasting; management reporting packs | |

**Financial integrity requirements are absolute:** decimal arithmetic in all money paths (no
floating point); every posting reconcilable to its source; **100% unit test coverage on financial
and tax calculations** (DoD-03); soft deletion only.

---

### 6.10 Category H — People & Workforce

**7 modules · 310 requirements · 124 PW · Owner: HR Director**

| ID | Module | Code | Pri | Wave | Reqs | PW | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M21** | Core HR & Employee Lifecycle | `HCM` | P1 | W5 | 46 | 18 | Employee master; **Bangladesh Labour Act 2006 employment artefacts** — appointment letter, identity card, service book, probation limits; organisation hierarchy; employee documents; transfers and promotions; disciplinary records; employee self-service; leaver processing feeding access deprovisioning | |
| **M55** | Time, Attendance & Workforce Scheduling ★ | `WFM` | P1 | W5 | 52 | 22 | Biometric and mobile clock-in; **GPS-based attendance for field technicians**; shift patterns and roster planning across 51+ branches; leave types, accruals and balances; Bangladesh public holiday calendar including moon-dependent dates; overtime capture and approval; working-time rule enforcement | |
| **M56** | Payroll, Benefits & Statutory Compliance ★ | `PAY` | **P0** | W5 | 54 | 26 | Monthly and contractual payroll; salary structures (basic, house rent, medical, transport, technical allowances); **NBR income tax with AY thresholds, minimum tax and investment rebate**; provident fund; **gratuity at not less than 30 days' wages per completed year**; BEFTN bank file generation; payslip distribution; annual tax certificates; payroll approval and release segregation | |
| **M57** | Performance, Incentives & Compensation ★ | `PIC` | P1 | W5 | 42 | 16 | Technician scorecards from field-captured events; incentive and commission calculation; performance review cycles; compensation planning; leaderboards | |
| **M22** | Learning, Competency & Certification | `LMS` | P2 | W5 | 40 | 16 | Competency framework and skill matrix; **brand certification tracks across 17+ partners with expiry alerting**; course catalogue, enrolment, assessment and completion; Bengali content; re-certification; **dispatch eligibility enforcement (FR-LMS-039)** — a hard block on assigning uncertified technicians to brand warranty work; training effectiveness | |
| **M58** | Talent Acquisition & Onboarding ★ | `TAO` | P2 | W6 | 34 | 12 | Requisition and approval; candidate pipeline; offer approval segregation; onboarding checklists; provisioning integration with M29 and M66 | |
| **M59** | Health, Safety & Wellbeing ★ | `HSE` | P2 | W6 | 42 | 14 | **Bangladesh Labour Rules 2015** safety committee, safety officer and first-aid obligations; incident, near-miss and hazard reporting; accident notification and compensation; occupational health with restricted medical-data access; safety training linkage | |

> **Cross-wave build constraint (mandatory).** M22's eligibility check (FR-LMS-039) is consumed by
> M02 at assignment. **M02 goes live in W2; M22 in W5.** The interface must be built into M02 in
> W2 as a stub returning "eligible", and connected in W5. Retrofitting a blocking check into a
> live assignment path is materially riskier. Respondents must price this stub-and-connect
> approach explicitly.

> **Sequencing decision required (Q-05).** M59's mobile reporting — FR-HSE-009 (incident,
> near-miss and hazard reporting from the technician app) and FR-HSE-011 (immediate
> serious-incident alert) — depends only on P02 and M21, and can ship with the technician app in
> **W3** at low incremental cost. The remaining 40 requirements stay in W6. Respondents must
> state their position.

---

### 6.11 Category I — Governance, Risk, Quality & Knowledge

**4 modules · 170 requirements · 78 PW · Owner: Quality Manager / CFO**
*Per-module figures are the original estimates (+44% on recount); the category total is measured.
See §6.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M23** | Quality Management System | `QMS` | P1 | W5 | 32 | 16 | **ISO 9001:2015 and ISO 27001 evidence, executed in-system**; internal audit programme with plans, findings and verification; non-conformance reports; CAPA with effectiveness verification; complaint root-cause analysis; supplier quality; **marketplace seller quality gates identical to owned work**; SOP management and version control; quality KPI dashboards | |
| **M60** | Governance, Risk & Compliance ★ | `GRC` | P2 | W6 | 34 | 18 | Enterprise risk register; control library and testing; policy management and attestation; regulatory obligation register with currency review; **PDPA 2026 breach notification to the National Data Management Authority**; Chief Data Officer role and reporting line; compliance reporting | |
| **M24** | Document, Records & E-Signature | `DMS` | P1 | W3 | 28 | 15 | Centralised document store with version control and categorisation; template engine for service reports, quotations, invoices and certificates; **qualified e-signature for binding contracts, operational e-signature for job completion**; approval workflows with audit trail; Bengali OCR; **records retention schedules enforced by the system, minimum five years for processing records**; legal hold; evidence packs for warranty and ISO audits | |
| **M61** | Knowledge Management & Technical Library ★ | `KMS` | P2 | W6 | 24 | 13 | Repair manuals, wiring diagrams, troubleshooting guides and past repair notes; **offline availability in the technician app**; knowledge authoring and review; search across Bengali and English content; article effectiveness measurement; feeds M32 conversational AI | |

---

### 6.12 Category J — Data, Analytics & Intelligence

**4 modules · 146 requirements · 97 PW · Owner: Chief Technology Officer**
*Per-module figures are the original estimates; the category total is measured. See §6.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M62** | Data Platform, Warehouse & Governance ★ | `DAT` | P1 | W4 / W8 | 34 | 22 | ClickHouse analytical warehouse; ETL/ELT pipelines; semantic layer and certified datasets; **data quality tests that block dependent refreshes on failure**; data lineage; data catalogue; row-level security context propagation; warehouse cost management | |
| **M25** | Business Intelligence & Reporting | `BID` | P1 | W4 | 30 | 16 | Executive, branch, technician, finance, warranty, contract, marketplace and MSP dashboards; branch league tables across 51+ branches; governed self-service exploration without SQL; scheduled distribution; PDF/Excel/CSV export; threshold and anomaly alerting; embedded analytics per portal; the KPI metric registry | |
| **M26** | AI/ML Services & Model Operations | `AIM` | P2 | W6–W8 | 38 | 30 | Dispatch assignment scoring and duration prediction; parts demand forecasting; **predictive maintenance**; churn prediction; quality-risk scoring; dynamic pricing models; ML inference gateway with fallback; MLflow model registry; **model cards and drift monitoring on every production model**; human-in-the-loop on material decisions | |
| **M63** | Process Automation & Workflow Orchestration ★ | `BPA` | P1 | W3 | 28 | 16 | **One platform-wide workflow engine serving all modules** — no module implements its own; trigger-action rules; no-code configuration of workflows, forms, thresholds and business rules; approval routing; scheduled jobs with success/failure/duration reporting; automation inventory and audit | |

---

### 6.13 Category K — Platform & Technology

**7 modules · 219 requirements *(5 of 7 specified)* · 120 PW · Owner: Chief Technology Officer**
*Per-module figures are the original estimates; the category total is measured across the five
written specifications. M66 and M67 remain estimated. See §6.1 and §20.1.1.*

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Scope summary | Vendor response |
|---|---|---|:--:|:--:|---:|---:|---|---|
| **M28** | Integration, API & Event Platform | `IPF` | **P0** | W1 | 44 | 26 | Kong API gateway; the 12 API families; OpenAPI 3.1 generation and validation; **transactional outbox and domain event bus**; webhook delivery with signature verification and replay protection; idempotency; circuit breakers and graceful degradation; integration monitoring, dead-letter handling and alerting; the 47 external integrations; sandbox environments; partner onboarding | |
| **M29** | Identity, Access & Information Security | `SEC` | **P0** | W1 | 44 | 24 | Keycloak identity, SSO, MFA and federation (including per-client corporate SAML/OIDC); RBAC to field level; **6 data isolation tiers enforced by record rules**; 30 segregation-of-duties controls enforced by the permission engine at role assignment; step-up authentication; session policy; **immutable audit trail — who, what, when, before, after**; privileged session recording; access lifecycle with ≤ 1 hour deprovisioning; field-level encryption for restricted data | |
| **M64** | Master Data Management & Configuration ★ | `MDM` | P1 | W2 | 26 | 14 | Golden-record governance across party, product, location and asset; data stewardship workflow; reference data management; validation rules; data quality scoring and remediation | |
| **M65** | Multi-Entity, Multi-Country & Localisation ★ | `GLO` | P2 | W9 | 30 | 20 | Multi-entity accounting and consolidation; country pack framework with Bangladesh as reference; locale packs; multi-currency and FX; **cross-border transfer controls with Authority notification records**; entity onboarding runbook | |
| **M30** | Platform Administration & Configuration | `ADM` | **P0** | W1 | 28 | 15 | Entity, branch, zone, calendar and holiday configuration; user and role administration; feature flags allowing any new capability to be disabled without deployment; system console; job monitoring; licence register; configuration versioning and promotion; translation management | |
| **M66** | Internal IT Service Management ★ | `ITS` | P2 | W6 | 22 *(est.)* | 11 *(est.)* | Internal support ticketing; change management; internal IT asset lifecycle; consumed by M58 onboarding provisioning, M29 access requests and M59 equipment findings. **Specification outstanding — see §20.1** | |
| **M67** | Project, Program & Portfolio Management ★ | `PPM` | P2 | W7 | 26 *(est.)* | 14 *(est.)* | Project and programme tracking; portfolio prioritisation; resource planning; benefits tracking. **Specification outstanding — see §20.1** | |

---

### 6.14 Module Interaction and Critical Path

The build order is constrained by these hard dependencies. Respondents must demonstrate that
their proposed plan honours them.

```
M29 SEC + M28 IPF + M30 ADM (platform foundation)
   → M33 CPM + M37 CAT + M17 AST (masters)
      → M01 SRM + M04 FRD (intake & work)
         → M15 INV (parts consumption)
            → M02 FSM (dispatch) → M03 LOG (movement)
               → M11 PRC → M36 QTE → M20 ARB → M19 FIN (money)
                  → M08 CTR + M09 WTY (agreements)
                     → M05 RMS / M06 DTS / M13 RNT / M14 TRF / M12 MKP (new lines)
                        → M26 AIM (intelligence over accumulated data)
```

**Category boundary rules the design must honour:**

1. A module may **read** another category's data only through published APIs or the shared kernel.
2. Cross-category writes occur only via **domain events** or an explicit orchestrated command.
3. Each category owns its own scheduled jobs; no cross-category cron dependencies.
4. **Financial postings originate in Category G only.** Other categories raise *billable events*, never journal entries.
5. Identity and permission decisions are always delegated to M29; **no module implements its own authentication or authorisation**.

### 6.15 Business-Line Architecture

Nine business lines run through shared modules. Each is **configured, not coded separately**.

| Business line | Order object | Work object | Billing model | Modules engaged |
|---|---|---|---|---|
| Warranty repair | Service Order (type=warranty) | Work Order | Brand claim | M01, M02, M09, M15, M20 |
| Paid repair | Service Order (type=paid) | Work Order | Invoice on completion | M01, M02, M11, M15, M19 |
| AMC / RAMC | Contract | Scheduled Work Order | Recurring subscription | M08, M39, M01, M02, M20 |
| Managed services | MSP Contract | MSP Ticket / Patch Job | Per-seat or per-asset recurring | M05, M08, M39, M20, M27 |
| Data services | Data Case | Recovery / Backup Job | Fixed fee or subscription | M06, M20, M24 |
| Rental | Rental Agreement | Delivery / Collection / Service | Period + usage + damages | M13, M03, M17, M20 |
| Trade-in & resale | Trade-In Offer / Sales Order | Refurb Work Order | Purchase then margin on resale | M14, M38, M15, M20 |
| Marketplace | Marketplace Order | Seller Job | Commission + fees | M12, M11, M53, M23 |
| Recycling | Collection Event | Recycling Batch | Fee or material recovery credit | M18, M03, M20 |

**Design consequence.** The Service Order object must be **polymorphic by service line without
becoming a god-object**. The reference design achieves this with a thin `fix.service.order` core
plus line-specific extension models linked one-to-one, each owned by its business-line module.
Respondents proposing a different approach must demonstrate how they avoid both a god-object and
nine parallel order tables.

---

## 7. PORTAL & APPLICATION SUITE — P01 TO P12

### 7.1 Principle

The ERP is the **system of record**. Portals and applications are **surfaces** onto it.

| Rule | Consequence |
|---|---|
| No portal holds authoritative state | A portal may cache for performance, never for truth |
| No portal implements business rules | Rules live in the ERP module that owns the object |
| Every portal authenticates through M29 | One identity, one session policy, one audit trail |
| Every portal calls through the M28 gateway | One place for rate limits, versioning and observability |
| Every portal is measured | Adoption, task completion and error rates are KPIs, not afterthoughts |

### 7.2 Suite Overview

| ID | Portal / application | Users | Volume | Technology | Wave | New in v2.0 |
|---|---|---|---|---|:--:|:--:|
| **P01** | Customer Self-Service Portal & Mobile App | Individual customers | 250,000+/month | Next.js 15 (web) + Flutter/React Native (app) | W2 / W6 | |
| **P02** | Technician Mobile Application | Field & workshop technicians | 200–400 | Flutter (Android primary, iOS secondary) | W2 | |
| **P03** | Admin Operations Portal | Back-office & branch staff | 150–250 | Odoo Web (OWL 2) | W1 | |
| **P04** | Corporate B2B Portal | Corporate & government clients | 500–2,000 | Next.js 15 | W4 | |
| **P05** | Vendor & Supplier Portal | Parts vendors, couriers, sub-contractors | 200–500 | Odoo Portal + Next.js | W3 | |
| **P06** | Analytics & Executive Dashboard | Management | 25–60 | Metabase + Grafana (embedded) | W4 | |
| **P07** | Marketplace Seller Portal & App ★ | External engineers & shops | 500–2,000 | Next.js 15 + mobile | W7 | ★ |
| **P08** | Brand Partner Portal ★ | 17+ brand partners | 50–150 | Next.js 15 | W4 | ★ |
| **P09** | Logistics & Rider Application ★ | Riders, coordinators, courier staff | 50–200 | Flutter | W3 | ★ |
| **P10** | Contact Centre Agent Console ★ | Contact centre agents & supervisors | 30–80 | Next.js 15 | W4 | ★ |
| **P11** | Field Auditor & Quality Application ★ | Quality auditors, branch managers | 20–60 | Flutter | W5 | ★ |
| **P12** | Partner & Referral Portal ★ | Alliance partners, referrers, resellers | 100–500 | Next.js 15 | W7 | ★ |

### 7.3 P01 — Customer Self-Service Portal & Mobile Application

**Backing modules:** M01, M02, M03, M06, M07, M08, M09, M10, M11, M12, M13, M14, M18, M20, M27,
M33, M34, M38

| Area | Capabilities |
|---|---|
| **Account** | Register with phone/email OTP · social and biometric login · profile · multiple tagged addresses with saved GPS · household members · language preference · theme personalisation · notification preferences · **PDPA consent management** |
| **Devices** | Register devices by serial/IMEI/photo · device history · warranty status · download device history report · transfer ownership |
| **Booking** | Book a service in ≤ 3 steps · choose delivery mode (walk-in, on-site, pick & drop, remote) · select slot · describe the fault with photos and voice · upfront price indication · reschedule and cancel |
| **Tracking** | Live status timeline · live technician map with ETA · technician name and photo · push, SMS and WhatsApp updates · **public tracking link without login** |
| **Approvals** | Review estimates · approve, part-approve or decline · e-sign · view revised estimates |
| **Payments** | bKash, Nagad, card, bank transfer · invoices and receipts · payment history · saved methods · refund status |
| **Contracts** | View AMC/RAMC contracts · entitlement balance · scheduled visit calendar · renew · buy new |
| **Warranty** | Check warranty · buy extension and protection products · submit a claim · view claim status |
| **Loyalty** | Privilege status and benefits · points balance and history · redeem · vouchers · referral link and rewards |
| **Shop** | Browse and buy parts, accessories and refurbished devices · rental booking · cart, checkout, order tracking · returns |
| **Trade-in** | Submit with photos · receive an offer · accept and arrange collection · get paid |
| **Data services** | Request data recovery · case status · backup subscription status · download destruction certificates |
| **Recycling** | Book an e-waste collection or find a drop-off point · earn points |
| **Support** | AI assistant in Bengali and English · live chat · in-app hotline call · attach files · rate the conversation · transcript by email · in-app inbox · knowledge base and FAQ |
| **Feedback** | Multi-parameter service and technician rating · write a review · raise and track a complaint |

**Design requirements:** Bengali-first with English toggle, professionally translated (machine
translation is not acceptable for release) · works on 3G · **first-load payload under 400 KB on
the booking path** · PWA with offline shell and installability · WCAG 2.1 AA · booking funnel
conversion is the primary design KPI.

**KPIs:** online booking rate 40% → **88%** · booking funnel conversion > 72% · > 80% of status
enquiries self-served · > 120,000 monthly active users · app store rating > 4.5.

### 7.4 P02 — Technician Mobile Application

**Backing modules:** M01, M02, M03, M05, M06, M13, M14, M15, M17, M21, M22, M31, M59, M61

| Area | Capabilities |
|---|---|
| **Day** | Optimised job queue · accept/decline with reason · shift clock-in/out with geofence · leave request · daily summary |
| **Navigation** | Turn-by-turn navigation · route overview · automatic arrival detection |
| **Job execution** | Full job context and device history · guided diagnostic tree · fault coding · repair notes · time tracking (start/pause/resume/stop) |
| **Parts** | Van stock view · barcode/QR scan to consume · request parts not in van · return unused · van reconciliation |
| **Evidence** | Before/after photos with GPS and timestamp · short video · **voice notes in Bengali** · document scan · photo quality validation at capture |
| **Customer** | Estimate presentation and on-site approval · e-signature · on-site payment collection · receipt issue |
| **Quality** | QC checklist enforcement · test results capture · service report generation |
| **Workshop mode** | Bench assignment · WIP board · multi-job handling · L1/L2/L3 repair workflows |
| **Logistics** | Device handover and collection scanning · custody confirmation |
| **Remote** | Launch a remote support session for eligible jobs |
| **Safety** | Incident, near-miss and hazard reporting · panic/safety alert · immediate serious-incident escalation |
| **Communication** | In-app messaging with dispatch and workshop · escalation request |
| **Knowledge** | **Offline** repair manuals, wiring diagrams and past repair notes |
| **Personal** | Own performance scorecard · earnings and incentive tracker · certification status and expiry · assigned training |

**Non-negotiable requirements — these are pass/fail at Gate 2:**

| # | Requirement |
|---|---|
| 1 | Full operation offline for **24 hours** with no data loss |
| 2 | Sync within **30 seconds** of reconnection on 3G, with 100% data integrity |
| 3 | **Complete** Bengali interface, including every error message |
| 4 | Runs acceptably on a mid-range **Android 11 device with 3 GB RAM** |
| 5 | Battery consumption **under 12% per 8-hour shift** excluding navigation |
| 6 | Every state-changing action queued locally and **idempotent** on the server |
| 7 | **No feature requires a connection that a technician cannot complete offline** |

**KPIs:** daily active usage > 95% · job documentation time < 5 minutes · offline sync failures
**zero** · crash-free sessions > 99.5% · technician satisfaction > 4.2/5.

> **Risk RSK-008 — rated Critical.** Technician rejection of the mobile app is one of five risks
> that can end this programme. Four hundred people in the field decide whether it works. If the
> app is slower than paper, they will not use it, and dispatch, inventory, invoicing, warranty and
> quality all degrade. Respondents must set out, in detail, their approach to field usability
> design, technician co-design, pilot with respected senior technicians, and simplified "lite"
> mode contingency.

### 7.5 P03 — Admin Operations Portal

Delivered as **role-scoped workspaces** inside the Odoo web client, each opening on the work its
role actually does:

| Workspace | For | Opens on |
|---|---|---|
| Service Intake | Service centre agent | Queue, quick intake, customer search |
| Dispatch Console | Dispatch manager | Live map, unassigned queue, technician load, SLA risk |
| Branch Console | Branch manager | Today's numbers, WIP ageing, cash, staff, uncollected devices |
| Workshop Console | Workshop supervisor | Bench board, WIP by state, parts holds |
| Inventory Console | Inventory manager | Network stock, alerts, transfers, counts |
| Procurement Console | Procurement officer | Requisitions, POs, receipts, vendor performance |
| Finance Console | Finance officer/manager | Invoices, receipts, reconciliation, ageing, close checklist |
| HR Console | HR officer/manager | Attendance exceptions, leave, payroll run, incentives |
| Quality Console | Quality manager | NCRs, CAPAs, complaints, audits, checklists |
| Contract Console | Account manager | Contract base, renewals, entitlements, profitability |
| Warranty Console | Warranty officer | Claim pipeline, ageing, rejections, reconciliation |
| Marketplace Console | Marketplace operations | Seller approvals, disputes, scores, payouts |
| Managed Services Console | MSP operations | Estate health, alerts, tickets, SLA, patch compliance |
| System Console | IT administrator | Users, roles, configuration, jobs, integrations, health |

**Design requirements:** every workspace reachable in one click from home · any record reachable
in **≤ 4 clicks** from any starting point · bulk actions on every list view · **keyboard-first**
operation for intake, dispatch and finance · screen density suited to a **1366×768** laptop, the
most common branch hardware.

**KPIs:** walk-in intake < 3 minutes · full morning queue dispatched < 10 minutes · standard page
load < 2 seconds · new agent to competence < 4 hours.

### 7.6 P04 — Corporate B2B Portal

**Backing modules:** M05, M07, M08, M09, M11, M17, M20, M25, M27, M33

Multi-user access under one corporate account with role assignment and **multi-level approval
chains** (user → line manager → 1000FiX admin) · asset estate management with bulk upload and
site/department/user assignment · single and **bulk service requests via CSV upload** with
contract-coverage validation before submission · contracts, entitlement consumption and scheduled
maintenance calendar · managed-services estate health, incidents, alerts, patch compliance and SLA
attainment · real-time SLA status and **service credits earned** · consolidated invoicing by cycle
with approval workflow, itemised breakdown by site/department/asset, and dispute · scoped
analytics on their own estate · parts and services ordering at agreed pricing, rental requests,
trade-in and decommission projects · dedicated account manager contact · **downloadable
destruction certificates, disposal certificates and service evidence packs**.

**KPIs:** > 85% of contracted clients actively using the portal · > 70% of corporate requests
submitted through it · bulk request creation < 5 minutes · invoice disputes < 3% · client
satisfaction > 4.6/5.

### 7.7 P05 — Vendor & Supplier Portal

Onboarding with document submission and approval tracking · RFQ response with price, lead time and
validity · PO receipt, acknowledgement and query · advance shipping notices · receipt and
inspection outcomes · invoice submission against POs with matching status, payment schedule and
remittance advice · RTV notifications and credit notes · **own performance scorecard** (on-time
delivery, quality, responsiveness) · logistics partner consignment booking, status update, POD
upload and settlement claims · recycling partner batch transfers, disposal certificates and
material recovery reporting.

**KPIs:** > 90% of POs acknowledged through the portal · > 85% of invoices submitted through it ·
vendor phone/email queries −60% · RFQ response rate > 75%.

### 7.8 P06 — Analytics & Executive Dashboard

Group performance across **all 14 revenue streams** — revenue, margin, volume, cash, CSAT,
utilisation — with trend, forecast and **drill from group to a single job** · branch league tables
ranking all 51+ branches on every operational and financial dimension · purpose-built functional
dashboards for service, field, inventory, finance, HR, quality, warranty, contracts, marketplace
and managed services · live operations board (open jobs, technicians on map, SLA countdowns, queue
health, system health) · **governed self-service** on certified datasets without SQL, within
row-level security · scheduled distribution and subscription · threshold and anomaly alerting to
the right role · mobile-optimised key dashboards.

**KPIs:** executive dashboard load < 5 seconds · > 90% weekly usage by managers · **100% of
management reviews conducted on live data** · manual reporting effort −90%.

### 7.9 P07 — Marketplace Seller Portal & Application ★

Registration as a freelance engineer or shop with **NID, trade licence, references and work-sample
images**; OTP verification; approval tracking; digital agreement signature; registration fee;
expiry · profile, skills, categories, service areas, working hours, open/closed toggle · service
and product listings with pricing, availability and bulk management · broadcast jobs matching the
profile, quotations, counter-bidding, job management through to completion with evidence and
customer sign-off · customer chat on open jobs with escalation to 1000FiX · **wallet, earnings by
job, commission and fee breakdown, statements, payout history and schedule, payout request** ·
performance scorecard with explicit consequences · review responses · **boost and advertising
purchase with impressions and clicks** · required training, standards and policy acknowledgement ·
disputes with evidence.

**Governance requirements — contractually binding:**

- A seller **cannot transact** until documents are verified, the agreement is signed and admin approval is granted
- Quality and evidence standards for marketplace jobs are **identical** to owned jobs
- Payouts are **held for the defined period and blocked while a dispute is open**
- Falling below the performance threshold **automatically reduces visibility, then suspends**

**KPIs:** 500 approved active sellers by end of W8 · onboarding completion > 60% of starts ·
monthly active > 70% of approved · average rating > 4.4/5 · 12-month retention > 65%.

### 7.10 P08 — Brand Partner Portal ★

Claim submission receipt with full evidence packs · approve, part-approve, reject with reason or
request more information, with bulk actions · view photographs, diagnostic reports, parts replaced,
**technician certification** and purchase proof for any claim · reconciliation of submitted,
approved and paid claims with remittance advice upload · consignment parts visibility, consumption
reporting, replenishment requests and defective returns · publish and version labour rates, parts
pricing and claim rules · view 1000FiX service performance on their brand — volume, TAT,
first-time fix, rework, CSAT, failure patterns by model · raise quality concerns, view CAPA
responses, conduct partner audits with evidence access · view certification status of technicians
authorised on their brand · bulletins, technical notices and recall notifications.

**KPIs:** > 80% of claims submitted through the portal rather than email · average claim decision
< 10 days · approval rate > 92% · brand partner satisfaction > 4.5/5 · days from service to
reimbursement < 45.

### 7.11 P09 — Logistics & Rider Application ★

Daily optimised pickup and delivery manifest with route overview · collection: scan consignment,
verify against manifest, photograph items and packaging, seal number entry, customer OTP and
signature, issue receipt · transit status and exception recording (customer absent, wrong address,
refused, damaged) · delivery: recipient identity verification, handover scan, photo, OTP,
signature, payment collection · **every handover recorded with GPS, timestamp and both parties'
identity** · cash collected on delivery with end-of-shift reconciliation · **full offline
operation with queued sync** · coordinator web view: real-time pending/in-transit/delivered/
exception dashboard, rider and courier assignment, rescheduling, SLA monitoring.

**KPIs:** POD capture completeness **100%** · on-time collection and delivery > 93% · **custody
breaks: zero** · rider app offline reliability 100%.

### 7.12 P10 — Contact Centre Agent Console ★

Unified queue across voice, chat, WhatsApp, email, SMS and social with priority and SLA visible ·
**automatic screen-pop of Customer 360 on caller identification** with full cross-channel history,
open jobs, contracts, entitlements and dues · answer, hold, transfer, conference, consult · canned
responses in Bengali and English · knowledge base search · **create a service order, reschedule,
quote, take payment, renew a contract or raise a complaint without leaving the conversation** ·
jump to any ERP screen and return with the conversation intact · remote assistance launch with
consent capture · AI-suggested responses and next-best-action while the conversation is live ·
structured disposition coding, notes and follow-up tasks · recording playback, quality scoring and
coaching · live supervision with barge-in and whisper.

**KPIs:** average handling time −25% vs baseline · first-contact resolution > 78% · **agent screen
switches per contact < 3** · disposition coding completeness 100% · agent satisfaction > 4.2/5.

### 7.13 P11 — Field Auditor & Quality Application ★

Assigned audits, scheduling, scope and checklists · **offline** checklist completion with photo and
document evidence, observations recorded against clauses · findings with classification, severity,
linkage to processes, people and records, and owner assignment · on-site CAPA verification · branch
checks: cash spot checks, inventory spot counts, equipment and safety checks, 5S/housekeeping ·
marketplace seller audits against platform standards · on-device audit report generation with
auditee acknowledgement signature, syncing to M23.

**KPIs:** audit plan completion 100% · **100% of audits completed on mobile rather than paper** ·
finding-to-CAPA cycle time < 5 days · evidence attached to findings 100%.

### 7.14 P12 — Partner & Referral Portal ★

Application, document submission, agreement signature and approval · referral link and code
generation, direct lead submission, lead status tracking through to conversion · partner benefit
schedule · commission earned by referral, statements, payout schedule and history · approved
marketing materials, co-branded campaign requests, campaign performance · for resellers:
refurbished stock allocation, pricing, ordering, fulfilment and settlement · performance —
leads submitted, conversion rate, revenue attributed, ranking.

**KPIs:** > 200 active referral partners by end of W8 · > 12% of new customers referral-attributed
· partner commission accuracy **100%** · > 75% of approved partners adopting the portal.

### 7.15 Cross-Portal Standards

| # | Standard | Applies to |
|---|---|---|
| PS-01 | Single sign-on through M29; **no portal maintains its own credential store** | All |
| PS-02 | All API traffic through the M28 gateway with per-portal credentials and rate limits | All |
| PS-03 | Bengali and English throughout, **Bengali default** on customer and field surfaces | All |
| PS-04 | WCAG 2.1 AA accessibility | All web portals |
| PS-05 | Responsive from 320 px upward; no horizontal scrolling | All web portals |
| PS-06 | Consistent 1000FiX design system — **one component library, one token set** across all 12 | All |
| PS-07 | Works acceptably on 3G; critical paths under 400 KB first load | P01, P02, P07, P09 |
| PS-08 | Offline-capable with queued sync | P02, P09, P11 |
| PS-09 | Every user-visible error states what happened and what to do next, in the user's language | All |
| PS-10 | Analytics instrumentation on every critical funnel, feeding M25 | All |
| PS-11 | **No business rule implemented client-side**; the client validates for convenience only | All |
| PS-12 | Session, idle timeout and MFA policy inherited from M29, never portal-specific | All |

---

## 8. CROSS-CUTTING SPECIFICATIONS

### 8.1 Data Model

**225 entities.** Modelling standards are mandatory:

| # | Standard | Detail |
|---|---|---|
| DM-01 | Naming | Odoo models prefixed `fix.`; tables `fix_`; snake_case columns |
| DM-02 | Three-tier hierarchy | Odoo native → OCA extension → custom `cd_*` module |
| DM-03 | Dimensional context | Every transactional model carries `company_id`, `operating_unit_id`, and where relevant `zone_id`, `cost_center_id`, `business_line_id` |
| DM-04 | Chatter & activity | Every business model inherits `mail.thread` and `mail.activity.mixin` |
| DM-05 | Audit fields | Create/write user and date on all; explicit audit entries for controlled objects |
| DM-06 | Soft delete | Business records archived, **never hard-deleted** |
| DM-07 | Money | `Monetary` fields with explicit `currency_id`; **never floats** |
| DM-08 | Time | Stored UTC; presented `Asia/Dhaka`; durations in minutes |
| DM-09 | Text | UTF-8 throughout; Bengali collation `bn_BD` with ICU fallback |
| DM-10 | State machines | Explicit `state` field with the transition map declared in one place |
| DM-11 | Sequences | Branch- and business-line-aware with configurable masks |
| DM-12 | Referential integrity | Foreign keys enforced **at the database level**; `ondelete` policy declared |
| DM-13 | Extension pattern | Business-line specialisation via one-to-one extension models, **not by widening the core model** |
| DM-14 | Sensitive data | Fields classified S0–S3; S3 encrypted at field level and access-logged |
| DM-15 | Events | Every state change writes to the outbox table **in the same transaction** |

Entity growth from v1.0: service core 11 → 26 · logistics 0 → 11 · managed services 0 → 14 · data
services 0 → 8 · commercial 8 → 31 · marketplace 0 → 22 · rental 0 → 12 · refurbishment 0 → 10 ·
assets & IoT 2 → 15 · ESG 0 → 7 · finance & billing 9 → 28 · people & competency 4 → 17 · platform
6 → 24.

### 8.2 Integration & API Catalogue — 47 External Integrations

#### 8.2.1 Integration principles

| # | Principle | Consequence |
|---|---|---|
| IP-01 | The ERP is the system of record; integrations synchronise, they do not duplicate authority | Every field has one owning system, declared |
| IP-02 | All traffic passes through the API gateway | One place for auth, rate limits, versioning, observability |
| IP-03 | Every integration declares its pattern | Sync · async command · domain event · webhook · batch file |
| IP-04 | Every integration is idempotent | Retries and replays never double-apply |
| IP-05 | Every integration fails safely | Circuit breakers, timeouts, graceful degradation with user-visible messaging |
| IP-06 | Every integration is observable | Health, throughput, latency and error rate dashboards with alerting |
| IP-07 | **No credentials in code or configuration files** | Vault-stored, rotated, access-audited |
| IP-08 | Every external contract is versioned and documented | OpenAPI 3.1 for REST; JSON Schema for events |
| IP-09 | Third-party outages must not stop the business | **Documented, tested manual fallback for every P0 integration** |
| IP-10 | Data leaving the Company is minimised and logged | Only the fields the counterparty needs |

#### 8.2.2 The catalogue

| Group | Count | Integrations |
|---|---:|---|
| **Payments** | 9 | bKash (P0) · Nagad (P0) · SSLCOMMERZ (P0) · Rocket · **Bank BEFTN** (P0, batch) · bank statement import (P0) · seller payout rail · international gateway (Stripe/PayPal) · instalment/BNPL partner |
| **Communications** | 9 | Bangladesh SMS gateway primary (P0) + failover · **WhatsApp Business Cloud API** (P0) · email SMTP/IMAP (P0) · push FCM/APNs (P0) · **cloud telephony/IVR for hotline 16743** · WebRTC video · social messaging (Messenger, IMO) · in-app chat infrastructure |
| **Location, mapping & logistics** | 9 | Google Maps Platform (P0) · OSRM · VROOM · traffic data · **Traccar GPS server** (P0) · courier partners Pathao, RedX, Steadfast/Sundarban · international freight forwarder |
| **Remote support & monitoring** | 6 | Remote desktop (RustDesk/MeshCentral) · monitoring agent telemetry · SNMP/ICMP collector · patch feed · endpoint protection console · cloud provider APIs (M365/Google/AWS) |
| **Marketplace & trust** | 4 | **NID/identity verification** (P0) · trade licence/business registry check · **IMEI/stolen-device blocklist** · ad delivery service |
| **Government & compliance** | 5 | **NBR e-VAT filing** (P0) · BIN/TIN validation · e-waste authority reporting · biometric attendance devices · RJSC company registry |
| **AI, data & enterprise** | 5 | Self-hosted LLM inference · OCR (including Bengali) · Bengali speech-to-text · corporate client SSO (SAML/OIDC per client) · client ITSM (ServiceNow/Jira) |
| | **47** | **P0 12 · P1 17 · P2 12 · P3 6** |

#### 8.2.3 Mandatory fallback register for P0 integrations

| Integration | Fallback |
|---|---|
| bKash / Nagad / SSLCOMMERZ | Alternative gateway; cash at counter; payment link resent on restoration |
| SMS gateway | Failover gateway; WhatsApp; push; queued for retry |
| WhatsApp | SMS; email; in-app inbox |
| Google Maps | Cached geocodes; OSRM-only routing; manual address entry |
| Traccar | Last known position; manual status updates by technician |
| Bank statement import | Manual statement upload |
| BEFTN | Manual bank file submission via bank portal |
| NBR e-VAT | Manual portal filing from the generated return |
| Identity verification | Manual document review by compliance |
| Push notifications | SMS fallback for critical messages |
| LLM inference | Rule-based responses; direct human routing |
| Telephony | Divert hotline to mobile numbers with manual logging |

#### 8.2.4 The portal platform contract (constraint CON-03)

The Next.js 15 + Payload CMS 3 platform **cannot be replaced**. This is the most important
integration in the estate and has its own contract.

**Field ownership:**

| Data | Owned by | Direction | Sync |
|---|---|---|---|
| Customer identity and profile | ERP (M33/M07) | ERP → Portal | Event-driven, near real-time |
| Customer authentication | Identity provider (M29) | Shared | Federated |
| Marketing content, pages, blog, SEO | Portal (Payload CMS) | Portal only | — |
| Service catalogue and prices | ERP (M37, M11) | ERP → Portal | Scheduled + on change |
| Branch and coverage data | ERP (M30) | ERP → Portal | On change |
| Booking availability | ERP (M02) | Portal queries ERP | Synchronous |
| Service orders | ERP (M01) | Portal → ERP on create; ERP → Portal on update | Sync + events |
| Order status and tracking | ERP (M01, M02) | ERP → Portal | Events + polling fallback |
| Invoices and payments | ERP (M19, M20) | ERP → Portal | Events |
| Contracts and entitlements | ERP (M08) | ERP → Portal | Events |
| Loyalty points and vouchers | ERP (M10) | ERP → Portal | Events |
| Reviews and ratings | ERP (M12/M34) | Portal → ERP on submit; ERP → Portal on publish | Sync |

**Contract rules:** both sides support at least **two API versions concurrently** with six months'
deprecation notice · every POST accepts an `Idempotency-Key` and duplicate keys return the original
result · OAuth 2.0 client credentials per environment with short-lived tokens · 600 requests/minute
per portal instance, burst 100/second · portal timeout 5 s, ERP responds within **2 s at p95** ·
portal degrades gracefully with cached catalogue and queued booking · **nightly reconciliation job
compares order and customer counts with divergence alerting**.

#### 8.2.5 Domain event catalogue

Events are **facts about the past**, named `<aggregate>.<past-tense-verb>`, carrying a standard
envelope: `event_id`, `event_type`, `schema_version`, `occurred_at`, `company_id`,
`operating_unit_id`, `actor`, `correlation_id`, `causation_id`, `aggregate`, `payload`.

**Consumer rules:** every consumer records processed `event_id`s and ignores duplicates · ordering
guaranteed **per aggregate id only, never globally** · three retries with exponential backoff, then
dead-letter with alert · any consumer replayable from a point in time without side effects on
others · additive schema changes only within a version; breaking changes require a new
`schema_version` and a dual-publish period · **95% of events consumed within 5 seconds**.

The principal event inventory spans approximately 65 event types across service order, work order,
technician, SLA, consignment, part, stock, goods, asset, contract, warranty claim, invoice,
payment, refund, commission, payout, seller, review, dispute, rental, trade-in, refurb, wipe,
e-waste, alert, MSP ticket, employee, certification, payroll, non-conformance, CAPA, complaint,
customer, price book and model-prediction domains.

#### 8.2.6 API standards

| # | Standard |
|---|---|
| API-01 | REST over HTTPS with JSON; GraphQL only through the federation layer for composed portal reads |
| API-02 | Versioned in the path (`/v1/`); minimum two concurrent versions; six months' deprecation notice |
| API-03 | OpenAPI 3.1 generated from code, validated in CI, published to the developer portal |
| API-04 | Standard error envelope: `code`, `message` (localised), `details`, `correlation_id` |
| API-05 | Cursor-based pagination on all collections; maximum page size enforced |
| API-06 | Filtering, sorting and sparse field selection on all collection endpoints |
| API-07 | `Idempotency-Key` supported and **required** on all state-changing operations |
| API-08 | Rate limits per consumer with `X-RateLimit-*` headers and 429 with `Retry-After` |
| API-09 | Every response carries a `correlation_id` for tracing |
| API-10 | **No endpoint returns data outside the caller's authorisation scope, ever** — enforced server-side |
| API-11 | Bengali and English error and validation messages driven by `Accept-Language` |
| API-12 | Payload size limits enforced; large exports go through an async job with a download link |

**API performance targets:**

| Endpoint class | p50 | p95 | p99 |
|---|---|---|---|
| Status / lookup reads | 80 ms | 250 ms | 500 ms |
| Standard reads with joins | 150 ms | 400 ms | 800 ms |
| Writes (create/update) | 200 ms | 500 ms | 1,000 ms |
| Search | 200 ms | 600 ms | 1,200 ms |
| Availability calculation | 300 ms | 800 ms | 1,500 ms |
| Analytics queries | 1 s | 5 s | 10 s |

#### 8.2.7 Offline synchronisation protocol (P02, P09, P11)

| Aspect | Design |
|---|---|
| Local store | **Encrypted** local database with an append-only action journal |
| Data scope | Only the user's assigned work plus the reference data they need; re-evaluated on each sync |
| Action model | Every user action is a discrete, idempotent command with a client-generated UUID |
| Upload | Commands replayed in order on reconnection; server acknowledges each by UUID |
| Download | Delta since last successful sync token; full refresh available on demand |
| Conflict policy | **Server authoritative** for assignment, pricing, stock and state; **client wins** for evidence, notes and timestamps captured in the field |
| Conflict visibility | Any resolved conflict is shown to the user with what changed and why |
| Duration guarantee | **24 hours** of offline operation with no data loss |
| Sync target | Complete within **30 seconds** of connectivity restoration on 3G |
| Integrity | Checksums on every batch; failed batches retried, **never partially applied** |
| Storage | Automatic pruning of synced, closed work older than the retention window |

#### 8.2.8 Integration delivery sequence

| Wave | Integrations |
|---|---|
| W1 | SMS, WhatsApp, email |
| W2 | Redundant SMS, push, Google Maps, OSRM, VROOM, traffic, Traccar |
| W3 | bKash, Nagad, SSLCOMMERZ, Rocket, bank statement import, couriers, BIN/TIN validation, OCR |
| W4 | Telephony/IVR, in-app chat, NBR e-VAT |
| W5 | BEFTN, remote desktop, monitoring agents, SNMP, biometric attendance |
| W6 | Video, social messaging, patch feed, EDR console, cloud provider APIs, IMEI check, LLM, corporate SSO |
| W7 | Seller payout rail, KYC, trade licence check, ad server, client ITSM |
| W8 | Instalment/BNPL, e-waste authority reporting, Bengali speech-to-text |
| W9 | International gateway, international freight, RJSC registry |

### 8.3 Role, Permission & Access Model

#### 8.3.1 The role register — 38 registered roles

| Group | Roles | Count |
|---|---|---:|
| Executive & management | R01 CEO · R02 CTO · R03 CFO · R04 CCO · R05 Operations Director | 5 |
| Service operations | R06 Branch Manager · R07 Dispatch Manager · R08 Service Centre Agent · R09 Workshop Supervisor · R10 Senior Technician · R11 Junior Technician · R12 Specialist Technician (L3) · R13 Remote Support Engineer · R14 Data Services Technician | 9 |
| Logistics & supply chain | R15 Logistics Coordinator · R16 Rider · R17 Inventory Manager · R18 Branch Store Keeper · R19 Procurement Officer · R20 Warehouse Operative | 6 |
| Commercial | R21 Sales Manager · R22 Account Manager · R23 Marketing Manager · R24 Marketplace Operations Officer · R25 Retail/Refurbishment Officer | 5 |
| Finance, people & governance | R26 Finance Manager · R27 Finance Officer · R28 Warranty Claims Officer · R29 Cashier · R30 HR Manager · R31 HR Officer · R32 Quality Manager / ISO Coordinator | 7 |
| Technology & support | R33 IT/System Administrator · R34 Contact Centre Agent · R35 Contact Centre Supervisor | 3 |
| External | R36 Customer · R37 Corporate Portal User · R38 External Party (vendor, seller, brand, courier, referral, recycling, external auditor) | 3 |

> **Disclosed defect (audit finding H2-07).** Eight further roles — **R39 Data Steward, R40 Chief
> Data Officer, R41 Payroll Officer, R42 Training Coordinator, R43 Competency Assessor, R44 HSE
> Officer, R45 Recruiter, R46 Occupational Health** — are defined and used inside module
> specifications but are not yet in the central register. Two identifiers (R54, R57) are
> referenced with no definition, and **R60 is a duplicate identity for R32 and must be
> eliminated**. Formalisation to R46 and elimination of R60 is required before Wave 1 build. The
> successful respondent will be expected to complete this reconciliation as part of Wave 1.
> **Bid on 46 roles.**

#### 8.3.2 Data isolation tiers

| Tier | Rule | Enforced by | Objects |
|---|---|---|---|
| **T0 — Global** | Visible to all authenticated internal users | No record rule | Service catalogue, parts catalogue, brand and model master, checklist templates, knowledge base, branch directory |
| **T1 — Entity** | Visible within the legal entity | `company_id` rule | Chart of accounts, tax configuration, payroll structures, entity policies |
| **T2 — Branch** | Visible within the operating unit | `operating_unit_id` rule | Service orders, work orders, inventory, cash, branch HR, queue, local documents |
| **T3 — Zone** | Visible within the dispatch zone | `zone_id` rule | Technician schedules, van stock, dispatch assignments, route plans |
| **T4 — Own record** | Visible only to the owner or assignee | `partner_id` / `user_id` rule | Customer's own orders and invoices; technician's own jobs and earnings; seller's own listings and payouts; vendor's own POs |
| **T5 — Restricted** | Explicit grant only, access logged, step-up authentication | Named allow-list + audit | Individual payroll, NID records, bank details, data-recovery case content, call recordings, audit logs, biometric templates, seller KYC documents |

#### 8.3.3 Field-level permissions

Fields visible only to named roles include: `unit_cost` / `total_cost` / `margin` ·
`salary` / `allowances` / `deductions` · `nid_number` · `bank_account` ·
`recovered_data_index` · `call_recording_url` · `commission_rate` · `seller_kyc_document` ·
`technician_incentive_detail` · `customer_credit_limit` · `internal_note` (**never exposed to any
external portal**) · `vendor_price` · `model_confidence` / `model_features`.

#### 8.3.4 Segregation of duties

Thirty SoD controls must be enforced **by the permission engine at role assignment**, not by
policy. The registered set (SOD-01…SOD-12) includes:

| # | Incompatible duties | Risk | Enforcement |
|---|---|---|---|
| SOD-01 | Create vendor + approve vendor invoice | Fictitious vendor payment | Hard block |
| SOD-02 | Raise PO + receive goods + approve invoice | Purchase fraud | Hard block (any two permitted, not all three) |
| SOD-03 | Process payroll + approve payroll | Payroll fraud | Hard block |
| SOD-04 | Create credit note + approve credit note | Revenue leakage | Hard block |
| SOD-05 | Adjust inventory + perform the justifying count | Theft concealment | Hard block |
| SOD-06 | Approve marketplace seller + approve their payout | Collusion | Hard block |
| SOD-07 | Repair a device + perform its independent QC | Quality concealment | Hard block above value threshold |
| SOD-08 | Create customer + approve their credit limit | Credit fraud | Warning + approval |
| SOD-09 | Administer users + approve own access requests | Privilege escalation | Hard block |
| SOD-10 | Value a trade-in + purchase it + resell it | Asset misappropriation | Hard block |
| SOD-11 | Raise a warranty claim + approve its write-off | Claim manipulation | Hard block |
| SOD-12 | Handle cash + reconcile the cash book | Cash misappropriation | Hard block |

> **Disclosed defect (audit finding H2-06).** A further **18 SoD controls (SOD-13…SOD-30)** are
> implemented in module specifications but are not yet in the central matrix — including SOD-29
> (payroll approver cannot release the bank file) and SOD-30 (M57 calculates the incentive; only
> M56 can pay it). **Controls that cannot be evidenced are, for audit purposes, controls that do
> not exist.** Registration of all 30 is required before Wave 1 build and forms part of the
> successful respondent's Wave 1 scope. **Bid on 30 controls.**

Exceptions require CFO or CTO approval, are time-boxed, and appear on a standing exception report
reviewed quarterly.

#### 8.3.5 Approval authority matrix

| Transaction | Threshold | Approver |
|---|---|---|
| Repair estimate | > BDT 5,000 | Customer + system record |
| Repair estimate | > BDT 25,000 | Customer + Branch Manager |
| Repair estimate | > BDT 100,000 | Customer + Operations Director |
| Discount | ≤ 10% / ≤ 20% / ≤ 35% / > 35% | Agent / Branch Manager / Sales Manager / CCO |
| Purchase requisition | ≤ 50K / ≤ 500K / ≤ 2M / > 2M BDT | Inventory Manager / Procurement Manager / CFO / CEO |
| Credit note | ≤ BDT 10,000 / above | Finance Officer / Finance Manager |
| Inventory write-off | ≤ BDT 25,000 / above | Inventory Manager / CFO |
| Contract — standard / non-standard terms | Any value | Sales Manager / CCO + CFO |
| Marketplace seller payout | Standard / held or disputed | Automatic on schedule / Finance Manager |
| Trade-in offer | ≤ BDT 30,000 / above | Retail Officer / Retail Manager + Finance |
| Payroll run | Any | HR Manager + CFO |
| **Data destruction** | Any | Data Services Technician + witness |
| Access request — standard / privileged | Any | Line Manager / Line Manager + IT Admin + CTO |
| SoD exception | Any | CFO or CTO, time-boxed |

#### 8.3.6 External party access rules

| Rule | Detail |
|---|---|
| EA-01 | An external party may see only records where they are a named party |
| EA-02 | An external party **never** sees cost, margin, internal notes or other parties' data |
| EA-03 | Corporate portal users see only their own company's data, further scoped by their role in that company |
| EA-04 | A marketplace seller sees the customer's name, contact and address **only for a job they have been awarded, and only until a defined period after completion** |
| EA-05 | A brand partner sees only claims and service data relating to their own brand |
| EA-06 | A vendor sees only their own purchase orders, receipts and invoices |
| EA-07 | A courier partner sees only consignments assigned to them, with the minimum data needed to deliver |
| EA-08 | External sessions time out after 30 minutes of inactivity |
| EA-09 | **MFA is mandatory for any external action with financial consequence** |
| EA-10 | Every external access to customer personal data is logged and reportable |
| EA-11 | External API access is scoped by credential; **scope cannot be widened by request parameters** |
| EA-12 | Bulk export by external parties is limited, rate-controlled and logged |

#### 8.3.7 Access lifecycle

| Stage | Trigger | Action |
|---|---|---|
| **Provision** | `employee.joined` event from M21 | Identity created; role assigned from the position profile; portal access granted; training assigned |
| **Modify** | Transfer, promotion, role change | Old permissions revoked and new granted on the effective date; **no accumulation** |
| **Elevate** | Approved access request | Time-boxed elevation with automatic expiry and session recording |
| **Review** | Quarterly | Manager confirms or revokes each report's access; **unconfirmed access is revoked** |
| **Suspend** | Leave of absence, investigation | Access disabled, records preserved |
| **Deprovision** | `employee.left` event from M21 | **All access revoked within 1 hour**; devices deregistered; delegated authority reassigned |
| **External expiry** | Agreement or registration expiry | External access automatically disabled; data retained per retention schedule |

**Control:** zero orphaned accounts beyond 24 hours after a leaver event, measured weekly
(KPI-090).

### 8.4 Business Rules & Automation

Business rules are the enforced behaviour of the system. Implementation standards:

| # | Standard | Detail |
|---|---|---|
| BR-STD-01 | Rules are enforced **at the model layer**, never only in the UI | A rule bypassed by an API call is not a rule |
| BR-STD-02 | Every rule has an identifier, an owner and a test | Rules without tests are not released |
| BR-STD-03 | Thresholds are **configuration, not code** | Values change without a deployment |
| BR-STD-04 | Every violation produces a message stating what is wrong and what to do, in the user's language | |
| BR-STD-05 | Hard rules block; soft rules warn and log | Classification is explicit per rule |
| BR-STD-06 | Overrides are possible only where designed, and **always logged with a reason and an approver** | No silent overrides |
| BR-STD-07 | Rules are versioned; changing one requires the owner's approval | Audit of what was in force when |

**Rule classes:** **H** hard (blocks, no override) · **A** approved override (blocks, named role
may override with recorded reason) · **S** soft (warns and logs) · **C** computed (derives a value,
not user-overridable).

Respondents must demonstrate **negative testing through both UI and API** for every hard rule
(definition-of-done criterion DoD-04).

---

## 9. NON-FUNCTIONAL REQUIREMENTS

**101 numbered non-functional requirements (NFR-001 … NFR-101).** The full register is in Annex 1;
the binding targets are below. Every one is measurable and will be tested before the relevant wave
gate.

### 9.1 Performance

| ID | Requirement | Target | Measured by | Pri |
|---|---|---|---|:--:|
| NFR-001 | ERP screen load under normal load | ≤ **2 s p95** *(was 3 s in v1.0)* | Synthetic monitoring | P0 |
| NFR-002 | API response time | ≤ **400 ms p95** *(was 500 ms)* | Gateway metrics | P0 |
| NFR-003 | Concurrent internal users without degradation | **800+** *(was 500)* | Load test | P0 |
| NFR-004 | Concurrent customer portal users | **75,000+** *(was 50,000)* | Load test | P0 |
| NFR-005 | Standard report generation | ≤ **20 s** *(was 30 s)* | Report timing log | P1 |
| NFR-031 | Customer 360 view load | ≤ 2 s | Instrumentation | P0 |
| NFR-032 | Booking availability calculation | ≤ 800 ms p95 | API metrics | P0 |
| NFR-033 | Dispatch board refresh | ≤ 1 s for 500 open jobs | Instrumentation | P1 |
| NFR-034 | Live map update latency | ≤ 5 s from GPS emission | End-to-end trace | P1 |
| NFR-035 | Search results, any entity **including Bengali text** | ≤ 600 ms p95 | Instrumentation | P1 |
| NFR-036 | Technician app job list load **on 3G** | ≤ 8 s cold, ≤ 2 s warm | Field test | P0 |
| NFR-037 | Offline sync completion after 24 h offline | ≤ **30 s on 3G** | Field test | P0 |
| NFR-038 | Executive dashboard load | ≤ 5 s | Instrumentation | P1 |
| NFR-039 | Analytical warehouse query | ≤ 10 s p95 | Warehouse metrics | P2 |
| NFR-040 | Invoice generation from job closure | ≤ **5 s** | Instrumentation | P0 |
| NFR-041 | Bulk operation (1,000 records) | ≤ 60 s with progress feedback | Load test | P1 |
| NFR-042 | Payment confirmation round trip | ≤ 3 s p95 | Gateway metrics | P0 |
| NFR-043 | Event delivery to consumer | ≤ 5 s p95 | Event platform metrics | P1 |
| NFR-044 | Nightly route optimisation, all technicians | ≤ 20 minutes | Job monitor | P1 |

### 9.2 Availability & Continuity

| ID | Requirement | Target | Pri |
|---|---|---|:--:|
| NFR-006 | Uptime during Bangladesh business hours (09:00–22:00 BST) | ≥ **99.9%** | P0 |
| NFR-045 | Uptime 24×7 (managed services requires it) | ≥ 99.7% | P1 |
| NFR-007 | Disaster recovery | **RPO ≤ 15 min, RTO ≤ 2 h** *(was 1 h / 4 h)* | P0 |
| NFR-008 | Zero-downtime deployment for planned changes | Standard for all releases | P1 |
| NFR-046 | Customer portal availability | ≥ 99.9% | P0 |
| NFR-047 | Technician app functional without connectivity | **24 hours** | P0 |
| NFR-048 | Payment path availability | ≥ **99.95%** with multi-gateway failover | P0 |
| NFR-049 | Planned maintenance window | Outside 08:00–23:00 BST; ≤ 4 h/month; announced 72 h ahead | P1 |
| NFR-050 | Graceful degradation | Every P0 integration has a documented, **tested** manual fallback | P0 |
| NFR-051 | DR drill | Full failover exercised **twice yearly** with documented results | P0 |
| NFR-052 | Backup verification | Automated restore test **weekly** | P0 |

### 9.3 Scalability

| ID | Requirement | Target | Pri |
|---|---|---|:--:|
| NFR-009 | Growth headroom without re-architecture | **5× users and 10× data over 5 years** | P0 |
| NFR-010 | Elastic capacity for demand peaks | Automatic scaling for seasonal and promotional peaks | P1 |
| NFR-053 | Service order volume | **5 million per year by year 5** | P0 |
| NFR-054 | Device registry | **5 million assets** | P0 |
| NFR-055 | Telemetry ingestion | 50,000 points per minute | P2 |
| NFR-056 | GPS ingestion | 400 technicians at 30-second intervals, sustained | P1 |
| NFR-057 | Marketplace scale | 5,000 sellers, 50,000 listings | P2 |
| NFR-058 | Branch scale | **200 branches without configuration redesign** | P1 |
| NFR-059 | Multi-entity scale | 10 legal entities across 5 countries | P2 |
| NFR-060 | Document store | 50 TB with sub-10-second retrieval | P1 |

### 9.4 Security

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-011 | Role-based access control with **field-level** granularity | P0 |
| NFR-012 | MFA mandatory for admin, finance, HR and all privileged roles | P0 |
| NFR-013 | AES-256 at rest; TLS 1.2+ (TLS 1.3 preferred) in transit | P0 |
| NFR-014 | Complete **immutable** audit trail — who, what, when, before, after | P0 |
| NFR-015 | Branch-level data isolation enforced **at the record level** | P0 |
| NFR-061 | Field-level encryption for restricted data with separate key material | P0 |
| NFR-062 | Secrets in a vault; never in code, configuration files or logs | P0 |
| NFR-063 | Malware scanning on every file upload before storage or serving | P0 |
| NFR-064 | Segregation of duties enforced by the permission engine | P0 |
| NFR-065 | Step-up authentication for sensitive actions | P0 |
| NFR-066 | Automated dependency, container and infrastructure vulnerability scanning in CI and production | P1 |
| NFR-067 | Annual penetration test with findings tracked to closure | P1 |
| NFR-068 | Rate limiting and bot protection on all public endpoints | P0 |
| NFR-069 | Session policy: 30-min idle external, 60-min internal, absolute 12-hour maximum | P0 |
| NFR-070 | All privileged sessions recorded | P1 |
| NFR-071 | **Non-production environments use masked data only** | P0 |
| NFR-072 | Security incident response with defined severities and breach-notification assessment | P1 |

### 9.5 Usability & Accessibility

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-016 | Full Bengali and English in interfaces, notifications, reports and data entry | P0 |
| NFR-017 | Technician app on **Android 11+ with 3 GB RAM on intermittent 4G** | P0 |
| NFR-018 | Offline mode with automatic sync on reconnection | P0 |
| NFR-019 | Responsive design for mobile, tablet and desktop across all portals | P0 |
| NFR-020 | Low-bandwidth mode for field and rural operation | P0 |
| NFR-073 | WCAG 2.1 AA compliance on all web portals | P1 |
| NFR-074 | Bengali input including phonetic typing and voice-to-text on mobile | P1 |
| NFR-075 | New service agent reaches competence in ≤ 4 hours of training | P1 |
| NFR-076 | **Walk-in intake completed in ≤ 3 minutes** | P1 |
| NFR-077 | Any record reachable in ≤ 4 clicks from any starting point | P1 |
| NFR-078 | Every error message states what happened and what to do next, in the user's language | P1 |
| NFR-079 | Destructive actions require confirmation and are reversible where possible | P1 |
| NFR-080 | **Consistent design system across all 12 portals** — one component library, one token set | P1 |
| NFR-081 | Critical customer paths under 400 KB first load | P1 |
| NFR-082 | Technician app battery consumption ≤ 12% per 8-hour shift excluding navigation | P1 |

### 9.6 Maintainability & Operability

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-026 | API-first architecture with documented REST APIs for all integrations | P0 |
| NFR-027 | **No-code configuration** for workflows, forms, thresholds and business rules | P0 |
| NFR-028 | Customisation without modifying core product code | P0 |
| NFR-090 | Unit test coverage ≥ **80%** on custom code; **100% on financial calculations** | P0 |
| NFR-091 | Every module ships with an operational runbook | P0 |
| NFR-092 | Distributed tracing across all services with a single correlation id | P1 |

**Operability standards:** every deployment automated, repeatable and reversible · configuration
versioned and promoted through environments, **never hand-edited in production** · every alert has
a runbook entry; alerts without actions are removed · logs structured and searchable with **no
personal data in logs** · every scheduled job reports success, failure and duration — **silent
failure is a defect** · feature flags allow any new capability to be disabled without a deployment
· database migrations forward-only, tested against a production-sized dataset, reversible by a
documented procedure · capacity reviewed monthly against growth.

### 9.7 Data Integrity

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-029 | All transactions ACID-compliant with full rollback | P0 |
| NFR-030 | Automated backups: daily/30 days, weekly/1 year, **monthly/7 years** | P0 |
| DI-01 | Financial calculations use decimal arithmetic; **no floating point in money paths** | P0 |
| DI-02 | Every financial posting reconcilable to its source transaction | P0 |
| DI-03 | Referential integrity enforced at the database level, not only in application code | P0 |
| DI-04 | Offline sync guarantees **zero data loss and zero double-application** | P0 |
| DI-05 | Event delivery at-least-once with idempotent consumption | P0 |
| DI-06 | Data quality tests run on every warehouse load; **failures block dependent refreshes** | P1 |
| DI-07 | Cross-system reconciliation runs nightly with divergence alerting | P1 |
| DI-08 | **Soft deletion only**; hard deletion requires an approved, logged procedure | P0 |

### 9.8 Localisation Standards

| Aspect | Standard |
|---|---|
| Primary language (field & customer) | **Bengali (bn-BD)** |
| Secondary language | English (en) |
| Character encoding | UTF-8 throughout |
| Bengali collation | ICU `bn-BD` for sorting and comparison |
| Bengali fonts | Rendered correctly across Android, iOS, Windows and print output |
| Bengali input | Phonetic and Unicode keyboard; voice-to-text on mobile |
| Number format | **Bangladeshi lakh/crore grouping (12,34,567)** in Bengali locale; international grouping in English locale |
| Currency | **BDT (৳) primary**, two decimal places; multi-currency supported |
| Date format | DD/MM/YYYY; Bengali month names in the Bengali locale |
| Time | 12-hour with Bengali AM/PM equivalents; stored UTC, displayed Asia/Dhaka |
| Calendar | Gregorian with Bangladesh public holidays **including moon-dependent dates** |
| Fiscal year | **July–June** |
| Address | Division → District → Upazila/Thana → Union/Ward → Postcode |
| Phone | +880 with Bangladesh mobile operator validation |
| National ID | 10-digit and 17-digit formats validated |
| Translation completeness | **100% of user-facing strings before any module is accepted** |
| Translation quality | Professionally translated and reviewed by a native speaker. **Machine translation is not acceptable for release.** |

### 9.9 Environmental & Device Support

| Category | Supported |
|---|---|
| Desktop browsers | Chrome, Edge, Firefox (latest two versions); Safari (latest two) |
| Minimum desktop resolution | **1366×768** — the common branch hardware |
| Mobile OS — technician, rider, auditor | Android 11+ (primary); iOS 15+ (secondary) |
| Mobile OS — customer | Android 9+; iOS 14+ |
| Minimum device specification (field apps) | 3 GB RAM, 32 GB storage, GPS, camera, 4G |
| Network | Functional on 3G; optimised for 4G; full offline where specified |
| Peripherals | Thermal receipt printers, label printers, barcode/QR scanners, biometric devices, signature capture, queue displays, kiosks |
| Printing | A4 and thermal receipt; **Bengali rendering verified on all supported printers** |

### 9.10 Testing Standards

| Level | Coverage | When |
|---|---|---|
| Unit | ≥ 80% of custom code; **100% of financial and tax calculations** | Every commit |
| Integration | All module-to-module contracts and all external integrations against sandboxes | CI |
| Contract | Every published API validated against its OpenAPI specification | CI |
| Event | Every producer/consumer pair tested for schema compatibility and idempotency | CI |
| End-to-end | Every critical business journey (15 defined below) | Nightly |
| Performance | Every NFR performance target, **at 1.5× expected peak** | Before each wave gate |
| Security | SAST, DAST, dependency scanning every build; penetration test annually | Continuous + annual |
| Accessibility | WCAG 2.1 AA automated scan plus manual audit per portal | Before each portal release |
| Localisation | Translation completeness, Bengali rendering, formatting, layout under text expansion | Before each wave gate |
| Offline | 24-hour offline operation with a scripted conflict scenario set | Before each mobile release |
| Data migration | Reconciliation and control totals on every load | Before every cutover |
| UAT | **Every P0 and P1 requirement**, executed by named business super-users | Before each wave gate |

**The 15 critical journeys covered by end-to-end tests:**

1. Book online → dispatch → field repair → invoice → pay → close → survey
2. Walk-in intake → workshop repair → estimate → approval → QC → handover → pay
3. Pick & drop collection → workshop → return delivery → invoice
4. Warranty job → claim creation → submission → approval → reimbursement → reconciliation
5. AMC sale → activation → preventive schedule → visit → renewal
6. MSP alert → ticket → remote resolution → SLA measurement → monthly service report
7. Marketplace order → seller quote → customer selection → job → review → commission → payout
8. Rental reservation → delivery → return → damage assessment → billing
9. Trade-in request → offer → intake → data wipe → refurbishment → grading → resale
10. E-waste collection → triage → destruction → recycling → disposal certificate
11. Data recovery case → custody → recovery → handover → purge certificate
12. Purchase requisition → PO → receipt → inspection → three-way match → payment
13. Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting
14. Complaint → non-conformance → root cause → CAPA → verification → closure
15. Month-end close → reconciliation → VAT return → management pack

---

## 10. SECURITY, DATA PROTECTION & REGULATORY COMPLIANCE

### 10.1 Regulatory Currency — Bangladesh Statutes

**This section corrects a material error in RFP v1.0**, which cited the Digital Security Act 2018
as a governing statute. That Act has been repealed twice. Every citation below carries a
verified-on date under governance rule DoD-17.

| Statute | Status | Verified |
|---|---|---|
| Digital Security Act 2018 | **Repealed** by the Cyber Security Act 2023 (13 September 2023) | 2026-08-12 |
| Cyber Security Act 2023 | **Repealed** by the Cyber Security Ordinance 2025 (21 May 2025) | 2026-08-12 |
| **Cyber Security Ordinance 2025** | **In force** | 2026-08-12 |
| Personal Data Protection Ordinance 2025 | Issued 6 November 2025; amended by Ordinance No. 23 of 2026 (5 February 2026); repealed on enactment of the Act | 2026-08-12 |
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **In force** — enacted April 2026. Complaint and enforcement mechanisms activate **~13 May 2027, inside Wave 4** | 2026-08-12 |
| ICT Act 2006 | In force | 2026-08-12 |
| VAT and Supplementary Duty Act 2012 | In force | 2026-08-12 |
| Bangladesh Labour Act 2006 (as amended) | In force | 2026-08-12 |
| Bangladesh Labour Rules 2015 | In force | 2026-08-12 |

**Contractual obligation.** Every statutory and standards citation in the delivered system,
documentation and training material must carry a verified-on date, and must be **re-verified at
each wave gate**. This obligation exists because the specification previously cited a statute
repealed twice, and a withdrawn NIST revision, with no currency-review control (risk RSK-035).

### 10.2 Personal Data Protection Act 2026 — Statutory Obligations

The regulator is the **National Data Management Authority**. These obligations are new since
RFP v1.0 and are **all P0**.

| ID | Requirement | Owning module |
|---|---|---|
| NFR-090 | Process personal data only on consent or a stated legitimate ground, **recorded per processing purpose** | M33 |
| NFR-091 | Consent must be **clear, explicit, specific and freely given**, with a heightened *specific consent* standard for sensitive personal data unless a legitimate ground applies | M33 |
| NFR-092 | Issue a **transparency notice** before or during processing, stating data categories, purposes, risks, retention periods, third-party transfers and the withdrawal procedure | M33 |
| NFR-093 | Support data-subject rights: **access and portability**; **rectification with controller notification within 30 days**; **erasure** on purpose cessation, consent withdrawal, unlawful processing or legal requirement; and **withdrawal of consent through a simplified procedure** | M33, M29 |
| NFR-094 | **Notify the National Data Management Authority** of any breach likely to cause significant damage, within the prescribed timeframe | M60, M29 |
| NFR-095 | Maintain processing records for a **minimum of five years** | M24, M29 |
| NFR-096 | **Appoint a Chief Data Officer** if the Company is classified a *significant* data fiduciary, with role, authority and reporting line defined | M60 |
| NFR-097 | Technical and organisational security measures proportionate to risk | M29 |
| NFR-098 | Treat a processor's processing as the controller's own; **flow equivalent obligations to every processor and sub-processor by contract** — this includes the successful respondent | M42, M60 |
| NFR-099 | **Restrict large-scale transfer of Sensitive Personally Identifiable Data** — government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information and criminal records — notify the Authority of cross-border transfers and disclose the safeguards applied | M29, M65 |

**Penalty exposure:** up to **BDT 25 lakh** for security failures or rights violations, and up to
**BDT 50 lakh** for significant data fiduciaries, with additional fines for repeated violations.
The amending ordinance introduces turnover-linked penalties. This exposure is registered as risk
**RSK-032, rated Critical**.

### 10.3 Data Residency — Split-Residency Architecture

> **This is the single most consequential architectural constraint in this RFP, and it changed
> after v1.0 was issued.** RFP v1.0 assumed a single Singapore region. That position conflicts
> with NFR-099.

| ID | Requirement | Pri |
|---|---|:--:|
| **NFR-086** | **Split-residency data architecture.** Sensitive Personally Identifiable Data as defined by the PDPA 2026 — NID, passport, TIN, biometric templates, and recovered customer data held under M06 — is stored in a **Bangladesh-resident data store**. The remainder of each record may be held in the regional store. **Records are joined by a resident key, never by duplicating the sensitive field.** | **P0** |
| NFR-086a | The data model must carry a **residency classification on every field**, and the platform must enforce it **at write time — not by convention** | **P0** |
| NFR-086b | Any cross-border transfer of a residency-classified field requires an Authority notification record and a documented safeguard **before the transfer executes** | **P0** |
| NFR-086c | Non-production environments **never** contain unmasked residency-classified data in any region | **P0** |

**Fields currently classified as residency-restricted:**

| Field | Entity | Owning module |
|---|---|---|
| National ID number | `fix.identity.document` | M33 |
| Passport number | `fix.identity.document` | M33 |
| TIN | `fix.party`, `hr.employee` | M33, M21 |
| Biometric attendance template | `fix.attendance.record` | M55 |
| Recovered customer data and its index | `fix.recovered.inventory` | M06 |
| Marketplace seller KYC documents | `fix.mp.seller.document` | M12 |
| Criminal record checks (where collected) | `fix.mp.seller.document` | M12 |

> **Open decision D-13, blocking Wave 1 architecture.** A **legal opinion on the split-residency
> design is required before the Wave 1 architecture is fixed** (dependency DEP-31). Respondents
> must: (a) state how their design isolates residency-classified fields; (b) identify a
> Bangladesh-resident data store meeting the availability targets in §9.2 (assumption ASM-21 —
> procurability is not yet proven); (c) price the latency and operational cost of the split; and
> (d) state their contingency if the legal opinion requires a broader field set to be resident.
> **Retrofitting residency into a live system is the most expensive class of rework in this
> programme.**

### 10.4 Core Compliance Requirements

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-021 | **Mushak 6.3 tax invoice** format compliance per the VAT and SD Act 2012 | P0 |
| NFR-100 | **Mushak 9.1 monthly VAT return filed by the 15th of the following month**, submitted through the NBR VAT Online portal (vat.gov.bd) | P0 |
| NFR-101 | **Input VAT credit claimable only against a valid, compliant Mushak 6.3 invoice; the system must block credit claims without one** | P0 |
| NFR-022 | Bangladesh NBR income tax computation compliance | P0 |
| NFR-023 | **ICT Act 2006 and Cyber Security Ordinance 2025 compliance** | P0 |
| NFR-024 | ISO 9001:2015 audit trail and documentation requirements | P0 |
| NFR-025 | ISO 27001 security control alignment | P1 |
| NFR-083 | Bangladesh Labour Act compliance in HR and payroll | P0 |
| NFR-084 | Bangladesh e-waste and environmental handling rules | P1 |
| NFR-085 | Consumer protection obligations on marketplace transactions | P0 |
| NFR-087 | Data-subject rights supportable within legal constraints | P1 |
| NFR-088 | Records retention per the statutory schedule, **enforced by the system** | P0 |
| NFR-089 | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | P2 |

### 10.5 Respondent Security Obligations

The successful respondent will be a **data processor** under the PDPA 2026 and is subject to
flow-down obligations under NFR-098. The following are contractual:

| # | Obligation |
|---|---|
| RSO-01 | ISO 27001 certification, or a documented, audited equivalent, at contract signature |
| RSO-02 | Named data protection point of contact; cooperation with the Company's Chief Data Officer |
| RSO-03 | No production personal data may leave the approved environments; **no developer access to unmasked production personal data without a logged, time-boxed, approved grant** |
| RSO-04 | Sub-processors declared, approved in writing, and bound by equivalent obligations |
| RSO-05 | Breach notification to the Company **within 24 hours** of becoming aware |
| RSO-06 | Background screening of all personnel with production or personal-data access |
| RSO-07 | Signed confidentiality undertakings from every individual working on the engagement |
| RSO-08 | Secure development lifecycle with SAST, DAST, dependency scanning and secret scanning in CI |
| RSO-09 | Annual independent penetration test of the delivered system, findings tracked to closure |
| RSO-10 | **Zero critical or high security findings** at each wave gate (DoD-15) |
| RSO-11 | Return or verified destruction of all Company data at termination, with certificates |

---

## 11. DATA MIGRATION & LEGACY CUTOVER

### 11.1 Source Domains and Volumes

| Data source | Description | Estimated volume | Wave | Pri |
|---|---|---|:--:|:--:|
| Customer data | Records from spreadsheets, phone records, website registrations | 100,000+ | W1 | P0 |
| Device registry | Device information, serial numbers, warranty details | 200,000+ | W1 | P0 |
| Branch & employee master | Locations, staff, org structure | 500+ employees, 51+ branches | W1 | P0 |
| Service history | Past service orders and repair records | 500,000+ | W2 | P1 |
| Inventory | Current stock levels across all locations | 10,000+ SKUs, all locations | W2 | P0 |
| Financial history | Accounting records, invoices, payments | 3+ years | W3 | P0 |
| Vendor master & open POs | Supplier and partner information | 200+ vendors | W3 | P1 |
| Contract data | Active AMC, RAMC, corporate contracts | 5,000+ | W4 | P0 |
| Open warranty claims | In-flight claims with brand partners | TBD | W4 | P0 |
| Employee records & certifications | HR records, technician profiles, certification status | 500+ | W5 | P0 |
| Open quality records | NCRs, CAPAs, audit findings | TBD | W5 | P1 |
| Document archive | Service reports, warranty documents, photos | Significant | W3–W5 | P2 |

### 11.2 Migration Requirements

| ID | Requirement | Pri |
|---|---|:--:|
| MIG-001 | Detailed migration plan with field-level source-to-target mapping, per wave | P0 |
| MIG-002 | **Data profiling before every load** — completeness, validity, duplication, staleness reported to the data owner | P0 |
| MIG-003 | Cleansing performed **in the source** where possible, with the business data owner accountable | P0 |
| MIG-004 | Validation rules and **reconciliation reports with control totals** on every load | P0 |
| MIG-005 | Trial migration into `staging` with business UAT before every cutover | P0 |
| MIG-006 | **Signed reconciliation** by the named data owner as a wave gate criterion | P0 |
| MIG-007 | Documented, rehearsed rollback plan for every cutover | P0 |
| MIG-008 | Migration tooling delivered to the Company, repeatable and re-runnable | P0 |
| MIG-009 | Incremental/delta migration during the parallel-run period | P1 |
| MIG-010 | Historical data migrated with **audit trail preservation** and original reference retention (FR-SRM-088 legacy order lookup) | P0 |
| MIG-011 | Bengali text conversion and encoding normalisation to UTF-8 | P1 |
| MIG-012 | An **archive area for uncleansable records**, retrievable but not transacted against | P1 |
| MIG-013 | Financial history reconciled **to the trial balance** before Gate 3 | P0 |
| MIG-014 | **Residency classification applied at migration**; no residency-restricted field lands in the regional store | P0 |
| MIG-015 | Personal data migrated only with a lawful basis recorded; **transparency notice obligations addressed for migrated data subjects** | P0 |

> **Assumption ASM-03 and risk RSK-014.** Existing customer and device data is assumed exportable
> at **≥ 80% quality**. If this proves false, migration effort increases materially and a manual
> cleansing programme is required. Respondents must state their assumptions, their profiling
> approach, and how they price the downside.

---
---

# PART C — HOW IT WILL BE DELIVERED

---

## 12. IMPLEMENTATION APPROACH — 9 WAVES OVER 36 MONTHS

### 12.1 Sequencing Logic

Four constraints determine the order:

| Constraint | Consequence |
|---|---|
| **Technical dependency** | Identity, integration and master data must exist before anything transacts |
| **Business criticality** | The v1.0 commitments (service, dispatch, inventory, finance, contracts, warranty) come first |
| **Data accumulation** | Machine learning cannot be built before there is data to learn from — hence AI in Waves 6–8, not Wave 2 |
| **Business absorption capacity** | 51+ branches and 500+ staff can absorb roughly **one major process change per quarter**. **UAT super-user availability, not developer capacity, is the binding constraint on this programme.** |

### 12.2 Wave Plan

```
Year 1                          Year 2                          Year 3
M1────M4────M8────M13───M18     M19──M22───M26───M30            M31──M34──M36
│ W1  │ W2  │ W3  │ W4  │       │ W5 │ W6  │ W7  │              │ W8  │ W9 │
│Found│Field│Money│Agree│       │Peo-│New  │Market              │Intel│Exp-│
│ation│ Ops │  &  │ments│       │ple │Asset│place               │ligen│an- │
│  &  │  &  │Move-│  &  │       │ &  │Busi-│  &  │              │ce & │sion│
│Servi│Inven│ment │Cont-│       │MSP │ness │Sett-│              │ ESG │    │
│ ce  │tory │     │act  │       │    │lines│lement              │     │    │
└─────┴─────┴─────┴─────┘       └────┴─────┴─────┘              └─────┴────┘
```

### 12.3 Wave Detail

#### Wave 1 — Foundation & Service Core (Months 1–4)

| | |
|---|---|
| **Modules** | M29 SEC · M28 IPF · M30 ADM · M33 CPM · M37 CAT · M07 CRM · M17 AST (registry) · M01 SRM (core) · M04 FRD |
| **Portals** | P03 Admin Operations |
| **Team** | 7 FTE (2 Odoo, 1 DevOps, 1 BA, 1 QA, 1 Architect, 0.5 PM, 0.5 Change) |
| **Requirements** | ~142 |
| **Geography** | Dhaka HQ + 5 pilot service centres |

**Delivers:** identity provider, SSO, role framework, audit trail · API gateway, event platform,
workflow engine, integration framework · entity, branch, zone and calendar configuration, Bengali
localisation base · **party master with PDPA consent and transparency notices** · product and
service catalogue · device and asset registry with brand and model masters · service order and work
order core with lifecycle, SLA, diagnosis, estimate and QC · front desk token queue, intake,
handover, cash drawer, shift control · SMS, WhatsApp and email notification delivery.

**Also in Wave 1 scope (remediation carried from the documentation audits):** completion of the
role register to R46 with R60 eliminated · registration of SOD-13…SOD-30 · the programme KPI
register with colliding identifiers reassigned · the unified CD register as sole allocator · the
retirement record for 28 unused Category A requirement IDs. See §20.

**Data migration:** customers, devices, branch and employee master.

#### Wave 2 — Field Operations & Inventory (Months 5–8)

| | |
|---|---|
| **Modules** | M02 FSM · M31 WSR · M15 INV · M10 LOY · M64 MDM · M01 SRM (complete) · M17 AST (complete) |
| **Portals** | P01 Customer Portal · P02 Technician App |
| **Team** | 11.5 FTE (+2 Flutter, +1 Odoo, +1 frontend) |
| **Requirements** | ~178 |
| **Geography** | All Dhaka centres (~20) |

**Delivers:** dispatch engine, dispatch board, zones, route optimisation · GPS tracking, live
operations map, customer tracking page · **technician mobile app with full offline capability** ·
workshop bench management and repair-level routing · multi-location inventory, van stock, barcode
operations, replenishment alerts · Privilege programme, points, vouchers, campaigns · customer
portal booking, tracking, history, approvals · **the M22 eligibility stub in M02**.

#### Wave 3 — Money, Movement & Documents (Months 9–13)

| | |
|---|---|
| **Modules** | M19 FIN · M20 ARB · M52 APE · M50 TRE · M11 PRC · M36 QTE · M03 LOG · M16 PRO · M41 WMS · M24 DMS · M63 BPA |
| **Portals** | P05 Vendor Portal · P09 Logistics & Rider App |
| **Team** | 16 FTE |
| **Requirements** | ~156 |
| **Geography** | All Dhaka + Chittagong |

**Delivers:** general ledger, AR, AP, banking, cash control · Mushak VAT invoicing, TDS, VAT
sub-ledgers · payment gateway integration with auto-reconciliation · price books, rate cards,
quotation engine, discount governance · logistics: consignments, chain of custody, pick & drop,
courier integration, rider app · procurement: requisition, PO, receipt, three-way match, vendor
portal · warehouse management · document management, templates, e-signature, retention · the
platform workflow engine.

#### Wave 4 — Agreements, Billing & Contact (Months 14–18) — **v1.0 scope complete**

| | |
|---|---|
| **Modules** | M08 CTR · M09 WTY · M39 SUB · M51 TAX · M53 REV (core) · M27 CCE · M32 CAI · M34 CXM · M25 BID (core) · M62 DAT (core) · M42 SRM2 |
| **Portals** | P04 Corporate B2B · P06 Analytics · P08 Brand Partner · P10 Contact Centre |
| **Team** | 17 FTE |
| **Requirements** | ~189 |
| **Geography** | All active service centres |

**Delivers:** contract engine across all 14 product families · warranty entitlement, protection
products, brand claim automation for 17+ partners · subscription and consolidated B2B billing,
dunning, refunds · Bangladesh tax compliance and NBR e-VAT filing · omnichannel contact centre with
hotline integration and the AI assistant · executive, branch, technician, finance and warranty
dashboards · corporate B2B portal · brand partner portal.

> **PDPA enforcement activates inside this wave (~13 May 2027).** Data-subject rights, transparency
> notices, breach notification and the Chief Data Officer determination must be operational by
> Gate 4 regardless of wave content.

#### Wave 5 — People, Quality & Managed Services (Months 19–22)

| | |
|---|---|
| **Modules** | M21 HCM · M55 WFM · M56 PAY · M57 PIC · M22 LMS · M23 QMS · M05 RMS · M45 EAM · M46 FLT · M49 FXA |
| **Portals** | P11 Field Auditor App |
| **Team** | 17 FTE |
| **Requirements** | ~148 |
| **Geography** | **All 51+ service centres** |

**Delivers:** HR, attendance, leave, roster, payroll with Bangladesh tax and BEFTN · technician
performance capture and incentive calculation · **competency framework with hard dispatch
enforcement** · learning management with Bengali content · quality management: NCR, CAPA,
complaints, audits, ISO evidence · managed services: remote support, monitoring, alerting, MSP
ticketing, SLA reporting · enterprise asset and test equipment with calibration · fleet · fixed
assets.

#### Wave 6 — New Asset Businesses (Months 23–26)

| | |
|---|---|
| **Modules** | M13 RNT · M14 TRF · M06 DTS · M43 DPL · M44 ITC · M54 FPA · M58 TAO · M59 HSE · M60 GRC · M61 KMS · M66 ITS · M26 AIM (dispatch and forecasting models) |
| **Portals** | P01 native mobile applications |
| **Team** | 19 FTE (+1 AI/ML, +1 data engineer) |
| **Requirements** | ~134 |

**Delivers:** rental asset pool, reservations, agreements, tariffs, deposits, condition reports,
damages · trade-in, refurbishment, grading, resale, provenance · data services: recovery cases,
custody controls, backup subscriptions, certified destruction · demand planning · import and landed
cost · costing and FP&A · talent acquisition, health & safety, GRC, knowledge management · ML
services: dispatch assignment scoring, duration prediction, demand forecasting.

#### Wave 7 — Marketplace & Settlement (Months 27–30)

| | |
|---|---|
| **Modules** | M38 ECM · M12 MKP · M40 PCM · M11 PRC (dynamic pricing) · M53 REV (marketplace settlement) · M47 FAC · M67 PPM |
| **Portals** | P07 Marketplace Seller · P12 Partner & Referral |
| **Team** | 19 FTE |
| **Requirements** | ~121 |

**Delivers:** e-commerce storefront · marketplace: seller onboarding with KYC, listings, job
broadcast, bidding, ratings, disputes · commission calculation, seller wallets, payout runs,
escrow · paid boost and advertising · dynamic pricing with guard rails · partner and referral
portal with commission statements.

#### Wave 8 — Intelligence & Sustainability (Months 31–34)

| | |
|---|---|
| **Modules** | M62 DAT (warehouse) · M25 BID (full) · M26 AIM (predictive, pricing, quality models) · M48 IOT · M18 ESG |
| **Team** | 16 FTE |
| **Requirements** | ~79 |

**Delivers:** analytical warehouse, semantic layer, governed self-service · telemetry ingestion and
asset health scoring · predictive maintenance, churn, quality-risk and pricing models · Bengali
conversational and document AI at full scope · e-waste collection, recycling, disposal
certification, ESG reporting.

#### Wave 9 — Expansion Readiness (Months 35–36)

| | |
|---|---|
| **Modules** | M65 GLO — multi-entity, country packs |
| **Team** | 10 FTE |
| **Requirements** | ~33 |

**Delivers:** multi-entity accounting and consolidation · country pack framework with Bangladesh as
reference · entity onboarding runbook · multi-currency and FX at full scope · international payment
and shipping integration · performance and scale hardening.

> **Wave capacity warning (audit finding M-09).** Wave capacity has not been validated against the
> restated effort of 1,513 PW. Wave 4 at ~230 PW against a 17-FTE, ~18-week wave gives roughly 306
> available person-weeks at 100% capacity, or ~245 at 80% — a fit with almost no contingency.
> Waves 3 and 6 are similarly tight. **Respondents must produce their own capacity plan and state
> explicitly whether they believe the 36-month, 9-wave shape is achievable at the measured effort.
> A respondent who simply accepts the published plan without their own capacity analysis will be
> scored down.**

### 12.4 Wave Gate Acceptance Criteria

Each gate is a formal Go/No-Go with the Steering Committee. **All criteria must be met**; partial
passes are recorded as conditional with a dated remediation plan. Milestone payments are tied to
gate passage (§16.4).

**Gate 1 — Foundation (Month 4)**

| # | Criterion | Evidence |
|---|---|---|
| G1-01 | Service orders created from all live channels at pilot sites | Demonstration + transaction log |
| G1-02 | Full service order lifecycle operating end to end | Demonstration |
| G1-03 | **Walk-in intake completed in under 3 minutes by branch staff** | Timed observation, 20 samples |
| G1-04 | SLA clocks and escalations firing correctly | Test evidence |
| G1-05 | Customer and device data migrated and reconciled | **Signed** reconciliation |
| G1-06 | SSO and role framework operating for all delivered roles | Security test report |
| G1-07 | Audit trail complete for all delivered objects | Audit sample review |
| G1-08 | **100% Bengali translation on delivered screens** | Translation coverage report |
| G1-09 | **Zero critical or high security findings** | Security review |
| G1-10 | Performance targets met for delivered screens | Load test report at 1.5× peak |
| G1-11 | UAT signed off by named super-users | Signed UAT record |
| G1-12 | Runbooks and training materials delivered | Document register |
| G1-13 | PDPA consent, transparency notice and residency classification operating | Compliance review |

**Gate 2 — Field Operations (Month 8)**

| # | Criterion |
|---|---|
| G2-01 | Technician app in daily use by **100%** of Dhaka technicians |
| G2-02 | **24-hour offline operation demonstrated with zero data loss** |
| G2-03 | Sync completing within 30 seconds on 3G after 24 hours offline |
| G2-04 | Route optimisation reducing measured travel time by **≥ 15%** |
| G2-05 | GPS tracking and customer tracking page live |
| G2-06 | Inventory accuracy **≥ 95%** at migrated locations, verified by count |
| G2-07 | Van stock reconciling daily with variance < 2% |
| G2-08 | Online booking rate **≥ 60%** at pilot sites |
| G2-09 | **Paper service forms withdrawn in Dhaka** |
| G2-10 | Privilege benefits applying automatically and correctly |

**Gate 3 — Money & Movement (Month 13)**

| # | Criterion |
|---|---|
| G3-01 | **100% of invoices generated automatically from closed jobs** |
| G3-02 | Payment auto-matching ≥ 90% |
| G3-03 | bKash, Nagad and card payments live and reconciling |
| G3-04 | **Mushak invoices accepted with zero NBR exceptions** |
| G3-05 | First full month-end closed within 5 days |
| G3-06 | Three-way matching blocking unmatched vendor invoices |
| G3-07 | Pick & drop operating with unbroken chain of custody, **zero exceptions** |
| G3-08 | Financial history migrated and **reconciled to the trial balance** |
| G3-09 | Branch cash reconciling daily across all live branches |

**Gate 4 — Agreements & Contact (Month 18) — v1.0 scope complete**

| # | Criterion |
|---|---|
| G4-01 | Warranty claims auto-created within 24 h and submitted within 72 h |
| G4-02 | First-submission approval rate ≥ 90% |
| G4-03 | Contract engine operating all live product families |
| G4-04 | Preventive maintenance work generating automatically on schedule |
| G4-05 | 10+ corporate clients transacting on the B2B portal |
| G4-06 | Hotline conversations captured in the system of record |
| G4-07 | AI assistant resolving ≥ 40% of first contacts |
| G4-08 | Consolidated B2B invoicing operating correctly |
| G4-09 | Executive and branch dashboards in weekly management use |
| G4-10 | **Every v1.0 BRD requirement demonstrated as delivered or formally superseded** |
| G4-11 | **PDPA data-subject rights, breach notification and CDO determination operational** |

**Gate 5 — People, Quality & MSP (Month 22)**

| # | Criterion |
|---|---|
| G5-01 | **First payroll run processed, validated and paid with zero errors** |
| G5-02 | BEFTN file accepted by the bank without rework |
| G5-03 | **Zero uncertified technicians assignable to brand warranty work** |
| G5-04 | ISO 9001 internal audit executed entirely in the system |
| G5-05 | First MSP clients live with monitored estates and SLA reporting |
| G5-06 | **All 51+ service centres operating on the platform** |
| G5-07 | Attendance capture ≥ 98% complete across all branches |

**Gate 6 — New Asset Businesses (Month 26)**

| # | Criterion |
|---|---|
| G6-01 | Rental transacting with full condition, deposit and damage control |
| G6-02 | **Zero refurbished units released without a data destruction certificate** |
| G6-03 | Data-services chain of custody with **zero exceptions** |
| G6-04 | Automatic dispatch assignment ≥ 50% with ≥ 88% dispatcher agreement |
| G6-05 | Parts demand forecast accuracy within target |
| G6-06 | Customer native mobile apps published and adopted |

**Gate 7 — Marketplace (Month 30)**

| # | Criterion |
|---|---|
| G7-01 | 200+ approved sellers transacting |
| G7-02 | **Payout accuracy 100% with zero unexplained variance** |
| G7-03 | Marketplace jobs meeting the same quality and evidence standards as owned jobs |
| G7-04 | Dispute rate below target with all disputes resolved within SLA |
| G7-05 | **VAT treatment validated by external tax advice** |
| G7-06 | Dynamic pricing operating within guard rails with a complete decision audit |

**Gate 8 — Intelligence & Sustainability (Month 34)**

| # | Criterion |
|---|---|
| G8-01 | All management reporting served from the warehouse; **zero manual packs** |
| G8-02 | Predictive maintenance precision ≥ 70% on the pilot estate |
| G8-03 | **Overall automation of routine operational work ≥ 85%** |
| G8-04 | E-waste chain fully certified with zero uncertified disposals |
| G8-05 | Every production model has a current model card and drift monitoring |

**Gate 9 — Expansion Readiness (Month 36)**

| # | Criterion |
|---|---|
| G9-01 | **A test entity in a second country stood up in ≤ 12 weeks using configuration only** |
| G9-02 | Consolidated multi-entity reporting validated |
| G9-03 | Full-scale load test passed at 1.5× projected peak |
| G9-04 | All programme documentation handed over and accepted |
| G9-05 | Support model transitioned to steady state |

### 12.5 Module Definition of Done

No module is accepted at a wave gate until every item is true. This list is contractually binding.

| # | Criterion |
|---|---|
| DoD-01 | Registered with ID, code, category, priority, wave and owners **before** its specification was written |
| DoD-02 | All P0 and P1 requirements implemented and demonstrated |
| DoD-03 | Unit test coverage ≥ 80%; **100% on financial and tax calculations** |
| DoD-04 | Business rules enforced at the model layer, verified by **negative tests through both UI and API** |
| DoD-05 | Domain events published through the outbox and registered in the event catalogue |
| DoD-06 | APIs documented in OpenAPI 3.1 and published |
| DoD-07 | Access control, record rules and field permissions defined and **negative-tested for every applicable role** |
| DoD-08 | **Bengali translation complete for all user-facing strings** |
| DoD-09 | KPIs instrumented with allocated `KPI-nnn` identifiers and visible in M25 |
| DoD-10 | Data migration mapping defined and dry-run executed where legacy data exists |
| DoD-11 | Operational runbook written |
| DoD-12 | Training material produced in **Bengali and English** for every affected role |
| DoD-13 | UAT executed and **signed by named business super-users** |
| DoD-14 | Performance tested against applicable NFRs |
| DoD-15 | Security review completed with **zero open high or critical findings** |
| DoD-16 | Rollback plan documented and rehearsed |
| DoD-17 | **Regulatory citations verified current, with a verified-on date** |

### 12.6 Delivery Method & Rollout

| Aspect | Approach |
|---|---|
| Cadence | Two-week sprints; five to ten sprints per wave |
| Ceremonies | Sprint planning, daily stand-up, **sprint review with business owners**, retrospective |
| Definition of ready | Requirement has acceptance criteria, a business owner and no unresolved dependency |
| Definition of done | All 17 criteria in §12.5 |
| Demo discipline | **Every sprint review demonstrates working software to the business owner, never slides** |
| Wave gate | Formal Go/No-Go with the Steering Committee against published criteria |
| Hypercare | **Four weeks of elevated support after every wave go-live** |
| Release cadence | Fortnightly to staging; monthly to production within a wave; hotfixes as needed |

**Geographic sequence:** pilot (Dhaka HQ + 5 centres, W1) → all Dhaka (~20 centres, W2) → major
cities (+Chittagong, Sylhet, Khulna, Rajshahi, W3) → national (all 51+, W4–W5) → new capability to
all centres as each business line goes live (W6–W8).

**Rollout pattern per location:**

```
T−4 weeks   Site readiness assessment: connectivity, hardware, staffing
T−3 weeks   Data preparation and validation with the branch
T−2 weeks   Branch champion training (train the trainer)
T−1 week    All-staff training in Bengali; system access provisioned
T−3 days    Data cutover; parallel run begins
T−0         Go-live with on-site support
T+2 weeks   Parallel run ends; legacy process withdrawn
T+4 weeks   Hypercare ends; adoption review
```

**Parallel running:**

| Process | Parallel period | Reason |
|---|---|---|
| Service orders | 2 weeks | Operational safety |
| Inventory | 2 weeks + full count at cutover | Valuation accuracy |
| Finance | **1 full month-end** | Reconciliation confidence |
| Payroll | **2 pay cycles** | Zero tolerance for pay errors |
| Warranty claims | 1 month | Brand relationship protection |

### 12.7 Team Model

**Indicative composition by wave (full-time equivalents):**

| Role | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Programme Manager | 0.5 | 0.5 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Solution Architect | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Senior Odoo Developer | 2 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 2 |
| Flutter / Mobile Developer | — | 2 | 2 | 1 | 2 | 3 | 2 | 1 | — |
| Frontend Developer (Next.js) | — | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 |
| DevOps / Platform Engineer | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 |
| Data / BI Engineer | — | — | — | 1 | 1 | 1 | 1 | 2 | 1 |
| AI / ML Engineer | — | — | — | — | — | 1 | 1 | 1 | — |
| Business Analyst | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 |
| QA Engineer | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 |
| Change & Training Lead | 0.5 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| **Total** | **7** | **11.5** | **16** | **17** | **17** | **19** | **19** | **16** | **10** |

Respondents must propose their own staffing plan. The above is the Company's model and is **not
prescriptive**, but a materially smaller team must be justified against the measured 1,513 PW.

**Business-side commitment (the Company's obligation):**

| Role | Commitment | Waves |
|---|---|---|
| Executive Sponsor (CEO) | 4 hours/month steering | All |
| Module Business Owners | 20% of time | Waves affecting their module |
| Super-Users (2–3 per module) | 30% during UAT, 10% otherwise | Waves affecting their module |
| Branch Champions (1 per branch) | 4 hours/week during rollout | W1–W5 |
| Data Owners | 20% during migration | W1–W5 |

> **This is the binding constraint on the programme (risk RSK-001, rated Critical).** If business
> availability is not protected, waves will slip regardless of development capacity. The Company
> accepts that a wave gate slips rather than allowing development to run ahead into unaccepted
> work.

### 12.8 Contingency

| Scenario | Response |
|---|---|
| Wave slips ≤ 4 weeks | Absorb in the next wave's buffer; no dependency change |
| Wave slips > 4 weeks | Steering Committee decides: descope P2/P3, extend, or reallocate |
| Business UAT capacity unavailable | Wave gate slips; **development does not run ahead into unaccepted work** |
| Key integration blocked externally | Deliver the module with the documented manual fallback; integrate later |
| Adoption failure at a location | Pause rollout, diagnose, remediate, re-pilot before continuing |
| Budget pressure | **Defer W8 and W9 first; W6 and W7 are the revenue-generating waves** |
| Team attrition | Two-person minimum knowledge coverage on every module; documentation as a definition-of-done item |

**What cannot be descoped under any circumstances:**

| Item | Reason |
|---|---|
| M29 Identity & Security | Everything depends on it |
| M28 Integration platform | Everything depends on it |
| M01 Service & M02 Field | The business itself |
| M19 / M51 Finance & Bangladesh compliance | Legal obligation |
| M09 Warranty claims | The largest single revenue-recovery benefit |
| M33 PDPA obligations | Statutory, with penalty exposure |
| Bengali localisation | Field adoption fails without it |
| Offline capability | Field operation fails without it |
| Audit trail and data protection | Legal and ISO obligation |

---

## 13. TRAINING, CHANGE MANAGEMENT & ADOPTION

### 13.1 Training Requirements

| ID | Requirement | Pri |
|---|---|:--:|
| TRN-001 | Role-based training programmes for each of the 46 roles | P0 |
| TRN-002 | Train-the-Trainer programme for 1000FiX internal champions, **one per branch** | P0 |
| TRN-003 | **Training delivered in Bengali** for field staff and service centre employees | P0 |
| TRN-004 | Hands-on training in the dedicated `training` environment with curated scenario data | P0 |
| TRN-005 | Video-based training library for on-demand learning, in Bengali and English | P0 |
| TRN-006 | User manuals and quick-reference cards in Bengali and English | P0 |
| TRN-007 | In-application guided tours and contextual help | P1 |
| TRN-008 | Training effectiveness assessment (pre/post evaluation) | P1 |
| TRN-009 | Refresher training each wave, plus quarterly for the first year post-go-live | P1 |
| TRN-010 | Administrator training on configuration, customisation, extension and maintenance | P0 |
| TRN-011 | **Developer knowledge transfer** enabling the Company to maintain and extend the system independently | P0 |
| TRN-012 | External party training: marketplace sellers, brand partners, vendors, corporate portal users | P1 |

### 13.2 Training Volumes

| User group | Users | Duration | Format |
|---|---:|---|---|
| Executive / management | 15–25 | 1 day | In-person workshop |
| Service operations | 30–50 | 3–5 days | Classroom + hands-on |
| **Field technicians** | **200–400** | 2–3 days per batch of 30 | Mobile-focused, hands-on, **Bengali** |
| Service centre staff | 150–250 | 3–5 days per batch of 30 | Classroom + hands-on, **Bengali** |
| Logistics & riders | 60–175 | 1–2 days per batch | Mobile-focused, **Bengali** |
| Customer service / contact centre | 34–70 | 2–3 days | Classroom + hands-on |
| Finance | 15–30 | 3–5 days | Classroom + hands-on |
| HR | 10–15 | 2–3 days | Classroom + hands-on |
| Quality & audit | 5–15 | 2–3 days | Classroom + mobile |
| System administrators | 5–10 | 5–10 days | Technical deep-dive |
| **Company developers (knowledge transfer)** | 3–6 | **20+ days across the programme** | Pair working + technical deep-dive |
| Marketplace sellers | 500–2,000 | Self-service + onboarding | Digital, **Bengali** |
| Corporate portal users | 500–2,000 | Account-manager-led | Digital + assisted |

### 13.3 Change Management

| ID | Requirement | Pri |
|---|---|:--:|
| CHM-001 | Change management strategy and communication plan per wave | P0 |
| CHM-002 | Stakeholder map maintained and reviewed each wave, with **resistance actively tracked** | P0 |
| CHM-003 | Champion network — one trained champion per branch, monthly champion forum | P0 |
| CHM-004 | Monthly all-staff update; wave-specific briefings; visible executive sponsorship | P0 |
| CHM-005 | **Weekly adoption measurement by role and branch**, with intervention where adoption lags | P0 |
| CHM-006 | Floor-walkers during go-live; dedicated internal support channel; escalation path | P0 |
| CHM-007 | Feedback collection during and after each rollout, with visible actions | P0 |
| CHM-008 | Recognition programme for early adopters and champions | P1 |

### 13.4 Adoption Risk by Group

| Group | Risk | Mitigation the respondent must deliver |
|---|---|---|
| **Field technicians** | **Critical** — app rejection collapses the field model | Bengali-first, extremely simple UX, field pilot with respected senior technicians before rollout, device provision, **incentive visibility as an immediate personal benefit**, champion network |
| Branch counter staff | High — highest transaction volume | **Speed as the explicit design goal** with measured intake time; champion-led training; involve resistors in design and UAT |
| Finance staff | Medium — process change and control tightening | Early involvement in design; parallel running; audit-trail benefit emphasised |
| Branch managers | Medium — visibility cuts both ways | Position dashboards as their tool, not surveillance; involve in KPI design |
| Marketplace sellers | High — external, low switching cost | Simple onboarding, **fast payouts**, transparent scoring |
| Corporate clients | Medium | Account-manager-led onboarding; demonstrable time savings |

---

## 14. SUPPORT, MAINTENANCE, HYPERCARE & WARRANTY

### 14.1 Hypercare

| ID | Requirement | Pri |
|---|---|:--:|
| SUP-001 | **Four weeks of hypercare after every wave go-live** — elevated staffing, daily triage, on-site presence at pilot and major sites | P0 |
| SUP-002 | Named hypercare lead per wave with a published escalation path | P0 |
| SUP-003 | Daily defect and adoption reporting during hypercare | P0 |
| SUP-004 | Exit criteria from hypercare agreed with the Company before it ends | P0 |

### 14.2 Steady-State Support

| ID | Requirement | Pri |
|---|---|:--:|
| SUP-005 | Dedicated support team covering Bangladesh business hours (**09:00–22:00 BST, Sunday–Thursday**) | P0 |
| SUP-006 | **24/7 support for system-down and severity-1 scenarios** (managed services clients require it) | P0 |
| SUP-007 | Ticketing system for issue logging, tracking and resolution, with Company visibility | P0 |
| SUP-008 | Resolution SLAs: **Critical 4 h · High 8 h · Medium 24 h · Low 72 h** | P0 |
| SUP-009 | Dedicated account manager | P0 |
| SUP-010 | **Bengali-speaking support staff** | P0 |
| SUP-011 | Quarterly service reviews with improvement recommendations | P1 |
| SUP-012 | On-site support availability when required | P1 |
| SUP-013 | Root cause analysis on every Critical and High incident, delivered within 5 working days | P0 |

### 14.3 System Maintenance

| ID | Requirement | Pri |
|---|---|:--:|
| SUP-014 | Regular updates and patches, minimum quarterly | P0 |
| SUP-015 | **Security patches within 48 hours** of critical vulnerability disclosure | P0 |
| SUP-016 | Zero-downtime deployment for planned changes | P1 |
| SUP-017 | Planned maintenance communicated 72 hours in advance, outside 08:00–23:00 BST, ≤ 4 h/month | P0 |
| SUP-018 | Automated health monitoring with proactive alerting | P0 |
| SUP-019 | Regular database optimisation and performance tuning | P0 |
| SUP-020 | **Backup verification weekly; DR failover exercised twice yearly** with documented results | P0 |
| SUP-021 | Odoo 19.x patch currency maintained; a major-version upgrade is a separate engagement | P0 |
| SUP-022 | OCA module currency maintained; upstream contribution of migrations | P0 |
| SUP-023 | Annual licence register review across all L1–L6 components | P0 |
| SUP-024 | **Annual regulatory currency review** of every statutory citation embedded in the system | P0 |

### 14.4 Warranty & Guarantees

| ID | Requirement | Pri |
|---|---|:--:|
| SUP-025 | **Minimum 12-month post-go-live warranty per wave** for defect correction at no additional cost | P0 |
| SUP-026 | Performance guarantee: the system meets all agreed NFR benchmarks throughout the warranty | P0 |
| SUP-027 | Data integrity guarantee during migration and operation | P0 |
| SUP-028 | **Source code escrow** where any component is proprietary to the respondent | P0 |
| SUP-029 | Knowledge transfer sufficient for the Company to maintain and extend independently, verified by a practical assessment at Gate 9 | P0 |
| SUP-030 | Transition assistance of no less than 90 days at contract end, at agreed rates | P0 |

---
---

# PART D — COMMERCIAL & PROCUREMENT

---

## 15. RESPONDENT QUALIFICATION REQUIREMENTS

### 15.1 Mandatory Pre-Qualification (Pass / Fail)

A submission failing any of the following is **eliminated at Stage 1 regardless of overall
score**. Evidence must be attached.

| ID | Mandatory requirement | Evidence required |
|---|---|---|
| **MQ-01** | Legally registered entity, trading for **≥ 5 years**, with audited financial statements for the last 3 fiscal years | Registration certificate, audited accounts |
| **MQ-02** | **≥ 3 completed ERP implementations of ≥ 500 functional requirements** in the last 5 years, at least one on the proposed platform | Reference projects with contactable clients |
| **MQ-03** | Demonstrable **Odoo delivery capability** — minimum 5 developers with production Odoo experience, and at least one completed Odoo v17+ implementation *(primary track only)* | CVs, project evidence, OCA contribution history |
| **MQ-04** | **Bengali language capability** — either Bengali-speaking team members or a named local implementation partner under contract | Team CVs, partner agreement |
| **MQ-05** | **ISO 27001 certification or an audited equivalent**, current at submission | Certificate |
| **MQ-06** | Capacity to field a **peak team of 19 FTE** without displacing another committed engagement | Resource plan, current commitments statement |
| **MQ-07** | Mobile application delivery capability — at least one production **offline-first** field application | Project evidence, app store listing |
| **MQ-08** | Acceptance that **all source code, configuration and documentation is the property of 1000FiX** and is delivered continuously to a Company-controlled repository | Signed acknowledgement |
| **MQ-09** | Acceptance of **milestone-based payment tied to wave gate passage** | Signed acknowledgement |
| **MQ-10** | No conflict of interest; no debarment or litigation that would impair performance | Declaration |
| **MQ-11** | Proposal validity of **180 days** from the submission deadline | Signed cover letter |
| **MQ-12** | Complete **Appendix A requirement response at requirement level** for all requirements in Annex 1 | Completed workbook |

### 15.2 Company Profile Information Required

| # | Requirement |
|---|---|
| VQ-01 | Legal name, registration, incorporation details, ownership structure |
| VQ-02 | Year established; years in ERP implementation |
| VQ-03 | Company size: total employees, ERP consultants, developers, QA, support staff |
| VQ-04 | Office locations, especially South Asia and Bangladesh presence |
| VQ-05 | Annual revenue for the last 3 fiscal years |
| VQ-06 | Financial stability documentation |
| VQ-07 | Quality and security certifications: ISO 9001, ISO 27001, CMMI or equivalent |
| VQ-08 | Delivery methodology and its documentation |
| VQ-09 | Open-source contribution record, particularly OCA |
| VQ-10 | Insurance: professional indemnity, cyber liability — cover levels |

### 15.3 Relevant Experience

| # | Requirement |
|---|---|
| VQ-11 | Number and scale of ERP implementations completed in the last 5 years |
| VQ-12 | **Field service management** implementations — minimum 3 references |
| VQ-13 | **Multi-location service business** implementations — minimum 3 references |
| VQ-14 | **Bangladesh or South Asia** delivery experience — strongly preferred |
| VQ-15 | After-sales service / warranty management domain experience |
| VQ-16 | Marketplace, commission and settlement platform experience |
| VQ-17 | Managed services / RMM / PSA platform experience |
| VQ-18 | Payroll and statutory compliance in a regulated jurisdiction |
| VQ-19 | Data warehouse and ML delivery in production |
| VQ-20 | Bengali localisation experience |
| VQ-21 | Case studies with **measurable, verifiable business outcomes** |
| VQ-22 | Any implementation that failed, was terminated early or was materially re-baselined in the last 5 years — with an honest account of why. **Non-disclosure discovered at reference check is grounds for elimination.** |

### 15.4 Proposed Team

| # | Requirement |
|---|---|
| VQ-23 | Programme Manager — PMP/PRINCE2 certified, 10+ years, named and committed |
| VQ-24 | Solution Architect — 10+ years ERP architecture, named and committed |
| VQ-25 | Odoo technical lead with demonstrable v17+ production experience |
| VQ-26 | Functional consultants with field service / after-sales domain expertise |
| VQ-27 | Mobile lead with offline-first production experience |
| VQ-28 | Frontend lead with Next.js 15 / React 19 production experience |
| VQ-29 | DevOps/platform engineer with Kubernetes, observability and multi-environment experience |
| VQ-30 | Data/BI engineer with warehouse and semantic-layer experience |
| VQ-31 | Data migration specialist |
| VQ-32 | Change management and training lead |
| VQ-33 | Security lead accountable for RSO-01…RSO-11 |
| VQ-34 | Bengali-speaking team members or a named local implementation partner |
| VQ-35 | **CVs of all key personnel**, with the percentage of their time committed to this engagement |
| VQ-36 | **Key personnel lock-in**: named key personnel may not be substituted without Company approval; substitution proposals must be of equal or better calibre |

### 15.5 References

| # | Requirement |
|---|---|
| VQ-37 | Minimum **3 client references** from field service, after-sales or multi-location service industries |
| VQ-38 | Minimum **2 client references** from South Asia |
| VQ-39 | At least **1 reference for a programme of ≥ 24 months' duration** |
| VQ-40 | For each: company, contact person, project scope, duration, value band, outcome, current status |
| VQ-41 | Written permission for 1000FiX to contact references directly and without the respondent present |
| VQ-42 | Willingness to host a **site visit** to at least one reference client |

---

## 16. COMMERCIAL STRUCTURE & PRICING RESPONSE

### 16.1 Indicative Budget Envelope

The indicative envelope for this programme is **USD 690,000 – 1,150,000 total cost of ownership
over three years**.

**This figure has been restated and the Company is disclosing why.** The approved business case
modelled implementation against **834 person-weeks across 30 modules**. Direct enumeration of the
completed specifications returns **1,513 person-weeks across 67 modules** — approximately **1.8×
the effort of the approved plan**. At the same unit rates, implementation and custom development
moves from $290K–470K to approximately **$525K–855K**, and the three-year TCO from $455K–780K to
approximately **$690K–1,150K**.

| Category | Previously modelled (3-yr) | **Restated (3-yr)** |
|---|---|---|
| Software licensing (L6 only; ERP core is $0) | $0–36K | $0–36K |
| Implementation & custom development | $290K–470K | **$525K–855K** |
| Infrastructure / hosting | $52K–96K | $52K–96K |
| Third-party APIs | $41K–95K | $41K–95K |
| Training & change management | $22K–43K | $35K–65K |
| Support & maintenance (Yr 2–3) | $50K–110K | $60K–130K |
| *Component sum* | *$405K–750K* | *$713K–1,277K* |
| **HEADLINE 3-YEAR TCO** | **$455K–780K** | **$690K–1,150K** |

> **Why the headline differs from the component sum.** The headline range is the restated figure
> from the Company's source register, derived by applying measured effort to the approved unit
> rates. The component sum is wider at both ends because **the lower bound assumes every line lands
> at its best case simultaneously, and the upper bound assumes every line lands at its worst case
> simultaneously — neither is likely.** The Company's financial model carries the same caveat.
> **Respondents should price the component lines and expect the outturn to fall inside the headline
> range.** A bid whose total sits outside the headline range must justify the variance under §16.1.

> **Decision D-14 is open.** The Steering Committee has not yet decided whether to fund the
> restated figure, phase it across more waves, or cut scope. Respondents should be aware that
> **scope reduction is a live possibility** and should structure their pricing so that Waves 8 and
> 9 — and, if necessary, Category D, F, I or J modules — can be removed cleanly without stranding
> cost. The Company reserves the right to award a reduced scope.

Respondents proposing outside the envelope must justify the variance explicitly. **A bid that is
materially below the envelope will be scrutinised for scope understanding, not rewarded for
price.**

### 16.2 Pricing Response Structure

All pricing in **USD**, exclusive of Bangladesh VAT, with the VAT treatment stated separately.
Where any component is priced in BDT, state the exchange rate assumption and who bears FX risk.

#### 16.2.1 Implementation services by wave

| Wave | Modules | Reqs | Effort (PD) | Blended rate | Cost (USD) |
|---|---|---:|---:|---:|---:|
| W1 — Foundation & Service Core | | | | | |
| W2 — Field Operations & Inventory | | | | | |
| W3 — Money, Movement & Documents | | | | | |
| W4 — Agreements, Billing & Contact | | | | | |
| W5 — People, Quality & MSP | | | | | |
| W6 — New Asset Businesses | | | | | |
| W7 — Marketplace & Settlement | | | | | |
| W8 — Intelligence & Sustainability | | | | | |
| W9 — Expansion Readiness | | | | | |
| **Total implementation** | | **2,930** | | | |

#### 16.2.2 Implementation services by discipline

| Discipline | Effort (PD) | Rate | Cost (USD) |
|---|---:|---:|---:|
| Programme management | | | |
| Solution architecture | | | |
| Business analysis & functional design | | | |
| Odoo configuration (L1/L2/L3) | | | |
| Custom Odoo development (L5) | | | |
| Standalone service development (L5) | | | |
| Mobile application development (Flutter) | | | |
| Frontend development (Next.js) | | | |
| Integration development (47 integrations) | | | |
| Data platform & BI | | | |
| AI/ML | | | |
| DevOps & platform engineering | | | |
| Data migration | | | |
| Testing (unit, integration, contract, E2E, performance, security, accessibility, localisation, offline) | | | |
| Bengali translation & localisation | | | |
| Documentation & runbooks | | | |
| **Total** | | | |

#### 16.2.3 Custom development register

State every CD deliverable proposed, with type (Odoo module / service / application /
extension), the module it serves, effort and cost. The Company's reference count is
**~138 CD items** — 58 Odoo modules, 12 standalone services, 6 applications, 62 extensions.

> **Disclosed defect (audit finding H2-05).** More than 70 CD identifiers currently **collide
> across module specifications**. A unified CD register with sole allocating authority must be
> produced before any build backlog is created. **This is Wave 1 scope and must be priced.**

#### 16.2.4 Licensing and subscription (L6 and any proposed additions)

| Item | Licence metric | Year 1 | Year 2 | Year 3 | 3-Year total |
|---|---|---:|---:|---:|---:|
| Cloud telephony / CPaaS | | | | | |
| Qualified e-signature | | | | | |
| Identity verification / KYC | | | | | |
| Endpoint RMM agent (conditional, W5 decision) | | | | | |
| *Any additional L6 component proposed* | | | | | |
| **Total** | | | | | |

#### 16.2.5 Infrastructure and hosting

| Item | Year 1 | Year 2 | Year 3 | 3-Year total |
|---|---:|---:|---:|---:|
| Regional cloud (compute, storage, network) | | | | |
| **Bangladesh-resident sensitive-data store (NFR-086)** | | | | |
| Database and analytical platform | | | | |
| Object storage (20 TB growing) | | | | |
| CDN, WAF, DDoS protection | | | | |
| Non-production environments (dev, staging, training, DR) | | | | |
| Observability and backup | | | | |
| **Total** | | | | |

#### 16.2.6 Third-party API consumption

| Service | Basis | Year 1 | Year 2 | Year 3 |
|---|---|---:|---:|---:|
| SMS (transactional + OTP) | Per message | | | |
| WhatsApp Business | Per conversation | | | |
| Google Maps Platform | Per request | | | |
| Traffic data | Per request | | | |
| Identity verification | Per check | | | |
| Cloud storage egress | Per GB | | | |
| Telephony | Per minute + seats | | | |
| E-signature | Per envelope | | | |
| **Total** | | | | |

#### 16.2.7 Training and change management

| Item | Cost (USD) |
|---|---:|
| Train-the-Trainer programme (51+ branch champions) | |
| End-user training (all groups per §13.2) | |
| Administrator training | |
| **Company developer knowledge transfer** | |
| Training material development (Bengali + English) | |
| Video training library | |
| External party training (sellers, brands, vendors, corporate) | |
| Change management programme | |
| **Total** | |

#### 16.2.8 Support and maintenance

| Item | Year 1 | Year 2 | Year 3 | Basis |
|---|---:|---:|---:|---|
| Hypercare (4 weeks × 9 waves) | | | | |
| Business-hours support (09:00–22:00 BST, Sun–Thu) | | | | |
| 24/7 severity-1 support | | | | |
| Preventive maintenance and patching | | | | |
| Odoo and OCA currency maintenance | | | | |
| Enhancement hours pool (state hourly rate) | | | | |
| **Total** | | | | |

#### 16.2.9 Three-year total cost of ownership

| Category | Year 1 | Year 2 | Year 3 | 3-Year total |
|---|---:|---:|---:|---:|
| Implementation & custom development | | | | |
| Licensing (L6) | | | | |
| Infrastructure & hosting | | | | |
| Third-party APIs | | | | |
| Training & change management | | | | |
| Support & maintenance | | | | |
| **GRAND TOTAL** | | | | |

#### 16.2.10 Five-year view

Respondents must also state the **Year 4 and Year 5** run-rate for licensing, infrastructure, APIs
and support, so that the Company can assess total lifetime cost. This is mandatory for
alternative-architecture proposals (ALT-05).

#### 16.2.11 Rate card

| Role | Onshore day rate | Offshore day rate | Overtime / out-of-hours |
|---|---:|---:|---:|
| Programme Manager | | | |
| Solution Architect | | | |
| Senior Odoo Developer | | | |
| Odoo Developer | | | |
| Flutter / Mobile Developer | | | |
| Frontend Developer | | | |
| DevOps Engineer | | | |
| Data / BI Engineer | | | |
| AI / ML Engineer | | | |
| Business Analyst | | | |
| QA Engineer | | | |
| Change & Training Lead | | | |

Rates must be **fixed for 24 months** and thereafter capped at Bangladesh CPI or 5% per annum,
whichever is lower.

### 16.3 Optional and Descopable Items

Price the following **separately and removably**, so the Company can exercise its scope options:

| # | Item |
|---|---|
| OPT-01 | Wave 8 (Intelligence & Sustainability) in full |
| OPT-02 | Wave 9 (Expansion Readiness) in full |
| OPT-03 | Category D (M13, M14, M18) |
| OPT-04 | Category F modules M45, M46, M47, M48 |
| OPT-05 | M66 and M67 (specifications outstanding — see §20.1) |
| OPT-06 | M27 notification service pulled forward to W1/W2 (recommended — see §6.4) |
| OPT-07 | M59 mobile incident reporting pulled forward to W3 (recommended — see §6.10) |
| OPT-08 | M61 knowledge core pulled forward to W4 to unblock M32 |
| OPT-09 | Commercial RMM agent adoption at Wave 5 |
| OPT-10 | Marketplace agent-model VAT treatment (alternative to principal model) |
| OPT-11 | Extended offline window from 24 to 72 hours (RSK-013 contingency) |
| OPT-12 | Additional Bangladesh-resident data store capacity if the DEP-31 legal opinion widens the residency-restricted field set |

### 16.4 Payment Structure

Payment is **milestone-based and tied to wave gate passage**. No milestone payment is released
against a conditionally passed gate until the dated remediation plan is complete.

| Milestone | % of implementation value |
|---|---:|
| Contract signature and mobilisation | 8% |
| Wave 1 gate passed (Month 4) | 12% |
| Wave 2 gate passed (Month 8) | 12% |
| Wave 3 gate passed (Month 13) | 12% |
| **Wave 4 gate passed (Month 18) — v1.0 scope complete** | **14%** |
| Wave 5 gate passed (Month 22) | 12% |
| Wave 6 gate passed (Month 26) | 11% |
| Wave 7 gate passed (Month 30) | 9% |
| Wave 8 gate passed (Month 34) | 5% |
| Wave 9 gate passed and programme closure accepted (Month 36) | 3% |
| **Retention released after the 12-month warranty on the final wave** | **2%** |

**Retention.** 5% of each milestone payment is retained and released at the wave's 12-month
warranty expiry, subject to no open Critical or High defects.

**Service credits.** SLA breaches in the support agreement attract service credits against the
following period's fees, on a scale to be agreed at contract.

### 16.5 Commercial Rules

| # | Rule |
|---|---|
| CR-01 | All prices firm and fixed for the wave to which they relate |
| CR-02 | Effort and cost per wave are **re-baselined at wave start** against the agreed requirement set; variance beyond ±10% requires Steering Committee approval |
| CR-03 | Change requests priced from the published rate card, never renegotiated per change |
| CR-04 | No payment for rework caused by respondent defect or misunderstanding of a documented requirement |
| CR-05 | Travel and accommodation within Bangladesh included in rates; state any exclusions explicitly |
| CR-06 | The Company will not pay for respondent learning of the Odoo platform or the Bengali language |
| CR-07 | Performance bond or bank guarantee of 10% of contract value, to be negotiated |
| CR-08 | The Company may award the whole programme, a subset of waves, or a subset of categories |
| CR-09 | The Company may engage more than one respondent for different components if that produces a better outcome |

---

## 17. EVALUATION METHODOLOGY & SCORING

### 17.1 Evaluation Process

| Stage | Activity | Outcome |
|---|---|---|
| **1** | **Compliance review** | Pass/fail against MQ-01…MQ-12 (§15.1). Failures eliminated. |
| **2** | **Technical evaluation** | Weighted scoring by the evaluation committee against §17.2 |
| **3** | **Scripted demonstration** | Shortlisted respondents demonstrate the scenarios in §17.4 |
| **4** | **Technical deep-dive & team interview** | Named key personnel interviewed; architecture challenged |
| **5** | **Reference checks and site visit** | Direct contact with references, without the respondent present |
| **6** | **Commercial evaluation** | 3-year and 5-year TCO analysis, rate-card benchmarking, descope flexibility |
| **7** | **Final scoring, due diligence & negotiation** | Combined score; contract negotiation with the preferred respondent |

The Company expects to shortlist **3–4 respondents** after Stage 2 and to take **2 finalists**
through Stages 3–5.

### 17.2 Scoring Matrix

| # | Criterion | Weight | What earns a high score |
|---|---|---:|---|
| 1 | **Functional fit — Categories A, C, E** (service, commercial, supply chain — the operational core) | **18%** | Requirement-level responses showing genuine platform knowledge; high L1/L2 coverage with evidence; realistic custom-development scope |
| 2 | **Functional fit — Categories B, D, F, G, H, I, J, K** | **12%** | Depth on statutory-dense areas (finance, tax, payroll, GRC); credible handling of the new business lines |
| 3 | **Portal & mobile capability** — especially P02 offline and P01 conversion | **10%** | Demonstrated offline-first field application; measured performance on low-end Android; Bengali-first design evidence |
| 4 | **Technical architecture & platform engineering** | **10%** | Adherence to AS-01…AS-15; event-driven design; API discipline; no business logic in portals |
| 5 | **Bangladesh regulatory & data protection competence** | **8%** | PDPA 2026 design, split-residency architecture, Mushak/TDS, Labour Act, ISO alignment |
| 6 | **Integration capability** — 47 integrations plus the portal platform contract | **7%** | Named experience with Bangladesh payment rails, telephony, courier APIs; fallback design |
| 7 | **Delivery approach, wave plan & capacity realism** | **8%** | An **independent capacity analysis** against 1,513 PW; an honest view of whether 9 waves in 36 months is achievable |
| 8 | **Data migration approach** | **5%** | Profiling-first, reconciliation-led, with an honest position on the 80% quality assumption |
| 9 | **Team quality & key personnel commitment** | **7%** | Named, committed, verifiable individuals; Bengali capability; low bench-swap risk |
| 10 | **Relevant experience & references** | **6%** | Comparable scale and duration; verifiable outcomes; honest disclosure of failures |
| 11 | **Change management, training & knowledge transfer** | **4%** | Bengali-first training; champion model; a credible plan to make 1000FiX self-sufficient |
| 12 | **Support, maintenance & warranty** | **3%** | SLA credibility; Bengali support; root-cause discipline |
| 13 | **Total cost of ownership (3-year and 5-year)** | **2%** | Value, not lowest price; descope flexibility; rate-card fairness |
| | **Total** | **100%** | |

**Deliberate weighting note.** Cost carries a low weight because the reference architecture removes
licence cost from the comparison and because a programme of this length fails on capability and
capacity, not on price. **Functional and technical fit together carry 50%.** Respondents should
not expect to win on price.

### 17.3 Scoring Scale

| Score | Description |
|---|---|
| **90–100** | Excellent — fully meets and demonstrably exceeds the requirement, with evidence |
| **70–89** | Good — meets the requirement with minor, clearly stated gaps |
| **50–69** | Adequate — meets most of the requirement; some gaps need remediation planning |
| **30–49** | Below average — significant gaps; substantial custom work or capability building required |
| **0–29** | Poor — does not meet the requirement |

A score below **50 on criteria 1, 3, 4, 5 or 7** may result in elimination irrespective of the
weighted total.

### 17.4 Scripted Demonstration Scenarios

Shortlisted respondents will demonstrate the following on a working system — configured, not
mocked. Slides are not accepted.

| # | Scenario | Assesses |
|---|---|---|
| D-01 | Walk-in intake of an unregistered device to a dispatched service order, **timed, in Bengali** | M01, M04, M33, NFR-076 |
| D-02 | Dispatch of a morning queue with skill, certification, location and van-stock constraints; then an emergency insertion with re-optimisation | M02, M22 |
| D-03 | Technician app: full job execution **with the device in airplane mode**, then sync | P02, NFR-037, NFR-047 |
| D-04 | Estimate → customer approval → parts consumption → QC → invoice → payment, end to end | M01, M15, M36, M20 |
| D-05 | Warranty job → automatic claim creation with evidence pack → brand portal submission → reconciliation | M09, P08 |
| D-06 | Mushak 6.3 invoice generation and a Mushak 9.1 return preparation | M51 |
| D-07 | A PDPA data-subject access and erasure request, end to end, showing residency handling | M33, M29, NFR-093, NFR-086 |
| D-08 | Marketplace: seller onboarding with KYC → job broadcast → bid → award → completion → commission → payout | M12, M53, P07 |
| D-09 | A segregation-of-duties violation attempted and blocked, through both UI and API | M29, DoD-04 |
| D-10 | Executive dashboard drill from group revenue to a single job | M25, P06 |
| D-11 | An integration failure with graceful degradation and documented fallback | M28, NFR-050 |
| D-12 | Configuration of a new contract product family **without code change** | M08 |

### 17.5 What Will Be Marked Down

The Company is stating these explicitly so respondents do not waste effort:

| # | Behaviour |
|---|---|
| 1 | Module-level rather than requirement-level functional responses |
| 2 | Over-classification of requirements to L5 custom development without justification |
| 3 | Accepting the published wave plan without an independent capacity analysis |
| 4 | Proposing business logic in portals, or a portal-held authoritative state |
| 5 | Treating Bengali localisation or offline capability as a phase-two item |
| 6 | Generic marketing content in place of specific, evidenced answers |
| 7 | Bench-and-swap staffing models with unnamed personnel |
| 8 | Silence on the disclosed open items in §20 |
| 9 | Pricing that cannot be cleanly descoped |
| 10 | Machine-translated Bengali in any deliverable, including the proposal |

---

## 18. SUBMISSION INSTRUCTIONS & PROCUREMENT TIMETABLE

### 18.1 Procurement Timetable

| Event | Date |
|---|---|
| RFP issuance | **13 August 2026** |
| NDA execution and Annex 1 release | From 17 August 2026, on request |
| Respondent briefing webinar | 27 August 2026 |
| Written question deadline | **17 September 2026** |
| Consolidated answers published to all respondents | 26 September 2026 |
| **Proposal submission deadline** | **30 October 2026, 17:00 BST** |
| Compliance review (Stage 1) | 2–6 November 2026 |
| Technical evaluation (Stage 2) | 9 November – 4 December 2026 |
| Shortlist notification | 8 December 2026 |
| Scripted demonstrations (Stage 3) | 14 December 2026 – 8 January 2027 |
| Technical deep-dive & team interviews (Stage 4) | 12–22 January 2027 |
| Reference checks and site visits (Stage 5) | 25 January – 12 February 2027 |
| Commercial evaluation (Stage 6) | 15–26 February 2027 |
| Preferred respondent notification | 3 March 2027 |
| Contract negotiation | 8 March – 9 April 2027 |
| **Contract signature (target)** | **16 April 2027** |
| **Programme kickoff (target)** | **3 May 2027** |
| Wave 1 gate (target) | September 2027 |
| Wave 4 gate — v1.0 scope complete (target) | November 2028 |
| Programme closure (target) | May 2030 |

1000FiX reserves the right to amend this timetable with reasonable notice to all respondents.

### 18.2 Submission Format

1. **Electronic submission only**, to **info@1000fix.com**, subject line:
   `ERP RFP Response — [Respondent Name] — 1000FIX-ERP-RFP-2026-002`
2. **Formats:** PDF for the narrative proposal; **Excel or CSV** for Appendix A (requirement
   response) and Appendix E (pricing). Scanned PDFs of the response matrices are not acceptable.
3. **Language:** English. Bengali supplementary material accepted and welcomed.
4. **Page limit:** the narrative proposal must not exceed **120 pages** excluding appendices.
   Concision is scored favourably.
5. **File size:** maximum 50 MB per email; use a secure file-sharing link for larger submissions
   and provide access for 180 days.
6. **Naming:** `[Respondent]_[SectionNumber]_[SectionName]_v[n].[ext]`
7. Late submissions will not be accepted.

### 18.3 Required Proposal Structure

| Section | Required content |
|---|---|
| **Cover letter** | Executive summary, commitment statement, authorised signatory, 180-day validity confirmation |
| **Section 1 — Compliance** | Point-by-point evidence against MQ-01…MQ-12 |
| **Section 2 — Company profile** | Per §15.2 |
| **Section 3 — Solution overview** | Architecture, layer allocation, differentiators, and the respondent's view of the reference architecture |
| **Section 4 — Functional response** | Narrative by category, cross-referencing Appendix A |
| **Section 5 — Technical response** | Architecture, security, data protection, residency, performance, integration |
| **Section 6 — Portal & mobile response** | Per-portal approach; offline architecture in detail |
| **Section 7 — Delivery plan** | Wave plan, **independent capacity analysis**, methodology, governance, risk mitigation |
| **Section 8 — Data migration** | Approach, tooling, profiling, reconciliation, rollback |
| **Section 9 — Team** | Org chart, named key personnel, commitment percentages, local partner |
| **Section 10 — Training, change & knowledge transfer** | Approach, materials, Bengali strategy, self-sufficiency plan |
| **Section 11 — Support & maintenance** | SLAs, team, escalation, tooling |
| **Section 12 — Commercial** | Narrative to Appendix E |
| **Section 13 — References & case studies** | Per §15.5, including the §VQ-22 disclosure |
| **Section 14 — Response to disclosed open items** | A position on **every item in §20** |
| **Section 15 — Exceptions & assumptions** | Any deviation from this RFP, with justification and commercial impact |
| **Appendix A** | **Requirement Response Matrix** — every requirement in Annex 1 (Excel/CSV) |
| **Appendix B** | Key personnel CVs |
| **Appendix C** | Detailed project plan with dependencies (Gantt or equivalent, machine-readable) |
| **Appendix D** | Sample deliverables — a design document, a runbook, an OpenAPI specification, a test report from a comparable engagement |
| **Appendix E** | **Pricing workbook** (Excel) per §16.2 |
| **Appendix F** | Certifications, insurance, financial statements |
| **Appendix G** | *(Optional)* Alternative-architecture proposal per §5.7 |

### 18.4 Questions and Clarifications

- All questions in writing to **info@1000fix.com** by **17 September 2026**
- Questions and answers will be published to all respondents, anonymised
- **No individual pre-submission meetings will be held.** The briefing webinar on 27 August 2026 is
  the only group session
- 1000FiX may request clarification, additional demonstration or a proof of concept from any
  respondent
- 1000FiX may conduct due diligence on any aspect of a proposal, including financial standing,
  delivery capacity and reference verification

### 18.5 Reservations

1000FiX reserves the right to: accept or reject any or all proposals at its sole discretion;
award a reduced scope; award to more than one respondent; cancel this procurement at any stage;
negotiate with one or more respondents; and amend the timetable. This RFP does not commit 1000FiX
to award a contract or to reimburse any cost of proposal preparation.

---

## 19. CONTRACTUAL TERMS & CONDITIONS

### 19.1 General Terms

1. **No obligation.** This RFP does not commit 1000FiX to award a contract, pay any proposal
   preparation cost, or procure any services.
2. **Confidentiality.** All information in this RFP, in Annex 1, and in all responses is
   confidential. Respondents may not disclose any aspect of this process to third parties without
   written consent. An NDA must be executed before Annex 1 is released.
3. **Intellectual property.** All customisations, configurations, custom modules, services,
   applications, migrations, test suites, documentation and training material created for 1000FiX
   **are owned by 1000FiX**. The respondent retains ownership only of pre-existing proprietary
   frameworks, which must be declared in the Exceptions schedule and licensed to 1000FiX
   perpetually, irrevocably and royalty-free for the operation and extension of the system.
4. **Open-source obligations.** The respondent must comply with all component licences, must
   contribute OCA migrations upstream, and must maintain a licence register.
5. **Data ownership.** All data entered into or generated by the system belongs exclusively to
   1000FiX. Full export in open, documented formats must be available at any time, not only at
   termination.
6. **Source code delivery.** Source code, configuration and infrastructure-as-code are delivered
   **continuously** to a Company-controlled repository, not at milestones. A milestone is not
   complete until the corresponding code is in the Company repository.
7. **Non-exclusivity.** This RFP grants no exclusive rights. 1000FiX may engage multiple parties.
8. **Validity.** Proposals must remain valid for **180 days** from the submission deadline.
9. **Governing law.** Any contract arising shall be governed by the laws of the People's Republic
   of Bangladesh.
10. **Dispute resolution.** Good-faith negotiation, then mediation, then arbitration under the
    Arbitration Act of Bangladesh.

### 19.2 Contractual Expectations

The selected respondent will enter a formal contract including:

- A detailed Statement of Work per wave, with the requirement set frozen at wave start
- Service Level Agreements with a service-credit and incentive structure
- **Milestone payments tied to wave gate passage**, with 5% retention per milestone
- The 17-point Definition of Done as an acceptance standard
- Warranty and defect liability of not less than 12 months per wave
- Performance bond or bank guarantee (10%, to be negotiated)
- **Key personnel lock-in** with approval required for substitution
- Source code escrow for any proprietary component
- Termination for convenience and for cause, with 90 days' transition assistance
- Non-disclosure agreement
- **Data processing agreement** under the PDPA 2026, with sub-processor control
- Business continuity provisions
- Step-in rights on sustained material breach

### 19.3 Compliance Obligations

The respondent must comply with:

- All applicable laws of the People's Republic of Bangladesh
- **Personal Data Protection Act 2026 (Law 63 of 2026)**
- **Cyber Security Ordinance 2025**
- ICT Act 2006
- VAT and Supplementary Duty Act 2012, and all NBR regulations
- Bangladesh Labour Act 2006 and Bangladesh Labour Rules 2015 (for on-site staff)
- Bangladesh e-waste and environmental handling rules
- ISO 9001:2015 process obligations, which 1000FiX must maintain throughout

### 19.4 Programme Governance the Respondent Must Operate Within

```
                    ┌──────────────────────────────┐
                    │           BOARD              │
                    │  Investment approval         │
                    │  Quarterly programme review  │
                    └───────────────┬──────────────┘
                                    │
                    ┌───────────────▼──────────────┐
                    │  ERP STEERING COMMITTEE      │
                    │  CEO (chair) · CTO · CFO ·   │
                    │  CCO · Ops Director ·        │
                    │  HR Director · Quality Mgr   │
                    │  Monthly · Gate decisions ·  │
                    │  Change control · Risk       │
                    └───────────────┬──────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
┌───────▼────────┐        ┌─────────▼─────────┐      ┌──────────▼─────────┐
│ PROGRAMME      │        │ ARCHITECTURE      │      │ BUSINESS OWNERS    │
│ MANAGEMENT     │        │ REVIEW BOARD      │      │ FORUM              │
│ OFFICE         │        │ CTO · Architect · │      │ 16 module owners   │
│ Weekly         │        │ Leads · Security  │      │ Fortnightly        │
│ Plan · Risk ·  │        │ Fortnightly       │      │ Requirements ·     │
│ Report · Change│        │ Standards · ADRs  │      │ UAT · Adoption     │
└───────┬────────┘        └───────────────────┘      └────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────────────────────┐
│  DELIVERY SQUADS                                                        │
│  Service · Commercial · Supply · Finance · People · Platform · Data     │
│  Daily stand-up · Fortnightly sprint · Sprint review with owners        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Decision rights:**

| Decision | Authority |
|---|---|
| Programme investment and continuation | Board |
| Wave Go/No-Go | Steering Committee |
| Scope change affecting a P0 or P1 requirement | Steering Committee |
| Scope change within a module (P2/P3) | PMO with the business owner |
| Architecture standard change | Architecture Review Board |
| Technology selection (new L4/L5) | Architecture Review Board |
| New L6 commercial component | CFO, on Architecture Board recommendation |
| Requirement acceptance at UAT | **Named business owner** |
| Risk acceptance (Critical or High) | Steering Committee |
| Segregation-of-duties exception | CFO or CTO, time-boxed |
| Production emergency change | CTO, with retrospective Steering review |

**Change control rules:** no change is implemented before it is approved and recorded · **no wave
absorbs a change mid-wave** — approved changes enter the next wave · a change that removes scope
must state which benefit is forgone · the change log is reviewed at every Steering Committee
meeting.

---
---

# PART E — DISCLOSURE & REFERENCE

---

## 20. DISCLOSED OPEN ITEMS, KNOWN DEFECTS & PROGRAMME RISKS

The Company has audited its own specification set twice and is disclosing what those audits found.
This is deliberate: a respondent who prices against a specification whose defects are hidden will
either lose money or cut corners, and neither outcome serves 1000FiX.

**Respondents must state a position on every item in this section (proposal Section 14).**
Silence will be scored as a failure to engage with the specification.

### 20.1 Specification Completeness

| # | Item | Status | Impact on respondents |
|---|---|---|---|
| 20.1.1 | **M66 Internal IT Service Management and M67 Project, Program & Portfolio Management have no specification file.** These are the only two outstanding module specifications. Estimated at 22 and 26 requirements, 11 and 14 PW. | **Open** — to be written before Wave 6 | Price these as estimates and state your assumption basis. M66 is referenced by M58 onboarding provisioning, M29 access requests and M59 equipment findings; those interface contracts are currently unverifiable. |
| 20.1.2 | **28 requirement IDs in Category A are allocated but unused** — 16 in M01, 9 in M02, 3 in M31. Recorded counts were taken from the highest ID rather than the actual count. Category A's registered total of 388 was 26 overstated; the measured figure is 362. | **Fixed in the register; open in the modules** | Do not assume contiguous requirement sequences in M01, M02 or M31. The recommendation is to **retire** the unused IDs rather than renumber, since renumbering would violate the permanent-identity rule. |
| 20.1.3 | The specification set is **93 documents written of 123 planned (76%)**. Planned-but-unwritten documents include the market benchmark study, module gap analysis, module boundary and overlap rules, per-portal specifications (12), consolidated identifier conventions, and four delivery documents. | Open | Module boundaries are currently declared in each category overview and in each module file §3. Portal detail is in the portal suite overview. State any material information gap you encounter. |

### 20.2 Identifier and Register Integrity

| # | Item | Status | Impact on respondents |
|---|---|---|---|
| 20.2.1 | **More than 70 custom-development (`CD-nnn`) identifiers collide across modules.** Some identifiers are claimed by up to 8 different modules. | **Open — must be resolved before any build contract is issued** | This is the most consequential defect for a builder. CD identifiers name **deliverable software modules** and will appear in the build backlog, repository structure and deployment manifest. A unified CD register with sole allocating authority is **Wave 1 scope and must be priced.** |
| 20.2.2 | **22 KPI identifiers are used by two or more modules** — one identifier resolves to nine different metrics. | Open | The programme KPI register must be built and ~60 identifiers reassigned. This is **Wave 1 scope and must be priced.** Benefits reporting references KPI IDs; those references are currently ambiguous. |
| 20.2.3 | **18 segregation-of-duties controls (SOD-13…SOD-30) are implemented in module specifications but unregistered** in the central matrix. | Open | Registration of all 30 is **Wave 1 scope**. Controls that cannot be evidenced are, for audit purposes, controls that do not exist. **Bid on 30 controls.** |
| 20.2.4 | **Roles R39–R46 are used but unregistered; R54 and R57 are referenced with no definition; R60 is a duplicate identity for R32.** | Open — **R60 is a live permission defect** | A duplicate role identity means an access rule written against R32 does not apply to a user granted R60. **Bid on 46 roles**, with R60 eliminated and R54/R57 resolved, as Wave 1 scope. |
| 20.2.5 | M42 uses the four-character code `SRM2` against a three-character convention, because `SRM` is permanently allocated to M01. | Accepted and documented | Use the codes exactly as allocated. |

### 20.3 Cost, Effort and Scope

| # | Item | Status | Impact on respondents |
|---|---|---|---|
| 20.3.1 | **Programme effort is 1,513 PW measured against 834 PW in the approved business case — approximately 1.8×.** Requirements are 2,930 against 1,180 — +148%. | **Escalated as Steering Committee decision D-14** | The Committee has not yet chosen between funding, phasing or cutting. **Structure pricing so waves and categories descope cleanly.** The Company may award a reduced scope. |
| 20.3.2 | The estimating model failed in an explicable way: requirement counts were under-estimated wherever a category carries statutory, contractual or master-data obligations — F +73%, H +52%, I +44%, C +39%, G +29% — and were accurate where purely operational — D 0%, J +12%. | Understood; correction mechanism retired | Expect statutory-dense areas to be requirement-heavy but individually small — most resolve to configuration in a versioned rule pack rather than new code. Effort tracked at only +15% against +21% on count. |
| 20.3.3 | **Wave capacity has not been validated against the restated effort.** W4 at ~230 PW against a 17-FTE, ~18-week wave leaves almost no contingency. W3 and W6 are similarly tight. | Open | Produce your **own capacity plan**. This is scored (criterion 7, §17.2). |
| 20.3.4 | The return figures in §1.5 use the restated cost line; the Company's internal charter documents still show ROI computed against the superseded cost. | Being re-baselined | Not a respondent obligation, but be aware the internal business case is under revision. |

### 20.4 Superseded v1.0 Requirements

Four v1.0 requirements are formally superseded. **No v1.0 requirement has been deleted.**

| v1.0 requirement | Superseded by | Reason |
|---|---|---|
| INT-022 — Rasa 3.6 Bengali chatbot | FR-CAI-* (LLM-based Bengali assistant, M32) | Rasa open source is in maintenance mode |
| INT-019 — Google Routes / Timefold routing | FR-FSM-* (VROOM + OSRM with selective traffic API) | $0 licence, self-hosted, embeds custom constraints |
| BR-BI-007 — drag-and-drop report builder | FR-BID-018 (semantic-layer self-service exploration) | Warehouse-backed approach supersedes the point tool |
| BR-DMS-003 — approval workflows in DMS | FR-BPA-* (one platform-wide workflow engine, M63) | One workflow engine serves all modules |

### 20.5 Open Decisions That Shape the Build

| # | Decision | Owner | Needed by | Consequence if delayed |
|---|---|---|---|---|
| **D-13** | **Approve the split-residency data architecture**, subject to the legal opinion in DEP-31 | CTO + CFO + Legal | **Before Wave 1 architecture is fixed** | **The entire data architecture is blocked. This is the most urgent open decision in the programme.** |
| **D-14** | Accept the restated TCO, or direct a descope | Board / CEO / CFO | Before the next Board review | The Board is working from a figure the audit found materially low |
| **D-15** | Confirm whether 1000FiX is a *significant data fiduciary* and, if so, appoint a Chief Data Officer | CEO + Legal | W4 minus 3 months | Statutory non-appointment |
| D-01 | Approve the expanded scope, budget and 36-month horizon | Board / CEO | Before kickoff | Programme cannot start |
| D-02 | Confirm and protect business super-user availability across all waves | CEO + department heads | Before kickoff | RSK-001 materialises; waves slip |
| **D-03** | **Marketplace commercial model — principal vs agent, commission structure, settlement terms, liability** | CEO + CFO + Legal | W7 minus 3 months | RSK-022; Wave 7 blocked |
| D-04 | Legal-entity structure for rental and refurbished resale | CFO + Legal | W6 minus 3 months | Finance design blocked; possible rework |
| D-05 | Multi-country target markets and sequence | CEO | W9 minus 3 months | Country pack cannot be specified |
| D-06 | Telephony vendor for hotline 16743 | CTO | W4 minus 2 months | Contact centre build blocked |
| D-07 | Whether to adopt a commercial RMM agent (L6) | CTO + CFO | W5 | Pilot outcome determines |
| D-08 | Data residency posture for recovered customer data | CTO + Legal | W6 minus 2 months | M06 blocked |
| D-09 | Whether 1000FiX guarantees marketplace work to the customer | CEO + Legal | W7 minus 3 months | Liability model undefined |
| D-10 | Seller insurance requirement and liability caps | Legal | W7 minus 3 months | Seller agreement undefined |
| D-11 | Technician device procurement model (Company-issued vs allowance) | Ops Director + CFO | W2 minus 2 months | Field rollout blocked |
| D-12 | Refurbished warranty terms and reserve policy | CFO + Retail Head | W6 | M14 commercial model undefined |

### 20.6 Critical and High Risks the Respondent Must Address

**Five risks are rated Critical — these are the ones that can end the programme.**

| ID | Risk | Rating | Owner | The respondent's obligation |
|---|---|---|---|---|
| **RSK-001** | Business super-user availability falls short, stalling UAT | **Critical** | CEO | Design a delivery model that does not run ahead into unaccepted work; propose ways to reduce the super-user burden without reducing acceptance rigour |
| **RSK-002** | Scope creep across a 36-month programme | **Critical** | Steering Committee | Operate wave-locked scope; propose a parking-lot discipline |
| **RSK-008** | **Technician rejection of the mobile app** | **Critical** | Ops Director | Set out field usability approach, technician co-design, pilot with senior technicians, and a simplified "lite" mode contingency |
| **RSK-022** | Marketplace VAT and liability model incorrect | **Critical** | CFO | Build M12/M53 so the revenue treatment is configurable; price both principal and agent treatments |
| **RSK-023** | Marketplace quality failure damages the 1000FiX brand | **Critical** | CCO | Apply identical QC and evidence standards to marketplace and owned work; automatic scoring consequences |
| **RSK-032** | **Non-compliance with the PDPA 2026**, whose enforcement activates inside Wave 4 | **Critical** | CFO / CTO | Consent, notice and rights built into M33 and every capture point from Wave 1 |
| **RSK-033** | **Data residency architecture unlawful** — Singapore hosting conflicts with the PDPA restriction on cross-border transfer of Sensitive Personally Identifiable Data | **Critical** | CTO / Legal | Split-residency design with field-level enforcement; contingency if the legal opinion widens the resident field set |
| **RSK-036** | Cost estimate materially understated | **Critical** | CFO | Price honestly; structure for clean descope |
| RSK-013 | Field connectivity worse than assumed, breaking sync | High | CTO | Offline-first with a 24-hour guarantee; field testing in the weakest coverage areas; extension to 72 hours as contingency (OPT-11) |
| RSK-014 | Data migration quality below usable threshold | High | CTO | Profiling before every load; trial migrations; archive area for uncleansable records |
| RSK-015 | **OCA v19 migration gaps on critical modules** — `field-service` ~25 of 33 migrated, `helpdesk` ~20 of 28 | High | Solution Architect | Verify migration status before each wave; fork, migrate and contribute upstream; state which modules you will migrate and at what cost |
| RSK-016 | Portal platform API contract instability | High | CTO | Versioned contract; contract tests in both CI pipelines; joint change process |
| RSK-017 | Performance inadequate at 51+ branches under real load | High | CTO | Load test at 1.5× projected peak before every gate |
| RSK-018 | Offline sync conflicts corrupt data | High | Solution Architect | Append-only journal; server-authoritative resolution; extensive scripted conflict testing |
| RSK-021 | Technical debt accumulates under wave pressure | High | Solution Architect | Architecture standards enforced in CI; refactoring capacity reserved each wave |
| RSK-025 | Brand partner claim rejection rate does not improve | High | Finance Director | Evidence completeness enforced before submission; per-brand rule engine |
| RSK-026 | Bangladesh VAT, tax or labour regulation changes mid-programme | High | CFO | **Configuration-driven, versioned rule packs**; country-pack isolation |
| RSK-034 | Chief Data Officer not appointed where required | High | CEO | Design the role's system access and reporting into M60 |
| RSK-035 | Regulatory citations drift out of date | High | CTO | Verified-on dates on every citation; re-verified at each wave gate |

### 20.7 Key Assumptions the Respondent Should Test

| ID | Assumption | If false |
|---|---|---|
| ASM-01 | All service centres have at least 3G connectivity during operating hours | Extended offline windows; SMS fallback; connectivity investment |
| ASM-02 | Technicians will use Company-issued Android 11+ devices | Device procurement cost added; support matrix widened |
| ASM-03 | Existing customer and device data is exportable at **≥ 80% quality** | Migration effort increases materially; manual cleansing programme |
| ASM-04 | The 17+ brand partnerships continue through the programme | Warranty benefit case reduces |
| ASM-05 | Bangladesh VAT rates and Mushak format remain broadly stable | Configuration changes; possible rework of tax reporting |
| ASM-07 | The portal platform exposes and maintains documented, versioned APIs | Integration effort increases; adapter layer required |
| ASM-08 | bKash, Nagad and SSLCOMMERZ provide sandbox and production access on schedule | Payment go-live slips; cash-only fallback |
| ASM-11 | Odoo 19 remains supported through the programme; a later major upgrade is a separate project | Upgrade project added to the roadmap |
| ASM-12 | OCA critical-path modules complete v19 migration, or can be migrated by the delivery team | Custom development substitutes; effort increases |
| ASM-15 | Bengali-capable open-weight language models remain available and adequate | Commercial LLM API considered, with data-residency implications |
| ASM-16 | Go-live does not fall in Ramadan, Eid-ul-Fitr or Eid-ul-Adha peak periods | Wave dates adjusted |
| ASM-19 | Technicians can read Bengali interfaces | Icon-led and voice-led interface variants required |
| ASM-20 | Biometric attendance hardware is procured before Wave 5 | GPS-based clock-in used as the sole mechanism |
| **ASM-21** | **A Bangladesh-resident data store of adequate reliability and performance is procurable** | The architecture must be re-planned; on-premises may be necessary |
| **ASM-22** | **PDPA enforcement timing holds at approximately 13 May 2027** | An earlier activation compresses the compliance window inside Wave 4 |

### 20.8 Facts Under Verification

| # | Item | Status |
|---|---|---|
| 20.8.1 | The **"17+ brands"** figure, carried from the v1.0 BRD, underpins M22's certification coverage reporting and its KPI target. It has not been verified against the current principal agreement list. | Written confirmation being sought from each principal before Wave 5 |
| 20.8.2 | **AY 2026–27 income tax parameters** used in M56 — thresholds BDT 375,000 / 425,000 / 500,000 / 525,000; minimum tax BDT 5,000 (BDT 1,000 first-time); investment rebate 10% capped at BDT 750,000 eligible investment. **Sources conflict on whether the 5% introductory slab survives.** | **The statutory pack must be built from the enacted Finance Act, not from press reporting.** Verification required at W5 minus 3 months. Respondents must design the tax pack as versioned configuration so a late parameter change is not a code change. |

### 20.9 Constraints

| ID | Constraint | Consequence |
|---|---|---|
| CON-01 | Three-year budget envelope (restated, §16.1) | W8 and W9 are the first deferral candidates |
| CON-02 | v1.0 committed scope must be delivered by Month 18 | Waves 1–4 cannot be reordered |
| CON-03 | **The Next.js 15 + Payload CMS portal platform cannot be replaced** | The ERP integrates; API contract discipline is mandatory |
| CON-04 | All financial transactions must comply with NBR requirements | Compliance is a P0 gate, not a feature |
| CON-05 | Bengali must be primary for field and customer surfaces | Translation is a definition-of-done item, not a follow-up |
| CON-06 | bKash and Nagad must be primary payment methods | Bangladesh-specific gateway integration is mandatory |
| CON-07 | Field applications must operate offline | Offline-first architecture is non-negotiable |
| CON-08 | No go-live during Ramadan or the Eid periods | Wave dates account for the Islamic calendar |
| CON-09 | **Sensitive personal data must be Bangladesh-resident**; other data in an approved region | Split-residency architecture (supersedes the v1.0 single-region constraint) |
| CON-10 | Automation must augment roles, not displace staff without approval | Change messaging and redeployment planning required |
| CON-11 | ISO 9001:2015 certification must be maintained throughout | Process changes require QMS documentation updates in step |
| CON-12 | Business super-user time is finite | **UAT capacity, not developer capacity, paces the programme** |

### 20.10 What Would Make This Programme Fail

Stated plainly, because a risk register can obscure the obvious. Respondents should address each
in their delivery plan.

1. **The business does not free up its people.** Software can be built; it cannot be accepted,
   tested, trained or adopted without the business. This is the single largest risk.
2. **Technicians reject the app.** Four hundred people in the field decide whether this programme
   works. If the app is slower than paper, they will not use it, and everything downstream —
   dispatch, inventory, invoicing, warranty, quality — degrades.
3. **Scope grows continuously.** Thirty-six months is long enough for the business to change twice.
   Without ruthless change control, the programme never finishes.
4. **The marketplace is launched before the tax and liability model is settled.** This is the one
   decision that could create a restatement or a regulatory problem.
5. **Benefits are never measured.** If baselines are not captured before each wave, no benefit can
   be claimed honestly, and the business case becomes decoration.

**None of these is a technology problem. All of them are addressable.**

---

## 21. APPENDICES

### Appendix A — Requirement Response Matrix *(to be completed by respondents)*

Delivered with Annex 1 as a machine-readable workbook. One row per requirement, with columns:

`FR ID` · `Module` · `Category` · `Title` · `Statement` · `Priority` · `Wave` ·
**`Response code (N/O/T/S/C/X/G)`** · **`Delivery layer (L1–L6)`** · `Component/module name` ·
**`Effort (person-days)`** · `Proposed wave` · `Dependencies` · `Risk (H/M/L)` · `Comments`

### Appendix B — Service Centre Network

1000FiX operates **51+ service centres** across all 8 divisions. The complete list of locations,
addresses, operating hours, connectivity status and hardware inventory will be provided to
shortlisted respondents during Stage 3.

**Regional structure:** Dhaka — corporate HQ, central warehouse, ~20 service centres · Chittagong —
regional hub and centres · Rajshahi — regional hub and centres · Khulna — regional hub and centres
· Sylhet, Barisal, Rangpur, Mymensingh — service centres with standard operations.

### Appendix C — Authorised Brand Partner Matrix

| Brand | Product categories serviced | Warranty type |
|---|---|---|
| Dell | Laptops, desktops, servers, monitors | Full warranty + extended |
| HP | Laptops, desktops, printers | Full warranty + extended |
| Lenovo | Laptops, desktops | Full warranty |
| Acer | Laptops, desktops | Full warranty |
| Samsung | Mobile, tablet, TV, appliances | Full warranty |
| Xiaomi | Mobile, smart devices | Full warranty |
| Huawei | Mobile, networking | Full warranty |
| Honor | Mobile | Full warranty |
| Sony | Laptops, electronics | Full warranty |
| Toshiba | Laptops | Full warranty |
| Gigabyte | Motherboards, components | Full warranty |
| Microsoft | Surface devices | Full warranty |
| BenQ | Monitors, projectors | Full warranty |
| Epson | Printers | Full warranty |
| Intel | Components | Full warranty |
| TwinMOS | Memory, storage | Full warranty |
| Delux | Peripherals | Full warranty |

*Each partner has its own claim format, evidence requirements, rate card and technician
certification requirements. Per-brand claim specifications will be provided at Wave 4 (dependency
DEP-22). The count is under verification — see §20.8.1.*

### Appendix D — KPI Register Summary

**95 programme KPIs (KPI-001 … KPI-095)** across ten domains. Selected targets:

| Domain | KPI | Baseline | W4 | W8 |
|---|---|---|---|---|
| Service | Service order automation rate | 20% | 65% | **85%** |
| Service | Average TAT — IT equipment | unmeasured | < 36 h | **< 24 h** |
| Service | Average TAT — appliance on-site | unmeasured | < 6 h | **< 4 h** |
| Service | First-time fix rate | 70% | 82% | **88%** |
| Service | Rework rate | unmeasured | < 5% | **< 3%** |
| Service | SLA compliance | unmeasured | 92% | **96%** |
| Service | Walk-in intake time | ~10 min | < 4 min | **< 3 min** |
| Field | Jobs per technician per day | 4–5 | 7 | **8–9** |
| Field | Technician utilisation | 55% | 74% | **82%** |
| Field | Automatic assignment rate | 0% | 20% | **70%** |
| Field | Travel time as % of working day | ~35% | 26% | **22%** |
| Field | Technician app daily active usage | 0% | 92% | **95%** |
| Field | Offline sync failures | n/a | 0 | **0** |
| Field | Chain-of-custody exceptions | untracked | 0 | **0** |
| Customer | CSAT | 3.8/5 | 4.4/5 | **4.7/5** |
| Customer | NPS | unmeasured | 42 | **55** |
| Customer | Online booking rate | 40% | 72% | **88%** |
| Customer | Churn | ~15% | 11% | **< 8%** |
| Customer | AI first-contact resolution | 0% | 40% | **55%** |
| Commercial | AMC/RAMC renewal rate | 60% | 80% | **88%** |
| Commercial | Contract base growth | baseline | 1.6× | **2.5×** |
| Commercial | Gross margin on paid repair | baseline | +2 pts | **+4 pts** |
| Warranty | Claims submitted within 72 h | ~50% at 30–90 d | 92% | **95%** |
| Warranty | Warranty revenue leakage | 15–20% | 5% | **< 2%** |
| Warranty | Days from service to reimbursement | 60–120 | 55 | **< 45** |
| Supply chain | Inventory accuracy | 75% | 96% | **98%** |
| Supply chain | Part availability at first request | unmeasured | 88% | **93%** |
| Supply chain | Van stock variance | untracked | < 2% | **< 1%** |
| Financial | Month-end close cycle | 15–20 days | 5 days | **≤ 3 days** |
| Financial | Bank reconciliation auto-match | manual | 90% | **94%** |
| Financial | Invoices auto-generated | 0% | 100% | **100%** |
| Financial | Revenue leakage (unbilled delivered work) | unknown | < 1.5% | **< 0.5%** |
| Financial | VAT returns filed on time with zero adjustment | manual | 100% | **100%** |
| People | Payroll processing time | 3 days | 6 h | **< 4 h** |
| People | Certifications current (no lapses) | unknown | 100% | **100%** |
| People | Claims rejected for uncertified technician | unknown | Zero | **Zero** |
| Quality | ISO major non-conformances | unknown | Zero | **Zero** |
| New lines | Monitored assets under management | 0 | — | **5,000** |
| New lines | MSP SLA attainment | n/a | — | **98%** |
| New lines | Rental fleet utilisation | n/a | — | **68%** |
| New lines | Refurbished units sold per year | 0 | — | **12,000** |
| New lines | Approved active marketplace sellers | 0 | — | **500** |
| New lines | Marketplace share of job volume | 0% | — | **25%** |
| New lines | Seller payout accuracy | n/a | — | **100%** |
| New lines | E-waste diversion from landfill | n/a | — | **92%** |
| Platform | System uptime (business hours) | — | — | **≥ 99.9%** |
| Platform | API p95 latency | — | — | **< 400 ms** |
| Platform | Event delivery success | — | — | **> 99.9%** |
| Platform | Critical vulnerabilities open > 7 days | — | — | **Zero** |
| Platform | Orphaned accounts after leaver | — | — | **Zero beyond 24 h** |
| Platform | Bengali translation completeness | — | — | **100%** |
| Platform | Overall automation of routine work | 20% | 65% | **85%** |

> **Note (audit finding H2-04).** 22 KPI identifiers currently collide across modules. The
> programme KPI register with reassigned identifiers is Wave 1 scope — see §20.2.2.

**Benefit tracking discipline the respondent must support:** every KPI's baseline is measured and
signed off **before** the relevant wave begins. **A KPI without a baseline cannot claim a benefit.**

### Appendix E — Pricing Workbook *(to be completed by respondents)*

Machine-readable workbook mirroring §16.2, issued with Annex 1.

### Appendix F — Annex 1 Document Register

Released to respondents under NDA. **93 documents written, 30 planned.**

| Folder | Contents |
|---|---|
| `00_Governance_and_Charter/` | Master index · Executive summary & scope charter · Scope expansion delta v1→v2 · Risks, assumptions, dependencies & governance · **Documentation audit report** · **Category H audit & repository integrity report** |
| `02_Architecture/` | ERP module architecture & system map · **Module catalogue master register (authoritative)** · Technology stack & build-vs-buy decisions |
| `03_Modules/` | **65 module specifications** across 11 category folders, each with the full 19-section template · 11 category overviews · category audit reports · module template |
| `04_Portals_and_Applications/` | Portal suite overview (P01–P12) |
| `05_Cross_Cutting_Specifications/` | Feature & function register · Data model & entity catalogue · Integration & API catalogue · Role, permission & access matrix · Business rules & automation catalogue · Non-functional requirements & standards |
| `06_Delivery_and_Implementation/` | Implementation roadmap & phasing · KPI, benefits & acceptance criteria |
| `99_Reference/_Superseded/` | Five superseded pillar documents, retained for traceability |
| Root | README · Folder structure |

**Precedence.** Where documents disagree on module identity, code, category, ownership, priority or
wave, `02_Architecture/02-02_Module_Catalogue_Master_Register.md` is authoritative. Where this RFP
disagrees with Annex 1 on commercial or procurement terms, **this RFP prevails**. Where this RFP
disagrees with Annex 1 on a functional or technical requirement, **Annex 1 prevails** and the
discrepancy must be raised as a question under §18.4.

### Appendix G — Glossary

| Term | Definition |
|---|---|
| **1000FiX** | 1000FiX Services Limited, the issuing organisation |
| **AMC** | Annual Maintenance Contract |
| **API** | Application Programming Interface |
| **AR / AP** | Accounts Receivable / Accounts Payable |
| **AS-nn** | Architecture standard identifier |
| **ASM-nn** | Assumption identifier |
| **BDT** | Bangladeshi Taka |
| **BEFTN** | Bangladesh Electronic Funds Transfer Network |
| **BIN** | Business Identification Number (VAT registration) |
| **BO-nn** | Business objective identifier |
| **BRU-nn** | Business rule identifier |
| **BST** | Bangladesh Standard Time (UTC+6) |
| **CAPA** | Corrective and Preventive Action |
| **CD-nnn** | Custom development deliverable identifier |
| **CDO** | Chief Data Officer (PDPA 2026 role) |
| **CON-nn** | Constraint identifier |
| **CPaaS** | Communications Platform as a Service |
| **CSAT** | Customer Satisfaction Score |
| **D-nn** | Programme decision identifier |
| **DEP-nn** | Dependency identifier |
| **DoD-nn** | Definition-of-done criterion |
| **DPIA** | Data Protection Impact Assessment |
| **EaaS** | Equipment-as-a-Service |
| **ERP** | Enterprise Resource Planning |
| **ESG** | Environmental, Social and Governance |
| **FIFO** | First In, First Out (inventory valuation) |
| **FR-<CODE>-nnn** | Functional requirement identifier |
| **FSM** | Field Service Management |
| **GL** | General Ledger |
| **GRN** | Goods Receipt Note |
| **IEEE 2883** | Standard for sanitising storage media |
| **IMEI** | International Mobile Equipment Identity |
| **INT-nnn** | Integration identifier |
| **ISO 9001:2015** | Quality management system standard |
| **ISO 27001** | Information security management standard |
| **ISO 45001** | Occupational health and safety management standard |
| **KPI-nnn** | Key performance indicator identifier |
| **KYC** | Know Your Customer |
| **L1–L6** | Delivery layer (Odoo native / OCA / third-party / open source / custom / commercial) |
| **LLM** | Large Language Model |
| **MFA** | Multi-Factor Authentication |
| **Mnn** | ERP module identifier (M01–M67) |
| **MQ-nn** | Mandatory qualification identifier |
| **MRR / ARR** | Monthly / Annual Recurring Revenue |
| **MSP** | Managed Service Provider |
| **Mushak 6.3** | Bangladesh VAT tax invoice form |
| **Mushak 9.1** | Bangladesh monthly VAT return form |
| **NBR** | National Board of Revenue, Bangladesh |
| **NCR** | Non-Conformance Report |
| **NDMA** | National Data Management Authority (PDPA 2026 regulator) |
| **NFR-nnn** | Non-functional requirement identifier |
| **NID** | National Identity (Bangladesh) |
| **NPS** | Net Promoter Score |
| **NTE** | Not-to-Exceed |
| **OCA** | Odoo Community Association |
| **OIDC** | OpenID Connect |
| **OSRM** | Open Source Routing Machine |
| **P0–P3** | Priority level |
| **Pnn** | Portal identifier (P01–P12) |
| **PDPA 2026** | Personal Data Protection Act 2026 (Bangladesh, Law 63 of 2026) |
| **PII** | Personally Identifiable Information |
| **PO** | Purchase Order |
| **POD** | Proof of Delivery |
| **PSA** | Professional Services Automation |
| **PW / PD** | Person-week / person-day |
| **PWA** | Progressive Web Application |
| **RAMC** | Residential Annual Maintenance Contract |
| **RBAC** | Role-Based Access Control |
| **RFQ** | Request for Quotation |
| **RG-nn** | Register governance rule |
| **RJSC** | Registrar of Joint Stock Companies and Firms |
| **RMA** | Return Merchandise Authorisation |
| **RMM** | Remote Monitoring and Management |
| **Rnn** | User role identifier |
| **RPO / RTO** | Recovery Point Objective / Recovery Time Objective |
| **RSK-nnn** | Risk identifier |
| **RSO-nn** | Respondent security obligation |
| **RTV** | Return to Vendor |
| **SAML** | Security Assertion Markup Language |
| **SAST / DAST** | Static / Dynamic Application Security Testing |
| **SLA** | Service Level Agreement |
| **SOD-nn** | Segregation-of-duties control identifier |
| **SOP** | Standard Operating Procedure |
| **T0–T5** | Data isolation tier |
| **TAT** | Turnaround Time |
| **TCO** | Total Cost of Ownership |
| **TDS** | Tax Deducted at Source |
| **TIN** | Taxpayer Identification Number |
| **UAT** | User Acceptance Testing |
| **VAT** | Value Added Tax |
| **VROOM** | Vehicle Routing Open-source Optimisation Machine |
| **Wn** | Delivery wave (W1–W9) |
| **WCAG 2.1 AA** | Web Content Accessibility Guidelines, level AA |
| **WIP** | Work In Progress |

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 17 March 2026 | 1000FiX Services Limited | Initial RFP release — 11 modules, 6 portals, ~405 requirements, 18 months, $150K–350K |
| **2.0** | **13 August 2026** | **1000FiX Services Limited** | **Re-baselined against the v2.0 specification set. Scope restated to 67 modules in 11 categories, 12 portals, 2,930 measured requirements, 225 entities, 47 integrations, 101 NFRs, 14 revenue streams, 9 waves over 36 months. Repositioned from product selection to build-and-integrate against a specified reference architecture (Odoo 19 CE + OCA + open source + custom), with a permitted alternative-architecture response. Regulatory position corrected — Digital Security Act 2018 replaced by the Cyber Security Ordinance 2025, and the Personal Data Protection Act 2026 added in full with split-residency data architecture. Budget envelope restated to $690K–1,150K on measured effort of 1,513 person-weeks. Evaluation matrix rebuilt for an implementation-partner model. New Part E discloses all open audit findings, open decisions, Critical risks, assumptions and constraints.** |

---

**END OF DOCUMENT**

---

*This RFP is the property of 1000FiX Services Limited. All rights reserved.*

*1000FiX Services Limited*
*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: +880 9644-300600 | Email: info@1000fix.com*
*Website: https://1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
