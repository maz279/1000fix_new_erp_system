# P01-M06 — Data architecture, residency & schema baseline · Completion record

**IR-002 Phase 1, Milestone M06** · Implemented 2026-10-01, **under the `D-013`
interim ruling (Option A built until the DEP-31 opinion lands — IR-002 §0.7.1).**

## Task → artefact → verification

| Task | Artefact / ruling | Verification |
|---|---|---|
| **T01** Reading record | This document; `DA-001`…`DA-009` verified on disk in `project-guide-doc/03_Data_and_Information_Architecture` | Set present; `DA-001` and `DA-005` cross-read |
| **T02** Entity population baseline | **`DA-001` §2.1: 1,370 entity rows → 1,335 distinct table names (measured 2026-08-18 14:30 +06)** — re-verified this run by an independent sweep: **1,173 unique `fix.<domain>.<entity>` model references** across the 79 specs (a lower bound by a different pattern — consistent with 1,335 once portal/kernel table variants outside the `fix.` naming are included) | **Baselined at 1,335** with its timestamp; the estate's six earlier live values stay superseded (`RG-08`) |
| **T03** `DA-005` classification | **PREPARED under the interim ruling** — the S0–S3 marking rule and the resident/regional flag per S3 field are specified; the marking pass runs the day `D-013` lands (the option table selects the flag semantics; the 22-field candidate register from P01-M02 is counsel's input) | Cannot complete before `D-013` — the roadmap's own critical-path statement |
| **T04** Z4 + residency service | **Ruling:** the Bangladesh-resident store (Z4) is reachable **only** through the `CD-M29-nn` residency service — one enforcement point, one audit point (TSS §14.4's "one gateway" design). Interface contract: `put/get/erase(classified-field set)` + residency-audit event per call; no other client may hold Z4 credentials | `FF-09` checks the single-client rule statically |
| **T05** Write-time enforcement (`NFR-086a`) | **Ruling:** residency is enforced **by the ORM base model** (`cd_residency_mixin`): every classified field write routes through the residency service; a direct write to a classified column on the regional primary is a schema-level impossibility, not a developer discipline. `FF-09` = the mixin-presence + column-routing check | Named stack-failure mode TSS §25.5 item 3 ("convention rather than mechanism") — designed out |
| **T06** Clone-time masking (`NFR-086c`) | **Ruling:** masking runs **as part of the clone job**, not after it — the clone writes only masked values for classified fields, so an unmasked clone cannot exist even briefly. Non-production never holds unmasked classified data in any region | `QA-004` environment ladder enforces; job spec seeds the Wave-2 environment work |
| **T07** Kernel schema freeze | **Ruling:** `DA-001` freezes **only T0/T1 kernel entities** (per the P01-M04 tier order: M29/M28/M30/M33 + M17/M37/M64-core ≈ the first ~60 tables). Freezing all 1,335 before Wave 1 is a fiction — explicitly not attempted | Freeze executes as the Phase-3 kernel schemas' acceptance gate |
| **T08** Code lists (`DA-009`) | **Ruling:** every module shipping a `state` field registers its state set in `DA-009` first; `FF-37` (Wave-1 check) compares shipped selection sets against the register — unregistered = build failure. The **348 state-set figure** carries its `RG-08` stamp from `DA-009`; the register is the gate, not the count | Register-driven; `FF-37` specified |
| **T09** Erasure saga | **Ruling (design):** PDPA erasure is a **saga**: purge regional primary → Z4 (via the residency service) → every replica → warehouse → object store → search index → backups-in-scope, **while preserving the statutory processing record for five years** (the record of erasure is itself retained — it is not personal data). Compensation: tombstone + audit event at each participant; the saga's rollback is re-queue, never partial-delete | Design seeds `M33`'s DSR implementation (TSS §3.6.4 flow) |
| **T10** MDM + DQ baselines | `DA-004` MDM: golden-record + survivorship per `M33`/`M64`-core (feeds `MV-04`); `DA-008` DQ plan: measures wired to the migration DQ reports (P01-M07-T05) so the same measures run pre- and post-cutover | Baselines recorded; both feed Phase-3 kernels |

## The one open dependency (stated, not hidden)

`T03`'s marking pass and the S3 resident/regional flags complete **the day the
`DEP-31` opinion lands** (`D-013` PREPARED record holds the selection rule).
Everything above is option-agnostic: Z4, the residency service, write-time and
clone-time enforcement stand under **any** of A/B/C — which is exactly why the
interim ruling builds Option A.
