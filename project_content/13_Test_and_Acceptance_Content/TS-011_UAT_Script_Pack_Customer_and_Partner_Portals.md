---
id: TS-011
title: UAT Script Pack — Customer and Partner Portals
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Owners Forum with QA Lead
author: QA Lead with portal owners, Content Design and Localisation
reviewers: [CCO delegate, Customer Service Manager, Account Manager representatives, Procurement Officer, Marketplace Operations Officer, Content Design Lead, Localisation Lead, Accessibility reviewer, Security Lead]
approver: Content Design Lead with CCO delegate
content_class: D
purpose: >
  The acceptance scripts executed as the external parties themselves — a customer, a corporate
  administrator, a vendor, a marketplace seller, a brand partner, a courier and a referral partner —
  on the six portals they use. External-facing defects are found by external users: the first person
  to discover that a seller can see another seller's payout, or that a corporate approver can approve
  their own request, or that the Bengali booking flow breaks at step three on a 3G connection, will
  be someone outside the company, and by then it is an incident rather than a defect. The company
  must find them first, by being them.
traces_to: [P01, P04, P05, P07, P08, P09, P12, M07, M08, M09, M10, M12, M13, M14, M17, M20, M27, M33, M38, M40, 05-04, 05-04 §8, 05-05, 05-06 §5, 06-02 §4, UI-011, UI-014, UI-015, UI-017, UI-018, UI-019, UI-022, UI-037, UI-038, UI-039, UI-040, UI-042, HC-003, HC-006, HC-007, HC-009, HC-010, HC-014, LG-002, EO-001, TS-001, TS-002, TS-006, TS-007, TS-012, TS-015, TS-016, TS-017, TS-018]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: TS-011_UAT_Script_Pack_Customer_and_Partner_Portals_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P01 capability set and design requirements (Bengali-first with English toggle, 3G, first-load payload under 400 KB on the booking path, WCAG 2.1 AA, booking in ≤ 3 steps); P04, P05, P07, P08, P12 capability sets and KPIs; §3 PS-01…PS-12
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.7 external roles (R36 250,000+/month, R37 500–2,000, R38 1,000–3,000); §8 External Party Access Rules EA-01…EA-12
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 2 G2-08 online booking ≥ 60% at pilot sites; Gate 4 G4-05 ten or more corporate clients transacting on the B2B portal; Gate 7 G7-01…G7-04; §2.3 KPI-020…027
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — Customer and Partner Portals

| Item | Value |
|---|---|
| Test level | **UAT** — method in [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 |
| Roles executing | `R36` `R37` `R38` — **3 registered roles covering 7 distinct external audiences** |
| Portals covered | `P01` `P04` `P05` `P07` `P08` `P09` `P12` — **7 portals** |
| Modules covered | `M07`–`M14`, `M17`, `M20`, `M27`, `M33`, `M38`, `M40` as surfaced externally |
| Environment | `UAT` — frozen for the cycle |
| Test data set | `TS-002` — personas 1, 4, 5, 6, 7, 8, 11 |
| Wave | W2, extending to W7 for `P07` and `P12` — open item `O-01` |

> **Template conformance.** As `TS-006`: `TPL_Test_Script.md` at pack level, all six sections
> retained in order with pack-level interpretation.

> **Method by reference.** `UA-01`…`UA-18` (`TS-006` §2.1), `UA-19`–`UA-22` (`TS-007` §2.1). This
> pack adds `UA-36`…`UA-41` (§2.1), which exist because the executor is not an employee.

---

## 1. Traceability

### 1.1 The problem this pack has that no other pack has

Every other UAT pack has a real executor: a named super-user who does the job every day and knows
what right looks like. **This one does not.** A customer cannot be a super-user, a brand partner is
not on the payroll, and 250,000 monthly customers cannot be represented by an internal proxy who
knows where the buttons are.

That produces a specific failure: **an employee executing a customer script passes it, because they
know what the system expects.** The defects that matter on `P01` — a booking flow that loses a
Bengali-speaking first-time user at step three, a payment path that times out on 3G, a tracking link
that assumes login — are invisible to anyone who has seen the screen before.

Four consequences, stated as rules in §2.1:

| Consequence | Rule |
|---|---|
| Scripts are executed by people who have **not seen the system** | `UA-36` |
| The **device and network** the audience actually uses are part of the script | `UA-37` |
| Where a real counterparty exists — 17+ brands, vendors, corporate clients — **they execute their own** | `UA-38` |
| Every external script proves the **scope boundary**, not just the task | `UA-39` |

### 1.2 Traceability obligation

Per `TS-006` §1.2, with three required columns:

| Field | Source |
|---|---|
| **Portal and copy pack** | `Pnn` and the `UI` pack the labels are quoted from — `UI-011`, `UI-014`, `UI-015`, `UI-017`, `UI-018`, `UI-019`, `UI-022`, plus the critical-flow packs `UI-037`…`UI-042` |
| **External access rule** | The `EA-01`…`EA-12` rule the script's scope check exercises (`05-04` §8) |
| **Help set** | The `HC` set that supports the task, so a script that cannot be completed without help is distinguishable from one that fails |

### 1.3 Audience coverage

**Seven audiences, three registered roles.** `05-04` §1.7 collapses vendor, seller, brand, courier,
referral and recycling partners into a single `R38`; this pack keeps them separate because their
scripts, their scope rules and their agreements differ.

| Audience | Role | Portal | Population | Scripts | `P0` | Language | Help set |
|---|---|---|---:|---:|---:|---|---|
| **Customer** | `R36` | `P01` | 250,000+/month | **18** | 10 | **Bengali** | `HC-003` |
| **Corporate administrator** | `R37` | `P04` | 500–2,000 | 14 | 7 | English | `HC-006` |
| **Marketplace seller** | `R38` | `P07` | 500–2,000 | 12 | 6 | **Bengali** | `HC-009` |
| **Brand partner** | `R38` | `P08` | 17+ organisations | 10 | 5 | English | `HC-010` |
| **Vendor / supplier** | `R38` | `P05` | 200–500 | 8 | 4 | English | `HC-007` |
| **Referral / channel partner** | `R38` | `P12` | 100–500 | 6 | 2 | Bengali or English | `HC-014` |
| **Courier partner** | `R38` | `P09` | part of 200–500 | 4 | 2 | **Bengali** | `HC-011` |
| **Total** | | **7 portals** | | **72** | **36** | | |

---

## 2. Preconditions

### 2.1 Additional rules for external-audience scripts

| # | Rule |
|---|---|
| **UA-36** | **A customer script is executed by someone who has not seen the system before.** For `P01`, at least half the `P0` executions are by first-time users recruited from outside the programme, briefed on the *task* and not on the screen. An internal proxy execution is recorded as a proxy and does not satisfy exit |
| **UA-37** | **The device and the network are part of the script.** `P01` on a mid-range Android over 3G; `P07` and `P09` likewise; `P04` and `P08` on a desktop browser from the audience's list. A customer path tested on office fibre is not tested (`PS-07`, `NFR-081`) |
| **UA-38** | **Where a real counterparty exists, they execute their own scripts.** 17+ brand partners, named vendors, and the 10+ corporate clients `G4-05` requires. A proxy cannot confirm that a brand's claim workflow fits the brand's process |
| **UA-39** | **Every external script proves the scope boundary as a numbered step**: the executor attempts to reach another party's record and is refused (`EA-01`…`EA-12`). This is not optional and is not deferred to `TS-017` — see the boundary note below |
| **UA-40** | **Consent and preference behaviour is verified on every audience that has a choice.** Under the Personal Data Protection Act 2026 a transparency notice, a withdrawal path and a rights request must all work, not merely exist (`NFR-090`…`093`) |
| **UA-41** | **An external script that cannot be completed without contacting the company is a failure**, recorded against the portal, not against the executor. Self-service that requires a phone call is the thing these portals exist to remove (`KPI-025`) |

> **Boundary with `TS-017`.** `TS-017` proves **systematically** that all 379 denied `role × portal`
> cells and every `T0`–`T5` isolation tier hold, from the inside, by construction. `UA-39` proves
> **experientially** that a real external user, holding real credentials, cannot reach another
> party's data by the routes a real user would try — a shared link, a browser back button, a bookmarked
> URL, an exported file. **The two are different tests of the same rule and neither replaces the
> other**; the counting of denied cells belongs to `TS-017` alone (`CP-01`).

### 2.2 Additional preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-006` preconditions 1–4, 7, 9, 11 met | Exit records |
| 2 | **First-time-user executors recruited and briefed on tasks only** | `UA-36` — **no process exists**, `O-02` |
| 3 | Mid-range Android 11 devices with 3 GB RAM, and a throttled 3G connection | `UA-37`; `NFR-017`, `NFR-036` |
| 4 | Real counterparty participation agreed: brands, vendors, 10+ corporate clients | `UA-38`; `G4-05` — **not arranged**, `O-03` |
| 5 | `UI-011`, `UI-014`, `UI-015`, `UI-017`, `UI-018`, `UI-019`, `UI-022` and `UI-037`…`UI-042` published | `UA-08` |
| 6 | `HC-003`, `HC-006`, `HC-007`, `HC-009`, `HC-010`, `HC-011`, `HC-014` help sets available | `UA-41` — **all seven are specifications; the articles are unwritten**, `O-04` |
| 7 | `LG-002` Portal Terms of Use accepted by the customer executor, with the acceptance recorded | `LG-002`; `LG-001` sign-off log |
| 8 | Payment gateways in sandbox: bKash, Nagad, card, bank transfer | `TS-002` `M-05` |
| 9 | Two accounts per audience, belonging to **different** parties, for every `UA-39` scope check | `TS-002` `O-04` |
| 10 | A corporate account with a multi-level approval chain, four sites and three departments | `MD-015`; `P04` |
| 11 | Bengali interface complete on `P01`, `P07` and `P09` | `PS-03`; `KPI-092` |

---

## 3. Scripts

### 3.1 Block A — Customer, `R36` on `P01` · 18 scripts

**Bengali-first** · 250,000+/month · `HC-003` · `UI-011`, `UI-037`…`UI-042`

| Script | The job, as the customer | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R36-001` | **Register with a phone OTP and accept the terms** — first-time user, Bengali, 3G | `LG-002`; `UI-040`; `UA-36` `UA-37` | **P0** |
| `UAT-R36-002` | **Book a service in three steps or fewer**, describing the fault with a photo | `P01` design requirement; `UI-037`; `G2-08` | **P0** |
| `UAT-R36-003` | Register a device by serial, by IMEI and by photo | `M17`; `TS-002` `D-01`, `D-02` | **P0** |
| `UAT-R36-004` | Check whether your device is in warranty and understand the answer | `MD-031`; `HC-003` | **P0** |
| `UAT-R36-005` | **Track a job from a link, without logging in** | `P01` public tracking link; `EA-01` | **P0** |
| `UAT-R36-006` | **Approve, part-approve and decline an estimate, and e-sign** | `BRU-SRM-07`(H); `UI-038` | **P0** |
| `UAT-R36-007` | **Pay by bKash, then by card, and get a receipt you can read in Bengali** | `NFR-042`; `UI-039`; `DT-016` | **P0** |
| `UAT-R36-008` | **Attempt to see another customer's job, invoice or device, and be refused** — by shared link, back button and bookmarked URL | `EA-01`, `EA-02`; `UA-39` | **P0** |
| `UAT-R36-009` | **Withdraw consent and make a data-access request, and see both take effect** | `NFR-092`, `NFR-093`; `UI-042`; `UA-40` | **P0** |
| `UAT-R36-010` | Complete the whole booking-to-payment path on a mid-range Android over 3G, **with the booking path under 400 KB first load** | `NFR-081`; `PS-07`; `UA-37` | **P0** |
| `UAT-R36-011` | Submit a warranty claim and follow its status | `M09`; `HC-003` | P1 |
| `UAT-R36-012` | Buy a warranty extension, and see the exclusions before buying | `BRU-WTY-07`(H); `MD-031` | P1 |
| `UAT-R36-013` | View an AMC contract, its entitlement balance and its visit calendar; renew it | `M08`; `P04`-parity check | P1 |
| `UAT-R36-014` | See your Privilege status and points, redeem points, and share a referral link | `MD-034`; `M10` | P1 |
| `UAT-R36-015` | Buy a part and a refurbished device, and return one | `M38`; `BRU-TRF-04`(H) | P1 |
| `UAT-R36-016` | Submit a trade-in with photos, accept an offer, arrange collection | `M14`; `DT-038` | P1 |
| `UAT-R36-017` | Ask the AI assistant a question in Bengali, then reach a human with the context intact | `M32`; `HC-018`, `HC-019` | P1 |
| `UAT-R36-018` | Rate the service, write a review, raise a complaint and track it | `BRU-QMS-04`(H); `KPI-020` | P2 |

### 3.2 Block B — Corporate administrator, `R37` on `P04` · 14 scripts

500–2,000 users · English · `HC-006` · `UI-014`

| Script | The job, as the client | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R37-001` | Add users under one corporate account and assign their roles | `P04` Account; `EA-03` | **P0** |
| `UAT-R37-002` | **Raise a bulk service request by CSV upload with 40 rows, 6 invalid — and see each invalid row reported individually** | `NFR-041`; `P04` under 5 minutes | **P0** |
| `UAT-R37-003` | **Validate a request against contract coverage before submission, and be told when it is out of scope** | `BRU-CTR-02`(H) `BRU-CTR-04`(H) | **P0** |
| `UAT-R37-004` | Approve an estimate within your delegated authority, and **be refused beyond it** | `05-04` §7; `UA-10` | **P0** |
| `UAT-R37-005` | **Try to approve your own request where the approval chain forbids it, and be refused** | `P04` multi-level chain; `SOD` principle | **P0** |
| `UAT-R37-006` | **Attempt to see another company's data, and be refused; then attempt to see a department outside your role within your own company** | `EA-03`; `UA-39` | **P0** |
| `UAT-R37-007` | Bulk upload 340 assets and assign them to sites, departments and users | `TS-002` `D-08`; `NFR-041` | **P0** |
| `UAT-R37-008` | Read a consolidated invoice, check it against your own records, and dispute a line | `DT-020`; `BRU-BIL-07`(H); `KPI` disputes < 3% | P1 |
| `UAT-R37-009` | See real-time SLA status per request, breach history and service credits earned | `DT-031`; `BRU-CTR-08`(C/A) | P1 |
| `UAT-R37-010` | See your estate health, open incidents and patch compliance | `M05`; `P04` managed services | P1 |
| `UAT-R37-011` | Run scoped analytics on your own estate and export it | `P04` Reporting; `PRU-P06-03`(H) | P1 |
| `UAT-R37-012` | Order parts against agreed pricing, and request a rental | `MD-029`; `M13` | P1 |
| `UAT-R37-013` | Download a destruction certificate and a service evidence pack | `DT-034`; `DT-035` | P1 |
| `UAT-R37-014` | **Confirm you cannot see cost, margin or any internal note anywhere in the portal** | `EA-02`; `05-04` §5 | P2 |

### 3.3 Block C — Marketplace seller, `R38` on `P07` · 12 scripts

**Bengali** · 500–2,000 · `HC-009` · `UI-017` · **W7 block**

| Script | The job, as the seller | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R38-P07-001` | Register as a freelance engineer: submit NID and trade licence, verify by OTP, sign the agreement digitally | `BRU-ECM-01`(H); `UI-040`; `EO-001` | **P0** |
| `UAT-R38-P07-002` | **Attempt to transact before approval, and be refused at every entry point** | `BRU-ECM-01`(H) | **P0** |
| `UAT-R38-P07-003` | **Attempt to list in a category you hold no verified qualification for, and be refused** | `BRU-ECM-07`(H) | **P0** |
| `UAT-R38-P07-004` | See a broadcast job, quote, win it, and complete it with evidence and customer sign-off | `BRU-ECM-03`(H) `BRU-FSM-12`(H) | **P0** |
| `UAT-R38-P07-005` | **Attempt to see another seller's listings, earnings or payout, and be refused** | `EA-01`, `EA-04`; `UA-39` | **P0** |
| `UAT-R38-P07-006` | Read your payout statement and reconcile it to your completed jobs, to the paisa | `DT-039`; `UA-19` `UA-21`; `G7-02` | **P0** |
| `UAT-R38-P07-007` | **Confirm your access to a customer's contact data expires after the defined period post-completion** | `BRU-ECM-05`(H) `EA-04` | P1 |
| `UAT-R38-P07-008` | See your scorecard and understand what falls below threshold and what happens then | `BRU-ECM-04`(C); `HC-009` | P1 |
| `UAT-R38-P07-009` | Raise a dispute with evidence and follow its decision | `BRU-ECM-09`(H) | P1 |
| `UAT-R38-P07-010` | Buy a boost, and confirm the listing is disclosed as promoted | `BRU-ECM-06`(H) | P1 |
| `UAT-R38-P07-011` | Respond once to a customer review, and confirm you cannot respond twice | `BRU-ECM-02`(H) | P1 |
| `UAT-R38-P07-012` | Do the whole registration and first job in Bengali on a mid-range Android | `PS-03`, `PS-07`; `UA-37` | P2 |

### 3.4 Block D — Brand partner, `R38` on `P08` · 10 scripts

17+ organisations · English · `HC-010` · `UI-018` · **`UA-38` applies — the brands execute these**

| Script | The job, as the brand | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R38-P08-001` | **Receive a claim with its full evidence pack and judge whether it is sufficient** | `BRU-WTY-01`(H); `DT-033`; `UA-38` | **P0** |
| `UAT-R38-P08-002` | Approve, part-approve, reject with a reason, and request more information | `AUT-020` | **P0** |
| `UAT-R38-P08-003` | **Attempt to see service data or claims for a brand that is not yours, and be refused** | `EA-05`; `UA-39` | **P0** |
| `UAT-R38-P08-004` | Upload remittance advice and resolve a difference against submitted claims | `AUT-021` | **P0** |
| `UAT-R38-P08-005` | Publish and version a rate card, and confirm which version applied to a claim already submitted | `MD-029`; `CG-006` §5; `TS-007` `N-01` | **P0** |
| `UAT-R38-P08-006` | View consignment parts supplied, their consumption, and request replenishment | `BRU-INV-04`(C) `BRU-WTY-04`(H) | P1 |
| `UAT-R38-P08-007` | View 1000FiX service performance on your brand, and confirm the figures against your own records | `SL-26`; `KPI` per brand | P1 |
| `UAT-R38-P08-008` | Check the certification status of technicians authorised on your brand | `BRU-HRM-01`(H); `G5-03` | P1 |
| `UAT-R38-P08-009` | Raise a quality concern and view the CAPA response | `BRU-QMS-02`(H) | P1 |
| `UAT-R38-P08-010` | Issue a technical bulletin or a recall notification to 1000FiX | `KB-010` | P2 |

### 3.5 Block E — Vendor / supplier, `R38` on `P05` · 8 scripts

200–500 · English · `HC-007` · `UI-015` · **`UA-38` applies**

| Script | The job, as the vendor | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R38-P05-001` | Register, submit documents, and track approval to activation | `BRU-SCM-02`(H); `EO` kit | **P0** |
| `UAT-R38-P05-002` | Receive an RFQ and submit a quotation with price, lead time and validity | `DT-022` | **P0** |
| `UAT-R38-P05-003` | Receive a PO, acknowledge it, and confirm a delivery date | `DT-023`; `AUT-032`; `EA-06` | **P0** |
| `UAT-R38-P05-004` | **Attempt to see another vendor's PO, price or scorecard, and be refused** | `EA-01`, `EA-06`; `UA-39` | **P0** |
| `UAT-R38-P05-005` | Submit an invoice against a PO and track its matching status to a payment date | `BRU-SCM-01`(H) | P1 |
| `UAT-R38-P05-006` | See a rejection outcome from inspection and respond to it | `BRU-INV-07`(H); `DT-024` | P1 |
| `UAT-R38-P05-007` | Read your own scorecard and identify the events behind the score | `KPI-048`; `SL-26` | P1 |
| `UAT-R38-P05-008` | **Attempt a bulk export and confirm it is limited, rate-controlled and logged** | `EA-12` | P2 |

### 3.6 Block F — Referral / channel partner, `R38` on `P12` · 6 scripts

100–500 · `HC-014` · `UI-022` · **W7 block**

| Script | The job, as the partner | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R38-P12-001` | Apply, submit documents, sign the partner agreement, get approved | `M40`; `UA-22` | **P0** |
| `UAT-R38-P12-002` | Generate a referral link, submit a lead, and track it to conversion | `AUT-030`; `KPI-035` | **P0** |
| `UAT-R38-P12-003` | Read a commission statement and reconcile it to converted referrals | `DT-040`; `UA-19` `UA-21` | P1 |
| `UAT-R38-P12-004` | **Attempt to see another partner's leads or commission, and be refused** | `EA-01`; `UA-39` | P1 |
| `UAT-R38-P12-005` | As a reseller, view refurbished stock allocation, order, and track settlement | `M14`; `M40` | P1 |
| `UAT-R38-P12-006` | Confirm a commission reversal after a referred transaction is refunded | `BRU-BIL-04`(C) | P2 |

### 3.7 Block G — Courier partner, `R38` on `P09` · 4 scripts

**Bengali** · `HC-011` · `UI-019`

| Script | The job, as the courier | Rules and criteria | Pri |
|---|---|---|:--:|
| `UAT-R38-P09-001` | Receive a consignment booking and update its status | `EA-07`; `M03` | **P0** |
| `UAT-R38-P09-002` | Upload a POD and complete a handover with OTP and signature | `BRU-LOG-01`(H) `BRU-LOG-02`(H); `DT-028` | **P0** |
| `UAT-R38-P09-003` | **Attempt to see a consignment not assigned to you, or any data beyond the minimum needed to deliver, and be refused** | `EA-07`; `UA-39` | P1 |
| `UAT-R38-P09-004` | Submit a settlement claim | `M20`; `EA-06` | P1 |

**Pack total: 72 scripts · 36 at `P0` · 27 at `P1` · 9 at `P2`.**

### 3.8 Negative and edge cases

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | Session expires mid-booking on `P01` | Draft preserved or the loss stated clearly; **never a silent reset to step one** (`NFR-069`, `PS-09`) |
| N-02 | 3G drops during payment | Idempotent; one charge, one receipt; the customer told the true state (`DI-05`, `NFR-042`) |
| N-03 | Two household members act on the same job simultaneously | Server-authoritative; the loser told what happened (`PS-11`) |
| N-04 | Customer shares a tracking link publicly | Link exposes only what a tracking link should — no contact details, no invoice, no other job (`EA-01`) |
| N-05 | Corporate user removed from a company while holding an open approval | Approval reassigned per the chain; **not left pending on a revoked account** (`05-04` §9) |
| N-06 | Seller suspended while holding an open job | Job completes under supervision; the customer is not stranded (`TS-007` `N-05`) |
| N-07 | Brand partner's rate card changes between claim submission and decision | The version at submission applies, and both parties can see which (`CG-006` §5) |
| N-08 | External API credential used with a widened scope parameter | Scope cannot be widened by request parameter (`EA-11`) |
| N-09 | External session idles past 30 minutes | Timed out (`EA-08`); the policy comes from `M29`, not the portal (`PS-12`) |
| N-10 | External party attempts a financially consequential action without MFA | Refused (`EA-09`) |
| N-11 | Every external access to customer personal data | Logged and reportable (`EA-10`) |
| N-12 | Customer requests erasure while a job is open and an invoice is unpaid | Rights request honoured within legal and contractual constraints, with the constraint explained (`NFR-093`, `NFR-088`) |

### 3.9 Bilingual check

**Bilingual pack.** Bengali is the execution language for the customer, seller and courier blocks —
by far the largest populations in scope.

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| `P01` booking, estimate, payment and consent flows (`UI-037`…`UI-039`, `UI-042`) | ● | ● | ● on a 5-inch device at 3G |
| `P07` registration and job flow (`UI-017`, `UI-040`) | ● | ● | ● |
| `P09` courier handover (`UI-019`) | ● | ● | ● |
| Every validation and error message an external user can reach (`UI-004`) | ● | ● | **● — `PS-09` requires it to say what happened and what to do next, in the user's language** |
| Terms of Use at acceptance (`LG-002`, `BN-015`) | ● | ● | ● |
| Receipt, invoice and statement as received (`DT-010`, `DT-016`, `DT-017`) | ● | ● | ● |
| Amount grouping — `12,34,567` (`05-06` §9) | ● | ● | ● |
| Help articles reached from the flow (`HC-003`, `HC-009`) | ● | ● | ● |

---

## 4. Exit Criteria

`TS-006` §4 applies. Additional:

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100%** |
| `P1` scripts passed | ≥ 98% |
| **`P01` `P0` executions by first-time users** | **≥ 50%** (`UA-36`); proxy executions recorded separately and excluded from this figure |
| Executions on the audience's real device and network | 100% where `UA-37` applies |
| **Real-counterparty executions** | ≥ 1 brand, ≥ 1 vendor and **≥ 10 corporate clients** (`UA-38`; `G4-05`) |
| **Scope-boundary refusals** | **100% of the 7 audiences, by all four routes** — shared link, back button, bookmarked URL, export (`UA-39`) |
| Consent, withdrawal and rights-request verifications | 100% of audiences with a choice (`UA-40`) |
| Scripts requiring a phone call to complete | **Zero** (`UA-41`) |
| `P01` booking path first load | **Under 400 KB** (`NFR-081`) |
| Booking completable in ≤ 3 steps | Confirmed by a first-time user |
| Bengali execution of the customer, seller and courier `P0` sets | **100%** |
| Open Critical defects | Zero |
| Open High defects on any external-scope boundary | **Zero, and not deferrable** — a scope leak is a breach, not a defect (§5) |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Two automatic escalations, and one non-deferral:**

| Trigger | Escalation |
|---|---|
| Any defect where an external party can reach another party's data, by any route | **Critical** to CTO, Chief Data Officer and Security Lead; **not deferrable**. `EA-01`/`EA-02` are absolute, and under the Personal Data Protection Act 2026 this is a breach with an Authority notification obligation (`NFR-094`) |
| Any defect where a first-time user could not complete a `P0` customer task | **High minimum**, to the Content Design Lead and the portal owner — not to the executor. `KPI-022` targets 88% online booking and `KPI-025` 80% deflection; a task a new user cannot complete makes both unreachable |

---

## 6. Sign-off

| Audience | Executor / representative | Portal | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|---|
| Customer | Customer Service Manager on behalf of the first-time-user cohort | `P01` | | | | |
| Corporate administrator | Named client representative | `P04` | | | | |
| Marketplace seller | Marketplace Operations Officer with a named seller | `P07` | | | | |
| Brand partner | Named brand representative | `P08` | | | | |
| Vendor | Named vendor representative | `P05` | | | | |
| Referral partner | Named partner representative | `P12` | | | | |
| Courier partner | Named courier representative | `P09` | | | | |
| **Pack acceptance** — CCO delegate | | | | | | |
| **Content and accessibility** — Content Design Lead | | | | | | |

> **The customer row is deliberately signed by an employee.** A first-time-user cohort cannot hold
> accountability for an acceptance gate. What the cohort produces is *evidence*; the Customer Service
> Manager signs that the evidence was gathered as `UA-36` requires and that the outcome is
> acceptable. Recording this prevents the cohort's participation being treated as sign-off.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This pack spans W2 to W7 and is registered at W2.** `P01`, `P04` and `P05` blocks fall in W2–W3; `P07` and `P12` are W7 portals evidencing `G7`. `UA-16` requires a signature per audience per release, so a single sign-off is impossible. Same shape as `TS-007` `O-01` | Programme Content Lead with QA Lead | **W2 — register decision** |
| **O-02** | **`UA-36` requires first-time users and no process exists to recruit, brief, consent or compensate them.** Half the `P01` `P0` executions depend on it, and the people involved are not employees — which raises a data-protection question about their accounts and any data they enter. **Without this the customer block is executed by proxy and its most valuable defects are not found** | Customer Service Manager with Legal Counsel | **W2 — before the cycle** |
| **O-03** | **`UA-38` real-counterparty participation is not arranged.** `G4-05` requires 10+ corporate clients transacting; brands and vendors must judge their own workflows. **Asking a brand partner to execute UAT is a commercial conversation, not a test-planning one**, and nobody owns it | CCO delegate with Account Management | **W2 for vendors and corporates; W4 for brands** |
| **O-04** | **All seven help sets are specifications; their articles are unwritten.** `AUDIT-010` records that `HC-003`…`HC-014` enumerate articles that do not exist. `UA-41` classifies a script needing a phone call as a failure — **but a script needing a help article that does not exist will fail for the wrong reason**, and the diagnosis will land on the portal | Content Design Lead | **W2** |
| **O-05** | **`LG-002` is written and the remaining 22 `LG` files are not.** Precondition 7 requires terms accepted and recorded; `LG-001` provides the sign-off log. **But `P05`, `P07`, `P08` and `P12` each need their own agreement** — seller agreement, vendor terms, brand agreement, partner agreement — and none exists, so `UA-22` cannot be discharged for four audiences | Legal Counsel | **W2 for `P05`; W4 for `P08`; W7 for `P07` and `P12`** |
| **O-06** | **`05-04` §1.7 collapses six external audiences into `R38`**, so a `TS-017` negative test keyed to `R38` cannot distinguish a seller from a vendor from a brand. This pack keeps them separate; **the role register does not**, and the permission engine follows the register. `TS-017` `O-*` records the counting consequence | Enterprise Architecture with `M29` owner | **W2 — before `TS-017` derivation** |
| **O-07** | **`EO-001` and the ecosystem onboarding kits are unwritten** (Category 18 unstarted). `UAT-R38-P07-001` and `UAT-R38-P05-001` are onboarding scripts, and onboarding without a kit tests the form rather than the journey | Commercial content owners | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **Method taken by reference from `TS-006` and `TS-007` rather than restated (`CP-01`)**
- [x] **The no-real-executor problem named, and four of the six added rules derived from it**
- [x] **The boundary with `TS-017` stated: systematic versus experiential, neither replacing the other**
- [x] 72 scripts enumerated across 7 audiences and 7 portals, with rules, criteria and priority
- [x] Seven audiences kept distinct although `05-04` §1.7 collapses six of them into `R38`, and the consequence recorded
- [x] Device and network made part of the script rather than an environment note
- [x] Scope-boundary refusal required by four real-user routes, as a numbered step in every block
- [x] Consent, withdrawal and rights requests treated as behaviour to verify, not features to confirm
- [x] Twelve external edge cases stated, including scope-widening API parameters and mid-payment network loss
- [x] Bilingual obligation stated for the three Bengali-first audiences
- [x] Scope leak classified as a breach with an Authority notification obligation, and made non-deferrable
- [x] **The reason the customer row is signed by an employee recorded, so cohort participation is not read as sign-off**
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 72 per-step grids — outstanding**
- [ ] **`O-02` first-time-user process absent — outstanding; the customer block's value depends on it**
- [ ] **`O-03` real counterparties not arranged — outstanding; blocking `G4-05`**
- [ ] **`O-05` four external agreements do not exist — outstanding; `UA-22` undischargeable**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CCO delegate**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
