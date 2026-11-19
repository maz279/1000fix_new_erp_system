# M29 Identity, Access & Security: second sub-module capture audit

**Date:** 19 Nov 2026 · **Area:** A12 · **Workspace fragment:** `cd_p03_portal/static/src/a12/m29.js`
**Backend:** `cd_rbac_ext` 19.0.1.6.0 (`models/fix_m29_capture2.py`, imported last), `cd_grc` (`models/fix_m29_breach_handoff.py`),
`cd_p03_portal/controllers/a12/m29.py` · **Branch:** `fix/m29-capture-pass2` (worktree `1000 fix/m29cap2-wt`)

The user again reported that not every M29 sub-module page has a relevant data-capture button. The
[14 Nov audit](M29_CAPTURE_BUTTON_AUDIT_2026-11-14.md) had given every page a "+ New" and its own
list's chips. This pass checked each page against what the **spec** says a person records there
(§5 FR-SEC-001..052, §8 lifecycles, §9 BRU-SEC, §10.1 entities, §11 AUT-SEC, §13 SoD, §14 reports), rather
than against the lists already on the page.

## What was missing

| # | Page | Spec | Gap found in the code |
|---|---|---|---|
| 1 | Identity & MFA | §8.1 Active → **Suspended** → Active; `identity.suspended`; `/identities/{id}/suspend` | JML had joiner / mover / leaver only. Suspending someone for leave or an investigation meant either a leaver event (which removes every group, so access can't be restored) or untracked deactivation on the User form. |
| 1 | Identity & MFA | FR-SEC-012 (P0) service accounts; BRU-SEC-17 / AUT-SEC-11 orphaned accounts; AUT-SEC-25 rotation | No register of non-human identities anywhere: no accountable owner, no scope, no credential rotation, no orphan rule. |
| 1 | Identity & MFA | FR-SEC-010 device trust; AUT-SEC-03 "deregister devices, reassign delegated authority" on a leaver | Devices were enrolled in M02 but never shown on the page. **A leaver kept their enrolled technician devices and their delegations of authority.** |
| 1 | Identity & MFA | FR-SEC-028/029 mover / leaver | **Defect: the "Record a Joiner / Mover / Leaver" form could not record a mover or a leaver.** The JML surface fenced the employee picker server-side to employees *without* a login, for the 14 Nov New-User form. That fence applied to every form on the model, so only login-less people could be picked, and a mover or leaver needs a login. |
| 2 | Role & Group Model | FR-SEC-019 delegation (bounded, audited, auto-expiry) | M63's `fix.approval.substitution` implements it, but no M29 page offered or listed it. |
| 6 | Data Protection | FR-SEC-047 (P0) "a sensitivity classification **and a residency classification on every field**"; §10.1 `owning_module`, `classified_by` | The classification had sensitivity only. Residency class, owning module and who classified it were missing. |
| 6 | Data Protection | FR-SEC-049 (P0) cross-border transfer gate; FR-SEC-051 data-subject right execution | M60 (`fix.grc.data.transfer`) and M33 (`fix.rights.request`) own these, but neither appeared on the M29 page. |
| 7 | Monitoring & Audit | §8.3 / AUT-SEC-13 / NFR-094 breach assessment; §13 "the triager cannot be the sole approver that it is non-notifiable"; `security.breach_assessed`; hand-off to M60 | The breach assessment was free text, required only for the "data leak" category. There was no personal-data flag, no notifiable decision, no second-officer rule, no statutory clock and no M60 hand-off. A phishing or unauthorised-access incident that exposed personal data could close with no assessment at all. |
| 7 | Monitoring & Audit | FR-SEC-035 / BRU-SEC-20 / AUT-SEC-10 break-glass: "loud, post-hoc justification, automatic expiry"; FR-SEC-034 session recording; §14 "sessions recorded and reviewed" | The "break-glass" record was really a pre-approved elevation. There was no emergency path that opens first and is justified afterwards, no record of the actions taken, and no review of a session by anyone else. |
| 7 | Monitoring & Audit | AUT-SEC-16 / AC-26 / INT-SEC-06 penetration tests: "load findings, assign owners and SLAs, track to verified closure" | Vulnerabilities could say `source = pentest`, but no engagement record tied a report to its findings or proved closure. |

Pages 3 (Record & Field Rules), 4 (Access Requests) and 5 (SoD Testing) already captured everything the spec
gives them. SoD exceptions are approved by the CFO/CTO group and are time-boxed to a quarter, which covers the
quarterly-review rule.

## What was built

**Page 1, Identity & MFA**
- **Suspend / Reinstate** (`M29-form-suspend`, plus `suspend` / `reinstate` on `fix.jml.event`). A suspension needs a reason (leave, investigation, unconfirmed certification, security, other) and a justification. A second Access Approver applies it. It switches the login off and ends its sessions **but keeps the roles**. A reinstatement switches the login back on, but only when the login's last identity event was a suspension: a leaver, or a login whose access end date has passed, must come back through a joiner. The login is always the employee's own, never a typed one. Audit rows: `identity.suspended` and `identity.reinstated`.
- **Service Account** register (`fix.service.account`, `M29-form-service-account`, `M29-service-accounts`). Each account records kind, purpose, permitted scope, technical login, client id, an **accountable owner** (an active internal user, never the account itself) and a credential **vault reference** (never the secret). Rotation follows its own schedule:
  - **Register Rotation** (owner or officer) needs a new `vault://` reference.
  - **Suspend / Retire** switch the login off. **Reactivate** needs a second person and an active owner.
  - The hourly job flags an account without an active owner, and **suspends it after 24 hours** (BRU-SEC-17). It also reminds the owner a week before a rotation falls due.
- **Leaver hand-off** (every leaver path, including the `employee.left` consumer): enrolled technician devices are revoked ("Technician left"), and delegations to or from the leaver end. Both are audited.
- **Device Registration** chip opens M02's device form. The page lists the device registry.
- **JML picker defect fixed:** the surface-wide fence was removed. Each form now declares its own checked filter: New User = no login, Suspend = has a login, generic JML = anyone. The server still derives the login from the employee on create.

**Page 2, Role & Group Model:** a **Delegation of Authority** chip opens M63's substitution form; the page lists the delegations.

**Page 6, Data Protection:**
- The classification now records a **Residency Class**: not classified / Bangladesh-resident / restricted / critical information infrastructure.
- It also records the **Owning Module**.
- **Classified By / On** is stamped on create and on every reclassification, and the change is audited.
- A residency-classified field must be at least S2.
- **Cross-Border Transfer** (M60) and **Data-Subject Request** (M33) chips, with their lists on the page.

**Page 7, Monitoring & Audit**
- **Breach assessment as a decision.** The incident records owner, *Personal data involved?* (unknown / no / yes), *significant damage likely?* and the number of data subjects. A "yes" schedules the assessment, which is due 72 hours after detection.
  - **Assess Breach** (officer): **notifiable** stamps the statutory clock and creates the **M60 Personal Data Breach** record, telling the Compliance Officers.
  - **Not notifiable** waits for **a second officer's confirmation**.
  - Significant damage forces notifiable.
  - The facts lock once assessed.
  - An incident cannot close while personal data is "unknown", or while it is "yes" and the decision is not settled.
- **Emergency break-glass** on the privileged session:
  - Only administrators and Security Officers can use it.
  - It opens at once without approval, for at most 4 hours (`fix_rbac_ext.break_glass_hours`).
  - Every approver, officer and administrator is told immediately.
  - A post-hoc justification is due within 24 hours, otherwise the hourly job escalates it.
- **Every** session's close now asks *what was done* (FR-SEC-034). A closed session is **reviewed by someone other than the holder**: *Justified*, or *Not Justified*, which raises a policy-breach incident on the session. The Privileged Session Log shows break-glass and review columns.
- **Penetration Test** register (`fix.security.pentest`, `M29-form-pentest`, `M29-pentests`):
  - It covers the engagement, provider, type, scope, test window and report.
  - Findings are vulnerabilities linked to the test, and can be filed only once the report is in; their source becomes "pentest".
  - It **closes only when every finding is verified closed or risk-accepted** (AC-26).
- New KPI tiles: Breach Assessments Overdue, Break-Glass Unreviewed, Orphaned Service Accounts.

All decision and lifecycle stamps are guarded by `fix.guarded.mixin`, are absent from the write whitelist and read-only on the forms. Audit rows carry references and categories, never personal data. Forms with more than 15 fields are tabbed (session, service account, incident, pen test).

## Evidence

- **Page guard** `cd_p03_portal/tests/test_m29_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node over the real registry: **50 checks**. Run against unmodified HEAD (a6ca660a) in a throwaway tree, **22 fail**, covering every finding above; after the change, **50/50 pass**.
- **Live suite** `cd_rbac_ext/tests/test_m29_capture_pass2_live.py`: **27 tests**, run as non-admin users (plain user, two officers, two approvers, administrator) through `/p03/model/form|write|action|choices` on a private clone (`fix_test_m29c2`, after `-u cd_rbac_ext,cd_grc,cd_p03_portal`, 0 errors). **27/27 pass.**
- **Mutation check:** 28 mutants, each removing one new rule. **27 turn the suite red.**
  - Four first survived because a second defence masked them: two were caught only by the form lock, and two by the ACL. The tests now also assert the ORM refusal, and a user granted the ACL directly but holding no appointment, so all four are red.
  - The one survivor is a true equivalent. It removes the redundant re-derivation of the login on a suspension, but the base `create` already sets the employee's own login, and an employee without one is refused first.
- **Regression** on the private clone, all of `cd_rbac_ext` (including 14 Nov's 43-test live suite) plus the M29/A12/estate/KPI/report-export portal guards and `cd_grc`:
  - **8 failures came from the new rules.** Older tests closed incidents without answering "personal data involved?", or closed sessions without a record of actions. One control test (x5) forbids the names `last_rotated_on` and `next_rotation_on` anywhere in m29.js. The tests now answer "no" or pass the summary, and the service-account form shows neither field (the rotation date stays on the list).
  - Re-run: **all green.**
  - **3 `cd_grc` handoff failures** (risk register relay) **also fail with the `cd_grc` override removed.** Cause: the clone holds 52,625 events with no `relayed_at`, and the tests relay only the oldest 10,000, so their own event is never reached. On a copy with that backlog marked relayed, **all 11 handoff tests pass with the M29 code.**
- **Headless browser walk** (Playwright, private server on port 8151 running this branch, signed in as a walk user on the clone only):

| Page | "+" button | Forms capturing it (as rendered) |
|---|---|---|
| Identity & MFA | + Provision a New Login | Provision Login · JML Event · **Suspend / Reinstate** · **Service Account** · **Device Registration** · User |
| Role & Group Model | + New Business Role | Role · Model Access · **Delegation of Authority** |
| Record & Field Rules | + New Record Rule | Record Rule · Field Rule · Isolation Tier |
| Access Requests | + Access Request | Access Request · Certification Campaign · Certification Line |
| SoD Testing | + New SoD Test Run | SoD Test Run · SoD Control · SoD Exception |
| Data Protection | + New Sensitive Field | Sensitive Field · Encryption Key · **Cross-Border Transfer** · **Data-Subject Request** |
| Monitoring & Audit | + Report a Security Incident | Security Incident · Privileged Session · Vulnerability · **Penetration Test** |

  0 page errors. A Penetration Test was **saved through the form** (PT/2026/010, Planned). The Suspend / Reinstate chip opens with the action set to "suspend". The three new KPI tiles render live.

## Open (owner decisions, not built)

- **Authority notification reference on transfers (AC-14).** M60's transfer approval requires safeguards over an in-force processing activity, but it has no Authority-notification record. Which regulator receives the notification is the spec's open question Q-04, so it was left to M60 and Legal.
- **Device trust for non-technician apps** (rider, auditor) has no register. Q-11 asks whether device binding is mandatory.
- **People on fix_real:** one Security Officer, one Access Approver and no Key Custodian (see the 14 Nov report). A second officer is needed to confirm "not notifiable" and to review a break-glass used by the only officer.
- Keycloak-side MFA enrolment and step-up remain L4 configuration, not workspace records.

## State

- Code commit `fix(CD-M29-01)`, rebased onto the shared branch at 00253dc4. After the rebase and ruff formatting, the full `cd_rbac_ext` suite, the M29 page guard and the estate page standard were re-run on the private clone: **1,045 tests, 0 failures**.
- Deploying needs `-u cd_rbac_ext,cd_grc,cd_p03_portal` on fix_real and fix_dev, plus one restart of 8069/8090. That is the owner's call, and is combined with the peers holding restarts.
