---
id: OP-009
title: Runbook — Identity and Access
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Security
author: Security Lead with Platform Engineering
reviewers: [Chief Technology Officer, Data Protection Officer, HR Director, Internal Audit, Support Lead, Enterprise Architect]
approver: Chief Technology Officer
content_class: C
purpose: >
  The operating procedures for the identity provider that every portal and every employee depends
  on — sign-in, MFA, session policy, lockout, federation, privileged access, break-glass and the
  audit record. Identity failure locks out all twelve portals simultaneously, and break-glass
  access that is invented during that incident is neither authorised nor auditable.
traces_to: [M29, PS-01, 05-04, 05-06 NFR-011, NFR-012, NFR-062, NFR-065, NFR-069, NFR-070, NFR-072, KPI-089, KPI-090, OP-007, OP-013, OP-015, OP-012, UI-005, UI-036, SP-004]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md — identity, SSO, MFA, federation, privileged access and audit scope
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md PS-01 — single sign-on through M29; no portal maintains its own credential store
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-012 MFA mandatory for privileged roles; NFR-065 step-up authentication; NFR-069 session policy 30 min external / 60 min internal / 12 h absolute; NFR-070 privileged sessions recorded; NFR-062 secrets in a vault
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-089 critical vulnerabilities open > 7 days zero; KPI-090 orphaned accounts after leaver zero beyond 24 h
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/02_Architecture/02-05 §4 — Keycloak 26.x serving M29 identity, SSO, MFA and federation from W1
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03 §2.7 INT-046 — corporate client SSO (SAML/OIDC per client), W6
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Runbook — Identity and Access

> **Identity is the only component whose failure is total.** When the ERP is slow, people wait;
> when identity is down, nobody — customer, technician, cashier, administrator — can do anything
> at all, on any of the twelve portals, because `PS-01` gives them no other credential store.
>
> That single point of failure is a deliberate architectural choice. This runbook is the price of
> making it safely.
>
> **Verification status.** Authored at W0/W1; commands and thresholds are indicative until G3
> verification in the built environment.

| Item | Value |
|---|---|
| System | Keycloak 26.x identity provider — authentication, SSO, MFA, federation, session and token issuance for all 12 portals and all internal users |
| Owner team | Security, operated with Platform Engineering |
| Criticality | **P0** — total dependency |
| Availability target | Must exceed the highest portal target it gates: **≥ 99.9%** (`NFR-046`), effectively 24×7 (`NFR-045`) |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) — identity pages the security on-call **in addition to** the platform on-call |
| Escalation path | On-call → Security Lead → CTO → [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) TE-E9…TE-E12 for security events |

---

## 1. What This System Does

Every sign-in, every token, every session and every permission decision starts here. `PS-01`
forbids any portal from holding its own credential store, so the identity provider is the single
authority for who a person is; `05-04` decides what they may then do; `M29` records that they did
it.

**If it stops:** no one can sign in anywhere. Users already signed in continue until their token
expires — minutes to an hour — and then stop. The technician app keeps working offline against a
cached identity for up to 24 hours (`NFR-047`), which is the only part of the estate with natural
resilience. Branches fall back to paper ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md) FB-01). Customers cannot book, pay or track.

---

## 2. Architecture Summary

| Component | Purpose | Depends on |
|---|---|---|
| **Keycloak 26.x** (HA, ≥ 2 nodes) | Authentication, token issuance, MFA, session management, federation | PostgreSQL, network, TLS certificates |
| **Keycloak database** | Realms, clients, users, sessions (persistent), credentials | [`OP-007`](OP-007_Runbook_Core_ERP_Platform.md) PostgreSQL cluster |
| **Realm — internal** | Employees; MFA mandatory for privileged roles (`NFR-012`) | HR joiner feed (`M21`, [`OP-015`](OP-015_Access_Request_and_Joiner_Mover_Leaver_Content.md)) |
| **Realm — external** | Customers, sellers, vendors, brand, corporate, partner users | Portal registration flows |
| **Identity brokering** | Corporate client SSO per client (`INT-046`, SAML/OIDC, W6) | Client IdP availability |
| **OTP delivery** | Customer authentication by one-time code | SMS (`INT-010`/`INT-011`), WhatsApp (`INT-012`) — [`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md) |
| **API gateway integration** | Token validation at the edge (`PS-02`) | Kong (`OP-008`) |
| **Vault** | Client secrets, signing keys, break-glass credentials (`NFR-062`) | Vault availability |
| **Session store** | Active sessions; supports forced revocation | Keycloak DB / Redis (`OP-007`) |
| **Audit sink** | Immutable authentication and administrative event log (`NFR-014`) | Log platform, retained per `NFR-095` (5 years minimum) |

**Session policy (`NFR-069`), which is a configuration fact, not a preference:**

| Population | Idle timeout | Absolute maximum |
|---|---|---|
| External users (customers, sellers, vendors, partners, corporate) | **30 minutes** | **12 hours** |
| Internal users | **60 minutes** | **12 hours** |
| Privileged roles | 60 minutes, **plus step-up on sensitive actions** (`NFR-065`) | 12 hours |
| Technician app (offline capable) | Cached identity valid **24 hours** offline (`NFR-047`), then re-authentication required | 24 hours offline |

---

## 3. Health Checks

| Check | Command / dashboard | Healthy looks like |
|---|---|---|
| Provider liveness | `GET /health/ready` on each node | 200 from every node |
| Sign-in success rate | Grafana → *Identity* → success ÷ attempts, by realm | > 97% internal, > 92% external (external includes user error) |
| Sign-in latency | p95 token issuance | < 800 ms |
| Token validation errors at the gateway | Kong 401/403 rate | Flat; a step change means a key, clock or configuration problem |
| **Clock skew** | NTP offset on every node and gateway | **< 30 seconds** — skew invalidates tokens silently |
| Certificate and signing key expiry | Expiry report | > 30 days remaining |
| Active sessions | Session count by realm | Within normal daily curve; a collapse means mass expiry |
| Lockout rate | Locked accounts per hour | Baseline; a spike means either an attack or a configuration change |
| MFA enrolment coverage | Privileged accounts with MFA ÷ privileged accounts | **100%** (`NFR-012`) |
| Orphaned accounts | Accounts active with no matching active employee (`M21` feed) | **Zero beyond 24 hours** (`KPI-090`) |
| Service account inventory | Non-human accounts with owner and expiry | Every one has a named owner and a review date |
| Failed federation | Corporate IdP errors (`INT-046`) | Zero sustained; per-client visibility |
| Privileged session recordings | Recording coverage of privileged sessions | 100% (`NFR-070`) |
| OTP delivery success | Delivered ÷ requested, by channel | > 95%; failures fall back per [`NT-025`](../04_Notification_and_Messaging/NT-025_Notification_Failure_and_Fallback_Copy.md) |

**Daily check (09:00 BST).** Sign-in success rate · lockout spike · MFA coverage · orphaned account
report · certificate/key expiry · privileged sessions from the previous 24 hours reviewed.

---

## 4. Routine Operations

| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|
| **Password reset (self-service)** | User completes the self-service flow; no operator involvement | Low | None |
| **Password reset (assisted)** | Verify identity per §6 → trigger reset → user sets their own at next sign-in → **never** set a password on the user's behalf | Medium — this is the most common social-engineering target | Standard |
| **MFA device reset** | Identity proofing per §6 → line-manager confirmation → reset → user re-enrols → record | **High** — an MFA reset is a full account takeover if the requester is not who they claim | Standard, with proofing evidence |
| **Unlock an account** | Confirm the lock reason was failed attempts, not a security block → unlock | Low | Standard |
| **Create an account** | Only from an approved `OP-015` request driven by the `M21` joiner event. **Never** from a message | Medium | Per `OP-015` |
| **Grant a role** | Standard profile applied by role ([`MD-009`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md), `05-04`); anything beyond it needs [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) authority | Medium | Per `OP-015` |
| **Revoke access (leaver)** | Triggered by the `M21` leaver event; disable, revoke sessions, transfer ownership of records, record equipment return | **High if missed** — `KPI-090` is zero beyond 24 h | Automatic + verified |
| **Force-revoke all sessions for a user** | Session admin → revoke → confirm the user is signed out everywhere | Medium | Security judgement |
| **Rotate signing keys** | Publish the new key alongside the old → allow token lifetime to pass → retire the old key | **High** — retiring early invalidates every live token | Normal change |
| **Rotate a client secret** | Update vault → deploy to the client → verify → revoke old (`OP-008` pattern) | Medium | Normal change |
| **Onboard a corporate client SSO** (`INT-046`) | Exchange metadata → map attributes to roles → test with a pilot user → agree the client's own JML notification duty | Medium — a client that does not tell us about leavers creates orphaned access **in our system** | CAB + Account Management |
| **Quarterly access recertification** | Generate per-manager reports → managers confirm or revoke → revoke non-responses after the deadline → record | Medium — recertification that never revokes anything is theatre | Security + line managers |
| **Add a service account** | Named human owner, stated purpose, scoped permissions, expiry date, credential in vault | Medium | CTO |

> **`RO-02`.** *Non-response on a recertification is a revocation, not an approval.* Stated
> explicitly because the opposite default is how access accumulates in every organisation that has
> ever run a recertification campaign.

---

## 5. Common Failure Modes

| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|
| **Nobody can sign in, anywhere** | Identity provider down, database unreachable, or certificate expired | Node health; DB connectivity; certificate dates | Restart nodes; restore DB connectivity; replace certificate | **Immediately — `Sev1`, always** |
| Sign-in works, portals reject the token | Signing key rotated too early, or clock skew | Compare key IDs; check NTP offset | Restore the previous key until tokens expire; fix NTP | `Sev1` — the symptom looks like an application fault and wastes time |
| One portal cannot authenticate, others fine | Client configuration, redirect URI, or client secret | Client config; error in the auth log | Correct the client configuration | Customer-facing portal — `Sev1` |
| Mass lockouts | Credential-stuffing attempt, or a lockout threshold change | Failed attempt sources; recent configuration changes | Rate-limit and block sources (`NFR-068`); do **not** raise the lockout threshold as a workaround | **Any suspected attack — security incident, `Sev1`** |
| Customers not receiving OTP | SMS provider failure (`OP-008` FB-03) | OTP delivery dashboard; provider status | Fail over to the secondary gateway, then WhatsApp | OTP unavailable > 15 min — customers cannot sign in |
| MFA prompts loop | Time drift on the user's device, or an enrolment defect | Server time vs token window | Guide the user to correct device time; re-enrol if needed | Widespread — check server NTP first |
| A leaver still has access | JML automation failed, or the leaver event never fired | `M21` event log vs account state | Revoke immediately; investigate the pipeline | **Always — `KPI-090` breach and a reportable control failure** |
| A user has access they should not | Role assignment outside the standard profile | `05-04` matrix vs actual assignment | Revoke; determine who granted it and under what authority | Any privileged or finance permission — security incident |
| Corporate SSO failing for one client | Client-side IdP change or expired federation metadata | Federation error log; metadata validity | Re-exchange metadata with the client | Client is blocked — notify the account manager ([`OP-004`](OP-004_Incident_Communication_Template_Set.md) template 6) |
| Session expiring too quickly | Policy misconfiguration, or a load balancer breaking session affinity | Effective session policy vs `NFR-069`; LB configuration | Correct the policy; never extend beyond `NFR-069` limits to silence complaints | Change requested to exceed policy — refuse and escalate |
| Privileged session not recorded | Recording pipeline failure (`NFR-070`) | Recording coverage report | Restore recording **before** further privileged work | Always — an unrecorded privileged session is an audit finding |
| Identity DB replication lag | Underlying database issue | `OP-007` §3 checks | Follow `OP-007` | Lag risks authentication inconsistency |

---

## 6. Incident Response

| Severity | Response time | First actions | Who to notify | Comms template (`OP-004`) |
|---|---|---|---|---|
| **Sev1** — identity unavailable | Page immediately, both platform and security on-call | Declare · confirm blast radius across all portals · publish to the **login-screen notice** ([`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md), which renders before authentication) · start the timeline | Incident Commander, CTO, Security Lead, Support Lead, Operations Director | 1, 3, 5 |
| **Sev1** — suspected compromise | Page immediately | **Preserve first**: capture logs and sessions before revoking. Then contain: revoke sessions, disable the account, rotate affected credentials | CTO, Security Lead, **DPO** (`NFR-094` assessment clock starts at detection) | 1, plus `OP-004` §2.6 template 22 |
| **Sev2** — degraded (one portal, one client, OTP channel) | 30 min | Confirm scope; apply the channel fallback | Security Lead, Support Lead | 2 |
| **Sev3** | Next business day | Ticket | Security | — |

**Identity proofing for an assisted reset or MFA reset** — the procedure that stops the most common
attack on any service desk:

| Step | Requirement |
|---|---|
| 1 | The request arrives through a **recorded channel** ([`OP-001`](OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.4). A request by voice alone is completed only after step 3 |
| 2 | The requester is asked one item from the HR record that is **not** in the corporate directory and not on a business card |
| 3 | The **line manager confirms**, through a separate channel from the one the request arrived on |
| 4 | For privileged accounts, a **second** confirmation from Security |
| 5 | The reset link goes to the **registered** address or device — never to one supplied in the request |
| 6 | The proofing evidence is recorded on the ticket |

> **`IP-01`.** Urgency is not a reason to skip proofing; urgency is the standard pretext. The
> macro that says so politely is [`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) #11.

---

## 7. Manual Fallback

> Identity has no manual fallback in the ordinary sense — you cannot authenticate on paper. What
> exists is a **degraded operating mode** that lets the business trade while identity is restored.

| Scenario | Fallback procedure | Duration tolerable | Reconciliation on recovery |
|---|---|---|---|
| Identity down, branches open | `OP-014` FB-01 paper mode; the branch manager authorises transactions **on their own signature**, recorded on the form with time and staff name | 4 h | Every form entered afterwards is attributed to the named staff member, not to the manager's account |
| Identity down, technicians in the field | App continues on cached identity for up to 24 h (`NFR-047`) | 24 h | Automatic on sync |
| Identity down, customers cannot sign in | Hotline 16743 takes bookings; customers told to try again later; **no workaround credential is ever issued** | 4 h | Bookings entered by the contact centre |
| Identity down, administrative action required | Break-glass §9 | Minutes | Every break-glass action reviewed within 1 working day |
| MFA channel unavailable (SMS down) | Alternative second factor for privileged users (authenticator app, already enrolled); **MFA is never disabled to restore access** | Until the channel returns | None |

**`FB-02`. MFA is never turned off to work around an outage.** If that is proposed during an
incident, the answer is no, and the person proposing it should be told this rule exists precisely
because the proposal is reasonable-sounding under pressure.

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| Identity database (realms, users, clients, roles) | ≤ 15 min | **≤ 1 h** — must be faster than the ERP's 2 h, because everything else waits on it | Restore with the ERP cluster procedure (`OP-007` §8), verify a test sign-in per realm | *Not yet* |
| Realm configuration export | Per change | ≤ 30 min | Version-controlled export re-imported (`OPS-02`) | *Not yet* |
| Signing keys | Per rotation | ≤ 30 min | Vault restore; **key loss invalidates every token and every session** | *Not yet* |
| Federation metadata (per corporate client) | Per change | ≤ 2 h | Re-exchange with the client — depends on **their** availability, which is why it is held, not fetched | *Not yet* |
| Audit log | Continuous | N/A — append-only | Retained ≥ 5 years (`NFR-095`); restoration is for investigation, not for service | *Not yet* |

**Recovery verification set:** one internal sign-in with MFA · one external sign-in with OTP · one
corporate federated sign-in (from W6) · one token validated at the gateway · one privileged action
producing a recorded session and an audit entry. **Service is not restored until all five pass**,
regardless of what the health endpoint says.

---

## 9. Break-Glass Access

The section this runbook exists for. Break-glass is pre-authorised, pre-provisioned and rehearsed —
or it is improvisation during the worst incident the programme will have.

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| **Identity provider unavailable; ERP administration required** | CTO; if unreachable within 15 min, Operations Director, recorded | Local emergency administrator on the ERP, credentials in the vault break-glass path. **Two people: one acting, one witnessing.** Time-boxed to the incident | Vault retrieval, session recording, incident record, review in 1 working day |
| **Vault also unavailable** | CTO **and** CEO/Managing Director jointly | Sealed offline credential envelope held in the head-office safe, opened with both signatures on the log sheet | Physical log sheet, photographed into the incident record; **credential rotated immediately after** |
| **Suspected administrator account compromise** | Security Lead | Disable the account, revoke sessions, rotate its credentials, hand the account to Security | Security incident record; DPO informed |
| **Corporate client IdP down; client blocked** | Account Manager + Security Lead | Temporary local credentials for named client users, **expiring in 24 hours**, MFA still required | Ticket, expiry evidence, client notification |
| **Last remaining administrator locked out** | CTO | Recovery path documented in the sealed envelope; never a permanent second admin "just in case" | As row 2 |

| # | Rule |
|---|---|
| **BG-10** | Break-glass credentials are **tested quarterly** — retrieved, verified, rotated. An untested break-glass credential is a belief, not a control |
| **BG-11** | Every use is rotated immediately afterwards and reviewed by Security within 1 working day (`NFR-070`) |
| **BG-12** | The sealed envelope procedure is rehearsed in the DR exercise ([`OP-012`](OP-012_Disaster_Recovery_and_Continuity_Playbook.md) §Exercises), because the safe, the signatories and the log sheet all have failure modes of their own |
| **BG-13** | **Break-glass is never used to bypass an approval queue.** Where it has been, the queue is the finding ([`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md)) |

---

## 10. Change and Rollback

| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|
| Realm or client configuration | Normal change | Re-import the previous version-controlled export | Sign-in per affected portal |
| **Session or MFA policy** | **CTO + Security**, never a standard change | Restore the previous policy | Verify against `NFR-069`/`NFR-012` — the policy is an NFR, so a change is an NFR variance and needs recording |
| Role or permission model | CAB + `SP-004` authority | Restore the previous role mapping | Access matrix spot check against `05-04` |
| Signing key rotation | Normal change | Re-publish the retired key **only if it has not passed its retirement window** | Token validation test |
| Identity provider version upgrade | CAB, staging first | Redeploy previous version; **database migration may prevent it** — check before upgrading | Full §8 verification set |
| Federation onboarding | CAB | Disable the federation; the client's users cannot sign in — coordinate with the client first | Pilot user sign-in |
| Lockout thresholds | Security Lead | Restore previous | Lockout rate observed 24 h |

> **`CR-04`.** An identity change is deployed **only** in a window when Security and Platform are
> both available, and never on the day of a wave cutover. `NFR-008` zero-downtime does not apply
> comfortably to token-issuing infrastructure: tokens outlive deployments.

---

## 11. Post-Incident

Every `Sev1` and `Sev2` requires a review in `OP-016`. Identity incidents add mandatory questions:

| Question | Why |
|---|---|
| Was any account compromised, and what did it reach? | Determines whether this is an availability incident or a personal-data incident (`NFR-094` assessment) |
| Was break-glass used? By whom, witnessed by whom, rotated when? | `BG-11`; an unrotated credential is a live finding |
| Did the login-screen notice reach locked-out users? | It is the only channel that works when identity is down (`OP-005`) |
| Were privileged sessions recorded throughout? | `NFR-070`; gaps are audit findings regardless of outcome |
| Did any control get weakened to restore service (MFA, lockout, session length)? | If yes, when is it restored, and who verifies? A temporary weakening that is never reversed is the most common post-incident finding in security operations |
| Did the leaver/joiner pipeline behave? | `KPI-090` |

---

## Open Items

1. **OP-009-OI-01** — **Break-glass has no owner, no vault path and no safe.** §9 describes a control
   the company does not yet operate. It must exist **before W1 go-live**, not after the first
   incident. This is the highest-priority open item in Category 17.
2. **OP-009-OI-02** — Identity RTO is set here at **1 hour**, tighter than the `NFR-007` platform RTO
   of 2 hours, because everything else waits on identity. **This is a proposal**; `05-06` does not
   carry a component-level RTO and the Steering Committee has not accepted one.
3. **OP-009-OI-03** — **Quarterly access recertification has no named owner** and no tooling before
   `M66` (W6). Until then it is a manual campaign from `05-04` and `MD-009`, and nobody is
   resourced to run it.
4. **OP-009-OI-04** — Corporate SSO (`INT-046`, W6) requires each client to notify us of **their**
   leavers. That obligation is not in any contract template ([`LG-003`](../10_Legal_Policy_and_Compliance/LG-003_Portal_Terms_of_Use_Corporate.md)) and creates orphaned access
   in our system that `KPI-090` will not detect.
5. **OP-009-OI-05** — `NFR-012` requires MFA for "admin, finance, HR and all privileged roles". The
   **privileged role list is not enumerated** anywhere; `05-04` has 38 roles with no privilege flag.
   MFA coverage is therefore unmeasurable as written.
6. **OP-009-OI-06** — Service-account inventory (§3) does not exist and no module owns it. Service
   accounts are the access class that recertification always misses.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; engineering and security audience
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2
- [ ] Named approver recorded — CTO; **§9 additionally requires Security Lead and a Board-level
      acknowledgement of the sealed-envelope procedure**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required (Class C):** G1 ●, G2 ●, G3 ● (deferred to build). G4 n/a.

---

*`OP-009` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
