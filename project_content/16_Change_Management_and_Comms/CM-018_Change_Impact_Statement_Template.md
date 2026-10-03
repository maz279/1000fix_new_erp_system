---
id: CM-018
title: Change Impact Statement Template
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with HR and Business Process
reviewers: [HR Director, Operations Director, L&D Lead, Business Process Lead, Security Lead, Localisation Lead, Content Design Lead, Programme Content Lead, Quality Manager]
approver: Content Design Lead, with the HR Director approving the role coverage
content_class: D
purpose: >
  Fixes one structure for the per-role change impact statement — what changes, what stops, what
  starts, what support exists, and what is explicitly unaffected — and the rules for producing one
  for each of the 38 registered roles at the wave that touches it. Thirty-eight roles each need to
  see their own change rather than the programme's; a role that has never been shown its own
  before-and-after is a role that discovers the change at go-live, which is the definition of an
  adoption failure.
traces_to: [05-04, TR-002, MD-009, CM-001, CM-002, CM-005, CM-010, CM-011, CM-012, SP-001, SP-002, 06-01, 06-02, M22, M29]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 — the 38 registered roles R01…R38 with headcounts, portals, MFA requirement and data scope
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §2 — the portal access matrix, role by role, across P01…P12
    verified: 2026-08-20
    class: P1
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-002 §2 — the role-to-pack map for all 38 registered roles, and the prohibition on inventing a role outside 05-04 and MD-009
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §4.1 — 38 registered roles, 46 in use; 6 isolation tiers; 30 SoD controls
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.2 — the fifteen current-state processes each statement's "what stops" column is drawn from
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-018 — Change Impact Statement Template

> **Scope note.** This file owns **the structure of a change impact statement and the rules for
> producing 38 of them**. It does not own the role register (`05-04`, `MD-009`), the curriculum
> (`TR-002`), the process definitions (`SP-*`), or the delivery of a statement to a person
> (`CM-005` K2, `CM-010` slide 3).
>
> **Language note.** This file is `bilingual: no` because it is a **template**, the same treatment
> `CG-009` §3 gives `NT-001`, `DT-001` and `HC-002`. **Every statement produced from it for a
> Bengali-first role is bilingual.** `CI-14` makes that binding; §4.6 lists the roles it applies
> to.

---

## 1. Purpose

The register's justification is exact: *"38+ roles each need to see their own change, not the
programme's."*

A programme communicates in capabilities: dispatch, inventory, billing. A person experiences a
change as a list of things that are different on Monday. The gap between those two is where
adoption is lost, and it is not closed by more communication — it is closed by one document, per
role, that says *this is your Monday*.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No per-role analysis | Every audience receives the programme's view of the change and translates it themselves, badly |
| No "what stops" column | The old artefact survives alongside the new one, and the wave gate fails on legacy withdrawal |
| No structure | Thirty-eight statements by different authors are not comparable, so gaps are invisible |
| Impact stated without support | The statement becomes a list of demands |
| No "unaffected" section | Everything unstated is assumed to be at risk (`NR-05`) |
| Roles missed | A role that never receives a statement discovers its change at go-live |
| Statement written after training is designed | Training teaches a change nobody has described |
| Segregation-of-duties changes not surfaced | A person loses an authority they exercise daily and finds out when a transaction is refused |

---

## 2. Scope

**In scope:** the nine-section statement structure; the production rules and their sequence; the
role coverage requirement across all 38 registered roles; wave assignment; the authority-and-access
section; the effort model; the review and sign-off route; the reuse rule into `CM-005` K2 and
`CM-010`; and rules `CI-01`…`CI-16`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The role register, headcounts and portal access | `05-04` §1, §2 · `MD-009` — **`CI-02` prohibits inventing a role here** |
| Curriculum, prerequisites and assessment | `TR-002`, `TR-004` |
| Process definitions and SOPs | `SP-001`…`SP-006` architecture; `SP-007`+ procedures |
| The narrative framing | [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) |
| Delivery of a statement to a person | [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) K2; [`CM-010_Town_Hall_and_Roadshow_Content.md`](CM-010_Town_Hall_and_Roadshow_Content.md) slide 3 |
| Objections a statement provokes | [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) |
| Access provisioning and SoD enforcement | `M29`; `05-04` §3 |
| Job descriptions and grading | HR — **a change impact statement is not a job description and does not amend one** |
| External-party impact | Category 18 `EO`; [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md), [`CM-015_Vendor_and_Seller_Transition_Pack.md`](CM-015_Vendor_and_Seller_Transition_Pack.md) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Produce 38 statements to one structure |
| **Business Process Lead** | Supply the before/after from the process analysis |
| **HR Director** | Assure that nothing in a statement amends a job description or a grading |
| **L&D** | Design a course from a described change rather than from a specification |
| **Line managers** | Hold a conversation with their own team about their own work |
| **Security Lead** | Verify that authority and access changes are surfaced, not discovered |
| **Content Design** | Review 38 statements against one structure |

---

## 4. Content

### 4.1 The nine sections

**`CI-01`: nine sections, fixed order, two pages.** A statement longer than two pages is a
process specification and belongs in `SP-*`.

| # | Section | Rule | Length |
|:--:|---|---|---|
| **1** | **Who this is for** | The `05-04` role ID and name, headcount, sites, and the wave | 2 lines |
| **2** | **What your job is** | **One sentence, in the role's own terms.** If the author cannot write it, the analysis is not done | 1 line |
| **3** | **What stops** | The named artefact or practice that ends — the pad, the spreadsheet, the whiteboard, the phone call | 3–6 lines |
| **4** | **What starts** | The named new action, with where it happens | 3–6 lines |
| **5** | **What stays exactly as it is** | **Mandatory** (`NR-05`). At least three lines | 3+ lines |
| **6** | **Your authority and access** | What you may do, what needs approval, what you can see — and **what changes** | Table |
| **7** | **What you need to do before your wave** | Training, device, login, data check — with dates | Checklist |
| **8** | **Where to get help** | `CM-005` K4 routes, named champion | 3 lines |
| **9** | **What we do not yet know** | **Mandatory.** Open items affecting this role, with owner and date | 1+ lines |

> **`CI-03` — section 9 is not an admission of weakness.** A statement that presents a change as
> fully resolved when four decisions are open is disproved within a month. Naming the open items,
> with owners, is what makes the other eight sections believable.

### 4.2 Section 3 and 4 — the discipline

**`CI-04`: "what stops" is named to an artefact, never to a behaviour.** *"Manual processes stop"*
is not a statement; *"the pre-numbered paper intake pad stops, and the last pad is collected on
[date]"* is.

| Good | Not acceptable |
|---|---|
| *"The branch stock spreadsheet stops. It is archived on [date] and is read-only afterwards."* | *"Manual stock tracking will be phased out."* |
| *"You stop phoning the technician to assign a job. Assignment happens on the dispatch board."* | *"Dispatch becomes digital."* |
| *"The paper service form stops. Nothing is keyed at the branch two days later."* | *"Paperwork is reduced."* |
| *"You stop preparing the warranty claim by hand. The claim is created from the closed job."* | *"Warranty is automated."* |

**`CI-05`: every "what stops" line has a date and an owner for its withdrawal.** An artefact
without a withdrawal date survives, and `DM-014` `CV-03` fails the wave gate for the whole wave.

### 4.3 Section 6 — authority and access

The section most often omitted and most often the cause of a first-week escalation.

| Column | Content |
|---|---|
| What you can do | The transactions this role may initiate |
| What needs approval | The approval limit, and **who** approves — from `05-05` and `MD-015` |
| What you can see | The data scope from `05-04` §1 |
| Which portals | From `05-04` §2 |
| **What changes** | **Explicitly.** An authority gained, an authority lost, an approval newly required |
| MFA | Whether this role now requires it (`05-04` §1) |

> **`CI-06` — an authority a person exercises today and will not exercise tomorrow is stated in
> section 6 and is never left to be discovered.** With 30 segregation-of-duties controls and six
> isolation tiers, some roles will lose informal authority they have held for years. Discovering
> that at a counter, with a customer waiting, converts a control improvement into a grievance.

### 4.4 Producing 38 statements

**`CI-07`: a statement is produced for every registered role, at the wave that first touches it.**

| Step | Activity | Owner | Input |
|:--:|---|---|---|
| 1 | Confirm the role from `05-04` §1 and `MD-009` | Change Lead | `CI-02` |
| 2 | Establish the current state — **observed, not assumed** | Business Process Lead | BRD §6.2; site observation |
| 3 | Establish the future state | Business Process with the module business owner | `SP-*`, `05-01` |
| 4 | Draft sections 1–5 | Change Lead | `CM-001` vocabulary |
| 5 | **Section 6 drafted with the Security Lead** | Change Lead + Security | `05-04`, `05-05` |
| 6 | Section 7 from `TR-002` and `CM-012` | L&D | Course dates |
| 7 | **Reviewed by two people who hold the role** | Change Lead | — |
| 8 | HR check — nothing amends a job description | HR Director | — |
| 9 | G1 editorial; G2 factual with the module business owner | Content Design; Domain owner | `CG-007` |
| 10 | Bengali where the role is Bengali-first (§4.6) | Localisation | `BN-018` |
| 11 | Issue via `CM-005` K2 | Change Lead | `CM-003` M2 |

> **`CI-08` — step 7 is not optional and is not a review by a manager of the role.** Two people
> who do the job read the statement and say whether it describes their work. A statement that
> survives that test is worth issuing; one that has not been tested is the programme's view of
> someone else's job.

### 4.5 Role coverage and wave assignment

**`CI-09`: coverage is counted against `05-04`'s 38 registered roles, and the count is reported.**

| Wave | Roles first touched | Count |
|:--:|---|---:|
| **W1** | `R01`–`R05` executive · `R06` branch manager · `R08` agent · `R09` workshop supervisor · `R33` IT admin · `R07` dispatch manager | **11** |
| **W2** | `R10`–`R12` technicians · `R17` inventory manager · `R18` storekeeper · `R20` warehouse operative · `R36` customer | **7** |
| **W3** | `R15` logistics coordinator · `R16` rider · `R19` procurement officer · `R26`–`R27` finance · `R29` cashier · `R38` external party (vendor, courier) | **7** |
| **W4** | `R13` remote support · `R21`–`R23` commercial · `R28` warranty officer · `R34`–`R35` contact centre · `R37` corporate user · `R38` (brand partner) | **8** |
| **W5** | `R30`–`R31` HR · `R32` quality manager | **3** |
| **W6** | `R14` data services technician · `R25` retail/refurbishment officer | **2** |
| **W7** | `R24` marketplace operations · `R38` (seller, referral partner) | **1** |
| | **Total registered roles covered** | **39 role-wave entries across 38 roles** |

> **`CI-10` — `R38` receives four statements, not one.** *External Party* is a single registered
> role covering vendors, marketplace sellers, brand partners, couriers, referral partners,
> recycling partners and external auditors, entering at four different waves with entirely
> different changes. One statement for seven counterparty types would be useless to all of them.
> The four are produced through `CM-014` and `CM-015` rather than internally.

> **`CI-11` — `R36` Customer and `R37` Corporate User receive statements in the form of
> `CM-013` and `CM-014` respectively**, not as internal change impact statements. They are
> counted here so that coverage cannot appear complete while an audience is unaddressed.

### 4.6 The bilingual rule for statements

**`CI-12` (recorded in §4.8): a statement for a Bengali-first role is produced in Bengali and
English.** From `CG-010` §3.3:

| Roles requiring a Bengali statement | Why |
|---|---|
| `R08` service centre agent · `R09` workshop supervisor · `R10`–`R12` technicians · `R16` rider · `R18` storekeeper · `R20` warehouse operative · `R29` cashier | Branch, field, workshop, store and counter populations |
| `R06` branch manager | 51+ sites; mixed English comfort |
| `R34` contact centre agent | Works in Bengali with customers |
| `R30`, `R31` HR — for anything reaching employees generally | `CG-010` §3.3: HR and payroll content is bilingual |

Head-office roles (`R01`–`R05`, `R07`, `R13`, `R17`, `R19`, `R21`–`R28`, `R32`, `R33`, `R35`)
receive English statements.

### 4.7 Effort

Stated because 38 statements is a real production load and appears in no plan.

| Component | Per statement |
|---|---|
| Current-state observation | 0.5–1 day |
| Future-state confirmation | 0.5 day |
| Drafting | 0.5 day |
| Two role-holder reviews | 0.5 day |
| Editorial, factual, HR and security review | 0.5 day |
| Bengali where applicable | 0.5 day |
| **Total** | **2.5–3.5 days**, or **3–4 days bilingual** |
| **38 roles** | **≈ 95–140 person-days** |

> **`CI-13` — this is between a third and a half of the entire `CM` category estimate.** Master
> Index §7 puts `CM` at 90–140 person-days for all 18 files. The per-role statements alone consume
> that. The estimate is wrong, and it is recorded here rather than absorbed. `O-01`.

### 4.8 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `CI-01` | Nine sections, fixed order, two pages | **H** |
| `CI-02` | No role is invented here; `05-04` and `MD-009` govern | **H** |
| `CI-03` | Section 9 — what we do not yet know — is mandatory | **H** |
| `CI-04` | "What stops" is named to an artefact, never to a behaviour | **H** |
| `CI-05` | Every "what stops" line has a withdrawal date and an owner | **H** |
| `CI-06` | Authority and access changes are stated, never left to be discovered | **H** |
| `CI-07` | Every registered role receives a statement at the wave that first touches it | **H** |
| `CI-08` | Every statement is reviewed by two people who hold the role | **H** |
| `CI-09` | Coverage is counted against 38 registered roles and reported | **H** |
| `CI-10` | `R38` external party receives four statements, produced through `CM-014` and `CM-015` | **H** |
| `CI-11` | `R36` and `R37` are addressed by `CM-013` and `CM-014` and counted in coverage | **H** |
| `CI-12` | Statements for Bengali-first roles are bilingual (`CG-010` §3.3) | **H** |
| `CI-13` | The effort figure is reported to the PMO, not absorbed | **H** |
| `CI-14` | The template is English; **every instance for a Bengali-first role is bilingual** | **H** |
| `CI-15` | A statement never amends a job description, a grade or a reporting line; HR checks this before issue | **H** |
| `CI-16` | A statement is reissued when the role's wave scope changes, not annotated | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-04` §1, §2 | The 38 roles, their headcounts, data scope and portal access — sections 1 and 6 |
| `MD-009` | Role and job title master; `CI-02` |
| `TR-002` | The role-to-pack map that section 7 draws its training dates from |
| `05-05` · `MD-015` | Approval limits and authority for section 6 |
| BRD §6.2 | The current-state artefacts section 3 names |
| `SP-*` | The future-state procedures section 4 describes |
| [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) | Vocabulary and the what-does-not-change discipline |
| [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) | K2 is the statement's communication form (`WL-06`) |
| [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) | The objections a statement provokes, particularly `OB-03` and `OB-05` |
| [`CM-014_Corporate_Client_Transition_Pack.md`](CM-014_Corporate_Client_Transition_Pack.md) · [`CM-015_Vendor_and_Seller_Transition_Pack.md`](CM-015_Vendor_and_Seller_Transition_Pack.md) | Where the `R37` and `R38` statements are produced |
| `M29` | Access provisioning that section 6 describes |

| Depended on by |
|---|
| `CM-005` K2 · `CM-010` slide 3 · `TR-002` course design inputs · `CM-012` D4 role scoping · line-manager conversations at 51+ sites |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave, for the roles that wave touches**; all statements reviewed at each wave gate for continued accuracy |
| Trigger for out-of-cycle review | A role added or changed in `05-04` or `MD-009` · a scope change altering what stops · an authority or SoD change · a section 9 open item closing |
| Owner | Change Lead; section 6 co-owned with the Security Lead; HR check owned by the HR Director |
| Change log | `RF-006`; a structural change is MAJOR and reissues all statements |
| Enforcement | `CI-01`…`CI-16`; coverage count reported to `S02` via `CM-004` Section 5 |
| Improvement loop | **A statement whose section 3 artefact is still in use at the wave gate is the finding.** It means either the withdrawal date was not owned or the replacement does not do the job, and both are answerable before the next wave |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The effort estimate for this category is wrong.** §4.7 derives 95–140 person-days for the 38 statements alone; Master Index §7 allocates 90–140 person-days for **all 18 `CM` files**. Either the statements are not produced to this standard or the category estimate must be restated. This compounds audit finding **AF-09**, which already records that content effort sits outside the approved business case | Programme Content Lead with the PMO | **W1 — with the next `AF-09` escalation** |
| **`O-02`** | **The current state has not been observed for any role.** `CI-07` step 2 requires observation rather than assumption, and BRD §6.2 describes fifteen processes at company level, not at role level across 51+ sites. Without observation, section 3 is written from the specification's description of the past | Business Process Lead | **W1 minus 8 weeks for the eleven W1 roles** |
| **`O-03`** | **Section 6 cannot be completed for most roles.** Approval limits live in `MD-015` and `05-05`; the 30 segregation-of-duties controls and six isolation tiers are specified but not yet configured. Authority changes therefore cannot be stated with confidence, which is precisely what `CI-06` exists to prevent | Security Lead with the module business owners | **W1** |
| **`O-04`** | **`TR-002` records that three roles are unregistered in `MD-009` and four carry declared interim training routes** (`AUDIT-009` finding TR-01 and the register consequence). `CI-02` prohibits inventing a role here, so those roles cannot receive a statement until the register is corrected | HR Director with Programme Content Lead | **W1** |
| **`O-05`** | **`CI-08` requires two role-holder reviews per statement — 76 reviews across 38 roles**, from people whose time is the programme's binding constraint (`RSK-001`, `CON-12`). No allocation exists | Change Lead with department heads | **W1** |
| **`O-06`** | **Eleven of the 38 role types require a Bengali statement** (§4.6), and no Bengali production capacity is allocated to this file. `CI-14` makes the instance obligation binding despite the template being English | Localisation Lead | **W1 minus 4 weeks** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action content present (`CG-009` §3) — expressed as the §4.4 production sequence and §4.5 wave assignment
- [x] Nine-section structure fixed, with both "what stays the same" and "what we do not yet know" mandatory
- [x] **"What stops" required to name an artefact with a withdrawal date and owner**, tying to the `DM-014` `CV-03` gate rule
- [x] Authority and access section required, with the SoD-loss case made explicit
- [x] **All 38 registered roles assigned to a wave**, with `R36`, `R37` and `R38` handled explicitly rather than silently omitted
- [x] Two role-holder reviews made a production requirement
- [x] Bilingual rule stated for the eleven Bengali-first role types despite the template being English
- [x] **Effort derived and the resulting contradiction with Master Index §7 reported rather than absorbed**
- [x] Sixteen governing rules with enforcement classes
- [x] All internal links resolve
- [x] Bengali counterpart — n/a for the **template**, `bilingual: no` per `CG-010` §3.2; **instances for Bengali-first roles are bilingual under `CI-14`**
- [ ] **`O-01` category effort estimate contradicted by this file's own derivation**
- [ ] **`O-02` current state unobserved for every role**
- [ ] **`O-03` section 6 authority changes cannot yet be stated**
- [ ] **`O-04` three roles unregistered in `MD-009`**
- [ ] **`O-05` 76 role-holder reviews unallocated**
- [ ] Named approver recorded — **pending Content Design Lead with the HR Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
