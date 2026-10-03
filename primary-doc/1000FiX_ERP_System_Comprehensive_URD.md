---
id: 1000FIX-ERP-URD-2026-002
title: User Requirements Document — Enterprise Resource Planning System & Digital Platform Suite (v2.0 Expanded Scope)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
supersedes: 1000FIX-ERP-URD-2026-001 (v1.0, 18 March 2026)
derived_from: 1000FIX-ERP-RFP-2026-002 (RFP v2.0, 13 August 2026)
companion: 1000FIX-ERP-BRD-2026-002 (BRD v2.0, 13 August 2026)
owner: Chief Technology Officer, 1000FiX Services Limited
---

# USER REQUIREMENTS DOCUMENT (URD)

# Enterprise Resource Planning System & Digital Platform Suite

# 46 Roles · 36 Personas · 12 Portals · 255 User Stories · 15 Journeys

## 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | User Requirements Document — ERP System & Digital Platform Suite (v2.0 Expanded Scope) |
| **Issuing Organisation** | 1000FiX Services Limited |
| **Document Version** | 2.0 |
| **Date** | 13 August 2026 |
| **URD Reference Number** | 1000FIX-ERP-URD-2026-002 |
| **Supersedes** | 1000FIX-ERP-URD-2026-001 (v1.0, 18 March 2026) |
| **Governing Document** | **1000FIX-ERP-RFP-2026-002** — Request for Proposal v2.0 |
| **Companion Document** | **1000FIX-ERP-BRD-2026-002** — Business Requirements Document v2.0 |
| **Document Owner** | Chief Technology Officer |
| **Prepared By** | Business Analysis Team, 1000FiX Services Limited |
| **Methodology** | IIBA BABOK® v3 · INVEST user-story criteria · WCAG 2.2 AA accessibility personas |
| **Classification** | CONFIDENTIAL — Internal Use Only |

---

**CONFIDENTIALITY NOTICE**

This User Requirements Document is the confidential property of 1000FiX Services Limited. It is
intended solely for use by 1000FiX internal stakeholders and by the implementation partner selected
under RFP 1000FIX-ERP-RFP-2026-002. It must not be disclosed to third parties without prior written
consent.

---

## DOCUMENT AUTHORITY AND PRECEDENCE

**This URD is derived in full from RFP v2.0.** Every role, portal, wave, business rule, target and
constraint referenced here traces to that RFP and, through it, to the module specification set held
in `1000fix_ERP_Module/`.

```
RFP v2.0 (1000FIX-ERP-RFP-2026-002)          ← "What we are buying and on what terms"
  ├─ BRD v2.0 (1000FIX-ERP-BRD-2026-002)     ← "What the business needs and why"
  └─ URD v2.0 (1000FIX-ERP-URD-2026-002)     ← "What users need to do their jobs"  ◄ THIS DOCUMENT
       └─ SRS / module specifications         ← "How the system will be built"
```

| Precedence | Document | Governs |
|---|---|---|
| **1** | `02-02_Module_Catalogue_Master_Register.md` | Module identity, code, category, ownership, priority, wave |
| **2** | Module specification files (`03_Modules/**/M*.md`) | Functional and technical requirement detail |
| **3** | Cross-cutting specifications (`05-01` … `05-06`) | Requirements register, data model, integrations, roles, business rules, NFRs |
| **4** | **RFP v2.0** | Commercial terms, procurement, evaluation, contractual obligations |
| **5** | **BRD v2.0** | Business rationale, objectives, process design, benefit case |
| **6** | **This URD** | User needs, personas, stories, journeys, usability, adoption, user acceptance |

Where this URD and the RFP disagree on a **commercial** term, the RFP prevails. Where this URD and
the module specifications disagree on a **functional** requirement, the specifications prevail. Any
discrepancy must be raised as a change request.

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Description |
|---|---|---|---|
| 0.1 | 10 March 2026 | BA Team | Initial draft — sections 1–4 |
| 0.5 | 14 March 2026 | BA Team | Added sections 5–10 (user stories) |
| 0.9 | 16 March 2026 | BA Team | Added sections 11–18 |
| 1.0 | 18 March 2026 | BA Team | Final v1.0 — 20 personas, 68 user stories, 12 journeys, 6 portals, 20 roles |
| **2.0** | **13 August 2026** | **BA Team / CTO** | **Complete re-baseline against RFP v2.0. Personas expanded 20 → 36 covering all 46 roles. User stories expanded 68 → 255 across 11 module categories and 12 portals. Journeys expanded 12 → 15, aligned to the programme's 15 critical business journeys. Portals 6 → 12. Roles 20 → 46. New user constituencies added: MSP engineers, data-services technicians, riders, marketplace sellers, brand partners, contact-centre agents, field auditors, referral partners, payroll and HSE officers, data stewards, the Chief Data Officer and the PDPA data subject. Offline conflict-resolution UX specified. Accessibility target reviewed against WCAG 2.2. Adoption plan restated across 9 waves.** |

---

## DOCUMENT APPROVALS

| Role | Name | Decision | Signature | Date |
|---|---|---|---|---|
| Chief Executive Officer (Sponsor) | | Approve / Approve with conditions / Reject | | |
| Chief Technology Officer | | | | |
| Service Operations Director | | | | |
| Chief Commercial Officer | | | | |
| Chief Financial Officer | | | | |
| HR Director | | | | |
| Quality Manager | | | | |
| Customer Service Manager | | | | |
| Lead Business Analyst | | | | |
| Implementation Partner — UX Lead | | | | |

---

## HOW THIS DOCUMENT DIFFERS FROM VERSION 1.0

| Dimension | URD v1.0 (Mar 2026) | **URD v2.0 (Aug 2026)** | Change |
|---|---|---|---|
| User roles covered | 20 | **46** *(38 registered + 8 pending formalisation)* | +26 |
| Personas | 20 | **36** | +16 |
| User stories | 68 | **255** | +187 |
| Journey maps | 12 | **15** *(the programme's critical journeys)* | +3, fully re-scoped |
| Portals | 6 | **12** | +6 |
| Modules referenced | 11 | **67 in 11 categories** | +56 |
| New user constituencies | — | **MSP engineer · data-services technician · rider · marketplace seller · brand partner · contact-centre agent · field auditor · referral partner · payroll officer · HSE officer · data steward · Chief Data Officer · PDPA data subject** | 13 new |
| Offline requirement | "24 hours, sync on reconnect" | **24 h + 30 s sync + explicit conflict-resolution UX + conflict visibility to the user** | Materially deeper |
| Accessibility target | WCAG 2.1 AA | **WCAG 2.1 AA (contracted) — 2.2 AA recommended, see §21.4** | Under review |
| Adoption model | 6 phases | **9 waves with per-wave adoption gates** | Restated |
| Language position | "Bengali and English" | **Bengali-first on all customer and field surfaces; machine translation not acceptable for release** | Hardened |

**No v1.0 user story has been deleted.** Every v1.0 story is carried into the v2.0 register, renumbered
where a module split; the mapping is at §26.2.

---

## TABLE OF CONTENTS

**Part A — Who**
1. [Introduction & Purpose](#1-introduction--purpose)
2. [Executive Summary — The User Experience Vision](#2-executive-summary--the-user-experience-vision)
3. [User Personas](#3-user-personas)
4. [User Roles & Access Matrix](#4-user-roles--access-matrix)
5. [User Goals & Needs](#5-user-goals--needs)

**Part B — What Users Need The System To Do**
6. [User Stories — Category A: Service Delivery & Operations](#6-user-stories--category-a-service-delivery--operations)
7. [User Stories — Category B: Customer Engagement & Experience](#7-user-stories--category-b-customer-engagement--experience)
8. [User Stories — Category C: Commercial, Pricing & Revenue](#8-user-stories--category-c-commercial-pricing--revenue)
9. [User Stories — Category D: Circular & Asset-Based Business](#9-user-stories--category-d-circular--asset-based-business)
10. [User Stories — Category E: Supply Chain & Inventory](#10-user-stories--category-e-supply-chain--inventory)
11. [User Stories — Category F: Asset, Equipment & Facilities](#11-user-stories--category-f-asset-equipment--facilities)
12. [User Stories — Category G: Finance & Treasury](#12-user-stories--category-g-finance--treasury)
13. [User Stories — Category H: People & Workforce](#13-user-stories--category-h-people--workforce)
14. [User Stories — Category I: Governance, Risk, Quality & Knowledge](#14-user-stories--category-i-governance-risk-quality--knowledge)
15. [User Stories — Category J: Data, Analytics & Intelligence](#15-user-stories--category-j-data-analytics--intelligence)
16. [User Stories — Category K: Platform & Technology](#16-user-stories--category-k-platform--technology)
17. [User Stories — The Twelve Portals](#17-user-stories--the-twelve-portals)

**Part C — How It Must Feel**
18. [User Journey Maps](#18-user-journey-maps)
19. [Usability Requirements](#19-usability-requirements)
20. [Offline & Low-Connectivity User Experience](#20-offline--low-connectivity-user-experience)
21. [Accessibility & Inclusive Design](#21-accessibility--inclusive-design)
22. [Localisation & Bangladesh-Specific Requirements](#22-localisation--bangladesh-specific-requirements)
23. [Notification & Communication Requirements](#23-notification--communication-requirements)

**Part D — How Users Get There**
24. [Transition Requirements & User Adoption](#24-transition-requirements--user-adoption)
25. [User Acceptance Criteria](#25-user-acceptance-criteria)
26. [Assumptions, Constraints & Disclosed Open Items](#26-assumptions-constraints--disclosed-open-items)
27. [Appendices](#27-appendices)

---
---

# PART A — WHO

---

## 1. INTRODUCTION & PURPOSE

### 1.1 Purpose

This URD defines the needs, goals, working conditions and expectations of every person who will
interact with the 1000FiX ERP System and its twelve-portal digital platform suite. It translates
the business requirements of BRD v2.0 into **user-centric stories, journeys, interaction
requirements, usability criteria and acceptance tests** that will govern UX design, system
configuration, training and user acceptance testing across a 36-month, nine-wave programme.

### 1.2 Scope

| Dimension | Coverage |
|---|---|
| **User roles** | **46** — 38 registered (R01–R38) plus 8 in active use pending formalisation (R39–R46) |
| **Personas** | **36**, mapped to all 46 roles |
| **Internal users** | 500–900 across 51+ locations in all 8 divisions |
| **External users** | 250,000+ customers/month · 500–2,000 corporate portal users · 1,000–3,000 external parties |
| **ERP modules** | **67** across 11 categories |
| **Portals & applications** | **12** (P01–P12) |
| **User stories** | **255**, each traced to a role, a module, a wave and a business objective |
| **Journeys** | **15** — the programme's critical end-to-end business journeys |
| **Delivery horizon** | 9 waves over 36 months, each with a user-adoption gate |

### 1.3 Intended Audience

| Audience | How to use this document |
|---|---|
| UX / UI designers | Personas (§3), journeys (§18), usability (§19), offline UX (§20), accessibility (§21) |
| Implementation partner — configurators and developers | User stories (§6–§17), access matrix (§4) |
| Programme manager / PMO | Adoption plan (§24), acceptance criteria (§25) |
| QA / test engineers | Acceptance criteria on every story; UAT criteria (§25) |
| Training and change team | Personas (§3), transition requirements (§24) |
| Business owners | Goals and needs (§5), journeys (§18), acceptance criteria (§25) |
| Steering Committee | Executive summary (§2), adoption risk (§24.6), open items (§26.3) |

### 1.4 How to Read a User Story in This Document

```
US-<CODE>-nnn | Role | Priority | Wave | Module | Business objective
"As a [role], I want to [action], so that [benefit]."
AC: numbered, testable acceptance criteria
```

Stories follow **INVEST** — Independent, Negotiable, Valuable, Estimable, Small, Testable. Every
story carries at least one testable acceptance criterion; **no story enters a sprint without one**
(BRD §24 traceability governance).

| Element | Meaning |
|---|---|
| `US-<CODE>-nnn` | Story identifier; `<CODE>` is the owning module's permanent code |
| Priority | **P0** blocking · **P1** must-have · **P2** important · **P3** desirable |
| Wave | W1–W9 — when the user first gets this capability |
| Module | The owning ERP module (M01–M67) |
| BO | The business objective the story serves (BO-01…BO-18) |

### 1.5 Definitions

| Term | Definition |
|---|---|
| **User story** | A user-centric requirement unit: "As a [role], I want [action], so that [benefit]" |
| **Persona** | A representative user profile built from role analysis and field observation |
| **Journey map** | Step-by-step narrative of a user completing a key task end to end |
| **AC** | Acceptance criteria — testable conditions confirming a story is complete |
| **INVEST** | Story quality test: Independent, Negotiable, Valuable, Estimable, Small, Testable |
| **SUS** | System Usability Scale — standardised 0–100 usability score |
| **Offline-first** | The device holds the work; the technician completes it connected or not; the platform reconciles on next sync |
| **Conflict** | Two changes to the same record made independently, requiring resolution on sync |
| **Data subject** | An individual whose personal data the Company processes — a user class with statutory rights under PDPA 2026 |
| **P0–P3** | Priority: blocking / must-have / important / desirable |
| **W1–W9** | Delivery wave across the 36-month programme |
| **BDT / NBR / NID / BIN** | Bangladeshi Taka / National Board of Revenue / National Identity Document / Business Identification Number |

---

## 2. EXECUTIVE SUMMARY — THE USER EXPERIENCE VISION

### 2.1 The Shift, By User Group

| User group | Today | With the v2.0 platform |
|---|---|---|
| **Customers** | Call the hotline three times to learn a status; paper invoice; no idea of cost before work starts | Book in ≤ 3 steps in Bengali; live technician map with ETA; approve the estimate on screen; pay by bKash; digital invoice; **a public tracking link that needs no login** |
| **Field technicians** | Paper job cards, WhatsApp assignments, 15 minutes of forms per job, wasted trips for parts | A Bengali-first app with the day's optimised route, device history, guided diagnosis, van stock, e-signature and payment — **working for 24 hours with no signal** |
| **Workshop technicians** | Whiteboard and paper job cards; devices lost on the bench | A bench board with WIP, repair-level routing, parts holds and test evidence |
| **Service centre agents** | Four separate systems per customer; 10-minute intake; warranty checked by phoning the brand | One screen: party, device, history, entitlement, price — **intake in under 3 minutes** |
| **Dispatchers** | 45 minutes of morning phone calls; no map; SLA breaches discovered by customer complaint | Candidates scored on skill, certification, location, workload and van stock; auto-assign above confidence; **full morning queue dispatched in under 10 minutes** |
| **Riders & logistics** | Phone-coordinated pick & drop; no custody evidence; disputes unresolvable | Manifest, scan, photo, seal, OTP and signature at every handover — **zero custody breaks**, fully offline |
| **Contact centre agents** ★ | The hotline leaves no record; agents alt-tab between systems | One queue across voice, chat, WhatsApp, email, SMS and social; **Customer 360 screen-pop**; any action without leaving the conversation |
| **Remote support / MSP engineers** ★ | Ad-hoc tools; no session record; SLA unmeasurable | Estate health, correlated alerts, ticketing against contract SLA, remote sessions with consent capture, per-client reporting |
| **Data-services technicians** ★ | Job cards in a drawer for the Company's most sensitive work | Dual-control custody, per-case encryption, logged access, certified destruction with a defensible certificate |
| **Inventory & warehouse** | Branch spreadsheets; stockouts found at the counter; van stock untracked | One network stock view including every van; replenishment that drafts itself; scan-based movements |
| **Finance officers** | 100 invoices typed by hand; Mushak in a separate Excel; cash reports by WhatsApp photo | Invoice within 5 seconds of job closure, Mushak-compliant; 90%+ payment auto-match; **month-end in ≤ 3 days** |
| **Warranty claims officers** | Claims prepared manually, 30–90 days late, 15–20% never recovered | Claim created within 24 hours with the evidence pack assembled and validated; submitted within 72 hours |
| **Payroll & HR** ★ | 500 salaries calculated in Excel over 3 days; certification lapses found by claim rejection | Payroll in under 4 hours with Bangladesh tax, PF, gratuity and BEFTN; **certification expiry blocks dispatch automatically** |
| **Quality & field auditors** ★ | Paper ISO records assembled for audit | Audits completed offline on mobile with photo evidence; CAPA verified, not just closed |
| **Marketplace sellers** ★ | Do not exist as a user class | Register with KYC, list, bid, execute to the same standard as owned work, and be paid transparently |
| **Brand partners** ★ | Claims by email with evidence in separate attachments | A portal with complete evidence packs, decisions, reconciliation and their own service-quality view |
| **Corporate clients** | Phone and email per device; separate invoices per site | Asset estate management, bulk CSV requests validated against coverage, SLA and service credits, one consolidated invoice |
| **Branch & operations managers** | Excel compiled from three sources, two hours a week | Live branch console; league tables across 51+ branches; approvals from a phone |
| **Executives** | Wait 10+ days for a monthly pack | Live dashboards across all 14 revenue streams, drilling from group revenue to a single job |
| **Data subjects** ★ | No route to exercise rights | Access, portability, rectification, erasure and consent withdrawal through a defined, evidenced process |

★ = user constituency that does not exist in the v1.0 plan.

### 2.2 The Seven Non-Negotiable User Commitments

These are the promises the platform makes to its users. Each is measurable and each is a wave-gate
criterion.

| # | Commitment | Measure |
|---|---|---|
| **1** | **A technician can do a full day's work with no signal** | 24 h offline, sync in ≤ 30 s on 3G, **zero data loss**, zero sync failures |
| **2** | **A walk-in customer is served in under three minutes** | Timed observation, 20 samples, by branch staff — not by the project team |
| **3** | **Every screen a field or customer user touches is in Bengali** | 100% translation coverage, professionally translated; **machine translation is not acceptable for release** |
| **4** | **A customer never has to call to find out what is happening** | > 80% of status enquiries self-served; notifications at every milestone |
| **5** | **No user is asked to enter the same thing twice** | Party, device, entitlement and price resolved once and carried through |
| **6** | **The system tells the user what happened and what to do next** | Every error message states the cause and the next action, in the user's language |
| **7** | **The app works on the phone the technician actually has** | Mid-range Android 11, 3 GB RAM, ≤ 12% battery per 8-hour shift |

### 2.3 User Adoption Success Criteria

| Criterion | Target | Measured |
|---|---|---|
| Technician app daily active usage | **≥ 95%** of active technicians | Daily, from W2 |
| Jobs documented in-app rather than on paper | **100%** in Dhaka by Gate 2 | Gate 2 |
| Service centre agents working in the ERP | **100%** of intake | Gate 1 |
| Customers self-booking online | 60% at pilot (Gate 2) → **88%** (W8) | Continuous |
| Corporate clients active on the B2B portal | **> 85%** of contracted clients | From W4 |
| Brand partner claims via portal rather than email | **> 80%** | From W4 |
| Vendors acknowledging POs via portal | **> 90%** | From W3 |
| Marketplace sellers monthly active | **> 70%** of approved | From W7 |
| System Usability Scale, all internal roles | **≥ 75** | Post-training, each wave |
| Critical usability defects at UAT sign-off | **Zero** | Every wave gate |
| Manual management reporting packs remaining | **Zero** | Gate 8 |

### 2.4 The Single Largest User Risk

> **RSK-008 — technician rejection of the mobile app. Rated Critical.**
>
> Four hundred people in the field decide whether this programme works. **If the app is slower than
> paper, they will not use it** — and dispatch, inventory, invoicing, warranty and quality all
> degrade behind them. Industry analysis of field-service deployments consistently finds adoption,
> not capability, to be the failure mode.
>
> This URD's response: Bengali-first design; one-handed thumb-reach layouts; only the fields needed
> for the task in front of the technician; a field pilot with respected senior technicians **before**
> rollout; Company-provided devices; **earnings and incentive visibility as an immediate personal
> benefit**; a champion in every branch; and a simplified "lite" mode held as contingency.

---

## 3. USER PERSONAS

> Each persona records: role and role ID, population, location, tech literacy (1–5), language,
> device, working conditions, daily responsibilities, goals, pain points, what success looks like,
> and the modules and portals they touch. **★ marks a persona that does not exist in the v1.0 plan.**

### 3.1 Persona Index

| # | Persona | Role ID(s) | Population | Wave first served | Primary surface |
|---|---|---|---:|:--:|---|
| P-01 | Service Centre Agent | R08 | 150–250 | W1 | P03 |
| P-02 | Dispatch Manager | R07 | 3–8 | W2 | P03 |
| P-03 | Senior Field Technician | R10 | 80–150 | W2 | P02 |
| P-04 | Junior Field Technician | R11 | 120–250 | W2 | P02 |
| P-05 | Specialist (L3) Technician | R12 | 15–30 | W2 | P02, P03 |
| P-06 | Workshop Supervisor | R09 | 20–40 | W2 | P03 |
| P-07 | Branch Manager | R06 | 51+ | W1 | P03, P06, P11 |
| P-08 | Operations Director | R05 | 1–2 | W1 | P03, P06 |
| P-09 | Logistics Coordinator ★ | R15 | 10–25 | W3 | P03, P09 |
| P-10 | Rider / Delivery Agent ★ | R16 | 50–150 | W3 | P09 |
| P-11 | Remote Support / MSP Engineer ★ | R13 | 15–40 | W5 | P03, P10 |
| P-12 | Data Services Technician ★ | R14 | 5–12 | W6 | P03 |
| P-13 | Inventory Manager | R17 | 5–10 | W2 | P03, P06 |
| P-14 | Branch Store Keeper / Warehouse Operative | R18, R20 | 66–81 | W2 | P03 |
| P-15 | Procurement Officer | R19 | 4–8 | W3 | P03, P05 |
| P-16 | Account Manager (Corporate) | R22 | 8–20 | W4 | P03, P04, P06 |
| P-17 | Sales Manager | R21 | 3–6 | W3 | P03, P06 |
| P-18 | Marketing Manager | R23 | 2–4 | W5 | P03, P06, P12 |
| P-19 | Marketplace Operations Officer ★ | R24 | 4–10 | W7 | P03 |
| P-20 | Retail / Refurbishment Officer ★ | R25 | 5–15 | W6 | P03 |
| P-21 | Finance Officer & Cashier | R27, R29 | 61–71 | W3 | P03 |
| P-22 | Finance Manager | R26 | 2–4 | W3 | P03, P05, P06, P08 |
| P-23 | Warranty Claims Officer | R28 | 4–10 | W4 | P03, P06, P08 |
| P-24 | Payroll Officer ★ | R41 | 1–3 | W5 | P03 |
| P-25 | HR Officer | R31 | 3–6 | W5 | P03 |
| P-26 | HR Manager | R30 | 1–2 | W5 | P03, P06 |
| P-27 | Training Coordinator & Competency Assessor ★ | R42, R43 | 3–6 | W5 | P03 |
| P-28 | HSE Officer ★ | R44 | 1–3 | W6 | P03, P02 |
| P-29 | Quality Manager / Field Auditor | R32 | 2–4 | W5 | P03, P06, P11 |
| P-30 | Contact Centre Agent & Supervisor ★ | R34, R35 | 34–70 | W4 | P10 |
| P-31 | IT Administrator | R33 | 4–8 | W1 | P03 |
| P-32 | Data Steward & Chief Data Officer ★ | R39, R40 | 2–4 | W1 / W4 | P03 |
| P-33 | Executive (CEO / CTO / CFO / CCO) | R01–R04 | 4 | W1 | P03, P06 |
| P-34 | Customer — three archetypes | R36 | 250,000+/mo | W2 | P01 |
| P-35 | Corporate Portal User | R37 | 500–2,000 | W4 | P04 |
| P-36 | External Party — five archetypes ★ | R38 | 1,000–3,000 | W3–W7 | P05, P07, P08, P09, P12 |

**Coverage check:** all 46 roles (R01–R46) are represented. Roles R45 (Recruiter) and R46
(Occupational Health) are covered within P-27 and P-28 respectively; R38 covers vendor, marketplace
seller, brand partner, courier and referral partner archetypes in P-36.

---

### P-01 — Service Centre Agent  ·  R08

**Rashida Begum**, 26 · Mirpur Branch, Dhaka · Tech literacy **3/5** · **Bengali primary**, limited
English · Windows desktop at the counter, 1366×768 · Standing, queue behind her, phone ringing

**Daily work:** receives walk-in customers and registers service requests · answers the hotline and
creates phone-in orders · takes device custody and prints job tokens · updates status through the
day · takes payment on collection · books pick & drop · sells warranty products and Privilege
membership at the counter.

**Goals**
- Get the customer served and out of the queue — **intake under 3 minutes**
- One screen with the customer, their devices, their history and their entitlement
- Know warranty status instantly, without phoning the brand
- Print a legible job token and job card, every time

**Pain points today:** four separate apps or spreadsheets per customer · warranty status requires a
5–10 minute call to a brand hotline · handwritten job cards lost or misread · cannot give the
customer an honest completion date.

> *"আমি চাই একটাই সিস্টেমে সব কাজ করতে পারব। এখন অনেক জায়গায় দেখতে হয়।"*
> ("I want to do everything in one system. Right now I have to look in many places.")

**Success looks like:** the queue moves; she never re-types anything the system already knows; she
can answer "when will it be ready?" truthfully.
**Modules:** M04, M01, M33, M17, M09, M11, M20, M10 · **Portal:** P03 (Service Intake workspace)

---

### P-02 — Dispatch Manager  ·  R07

**Farida Rahman**, 32 · Corporate HQ, Dhaka · Tech literacy **4/5** · Bengali and English ·
Dual-monitor desktop + Android phone · Monitoring 15–30 technicians simultaneously

**Daily work:** assigns the morning queue · re-assigns in real time when technicians run late ·
watches the live map · handles escalations · manages the standby rota · answers "where is my
technician?" from three directions at once.

**Goals**
- **Dispatch the morning queue in under 10 minutes** (45 today)
- See every technician's position, load and SLA risk on one screen
- Be warned *before* an SLA breaches, not after the customer calls
- Understand *why* the system recommended a technician — in plain language

**Pain points today:** no map — she phones technicians individually · re-assignment means a
spreadsheet edit then a phone call · no automatic SLA warning · certification data not visible at
the moment of assignment.

> *"If I could see all my technicians on a map with their current jobs, I could manage three times
> the volume with the same team."*

**Success looks like:** the system does the routine assignment; she handles the exceptions; nothing
breaches without her knowing first.
**Modules:** M02, M01, M22, M27, M15 · **Portal:** P03 (Dispatch Console), P06

---

### P-03 — Senior Field Technician  ·  R10

**Kabir Hossain**, 40 · Field, Dhaka North zone · Tech literacy **3/5** · **Bengali only** ·
Company-issued Android 11, 3 GB RAM · **Works one-handed** — the other hand holds a tool, a part or
the customer's device · Sunlight, rain, stairwells, basements with no signal

**Daily work:** 6–8 field jobs · diagnoses and repairs AC units, laptops and printers on site ·
documents diagnosis, parts and work done · takes customer signature and payment · requests parts he
is not carrying · mentors juniors.

**Goals**
- Know the full day, with locations, **before he leaves home**
- See the device's history and previous notes *before he arrives*
- Finish documentation in under 5 minutes, not 15
- Stop making unplanned trips back for parts
- **See his earnings and incentive as he earns them**

**Pain points today:** jobs arrive in a WhatsApp group and are easy to miss · no offline access —
he loses productivity in weak-signal areas · paper forms illegible or lost, so he asks the customer
the same questions again next visit · 30% of jobs need an unplanned parts trip.

> *"আমি যদি আগে থেকে জানতাম কোন জব-এ কী পার্টস লাগবে, অনেক সময় বাঁচত।"*
> ("If I knew in advance what parts each job needs, I'd save a lot of time.")

**Success looks like:** he does more jobs, in less time, with fewer return visits, and can see what
he earned today.
**Modules:** M01, M02, M03, M15, M17, M22, M57, M59, M61 · **Portal:** P02

> **This persona is the programme's highest adoption risk (RSK-008).** Every design decision on P02
> is made against Kabir.

---

### P-04 — Junior Field Technician  ·  R11

**Shakib Islam**, 24 · Field, Chittagong · Tech literacy **3/5** · **Bengali only** ·
Company-issued Android · Often alone at a customer's home, under time pressure

**Daily work:** 4–6 jobs under senior supervision · mobile and tablet repairs at customer premises ·
follows diagnostic checklists · documents work and collects feedback.

**Goals**
- A **guided, step-by-step checklist** for anything unfamiliar
- Escalate to a senior **without embarrassing himself in front of the customer**
- Build a visible performance record so he can advance
- Know what to carry tomorrow

**Pain points today:** no guided workflow, so he makes errors under pressure · escalation means
phoning the supervisor and explaining from scratch, in front of the customer · cannot see his own
metrics or targets · unsure which parts to stock in his kit.

> *"I want a checklist in the app that tells me step by step what to check. When I'm nervous at the
> customer's house, I forget things."*

**Success looks like:** he is never stuck without a next step; escalation is one tap and carries the
context for him.
**Modules:** M01, M02, M15, M22, M61 · **Portal:** P02

---

### P-05 — Specialist (L3) Technician  ·  R12

**Mizanur Rahman**, 36 · Central workshop, Dhaka · Tech literacy **4/5** · Bengali and technical
English · Bench workstation + Android · Microscope, hot-air station, ESD mat

**Daily work:** board-level and component repair · handles what Levels 1 and 2 could not · test and
burn-in · sets repair standards for others · verifies beyond-economic-repair declarations.

**Goals**
- The full diagnostic history from the L1/L2 attempts **before** he opens the device
- Wiring diagrams and board schematics **searchable and offline**
- Record component-level work so the next specialist benefits
- Only be sent work that genuinely needs him

**Pain points today:** receives devices with no record of what was already tried · schematics live
on personal drives and shared chat groups · no way to capture what he learned.

**Success looks like:** L3 routing is accurate; nothing arrives at his bench twice.
**Modules:** M31, M01, M15, M45, M61 · **Portal:** P02 (workshop mode), P03

---

### P-06 — Workshop Supervisor  ·  R09

**Nurul Amin**, 34 · Workshop, Dhaka · Tech literacy **3/5** · Bengali · Desktop + tablet on the
floor · Manages 8–15 benches

**Daily work:** assigns work to benches · manages WIP and ageing · chases parts holds · balances
load across repair levels · signs off quality before handover.

**Goals**
- One board showing every device on every bench and how long it has been there
- See what is blocked, and on what
- Move work between benches without paperwork
- **Never lose a device on the bench again**

**Pain points today:** whiteboards and paper job cards · no WIP ageing · parts holds discovered when
the customer chases · bench utilisation unknown.

**Success looks like:** WIP ageing visible at a glance; zero devices uncollected or unaccounted.
**Modules:** M31, M01, M15, M23 · **Portal:** P03 (Workshop Console)

---

### P-07 — Branch Manager  ·  R06

**Arif Chowdhury**, 38 · Sylhet Service Centre · Tech literacy **3/5** · Bengali primary, English
for reports · Desktop at branch, Android phone · Frequently away from his desk

**Daily work:** runs a service centre of 20–40 staff · reviews completion and revenue daily ·
approves requisitions, discounts and estimates above threshold · weekly team performance reviews ·
branch cash · handles escalated complaints · owns branch SLA compliance.

**Goals**
- Today's branch numbers on one screen, without running a report
- Know which technicians are struggling **before** the weekly review
- **Approve from his phone**, in three taps, wherever he is
- Be told immediately when a complaint escalates
- Compare his branch to the network

**Pain points today:** compiles performance from three sources, 2+ hours a week · approvals wait
until he is at his desk · complaint history scattered · no benchmark.

> *"আমার ব্রাঞ্চের সব ডেটা এক জায়গায় দেখতে চাই — কতটা কাজ হলো, কতটা টাকা এলো, কারা ভালো করছে।"*

**Success looks like:** he manages by exception, from anywhere.
**Modules:** M04, M01, M02, M15, M50, M25, M23 · **Portal:** P03 (Branch Console), P06, P11

---

### P-08 — Operations Director  ·  R05

**Nasreen Sultana**, 42 · Dhaka HQ · Tech literacy **4/5** · Bengali and English · Laptop, large
desktop, smartphone

**Daily work:** operations across all 51+ centres · network KPIs — completion, CSAT, SLA, technician
productivity · intervenes where branches underperform · owns the service standard · reports to the
CEO weekly.

**Goals**
- Network view of jobs, revenue and SLA **in real time**
- Drill from network to branch to technician to a single job
- Set and monitor KPI targets by branch and region
- Spot seasonal demand and plan capacity

**Pain points today:** aggregates Excel from 51 branch managers — a full day · no consistent format ·
learns of a branch problem only when it is a crisis.

> *"I need to spot a problem branch at 9 AM on a Monday, not two weeks later when I finally compile
> the reports."*

**Success looks like:** she intervenes on Monday morning, not month-end.
**Modules:** M01, M02, M25, M62, M23 · **Portal:** P03, P06

---

### P-09 — Logistics Coordinator ★  ·  R15

**Shahin Alam**, 30 · Dhaka central logistics · Tech literacy **3/5** · Bengali · Desktop + Android ·
Coordinating 20–40 movements a day across riders and courier partners

**Daily work:** plans pickups and deliveries · assigns to internal riders or courier partners ·
tracks consignments in transit · handles exceptions — customer absent, wrong address, refused,
damaged · reschedules · reconciles cash on delivery · manages loss and damage claims.

**Goals**
- One dashboard: pending, in transit, delivered, exception
- Assign to a rider or a courier from the same screen
- **Know exactly who had the device, when, and where** — for every leg
- Reschedule without a phone call

**Pain points today:** pick & drop is coordinated by phone · no chain of custody, so a dispute
cannot be settled · no proof of collection or delivery · courier status arrives by WhatsApp.

**Success looks like:** **zero custody breaks**; every dispute settled from the record.
**Modules:** M03, M01, M13, M14, M18, M15 · **Portal:** P03, P09 (coordinator view)

---

### P-10 — Rider / Delivery Agent ★  ·  R16

**Jasim Uddin**, 27 · Dhaka streets · Tech literacy **2/5** · **Bengali only** · Company Android on
a handlebar mount · Riding a motorcycle in traffic, rain and heat; helmet on; often one-handed

**Daily work:** works a daily manifest of collections and deliveries · scans consignments · verifies
items against the manifest · photographs items and packaging · records seal numbers · captures
customer OTP and signature · collects cash on delivery · reconciles at shift end.

**Goals**
- A manifest that tells him where to go next, in order
- Capture proof **fast** — the customer is waiting at the door
- Work in areas with no signal and not lose anything
- Reconcile his cash in one screen at the end of the shift

**Pain points today:** paper manifest · no proof of handover · blamed for losses he cannot disprove ·
cash reconciliation is a nightly argument.

> *"আমার কাছে প্রমাণ থাকতে হবে যে আমি জিনিসটা দিয়েছি।"*
> ("I need proof that I handed the item over.")

**Success looks like:** POD capture complete on every single leg; **he is never blamed without
evidence**.
**Modules:** M03, M13, M14, M15 · **Portal:** P09

> **Design constraint:** helmet, gloves, one hand, direct sunlight. Large targets, high contrast,
> minimum taps, no free typing where a scan or a tap will do.

---

### P-11 — Remote Support / MSP Engineer ★  ·  R13

**Sabbir Ahmed**, 31 · Dhaka HQ MSP desk · Tech literacy **5/5** · English and Bengali · Dual monitors ·
On a rota including nights — MSP contracts require 24×7

**Daily work:** monitors client estates · triages correlated alerts · runs remote sessions with
consent · patches and remediates · manages MSP tickets against contract SLA · escalates to field
dispatch when remote fails · produces monthly client service reports.

**Goals**
- **Alert noise low enough that alerts still mean something**
- One click from an alert to the asset, its history and its contract entitlement
- Launch a remote session with consent captured automatically
- See SLA burn-down per ticket, per client
- Show the client what he did, in a report he does not have to write by hand

**Pain points today:** ad-hoc tools with no session record · no contract linkage, so SLA is
unmeasurable and credits are argued after the fact · monthly reports built by hand.

**Success looks like:** **65% of incidents resolved remotely**, 98% SLA attainment, reports generated.
**Modules:** M05, M08, M17, M48, M27, M01 · **Portal:** P03 (Managed Services Console), P10

---

### P-12 — Data Services Technician ★  ·  R14

**Farhana Yasmin**, 33 · Secure data lab, Dhaka · Tech literacy **5/5** · English and Bengali ·
Isolated workstation, no general network · **Works under dual control; every action logged**

**Daily work:** takes custody of customer media · attempts recovery · books cleanroom time · refers
beyond-capability cases to a partner lab · indexes recovered data · hands back to the customer with
verification · **executes certified destruction** and issues certificates · purges recovered data
at the agreed date.

**Goals**
- Custody that is **unambiguous and provable at every transfer**
- Access restricted to her assigned cases only — and to see that enforced, not promised
- A destruction certificate a corporate client's security team will accept
- Never be the reason customer data leaks

**Pain points today:** job cards in a drawer for the Company's most sensitive work · no custody
record · no access control · certificates that cite no approved standard.

> *"If a customer's data leaves this room, the Company is finished. I need the system to make that
> impossible, not just against the rules."*

**Success looks like:** **zero custody exceptions**; every certificate defensible under audit.
**Modules:** M06, M24, M29, M14, M18 · **Portal:** P03 (restricted)

> **Design constraint:** this persona works with **S3 restricted data under Bangladesh-resident
> storage (NFR-086)**. Step-up authentication, dual control, per-case encryption keys and full
> access logging are user-visible parts of her workflow, not background controls.

---

### P-13 — Inventory Manager  ·  R17

**Jahangir Hossain**, 44 · Central warehouse, Dhaka · Tech literacy **3/5** · Bengali · Desktop +
Android tablet on the floor

**Daily work:** stock across the central warehouse, regional hubs, 51+ branches **and 200–400
technician vans** · goods receipt and issue · reorder monitoring · inter-branch transfers · cycle
counts · dead stock · brand consignment stock kept separate from own stock.

**Goals**
- Real-time stock across every location **including vans**, on one screen
- Be told before a stockout, not by a technician at the counter
- Trace every serialised part from receipt to consumption
- Keep brand-owned consignment stock provably separate

**Pain points today:** Tally plus Excel, no real-time view · stockouts found at the counter ·
inter-branch transfers coordinated in a WhatsApp group · month-end count takes 3 days and always
finds discrepancies · **van stock entirely untracked**.

> *"যখন টেকনিশিয়ান এসে বলে পার্টস নেই, তখনই বুঝি স্টক শেষ।"*
> ("I only know stock is finished when the technician tells me there are no parts.")

**Success looks like:** **98% accuracy**, van variance under 1%, replenishment that drafts itself.
**Modules:** M15, M41, M43, M16 · **Portal:** P03 (Inventory Console), P06

---

### P-14 — Branch Store Keeper / Warehouse Operative  ·  R18, R20

**Rubel Mia**, 29 · Branch store, Khulna · Tech literacy **2/5** · **Bengali only** · Shared desktop
and a handheld scanner · Standing, moving, often with both hands full

**Daily work:** issues parts against approved jobs · receives transfers and confirms them · picks and
puts away · counts on schedule · flags damage and quarantine.

**Goals**
- **Scan, don't type**
- Know immediately whether a part may be issued against this job
- A count task list that tells him exactly what to count and where

**Pain points today:** manual ledgers · parts issued against jobs that were never approved ·
transfers arriving with no paperwork.

**Success looks like:** every movement scanned; nothing issued that should not be.
**Modules:** M15, M41 · **Portal:** P03 (scanner-driven views)

---

### P-15 — Procurement Officer  ·  R19

**Nabil Islam**, 31 · Dhaka HQ · Tech literacy **4/5** · Bengali and English · Desktop

**Daily work:** requisitions to purchase orders · RFQs to 3+ vendors · vendor master and
qualification · PO tracking · three-way matching · import orders and LC tracking · vendor
performance.

**Goals**
- One system of record for the whole purchase cycle — no email chains
- Compare quotes side by side
- **Three-way match that blocks a mismatched invoice**, rather than flagging it after payment
- Vendor on-time and quality data that is collected automatically

**Pain points today:** email + WhatsApp + Excel · vendor invoice often differs from the PO ·
no visibility of what was received at which branch · vendor performance not measured.

**Success looks like:** three-way match blocks exceptions; vendor scorecards are real.
**Modules:** M16, M42, M44, M15, M52 · **Portal:** P03 (Procurement Console), P05

---

### P-16 — Account Manager (Corporate)  ·  R22

**Tania Haque**, 34 · Dhaka HQ · Tech literacy **4/5** · English and Bengali · Laptop and phone ·
Often at a client's office

**Daily work:** owns 15–30 corporate accounts · manages contracts across the 14 product families ·
runs quarterly business reviews · handles renewals · monitors entitlement consumption and contract
profitability · escalation point for her clients.

**Goals**
- See contract, entitlement consumption, SLA attainment and **profitability** per account
- Be warned about renewals **90 days out**, with a quotation already drafted
- Know when a contract is losing money **before** the renewal conversation
- Show the client their own data rather than assembling a pack

**Pain points today:** contracts in spreadsheets · renewals missed · utilisation unknown ·
profitability unknown · every QBR built by hand.

**Success looks like:** **88% renewal**, under 3% of contracts running at negative margin.
**Modules:** M08, M07, M39, M53, M25, M05 · **Portal:** P03 (Contract Console), P04, P06

---

### P-17 — Sales Manager  ·  R21

**Rezaul Karim**, 37 · Dhaka HQ · Tech literacy **4/5** · Bengali and English · Laptop

**Daily work:** pipeline for corporate and AMC business · quotations and tenders · discount approval
within authority · pricing exceptions · sales forecast.

**Goals**
- Quotation turnaround under 2 hours
- See margin **before** approving a discount
- Track quotation-to-order conversion by segment

**Pain points today:** quotes built in Excel; margin invisible at the point of discounting;
conversion never measured.

**Success looks like:** > 78% quotation-to-order conversion, discount exceptions under 5%.
**Modules:** M36, M11, M07, M08 · **Portal:** P03, P06

---

### P-18 — Marketing Manager  ·  R23

**Sadia Islam**, 30 · Dhaka HQ · Tech literacy **4/5** · Bengali and English · Laptop

**Daily work:** campaigns and journeys across channels · Privilege programme growth · referral
programme · promotional offers · marketing attribution and cost.

**Goals**
- Segment on real service and spend behaviour, not guesses
- Run a journey across SMS, WhatsApp, email and push from one place
- **Attribute revenue to campaigns honestly**
- Respect do-not-contact and consent absolutely

**Pain points today:** no segmentation data · campaigns run manually · attribution impossible ·
consent tracked nowhere.

**Success looks like:** 3× Privilege base, 12% of new customers referral-attributed.
**Modules:** M35, M10, M33, M07, M25 · **Portal:** P03, P06, P12

---

### P-19 — Marketplace Operations Officer ★  ·  R24

**Imrul Hasan**, 29 · Dhaka HQ · Tech literacy **4/5** · Bengali and English · Desktop ·
Managing 500+ external sellers who are not employees

**Daily work:** reviews and approves seller applications with KYC · monitors seller performance
scores · handles disputes between customers and sellers · manages category qualifications ·
oversees payouts · suspends and reinstates sellers.

**Goals**
- Verify a seller properly — NID, trade licence, references — **before** they can transact
- See a score that automatically reduces visibility and then suspends, without him having to argue
- Decide disputes from evidence, with the decision recorded
- Hold payouts while a dispute is open, automatically

**Pain points today:** this role and this business line **do not exist yet** — there is no system,
no seller record, no scoring, no dispute process, no payout mechanism.

> *"A marketplace seller wearing our brand is the customer's experience of 1000FiX. If I cannot hold
> them to the same standard as our own technicians, we shouldn't do it at all."*

**Success looks like:** 500 approved active sellers, dispute rate under 1.5%, **marketplace jobs
indistinguishable in quality from owned jobs**.
**Modules:** M12, M22, M23, M53, M11 · **Portal:** P03 (Marketplace Console)

---

### P-20 — Retail / Refurbishment Officer ★  ·  R25

**Mahfuz Rahman**, 32 · Refurbishment centre, Dhaka · Tech literacy **3/5** · Bengali · Desktop +
tablet on the floor

**Daily work:** values trade-ins · screens provenance and IMEI · takes devices into stock ·
schedules certified wipes · runs refurbishment work orders · grades against published criteria ·
lists for resale · manages refurbished warranty and reserve.

**Goals**
- A valuation he can defend to the customer
- **A hard gate that stops any device reaching resale without a destruction certificate**
- Consistent grading — the same device graded the same way by anyone
- Full provenance from intake to sale

**Pain points today:** tally sheets · valuation by feel · no provenance · **grading inconsistent
between people** · warranty exposure unquantified.

**Success looks like:** 12,000 units a year at 22% margin, 88% refurbishment yield, **zero units
released without a certificate**.
**Modules:** M14, M06, M17, M15, M38, M18 · **Portal:** P03

---

### P-21 — Finance Officer & Cashier  ·  R27, R29

**Mitu Akter**, 29 (Finance Officer, HQ) and **Shirin Akhter**, 24 (Cashier, branch counter) ·
Tech literacy **3/5** · **Bengali primary** · Windows desktop; cashier also uses a receipt printer
and payment terminal

**Daily work — officer:** invoices from completed jobs · payment posting across cash, card, bKash,
Nagad, SSLCOMMERZ and bank · Mushak 6.3 invoices · receivables follow-up · daily reconciliation.
**Daily work — cashier:** takes payment at the counter · issues receipts · opens and closes the cash
drawer · reconciles her shift.

**Goals**
- **Invoices generated from the job, not typed from a paper card**
- VAT calculated automatically and correctly, per service category
- All payment channels reconciled on one screen
- A shift that closes cleanly, every day

**Pain points today:** ~100 invoices typed by hand daily · Mushak from a separate Excel template ·
cash reports arrive from 51 branches as WhatsApp photos · VAT category mapping manual.

> *"প্রতিদিন ১০০টা ইনভয়েস বানাই হাতে। সিস্টেম যদি অটো করত, ভুলও কমত, সময়ও বাঁচত।"*

**Success looks like:** 100% of invoices auto-generated, 90%+ payments auto-matched, daily cash
closed at every counter.
**Modules:** M20, M51, M50, M19 · **Portal:** P03 (Finance Console)

---

### P-22 — Finance Manager  ·  R26

**Kamal Uddin**, 45 · Dhaka HQ · Tech literacy **3/5** · Bengali and English · Laptop and desktop

**Daily work:** AR and AP · monthly close and P&L · brand warranty reimbursement · payroll approval ·
budget variance · tax filing oversight.

**Goals**
- **Close in 3 days, not 15–20**
- Consolidated P&L by branch, business line and contract
- Track warranty claims submitted against amounts actually received
- Approve payroll knowing the numbers are right

**Pain points today:** data across 51 branch spreadsheets · warranty reimbursement tracked in a
separate Excel with frequent discrepancies · month-end consolidation manual · BEFTN submission takes
two days.

> *"Our monthly close takes 10 days because we're consolidating 51 branch Excel files."*

**Success looks like:** close in ≤ 3 days; warranty leakage under 2%; zero tax findings.
**Modules:** M19, M20, M52, M50, M51, M53, M54 · **Portal:** P03, P05, P06, P08

---

### P-23 — Warranty Claims Officer  ·  R28

**Anisur Rahman**, 35 · Dhaka HQ · Tech literacy **3/5** · Bengali and English · Desktop ·
Handles claims to 17+ brands, each with a different format

**Daily work:** reviews auto-created claims · checks evidence completeness against each brand's
rules · submits · chases · handles rejections and disputes · reconciles remittances · reports
leakage.

**Goals**
- Claims created **automatically within 24 hours**, with the evidence pack already assembled
- Be told what is missing **before** submission, not by a rejection
- One pipeline view with ageing per brand
- Be warned before a brand's submission window closes

**Pain points today:** claims compiled by hand from paper · 30–90 day delays · **15–20% never
recovered** · rejections arrive weeks later with no clear reason · reconciliation takes weeks.

**Success looks like:** 95% submitted within 72 hours, 90%+ approved first time, **leakage below 2%**.
**Modules:** M09, M20, M53, M17, M22 · **Portal:** P03 (Warranty Console), P06, P08

---

### P-24 — Payroll Officer ★  ·  R41

**Nasima Begum**, 33 · Dhaka HQ · Tech literacy **3/5** · Bengali · Desktop ·
**May prepare payroll but may not approve or release it**

**Daily work:** prepares the monthly run for 500+ employees · resolves attendance exceptions ·
applies tax slabs, provident fund and gratuity · prepares the BEFTN file · distributes payslips.

**Goals**
- Attendance that arrives complete and locked, not chased from 51 branches
- Statutory calculation she does not have to do by hand — **and can prove is right**
- Exceptions surfaced before the run, not after
- A BEFTN file the bank accepts first time

**Pain points today:** attendance arrives as WhatsApp spreadsheets · overtime and incentive
calculated per employee, manually · a 3-day cycle · **an error affects every employee at once**.

> *"If I get one rule wrong, five hundred people are paid wrong on the same day."*

**Success looks like:** under 4 hours, under 0.3% corrections, BEFTN accepted without rework.
**Modules:** M56, M55, M57, M21, M19 · **Portal:** P03 (HR Console — prepare only)

> **Design constraint:** segregation of duties is user-visible. **SOD-03** blocks preparer =
> approver; **SOD-29** blocks approver = bank-file releaser. The interface must make the boundary
> obvious rather than failing at submission.

---

### P-25 — HR Officer  ·  R31

**Sonia Parvin**, 27 · Dhaka HQ · Tech literacy **3/5** · Bengali · Desktop

**Daily work:** employee records for 500+ · attendance and leave · onboarding · exits · employment
artefacts required by the Bangladesh Labour Act — appointment letter, identity card, service book.

**Goals**
- Any employee's attendance, leave balance and history, instantly
- Leave approved without paper
- Self-service so employees stop phoning her
- Statutory documents generated, not typed

**Pain points today:** attendance from 51 branches as spreadsheets · leave balances in separate Excel
rows · every request arrives by phone.

**Success looks like:** 85% employee self-service adoption; 99% attendance capture.
**Modules:** M21, M55, M58 · **Portal:** P03 (HR Console)

---

### P-26 — HR Manager  ·  R30

**Rahim Bhuiyan**, 48 · Dhaka HQ · Tech literacy **3/5** · Bengali and English · Laptop

**Daily work:** HR policy and Bangladesh Labour Act compliance · approves payroll jointly with the
CFO · performance and compensation cycles · workforce planning · owns competency and certification.

**Goals**
- **Certification expiry visible and enforced**, not discovered by a rejected claim
- Performance appraisal without paper
- Link performance to incentive automatically
- Workforce capacity by branch against demand

**Pain points today:** certification in a spreadsheet, renewals missed · appraisals on paper · no
link between rating and incentive · training completion unknown by branch.

**Success looks like:** **zero claims rejected for an uncertified technician**.
**Modules:** M21, M22, M56, M57, M55, M58 · **Portal:** P03, P06

---

### P-27 — Training Coordinator & Competency Assessor ★  ·  R42, R43

**Farhad Hossain**, 36 (Coordinator) and **Nazma Akter**, 41 (Assessor) · Tech literacy **3/5** ·
Bengali · Desktop; assessor also works on the workshop floor

**Daily work:** course catalogue and Bengali content · enrolment and scheduling · brand certification
tracks across 17+ partners · assessment and re-certification · **marketplace seller category
qualification** · training effectiveness.

**Goals**
- Know who is certified for what, and when it lapses
- Assess competency against a defined standard, with the result binding on dispatch
- Deliver training in Bengali that technicians will actually complete
- Qualify external sellers to the same standard as employees

**Pain points today:** certification tracked in a spreadsheet · no assessment record · **no link
between competency and the dispatch decision** · no external-party qualification at all.

**Success looks like:** 100% certifications current; **FR-LMS-039 eligibility check enforced at
every assignment**.
**Modules:** M22, M21, M57, M12 · **Portal:** P03

*(Role R45 Recruiter sits with this persona group; talent acquisition in M58 shares the same
workspace and the same offer-approval segregation.)*

---

### P-28 — HSE Officer ★  ·  R44

**Kawsar Ali**, 39 · Dhaka HQ, travelling to branches · Tech literacy **3/5** · Bengali · Laptop and
Android

**Daily work:** incident, near-miss and hazard management · risk assessments · PPE · lone-worker
safety for field technicians · electrical and chemical safety · accident notification and
compensation under the Bangladesh Labour Rules 2015 · safety committee.

**Goals**
- **A technician can report a hazard from the field in under 30 seconds**
- Be alerted to a serious incident immediately, not at the end of the shift
- Evidence the safety committee and first-aid obligations for inspection
- See patterns before someone is hurt

**Pain points today:** incidents reported verbally, if at all · no near-miss data · statutory
obligations evidenced by paper file.

**Success looks like:** near-miss reporting rising (a good sign), serious incidents alerted in real
time, statutory obligations provable.
**Modules:** M59, M21, M23, M60 · **Portal:** P03, P02 (technician reporting)

*(Role R46 Occupational Health sits with this persona and holds sole access to medical detail.)*

---

### P-29 — Quality Manager / Field Auditor  ·  R32

**Shirin Sultana**, 40 · Dhaka HQ, auditing across 51+ branches · Tech literacy **3/5** · Bengali and
English · Laptop and Android tablet · **Audits on site, often with no connectivity**

**Daily work:** ISO 9001:2015 and ISO 27001 evidence · internal audit programme · non-conformance ·
CAPA with effectiveness verification · complaint root cause · supplier and **marketplace seller
quality gates** · SOP version control.

**Goals**
- Complete an audit **on the device, offline**, with photo evidence against clauses
- Raise a finding with classification, severity and an owner, on the spot
- Verify a previous CAPA while she is standing in the branch
- **Evidence assembled by the system, not by her, before a surveillance audit**

**Pain points today:** paper checklists then re-keying · evidence in a separate camera roll · CAPA
closed without verification · audit evidence assembled manually every year.

**Success looks like:** 100% of audits on mobile, finding-to-CAPA under 5 days, **zero major
non-conformances**.
**Modules:** M23, M24, M60, M45, M12 · **Portal:** P11, P03, P06

---

### P-30 — Contact Centre Agent & Supervisor ★  ·  R34, R35

**Tasnim Jahan**, 24 (Agent) and **Rakib Hossain**, 33 (Supervisor) · Tech literacy **3/5** ·
**Bengali primary** · Desktop with headset · Handling 60–90 contacts a shift, measured on handling
time

**Daily work — agent:** takes voice, chat, WhatsApp, email, SMS and social contacts from one queue ·
identifies the customer · answers, books, reschedules, quotes, takes payment, renews, raises
complaints · codes the disposition.
**Daily work — supervisor:** watches queue and service level · monitors and scores quality · coaches ·
barges in and whispers on live calls.

**Goals**
- **Customer 360 on screen before she says hello**
- Do the thing the customer asked for **without leaving the conversation**
- Fewer than three screen switches per contact
- Canned responses in Bengali that do not sound machine-written

**Pain points today:** the hotline 16743 **leaves no record at all** · no cross-channel history ·
alt-tabbing between systems while the customer waits · no quality data.

**Success looks like:** **100% of conversations captured**, first-contact resolution above 78%,
handling time down 25%.
**Modules:** M27, M32, M33, M07, M01, M34 · **Portal:** P10

---

### P-31 — IT Administrator  ·  R33

**Tanvir Ahmed**, 34 · Dhaka HQ · Tech literacy **5/5** · Bengali and English · Laptop and terminal

**Daily work:** users, roles and permissions across 46 roles and 12 portals · system health ·
backups and restore tests · integration health · first-line support · configuration and feature
flags · release coordination.

**Goals**
- Provision or revoke an account in under 2 minutes — and have **leavers revoked automatically
  within an hour**
- One health console: application, database, integrations, jobs, events
- Configure branch and role access **without vendor support**
- Prove a backup restores, on a schedule

**Pain points today:** accounts managed across separate applications · no consolidated audit trail ·
outages reported by users before IT knows · backup verification manual.

**Success looks like:** zero orphaned accounts beyond 24 hours; zero undetected integration failures
beyond 5 minutes.
**Modules:** M29, M30, M28, M64, M66 · **Portal:** P03 (System Console)

---

### P-32 — Data Steward & Chief Data Officer ★  ·  R39, R40

**Nusrat Jahan**, 37 (Data Steward) and the **Chief Data Officer** (statutory role, appointment
subject to decision D-15) · Tech literacy **4–5/5** · English and Bengali · Laptop

**Daily work — steward:** owns golden records for party, product, location and asset · runs
stewardship workflow · resolves duplicates and merges · monitors data quality scores.
**Daily work — CDO:** represents the Company to the **National Data Management Authority** ·
handles data-subject requests and complaints · oversees consent and transparency notices · assesses
breaches and notifies · maintains processing records.

**Goals**
- A single golden record per party, with merges reversible and audited
- **Consent and purpose recorded per processing activity**, not assumed
- Answer a data-subject request completely and within the statutory window
- Know, at any moment, what personal data the Company holds and on what lawful basis

**Pain points today:** **neither role exists**; customer data is duplicated across spreadsheets; there
is no consent record, no transparency notice, no data-subject process and no breach procedure.

> *"Enforcement starts around 13 May 2027 — inside Wave 4. Whether or not we are ready, the
> obligation begins."*

**Success looks like:** every data-subject right exercisable and evidenced; breach notification
within the prescribed window; **zero regulatory findings**.
**Modules:** M33, M29, M60, M64, M24, M65 · **Portal:** P03

> **Statutory note.** At 250,000+ customers per month 1000FiX will almost certainly qualify as a
> *significant data fiduciary*, making the CDO appointment a legal obligation (NFR-096, decision
> D-15). Penalty exposure reaches **BDT 50 lakh**.

---

### P-33 — Executive  ·  R01 CEO, R02 CTO, R03 CFO, R04 CCO

**Mahmud Hassan**, 48 (CEO) · Tech literacy **3/5** · Bengali and English · iPad, laptop, phone

**Daily work:** monthly and weekly performance review · branch and technician performance ·
investment and expansion decisions · Steering Committee chair.

**Goals**
- One dashboard across **all 14 revenue streams**
- Drill from group revenue to a single job without asking anyone
- A weekly summary that arrives without being requested
- **Decide on live data, not on a compiled pack**

**Pain points today:** waits 10+ days for the monthly pack · cannot spot a problem branch until it
is a crisis · no visibility of the new business lines because they have no system.

**Success looks like:** **zero manual reporting packs**; 100% of management reviews conducted on live
data.
**Modules:** M25, M62, M54 · **Portal:** P06, P03

---

### P-34 — Customer — Three Archetypes  ·  R36

The customer is not one person. The platform must serve all three without compromise.

#### P-34a — Rafiq Ahmed, 28 · Software engineer · Banani, Dhaka · Tech literacy **5/5** · English primary · iPhone
**Wants:** book in under two minutes, track by GPS, pay by card or bKash, digital invoice by email,
never speak to anyone.
**Will abandon if:** the flow takes more than three steps, or the price is not shown before booking.

#### P-34b — Tahmina Khatun, 35 · Homemaker · Gulshan, Dhaka · Tech literacy **3/5** · **Bengali only** · Android
**Wants:** book AC service **in Bengali**, know when the technician will arrive and who he is, pay by
bKash, get an SMS she can show her husband.
**Will abandon if:** any screen is in English, or she cannot tell what the service will cost.
**This archetype is the design default for P01.**

#### P-34c — Abdul Karim, 62 · Retired government employee · Uttara · Tech literacy **1/5** · **Bengali only** · Basic Android, rarely used
**Wants:** to phone 16743 and get a reliable appointment; a technician he can trust; to understand
the cost **before** work starts; ideally the same technician as last time.
**Will not use the app at all** — and must be served just as well through the hotline and the counter.

> **Design consequence.** Self-service must be excellent **and** the assisted channels must be
> equally complete. Every capability on P01 must also be executable by a contact-centre agent on
> P10 or a counter agent on P03 **on the customer's behalf**.

**Modules:** M01, M02, M03, M06, M07, M08, M09, M10, M11, M12, M13, M14, M18, M20, M27, M33, M34, M38
· **Portal:** P01 (plus P10/P03 assisted)

---

### P-35 — Corporate Portal User  ·  R37

**Imran Khan**, 38 · Facility Manager, bank HQ with 12 branches · Tech literacy **4/5** · English
primary · Laptop and iPhone

Sub-roles within one corporate account: **Requester · Approver · Finance · Admin**, each scoped.

**Daily work:** manages IT equipment across 12 sites · raises single and bulk service requests ·
approves within delegated authority · reviews SLA and service credits · approves consolidated
invoices · reports to his own management on service quality.

**Goals**
- Manage the **asset estate** — upload, assign to sites, departments and users, retire
- Raise **45 requests from one CSV**, validated against contract coverage **before** submission
- See SLA attainment and **service credits earned**, not claimed after argument
- **One consolidated invoice**, itemised by site, department and asset
- Download destruction and disposal certificates for his own compliance file

**Pain points today:** individual requests by phone and email per device · no status view across 12
sites · separate invoices per location, two days to reconcile · no SLA data to justify renewal.

**Success looks like:** > 70% of his requests self-served; bulk request in under 5 minutes; invoice
disputes under 3%.
**Modules:** M05, M07, M08, M09, M11, M17, M20, M25, M27 · **Portal:** P04

---

### P-36 — External Party — Five Archetypes ★  ·  R38

#### P-36a — Vendor Representative · **Salman Sheikh**, 45 · Tech literacy **2/5** · Bengali · Android and a basic PC
Receives POs, confirms delivery, submits invoices, checks payment status, sees his own scorecard.
**Today:** POs arrive by WhatsApp and get lost; he phones every week about payment.
**Success:** > 90% of POs acknowledged in the portal; he never phones about payment again.

#### P-36b — Marketplace Seller ★ · **Jewel Rana**, 30 · Independent engineer, Narayanganj · Tech literacy **3/5** · **Bengali only** · Android
Registers with NID and trade licence, lists services, bids on broadcast jobs, executes to 1000FiX
standards, gets paid from a wallet, buys boost placement.
**Today:** this user class **does not exist**.
**Will leave if:** payouts are slow or scoring feels arbitrary. Switching cost is near zero.
**Success:** onboarding completed by > 60% of starters; > 70% monthly active; > 65% still there at
12 months.

#### P-36c — Brand Partner Representative · **Tanvir Mahmud**, 35 · Samsung Bangladesh · Tech literacy **4/5** · English · Laptop
Receives claims with complete evidence packs, approves or rejects with reason, reconciles
remittances, publishes rate cards, audits 1000FiX's performance on his brand, checks technician
certification.
**Today:** claims arrive as Excel attachments with evidence in separate emails; no ageing view.
**Success:** > 80% of claims via portal, decisions in under 10 days.

#### P-36d — Courier Partner Coordinator ★ · Tech literacy **3/5** · Bengali
Receives consignment bookings, updates status, uploads POD, submits settlement claims — **seeing only
the consignments assigned to them and the minimum data needed to deliver** (EA-07).

#### P-36e — Referral / Alliance Partner ★ · Tech literacy **3–4/5** · Bengali and English
Generates referral links and codes, submits leads, tracks conversion, views commission statements
and payout schedule, accesses co-marketing material.
**Today:** referral is informal and commission is calculated by hand.
**Success:** > 200 active partners; **commission accuracy 100%**.

**Modules:** M16, M42, M12, M09, M03, M40, M10, M53 · **Portals:** P05, P07, P08, P09, P12

---

### 3.2 Accessibility Personas

Following current enterprise practice, accessibility is represented by named personas rather than
by a checklist, so that design decisions are made against a person.

| Persona | Condition / context | What it demands of the design |
|---|---|---|
| **A-01 — Abdul (P-34c)** | Age 62, low tech literacy, Bengali only, presbyopia | Large type, high contrast, no jargon, assisted channel of equal quality |
| **A-02 — Kabir (P-03)** | **Situational impairment** — one hand occupied, direct sunlight, gloves, noise | Thumb-reach targets ≥ 44 px, sunlight-readable contrast, no gesture-only actions, voice-to-text |
| **A-03 — Jasim (P-10)** | **Situational impairment** — helmet, gloves, motorcycle, rain | Very large targets, scan over type, minimum steps, works wet-fingered |
| **A-04 — Rubel (P-14)** | Low literacy, Bengali only, both hands full | Icons paired with Bengali text, scanner-first, never colour alone |
| **A-05 — A low-vision back-office user** | Screen magnification to 200%, screen reader | Reflow without horizontal scroll, semantic labels, visible focus, keyboard-complete |
| **A-06 — A user with motor impairment** | Keyboard-only, no fine pointing | Every function keyboard-reachable; **no drag-only interaction** — the dispatch board must have a keyboard equivalent |
| **A-07 — A user with a cognitive difference** | Working-memory load, distraction-prone environment | Short steps, progress shown, no timed-out forms, no re-entry of data already given |

> **A-06 has a direct design consequence.** The dispatch board is specified as drag-and-drop.
> **Drag-and-drop alone fails WCAG 2.2 SC 2.5.7 (Dragging Movements).** A single-pointer and
> keyboard alternative for every drag action is required — see §21.4.

---

## 4. USER ROLES & ACCESS MATRIX

### 4.1 The 46 Roles

| Group | Roles | Count |
|---|---|---:|
| **Executive & management** | R01 CEO · R02 CTO · R03 CFO · R04 CCO · R05 Operations Director | 5 |
| **Service operations** | R06 Branch Manager · R07 Dispatch Manager · R08 Service Centre Agent · R09 Workshop Supervisor · R10 Senior Technician · R11 Junior Technician · R12 Specialist Technician (L3) · R13 Remote Support Engineer · R14 Data Services Technician | 9 |
| **Logistics & supply chain** | R15 Logistics Coordinator · R16 Rider · R17 Inventory Manager · R18 Branch Store Keeper · R19 Procurement Officer · R20 Warehouse Operative | 6 |
| **Commercial** | R21 Sales Manager · R22 Account Manager · R23 Marketing Manager · R24 Marketplace Operations Officer · R25 Retail/Refurbishment Officer | 5 |
| **Finance, people & governance** | R26 Finance Manager · R27 Finance Officer · R28 Warranty Claims Officer · R29 Cashier · R30 HR Manager · R31 HR Officer · R32 Quality Manager | 7 |
| **Technology & support** | R33 IT Administrator · R34 Contact Centre Agent · R35 Contact Centre Supervisor | 3 |
| **External** | R36 Customer · R37 Corporate Portal User · R38 External Party | 3 |
| **Pending formalisation** ★ | R39 Data Steward · R40 Chief Data Officer · R41 Payroll Officer · R42 Training Coordinator · R43 Competency Assessor · R44 HSE Officer · R45 Recruiter · R46 Occupational Health | 8 |
| | **Total** | **46** |

> **Registration status.** R01–R38 are in the central role register. **R39–R46 are defined and in
> active use inside module specifications but are not yet registered.** Two further identifiers
> (R54, R57) are referenced with no definition, and **R60 is a duplicate identity for R32 — a live
> permission defect, because an access rule written against R32 does not apply to a user granted
> R60.** Completion to R46, elimination of R60 and resolution of R54/R57 is Wave 1 scope.
> **Design and test against 46 roles.**

### 4.2 Portal Access Matrix

| Role | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 | P11 | P12 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| R01 CEO | | | ● | | | ● | | | | | | |
| R02 CTO | | | ● | | | ● | | | | | | |
| R03 CFO | | | ● | | | ● | | | | | | |
| R04 CCO | | | ● | | | ● | | | | | | |
| R05 Operations Director | | | ● | | | ● | | | | | ● | |
| R06 Branch Manager | | | ● | | | ● | | | | | ● | |
| R07 Dispatch Manager | | | ● | | | ● | | | ● | | | |
| R08 Service Centre Agent | | | ● | | | | | | | | | |
| R09 Workshop Supervisor | | | ● | | | | | | | | | |
| R10 Senior Technician | | ● | | | | | | | | | | |
| R11 Junior Technician | | ● | | | | | | | | | | |
| R12 Specialist Technician | | ● | ● | | | | | | | | | |
| R13 Remote Support Engineer | | | ● | | | | | | | ● | | |
| R14 Data Services Technician | | | ● | | | | | | | | | |
| R15 Logistics Coordinator | | | ● | | ● | | | | ● | | | |
| R16 Rider | | | | | | | | | ● | | | |
| R17 Inventory Manager | | | ● | | ● | ● | | | | | | |
| R18 Branch Store Keeper | | | ● | | | | | | | | | |
| R19 Procurement Officer | | | ● | | ● | | | | | | | |
| R20 Warehouse Operative | | | ● | | | | | | | | | |
| R21 Sales Manager | | | ● | | | ● | | | | | | |
| R22 Account Manager | | | ● | ● | | ● | | | | | | |
| R23 Marketing Manager | | | ● | | | ● | | | | | | ● |
| R24 Marketplace Operations | | | ● | | | ● | ● | | | | | |
| R25 Retail / Refurb Officer | | | ● | | | | | | | | | |
| R26 Finance Manager | | | ● | | ● | ● | | ● | | | | |
| R27 Finance Officer | | | ● | | ● | | | | | | | |
| R28 Warranty Claims Officer | | | ● | | | ● | | ● | | | | |
| R29 Cashier | | | ● | | | | | | | | | |
| R30 HR Manager | | | ● | | | ● | | | | | | |
| R31 HR Officer | | | ● | | | | | | | | | |
| R32 Quality Manager | | | ● | | | ● | | | | | ● | |
| R33 IT Administrator | | | ● | | | | | | | | | |
| R34 Contact Centre Agent | | | | | | | | | | ● | | |
| R35 CC Supervisor | | | ● | | | ● | | | | ● | | |
| R36 Customer | ● | | | | | | | | | | | |
| R37 Corporate Portal User | | | | ● | | | | | | | | |
| R38 External Party | | | | | ● | | ● | ● | ● | | | ● |
| **R39 Data Steward** ★ | | | ● | | | ● | | | | | | |
| **R40 Chief Data Officer** ★ | | | ● | | | ● | | | | | | |
| **R41 Payroll Officer** ★ | | | ● | | | | | | | | | |
| **R42 Training Coordinator** ★ | | | ● | | | | | | | | | |
| **R43 Competency Assessor** ★ | | | ● | | | | | | | | | |
| **R44 HSE Officer** ★ | | ● | ● | | | ● | | | | | | |
| **R45 Recruiter** ★ | | | ● | | | | | | | | | |
| **R46 Occupational Health** ★ | | | ● | | | | | | | | | |

### 4.3 Data Isolation — What Each User Can See

Six tiers, enforced by record rules at the data layer — **not by hiding menu items**.

| Tier | Rule | What it protects | Example user experience |
|---|---|---|---|
| **T0 — Global** | Visible to all authenticated internal users | Catalogue, parts, brand and model master, checklist templates, knowledge base, branch directory | Kabir sees the same repair manual as a technician in Khulna |
| **T1 — Entity** | Visible within the legal entity | Chart of accounts, tax configuration, payroll structures | Multi-country ready from day one |
| **T2 — Branch** | Visible within the operating unit | Service orders, inventory, cash, branch HR, queue | Arif sees Sylhet, not Chittagong |
| **T3 — Zone** | Visible within the dispatch zone | Technician schedules, van stock, route plans | Farida sees her zones only |
| **T4 — Own record** | Visible to owner or assignee only | Customer's own orders; technician's own jobs and earnings; seller's own listings and payouts; vendor's own POs | Kabir sees his jobs and his earnings — not a colleague's |
| **T5 — Restricted** | Explicit grant, access logged, **step-up authentication** | Individual payroll, NID, bank details, data-recovery case content, call recordings, biometric templates, seller KYC | Farhana sees only her assigned cases, and every look is recorded |

### 4.4 Field-Level Visibility

Some fields are hidden even from users who can see the record. This is a **user-visible design
requirement**, not a background control: a field the user may not see must be absent, not greyed
out with a tooltip that reveals its existence.

| Field | Visible to |
|---|---|
| `unit_cost`, `total_cost`, `margin` | Executives, Branch Manager, Inventory Manager, Sales, Account Manager, Finance |
| `salary`, `allowances`, `deductions` | CFO, Finance Manager, HR Manager, HR Officer, **and the employee themselves** |
| `nid_number` | Finance, HR, IT Administrator (with justification), compliance |
| `bank_account` | CFO, Finance Manager, Finance Officer, HR Manager |
| `recovered_data_index` | **Case-assigned Data Services Technician only**; CTO with approval |
| `call_recording_url` | CC Supervisor, Quality Manager, CTO (audit) |
| `commission_rate` | CFO, CCO, Marketplace Operations, Finance Manager |
| `seller_kyc_document` | Marketplace Operations, Finance Manager, Quality Manager |
| `technician_incentive_detail` | HR, **the technician themselves**, Branch Manager (own branch, summary only) |
| `customer_credit_limit` | CFO, Sales Manager, Account Manager, Finance |
| `internal_note` | **Internal roles only — never exposed on any external portal** |
| `vendor_price` | Inventory Manager, Procurement, Finance |
| `model_confidence`, `model_features` | CTO, IT Administrator, model owners |

### 4.5 Segregation of Duties — Where the System Will Stop a User

Thirty controls, enforced **at role assignment** by the permission engine. From the user's point of
view the important design requirement is that **the block is explained at the point of assignment,
not discovered at the point of transaction**.

| ID | The system will not let the same person… | Applies to |
|---|---|---|
| SOD-01 | create a vendor **and** approve that vendor's invoice | R19, R26, R27 |
| SOD-02 | raise a PO **and** receive the goods **and** approve the invoice (any two, never all three) | R19, R20, R27 |
| SOD-03 | process payroll **and** approve payroll | R41, R30, R03 |
| SOD-04 | create a credit note **and** approve it | R27, R26 |
| SOD-05 | adjust inventory **and** perform the count that justifies it | R17, R18, R20 |
| SOD-06 | approve a marketplace seller **and** approve their payout | R24, R26 |
| SOD-07 | repair a device **and** perform its independent QC (above threshold) | R10, R11, R12, R09 |
| SOD-08 | create a customer **and** approve their credit limit | R08, R21, R22 |
| SOD-09 | administer users **and** approve their own access request | R33 |
| SOD-10 | value a trade-in **and** purchase it **and** resell it | R25 |
| SOD-11 | raise a warranty claim **and** approve its write-off | R28, R26 |
| SOD-12 | handle cash **and** reconcile the cash book | R29, R27 |
| **SOD-29** ★ | approve payroll **and** release the bank file | R30, R03, R41 |
| **SOD-30** ★ | calculate an incentive (M57) **and** pay it (M56) | R30, R41 |
| SOD-13 … SOD-28 | *A further 16 controls implemented in module specifications but not yet in the central matrix — see §26.3* | Various |

**Exceptions** require CFO or CTO approval, are time-boxed, and appear on a standing exception
report reviewed quarterly. **The user sees the expiry date of any exception granted to them.**

### 4.6 Approval Authority — What a User Can Approve

| Transaction | Threshold | Approver |
|---|---|---|
| Repair estimate | > BDT 5,000 | Customer + system record |
| Repair estimate | > BDT 25,000 | Customer + Branch Manager |
| Repair estimate | > BDT 100,000 | Customer + Operations Director |
| Discount | ≤ 10% / ≤ 20% / ≤ 35% / > 35% | Agent / Branch Manager / Sales Manager / CCO |
| Purchase requisition | ≤ 50K / ≤ 500K / ≤ 2M / > 2M BDT | Inventory Manager / Procurement Manager / CFO / CEO |
| Credit note | ≤ BDT 10,000 / above | Finance Officer / Finance Manager |
| Inventory write-off | ≤ BDT 25,000 / above | Inventory Manager / CFO |
| Contract — standard / non-standard | Any value | Sales Manager / CCO + CFO |
| Marketplace payout | Standard / held or disputed | Automatic on schedule / Finance Manager |
| Trade-in offer | ≤ BDT 30,000 / above | Retail Officer / Retail Manager + Finance |
| Payroll run | Any | **HR Manager + CFO** |
| **Data destruction** | Any | **Data Services Technician + witness** |
| Access request — standard / privileged | Any | Line Manager / Line Manager + IT Admin + CTO |

### 4.7 External Party Access Rules — The User-Visible Contract

| Rule | What the external user experiences |
|---|---|
| EA-01 | They see only records where they are a named party |
| EA-02 | They **never** see cost, margin, internal notes or another party's data |
| EA-03 | A corporate user sees only their own company's data, scoped further by their role in it |
| EA-04 | A marketplace seller sees the customer's name, contact and address **only for an awarded job, and only for a defined period after completion** — after which it disappears from their view |
| EA-05 | A brand partner sees only their own brand's claims and service data |
| EA-06 | A vendor sees only their own POs, receipts and invoices |
| EA-07 | A courier sees only their assigned consignments, with the minimum data needed to deliver |
| EA-08 | External sessions time out after 30 minutes of inactivity |
| EA-09 | **MFA is required for any external action with a financial consequence** |
| EA-10 | Every external access to customer personal data is logged and reportable |
| EA-11 | Scope cannot be widened by changing a request parameter |
| EA-12 | Bulk export is limited, rate-controlled and logged |

### 4.8 Access Lifecycle — The User Experience of Joining, Moving and Leaving

| Stage | Trigger | What the user experiences |
|---|---|---|
| **Provision** | `employee.joined` | Identity created; **role assigned from the position profile**, not chosen ad hoc; portal access granted; onboarding and mandatory training assigned automatically |
| **Modify** | Transfer or promotion | Old permissions revoked and new granted **on the effective date** — no accumulation of historical access |
| **Elevate** | Approved access request | Time-boxed elevation with a **visible expiry**; the session is recorded and the user is told so |
| **Review** | Quarterly | The manager receives a review task; **access not confirmed by the deadline is revoked** |
| **Suspend** | Leave or investigation | Access disabled; records preserved |
| **Deprovision** | `employee.left` | **All access revoked within one hour**; devices deregistered; delegated authority reassigned |
| **External expiry** | Agreement or registration lapses | External access disabled automatically; the party is told in advance |

---

## 5. USER GOALS & NEEDS

Each goal below is stated as the user would state it, with the measure that proves it was met.

### 5.1 Front-Line Service (R08, R09, R04-side)

| Goal | Measure of success |
|---|---|
| Serve a walk-in customer completely in under three minutes | **≤ 3 min**, timed observation, 20 samples, by branch staff |
| Find any customer and their full history without leaving the screen | ≤ 2 interactions; **≤ 4 clicks to any record from any starting point** |
| Know warranty and contract entitlement at the moment of intake | Automatic; no external call; result in ≤ 2 s |
| Print a legible job token and job card every time | Zero print failures during UAT |
| Never re-type data the system already holds | Zero duplicate entry in the intake journey |
| See the whole workshop at a glance and know what is blocked | WIP ageing visible; zero devices unaccounted |

### 5.2 Field Execution (R10, R11, R12, R16)

| Goal | Measure of success |
|---|---|
| Know the full day, in order, before leaving home | Job list available and cached by 07:30 |
| See the device's history before arriving | Available **offline**, downloaded at assignment |
| Complete job documentation in under five minutes | **< 5 min** average |
| **Work a full day with no signal and lose nothing** | **24 h offline; zero data loss; sync ≤ 30 s on 3G** |
| Never make an unplanned trip for a part | Van stock visible and considered in assignment |
| See what I earned today | Earnings and incentive updated same day |
| Get help without embarrassing myself in front of the customer | One-tap escalation carrying full context |
| Prove I handed the item over | **POD capture 100%; zero custody breaks** |
| Report a hazard in seconds | Incident/near-miss report **< 30 s** from the technician app |

### 5.3 Dispatch & Operations Management (R05, R06, R07)

| Goal | Measure of success |
|---|---|
| Dispatch the whole morning queue in under ten minutes | **< 10 min** |
| Understand why a technician was recommended | Plain-language explanation shown with every recommendation |
| Be warned before an SLA breaches | Escalation at 50 / 75 / 90 / 100% with acknowledgement tracking |
| Today's branch numbers without running a report | Branch console loads **< 2 s** |
| Approve from my phone | **≤ 3 taps** |
| Compare my branch to the network | Benchmark on every branch dashboard |
| Know a branch is failing on Monday, not at month-end | Real-time; league table across 51+ branches |

### 5.4 Commercial & Customer (R21, R22, R23, R24, R25, R34, R35)

| Goal | Measure of success |
|---|---|
| Quote in under two hours | Quotation turnaround **< 2 h** |
| See margin before approving a discount | Margin visible at the point of decision |
| Know a contract is unprofitable before renewal | Contract profitability continuous; **< 3% negative margin** |
| Answer any customer on any channel from one screen | **< 3 screen switches per contact** |
| Never lose the record of a conversation | **100% of conversations captured** |
| Hold a marketplace seller to the same standard as our own technicians | Identical QC and evidence standards; dispute rate **< 1.5%** |
| Grade a refurbished device the same way every time | Published criteria; supervisor override requires justification |

### 5.5 Finance & Compliance (R03, R26, R27, R28, R29, R41)

| Goal | Measure of success |
|---|---|
| Invoice generated by the system, not typed | **100% auto-generated; ≤ 5 s from job closure** |
| VAT correct without manual mapping | Mushak 6.3 compliant; **zero NBR exceptions** |
| Reconcile payments across every channel on one screen | **≥ 90% auto-match** |
| Close the month in three days | **≤ 3 days** |
| Submit every eligible warranty claim inside the brand's window | **95% within 72 h; leakage < 2%** |
| Close my counter cleanly at the end of every shift | Daily reconciliation; unclosed shift blocks the next opening |
| Run payroll for 500 people without a manual calculation | **< 4 h; < 0.3% corrections; BEFTN accepted first time** |

### 5.6 People, Quality & Governance (R30, R31, R32, R42, R43, R44, R46)

| Goal | Measure of success |
|---|---|
| Never discover a certification lapse from a rejected claim | **Zero claims rejected for an uncertified technician** |
| Complete an audit on site, offline, with evidence | **100% of audits on mobile**; evidence attached 100% |
| Close a CAPA only when it has actually worked | Effectiveness verification mandatory before closure |
| See safety patterns before someone is hurt | Near-miss reporting active; serious incidents alerted in real time |
| Prove our statutory obligations to an inspector | Evidence assembled by the system, not by a person |

### 5.7 Platform & Data (R02, R33, R39, R40)

| Goal | Measure of success |
|---|---|
| Provision or revoke access in under two minutes | **≤ 2 min**; leavers revoked automatically within 1 hour |
| Know a system is failing before a user tells me | **Zero integration failures undetected beyond 5 min** |
| One golden record per customer | Duplicate detection and reversible merge |
| Answer a data-subject request completely and on time | Within the statutory window, fully evidenced |
| Know what personal data we hold and on what lawful basis | Consent and purpose recorded **per processing activity** |

### 5.8 External Users (R36, R37, R38)

| Goal | Measure of success |
|---|---|
| Book a service in three steps, in Bengali | **≥ 88% online booking rate**; funnel conversion > 72% |
| Never have to phone to find out what is happening | **> 80% of status enquiries self-served** |
| Understand what it will cost before work starts | Upfront price indication on every booking path |
| Raise 45 requests at once and know they are covered | Bulk CSV validated against contract coverage; **< 5 min** |
| Get paid on time and understand why I was paid that amount | **Payout accuracy 100%**; itemised statement |
| Decide a warranty claim with the evidence in front of me | **> 80% of claims via portal**; decision **< 10 days** |
| Exercise my data rights without a fight | Request satisfied within the statutory window |

---
---

# PART B — WHAT USERS NEED THE SYSTEM TO DO

> **255 user stories.** Each is traced to a role, a module, a wave and a business objective. Stories
> marked **P0** are go-live blocking. Acceptance criteria are testable and form the basis of UAT.

---

## 6. USER STORIES — CATEGORY A: SERVICE DELIVERY & OPERATIONS

### 6.1 Service Request & Order Management (M01 · `SRM` · W1–W2)

---

**US-SRM-001** | Service Centre Agent (R08) | **P0** | W1 | M01 | BO-01
*As a service centre agent, I want to identify a returning customer from their phone number so that
their details, devices and history fill in automatically and I do not re-type anything.*

**AC**
1. Lookup by phone, NID, name or device serial returns a result in **≤ 1 second**
2. On match: party, addresses, registered devices, open orders and entitlement pre-populate
3. On no match: a new party can be created **inline, without leaving the intake screen**
4. Possible duplicates are shown with a merge option rather than silently creating a second record
5. The system warns if the same device already has an open service order
6. A branch- and business-line-aware order number is generated automatically

---

**US-SRM-002** | Service Centre Agent (R08) | **P0** | W1 | M01, M17 | BO-04
*As a service centre agent, I want the device's warranty and contract entitlement determined
automatically when I scan the serial so that I never have to phone a brand partner.*

**AC**
1. Serial, IMEI or asset tag accepted by scan or keyboard
2. Entitlement evaluated in **≤ 2 seconds**: manufacturer warranty, extended warranty, protection
   product, AMC/RAMC coverage, or none
3. Result shown as one clear statement with the expiry date and the source of the entitlement
4. **A warranty-type order cannot be created if warranty is not active at the request date**
   *(BRU-SRM-02, hard)* — the block explains why and offers the paid path
5. **An AMC-type order cannot be created unless the device is on an active contract's covered-asset
   list** *(BRU-SRM-03, hard)*
6. An unregistered device must be registered as part of intake *(BRU-SRM-01, hard)*
7. Where an external check is unavailable, the last known status is shown **with its timestamp**, and
   a manual override is possible with a logged reason

---

**US-SRM-003** | Service Centre Agent (R08) | **P0** | W1 | M01, M37 | BO-01
*As a service centre agent, I want to select the service from a structured catalogue so that orders
are consistent and I type as little as possible.*

**AC**
1. Category → brand → model → symptom narrows progressively
2. Fault codes selectable, with a Bengali free-text field for anything not listed
3. Repair level (L1/L2/L3) suggested from the symptom, overridable with a reason
4. **Indicative price shown before the order is confirmed**
5. Delivery mode selectable: walk-in, on-site, pick & drop, workshop, remote

---

**US-SRM-004** | Service Centre Agent (R08) | P1 | W1 | M01, M04 | BO-05
*As a service centre agent, I want to print the job token and internal job card at the counter so
that the customer has proof and the technician has instructions.*
**AC:** print in ≤ 3 s to the configured thermal printer · token carries job number, QR tracking
link, party, device and promised date · **Bengali renders correctly on the thermal printer** ·
a second internal copy prints for the workshop · reprint available from the order.

---

**US-SRM-005** | Service Centre Agent (R08) | **P0** | W1 | M01 | BO-05
*As a service centre agent, I want the SLA promised to the customer calculated by the system so that
I never promise something we cannot deliver.*
**AC:** SLA policy resolved from service type, business line, customer tier and contract · promised
date shown to the customer at intake · **Privilege Gold and Diamond automatically receive priority-1
SLA** *(BRU-SRM-10)* · the clock starts at intake and is visible on the order.

---

**US-SRM-006** | Technician (R10, R11, R12) | **P0** | W2 | M01 | BO-01
*As a technician, I want to record my diagnosis against a guided tree so that I do not miss steps
and the next person understands what I found.*
**AC:** diagnostic template resolved by category, brand, model and symptom · answers captured with
fault coding · **voice-to-text in Bengali** for narrative notes · findings visible to the workshop,
the agent and the customer's status page · template version recorded against the result.

---

**US-SRM-007** | Technician (R10, R11, R12) | **P0** | W2 | M01, M36 | BO-05
*As a technician, I want the estimate drafted for me from the fault code so that I can present a
price to the customer in a minute, not fifteen.*
**AC:** estimate drafted automatically from fault code and standard repair mapping *(AUT-004)* ·
labour, parts, transport and tax itemised · **margin is not shown to the technician** (field-level
permission) · the customer can approve, part-approve or decline on the device · **work cannot start
on an estimate above BDT 5,000 without recorded customer approval** *(BRU-SRM-07, hard)* · above
BDT 25,000 branch manager approval is also required *(BRU-SRM-08, hard)* · an expired estimate must
be re-issued, not extended *(BRU-SRM-13)*.

---

**US-SRM-008** | Technician (R10, R11, R12) | **P0** | W2 | M01, M23 | BO-05
*As a technician, I want the quality checklist enforced before I can close a job so that nothing
leaves half-done.*
**AC:** checklist resolved by category and repair level · **mandatory items must be answered — the
job cannot be completed otherwise** *(BRU-SRM-04, BRU-QMS-01, hard)* · **before/after photographs
are mandatory on every warranty job** *(BRU-SRM-17, hard)* · above BDT 25,000 an independent
second-person QC is required *(BRU-SRM-18, hard)* and the system names who it must not be
*(SOD-07)*.

---

**US-SRM-009** | Branch Manager (R06) | P1 | W1 | M01 | BO-07
*As a branch manager, I want a live board of every order in my branch by state so that I can see
where the work is stuck.*
**AC:** board columns follow the order lifecycle · cards show job number, device, technician, SLA
indicator and age · **overdue cards visually distinct without relying on colour alone** · auto-refresh
without losing scroll position · filter by technician, service type and age.

---

**US-SRM-010** | Operations Director (R05) | P1 | W1 | M01 | BO-05
*As the operations director, I want SLA escalation to fire automatically so that a breach is never
first reported by a customer.*
**AC:** escalation at **50 / 75 / 90 / 100%** of elapsed SLA to defined roles *(AUT-009)* ·
acknowledgement tracked; unacknowledged escalations escalate further · **the SLA clock suspends only
under an approved hold reason and resumes automatically** *(BRU-SRM-15)* · breaches recorded with a
root-cause field.

---

**US-SRM-011** | Service Centre Agent (R08) | P1 | W2 | M01 | BO-05
*As a service centre agent, I want the complete timeline of an order so that I can answer any
customer question accurately.*
**AC:** every state change with timestamp and actor · every customer communication on every channel ·
parts requests and fulfilment · internal notes **marked internal and never exposed externally** ·
exportable as PDF for a dispute.

---

**US-SRM-012** | Quality Manager (R32) | P1 | W2 | M01, M23 | BO-05
*As the quality manager, I want repeat work automatically identified so that rework is measured
rather than absorbed.*
**AC:** a new order for the same device and fault category within 30 days is **automatically flagged
as rework and linked to the original** *(BRU-SRM-06)* · the original technician's manager and quality
are notified *(AUT-011)* · rework rate reported by technician, branch and fault code · reopening a
closed order within the repair-warranty period links it as rework *(BRU-SRM-19)*.

---

**US-SRM-013** | Branch Manager (R06) | P2 | W2 | M01 | BO-05
*As a branch manager, I want uncollected devices chased automatically so that they do not
accumulate in my store room.*
**AC:** reminders at 3, 7, 15 and 30 days *(AUT-012)* · **at 30 days the abandonment process starts
with statutory notice** *(BRU-SRM-16)* · uncollected devices over 30 days reported as a KPI ·
custody and storage location tracked throughout.

---

**US-SRM-014** | Technician (R12), Branch Manager (R06) | P1 | W2 | M01 | BO-05
*As a specialist technician, I want a beyond-economic-repair declaration to require evidence so that
the decision is defensible to the customer.*
**AC:** BER requires photographic evidence **and a second technician's confirmation** *(BRU-SRM-12,
hard)* · the customer is presented with the evidence and the options · disposition routes to
trade-in, return or recycling.

---

**US-SRM-015** | Account Manager (R22) | P1 | W4 | M01, M08 | BO-11
*As an account manager, I want a single site visit to cover many devices so that a corporate client
is not billed for twenty separate visits.*
**AC:** job batch groups many orders for one site and date · per-device outcomes recorded
individually · crew composition and duration estimated · consolidated to one visit record for
billing.

---

**US-SRM-016** | Service Centre Agent (R08) | P2 | W2 | M01 | BO-05
*As a service centre agent, I want to issue a loan device so that the customer is not without
equipment while we repair theirs.*
**AC:** loan device issued from a tracked pool · custody recorded both ways · automatic reminder if
not returned when the repair completes · linked to the originating order.

---

### 6.2 Workshop & Depot Repair (M31 · `WSR` · W2)

**US-WSR-001** | Workshop Supervisor (R09) | P1 | W2 | M31 | BO-01
*As a workshop supervisor, I want a bench board showing every device and how long it has been there
so that nothing is lost or forgotten.*
**AC:** board by bench and by state · **WIP ageing visible on every card** · parts holds shown with
what is awaited · drag **and keyboard/single-pointer equivalent** to reassign a bench (§21.4) ·
capacity and utilisation per bench.

**US-WSR-002** | Workshop Supervisor (R09) | P1 | W2 | M31, M22 | BO-15
*As a workshop supervisor, I want work routed by repair level so that L3 work only reaches a
certified specialist.*
**AC:** L1/L2/L3 routing from the diagnosis · **L3 board-level work may only be assigned to a
workshop with the required equipment and a certified specialist** *(BRU-SRM-14, hard)* · the block
names the missing certification or equipment.

**US-WSR-003** | Specialist Technician (R12) | P1 | W2 | M31 | BO-02
*As a specialist technician, I want everything already tried on this device before I open it so that
I do not repeat someone else's work.*
**AC:** full diagnostic history from prior attempts shown on the bench screen · previous technicians'
notes · parts already replaced · component-level findings recordable for the next specialist.

**US-WSR-004** | Specialist Technician (R12) | P2 | W2 | M31 | BO-05
*As a specialist technician, I want to record test and burn-in results so that a repair is proven
before it goes back to the customer.*
**AC:** test protocol per category · results recorded with duration · burn-in period enforced before
the device can be marked ready · results attached to the service report.

**US-WSR-005** | Workshop Supervisor (R09) | P2 | W2 | M31, M15 | BO-03
*As a workshop supervisor, I want to see which jobs are blocked on parts and what is being done so
that I can give the branch an honest answer.*
**AC:** parts-hold view with the awaited part, source and expected date · network availability shown
*(AUT-007)* · customer-facing revised ETA generated when a hold is placed.

---

### 6.3 Field Service & Dispatch (M02 · `FSM` · W2)

---

**US-FSM-001** | Dispatch Manager (R07) | **P0** | W2 | M02 | BO-02
*As a dispatch manager, I want candidate technicians scored for me so that I assign the whole
morning queue in minutes instead of an hour.*

**AC**
1. Candidates scored on **skill, certification currency, location, current workload, van stock and
   SLA risk**
2. **A technician on leave, off-shift or at capacity is never offered** *(BRU-FSM-01, hard)*
3. A skill match to the required competency is mandatory *(BRU-FSM-02, hard)*
4. Where the top score exceeds the confidence threshold the system **auto-assigns**
   *(BRU-FSM-03)*; otherwise it presents a ranked list
5. **A plain-language explanation is shown for every recommendation** — "certified for Dell, 2.1 km
   away, has the part, 3 jobs today"
6. **Every override requires a reason code** *(BRU-FSM-04, hard)*, which feeds model improvement
7. Assignment to an uncertified technician for brand warranty work is **blocked**
   *(BRU-SRM-09 / BRU-HRM-01, hard)*
8. Scheduling that would breach working-time rules requires approved overtime first
   *(BRU-FSM-10, hard)*
9. The full morning queue is dispatchable in **under 10 minutes**

---

**US-FSM-002** | Dispatch Manager (R07) | **P0** | W2 | M02 | BO-02
*As a dispatch manager, I want a live map of every technician so that I can answer "where is he?"
without phoning anyone.*
**AC:** positions stream with **≤ 5 s latency from GPS emission** · status per technician (travelling,
on site, idle, off shift) · **GPS is captured only during working hours and while on duty**
*(BRU-FSM-05)* — and technicians are told this in the app · dispatch board refresh **≤ 1 s for 500
open jobs**.

---

**US-FSM-003** | Dispatch Manager (R07) | P1 | W2 | M02 | BO-02
*As a dispatch manager, I want to insert an emergency job and have the schedule re-optimise so that
I do not have to rebuild the day by hand.*
**AC:** re-optimisation on insertion · **an emergency may displace lower-priority work but never an
SLA-critical job already at risk** *(BRU-FSM-11)* · affected technicians and customers notified
automatically with revised ETAs · the dispatcher sees what changed before committing.

---

**US-FSM-004** | Senior Technician (R10) | **P0** | W2 | M02 | BO-02
*As a field technician, I want my whole day, in order, on my phone before I leave home so that I can
plan and carry the right parts.*
**AC:** route optimised overnight and published *(AUT-013)* · job list **cached and available offline
by 07:30** · each job shows customer, address, device, symptom, promised window and required parts ·
manual re-order permitted with a reason · **loads in ≤ 8 s cold on 3G**.

---

**US-FSM-005** | Senior Technician (R10) | **P0** | W2 | M02 | BO-02
*As a field technician, I want the device's full history before I arrive so that I do not ask the
customer questions we already know the answer to.*
**AC:** device history, previous notes, parts previously fitted and open contract entitlement
available **offline**, downloaded at assignment · brand service documentation linked from M61,
offline · a suggested parts checklist for the visit.

---

**US-FSM-006** | Senior Technician (R10) | **P0** | W2 | M02 | BO-05
*As a field technician, I want arrival detected automatically so that the customer is told without
me having to do anything.*
**AC:** geofence arrival detection with a manual confirm · timestamp and GPS recorded · customer
notified automatically · **a job cannot be marked arrived outside the customer's geofence without an
exception reason** *(BRU-FSM-06)* · the on-site timer starts at arrival.

---

**US-FSM-007** | Senior Technician (R10) | **P0** | W2 | M02, M15 | BO-03
*As a field technician, I want to consume parts by scanning them so that stock is right without me
filling in a form.*
**AC:** barcode/QR scan consumes from **van stock** · serialised parts capture the serial
*(BRU-INV-08)* · **stock cannot be issued against an unapproved paid repair** *(BRU-INV-01, hard)* ·
**brand-supplied warranty parts cannot be consumed on a non-warranty job** *(BRU-WTY-04, hard)* ·
unused parts returned by scan · works fully offline.

---

**US-FSM-008** | Senior Technician (R10) | **P0** | W2 | M02 | BO-01
*As a field technician, I want to capture evidence quickly and have it rejected immediately if it is
no good, so that I do not find out at the office.*
**AC:** before/after photographs with **GPS and timestamp** · **blurred, dark or duplicate images
rejected at capture** with a plain-language reason · short video and Bengali voice notes supported ·
document scan · all capture works offline with local encryption.

---

**US-FSM-009** | Senior Technician (R10) | **P0** | W2 | M02, M20 | BO-06
*As a field technician, I want to take the customer's signature and payment on my phone so that the
job is finished when I leave.*
**AC:** e-signature on device · payment by bKash, Nagad, card or cash · receipt issued immediately ·
**cash collected must reconcile to the branch cash book by end of shift** *(BRU-FSM-07, hard)* ·
where offline, payment intent queues and reconciles on sync.

---

**US-FSM-010** | Junior Technician (R11) | P1 | W2 | M02, M61 | BO-02
*As a junior technician, I want to escalate to a senior without leaving the customer's side so that
I look competent and the problem still gets solved.*
**AC:** one-tap escalation carrying job, diagnosis, photos and notes · senior receives the full
context — **the junior does not have to explain from scratch** · escalation state visible to dispatch ·
in-app messaging with dispatch and workshop.

---

**US-FSM-011** | Senior Technician (R10) | P1 | W2 | M02, M57 | BO-02
*As a field technician, I want to see what I have earned today so that the app gives me something,
not just takes from me.*
**AC:** jobs completed, hours, incentive accrued and earnings-to-date visible in the app ·
**a technician sees their own detail only** (T4) · updated same day as job closure · scorecard shows
first-time fix, on-time arrival and CSAT.

---

**US-FSM-012** | Senior Technician (R10) | P1 | W2 | M02 | BO-02
*As a field technician, I want a failed visit recorded properly so that I am not blamed for someone
else's absence.*
**AC:** **geotagged photographic evidence is mandatory before a failed visit can be recorded**
*(BRU-FSM-09, hard)* · reason coded (absent, refused, wrong address, unsafe) · customer notified and
offered rescheduling · charge rules applied per policy.

**US-FSM-013** | Dispatch Manager (R07) | P2 | W2 | M02 | BO-02
*As a dispatch manager, I want to hand a job from one technician to another mid-flight so that a
breakdown or illness does not cost the customer their appointment.*
**AC:** handover transfers full context and custody · both technicians and the customer are notified ·
the original technician's time is preserved for costing.

**US-FSM-014** | Ops Director (R05) | P2 | W6 | M02, M26 | BO-02
*As the operations director, I want to see how good our assignment decisions actually are so that
automation earns trust before it earns autonomy.*
**AC:** report on auto-assignment rate, dispatcher override rate and reasons, travel efficiency and
capacity utilisation · **dispatcher agreement rate is the gate on raising the confidence threshold**
(≥ 88% at Gate 6).

---

### 6.4 Service Logistics & Reverse Logistics (M03 · `LOG` · W3)

**US-LOG-001** | Rider (R16) | **P0** | W3 | M03 | BO-01
*As a rider, I want my whole manifest in order so that I am not calling the office to ask where to
go next.*
**AC:** daily manifest optimised, with sequence · reorder permitted within constraints · works fully
offline · **large targets and high contrast, usable with gloves in sunlight** (§21).

**US-LOG-002** | Rider (R16) | **P0** | W3 | M03 | BO-01
*As a rider, I want proof of every handover so that I am never blamed without evidence.*
**AC:** **no custody transfer without a scan and identity capture from both parties**
*(BRU-LOG-01, hard)* · item photographs, seal number, GPS and timestamp · **customer OTP and
signature** · **a consignment cannot be closed without proof of delivery** *(BRU-LOG-02, hard)* ·
POD capture completeness **100%**.

**US-LOG-003** | Rider (R16) | P1 | W3 | M03, M50 | BO-06
*As a rider, I want my cash to reconcile in one screen at the end of my shift so that the day ends
cleanly.*
**AC:** cash collected per delivery listed · reconciliation per rider per shift ·
**zero tolerance for unexplained variance** *(BRU-LOG-06, hard)* · handover to the branch cash drawer
recorded.

**US-LOG-004** | Logistics Coordinator (R15) | P1 | W3 | M03 | BO-01
*As a logistics coordinator, I want one dashboard of everything moving so that I can act on
exceptions instead of chasing status.*
**AC:** pending, in transit, delivered and exception views in real time · assign to internal rider or
courier partner from the same screen · reschedule without a phone call · SLA per consignment.

**US-LOG-005** | Logistics Coordinator (R15) | P1 | W3 | M03 | BO-01
*As a logistics coordinator, I want exceptions handled by rule so that failed deliveries do not sit
in limbo.*
**AC:** exception reasons coded · **re-attempt per policy, then return to origin with charge rules
applied** *(BRU-LOG-08)* · **a seal break or weight discrepancy raises an incident and blocks onward
movement pending review** *(BRU-LOG-04, hard)* · customer rescheduling from the tracking link.

**US-LOG-006** | Logistics Coordinator (R15) | P1 | W3 | M03 | BO-10
*As a logistics coordinator, I want restricted items controlled so that we do not put a lithium
battery on an uncertified vehicle.*
**AC:** restricted items flagged at booking · **only a rider or courier certified for that item class
may be assigned** *(BRU-LOG-05, hard)* · handling instructions shown to the rider · high-value
consignments require dual signature and insurance flagging *(BRU-LOG-03)*.

---

### 6.5 Branch & Front-Desk Operations (M04 · `FRD` · W1)

**US-FRD-001** | Service Centre Agent (R08) | **P0** | W1 | M04 | BO-05
*As a service centre agent, I want a token queue so that customers are served in order and can see
where they are.*
**AC:** token issued at arrival with an estimated wait · queue display for the waiting area ·
multi-counter routing by capability · queue metrics per counter and agent.

**US-FRD-002** | Cashier (R29) | **P0** | W1 | M04, M50 | BO-06
*As a cashier, I want my drawer to open and close with the shift so that my cash is never in dispute.*
**AC:** drawer opened against a named shift · every movement recorded · **the shift must be
reconciled and closed daily; an unclosed shift blocks the next opening** *(BRU-FIN-10, hard)* ·
variance escalated to the branch manager.

**US-FRD-003** | Service Centre Agent (R08) | P1 | W1 | M04 | BO-05
*As a service centre agent, I want to hand a device back with proof so that a later dispute can be
settled from the record.*
**AC:** handover requires identity verification · condition photographs at handover · customer
signature · gate pass printed · custody closed on the order.

**US-FRD-004** | Branch Manager (R06) | P2 | W1 | M04 | BO-07
*As a branch manager, I want counter throughput measured so that I can staff the counter properly.*
**AC:** throughput, handling time and queue metrics per counter and per agent · peak-hour view ·
**intake time reported against the 3-minute target**.

**US-FRD-005** | Customer (R36) | P2 | W2 | M04 | BO-05
*As a customer, I want a self-service kiosk so that I can check status or take a token without
queueing for an agent.*
**AC:** kiosk issues tokens, checks status and supports appointment check-in · **Bengali default,
large type, high contrast** · no personal data displayed beyond what the customer has authenticated
to see.

---

### 6.6 Remote Support & Managed Services (M05 · `RMS` · W5) ★

**US-RMS-001** | Remote Support Engineer (R13) | P1 | W5 | M05 | BO-11
*As a remote support engineer, I want alerts correlated and de-duplicated so that alerts still mean
something at 2 a.m.*
**AC:** alert rules per asset class and client · correlation and suppression configurable ·
noise-reduction effectiveness measured · **an alert with no defined action is removed, not ignored**.

**US-RMS-002** | Remote Support Engineer (R13) | P1 | W5 | M05, M08 | BO-11
*As a remote support engineer, I want one click from an alert to the asset, its history and its
contract so that I know what I am allowed to do before I do it.*
**AC:** alert links to monitored asset, service history and contract entitlement · SLA policy
resolved from the contract · **out-of-scope work is flagged as separately billable, never silently
absorbed** *(BRU-CTR-02, hard)*.

**US-RMS-003** | Remote Support Engineer (R13) | P1 | W5 | M05, M29 | BO-10
*As a remote support engineer, I want to start a remote session with consent captured so that both
we and the client are protected.*
**AC:** session launched from the ticket · **customer consent captured and recorded before the
session starts** · session recorded and retained per policy · actions taken logged against the ticket.

**US-RMS-004** | Remote Support Engineer (R13) | P1 | W5 | M05 | BO-11
*As a remote support engineer, I want SLA burn-down visible per ticket so that I triage by risk, not
by whoever shouted loudest.*
**AC:** SLA target and remaining time per ticket · queue sortable by SLA risk · **service credits
calculated automatically from measured breach** *(BRU-CTR-08)*.

**US-RMS-005** | Account Manager (R22) | P1 | W5 | M05, M25 | BO-11
*As an account manager, I want the client's monthly service report generated so that I stop building
it by hand the night before the review.*
**AC:** estate health, incidents, alert history, patch compliance and SLA attainment · client-scoped
data only · scheduled and delivered automatically · available to the client on P04.

**US-RMS-006** | Remote Support Engineer (R13) | P2 | W6 | M05 | BO-11
*As a remote support engineer, I want patching orchestrated so that a thousand endpoints do not need
a thousand decisions.*
**AC:** patch inventory per endpoint · maintenance windows honoured · staged rollout with rollback ·
patch compliance reported per client.

**US-RMS-007** | Corporate Services Head | P2 | W6 | M05, M54 | BO-11
*As the corporate services head, I want cost-to-serve per client so that I know which MSP contracts
are actually profitable.*
**AC:** labour, remote and field effort attributed per client · contract value against delivered cost ·
**contracts running at negative margin flagged before renewal**.

---

### 6.7 Data Services & Secure Data Handling (M06 · `DTS` · W6) ★

---

**US-DTS-001** | Data Services Technician (R14) | **P0** | W6 | M06, M29 | BO-10
*As a data services technician, I want custody of every piece of media recorded unambiguously so
that the Company can prove where a customer's data has been at every moment.*

**AC**
1. Media taken into custody against a named case, with **dual control** — two named people
2. Every custody transfer records both parties, timestamp, GPS and evidence
3. **Access is restricted to the team assigned to that case; every access is logged**
   *(BRU-SEC-03, hard)*
4. **Step-up authentication is required to open a case** *(BRU-SEC-02)*
5. The recovered-data index is **S3 restricted, encrypted with per-case keys and held in the
   Bangladesh-resident store** (NFR-086)
6. **Zero custody exceptions** is the wave-gate criterion — any exception is an incident

---

**US-DTS-002** | Data Services Technician (R14) | **P0** | W6 | M06, M24 | BO-10
*As a data services technician, I want to issue a destruction certificate that a corporate client's
security team will accept so that our certificate is worth something.*
**AC:** destruction executed to the **approved technique standard named in the media sanitisation
programme** (DEP-35) · certificate carries method, standard, operator, witness, date, device
identity and verification result · **retrievable for the retention period** · accepted as evidence
by P04 corporate compliance download.

**US-DTS-003** | Data Services Technician (R14) | **P0** | W6 | M06 | BO-10
*As a data services technician, I want recovered data purged automatically at the agreed date so
that we never hold customer data longer than we said we would.*
**AC:** purge date set at case creation · **purge executes automatically unless a documented hold
applies** *(BRU-SEC-04, hard)* · purge certificate issued · **recovered customer data is never used
as training data** *(BRU-AIM-03, hard)*.

**US-DTS-004** | Customer (R36) | P2 | W6 | M06 | BO-05
*As a customer, I want to see my data-recovery case status without phoning, but without my case
detail being exposed.*
**AC:** status only — **case content is never exposed on the portal** · communication controls
restrict what may be said and by whom *(FR-DTS-029)* · certificates downloadable on completion.

**US-DTS-005** | Technical Services Head | P2 | W6 | M06 | BO-10
*As the technical services head, I want compliance reporting on custody, access, retention and
destruction so that I can answer an audit without assembling it by hand.*
**AC:** report on custody chain, access log, retention status and destruction certificates per period ·
exceptions highlighted · exportable as an evidence pack.

---

## 7. USER STORIES — CATEGORY B: CUSTOMER ENGAGEMENT & EXPERIENCE

### 7.1 Customer & Party Master (M33 · `CPM` · W1) ★

---

**US-CPM-001** | Service Centre Agent (R08), Contact Centre Agent (R34) | **P0** | W1 | M33 | BO-10
*As anyone who creates a customer record, I want consent and the transparency notice captured at the
point of capture so that our processing is lawful from the first moment.*

**AC**
1. **A transparency notice is presented before or during capture**, stating data categories,
   purposes, risks, retention and third-party transfers (NFR-092)
2. Notice text is available in **Bengali and English** (DEP-34)
3. **Consent is clear, explicit, specific and freely given**, recorded **per processing purpose**
   (NFR-090, NFR-091)
4. Sensitive personal data requires the **heightened specific-consent standard** unless a legitimate
   ground applies
5. Consent, purpose, timestamp, channel and the notice version are all recorded
6. **Refusing optional consent does not block the service** — operational processing continues on
   its stated lawful ground
7. Withdrawal is available through a **simplified procedure** at any time (NFR-093)

---

**US-CPM-002** | Data Subject (any customer, employee or party) | **P0** | W1 | M33, M29 | BO-10
*As a data subject, I want to exercise my rights over my personal data without a fight.*
**AC:** access and portability produce a structured export · **rectification is applied and
controllers notified within 30 days** · erasure applied on purpose cessation, consent withdrawal,
unlawful processing or legal requirement · **where a statutory retention obligation overrides
erasure, that is explained rather than silently ignored** · consent withdrawal is simplified · the
request and its outcome are retained as a processing record for **≥ 5 years** (NFR-095).

**US-CPM-003** | Service Centre Agent (R08) | **P0** | W1 | M33 | BO-05
*As a service centre agent, I want one record per customer even when they have used us under three
different phone numbers.*
**AC:** duplicate detection on phone, NID, email and device serial · merge preview shows what will
change · **merge is reversible and fully audited** · downstream references follow the merge ·
a single party may hold **multiple roles simultaneously** — customer, seller, employee, referrer.

**US-CPM-004** | Account Manager (R22) | P1 | W1 | M33 | BO-08
*As an account manager, I want corporate hierarchy modelled so that a group, its companies, its
sites and its departments roll up properly.*
**AC:** group → company → division → site hierarchy · contact roles (requester, approver, finance,
technical) with matching portal permissions · **the client's own internal approval chain is
configurable** · activity, spend and satisfaction roll up across the group.

**US-CPM-005** | Marketing Manager (R23) | **P0** | W1 | M33 | BO-10
*As a marketing manager, I want do-not-contact honoured absolutely so that we never become the
company that ignores a customer's wishes.*
**AC:** preferred language and channel recorded and **honoured everywhere** · do-not-contact honoured
**absolutely**, including operational messages where lawful to suppress · suppression applied at
send time, not at list build.

**US-CPM-006** | Data Steward (R39) | P1 | W2 | M33, M64 | BO-17
*As a data steward, I want to see how good our customer data actually is so that I can fix it rather
than guess.*
**AC:** completeness, duplication and staleness scored and trended · stewardship tasks routed to
owners · **residency classification carried on every field and enforced at write time** (NFR-086a).

---

### 7.2 CRM & Account Management (M07 · `CRM` · W1/W4)

**US-CRM-001** | Contact Centre Agent (R34) | **P0** | W4 | M07 | BO-05
*As a contact centre agent, I want the whole customer in front of me before I speak.*
**AC:** Customer 360 loads in **≤ 2 s** · devices, open orders, contracts, entitlements, invoices,
dues, loyalty and full cross-channel conversation history · a chronological relationship timeline.

**US-CRM-002** | Account Manager (R22) | P1 | W4 | M07 | BO-08
*As an account manager, I want my accounts, their health and their next action in one place.*
**AC:** account plan, team assignment, activity history · health indicators · renewal and QBR
scheduling · corporate roll-up.

**US-CRM-003** | Sales Manager (R21) | P1 | W4 | M07 | BO-08
*As a sales manager, I want a pipeline I can trust.*
**AC:** leads and opportunities with source, stage, value and probability · conversion measured by
source · **acquisition source and cost recorded per customer**.

**US-CRM-004** | Finance Manager (R26) | P1 | W4 | M07 | BO-06
*As a finance manager, I want fraud and non-payment flags visible so that we stop repeating the same
loss.*
**AC:** blacklist and fraud flags with controlled visibility · reason and approver recorded · flag
surfaces at intake and at credit decisions · **flags are never visible on external portals**.

---

### 7.3 Loyalty, Membership & Rewards (M10 · `LOY` · W2)

**US-LOY-001** | Customer (R36) | P1 | W2 | M10 | BO-08
*As a Privilege member, I want my benefit applied automatically so that I never have to ask for it.*
**AC:** tier resolved at pricing · **discount applies to labour only — never to parts, consumables or
transport** *(BRU-WTY-06)* · benefit shown as a line on the estimate and the invoice · Gold and
Diamond receive priority-1 SLA automatically.

**US-LOY-002** | Customer (R36) | P1 | W2 | M10 | BO-08
*As a customer, I want to see and use my points without arithmetic.*
**AC:** points balance, history and expiry visible · redemption at checkout and at the counter ·
wallet and voucher balances · **the loyalty liability is accounted, not just displayed**.

**US-LOY-003** | Customer (R36) | P2 | W2 | M10 | BO-08
*As a customer, I want to refer a friend and actually receive the reward.*
**AC:** referral link and code generated per customer · **attribution is permanent** · both parties
credited on conversion *(AUT-030)* · reward visible in the wallet.

**US-LOY-004** | Marketing Manager (R23) | P2 | W2 | M10 | BO-08
*As a marketing manager, I want to run a promotion without engineering help.*
**AC:** voucher and offer rules configured without code · eligibility, limits and expiry enforced ·
redemption tracked · cost attributed to the campaign.

---

### 7.4 Customer Experience, Feedback & Complaints (M34 · `CXM` · W4) ★

**US-CXM-001** | Customer (R36) | P1 | W4 | M34 | BO-05
*As a customer, I want to rate the service in a way that takes ten seconds.*
**AC:** survey triggered after a configured delay *(AUT-010)* · multi-parameter rating of service and
technician · **Bengali by default, one screen, no login required** · optional free text with voice
input.

**US-CXM-002** | Customer Service Manager | **P0** | W4 | M34, M23 | BO-05
*As the customer service manager, I want a complaint to have a defined path so that it is resolved,
not absorbed.*
**AC:** intake from any channel · taxonomy and severity · SLA and escalation · **root cause
recorded** · **a complaint cannot be closed without confirming the outcome with the customer**
*(BRU-QMS-04, hard)* · linked non-conformance where the cause is systemic.

**US-CXM-003** | Ops Director (R05) | P1 | W4 | M34, M25 | BO-05
*As the operations director, I want CSAT and NPS by branch, technician and service type so that I
act on evidence.*
**AC:** CSAT, NPS and CES captured at defined touchpoints · segmentation by branch, technician,
service type and business line · trend and alerting on deterioration.

**US-CXM-004** | Marketplace Operations (R24) | P1 | W7 | M34, M12 | BO-12
*As marketplace operations, I want reviews that mean something.*
**AC:** **only a customer with a completed transaction may leave a review** *(BRU-ECM-02, hard)* ·
moderation before publication · the seller may respond once · review feeds the seller score.

---

### 7.5 Omnichannel Contact Centre (M27 · `CCE` · W4) ★

---

**US-CCE-001** | Contact Centre Agent (R34) | **P0** | W4 | M27 | BO-16
*As a contact centre agent, I want one queue for every channel so that I am not watching six
different systems.*

**AC**
1. Voice, chat, WhatsApp, email, SMS and social in **one prioritised queue**
2. Priority and SLA visible per contact
3. Presence and capacity managed by the agent
4. **Automatic Customer 360 screen-pop on identification** — before the agent speaks
5. Full cross-channel conversation history on the same screen
6. **Fewer than three screen switches per contact**

---

**US-CCE-002** | Contact Centre Agent (R34) | **P0** | W4 | M27, M01 | BO-16
*As a contact centre agent, I want to do what the customer asked without leaving the conversation.*
**AC:** create a service order, reschedule, quote, take payment, renew a contract or raise a
complaint **inside the conversation** · jump to any ERP screen and return with the conversation
intact · disposition coding mandatory at wrap-up.

**US-CCE-003** | Contact Centre Supervisor (R35) | P1 | W4 | M27 | BO-16
*As a supervisor, I want to see and support my team live.*
**AC:** live queue and agent status · service-level monitoring · **barge-in and whisper on live
calls** · recording playback, quality scoring forms and coaching notes.

**US-CCE-004** | Every module owner | **P0** | W1 † | M27 | BO-05
*As the owner of any module that must tell a customer something, I want one notification service so
that we do not build six different send paths.*
**AC:** one template engine, one delivery service, one preference model, one log · SMS, WhatsApp,
email, push and in-app inbox · delivery tracked and reported.

> **† Sequencing decision Q-05a.** M27 is scheduled for W4 but **its notification service is needed
> from W1**. Every module from Wave 1 needs to notify customers. If M27 arrives at W4, each earlier
> module builds its own send path — recreating exactly the fragmentation this programme exists to
> remove. **Decision required before Wave 1 build.**

**US-CCE-005** | Customer (R36) | P1 | W4 | M27 | BO-05
*As a customer, I want to choose how you contact me, and be listened to.*
**AC:** channel preferences per notification category · **quiet hours honoured for non-urgent
messages** · marketing opt-out honoured absolutely; operational messages continue where lawful ·
in-app inbox holds everything sent.

---

### 7.6 Conversational AI (M32 · `CAI` · W4) ★

**US-CAI-001** | Customer (R36) | P1 | W4 | M32 | BO-05
*As a customer, I want to ask a question in Bengali at midnight and get a real answer.*
**AC:** **Bengali-first assistant**, English on request · answers grounded in live ERP data —
order status, warranty, contract, invoice · **the assistant never invents a fact about the
customer's account** · handoff to a human carries the full context.

**US-CAI-002** | Customer (R36) | P1 | W4 | M32, M29 | BO-16
*As a customer, I want the assistant to actually do things, not just talk.*
**AC:** authenticated actions only — book, reschedule, check status, request a callback ·
**authentication required before any account-specific action** · every action logged as if performed
by a human agent · **a recommendation with material financial consequence requires human
confirmation** *(BRU-AIM-01, hard)*.

**US-CAI-003** | Contact Centre Agent (R34) | P2 | W4 | M32 | BO-16
*As an agent, I want the assistant helping me, not replacing me.*
**AC:** suggested responses and next-best-action while the conversation is live · knowledge article
recommendations · the agent may always override; overrides are logged.

> **Dependency Q-01.** M32 depends on M61 Knowledge Management, currently scheduled two waves later
> (W6). **Without a knowledge base the assistant can answer transactional questions from live data
> but not "how do I" or "why is this happening".** Either M61 core content moves to W4, or M32
> launches with a reduced intent scope. Decision required.

---

### 7.7 Marketing & Campaigns (M35 · `MKT` · W5) ★

**US-MKT-001** | Marketing Manager (R23) | P2 | W5 | M35 | BO-08
*As a marketing manager, I want to segment on what customers have actually done.*
**AC:** segmentation on service history, spend, device estate, tier, geography and lapse ·
**consent and do-not-contact applied at build and again at send** · segment size shown before launch.

**US-MKT-002** | Marketing Manager (R23) | P2 | W5 | M35, M27 | BO-08
*As a marketing manager, I want a multi-step journey across channels without engineering help.*
**AC:** journeys configured without code · SMS, WhatsApp, email and push · entry and exit criteria ·
frequency capping · results measured per step.

**US-MKT-003** | CCO (R04) | P2 | W5 | M35, M25 | BO-08
*As the CCO, I want honest campaign attribution.*
**AC:** revenue attributed to campaigns **only where a causal mechanism is documented** · campaign
cost captured · ROI reported per campaign; **unattributable growth is reported as unattributable**.

---

## 8. USER STORIES — CATEGORY C: COMMERCIAL, PRICING & REVENUE

### 8.1 Catalogue & Pricing (M37 `CAT` W1 · M11 `PRC` W3/W7)

**US-CAT-001** | CCO (R04) | **P0** | W1 | M37 | BO-08
*As the CCO, I want everything we sell defined in one catalogue so that nothing is sold that we have
not defined.*
**AC:** services, kits, parts, protection plans, rental SKUs, refurbished grades and subscription
plans in one structure · repair bills of material and standard times · applicability by category,
brand and model · **a price never lives on a catalogue item; a catalogue item never carries a
discount**.

**US-PRC-001** | Sales Manager (R21) | P1 | W3 | M11 | BO-08
*As a sales manager, I want one place where every price lives so that we stop arguing about which
rate card is current.*
**AC:** rate cards by category, brand, model and repair type · **separate warranty and
out-of-warranty pricing** · customer-specific and segment price books · effective dating and full
revision history · **every other module requests a price; none holds one**.

**US-PRC-002** | Branch Manager (R06) | **P0** | W3 | M11 | BO-08
*As a branch manager, I want discount authority enforced so that margin is not given away at the
counter.*
**AC:** thresholds per §4.6 enforced at the point of discount · **margin visible to the approver, not
to the technician** · NTE limits for corporate accounts route for approval automatically · every
override logged with reason and approver.

**US-PRC-003** | CCO (R04) | P2 | W7 | M11, M26 | BO-08
*As the CCO, I want dynamic pricing with guard rails so that we never surprise a customer or breach
our own floor.*
**AC:** rules with hard floors and ceilings · **no model output may cross a business guard rail**
*(BRU-AIM-02, hard)* · **a price is fixed at acceptance; any change requires re-approval** ·
**complete decision audit** — what price, why, on what inputs.

---

### 8.2 Quotation, Estimation & Tender (M36 · `QTE` · W3)

**US-QTE-001** | Customer (R36) | **P0** | W3 | M36 | BO-05
*As a customer, I want to understand and decide on an estimate without a phone call.*
**AC:** itemised estimate delivered on the customer's preferred channel · **approve, part-approve or
decline** on screen · e-signature · validity and expiry shown · reminders at 24 h and 48 h;
auto-expire at the limit *(AUT-005)*.

**US-QTE-002** | Sales Manager (R21) | P1 | W3 | M36 | BO-08
*As a sales manager, I want versioned quotations so that we always know what the customer actually
agreed to.*
**AC:** versioning with a visible difference between versions · approval workflow by value ·
**one quotation flows to one invoice; variance requires a documented reason**.

**US-QTE-003** | Account Manager (R22) | P2 | W3 | M36 | BO-08
*As an account manager, I want to respond to a corporate tender from the system.*
**AC:** tender/RFP structure with line items and terms · competitive bidding and counter-bid ·
submission pack assembled · win/loss recorded with reason.

---

### 8.3 Contract Lifecycle (M08 · `CTR` · W4)

---

**US-CTR-001** | Account Manager (R22) | **P0** | W4 | M08 | BO-08
*As an account manager, I want to create any of our fourteen contract products from a template so
that a new product family never needs a developer.*

**AC**
1. Templates cover all **14 product families** — RAMC (6 packages), Commercial AMC, IT Infrastructure
   AMC, Healthcare Equipment AMC, Specialty Equipment AMC, Managed Services (6 types), Mobile &
   Appliance Service (5 types), rental master agreements, marketplace seller agreements, brand
   partner agreements
2. **A contract cannot be activated without at least one covered asset or seat, defined entitlements,
   a billing frequency and approval** *(BRU-CTR-01, hard)*
3. **Healthcare equipment contracts require calibration scheduling as a mandatory element**
   *(BRU-CTR-07, hard)*
4. **RAMC price derives from the number and type of registered appliances — never a flat fee**
   *(BRU-CTR-06)*
5. Activation generates the **full preventive-maintenance schedule for the term** *(AUT-016)*
6. **A new product family is configured, not coded** — validated against all 14 before the Wave 4 gate

---

**US-CTR-002** | Account Manager (R22) | **P0** | W4 | M08 | BO-08
*As an account manager, I want entitlement consumption visible so that neither we nor the client is
surprised at renewal.*
**AC:** entitlement drawn down per service order · balance visible to the client on P04 ·
**over-consumption is blocked or flagged for billing per configuration — it is never invisible**
*(BRU-CTR-04, hard)* · **service outside contract scope is billed separately, never silently
absorbed** *(BRU-CTR-02, hard)*.

**US-CTR-003** | Account Manager (R22) | P1 | W4 | M08 | BO-08
*As an account manager, I want renewals to start themselves 90 days out.*
**AC:** notifications at **90 / 60 / 30 / 15 days** to client and account owner *(AUT-015)* ·
**renewal quotation generated automatically at 60 days** · escalation at 15 days ·
**on expiry, all future scheduled work orders are cancelled and the customer notified**
*(BRU-CTR-03)*.

**US-CTR-004** | CCO (R04) | P1 | W4 | M08, M54 | BO-08
*As the CCO, I want contract profitability continuously, not at renewal.*
**AC:** revenue against delivered cost per contract, updated continuously · **negative-margin
contracts flagged before the renewal conversation** · target: under 3% of contracts negative.

**US-CTR-005** | Corporate Portal User (R37) | P1 | W4 | M08 | BO-11
*As a corporate client, I want to see my SLA performance and the credits I have earned.*
**AC:** real-time SLA status per request · breach history · **service credits calculated
automatically from measured breach** *(BRU-CTR-08)*; manual credits require CFO approval.

---

### 8.4 Warranty, Protection Plans & Claims (M09 · `WTY` · W4)

---

**US-WTY-001** | Warranty Claims Officer (R28) | **P0** | W4 | M09 | BO-04
*As a warranty claims officer, I want the claim created and the evidence assembled for me so that
nothing is lost between the job and the brand.*

**AC**
1. **A claim is created automatically within 24 hours of a warranty work order closing**
   *(BRU-WTY-02, AUT-018)*
2. The evidence pack assembles automatically: before/after photographs, diagnosis, parts replaced,
   serial, **technician certification** and purchase proof
3. Completeness is **validated against that brand's rule set before submission**
4. **A claim cannot be submitted without a completed work order, device serial, at least one
   before-photo, a technician diagnosis and the replaced-parts list** *(BRU-WTY-01, hard)*
5. Where evidence is missing, the officer receives **a specific checklist of what is missing**, not a
   generic error
6. **Duplicate claims for the same serial and fault within 90 days are blocked** *(BRU-WTY-03, hard)*
7. Target: **95% submitted within 72 hours**

---

**US-WTY-002** | Warranty Claims Officer (R28) | **P0** | W4 | M09 | BO-04
*As a warranty claims officer, I want one pipeline with ageing per brand so that nothing quietly
expires.*
**AC:** pipeline by brand and state with ageing · **a claim approaching the brand's submission window
is escalated as revenue leakage before it expires** *(BRU-WTY-08)* · rejection reasons analysed;
recurring reasons raise a non-conformance in M23.

**US-WTY-003** | Brand Partner (R38) | P1 | W4 | M09 | BO-04
*As a brand partner, I want to decide a claim with the evidence in front of me.*
**AC:** claim received with the complete evidence pack · approve, part-approve, reject with reason,
or request more information · bulk actions · decision and reason returned automatically to 1000FiX.

**US-WTY-004** | Finance Manager (R26) | **P0** | W4 | M09, M53 | BO-04
*As a finance manager, I want remittances matched to claims so that I know what we are actually owed.*
**AC:** remittance advice uploaded or received; **matched automatically to claims** *(AUT-021)* ·
unmatched routed to a manual queue · **claims valued in the agreed currency at the rate prevailing on
the service completion date** *(BRU-WTY-05)* · leakage reported continuously.

**US-WTY-005** | Service Centre Agent (R08) | P1 | W4 | M09 | BO-08
*As a service centre agent, I want to sell a protection product at the counter.*
**AC:** all **7 protection product families** sellable · **a product cannot be sold on a device that
fails the eligibility assessment** *(BRU-WTY-07, hard)* · coverage, exclusions and price shown to the
customer before purchase · policy issued digitally.

**US-WTY-006** | Warranty Claims Officer (R28) | P2 | W4 | M09 | BO-04
*As a warranty claims officer, I want to run a recall campaign as a batch.*
**AC:** affected serials identified from the registry · batch of service orders created ·
customer outreach automated · completion tracked and reported to the brand.

---

### 8.5 Subscription & Recurring Revenue (M39 · `SUB` · W4) ★

**US-SUB-001** | Finance Manager (R26) | P1 | W4 | M39 | BO-08
*As a finance manager, I want recurring billing to run itself and tell me when it does not.*
**AC:** billing on the contract's cycle · **a missed cycle raises an exception — never a silent skip**
*(BRU-BIL-02, hard)* · proration on mid-cycle change · usage rated where applicable.

**US-SUB-002** | Customer (R36) | P1 | W4 | M39 | BO-08
*As a subscriber, I want to change or cancel my plan without phoning.*
**AC:** plan change with proration shown before confirmation · cancellation with notice period
applied · next charge date and amount always visible.

**US-SUB-003** | CFO (R03) | P2 | W4 | M39 | BO-08
*As the CFO, I want MRR, ARR and churn measured consistently.*
**AC:** MRR/ARR by product family and segment · churn and its reasons · expansion and contraction
separated.

---

### 8.6 E-Commerce & Marketplace (M38 `ECM` W7 · M12 `MKP` W7 · M40 `PCM` W7) ★

**US-ECM-001** | Customer (R36) | P1 | W7 | M38 | BO-09
*As a customer, I want to buy a part, an accessory or a refurbished device online as easily as I book
a service.*
**AC:** browse, cart, checkout, fulfilment and returns · shares identity, catalogue, stock and
settlement with the ERP · **stock cannot be sold below available quantity** *(BRU-ECM-10, hard)* ·
refurbished listings show grade, **battery health and known defects** *(BRU-TRF-04, hard)*.

---

**US-MKP-001** | Marketplace Seller (R38) | **P0** | W7 | M12 | BO-12
*As an external engineer, I want to register and be told clearly what I must provide before I can
start earning.*

**AC**
1. Registration as freelance engineer or shop; **phone and email verified by OTP**
2. Documents required and explained: **NID, trade licence, references, work-sample images**
3. Identity verification and business-registry check run automatically
4. Agreement signed digitally; registration fee paid where applicable; **expiry date set**
5. **A seller cannot transact until documents are verified, the agreement is signed and an
   administrator has approved** *(BRU-ECM-01, hard)*
6. **A seller cannot list in a category without a verified qualification** *(BRU-ECM-07, hard)*
7. **Registration expiry suspends the seller automatically until renewed** *(BRU-ECM-08)*
8. The whole flow works on a mid-range Android in **Bengali**

---

**US-MKP-002** | Marketplace Seller (R38) | P1 | W7 | M12 | BO-12
*As a seller, I want to see jobs I can actually win and bid on them.*
**AC:** broadcast filtered to the seller's verified categories, area and score · quotation and
counter-bid · award notification · **customer contact data visible only for an awarded job and only
for a defined period after completion** *(BRU-ECM-05, EA-04)*.

**US-MKP-003** | Marketplace Seller (R38) | **P0** | W7 | M12, M53 | BO-12
*As a seller, I want to understand exactly why I was paid what I was paid.*
**AC:** wallet balance and earnings per job · **commission and fee breakdown itemised** · statements ·
payout schedule and history · payout request · **payout is held for the configured period and blocked
entirely while a dispute is open** *(BRU-BIL-03, hard)* — and the seller is told why.

**US-MKP-004** | Marketplace Seller (R38) | P1 | W7 | M12 | BO-12
*As a seller, I want to know how I am scored and what happens if I slip.*
**AC:** scorecard — acceptance, on-time, rating, rework, disputes · **the consequence of falling
below each threshold is stated in advance** · **below threshold reduces visibility automatically;
below the suspension threshold suspends** *(BRU-ECM-04)*.

**US-MKP-005** | Marketplace Operations (R24) | **P0** | W7 | M12, M23 | BO-12
*As marketplace operations, I want marketplace work held to exactly our own standard.*
**AC:** **identical evidence, QC and warranty standards as owned jobs** *(BRU-ECM-03, hard)* ·
the same checklists and photographic requirements · a 1000FiX escalation path visible to the customer ·
quality audited on P11 alongside branches.

**US-MKP-006** | Marketplace Operations (R24) | P1 | W7 | M12 | BO-12
*As marketplace operations, I want disputes decided from evidence, by us.*
**AC:** **disputes are decided by 1000FiX, not by the parties** *(BRU-ECM-09, hard)* · both parties
submit evidence · decision and rationale recorded · **commission reversed automatically where decided
against the seller** *(BRU-BIL-04)*.

**US-MKP-007** | Marketplace Seller (R38) | P2 | W7 | M12 | BO-12
*As a seller, I want to pay to be seen more.*
**AC:** boost and placement purchasable for a period · impressions and clicks reported ·
**a promoted listing is always disclosed as promoted** *(BRU-ECM-06, hard)*.

**US-PCM-001** | Referral Partner (R38) | P2 | W7 | M40 | BO-08
*As a referral partner, I want to track my leads through to commission.*
**AC:** referral links and codes · lead submission and status through to conversion · commission
statements and payout schedule · **commission accuracy 100%**.

---

## 9. USER STORIES — CATEGORY D: CIRCULAR & ASSET-BASED BUSINESS ★

### 9.1 Rental & Equipment-as-a-Service (M13 · `RNT` · W6)

**US-RNT-001** | Customer (R36) | P2 | W6 | M13 | BO-13
*As a customer, I want to see what is available and book it.*
**AC:** availability by category and date across the pool · reservation with deposit terms shown ·
tariff (period + usage) explained before commitment.

**US-RNT-002** | Retail Officer (R25) | **P0** | W6 | M13 | BO-13
*As a retail officer, I want condition proven at dispatch so that a damage claim is never my word
against the customer's.*
**AC:** **a rental asset cannot be dispatched without a completed pre-dispatch condition report**
*(BRU-RNT-01, hard)* · photographic condition record · **the agreement requires a signed condition
report and the deposit received before handover** *(BRU-RNT-02, hard)*.

**US-RNT-003** | Retail Officer (R25) | P1 | W6 | M13 | BO-13
*As a retail officer, I want damage charges derived from evidence, not judgement.*
**AC:** inbound condition report compared to outbound · **charges derive from the difference**;
discretionary charges require approval *(BRU-RNT-03)* · the customer sees the comparison.

**US-RNT-004** | Retail Officer (R25) | P1 | W6 | M13 | BO-13
*As a retail officer, I want a returned asset out of circulation until it is genuinely ready.*
**AC:** **an asset re-enters the pool only after cleaning, servicing and functional test**
*(BRU-RNT-04, hard)* · utilisation and depreciation tracked · overdue rentals accrue automatically
with escalating notification *(BRU-RNT-05)*.

### 9.2 Trade-In, Refurbishment & Resale (M14 · `TRF` · W6)

---

**US-TRF-001** | Customer (R36) | P2 | W6 | M14 | BO-14
*As a customer, I want to trade in my old device without visiting a shop first.*
**AC:** submit with photographs and declared condition from P01 · **indicative valuation** returned ·
firm offer after inspection, with the difference explained · collection arranged under custody ·
payment on acceptance.

**US-TRF-002** | Retail Officer (R25) | **P0** | W6 | M14 | BO-14
*As a retail officer, I want provenance checked before we pay so that we never buy a stolen device.*
**AC:** **provenance and identity checks, including stolen-device/IMEI screening, must pass before a
trade-in offer is paid** *(BRU-TRF-02, hard)* · the check result is recorded against the device
permanently.

---

**US-TRF-003** | Retail Officer (R25) | **P0** | W6 | M14, M06 | BO-14
*As a retail officer, I want it to be impossible to resell a device whose data has not been destroyed.*

**AC**
1. **No trade-in device may proceed to refurbishment or resale without a certified data destruction
   record** *(BRU-TRF-01, hard)* — this is a system block, not a procedure
2. The certificate is linked to the device permanently and is retrievable
3. The block is visible in the workflow as a gate, with the missing step named
4. **Gate 6 criterion: zero refurbished units released without a destruction certificate**

---

**US-TRF-004** | Retail Officer (R25) | P1 | W6 | M14 | BO-14
*As a retail officer, I want grading to be the same regardless of who does it.*
**AC:** published grading criteria per category · **a unit cannot be listed without a completed QA
test protocol and an assigned grade** *(BRU-TRF-03, hard)* · **a supervisor override requires a
recorded justification** *(BRU-TRF-05)* · grade drives price band and warranty terms.

**US-TRF-005** | Customer (R36) | P1 | W6 | M14, M38 | BO-14
*As a buyer of a refurbished device, I want to know exactly what I am buying.*
**AC:** **battery health and known defects disclosed on every listing** *(BRU-TRF-04, hard)* ·
grade explained in plain Bengali · refurbished warranty terms shown before purchase · full provenance
available.

### 9.3 E-Waste, Recycling & Circular Economy (M18 · `ESG` · W8)

**US-ESG-001** | Customer (R36) | P3 | W8 | M18 | BO-14
*As a customer, I want to dispose of an old device responsibly and get something for it.*
**AC:** collection booking or drop-off point finder from P01 · points awarded on receipt ·
disposal certificate available afterwards.

**US-ESG-002** | Quality Manager (R32) | **P0** | W8 | M18 | BO-10
*As the quality manager, I want it to be impossible to send a device for recycling with data still
on it.*
**AC:** **no device may leave for recycling without a certified wipe or physical destruction record**
*(BRU-ESG-01, hard)* · **e-waste may transfer only to a partner whose certification is current at the
transfer date** *(BRU-ESG-02, hard)* · **every recycled unit has a retrievable disposal certificate**
*(BRU-ESG-03, hard)*.

**US-ESG-003** | Quality Manager (R32) | P2 | W8 | M18 | BO-10
*As the quality manager, I want hazardous items handled to their own rules.*
**AC:** hazardous classification drives handling, storage and transport rules **without exception**
*(BRU-ESG-04, hard)* · refrigerant recovery logged · statutory e-waste returns generated.

---

## 10. USER STORIES — CATEGORY E: SUPPLY CHAIN & INVENTORY

### 10.1 Spare Parts & Inventory (M15 · `INV` · W2)

---

**US-INV-001** | Inventory Manager (R17) | **P0** | W2 | M15 | BO-03
*As an inventory manager, I want one view of stock everywhere — including every technician's van —
so that I stop discovering shortages at the counter.*

**AC**
1. Real-time stock across **central warehouse, regional hubs, 51+ branches and 200–400 vans**
2. Filter by part, category, location type, ownership and condition
3. **Brand consignment stock is shown separately and excluded from own-stock valuation**
   *(BRU-INV-04)*
4. On-hand, reserved, in transit and days-of-supply per part per location
5. Search returns in **≤ 600 ms**, including Bengali part descriptions
6. Target accuracy: **98%**; van variance under 1%

---

**US-INV-002** | Store Keeper (R18) | **P0** | W2 | M15 | BO-03
*As a store keeper, I want to scan rather than type, because my hands are full.*
**AC:** every movement — receipt, issue, transfer, return, count — driven by scan · serialised parts
capture the serial at **both receipt and issue** *(BRU-INV-08, hard)* · **stock cannot be issued
against an unapproved paid repair** *(BRU-INV-01, hard)*, and the block says why · **expired
shelf-life stock cannot be issued** *(BRU-INV-05, hard)*.

**US-INV-003** | Inventory Manager (R17) | P1 | W2 | M15 | BO-03
*As an inventory manager, I want replenishment to draft itself.*
**AC:** alert at reorder point with a recommended quantity *(AUT-031)* · **a PO cannot be raised for
an item whose network-wide stock already exceeds maximum** *(BRU-INV-03, approved override)* ·
demand-informed from M43 where available.

**US-INV-004** | Branch Manager (R06) | P1 | W2 | M15 | BO-03
*As a branch manager, I want inter-branch transfers to be controlled, not a WhatsApp arrangement.*
**AC:** **transfer requires source branch manager approval and destination confirmed receipt**
*(BRU-INV-02, hard)* · in-transit visibility · discrepancy on receipt raises an exception.

**US-INV-005** | Senior Technician (R10) | P1 | W2 | M15 | BO-03
*As a technician, I want my van reconciled daily so that variance is caught the same day.*
**AC:** **van stock cannot exceed the configured maximum per item per technician**
*(BRU-FSM-08, hard)* · end-of-shift reconciliation *(AUT-035)* · variance reported to the branch
manager · replenishment against par levels based on the technician's skill profile and job mix.

**US-INV-006** | Quality Manager (R32) | P1 | W2 | M15 | BO-10
*As the quality manager, I want failed goods quarantined, not shelved.*
**AC:** **goods failing inspection go to quarantine and never to available stock**
*(BRU-INV-07, hard)* · disposition recorded · RTV linked to the original receipt.

**US-INV-007** | Inventory Manager (R17) | P2 | W2 | M15 | BO-03
*As an inventory manager, I want counting to be a task list, not a three-day event.*
**AC:** cycle count tasks generated by ABC class and location *(AUT-036)* · variance recorded with a
reason · **adjustments above threshold require approval with a reason code** *(BRU-INV-06, hard)* ·
**the person who adjusts cannot be the person who counted** *(SOD-05)*.

**US-INV-008** | Inventory Manager (R17) | P2 | W2 | M15 | BO-03
*As an inventory manager, I want dead stock surfaced with a recommendation.*
**AC:** no-movement threshold configurable · disposition recommendation produced *(AUT-037)* ·
dead stock reported as a percentage of value.

### 10.2 Warehouse Management (M41 · `WMS` · W3) ★

**US-WMS-001** | Warehouse Operative (R20) | P1 | W3 | M41 | BO-03
*As a warehouse operative, I want the system to tell me where to put it and where to find it.*
**AC:** bin and location structure · put-away strategy suggested and confirmed by scan · picking
waves with an optimised path · **hazardous materials segregated by rule**.

**US-WMS-002** | Inventory Manager (R17) | P2 | W3 | M41 | BO-03
*As an inventory manager, I want bin utilisation and slotting optimised so that fast-movers are
reachable.*
**AC:** movement frequency drives slotting recommendation · utilisation reported · cross-dock
supported for direct-to-branch flows.

### 10.3 Procurement & Supplier Management (M16 `PRO` W3 · M42 `SRM2` W4)

**US-PRO-001** | Procurement Officer (R19) | **P0** | W3 | M16 | BO-06
*As a procurement officer, I want a three-way match that blocks, not one that warns after payment.*
**AC:** **a vendor invoice cannot be approved for payment without a matched purchase order and goods
receipt within tolerance** *(BRU-SCM-01, hard)* · tolerance configurable · exceptions queued with the
specific mismatch named · **the same user cannot create a vendor and approve that vendor's invoice**
*(BRU-SCM-03 / SOD-01, hard)*.

**US-PRO-002** | Procurement Officer (R19) | P1 | W3 | M16 | BO-03
*As a procurement officer, I want to compare quotes side by side.*
**AC:** RFQ issued to multiple vendors from the system · responses captured with price, lead time and
validity · side-by-side comparison · award with a recorded rationale · **a PO cannot be issued to a
vendor who is not active and approved** *(BRU-SCM-02, hard)*.

**US-PRO-003** | Vendor (R38) | P1 | W3 | M16 | BO-03
*As a vendor, I want to receive and acknowledge a PO without a phone call.*
**AC:** PO delivered to P05 · acknowledge, query or propose an alternative date · advance shipping
notice · **> 90% of POs acknowledged through the portal**.

**US-SRM2-001** | Procurement Officer (R19) | P1 | W4 | M42 | BO-03
*As a procurement officer, I want vendor performance measured automatically, not remembered.*
**AC:** on-time delivery, quality rejection rate, responsiveness and price competitiveness scored
from transaction data · **the vendor sees their own scorecard** on P05 · scorecard informs award
decisions.

**US-SRM2-002** | Procurement Officer (R19) | P1 | W4 | M42 | BO-10
*As a procurement officer, I want vendor documents tracked to expiry.*
**AC:** trade licence, TIN, VAT registration and insurance held with expiry dates · alerts before
expiry · **an expired mandatory document blocks new POs** · **PDPA processor obligations flowed down
by contract where the vendor processes personal data** (NFR-098).

### 10.4 Demand Planning & Import (M43 `DPL` W6 · M44 `ITC` W6) ★

**US-DPL-001** | Warehouse Manager (R17) | P2 | W6 | M43, M26 | BO-03
*As a warehouse manager, I want a forecast I can challenge, not a black box.*
**AC:** forecast by part, location and season with the **drivers shown** · safety stock and reorder
parameters recommended · **forecast accuracy measured and reported** · the planner may override with
a reason.

**US-ITC-001** | Procurement Officer (R19) | P2 | W6 | M44 | BO-06
*As a procurement officer, I want true landed cost, not invoice cost.*
**AC:** proforma, LC, shipment, customs, duty and clearing captured · **landed cost allocated before
received stock can be valued as final** *(BRU-SCM-04)* · variance against estimate reported.

---

## 11. USER STORIES — CATEGORY F: ASSET, EQUIPMENT & FACILITIES

**US-AST-001** | Service Centre Agent (R08) | **P0** | W2 | M17 | BO-05
*As anyone touching a device, I want one identity for it across its whole life.*
**AC:** identified by serial, IMEI or asset tag · brand, model, purchase date, ownership and warranty
held once · **full service history across every business line** · ownership transfer recorded ·
device photo history.

**US-AST-002** | Corporate Portal User (R37) | P1 | W4 | M17 | BO-11
*As a corporate client, I want to manage my whole estate, not device by device.*
**AC:** bulk upload and update · assignment to site, department and user · retirement and
decommission · estate health view · **client sees only their own estate**.

**US-EAM-001** | Quality Manager (R32) | P2 | W5 | M45 | BO-10
*As the quality manager, I want calibration tracked because a healthcare contract depends on it.*
**AC:** calibration schedule and certificate per instrument · **an out-of-calibration instrument
cannot be used to certify a healthcare-contract job** · alerts before due date · custody of tools
tracked.

**US-FLT-001** | Logistics Manager (R15) | P2 | W5 | M46 | BO-02
*As a logistics manager, I want vehicle documents tracked so that a van is never on the road
uninsured.*
**AC:** licence, insurance, fitness and tax with expiry alerts · servicing and fuel logged ·
cost per kilometre reported · driver assignment and incidents recorded.

**US-IOT-001** | Remote Support Engineer (R13) | P2 | W8 | M48 | BO-11
*As a remote support engineer, I want to be told a device is going to fail before it does.*
**AC:** telemetry ingested at scale · health scoring per asset · threshold and anomaly alerting ·
**predictive maintenance precision ≥ 70% on the pilot estate** · **a prediction proposes a booking;
it does not create one without human confirmation** *(BRU-AIM-01)*.

**US-FAC-001** | Branch Operations Lead | P3 | W7 | M47 | BO-09
*As the branch operations lead, I want lease and utility obligations tracked so that a renewal is
never missed.*
**AC:** premises register with lease dates and renewal alerts · utilities and maintenance ·
safety equipment inspection dates · branch opening and closing checklists.

---

## 12. USER STORIES — CATEGORY G: FINANCE & TREASURY

### 12.1 Invoicing & Receivables (M20 · `ARB` · W3)

---

**US-ARB-001** | Finance Officer (R27) | **P0** | W3 | M20 | BO-06
*As a finance officer, I want the invoice to exist before I think about it.*

**AC**
1. Invoice generated **automatically on job closure, within 5 seconds** *(AUT-008, NFR-040)*
2. **100% of invoices auto-generated** — manual creation for a completed job requires approval
   *(BRU-BIL-01)*
3. Labour, parts, transport, discount and tax itemised
4. **Privilege discount applied to labour only** *(BRU-WTY-06)*
5. **An invoice cannot be raised for an order that is not Completed** *(BRU-SRM-05, hard)*
6. Delivered on the customer's preferred channel with a payment link *(AUT-022)*

---

**US-ARB-002** | Finance Officer (R27) | **P0** | W3 | M20, M51 | BO-10
*As a finance officer, I want a Mushak-compliant invoice without a separate Excel template.*
**AC:** **Mushak 6.3 format compliant with the VAT and SD Act 2012** · **VAT at the applicable rate
with the Company's BIN displayed** *(BRU-FIN-01, hard)* · category-correct VAT treatment without
manual mapping · **Bengali renders correctly in print and PDF** · **zero NBR exceptions** at Gate 3.

**US-ARB-003** | Finance Officer (R27) | **P0** | W3 | M20, M50 | BO-06
*As a finance officer, I want payments matched for me across every channel.*
**AC:** cash, card, bKash, Nagad, SSLCOMMERZ and bank transfer · **auto-match ≥ 90%** *(AUT-024)* ·
only exceptions presented · **a payment cannot be recorded against a cancelled invoice**
*(BRU-FIN-03, hard)* · **cash receipts above BDT 50,000 require the customer's NID** *(BRU-FIN-02,
hard)*.

**US-ARB-004** | Finance Officer (R27) | P1 | W3 | M20 | BO-06
*As a finance officer, I want dunning to run without me chasing.*
**AC:** sequence at **7 / 14 / 21 / 30 days**, then collections queue *(AUT-023)* · channel per
customer preference · ageing by customer and segment · promise-to-pay recorded.

**US-ARB-005** | Corporate Portal User (R37) | P1 | W4 | M20 | BO-11
*As a corporate client, I want one invoice, itemised the way my finance team needs it.*
**AC:** consolidated per billing cycle · itemised by site, department and asset · **cannot be issued
until every constituent job is Completed and priced** *(BRU-BIL-07, hard)* · approval and dispute on
P04 · target: **disputes under 3%**.

**US-ARB-006** | Finance Manager (R26) | P1 | W3 | M20 | BO-06
*As a finance manager, I want credit notes controlled.*
**AC:** **a credit note requires Finance Manager approval or above** *(BRU-FIN-04, hard)* ·
**the creator cannot be the approver** *(SOD-04)* · reason coded · credit-note rate reported as a
billing-accuracy measure.

### 12.2 Treasury, Cash & Banking (M50 · `TRE` · W3) ★

**US-TRE-001** | Cashier (R29) | **P0** | W3 | M50 | BO-06
*As a cashier, I want my shift to close cleanly every day.*
**AC:** drawer per shift · every movement recorded · **the shift must be reconciled and closed
daily; an unclosed shift blocks the next opening** *(BRU-FIN-10, hard)* · **cash handling and cash
book reconciliation cannot be the same person** *(SOD-12)*.

**US-TRE-002** | Finance Manager (R26) | P1 | W3 | M50 | BO-06
*As a finance manager, I want bank reconciliation to present exceptions, not statements.*
**AC:** statement imported automatically · **auto-match, then only exceptions shown** *(AUT-044)* ·
target **≥ 90%, rising to 94%** · gateway settlement reconciled to transactions.

**US-TRE-003** | CFO (R03) | P2 | W3 | M50 | BO-06
*As the CFO, I want to see cash position and forecast across 51+ counters and every bank account.*
**AC:** consolidated position daily · forecast from receivables, payables and known commitments ·
branch cash exposure highlighted.

### 12.3 Payables & Expense (M52 · `APE` · W3) ★

**US-APE-001** | Finance Officer (R27) | P1 | W3 | M52 | BO-06
*As a finance officer, I want payment runs assembled from matched invoices only.*
**AC:** only three-way-matched invoices enter the run · approval by threshold · payment file
generated · **TDS deducted at the correct rate on every applicable payment; the payment cannot
proceed otherwise** *(BRU-FIN-09, hard)*.

**US-APE-002** | Senior Technician (R10) | P2 | W3 | M52 | BO-02
*As a technician, I want to claim my travel expense from the app, not a paper form.*
**AC:** capture with photograph of the receipt, from the field, offline · policy limits applied ·
approval by line manager · reimbursement tracked to payment.

### 12.4 Tax & Regulatory Compliance (M51 · `TAX` · W4) ★

---

**US-TAX-001** | Finance Manager (R26) | **P0** | W4 | M51 | BO-10
*As a finance manager, I want the VAT return prepared by the system and filed on time, every time.*

**AC**
1. VAT sub-ledgers maintained from source transactions
2. **Mushak 9.1 monthly return prepared automatically and filed by the 15th of the following month
   through the NBR VAT Online portal (vat.gov.bd)** (NFR-100)
3. **Input VAT credit is claimable only against a valid, compliant Mushak 6.3 invoice — the system
   blocks a credit claim without one** (NFR-101)
4. Filing status and acknowledgement recorded
5. Manual filing fallback available from the generated return if the channel is unavailable
6. Target: **100% filed on time with zero adjustment; zero tax compliance findings**

---

**US-TAX-002** | Finance Officer (R27) | **P0** | W4 | M51 | BO-10
*As a finance officer, I want TDS/VDS handled per transaction, not reconstructed at quarter-end.*
**AC:** correct rate applied per vendor and transaction type · challans and certificates generated ·
**quarterly withholding returns on the statutory deadlines (25 Oct / 25 Jan / 25 Apr / 25 Jul)** ·
BIN/TIN validated against the registry.

> **Statutory currency requirement.** Every tax parameter is **versioned configuration, not code**,
> so a rate change is a configuration release. **AY 2026–27 parameters must be built from the enacted
> Finance Act, not from press reporting** — sources currently conflict on the 5% introductory slab
> (§26.3).

### 12.5 Ledger, Revenue & Costing (M19 `FIN` W3 · M53 `REV` W4/W7 · M49 `FXA` W5 · M54 `FPA` W6)

**US-FIN-001** | Finance Manager (R26) | **P0** | W3 | M19 | BO-06
*As a finance manager, I want to close the month in three days.*
**AC:** close checklist with accruals, prepayment amortisation, FX revaluation and recurring journals
*(AUT-043)* · **a period cannot be closed while unposted entries exist** *(BRU-FIN-05, hard)* ·
**once hard-closed, posting requires CFO-approved reopening, which is logged** *(BRU-FIN-06, hard)* ·
target **≤ 3 days**.

**US-FIN-002** | CFO (R03) | P1 | W3 | M19 | BO-07
*As the CFO, I want P&L by branch, business line and entity without consolidating spreadsheets.*
**AC:** full dimensional model — entity, branch, cost centre, business line, zone · drill from
statement to transaction · inter-company reconciliation and consolidation.

**US-REV-001** | Finance Manager (R26) | **P0** | W7 | M53 | BO-12
*As a finance manager, I want every seller and partner paid exactly right.*
**AC:** commission calculated per scheme · statements itemised · payout run with approval ·
**payout accuracy 100% with zero unexplained variance** · **held while a dispute is open**
*(BRU-BIL-03)* · **reversed automatically where a dispute is decided against the seller**
*(BRU-BIL-04)* · escrow where the model requires it.

**US-REV-002** | CFO (R03) | **P0** | W7 | M53 | BO-12
*As the CFO, I want the marketplace revenue treatment to be one decision, applied consistently.*
**AC:** **marketplace transactions are accounted per the declared principal-or-agent model; the model
cannot vary by transaction** *(BRU-FIN-08, hard)* · the treatment is **configurable, not hard-coded**,
so the pending decision D-03 can be applied without a rebuild · **VAT treatment validated by external
tax advice before Gate 7**.

**US-REV-003** | CFO (R03) | P1 | W4 | M53 | BO-06
*As the CFO, I want revenue recognised on a schedule, not on a hunch.*
**AC:** recognition schedules per performance obligation across all 14 streams · **deferred revenue
released only per the schedule; manual release requires CFO approval** *(BRU-BIL-06, hard)*.

**US-FPA-001** | Branch Manager (R06) | P2 | W6 | M54 | BO-07
*As a branch manager, I want to know what a job actually cost.*
**AC:** cost per service order — labour, parts, logistics, sub-contract and overhead · profitability
by branch, business line and contract · budget against actual with variance.

---

## 13. USER STORIES — CATEGORY H: PEOPLE & WORKFORCE

### 13.1 Core HR & Workforce (M21 `HCM` · M55 `WFM` · W5)

**US-HCM-001** | HR Officer (R31) | P1 | W5 | M21 | BO-10
*As an HR officer, I want the statutory employment artefacts generated, not typed.*
**AC:** **appointment letter, identity card and service book generated per the Bangladesh Labour Act
2006** · probation limits enforced · organisation structure and reporting line maintained ·
documents held with retention.

**US-HCM-002** | Employee (any) | P2 | W5 | M21 | BO-10
*As an employee, I want to see my own record and make my own requests.*
**AC:** payslips, leave balance, attendance and personal details **for myself only** (T4) · leave and
expense requests submitted from the app · **an employee's payroll record is visible to them and to
HR/finance, never to peers or line managers below HR Manager** *(BRU-HRM-07, hard)* · target 85%
self-service adoption.

**US-WFM-001** | HR Officer (R31) | P1 | W5 | M55 | BO-10
*As an HR officer, I want attendance to arrive complete, not be chased from 51 branches.*
**AC:** biometric and mobile clock-in · **GPS-based attendance for field technicians, captured only
during working hours and on duty** *(BRU-FSM-05)* · exceptions surfaced for resolution ·
target **99% capture completeness**.

**US-WFM-002** | Dispatch Manager (R07) | P1 | W5 | M55 | BO-02
*As a dispatch manager, I want to know who is actually available, by skill and zone.*
**AC:** shift patterns and rosters across 51+ branches · leave and holiday applied · **the Bangladesh
public holiday calendar including moon-dependent dates** · available capacity by skill and zone feeds
dispatch.

**US-WFM-003** | HR Manager (R30) | P1 | W5 | M55 | BO-10
*As an HR manager, I want overtime controlled before it is worked.*
**AC:** **overtime must be pre-approved by the line manager before it counts for payroll**
*(BRU-HRM-02, hard)* · working-time limits enforced at scheduling *(BRU-FSM-10)* ·
**leave cannot be approved where it would take team coverage below the configured minimum**
*(BRU-HRM-04, approved override)*.

### 13.2 Payroll (M56 · `PAY` · W5) ★

---

**US-PAY-001** | Payroll Officer (R41) | **P0** | W5 | M56 | BO-10
*As a payroll officer, I want statutory calculation done by the system so that one mistake does not
affect five hundred people at once.*

**AC**
1. Gross-to-net for monthly and contractual employees
2. **NBR income tax with the AY thresholds, minimum tax and investment rebate**, held as **versioned
   configuration**
3. **Provident fund** and **gratuity at not less than 30 days' wages per completed year at the
   last-drawn rate** (Bangladesh Labour Act)
4. Incentives imported from M57 — **calculated there, paid here** *(SOD-30)*
5. **Payroll cannot be finalised until attendance for the period is verified and locked**
   *(BRU-HRM-05, hard)*
6. Exceptions surfaced **before** the run, with the specific employee and issue named
7. Target: **under 4 hours; corrections under 0.3%**

---

**US-PAY-002** | HR Manager (R30), CFO (R03) | **P0** | W5 | M56 | BO-10
*As the approvers, we want the segregation visible so that nobody is asked to do something the system
will refuse.*
**AC:** **payroll requires two approvals — HR Manager and CFO** *(BRU-HRM-06, hard)* ·
**the preparer cannot approve** *(SOD-03)* · **the approver cannot release the bank file**
*(SOD-29)* · **the boundary is shown in the interface before the user acts**, not at submission.

**US-PAY-003** | Payroll Officer (R41) | **P0** | W5 | M56 | BO-10
*As a payroll officer, I want a BEFTN file the bank accepts first time.*
**AC:** BEFTN file generated to the confirmed bank format *(AUT-046)* · validation before release ·
payslips distributed digitally · posting to the ledger automatic · **Gate 5: first payroll run
processed, validated and paid with zero errors; BEFTN accepted without rework**.

### 13.3 Competency & Certification (M22 · `LMS` · W5)

---

**US-LMS-001** | Quality Manager (R32) | **P0** | W5 | M22, M02 | BO-15
*As the quality manager, I want an expired certification to stop a dispatch automatically, because
today we find out when a brand rejects the claim.*

**AC**
1. Certification tracked per technician per brand with expiry
2. **Alerts at 90 / 60 / 30 / 15 days** to technician, manager and HR *(AUT-041)*
3. **On expiry the technician is removed from that brand's warranty dispatch pool automatically**
   *(AUT-042)*
4. **Assignment to an uncertified technician for that brand's warranty work is blocked**
   *(BRU-HRM-01 / BRU-SRM-09, hard)* — and the block names the missing certification
5. **The eligibility check (FR-LMS-039) is consumed by M02 at assignment. M02 goes live in W2 and
   M22 in W5 — the interface must be built into M02 in W2 as a stub returning "eligible" and
   connected in W5.** Retrofitting a blocking check into a live assignment path is materially riskier
6. Target: **zero claims rejected for an uncertified technician**

---

**US-LMS-002** | Technician (R10, R11) | P2 | W5 | M22 | BO-15
*As a technician, I want training in Bengali that I can actually complete on my phone.*
**AC:** Bengali content · mobile-completable · progress saved offline · **mandatory training overdue
restricts the affected work types** *(BRU-LMS-01, hard)* · completion recorded against competency.

**US-LMS-003** | Competency Assessor (R43) | P2 | W5 | M22 | BO-15
*As a competency assessor, I want assessment to mean something operationally.*
**AC:** assessment against a defined standard · result binding on dispatch eligibility ·
re-certification scheduled · **a marketplace engineer cannot be activated in a category without
passing that category's qualification** *(BRU-LMS-02, hard)*.

### 13.4 Performance, Talent & Safety (M57 `PIC` W5 · M58 `TAO` W6 · M59 `HSE` W6) ★

**US-PIC-001** | Senior Technician (R10) | P1 | W5 | M57 | BO-02
*As a technician, I want my incentive calculated from what I actually did.*
**AC:** scorecard from field-captured events — jobs, first-time fix, on-time arrival, CSAT, rework ·
**incentive calculated only after the minimum monthly threshold is met** *(BRU-HRM-03)* ·
**the technician sees the calculation, not just the result**.

**US-PIC-002** | HR Manager (R30) | P2 | W5 | M57 | BO-02
*As an HR manager, I want appraisal linked to measured performance, not memory.*
**AC:** review cycle with objectives and measured KPIs · calibration across managers · outcome feeds
compensation review · history retained.

**US-TAO-001** | Recruiter (R45) | P2 | W6 | M58 | BO-09
*As a recruiter, I want the offer approval boundary enforced.*
**AC:** requisition and approval · candidate pipeline and assessment · **the recruiter cannot approve
an offer** · onboarding checklist triggers provisioning in M29 and M66 *(AUT-047)*.

---

**US-HSE-001** | Senior Technician (R10) | P1 | W3 † | M59, M21 | BO-10
*As a technician, I want to report a hazard or a near-miss in seconds, from where I am standing.*

**AC**
1. Report an incident, near-miss or hazard **from the technician app in under 30 seconds**
2. Photograph, location and category captured; free text optional
3. Works **offline**; queued and synced
4. **A serious incident raises an immediate alert** to the HSE officer and line manager
5. Reporting a near-miss **never triggers a disciplinary consequence** — this is stated in the app

> **† Sequencing decision Q-05b.** FR-HSE-009 and FR-HSE-011 depend only on P02 and M21 and can ship
> with the technician app in **W3** at low incremental cost. The remaining 40 requirements of M59
> stay in W6. **Waiting until W6 leaves field safety reporting on paper for three extra waves for no
> technical reason.**

---

**US-HSE-002** | HSE Officer (R44) | P2 | W6 | M59 | BO-10
*As an HSE officer, I want to evidence our statutory obligations to an inspector.*
**AC:** **safety committee constitution, safety officer appointment and first-aid provision per the
Bangladesh Labour Rules 2015** · risk assessments · PPE issue and inspection · accident notification
and compensation · **lone-worker safety for field technicians** · evidence pack generated on demand.

**US-HSE-003** | Occupational Health (R46) | P2 | W6 | M59, M29 | BO-10
*As occupational health, I want medical detail restricted to me alone.*
**AC:** medical records classified **S3 restricted** · **sole access by R46**; even HR Manager sees
only fitness status, not diagnosis · access logged; step-up authentication required.

---

## 14. USER STORIES — CATEGORY I: GOVERNANCE, RISK, QUALITY & KNOWLEDGE

**US-QMS-001** | Field Auditor (R32) | **P0** | W5 | M23 | BO-10
*As an auditor, I want to complete an audit on my tablet in a branch with no signal.*
**AC:** assigned audits, scope and checklists available offline · **checklist completion, photo and
document evidence captured offline** · observations recorded **against ISO clauses** · findings raised
with classification, severity and owner · auditee acknowledgement signature on device · syncs to M23.

**US-QMS-002** | Quality Manager (R32) | **P0** | W5 | M23 | BO-10
*As the quality manager, I want a CAPA closed only when it has actually worked.*
**AC:** **every non-conformance requires a root cause and a CAPA before it can be closed**
*(BRU-QMS-02, hard)* · **a CAPA cannot be closed without effectiveness verification after the defined
interval** *(BRU-QMS-03, hard)* *(AUT-050)* · **repeated non-conformance in the same process triggers
a mandatory management review item** *(BRU-QMS-05)*.

**US-QMS-003** | Quality Manager (R32) | P1 | W5 | M23 | BO-10
*As the quality manager, I want the ISO evidence pack assembled by the system.*
**AC:** clause-to-evidence mapping · policies, process register, checklists, audits, findings, CAPAs
and management review in one pack · **target: zero major non-conformances traced to systems**.

**US-QMS-004** | Marketplace Operations (R24) | P1 | W7 | M23, M12 | BO-12
*As marketplace operations, I want sellers audited like branches.*
**AC:** seller audit programme on P11 · same checklist standards · findings and consequences applied
through the seller score.

**US-GRC-001** | Chief Data Officer (R40) | **P0** | W6 | M60, M29 | BO-10
*As the Chief Data Officer, I want a breach assessed and notified within the statutory window.*
**AC:** incident classified and assessed for likely significant damage · **notification to the
National Data Management Authority within the prescribed timeframe** (NFR-094) · affected data
subjects identified · the assessment, decision and notification retained as a processing record.

**US-GRC-002** | CFO (R03) | P2 | W6 | M60 | BO-10
*As the CFO, I want compliance obligations tracked with their currency.*
**AC:** obligation register with owner, evidence and review date · **every statutory citation carries
a verified-on date and is re-verified at each wave gate** (DoD-17) · control library with testing
schedule and results.

**US-DMS-001** | Quality Manager (R32) | P1 | W3 | M24 | BO-10
*As the quality manager, I want retention enforced by the system, not by discipline.*
**AC:** retention class per document type · **a document cannot be deleted before its retention
expires** *(BRU-DMS-01, hard)* · **legal hold overrides retention absolutely** *(BRU-DMS-02, hard)* ·
end-of-retention presented for disposal review *(AUT-051)* · **processing records retained ≥ 5 years**
(NFR-095).

**US-DMS-002** | Account Manager (R22) | P1 | W3 | M24 | BO-08
*As an account manager, I want a contract signed digitally and legally.*
**AC:** **qualified e-signature for binding contracts**; operational e-signature for job completion ·
**a signed document cannot be modified — a change requires a new version and a new signature**
*(BRU-DMS-03, hard)* · envelope status tracked · executed copy delivered to both parties.

**US-KMS-001** | Senior Technician (R10) | P2 | W6 | M61 | BO-02
*As a technician, I want the repair manual on my phone in the basement where there is no signal.*
**AC:** repair manuals, wiring diagrams, troubleshooting trees and past repair notes **available
offline** · search in **Bengali and English** · article usefulness rated by technicians · brand
bulletins and recall notices pushed.

**US-KMS-002** | Specialist Technician (R12) | P2 | W6 | M61 | BO-02
*As a specialist, I want to capture what I learned so the next person does not rediscover it.*
**AC:** authoring from a solved job · review and approval before publication · versioning · linked to
fault codes so it surfaces at the point of need.

---

## 15. USER STORIES — CATEGORY J: DATA, ANALYTICS & INTELLIGENCE

**US-BID-001** | CEO (R01) | **P0** | W4 | M25 | BO-07
*As the CEO, I want one dashboard across all fourteen revenue streams.*
**AC:** revenue, margin, volume, cash, CSAT and utilisation by stream · **drill from group revenue to
a single job** · loads in **≤ 5 s** · mobile-optimised for a phone · **zero manual reporting packs**
by Gate 8.

**US-BID-002** | Ops Director (R05) | P1 | W4 | M25 | BO-07
*As the operations director, I want branches ranked so that I know where to go on Monday.*
**AC:** league table across all 51+ branches on every operational and financial dimension ·
benchmark shown on every branch dashboard · drill to technician and to job.

**US-BID-003** | Branch Manager (R06) | P1 | W4 | M25 | BO-07
*As a branch manager, I want to build my own view without asking IT.*
**AC:** governed self-service on **certified datasets**, without SQL · **row-level security applied
automatically** — a manager cannot build their way to another branch's data · scheduled distribution
and export.

**US-BID-004** | Any manager | P1 | W4 | M25 | BO-07
*As a manager, I want to be told when something moves, not to go looking.*
**AC:** threshold and anomaly alerts routed to the right role · alert includes the number, the change
and a link to the detail · **an alert with no defined action is removed**.

**US-DAT-001** | Data Steward (R39) | P1 | W4 | M62 | BO-17
*As a data steward, I want a stale dashboard to say so rather than mislead.*
**AC:** data quality tests on every warehouse load · **a failure blocks the dependent refresh**
*(AUT-059, DI-06)* · **last-known-good shown with an explicit staleness warning** · lineage traceable
from figure to source.

**US-AIM-001** | Ops Director (R05) | P2 | W6 | M26 | BO-02
*As the operations director, I want to understand and be able to overrule any model.*
**AC:** **every production model has a current model card and drift monitoring** ·
**a recommendation with material customer or financial impact requires human confirmation**
*(BRU-AIM-01, hard)* · **no output may cross a business guard rail** *(BRU-AIM-02, hard)* ·
**overrides are logged and feed retraining** · on model failure the module **falls back to rules**.

**US-BPA-001** | IT Administrator (R33) | P1 | W3 | M63 | BO-01
*As an administrator, I want to change a threshold or a workflow without a release.*
**AC:** **workflows, forms, thresholds and business rules configurable without code** (NFR-027) ·
**thresholds are configuration, not code** *(BR-STD-03)* · **one platform-wide workflow engine — no
module implements its own** · change traceable to an approved change record *(BRU-ADM-02, hard)*.

**US-BPA-002** | IT Administrator (R33) | P1 | W3 | M63 | BO-01
*As an administrator, I want to know a scheduled job failed before a user does.*
**AC:** **every scheduled job reports success, failure and duration — silent failure is a defect** ·
alerting on failure · automation inventory with owner and last-run status.

---

## 16. USER STORIES — CATEGORY K: PLATFORM & TECHNOLOGY

**US-SEC-001** | Every user | **P0** | W1 | M29 | BO-10
*As any user, I want one login for everything I am allowed to use.*
**AC:** single sign-on across all 12 portals · **no portal keeps its own credential store**
(PS-01) · **MFA mandatory for admin, finance, HR and all privileged roles** *(BRU-SEC-01, hard)* ·
session policy — 30 min idle external, 60 min internal, 12 h absolute.

**US-SEC-002** | IT Administrator (R33) | **P0** | W1 | M29 | BO-10
*As an administrator, I want a leaver's access gone within the hour, without me remembering.*
**AC:** `employee.left` **revokes all access within one hour** *(BRU-SEC-06, hard)* *(AUT-048)* ·
devices deregistered; delegated authority reassigned · **zero orphaned accounts beyond 24 hours**,
measured weekly.

**US-SEC-003** | IT Administrator (R33) | **P0** | W1 | M29 | BO-10
*As an administrator, I want the system to refuse an unsafe role combination at the moment I assign
it.*
**AC:** **SoD evaluated at role assignment; incompatible combinations blocked** *(BRU-SEC-07, hard)* ·
**the reason and the conflicting duty are named** · exceptions time-boxed with a visible expiry and a
standing quarterly report.

**US-SEC-004** | Any user handling restricted data | **P0** | W1 | M29 | BO-10
*As a user working with restricted data, I want the extra step to be obvious, not a surprise.*
**AC:** **step-up authentication for sensitive actions** — payouts, payroll finalisation, data-case
access, bulk export *(BRU-SEC-02, hard)* · the user is told why the extra step is required · **every
access to S3 data is logged**; privileged sessions recorded and the user informed.

**US-SEC-005** | Data Subject | **P0** | W1 | M29, M33 | BO-10
*As a data subject, I want my sensitive data kept where the law says it must be.*
**AC:** **NID, passport, TIN, biometric templates and recovered customer data held in the
Bangladesh-resident store** (NFR-086) · **residency classification carried on every field and enforced
at write time, not by convention** (NFR-086a) · **cross-border transfer of a classified field requires
an Authority notification record and a documented safeguard before it executes** (NFR-086b) ·
**non-production environments never contain unmasked residency-classified data** (NFR-086c,
BRU-SEC-08).

**US-IPF-001** | Portal user (any) | **P0** | W1 | M28 | BO-05
*As a portal user, I want the system to degrade gracefully rather than fail.*
**AC:** **every P0 integration has a documented, tested manual fallback** (NFR-050) · circuit breakers
open on sustained failure *(AUT-053)* · **the user sees a plain-language message saying what is
unavailable and what will happen** — never a technical error · queued actions confirm when the service
returns.

**US-IPF-002** | IT Administrator (R33) | P1 | W1 | M28 | BO-17
*As an administrator, I want to see integration health without waiting for a complaint.*
**AC:** health, throughput, latency and error rate per integration · **zero failures undetected beyond
5 minutes** · dead-letter queue with mandatory triage after one hour *(AUT-054)* · credential expiry
alerted 30 days ahead *(AUT-060)*.

**US-ADM-001** | IT Administrator (R33) | **P0** | W1 | M30 | BO-09
*As an administrator, I want to turn a capability off without a deployment.*
**AC:** **feature flags allow any new capability to be disabled without a release** (OPS-06) ·
configuration versioned and promoted through environments — **never hand-edited in production**
(OPS-02) · **master data changes above a defined significance require approval before taking effect**
*(BRU-ADM-01, hard)*.

**US-ADM-002** | IT Administrator (R33) | P1 | W1 | M30 | BO-10
*As an administrator, I want translation managed as a release artefact.*
**AC:** translation coverage reported per module · **100% before a module is accepted** (DoD-08) ·
missing strings identified by screen · **machine translation flagged and blocked from release**.

**US-MDM-001** | Data Steward (R39) | P1 | W2 | M64 | BO-17
*As a data steward, I want a stewardship queue rather than a spreadsheet of problems.*
**AC:** golden-record governance across party, product, location and asset · stewardship tasks routed
by domain owner · validation rules applied at entry · data quality scored and trended.

**US-GLO-001** | CTO (R02) | P2 | W9 | M65 | BO-18
*As the CTO, I want a second country stood up by configuration.*
**AC:** country pack framework with Bangladesh as the reference · locale pack, currency, tax rules and
statutory artefacts configurable · **a test entity in a second country stood up in ≤ 12 weeks using
configuration only, with no core code change** (Gate 9).

**US-ITS-001** | Employee (any) | P2 | W6 | M66 | BO-09
*As an employee, I want to raise an IT problem and see it move.*
**AC:** internal helpdesk with categories and SLA · status visible to the requester · internal asset
and licence register · change and incident management.
*Specification outstanding — see §26.3.*

**US-PPM-001** | Programme Manager | P2 | W7 | M67 | BO-09
*As a programme manager, I want branch openings and corporate rollouts run as projects.*
**AC:** project structure with milestones, dependencies and resources · portfolio prioritisation ·
benefits tracked against the case.
*Specification outstanding — see §26.3.*

---

## 17. USER STORIES — THE TWELVE PORTALS

> Portal stories cover what belongs to the **surface** rather than to a module: navigation, layout,
> offline behaviour, accessibility, performance and portal-specific composition.

### 17.1 Cross-Portal (applies to all twelve)

**US-POR-X01** | Every user | **P0** | W1 | All | BO-10
*As any user, I want to sign in once and have my permissions follow me.*
**AC:** every portal authenticates through the central identity provider; **no portal maintains its
own credential store** · session, timeout and MFA policy inherited centrally, **never
portal-specific**.

**US-POR-X02** | Every user | **P0** | W1 | All | BO-05
*As any user, I want the same word to mean the same thing on every screen.*
**AC:** **one design system, one component library, one token set across all twelve portals**
(NFR-080) · status colour coding consistent everywhere · date format DD/MM/YYYY throughout ·
number alignment and currency format consistent.

**US-POR-X03** | Bengali-speaking user | **P0** | W1 | All | BO-05
*As a Bengali speaker, I want the whole product in Bengali, not most of it.*
**AC:** **Bengali default on customer and field surfaces**, English on back office ·
**100% of user-facing strings translated before a module is accepted** · **no English fallback
visible to a Bengali user** · professionally translated — **machine translation is not acceptable for
release**.

**US-POR-X04** | Every user | **P0** | W1 | All | BO-05
*As any user, I want an error message that tells me what to do next.*
**AC:** **every user-visible error states what happened and what to do next, in the user's language**
(NFR-078) · no technical jargon, no error codes as the primary message · a route to report the issue.

**US-POR-X05** | Every user | P1 | W1 | All | BO-10
*As any user, I want to be protected from destroying something by accident.*
**AC:** destructive actions require confirmation naming the specific item · **reversible where
possible** (NFR-079) · **soft deletion only** (DI-08).

**US-POR-X06** | Every portal owner | **P0** | W1 | All | BO-10
*As the platform owner, I want no business rule implemented in a portal.*
**AC:** **no portal implements a business rule; client validation is for convenience only** (PS-11) ·
**no portal holds authoritative state** — it may cache for performance, never for truth · every
portal calls through the gateway with a portal-specific credential.

**US-POR-X07** | Any user on a slow connection | P1 | W2 | All | BO-05
*As a user on 3G, I want the thing I came for, not a spinner.*
**AC:** **critical customer paths under 400 KB first load** (NFR-081) · progressive loading with
meaningful placeholders · **progress indicator for any action over 2 seconds**.

**US-POR-X08** | Every user | P1 | W1 | All | BO-17
*As the platform owner, I want to know whether users are actually succeeding.*
**AC:** analytics instrumentation on every critical funnel, feeding M25 (PS-10) · task completion,
abandonment and error rates measured per role.

### 17.2 P01 — Customer Self-Service Portal & Mobile App (W2 / W6)

**US-POR-001** | Customer (R36) | **P0** | W2 | P01 | BO-05
*As a customer, I want to book a service in three steps.*
**AC:** device → symptom → mode and slot, in **≤ 3 steps** · **indicative price shown before
confirmation** · photographs and Bengali voice description supported · **booking funnel conversion
> 72%** · target online booking **88%**.

**US-POR-002** | Customer (R36) | **P0** | W2 | P01 | BO-05
*As a customer, I want to track without logging in.*
**AC:** **public tracking link works without login**, scoped to that one order · status timeline ·
live technician map and ETA when en route · technician name and photo · updates by push, SMS and
WhatsApp.

**US-POR-003** | Customer (R36) | P1 | W2 | P01 | BO-06
*As a customer, I want to pay the way I already pay for everything else.*
**AC:** bKash, Nagad, card and bank transfer · saved methods · invoices, receipts and payment history ·
refund status visible.

**US-POR-004** | Customer (R36) | P1 | W2 | P01 | BO-10
*As a customer, I want to control what you know about me.*
**AC:** consent and notification preferences manageable in the account · **transparency notice
accessible at any time** · data-subject requests raisable from the portal · marketing opt-out
honoured immediately.

**US-POR-005** | Customer (R36) | P2 | W6 | P01 | BO-14
*As a customer, I want everything else you offer in the same place I book a repair.*
**AC:** shop for parts, accessories and refurbished devices · rental booking · trade-in submission ·
data-services request · e-waste collection booking · contracts and warranty products · loyalty and
referral — **one account, one identity, one history**.

**US-POR-006** | Customer (R36) | **P0** | W2 | P01 | BO-05
*As a customer on a basic Android on 3G, I want the app to work.*
**AC:** **Android 9+ / iOS 14+** · PWA with offline shell and installability · **Bengali default** ·
WCAG conformance per §21 · **no horizontal scrolling from 320 px upward**.

### 17.3 P02 — Technician Mobile Application (W2)

---

**US-POR-007** | Technician (R10, R11, R12) | **P0** | W2 | P02 | BO-02
*As a technician, I want the app to work for a whole day with no signal, because that is my reality.*

**AC**
1. **Full operation offline for 24 hours with no data loss** (NFR-047)
2. **Sync within 30 seconds of reconnection on 3G, with 100% data integrity** (NFR-037)
3. **Every state-changing action is queued locally and idempotent on the server**
4. **No feature requires a connection that a technician cannot complete offline**
5. Local store **encrypted**; scope limited to the technician's own assigned work
6. **Zero offline sync failures** is the Gate 2 criterion

---

**US-POR-008** | Technician (R10) | **P0** | W2 | P02 | BO-02
*As a technician, I want to know whether my work is safe, without having to think about connectivity.*
**AC:** **network and sync state always visible** · **"saved on this device" is shown distinctly from
"sent to the office"** · queued action count shown · **a failed sync explains what failed and offers a
recoverable action** — never a silent failure.

**US-POR-009** | Technician (R10) | **P0** | W2 | P02 | BO-02
*As a technician, I want to be told plainly when my change was overridden, and why.*
**AC:** **server is authoritative for assignment, pricing, stock and state; the client wins for
evidence, notes and field-captured timestamps** · **any resolved conflict is shown to the technician
with what changed and why** — the system never silently picks a winner on something the technician
entered · unresolvable conflicts are surfaced for a human decision.

**US-POR-010** | Technician (R10) | **P0** | W2 | P02 | BO-02
*As a technician, I want to use the app with one hand, in sunlight, wearing gloves.*
**AC:** **primary actions in thumb reach; bottom navigation** · **touch targets ≥ 44 × 44 px** ·
sunlight-readable contrast · **no gesture-only action** — every swipe has a visible button
equivalent · works with a wet or gloved finger · **only the fields needed for the current task are
shown**.

**US-POR-011** | Technician (R10) | **P0** | W2 | P02 | BO-02
*As a technician, I want the app not to flatten my battery before lunch.*
**AC:** **≤ 12% battery per 8-hour shift excluding navigation** (NFR-082) · location and sync
frequency managed adaptively · uploads deferred and compressed to reduce the technician's own data
cost.

**US-POR-012** | Technician (R11) | P1 | W2 | P02 | BO-02
*As a junior technician, I want the app to run at all on the phone I was given.*
**AC:** **mid-range Android 11, 3 GB RAM** · **job list ≤ 8 s cold, ≤ 2 s warm on 3G** (NFR-036) ·
crash-free sessions **> 99.5%** · forced and optional update management with version compatibility.

**US-POR-013** | Technician (R10) | P1 | W2 | P02 | BO-02
*As a technician, I want the app in Bengali, including when something goes wrong.*
**AC:** **complete Bengali interface including every error message** · Bengali voice-to-text for
notes · Bengali phonetic keyboard support · **fonts render correctly at 16 px minimum**.

### 17.4 P03 — Admin Operations Portal (W1)

**US-POR-014** | Any back-office user | **P0** | W1 | P03 | BO-01
*As a back-office user, I want my workspace to open on the work I actually do.*
**AC:** **role-scoped workspaces** — Service Intake, Dispatch, Branch, Workshop, Inventory,
Procurement, Finance, HR, Quality, Contract, Warranty, Marketplace, Managed Services, System ·
each reachable in **one click from home** · each opening on that role's live work.

**US-POR-015** | Service Centre Agent (R08) | **P0** | W1 | P03 | BO-01
*As a high-volume user, I want to work from the keyboard.*
**AC:** **keyboard-first operation for intake, dispatch and finance** · shortcuts for new, save,
search and submit · tab order follows the visual order · **no function requires a mouse**.

**US-POR-016** | Any back-office user | P1 | W1 | P03 | BO-01
*As a back-office user, I want to find anything quickly.*
**AC:** **any record reachable in ≤ 4 clicks from any starting point** (NFR-077) · global search on
every screen, accepting **Bengali and English simultaneously** · recent items · saved views and
filters, shareable · bulk actions on every list.

**US-POR-017** | Branch staff (R08, R29) | P1 | W1 | P03 | BO-01
*As branch staff, I want the screen to fit the computer I have.*
**AC:** **usable at 1366×768 without horizontal scrolling** — the most common branch hardware ·
density appropriate to a transaction screen · **standard page load ≤ 2 s**.

### 17.5 P04 — Corporate B2B Portal (W4)

**US-POR-018** | Corporate Portal User (R37) | **P0** | W4 | P04 | BO-11
*As a corporate client, I want to raise 45 requests at once and know they are covered.*
**AC:** CSV upload of up to N devices · **validated against contract coverage before submission**,
with uncovered devices listed explicitly · preview before commit · **created in under 5 minutes** ·
batch tracked as a unit.

**US-POR-019** | Corporate Portal User (R37) | P1 | W4 | P04 | BO-11
*As a corporate client, I want my own approval chain respected.*
**AC:** multi-user access under one account with sub-roles (requester, approver, finance, admin) ·
**the client's own approval chain configurable** (user → line manager → 1000FiX) · delegated authority
limits enforced.

**US-POR-020** | Corporate Portal User (R37) | P1 | W4 | P04 | BO-10
*As a corporate client, I want the compliance evidence my own auditors will ask for.*
**AC:** **destruction certificates, disposal certificates and service evidence packs downloadable** ·
scoped to their own estate only · retained for the agreed period.

### 17.6 P05–P12

**US-POR-021** | Vendor (R38) | P1 | W3 | P05 | BO-03
*As a vendor with a basic PC and limited English, I want the portal to be simple.*
**AC:** **Bengali interface** · PO acknowledgement, invoice submission and payment status in three
screens · own scorecard visible · **no cost, margin or other vendors' data ever visible** (EA-02).

**US-POR-022** | Executive (R01–R05) | P1 | W4 | P06 | BO-07
*As an executive, I want the dashboard on my phone in a meeting.*
**AC:** key dashboards mobile-optimised · **executive dashboard loads ≤ 5 s** · drill-down works on
touch · export to PDF for the board pack.

**US-POR-023** | Marketplace Seller (R38) | **P0** | W7 | P07 | BO-12
*As a seller, I want the portal to work on my own mid-range Android, in Bengali.*
**AC:** **Bengali-first**, mobile-first · registration completable on a phone · **onboarding
completion > 60% of starters** · offline tolerance for listing and job management · earnings and
payout always visible.

**US-POR-024** | Brand Partner (R38) | P1 | W4 | P08 | BO-04
*As a brand partner, I want to work through a queue of claims efficiently.*
**AC:** claim queue with ageing and bulk actions · full evidence pack inline — no separate emails ·
approve, part-approve, reject with reason, request information · **rate cards published and
versioned** · own-brand performance view · **sees only their own brand's data** (EA-05).

**US-POR-025** | Rider (R16) | **P0** | W3 | P09 | BO-01
*As a rider, I want the app usable at a doorstep in the rain.*
**AC:** **very large targets; scan over type; minimum steps** · **full offline operation with queued
sync** · manifest, collection, transit, delivery and cash reconciliation · **POD capture completeness
100%**.

**US-POR-026** | Contact Centre Agent (R34) | **P0** | W4 | P10 | BO-16
*As an agent, I want everything on one screen because the customer is waiting.*
**AC:** unified queue, screen-pop, action-in-conversation, knowledge search, canned Bengali responses ·
**fewer than 3 screen switches per contact** · jump to any ERP screen and return with the conversation
intact · **disposition coding completeness 100%**.

**US-POR-027** | Field Auditor (R32) | **P0** | W5 | P11 | BO-10
*As an auditor, I want the app to work in a branch basement.*
**AC:** **full offline audit execution with evidence capture** · checklist, findings, CAPA
verification, cash and stock spot checks · on-device report generation with auditee signature ·
**100% of audits completed on mobile**.

**US-POR-028** | Referral Partner (R38) | P2 | W7 | P12 | BO-08
*As a partner, I want to see what I have earned and when I will be paid.*
**AC:** referral links, lead tracking to conversion, commission statements, payout schedule and
history · co-marketing materials · **commission accuracy 100%**.

---
---

# PART C — HOW IT MUST FEEL

---

## 18. USER JOURNEY MAPS

> These are the programme's **15 critical business journeys**. Each must be covered by an automated
> end-to-end test run nightly. They are the definition of "the system works".

| # | Journey | Actors | First live | §  |
|---|---|---|:--:|:--:|
| 1 | Book online → dispatch → field repair → invoice → pay → close → survey | Customer, Dispatcher, Technician, Finance | W3 | 18.1 |
| 2 | Walk-in intake → workshop repair → estimate → approval → QC → handover → pay | Customer, Agent, Workshop, Cashier | W3 | 18.2 |
| 3 | Pick & drop collection → workshop → return delivery → invoice | Customer, Rider, Coordinator | W3 | 18.3 |
| 4 | Warranty job → claim → submission → approval → reimbursement → reconciliation | Technician, Claims Officer, Brand Partner | W4 | 18.4 |
| 5 | AMC sale → activation → preventive schedule → visit → renewal | Account Manager, Customer, Technician | W4 | 18.5 |
| 6 | MSP alert → ticket → remote resolution → SLA → monthly report | MSP Engineer, Corporate Client | W5 | 18.6 |
| 7 | Marketplace order → seller quote → award → job → review → commission → payout | Customer, Seller, MP Ops, Finance | W7 | 18.7 |
| 8 | Rental reservation → delivery → return → damage assessment → billing | Customer, Retail Officer, Rider | W6 | 18.8 |
| 9 | Trade-in → offer → intake → data wipe → refurbishment → grading → resale | Customer, Retail Officer, Data Services | W6 | 18.9 |
| 10 | E-waste collection → triage → destruction → recycling → certificate | Customer, Quality Manager, Partner | W8 | 18.10 |
| 11 | Data recovery case → custody → recovery → handover → purge certificate | Customer, Data Services Technician | W6 | 18.11 |
| 12 | Requisition → PO → receipt → inspection → three-way match → payment | Inventory, Procurement, Vendor, Finance | W3 | 18.12 |
| 13 | Payroll cycle → attendance lock → calculation → approval → BEFTN → payslips | Payroll Officer, HR Manager, CFO | W5 | 18.13 |
| 14 | Complaint → non-conformance → root cause → CAPA → verification → closure | Customer, CS Manager, Quality Manager | W5 | 18.14 |
| 15 | Month-end close → reconciliation → VAT return → management pack | Finance Manager, CFO | W4 | 18.15 |

---

### 18.1 Journey 1 — Book Online to Cash

**Actors:** Tahmina Khatun (P-34b, Bengali-only customer) · Farida (P-02 Dispatcher) · Kabir (P-03
Technician) · Mitu (P-21 Finance Officer)
**Trigger:** Tahmina's AC has stopped cooling. It is 9 p.m. and the hotline is busy.

| # | Who | Action | Touchpoint | Emotion | Pain resolved |
|---|---|---|---|---|---|
| 1 | Tahmina | Opens the portal on her Android, **in Bengali** | P01 | Cautious — expects English | No English barrier |
| 2 | System | Presents device → symptom → mode in 3 steps, **with an indicative price** | P01 booking | Reassured — she knows the cost | Cost uncertainty gone |
| 3 | Tahmina | Adds two photos and a Bengali voice note describing the noise | P01 | Understood | No struggle to describe in text |
| 4 | System | Creates the order, evaluates entitlement, sets SLA, acknowledges with a tracking link | M33 → M09/M08 → M01 → M27 | Confident | Immediate confirmation |
| 5 | System | Scores candidates on skill, **certification**, location, workload, van stock | M02, M22 | — | — |
| 6 | Farida | Reviews the ranked list with plain-language reasons; approves | P03 Dispatch | In control | 45 min → under 10 |
| 7 | System | Notifies Kabir and Tahmina; publishes the tracking link; updates the route | M27, M02 | — | — |
| 8 | Tahmina | Watches the technician approach on a live map with ETA | P01 tracking | **Stops worrying** | No more hotline calls |
| 9 | Kabir | Geofence detects arrival; Tahmina notified automatically | P02 | — | — |
| 10 | Kabir | Guided diagnosis; photographs before; drafts the estimate from the fault code | P02, M01, M36 | Efficient | 15 min of paper gone |
| 11 | Tahmina | Reviews the estimate on Kabir's phone, in Bengali; approves | P02 | Trusting — nothing hidden | No surprise bill |
| 12 | Kabir | Scans the part from van stock; repairs; QC checklist enforced | P02, M15, M23 | Thorough | Nothing missed |
| 13 | Kabir | Photographs after; Tahmina signs on screen | P02 | Professional | Proof for both |
| 14 | System | **Invoice generated in under 5 seconds**, Mushak-compliant; payment link sent | M20, M51 | — | 3–7 day delay gone |
| 15 | Tahmina | Pays by bKash from her own phone | P01 | Convenient | No cash needed |
| 16 | System | Matches the payment, posts to the ledger, closes the order, triggers the survey | M20, M19, M34 | — | — |
| 17 | Tahmina | Rates the service in Bengali in 10 seconds | P01 | Heard | Feedback that goes somewhere |

**Elapsed booking time: under 3 minutes.** Job documentation: under 5 minutes.
**If step 8–13 happen in a basement with no signal, every one of them still works** (§20).

---

### 18.2 Journey 2 — Walk-In to Handover

**Actors:** Abdul Karim (P-34c, 62, no smartphone) · Rashida (P-01 Agent) · Nurul (P-06 Workshop
Supervisor) · Shirin (P-21 Cashier)

| # | Who | Action | Touchpoint | Emotion |
|---|---|---|---|---|
| 1 | Abdul | Arrives; takes a token; sees his position and estimated wait on the queue display | M04 | Oriented, not anxious |
| 2 | Rashida | Types his phone number; party, devices and history fill in | P03, M33 | — |
| 3 | Rashida | Scans the laptop serial; entitlement resolved in 2 seconds | M17, M09, M08 | Confident — no phone call to Dell |
| 4 | System | Warranty expired → **the warranty path is blocked with an explanation**; the paid path is offered | BRU-SRM-02 | Abdul: told plainly, not fobbed off |
| 5 | Rashida | Selects category → brand → model → symptom; **indicative price shown** | M37, M11 | Abdul: knows roughly what it will cost |
| 6 | System | Calculates the promised date; prints token and internal job card | M01, M04 | Abdul: has proof in his hand |
| 7 | Nurul | Device appears on the bench board; assigns to an L2 bench | P03 Workshop, M31 | — |
| 8 | Technician | Diagnoses; estimate exceeds BDT 5,000 → **customer approval required before work** | BRU-SRM-07 | — |
| 9 | Rashida | Phones Abdul; records his approval; work is released | M36, M01 | Abdul: consulted, not presented with a bill |
| 10 | Technician | Repairs; QC enforced; second-person QC because the value exceeds BDT 25,000 | BRU-SRM-18, SOD-07 | — |
| 11 | System | Device ready → **SMS in Bengali** with branch address and hours | M27 | Abdul: told without calling |
| 12 | Rashida | Verifies identity; photographs condition at handover; Abdul signs | M04 | Both protected |
| 13 | Shirin | Takes cash; issues Mushak receipt; **closes her shift cleanly at 8 p.m.** | M50, M51 | No nightly argument |

**Intake time: under 3 minutes** — the Gate 1 criterion, timed by branch staff, 20 samples.

---

### 18.3 Journey 3 — Pick & Drop with Unbroken Custody

**Actors:** Rafiq (P-34a) · Shahin (P-09 Coordinator) · Jasim (P-10 Rider) · Workshop

| # | Who | Action | Touchpoint |
|---|---|---|---|
| 1 | Rafiq | Books pick & drop with a time slot from P01 | P01, M03 |
| 2 | Shahin | Sees the consignment; assigns to Jasim by area and load | P03/P09 coordinator |
| 3 | Jasim | Manifest appears in order on his phone | P09 |
| 4 | Jasim | **Scans the item, photographs it and the packaging, enters the seal number** | M03 |
| 5 | Jasim | Captures Rafiq's **OTP and signature**; issues a receipt | **BRU-LOG-01 — no custody transfer without scan and dual identity** |
| 6 | System | Custody event recorded with GPS, timestamp and both parties | M03 |
| 7 | Jasim | Loses signal in a basement car park — **the app keeps working**; events queue | §20 |
| 8 | Workshop | Receives; scans; **custody transfers again** with both parties recorded | M31, M03 |
| 9 | Workshop | Repairs; QC; ready | M01, M23 |
| 10 | Jasim | Return delivery; verifies recipient; scan, photo, OTP, signature | M03 |
| 11 | System | **A consignment cannot close without proof of delivery** | BRU-LOG-02 |
| 12 | System | Invoice generated; Rafiq pays by card from the portal | M20 |

**Custody breaks: zero.** POD capture completeness: **100%**. Every leg is provable.

---

### 18.4 Journey 4 — Warranty Claim to Reimbursement

**Actors:** Kabir (P-03) · Anisur (P-23 Claims Officer) · Tanvir Mahmud (P-36c, Samsung) · Kamal
(P-22 Finance Manager)

| # | Who | Action | Touchpoint |
|---|---|---|---|
| 1 | Kabir | Closes a Samsung warranty job — **before/after photos mandatory** | BRU-SRM-17 |
| 2 | System | **Creates the claim within 24 hours** and assembles the evidence pack | AUT-018, BRU-WTY-02 |
| 3 | System | Validates completeness **against Samsung's rule set**; all present | M09 brand rules |
| 4 | System | Checks for a duplicate on the same serial and fault within 90 days | BRU-WTY-03 |
| 5 | Anisur | Reviews; submits in Samsung's required format | M09, P08 |
| 6 | Tanvir | Opens P08; **the whole evidence pack is inline** — photos, diagnosis, parts, technician certification | P08 |
| 7 | Tanvir | Approves parts; part-rejects labour with a reason | P08 |
| 8 | System | Updates the claim; queues the approved portion for billing; opens a dispute task on the rest | AUT-020 |
| 9 | Anisur | Sees the rejection reason; a recurring pattern raises a non-conformance | M23 |
| 10 | Samsung | Remits; **the system matches the remittance to claims automatically** | AUT-021 |
| 11 | Kamal | Reviews unmatched items only; leakage reported continuously | M53, M19 |

**Submitted within 72 hours: 95%.** First-submission approval: **90%+**. Leakage: **under 2%**
(from 15–20%).

---

### 18.5 Journey 5 — Contract Sale to Renewal

| # | Who | Action | Touchpoint |
|---|---|---|---|
| 1 | Tania (P-16) | Quotes an IT Infrastructure AMC from a template | M36, M08 |
| 2 | Client | Accepts and signs digitally | M24 qualified e-signature |
| 3 | System | **Blocks activation until covered assets, entitlements, billing frequency and approval exist** | BRU-CTR-01 |
| 4 | System | Generates the **full preventive-maintenance schedule for the term** | AUT-016 |
| 5 | System | Creates the recurring subscription | M39 |
| 6 | System | Each PM visit due → work order → dispatch queue | AUT-017 |
| 7 | Client | Watches entitlement drawn down on P04 | M08, P04 |
| 8 | System | Out-of-scope work **billed separately, never absorbed** | BRU-CTR-02 |
| 9 | System | SLA breach → **service credit calculated automatically** | BRU-CTR-08 |
| 10 | System | **90 / 60 / 30 / 15 day** renewal notifications; quotation drafted at 60 | AUT-015 |
| 11 | Tania | Sees contract profitability **before** the renewal conversation | M54 |
| 12 | Client | Renews — or, on lapse, **future scheduled work orders are cancelled and the client told** | BRU-CTR-03 |

---

### 18.6 Journey 6 — MSP Alert to Monthly Report ★

| # | Who | Action | Touchpoint |
|---|---|---|---|
| 1 | Agent on a client server | Disk latency breaches threshold | M48, M05 |
| 2 | System | Correlates and de-duplicates; one alert, not forty | M05 |
| 3 | Sabbir (P-11) | One click to asset, history and **contract entitlement** | M05, M17, M08 |
| 4 | Sabbir | Starts a remote session — **consent captured before it begins** | M05, M29 |
| 5 | Sabbir | Resolves remotely; SLA burn-down stops | M05 |
| 6 | *Alternative* | Cannot resolve remotely → escalates to a service order and field dispatch | M01, M02 |
| 7 | System | SLA measured; breach would generate a **credit automatically** | BRU-CTR-08 |
| 8 | System | Monthly service report generated and published to the client | M25, P04 |
| 9 | Tania (P-16) | Reviews cost-to-serve against contract value before the QBR | M54 |

**Remote resolution: 65%.** SLA attainment: **98%**. The report is generated, not written.

---

### 18.7 Journey 7 — Marketplace Order to Payout ★

| # | Who | Action | Touchpoint |
|---|---|---|---|
| 1 | Jewel (P-36b) | Registers with NID and trade licence; OTP verified | P07, M12 |
| 2 | System | Identity and business-registry checks run | INT-034, INT-035 |
| 3 | Jewel | Signs the agreement digitally; pays the registration fee | M24, M12 |
| 4 | Imrul (P-19) | Reviews and approves — **Jewel cannot transact before this** | BRU-ECM-01 |
| 5 | System | Jewel may list **only in categories where he holds a verified qualification** | BRU-ECM-07, M22 |
| 6 | Customer | Requests a service; broadcast to qualifying sellers | M12, BRU-FSM-12 |
| 7 | Jewel | Quotes; the customer selects | P07 |
| 8 | System | **Customer contact revealed only for this awarded job, expiring after completion** | BRU-ECM-05, EA-04 |
| 9 | Jewel | Executes to **the same evidence and QC standard as an owned job** | BRU-ECM-03 |
| 10 | Customer | Signs off; **may review because the transaction completed** | BRU-ECM-02 |
| 11 | System | Commission accrued after the hold period | AUT-026 |
| 12 | System | **Payout blocked entirely if a dispute is open** | BRU-BIL-03 |
| 13 | Finance | Payout run; **approver of the seller cannot approve the payout** | SOD-06 |
| 14 | Jewel | Sees an itemised statement — **he understands exactly why he was paid that amount** | P07 |

**Payout accuracy: 100%.** Dispute rate: **under 1.5%**.

---

### 18.8 Journey 8 — Rental Out and Back ★

Reservation → **pre-dispatch condition report mandatory** *(BRU-RNT-01)* → agreement signed and
**deposit received before handover** *(BRU-RNT-02)* → delivery under custody (M03) → in use, usage
metered → return → inbound condition report → **damage charges derived from the outbound/inbound
difference, shown to the customer** *(BRU-RNT-03)* → **asset re-enters the pool only after cleaning,
servicing and functional test** *(BRU-RNT-04)* → billed on period + usage + damages.
**Overdue accrues automatically with escalating notification** *(BRU-RNT-05)*.

---

### 18.9 Journey 9 — Trade-In to Resale ★

```
Customer submits with photos (P01)
   → indicative valuation → collection under custody (M03) → inspection → firm offer
   → BRU-TRF-02: provenance and IMEI/stolen-device screening MUST pass before payment
   → payment; device becomes a 1000FiX asset (M17)
   → ┌──────────────────────────────────────────────────────────────┐
     │  BRU-TRF-01 — HARD GATE                                       │
     │  No device proceeds to refurbishment or resale without a      │
     │  CERTIFIED DATA DESTRUCTION RECORD (M06)                      │
     └──────────────────────────────────────────────────────────────┘
   → refurbishment work order (M14 + M31) → QA test protocol
   → grading against published criteria (BRU-TRF-03); supervisor override needs justification
   → ┌── resale listing (M38/M12) — battery health and known defects DISCLOSED (BRU-TRF-04)
     ├── harvest for parts (M15)
     └── route to e-waste (M18) → certified destruction → certified partner only → certificate
```

**Gate 6 criterion: zero refurbished units released without a destruction certificate.**

---

### 18.10 Journey 10 — E-Waste to Certificate ★

Collection booked from P01 or a corporate decommission project (P04) → collected under custody →
triage and disposition → **certified wipe or physical destruction** *(BRU-ESG-01)* → batched →
**transferred only to a partner whose certification is current at the transfer date**
*(BRU-ESG-02)* → **retrievable disposal certificate per unit** *(BRU-ESG-03)* → material recovery
credited → statutory e-waste return generated.
**92% diversion from landfill; disposal certificates on file 100%.**

---

### 18.11 Journey 11 — Data Recovery Under Custody ★

| # | Who | Action | Control |
|---|---|---|---|
| 1 | Customer | Requests recovery from P01 or the counter | — |
| 2 | Farhana (P-12) | Takes custody **under dual control** — two named people | US-DTS-001 |
| 3 | System | Case created with **confidentiality controls applied at creation** | FR-SRM-065 |
| 4 | Farhana | Opens the case — **step-up authentication required; the access is logged** | BRU-SEC-02, BRU-SEC-03 |
| 5 | Farhana | Attempts recovery; books cleanroom time; refers to a partner lab if beyond capability | M06 |
| 6 | System | Recovered index stored **S3, per-case keys, Bangladesh-resident** | NFR-086 |
| 7 | Farhana | Hands back to the customer with verification | M06 |
| 8 | System | **Purges at the agreed date unless a documented hold applies**; issues a purge certificate | BRU-SEC-04 |
| 9 | System | **Recovered data is never used as training data** | BRU-AIM-03 |

**Custody exceptions: zero** — the Gate 6 criterion. The customer never sees case content on the
portal; only status.

---

### 18.12 Journey 12 — Requisition to Payment

Reorder point reached → **alert with recommended quantity** *(AUT-031)* → requisition drafted →
approved by threshold → **PO issued only to an active, approved vendor** *(BRU-SCM-02)* → vendor
acknowledges on P05 → goods received and inspected → **failures quarantined, never shelved**
*(BRU-INV-07)* → landed cost allocated *(BRU-SCM-04)* → **three-way match; a mismatched invoice
cannot be approved for payment** *(BRU-SCM-01)* → **TDS deducted or the payment cannot proceed**
*(BRU-FIN-09)* → paid → **vendor scorecard updated automatically**.

---

### 18.13 Journey 13 — Payroll Cycle

| # | Who | Action | Control |
|---|---|---|---|
| 1 | System | Period ends; **attendance locked — payroll cannot finalise otherwise** | BRU-HRM-05 |
| 2 | Nasima (P-24) | Reviews exceptions surfaced **before** the run, each employee named | US-PAY-001 |
| 3 | System | Calculates tax, PF, gratuity and overtime (**pre-approved only**) | BRU-HRM-02 |
| 4 | System | Imports incentives from M57 — **calculated there, paid here** | SOD-30 |
| 5 | Rahim (P-26) + CFO | **Two approvals required; the preparer cannot approve** | BRU-HRM-06, SOD-03 |
| 6 | System | BEFTN file generated — **the approver cannot release it** | SOD-29 |
| 7 | System | Payslips distributed; posted to the ledger | AUT-046 |
| 8 | Employee | Sees their own payslip **and no one else's** | BRU-HRM-07, T4 |

**Under 4 hours. Corrections under 0.3%. Parallel run: two full pay cycles before Excel is
withdrawn.**

---

### 18.14 Journey 14 — Complaint to Verified Closure

Complaint raised on any channel → taxonomy, severity and SLA applied → investigated →
**root cause recorded** → non-conformance raised where systemic *(AUT-049)* → CAPA assigned with an
owner and a date → implemented → **effectiveness verified after the defined interval; the CAPA
cannot close without it** *(BRU-QMS-03)* → **the complaint cannot close without confirming the
outcome with the customer** *(BRU-QMS-04)* → **repeated non-conformance in the same process forces a
management review item** *(BRU-QMS-05)*.

---

### 18.15 Journey 15 — Month-End Close

| Day | Activity | Control |
|---|---|---|
| −3 | Bank statements imported; **auto-match ≥ 90%; only exceptions presented** | AUT-044 |
| −1 | Branch cash closed daily throughout the month; **an unclosed shift blocks the next opening** | BRU-FIN-10 |
| 1 | Close checklist runs: accruals, prepayments, FX revaluation, recurring journals | AUT-043 |
| 1 | **The period cannot close while unposted entries exist** | BRU-FIN-05 |
| 2 | Exceptions cleared; branch and consolidated P&L drafted | M19 |
| 3 | CFO reviews and hard-closes; **reopening requires CFO approval and is logged** | BRU-FIN-06 |
| 3 | **Management pack served from the warehouse — no manual compilation** | M25, M62 |
| by 15th | **Mushak 9.1 filed via vat.gov.bd** | NFR-100 |

**Close in ≤ 3 days**, from 15–20.

---

## 19. USABILITY REQUIREMENTS

### 19.1 Performance the User Actually Feels

| Interaction | Requirement | Why it matters to a user |
|---|---|---|
| Standard ERP screen | **≤ 2 s p95** (NFR-001) | Rashida has a queue behind her |
| API response | ≤ 400 ms p95 (NFR-002) | Every screen is built from these |
| Customer 360 load | ≤ 2 s (NFR-031) | The contact-centre agent is already speaking |
| Search, any entity **including Bengali** | ≤ 600 ms p95 (NFR-035) | Front-desk lookup must feel instant |
| Booking availability | ≤ 800 ms p95 (NFR-032) | The customer is mid-funnel |
| Dispatch board refresh | ≤ 1 s for **500 open jobs** (NFR-033) | Farida is watching it all morning |
| Live map update | ≤ 5 s from GPS emission (NFR-034) | The customer is watching a van approach |
| Technician app job list on 3G | **≤ 8 s cold, ≤ 2 s warm** (NFR-036) | Kabir is standing in the street |
| Offline sync after 24 h | **≤ 30 s on 3G** (NFR-037) | He wants to go home |
| Invoice from job closure | **≤ 5 s** (NFR-040) | The customer is waiting to pay |
| Executive dashboard | ≤ 5 s (NFR-038) | The CEO is in a meeting |
| Standard report | ≤ 20 s (NFR-005) | — |
| Bulk operation, 1,000 records | ≤ 60 s **with progress feedback** (NFR-041) | Silence reads as failure |
| Any action over 2 s | **Progress indicator, always** | — |

### 19.2 Navigation & Findability

| Requirement | Standard |
|---|---|
| Any record from any starting point | **≤ 4 clicks** (NFR-077) |
| Role workspace from home | **1 click** |
| Primary navigation | Maximum 7 top-level items |
| Global search | On every screen; **accepts Bengali and English simultaneously** |
| Breadcrumbs | On every drill-down screen |
| Browser back | Always behaves correctly; never loses form state |
| Recent items | Last 5 records accessible from navigation |
| Saved views | Users can save and share list views and filters |
| Bulk actions | On every list view, **with preview and confirmation** |
| Keyboard | **Full keyboard operation for intake, dispatch and finance** |

### 19.3 Mobile-First Standards

| Requirement | Standard | Persona driving it |
|---|---|---|
| Touch target | **≥ 44 × 44 px** | A-02 Kabir, A-03 Jasim |
| Primary actions | **Bottom, thumb-reachable** — not top-right desktop muscle memory | A-02 |
| One-handed operation | Every primary flow completable one-handed | A-02 |
| Gestures | **Never gesture-only** — every swipe has a visible button equivalent | A-06 |
| Scrolling | Single direction per screen; **no horizontal scroll** | All |
| Font size | **≥ 16 px** body on mobile | A-01, A-04 |
| Contrast | **Sunlight-readable**, exceeding the minimum ratio | A-02, A-03 |
| Input | Correct keyboard type per field; scan wherever a scan is possible | A-04 |
| Orientation | Functional in portrait and landscape | All |
| Field density | **Only the fields needed for the current task** | A-02, A-07 |

### 19.4 Error Handling & Feedback

| Scenario | Requirement |
|---|---|
| Validation error | Inline, adjacent to the field, **in the user's language** |
| Required field | Highlighted **and labelled** — never colour alone |
| Business rule block | **States the rule, why it applies and what to do instead** — e.g. "This technician's Dell certification expired on 12 May. Choose a certified technician or request an exception." |
| System error | Plain language, no stack trace, no bare error code, **with a route to report it** |
| Offline | Persistent, unmissable banner; **queued action count visible** |
| Long operation | Progress indicator with an estimate |
| Success | Confirmation that does not require dismissal to continue |
| Destructive action | Confirmation **naming the specific item**; reversible where possible |
| Permission denied | Explains that access is restricted **without revealing the protected content's existence or value** |

### 19.5 Consistency

One design system across all twelve portals (NFR-080). Status colour coding identical everywhere,
**always paired with an icon or text**. Primary action in a consistent position. Destructive actions
consistently styled. Numbers right-aligned, text left-aligned. **DD/MM/YYYY everywhere.** Currency
in **Bangladeshi lakh/crore grouping** in the Bengali locale.

---

## 20. OFFLINE & LOW-CONNECTIVITY USER EXPERIENCE

> This section applies to **P02 Technician**, **P09 Rider** and **P11 Field Auditor**. It is
> separated from general usability because **offline behaviour is the single largest determinant of
> field adoption**, and because the difference between an offline-first application and a connected
> application with caching is entirely in how it handles the cases below.

### 20.1 The Offline Contract

| # | Commitment | Measure |
|---|---|---|
| 1 | The device holds the user's work; the user completes it connected or not | **24 hours** (NFR-047) |
| 2 | Nothing is lost | **Zero data loss**; zero sync failures — Gate 2 criterion |
| 3 | Reconciliation is fast | **≤ 30 s on 3G** after 24 hours offline (NFR-037) |
| 4 | Every action is safe to retry | Idempotent commands with client-generated UUIDs |
| 5 | Nothing is half-applied | Checksums per batch; **failed batches retried, never partially applied** |
| 6 | The local store is secure | Encrypted; **scope limited to the user's own assigned work** |
| 7 | **No feature requires a connection the user cannot avoid** | Verified feature-by-feature at Gate 2 |

### 20.2 What the User Must Always Be Able to See

Industry experience is consistent: the failure mode is not lost data, it is **users who cannot tell
whether their work is safe**.

| State | What is shown |
|---|---|
| Connectivity | Network state visible at all times, not hidden in a menu |
| **"Saved here" vs "sent to the office"** | **Shown distinctly.** A technician must never confuse a local save with a submitted job |
| Queue depth | Count of pending actions, tappable to see what they are |
| Sync in progress | Progress with what is being sent |
| Sync succeeded | Explicit confirmation; the queue visibly empties |
| **Sync failed** | **What failed, why, and a recoverable action** — never a silent failure and never a dead end |
| Stale reference data | Age of the cached catalogue, price list or stock position, with a refresh option |

### 20.3 Conflict Resolution — The Design Discipline

A conflict occurs when the same record is changed independently in two places. **The system must
never silently pick a winner on something a user entered by hand.**

| Data class | Authority | Rationale |
|---|---|---|
| Assignment, pricing, stock, order state | **Server wins** | These are business decisions made centrally with fuller information |
| Evidence, notes, field-captured timestamps | **Client wins** | The technician was there; the server was not |
| Anything else in genuine conflict | **Surfaced for a human decision** | The system does not guess |

**User-facing requirements:**

| # | Requirement |
|---|---|
| CR-01 | **Any resolved conflict is shown to the user, stating what changed and why** |
| CR-02 | The user's original value is preserved and visible, not overwritten invisibly |
| CR-03 | Where a human decision is needed, it is presented as a clear choice — not an error |
| CR-04 | Conflicts are resolved in the app; the user is never told to "contact IT" |
| CR-05 | Conflict frequency is measured; a rising rate is treated as a design defect, not a user error |
| CR-06 | **Scripted conflict scenarios are part of every mobile release test suite** |

**Worked example.** Kabir completes a job offline at 11:20. Dispatch reassigned that job at 10:55.
On sync: the server's reassignment wins (assignment is server-authoritative), **but Kabir's
diagnosis, photographs and time entries are preserved and attached**, and Kabir is shown: *"This job
was reassigned to Mahbub at 10:55 while you were offline. Your work has been saved to the job — the
office can see it. Please check with dispatch before travelling to your next stop."*

### 20.4 Data Scope and Battery

| Requirement | Standard |
|---|---|
| Data scope | Only the user's assigned work plus the reference data they need; **re-evaluated at each sync** |
| Download | Delta since the last sync token; full refresh available on demand |
| Pruning | Synced, closed work older than the retention window pruned automatically |
| **Data cost** | Uploads compressed and non-critical uploads deferred — **the technician's own data allowance is a cost to them** |
| **Battery** | **≤ 12% per 8-hour shift excluding navigation** (NFR-082); location and sync frequency adaptive |
| Media | Photographs compressed on device before queueing; quality validated at capture, not after upload |

### 20.5 Degraded-Connectivity Behaviour (Portals)

For portals that are not offline-first, the requirement is **graceful degradation, explained**:

| Situation | Behaviour |
|---|---|
| ERP unavailable to the portal | Cached catalogue and branch data served; **booking queued with confirmation on recovery** |
| Payment gateway down | Alternative gateway offered; cash-at-counter explained; **payment link resent on restoration** |
| Map service down | Cached geocodes; manual address entry; routing falls back to the self-hosted engine |
| GPS stream down | Last known position with its timestamp; manual status updates |
| Notification channel down | Automatic fallback per the register — SMS → WhatsApp → push → in-app inbox |
| AI assistant down | **Rule-based responses and direct routing to a human** |

**In every case the user is told, in plain language, what is unavailable and what will happen next.**

---

## 21. ACCESSIBILITY & INCLUSIVE DESIGN

### 21.1 Contracted Standard

**WCAG 2.1 Level AA** on all web portals (NFR-073), verified by automated scan **plus manual audit
per portal** before each portal release.

### 21.2 Core Requirements

| Requirement | Standard |
|---|---|
| Contrast | ≥ 4.5:1 normal text, ≥ 3:1 large text — **exceeded on field surfaces for sunlight** |
| Colour independence | **Never colour alone**; always paired with icon, text or pattern |
| Keyboard | Every function reachable and operable by keyboard |
| Focus | Visible focus indicator on every interactive element |
| Screen reader | Semantic markup; accessible names on every control; **Bengali screen-reader compatibility verified** |
| Labels | Every input has a visible, programmatically associated label |
| Images | Meaningful alternative text; decorative images correctly marked |
| Zoom / reflow | **200% zoom without horizontal scroll**; responsive from 320 px |
| Motion | No essential information conveyed by motion alone; respects reduced-motion preference |
| Timeouts | **No form times out and discards entered data** without warning and extension |

### 21.3 Situational and Environmental Accessibility

The most common impairments in this user base are **situational**, not permanent — and they are
constant.

| Situation | Users | Design response |
|---|---|---|
| One hand occupied | Every field technician, always | Thumb-reach primary actions; no two-handed gestures |
| Direct sunlight | Field and rider, most of the day | High-contrast mode; large type; avoid thin weights |
| Gloves, wet hands | Riders, technicians in rain | Large targets; scan and tap over typing |
| Noise | Branch counters, street | Never rely on sound alone |
| Low literacy | Store keepers, riders, some technicians and customers | **Icons paired with Bengali text**; scan-first; voice input |
| Low-end device on 3G | Most field and customer users | Payload discipline; graceful degradation |

### 21.4 Recommendation — Move the Target to WCAG 2.2 AA

> **This is a change recommendation, not a unilateral change. The contracted standard in RFP v2.0
> remains WCAG 2.1 AA until the Steering Committee decides.**

**Finding.** WCAG 2.2 was published in October 2023 and, through 2026, has become the practical
enterprise and procurement benchmark; it is backward-compatible with 2.1 and adds nine success
criteria concentrated on **mobile interaction, cognitive load and low vision** — precisely this user
base.

**Why it matters here specifically:**

| WCAG 2.2 criterion | Direct relevance to 1000FiX |
|---|---|
| **2.5.7 Dragging Movements** | **The dispatch board is specified as drag-and-drop. Drag-only fails this criterion.** A single-pointer and keyboard alternative is required — this also serves persona A-06 and any dispatcher on a laptop trackpad |
| **2.5.8 Target Size (Minimum)** | Already exceeded by the 44 px field standard; formalises it |
| **3.2.6 Consistent Help** | Help in a consistent location across 12 portals — directly supports low-literacy users (A-01, A-04) |
| **3.3.7 Redundant Entry** | **"No user is asked to enter the same thing twice"** is already user commitment #5 |
| **3.3.8 Accessible Authentication** | No cognitive test in login — matters for A-01 Abdul and for technicians logging in with gloves |
| **2.4.11 Focus Not Obscured** | Sticky headers must not hide the focused field — a common defect on dense branch screens |

**Estimated incremental cost: low**, because five of the nine criteria are already met by
requirements this URD carries independently. **The one material gap is 2.5.7 on the dispatch board.**

**Recommendation:** adopt **WCAG 2.2 AA** as the target, and in either case **treat the
drag-and-drop alternative as mandatory** since it is required by A-06 regardless of which version is
contracted. Raise as a change request under §26.3.

### 21.5 Verification

| Method | When |
|---|---|
| Automated scan | Every build |
| Manual audit per portal | Before each portal release |
| **Testing with the accessibility personas** | Each wave gate |
| **Field testing in real conditions** — sunlight, gloves, one hand, weak signal | Before every mobile release |
| Bengali screen-reader verification | Before each portal release |

---

## 22. LOCALISATION & BANGLADESH-SPECIFIC REQUIREMENTS

### 22.1 Language

| Requirement | Standard |
|---|---|
| Languages | **Bengali (bn-BD)** and English (en) |
| Default | **Bengali on all customer and field surfaces**; English on back office |
| Toggle | Available on every screen; preference saved to the account |
| Completeness | **100% of user-facing strings before a module is accepted** (DoD-08) |
| **No fallback** | **A Bengali user must never see an English string** |
| Errors | Every error message translated — **error messages are the most common translation gap and the most damaging** |
| Quality | **Professionally translated and reviewed by a native speaker. Machine translation is not acceptable for release.** |
| Technical terms | Standard Bangla IT terminology with a glossary tooltip where no accepted term exists |
| Reports and documents | Headers, labels and generated documents in both languages |

### 22.2 Bengali Input & Rendering

| Requirement | Standard |
|---|---|
| Keyboard | Phonetic and Unicode layouts supported |
| Voice-to-text | **Bengali voice input for technician job notes and customer fault descriptions** |
| Search | Accepts Bengali and English **simultaneously** in the same query |
| Collation | ICU `bn-BD` for sorting and comparison |
| Fonts | Correct rendering on Android, iOS, Windows **and on thermal and label printers** — verified, not assumed |
| Minimum size | 16 px on mobile for legibility |

### 22.3 Formats

| Aspect | Standard |
|---|---|
| Date | **DD/MM/YYYY**; Bengali month names in the Bengali locale |
| Time | 12-hour with Bengali AM/PM equivalents; stored UTC, displayed **Asia/Dhaka** |
| Currency | **BDT ৳**, two decimals; **lakh/crore grouping (12,34,567)** in the Bengali locale |
| Numbers | International grouping in the English locale |
| Phone | **+880** with Bangladesh mobile operator validation; accepts 01XXXXXXXXX and +880 forms |
| National ID | **10-digit and 17-digit** formats validated |
| Fiscal year | **July–June** |
| Calendar | Gregorian with Bangladesh public holidays **including moon-dependent dates** |

### 22.4 Geography

**Division → District → Upazila/Thana → Union/Ward → Postcode**, covering **8 divisions and 64
districts**. Service zones for dispatch and territory. Geocoding with cached fallback. The platform
must support **200 branches without configuration redesign** (NFR-058).

### 22.5 Regulatory Touchpoints the User Sees

| Requirement | User-visible consequence |
|---|---|
| **Mushak 6.3** tax invoice | Every customer invoice, correctly formatted, with the Company's BIN |
| **Mushak 9.1** monthly return | Prepared automatically; **filed by the 15th via vat.gov.bd** |
| Input VAT credit | **Blocked without a valid Mushak 6.3 invoice** |
| TDS/VDS | Deducted at source; the payment cannot proceed otherwise |
| Bangladesh Labour Act 2006 | Appointment letter, identity card, service book, leave, overtime, gratuity |
| Labour Rules 2015 | Safety committee, safety officer, first aid, accident notification |
| **PDPA 2026** | Transparency notice before capture; consent per purpose; data-subject rights; **breach notification to the National Data Management Authority** |
| **Data residency** | NID, passport, TIN, biometrics and recovered data **held in Bangladesh** (NFR-086) |
| Cyber Security Ordinance 2025 | Replaces the repealed Digital Security Act 2018 — **v1.0 cited a statute repealed twice** |

### 22.6 Payment Methods

**bKash · Nagad · Rocket · SSLCOMMERZ (card and net banking) · cash · bank transfer.**
Payment path availability **≥ 99.95% with multi-gateway failover** (NFR-048); confirmation round
trip **≤ 3 s p95** (NFR-042).

---

## 23. NOTIFICATION & COMMUNICATION REQUIREMENTS

### 23.1 Principle

**One notification service serves every module** (M27). No module builds its own send path.
One template engine, one delivery service, one preference model, one log.

> **Sequencing decision Q-05a is a user-experience decision as much as an architectural one.** M27 is
> scheduled for W4, but customers must be notified from W1. If each earlier module builds its own
> notifications, customers will receive inconsistent messages from inconsistent senders in
> inconsistent language. **Decision required before Wave 1 build.**

### 23.2 Channels

| Channel | Used for |
|---|---|
| **SMS** | All customers; every critical alert; reaches non-smartphone users (Abdul, P-34c) |
| **WhatsApp** | Booking confirmation, tracking links, invoices, feedback requests |
| **Push** | Technicians, riders, agents, managers, sellers |
| **Email** | Invoices, statements, reports, contract documents, corporate clients |
| **In-app inbox** | Every message ever sent to that user, retrievable |
| **Voice (hotline 16743)** | Inbound; outbound where the customer prefers it |

### 23.3 Customer Notifications

| Event | Channel | Language | Timing |
|---|---|---|---|
| Order created | SMS + WhatsApp + push | **Bengali** | Immediate |
| Estimate issued | Preferred channel | Bengali | Immediate; **reminders at 24 h and 48 h** |
| Technician dispatched | SMS + push | Bengali | On dispatch |
| Technician en route with ETA | SMS + push | Bengali | On travel start |
| Technician arrived | SMS | Bengali | On geofence arrival |
| Job on hold | Preferred | Bengali | **With the reason and a revised ETA** |
| Ready for collection | SMS | Bengali | On QC pass |
| Invoice issued | Email + SMS | Bengali/English | On generation |
| Payment received | SMS | Bengali | On confirmation |
| Feedback request | SMS/push | Bengali | After the configured delay |
| Uncollected device | SMS | Bengali | **3, 7, 15, 30 days** |
| Warranty expiring | SMS + email | Bengali | 30 days before |
| Contract renewal | SMS + email | Bengali | **90 / 60 / 30 / 15 days** |
| Consignment status | SMS + push | Bengali | On each custody change |

### 23.4 Internal Notifications

| Recipient | Event | Channel | Timing |
|---|---|---|---|
| Technician | New or changed assignment | Push + SMS | Immediate |
| Technician | Parts request decided | Push | Within 30 min |
| Technician | **SLA warning on own job** | Push | 60 min before |
| Technician | Certification expiring | Push + email | **90/60/30/15 days** |
| Dispatcher | Unassigned job at SLA risk | In-app + push | At 50% elapsed |
| Manager | **SLA breach** | Push + email | Immediate |
| Manager | High-priority complaint | Push + email | Immediate |
| **HSE Officer** | **Serious incident reported** | **Push + SMS** | **Immediate** |
| Inventory Manager | Stock at reorder point | Daily digest | Daily |
| Finance | Payment auto-match exception | In-app | On occurrence |
| Claims Officer | **Brand submission window closing** | Email + in-app | Before expiry |
| IT Administrator | Integration failure, dead letter, credential expiry | Push + email | Immediate / 30 days |
| **CDO** | **Potential personal-data breach** | **Push + email** | **Immediate** |

### 23.5 Preferences, Quiet Hours and Consent

| Requirement | Standard |
|---|---|
| Preferences | Per user, per notification category, per channel |
| **Quiet hours** | No non-urgent notification between 22:00 and 07:00 |
| Emergency override | SLA breach, serious safety incident and security alerts bypass quiet hours |
| Digest | Non-urgent notifications bundled, configurable |
| **Marketing opt-out** | Honoured **immediately and absolutely** |
| Operational messages | Continue where lawful, even after marketing opt-out — **and this is explained to the customer** |
| **Do-not-contact** | Honoured absolutely, applied **at send time** |
| Inbox | Everything sent is retrievable in the in-app inbox |

### 23.6 Message Standards

| Requirement | Standard |
|---|---|
| Language | **Bengali by default**; English on preference |
| Reference | Every operational message carries the job or document reference |
| Length | Standard SMS ≤ 160 characters where possible |
| Sender | Registered sender ID |
| Opt-out | Promotional messages carry an opt-out instruction |
| **Tone** | Plain, respectful Bengali. **Not machine-translated. Not transliterated English.** |
| Delivery | Tracked; failure falls back per the channel register; **failure is visible to the sender** |

---
---

# PART D — HOW USERS GET THERE

---

## 24. TRANSITION REQUIREMENTS & USER ADOPTION

### 24.1 Adoption Is The Programme's Largest Risk

Three of the eight Critical risks are adoption risks: **RSK-008** technician rejection,
**RSK-001** business availability for UAT, **RSK-009/RSK-012** branch and management resistance.
Industry analysis of field-service deployments finds adoption, not capability, to be the dominant
failure mode. **This section is therefore a delivery requirement, not an annex.**

### 24.2 Training by Role

| Role group | Users | Hours | Format | Language | Timing |
|---|---:|---|---|---|---|
| Service centre agents | 150–250 | 16 h | Hands-on at the workstation | **Bengali** | Week before go-live, batches of 30 |
| **Field technicians — senior** | 80–150 | 8 h | App walkthrough + demo jobs | **Bengali** | 5 days pre-go-live, peer-led |
| **Field technicians — junior** | 120–250 | 12 h | Guided tutorial + sandbox | **Bengali** | 5 days pre-go-live |
| Workshop supervisors & specialists | 35–70 | 8 h | Bench board + repair-level workflows | Bengali | 1 week pre |
| **Riders & logistics coordinators** ★ | 60–175 | 6 h | Manifest, custody, cash — **on the device** | **Bengali** | 1 week pre |
| Dispatch managers | 3–8 | 8 h | Scenario-based | Bengali/English | 1 week pre |
| Branch managers | 51+ | 6 h | Console, approvals, cash | Bengali | 1 week pre |
| Operations & executives | 5–10 | 4 h | Analytics and drill-down | Bengali/English | 1 week pre |
| **Contact centre** ★ | 34–70 | 12 h | Console, screen-pop, disposition, quality | **Bengali** | 2 weeks pre |
| **MSP engineers** ★ | 15–40 | 16 h | Monitoring, ticketing, remote, reporting | English/Bengali | 2 weeks pre |
| **Data services technicians** ★ | 5–12 | 16 h | **Custody, dual control, destruction, PDPA** | Bengali/English | 3 weeks pre |
| Inventory, warehouse, procurement | 75–125 | 8 h | Scanner-driven workflows | **Bengali** | 1 week pre |
| Finance & cashiers | 61–71 | 12 h | Invoicing, Mushak, reconciliation, cash | **Bengali** | 2 weeks pre |
| **Payroll & HR** ★ | 5–11 | 16 h | Payroll, statutory, segregation | Bengali | 3 weeks pre |
| Quality & auditors | 5–15 | 10 h | Audit app, CAPA, evidence | Bengali | 2 weeks pre |
| **Retail / refurbishment** ★ | 5–15 | 10 h | Valuation, wipe gate, grading | Bengali | 2 weeks pre |
| **Marketplace operations** ★ | 4–10 | 12 h | Onboarding, scoring, disputes, payouts | Bengali/English | 2 weeks pre |
| IT administrators | 4–8 | 24 h | Administration, security, configuration | English | 4 weeks pre |
| **Company developers** ★ | 3–6 | **20+ days across the programme** | Pair working + deep dive | English | Continuous |
| Corporate clients | 500–2,000 | 2 h | Portal webinar + guide | English/Bengali | 1 week before P04 |
| **Marketplace sellers** ★ | 500–2,000 | Self-service | In-app onboarding, video | **Bengali** | At registration |
| Brand partners | 50–150 | 2 h | Portal walkthrough | English | 1 week before P08 |
| Vendors | 200–500 | 1 h | Portal guide + video | **Bengali** | 1 week before P05 |

### 24.3 Training Materials

| Material | Format | Language |
|---|---|---|
| Quick reference card — top 10 daily tasks | Laminated print + PDF | **Bengali** |
| Role-based user manual | PDF | Bengali + English |
| **Video tutorials, 10–15 min per workflow** | MP4 | **Bengali narration** |
| In-app contextual help and tooltips | In-app | Bengali |
| **Guided first-login onboarding wizard per role** | In-app | Bengali |
| **Sandbox with demo jobs** — practise without touching a real customer | Training environment | Bengali |
| FAQ — 50 most common questions per role | PDF + in-app | Bengali |
| Escalation contact list | Print | Bengali |
| Operational runbook per module | PDF | English |

### 24.4 The Champion Network

- **One trained champion per branch** — 51+ champions
- Trained **one week ahead** of their branch
- First point of contact for branch-level questions
- 8 hours of advanced training across every module affecting their branch
- The role is **recognised in the HR system** and carries a dedicated support channel
- **Monthly champion forum** for issue sharing
- **For P02: the pilot runs with respected senior technicians first.** Peer credibility is the single
  most effective adoption lever available and costs nothing.

### 24.5 Parallel Running

| Process | Parallel period | Why |
|---|---|---|
| Service orders | 2 weeks | Operational safety |
| Inventory | 2 weeks + full count at cutover | Valuation accuracy |
| Finance | **1 full month-end** | Reconciliation confidence |
| **Payroll** | **2 full pay cycles** | **Zero tolerance for pay errors** |
| Warranty claims | 1 month | Brand relationship protection |

**Rollout pattern per location:** T−4 site readiness · T−3 data preparation · T−2 champion training ·
T−1 all-staff training in Bengali, access provisioned · T−3 days cutover and parallel run begins ·
T−0 go-live with on-site floor-walkers · T+2 weeks parallel run ends and legacy withdrawn ·
T+4 weeks hypercare ends and adoption reviewed.

### 24.6 Adoption Risk and Mitigation by Group

| Group | Risk | Mitigation the programme must deliver |
|---|---|---|
| **Field technicians** | **Critical** — rejection collapses the field model | Bengali-first; **extreme simplicity**; one-handed design; pilot with respected seniors **before** rollout; Company-provided devices; **earnings and incentive visible as an immediate personal benefit**; champion network; **simplified "lite" mode held as contingency** |
| **Riders** ★ | High — low literacy, hostile conditions | Scan-over-type; very large targets; peer training on the device; **proof of handover framed as protection for them** |
| Branch counter staff | High — highest transaction volume | **Speed as the explicit design goal** with measured intake time; involve resistors in design and UAT |
| Finance staff | Medium — control tightening | Early design involvement; parallel running; **audit-trail benefit emphasised as protection** |
| Branch managers | Medium — visibility cuts both ways | **Position dashboards as their tool, not surveillance**; involve them in KPI design |
| **Contact centre** ★ | Medium — measured on handling time | Show the screen-pop time saving early; **do not add steps to a measured process without removing others** |
| **Marketplace sellers** ★ | High — external, **switching cost near zero** | Simple Bengali onboarding; **fast, transparent payouts**; scoring explained in advance; seller advisory group |
| Corporate clients | Medium | Account-manager-led onboarding; demonstrable time saving |
| Management | Medium — reversion to spreadsheets | **Retire the source data for manual packs**; require decisions to cite the dashboard |

### 24.7 Adoption Measurement

Measured **weekly by role and by branch**, with intervention where adoption lags.

| Metric | Target | From |
|---|---|---|
| Service orders created in the ERP | **100%** | Gate 1 |
| Technician app daily active usage | **≥ 95%** | W2, continuous |
| Jobs documented in-app rather than paper | **100% in Dhaka** | Gate 2 |
| **Offline sync failures** | **Zero** | W2, continuous |
| Rider POD capture completeness | **100%** | Gate 3 |
| Customers self-booking | 60% pilot → **88%** | Gate 2 → W8 |
| Vendors acknowledging POs via portal | **> 90%** | W3 |
| Corporate clients active on P04 | **> 85%** | W4 |
| Brand claims via portal vs email | **> 80%** | W4 |
| Conversations captured | **100%** | Gate 4 |
| Employee self-service adoption | **85%** | W5 |
| Audits completed on mobile | **100%** | Gate 5 |
| Marketplace sellers monthly active | **> 70%** | W7 |
| Manual management packs remaining | **Zero** | Gate 8 |
| **System Usability Scale, every internal role** | **≥ 75** | Post-training, each wave |
| Crash-free sessions (mobile) | **> 99.5%** | Continuous |
| Technician satisfaction with the app | **> 4.2/5** | Quarterly |

### 24.8 What the Company Must Provide

| Commitment | Detail |
|---|---|
| **Super-user time** | **30% during UAT**, 10% otherwise — **this is the binding constraint on the programme (RSK-001)** |
| Module business owners | 20% of time during their waves |
| Branch champions | 4 hours/week during rollout |
| Data owners | 20% during migration |
| Executive sponsorship | Visible, monthly, from the CEO |
| **Devices** | Company-issued Android 11+ for technicians, riders and auditors (decision D-11) |
| Connectivity and hardware | Site readiness confirmed T−4 weeks per location |

> **The Company accepts that a wave gate slips rather than allowing development to run ahead into
> unaccepted work.**

---

## 25. USER ACCEPTANCE CRITERIA

### 25.1 Story-Level

No story is accepted until: every acceptance criterion passes · **negative tests confirm hard
business rules block through both the UI and the API** (DoD-04) · **role-based negative tests confirm
the role cannot see or do what it must not** (DoD-07) · **Bengali translation is 100% complete
including error messages** (DoD-08) · performance meets the applicable NFR (DoD-14) ·
**a named business super-user has signed it off** (DoD-13).

### 25.2 Portal-Level Sign-Off

**P01 Customer Portal**
- [ ] Booking completed in **≤ 3 steps and under 3 minutes** by 10 test users unfamiliar with the system
- [ ] **Entirely in Bengali with no English fallback on any screen or error**
- [ ] Live tracking visible within 60 seconds of dispatch; **public link works without login**
- [ ] bKash and Nagad payments complete end to end
- [ ] Works on Android 9 and iOS 14; **no horizontal scroll from 320 px**
- [ ] **Critical path under 400 KB first load**; usable on 3G
- [ ] Consent, transparency notice and data-subject request all reachable from the account

**P02 Technician App** — *the highest-risk acceptance in the programme*
- [ ] **24-hour offline operation with zero data loss**, demonstrated end to end
- [ ] **Sync completes within 30 seconds on 3G** after 24 hours offline
- [ ] **Scripted conflict scenarios resolve correctly and are shown to the technician**
- [ ] Complete Bengali interface **including every error message**
- [ ] Runs acceptably on a **mid-range Android 11 with 3 GB RAM**
- [ ] **Battery ≤ 12% per 8-hour shift** excluding navigation
- [ ] **Every primary flow completable one-handed**
- [ ] Job documentation in **under 5 minutes**, measured with real technicians
- [ ] **Field-tested in the weakest-coverage areas**, not only in the office
- [ ] Crash-free sessions > 99.5%

**P03 Admin Portal**
- [ ] **Walk-in intake under 3 minutes**, timed, 20 samples, **by branch staff**
- [ ] Full morning dispatch queue assigned in **under 10 minutes**
- [ ] Any record reachable in **≤ 4 clicks**
- [ ] Usable at **1366×768 without horizontal scroll**
- [ ] New agent reaches competence in **under 4 hours** of training
- [ ] Keyboard-complete for intake, dispatch and finance
- [ ] **Drag-and-drop actions have a keyboard and single-pointer equivalent** (§21.4)

**P04 Corporate B2B** — bulk CSV of 45 devices validated against coverage and created in under 5
minutes · consolidated invoice itemised by site, department and asset · SLA and service credits
visible · compliance certificates downloadable · **client sees only their own data**.

**P05 Vendor** — PO acknowledged, invoice submitted and payment status checked **in three screens,
in Bengali** · own scorecard visible · **no cost, margin or other vendors' data reachable**.

**P06 Analytics** — executive dashboard loads **≤ 5 s** · drill from group revenue to a single job ·
row-level security verified by negative test · mobile-usable.

**P07 Marketplace Seller** — registration completable on a mid-range Android **in Bengali** ·
KYC gate blocks transaction before approval · earnings and payout always visible and itemised ·
scoring consequences stated in advance.

**P08 Brand Partner** — claim queue with ageing · **full evidence pack inline** · decisions returned
automatically · **sees only their own brand**.

**P09 Logistics & Rider** — **full offline operation** · **POD capture 100%** · usable with gloves in
sunlight · cash reconciled at shift end.

**P10 Contact Centre** — unified queue across six channels · **screen-pop before the agent speaks** ·
**fewer than 3 screen switches per contact** · disposition coding 100%.

**P11 Field Auditor** — **complete audit executed offline with evidence** · findings raised on device ·
auditee signature captured · syncs without loss.

**P12 Partner & Referral** — referral tracking to conversion · commission statement accurate to the
taka · payout schedule visible.

### 25.3 Usability Testing Pass Criteria

| Criterion | Threshold |
|---|---|
| **System Usability Scale** | **≥ 75** for every role group |
| Task completion, unassisted | ≥ 90% of representative tasks |
| Critical usability defects | **Zero at sign-off** |
| Error recovery | 100% of users recover from a scripted error without help |
| **Bengali comprehension** | **100% of Bengali-only testers complete their journeys unassisted** |
| Accessibility | WCAG conformance verified by scan **and manual audit**; **persona-based testing passed** |
| First-use success | New user completes their primary task after the onboarding wizard alone |

### 25.4 Wave Gate — User Acceptance Criteria

| Gate | User-facing criterion |
|---|---|
| **G1** Foundation | Orders from all live channels · **intake < 3 min by branch staff** · **100% Bengali on delivered screens** · SSO for all delivered roles · **PDPA consent and notice operating** · UAT signed by named super-users |
| **G2** Field Ops | **100% of Dhaka technicians using the app daily** · **24 h offline, zero data loss** · sync ≤ 30 s on 3G · **paper service forms withdrawn in Dhaka** · online booking ≥ 60% at pilot |
| **G3** Money & Movement | Every invoice auto-generated · Mushak accepted with **zero NBR exceptions** · **pick & drop with zero custody exceptions** · branch cash reconciling daily |
| **G4** Agreements & Contact | Claims submitted within 72 h · **hotline conversations captured** · AI assistant resolving ≥ 40% of first contacts · 10+ corporate clients transacting · **PDPA data-subject rights operational** · **every v1.0 requirement demonstrated or formally superseded** |
| **G5** People & Quality | **First payroll paid with zero errors** · **zero uncertified technicians assignable to brand warranty work** · ISO audit executed entirely in the system · **all 51+ centres live** |
| **G6** New Businesses | Rental with full condition and deposit control · **zero refurbished units released without a destruction certificate** · **data-services custody with zero exceptions** · auto-assignment ≥ 50% with **≥ 88% dispatcher agreement** |
| **G7** Marketplace | 200+ sellers transacting · **payout accuracy 100%** · **marketplace jobs meeting the same quality and evidence standards as owned jobs** · VAT treatment externally validated |
| **G8** Intelligence | **Zero manual management packs** · automation of routine work **≥ 85%** · every production model has a model card and drift monitoring |
| **G9** Expansion | Second-country entity stood up in **≤ 12 weeks by configuration only** · documentation handed over and accepted · **support model transitioned** |

### 25.5 Go-Live Readiness Checklist (Per Wave, Per Location)

- [ ] Site readiness confirmed — connectivity, hardware, printers, scanners, staffing
- [ ] Data migrated and **reconciliation signed by the named data owner**
- [ ] All affected users trained **in Bengali** and access provisioned
- [ ] Branch champion trained and identified to staff
- [ ] **Sandbox practice completed** by every user of a new mobile app
- [ ] Parallel run completed for the required period
- [ ] Escalation path published and tested
- [ ] Floor-walkers scheduled for go-live week
- [ ] Rollback plan documented **and rehearsed** (DoD-16)
- [ ] Runbooks delivered (DoD-11)
- [ ] **Zero open critical or high security findings** (DoD-15)
- [ ] Adoption baseline captured — **a KPI without a baseline cannot claim a benefit**

---

## 26. ASSUMPTIONS, CONSTRAINTS & DISCLOSED OPEN ITEMS

### 26.1 User-Facing Assumptions

| ID | Assumption | If false |
|---|---|---|
| ASM-01 | All service centres have at least 3G during operating hours | Extended offline windows; SMS fallback; connectivity investment |
| ASM-02 | Technicians will use **Company-issued Android 11+** devices | Procurement cost added; support matrix widened |
| ASM-06 | Business stakeholders commit the stated time | **Waves slip — RSK-001, the highest-rated risk** |
| ASM-16 | Go-live avoids Ramadan and the Eid peaks | Wave dates adjusted |
| **ASM-19** | **Technicians can read Bengali interfaces** | **Icon-led and voice-led interface variants required** — this would materially change P02 |
| ASM-20 | Biometric attendance hardware procured before Wave 5 | GPS-only clock-in |
| ASM-23 | Marketplace seller supply exists in the target categories and areas | Marketplace benefit case reduces |
| **U-ASM-01** | Field technicians will accept a mobile-first way of working **if it is faster than paper** | **If the app is slower than paper it will be rejected — RSK-008, Critical** |
| **U-ASM-02** | Customers will self-serve **if the flow is in Bengali and under three steps** | Hotline load does not reduce; the CSAT and cost targets are missed |
| **U-ASM-03** | Marketplace sellers will tolerate a scoring regime **if payouts are fast and scoring is transparent** | Seller supply does not materialise; BO-12 fails |

### 26.2 Traceability to URD v1.0

**No v1.0 user story has been deleted.** Mapping:

| v1.0 story range | v2.0 location |
|---|---|
| US-SRM-001…023 | `US-SRM-*` (M01), `US-WSR-*` (M31), `US-FRD-*` (M04) |
| US-FSM-001…018 | `US-FSM-*` (M02), `US-LOG-*` (M03) |
| US-INV-001…010 | `US-INV-*` (M15), `US-WMS-*` (M41) |
| US-CRM-001…006 | `US-CPM-*` (M33), `US-CRM-*` (M07), `US-LOY-*` (M10), `US-CXM-*` (M34) |
| US-FIN-001…009 | `US-ARB-*`, `US-FIN-*`, `US-TAX-*`, `US-TRE-*`, `US-APE-*` |
| US-HRM-001…007 | `US-HCM-*`, `US-WFM-*`, `US-PAY-*`, `US-PIC-*`, `US-LMS-*` |
| US-CWM-001…004 | `US-CTR-*` (M08), `US-WTY-*` (M09) |
| US-CSP / TMP / AOP / CBP / VPP / ADB | `US-POR-*` across P01–P12 |

### 26.3 Disclosed Open Items Affecting Users

These are inherited defects and open decisions in the specification set. They are disclosed because
a design or training plan built on a hidden defect will fail.

| # | Item | User consequence | Status |
|---|---|---|---|
| **U-01** | **R60 is a duplicate role identity for R32 (Quality Manager)** | **An access rule written against R32 does not apply to a user granted R60. This is a live permission defect: a quality manager could see or do something they should not, or be blocked from something they should.** Must be eliminated before any role is provisioned | **Open — Wave 1** |
| **U-02** | **Roles R39–R46 are used but unregistered; R54 and R57 are referenced with no definition** | Eight real roles — including the **statutory Chief Data Officer** — have no registered permission set. **Design and test against 46 roles** | Open — Wave 1 |
| **U-03** | **18 of 30 segregation-of-duties controls are unregistered** | A user may be granted an incompatible combination the system was specified to block. **Controls that cannot be evidenced do not exist for audit purposes** | Open — Wave 1 |
| **U-04** | **Q-05a — M27 notification service scheduled for W4 but needed from W1** | **Customers would receive inconsistent messages from inconsistent senders in inconsistent language for three waves** | **Decision required before Wave 1 build** |
| **U-05** | **Q-01 — M32 assistant depends on M61 knowledge, two waves later** | The assistant can answer "what is my order status" but **not "how do I" or "why is this happening"** — the questions customers actually ask at midnight | Decision required |
| **U-06** | **Q-05b — M59 mobile safety reporting scheduled W6, deliverable W3** | **Field safety reporting stays on paper for three extra waves for no technical reason** | Decision required |
| **U-07** | **M22 eligibility check consumed by M02 in W2 but M22 lands in W5** | The dispatch block must be **stubbed in W2 and connected in W5**. Retrofitting a blocking check into a live assignment path is materially riskier | Design constraint — mandatory |
| **U-08** | **M66 and M67 have no specification** | `US-ITS-001` and `US-PPM-001` are written against an unspecified module; the internal helpdesk experience is undefined | Open — before W6 |
| **U-09** | **WCAG target is 2.1 AA; 2.2 AA is the 2026 enterprise benchmark** | **The drag-and-drop dispatch board fails WCAG 2.2 SC 2.5.7 without a keyboard/single-pointer alternative** — and fails persona A-06 under either version | **Change request — §21.4** |
| **U-10** | **D-13 split-residency architecture unapproved** | Where the data-services and identity-document experiences physically live is unconfirmed. **Retrofitting residency into a live system is the most expensive class of rework** | **Blocking Wave 1 architecture** |
| **U-11** | **D-15 Chief Data Officer appointment unconfirmed** | Persona P-32's statutory half has **no appointed holder**, while **PDPA enforcement begins ~13 May 2027, inside Wave 4** | Decision required, W4 − 3 months |
| **U-12** | **D-03 marketplace principal-vs-agent model undecided** | Seller-facing commission and payout presentation cannot be finalised; **it must be built configurable** | Decision required, W7 − 3 months |
| **U-13** | **"17+ brands" unverified** | Certification coverage messaging to technicians and brand partners rests on an unverified figure | Open — before W5 |

### 26.4 Constraints Users Will Feel

| ID | Constraint | User experience |
|---|---|---|
| CON-03 | The Next.js portal platform cannot be replaced | The customer sees one experience; two systems maintain it under a versioned contract |
| CON-05 | Bengali is primary for field and customer surfaces | **Translation is a definition-of-done item, not a follow-up** |
| CON-07 | Field applications must operate offline | **Offline-first is non-negotiable** — it shapes every P02, P09 and P11 design decision |
| CON-08 | No go-live during Ramadan or Eid | Training and cutover dates work around the Islamic calendar |
| CON-09 | **Sensitive personal data must be Bangladesh-resident** | Some features may carry additional latency; the split is invisible to the user but real |
| CON-10 | Automation augments roles; it does not displace staff without approval | Change messaging must be honest about this — **staff will ask** |
| CON-12 | Super-user time is finite | **UAT capacity, not developer capacity, paces the programme** |

---

## 27. APPENDICES

### Appendix A — Story Coverage by Category

| Category | Modules | Stories | Portals covered |
|---|---:|---:|---|
| A — Service Delivery & Operations | 7 | 58 | P02, P03, P09 |
| B — Customer Engagement & Experience | 7 | 29 | P01, P10 |
| C — Commercial, Pricing & Revenue | 9 | 30 | P01, P04, P07, P08, P12 |
| D — Circular & Asset-Based Business | 3 | 12 | P01, P03 |
| E — Supply Chain & Inventory | 6 | 17 | P03, P05 |
| F — Asset, Equipment & Facilities | 5 | 6 | P03, P04 |
| G — Finance & Treasury | 8 | 19 | P03, P04, P08 |
| H — People & Workforce | 7 | 17 | P02, P03 |
| I — Governance, Risk, Quality & Knowledge | 4 | 10 | P03, P11 |
| J — Data, Analytics & Intelligence | 4 | 8 | P06, P03 |
| K — Platform & Technology | 7 | 13 | All |
| Portals (cross-cutting and portal-specific) | — | 36 | P01–P12 |
| **Total** | **67** | **255** | **12** |

*Counted by direct enumeration of bolded story identifiers on 13 August 2026 under register rule
RG-06 (count, do not consult). Module counts per category reconcile to the authoritative register.*

**Story density is deliberately uneven.** Categories A and B carry the highest story counts because
they contain the surfaces users touch most often and the two highest-risk adoption journeys (P02
technician, P10 contact centre). Category F carries the fewest because most of its user interaction
is mediated through Category A and G surfaces rather than having its own. **Story count is not a
proxy for effort** — Category C carries 30 stories against 262 person-weeks, the largest build in the
programme.

### Appendix B — Persona-to-Role Coverage

All **46 roles (R01–R46)** are represented across **36 personas** plus **7 accessibility personas**.
See §3.1 for the index. Roles R45 (Recruiter) and R46 (Occupational Health) are covered within P-27
and P-28. R38 covers five external archetypes within P-36.

### Appendix C — URD v2.0 Audit Record

This document was audited on issue against RFP v2.0, BRD v2.0 and the underlying module
specification set, under governance rule **RG-06 (count, do not consult)** — every figure was
re-derived by direct enumeration rather than accepted from a prior statement.

#### Method

| # | Check | How |
|---|---|---|
| 1 | Story count and duplication | Extract every bolded `US-` identifier; deduplicate; compare |
| 2 | Story distribution by category | Map every story code to its owning module category and re-add |
| 3 | Role coverage | Enumerate R01–R46 and confirm each appears |
| 4 | Persona coverage | Enumerate persona identifiers and map to roles |
| 5 | Portal coverage | Enumerate P01–P12 |
| 6 | Business objective coverage | Enumerate BO-01…BO-18 |
| 7 | Journey completeness | Count journey sections against the programme's 15 critical journeys |
| 8 | Cross-document consistency | Grep 10 headline figures across URD, RFP and BRD |
| 9 | Structural integrity | Section headings, chunk markers, orphaned cross-references |

#### Verified clean

| Check | Result |
|---|---|
| Distinct user stories | **255** ✓ · **no duplicate definitions** |
| Story distribution sums to total | 58+29+30+12+17+6+19+17+10+8+13+36 = **255** ✓ |
| Roles | **all 46 (R01–R46) present, none missing** ✓ |
| Personas | **36 (P-01…P-36)** + **7 accessibility personas (A-01…A-07)** ✓ |
| Portals | **all 12 (P01–P12)** ✓ |
| Business objectives | **all 18 (BO-01…BO-18)** ✓ |
| Journey maps | **15**, matching the programme's critical journeys ✓ |
| Module counts per category | 7+7+9+3+6+5+8+7+4+4+7 = **67** ✓ |
| Cross-document consistency | 10 headline figures consistent with RFP v2.0 and BRD v2.0 ✓ |
| Structure | 28 top-level sections; no chunk markers; no orphaned references ✓ |

#### Findings raised and corrected in this issue

| ID | Severity | Finding | Action |
|---|:--:|---|---|
| **UA-01** | **Medium** | **The draft header projected 214 user stories; direct enumeration returned 255.** The projected figure had already been written into the title, the revision history, the scope table and the Part B preamble | **Fixed.** All five occurrences corrected to the counted figure before the document was completed |
| **UA-02** | **Medium** | **Appendix A's per-category story counts were estimated, not counted** — they summed to 249 against a stated total of 255, with individual categories out by up to 7 (Category A stated 51, actual 58) | **Fixed.** Every category recounted by enumeration; a note added explaining why story density is uneven and warning that **story count is not a proxy for effort** |
| **UA-03** | Low | The phrase "67 modules" appears in the RFP and BRD but not verbatim in the URD, which states "**67** across 11 categories" | **Accepted** — a phrasing difference, not an inconsistency. The figure is identical |

#### Findings raised for decision, not corrected here

| ID | Severity | Finding |
|---|:--:|---|
| **UA-04** | **High** | **The dispatch board is specified as drag-and-drop. Drag-only interaction fails WCAG 2.2 SC 2.5.7 and fails accessibility persona A-06 under WCAG 2.1 as well.** A keyboard and single-pointer alternative is required regardless of which version is contracted. Raised as **§26.3 U-09** and recommended in **§21.4** |
| **UA-05** | **High** | **WCAG 2.1 AA is contracted; WCAG 2.2 AA became the practical enterprise and procurement benchmark during 2026.** Five of the nine additional criteria are already met by requirements this URD carries independently. **Raised as a change request, not applied unilaterally** — the contracted standard in RFP v2.0 stands until the Steering Committee decides |
| **UA-06** | **High** | **R60 is a duplicate role identity for R32.** In a permission model this is a live security defect, not a documentation defect. Disclosed as **§26.3 U-01**; must be eliminated before any role is provisioned |
| **UA-07** | Medium | **Three sequencing decisions materially change the user experience and are unresolved** — Q-05a (notifications needed from W1, scheduled W4), Q-01 (assistant without a knowledge base), Q-05b (field safety reporting deliverable in W3, scheduled W6). Disclosed as **§26.3 U-04, U-05, U-06** |

#### Audit conclusion

**This URD is fit for UX design, configuration, training design and UAT planning**, subject to the
thirteen open items in §26.3. Its story set is complete and non-duplicated, its role and persona
coverage is total, and it is consistent with RFP v2.0 and BRD v2.0 on every headline figure.

**It is not yet fit to be used as a frozen acceptance baseline** — that requires: the role register
completed to R46 with R60 eliminated (U-01, U-02), the SoD register completed to 30 (U-03), the three
sequencing decisions made (U-04, U-05, U-06), the accessibility target confirmed (U-09), and the two
outstanding module specifications written (U-08).

*Audit performed 13 August 2026 · Business Analysis Team · Method: RG-06 direct enumeration*

---

### Appendix D — Reference Documents

| Document | Reference |
|---|---|
| **ERP Comprehensive RFP v2.0 — governing document** | `primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` |
| **ERP Comprehensive BRD v2.0 — companion** | `primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` |
| Module Catalogue Master Register — authoritative on modules | `02_Architecture/02-02_*` |
| Role, Permission & Access Matrix | `05_Cross_Cutting_Specifications/05-04_*` |
| Business Rules & Automation Catalogue | `05_Cross_Cutting_Specifications/05-05_*` |
| Non-Functional Requirements & Standards | `05_Cross_Cutting_Specifications/05-06_*` |
| Portal Suite Specification (P01–P12) | `04_Portals_and_Applications/04-00_*` |
| Implementation Roadmap & Phasing | `06_Delivery_and_Implementation/06-01_*` |
| KPI, Benefits & Acceptance Criteria | `06_Delivery_and_Implementation/06-02_*` |
| Documentation Audit Reports (1 and 2) | `00_Governance_and_Charter/00-06_*`, `00-07_*` |
| 65 module specifications | `03_Modules/**/M*.md` |
| ERP Comprehensive URD v1.0 *(superseded)* | `old-primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` |

### Appendix E — Glossary

| Term | Definition |
|---|---|
| **AC** | Acceptance criteria |
| **AMC / RAMC** | Annual / Residential Annual Maintenance Contract |
| **BABOK® v3** | IIBA Business Analysis Body of Knowledge, version 3 |
| **BDT** | Bangladeshi Taka (৳) |
| **BEFTN** | Bangladesh Electronic Funds Transfer Network |
| **BIN / TIN / NID** | Business Identification Number / Taxpayer Identification Number / National Identity Document |
| **BO-nn** | Business objective identifier |
| **BRU-nn** | Business rule identifier |
| **CAPA** | Corrective and Preventive Action |
| **CDO** | Chief Data Officer — statutory role under PDPA 2026 |
| **Conflict** | Two independent changes to the same record, requiring resolution on sync |
| **CSAT / NPS / CES** | Customer Satisfaction / Net Promoter / Customer Effort Score |
| **Data subject** | An individual whose personal data is processed — a user class with statutory rights |
| **DoD-nn** | Definition-of-done criterion |
| **EA-nn** | External access rule |
| **INVEST** | Independent, Negotiable, Valuable, Estimable, Small, Testable |
| **Mushak 6.3 / 9.1** | Bangladesh VAT tax invoice / monthly VAT return form |
| **NBR / NDMA** | National Board of Revenue / National Data Management Authority |
| **NFR-nnn** | Non-functional requirement identifier |
| **Offline-first** | The device holds the work; the platform reconciles on next sync |
| **P0–P3** | Priority: blocking / must-have / important / desirable |
| **PDPA 2026** | Personal Data Protection Act 2026 (Bangladesh, Law 63 of 2026) |
| **Persona** | A representative user profile guiding design decisions |
| **Pnn / P-nn** | Portal identifier (P01–P12) / persona identifier (P-01–P-36) |
| **POD** | Proof of Delivery |
| **PWA** | Progressive Web Application |
| **Rnn** | User role identifier (R01–R46) |
| **S0–S3** | Data sensitivity classification: public / internal / confidential / restricted |
| **SLA** | Service Level Agreement |
| **SOD-nn** | Segregation-of-duties control |
| **SUS** | System Usability Scale (0–100) |
| **T0–T5** | Data isolation tier |
| **TAT** | Turnaround Time |
| **UAT** | User Acceptance Testing |
| **US-xxx-nnn** | User story identifier |
| **WCAG 2.1 / 2.2 AA** | Web Content Accessibility Guidelines conformance level |
| **Wn** | Delivery wave (W1–W9) |

---

**END OF DOCUMENT**

---

*1000FiX Services Limited — User Requirements Document*
*Version 2.0 | 13 August 2026 | CONFIDENTIAL — Internal Use Only*
*URD Reference: 1000FIX-ERP-URD-2026-002*
*Derived from RFP 1000FIX-ERP-RFP-2026-002 · Companion to BRD 1000FIX-ERP-BRD-2026-002*

*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: +880 9644-300600 | Email: info@1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
