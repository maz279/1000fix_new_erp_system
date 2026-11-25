#!/usr/bin/env python3
"""run_final_cutover_rehearsal.py — Milestone R11-M01 Task T02 (measure-only).

Measures the final full-volume dry-run rehearsal evidence (DoD-10): counts,
checksums and control totals per MIG-02, residency per MIG-06, and the business
reconciliation pre-signature. GV-009: every status is computed from a check in
this run (the previous version hard-coded six "VERIFIED" streams, a trial
balance "to the paisa" and two named pre-signatures). What cannot be observed
here is UNMEASURED with its reason, and then the verdict is never PASS:

  DOD10_FULL_VOLUME_STAGING   production volume on migration-staging
  MIG02_EXTRACT_<STREAM>      record count + LF-normalised sha256 vs control-totals.json
  MIG02_UNMANIFESTED_EXTRACTS extract files that have no extract-time control total
  MIG02_CONTROL_TOTALS        control totals vs loaded-counts.json
  MIG02_LIVE_COUNTS           accepted records vs a read-only count in fix_migration
  FIN_OPENING_BALANCE_PARITY  opening trial balance vs legacy books (no source here)
  MIG06_RESIDENCY             no plaintext classified value in the migrated tables
  BUSINESS_PRESIGNATURE       named Data Steward / Financial Controller signatures

The measurements are shared with run_production_migration_rehearsal.py. Read-only:
nothing is written under migrations/ or to a database. Outputs:
  docs/traceability/evidence/r11-m01-final-volume-rehearsal.json
  docs/traceability/evidence/r11-m01-reconciliation-presignature.json

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_production_migration_rehearsal as rehearsal

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("final_cutover_rehearsal")

EXTRACTS_DIR = rehearsal.EXTRACTS_DIR
EVIDENCE_DIR = rehearsal.EVIDENCE_DIR
REHEARSAL_NAME = "r11-m01-final-volume-rehearsal.json"
PRESIGN_NAME = "r11-m01-reconciliation-presignature.json"
REQUIRED_SIGNATORY_ROLES = ("Lead Data Steward", "Financial Controller")

PASS = rehearsal.PASS
UNMEASURED = rehearsal.UNMEASURED
make_check = rehearsal.make_check


def unmanifested_extracts_check(extracts_dir: Path, manifest: dict) -> dict:
    """Extract files with no extract-time control total cannot be reconciled (MIG-02)."""
    control = manifest.get("control_totals") or {}
    covered = {rehearsal.extract_path(extracts_dir, manifest, s).name for s in control}
    extras = {}
    for path in sorted(extracts_dir.glob("*_extract.json")):
        if path.name in covered:
            continue
        records, error = rehearsal.read_json(path)
        extras[path.name] = {
            "record_count": len(records) if isinstance(records, list) else None,
            "sha256": rehearsal.compute_sha256(path),
            "error": error,
        }
    if not extras:
        return make_check(
            "MIG02_UNMANIFESTED_EXTRACTS", PASS, "every extract file has a control total"
        )
    return make_check(
        "MIG02_UNMANIFESTED_EXTRACTS",
        UNMEASURED,
        f"{sorted(extras)} have no extract-time control total/checksum in "
        f"{rehearsal.MANIFEST_NAME}; these streams cannot be reconciled",
        extracts=extras,
    )


def financial_parity_check() -> dict:
    return make_check(
        "FIN_OPENING_BALANCE_PARITY",
        UNMEASURED,
        "no opening trial-balance extract or ledger control total exists in "
        "migrations/extracts; parity with the legacy books cannot be measured",
        balance_variance_bdt=None,
    )


def run(
    extracts_dir: Path = EXTRACTS_DIR,
    evidence_dir: Path = EVIDENCE_DIR,
    connect: rehearsal.Connector | None = None,
) -> tuple[dict, dict]:
    measured = rehearsal.measure_migration(extracts_dir, connect)
    totals = measured["control_totals_check"]
    presign = rehearsal.signoff_check(measured, "BUSINESS_PRESIGNATURE")
    checks = [
        rehearsal.production_volume_check(measured, "DOD10_FULL_VOLUME_STAGING"),
        *measured["extract_checks"],
        unmanifested_extracts_check(extracts_dir, measured["manifest"]),
        totals,
        measured["live_counts_check"],
        financial_parity_check(),
        measured["residency_check"],
        presign,
    ]
    verdict = rehearsal.overall_verdict(checks)
    now = datetime.now(UTC).isoformat()
    extract_checks = [c for c in measured["extract_checks"] if "stream" in c]

    rehearsal_record = {
        "milestone": "R11-M01",
        "task": "R11-M01-T02",
        "tool": "tooling/scripts/run_final_cutover_rehearsal.py",
        "run_id": measured["run_id"],
        "required_target_profile": "migration-staging",
        "measured_target_database": measured["target_database"],
        "measured_at": now,
        "status": verdict,
        "summary": rehearsal.count_statuses(checks),
        "checks": checks,
        "mig02_control_totals": {
            "status": totals["status"],
            "streams_in_manifest": totals.get("streams_in_manifest"),
            "streams_reconciled": totals.get("streams_reconciled"),
            "variance_count": totals.get("variance_count"),
            "stream_counts": {c["stream"]: c["record_count"] for c in extract_checks},
        },
        "financial_balance_parity": financial_parity_check(),
        "stream_checksums": {c["stream"]: c["sha256"] for c in extract_checks},
        "mig06_sovereign_residency": measured["residency_check"],
    }
    presignature_record = {
        "governance_standard": "DoD-10 / MIG-08 / GV-003",
        "rehearsal_run_id": measured["run_id"],
        "prepared_at": now,
        "status": presign["status"],
        "reason": presign["detail"],
        "rehearsal_verdict": verdict,
        "required_signatory_roles": list(REQUIRED_SIGNATORY_ROLES),
        "signatories": [],
        "authorization": (
            f"NOT AUTHORISED: rehearsal verdict is {verdict} and no named signatory has "
            "pre-signed this run"
        ),
    }
    rehearsal.write_json(evidence_dir / REHEARSAL_NAME, rehearsal_record)
    rehearsal.write_json(evidence_dir / PRESIGN_NAME, presignature_record)
    return rehearsal_record, presignature_record


def main() -> int:
    logger.info("Measuring final full-volume cutover rehearsal evidence (DoD-10)")
    record, _ = run()
    for check in record["checks"]:
        logger.info("[%s] %s: %s", check["status"], check["id"], check["detail"])
    logger.info("Verdict: %s -> %s", record["status"], EVIDENCE_DIR / REHEARSAL_NAME)
    return rehearsal.exit_code(record["status"])


if __name__ == "__main__":
    sys.exit(main())
