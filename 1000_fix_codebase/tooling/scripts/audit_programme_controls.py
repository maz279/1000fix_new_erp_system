#!/usr/bin/env python3
"""audit_programme_controls.py — Internal Audit of Programme Controls (R11-M03-T05).

Implements:
1. Audit of the Gate evidence chain G0a -> G9: each gate's verifier script is
   on disk and its newest evidence record is read and validated (recorded
   verdict + every recorded criterion must be PASS).
2. Audit of the GV-005 cross-wave stub ledger (closed / open / expired by
   target date - all parsed from docs/traceability/gv-005-stub-register.md).
3. Pipeline bypass controls: FF-03 (check-vendor-clean.sh run now), FF-09
   (check_ff09_residency.py run now), CI workflow bypass markers (scanned now)
   and the AR-012 §10 bypass log itself (no artefact exists to audit).
4. A computed Internal Audit opinion (IAO-2026-R11-01) derived from the checks.
5. Emits r11-m03-internal-audit-opinion.json and the Markdown opinion document.

GV-009: every status is measured in this run. Signing an audit opinion is a
human act this tool cannot observe - the sign-off is UNMEASURED, so the
verdict is never PASS on this tool's word alone. Verdict: FAIL if any check
failed, INCOMPLETE if any is UNMEASURED, else PASS. Opinion: UNQUALIFIED only
for PASS; QUALIFIED when exceptions were found; DISCLAIMER otherwise.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_DIR = REPO_ROOT / "tooling" / "gate"
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
STUB_REGISTER = REPO_ROOT / "docs" / "traceability" / "gv-005-stub-register.md"
FORKS_FILE = REPO_ROOT / "FORKS.yaml"
VENDOR_CLEAN_SCRIPT = REPO_ROOT / "tooling" / "scripts" / "check-vendor-clean.sh"
FF09_SCRIPT = REPO_ROOT / "tooling" / "fitness" / "check_ff09_residency.py"
WORKFLOW_DIRS = [REPO_ROOT.parent / ".github" / "workflows", REPO_ROOT / ".github" / "workflows"]

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
PASS_WORDS = {"PASS", "GREEN"}
BYPASS_MARKER = re.compile(
    r"continue-on-error:\s*true|--no-verify|^\s*if:\s*false\b|\|\|\s*true\b", re.IGNORECASE
)

REQUIRED_GATES = [
    ("G0a", "verify-gate-g0a.ps1", "P01/R01", "Foundations & Governance"),
    ("G0b", "verify-gate-g0b.ps1", "P01/R01", "Sovereignty & Architecture Baseline"),
    ("G1", "verify-gate-g1.ps1", "P04/R02", "Wave 1 Service Delivery Architecture"),
    ("G1a", "verify-gate-g1a.ps1", "P05/R03", "Wave 2 Field Service & Mobile App"),
    ("G2", "verify-gate-g2.ps1", "P06/R04", "Wave 3 Commercial & Billing Engine"),
    ("G3", "verify-gate-g3.ps1", "P07/R05", "Wave 4 PDPA, Agreements & Contact Centre"),
    ("G4", "verify-gate-g4.ps1", "P08/R06", "Wave 5 People, Payroll & Quality Depth"),
    ("G5", "verify-gate-g5.ps1", "P09/R07", "Wave 6 Asset Management & GRC"),
    ("G6", "verify-gate-g6.ps1", "P10/R08", "Wave 7 Advanced Automation & Integrations"),
    ("G7", "verify-gate-g7.ps1", "P11/R09", "Wave 8 BI, Warehouse & Analytics"),
    ("G8", "verify-gate-g8.ps1", "P11/R10", "Wave 9 Multi-Entity & Final Pre-Prod"),
    ("G9", "verify-gate-g9.ps1", "P12/R11", "Programme Closure & Final Acceptance"),
]


def derive_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return "INCOMPLETE"
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


# --------------------------------------------------------------- gate chain --


def find_gate_evidence(gate: str, dirs: list[Path]) -> list[Path]:
    """Evidence files of exactly this gate (``gate-g1-*`` never matches G1a)."""
    pattern = re.compile(rf"^gate-{re.escape(gate.lower())}(?:-.*)?\.json$", re.IGNORECASE)
    found = [p for d in dirs if d.is_dir() for p in d.iterdir() if pattern.match(p.name)]
    return sorted(found, key=lambda p: p.stat().st_mtime, reverse=True)


def _criteria_statuses(data: Any) -> list[str]:
    items: list[Any] = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("criteria", "criteria_verification_matrix", "checks"):
            block = data.get(key)
            if isinstance(block, list):
                items = block
                break
            if isinstance(block, dict):
                items = list(block.values())
                break
    out = []
    for item in items:
        if isinstance(item, dict):
            value = item.get("status", item.get("Status", item.get("outcome")))
            out.append(str(value).upper() if value is not None else "MISSING")
    return out


def assess_gate_evidence(data: Any) -> tuple[bool, str]:
    """(passed, detail) for one gate evidence record: the recorded verdict and
    every recorded criterion must be PASS."""
    statuses = _criteria_statuses(data)
    recorded = None
    if isinstance(data, dict):
        for key in ("overall_verdict", "verdict", "status"):
            if isinstance(data.get(key), str):
                recorded = data[key].upper()
                break
    not_pass = [s for s in statuses if s not in PASS_WORDS]
    if recorded is None and not statuses:
        return False, "evidence carries neither a verdict nor criteria"
    verdict_ok = recorded is None or recorded in PASS_WORDS
    counts = ", ".join(f"{s}={statuses.count(s)}" for s in sorted(set(statuses))) or "no criteria"
    detail = f"recorded verdict {recorded or '(none)'}; criteria {counts}"
    return verdict_ok and bool(statuses or recorded) and not not_pass, detail


def audit_gate_evidence_chain(
    gate_dir: Path = GATE_DIR, evidence_dirs: list[Path] | None = None
) -> dict[str, Any]:
    dirs = evidence_dirs if evidence_dirs is not None else [gate_dir / "evidence", EVIDENCE_DIR]
    gates = []
    for gate, script, phase, name in REQUIRED_GATES:
        script_present = (gate_dir / script).is_file()
        evidence = find_gate_evidence(gate, dirs)
        row: dict[str, Any] = {
            "gate": gate,
            "phase": phase,
            "name": name,
            "script": script,
            "script_present": script_present,
            "evidence_count": len(evidence),
        }
        if not evidence:
            row.update(status=FAIL, detail="no evidence record found for this gate")
        else:
            newest = evidence[0]
            row["evidence_file"] = _rel(newest)
            try:
                data = json.loads(newest.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as exc:
                row.update(status=FAIL, detail=f"evidence unreadable: {exc}")
            else:
                ok, detail = assess_gate_evidence(data)
                row.update(status=PASS if ok and script_present else FAIL, detail=detail)
        if not script_present:
            row["detail"] = f"verifier script missing; {row['detail']}"
        gates.append(row)
    failing = [g["gate"] for g in gates if g["status"] != PASS]
    return {
        "total_gates_audited": len(gates),
        "gates_passed": len(gates) - len(failing),
        "gates_not_passed": failing,
        "missing_scripts": [g["script"] for g in gates if not g["script_present"]],
        "all_scripts_present": all(g["script_present"] for g in gates),
        "gates": gates,
        "note": "evidence content is validated as recorded; signatures in signed reports are not verifiable here",
        "status": PASS if not failing else FAIL,
    }


# ---------------------------------------------------------------- stub ledger --


def audit_gv005_stub_ledger(register: Path = STUB_REGISTER, today: date | None = None) -> dict:
    """Closed / open / expired stubs, parsed from the GV-005 register table."""
    today = today or datetime.now(UTC).date()
    if not register.is_file():
        return {"status": FAIL, "reason": f"{register.name} missing"}
    stubs = []
    for line in register.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `STUB-"):
            continue
        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
        if len(parts) < 12:
            continue
        status = parts[11].replace("*", "").strip()
        target = parts[8].replace("*", "").strip()
        try:
            target_date: date | None = date.fromisoformat(target)
        except ValueError:
            target_date = None
        closed = status.upper() == "CLOSED"
        stubs.append(
            {
                "stub_id": parts[0].replace("`", "").strip(),
                "from_module": parts[1].replace("*", "").strip(),
                "target_module": parts[2].replace("*", "").strip(),
                "expiry_milestone": parts[7].replace("*", "").strip(),
                "target_date": target,
                "status": status,
                "is_closed": closed,
                "is_expired": (not closed) and target_date is not None and target_date < today,
            }
        )
    total = len(stubs)
    closed = sum(1 for s in stubs if s["is_closed"])
    expired = sum(1 for s in stubs if s["is_expired"])
    result: dict[str, Any] = {
        "register_document": _rel(register),
        "evaluated_on": today.isoformat(),
        "total_stubs_registered": total,
        "closed_stubs": closed,
        "open_stubs": total - closed,
        "expired_stubs": expired,
        "closure_rate": f"{closed / total * 100:.1f}%" if total else "n/a",
        "stubs": stubs,
    }
    if not total:
        result.update(status=UNMEASURED, reason="no STUB rows parsed from the register")
    else:
        result["status"] = PASS if closed == total else FAIL
    return result


# --------------------------------------------------------------- bypass log --


def _bash() -> str | None:
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if sys.platform == "win32" and git_bash.is_file():
        return str(git_bash)
    return shutil.which("bash")


def run_check(cmd: list[str], timeout: int = 300) -> tuple[int | None, str]:
    """(exit code, last output line); exit None when the command could not run."""
    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    lines = [ln.strip() for ln in (proc.stdout + proc.stderr).splitlines() if ln.strip()]
    return proc.returncode, (lines[0] if lines else "")


def count_forks(forks_file: Path = FORKS_FILE) -> int | None:
    """Entries under ``forks:`` in FORKS.yaml (None when the file is missing)."""
    if not forks_file.is_file():
        return None
    body = [ln for ln in forks_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    body = [ln for ln in body if not ln.lstrip().startswith("#")]
    return sum(1 for ln in body if re.match(r"^\s*-\s*repo\s*:", ln))


def scan_bypass_markers(workflow_dirs: list[Path]) -> tuple[int, list[str]]:
    """(workflow files scanned, non-comment lines carrying a bypass marker)."""
    files = [p for d in workflow_dirs if d.is_dir() for p in sorted(d.glob("*.y*ml"))]
    hits = []
    for wf in files:
        for n, line in enumerate(wf.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if BYPASS_MARKER.search(line):
                hits.append(f"{wf.name}:{n}: {line.strip()[:120]}")
    return len(files), hits


def audit_bypass_log(runner=run_check) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}

    bash = _bash()
    forks = count_forks()
    if bash is None or not VENDOR_CLEAN_SCRIPT.is_file():
        checks["ff03_vendor_clean"] = {
            "status": UNMEASURED,
            "reason": "bash or check-vendor-clean.sh unavailable",
        }
    else:
        code, line = runner([bash, str(VENDOR_CLEAN_SCRIPT)])
        checks["ff03_vendor_clean"] = {
            "status": UNMEASURED if code is None else (PASS if code == 0 else FAIL),
            "exit_code": code,
            "detail": line,
            "forks_yaml_entries": forks,
        }

    if not FF09_SCRIPT.is_file():
        checks["ff09_residency"] = {"status": FAIL, "reason": "check_ff09_residency.py missing"}
    else:
        code, line = runner([sys.executable, str(FF09_SCRIPT)])
        m = re.search(r"(\d+) residency bypass path", line)
        checks["ff09_residency"] = {
            "status": UNMEASURED if code is None else (PASS if code == 0 else FAIL),
            "exit_code": code,
            "detail": line,
            "residency_bypass_paths": int(m.group(1)) if m else (0 if code == 0 else None),
        }

    scanned, hits = scan_bypass_markers(WORKFLOW_DIRS)
    checks["ci_bypass_markers"] = (
        {"status": UNMEASURED, "reason": "no CI workflow files found to scan"}
        if not scanned
        else {
            "status": PASS if not hits else FAIL,
            "workflow_files_scanned": scanned,
            "markers": hits,
        }
    )
    checks["bypass_log_register"] = {
        "status": UNMEASURED,
        "reason": "no AR-012 §10 pipeline bypass log artefact exists in the repository to audit",
    }
    return {
        "checks": checks,
        "status": derive_verdict([c["status"] for c in checks.values()]),
    }


# ------------------------------------------------------------------ opinion --


def issue_internal_audit_opinion(checks: dict[str, str]) -> dict[str, Any]:
    """The opinion is derived from the check statuses, never asserted."""
    verdict = derive_verdict(list(checks.values()))
    opinion = {
        PASS: "UNQUALIFIED_CLEAN_OPINION",
        FAIL: "QUALIFIED_OPINION_EXCEPTIONS_FOUND",
    }.get(verdict, "DISCLAIMER_INSUFFICIENT_EVIDENCE")
    exceptions = [k for k, v in checks.items() if v == FAIL]
    unmeasured = [k for k, v in checks.items() if v == UNMEASURED]
    return {
        "opinion_id": "IAO-2026-R11-01",
        "programme": "1000FiX Integrated Smart ERP System v2.0",
        "governing_standard": "GV-009 (Programme Assurance & Governance Framework)",
        "scope": "Gate Evidence Chain G0a -> G9, GV-005 Stub Ledger, Pipeline Bypass Controls",
        "audit_opinion": opinion,
        "basis": {"verdict": verdict, "exceptions": exceptions, "unmeasured": unmeasured},
        "issued_at_utc": datetime.now(UTC).isoformat(),
        "status": "COMPUTED_UNSIGNED",
    }


def render_markdown(ev: dict[str, Any]) -> str:
    gate, stub, byp = ev["gate_chain_audit"], ev["stub_ledger_audit"], ev["bypass_log_audit"]
    op = ev["internal_audit_opinion"]
    lines = [
        "# Internal Audit Opinion on Programme Controls & Governance (R11-M03-T05)",
        "",
        f"**Document ID**: `{op['opinion_id']}`  ",
        "**Standard**: `GV-009` (Programme Assurance & Governance Framework) · `GV-005` (Stub Management)  ",
        f"**Evaluation Date**: {ev['evaluated_at_utc']}  ",
        f"**Computed Verdict**: **`{ev['verdict']}`** — {op['audit_opinion']}  ",
        "",
        "Every status below was measured by `tooling/scripts/audit_programme_controls.py` in this "
        "run (GV-009). A check that could not be observed is UNMEASURED and keeps the verdict "
        "from PASS.",
        "",
        "---",
        "",
        "## 1. Summary of Audit Checks",
        "",
        "| Check | Result | Detail |",
        "|---|:---:|---|",
        f"| Gate evidence chain G0a→G9 | **{gate['status']}** | {gate['gates_passed']}/"
        f"{gate['total_gates_audited']} gates PASS; not passed: "
        f"{', '.join(gate['gates_not_passed']) or 'none'} |",
        f"| GV-005 stub ledger | **{stub['status']}** | {stub.get('closed_stubs', 0)}/"
        f"{stub.get('total_stubs_registered', 0)} closed; {stub.get('open_stubs', 0)} open; "
        f"{stub.get('expired_stubs', 0)} expired |",
    ]
    for name, chk in byp["checks"].items():
        detail = (
            chk.get("reason")
            or chk.get("detail")
            or (
                "; ".join(chk.get("markers", []))
                or f"{chk.get('workflow_files_scanned', 0)} files, 0 markers"
            )
        )
        lines.append(f"| Bypass control `{name}` | **{chk['status']}** | {detail} |")
    signoff = ev["audit_sign_off"]
    lines.append(f"| Audit sign-off | **{signoff['status']}** | {signoff['reason']} |")
    lines += [
        "",
        "---",
        "",
        "## 2. Gate Evidence Chain",
        "",
        "| Gate | Name | Script | Evidence | Result | Detail |",
        "|---|---|:---:|---|:---:|---|",
    ]
    for g in gate["gates"]:
        lines.append(
            f"| `{g['gate']}` | {g['name']} | {'yes' if g['script_present'] else 'NO'} | "
            f"{g.get('evidence_file', '—')} | **{g['status']}** | {g['detail']} |"
        )
    lines += ["", "## 3. GV-005 Stub Ledger", ""]
    if stub.get("stubs"):
        lines += ["| Stub | Target Date | Status | Expired |", "|---|---|---|:---:|"]
        lines += [
            f"| `{s['stub_id']}` | {s['target_date']} | {s['status']} | "
            f"{'yes' if s['is_expired'] else 'no'} |"
            for s in stub["stubs"]
        ]
    else:
        lines.append(f"- {stub.get('reason', 'no stubs parsed')}")
    lines += [
        "",
        "## 4. Computed Opinion",
        "",
        f"- **Opinion**: `{op['audit_opinion']}` (derived from verdict `{op['basis']['verdict']}`)",
        f"- **Exceptions**: {', '.join(op['basis']['exceptions']) or 'none'}",
        f"- **Unmeasured**: {', '.join(op['basis']['unmeasured']) or 'none'}",
        "- **Signatories**: none recorded — this tool computes the opinion; signing it is a human act "
        "it cannot observe.",
        "",
    ]
    return "\n".join(lines)


def build_evidence(gate_audit: dict, stub_audit: dict, bypass_audit: dict) -> dict[str, Any]:
    sign_off = {
        "status": UNMEASURED,
        "reason": "Head of Internal Audit / Audit Committee Chair signatures are a human act; "
        "no signed opinion is observable here",
    }
    checks = {
        "gate_chain": gate_audit["status"],
        "stub_ledger": stub_audit["status"],
        **{f"bypass:{k}": v["status"] for k, v in bypass_audit["checks"].items()},
        "audit_sign_off": sign_off["status"],
    }
    opinion = issue_internal_audit_opinion(checks)
    return {
        "task_id": "R11-M03-T05",
        "milestone": "R11-M03",
        "evaluated_at_utc": datetime.now(UTC).isoformat(),
        "standards": ["GV-009", "GV-005", "AR-012 §10", "AS-05", "FF-09"],
        "gate_chain_audit": gate_audit,
        "stub_ledger_audit": stub_audit,
        "bypass_log_audit": bypass_audit,
        "audit_sign_off": sign_off,
        "checks": checks,
        "internal_audit_opinion": opinion,
        "verdict": opinion["basis"]["verdict"],
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 console must not crash the run
        sys.stdout.reconfigure(errors="replace")
    print("=" * 72)
    print("1000FiX ERP — Task R11-M03-T05: Internal Audit of Programme Controls")
    print("=" * 72)

    print("\n[1/3] Auditing Gate Evidence Chain G0a -> G9...")
    gate_audit = audit_gate_evidence_chain()
    for g in gate_audit["gates"]:
        print(f"      [{g['status']}] {g['gate']}: {g['detail']}")

    print("\n[2/3] Auditing GV-005 Cross-Wave Stub Ledger...")
    stub_audit = audit_gv005_stub_ledger()
    print(
        f"      [{stub_audit['status']}] {stub_audit.get('closed_stubs', 0)}/"
        f"{stub_audit.get('total_stubs_registered', 0)} closed, "
        f"{stub_audit.get('expired_stubs', 0)} expired"
    )

    print("\n[3/3] Auditing Pipeline Bypass Controls (FF-03, FF-09, CI markers, bypass log)...")
    bypass_audit = audit_bypass_log()
    for name, chk in bypass_audit["checks"].items():
        print(
            f"      [{chk['status']}] {name}: {chk.get('reason') or chk.get('detail') or chk.get('markers')}"
        )

    evidence = build_evidence(gate_audit, stub_audit, bypass_audit)
    opinion = evidence["internal_audit_opinion"]
    print(
        f"\n[OPINION] {opinion['audit_opinion']} ({opinion['opinion_id']}) -> {evidence['verdict']}"
    )

    json_path = EVIDENCE_DIR / "r11-m03-internal-audit-opinion.json"
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"\n[OK] Internal audit evidence JSON written: {json_path}")

    md_path = DOCS_DIR / "r11-m03-internal-audit-opinion.md"
    md_path.write_text(render_markdown(evidence), encoding="utf-8")
    print(f"[OK] Internal audit opinion written: {md_path}")

    return exit_code_for(evidence["verdict"])


if __name__ == "__main__":
    sys.exit(main())
