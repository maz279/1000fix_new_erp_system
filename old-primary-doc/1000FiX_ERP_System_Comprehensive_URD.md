# User Requirements Document (URD)
# Comprehensive ERP System & Smart Portal Suite
# 1000FiX Services Limited

---

**Document Reference:** 1000FIX-ERP-URD-2026-001
**Version:** 1.0
**Date:** March 18, 2026
**Classification:** CONFIDENTIAL — Internal Use Only
**Related Documents:** 1000FIX-ERP-RFP-2026-001 | 1000FIX-ERP-BRD-2026-001

---

## Document Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 0.1 | March 10, 2026 | BA Team | Initial draft — Sections 1–4 |
| 0.5 | March 14, 2026 | BA Team | Added Sections 5–10 (User Stories) |
| 0.9 | March 16, 2026 | BA Team | Added Sections 11–18 |
| 1.0 | March 18, 2026 | BA Team | Final version issued for approval |

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Sponsor / CEO | Mahmud Hassan | __________ | ________ |
| Operations Director | Nasreen Sultana | __________ | ________ |
| Finance Manager | Kamal Uddin | __________ | ________ |
| IT Administrator | Tanvir Ahmed | __________ | ________ |
| Lead Business Analyst | __________ | __________ | ________ |

---

## Table of Contents

1. Introduction & Purpose
2. Executive Summary
3. User Personas
4. User Roles & Access Matrix
5. User Goals & Needs
6. User Stories — Service & Repair Management (SRM)
7. User Stories — Field Service Management (FSM)
8. User Stories — Inventory Management (INV)
9. User Stories — CRM, Finance, HR & Contracts
10. User Stories — Smart Portal Suite
11. User Journey Maps
12. Usability Requirements
13. Localization & Bangladesh-Specific Requirements
14. Notification & Communication Requirements
15. Transition Requirements (User Adoption)
16. User Acceptance Criteria
17. Assumptions & Constraints
18. Appendices

---

# Section 1 — Introduction & Purpose

## 1.1 Purpose

This User Requirements Document (URD) defines the needs, goals, and expectations of every user who will interact with the 1000FiX ERP System and Smart Portal Suite. It translates the business requirements established in the BRD (1000FIX-ERP-BRD-2026-001) into user-centric stories, interaction requirements, usability criteria, and journey maps that will guide UX design, system configuration, and user acceptance testing.

## 1.2 Scope

This URD covers all 20 ERP user roles interacting with:
- 11 ERP modules (Service & Repair, Field Service, Inventory, CRM, Finance, HR, Contracts/Warranty, Procurement, BI/Reporting, Document Management, Quality Management)
- 6 Smart Portals (Customer Self-Service, Technician Mobile PWA, Admin Operations, Corporate B2B, Vendor & Partner, Analytics Dashboard)

## 1.3 Intended Audience

| Audience | How to Use This Document |
|----------|--------------------------|
| UX/UI Designers | Personas (Section 3), Journey Maps (Section 11), Usability Requirements (Section 12) |
| ERP Configurators / Developers | User Stories (Sections 6–10), Access Matrix (Section 4) |
| Project Managers | User Adoption Plan (Section 15), UAC (Section 16) |
| QA / Test Engineers | Acceptance Criteria (Section 16), User Stories with AC |
| Training Team | Transition Requirements (Section 15), Personas (Section 3) |
| Business Stakeholders | Executive Summary (Section 2), Journey Maps (Section 11) |

## 1.4 Document Hierarchy

```
RFP (1000FIX-ERP-RFP-2026-001)
  └─ BRD (1000FIX-ERP-BRD-2026-001)     ← "What the business needs"
       └─ URD (1000FIX-ERP-URD-2026-001) ← "What users need to do their jobs"
            └─ SRS / Technical Spec       ← "How the system will be built"
```

## 1.5 Definitions

| Term | Definition |
|------|-----------|
| User Story | "As a [role], I want to [action], so that [benefit]." — a user-centric requirement unit |
| Persona | A representative fictional user profile built from real user research |
| Journey Map | Step-by-step narrative of a user completing a key task end-to-end |
| AC | Acceptance Criteria — testable conditions that confirm a user story is complete |
| P1 / P2 / P3 | Priority: P1 = Must-Have, P2 = Important, P3 = Nice-to-Have |
| PWA | Progressive Web App — mobile web app with offline capability |
| SLA | Service Level Agreement — response/resolution time commitments |
| AMC | Annual Maintenance Contract |
| RAMC | Residential Annual Maintenance Contract |
| BDT | Bangladeshi Taka (৳) |
| NBR | National Board of Revenue (Bangladesh) |
| NID | National Identity Document (Bangladesh) |

---

# Section 2 — Executive Summary

## 2.1 User Experience Vision

The 1000FiX ERP System will transform daily work for 500+ employees and 250,000+ monthly customers by replacing manual, error-prone processes with a unified, intuitive, and mobile-ready platform. The vision is summarized below by stakeholder group:

| User Group | Current Experience | Future Experience |
|------------|--------------------|-------------------|
| Customers | Call hotline, wait for callback, uncertain status | Book in 3 taps, track technician live, pay via bKash |
| Field Technicians | Paper job cards, manual forms, calls to dispatch | Mobile app with daily jobs, offline capability, GPS navigation |
| Service Agents | Spreadsheets, phone calls, manual lookups | Single screen: customer history, device status, instant booking |
| Dispatch Managers | Manual assignment (45 min/morning) | AI-assisted dispatch in 2 minutes |
| Finance Officers | Manual invoices, separate VAT calculations | Auto-generated Mushak-compliant invoices, one-click reconciliation |
| Branch Managers | Weekly Excel reports from multiple sources | Real-time branch dashboard, exception alerts on phone |
| Corporate Clients | Email/phone requests, separate invoice per job | B2B portal: bulk booking, consolidated monthly invoices, SLA dashboard |
| CEO / Management | Monthly reports from finance, lag of weeks | Live analytics dashboard, drill-down to any branch/technician |

## 2.2 Key User Value Propositions

1. **Speed**: Service agents complete job intake in under 3 minutes vs. 12+ minutes today
2. **Mobility**: Technicians work fully paperless from any location, even without internet
3. **Transparency**: Customers see real-time technician location and service status
4. **Accuracy**: Finance officers eliminate 95% of manual invoice errors
5. **Visibility**: Managers get branch and network KPIs updated every 15 minutes
6. **Self-Service**: Customers handle booking, tracking, and payment without calling

## 2.3 User Adoption Success Criteria

- 90% of service center agents actively using ERP within 60 days of go-live
- 85% of field technicians completing jobs via mobile app within 30 days
- 75% of customers self-booking online within 90 days of portal launch
- System Usability Scale (SUS) score ≥ 75 across all user groups in post-go-live survey
- Zero critical usability defects in UAT sign-off

---

# Section 3 — User Personas

> Each persona includes: Role, Age, Location, Tech Literacy (1–5), Language, Daily Responsibilities, Primary Goals, Pain Points, Representative Quote, Preferred Device/Channel.

---

## Persona 1 — Service Center Agent

**Name:** Rashida Begum
**Role:** Front-Desk Service Center Agent
**Age:** 26 | **Location:** Mirpur Branch, Dhaka | **Tech Literacy:** 3/5
**Language:** Bengali (primary), limited English
**Device:** Windows desktop at service counter

**Daily Responsibilities:**
- Receive walk-in customers and register service requests
- Answer incoming calls and create phone-in service orders
- Collect customer devices, print job tokens
- Update service order status throughout the day
- Collect payments (cash, bKash, card) upon job completion
- Coordinate with technicians on job status updates

**Primary Goals:**
- Process customer intake quickly (customers queuing behind)
- Find existing customer records without searching multiple systems
- Know device warranty status instantly (avoid manual brand website checks)
- Generate printed job cards without manual typing

**Pain Points:**
- Currently opens 4 separate apps/spreadsheets per customer
- Warranty status requires calling brand partner hotline (5–10 min wait)
- Handwritten job cards often lost or misread by technicians
- No way to tell customer an accurate completion time

**Quote:** *"আমি চাই একটাই সিস্টেমে সব কাজ করতে পারব। এখন অনেক জায়গায় দেখতে হয়।"* ("I want to do everything in one system. Right now I have to look in many places.")

---

## Persona 2 — Dispatch Manager

**Name:** Farida Rahman
**Role:** Dispatch & Scheduling Manager
**Age:** 32 | **Location:** Corporate HQ, Dhaka | **Tech Literacy:** 4/5
**Language:** Bengali and English
**Device:** Dual-monitor desktop, smartphone (Android)

**Daily Responsibilities:**
- Assign field service jobs to technicians each morning
- Re-assign jobs in real time when technicians are delayed or unavailable
- Monitor 15–30 technicians simultaneously on a map view
- Handle escalations when technicians cannot complete jobs on-site
- Communicate estimated arrival times to customers

**Primary Goals:**
- Complete daily dispatch planning in under 10 minutes (currently 45 min)
- Monitor all active technicians' locations and job status on one screen
- Automatically get alerts when a job is running over SLA
- Easily re-assign jobs without phoning individual technicians

**Pain Points:**
- No real-time map view — calls technicians individually for status
- Re-assignment requires manual updates in spreadsheet then phone call
- No automatic SLA breach alert — discovered only when customer calls
- Cannot see technician skill/certification data quickly during assignment

**Quote:** *"If I could see all my technicians on a map with their current jobs, I could manage 3x the volume with the same team."*

---

## Persona 3 — Senior Field Technician

**Name:** Kabir Hossain
**Role:** Senior Field Technician (AC & IT Equipment)
**Age:** 40 | **Location:** Field (Dhaka North zone) | **Tech Literacy:** 3/5
**Language:** Bengali (primary)
**Device:** Android smartphone (company-provided)

**Daily Responsibilities:**
- Complete 6–8 field service jobs per day
- Diagnose and repair AC units, laptops, and printers on-site
- Document diagnosis, parts used, and work performed
- Collect customer signature and payment on completion
- Request parts from warehouse when not carried on-person

**Primary Goals:**
- Know his full day's job list with locations every morning
- Access customer device history and previous service notes before arriving
- Record job completion quickly — currently 15 min of paper forms
- Avoid traveling back to service center for parts he could have brought

**Pain Points:**
- Currently receives jobs via WhatsApp group message — easy to miss
- No offline access — loses productivity in weak-signal areas
- Paper forms illegible/lost; repeat questions to customer on next visit
- Travel time wasted: 30% of jobs require unplanned parts trip

**Quote:** *"আমি যদি আগে থেকে জানতাম কোন জব-এ কী পার্টস লাগবে, অনেক সময় বাঁচত।"* ("If I knew in advance what parts each job needs, I'd save a lot of time.")

---

## Persona 4 — Junior Field Technician

**Name:** Shakib Islam
**Role:** Junior Field Technician (Mobile & Tablet Repair)
**Age:** 24 | **Location:** Field (Chittagong) | **Tech Literacy:** 3/5
**Language:** Bengali
**Device:** Android smartphone (company-provided)

**Daily Responsibilities:**
- Complete 4–6 field service jobs per day under senior technician supervision
- Handle mobile phone and tablet repairs at customer premises
- Follow diagnostic checklists provided by supervisor
- Document work and collect customer feedback

**Primary Goals:**
- Access guided diagnostic checklists for unfamiliar device issues
- Escalate jobs to senior technician without disrupting the customer
- Build up personal performance record to advance to senior level
- Understand what tools/parts to carry for daily job types

**Pain Points:**
- No guided workflow for complex repairs — makes errors under pressure
- Escalation requires calling supervisor and explaining from scratch
- Cannot see his own performance metrics or targets
- Unsure which spare parts to stock in field kit

**Quote:** *"I want a checklist in the app that tells me step by step what to check. When I'm nervous at the customer's house, I forget things."*

---

## Persona 5 — Branch Manager

**Name:** Arif Chowdhury
**Role:** Branch Manager (Sylhet Service Center)
**Age:** 38 | **Location:** Sylhet | **Tech Literacy:** 3/5
**Language:** Bengali (primary), English for reports
**Device:** Desktop at branch, Android phone

**Daily Responsibilities:**
- Oversee all operations at a single service center (20–40 staff)
- Review daily job completion rates and revenue
- Approve parts requisitions and expense requests
- Conduct weekly team performance reviews
- Ensure branch-level SLA compliance
- Handle escalated customer complaints

**Primary Goals:**
- See daily branch performance on one screen without running reports manually
- Know which technicians are underperforming before weekly review meeting
- Approve inventory requisitions from phone while away from branch
- Get notified immediately when a complaint escalates

**Pain Points:**
- Currently compiles performance data manually from 3 different sources (2+ hours/week)
- Approvals happen only when physically at desk — delays for field staff
- Customer complaint history not visible in one place
- Cannot compare his branch's performance to network average

**Quote:** *"আমার ব্রাঞ্চের সব ডেটা এক জায়গায় দেখতে চাই — কতটা কাজ হলো, কতটা টাকা এলো, কারা ভালো করছে।"*

---

## Persona 6 — Operations Manager

**Name:** Nasreen Sultana
**Role:** National Operations Manager
**Age:** 42 | **Location:** Dhaka HQ | **Tech Literacy:** 4/5
**Language:** Bengali and English
**Device:** Laptop, large-screen desktop, smartphone

**Daily Responsibilities:**
- Oversee operations across all 51+ service centers
- Review network-wide KPIs: completion rate, customer satisfaction, SLA compliance
- Identify branches with performance issues and intervene
- Approve policy changes in service standards
- Report to CEO on operational health weekly

**Primary Goals:**
- Network-wide view of jobs, revenue, and SLA in real time
- Drill down to any branch or technician from summary to detail
- Set and monitor KPI targets by branch and region
- Identify seasonal demand patterns to plan capacity

**Pain Points:**
- Currently aggregates Excel reports from 51 branch managers (takes 1 day)
- No consistent reporting format across branches
- Cannot identify a branch problem until it is already a crisis
- Travel to branches required to assess real operational state

**Quote:** *"I need to spot a problem branch at 9 AM on a Monday, not 2 weeks later when I finally compile the reports."*

---

## Persona 7 — Finance Officer

**Name:** Mitu Akter
**Role:** Finance & Accounts Officer
**Age:** 29 | **Location:** Dhaka HQ | **Tech Literacy:** 3/5
**Language:** Bengali (primary)
**Device:** Windows desktop

**Daily Responsibilities:**
- Generate and issue service invoices (50–100/day)
- Process customer payments (cash, mobile money, card)
- Prepare NBR-compliant Mushak VAT invoices (Mushak 6.3)
- Reconcile daily cash collections from branches
- Follow up on outstanding invoices

**Primary Goals:**
- Generate invoices directly from completed service orders — no manual re-entry
- Calculate VAT automatically for each service category
- Reconcile daily payments from all channels in one screen
- Submit monthly VAT returns from system-generated data

**Pain Points:**
- Currently types invoice details manually from paper job cards
- Mushak invoice format requires separate Excel template — error-prone
- Receives cash collection reports from 51 branches via WhatsApp photos
- VAT category mapping done manually for each service type

**Quote:** *"প্রতিদিন ১০০টা ইনভয়েস বানাই হাতে। সিস্টেম যদি অটো করত, ভুলও কমত, সময়ও বাঁচত।"*

---

## Persona 8 — Finance Manager

**Name:** Kamal Uddin
**Role:** Finance Manager
**Age:** 45 | **Location:** Dhaka HQ | **Tech Literacy:** 3/5
**Language:** Bengali and English
**Device:** Laptop, desktop

**Daily Responsibilities:**
- Manage accounts payable/receivable
- Prepare monthly P&L statements
- Manage brand partner warranty reimbursement claims
- Oversee payroll processing (500+ employees)
- Budget vs. actual variance reporting

**Primary Goals:**
- Monthly financial close in 3 days vs. current 10+ days
- Consolidated P&L by branch, service category, and division
- Track warranty reimbursement claims vs. amounts received
- Automate salary disbursement via BEFTN

**Pain Points:**
- Financial data scattered across branch-level spreadsheets
- Warranty reimbursement tracking in separate Excel — frequent discrepancies
- Month-end close requires consolidation from 51 branches manually
- BEFTN payroll submission is manual — 2 days of work each month

**Quote:** *"Our monthly close takes 10 days because we're consolidating 51 branch Excel files. A real accounting system would cut that to 3 days."*

---

## Persona 9 — HR Officer

**Name:** Sonia Parvin
**Role:** HR Officer
**Age:** 27 | **Location:** Dhaka HQ | **Tech Literacy:** 3/5
**Language:** Bengali (primary)
**Device:** Windows desktop

**Daily Responsibilities:**
- Maintain employee records (500+ employees)
- Process attendance and leave requests
- Calculate monthly payroll including overtime and incentives
- Onboard new technicians and agents
- Process resignation/termination paperwork

**Primary Goals:**
- Access any employee's attendance, leave balance, and payroll history instantly
- Process monthly payroll without manual calculation of overtime and incentives
- Approve leave requests from branch staff without waiting for paper forms
- Generate employee headcount and turnover reports for management

**Pain Points:**
- Attendance data from 51 branches arrives as WhatsApp spreadsheets
- Overtime calculation is manual for each employee every month
- No self-service portal for employees — HR receives all requests via phone
- Leave balance tracking is per-person in separate Excel rows

**Quote:** *"পাঁচশত কর্মীর বেতন হিসাব প্রতি মাসে ম্যানুয়ালি করতে হয়। এটা অনেক সময় লাগে।"*

---

## Persona 10 — HR Manager

**Name:** Rahim Bhuiyan
**Role:** HR Manager
**Age:** 48 | **Location:** Dhaka HQ | **Tech Literacy:** 3/5
**Language:** Bengali and English
**Device:** Laptop, desktop

**Daily Responsibilities:**
- Set HR policies and compliance with Bangladesh Labour Act
- Approve annual performance reviews
- Manage training and certification programs for technicians
- Report on workforce KPIs to CEO

**Primary Goals:**
- Track technician certifications (brand partner, safety) with auto-expiry alerts
- Performance appraisal workflow without paper forms
- Workforce planning: headcount by branch vs. demand
- Training completion tracking by employee

**Pain Points:**
- Certification expiry tracked in a separate spreadsheet — often misses renewal dates
- No digital performance appraisal — all paper forms
- No link between technician performance ratings and incentive calculations
- Cannot see training completion status by branch

---

## Persona 11 — Inventory Manager

**Name:** Jahangir Hossain
**Role:** Inventory & Spare Parts Manager
**Age:** 44 | **Location:** Central Warehouse, Dhaka | **Tech Literacy:** 3/5
**Language:** Bengali (primary)
**Device:** Desktop at warehouse, Android tablet for floor operations

**Daily Responsibilities:**
- Manage spare parts inventory across central warehouse and 51 branches
- Process goods receipt (PO fulfilment) and goods issue (service orders)
- Monitor stock levels and trigger reorder when below reorder point
- Handle inter-branch stock transfer requests
- Conduct monthly physical stock counts

**Primary Goals:**
- See real-time stock level across all locations from one screen
- Automatic low-stock alerts before stockouts occur
- Receive and verify goods from suppliers against purchase orders
- Issue parts to technicians with full traceability

**Pain Points:**
- Currently uses a combination of Tally and Excel; no real-time visibility
- Stockouts discovered only when technician requests a part at the counter
- Inter-branch transfers tracked manually in a WhatsApp group
- Month-end stock count takes 3 days and always finds discrepancies

**Quote:** *"যখন টেকনিশিয়ান এসে বলে পার্টস নেই, তখনই বুঝি স্টক শেষ। আগে থেকে জানার ব্যবস্থা থাকলে ভালো হত।"*

---

## Persona 12 — Procurement Officer

**Name:** Nabil Islam
**Role:** Procurement Officer
**Age:** 31 | **Location:** Dhaka HQ | **Tech Literacy:** 4/5
**Language:** Bengali and English
**Device:** Desktop

**Daily Responsibilities:**
- Create purchase orders for spare parts and consumables
- Get quotations from 3+ vendors per category
- Manage vendor relationships and approved vendor list
- Track PO delivery status and update inventory on receipt
- Process vendor invoices for payment approval

**Primary Goals:**
- Create and track purchase orders without manual email chains
- Compare vendor quotes side-by-side before approving
- Know exact delivery status of each PO at any time
- Three-way match: PO vs. goods receipt vs. vendor invoice

**Pain Points:**
- PO process involves email + WhatsApp + Excel — no single system of record
- Vendor invoice often differs from PO — reconciliation is manual
- No visibility into what was received at each branch vs. what was ordered
- Cannot track vendor on-time delivery performance systematically

---

## Persona 13 — IT Administrator

**Name:** Tanvir Ahmed
**Role:** IT Administrator
**Age:** 34 | **Location:** Dhaka HQ | **Tech Literacy:** 5/5
**Language:** Bengali and English
**Device:** Laptop, terminal access

**Daily Responsibilities:**
- Manage ERP user accounts, roles, and permissions
- Monitor system performance and uptime
- Manage data backups and recovery
- Coordinate with ERP vendor for updates/patches
- Provide first-level IT support to all ERP users

**Primary Goals:**
- Create/deactivate user accounts in under 2 minutes
- See system health dashboard: server load, DB performance, error rates
- Configure branch-level access restrictions without vendor support
- Run and verify daily automated backup

**Pain Points:**
- Currently manages user accounts across multiple separate applications
- No consolidated audit trail of user actions across all systems
- System outages discovered by users before IT knows about them
- Backup verification is manual — no automated report

---

## Persona 14 — Corporate Client Facility Manager

**Name:** Imran Khan
**Role:** Corporate Facility Manager (Bank HQ, 12 locations)
**Age:** 38 | **Location:** Dhaka, corporate offices | **Tech Literacy:** 4/5
**Language:** English (primary), Bengali
**Device:** Laptop, iPhone

**Daily Responsibilities:**
- Manage IT equipment maintenance across 12 bank branches
- Place bulk service requests for 50–100 devices per quarter
- Review service quality and SLA compliance by branch
- Approve consolidated invoices from 1000FiX

**Primary Goals:**
- Submit bulk service requests for multiple devices in one transaction
- Dashboard showing AMC coverage, upcoming service schedules, and open jobs
- Single monthly invoice for all services across all locations
- Flag and escalate poor service quality for specific jobs

**Pain Points:**
- Currently places individual requests via phone and email per device
- No visibility into job status across 12 locations simultaneously
- Receives separate invoices per location — reconciliation takes 2 days
- No SLA performance data to justify contract renewal to management

---

## Persona 15 — Vendor / Supplier Representative

**Name:** Salman Sheikh
**Role:** Parts Supplier Representative
**Age:** 45 | **Location:** Dhaka (Electronics wholesale market) | **Tech Literacy:** 2/5
**Language:** Bengali
**Device:** Android phone, basic Windows PC

**Daily Responsibilities:**
- Receive purchase orders from 1000FiX
- Confirm order quantities and delivery dates
- Update delivery/tracking information
- Submit invoices for payment
- Check payment status

**Primary Goals:**
- Receive POs digitally without phone calls
- Confirm delivery schedule through the portal
- Submit delivery confirmation and invoice online
- Know payment status without calling accounts team

**Pain Points:**
- Receives POs via WhatsApp or phone — easy to lose
- Has to call 1000FiX every week to check payment status
- Invoice submission by hand delivery or email — no confirmation receipt
- No history of all orders in one place for his own records

---

## Persona 16 — Brand Partner Representative

**Name:** Tanvir Mahmud
**Role:** Samsung Authorized Service Centre Liaison
**Age:** 35 | **Location:** Dhaka (Samsung Bangladesh office) | **Tech Literacy:** 4/5
**Language:** English (primary), Bengali
**Device:** Laptop

**Daily Responsibilities:**
- Review warranty claims submitted by 1000FiX on Samsung devices
- Approve or dispute warranty repair costs
- Monitor service quality on Samsung warranty jobs
- Process reimbursement to 1000FiX for approved claims

**Primary Goals:**
- View all pending warranty claims with supporting documentation
- Approve or reject claims with comments from one dashboard
- Monitor Samsung service quality metrics (first-time fix rate, customer satisfaction)
- Download consolidated monthly reimbursement reports

**Pain Points:**
- Currently receives warranty claims as Excel attachments via email
- Supporting evidence (photos, diagnostic reports) in separate emails
- No way to track how long each claim has been pending
- Monthly reconciliation between submitted and approved amounts is manual

---

## Persona 17 — Customer (Tech-Savvy)

**Name:** Rafiq Ahmed
**Role:** Software Engineer (Customer)
**Age:** 28 | **Location:** Banani, Dhaka | **Tech Literacy:** 5/5
**Language:** English (primary), Bengali
**Device:** iPhone, laptop

**Goals:** Book service online in under 2 minutes, track technician arrival by GPS, pay via card or bKash, receive digital invoice by email.

**Pain Points:** Current 1000FiX website has no real-time tracking; must call hotline to get status update; paper invoices only.

---

## Persona 18 — Customer (General Urban)

**Name:** Tahmina Khatun
**Role:** Homemaker (Customer)
**Age:** 35 | **Location:** Gulshan, Dhaka | **Tech Literacy:** 3/5
**Language:** Bengali (primary)
**Device:** Android smartphone

**Goals:** Book AC service in Bengali on smartphone; know when technician will arrive; pay via bKash; get SMS confirmation.

**Pain Points:** English-only interfaces are confusing; uncertain about service cost before booking; needs to call hotline to know technician ETA.

---

## Persona 19 — Customer (Elderly / Low Tech)

**Name:** Abdul Karim
**Role:** Retired Government Employee (Customer)
**Age:** 62 | **Location:** Uttara, Dhaka | **Tech Literacy:** 1/5
**Language:** Bengali only
**Device:** Basic Android phone (used rarely)

**Goals:** Call hotline and get a reliable appointment; know a trusted technician will arrive; understand the cost before the technician starts.

**Pain Points:** Cannot use smartphone apps; concerned about being overcharged; wants the same technician as last time.

---

## Persona 20 — CEO / Business Owner

**Name:** Mahmud Hassan
**Role:** CEO & Founder
**Age:** 48 | **Location:** Dhaka HQ | **Tech Literacy:** 3/5
**Language:** Bengali and English
**Device:** iPad, laptop, smartphone

**Daily Responsibilities:**
- Review monthly P&L and growth metrics
- Evaluate branch and technician performance
- Make strategic decisions on expansion and new services

**Goals:** Real-time executive dashboard showing revenue, jobs completed, customer satisfaction, and technician utilization; ability to drill down to any branch; weekly automated summary delivered to email.

**Pain Points:** Currently waits 10+ days for monthly finance reports; no way to spot a problem branch until it becomes a crisis.

---

# Section 4 — User Roles & Access Matrix

## 4.1 Role Hierarchy

```
CEO / Business Owner
  └── Operations Manager
        ├── Branch Manager (×51)
        │     ├── Service Center Agent (×3-5 per branch)
        │     ├── Senior Technician (×4-8 per branch)
        │     └── Junior Technician (×2-4 per branch)
        └── Dispatch Manager (×3 national zones)
  └── Finance Manager
        └── Finance Officer (×3-5)
  └── HR Manager
        └── HR Officer (×2-3)
  └── IT Administrator
  └── Inventory Manager
        └── Procurement Officer
        └── Warehouse Staff
--- External ---
  Corporate Client (B2B Portal)
  Vendor / Supplier (Vendor Portal)
  Brand Partner Rep (Partner Portal)
  Customer (Customer Portal)
```

## 4.2 Portal Access by Role

| Role | Customer Portal | Technician PWA | Admin Portal | B2B Portal | Vendor Portal | Analytics |
|------|:--------------:|:--------------:|:------------:|:----------:|:-------------:|:---------:|
| Customer | ✓ | — | — | — | — | — |
| Field Technician | — | ✓ | — | — | — | — |
| Service Center Agent | — | — | ✓ (limited) | — | — | — |
| Dispatch Manager | — | — | ✓ (full) | — | — | ✓ (ops) |
| Branch Manager | — | — | ✓ (branch) | — | — | ✓ (branch) |
| Operations Manager | — | — | ✓ (full) | — | — | ✓ (full) |
| Finance Officer | — | — | ✓ (finance) | — | — | ✓ (finance) |
| Finance Manager | — | — | ✓ (finance) | — | — | ✓ (full) |
| HR Officer/Manager | — | — | ✓ (HR) | — | — | ✓ (HR) |
| Inventory Manager | — | — | ✓ (inventory) | — | — | ✓ (inventory) |
| Procurement Officer | — | — | ✓ (procurement) | — | ✓ | — |
| IT Administrator | — | — | ✓ (system) | — | — | — |
| CEO | — | — | — | — | — | ✓ (executive) |
| Corporate Client | — | — | — | ✓ | — | — |
| Vendor | — | — | — | — | ✓ | — |
| Brand Partner | — | — | — | — | ✓ (partner view) | — |

## 4.3 ERP Module Access by Role (Create / Read / Update / Delete)

| Module | Agent | Dispatcher | Field Tech | Branch Mgr | Ops Mgr | Finance Offr | HR Offr | Inv Mgr | IT Admin |
|--------|-------|-----------|-----------|-----------|---------|-------------|--------|--------|---------|
| Service Orders | C,R,U | C,R,U | R,U | C,R,U,D | C,R,U,D | R | R | R | R |
| Work Orders | R,U | C,R,U | R,U | C,R,U,D | C,R,U,D | R | — | R | R |
| Customer / CRM | C,R,U | R | R | C,R,U | C,R,U,D | R | — | — | R |
| Inventory | R | R | R (view) | R,U | R,U | R | — | C,R,U,D | R |
| Invoicing | C,R | R | R | R,U | R,U | C,R,U | — | — | R |
| Payments | C,R | — | C,R | R | R,U | C,R,U,D | — | — | R |
| HR / Payroll | — | — | R (own) | R (branch) | R | — | C,R,U,D | — | R |
| Contracts/AMC | R | R | R | R,U | C,R,U,D | R | — | — | R |
| Procurement | — | — | — | R,U | R,U | R | — | C,R,U,D | R |
| BI / Reports | R (basic) | R (ops) | R (own) | R (branch) | R,U | R (fin) | R (HR) | R (inv) | R (sys) |
| Quality | R | R | C,R | R,U | C,R,U,D | — | — | — | R |
| Document Mgmt | R | R | R | C,R,U | C,R,U,D | R | — | R | C,R,U,D |
| User Management | — | — | — | — | — | — | — | — | C,R,U,D |

---

# Section 5 — User Goals & Needs

## 5.1 Operations Staff (Agents, Dispatch Managers)

| Goal | Measure of Success |
|------|-------------------|
| Complete service intake in <3 minutes per customer | Average intake time ≤ 3 min in system logs |
| Find any customer's full history in ≤ 2 clicks | User testing: 95% find within 2 clicks |
| Assign all morning jobs in <10 minutes | Dispatch time logged in system |
| Know real-time location of all assigned technicians | Map refresh ≤ 30 seconds |
| Get automatic SLA breach warnings before they escalate | Alert fires 30 min before SLA deadline |

## 5.2 Field Technicians (Senior & Junior)

| Goal | Measure of Success |
|------|-------------------|
| Access full job list with customer info each morning | Job list loads within 10 sec even on 3G |
| Complete job documentation in <5 minutes on mobile | Average documentation time ≤ 5 min |
| Work offline for up to 24 hours | App tested offline for 24h without data loss |
| Access repair guides and parts database on-site | Database available offline |
| See own earnings and performance score | Updated same day as job close |

## 5.3 Management (Branch Managers, Operations Manager)

| Goal | Measure of Success |
|------|-------------------|
| Branch KPI dashboard available by 7 AM daily | Automated overnight data refresh |
| Approve requests from mobile without returning to desk | Mobile approval in ≤ 3 taps |
| Compare own branch to network average | Benchmark widget on every branch dashboard |
| Receive instant alerts for customer complaints | Alert within 2 minutes of complaint submission |
| Drill down from network view to individual job in ≤4 clicks | User testing: 90% achieve in ≤4 clicks |

## 5.4 Finance & HR

| Goal | Measure of Success |
|------|-------------------|
| Generate NBR Mushak invoice from service order in 1 click | Invoice generation ≤ 5 seconds |
| Monthly payroll processing in <1 day vs. current 3 days | Payroll close time tracked |
| VAT return data auto-populated in NBR-compliant format | Zero manual tax calculation required |
| Approve leave and expense requests remotely | Mobile approval available |
| All financial reports available within 1 day of month-end | System close process automated |

## 5.5 Support Functions (Inventory, Procurement, IT)

| Goal | Measure of Success |
|------|-------------------|
| Real-time stock level visible across all 51 branches | Stock data refreshes every 15 minutes |
| Automatic reorder alert when stock falls below safety level | Alert fires at reorder point, not at zero |
| Three-way PO match automated | System automatically flags mismatches |
| User account created/deactivated in <2 minutes | IT admin task time ≤ 2 min |

## 5.6 External Users (Customers, Corporate, Vendors, Partners)

| Goal | Measure of Success |
|------|-------------------|
| Customer books service in ≤3 steps on mobile | Booking funnel conversion ≥ 70% |
| Customer tracks technician in real time | GPS update ≤ 30-second latency |
| Corporate client submits bulk service request in <5 min | Booking creation time logged |
| Vendor receives and confirms PO without phone call | Portal PO acknowledgment rate ≥ 90% |
| Brand partner approves warranty claim with attachments online | Claim approval without email/phone |

---

# Section 6 — User Stories: Service & Repair Management (SRM)

> Format: **[US-SRM-NNN]** | Role | Priority | Linked BRD Requirement

---

### 6.1 Service Request Intake

**US-SRM-001** | Service Center Agent | P1 | BR-SRM-001
*As a service center agent, I want to create a new service order by entering the customer's phone number, so that the system auto-fills their name, address, and device history.*
**AC:**
1. System looks up customer by phone number in ≤1 second
2. If found: name, address, registered devices pre-populated
3. If not found: agent can create new customer record inline
4. Duplicate check: system warns if same device has open service order
5. New service order gets unique job number (format: BRANCHCODE-YYMMDD-NNN)

**US-SRM-002** | Service Center Agent | P1 | BR-SRM-002
*As a service center agent, I want to check a device's warranty status instantly by scanning the serial number barcode, so that I don't need to call the brand partner.*
**AC:**
1. Barcode scanner input accepted in serial number field
2. System checks against warranty registry in ≤2 seconds
3. Displays warranty status: In-Warranty / Out-of-Warranty / Expired, with expiry date
4. If brand partner API is down, last-known status displayed with timestamp
5. Agent can manually override with reason logged

**US-SRM-003** | Service Center Agent | P1 | BR-SRM-003
*As a service center agent, I want to select the service type, device model, and problem description from dropdown lists, so that service orders are standardized and require minimal typing.*
**AC:**
1. Service category dropdown: IT Equipment / Home Appliance / Mobile & Tablet
2. Brand and model selection narrows based on category selection
3. Problem description has pre-defined options + free-text field
4. Service level (Level 1 / Level 2 / Level 3) auto-suggested based on problem
5. Estimated service charge displayed before order confirmation

**US-SRM-004** | Service Center Agent | P2 | BR-SRM-004
*As a service center agent, I want to print a customer job token with the service order number and QR code at the front desk printer, so that the customer can track their order.*
**AC:**
1. Print button visible after service order is saved
2. Print to configured receipt printer in ≤3 seconds
3. Token includes: Job Number, QR code, customer name, device, estimated completion date
4. QR code links to customer tracking page
5. Second copy (internal job card) printed for technician

**US-SRM-005** | Service Center Agent | P1 | BR-SRM-005
*As a service center agent, I want to register a customer's device (serial number, purchase date, brand) when they visit for the first time, so that warranty checks are instant on future visits.*
**AC:**
1. Device registration form: serial number, brand, model, purchase date, warranty expiry
2. Customer can register multiple devices under one account
3. Device record linked to customer account
4. Photo upload field for purchase receipt
5. Confirmation SMS sent to customer with device registration details

**US-SRM-006** | Dispatch Manager | P1 | BR-SRM-010
*As a dispatch manager, I want to see all unassigned service orders in a prioritized queue, so that I can assign the most urgent jobs first.*
**AC:**
1. Queue sorted by: SLA deadline ascending (nearest first)
2. Filter options: branch, service type, priority (Urgent/Normal/Low)
3. Each row shows: job number, customer, device, problem, SLA deadline, status
4. Color coding: Red = ≤1h to SLA, Amber = ≤4h, Green = >4h
5. One-click assignment opens technician selection panel

**US-SRM-007** | Dispatch Manager | P1 | BR-SRM-011
*As a dispatch manager, I want the system to recommend the best available technician for each job based on skills, location, and current workload, so that I can dispatch optimally.*
**AC:**
1. System shows ranked list of available technicians for each job
2. Ranking factors: brand certification match, distance from job, current job count
3. Technician skill/certification visible inline (e.g., "Dell Certified", "AC Installer")
4. Estimated travel time shown for top 3 recommendations
5. Dispatcher can override recommendation with reason logged

**US-SRM-008** | Branch Manager | P2 | BR-SRM-015
*As a branch manager, I want to see the day's service order pipeline (pending, in-progress, completed) for my branch in a visual board, so that I can identify bottlenecks.*
**AC:**
1. Kanban-style board: columns = Pending Diagnosis / In Progress / Awaiting Parts / Quality Check / Ready for Delivery / Closed
2. Each card shows: job number, device, technician assigned, SLA indicator
3. Cards auto-move columns as status is updated by technicians
4. Overdue cards highlighted in red
5. Board refreshes every 2 minutes automatically

**US-SRM-009** | Service Center Agent | P1 | BR-SRM-020
*As a service center agent, I want to update the customer when their device is ready for collection and send an SMS with the collection details, so that the customer doesn't need to call to check status.*
**AC:**
1. "Ready for Delivery" status change triggers auto-SMS to customer
2. SMS template in Bengali and English based on customer preference
3. SMS includes: job number, service center address, working hours
4. Agent can preview and edit SMS before sending
5. SMS delivery confirmation logged in service order timeline

**US-SRM-010** | Service Center Agent | P1 | BR-SRM-021
*As a service center agent, I want to process the final payment (cash, bKash, Nagad, card) and generate the official Mushak VAT invoice upon device collection, so that all transactions are compliant.*
**AC:**
1. Payment screen shows: service charge breakdown, parts cost, VAT (15%), total
2. Payment method selection: Cash / bKash / Nagad / Rocket / Card (SSLCOMMERZ)
3. bKash/Nagad payment initiated from ERP, confirmation required before invoice prints
4. Mushak 6.3 format invoice auto-generated with NBR-compliant fields
5. Invoice stored in customer's digital account and sent by email/SMS

---

### 6.2 Service Order Management

**US-SRM-011** | Technician | P1 | BR-SRM-025
*As a field technician, I want to update the diagnosis and repair status on my mobile app after examining the device, so that the customer and agent know what's being done.*
**AC:**
1. Status options: Received → Diagnosed → Repair In Progress → Awaiting Parts → Repair Complete → QC Passed
2. Technician can add diagnosis notes with voice-to-text (Bengali supported)
3. Photo upload for before/after device condition
4. Parts required list: technician selects from parts catalog; triggers parts request
5. Status update synced to system and visible to customer portal within 60 seconds

**US-SRM-012** | Service Center Agent | P2 | BR-SRM-026
*As a service center agent, I want to see and update the complete timeline of every service order, so that I can answer customer inquiries accurately.*
**AC:**
1. Timeline view shows all status changes with timestamp and actor
2. Customer communications (SMS, email) shown in timeline
3. Parts requests and fulfillment shown in timeline
4. Agent can add manual note to timeline
5. Timeline exportable as PDF for customer disputes

**US-SRM-013** | Branch Manager | P2 | BR-SRM-030
*As a branch manager, I want to see daily, weekly, and monthly job completion summaries for my branch, so that I can track performance trends.*
**AC:**
1. Dashboard widget: total jobs today / this week / this month
2. Breakdown by status: completed, in-progress, pending, overdue
3. Completion rate % vs. target shown
4. Average turnaround time (TAT) by service category
5. Comparison to previous period (week/month)

**US-SRM-014** | Operations Manager | P1 | BR-SRM-035
*As an operations manager, I want to set and monitor service SLA targets (e.g., laptop repair ≤ 3 business days) per service category, so that I can enforce quality standards.*
**AC:**
1. SLA configuration by: service type, device category, priority level
2. System calculates SLA deadline on service order creation
3. SLA breach alert: 30 min before breach → agent and manager notified
4. SLA compliance rate shown on ops dashboard
5. SLA breaches logged with root cause field for post-analysis

**US-SRM-015** | Service Center Agent | P1 | BR-SRM-040
*As a service center agent, I want to accept a pick & drop service request online, schedule a pickup time, and assign a pickup coordinator, so that the customer doesn't need to visit the service center.*
**AC:**
1. Pick & Drop booking captures: customer address, preferred pickup date/time slot
2. Pickup coordinator assigned from available staff
3. Customer receives SMS with coordinator name and estimated arrival time
4. Device condition recorded at pickup with photos (pre-repair state)
5. Return delivery scheduled at repair completion

---

# Section 7 — User Stories: Field Service Management (FSM)

---

**US-FSM-001** | Senior Field Technician | P1 | BR-FSM-001
*As a senior field technician, I want to see my full daily job schedule with customer locations on a map each morning, so that I can plan my route before leaving the service center.*
**AC:**
1. Job list available by 7:30 AM for same-day jobs
2. Map view shows all job pins with customer addresses
3. Recommended route calculated automatically (Timefold optimization)
4. Each pin shows: customer name, time slot, service type, priority
5. Technician can re-order jobs manually if needed with reason logged

**US-FSM-002** | Senior Field Technician | P1 | BR-FSM-002
*As a field technician, I want to access the customer's full device history and previous service notes before I arrive at their location, so that I can prepare the right tools and parts.*
**AC:**
1. Job detail screen shows: device make/model, all previous service records, parts used historically
2. Previous technician notes visible
3. Parts checklist can be built by technician pre-visit
4. Data available offline (downloaded when job assigned)
5. Brand-specific service manual link available

**US-FSM-003** | Senior Field Technician | P1 | BR-FSM-003
*As a field technician, I want to check-in to a job when I arrive at the customer's location, so that dispatch knows I've arrived and the customer is notified.*
**AC:**
1. "I've Arrived" button on job screen
2. GPS location captured at check-in (validates technician is at/near customer address)
3. Customer receives automatic SMS: "Your technician [Name] has arrived"
4. Job timer starts at check-in for SLA tracking
5. Dispatch map updates to show technician status as "On Site"

**US-FSM-004** | Junior Field Technician | P1 | BR-FSM-005
*As a junior technician, I want to access guided step-by-step diagnostic checklists for each service type on my mobile, so that I don't miss steps when handling complex repairs.*
**AC:**
1. Checklist library organized by: device type → brand → problem category
2. Each checklist item has a pass/fail/N.A. checkbox
3. Checklist completion is mandatory before job can be marked "Repair Complete"
4. Technician can attach photo evidence to checklist items
5. Incomplete checklist triggers warning before completion submission

**US-FSM-005** | Field Technician | P1 | BR-FSM-006
*As a field technician, I want to request spare parts from the nearest branch warehouse through the app, so that I don't have to travel back to the service center.*
**AC:**
1. Parts request form: job number, part name/SKU, quantity needed
2. System checks availability at nearest branches automatically
3. Parts request submitted to inventory manager for approval
4. Technician receives in-app notification when parts approved and ready
5. Parts consumption recorded against job and deducted from inventory

**US-FSM-006** | Field Technician | P1 | BR-FSM-007
*As a field technician, I want to complete job documentation (parts used, time spent, customer signature) on my phone in under 5 minutes, so that paperwork doesn't take time away from productive work.*
**AC:**
1. Parts used: searchable dropdown, quantity entry
2. Time spent: auto-calculated from check-in to completion
3. Work done description: voice-to-text or pre-defined option selection
4. Customer signature captured on phone screen (touchscreen)
5. All fields sync to ERP within 30 seconds of internet connection restored

**US-FSM-007** | Dispatch Manager | P1 | BR-FSM-010
*As a dispatch manager, I want to see all field technicians' real-time locations and current job status on an interactive map, so that I can proactively manage the field team.*
**AC:**
1. Map shows all active technicians with colored pins: Green = On Route, Blue = On Site, Orange = Delayed, Red = SLA Alert
2. Click on pin: shows technician name, current job, ETA to completion
3. Map auto-refreshes every 30 seconds
4. Filter by zone, technician, or status
5. SLA-at-risk jobs shown with countdown timer on map

**US-FSM-008** | Dispatch Manager | P2 | BR-FSM-011
*As a dispatch manager, I want to reassign a job from one technician to another directly on the map when a technician is unexpectedly delayed, so that SLA is preserved.*
**AC:**
1. Right-click on job pin → "Reassign" option
2. System shows available technicians sorted by distance and availability
3. New technician selected → old technician notified of removal, new technician notified of assignment
4. Customer notified automatically of technician change and new ETA
5. Reassignment logged with reason in job history

**US-FSM-009** | Field Technician | P1 | BR-FSM-015
*As a field technician, I want to use the app fully offline for up to 24 hours, so that poor mobile connectivity in some areas doesn't stop me from completing my work.*
**AC:**
1. Job list, customer data, checklists, and parts catalog downloaded on app open (WiFi or 4G)
2. All actions (check-in, status updates, documentation) queued locally when offline
3. Queue syncs automatically when connection restored
4. Offline indicator shown in app header when in offline mode
5. No data loss after 24 hours offline tested in QA

**US-FSM-010** | Field Technician | P2 | BR-FSM-020
*As a field technician, I want to collect cash and mobile money payments on-site and record them in the app, so that I don't need to carry cash back to the service center.*
**AC:**
1. Payment collection screen shows: invoice total, payment method selection
2. bKash/Nagad: system generates payment request; customer pays on their phone; technician confirms
3. Cash: technician enters amount collected; system generates receipt
4. Digital receipt sent to customer via SMS
5. Payment logged to service order; reconciled by finance at end of day

**US-FSM-011** | Senior Field Technician | P2 | BR-FSM-021
*As a senior technician, I want to escalate a job to the service center if on-site repair is not possible, so that the customer's device is moved to the workshop with proper documentation.*
**AC:**
1. "Escalate to Workshop" button visible in job screen
2. Technician documents reason for escalation
3. Customer notified of escalation and estimated workshop repair time
4. New service order created in ERP as workshop job; linked to field job
5. Device pick-up logistics arranged through system

**US-FSM-012** | Junior Field Technician | P2 | BR-FSM-022
*As a junior technician, I want to request remote technical support from a senior technician through the app during a difficult job, so that I can resolve complex issues without leaving the customer.*
**AC:**
1. "Request Support" button in job screen
2. Support request shows: job description, device, problem, photos
3. Available senior technicians/supervisors notified in-app
4. In-app chat or voice call initiated between junior and senior
5. Support conversation logged against job record

**US-FSM-013** | Field Technician | P1 | BR-FSM-025
*As a field technician, I want to view my daily performance metrics (jobs completed, on-time rate, customer ratings) on my app dashboard, so that I know how I'm doing against targets.*
**AC:**
1. Personal dashboard: today's jobs completed / remaining, on-time completion %, average customer rating
2. This week and this month summary
3. Monthly target progress bar
4. Top-3 compliments/complaints from customer feedback
5. Earnings estimate for current month (based on completed jobs)

---

# Section 8 — User Stories: Inventory Management (INV)

---

**US-INV-001** | Inventory Manager | P1 | BR-INV-001
*As an inventory manager, I want to see real-time stock levels for all spare parts across all 51 branches on one screen, so that I can identify potential stockouts before they happen.*
**AC:**
1. Dashboard: list of all SKUs with quantity by branch and total network stock
2. Color coding: Red = at or below reorder point, Amber = ≤150% of reorder point, Green = adequate
3. Filter by: branch, category, brand, low-stock only
4. Last updated timestamp shown per branch
5. Export to Excel button available

**US-INV-002** | Inventory Manager | P1 | BR-INV-002
*As an inventory manager, I want the system to automatically generate a purchase requisition when any item falls below its reorder point, so that I never experience stockouts on critical parts.*
**AC:**
1. Reorder point and economic order quantity configurable per SKU
2. Auto-requisition triggered when stock ≤ reorder point
3. Requisition includes: SKU, current stock, reorder point, suggested order quantity, preferred vendor
4. Inventory manager receives in-app and email notification
5. Requisition sent to procurement officer for PO creation

**US-INV-003** | Warehouse Staff | P1 | BR-INV-005
*As a warehouse staff member, I want to receive incoming goods against a purchase order using a barcode scanner, so that stock updates happen automatically without manual data entry.*
**AC:**
1. GRN screen: scan PO barcode or search by PO number
2. For each line item: scan part barcode, enter quantity received
3. System flags discrepancies (received ≠ PO quantity) for approval
4. On confirmation: inventory updated in real time
5. GRN document generated and linked to PO

**US-INV-004** | Inventory Manager | P2 | BR-INV-010
*As an inventory manager, I want to request inter-branch stock transfers when one branch is short and another has surplus, so that I can balance stock without waiting for new procurement.*
**AC:**
1. Transfer request: source branch, destination branch, SKU, quantity
2. Source branch manager notified for approval
3. On approval: stock decremented from source, incremented at destination
4. Transfer order document generated for courier/delivery tracking
5. Recipient branch confirms receipt; system records in-transit period

**US-INV-005** | Field Technician | P1 | BR-INV-015
*As a field technician, I want to check the availability of a spare part at any branch from my mobile, so that I know where to source it before requesting a transfer.*
**AC:**
1. Parts search in technician app: search by name, SKU, or barcode
2. Results show: available qty at each branch, distance from technician
3. "Request from Branch" button on result row
4. Request notification sent to branch inventory manager
5. Technician sees request status in app

**US-INV-006** | Inventory Manager | P2 | BR-INV-020
*As an inventory manager, I want to conduct a stock count by scanning items in the warehouse with a mobile device, so that physical count is reconciled automatically against system stock.*
**AC:**
1. Stock count session initiated in system (freezes outgoing movements during count)
2. Scanner/mobile app: scan item barcode, enter counted quantity
3. Count vs. system stock comparison shown in real time
4. Discrepancies flagged: system prompts for recount before acceptance
5. Variance report generated; approval required for adjustments

---

# Section 9 — User Stories: CRM, Finance, HR & Contracts

---

### 9.1 CRM User Stories

**US-CRM-001** | Service Center Agent | P1 | BR-CRM-001
*As a service center agent, I want to search for a customer by name, phone, or device serial number and see their complete interaction history, so that I can provide personalized service.*
**AC:**
1. Search returns results in ≤1 second
2. Customer profile shows: total visits, devices registered, open jobs, lifetime spend, loyalty points
3. Last 5 service orders shown on profile with status
4. One-click to create new service order from customer profile
5. Customer tags visible: VIP, Corporate, Privileged Program member

**US-CRM-002** | Service Center Agent | P1 | BR-CRM-002
*As a service center agent, I want to log a customer complaint with category and priority, so that it is tracked and escalated to the right team.*
**AC:**
1. Complaint form: category (Service Quality/Technician Behavior/Billing/Delay), priority (High/Medium/Low), description
2. Complaint linked to original service order
3. Branch manager automatically notified for High priority complaints
4. Complaint reference number sent to customer via SMS
5. Resolution deadline shown: High = 24h, Medium = 72h, Low = 7 days

**US-CRM-003** | Operations Manager | P2 | BR-CRM-010
*As an operations manager, I want to view customer satisfaction scores and complaint trends by branch, so that I can identify service quality issues.*
**AC:**
1. Dashboard: average CSAT score by branch, trend over 3 months
2. Top complaint categories by branch and service type
3. Complaint resolution rate and average resolution time
4. Branches below CSAT target highlighted in red
5. Filter by date range, service category, branch

**US-CRM-004** | Finance Officer | P1 | BR-CRM-015
*As a finance officer, I want to manage the Privileged Program discount (50% off labor charges) automatically at invoice generation, so that no manual discount calculation is required.*
**AC:**
1. Customer's Privileged Program membership checked on invoice creation
2. Discount applied automatically to labor line items only (not parts)
3. Discount amount shown as separate line on invoice
4. Override requires manager approval; override reason logged
5. Monthly report of total Privileged Program discounts granted

### 9.2 Finance User Stories

**US-FIN-001** | Finance Officer | P1 | BR-FIN-001
*As a finance officer, I want to generate a Mushak 6.3 compliant VAT invoice from a completed service order in one click, so that I don't manually type invoice data.*
**AC:**
1. "Generate Invoice" button active only when service order status = Completed
2. Invoice auto-populated: customer NID/BIN, service description, amounts, VAT (15%), total
3. Invoice preview before printing/sending
4. PDF generated in Mushak 6.3 format; stored in system
5. Invoice number sequential, branch-wise, format: BRANCH-FIN-YYYYMM-NNN

**US-FIN-002** | Finance Officer | P1 | BR-FIN-002
*As a finance officer, I want to record and reconcile daily payments received from all channels (cash, bKash, Nagad, card) in one screen, so that end-of-day reconciliation takes under 15 minutes.*
**AC:**
1. Daily payments screen: all payments by channel, matched to invoices
2. Unmatched payments flagged for manual assignment
3. Cash collection per branch tallied and compared to expected (from completed jobs)
4. Discrepancies highlighted with alert for manager review
5. End-of-day report: total collected by channel, branch, and service type

**US-FIN-003** | Finance Manager | P1 | BR-FIN-010
*As a finance manager, I want to view the monthly P&L by branch and service category, so that I can identify the most and least profitable operations.*
**AC:**
1. P&L report: revenue, cost of parts, labor cost, gross profit by branch and service type
2. Current month vs. previous month comparison
3. Branch contribution as % of total network revenue
4. Drill-down: click on branch → detailed transactions
5. Export to Excel and PDF

**US-FIN-004** | Finance Manager | P2 | BR-FIN-015
*As a finance manager, I want to track warranty reimbursement claims submitted to brand partners and amounts received, so that I know exactly how much is owed to us.*
**AC:**
1. Claims register: claim number, brand, jobs covered, amount claimed, amount approved, payment received, outstanding
2. Aging report: outstanding claims by brand partner by age bucket (0-30 / 31-60 / 60+ days)
3. Dispute tracking: disputed claims logged with reason
4. Auto-alert when claim not acknowledged in 7 days
5. Monthly reconciliation report by brand partner

**US-FIN-005** | Finance Officer | P1 | BR-FIN-020
*As a finance officer, I want to process technician incentive payments as part of monthly payroll, with system-calculated amounts based on job completion metrics, so that manual incentive calculations are eliminated.*
**AC:**
1. Incentive rules configurable: rate per completed job, bonus for CSAT ≥ 4.5, deduction for SLA breach
2. System calculates incentive per technician at month-end
3. Finance officer reviews and approves incentive run
4. Incentive amounts added to payroll batch
5. Incentive breakdown report available per technician

### 9.3 HR User Stories

**US-HRM-001** | HR Officer | P1 | BR-HRM-001
*As an HR officer, I want to view attendance and leave records for all employees in real time, so that payroll calculations are based on accurate data.*
**AC:**
1. Attendance dashboard: present/absent/late by branch and department
2. Leave balance per employee: annual, sick, casual remaining
3. Attendance data from biometric device integration or manual entry
4. Late arrival threshold configurable: default >15 min after shift start
5. Attendance report exportable by branch, department, or employee

**US-HRM-002** | HR Officer | P1 | BR-HRM-002
*As an HR officer, I want to run the monthly payroll for all employees in one batch, with automatic calculation of basic salary, overtime, allowances, and deductions, so that payroll close is completed in one day.*
**AC:**
1. Payroll run inputs auto-populated from attendance, leave, and incentive modules
2. Overtime calculated: hours beyond standard shift × overtime rate (per Labour Act)
3. Deductions: income tax, provident fund, absent day deductions auto-calculated
4. Payroll preview screen for officer review before approval
5. On approval: BEFTN file generated for bank salary transfer

**US-HRM-003** | HR Manager | P2 | BR-HRM-010
*As an HR manager, I want to track technician certification status with automatic expiry reminders, so that no technician is dispatched with an expired brand certification.*
**AC:**
1. Certification register per technician: certification name, issuing brand, issue date, expiry date
2. Auto-alert to HR and branch manager: 60 days before expiry, 30 days before, on expiry
3. Dispatch system checks certification before assigning brand warranty job
4. Expired certification shown as warning on technician profile
5. Renewal tracking: planned renewal date, renewal confirmation upload

**US-HRM-004** | Employee (Technician/Agent) | P2 | BR-HRM-015
*As an employee, I want to apply for leave and check my leave balance through an employee self-service portal, so that I don't need to call or visit HR for routine requests.*
**AC:**
1. ESS (Employee Self-Service) accessible via web and mobile
2. Leave application: type (annual/sick/casual), dates, reason
3. Application routed to line manager for approval
4. Employee notified of approval/rejection with reason
5. Leave balance updated immediately on approval

### 9.4 Contract & Warranty User Stories

**US-CWM-001** | Service Center Agent | P1 | BR-CWM-001
*As a service center agent, I want to look up a customer's AMC contract and see which devices are covered, so that I can create a service order under the contract without additional charges.*
**AC:**
1. Customer search shows active AMC contracts with covered devices
2. Contract details: coverage period, services included, remaining visits, SLA
3. "Create AMC Service Order" links job to contract automatically
4. No charge invoice generated for covered services
5. Contract usage tracked: visits remaining, services consumed

**US-CWM-002** | Finance Manager | P2 | BR-CWM-005
*As a finance manager, I want to receive an alert 60 days before any AMC contract expires, so that the renewal team can contact the customer in time.*
**AC:**
1. Automated alert: 90 days, 60 days, 30 days before contract expiry
2. Alert sent to: account manager, finance, branch manager
3. Renewal opportunity created in CRM automatically
4. Customer receives renewal offer via SMS and email at 60 days
5. Contract renewal report: contracts expiring in next 90 days by branch

---

# Section 10 — User Stories: Smart Portal Suite

---

### 10.1 Customer Self-Service Portal

**US-CSP-001** | Customer (All) | P1 | BR-CSP-001
*As a customer, I want to book a service for my device in 3 steps (service type → schedule → confirm/pay), so that booking is fast and requires minimal effort.*
**AC:**
1. Step 1: Select service category → brand → model → problem
2. Step 2: Select service delivery mode (walk-in / on-site / pick & drop); choose date/time slot
3. Step 3: Review summary, enter payment, confirm
4. Total booking flow completable in ≤3 minutes on 4G
5. Booking confirmation SMS in Bengali sent within 30 seconds

**US-CSP-002** | Customer (All) | P1 | BR-CSP-002
*As a customer, I want to track my technician's real-time location on a map after they are dispatched, so that I know exactly when they will arrive.*
**AC:**
1. Tracking link sent via SMS after technician dispatched
2. Map shows technician current location updated every 30 seconds
3. Estimated arrival time displayed and updated as technician moves
4. Technician photo and name shown for security
5. "Call Technician" button available on tracking screen

**US-CSP-003** | Customer (All) | P1 | BR-CSP-003
*As a customer, I want to pay for my service using bKash, Nagad, or debit/credit card through the portal, so that I don't need to carry cash.*
**AC:**
1. Payment methods: bKash, Nagad, Rocket, SSLCOMMERZ (VISA/MC/local bank)
2. Saved payment methods (tokenized) for repeat customers
3. Payment confirmation shown within 10 seconds of transaction
4. Digital receipt sent by email and SMS in Bengali
5. Refund process available for cancellations within policy

**US-CSP-004** | Customer (All) | P1 | BR-CSP-004
*As a customer, I want to view my complete service history for all my registered devices, so that I can track repairs and maintenance over time.*
**AC:**
1. Service history: date, service type, technician, diagnosis, cost, invoice download
2. Filters: by device, date range, service type
3. Download invoice (PDF) for any completed job
4. Warranty status shown per registered device
5. "Book Again" button on any historical service

**US-CSP-005** | Customer (All) | P2 | BR-CSP-010
*As a customer, I want to rate my service experience and leave feedback after every completed job, so that I can help 1000FiX maintain quality.*
**AC:**
1. Rating prompt sent via SMS/app 2 hours after job completion
2. 1–5 star rating for technician and overall service
3. Optional text feedback (100 characters, Bengali/English)
4. Rating stored against technician profile
5. Thank you message sent on feedback submission

### 10.2 Technician Mobile PWA

**US-TMP-001** | Field Technician | P1 | BR-TMP-001
*As a field technician, I want my day's job list to load automatically when I open the app each morning, sorted by recommended route, so that I can start work immediately.*
**AC:**
1. Job list available by 7:30 AM (overnight dispatch process runs by 7:00 AM)
2. Jobs sorted by optimized route (Timefold)
3. Each job card: time slot, customer name, address, device, service type, estimated duration
4. Map view toggle shows all jobs on map
5. App opens offline if no internet; last synced data shown

**US-TMP-002** | Field Technician | P1 | BR-TMP-002
*As a field technician, I want push notifications for new or changed job assignments, so that I'm always aware of schedule updates without checking the app constantly.*
**AC:**
1. Push notification on: new job assigned, job reassigned, job cancelled, customer message received
2. Notification includes: customer name, address, time slot
3. Technician must acknowledge reassignment within 5 minutes or escalated
4. Notification sound and vibration configurable
5. Notification history accessible in app

**US-TMP-003** | Field Technician | P1 | BR-TMP-003
*As a field technician, I want to access the full parts catalog offline, so that I can search for parts and record parts used even without internet.*
**AC:**
1. Parts catalog synced at app open (≤5 MB compressed)
2. Search by: name, SKU, brand compatibility
3. Parts usage recording works offline
4. Catalog shows: part name, SKU, standard price, compatibility list
5. New parts added to catalog visible after next sync

### 10.3 Admin Operations Portal

**US-AOP-001** | Dispatch Manager | P1 | BR-AOP-001
*As a dispatch manager, I want a real-time operations dashboard showing total open jobs, technicians on field, jobs at risk of SLA breach, and today's completion rate, so that I have a complete picture at a glance.*
**AC:**
1. Dashboard loads in ≤2 seconds
2. KPI tiles: Open Jobs / Active Technicians / SLA At-Risk / Today's Completion Rate
3. Tiles refresh every 2 minutes automatically
4. Click on any tile → filtered job or technician list
5. Dashboard configurable: tiles can be added/removed by admin

**US-AOP-002** | Dispatch Manager | P1 | BR-AOP-002
*As a dispatch manager, I want to receive an in-app alert with an alarm tone when a job is 1 hour away from SLA breach, so that I can intervene before the breach occurs.*
**AC:**
1. Alert fires at T-60 minutes before SLA deadline
2. Alert shows: job number, customer, current technician, time to SLA
3. One-click escalation: mark as priority, contact technician, reassign
4. Alert acknowledged: dispatch manager confirms action taken
5. If not acknowledged in 10 minutes: escalated to branch manager

**US-AOP-003** | Service Center Agent | P2 | BR-AOP-005
*As a service center agent, I want to create a service order on behalf of a customer who calls by phone, without the customer needing to use the self-service portal.*
**AC:**
1. "Phone-In Booking" mode available in admin portal
2. Agent enters customer phone number → existing customer loaded or new customer created
3. Service type, device, schedule entered by agent
4. Booking confirmation SMS sent to customer on agent's behalf
5. "Created by Agent" logged in service order metadata

### 10.4 Corporate B2B Portal

**US-CBP-001** | Corporate Facility Manager | P1 | BR-CBP-001
*As a corporate facility manager, I want to submit a bulk service request for multiple devices across multiple locations in a single form, so that I don't make individual requests per device.*
**AC:**
1. Bulk request: upload CSV with device list (serial number, location, problem) or manual table entry
2. Up to 50 devices per bulk submission
3. Each device assigned a service order automatically
4. Summary confirmation email sent to facility manager with all job numbers
5. All jobs linked to corporate account for consolidated reporting

**US-CBP-002** | Corporate Facility Manager | P1 | BR-CBP-002
*As a corporate facility manager, I want a single consolidated invoice for all services across all locations for the month, so that my finance team can process one payment.*
**AC:**
1. Monthly invoice consolidates all jobs at all locations for the period
2. Invoice sorted by: location, device, service type
3. PO reference field on invoice (corporate PO number)
4. Invoice sent by email as PDF on the 1st of each month
5. Payment portal link included in invoice email (SSLCOMMERZ/bank transfer)

### 10.5 Vendor & Partner Portal

**US-VPP-001** | Vendor Representative | P1 | BR-VPP-001
*As a parts supplier, I want to receive purchase orders from 1000FiX through the vendor portal and confirm my delivery schedule, so that PO management doesn't require phone calls.*
**AC:**
1. New PO notification sent to vendor via email and portal
2. Vendor views PO details: line items, quantities, delivery address, required date
3. Vendor confirms or proposes revised delivery date
4. Confirmation logged; 1000FiX procurement officer notified
5. PO remains open until GRN confirmed by 1000FiX warehouse

**US-VPP-002** | Brand Partner Rep | P1 | BR-VPP-005
*As a brand partner representative, I want to view all pending warranty claim submissions from 1000FiX with supporting photos and diagnostics, so that I can approve or dispute claims from one portal.*
**AC:**
1. Claims list: job number, device serial, repair description, parts used, labor cost, total claim
2. Supporting attachments: before/after photos, diagnostic report, customer signature
3. Approve/Dispute/Request-More-Info actions available per claim
4. Dispute reason required for disputed claims
5. Approved claims total shown with payment schedule

### 10.6 Analytics & BI Dashboard

**US-ADB-001** | CEO | P1 | BR-ADB-001
*As a CEO, I want an executive dashboard showing revenue, jobs completed, customer satisfaction, and technician utilization for the current month, so that I can assess business health in under 5 minutes.*
**AC:**
1. Executive dashboard: MTD revenue (৳), jobs completed, avg CSAT, technician utilization %
2. vs. previous month and vs. target shown for each metric
3. Revenue trend line chart: last 6 months
4. Top 5 and bottom 5 branches by revenue shown
5. Dashboard loads in ≤3 seconds; available on tablet/mobile

**US-ADB-002** | Operations Manager | P1 | BR-ADB-002
*As an operations manager, I want to drill from the network summary down to a specific branch and further to individual technician performance in 3 clicks, so that I can identify the root cause of performance issues.*
**AC:**
1. Network → Region → Branch → Technician drill-down path
2. Each level shows consistent KPIs: jobs, completion rate, SLA %, CSAT, revenue
3. Drill-down via click on chart or table row
4. Back navigation breadcrumb
5. Deepest level: individual technician scorecard with job list

**US-ADB-003** | Finance Manager | P1 | BR-ADB-005
*As a finance manager, I want automated weekly financial summary reports delivered to my email every Monday morning, so that I stay informed without logging in each day.*
**AC:**
1. Report schedule configurable: daily/weekly/monthly
2. Report includes: weekly revenue, outstanding invoices, collected payments, top services by revenue
3. Delivered by 8:00 AM on configured day
4. Report format: inline HTML email + attached PDF
5. Recipient list configurable by IT admin


---

# Section 11 — User Journey Maps

> Each journey map shows: Actor(s), Trigger, Steps, Touchpoints, Emotional State, Pain Points Resolved, and System Features Engaged.

---

## Journey 1: Customer Walk-In Service Request

**Actor(s):** Customer (Tahmina Khatun) + Service Center Agent (Rashida Begum)
**Trigger:** Customer arrives at Mirpur branch with a malfunctioning AC remote controller

| Step | Who | Action | System Touchpoint | Emotion | Pain Point Resolved |
|------|-----|--------|------------------|---------|---------------------|
| 1 | Customer | Walks into service center, takes token from queue system | Physical queue display | Uncertain | Clear queue visibility |
| 2 | Agent | Greets customer; types customer phone number | ERP: Customer search screen | — | — |
| 3 | System | Auto-fills customer name, address, and registered devices | CRM module | Customer: relieved (quick) | No more manual re-entry |
| 4 | Agent | Scans AC unit serial number to check warranty | ERP: Warranty check | — | — |
| 5 | System | Shows warranty status: "In-Warranty — Samsung — expires Aug 2026" | Integration: Samsung API | Agent: confident | No more calling Samsung hotline |
| 6 | Agent | Selects service type: Home Appliance → AC → Remote Controller Issue | ERP: Service order creation | — | — |
| 7 | System | Estimates completion time: 2 business days; auto-assigns to AC technician queue | SRM + FSM modules | Customer: informed | Uncertain wait time eliminated |
| 8 | Agent | Confirms service order; prints job token with QR code | ERP: Print queue | Customer: satisfied | Clear proof of job registration |
| 9 | System | Sends SMS to customer: "Job #MRP-260318-042 registered. Track: [link]" | Notification module | Customer: confident | No more status anxiety |
| 10 | Customer | Leaves device; scans QR code on token to bookmark tracking page | Customer Portal | Customer: in control | Self-tracking empowerment |

**Duration:** 4 minutes (vs. 12+ minutes currently)
**Features Demonstrated:** CRM auto-fill, warranty API check, auto-assignment, SMS notification, QR tracking

---

## Journey 2: Customer Online Booking via Portal

**Actor(s):** Rafiq Ahmed (tech-savvy customer, uses iPhone)
**Trigger:** Rafiq's Dell laptop screen cracked; wants repair without visiting service center

| Step | Who | Action | System Touchpoint | Emotion |
|------|-----|--------|------------------|---------|
| 1 | Customer | Opens 1000FiX customer portal on iPhone | Customer Portal: Home page | Expecting it to be easy |
| 2 | Customer | Selects: IT Equipment → Laptop → Dell → Screen Damage | Booking wizard: Step 1 | Focused |
| 3 | System | Shows available service modes: Walk-in / On-site / Pick & Drop with prices | Portal: service mode selection | Pleasantly surprised (transparent pricing) |
| 4 | Customer | Selects Pick & Drop; chooses tomorrow 10–12 AM pickup slot | Booking wizard: Step 2 | Satisfied — flexible slots available |
| 5 | Customer | Reviews summary: service, slot, estimated cost BDT 2,500 + parts | Booking wizard: Step 3 | Confident |
| 6 | Customer | Pays BDT 500 advance via saved bKash | Payment: bKash integration | Smooth — payment in 3 taps |
| 7 | System | Creates service order; assigns pickup coordinator; sends SMS confirmation | SRM + FSM + Notification | Relieved — immediate confirmation |
| 8 | Next day | Coordinator arrives; scans device serial; photos device condition in app | FSM: Field technician app | Customer: trusts the process |
| 9 | Customer | Receives SMS with job updates (Received → Diagnosed → In Repair) | Notification: multi-step SMS | Informed — no need to call |
| 10 | Customer | Receives "Ready" SMS; returns device is delivered; pays balance via portal | Customer Portal: payment | Completely satisfied |

**Duration of initial booking:** 2 minutes 45 seconds
**Features Demonstrated:** 3-step booking, transparent pricing, advance payment, GPS dispatch, status notifications

---

## Journey 3: Field Technician Daily Workflow

**Actor(s):** Kabir Hossain (Senior Technician, Dhaka North zone)
**Trigger:** Kabir opens technician app at 7:45 AM before leaving home

| Step | Who | Action | System Touchpoint | Emotion |
|------|-----|--------|------------------|---------|
| 1 | Technician | Opens app; reviews 7 jobs sorted by optimized route | FSM: Daily job list | Prepared — knows the day |
| 2 | Technician | Taps Job 1: reviews customer history, device service notes, parts needed | FSM: Job detail + CRM history | Confident — no surprises |
| 3 | Technician | Leaves home; Google Maps navigation launched from within app | FSM: Maps integration | Efficient — no separate app needed |
| 4 | System | Notifies customer: "Your technician is on the way. ETA: 25 minutes" | Notification: automated SMS | — |
| 5 | Technician | Arrives; taps "I've Arrived" — customer gets "arrived" SMS | FSM: Check-in | Customer: reassured |
| 6 | Technician | Completes repair; follows guided checklist for AC installation | FSM: Checklist completion | Thorough — no missed steps |
| 7 | Technician | Documents: parts used (2 items scanned), time: 45 min, photos | FSM: Job documentation | Efficient — voice-to-text for notes |
| 8 | Technician | Requests customer signature on phone screen | FSM: Digital signature | Professional |
| 9 | Customer | Pays BDT 3,200 via bKash through technician's payment screen | FSM: Mobile payment | Convenient — no cash needed |
| 10 | Technician | Job marked complete; moves to Job 2 per optimized route | FSM: Next job navigation | Productive — day flows smoothly |
| 11 | [Job 4 scenario] | Enters low-signal area; app switches to offline mode | FSM: Offline mode | Uninterrupted — offline works |
| 12 | Technician | Completes 2 more jobs offline; syncs when signal restored | FSM: Sync queue | No data loss — seamless sync |

**Jobs completed:** 7/7 | **Average job documentation time:** 4.5 minutes (vs. 15 min paper)
**Features Demonstrated:** Optimized routing, pre-visit customer data, GPS check-in, checklist, offline mode, mobile payment

---

## Journey 4: Dispatch Manager Morning Optimization

**Actor(s):** Farida Rahman (Dispatch Manager)
**Trigger:** 7:00 AM — Farida arrives at office; 25 technicians, 48 jobs to assign

| Step | Who | Action | System Touchpoint | Emotion |
|------|-----|--------|------------------|---------|
| 1 | Farida | Opens dispatch console; sees 48 unassigned jobs in priority queue | Admin Portal: Dispatch Console | Focused — can see all at once |
| 2 | System | AI has auto-assigned 41 of 48 jobs overnight (Timefold optimization) | FSM: AI dispatch | Impressed — most work already done |
| 3 | Farida | Reviews 7 unassigned jobs flagged by system (skill mismatch / zone conflict) | Admin Portal: Flagged items | Focused |
| 4 | Farida | Job 1: Server repair; system recommends Hasan (Dell Certified) | FSM: Recommendation engine | Confident — right person suggested |
| 5 | Farida | Assigns Hasan; confirms all other AI suggestions with one "Approve All" | Admin Portal: Batch approve | Efficient — 2 minutes total |
| 6 | System | All technicians receive job notifications on their apps | FSM: Push notifications | — |
| 7 | [9:30 AM] | Farida receives alert: Technician Shakib delayed 2h (traffic) | Admin Portal: SLA alert | Proactive — alert before SLA breach |
| 8 | Farida | Reassigns Shakib's Job 3 to Mahbub (nearby, available) | Admin Portal: Map reassignment | In control |
| 9 | System | Customer notified of new technician and revised ETA | Notification module | Customer: informed, not frustrated |
| 10 | Farida | Reviews map at 12 PM: 22 of 25 technicians green, 3 on amber | Admin Portal: Live map | Confident — manageable load |

**Total dispatch time:** 9 minutes (vs. 45 minutes manually)
**Features Demonstrated:** AI auto-dispatch, batch approval, SLA alerts, map-based reassignment

---

## Journey 5: Warranty Claim Processing

**Actor(s):** Service Center Agent + Finance Manager + Samsung Brand Partner Rep
**Trigger:** Customer brings Samsung laptop for in-warranty repair

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Agent | Registers warranty service order; system confirms Samsung warranty valid | SRM + Warranty API |
| 2 | Technician | Completes repair; documents: replaced motherboard (Samsung part), 3h labor | FSM + Inventory |
| 3 | Agent | Closes service order; system auto-generates warranty claim draft | CWM: Warranty claim creation |
| 4 | Finance Mgr | Reviews claim: parts cost BDT 8,500 + labor BDT 900 = BDT 9,400 | CWM: Claim approval |
| 5 | System | Claim submitted to Samsung portal with: service order, photos, diagnostic report, technician cert | Integration: Brand partner portal |
| 6 | Samsung Rep | Logs into vendor portal; reviews claim documentation | Vendor Portal: Claims review |
| 7 | Samsung Rep | Approves BDT 8,500 parts; disputes BDT 900 labor (outside coverage) | Vendor Portal: Partial approval |
| 8 | Finance Mgr | Sees dispute notification; accepts partial; logs dispute to internal record | CWM: Dispute handling |
| 9 | System | Approved amount tracked in warranty reimbursement register | Finance module |
| 10 | System | Alert fires when reimbursement not received in 30 days | Finance: Aging alert |

---

## Journey 6: Finance Officer End-of-Day Reconciliation

**Actor(s):** Mitu Akter (Finance Officer)
**Trigger:** 6:00 PM — end of business day; need to reconcile all payments

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Mitu | Opens Finance module → Daily Reconciliation screen | Finance module |
| 2 | System | Shows: 87 invoices issued today, 82 paid, 5 outstanding | Finance: Reconciliation dashboard |
| 3 | Mitu | Reviews payment channels: Cash BDT 145K, bKash BDT 198K, Card BDT 67K | Finance: Channel summary |
| 4 | System | Flags 2 invoices: payment received but not matched to invoice | Finance: Unmatched payments |
| 5 | Mitu | Manually matches the 2 unmatched payments to correct invoices | Finance: Manual matching |
| 6 | Mitu | Reviews 5 outstanding invoices; sends follow-up SMS to customers from system | Finance + Notification |
| 7 | System | Generates Mushak VAT summary: total taxable value, total VAT collected today | Finance: VAT summary |
| 8 | Mitu | Exports daily summary report; forwards to Finance Manager | Finance: Report export |

**Duration:** 25 minutes (vs. 2+ hours previously)

---

## Journey 7: Corporate Client Bulk Booking

**Actor(s):** Imran Khan (Facility Manager, Bank HQ)
**Trigger:** Quarterly IT equipment maintenance due for 45 PCs across 12 locations

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Imran | Logs into B2B portal; clicks "New Bulk Service Request" | B2B Portal |
| 2 | Imran | Uploads CSV with 45 devices (serial, location, service type needed) | B2B Portal: CSV upload |
| 3 | System | Validates CSV; shows preview of 45 service orders to be created | B2B Portal: Validation |
| 4 | Imran | Sets preferred scheduling window: Mon–Thu 9 AM–3 PM over next 2 weeks | B2B Portal: Schedule |
| 5 | System | Creates 45 service orders; assigns to branch teams; sends confirmation | SRM + B2B Portal |
| 6 | Imran | Views unified dashboard: status of all 45 jobs across 12 locations | B2B Portal: Status dashboard |
| 7 | System | Sends Imran daily summary email: jobs completed / in-progress / pending | Notification: B2B summary |
| 8 | Month-end | System generates consolidated invoice: all 45 jobs, all locations, 1 invoice | Finance: Consolidated invoicing |

---

## Journey 8: Branch Manager Weekly Review

**Actor(s):** Arif Chowdhury (Sylhet Branch Manager)
**Trigger:** Monday morning — preparing for weekly team stand-up meeting

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Arif | Opens analytics dashboard → Branch Performance | Analytics: Branch dashboard |
| 2 | System | Shows: jobs completed this week: 218, completion rate: 94.3%, revenue: BDT 4.2L | Analytics: Branch KPIs |
| 3 | Arif | Notes 94.3% vs. branch target 95% and network average 93.8% | Analytics: Benchmark widget |
| 4 | Arif | Drills into "Incomplete Jobs" → 13 incomplete; 8 awaiting parts | Analytics: Drill-down |
| 5 | Arif | Identifies: 3 technicians each had 1 SLA breach this week | Analytics: Technician scorecard |
| 6 | Arif | Reviews customer satisfaction: branch CSAT 4.3/5 — same as last week | Analytics: CSAT trend |
| 7 | Arif | Downloads PDF summary for weekly meeting printout | Analytics: Report export |
| 8 | [During meeting] | Shows technicians their individual scorecards on screen | Analytics: Mobile view |

**Preparation time:** 8 minutes (vs. 2+ hours of manual data collection)

---

## Journey 9: HR Officer Monthly Payroll Run

**Actor(s):** Sonia Parvin (HR Officer)
**Trigger:** Last business day of month — payroll must be processed for 500 employees

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Sonia | Opens HR module → Payroll → New Payroll Run (March 2026) | HR module |
| 2 | System | Auto-imports attendance data, approved leaves, and approved incentive amounts | HR + FSM (incentives) |
| 3 | System | Calculates: basic salary + overtime + allowances − deductions − income tax | HR: Payroll calculation engine |
| 4 | Sonia | Reviews payroll summary: 498 employees processable; 2 with data issues | HR: Payroll preview |
| 5 | Sonia | Resolves 2 exceptions: 1 missing attendance (enters manually), 1 resignation (terminal pay) | HR: Exception handling |
| 6 | Sonia | Submits payroll run for Finance Manager approval | HR: Approval workflow |
| 7 | Finance Mgr | Reviews and approves; BEFTN file generated automatically | Finance: BEFTN file generation |
| 8 | Sonia | BEFTN file downloaded; uploaded to bank portal; salary transfer initiated | External: Bank portal |
| 9 | System | Sends salary SMS to all employees on transfer date | Notification: Salary SMS |

**Payroll close time:** 6 hours (vs. 2–3 days previously)

---

## Journey 10: Inventory Replenishment

**Actor(s):** Jahangir Hossain (Inventory Manager) + Nabil Islam (Procurement Officer)
**Trigger:** System alert fires: Laptop screen assembly (SKU: SCR-LAP-15FHD) below reorder point

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | System | Alert sent to Jahangir: "Stock at 8 units (reorder point: 15)" | Inventory: Auto-alert |
| 2 | Jahangir | Reviews: consumes avg 12/week; order qty suggestion = 50 units | Inventory: Stock analytics |
| 3 | Jahangir | Creates purchase requisition; selects preferred vendor (Global Parts BD) | Inventory: Requisition form |
| 4 | Nabil | Receives requisition in Procurement module; requests quotes from 2 additional vendors | Procurement: RFQ module |
| 5 | Nabil | Receives 3 quotes; system shows side-by-side price comparison | Procurement: Quote comparison |
| 6 | Nabil | Selects lowest-price qualified vendor; creates PO for 50 units | Procurement: PO creation |
| 7 | Vendor | Receives PO via Vendor Portal; confirms delivery date: 3 days | Vendor Portal: PO confirmation |
| 8 | [3 days later] | Warehouse staff receives goods; scans each unit against PO | Inventory: GRN via scanner |
| 9 | System | Stock updated: 50 units added; alert cleared; Jahangir notified | Inventory: Real-time update |
| 10 | System | Three-way match: PO vs. GRN vs. vendor invoice — all match; AP triggered | Finance: AP auto-match |

---

## Journey 11: CEO Monthly Business Review

**Actor(s):** Mahmud Hassan (CEO)
**Trigger:** First Monday of the month — reviewing February 2026 performance

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | CEO | Opens analytics dashboard on iPad; selects "Executive Dashboard — February 2026" | Analytics: Executive dashboard |
| 2 | System | Shows: Revenue BDT 1.87 Crore (↑12.3% MoM), Jobs Completed: 8,342, CSAT: 4.4/5 | Analytics: KPI tiles |
| 3 | CEO | Notes Technician Utilization 73% (target 80%); taps to investigate | Analytics: Utilization drill-down |
| 4 | System | Shows utilization by division: Chittagong 61%, Dhaka 79%, Sylhet 82% | Analytics: Regional breakdown |
| 5 | CEO | Drills into Chittagong: 3 branches under-performing; Halishahar branch worst | Analytics: Branch drill-down |
| 6 | CEO | Reviews Halishahar: high technician absenteeism (6 days in Feb) | HR analytics: Attendance |
| 7 | CEO | Reviews Revenue Growth: IT Equipment ↑18%, Home Appliance ↑9%, Mobile ↑6% | Analytics: Revenue by category |
| 8 | CEO | Exports executive summary as PDF; shares with board via email | Analytics: Export + share |

**Total review time:** 12 minutes (vs. waiting 10 days for monthly reports)

---

## Journey 12: New Technician Onboarding

**Actor(s):** New Technician (Day 1) + HR Officer Sonia
**Trigger:** New junior technician joins Sylhet branch

| Step | Who | Action | System Touchpoint |
|------|-----|--------|------------------|
| 1 | Sonia | Creates employee record; assigns role "Junior Technician"; branch = Sylhet | HR module: Employee creation |
| 2 | System | Generates employee ID; sends welcome SMS with app download link and temp password | Notification + HR |
| 3 | New tech | Downloads technician app; logs in; sees onboarding wizard | Technician PWA: Onboarding wizard |
| 4 | Wizard | Step 1: Profile completion (photo, certifications, skills) | Technician PWA |
| 5 | Wizard | Step 2: 15-minute interactive tutorial: how to accept jobs, check-in, document | Technician PWA: Training mode |
| 6 | Wizard | Step 3: Demo job completed in sandbox (no real customer) | Technician PWA: Sandbox mode |
| 7 | System | Wizard completed → access to live job list unlocked | FSM: Activation |
| 8 | Sonia | Assigns first 2 shadow jobs (with senior technician) via dispatch system | FSM: Shadow assignment flag |

---

# Section 12 — Usability Requirements

## 12.1 Performance Standards

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Page load (desktop/WiFi) | ≤ 2 seconds (95th percentile) | Service center agents handle queues; lag causes customer wait |
| Page load (mobile/4G) | ≤ 3 seconds (95th percentile) | Field technician app on field network |
| Page load (mobile/2G) | ≤ 8 seconds (95th percentile) | Rural Bangladesh connectivity |
| Search response | ≤ 1 second | Customer lookup at front desk must be instant |
| Form save | ≤ 2 seconds | Technician cannot wait during job documentation |
| Report generation (standard) | ≤ 5 seconds | Managers need immediate access |
| Report generation (large, 1000+ records) | ≤ 30 seconds with progress indicator | Complex financial reports |
| Dashboard refresh | ≤ 3 seconds | Ops dashboard must always show current state |

## 12.2 Navigation & Discoverability

| Requirement | Standard |
|-------------|---------|
| Maximum clicks to any function | 3 clicks from main menu |
| Primary navigation | Maximum 7 top-level items (Miller's Law) |
| Breadcrumb navigation | All drill-down screens must show breadcrumb |
| Back navigation | Browser back button must always work correctly |
| Search | Global search bar accessible from every screen |
| Recent items | Last 5 visited records accessible from navigation |
| Keyboard shortcuts | Power users: Ctrl+N (new record), Ctrl+S (save), Ctrl+F (search) |

## 12.3 Mobile-First Design Requirements

| Requirement | Standard |
|-------------|---------|
| Minimum touch target size | 44 × 44 pixels (Apple HIG / Material Design) |
| Navigation position | Bottom navigation bar (thumb-accessible) for technician app |
| Scroll direction | Single-direction scrolling per screen; no horizontal scroll |
| Font size minimum | 16px body text on mobile; 14px on desktop |
| Form inputs | Full-width on mobile; optimized keyboard type per input (numeric, email, etc.) |
| Swipe gestures | Left swipe on job card: quick actions (Check-in / Complete / Escalate) |
| Portrait/landscape | App functional in both orientations |

## 12.4 Error Handling & Feedback

| Scenario | Requirement |
|----------|------------|
| Form validation error | Inline error messages, adjacent to field, in Bengali and English |
| Required field missing | Field highlighted red; "Required" message before any submission |
| System error (500) | User-friendly error message; no technical jargon; option to report issue |
| Offline state | Clear "Offline Mode" banner; queued actions count shown |
| Long operation | Progress indicator for any action >2 seconds |
| Successful save | Green confirmation toast notification (3 seconds auto-dismiss) |
| Destructive actions | Confirmation dialog: "Are you sure?" with item name in message |

## 12.5 Accessibility (WCAG 2.1 AA)

| Requirement | Standard |
|-------------|---------|
| Color contrast | Minimum 4.5:1 for normal text, 3:1 for large text |
| Non-color indicators | Never use color as the only differentiator (also use icon/text) |
| Screen reader | All interactive elements have aria-label |
| Keyboard navigation | All functions accessible by keyboard only (Tab, Enter, Escape) |
| Focus indicators | Visible focus ring on all interactive elements |
| Images | All images have meaningful alt text |
| Form labels | Every form input has a visible, programmatically associated label |
| Video/audio | Not applicable (no media content in ERP) |

## 12.6 Consistent Design Language

- All screens use a unified design system (shadcn/ui or equivalent)
- Primary action button: always top-right or bottom of form
- Destructive action button: always styled in red
- Status badges: consistent color coding across all modules (Green=Active/Complete, Red=Overdue/Error, Amber=Warning/Pending, Blue=In Progress)
- Data tables: consistent column alignment (numbers right-aligned, text left-aligned)
- Date format: DD/MM/YYYY consistently throughout all modules

---

# Section 13 — Localization & Bangladesh-Specific Requirements

## 13.1 Language Support

| Requirement | Specification |
|-------------|--------------|
| Supported languages | Bengali (bn-BD) and English (en-US) |
| Default language | Bengali (bd-BD) |
| Language toggle | Available on every screen (header); user preference saved to account |
| Completeness | 100% of UI strings translated; no English fallback visible to Bengali users |
| Technical terms | Use standard Bangla IT terminology; provide glossary tooltip for specialized terms |
| Error messages | Translated to Bengali with professional language (not machine-translated) |
| Reports | Report headers and labels available in both languages |

## 13.2 Bengali Language Input

| Requirement | Specification |
|-------------|--------------|
| Keyboard input | Support Avro and Bijoy keyboard layouts |
| Voice-to-text | Bengali voice input for technician job notes (Android native API) |
| Search | Search queries accepted in both Bengali and English simultaneously |
| SMS content | All outbound SMS composed in Bengali by default |
| WhatsApp | WhatsApp message templates in Bengali |
| Font rendering | Kalpurush or SolaimanLipi font; minimum 16px for readability |

## 13.3 Date, Time & Number Formatting

| Format | Specification |
|--------|--------------|
| Date display | DD/MM/YYYY (e.g., 18/03/2026) |
| Date input | Calendar picker with DD/MM/YYYY format |
| Time | 12-hour format with AM/PM (standard in Bangladesh) |
| Currency | BDT with ৳ symbol; comma separator for thousands (৳1,23,456 — Bangladesh lakhs format) |
| Phone numbers | Accept both +880XXXXXXXXXX and 01XXXXXXXXX formats |
| Percentage | Display as XX.X% |

## 13.4 Bangladesh Regulatory Compliance

| Requirement | Specification |
|-------------|--------------|
| VAT Invoice (Mushak 6.3) | Invoice format compliant with NBR FY2024-25 Mushak 6.3 template |
| VAT Rate | Standard 15% VAT; zero-rated services configurable |
| BIN/TIN fields | BIN (Business Identification Number) and TIN fields on all business invoices |
| NID validation | 10 or 17-digit NID format accepted for customer registration |
| BEFTN | Bangladesh Electronic Funds Transfer Network format for salary payments |
| Bangladesh Labour Act | Leave entitlements, overtime rules, and termination pay compliant with Labour Act 2006 |
| ICT Act | Data handling and storage compliant with Bangladesh ICT Act 2006 (Amendment 2013) |

## 13.5 Payment Methods

| Payment Method | Integration Requirement |
|----------------|------------------------|
| bKash | bKash Merchant Payment API; OTP confirmation required |
| Nagad | Nagad Merchant API; direct debit support |
| Rocket (DBBL Mobile Banking) | Rocket API |
| SSLCOMMERZ | All VISA, Mastercard, local bank debit cards; installment options |
| Cash | Manual entry with cash receipt print |
| Bank Transfer | BEFTN reference number field on invoice |

## 13.6 Connectivity & Offline Requirements

| Requirement | Specification |
|-------------|--------------|
| Technician app offline duration | Must operate for 24 hours without any connectivity |
| Data sync on reconnect | Automatic sync within 30 seconds of connection restored |
| Offline data scope | Job list, customer data, device history, parts catalog, checklists |
| Offline actions supported | Check-in, status update, job documentation, payment collection, photo capture |
| Low-bandwidth optimization | Assets compressed; lazy loading; API responses paginated; images ≤200KB |
| Service worker | PWA service worker pre-caches critical assets (Serwist) |

## 13.7 Bangladesh Geography

| Requirement | Specification |
|-------------|--------------|
| Administrative divisions | All 8 Bangladesh divisions supported in address fields |
| Districts | All 64 districts available in district dropdown |
| Upazila | Upazila/Thana field available |
| Postal code | 4-digit Bangladesh postal code field |
| Google Maps | Bangladesh-specific map tiles; all major cities covered |
| Service zone mapping | Service zones defined by Dhaka zones (North/South/Central) and division capitals |

---

# Section 14 — Notification & Communication Requirements

## 14.1 Notification Channels

| Channel | Supported | Use Case |
|---------|-----------|---------|
| SMS | Required | All customers; all critical alerts; reach even non-smartphone users |
| In-App Push (PWA) | Required | Technicians, agents, managers (portal users) |
| Email | Required | Invoices, reports, contract renewals, corporate clients |
| WhatsApp (via API) | Required | Customer booking confirmations, tracking links, feedback requests |
| In-System Notification | Required | All internal staff; non-urgent alerts |

## 14.2 Event-Triggered Notifications

### Customer Notifications

| Event | Channel | Language | Timing |
|-------|---------|---------|--------|
| Service order created | SMS + WhatsApp | Bengali | Immediate |
| Technician dispatched | SMS + WhatsApp | Bengali | On dispatch |
| Technician en route (ETA) | SMS | Bengali | When technician starts travel |
| Technician arrived | SMS | Bengali | On check-in |
| Job completed | SMS | Bengali | On job close |
| Invoice ready | Email + SMS | Bengali/English | On invoice generation |
| Device ready for collection (walk-in) | SMS | Bengali | On QC pass |
| Warranty expiry reminder | SMS + Email | Bengali | 30 days before expiry |
| AMC renewal reminder | SMS + Email | Bengali | 60 and 30 days before |
| Service feedback request | SMS | Bengali | 2 hours after job close |

### Technician Notifications

| Event | Channel | Timing |
|-------|---------|--------|
| New job assigned | Push + SMS | Immediate |
| Job reassigned | Push + SMS | Immediate |
| Job cancelled | Push | Immediate |
| Parts request approved/rejected | Push | Within 30 min |
| SLA warning (job near deadline) | Push (alarm) | 60 min before SLA |
| Customer message received | Push | Immediate |
| Monthly incentive calculated | In-app | Month end |

### Manager Notifications

| Event | Channel | Timing |
|-------|---------|--------|
| SLA breach (job exceeded deadline) | Push + Email | Immediate |
| High-priority complaint logged | Push + Email | Immediate |
| Technician not checked in 30 min after shift start | In-app | 30 min after start |
| Stock at reorder point (Branch Manager) | Email | Daily digest |
| Daily operations summary | Email | 8 PM daily |
| Weekly performance report | Email | Monday 8 AM |

## 14.3 Notification Preferences

- Each user can configure preferred channels per event category
- Quiet hours: No non-emergency notifications sent between 10 PM and 7 AM
- Emergency override: SLA breach alerts bypass quiet hours
- Digest mode: Non-urgent notifications bundled into daily digest (configurable)
- Unsubscribe: Customers can opt out of marketing communications; operational notifications mandatory

## 14.4 SMS Template Standards

All SMS templates must:
- Be in Bengali (primary) and English (optional)
- Include job reference number
- Be ≤160 characters (1 SMS) for standard notifications
- Include opt-out instruction for promotional SMS ("Reply STOP to unsubscribe")
- Be pre-approved by Bangladesh Telecommunication Regulatory Commission (BTRC) sender ID registered as "1000FIX"

---

# Section 15 — Transition Requirements (User Adoption)

## 15.1 Training Plan by Role

| Role | Training Hours | Format | Language | Trainer | Timeline |
|------|---------------|--------|---------|--------|---------|
| Service Center Agent | 16h | Hands-on at workstation | Bengali | Super-user from each branch | Week before go-live |
| Field Technician (Senior) | 8h | App walkthrough + demo jobs | Bengali | Peer trainer | 5 days pre-go-live |
| Field Technician (Junior) | 12h | Guided tutorial + sandbox | Bengali | Senior technician | 5 days pre-go-live |
| Dispatch Manager | 8h | Scenario-based training | English/Bengali | ERP vendor trainer | 1 week pre-go-live |
| Branch Manager | 6h | Dashboard and approval workflows | Bengali | BA team | 1 week pre-go-live |
| Operations Manager | 4h | Analytics and reporting | English/Bengali | ERP vendor trainer | 1 week pre-go-live |
| Finance Officer/Manager | 12h | Finance module + Mushak invoicing | Bengali | ERP vendor finance specialist | 2 weeks pre-go-live |
| HR Officer/Manager | 8h | HR + Payroll module | Bengali | ERP vendor HR specialist | 2 weeks pre-go-live |
| Inventory/Procurement | 8h | Inventory and PO workflows | Bengali | ERP vendor trainer | 1 week pre-go-live |
| IT Administrator | 24h | System admin, user management, security | English | ERP vendor technical team | 4 weeks pre-go-live |
| Corporate Clients | 2h | B2B portal webinar | English | Account manager | 1 week before B2B launch |

## 15.2 Training Materials Required

| Material | Description | Format | Language |
|----------|-------------|--------|---------|
| Quick Reference Card (QRC) | 1-page laminated guide for top 10 daily tasks | Print + PDF | Bengali |
| Role-Based User Manual | Step-by-step for all functions per role | PDF | Bengali + English |
| Video Tutorials (10–15 min each) | Screen recordings for each key workflow | MP4 | Bengali narration |
| In-App Tooltips | Contextual help text on all complex fields | In-app | Bengali |
| Guided Onboarding Wizard | First-login interactive tutorial per role | In-app | Bengali |
| FAQ Document | 50 most common user questions per role | PDF + in-app | Bengali |
| Escalation Contact List | Who to call for each type of ERP issue | Print | Bengali |

## 15.3 Super-User Program

- Minimum 1 designated super-user per service branch (51 branches)
- Super-users trained 1 week ahead of standard user training
- Super-users are first point of contact for branch-level ERP issues
- Super-users receive 8-hour advanced training (all modules affecting their branch)
- Super-user role acknowledged in HR system; access to super-user support channel
- Monthly super-user call (30 min) for issue sharing and tips

## 15.4 Parallel Run Period

| Phase | Duration | Description |
|-------|---------|-------------|
| Shadow running | 2 weeks | ERP runs alongside legacy; results compared daily |
| Primary with fallback | 2 weeks | ERP is primary; legacy kept available for emergency fallback |
| ERP-only | Ongoing | Legacy systems decommissioned after parallel run complete |

**Parallel run success criteria:** ≤5% discrepancy between ERP and legacy data across all metrics

## 15.5 User Adoption KPIs

| KPI | Target | Measurement Method | Timeline |
|-----|--------|-------------------|---------|
| Service orders created via ERP | 100% of all jobs | System count | Day 1 post-go-live |
| Field technicians active on app | ≥90% of assigned technicians | Daily app logins | Day 30 |
| Jobs documented via app (vs. paper) | ≥85% | Digital signatures on jobs | Day 30 |
| Customers self-booking online | ≥50% | Portal booking % | Day 60 |
| Invoices generated from ERP | 100% | Invoice system source | Day 1 |
| Monthly payroll via ERP | 100% | Payroll module usage | Month 2 |
| System Usability Scale (SUS) score | ≥75 average across all roles | Post-training survey | Day 45 |

---

# Section 16 — User Acceptance Criteria

## 16.1 Portal-Level UAT Sign-Off Criteria

### Customer Self-Service Portal
- [ ] 3-step booking completed in ≤3 minutes by 10 test users unfamiliar with the system
- [ ] Real-time technician tracking visible within 60 seconds of dispatch
- [ ] bKash payment processed end-to-end without error in test environment
- [ ] Service history and digital invoice download functional for all test users
- [ ] Bengali UI fully displayed with no English fallback on any screen
- [ ] Portal accessible on iPhone, Android, and mobile Chrome; no layout breaks

### Technician Mobile PWA
- [ ] Job list loads by 7:30 AM in test scenario
- [ ] App operates offline for 4 hours in controlled test; all queued actions sync on reconnect
- [ ] Job documentation (10 data points) completed in ≤5 minutes by 10 test technicians
- [ ] GPS check-in validates location within 100m of customer address
- [ ] Parts catalog search returns result in ≤2 seconds in offline mode
- [ ] Push notifications received within 30 seconds of dispatch in test

### Admin Operations Portal
- [ ] Dispatch console loads in ≤2 seconds with 50 active jobs in test data
- [ ] AI dispatch recommendation covers ≥80% of test jobs correctly
- [ ] Live technician map refreshes every 30 seconds confirmed by test
- [ ] SLA breach alert fires at T-60 minutes in test scenario
- [ ] Batch approval of 20 jobs completed in ≤2 minutes

### Finance Module
- [ ] Mushak 6.3 invoice generated from completed service order in ≤5 seconds
- [ ] Invoice format validated against NBR Mushak 6.3 template by finance team
- [ ] Daily reconciliation screen loads with 100 test transactions in ≤3 seconds
- [ ] BEFTN payroll file format validated by test bank submission

### HR Module
- [ ] Payroll calculation for 500-employee test dataset completes in ≤5 minutes
- [ ] Leave application routed to line manager and approved within test workflow
- [ ] Attendance integration tested: biometric data imported without errors

## 16.2 Usability Testing Pass Criteria

| Test | Method | Pass Criterion |
|------|--------|---------------|
| System Usability Scale (SUS) | Post-training survey (10 questions) per role | SUS score ≥ 75 for all roles |
| Task Completion Rate | Observed usability test: 10 tasks per role | ≥ 90% task completion without assistance |
| Error Rate | Count of errors during usability test | ≤ 2 unrecoverable errors per user per test |
| Time on Task | Service order intake, job documentation, invoice generation | Within specified time targets (Sections 5.1–5.5) |
| Bengali UI acceptance | Observed with Bengali-primary users | 0 English-only fallback screens reported |

## 16.3 Performance UAC

| Scenario | Acceptance Criterion |
|----------|---------------------|
| 500 concurrent users | Page load ≤3 seconds (95th percentile) |
| Peak dispatch hour (8–9 AM): 100 simultaneous dispatchers | Dispatch console load ≤2 seconds |
| 50,000 service orders in DB | Standard report generation ≤5 seconds |
| 250,000 customer records in CRM | Customer search returns result ≤1 second |
| Technician app offline 4 hours | Zero data loss on sync; all queued actions applied correctly |

## 16.4 Go-Live Readiness Checklist

### User Readiness
- [ ] 100% of Day-1 users (agents, dispatchers) trained and certified
- [ ] 100% of field technicians have app installed and account activated
- [ ] All branch super-users identified and trained
- [ ] Quick Reference Cards printed and distributed to all service centers
- [ ] Help desk support line staffed for go-live week (extended hours)

### Data Readiness
- [ ] Customer master data migrated and verified (≤0.5% error rate)
- [ ] Product/device catalog migrated
- [ ] Open service orders migrated from legacy system
- [ ] Technician profiles and certifications loaded
- [ ] Chart of accounts configured and approved by Finance Manager
- [ ] Initial inventory counts loaded for all 51 branches

### System Readiness
- [ ] All integrations tested end-to-end (bKash, Nagad, SMS gateway, Google Maps, brand partner APIs)
- [ ] User accounts created for 100% of go-live users
- [ ] Role-based access verified for each role (5 users per role tested)
- [ ] Backup and recovery tested: restore from backup in ≤4 hours
- [ ] Security scan completed: no critical/high vulnerabilities
- [ ] Performance load test passed at 150% of expected peak load

---

# Section 17 — Assumptions & Constraints

## 17.1 Assumptions

| ID | Assumption | Impact if False |
|----|-----------|----------------|
| A-01 | All field technicians will be provided company Android smartphones (Android 11+) | Technician app may not be usable on personal devices |
| A-02 | All service centers have stable WiFi internet (minimum 10 Mbps) for desktop operations | Admin portal performance will degrade |
| A-03 | All customers have a mobile phone number (at minimum feature phone with SMS) | SMS-based communications not deliverable |
| A-04 | Biometric attendance devices at all branches will be integrated via API | Manual attendance entry required, increasing HR workload |
| A-05 | Preferred ERP vendor provides REST APIs for all modules | Integration with web portal platform may require additional development |
| A-06 | Brand partner warranty APIs (Dell, Samsung, HP, etc.) are accessible and documented | Warranty status check will require manual brand portal login |
| A-07 | Customers who book online have internet data on their smartphones | Online booking adoption target may not be met |
| A-08 | Corporate clients have designated IT-literate portal contact persons | B2B portal onboarding support requirements will increase |
| A-09 | NBR's Mushak invoice specifications for FY2025-26 do not change during implementation | Invoice module may require re-configuration |
| A-10 | 1000FiX's existing PostgreSQL 16 database can be integrated with the selected ERP via API | Integration architecture may need complete re-design |

## 17.2 Constraints

| ID | Constraint | Category |
|----|-----------|---------|
| C-01 | ERP system budget ceiling: USD 150,000–350,000 (3-year TCO) | Budget |
| C-02 | Full system deployment within 18 months | Timeline |
| C-03 | Must integrate with existing Next.js 15 / Payload CMS 3 / PostgreSQL 16 platform | Technology |
| C-04 | No disruption to operations during Eid-ul-Fitr and Eid-ul-Adha (peak service periods) | Operations |
| C-05 | Bangladesh NBR Mushak invoice format must be supported natively | Regulatory |
| C-06 | Bangladesh Labour Act 2006 compliance for payroll module | Regulatory |
| C-07 | Bangladesh ICT Act 2006 data storage and privacy requirements | Regulatory |
| C-08 | Technician app must work on 3G minimum; no required WiFi dependency in field | Technical |
| C-09 | System must support Bengali language throughout; no English-only critical functions | Localization |
| C-10 | Payment processing must use Bangladesh-approved gateways (bKash, Nagad, SSLCOMMERZ) | Regulatory/Technical |
| C-11 | User training budget: ≤5% of total ERP project cost | Budget |

---

# Section 18 — Appendices

## Appendix A — User Story ID Reference Index

| Module | ID Range | Story Count | Section |
|--------|---------|-------------|---------|
| Service & Repair Management | US-SRM-001 to US-SRM-015+ | 15 | Section 6 |
| Field Service Management | US-FSM-001 to US-FSM-013+ | 13 | Section 7 |
| Inventory Management | US-INV-001 to US-INV-006+ | 6 | Section 8 |
| CRM | US-CRM-001 to US-CRM-004+ | 4 | Section 9.1 |
| Finance | US-FIN-001 to US-FIN-005+ | 5 | Section 9.2 |
| HR Management | US-HRM-001 to US-HRM-004+ | 4 | Section 9.3 |
| Contract & Warranty | US-CWM-001 to US-CWM-002+ | 2 | Section 9.4 |
| Customer Self-Service Portal | US-CSP-001 to US-CSP-005+ | 5 | Section 10.1 |
| Technician Mobile PWA | US-TMP-001 to US-TMP-003+ | 3 | Section 10.2 |
| Admin Operations Portal | US-AOP-001 to US-AOP-003+ | 3 | Section 10.3 |
| Corporate B2B Portal | US-CBP-001 to US-CBP-002+ | 2 | Section 10.4 |
| Vendor & Partner Portal | US-VPP-001 to US-VPP-002+ | 2 | Section 10.5 |
| Analytics Dashboard | US-ADB-001 to US-ADB-003+ | 3 | Section 10.6 |
| **TOTAL** | | **67+ core stories** | |

---

## Appendix B — User Requirements Traceability Matrix (RTM)

| URD Story ID | Story Summary | BRD Requirement | RFP Section | Business Objective |
|-------------|--------------|----------------|------------|-------------------|
| US-SRM-001 | Auto-fill customer on phone lookup | BR-SRM-001 | 5.1 (CRM) | BO-03 (Customer Sat) |
| US-SRM-002 | Warranty check via barcode scan | BR-SRM-002 | 5.1 (Service Mgmt) | BO-02 (Efficiency) |
| US-SRM-005 | Device registration | BR-SRM-005 | 5.1 (CRM) | BO-03 (Customer Sat) |
| US-SRM-007 | AI technician recommendation | BR-SRM-011 | 5.2 (Field Service) | BO-02 (Efficiency) |
| US-SRM-010 | Mushak VAT invoice at collection | BR-SRM-021 | 5.5 (Finance) | BO-06 (Compliance) |
| US-FSM-001 | Daily job list with optimized route | BR-FSM-001 | 5.2 (Field Service) | BO-02 (Efficiency) |
| US-FSM-003 | GPS check-in and customer SMS | BR-FSM-003 | 5.2 (Field Service) | BO-03 (Customer Sat) |
| US-FSM-009 | 24-hour offline mode | BR-FSM-015 | 7.3 (Technical) | BO-02 (Efficiency) |
| US-INV-001 | Real-time stock visibility | BR-INV-001 | 5.3 (Inventory) | BO-04 (Inventory) |
| US-INV-002 | Auto reorder alert | BR-INV-002 | 5.3 (Inventory) | BO-04 (Inventory) |
| US-FIN-001 | 1-click Mushak invoice | BR-FIN-001 | 5.5 (Finance) | BO-06 (Compliance) |
| US-FIN-002 | Daily payment reconciliation | BR-FIN-002 | 5.5 (Finance) | BO-05 (Finance) |
| US-HRM-002 | Monthly payroll batch processing | BR-HRM-002 | 5.6 (HR) | BO-07 (HR) |
| US-CSP-001 | 3-step online booking | BR-CSP-001 | 6.1 (Customer Portal) | BO-01 (Digital) |
| US-CSP-002 | Real-time technician tracking | BR-CSP-002 | 6.1 (Customer Portal) | BO-03 (Customer Sat) |
| US-ADB-001 | CEO executive dashboard | BR-ADB-001 | 6.6 (Analytics) | BO-08 (Visibility) |

---

## Appendix C — Persona Summary Table

| # | Persona Name | Role | Tech Level | Language | Primary Device |
|---|-------------|------|-----------|---------|---------------|
| 1 | Rashida Begum | Service Center Agent | 3/5 | Bengali | Desktop |
| 2 | Farida Rahman | Dispatch Manager | 4/5 | Bengali/English | Desktop + Phone |
| 3 | Kabir Hossain | Senior Technician | 3/5 | Bengali | Android Phone |
| 4 | Shakib Islam | Junior Technician | 3/5 | Bengali | Android Phone |
| 5 | Arif Chowdhury | Branch Manager | 3/5 | Bengali | Desktop + Phone |
| 6 | Nasreen Sultana | Operations Manager | 4/5 | Bengali/English | Laptop |
| 7 | Mitu Akter | Finance Officer | 3/5 | Bengali | Desktop |
| 8 | Kamal Uddin | Finance Manager | 3/5 | Bengali/English | Laptop |
| 9 | Sonia Parvin | HR Officer | 3/5 | Bengali | Desktop |
| 10 | Rahim Bhuiyan | HR Manager | 3/5 | Bengali/English | Laptop |
| 11 | Jahangir Hossain | Inventory Manager | 3/5 | Bengali | Desktop + Tablet |
| 12 | Nabil Islam | Procurement Officer | 4/5 | Bengali/English | Desktop |
| 13 | Tanvir Ahmed | IT Administrator | 5/5 | Bengali/English | Laptop |
| 14 | Imran Khan | Corporate Facility Mgr | 4/5 | English/Bengali | Laptop + iPhone |
| 15 | Salman Sheikh | Parts Supplier | 2/5 | Bengali | Phone + Basic PC |
| 16 | Tanvir Mahmud | Brand Partner Rep | 4/5 | English/Bengali | Laptop |
| 17 | Rafiq Ahmed | Customer (Tech-Savvy) | 5/5 | English/Bengali | iPhone/Laptop |
| 18 | Tahmina Khatun | Customer (Urban) | 3/5 | Bengali | Android Phone |
| 19 | Abdul Karim | Customer (Elderly) | 1/5 | Bengali | Basic Phone |
| 20 | Mahmud Hassan | CEO | 3/5 | Bengali/English | iPad + Phone |

---

## Appendix D — Existing Portal URD Cross-Reference

The existing portal URD (`03_URD_User_Requirements_Document.md`, v1.0, January 2026) covers the 8-portal web platform for customer-facing and agent-facing web interactions. This ERP URD extends and complements that document:

| Aspect | Existing Portal URD | This ERP URD |
|--------|--------------------|-----------------------------|
| Scope | 8 web portals, customer journeys | 11 ERP modules + 6 portals, all 20 user roles |
| Personas | 12 (customer-centric) | 20 (full internal + external coverage) |
| User Stories | 150+ (portal interactions) | 67+ (ERP operations + portal user stories) |
| Journey Maps | 8 (customer-focused) | 12 (all operational journeys) |
| Backend Operations | Not covered | Fully covered (Finance, HR, Inventory, etc.) |
| Language | English document | Bengali-primary UI, bilingual document |
| Combined Coverage | Together: complete user requirements for entire platform | |

---

## Appendix E — Glossary

| Term | Definition |
|------|-----------|
| AC | Acceptance Criteria — testable conditions for user story completion |
| AMC | Annual Maintenance Contract — corporate equipment maintenance agreement |
| BEFTN | Bangladesh Electronic Funds Transfer Network — bank salary transfer system |
| BDT | Bangladeshi Taka (৳) — official currency |
| BIN | Business Identification Number — NBR-issued tax identifier for businesses |
| BTRC | Bangladesh Telecommunication Regulatory Commission |
| CRM | Customer Relationship Management module |
| CSAT | Customer Satisfaction Score (1–5 scale) |
| ERP | Enterprise Resource Planning — integrated business management system |
| ESS | Employee Self-Service — employee-facing HR portal |
| FSM | Field Service Management module |
| GRN | Goods Receipt Note — document confirming goods received against PO |
| HRM | Human Resource Management module |
| IIBA | International Institute of Business Analysis |
| Mushak | Bangla term for VAT; Mushak 6.3 = NBR-mandated VAT invoice format |
| NBR | National Board of Revenue — Bangladesh tax authority |
| NID | National Identity Document — Bangladesh national ID card |
| P1/P2/P3 | Priority levels: P1=Must-Have, P2=Important, P3=Nice-to-Have |
| PWA | Progressive Web App — web app with native-app features, offline capability |
| RAMC | Residential Annual Maintenance Contract |
| RBAC | Role-Based Access Control |
| RFP | Request for Proposal — vendor bidding document |
| SLA | Service Level Agreement — time targets for service delivery |
| SRM | Service & Repair Management module |
| SUS | System Usability Scale — standardized 10-question usability questionnaire (score 0–100) |
| TAT | Turnaround Time — time from service order creation to completion |
| TIN | Tax Identification Number — individual NBR tax identifier |
| UAT | User Acceptance Testing |
| URD | User Requirements Document — this document |
| WCAG | Web Content Accessibility Guidelines (v2.1 AA standard required) |

---

## Appendix F — Reference Documents

| Document | Reference Number | Location | Version |
|----------|----------------|---------|--------|
| ERP System RFP | 1000FIX-ERP-RFP-2026-001 | `ERP system for 1000 fix\1000FiX_ERP_System_Comprehensive_RFP.md` | 1.0 |
| ERP System BRD | 1000FIX-ERP-BRD-2026-001 | `ERP system for 1000 fix\1000FiX_ERP_System_Comprehensive_BRD.md` | 1.0 |
| Company Profile | — | `1000FiX_Services_Company_Profile.md` | Jan 2026 |
| Portal BRD v2.0 | — | `Intergrated_web_portal\project_requirement_document\01_BRD_Business_Requirements_Document_v2.0.md` | 2.0 |
| Portal URD | — | `Intergrated_web_portal\project_requirement_document\03_URD_User_Requirements_Document.md` | 1.0 |
| Portal SRS | — | `Intergrated_web_portal\project_requirement_document\04_SRS_Software_Requirements_Specification.md` | 1.0 |
| Technology Stack | — | `Intergrated_web_portal\project_requirement_document\05_Technology_Stack_Document.md` | 1.0 |
| Use Case Library | — | `Marketing_1\1000FIX_Smart_Portal_System_Use_Cases.md` | 1.0 |
| Digital Transformation White Paper | — | `Marketing_1\1000FIX_Digital_Transformation_White_Paper_Service_Industry.md` | 1.0 |
| IIBA BABOK v3 | — | International Institute of Business Analysis, 2015 | 3.0 |
| NBR Mushak 6.3 Template | — | National Board of Revenue, Bangladesh | FY2024-25 |

---

*Document Reference: 1000FIX-ERP-URD-2026-001*
*Version: 1.0 | Date: March 18, 2026*
*Classification: CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited | 586/1, Begum Rokeya Sarani, Shewrapara, Mirpur, Dhaka-1216*

---
*End of Document*
