# M24 Documents & E-Signature: data-capture audit, second pass

**Date:** 19 Nov 2026 · **Estate:** fix_real on port 8069 (fix_dev on 8090) · **Branch:** `fix/m24-capture-pass2` · **Status:** LIVE on 8069 and 8090 (see §7)

## 1. The question

The user again saw M24 sub-module pages without a relevant data-capture button. The 13 Nov pass ([M24_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M24_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) gave every page a button over the models that already existed. It also listed five spec items with no model at all, including the registry's own "Share Token" form. This pass checks each page against the records the spec says a person captures there, and builds what was missing.

## 2. Method

1. **Spec:** `1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24_Document_Records_and_ESignature.md`: FR-DMS-001…042 (§5), the three lifecycles (§8: document, envelope, disposal batch), BRU-DMS-01…20 (§9), the 23 owned entities (§10.1), automations AUT-DMS-01…20 (§11) and roles/SOD-23 (§13). Also `contracts/nav/registry.json` (M24 forms: Upload, Signature Envelope, **Share Token**, Retention Policy).
2. **Code, as the user sees it:** the workspace's own page rule (`fregCreate` / `fregPanels` from `p03_workspace.js`) executed in node over the real fragments (the `test_m24_capture_buttons.py` probe), listing each page's "+ New" and chips.
3. **Model inventory:** every `_name` in `cd_document_core` and `cd_esignature` matched against §10.1.
4. **Live data, read-only:** fix_real and fix_dev counts (§6).

## 3. Findings (HEAD a6ca660a)

Of the 23 entities in §10.1, 7 existed (document, template, retention class, legal hold, disposal record, envelope, signer). None of the 16 others had a model, so no page could capture them.

| # | Page | What the page offered | What the spec requires there, missing |
|---|---|---|---|
| 1 | Repository & Integrity | + Document (upload) | FR-DMS-013 / AUT-DMS-20: the **physical-records register** (where a paper original is, who holds it, its evidenced destruction). T-13 / AUT-DMS-19: **integrity sweeps** re-hashing stored bytes. No model for either. |
| 2 | Auto-Filing | + Document Template | FR-DMS-021 (P0) / BRU-DMS-09 (H): **template changes need approval**, and a document binds to the version used. A template had no version, no state and no approver; anyone could edit one in place. |
| 3 | Classification & Search | + Document (the same upload as page 1) | FR-DMS-004 (P0) / BRU-DMS-01 (H): the **document class taxonomy** with mandatory metadata, tier, retention class and signature level. FR-DMS-006 (P0) / BRU-DMS-08 (H): the **exception queue** for captures that cannot be classified. No model for either. |
| 4 | Versioning & Control | + New Controlled Document | FR-DMS-019: **distribution to named people with acknowledgement**. No model. |
| 5 | E-Signature | + Signature Envelope | FR-DMS-026 / scope item 12: a **wet-ink signature, scanned**, for a signer without a login. Such a signer could not sign at all. FR-DMS-033 (P0): **on-demand verification**, which had no method. BRU-DMS-17 (H): the class's assurance level was not enforced. |
| **6** | Retention & Holds | + Place Legal Hold, **Dispose of Document** | FR-DMS-038 (P0), §8.3, **SOD-23**, BRU-DMS-05 (H): disposal is a **batch** prepared by one officer and approved by another. **Defect:** the 13 Nov "Dispose of Document" let one Records Officer dispose of a document with no approval at all. Also FR-DMS-036/037 (P0): a **hold over a scope** (class, type, business object, dates), propagated to later filings. Only one-document holds existed, and releasing a document released every matter at once. FR-DMS-040 (P0) / BRU-DMS-19 (H): **retention violations** in both directions. No model for any of these. |
| **7** | Evidence Packs | **No + New**; one chip to M31's workshop form | FR-DMS-041 (P0) / AUT-DMS-15 / AC-11: **evidence pack assembly** for a claim, audit, dispute or regulator: manifest, completeness check, seal. FR-DMS-042 (P0) / BRU-DMS-13 (H) / AC-13: the **controlled external release**, which is the registry's "Share Token" form: scoped, approved, time-boxed, watermarked, logged. T-11: the **access log**. No model for any of these, and no public route. |

Three more defects came up on the way:
- **The "Evidence Packs < 5 min" KPI counted completed signature envelopes.** It now counts packs sealed within 300 seconds of the request.
- **The Upload form could not link a document to its business object** (FR-DMS-005), which the spec calls the primary index. A class that makes the link mandatory would have sent every workspace upload to the exception queue.
- `cd_hr_core` generates employment contracts from these templates. Refusing every template not yet approved would have stopped M21. The rule built is the one FR-DMS-021 states: an **unapproved change** (a draft version 2 or later) or a **retired** version generates nothing.

## 4. What was built

`cd_document_core` 19.0.2.0.0: new file `models/fix_document_capture.py` (imported last; it imports the files it extends itself), `controllers/fix_release.py`, `security/fix_document_capture_security.xml`, `data/fix_document_capture_cron.xml`. `cd_esignature` 19.0.2.0.0: `models/fix_esignature_capture.py`.

| Page | Record | Rules it enforces |
|---|---|---|
| 1 | `fix.physical.record` | Registered and moved only by a Records Officer; the custodian, location and condition are tracked. Destruction is refused while the document is held, before its retention has run, or without uploaded evidence (filed as a destruction certificate). A daily job gives the custodian a to-do when one falls due (AUT-DMS-20). |
| 1 | `fix.document.integrity.check` (+ divergence lines) | Saving one runs it (Records Officer or administrator): every stored document is re-hashed and compared with its SHA-256 fingerprint, and each divergence is listed and noted on the document. A weekly job runs one too. A sweep is never edited. |
| 2 | template governance (`fix.document.template` + `version`, `state`, `approved_by_id`, `previous_id`) | Approved by a Document Controller who neither created nor last edited it. Once approved it is frozen; "Start New Version" copies it into the next draft, and approving that version retires the one before. The unique key is now (code, version). |
| 3 | `fix.document.class` | Written by a Records Officer or Document Controller, and activated by a Document Controller who did not write it. One active class per document type (BRU-DMS-01). Frozen once active. **From the first active class of a company:** each new document is filed under its class, takes the class's retention class if it has none, is raised to the class's minimum tier, and must carry the class's mandatory metadata (Bengali name, business-object link, description, branch). |
| 3 | `fix.document.exception` | A capture with no class for its type, or missing mandatory metadata, gets `filing_state = exception` and a queue row with the cause; it is never filed incomplete and never discarded. A Records Officer supplies the class and metadata on the exception form (written to the document) and files it; the filing re-checks the class. |
| 4 | `fix.document.distribution` + `fix.document.acknowledgement` | Only the published, current version of a controlled document (BRU-DMS-11), distributed by its author or a Document Controller. Each recipient gets a to-do and acknowledges with their own login; an acknowledgement of a superseded version is refused. It closes when everyone has acknowledged. |
| 5 | `fix.esignature.wet.signature` | A witness records a paper signature: the scan is required and filed (new document type `signature_scan`), the identity document checked is noted, the witness cannot be the signer, the signer must be next in sequence, and the envelope must be sent and inside its window. The signer is stamped `wet_ink_scan`. The record is never edited or deleted. |
| 5 | `action_verify` on the envelope | Re-hashes the bytes and signer list against the seal, reads the completion certificate back (sealed hash, signers) and stamps intact/broken with the finding. Anyone may run it. |
| 5 | BRU-DMS-17 | A class at "qualified" level refuses a session signature and a wet scan; only the provider callback signs it. |
| 6 | `fix.disposal.batch` | §8.3 lifecycle. A Records Officer prepares it for one retention class and cut-off: saving lists the eligible documents and, separately, those **excluded because they are held**. It is submitted, then approved by a **Disposal Approver** (new group `group_disposal_approver`) who did not prepare it (SOD-23). Execution is all or nothing: a document held or changed since approval fails the batch with nothing disposed. Each document gets its register entry (now with `batch_id`) and certificate, and the batch gets its own certificate. **`fix.document.action_dispose` now refuses any call that does not come from an approved batch**, Records Officers and the superuser included (an in-process token, as in the guard mixin). The "Dispose of Document" form and row action are gone. |
| 6 | `fix.retention.violation` | A nightly scan raises both directions (BRU-DMS-19): expired, unheld and undisposed more than 90 days past the date (`cd_document_core.over_retention_grace_days`), or archived or emptied before the date with no disposal on the register. There is one open violation per document and type. A Records Officer can raise one manually; investigating and closing it need a note. |
| 6 | `fix.legal.hold.order` | A matter (reference, instructing authority, date) over a scope: retention class, type, business object, filing period. At least one criterion is required. Applying it holds every match at once, and a document filed later that matches is held on creation (FR-DMS-036). **Release is matter by matter:** a document stays held while any other matter holds it, and releasing a multi-matter document from the browser is refused (BRU-DMS-04). |
| 7 | `fix.evidence.pack` (+ required-composition lines) | Purpose (claim, audit, dispute, regulatory), subject, documents. "Collect" gathers every document linked to the subject record. "Assemble & Seal" checks the composition, and **an incomplete pack is marked INCOMPLETE with each missing item named** (AC-11). The manifest (fingerprints) is filed, its SHA-256 sealed, and request-to-seal seconds recorded (KPI-C24-04). A sealed pack is frozen; "Verify Seal" re-hashes it. |
| 7 | `fix.external.release` ("Share Token") + `fix.document.access.log` | Scoped to a sealed pack or named documents (no T5 document), lasting at most 30 days (`cd_document_core.external_release_max_days`). Requested, then approved by a Records Officer or Document Controller who did not request it; approval issues a random token. Public route `/dms/release/<token>`: it works only while the release is granted and unexpired, serves only documents in scope, **watermarks every PDF (reportlab + PyPDF2) and image (PIL)** and withholds any other file type when a watermark is required. It logs every grant, view and download with the IP to an append-only log. Revocation or the hourly expiry job kills the link. |

Workspace (`cd_p03_portal`):
- `a10/m24.js`: 14 new screens (a new group, "Evidence & Release"), 11 new forms and 10 new chips, and the page mappings in §4.1.
- The Upload form gains the business-object link.
- The template list shows version and state, with Approve, New Version and Retire.
- The envelope list gains "Verify Signature Evidence", and the envelope form shows the required assurance and the verification.
- `controllers/a10/m24.py` serves the new models with their actions and picker domains, and the KPI is fixed.
- `writable.py` is regenerated. No workflow field is writable.

### 4.1 Pages now

| # | Page | "+ New" | Chips |
|---|---|---|---|
| 1 | Repository & Integrity | + Document (upload) | Upload, **Physical Record**, **Integrity Sweep** |
| 2 | Auto-Filing | + Document Template | Document Template (versions approved on the list) |
| 3 | Classification & Search | **+ Document Class** | **Document Class**, Upload; screen **Classification Exceptions** |
| 4 | Versioning & Control | + New Controlled Document | Controlled Document, **Distribution**; screen **Acknowledgements** |
| 5 | E-Signature | + Signature Envelope | Signature Envelope, **Wet-Ink Signature** |
| 6 | Retention & Holds | + Place Legal Hold | Place Legal Hold, **Legal Hold Order**, **Disposal Batch**, **Retention Violation**, Retention Policy |
| 7 | Evidence Packs | **+ Evidence Pack** | **Evidence Pack**, **Share Token**, Workshop Evidence Item (M31) |

## 5. Evidence

All runs used a private clone, `fix_test_m24c2` (from `fix_test_m25c2`), with `-u cd_document_core,cd_esignature,cd_p03_portal,cd_requisition`. That exited 0 with no ERROR from these modules. `cd_requisition` was included only because the clone predated M16's pass-2 tables. The upgrade moved the template constraint to `UNIQUE (code, version)` and created all 15 new tables.

- **Guard** `cd_document_core/tests/test_m24_capture_pass2.py`: **21 tests, 21 passed, 0 skipped.**
  - Every capture is saved through `/p03/model/write` and every workflow step through `/p03/model/action`, as non-admin users: clerk, Records Officer, Document Controller and Disposal Approver.
  - The public release route is driven as the public user: in-scope file served, out-of-scope 404, PDF text shows "CONTROLLED RELEASE" and the release number, every access logged with its IP, the link dead after revocation and after expiry.
- **Pass-1 guards updated for the new rules:**
  - `test_m24_capture_buttons.py`: page 3 now captures the class and page 7 the pack; "Dispose of Document" is gone; the source probe now joins every file that declares the model.
  - `test_m24_capture_live.py`: a lone disposal is refused even to a Records Officer; a held document is excluded from its batch.
  - `cd_document_core`'s two disposal tests keep their register, certificate and wipe assertions, now through the batch token, and also assert the lone refusal.
- **Mutation check** (`scratchpad/m24/mutate.py`): 42 defects re-introduced one at a time, each find-string preflighted to match exactly once.
  - First run: 36/42 killed. Four survivors were guard gaps: the template freeze was only tried through the endpoint, whose form lock hid the ORM rule (and the reverse); the revoked token was not checked; the certificate-hash finding was hidden by the signer check. The tests were added, and the re-run killed all four (plus the two mutants re-pointed after formatting): **40/42 in total**.
  - The two survivors are equivalent, because a second layer enforces the same rule: only Records Officers have write on `fix.document.exception`, and a document held after approval is also refused by `action_assert_can_destroy` inside the batch's rolled-back savepoint (nothing disposed either way).
  - Sources were verified byte-identical afterwards.
- **Regression:** `cd_document_core` + `cd_esignature` (all), plus the workspace's M24, A10 whitelist, A10 control suite, estate-page, sub-module and create-button guards, plus M08 pass 2, M36 buttons, both `cd_contract_core` contract suites and the `cd_hr_core` ORM suite (contract generation from templates): **1,045 tests, 0 failures**, 12 skipped. Every skip is a control-suite model with no workflow fields.
- **Lists:** all 21 list screens and 7 page lists requested over the wire with their declared columns: **0 columns dropped**.
- **Live walk** (headless Chromium, private server on 8124 over the clone, admin session):
  - All 7 pages show the "+ New" and chips in §4.1.
  - The "+ New" and every chip open their form with no error.
  - All 17 lists render. **0 console errors.**
  - Four saves through the forms landed as expected: a retention class, a Document Class (Draft, T2, its retention class), an Evidence Pack (EVP, Draft) and a Disposal Batch (Proposed, preparer stamped).

What this did not cover: a click-through on fix_real or fix_dev (not deployed yet, §7), real users holding the M24 roles (none exist, §6), and a browser download through the public route (proven by calling the route in-process, not over HTTP from outside).

## 6. Not done / open

1. **Nobody but `admin` holds an M24 role on fix_real or fix_dev.** That covers Records Officer, Document Controller and now Disposal Approver. Until the owner appoints people (M24 Q-06, Q-10), no real user can approve a class or template, prepare or approve a disposal batch, place a hold order or grant a release. SOD-23 also means admin alone can never complete a batch, because the approver must differ from the preparer.
2. **Classification is off until a class is activated**, and none is seeded. The class taxonomy is the owner's (Quality Manager). The spec's 14-class statutory schedule is not loaded, because retention periods carry legal bases nobody has signed off (§16.3, Q-01).
3. **The existing templates on fix_real (3) and fix_dev (4) show as Draft v1.** No one has approved them. They still generate, because only an unapproved *change* is refused. A Document Controller should approve them.
4. **Not built:**
   - OCR and bilingual full-text extraction (FR-DMS-008/009, INT-DMS-02: an engine to host);
   - storage tiering (FR-DMS-014);
   - bulk import (FR-DMS-012);
   - redaction (FR-DMS-024);
   - controlled printing (FR-DMS-023);
   - version comparison (FR-DMS-016);
   - the retention-schedule version adopted from M60 (FR-DMS-034, AUT-DMS-06; this needs the M60 slice, Q-01);
   - remote signing by WhatsApp/SMS link and the qualified provider (FR-DMS-028/032; L6, Q-02, Q-03, Q-09);
   - a hold placed by M60 through an API command (`/api/v1/holds`). D-040 keeps holds in M24's kernel and a Records Officer places them.
5. **The retention scan reads every document nightly.** That is fine at today's volume (0 and 7 documents), but it needs batching before the 500,000-document migration (§16.4).
6. **A divergence found by an integrity sweep** is noted on the document and on the sweep. No incident is raised in M47/ITSM, and no new event type was added (the event registry is a contract).
7. **The release watermark covers PDFs and images.** Any other file type is withheld while the watermark is required. Disposal removes the file from Odoo's store only. Removal from backups within a declared window (T-06, Q-08) is a platform task.

## 7. State

**LIVE on fix_real (8069) and fix_dev (8090), 19 Nov 2026. The owner approved the deploy.**

- **Landed** `61b4084b` (fix) and `fdee2885` (report) on `fix/a03-live-data-and-pending-work` by compare-and-swap. Both are pushed, with `fix/m24-capture-pass2`.
  - The only rebase conflict was `a10/writable.py`, regenerated from all forms (M23's and M24's).
  - After the rebase: M24, whitelist, control-suite, estate and sub-module guards plus both module suites ran 914 tests, 0 failures caused by this change. Three M23 tests needed M23's tables on the clone; after `-u cd_qms_process` they pass.
- **Deploy:**
  1. Checked that no other `odoo-bin` was running. The version gap on both databases was exactly `cd_document_core` and `cd_esignature`.
  2. Backups: `1000 fix/backups/fix_{real,dev}_pre_m24_pass2_deploy_2026-11-19.dump`.
  3. `-u cd_document_core,cd_esignature,cd_p03_portal --stop-after-init` on fix_real, then fix_dev. Both exited 0; the only errors were rST warnings from other modules' manifests. The gap was then 0 on both and the shared tip unchanged (`742e46bc`).
  4. One restart of each: 8069 is now PID 44100 (155 modules loaded) and 8090 is PID 46556 (151 modules), with 0 registry failures and `/web/login` returning 200 on both.
- **Verified live, read-only:**
  - Both databases: modules at 19.0.2.0.0, all 15 new tables, 5 active M24 crons, the Disposal Approver group, and the template key `UNIQUE (code, version)`.
  - The existing templates show **Draft v1**: 3 on fix_real, 4 on fix_dev.
  - All 28 lists served with their declared columns, 0 dropped, on both servers.
  - A headless walk signed in as the dev admin on both servers: all 7 pages show the "+ New" and chips in §4.1, every form opens with no error, all 17 lists render, and there were **0 console errors**. Nothing was saved on the live databases.
- **Not done:** the owner items in §6 (role holders, a first document class, approving the existing templates).
