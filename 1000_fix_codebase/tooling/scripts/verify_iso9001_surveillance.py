#!/usr/bin/env python3
"""verify_iso9001_surveillance.py — ISO 9001:2015 Surveillance & CON-11 Audit (R11-M03-T03).

GV-009: the previous version wrote four invented internal audits, three invented
NCRs/CAPAs (ESD wrist-strap, skewed barcode label, ...), an invented certificate
("ISO-9001-BGD-2026-042", "MAINTAINED", a named lead auditor) and a markdown
report of literal **PASS** rows ending "CERTIFICATE UNCONDITIONALLY MAINTAINED".
Every status below is now computed in this run:

  M23_QMS_MODELS_PRESENT        cd_qms_process defines fix.internal.audit, fix.ncr
                                and fix.capa (AST scan of its models/)
  CAPA_CLOSE_REQUIRES_VERIFICATION
                                fix.capa.action_close refuses closure unless the CAPA
                                is 'verified' (AST: a raise guarded by that compare)
  QMS_AUDIT_RECORDS             production M23 audit / NCR / CAPA records never reach
  CON11_ZERO_MAJOR_SYSTEM_NCRS  a workstation (DE-12); the dev database holds only
  CAPA_CLOSURE_RATE             synthetic seed rows, which say nothing about the
                                certified QMS -> UNMEASURED
  SURVEILLANCE_CERTIFICATE      the certification body's surveillance report -> UNMEASURED

Emits:
- docs/traceability/evidence/r11-m03-iso9001-surveillance-result.json
- docs/traceability/r11-m03-iso9001-surveillance-report.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import ast
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
QMS_MODELS_DIR = REPO_ROOT / "addons" / "domain" / "i_governance" / "cd_qms_process" / "models"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"

REQUIRED_MODELS = ("fix.internal.audit", "fix.ncr", "fix.capa")

RECORDS_UNMEASURED = (
    "production M23 records (fix.internal.audit / fix.ncr / fix.capa) are not available "
    "on a workstation (DE-12); the local database holds synthetic seed rows only. "
    "Requires an export from the production QMS for the surveillance period"
)
CERTIFICATE_UNMEASURED = (
    "certificate maintenance is decided by the external certification body; requires "
    "its ISO 9001:2015 surveillance audit report"
)


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _model_name(node: ast.ClassDef) -> str | None:
    for stmt in node.body:
        if (
            isinstance(stmt, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "_name" for t in stmt.targets)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        ):
            return stmt.value.value
    return None


def scan_models(models_dir: Path) -> tuple[dict[str, ast.ClassDef], list[str]]:
    """Map Odoo model name -> class node for every models/*.py; also parse errors."""
    found: dict[str, ast.ClassDef] = {}
    errors: list[str] = []
    for path in sorted(models_dir.glob("*.py")) if models_dir.is_dir() else []:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, ValueError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and (name := _model_name(node)):
                found.setdefault(name, node)
    return found, errors


def models_present_check(
    found: dict[str, ast.ClassDef], errors: list[str], models_dir: Path
) -> dict:
    if not models_dir.is_dir():
        return make_check("M23_QMS_MODELS_PRESENT", FAIL, f"{models_dir} not found")
    missing = [m for m in REQUIRED_MODELS if m not in found]
    detail = (
        f"missing {missing}"
        if missing
        else f"{', '.join(REQUIRED_MODELS)} defined in cd_qms_process"
    )
    if errors:
        detail += f"; unparseable: {errors}"
    return make_check(
        "M23_QMS_MODELS_PRESENT",
        FAIL if missing or errors else PASS,
        detail,
        models_found=sorted(m for m in REQUIRED_MODELS if m in found),
    )


def _guards_on_verified(func: ast.FunctionDef) -> bool:
    """True when the method holds an `if <...> 'verified' ...: raise` guard."""
    for node in ast.walk(func):
        if not isinstance(node, ast.If):
            continue
        compares_verified = any(
            isinstance(sub, ast.Constant) and sub.value == "verified" for sub in ast.walk(node.test)
        )
        raises = any(isinstance(stmt, ast.Raise) for stmt in node.body)
        if compares_verified and raises:
            return True
    return False


def capa_close_check(found: dict[str, ast.ClassDef]) -> dict:
    capa = found.get("fix.capa")
    if capa is None:
        return make_check("CAPA_CLOSE_REQUIRES_VERIFICATION", FAIL, "fix.capa model not found")
    close = next(
        (n for n in capa.body if isinstance(n, ast.FunctionDef) and n.name == "action_close"), None
    )
    if close is None:
        return make_check(
            "CAPA_CLOSE_REQUIRES_VERIFICATION", FAIL, "fix.capa has no action_close method"
        )
    ok = _guards_on_verified(close)
    return make_check(
        "CAPA_CLOSE_REQUIRES_VERIFICATION",
        PASS if ok else FAIL,
        "fix.capa.action_close raises unless the CAPA is 'verified'"
        if ok
        else "fix.capa.action_close has no raise guarded on the 'verified' state",
    )


def audit_qms_estate(models_dir: Path = QMS_MODELS_DIR) -> dict:
    found, errors = scan_models(models_dir)
    checks = [
        models_present_check(found, errors, models_dir),
        capa_close_check(found),
        make_check("QMS_AUDIT_RECORDS", UNMEASURED, RECORDS_UNMEASURED),
        make_check("CON11_ZERO_MAJOR_SYSTEM_NCRS", UNMEASURED, RECORDS_UNMEASURED),
        make_check("CAPA_CLOSURE_RATE", UNMEASURED, RECORDS_UNMEASURED),
        make_check("SURVEILLANCE_CERTIFICATE", UNMEASURED, CERTIFICATE_UNMEASURED),
    ]
    con11 = next(c for c in checks if c["id"] == "CON11_ZERO_MAJOR_SYSTEM_NCRS")
    cert = next(c for c in checks if c["id"] == "SURVEILLANCE_CERTIFICATE")
    return {
        "task_id": "R11-M03-T03",
        "milestone": "R11-M03",
        "evaluated_at_utc": datetime.now(UTC).isoformat(),
        "standards": ["ISO 9001:2015", "CON-11 Binding Rule", "M23 QMS Process"],
        "checks": checks,
        "qms_audit": {
            "audits_conducted": None,
            "major_non_conformances_traced_to_systems": None,
            "unclosed_capas": None,
            "con11_verdict": con11["status"],
            "status": UNMEASURED,
            "detail": RECORDS_UNMEASURED,
        },
        "surveillance_certificate": {"status": cert["status"], "detail": CERTIFICATE_UNMEASURED},
        "summary": {
            "checks_passed": sum(1 for c in checks if c["status"] == PASS),
            "checks_failed": sum(1 for c in checks if c["status"] == FAIL),
            "checks_unmeasured": sum(1 for c in checks if c["status"] == UNMEASURED),
        },
        "verdict": overall_verdict(checks),
    }


def render_markdown(evidence: dict) -> str:
    lines = [
        "# ISO 9001:2015 Surveillance & CON-11 Audit (R11-M03-T03)",
        "",
        "Generated by `tooling/scripts/verify_iso9001_surveillance.py` at "
        f"{evidence['evaluated_at_utc']}. Every status below is computed in that run.",
        "",
        f"**Verdict: {evidence['verdict']}** · CON-11: {evidence['qms_audit']['con11_verdict']} · "
        f"Surveillance certificate: {evidence['surveillance_certificate']['status']}",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    lines += [f"| `{c['id']}` | {c['status']} | {c['detail']} |" for c in evidence["checks"]]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    print("=" * 72)
    print("1000FiX ERP — Task R11-M03-T03: ISO 9001:2015 Surveillance & CON-11 Audit")
    print("=" * 72)
    evidence = audit_qms_estate()
    for check in evidence["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m03-iso9001-surveillance-result.json"
    json_path.write_bytes(
        (json.dumps(evidence, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = DOCS_DIR / "r11-m03-iso9001-surveillance-report.md"
    md_path.write_bytes(render_markdown(evidence).encode("utf-8"))

    print(f"\nVerdict: {evidence['verdict']}")
    print(f"[OK] ISO 9001 evidence JSON written: {json_path}")
    print(f"[OK] ISO 9001 audit report written: {md_path}")
    return exit_code(evidence["verdict"])


if __name__ == "__main__":
    sys.exit(main())
