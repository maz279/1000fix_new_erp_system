---
id: OP-015
title: Access Request and Joiner, Mover, Leaver Content
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Security with HR
author: Security Lead with HR and Platform Engineering
reviewers: [Chief Technology Officer, HR Director, Chief Financial Officer, Internal Audit, Data Protection Officer, Operations Director, Support Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  The request forms, the approval routing, the standard access profile for every role, and the
  joiner, mover and leaver procedures that grant and remove access across 67 modules and 12
  portals. High technician turnover with unrevoked access is the most common insider-risk finding
  in service businesses, and an access model with no standard profiles becomes a model where
  everyone has whatever the last similar person had.
traces_to: [M29, M21, M66, MD-008, MD-009, MD-012, 05-04, SP-006, 05-06 NFR-011, NFR-012, NFR-064, KPI-090, OP-001, OP-009, OP-013, SP-004, SP-023, SP-031, UI-036, LG-021]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md — 38 roles, portal access matrix, SoD exception authority
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-090 — orphaned accounts after leaver, zero beyond 24 h
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md §1 — leaver access revoked within one hour (BRU-SEC-06); §2 joiner and leaver decisions sit in SP-023 and are executed here
    verified: 2026-08-20
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md and MD-012_Employee_Master_Data_Template.md — the role and employee records access profiles attach to
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-011 field-level RBAC; NFR-012 MFA for privileged roles; NFR-064 segregation of duties enforced by the permission engine
    verified: 2026-08-20
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md §3 — 05-04 §6 registers SOD-01…SOD-12 while module files use SOD-01…SOD-30, nine numbers carry two meanings, and the second meanings are reallocated to SOD-31…SOD-39
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# OP-015 — Access Request and Joiner, Mover, Leaver

> **Access is granted in a minute and removed in a quarter, unless something forces the removal.**
> This file is that something.
>
> Two numbers frame it: **38 roles** (`05-04`) and **zero orphaned accounts beyond 24 hours**
> (`KPI-090`). Everything here exists to make the first manageable and the second true.

---

## 1. Purpose

**What stops without this file:**

| Absent | Consequence |
|---|---|
| Standard access profiles | Every grant is bespoke, justified by "the same as her", and the model drifts within one quarter beyond anyone's ability to describe |
| A request form and route | Access is requested in messages and granted by whoever is helpful. [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) A-85/A-86 exists precisely to stop this |
| Leaver automation with a deadline | Departed technicians keep working accounts. At high field turnover this is the largest standing insider risk the company holds |
| **Mover** handling | The most-missed case: people accumulate access as they move, and after three moves hold a combination nobody would ever have approved as a whole |
| Recertification | The model is only as accurate as its last review; without one, it describes the company as it was |
| SoD checking at grant time | `NFR-064` conflicts are discovered by audit rather than prevented at the point of request |

---

## 2. Scope

**In scope:** access classes; the standard access profile model per role; the request forms and
their fields; approval routing; joiner, mover and leaver procedures with timings; temporary,
emergency and third-party access; equipment allocation and recovery; recertification; segregation
of duties at grant time; and the evidence retained.

**Out of scope:**

| Situation | Owned by |
|---|---|
| Who a role is and what it does | [`MD-009`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md), `05-04` |
| The permission model itself | `M29`, `05-04` |
| Identity operations — resets, MFA, sessions, break-glass | [`OP-009`](OP-009_Runbook_Identity_and_Access.md) |
| The HR decision to hire, move or exit someone | [`SP-023`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) |
| Approval authority limits generally | `SP-004` |
| Executing the provisioning tickets | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) |
| Customer, seller, vendor or partner portal registration | The relevant `EO` onboarding kit |
| IT asset lifecycle beyond allocation and recovery | `M66` |

---

## 3. Audience

| Reader | Uses this file to |
|---|---|
| Line managers | Raise and approve requests correctly, first time |
| HR | Trigger joiner, mover and leaver events |
| Service desk (T1) | Process requests and refuse the ones that bypass the route |
| Security | Approve privileged access and run recertification |
| Internal Audit | Evidence that access is controlled |
| Branch managers | Understand what happens on the day a technician leaves |
| New joiners | Know what they will get and when |

---

## 4. Content

### 4.1 Access classes

| Class | Definition | Approval | MFA | Recertify |
|:--:|---|---|:--:|---|
| **A0 — Standard profile** | The access every holder of a role gets, by definition of the role | Line manager only (confirms the role) | Per role | Annually |
| **A1 — Extended** | Additional access within the person's function | Line manager + function head | Per role | Every 6 months |
| **A2 — Cross-functional** | Access belonging to another function | Both function heads | Yes | Every 6 months |
| **A3 — Privileged** | Administration, configuration, security, or unrestricted data access | **CTO or Security Lead** | **Mandatory** (`NFR-012`) | **Quarterly** |
| **A4 — Financial authority** | Payment release, credit note, price override, payroll | **CFO** | **Mandatory** | **Quarterly** |
| **A5 — Temporary** | Any class, time-boxed, with an automatic expiry | As for the underlying class | As for the class | Expires — never recertified |
| **A6 — Third party** | Vendor, contractor, auditor, implementation partner | CTO + sponsoring manager | **Mandatory** | **Quarterly, and on contract change** |
| **A7 — Break-glass** | Emergency administrative access | Pre-authorised (`OP-009` §9) | N/A — sealed procedure | Tested quarterly |

> **`AC-01`.** Every grant belongs to exactly one class. A request that does not fit a class is
> refused and escalated — a new class is a decision, not a workaround.

### 4.2 Standard access profiles

The mechanism that makes 38 roles administrable. A profile is **attached to the role in `MD-009`**,
not to the person, and joining a role grants it automatically.

| Element | Rule |
|---|---|
| Owner | The function head owns the profile for their roles; Security owns the model |
| Content | Modules, portals, record scope (branch/division/company), field-level restrictions (`NFR-011`), approval limits |
| Scope default | **Branch-level isolation is the default** (`NFR-015`); wider scope is an A1/A2 grant with a reason |
| Change | A profile change is a change to *everyone* holding that role and follows `SP-031` CAB, with an impact list |
| Review | Annually, and whenever the role definition changes in `MD-009` |
| Exceptions | Recorded against the person with an expiry, never absorbed into the profile |

**Profile coverage requirement.** Every one of the 38 roles in `05-04` must have a profile before
its first holder is provisioned. **Profiles do not exist yet** — see OI-01; until they do, every
grant is bespoke and `A0` cannot operate.

| Role family (`MD-009`) | Typical portals | Typical class | Notes |
|---|---|---|---|
| Branch and front desk | `P03` | A0 | Branch-scoped by default |
| Field technician | `P02` | A0 | Own jobs only; device-bound |
| Rider / logistics | `P09` | A0 | Own consignments |
| Dispatcher | `P03` | A0 + A1 | Branch or zone scope |
| Workshop and quality | `P03`, `P11` | A0 | |
| Warehouse and procurement | `P03`, `P05` | A0 + A1 | SoD: cannot both order and receive (`NFR-064`) |
| Finance and cashier | `P03` | A0 + **A4** | SoD: cannot both post and approve payment |
| HR and payroll | `P03` | A0 + A1, payroll is **A4** | Sensitive personal data (`NFR-086`) |
| Contact centre | `P10` | A0 | Customer data, no financial authority |
| Account management | `P04` | A0 + A2 | Client-scoped |
| Marketplace ops | `P07` | A0 + A1 | |
| Analytics and BI | `P06` | A0 + A2 | Read-only by default; export permissions per [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) |
| IT / system administration (`R33`) | All | **A3** | Recorded sessions (`NFR-070`) |
| Executive | `P06`, read across | A2 | Read-heavy, write-light — the profile most often over-granted |

### 4.3 The request form

One form, all classes. Fields marked ✱ are mandatory and a request without them is returned, not
chased.

| Field | Notes |
|---|---|
| ✱ Requester | Who is asking |
| ✱ For whom | The person the access is for — **often not the requester** |
| ✱ Employee ID / contract reference | Links to [`MD-012`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md) or the third-party contract |
| ✱ Role | From `MD-009` |
| ✱ Access class | §4.1 |
| ✱ What is needed | In business terms — *"approve purchase orders up to BDT 200,000 for Chattogram"*, not *"same as Rahim"* |
| ✱ Business reason | Why the standard profile is insufficient (A1+ only) |
| ✱ Start date | |
| **✱ End date** | **Mandatory for A5, A6 and every contractor grant.** A request with no end date for a temporary class is invalid |
| Branch / division scope | Defaults to the person's own (`NFR-015`) |
| Financial limit sought | A4 only; must reconcile with `SP-004` |
| SoD declaration | Auto-checked; conflicts surface to the approver (§4.7) |
| Data classification touched | Whether the access reaches S3/sensitive data (`NFR-086`) |
| ✱ Approver(s) | Routed automatically by class |

**Refusal reasons that are always valid:** no business reason; "same as" without specifics; no end
date on a temporary class; an SoD conflict without an approved exception; a request for someone
else's account rather than access for a named person; a request routed around the form
([`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) `mac.int.access_route`).

### 4.4 Joiner

| Step | Action | Owner | Timing |
|---:|---|---|---|
| 1 | HR creates the employee record; the joiner event fires (`M21`) | HR | On contract signature |
| 2 | Line manager confirms role and start date; profile is derived (§4.2) | Line manager | ≥ 5 working days before start |
| 3 | Account created, disabled, with a start-date activation | Service desk | ≥ 2 working days before start |
| 4 | Equipment allocated and recorded against the person (`M66`) | Internal IT | Before start |
| 5 | Any A1+ access requested and approved separately | Line manager | Before start |
| 6 | **Day one:** account activates; the joiner sets their own password and enrols MFA | The joiner | Day 1 |
| 7 | Mandatory induction: security, data protection, acceptable use ([`LG-021`](../10_Legal_Policy_and_Compliance/LG-021_ISMS_Policy_Set.md)), before privileged access is enabled | L&D + joiner | Day 1–5 |
| 8 | Manager confirms the joiner can do their work — **an access request raised on day one is a profile defect**, and is recorded as such | Line manager | Day 1–5 |

**`JN-01`.** No account is created without an HR record. This closes the route by which contractors,
interns and "temporary help" acquire permanent access nobody can attribute.

### 4.5 Mover — the case that is always missed

| Step | Action | Owner | Timing |
|---:|---|---|---|
| 1 | HR records the change; the mover event fires (`M21`) | HR | On decision |
| 2 | **Old profile is removed and the new one applied.** The default is replacement, **never addition** | Service desk | Effective date |
| 3 | Any A1–A4 grants held under the old role are **revoked automatically**; they must be re-requested if still needed | System | Effective date |
| 4 | Handover period: where the person must retain old access to hand over, it is granted as **A5 temporary with an expiry ≤ 30 days** | Line manager | On request |
| 5 | Branch or division scope updated | Service desk | Effective date |
| 6 | SoD re-check against the new combination | System + Security | Effective date |
| 7 | Equipment reallocated if the role changes device needs | Internal IT | Within 5 working days |
| 8 | Both managers confirm completion | Old and new manager | Within 5 working days |

> **`MV-01`.** *Replacement, not addition,* is the entire content of this section. Every access
> model that has ever failed an audit failed at this step, because addition is the helpful thing to
> do and nobody is harmed on the day.

### 4.6 Leaver

| Step | Action | Owner | Timing |
|---:|---|---|---|
| 1 | HR records the exit; the leaver event fires (`M21`) | HR | On notice, with the effective date |
| 2 | Manager identifies records, approvals and customer relationships to transfer | Line manager | Before the last day |
| 3 | Data belonging to the company is transferred; personal data on devices handled per `LG-021` | Line manager + IT | Before the last day |
| 4 | **On the effective date: all access disabled and every session revoked** | System + service desk | **Within 1 hour of the effective time** (`SP-031` §1, `BRU-SEC-06`) |
| 5 | MFA devices deregistered; tokens and API credentials owned by the person rotated | Security | Same day |
| 6 | Equipment recovered and recorded; non-return escalated to HR the same day | Internal IT | Same day |
| 7 | Physical access, branch keys and building passes withdrawn | Branch manager / Admin | Same day |
| 8 | Mailbox handling per the retention policy; **auto-forwarding to a colleague is not permitted** without DPO agreement | IT + DPO | Same day |
| 9 | Account **disabled, not deleted**, for the retention period; then anonymised per `NFR-088` | IT | Per schedule |
| 10 | Leaver checklist signed and filed | HR | Within 2 working days |
| 11 | Exception report: any access still active after 24 hours | Security | Daily (`KPI-090`) |

**Immediate-exit variant.** For dismissal, resignation with immediate effect, or any exit with a
security concern: **steps 4–7 execute first, and step 2 is done afterwards from the disabled
account.** The decision to use this variant is HR's with Security, and it does not require the
manager's agreement.

> **A discrepancy that must be resolved, not averaged.** `SP-031` §1 requires revocation **within
> one hour**; `KPI-090` measures orphaned accounts **beyond 24 hours**. The one-hour rule is the
> procedure and the 24-hour figure is the tolerance the KPI reports against. This file operates to
> **one hour** and treats anything beyond it as a control failure even though the KPI would not
> report it. Raised as OI-04 so the two are aligned rather than quietly diverging.

### 4.7 Segregation of duties at grant time

`NFR-064` requires SoD to be enforced by the permission engine, not by review. The request form
checks the **resulting combination**, not the increment.

| Incompatible pair (illustrative — **the register is [`SP-006`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md)**, which harmonises `SOD-01`…`SOD-39`) | Why |
|---|---|
| Create a vendor **and** approve a payment to it | Fictitious-vendor fraud |
| Post a journal **and** approve it | Unreviewed adjustment |
| Order stock **and** receive it | Phantom receipt |
| Grant access **and** approve the grant | Self-service privilege |
| Change a price **and** approve the resulting credit note | Concealed discounting |
| Configure payroll **and** run it | Ghost employee |
| Execute a change **and** approve it (`SP-031`) | Uncontrolled production change |

| # | Rule |
|---|---|
| **SD-01** | A conflict is surfaced **to the approver, in plain language**, before approval — not logged for later audit |
| **SD-02** | Exceptions require **CFO or CTO** authority (`05-04` §7, `SP-004` A-85/A-86 routing), a stated compensating control, and an expiry |
| **SD-03** | Small branches genuinely cannot separate every duty. The answer is a **recorded exception with a compensating control** (dual sign-off on paper, weekly review by the branch manager), never a silent grant |
| **SD-04** | Exceptions are reviewed at every recertification and expire by default |

### 4.8 Temporary, emergency and third-party access

| Situation | Rule |
|---|---|
| **Temporary (A5)** | End date mandatory; expires automatically; extension is a new request, not an edit |
| **Emergency, out of hours** | The on-call may grant **A0/A1 only**, for ≤ 24 hours, recorded, with retrospective approval within 1 working day. A3/A4 emergency access goes through break-glass (`OP-009` §9), not through this route |
| **Third party (A6)** | Named individuals only — **never a shared vendor account**; contract reference recorded; expiry aligned to the contract; quarterly recertification; access removed on contract end **without waiting for a leaver event, because there will not be one** |
| **Corporate client administrators** (`P04`) | The client controls their own users; **our duty is to remove access on contract termination** ([`EO-014`](../18_Ecosystem_Onboarding_Content/EO-014_Ecosystem_Offboarding_and_Exit_Content.md)), and to require the client to notify us of their leavers (`OP-009` OI-04) |
| **Auditors and regulators** | Read-only, time-boxed, scoped, recorded; disclosure logged ([`AP-012`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md)) |

### 4.9 Recertification

| Class | Frequency | Reviewer | Non-response |
|:--:|---|---|---|
| A0 | Annually | Line manager confirms the person still holds the role | Role assumed correct if HR record matches |
| A1, A2 | 6 months | Line manager + function head | **Revoked** |
| A3, A4 | **Quarterly** | Security Lead / CFO | **Revoked** |
| A6 | Quarterly and on contract change | Sponsoring manager | **Revoked** |

| # | Rule |
|---|---|
| **RC-01** | **Non-response is revocation** (`OP-009` `RO-02`). A campaign that revokes nothing has measured nothing |
| **RC-02** | Reviewers see access **in business language**, not permission codes. A manager cannot certify `res.groups` membership |
| **RC-03** | Results are reported: percentage reviewed, percentage revoked, exceptions extended. A stable zero-revocation rate is itself a finding |
| **RC-04** | Before `M66` (W6), recertification is a manual campaign from `05-04` and `MD-009` — see OI-03 |

### 4.10 Evidence and measurement

| Evidence | Retention | Where |
|---|---|---|
| Request, approval, grant record | 7 years (`NFR-088`) | Ticket + identity audit log |
| SoD exception with compensating control | 7 years | Security register |
| Leaver checklist | 7 years | HR record |
| Recertification results | 7 years | Security register |
| Equipment allocation and return | Asset life + 7 years | `M66` asset register |

| Measure | Target | Source |
|---|---|---|
| **Orphaned accounts beyond 24 h** (`KPI-090`) | **Zero** | Daily exception report |
| Leaver revocation within 1 hour | ≥ 95%, rising to 100% | Identity audit vs HR effective time |
| Requests granted outside the form | **Zero** | Grant audit vs ticket record |
| Standard-profile coverage | 38 of 38 roles | `MD-009` |
| A3/A4 accounts with MFA | 100% (`NFR-012`) | Identity report |
| Recertification completion | 100% by deadline | Security register |
| Access requests raised in a joiner's first week | Declining — each one is a profile defect | Ticket system |
| Temporary grants past expiry | **Zero** | Identity report |

### 4.11 Open decisions

| # | Decision required | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|
| **OP-015-OI-01** | **The 38 standard access profiles do not exist.** They must be authored against `05-04` and attached in `MD-009` | Security + function heads | **W1** | Every grant is bespoke; `A0` cannot operate and W1 provisioning is manual and inconsistent |
| **OP-015-OI-02** | Automated joiner/mover/leaver from `M21` events — confirm it is in W1 scope, since `M66` (W6) owns the workflow | CTO | W1 | Leaver revocation is a manual promise against a one-hour deadline |
| **OP-015-OI-03** | Recertification tooling before W6 | Security Lead | W2 | `RC-01` cannot be executed at scale by hand for 800+ users |
| **OP-015-OI-04** | Reconcile the **one-hour** revocation rule (`SP-031`) with the **24-hour** KPI tolerance (`KPI-090`) | CTO + Internal Audit | W1 | Two standards for the same control |
| **OP-015-OI-05** | `SP-006` records that `05-04` §6 registers only `SOD-01`…`SOD-12` while module files use up to `SOD-30`, with nine numbers carrying two meanings. **Grant-time enforcement (`NFR-064`) cannot be built against a register in that state** — confirm `SP-006`’s reallocation to `SOD-31`…`SOD-39` is accepted first | CFO + Security + Enterprise Architecture | W1 | `SD-01` surfaces conflicts against an ambiguous register, and `M60` tests a control whose number means two things |
| **OP-015-OI-06** | Field technician turnover rate is unstated anywhere; it sizes the leaver process | HR Director | W1 | The highest-volume JML population is unquantified |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-04` | Roles, permissions, portal matrix and SoD authority |
| `MD-009`, [`MD-008`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md), `MD-012` | Where profiles attach and who holds them |
| `M21` | The joiner, mover and leaver events that drive everything here |
| `M29` / `OP-009` | Where access is actually granted and revoked |
| `M66` | Request workflow, asset allocation and recertification tooling from W6 |
| `SP-004` | Approval authority limits — access approvals are `A-85` (standard) and `A-86` (privileged) |
| `SP-006` | The segregation-of-duties register checked at grant time (§4.7) |
| `SP-023` | The HR decisions this file executes |
| `SP-031` | The provisioning and change procedure |
| `LG-021` | Acceptable use, induction and device handling |
| [`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) | The request route and its refusal macros |

**Depended on by:** `OP-001` · `OP-009` · [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) (`RT-07` on-call access) · [`UI-036`](../03_UI_Copy_and_Microcopy/03C_Admin_Workspaces/UI-036_Workspace_System_Console_Copy.md) ·
`MD-008`, `MD-009`, `MD-012` · `LG-021` · Internal Audit.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly for profiles and classes; annually for the file |
| Trigger for out-of-cycle review | A new role in `MD-009` · a new portal · any orphaned-account finding · any SoD exception granted at branch level · `M66` go-live |
| Owner | Security with HR |
| Change route | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md); profile changes follow `SP-031` CAB because they change many people at once |
| Evidence | Per §4.10 |

---

## Open Items

1. **OP-015-OI-01** — 38 standard access profiles do not exist (blocks W1 provisioning quality).
2. **OP-015-OI-02** — JML automation may not exist before W6.
3. **OP-015-OI-03** — no recertification tooling before W6.
4. **OP-015-OI-04** — one-hour rule vs 24-hour KPI tolerance unreconciled.
5. **OP-015-OI-05** — `SP-006` reports the `SOD-` identifier space is unharmonised (12 registered, 30 in use, 9 numbers with two meanings); grant-time SoD enforcement cannot be built on it.
6. **OP-015-OI-06** — technician turnover rate unstated; the leaver volume is unknown.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — applies to the request form when it is built, not to this file
- [x] Bengali counterpart — n/a by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2. **The request form itself is user-facing and will
      need Bengali when built as `UI` content**
- [ ] Named approver recorded — CTO; HR Director and CFO co-approval for §4.6 and §4.7
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open decisions pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ●. G4 n/a.

---

*`OP-015` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
