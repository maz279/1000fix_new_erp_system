---
id: FIX-ERP2-P01
portal_id: P01
portal_code: CSP
portal_name: Customer Self-Service Portal & Mobile Application
type: Portal + Native Application
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Digital Channels Squad
priority: P0
wave: W2 (web) · W6 (native application)
---

# P01 — Customer Self-Service Portal & Mobile Application
### Portal Suite · Code `CSP` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P01 |
| **Portal code** | `CSP` |
| **Type** | Progressive Web Application + native mobile application |
| **Status** | Existing (expanded in v2.1 — trade-in, rental, marketplace, data services, e-waste and protection products added) |
| **Priority** | **P0** — the highest-volume surface in the estate |
| **Delivery wave** | **W2** (PWA, Months 5–8) · **W6** (native app, Months 23–26) |
| **Users** | Individual retail customers |
| **Volume** | **250,000+ per month**; target > 120,000 monthly active |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Digital Channels Squad |
| **Technology** | Next.js 15 (React 19) PWA · React Native (Android primary, iOS secondary) · shared design system |
| **Custom development** | `CD-200` (web), `CD-201` (native application) |
| **Requirement range** | FR-POR-001 … FR-POR-040 |
| **Requirement count** | **40** *(measured — supersedes the 26 allocation in `05-01` §4)* |
| **Effort estimate** | **42 person-weeks** (28 PW web · 14 PW native) |
| **Backing modules** | M01, M02, M03, M06, M07, M08, M09, M10, M11, M12, M13, M14, M17, M18, M20, M27, M33, M34, M37, M38, M39 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P01 is **the front door**. It is the only surface most customers will ever see, and for a
company whose competitive claim rests on convenience — pick-and-drop, on-site service, online
booking, order tracking — it is where that claim is either honoured or exposed.

Its job is narrow and demanding: let a customer with a broken device get help **in under three
minutes, on a phone, on a 3G connection, in Bengali**, and then keep them informed without them
having to ask.

P01 holds no authoritative state. Every booking it creates belongs to M01, every payment to
M20, every device to M17. What P01 owns is the **journey** — the sequence, the wording, the
number of taps, and the moment a customer decides to complete or abandon.

### Why It Exists

Three facts make this the programme's highest-leverage surface.

**The hotline is absorbing work that should never reach it.** The Company operates hotline
16743 and a contact centre of 30–60 agents. A large share of contact volume is status enquiry —
*"is my laptop ready?"* — which is a question the system can answer without a human. Every
status call deflected to self-service is contact-centre capacity returned to work that
genuinely needs a person.

**Online booking is at 40% and must reach 88%.** That is not a marketing target; it is the
mechanism by which intake becomes structured data. A booking made on the phone arrives as free
text and an agent's interpretation. A booking made in P01 arrives with a device identity, a
fault category, an address with GPS, photographs and a slot — which is what M02 needs to
dispatch well and M26 needs to learn from.

**Fourteen revenue streams need a shopfront.** The v2.1 scope adds rental (M13), trade-in and
refurbished resale (M14), parts e-commerce (M38), the marketplace (M12), protection products
(M09), data services (M06) and e-waste collection (M18). Each is a new business line, and none
of them reaches a retail customer without this surface. P01 is where scope expansion becomes
revenue rather than architecture.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 1 | "Customer Self-Service Portal — 250,000+ monthly — service booking, order tracking, invoice/payment, loyalty management" |
| ERP BRD BR-SRM-001 | Service orders must be creatable from "web portal, WhatsApp chatbot, phone, walk-in terminal, email" — P01 is the web channel |
| ERP BRD BR-SRM-009 | "Send automated customer notifications (SMS + WhatsApp) at each lifecycle milestone" |
| ERP BRD BR-SRM-012 | "Generate customer-facing repair quotations with digital approval (accept/reject)" |
| ERP BRD BR-FSM-014 | "Provide customers with a real-time technician tracking link with ETA on the day of service" |
| ERP BRD BR-CRM-002 | Device registry per customer — the customer-facing view of M17 |
| ERP BRD BR-CRM-005 | "Automated post-service satisfaction surveys (CSAT + NPS) via SMS/WhatsApp" |
| ERP BRD BR-CRM-006 | Privilege Program tiers — enrolment, upgrade, benefit application, renewal |
| ERP BRD BR-FIN-004 | "Multiple payment methods: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer" |
| ERP BRD BR-CWM-010 | Warranty extension products — enrolment, billing and coverage tracking |
| ERP BRD NFR-004 | "Customer portal shall support 50,000+ concurrent users" |
| ERP BRD NFR-001 | Page load ≤ 3 seconds under normal load |
| `04-00` §P01 | The full capability set, design requirements and five KPIs adopted verbatim in §5 and §15 |
| `04-00` §1 | "No portal holds authoritative state… no portal implements business rules" — the governing constraint |
| `04-00` §3 PS-01…PS-12 | Twelve cross-portal standards, all binding on P01 |
| Company Profile §Digital Presence | Existing customer portal, order tracking and 1000FiX Station — the surfaces P01 replaces |
| Company Profile §Customer Benefits | Convenience and transparency are stated competitive advantages |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** A portal's boundary is unusual: almost nothing it
> displays belongs to it. The discipline is to state clearly what P01 *owns* — journey, session,
> presentation and consent capture — and to name the module that owns everything else.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The customer account surface: registration, login, profile, addresses, household members, preferences |
| 2 | Self-registration and identity verification by phone and email OTP, social login and device biometrics |
| 3 | The booking journey: service selection, delivery mode, slot, fault description, evidence capture, confirmation |
| 4 | Device self-registration and the customer-facing device history view |
| 5 | Status tracking, live technician tracking and the public no-login tracking link |
| 6 | Estimate presentation, approval, part-approval and decline with e-signature |
| 7 | Payment initiation, method selection and the payment result experience |
| 8 | Invoice, receipt and statement retrieval |
| 9 | Contract, entitlement and scheduled-visit presentation, and renewal and purchase journeys |
| 10 | Warranty status display, protection-product purchase and claim submission |
| 11 | Loyalty status, points, vouchers, referral link and redemption journeys |
| 12 | The retail shopfront: parts, accessories, refurbished devices, rental booking, cart and checkout |
| 13 | Trade-in submission, offer presentation, acceptance and collection arrangement |
| 14 | Data-services request and case status, and destruction-certificate retrieval |
| 15 | E-waste collection booking and drop-off point finder |
| 16 | Support surface: AI assistant, live chat, in-app calling, knowledge base and the notification inbox |
| 17 | Feedback capture: CSAT, NPS, technician rating, review submission and complaint raising |
| 18 | Consent capture and preference management, presented in the customer's language |
| 19 | Offline shell, installability, push notification registration and delivery |
| 20 | Funnel instrumentation on every critical journey |
| 21 | Bengali-first presentation with an English toggle, across every screen and every error |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The service order, its lifecycle, SLA and state machine** | **M01** Service Request & Order Management | P01 initiates and displays; it never advances a state |
| **Dispatch, scheduling, routing and technician assignment** | **M02** Field Service & Dispatch | A customer chooses a slot; the system chooses a technician |
| **The live technician position stream** | **M02** (device owned by M46, pipe by M48) | P01 renders a position it is given |
| **Price calculation, discount and promotion logic** | **M11** Pricing & Dynamic Pricing | P01 displays a price the pricing engine returned. **No price is ever computed client-side** |
| **Estimate construction, approval thresholds and revision rules** | **M01 / M36** | P01 presents and captures the decision |
| **Payment processing, gateway integration and settlement** | **M20** Receivable & Collections (gateways via M28) | P01 initiates; it never handles card data or holds a payment state |
| **Invoice generation, tax computation and Mushak formatting** | **M20 / M51** | P01 retrieves a rendered document |
| **Customer and party master, deduplication and merge** | **M33** Party Master | P01 submits a registration; M33 decides whether it is a new party |
| **Device identity, resolution, ownership history and genealogy** | **M17** Device & Customer Asset Registry | P01 submits identifiers; M17 resolves them |
| **Contract terms, entitlement rules and renewal pricing** | **M08** Contract Lifecycle | P01 displays entitlement; it does not compute it |
| **Warranty validation, claim adjudication and brand submission** | **M09** Warranty & Claims | P01 submits a claim; M09 runs it |
| **Loyalty tier rules, accrual, expiry and redemption validity** | **M10** Loyalty & Rewards | P01 shows a balance; M10 owns the arithmetic |
| **Catalogue content, specification and availability** | **M37 / M15 / M38** | P01 renders a catalogue it does not author |
| **Trade-in valuation and refurbishment grading** | **M14** Trade-In & Refurbishment | P01 collects photographs; M14 makes the offer |
| **Marketplace seller listings, matching and commission** | **M12** Marketplace | P01 is the buyer surface; P07 is the seller surface |
| **Rental availability, rate ladder and agreement terms** | **M13** Rental & EaaS | P01 books against availability M13 publishes |
| **Notification channel selection, templates and delivery** | **M27** Contact Centre & Communications | P01 registers a push token and renders an inbox; M27 sends |
| **The AI assistant's model, intents and Bengali NLP** | **M32** Conversational AI (surfaced here) | P01 embeds the assistant; M32 owns its behaviour |
| **Live chat routing, agent assignment and transcripts** | **M27** (agent side is **P10**) | P01 is the customer end of a conversation M27 routes |
| **Complaint classification, root cause and CAPA** | **M34 / M23** | P01 raises; the quality process runs elsewhere |
| **Identity, session policy, MFA and credential storage** | **M29** Identity & Security | **PS-01** — P01 maintains no credential store |
| **Consent as a party attribute and its legal record** | **M33** | P01 captures the act; M33 holds the record |

### 3.3 Shared Concepts

| Concept | P01's Role | Owning Module |
|---|---|---|
| Customer journey and funnel | **Owns** — the defining concern of this portal | P01 |
| Session and authentication | Delegates entirely | M29 |
| Service order | Creates via API; renders status | M01 |
| Device | Submits identifiers; renders history | M17 |
| Estimate | Presents; captures the decision and signature | M01 / M36 |
| Payment | Initiates; renders the outcome | M20 |
| Price | Displays only; never computes | M11 |
| Contract and entitlement | Displays; initiates renewal | M08 |
| Loyalty balance | Displays; initiates redemption | M10 |
| Notification | Registers the token; renders the inbox | M27 |
| Consent | Captures the act with evidence | M33 / M29 |
| Product and service catalogue | Renders | M37 / M38 |
| Review and rating | Captures | M34 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Salesforce Service Cloud / Experience Cloud customer portals** | Authenticated self-service with case creation, asset history, entitlement visibility and knowledge deflection | **Design for full resolution, not information.** The dominant finding across self-service research is that most journeys fail because they inform without completing. Every P01 journey terminates in a completed task — booked, approved, paid, resolved — or in an explicit hand-off to a human with context carried | Its portal licensing model and component framework |
| **Field-service customer portals (ServiceTitan, Jobber, FieldEx, Field Ascend)** | Customer schedules appointments, views service history, tracks the technician in real time, approves quotes | **The whole pattern**, and specifically **live technician tracking with ETA** — which research identifies as the single feature that most reduces inbound status calls. The customer stops asking because they can see | Their assumption of a single-country, single-language, high-bandwidth customer base |
| **Zendesk / monday.com self-service portal practice** | Role-aware dashboards, saved views, personalised recommendations, knowledge deflection measured as a KPI | **Deflection as a measured outcome, not a hope.** "Self-service status checks versus hotline calls > 80%" is a portal KPI in `04-00`, and P01 instruments both sides of that ratio so it is provable | Heavy knowledge-base-first design; a customer with a broken laptop wants a booking, not an article |
| **Amazon / Daraz order tracking** | A single canonical status timeline, public tracking without login, proactive notification at each milestone | **The public tracking link without login** — adopted directly. In Bangladesh a device is frequently handed in by one family member and asked about by another; requiring the second person to have an account guarantees a phone call | Full marketplace UX complexity |
| **bKash / Nagad / Pathao consumer apps** *(the local benchmark that matters most)* | Bengali-first interface, OTP-based identity, low-bandwidth operation, small install footprint, payment flows customers already know | **The interaction vocabulary Bangladeshi customers already have.** Payment confirmation, OTP entry and status presentation follow the conventions of the apps the customer uses daily rather than a Western SaaS convention. This is the single largest adoption lever and no international benchmark supplies it | — |
| **Progressive Web App practice** | Offline shell, installability, push notification, sub-second repeat loads, no app-store dependency | **PWA before native, deliberately.** The web PWA ships in Wave 2 and the native app in Wave 6, because an app-store install is a barrier at the moment of a broken device, and because a 400 KB first load reaches a customer a 40 MB install does not | Native-first delivery. Native adds biometric login, better push reliability and store presence — real but not urgent |
| **Next.js 15 / React 19 enterprise portal practice** | Partial pre-rendering with Suspense boundaries: static shell served instantly, user-specific data streamed milliseconds later | **Partial pre-rendering on the booking path**, so the first meaningful paint does not wait on an authenticated call. This is what makes a sub-3-second load on 3G achievable rather than aspirational | Edge-compute deployment topology; the estate is single-region |
| **WCAG 2.1 AA and multilingual accessibility practice** | Correct language tagging so screen readers pronounce Bengali script accurately; semantic HTML and ARIA; touch-target and small-screen criteria added in 2.1 | **Language-of-parts tagging on every mixed-script element.** A Bengali interface with untagged English product names is read incorrectly by a screen reader, which fails the very users accessibility exists for | Nothing. `04-00` PS-04 makes WCAG 2.1 AA binding |

**Design position.** Five deliberate differences from the benchmark.

First, **Bengali is the default, not a toggle.** Every international benchmark treats
localisation as a setting on an English product. P01 opens in Bengali and offers English. This
inverts the effort — Bengali strings must be complete before release, not translated after —
and it is the reason `04-00` PS-03 makes Bengali default on customer surfaces and AS-12 makes
translation a definition-of-done item rather than a follow-up.

Second, **the booking path is budgeted in kilobytes.** `04-00` sets 400 KB first load on the
booking path. This is treated as a hard budget enforced in CI, not a guideline. A customer on a
3G connection in a district town is the design centre, not the edge case, and every feature
proposed for the booking path must fit the budget or go elsewhere in the journey.

Third, **no business rule runs client-side.** `04-00` PS-11 is absolute. The client validates
for convenience — a required field, an obviously malformed phone number — but every price,
every entitlement, every eligibility decision comes from the module that owns it. This is
slower to build and it is the only way twelve surfaces stay consistent with one system of
record.

Fourth, **abandonment is instrumented as carefully as completion.** Booking funnel conversion
above 72% is a `04-00` KPI, and a funnel target is meaningless without knowing where the other
28% leave. Every step transition is instrumented to M25, so the funnel is a diagnosable object
rather than a number in a report.

Fifth, **the portal degrades rather than fails.** When a backing module is unavailable, P01
shows what it can and tells the customer plainly what it cannot do right now and what to do
instead — `04-00` PS-09. A blank screen or a generic error at the moment a customer's laptop is
broken is a retention event.

---

## 5. Capability Areas & Functions

### 5.1 Account, Identity & Preferences

| FR ID | Feature | Function — "The portal shall…" | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-001 | Registration | Register a customer with a phone number verified by OTP, an optional email, and a name, completing in under 60 seconds with no mandatory field the customer must look up | **P0** | W2 |
| FR-POR-002 | Authentication | Authenticate through M29 by OTP, password, social login or device biometrics, holding no credential store of its own (**PS-01**) | **P0** | W2 |
| FR-POR-003 | Profile | Maintain name, contacts, language, theme and notification preferences, writing to M33 and never holding a second copy of the party record | **P0** | W2 |
| FR-POR-004 | Addresses | Maintain multiple tagged addresses with saved GPS coordinates and Bangladesh address structure (division → district → upazila → union/ward), selectable in one tap at booking | **P0** | W2 |
| FR-POR-005 | Household members | Permit named household or office members to be associated with the account so a device handed in by one is visible to another | P2 | W6 |
| FR-POR-006 | Consent management | Present each consent purpose in the customer's language, capture grant and revocation with timestamp and version, and write the record to M33 | **P0** | W2 |
| FR-POR-007 | Account deletion and export | Allow a customer to request account deletion and a copy of their data, routed to M29 and M33 for lawful handling | P2 | W6 |

### 5.2 Devices

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-008 | Device registration | Register a device by typing or scanning a serial, IMEI or service tag, or by photographing the label, submitting to M17 for resolution and showing the resolved model back for confirmation | **P0** | W2 |
| FR-POR-009 | My devices | List the customer's devices with model, purchase date, warranty state and last service, drawn live from M17 | **P0** | W2 |
| FR-POR-010 | Device history | Show the service timeline for a device — date, what was wrong, what was done, outcome — **without cost or internal notes** (M17 BRU-AST-20) | **P0** | W2 |
| FR-POR-011 | Device report | Generate a downloadable device history report suitable for resale or insurance, watermarked and verifiable | P2 | W6 |
| FR-POR-012 | Ownership transfer | Initiate transfer of a device to another customer, routed to M17 for evidence and confirmation | P2 | W6 |

### 5.3 Booking

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-013 | Three-step booking | Complete a booking in no more than three steps — what is wrong, where and when, confirm — with every step recoverable if abandoned | **P0** | W2 |
| FR-POR-014 | Delivery mode | Offer walk-in, on-site, pick-and-drop and remote support, showing only the modes available for that device category, location and time | **P0** | W2 |
| FR-POR-015 | Slot selection | Present bookable slots reflecting real capacity from M02 and M55, never offering a slot that cannot be served | **P0** | W2 |
| FR-POR-016 | Fault description | Capture the fault by guided category selection, free text, photographs and a Bengali voice note, with the guided path producing the structured fault code M01 needs | **P0** | W2 |
| FR-POR-017 | Price indication | Show an indicative price or price range returned by M11 before the customer commits, with the basis stated and the limits of the indication made plain | **P0** | W2 |
| FR-POR-018 | Booking amendment | Reschedule or cancel within the policy window without contacting an agent, showing any applicable charge before confirmation | P1 | W2 |
| FR-POR-019 | Booking recovery | Restore an abandoned booking on the customer's next visit and, where consent allows, prompt once by their preferred channel | P1 | W2 |

### 5.4 Tracking & Approvals

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-020 | Status timeline | Present a single canonical status timeline for every job with plain-language milestone names and the expected next step | **P0** | W2 |
| FR-POR-021 | Live technician tracking | On the day of service, show the technician's position, name, photograph and ETA on a map, refreshed from M02 (BR-FSM-014) | **P0** | W2 |
| FR-POR-022 | Public tracking link | Serve a tracking view addressable by link without login, exposing status and ETA only — never device history, cost or personal data | **P0** | W2 |
| FR-POR-023 | Proactive updates | Deliver milestone notifications by push, SMS and WhatsApp according to the customer's preference, dispatched by M27 (BR-SRM-009) | **P0** | W2 |
| FR-POR-024 | Estimate approval | Present an estimate with itemised work and parts, and capture approve, part-approve or decline with an e-signature and a timestamp (BR-SRM-012) | **P0** | W2 |
| FR-POR-025 | Revised estimates | Present a revised estimate as a comparison against the original, showing what changed and why, and require a fresh decision | P1 | W2 |

### 5.5 Payments, Invoices & Contracts

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-026 | Payment | Initiate payment by bKash, Nagad, card, SSLCOMMERZ or bank transfer, handling no card data itself and rendering the outcome unambiguously (BR-FIN-004) | **P0** | W2 |
| FR-POR-027 | Saved methods | Offer tokenised saved payment methods where the gateway supports them, storing no instrument data in the portal | P2 | W6 |
| FR-POR-028 | Invoices and receipts | Retrieve invoices, receipts and payment history as rendered documents from M20, including NBR-compliant Mushak invoices | **P0** | W2 |
| FR-POR-029 | Refund status | Show the state of any refund or credit note with an expected date | P1 | W2 |
| FR-POR-030 | Contracts | Display AMC and RAMC contracts, entitlement balance, consumption and the scheduled visit calendar from M08 | P1 | W4 |
| FR-POR-031 | Contract purchase and renewal | Purchase a new contract or renew an existing one, with the price and terms supplied by M08 and M11 | P1 | W4 |

### 5.6 Warranty, Loyalty & Referral

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-032 | Warranty status | Show manufacturer, extended and workmanship warranty state per device, resolved by M17 with the basis stated (BR-CWM-005) | **P0** | W2 |
| FR-POR-033 | Protection products | Present and sell warranty extensions and protection products, with coverage and exclusions stated before purchase (BR-CWM-010) | P1 | W4 |
| FR-POR-034 | Claim submission | Submit a warranty claim with evidence, and track its state to conclusion | P1 | W4 |
| FR-POR-035 | Loyalty | Show Privilege tier, benefits, points balance and history, and complete a redemption, with all arithmetic performed by M10 (BR-CRM-006) | P1 | W2 |
| FR-POR-036 | Referral | Generate a shareable referral link or code, and show referrals made, converted and rewarded | P2 | W6 |

### 5.7 Shop, Circular Services & Support

| FR ID | Feature | Function | Pri | Wave |
|---|---|---|:--:|:--:|
| FR-POR-037 | Shopfront | Browse and buy parts, accessories and refurbished devices, and book rentals, with cart, checkout, order tracking and returns, against catalogue and availability from M37, M38, M15 and M13 | P1 | W6 |
| FR-POR-038 | Trade-in and e-waste | Submit a trade-in with photographs and receive an offer from M14; and book an e-waste collection or find a drop-off point through M18 | P2 | W6 |
| FR-POR-039 | Support | Provide the M32 AI assistant in Bengali and English, escalation to live chat and in-app calling through M27, a knowledge base from M61, and a single inbox of every notification sent | **P0** | W2 |
| FR-POR-040 | Feedback | Capture CSAT, NPS and a multi-parameter technician rating after service, accept a written review, and allow a complaint to be raised and tracked (BR-CRM-005) | **P0** | W2 |

> **Cross-cutting.** Data-services request and case status (M06) and destruction-certificate
> retrieval are delivered within FR-POR-039's support surface and the FR-POR-028 document
> retrieval pattern rather than as separate requirements. Offline shell, installability and push
> registration are technical functions and are specified in §6.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No authoritative state** | P01 persists no business object. Local storage holds session context, draft bookings and cached reference data only, all reconstructible from the ERP (**`04-00` §1**) |
| T-02 | **Booking-path payload budget** | ≤ 400 KB total first load on the booking path, enforced by a CI budget check that fails the build on regression (**PS-07**) |
| T-03 | **Partial pre-rendering** | The static shell is served from cache; authenticated content streams into Suspense boundaries. First contentful paint does not wait on an authenticated call |
| T-04 | **Performance envelope** | Page load ≤ 3 s on a 3G connection at p75; repeat load ≤ 1 s from the service-worker shell (NFR-001) |
| T-05 | **Concurrency envelope** | 50,000+ concurrent users without degradation (NFR-004); static and cacheable content served from CDN, authenticated calls rate-limited per session at the M28 gateway |
| T-06 | **Offline shell** | The service worker serves the shell, the customer's device list and their open job statuses offline, and states plainly that the data is cached and when it was fetched |
| T-07 | **Idempotent submission** | Every state-changing submission — booking, approval, payment initiation, review — carries a client-generated idempotency key so a retry on a flaky connection cannot double-post |
| T-08 | **All traffic through the gateway** | Every call routes through the M28 gateway with per-portal credentials, rate limits and observability (**PS-02**). No direct module call exists |
| T-09 | **No client-side business logic** | Prices, entitlements and eligibility are never computed in the client. Client validation is for convenience only and is always re-validated server-side (**PS-11**) |
| T-10 | **Session policy inherited** | Session lifetime, idle timeout and step-up authentication are M29 policy, not portal configuration (**PS-12**) |
| T-11 | **Payment isolation** | No card data touches P01. Payment is a redirect or an SDK handoff; P01 receives only a result token and renders the outcome |
| T-12 | **Language of parts** | Every mixed-script element carries a `lang` attribute so a screen reader pronounces Bengali and English correctly (WCAG 3.1.2) |
| T-13 | **Accessibility** | WCAG 2.1 AA across every journey, including touch-target size, contrast, focus order and error identification (**PS-04**) |
| T-14 | **Responsive floor** | Usable from 320 px width with no horizontal scrolling (**PS-05**) |
| T-15 | **Design system** | One component library and one token set shared with P04, P07, P08, P10 and P12 (**PS-06**) |
| T-16 | **Error contract** | Every user-visible error states what happened, what it means and what to do next, in the customer's language (**PS-09**) |
| T-17 | **Graceful degradation** | Where a backing module is unavailable, the affected capability is disabled with an explanation and an alternative route, never a blank screen or a stack trace |
| T-18 | **Funnel instrumentation** | Every step of every critical journey emits a structured analytics event to M25, including abandonment with the step reached (**PS-10**) |
| T-19 | **Push registration** | Device push tokens are registered against the party in M27, refreshed on rotation, and revoked on logout and account deletion |
| T-20 | **Native parity** | The native application uses the same APIs and the same design tokens as the PWA; it adds biometric login, reliable push and store presence, and no exclusive business capability |
| T-21 | **Data minimisation on the public link** | The no-login tracking view is served by a separate, tokenised, expiring endpoint exposing status and ETA only, with no path to any other record |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P01 |
|---|---|---|
| **Individual customer** | Phones the hotline, waits, describes the fault twice, phones again to ask if it is ready | Books in three steps on a phone, watches the technician approach on a map, approves the estimate from the sofa |
| **A customer's family member** | Cannot get a status because the job is in someone else's name | Opens the tracking link that was shared with them |
| **Contact centre agent** | Spends the shift answering "is it ready yet?" | Handles the conversations that genuinely need a person |
| **Service centre agent** | Transcribes a phone booking into the system and guesses the device | Receives a booking with a resolved device, a fault code, photographs and a GPS address |
| **Technician** | Arrives with a one-line fault description | Arrives with photographs, a voice note and a structured fault category |
| **Dispatcher** | Works from bookings of uneven quality | Works from structured demand with real slot commitments behind it |
| **Marketing** | Cannot attribute a campaign to a booking | Sees the funnel end to end, by channel, by campaign, by device category |
| **Finance** | Chases payment after the job | Collects at approval or on completion through the customer's usual wallet |
| **CCO** | Has fourteen revenue streams and one shopfront that sells none of them | Has a surface where rental, trade-in, refurbished resale, protection products and parts all reach a retail customer |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Customer retention** | Transparency, recognition of device history, and a service experience that does not require a phone call | Contributes to the **BDT 78 lac/year** retention benefit attributed to M07 + M10 + M27 in Scope Charter §6.2 |
| **Contact-centre cost avoidance** | Status enquiry deflected to self-service at > 80% | Every deflected status call is agent capacity returned. At 250,000+ monthly customers this is the largest single volume lever in the estate |
| **Administrative labour savings** | Bookings arrive structured; no transcription, no re-keying, no device guessing | Contributes to the **BDT 62 lac/year** cross-module administrative saving in §6.2 |
| **Revenue enablement — new streams** | Rental, trade-in, refurbished resale, parts retail and protection products reach retail customers only through this surface | Underpins the retail share of **BDT 48 lac** (M13), **BDT 65 lac** (M14) and the protection-product component of **BDT 72 lac** (M08) |
| **AMC/RAMC renewal** | Renewal presented in-app with entitlement consumption visible, before expiry | Supports the **BDT 72 lac/year** AMC uplift attributed to M08 |
| **Loyalty programme activation** | Points, tier and vouchers visible and redeemable without an agent | Supports the **BDT 78 lac** retention benefit; a loyalty scheme customers cannot see does not change behaviour |
| **Cash collection speed** | Payment at approval and on completion through bKash and Nagad rather than cash at counter | Supports the **BDT 26 lac/year** financial close and cash-flow benefit attributed to M19 + M20 |
| **Dispatch quality** | Structured fault codes and photographs before the visit improve parts prediction and first-time fix | Supports KPI-004 first-time fix 88% and the **BDT 130 lac/year** productivity benefit attributed to M02 + M26 |
| **Marketing attribution** | Every booking carries its channel and campaign | Makes marketing spend measurable for the first time |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The convenience claim becomes verifiable** | The Company's stated competitive advantages are convenience and transparency. P01 is where those stop being marketing copy and become a measurable funnel |
| **Bengali-first as a market position** | A genuinely Bengali product, not a translated one, addresses the majority of the addressable market on its own terms. Most competitors do not |
| **Accessibility as inclusion** | WCAG 2.1 AA with correct Bengali language tagging means customers using screen readers can book a repair independently |
| **Data quality at source** | Structured intake at the customer's hand is the cheapest place in the whole estate to get data right; every downstream module benefits |
| **Consent captured properly** | Purpose-specific, versioned, revocable consent captured in the customer's language is the practical basis of the ISMS and privacy position |
| **Brand consistency** | One design system across six external surfaces means a customer, a corporate client and a brand partner all meet the same company |
| **Expansion readiness** | Locale, currency and payment method are M65 configuration; a second country is a country pack, not a second portal |

---

## 8. User Journeys & State Models

### 8.1 The Booking Funnel — the portal's primary object

```
   ENTRY ─────────────────────────────────────────────────────┐
   (organic · campaign · WhatsApp · QR · referral · direct)   │
        │                                                     │
   ┌────▼─────────┐  abandonment instrumented at every step ──┤
   │ 1. WHAT IS   │  device selected or registered            │
   │    WRONG     │  fault category · photos · voice note     │
   └────┬─────────┘  ▸ price indication shown (M11)           │
        │                                                     │
   ┌────▼─────────┐                                           │
   │ 2. WHERE &   │  delivery mode (walk-in · on-site ·       │
   │    WHEN      │  pick-and-drop · remote)                  │
   └────┬─────────┘  address · slot from real capacity (M02)  │
        │                                                     │
   ┌────▼─────────┐                                           │
   │ 3. CONFIRM   │  summary · terms · consent · submit       │
   └────┬─────────┘                                           │
        │ idempotent submit → M01 creates the service order   │
   ┌────▼─────────┐                                           │
   │  CONFIRMED   │──► tracking · notifications · approval ───┘
   └──────────────┘

   Abandoned at any step → draft retained → recoverable on return
                          → one consented prompt by preferred channel
```

| Step | Completion measured as | Primary abandonment cause to instrument |
|---|---|---|
| Entry → Step 1 | Device identified or registered | Device not found; serial unreadable |
| Step 1 → Step 2 | Fault captured | Category list does not match the problem; price indication too high |
| Step 2 → Step 3 | Slot selected | No slot available; delivery mode unavailable at that address |
| Step 3 → Confirmed | Order created | Terms friction; login required too late; submission failure |

> **Design rule.** Login is requested **as late as possible** — at Step 3, not at entry. A
> customer forced to authenticate before seeing whether the Company can help them abandons at
> the highest rate of any step in this funnel.

### 8.2 Job Status as the Customer Sees It

P01 renders a **simplified, plain-language projection** of M01's state machine. The customer
never sees an internal state name.

```
  BOOKED ──► COLLECTED / ARRIVED ──► BEING DIAGNOSED ──► ESTIMATE READY
                                                              │
                        ┌─────────────────────────────────────┤ approve
                        │                                     │
                        │ decline                       ┌─────▼──────┐
                  ┌─────▼──────┐                        │  BEING     │
                  │  RETURNING │                        │  REPAIRED  │
                  │  UNREPAIRED│                        └─────┬──────┘
                  └────────────┘                              │
                                     ┌────────────────────────┤
                          waiting    │                        │
                       ┌─────────────▼──┐              ┌──────▼──────┐
                       │ WAITING FOR    │              │ READY /     │
                       │ A PART         │              │ ON THE WAY  │
                       └────────────────┘              └──────┬──────┘
                                                              │
                                                       ┌──────▼──────┐
                                                       │  COMPLETED  │──► feedback
                                                       └─────────────┘
```

| Internal state (M01) | Shown to the customer as | Why |
|---|---|---|
| Created, Assigned | Booked | The customer does not care who it is assigned to until the day |
| In progress — diagnosis | Being diagnosed | Sets the expectation that a price follows |
| Estimate issued | Estimate ready — your decision needed | Names the action required of them |
| Parts pending | Waiting for a part, expected *date* | The single most-called-about state; it must carry an expected date or it generates a call |
| In progress — repair | Being repaired | — |
| Completed, ready | Ready for collection / On the way to you | Mode-dependent wording |
| Invoiced, Closed | Completed | Internal accounting states are not customer states |

> **Rule.** A state without a plain-language name and an expected next step is not shown. If a
> state cannot be explained to a customer, it is an internal state and P01 maps it to the last
> explainable one.

---

## 9. Portal Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P01-01 | P01 persists no authoritative business state; every business object is created and owned by its module | **H** | CTO |
| PRU-P01-02 | No price, entitlement, discount or eligibility decision is computed client-side (**PS-11**) | **H** | CTO |
| PRU-P01-03 | Authentication and session policy are delegated entirely to M29; P01 holds no credential store (**PS-01**) | **H** | CTO |
| PRU-P01-04 | Every API call routes through the M28 gateway with per-portal credentials (**PS-02**) | **H** | CTO |
| PRU-P01-05 | No card or wallet credential is stored, logged or transmitted by P01 | **H** | CFO |
| PRU-P01-06 | The public tracking link exposes status and ETA only, and no path from it reaches any other record | **H** | CTO |
| PRU-P01-07 | Cost, margin and internal notes are never present in any P01 response payload (M17 BRU-AST-20) | **H** | CFO |
| PRU-P01-08 | A customer may access only their own records; household association is explicit and revocable | **H** | CTO |
| PRU-P01-09 | The booking path first load may not exceed 400 KB; the build fails on regression (**PS-07**) | **H** | Digital Channels Squad |
| PRU-P01-10 | Every user-visible string, including every error, exists in Bengali before release (AS-12, **PS-03**) | **H** | CCO |
| PRU-P01-11 | Bengali is the default language on first visit; English is a toggle | **H** | CCO |
| PRU-P01-12 | Login is not required before the customer can see whether the Company can help them | **C** | CCO |
| PRU-P01-13 | Every state-changing submission is idempotent; a retry cannot double-post | **H** | CTO |
| PRU-P01-14 | A slot is offered only where capacity genuinely exists in M02 and M55 | **H** | Operations Director |
| PRU-P01-15 | A price indication states its basis and its limits; it is never presented as a final price | **H** | CCO |
| PRU-P01-16 | An estimate decision is captured with an e-signature, a timestamp and the version approved | **H** | CFO |
| PRU-P01-17 | Consent is purpose-specific, versioned, revocable, and captured in the customer's language | **H** | CCO |
| PRU-P01-18 | A job state with no plain-language name and no expected next step is not displayed | **C** | CCO |
| PRU-P01-19 | Where a backing module is unavailable, the capability is disabled with an explanation and an alternative route (**PS-09**) | **H** | CTO |
| PRU-P01-20 | Every critical journey step emits an analytics event, including abandonment (**PS-10**) | **H** | CCO |
| PRU-P01-21 | The native application introduces no business capability the PWA does not have | **C** | CTO |
| PRU-P01-22 | WCAG 2.1 AA conformance is a release gate, not a backlog item (**PS-04**) | **H** | CCO |

---

## 10. Data, Caching & State Model

> P01 owns no entity. This section states precisely what it may hold, for how long, and what
> must never be held.

### 10.1 Client-Side State — permitted

| Object | Purpose | Lifetime | Reconstructible From |
|---|---|---|---|
| Session context | Token reference, party ID, language, tier | Session, per M29 policy | M29 |
| Draft booking | Recovery of an abandoned funnel | 7 days, then purged | Nothing — it is a draft, and its loss is acceptable |
| Device list projection | Offline "my devices" view | 24 hours, revalidated | M17 |
| Open job status projection | Offline status view, stamped with fetch time | 4 hours, revalidated | M01 |
| Catalogue and reference data | Fault categories, service types, addresses | 24 hours | M37, M64 |
| Notification inbox projection | Offline inbox | 30 days | M27 |
| Push token | Delivery routing | Until rotation or logout | M27 |
| Analytics event queue | Instrumentation under poor connectivity | Until delivered | — |

### 10.2 Never Held Client-Side

| Item | Reason |
|---|---|
| Card, wallet or bank credentials | PRU-P01-05; payment is a gateway handoff |
| Any cost, margin or internal note | PRU-P01-07 |
| Another customer's data of any kind | PRU-P01-08 |
| Authentication credentials or password material | PRU-P01-03; M29 owns identity |
| Pricing rules, entitlement rules or eligibility logic | PRU-P01-02 |
| Unencrypted personal identifiers beyond what the session needs | AS-14 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party`, consent record | M33 | Read; submit registration and consent |
| `fix.asset`, `fix.asset.service.history` | M17 | Read; submit identifiers for resolution |
| `fix.service.order` | M01 | Create via API; read status |
| `fix.estimate` | M01 / M36 | Read; submit decision and signature |
| `fix.invoice`, `fix.payment`, `fix.credit.note` | M20 | Read; initiate payment |
| `fix.contract`, `fix.entitlement` | M08 | Read; initiate renewal |
| `fix.warranty`, `fix.warranty.claim` | M09 / M17 | Read; submit claim |
| `fix.loyalty.balance`, `fix.voucher` | M10 | Read; initiate redemption |
| `fix.catalogue.item`, price | M37 / M11 | Read |
| `fix.rental.availability` | M13 | Read; book |
| `fix.tradein.offer` | M14 | Submit; read offer |
| `fix.notification` | M27 | Read inbox; register token |
| `fix.knowledge.article` | M61 | Read |
| `fix.review`, `fix.complaint` | M34 | Submit; read status |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P01-01 | Job milestone reached in M01 | Deliver a push, SMS or WhatsApp notification through M27 per the customer's preference, and write it to the in-app inbox | Retry through M27; the inbox entry is always written so the customer can find it |
| AUT-P01-02 | Technician dispatched for the day | Enable live tracking on the job and notify the customer that the technician is on the way with an ETA | Show status without the map and state that tracking is unavailable |
| AUT-P01-03 | Estimate issued | Notify the customer that a decision is needed, with the amount and the deadline, and deep-link to the approval screen | Escalate to M27 for an agent-assisted call after the configured wait |
| AUT-P01-04 | Estimate unapproved beyond the configured window | Send one reminder, then hand off to M27 for an agent follow-up | Reminder only |
| AUT-P01-05 | Booking abandoned mid-funnel | Retain the draft; where consent allows, send **one** prompt by the preferred channel with a resume link | No prompt without consent; draft retained regardless |
| AUT-P01-06 | Job completed | Request CSAT, NPS and a technician rating in-app and by the preferred channel (BR-CRM-005) | Request once more, then stop |
| AUT-P01-07 | Payment due or received | Notify with the amount and, on receipt, deliver the receipt to the inbox | Retry; the receipt remains retrievable |
| AUT-P01-08 | Warranty or contract approaching expiry | Present a renewal or protection-product offer in-app and, with consent, by the preferred channel, at the horizons M08 defines | In-app only |
| AUT-P01-09 | Loyalty tier changes, or points near expiry | Notify with the benefit gained or the action needed | In-app only |
| AUT-P01-10 | Backing module unavailable | Disable the affected capability, show the explanation and alternative route, and raise a platform alert to M30 | Fail closed and visible, never silent |
| AUT-P01-11 | Complaint raised | Acknowledge immediately with a reference and an expected response time, and route to M34 | Acknowledge; escalate the routing failure |
| AUT-P01-12 | Trade-in offer issued by M14 | Notify the customer, present the offer with its validity period, and enable acceptance and collection booking | In-app only |

---

## 12. Module Interfaces

### 12.1 Modules P01 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, session, MFA, step-up, consent enforcement | OIDC via gateway |
| M28 Integration Platform | Every API call; rate limits, versioning, observability | Gateway |
| M33 Party Master | Customer identity, addresses, preferences, consent | REST |
| M17 Asset Registry | Device resolution, my-devices list, service history, warranty state | REST |
| M01 Service Order | Booking creation, status, estimate, completion | REST + events |
| M02 Field Service | Slot availability, technician position and ETA | REST + stream |
| M03 Logistics | Pick-and-drop scheduling and consignment status | REST |
| M11 Pricing | Indicative price and final price display | REST |
| M20 Receivable & Billing | Invoice, receipt, payment initiation, refund status | REST |
| M08 Contracts | Contract, entitlement, scheduled visits, renewal quotation | REST |
| M09 Warranty | Protection products, claim submission and status | REST |
| M10 Loyalty | Tier, points, vouchers, referral, redemption | REST |
| M37 / M38 Catalogue & E-Commerce | Service and product catalogue, shopfront, cart, checkout | REST |
| M13 Rental | Rental availability and booking | REST |
| M14 Trade-In & Refurbishment | Trade-in submission and offer | REST |
| M06 Data Services | Data-recovery case request and status, destruction certificates | REST |
| M18 E-Waste | Collection booking and drop-off points | REST |
| M27 Communications | Notification inbox, live chat, in-app calling, push registration | REST + WebSocket |
| M32 Conversational AI | The Bengali and English AI assistant | Embedded SDK |
| M61 Knowledge Management | Knowledge base and FAQ content | REST |
| M34 Customer Experience | Review, rating and complaint submission | REST |
| M65 Localisation | Locale, currency, translation bundles | Build-time + REST |
| M64 MDM | Reference data: fault categories, address hierarchy | REST, cached |

### 12.2 What P01 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M01 | Service order creation, estimate decision with signature, reschedule and cancellation | Command (idempotent) |
| M33 | Registration, profile, address and preference changes; consent grant and revocation | Command |
| M17 | Device registration submissions and identifier captures | Command |
| M20 | Payment initiation and payment-result acknowledgement | Command |
| M08 | Contract renewal and purchase intent | Command |
| M09 | Warranty claim submission with evidence | Command |
| M10 | Redemption and referral-share events | Command |
| M14 | Trade-in submission with photographs | Command |
| M18 | E-waste collection booking | Command |
| M34 | CSAT, NPS, technician rating, review, complaint | Command |
| M27 | Push token registration and revocation; chat messages | Command |
| M25 / M62 | Funnel, journey and abandonment analytics events | Event stream |

### 12.3 Events P01 Consumes

| Event | Source | Effect in P01 |
|---|---|---|
| `service_order.status_changed` | M01 | Update the timeline; trigger notification |
| `estimate.issued` / `estimate.revised` | M01 / M36 | Surface the decision prompt |
| `dispatch.technician_en_route` | M02 | Enable live tracking with ETA |
| `payment.received` / `refund.processed` | M20 | Update payment state; deliver the receipt |
| `asset.warranty_expiring` | M17 | Present a protection-product offer |
| `contract.renewal_due` | M08 | Present the renewal journey |
| `loyalty.tier_changed` / `loyalty.points_expiring` | M10 | Notify and prompt |
| `tradein.offer_issued` | M14 | Present the offer |
| `claim.status_changed` | M09 | Update claim state |
| `notification.sent` | M27 | Write to the in-app inbox |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P01-01 | bKash, Nagad, SSLCOMMERZ payment gateways | Outbound redirect / SDK | Payment initiation and result; **via M20 and M28, never direct** |
| INT-P01-02 | WhatsApp Business API | Outbound | Milestone notification and conversational support; via M27 |
| INT-P01-03 | SMS gateway (Bangladesh) | Outbound | OTP and milestone notification; via M27 and M29 |
| INT-P01-04 | Firebase Cloud Messaging / APNs | Bidirectional | Push notification delivery and token management; via M27 |
| INT-P01-05 | Google Maps Platform | Outbound | Address selection, GPS capture, technician tracking map |
| INT-P01-06 | 1000FiX public web platform (Next.js + Payload CMS) | Bidirectional | Shared identity and deep links between the marketing site and the portal |
| INT-P01-07 | App stores (Google Play, Apple App Store) | Outbound | Native application distribution and rating capture (W6) |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/auth/*` | POST | OTP request, verification, token exchange, refresh | M29 |
| `/api/v1/parties/me` | GET/PATCH | Profile, addresses, preferences, consent | M33 |
| `/api/v1/assets/resolve` | POST | Resolve a submitted identifier to a device | M17 |
| `/api/v1/assets` | GET/POST | My devices; register a device | M17 |
| `/api/v1/assets/{id}/history` | GET | Customer-scoped service timeline | M17 |
| `/api/v1/availability/slots` | GET | Bookable slots by mode, location and date | M02 |
| `/api/v1/pricing/indication` | POST | Indicative price for a fault and device | M11 |
| `/api/v1/service-orders` | POST | Create a booking (idempotent) | M01 |
| `/api/v1/service-orders/{id}` | GET | Status timeline | M01 |
| `/api/v1/service-orders/{id}/estimate` | GET/POST | Retrieve and decide an estimate | M01 |
| `/api/v1/track/{token}` | GET | Public no-login tracking view | M01 |
| `/api/v1/payments/initiate` | POST | Begin a payment | M20 |
| `/api/v1/invoices` | GET | Invoices, receipts, statements | M20 |
| `/api/v1/contracts` | GET/POST | Contracts, entitlement, renewal | M08 |
| `/api/v1/warranty/claims` | POST | Submit a claim with evidence | M09 |
| `/api/v1/loyalty/me` | GET/POST | Tier, points, redemption, referral | M10 |
| `/api/v1/catalogue` | GET | Services, parts, accessories, refurbished stock | M37 / M38 |
| `/api/v1/rental/availability` | GET/POST | Rental booking | M13 |
| `/api/v1/tradein` | POST | Submit a trade-in | M14 |
| `/api/v1/notifications/inbox` | GET | In-app notification inbox | M27 |
| `/api/v1/feedback` | POST | CSAT, NPS, rating, review, complaint | M34 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R36 Customer (Individual)** | C R U | **Own records only** — own party, own devices, own jobs, own invoices, own contracts, own loyalty. This is the only role with an account on P01 |
| R36 — household member | R | Devices and jobs explicitly shared by the account holder; revocable at any time |
| Anonymous — public tracking | R | **Status and ETA of one job only**, via an expiring tokenised link; no path to any other record |
| Anonymous — pre-login browsing | R | Catalogue, service information, price indication and knowledge base only |

> **Per `05-04` §2, R36 Customer is the only role with P01 access.** No internal role signs in
> to P01. Where an agent must act on a customer's behalf, they do so in P03 or P10 under their
> own identity, and the action is attributed to them — never impersonated through P01.

**Field-level restrictions.** `unit_cost`, `total_cost`, `margin`, `internal_note`,
`technician_incentive_detail` and `model_confidence` are absent from every P01 payload
(`05-04` §5). `nid_number` and `bank_account` are never rendered. The public tracking view
carries status and ETA only.

**Authentication policy.** MFA is optional for R36 per `05-04` §1, but **step-up
authentication is mandatory** for: changing a registered phone number, initiating a refund,
transferring device ownership, and requesting account deletion. Step-up is enforced by M29, not
by P01.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Booking funnel** | Entry channel, each step entered and completed, time per step, abandonment step and reason where inferable | M25 — the primary design KPI |
| Device resolution | Attempts, automatic resolutions, manual confirmations, failures — a direct measure of M17's identity quality at the customer's hand | M25, M17 |
| Slot availability | Searches returning no slot, by mode, location and date — a capacity signal for M55 | M25, M55 |
| Price indication | Indications shown, and conversion to booking by price band — the honest measure of price sensitivity | M25, M11 |
| Estimate decision | Time to decision, approve/part-approve/decline rate by amount band | M25, M01 |
| Payment | Method selected, success, failure and failure reason by gateway | M25, M20 |
| Status enquiry deflection | Status views in P01 versus status calls to the hotline, over the same period | M25, M27 |
| Tracking link usage | Public link opens, unique openers, conversion to account creation | M25 |
| Support | Assistant sessions, escalations to live chat, resolution without escalation | M25, M32, M27 |
| Shopfront | Catalogue views, add-to-cart, checkout, abandonment | M25, M38 |
| Performance | Real-user first contentful paint, largest contentful paint and payload size by connection class | M30, M25 |
| Accessibility | Screen-reader session share, language toggle usage, text-scaling usage | M25 |
| Errors | Every user-visible error by type, screen and frequency | M30, M25 |
| Crash and stability | Native crash-free session rate, PWA service-worker failures | M30 |

> **Rule.** Instrumentation is a definition-of-done item for every journey (**PS-10**). A journey
> that ships without funnel instrumentation cannot be improved and will not be.

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Online booking rate** | **40%** | 70% | **88%** |
| — | **Booking funnel conversion** | unmeasured | 62% | **> 72%** |
| — | **Self-service status checks vs hotline calls** | ~0 | 60% | **> 80% of status enquiries** |
| — | **Portal monthly active users** | — | 70,000 | **> 120,000** |
| — | **App store rating** | — | — | **> 4.5** |
| — | Booking completion time (median) | unmeasured | < 4 min | **< 3 min** |
| — | Booking-path first load payload | unmeasured | ≤ 400 KB | **≤ 400 KB** |
| — | Page load on 3G (p75) | unmeasured | ≤ 3.5 s | **≤ 3 s** |
| — | Estimate decisions made in-portal | ~0% | 65% | **> 85%** |
| — | Digital payment share of customer payments | unmeasured | 45% | **> 70%** |
| — | Feedback response rate after service | unmeasured | 30% | **> 45%** |
| — | Registrations completing device registration | n/a | 60% | **> 80%** |
| — | Public tracking links opened per job | n/a | 0.4 | **> 0.8** |
| — | WCAG 2.1 AA automated conformance | n/a | **100%** | **100%** |
| — | Bengali string completeness | partial | **100%** | **100%** |
| **KPI-004** *(supported)* | First-time fix rate | 72% | 82% | **88%** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P01. P01 has
> **no KPI-0nn identifiers allocated** in the programme KPI register; all fifteen unnumbered
> metrics require allocation in `06-02` (not yet issued). Recorded as an audit action. KPI-004
> is owned by M02 and is shown as *supported*, not claimed.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Next.js 15 / React 19 PWA** — the primary surface; partial pre-rendering, service worker, design system | 62% |
| L5 | **React Native application** — Android primary, iOS secondary; biometric login, reliable push, store presence | 26% |
| L4 | Shared design system and component library (also serving P04, P07, P08, P10, P12) | 8% |
| L1/L2 | Odoo `portal` and `website` foundations where a rendered document or a portal-authenticated route is reused | 4% |

> P01 is almost entirely custom. This is correct: it is a consumer product competing for
> attention against consumer apps, and no ERP portal framework produces an experience that wins
> that comparison. The layered delivery model (`02-01` §5) directs exactly this case to L5.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-200** | `p01_customer_web` — PWA: account, devices, booking funnel, tracking, approvals, payments, contracts, warranty, loyalty, shopfront, support, feedback, offline shell, instrumentation | Next.js 15 application | 28 PW |
| **CD-201** | `p01_customer_app` — native application: parity surface, biometric login, push reliability, store presence, native camera and scan | React Native application | 14 PW |

> **CD register.** P01 has no allocation in `02-05` §5.2, which registers `cd_*` Odoo modules;
> `02-05` §5.4 lists portal applications separately without IDs. Two IDs, **CD-200…201**, are
> claimed from the extension block, continuing from CD-199 which is the highest ID claimed by any
> module in `03_Modules`. **All CD IDs remain provisional** pending the unified CD register required by
> audit finding M-01 in `02-05`.
>
> **Portal suite CD block.** CD-200…201 P01 · CD-202 P02 · CD-203 P03 · CD-204 P04 ·
> CD-205 P05 · CD-206 P06 · CD-207…208 P07 · CD-209 P08 · CD-210 P09 · CD-211 P10 ·
> CD-212 P11 · CD-213 P12. **CD-214 is the next free ID.**

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | Authentication and session; nothing renders without it |
| M28 Integration Platform | Every call routes through the gateway |
| M33 Party Master | A customer must exist before they can have an account |
| M17 Asset Registry | A booking requires a device identity; **the W1 identity core is the binding prerequisite** |
| M01 Service Order | The booking must land somewhere |
| M11 Pricing | Price indication; may be a simple rate card in W2 and dynamic from W3 |
| M02 Field Service | Slot availability and technician tracking |
| M27 Communications | Notification delivery and the inbox |
| M20 Receivable & Billing | Payment initiation and invoice retrieval; available W3 — **W2 launches with booking and tracking, payment follows** |
| M65 Localisation | Bengali translation infrastructure |

**Phasing within the portal.** W2 ships account, devices, booking, tracking, approvals,
support and feedback. W3 adds payment and invoices. W4 adds contracts, warranty and protection
products. W6 adds the shopfront, rental, trade-in, e-waste and the native application.

### 16.4 Migration & Cutover

| Source | Volume | Target | Wave |
|---|---|---|---|
| Existing customer portal accounts | Unknown | M33 party records with re-verification by OTP on first login | W2 |
| Legacy order-tracking system references | Active jobs at cutover | M01 with a redirect from the legacy tracking URL | W2 |
| 1000FiX Station platform users | Unknown | M33, merged by M33 deduplication | W2 |

> **Migration position.** Legacy accounts are **not** migrated with credentials. A returning
> customer re-verifies by OTP on first login, at which point M33 matches or creates the party.
> Migrating credentials from a system whose storage practice is unknown would import an unknown
> security posture into a platform that has one.
>
> The legacy tracking URL must **redirect rather than break**. Customers hold that link in
> messages and bookmarks, and a dead link at cutover produces exactly the hotline call volume
> the portal exists to remove.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A first-time customer completes a booking in under 3 minutes, median, on a mid-range Android phone on a 3G connection | Moderated usability test with 20 representative customers, in Bengali |
| AC-02 | The booking path first load is ≤ 400 KB and the CI budget check fails the build on regression | Build pipeline evidence |
| AC-03 | Page load is ≤ 3 s at p75 on a throttled 3G profile across every critical journey | Synthetic and real-user performance measurement |
| AC-04 | The portal sustains 50,000 concurrent users without degradation | Load test at NFR-004 volume |
| AC-05 | No price, entitlement or eligibility value is computed in client code | Code review plus a runtime assertion that all such values carry a server provenance marker |
| AC-06 | P01 persists no authoritative business object; clearing local storage loses nothing but a draft | Schema and storage audit |
| AC-07 | A retried submission on a flaky connection creates exactly one booking, one approval and one payment | Idempotency test with induced network failure |
| AC-08 | The public tracking link exposes status and ETA only, and no request from it reaches any other record | Penetration test on the tracking endpoint |
| AC-09 | No P01 response payload contains cost, margin or internal notes | Automated payload inspection across every endpoint |
| AC-10 | A customer cannot access another customer's records through any path, including direct object reference | Tenant-isolation penetration test |
| AC-11 | No card or wallet credential is stored, logged or transmitted by P01 | PCI-scope review and log inspection |
| AC-12 | Every user-visible string, including every error, renders in Bengali | Translation coverage report at 100% (AS-12) |
| AC-13 | The portal opens in Bengali by default and the English toggle persists per user | Scripted test |
| AC-14 | WCAG 2.1 AA conformance across every critical journey, including correct language tagging on mixed-script elements | Automated scan plus manual screen-reader audit in Bengali |
| AC-15 | Every journey is usable from 320 px width with no horizontal scrolling | Responsive test matrix |
| AC-16 | The offline shell serves the device list and open job statuses, stamped with the fetch time | Offline test |
| AC-17 | Every critical journey step emits its analytics event, and the funnel reconciles end to end in M25 | Funnel reconciliation report |
| AC-18 | With a backing module deliberately unavailable, the affected capability is disabled with an explanation and an alternative route — no blank screen, no stack trace | Chaos test against each backing module |
| AC-19 | A slot offered in P01 is always servable; no booking is created against phantom capacity | Reconciliation of offered slots against M02 capacity over 30 days |
| AC-20 | The legacy tracking URL redirects correctly for every job open at cutover | Cutover verification |
| AC-21 | Online booking reaches 88% and funnel conversion exceeds 72% | Six consecutive monthly reports |
| AC-22 | The native application introduces no business capability absent from the PWA | Feature parity review |
| AC-23 | CCO and Customer Service Manager sign off UAT, conducted in Bengali with real customers | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3 plus the 23 criteria
above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many accounts exist on the current customer portal and 1000FiX Station, and what is the overlap? This sizes the re-verification wave at cutover | CCO / CTO | W2 minus 3 months |
| Q-02 | Can the legacy tracking URL be redirected, and who controls that domain and its DNS? | CTO | **W2 minus 3 months** |
| Q-03 | What is shown as an indicative price before diagnosis — a range, a starting-from figure, or nothing — and who owns the commercial risk of that number? | CCO / CFO | W2 design |
| Q-04 | Is a booking permitted without login, with identity captured at confirmation? This is the single largest funnel decision in the portal | CCO | **W2 design** |
| Q-05 | What is the cancellation and reschedule policy window, and is any charge applied? | CCO / Operations Director | W2 design |
| Q-06 | Which payment gateways are contracted, on what settlement terms, and does any require a redirect that breaks the in-app journey? | CFO / CTO | W3 |
| Q-07 | Is WhatsApp the primary notification channel, and what is the cost per message at 250,000 customers per month? | CCO / CFO | W2 design |
| Q-08 | What consent purposes must be presented separately, and has Legal approved the Bengali wording? | CCO / Legal | **W2 minus 2 months** |
| Q-09 | Does the household-member feature create a privacy exposure the Company is willing to accept, and how is it revoked? | CCO / Legal | W6 design |
| Q-10 | Is the native application Android-only at first release, given the Bangladesh device mix? | CCO / CTO | W6 scoping |
| Q-11 | Who owns the Bengali content voice — Marketing, or a dedicated content designer? Machine translation is excluded by `04-00`, so this is a resourcing question | CCO / Marketing Head | **W2 minus 3 months** |
| Q-12 | What is the retention period for booking drafts, photographs and voice notes attached to abandoned bookings? | CCO / Legal / CFO | W2 build |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §1 (the portal principle),
§P01 (capability set, design requirements, KPIs), §3 (PS-01…PS-12), §4 (coverage matrix) ·
`P02_Technician_Mobile_Application.md` · `P03_Admin_Operations_Portal.md` ·
`P04_Corporate_B2B_Portal.md` · `P10_Contact_Centre_Agent_Console.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md` ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`
§5.8, §12.2, §13 (BRU-AST-20) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §5, §10 (AS-01, AS-08, AS-12, AS-14) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.4 (portal applications) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 (FR-POR allocation) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §2 (portal access), §5 ·
`03_Modules/K_Platform_and_Technology/_CATEGORY_OVERVIEW.md` §7 (the platform contract)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 1, BR-SRM-001,
BR-SRM-009, BR-SRM-012, BR-FSM-014, BR-CRM-002, BR-CRM-005, BR-CRM-006, BR-FIN-004,
BR-CWM-005, BR-CWM-010, NFR-001, NFR-004 ·
`1000FiX_Services_Company_Profile.md` §Digital Presence & Customer Portal, §Customer Benefits,
§Competitive Advantages

**External benchmark**
[Customer self-service portals — design for full resolution, not information](https://www.zendesk.com/service/help-center/customer-self-service/) ·
[IT self-service portal best practices — end-to-end flows and role-aware personalisation](https://monday.com/blog/service/it-self-service-portal/) ·
[Field-service customer portals — scheduling, service history and real-time technician tracking](https://field-ascend.com/en-us/why-your-customers-want-a-customer-portal) ·
[Field service platforms with customer portals — self-service request creation into the work-order queue](https://fieldpathpro.com/blog/customer-portal-field-service-platforms-2025) ·
[Field service management best practices 2026](https://www.fieldex.com/en/blog/field-service-management-best-practices) ·
[Customer self-service portal examples and patterns](https://www.clinked.com/blog/customer-self-service-portals) ·
[Next.js 15 enterprise portals — partial pre-rendering and streaming](https://www.indujitechnologies.com/blog/nextjs-15-vs-react-19-enterprise-portal) ·
[Next.js 15 for enterprise customer portals](https://sprintlabs.tech/blog/p/tech-comparison-enterprise-customer-portal-nextjs) ·
[WCAG 2.1 AA success criteria](https://www.levelaccess.com/blog/wcag-2-1-exploring-new-success-criteria/) ·
[WCAG 3.1.2 Language of Parts](https://www.wcag.com/developers/3-1-2-language-of-parts/) ·
[Multilingual accessibility — language tagging for Bengali and other Indic scripts](https://www.skynetindia.info/blog/multilingual-accessibility-india/) ·
[Accessible design systems at scale](https://humanmade.com/accessibility/accessible-design-systems-scaling-inclusive-design/)

---

*Portal P01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
