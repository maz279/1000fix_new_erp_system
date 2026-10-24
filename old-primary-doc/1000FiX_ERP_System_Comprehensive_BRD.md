# BUSINESS REQUIREMENTS DOCUMENT (BRD)

# Comprehensive Enterprise Resource Planning (ERP) System & Smart Portal Suite

# For 1000FiX Services Limited

---

| **Document Information** | |
|---|---|
| **Document Title** | Business Requirements Document — Comprehensive ERP System & Smart Portal Suite |
| **Issuing Organization** | 1000FiX Services Limited |
| **Document Version** | 1.0 |
| **Date** | March 17, 2026 |
| **BRD Reference Number** | 1000FIX-ERP-BRD-2026-001 |
| **Related RFP** | 1000FIX-ERP-RFP-2026-001 |
| **Document Owner** | Chief Technology Officer |
| **Prepared By** | Business Analysis Team, 1000FiX Services Limited |
| **Classification** | CONFIDENTIAL — Internal Use Only |

---

**CONFIDENTIALITY NOTICE**

This Business Requirements Document (BRD) is the confidential property of 1000FiX Services Limited. It is intended solely for use by 1000FiX internal stakeholders and the selected ERP implementation vendor. It must not be disclosed to third parties without prior written consent.

---

## DOCUMENT REVISION HISTORY

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | March 10, 2026 | Business Analysis Team | Initial draft — Sections 1-5 |
| 0.5 | March 14, 2026 | Business Analysis Team | Added Sections 6-12 |
| 0.9 | March 16, 2026 | Business Analysis Team | Added Sections 13-22, full review |
| 1.0 | March 17, 2026 | CTO, 1000FiX | Final version issued |

---

## DOCUMENT APPROVALS

| Role | Name | Signature | Date |
|---|---|---|---|
| Project Sponsor / CEO | [Name] | _________ | _________ |
| CTO / IT Director | [Name] | _________ | _________ |
| Service Operations Director | [Name] | _________ | _________ |
| Finance Director / CFO | [Name] | _________ | _________ |
| HR Director | [Name] | _________ | _________ |
| ERP Implementation Vendor PM | [Name] | _________ | _________ |

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Business Context & Background](#2-business-context--background)
3. [Business Objectives](#3-business-objectives)
4. [Project Scope](#4-project-scope)
5. [Stakeholder Analysis](#5-stakeholder-analysis)
6. [Current State Analysis (As-Is)](#6-current-state-analysis-as-is)
7. [Future State Vision (To-Be)](#7-future-state-vision-to-be)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Business Rules](#10-business-rules)
11. [Data Requirements](#11-data-requirements)
12. [Business Process Flows](#12-business-process-flows)
13. [Use Cases](#13-use-cases)
14. [Integration Requirements](#14-integration-requirements)
15. [Assumptions](#15-assumptions)
16. [Constraints](#16-constraints)
17. [Dependencies](#17-dependencies)
18. [Risk Register](#18-risk-register)
19. [Cost-Benefit Analysis & ROI](#19-cost-benefit-analysis--roi)
20. [Acceptance Criteria & KPIs](#20-acceptance-criteria--kpis)
21. [Implementation Approach](#21-implementation-approach)
22. [Appendices](#22-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 The Business Problem

1000FiX Services Limited is Bangladesh's largest and only ISO 9001:2015 certified after-sales service provider, operating 51+ service centers across all 8 administrative divisions with 500+ employees serving 250,000+ customers monthly. Despite its market leadership, the Company's operational infrastructure remains critically fragmented:

- **No unified system** — Service orders, inventory, finance, HR, and customer data live in disconnected spreadsheets and standalone tools
- **Manual processes dominate** — Only ~20% of operations are automated; technician dispatch, warranty claims, and invoicing are all manual
- **Zero real-time visibility** — Management cannot see live operational status across 51+ locations
- **Scalability ceiling** — Current processes physically cannot support the Company's growth ambitions
- **Customer experience gap** — No self-service portal, no real-time tracking, no automated notifications

These inefficiencies cost the Company an estimated **BDT 2-3 crore annually** in lost productivity, delayed warranty billing, inventory waste, and customer churn.

### 1.2 The Proposed Solution

1000FiX will implement a **Comprehensive Enterprise Resource Planning (ERP) System** integrated with a **Smart Portal Suite of 6 web/mobile portals** to serve as the unified operational backbone of the entire business.

The ERP will cover all core business functions:

| Domain | Key Capability |
|---|---|
| Service & Repair Management | End-to-end service order lifecycle from intake to invoice |
| Field Service Management | AI-powered dispatch, GPS tracking, mobile technician app |
| Inventory Management | Multi-location stock across 51+ centers with auto-replenishment |
| CRM | 360° customer and device management |
| Financial Management | Multi-branch accounting, automated invoicing, VAT compliance |
| HR & Payroll | Technician workforce management and performance-linked payroll |
| Contract & Warranty | AMC/RAMC lifecycle, brand warranty claim processing |
| Procurement | Spare parts sourcing and vendor management |
| Business Intelligence | Real-time dashboards and analytics |

The ERP will integrate bidirectionally with 1000FiX's in-development 8-portal web platform (Next.js 15 + Payload CMS 3 + PostgreSQL 16), creating a complete digital ecosystem.

### 1.3 Strategic Alignment

This initiative is directly aligned with 1000FiX's 5-year digital transformation strategy, which targets:
- 87% revenue growth within 18 months of full ERP deployment
- 70% operational automation
- 5x business scale-up capability
- Expansion to new service categories and geographic markets

### 1.4 Investment Summary

| Category | 3-Year TCO |
|---|---|
| Software Licensing | $45,000 – $90,000 |
| Implementation Services | $60,000 – $150,000 |
| Training | $10,000 – $20,000 |
| Infrastructure / Hosting | $20,000 – $50,000 |
| Support & Maintenance | $15,000 – $40,000 |
| **Total (3-Year TCO)** | **$150,000 – $350,000** |

**Expected payback period: 12–18 months post full go-live.**

### 1.5 Document Purpose

This BRD defines the complete business requirements for the ERP system in sufficient detail to:
- Guide vendor selection and contract negotiations
- Serve as the implementation blueprint for the selected vendor
- Establish the acceptance criteria for each deliverable
- Provide a baseline for scope management and change control

---

## 2. BUSINESS CONTEXT & BACKGROUND

### 2.1 Company Overview

| Attribute | Details |
|---|---|
| **Legal Name** | 1000FiX Services Limited |
| **Founded** | August 29, 2017 |
| **Headquarters** | 586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh |
| **Hotline** | 16743 |
| **Website** | https://1000fix.com |
| **Certification** | ISO 9001:2015 — Bangladesh's only ISO-certified IT service provider |
| **Service Network** | 51+ service centers across all 8 divisions |
| **Employees** | 500+ (technicians, service center staff, support, management) |
| **Monthly Customers** | 250,000+ |
| **Brand Partnerships** | 17+ authorized warranty service agreements |

### 2.2 Industry Context

The Bangladesh after-sales service and electronics repair market is experiencing rapid transformation:

- The consumer electronics market in Bangladesh exceeds USD 2.5 billion annually
- Smartphone penetration has crossed 50 million active users
- Air conditioner penetration is growing at 18% per year in urban households
- Demand for professional after-sales service has surged with the rise of premium device ownership
- Brand manufacturers (Dell, HP, Samsung, etc.) increasingly rely on third-party authorized service networks rather than maintaining their own service infrastructure in developing markets

1000FiX has positioned itself uniquely in this landscape — the only ISO 9001:2015 certified provider in Bangladesh, with the broadest brand authorization portfolio and the largest geographic footprint. This certification is not merely symbolic; it commits the Company to documented quality processes, which creates the internal pressure to formalize and systematize operations.

### 2.3 Business Model

1000FiX operates five distinct revenue streams:

| Revenue Stream | Description | Estimated Contribution |
|---|---|---|
| **Authorized Warranty Service** | Repair services reimbursed by brand partners (Dell, HP, Samsung, etc.) | 35-40% |
| **Out-of-Warranty Paid Repairs** | Direct customer-paid repairs (all device categories) | 30-35% |
| **AMC/RAMC Subscriptions** | Annual/residential maintenance contracts (recurring revenue) | 15-20% |
| **Warranty Extension Sales** | Extended protection plans sold to customers | 5-8% |
| **Spare Parts & Accessories** | Genuine parts sold with or without service | 5-7% |

The **warranty service** revenue stream is particularly critical as it involves structured financial relationships with 17+ international brands. Efficient warranty claim processing directly impacts cash flow — delays of 30-90 days in submitting claims to brands are currently common due to manual processes.

### 2.4 Service Delivery Infrastructure

**Service Categories:**
- **IT Equipment**: Laptops (all brands + Level 1-3 motherboard repair), desktops, servers, printers/plotters, CCTV/networking, projectors, UPS, MacBook/Apple
- **Home Appliances**: AC (installation, cleaning, repair, gas refill), refrigerator, TV, washing machine, microwave, geyser, treadmill, combo packages
- **Mobile & Tablets**: All major brands, warranty and out-of-warranty

**Service Delivery Modes:**
1. Walk-in at service center
2. On-site/home service (technician dispatch)
3. Pick & Drop (device collection, repair, return)
4. Remote PC support

**Value-Added Programs:**
- Privilege Program: Silver/Gold/Diamond tiers (50% discount on service charges)
- RAMC: 6 home appliance maintenance packages
- Corporate AMC: Annual enterprise contracts
- Warranty Extension Program
- Laptop Rental Service
- Device Exchange/Trade-In

### 2.5 Why ERP — Now

The following factors have made 2026 the critical inflection point for ERP implementation:

1. **Scale pressure**: 51+ locations cannot be managed through spreadsheets; coordination failures are increasing
2. **Revenue leakage**: Manual warranty claim processing means an estimated 15-20% of warranty revenue is unclaimed or delayed beyond brand payment deadlines
3. **ISO compliance requirement**: ISO 9001:2015 requires documented, traceable processes — impossible without a system of record
4. **Concurrent web platform initiative**: 1000FiX is building an 8-portal web platform; the ERP must serve as its back-office engine
5. **Competitive threat**: Well-funded competitors are investing in digital capabilities; 1000FiX's scale advantage may erode without operational excellence
6. **Growth ambition**: Board-approved target of 87% revenue growth in 18 months requires operational capacity that only automation can provide

### 2.6 Current IT Landscape

| System | Purpose | Status |
|---|---|---|
| WordPress website (1000fix.com) | Public presence, basic booking | Being replaced |
| Manual spreadsheets | Service order tracking, inventory | Primary operational tool (critical gap) |
| Standalone accounting software | Basic bookkeeping | Disconnected from operations |
| WhatsApp/phone | Technician dispatch and communication | Ad-hoc, no tracking |
| Paper-based forms | Service reports, QC checklists | Physical archive, no search |
| Email | Warranty claims to brand partners | Untracked, no workflow |
| order tracking portal (station.1000fix.com) | Basic order status | Limited functionality |

---

## 3. BUSINESS OBJECTIVES

Each objective is SMART (Specific, Measurable, Achievable, Relevant, Time-bound) and is assigned an owner and linked to ERP domains.

| ID | Business Objective | Metric | Baseline | Target | Timeline | Owner | ERP Domain |
|---|---|---|---|---|---|---|---|
| **BO-01** | Automate the end-to-end service order lifecycle to eliminate manual coordination | % of service orders processed without manual intervention | 20% | 70% | 18 months | Service Ops Director | Service & Repair Mgmt |
| **BO-02** | Maximize field technician productivity through AI-powered scheduling and route optimization | Average jobs completed per technician per day | 4-5 | 7-8 | 12 months | Service Ops Director | Field Service Mgmt |
| **BO-03** | Achieve near-perfect inventory accuracy across all 51+ locations | Inventory accuracy rate | ~75% | 98%+ | 12 months | Warehouse Manager | Inventory Mgmt |
| **BO-04** | Recover all eligible warranty revenue from brand partners through timely claim submission | % of eligible warranty claims submitted within 7 days of service completion | ~50% | 95%+ | 9 months | Finance Director | Contract & Warranty Mgmt |
| **BO-05** | Improve customer satisfaction and reduce service TAT | Average service turnaround time; CSAT score | Avg TAT: unknown; CSAT: 3.8/5 | TAT: <24 hrs (IT), <4 hrs (appliance); CSAT: 4.7/5 | 12 months | Customer Service Manager | CRM |
| **BO-06** | Reduce monthly financial close cycle from 15-20 days to under 5 days | Days to financial close | 15-20 days | ≤5 days | 10 months | CFO | Financial Mgmt |
| **BO-07** | Enable real-time visibility across all branches for executive decision-making | Time to access branch performance data | Days/manual compilation | Real-time dashboard (< 5 sec) | 12 months | CEO | BI & Reporting |
| **BO-08** | Drive AMC/RAMC subscription growth through automated renewal management | Contract renewal rate; AMC customer base | ~60% renewal | 85%+ renewal; 2x customer base | 18 months | Sales Director | Contract Mgmt |
| **BO-09** | Enable 87% revenue growth by removing operational capacity constraints | Annual revenue growth | Baseline | +87% (18 months) | 18 months | CEO | All Modules |
| **BO-10** | Ensure full Bangladesh regulatory compliance (VAT, tax, labor law) with zero manual intervention | Tax compliance audit findings; late filing incidents | Manual, error-prone | Zero non-compliance incidents | 10 months | CFO / HR Director | Finance & HR |

---

## 4. PROJECT SCOPE

### 4.1 In-Scope

#### ERP Core Modules (11)

| # | Module | Scope Description |
|---|---|---|
| 1 | Service & Repair Management | Complete service order lifecycle; multi-channel intake; workflow management; SLA tracking |
| 2 | Field Service Management | Technician scheduling, AI dispatch, GPS tracking, mobile app, route optimization |
| 3 | Inventory & Spare Parts | Multi-location (51+) stock management; van inventory; auto-replenishment |
| 4 | Customer Relationship Management | Customer/device database; service history; loyalty programs; communications |
| 5 | Financial Management | GL, AR, AP, invoicing, payment, bank reconciliation, VAT, financial reporting |
| 6 | HR & Payroll | Employee management; technician skills; attendance; payroll; training |
| 7 | Contract & Warranty Management | AMC/RAMC lifecycle; brand warranty claims; SLA enforcement |
| 8 | Procurement & Supply Chain | Purchase requisition, PO, GRN, vendor management |
| 9 | Business Intelligence & Reporting | Real-time dashboards; KPI tracking; custom reports; analytics |
| 10 | Document Management | Digital forms; e-signatures; document storage; approval workflows |
| 11 | Quality Management | ISO 9001:2015 compliance; CAPA; complaint management; QC checklists |

#### Smart Portal Suite (6 Portals)

| # | Portal | Users | Key Functions |
|---|---|---|---|
| 1 | Customer Self-Service Portal | 250,000+ monthly | Service booking, order tracking, invoice/payment, loyalty management |
| 2 | Technician Mobile Portal (PWA) | 200-400 technicians | Job queue, GPS navigation, digital forms, parts recording, e-signature |
| 3 | Admin Operations Portal | 100-150 back-office users | Service dispatch, inventory, customer management, system configuration |
| 4 | Corporate B2B Portal | 500-2,000 corporate users | AMC management, bulk booking, consolidated invoicing, SLA monitoring |
| 5 | Vendor & Partner Portal | 100-500 vendors/brand partners | PO management, warranty claims, invoice submission |
| 6 | Analytics Dashboard | 15-25 management users | Executive dashboards, branch performance, trend analysis |

#### Integrations
- Bidirectional API with 1000FiX web platform (Next.js 15 + Payload CMS 3)
- Bangladesh payment gateways: bKash, Nagad, SSLCOMMERZ
- SMS gateway (Bangladesh)
- WhatsApp Business API
- Google Maps + Route Optimization API
- Firebase push notifications
- AI chatbot (Rasa 3.6 Bengali NLP) — integration only
- Biometric attendance devices

#### Data Migration
- All 9 identified data sources (customer data, service history, inventory, financial records, contracts, HR records, vendor data, device registry, documents)

#### Training & Change Management
- All 6 user groups; Bengali and English materials; train-the-trainer program

#### Post-Go-Live Support
- 12-month warranty support; ongoing AMS

### 4.2 Out of Scope

The following are **explicitly excluded** from this project:

| # | Excluded Item | Reason / Notes |
|---|---|---|
| OOS-1 | Development of the 8-portal web platform (Next.js 15 + Payload CMS) | Separate project; ERP integrates with it but does not replace it |
| OOS-2 | E-commerce / spare parts online store development | Handled by the web platform project |
| OOS-3 | Marketing automation platform | Not an ERP function; future initiative |
| OOS-4 | Fleet management for delivery vehicles | Not in current scope |
| OOS-5 | Property / real estate management for service center premises | Outside core operations |
| OOS-6 | AI-powered predictive maintenance engine | Future Phase 7+ initiative |
| OOS-7 | ERP for 1000FiX's vendor/supplier companies | Only vendor portal, not their internal systems |
| OOS-8 | Direct integration with individual brand partner back-end ERP systems | Vendor portal + manual/email export to brand partners |
| OOS-9 | Custom hardware development (barcode scanners, kiosks) | Standard commercial hardware used |
| OOS-10 | Business process outsourcing or call center platform | Not in ERP scope |

### 4.3 Phase Boundaries

| Phase | Modules | Go-Live |
|---|---|---|
| Phase 1 — Foundation | Service & Repair, CRM, Basic Inventory | Month 4 |
| Phase 2 — Field Operations | Field Service, Technician Portal, Route Optimization | Month 7 |
| Phase 3 — Financial Control | Finance & Accounting, Invoicing, Payment Integration | Month 10 |
| Phase 4 — Contracts & Partners | Contract/Warranty, Vendor Portal, B2B Portal | Month 13 |
| Phase 5 — Workforce & Intelligence | HR & Payroll, Full BI, Quality Management | Month 16 |
| Phase 6 — Optimization | Document Mgmt, Advanced Analytics, Full Integration | Month 18 |

---

## 5. STAKEHOLDER ANALYSIS

### 5.1 Stakeholder Register

| ID | Stakeholder | Role/Title | Department | Interest | Influence | Impact |
|---|---|---|---|---|---|---|
| STK-01 | CEO / Managing Director | Executive Sponsor | Executive | ROI, growth, competitive position | Very High | Very High |
| STK-02 | CTO / IT Director | Technical Authority | IT | Architecture, integration, security | Very High | Very High |
| STK-03 | CFO / Finance Director | Financial Requirements Owner | Finance | Accurate reporting, VAT compliance, cash flow | High | High |
| STK-04 | Service Operations Director | Primary Process Owner | Operations | Service efficiency, SLA compliance | High | Very High |
| STK-05 | HR Director | HR Module Owner | HR | Payroll accuracy, workforce management | Medium | High |
| STK-06 | Sales & Marketing Director | CRM/Contract Module Owner | Sales | Pipeline visibility, AMC renewals | Medium | Medium |
| STK-07 | Branch Managers (51+) | Local Operations Leads | Operations | Branch visibility, local inventory | High | High |
| STK-08 | Field Technicians (200-400) | Primary Mobile App Users | Field Service | Easy-to-use app, clear job queue | Very High | Very High |
| STK-09 | Service Center Staff (150-250) | Walk-In Service Operations | Operations | Fast order entry, customer lookup | High | High |
| STK-10 | Customer Service Agents (30-50) | Call Center / Hotline | Customer Service | Quick CRM access, order visibility | High | High |
| STK-11 | Warehouse / Inventory Manager | Inventory Module Owner | Inventory | Stock accuracy, replenishment alerts | High | High |
| STK-12 | Finance / Billing Staff (15-25) | AR/AP Processing | Finance | Invoice automation, payment reconciliation | High | High |
| STK-13 | IT Administrator (5-10) | System Administration | IT | System stability, user management | Medium | High |
| STK-14 | Quality Assurance Manager | ISO Compliance Owner | Quality | QMS features, audit trails, CAPA | Medium | Medium |
| STK-15 | Corporate B2B Clients | External Portal Users | External | Self-service, consolidated billing, SLA data | Medium | Medium |
| STK-16 | Individual Customers | External Portal Users | External | Easy booking, real-time tracking, fast service | High | High |
| STK-17 | Brand Partners (Dell, HP, etc.) | Warranty Claim Recipients | External | Accurate claim data, timely submission | Medium | Medium |
| STK-18 | Spare Parts Vendors | Procurement Counterparties | External | Clear POs, timely payment, portal access | Low | Low |
| STK-19 | Bangladesh NBR | Regulatory Authority | Government | VAT compliance, tax filing | Low | High |
| STK-20 | ERP Vendor / Implementation Team | Solution Delivery | External | Clear requirements, timely decisions, payment | High | Very High |

### 5.2 RACI Matrix

Activities are listed on rows; key stakeholder groups on columns. **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed.

| Activity | CEO | CTO | CFO | Ops Dir | HR Dir | Branch Mgrs | Technicians | Finance Staff | ERP Vendor |
|---|---|---|---|---|---|---|---|---|---|
| Define business objectives | A | C | C | C | C | I | I | I | I |
| Approve BRD | A | C | C | C | C | I | I | I | I |
| Define functional requirements | I | C | C | R | C | C | C | C | C |
| Vendor evaluation & selection | A | R | C | C | I | I | I | I | — |
| Contract negotiation | A | C | R | C | I | I | I | I | R |
| Project kickoff | A | R | I | I | I | I | I | I | R |
| Solution design | I | A | C | C | C | I | I | I | R |
| System configuration | I | C | C | C | C | I | I | I | R |
| Data migration | I | R | C | C | C | I | I | C | R |
| User acceptance testing (UAT) | I | C | C | R | C | R | R | R | C |
| Go-live approval | A | C | C | C | C | I | I | I | C |
| Training delivery | I | C | I | C | C | C | R | R | R |
| Post-go-live support | I | A | I | C | I | C | C | I | R |
| Performance monitoring | A | C | C | C | C | C | I | I | I |

---

## 6. CURRENT STATE ANALYSIS (AS-IS)

### 6.1 Current System Landscape

```
+------------------+     +------------------+     +------------------+
|  WordPress Site  |     | Manual           |     | Standalone       |
|  (1000fix.com)   |     | Spreadsheets     |     | Accounting Tool  |
|  - Basic booking |     | - Service orders |     | - Basic GL       |
|  - No real-time  |     | - Inventory      |     | - No integration |
+------------------+     | - Customer data  |     +------------------+
                          +------------------+
         +------------------+     +------------------+
         | WhatsApp/Phone   |     | Paper Forms      |
         | - Technician     |     | - Service reports|
         |   dispatch       |     | - QC checklists  |
         | - No tracking    |     | - Warranty claims|
         +------------------+     +------------------+
```

**System Integration Score: ZERO** — No systems are connected to each other. All data reconciliation is done manually.

### 6.2 As-Is Process Analysis

#### Process 1: Service Request Intake
- **Current**: Customer calls hotline (16743) or walks in → Agent writes on paper or enters into spreadsheet → No automatic acknowledgment → No tracking number generated consistently
- **Pain Points**: Data entry errors; no search capability; no SMS acknowledgment; no service history lookup at intake

#### Process 2: Technician Dispatch
- **Current**: Coordinator reviews paper job list → Calls/WhatsApps technician → Verbal assignment → No tracking of acceptance → No GPS monitoring
- **Pain Points**: No visibility into technician location or workload; no skill-matching; frequent re-assignments; technician productivity unknown

#### Process 3: Service Execution & Reporting
- **Current**: Technician uses paper service form → Customer signs paper → Technician returns form to service center → Form manually entered into spreadsheet (often delayed 1-3 days)
- **Pain Points**: No real-time updates; data entry backlog; forms lost; no before/after photos standardized; no quality checklist enforcement

#### Process 4: Inventory Management
- **Current**: Each service center tracks own stock in local spreadsheets → No central visibility → Phone calls between branches to check availability → Manual replenishment requests
- **Pain Points**: Stockouts at one branch while excess at another; no automatic reorder alerts; no consumption analysis; van stock entirely untracked

#### Process 5: Warranty Claim Processing
- **Current**: Finance/admin prepares warranty claim manually from paper service forms → Emails to brand partner → Awaits response → Follows up manually → Reconciles payment via email
- **Pain Points**: 30-90 day claim submission delays; claims lost or forgotten; ~15-20% revenue leakage; no tracking of claim status; reconciliation takes weeks

#### Process 6: Invoicing & Payment
- **Current**: Billing staff manually creates invoice from paper service form → Invoice sent via WhatsApp/email/printed → Payment received in cash or bank transfer → Manually recorded
- **Pain Points**: Invoice errors; delayed invoicing (often 3-7 days post-service); no automated reminders; cash reconciliation unreliable

#### Process 7: AMC/RAMC Management
- **Current**: Contract created in spreadsheet → Renewal reminders manually checked and communicated → Scheduled maintenance tracked in calendar → No system-driven alerts
- **Pain Points**: Renewal lapses due to missed follow-up; no utilization tracking; no auto-invoicing; profitability unknown per contract

#### Process 8: Financial Reporting
- **Current**: Finance team collects branch spreadsheets monthly → Consolidates manually in Excel → Produces P&L 15-20 days after month-end
- **Pain Points**: 15-20 day close cycle; consolidation errors; branch data incomplete; no real-time dashboards; decisions made on stale data

#### Process 9: HR & Payroll
- **Current**: Attendance via manual sign-in book → Leave tracked in spreadsheet → Payroll calculated manually in Excel → Bank transfers initiated individually
- **Pain Points**: Attendance errors; leave balance disputes; payroll calculation errors; overtime tracking inaccurate; no performance-linked incentive calculation

#### Process 10: Customer Communication
- **Current**: Status updates given verbally when customer calls → No proactive notifications → No service completion confirmation except verbal
- **Pain Points**: Customer calls hotline multiple times for status → Call center overwhelmed → Low customer satisfaction; no digital communication audit trail

### 6.3 Performance Baseline Metrics

| Metric | Current Baseline | Industry Benchmark | Gap |
|---|---|---|---|
| Service order automation rate | ~20% | 60-80% | -40-60% |
| Average jobs per technician/day | 4-5 | 7-9 | -3-4 jobs |
| First-time fix rate | ~70% | 80-90% | -10-20% |
| Inventory accuracy | ~75% | 95-99% | -20-24% |
| Warranty claim submission time | 30-90 days | <7 days | -23-83 days |
| Month-end financial close | 15-20 days | 3-5 days | -10-15 days |
| Customer CSAT | 3.8/5 | 4.5-4.8/5 | -0.7-1.0 |
| Online booking rate | ~40% | 70-90% | -30-50% |
| AMC renewal rate | ~60% | 80-90% | -20-30% |
| Technician utilization rate | ~55% | 75-85% | -20-30% |

### 6.4 Financial Impact of Current State Gaps

| Gap | Estimated Annual Cost |
|---|---|
| Unclaimed/delayed warranty revenue | BDT 80-120 lacs |
| Technician underutilization | BDT 60-90 lacs (labor cost vs. output) |
| Inventory waste (excess + stockouts) | BDT 30-50 lacs |
| Manual invoicing delays (cash flow cost) | BDT 20-30 lacs |
| Customer churn from poor experience | BDT 40-70 lacs |
| Excessive administrative overhead | BDT 25-40 lacs |
| **Total Estimated Annual Cost** | **BDT 2.55 – 4.0 crore** |

---

## 7. FUTURE STATE VISION (TO-BE)

### 7.1 Future System Landscape

```
+===========================================================================+
|                    1000FiX DIGITAL ECOSYSTEM (TO-BE)                      |
|                                                                           |
| +---------------------------+     +-----------------------------------+   |
| |   ERP CORE SYSTEM         |<--->|   8-PORTAL WEB PLATFORM           |   |
| |  (Back-Office Engine)     | API |   (Next.js 15 + Payload CMS 3)    |   |
| |                           |     |                                   |   |
| | • Service & Repair Mgmt   |     | • Customer Portal                 |   |
| | • Field Service Mgmt      |     | • Technician Mobile Portal        |   |
| | • Inventory Mgmt          |     | • Admin Operations Portal         |   |
| | • CRM                     |     | • Corporate B2B Portal            |   |
| | • Financial Management    |     | • Vendor/Partner Portal           |   |
| | • HR & Payroll            |     | • Analytics Dashboard             |   |
| | • Contract & Warranty     |     | • AI Chatbot (Rasa 3.6 Bengali)   |   |
| | • Procurement             |     | • Public Website                  |   |
| | • BI & Analytics          |     |                                   |   |
| | • Document Management     |     +-----------------------------------+   |
| | • Quality Management      |                                            |
| +---------------------------+                                            |
|        |          |          |                                            |
|   +----+    +-----+    +-----+----+                                      |
|   |bKash|  |Nagad|  |SSLCOMMERZ| (Payment Gateways)                     |
|   +----+    +-----+    +----------+                                      |
|        |                                                                  |
|   +----+-------+  +----------+  +----------+  +----------+              |
|   |Google Maps |  |SMS Gateway|  |WhatsApp  |  |Firebase  |              |
|   |Route Optim.|  |Bangladesh |  |Business  |  |Push Notif|              |
|   +------------+  +----------+  +----------+  +----------+              |
+===========================================================================+
```

### 7.2 Departmental Transformation

#### Service Operations — From Reactive to Proactive
- **Today**: Coordinator manually assigns jobs by phone, no visibility into field operations
- **Tomorrow**: AI dispatch engine automatically assigns and schedules jobs; coordinator monitors live map; SLA alerts fire automatically; escalations are rule-driven

#### Field Technicians — From Paper to Mobile
- **Today**: Paper service form, verbal customer sign-off, manual parts recording
- **Tomorrow**: Mobile PWA shows full job queue and GPS navigation; digital checklist auto-populates from device history; customer signs on screen; parts scanned via barcode; data syncs to ERP in real time

#### Inventory — From Guesswork to Precision
- **Today**: Branch calls other branches to find parts; no central visibility
- **Tomorrow**: One dashboard shows stock levels at all 51+ locations; auto-replenishment orders are generated when stock hits reorder point; inter-branch transfer requests processed digitally

#### Finance — From Manual to Automated
- **Today**: Invoice typed from paper form, sent via WhatsApp, payment manually recorded
- **Tomorrow**: Invoice generated automatically when work order is closed; bKash/Nagad payment link sent to customer; payment auto-reconciled in accounting system; warranty claims auto-submitted to brand partners

#### Customer Experience — From Opaque to Transparent
- **Today**: Customer calls hotline 3+ times to get status update
- **Tomorrow**: Customer receives SMS at booking, dispatch, en-route, completed; can track technician on map; receives digital invoice; rates service via portal

### 7.3 Key Automation Scenarios (Target: 70%)

| # | Automation Scenario | Manual Steps Eliminated |
|---|---|---|
| A1 | Service order auto-created from web booking, WhatsApp chatbot, or walk-in terminal | Manual spreadsheet entry |
| A2 | AI dispatch auto-assigns technician based on skills, location, availability | Phone/WhatsApp assignment |
| A3 | Technician route auto-optimized for all daily jobs | No route planning |
| A4 | Customer SMS/WhatsApp notification at each status milestone | Manual customer call |
| A5 | Invoice auto-generated when work order closed | Manual invoice preparation |
| A6 | Payment link auto-sent to customer on invoice creation | Manual payment collection |
| A7 | Warranty claim auto-prepared from closed work order and submitted to brand | Manual claim compilation and emailing |
| A8 | Inventory reorder alert auto-generated when stock falls below minimum | Manual stock checks |
| A9 | AMC renewal notification auto-sent 60/30/15 days before expiry | Manual calendar reminders |
| A10 | Payroll auto-calculated from attendance and performance data | Manual Excel calculation |
| A11 | VAT return auto-compiled from invoice and payment data | Manual VAT calculation |
| A12 | Financial reports auto-generated at period-end | Manual Excel consolidation |
| A13 | CSAT survey auto-sent after service completion | No systematic follow-up |
| A14 | SLA breach alerts auto-escalated to manager | No SLA tracking |

---

## 8. FUNCTIONAL REQUIREMENTS

Requirements are classified per IIBA BABOK v3:
- **BR** = Business Requirement (goal/outcome)
- **SR** = Stakeholder Requirement (what a stakeholder needs)
- **FR** = Functional Requirement ("The system shall…")
- **TR** = Transition Requirement (migration/training need)

Priority: **P1** = Must-Have | **P2** = Important | **P3** = Nice-to-Have
Linked to Business Objective (BO-01 to BO-10).

---

### 8.1 Service & Repair Management (SRM)

**Business Requirement**: Provide a unified system of record for all service orders across all channels and locations, enabling 70% automation of the service delivery lifecycle. *(Links: BO-01, BO-05)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-SRM-001 | FR | The system shall create service orders from the following channels: web portal, WhatsApp chatbot, phone (manual entry by agent), walk-in terminal, and email | P1 | BO-01 |
| BR-SRM-002 | FR | The system shall auto-generate a unique service order number upon creation | P1 | BO-01 |
| BR-SRM-003 | FR | The system shall classify service orders by type: Warranty, Out-of-Warranty, AMC, RAMC, Emergency, Preventive Maintenance | P1 | BO-04 |
| BR-SRM-004 | FR | The system shall support the full service order lifecycle: Created → Assigned → In Progress → Parts Pending → Completed → Invoiced → Closed → Archived | P1 | BO-01 |
| BR-SRM-005 | FR | The system shall link each service order to a specific customer record and device record (by serial number) | P1 | BO-05 |
| BR-SRM-006 | FR | The system shall display complete service history for any device when a new service order is created | P1 | BO-05 |
| BR-SRM-007 | FR | The system shall define and track SLA timelines per service type, brand partner, and customer tier | P1 | BO-05 |
| BR-SRM-008 | FR | The system shall trigger escalation alerts at 50%, 75%, and 90% of SLA elapsed time | P1 | BO-05 |
| BR-SRM-009 | FR | The system shall send automated customer notifications (SMS + WhatsApp) at each lifecycle milestone | P1 | BO-05 |
| BR-SRM-010 | FR | The system shall support before/after photo attachments to service orders with timestamp and GPS tag | P1 | BO-01 |
| BR-SRM-011 | FR | The system shall enforce configurable approval workflows for repairs exceeding a specified cost threshold | P1 | BO-06 |
| BR-SRM-012 | FR | The system shall generate customer-facing repair quotations with digital approval (accept/reject) | P1 | BO-05 |
| BR-SRM-013 | FR | The system shall maintain diagnostic checklist templates per device type and complaint category | P1 | BO-02 |
| BR-SRM-014 | FR | The system shall track labor time per service order (technician time entry from mobile) | P1 | BO-02 |
| BR-SRM-015 | FR | The system shall track parts consumed per service order, linked directly to inventory deductions | P1 | BO-03 |
| BR-SRM-016 | FR | The system shall flag rework cases (same device returning for same issue within 30 days) | P1 | BO-05 |
| BR-SRM-017 | FR | The system shall support configurable service order templates for common repair types | P2 | BO-01 |
| BR-SRM-018 | FR | The system shall support repair level classification: Level 1 (Basic), Level 2 (Intermediate), Level 3 (Board-Level/Advanced) | P1 | BO-02 |
| BR-SRM-019 | FR | The system shall generate warranty claims automatically upon closing a warranty-type service order | P1 | BO-04 |
| BR-SRM-020 | SR | Technicians require access to complete device and customer history from the service order on mobile | P1 | BO-02 |

---

### 8.2 Field Service Management (FSM)

**Business Requirement**: Deploy an AI-powered field service management capability that maximizes technician productivity through intelligent scheduling, real-time tracking, and mobile-first operations. *(Links: BO-02, BO-05)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-FSM-001 | FR | The system shall provide an AI-powered scheduling engine that assigns technicians based on: skill/certification, geographic zone, current workload, job priority, and van inventory | P1 | BO-02 |
| BR-FSM-002 | FR | The system shall provide a visual dispatch board (calendar + map view) with drag-and-drop assignment capability | P1 | BO-02 |
| BR-FSM-003 | FR | The system shall track real-time GPS location of all active field technicians on a live map | P1 | BO-02 |
| BR-FSM-004 | FR | The system shall optimize daily routes for each technician to minimize travel time across all assigned jobs | P1 | BO-02 |
| BR-FSM-005 | FR | The system shall support insertion of emergency jobs with automatic re-optimization of affected technician's schedule | P1 | BO-02 |
| BR-FSM-006 | FR | The system shall manage service territories/zones with geo-fencing per branch | P2 | BO-02 |
| BR-FSM-007 | FR | The system shall provide a mobile app (PWA or native) with offline capability for field technicians | P1 | BO-02 |
| BR-FSM-008 | FR | The mobile app shall display the technician's daily job queue with priority, schedule, and navigation | P1 | BO-02 |
| BR-FSM-009 | FR | The mobile app shall provide GPS navigation to each job site via Google Maps integration | P1 | BO-02 |
| BR-FSM-010 | FR | The mobile app shall auto-capture time stamps for: departed, arrived, repair started, repair completed | P1 | BO-02 |
| BR-FSM-011 | FR | The mobile app shall enable barcode/QR code scanning for parts consumption recording | P1 | BO-03 |
| BR-FSM-012 | FR | The mobile app shall capture customer electronic signature on service completion | P1 | BO-05 |
| BR-FSM-013 | FR | The mobile app shall function in offline mode and sync all data when connectivity is restored | P1 | BO-02 |
| BR-FSM-014 | FR | The system shall provide customers with a real-time technician tracking link with ETA on the day of service | P1 | BO-05 |
| BR-FSM-015 | FR | The system shall manage pick & drop service lifecycle: pickup scheduled → picked up → in repair → completed → delivery scheduled → delivered | P1 | BO-01 |
| BR-FSM-016 | SR | Technicians require access to device repair history, diagnostic guides, and troubleshooting references on mobile | P2 | BO-02 |
| BR-FSM-017 | FR | The mobile app shall support offline photo capture (before/after) with auto-sync | P1 | BO-01 |

---

### 8.3 Inventory & Spare Parts Management (INV)

**Business Requirement**: Achieve 98%+ inventory accuracy across all 51+ locations with automated replenishment eliminating stockouts and excess. *(Links: BO-03)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-INV-001 | FR | The system shall manage inventory across 51+ service center locations plus central warehouse(s) | P1 | BO-03 |
| BR-INV-002 | FR | The system shall track van/mobile stock per technician (parts carried in the field) | P1 | BO-03 |
| BR-INV-003 | FR | The system shall provide a single dashboard showing real-time stock levels at all locations | P1 | BO-07 |
| BR-INV-004 | FR | The system shall support barcode and QR code scanning for all stock movements | P1 | BO-03 |
| BR-INV-005 | FR | The system shall support serial number tracking for high-value spare parts | P1 | BO-03 |
| BR-INV-006 | FR | The system shall automatically generate replenishment alerts when stock falls below configured minimum levels | P1 | BO-03 |
| BR-INV-007 | FR | The system shall support inter-branch stock transfer requests with approval workflow | P1 | BO-03 |
| BR-INV-008 | FR | The system shall automatically reserve parts against a service order when parts requisition is created | P1 | BO-03 |
| BR-INV-009 | FR | The system shall maintain a master parts catalog with compatibility mapping to device brands and models | P1 | BO-03 |
| BR-INV-010 | FR | The system shall classify parts as: Genuine (OEM), Compatible, Refurbished | P1 | BO-03 |
| BR-INV-011 | FR | The system shall support FIFO and weighted average stock valuation methods | P1 | BO-06 |
| BR-INV-012 | FR | The system shall support goods receipt with quality inspection step before stocking | P1 | BO-03 |
| BR-INV-013 | FR | The system shall support cycle counting with variance reporting | P1 | BO-03 |
| BR-INV-014 | FR | The system shall track defective parts returns to vendor (RTV) | P1 | BO-03 |
| BR-INV-015 | FR | The system shall identify and report dead stock (no movement in configurable period) | P2 | BO-03 |

---

### 8.4 Customer Relationship Management (CRM)

**Business Requirement**: Build a 360° view of every customer and device to enable personalized service, improve retention, and drive loyalty program growth. *(Links: BO-05, BO-08)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-CRM-001 | FR | The system shall maintain a unified customer record with: personal information, contact details, address(es), device registry, service history, contracts, invoices, and communication history | P1 | BO-05 |
| BR-CRM-002 | FR | The system shall maintain a device registry per customer: brand, model, serial number, purchase date, warranty expiry, condition | P1 | BO-04 |
| BR-CRM-003 | FR | The system shall segment customers as: Individual, Corporate, Privilege Member (Silver/Gold/Diamond), AMC Holder | P1 | BO-08 |
| BR-CRM-004 | FR | The system shall record and display communication history for each customer across all channels | P1 | BO-05 |
| BR-CRM-005 | FR | The system shall send automated post-service satisfaction surveys (CSAT + NPS) via SMS/WhatsApp | P1 | BO-05 |
| BR-CRM-006 | FR | The system shall manage Privilege Program tiers: enrollment, upgrade rules, benefit application, renewal | P1 | BO-08 |
| BR-CRM-007 | FR | The system shall manage corporate/B2B accounts with multiple contacts, multiple locations, and bulk service capabilities | P1 | BO-08 |
| BR-CRM-008 | FR | The system shall provide complaint management with root cause classification and resolution tracking | P1 | BO-05 |
| BR-CRM-009 | FR | The system shall detect and flag duplicate customer records with merge functionality | P2 | BO-05 |
| BR-CRM-010 | FR | The system shall support promotional campaign management with coupon/voucher generation and tracking | P2 | BO-08 |

---

### 8.5 Financial Management (FIN)

**Business Requirement**: Automate financial operations from service order to cash with full Bangladesh regulatory compliance. *(Links: BO-06, BO-10)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-FIN-001 | FR | The system shall maintain a multi-branch chart of accounts with configurable structure per branch and cost center | P1 | BO-06 |
| BR-FIN-002 | FR | The system shall automatically generate invoices from completed service orders without manual data entry | P1 | BO-06 |
| BR-FIN-003 | FR | The system shall generate warranty claim invoices to brand partners with all required documentation attached | P1 | BO-04 |
| BR-FIN-004 | FR | The system shall support multiple payment methods: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer | P1 | BO-06 |
| BR-FIN-005 | FR | The system shall automatically calculate and apply Bangladesh VAT on all applicable transactions | P1 | BO-10 |
| BR-FIN-006 | FR | The system shall generate Bangladesh NBR-compliant tax invoices (Mushak format) | P1 | BO-10 |
| BR-FIN-007 | FR | The system shall automate bank reconciliation with imported bank statements | P1 | BO-06 |
| BR-FIN-008 | FR | The system shall generate branch-wise P&L and consolidated financial statements | P1 | BO-06, BO-07 |
| BR-FIN-009 | FR | The system shall track accounts receivable aging with automated payment reminder workflows | P1 | BO-06 |
| BR-FIN-010 | FR | The system shall process vendor invoices with 3-way matching (PO + GRN + Invoice) | P1 | BO-06 |
| BR-FIN-011 | FR | The system shall support AMC/RAMC subscription billing with configurable billing cycles | P1 | BO-08 |
| BR-FIN-012 | FR | The system shall support Bangladesh fiscal year (July–June) and period management | P1 | BO-06 |
| BR-FIN-013 | FR | The system shall maintain a complete, immutable audit trail for all financial transactions | P1 | BO-10 |
| BR-FIN-014 | FR | The system shall support credit note and refund processing | P1 | BO-06 |
| BR-FIN-015 | FR | The system shall track fixed assets and calculate depreciation | P2 | BO-06 |

---

### 8.6 Human Resource Management & Payroll (HRM)

**Business Requirement**: Manage the full technician and staff workforce lifecycle with performance-linked payroll that motivates and retains talent. *(Links: BO-02, BO-10)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-HRM-001 | FR | The system shall maintain employee master records with all personal, employment, and qualification data | P1 | BO-10 |
| BR-HRM-002 | FR | The system shall maintain a skill matrix for all technicians: certifications, brand authorizations, specializations, expiry dates | P1 | BO-02 |
| BR-HRM-003 | FR | The system shall send certification expiry alerts 60/30/15 days before expiry | P1 | BO-02 |
| BR-HRM-004 | FR | The system shall track attendance via biometric device integration or GPS-based mobile clock-in | P1 | BO-02 |
| BR-HRM-005 | FR | The system shall manage all leave types (annual, sick, casual, maternity/paternity) with balance tracking | P1 | BO-10 |
| BR-HRM-006 | FR | The system shall manage Bangladesh public holiday calendar with automatic application | P1 | BO-10 |
| BR-HRM-007 | FR | The system shall calculate payroll including: basic salary, allowances, overtime, incentives, statutory deductions | P1 | BO-10 |
| BR-HRM-008 | FR | The system shall calculate performance-based incentives for technicians based on jobs completed, CSAT ratings, and first-time fix rate | P1 | BO-02 |
| BR-HRM-009 | FR | The system shall deduct income tax as per Bangladesh tax slabs and provident fund contributions | P1 | BO-10 |
| BR-HRM-010 | FR | The system shall generate bank salary transfer files in Bangladesh bank-compatible format | P1 | BO-10 |
| BR-HRM-011 | FR | The system shall generate and distribute digital payslips to employees | P1 | BO-10 |
| BR-HRM-012 | FR | The system shall manage training programs: course catalog, enrollment, attendance, completion, certification | P1 | BO-02 |

---

### 8.7 Contract & Warranty Management (CWM)

**Business Requirement**: Recover 100% of warranty revenue through automated claim management and grow AMC/RAMC subscription base through systematic renewal management. *(Links: BO-04, BO-08)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-CWM-001 | FR | The system shall create and manage AMC contracts with: covered devices, service inclusions, response SLAs, visit schedule, billing terms | P1 | BO-08 |
| BR-CWM-002 | FR | The system shall automatically generate scheduled maintenance work orders from active AMC/RAMC contracts | P1 | BO-08 |
| BR-CWM-003 | FR | The system shall track AMC contract utilization: visits used vs. included, parts consumed | P1 | BO-08 |
| BR-CWM-004 | FR | The system shall send renewal alerts at 60, 30, and 15 days before contract expiry | P1 | BO-08 |
| BR-CWM-005 | FR | The system shall auto-validate warranty status when a service order is created (by serial number + purchase date) | P1 | BO-04 |
| BR-CWM-006 | FR | The system shall auto-generate warranty claim records from closed warranty-type service orders | P1 | BO-04 |
| BR-CWM-007 | FR | The system shall track warranty claim lifecycle: Submitted → Under Review → Approved → Parts Shipped → Completed → Billed → Paid | P1 | BO-04 |
| BR-CWM-008 | FR | The system shall attach all required documentation to warranty claims (photos, diagnostic report, parts used) | P1 | BO-04 |
| BR-CWM-009 | FR | The system shall reconcile brand partner warranty payments against submitted claims | P1 | BO-04 |
| BR-CWM-010 | FR | The system shall manage warranty extension products: enrollment, billing, and coverage tracking | P1 | BO-08 |
| BR-CWM-011 | FR | The system shall define and monitor SLAs per service type, customer tier, and contract with real-time dashboard | P1 | BO-05 |
| BR-CWM-012 | FR | The system shall produce contract profitability analysis (revenue vs. actual cost of services delivered) | P2 | BO-08 |

---

### 8.8 Procurement & Supply Chain (SCM)

**Business Requirement**: Streamline spare parts procurement to ensure part availability while minimizing excess inventory investment. *(Links: BO-03)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-SCM-001 | FR | The system shall maintain a vendor master with classification: OEM, authorized distributor, local supplier | P1 | BO-03 |
| BR-SCM-002 | FR | The system shall support purchase requisition with approval workflow | P1 | BO-03 |
| BR-SCM-003 | FR | The system shall auto-generate purchase orders from approved replenishment alerts | P2 | BO-03 |
| BR-SCM-004 | FR | The system shall record goods receipt with quality inspection before stocking | P1 | BO-03 |
| BR-SCM-005 | FR | The system shall perform 3-way matching: PO + GRN + Vendor Invoice | P1 | BO-06 |
| BR-SCM-006 | FR | The system shall manage return-to-vendor (RTV) for defective or incorrect parts | P1 | BO-03 |
| BR-SCM-007 | FR | The system shall track vendor performance: on-time delivery rate, quality rejection rate, lead time | P2 | BO-03 |

---

### 8.9 Business Intelligence & Reporting (BI)

**Business Requirement**: Provide real-time operational and financial visibility to all management levels to enable data-driven decision-making. *(Links: BO-07, BO-09)*

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-BI-001 | FR | The system shall provide a real-time executive dashboard with configurable KPIs | P1 | BO-07 |
| BR-BI-002 | FR | The system shall provide branch performance dashboards comparing all 51+ locations | P1 | BO-07 |
| BR-BI-003 | FR | The system shall track technician performance: jobs/day, first-time fix rate, CSAT, rework rate, earnings | P1 | BO-02 |
| BR-BI-004 | FR | The system shall provide service analytics: TAT, most common faults, parts consumption, rework | P1 | BO-07 |
| BR-BI-005 | FR | The system shall provide inventory analytics: turnover, dead stock, inter-branch movement, stockout frequency | P1 | BO-03 |
| BR-BI-006 | FR | The system shall provide financial analytics: revenue by service type/brand/branch, profitability, cash flow | P1 | BO-07 |
| BR-BI-007 | FR | The system shall provide a custom report builder with drag-and-drop interface | P1 | BO-07 |
| BR-BI-008 | FR | The system shall support scheduled report generation and email distribution | P1 | BO-07 |
| BR-BI-009 | FR | The system shall export reports to PDF, Excel, and CSV formats | P1 | BO-07 |
| BR-BI-010 | FR | The system shall provide warranty claim analytics: claims by brand, approval rate, aging, revenue realization | P1 | BO-04 |

---

### 8.10 Document Management (DMS)

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-DMS-001 | FR | The system shall store service reports, invoices, contracts, warranty claims, and compliance documents in a centralized repository with version control | P1 | BO-01 |
| BR-DMS-002 | FR | The system shall support electronic signature capture and verification | P1 | BO-01 |
| BR-DMS-003 | FR | The system shall provide configurable document approval workflows | P1 | BO-01 |
| BR-DMS-004 | FR | The system shall generate document templates for: service reports, quotations, invoices, warranty certificates, AMC agreements | P1 | BO-01 |
| BR-DMS-005 | FR | The system shall enforce document retention policies per document type | P2 | BO-10 |

---

### 8.11 Quality Management (QMS)

| Req ID | Type | Requirement | Priority | BO Link |
|---|---|---|---|---|
| BR-QMS-001 | FR | The system shall maintain ISO 9001:2015 compliance documentation with version control | P1 | BO-10 |
| BR-QMS-002 | FR | The system shall manage customer complaints with root cause analysis and CAPA tracking | P1 | BO-05 |
| BR-QMS-003 | FR | The system shall track service quality KPIs: rework rate, complaints, SLA compliance, CSAT | P1 | BO-05 |
| BR-QMS-004 | FR | The system shall support internal audit management with findings and corrective action tracking | P2 | BO-10 |
| BR-QMS-005 | FR | The system shall enforce quality inspection checklists on service completion before closing work orders | P1 | BO-05 |


---

## 9. NON-FUNCTIONAL REQUIREMENTS

| Req ID | Category | Requirement | Priority |
|---|---|---|---|
| NFR-001 | Performance | Page load time ≤ 3 seconds for all ERP screens under normal load | P1 |
| NFR-002 | Performance | API response time ≤ 500ms at 95th percentile | P1 |
| NFR-003 | Performance | System shall support 500+ concurrent internal users without degradation | P1 |
| NFR-004 | Performance | Customer portal shall support 50,000+ concurrent users | P1 |
| NFR-005 | Performance | Standard reports shall generate within 30 seconds | P1 |
| NFR-006 | Availability | System uptime SLA: 99.9% during Bangladesh business hours (9AM–10PM BST) | P1 |
| NFR-007 | Availability | Disaster recovery RTO ≤ 4 hours; RPO ≤ 1 hour | P1 |
| NFR-008 | Availability | Zero-downtime deployment for planned maintenance | P2 |
| NFR-009 | Scalability | Architecture must support 5x user and data volume growth over 5 years without re-architecture | P1 |
| NFR-010 | Scalability | Auto-scaling for traffic spikes (promotional periods, seasonal demand) | P2 |
| NFR-011 | Security | Role-Based Access Control (RBAC) with field-level permission granularity | P1 |
| NFR-012 | Security | Multi-Factor Authentication (MFA) mandatory for all admin and finance users | P1 |
| NFR-013 | Security | AES-256 encryption at rest; TLS 1.2+ in transit | P1 |
| NFR-014 | Security | Complete immutable audit trail for all data changes (who, what, when, before/after) | P1 |
| NFR-015 | Security | Branch-level data isolation (users see only their branch data unless granted wider access) | P1 |
| NFR-016 | Usability | Full Bengali and English language support in UI, notifications, reports, and data entry | P1 |
| NFR-017 | Usability | Technician mobile app optimized for Android 10+ devices with minimum 4G / intermittent connectivity | P1 |
| NFR-018 | Usability | Offline mode with automatic data sync on reconnect for technician mobile app | P1 |
| NFR-019 | Usability | Responsive web design for all portal interfaces (mobile, tablet, desktop) | P1 |
| NFR-020 | Usability | Low-bandwidth mode for field operations in rural Bangladesh (compress data sync, offline-first) | P1 |
| NFR-021 | Compliance | Bangladesh VAT (Mushak) invoice format compliance | P1 |
| NFR-022 | Compliance | Bangladesh NBR income tax computation compliance | P1 |
| NFR-023 | Compliance | Bangladesh ICT Act, 2006 and Digital Security Act, 2018 compliance | P1 |
| NFR-024 | Compliance | ISO 9001:2015 audit trail and documentation requirements | P1 |
| NFR-025 | Compliance | ISO 27001 security controls alignment | P2 |
| NFR-026 | Maintainability | API-first architecture with documented REST APIs for all integrations | P1 |
| NFR-027 | Maintainability | No-code/low-code configuration for workflows, forms, and business rules | P1 |
| NFR-028 | Maintainability | System must support customization without modifying core product code | P1 |
| NFR-029 | Data Integrity | All transactions must be ACID-compliant with full rollback capability | P1 |
| NFR-030 | Data Integrity | Automated daily backups with 30-day retention; weekly backups with 1-year retention | P1 |

---

## 10. BUSINESS RULES

Business rules are constraints the system must enforce derived from 1000FiX's business policies.

### 10.1 Service Order Rules

| Rule ID | Business Rule |
|---|---|
| BRU-SRM-01 | A service order cannot be created for a device unless the device's serial number is registered in the system |
| BRU-SRM-02 | A warranty-type service order can only be created if the device's warranty expiry date is in the future at the time of service request |
| BRU-SRM-03 | An AMC-type service order can only be created if the device is listed in the customer's active AMC contract |
| BRU-SRM-04 | A service order cannot be moved to "Completed" status unless the digital quality checklist is marked as passed |
| BRU-SRM-05 | An invoice cannot be generated for a service order that is not in "Completed" status |
| BRU-SRM-06 | A rework flag must be automatically applied to any new service order for a device that had a closed service order for the same fault category within the preceding 30 days |
| BRU-SRM-07 | Repair cost estimates exceeding BDT 5,000 must be approved by the customer before work can proceed |
| BRU-SRM-08 | Repair cost estimates exceeding BDT 25,000 must receive customer approval AND branch manager approval |
| BRU-SRM-09 | A service order cannot be assigned to a technician who does not hold the required brand certification for warranty work on that brand |
| BRU-SRM-10 | Service orders from Privilege Program members (Gold/Diamond) must automatically receive priority-1 SLA regardless of service type |

### 10.2 Warranty and Contract Rules

| Rule ID | Business Rule |
|---|---|
| BRU-CWM-01 | A warranty claim cannot be submitted to a brand partner without: a completed work order, device serial number, at least one before-photo, technician's diagnosis text, and replaced parts list |
| BRU-CWM-02 | A warranty claim must be auto-created and queued for submission within 24 hours of a warranty service order being closed |
| BRU-CWM-03 | An AMC contract cannot be created without: at least one device listed, at least one service type defined, valid billing frequency, and management approval |
| BRU-CWM-04 | When an AMC contract expires, all open scheduled maintenance work orders linked to that contract must automatically be cancelled and the customer notified |
| BRU-CWM-05 | The system must prevent duplicate warranty claims for the same serial number and fault within a 90-day window |
| BRU-CWM-06 | Privilege Program discounts apply only to labor charges and not to parts, consumables, or transportation charges |
| BRU-CWM-07 | RAMC package pricing must be calculated based on the number and type of appliances registered, not a flat fee |

### 10.3 Inventory Rules

| Rule ID | Business Rule |
|---|---|
| BRU-INV-01 | Parts cannot be issued from inventory against a service order that has not been approved for repair by the customer (for paid repairs) |
| BRU-INV-02 | An inter-branch transfer cannot be executed without originating branch manager approval AND destination branch manager acknowledgment |
| BRU-INV-03 | Van stock replenishment to a technician cannot exceed the pre-configured maximum van stock level per item |
| BRU-INV-04 | A purchase order cannot be raised for an item if the combined stock across all locations exceeds the maximum stock level |
| BRU-INV-05 | Warranty parts (brand-provided) must be tracked separately from commercial stock and cannot be used for out-of-warranty repairs |

### 10.4 Financial Rules

| Rule ID | Business Rule |
|---|---|
| BRU-FIN-01 | All customer invoices must include Bangladesh VAT at the applicable rate and display the 1000FiX VAT registration number |
| BRU-FIN-02 | Cash payments exceeding BDT 50,000 must record the customer's National ID (NID) number per NBR guidelines |
| BRU-FIN-03 | A payment cannot be recorded against a cancelled invoice |
| BRU-FIN-04 | A credit note cannot be issued without approval from the Finance Manager |
| BRU-FIN-05 | Financial period cannot be closed if there are unposted journal entries in that period |
| BRU-FIN-06 | A vendor invoice cannot be approved for payment without a corresponding approved GRN in the system |
| BRU-FIN-07 | Warranty claim invoices to brand partners must be generated in USD equivalent at the prevailing exchange rate on the date of service completion |

### 10.5 HR Rules

| Rule ID | Business Rule |
|---|---|
| BRU-HRM-01 | A technician cannot be assigned to brand warranty work for which their certification has expired |
| BRU-HRM-02 | Overtime must be pre-approved by the line manager before it can be recorded for payroll calculation |
| BRU-HRM-03 | Performance incentive must be calculated only after minimum monthly job completion threshold is met (configurable per tier) |
| BRU-HRM-04 | Annual leave cannot be approved if team coverage threshold would fall below the configured level |
| BRU-HRM-05 | Payroll cannot be finalized for a period if attendance records for that period have not been verified and locked |

### 10.6 Portal and Access Rules

| Rule ID | Business Rule |
|---|---|
| BRU-PRT-01 | A customer can only view service orders, invoices, and device records associated with their registered account |
| BRU-PRT-02 | A field technician can only access the customer profile and device history for service orders currently assigned to them |
| BRU-PRT-03 | Corporate B2B portal users can only view and manage records associated with their registered corporate account |
| BRU-PRT-04 | A branch manager can only access financial, inventory, and HR data for their own branch(es) unless granted wider access by a system administrator |
| BRU-PRT-05 | Admin portal access must require MFA at every login |

---

## 11. DATA REQUIREMENTS

### 11.1 Key Data Entities

| Entity | Description | Key Attributes |
|---|---|---|
| Customer | Individual or corporate client | CustomerID, Name, Type, Phone, Email, NID, Address(es), Tier |
| Device | Product registered to a customer | DeviceID, CustomerID, Brand, Model, SerialNumber, PurchaseDate, WarrantyExpiry |
| Service Order | Customer's request for service | ServiceOrderID, CustomerID, DeviceID, Type, Channel, Status, Priority, BranchID |
| Work Order | Internal task assigned to technician | WorkOrderID, ServiceOrderID, TechnicianID, ScheduledDate, Status, LaborTime |
| Technician | Field or service center engineer | TechnicianID, EmployeeID, Skills, Certifications, Zone, VanInventory |
| Inventory Item | Spare part or consumable | ItemID, PartNumber, Description, Brand, Model, UOM, Category, StockLevels |
| Stock Location | Warehouse, service center, or van | LocationID, Type, BranchID, Address, ManagerID |
| Contract | AMC, RAMC, or corporate agreement | ContractID, CustomerID, Type, StartDate, EndDate, Devices, Terms, BillingCycle |
| Warranty Claim | Claim to brand partner | ClaimID, ServiceOrderID, BrandID, SubmissionDate, Status, ReimbursementAmount |
| Invoice | Financial bill | InvoiceID, ServiceOrderID, CustomerID, LineItems, TaxAmount, TotalAmount |
| Payment | Payment received | PaymentID, InvoiceID, Method, Amount, Date, Reference |
| Vendor | Supplier of spare parts | VendorID, Name, Type, ContactInfo, TaxID, PaymentTerms |
| Employee | All staff members | EmployeeID, Name, Department, Role, JoinDate, Salary, Skills, Attendance |
| Branch | Service center location | BranchID, Name, Address, Division, Manager, OperatingHours, ServiceTypes |

### 11.2 Entity Relationship Summary

```
Customer (1) ──── (N) Device
Customer (1) ──── (N) ServiceOrder
ServiceOrder (1) ── (N) WorkOrder
WorkOrder (N) ───── (1) Technician
WorkOrder (1) ──── (N) PartUsage ── (N) InventoryItem ── (1) StockLocation
Customer (1) ──── (N) Contract
Contract (1) ──── (N) WorkOrder [AMC type]
ServiceOrder (1) ── (1) WarrantyClaim [warranty type]
ServiceOrder (1) ── (1) Invoice ── (N) Payment
Employee (N) ────── (1) Branch
```

### 11.3 Data Migration Plan

| Source | Data Type | Estimated Volume | Format | Priority |
|---|---|---|---|---|
| Existing customer records | Customer master | 100,000+ | Spreadsheet | P1 |
| Device registry | Customer devices | 200,000+ | Spreadsheet | P1 |
| Service history | Past service orders | 500,000+ | Spreadsheet/paper | P1 |
| Financial records | Invoices, payments (3 years) | 1,000,000+ | Accounting export | P1 |
| Inventory data | Current stock all locations | 10,000+ SKUs x 51 locations | Spreadsheet | P1 |
| Employee records | All HR data | 500+ | Spreadsheet/paper | P1 |
| Vendor master | Supplier info | 200+ | Spreadsheet | P1 |
| Active contracts | AMC/RAMC/Corporate | 5,000+ | Spreadsheet | P1 |
| Document archive | Service reports, warranty docs | TBD | PDF/paper scans | P2 |

**Migration Phases:** Data profiling → Cleansing → Mapping → Trial migration → UAT → Final cutover → Validation sign-off

### 11.4 Data Retention Policy

| Data Type | Retention Period | Basis |
|---|---|---|
| Customer records | 7 years after last transaction | Bangladesh business law |
| Financial transactions | 7 years | Bangladesh Companies Act / NBR |
| Service records | 5 years | Operational and warranty purposes |
| Warranty claims | 7 years | Brand partner audit requirements |
| Employee records | 10 years after termination | Bangladesh Labour Act |
| Audit logs | 5 years | ICT Act / ISO 27001 |

---

## 12. BUSINESS PROCESS FLOWS

### Process 1: Multi-Channel Service Request to Completion

**Actors**: Customer, Call Center Agent, System, Dispatcher, Technician, Billing Staff

**Flow:**

```
CUSTOMER          SYSTEM             DISPATCHER        TECHNICIAN
    |                 |                   |                 |
Contact 1000FiX ───> Create SR            |                 |
(portal/phone/       Assign order#        |                 |
 WhatsApp/walk-in)   Check warranty/AMC   |                 |
    |                 |                   |                 |
<── Acknowledge SMS   |                   |                 |
    (order# + link)   |──────────────────>AI dispatch ────>|
    |                 |                   (skills+zone)     |
<── Dispatched SMS    |                   |                 Accept job
    |                 |                   |                 Navigate (GPS)
<── En Route SMS      |                   |                 |
    |                 |                   |         Check in at site
    |                 |                   |                 Diagnose
    |                 |                   |                 Scan parts
<── Approve quote     |                   |        (if out-of-warranty)
 ──> Approve ─────────>                   |                 Execute repair
    |                 |                   |                 QC checklist
<── Sign (e-sig)      |                   |       Work order closed
    |                 |                   |                 |
<── Invoice + payment |<──── Auto-post GL  |                 |
    link (auto)       |                   |                 |
Pay via bKash/card ──>|                   |                 |
<── CSAT survey       |                   |                 |
```

**Decision Points:**
- Warranty active → Warranty type order (no charge to customer; brand claim)
- AMC active → AMC type order
- Estimate > BDT 5,000 → Customer quotation approval required
- No technician → SLA countdown; alert at 75%

---

### Process 2: Warranty Claim Processing

```
WORK ORDER CLOSED (warranty)
         |
System auto-creates Warranty Claim
Attaches: photos, diagnosis, parts, serial#
         |
Finance reviews within 24 hours
         |
[Complete] → Approve for submission
         |
Submit to brand partner portal/email
         |
Brand partner responds:
  [Approved] → Billing queue → Match payment → Close claim → Post GL
  [Rejected] → Alert finance + reason → Dispute resolution task
  [More info] → Upload supplementary docs → Re-submit
```

---

### Process 3: Inventory Replenishment

```
ERP monitors stock levels continuously
         |
[Stock falls below Reorder Point]
         |
Auto-generate Replenishment Alert + Reorder Qty
Alert → Warehouse Manager
         |
Manager reviews → Confirms → Selects vendor
         |
PO auto-generated → Sent to vendor
         |
Goods arrive → GRN created → Quality check
         |
[Pass] → Stock updated → Alert cleared
[Fail] → Quarantine → Vendor notified
         |
3-way match: PO + GRN + Invoice → AP payment queue
```

---

### Process 4: AMC Contract Lifecycle

```
Sales identifies lead → Creates proposal → Customer signs
         |
System: Create AMC contract
Define: devices, coverage, schedule, SLA, billing
         |
Contract ACTIVE → Invoice generated → Customer pays
         |
[Scheduled maintenance due]
Auto-create work order → Dispatch technician → Execute PM → Close WO
Track utilization: visits used / parts consumed
         |
[60 days before expiry]
Renewal alert → SMS to customer + task to account manager
         |
[Customer renews] → New contract → Old contract archived
[Customer declines] → Contract expires → Standard billing resumes
```

---

### Process 5: Invoice-to-Cash

```
Work order closed → Auto-generate invoice (labor + parts + VAT)
         |
[Privilege member] → Apply 50% labor discount automatically
         |
Generate Mushak VAT invoice
         |
Send to customer: SMS + WhatsApp + portal (with bKash/Nagad/card link)
         |
Customer pays → Payment gateway confirmation
         |
Auto-match payment → Mark invoice Paid → Post AR cleared to GL
         |
[Unpaid 7 days] → Auto-reminder #1
[Unpaid 14 days] → Auto-reminder #2
[Unpaid 21 days] → Collections queue
```

---

### Process 6: Field Technician Daily Workflow

```
START OF DAY: Open mobile app → View optimized job queue

FOR EACH JOB:
  1. Tap job → Review customer/device/complaint/history
  2. Navigate (Google Maps GPS)
  3. Arrive → Tap "Arrived" (auto-timestamp)
  4. Complete diagnostic checklist on mobile
  5. Check van stock:
     - Available → Scan barcode to reserve
     - Not in van → Request from nearest branch
  6. Execute repair → Track time on job
  7. Complete QC checklist
  8. Capture before/after photos
  9. Customer e-signs on screen
  10. Tap "Complete Job" → Invoice auto-generated → Payment link sent
  11. Move to next job

END OF DAY: All data synced to ERP → Van stock reconciled → Metrics updated
```

---

### Process 7: Inter-Branch Stock Transfer

```
Requesting branch: Check all-location stock view → Identify surplus at another branch
         |
Submit inter-branch transfer request → System notifies supplying branch manager
         |
Supplying branch manager approves
         |
System creates transfer order → Reserves stock at source
Items picked, packed, dispatched
         |
Destination receives → Scans items → Confirms receipt
         |
Source stock reduced → Destination stock increased → Transfer order closed
```

---

### Process 8: Technician Performance Management

```
Daily: Work orders assigned → Technician executes → Data captured in real time
         |
System calculates per technician:
- Jobs completed (vs. target)
- First-time fix rate
- Average TAT
- Customer CSAT ratings
- Rework rate
- Travel efficiency
         |
Weekly: Performance dashboard visible to technician + manager
         |
Monthly: Incentive calculated (base threshold met + performance score)
         |
Payroll: Performance incentive included in payroll run
         |
Annual: KPIs feed into performance review and career development
```

---

### Process 9: Corporate B2B Service Workflow

```
Corporate admin logs into B2B portal
         |
Option A: Single service request (one device)
Option B: Bulk upload (CSV with device list)
         |
System validates devices against active AMC coverage
         |
Service orders created → Grouped under corporate job batch
         |
Service coordinator assigns technician(s) for site visit
         |
Services executed → Work orders closed → SLA tracked per device
         |
Consolidated invoice generated per billing cycle
         |
Corporate admin reviews on B2B portal → Approves for payment
         |
Payment received → Posted to corporate account
```

---

### Process 10: Monthly Financial Close

```
Day 1-3: Finance runs bank reconciliation (automated statement matching)
Day 3-4: Review unmatched items → Resolve manually
Day 4: Finance reviews AP/AR aging → Posts accruals
Day 4-5: Finance generates draft P&L (branch + consolidated)
Day 5: CFO reviews and approves
Day 5: System locks the period → Reports distributed to management
(Previously: 15-20 days → Target: ≤ 5 days)
```

---

## 13. USE CASES

### UC-001: Log Service Request (Multi-Channel)

**Actors**: Customer / Call Center Agent; ERP System
**Preconditions**: Customer can be found or created; system operational
**Trigger**: Customer contacts 1000FiX via any channel

**Main Flow:**
1. Customer contacts 1000FiX (phone, walk-in, portal, WhatsApp, chatbot)
2. Agent or self-service form collects: device brand/model/serial, complaint, preferred service type, preferred date/time
3. System searches for existing customer record — found: pre-populates; not found: agent creates new account
4. System checks device warranty by serial number + purchase date
5. System classifies order: Warranty / AMC / Paid
6. System generates unique service order number
7. Acknowledgment SMS sent to customer with order number and tracking link
8. Service order appears in dispatch queue

**Alternative Flows:**
- A1 — Device not registered: Agent registers device, then creates order
- A2 — Walk-in no appointment: Service order with "Walk-In" channel; assigned to service center queue
- A3 — Warranty expired: System notifies; order type converted to Out-of-Warranty

**Postconditions**: Order in "Open" status; customer notified; order in dispatch queue

---

### UC-002: Assign Work Order to Technician

**Actors**: Dispatcher; ERP System
**Preconditions**: Service order in "Open" status; technicians available
**Trigger**: Dispatcher reviews open queue

**Main Flow:**
1. Dispatcher opens open service order queue (sorted by SLA priority)
2. Opens service order; views AI-recommended technicians with match scores
3. Accepts recommendation or manually selects technician
4. System validates: certification match, no scheduling conflict
5. Dispatcher confirms; system creates work order, status → "Assigned"
6. Technician receives push notification + SMS with job details
7. System updates technician's daily schedule with route optimization

**Alternative Flows:**
- A1 — No technician available: Order queued; SLA countdown; manager alerted at 75%
- A2 — Emergency insertion: System re-optimizes existing schedule; technician notified of change

**Postconditions**: Work order "Assigned"; technician notified; live on dispatch map

---

### UC-003: Technician Executes Field Job (Mobile)

**Actors**: Field Technician; Mobile App; Customer
**Preconditions**: Work order assigned; mobile app installed and logged in
**Trigger**: Technician starts work day or receives job notification

**Main Flow:**
1. Opens mobile app; views optimized job queue
2. Taps job; reviews customer, device, complaint, and history
3. Taps "Navigate" — Google Maps opens with directions
4. Arrives; taps "Arrived" — timestamp and GPS recorded; customer notified
5. Photographs device (before-repair)
6. Completes diagnostic checklist; records findings
7. Checks van stock (barcode scan); if part missing → raises parts request
8. Executes repair; tracks time on job
9. Completes QC checklist; confirms repair successful
10. Photographs completed repair (after-repair)
11. Customer signs on screen (e-signature)
12. Taps "Complete Job" — invoice auto-generated; payment link sent to customer
13. App syncs data to ERP

**Alternative Flows:**
- A1 — Offline: All data stored locally; auto-syncs on reconnect
- A2 — Cannot fix: Marks "Parts Pending" or "Escalation"; dispatcher notified
- A3 — Customer absent: Marks "Customer Absent"; reschedule workflow triggered

**Postconditions**: Work order "Completed"; inventory deducted; invoice created; performance metrics updated

---

### UC-004: Customer Tracks Service Status

**Actors**: Customer; Customer Portal
**Preconditions**: Active service order; customer has tracking link or account
**Trigger**: Customer clicks tracking link in SMS or logs into portal

**Main Flow:**
1. Customer opens tracking link or portal
2. Portal shows visual status timeline: Received → Assigned → En Route → In Progress → Completed → Invoice Sent
3. Current step highlighted; ETA displayed
4. If technician en route: live map shows technician location
5. Customer can view technician name and photo

**Postconditions**: Customer informed without calling hotline; hotline load reduced

---

### UC-005: Process Warranty Claim

**Actors**: ERP System (auto); Finance/Warranty Staff; Brand Partner
**Preconditions**: Warranty service order closed; documentation attached
**Trigger**: Warranty work order status changes to "Completed"

**Main Flow:**
1. System auto-creates warranty claim from closed work order (includes photos, diagnosis, parts, serial number)
2. Claim enters "Pending Finance Review" queue
3. Finance staff reviews and approves within 24 hours
4. System generates claim in brand partner's required format; submits
5. Brand partner responds: Approved / Rejected / More Info Required
6. If approved: payment matched to claim; posted to GL; claim closed
7. If rejected: finance alerted with reason; dispute task created

**Postconditions**: Warranty revenue recovered; GL updated; brand payment reconciled

---

### UC-006: Generate Invoice and Collect Payment

**Actors**: ERP System (auto); Customer; Finance Staff
**Preconditions**: Paid service order "Completed"
**Trigger**: Work order closed by technician

**Main Flow:**
1. System auto-generates invoice: labor + parts + VAT
2. Privilege Program discount applied automatically (50% on labor if applicable)
3. Mushak VAT invoice generated per NBR format
4. Invoice sent: email + WhatsApp + portal with bKash/Nagad/card payment link
5. Customer pays; payment gateway confirms
6. System auto-matches payment to invoice; marks "Paid"; posts to GL
7. Service order → "Closed"; CSAT survey triggered

**Alternative Flows:**
- A1 — Cash payment at service center: Staff records cash; system matches
- A2 — Corporate client: Invoice added to monthly statement

**Postconditions**: Invoice paid; AR cleared; GL updated; order closed

---

### UC-007: AMC Contract Renewal

**Actors**: ERP System (alerts); Account Manager; Customer
**Preconditions**: Active AMC within 60 days of expiry
**Trigger**: System detects contract expiry date within 60 days

**Main Flow:**
1. System sends automated renewal reminder to customer at 60 days
2. Account manager assigned renewal task with customer details
3. Manager contacts customer; creates renewal quotation
4. Customer approves; new contract created in ERP
5. Renewal invoice generated; customer pays; contract activated
6. Old contract archived; CRM updated

**Alternative Flows:**
- A1 — Customer declines: Contract marked "Expired"; scheduled work orders cancelled; standard billing
- A2 — No action at 15 days: Escalation to sales manager

**Postconditions**: Contract renewed or expired; revenue outcome tracked

---

### UC-008: Inventory Replenishment

**Actors**: ERP System; Warehouse Manager; Vendor
**Preconditions**: Reorder point configured for item
**Trigger**: Stock falls below reorder point

**Main Flow:**
1. System detects stock at or below reorder point
2. Calculates reorder quantity based on demand history and lead time
3. Alert sent to warehouse manager
4. Manager confirms quantity and vendor; PO generated and sent
5. Vendor acknowledges; goods delivered; GRN created; quality check performed
6. Items stocked; stock levels updated; alert cleared
7. 3-way match executed; vendor invoice routed to AP

**Postconditions**: Stock replenished; PO closed; vendor invoice in AP queue

---

### UC-009: Generate Branch Performance Report

**Actors**: Branch/Regional Manager; System
**Preconditions**: System has data for requested period
**Trigger**: Manager selects report from BI dashboard

**Main Flow:**
1. Manager opens BI dashboard; selects Branch Performance report
2. Sets filters: branch(es), date range, service type
3. System generates report: orders, TAT, SLA compliance, revenue, cost, technician utilization, CSAT
4. Manager drills down on underperforming metric
5. Compares to prior period and benchmark
6. Exports to PDF for board presentation

**Postconditions**: Data accessed in < 30 seconds; report exported

---

### UC-010: Privilege Program Enrollment

**Actors**: Customer; Customer Service Agent / Customer Portal
**Preconditions**: Customer has an account
**Trigger**: Customer requests enrollment

**Main Flow:**
1. Customer or agent selects Privilege Program enrollment
2. System shows Silver/Gold/Diamond tiers with benefits and pricing
3. Customer selects tier; system generates invoice
4. Customer pays; system activates membership; updates CRM tier
5. 50% labor discount applied to all future service invoices automatically
6. Renewal reminder scheduled for 30 days before expiry

**Postconditions**: Customer enrolled; tier applied; renewal reminder set

---

### UC-011: Corporate Bulk Service Request

**Actors**: Corporate Admin; B2B Portal; Service Operations
**Preconditions**: Corporate account active with AMC
**Trigger**: Corporate client has multiple devices requiring service

**Main Flow:**
1. Corporate admin uploads CSV of device serial numbers + locations + issues
2. System validates devices against active AMC coverage
3. Service orders created; grouped under corporate job batch
4. Coordinator assigns technician(s) for site visit
5. Services executed; all work orders closed
6. Consolidated invoice generated per billing cycle; corporate admin reviews on B2B portal

**Postconditions**: All orders created; corporate billed on schedule; SLA tracked per device

---

### UC-012 to UC-020 (Summary)

| UC | Title | Key Actor | Key Outcome |
|---|---|---|---|
| UC-012 | Purchase Warranty Extension | Customer | Extension activated; device record updated |
| UC-013 | Technician Van Stock Reconciliation | Technician + Warehouse | Discrepancies identified and resolved daily |
| UC-014 | Leave Request and Approval | Employee + HR Manager | Leave approved/rejected; calendar updated; payroll impacted |
| UC-015 | Monthly Payroll Run | HR + Finance Manager | Payroll processed; bank file generated; payslips distributed |
| UC-016 | ISO Internal Audit Logging | Quality Manager | Findings recorded; CAPAs created and tracked |
| UC-017 | Customer Complaint Resolution | Customer + Service Manager | Complaint resolved; root cause recorded; QC dashboard updated |
| UC-018 | New Vendor Onboarding | Procurement + Finance | Vendor activated in master; POs can be raised |
| UC-019 | Financial Period Closing | Finance + CFO | Period locked; reports distributed; GL accurate |
| UC-020 | Emergency After-Hours Service | Customer + On-Call Technician | Emergency order created; on-call technician dispatched; premium applied |

---

## 14. INTEGRATION REQUIREMENTS

### 14.1 Integration Architecture

```
+─────────────────────────────────────────────────+
|              1000FiX ERP CORE                    |
|  Service | Finance | HR | Inventory | Contracts   |
+──────────────────┬──────────────────────────────+
                   | REST API / Webhooks
+──────────────────┴──────────────────────────────+
|        1000FiX WEB PLATFORM                      |
|  Next.js 15 + Payload CMS 3 + PostgreSQL 16      |
|  Customer Portal | Admin | B2B | Technician App   |
+──────┬──────┬────┬──────┬────────────────────────+
       |      |    |      |
    bKash  Nagad  SMS  WhatsApp  Google Maps  Firebase
```

### 14.2 Integration Catalog

| # | System | Direction | Data Exchanged | Priority |
|---|---|---|---|---|
| INT-01 | 1000FiX Web Platform (Next.js 15) | Bidirectional REST + Webhooks | Service orders, customers, availability, location, invoices | P1 |
| INT-02 | bKash Payment Gateway | Bidirectional | Payment links, payment confirmations | P1 |
| INT-03 | Nagad Payment Gateway | Bidirectional | Payment links, payment confirmations | P1 |
| INT-04 | SSLCOMMERZ | Bidirectional | Card payment processing | P1 |
| INT-05 | Bangladesh SMS Gateway | Outbound | Transactional SMS (status, OTP, reminders) | P1 |
| INT-06 | WhatsApp Business API | Bidirectional | Notifications, invoice sharing, chatbot handoff | P1 |
| INT-07 | Google Maps Platform | Outbound | Geocoding, GPS tracking, route optimization | P1 |
| INT-08 | Firebase Cloud Messaging | Outbound | Push notifications to mobile app | P1 |
| INT-09 | Rasa 3.6 Bengali Chatbot | Bidirectional | Customer intent, service order creation | P2 |
| INT-10 | Timefold Optimization Engine | Bidirectional | Job schedule, route optimization | P2 |
| INT-11 | Biometric Attendance Devices | Inbound (file/SDK) | Clock-in/out timestamps | P2 |
| INT-12 | Cloudinary / Cloud Storage | Bidirectional | Photo/document upload and retrieval | P1 |
| INT-13 | Email Service (SendGrid/SES) | Outbound | Invoices, notifications, system emails | P1 |
| INT-14 | Metabase BI | Bidirectional | Analytics data, embedded dashboards | P2 |
| INT-15 | Bangladesh Bank (BEFTN) | Outbound (file) | Monthly payroll salary transfer file | P1 |

### 14.3 Minimum Web Platform API Endpoints

| Endpoint | Direction | Purpose |
|---|---|---|
| POST /api/service-orders | ERP receives from Web | Create order from web booking |
| GET /api/service-orders/{id}/status | Web calls ERP | Real-time status for tracking page |
| GET /api/technicians/{id}/location | Web calls ERP | Live GPS for customer tracking map |
| GET /api/slots/availability | Web calls ERP | Booking availability for scheduling |
| POST /api/customers/sync | Bidirectional | Sync customer registration |
| POST /api/payments/confirm | ERP receives | Payment gateway confirmation |
| GET /api/invoices/{id} | Web calls ERP | Invoice data for portal display |
| GET /api/contracts/{customerId} | Web calls ERP | Active contracts for portal display |
| Webhook: service_order.status_changed | ERP pushes to Web | Trigger customer notifications |
| Webhook: technician.dispatched | ERP pushes to Web | Enable live tracking |

---

## 15. ASSUMPTIONS

| ID | Assumption |
|---|---|
| ASM-01 | All service center locations have at least 3G mobile internet connectivity during operating hours |
| ASM-02 | Field technicians own or will be issued Android smartphones (Android 10+) |
| ASM-03 | Existing customer data can be exported from spreadsheets with minimum 80% data quality |
| ASM-04 | Brand partners will continue authorized service relationships during the project |
| ASM-05 | Bangladesh VAT rates and Mushak invoice format remain stable during implementation |
| ASM-06 | Management will allocate minimum 20% of key stakeholder time for the ERP project |
| ASM-07 | Selected ERP vendor has prior Bangladesh localization experience (VAT, payroll, Bengali) |
| ASM-08 | The 1000FiX web platform will expose well-documented REST APIs for integration |
| ASM-09 | bKash, Nagad, and SSLCOMMERZ will provide sandbox environments and technical support |
| ASM-10 | No major organizational restructuring will occur during the 18-month implementation |
| ASM-11 | Biometric attendance devices will be procured and installed before HR module go-live |
| ASM-12 | Historical financial data is available in structured format for at least 3 years |
| ASM-13 | ERP will be hosted in a cloud region with low latency to Bangladesh (Singapore preferred) |
| ASM-14 | Power backup (UPS/generator) exists at primary service centers |
| ASM-15 | Management will provide dedicated super-users from each department for UAT |
| ASM-16 | Project will not go live during Eid-ul-Fitr or Eid-ul-Adha peak periods |
| ASM-17 | Third-party API costs (Google Maps, WhatsApp Business, SMS) are within budget |
| ASM-18 | Brand partner warranty claim processes can be mapped to the ERP warranty claim workflow |
| ASM-19 | All technicians can read Bengali-language mobile app interfaces |
| ASM-20 | Internet connectivity issues during service execution are handled by the app's offline mode |

---

## 16. CONSTRAINTS

| ID | Constraint | Type | Impact |
|---|---|---|---|
| CON-01 | Total 3-year budget ceiling: USD $350,000 | Budget | Restricts custom development scope |
| CON-02 | Full system go-live within 18 months of project kickoff | Schedule | Requires phased approach and strict scope management |
| CON-03 | ERP must integrate with Next.js 15 / Payload CMS 3 web platform; platform cannot be replaced | Technical | Integration complexity; API contract alignment required |
| CON-04 | All financial transactions must comply with Bangladesh NBR VAT and income tax regulations | Regulatory | Vendor must have Bangladesh tax compliance out-of-the-box |
| CON-05 | System must support Bengali as primary language for field technician interfaces | Technical | Unicode Bengali rendering required |
| CON-06 | Customer portals must accept bKash and Nagad as primary payment methods | Technical | Bangladesh-specific payment gateway integration required |
| CON-07 | Mobile app must function offline in field conditions | Technical | Offline-first architecture mandatory |
| CON-08 | System cannot go live during Ramadan, Eid-ul-Fitr, or Eid-ul-Adha | Operational | Project plan must account for Bangladesh holiday schedule |
| CON-09 | Data must be hosted in South/Southeast Asia region (Singapore/India preferred) | Technical | Cloud provider region constrained |
| CON-10 | Existing employees cannot be displaced without management approval | Organizational | Automation augments roles; no unilateral headcount reduction |
| CON-11 | 1000FiX brand identity must be applied consistently across all portals | Design | White-labeling of portal suite required |

---

## 17. DEPENDENCIES

### 17.1 Internal Dependencies

| ID | Dependency | Owner | Impact if Not Met |
|---|---|---|---|
| DEP-01 | IT team finalizes web platform APIs before ERP integration development | CTO | Integration timeline delayed |
| DEP-02 | Finance completes chart of accounts restructuring before financial module config | CFO | Financial setup delayed |
| DEP-03 | HR provides finalized payroll structure before HR module configuration | HR Director | Payroll setup delayed |
| DEP-04 | Biometric hardware procured and installed before Phase 5 | IT Admin | GPS fallback used |
| DEP-05 | Historical data cleaned and formatted before Phase 1 go-live | All departments | Migration delayed |
| DEP-06 | 3+ super-users/champions authorized before UAT | Department heads | UAT coverage insufficient |
| DEP-07 | Bangladesh bank BEFTN format confirmed with banking partner | Finance | Payroll file format may need rework |

### 17.2 External Dependencies

| ID | Dependency | External Party | Impact if Not Met |
|---|---|---|---|
| DEP-08 | bKash API sandbox and production access | bKash | Portal payments unavailable |
| DEP-09 | Nagad API access | Nagad | Payments limited |
| DEP-10 | SSLCOMMERZ card payment integration | SSLCOMMERZ | Card payment unavailable |
| DEP-11 | Google Maps Platform API key | Google | GPS tracking and routing disabled |
| DEP-12 | WhatsApp Business API access (Meta approved) | Meta / WhatsApp BSP | WhatsApp notifications disabled |
| DEP-13 | Bangladesh SMS gateway onboarding | SMS provider | Notifications limited to app push only |
| DEP-14 | Brand partner warranty claim format specifications | Dell, HP, Samsung, etc. | Warranty claim automation delayed |
| DEP-15 | ERP vendor contract finalized | Selected ERP Vendor | All timelines shift |

---

## 18. RISK REGISTER

| Risk ID | Risk Description | Category | Probability | Impact | Score | Mitigation | Contingency |
|---|---|---|---|---|---|---|---|
| RSK-01 | Budget overrun due to scope creep | Budget | Medium | High | High | Change control; all additions require CEO + budget approval | Defer P3 features |
| RSK-02 | Timeline delay beyond 18 months | Schedule | Medium | High | High | Phase milestones; weekly tracking; early escalation | Extend Phase 5-6 scope |
| RSK-03 | Low technician mobile app adoption | Change Mgmt | High | Critical | Critical | Bengali UI; simple UX; field pilot with champions; gamification | Lite version; extended on-site support |
| RSK-04 | Data migration quality issues | Data | Medium | High | High | Data profiling; trial migration; 2-week parallel run | Manual validation for top 1,000 customers |
| RSK-05 | Vendor delivery failure | Vendor | Low | Very High | High | Milestone payments; penalty clauses; source code escrow | Backup vendor shortlist; termination provisions |
| RSK-06 | Web platform API compatibility breaks | Technical | Medium | High | High | Agreed API contract with versioning | API versioning fallback; temporary manual sync |
| RSK-07 | Bangladesh internet instability in field | Technical | High | Medium | High | Offline-first architecture | Expanded offline cache |
| RSK-08 | Brand partner claim format changes | External | Low | Medium | Medium | Configurable claim templates; quarterly brand review | Manual claim override |
| RSK-09 | Bangladesh VAT/tax regulation change | Regulatory | Low | High | Medium | Monitor NBR announcements; vendor must commit to update SLA | Manual override during transition |
| RSK-10 | Key business champion leaves | Organizational | Medium | High | High | Knowledge transfer docs; train 2 super-users per module | Re-assign project sponsor role |
| RSK-11 | System performance inadequate for 51+ branches | Technical | Low | Very High | High | Load testing before go-live; performance SLA in contract | Phased regional rollout |
| RSK-12 | Customer data privacy breach | Security | Low | Very High | High | ISO 27001 controls; pen testing; field-level access | Incident response plan |
| RSK-13 | Staff resistance to change | Change Mgmt | Medium | High | High | Executive sponsorship; early wins communicated; involve resistors in UAT | Additional change management workshops |
| RSK-14 | bKash/Nagad API downtime | External | Medium | Medium | Medium | Multiple payment methods; graceful degradation | SMS retry; alternative payment method |
| RSK-15 | Data duplication during parallel run | Technical | High | Medium | High | Strict parallel-run rules; daily data reconciliation | Extended parallel run window |

---

## 19. COST-BENEFIT ANALYSIS AND ROI

### 19.1 Investment Summary (3-Year TCO)

| Category | Year 1 | Year 2 | Year 3 | 3-Year Total |
|---|---|---|---|---|
| Software Licensing | $25,000–$50,000 | $10,000–$20,000 | $10,000–$20,000 | $45,000–$90,000 |
| Implementation Services | $60,000–$150,000 | — | — | $60,000–$150,000 |
| Training | $8,000–$15,000 | $2,000–$5,000 | — | $10,000–$20,000 |
| Infrastructure/Hosting | $8,000–$18,000 | $6,000–$16,000 | $6,000–$16,000 | $20,000–$50,000 |
| Support and Maintenance | $3,000–$10,000 | $6,000–$15,000 | $6,000–$15,000 | $15,000–$40,000 |
| **TOTAL** | **$104,000–$243,000** | **$24,000–$56,000** | **$22,000–$51,000** | **$150,000–$350,000** |

### 19.2 Quantified Annual Benefits

| Benefit Area | Conservative | Base Case | Optimistic |
|---|---|---|---|
| Warranty revenue recovery (15-20% currently unclaimed) | BDT 60 lac | BDT 100 lac | BDT 140 lac |
| Technician productivity gain (60% more jobs, same headcount) | BDT 50 lac | BDT 90 lac | BDT 130 lac |
| Inventory cost reduction (overstock + stockout losses -50%) | BDT 12 lac | BDT 20 lac | BDT 30 lac |
| Administrative labor savings (40% reduction in back-office hours) | BDT 20 lac | BDT 35 lac | BDT 50 lac |
| Customer retention improvement (churn 15% to 8%) | BDT 30 lac | BDT 55 lac | BDT 80 lac |
| AMC renewal rate 60% to 85% | BDT 30 lac | BDT 50 lac | BDT 70 lac |
| Financial close efficiency and cash flow | BDT 10 lac | BDT 18 lac | BDT 25 lac |
| **Total Annual Benefit (BDT)** | **212 lac** | **368 lac** | **525 lac** |
| **Total Annual Benefit (USD at ~110 BDT)** | **~$193K** | **~$335K** | **~$477K** |

### 19.3 ROI Summary

| Scenario | 3-Year Benefit | 3-Year Cost | Net Benefit | ROI | Payback |
|---|---|---|---|---|---|
| Conservative | $579K | $350K | $229K | 65% | 22 months |
| Base Case | $1.0M | $250K | $750K | 300% | 14 months |
| Optimistic | $1.43M | $150K | $1.28M | 853% | 10 months |

**Base case payback period: approximately 14 months post full go-live.**

---

## 20. ACCEPTANCE CRITERIA AND KPIs

### 20.1 Phase-Level Acceptance Criteria

**Phase 1 (Month 4):**
- Service orders created from all 5 channels
- Full service order lifecycle functional
- Customer SMS at each milestone
- Basic inventory at Dhaka HQ
- All customer and device records migrated

**Phase 2 (Month 7):**
- Technician mobile app functional with offline mode tested
- GPS tracking live for all Dhaka field technicians
- Route optimization reducing travel time by 15%+
- Digital forms replacing paper for Dhaka operations

**Phase 3 (Month 10):**
- 100% invoices auto-generated from closed work orders
- bKash and Nagad payments functional and auto-matched
- Bangladesh Mushak VAT invoices generated correctly
- Branch P&L available within 5 days of period end

**Phase 4 (Month 13):**
- AMC/RAMC management fully operational
- Warranty claims auto-created within 24 hours
- Warranty claim submission tracked end-to-end
- 10+ corporate clients on B2B portal

**Phase 5 (Month 16):**
- First payroll run fully processed and validated
- Full BI dashboard for all management roles
- All 51+ service centers live

**Phase 6 Full Go-Live (Month 18):**
- All modules operational across all locations
- All portal integrations functional
- 99.9% uptime over 30-day period
- 85%+ of target users actively using system

### 20.2 Business KPI Targets (6 Months Post Go-Live)

| KPI | Baseline | Target |
|---|---|---|
| Service order automation rate | 20% | 70% |
| Average jobs/technician/day | 4-5 | 7-8 |
| First-time fix rate | 70% | 85% |
| Inventory accuracy | 75% | 98% |
| Warranty claim submission time | 30-90 days | < 7 days |
| Month-end financial close | 15-20 days | ≤ 5 days |
| Customer CSAT | 3.8/5 | 4.7/5 |
| Online booking rate | 40% | 85% |
| AMC renewal rate | 60% | 85% |

### 20.3 System Performance Acceptance

| Test | Threshold |
|---|---|
| Page load (standard ERP screen) | ≤ 3 seconds at 500 concurrent users |
| API response time | ≤ 500ms at 95th percentile |
| Report generation | ≤ 30 seconds |
| Mobile offline sync integrity | 100% data integrity on reconnect |
| System uptime | ≥ 99.9% over 30-day period |
| DR drill | RPO ≤ 1 hour; RTO ≤ 4 hours |

---

## 21. IMPLEMENTATION APPROACH

### 21.1 Methodology
Agile/Iterative: 2-3 week sprints, sprint reviews with business stakeholders, UAT at each phase boundary, Go/No-Go gates.

### 21.2 Phased Rollout

| Phase | Duration | Modules | Geographic Scope |
|---|---|---|---|
| Phase 1 — Foundation | Months 1-4 | Service & Repair, CRM, Basic Inventory | Dhaka HQ + 5 pilot centers |
| Phase 2 — Field Operations | Months 4-7 | Field Service, Mobile App, Route Optimization | All Dhaka centers |
| Phase 3 — Financial Control | Months 7-10 | Finance, Invoicing, Payments | All Dhaka + Chittagong |
| Phase 4 — Contracts and Partners | Months 10-13 | Contract/Warranty, B2B, Vendor Portals | All active centers |
| Phase 5 — Workforce and Intelligence | Months 13-16 | HR, Full BI, Quality Management | All 51+ centers |
| Phase 6 — Full Rollout | Months 16-18 | Document Management, Advanced Analytics | Complete |

### 21.3 Key Milestones

| Milestone | Target Date |
|---|---|
| Project Kickoff | September 1, 2026 |
| Business Blueprint Complete | September 30, 2026 |
| Phase 1 Go-Live | January 1, 2027 |
| Phase 2 Go-Live | April 1, 2027 |
| Phase 3 Go-Live | July 1, 2027 |
| Phase 4 Go-Live | October 1, 2027 |
| Phase 5 Go-Live | January 1, 2028 |
| Full System Go-Live | March 1, 2028 |
| Project Closure | May 31, 2028 |

---

## 22. APPENDICES

### Appendix A: Glossary

| Term | Definition |
|---|---|
| AMC | Annual Maintenance Contract |
| RAMC | Residential Annual Maintenance Contract |
| Privilege Program | 1000FiX loyalty program — Silver/Gold/Diamond tiers, 50% labor discount |
| Work Order | Internal task assigned to a technician to execute service in a service order |
| Service Order | Customer-facing record of a service request |
| FTFR | First-Time Fix Rate — % of orders resolved on first visit |
| SLA | Service Level Agreement |
| CSAT | Customer Satisfaction Score |
| NPS | Net Promoter Score |
| TAT | Turnaround Time — service request to completion |
| BDT | Bangladeshi Taka |
| NBR | National Board of Revenue — Bangladesh tax authority |
| Mushak | Bangladesh VAT invoice format (NBR prescribed) |
| VAT | Value Added Tax |
| NID | National Identity Document (Bangladesh) |
| RBAC | Role-Based Access Control |
| MFA | Multi-Factor Authentication |
| PWA | Progressive Web Application |
| SaaS | Software as a Service |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| GRN | Goods Receipt Note |
| RTV | Return to Vendor |
| 3-Way Match | Matching PO + GRN + Vendor Invoice to approve payment |
| FIFO | First In, First Out |
| CAPA | Corrective and Preventive Action |
| BABOK | Business Analysis Body of Knowledge (IIBA) |
| RACI | Responsible, Accountable, Consulted, Informed |
| BEFTN | Bangladesh Electronic Funds Transfer Network |
| TCO | Total Cost of Ownership |
| P1/P2/P3 | Priority: Must-Have / Important / Nice-to-Have |
| BR/FR/SR/TR/BRU/NFR | Requirement type codes per IIBA BABOK v3 |

### Appendix B: Requirements Traceability Matrix (Summary)

| Req ID | Requirement (Short) | Type | Priority | Business Objective | Acceptance Criterion |
|---|---|---|---|---|---|
| BR-SRM-001 | Multi-channel service order creation | FR | P1 | BO-01 | Phase 1: Orders created from all 5 channels |
| BR-SRM-007 | SLA tracking | FR | P1 | BO-05 | Phase 1: SLA countdown on all orders |
| BR-FSM-001 | AI scheduling engine | FR | P1 | BO-02 | Phase 2: 15%+ travel time reduction |
| BR-FSM-007 | Technician mobile app | FR | P1 | BO-02 | Phase 2: 100% technicians using app |
| BR-INV-001 | Multi-location inventory | FR | P1 | BO-03 | Phase 1: All HQ stock in system |
| BR-INV-006 | Auto-replenishment alerts | FR | P1 | BO-03 | Phase 1: Zero missed reorder alerts |
| BR-CRM-001 | 360 degree customer profile | FR | P1 | BO-05 | Phase 1: All customer records migrated |
| BR-FIN-002 | Auto-invoice from work order | FR | P1 | BO-06 | Phase 3: 100% invoices auto-generated |
| BR-FIN-005 | Bangladesh VAT auto-calculation | FR | P1 | BO-10 | Phase 3: Zero tax compliance errors |
| BR-CWM-006 | Auto-generate warranty claims | FR | P1 | BO-04 | Phase 4: Claims auto-created within 24 hrs |
| BR-CWM-004 | AMC renewal alerts | FR | P1 | BO-08 | Phase 4: Renewal rate 85%+ |
| BR-HRM-008 | Performance-linked incentive | FR | P1 | BO-02 | Phase 5: Incentive payroll accurate |
| BR-BI-001 | Executive real-time dashboard | FR | P1 | BO-07 | Phase 5: All KPIs in real time |
| BRU-SRM-04 | QC checklist before completion | BRU | P1 | BO-05 | Phase 1: QC enforced on all orders |
| BRU-CWM-02 | Warranty claim within 24 hrs | BRU | P1 | BO-04 | Phase 4: Claim auto-created < 24 hrs |
| NFR-016 | Bengali + English language support | NFR | P1 | BO-02 | Phase 1: All interfaces bilingual |
| NFR-018 | Offline mode | NFR | P1 | BO-02 | Phase 2: Offline operation tested |

Full RTM with all 190+ requirements provided as separate Excel file.

### Appendix C: Reference Documents

| Document | Reference | Location in Codebase |
|---|---|---|
| ERP System Comprehensive RFP | 1000FIX-ERP-RFP-2026-001 | ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_RFP.md |
| Integrated Portal BRD v2.0 | — | Intergrated_web_portal/project_requirement_document/01_BRD_Business_Requirements_Document_v2.0.md |
| User Requirements Document | — | Intergrated_web_portal/project_requirement_document/03_URD_User_Requirements_Document.md |
| Software Requirements Specification | — | Intergrated_web_portal/project_requirement_document/04_SRS_Software_Requirements_Specification.md |
| Technology Stack Document | — | Intergrated_web_portal/project_requirement_document/05_Technology_Stack_Document.md |
| Company Profile | — | 1000FiX_Services_Company_Profile.md |
| Smart Portal Use Cases | — | Marketing_1/1000FIX_Smart_Portal_System_Use_Cases.md |
| Digital Transformation White Paper | — | Marketing_1/1000FIX_Digital_Transformation_White_Paper_Service_Industry.md |

### Appendix D: Authorized Brand Partners — Warranty Terms Summary

| Brand | Product Categories | Claim Method | Reimbursement Timeline |
|---|---|---|---|
| Dell | Laptops, Desktops, Servers, Monitors | Dell Partner Portal | 30-45 days |
| HP | Laptops, Desktops, Printers | HP Service Partner Portal | 30-60 days |
| Lenovo | Laptops, Desktops | Lenovo Partner Portal / Email | 45-60 days |
| Acer | Laptops, Desktops | Email + Documentation | 45-75 days |
| Samsung | Mobile, TV, Appliances | Samsung Partner System | 30-45 days |
| Xiaomi | Mobile, Smart Devices | Mi Service Portal | 30-45 days |
| Huawei | Mobile, Networking | Huawei Partner Portal | 45-60 days |
| Sony | Electronics, Laptops | Email Documentation | 45-75 days |
| BenQ | Monitors, Projectors | BenQ Partner Email | 45-75 days |
| Epson | Printers | Epson Partner Portal | 30-45 days |
| Gigabyte | Motherboards, GPUs | Email Documentation | 60-90 days |
| Microsoft | Surface Devices | Microsoft Partner Center | 30-45 days |
| Toshiba | Laptops | Email Documentation | 60-90 days |
| Intel | Components | Intel Partner Program | 45-60 days |
| TwinMOS | Memory, Storage | Email Documentation | 60-75 days |
| Delux | Peripherals | Email Documentation | 60-75 days |
| PNS | Various | Email Documentation | 60-75 days |

---

**END OF DOCUMENT**

---

*1000FiX Services Limited — Business Requirements Document*
*Version 1.0 | March 18, 2026 | CONFIDENTIAL*
*BRD Reference: 1000FIX-ERP-BRD-2026-001*

*586/1 (4th Floor), Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216, Bangladesh*
*Hotline: 16743 | Phone: 09644-300600 | Email: info@1000fix.com*
*ISO 9001:2015 Certified — Bangladesh's Largest After-Sales Service Provider*
