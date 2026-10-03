---
id: FIX-ERP2-010
title: Portal & Application Suite Specification (P01–P12)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Portal & Application Suite Specification
# 12 Portals and Applications (P01–P12)

---

## 1. Principle

The ERP is the **system of record**. Portals and applications are **surfaces** onto it.

| Rule | Consequence |
|---|---|
| No portal holds authoritative state | A portal may cache for performance, never for truth |
| No portal implements business rules | Rules live in the ERP module that owns the object |
| Every portal authenticates through M29 | One identity, one session policy, one audit trail |
| Every portal calls through the M28 gateway | One place for rate limits, versioning and observability |
| Every portal is measured | Adoption, task completion and error rates are KPIs, not afterthoughts |

---

## 2. Suite Overview

| ID | Portal / Application | Users | Volume | Technology | Wave | New |
|---|---|---|---|---|:--:|:--:|
| P01 | Customer Self-Service Portal & Mobile App | Individual customers | 250,000+/month | Next.js 15 (web) + React Native (app) | W2 | |
| P02 | Technician Mobile Application | Field & workshop technicians | 200–400 | Flutter (Android primary, iOS secondary) | W2 | |
| P03 | Admin Operations Portal | Back-office & branch staff | 150–250 | Odoo Web (OWL 2) | W1 | |
| P04 | Corporate B2B Portal | Corporate & government clients | 500–2,000 | Next.js 15 | W4 | |
| P05 | Vendor & Supplier Portal | Parts vendors, couriers, sub-contractors | 200–500 | Odoo Portal + Next.js | W3 | |
| P06 | Analytics & Executive Dashboard | Management | 25–60 | Metabase + Grafana (embedded) | W4 | |
| **P07** | **Marketplace Seller Portal & App** | External engineers & shops | 500–2,000 | Next.js 15 + React Native | W7 | ★ |
| **P08** | **Brand Partner Portal** | 17+ brand partners | 50–150 | Next.js 15 | W4 | ★ |
| **P09** | **Logistics & Rider Application** | Riders, logistics coordinators, couriers | 50–200 | Flutter | W3 | ★ |
| **P10** | **Contact Centre Agent Console** | Contact centre agents & supervisors | 30–80 | Next.js 15 | W4 | ★ |
| **P11** | **Field Auditor & Quality Application** | Quality auditors, branch managers | 20–60 | Flutter | W5 | ★ |
| **P12** | **Partner & Referral Portal** | Alliance partners, referrers | 100–500 | Next.js 15 | W7 | ★ |

---

# P01 — Customer Self-Service Portal & Mobile Application

**Users:** individual customers · **Wave:** W2 (portal), W6 (native app)
**Backing modules:** M01, M02, M03, M06, M07, M08, M09, M10, M11, M12, M13, M14, M18, M20, M27

## Capability Set

| Area | Capabilities |
|---|---|
| **Account** | Register with phone/email OTP · social and biometric login · profile · multiple tagged addresses with saved GPS · household members · language preference · theme personalisation · notification preferences · consent management |
| **Devices** | Register devices by serial/IMEI/photo · view device history · warranty status · download device history report · transfer ownership |
| **Booking** | Book a service in ≤ 3 steps · choose delivery mode (walk-in, on-site, pick & drop, remote) · select slot · describe the fault with photos and voice · upfront price indication · reschedule and cancel |
| **Tracking** | Live status timeline · live technician map with ETA · technician name and photo · push, SMS and WhatsApp updates · public tracking link without login |
| **Approvals** | Review estimates · approve, part-approve or decline · e-sign · view revised estimates |
| **Payments** | Pay by bKash, Nagad, card and bank transfer · view invoices and receipts · payment history · saved payment methods · refund status |
| **Contracts** | View AMC/RAMC contracts · entitlement balance · scheduled visit calendar · renew · buy a new contract |
| **Warranty** | Check warranty · buy warranty extension and protection products · submit a claim · view claim status |
| **Loyalty** | Privilege membership status and benefits · points balance and history · redeem points · vouchers · referral link and rewards |
| **Shop** | Browse and buy parts, accessories and refurbished devices · rental booking · cart, checkout and order tracking · returns |
| **Trade-in** | Submit a trade-in request with photos · receive an offer · accept and arrange collection · get paid |
| **Data services** | Request data recovery · view case status · view backup subscription status · download destruction certificates |
| **Recycling** | Book an e-waste collection or find a drop-off point · earn points |
| **Support** | AI assistant in Bengali and English · live chat with an agent · call the hotline in-app · attach files · rate the conversation · receive transcript by email · in-app inbox of all notifications · knowledge base and FAQ |
| **Feedback** | Rate the service and technician on multiple parameters · write a review · raise a complaint and track it |

## Design Requirements

- Bengali-first, with English toggle; all content professionally translated, not machine-translated
- Works on a 3G connection; total first-load payload under 400 KB on the booking path
- Progressive Web App with offline shell and installability
- WCAG 2.1 AA
- Booking funnel conversion is the primary design KPI

## KPIs

| KPI | Baseline | Target |
|---|---|---|
| Online booking rate | 40% | 88% |
| Booking funnel conversion | unmeasured | > 72% |
| Self-service status checks (vs hotline calls) | ~0 | > 80% of status enquiries |
| Portal monthly active users | — | > 120,000 |
| App store rating | — | > 4.5 |

---

# P02 — Technician Mobile Application

**Users:** field and workshop technicians · **Wave:** W2
**Backing modules:** M01, M02, M03, M05, M06, M13, M14, M15, M17, M21, M22

## Capability Set

| Area | Capabilities |
|---|---|
| **Day** | Optimised job queue · accept/decline with reason · shift clock-in/out with geofence · leave request · daily summary |
| **Navigation** | Turn-by-turn navigation · route overview · automatic arrival detection |
| **Job execution** | Full job context and device history · guided diagnostic tree · fault coding · repair notes · time tracking (start/pause/resume/stop) |
| **Parts** | Van stock view · barcode/QR scan to consume · request parts not in van · return unused parts · van reconciliation |
| **Evidence** | Before/after photos with GPS and timestamp · short video · voice notes in Bengali · document scan |
| **Customer** | Estimate presentation and on-site approval · e-signature · on-site payment collection · receipt issue |
| **Quality** | QC checklist enforcement · test results capture · service report generation |
| **Workshop mode** | Bench assignment · WIP board · multi-job handling · repair-level (L1/L2/L3) workflows |
| **Logistics** | Device handover and collection scanning · custody confirmation |
| **Remote** | Launch a remote support session for eligible jobs |
| **Communication** | In-app messaging with dispatch and workshop · escalation request · panic/safety alert |
| **Knowledge** | Offline repair manuals, wiring diagrams and past repair notes |
| **Personal** | Own performance scorecard · earnings and incentive tracker · certification status and expiry · assigned training |

## Non-Negotiable Requirements

| # | Requirement |
|---|---|
| 1 | Full operation offline for 24 hours with no data loss |
| 2 | Sync within 30 seconds of reconnection, with 100% data integrity |
| 3 | Bengali user interface, complete — including error messages |
| 4 | Runs acceptably on a mid-range Android 11 device with 3 GB RAM |
| 5 | Battery consumption under 12% per 8-hour shift excluding navigation |
| 6 | Every state-changing action is queued locally and idempotent on the server |
| 7 | No feature requires a connection that a technician cannot complete offline |

## KPIs

| KPI | Target |
|---|---|
| Daily active usage among active technicians | > 95% |
| Job documentation time | < 5 minutes |
| Offline sync failures | Zero |
| Crash-free sessions | > 99.5% |
| Technician satisfaction with the app | > 4.2/5 |

---

# P03 — Admin Operations Portal

**Users:** service agents, dispatchers, branch managers, operations, finance, HR, inventory,
procurement, quality, IT · **Wave:** W1
**Backing modules:** all

## Capability Set

Delivered as role-scoped workspaces inside the Odoo web client, each opening on the work its
role actually does:

| Workspace | For | Opens On |
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

## Design Requirements

- Every workspace is reachable in one click from the home screen
- Any record reachable in ≤ 4 clicks from any starting point
- Bulk actions on every list view
- Keyboard-first operation for high-volume roles (intake, dispatch, finance)
- Screen density suited to a 1366×768 laptop — the most common branch hardware

## KPIs

| KPI | Target |
|---|---|
| Walk-in intake time | < 3 minutes |
| Dispatch of a full morning queue | < 10 minutes |
| Page load (standard screen) | < 2 seconds |
| Training time to competence (new agent) | < 4 hours |

---

# P04 — Corporate B2B Portal

**Users:** corporate and government client staff · **Wave:** W4
**Backing modules:** M05, M07, M08, M09, M11, M17, M20, M25, M27

## Capability Set

| Area | Capabilities |
|---|---|
| **Account** | Multi-user access under one corporate account · role assignment · multi-level approval chains (user → line manager → 1000FiX admin) · multiple sites and departments |
| **Asset estate** | View and manage the full registered asset estate · bulk upload and update · assign assets to sites, departments and users · retire and decommission |
| **Service** | Raise single or bulk service requests (CSV upload) · validate against contract coverage before submission · track every request · approve estimates within delegated authority |
| **Contracts** | View contracts and entitlements · consumption against entitlement · scheduled maintenance calendar · renewal quotations · amendments |
| **Managed services** | Estate health dashboard · open incidents · alert history · patch compliance · SLA attainment · service reports · schedule service reviews |
| **SLA** | Real-time SLA status per request · breach history · service credits earned |
| **Billing** | Consolidated invoices by cycle · invoice approval workflow · itemised breakdown by site, department and asset · payment · statements · dispute an invoice |
| **Reporting** | Scoped analytics on their own estate — volume, cost, downtime, TAT, top-failing assets — with export |
| **Procurement** | Order parts and services against agreed pricing · rental requests · trade-in and decommission projects |
| **Support** | Dedicated account manager contact · priority chat and phone · knowledge base |
| **Compliance** | Download destruction certificates, disposal certificates and service evidence packs |

## KPIs

| KPI | Target |
|---|---|
| Corporate clients actively using the portal | > 85% of contracted clients |
| Bulk requests submitted through the portal | > 70% of corporate requests |
| Bulk service request creation time | < 5 minutes |
| Invoice disputes | < 3% of consolidated invoices |
| Corporate client satisfaction | > 4.6/5 |

---

# P05 — Vendor & Supplier Portal

**Users:** parts vendors, courier partners, sub-contractors, recycling partners · **Wave:** W3
**Backing modules:** M03, M15, M16, M18, M20

## Capability Set

| Area | Capabilities |
|---|---|
| **Onboarding** | Register · submit documents · track approval · maintain profile, catalogue and banking details |
| **Sourcing** | Receive and respond to RFQs · submit quotations with price, lead time and validity |
| **Orders** | Receive POs · acknowledge or query · confirm delivery dates · submit advance shipping notices |
| **Delivery** | View expected receipts · see receipt and inspection outcomes · respond to rejections |
| **Invoicing** | Submit invoices against POs · track matching status · see payment schedule and remittance advice |
| **Returns** | Receive RTV notifications · issue credit notes · track return status |
| **Performance** | View own scorecard — on-time delivery, quality, responsiveness — with detail |
| **Logistics partners** | Receive consignment bookings · update status · upload POD · submit settlement claims |
| **Recycling partners** | Receive batch transfers · upload disposal certificates · report material recovery |

## KPIs

| KPI | Target |
|---|---|
| POs acknowledged through the portal | > 90% |
| Invoices submitted through the portal | > 85% |
| Vendor phone/email queries | −60% |
| RFQ response rate | > 75% |

---

# P06 — Analytics & Executive Dashboard

**Users:** executives, directors, branch and functional managers · **Wave:** W4
**Backing modules:** M25 (all data from all modules)

## Capability Set

| Area | Capabilities |
|---|---|
| **Executive** | Group performance across 14 revenue streams · revenue, margin, volume, cash, CSAT, utilisation · trend and forecast · drill from group to a single job |
| **Branch league** | Rank and compare all 51+ branches on every operational and financial dimension |
| **Functional** | Purpose-built dashboards for service, field, inventory, finance, HR, quality, warranty, contracts, marketplace and managed services |
| **Real-time** | Live operations board — open jobs, technicians on map, SLA countdowns, queue health, system health |
| **Self-service** | Build analyses on certified datasets without SQL, within row-level security |
| **Distribution** | Schedule and subscribe to reports; export to PDF, Excel and CSV |
| **Alerting** | Threshold and anomaly alerts delivered to the right role |
| **Mobile** | Key dashboards optimised for phone, for managers away from a desk |

## KPIs

| KPI | Target |
|---|---|
| Executive dashboard load | < 5 seconds |
| Weekly usage by managers | > 90% |
| Decisions made on live data rather than compiled spreadsheets | 100% of management reviews |
| Manual management reporting effort | −90% |

---

# P07 — Marketplace Seller Portal & Application ★

**Users:** external engineers (freelancers) and shops · **Wave:** W7
**Backing modules:** M11, M12, M15, M20, M22, M23, M27

## Capability Set

| Area | Capabilities |
|---|---|
| **Registration** | Register as a freelance engineer or a shop · submit NID, trade licence, references and work-sample images · verify phone and email by OTP · track approval · sign the agreement digitally · pay any registration fee · see registration expiry |
| **Profile** | Manage profile, skills, categories, service areas, working hours and photos · shop open/closed toggle |
| **Listings** | Create and manage service and product listings · pricing · availability · enable/disable individual listings · bulk listing management · own warehouse stock |
| **Work** | See broadcast jobs matching their profile · submit quotations · counter-bid · accept jobs · manage the job through to completion with evidence and customer sign-off |
| **Communication** | Chat with the customer on an open job · attach files · escalate to 1000FiX |
| **Earnings** | Wallet balance · earnings by job · commission and fee breakdown · statements · payout history and schedule · request payout |
| **Performance** | Own scorecard — acceptance rate, on-time rate, rating breakdown, rework, disputes · consequences of falling below threshold |
| **Reviews** | See customer reviews · respond once per review |
| **Growth** | Buy boost/top-listing placement for a period · buy page-targeted advertising · view impressions and clicks |
| **Standards** | Access required training and standards · acknowledge policy updates · see certification requirements per category |
| **Disputes** | Raise and respond to disputes with evidence |

## Governance Requirements

- A seller cannot transact until documents are verified, the agreement is signed and admin approval is granted
- Quality and evidence standards for marketplace jobs are identical to owned jobs
- Payouts are held for the defined period and blocked while a dispute is open
- Falling below the performance threshold reduces visibility automatically, then suspends

## KPIs

| KPI | Target |
|---|---|
| Approved active sellers | 500 by end of W8 |
| Seller onboarding completion rate | > 60% of started registrations |
| Seller monthly active rate | > 70% of approved sellers |
| Average seller rating | > 4.4/5 |
| Seller retention at 12 months | > 65% |

---

# P08 — Brand Partner Portal ★

**Users:** 17+ authorised brand partners · **Wave:** W4
**Backing modules:** M09, M15, M17, M23, M25

## Capability Set

| Area | Capabilities |
|---|---|
| **Claims** | Receive claim submissions with full evidence packs · approve, part-approve, reject with reason, or request more information · bulk actions |
| **Evidence** | View photographs, diagnostic reports, parts replaced, technician certification and purchase proof for any claim |
| **Reconciliation** | View submitted, approved and paid claims · upload remittance advice · resolve differences |
| **Consignment parts** | View parts supplied to 1000FiX · consumption reporting · replenishment requests · defective returns |
| **Rate cards** | Publish and version labour rates, parts pricing and claim rules |
| **Performance** | View 1000FiX service performance on their brand — volume, TAT, first-time fix, rework, CSAT, failure patterns by model |
| **Quality** | Raise quality concerns · view CAPA responses · schedule and conduct partner audits with evidence access |
| **Certification** | View the certification status of technicians authorised on their brand |
| **Communication** | Bulletins, technical notices and recall notifications to 1000FiX |

## KPIs

| KPI | Target |
|---|---|
| Claims submitted through the portal (vs email) | > 80% |
| Average claim decision time | < 10 days |
| Claim approval rate | > 92% |
| Brand partner satisfaction | > 4.5/5 |
| Days from service to reimbursement | < 45 |

---

# P09 — Logistics & Rider Application ★

**Users:** internal riders, logistics coordinators, courier partner staff · **Wave:** W3
**Backing modules:** M03, M13, M14, M15, M18

## Capability Set

| Area | Capabilities |
|---|---|
| **Manifest** | Daily optimised pickup and delivery manifest · route overview · reorder within constraints |
| **Collection** | Scan consignment · verify items against manifest · capture photos of items and packaging · seal number entry · customer OTP and signature · issue receipt |
| **Transit** | Update status · record exceptions (customer absent, address wrong, refused, damaged) · request rescheduling |
| **Delivery** | Verify recipient identity · scan handover · capture photo, OTP and signature · collect payment where applicable |
| **Custody** | Every handover recorded with GPS, timestamp and both parties' identity |
| **Cash** | Record cash collected on delivery · reconcile at end of shift |
| **Offline** | Full offline operation with queued sync |
| **Coordinator view (web)** | Real-time dashboard of pending, in-transit, delivered and exception consignments · assign to riders or courier partners · reschedule · monitor SLA · central vs branch team assignment |

## KPIs

| KPI | Target |
|---|---|
| POD capture completeness | 100% |
| On-time collection and delivery | > 93% |
| Custody breaks | Zero |
| Rider app offline reliability | 100% |

---

# P10 — Contact Centre Agent Console ★

**Users:** contact centre agents, team leaders, quality analysts · **Wave:** W4
**Backing modules:** M01, M05, M07, M08, M09, M11, M20, M23, M27

## Capability Set

| Area | Capabilities |
|---|---|
| **Queue** | Unified queue across voice, chat, WhatsApp, email, SMS and social · priority and SLA visible · presence and capacity management |
| **Context** | Automatic screen pop of Customer 360 on caller identification · full conversation history across channels · open jobs, contracts, entitlements and dues |
| **Handling** | Answer, hold, transfer, conference, consult · canned responses in Bengali and English · attachments · knowledge base search |
| **Action** | Create a service order, reschedule, quote, take payment, renew a contract, raise a complaint — without leaving the conversation |
| **Navigation** | Jump to any relevant ERP screen and return with the conversation intact |
| **Remote support** | Launch a remote assistance session with consent capture |
| **AI assist** | Suggested responses, next-best-action and article recommendations while the conversation is live |
| **Wrap-up** | Structured disposition coding · notes · follow-up task creation |
| **Quality** | Recording playback · quality scoring forms · coaching notes · agent feedback |
| **Supervision** | Live queue and agent status · service-level monitoring · barge-in and whisper on calls |

## KPIs

| KPI | Target |
|---|---|
| Average handling time | −25% vs baseline once established |
| First-contact resolution | > 78% |
| Agent screen switches per contact | < 3 |
| Disposition coding completeness | 100% |
| Agent satisfaction with tooling | > 4.2/5 |

---

# P11 — Field Auditor & Quality Application ★

**Users:** quality auditors, branch managers, regional managers · **Wave:** W5
**Backing modules:** M15, M17, M23, M24

## Capability Set

| Area | Capabilities |
|---|---|
| **Audit programme** | See assigned audits · schedule · scope and checklist |
| **Execution** | Complete audit checklists offline · capture photo and document evidence · record observations against clauses |
| **Findings** | Raise findings with classification and severity · link to processes, people and records · assign owners |
| **Verification** | Verify previously raised CAPAs on site |
| **Branch checks** | Cash spot checks · inventory spot counts · equipment and safety checks · 5S/housekeeping |
| **Marketplace** | Audit marketplace sellers against platform standards |
| **Reporting** | Generate the audit report on device · obtain the auditee's acknowledgement signature · sync to M23 |

## KPIs

| KPI | Target |
|---|---|
| Audit plan completion | 100% |
| Audits completed on mobile (vs paper) | 100% |
| Finding-to-CAPA cycle time | < 5 days |
| Evidence attached to findings | 100% |

---

# P12 — Partner & Referral Portal ★

**Users:** alliance partners, referral partners, corporate resellers · **Wave:** W7
**Backing modules:** M10, M12, M14, M20

## Capability Set

| Area | Capabilities |
|---|---|
| **Onboarding** | Apply, submit documents, sign the partner agreement, get approved |
| **Referral** | Generate and share referral links and codes · submit leads directly · track lead status through to conversion |
| **Benefits** | View the partner benefit schedule available to their members or customers |
| **Earnings** | Commission earned by referral · statements · payout schedule and history |
| **Co-marketing** | Access approved marketing materials · request co-branded campaigns · view campaign performance |
| **Reseller** | For resellers: view allocation of refurbished stock, pricing, place orders, track fulfilment and settlement |
| **Performance** | Leads submitted, conversion rate, revenue attributed, ranking |

## KPIs

| KPI | Target |
|---|---|
| Active referral partners | > 200 by end of W8 |
| Referral-attributed new customers | > 12% of new customers |
| Partner commission accuracy | 100% |
| Partner portal adoption | > 75% of approved partners |

---

## 3. Cross-Portal Standards

| # | Standard | Applies To |
|---|---|---|
| PS-01 | Single sign-on through M29; no portal maintains its own credential store | All |
| PS-02 | All API traffic through the M28 gateway with per-portal credentials and rate limits | All |
| PS-03 | Bengali and English throughout, with Bengali default on customer and field surfaces | All |
| PS-04 | WCAG 2.1 AA accessibility | All web portals |
| PS-05 | Responsive from 320 px upward; no horizontal scrolling | All web portals |
| PS-06 | Consistent 1000FiX design system — one component library, one token set | All |
| PS-07 | Works acceptably on a 3G connection; critical paths under 400 KB first load | P01, P02, P07, P09 |
| PS-08 | Offline-capable with queued sync | P02, P09, P11 |
| PS-09 | Every user-visible error states what happened and what to do next, in the user's language | All |
| PS-10 | Analytics instrumentation on every critical funnel, feeding M25 | All |
| PS-11 | No business rule implemented client-side; the client validates for convenience only | All |
| PS-12 | Session, idle timeout and MFA policy inherited from M29, not portal-specific | All |

---

## 4. Portal-to-Module Coverage Matrix

| | M01 | M02 | M03 | M04 | M05 | M06 | M07 | M08 | M09 | M10 | M11 | M12 | M13 | M14 | M15 | M16 | M17 | M18 | M19 | M20 | M21 | M22 | M23 | M24 | M25 | M26 | M27 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **P01** Customer | ● | ● | ● | | | ● | ● | ● | ● | ● | ● | ● | ● | ● | | | ● | ● | | ● | | | ● | ● | | | ● |
| **P02** Technician | ● | ● | ● | | ● | ● | | | ● | | | | ● | ● | ● | | ● | | | | ● | ● | ● | ● | ● | | ● |
| **P03** Admin | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| **P04** B2B | ● | | ● | | ● | ● | ● | ● | ● | | ● | ● | ● | ● | | | ● | ● | | ● | | | ● | ● | ● | | ● |
| **P05** Vendor | | | ● | | | | | | | | | | | | ● | ● | | ● | | ● | | | ● | ● | | | |
| **P06** Analytics | | | | | | | | | | | | | | | | | | | | | | | | | ● | ● | |
| **P07** Seller | ● | ● | | | | | | | | | ● | ● | | | ● | | | | | ● | | ● | ● | ● | ● | | ● |
| **P08** Brand | ● | | | | | | | | ● | | | | | | ● | | ● | | | ● | | ● | ● | ● | ● | | |
| **P09** Logistics | ● | ● | ● | | | ● | | | | | | ● | ● | ● | ● | | ● | ● | | ● | | | | ● | | | |
| **P10** Contact Centre | ● | ● | ● | | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | | | ● | | | ● | | | ● | ● | ● | ● | ● |
| **P11** Auditor | ● | ● | | ● | | | | | | | | | | | ● | | ● | | ● | | ● | ● | ● | ● | ● | | |
| **P12** Partner | | | | | | | ● | | | ● | ● | ● | | ● | | | | | | ● | | | | ● | ● | | ● |

---

*Next document: `11_Feature_and_Function_Register.md`*
