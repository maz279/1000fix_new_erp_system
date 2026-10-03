---
id: OP-011
title: Runbook — Portal and Mobile App Operations
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Mobile Engineering
author: Mobile Engineering with Platform Engineering and Content Design
reviewers: [Chief Technology Officer, Operations Director, Support Lead, QA Lead, Field Operations Manager, Contact Centre Supervisor, Marketplace Ops]
approver: Chief Technology Officer
content_class: C
purpose: >
  The release-channel, staged-rollout, forced-upgrade, store-submission, rollback and offline-sync
  procedures for six portals and four mobile applications. A bad forced upgrade can take 200–400
  technicians offline mid-shift, and a store review queue means the fix is not in the company's
  hands — both facts have to be operated deliberately rather than discovered.
traces_to: [P01, P02, P07, P09, P11, 02-05 §5.4, 05-06 NFR-017, NFR-018, NFR-036, NFR-037, NFR-047, NFR-081, NFR-082, DI-04, OP-005, OP-006, OP-013, OP-014, TS-015, NT-021]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §5.4 — Flutter applications (P02 technician, P09 rider, P11 auditor, P01 customer); Next.js 15 + React 19 portals (P01, P04, P07, P08, P10, P12)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-017 Android 11+ with 3 GB RAM; NFR-018 offline with automatic sync; NFR-036 job list ≤ 8 s cold on 3G; NFR-037 sync ≤ 30 s after 24 h offline; NFR-047 24-hour offline operation; NFR-081 ≤ 400 KB first load; NFR-082 ≤ 12% battery per 8-hour shift; DI-04 offline sync guarantees zero data loss and zero double-application
    verified: 2026-08-20
    class: P1
  - source: project_content/13_Test_and_Acceptance_Content/TS-015_Offline_and_Field_Condition_Test_Scripts.md — offline and field-condition scenarios and conflict cases
    verified: 2026-08-20
    class: P1
  - source: Google Play Console — staged rollout from 1%, halting a rollout stops further distribution but users who received the version keep it. https://support.google.com/googleplay/android-developer/answer/6346149
    verified: 2026-08-20
    class: P2
  - source: Android release practice — progressive 1% → 10% → 50% → 100% rollout; halt if crash rate exceeds a threshold (commonly 0.5% of sessions); force-upgrade reserved for security, data-loss or regulatory issues. https://proandroiddev.com/ready-aim-release-android-app-rollout-tips-1bc6f851e6fb
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# Runbook — Portal and Mobile App Operations

> **The mobile estate is the only part of this system that the company cannot fix instantly.** A
> server bug is fixed in minutes; a bad app build is fixed at the speed of a store review and a
> user tapping "update" — on a 3G connection, mid-shift, on a 3 GB device.
>
> Everything in this runbook exists to keep that gap small and survivable.
>
> **Verification status.** Authored at W0/W1 against applications delivered from W2. Indicative
> until G3 verification.

| Item | Value |
|---|---|
| System | 4 Flutter applications (`P02` technician, `P09` rider, `P11` auditor, `P01` customer) and 6 Next.js portals (`P01` web, `P04`, `P07`, `P08`, `P10`, `P12`) |
| Owner team | Mobile Engineering (apps), Platform Engineering (portal hosting) |
| Criticality | **P0 for `P02`** — 200–400 technicians cannot work without it; P1 for the rest |
| Availability target | `NFR-046` customer portal ≥ 99.9% · `NFR-047` 24-hour offline operation · `NFR-036` ≤ 8 s cold job list on 3G |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) |
| Escalation path | On-call → Mobile lead → CTO; **Field Operations Manager in parallel** for any `P02` incident, because the mitigation is operational, not technical |

---

## 1. What This System Does

The portals and applications are where every population actually meets the ERP. The Flutter apps
additionally hold **local state that exists nowhere else until it syncs** — a completed job, a
signature, a photograph, a part consumed, a payment collected in the field. `NFR-047` guarantees 24
hours of offline operation and `DI-04` guarantees zero data loss and zero double-application on
sync.

**If a portal stops:** that population falls back to another channel ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md)).
**If an app stops or is upgraded badly:** the work continues on paper, but the local data on those
devices is at risk, and that is the difference between an inconvenience and an incident.

---

## 2. Architecture Summary

| Component | Purpose | Depends on |
|---|---|---|
| **Flutter apps** (`P02`, `P09`, `P11`, `P01`) | Offline-first field and customer applications | Local store, sync engine, identity ([`OP-009`](OP-009_Runbook_Identity_and_Access.md)), gateway ([`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md)) |
| **Local store** | Encrypted on-device database holding queued work | Device storage |
| **Sync engine** | Bidirectional, idempotent, conflict-aware synchronisation (`DI-04`) | Connectivity, gateway, server-side reconciliation |
| **Next.js 15 portals** | Server-rendered web surfaces for six populations | Portal platform, gateway, CDN |
| **Portal platform** (Payload CMS 3, `CON-03`) | Content and portal hosting — **cannot be replaced** (`05-03` §3) | Its own operational contract |
| **Distribution** — Google Play, Apple App Store | Store review, staged rollout, halt | The stores' own timelines |
| **In-app update mechanism** | Prompted and forced upgrade paths | Store APIs, version policy service |
| **Feature flags** (`OPS-06`) | Disable a capability without a deployment — **the only instant remedy the mobile estate has** | Flag service availability |
| **Crash and ANR reporting** | Per-version crash rate, ANR rate, affected users | Reporting SDK |

**Version support policy** — the operational contract with the fleet:

| Rule | Value |
|---|---|
| Minimum supported OS | Android 11+, iOS 15+ for field apps; Android 9+, iOS 14+ for the customer app (`05-06` §10) |
| Versions supported concurrently | **The current version and the two before it** |
| Grace period before a version is blocked | **21 days** from release, extended for any cohort with a known connectivity constraint |
| Forced upgrade | Only under §4's four conditions |
| Server API compatibility | Server supports every app version inside the support window; breaking API changes require a dual-support period (`OP-008` `CR-03`) |

---

## 3. Health Checks

| Check | Command / dashboard | Healthy looks like |
|---|---|---|
| Crash-free sessions per version | Crash dashboard | **> 99.5%**; a new version below this halts its rollout |
| ANR rate (Android) | Play vitals | Below the store's bad-behaviour threshold and below the previous version's |
| **Version distribution** | Active devices by app version | ≥ 90% on the current or previous version within 21 days |
| **Devices not synced** | Sync dashboard: devices with `last_sync` older than 24 h | **Zero during a working day.** Each one is unrecorded work |
| Sync failure rate | Failed sync attempts ÷ attempts | < 1%; a spike means a server-side or schema problem, not a device problem |
| Sync duration on 3G | p95 sync completion after 24 h offline | ≤ 30 s (`NFR-037`) |
| Cold start on 3G | p95 job list load | ≤ 8 s (`NFR-036`) |
| Battery consumption | Per-shift battery telemetry | ≤ 12% per 8-hour shift excluding navigation (`NFR-082`) |
| Portal first-load size | Build report | ≤ 400 KB on critical customer paths (`NFR-081`) |
| Portal availability and latency | Synthetic monitoring per portal | `NFR-046`, `NFR-001` |
| Staged rollout state | Store console | Matches the planned percentage; no unexplained halt |
| Store policy status | Store console | No policy warnings, no pending removals |
| Certificate/signing key validity | Store signing configuration | Valid; expiry tracked (`OP-009` pattern) |

**Daily check (07:30 BST — before the field shift starts).** Devices not synced · crash rate on the
current version · rollout state · any store warning. **07:30 matters**: a technician who leaves the
depot with a broken app is unreachable for the rest of the shift.

---

## 4. Routine Operations

| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|
| **Portal release** | Build → staging → smoke ([`TS-013`](../13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md)) → deploy behind a flag → enable progressively → monitor | Low — instantly reversible | Normal change |
| **App release — staged rollout** | Submit → store review → **1% → 10% → 50% → 100%**, minimum 24 h at each step, longer over a weekend | Medium | Normal change (CAB for `P02`) |
| **Halt a rollout** | Halt in the store console immediately. **Users who already received the version keep it** — halting stops spread, it does not recall | Medium | On-call authority; no approval needed to halt |
| **Roll forward a fix** | New build, expedited review request where the store supports it, staged again from 10% if the fix is well understood | Medium | Mobile lead |
| **Force an upgrade** | Only under the four conditions below; announce 72 h ahead ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) template 15) unless the condition is security | **High** | **CTO** |
| **Change the minimum supported version** | Confirm the fleet distribution first → announce → enforce after the grace period | High — blocks anyone who cannot update | CTO |
| **Toggle a feature flag** | Change, observe, record in the change register (`OPS-06`) | Low — **this is the fast path and should be preferred over any app release** | Standard change |
| **Push a server-side configuration to apps** | Versioned configuration document fetched at sync; validate against schema before publishing | Medium — a bad configuration reaches every device without a store review | Normal change |
| **Wipe and re-enrol a device** | Only after confirming **the device has synced**; otherwise unsynced work is destroyed | **High** | Field Operations Manager + Support |
| **Recover unsynced data from a device** | Support-guided export from the app's diagnostics path → hand to Platform for ingestion | High | Mobile lead |
| **Store account and signing key maintenance** | Two named holders minimum; keys in vault (`NFR-062`) | High — losing a signing key means a new app listing and a fleet-wide reinstall | CTO |

**The four conditions that justify a forced upgrade** (`FU-01`):

| # | Condition |
|---|---|
| 1 | A **security** defect exploitable in the shipped version |
| 2 | A defect causing **data loss or double-application** (`DI-04` breach) |
| 3 | A **regulatory or statutory** requirement that the old version cannot meet |
| 4 | A **server contract change** that the old version cannot survive and that cannot be dual-supported |

Anything else is a prompted upgrade. `FU-02`: a forced upgrade is **never scheduled during a
working shift** — it goes out between 22:00 and 05:00 BST, and the fleet is checked at 07:30 before
the shift starts.

---

## 5. Common Failure Modes

| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|
| **Crash rate spikes on a new version** | Regression, or a device/OS combination untested | Crash dashboard by device and OS | **Halt the rollout first, diagnose second** | Crash-free sessions < 99% — `Sev1` for `P02` |
| Technicians cannot sign in after an update | Token or identity contract change (`OP-009`) | Auth errors by version | Roll forward; interim: technicians already signed in keep working offline | Any cohort blocked at shift start — `Sev1` |
| **Sync failing fleet-wide** | Server-side schema change, gateway error, or an expired contract version | Sync failure rate; server logs by app version | Restore the previous server contract; apps keep buffering (`NFR-047` gives 24 h) | **> 4 h — data is accumulating on devices with no server copy** |
| Sync failing on some devices | Device storage full, clock drift, or a corrupt local record | Device diagnostics from the app | Guide storage clearing; re-sync; last resort export and re-enrol | A device holds > 1 day of work |
| **Duplicate records after sync** | Idempotency key not honoured (`DI-04`/`IP-04` breach) | Compare client and server keys | Stop the sync path; deduplicate server-side; raise a defect | **Always — `Sev1` if financial** |
| Work lost after an update | Migration of the local store failed | Local store version; migration logs | Recover from the device's pre-migration copy if retained; **this is why the app retains one** | **Always — `Sev1`, and a mandatory PIR** |
| App slow or draining battery | Background location, polling frequency, or an unoptimised build | Battery telemetry (`NFR-082`); trace | Adjust the polling and location strategy by configuration if possible | Technicians reporting dead devices before shift end |
| Portal blank or erroring for all users | Deployment fault or CDN cache poisoning | Synthetic checks; error rate | Roll back the deployment; purge the CDN | Customer-facing — `Sev1` |
| Portal slow only on mobile networks | Payload size regression (`NFR-081`) | Build size report; field test | Roll back; enforce the budget in CI | Recurs — the budget is not gated |
| **Store rejects a submission** | Policy, permissions declaration, or metadata | Store review message | Correct and resubmit; **plan for 24–72 h of review even for a fix** | A fix for a `Sev1` is behind a review queue — escalate to store support and communicate an operational workaround |
| Store removes the app | Policy violation | Store notice | CTO and Legal engage immediately; users retain the installed app | **Immediately — `Sev1`, existential for `P02`** |
| A cohort stuck on an old version | Devices with no storage, no data allowance, or no Play services | Version distribution by branch and device model | Branch-level intervention with the champion ([`CM-008`](../16_Change_Management_and_Comms/CM-008_Champion_and_Super_User_Network_Kit.md)); Wi-Fi update at the depot | Blocks a forced-upgrade deadline |

---

## 6. Incident Response

| Severity | Response time | First actions | Who to notify | Comms template ([`OP-004`](OP-004_Incident_Communication_Template_Set.md)) |
|---|---|---|---|---|
| **Sev1** — field fleet blocked or losing data | Page immediately | **Halt any rollout** · confirm whether unsynced data is at risk · instruct the fleet through in-app and SMS (`OP-004` template 4) · switch to paper (`OP-014` FB-02) | Incident Commander, CTO, Field Operations Manager, Support Lead | 1, 4, 5 |
| **Sev1** — customer portal down | Page immediately | Roll back; status page; hotline takes bookings | Incident Commander, CTO, Contact Centre | 1, 3 |
| **Sev2** — degraded (slow sync, one portal, one cohort) | 30 min | Contain; decide roll-back vs roll-forward | Mobile lead, Support Lead | 2 |
| **Sev3** | Next business day | Ticket, next release | Mobile team | — |

**The decision that has to be made in the first ten minutes of an app incident:**

```
Is unsynced work at risk on devices?
  YES → Sev1. Instruct: do NOT reinstall, do NOT sign out, do NOT clear app data.
        (These three actions destroy the local store. OP-004 template 4 carries the wording.)
  NO  → severity by user impact.
```

[`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) `mac.tech.ack` and `OP-004` template 4 both carry that instruction because it is the only
message that matters to a technician in the first minute, and because the instinctive user
response — reinstall the app — is exactly the destructive one.

---

## 7. Manual Fallback

| Scenario | Fallback procedure | Duration tolerable | Reconciliation on recovery |
|---|---|---|---|
| App unusable for the field fleet | `OP-014` FB-02 — paper job card and signature sheet, photographs taken on the device camera roll with the job reference written on the first frame | One shift | Entered by the branch within 24 h; photographs attached by reference |
| Sync blocked but app usable | Continue working; the app buffers (`NFR-047`). **Tell technicians explicitly that buffering is working** — otherwise they reinstall | 24 h | Automatic |
| Customer portal down | Hotline 16743 and WhatsApp take bookings | 4 h | Contact centre enters; SMS confirms |
| Seller/vendor/partner portal down | Email intake to the owning function's mailbox | 1 working day | Entered on recovery |
| Store outage or blocked release | No new installs or updates; existing installs keep working | Days | None — but the forced-upgrade deadline is extended, formally and in writing |
| Device lost or destroyed mid-shift | Job re-issued to another technician from the dispatch board; **the unsynced work on that device is gone** and is re-collected from the customer where possible | Immediate | Documented loss; counted in [`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md) |

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| **On-device unsynced work** | **Zero tolerance — it exists only on the device** | Sync-dependent | The app retains a pre-migration copy of the local store across upgrades and a rolling local journal; recovery is by diagnostics export | *Not yet* |
| Portal build artefacts | Per release | ≤ 30 min | Redeploy the previous artefact | *Not yet* |
| App binaries (all supported versions) | Per release | ≤ 1 h | Retained in the artefact store; stores do not reliably permit re-publishing an old version | *Not yet* |
| **Signing keys** | Per rotation | — | Vault, with an offline copy. **Loss is unrecoverable**: a new app identity means every device must reinstall | *Not yet* |
| Store metadata and screenshots | Per change | ≤ 4 h | Version-controlled | *Not yet* |
| Feature flag state | Continuous | ≤ 5 min | Version-controlled with an audited change log | *Not yet* |

> **`BR-01`.** The store is **not** a backup. An old version that has been superseded cannot
> reliably be re-published, which is why rollback for mobile is roll-**forward** in practice and why
> the staged rollout percentages in §4 are the real control.

---

## 9. Break-Glass Access

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| Emergency halt of a rollout | **Any on-call engineer**, no approval | Halt in the store console; notify the Incident Commander immediately | Store console log, incident record |
| Emergency feature-flag disable | Any on-call engineer | Disable, record, notify | Flag change log |
| Emergency forced upgrade (security) | CTO | Force with the shortest safe notice; `OP-005` template 14 | Change record, incident record |
| Extract data from a technician's device | Field Operations Manager + Support Lead, **with the technician present** | Diagnostics export only; never a manual database read from the device | Ticket with the technician named as present |
| Emergency store account access | CTO | Second key holder; MFA | Store audit log |

**`BG-20`.** Halting a rollout requires **no approval at any hour**. The cost of an unnecessary halt
is a day's delay; the cost of a delayed halt is the whole fleet. Anyone hesitating over authority
should halt.

---

## 10. Change and Rollback

| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|
| Portal deployment | Normal change | Redeploy previous artefact; purge CDN | Synthetic checks, smoke pack |
| Portal feature behind a flag | Standard change | Disable the flag | Flag state + user check |
| **App release** | Normal change; **CAB for `P02`** | Halt the rollout; roll **forward** with a fix (see `BR-01`) | Crash rate, sync rate, version distribution |
| Forced upgrade | CTO | Withdraw the enforcement flag — users revert to prompted | Fleet distribution |
| Minimum supported version change | CTO | Restore the previous minimum | Blocked-user count returns to zero |
| Local store schema change | CAB | **Forward-only, like a database migration** (`OPS-07`). The app must migrate the local store safely and retain a pre-migration copy | Migration tested against a populated store on a minimum-spec device |
| Server API contract change | CAB (`OP-008`) | Restore dual support | Every supported app version validated |

> **`CR-06`.** The riskiest change in this runbook is a **local store schema migration**, because it
> runs on a device the company cannot reach, against data that exists nowhere else, possibly on
> 12% battery in a stairwell. It is tested on a minimum-specification device with a full local store
> before any rollout begins ([`TS-015`](../13_Test_and_Acceptance_Content/TS-015_Offline_and_Field_Condition_Test_Scripts.md)), and it never ships in the same release as a forced upgrade.

---

## 11. Post-Incident

Every `Sev1` and `Sev2` requires a review in `OP-016`. Mobile incidents add:

| Question | Why |
|---|---|
| Was any unsynced work lost? How much, whose, and was the customer affected? | The only irreversible outcome in this runbook |
| How long between the first crash report and the halt? | The halt latency is the single most improvable number in mobile operations |
| Did the fleet receive the instruction, and did they follow it? | An instruction not to reinstall only works if it arrives before the instinct does |
| Was the release staged as §4 requires? | Most fleet-wide mobile incidents are staged-rollout failures that were not staged |
| Did the store review delay the fix, and what did we do in the meantime? | The operational workaround is the mitigation, not the fix |

---

## Open Items

1. **OP-011-OI-01** — **Store accounts, signing keys and their holders do not exist yet.** Two named
   holders and a vault path are required before the first submission. Losing a signing key after
   launch would require every technician to reinstall.
2. **OP-011-OI-02** — The **21-day grace period and three-version support window (§2) are proposed
   here**, not derived from any upstream specification. They set server-side compatibility
   obligations and need Enterprise Architecture agreement.
3. **OP-011-OI-03** — Crash-free threshold (99.5%) and the halt trigger are proposed; QA and Mobile
   must ratify, and the threshold must be wired into the release process rather than watched.
4. **OP-011-OI-04** — `NFR-082` (≤ 12% battery per 8-hour shift) has **no measurement method
   defined**. Without one, §3's check cannot run.
5. **OP-011-OI-05** — Device ownership is unclear: company-provided or personal (BYOD)? It changes
   the wipe procedure (§4), the data-protection position (`NFR-090`), and whether §7's "device lost"
   row is an asset loss or a personal-property incident.
6. **OP-011-OI-06** — `P01` customer app is Flutter and the `P01` web portal is Next.js (`02-05`
   §5.4). Both are "the customer portal" on the status page (`OP-005` component 2). Confirm that a
   web-only or app-only incident can be published separately — currently it cannot.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a for the runbook; the apps it governs are bound by it
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2. **The fleet instructions it triggers
      are bilingual and live in `OP-004` and `OP-003`**
- [ ] Named approver recorded — CTO; Field Operations Manager co-approval for §6 and §7
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ● (deferred). G4 n/a.

---

*`OP-011` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
