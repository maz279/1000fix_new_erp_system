# M59 Health, Safety & Wellbeing: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M59 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M59_Health_Safety_and_Wellbeing.md`. Sections used:
  - §3: the 19 in-scope capabilities and the boundaries (M22 delivers training, M17/M46 own the vehicle, M55 the leave, M56 the payment);
  - §5: FR-HSE-001 … 042;
  - §8: the incident and lone-worker lifecycles;
  - §9: BRU-HSE-01 … 18;
  - §10.1: the 25 owned entities;
  - §11: AUT-HSE-01 … 18;
  - §13: roles (R44 HSE Officer, R46 Occupational Health) and the health-data boundary.
- Code:
  - `cd_p03_portal/static/src/a09/m59.js`: the page registry (8 sub-module pages);
  - `cd_p03_portal/controllers/a09/m59.py`: surfaces, reports and KPIs;
  - `cd_hse/models/*.py`: hazard, JSA, incident with team / root cause / CAPA, Form 28 register, PPE item and issue, road check, lone-worker session, hazardous substance, drill, committee with members and meetings, occupational health, fitness status, lapsed-certification follow-up.
- Live data (fix_real, read-only count on 18 Nov):
  - **no M59 record of any kind**: 0 hazards, JSAs, incidents, register entries, PPE items or issues, road checks, lone-worker sessions, substances, drills, committees, health records or inspections;
  - **0 driving-licence records** (`fix.driver`), so no road check can be recorded on fix_real until one exists;
  - 504 active employees, 73 active branches;
  - each M59 role group (HSE Officer, Occupational Health, Statutory Notification Authority, Injury Compensation Approver) has 2 holders.

So every M59 flow on fix_real starts from a workspace capture: a page without the right button is a register that can never be filled.

## 1. What was there (HEAD 32e24dc9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Hazard Register & Risk | Hazard | **none** | The Safety Inspection list was on the page with **no capture**. |
| 2 | Procedures & Permits | JSA | JSA | The page named in its title neither procedures nor permits. **No safe work procedure existed** (FR-HSE-006 P1: published, linked to task types and hazards) and **no permit to work** (FR-HSE-007: authorisation and closure). |
| 3 | Incident Management | Incident | Incident Report, Anonymous Safety Report | The investigation team, root cause and CAPA lists, and their forms, **sat on no page at all**: an investigation (BRU-HSE-05) and its CAPA (BRU-HSE-06), which closing an incident requires, could not be captured from the sub-module. **No witness statement** (FR-HSE-012, T-09 "the account is preserved verbatim"). |
| 4 | Statutory Notification | Form 28 entry | none | None (the register entry is opened by the incident; a hand entry for an accident outside the system is legitimate). |
| 5 | PPE | PPE Item | PPE Issue | No chip for the PPE item itself (only the list's "+ New"). |
| 6 | Field & Road Safety | Road Check | **none** | The lone-worker and battery/chemical lists had **no capture**. A road check is refused without a driving-licence record (BRU-HSE-07), and **no M59 page reached one**: on fix_real (0 licences) no road check could ever be saved. **No right-to-stop-work record** (FR-HSE-026 P1, **BRU-HSE-10 H**: "the refusal is recorded, reviewed and carries no penalty") and **no customer-premises hazard** (FR-HSE-025 P1, AUT-HSE-17: "surface the hazard to the assigned technician" on later visits). |
| 7 | Training & Drills | Drill | **none** | The Safety Committee list had **no capture**; Committee Members and Committee Meetings **sat on no page**. **No site emergency plan** (FR-HSE-035 P1: evacuation, first-aid provision, fire equipment per site). |
| 8 | Health & Wellbeing | Health Record | Return-to-Work | **"Return-to-Work" opened the periodic-medical form** (record type defaulted to "Periodic Medical"). The Fitness for Work and Lapsed Safety Certification lists sat on no page. |

Guard `cd_p03_portal/tests/test_m59_capture_buttons.py` on HEAD: **24 of 41 tests fail.** The failures cover pages 1, 2, 3, 6, 7 and 8, the creatable list with no capture, the seven screens on no page, the Return-to-Work chip, the six missing registers, their decisions, security and load order.

## 2. What was built

### Backend: `cd_hse` 19.0.0.5.0, new file `models/fix_hse_capture.py`

Every decision is taken by someone other than the person who raised it. Stamps and outcomes are guarded fields (`fix.guarded.mixin`), changed only by their action, never typed. A record that is evidence is never deleted.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 2 | `fix.hse.procedure` Safe Work Procedure (FR-HSE-006) | Code, title, category (electrical, battery, chemical, height, road, manual handling, fire…), task type, scope, steps, hazards controlled, document, version, effective date, review date. | Prepared and submitted by an HSE Officer; **approved by another HSE Officer** (neither preparer nor submitter); returned with a reason. Scope and steps are required to submit. **Frozen once submitted**: a change is a new version, and approving it **supersedes the version in force**. Published to every employee; a draft is read only by HSE and its preparer. Never deleted once submitted. |
| 2 | `fix.hse.permit` Permit to Work (FR-HSE-007) | Type (hot work, electrical isolation, height, confined space, damaged battery, refrigerant…), activity, location, branch, field order, the person doing the work, an approved JSA or procedure, precautions, isolation points, a bounded window. | Requested by the person doing the work (HSE may raise one for a technician), **for their own work only**. Precautions are required to request it, and an electrical permit names its isolation points. The window ends after it starts and lasts at most 12 hours (setting `cd_hse.permit_max_hours`). **Authorised by an HSE Officer who neither requested it nor does the work**; the terms are fixed once requested. **Closed with a note on how the area was left.** An authorised permit past its window **expires by itself (hourly job) and HSE and the worker are told**. Read by the requester, the worker, their line manager and HSE. |
| 3 | `fix.hse.witness.statement` (FR-HSE-012, T-09) | Incident, witness (an employee, or name and contact), the statement verbatim, the signed scan; who took it and when. | Taken by HSE while the incident is open; the witness must be named. **Kept as given: never edited, never deleted**; a correction is a further statement. Read by the HSE roles only (no plain-user access). |
| 6 | `fix.hse.work.refusal` Right to Stop Work (FR-HSE-026, **BRU-HSE-10**) | Who refused, ground (unsafe premises, no PPE, unsafe tool, live electrics, height, battery/chemical, threat, weather, unwell…), what made it unsafe, field order, location; review outcome and note. | **Recorded by the technician in their own name** (or by HSE for them). **HSE Officers and the line manager get a to-do at once.** **Kept as given; never deleted.** **Reviewed by an HSE Officer who neither refused nor recorded it**, with one of three outcomes: upheld (stays stopped until made safe), made safe and resumed, or not substantiated. **No outcome carries a penalty**: the record has no penalty field, and the message on review says so. Read by the person, their line manager and HSE only. |
| 6 | `fix.hse.location.hazard` Customer Site Hazard (FR-HSE-025, AUT-HSE-17) | Customer, premises address (filled from the customer when blank), type, the hazard found, the field order it was found on, precautions for the next visit. | **Any employee reports one**; HSE is asked to confirm it. The reporter may add precautions while it is reported. **Confirmed by HSE only with the precautions**; retired with a reason; never deleted. **While reported or confirmed, every field order for that customer shows it**: computed `hse_site_hazard_ids` / `hse_site_hazard_note` on `fix.field.order`, shown read-only on M02's Field Work Order form (safety tab). Every employee reads it, so the technician sent there sees it. |
| 7 | `fix.hse.emergency.plan` Site Emergency Plan (FR-HSE-035) | Site/branch, evacuation procedure, assembly point, plan document, fire wardens, first-aiders, extinguisher count and service date, first-aid boxes, fire-alarm test date, emergency contacts, version and review dates. | Prepared by HSE; **put in force by another HSE Officer**, and only with an evacuation procedure, assembly point, at least one warden and one first-aider, extinguishers and first-aid boxes. **One plan in force per site**: putting a new version in force supersedes the old. Frozen once in force (revise to change). **A daily job flags a plan past its review date or extinguisher service date to HSE, once.** Read by every employee. |

Other backend changes:
- **Driving licence (FR-HSE-019):** the estate keeps the licence on M46's `fix.driver`, which the road check reads. HSE Officers may now create and update it too (new ACL row in cd_hse; fleet officers already could). The driver's state and suspension stay guarded by M46.
- **Security:** ACLs per role. The privacy and company rules are in a new `security/fix_hse_capture_rules.xml`, and the operating-unit rules for permits and plans come from `generate-isolation-rules.py`. Only the cd_hse output was kept; the generator's drift in six other modules was reverted.
- **Data:** sequences PTW/, WIT/, WRF/, LHZ/; the permit-expiry job (hourly) and the plan-review job (daily) in `data/fix_hse_capture_data.xml`.
- **Load order:** the new file is imported last (`# ruff: noqa: I001` tuple form).
- **Notifications** are to-dos (activities), not new domain events: spec §12.3 names `hse.work_refused` and `hse.location_hazard_flagged`, but a new event needs a schema and registry entries, so it is listed in §4.

### Workspace: `m59.js`, `m02.js`, `controllers/a09/m59.py`, `writable.py`

- Six new lists, on their pages and in the navigation: Safe Work Procedures, Permits to Work, Witness Statements, Right to Stop Work, Customer Site Hazards, Site Emergency Plans. Each comes with its actions, and every decision asks for its reason.
- Six new tabbed forms (AGENTS.md): Safe Work Procedure, Permit to Work, Witness Statement, Work Refusal, Customer Site Hazard and Site Emergency Plan. There is also a Return-to-Work form that starts a return-to-work record (Occupational Health only).
- Seven existing screens placed on their pages: Investigation Team, Root Causes and CAPA on page 3; Committee Members and Meetings on page 7; Fitness for Work and Lapsed Safety Certifications on page 8.
- "JSA & Safe Procedures" renamed to what it lists: Job Safety Analyses (JSA).
- `writable.py` regenerated with `form_fields.py --a09`: only the six new entries were added. The A02 whitelist is unchanged, because the M02 hazard note is read-only.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Hazard Register & Risk | Hazard | Hazard, **Safety Inspection** |
| 2 Procedures & Permits | JSA | JSA, **Safe Work Procedure**, **Permit to Work** |
| 3 Incident Management | Incident | Incident Report, Anonymous Safety Report, **Investigation Team Member**, **Witness Statement**, **Root Cause**, **CAPA Action** |
| 4 Statutory Notification | Form 28 entry | (none needed) |
| 5 PPE | PPE Item | **PPE Item**, PPE Issue |
| 6 Field & Road Safety | Road Check | **Road Check**, **Driving Licence** (M46 form), **Lone-Worker Check-In**, **Work Refusal**, **Customer Site Hazard**, **Hazardous Substance** |
| 7 Training & Drills | Drill | **Emergency Drill**, **Emergency Plan**, **Safety Committee**, **Committee Member** |
| 8 Health & Wellbeing | Health Record | **Occupational Health Record**, Return-to-Work (**now a return-to-work record**) |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m59_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. It also checks every list action against the surface, every new list column and form field against the model, the whitelist against the forms, and that no stamp or decision is writable. | **HEAD 32e24dc9: 24 of 41 fail.** After: **41/41.** |
| Estate page standard (all 67 modules), M02 capture guard (after adding the site-hazard note to the Field Work Order form) and sub-module mapping. | **677/677** with the M59 guard; the M02 guard + estate pages re-run after the M02 change gave **630/630**. |
| Live tests `cd_hse/tests/test_m59_capture_live.py` on a private clone `fix_test_m59` (TEMPLATE fix_test, `-u all` exit 0, then `-u cd_hse,cd_p03_portal` exit 0 with no ERROR). They run as freshly created non-admin users: two HSE Officers, a technician, a colleague and a line manager. Workspace saves go through the real `/p03/model/write`. | **17/17.** The first run caught a real defect, fixed before this result: a witness statement naming no witness at all was accepted, because `@api.constrains` does not run on create when its fields are absent. The check now also runs in `create()`. |
| Mutation check: 24 rules removed one at a time. Procedure: approver differs from preparer, frozen after draft, approval supersedes, needs scope and steps. Permit: own work only, authoriser is not a party, precautions, isolation points, bounded window, terms fixed, expiry. Witness: named, verbatim, never deleted. Refusal: own name, independent reviewer, immutable account, manager told, never deleted. Site hazard: precautions to confirm, shown on the next field order while reported. Plan: other officer, needs a warden, flagged once. | **24 of 24 turned the live tests red**; the source was restored byte for byte (sha256 checked). |
| Regression on the same clone: every `cd_hse` and `cd_vehicle_ext` test, the A09 control suite (every workflow field guarded, every guarded field refuses a direct write, no form offers one), the A09 and A02 write whitelists, the P0 people controls, and the M59, M02, estate and mapping guards. | **1,407 tests: 1,406 passed, 1 failed.** The failure (`test_the_safety_lapsed_event_reaches_the_consumer_through_the_relay`) **fails identically with the HEAD 32e24dc9 code on the same database**. It is the event-outbox relay class that earlier audits (M51, M57) recorded, and it is not touched here. |
| Workspace UI on a private server (port 8097) over the clone, signed in as admin. | The M59 home lists the six new screens as LIVE. **Page 6 now shows six captures** (Road Check, Driving Licence, Lone-Worker Check-In, Work Refusal, Customer Site Hazard, Hazardous Substance); before, it showed none. A **work refusal was saved from its tabbed form** (`WRF/2026/0136`, state Recorded, in the user's own name, confirmed in Postgres). **Return-to-Work opens with record type "Return to Work".** No server error from M59 (the one log error is an unrelated AR cron on the clone). |

## 4. Not built here (owner decisions, other modules, or the technician app)

- **Pre-job safety check (FR-HSE-008)**, **panic alert multi-channel delivery (T-03)** and **offline hazard reporting (T-01)** are technician-app (P02) behaviours. The panic path already reaches HSE (M02 audit, 13 Nov); a P02 checklist is app work, not a workspace capture.
- **Investigation timeline and evidence pack (FR-HSE-012):** witness statements are now records. The timeline and photo/voice evidence remain the incident's description, findings and chatter attachments.
- **Journey risk (FR-HSE-021), heat controls (FR-HSE-027), equipment safety register (FR-HSE-034), electrical test records (FR-HSE-029):** these are P2 items, or are coordinated with M17/M45 (equipment and calibration registers). They are not captures this audit could own.
- **Wellbeing and assistance (FR-HSE-041, P2, BRU-HSE-18 aggregate only):** this needs an owner decision on the assistance provider. No individual record should exist.
- **Domain events** `hse.work_refused`, `hse.location_hazard_flagged` (spec §12.3): notification is by to-do today. Publishing them needs event schemas and registry entries; it is a follow-up for the integration owner.
- **Data:** fix_real holds no M59 record, no driving licence, no committee and no emergency plan. The registers are now capturable, but filling them is a take-on for the HSE Officers: procedures, site plans, committees and licences.

## 5. State

**Built and verified in worktree `1000 fix/m59cap-wt`, branch `fix/m59-capture-buttons` (from 32e24dc9). Not landed on the shared branch, not deployed.**

- The shared branch has since moved to 00326139 (commercial document title band), with no file overlap.
- `writable.py` must be regenerated after a rebase (`form_fields.py --a09`).
- **Deploying** means `-u cd_hse,cd_p03_portal` on fix_real, plus one 8069 restart. The new models, surfaces and controllers need the restart, so it must be coordinated with the peer sessions deploying at the same time. fix_dev (8090) is the same, separately.
- After deploy, fix_real will still hold no M59 records. The HSE Officers' take-on (licences, procedures, site plans, committee) is what fills the registers.
