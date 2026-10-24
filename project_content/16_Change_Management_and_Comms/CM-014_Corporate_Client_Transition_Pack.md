---
id: CM-014
title: Corporate Client Transition Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Account Management
author: Change Lead with Account Management and Content Design
reviewers: [CCO, CFO, Account Management Lead, Service Operations Director, Legal & Compliance, Financial Controller, Support Lead, Content Design Lead, Localisation Lead, Programme Content Lead]
approver: Content Design Lead, with the CCO approving client-facing commitments and Legal approving any contractual statement
content_class: D
purpose: >
  Gives every account manager the same materials and the same sequence for taking a contracted
  corporate or government client through the transition to the B2B portal — estate upload,
  approval-chain configuration, consolidated invoice format change, SLA reporting continuity and
  the escalation path — account by account rather than by broadcast. Corporate clients have
  contractual expectations that a system change does not suspend, and an unmanaged transition
  puts renewal at risk on accounts the company cannot afford to lose.
traces_to: [P04, EO-007, EO-008, CM-001, CM-002, CM-003, CM-016, CM-018, DM-004, DM-008, DM-010, LG-003, LG-016, LG-015, MD-015, MD-028, NT-010, 04-00, 06-01, M05, M08, M20]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 — corporate B2B portal capability set and KPIs, including above 85% of contracted clients actively using the portal and invoice disputes below 3%
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-011 — corporate clients do not use the B2B portal, mitigated by account-manager-led onboarding and demonstrable time saving
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 Wave 4 — corporate B2B portal, contract engine, billing engine and consolidated B2B invoicing delivered at W4; gate criterion G4-05 requires 10+ corporate clients transacting
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 — multi-level approval chains, asset estate bulk upload, consolidated invoicing by cycle and scoped analytics
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.3 — corporate client users are partly bilingual; portal UI yes, contractual and technical documents English
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §3.1 DEP-04 — contract product definitions for all 14 families required at W4 start, owned by the CCO, blocking contract engine configuration if late
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-014 — Corporate Client Transition Pack

> **Scope note.** This file owns **the transition of an existing contracted client**. It does not
> own onboarding a new one ([`EO-007`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md)) or
> configuring the client's own administration
> ([`EO-008`](../18_Ecosystem_Onboarding_Content/EO-008_Corporate_Admin_Setup_and_Delegation_Guide.md)). It does not own the
> contract, the SLA, the invoice template or the portal. **The boundary with `EO-007` and `EO-008`
> is stated in `O-01` and is not yet agreed on both sides.**
>
> **Contract note.** Nothing here amends an agreement. `AT-02` is absolute: **a transition
> communication is not a contract variation**, and any change to invoice format, SLA reporting or
> service credit calculation that touches an agreed term goes through Legal and the CCO as a
> variation, in writing, on the client's paper.

---

## 1. Purpose

The register's justification is exact: *"Corporate clients have contractual expectations;
unmanaged transition risks renewal."*

A corporate client is not an audience. It is a set of named people — a requester, an approver, a
finance contact, an administrator — inside an organisation that has its own change process, its
own procurement calendar and its own view of what it agreed to. The transition happens inside
their organisation, on their terms, or it does not happen.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| Broadcast transition | Ten to forty organisations receive a message none of them can act on |
| Invoice format changed without notice | The invoice fails the client's AP system and is not paid; the dispute rate target is 3% |
| Estate not uploaded before invitation | The client logs in, sees nothing of theirs, and does not return |
| Approval chains not configured | The client's own approvals deadlock, and the company is blamed (`EO-008`'s stated risk) |
| SLA reporting discontinuity | A client cannot evidence service credits across the change and disputes the period |
| Account manager not equipped | Each of 8–20 account managers improvises, and the largest clients get the least consistent treatment |
| Transition scheduled into their year-end | The client's finance team declines to engage, and the account slips a quarter |
| Renewal conversation collides with transition | Two difficult conversations at once, on the account the company can least afford to lose |

---

## 2. Scope

**In scope:** the account-level transition sequence; the pre-conditions before a client is
invited; the six assets; the invoice-format change and its notice period; SLA and service-credit
continuity; approval-chain configuration; the client-side stakeholder map; the renewal-collision
rule; measurement; and rules `AT-01`…`AT-16`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Onboarding a **new** corporate client | [`EO-007`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md) |
| Corporate administrator setup and delegation | [`EO-008`](../18_Ecosystem_Onboarding_Content/EO-008_Corporate_Admin_Setup_and_Delegation_Guide.md) |
| Contracts, terms, SLA definitions and service credits | `LG-003`, `LG-015`, `LG-016`; `MD-028` |
| Consolidated invoice template and its statutory content | `DT-*` billing templates |
| Contract and entitlement data migration | `DM-010`; open items `DM-008` |
| Corporate portal UI copy | `UI-014`; Bengali in `BN-012` |
| Transactional notifications to corporate users | `NT-010` |
| Adoption campaigns after transition | [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) |
| Managed-services estate onboarding | `M05`; `EO-007` |
| Individual customer transition | [`CM-013_Customer_Migration_and_Transition_Pack.md`](CM-013_Customer_Migration_and_Transition_Pack.md) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Account Managers (`R22`, 8–20)** | Run an account transition to one sequence |
| **CCO** | Assure consistency across the contracted base |
| **Financial Controller** | Time the invoice-format change against billing cycles |
| **Service Operations Director** | Confirm SLA reporting continuity across the change |
| **Legal** | Identify what is a variation and what is not |
| **Change Lead** | Track transition coverage against `G4-05` and the 85% target |
| **Support Lead** | Anticipate corporate enquiry load |

---

## 4. Content

### 4.1 The unit of transition is the account

**`AT-01`: one plan per account, owned by its account manager, with a date agreed with the
client.** Nothing in this file is sent to more than one organisation at a time.

| Account tier | Definition | Treatment | Sequence length |
|---|---|---|---|
| **Tier 1 — strategic** | Highest revenue, multi-site, or government | **Face-to-face, executive-sponsored**, bespoke schedule | 10–12 weeks |
| **Tier 2 — core contracted** | Standard AMC/RAMC or managed-services contract | Account-manager-led, standard sequence | 6–8 weeks |
| **Tier 3 — light** | Low volume, single site | Guided self-serve with a scheduled call | 3–4 weeks |

> **`AT-03` — `G4-05` requires 10+ corporate clients transacting at the W4 gate**, and `04-00`
> §P04 targets **> 85% of contracted clients active**. Those are different numbers doing different
> jobs: ten is the gate, 85% is the outcome. **The ten are chosen for transition first, and they
> are chosen for likelihood of success, not for size.**

### 4.2 The account sequence

| # | Step | Owner | Offset | Client action |
|:--:|---|---|---|---|
| 1 | **Account assessment** — users, sites, approval chains, invoice format, SLA reporting, estate size | Account Manager | W4 − 12 weeks | — |
| 2 | **Executive notice** to the client's contract owner | Account Manager (Tier 1: with the CCO) | W4 − 10 weeks | Acknowledge; nominate a project contact |
| 3 | **Client stakeholder map** — requester, approver, finance, admin, IT | Account Manager | W4 − 9 weeks | Confirm names |
| 4 | **Estate data prepared and validated with the client** | Account Manager + Data Migration | W4 − 8 weeks | **Review and confirm the estate** |
| 5 | **Invoice-format change notice** — with a sample | Account Manager + Finance | **W4 − 8 weeks minimum** | Confirm their AP system accepts it |
| 6 | **Approval-chain design session** | Account Manager | W4 − 6 weeks | Confirm the chain and the delegated limits |
| 7 | Account configured and populated — estate, users, contracts, entitlements | Account Manager + Ops | W4 − 3 weeks | — |
| 8 | **Administrator handover session** | Account Manager | W4 − 2 weeks | Their admin takes control |
| 9 | **First transaction assisted** — one request, one approval, one invoice view | Account Manager | W4 | — |
| 10 | **Parallel window** — existing route accepted alongside the portal | Account Manager | W4 to W4 + 8 weeks | — |
| 11 | **Route closed for this account**, confirmed in writing | Account Manager | W4 + 8 weeks | **Confirm** |
| 12 | **Post-transition review** with the client | Account Manager | W4 + 12 weeks | Attend |

> **`AT-04` — step 5 has a minimum notice period, not a target one.** A corporate client's
> accounts-payable system has to accept the new invoice. `04-00` §P04 targets **invoice disputes
> below 3% of consolidated invoices**; an unannounced format change puts every invoice in that
> cycle at risk simultaneously.

> **`AT-05` — step 8 is a handover, not a demonstration.** `EO-008`'s stated risk is that
> *"corporate admins configure their own delegation chains; errors here produce approval deadlocks
> the company gets blamed for."* The session ends with the client's administrator having made a
> change themselves.

### 4.3 The six assets

| # | Asset | For | When | Owner |
|:--:|---|---|---|---|
| **B1** | **Account manager playbook** — the sequence, what to say, what is a variation | `R22` | Before W4 − 12 weeks | Change Lead |
| **B2** | **Executive transition letter** — what changes, why, what is required, who owns it | Client contract owner | Step 2 | Account Manager |
| **B3** | **Estate validation pack** — the client's own asset estate, in a form their facilities or IT team can check | Client project contact | Step 4 | Account Manager + Data Migration |
| **B4** | **Invoice-change notice with a worked sample** | Client finance contact | **Step 5** | Finance + Account Manager |
| **B5** | **Administrator handover guide** — users, sites, approval chains, delegated limits | Client administrator | Step 8 | Account Manager |
| **B6** | **Continuity statement** — SLA measurement, service credits, reporting, escalation contacts across the change | Client contract owner | Step 2, restated at step 12 | Service Ops + Legal |

> **`AT-06` — B6 is the asset that protects the renewal.** It states, in writing, that SLA
> measurement is continuous across the transition, how a period spanning the change is calculated,
> and that the escalation contacts do not change. Without it, the first breached SLA after the
> change becomes an argument about whether the clock was running.

### 4.4 SLA and service-credit continuity

**`AT-07`: a period spanning the transition is calculated on a stated basis, agreed before the
transition, not after the first breach.**

| Question | Position |
|---|---|
| Which system measures the SLA during the parallel window? | **Declared in B6 per account, before step 9** |
| How is a period spanning the cutover calculated? | Stated in B6; the default is to close the legacy period and open a new one at the cutover instant |
| Are service credits affected? | **No.** Any change is a variation (`AT-02`) |
| Where does the client see their SLA position? | `P04`; and until then, the existing report, unchanged |
| What if the reporting differs between systems? | **Investigated against `DM-013`**, not resolved in the client's disfavour by default |

> **`AT-08` — `MD-028` SLA definitions carry a known defect.** `AUDIT-013` finding `LG-01`
> records that `DT-031` maps nine `MD-028` fields that do not exist and that `MD-028` has no clock
> start/stop event field at all — audit check `F3` fails today. **Until that is resolved, B6 cannot
> state how a period spanning the transition is calculated**, because the clock's start and stop
> are not defined in the master data. Recorded as `O-02`.

### 4.5 The client-side stakeholder map

`AT-09`: the transition reaches **five roles inside the client**, and missing any one stalls it.

| Client role | What they need | What stalls if they are missed |
|---|---|---|
| **Contract owner** | Why, what is required, what does not change | Nothing starts |
| **Project contact** | The sequence and the dates | The account drifts |
| **Requester community** | How to raise a request; that bulk upload exists | Requests keep arriving by email |
| **Approver(s)** | The approval chain and their delegated limit | **Approval deadlock** — `EO-008`'s stated risk |
| **Finance contact** | The invoice format change, with a sample | **Invoices unpaid** |
| **IT / security** | Access, SSO, data handling | Portal access blocked at their firewall |

### 4.6 Timing constraints inside the client

**`AT-10`: the transition is scheduled around the client's calendar, not the programme's.**

| Constraint | Rule |
|---|---|
| Client financial year-end | **No transition in the month before or after** |
| Their own system change freeze | Asked for at step 1; respected |
| **Renewal date** | **No transition step in the 60 days before a renewal decision** (`AT-11`) |
| Peak operational period | Asked for at step 1 |
| Ramadan and Eid | `ASM-16` applies to clients as it does internally |

> **`AT-11` — transition and renewal are never negotiated in the same conversation.** A client
> being asked to change how they transact and to re-sign in the same quarter will treat the change
> as a negotiating position. `RSK-011` rates corporate portal non-adoption Medium/Medium; a
> mishandled renewal is a different and larger loss.

### 4.7 Measurement

| Measure | Source | Target |
|---|---|---|
| Accounts transitioned / contracted base | Transition register | **> 85% active** (`04-00` §P04) |
| **Clients transacting at the W4 gate** | `P04` | **10+** (`G4-05`) |
| Bulk requests via portal | `P04` | > 70% of corporate requests |
| **Invoice disputes** | Finance | **< 3% of consolidated invoices** |
| Approval deadlocks reported | Support | **Zero tolerance; each investigated** |
| **SLA disputes citing the transition** | Service Ops | **Zero** |
| Corporate client satisfaction | Survey | > 4.6/5 |
| Renewal rate on transitioned accounts | Commercial | **No worse than the pre-transition base** |

> **`AT-12` — the renewal-rate measure is the one that matters.** Portal adoption on an account
> that then fails to renew is not a success. It is the only measure in this file that captures the
> risk the register named.

### 4.8 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| `R22` account managers | B1 playbook + briefing | **W4 − 14 weeks** | The sequence, the variation boundary | Complete step 1 for every account |
| Client contract owner | **Letter + meeting** (Tier 1: with the CCO) | W4 − 10 weeks | B2 transition letter, B6 continuity statement | Acknowledge; nominate a project contact |
| Client project contact | Working session | W4 − 9 weeks | The sequence and dates | Confirm the stakeholder names |
| Client facilities / IT | B3 estate pack | W4 − 8 weeks | Their own estate, to check | **Review and confirm** |
| **Client finance contact** | **B4 notice with a sample invoice** | **W4 − 8 weeks minimum** | The format change | **Confirm your AP system accepts it** |
| Client approvers | Design session | W4 − 6 weeks | Approval chain and limits | Confirm the chain |
| Client administrator | **B5 handover session** | W4 − 2 weeks | Configuration control | **Make one change yourself** |
| Client requesters | Short guide + `EO-007` when it exists | W4 − 1 week | How to raise a request | Raise your next request in the portal |
| Client contract owner | Review meeting | W4 + 12 weeks | What worked; what is open | Agree the close-out |
| `S02` Steering | `CM-004` Section 5 | Monthly | Accounts transitioned; the ten for `G4-05` | Unblock the named account |

### 4.9 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `AT-01` | One transition plan per account, owned by its account manager, dated with the client | **H** |
| `AT-02` | **A transition communication is never a contract variation**; anything that is goes through Legal and the CCO in writing | **H** |
| `AT-03` | The ten `G4-05` accounts are chosen for likelihood of success, not for size | **H** |
| `AT-04` | The invoice-format change carries a minimum eight weeks' notice with a worked sample | **H** |
| `AT-05` | The administrator session is a handover; it ends with the client making a change | **H** |
| `AT-06` | Every account receives a written continuity statement before its first transaction | **H** |
| `AT-07` | A period spanning the transition is calculated on a basis agreed in advance | **H** |
| `AT-08` | B6 cannot state the spanning-period basis while `MD-028` lacks clock start/stop events | **H** |
| `AT-09` | Five client-side roles are identified and reached; none is assumed | **H** |
| `AT-10` | The transition is scheduled around the client's calendar | **H** |
| `AT-11` | No transition step within 60 days of a renewal decision | **H** |
| `AT-12` | Renewal rate on transitioned accounts is measured and reported | **H** |
| `AT-13` | The account is populated with the client's own estate and contracts before invitation | **H** |
| `AT-14` | The existing route runs in parallel for eight weeks and its closure is confirmed in writing | **H** |
| `AT-15` | Every promise is limited to delivered `04-00` §P04 capability (`NR-08`) | **H** |
| `AT-16` | An approval deadlock reported by a client is investigated individually, same day | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `04-00` §P04 | The capability, the targets and the invoice-dispute tolerance |
| `06-02` `G4-05` | Ten clients transacting — the gate this pack must deliver |
| `00-04` §1.2 `RSK-011` | The risk and its account-manager-led mitigation |
| `00-04` §3.1 `DEP-04` | Contract product definitions for all 14 families, required at W4 start |
| `MD-028`, `LG-015` | SLA definitions and service credits — **`AUDIT-013` `LG-01` records `F3` failing today** |
| `LG-003`, `LG-016` | Corporate terms; the agreements `AT-02` protects |
| [`../12_Data_Migration_Content/DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md`](../12_Data_Migration_Content/DM-010_Field_Mapping_Workbook_Contracts_Warranty_and_Claims.md) | Contract and entitlement migration behind step 4 |
| [`EO-007`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md) · [`EO-008`](../18_Ecosystem_Onboarding_Content/EO-008_Corporate_Admin_Setup_and_Delegation_Guide.md) | Onboarding and administrator setup — steps 8 and 12 hand over to them (`O-01`) |
| `NT-010` | Corporate transactional messages this pack must not duplicate |
| [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) | `CI-11` counts `R37` corporate users as addressed here |
| [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) | The campaign that follows the transition |

| Depended on by |
|---|
| `G4-05` gate evidence · the `P04` 85% adoption target · corporate renewal continuity · `CM-016` corporate campaign baseline · `CI-10`/`CI-11` `R37` coverage |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **After every account transition**, and at the W4 gate |
| Trigger for out-of-cycle review | An invoice dispute attributed to the change · an approval deadlock · an SLA dispute citing the transition · a contract variation |
| Owner | Account Management; B4 co-owned with Finance; B6 co-owned with Service Operations and Legal |
| Change log | `RF-006`; any change to B6 or to an invoice statement requires Legal and the CCO |
| Enforcement | `AT-01`…`AT-16`; transition register reconciled weekly; renewal rate reported at each wave gate |
| Improvement loop | **The first three accounts are run as a deliberate pilot and the sequence is corrected before the fourth.** With 8–20 account managers and a contracted base in the tens, there is no second chance to standardise once everyone has started |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The boundary with `EO-007` and `EO-008` is undefined in both directions.** Both files exist and are at `Draft`. `EO-008` covers multi-user, multi-site, multi-level approval configuration — which is also step 6 and asset B5 here. **Neither file states which one an account manager follows for an *existing* client**, and `TR-023`/`CM-008` proved that two categories describing one activity without a stated boundary produces two competing programmes. This is that pattern, one category later | Programme Content Lead with Account Management | **W4 minus 3 months** |
| **`O-02`** | **B6 cannot be written while `MD-028` is defective.** `AUDIT-013` `LG-01` records that audit check `F3` fails today — `DT-031` maps nine `MD-028` fields that do not exist and `MD-028` carries no clock start/stop event field. `AT-07` and `AT-08` require the spanning-period calculation to be agreed in advance; **it cannot be stated at all until the SLA clock is defined**, and service credits carry financial liability | Service Operations Director with Legal and the MDM lead | **W4 minus 4 months** |
| **`O-03`** | **`DEP-04` contract product definitions for all 14 families are required at W4 start and are not confirmed.** Step 7 configures the account against them; without them the estate can be uploaded and the contracts cannot | CCO | **W4 start** |
| **`O-04`** | **The contracted base has not been assessed or tiered.** §4.1 and step 1 both assume an account register with tier, renewal date, invoice format, approval structure and year-end. `G4-05` needs ten accounts chosen twelve weeks before the gate | Account Management Lead | **W4 minus 5 months** |
| **`O-05`** | **The eight-week parallel window is unpriced**, matching `CM-015` `O-07` on the supply side. Account managers running two request-intake routes and finance running two invoice routes for two months, staggered across the base, is a real cost in the function whose availability is already a constraint | CCO with CFO | **W4 minus 3 months** |
| **`O-06`** | **`AT-11` renewal proximity cannot be applied without renewal dates**, which sit in the contract base that `O-04` records as unassessed. The rule protecting the outcome the register named — renewal — is currently unenforceable | Account Management Lead | **W4 minus 5 months** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Account, not audience, established as the unit of transition**, with three tiers and a distinct sequence length each
- [x] Twelve-step sequence with the client actions and the reply points identified
- [x] **Invoice-format change given a minimum notice period with a worked sample**, tied to the 3% dispute tolerance
- [x] Administrator session specified as a handover ending in a client-made change
- [x] **SLA and service-credit continuity made a written statement per account**, with the `MD-028` defect blocking it recorded rather than written around
- [x] Five client-side roles identified with the stall each one causes
- [x] Client-calendar constraints including the 60-day renewal exclusion
- [x] **Renewal rate measured**, as the only measure that captures the risk the register named
- [x] Contract-variation boundary stated and made absolute
- [x] Sixteen governing rules with enforcement classes
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2 and §3.3 (corporate contractual and technical documents are English; `P04` portal UI is bilingual and is owned by `UI-014` and `BN-012`)
- [ ] **`O-01` boundary with `EO-007` and `EO-008` undefined in both directions**
- [ ] **`O-02` B6 unwritable — `MD-028` has no SLA clock definition and `F3` fails today**
- [ ] **`O-03` `DEP-04` contract product definitions unconfirmed**
- [ ] **`O-04` contracted base not assessed or tiered**
- [ ] **`O-06` `AT-11` unenforceable without renewal dates**
- [ ] Named approver recorded — **pending Content Design Lead with the CCO and Legal**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
