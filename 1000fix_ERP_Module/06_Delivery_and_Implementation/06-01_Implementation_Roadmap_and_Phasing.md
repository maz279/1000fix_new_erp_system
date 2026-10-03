---
id: FIX-ERP2-017
title: Implementation Roadmap & Phasing
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Implementation Roadmap & Phasing
# 9 Waves Over 36 Months

---

## 1. Sequencing Logic

Four constraints determine the order:

| Constraint | Consequence |
|---|---|
| **Technical dependency** | Identity, integration and master data must exist before anything transacts |
| **Business criticality** | The v1.0 commitments (service, dispatch, inventory, finance, contracts, warranty) come first and land on their original dates |
| **Data accumulation** | Machine learning cannot be built before there is data to learn from — hence AI in Waves 6–8, not Wave 2 |
| **Business absorption capacity** | 51+ branches and 500+ staff can absorb roughly one major process change per quarter; UAT super-user availability, not developer capacity, is the binding constraint |

### The v1.0 Commitment Is Protected

| v1.0 Phase | v1.0 Go-Live | v2.0 Wave | v2.0 Go-Live | Status |
|---|---|---|---|---|
| Phase 1 — Foundation | Month 4 | W1 | Month 4 | Unchanged |
| Phase 2 — Field Operations | Month 7 | W2 | Month 8 | +1 month (broader inventory scope) |
| Phase 3 — Financial Control | Month 10 | W3 | Month 13 | +3 months (logistics and pricing added ahead of it) |
| Phase 4 — Contracts & Partners | Month 13 | W4 | Month 18 | +5 months (contact centre and billing engine added) |
| Phase 5 — Workforce & Intelligence | Month 16 | W5 | Month 22 | +6 months |
| Phase 6 — Optimisation | Month 18 | W5–W8 | Month 34 | Absorbed into new-business waves |

The additions in Waves 1–4 (logistics, front desk, pricing, billing engine, contact centre)
are the foundations the new business lines require. Building them later would mean rebuilding
finance and service twice.

---

## 2. Wave Plan

```
Year 1                          Year 2                          Year 3
M1────M4────M8────M13───M18     M19──M22───M26───M30            M31──M34──M36
│ W1  │ W2  │ W3  │ W4  │       │ W5 │ W6  │ W7  │              │ W8  │ W9 │
│Found│Field│Money│Agree│       │Peo-│New  │Market              │Intel│Exp-│
│ation│ Ops │ &   │ments│       │ple &│Asset│place              │ligen│and │
│  &  │  &  │Move-│ &   │       │MSP │Busi-│  &  │              │ ce &│sion│
│Servi│Inven│ment │Cont-│       │    │ness │Sett-│              │ ESG │    │
│ ce  │tory │     │act  │       │    │lines│lement              │     │    │
└─────┴─────┴─────┴─────┘       └────┴─────┴─────┘              └─────┴────┘
```

---

## 3. Wave Detail

### Wave 1 — Foundation & Service Core (Months 1–4)

| | |
|---|---|
| **Modules** | M29 SEC · M28 IPF · M30 ADM (core config) · M07 CRM · M17 AST (registry) · M01 SRM (core) · M04 FRD |
| **Portals** | P03 Admin Operations |
| **Team** | 6 (2 Odoo, 1 DevOps, 1 BA, 1 QA, 1 PM/CTO) |
| **Requirements** | 142 |
| **Geography** | Dhaka HQ + 5 pilot service centres |

**Delivers**

- Identity provider, single sign-on, role framework, audit trail
- API gateway, event platform, workflow engine, integration framework
- Entity, branch, zone and calendar configuration; Bengali localisation base
- Customer master with the full classification model and Bangladesh address hierarchy
- Device and asset registry with brand and model masters
- Service order and work order core with lifecycle, SLA, diagnosis, estimate and QC
- Front desk: token queue, intake, handover, cash drawer, shift control
- SMS, WhatsApp and email notification delivery

**Data migration:** customers, devices, branch and employee master

**Gate criteria**

- Service orders created from all channels at pilot sites, end to end
- Walk-in intake in under 3 minutes, demonstrated by branch staff
- Customer and device data migrated with reconciliation signed off
- SLA clocks and escalation firing correctly
- 100% Bengali translation on all delivered screens
- Zero critical or high security findings

---

### Wave 2 — Field Operations & Inventory (Months 5–8)

| | |
|---|---|
| **Modules** | M02 FSM · M15 INV · M10 LOY · M01 SRM (complete) · M17 AST (complete) |
| **Portals** | P01 Customer Portal · P02 Technician App |
| **Team** | 9 (+2 Flutter, +1 Odoo) |
| **Requirements** | 178 |
| **Geography** | All Dhaka centres |

**Delivers**

- Dispatch engine, dispatch board, zones, route optimisation
- GPS tracking, live operations map, customer tracking page
- Technician mobile app with full offline capability
- Multi-location inventory, van stock, barcode operations, replenishment alerts
- Privilege programme, points, vouchers, campaigns
- Customer portal: booking, tracking, history, approvals
- Workshop bench management and repair-level routing

**Data migration:** inventory across pilot locations, service history archive

**Gate criteria**

- Technician app in daily use by all Dhaka technicians
- 24-hour offline operation demonstrated with zero data loss
- Route optimisation reducing measured travel time by ≥ 15%
- Inventory accuracy ≥ 95% at migrated locations
- Online booking rate ≥ 60% at pilot sites
- Paper service forms withdrawn in Dhaka

---

### Wave 3 — Money, Movement & Documents (Months 9–13)

| | |
|---|---|
| **Modules** | M19 FIN · M11 SLS · M03 LOG · M16 SCM · M24 DMS |
| **Portals** | P05 Vendor Portal · P09 Logistics & Rider App |
| **Team** | 11 (+1 Odoo finance specialist, +1 QA) |
| **Requirements** | 156 |
| **Geography** | All Dhaka + Chittagong |

**Delivers**

- General ledger, AR, AP, banking, cash control, fixed assets
- Mushak VAT invoicing, TDS, VAT sub-ledgers, return preparation
- Payment gateway integration (bKash, Nagad, SSLCOMMERZ) with auto-reconciliation
- Price books, rate cards, quotation engine, discount governance
- Logistics: consignments, chain of custody, pick & drop, courier integration, rider app
- Procurement: requisition, PO, receipt, three-way match, vendor portal
- Document management, templates, e-signature, retention

**Data migration:** three years of financial history, vendor master, open POs

**Gate criteria**

- 100% of invoices generated automatically from closed jobs
- Payment auto-matching ≥ 90%
- Mushak invoices accepted without NBR exception
- Month-end close completed within 5 days for the first full month
- Pick & drop operating with unbroken chain of custody
- Three-way matching blocking unmatched vendor invoices

---

### Wave 4 — Agreements, Billing & Contact (Months 14–18)

| | |
|---|---|
| **Modules** | M08 CTR · M09 WTY · M20 BIL (core) · M27 CCE · M25 BID (core) |
| **Portals** | P04 Corporate B2B · P06 Analytics · P08 Brand Partner · P10 Contact Centre |
| **Team** | 12 (+1 frontend) |
| **Requirements** | 189 |
| **Geography** | All active service centres |

**Delivers**

- Contract engine covering all product families, entitlements, SLAs, renewals
- Warranty entitlement, warranty products, brand claim automation for 17+ partners
- Billing engine: subscriptions, consolidated B2B invoicing, dunning, refunds
- Omnichannel contact centre with hotline integration and the AI assistant
- Executive, branch, technician, finance and warranty dashboards
- Corporate B2B portal with asset estates and consolidated invoicing
- Brand partner portal for claim submission and reconciliation

**Data migration:** active contracts, open warranty claims

**Gate criteria**

- Warranty claims auto-created within 24 hours and submitted within 72
- Claim approval rate ≥ 90% on first submission
- 10+ corporate clients transacting on the B2B portal
- Hotline conversations captured in the system of record
- AI assistant resolving ≥ 40% of first contacts
- **v1.0 scope complete at this gate**

---

### Wave 5 — People, Quality & Managed Services (Months 19–22)

| | |
|---|---|
| **Modules** | M21 HRM · M22 LMS · M23 QMS · M05 RMS |
| **Portals** | P11 Field Auditor App |
| **Team** | 12 |
| **Requirements** | 148 |
| **Geography** | All 51+ service centres |

**Delivers**

- HR, attendance, leave, roster, payroll with Bangladesh tax and BEFTN
- Technician performance capture and incentive calculation
- Competency framework, certification tracking with hard dispatch enforcement
- Learning management with Bengali content
- Quality management: NCR, CAPA, complaints, audits, ISO evidence
- Managed services: remote support, monitoring, alerting, MSP ticketing, SLA reporting
- Field auditor app

**Data migration:** employee records, certifications, open quality records

**Gate criteria**

- First payroll run processed and validated end to end
- Zero uncertified technicians assignable to brand warranty work
- ISO 9001 internal audit executed entirely in the system
- First MSP clients onboarded with monitored estates live
- All 51+ centres operating on the platform

---

### Wave 6 — New Asset Businesses (Months 23–26)

| | |
|---|---|
| **Modules** | M13 RNT · M14 TRF · M06 DTS · M26 AIM (dispatch and forecasting models) |
| **Portals** | P01 native mobile applications |
| **Team** | 14 (+1 AI/ML, +1 data engineer) |
| **Requirements** | 134 |

**Delivers**

- Rental: asset pool, reservations, agreements, tariffs, deposits, condition reports, damages
- Trade-in, refurbishment, grading, resale, provenance
- Data services: recovery cases, custody controls, backup subscriptions, certified destruction
- ML services: dispatch assignment scoring, duration prediction, demand forecasting
- Customer native mobile applications

**Gate criteria**

- Rental transacting with full condition and deposit control
- Zero refurbished units released without a destruction certificate
- Data-services chain of custody with zero exceptions
- Automatic dispatch assignment ≥ 50% with ≥ 88% dispatcher agreement
- Parts forecast accuracy within target

---

### Wave 7 — Marketplace & Settlement (Months 27–30)

| | |
|---|---|
| **Modules** | M12 ECM · M20 BIL (marketplace settlement) · M11 SLS (dynamic pricing) |
| **Portals** | P07 Marketplace Seller · P12 Partner & Referral |
| **Team** | 14 |
| **Requirements** | 121 |

**Delivers**

- E-commerce storefront for parts, accessories and refurbished devices
- Marketplace: seller onboarding with KYC, listings, job broadcast, bidding, ratings, disputes
- Commission calculation, seller wallets, payout runs, escrow
- Paid boost and advertising placement
- Dynamic pricing with guard rails
- Partner and referral portal with commission statements

**Gate criteria**

- 200+ approved sellers transacting
- Payout accuracy 100% with zero unexplained variance
- Marketplace jobs meeting the same quality standards as owned jobs
- Dispute rate below target with all disputes resolved within SLA
- VAT treatment validated by external tax advice

---

### Wave 8 — Intelligence & Sustainability (Months 31–34)

| | |
|---|---|
| **Modules** | M25 BID (warehouse) · M26 AIM (predictive, pricing, quality models) · M17 AST (IoT) · M18 ESG |
| **Team** | 12 |
| **Requirements** | 79 |

**Delivers**

- Analytical warehouse, semantic layer, governed self-service
- Telemetry ingestion and asset health scoring
- Predictive maintenance, churn, quality-risk and pricing models
- Bengali conversational and document AI at full scope
- E-waste collection, recycling, disposal certification, ESG reporting

**Gate criteria**

- All management reporting served from the warehouse; no manual packs remain
- Predictive maintenance precision ≥ 70% on the pilot estate
- Overall automation of routine operational work ≥ 85%
- E-waste chain fully certified with zero uncertified disposals

---

### Wave 9 — Expansion Readiness (Months 35–36)

| | |
|---|---|
| **Modules** | M30 ADM (multi-entity, country packs) |
| **Team** | 9 |
| **Requirements** | 33 |

**Delivers**

- Multi-entity accounting and consolidation
- Country pack framework with Bangladesh as the reference implementation
- Entity onboarding runbook
- Multi-currency and FX at full scope
- International payment and shipping integration
- Performance and scale hardening

**Gate criteria**

- A test entity in a second country stood up in under 12 weeks using only configuration
- Consolidated reporting across entities validated
- Full-scale load test passed at 1.5× projected peak

---

## 4. Team Model

### Composition by Wave

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

*Figures are full-time equivalents. Peak of 19 in Waves 6–7 reflects concurrent delivery of
three new business lines plus the marketplace.*

### Business-Side Commitment

| Role | Commitment | Waves |
|---|---|---|
| Executive Sponsor (CEO) | 4 hours/month steering | All |
| Module Business Owners | 20% of time | Waves affecting their module |
| Super-Users (2–3 per module) | 30% during UAT, 10% otherwise | Waves affecting their module |
| Branch Champions (1 per branch) | 4 hours/week during rollout | W1–W5 |
| Data Owners | 20% during migration | W1–W5 |

**This is the binding constraint on the programme.** If business availability is not
protected, waves will slip regardless of development capacity.

---

## 5. Delivery Method

| Aspect | Approach |
|---|---|
| Cadence | Two-week sprints; five to ten sprints per wave |
| Ceremonies | Sprint planning, daily stand-up, sprint review with business owners, retrospective |
| Definition of ready | Requirement has acceptance criteria, a business owner and no unresolved dependency |
| Definition of done | See Doc 04 §7 — all 15 criteria |
| Demo discipline | Every sprint review demonstrates working software to the business owner, never slides |
| Wave gate | Formal Go/No-Go with the Steering Committee against published criteria |
| Hypercare | Four weeks of elevated support after every wave go-live |
| Release cadence | Fortnightly to staging; monthly to production within a wave; hotfixes as needed |

---

## 6. Rollout Approach

### Geographic Sequence

| Stage | Locations | Waves |
|---|---|---|
| Pilot | Dhaka HQ + 5 selected centres | W1 |
| Dhaka | All Dhaka centres (~20) | W2 |
| Major cities | + Chittagong, Sylhet, Khulna, Rajshahi | W3 |
| National | All 51+ centres | W4–W5 |
| New capability | All centres receive each new business line as it goes live | W6–W8 |

### Rollout Pattern Per Location

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

### Parallel Running

| Process | Parallel Period | Reason |
|---|---|---|
| Service orders | 2 weeks | Operational safety |
| Inventory | 2 weeks + full count at cutover | Valuation accuracy |
| Finance | 1 full month-end | Reconciliation confidence |
| Payroll | 2 pay cycles | Zero tolerance for pay errors |
| Warranty claims | 1 month | Brand relationship protection |

---

## 7. Change Management

| Activity | Detail |
|---|---|
| Stakeholder map | Maintained and reviewed each wave; resistance actively tracked |
| Communication | Monthly all-staff update; wave-specific briefings; visible executive sponsorship |
| Champion network | One trained champion per branch; monthly champion forum |
| Training | Role-based, in Bengali, delivered before access is granted; refreshers each wave |
| Materials | Quick-reference cards, video walkthroughs, in-app guidance, searchable help |
| Support | Floor-walkers during go-live; dedicated internal support channel; escalation path |
| Adoption measurement | Weekly usage reporting by role and branch; intervention where adoption lags |
| Recognition | Early adopters and champions recognised publicly |
| Feedback loop | Every wave retrospective includes end-user feedback with visible actions |

### Adoption Risk by Group

| Group | Risk | Mitigation |
|---|---|---|
| Field technicians | **Critical** — app rejection collapses the field model | Bengali-first, extremely simple UX, field pilot with respected senior technicians, device provision, incentive visibility as an immediate personal benefit |
| Branch counter staff | High — highest transaction volume | Speed as the design goal; measured intake time; champion-led training |
| Finance staff | Medium — process change and control tightening | Early involvement in design; parallel running; audit-trail benefit emphasised |
| Branch managers | Medium — visibility cuts both ways | Position dashboards as their tool, not surveillance; involve in KPI design |
| Marketplace sellers | High — external, low switching cost | Simple onboarding, fast payouts, transparent scoring |
| Corporate clients | Medium | Account-manager-led onboarding; demonstrable time savings |

---

## 8. Milestone Schedule

| Milestone | Month | Gate |
|---|---|---|
| Programme kickoff | 0 | Charter approved, team mobilised |
| Foundation go-live | 4 | W1 gate |
| Field operations go-live | 8 | W2 gate |
| Financial control go-live | 13 | W3 gate |
| **v1.0 scope complete** | **18** | **W4 gate** |
| Workforce & MSP go-live | 22 | W5 gate |
| New asset businesses go-live | 26 | W6 gate |
| Marketplace go-live | 30 | W7 gate |
| Full intelligence go-live | 34 | W8 gate |
| Expansion readiness | 36 | W9 gate — programme closure |
| Benefits realisation review | 42 | Post-implementation review |

---

## 9. Contingency

| Scenario | Response |
|---|---|
| Wave slips by ≤ 4 weeks | Absorb in the next wave's buffer; no dependency change |
| Wave slips by > 4 weeks | Steering Committee decides: descope P2/P3, extend, or reallocate |
| Business UAT capacity unavailable | Wave gate slips; development does not run ahead into unaccepted work |
| Key integration blocked externally | Deliver the module with the documented manual fallback; integrate later |
| Adoption failure at a location | Pause rollout, diagnose, remediate, re-pilot before continuing |
| Budget pressure | Defer W8 and W9 first; W6 and W7 are the revenue-generating waves |
| Team attrition | Two-person minimum knowledge coverage on every module; documentation as a definition-of-done item |

### What Cannot Be Descoped

| Item | Reason |
|---|---|
| M29 Identity & Security | Everything depends on it |
| M28 Integration platform | Everything depends on it |
| M01 Service & M02 Field | The business itself |
| M19 Finance & Bangladesh compliance | Legal obligation |
| M09 Warranty claims | The largest single revenue-recovery benefit |
| Bengali localisation | Field adoption fails without it |
| Offline capability | Field operation fails without it |
| Audit trail and data protection | Legal and ISO obligation |

---

*Next document: `18_KPI_Benefits_and_Acceptance_Criteria.md`*
