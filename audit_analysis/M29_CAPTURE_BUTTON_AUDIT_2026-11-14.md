# M29 Identity, Access & Security: sub-module capture audit

**Date:** 14 Nov 2026 · **Area:** A12 · **Workspace fragment:** `cd_p03_portal/static/src/a12/m29.js`
**Backend:** `cd_rbac_ext` (models), `cd_p03_portal/controllers/a12/m29.py` (surfaces, write whitelist, reports, KPIs)

The user reported that not every M29 sub-module page has a relevant data-capture button.
The report was correct. Before this fix, two of the seven pages had no capture at all. Four more offered
only their "+ New" and not the other records shown on the page. Three working screens were on no page.

## What M29 is supposed to capture

The Function Register only names the seven sub-modules (14 + 13 + 15 + 10 + 9 + 10 + 7 = 78 functions).
The detail is in `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md`:
§5 (FR-SEC-001..052), §10.1 (owned entities), §11 (AUT-SEC-01..25) and §9 (BRU-SEC-01..25).

| # | Sub-module | Spec basis | What a person records there |
|---|---|---|---|
| 1 | Identity & MFA | §5.1, FR-SEC-001, 027-029, AUT-SEC-01/03 | The identity-lifecycle event: joiner, mover or leaver. Logins come from onboarding: `employee.joined` → identity-lifecycle service → Keycloak. The **1000FiX SSO (Keycloak)** provider is enabled on fix_real. |
| 2 | Role & Group Model | §5.2, FR-SEC-013/014 | Business roles and permission sets (model access) |
| 3 | Record & Field Rules | FR-SEC-015/016, isolation tiers T0-T5 | Record rules, field rules, isolation tiers |
| 4 | Access Requests | §5.3, FR-SEC-025/026 | Access requests, certification campaigns and lines |
| 5 | SoD Testing | FR-SEC-022..024 | SoD test runs, SoD controls, time-boxed SoD exceptions |
| 6 | Data Protection | §5.6, FR-SEC-046/047 | Field classification and encryption-key references |
| 7 | Monitoring & Audit | §5.4/5.5/5.7, AUT-SEC-10/13-16, BRU-SEC-21 | Security incidents, break-glass requests and **vulnerabilities**. The audit trail itself is system-written. |

## What the code did (proved on HEAD before the fix)

`cd_p03_portal/tests/test_m29_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node
over the real registry. Against unmodified HEAD, in a throwaway worktree, **12 of its 26 checks fail, and all 7 pages fail**:

| # | Page | "+ New" on HEAD | Form chips on HEAD | Defect |
|---|---|---|---|---|
| 1 | Identity & MFA | **none** | User (opened a **blank login** form) | No capture. The User chip let an admin create a login outside onboarding: no joiner event, no SoD gate, no audit. JML Automation, the identity lifecycle, sat on page 4. |
| 2 | Role & Group Model | Business Role | Role | Model Access was listed but could not be captured |
| 3 | Record & Field Rules | Record Rule | Record Rule | Field Rule and Isolation Tier were listed but could not be captured |
| 4 | Access Requests | Access Request | Access Request | Certification campaigns and lines could not be captured. **Certification Campaigns** and **Role Assignments** were on no page. |
| 5 | SoD Testing | SoD Test Run | **none** | SoD controls could not be captured. **SoD Exceptions** were on no page. |
| 6 | Data Protection | Sensitive Field | **none** | Encryption keys could not be captured |
| 7 | Monitoring & Audit | **none** | **none** | No capture. Nobody could report an incident or request break-glass access from the page. **No vulnerability register existed anywhere in the codebase**: spec §10.1 `fix.vulnerability`, BRU-SEC-21, AC-23 and the KPI "critical vulnerabilities open > 7 days: zero" had nothing to measure. |

Two further findings:
- A reported incident wrote nothing to the audit trail, so a capture made from page 7 never appeared on that page's grid. The spec event is `security.incident_raised`.
- The SoD Violations report screen had no report route, so no page offered it.

## What was changed

**Workspace (m29.js)**
- Every page names its captures explicitly:
  - 1: "+ Record a Joiner / Mover / Leaver". JML moved onto the page.
  - 2: + Model Access.
  - 3: + Field Rule and + Isolation Tier.
  - 4: + Certification Campaign and + Certification Line. Campaigns and Role Assignments moved onto the page.
  - 5: + SoD Control and + SoD Exception. SoD Exceptions and the SoD Violations report are on the page.
  - 6: + Encryption Key.
  - 7: "+ Report a Security Incident", + Privileged Session and + Vulnerability.
- The User form is now `create: false`, with a message pointing to onboarding and the JML event. Editing an existing user is unchanged.
- New screens:
  - Vulnerability Register list, with row actions: Mark Remediated, Verify Closed, Send Back, Accept Risk.
  - Vulnerability form.
  - Vulnerability Register report.
  - KPI tile "Critical Vulns Past Due".

**Backend (cd_rbac_ext 19.0.1.4.0)**
- New `fix.vulnerability`, in `models/fix_vulnerability.py`, follows spec §10.1.
  - **Fields:** source, identifier, component and severity. The remediation due date is computed: critical = 7 days per the spec. High 30, medium 90 and low 180 days are working defaults the owner can change.
  - **Lifecycle:** open → remediated (by the owner or an officer, with a note) → verified. The verifier must be a Security Officer who did not remediate the finding.
  - **Risk acceptance:** a Security Officer who neither reported nor owns the finding can accept the risk, with a reason, for 90 days by default. When the acceptance ends, the finding reopens.
  - **Guards:** all lifecycle stamps are guarded. After filing, only an officer can change the severity, and the change is audited. Once a finding leaves Open, it cannot change.
  - **Access:** the reporter and the remediation owner see the record; Security Officers see all. Each step writes an audit row containing only the reference and severity, never the component, because every internal user can read the trail.
  - **Daily job (BRU-SEC-21):** escalates each critical finding open past its due date, once. It posts a message, gives Security Officers an activity and writes a `vulnerability.critical_open` audit row.
- `fix.security.incident.create` now writes an "incident reported" audit row (reference, severity, category; never the title).
- Controller: `fix.vulnerability` surface (caller's record rules), write whitelist, `vulnerability_register` report, `critical_vulns_overdue` KPI.

## Evidence

- `cd_p03_portal/tests/test_m29_capture_buttons.py`: 26 checks. **12 fail on HEAD, 26 pass after the fix.**
- `cd_rbac_ext/tests/test_m29_capture_live.py`: 29 tests on fix_test, run as non-admin users through `/p03/model/form|write|action`. **29/29 pass.** They show that:
  - all 17 capture forms open blank for their intended actor;
  - a joiner can be filed but not applied by its filer;
  - a plain user's incident report lands on the audit trail without its title;
  - a break-glass request is created in the requester's name;
  - a vulnerability is filed with a 7-day due date for critical severity, and typed stamps are ignored;
  - only the reporter, the owner and Security Officers can read a vulnerability;
  - only an officer can change severity, and the change is audited;
  - the owner remediates and a second officer verifies; an officer cannot verify their own remediation;
  - risk acceptance is refused for the owner, and a lapsed acceptance reopens the finding;
  - a critical finding past due is escalated exactly once;
  - the report and the KPI read as the caller.
- Browser check on 8069 with `?debug=assets`, which serves the new JS from disk to this session only:
  - all 7 pages show their "+" button;
  - Monitoring & Audit lists "Forms Capturing It: Security Incident · Privileged Session · Vulnerability";
  - "+ Report a Security Incident" opens the incident form.
- Regression on fix_test covered all `cd_rbac_ext` suites plus the estate, KPI, report-export, A12 whitelist and M19/M28 capture guards: **1,275 tests**. The 3 failures were all caused by this change:
  - two tests counted incident audit rows exactly, and a report now adds its own row;
  - the estate standard requires the User chip to stay on a page.
  After the fixes, a re-run of those plus both M29 guards and the estate test is **667/667 green**.

## Deploy (14 Nov 2026, user-approved)

1. A read-only drift check of the working tree against fix_real showed one difference only: `TABLE fix_vulnerability`.
2. `-u cd_rbac_ext` on fix_real: clean, 155 modules loaded.
3. 8069 relaunched (no supervisor; same command line). `/web/login` returned 200 in about 3 s, with 0 "Failed to load registry" lines.
4. The production bundle `c5daf52` contains the new registry. `/p03/model/records` for `fix.vulnerability` and the Vulnerability Register report are served.
5. Production page sweep (no debug mode):

| Page | "+" button | Forms on the page |
|---|---|---|
| Identity & MFA | + Record a Joiner / Mover / Leaver | JML Event · User (opens existing users only) |
| Role & Group Model | + New Business Role | Role · Model Access |
| Record & Field Rules | + New Record Rule | Record Rule · Field Rule · Isolation Tier |
| Access Requests | + Access Request | Access Request · Certification Campaign · Certification Line |
| SoD Testing | + New SoD Test Run | SoD Test Run · SoD Control · SoD Exception |
| Data Protection | + New Sensitive Field | Sensitive Field · Encryption Key |
| Monitoring & Audit | + Report a Security Incident | Security Incident · Privileged Session · Vulnerability |

The Vulnerability chip opens its form. No records were created on fix_real.

## Follow-up: Provision a New Login (same day, user request)

**The user's report:** on the M29 Users screen (`function wise check/m29/user.pdf`), there was no way to enter a new user.

**Investigation corrected an assumption in this audit.** Onboarding publishes `employee.joined`, and the identity-lifecycle service, which is running and healthy, creates only the **Keycloak** account. It never creates an Odoo login. Odoo sign-up is set to `b2b` (invitation only), so SSO does not auto-create logins either. 0 users have ever signed in by SSO; all 344 logins came from the migration. Before this change, a login could only be made in the Odoo back end.

**Built (FR-SEC-001/027, AUT-SEC-01):**
- **"+ Provision a New Login"** appears on the Users list, through a new engine option `newForm` that lets a list name the form which creates its records. It is also the "+" of the Identity & MFA page. It is a joiner event in four tabs:
  1. **Person:** an employee picker offering only the 194 employees with no login, plus the login to be created (the work email, following the estate convention: all 310 linked logins equal the work email).
  2. **Roles & Permissions:** a main role plus any additional roles.
  3. **Data Scope:** the allowed operating units and the default unit.
  4. **What This Grants:** a computed preview of every role's permission groups, the scope, and any **duty conflict** between the chosen roles.
- **Apply:** a second Access Approver, who is neither the filer nor the person, applies the event. It:
  - creates the login with internal-user access only;
  - links it to the employee;
  - grants **every** role through the SoD gate;
  - sets the data scope;
  - **queues** the standard "set your password / sign in" invitation, so it is never sent inside the click;
  - writes a `joiner_login` audit row.

  A login that already exists is refused rather than duplicated, as is an employee with no work email. A refused grant or a blocked duty pair undoes everything: no partial login is left behind.
- The JML form gained the same roles, scope and preview fields, so movers can change scope too.

**Evidence:**
- 7 new live tests run as non-admin users: end-to-end provisioning, existing-login refusal, missing work email, rollback on a refused grant, preview of a blocked pair with refusal, and the picker filter. Together with both M29 guards and both existing M29 suites: **216/216 green** on fix_test.
- Deployed: `-u cd_rbac_ext` on fix_real (clean); drift 0 after the M31 session deployed its own Workshop schema; 8069 relaunched 11:09 with the user's approval.
- Live on bundle `8b00a02`: the Users screen shows "+ Provision a New Login", the 4-tab form opens, and the picker returns exactly 194 employees. No records were created on fix_real.

**Notes:**
- The invitation email goes through fix_real's configured mail server, which is Mailpit (no real delivery) until a real SMTP is set.
- Applying needs a second Access Approver. fix_real has one Access Approver plus the administrator.
- 4 login-less employees have a work email that is already another user's login. They will be refused with that login named, and must be linked by hand.

## Round 2: the New User form, rebuilt (user feedback, same day)

**Feedback:** "not looking professional; make it multi-tab with a detailed permission checklist (access, deny, read, edit, write, print…), as a top-class ERP does."

**Research (how leading ERPs do it):**
- **Dynamics 365 F&O:** users get roles; roles bundle duties; duties bundle privileges. The administrator reviews *effective* permissions before go-live ([Microsoft Learn: role-based security](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/role-based-security)).
- **NetSuite:** each permission is a level on one ladder: None, View, Create, Edit, Full. Print comes with View; export is its own permission ([Oracle: access levels for permissions](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N326341.html)).
- **SAP S/4HANA:** business roles grant access; restrictions (Write / Read / Value Help) narrow it by organisational value ([SAP Community: using restrictions](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-sap/using-restrictions-to-enhance-user-authorizations-in-the-sap-s-4hana-cloud/ba-p/13575978)).
- **Odoo:** a per-application level picker on the user's Access Rights tab ([Odoo docs: access rights](https://www.odoo.com/documentation/18.0/applications/general/users/access_rights.html)).

**What was built.** "New User" opens from **+ Provision a New Login** on the Users list and as the Identity & MFA "+". It has six tabs:

| Tab | Captures |
|---|---|
| 1. Person | Employee (only those without a login; the approver picks by name without needing HR rights) and start date. Read-only HR card: code, job, department, unit, manager, phone. Login (work email), interface language, time zone. |
| 2. Roles | Main role, additional roles, business justification (required) |
| 3. Data Scope | Allowed operating units, default unit |
| 4. Module Permissions | A **one-click preset** ("Everything the roles allow" / "View only, in every module" / "No access anywhere"), then a **checklist** with one row per module the roles reach. Each row shows Business Area, Module, **Roles Allow** (computed from the real access rules), **Access Level** (No access / View / Create / Edit, a ladder) and **Approve / Print / Export / E-mail** checkboxes. |
| 5. Validity & Security | Access Valid Until: a daily job deactivates the login after that date, the same way a leaver is deprovisioned. Sign-in and MFA explained. |
| 6. Review & Approval | Access summary covering role-by-role permission groups, scope, the checklist tally, denied modules and **duty conflicts**. Shows the approval stamp and what was done. |

**Enforcement, not decoration:**
- The checklist can only **narrow** what the roles grant; asking for more is refused with "add a role". That is the SAP / D365 model.
- When the event is applied, each narrowed module becomes a `fix.module.permission` row.
- The workspace server checks it on **every** request: view (lists, forms), create and edit (saves), approve (workflow actions), print (PDF), export (Excel/CSV) and e-mail (reports and lists).
- A mover replaces the person's previous narrowing.
- The narrowed rows are listed on Identity & MFA › **Module Permissions**.

**Usability details:**
- Short ladder labels, so nothing is truncated.
- Single-line rows.
- Read-only multi-line values keep their line breaks (`.d365-ro { white-space: pre-line }`).
- Every tab has a step note ("Step n of 6") in plain language.

**Evidence:**
- 43 live tests in `test_m29_capture_live.py`, run as non-admin users. They cover:
  - checklist fill;
  - refusal above the roles;
  - narrowing applied and enforced (denied module refused for the person, not for others);
  - view-only blocking create, edit, approve, print and e-mail but not reading;
  - mover replacement;
  - language, time zone and end date applied, with expiry deprovisioning;
  - the one-click preset;
  - the employee card.
- 35 node checks in `test_m29_capture_buttons.py`. Together, 76/76 green.
- Clicked through on a private fix_test preview (port 8075) as an Access Approver with no HR rights: pick a joiner, choose a role, save → 61-module checklist; preset View → M04 raised to Create → save → summary "Create 1, View 60 - 41 narrowed".

## Gaps left (no model, or an owner decision)

- **Cross-border transfer control** (FR-SEC-049, BRU-SEC-14, `fix.residency.transfer`): no model. It waits on the legal opinion the spec itself raises (Q-01, DEP-31, D-13, the 2026 localisation amendment). It was not built, because a register with no transfer mechanism behind it would only be paperwork.
- **Device trust / MFA enrolment / service accounts** (FR-SEC-010/004/012): these are L4 (Keycloak) and Odoo `res.device` data, and nothing on the Identity page is typed for them. Forced session revocation is a possible row action and is not built.
- **Delegation** (FR-SEC-019) exists as `fix.approval.substitution` in the workflow engine (M63), not on an M29 page.
- **People:** on fix_real, Security Officer and Access Approver each have **one** holder, and Key Custodian has **none**. With one officer, a vulnerability can be remediated by its owner but no second officer can verify a fix that same officer made. Incident severity changes and risk acceptances likewise need two officers. Name a second Security Officer and a Key Custodian.
- Sensitive Field, Field Rule, Isolation Tier, Model Access and Record Rule can be created by system administrators only (ACL). For those, the chips are admin captures by design.
- fix_real currently has 0 JML events, 0 incidents, 0 privileged sessions and 0 vulnerabilities. 194 active employees have no login; they get one through onboarding, not from this page.
