---
id: SC-011
title: Security Incident Response Plan
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, delegated to the Security Lead; personal-data breaches jointly with the Chief Data Officer
approver: Design Authority (constituted under GV-002), countersigned by Legal Counsel
standards_basis: >
  NIST SP 800-61 Rev. 3 (Incident Response Recommendations, April 2025 — CSF 2.0 Community Profile;
  supersedes r2) · ISO/IEC 27035-1/-2/-3 (incident management) · ISO/IEC 27001:2022 A.5.24–A.5.28 ·
  ISO/IEC 27037 / 27041 / 27043 (evidence and investigation) · PDPA 2026 NFR-094 ·
  Cyber Security Ordinance 2025 (CII incident obligations)
traces_to: >
  PGD-000 SC-011 · M29 §8.3 breach assessment state model, FR-SEC-035, NFR-072 · M60 FR-GRC-036 ·
  05-06 §6.3 NFR-094 · SC-001 §7.6 break-glass, §12 · SC-002 §11 · SC-008 §6 four clocks ·
  SC-010 §9 forensic readiness · OP-004, OP-013, OP-016 ·
  audit findings OP-04, OP-08, OP-09, OP-18, OP-20, LG-021 CS1/CS2/CS5
depends_on: SC-001 · SC-008 (notification obligations) · SC-010 (evidence) · GV-002 (bodies)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 15:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-011 — Security Incident Response Plan

### Category 05 · Code `SC` · NIST SP 800-61r3 · ISO/IEC 27035 · ISO/IEC 27001:2022 A.5.24–A.5.28

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-011`.
> 2. **`PG-03` Count, do not consult.** Readiness figures counted at **2026-08-18 15:25 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1. **NIST SP 800-61 r2 is superseded; r3 is used.**
> 4. **`PG-M4` Verify citations.** **No notification deadline is stated as fact in this document**
>    (`OP-18`, `NC-3`).

---

## 1. Purpose

This document is the **plan** behind the templates. `PGD-000` marks `SC-011` ◐ against `OP-004` and
`OP-016`, and the marking is exact: `OP-004` supplies **26 incident communication templates**,
`OP-016` supplies a **post-incident review template and register** — and `LG-021` §4.10.7 states
the position bluntly:

> **"Incident templates are `OP-004`; the template is not the process."**

Audit `C-04` found the underlying gap: **breach notification is absent, and no regulator is named
anywhere in the repository.** That has since been partly remediated — the National Data Management
Authority is now named in `05-06` §6.3 and `LG-024` — but **naming a regulator is not a
notification capability**.

What this document adds to the templates: detection sources, severity that determines behaviour,
the roles that act, containment decisions taken in advance rather than at 02:00, **the breach
assessment that decides whether a regulator must be told**, **four notification clocks that may run
simultaneously**, evidence handling, and the recovery and learning loop.

**Four audit findings say this plan cannot yet execute**, and they are stated at the front rather
than buried:

| Finding | Statement | Consequence for this plan |
|---|---|---|
| **`OP-08`** | **Break-glass is documented and does not exist** — no vault path, no sealed envelope, no safe procedure, no named holders, no test | **The compensating control for a single-IdP architecture is missing.** `SC-002` `TH-081` is Critical with no control |
| **`OP-09`** | **The on-call rota needs ten people and has none** — six platform engineers, four security responders | **There is nobody to page.** *"An unstaffed rota does not degrade gracefully — it degrades into two people, and then into one"* |
| **`OP-20`** | **No delegated authority for emergency spend during an incident** | The CTO is the only spend authority at 02:00 |
| **`OP-18`** | **The breach-notification clock is not law yet** | `OP-004` `RN-03` plans to **72 hours, explicitly marked a planning figure and not a legal statement** |

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **What counts as a security incident**, and the classes this estate actually faces |
| 2 | **Detection sources** — automated, human and external |
| 3 | **Severity `S1`…`S4`** with response times, and what each severity *changes* |
| 4 | **Roles** — incident commander, technical lead, communications, legal, DPO, scribe |
| 5 | **The lifecycle** — detect, triage, contain, eradicate, recover, learn |
| 6 | **Containment decisions pre-agreed**, including the ones that hurt |
| 7 | **The breach assessment** — the `NFR-094` decision, made against criteria |
| 8 | **Four notification clocks**, their owners, and the rule that none may be stated as fact |
| 9 | **Evidence handling** during response |
| 10 | **Break-glass operation** — the `OP-08` procedure |
| 11 | **Post-incident review and the learning loop** into `SC-002` and `SC-009` |
| 12 | **Readiness** — what must exist before this plan can run, stated as a gap list |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Communication copy and templates | `OP-004` | 26 templates; this supplies the process |
| Post-incident review template | `OP-016` | This supplies when, who and what feeds it |
| IT incident process generally | `M66`, `SP-031` | **A security incident *is* an incident**: `M66` runs the process, this document owns the security judgement (`M29` §3.2) |
| On-call rota mechanics | `OP-013` | Referenced; `OP-09` records it is unstaffed |
| Disaster recovery | `OP-012`, `PE-007` | A DR event is not an incident unless it has a security cause; §7.4 states the seam |
| Breach *notification to the Authority* as an act | **`M60`** (`NFR-094`) | `M29` detects and assesses; **`M60` notifies** |
| Threat identification | `SC-002` | — |
| Log specification | `SC-010` | This uses the evidence |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Incident commander** | §5 lifecycle, §6 containment, §8 clocks |
| **On-call responders** | §4 severity, §5, §6 — **the pages you act on** |
| **CDO / DPO** | §7 breach assessment, §8 clock (a) |
| **Legal Counsel** | §7, §8 — and `Q-01` |
| **CTO / Steering Committee** | §12 readiness gaps |
| **Enterprise clients and brand partners** | §8 clock (d); `LG-021` `CS5` |

---

## 2. Basis

### 2.1 Standards conformance

| Standard | How this document conforms | Departure |
|---|---|---|
| **NIST SP 800-61 Rev. 3** *(April 2025; **supersedes r2**; verified 2026-08-18)* | **r3's two-phase CSF 2.0 structure is adopted**: *preparation* (Govern, Identify, Protect) and *response* (Detect, Respond, Recover). §3 and §12 are preparation; §5–§9 are response | r3 treats incident response as part of **cybersecurity risk management** rather than a standalone playbook — which is why §11 feeds `SC-002` and `GV-005` rather than closing a ticket |
| **ISO/IEC 27035-1/-2/-3** | Plan and prepare, detect and report, assess and decide, respond, lessons learned | — |
| **ISO/IEC 27001:2022 A.5.24–A.5.28** | Planning and preparation, assessment and decision, response, learning, evidence collection | — |
| **ISO/IEC 27037, 27041, 27043** | Evidence handling during response — §9, with readiness in `SC-010` §9 | — |
| **PDPA 2026 `NFR-094`** | §7 breach assessment; §8 clock (a) | **The notification period is not prescribed** (`OP-18`). §8 `NC-3` |
| **Cyber Security Ordinance 2025** | §8 clock (b); §12 the CII readiness obligation | **CII status is undetermined** (`SC-008` `CR-16`) |

### 2.2 Source material

| Source | Supplies |
|---|---|
| `M29` §8.3 | **The breach-assessment state model** — Triaged → Contained → **Breach assessment** → Notifiable? → Remediated → Closed. **Adopted verbatim** in §5 |
| `M29` §10.1 | `fix.security.incident`, `fix.security.event` field sets |
| `M29` §5.7, `NFR-072` | Security event correlation and alerting; incident response with severity and containment |
| `M60` `FR-GRC-036` | **Breach register** with assessment, containment, notification decision and evidence |
| `LG-021` `IS-10` | The four clocks, the detection-start rule, and `CS1`, `CS2`, `CS5` |
| `OP-004` | 26 incident communication templates; `RN-03` 72-hour planning assumption |
| `OP-016` | Post-incident review template and register |
| `OP-013` | On-call and escalation; §4.8's **proposed** incident-spend limits (`AU-01`) |
| `SC-010` §9 | Forensic readiness — sources, chain of custody, competence |
| `SC-008` §6 | The four clocks, dated and owned |

### 2.3 Enumeration

| # | Figure | **Counted 2026-08-18 15:25 (+06)** |
|---|---|---:|
| 1 | Incident communication templates available | **26** (`OP-004`) |
| 2 | Post-incident review templates | **1** (`OP-016`) |
| 3 | **Named on-call responders** | **0** (`OP-09`) |
| 4 | **Break-glass credential holders named** | **0** (`OP-08`) |
| 5 | Break-glass tests performed | **0** |
| 6 | Tabletop exercises performed | **0** |
| 7 | Incident register entries | **0** |
| 8 | **Notification clocks that may run at once** | **4** |
| 9 | Clocks with a legally-stated deadline | **0** (`OP-18`) |
| 10 | Forensic specialist retainers arranged | **0** (`SC-010` `CP-3`) |

---

## 3. What Counts as an Incident

### 3.1 Definition

> **A security incident is an event, or a series of events, that compromises or credibly threatens
> the confidentiality, integrity or availability of information or of the system — or that breaches
> a security control, whether or not harm followed.**

The last clause matters. **A control that failed without consequence is still an incident**, because
the next occurrence may not be harmless, and `LG-021` §4.1.6 already establishes that an
unevidenced control is a deficiency.

### 3.2 Incident classes this estate actually faces

Derived from `SC-002` rather than from a generic list.

| # | Class | Example | `SC-002` |
|---|---|---|---|
| `IC-1` | **Unauthorised data access** | Cross-branch, cross-tenant or cross-party read | `TH-021`, `TH-049`…`TH-051` |
| `IC-2` | **Residency violation** | A residency-classified value found in `Z3`, a cache, an index, a log or a backup | `TH-047`, `TH-048` |
| `IC-3` | **Account compromise** | Credential stuffing, session theft, seller takeover | `TH-001`…`TH-014` |
| `IC-4` | **Privilege abuse or escalation** | Standing rights, self-approval, delegation-acquired SoD | `TH-076`…`TH-083` |
| `IC-5` | **Data exfiltration** | Bulk export, unlisted egress destination | `TH-044`, `TH-058` |
| `IC-6` | **Integrity compromise** | Audit chain break, tampered backup, unauthorised deployment | `TH-031`…`TH-033`, `TH-075` |
| `IC-7` | **Supply-chain compromise** | Malicious dependency, poisoned image | `TH-094`, `A03:2025` |
| `IC-8` | **`M06` custody incident** | Recovered customer data accessed outside its case, or unpurged past its date | `TH-084` |
| `IC-9` | **`Z7` third-party incident** | A remote-support identity used to reach a client estate | `TH-069` |
| `IC-10` | **Availability attack** | DDoS, application-layer DoS, lockout abuse | `TH-063`…`TH-074` |
| `IC-11` | **Ransomware** | Encryption of `DS-02`/`DS-06` and reachable backups | `TH-074`, `AB-31` |
| `IC-12` | **Insider incident** | `AB-09`…`AB-16` | §8.2 |

> **`IC-2` is unusual and easy to miss.** A residency violation may involve **no attacker, no
> unauthorised access and no data loss** — an engineer added a cache. **It is still an incident,
> because it is a potential statutory breach**, and treating it as a defect ticket would mean the
> assessment in §7 never runs.

### 3.3 Detection sources

| Source | Feeds | Reliability |
|---|---|---|
| **Hash-chain verification job** | `IC-6` | ✔ Highest-value automated detection (`SC-010` `MO-1`) |
| **Authorisation-denial spike** | `IC-1`, `IC-3` | ✔ (`MO-2`) |
| **Bulk-export anomaly** | `IC-5`, `IC-12` | ✔ (`MO-3`) |
| **`T5` access without a work item** | `IC-1`, `IC-12` | ✔ (`MO-4`) |
| **Break-glass use** | `IC-4` | ✔ Independent path (`BG-A2`) |
| **`Z4` access outside `CD-233`** | `IC-2` | ✔ Should be impossible (`SEC-ZR-2`) |
| **Unlisted egress attempt** | `IC-5` | ✔ (`SEC-ZR-1`) |
| Vulnerability scanning and pen-test | `IC-7`, all | ✔ `SC-009` |
| **Human report from staff** | all | ✔ **`LG-020` `AU-17`: a User must report a suspected incident immediately, and reporting one is never penalised** |
| **Customer or client report** | all | ✔ |
| **External researcher** | all | ✔ `SC-009` §10 responsible disclosure |
| **Regulator, CIRT or third-party notification** | all | ✔ |
| Cross-source behavioural correlation | all | ✖ **No SIEM** (`MO-9`) |

---

## 4. Severity

### 4.1 The scale

Severity determines **behaviour**, not priority order. Each level changes who is woken, what may be
done without approval, and who is told.

| Sev | Definition | Response start | Incident commander | Notify |
|---|---|---|---|---|
| **`S1`** | Confirmed or highly likely compromise of **personal data at scale**, of `Z4`, of `Z7` into a client estate, of the audit trail's integrity, or **estate-wide unavailability** | **Immediate, 24×7** | **CTO or delegate** | CEO, CDO, Legal, Steering Committee **at declaration** |
| **`S2`** | Confirmed compromise of a **single tenant, branch, party or system**; privilege abuse; exfiltration of a bounded dataset; a control failure with statutory implications | **≤ 1 hour, 24×7** | Security Lead | CTO, CDO if personal data |
| **`S3`** | Control failure with **no evidence of exploitation**; a residency violation with no external exposure; a contained account compromise | ≤ 4 hours, business hours | On-call responder | Security Lead |
| **`S4`** | Minor policy breach, near miss, or a suspicious event requiring investigation | ≤ 1 working day | On-call responder | Logged |

| # | Rule |
|---|---|
| `SV-1` | **Severity is assigned on the credible worst case at the time**, and revised as facts arrive. **Under-calling to avoid waking people is the failure mode this rule exists to prevent** |
| `SV-2` | **A residency violation is `S3` minimum**, and `S1` if data left the country — because §7's assessment must run |
| `SV-3` | **Any `Z7` incident is `S1` minimum** — the affected party is a third-party organisation, not 1000FiX |
| `SV-4` | **An audit-chain break is `S1` minimum** — the integrity of every other investigation depends on it |
| `SV-5` | **Severity may be raised by anyone; lowering requires the incident commander** and is recorded with reasons |
| `SV-6` | `M66` platform incident severity and this scale are **reconciled**, closing `AUDIT-017` `OP-04` (*"platform incident severity had three claimed owners and no owner"*): **`M66` owns the process and the operational severity; this document owns the security severity, and the higher of the two governs** |

### 4.2 Roles

| Role | Responsibility | Named today |
|---|---|---|
| **Incident commander** | Owns the incident. Decides containment. **Not the person doing the technical work** | ✖ Role defined; **no rota** (`OP-09`) |
| **Technical lead** | Investigation and remediation | ✖ |
| **Communications lead** | Internal and external messaging using `OP-004` | ✖ |
| **Legal Counsel** | Notification obligations, privilege, regulator contact | ✖ Unnamed |
| **CDO / DPO** | **Owns the §7 breach assessment** and clock (a) | ✖ **Unappointed** (`NFR-096`) |
| **Scribe** | Contemporaneous timeline — **the single most-skipped and most-valuable role** | ✖ |
| **Executive sponsor** | `S1` only: external and board communication, spend authority | CTO |

> **`SC-011-F-01`. The incident commander must not be the person fixing the problem.** Under `S1`
> conditions the technical lead is deep in a system; the commander is tracking clocks, evidence,
> containment consequences and four notification obligations. **One person cannot do both, and the
> failure mode is that the clocks are noticed after they expire.** At the current staffing —
> **`OP-09`: zero named responders** — this separation is unachievable, which is §12's first gap.

---

## 5. The Lifecycle

**Adopted from `M29` §8.3 verbatim**, with the operational content this document adds.

```
   Detection: anomaly · alert · vulnerability · staff report · client report ·
              researcher · regulator or third-party notice
        │
   ┌────▼─────┐
   │ TRIAGED  │  severity assigned (S1–S4); INCIDENT COMMANDER NAMED;
   └────┬─────┘  scribe started; clocks §8 START AT DETECTION
        │
   ┌────▼──────────┐
   │  CONTAINED    │  access revoked · sessions killed · systems isolated
   └────┬──────────┘  §6 pre-agreed decisions; EVIDENCE PRESERVED FIRST (§9)
        │
   ┌────▼──────────────────────┐
   │ ★ BREACH ASSESSMENT       │  Is personal data involved?
   │   (NFR-094) — §7          │  Is significant damage likely?
   └────┬──────────────┬───────┘  DECISION AND REASONING RECORDED EITHER WAY
        │ no           │ yes
        │         ┌────▼──────────────────────────┐
        │         │ NOTIFIABLE                    │
        │         │ ──► M60 notifies the Authority│  clock (a)
        │         │ ──► NCSA if CII               │  clock (b)
        │         │ ──► data subjects informed    │  clock (c)
        │         │ ──► clients/brands/insurers   │  clock (d)
        │         └────┬──────────────────────────┘
        │              │
   ┌────▼──────────────▼───┐
   │      REMEDIATED       │  root cause fixed; control added; RETEST PASSED
   └────┬──────────────────┘
        │
   ┌────▼──────┐
   │  CLOSED   │  post-incident review (OP-016); M23 CAPA where systemic;
   └───────────┘  M66 records the incident process; SC-002 RM-05 update
```

| Phase | Additions this document makes |
|---|---|
| **Detect** | §3.3 sources; **the clock starts here** (`NC-1`) |
| **Triage** | Severity `SV-1`…`SV-6`; commander named; **scribe started**; register entry opened |
| **Contain** | §6 pre-agreed decisions; **`EV-1`: preserve before you contain** |
| **Assess** | §7 — **runs on every incident touching personal data, and the decision not to notify is recorded** (`NC-2`) |
| **Eradicate** | Root cause, not symptom. `RV.3` root-cause record (`SC-005` §4) |
| **Recover** | §7.4 seam with DR; **verified restoration, not assumed** |
| **Learn** | §11 — feeds `SC-002` `RM-05`, `SC-009` `RC-4`, `M23` CAPA, `GV-005` |

---

## 6. Containment — Decisions Taken in Advance

> **Containment decisions are business decisions with technical execution, and they are made badly
> at 02:00 by whoever is awake.** Each is pre-authorised here, with its cost stated, so the
> responder acts rather than escalates.

| # | Action | Pre-authorised at | Cost | Notes |
|---|---|---|---|---|
| `CT-1` | **Revoke a user's sessions and credentials** | On-call responder, any severity | One user disrupted | ≤ 60 s propagation (`BRU-SEC-25`) |
| `CT-2` | **Revoke an external party's or API consumer's credentials** | On-call responder | One party's integration stops | `EA-11` scope is per-credential |
| `CT-3` | **Block an egress destination** | On-call responder | One integration stops; **`SU-3` degraded mode applies** | `SEC-ZR-1` |
| `CT-4` | **Disable a portal surface** | **Security Lead** | That population loses service | 12 surfaces; `P01` is 250,000+/month |
| `CT-5` | **Terminate all `Z7` remote sessions** | On-call responder | Managed-services support stops | **`SV-3`: `Z7` is `S1` minimum** |
| `CT-6` | **Isolate a `Z2` workload** | Security Lead | Capacity reduced | mTLS identity revocation |
| `CT-7` | **Suspend the residency service `CD-233`** | **CTO** | **All `S3` reads fail estate-wide** — `M06`, KYC, biometric, NID verification stop. `DG-1`…`DG-6` degraded mode | Highest-cost containment available |
| `CT-8` | **Block a deployment pipeline** | Security Lead | No releases | `IC-7` supply chain |
| `CT-9` | **Force estate-wide credential reset** | **CTO** | 800+ staff and up to 5,000 external users re-authenticate | `IC-3` at scale |
| `CT-10` | **Disconnect from a client estate** (`Z7`) | Security Lead, **with client notification** | That client loses managed support | `IC-9`; `LG-021` `CS5` |
| `CT-11` | **Take the estate offline** | **CEO or CTO** | 51+ branches on `OP-014` manual fallback | Last resort; `IC-11` ransomware |

| # | Rule |
|---|---|
| `CN-1` | **Preserve evidence before containing** (`EV-1`) — containment frequently destroys the evidence of what happened |
| `CN-2` | **A containment action is logged with its authoriser and its reason** |
| `CN-3` | **Containment that stops a `05-03` §7 P0 integration triggers the declared fallback**, not an improvisation |
| `CN-4` | **`CT-7` and `CT-11` are announced to the Steering Committee at the moment they are taken**, not afterwards |

---

## 7. The Breach Assessment

**The `NFR-094` decision.** `M29` §8.3 places it in the lifecycle; this is how it is made.

### 7.1 The two questions

| # | Question | If unclear |
|---|---|---|
| `BA-1` | **Is personal data involved?** | **Assume yes** until established otherwise. Most systems in this estate touch personal data |
| `BA-2` | **Is significant damage to data subjects likely?** | **`Q-01`: the threshold is not defined in the estate.** Until Legal sets it, §7.2's criteria apply as a stated working basis |

### 7.2 Criteria for `BA-2` — a working basis pending `Q-01`

Assessed on **harm to the individual** (`SC-003` §2.2), not loss to the company.

| Factor | Raises the likelihood of significant damage |
|---|---|
| **Category** | **NID, passport, TIN, biometric, criminal record, recovered customer data, KYC** — the `NFR-099` categories. **A biometric template is irreversible** |
| **Volume** | Many subjects, or few subjects with high-sensitivity data |
| **Identifiability** | Directly identified, vs pseudonymised, vs aggregated |
| **Recipient** | Unknown or hostile, vs a known party under obligation |
| **Reversibility** | Can the harm be undone? **A leaked NID cannot be reissued easily; a fingerprint cannot at all** |
| **Vulnerability of subjects** | `DS-3` employees, `DS-6` recovery customers, minors |
| **Consequence** | Identity fraud, financial loss, discrimination, employment consequence, physical risk |

| # | Rule |
|---|---|
| `BA-3` | **Any incident involving an `NFR-099` category is presumed notifiable** unless the assessment establishes otherwise. The conservative reading, stated as such (`SC-008` `SC-008-D-04`) |
| `BA-4` | **A decision not to notify is recorded with its reasoning** (`LG-021` §4.10.3) — this is the record a regulator asks for, and its absence is worse than a late notification |
| `BA-5` | **The CDO owns the assessment; `M60` performs the notification** (`NFR-094`). **`M29` detects and assesses; `M60` notifies.** The separation is deliberate |
| `BA-6` | **`M60` `FR-GRC-036` breach register records assessment, containment, notification decision and evidence** — including **contractual notifications where statute is silent** |
| `BA-7` | **A `M06` case breach is assessed and notified where the threshold is met** (`BRU-DTS-17`) — and `DS-6` is the most exposed population in the estate |

### 7.3 Residency violations

| # | Rule |
|---|---|
| `RV-1` | **A residency violation is assessed under §7 even with no unauthorised access**, because unlawful processing is itself the harm |
| `RV-2` | Where a residency-classified value **left Bangladesh**, the assessment addresses `NFR-086b` **and** `NFR-099`, and Legal considers whether a transfer notification is separately owed |
| `RV-3` | **Remediation is deletion of the copy plus evidence of deletion** — and where the copy was in a backup or an immutable store, that evidence is harder than it sounds. §12 `Q-04` |

### 7.4 The seam with disaster recovery

| Situation | Owner |
|---|---|
| Availability loss with **no security cause** | `OP-012` DR; **not** an incident under this plan |
| Availability loss with a security cause (`IC-10`, `IC-11`) | **This plan**, with DR executing recovery |
| **DR executed in a way that creates a compliance event** — e.g. a `Z4` cross-border restore | **This plan.** `SC-007` §9; `TH-055` |
| Ransomware | **This plan**, with DR recovery and `SEC-DR-04` immutable backup — **which does not exist** (`OP-02`) |

---

## 8. The Four Notification Clocks

Dated and owned in `SC-008` §6; operationalised here. **They may run simultaneously and they are
different.**

| Clock | Trigger | Owner | Deadline | State |
|---|---|---|---|---|
| **(a) National Data Management Authority** | Breach likely to cause **significant damage** | **CDO**, via `M60` | **Prescribed by regulations not yet published** | ⚠ `OP-004` `RN-03` plans to **72 hours as an explicit planning assumption**, not a legal statement |
| **(b) National cyber-security structure / NCSA** | A cyber incident, **if 1000FiX is CII** | **CTO** | Per `ST-03` and its rules | ✖ **CII status undetermined** (`SC-008` `CR-16`) |
| **(c) Affected data subjects** | Where the risk to them requires it | CDO | Per statute; `LG-008` §4.8 | ◐ |
| **(d) Clients, brand partners, insurers** | Per contract | Legal | Per instrument — **frequently shorter than statute** | ◐ `LG-004` §4.7.5, `LG-005` §6.6, `LG-006` §6.5, `LG-007` §6.4 all impose it |

| # | Rule |
|---|---|
| `NC-1` | **The clock starts at detection**, not at confirmation, not at containment (`LG-021` §4.10.3) |
| `NC-2` | **A decision not to notify is recorded with its reasoning** |
| `NC-3` | **No document may state a notification deadline as fact until the period is prescribed** (`OP-18`). `OP-004` `RN-03`'s 72 hours is a **planning figure to be replaced, not inherited** |
| `NC-4` | **Operational readiness is planned to the shortest applicable clock.** Contractual (d) is frequently shorter than statutory (a), and planning to statute alone breaches the contract |
| `NC-5` | **A vulnerability affecting a client is disclosed to that client** — `LG-021` `CS5` |
| `NC-6` | **All four clocks are tracked on the incident record**, visibly, from triage. The commander does not hold them in their head |

> **`SC-011-F-02`. `NC-4` is the rule most likely to be missed and most likely to bite.** A team
> planning to a 72-hour statutory assumption will comfortably breach a 24-hour contractual
> obligation to a brand partner — and the contractual breach has an immediate commercial
> consequence, where the statutory one has a regulatory process behind it. **Legal must extract the
> shortest contractual clock from `LG-004`…`LG-007` and publish it.** `Q-02`.

---

## 9. Evidence During Response

Readiness is `SC-010` §9. This is conduct **during** an incident.

| # | Rule |
|---|---|
| `EV-1` | **Preserve before you contain.** Volatile state, sessions, memory and logs are destroyed by the actions that stop the bleeding. Where the two conflict, **containment wins for `S1` — and the decision is recorded** |
| `EV-2` | **Acquisition follows `SC-010` §9.3 chain of custody**: what, when, by whom, from where, under what authority, with a hash |
| `EV-3` | **Analysis is on a copy** (`CC-4`) |
| `EV-4` | **A legal hold is instructed immediately** for material in scope (`FR-GRC-039`, `BRU-SEC-23`) — before retention could expire |
| `EV-5` | **`Z4` evidence is collected, analysed and stored in-country** — otherwise the investigation is itself a transfer (`SC-010` `FR-7`) |
| `EV-6` | **The scribe's timeline is evidence.** Contemporaneous, timestamped, retained |
| `EV-7` | **Acquisition is not performed by a person implicated** (`CP-2`) |
| `EV-8` | Where in-house competence is insufficient, the **pre-arranged specialist** is engaged — **and there is none** (`SC-010` `CP-3`, §12) |

---

## 10. Break-Glass — Operating the `OP-08` Control

`SC-001` §7.6 specifies the architecture (`BG-A1`…`BG-A5`). This is the procedure. **`OP-08`
records that none of it exists**, and `SC-002` `TH-081` rates the consequence Critical.

### 10.1 When it is used

| # | Trigger |
|---|---|
| `BG-U1` | Identity provider unavailable and administrative access is required to recover (`TH-081`) |
| `BG-U2` | Every privileged path is compromised or unavailable |
| `BG-U3` | A `Z5`→`Z4` read is genuinely required and §5.5's denial blocks it |
| `BG-U4` | Vault unseal is required (`SC-006` `VA-2`) |

### 10.2 The procedure

| # | Step |
|---|---|
| `BG-P1` | **Two named signatories** retrieve the sealed credential from the head-office safe; a second sealed copy is held off-site |
| `BG-P2` | **Use triggers immediate multi-party notification over a path independent of the systems being recovered** (`BG-A2`) — this is automatic, not a courtesy |
| `BG-P3` | **The grant is time-boxed with automatic expiry** (`BG-A3`). No manual revocation step, because a forgotten revocation is the normal failure |
| `BG-P4` | **Session recording is mandatory; a recording failure terminates the session** (`BG-A4`) |
| `BG-P5` | **Post-hoc justification is mandatory** within one working day; its absence is a control failure |
| `BG-P6` | **Credentials rotate on use** (`BG-A5`, `BG-11`), and the envelope is re-sealed |
| `BG-P7` | **Every use opens an incident record**, minimum `S3`, regardless of outcome |

### 10.3 Readiness

| # | Requirement | State |
|---|---|---|
| `BG-R1` | Vault break-glass path exists | ✖ |
| `BG-R2` | Sealed offline credential envelope, head-office safe | ✖ |
| `BG-R3` | Second sealed copy, off-site | ✖ |
| `BG-R4` | **Two named signatories** | ✖ |
| `BG-R5` | **Quarterly test** (`BG-10`) | ✖ |
| `BG-R6` | Independent notification path | ✖ |

> **`SC-011-F-03`. Six of six break-glass readiness items are absent, and `OP-08` observes that it
> is *"days of work, not months, and the cheapest high-severity item in this report."*** It is also
> the compensating control for a deliberate architectural concentration: **every portal depends on
> one identity provider by design**. Without it, an identity outage means administrative recovery is
> improvised under `S1` conditions — *which is precisely the circumstance in which improvised
> privileged access becomes an unattributable production change*. **W1 go-live blocker.**

---

## 11. Post-Incident Review and the Learning Loop

`OP-016` supplies the template and the register. This supplies when, who and where the output goes.

| # | Rule |
|---|---|
| `PI-1` | **Mandatory for every `S1` and `S2`**, and for any `S3` with a systemic cause. Held **within 10 working days** |
| `PI-2` | **Blameless.** `LG-020` `AU-17` already guarantees that reporting an incident is never penalised; a review that punishes destroys reporting |
| `PI-3` | Attended by the commander, technical lead, CDO where personal data was involved, and **a person not involved in the response** |
| `PI-4` | **Outputs are actions with owners and dates**, not observations |

**Where the output goes — r3's point that incident response is part of risk management, not a
closed ticket:**

| Output | Destination |
|---|---|
| A realised threat not in the model | **`SC-002` `RM-05`** — add it; re-rate its class |
| A vulnerability with no matching threat | **`SC-009` `RC-4`** and `SC-002` `RM-06` |
| A control that failed | **`SC-001` §9** control revision; `M60` deficiency with **retest before closure** (`BRU-GRC-08`) |
| A systemic cause | **`M23` CAPA** |
| A residual risk | **`GV-005`** |
| A gate that would have caught it | **`SC-005` §5** |
| An abuse case not tested | **`SC-005` `AT-7`** — added within the remediation, not after |
| A detection that did not fire | **`SC-010` §12** |
| A wave-gate evidence item | **`GV-009`** |

| # | Rule |
|---|---|
| `PI-5` | **`M23` CAPA where systemic** (`M29` §8.3) |
| `PI-6` | **`M66` records the incident process**; this document owns the security judgement |
| `PI-7` | **An incident closed with no learning output is challenged**, not accepted. Every incident teaches something or the review was not held properly |

---

## 12. Readiness — What Must Exist Before This Plan Can Run

> A plan whose preconditions are absent is a document. **NIST SP 800-61r3's first phase is
> preparation, and this is that phase assessed honestly.**

| # | Requirement | State | Owner | Needed by |
|---|---|---|---|---|
| `RD-1` | **A staffed on-call rota** — 6 platform engineers + 4 security responders | ✖ **Zero named** (`OP-09`) | CTO with HR | **W1 go-live** |
| `RD-2` | **On-call allowance and time-in-lieu agreed with HR** | ✖ (`OP-013` `OI-03`) | HR Director | W1 |
| `RD-3` | **Break-glass — all six items** | ✖ (`OP-08`) | CTO with Security Lead | **W1 go-live** |
| `RD-4` | **An emergency-spend delegation** | ✖ `OP-013` §4.8 **proposes** BDT 25,000 on-call / 100,000 platform lead / CTO above, marked `AU-01`. `SP-004` has no such delegation (`OP-20`) | **CFO** | W1 |
| `RD-5` | **A named CDO** for clock (a) and §7 | ✖ (`NFR-096`) | Board | **Now** |
| `RD-6` | **A named Security Lead** | ✖ | CTO | W1 |
| `RD-7` | **The `BA-2` significant-damage threshold** | ✖ | Legal | W2 |
| `RD-8` | **The shortest contractual notification clock, extracted and published** | ✖ | Legal | W2 |
| `RD-9` | **CII determination** for clock (b) | ✖ (`CR-16`) | Legal | W2 |
| `RD-10` | **A forensic specialist retainer** | ✖ (`SC-010` `CP-3`) | CTO | W2 |
| `RD-11` | **An immutable backup outside the provider account** for `IC-11` | ✖ (`OP-02`) | CTO | W2 |
| `RD-12` | **A lawful `Z4` recovery path** | ✖ (`OP-01`) | CTO with Legal | W2 |
| `RD-13` | **Tabletop exercises** — at least one before each wave gate | ✖ Zero held | Security Lead | W1 |
| `RD-14` | **The incident register** (`M60` `FR-GRC-036`) | ✖ Not built | `M60` | W2 |
| `RD-15` | **Detection: the eight achievable queries** (`SC-010` §12) | ✖ Not built | Platform Squad | W2 |

**15 readiness items. 15 absent.**

> **`SC-011-F-04`. This is the honest position and it is not a criticism of the estate — nothing is
> built.** But four of the fifteen are **organisational, cheap and independent of the build**:
> `RD-3` break-glass (*days of work*), `RD-4` spend delegation (a CFO signature), `RD-5` the CDO
> appointment, and `RD-8` extracting the shortest contractual clock. **They can be closed before a
> single line of code is written, and they are the four that hurt most at 02:00.** Escalated to
> `GV-005` and to the Steering Committee.

---

## 13. Exercises

| # | Exercise | Cadence | Scope |
|---|---|---|---|
| `EX-1` | **Break-glass test** | **Quarterly** (`BG-10`) | Retrieve, use, rotate, re-seal |
| `EX-2` | **Tabletop** | **Before each wave gate** | A scenario from `SC-002` §12 attack trees |
| `EX-3` | **Notification rehearsal** | Annually | All four clocks; who calls whom; the `OP-004` template used |
| `EX-4` | **Evidence acquisition drill** | Annually | `SC-010` §9.3 chain of custody end to end |
| `EX-5` | **`Z4` degraded-mode exercise** | **Before W2** | `SC-007` §9.2 `DG-1`…`DG-6` — **the mode currently relied on and never tested** |
| `EX-6` | **DR failover drill** | Twice yearly (`NFR-051`) | Both tiers and the residency service (`AR-001` `DR-03`) |

**Suggested first tabletop, at W1:** `SC-002` §12.1 path `B` — *a residency-classified value is
found in a regional cache*. It exercises `IC-2`, `SV-2`, §7.3, clock (a), and `RV-3`'s deletion
evidence, and **it is the scenario most likely to actually occur**, because it needs no attacker.

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **What constitutes "significant damage"**, and what is the prescribed notification period? (`PN3`, `OP-18`) | Legal Counsel | **W2** | §7.2; clock (a); `RD-7` |
| `Q-02` | **What is the shortest contractual notification clock** across `LG-004`…`LG-007`? | Legal | W2 | `NC-4`; `RD-8` |
| `Q-03` | **Is 1000FiX CII?** | Legal | W2 | Clock (b); `RD-9` |
| `Q-04` | How is deletion of a residency-violating copy **evidenced** where it reached an immutable store? | CDO with Platform Eng | W2 | `RV-3` |
| `Q-05` | Who are the two break-glass signatories, and where is the safe? | CTO | **W1** | `RD-3`; shares `SC-006` `ES-2` |
| `Q-06` | Is the `OP-013` §4.8 spend proposal ratified? | CFO | W1 | `RD-4` |
| `Q-07` | Who is the incident commander at 02:00 on a Friday? | CTO with HR | **W1** | `RD-1`; `SC-011-F-01` |

---

## 15. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-011-D-01` | Standard | 800-61r2 · **r3** · ISO 27035 only | **r3 + 27035** | r2 is superseded; **r3's framing of IR as part of risk management** is why §11 feeds `SC-002` and `GV-005` | Two-phase structure; preparation is §3/§12 |
| `SC-011-D-02` | Severity | Reuse `M66` operational severity · **A security scale reconciled with it** | **Security scale; higher of the two governs** | An availability scale cannot express *"one record read by the wrong branch"*, which may be `S2` | `SV-6` closes `OP-04` |
| `SC-011-D-03` | Residency violations | Defect ticket · **Incident, `S3` minimum** | **Incident** | Unlawful processing is the harm; a defect ticket never runs §7 | `SV-2`; more incidents recorded, correctly |
| `SC-011-D-04` | Containment authority | Escalate each time · **Pre-authorise with stated cost** | **Pre-authorise** | Containment decisions are made badly at 02:00 by whoever is awake | §6 — 11 actions, 4 authority levels |
| `SC-011-D-05` | Evidence vs containment | Always preserve first · **Preserve first, containment wins at `S1`, decision recorded** | **Middle** | An absolute preserve-first rule loses data during an active exfiltration | `EV-1` |
| `SC-011-D-06` | Notification planning basis | 72 h · **Shortest applicable clock** | **Shortest** | Contractual (d) is frequently shorter than statutory (a) | `NC-4`; `Q-02` must be answered |
| `SC-011-D-07` | Publish the readiness gaps? | Omit · **Publish 15 of 15 absent** | **Publish** | A plan whose preconditions are hidden reads as a capability | §12; four are closeable now |

---

## 16. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Incident classes derive from the threat model, not a generic list | §3.2 — 12 classes, each traced |
| `AC-02` | Severity changes behaviour, not just priority | §4.1 |
| `AC-03` | Roles are defined, and the commander is separated from the technical lead | §4.2; `SC-011-F-01` |
| `AC-04` | The `M29` §8.3 state model is adopted, not replaced | §5 |
| `AC-05` | Containment decisions are pre-authorised with stated cost | §6 — 11 actions |
| `AC-06` | The breach assessment has criteria and records a negative decision | §7.2, `BA-4` |
| `AC-07` | All four clocks are owned, and none is stated as fact | §8; `NC-3` |
| `AC-08` | Evidence conduct is specified for response, not only readiness | §9 |
| `AC-09` | Break-glass has a procedure and its readiness state is published | §10 — 6 of 6 absent |
| `AC-10` | The learning loop names nine destinations | §11 |
| `AC-11` | **Readiness gaps are published, with those closeable now identified** | §12 — 15 of 15; 4 closeable |
| `AC-12` | Exercises are scheduled, including a first scenario | §13 |

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` §7.6, §12 | Break-glass architecture; failure model |
| Upstream | `SC-002` | Incident classes; tabletop scenarios |
| Upstream | `SC-008` §6 | The four clocks |
| Upstream | `SC-010` §9, §12 | Forensic readiness; detections |
| Downstream | `SC-002` `RM-05` | Realised threats update the model |
| Downstream | `SC-009` `RC-4` | Findings without a threat |
| Downstream | `M60` `FR-GRC-036` | Breach register; **`M60` notifies** |
| Downstream | `M23` | CAPA where systemic |
| Downstream | `M66` | The ITSM process this runs inside |
| Downstream | `GV-005`, `GV-009` | Readiness risks; gate evidence |
| Lateral | `../../project_content/17_Operations_Support_and_Runbooks/OP-004_*.md` | 26 templates — **the templates this plan sits behind** |
| Lateral | `../../project_content/17_Operations_Support_and_Runbooks/OP-013_*.md`, `OP-016_*.md` | On-call; post-incident review |

---

## 18. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-002`, `./SC-003`, `./SC-007`, `./SC-008`, `./SC-009`, `./SC-010` ·
`../00_Programme_Governance_and_Control/GV-002_*.md`, `GV-005_*.md`, `GV-009_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` §8.3, §10.1 ·
`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §6.3 ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md` `IS-10`, `LG-020_*.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-004_*.md`, `OP-012_*.md`, `OP-013_*.md`, `OP-016_*.md` ·
`../../project_content/_AUDIT/AUDIT-017_*.md` (`OP-04`, `OP-08`, `OP-09`, `OP-18`, `OP-20`)

**External standards** *(all verified 2026-08-18; registered in `SC-008` §4.2)*

| Source | Version / status | Used for |
|---|---|---|
| **NIST SP 800-61** | **Rev. 3, April 2025 — CSF 2.0 Community Profile. Supersedes r2** | Two-phase structure; IR as risk management |
| ISO/IEC 27035-1/-2/-3 | Current | Incident management process |
| ISO/IEC 27001 | :2022 + Amd 1:2024 — A.5.24–A.5.28 | Obligation |
| ISO/IEC 27037, 27041, 27043 | Current | Evidence and investigation |
| **PDPA 2026** `NFR-094` | **Notification period left to regulations not yet published** | Clock (a) |
| **Cyber Security Ordinance 2025** | In force; CII obligations incl. own CERT/CIRT and SOC | Clock (b) |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Supplies the plan behind `OP-004`'s 26 templates: 12 incident classes derived from `SC-002`, a security severity scale reconciled with `M66` (**closing `OP-04`**), 11 pre-authorised containment decisions, the `NFR-094` breach assessment with criteria, four clocks none of which is stated as fact, the `OP-08` break-glass procedure, and a **published readiness list of 15 items, 15 absent, 4 closeable before any code is written** | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-011` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
