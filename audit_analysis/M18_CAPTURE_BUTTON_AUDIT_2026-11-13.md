# M18 E-Waste & Recycling: sub-module data-capture audit (13 Nov 2026)

**Report:** "not all the sub-modules have a relevant data capture button".

**Scope:** the 10 Function Register sub-module pages of the M18 workspace
(`cd_p03_portal/static/src/a05/m18.js`).

Each page was checked against two things:
- the module specification, `1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M18_EWaste_Recycling_and_Circular_Economy.md`
  (FR-ESG-001…026, T-01…13, BRU-ESG-01…20);
- the server rules in `cd_ewaste`.

## How it was measured

- **Page rule.** The engine's own `fregCreate` (in `p03_workspace.js`) was run in node over the real registry. It returns the button each page shows. This is the same method as the M02, M06 and M13 audits.
- **Server rules.** Each form a page offers was checked against the model's `create` and `write` guards. A button the server refuses counts as a defect, not as a capture.
- **Live data.** See "Live state" below.

## Findings (before)

| # | Sub-module | What the page offered | Verdict |
|---|---|---|---|
| 1 | Intake & Channels | + New Collection Intake; incentive chip | OK. The customer is required by the model, but the form did not mark it required. |
| 2 | Triage & Disposition | + New Triage & Sanitization Record | OK, but its item picker listed every collection. The server refuses any item that is not in `collected` state. |
| 3 | Data Destruction | **nothing** (`create: false`, no forms) | **Missing.** This is the P0 destruction gate (FR-ESG-009). The page listed triage decisions, not the items waiting for destruction. Binding the M06 certificate, starting destruction and releasing to the recycler were list buttons only. |
| 4 | Outbound Recycler | + New Recycler Dispatch Batch | OK. Its recycler picker listed unapproved recyclers (dispatch refuses them), and its PIC picker listed draft consents. Basel PIC and recycler-money lists were on no page. |
| 5 | Green Certificates | + New Green & Destruction Certificate | **Dead button.** `fix.ewaste.certificate.create` refuses every typed certificate: "recorded from its processed recycler batch … never typed in". |
| 6 | Public Drives & Bins | + New Collection Drive Event | OK |
| 7 | Hazardous Fraction | + New Battery & Hazardous Dossier | OK, but see defect D1 (no photo upload, so the HSE inspection could never be recorded). |
| 8 | EPR Reporting | + New Statutory Environmental Return | OK |
| 9 | ESG & Carbon | nothing | **Correct.** ESG figures are computed from transactions. T-07 and BRU-ESG-11 say no entry path may exist. |
| 10 | Compliance Pack | page 8's return again | **Wrong capture.** It repeated page 8. The DoE e-waste registration that returns are filed under (FR-ESG-016/017) had no page. |

### D1: no evidence could be uploaded anywhere in M18

Six steps in the chain refuse to proceed without a scanned document:

| Model | Evidence field | What it unblocks |
|---|---|---|
| recycler | licence scan | approval, and the licence re-check at every dispatch |
| batch | processing evidence | `processed` |
| certificate | recycler certificate scan | issue |
| battery | inspection photo | HSE inspection |
| Basel PIC | consent scan | confirm consent |
| DoE registration | certificate scan | confirm registration |

Each of these was a many-to-one **picker over existing `ir.attachment` rows**, and the workspace has no upload for that field type. So:

- **No recycler could become dispatchable from the workspace.** Therefore no batch could leave, and no item could ever be certified.
- **The picker read `ir.attachment` with sudo across the whole company.** Any M18 user could browse the names of every file in the company (payslips, contracts), and could "prove" a step with an unrelated file.

## What was changed

### Workspace (`static/src/a05/m18.js`, served from disk, live on 8069 now)

| # | Page now offers | Chips on the page |
|---|---|---|
| 1 | + New Collection Intake (customer now required) | E-Waste Incentive / Recycler Money; Settlements list added to the page |
| 2 | + New Triage & Sanitization Record (picker limited to collected items) | none |
| 3 | **Start Secure Destruction**: pick a triaged Recycle-Only item → `action_secure_destruction`. The page now lists the items awaiting or in destruction. | **Bind an M06 Wipe Certificate** (plain write, guarded by the model's one-certificate-one-item rule); **Release a Destroyed Item to the Recycler** → `action_recycle_estimated` (refused until M06 verified) |
| 4 | + New Recycler Dispatch Batch (recycler picker: approved recyclers only; PIC picker: consented only; processing evidence uploaded here) | Recycler, Basel PIC, Incentive; PIC and Settlements lists added to the page |
| 5 | **Record a Recycler Certificate**: pick a processed batch with no live certificate → `action_record_certificate` | **Enter a Recycler Certificate**: pick a draft, then enter its number, the weight it states and its uploaded scan. The list no longer offers the refused "+ New". |
| 6 | + New Collection Drive Event | none |
| 7 | + New Battery & Hazardous Dossier (inspection photo uploaded here) | none |
| 8 | + New Statutory Environmental Return | DoE Registration |
| 9 | none (computed; the list explains Recompute) | none |
| 10 | **+ New DoE E-Waste Registration** (page now lists registrations: authority, role, number, EPR target, validity) | Recycler, Basel PIC |

Every evidence field is now shown read-only, as the file on record, with an **Upload** input beside it.

### Server (`cd_ewaste`; needs an 8069/8089 restart, no schema change)

- **`models/ewaste_common.py`**:
  - `lift_uploads`, `stage_uploads`, `attach_staged` and `lock_uploads`;
  - a form sends the file itself; the model attaches it to the record (`res_model`/`res_id` = that record) and fills the link inside its own `write()`;
  - every existing state and freeze rule therefore applies to the upload exactly as before;
  - the file input locks whenever its link is locked.
- **`models/fix_ewaste_ops.py`** (certificate, batch, battery, recycler) and **`models/fix_ewaste_compliance.py`** (the licence-record base of PIC and registration): non-stored `*_file` / `*_filename` fields and the hooks.
- **`controllers/a05/writable.py`**: regenerated (`form_fields.py --a05`). The six link fields are no longer writable from the workspace; the upload fields are. The diff touches M18 lines only.

**Until the restart**, the running server does not know the upload fields:
- the forms load, but leave the upload inputs out;
- the evidence link shows read-only.

So evidence still cannot be attached from the workspace until the restart (before this change it could only be "attached" by picking someone else's file).

### Guard test

`cd_p03_portal/tests/test_m18_submodule_capture.py` covers:
- the page rule, executed over the real registry, with the expected button for each of the 10 pages;
- no two pages offering the same button;
- every chip resolving to a form, and every M18 list on a page;
- no refused create offered;
- evidence uploaded, not picked (whitelist checked);
- every form field, picker column, filter and step method existing on its surface;
- the legitimate path through `/p03/model/write` and `/p03/model/action` as non-admin users with only their M18 role:
  - bind, then start, then release (refused while unverified);
  - record a certificate from its batch, then upload the scan, then issue; the frozen upload is refused afterwards;
  - recycler licence upload;
  - processing evidence upload, refused before the recycler has received the batch;
  - battery photo upload, then HSE inspection;
  - registration with its scan, confirmed by a second officer.

## Still open (spec items with no model: need owner decisions, not built)

| Spec item | Gap |
|---|---|
| FR-ESG-001/003 | The collection has no channel/source type, condition, hazard flags or photos (only customer, device, category, weight, count). |
| FR-ESG-022 | No collection-point register (capacity, hazmat limits, responsible person). T-06 is a single company-wide battery ceiling, not per location and class. |
| FR-ESG-005, BRU-ESG-14 | No corporate disposal contract (declared asset list reconciled to certificates). |
| FR-ESG-008 | No parts-harvesting route to M15. |
| FR-ESG-023, BRU-ESG-15 | No donation route. |
| FR-ESG-014 | Material recovery is only a money line (settlement kind *recovery income*). There are no recovered material classes with weights per batch. |
| FR-ESG-016 | No regulatory obligation register. Only the DoE registration exists. |
| FR-ESG-024, BRU-ESG-18 | No recycler downstream-vendor declarations or verification. |
| FR-ESG-002, BRU-ESG-13 | No portal booking. The incentive is a manual, approved settlement, not triggered on receipt. |
| Batch receipt / processing | These stay "type on the batch record, then press the list button". A one-screen step (like page 3's) would need the weighbridge figures passed to `action_receive` as arguments. |

## Verification

| Check | Result |
|---|---|
| Page rule, before → after (node, real registry) | 3: none → Start Secure Destruction; 5: dead "+ New certificate" → Record a Recycler Certificate; 10: page 8's return → + New DoE E-Waste Registration; 9: none (correct) |
| `test_m18_submodule_capture.py` (private copy of fix_test) | **25 passed** |
| Regression: whole `cd_ewaste` suite, `test_a05_control_suite.py`, `tests/test_journey_10_ewaste.py` | **126 passed, 6 skipped, 0 failed**. The 6 skips are the A05 control suite's "model carries no workflow-controlled fields" cases, not M18. |
| Estate page standard (`test_estate_module_pages.py`, all 67 modules) | **605 passed** |
| ruff 0.8.4 check + format on the changed Python | clean |
| Live 8069 (`fix_real`, `?debug=assets`), click sweep of the 10 sub-module pages | Every page shows the expected button (table above); page 9 shows none. |
| Live server probe: every M18 list, form and step picker through `/p03/model/form` and `/p03/model/records` | 0 errors. The only fields left out are the 10 upload fields, which the running server gains at the restart. All picker filters were accepted, including the revoked-certificate one. |

## Live state and what is pending

- **`fix_real` holds 0 rows in every M18 table** except 6 computed ESG metrics. Nothing in M18 has been used on the live estate, so the paths are proved by the tests above, not on live data.
- **DEPLOYED 13 Nov 2026 at 13:31–13:32 (user-approved restart).**
  - 8089 was stopped first, then 8069; the supervisor relaunched each (new pids 50616 / 45500, `/web/login` 200).
  - **Before the restart:** a schema-gap check (code on disk vs `fix_real`) ran in a window with no peer pre-commit stash and found **0 gaps**, so the restart broke no other session's screens.
  - **Each stop waited for the same quiet window:** my edits on disk and no stash for over 150 s. 8069's last stash was 330 s before its boot.
  - **Boot logs:** 155 modules loaded and the registry loaded on both servers, with 0 ERROR/CRITICAL/Traceback.
  - **Production bundle `0a2768c`** (served without debug) contains the new M18 screens and upload fields.
  - **Signed-in probe after the restart (13 Nov, ~13:45):**
    - `/p03/model/form` on 8069 serves every upload field (`evidence_file`, `processing_file`, `inspection_file`, `licence_file`) on all six evidence forms, with each attachment link read-only. These fields exist only in the new code.
    - On a new batch the processing upload is served read-only, which is intended: evidence is accepted only once the recycler has received the batch.
    - A click sweep of the 10 pages on the production bundle `bae4c2d` (no debug mode) shows every expected button; page 9 shows none.
    - The whitelist drop of the old link fields was not observed live: on create the endpoint silently drops such a field, and with 0 M18 rows that cannot be seen without creating a real record. It is proved by the guard test.
- **No `-u` was needed:** the upload fields are not stored, so there is no schema change.
- **Committed** on `fix/a03-live-data-and-pending-work` as `88395d76` (code and test; all pre-commit hooks passed), with this report in a docs commit after it. Not pushed. The committed files:
  - `cd_ewaste/models/{ewaste_common,fix_ewaste_ops,fix_ewaste_compliance}.py`
  - `cd_p03_portal/static/src/a05/m18.js`
  - `cd_p03_portal/controllers/a05/writable.py`
  - `cd_p03_portal/tests/test_m18_submodule_capture.py`
