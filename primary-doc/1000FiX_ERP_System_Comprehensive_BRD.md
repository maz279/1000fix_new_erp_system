---
id: 1000FIX-ERP-BRD-2026-002
title: Business Requirements Document — Enterprise Resource Planning System & Digital Platform Suite (v2.0 Expanded Scope)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
supersedes: 1000FIX-ERP-BRD-2026-001 (v1.0, 17 March 2026)
derived_from: 1000FIX-ERP-RFP-2026-002 (RFP v2.0, 13 August 2026)
owner: Chief Technology Officer, 1000FiX Services Limited
---

# BUSINESS REQUIREMENTS DOCUMENT (BRD)

# Enterprise Resource Planning System & Digital Platform Suite

# 67 Modules · 11 Categories · 12 Portals · 36 Months

## 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Business Requirements Document — ERP System & Digital Platform Suite (v2.0 Expanded Scope) |
| **Issuing Organisation** | 1000FiX Services Limited |
| **Document Version** | 2.0 |
| **Date** | 13 August 2026 |
| **BRD Reference Number** | 1000FIX-ERP-BRD-2026-002 |
| **Supersedes** | 1000FIX-ERP-BRD-2026-001 (v1.0, 17 March 2026) |
| **Governing Document** | **1000FIX-ERP-RFP-2026-002** — Request for Proposal v2.0, 13 August 2026 |
| **Document Owner** | Chief Technology Officer |
| **Prepared By** | Business Analysis Team, 1000FiX Services Limited |
| **Methodology** | IIBA BABOK® v3 |
| **Classification** | CONFIDENTIAL — Internal Use Only |

---

**CONFIDENTIALITY NOTICE**

This Business Requirements Document is the confidential property of 1000FiX Services Limited. It
is intended solely for use by 1000FiX internal stakeholders and by the implementation partner
selected under RFP 1000FIX-ERP-RFP-2026-002. It must not be disclosed to third parties without
prior written consent. A Non-Disclosure Agreement must be executed before this document or the
underlying module specification set is released to any external party.

---

## DOCUMENT AUTHORITY AND PRECEDENCE

**This BRD is derived in full from RFP v2.0 (1000FIX-ERP-RFP-2026-002).** Every scope figure,
module, portal, requirement count, non-functional target, business rule, risk, assumption,
constraint, dependency, decision, wave, gate criterion, KPI and cost figure in this document is
traceable to that RFP and, through it, to the module specification set held in
`1000fix_ERP_Module/`.

| Precedence | Document | Governs |
|---|---|---|
| **1** | `02_Architecture/02-02_Module_Catalogue_Master_Register.md` | Module identity, code, category, ownership, priority, wave |
| **2** | Module specification files (`03_Modules/**/M*.md`) | Functional and technical requirement detail |
| **3** | Cross-cutting specifications (`05-01` … `05-06`) | Requirements register, data model, integrations, roles, business rules, NFRs |
| **4** | **RFP v2.0 (1000FIX-ERP-RFP-2026-002)** | Commercial terms, procurement, evaluation, contractual obligations |
| **5** | **This BRD** | Business rationale, objectives, stakeholder needs, process design, benefit case, acceptance |

Where this BRD and the RFP disagree on a **commercial or procurement** term, the RFP prevails.
Where this BRD and the module specification set disagree on a **functional or technical**
requirement, the specification set prevails. Any discrepancy discovered must be raised as a change
request under §21.8.

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 10 March 2026 | Business Analysis Team | Initial draft — sections 1–5 |
| 0.5 | 14 March 2026 | Business Analysis Team | Added sections 6–12 |
| 0.9 | 16 March 2026 | Business Analysis Team | Added sections 13–22, full review |
| 1.0 | 17 March 2026 | CTO | Final v1.0 issued — 11 modules, 6 portals, ~190 catalogued requirements, 18 months, $150K–350K |
| **2.0** | **13 August 2026** | **Business Analysis Team / CTO** | **Complete re-baseline against RFP v2.0. Scope restated to 67 modules in 11 categories, 12 portals, 2,930 measured functional requirements, 225 data entities, 47 integrations, 101 non-functional requirements, 14 revenue streams, 9 waves over 36 months. Business objectives expanded from 10 to 18. Stakeholder register expanded from 20 to 46 roles. Business rules restated on the v2.0 catalogue with hard/override/soft/computed classification. Regulatory position corrected — Digital Security Act 2018 replaced by Cyber Security Ordinance 2025; Personal Data Protection Act 2026 added in full with split-residency data architecture. Investment restated to $690K–1,150K on measured effort of 1,513 person-weeks. New §22 automation catalogue and §23 disclosed open items.** |

---

## DOCUMENT APPROVALS

| Role | Name | Decision | Signature | Date |
|---|---|---|---|---|
| Chief Executive Officer (Project Sponsor) | | Approve / Approve with conditions / Reject | | |
| Chief Technology Officer | | | | |
| Chief Financial Officer | | | | |
| Chief Commercial Officer | | | | |
| Service Operations Director | | | | |
| HR Director | | | | |
| Quality Manager | | | | |
| Implementation Partner — Programme Manager | | | | |

**Conditions of approval to be recorded here:**

---

## HOW THIS DOCUMENT DIFFERS FROM VERSION 1.0

| Dimension | BRD v1.0 (Mar 2026) | **BRD v2.0 (Aug 2026)** | Change |
|---|---|---|---|
| ERP modules | 11 | **67 in 11 categories** | +56 |
| Portals & applications | 6 | **12** | +6 |
| Catalogued business requirements | ~190 (BRD) / ~405 (RFP) | **2,930 measured functional requirements** | +~2,525 |
| Business objectives | 10 (BO-01…BO-10) | **18 (BO-01…BO-18)** | +8 |
| Revenue streams supported | 5 | **14** | +9 |
| Stakeholder roles modelled | 20 | **38 registered, 46 in use** | +26 |
| Data entities | ~14 named / ~40 total | **225** | +185 |
| Business rule domains | 6 | **11** | +5 |
| Integrations | 15 | **47** | +32 |
| Non-functional requirements | 30 | **101** | +71 |
| Delivery horizon | 18 months, 6 phases | **36 months, 9 waves** | +18 months |
| Build effort | not stated | **1,513 person-weeks measured** | — |
| 3-year investment | $150K–350K | **$690K–1,150K** | +$540K–800K |
| Annual benefit at steady state | BDT 368 lac (~$335K) | **BDT 876 lac (~$797K)** | +BDT 508 lac |
| Governing data protection law | Digital Security Act 2018 | **Personal Data Protection Act 2026** + Cyber Security Ordinance 2025 | Corrected — DSA 2018 repealed twice |
| Data residency | Single region (Singapore) | **Split residency** — Bangladesh-resident store for sensitive personal data | Structural |
| Automation target | 70% | **85%** | +15 pts |

**No v1.0 requirement has been deleted.** Every v1.0 requirement is carried into the v2.0
register; four are formally superseded and are listed in §23.4.

---

## TABLE OF CONTENTS

**Part A — Why**
1. [Executive Summary](#1-executive-summary)
2. [Business Context & Background](#2-business-context--background)
3. [Business Objectives](#3-business-objectives)
4. [Project Scope](#4-project-scope)
5. [Stakeholder Analysis](#5-stakeholder-analysis)

**Part B — From What, To What**
6. [Current State Analysis (As-Is)](#6-current-state-analysis-as-is)
7. [Future State Vision (To-Be)](#7-future-state-vision-to-be)

**Part C — What Is Required**
8. [Business Requirements — 67 Modules in 11 Categories](#8-business-requirements--67-modules-in-11-categories)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Business Rules](#10-business-rules)
11. [Data Requirements](#11-data-requirements)
12. [Business Process Flows](#12-business-process-flows)
13. [Use Cases](#13-use-cases)
14. [Integration Requirements](#14-integration-requirements)

**Part D — Conditions, Constraints & Consequences**
15. [Assumptions](#15-assumptions)
16. [Constraints](#16-constraints)
17. [Dependencies](#17-dependencies)
18. [Risk Register](#18-risk-register)
19. [Cost-Benefit Analysis & ROI](#19-cost-benefit-analysis--roi)

**Part E — How Success Is Judged**
20. [Acceptance Criteria & KPIs](#20-acceptance-criteria--kpis)
21. [Implementation Approach & Governance](#21-implementation-approach--governance)
22. [Automation Catalogue](#22-automation-catalogue)
23. [Disclosed Open Items & Known Defects](#23-disclosed-open-items--known-defects)
24. [Appendices](#24-appendices)

---
---

# PART A — WHY

---

## 1. EXECUTIVE SUMMARY

### 1.1 The Business Problem

1000FiX Services Limited is Bangladesh's largest and only ISO 9001:2015 certified after-sales
service provider, operating 51+ service centres across all 8 administrative divisions with 500+
employees serving 250,000+ customers monthly. Despite that market position, the Company's
operational infrastructure is critically fragmented — and the fragmentation is now compounding.

**The original problem, unchanged since March 2026:**

- **No unified system.** Service orders, inventory, finance, HR and customer data live in
  disconnected spreadsheets and standalone tools.
- **Manual processes dominate.** Only ~20% of routine operational work is automated. Technician
  dispatch, warranty claims and invoicing are all manual.
- **Zero real-time visibility.** Management cannot see live operational status across 51+
  locations; decisions are made on data that is days old.
- **Scalability ceiling.** Current processes physically cannot support the Company's growth
  ambitions.
- **Customer experience gap.** No self-service, no real-time tracking, no automated notification.

**The problem that has become visible since:**

The Company has committed — in its board-approved business plan, its Service App scope of work and
its portal technology roadmap — to operating **fourteen distinct revenue streams**. The ERP
approved in March 2026 could run **five** of them. The remaining nine are not new business ideas;
they are **existing commercial commitments with no system of record**:

managed IT services · equipment rental · data recovery · data backup subscriptions · refurbished
device resale · trade-in · e-waste recycling · marketplace commission and settlement · advertising
and lead placement.

Running those nine on spreadsheets alongside a modern ERP would recreate, within three years,
exactly the fragmentation the ERP was approved to remove.

**Quantified cost of the current state: BDT 2.55 – 4.0 crore per year** (§6.4).

### 1.2 The Proposed Solution

1000FiX will implement a **comprehensive Enterprise Resource Planning system** — **67 modules
across 11 categories** — surfaced through a **twelve-portal digital platform suite**, delivered in
**9 waves over 36 months**, on an open-source reference architecture (Odoo 19 Community Edition +
OCA + self-hosted open source + custom development) carrying **zero core licence cost**.

| Category | Modules | Requirements | Effort (PW) | Accountable Executive |
|---|---:|---:|---:|---|
| **A** — Service Delivery & Operations | 7 | 362 | 206 | Service Operations Director |
| **B** — Customer Engagement & Experience | 7 | 320 | 148 | Chief Commercial Officer |
| **C** — Commercial, Pricing & Revenue | 9 | 494 | 262 | Chief Commercial Officer |
| **D** — Circular & Asset-Based Business | 3 | 109 | 60 | Corporate Services / Retail Ops Head |
| **E** — Supply Chain & Inventory | 6 | 235 | 119 | Supply Chain Director |
| **F** — Asset, Equipment & Facilities | 5 | 232 | 114 | Service Ops Director / CTO |
| **G** — Finance & Treasury | 8 | 333 | 185 | Chief Financial Officer |
| **H** — People & Workforce | 7 | 310 | 124 | HR Director |
| **I** — Governance, Risk, Quality & Knowledge | 4 | 170 | 78 | Quality Manager / CFO |
| **J** — Data, Analytics & Intelligence | 4 | 146 | 97 | Chief Technology Officer |
| **K** — Platform & Technology | 7 | 219 *(5 of 7 specified)* | 120 | Chief Technology Officer |
| | **67** | **2,930 measured** | **1,513** | |

*Counted by direct enumeration of the module specification files on 13 August 2026. Two Category K
specifications (M66, M67) remain outstanding; their estimated 48 requirements and 25 PW bring the
projected total to ~2,978 requirements and ~1,538 PW.*

The ERP is the **system of record**. The twelve portals are **surfaces** onto it. Any business
object with a lifecycle, a financial consequence or an audit obligation is mastered in the ERP;
**portals never hold authoritative state**.

### 1.3 Strategic Alignment

| Company strategic goal | How this programme delivers it |
|---|---|
| Operate all 14 committed revenue streams | Every stream has an owning module from the wave it launches (§4.2) |
| 87% revenue growth within 18 months of the v1.0 scope completing | BO-09; capacity constraints removed by Waves 1–4 |
| 85% operational automation | BO-01; 60 catalogued automations (§22) |
| 5× business scale-up capability | NFR-009, NFR-053, NFR-058 — 5 million service orders/year, 200 branches |
| Maintain ISO 9001:2015 certification | BO-10, M23; ISO evidence executed in-system from Wave 5 |
| Full Bangladesh regulatory compliance | BO-10; M51 tax, M56 payroll, M33/M60 data protection |
| Expansion to a second country | BO-18; M65 country-pack framework, Wave 9 |

### 1.4 Investment Summary

| Category | 3-Year Total |
|---|---|
| Software licensing (L6 commercial components only; ERP core is $0) | $0 – $36,000 |
| Implementation & custom development | $525,000 – $855,000 |
| Infrastructure & hosting | $52,000 – $96,000 |
| Third-party APIs | $41,000 – $95,000 |
| Training & change management | $35,000 – $65,000 |
| Support & maintenance (Years 2–3) | $60,000 – $130,000 |
| **Total 3-Year TCO** | **$690,000 – $1,150,000** |

> **This figure has been restated and the restatement is disclosed, not buried.** The approved
> business case modelled implementation against **834 person-weeks across 30 modules**. Direct
> enumeration of the completed specifications returns **1,513 person-weeks across 67 modules** —
> approximately **1.8× the effort of the approved plan**. The Steering Committee decision on
> whether to fund, phase or cut is **open as decision D-14** (§23.3). See §19.

### 1.5 Expected Return

| Scenario | 3-Year Benefit | 3-Year Cost | Net | ROI | Payback |
|---|---:|---:|---:|---:|---|
| Conservative | $1.24M | $1.15M | $90K | 8% | 32 months |
| **Base case** | **$1.96M** | **$0.92M** | **$1.04M** | **113%** | **22 months** |
| Optimistic | $2.61M | $0.69M | $1.92M | 278% | 15 months |

Annual steady-state benefit at Year 3+ is modelled at **BDT 876 lac (~USD 797K)** in the base
case, of which **BDT 334 lac derives from the nine new revenue streams** that cannot be operated
at all under the v1.0 scope.

Benefit realisation is deliberately lagged: new business lines contribute nothing until they go
live, so the first two years of the v2.0 case closely track the v1.0 case. **The step change
occurs in Year 3.**

### 1.6 Document Purpose

This BRD defines the complete business requirements for the programme in sufficient detail to:

1. Give the Board and Steering Committee the business case on which to approve, phase or descope
2. Serve as the business-side specification against which the implementation partner delivers
3. Establish the acceptance criteria for each of the nine wave gates
4. Provide the baseline for scope management and change control across a 36-month programme
5. Trace every requirement to a named business objective, a named owner and a testable outcome

### 1.7 Critical Success Factors

Stated plainly, because a risk register can obscure the obvious. Each is addressed in §18.

1. **The business must free up its people.** Software can be built; it cannot be accepted, tested,
   trained or adopted without the business. **UAT capacity, not developer capacity, paces this
   programme.** *(RSK-001, Critical)*
2. **Technicians must accept the app.** Four hundred people in the field decide whether this
   programme works. If the app is slower than paper, they will not use it, and dispatch,
   inventory, invoicing, warranty and quality all degrade. *(RSK-008, Critical)*
3. **Scope must not grow continuously.** Thirty-six months is long enough for the business to
   change twice. *(RSK-002, Critical)*
4. **The marketplace must not launch before the tax and liability model is settled.**
   *(RSK-022, Critical)*
5. **Benefits must be measured.** If baselines are not captured before each wave, no benefit can be
   claimed honestly and the business case becomes decoration.

**None of these is a technology problem.**

---

## 2. BUSINESS CONTEXT & BACKGROUND

### 2.1 Company Overview

| Attribute | Details |
|---|---|
| **Legal name** | 1000FiX Services Limited |
| **Founded** | 29 August 2017 |
| **Head office** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |
| **Hotline** | 16743 (16 + "Fix" on the Bangla keypad) |
| **Phone** | +880 9644-300600 |
| **WhatsApp** | +880 1904 095968 |
| **Website** | https://1000fix.com |
| **Certification** | ISO 9001:2015 — Bangladesh's first and only ISO-certified IT service provider |
| **Service network** | 51+ service centres across all 8 administrative divisions |
| **Employees** | 500+, including 200–400 field technicians |
| **Customers served** | 250,000+ per month |
| **Brand partnerships** | 17+ authorised warranty service agreements *(figure under verification — §23.8)* |

### 2.2 Industry Context

The Bangladesh after-sales service and electronics repair market is in rapid transition:

- Consumer electronics market exceeding USD 2.5 billion annually
- Smartphone penetration past 50 million active users
- Air-conditioner penetration growing at ~18% per year in urban households
- Demand for professional after-sales service rising with premium device ownership
- Brand manufacturers increasingly relying on third-party authorised service networks rather than
  maintaining their own infrastructure in developing markets

1000FiX is uniquely positioned: the only ISO 9001:2015 certified provider in the country, the
broadest brand authorisation portfolio and the largest geographic footprint. **That certification
is not symbolic** — it commits the Company to documented, traceable quality processes, which
creates internal pressure to systematise operations that spreadsheets cannot satisfy.

### 2.3 Business Model — Fourteen Revenue Streams

| # | Revenue stream | In v1.0 ERP scope | Owning module | First live |
|---|---|:--:|---|:--:|
| 1 | Authorised brand warranty service | ✓ | M09 | W4 |
| 2 | Out-of-warranty paid repair | ✓ | M01 / M31 | W1–W2 |
| 3 | AMC / RAMC maintenance contracts | ✓ | M08 | W4 |
| 4 | Warranty extension & protection products | ✓ | M09 | W4 |
| 5 | Spare parts & accessories | ✓ | M15 / M38 | W2 / W7 |
| 6 | **Corporate managed IT services (MSP)** | — | M05 | W5 |
| 7 | **Equipment rental / Equipment-as-a-Service** | — | M13 | W6 |
| 8 | **Data recovery** | — | M06 | W6 |
| 9 | **Data backup & archival subscriptions** | — | M06 / M39 | W6 |
| 10 | **Refurbished device resale** | — | M14 | W6 |
| 11 | **Trade-in / exchange margin** | — | M14 | W6 |
| 12 | **E-waste recycling & material recovery** | — | M18 | W8 |
| 13 | **Marketplace commission & settlement** | — | M12 | W7 |
| 14 | **Advertising, boost & lead placement** | — | M12 / M35 | W7 |

**Streams 1–5 are approximately today's revenue.** The warranty service stream is particularly
critical: it involves structured financial relationships with 17+ international brands, and
manual claim processing currently causes **15–20% revenue leakage** with 30–90 day submission
delays and 60–120 day reimbursement cycles.

**Streams 6–14 are the strategic case for this programme.** They contribute nothing today because
no system can run them.

### 2.4 Service Delivery Infrastructure

#### 2.4.1 Service categories

| Category | Coverage |
|---|---|
| **IT equipment** | Laptops and notebooks (Level 1–3, including motherboard-level), desktops (brand and clone), MacBook and Apple products, servers, printers/photocopiers/plotters, monitors and displays, projectors, UPS, routers and networking, CCTV and surveillance, Microsoft Surface |
| **Home appliances** | Air conditioning (installation, jet wash, hydraulic service, dismantling, gas refill, leakage repair, servicing), refrigerator, television, washing machine, microwave and oven, geyser/water heater, treadmill, combination packages |
| **Mobile & tablet** | Samsung, Xiaomi, Huawei, Honor and others; tablets; speakers; warranty and out-of-warranty |
| **New service lines (v2.0)** | Managed IT services and 24/7 remote support; data recovery (HDD, SSD, RAID, USB, memory card, mobile, email/database); data backup and archival (cloud, on-site, hybrid, CDP); certified data destruction; equipment rental across eight asset categories; trade-in, refurbishment, grading and resale; e-waste collection, recycling and certified disposal; marketplace intermediation |

#### 2.4.2 Service delivery modes

1. **Walk-in** at any of 51+ service centres
2. **On-site / home service** — technician dispatched to the customer
3. **Pick & drop** — collection, workshop repair, return delivery
4. **Workshop / depot** — bench repair with WIP and bench management *(new in v2.0 — M31)*
5. **Remote support** — remote diagnostics, software support, managed monitoring *(expanded — M05)*

#### 2.4.3 Value-added programmes

Privilege Program (Silver / Gold / Diamond) · Residential AMC (RAMC — 6 packages) · Commercial AMC
· IT Infrastructure AMC · Healthcare Equipment AMC with mandatory calibration · Specialty Equipment
AMC · Managed Service Contracts (6 types) · Mobile & Appliance Service Contracts (5 types) ·
Warranty extension and protection products (7 families) · Partner Alliance Program · equipment
rental · device exchange and trade-in · referral programme.

**Fourteen contract product families and seven protection product families must be modelled
without code change** (§8.5). This is why M08 is specified as a contract *engine*, not an AMC
table.

### 2.5 Why ERP — Now

| # | Driver | Consequence of delay |
|---|---|---|
| 1 | **Scale pressure** | 51+ locations cannot be coordinated through spreadsheets; coordination failures are increasing |
| 2 | **Revenue leakage** | 15–20% of warranty revenue is unclaimed or submitted beyond brand deadlines |
| 3 | **ISO 9001:2015 obligation** | Documented, traceable processes are impossible without a system of record |
| 4 | **Nine committed revenue streams with no system** | Every quarter of delay is a quarter those lines cannot scale |
| 5 | **Concurrent portal platform** | The Next.js portal platform is being built now and needs a back-office engine |
| 6 | **PDPA 2026 enforcement from ~13 May 2027** | Enforcement lands inside Wave 4. Consent, notice, data-subject rights and breach notification must be system-enforced by then, with penalties to BDT 50 lakh |
| 7 | **Competitive threat** | Well-funded competitors are investing in digital capability; scale advantage erodes without operational excellence |
| 8 | **Growth ambition** | Board-approved +87% revenue target requires capacity only automation can provide |

### 2.6 Relationship to Other 1000FiX Programmes

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     1000FiX DIGITAL ESTATE (v2.0)                            │
│                                                                              │
│   ┌────────────────────────┐        ┌──────────────────────────────┐        │
│   │  CORPORATE WEBSITE     │        │  EXPERIENCE LAYER            │        │
│   │  (Next.js + Payload)   │◄──────►│  12 portals & applications   │        │
│   │  SEPARATE PROGRAMME    │        │  P01 … P12   IN SCOPE        │        │
│   └───────────┬────────────┘        └──────────────┬───────────────┘        │
│               │      REST / JSON-2 / GraphQL / Webhooks / Events            │
│               └──────────────────┬─────────────────┘                        │
│                                  ▼                                          │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │           1000FiX ERP v2.0 — SYSTEM OF RECORD    IN SCOPE            │  │
│   │  67 modules · 11 categories · 2,930 requirements · 225 entities      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                  │                                          │
│   ┌──────────────────────────────▼───────────────────────────────────────┐  │
│   │  DATA & INTELLIGENCE PLATFORM                       IN SCOPE         │  │
│   │  PostgreSQL 16 · TimescaleDB · ClickHouse · Metabase · MLflow        │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Boundary rule.** The ERP owns *state and truth*; the portals own *experience and reach*.

**Constraint CON-03:** the Next.js 15 + Payload CMS 3 portal platform **cannot be replaced**. The
ERP integrates with it under a versioned, contract-tested API agreement (§14.4).

---

## 3. BUSINESS OBJECTIVES

Each objective is SMART, owned by a named executive, measurable against a captured baseline, and
traced to the modules that deliver it. **BO-01 to BO-10 are carried forward from v1.0 with raised
targets. BO-11 to BO-18 are new and correspond to the nine new revenue streams and the platform
capabilities that make them possible.**

| ID | Business objective | Metric | Baseline | Target | By month | Owner | Modules |
|---|---|---|---|---|:--:|---|---|
| **BO-01** | Automate the end-to-end service order lifecycle | % processed without manual intervention | 20% | **85%** *(was 70%)* | M34 | Ops Director | M01, M02, M20 |
| **BO-02** | Maximise field technician productivity | Jobs per technician per day | 4–5 | **8–9** *(was 7–8)* | M26 | Ops Director | M02, M26 |
| **BO-03** | Achieve inventory accuracy across all locations | Accuracy rate | 75% | **98%+** | M18 | Inventory Manager | M15 |
| **BO-04** | Recover all eligible warranty revenue | % claims submitted within 72 hours | ~50% at 30–90 days | **95%+** | M18 | Finance Director | M09 |
| **BO-05** | Improve customer satisfaction and reduce turnaround | CSAT · TAT | 3.8/5 · unmeasured | **4.7/5** · <24 h IT, <4 h appliance | M22 | Customer Service Manager | M01, M07, M27, M34 |
| **BO-06** | Compress the financial close | Days to close | 15–20 | **≤ 3 days** *(was ≤5)* | M20 | CFO | M19, M20 |
| **BO-07** | Give management real-time visibility | Time to branch performance data | Days | **Real-time** | M18 | CEO | M25, M62 |
| **BO-08** | Grow contract subscriptions | Renewal rate · contract base | 60% · baseline | **88% · 2.5×** | M30 | CCO | M08, M10, M39 |
| **BO-09** | Remove capacity constraints on growth | Annual revenue growth | Baseline | **+87% over 18 months post-W4** | M36 | CEO | All |
| **BO-10** | Full Bangladesh regulatory compliance | Compliance findings · late filings | Manual, error-prone | **Zero** | M18 | CFO / HR Director | M19, M51, M56, M23, M33, M60 |
| **BO-11** | **Build managed services into a material revenue line** | MSP revenue share | 0% | **≥ 12% of revenue** | M34 | Corporate Services Head | M05, M08 |
| **BO-12** | **Scale delivery capacity beyond owned headcount** | Marketplace share of job volume | 0% | **≥ 25%** | M34 | CCO | M12 |
| **BO-13** | **Establish rental as a profitable asset business** | Fleet utilisation · gross margin | n/a | **68% · 55%** | M32 | Corporate Services Head | M13 |
| **BO-14** | **Build a circular device business** | Refurbished units/yr · margin | 0 | **12,000 · 22%** | M34 | Retail Operations Head | M14, M18 |
| **BO-15** | **Make competency an enforced control** | Claims rejected for uncertified technician | Unknown | **Zero** | M24 | Quality Manager | M22 |
| **BO-16** | **Bring every customer conversation into the system** | Conversations captured | ~0% | **100%** | M20 | Customer Service Manager | M27 |
| **BO-17** | **Make decisions on live data** | Manual reporting packs | 100% | **Zero** | M34 | CTO | M25, M62 |
| **BO-18** | **Be ready to operate in a second country** | Time to stand up a country pack | Not possible | **≤ 12 weeks** | M36 | CTO | M65 |

### 3.1 Objective Dependency

Objectives are not independent. BO-09 (growth) depends on BO-01, BO-02 and BO-12 delivering
capacity. BO-11, BO-13 and BO-14 depend on BO-10 (compliance) and on the Category G finance
modules being live first. BO-17 depends on every module instrumenting its KPIs (DoD-09).

```
BO-10 Compliance ──┐
BO-01 Automation ──┼──► BO-09 Growth ◄── BO-12 Marketplace capacity
BO-02 Productivity ┘         ▲
                             ├── BO-11 MSP revenue
BO-03 Inventory ─────────────┤   BO-13 Rental margin
BO-04 Warranty recovery ─────┤   BO-14 Circular business
BO-05 CSAT ◄── BO-16 Conversations   │
BO-06 Close ─────────────────┘       │
BO-07 Visibility ◄── BO-17 Live data ┘
BO-08 Contract base
BO-15 Competency control ──► protects BO-04
BO-18 Country readiness ──► enables growth beyond Bangladesh
```

### 3.2 Benefit Ownership

Each benefit has a named owner accountable for realising it. **A KPI without a signed-off baseline
cannot claim a benefit.** Baselines are captured before the relevant wave begins.

| Benefit | Owner | Measured from |
|---|---|:--:|
| Warranty revenue recovery | Finance Director | W4 |
| Technician productivity | Ops Director | W2 |
| Inventory cost reduction | Inventory Manager | W3 |
| Administrative labour savings | Ops Director | W3 |
| Customer retention | CCO | W4 |
| Contract renewal uplift | CCO | W5 |
| Close & cash flow | CFO | W3 |
| MSP revenue | Corporate Services Head | W6 |
| Rental margin | Corporate Services Head | W7 |
| Refurbishment margin | Retail Operations Head | W7 |
| Marketplace revenue | CCO | W8 |
| Data services revenue | Technical Services Head | W7 |
| E-waste recovery | Quality Manager | W9 |
| Pricing margin uplift | CCO | W8 |

---

## 4. PROJECT SCOPE

### 4.1 Scope Summary

| Deliverable | Scale |
|---|---|
| ERP system of record | **67 modules** across 11 categories |
| Digital platform suite | **12 portals and applications** |
| Functional delivery | **2,930 measured functional requirements** (~2,978 projected) |
| Non-functional compliance | **101 non-functional requirements** |
| Integration | **47 external integrations** plus the portal platform contract |
| Data model | **225 entities** with dimensional context, residency classification and audit |
| Access model | **38 registered roles** (46 in use), 6 isolation tiers, 30 SoD controls, field-level permissions |
| Business rules | **11 rule domains**, hard/override/soft/computed classification |
| Automation | **60 catalogued automations**, 85% of routine work by Wave 8 |
| Data migration | 11 source domains; 800,000+ transactional records; 3+ years of financial history |
| Delivery | **9 waves over 36 months**, each with a formal gate |
| Adoption | 500–900 internal users across 51+ locations; 250,000+ monthly external users; 1,000–3,000 external party users |

### 4.2 In Scope — The 67 Modules

> **Reconciliation note — read before adding the columns.** Two different measurements appear in
> the tables below and **they do not sum to each other**. This is inherited from the source
> register and is disclosed rather than smoothed over.
>
> | Figure | Basis | Where it comes from |
> |---|---|---|
> | **Category totals** (in each heading) | **Measured** by direct enumeration of the module specification files on 13 August 2026 | Register `02-02` §3 |
> | **Per-module requirement and effort figures** (in each row) | **Measured for Categories A, B and H; estimated for C, D, E, F, G, I, J, K** | Register `02-02` §2 |
>
> **Consequence.** In the eight estimated categories the per-module rows sum *below* the measured
> category total, because the original estimates under-predicted statutory- and master-data-dense
> work. The variance is known and explained:
>
> | Category | Per-module rows sum to | Measured total | Variance |
> |---|---:|---:|---:|
> | A — Service Delivery | 389 *(includes 28 allocated-but-unused IDs — §23.1.2)* | **362** | −7% |
> | B — Customer Engagement | 320 | **320** | 0% |
> | C — Commercial | 356 *(est.)* | **494** | **+39%** |
> | D — Circular | 109 *(est.)* | **109** | 0% |
> | E — Supply Chain | 192 *(est.)* | **235** | **+22%** |
> | F — Asset & Facilities | 134 *(est.)* | **232** | **+73%** |
> | G — Finance & Treasury | 258 *(est.)* | **333** | **+29%** |
> | H — People & Workforce | 310 | **310** | 0% |
> | I — Governance & Quality | 118 *(est.)* | **170** | **+44%** |
> | J — Data & Analytics | 130 *(est.)* | **146** | **+12%** |
> | K — Platform (5 of 7 written) | 220 *(est., 7 modules)* | **219** *(5 modules)* | — |
>
> **Use the measured category totals for planning, funding and contracting.** Per-module rows in
> the eight estimated categories indicate relative size only and **must not be used for
> contractual commitment** (register rule RG-05). They are re-baselined at each wave start.

#### Category A — Service Delivery & Operations (7 modules · **362 measured** reqs · 206 PW)

| ID | Module | Code | Pri | Wave | Reqs | PW | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M01 | Service Request & Order Management | `SRM` | **P0** | W1–W2 | 88 | 46 | Owns the service order — the master record of every customer service need, from any channel, for any business line |
| M31 | Workshop & Depot Repair Management ★ | `WSR` | P1 | W2 | 58 | 30 | Owns in-house bench repair: workshop routing, Level 1/2/3 repair, RMA-in, component-level work, test and burn-in |
| M02 | Field Service & Dispatch Management | `FSM` | **P0** | W2 | 74 | 40 | Decides who does field work, when and in what order; tracks and executes it on mobile |
| M03 | Service Logistics & Reverse Logistics | `LOG` | P1 | W3 | 42 | 22 | Moves devices, parts and assets between customers, branches, workshops, vendors and recyclers with unbroken custody |
| M04 | Branch & Front-Desk Operations | `FRD` | P1 | W1 | 32 | 13 | Runs the counter at 51+ service centres: queue, intake, handover, cash, shift discipline |
| M05 | Remote Support & Managed Services | `RMS` | P1 | W5 | 61 | 37 | Delivers remote assistance and contracted managed IT services with monitoring, alerting and SLA reporting |
| M06 | Data Services & Secure Data Handling | `DTS` | P2 | W6 | 34 | 18 | Delivers data recovery, backup subscriptions, migration and certified destruction under controlled custody |

#### Category B — Customer Engagement & Experience (7 modules · **320 measured** reqs · 148 PW)

| ID | Module | Code | Pri | Wave | Reqs | PW | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M33 | Customer & Party Master Management ★ | `CPM` | **P0** | W1 | 52 | 24 | The single authoritative record of every party — customer, corporate group, household, dealer, government body — with identity, hierarchy, addresses and consent |
| M07 | CRM, Sales Pipeline & Account Management | `CRM` | P1 | W1 / W4 | 46 | 22 | Leads, opportunities, account plans, dedicated account managers and quarterly business reviews |
| M10 | Loyalty, Membership & Rewards | `LOY` | P1 | W2 | 44 | 18 | Privilege tiers, points, wallet, vouchers, referral mechanics and the loyalty liability |
| M34 | Customer Experience, Feedback & Complaints ★ | `CXM` | P1 | W4 | 42 | 17 | CSAT, NPS, CES, the closed feedback loop, and the customer-facing complaint process |
| M27 | Omnichannel Contact Centre & Communications | `CCE` | P1 | W4 † | 58 | 32 | Every inbound and outbound conversation across voice, chat, WhatsApp, email, SMS and social — and all notification delivery |
| M32 | Conversational AI & Virtual Assistant ★ | `CAI` | P1 | W4 ‡ | 38 | 18 | The Bengali-first AI assistant that handles first-line conversations and performs authenticated actions |
| M35 | Marketing, Campaigns & Demand Generation ★ | `MKT` | P2 | W5 | 40 | 17 | Campaign planning and execution, journey orchestration, budget and marketing attribution |

> **† Sequencing decision required (Q-05).** M27's **notification service** should move from Wave
> 4 to Wave 1 or Wave 2. Every module from Wave 1 onward needs to notify customers; if M27 arrives
> at W4, each earlier module builds its own send path — recreating the fragmentation this
> programme exists to remove. **Business decision required before Wave 1 build.**
>
> **‡ Dependency decision required (Q-01).** M32 depends on M61 Knowledge Management, scheduled
> two waves later (W6). Either M61 core content moves to W4, or M32 launches with a reduced intent
> scope.

#### Category C — Commercial, Pricing & Revenue (9 modules · **494 measured** reqs · 262 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M37 | Product & Service Catalogue Management ★ | `CAT` | **P0** | W1 | 34 | 18 | The definition of everything sellable: services, kits, parts, plans, rental SKUs, refurbished grades, subscriptions — with repair bills of material |
| M11 | Pricing, Rate Cards & Dynamic Pricing | `PRC` | P1 | W3 / W7 | 36 | 20 | Every price in the business: rate cards, price books, customer-specific pricing, discount governance, dynamic pricing |
| M36 | Quotation, Estimation & Tender Management ★ | `QTE` | P1 | W3 | 32 | 17 | Estimates, quotations, competitive bidding, corporate tenders and customer approval loops |
| M08 | Contract Lifecycle Management | `CTR` | P1 | W4 | 44 | 24 | Every agreement across **14 contract product families**: scope, entitlement, SLA, amendment, renewal, profitability |
| M09 | Warranty, Protection Plans & Claims | `WTY` | **P0** | W4 | 48 | 28 | Warranty entitlement, **seven protection-product families**, and recovery of money from 17+ brand partners |
| M39 | Subscription & Recurring Revenue ★ | `SUB` | P1 | W4 | 30 | 17 | Recurring and usage-based billing mechanics, proration, MRR/ARR, plan changes and churn |
| M38 | E-Commerce & Digital Storefront ★ | `ECM` | P1 | W7 | 40 | 24 | Selling 1000FiX's own products and services online: catalogue browsing, cart, checkout, fulfilment, returns |
| M12 | Marketplace & Seller Ecosystem | `MKP` | P1 | W7 | 62 | 40 | The aggregator: third-party sellers, listings, job broadcast, ratings, disputes, commission and payouts |
| M40 | Partner, Channel, Alliance & Franchise ★ | `PCM` | P2 | W7 | 30 | 16 | Relationship management for brand partners, alliance partners, referral partners, resellers and franchise branches |

#### Category D — Circular & Asset-Based Business (3 modules · **109 measured** reqs · 60 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M13 | Rental & Equipment-as-a-Service | `RNT` | P2 | W6 | 44 | 25 | Rents eight asset categories with reservation, agreement, tariff, deposit, condition, damage and return |
| M14 | Trade-In, Refurbishment & Resale | `TRF` | P2 | W6 | 39 | 22 | Buys used devices, grades and refurbishes them, and resells them with controlled warranty |
| M18 | E-Waste, Recycling & Circular Economy | `ESG` | P3 | W8 | 26 | 13 | Collects end-of-life devices, certifies destruction and disposal, and recovers materials |

#### Category E — Supply Chain & Inventory (6 modules · **235 measured** reqs · 119 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M15 | Spare Parts & Inventory Management | `INV` | **P0** | W2 | 48 | 24 | Owns stock: what exists, where, in what condition, under whose ownership, and what it is worth |
| M41 | Warehouse Management ★ | `WMS` | P1 | W3 | 34 | 20 | Owns physical warehouse execution: bins, put-away, picking strategies, waves, cross-dock, cycle counting on the floor |
| M16 | Procurement & Strategic Sourcing | `PRO` | P1 | W3 | 32 | 16 | Owns buying: requisition, RFQ, purchase order, receipt, three-way match |
| M42 | Supplier Relationship & Performance ★ | `SRM2` | P1 | W4 | 26 | 13 | Owns the supplier as a relationship: qualification, contracts, scorecards, risk, development |
| M43 | Demand Planning & Replenishment ★ | `DPL` | P2 | W6 | 24 | 14 | Owns how much to hold and when to order: forecast consumption, safety stock, reorder parameters, network balancing |
| M44 | Import, Trade Compliance & Landed Cost ★ | `ITC` | P2 | W6 | 28 | 15 | Owns cross-border supply: proforma, LC, shipment, customs, duty, clearing, true landed cost |

*Code note: M42 carries `SRM2` because `SRM` is permanently allocated to M01 under register rule
RG-02. Codes are permanent and must be used exactly as allocated.*

#### Category F — Asset, Equipment & Facilities (5 modules · **232 measured** reqs · 114 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M17 | Device & Customer Asset Registry | `AST` | P1 | W2 / W8 | 34 | 18 | The identity, ownership, history and condition of every device and asset the Company touches |
| M45 | Enterprise Asset & Test Equipment ★ | `EAM` | P2 | W5 | 26 | 14 | Company-owned tools, diagnostic and test equipment: issue, custody, **calibration**, maintenance, retirement |
| M46 | Fleet & Vehicle Management ★ | `FLT` | P2 | W5 | 24 | 12 | Service vans, rider motorcycles and company vehicles: documents, servicing, fuel, drivers, telematics, cost per kilometre |
| M47 | Facility, Branch Infrastructure & Workplace ★ | `FAC` | P3 | W7 | 22 | 11 | 51+ premises: leases, utilities, maintenance, security, safety equipment, occupancy, opening and closing |
| M48 | IoT Telemetry & Predictive Maintenance ★ | `IOT` | P2 | W8 | 28 | 18 | Time-series ingestion from connected assets, health scoring, threshold alerting and failure prediction |

#### Category G — Finance & Treasury (8 modules · **333 measured** reqs · 185 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M19 | Financial Accounting & General Ledger | `FIN` | **P0** | W3 | 40 | 24 | The statutory ledger: chart of accounts, journals, periods, multi-entity, consolidation, financial statements |
| M20 | Accounts Receivable, Invoicing & Collections | `ARB` | **P0** | W3 | 36 | 20 | Customer invoicing, receipts, matching, ageing, dunning, credit notes and refunds |
| M52 | Accounts Payable & Employee Expense ★ | `APE` | P1 | W3 | 28 | 14 | Vendor invoices, three-way-matched approval, payment runs, advances, staff expense claims |
| M50 | Treasury, Cash & Banking ★ | `TRE` | P1 | W3 | 30 | 16 | Bank accounts, branch cash across 51+ counters, gateway settlement, cash-flow forecasting, LC and facilities |
| M51 | Tax & Regulatory Compliance (Bangladesh) ★ | `TAX` | **P0** | W4 | 34 | 20 | Mushak VAT, VAT sub-ledgers and returns, TDS/VDS, challans and certificates, income-tax schedules |
| M53 | Revenue Recognition, Commission & Settlement ★ | `REV` | P1 | W4 / W7 | 38 | 24 | Revenue schedules, deferral, performance obligations, commission ledgers, seller and partner payouts, escrow |
| M49 | Fixed Assets & Capital Investment ★ | `FXA` | P2 | W5 | 22 | 11 | Asset register, capitalisation, depreciation, disposal, CWIP, impairment, capital approval |
| M54 | Cost Accounting, Budgeting & FP&A ★ | `FPA` | P2 | W6 | 30 | 17 | Cost allocation, job and contract costing, budgets, variance, forecasting, business-line profitability |

#### Category H — People & Workforce (7 modules · **310 measured** reqs · 124 PW)

| ID | Module | Code | Pri | Wave | Reqs | PW | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M21 | Core HR & Employee Lifecycle | `HCM` | P1 | W5 | 46 | 18 | The employee master: personal data, contracts, organisation structure, movements, exit, self-service |
| M55 | Time, Attendance & Workforce Scheduling ★ | `WFM` | P1 | W5 | 52 | 22 | Biometric and GPS attendance, exceptions, leave, shifts, rosters and available capacity by skill and zone |
| M56 | Payroll, Benefits & Statutory Compliance ★ | `PAY` | **P0** | W5 | 54 | 26 | Gross-to-net payroll with Bangladesh tax slabs, provident fund, gratuity, BEFTN files and payslips |
| M57 | Performance, Incentives & Compensation ★ | `PIC` | P1 | W5 | 42 | 16 | Technician KPI capture, incentive schemes, appraisal, compensation review and pay transparency |
| M22 | Learning, Competency & Certification | `LMS` | P2 | W5 | 40 | 16 | Competency framework, **brand certification tracking with dispatch enforcement**, training and assessment |
| M58 | Talent Acquisition & Onboarding ★ | `TAO` | P2 | W6 | 34 | 12 | Requisition to hire: vacancies, candidates, assessment, offer, and structured onboarding to productivity |
| M59 | Health, Safety & Wellbeing ★ | `HSE` | P2 | W6 † | 42 | 14 | Incidents, near-misses, risk assessment, PPE, lone-worker safety, electrical and chemical safety, wellbeing |

> **Cross-wave build constraint (mandatory).** M22's dispatch eligibility check (FR-LMS-039) is
> consumed by M02 at assignment. **M02 goes live in W2; M22 in W5.** The interface must be built
> into M02 in W2 as a stub returning "eligible", and connected in W5. Retrofitting a blocking check
> into a live assignment path is materially riskier.
>
> **† Sequencing decision required (Q-05).** M59's mobile incident, near-miss and hazard reporting
> (FR-HSE-009, FR-HSE-011) depends only on P02 and M21, and can ship with the technician app in
> **W3** at low incremental cost. The remaining 40 requirements stay in W6.

#### Category I — Governance, Risk, Quality & Knowledge (4 modules · **170 measured** reqs · 78 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M23 | Quality Management System | `QMS` | P1 | W5 | 32 | 16 | ISO 9001:2015 operating system: policies, process register, checklists, non-conformance, CAPA, internal audit, management review |
| M60 | Governance, Risk & Compliance ★ | `GRC` | P2 | W6 | 34 | 18 | Enterprise risk register, internal control framework, controls testing, compliance obligations, legal matters, insurance, licences, **PDPA breach notification** |
| M24 | Document, Records & E-Signature | `DMS` | P1 | W3 | 28 | 15 | Every document: storage, versioning, templates, signature, retention, legal hold, disposal, evidence packs |
| M61 | Knowledge Management & Technical Library ★ | `KMS` | P2 | W6 | 24 | 13 | Repair manuals, wiring diagrams, solution articles, troubleshooting trees, tribal knowledge, brand bulletins and recall notices |

#### Category J — Data, Analytics & Intelligence (4 modules · **146 measured** reqs · 97 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M62 | Data Platform, Warehouse & Governance ★ | `DAT` | P1 | W4 / W8 | 34 | 22 | Pipelines, warehouse, dimensional model, semantic layer, data quality, lineage and the feature store |
| M25 | Business Intelligence & Reporting | `BID` | P1 | W4 | 30 | 16 | Dashboards, reports, self-service exploration, distribution, alerting and embedded analytics |
| M26 | AI/ML Services & Model Operations | `AIM` | P2 | W6–W8 | 38 | 30 | The model portfolio, training, serving, monitoring, governance and generative AI services |
| M63 | Process Automation & Workflow Orchestration ★ | `BPA` | P1 | W3 | 28 | 16 | **One platform-wide workflow engine** — cross-module workflow, approvals, business-rule execution, scheduled and event-driven automation |

#### Category K — Platform & Technology (7 modules · **219 measured** reqs across the 5 written specifications · 120 PW)

| ID | Module | Code | Pri | Wave | Reqs *(est.)* | PW *(est.)* | Business definition |
|---|---|---|:--:|:--:|---:|---:|---|
| M28 | Integration, API & Event Platform | `IPF` | **P0** | W1 | 44 | 26 | Gateway, API management, event bus, connectors, webhooks, sync protocol and integration observability |
| M29 | Identity, Access & Information Security | `SEC` | **P0** | W1 | 44 | 24 | Who is who, what they may do, and the audit trail and data protection that proves it |
| M64 | Master Data Management & Configuration ★ | `MDM` | P1 | W2 | 26 | 14 | Master data ownership, stewardship workflows, data quality rules, reference data distribution, business-rule parameters |
| M65 | Multi-Entity, Multi-Country & Localisation ★ | `GLO` | P2 | W9 | 30 | 20 | Legal entities, country packs, locale packs, currency, translation, jurisdiction isolation, expansion readiness |
| M66 | Internal IT Service Management ★ | `ITS` | P2 | W6 | 22 *(est.)* | 11 *(est.)* | The Company's own IT: employee helpdesk, internal asset and licence management, change and incident management. **Specification outstanding — §23.1** |
| M30 | Platform Administration & Configuration | `ADM` | **P0** | W1 | 28 | 15 | Organisation structure, users, environments, feature flags, jobs, health console, archival, announcements |
| M67 | Project, Program & Portfolio Management ★ | `PPM` | P2 | W7 | 26 *(est.)* | 14 *(est.)* | Delivery of projects: corporate rollouts, IT infrastructure engagements, branch openings, internal initiatives. **Specification outstanding — §23.1** |

★ = module that did not exist in the v1.0 plan.

### 4.3 In Scope — The 12 Portals

| ID | Portal / application | Users | Volume | Technology | Wave | New |
|---|---|---|---|---|:--:|:--:|
| P01 | Customer Self-Service Portal & Mobile App | Individual customers | 250,000+/month | Next.js 15 + mobile | W2 / W6 | |
| P02 | Technician Mobile Application | Field & workshop technicians | 200–400 | Flutter (Android primary) | W2 | |
| P03 | Admin Operations Portal | Back-office & branch staff | 150–250 | Odoo Web (OWL 2) | W1 | |
| P04 | Corporate B2B Portal | Corporate & government clients | 500–2,000 | Next.js 15 | W4 | |
| P05 | Vendor & Supplier Portal | Vendors, couriers, sub-contractors | 200–500 | Odoo Portal + Next.js | W3 | |
| P06 | Analytics & Executive Dashboard | Management | 25–60 | Metabase + Grafana | W4 | |
| P07 | Marketplace Seller Portal & App ★ | External engineers & shops | 500–2,000 | Next.js 15 + mobile | W7 | ★ |
| P08 | Brand Partner Portal ★ | 17+ brand partners | 50–150 | Next.js 15 | W4 | ★ |
| P09 | Logistics & Rider Application ★ | Riders, coordinators, couriers | 50–200 | Flutter | W3 | ★ |
| P10 | Contact Centre Agent Console ★ | Agents & supervisors | 30–80 | Next.js 15 | W4 | ★ |
| P11 | Field Auditor & Quality Application ★ | Auditors, branch managers | 20–60 | Flutter | W5 | ★ |
| P12 | Partner & Referral Portal ★ | Alliance partners, referrers, resellers | 100–500 | Next.js 15 | W7 | ★ |

### 4.4 Out of Scope

| # | Excluded | Rationale |
|---|---|---|
| OOS-01 | Development of the corporate website and the Next.js portal platform | Separate programme; the ERP integrates with it and does not replace it (CON-03) |
| OOS-02 | Manufacturing or assembly of devices | Not a 1000FiX business |
| OOS-03 | Consumer lending or instalment underwriting | Regulated activity; partner-provided. The ERP records the receivable only |
| OOS-04 | Full-scope Enterprise Asset Management for client-owned plant machinery | M17/M45 cover IT, mobile, appliance, test and rental assets only |
| OOS-05 | Building a proprietary payment switch | Integrates with bKash, Nagad, SSLCOMMERZ |
| OOS-06 | Replacement of brand partners' internal warranty systems | Integration and portal only |
| OOS-07 | Manufacture of telematics or custom hardware (kiosks, scanners, RMM appliances) | Standard commercial hardware |
| OOS-08 | Country-specific tax engines beyond Bangladesh in Waves 1–8 | M65 provides the framework; country packs are separate projects |
| OOS-09 | Odoo major-version upgrade beyond 19.x | Separate engagement (ASM-11) |
| OOS-10 | Business process outsourcing or call-centre staffing | The console is in scope; the operation is not |

### 4.5 Priority Model

| Priority | Modules | Definition | Descope authority |
|---|---:|---|---|
| **P0** | 13 | Regulatory, safety or go-live blocking | **Cannot be descoped** |
| **P1** | 31 | Must-have — core business capability | CEO approval only |
| **P2** | 21 | Important — significant value, deferrable one wave | PMO change control |
| **P3** | 2 | Desirable — enhances experience or efficiency | Backlog, opportunistic |

**P0 modules:** M01, M02, M09, M15, M19, M20, M28, M29, M30, M33, M37, M51, M56.

At requirement level the distribution is approximately **P0 23% · P1 43% · P2 27% · P3 7%**.

### 4.6 Wave Boundaries

| Wave | Months | Theme | Modules | Portals | Reqs |
|---|---|---|---:|---|---:|
| **W1** | 1–4 | Foundation & Service Core | 8 | P03 | ~142 |
| **W2** | 5–8 | Field Operations & Inventory | 7 | P01, P02 | ~178 |
| **W3** | 9–13 | Money, Movement & Documents | 11 | P05, P09 | ~156 |
| **W4** | 14–18 | Agreements, Billing & Contact — **v1.0 scope complete** | 11 | P04, P06, P08, P10 | ~189 |
| **W5** | 19–22 | People, Quality & Managed Services | 10 | P11 | ~148 |
| **W6** | 23–26 | New Asset Businesses | 12 | P01 native apps | ~134 |
| **W7** | 27–30 | Marketplace & Settlement | 7 | P07, P12 | ~121 |
| **W8** | 31–34 | Intelligence & Sustainability | 4 | — | ~79 |
| **W9** | 35–36 | Expansion Readiness | 1 | — | ~33 |
| | | **Total wave entries** | **71** | | **~1,180** |

> **Two reconciliation notes.**
>
> 1. **71 wave entries for 67 modules.** Four modules are delivered across two waves and are
>    counted in both — M01 (W1–W2), M17 (W2/W8), M11 (W3/W7), M53 (W4/W7).
> 2. **The requirement column sums to ~1,180, not 2,930.** The per-wave requirement counts are
>    inherited from the original 30-module roadmap and have **not** been restated against the
>    measured 2,930. They indicate relative wave size only. **This is part of the capacity
>    re-planning required before the roadmap is baselined — see §21.2 and §23.3.2.**
>
> **A further source inconsistency is disclosed rather than silently resolved:** the module
> register records **M07** as W1/W4 and the roadmap places **M25** partly in W8, but the register's
> own wave view omits both from those waves. The counts above follow the register's wave view,
> which declares itself authoritative. The discrepancy must be resolved at roadmap baseline.

**The v1.0 commitment is protected.** Waves 1–4 (Months 1–18) deliver the entire v1.0 module set
plus the additions that are inexpensive because they sit on the same foundations. Waves 5–9
deliver the new business lines.

| v1.0 phase | v1.0 go-live | v2.0 wave | v2.0 go-live | Variance |
|---|---|---|---|---|
| Phase 1 — Foundation | Month 4 | W1 | Month 4 | **Unchanged** |
| Phase 2 — Field Operations | Month 7 | W2 | Month 8 | +1 month (broader inventory scope) |
| Phase 3 — Financial Control | Month 10 | W3 | Month 13 | +3 months (logistics and pricing added ahead) |
| Phase 4 — Contracts & Partners | Month 13 | W4 | Month 18 | +5 months (contact centre and billing engine added) |
| Phase 5 — Workforce & Intelligence | Month 16 | W5 | Month 22 | +6 months |
| Phase 6 — Optimisation | Month 18 | W5–W8 | Month 34 | Absorbed into new-business waves |

---

## 5. STAKEHOLDER ANALYSIS

### 5.1 Stakeholder Register — Internal

| ID | Stakeholder | Role | Population | Interest | Influence | Impact | Primary surface |
|---|---|---|---:|---|---|---|---|
| **R01** | Chief Executive Officer | Executive sponsor | 1 | ROI, growth, competitive position | Very High | Very High | P03, P06 |
| **R02** | Chief Technology Officer | Technical authority, programme owner | 1 | Architecture, integration, security, data protection | Very High | Very High | P03, P06 |
| **R03** | Chief Financial Officer | Finance & compliance owner | 1 | Accurate reporting, VAT/tax compliance, cash flow, TCO | Very High | High | P03, P06 |
| **R04** | Chief Commercial Officer | Commercial owner | 1 | Pricing, contracts, marketplace, partner ecosystem | High | High | P03, P06 |
| **R05** | Operations Director | Primary process owner | 1–2 | Service efficiency, SLA compliance, technician productivity | High | Very High | P03, P06, P11 |
| **R06** | Branch Manager | Local operations lead | 51+ | Branch visibility, local inventory, cash, staff | High | High | P03, P06, P11 |
| **R07** | Dispatch Manager | Dispatch owner | 3–8 | Assignment quality, SLA risk, technician load | High | High | P03, P06 |
| **R08** | Service Centre Agent | Walk-in operations | 150–250 | Fast intake, customer lookup, queue | High | High | P03 |
| **R09** | Workshop Supervisor | Bench repair | 20–40 | WIP visibility, bench utilisation, parts holds | Medium | High | P03 |
| **R10** | Senior Technician | Primary mobile user | 80–150 | Simple app, clear job queue, earnings visibility | **Very High** | **Very High** | P02 |
| **R11** | Junior Technician | Primary mobile user | 120–250 | Simple app, guidance, offline reliability | **Very High** | **Very High** | P02 |
| **R12** | Specialist Technician (L3) | Board-level repair | 15–30 | Diagnostics, knowledge base, workshop tools | Medium | High | P02, P03 |
| **R13** | Remote Support Engineer | MSP delivery | 15–40 | Estate health, ticketing, remote sessions | Medium | High | P03, P10 |
| **R14** | Data Services Technician | Data recovery & destruction | 5–12 | Custody controls, case privacy | Medium | High | P03 |
| **R15** | Logistics Coordinator | Consignment control | 10–25 | Real-time consignment view, rider assignment | High | High | P03, P09 |
| **R16** | Rider / Delivery Agent | Field logistics | 50–150 | Manifest, offline capture, cash reconciliation | High | High | P09 |
| **R17** | Inventory Manager | Inventory owner | 5–10 | Network stock accuracy, replenishment | High | High | P03, P06 |
| **R18** | Branch Store Keeper | Branch stock | 51+ | Fast issue, accurate counts | Medium | High | P03 |
| **R19** | Procurement Officer | Sourcing | 4–8 | RFQ, PO, vendor performance | Medium | Medium | P03, P05 |
| **R20** | Warehouse Operative | Warehouse execution | 15–30 | Put-away, picking, counting | Medium | Medium | P03 |
| **R21** | Sales Manager | Commercial pipeline | 3–6 | Pipeline visibility, quotation speed | Medium | Medium | P03, P06 |
| **R22** | Account Manager (Corporate) | B2B relationships | 8–20 | Contract base, renewals, entitlement, profitability | High | High | P03, P04, P06 |
| **R23** | Marketing Manager | Campaigns & loyalty | 2–4 | Segmentation, campaign performance, attribution | Medium | Medium | P03, P06, P12 |
| **R24** | Marketplace Operations Officer | Seller ecosystem | 4–10 | Seller quality, disputes, payouts | Medium | High | P03 |
| **R25** | Retail / Refurbishment Officer | Circular business | 5–15 | Grading consistency, provenance, resale margin | Medium | Medium | P03 |
| **R26** | Finance Manager | AR/AP/GL | 2–4 | Automation, reconciliation, close cycle | High | High | P03, P05, P06, P08 |
| **R27** | Finance Officer | Transaction processing | 10–20 | Invoice automation, payment matching | High | High | P03, P05 |
| **R28** | Warranty Claims Officer | Claim recovery | 4–10 | Claim pipeline, evidence completeness, ageing | High | **Very High** | P03, P06, P08 |
| **R29** | Cashier / Counter Finance | Branch cash | 51+ | Fast receipting, daily reconciliation | Medium | High | P03 |
| **R30** | HR Manager | People owner | 1–2 | Payroll accuracy, statutory compliance | High | High | P03, P06 |
| **R31** | HR Officer | HR administration | 3–6 | Attendance, leave, records | Medium | Medium | P03 |
| **R32** | Quality Manager / ISO Coordinator | Quality & ISO owner | 2–4 | Audit evidence, CAPA, non-conformance | High | High | P03, P06, P11 |
| **R33** | IT / System Administrator | System administration | 4–8 | Stability, access control, integration health | High | High | P03 |
| **R34** | Contact Centre Agent | Conversation handling | 30–60 | Screen-pop, single console, low handling time | High | High | P10 |
| **R35** | Contact Centre Supervisor | Queue & quality | 4–10 | Service level, agent quality, coaching | Medium | Medium | P10, P06 |

### 5.2 Stakeholder Register — External

| ID | Stakeholder | Population | Interest | Influence | Impact | Surface |
|---|---|---:|---|---|---|---|
| **R36** | Customer (individual) | 250,000+/month | Easy booking, real-time tracking, fast service, transparent pricing | High | High | P01 |
| **R37** | Corporate Portal User (Requester / Approver / Finance / Admin) | 500–2,000 | Self-service, bulk requests, SLA data, consolidated billing | Medium | High | P04 |
| **R38** | External Party — vendor, marketplace seller, brand partner, courier, referral partner, recycling partner, external auditor | 1,000–3,000 | Clear orders, timely payment, fair scoring, portal access | Medium | High | P05, P07, P08, P09, P12 |
| **EXT-01** | Bangladesh NBR | Regulator | VAT/tax compliance, Mushak filing | Low | **Very High** | — |
| **EXT-02** | National Data Management Authority | Regulator | PDPA 2026 compliance, breach notification | Low | **Very High** | — |
| **EXT-03** | Brand partners (17+) | 17+ | Accurate claim data, evidence, timely submission, certified technicians | Medium | High | P08 |
| **EXT-04** | ISO certification body | 1 | Documented, traceable, auditable processes | Low | High | — |
| **EXT-05** | Payment providers (bKash, Nagad, SSLCOMMERZ) | 3 | Integration compliance, settlement accuracy | Low | High | — |
| **EXT-06** | Banking partner (BEFTN) | 1–2 | File format compliance | Low | High | — |
| **EXT-07** | Implementation partner | 1 | Clear requirements, timely decisions, payment | High | **Very High** | — |

### 5.3 Roles Pending Formalisation

Eight roles are defined and in active use inside the module specifications but are not yet in the
central role register. **The programme will be delivered against 46 roles, not 38.**

| ID | Role | Introduced in | Status |
|---|---|---|---|
| **R39** | Data Steward | M33 | Definition contested — M43 and M64 both raise it as an open question |
| **R40** | Chief Data Officer | M33 + 8 others | Used consistently across 9 modules; **statutory role under PDPA 2026 if 1000FiX is a significant data fiduciary (D-15)** |
| **R41** | Payroll Officer | M56 | Prepare only; cannot approve or release |
| **R42** | Training Coordinator | M22 | Defined |
| **R43** | Competency Assessor | M22 | Scoped assessment authority |
| **R44** | HSE Officer | M59 | Defined |
| **R45** | Recruiter | M58 | Cannot approve an offer |
| **R46** | Occupational Health | M59 | Sole access to medical detail |

> **Live defect requiring correction before Wave 1 build.** Identifiers **R54** and **R57** are
> referenced with no definition anywhere, and **R60 is a duplicate identity for R32 (Quality
> Manager)**. A duplicate role identity means an access rule written against R32 does not apply to
> a user granted R60 — this is a security defect, not a documentation defect. See §23.2.

### 5.4 RACI Matrix

**R** = Responsible · **A** = Accountable · **C** = Consulted · **I** = Informed

| Activity | CEO | CTO | CFO | CCO | Ops Dir | HR Dir | Quality Mgr | Branch Mgrs | Technicians | Finance | Partner |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Approve programme investment and scope | **A** | C | C | C | C | C | C | I | I | I | I |
| Approve this BRD | **A** | C | C | C | C | C | C | I | I | I | I |
| Approve the restated TCO (D-14) | **A** | C | **R** | C | I | I | I | I | I | I | I |
| Approve split-residency architecture (D-13) | C | **A** | C | I | I | I | I | I | I | I | C |
| Define functional requirements | I | C | C | C | **R** | C | C | C | C | C | C |
| Partner evaluation & selection | **A** | **R** | C | C | C | I | I | I | I | I | — |
| Contract negotiation | **A** | C | **R** | C | C | I | I | I | I | I | R |
| Solution design | I | **A** | C | C | C | C | C | I | I | C | **R** |
| Business rule sign-off | I | C | C | C | **A** | C | C | C | I | C | R |
| Data migration & reconciliation sign-off | I | **A** | C | C | C | C | C | **R** | I | **R** | R |
| UAT execution & acceptance | I | C | C | C | **A** | C | C | **R** | **R** | **R** | C |
| Wave gate Go/No-Go | **A** | C | C | C | C | C | C | I | I | I | C |
| Training delivery | I | C | I | C | C | **A** | C | **R** | **R** | R | **R** |
| Legacy decommission | I | C | C | C | **A** | C | C | **R** | I | R | C |
| Benefit realisation tracking | **A** | C | **R** | C | C | C | C | C | I | C | I |
| Post-go-live support | I | **A** | I | I | C | I | C | C | C | I | **R** |

### 5.5 Business-Side Commitment Required

| Role | Commitment | Waves |
|---|---|---|
| Executive Sponsor (CEO) | 4 hours/month steering | All |
| Module Business Owners (16 named) | **20% of time** | Waves affecting their module |
| Super-Users (2–3 per module) | **30% during UAT**, 10% otherwise | Waves affecting their module |
| Branch Champions (1 per branch) | 4 hours/week during rollout | W1–W5 |
| Data Owners | 20% during migration | W1–W5 |

> **This is the binding constraint on the programme (RSK-001, rated Critical).** If business
> availability is not protected, waves will slip regardless of development capacity. The Company
> accepts that a wave gate slips rather than allowing development to run ahead into unaccepted
> work.

### 5.6 Module Business Ownership

| Business owner | Modules |
|---|---|
| Chief Technology Officer | M25, M26, M28, M29, M30, M48, M62, M63, M64, M65, M66, M67 |
| Chief Financial Officer | M19, M20, M39, M49, M50, M51, M52, M53, M54, M60 |
| Chief Commercial Officer | M07, M08, M11, M12, M33, M36, M37, M38, M40 |
| Service Operations Director | M01, M02, M17, M31 |
| HR Director | M21, M22, M55, M56, M57, M58, M59 |
| Quality Manager | M18, M23, M24, M45, M61 |
| Customer Service Manager | M27, M32, M34 |
| Corporate Services Head | M05, M13 |
| Logistics Manager | M03, M46 |
| Warehouse Manager | M15, M41, M43 |
| Procurement Manager | M16, M42, M44 |
| Marketing Head | M10, M35 |
| Branch Operations Lead | M04, M47 |
| Retail Operations Head | M14 |
| Technical Services Head | M06 |
| Finance Director | M09 |

**Every module has exactly one business owner and one system owner** (register rule RG-03). The
business owner accepts the module's requirements at UAT (DoD-13).

---
---

# PART B — FROM WHAT, TO WHAT

---

## 6. CURRENT STATE ANALYSIS (AS-IS)

### 6.1 Current System Landscape

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ WordPress site   │  │ Manual           │  │ Standalone       │
│ (1000fix.com)    │  │ spreadsheets     │  │ accounting tool  │
│ 5–7 s load       │  │ · Service orders │  │ · Basic GL       │
│ Basic booking    │  │ · Inventory      │  │ · No integration │
└──────────────────┘  │ · Customer data  │  └──────────────────┘
                      │ · Contracts, HR  │
┌──────────────────┐  └──────────────────┘  ┌──────────────────┐
│ station.1000fix  │  ┌──────────────────┐  │ Paper forms      │
│ .com + legacy    │  │ WhatsApp / phone │  │ · Service reports│
│ 123.0.26.238     │  │ · Dispatch       │  │ · QC checklists  │
│ order tracking   │  │ · No tracking    │  │ · Job cards      │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Email            │  │ Sign-in books    │  │ Excel payroll    │
│ · Warranty claims│  │ · Attendance     │  │ · 3-day cycle    │
│ · Untracked      │  │ · Unverifiable   │  │ · Manual tax     │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  NINE COMMITTED REVENUE STREAMS WITH NO SYSTEM AT ALL:       │
│  MSP · Rental · Data recovery · Backup · Refurbishment ·     │
│  Trade-in · E-waste · Marketplace · Advertising              │
└──────────────────────────────────────────────────────────────┘
```

**System integration score: ZERO.** No system is connected to any other. All reconciliation is
manual.

### 6.2 As-Is Process Analysis

| # | Process | Current state | Pain points |
|---|---|---|---|
| 1 | **Service request intake** | Customer calls 16743 or walks in → agent writes on paper or into a spreadsheet → no automatic acknowledgment → order number inconsistent | Data entry errors; no search; no SMS acknowledgment; no service-history lookup at intake; ~10 minute walk-in intake |
| 2 | **Workshop / bench repair** | Whiteboards and paper job cards | No WIP ageing, no bench utilisation, no repair-level routing, devices lost on the bench |
| 3 | **Technician dispatch** | Coordinator reviews a paper job list → calls or WhatsApps the technician → verbal assignment | No visibility of technician location or workload; no skill or certification matching; frequent reassignment; productivity unknown; ~35% of the working day in travel |
| 4 | **Service execution & reporting** | Paper service form → customer signs paper → form returned to the branch → manually keyed 1–3 days later | No real-time updates; data-entry backlog; forms lost; photos not standardised; QC not enforced |
| 5 | **Pick & drop logistics** | Phone-coordinated | No chain of custody; no proof of collection or delivery; disputes unresolvable |
| 6 | **Inventory management** | Each branch tracks its own stock in local spreadsheets; phone calls between branches to check availability | Stockouts at one branch while excess sits at another; no reorder alerts; no consumption analysis; **van stock entirely untracked** |
| 7 | **Warranty claim processing** | Finance prepares claims manually from paper forms → emails the brand → follows up manually → reconciles by email | 30–90 day submission delay; claims lost; **15–20% revenue leakage**; no status tracking; reconciliation takes weeks; 60–120 days to reimbursement |
| 8 | **Invoicing & payment** | Billing staff manually creates an invoice from the paper form → sends by WhatsApp/email/print → payment in cash or transfer → manually recorded | Invoice errors; 3–7 day invoicing delay; no automated reminders; unreliable cash reconciliation |
| 9 | **AMC / RAMC management** | Contract in a spreadsheet; renewal reminders checked by hand; maintenance tracked in a calendar | Renewal lapses; no utilisation tracking; no auto-invoicing; **contract profitability unknown** |
| 10 | **Financial reporting** | Branch spreadsheets collected monthly and consolidated in Excel | **15–20 day close**; consolidation errors; incomplete branch data; decisions on stale data |
| 11 | **HR & payroll** | Sign-in books → leave in a spreadsheet → payroll calculated in Excel → individual bank transfers | Attendance errors; leave balance disputes; payroll errors; overtime inaccurate; no performance-linked incentive |
| 12 | **Certification management** | Manually tracked, if at all | **Certification lapses are discovered when a brand rejects a claim** |
| 13 | **Customer communication** | Status given verbally when the customer calls | Customers call the hotline 3+ times per job; call centre overwhelmed; no digital audit trail |
| 14 | **Quality & ISO** | Paper records, assembled for audit | Audit evidence compiled manually; CAPA effectiveness unverified |
| 15 | **The nine new revenue streams** | **No system whatsoever** | MSP contracts sold but delivered manually; rental assets untracked; refurbished units resold without provenance; marketplace unbuildable; e-waste without compliance evidence |

### 6.3 Performance Baseline

| Metric | Current baseline | Industry benchmark | Gap |
|---|---|---|---|
| Service order automation rate | ~20% | 60–80% | −40 to −60 pts |
| Average jobs per technician/day | 4–5 | 7–9 | −3 to −4 |
| Technician utilisation | ~55% | 75–85% | −20 to −30 pts |
| Travel as % of working day | ~35% | 20–25% | +10 to +15 pts |
| First-time fix rate | ~70% | 80–90% | −10 to −20 pts |
| Inventory accuracy | ~75% | 95–99% | −20 to −24 pts |
| Warranty claim submission time | 30–90 days | < 7 days | −23 to −83 days |
| Warranty revenue leakage | 15–20% | < 2% | +13 to +18 pts |
| Month-end financial close | 15–20 days | 3–5 days | −10 to −15 days |
| Customer CSAT | 3.8/5 | 4.5–4.8/5 | −0.7 to −1.0 |
| Online booking rate | ~40% | 70–90% | −30 to −50 pts |
| AMC renewal rate | ~60% | 80–90% | −20 to −30 pts |
| Walk-in intake time | ~10 min | < 3 min | +7 min |
| Payroll processing time | 3 days | < 1 day | −2 days |
| Conversations captured in a system | ~0% | 100% | −100 pts |
| Revenue streams with a system of record | 5 of 14 | 14 of 14 | −9 streams |

### 6.4 Financial Impact of the Current State

| Gap | Estimated annual cost |
|---|---|
| Unclaimed or delayed warranty revenue | BDT 80–120 lac |
| Technician underutilisation | BDT 60–90 lac |
| Inventory waste (excess + stockouts) | BDT 30–50 lac |
| Manual invoicing delay (cash-flow cost) | BDT 20–30 lac |
| Customer churn from poor experience | BDT 40–70 lac |
| Excessive administrative overhead | BDT 25–40 lac |
| **Total quantified annual cost** | **BDT 2.55 – 4.0 crore** |

**Not included above, because it is opportunity cost rather than waste:** the nine committed
revenue streams that cannot operate at scale without a system. Their modelled contribution at
steady state is **BDT 334 lac per year** (§19.2).

### 6.5 Legacy Decommission Commitment

The programme is accountable for the **complete withdrawal** of each legacy practice at the wave
stated. **A wave gate is not passed while its legacy process is still running beyond the agreed
parallel-run period.**

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

## 7. FUTURE STATE VISION (TO-BE)

### 7.1 The Operating Model

```
                          ┌─────────────────────────────────────┐
                          │        EXPERIENCE LAYER             │
                          │  12 portals & applications (P01–P12)│
                          └──────────────────┬──────────────────┘
                                             │
                          ┌──────────────────▼──────────────────┐
                          │      EXPERIENCE API GATEWAY         │
                          │  OAuth2/OIDC · rate limits · BFF    │
                          └──────────────────┬──────────────────┘
                                             │
   ┌─────────────────────────────────────────▼─────────────────────────────────┐
   │                  1000FiX ERP v2.0 — SYSTEM OF RECORD                      │
   │   11 categories · 67 modules · 2,930 requirements                         │
   │  ┌─────────────────────────────────────────────────────────────────────┐  │
   │  │ SHARED KERNEL — party · product · location · entity · document ·    │  │
   │  │                 event                                                │  │
   │  └─────────────────────────────────────────────────────────────────────┘  │
   └───────────────────────────────────┬───────────────────────────────────────┘
                                       │
   ┌───────────────────────────────────▼───────────────────────────────────────┐
   │            DATA & INTELLIGENCE PLATFORM · 225 entities                    │
   │  OLTP · time series · analytical warehouse · ML · BI · observability      │
   └───────────────────────────────────────────────────────────────────────────┘
```

**The six shared kernel concepts** — party, product & service catalogue, location & geography,
legal entity & operating unit, document, and event — are modelled **once** and used by nearly
every module. A single party may hold multiple roles simultaneously: a marketplace seller can also
be a customer; a corporate client can also be a referral partner.

### 7.2 Business-Line Architecture

Nine business lines run through **shared modules**. Each is **configured, not coded separately.**

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
becoming a god-object** — a thin core plus line-specific extension models linked one-to-one, each
owned by its business-line module.

### 7.3 Departmental Transformation

#### Service operations — from reactive to proactive
**Today:** a coordinator assigns jobs by phone with no visibility of field operations.
**Tomorrow:** the dispatch engine scores candidates on skill, certification, location, workload and
van stock, and auto-assigns above a confidence threshold; the coordinator monitors a live map; SLA
alerts fire at 50/75/90/100%; escalation is rule-driven; **every override is logged with a reason
code that feeds model improvement.**

#### Field technicians — from paper to mobile, offline-first
**Today:** paper service form, verbal sign-off, manual parts recording.
**Tomorrow:** a Bengali-first Flutter app shows the optimised queue with turn-by-turn navigation;
the diagnostic tree is guided; parts are scanned from van stock; before/after photos carry GPS and
timestamp; the customer signs on screen; **the app works for 24 hours with no connectivity and
syncs within 30 seconds on 3G with zero data loss.**

#### Workshop — from whiteboard to bench board
**Today:** whiteboards and paper job cards.
**Tomorrow:** bench assignment, WIP board, repair-level routing (L1/L2/L3), parts holds visible,
test and burn-in recorded, multi-job handling.

#### Logistics — from phone calls to unbroken custody
**Today:** pick & drop coordinated by phone; no custody evidence.
**Tomorrow:** every handover records GPS, timestamp and **both parties' identity**; seal numbers;
photographs; customer OTP and signature; POD capture completeness 100%; **zero custody breaks.**

#### Inventory — from guesswork to precision
**Today:** branches phone each other to find parts.
**Tomorrow:** one dashboard shows stock at all 51+ locations plus van stock; replenishment drafts
itself at the reorder point; inter-branch transfer is digital with approval; **brand consignment
stock is segregated from own stock and cannot be consumed on non-warranty jobs.**

#### Finance — from manual to automated
**Today:** invoice typed from a paper form, sent by WhatsApp, payment recorded by hand.
**Tomorrow:** the invoice generates within 5 seconds of job closure; Mushak 6.3 compliant; the
payment link goes out on the customer's preferred channel; **90%+ of payments auto-match**; the
Mushak 9.1 return is prepared automatically and filed by the 15th; **month-end closes in ≤ 3 days.**

#### Warranty — from leakage to recovery
**Today:** claims prepared manually, submitted 30–90 days late, 15–20% never recovered.
**Tomorrow:** the claim is created automatically within 24 hours of the warranty job closing, with
the evidence pack assembled and validated for completeness; submitted within 72 hours in the
brand's required format; **95%+ submitted on time, first-submission approval ≥ 90%, leakage < 2%.**

#### People — from spreadsheets to controls
**Today:** sign-in books, Excel payroll, certification lapses discovered by claim rejection.
**Tomorrow:** biometric and GPS attendance; roster and capacity by skill and zone; payroll with
Bangladesh tax slabs, PF, gratuity and BEFTN in under 4 hours; and **a hard dispatch block on any
technician whose brand certification has expired.**

#### Customer experience — from opaque to transparent
**Today:** the customer calls the hotline three times to learn the status.
**Tomorrow:** booking in ≤ 3 steps; notifications at every milestone by push, SMS and WhatsApp; a
live technician map with ETA; a public tracking link without login; estimate approval on screen;
**> 80% of status enquiries self-served.**

#### Management — from compiled packs to live data
**Today:** branch spreadsheets consolidated monthly.
**Tomorrow:** executive dashboards across all 14 revenue streams with drill from group revenue to a
single job; branch league tables; **zero manual reporting packs.**

### 7.4 The Nine New Business Lines — What Becomes Possible

| Business line | What the system makes possible |
|---|---|
| **Managed services (M05)** | MSP contracts with monitored estates, agent and agentless monitoring, alerting with noise reduction, ticketing against SLA, patch management, per-client profitability and service reports |
| **Rental (M13)** | Asset pool across 8 categories with reservation, tariff, deposit, **condition report at dispatch and return**, damage assessment and recovery, utilisation and depreciation discipline |
| **Data recovery (M06)** | Cases with **dual-control media custody**, cleanroom scheduling, partner lab referral, restricted access, and compliance reporting for audit |
| **Backup subscriptions (M06/M39)** | Provisioned storage per plan, monitored backup jobs, restore requests with SLA and verification, recurring billing |
| **Refurbishment & resale (M14)** | Trade-in valuation, IMEI/stolen-device screening, **certified data wipe before any refurbishment**, grading against published criteria, provenance record, controlled refurbished warranty |
| **Trade-in (M14)** | Customer-submitted photos and condition, indicative then firm offer, collection, payment |
| **E-waste (M18)** | Collection events, triage, certified destruction, batches to certified partners only, material recovery credit, **retrievable disposal certificate for every unit** |
| **Marketplace (M12)** | Seller onboarding with KYC, listings, job broadcast, competitive bidding, ratings, disputes, wallets, commission, escrow, payouts, paid boost — with **quality and evidence standards identical to owned jobs** |
| **Advertising (M12/M35)** | Boost and placement purchase with impressions and clicks, always disclosed as promoted |

### 7.5 Target Automation — 85% by Wave 8

| Process | Manual today | Automated target | Wave |
|---|---|---|:--:|
| Service order creation | 100% manual | 90% automatic from digital channels | W2 |
| Customer status notification | Manual on request | **100% automatic** | W1 |
| Access provisioning and revocation | 100% manual | **100% automatic** | W1 |
| Route planning | Not done | **100% automatic** | W2 |
| Invoice generation | 100% manual | **100% automatic** | W3 |
| Payment matching | 100% manual | 94% automatic | W3 |
| Replenishment ordering | 100% manual | 80% automatic | W3 |
| Warranty claim creation | 100% manual | **100% automatic** | W4 |
| Warranty claim submission | 100% manual | 85% automatic | W4 |
| Contract renewal outreach | 100% manual | **100% automatic** | W4 |
| Preventive work order creation | 100% manual | **100% automatic** | W4 |
| VAT return preparation | 100% manual | **100% automatic** | W4 |
| Payroll calculation | 100% manual | **100% automatic** | W5 |
| Technician assignment | 100% manual | 70% automatic | W6 |
| Commission and payout calculation | Not done | **100% automatic** | W7 |
| Management reporting | 100% manual | **100% automatic** | W8 |
| **Overall routine operational work** | **~20%** | **85%** | **W8** |

The full catalogue of **60 numbered automations** with triggers, actions and failure behaviour is
at §22.

### 7.6 Guiding Principles

| # | Principle | What it means in practice |
|---|---|---|
| 1 | **One system of record** | Every business object with a lifecycle or financial consequence is mastered in the ERP. Portals and apps hold no authoritative state. |
| 2 | **Zero licence cost by default** | Odoo 19 CE + OCA + self-hosted open source. Commercial components require CFO approval and a documented open-source alternative assessment. |
| 3 | **Configure before extend, extend before fork** | Selection hierarchy L1→L2→L3→L4→L5→L6. |
| 4 | **API-first and event-driven** | Every module exposes documented APIs and emits domain events. **No module reads another module's tables.** |
| 5 | **Bengali-first for field and customer surfaces** | Bengali is primary for technician and customer interfaces; English for back office. |
| 6 | **Offline-capable where the work is offline** | Technician, logistics and field-audit applications operate 24 hours without connectivity. |
| 7 | **Multi-entity and multi-currency from the schema up** | Even operating one entity in one country, every record carries entity, branch, currency and locale dimensions. |
| 8 | **Compliance is a feature, not a project** | ISO 9001:2015, ISO 27001, NBR VAT/TDS, Bangladesh Labour Act and PDPA 2026 are modelled as **enforced system behaviour**. |
| 9 | **Every module is measurable** | No module ships without its KPI set instrumented and visible in M25. |
| 10 | **Automate to 85%** | Using M26 AI services by Wave 8. |

---
---

# PART C — WHAT IS REQUIRED

---

## 8. BUSINESS REQUIREMENTS — 67 MODULES IN 11 CATEGORIES

### 8.1 Requirement Classification and Identifiers

Requirements are classified per **IIBA BABOK® v3**:

| Type | Meaning | Held in |
|---|---|---|
| **BR** | Business requirement — a goal or outcome the enterprise needs | This BRD, §3 and §8 |
| **SR** | Stakeholder requirement — what a stakeholder needs to do their work | This BRD, §8 and §13 |
| **FR** | Functional requirement — "the system shall…" | Module specification files, `FR-<CODE>-nnn` |
| **NFR** | Non-functional requirement — a quality of the solution | §9, `NFR-001…NFR-101` |
| **BRU** | Business rule — a constraint the system enforces | §10, `BRU-<CODE>-nn` |
| **TR** | Transition requirement — migration, training, cutover | §11.6, §13, §21 |

**Identifier conventions — permanent, never reused:**

```
FR-<CODE>-nnn        Functional requirement       e.g. FR-SRM-014
FN-<CODE>-nnn.m      Function within a feature    e.g. FN-RNT-007.2
E-<CODE>-nn          Data entity                  e.g. E-CTR-03
INT-nnn              Integration                  e.g. INT-042
EVT-<domain>.<verb>  Domain event                 e.g. EVT-service_order.completed
R01–R46              User role                    e.g. R14 Data Services Technician
BRU-<CODE>-nn        Business rule                e.g. BRU-SRM-09
AUT-nnn              Automation                   e.g. AUT-018
NFR-nnn              Non-functional requirement
KPI-nnn              Key performance indicator
CD-nnn               Custom development deliverable
W1–W9                Delivery wave
```

**How to read this section.** The **2,930 individually numbered, individually
acceptance-criteria'd functional requirements** are held in the module specification files. This
section states, for each module, the **business requirement it satisfies**, the objectives it
serves, the requirement volume and the effort — at the level the business needs to approve scope,
own outcomes and accept delivery. It does not restate 2,930 rows.

### 8.2 Category A — Service Delivery & Operations

> **BR-A:** Provide a single system of record for every unit of service work the Company performs
> — across five delivery modes, all fourteen business lines and 51+ locations — enabling 85%
> automation of the service delivery lifecycle with SLA, quality and custody enforced by the
> system rather than by discipline.
> *(Serves BO-01, BO-02, BO-05, BO-11, BO-15)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M01 SRM** | Own the service order from any channel for any business line: multi-channel intake; full lifecycle; classification across 14 business lines; diagnosis; estimate and customer approval loop; SLA definition, clocks, holds and escalation; quality control; rework detection; job cost roll-up; legacy order lookup | 88 | BO-01, BO-05 |
| **M31 WSR** | Run in-house bench repair: workshop routing, bench assignment and WIP board, Level 1/2/3 repair, RMA-in, component-level work, test and burn-in, parts holds, multi-job handling | 58 | BO-01, BO-02 |
| **M02 FSM** | Decide who does field work, when and in what order, and execute it on mobile: dispatch engine scoring skill, certification, location, workload and van stock; route optimisation and re-optimisation; GPS; geofencing; zones; capacity and slot management; standby rota; offline execution; assignment explanation and override logging | 74 | BO-01, BO-02, BO-15 |
| **M03 LOG** | Move devices, parts and assets between customers, branches, workshops, vendors and recyclers **with unbroken custody**: consignments and legs; chain of custody with GPS, timestamp and dual identity; pick & drop; courier integration; rider manifests; cash on delivery; loss and damage claims; restricted-item control; logistics cost allocation | 42 | BO-01, BO-05 |
| **M04 FRD** | Run the counter at 51+ centres: token queue and wait-time estimation; **walk-in intake in under 3 minutes**; handover; counter cash drawer and shift control; receipt, job-sheet, label and gate-pass printing; self-service kiosk | 32 | BO-01, BO-05 |
| **M05 RMS** | Deliver remote assistance and contracted managed IT services: MSP contracts and estates; agent and agentless monitoring; alerting with noise reduction; MSP ticketing against SLA; patch management; remote sessions; runbooks; client onboarding and offboarding; per-client profitability | 61 | **BO-11**, BO-05 |
| **M06 DTS** | Deliver data recovery, backup subscriptions, migration and **certified destruction under controlled custody**: cases; dual-control media custody; cleanroom scheduling; partner lab referral; backup plans and restore testing; certified destruction to an approved technique standard; restricted access and compliance reporting | 34 | BO-10, BO-14 |

**Category A total: 362 requirements · 206 PW**

**Non-negotiable business controls in Category A:**

- A service order cannot be created without an identified device *(BRU-SRM-01, hard)*
- A warranty-type order requires an active warranty at the request date *(BRU-SRM-02, hard)*
- A service order cannot reach Completed without a passed quality checklist *(BRU-SRM-04, hard)*
- **A service order cannot be assigned to a technician lacking current certification for that
  brand's warranty work** *(BRU-SRM-09 / BRU-HRM-01, hard — this is BO-15)*
- Before/after photographs are mandatory on every warranty job *(BRU-SRM-17, hard)*
- Independent second-person QC above BDT 25,000 *(BRU-SRM-18, hard)*
- **No custody transfer without a scan and identity capture from both parties** *(BRU-LOG-01, hard)*
- A device uncollected 30 days after Ready enters the abandonment process with statutory notice
  *(BRU-SRM-16, computed)*

### 8.3 Category B — Customer Engagement & Experience

> **BR-B:** Hold one authoritative record of every party the Company deals with, honour the
> statutory obligations attached to their personal data, capture every conversation on every
> channel, and measure and act on how customers actually experience the service.
> *(Serves BO-05, BO-08, BO-10, BO-16)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M33 CPM** | Be the single authoritative record of every party — individual, corporate group, household, dealer, government body, employee, vendor, seller, brand, partner — with multi-role capability, Bangladesh address hierarchy, identity documents with residency classification, **PDPA 2026 consent, transparency notice and data-subject rights**, duplicate detection and merge with reversal, and data-quality management | 52 | BO-05, **BO-10** |
| **M07 CRM** | Manage the commercial relationship: Customer 360, segmentation, corporate hierarchy and contact roles, approval chain configuration, lead and opportunity pipeline, account teams, blacklist and fraud flags, win-back segmentation, referral attribution | 46 | BO-05, BO-08 |
| **M10 LOY** | Run the Privilege Program and every reward mechanic: tier enrolment, renewal and upgrade; points, wallet and vouchers; referral; tier-based automatic entitlement; **loyalty liability accounting** | 44 | BO-08 |
| **M34 CXM** | Measure and close the loop on customer experience: CSAT, NPS and CES at every touchpoint; multi-parameter service and technician rating; review capture and publication; complaint intake, taxonomy, escalation and closure; voice-of-customer analytics | 42 | BO-05 |
| **M27 CCE** | Bring **every** inbound and outbound conversation into the system of record across voice, chat, WhatsApp, email, SMS and social — including hotline 16743 — with screen-pop, cross-channel history, disposition coding, recording, quality scoring and supervision; and own **all notification delivery** for every module | 58 | **BO-16**, BO-05 |
| **M32 CAI** | Provide a Bengali-first AI assistant that handles first-line conversations and performs authenticated actions against live ERP data, with knowledge grounding, agent handoff with context, guard rails and fallback to rules | 38 | BO-05, BO-16 |
| **M35 MKT** | Plan and execute campaigns and demand generation: segmentation, multi-channel journeys, promotional offers, lead capture and attribution, advertising and boost placement, campaign cost attribution | 40 | BO-08 |

**Category B total: 320 requirements · 148 PW**

### 8.4 Category C — Commercial, Pricing & Revenue

> **BR-C:** Define everything the Company sells, price it once and only once, quote it accurately,
> commit to it under a contract engine that models fourteen product families without code change,
> and reach the customer through every route to market — direct, contract, subscription,
> e-commerce and marketplace.
> *(Serves BO-04, BO-08, BO-11, BO-12, BO-13, BO-14)*

**This is the largest category in the programme by both requirement count and effort.** The
commercial chain has exactly one owner per link:

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

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M37 CAT** | Define everything sellable — services, service kits, parts, protection plans, rental SKUs, refurbished grades, subscription plans — with repair bills of material and standard times. **A price never lives on a catalogue item; a catalogue item never carries a discount** | 34 | BO-01, BO-08 |
| **M11 PRC** | Hold **every price in the business**: rate cards by device category, brand, model and repair type; warranty vs out-of-warranty; price books; customer-specific and segment pricing; discount governance and approval thresholds; NTE limits; dynamic pricing with guard rails and full decision audit | 36 | BO-08, BO-09 |
| **M36 QTE** | Build, version, issue and track estimates and quotations: labour + parts + transport + tax build-up; customer approval loop with part-approval and decline; validity and expiry; competitive bidding; corporate tenders; **quotation-to-invoice integrity** | 32 | BO-05, BO-08 |
| **M08 CTR** | Be a contract **engine**, not an AMC table — modelling **14 product families** without code change (RAMC 6 packages, Commercial AMC, IT Infrastructure AMC, Healthcare Equipment AMC with mandatory calibration, Specialty Equipment AMC, Managed Services 6 types, Mobile & Appliance Service 5 types, rental master agreements, marketplace seller agreements, brand partner agreements) with entitlement definition and consumption, SLA terms, preventive schedule generation, amendment, renewal and **contract profitability** | 44 | **BO-08**, BO-11 |
| **M09 WTY** | Recover every taka of warranty revenue: registration and automated entitlement verification by serial and purchase date; **7 protection product families**; brand claim automation for 17+ partners with per-brand rule engines and evidence packs; claim lifecycle to reimbursement; reconciliation with brand remittances; recall handling | 48 | **BO-04** |
| **M39 SUB** | Run recurring and usage-based revenue: billing cycles and proration, plan change, MRR/ARR, dunning triggers, churn measurement | 30 | BO-08, BO-11 |
| **M38 ECM** | Sell 1000FiX's own products and services online, sharing identity, catalogue, stock and settlement with the ERP: browse, cart, checkout, fulfilment, returns | 40 | BO-09, BO-14 |
| **M12 MKP** | Run the aggregator: seller registration and KYC, listings, job broadcast, competitive and counter-bidding, ratings and reviews, disputes, seller wallets, commission, escrow, payouts, paid boost and advertising, **performance scoring with automatic visibility reduction and suspension** | 62 | **BO-12** |
| **M40 PCM** | Manage brand partners, alliance partners, referral partners, resellers and franchise branches: agreements, commission schemes, co-marketing, partner performance | 30 | BO-08, BO-09 |

**Category C total: 494 requirements · 262 PW**

**Three boundaries that must not blur:**

| Boundary | Rule |
|---|---|
| M37 Catalogue vs M11 Pricing | A price never lives on a catalogue item. A catalogue item never carries a discount. |
| M08 Contract vs M39 Subscription | M08 defines entitlement ("what did we promise?"); M39 turns it into money owed ("what do we bill, when, how much?"). A subscription always has an M08 contract behind it. |
| M38 E-Commerce vs M12 Marketplace | One storefront, two supply models. The customer sees one experience; **the ledger sees two revenue treatments.** |

> **Critical open decision (D-03, RSK-022).** The marketplace **principal-versus-agent VAT and
> liability model** is not settled. External tax and legal opinion is required three months before
> Wave 7 build. M12 and M53 must be designed so the revenue treatment is **configurable, not
> hard-coded** — and **the model cannot vary by transaction** *(BRU-FIN-08, hard)*.

### 8.5 Category D — Circular & Asset-Based Business

> **BR-D:** Operate the circular device economy end to end — rent, take in, wipe, refurbish, grade,
> resell and finally recycle — with provenance, certified data destruction and disposal evidence
> at every step.
> *(Serves BO-13, BO-14, BO-10)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M13 RNT** | Rent eight asset categories with reservation and availability, rental agreements and master framework agreements with call-off, tariffs (period + usage), deposits, **condition reports at dispatch and return**, damage assessment and recovery, utilisation and depreciation discipline, subscription rental | 44 | **BO-13** |
| **M14 TRF** | Buy used devices, grade and refurbish them, and resell them with controlled warranty: trade-in request with photos, indicative and firm valuation, **IMEI/stolen-device screening**, intake, **certified data wipe before any refurbishment**, refurbishment work orders, grading against published criteria, provenance record, resale lots, refurbished warranty terms and reserve | 39 | **BO-14** |
| **M18 ESG** | Collect end-of-life devices, certify destruction and disposal, and recover materials: collection events and drop-off points, triage and disposition, certified destruction, recycling batches to certified partners, material recovery credit, disposal certificates, statutory e-waste reporting, ESG reporting | 26 | BO-14, BO-10 |

**Category D total: 109 requirements · 60 PW**

**Non-negotiable business controls in Category D:**

- **No trade-in device proceeds to refurbishment or resale without a certified data destruction
  record** *(BRU-TRF-01, hard)*
- Provenance and identity checks must pass before a trade-in offer is paid *(BRU-TRF-02, hard)*
- A refurbished unit cannot be listed without a completed QA test protocol and an assigned grade
  *(BRU-TRF-03, hard)*
- Battery health and known defects must be disclosed on every refurbished listing *(BRU-TRF-04, hard)*
- A rental asset cannot be dispatched without a completed pre-dispatch condition report
  *(BRU-RNT-01, hard)*
- **No device leaves for recycling without a certified wipe or physical destruction record**
  *(BRU-ESG-01, hard)*
- E-waste may transfer only to a partner whose certification is current at the transfer date
  *(BRU-ESG-02, hard)*

### 8.6 Category E — Supply Chain & Inventory

> **BR-E:** Know what stock exists, where it is, in what condition, under whose ownership and what
> it is worth — across 51+ branches, central and regional hubs, and 200–400 technician vans — and
> buy, receive, store and replenish it without stockouts or excess.
> *(Serves BO-03)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M15 INV** | Own stock across 51+ locations plus hubs plus **technician van stock**: real-time network visibility; barcode and QR; serial and batch tracking; parts catalogue with brand/model cross-reference; genuine vs compatible classification; substitution mapping; **warranty-parts segregation**; **brand-owned consignment stock**; three-tier parts pricing; goods receipt with inspection; inter-branch transfer with approval; requisition and reservation from service orders; automatic replenishment; cycle counting; dead stock; RTV; FIFO and weighted-average valuation | 48 | **BO-03** |
| **M41 WMS** | Execute the physical warehouse: bins and locations, put-away strategy, picking waves, packing, cross-dock, hazardous-material handling, warehouse mobile operations | 34 | BO-03 |
| **M16 PRO** | Buy: requisition with branch and central approval, RFQ and quotation comparison, purchase orders, blanket orders, goods receipt and inspection, **three-way matching that blocks unmatched invoices**, budget control, import order and LC tracking | 32 | BO-03, BO-06 |
| **M42 SRM2** | Own the supplier as a relationship: qualification and onboarding, document management with expiry, performance scorecards on delivery/quality/pricing/responsiveness, contracts and pricing agreements, risk and development, **flow-down of PDPA processor obligations by contract** | 26 | BO-03, BO-10 |
| **M43 DPL** | Decide how much to hold and when to order: demand forecasting by part, location and season; replenishment planning; safety stock optimisation; supplier lead-time modelling; forecast accuracy measurement | 24 | BO-03 |
| **M44 ITC** | Own cross-border supply: proforma, letters of credit, shipment, customs documentation, duty and tariff, clearing, **true landed cost allocated to inventory valuation**, trade compliance screening | 28 | BO-03, BO-06 |

**Category E total: 235 requirements · 119 PW**

### 8.7 Category F — Asset, Equipment & Facilities

> **BR-F:** Know the identity, ownership, history and condition of every device and asset the
> Company touches — the customer's, the client's estate, the Company's own tools and vehicles, and
> the premises they operate from — and use telemetry to predict failure before it happens.
> *(Serves BO-02, BO-11, BO-13)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M17 AST** | Hold the identity, ownership, history and condition of every device: brand, model, serial, IMEI, purchase date, warranty status, ownership and transfer; corporate asset estates with bulk upload and site/department/user assignment; full service history per device; device photo library; asset health index | 34 | BO-05, BO-11 |
| **M45 EAM** | Manage Company-owned tools, diagnostic and test equipment: issue, custody, **calibration schedules and certificates** (required by Healthcare Equipment AMC), maintenance, retirement | 26 | BO-10, BO-08 |
| **M46 FLT** | Manage service vans, rider motorcycles and company vehicles: documents and expiry, servicing, fuel, drivers, telematics, cost per kilometre, incidents | 24 | BO-02 |
| **M47 FAC** | Manage 51+ premises: leases and renewals, utilities, maintenance, security, safety equipment, occupancy, opening and closing | 22 | BO-09 |
| **M48 IOT** | Ingest telemetry at scale, score asset health, alert on thresholds and **predict failure with ≥ 70% precision on the pilot estate** | 28 | BO-11, BO-13 |

**Category F total: 232 requirements · 114 PW**

### 8.8 Category G — Finance & Treasury

> **BR-G:** Close the books in three days, invoice every completed job automatically and
> accurately, recover every receivable, pay every obligation once and only once, and satisfy
> every Bangladesh statutory obligation without manual intervention.
> *(Serves BO-06, BO-10, BO-12)*

**This category carries the heaviest statutory density in the programme.** Requirement counts here
ran **+29% above the original estimate** for that reason.

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M19 FIN** | Maintain the statutory ledger: multi-entity, multi-branch chart of accounts with the full dimensional model (entity, branch, cost centre, business line, zone); GL with drill-down to transaction; manual and automated journals; **Bangladesh fiscal year July–June**; period-end close with automated checks; inter-company reconciliation and consolidation; audit support; financial controls testing | 40 | **BO-06**, BO-10 |
| **M20 ARB** | Invoice and collect: **automatic invoice generation from closed jobs within 5 seconds, for 100% of jobs**; warranty claim invoicing to brand partners; corporate consolidated invoicing on configurable cycles; multi-method payment recording; advance and deposit management; credit notes and refunds; ageing; automated dunning; collections; revenue assurance | 36 | **BO-06**, BO-04 |
| **M52 APE** | Pay obligations under control: vendor invoice processing with three-way matching; payment scheduling and batch processing; approval workflows by threshold; technician and employee expense capture, approval and reimbursement; vendor ageing | 28 | BO-06 |
| **M50 TRE** | Control cash: bank accounts and statement import with **≥ 90% auto-match**; branch cash drawers and daily reconciliation across 51+ counters; gateway settlement reconciliation; cash position and forecasting; BEFTN disbursement; LC and facilities | 30 | BO-06 |
| **M51 TAX** | Satisfy Bangladesh tax obligations by system behaviour: **Mushak 6.3 tax invoice** per the VAT and SD Act 2012; VAT sub-ledgers; **Mushak 9.1 monthly return filed by the 15th via vat.gov.bd**; **input VAT credit blocked without a valid Mushak 6.3 invoice**; TDS/VDS with quarterly returns; challans and certificates; BIN/TIN validation; NBR e-VAT submission; income-tax schedules | 34 | **BO-10** |
| **M53 REV** | Recognise revenue correctly and settle every party: revenue schedules and deferral across all 14 streams; performance obligations; **marketplace commission calculation and seller settlement**; partner and referral commission; escrow; **payout runs with 100% accuracy and zero unexplained variance**; advertising billing; deposit accounting | 38 | **BO-12**, BO-06 |
| **M49 FXA** | Manage capital: fixed asset register, capitalisation, depreciation, disposal, CWIP, impairment, capital approval, **rental fleet capitalisation and depreciation discipline** | 22 | BO-13, BO-06 |
| **M54 FPA** | Understand cost and profitability: cost per service order (labour + parts + logistics + sub-contract + overhead); branch, business-line and contract profitability; budgets and variance; forecasting; management reporting | 30 | BO-07, BO-08 |

**Category G total: 333 requirements · 185 PW**

**Financial integrity requirements are absolute:** decimal arithmetic in all money paths (no
floating point); every posting reconcilable to its source; **100% unit test coverage on financial
and tax calculations**; soft deletion only; a period cannot close with unposted entries; a
hard-closed period cannot be posted to without logged CFO-approved reopening.

### 8.9 Category H — People & Workforce

> **BR-H:** Employ, schedule, pay, develop and protect a 500+ workforce across 51+ locations in
> full compliance with Bangladesh employment law — and make technician competency an **enforced
> operational control**, not an HR record.
> *(Serves BO-02, BO-10, BO-15)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M21 HCM** | Hold the employee master: personal data; **Bangladesh Labour Act 2006 employment artefacts — appointment letter, identity card, service book, probation limits**; organisation structure; movements; documents; disciplinary records; self-service; exit processing feeding access deprovisioning | 46 | BO-10 |
| **M55 WFM** | Know who is available, when, where and with what skill: biometric and mobile clock-in; **GPS attendance for field technicians**; exceptions; leave types, accruals and balances; **Bangladesh public holiday calendar including moon-dependent dates**; shift patterns and rosters across 51+ branches; overtime capture and approval; working-time rule enforcement | 52 | BO-02, BO-10 |
| **M56 PAY** | Pay accurately and lawfully: monthly and contractual payroll; salary structures; **NBR income tax with AY thresholds, minimum tax and investment rebate**; provident fund; **gratuity at not less than 30 days' wages per completed year**; BEFTN file generation; payslip distribution; annual tax certificates; **payroll approval and release segregation** | 54 | **BO-10** |
| **M57 PIC** | Measure and reward performance: technician scorecards from field-captured events; incentive and commission calculation; appraisal cycles; compensation review; leaderboards | 42 | BO-02 |
| **M22 LMS** | Make competency an enforced control: competency framework and skill matrix; **brand certification tracking across 17+ partners with expiry alerting**; course catalogue, enrolment, assessment and completion; Bengali content; re-certification; **dispatch eligibility enforcement (FR-LMS-039) — a hard block on assigning uncertified technicians to brand warranty work** | 40 | **BO-15**, BO-04 |
| **M58 TAO** | Hire and onboard: requisition and approval, candidate pipeline, assessment, **offer approval segregation**, onboarding checklists, provisioning integration with M29 and M66 | 34 | BO-09 |
| **M59 HSE** | Keep people safe and comply: **Bangladesh Labour Rules 2015 safety committee, safety officer and first-aid obligations**; incident, near-miss and hazard reporting from the technician app; accident notification and compensation; lone-worker safety; electrical and chemical safety; occupational health with restricted medical-data access | 42 | BO-10 |

**Category H total: 310 requirements · 124 PW**

### 8.10 Category I — Governance, Risk, Quality & Knowledge

> **BR-I:** Operate ISO 9001:2015 as a system rather than a paper exercise, manage enterprise risk
> and compliance obligations under a single control framework, retain and dispose of records
> lawfully, and put the Company's technical knowledge in the hands of the technician who needs it —
> offline.
> *(Serves BO-05, BO-10, BO-15, BO-17)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M23 QMS** | Run ISO 9001:2015 and ISO 27001 evidence **in-system**: policies, process register, checklists, internal audit programme with plans, findings and verification; non-conformance; CAPA with **effectiveness verification**; complaint root-cause analysis; supplier quality; **marketplace seller quality gates identical to owned work**; SOP version control; quality KPI dashboards | 32 | **BO-10**, BO-05 |
| **M60 GRC** | Own enterprise risk and compliance: risk register, control library and testing, policy management and attestation, regulatory obligation register with **currency review**, legal matters, insurance, licences, **PDPA 2026 breach notification to the National Data Management Authority**, Chief Data Officer role and reporting line | 34 | **BO-10** |
| **M24 DMS** | Own every document: centralised store with version control and categorisation; template engine; **qualified e-signature for binding contracts and operational e-signature for job completion**; approval workflows with audit trail; Bengali OCR; **records retention enforced by the system, minimum five years for processing records**; legal hold; evidence packs for warranty and ISO audits | 28 | BO-10, BO-04 |
| **M61 KMS** | Put technical knowledge where the work is: repair manuals, wiring diagrams, solution articles, troubleshooting trees, tribal knowledge, brand bulletins and recall notices — **available offline in the technician app**; authoring and review; Bengali and English search; article effectiveness; feeds M32 | 24 | BO-02, BO-05 |

**Category I total: 170 requirements · 78 PW**

### 8.11 Category J — Data, Analytics & Intelligence

> **BR-J:** Make every management decision on live, governed, trustworthy data; automate what is
> repeatable through one workflow engine; and use machine learning where there is enough data to
> learn from — with human confirmation on anything material.
> *(Serves BO-01, BO-02, BO-07, BO-17)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M62 DAT** | Build the analytical foundation: warehouse, pipelines, dimensional model, semantic layer, certified datasets, **data quality tests that block dependent refreshes on failure**, lineage, catalogue, row-level security propagation, feature store | 34 | **BO-17**, BO-07 |
| **M25 BID** | Serve the decision: executive, branch, technician, finance, warranty, contract, marketplace and MSP dashboards; **branch league tables across 51+ branches**; governed self-service without SQL; scheduled distribution; export; threshold and anomaly alerting; embedded analytics per portal; the KPI metric registry | 30 | **BO-07**, BO-17 |
| **M26 AIM** | Apply machine learning where it pays: dispatch assignment scoring and duration prediction; parts demand forecasting; **predictive maintenance**; churn prediction; quality-risk scoring; dynamic pricing models; inference gateway with fallback; model registry; **model cards and drift monitoring on every production model**; **human-in-the-loop on material decisions** | 38 | BO-02, BO-03 |
| **M63 BPA** | Provide **one platform-wide workflow engine serving all modules** — no module implements its own: trigger-action rules; no-code configuration of workflows, forms, thresholds and business rules; approval routing; scheduled jobs with success/failure/duration reporting; automation inventory and audit | 28 | **BO-01** |

**Category J total: 146 requirements · 97 PW**

### 8.12 Category K — Platform & Technology

> **BR-K:** Provide the identity, integration, configuration and master-data foundation on which
> every other module depends — secure, auditable, multi-entity-ready and able to stand up a second
> country without core code change.
> *(Serves BO-10, BO-18, and every other objective indirectly)*

| Module | Business requirement | Reqs | Objectives |
|---|---|---:|---|
| **M28 IPF** | Connect everything, observably: API gateway; the 12 API families; OpenAPI 3.1 generation and validation; **transactional outbox and domain event bus**; webhook delivery with signature verification and replay protection; idempotency; circuit breakers and graceful degradation; integration monitoring, dead-letter handling and alerting; **the 47 external integrations**; sandbox environments | 44 | All |
| **M29 SEC** | Know who is who and what they may do, and prove it: Keycloak identity, SSO, MFA and federation including per-client corporate SAML/OIDC; **RBAC to field level**; **6 data isolation tiers enforced by record rules**; **30 segregation-of-duties controls enforced by the permission engine at role assignment**; step-up authentication; session policy; **immutable audit trail — who, what, when, before, after**; privileged session recording; **access revoked within 1 hour of a leaver event**; field-level encryption for restricted data | 44 | **BO-10** |
| **M64 MDM** | Govern master data: golden-record governance across party, product, location and asset; stewardship workflow; reference data distribution; validation rules; data quality scoring and remediation | 26 | BO-03, BO-17 |
| **M65 GLO** | Make expansion a configuration exercise: multi-entity accounting and consolidation; country pack framework with Bangladesh as reference; locale packs; multi-currency and FX; **cross-border transfer controls with Authority notification records**; entity onboarding runbook | 30 | **BO-18** |
| **M30 ADM** | Configure and operate the platform: entity, branch, zone, calendar and holiday configuration; user and role administration; **feature flags allowing any capability to be disabled without deployment**; system console; job monitoring; licence register; configuration versioning and promotion; translation management | 28 | All |
| **M66 ITS** | Run the Company's own IT: employee helpdesk, internal asset and licence management, change and incident management. *(Specification outstanding — §23.1)* | 22 *(est.)* | BO-09 |
| **M67 PPM** | Deliver projects: corporate rollouts, IT infrastructure engagements, branch openings, internal initiatives; portfolio prioritisation; resource planning; benefits tracking. *(Specification outstanding — §23.1)* | 26 *(est.)* | BO-09 |

**Category K total: 219 requirements *(5 of 7 modules specified)* · 120 PW**

### 8.13 Critical Path and Category Boundary Rules

The build order is constrained by these hard dependencies:

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
4. **Financial postings originate in Category G only.** Other categories raise *billable events*,
   never journal entries.
5. Identity and permission decisions are always delegated to M29; **no module implements its own
   authentication or authorisation**.

### 8.14 Portal Business Requirements

> **BR-P:** Surface the system of record to twelve distinct audiences, each on the device and in
> the language they actually use, without any portal holding authoritative state or implementing a
> business rule.

| Portal | Business requirement | Key business KPI |
|---|---|---|
| **P01 Customer** | Let a customer register devices, book in ≤ 3 steps, track live, approve estimates, pay, manage contracts and loyalty, shop, trade in, request data services, book recycling, and get support in Bengali — on 3G, under 400 KB first load | Online booking **40% → 88%**; > 80% of status enquiries self-served |
| **P02 Technician** | Let a technician run a full day's work — queue, navigation, diagnosis, parts, evidence, estimate, signature, payment, QC — **entirely offline for 24 hours** on a mid-range Android 11 device, in complete Bengali | Daily active usage **> 95%**; job documentation < 5 min; **offline sync failures: zero** |
| **P03 Admin Operations** | Give each back-office role a workspace that opens on the work it actually does, with any record reachable in ≤ 4 clicks and keyboard-first operation for high-volume roles | Walk-in intake **< 3 min**; morning queue dispatched < 10 min; new agent competent < 4 h |
| **P04 Corporate B2B** | Let a corporate client manage their asset estate, raise single and **bulk (CSV) service requests validated against contract coverage**, see SLA and service credits, approve consolidated invoices, and download compliance certificates | > 85% of contracted clients active; > 70% of corporate requests via portal |
| **P05 Vendor & Supplier** | Let a vendor respond to RFQs, acknowledge POs, submit invoices against them, see matching and payment status, and view their own scorecard | > 90% of POs acknowledged; > 85% of invoices submitted; vendor queries **−60%** |
| **P06 Analytics** | Let management see all 14 revenue streams with drill from group revenue to a single job, rank all 51+ branches, and build governed self-service analyses | **100% of management reviews on live data**; manual reporting effort **−90%** |
| **P07 Marketplace Seller** | Let an external engineer or shop register with KYC, list, bid, execute jobs to the same evidence standard as owned work, and be paid transparently | 500 approved active sellers; average rating > 4.4/5; 12-month retention > 65% |
| **P08 Brand Partner** | Let a brand partner receive claims with complete evidence packs, decide them, reconcile remittances, publish rate cards, and see 1000FiX's performance on their brand | **> 80% of claims via portal** rather than email; decision < 10 days; approval > 92% |
| **P09 Logistics & Rider** | Let a rider work a manifest offline with scan, photo, seal, OTP and signature at every custody transfer, and reconcile cash at shift end | POD completeness **100%**; on-time > 93%; **custody breaks: zero** |
| **P10 Contact Centre** | Let an agent handle any channel from one queue with automatic Customer 360 screen-pop and take any action without leaving the conversation | Handling time **−25%**; first-contact resolution > 78%; **screen switches < 3** |
| **P11 Field Auditor** | Let an auditor complete ISO and branch audits offline with evidence, raise classified findings, and verify CAPAs on site | **100% of audits on mobile**; finding-to-CAPA < 5 days; evidence attached 100% |
| **P12 Partner & Referral** | Let an alliance or referral partner generate links, submit leads, track conversion, and see commission statements | > 200 active partners; > 12% of new customers referral-attributed; commission accuracy **100%** |

**Cross-portal business rules:** single sign-on through M29 with no portal credential store · all
traffic through the M28 gateway · Bengali and English throughout with **Bengali default on customer
and field surfaces** · WCAG 2.1 AA · responsive from 320 px · **one design system across all
twelve** · **no business rule implemented client-side** · session, timeout and MFA policy inherited
centrally.

### 8.15 Requirement Traceability to v1.0

**No v1.0 requirement has been deleted.** The mapping is:

| v1.0 requirement range | v2.0 location |
|---|---|
| BR-SRM-001 … BR-SRM-020 | FR-SRM-* (M01), FR-WSR-* (M31) |
| BR-FSM-001 … BR-FSM-017 | FR-FSM-* (M02), FR-LOG-* (M03) where pick & drop moved |
| BR-INV-001 … BR-INV-015 | FR-INV-* (M15), FR-WMS-* (M41) |
| BR-CRM-001 … BR-CRM-010 | FR-CPM-* (M33), FR-CRM-* (M07), FR-LOY-* (M10), FR-CXM-* (M34) |
| BR-FIN-001 … BR-FIN-015 | FR-FIN-* (M19), FR-ARB-* (M20), FR-TAX-* (M51) |
| BR-HRM-001 … BR-HRM-012 | FR-HCM-* (M21), FR-WFM-* (M55), FR-PAY-* (M56), FR-PIC-* (M57), FR-LMS-* (M22) |
| BR-CWM-001 … BR-CWM-012 | FR-CTR-* (M08) and FR-WTY-* (M09) |
| BR-SCM-001 … BR-SCM-007 | FR-PRO-* (M16), FR-SRM2-* (M42) |
| BR-BI-001 … BR-BI-010 | FR-BID-* (M25), FR-DAT-* (M62) |
| BR-DMS-001 … BR-DMS-005 | FR-DMS-* (M24) |
| BR-QMS-001 … BR-QMS-005 | FR-QMS-* (M23), FR-GRC-* (M60) |
| NFR-001 … NFR-030 | NFR-001 … NFR-030 retained; NFR-031 … NFR-101 new |
| BRU-* | Retained, renumbered only where a module split |

Four v1.0 requirements are **superseded** — listed in §23.4.

---

## 9. NON-FUNCTIONAL REQUIREMENTS

**101 numbered non-functional requirements (NFR-001 … NFR-101).** Every one is measurable and is
tested before the relevant wave gate. NFR-001 to NFR-030 are carried forward from v1.0 with
targets raised where v2.0 scope demands it; NFR-031 onward are new.

### 9.1 Performance

| ID | Requirement | Target | Measured by | Pri |
|---|---|---|---|:--:|
| NFR-001 | ERP screen load under normal load | ≤ **2 s p95** *(was 3 s)* | Synthetic monitoring | P0 |
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

### 9.6 Compliance

Full detail, including the Personal Data Protection Act 2026 obligation set, is at §11.4 and
§11.5.

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-021 | **Mushak 6.3 tax invoice** format compliance per the VAT and SD Act 2012 | P0 |
| NFR-100 | **Mushak 9.1 monthly VAT return filed by the 15th of the following month**, via the NBR VAT Online portal (vat.gov.bd) | P0 |
| NFR-101 | **Input VAT credit claimable only against a valid, compliant Mushak 6.3 invoice; the system must block credit claims without one** | P0 |
| NFR-022 | Bangladesh NBR income tax computation compliance | P0 |
| NFR-023 | **ICT Act 2006 and Cyber Security Ordinance 2025 compliance** *(corrects the v1.0 citation of the repealed Digital Security Act 2018)* | P0 |
| NFR-024 | ISO 9001:2015 audit trail and documentation requirements | P0 |
| NFR-025 | ISO 27001 security control alignment | P1 |
| NFR-083 | Bangladesh Labour Act compliance in HR and payroll | P0 |
| NFR-084 | Bangladesh e-waste and environmental handling rules | P1 |
| NFR-085 | Consumer protection obligations on marketplace transactions | P0 |
| NFR-086 | **Split-residency data architecture** — see §11.5 | **P0** |
| NFR-087 | Data-subject rights supportable within legal constraints | P1 |
| NFR-088 | Records retention per the statutory schedule, **enforced by the system** | P0 |
| NFR-089 | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | P2 |
| NFR-090 … NFR-099 | **Personal Data Protection Act 2026 obligation set** — see §11.4 | **P0** |

### 9.7 Maintainability & Operability

| ID | Requirement | Pri |
|---|---|:--:|
| NFR-026 | API-first architecture with documented REST APIs for all integrations | P0 |
| NFR-027 | **No-code configuration** for workflows, forms, thresholds and business rules | P0 |
| NFR-028 | Customisation without modifying core product code | P0 |
| NFR-090* | Unit test coverage ≥ **80%** on custom code; **100% on financial calculations** | P0 |
| NFR-091* | Every module ships with an operational runbook | P0 |
| NFR-092* | Distributed tracing across all services with a single correlation id | P1 |

*\* NFR-090, NFR-091 and NFR-092 appear in both the maintainability and data-protection ranges in
the source register. The data-protection meaning governs where they concern personal data; the
maintainability meaning governs otherwise. **This overlap is a known register defect — see §23.2.***

**Operability standards:** every deployment automated, repeatable and reversible · configuration
versioned and promoted through environments, **never hand-edited in production** · every alert has
a runbook entry; alerts without actions are removed · logs structured and searchable with **no
personal data in logs** · every scheduled job reports success, failure and duration — **silent
failure is a defect** · feature flags allow any new capability to be disabled without deployment ·
database migrations forward-only, tested against a production-sized dataset · capacity reviewed
monthly.

### 9.8 Data Integrity

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

### 9.9 Localisation

| Aspect | Standard |
|---|---|
| Primary language (field & customer) | **Bengali (bn-BD)** |
| Secondary language | English (en) |
| Character encoding | UTF-8 throughout |
| Bengali collation | ICU `bn-BD` for sorting and comparison |
| Bengali fonts | Rendered correctly across Android, iOS, Windows and print output |
| Bengali input | Phonetic and Unicode keyboard; voice-to-text on mobile |
| Number format | **Bangladeshi lakh/crore grouping (12,34,567)** in Bengali locale |
| Currency | **BDT (৳) primary**, two decimal places; multi-currency supported |
| Date format | DD/MM/YYYY; Bengali month names in the Bengali locale |
| Time | 12-hour with Bengali AM/PM equivalents; stored UTC, displayed Asia/Dhaka |
| Calendar | Gregorian with Bangladesh public holidays **including moon-dependent dates** |
| Fiscal year | **July–June** |
| Address | Division → District → Upazila/Thana → Union/Ward → Postcode |
| Phone | +880 with Bangladesh mobile operator validation |
| National ID | 10-digit and 17-digit formats validated |
| Translation completeness | **100% of user-facing strings before any module is accepted** (DoD-08) |
| Translation quality | Professionally translated and reviewed by a native speaker. **Machine translation is not acceptable for release.** |

### 9.10 Device & Environment Support

| Category | Supported |
|---|---|
| Desktop browsers | Chrome, Edge, Firefox (latest two); Safari (latest two) |
| Minimum desktop resolution | **1366×768** — the common branch hardware |
| Mobile OS — technician, rider, auditor | Android 11+ (primary); iOS 15+ (secondary) |
| Mobile OS — customer | Android 9+; iOS 14+ |
| Minimum device specification (field apps) | 3 GB RAM, 32 GB storage, GPS, camera, 4G |
| Network | Functional on 3G; optimised for 4G; full offline where specified |
| Peripherals | Thermal receipt printers, label printers, barcode/QR scanners, biometric devices, signature capture, queue displays, kiosks |
| Printing | A4 and thermal receipt; **Bengali rendering verified on all supported printers** |

---

## 10. BUSINESS RULES

Business rules are the constraints the system enforces on behalf of Company policy. They are the
mechanism by which policy becomes behaviour.

### 10.1 How Rules Are Implemented

| # | Standard | Detail |
|---|---|---|
| BR-STD-01 | Rules are enforced **at the model layer**, never only in the user interface | **A rule bypassed by an API call is not a rule** |
| BR-STD-02 | Every rule has an identifier, an owner and a test | Rules without tests are not released |
| BR-STD-03 | Thresholds are **configuration, not code** | Values change without a deployment |
| BR-STD-04 | Every violation produces a message stating what is wrong and what to do, in the user's language | |
| BR-STD-05 | Hard rules block; soft rules warn and log | Classification is explicit per rule |
| BR-STD-06 | Overrides are possible only where designed, and **always logged with a reason and an approver** | **No silent overrides** |
| BR-STD-07 | Rules are versioned; changing one requires the owner's approval | Audit of what was in force when |

**Rule classification:**

| Class | Behaviour |
|---|---|
| **H — Hard** | Blocks the transaction. No override. |
| **A — Approved override** | Blocks, but a named role may override with a recorded reason. |
| **S — Soft** | Warns and logs; the user may proceed. |
| **C — Computed** | Automatically derives a value; not user-overridable. |

**Verification:** every hard rule must be **negative-tested through both the user interface and the
API** before its module is accepted (DoD-04).

### 10.2 Service & Repair Rules (M01, M31)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SRM-01 | A service order cannot be created without an identified device; an unregistered device must be registered as part of intake | **H** | Ops Director |
| BRU-SRM-02 | A warranty-type order can be created only if the device's warranty is active at the date of the service request | **H** | Warranty Officer |
| BRU-SRM-03 | An AMC-type order can be created only if the device appears on an active contract's covered-asset list | **H** | Account Manager |
| BRU-SRM-04 | A service order cannot reach Completed unless its quality checklist is recorded as passed | **H** | Quality Manager |
| BRU-SRM-05 | An invoice cannot be raised for a service order that is not Completed | **H** | Finance Manager |
| BRU-SRM-06 | A new order for the same device and fault category within 30 days is automatically flagged as rework and linked to the original | C | Quality Manager |
| BRU-SRM-07 | Repair estimates above **BDT 5,000** require documented customer approval before work begins | **H** | Ops Director |
| BRU-SRM-08 | Repair estimates above **BDT 25,000** require customer approval **and** branch manager approval | **H** | Ops Director |
| BRU-SRM-09 | A service order cannot be assigned to a technician lacking a current certification for that brand's warranty work | **H** | Quality Manager |
| BRU-SRM-10 | Privilege Gold and Diamond members automatically receive priority-1 SLA regardless of service type | C | CCO |
| BRU-SRM-11 | Parts cannot be issued against an unapproved paid repair | **H** | Inventory Manager |
| BRU-SRM-12 | A device declared beyond economic repair requires photographic evidence and a second technician's confirmation | **H** | Ops Director |
| BRU-SRM-13 | An estimate expires at its stated validity; expired estimates require re-issue, not extension | **H** | CCO |
| BRU-SRM-14 | Level 3 board-level repairs may be performed only at a workshop with the required equipment and by a certified specialist | **H** | Ops Director |
| BRU-SRM-15 | The SLA clock is suspended only by an approved hold reason and resumes automatically when released | C | Ops Director |
| BRU-SRM-16 | A device uncollected 30 days after Ready enters the abandonment process with statutory notice | C | Branch Manager |
| BRU-SRM-17 | Before/after photographs are mandatory on every warranty job; the job cannot close without them | **H** | Warranty Officer |
| BRU-SRM-18 | Independent QC by a second person is mandatory for repairs above BDT 25,000 | **H** | Quality Manager |
| BRU-SRM-19 | A closed order may be reopened only within the repair warranty period; reopening links it as rework | A | Branch Manager |
| BRU-SRM-20 | Customer data-access notes (passwords, unlock codes) are captured only with explicit consent and are purged at handover | **H** | Quality Manager |

### 10.3 Field Service & Dispatch Rules (M02)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FSM-01 | A technician on leave, off-shift or at capacity is never offered as a candidate | **H** | Dispatch Manager |
| BRU-FSM-02 | Assignment requires a skill match to the required competency for the job | **H** | Quality Manager |
| BRU-FSM-03 | Automatic assignment occurs only when the top candidate's score exceeds the configured confidence threshold | C | Ops Director |
| BRU-FSM-04 | Every dispatcher override of an automatic recommendation requires a reason code | **H** | Ops Director |
| BRU-FSM-05 | GPS capture occurs only during working hours and while on duty | **H** | HR Director |
| BRU-FSM-06 | A job cannot be marked Arrived outside the customer's geofence without an exception reason | A | Dispatch Manager |
| BRU-FSM-07 | On-site payment must be reconciled to the branch cash book by the end of the technician's shift | **H** | Finance Manager |
| BRU-FSM-08 | Van stock cannot exceed the configured maximum per item per technician | **H** | Inventory Manager |
| BRU-FSM-09 | A failed visit requires geotagged evidence before it can be recorded | **H** | Ops Director |
| BRU-FSM-10 | Scheduling that would breach working-time limits requires approved overtime first | **H** | HR Director |
| BRU-FSM-11 | Emergency insertion may displace lower-priority jobs but never an SLA-critical job already at risk | C | Dispatch Manager |
| BRU-FSM-12 | A marketplace seller may be offered a job only if score, certification and category access all qualify | **H** | Marketplace Operations |

### 10.4 Logistics Rules (M03)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-LOG-01 | **No custody transfer without a scan and an identity capture from both parties** | **H** | Logistics Manager |
| BRU-LOG-02 | A consignment cannot be closed without proof of delivery | **H** | Logistics Manager |
| BRU-LOG-03 | Consignments above the declared-value threshold require dual signature and insurance flagging | **H** | CFO |
| BRU-LOG-04 | Any seal break or weight discrepancy automatically raises an incident and blocks onward movement pending review | **H** | Logistics Manager |
| BRU-LOG-05 | Restricted items (lithium batteries, refrigerant) may be carried only by a certified rider or courier | **H** | Quality Manager |
| BRU-LOG-06 | Cash collected on delivery is reconciled per rider per shift with **zero tolerance for unexplained variance** | **H** | Finance Manager |
| BRU-LOG-07 | Logistics charges are waived automatically where contract, warranty or Privilege tier entitles the customer | C | CCO |
| BRU-LOG-08 | Failed delivery is re-attempted per policy, then returned to origin with charge rules applied | C | Logistics Manager |

### 10.5 Contract & Warranty Rules (M08, M09)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CTR-01 | A contract cannot be activated without at least one covered asset or seat, defined entitlements, a billing frequency and approval | **H** | CCO |
| BRU-CTR-02 | Service delivered outside contract scope is billed separately and **never silently absorbed** | **H** | Finance Manager |
| BRU-CTR-03 | On contract expiry, all future scheduled work orders are cancelled and the customer is notified | C | Account Manager |
| BRU-CTR-04 | Entitlement over-consumption is blocked or flagged for billing per configuration; **it is never invisible** | **H** | Finance Manager |
| BRU-CTR-05 | Contract suspension for non-payment follows the defined notice sequence | **H** | CFO |
| BRU-CTR-06 | RAMC package price derives from the number and type of registered appliances, **never a flat fee** | C | CCO |
| BRU-CTR-07 | Healthcare equipment contracts require calibration scheduling as a mandatory element | **H** | Quality Manager |
| BRU-CTR-08 | Service credits are calculated automatically from measured SLA breach; manual credits require CFO approval | C/A | CFO |
| BRU-WTY-01 | A warranty claim cannot be submitted without a completed work order, device serial, at least one before-photo, a technician diagnosis and the replaced-parts list | **H** | Warranty Officer |
| BRU-WTY-02 | A warranty claim is auto-created and queued **within 24 hours** of a warranty work order closing | C | Warranty Officer |
| BRU-WTY-03 | Duplicate claims for the same serial and fault within 90 days are blocked | **H** | Warranty Officer |
| BRU-WTY-04 | Brand-supplied warranty parts cannot be consumed on non-warranty jobs | **H** | Inventory Manager |
| BRU-WTY-05 | Claims are valued in the agreed currency at the rate prevailing on the service completion date | C | Finance Manager |
| BRU-WTY-06 | Privilege discounts apply to **labour only** — never to parts, consumables or transport | C | CCO |
| BRU-WTY-07 | A warranty product cannot be sold on a device that fails the eligibility assessment | **H** | CCO |
| BRU-WTY-08 | A claim not submitted within the brand's stated window is escalated as revenue leakage **before it expires** | C | Finance Director |

### 10.6 Inventory & Procurement Rules (M15, M16, M41, M42, M44)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-INV-01 | Stock cannot be issued against an unapproved paid repair | **H** | Inventory Manager |
| BRU-INV-02 | Inter-branch transfer requires the source branch manager's approval and the destination's confirmed receipt | **H** | Inventory Manager |
| BRU-INV-03 | A purchase order cannot be raised for an item whose network-wide stock already exceeds the maximum level | A | Procurement Manager |
| BRU-INV-04 | Brand consignment stock is excluded from own-stock valuation and reported separately | C | CFO |
| BRU-INV-05 | Expired shelf-life stock cannot be issued | **H** | Inventory Manager |
| BRU-INV-06 | Stock adjustments above threshold require approval with a reason code | **H** | CFO |
| BRU-INV-07 | Goods failing inspection go to quarantine and **never to available stock** | **H** | Quality Manager |
| BRU-INV-08 | Serialised parts must have their serial captured at both receipt and issue | **H** | Inventory Manager |
| BRU-SCM-01 | A vendor invoice cannot be approved for payment without a matched purchase order and goods receipt within tolerance | **H** | Finance Manager |
| BRU-SCM-02 | A purchase order cannot be issued to a vendor who is not active and approved | **H** | Procurement Manager |
| BRU-SCM-03 | The same user cannot create a vendor and approve that vendor's invoice | **H** | CFO |
| BRU-SCM-04 | Import landed cost must be allocated before received stock can be valued as final | C | Finance Manager |
| BRU-SCM-05 | Sub-contracted devices must move under a logistics consignment with full custody evidence | **H** | Ops Director |

### 10.7 Financial Rules (M19, M20, M39, M51, M53)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FIN-01 | Every customer invoice includes VAT at the applicable rate and displays the Company's BIN | **H** | CFO |
| BRU-FIN-02 | Cash receipts above **BDT 50,000** require the customer's NID to be recorded | **H** | CFO |
| BRU-FIN-03 | A payment cannot be recorded against a cancelled invoice | **H** | Finance Manager |
| BRU-FIN-04 | A credit note requires approval by the Finance Manager or above | **H** | CFO |
| BRU-FIN-05 | A financial period cannot be closed while unposted entries exist in it | **H** | CFO |
| BRU-FIN-06 | Once hard-closed, no posting is possible without CFO-approved reopening, which is logged | **H** | CFO |
| BRU-FIN-07 | Foreign-currency balances are revalued at period end at the official rate | C | Finance Manager |
| BRU-FIN-08 | Marketplace transactions are accounted per the declared principal-or-agent model; **the model cannot vary by transaction** | **H** | CFO |
| BRU-FIN-09 | TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise | **H** | CFO |
| BRU-FIN-10 | Branch cash must be reconciled and closed daily; an unclosed shift blocks the next shift's opening | **H** | Finance Manager |
| BRU-BIL-01 | An invoice is generated automatically on job closure; manual creation for a completed job requires approval | C/A | Finance Manager |
| BRU-BIL-02 | Subscription billing runs on the contract's cycle; a missed cycle raises an exception, **never a silent skip** | **H** | Finance Manager |
| BRU-BIL-03 | A seller payout is held for the configured period after job completion and **blocked entirely while a dispute is open** | **H** | CFO |
| BRU-BIL-04 | Commission is reversed automatically when the underlying transaction is refunded or a dispute is decided against the seller | C | Finance Manager |
| BRU-BIL-05 | Refunds are issued to the original payment method unless the customer accepts store credit | C | Finance Manager |
| BRU-BIL-06 | Deferred revenue is released only per the recognition schedule; manual release requires CFO approval | **H** | CFO |
| BRU-BIL-07 | A consolidated corporate invoice cannot be issued until every constituent job is Completed and priced | **H** | Finance Manager |

### 10.8 Marketplace Rules (M12)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ECM-01 | A seller cannot transact until documents are verified, the agreement is digitally signed, and an administrator has approved | **H** | Marketplace Operations |
| BRU-ECM-02 | Only customers with a completed transaction may leave a review | **H** | Marketplace Operations |
| BRU-ECM-03 | **Marketplace jobs are held to the same evidence, QC and warranty standards as owned jobs** | **H** | Quality Manager |
| BRU-ECM-04 | A seller whose performance score falls below threshold has visibility reduced automatically; below the suspension threshold they are suspended | C | Marketplace Operations |
| BRU-ECM-05 | Seller access to customer contact data is limited to awarded jobs and expires a defined period after completion | **H** | CTO |
| BRU-ECM-06 | Paid boost and advertising never override the disclosure that a listing is promoted | **H** | CCO |
| BRU-ECM-07 | A seller cannot list in a category for which they hold no verified qualification | **H** | Marketplace Operations |
| BRU-ECM-08 | Registration expiry automatically suspends the seller until renewed | C | Marketplace Operations |
| BRU-ECM-09 | **Disputes are decided by 1000FiX, not by the parties**; the decision and its evidence are recorded | **H** | Marketplace Operations |
| BRU-ECM-10 | Stock cannot be sold below available quantity; out-of-stock items cannot be ordered | **H** | Inventory Manager |

### 10.9 Rental, Refurbishment & E-Waste Rules (M13, M14, M18)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-RNT-01 | A rental asset cannot be dispatched without a completed pre-dispatch condition report | **H** | Retail Manager |
| BRU-RNT-02 | A rental agreement requires a signed condition report and the deposit received before handover | **H** | Finance Manager |
| BRU-RNT-03 | Damage charges derive from the difference between outbound and inbound condition reports; discretionary charges require approval | C/A | Retail Manager |
| BRU-RNT-04 | A returned rental asset re-enters the available pool only after cleaning, servicing and functional test | **H** | Retail Manager |
| BRU-RNT-05 | Overdue rentals accrue charges automatically per the tariff with escalating notification | C | Finance Manager |
| BRU-TRF-01 | **No trade-in device proceeds to refurbishment or resale without a certified data destruction record** | **H** | Quality Manager |
| BRU-TRF-02 | Provenance and identity checks (including stolen-device screening where available) must pass before a trade-in offer is paid | **H** | Retail Manager |
| BRU-TRF-03 | A refurbished unit cannot be listed for sale without a completed QA test protocol and an assigned grade | **H** | Quality Manager |
| BRU-TRF-04 | Battery health and known defects must be disclosed on every refurbished listing | **H** | CCO |
| BRU-TRF-05 | A supervisor grade override requires a recorded justification | A | Quality Manager |
| BRU-ESG-01 | **No device may leave for recycling without a certified wipe or physical destruction record** | **H** | Quality Manager |
| BRU-ESG-02 | E-waste may be transferred only to a partner whose certification is current at the transfer date | **H** | Quality Manager |
| BRU-ESG-03 | Every recycled unit must have a retrievable disposal certificate | **H** | Quality Manager |
| BRU-ESG-04 | Hazardous items follow their specific handling, storage and transport rules without exception | **H** | Quality Manager |

### 10.10 HR, Competency & Quality Rules (M21, M22, M23, M55, M56, M57)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-HRM-01 | A technician cannot be assigned brand warranty work once their certification for that brand has expired | **H** | Quality Manager |
| BRU-HRM-02 | Overtime must be pre-approved by the line manager before it counts for payroll | **H** | HR Director |
| BRU-HRM-03 | Performance incentive is calculated only after the minimum monthly job threshold is met | C | HR Director |
| BRU-HRM-04 | Leave cannot be approved where it would take team coverage below the configured minimum | A | HR Director |
| BRU-HRM-05 | Payroll cannot be finalised until attendance for the period is verified and locked | **H** | HR Director |
| BRU-HRM-06 | Payroll requires **two approvals — HR Manager and CFO** | **H** | CFO |
| BRU-HRM-07 | An employee's own payroll record is visible to them and to HR/finance, **never to peers or line managers below HR Manager** | **H** | HR Director |
| BRU-LMS-01 | Mandatory training must be completed within the assigned deadline; overdue mandatory training restricts the affected work types | **H** | Quality Manager |
| BRU-LMS-02 | A marketplace engineer cannot be activated in a category without passing that category's qualification | **H** | Marketplace Operations |
| BRU-QMS-01 | A quality checklist cannot be marked complete with unanswered mandatory items | **H** | Quality Manager |
| BRU-QMS-02 | Every non-conformance requires a root cause and a CAPA before it can be closed | **H** | Quality Manager |
| BRU-QMS-03 | A CAPA cannot be closed without **effectiveness verification** after the defined interval | **H** | Quality Manager |
| BRU-QMS-04 | A complaint cannot be closed without confirming the outcome with the customer | **H** | Quality Manager |
| BRU-QMS-05 | Repeated non-conformance in the same process triggers a mandatory management review item | C | Quality Manager |

### 10.11 Security, Data & Platform Rules (M06, M24, M29, M30, M26)

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SEC-01 | Admin, finance and HR portal access requires **MFA at every login** | **H** | CTO |
| BRU-SEC-02 | Sensitive actions (payouts, payroll finalisation, data-case access, bulk export) require **step-up authentication** | **H** | CTO |
| BRU-SEC-03 | Access to a data-recovery case is limited to the assigned team; **every access is logged** | **H** | CTO |
| BRU-SEC-04 | Recovered customer data is purged at the agreed date unless a documented hold applies | **H** | CTO |
| BRU-SEC-05 | Personal data cannot be exported in bulk without approval, and every export is logged | **H** | CTO |
| BRU-SEC-06 | A leaver's access is revoked **within one hour** of the leaver event | **H** | HR Director / CTO |
| BRU-SEC-07 | Incompatible duty combinations cannot be assigned; exceptions are time-boxed and reported | **H** | CFO / CTO |
| BRU-SEC-08 | Production data used in non-production environments **must be masked** | **H** | CTO |
| BRU-DMS-01 | Documents cannot be deleted before their retention period expires | **H** | Quality Manager |
| BRU-DMS-02 | Documents under legal hold cannot be disposed of regardless of retention | **H** | Quality Manager |
| BRU-DMS-03 | A signed document cannot be modified; changes require a new version and a new signature | **H** | Quality Manager |
| BRU-ADM-01 | Master data changes above the defined significance require approval before taking effect | **H** | CTO |
| BRU-ADM-02 | Configuration changes in production must be traceable to an approved change record | **H** | CTO |
| BRU-AIM-01 | **A model recommendation with material customer or financial impact requires human confirmation** | **H** | CTO |
| BRU-AIM-02 | No model output may cross a defined business guard rail (price floor/ceiling, certification requirement, safety rule) | **H** | CTO |
| BRU-AIM-03 | **Recovered customer data (M06) is never used as training data** | **H** | CTO |

### 10.12 Segregation of Duties

Thirty SoD controls must be enforced **by the permission engine at role assignment**, not by
policy. The registered set:

| ID | Incompatible duties | Risk | Enforcement |
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

> **A further 18 controls (SOD-13 … SOD-30) are implemented in module specifications but are not
> yet in the central matrix** — including SOD-29 (payroll approver cannot release the bank file)
> and SOD-30 (M57 calculates the incentive; only M56 can pay it). **Controls that cannot be
> evidenced are, for audit purposes, controls that do not exist.** Registration of all 30 is
> required before Wave 1 build. See §23.2.

Exceptions require CFO or CTO approval, are time-boxed, and appear on a standing exception report
reviewed quarterly.

### 10.13 Approval Authority Matrix

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
| Payroll run | Any | **HR Manager + CFO** |
| **Data destruction** | Any | **Data Services Technician + witness** |
| Access request — standard / privileged | Any | Line Manager / Line Manager + IT Admin + CTO |
| SoD exception | Any | CFO or CTO, time-boxed |

### 10.14 External Party Access Rules

| ID | Rule |
|---|---|
| EA-01 | An external party may see only records where they are a named party |
| EA-02 | An external party **never** sees cost, margin, internal notes or other parties' data |
| EA-03 | Corporate portal users see only their own company's data, further scoped by their role in that company |
| EA-04 | A marketplace seller sees the customer's name, contact and address **only for an awarded job, and only until a defined period after completion** |
| EA-05 | A brand partner sees only claims and service data relating to their own brand |
| EA-06 | A vendor sees only their own purchase orders, receipts and invoices |
| EA-07 | A courier partner sees only consignments assigned to them, with the minimum data needed to deliver |
| EA-08 | External sessions time out after 30 minutes of inactivity |
| EA-09 | **MFA is mandatory for any external action with financial consequence** |
| EA-10 | Every external access to customer personal data is logged and reportable |
| EA-11 | External API access is scoped by credential; **scope cannot be widened by request parameters** |
| EA-12 | Bulk export by external parties is limited, rate-controlled and logged |

---

## 11. DATA REQUIREMENTS

### 11.1 Data Model Scale and Standards

**225 entities** across the eleven categories. Growth from v1.0:

| Domain | v1.0 entities | v2.0 entities | Notable additions |
|---|---:|---:|---|
| Service core | 11 | 26 | Workshop bench, RMA, job batch, service task, escalation, session |
| Logistics | 0 | 11 | Consignment, leg, custody event, courier partner, route manifest, POD |
| Managed services | 0 | 14 | Monitored asset, alert, patch job, runbook, MSP ticket, health score |
| Data services | 0 | 8 | Recovery case, media chain-of-custody, wipe certificate, backup plan, restore test |
| Commercial | 8 | 31 | Price book, price rule, quotation, bid, subscription, entitlement, usage record |
| Marketplace | 0 | 22 | Seller, listing, offer, order split, commission, payout, wallet, dispute, review, ad placement |
| Rental | 0 | 12 | Rental asset, agreement, reservation, condition report, deposit, damage claim |
| Refurbishment | 0 | 10 | Trade-in offer, grading report, refurb work order, resale lot, provenance record |
| Assets & IoT | 2 | 15 | Asset estate, telemetry stream, alert rule, health index, maintenance plan |
| ESG | 0 | 7 | Collection event, recycling batch, material recovery, disposal certificate |
| Finance & billing | 9 | 28 | Revenue schedule, settlement run, commission ledger, escrow, credit note reason, FX rate |
| People & competency | 4 | 17 | Competency, certification track, assessment, enrolment, shift pattern |
| Platform | 6 | 24 | Entity, tenant, locale pack, feature flag, event log, integration credential |
| **Total** | **~40** | **225** | |

**Mandatory modelling standards:**

| # | Standard | Business consequence |
|---|---|---|
| DM-03 | Every transactional record carries `company_id`, `operating_unit_id`, and where relevant `zone_id`, `cost_center_id`, `business_line_id` | Multi-entity, multi-branch, multi-business-line reporting works from day one; **BO-18 becomes configuration, not rebuild** |
| DM-06 | **Soft delete only** — business records are archived, never hard-deleted | Audit trail and legal defensibility preserved |
| DM-07 | Money uses `Monetary` with explicit currency; **never floats** | Financial integrity |
| DM-08 | Timestamps stored UTC, presented Asia/Dhaka | Multi-country readiness |
| DM-10 | Every state machine explicit, with the transition map declared in one place | Testability and audit |
| DM-12 | Referential integrity enforced **at the database level** | Data cannot be corrupted by an application bug |
| DM-13 | Business-line specialisation via one-to-one extension models, **not by widening the core model** | The Service Order does not become a god-object |
| DM-14 | Every field classified **S0–S3**; S3 encrypted at field level and access-logged | PDPA and ISO 27001 compliance by design |
| DM-15 | Every state change writes to the outbox table **in the same transaction** | No lost events, no phantom events |

### 11.2 Core Entity Relationships

```
Party (1) ──┬── (N) Party Role  [customer · employee · vendor · seller · brand · referrer]
            ├── (N) Asset
            ├── (N) Service Order
            ├── (N) Contract
            └── (N) Identity Document  [S3 · Bangladesh-resident]

Asset (1) ──┬── (N) Service Order
            ├── (N) Warranty Register
            ├── (N) Condition Report
            ├── (0..1) Rental Asset      ─┐
            ├── (0..1) Monitored Asset    │  an asset may become
            ├── (0..1) Refurb Unit        │  any of these over
            └── (0..1) E-Waste Item      ─┘  its lifecycle

Contract (1) ──┬── (N) Entitlement ── (N) Entitlement Consumption ── (1) Service Order
               ├── (N) Covered Asset
               ├── (N) Contract SLA ── (N) SLA Measurement ── (0..1) SLA Credit
               └── (N) PM Schedule ── (N) PM Visit

Service Order (1) ──┬── (N) Work Order ──┬── (N) Diagnostic Result
                    │                    ├── (N) QC Result
                    │                    ├── (N) Part Consumption ── (1) Part
                    │                    └── (1) Technician ── (N) Certification Record
                    ├── (1) Estimate ── (N) Estimate Line
                    ├── (0..1) Warranty Claim ── (N) Claim Evidence
                    ├── (N) SLA Clock
                    └── (N) Billable Event ── (N) Charge ── (1) Invoice ── (N) Payment

Consignment (1) ── (N) Leg ── (N) Custody Event  [GPS · timestamp · both parties]
                            └── (0..1) POD Record

Marketplace Order (1) ── (N) Fulfilment Order ── (1) Seller
                                               └── (N) Commission Entry ── (1) Payout Run
```

### 11.3 Data Classification

Every field is classified. Classification drives encryption, masking, access logging, retention
**and residency**.

| Class | Description | Examples | Controls |
|---|---|---|---|
| **S0 — Public** | No restriction | Service catalogue, branch addresses, published prices | None |
| **S1 — Internal** | Business data, staff-visible | Service orders, stock levels, schedules | RBAC |
| **S2 — Confidential** | Restricted business or personal data | Customer contact details, pricing, margins, aggregate salaries | RBAC + field permissions + access log |
| **S3 — Restricted** | Highest sensitivity | **NID numbers, bank details, individual payroll, recovered customer data, call recordings, biometric templates, seller KYC documents** | Field-level encryption + explicit grant + step-up authentication + full access log + retention enforcement |

**S3 field inventory:** national ID number · bank account details · individual salary and payslip ·
recovered customer data index (per-case keys, dual control) · call recordings · biometric
attendance templates (irreversible, never exported) · seller KYC documents · customer identity
documents · API and integration credentials (vault-stored, never displayed after creation).

**Field-level visibility restrictions:** `unit_cost` / `total_cost` / `margin` ·
`salary` / `allowances` / `deductions` · `nid_number` · `bank_account` · `recovered_data_index` ·
`call_recording_url` · `commission_rate` · `seller_kyc_document` · `technician_incentive_detail` ·
`customer_credit_limit` · `internal_note` (**never exposed to any external portal**) ·
`vendor_price` · `model_confidence` / `model_features`.

### 11.4 Personal Data Protection Act 2026 — Statutory Data Obligations

> **This section corrects a material error in BRD v1.0**, which cited the Digital Security Act 2018
> as the governing statute. That Act has been repealed **twice**. Every citation below carries a
> verified-on date under governance rule DoD-17.

| Statute | Status | Verified |
|---|---|---|
| Digital Security Act 2018 | **Repealed** by the Cyber Security Act 2023 (13 September 2023) | 2026-08-12 |
| Cyber Security Act 2023 | **Repealed** by the Cyber Security Ordinance 2025 (21 May 2025) | 2026-08-12 |
| **Cyber Security Ordinance 2025** | **In force** | 2026-08-12 |
| **Personal Data Protection Act 2026 (Law 63 of 2026)** | **In force** — enacted April 2026. Complaint and enforcement mechanisms activate **~13 May 2027, inside Wave 4** | 2026-08-12 |
| ICT Act 2006 | In force | 2026-08-12 |
| VAT and Supplementary Duty Act 2012 | In force | 2026-08-12 |
| Bangladesh Labour Act 2006 (as amended) / Labour Rules 2015 | In force | 2026-08-12 |

**The regulator is the National Data Management Authority.** These obligations are **all P0**:

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
| NFR-098 | Treat a processor's processing as the controller's own; **flow equivalent obligations to every processor and sub-processor by contract** — including the implementation partner | M42, M60 |
| NFR-099 | **Restrict large-scale transfer of Sensitive Personally Identifiable Data** — government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information and criminal records — notify the Authority of cross-border transfers and disclose safeguards | M29, M65 |

**Penalty exposure: up to BDT 25 lakh** for security failures or rights violations, and up to
**BDT 50 lakh** for significant data fiduciaries, with additional fines for repeated violations and
turnover-linked penalties under the amending ordinance. Registered as **risk RSK-032, rated
Critical**.

**At 250,000+ customers per month, 1000FiX will almost certainly qualify as a significant data
fiduciary.** Classification assessment and CDO appointment are **decision D-15**, required by Wave
4 minus 3 months.

### 11.5 Data Residency — Split-Residency Architecture

> **This is the single most consequential data constraint in the programme, and it changed after
> BRD v1.0 was issued.** v1.0 assumed a single Singapore region (ASM-13). That position conflicts
> with NFR-099.

| ID | Requirement | Pri |
|---|---|:--:|
| **NFR-086** | **Split-residency data architecture.** Sensitive Personally Identifiable Data as defined by the PDPA 2026 — NID, passport, TIN, biometric templates, and recovered customer data held under M06 — is stored in a **Bangladesh-resident data store**. The remainder of each record may be held in the regional store. **Records are joined by a resident key, never by duplicating the sensitive field.** | **P0** |
| NFR-086a | The data model must carry a **residency classification on every field**, enforced **at write time — not by convention** | **P0** |
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
> design is required before the Wave 1 architecture is fixed** (dependency DEP-31). Assumption
> **ASM-21** — that a Bangladesh-resident store of adequate reliability and performance is
> procurable — is **not yet proven**. **Retrofitting residency into a live system is the most
> expensive class of rework in this programme.**

### 11.6 Data Migration

#### 11.6.1 Source domains and volumes

| Source | Data | Estimated volume | Target module | Wave | Pri |
|---|---|---|---|:--:|:--:|
| Customer spreadsheets | Customer master | 100,000+ | M33, M07 | W1 | P0 |
| Device registry spreadsheets | Customer devices | 200,000+ | M17 | W1 | P0 |
| Branch & employee master | Locations, staff, org structure | 500+ employees, 51+ branches | M30, M21 | W1 | P0 |
| Service history spreadsheets and paper | Past service orders | 500,000+ | M01 (archive) | W2 | P1 |
| `station.1000fix.com` | Order tracking records | TBD | M01 | W2 | P1 |
| Branch inventory spreadsheets | Stock across 51+ locations | 10,000 SKUs × 51 | M15 | W2 | P0 |
| Accounting software export | Invoices, payments, GL (3 years) | 1,000,000+ | M19 | W3 | P0 |
| Vendor spreadsheets | Vendor master, open POs | 200+ | M16 | W3 | P1 |
| Paper archive | Service reports, warranty documents | Significant | M24 | W3–W6 | P2 |
| Contract spreadsheets | AMC / RAMC / corporate | 5,000+ | M08 | W4 | P0 |
| Brand partner portals | Open warranty claims | ~2,000 | M09 | W4 | P0 |
| HR spreadsheets and files | Employee records, certifications | 500+ | M21, M22 | W5 | P0 |
| Quality records | Open NCRs, CAPAs, findings | TBD | M23 | W5 | P1 |

#### 11.6.2 Migration requirements

| ID | Requirement | Pri |
|---|---|:--:|
| MIG-001 | Detailed migration plan with **field-level source-to-target mapping**, per wave | P0 |
| MIG-002 | **Profiling before every load** — completeness, validity, duplication, staleness reported to the data owner | P0 |
| MIG-003 | Cleansing performed **in the source** where possible, with the business data owner accountable | P0 |
| MIG-004 | Validation rules and **reconciliation reports with control totals** on every load | P0 |
| MIG-005 | Trial migration into `staging` with business UAT before every cutover | P0 |
| MIG-006 | **Signed reconciliation** by the named data owner as a wave gate criterion | P0 |
| MIG-007 | Documented, rehearsed rollback plan for every cutover | P0 |
| MIG-008 | Migration tooling delivered to the Company, repeatable and re-runnable | P0 |
| MIG-009 | Incremental/delta migration during the parallel-run period | P1 |
| MIG-010 | Historical data migrated with **audit trail preservation** and **legacy identifiers retained on every record** for lookup and audit | P0 |
| MIG-011 | Bengali text conversion and encoding normalisation to UTF-8 | P1 |
| MIG-012 | An **archive area for uncleansable records** — retrievable, flagged, and excluded from operational logic | P1 |
| MIG-013 | Financial history reconciled **to the trial balance** before Gate 3 | P0 |
| MIG-014 | **Residency classification applied at migration**; no residency-restricted field lands in the regional store | P0 |
| MIG-015 | Personal data migrated only with a lawful basis recorded; **transparency notice obligations addressed for migrated data subjects** | P0 |

> **Assumption ASM-03 and risk RSK-014.** Existing customer and device data is assumed exportable
> at **≥ 80% quality**. If false, migration effort increases materially and a manual cleansing
> programme is required. Data owners are accountable for cleansing in the source.

### 11.7 Data Retention

| Data type | Retention period | Basis |
|---|---|---|
| **Processing records (PDPA)** | **Minimum 5 years** | **PDPA 2026, NFR-095** |
| Customer records | 7 years after last transaction | Bangladesh business law |
| Financial transactions | 7 years | Companies Act / NBR |
| VAT records | 7 years | VAT and SD Act 2012 |
| Service records | 5 years | Operational and warranty purposes |
| Warranty claims | 7 years | Brand partner audit requirements |
| Employee records | 10 years after termination | Bangladesh Labour Act |
| Audit logs | 5 years | ICT Act / Cyber Security Ordinance 2025 / ISO 27001 |
| Call recordings | Per policy, enforced by the system | PDPA + consumer protection |
| **Recovered customer data (M06)** | **Purged at the agreed date unless a documented hold applies** | **BRU-SEC-04, contractual** |
| Biometric templates | While employment subsists + statutory minimum | PDPA sensitive data |
| Backups | Daily/30 days · weekly/1 year · monthly/7 years | NFR-030 |

**Retention is enforced by the system** (NFR-088), not by policy. Documents cannot be deleted
before retention expires (BRU-DMS-01) and legal hold overrides retention absolutely (BRU-DMS-02).

---

## 12. BUSINESS PROCESS FLOWS

### 12.1 The Fifteen Critical Business Journeys

These journeys define the business end-to-end. **Each must be covered by an automated end-to-end
test run nightly.** They are the definition of "the system works".

| # | Journey | Modules | First live |
|---|---|---|:--:|
| 1 | Book online → dispatch → field repair → invoice → pay → close → survey | M01, M02, M20, M34, P01, P02 | W3 |
| 2 | Walk-in intake → workshop repair → estimate → approval → QC → handover → pay | M04, M31, M36, M01, M20 | W3 |
| 3 | Pick & drop collection → workshop → return delivery → invoice | M03, M31, M20, P09 | W3 |
| 4 | Warranty job → claim creation → submission → approval → reimbursement → reconciliation | M01, M09, M53, P08 | W4 |
| 5 | AMC sale → activation → preventive schedule → visit → renewal | M36, M08, M39, M01, M02 | W4 |
| 6 | MSP alert → ticket → remote resolution → SLA measurement → monthly service report | M05, M08, M25, P04 | W5 |
| 7 | Marketplace order → seller quote → customer selection → job → review → commission → payout | M12, M11, M53, P07 | W7 |
| 8 | Rental reservation → delivery → return → damage assessment → billing | M13, M03, M17, M20 | W6 |
| 9 | Trade-in request → offer → intake → data wipe → refurbishment → grading → resale | M14, M06, M38, M15 | W6 |
| 10 | E-waste collection → triage → destruction → recycling → disposal certificate | M18, M03, M24 | W8 |
| 11 | Data recovery case → custody → recovery → handover → purge certificate | M06, M24 | W6 |
| 12 | Purchase requisition → PO → receipt → inspection → three-way match → payment | M16, M15, M52 | W3 |
| 13 | Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips → posting | M55, M56, M19 | W5 |
| 14 | Complaint → non-conformance → root cause → CAPA → verification → closure | M34, M23 | W5 |
| 15 | Month-end close → reconciliation → VAT return → management pack | M19, M50, M51, M25 | W4 |

### 12.2 Process 1 — Multi-Channel Service Request to Cash

**Actors:** Customer · Contact Centre Agent / Service Centre Agent · System · Dispatcher ·
Technician · Finance

```
CUSTOMER              SYSTEM                     DISPATCH          TECHNICIAN
    │                    │                          │                  │
Contact via any ───► AUT-001                        │                  │
channel (portal,     Create service order           │                  │
app, phone 16743,    Identify party (M33)           │                  │
WhatsApp, chatbot,   Identify/register device (M17) │                  │
walk-in, e-mail)     Evaluate entitlement:          │                  │
    │                  warranty (M09)?              │                  │
    │                  contract (M08)?              │                  │
    │                  else paid (M11)              │                  │
    │                Assign SLA policy, start clock │                  │
    │                Acknowledge on preferred       │                  │
◄── Ack + tracking     channel (M27)                │                  │
    link             Enter dispatch queue           │                  │
    │                    │                          │                  │
    │                AUT-002 Score candidates ─────►│                  │
    │                  skill · certification (M22)  │                  │
    │                  location · workload          │                  │
    │                  van stock (M15)              │                  │
    │                Auto-assign above confidence   │                  │
    │                  else ranked list ───────────►│ Dispatcher       │
    │                                          decides / overrides     │
    │                                          (reason code logged)    │
    │                AUT-003 Notify ───────────────────────────────────►│
◄── Dispatched          publish tracking link                     Accept
    notification        update route (VROOM/OSRM)                 Navigate
    │                    │                          │                  │
◄── En route + ETA   GPS stream (Traccar) ─────────►│ Live map    Arrive
    live map            geofence arrival detection  │             (auto-timestamp)
    │                    │                          │                  │
    │                    │                          │             Diagnose
    │                AUT-004 Draft estimate from    │             (guided tree)
    │                  fault code + standard repair │             Photo before
◄── Estimate (M36)   AUT-005 Send · start expiry    │                  │
 ──► Approve/part-      timer · remind 24h/48h      │                  │
     approve/decline    │                          │                  │
    │                AUT-006 Reserve parts (M15)    │             Scan parts
    │                  release work order           │             Execute repair
    │                    │                          │             Photo after
    │                    │                          │             QC checklist
    │                BRU-SRM-04 QC must pass ───────┼────────────► blocked if not
◄── Sign (e-sig)         │                          │             Customer signs
    │                AUT-008 Service report         │             Complete job
    │                  Invoice ≤ 5 s (M20, NFR-040) │                  │
◄── Invoice +           Mushak 6.3 (M51)            │                  │
    payment link        Privilege discount (M10)    │                  │
 ──► Pay bKash/       AUT-024 Match payment         │                  │
     Nagad/card         Post to ledger (M19)        │                  │
    │                    │                          │                  │
◄── Receipt          Warranty? ──► AUT-018 Create claim + evidence pack (M09)
◄── CSAT survey      AUT-010 Survey after delay (M34)                  │
    │                Update KPIs, warehouse (M25/M62)                  │
```

**Decision points:** warranty active → warranty type, brand claim · contract active → AMC type,
entitlement consumed · estimate > BDT 5,000 → customer approval required before work
*(BRU-SRM-07)* · estimate > BDT 25,000 → + branch manager *(BRU-SRM-08)* · uncertified technician
→ **hard block** *(BRU-SRM-09)* · no technician available → SLA escalation at 50/75/90/100%
*(AUT-009)*.

### 12.3 Process 2 — Warranty Claim to Reimbursement

```
WARRANTY WORK ORDER CLOSED
         │
AUT-018  System creates the claim within 24 h (BRU-WTY-02)
         Assembles the evidence pack: before/after photos, diagnosis,
         parts replaced, serial, technician certification (M22), purchase proof
         Validates completeness against the brand's rule set (M09 brand rule engine)
         │
         ├── Incomplete ──► Task to Warranty Officer with a specific checklist
         │
AUT-019  Complete ──► Submit in the brand's required format (P08 or API)
         │            Duplicate check: same serial + fault within 90 days? (BRU-WTY-03)
         │
AUT-020  Brand response:
         ├── Approved ──────► Queue for billing (M20) ──► Await remittance
         ├── Part-approved ─► Record variance; queue the approved portion
         ├── Rejected ──────► Dispute task + reason analysis ──► feeds M23 CAPA
         └── More info ─────► Supplementary evidence ──► re-submit
         │
AUT-021  Brand remittance received ──► Match to claims ──► Post to ledger (M19)
         Unmatched ──► Manual matching queue
         │
BRU-WTY-08  Claim approaching the brand's submission window ──► escalate as
            revenue leakage BEFORE it expires
```

**Target outcomes:** claims created within 24 h · **submitted within 72 h for 95%+** ·
first-submission approval **≥ 90%** · service-to-reimbursement **< 45 days** · leakage **< 2%**.

### 12.4 Process 3 — Inventory Replenishment and Van Stock

```
CONTINUOUS   M15 monitors stock at every location + every van
             │
AUT-031      Stock reaches reorder point (M43 forecast-informed)
             ──► Alert + draft purchase requisition with recommended quantity
             │
             BRU-INV-03: blocked if network-wide stock already exceeds maximum
             │
AUT-032      Requisition approved (threshold per §10.13)
             ──► PO generated and transmitted (M16); acknowledgement tracked (P05)
             │
AUT-033      Goods received ──► inspection (BRU-INV-07: fail ⇒ quarantine, never stock)
             ──► landed cost allocated (M44, BRU-SCM-04)
             ──► stock updated; serials captured (BRU-INV-08)
             │
AUT-034      Three-way match successful ──► vendor invoice to payment schedule (M52)
             Failed ──► exception queue (BRU-SCM-01 blocks payment)
             │
DAILY        AUT-035 Technician shift ends ──► van stock reconciled
             ──► variance reported to branch manager (target < 2%, then < 1%)
             │
PERIODIC     AUT-036 Cycle count due ──► count task list by ABC class and location
             AUT-037 Dead stock threshold ──► disposition recommendation
```

### 12.5 Process 4 — Contract Lifecycle (AMC / RAMC / MSP)

```
Opportunity (M07) ──► Quotation (M36) ──► Customer accepts
         │
AUT-016  Contract activated (M08) from a template for one of 14 product families
         BRU-CTR-01: blocked without covered assets, entitlements, billing frequency, approval
         ──► Generate the FULL preventive-maintenance schedule for the term
         ──► Healthcare family: calibration scheduling mandatory (BRU-CTR-07)
         ──► Subscription created (M39) if recurring
         │
AUT-017  PM visit due − lead time ──► create work order ──► dispatch queue
         │
ONGOING  Entitlement consumed per service order (BRU-CTR-04: never invisible)
         SLA measured; breach ⇒ service credit calculated automatically (BRU-CTR-08)
         Out-of-scope service billed separately (BRU-CTR-02: never silently absorbed)
         Contract profitability tracked continuously (revenue vs delivered cost)
         │
AUT-015  Expiry − 90/60/30/15 days ──► notify customer + account owner
         ──► renewal quotation generated at 60 days
         │
         ├── Renewed ──► new term; entitlements reset; old contract archived
         └── Lapsed ──► BRU-CTR-03: future scheduled work orders cancelled,
                        customer notified; standard billing resumes
```

### 12.6 Process 5 — Order to Cash and Month-End Close

```
Job closed ──► AUT-008 invoice generated ≤ 5 s (NFR-040), 100% of jobs (KPI-053)
               Mushak 6.3 compliant (NFR-021); BIN displayed (BRU-FIN-01)
               Privilege discount on labour only (BRU-WTY-06)
         │
AUT-022  Delivered on preferred channels with a payment link (M27)
         │
         ├── Customer pays ──► AUT-024 auto-match ≥ 90% ──► post to ledger
         ├── Cash at counter ──► M50 cash drawer ──► BRU-FIN-10 daily reconciliation
         └── Corporate ──► consolidated invoice per cycle (BRU-BIL-07)
         │
AUT-023  Unpaid at 7/14/21/30 days ──► dunning sequence ──► collections queue
         │
MONTH-END
AUT-043  Close checklist · accruals · prepayment amortisation · FX revaluation ·
         recurring journals
AUT-044  Bank statement imported ──► auto-match ──► present only exceptions
         BRU-FIN-05: period cannot close with unposted entries
         │
         VAT return prepared automatically (M51)
         Mushak 9.1 filed by the 15th via vat.gov.bd (NFR-100)
         Input credit blocked without a valid Mushak 6.3 (NFR-101)
         │
         Period locked ──► management pack served from the warehouse (M25/M62)
         TARGET: ≤ 3 DAYS (BO-06, KPI-050)
```

### 12.7 Process 6 — Technician Daily Workflow (Offline-First)

```
START OF DAY  Open P02 ──► shift clock-in with geofence (M55)
              ──► optimised job queue (route computed overnight, AUT-013)

FOR EACH JOB
  1  Review full context: customer, device, history, entitlement, knowledge (M61 offline)
  2  Navigate (turn-by-turn); automatic arrival detection
  3  Tap Arrived ──► timestamp + GPS; customer notified
  4  Photo before (GPS + timestamp; blur/dark rejected at capture)
  5  Guided diagnostic tree; fault coding
  6  Van stock: scan to consume │ not in van ⇒ request (AUT-007 network search)
  7  Estimate presented on screen ⇒ customer approves/part-approves/declines
  8  Execute repair; time tracked (start/pause/resume/stop)
  9  QC checklist — mandatory items must be answered (BRU-QMS-01)
 10  Photo after
 11  Customer e-signature
 12  Complete ──► invoice generated ──► payment collected on site if applicable
 13  Next job

INCIDENT      Any point ──► report incident/near-miss/hazard (M59) or panic alert

END OF DAY    Van stock reconciled (AUT-035) · cash reconciled to branch (BRU-FSM-07)
              Earnings and incentive view updated (M57)

CONNECTIVITY  ALL of the above works with NO connectivity for 24 hours (NFR-047).
              Every action is an idempotent command with a client UUID in an
              append-only journal. On reconnect: replay in order, server
              acknowledges each by UUID, sync completes in ≤ 30 s on 3G (NFR-037).
              Server authoritative for assignment, pricing, stock and state.
              Client wins for evidence, notes and field-captured timestamps.
              Any resolved conflict is SHOWN to the technician with what changed and why.
```

### 12.8 Process 7 — Marketplace Order to Payout

```
Customer request ──► Broadcast to qualifying sellers (BRU-FSM-12, BRU-ECM-07)
         │
Sellers submit quotations ──► counter-bid ──► customer selects
         │
Job awarded ──► seller sees customer contact ONLY for this job, expiring after
                completion (BRU-ECM-05, EA-04)
         │
Execution ──► SAME evidence, QC and warranty standards as owned jobs (BRU-ECM-03)
         │
Completion ──► customer sign-off ──► review permitted only after a completed
               transaction (BRU-ECM-02)
         │
AUT-026  Hold period elapsed ──► commission accrued (M53)
         BRU-BIL-03: payout BLOCKED entirely while a dispute is open
         │
AUT-027  Payout run ──► calculate ──► statements ──► disbursement file ──► approval
         SOD-06: the approver of the seller cannot approve their payout
         │
         Dispute raised? ──► decided by 1000FiX, not the parties (BRU-ECM-09)
                          ──► commission reversed if decided against the seller (BRU-BIL-04)
         │
CONTINUOUS  Seller score ──► below threshold: visibility reduced automatically
                          ──► below suspension threshold: suspended (BRU-ECM-04)
```

### 12.9 Process 8 — Trade-In to Resale (Circular)

```
Customer submits trade-in with photos and declared condition (P01)
         │
Indicative valuation (M14 + market price feed) ──► customer accepts in principle
         │
Collection (M03 with custody) or walk-in (M04)
         │
Inspection ──► firm offer ──► BRU-TRF-02: provenance and IMEI/stolen-device
                              screening MUST pass before payment
         │
Payment to customer ──► device becomes 1000FiX asset (M17)
         │
    ┌────────────────────────────────────────────────────────┐
    │  BRU-TRF-01 — HARD GATE                                │
    │  No device proceeds to refurbishment or resale without  │
    │  a CERTIFIED DATA DESTRUCTION RECORD (M06)              │
    └────────────────────────────────────────────────────────┘
         │
Refurbishment work order (M14 + M31 bench) ──► parts consumed (M15)
         │
QA test protocol ──► grading against published criteria (BRU-TRF-03)
         Supervisor override requires recorded justification (BRU-TRF-05)
         │
    ┌────────────────────┬───────────────────────────────────┐
    ▼                    ▼                                   ▼
Resale listing      Harvest for parts                  Route to e-waste (M18)
(M38/M12)           (M15)                              │
Battery health and                                     Triage ──► certified
known defects MUST                                     destruction ──► batch to
be disclosed                                           certified partner only
(BRU-TRF-04)                                           (BRU-ESG-02)
Refurbished warranty                                   │
terms + reserve                                        Disposal certificate
                                                       retrievable per unit
                                                       (BRU-ESG-03)
```

### 12.10 Process 9 — Payroll Cycle

```
Period end ──► AUT-045 attendance locked (BRU-HRM-05: payroll cannot finalise otherwise)
         │
Calculate: basic · allowances · overtime (pre-approved only, BRU-HRM-02) ·
           incentives (M57, threshold met first — BRU-HRM-03) ·
           income tax per NBR AY slabs · provident fund · gratuity provision
         │
Present for approval ──► BRU-HRM-06: TWO approvals — HR Manager AND CFO
                         SOD-03: preparer cannot approve
                         SOD-29: approver cannot release the bank file
         │
AUT-046  Approved ──► BEFTN file generated ──► payslips distributed ──► posted to ledger
         │
         Employee payroll visible only to the employee and HR/finance (BRU-HRM-07)
         Individual payslip is S3 — encrypted, access-logged
         │
PARALLEL RUN: two full pay cycles before legacy Excel payroll is withdrawn
TARGET: < 4 hours processing (KPI-059) · < 0.3% corrections (KPI-060) · zero errors at Gate 5
```

### 12.11 Process 10 — Access Lifecycle

```
AUT-047  employee.joined (M21) ──► identity created (M29)
         ──► role assigned FROM THE POSITION PROFILE (not ad hoc)
         ──► portal access granted · onboarding and mandatory training assigned
         ──► SoD evaluated at assignment; incompatible combinations BLOCKED (BRU-SEC-07)
         │
MODIFY   Transfer/promotion ──► old permissions revoked, new granted on the effective
         date. NO ACCUMULATION.
         │
ELEVATE  Approved access request ──► time-boxed elevation with automatic expiry
         and session recording
         │
AUT-052  QUARTERLY certification ──► review tasks to all managers
         ──► UNCONFIRMED ACCESS IS REVOKED at the deadline
         │
AUT-048  employee.left ──► ALL access revoked within ONE HOUR (BRU-SEC-06)
         ──► devices deregistered · delegated authority reassigned · clearance triggered
         │
CONTROL  Zero orphaned accounts beyond 24 hours after a leaver event (KPI-090),
         measured weekly.
```

---

## 13. USE CASES

Use cases are stated in BABOK form: actors, preconditions, trigger, main flow, alternative flows,
postconditions. The set below covers the v1.0 use cases (restated against v2.0 modules) plus the
use cases introduced by the nine new revenue streams.

### UC-001 — Log a Service Request (Multi-Channel)

**Actors:** Customer · Contact Centre Agent (R34) · Service Centre Agent (R08) · System
**Preconditions:** the party can be found or created; the system is operational
**Trigger:** the customer contacts 1000FiX on any channel

**Main flow**

1. Contact received via portal, mobile app, hotline 16743, WhatsApp, chatbot, walk-in or email
2. System resolves the party (M33) — found: pre-populates; not found: creates with **PDPA-compliant
   consent capture and transparency notice** (NFR-090…092)
3. System resolves the device (M17) by serial/IMEI; if unregistered, registers it as part of intake
   *(BRU-SRM-01 blocks otherwise)*
4. System evaluates entitlement: warranty active (M09)? covered by contract (M08)? else paid (M11)
5. System classifies the order and assigns the SLA policy; the SLA clock starts
6. Unique order number generated with a branch- and business-line-aware sequence
7. Acknowledgment sent on the customer's preferred channel with a tracking link (M27)
8. Order enters the dispatch queue

**Alternative flows**
A1 — Warranty expired: system notifies; order converts to paid; estimate path invoked
A2 — Walk-in without appointment: token issued (M04); target **intake ≤ 3 minutes**
A3 — Duplicate detected (same device, same fault, < 30 days): flagged as rework *(BRU-SRM-06)*
A4 — Customer declines consent for optional processing: order proceeds on the legitimate-ground
basis; marketing processing suppressed

**Postconditions:** order Open; customer notified; SLA running; order visible in the dispatch queue

---

### UC-002 — Assign Work to a Technician

**Actors:** Dispatch Manager (R07) · System · Technician (R10/R11/R12)
**Preconditions:** service order Open; technicians rostered
**Trigger:** the order enters the dispatch queue

**Main flow**

1. System scores candidates on skill, **certification currency (M22)**, location, workload,
   van stock (M15) and SLA risk
2. Where the top score exceeds the confidence threshold, the system auto-assigns *(BRU-FSM-03)*;
   otherwise it presents a ranked list with a **plain-language explanation of why**
3. Dispatcher accepts or overrides; **every override requires a reason code** *(BRU-FSM-04)*
4. System validates: certification current *(BRU-SRM-09 — hard block)*, not on leave or off-shift
   *(BRU-FSM-01)*, working-time limits not breached *(BRU-FSM-10)*
5. Work order created; technician and customer notified; route updated
6. Tracking link published to the customer

**Alternative flows**
A1 — No qualified technician: order queued; SLA escalation at 50/75/90/100% *(AUT-009)*
A2 — Emergency insertion: schedule re-optimised; **never displaces an SLA-critical job already at
risk** *(BRU-FSM-11)*
A3 — Marketplace dispatch: offered to qualifying sellers only *(BRU-FSM-12)*

**Postconditions:** work order Assigned; technician notified; job on the live map

---

### UC-003 — Execute a Field Job (Offline-Capable)

**Actors:** Technician (R10/R11/R12) · P02 · Customer
**Preconditions:** work order assigned; app installed and synced
**Trigger:** technician starts the day or receives an assignment

**Main flow** — as §12.7.

**Alternative flows**
A1 — **No connectivity:** every action is queued locally as an idempotent command; the job
completes fully offline; sync on reconnect within 30 seconds *(NFR-037, NFR-047)*
A2 — Part not in van: request raised; network searched; transfer or purchase initiated; job held
with a revised ETA to the customer *(AUT-007)*
A3 — Cannot fix: Parts Pending or Escalation; dispatcher notified; SLA clock suspended only under
an approved hold reason *(BRU-SRM-15)*
A4 — Customer absent or access refused: **geotagged evidence mandatory** before the failed visit
can be recorded *(BRU-FSM-09)*
A5 — QC fails: the job cannot be completed *(BRU-SRM-04)*
A6 — Sync conflict: server wins on assignment, pricing, stock and state; client wins on evidence
and field timestamps; **the conflict is shown to the technician with what changed and why**

**Postconditions:** work order Completed; inventory deducted; invoice created; KPIs updated; claim
created if warranty

---

### UC-004 — Customer Tracks Service Status

**Actors:** Customer (R36) · P01
**Trigger:** the customer opens the tracking link or the portal

**Main flow:** visual status timeline · current step and ETA · live technician map with name and
photo when en route · notifications at every milestone by push, SMS and WhatsApp · **public
tracking link works without login**

**Postconditions:** the customer is informed without calling; hotline load reduced by **> 80% of
status enquiries** (KPI-025)

---

### UC-005 — Process a Warranty Claim

**Actors:** System · Warranty Claims Officer (R28) · Brand Partner (R38 / EXT-03)
**Trigger:** a warranty work order closes

**Main flow** — as §12.3.

**Alternative flows**
A1 — Evidence incomplete: claim held with a **specific checklist** of what is missing; not
submitted
A2 — Duplicate within 90 days: **blocked** *(BRU-WTY-03)*
A3 — Brand rejects: dispute task; reason analysed; recurring reasons raise a non-conformance in
M23
A4 — Brand submission window approaching: **escalated as revenue leakage before expiry**
*(BRU-WTY-08)*

**Postconditions:** claim submitted within 72 hours; reimbursement tracked to the ledger

---

### UC-006 — Generate an Invoice and Collect Payment

**Actors:** System · Customer · Cashier (R29) / Finance Officer (R27)
**Trigger:** the work order closes

**Main flow** — as §12.6. Invoice within **5 seconds**; Mushak 6.3 compliant; Privilege discount on
labour only; payment link on the preferred channel; auto-match ≥ 90%.

**Alternative flows**
A1 — Cash at the counter: recorded to the cash drawer; **daily reconciliation blocks the next
shift if unclosed** *(BRU-FIN-10)*
A2 — Cash > BDT 50,000: **customer NID must be recorded** *(BRU-FIN-02)*
A3 — Corporate: added to the consolidated invoice for the cycle; **cannot issue until every
constituent job is Completed and priced** *(BRU-BIL-07)*
A4 — Payment gateway outage: alternative gateway; cash fallback; link resent on restoration

**Postconditions:** invoice paid; AR cleared; ledger posted; order closed; CSAT triggered

---

### UC-007 — Renew a Contract

**Actors:** System · Account Manager (R22) · Customer
**Trigger:** contract expiry − 90 days

**Main flow** — as §12.5. Notifications at 90/60/30/15 days; renewal quotation auto-generated at 60
days.

**Alternative flows**
A1 — Customer declines: contract expires; **future scheduled work orders cancelled and the
customer notified** *(BRU-CTR-03)*
A2 — No action at 15 days: escalation to the Sales Manager
A3 — Amendment rather than renewal: contract amendment recorded with effective date

**Postconditions:** contract renewed or expired; the outcome is tracked against KPI-028 (renewal
rate target 88%)

---

### UC-008 — Replenish Inventory

**Actors:** System · Inventory Manager (R17) · Procurement Officer (R19) · Vendor (R38)
**Trigger:** stock reaches the reorder point

**Main flow** — as §12.4.

**Postconditions:** stock replenished; PO closed; vendor invoice in the payment schedule after a
successful three-way match

---

### UC-009 — Onboard a Marketplace Seller ★

**Actors:** Seller (R38) · Marketplace Operations Officer (R24) · System · KYC provider
**Preconditions:** the marketplace commercial model (D-03) is decided and configured
**Trigger:** a seller applies through P07

**Main flow**

1. Seller registers as a freelance engineer or a shop; verifies phone and email by OTP
2. Submits **NID, trade licence, references and work-sample images**
3. System performs identity verification (INT-034) and business registry check (INT-035)
4. Seller signs the agreement digitally (M24 qualified e-signature)
5. Registration fee paid if applicable; registration expiry set
6. Marketplace Operations reviews and approves
7. Seller may declare categories only where they hold a **verified qualification** *(BRU-ECM-07)*;
   category qualification assessed via M22 *(BRU-LMS-02)*
8. Seller becomes active and may list

**Alternative flows**
A1 — Verification fails: application rejected with reason; no transacting *(BRU-ECM-01)*
A2 — Registration expires: **seller automatically suspended until renewed** *(BRU-ECM-08)*
A3 — Score falls below threshold post-activation: visibility automatically reduced, then suspension
*(BRU-ECM-04)*

**Postconditions:** seller active, scoped to qualified categories, with a wallet and a scorecard

---

### UC-010 — Deliver a Managed-Service Incident ★

**Actors:** Monitoring agent · Remote Support Engineer (R13) · Corporate client (R37) · System
**Preconditions:** MSP contract active; estate onboarded and monitored
**Trigger:** an alert rule breaches

**Main flow**

1. Telemetry breaches a threshold *(AUT-038)*; alerts correlated and de-duplicated to control noise
   *(FR-RMS-057)*
2. Ticket opened against the MSP contract SLA
3. Engineer triages; attempts remote resolution (RustDesk/MeshCentral) with **consent capture**
4. Resolved remotely → SLA measured, ticket closed, client notified
5. Not resolvable remotely → escalates to a service order (M01) and field dispatch (M02)
6. Monthly service report generated for the client (P04)

**Alternative flows**
A1 — Predicted failure above confidence *(AUT-039)*: proactive service proposed to the account
manager before failure
A2 — SLA breached: **service credit calculated automatically** *(BRU-CTR-08)*

**Postconditions:** incident resolved; SLA attainment measured; per-client profitability updated

---

### UC-011 — Rent Equipment ★

**Actors:** Customer · Retail Officer (R25) · Rider (R16) · System
**Trigger:** rental reservation

**Main flow**

1. Availability checked against the rental pool; reservation made
2. Rental agreement created; tariff applied; **deposit received** *(BRU-RNT-02)*
3. **Pre-dispatch condition report completed and signed** *(BRU-RNT-01 — hard gate)*
4. Delivered under custody (M03)
5. On return: inbound condition report; **damage charges derive from the outbound/inbound
   difference** *(BRU-RNT-03)*
6. Asset re-enters the pool **only after cleaning, servicing and functional test** *(BRU-RNT-04)*
7. Billing: period + usage + damages

**Alternative flows**
A1 — Overdue: charges accrue automatically with escalating notification *(BRU-RNT-05)*
A2 — Irreparable fault during rental: swap-out with logistics and agreement update *(FR-SRM-064)*

**Postconditions:** rental billed; utilisation and depreciation updated; deposit returned or
applied

---

### UC-012 — Recover Customer Data ★

**Actors:** Customer · Data Services Technician (R14) · System
**Preconditions:** the data-services facility, controls and staff undertakings are in place
(DEP-12)
**Trigger:** a data recovery request

**Main flow**

1. Data case created with **confidentiality controls applied at creation** *(FR-SRM-065)*
2. Media taken into custody with **dual control**; every custody event recorded
3. Case access restricted to the assigned team; **every access logged** *(BRU-SEC-03)*
4. Recovery attempted; cleanroom booked if required; partner lab referral if beyond capability
5. Recovered data indexed — **S3, encrypted with per-case keys, Bangladesh-resident** (NFR-086)
6. Handover to the customer with verification
7. **Recovered data purged at the agreed date unless a documented hold applies** *(BRU-SEC-04)*
8. Purge certificate issued and retrievable

**Alternative flows**
A1 — Recovery unsuccessful: case closed with evidence; fee policy applied
A2 — Customer requests destruction instead: certified destruction to the approved technique
standard; certificate issued

**Postconditions:** custody unbroken with **zero exceptions**; certificates on file; **recovered
data never used as training data** *(BRU-AIM-03)*

---

### UC-013 — Handle a PDPA Data-Subject Request ★

**Actors:** Data subject · Chief Data Officer (R40) / Data Steward (R39) · System
**Trigger:** an access, rectification, erasure or consent-withdrawal request

**Main flow**

1. Request received (portal, email, hotline) and logged with an identity check
2. System assembles the data held about the subject across all modules via the party master (M33)
3. **Access/portability:** structured export provided
4. **Rectification:** correction applied; **controllers notified within 30 days** *(NFR-093)*
5. **Erasure:** applied where the purpose has ceased, consent is withdrawn, processing was
   unlawful, or law requires — **subject to statutory retention that overrides erasure**
6. **Consent withdrawal:** simplified procedure; downstream processing suppressed
7. Response issued within the statutory timeframe; the request and outcome retained as a processing
   record for **≥ 5 years** *(NFR-095)*

**Alternative flows**
A1 — Erasure conflicts with a retention obligation (financial, employment, warranty): the conflict
is recorded, the subject informed, and the record retained until the obligation lapses
A2 — Request relates to residency-restricted fields: handled entirely within the Bangladesh-resident
store

**Postconditions:** the request is satisfied and evidenced; **no personal data leaves its lawful
residency**

---

### UC-014 to UC-030 — Summary

| UC | Title | Primary actor | Key outcome | Wave |
|---|---|---|---|:--:|
| UC-014 | Walk-in intake and handover | Service Centre Agent | Intake ≤ 3 min; device under custody; token queue managed | W1 |
| UC-015 | Workshop bench repair (L1/L2/L3) | Workshop Supervisor | WIP visible; repair-level routing; test and burn-in evidenced | W2 |
| UC-016 | Pick & drop with unbroken custody | Rider | POD 100%; zero custody breaks | W3 |
| UC-017 | Corporate bulk service request | Corporate Portal User | CSV validated against contract coverage; batch created ≤ 5 min | W4 |
| UC-018 | Consolidated corporate invoicing and dispute | Corporate Portal User + Finance | Invoice approved or disputed on the portal; < 3% dispute rate | W4 |
| UC-019 | Brand partner claim decision | Brand Partner | Decision < 10 days; evidence complete; reconciliation clean | W4 |
| UC-020 | Purchase requisition to payment | Procurement Officer | Three-way match blocks unmatched invoices | W3 |
| UC-021 | Vendor RFQ response and scorecard | Vendor | > 75% RFQ response; scorecard visible to the vendor | W3 |
| UC-022 | Technician certification expiry | System + HR | **Technician removed from that brand's dispatch pool on expiry** *(AUT-042)* | W5 |
| UC-023 | Monthly payroll run | HR Manager + CFO | Zero errors; BEFTN accepted first time; < 4 h processing | W5 |
| UC-024 | ISO internal audit on mobile | Quality Auditor | 100% of audits on mobile; finding-to-CAPA < 5 days | W5 |
| UC-025 | Complaint to CAPA closure | Customer Service Manager | Root cause recorded; **CAPA closed only after effectiveness verification** | W5 |
| UC-026 | Trade-in to resale | Retail Officer | **Zero units released without a destruction certificate** | W6 |
| UC-027 | E-waste collection to disposal certificate | Quality Manager | 92% diversion from landfill; certificate per unit | W8 |
| UC-028 | Marketplace dispute resolution | Marketplace Operations | **1000FiX decides**; commission reversed if against the seller | W7 |
| UC-029 | Executive branch performance review | CEO / Branch Manager | Drill from group revenue to a single job; **zero manual packs** | W8 |
| UC-030 | Stand up a second-country entity | CTO | Country pack configured in **≤ 12 weeks, no core code change** | W9 |

---

## 14. INTEGRATION REQUIREMENTS

### 14.1 Integration Principles

| # | Principle | Business consequence |
|---|---|---|
| IP-01 | The ERP is the system of record; integrations **synchronise, they do not duplicate authority** | Every field has one owning system, declared |
| IP-02 | All traffic passes through the API gateway | One place for auth, rate limits, versioning, observability |
| IP-03 | Every integration declares its pattern | Sync · async command · domain event · webhook · batch file |
| IP-04 | Every integration is **idempotent** | Retries and replays never double-apply |
| IP-05 | Every integration **fails safely** | Circuit breakers, timeouts, graceful degradation with user-visible messaging |
| IP-06 | Every integration is observable | Health, throughput, latency and error rate dashboards with alerting |
| IP-07 | **No credentials in code or configuration files** | Vault-stored, rotated, access-audited |
| IP-08 | Every external contract is versioned and documented | OpenAPI 3.1 for REST; JSON Schema for events |
| IP-09 | **Third-party outages must not stop the business** | Documented, tested manual fallback for every P0 integration |
| IP-10 | Data leaving the Company is **minimised and logged** | Only the fields the counterparty needs — a PDPA obligation |

### 14.2 The 47 External Integrations

| Group | Count | Integrations | Wave |
|---|---:|---|---|
| **Payments** | 9 | **bKash** (P0) · **Nagad** (P0) · **SSLCOMMERZ** (P0) · Rocket · **Bank BEFTN** (P0) · **bank statement import** (P0) · seller payout rail · international gateway · instalment/BNPL | W3, W5, W7–W9 |
| **Communications** | 9 | **Bangladesh SMS primary** (P0) + failover · **WhatsApp Business Cloud API** (P0) · **email SMTP/IMAP** (P0) · **push FCM/APNs** (P0) · **cloud telephony/IVR for hotline 16743** · WebRTC video · social messaging · in-app chat | W1–W2, W4, W6 |
| **Location, mapping & logistics** | 9 | **Google Maps Platform** (P0) · OSRM · VROOM · traffic data · **Traccar GPS** (P0) · Pathao · RedX · Steadfast/Sundarban · international freight | W2–W3, W9 |
| **Remote support & monitoring** | 6 | Remote desktop (RustDesk/MeshCentral) · monitoring agent telemetry · SNMP/ICMP collector · patch feed · endpoint protection console · cloud provider APIs (M365/Google/AWS) | W5–W6 |
| **Marketplace & trust** | 4 | **NID/identity verification** (P0) · trade licence/business registry · **IMEI/stolen-device blocklist** · ad delivery | W6–W7 |
| **Government & compliance** | 5 | **NBR e-VAT filing** (P0) · BIN/TIN validation · e-waste authority reporting · biometric attendance devices · RJSC company registry | W3–W5, W8–W9 |
| **AI, data & enterprise** | 5 | Self-hosted LLM inference · OCR (including Bengali) · Bengali speech-to-text · corporate client SSO (SAML/OIDC per client) · client ITSM (ServiceNow/Jira) | W3, W6–W8 |
| | **47** | **P0: 12 · P1: 17 · P2: 12 · P3: 6** | |

### 14.3 Mandatory Fallbacks for P0 Integrations

**Business continuity requirement:** no third-party outage may stop the business. Each fallback
must be **documented and tested**, not merely designed.

| Integration | Fallback |
|---|---|
| bKash / Nagad / SSLCOMMERZ | Alternative gateway; cash at counter; payment link resent on restoration |
| SMS gateway | Failover gateway; WhatsApp; push; queued for retry |
| WhatsApp | SMS; email; in-app inbox |
| Google Maps | Cached geocodes; OSRM-only routing; manual address entry |
| Traccar GPS | Last known position; manual status updates by the technician |
| Bank statement import | Manual statement upload |
| BEFTN | Manual bank file submission via the bank portal |
| NBR e-VAT | Manual portal filing from the generated return |
| Identity verification | Manual document review by compliance |
| Push notifications | SMS fallback for critical messages |
| LLM inference | Rule-based responses; direct human routing |
| Telephony | Divert hotline to mobile numbers with manual logging |

### 14.4 The Portal Platform Contract (Constraint CON-03)

The Next.js 15 + Payload CMS 3 platform **cannot be replaced**. This is the most important
integration in the estate and has its own contract.

**Field ownership — who is authoritative for what:**

| Data | Owned by | Direction | Sync |
|---|---|---|---|
| Customer identity and profile | **ERP** (M33/M07) | ERP → Portal | Event-driven, near real-time |
| Customer authentication | **Identity provider** (M29) | Shared | Federated |
| Marketing content, pages, blog, SEO | **Portal** (Payload CMS) | Portal only | — |
| Service catalogue and prices | **ERP** (M37, M11) | ERP → Portal | Scheduled + on change |
| Branch and coverage data | **ERP** (M30) | ERP → Portal | On change |
| Booking availability | **ERP** (M02) | Portal queries ERP | Synchronous |
| Service orders | **ERP** (M01) | Portal → ERP on create; ERP → Portal on update | Sync + events |
| Order status and tracking | **ERP** (M01, M02) | ERP → Portal | Events + polling fallback |
| Invoices and payments | **ERP** (M19, M20) | ERP → Portal | Events |
| Contracts and entitlements | **ERP** (M08) | ERP → Portal | Events |
| Loyalty points and vouchers | **ERP** (M10) | ERP → Portal | Events |
| Reviews and ratings | **ERP** (M12/M34) | Portal → ERP on submit; ERP → Portal on publish | Sync |

**Contract rules:** both sides support **at least two API versions concurrently** with six months'
deprecation notice · every POST accepts an `Idempotency-Key` and duplicate keys return the original
result · OAuth 2.0 client credentials per environment · 600 requests/minute per portal instance ·
portal timeout 5 s, ERP responds within **2 s at p95** · the portal **degrades gracefully** with a
cached catalogue and queued booking · **a nightly reconciliation job compares order and customer
counts with divergence alerting**.

### 14.5 Domain Events

Events are **facts about the past**, named `<aggregate>.<past-tense-verb>`, carrying a standard
envelope (`event_id`, `event_type`, `schema_version`, `occurred_at`, `company_id`,
`operating_unit_id`, `actor`, `correlation_id`, `causation_id`, `aggregate`, `payload`).

**Business-critical event chains:**

| Event | Producer | Business consequence |
|---|---|---|
| `service_order.completed` | M01 | Triggers warranty claim (M09), invoice (M20), CSAT survey (M34), quality signal (M23), KPI update (M25) |
| `certification.expired` | M22 | **Hard dispatch block in M02** — this is BO-15 |
| `contract.expiring` | M08 | Renewal journey (M10, M27) and account manager task |
| `stock.below_reorder` | M15 | Replenishment draft (M16) and alert |
| `employee.left` | M21 | **All access revoked within one hour (M29)** |
| `invoice.paid` | M20 | Order closure (M01), ledger posting (M19), customer notification (M27) |
| `commission.earned` | M12 | Payout accrual (M53) |
| `wipe.certified` | M06 | **Releases the device for refurbishment (M14) or recycling (M18)** |
| `sla.breached` | M01 | Contract service credit (M08), quality event (M23), billing adjustment (M20) |
| `rework.detected` | M01 | Technician manager notification (M21), quality (M23), model feedback (M26) |

**Consumer rules:** every consumer records processed `event_id`s and ignores duplicates · ordering
guaranteed **per aggregate id only, never globally** · three retries with exponential backoff, then
dead-letter with alert · **95% of events consumed within 5 seconds**.

### 14.6 Offline Synchronisation (P02, P09, P11)

| Aspect | Business requirement |
|---|---|
| Duration guarantee | **24 hours** of offline operation with **no data loss** |
| Sync target | Complete within **30 seconds** of reconnection on 3G |
| Conflict policy | **Server authoritative** for assignment, pricing, stock and state; **client wins** for evidence, notes and field-captured timestamps |
| Conflict visibility | **Any resolved conflict is shown to the user with what changed and why** |
| Integrity | Checksums on every batch; failed batches retried, **never partially applied** |
| Local security | Encrypted local store; scope limited to the user's own assigned work |

---
---

# PART D — CONDITIONS, CONSTRAINTS & CONSEQUENCES

---

## 15. ASSUMPTIONS

Every assumption carries a stated consequence if it proves false, and a named owner. Assumptions
are re-tested at each wave gate.

| ID | Assumption | If false | Owner |
|---|---|---|---|
| ASM-01 | All service centres have at least 3G connectivity during operating hours | Extended offline windows; SMS fallback; connectivity investment required | CTO |
| ASM-02 | Technicians will use Company-issued Android 11+ devices | Device procurement cost added; support matrix widened | Ops Director |
| ASM-03 | Existing customer and device data is exportable at **≥ 80% quality** | Migration effort increases materially; manual cleansing programme required *(RSK-014)* | CTO |
| ASM-04 | The 17+ brand partnerships continue through the programme | Warranty benefit case reduces; claim automation value falls | CEO |
| ASM-05 | Bangladesh VAT rates and Mushak format remain broadly stable | Configuration changes; possible rework of tax reporting | CFO |
| ASM-06 | Business stakeholders commit the stated time (§5.5) | Waves slip — **this is RSK-001, the highest-rated risk** | CEO |
| ASM-07 | The portal platform exposes and maintains documented, versioned APIs | Integration effort increases; adapter layer required | CTO |
| ASM-08 | bKash, Nagad and SSLCOMMERZ provide sandbox and production access on schedule | Payment go-live slips; cash-only fallback at counters | CFO |
| ASM-10 | No major organisational restructuring during the programme | Re-baseline required | CEO |
| ASM-11 | Odoo 19 remains supported through the programme; a later major upgrade is a separate project | Upgrade project added to the roadmap | CTO |
| ASM-12 | OCA critical-path modules complete v19 migration, or can be migrated by the delivery team | Custom development substitutes; effort increases *(RSK-015)* | Solution Architect |
| ASM-13 | *(v1.0 — superseded)* Cloud hosting in a single Singapore region remains acceptable | **Superseded by ASM-21 and NFR-086.** Regional hosting remains the assumption for non-sensitive data only | CTO |
| ASM-14 | Corporate demand for managed services exists at the assumed price point | MSP benefit case reduces; pricing revisited | Corporate Services Head |
| ASM-15 | Bengali-capable open-weight language models remain available and adequate | Commercial LLM API considered, with data-residency implications | CTO |
| ASM-16 | Go-live does not fall in Ramadan, Eid-ul-Fitr or Eid-ul-Adha peak periods | Wave dates adjusted | Programme Manager |
| ASM-17 | Third-party API costs remain within the projected envelope ($1,890–5,230/month at scale) | Budget variance; usage optimisation required | CFO |
| ASM-18 | Historical financial data for at least three years is available in structured form | Reduced comparative reporting at go-live | CFO |
| ASM-19 | Technicians can read Bengali interfaces | Icon-led and voice-led interface variants required | Ops Director |
| ASM-20 | Biometric attendance hardware is procured before Wave 5 | GPS-based clock-in used as the sole mechanism | HR Director |
| **ASM-21** | **A Bangladesh-resident data store of adequate reliability and performance is procurable** | **The architecture must be re-planned; on-premises may be necessary. Not yet proven — see D-13** | **CTO** |
| **ASM-22** | **PDPA enforcement timing holds at approximately 13 May 2027** | An earlier activation compresses the compliance window inside Wave 4 | CFO / Legal |
| ASM-23 | Marketplace seller supply exists in the target categories and areas | Marketplace benefit case reduces; owned capacity remains the constraint | CCO |
| ASM-24 | Power backup (UPS/generator) exists at primary service centres | Branch downtime during outages; offline-first mitigates at the counter | IT Administrator |

---

## 16. CONSTRAINTS

| ID | Constraint | Type | Business consequence |
|---|---|---|---|
| **CON-01** | Three-year budget envelope of **$690K–1,150K** (restated) | Budget | W8 and W9 are the first deferral candidates; **W6 and W7 are the revenue-generating waves and must be protected** |
| **CON-02** | v1.0 committed scope must be delivered by **Month 18** | Schedule | **Waves 1–4 cannot be reordered** |
| **CON-03** | The Next.js 15 + Payload CMS portal platform **cannot be replaced** | Technical | The ERP integrates; API contract discipline is mandatory |
| **CON-04** | All financial transactions must comply with NBR requirements | Regulatory | **Compliance is a P0 gate, not a feature** |
| **CON-05** | Bengali must be primary for field and customer surfaces | Technical | **Translation is a definition-of-done item, not a follow-up** |
| **CON-06** | bKash and Nagad must be primary payment methods | Technical | Bangladesh-specific gateway integration is mandatory |
| **CON-07** | Field applications must operate offline | Technical | **Offline-first architecture is non-negotiable** |
| **CON-08** | No go-live during Ramadan or the Eid periods | Operational | Wave dates account for the Islamic calendar |
| **CON-09** | **Sensitive personal data must be Bangladesh-resident**; other data in an approved region | Regulatory / technical | Split-residency architecture — **supersedes the v1.0 single-region constraint** |
| **CON-10** | Automation must augment roles, not displace staff without approval | Organisational | Change messaging and redeployment planning required |
| **CON-11** | ISO 9001:2015 certification must be maintained throughout | Regulatory | Process changes require QMS documentation updates **in step** |
| **CON-12** | Business super-user time is finite | Resource | **UAT capacity, not developer capacity, paces the programme** |
| **CON-13** | 1000FiX owns all source code, configuration, migrations, tests and documentation | Contractual | Delivered continuously to a Company-controlled repository, not at milestones |
| **CON-14** | Zero core licence cost | Commercial | L6 commercial components require CFO approval and a documented open-source alternative assessment |

---

## 17. DEPENDENCIES

### 17.1 Internal Dependencies

| ID | Dependency | Needed by | Owner | Impact if late |
|---|---|---|---|---|
| DEP-01 | Chart of accounts restructured for the dimensional model | W3 start | CFO | Finance configuration blocked |
| DEP-02 | Payroll structures, tax parameters and PF rules confirmed | W5 start | HR Director | Payroll configuration blocked |
| DEP-03 | Service catalogue and rate cards finalised and approved | W3 start | CCO | Pricing engine cannot be configured |
| DEP-04 | Contract product definitions for all **14 families** | W4 start | CCO | Contract engine cannot be configured |
| DEP-05 | Legacy data extracted, profiled and cleansed | Per wave | Department heads | Migration slips; go-live slips |
| DEP-06 | **Super-users named, trained and time-protected** | Each wave | Department heads | **UAT fails — RSK-001** |
| DEP-07 | Branch connectivity and hardware readiness | Per rollout site | IT Administrator | Site rollout blocked |
| DEP-08 | Technician devices procured and enrolled | W2 | Ops Director | Field rollout blocked |
| DEP-09 | **Marketplace commercial model decided** (commission, liability, settlement) | W7 − 3 months | CEO + CFO | **Marketplace build blocked — RSK-022** |
| DEP-10 | Rental and refurbishment legal-entity decision | W6 − 3 months | CFO | Finance structure blocked |
| DEP-11 | Telephony vendor selected | W4 − 2 months | CTO | Contact centre build blocked |
| DEP-12 | Data-services facility, controls and staff undertakings in place | W6 | Technical Services Head | Data services cannot launch |
| DEP-13 | Multi-country target markets decided | W9 − 3 months | CEO | Country pack cannot be specified |
| DEP-14 | Quality management system documentation current | W5 | Quality Manager | QMS configuration blocked |
| DEP-15 | Biometric attendance hardware installed | W5 | IT Administrator | GPS-only fallback |

### 17.2 Regulatory Dependencies

| ID | Dependency | Owner | Needed by | Impact if late |
|---|---|---|---|---|
| **DEP-31** | **Legal opinion on the split-residency data architecture** — confirming which fields must be Bangladesh-resident under the PDPA 2026 and what safeguards permit cross-border processing of the remainder | CTO + Legal | **Before the Wave 1 architecture is fixed** | **The whole data architecture rests on an unverified assumption. Retrofitting residency into a live system is the most expensive class of rework** |
| **DEP-32** | **Significant data fiduciary classification assessment** — whether 1000FiX must appoint a Chief Data Officer | CEO + Legal | W4 − 3 months | Statutory non-appointment; penalty exposure |
| **DEP-33** | **Registration or notification with the National Data Management Authority**, if required at this scale | Legal | W4 − 3 months | Operating without required registration |
| **DEP-34** | **PDPA-compliant transparency notice text**, in Bengali and English, for every capture point | Legal + CCO | W1 build | **Consent captured without a valid notice is not valid consent** |
| **DEP-35** | **Media sanitisation programme document** naming the approved technique standard | Quality Manager | W6 − 2 months | M06 destruction certificates cite no approved standard and are not defensible |

### 17.3 External Dependencies

| ID | Dependency | External party | Needed by | Impact if late |
|---|---|---|---|---|
| DEP-16 | bKash API access (sandbox then production) | bKash | W3 | Mobile money unavailable |
| DEP-17 | Nagad API access | Nagad | W3 | Reduced payment options |
| DEP-18 | SSLCOMMERZ integration | SSLCOMMERZ | W3 | Card payments unavailable |
| DEP-19 | WhatsApp Business API approval | Meta / BSP | W1 | WhatsApp channel unavailable |
| DEP-20 | SMS gateway contracts (primary and failover) | SMS providers | W1 | Notifications limited to push and email |
| DEP-21 | Google Maps Platform commercial terms | Google | W2 | Mapping and geocoding limited to OSM |
| DEP-22 | **Brand partner claim format specifications** | 17+ brands | W4 | Claim automation limited to manual formats |
| DEP-23 | BEFTN file format confirmation | Banking partner | W5 | Manual salary disbursement |
| DEP-24 | NBR e-VAT submission specification | NBR | W4 | Manual VAT filing |
| DEP-25 | Courier partner API access | Pathao / RedX / others | W3 | Internal riders only |
| DEP-26 | Telephony carrier interconnect for 16743 | Telecom operator | W4 | Hotline remains outside the system |
| DEP-27 | Identity verification service agreement | KYC provider | W7 | Manual seller verification |
| DEP-28 | Certified e-waste recycling partners | Recycling partners | W8 | E-waste programme cannot launch |
| DEP-29 | **External tax and legal opinion on the marketplace model** | Advisors | W7 − 3 months | **Marketplace blocked — RSK-022** |
| DEP-30 | Accredited e-signature provider agreement | Trust service provider | W3 | Operational signatures only; contracts remain wet-signed |
| DEP-36 | Implementation partner contract executed | Selected partner | Before kickoff | All timelines shift |

---

## 18. RISK REGISTER

Scoring: Probability (L/M/H) × Impact (Low/Med/High/Critical) → Rating.

### 18.1 Critical Risks — The Ones That Can End the Programme

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| **RSK-001** | **Business super-user availability falls short, stalling UAT** | **H** | High | **Critical** | Named super-users with time formally protected in their objectives; UAT dates in the annual plan; escalation to CEO on non-availability | **Wave gate slips; development does not run ahead into unaccepted work** | CEO |
| **RSK-002** | **Scope creep across a 36-month programme** | **H** | High | **Critical** | Formal change control; wave-locked scope; a parking lot for good ideas | Defer to a later wave; **never mid-wave insertion** | Steering Committee |
| **RSK-008** | **Technician rejection of the mobile app** | **H** | **Critical** | **Critical** | Bengali-first design; extreme simplicity; field pilot with respected senior technicians before rollout; Company-provided devices; **earnings and incentive visibility as an immediate personal benefit**; champion network | Simplified "lite" mode; extended on-site support; phased feature introduction | Ops Director |
| **RSK-022** | **Marketplace VAT and liability model incorrect** | M | **Critical** | **Critical** | External tax and legal advice **before** Wave 7 build; principal-vs-agent decision documented and approved; revenue treatment configurable | Suspend marketplace transactions until corrected; restate if required | CFO |
| **RSK-023** | **Marketplace quality failure damages the 1000FiX brand** | M | **Critical** | **Critical** | **Same QC and evidence standards as owned work**; performance scoring with automatic consequences; 1000FiX escalation path; seller insurance requirement | Suspend the seller; complete the job with own technicians; compensate the customer | CCO |
| **RSK-032** | **Non-compliance with the Personal Data Protection Act 2026.** Enforcement activates ~13 May 2027 — **inside Wave 4**. Penalties to BDT 25 lakh, or BDT 50 lakh for significant data fiduciaries | **H** | **Critical** | **Critical** | Full PDPA obligation set in §11.4; consent and transparency notice built into M33 and every capture point from Wave 1; breach notification designed into M60; CDO appointment assessed before Wave 4 | Suspend affected processing; retrospective consent campaign; regulator engagement | CFO / CTO |
| **RSK-033** | **Data residency architecture unlawful.** Single-region hosting conflicts with the PDPA restriction on cross-border transfer of Sensitive PII — NID, passport, TIN and biometric identifiers, all of which this ERP holds | **M** | **Critical** | **Critical** | Split-residency architecture (NFR-086); residency classification on every field enforced at write time; **legal opinion required before Wave 1 architecture is fixed (DEP-31, D-13)** | Re-host the sensitive-data store in Bangladesh; accept latency cost | CTO / Legal |
| **RSK-036** | **Cost estimate materially understated.** The business case was modelled on 834 PW across 30 modules; the specified architecture measures **1,513 PW across 67** | **H** | High | **Critical** | TCO restated in §19; re-baselined at each wave start; **not presented as final without the counted figure** | Descope Categories D, F, I or J; defer Waves 8–9 | CFO |

### 18.2 High Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| RSK-003 | Programme fatigue over 36 months | M | High | High | Visible wave-by-wave value; celebrate gates; rotate assignments | Re-baseline with a shorter horizon and fewer waves | Programme Manager |
| RSK-004 | Key personnel loss (internal or partner) | M | High | High | **Two-person knowledge coverage on every module**; documentation as definition-of-done; knowledge transfer sessions | Contracted backfill; extend the affected wave | CTO |
| RSK-005 | Estimate inaccuracy on the new business lines (no precedent) | M | High | High | Discovery spike before each new-line wave; re-estimate at wave start; **20% contingency on W5–W8** | Descope P2/P3 within the wave | Programme Manager |
| RSK-006 | Partner delivery failure | L | Critical | High | Milestone-based payment; penalty clauses; source-code escrow; capability assessment before award | Backup partner shortlist; bring critical work in house | CTO |
| RSK-007 | Budget pressure mid-programme | M | High | High | Waves are independently valuable; each has a defined stop point | **Stop after W4 (v1.0 complete) or W7 (revenue lines live); W8–W9 are deferrable** | CFO |
| RSK-009 | Branch staff resistance at counter operations | M | High | High | **Speed as the explicit design goal** with measured intake time; involve resistors in design and UAT; visible executive sponsorship | Additional training cycles; temporary dual running | Ops Director |
| RSK-010 | Marketplace sellers fail to adopt | M | High | High | Simple onboarding; **fast, transparent payouts**; clear scoring; seller advisory group | Reduce commission for early adopters; direct recruitment | CCO |
| RSK-012 | Management reverts to spreadsheets | M | High | High | **Retire the source data for manual packs**; make dashboards materially better; require decisions to cite the dashboard | Executive mandate; remove spreadsheet access to source data | CEO |
| RSK-013 | Field connectivity worse than assumed, breaking sync | **H** | Med | High | Offline-first with a 24-hour guarantee; aggressive payload compression; deferred non-critical upload; **field testing in the weakest coverage areas** | Extend the offline window to 72 hours; SMS-based critical status fallback | CTO |
| RSK-014 | Data migration quality below usable threshold | M | High | High | Profiling before every load; cleansing in the source; trial migrations; **reconciliation sign-off**; archive area for uncleansable records | Manual validation of the highest-value records; phased migration | CTO |
| RSK-015 | **OCA v19 migration gaps on critical modules** — `field-service` ~25 of 33 migrated, `helpdesk` ~20 of 28 | M | High | High | Verify migration status before each wave; fork, migrate and **contribute upstream** | Build the specific capability as a custom module | Solution Architect |
| RSK-016 | Portal platform API contract instability | M | High | High | Agreed, versioned contract; **contract tests in both CI pipelines**; joint change process | Version pinning with a temporary adapter layer | CTO |
| RSK-017 | Performance inadequate at 51+ branches under real load | L | Critical | High | **Load testing at 1.5× projected peak before every gate**; read replicas; partitioning; caching | Phased regional rollout; vertical scaling | CTO |
| RSK-018 | Offline sync conflicts corrupt data | L | Critical | High | Append-only journal; server-authoritative resolution; idempotent commands; **extensive scripted conflict testing** | Manual reconciliation tooling; conflict quarantine | Solution Architect |
| RSK-019 | Integration dependency on a third party that changes or fails | M | High | High | **Documented, tested fallback for every P0 integration**; circuit breakers; multi-provider where possible | Manual process per the fallback register | CTO |
| RSK-021 | Technical debt accumulates under wave pressure | M | High | High | Architecture standards enforced in CI; **refactoring capacity reserved each wave**; architecture review at every gate | Dedicated remediation sprint between waves | Solution Architect |
| RSK-025 | Brand partner claim rejection rate does not improve | M | High | High | **Evidence completeness enforced before submission**; per-brand rule engine; quarterly brand reviews | Manual claim preparation for the affected brand; renegotiate terms | Finance Director |
| RSK-026 | Bangladesh VAT, tax or labour regulation changes mid-programme | M | High | High | **Configuration-driven, versioned rule packs**; monitoring of NBR announcements; country-pack isolation | Manual override during transition; expedited configuration change | CFO |
| RSK-031 | Competitor moves faster on digital capability | M | High | High | Wave-by-wave delivery of visible customer-facing capability; **do not wait for programme completion to compete** | Reprioritise customer-facing waves | CEO |
| RSK-034 | Chief Data Officer not appointed where required | M | High | High | Classification assessment commissioned before Wave 4; role, authority and reporting line defined in M60 | Interim appointment from Legal or Compliance | CEO |
| RSK-035 | Regulatory citations drift out of date | M | High | High | **Every statutory and standards citation carries a verified-on date; re-verified at each wave gate (DoD-17)** | Emergency review and correction | CTO |

### 18.3 Medium Risks

| ID | Risk | Prob | Impact | Rating | Mitigation | Owner |
|---|---|:-:|:-:|:-:|---|---|
| RSK-011 | Corporate clients do not use the B2B portal | M | Med | Med | Account-manager-led onboarding; demonstrable time saving; incentivise portal use | CCO |
| RSK-020 | AI models underperform or produce unsafe outputs | M | Med | Med | **Human-in-the-loop on material decisions**; hard guard rails; graceful degradation to rules; model cards and drift monitoring | CTO |
| RSK-024 | Data-services breach exposing customer data | L | **Critical** | High | Least privilege; **dual control**; field-level encryption; time-boxed retention; full access audit; staff undertakings | CTO |
| RSK-027 | Rental asset losses exceed provision | M | Med | Med | Identity verification; deposits; condition reports; insurance; utilisation and loss monitoring | Corporate Services Head |
| RSK-028 | Refurbished units create warranty liability beyond provision | M | Med | Med | Rigorous grading; QA protocol; disclosed condition; warranty reserve | Retail Operations Head |
| RSK-029 | E-waste handling non-compliance | L | High | Med | **Certified partners only, with certification currency checked**; disposal certificates mandatory | Quality Manager |
| RSK-030 | Payment gateway outage during peak | M | Med | Med | Multiple gateways; graceful degradation; cash and bank fallback | CFO |

### 18.4 Risk Heat Summary

| Rating | Count | Governance requirement |
|---|---:|---|
| **Critical** | **8** | **Steering Committee review at every meeting; named owner reports monthly** |
| High | 21 | PMO tracking; owner reports at each wave gate |
| Medium | 7 | Register review quarterly |

> **Eight Critical risks, of which three are new since v1.0 and all three concern data protection
> or cost.** RSK-032, RSK-033 and RSK-036 did not appear in BRD v1.0 because the governing statute
> was mis-identified and the effort was under-measured. Both errors have been corrected here.

---

## 19. COST-BENEFIT ANALYSIS AND ROI

### 19.1 Investment — Three-Year Total Cost of Ownership

| Category | Year 1 | Year 2 | Year 3 | 3-Year total |
|---|---:|---:|---:|---:|
| Software licensing (L6 only; ERP core is $0) | $0–12K | $0–12K | $0–12K | **$0–36K** |
| Implementation & custom development | $245K–380K | $172K–290K | $108K–185K | **$525K–855K** |
| Infrastructure & hosting | $12K–20K | $18K–32K | $22K–44K | **$52K–96K** |
| Third-party APIs | $9K–20K | $14K–33K | $18K–42K | **$41K–95K** |
| Training & change management | $16K–29K | $11K–22K | $8K–14K | **$35K–65K** |
| Support & maintenance | — | $25K–55K | $35K–75K | **$60K–130K** |
| **Component sum** | $282K–461K | $240K–444K | $191K–372K | $713K–1,277K |
| **HEADLINE 3-YEAR TCO** | | | | **$690K–1,150K** |

> **Why the headline differs from the component sum.** The headline range is the restated figure
> from the source register (`02-02` §3.2), derived by applying measured effort to the approved unit
> rates. The component sum is wider at both ends because **the lower bound assumes every line lands
> at its best case simultaneously, and the upper bound assumes every line lands at its worst case
> simultaneously — neither is likely.** The source financial model states the same caveat. **Use
> the headline range for approval and the component table for line-by-line budgeting**, and expect
> the outturn to fall inside the headline range. Both figures are re-baselined at each wave start
> under RG-05.

#### 19.1.1 Why the figure moved — disclosed in full

| | Approved plan (30 modules) | **Measured (65 of 67 specifications)** | Change |
|---|---:|---:|---:|
| Requirements | 1,180 | **2,930** | **+148%** |
| Build effort | 834 PW | **1,513 PW** | **+81%** |
| Implementation & custom development | $290K–470K | **$525K–855K** | **+81%** |
| 3-year TCO | $455K–780K | **$690K–1,150K** | **+52%** |

**The estimating model failed in a specific, explicable way.** Requirement count was
under-estimated wherever a category carries **statutory, contractual or master-data obligations** —
Category F +73%, H +52%, I +44%, C +39%, G +29% — and was estimated accurately where the category
is purely operational — D 0%, J +12%. **Effort tracked far closer than count (+15% aggregate)**,
because statutory requirements are numerous but individually small: most resolve to configuration
in a versioned rule pack rather than new code.

> **Decision D-14 is open.** The Steering Committee has not yet decided whether to fund the
> restated figure, phase it across more waves, or cut scope. **Cutting scope is legitimate — but it
> must be a decision taken with the measured figure in front of the Committee, not absorbed
> silently across waves.** Commercial responses are structured so that Waves 8 and 9, and
> Categories D, F, I and J, can be removed cleanly.

### 19.2 Quantified Annual Benefit at Steady State (Year 3+)

| # | Benefit | Conservative | Base | Optimistic | Module | First realised |
|---|---|---:|---:|---:|---|:--:|
| 1 | Warranty revenue recovery | 60 | **100** | 140 | M09 | W4 |
| 2 | Technician productivity | 85 | **130** | 175 | M02, M26 | W2 |
| 3 | Inventory cost reduction | 20 | **34** | 50 | M15, M26 | W3 |
| 4 | Administrative labour savings | 38 | **62** | 88 | All | W3 |
| 5 | Customer retention | 46 | **78** | 112 | M07, M10, M27 | W4 |
| 6 | AMC/RAMC renewal uplift | 42 | **72** | 100 | M08 | W5 |
| 7 | Financial close & cash flow | 15 | **26** | 38 | M19, M20 | W3 |
| | *Subtotal — existing revenue streams* | *306* | ***502*** | *703* | | |
| 8 | **Managed services (MSP)** | 55 | **95** | 145 | M05 | W6 |
| 9 | **Rental gross margin** | 28 | **48** | 72 | M13 | W7 |
| 10 | **Refurbishment & resale margin** | 38 | **65** | 96 | M14 | W7 |
| 11 | **Marketplace commission & advertising** | 48 | **84** | 130 | M12 | W8 |
| 12 | **Data services** | 17 | **30** | 46 | M06 | W7 |
| 13 | **E-waste material recovery** | 7 | **12** | 19 | M18 | W9 |
| 14 | **Dynamic pricing margin uplift** | 22 | **40** | 62 | M11, M26 | W8 |
| | *Subtotal — new revenue streams* | *215* | ***374*** | *570* | | |
| | **Total (BDT lac per year)** | **521** | **876** | **1,273** | | |
| | **Total (USD @ 110)** | **~$474K** | **~$797K** | **~$1.16M** | | |

**BDT 374 lac — 43% of the total annual benefit — comes from revenue streams that cannot operate
at all under the v1.0 scope.** This is the strategic case for the expansion, stated in money.

### 19.3 Benefit Realisation Curve

| Period | Cumulative benefit (base, BDT lac) | Notes |
|---|---:|---|
| Year 1 (M1–M12) | 45 | Pilot productivity and early automation only |
| Year 2 (M13–M24) | 310 | v1.0 scope fully live; warranty and contract benefits landing |
| Year 3 (M25–M36) | 645 | New business lines ramping |
| Year 4 (steady state) | **876** | Full run rate |
| Year 5 | 920 | Compounding on customer base growth |

**Benefit realisation is deliberately lagged.** New business lines contribute nothing until they go
live, so the first two years of the v2.0 case closely track the v1.0 case. **The step change occurs
in Year 3** — which is precisely why the programme's later waves must be protected from budget
pressure ahead of Waves 8 and 9.

### 19.4 Return

| Scenario | 3-year benefit | 3-year cost | Net | ROI | Payback |
|---|---:|---:|---:|---:|---|
| Conservative | $1.24M | $1.15M | $90K | 8% | 32 months |
| **Base case** | **$1.96M** | **$0.92M** | **$1.04M** | **113%** | **22 months** |
| Optimistic | $2.61M | $0.69M | $1.92M | 278% | 15 months |

**Base-case payback: approximately 22 months from programme start.**

> **Honest statement of the conservative case.** At the conservative benefit and the upper cost
> bound, this programme returns 8% over three years — it approximately breaks even. That case
> arises if the new business lines under-deliver *and* the cost lands at the top of the range. The
> mitigation is not optimism: it is that **Waves 6 and 7 are the revenue-generating waves and are
> the last things that should be cut**, and that each wave has a defined stop point where the
> programme has already delivered standalone value.

### 19.5 The Cost of Not Proceeding

| If deferred | Consequence |
|---|---|
| Current-state waste continues | **BDT 2.55–4.0 crore per year** (§6.4) |
| Managed services without a system | MSP contracts sold but delivered manually; SLA credits leak; the segment stays sub-scale |
| Rental without a system | No utilisation tracking, no damage recovery, no depreciation discipline — asset write-offs |
| Marketplace without a system | Cannot onboard external capacity; **growth capped at owned technician headcount** |
| Refurbishment & trade-in without a system | No device provenance, no grading consistency, warranty exposure on resold units |
| PDPA obligations unmet by May 2027 | Penalty exposure to **BDT 50 lakh** plus turnover-linked fines; enforcement lands inside Wave 4 regardless of programme status |
| Multi-country deferred to a v3.0 rebuild | Retrofitting multi-entity into a live single-entity ERP typically costs **3–5×** the cost of designing for it |
| A second ERP for the new lines | **Guaranteed reconstruction of today's fragmentation** |

### 19.6 Benefit Tracking Discipline

| Practice | Requirement |
|---|---|
| **Baseline capture** | Every KPI's baseline is measured and **signed off before the relevant wave begins**. **A KPI without a baseline cannot claim a benefit.** |
| Monthly reporting | The PMO publishes a KPI dashboard monthly; benefit owners comment on variance |
| Quarterly review | The Steering Committee reviews benefit realisation against plan and agrees corrective action |
| Attribution discipline | Benefits are attributed to the ERP **only where a causal mechanism is documented**; general market growth is excluded |
| Post-implementation review | **Full independent benefits audit at Month 42**, six months after programme closure |
| Honest reporting | **Missed benefits are reported as missed, with the reason. A benefit case that is never revisited is not a business case.** |

---
---

# PART E — HOW SUCCESS IS JUDGED

---

## 20. ACCEPTANCE CRITERIA AND KPIs

### 20.1 Module Definition of Done

**No module is accepted at a wave gate until every one of these seventeen items is true.** This
list is contractually binding on the implementation partner.

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
| DoD-09 | KPIs instrumented with allocated identifiers and visible in M25 |
| DoD-10 | Data migration mapping defined and dry-run executed where legacy data exists |
| DoD-11 | Operational runbook written |
| DoD-12 | Training material produced in **Bengali and English** for every affected role |
| DoD-13 | **UAT executed and signed by named business super-users** |
| DoD-14 | Performance tested against applicable NFRs |
| DoD-15 | Security review completed with **zero open high or critical findings** |
| DoD-16 | Rollback plan documented and rehearsed |
| DoD-17 | **Regulatory citations verified current, with a verified-on date** |

### 20.2 Wave Gate Acceptance Criteria

Each gate is a formal Go/No-Go with the Steering Committee. **All criteria must be met**; partial
passes are recorded as conditional with a dated remediation plan. **Milestone payments are tied to
gate passage.**

#### Gate 1 — Foundation (Month 4)

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
| G1-10 | Performance targets met for delivered screens | Load test at 1.5× peak |
| G1-11 | UAT signed off by named super-users | Signed UAT record |
| G1-12 | Runbooks and training materials delivered | Document register |
| G1-13 | **PDPA consent, transparency notice and residency classification operating** | Compliance review |

#### Gate 2 — Field Operations (Month 8)

| # | Criterion |
|---|---|
| G2-01 | Technician app in daily use by **100%** of Dhaka technicians |
| G2-02 | **24-hour offline operation demonstrated with zero data loss** |
| G2-03 | Sync completing within 30 seconds on 3G after 24 hours offline |
| G2-04 | Route optimisation reducing measured travel time by **≥ 15%** |
| G2-05 | GPS tracking and the customer tracking page live |
| G2-06 | Inventory accuracy **≥ 95%** at migrated locations, verified by count |
| G2-07 | Van stock reconciling daily with variance < 2% |
| G2-08 | Online booking rate **≥ 60%** at pilot sites |
| G2-09 | **Paper service forms withdrawn in Dhaka** |
| G2-10 | Privilege benefits applying automatically and correctly |

#### Gate 3 — Money & Movement (Month 13)

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

#### Gate 4 — Agreements & Contact (Month 18) — **v1.0 scope complete**

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

#### Gate 5 — People, Quality & MSP (Month 22)

| # | Criterion |
|---|---|
| G5-01 | **First payroll run processed, validated and paid with zero errors** |
| G5-02 | BEFTN file accepted by the bank without rework |
| G5-03 | **Zero uncertified technicians assignable to brand warranty work** |
| G5-04 | ISO 9001 internal audit executed entirely in the system |
| G5-05 | First MSP clients live with monitored estates and SLA reporting |
| G5-06 | **All 51+ service centres operating on the platform** |
| G5-07 | Attendance capture ≥ 98% complete across all branches |

#### Gate 6 — New Asset Businesses (Month 26)

| # | Criterion |
|---|---|
| G6-01 | Rental transacting with full condition, deposit and damage control |
| G6-02 | **Zero refurbished units released without a data destruction certificate** |
| G6-03 | Data-services chain of custody with **zero exceptions** |
| G6-04 | Automatic dispatch assignment ≥ 50% with ≥ 88% dispatcher agreement |
| G6-05 | Parts demand forecast accuracy within target |
| G6-06 | Customer native mobile apps published and adopted |

#### Gate 7 — Marketplace (Month 30)

| # | Criterion |
|---|---|
| G7-01 | 200+ approved sellers transacting |
| G7-02 | **Payout accuracy 100% with zero unexplained variance** |
| G7-03 | Marketplace jobs meeting the same quality and evidence standards as owned jobs |
| G7-04 | Dispute rate below target with all disputes resolved within SLA |
| G7-05 | **VAT treatment validated by external tax advice** |
| G7-06 | Dynamic pricing operating within guard rails with a complete decision audit |

#### Gate 8 — Intelligence & Sustainability (Month 34)

| # | Criterion |
|---|---|
| G8-01 | All management reporting served from the warehouse; **zero manual packs** |
| G8-02 | Predictive maintenance precision ≥ 70% on the pilot estate |
| G8-03 | **Overall automation of routine operational work ≥ 85%** |
| G8-04 | E-waste chain fully certified with zero uncertified disposals |
| G8-05 | Every production model has a current model card and drift monitoring |

#### Gate 9 — Expansion Readiness (Month 36)

| # | Criterion |
|---|---|
| G9-01 | **A test entity in a second country stood up in ≤ 12 weeks using configuration only** |
| G9-02 | Consolidated multi-entity reporting validated |
| G9-03 | Full-scale load test passed at 1.5× projected peak |
| G9-04 | All programme documentation handed over and accepted |
| G9-05 | Support model transitioned to steady state |

### 20.3 KPI Register — 95 Programme KPIs

#### Service delivery

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-001 Service order automation rate | 20% | 65% | **85%** | M01 |
| KPI-002 Average TAT — IT equipment | unmeasured | < 36 h | **< 24 h** | M01 |
| KPI-003 Average TAT — appliance on-site | unmeasured | < 6 h | **< 4 h** | M01 |
| KPI-004 First-time fix rate | 70% | 82% | **88%** | M01 |
| KPI-005 Rework rate | unmeasured | < 5% | **< 3%** | M01, M23 |
| KPI-006 SLA compliance | unmeasured | 92% | **96%** | M01 |
| KPI-007 QC first-pass rate | unmeasured | 92% | **95%** | M01 |
| KPI-008 Estimate approval conversion | unmeasured | 72% | **78%** | M36 |
| KPI-009 Devices uncollected > 30 days | unmeasured | < 1% | **< 0.5%** | M01 |
| KPI-010 Walk-in intake time | ~10 min | < 4 min | **< 3 min** | M04 |

#### Field operations

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-011 Jobs per technician per day | 4–5 | 7 | **8–9** | M02 |
| KPI-012 Technician utilisation | 55% | 74% | **82%** | M02 |
| KPI-013 Automatic assignment rate | 0% | 20% | **70%** | M02, M26 |
| KPI-014 Travel time as % of working day | ~35% | 26% | **22%** | M02 |
| KPI-015 On-time arrival within window | unmeasured | 88% | **92%** | M02 |
| KPI-016 Technician app daily active usage | 0% | 92% | **95%** | M02 |
| KPI-017 Offline sync failures | n/a | 0 | **0** | M02 |
| KPI-018 Logistics on-time collection/delivery | unmeasured | 90% | **93%** | M03 |
| KPI-019 Chain-of-custody exceptions | untracked | 0 | **0** | M03 |

#### Customer

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-020 CSAT | 3.8/5 | 4.4/5 | **4.7/5** | M34 |
| KPI-021 NPS | unmeasured | 42 | **55** | M34 |
| KPI-022 Online booking rate | 40% | 72% | **88%** | P01 |
| KPI-023 Customer churn | ~15% | 11% | **< 8%** | M07, M26 |
| KPI-024 Complaint resolution within SLA | unmeasured | 90% | **95%** | M23, M34 |
| KPI-025 Status enquiries deflected to self-service | 0% | 60% | **80%** | M27 |
| KPI-026 AI first-contact resolution | 0% | 40% | **55%** | M32 |
| KPI-027 First-contact resolution (all channels) | unmeasured | 70% | **78%** | M27 |

#### Commercial

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-028 AMC/RAMC renewal rate | 60% | 80% | **88%** | M08 |
| KPI-029 Contract base growth | baseline | 1.6× | **2.5×** | M08 |
| KPI-030 Contract SLA attainment | unmeasured | 95% | **97%** | M08 |
| KPI-031 Contracts with negative margin | unknown | < 6% | **< 3%** | M08 |
| KPI-032 Quotation-to-order conversion | unmeasured | 72% | **78%** | M36 |
| KPI-033 Gross margin on paid repair | baseline | +2 pts | **+4 pts** | M11 |
| KPI-034 Privilege membership base | baseline | 2× | **3×** | M10 |
| KPI-035 Referral-attributed new customers | 0% | 6% | **12%** | M10 |
| KPI-036 Warranty product attach rate | unmeasured | 12% | **18%** | M09 |

#### Warranty & claims

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-037 Claims submitted within 72 hours | ~50% at 30–90 d | 92% | **95%** | M09 |
| KPI-038 Warranty revenue leakage | 15–20% | 5% | **< 2%** | M09 |
| KPI-039 First-submission approval rate | unmeasured | 90% | **92%** | M09 |
| KPI-040 Days from service to reimbursement | 60–120 | 55 | **< 45** | M09 |
| KPI-041 Claims with complete evidence at submission | unmeasured | 96% | **98%** | M09 |

#### Supply chain

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-042 Inventory accuracy | 75% | 96% | **98%** | M15 |
| KPI-043 Part availability at first request | unmeasured | 88% | **93%** | M15 |
| KPI-044 Stockout-caused job delays | unmeasured | < 6% | **< 3%** | M15 |
| KPI-045 Inventory turns per year | unmeasured | 4.5 | **6+** | M15 |
| KPI-046 Dead stock as % of value | unmeasured | < 8% | **< 5%** | M15 |
| KPI-047 Van stock variance | untracked | < 2% | **< 1%** | M15 |
| KPI-048 Vendor on-time delivery | unmeasured | 88% | **92%** | M42 |
| KPI-049 Three-way match exception rate | n/a | < 8% | **< 5%** | M16 |

#### Financial

| KPI | Baseline | W4 | W8 | Source |
|---|---|---|---|---|
| KPI-050 Month-end close cycle | 15–20 days | 5 days | **≤ 3 days** | M19 |
| KPI-051 Bank reconciliation auto-match | manual | 90% | **94%** | M50 |
| KPI-052 Days sales outstanding | unmeasured | 38 | **< 32** | M20 |
| KPI-053 Invoices auto-generated | 0% | 100% | **100%** | M20 |
| KPI-054 Invoice within 1 hour of closure | ~3–7 days | 95% | **97%** | M20 |
| KPI-055 Billing accuracy (credit notes as % of invoices) | unmeasured | < 2.5% | **< 1.5%** | M20 |
| KPI-056 Revenue leakage (unbilled delivered work) | unknown | < 1.5% | **< 0.5%** | M20 |
| KPI-057 VAT returns filed on time with zero adjustment | manual | 100% | **100%** | M51 |
| KPI-058 Tax compliance findings | unmeasured | Zero | **Zero** | M51 |

#### People & quality

| KPI | Baseline | W5 | W8 | Source |
|---|---|---|---|---|
| KPI-059 Payroll processing time | 3 days | 6 h | **< 4 h** | M56 |
| KPI-060 Payroll corrections per run | unmeasured | < 0.5% | **< 0.3%** | M56 |
| KPI-061 Attendance capture completeness | manual | 98% | **99%** | M55 |
| KPI-062 Certifications current (no lapses) | unknown | 100% | **100%** | M22 |
| KPI-063 Claims rejected for uncertified technician | unknown | Zero | **Zero** | M22 |
| KPI-064 Mandatory training completion on time | unmeasured | 95% | **98%** | M22 |
| KPI-065 Employee self-service adoption | 0% | 75% | **85%** | M21 |
| KPI-066 CAPA closed on time | unmeasured | 90% | **95%** | M23 |
| KPI-067 ISO major non-conformances | unknown | Zero | **Zero** | M23 |
| KPI-068 Internal audit plan completion | manual | 100% | **100%** | M23 |

#### New business lines

| KPI | Target | By | Source |
|---|---|:--:|---|
| KPI-069 Monitored assets under management | 5,000 | W6 | M05 |
| KPI-070 MSP SLA attainment | 98% | W6 | M05 |
| KPI-071 Remote resolution rate (no site visit) | 65% | W6 | M05 |
| KPI-072 MSP gross margin | 55% | W7 | M05 |
| KPI-073 Data recovery success rate | 82% | W7 | M06 |
| KPI-074 Data-services custody exceptions | **Zero** | W6 | M06 |
| KPI-075 Rental fleet utilisation | 68% | W7 | M13 |
| KPI-076 Rental damage recovery rate | 85% | W7 | M13 |
| KPI-077 Refurbishment yield | 88% | W7 | M14 |
| KPI-078 Refurbished units sold per year | 12,000 | W8 | M14 |
| KPI-079 Approved active marketplace sellers | 500 | W8 | M12 |
| KPI-080 Marketplace share of job volume | 25% | W8 | M12 |
| KPI-081 Marketplace dispute rate | < 1.5% | W8 | M12 |
| KPI-082 Seller payout accuracy | **100%** | W7 | M53 |
| KPI-083 E-waste diversion from landfill | 92% | W8 | M18 |
| KPI-084 Disposal certificates on file | **100%** | W8 | M18 |

#### Platform

| KPI | Target | Source |
|---|---|---|
| KPI-085 System uptime (business hours) | ≥ 99.9% | M28 |
| KPI-086 API p95 latency | < 400 ms | M28 |
| KPI-087 Event delivery success | > 99.9% | M28 |
| KPI-088 Integration failures undetected > 5 min | **Zero** | M28 |
| KPI-089 Critical vulnerabilities open > 7 days | **Zero** | M29 |
| KPI-090 Orphaned accounts after leaver | **Zero beyond 24 h** | M29 |
| KPI-091 Backup restore tests passed | 100% | M29 |
| KPI-092 Bengali translation completeness | **100%** | M30 |
| KPI-093 Data quality test pass rate | > 99% | M62 |
| KPI-094 Manual management reports remaining | **Zero** | M25 |
| KPI-095 Overall automation of routine work | **85%** | All |

> **22 KPI identifiers currently collide across modules** — one identifier resolves to nine
> different metrics. The programme KPI register must be built and ~60 identifiers reassigned before
> benefit reporting can cite KPI IDs unambiguously. See §23.2.

### 20.4 Programme-Level Success Criteria

The programme is successful if, at Month 36:

| # | Criterion | Measure |
|---|---|---|
| 1 | All 14 revenue streams transact end to end in the ERP | **Zero shadow spreadsheets in any revenue process** |
| 2 | Routine operational work is 85% automated | KPI-095 |
| 3 | Month-end close completes in ≤ 3 days across all entities and lines | KPI-050 |
| 4 | 95%+ of eligible warranty claims submitted within 72 hours | KPI-037 |
| 5 | Marketplace delivers ≥ 25% of job volume | KPI-080 |
| 6 | MSP and rental together contribute ≥ 20% of revenue | BO-11, BO-13 |
| 7 | ISO 9001 surveillance passes with zero systems-related major non-conformances | KPI-067 |
| 8 | A second country entity can be stood up without core code change | G9-01 |
| 9 | Management decisions are made on live dashboards | KPI-094 |
| 10 | CSAT ≥ 4.7 and technician app usage ≥ 95% | KPI-020, KPI-016 |

---

## 21. IMPLEMENTATION APPROACH AND GOVERNANCE

### 21.1 Sequencing Logic

| Constraint | Consequence |
|---|---|
| **Technical dependency** | Identity, integration and master data must exist before anything transacts |
| **Business criticality** | The v1.0 commitments come first and land on substantially their original dates |
| **Data accumulation** | Machine learning cannot be built before there is data to learn from — hence AI in Waves 6–8, not Wave 2 |
| **Business absorption capacity** | 51+ branches and 500+ staff absorb roughly **one major process change per quarter**. **UAT super-user availability, not developer capacity, is the binding constraint** |

### 21.2 The Nine Waves

| Wave | Months | Theme | Key business outcome |
|---|---|---|---|
| **W1** | 1–4 | Foundation & Service Core | Identity, integration, party and catalogue masters, service order core, front desk. Pilot: Dhaka HQ + 5 centres |
| **W2** | 5–8 | Field Operations & Inventory | Dispatch, route optimisation, GPS, **technician app offline-first**, workshop, multi-location inventory with van stock, customer portal, loyalty. All Dhaka |
| **W3** | 9–13 | Money, Movement & Documents | Ledger, AR/AP, treasury, Mushak VAT, payment gateways, pricing, quotation, logistics with custody, procurement, warehouse, documents, workflow engine. + Chittagong |
| **W4** | 14–18 | Agreements, Billing & Contact | Contracts across 14 families, warranty claim automation, subscriptions, Bangladesh tax, revenue recognition, contact centre, AI assistant, CX, BI. **v1.0 scope complete.** All active centres |
| **W5** | 19–22 | People, Quality & Managed Services | HR, attendance, payroll, incentives, competency with **hard dispatch enforcement**, QMS, MSP, enterprise assets, fleet, fixed assets. **All 51+ centres** |
| **W6** | 23–26 | New Asset Businesses | Rental, trade-in and refurbishment, data services, demand planning, import and landed cost, FP&A, talent, HSE, GRC, knowledge, internal ITSM, first ML models |
| **W7** | 27–30 | Marketplace & Settlement | E-commerce, marketplace with KYC and payouts, partner and franchise, dynamic pricing, facilities, PPM |
| **W8** | 31–34 | Intelligence & Sustainability | Analytical warehouse, full BI, predictive and pricing models, IoT telemetry, e-waste and ESG |
| **W9** | 35–36 | Expansion Readiness | Multi-entity, country packs, multi-currency, scale hardening |

> **Wave capacity warning.** Wave capacity has **not** been validated against the restated effort of
> 1,513 PW. Wave 4 at ~230 PW against a 17-FTE, ~18-week wave gives roughly 306 available
> person-weeks at 100% capacity, or ~245 at 80% — a fit with almost no contingency. Waves 3 and 6
> are similarly tight. **A capacity re-plan is required before the roadmap is baselined.**

### 21.3 Delivery Method

| Aspect | Approach |
|---|---|
| Cadence | Two-week sprints; five to ten sprints per wave |
| Ceremonies | Sprint planning, daily stand-up, **sprint review with business owners**, retrospective |
| Definition of ready | Requirement has acceptance criteria, a business owner and no unresolved dependency |
| Definition of done | All 17 criteria in §20.1 |
| Demo discipline | **Every sprint review demonstrates working software to the business owner, never slides** |
| Wave gate | Formal Go/No-Go with the Steering Committee against published criteria |
| Hypercare | **Four weeks of elevated support after every wave go-live** |
| Release cadence | Fortnightly to staging; monthly to production within a wave; hotfixes as needed |

### 21.4 Rollout

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
| Payroll | **2 pay cycles** | **Zero tolerance for pay errors** |
| Warranty claims | 1 month | Brand relationship protection |

### 21.5 Training and Change Management

| Requirement | Detail |
|---|---|
| Role-based training | For each of the **46 roles** |
| Train-the-Trainer | **One trained champion per branch**; monthly champion forum |
| **Bengali delivery** | Mandatory for field staff, service centre staff, riders and technicians |
| Environment | Hands-on in the dedicated `training` environment with curated scenario data |
| Materials | Video library, quick-reference cards, in-app guidance, searchable help — **Bengali and English** |
| Administrator training | Configuration, customisation, extension, maintenance |
| **Company developer knowledge transfer** | **20+ days across the programme**, enabling 1000FiX to maintain and extend independently — verified by practical assessment at Gate 9 |
| External party training | Marketplace sellers, brand partners, vendors, corporate portal users |
| Adoption measurement | **Weekly usage reporting by role and branch**, with intervention where adoption lags |
| Support at go-live | Floor-walkers; dedicated internal channel; published escalation path |

**Training volumes:** executives 15–25 (1 day) · service operations 30–50 (3–5 days) · **field
technicians 200–400 (2–3 days per batch of 30, Bengali, mobile-focused)** · service centre staff
150–250 (3–5 days per batch) · logistics and riders 60–175 (1–2 days) · contact centre 34–70 (2–3
days) · finance 15–30 (3–5 days) · HR 10–15 (2–3 days) · quality and audit 5–15 (2–3 days) ·
system administrators 5–10 (5–10 days) · Company developers 3–6 (20+ days) · marketplace sellers
500–2,000 (self-service) · corporate portal users 500–2,000 (account-manager-led).

**Adoption risk by group:**

| Group | Risk | Mitigation |
|---|---|---|
| **Field technicians** | **Critical** — app rejection collapses the field model | Bengali-first, extremely simple UX, field pilot with respected senior technicians, device provision, **incentive visibility as an immediate personal benefit** |
| Branch counter staff | High — highest transaction volume | **Speed as the design goal** with measured intake time; champion-led training |
| Finance staff | Medium — process change and control tightening | Early involvement in design; parallel running; audit-trail benefit emphasised |
| Branch managers | Medium — visibility cuts both ways | Position dashboards as **their tool, not surveillance**; involve in KPI design |
| Marketplace sellers | High — external, low switching cost | Simple onboarding, **fast payouts**, transparent scoring |
| Corporate clients | Medium | Account-manager-led onboarding; demonstrable time savings |

### 21.6 Support Model

| Element | Requirement |
|---|---|
| Hypercare | 4 weeks after every wave go-live, with a named lead and daily triage |
| Business-hours support | **09:00–22:00 BST, Sunday–Thursday** |
| Critical support | **24/7 for system-down and severity-1** — managed services clients require it |
| Resolution SLAs | **Critical 4 h · High 8 h · Medium 24 h · Low 72 h** |
| Language | **Bengali-speaking support staff** |
| Root cause analysis | On every Critical and High incident, delivered within 5 working days |
| Maintenance | Quarterly patching; **security patches within 48 hours** of critical disclosure |
| Continuity | **Backup verification weekly; DR failover exercised twice yearly** |
| Regulatory currency | **Annual review of every statutory citation embedded in the system** |
| Warranty | **Minimum 12 months per wave** for defect correction at no additional cost |
| Escrow | Source code escrow for any proprietary component |
| Transition | No less than 90 days' assistance at contract end |

### 21.7 Governance

```
                    ┌──────────────────────────────┐
                    │           BOARD              │
                    │  Investment approval         │
                    │  Quarterly programme review  │
                    └───────────────┬──────────────┘
                    ┌───────────────▼──────────────┐
                    │  ERP STEERING COMMITTEE      │
                    │  CEO (chair) · CTO · CFO ·   │
                    │  CCO · Ops Director ·        │
                    │  HR Director · Quality Mgr   │
                    │  Monthly · Gate decisions ·  │
                    │  Change control · Risk       │
                    └───────────────┬──────────────┘
        ┌───────────────────────────┼───────────────────────────┐
┌───────▼────────┐        ┌─────────▼─────────┐      ┌──────────▼─────────┐
│ PROGRAMME      │        │ ARCHITECTURE      │      │ BUSINESS OWNERS    │
│ MANAGEMENT     │        │ REVIEW BOARD      │      │ FORUM              │
│ OFFICE         │        │ CTO · Architect · │      │ 16 module owners   │
│ Weekly         │        │ Leads · Security  │      │ Fortnightly        │
└───────┬────────┘        └───────────────────┘      └────────────────────┘
┌───────▼─────────────────────────────────────────────────────────────────┐
│  DELIVERY SQUADS — Service · Commercial · Supply · Finance · People ·   │
│  Platform · Data.  Daily stand-up · Fortnightly sprint review with owners│
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
| New commercial (L6) component | CFO, on Architecture Board recommendation |
| **Requirement acceptance at UAT** | **Named business owner** |
| Risk acceptance (Critical or High) | Steering Committee |
| Segregation-of-duties exception | CFO or CTO, time-boxed |
| Production emergency change | CTO, with retrospective Steering review |

**Cadence:** daily stand-up (squad) · fortnightly sprint review and Business Owners Forum ·
fortnightly Architecture Review Board · weekly PMO report · monthly Steering Committee · wave gate
review per wave · quarterly Board review · **post-implementation review at Month 42**.

### 21.8 Change Control

```
Change raised
   ├─► Impact assessment: scope · cost · schedule · risk · benefit
   ├─► Classification
   │      P2/P3 within a module ──► PMO + business owner ──► approve/defer
   │      P0/P1, cross-module, or cost impact ──► Steering Committee
   │      Architecture standard ──► Architecture Review Board
   ├─► Decision recorded with rationale
   └─► Baseline updated · affected documents versioned · communicated
```

**Rules:** no change is implemented before it is approved and recorded · **no wave absorbs a change
mid-wave** — approved changes enter the next wave · **a change that removes scope must state which
benefit is forgone** · the change log is reviewed at every Steering Committee meeting.

### 21.9 Contingency

| Scenario | Response |
|---|---|
| Wave slips ≤ 4 weeks | Absorb in the next wave's buffer; no dependency change |
| Wave slips > 4 weeks | Steering Committee decides: descope P2/P3, extend, or reallocate |
| Business UAT capacity unavailable | Wave gate slips; **development does not run ahead into unaccepted work** |
| Key integration blocked externally | Deliver the module with the documented manual fallback; integrate later |
| Adoption failure at a location | Pause rollout, diagnose, remediate, re-pilot before continuing |
| Budget pressure | **Defer W8 and W9 first; W6 and W7 are the revenue-generating waves** |
| Team attrition | Two-person knowledge coverage on every module; documentation as definition-of-done |

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

### 21.10 Programme Closure

| Criterion | Evidence |
|---|---|
| All wave gates passed | Signed gate reports |
| All P0 and P1 requirements delivered or formally superseded | Traceability matrix at 100% |
| All legacy systems and manual processes decommissioned | Decommission register complete (§6.5) |
| All documentation handed over and accepted | Document register; acceptance signature |
| Support model transitioned to steady state | Support agreement in force; runbooks accepted |
| Team knowledge transferred | Handover sessions completed; two-person coverage verified |
| Benefits tracking established and running | KPI dashboard live with named owners |
| Outstanding items transferred to business-as-usual backlog | Backlog accepted by the CTO |
| Final financial reconciliation of programme spend | CFO sign-off |
| Lessons learned documented | Retrospective report to the Board |

---

## 22. AUTOMATION CATALOGUE

**Target: 85% of routine operational work automated by Wave 8.** Each automation has a trigger, an
action, a failure behaviour and an owner. **Failure behaviour is as important as the automation
itself** — an automation that fails silently is worse than no automation.

### 22.1 Service Delivery Automations

| ID | Trigger | Action | Failure behaviour |
|---|---|---|---|
| AUT-001 | Booking received on any channel | Create service order, evaluate entitlement, assign SLA, acknowledge to customer, enter dispatch queue | Queue for manual creation; alert |
| AUT-002 | Order enters dispatch queue | Score candidates; auto-assign above confidence or present a ranked list | Present list to dispatcher |
| AUT-003 | Technician assigned | Notify technician and customer; publish tracking link; update route | Manual notification task |
| AUT-004 | Diagnosis completed | Draft estimate from fault code and standard repair mapping | Blank estimate for manual build |
| AUT-005 | Estimate issued | Send on preferred channels; start expiry timer; remind at 24 h and 48 h; expire on limit | Manual follow-up task |
| AUT-006 | Customer approves | Reserve parts, release work order, notify technician | Manual release task |
| AUT-007 | Parts unavailable | Search network; recommend source; raise transfer or purchase; hold job; inform customer with revised ETA | Escalate to inventory manager |
| AUT-008 | QC passed | Generate service report, raise invoice, notify customer as Ready | Manual invoice task |
| AUT-009 | SLA at 50/75/90/100% | Escalate to defined roles with acknowledgement tracking | Repeat and escalate further |
| AUT-010 | Job completed | Trigger CSAT survey after the configured delay | Retry once, then drop |
| AUT-011 | Same device + fault within 30 days | Flag rework, link records, notify quality and the technician's manager | — |
| AUT-012 | Device ready and uncollected | Reminder sequence at 3, 7, 15 and 30 days; then abandonment process | — |
| AUT-013 | Nightly 05:00 | Optimise all routes for the next day; publish; notify technicians | Retain previous manual sequence |
| AUT-014 | Technician syncs offline work | Reconcile parts, time and evidence; release downstream actions | Flag conflicts for review |

### 22.2 Commercial & Revenue Automations

| ID | Trigger | Action | Failure behaviour |
|---|---|---|---|
| AUT-015 | Contract expiry − 90/60/30/15 days | Notify customer and account owner; generate renewal quotation at 60 days | Manual renewal task |
| AUT-016 | Contract activated | Generate the full preventive-maintenance schedule for the term | Manual scheduling task |
| AUT-017 | Preventive visit due − lead time | Create the work order and enter the dispatch queue | Alert account manager |
| AUT-018 | Warranty job closed | Create claim, assemble evidence pack, validate completeness, queue for submission | Manual claim task with checklist |
| AUT-019 | Claim validated | Submit to the brand in their required format | Route to manual submission queue |
| AUT-020 | Brand response received | Update claim; on approval queue for billing; on rejection open a dispute task | Manual review queue |
| AUT-021 | Brand remittance received | Match to claims; post to ledger; flag unmatched | Manual matching queue |
| AUT-022 | Invoice issued | Deliver on preferred channels with payment link | Retry; then manual delivery task |
| AUT-023 | Invoice unpaid at 7/14/21/30 days | Execute the dunning sequence; at 30 days enter collections | — |
| AUT-024 | Payment received | Match to invoice; mark paid; post to ledger; receipt to customer | Manual matching queue |
| AUT-025 | Subscription cycle due | Generate the invoice with proration and usage | Alert finance |
| AUT-026 | Marketplace job completed and hold period elapsed | Accrue commission; add to the next payout run | Hold and alert |
| AUT-027 | Payout run scheduled | Calculate, produce statements, generate the disbursement file, request approval | Alert finance |
| AUT-028 | Refund approved | Execute through the original method; post; notify customer | Manual refund task |
| AUT-029 | Customer registers | Award registration points; send welcome journey; set preferences | Retry |
| AUT-030 | Referral converts | Credit both parties; notify; accrue partner commission | Manual credit task |

### 22.3 Supply Chain Automations

| ID | Trigger | Action | Failure behaviour |
|---|---|---|---|
| AUT-031 | Stock reaches reorder point | Alert; draft purchase requisition with recommended quantity | Alert only |
| AUT-032 | Requisition approved | Generate and transmit the purchase order; track acknowledgement | Manual PO task |
| AUT-033 | Goods received and inspected | Update stock; allocate landed cost; trigger three-way match | Manual posting task |
| AUT-034 | Three-way match successful | Route the vendor invoice to the payment schedule | Exception queue |
| AUT-035 | Technician shift ends | Reconcile van stock; report variance to branch manager | Alert |
| AUT-036 | Cycle count due | Generate the count task list by ABC class and location | Alert inventory manager |
| AUT-037 | Dead stock threshold reached | Produce a disposition recommendation | — |
| AUT-038 | Asset telemetry breaches threshold | Raise an alert; correlate; open a ticket if the rule requires | Alert only |
| AUT-039 | Predicted failure above confidence | Notify account manager; propose a proactive service booking | — |
| AUT-040 | E-waste item triaged for recycling | Verify a destruction certificate exists; batch for transfer | **Block and alert** |

### 22.4 People, Finance & Governance Automations

| ID | Trigger | Action | Failure behaviour |
|---|---|---|---|
| AUT-041 | Certification expiry − 90/60/30/15 days | Notify technician, manager and HR; schedule re-certification | Escalate |
| AUT-042 | Certification expires | **Remove the technician from that brand's warranty dispatch pool** | — |
| AUT-043 | Month end | Run close checklist, accruals, prepayment amortisation, FX revaluation, recurring journals | Alert finance |
| AUT-044 | Bank statement imported | Auto-match; present only exceptions | Full manual reconciliation |
| AUT-045 | Payroll period locked | Calculate payroll, incentives and tax; present for approval | Alert HR |
| AUT-046 | Payroll approved | Generate the BEFTN file, distribute payslips, post to ledger | Alert finance |
| AUT-047 | Employee joins | Create identity, assign role from position profile, grant portal access, assign onboarding and mandatory training | Manual provisioning task |
| AUT-048 | Employee leaves | **Revoke all access within one hour**; deregister devices; reassign delegated authority; trigger clearance | **Immediate escalation** |
| AUT-049 | Quality event (rework, failed QC, complaint) | Raise a non-conformance; route to the process owner | Alert quality manager |
| AUT-050 | CAPA due date + verification interval | Prompt effectiveness verification; reopen if not verified | Escalate |
| AUT-051 | Document reaches end of retention | Present for disposal review unless under legal hold | Hold and alert |
| AUT-052 | Access certification cycle due | Issue review tasks to all managers; **revoke unconfirmed access at the deadline** | Escalate to CTO |

### 22.5 Platform Automations

| ID | Trigger | Action | Failure behaviour |
|---|---|---|---|
| AUT-053 | Integration error rate above threshold | Alert the owner; open the circuit breaker; activate the documented fallback | Escalate |
| AUT-054 | Event in dead letter > 1 hour | Alert; create a triage task | Escalate |
| AUT-055 | Backup completes | Verify integrity; report; alert on failure | Immediate escalation |
| AUT-056 | Scheduled restore test due | Execute; verify; record evidence | Escalate |
| AUT-057 | Model drift detected | Alert the model owner; schedule retraining; continue with the current model | Fall back to rules |
| AUT-058 | Security anomaly detected | Alert; if severity warrants, suspend the session and require re-authentication | Escalate |
| AUT-059 | Data quality test fails | **Block the dependent dashboard refresh**; alert the data owner | Show last-known-good with a staleness warning |
| AUT-060 | Certificate or credential expiry − 30 days | Alert the owner; create a rotation task | Escalate at 7 days |

---

## 23. DISCLOSED OPEN ITEMS AND KNOWN DEFECTS

The specification set behind this BRD has been audited **twice**. This section discloses what those
audits found. It is stated openly because a business case built on hidden defects is not a business
case, and an implementation partner pricing against a specification whose defects are concealed
will either lose money or cut corners.

### 23.1 Specification Completeness

| # | Item | Status | Business consequence |
|---|---|---|---|
| 23.1.1 | **M66 Internal IT Service Management and M67 Project, Program & Portfolio Management have no specification file.** The only two outstanding module specifications. Estimated 22 and 26 requirements, 11 and 14 PW | **Open** — to be written before Wave 6 | M66 is referenced by M58 onboarding provisioning, M29 access requests and M59 equipment findings; **those interface contracts are currently unverifiable** |
| 23.1.2 | **28 requirement IDs in Category A are allocated but unused** — 16 in M01, 9 in M02, 3 in M31. Recorded counts were taken from the highest ID rather than the actual count | **Fixed in the register; open in the modules** | Category A's registered total of 388 was **26 overstated**; the measured figure is 362. Recommendation: **retire** the unused IDs rather than renumber, since renumbering would violate permanent-identity rule RG-02 |
| 23.1.3 | The specification set is **93 documents written of 123 planned (76%)** | In progress | Planned-but-unwritten: market benchmark study, module gap analysis, module boundary rules, 12 per-portal specifications, consolidated identifier conventions, four delivery documents. Module boundaries are currently declared in each category overview and each module file §3 |

### 23.2 Identifier and Register Integrity

| # | Item | Status | Business consequence |
|---|---|---|---|
| 23.2.1 | **More than 70 custom-development (`CD-nnn`) identifiers collide across modules** — some claimed by up to 8 different modules | **Open — must be resolved before any build contract is issued** | CD identifiers name **deliverable software modules** and will appear in the build backlog, repository structure and deployment manifest. **A collision here becomes a real conflict at build time, not a documentation defect.** A unified CD register with sole allocating authority is Wave 1 scope |
| 23.2.2 | **22 KPI identifiers are used by two or more modules** — one identifier resolves to nine different metrics | Open | **§20.3 reports benefits by KPI ID; those references are currently ambiguous.** The programme KPI register must be built and ~60 identifiers reassigned. Wave 1 scope |
| 23.2.3 | **18 segregation-of-duties controls (SOD-13…SOD-30) are implemented in module specifications but unregistered** in the central matrix — including SOD-29 (payroll approver cannot release the bank file) and SOD-30 (M57 calculates the incentive; only M56 can pay it) | Open | **An external auditor will ask for the SoD matrix. If it omits 18 of the 30 controls the system implements, the controls cannot be evidenced — and controls that cannot be evidenced are, for audit purposes, controls that do not exist.** Registration of all 30 is Wave 1 scope |
| 23.2.4 | **Roles R39–R46 are used but unregistered; R54 and R57 are referenced with no definition; R60 is a duplicate identity for R32** | Open — **R60 is a live permission defect** | A duplicate role identity means **an access rule written against R32 does not apply to a user granted R60, and vice versa.** In a permission model this is a security defect. Extend the register to R46, eliminate R60, resolve R54 and R57 — Wave 1 scope |
| 23.2.5 | **NFR-090, NFR-091 and NFR-092 are used twice** — once in the maintainability range (test coverage, runbook, tracing) and once in the PDPA range (consent, transparency notice, data-subject rights) | Open | Ambiguous in traceability and test planning. Both meanings are stated in §9.6 and §9.7; the ranges must be de-conflicted before the requirements baseline is frozen |
| 23.2.6 | M42 uses the four-character code `SRM2` against a three-character convention, because `SRM` is permanently allocated to M01 | **Accepted and documented** | Use the codes exactly as allocated |

### 23.3 Cost, Effort and Scope

| # | Item | Status | Business consequence |
|---|---|---|---|
| 23.3.1 | **Programme effort measures 1,513 PW against 834 PW in the approved business case — approximately 1.8×.** Requirements measure 2,930 against 1,180 — +148% | **Escalated as Steering Committee decision D-14** | The Committee has not yet chosen between funding, phasing or cutting. **The Board has been working from a figure the audit found materially low.** §19.1 states the restated position |
| 23.3.2 | **Wave capacity has not been validated against the restated effort.** W4 at ~230 PW against a 17-FTE, ~18-week wave leaves almost no contingency; W3 and W6 are similarly tight | Open | A capacity re-plan is required before the roadmap is baselined |
| 23.3.3 | The ROI figures in the Company's internal charter documents were computed against the **superseded** cost line | Being re-baselined | §19.4 uses the restated cost. The charter documents are under revision |

### 23.4 Superseded v1.0 Requirements

**No v1.0 requirement has been deleted.** Four are formally superseded by a stronger v2.0
requirement:

| v1.0 requirement | Superseded by | Reason |
|---|---|---|
| INT-022 — Rasa 3.6 Bengali chatbot | FR-CAI-* (LLM-based Bengali assistant, M32) | Rasa open source is in maintenance mode |
| INT-019 — Google Routes / Timefold routing | FR-FSM-* (VROOM + OSRM with selective traffic API) | $0 licence, self-hosted, embeds custom skill/certification/van-stock constraints |
| BR-BI-007 — drag-and-drop report builder | FR-BID-018 (semantic-layer self-service exploration) | Warehouse-backed approach supersedes the point tool |
| BR-DMS-003 — approval workflows in DMS | FR-BPA-* (one platform-wide workflow engine, M63) | One workflow engine serves all modules |

### 23.5 Decisions Required

| # | Decision | Owner | Needed by | Consequence if delayed |
|---|---|---|---|---|
| **D-13** | **Approve the split-residency data architecture**, subject to the legal opinion in DEP-31 | CTO + CFO + Legal | **Before Wave 1 architecture is fixed** | **The entire data architecture is blocked. The most urgent open decision in the programme** |
| **D-14** | **Accept the restated TCO of $690K–1,150K, or direct a descope** | Board / CEO / CFO | Before the next Board review | The Board is working from a materially low figure |
| **D-15** | **Confirm whether 1000FiX is a *significant data fiduciary* and, if so, appoint a Chief Data Officer** | CEO + Legal | W4 − 3 months | Statutory non-appointment; penalty exposure |
| D-01 | Approve the expanded scope, budget and 36-month horizon | Board / CEO | Before kickoff | Programme cannot start |
| D-02 | **Confirm and protect business super-user availability across all waves** | CEO + department heads | Before kickoff | **RSK-001 materialises; waves slip** |
| **D-03** | **Marketplace commercial model — principal vs agent, commission structure, settlement terms, liability** | CEO + CFO + Legal | W7 − 3 months | **RSK-022; Wave 7 blocked** |
| D-04 | Legal-entity structure for rental and refurbished resale | CFO + Legal | W6 − 3 months | Finance design blocked; possible rework |
| D-05 | Multi-country target markets and sequence | CEO | W9 − 3 months | Country pack cannot be specified |
| D-06 | Telephony vendor for hotline 16743 | CTO | W4 − 2 months | Contact centre build blocked |
| D-07 | Whether to adopt a commercial RMM agent | CTO + CFO | W5 | Pilot outcome determines |
| D-08 | Data residency posture for recovered customer data | CTO + Legal | W6 − 2 months | M06 blocked |
| D-09 | Whether 1000FiX guarantees marketplace work to the customer | CEO + Legal | W7 − 3 months | Liability model undefined |
| D-10 | Seller insurance requirement and liability caps | Legal | W7 − 3 months | Seller agreement undefined |
| D-11 | Technician device procurement model (Company-issued vs allowance) | Ops Director + CFO | W2 − 2 months | Field rollout blocked |
| D-12 | Refurbished warranty terms and reserve policy | CFO + Retail Head | W6 | M14 commercial model undefined |
| **Q-01** | M61 knowledge core to W4, or M32 launches with reduced intent scope | CTO + Customer Service Manager | W4 planning | AI assistant cannot answer "how do I" or "why is this happening" |
| **Q-05a** | M27 notification service to W1/W2 rather than W4 | CTO + Ops Director | **Before Wave 1 build** | **Each earlier module builds its own send path — recreating the fragmentation the programme exists to remove** |
| **Q-05b** | M59 mobile incident reporting to W3 with the technician app | HR Director + Ops Director | W3 planning | Safety reporting waits until W6 for no technical reason |

### 23.6 Facts Under Verification

| # | Item | Status |
|---|---|---|
| 23.6.1 | The **"17+ brands"** figure, carried from the v1.0 BRD, underpins M22's certification coverage reporting and KPI-062/KPI-063. **It has not been verified against the current principal agreement list** | Written confirmation being sought from each principal before Wave 5 |
| 23.6.2 | **AY 2026–27 income tax parameters** used in M56 — thresholds BDT 375,000 / 425,000 / 500,000 / 525,000; minimum tax BDT 5,000 (BDT 1,000 first-time); investment rebate 10% capped at BDT 750,000 eligible investment. **Sources conflict on whether the 5% introductory slab survives** | **The statutory pack must be built from the enacted Finance Act, not from press reporting.** Verification required at W5 − 3 months. The tax pack must be **versioned configuration** so a late parameter change is not a code change |

### 23.7 What the Audits Confirmed as Sound

Stated for balance, because an audit that reports only faults is not credible:

| Area | Assessment |
|---|---|
| **Module boundary logic** | Sound. The M01/M31, M33/M07, M27/M32, M15/M41, M05/M66 and M23/M60 boundaries are each defensible with both sides declared |
| **Benchmark grounding** | Accurate. SAP In-House Repair, Oracle Depot Repair, IFS, Dynamics 365 and ITIL references verified against current vendor documentation |
| **Evidence traceability** | Strong. Every new module traces to a specific section of the business plan, the Service App SOW or the portal roadmap, and those citations are accurate |
| **Bangladesh VAT mechanics** | Correct. Mushak 6.3 as tax invoice and Mushak 9.1 as monthly return accurately described |
| **ISO 9001:2015 clause mapping** | Correct. Clauses 4, 5, 6, 7.1.5, 7.2, 7.5, 8.2, 8.4, 8.5.1, 8.5.2, 8.6, 8.7, 9.1, 9.2, 9.3 and 10 cited accurately |
| **Benefit model internal logic** | Consistent. Benefit figures reconcile across the charter, the KPI document and the module files — **the issue was the cost side, not the benefit side** |
| **Category A functional depth** | Appropriate — at a level an implementation partner could quote against |

### 23.8 Governance Controls Adopted in Response

| Rule | Statement |
|---|---|
| **RG-01 (extended)** | **Register-first** applies to **every programme-wide identifier space** — `KPI-`, `CD-`, `SOD-`, `R`, `RSK-`, `DEP-`, `D-`, `NFR-`. No module file may introduce an identifier in a shared space that does not already exist in its owning register |
| **RG-02** | Module IDs and codes are **permanent**. A retired or allocated code is never reused |
| **RG-03** | Every module has exactly one business owner and one system owner |
| **RG-04** | **Boundary symmetry** — if module A declares a capability out of scope and owned by module B, module B must claim it |
| **RG-05** | Figures marked *(est.)* are extrapolations and **must not be used for contractual commitment** |
| **RG-06** | **Count, do not consult.** Any figure describing what the repository contains must be derived by **direct enumeration at the time of writing**. A prior statement of the same figure is not evidence. Every such figure carries the date it was counted |
| **DoD-17** | Every regulatory citation carries a **verified-on date**, re-verified at each wave gate |

---

### 23.9 BRD v2.0 Audit Record

This document was audited on issue, against RFP v2.0 and the underlying module specification set,
under governance rule **RG-06 (count, do not consult)** — every figure was re-derived by direct
enumeration rather than accepted from a prior statement.

#### Method

| # | Check | How |
|---|---|---|
| 1 | Category module counts, requirement totals and effort totals | Arithmetic re-computation against the register |
| 2 | Per-module figures summed against their category totals | Arithmetic, all 11 categories |
| 3 | Benefit model | All three scenario columns and both subtotals re-added |
| 4 | Cost model | All component lines and year columns re-added |
| 5 | Priority distribution | Summed against the 67-module total |
| 6 | Identifier completeness | Direct enumeration of BO, KPI, AUT, SOD, R, M, P, RSK and DEP identifiers in this document |
| 7 | Module coverage | Every module M01–M67 confirmed present |
| 8 | Figure consistency with RFP v2.0 | Cross-document grep on 14 headline figures |
| 9 | Regulatory citations | Verified-on dates present on every statutory reference |

#### Verified clean

| Check | Result |
|---|---|
| Category module counts | **67** — 7+7+9+3+6+5+8+7+4+4+7 ✓ |
| Category requirement totals | **2,930** ✓ matches the measured register total |
| Category effort totals | **1,513 PW** ✓ |
| Benefit model — conservative / base / optimistic | **521 / 876 / 1,273 BDT lac** ✓ all three columns re-add exactly |
| Benefit subtotals — existing vs new revenue streams | 306/502/703 and 215/374/570 ✓ |
| Priority distribution | 13 + 31 + 21 + 2 = **67** ✓ |
| Business objectives | **18 distinct (BO-01…BO-18)** ✓ |
| KPI register | **95 distinct (KPI-001…KPI-095)** ✓ |
| Automation catalogue | **60 distinct (AUT-001…AUT-060)** ✓ |
| Roles | **46 distinct (R01…R46)** ✓ |
| Modules | **all 67 present, none out of range** ✓ |
| Portals | **12 distinct (P01…P12)** ✓ |
| Cost model — component lines and year columns | Internally consistent ✓ |
| Headline figures vs RFP v2.0 | All 14 checked figures consistent ✓ |
| Regulatory citations | All carry verified-on dates per DoD-17 ✓ |

#### Findings raised and corrected in this issue

| ID | Severity | Finding | Action taken |
|---|:--:|---|---|
| **BA-01** | **High** | **Per-module requirement figures do not sum to their category totals in eight of eleven categories.** The per-module figures are the register's *estimates*; the category totals are the register's *measured* counts. Presented side by side without qualification, a reader adding the column would find a discrepancy of up to +73% (Category F) and would under-scope | **Fixed.** §4.2 now carries a reconciliation table showing both bases and the variance per category; estimated columns are marked *(est.)*; category headings are marked **measured**; the instruction to plan and contract against the measured totals is explicit. The same correction was applied to RFP §6.1a |
| **BA-02** | **Medium** | **The TCO component lines sum to $713K–1,277K against a headline of $690K–1,150K.** Both figures are correct on their own basis — the headline applies measured effort to approved unit rates; the component sum assumes every line lands at its extreme simultaneously | **Fixed.** §19.1 now shows both rows explicitly with an explanation of which to use for what. The same correction was applied to RFP §16.1 |
| **BA-03** | **Medium** | **The wave table's requirement column sums to ~1,180, not 2,930.** The per-wave counts are inherited from the original 30-module roadmap and were never restated | **Fixed and disclosed.** §4.6 now shows the total and states that per-wave counts indicate relative size only, pending the capacity re-plan already required under §23.3.2 |
| **BA-04** | Low | **Wave module counts diverged from the authoritative register** — this document had 9 modules in W1 and 5 in W8 against the register's 8 and 4 | **Fixed.** Counts now follow the register's wave view. The underlying source inconsistency (the register records M07 as W1/W4 and the roadmap places M25 partly in W8, but the register's wave view omits both) is **disclosed in §4.6 for resolution at roadmap baseline** |
| **BA-05** | Low | `NFR-090`, `NFR-091` and `NFR-092` carry two meanings each — maintainability and data protection — inherited from the source register | **Disclosed, not fixed.** Recorded as §23.2.5. Both meanings are stated in §9.6 and §9.7. De-confliction is required before the requirements baseline is frozen |

#### Findings carried from the source audits, not introduced here

All items in §23.1 through §23.6 are inherited defects in the specification set, identified by the
two prior audits (`00-06` and `00-07`) and reproduced here rather than concealed. **Ten remain
open**, of which the two that become expensive if deferred are the **duplicate role identity R60**
(a live permission defect) and the **70+ colliding CD identifiers** (which become real build
conflicts the moment a backlog is created).

#### Audit conclusion

**This BRD is fit for Steering Committee review, subject to the eight open decisions in §23.5.**
Its arithmetic is internally consistent, its identifier spaces are complete, and it is consistent
with RFP v2.0 on every headline figure. **It is not yet fit to be used as a frozen requirements
baseline** — that requires: the two outstanding module specifications (§23.1.1), the CD and KPI
register reconciliations (§23.2.1–2), the role and SoD register completion (§23.2.3–4), the NFR
range de-confliction (§23.2.5), and the wave capacity re-plan (§23.3.2).

*Audit performed 13 August 2026 · Business Analysis Team · Method: RG-06 direct enumeration*

---

## 24. APPENDICES

### Appendix A — Requirements Traceability Matrix (Summary)

The full RTM covering all 2,930 functional requirements is maintained in the requirement
management tool and mirrored in the module specification files. This summary demonstrates the
traceability chain: **Business Objective → Business Requirement → Functional Requirement Range →
Business Rule → Acceptance Criterion → KPI.**

| BO | Business requirement | FR range | Key business rule | Gate criterion | KPI |
|---|---|---|---|---|---|
| BO-01 | Automate the service order lifecycle | `FR-SRM-*`, `FR-FSM-*`, `FR-BPA-*` | BRU-SRM-04 QC before completion | G1-02, G8-03 | KPI-001, KPI-095 |
| BO-02 | Maximise technician productivity | `FR-FSM-*`, `FR-AIM-*` | BRU-FSM-03 confidence threshold | G2-04, G6-04 | KPI-011, KPI-013 |
| BO-03 | Inventory accuracy | `FR-INV-*`, `FR-WMS-*`, `FR-DPL-*` | BRU-INV-02 transfer approval | G2-06, G2-07 | KPI-042, KPI-047 |
| BO-04 | Recover warranty revenue | `FR-WTY-*` | BRU-WTY-01 evidence completeness; BRU-WTY-02 24 h creation | G4-01, G4-02 | KPI-037, KPI-038 |
| BO-05 | CSAT and turnaround | `FR-SRM-*`, `FR-CXM-*`, `FR-CCE-*` | BRU-SRM-10 Privilege SLA | G4-07 | KPI-020, KPI-002 |
| BO-06 | Compress the close | `FR-FIN-*`, `FR-ARB-*`, `FR-TRE-*` | BRU-FIN-05 no close with unposted entries | G3-05 | KPI-050, KPI-053 |
| BO-07 | Real-time visibility | `FR-BID-*`, `FR-DAT-*` | — | G4-09, G8-01 | KPI-094 |
| BO-08 | Grow contracts | `FR-CTR-*`, `FR-SUB-*`, `FR-LOY-*` | BRU-CTR-01 activation preconditions | G4-03, G4-04 | KPI-028, KPI-029 |
| BO-09 | Remove capacity constraints | All | — | Programme success criterion 1 | Revenue growth |
| BO-10 | Regulatory compliance | `FR-TAX-*`, `FR-PAY-*`, `FR-CPM-*`, `FR-GRC-*` | BRU-FIN-01 VAT + BIN; NFR-090…099 PDPA | G1-13, G3-04, G4-11 | KPI-057, KPI-058 |
| BO-11 | MSP as a revenue line | `FR-RMS-*` | BRU-CTR-08 automatic service credits | G5-05 | KPI-069, KPI-072 |
| BO-12 | Marketplace capacity | `FR-MKP-*`, `FR-REV-*` | BRU-ECM-03 same standards as owned work | G7-01, G7-02 | KPI-080, KPI-082 |
| BO-13 | Rental as a business | `FR-RNT-*` | BRU-RNT-01 pre-dispatch condition report | G6-01 | KPI-075, KPI-076 |
| BO-14 | Circular device business | `FR-TRF-*`, `FR-ESG-*` | **BRU-TRF-01 destruction certificate before refurbishment** | G6-02, G8-04 | KPI-078, KPI-083 |
| BO-15 | Competency as a control | `FR-LMS-*` | **BRU-SRM-09 / BRU-HRM-01 hard dispatch block** | G5-03 | KPI-062, KPI-063 |
| BO-16 | Conversations in the system | `FR-CCE-*`, `FR-CAI-*` | — | G4-06 | KPI-025, KPI-027 |
| BO-17 | Decisions on live data | `FR-BID-*`, `FR-DAT-*` | AUT-059 data quality blocks refresh | G8-01 | KPI-093, KPI-094 |
| BO-18 | Second-country readiness | `FR-GLO-*` | — | G9-01 | Time to country pack |

**Traceability governance:** every requirement has a named business owner who accepts it at UAT ·
an ID is never reused; a withdrawn requirement's ID is retired · adding or changing a P0/P1
requirement requires Steering Committee approval · **no requirement enters a sprint without a
testable acceptance criterion** · every requirement links to at least one test case and one demo
scenario before it can be marked Verified · the PMO reports requirement status by module and wave
fortnightly · **a deferred requirement moves wave with a recorded reason and a new target; it is
never silently dropped**.

### Appendix B — Authorised Brand Partner Matrix

| Brand | Product categories serviced | Warranty type | Typical claim method |
|---|---|---|---|
| Dell | Laptops, desktops, servers, monitors | Full warranty + extended | Partner portal |
| HP | Laptops, desktops, printers | Full warranty + extended | Service partner portal |
| Lenovo | Laptops, desktops | Full warranty | Partner portal / email |
| Acer | Laptops, desktops | Full warranty | Email + documentation |
| Samsung | Mobile, tablet, TV, appliances | Full warranty | Partner system |
| Xiaomi | Mobile, smart devices | Full warranty | Service portal |
| Huawei | Mobile, networking | Full warranty | Partner portal |
| Honor | Mobile | Full warranty | Partner portal |
| Sony | Laptops, electronics | Full warranty | Email documentation |
| Toshiba | Laptops | Full warranty | Email documentation |
| Gigabyte | Motherboards, components | Full warranty | Email documentation |
| Microsoft | Surface devices | Full warranty | Partner centre |
| BenQ | Monitors, projectors | Full warranty | Partner email |
| Epson | Printers | Full warranty | Partner portal |
| Intel | Components | Full warranty | Partner program |
| TwinMOS | Memory, storage | Full warranty | Email documentation |
| Delux | Peripherals | Full warranty | Email documentation |

*Each partner has its own claim format, evidence requirements, rate card and technician
certification requirements — the core driver of M09 and P08. Per-brand claim specifications are
required at Wave 4 (DEP-22). **The brand count is under verification — §23.6.1.***

### Appendix C — The Fourteen Contract Product Families

M08 must model all of these **without code change**. This is why it is specified as a contract
engine.

| Family | Products |
|---|---|
| Residential AMC (RAMC) | 6 appliance packages |
| Commercial AMC | Office, retail, restaurant equipment |
| IT Infrastructure AMC | Servers, network, storage, backup |
| Healthcare Equipment AMC | **With mandatory calibration** |
| Specialty Equipment AMC | Manufacturing, R&D, telecom |
| Managed Services | Basic · Comprehensive · Security · Cloud · DR/BC · IT Strategy |
| Mobile & Appliance Service | Basic · Comprehensive · Extended Warranty · Accidental Damage · Priority |
| Rental master agreements | Framework with call-off |
| Marketplace seller agreements | Terms, commission, standards |
| Brand partner agreements | Authorised service terms, rate cards |

**The seven protection product families (M09):** Standard Warranty Extension · Accidental Damage
Protection · Extended Repair Coverage · Mobile Device Protection · Home Appliance Protection ·
Computer & Laptop Care · Customised Coverage.

### Appendix D — Reference Documents

| Document | Reference | Location |
|---|---|---|
| **ERP Comprehensive RFP v2.0 — the governing document** | **1000FIX-ERP-RFP-2026-002** | `primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` |
| Module Catalogue Master Register — **authoritative on module identity** | FIX-ERP2-022 | `1000fix_ERP_Module/02_Architecture/02-02_*` |
| Executive Summary & Scope Charter | FIX-ERP2-001 | `1000fix_ERP_Module/00_Governance_and_Charter/00-02_*` |
| Scope Expansion Delta v1→v2 | FIX-ERP2-002 | `1000fix_ERP_Module/00_Governance_and_Charter/00-03_*` |
| Risks, Assumptions, Dependencies & Governance | FIX-ERP2-020 | `1000fix_ERP_Module/00_Governance_and_Charter/00-04_*` |
| **Documentation Audit Report (audit 1)** | FIX-ERP2-006 | `1000fix_ERP_Module/00_Governance_and_Charter/00-06_*` |
| **Category H Audit & Repository Integrity Report (audit 2)** | FIX-ERP2-00-07 | `1000fix_ERP_Module/00_Governance_and_Charter/00-07_*` |
| ERP Module Architecture & System Map | FIX-ERP2-003 | `1000fix_ERP_Module/02_Architecture/02-01_*` |
| Technology Stack & Build-vs-Buy Decisions | FIX-ERP2-019 | `1000fix_ERP_Module/02_Architecture/02-05_*` |
| **65 module specifications** | M01…M65 | `1000fix_ERP_Module/03_Modules/**/M*.md` |
| 11 category overviews | — | `1000fix_ERP_Module/03_Modules/*/_CATEGORY_OVERVIEW.md` |
| Portal Suite Specification (P01–P12) | FIX-ERP2-010 | `1000fix_ERP_Module/04_Portals_and_Applications/04-00_*` |
| Feature & Function Register | FIX-ERP2-011 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_*` |
| Data Model & Entity Catalogue | FIX-ERP2-012 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*` |
| Integration & API Catalogue | FIX-ERP2-013 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*` |
| Role, Permission & Access Matrix | FIX-ERP2-014 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_*` |
| Business Rules & Automation Catalogue | FIX-ERP2-015 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_*` |
| Non-Functional Requirements & Standards | FIX-ERP2-016 | `1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*` |
| Implementation Roadmap & Phasing | FIX-ERP2-017 | `1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_*` |
| KPI, Benefits & Acceptance Criteria | FIX-ERP2-018 | `1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_*` |
| ERP Comprehensive BRD v1.0 *(superseded)* | 1000FIX-ERP-BRD-2026-001 | `old-primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` |
| ERP Comprehensive RFP v1.0 *(superseded)* | 1000FIX-ERP-RFP-2026-001 | `old-primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` |

### Appendix E — Glossary

| Term | Definition |
|---|---|
| **1000FiX** | 1000FiX Services Limited, the issuing organisation |
| **AMC** | Annual Maintenance Contract |
| **API** | Application Programming Interface |
| **AR / AP** | Accounts Receivable / Accounts Payable |
| **ASM-nn** | Assumption identifier |
| **AUT-nnn** | Automation identifier |
| **BABOK® v3** | IIBA Business Analysis Body of Knowledge, version 3 — the methodology of this BRD |
| **BDT** | Bangladeshi Taka |
| **BEFTN** | Bangladesh Electronic Funds Transfer Network |
| **BIN** | Business Identification Number (VAT registration) |
| **BO-nn** | Business objective identifier |
| **BR / SR / FR / NFR / TR** | Business / Stakeholder / Functional / Non-Functional / Transition requirement |
| **BRU-nn** | Business rule identifier |
| **BST** | Bangladesh Standard Time (UTC+6) |
| **CAPA** | Corrective and Preventive Action |
| **CD-nnn** | Custom development deliverable identifier |
| **CDO** | Chief Data Officer — statutory role under PDPA 2026 |
| **CES** | Customer Effort Score |
| **CON-nn** | Constraint identifier |
| **CSAT** | Customer Satisfaction Score |
| **CWIP** | Capital Work In Progress |
| **D-nn** | Programme decision identifier |
| **DEP-nn** | Dependency identifier |
| **DoD-nn** | Definition-of-done criterion |
| **EaaS** | Equipment-as-a-Service |
| **ERP** | Enterprise Resource Planning |
| **ESG** | Environmental, Social and Governance |
| **FIFO** | First In, First Out (inventory valuation) |
| **FP&A** | Financial Planning and Analysis |
| **FTFR** | First-Time Fix Rate |
| **GL / GRN** | General Ledger / Goods Receipt Note |
| **HSE** | Health, Safety and Environment |
| **IMEI** | International Mobile Equipment Identity |
| **INT-nnn** | Integration identifier |
| **IoT** | Internet of Things |
| **ISO 9001:2015 / 27001 / 45001** | Quality / information security / occupational health and safety management standards |
| **KPI-nnn** | Key performance indicator identifier |
| **KYC** | Know Your Customer |
| **L1–L6** | Delivery layer — Odoo native / OCA / third-party / open source / custom / commercial |
| **LC** | Letter of Credit |
| **LLM** | Large Language Model |
| **MFA** | Multi-Factor Authentication |
| **Mnn** | ERP module identifier (M01–M67) |
| **MRR / ARR** | Monthly / Annual Recurring Revenue |
| **MSP** | Managed Service Provider |
| **Mushak 6.3 / 9.1** | Bangladesh VAT tax invoice form / monthly VAT return form |
| **NBR** | National Board of Revenue, Bangladesh |
| **NCR** | Non-Conformance Report |
| **NDMA** | National Data Management Authority — PDPA 2026 regulator |
| **NFR-nnn** | Non-functional requirement identifier |
| **NID** | National Identity (Bangladesh) |
| **NPS** | Net Promoter Score |
| **NTE** | Not-to-Exceed |
| **OCA** | Odoo Community Association |
| **P0–P3** | Priority level — blocking / must-have / important / desirable |
| **Pnn** | Portal identifier (P01–P12) |
| **PDPA 2026** | Personal Data Protection Act 2026 (Bangladesh, Law 63 of 2026) |
| **PF** | Provident Fund |
| **PM** | Preventive Maintenance |
| **PO / POD** | Purchase Order / Proof of Delivery |
| **PSA** | Professional Services Automation |
| **PW / PD** | Person-week / person-day |
| **PWA** | Progressive Web Application |
| **RACI** | Responsible, Accountable, Consulted, Informed |
| **RAMC** | Residential Annual Maintenance Contract |
| **RBAC** | Role-Based Access Control |
| **RFQ** | Request for Quotation |
| **RG-nn** | Register governance rule |
| **RMA** | Return Merchandise Authorisation |
| **RMM** | Remote Monitoring and Management |
| **Rnn** | User role identifier (R01–R46) |
| **RPO / RTO** | Recovery Point Objective / Recovery Time Objective |
| **RSK-nnn** | Risk identifier |
| **RTM** | Requirements Traceability Matrix |
| **RTV** | Return to Vendor |
| **S0–S3** | Data sensitivity classification — public / internal / confidential / restricted |
| **SLA** | Service Level Agreement |
| **SOD-nn** | Segregation-of-duties control identifier |
| **SOP** | Standard Operating Procedure |
| **T0–T5** | Data isolation tier |
| **TAT** | Turnaround Time |
| **TCO** | Total Cost of Ownership |
| **TDS / VDS** | Tax / VAT Deducted at Source |
| **TIN** | Taxpayer Identification Number |
| **UAT** | User Acceptance Testing |
| **VAT** | Value Added Tax |
| **Wn** | Delivery wave (W1–W9) |
| **WCAG 2.1 AA** | Web Content Accessibility Guidelines, level AA |
| **WIP** | Work In Progress |
| **3-way match** | Matching Purchase Order + Goods Receipt + Vendor Invoice before payment |

---

**END OF DOCUMENT**

---

*1000FiX Services Limited — Business Requirements Document*
*Version 2.0 | 13 August 2026 | CONFIDENTIAL — Internal Use Only*
*BRD Reference: 1000FIX-ERP-BRD-2026-002*
*Derived from RFP 1000FIX-ERP-RFP-2026-002*

*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: +880 9644-300600 | Email: info@1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
