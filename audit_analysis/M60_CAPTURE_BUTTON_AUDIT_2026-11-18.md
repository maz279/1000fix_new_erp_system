# M60 Governance, Risk & Compliance: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M60 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_Governance_Risk_and_Compliance.md`. Sections used:
  - §3: the 25 in-scope capabilities and the boundaries (M29 enforces SoD, M24 executes retention and holds, M23 owns CAPA);
  - §5: FR-GRC-001 … 044;
  - §8: the risk, control-test and obligation-occurrence lifecycles and their transition guards;
  - §9: BRU-GRC-01 … 22;
  - §10.1: the 32 owned entities;
  - §13: roles, tier T5 (legal, breach, whistleblowing), SOD-21/22.
- Code:
  - `cd_p03_portal/static/src/a10/m60.js`: the page registry (8 sub-module pages);
  - `cd_p03_portal/controllers/a10/m60.py`: surfaces, reports and KPIs;
  - `cd_grc/models/*.py`: risk register and appetite, controls and control tests, compliance frameworks and obligations, audit findings, SoD rules, the derived authority register, licences, policies, legal matters, PDPA requests, whistleblowing.
- Live data (fix_real, read-only count on 18 Nov): **no M60 record at all** (0 risks, appetite statements, controls, tests, SoD rules, obligations, frameworks, licences, policies, legal matters, PDPA requests, whistle reports). Only the derived authority register (14 rows) and M29's 63 SoD controls exist. Every cd_grc role group has exactly one holder.

## 1. What was there (HEAD 32e24dc9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Risk Register | Risk | Risk, Risk Appetite | **No dated assessment** (FR-GRC-003/005, T-01, BRU-GRC-03 H "assessments are versioned; a prior assessment is never overwritten"): a rescore overwrote the risk's likelihood and impact in place, so "what did we think last March, and who said so" was unanswerable. **No treatment action** with an owner and date (FR-GRC-004 P0); only a free-text "mitigation". **No realised risk event** (FR-GRC-007). The Risk Appetite list sat on no page. |
| 2 | Control Framework & Testing | Internal Control | Control Test | No "Internal Control" chip. The control had **no objective, nature (manual/automated) or key-control flag** (FR-GRC-011/012 P0), so the testing programme could not be scoped to key controls (KPI-C60-02). Deficiencies are raised as an NCR + CAPA in M23 by a failed test (kept: M23 owns CAPA). |
| 3 | SoD & Authority | SoD Rule | **none** | **No chip at all.** SoD tests (FR-GRC-019 P0) and time-boxed exceptions (FR-GRC-020 P0) existed only in M29; the M60 rule **named no control that enforces it**, so nothing showed whether a rule was enforced or tested (BRU-GRC-09/11). |
| 4 | Compliance Obligations | Compliance Obligation | Licence | **No obligation occurrence** (FR-GRC-024/025 P0, BRU-GRC-12/13 H): an obligation could not be discharged with evidence, verified, or recorded as breached; only a review-date nag existed. The obligation had **no owner, recurrence, lead time or consequence**. No regulatory change log (FR-GRC-026). No Compliance Framework chip. |
| 5 | Policy Governance | Policy | Policy | **No acknowledgement record** (FR-GRC-030): the Attestation Status report itself said "per-employee attestation sign-offs are not stored". No policy exception (FR-GRC-031). No retention policy chip (FR-GRC-032, M24 enforces). |
| 6 | Legal & IP | Legal Matter | **none** | **No chip at all.** No legal hold instruction (FR-GRC-039 P0); no IP register (FR-GRC-028); the matter had no provision or next action (FR-GRC-038). |
| 7 | PDPA Governance | "PDPA Register Entry" | **none** | **No chip at all.** No record of processing activities (FR-GRC-033 P0, BRU-GRC-16/17 H), no cross-border transfer register (FR-GRC-034 P0, BRU-GRC-18 H), no breach register (FR-GRC-036 P0), no privacy impact assessment (FR-GRC-037). The one form was titled and described as a **processing record** ("purpose, legal basis and retention") but captured a **data-subject request**, and let the user type the request's reference number. |
| 8 | Whistleblowing | Whistleblow Report | Whistleblow Report | None. |

Guard `cd_p03_portal/tests/test_m60_capture_buttons.py` on HEAD: **29 of 52 tests fail** — pages 1, 3, 4, 5, 6 and 7 miss captures; the three pages with no chip; the mislabelled PDPA form and its typed reference; creatable lists with no capture; a working screen on no page; the 12 missing registers, their security and their load order.

## 2. What was built

### Backend: `cd_grc` 19.0.0.2.0, new file `models/fix_m60_capture.py` (imported last)

Stamps, decisions and derived figures are guarded fields, never typed through a form. Every decision is taken by someone other than the person who raised it.

| Page | Record | Rules |
|---|---|---|
| 1 | `fix.risk.assessment` (FR-GRC-003/005, T-01) | Made by a Risk Owner or Compliance Officer only (BRU-GRC-01). **Refused until the appetite of the risk's category is stated (BRU-GRC-02).** Stamps who assessed, when, the controls relied on and the residual it replaces; carries the scores and the next review date onto the risk. **Never rewritten or deleted (BRU-GRC-03)**: a rescore is a new row. |
| 1 | `fix.risk.treatment` (FR-GRC-004) | Strategy (mitigate / transfer / avoid / accept), rationale, action, owner, due date, target residual. Decided by a Risk Owner or officer; puts an open risk under treatment; gives the owner a to-do. **A transfer names its instrument** (policy or contract clause, §8.1 guard). Only the action owner (or officer / risk owner) edits or completes it; **completion needs a note of what was done and where the evidence is**; only an officer cancels, with a reason. |
| 1 | `fix.risk.event` (FR-GRC-007) | Any employee records a realised loss, incident, claim, non-conformance or breach on the risk it realised; kept as reported; the risk owner gets a "reassess" to-do, and a loss, claim or breach on a risk scored below Major impact is flagged as challenging the assessment. |
| 2 | `fix.control` (extended) | Objective, nature (manual / automated / hybrid) and **key-control** flag (FR-GRC-011/012); the form now maps the obligations a control discharges (FR-GRC-013). |
| 3 | `fix.grc.sod.rule` (extended) | Names the **M29 SoD control that enforces it** and its test method, and shows that control's latest measured run — or "Not enforced" (FR-GRC-018/019, BRU-GRC-11). M29's own SoD Test Run and SoD Exception forms are the page's chips (M60 tests and governs; M29 enforces — no second engine). |
| 4 | `fix.compliance.obligation.occurrence` (FR-GRC-024/025) | One due instance per obligation and period, scheduled by an officer; the owner gets a to-do. **A discharge without evidence (an uploaded file or a filing reference) is recorded as a control failure, not a discharge (BRU-GRC-12)**; verified by an officer **other than the discharger**; **a missed occurrence is recorded as a breach with its consequence, never quietly closed (BRU-GRC-13)**; "not applicable" needs a justification. |
| 4 | `fix.compliance.obligation` (extended) | Owner, source type, recurrence, advance notice, consequence of breach (FR-GRC-023). |
| 4 | `fix.grc.regulatory.change` (FR-GRC-026) | Logged by the officer with source and effective date; affected obligations and controls; the impact assessment is the officer's act. |
| 5 | `fix.grc.policy.attestation` (FR-GRC-030) | **The employee's own acknowledgement of the current version** of an approved policy that requires attestation, stamped with the employee, version and time; one per employee per version; a signed paper copy is recorded only by an officer; never edited or deleted. The policy shows its acknowledgement count, and the **Attestation Status report now shows acknowledged / outstanding / rate** instead of "not stored". |
| 5 | `fix.grc.policy.exception` (FR-GRC-031) | Justification and compensating control, **at most 365 days**; decided by an officer **who did not request it**; a daily job expires it on its date (never extended silently). |
| 6 | `fix.grc.legal` (extended) | Provision, next action and due date, and what must be preserved (FR-GRC-038/039). The **Place Legal Hold** chip is M24's own form (M24 executes holds); the page lists the holds. |
| 6 | `fix.grc.ip.asset` (FR-GRC-028) | Trademarks, domains, software licences held, copyrights, designs; renewal flagged 60 days ahead; kept by Legal Counsel or the officer. |
| 7 | `fix.grc.processing.activity` (FR-GRC-033, BRU-GRC-16/17) | Purpose, lawful basis, data and subject categories, recipients, retention, safeguards, systems, owner. **In force only with retention and safeguards, and a high-risk activity only with an approved PIA**; never deleted (retire it). |
| 7 | `fix.grc.data.transfer` (FR-GRC-034, BRU-GRC-18) | Destination, recipient, basis, safeguards; **approved only over an activity in force, by an officer who did not request it**; suspension needs a reason. |
| 7 | `fix.grc.data.breach` (FR-GRC-036, BRU-GRC-20) | **Readable only by the Compliance Officer and Legal Counsel** (no plain-user ACL row). Contained only with the containment written; **closed only by an officer, with the assessment, the notification decision (contractual parties included) and who was notified**; never deleted. |
| 7 | `fix.grc.privacy.impact` (FR-GRC-037) | Risks, mitigations, residual risk; approved by an officer **who did not author it**; a high residual is not approved. |
| 7 | `fix.grc.pdpa` form | Retitled **Data Subject Request** with an accurate description; the reference is numbered on save, no longer typed. |

Security and data: ACLs (plain users read the registers and report events; officers keep the PDPA registers; nobody deletes any new record); company / operating-unit isolation rules from `generate-isolation-rules.py` (only the cd_grc file kept; the generator's drift in seven other modules was reverted); sequences PEX/, XBT/, BRCH/, PIA/; the daily policy-exception expiry job.

### Workspace: `cd_p03_portal/static/src/a10/m60.js`, `controllers/a10/m60.py`

- 16 new list screens on the nav (Risk Assessments, Treatment Actions, Risk Events, SoD Test Runs, SoD Exceptions, Obligation Calendar, Regulatory Changes, Policy Attestations, Policy Exceptions, Retention Schedule, Legal Holds, IP Register, Records of Processing, Cross-Border Transfers, Breach Register, Privacy Impact Assessments) with their workflow actions; every decision asks for its reason.
- 12 new two-tab forms; 6 existing forms gained the spec fields.
- Every page names its chips explicitly. Reused, not duplicated: M29 SoD Test Run and SoD Exception, M24 Place Legal Hold and Retention Policy.
- 12 new served surfaces; the A10 writable map regenerated (`form_fields.py --a10`).

| Page | "+ New" | Chips after |
|---|---|---|
| 1 Risk Register | Risk | Risk, Risk Appetite, Risk Assessment, Risk Treatment, Risk Event |
| 2 Control Framework & Testing | Internal Control | Internal Control, Control Test |
| 3 SoD & Authority | SoD Rule | SoD Rule, SoD Test Run, SoD Exception (delegated authority stays derived: no typed entry) |
| 4 Compliance Obligations | Compliance Obligation | Compliance Obligation, Compliance Framework, Obligation Occurrence, Licence, Regulatory Change |
| 5 Policy Governance | Policy | Policy, Policy Attestation, Policy Exception, Retention Policy |
| 6 Legal & IP | Legal Matter | Legal Matter, Place Legal Hold, IP Asset |
| 7 PDPA Governance | Data Subject Request | Data Subject Request, Processing Activity, Cross-Border Transfer, Data Breach, Privacy Impact Assessment |
| 8 Whistleblowing | Whistleblow Report | Whistleblow Report |

### Not built (stated, not hidden)

- **Insurance register and claims** (FR-GRC-040/041), **third-party risk** (FR-GRC-042) and **business continuity** (FR-GRC-043) belong to none of the eight registry pages (the page list is the frozen registry). Asset insurance already exists in M49 (`fix.asset.insurance`) and supplier risk in M42 (`fix.supplier.risk`); an enterprise insurance register would duplicate M49 and needs an owner decision.
- **Automated control testing by declared query** (FR-GRC-014, T-02) and the **annual control attestation** (FR-GRC-022, P2) are engines, not captures.
- **Deficiency rating** (deficiency / significant / material weakness, FR-GRC-017) stays with the M23 NCR/CAPA a failed test already raises.
- No GRC data was invented on fix_real: every register starts empty.
- **Owner gap:** on fix_real every cd_grc role (Compliance Officer, Risk Owner, Legal Counsel, Control Testing Officer, CFO, Audit Committee, Investigator) is held **only by `admin`**. Each two-person rule here (a transfer, PIA, policy exception or discharge is decided by an officer who did not raise it) therefore cannot complete until at least two real people hold the Compliance Officer role. Appointing them is the owner's decision (role grants go through M29).

## 3. Evidence

Measured on a private clone `fix_test_m60` (of `fix_test`, upgraded `-u all` with the worktree code, 166 modules, 0 errors) and a private server; the live 8069 / fix_real was not touched.

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m60_capture_buttons.py` (engine's own `fregCreate` / `fregPanels` in node) | **52/52** (HEAD: 29 failed) |
| Estate page standard `test_estate_module_pages.py` (all 67 modules) | green |
| Live ORM `cd_grc/tests/test_m60_capture_live.py` (non-admin users, real P03 endpoints) | **16/16** |
| Whole `cd_grc` suite on the clone | 74/77. The 3 failures (`test_a12_grc_handoffs.py`: escalated project risk -> register entry via `cron_relay`) fail **identically with this change switched off** on the same database: pre-existing, not M60's. |
| Mutation check: 16 defects re-introduced one at a time (appetite gate, overwritable assessment, transfer instrument, evidence-less discharge, self-verification, early breach, paper attestation by anyone, requester decides exception, untimeboxed exception, PIA gate, transfer over inactive activity, breach closed without decision, stale SoD result, page 7 / page 3 chips dropped, PDPA reference typeable) | **16/16 red** (the last one survived the first run; the guard was tightened) |
| Server probe from the page (`/p03/model/records`, `/form`, `/report` for the 8 page grids and every list, form and report on the pages) | **71 calls, 0 errors**; 28 chip forms, **0 fields dropped** by the server; the evidence field is served as an upload |
| Click-through under `?debug=assets` | Page 5 shows "+ New Policy" and 4 chips; the Policy Attestation chip opens a two-tab form. Page 7 shows "+ New Data Subject Request" and 5 chips; a Processing Activity was **created through its form (Saved, Draft) and put in force through the list action** (stamped Administrator). |

Bugs the live tests caught and that were fixed before commit: the policy-exception expiry job compared against the UTC date (up to 6 hours behind Dhaka, so an exception outlived its day); the SoD rule's "latest test" kept a stale value after its enforcing control was named.

## 4. State

- Code committed on `fix/m60-capture-buttons` (worktree `1000 fix/m60cap-wt`), based on 32e24dc9; the shared tip has since moved to 00326139 (M20 document files only, no overlap). **Not landed, not deployed, not pushed.**
- Deploy needs: land on the shared branch, then `-u cd_grc,cd_p03_portal` on fix_real (and fix_dev), then one 8069 / 8090 restart (new models and controllers). Peers M59, M61-M65 are auditing in parallel; M61 shares `controllers/a10/writable.py` — regenerate it (`form_fields.py --a10`) if it conflicts.
