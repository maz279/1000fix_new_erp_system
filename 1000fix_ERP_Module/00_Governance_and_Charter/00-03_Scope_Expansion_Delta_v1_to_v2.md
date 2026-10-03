---
id: FIX-ERP2-002
title: Scope Expansion Delta — v1.0 to v2.0
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Scope Expansion Delta — v1.0 → v2.0
# With Full Evidence Trail

---

## 1. Purpose

This document is the audit trail for the scope expansion. For every addition it answers
three questions:

1. **What is being added?**
2. **Where in the Company's own documentation is the commitment that requires it?**
3. **What breaks if we do not build it?**

Nothing in v2.0 is speculative. Every new module traces to an existing, documented
business commitment held somewhere in this workspace.

---

## 2. Module-Level Delta

### 2.1 Modules Carried Forward and Expanded (11)

| v1.0 Module | v2.0 Module(s) | Nature of Expansion |
|---|---|---|
| Service & Repair Management | **M01 SRM** + **M04 Front Desk** | Split. Bench-repair workshop routing, Level 1/2/3 board-level repair tracking, RMA workflow, multi-device job batching, refurbishment intake path added. Front desk, token queue, counter cash and branch shift operations promoted to a module of its own. |
| Field Service Management | **M02 FSM** + **M03 Logistics** | Split. Dispatch, GPS, mobile execution and route optimisation stay in M02. Pick & drop, courier partner integration, chain-of-custody, reverse logistics, inter-branch movement and last-mile delivery become M03. |
| Inventory & Spare Parts | **M15 INV** | Serialised parts genealogy, warranty-parts segregation, consignment stock from brand partners, marketplace seller stock visibility, rental asset pool separation, refurbished-parts grading. |
| CRM | **M07 CRM** | Household and corporate hierarchy, multi-tier corporate user approval chain (user → line manager → 1000FiX admin), per-customer price lists, consent & preference management, customer credit limits, saved GPS locations with tags. |
| Financial Management | **M19 FIN** + **M20 BIL** | Split. Ledger, VAT/Mushak, TDS, banking and statutory reporting stay in M19. Subscription billing, usage/metered billing, revenue recognition, partner commission settlement, marketplace payouts, escrow and refunds become M20. |
| HR & Payroll | **M21 HRM** + **M22 LMS** | Split. Employment, attendance, payroll and incentives stay in M21. Course catalogue, brand certification tracks, competency matrices, assessment and re-certification become M22. |
| Contract & Warranty Management | **M08 CTR** + **M09 WTY** | Split. AMC/RAMC, managed-service contracts, SLA definitions, entitlement consumption and renewals become M08. Brand warranty claims, extended-warranty products, accidental damage protection and claim reconciliation become M09. |
| Procurement & Supply Chain | **M16 SCM** | Vendor scorecards, RFQ/tendering, contract purchasing, import/LC tracking, marketplace seller onboarding as a supplier class, drop-ship. |
| Business Intelligence & Reporting | **M25 BID** | Data warehouse (ClickHouse), semantic layer, self-service exploration, embedded analytics per portal, scheduled distribution, data quality monitoring. |
| Document Management | **M24 DMS** | Bengali OCR, records retention schedules, legal hold, qualified e-signature, template engine, evidence packs for warranty and ISO audits. |
| Quality Management | **M23 QMS** | ISO 27001 controls alongside ISO 9001, supplier quality, marketplace seller quality gates, customer complaint taxonomy, CAPA effectiveness verification, internal audit programme. |

### 2.2 Modules Newly Created (19)

| New Module | Evidence Source | What Breaks Without It |
|---|---|---|
| **M03 Logistics & Reverse Logistics** | Business Plan §Pick & Drop; SOW §"Logistics team Interface — real-time dashboard of pending orders, schedule/re-schedule, service-center-wise or central logistics team assignment"; Company Profile §Pick & Drop Service | Pick & drop remains phone-coordinated; devices lost in transit have no chain of custody; no proof-of-collection or proof-of-delivery evidence for disputes |
| **M05 Remote Support & Managed Services** | Business Plan §Managed Service Contracts (6 contract types incl. security-focused, cloud, DR/BC, IT strategy) and §24/7 Technical Support (remote/software/hardware/networking/mobile/email support); SOW §"Remote service feature… like the TeamViewer app" | MSP contracts sold with no monitoring, ticketing, patch or asset baseline; SLA credits unquantifiable; the highest-margin B2B line cannot scale |
| **M06 Data Services** | Business Plan §Data Recovery Services (hard drive, SSD, RAID, USB, memory card, mobile, email/database) and §Data Backup Solutions (cloud, on-site, hybrid, CDP, archiving); §Refurbishment "Data Wiping and Privacy Protection"; §Recycling "Data Destruction" | Data recovery jobs tracked on paper with no chain-of-custody or privacy controls — a direct ISO 27001 and Digital Security Act exposure; backup subscriptions unbillable |
| **M11 Sales, Quotation & Dynamic Pricing** | SOW §Quotation and Acceptance (engineer quotes, customer bids, re-bid, order customisation after placement); SOW §"admin shall be able to define different pricing models for each customer"; Portal roadmap IMPL-63 Dynamic Pricing Engine | Pricing stays in static rate cards; no competitive quoting; no customer-specific or segment pricing; margin leakage on complex repairs |
| **M12 E-Commerce, Parts Retail & Marketplace** | SOW §E-Commerce Platform, §E-Commerce Aggregator Model, §"External engineer/service center can register as freelancer/shop", §Paid boost/top listing, §In-app ad section; Portal roadmap IMPL-58 Third-Party Technician Marketplace, IMPL-38 Service Partner Network & Commission Engine | The entire aggregator business model is unbuildable; growth remains capped by owned technician headcount |
| **M13 Rental & Asset-as-a-Service** | Business Plan §Rental Services (laptop, camera, projector, tablet, AV, server, networking, electronic test equipment); Company Profile §Laptop Rental Service; SOW §"rental service" as a service type | Rental assets untracked; no utilisation, damage, deposit or depreciation control; asset write-offs |
| **M14 Trade-In, Refurbishment & Resale** | Business Plan §Refurbishment and Resale (refurbishment, data wiping, QA testing, resale & distribution, warranty on refurbished); Company Profile §Exchange Offer; SOW §"Sell/exchange options… customer sells old device by inputting images, condition, warranty status… backend team analyses and offers a price" | No device provenance or grading; refurbished units resold without controlled warranty exposure; trade-in quotations manual and inconsistent |
| **M17 Asset, Device Registry & IoT** *(elevated from a sub-feature)* | SOW §"Corporate customer's asset listing… register all 100 devices with serial nos."; SOW §IoT Integration (phase 2); Portal roadmap IMPL-40 Predictive Maintenance Agent | Corporate asset estates unmanaged; predictive maintenance impossible; AMC entitlement cannot be tied to specific assets |
| **M18 E-Waste, Recycling & Sustainability** | Business Plan §Device Recycling and Responsible Disposal (recycling, data destruction, secure disposal, regulatory compliance, components recovery, awareness) | No compliance evidence for e-waste handling; no material-recovery revenue tracking; ESG reporting impossible |
| **M20 Billing, Revenue Recognition & Settlement** | SOW §commission, §payment status, §"invoice refund or replacement option"; Business Plan §subscription contracts; Portal roadmap IMPL-38 Commission Engine, IMPL-39 Referral Partner Program | Subscription and usage revenue mis-stated; marketplace sellers cannot be paid; commissions and referral payouts manual |
| **M22 Learning, Certification & Competency** | BRD BR-HRM-012 (training programmes) expanded; BRU-HRM-01 (cannot assign uncertified technician); Business Plan §"trained technicians", brand authorisation requirements across 17 partners | Brand certification lapses go undetected until a claim is rejected; dispatch cannot enforce competency; onboarding of marketplace engineers has no quality gate |
| **M26 AI/ML Services** | Portal roadmap IMPL-34 ML Service Architecture, IMPL-40 Predictive Maintenance, IMPL-41 Demand Forecasting & Capacity Planning, IMPL-42 Quality Monitoring Agent, IMPL-44 Enhanced Dispatch (70% auto-assign); SOW §AI-Powered Predictive Maintenance | Automation ceiling stays at ~70%; no demand forecasting for parts or capacity; dispatch remains rule-based |
| **M27 Conversational AI & Omnichannel Contact Centre** | Business Plan §24/7 Technical Support (phone, email, live chat, remote assistance, knowledge base, escalation procedures, quality monitoring); SOW §In-app chat, §Chatbot configuration, §Direct calling to call centre, §chat transcript emailed, §chat rating; Portal roadmap IMPL-23 & IMPL-43 chatbot | The hotline (16743) stays outside the system of record; no unified customer conversation history; 24/7 support commitment unmeasurable |
| **M30 Platform Administration, Multi-Entity & Multi-Country** | Portal roadmap IMPL-57 Multi-Country Expansion Framework, IMPL-51 Multi-Region Database; BRD BO-09 growth ambition; Business Plan international shipping references; SOW §"local & international customer and service provider" | Expansion beyond Bangladesh requires a rebuild; no tenant, entity, currency or locale isolation |
| **M04 Front Desk, Queue & Branch Operations** *(promoted)* | BRD FSM-030 walk-in queue; CD-17 walk-in queue module; URD Persona 1 Service Center Agent | Branch counter operations, token queue, cash drawer and shift handover stay informal across 51+ centres |
| **M08 Contract Lifecycle Management** *(split out)* | Business Plan §AMC (Residential, Commercial, IT Infrastructure, Healthcare Equipment, Specialty Equipment) and §Managed Service Contracts (6 types) and §Mobile/Home Appliance Service Contracts (5 types) | The Company markets 14+ distinct contract products; a single AMC object cannot model them |
| **M09 Warranty & Claims** *(split out)* | BRD §8.7; Business Plan §Warranty Extension Services (7 product types incl. Accidental Damage Protection, Mobile Device Protection, Home Appliance Protection, Computer & Laptop Care, Customised Coverage); Portal roadmap IMPL-37 Warranty Claim Processing | Warranty extension is a product family, not a flag; claim automation for 17+ brands needs its own domain |
| **M19 / M20 split** | See above | Statutory ledger and commercial billing have different change cadences and different owners |
| **M21 / M22 split** | See above | Competency management is a service-delivery control, not an HR administrative function |

---

## 3. Portal Delta

| # | Portal | v1.0 | v2.0 | Change |
|---|---|:--:|:--:|---|
| P01 | Customer Self-Service Portal & App | ✓ | ✓ | Extended: rental, trade-in, marketplace ordering, recycling drop-off booking, data-service requests, inbox, theme personalisation, credit points |
| P02 | Technician Mobile Application | ✓ | ✓ | Extended: bench workshop mode, logistics handover, remote-session launch, refurb grading, earnings & incentive view |
| P03 | Admin Operations Portal | ✓ | ✓ | Extended: multi-business-line consoles |
| P04 | Corporate B2B Portal | ✓ | ✓ | Extended: asset estate management, MSP dashboards, multi-level approval chains, SLA credits |
| P05 | Vendor & Supplier Portal | ✓ | ✓ | Extended: RFQ response, ASN, consignment |
| P06 | Analytics & Executive Dashboard | ✓ | ✓ | Extended: warehouse-backed, self-service |
| **P07** | **Marketplace Seller Portal** | — | ★ | New — external engineers and shops: listings, bids, jobs, ratings, wallet, payouts, boost purchase |
| **P08** | **Brand Partner Portal** | (merged in P05) | ★ | Separated — warranty claim submission, approvals, consignment parts, performance scorecards |
| **P09** | **Logistics & Courier Portal / App** | — | ★ | New — rider app, courier partner API console, chain-of-custody scanning |
| **P10** | **Contact Centre Agent Console** | — | ★ | New — omnichannel queue, screen-pop, knowledge base, remote-session control |
| **P11** | **Field Auditor & Quality App** | — | ★ | New — offline branch audits, ISO evidence capture, mystery-shopper checklists |
| **P12** | **Partner / Referral Portal** | — | ★ | New — alliance partners, referral tracking, commission statements |

---

## 4. Requirement Volume Delta

| Domain | v1.0 Reqs | v2.0 Reqs | Delta |
|---|---:|---:|---:|
| Service & Repair (SRM) | 37 | 88 | +51 |
| Field Service & Dispatch (FSM) | 31 | 74 | +43 |
| Logistics (LOG) | 0 | 42 | +42 |
| Front Desk (FRD) | 3 | 31 | +28 |
| Remote & Managed Services (RMS) | 0 | 61 | +61 |
| Data Services (DTS) | 0 | 34 | +34 |
| CRM | 18 | 55 | +37 |
| Contracts (CTR) | 12 | 52 | +40 |
| Warranty (WTY) | 10 | 48 | +38 |
| Loyalty & Campaigns (LOY) | 5 | 41 | +36 |
| Sales & Pricing (SLS) | 0 | 46 | +46 |
| E-Commerce & Marketplace (ECM) | 0 | 79 | +79 |
| Rental (RNT) | 0 | 44 | +44 |
| Trade-In & Refurbishment (TRF) | 0 | 39 | +39 |
| Inventory (INV) | 24 | 63 | +39 |
| Procurement (SCM) | 12 | 40 | +28 |
| Asset & IoT (AST) | 4 | 42 | +38 |
| E-Waste & ESG | 0 | 26 | +26 |
| Finance (FIN) | 35 | 68 | +33 |
| Billing & Settlement (BIL) | 0 | 51 | +51 |
| HR & Payroll (HRM) | 23 | 52 | +29 |
| Learning & Certification (LMS) | 1 | 30 | +29 |
| Quality (QMS) | 8 | 37 | +29 |
| Documents (DMS) | 8 | 30 | +22 |
| BI & Data Platform (BID) | 14 | 45 | +31 |
| AI/ML (AIM) | 2 | 38 | +36 |
| Contact Centre (CCE) | 0 | 47 | +47 |
| Integration Platform (IPF) | 31 | 58 | +27 |
| Security & Identity (SEC) | 22 | 44 | +22 |
| Platform Admin & Multi-Country (ADM) | 5 | 35 | +30 |
| Portals (all) | 74 | 140 | +66 |
| **Total** | **~405** | **1,180** | **+775** |

---

## 5. Data Model Delta

| Area | v1.0 Entities | v2.0 Entities | Notable Additions |
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

---

## 6. Integration Delta

| Category | v1.0 | v2.0 | New Integrations |
|---|---:|---:|---|
| Payments | 4 | 9 | International gateway (Stripe/PayPal) for cross-border, escrow provider, payout rails, instalment partner, card-on-file tokenisation |
| Communications | 4 | 9 | Cloud telephony / IVR, video call (WebRTC), email inbound parsing, push (multi-app), social messaging (Messenger/IMO) |
| Logistics | 0 | 5 | Courier partners (Pathao / RedX / Steadfast / Sundarban), international freight, address geocoding |
| Remote & monitoring | 0 | 6 | RMM agent, remote desktop (RustDesk/MeshCentral), SNMP/agent telemetry, patch feed, antivirus console, cloud provider APIs |
| Marketplace | 0 | 4 | NID/trade-licence verification, seller KYC, rating fraud detection, ad server |
| Mapping & routing | 2 | 4 | Traffic API, geofence service |
| Government & compliance | 1 | 5 | NBR e-VAT, TIN/BIN validation, e-waste authority reporting, BEFTN, RJSC |
| AI & data | 1 | 6 | LLM inference, vector store, ML model registry, OCR service, speech-to-text (Bengali) |
| Enterprise | 3 | 9 | Corporate SSO (SAML/OIDC per client), client ITSM (ServiceNow/Jira), accounting export, HRIS import |
| **Total** | **15** | **47** | **+32** |

---

## 7. Timeline Delta

| | v1.0 | v2.0 |
|---|---|---|
| Structure | 6 phases | 9 waves |
| Duration | 18 months | 36 months |
| First go-live | Month 4 | Month 4 (unchanged) |
| v1.0-equivalent scope complete | Month 18 | **Month 18 (unchanged)** |
| New business lines live | — | Months 19–33 |
| Multi-country ready | — | Month 36 |

**The expansion does not delay the original commitments.** Waves 1–4 (Months 1–18) deliver
the v1.0 module set plus the additions that are inexpensive because they sit on the same
foundations (M03 Logistics, M04 Front Desk, M11 Pricing, M20 Billing, M24 DMS, M27 Contact
Centre). Waves 5–9 (Months 19–36) deliver the new business lines.

---

## 8. Team Delta

| Role | v1.0 | v2.0 Peak | Notes |
|---|---:|---:|---|
| Senior Odoo Developer (Python) | 2 | 4 | Two squads: Service/Ops and Commercial/Finance |
| Flutter / Mobile Developer | 2 | 3 | Technician app, logistics rider app, field audit app |
| Frontend Developer (Next.js) | 0 | 2 | Marketplace, partner and contact-centre surfaces |
| DevOps / Platform Engineer | 1 | 2 | Kubernetes, observability, multi-environment |
| Data / BI Engineer | 0 | 1 | Warehouse, semantic layer, pipelines |
| AI/ML Engineer | 0 | 1 | Dispatch, forecasting, predictive maintenance, LLM |
| Business Analyst | 1 | 2 | One per pillar cluster |
| QA Engineer | (shared) | 2 | Automation + UAT coordination |
| Change / Training Lead | 0 | 1 | 38 roles, 51+ branches, external sellers |
| Programme Manager | (CTO) | 1 | Dedicated from Wave 3 |
| **Total (peak)** | **6** | **14** | Ramps 6 → 9 → 14 → 9 across waves |

---

## 9. What Was Considered and Rejected

| Option | Why Rejected |
|---|---|
| Keep v1.0 and build new lines as separate systems later | Recreates fragmentation; duplicate customer, device, finance and identity masters; the exact problem the ERP was approved to solve |
| Buy a specialist MSP/PSA tool (e.g. commercial RMM + PSA suite) | Per-technician licensing scales badly at 400 technicians; still needs ERP integration; L6 components used only for the RMM *agent*, not the PSA layer |
| Buy a marketplace SaaS platform | Commission model and settlement must sit in the ledger; SaaS marketplaces cannot be made the system of record without duplicating finance |
| Extend the Next.js portal platform to hold business logic | Violates the one-system-of-record principle; portal already carries experience responsibility; would split business rules across two codebases |
| Move to Odoo Enterprise for FSM/Helpdesk/Quality | ~$45–90K over three years in licence for capability the OCA modules already provide; also constrains customisation |
| Compress to 24 months by parallelising all waves | Team scaling beyond 14 raises coordination cost faster than throughput; UAT capacity of the business (super-users) is the binding constraint, not developer capacity |

---

## 10. Traceability Summary

Every v1.0 requirement is preserved. The mapping is:

| v1.0 Requirement Range | v2.0 Location |
|---|---|
| BR-SRM-001 … BR-SRM-020 | FR-SRM-001 … FR-SRM-020 (identical), then FR-SRM-021+ new |
| BR-FSM-001 … BR-FSM-017 | FR-FSM-001 … FR-FSM-017, plus FR-LOG-* where pick & drop moved |
| BR-INV-001 … BR-INV-015 | FR-INV-001 … FR-INV-015 |
| BR-CRM-001 … BR-CRM-010 | FR-CRM-001 … FR-CRM-010 |
| BR-FIN-001 … BR-FIN-015 | FR-FIN-001 … FR-FIN-015, plus FR-BIL-* where billing moved |
| BR-HRM-001 … BR-HRM-012 | FR-HRM-001 … FR-HRM-012, plus FR-LMS-* where training moved |
| BR-CWM-001 … BR-CWM-012 | FR-CTR-* (contracts) and FR-WTY-* (warranty) |
| BR-SCM-001 … BR-SCM-007 | FR-SCM-001 … FR-SCM-007 |
| BR-BI-001 … BR-BI-010 | FR-BID-001 … FR-BID-010 |
| BR-DMS-001 … BR-DMS-005 | FR-DMS-001 … FR-DMS-005 |
| BR-QMS-001 … BR-QMS-005 | FR-QMS-001 … FR-QMS-005 |
| NFR-001 … NFR-030 | NFR-001 … NFR-030 (retained), NFR-031+ new |
| BRU-* (all business rules) | BRU-* retained verbatim, renumbered only where a module split |
| CD-01 … CD-20 | CD-001 … CD-020 retained; CD-021 … CD-058 new |

No v1.0 requirement is deleted. Four are **superseded** by a stronger v2.0 requirement:

| Superseded | Superseded By | Reason |
|---|---|---|
| INT-022 (Rasa 3.6 Bengali chatbot) | FR-CCE-011 (LLM-based Bengali assistant) | Rasa OSS in maintenance mode; already flagged as a divergence in the v1.0 Technology Stack Specification |
| INT-019 (Google Routes / Timefold) | FR-FSM-031 (VROOM + OSRM with selective traffic API) | Already the accepted v1.0 divergence; formalised |
| BR-BI-007 (drag-and-drop report builder) | FR-BID-018 (semantic-layer self-service exploration) | Warehouse-backed approach supersedes the point tool |
| BR-DMS-003 (approval workflows in DMS) | FR-IPF-020 (platform-wide workflow engine) | One workflow engine serves all modules |

---

*Next document: `03_ERP_Module_Architecture_and_System_Map.md`*
