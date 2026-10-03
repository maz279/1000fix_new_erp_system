---
id: TR-002
title: Role-Based Curriculum Map
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with HR and Programme Content Lead
reviewers: [HR Director, Quality Manager, Operations Director, Technical Director, HSE Lead, Security Lead, Legal Counsel, Programme Content Lead]
approver: HR Director with Operations Director
content_class: E
purpose: >
  Maps every registered role to the courses it must complete, in sequence, with prerequisites,
  duration and certification outcome. 38+ roles cannot each receive a bespoke plan invented at the
  time; the map is the plan. It is also the file that shows which roles have no course at all —
  and that gap, including a statutory one covering every employee, is the most important thing in
  this document.
traces_to: [M22, M55, M59, M29, P02, P03, P06, P09, P10, P11, 05-04, 06-01, MD-009, MD-010, MD-011, TR-001, TR-004, TR-022, TR-023, TR-024, SP-011, SP-012, SP-023, SP-025, SP-026, SP-027, SP-030]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §5 — the 38 registered roles R01…R38 with headcount, portal access and scope
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-LMS-01 overdue mandatory training restricts the affected work types; BRU-SRM-09 and BRU-HRM-01 block assignment of an uncertified technician to brand warranty work
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-018 curricula and role-based learning paths with sequencing; FR-LMS-019 automatic assignment by role, product line, brand, location and identified gap
    verified: 2026-08-17
    class: P1
  - source: project_content/_AUDIT/AUDIT-006_Category_06_SP_Content_Audit.md finding SP-02 — six SOPs describe work performed by roles with no course pack, including SP-030 health and safety which applies to every employee
    verified: 2026-08-17
    class: P1
  - source: Bangladesh Labour Act 2006 with Bangladesh Labour Rules 2015 — safety committees required in establishments with 50 or more workers, regular safety training with refresher expected at least annually or on change of procedure or equipment
    verified: 2026-08-17
    class: P1
    note: Legal confirmation outstanding — TR-001 O-02
supersedes: none
review_due: 2027-02-17
---

# TR-002 — Role-Based Curriculum Map

> **This file contains a finding, not just a map.** §7 records that six roles performing documented
> work have no course pack, that one of those gaps covers **every employee** and rests on a
> statutory duty, and that the `TR` register at 24 files cannot close it without a register change.
> The map is in §4–§6. The gap is in §7. **Read §7.**

---

## 1. Purpose

`M22` FR-LMS-019 assigns training automatically by role. That automation needs a table telling it
what each role owes. This is that table.

Without it, three things happen, and all three have already been observed in programmes of this
size:

| Failure | Consequence |
|---|---|
| Curriculum decided per person at the time | 800+ individual decisions, none recorded, none consistent, none defensible at audit |
| Courses assigned by job title text rather than registered role | Title drift silently breaks assignment; `MD-009` exists to prevent exactly this |
| No sequence or prerequisite | People trained on exception handling before they can complete the standard transaction |

**Consequence of absence (`CP-03`).** `M22` FR-LMS-019 cannot be configured; `M22` FR-LMS-005 gap
analysis has no requirement to compare against; `BRU-LMS-01` cannot restrict work because nothing
defines what is mandatory for whom; and `M22` FR-LMS-038 cannot produce a competence evidence file
for ISO 9001 or a brand audit, because there is no statement of what competence the role required.

---

## 2. Scope

**In scope:** the curriculum architecture (four layers); the universal core every employee takes;
the role-to-pack map for all 38 registered roles; prerequisites and sequencing; the wave-by-wave
training calendar; the coverage gap analysis; and the rules `CU-01`…`CU-14`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Learning model, delivery mix, competency levels, budget basis | [`TR-001_Training_Strategy_and_Competency_Framework.md`](TR-001_Training_Strategy_and_Competency_Framework.md) |
| Course design and storyboarding | [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](TR-003_Course_Design_Standard_and_Storyboard_Template.md) |
| Pass marks, attempts, re-certification, appeal | [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) |
| The course content itself | `TR-007`…`TR-021` |
| The role register | `05-04` · [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) — **`CU-01` prohibits inventing a role here** |
| Access provisioning that competence gates | `M29` · `05-04` |
| Onboarding as a process | [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) |
| External-party enablement — sellers, vendors, brands, corporate users | Category 18 `EO` — **`R36`, `R37`, `R38` are out of scope here by design (§5.4)** |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Learning & Development** | Configure `M22` learning paths; plan delivery per wave |
| **HR Director / HR Officers** | Assign curricula on joining; evidence competence at audit |
| **Line managers** | Know what their people owe and when |
| **Security Lead / `R33`** | Understand which competence gates which access |
| **Quality Manager** | Assure certification coverage against `BRU-SRM-09` and ISO 9001 clause 7.2 |
| **HSE Lead** | Verify the statutory floor is covered — **see §7** |
| **Programme Content Lead** | Resolve the register consequence in §7 |

---

## 4. Content — curriculum architecture

### 4.1 Four layers

Every person's curriculum is assembled from four layers. **`CU-02`: layers are completed in order.**

| Layer | Name | Applies to | Delivered | Refresh |
|:--:|---|---|---|---|
| **1** | **Universal core** | **Every employee, no exception** | Induction, before system access | **Annual** |
| **2** | **Role pack** | The person's registered role | Before production access to that role's functions | On release (`TR-024`) |
| **3** | **Specialisation** | Device family, brand, portal, module depth | After Layer 2, as the work requires | Per `MD-011` validity |
| **4** | **Sustainment** | Everyone, continuously | Job aids, champions, refreshers, release training | Continuous |

### 4.2 Layer 1 — the universal core

**`CU-03`: no employee receives production system access until Layer 1 is complete.**

| Module | Duration | Why it is universal | Governing content | Statutory |
|---|---|---|---|:--:|
| **Health, safety and incident reporting** | 90 min | Every employee can be injured or witness an injury; every employee must know how to report | `SP-030` · `M59` · `KB-013` | **✔ — see §7** |
| **Information security and acceptable use** | 45 min | Everyone holds credentials; `M29` and `05-04` gate everything on identity | `LG-020` · `LG-021` · `M29` | |
| **Data protection and customer confidentiality** | 45 min | Every operational role touches customer data; `05-04` T5 restricts data-services access | `LG-008` · `LG-009` · `SP-012` | |
| **Anti-bribery, ethics and speaking up** | 30 min | Procurement, cash handling and vendor contact reach across the network | `LG-023` | |
| **Quality system and your part in it** | 30 min | ISO 9001:2015 clause 7.2 requires competence to be determined and evidenced | `LG-022` · `M23` | **✔ ISO** |
| **System basics and navigation** | 60 min | Common to all portals; prevents every role pack re-teaching login, search and navigation | `UI-001` · `UI-002` · `UI-005` | |
| **Terminology — what we call things** | 30 min | `CG-004` defines one approved term per object; the workforce must share it | `CG-004` · `BN-003` | |

**Total: approximately 5.5 hours.**

> **Layer 1 has no course pack file in the `TR` register.** Seven modules, one of them a statutory
> duty covering 800+ people, specified here and owned by nobody. **This is the substance of §7.**

### 4.3 Layer 2 — role packs

Fifteen role packs exist: `TR-007`…`TR-021`. Their coverage of the 38 registered roles is mapped in
§5 and analysed in §7.

### 4.4 Layer 3 — specialisation

| Specialisation | Applies to | Gated by | Evidence |
|---|---|---|---|
| Device family competence, `L1` / `L2` / `L3_board` | `R10`–`R12` | `TR-005` assessment | `MD-010` |
| **Brand authorisation** | Technicians on warranty work | Brand requirement | `MD-011` — **lapse suspends assignment** (`M22` FR-LMS-013, `BRU-SRM-09`, `BRU-HRM-01`) |
| **Refrigerant handling** | Appliance technicians | Statutory regime — **unconfirmed**, `KB-013` `O-05` | `MD-011` |
| Portal depth — `P03` workspace, `P06` analytics | Admin and management roles | Role pack completion | `M22` |
| Module depth — finance, HR, quality, inventory | Functional roles | Role pack completion | `M22` |
| High-voltage / stored-energy work | Technicians on microwave, UPS, display | `KB-012`, `KB-013` | HSE record |

### 4.5 Layer 4 — sustainment

The Required Drivers from `TR-001` §4.3, expressed as curriculum:

| Mechanism | Owner | File |
|---|---|---|
| Job aids at the point of work | L&D | [`../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) |
| Champion and super-user network | L&D with Change | [`../08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md`](../08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) |
| Release and refresher training | L&D | [`../08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md`](../08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) |
| Offline field reference | Technical + Content Design | `KB-016` — **boundary with `TR-022` defined in §6.3** |

---

## 5. The role-to-curriculum map

**`CU-01`: every row names a role registered in `05-04`. No role is invented here.**

### 5.1 Executive and management

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R01` Chief Executive Officer | 1 | **None registered** — `P06` analytics orientation only | `P06` dashboards | W4 |
| `R02` Chief Technology Officer | 1 | **None registered** | `P06`, `P03` system console awareness | W1 |
| `R03` Chief Financial Officer | 1 | **None registered** | `P06`, finance approval flows | W1 |
| `R04` Chief Commercial Officer | 1 | **None registered** | `P06`, pricing and contract approval | W2 |
| `R05` Operations Director | 1–2 | **None registered** | `P06`, `P03` all workspaces | W1 |
| `R06` Branch Manager | **51+** | [`TR-011`](../08B_Course_Packs/TR-011_Course_Pack_Branch_Manager.md) | `P06` branch analytics, cash, stock, `P11` | W1 |
| `R07` Dispatch Manager | 3–8 | [`TR-008`](../08B_Course_Packs/TR-008_Course_Pack_Dispatch_Manager.md) | Zone and capacity depth | W1 |

### 5.2 Service delivery

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R08` Service Centre Agent | **150–250** | [`TR-007`](../08B_Course_Packs/TR-007_Course_Pack_Service_Centre_Agent.md) | Intake triage (`SP-033`) | W1 |
| `R09` Workshop Supervisor | 20–40 | [`TR-010`](../08B_Course_Packs/TR-010_Course_Pack_Workshop_Supervisor.md) | WIP, QC gate, escalation | W1 |
| `R10` Senior Technician | 80–150 | [`TR-009`](../08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) | Device family, brand, `L2` | W2 |
| `R11` Junior Technician | **120–250** | [`TR-009`](../08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) | Device family, `L1` | W2 |
| `R12` Specialist Technician (L3) | 15–30 | [`TR-009`](../08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) + L3 extension | `L3_board`, brand, `KB` authoring | W2 |
| **`R13` Remote Support Engineer** | **15–40** | **⚠ NONE — see §7** | MSP estates, `SP-011` | W4 |
| **`R14` Data Services Technician** | **5–12** | **⚠ NONE — see §7** | `SP-012`, `05-04` T5 | W2 |

### 5.3 Logistics, inventory and procurement

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R15` Logistics Coordinator | 10–25 | [`TR-020`](../08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) | Manifest, exception handling | W3 |
| `R16` Rider / Delivery Agent | **50–150** | [`TR-020`](../08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) | Custody, POD, cash | W3 |
| `R17` Inventory Manager | 5–10 | [`TR-012`](../08B_Course_Packs/TR-012_Course_Pack_Inventory_and_Store_Keeper.md) | Network stock, transfers | W1 |
| `R18` Branch Store Keeper | **51+** | [`TR-012`](../08B_Course_Packs/TR-012_Course_Pack_Inventory_and_Store_Keeper.md) | Van stock reconciliation | W1 |
| `R19` Procurement Officer | 4–8 | [`TR-013`](../08B_Course_Packs/TR-013_Course_Pack_Procurement_Officer.md) | Three-way match, `P05` | W3 |
| `R20` Warehouse Operative | 15–30 | [`TR-012`](../08B_Course_Packs/TR-012_Course_Pack_Inventory_and_Store_Keeper.md) — **warehouse module** | Receipt, put-away, count | W3 |

### 5.4 Commercial

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R21` Sales Manager | 3–6 | [`TR-018`](../08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md) | Pipeline, quoting | W2 |
| `R22` Account Manager (Corporate) | 8–20 | [`TR-018`](../08B_Course_Packs/TR-018_Course_Pack_Account_and_Contract_Manager.md) | `P04`, contracts, SLA | W2 |
| **`R23` Marketing Manager** | **2–4** | **⚠ NONE — see §7** | `M35` campaigns | W2 |
| `R24` Marketplace Operations Officer | 4–10 | [`TR-019`](../08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md) | `P07`, seller governance | W7 |
| **`R25` Retail / Refurbishment Officer** | **5–15** | **⚠ NONE — see §7** | `SP-025`, data erasure | W5 |

### 5.5 Finance

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R26` Finance Manager | 2–4 | [`TR-014`](../08B_Course_Packs/TR-014_Course_Pack_Finance_Officer_and_Manager.md) | Close, VAT, `P06` | W1 |
| `R27` Finance Officer | 10–20 | [`TR-014`](../08B_Course_Packs/TR-014_Course_Pack_Finance_Officer_and_Manager.md) | AR, AP, reconciliation | W1 |
| `R28` Warranty Claims Officer | 4–10 | [`TR-014`](../08B_Course_Packs/TR-014_Course_Pack_Finance_Officer_and_Manager.md) — **warranty module** | `P08`, claim evidence | W4 |
| `R29` Cashier / Counter Finance | **51+** | [`TR-014`](../08B_Course_Packs/TR-014_Course_Pack_Finance_Officer_and_Manager.md) — **counter cash module** | `SP-019` cash and banking | W1 |

### 5.6 People, quality and technology

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R30` HR Manager | 1–2 | [`TR-015`](../08B_Course_Packs/TR-015_Course_Pack_HR_and_Payroll.md) | Payroll approval, statutory filing | W5 |
| `R31` HR Officer | 3–6 | [`TR-015`](../08B_Course_Packs/TR-015_Course_Pack_HR_and_Payroll.md) | Attendance, leave, onboarding | W5 |
| `R32` Quality Manager / ISO Coordinator | 2–4 | [`TR-016`](../08B_Course_Packs/TR-016_Course_Pack_Quality_and_Field_Auditor.md) | CAPA, audit programme, `P11` | W5 |
| `R33` IT / System Administrator | 4–8 | [`TR-021`](../08B_Course_Packs/TR-021_Course_Pack_System_Administrator.md) | `P03` system console, `M29`, `M30` | W1 |

### 5.7 Contact centre

| Role | Headcount | Layer 2 pack | Layer 3 | Wave |
|---|---|---|---|:--:|
| `R34` Contact Centre Agent | **30–60** | [`TR-017`](../08B_Course_Packs/TR-017_Course_Pack_Contact_Centre_Agent.md) | Six channels, `SP-034` scripts | W4 |
| `R35` Contact Centre Supervisor | 4–10 | [`TR-017`](../08B_Course_Packs/TR-017_Course_Pack_Contact_Centre_Agent.md) + supervisor extension | Queue, quality monitoring | W4 |

### 5.8 External parties — deliberately out of scope

| Role | Headcount | Position |
|---|---|---|
| `R36` Customer | 250,000+/month | Self-service help, not training — `HC-003` |
| `R37` Corporate Portal User | 500–2,000 | **Category 18 `EO`** onboarding content |
| `R38` External Party — vendor, seller, brand, courier, referral, recycler, auditor | 1,000–3,000 | **Category 18 `EO`** onboarding content |

**`CU-04`: external parties are enabled by Category 18, not trained by Category 08.** They are not
employees, the company has no competence obligation for them under ISO 9001 clause 7.2, and
`BRU-LMS-02` handles the one exception — a marketplace engineer cannot be activated in a category
without passing that category's qualification, which `TR-019` prepares the *operations officer* to
administer.

---

## 6. Sequencing, prerequisites and the calendar

### 6.1 Prerequisite rules

| # | Rule | Class |
|---|---|:--:|
| **CU-01** | Every curriculum row names a role registered in `05-04` / `MD-009` | **H** |
| **CU-02** | Layers are completed in order; Layer 2 cannot start before Layer 1 | **H** |
| **CU-03** | No production system access before Layer 1 is complete | **H** |
| **CU-05** | No production access to a role's money-, stock- or customer-affecting functions before that role's Layer 2 assessment is passed (`LS-14`) | **H** |
| **CU-06** | Technician brand and refrigerant specialisation gates assignment, not merely access (`BRU-SRM-09`, `BRU-HRM-01`) | **H** |
| **CU-07** | A role change triggers curriculum reassignment within 5 working days | **C** |
| **CU-08** | A person holding two roles takes the union of both curricula, not the larger of the two | **H** |
| **CU-09** | Overdue mandatory training restricts the affected work types (`BRU-LMS-01`) | **H** |
| **CU-10** | Training commitments publish to `M55` so committed learners are unavailable (`LS-18`) | **C** |
| **CU-11** | A pack may not be substituted for another without a recorded gap analysis | **A** |
| **CU-12** | Curriculum completion is evidenced per learner and retrievable per role (`M22` FR-LMS-038) | **H** |
| **CU-13** | Where a role's pack does not exist, the gap is **recorded in §7 and reported**, never silently covered by a neighbouring pack | **H** |
| **CU-14** | Wave sequencing follows `06-01`; a role trained more than one wave before it uses the system is retrained, not counted (`TR-024`) | **C** |

### 6.2 Training calendar by wave

Derived from the register's own wave assignments, aggregated by delivery load.

| Wave | Packs delivered | Populations | Approximate learner hours |
|:--:|---|---|---:|
| **W0** | Layer 1 core begins for the programme team | ~50 | 275 |
| **W1** | `TR-007`, `TR-008`, `TR-010`, `TR-011`, `TR-012`, `TR-014`, `TR-021`, `TR-022`, `TR-023` | Agents 150–250 · branch managers 51+ · supervisors 20–40 · store keepers 51+ · finance 12–24 · cashiers 51+ · admins 4–8 | **~3,000–4,500** |
| **W2** | `TR-009`, `TR-018`, `TR-024`, plus `TR-004`, `TR-005`, `TR-006` framework | **Technicians 200–400** · account managers 11–26 | **~4,000–7,000** |
| **W3** | `TR-013`, `TR-020` | Riders and coordinators 60–175 · procurement 4–8 | ~700–1,400 |
| **W4** | `TR-017` | Contact centre 34–70 | ~400–800 |
| **W5** | `TR-015`, `TR-016` | HR ~8 · quality and auditors 20–60 | ~350–800 |
| **W7** | `TR-019` | Marketplace ops 4–10 | ~80–200 |

> **W1 and W2 together carry roughly 80% of the total learner load**, concentrated in the two waves
> that also carry the heaviest build and migration effort. This is the single most important
> planning fact in the file, and it is why `TR-023`'s champion network is a `W1` deliverable rather
> than a nice-to-have.

### 6.3 The `TR-022` / `KB-016` boundary

**`AUDIT-008` finding KB-09 recorded that `TR-022` and `KB-016` may be the same artefact produced
by two workstreams — a direct `CP-01` risk. The boundary is defined here.**

| | `TR-022` Job Aid Library | `KB-016` Field Reference Card Set |
|---|---|---|
| Answers | *"How do I do this in the system?"* | *"Is this safe, and what does this mean technically?"* |
| Content | System task steps — record a resolution, raise a transfer, take a payment | Safety, hazard, code, substitution and escalation decisions |
| Derived from | Course packs and `UI-*` copy | Approved `KNW-` articles (`RC-01`) |
| Audience | **All 38 roles** | Field technicians and riders |
| Medium | One page, printable, in-app | One screen, offline-first, in `P02` |
| Owner | L&D | Technical with Content Design |
| Test | Can a trained user complete the transaction? | Can an untrained-in-this-instance person avoid harm? |

**`CU-15`: where a technician needs both, they are separate artefacts with separate owners, and
each links to the other rather than duplicating it.** A technician recording a resolution uses a
`TR-022` job aid; the same technician deciding whether a battery is safe to handle uses a `KB-016`
card.

---

## 7. The coverage gap — `AUDIT-006` SP-02 resolved and escalated

**This section is the reason the file carries a finding warning at the top.**

### 7.1 What the map shows

| | Count |
|---|---:|
| Registered roles in `05-04` | 38 |
| External-party roles, out of scope by `CU-04` | 3 (`R36`, `R37`, `R38`) |
| **Internal roles requiring a curriculum** | **35** |
| Roles covered by an existing Layer 2 pack | **29** |
| **Roles with no Layer 2 pack** | **6** |
| **Employees covered by Layer 1, which has no pack file** | **All of them** |

### 7.2 The six roles with no pack

| Role | Headcount | Work described in | Why informal training is not acceptable |
|---|---|---|---|
| **`R13` Remote Support Engineer** | 15–40 | `SP-011` | **Privileged access to customer estates.** `KB-007` §6 makes a wrong action on a degraded array irreversible; `TG-43` prohibits shared credentials. Also raised as `KB-007` `O-03` |
| **`R14` Data Services Technician** | 5–12 | `SP-012` | The most sensitive data the company handles; `05-04` T5 restricts access to assigned cases only |
| **`R25` Retail / Refurbishment Officer** | 5–15 | `SP-025` | Data-erasure obligation (`BRU-ESG-01`) and consumer-disclosure obligation on resale |
| **`R23` Marketing Manager** | 2–4 | `M35` | Campaign, consent and customer-data handling under `LG-008` |
| **Sustainability function** | Unsized | `SP-026` | **Regulatory duty** under the Hazardous Waste (E-waste) Management Rules 2021; `BRU-ESG-02`/`-03` |
| **Rental Operations function** | Unsized | `SP-027` | Company assets in customer possession; recovery and damage assessment |

**Two of these are not registered roles at all.** *Sustainability* and *Rental Operations* appear as
owning functions in `SP-026` and `SP-027` but have no `Rnn` in `05-04`. That is the same defect
audit `00-07` **H2-07** recorded — roles used operationally but unregistered — and `MD-009` was
written to resolve it. **`CU-01` therefore prevents this file from assigning them a curriculum at
all**, which is the correct behaviour and a genuine blockage.

### 7.3 The Layer 1 gap — the one that matters most

**Layer 1 (§4.2) applies to every employee, includes a statutory safety duty, and has no course
pack file in the `TR` register.**

| Element | Position |
|---|---|
| Population | **800+ employees** |
| Content | Seven modules, ~5.5 hours, specified in §4.2 |
| Statutory basis | Bangladesh Labour Act 2006 with Labour Rules 2015 — regular safety training, annual refresher, safety committees at 50+ workers. ISO 9001:2015 clause 7.2 for the quality module |
| Business-rule dependency | `BRU-LMS-01` restricts work when mandatory training is overdue — **but nothing defines what "mandatory" contains** |
| KPI dependency | `KPI-064` targets 95% then 98% mandatory-training completion **against a curriculum with no safety course in it** |
| Register position | **`TR` is declared at 24 files. There is no file for this.** |

`AUDIT-006` SP-02 stated the instruction: *"either add the missing packs to the `TR` register —
which changes Category 08 from 24 files to approximately 30 and changes the 452 total — or record
in `TR-002` the explicit decision that these roles are trained through another named route."*

**This file takes the second option for the six roles and rejects it for Layer 1.**

### 7.4 The resolution

| Gap | Resolution | Authority needed |
|---|---|---|
| `R13` Remote Support Engineer | **Named route:** `TR-021` System Administrator pack + a declared MSP delta module covering `SP-011` consent, session control and `KB-007` §5.1. Recorded in `TR-021` §2 | Training Lead — **within this category** |
| `R14` Data Services Technician | **Named route:** `TR-016` Quality pack + a declared data-services delta covering `SP-012` custody and `05-04` T5 | Training Lead |
| `R25` Retail / Refurbishment Officer | **Named route:** `TR-012` Inventory pack + a declared refurbishment delta covering `SP-025` erasure and disclosure | Training Lead |
| `R23` Marketing Manager | **Named route:** `TR-018` Account and Contract pack + consent and campaign-data module | Training Lead |
| Sustainability function | **Blocked.** No registered role; `CU-01` prevents assignment. `MD-009` must register it first | **MDM with HR** |
| Rental Operations function | **Blocked.** As above | **MDM with HR** |
| **Layer 1 universal core** | **A register change is required.** A mandatory induction and statutory-compliance pack must be added to the `TR` register, taking Category 08 to **25 files** and the programme total to **453** | **Programme Content Lead with the Steering Committee** |

**`CU-16`: the four named routes are an interim control, not an equivalent.** Each declares, in the
receiving pack, that it is carrying a role it was not designed for, so that the compromise is
visible at audit rather than discovered.

### 7.5 Why Layer 1 cannot take a named route

Every other gap can be absorbed by a neighbouring pack because the audiences overlap. Layer 1
cannot, for three reasons:

1. **Its audience is everyone**, including roles with no pack at all and roles whose packs land in
   W5 and W7. There is no neighbouring pack that reaches an employee in W1.
2. **It is the prerequisite for every other layer** (`CU-02`, `CU-03`). A prerequisite that lives
   inside one of the things it precedes is a circular dependency.
3. **It carries a statutory duty.** `LS-10` states that statutory training is not subject to
   prioritisation. Delivering it as an appendix to a role pack that half the workforce never takes
   is not a defensible compliance position.

**Recommendation to the Steering Committee: register `TR-025 — Mandatory Induction and Statutory
Compliance Pack`, `P0`, `W1`, content class `C`, bilingual, owned by HR with HSE.** Until that
decision is taken, §4.2 is the specification and no file owns it.

---

## 8. Dependencies

| Depends on | Why |
|---|---|
| [`TR-001_Training_Strategy_and_Competency_Framework.md`](TR-001_Training_Strategy_and_Competency_Framework.md) | Layers, competency levels, statutory floor |
| `05-04` Role, Permission and Access Matrix | The 38 roles and headcounts in §5 |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) | `CU-01`; and the register that must resolve the two unregistered functions |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Layer 3 gating |
| `M22` FR-LMS-018/019/038 | Learning paths, automatic assignment, evidence file |
| `06-01` Implementation Roadmap | §6.2 calendar |
| `M55` | `CU-10` availability |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | The Layer 1 safety module's source |
| `LG-008`, `LG-020`, `LG-021`, `LG-022`, `LG-023` | Layer 1 module sources |

| Depended on by |
|---|
| Every `TR` course pack · `M22` learning-path configuration · `M29` access provisioning gates · `SP-023` onboarding · `TR-024` release training |

---

## 9. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary** — the map changes as roles and portals land |
| Trigger for out-of-cycle review | A new role registered in `MD-009` · a pack added or retired · `KPI-064` missed · an access-related incident traced to curriculum |
| Owner | Learning & Development |
| Change log | `RF-006` |
| Enforcement | `CU-01`…`CU-16`; `M22` FR-LMS-019 automatic assignment configured from this file |

---

## 10. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`TR-025` Mandatory Induction and Statutory Compliance Pack must be registered**, taking Category 08 to 25 files and the programme total to 453. §7.5 states the recommendation; the decision is the Steering Committee's under `CM-R1`. **Until it is taken, 800+ employees have a specified statutory curriculum with no owner** | Programme Content Lead with Steering Committee | **W1 — before any wave grants system access** |
| **O-02** | **Sustainability and Rental Operations are not registered roles.** `CU-01` blocks curriculum assignment for both. `MD-009` must register them — the same defect class as `00-07` H2-07 | MDM with HR Director | **W1** |
| **O-03** | The four named routes in §7.4 require the receiving packs (`TR-012`, `TR-016`, `TR-018`, `TR-021`) to declare the additional role and author the delta module. **Each adds scope to a pack already estimated** | Training Lead | W2–W5 per pack |
| **O-04** | **The `TR-017` register row states 30–80 contact-centre agents; `05-04` registers `R34` at 30–60.** A 33% discrepancy in a population that drives delivery cost. Raised as audit finding **TR-06** | Programme Content Lead with Contact Centre | W4 |
| **O-05** | **`TR-016` is titled "Quality and Field Auditor" for an audience of 20–60 auditors, but `05-04` registers only `R32` Quality Manager at 2–4.** The 20–60 `P11` field auditors are not a registered role — again `00-07` H2-07. Raised as audit finding **TR-07** | MDM with Quality Manager | W5 |
| **O-06** | §6.2 learner-hour estimates are derived from headcount × pack duration. **Pack durations are estimates until each pack is authored**, so the calendar is provisional and will move | L&D | Recompute after `08B` authoring |
| **O-07** | `CU-05` requires assessment before production access to money-, stock- and customer-affecting functions. **Whether `M29` can gate access on an `M22` competence signal is unconfirmed**; if it cannot, the rule is a manual control across 800+ users | CTO with Security Lead | **Before W1 go-live** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 and §10 added and justified by category convention and by the finding they carry
- [x] All 38 registered roles mapped, with headcounts extracted from `05-04` rather than recalled
- [x] Four-layer architecture defined with completion order enforced (`CU-02`, `CU-03`)
- [x] Universal core specified module by module, with statutory basis identified
- [x] External parties excluded explicitly and the reasoning given (`CU-04`)
- [x] **`AUDIT-006` SP-02 addressed in full: four named routes, two blocked on role registration, and the Layer 1 gap escalated as a register change**
- [x] **`AUDIT-008` KB-09 resolved — the `TR-022` / `KB-016` boundary defined in §6.3 (`CU-15`)**
- [x] Gaps recorded and reported rather than silently absorbed (`CU-13`, `CU-16`)
- [x] Wave calendar derived from the register, with the W1–W2 concentration stated
- [x] Two further role-register discrepancies found and raised (`O-04`, `O-05`)
- [x] All internal links resolve
- [x] `BRU-LMS-*`, `BRU-SRM-*`, `BRU-HRM-*`, `BRU-ESG-*` cited to `05-05`; `FR-LMS-*` to `M22`; `KPI-064` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `TR-025` registered — outstanding; a statutory curriculum has no owner until it is**
- [ ] **`O-02` Sustainability and Rental Operations registered as roles — outstanding**
- [ ] **`O-07` access gating on competence confirmed — outstanding**
- [ ] Named approvers recorded — **pending HR Director and Operations Director**
- [x] English-only, per `CG-010` §3.2 — framework content

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
