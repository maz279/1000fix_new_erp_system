# M06 Data Services & Recovery: data-capture button audit, second pass

**Date:** 18 Nov 2026 · **Branch:** `fix/m06-capture-pass2` (worktree `m06cap2-wt`, from `6deb4dca`) · **Status:** built and tested on a private test database (`fix_test_m06c2`); see §6 for commit and deploy state

## 1. The question

The user saw M06 sub-module pages that still have no relevant button to record data.

The first pass (13 Nov, `all_working_folder/1000fix-2/function wise check/m06/M06_Submodule_Capture_Audit_2026-11-13.md`) put **a** button on every one of the 10 pages. It also listed spec gaps it did not build: staff undertakings, retention holds, inventory by type, restore-test evidence, backup runs and wipe requests. This pass checks each page against the specification again, asking whether the page captures what the spec says a person records there.

## 2. What the spec says

Source: `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md`: §5 features, §9 business rules, §10 entities and §11 automations.

| Page | What a person records there | Spec | Class |
|---|---|---|---|
| 1 Case Management | Failure symptoms, criticality, the data the customer needs, the customer's declarations | FR-DTS-001, 028 | P2 |
| 6 Recovered-Data Inventory | Volumes and file counts **by type and size**, never names | FR-DTS-006, T-02; entity `fix.recovered.inventory` | P1 |
| 7 Secure Handover & Purge | A retention hold: kept past the window only on a documented, approved, time-limited hold | FR-DTS-008b, BRU-DTS-06 | **P0 / H** |
| 8 Backup Plans | Each backup job's outcome, with an incident on two failures in a row. Restore tests with their scope and evidence | FR-DTS-012/013, AUT-DTS-11/12; entities `fix.backup.run`, `fix.restore.test` | P2 |
| 9 Secure Destruction | The wipe request from M14, M18, a customer or a corporate decommission. When erasure cannot be verified, physical destruction is mandatory | FR-DTS-019/024, AUT-DTS-08/10, BRU-DTS-10; entity `fix.wipe.request` | P1 / **H** |
| 10 Access Control & Audit | Each person's confidentiality undertaking for the case, recorded **before** access is granted | FR-DTS-010, BRU-DTS-12, AUT-DTS-01; entity `fix.confidentiality.undertaking` | **P0 / H** |

## 3. What the code had (HEAD `6deb4dca`)

All M06 tables on fix_real held **0 rows**, and only the administrator holds an M06 role. The page's button is therefore the only way into any of this.

| # | Page | Button before | Defect |
|---|---|---|---|
| 1 | Case Management | + Recovery Case | The case form had no field for symptoms, criticality, the data wanted or the customer's declarations. |
| 6 | Recovered-Data Inventory | + Record the Recovered-Data Inventory | Two totals only. No breakdown by type existed. |
| 7 | Secure Handover & Purge | + Record a Secure Handover | No hold record. The retention job flagged every case at its date whatever the customer or a court had asked, and nothing could stop a purge. |
| 8 | Backup Plans | + Backup Plan | No job-run record. The restore test existed as a model, but had no form, no list, no scope and no evidence. The list button asked only "passed/partial/failed", so a test passed with nothing to show. |
| 9 | Secure Destruction | + Destruction Request (the certificate) | **Dead end.** Verification refuses a certificate without its wipe log, and the form had no field to attach it. Every certificate made on this page could never be verified, so no case could be purged and no device released to M14 or M18. Nobody could *request* a wipe, and a failed erasure went nowhere. |
| 10 | Access Control & Audit | + Assign Named Z4 Staff | No undertaking record existed: only the customer NDA reference. Any operator could be named on a case and open its data. |

Pages 2–5 were correct. Page 2 gains a read-only list of the custody ledger every move writes, which no screen had shown.

## 4. What was built

`cd_data_case` 19.0.2.1.0, new `models/fix_data_capture.py` (imported last):

| Record | Page | Rules enforced by the model |
|---|---|---|
| `fix.data.confidentiality.undertaking` | 10 | A staff member accepts the undertaking themself on screen. To record one for someone else, attach the form they signed. A customer NDA or a partner-lab agreement always needs the signed document. One active undertaking per person per case. Cannot be edited; the lab manager or a Z4 custodian revokes it. **`action_assign_staff` refuses to name anyone without an active undertaking on that case, and every Z4 action (start, attempts, imaging, inventory, handover, the TOTP data read) refuses a person whose undertaking is revoked or expired.** |
| `fix.data.retention.hold` | 7 | Only on a handed-over case. Needs a basis and a written reason. It must end after the retention date and lasts at most 90 days (`cd_data_case.retention_hold_max_days`, the owner's number to change). One open hold per case. **Approved by a lab manager who did not request it.** While approved and running, the retention job skips the case and a manual purge is refused. It is released early by the requester or a manager, and expires by itself. |
| `fix.data.recovered.inventory` | 6 | One line per file type from a fixed list: files and GB, no free text, so no names (T-02). Only the case's named staff record lines, and only while the case is recovering or recovered. **The case totals are the sum of the lines.** The totals-only entry is refused once lines exist. Lines are fixed after handover. |
| `fix.data.wipe.request` | 9 | Any internal user, such as an M14 or M18 desk, can raise one. It needs a serial (BRU-DTS-11), a confidentiality level and a disposition. Its state comes from its certificates: requested, in progress, certified, physical destruction required, escalated, or cancelled. The certificate gains `wipe_request_id`. **The certificate's serial must match the request's, and only one certificate may await verification at a time. After a failed erasure the next certificate must be physical destruction (BRU-DTS-10).** Marking a certificate failed notifies the requester and the technician (AUT-DTS-10). Once worked, a request cannot be edited. |
| `fix.data.backup.run` | 8 | A failed or warning run needs an error reference or notes. A run cannot be dated in the future or edited. **The second failed or missed run in a row raises an incident: a chatter note plus a to-do for the plan owner and the recorder** (AUT-DTS-11). The plan shows its last job and its failure streak. |
| `fix.data.backup.test` (existing) | 8 | Gains a scope and an evidence upload. **A passed test needs its evidence.** It cannot be edited. Saving it rolls the plan's next test date forward and publishes `data_case.backup_test_logged`; this moved here from the list action, so every path does it. |
| `fix.data.recovery.case` (existing) | 1 | `failure_symptoms`, `criticality`, `target_data_description`, `customer_declarations`, `prior_recovery_attempt`. |

Workspace (`cd_p03_portal`):

- `static/src/a02/m06.js`:
  - Pages 6, 9 and 10 now open their own record. Pages 7 and 8 gain chips.
  - 7 new lists (custody ledger, inventory lines, holds, restore tests, job runs, wipe requests, undertakings) and 6 new forms. The module forms list grows from 16 to 22 entries.
  - The case form gains a "Customer Intake & Declarations" tab.
  - **The destruction form gains the wipe-log upload** and the request picker.
  - The backup list drops "Log Restore Test", which could not attach evidence; the Restore Test form replaces it.
- `controllers/a02/m06.py`: 7 new served surfaces with their actions. The inventory report gains a "By File Type" column.
- `controllers/a02/writable.py`: regenerated (M06 entries only).

Security: 5 ACL rows and 10 generated isolation rules (company and operating unit), plus the `WRQ/` sequence. The generator also rewrote 7 other modules' rule files (drift left by other sessions); those changes were reverted and not included.

## 5. Evidence

All runs were against `fix_test_m06c2`, a private copy of `fix_test_m05c2` upgraded with this branch (`-u cd_data_case,cd_p03_portal`, exit 0).

- **New guard test** `cd_p03_portal/tests/test_m06_capture_pass2.py`: 23 tests, all passing.
  - Pages and wiring: every new form is on its page with a chip, a served model and writable fields; pages 6, 9 and 10 open their own record; the 7 new lists bind real columns and whitelisted actions.
  - Saves run through `/p03/model/write` and `/p03/model/action` as non-admin users holding only M06 roles:
    - undertakings: own e-acknowledgement versus signed form, the assignment refused without one, a revocation stopping the work, the NDA needing its document;
    - holds: limits, segregation of duties, the purge and the retention job both blocked while a hold runs, release and expiry;
    - inventory per type: totals summed, duplicate refused, frozen at handover;
    - wipe request: a certificate verified on its **uploaded** evidence, a serial mismatch refused, a failed erasure forcing physical destruction, cancel;
    - backup runs: the incident on the second failure in a row;
    - restore test: refused without evidence;
    - case intake fields.
- **Mutation check: 17/17 red.** Each fixed defect was re-introduced and the suite failed for every one. The first run gave 15/17. The two survivors (the cron skip with automatic purge off, and an inventory edit by direct ORM write after handover) showed test gaps; those tests were tightened and both now go red.
- **Regression:**
  - Domain: `cd_data_case`, `cd_ewaste`, `cd_tradein` and `cd_rental_asset` ran **431 tests, 0 failed**. These cover the existing M06 suites updated for the undertaking gate and restore-test evidence, plus the M14/M18 certificate gates.
  - `cd_p03_portal`: **5,698 tests, 15 failed**. 3 were this change: the A02 control suite expects the estate's standard refusal for a guarded field, which is now fixed, and that suite passes. **The other 12 fail identically in the main checkout without this change** (M50 chip, M52 print action, five A10 guard messages, M50 pick form, an M22/M55 dispatch message, M60 hold row, M30 branch page). They belong to other modules.
- **UI walk** on a private server (port 8173, same database): all 10 M06 pages opened. Each showed its own button: page 6 "+ New Recovered Data by File Type", page 9 "+ New Wipe Request", page 10 "+ New Staff Confidentiality Undertaking". Each listed the chips in §4. The 6 new forms, the 7 new lists, the case form, the destruction form (now with a file upload) and the inventory report (with its "By File Type" column) all rendered with no error.
- ruff 0.8.4 check and format: clean.

Not covered: no click-through on fix_real itself before the deploy (all its M06 tables are empty, and nobody holds the Lab Manager, Z4 Custodian or Verifier roles there).

## 6. State and what is not done

- **Landed** as `b6aa3201` on `fix/a03-live-data-and-pending-work` (a fast-forward; the code commit was rebased onto `74fd8ed1`, cleanly). The generated whitelist is unchanged after the rebase.
- **Not pushed:** github.com:443 was unreachable from this machine on three attempts. Push both branches when the network is back.
- **Not deployed.** 8069 (fix_real, PID 83708) and 8090 (fix_dev, PID 83680) started at 23:28 on 18 Nov, before this landing. The version-gap check finds **both databases behind on five installed modules**: `cd_data_case` (this change) plus four other sessions' modules, `cd_rate_card`, `cd_crm_ext`, `cd_loyalty` and `cd_quotation`. A restart loads all their code. So a safe deploy is one `-u` of all five plus `cd_p03_portal` on both databases, a column re-check, then a restart of 8069 and 8090. That waits for the owner's go-ahead, coordinated with the sessions that own the other four modules.
- After deploying, someone must still appoint holders of the Data Recovery Lab Manager, Z4 Custodian and Wipe Certificate Verifier roles before holds, custodians and certificate verification can be used on fix_real.

**Not built (spec items with no page defect behind them, or owner decisions):**

- FR-DTS-026 equipment tracking and FR-DTS-030 case costing (P3/P2).
- FR-DTS-027 partner-lab referral (P3). BRU-DTS-15 (H) applies only once referrals exist.
- FR-DTS-023 bulk decommission reconciliation (P2). A request can carry the project reference, but there is no asset-list reconciliation.
- FR-DTS-014/015/016/017/018/031/032: billing, archival, CDP, migration and restore requests (P2/P3).
- BRU-DTS-08 technique matrix: the Company's sanitisation programme document (FR-DTS-020c) is the owner's to write. No matrix was invented.
- The 90-day hold cap and the 30-day retention are policy numbers for the owner.
- Nobody holds the Lab Manager, Z4 Custodian or Wipe Verifier roles on fix_real. Until those appointments are made, no hold can be approved, no custodian named and no certificate verified. The forms say so when they refuse.
