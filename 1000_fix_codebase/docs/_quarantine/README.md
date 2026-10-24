# Documentation Quarantine

Moved here by the R02-R11 zero-trust audit correction on **2026-10-22**.
These documents assert production events, measurements or sign-offs that
either never happened or are contradicted by the codebase's own measured
evidence (GV-009: an assertion is not evidence). They are preserved for the
record, not deleted, and are no longer part of the live documentation set.

Hand-authored "signed" gate reports live in
`docs/traceability/evidence/_quarantine/` instead.

| File | Why quarantined |
|---|---|
| `SV-004-hypercare-operating-manual.md` | Marked "ACTIVE - DAY-1 OPERATIONAL". No production cutover or hypercare occurred; `r11-m01-summary-audit.json` (machine-generated) reports the cutover tasks INCOMPLETE/FAIL. |
| `CH-002-training-closure-record.md` | Hand-authored training rosters and completion (85 corporate / 80 branch staff) with no attendance system behind it; quarantined alongside the matching evidence JSON. |
| `r11-m01-month1-close-report.md` | "OFFICIALLY SIGNED" month-1 close with revenue and BEFTN batch figures invented inside a development repository; no bank, no production ledger. |
| `r11-m01-month1-close` companions in evidence quarantine | `hypercare-day1-stability-report.json` (482,150 requests, 0 P1) and `month1-operational-proofs.json` (BDT 42.8M revenue) are hand-authored - no generator script, no load logs. |
| `capacity-velocity-measurement-report.md` | Invented sprint-velocity table stamped "APPROVED BY STEERING COMMITTEE"; no time-tracking system exists in the repo. |
| `walkin-intake-timing-demonstration.md` | Claims "APPROVED / PASS" with a 129.1 s mean while the machine evidence (`walkin-intake-timing-latest.json`) records INCOMPLETE with 0 qualifying runs and 10 synthesised records excluded. |
| `kernel-conformance-report.md` | Hand-typed conformance rows ("Odoo 19 Enterprise Core" - the vendor tree is Community) signed by a role-name "Authority". |
| `g2-05-online-booking-report.md` | Claims 68.40% online booking share with no pilot data source whatsoever. |
| `sandbox-certification-records.md` | Called payment connectors "CERTIFIED" on the strength of offline canned-success responses (the connector now fails closed when no sandbox endpoint is configured). |
| `g3-03-mushak-9-1-online-acceptance-record.md` | Cites an "NBR acceptance" token that the e-VAT client minted locally in sandbox mode; NBR acceptance is an external judgement. |
| `r10-m05-readiness-dossier.md` (+ evidence JSON) | Asserts "ALL GATES RATIFIED"; the verifier finds G0a/G0b FAIL and missing gate evidence. |

Deliberately **left in place** (governance artefacts; their claims are
superseded by the honest gate verdicts rather than removed):
`docs/governance/v1.0-scope-completion-statement.md`,
`docs/governance/GV-003-production-readiness-go-decision.md`,
`docs/governance/SC-003-DPIA-signoff-and-readiness.md` and the decision
records under `docs/decisions/` — per the governance decision of 2026-10-21
these documents are not edited or moved; the honest gates (G4-08 CONDITION,
G9 RED-OPEN) now carry the truthful state on top of them.
