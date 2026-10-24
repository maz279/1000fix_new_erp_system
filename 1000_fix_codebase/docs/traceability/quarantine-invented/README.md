# Quarantined: invented "production-volume" rehearsal artefacts (MG-005)

**Do not use as evidence.** R01 re-audit 2026-10-22.

These four untracked JSON files claimed a production-volume Wave-1 rehearsal
(`run: PROD_REHEARSAL_MG005_20261021`, `data_classification:
REAL_PRODUCTION_SHAPED`, totals such as 53 branches / 1,250 customers /
2,840 devices / 380 employees / 4,600 inventory / 520 workshop WIP). No such
rehearsal ran: the totals were written by a script, not measured from a
migration-staging database (GV-009 - an assertion is not evidence). The
MG-005 rehearsal is recorded as **NOT RUN** in `migrations/REHEARSAL.md`.

They were moved here (not deleted) so the audit trail is preserved;
`SHA256SUMS.txt` holds their hashes as found. Original locations:
`migrations/extracts/` and `tooling/migrations/extracts/`. Any document that
cites them (e.g. `docs/governance/GV-003-production-readiness-go-decision.md`)
cites invented evidence - see `docs/traceability/R01-reaudit-report-2026-10-22.md`.
