# M24 Documents & E-Signature: data-capture button audit

**Date:** 13 Nov 2026 · **Estate:** fix_real on port 8069 · **Status:** committed. On 8069 the JS is visible under `?debug=assets` (verified page by page). It reaches every user, together with the write whitelist that lets the new fields save, at the next restart of 8069/8089.

## 1. The question

The M24 workspace has 7 sub-module pages (Function Register, 56 functions). Not all of them showed a button that captures the right record. Which pages should have one, and what should it open?

## 2. What the spec says

Sources:

- `1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24_Document_Records_and_ESignature.md` (FR-DMS-001…042, lifecycle §8, rules §9, entities §10, roles §13)
- `contracts/nav/registry.json` (M24: 4 groups, 9 screens, forms Upload / Signature Envelope / Share Token / Retention Policy)
- `docs/decisions/D-040-m24-m60-grc-direction-ruling.md`: retention classes and legal hold are M24 kernel capabilities. That overrides the spec's line that hold placement belongs to M60.

| # | Sub-module | Spec | What a person records |
|---|---|---|---|
| 1 | Repository & Integrity | FR-001…014 | a document (web upload is one of the capture sources) |
| 2 | Auto-Filing | FR-001, 020, 021 | nothing per document, because transactions file their own. The human input is the **template** that generates the document. |
| 3 | Classification & Search | FR-004…011 | a document with its class, confidentiality tier and retention class |
| 4 | Versioning & Control | FR-015…019 | a **controlled** document draft (draft → review → approval → publication) |
| 5 | E-Signature | FR-025…033 | an envelope **with its named signers, roles and sequence** |
| 6 | Retention & Holds | FR-034…040 | a **legal hold** on an existing document, a **disposal** of an expired one, and the retention class |
| 7 | Evidence Packs | FR-041 | a sealed pack assembled from the source transaction |

## 3. What the code had (before)

`fregCreate` / `fregPanels` were evaluated over the real registry, and the backend was read.

| # | Page | Capture before | Defect |
|---|---|---|---|
| 1 | Repository & Integrity | + Document (upload) | Correct |
| 2 | Auto-Filing | + Document | **Wrong record.** An upload is the opposite of auto-filing. The page listed every document, and the template form had no chip. |
| 3 | Classification & Search | + Document | No chip. The confidentiality tier shown on the page could not be set at capture. |
| 4 | Versioning & Control | + Document | The list showed **every** document, controlled or not, and + New made an **uncontrolled** one |
| 5 | E-Signature | + New Signature Envelope | **The form had no signer grid**, and the signer list refuses + New, so a workspace envelope could never be sent ("An envelope needs at least one signer") |
| 6 | Retention & Holds | + Document | **Wrong record.** No page anywhere could **place a legal hold** or **dispose of a document**, although both methods were served. |
| 7 | Evidence Packs | none, no chip | Packs are filed by M31 workshop evidence and M09 claims, but nothing on the page pointed there |

There was one more defect, in the form behind page 2: **the Document Template form could never save**. A template is `bilingual` by default, and a bilingual template must have a Bengali name (`_check_bilingual`). The form did not show the Bengali name field, and it was not in the write whitelist.

## 4. What was changed

| # | Page | Capture now |
|---|---|---|
| 1 | Repository & Integrity | unchanged (+ Document) |
| 2 | Auto-Filing | **+ New Document Template**. The list shows only documents filed by a transaction (linked record). Chip: Document Template. |
| 3 | Classification & Search | + Document, plus an **Upload** chip. The upload form now has the **Confidentiality Tier**. |
| 4 | Versioning & Control | **+ New Controlled Document** (new form; it starts with the controlled flag set). The list shows controlled documents only. |
| 5 | E-Signature | + New Signature Envelope. The form now has a **Signers** grid (order, signer, signs as). Signature time and method stay stamped and are read-only. It also shows the sealed dates and the evidence hash. |
| 6 | Retention & Holds | **+ Place Legal Hold** (two steps: pick the document, then enter the matter reference; Records Officer only). Chips: **Place Legal Hold**, **Dispose of Document** (pick an expired, unheld document; Records Officer only; issues the certificate and the register entry), Retention Policy. |
| 7 | Evidence Packs | Chip **Workshop Evidence Item** opens M31's form, which files the governed evidence-pack document |

The Document Browser also gained the row actions Place Legal Hold (asks for the matter reference), Release Hold (asks why) and Dispose. Lists the system writes now explain their empty state.

### Files

- `addons/platform/cd_p03_portal/static/src/a10/m24.js`
- `addons/platform/cd_p03_portal/controllers/a10/writable.py`: regenerated. The M24-only changes are `isolation_tier`; the template's `name_bn`, `bilingual`, `report_ref` and `requires_approval`; and the envelope's `signer_ids`.
- `addons/platform/cd_p03_portal/tests/test_m24_capture_buttons.py`: **new guard**, 28 tests, **17 fail on HEAD**
- `addons/platform/cd_p03_portal/tests/test_m24_capture_live.py`: **new**, 7 tests. They drive `/p03/model/write` and `/p03/model/action` as a non-admin user. With HEAD's whitelist the template save and the envelope-with-signers save are both refused ("This screen does not edit signer_ids").

No model or schema change was needed.

## 5. Verification

- **Guard + estate standard + A10 whitelist:** 641 passed, 0 failed.
- **Live endpoint tests (private clone `fix_test_m24`):** 7/7 passed:
  - a template saves with its Bengali name, and is refused without it
  - an envelope with no signer is refused at Send; with a signer row it saves and sends (state Sent, evidence hash, deadline)
  - typed signature stamps are not accepted
  - a controlled document starts as a draft
  - a hold is refused to a clerk and placed by a Records Officer, and the register row records who placed it
  - disposal is refused to a clerk; a Records Officer's disposal writes the register entry and the certificate
  - a held document cannot be disposed
- **Browser, 8069 `?debug=assets`:**
  - each page's + New is as in §4
  - the envelope form shows the Signers grid
  - the template form shows the Bengali name and the Bilingual field
  - the controlled form opens with the flag ticked
  - Place Legal Hold opens step 1 and says there is nothing to hold (fix_real has 0 documents)
  - the Workshop Evidence Item chip opens M31's form

## 6. Not built: needs an owner decision or a model

| Gap | Spec | Why it is not a button |
|---|---|---|
| **Share Token / controlled external release** (registry form "Share Token") | FR-DMS-042, BRU-DMS-13 | No model exists (`fix.external.release`). It needs a scoped, approved, time-boxed, watermarked, logged public route: a security build, not a form. |
| Document class taxonomy, mandatory metadata, exception queue | FR-DMS-004, 006, BRU-DMS-08 | `document_type` is a fixed list; `fix.document.class` and `fix.document.exception` do not exist |
| Disposal **batches** approved by the class owner (SOD-23) | FR-DMS-038, §8.3 | No batch model. Disposal is one document at a time by a Records Officer. The method is fixed to secure wipe because the document has no method field. |
| Evidence pack **assembly for audit, dispute or regulator** | FR-DMS-041 | Assembly exists only for warranty claims (M09) and workshop jobs (M31) |
| Physical-records register, distribution and acknowledgement, redaction | FR-DMS-013, 019, 024 | No models |

### Facts on fix_real (13 Nov)

- 0 documents, 0 envelopes, 0 holds, 0 disposals
- 3 templates and 4 retention classes
- Records Officer and Document Controller are held by **admin only**. No real user can place a hold, dispose of a document or approve a controlled document until someone is appointed (owner decision).
- Creating a retention class is limited to system administrators by ACL, so Retention Policy is a chip, not a + New.
