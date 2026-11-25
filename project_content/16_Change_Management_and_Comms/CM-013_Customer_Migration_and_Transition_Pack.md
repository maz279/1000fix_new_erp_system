---
id: CM-013
title: Customer Migration and Transition Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketing with Change
author: Change Lead with Marketing and Content Design
reviewers: [CCO, Marketing Manager, Customer Service Manager, Contact Centre Supervisor, Data Migration Lead, Legal & Compliance, Localisation Lead, Content Design Lead, Support Lead, Programme Content Lead]
approver: Content Design Lead, with Legal approving the lawful basis and the privacy statements
content_class: D
purpose: >
  Carries 250,000-plus monthly customers from a service they experience through a phone call to
  one they experience through a portal — without any of them concluding that their history, their
  reference number or their entitlement has been lost. Existing customers with legacy reference
  numbers must be transitioned without losing their service history in their own eyes; a customer
  who cannot find their own past job in the new system does not conclude that the search is
  different, they conclude the company lost it.
traces_to: [P01, DM-004, DM-006, DM-013, DM-014, CM-001, CM-003, CM-006, CM-016, NT-004, NT-009, NT-015, HC-003, HC-015, LG-002, LG-008, LG-013, MD-021, 04-00, 06-01]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: CM-013_Customer_Migration_and_Transition_Pack_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 — customer portal capability set, design requirements (Bengali-first, 3G, under 400 KB booking path, WCAG 2.1 AA) and KPIs
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 KPIs — online booking rate baseline 40% and target 88%; self-service status checks target above 80% of status enquiries
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.10 — customer-facing cutover messages at T−7 days and go + 1 day, including the new reference format and legacy reference searchability
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.2 item 13 — customer communication today is verbal on request; customers call the hotline 3+ times per job
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.4a RSK-032, RSK-033 and §3.1a DEP-34 — Personal Data Protection Act 2026 obligations, split residency, and the absent transparency notice text
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 Wave 2 — customer portal delivered at W2 across all Dhaka centres; native applications at W6
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-013 — Customer Migration and Transition Pack

> **Scope note.** This file owns **what customers are told about the transition, and when**. It
> does not own transactional messaging (`NT-004`, `NT-009`, `NT-015`), help content (`HC-003`,
> `HC-015`), terms and privacy (`LG-002`, `LG-008`, `LG-013`), the migration itself (`DM-004`,
> `DM-006`) or adoption campaigns after the transition (`CM-016`).
>
> **Boundary note.** A transition message tells a customer that something has changed. A campaign
> asks them to do something new. §4.2 keeps them apart, because merging them turns a service
> notice into marketing and changes its lawful basis (`MG-04`).

---

## 1. Purpose

The register's justification is exact: *"Existing customers with legacy reference numbers must be
transitioned without losing their service history in their own eyes."*

The last clause is the whole file. The migration may be technically perfect — `DM-013`
reconciliation signed, every record accounted for — and still fail, because the customer's test is
not reconciliation. Their test is: *"I gave you a slip with a number on it. Can you find it?"*

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| Legacy reference not searchable, or not said to be | Every customer holding a slip calls the hotline to check |
| No transition notice | 250,000+ customers meet the change at their next interaction, at the counter or on the phone |
| Notice sent as marketing | A service change is delivered under a consent basis that may not cover it (`RSK-032`) |
| History visible but incomplete | The customer sees three of their eight past jobs and concludes the rest were lost |
| No contact-centre alignment | Agents contradict the notice within a day |
| Portal promoted before it is stable | The first impression is the one that sticks, and `P01`'s 88% booking target is set against it |
| No Bengali | The default language of the customer base is not the language of the transition |
| Notice sent to customers mid-complaint | A service failure is answered with a product announcement |

---

## 2. Scope

**In scope:** the transition promise; the reference-continuity position; the six transition
assets; the audience tranches and their sequencing; the lawful-basis boundary between service and
marketing; the contact-centre alignment; the history-visibility statement; the suppression rules;
the measurement of transition success; and rules `MG-01`…`MG-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Transactional notifications | `NT-004` customer, `NT-009`, `NT-015`; the `NT-001` matrix |
| Help articles and FAQ | `HC-003` customer help set; `HC-015` FAQ bank |
| Terms, privacy notice, consent text | `LG-002`, `LG-008`, `LG-013` |
| Customer and party data mapping | [`../12_Data_Migration_Content/DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](../12_Data_Migration_Content/DM-004_Field_Mapping_Workbook_Party_and_Customer.md) |
| Service history mapping | [`../12_Data_Migration_Content/DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md`](../12_Data_Migration_Content/DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md) |
| Adoption campaigns and their targets | [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) |
| The go-live customer notice | [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) G3 — **this file supplies the transition content G3 delivers** |
| Corporate client transition | [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md) |
| Loyalty points and voucher migration mechanics | `M10`; `DM-004` |
| Portal UI copy | `UI-011`; Bengali in `BN-009` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Marketing Manager (`R23`)** | Issue the transition sequence within the permitted claim and consent set |
| **Customer Service Manager** | Align the counter and the hotline to one position |
| **Contact Centre (`R34`, `R35`)** | Answer *"where is my old job?"* consistently |
| **Branch counter staff (`R08`)** | Answer the same question at the counter |
| **Data Migration Lead** | Know what has been promised to customers about their history |
| **Legal** | Confirm the basis on which 250,000+ people are contacted |
| **Change Lead** | Hold the boundary between transition and campaign |

---

## 4. Content

### 4.1 The transition promise

**`MG-01`: the pack makes exactly three promises, and every asset is checked against them.**

| # | Promise | What makes it true |
|:--:|---|---|
| **P1** | **"Your old reference still works."** | Legacy reference indexed and retrievable at the counter and in `P01` — `DM-006` `SH-12`, implementing `FR-SRM-088` |
| **P2** | **"Your service history is there."** | `DM-006` migrated history, with the **stated scope** — see §4.4 |
| **P3** | **"You do not have to do anything."** | No customer action is required to continue receiving service |

> **`MG-02` — P3 is what distinguishes a transition from a campaign.** The transition says
> *nothing is required of you*. The campaign, later, asks for something. A transition message with
> a call to action is a campaign wearing a service notice's clothes.

### 4.2 Transition and campaign are separate

| | **Transition (this file)** | **Campaign (`CM-016`)** |
|---|---|---|
| Says | Something has changed in how we serve you | Here is something you can now do |
| Asks | Nothing | Register, book online, download the app |
| Basis | **Service communication** — necessary to continue providing the service | **Marketing** — requires the consent state in `MD-021` and the basis in `LG-008` |
| Timing | At and around the change | **From two weeks after**, once the portal is stable |
| Reaches | Every customer in scope | Only customers whose consent state permits |
| Measured on | Enquiry volume, complaint volume, reference-lookup failures | Registration, booking share, MAU |

> **`MG-03` — the two are never combined in one message.** Combining them is efficient and it is
> the single most likely compliance error in this category. `RSK-032` puts penalties for rights
> violations at BDT 25 lakh, and BDT 50 lakh for a significant data fiduciary.

**`MG-04`: the classification of every asset is recorded in the asset itself and approved by
Legal before issue.**

### 4.3 The six transition assets

| # | Asset | Audience | When | Channel | Language |
|:--:|---|---|---|---|---|
| **C1** | **Advance notice — "something is changing"** | Customers with an **open job** at the affected sites | **T−7 days** | SMS + in-app | **BN-first** |
| **C2** | **Transition notice — "here is what changed"** | All customers in scope, **tranched** | **Go + 1 day** onward | In-app, portal banner, SMS | **BN-first** |
| **C3** | **Reference-continuity card** | Counter and hotline, to give to customers | From go | Printed card + agent script | **BN-first** |
| **C4** | **"Where is my history?" explainer** | Customers who ask; published in help | From go | `HC-003` article + agent answer | **BN-first** |
| **C5** | **Counter and hotline answer set** | `R08`, `R34`, `R35` | **T−2 days** | Console knowledge base + printed | **BN + EN** |
| **C6** | **Loyalty and entitlement continuity notice** | Customers with points, vouchers, contracts or warranties | Go + 3 days | SMS + in-app | **BN-first** |

> **`MG-05` — C1 goes only to customers with an open job.** A general advance notice to 250,000+
> people about a change they will not notice generates enquiry volume for no benefit. Customers
> with an open job will notice, and they are the ones who deserve warning.

> **`MG-06` — C6 is separate and later.** Loyalty points and contract entitlements are the two
> things customers check when they suspect data has been lost. A notice sent three days after go,
> once balances have been verified against `DM-013`, is credible; one sent on day one is a promise
> made before the evidence exists.

### 4.4 The history-visibility statement — the honest version

**`MG-07`: what is visible to the customer is stated exactly, and the boundary is published.**

| Element | Position |
|---|---|
| **Reference** | Legacy reference searchable; new format shown alongside |
| **Jobs** | The migrated scope from `DM-006` — **stated as a period, not as "all"** |
| Devices | Registered devices carried across (`DM-005`) |
| Invoices | Per the `DM-008` scope |
| Warranty and contracts | Active entitlements carried; expired history per `DM-010` scope |
| Loyalty | Balance carried; **transaction history per the migrated scope** |
| **What is not visible** | **Published.** Whatever falls outside the migrated period is stated, with how to obtain it |

> **`MG-08` — "we have everything" is prohibited unless the migration scope is genuinely
> unbounded.** `DM-001` scopes migration by entity and period; `DM-006` defines what service
> history moves. If three years move and a customer's 2019 repair does not, the message says so
> and says how to request it. A customer told *"everything is there"* who finds a gap concludes
> the company is either careless or lying, and both are worse than a stated boundary.

**`MG-09`: where history is not visible, a route exists to obtain it.** A statement of scope with
no retrieval route is an admission, not a service.

### 4.5 Tranching and suppression

| Element | Rule |
|---|---|
| **Tranche size** | Set by **contact-centre capacity**, not by sending capability (`CM-006` `O-01`) |
| Order | Customers with an open job → recently active → dormant. **Largest tranche last** |
| Interval | Minimum 24 hours between tranches, with enquiry volume reviewed between |
| **Suppression** | Customers with an **open complaint**, an **open dispute**, an **active service failure**, or a **bereavement or vulnerability flag** are suppressed |
| Channel preference | Respected from `MD-021`; a customer who has opted out of SMS receives the notice in-app and at the counter |
| **Frequency cap** | No customer receives more than **two** transition messages in seven days, excluding transactional notifications |
| Language | Determined by the customer's recorded preference; **Bengali where unknown** (`PS-03`) |

### 4.6 Contact centre and counter alignment

**`MG-10`: the counter and the hotline receive C5 two days before any customer receives C2.**

The three questions that will arrive, with the position:

| Question | Position |
|---|---|
| *"Where is my old job?"* | Search by the legacy reference. It is there. If it is outside the migrated period, explain the scope and offer the retrieval route (`MG-09`) |
| *"Do I have to register?"* | **No.** You can carry on exactly as you do now. The portal is available if you want it |
| *"Have I lost my points / my contract?"* | Balances and active entitlements are carried across. If a balance looks wrong, raise it and it is checked against the reconciliation, not argued about |

**`MG-11`: an agent never tells a customer that a discrepancy is the customer's error.** Migration
discrepancies are investigated against `DM-013`; the customer is told when they will hear.

### 4.7 Measurement

**`MG-12`: the transition is measured on absence of harm, not on adoption.** Adoption is
`CM-016`'s measure and applying it here creates pressure to turn the notice into a campaign.

| Measure | Definition | Target direction |
|---|---|---|
| **Reference-lookup failures** | Counter and hotline lookups by legacy reference that return nothing | **Zero; every instance investigated** |
| Transition enquiry volume | Contacts citing the change, per tranche | Within the forecast that sized the tranche |
| **History complaints** | Customers stating that history is missing | Counted; each reconciled against `DM-013` |
| Complaint volume | Total, versus the pre-transition baseline | **No increase** |
| Entitlement disputes | Loyalty, contract or warranty balance disputes | Counted; each reconciled |
| Opt-outs | Customers opting out of contact after a transition message | **A rise means the notice read as marketing** |

### 4.8 Native applications at W6

`06-01` §3 delivers customer native applications at **W6**, four waves after the portal. `MG-13`:
**the W2 transition does not promise an app.** A customer told at W2 that an app is coming will
ask for it at W3, W4 and W5. The app is announced by `CM-016` when it exists.

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| Customers with an open job | SMS + in-app, **BN-first** | **T−7 days** | C1: something changes; your job is unaffected; the hotline still answers | **None** |
| `R08`, `R34`, `R35` | Console KB + printed | **T−2 days** | C5 answer set | Learn the three positions |
| All customers in scope | In-app → portal banner → SMS, **tranched** | **Go + 1 day** onward | C2: what changed; your reference works; nothing required | **None** (`MG-02`) |
| Customers at the counter | Printed card | From go | C3 reference continuity | Keep it |
| Customers who ask | `HC-003` article + agent | From go | C4: what history is visible, and how to get the rest | Ask if you need an older record |
| Customers with points, contracts or warranties | SMS + in-app | **Go + 3 days** | C6: balances and entitlements carried | Check; raise anything that looks wrong |
| Contact centre | Volume report | Daily, first 2 weeks | Enquiry themes | Feed C4 and `HC-015` |
| — | — | **Go + 2 weeks** | **Campaign begins** — `CM-016` | Register, book online |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `MG-01` | The pack makes three promises and every asset is checked against them | **H** |
| `MG-02` | A transition message carries no call to action | **H** |
| `MG-03` | Transition and campaign are never combined in one message | **H** |
| `MG-04` | Every asset records its classification and is approved by Legal before issue | **H** |
| `MG-05` | The advance notice goes only to customers with an open job | **H** |
| `MG-06` | The loyalty and entitlement notice follows balance verification, not go-live | **H** |
| `MG-07` | The visible history scope is stated exactly, including what is not visible | **H** |
| `MG-08` | "We have everything" is prohibited unless migration scope is genuinely unbounded | **H** |
| `MG-09` | Where history is not visible, a retrieval route is published with it | **H** |
| `MG-10` | Counter and hotline are briefed two days before any customer message | **H** |
| `MG-11` | A discrepancy is never attributed to the customer; it is reconciled against `DM-013` | **H** |
| `MG-12` | The transition is measured on absence of harm, not on adoption | **H** |
| `MG-13` | The W2 transition does not promise the W6 native applications | **H** |
| `MG-14` | Tranche size is set by contact-centre capacity, not by sending capability | **H** |
| `MG-15` | Complaint, dispute, service-failure and vulnerability suppression is applied to every tranche | **H** |
| `MG-16` | No more than two transition messages per customer in seven days | **H** |
| `MG-17` | Bengali-first on every customer-facing asset; Bengali where preference is unknown (`PS-03`) | **H** |
| `MG-18` | A rise in opt-outs after a transition message is investigated as a classification failure | **S** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../12_Data_Migration_Content/DM-004_Field_Mapping_Workbook_Party_and_Customer.md`](../12_Data_Migration_Content/DM-004_Field_Mapping_Workbook_Party_and_Customer.md) | Legacy reference retention — promise P1 |
| [`../12_Data_Migration_Content/DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md`](../12_Data_Migration_Content/DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md) | The migrated history scope — promise P2 and §4.4 |
| [`../12_Data_Migration_Content/DM-013_Reconciliation_and_Validation_Report_Specification.md`](../12_Data_Migration_Content/DM-013_Reconciliation_and_Validation_Report_Specification.md) | What a discrepancy is reconciled against (`MG-11`) |
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) §4.10 | The customer-facing cutover messages this pack supplies content for |
| [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) | G3 is the delivery vehicle for C2 |
| [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) | Where the call to action lives |
| `LG-008`, `LG-002`, `LG-013` | Lawful basis, terms and consumer terms |
| `MD-021` | Segments, channel preference and consent state for tranching |
| `NT-004`, `NT-009`, `NT-015` | Transactional messages this pack must not duplicate |
| `HC-003`, `HC-015` | Where C4 lives permanently |
| `04-00` §P01 | What the portal actually offers at W2 |

| Depended on by |
|---|
| `CM-006` G3 and G4 · counter and hotline scripts at 51+ sites · `CM-016` campaign baseline · `P01` adoption reporting · `DM-014` §4.10 customer messages |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Before each wave that adds customer-facing sites**, and after each transition tranche |
| Trigger for out-of-cycle review | A change to migration scope · a reference-lookup failure · a PDPA position change · a rise in opt-outs |
| Owner | Marketing with the Change Lead; §4.4 co-owned with the Data Migration Lead; classification owned by Legal |
| Change log | `RF-006`; a change to the three promises is MAJOR |
| Enforcement | `MG-01`…`MG-18`; Legal classification gate before every issue |
| Improvement loop | **Every reference-lookup failure is investigated individually, not counted.** One failure is a data question; a pattern is a migration question; either way the answer changes what §4.4 is allowed to say |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The lawful basis for contacting 250,000+ customers is unconfirmed.** `MG-04` requires a classification per asset under the Personal Data Protection Act 2026. `DEP-34` records that PDPA-compliant transparency notice text has not been drafted in either language, `RSK-032` rates non-compliance Critical, and enforcement activates around 13 May 2027 — one wave after this pack is used. **This is the largest single exposure in Category 16** | Legal with Marketing and the CCO | **W2 minus 3 months** |
| **`O-02`** | **The migrated history scope is not yet fixed, and its owning decision is named.** `MG-07` and `MG-08` require an exact statement of what a customer will see. [`DM-006`](../12_Data_Migration_Content/DM-006_Field_Mapping_Workbook_Service_History_and_Jobs.md) `O-01` records `M01` `Q-04` as unresolved — **3, 5 or all years of service history** — so the `recent_closed` / `archive` boundary cannot be set and `SH-03` blocks the live load. `DM-011` additionally records all 48 legacy sources as unprofiled. **The pack cannot make promise P2 until `Q-04` is answered** | Operations Director with the CTO and the CCO | **W2 planning** |
| **`O-03`** | **Promise P1 has a specified mechanism and no verification.** `DM-006` `SH-12` is a Class `H` rule implementing `FR-SRM-088` — the legacy number indexed and searchable at the counter and in `P01`, with `ERR-SVH-012` as its error. `DM-006` itself says the register's promise *"is kept by `SH-12` and by nothing else"*. What is missing is **evidence that the counter search and the hotline console actually accept a legacy reference**, which is a `TS` test case that does not exist | Data Migration Lead with QA Lead | **W2 minus 2 months** |
| **`O-04`** | **The Bengali counterpart does not exist**, and every customer-facing asset is Bengali-first for a customer base whose default language is Bengali (`PS-03`). `CM-R6` blocks approval | Localisation Lead | **W2 minus 6 weeks** |
| **`O-05`** | **No tranching, suppression or frequency-capping capability is confirmed.** §4.5 requires segment selection, four suppression rules, channel-preference respect and a seven-day frequency cap at 250,000+ scale. `M27` omnichannel is W4; this pack is W2, and `CM-006` `O-06` records the same gap | CTO with Marketing | **W2 minus 2 months** |
| **`O-06`** | **The vulnerability and bereavement suppression flag does not exist in the data model.** §4.5 requires it; `MD-021` segments are commercial. Sending a service-change notice to a bereaved customer's number is the kind of error that reaches the press | CCO with the Data Migration Lead | **W2 minus 2 months** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Three transition promises fixed**, with what makes each true named
- [x] **Transition separated from campaign** on content, basis, timing, reach and measurement
- [x] Six assets specified with audience, timing, channel and language
- [x] Advance notice restricted to customers with an open job; entitlement notice deferred until balances are verified
- [x] **History visibility required to be stated exactly, with "we have everything" prohibited and a retrieval route mandatory**
- [x] Tranching bound to contact-centre capacity, with four suppression categories and a frequency cap
- [x] Counter and hotline briefed two days ahead, with the three arriving questions answered
- [x] **Measured on absence of harm rather than adoption**, with reference-lookup failure at zero tolerance
- [x] W6 native applications explicitly not promised at W2
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` lawful basis unconfirmed for 250,000+ recipients under the PDPA 2026**
- [ ] **`O-02` history window (3/5/all years) unresolved as `M01` `Q-04`; promise P2 cannot be made**
- [ ] **`O-03` `SH-12` specified but unverified; no test case exercises the counter or hotline lookup**
- [ ] **`O-04` Bengali counterpart not written**
- [ ] **`O-05` no tranching, suppression or frequency-capping capability**
- [ ] Named approver recorded — **pending Content Design Lead with Legal**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
