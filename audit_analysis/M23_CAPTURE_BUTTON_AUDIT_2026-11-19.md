# M23 Quality Management (ISO) — capture-button audit (19 Nov 2026)

**Question.** Not every M23 sub-module page has a relevant data capture button. What should each page capture, what does the codebase do, and what was fixed?

**First pass.** M23 had never had a capture audit. All eight pages carried a "+ New" since the 12 Nov estate page standard, so this pass asked the sharper question the later module passes ask: **does each page capture the records its spec functions need, and does each button capture what it says?**

**Sources checked.**
- The spec: `1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23_Quality_Management_System.md` — §5 FR-QMS-001..048, §8 lifecycles and transition guards, §9 BRU-QMS-01..20, §10.1 owned entities, §11 automations.
- The workspace: `cd_p03_portal/static/src/a10/m23.js` (8 sub-module mappings) and `controllers/a10/m23.py`; the engine's own `fregCreate` / `fregPanels` evaluated in node as the browser runs them.
- The models: `cd_qms_process` (`fix_qms.py`, `fix_qms_ops.py`); M60's `fix.audit.finding` (control audits) in `cd_grc`.
- Live data, read-only: `fix_real` holds 0 NCRs, CAPAs, audits, policies, processes, reviews and CoPQ rows; 3 checklist templates, all **published** with a typed item count (14, 9, 22) and **no item recorded anywhere**; 2 quality gates. `fix_dev` is similar (4 checklists, 1 certification, 4 CoPQ rows).

## 1. Each page: what it should capture, what it did, verdict

| # | Sub-module (spec) | Before (HEAD a6ca660a) | Verdict |
|---|---|---|---|
| 1 | Policy & Objectives (FR-QMS-001/002) | + New Policy & Objective; **no chip**. One record held one objective; nothing cascaded an objective to a branch, process or role, and no objective had a measurement basis. | **Partial** |
| 2 | Process Register (FR-QMS-003/004/005/010) | + New QMS Process; **no chip**. The form hid `outputs` and the process KPI the model holds; no purpose, interactions, controls, review date or work instruction. **No change could be assessed for QMS impact before release** (BRU-QMS-10, hard block). | **Gap** |
| 3 | Checklists & Gates (FR-QMS-011..016) | + New Checklist Template; **no Quality Gate chip** although the page lists gates. **A template had no items** — only a typed count — so no criteria, response type or evidence requirement could be authored (FR-QMS-011/016, P0); a published template could be edited in place (BRU-QMS-03); no applicability rules (FR-QMS-013) and no independent-inspection rule on a gate (FR-QMS-015). | **Gap** |
| 4 | NCR Management (FR-QMS-021..025, 031) | + New NCR. Sources limited to 5 of the 10 the spec names (no rework, external audit, claim rejection, seller, safety referral, staff report); no type, no ISO clause affected; containment was free text with **no owner or deadline** (FR-QMS-024); no photo. The form let the root cause be typed. | **Partial** |
| 5 | RCA & CAPA (FR-QMS-026..039) | + New CAPA. The "RCA (5-Why / 8D)" list was **the NCR list** with a typed root cause and a "Set Root Cause" prompt: no 5-Why, Ishikawa or 8D record, nothing kept the root cause apart from the symptom (BRU-QMS-04, hard) and nothing required 8D for a major NC (BRU-QMS-14, hard). A CAPA had **no action plan** (FR-QMS-033) and no observation window (FR-QMS-035). The CAPA form let anyone type "Implemented by", which the verifier-independence check reads. | **Borrowed / Gap** |
| 6 | Audit Programme (FR-QMS-040..046) | **"+ New Audit Finding" opened an internal AUDIT**, and the "Audit Finding" chip opened the same audit form. **A finding could not be recorded at all** (major / minor / observation / OFI with clause and evidence, FR-QMS-043). No annual programme (FR-QMS-040), no auditor register or independence beyond process ownership (FR-QMS-041, BRU-QMS-07), no evidence release (FR-QMS-046, BRU-QMS-15), and the certification form existed but had no chip. | **Mislabelled / Gap** |
| 7 | Management Review (FR-QMS-047) | + New Management Review; Review Action chip; inputs pulled, actions tracked (A10 P1-6). | OK |
| 8 | Statistics & CoPQ (FR-QMS-029/030/048) | **"+ New Qms Copq"** — a triage placeholder title, under a nav group "Record Coverage" with a screen called "Qms Copq" in both languages. A CoPQ entry named **no non-conformance and no attributed cause** (FR-QMS-029/030). | **Placeholder** |

## 2. What was changed

### New records (`cd_qms_process/models/fix_qms_capture.py`, module 19.0.0.2.0)

| Page | Record | Rules it enforces |
|---|---|---|
| 1 | `fix.qms.objective` | Measurable (basis, target, actual, unit, period, owner); attainment computed, including lower-is-better objectives such as the rework rate; cascades from a parent of the same policy year to a branch, process or role, each scope naming its subject; no cycle. |
| 2 | `fix.qms.change.assessment` | BRU-QMS-10: assessed with a recorded impact; **released only by the Quality Manager and only when every affected document, checklist and training item is ticked updated**; frozen once released or rejected. |
| 3 | `fix.qms.checklist.item` (grid on the template) | Response type, acceptance criteria (required for a measurement or reading), evidence required, "failure raises NCR". **A template with no item is not published; a published version's items and header are frozen** (BRU-QMS-03) and change through **New Version** (QM), which copies the items onto a draft `version + 1` and leaves the executed version untouched. |
| 5 | `fix.qms.rca` | 5-Why (≥ 3 whys), Ishikawa (≥ 1 category) or 8D (all eight disciplines). **Root cause required and must differ from the symptom** (BRU-QMS-04); **a major or critical NCR is investigated by 8D** (BRU-QMS-14). Completing it lands the root cause on the NCR (new → root cause), or revises it after a failed verification. |
| 5 | `fix.capa.action` (grid on the CAPA) | Owner, due date, executing module. Done by its owner or the QM with evidence; an action executed in M22/M24/M60/M42/M12/M01 names the record there (BRU-QMS-18). **A CAPA is implemented only when every action is done.** |
| 6 | `fix.qms.audit.programme` | Annual plan (processes, branches, supplier/seller classes, frequency); approved by the QM; shows audits planned and processes without an audit. One per company and year. |
| 6 | `fix.qms.auditor` | Kept by the QM: standards, competence evidence, own area and own work. **Once a company registers an auditor, an audit is assigned only to an active registered auditor who is independent of the branch and the processes in scope** (BRU-QMS-07, AUT-QMS-13), on create and on reassignment. |
| 6 | `fix.qms.audit.finding` | Major / minor / observation / OFI with clause, statement and objective evidence; recorded only while the audit is executed; a non-conformity raises its NCR (source audit, linked both ways); **the audit report raises any still missing** (AUT-QMS-14), so the existing journey opens the CAPA of a major. An observation/OFI is closed by the QM with a note; a non-conformity closes when its NCR does. |
| 6 | `fix.qms.evidence.release` | BRU-QMS-15: released to an external auditor only after approval by **a Quality Manager other than the one who recorded it**, with the evidence attached; each release is logged; what was approved cannot be changed. |

### Fields and actions on existing records
- **NCR**: six more sources, `nc_type`, `clause_ref`, containment owner / due date, **Confirm Containment** (stamps who and when), photo/evidence upload, link to its audit finding.
- **CAPA**: `observation_window_days`; `verification_due_on` is stamped at implementation and **verification is refused before it** (FR-QMS-035). A window of 0 keeps today's behaviour.
- **Process**: purpose, interactions, controls, next review, work instruction (M24 document); the form now shows outputs and the KPI.
- **Checklist template**: applicability (device category, brand, repair level, value band, delivery mode, customer type, branches). `item_count` is now **counted from the items** — the three live templates will read 0 until their items are authored (on a New Version, since they are published).
- **Quality gate**: independent inspection, value threshold and risk basis.
- **Internal audit**: a reference number (IA/…), programme, audited processes on the form, findings grid, auditee acknowledgement.
- **CoPQ**: NCR, attributed cause, attribution basis (required once a cause is attributed).

### Workspace (`a10/m23.js`, `controllers/a10/m23.py`)
- Page buttons and chips (evaluated with the engine): see §3.
- The typed **"Set Root Cause"** row action and the root-cause input left the workspace; a person establishes the root cause through a completed RCA. The model method stays for system hand-offs (M60's failed control test raises its NCR and CAPA through it).
- "Implemented by" on the CAPA form is now read-only (it is stamped by Implement).
- The **Open Audit Findings** KPI now counts open process-audit findings as well as M60's control-audit findings; the Audit Programme report counts the audit's own findings and shows its reference.
- New lists: Quality Objectives, Process Change Assessments, Checklist Items (read-only register), RCA (now `fix.qms.rca`), CAPA Action Plan, Annual Audit Programme, Audit Findings, Auditor Register, External Evidence Releases; "Qms Copq" became **CoPQ Ledger** under Analytics.
- `writable.py` regenerated by `form_fields.py --a10`; isolation rules regenerated for `cd_qms_process` only.

## 3. Result per page (engine-evaluated)

| # | "+ New" | Chips |
|---|---|---|
| 1 | Policy & Objective | Quality Objective |
| 2 | QMS Process | Process Change Assessment |
| 3 | Checklist Template (with Items grid) | Checklist Template, Quality Gate |
| 4 | NCR | NCR |
| 5 | CAPA (with Action Plan grid) | Root-Cause Analysis, CAPA |
| 6 | **Internal Audit** | Internal Audit, Audit Finding, Audit Programme, Auditor, Certification / Surveillance, Evidence Release |
| 7 | Management Review | Review Action |
| 8 | **CoPQ Entry** | CoPQ Entry |

## 4. Evidence

- **Static guard** `cd_p03_portal/tests/test_m23_capture_buttons.py`: 32/32 green; on HEAD a6ca660a **17 red** (pages 1/2/3/5/6, the mislabel, the placeholder, the RCA list, the typed root cause, the missing grids, the typable CAPA implementer and NCR root cause, the new models' ACL/isolation).
- **Live-ORM guard** `cd_qms_process/tests/test_m23_capture.py`: 19/19 green on a private clone (`fix_test_m23c`), every rule exercised as non-admin users, and every new form saved through `/p03/model/write` (including the checklist items and CAPA action plan written with their header in one call).
- **Mutation check**: 29 mutants (23 model rules, the KPI, the typed root cause back on the surface, the finding chip back on the audit form, the items grid removed, the gate chip removed, the placeholder title back) — **29/29 red**, files byte-identical afterwards.
- **Server probe** on a private server (port 8131, worktree code, `fix_test_m23c`): every M23 list (21) and form (19) requested with exactly its declared columns/fields — 0 errors, 0 silently dropped.
- **Headless UI walk** of the 8 pages on that server: each shows the "+ New" and chips of §3, every chip opens a populated form, 0 console errors, 0 HTTP ≥ 500. Screenshot of page 6: `M23_page6_audit_programme.png`.
- **Regression** (`cd_qms_process`, `cd_grc` handoffs, `cd_cx_feedback`, A10 control suite, A10 write whitelist, KPI tiles, generic API, estate page standard): 950 passed on the first run. Its failures were (a) the clone lagging peers (`fix_device.population` missing) — cleared by `-u all` on the clone; (b) `test_register_states_move_only_through_the_quality_manager`, which published a checklist with no items — updated to add an item (an intended rule change, FR-QMS-011); (c) **7 event-relay hand-off tests** (supplier CAR → NCR, risk escalation → register ×3, survey dispatch ×3) that **fail identically on the pre-change code a6ca660a against the same database**: a test-environment fault, not this change.

## 5. Open (owner / later build)

- **Quality risks and opportunities (FR-QMS-007, P1) and organisational context / interested parties (FR-QMS-006, P1) are not built.** A systemic quality risk must escalate into M60's risk register (BRU-QMS-16); `cd_grc` depends on `cd_qms_process`, so the escalation belongs in a `cd_grc` extension. Not done in this pass.
- **8D before CAPA on system hand-offs.** M60's failed control test raises a major NCR and its CAPA through `action_set_root_cause` without an 8D record. The workspace path now requires the RCA; whether system-raised NCRs must also wait for an 8D is the Quality Manager's decision.
- **The three published checklist templates on `fix_real`** (QC Bench Check v2, Final Cosmetic & Function Check, Internal Audit Checklist) hold no items: the QM authors them on a New Version and publishes it. Quality gate QG-02 points at "Final Cosmetic & Function Check" v1.0.
- **Nobody is registered as an auditor**, so auditor independence is enforced only for process ownership until the QM registers the first auditor. Appointing Quality Managers and QMS Auditors on `fix_real` remains business decision B2.
- Not built: sampling plans (FR-QMS-017, P2), checklist result intake and failure routing from M01/M31/M02 (FR-QMS-018/019 — the existing QC-failed → NCR path stays), repeat-failure detection by root cause (FR-QMS-028; the report still groups by order/description), overdue escalation schedules (FR-QMS-038), audit-readiness dashboard (FR-QMS-009), clause-traceability index (FR-QMS-005 beyond the clause fields).

## 6. State

- Code: `f77fca97` on `fix/m23-capture-buttons`, rebased onto the shared branch at `f70e9feb`; re-tested after the rebase (static guard, QMS suite, estate page standard, A10 write whitelist: 706 passed, the one failure the pre-existing supplier-CAR relay test).
- Landed on `fix/a03-live-data-and-pending-work` by compare-and-swap and pushed with the feature branch.
- **Deployed 19 Nov 2026** as part of the combined M22/M23/M26/M27 upgrade, run by the M22 session with the owner's approval in that session:
  - backups `backups/fix_{real,dev}_pre_combined_m22_m23_m26_m27_2026-11-19.dump`;
  - `-u` including `cd_qms_process,cd_p03_portal` on `fix_real`, then `fix_dev`, exit 0;
  - one restart at 10:57: 8069 = PID 64400, 8090 = PID 77212.
- Verified read-only after the restart, on both databases:
  - `cd_qms_process` 19.0.0.2.0 installed; all 9 new tables present, as are `fix_ncr.nc_type`, `fix_capa.observation_window_days`, `fix_internal_audit.programme_id`, `fix_qms_copq.attributed_cause`, and the 5 new sequences;
  - the 3 published checklists now show `item_count` 0, the expected correction from the typed counts 14/9/22;
  - the web bundle rebuilt after the restart (10:58 / 11:00) contains `M23-form-finding`, `-auditor`, `-evidence`, `-programme`, `-rca`, `M23-checklist-items` and "CoPQ Ledger";
  - every M23 list (21) and form (19), requested from the live 8069 and 8090 servers with its declared columns and fields: 0 errors, 0 dropped.
