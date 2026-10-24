#!/usr/bin/env python3
"""verify_r10_m05_all.py — Master Verifier for Milestone R10-M05: Production-Readiness Review.

Validates all 4 milestone tasks:
  T01: Readiness Dossier & Steering Pack (G0a–G8+GP, DoD-03, security, DR, 12 envs, 67/67 census, OpenAPI 100%)
  T02: Production Migration Rehearsal (MG-005, MIG-02 control totals, MG-007 rollback, MG-004 sign-off, Gate GP-11)
  T03: Training Closure (D-002 super-users, CH-002 role playbooks, training environment, completion >= plan)
  T04: Production-Readiness Review Board (GV-003 Go decision, named entry conditions, rollback triggers)

GV-009: every task verdict is derived from the CURRENT verdicts of the evidence
the task rests on - never from a keyword found in a document (a document can
claim anything). A claim the dossier/decision makes is checked against the
evidence it cites; a cited run that was quarantined as invented
(docs/traceability/quarantine-invented/) fails the task; human attestations
(certifications, votes, sign-offs) are UNMEASURED by this run, never PASS.
Overall: FAIL if any task FAILs, INCOMPLETE if any is INCOMPLETE, else PASS.
Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

CODEBASE_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = CODEBASE_ROOT / "docs" / "traceability" / "evidence"
QUARANTINE_DIR = CODEBASE_ROOT / "docs" / "traceability" / "quarantine-invented"
FITNESS_EVIDENCE_DIR = CODEBASE_ROOT / "tooling" / "fitness" / "evidence"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_r10_m05")

PASS_WORDS = {"PASS", "PASSED", "GREEN", "SUCCESS"}
INCOMPLETE_WORDS = {"INCOMPLETE", "UNMEASURED", "CONDITION", "CONDITIONAL"}
VERDICT_KEYS = ("overall_status", "overall_verdict", "verdict", "status")


def normalise(value: object) -> str:
    word = str(value).strip().upper() if value is not None else ""
    if word in PASS_WORDS:
        return "PASS"
    if word in INCOMPLETE_WORDS:
        return "INCOMPLETE"
    return "FAIL"


def combine(*states: str) -> str:
    if any(s == "FAIL" for s in states):
        return "FAIL"
    if any(s == "INCOMPLETE" for s in states):
        return "INCOMPLETE"
    return "PASS"


def read_json(path: Path) -> tuple[dict | None, str]:
    if not path.is_file():
        return None, f"{path.relative_to(CODEBASE_ROOT).as_posix()} missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"
    return (data, "") if isinstance(data, dict) else (None, f"{path.name} is not an object")


def evidence_verdict(data: dict) -> str:
    """The verdict an evidence file states for itself (its own computed field)."""
    for key in VERDICT_KEYS:
        if isinstance(data.get(key), str):
            return normalise(data[key])
    summary = data.get("summary")
    if isinstance(summary, dict):
        for key in VERDICT_KEYS:
            if isinstance(summary.get(key), str):
                return normalise(summary[key])
    return "FAIL"


def quarantined_run_ids(quarantine_dir: Path | None = None) -> set[str]:
    """Run ids of artefacts quarantined as invented (file stem up to the first '-')."""
    quarantine_dir = quarantine_dir or QUARANTINE_DIR
    if not quarantine_dir.is_dir():
        return set()
    return {p.name.split("-", 1)[0] for p in quarantine_dir.rglob("*.json")}


def invented_artefacts_present() -> list[str]:
    """Quarantined run ids that reappeared anywhere a pipeline would read them."""
    ids = quarantined_run_ids()
    found = []
    for folder in (
        CODEBASE_ROOT / "migrations" / "extracts",
        CODEBASE_ROOT / "tooling" / "migrations" / "extracts",
    ):
        if folder.is_dir():
            found += [
                p.relative_to(CODEBASE_ROOT).as_posix()
                for p in folder.glob("*.json")
                if p.name.split("-", 1)[0] in ids
            ]
    return found


def task(task_id: str, title: str, checks: list[dict], **extra) -> dict:
    status = combine(*(c["status"] for c in checks)) if checks else "FAIL"
    logger.info("Task %s: %s", task_id, status)
    for c in checks:
        if c["status"] != "PASS":
            logger.info("  [%s] %s: %s", c["status"], c["check"], c["detail"])
    return {"task_id": task_id, "title": title, "status": status, **extra, "checks": checks}


def check(name: str, status: str, detail: str) -> dict:
    return {"check": name, "status": status, "detail": detail}


def cited_evidence_check(name: str, rel_path: str) -> dict:
    data, problem = read_json(CODEBASE_ROOT / rel_path)
    if data is None:
        return check(name, "FAIL", f"cited evidence {problem}")
    verdict = evidence_verdict(data)
    return check(name, verdict, f"{rel_path} currently states {verdict}")


def verify_t01_readiness_dossier() -> dict:
    logger.info("--- [1/4] Verifying Task R10-M05-T01: Readiness Dossier & Steering Pack ---")
    checks = []
    for rel in (
        "docs/traceability/r10-m05-readiness-dossier.md",
        "docs/traceability/r10-m05-steering-pack.md",
    ):
        present = (CODEBASE_ROOT / rel).is_file()
        checks.append(
            check(
                f"document {rel}",
                "PASS" if present else "FAIL",
                "present" if present else "missing",
            )
        )
    dossier, problem = read_json(EVIDENCE_DIR / "r10-m05-readiness-dossier-evidence.json")
    if dossier is None:
        checks.append(check("dossier evidence", "FAIL", problem))
        return task("R10-M05-T01", "Compile the readiness dossier", checks)
    # every gate the dossier records as PASS must be PASS in the evidence it cites
    for gate, record in (dossier.get("gate_records") or {}).items():
        cited = str(record.get("evidence", ""))
        if cited.endswith(".json"):
            checks.append(cited_evidence_check(f"gate {gate}", cited))
        else:
            checks.append(
                check(
                    f"gate {gate}",
                    "INCOMPLETE",
                    f"cites {cited or 'nothing'}, not an evidence record",
                )
            )
    # DoD-03: the dossier claims every fitness function green - check the newest run
    runs = sorted(FITNESS_EVIDENCE_DIR.glob("fitness-*.json"))
    if runs:
        data, _ = read_json(runs[-1])
        results = (data or {}).get("results", [])
        failed = [r.get("suite") for r in results if r.get("status") == "FAIL"]
        checks.append(
            check(
                "DoD-03 fitness functions",
                "FAIL" if failed or not results else "PASS",
                f"{runs[-1].name}: {len(results)} checks, failing {failed or 'none'}",
            )
        )
    else:
        checks.append(check("DoD-03 fitness functions", "FAIL", "no fitness run evidence"))
    # security and DR figures the dossier quotes come from these evidence files
    for name, rel in (
        (
            "security closure (L9 pentest)",
            "docs/traceability/evidence/r09-m05-l9-pentest-evidence.json",
        ),
        ("DR rehearsal (RPO/RTO)", "docs/traceability/evidence/r10-m04-dr-rehearsal-evidence.json"),
    ):
        checks.append(cited_evidence_check(name, rel))
    return task(
        "R10-M05-T01", "Compile the readiness dossier", checks, dossier_id=dossier.get("dossier_id")
    )


def verify_t02_migration_rehearsal() -> dict:
    logger.info("--- [2/4] Verifying Task R10-M05-T02: Production Migration Rehearsal (MG-005) ---")
    checks = []
    rehearsal, problem = read_json(EVIDENCE_DIR / "r10-m05-migration-rehearsal-evidence.json")
    run_id = None
    mg005 = "NOT RUN"
    if rehearsal is None:
        checks.append(check("MG-005 rehearsal evidence", "FAIL", problem))
    else:
        run_id = rehearsal.get("run_id")
        verdict = evidence_verdict(rehearsal)
        discharged = rehearsal.get("gp_11_discharged") is True
        if verdict == "PASS" and discharged:
            mg005 = "RUN"
        checks.append(
            check(
                "MG-005 production-volume rehearsal",
                "PASS" if mg005 == "RUN" else "FAIL",
                f"rehearsal evidence states {verdict}, GP-11 discharged={discharged} -> MG-005 {mg005}",
            )
        )
        if run_id and run_id in quarantined_run_ids():
            checks.append(check("rehearsal run id", "FAIL", f"{run_id} is quarantined as invented"))
    signoff, problem = read_json(EVIDENCE_DIR / "r10-m05-mg004-business-signoff.json")
    checks.append(
        check("MG-004 business sign-off", "FAIL", problem)
        if signoff is None
        else check(
            "MG-004 business sign-off",
            evidence_verdict(signoff),
            f"sign-off evidence states {signoff.get('verdict', signoff.get('status'))}",
        )
    )
    invented = invented_artefacts_present()
    checks.append(
        check(
            "no invented rehearsal artefacts in the extract set",
            "FAIL" if invented else "PASS",
            f"quarantined run artefacts present: {invented}" if invented else "none present",
        )
    )
    return task(
        "R10-M05-T02",
        "Production migration rehearsal (MG-005, GP-11)",
        checks,
        run_id=run_id,
        mg005=mg005,
    )


def verify_t03_training_closure() -> dict:
    logger.info("--- [3/4] Verifying Task R10-M05-T03: Training Closure & Super-User Network ---")
    checks = []
    record = CODEBASE_ROOT / "docs" / "training" / "CH-002-training-closure-record.md"
    checks.append(
        check(
            "CH-002 closure record",
            "PASS" if record.is_file() else "FAIL",
            "present" if record.is_file() else "missing",
        )
    )
    training, problem = read_json(EVIDENCE_DIR / "r10-m05-training-closure-evidence.json")
    if training is None:
        checks.append(check("training evidence", "FAIL", problem))
    else:
        targets = training.get("targets", {})
        checks.append(
            check(
                "super-user certifications",
                "INCOMPLETE",
                f"{targets.get('certified_super_users')} certified super-users recorded - human "
                "certifications, UNMEASURED by this run",
            )
        )
    return task(
        "R10-M05-T03",
        "Training closure (D-002, CH-002)",
        checks,
        roster_id=(training or {}).get("roster_id"),
    )


def verify_t04_review_board_go(prerequisites: dict[str, str] | None = None) -> dict:
    logger.info(
        "--- [4/4] Verifying Task R10-M05-T04: Production-Readiness Review Board Go Decision ---"
    )
    checks = []
    decision_md = (
        CODEBASE_ROOT / "docs" / "governance" / "GV-003-production-readiness-go-decision.md"
    )
    decision, problem = read_json(EVIDENCE_DIR / "r10-m05-go-nogo-decision.json")
    if not decision_md.is_file() or decision is None:
        checks.append(
            check("GV-003 decision record", "FAIL", problem or "decision markdown missing")
        )
        return task("R10-M05-T04", "Production-readiness review board (GV-003 Go decision)", checks)
    text = decision_md.read_text(encoding="utf-8")
    cited_invented = sorted(rid for rid in quarantined_run_ids() if rid in text)
    checks.append(
        check(
            "decision cites no invented evidence",
            "FAIL" if cited_invented else "PASS",
            f"GV-003 cites quarantined run(s) {cited_invented}"
            if cited_invented
            else "no quarantined run cited",
        )
    )
    # a GO stands only on prerequisites that hold today
    for name, status in (prerequisites or {}).items():
        checks.append(check(f"prerequisite {name}", status, f"{name} currently {status}"))
    for name, rel in (
        ("DR rehearsal", "docs/traceability/evidence/r10-m04-dr-rehearsal-evidence.json"),
        ("HA kill-node drills", "docs/traceability/evidence/r10-m04-ha-kill-node-evidence.json"),
    ):
        checks.append(cited_evidence_check(f"prerequisite {name}", rel))
    votes = decision.get("votes", {})
    checks.append(
        check(
            "board votes",
            "INCOMPLETE",
            f"{votes.get('go_votes')}/{votes.get('total_board_members')} GO votes recorded - human "
            "attestations, UNMEASURED by this run",
        )
    )
    return task(
        "R10-M05-T04",
        "Production-readiness review board (GV-003 Go decision)",
        checks,
        decision_record=decision.get("decision_record"),
        recorded_determination=decision.get("determination"),
    )


def summarise(results: list[dict]) -> dict:
    status = combine(*(r["status"] for r in results)) if results else "FAIL"
    return {
        "milestone": "R10-M05",
        "title": "Production-readiness review",
        "verified_at": datetime.now(UTC).isoformat(),
        "overall_status": status,
        "tasks_passed": sum(1 for r in results if r["status"] == "PASS"),
        "tasks_incomplete": sum(1 for r in results if r["status"] == "INCOMPLETE"),
        "tasks_failed": sum(1 for r in results if r["status"] == "FAIL"),
        "tasks_summary": {r["task_id"]: r for r in results},
        "all_tasks_completed": status == "PASS",
    }


def main() -> int:
    logger.info("======================================================================")
    logger.info("STARTING MASTER VERIFICATION: MILESTONE R10-M05 (PRODUCTION-READINESS REVIEW)")
    logger.info("======================================================================")
    t01 = verify_t01_readiness_dossier()
    t02 = verify_t02_migration_rehearsal()
    t03 = verify_t03_training_closure()
    t04 = verify_t04_review_board_go(
        {
            "readiness dossier (T01)": t01["status"],
            "MG-005 migration rehearsal (T02)": t02["status"],
            "training closure (T03)": t03["status"],
        }
    )
    summary = summarise([t01, t02, t03, t04])
    summary_path = EVIDENCE_DIR / "r10-m05-summary-audit.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    logger.info("Saved summary audit to %s", summary_path)
    logger.info(
        "MILESTONE R10-M05: %s (%d PASS / %d INCOMPLETE / %d FAIL)",
        summary["overall_status"],
        summary["tasks_passed"],
        summary["tasks_incomplete"],
        summary["tasks_failed"],
    )
    return {"PASS": 0, "FAIL": 1}.get(summary["overall_status"], 2)


if __name__ == "__main__":
    sys.exit(main())
