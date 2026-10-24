"""Generate and verify the DoD-15 Security Remediation Record for R09-M05-T02.

Standard: DoD-15 (every high/critical finding remediated and re-tested;
mediums/lows assigned owners & dates).

GV-009: the previous version wrote three invented remediation actions (one
"REMEDIATED_AND_VERIFIED" with a re-test timestamp of "now"), a markdown record
of literal PASS lines ("22/22 vectors", "Bandit 0 Critical", "Signed & Verified")
and read the SAST counts from top-level keys the scan never writes (so SAST
always contributed 0). Every status below is now computed from the evidence the
pentest (run_l9_estate_pentest.py) and the SAST scan (run-security-scan.py)
wrote:

  PENTEST_CRITICAL_HIGH   critical + high findings in the latest L9 pentest run
                          (the re-test): each is listed as OPEN
  SAST_CRITICAL_HIGH      critical + high in the latest security-scan summary, and
                          that scan's own verdict
  RETEST_COVERAGE         every pentest vector was measured (an UNMEASURED vector
                          is not re-tested) -> UNMEASURED otherwise
  MEDIUM_LOW_OWNERSHIP    PASS when there are no medium/low items; otherwise owner
                          + target-date assignment needs a remediation register,
                          none is committed -> UNMEASURED

A missing input evidence file makes its checks UNMEASURED (no crash).

Emits:
- docs/traceability/evidence/r09-m05-security-remediation-evidence.json
- docs/security/DoD-15-security-remediation-record.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
SECURITY_DOCS_DIR = REPO_ROOT / "docs" / "security"
PENTEST_EVIDENCE = EVIDENCE_DIR / "r09-m05-l9-pentest-evidence.json"
SAST_EVIDENCE = REPO_ROOT / "tooling" / "fitness" / "evidence" / "security-scan-latest.json"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"
BLOCKING_SEVERITIES = ("CRITICAL", "HIGH")

OWNERSHIP_UNMEASURED = (
    "owner and target-date assignment for medium/low items needs a remediation "
    "register; none is committed to the repository"
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


def load_json(path: Path) -> tuple[dict | None, str | None]:
    if not path.is_file():
        return None, f"{path.name} not found"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("summary"), dict):
        return None, f"{path.name} has no 'summary' object"
    return data, None


def _count(summary: dict, key: str) -> int | None:
    value = summary.get(key)
    return value if isinstance(value, int) else None


def pentest_checks(pentest: dict | None, error: str | None) -> tuple[list[dict], list[dict]]:
    if pentest is None:
        reason = f"{error}; run tooling/scripts/run_l9_estate_pentest.py"
        return [
            make_check("PENTEST_CRITICAL_HIGH", UNMEASURED, reason),
            make_check("RETEST_COVERAGE", UNMEASURED, reason),
        ], []
    summary = pentest["summary"]
    findings = [f for f in pentest.get("findings") or [] if isinstance(f, dict)]
    open_items = [
        {
            "finding_code": f.get("code"),
            "severity": str(f.get("severity", "")).upper(),
            "vector": f.get("vector"),
            "target": f.get("target"),
            "status": "OPEN",
            "detail": f"reported by the pentest run at {pentest.get('timestamp')}",
        }
        for f in findings
    ]
    blocking = [i for i in open_items if i["severity"] in BLOCKING_SEVERITIES]
    critical, high = _count(summary, "critical_findings"), _count(summary, "high_findings")
    if critical is None or high is None:
        crit_high = make_check(
            "PENTEST_CRITICAL_HIGH", UNMEASURED, "pentest summary has no critical/high counts"
        )
    else:
        n = max(critical + high, len(blocking))
        codes = [i["finding_code"] for i in blocking]
        crit_high = make_check(
            "PENTEST_CRITICAL_HIGH",
            FAIL if n else PASS,
            f"{critical} critical + {high} high open in the pentest run at "
            f"{pentest.get('timestamp')}" + (f": {codes}" if codes else ""),
            critical_open=critical,
            high_open=high,
        )
    unmeasured_tests = _count(summary, "unmeasured_tests")
    unmeasured_codes = [
        r.get("code")
        for rows in (pentest.get("vector_results") or {}).values()
        if isinstance(rows, list)
        for r in rows
        if isinstance(r, dict) and r.get("outcome") == UNMEASURED
    ]
    if unmeasured_tests is None:
        coverage = make_check(
            "RETEST_COVERAGE", UNMEASURED, "pentest summary has no unmeasured_tests count"
        )
    else:
        coverage = make_check(
            "RETEST_COVERAGE",
            UNMEASURED if unmeasured_tests else PASS,
            f"{_count(summary, 'measured_tests')} of {_count(summary, 'total_tests')} vectors "
            f"measured; {unmeasured_tests} not re-tested"
            + (f": {unmeasured_codes}" if unmeasured_codes else ""),
            unmeasured_vectors=unmeasured_codes,
        )
    return [crit_high, coverage], open_items


def sast_check(sast: dict | None, error: str | None) -> dict:
    if sast is None:
        return make_check(
            "SAST_CRITICAL_HIGH", UNMEASURED, f"{error}; run tooling/scripts/run-security-scan.py"
        )
    summary = sast["summary"]
    critical, high = _count(summary, "critical"), _count(summary, "high")
    if critical is None or high is None:
        return make_check(
            "SAST_CRITICAL_HIGH", UNMEASURED, "scan summary has no critical/high counts"
        )
    verdict = sast.get("verdict")
    failed = critical + high > 0 or verdict != PASS
    return make_check(
        "SAST_CRITICAL_HIGH",
        FAIL if failed else PASS,
        f"security scan at {sast.get('timestamp')}: {critical} critical + {high} high; "
        f"scan verdict {verdict}",
        critical_open=critical,
        high_open=high,
    )


def ownership_check(pentest: dict | None, sast: dict | None) -> dict:
    if pentest is None or sast is None:
        return make_check(
            "MEDIUM_LOW_OWNERSHIP", UNMEASURED, "medium/low counts need both input evidence files"
        )
    counts = [
        _count(pentest["summary"], "medium_findings"),
        _count(pentest["summary"], "low_informational"),
        _count(sast["summary"], "medium"),
        _count(sast["summary"], "low"),
    ]
    if any(c is None for c in counts):
        return make_check("MEDIUM_LOW_OWNERSHIP", UNMEASURED, "medium/low counts missing")
    total = sum(c for c in counts if c is not None)
    if total == 0:
        return make_check("MEDIUM_LOW_OWNERSHIP", PASS, "no medium/low items need an owner")
    return make_check(
        "MEDIUM_LOW_OWNERSHIP",
        UNMEASURED,
        f"{total} medium/low items (pentest {counts[0]} medium + {counts[1]} low/info; "
        f"SAST {counts[2]} medium + {counts[3]} low); " + OWNERSHIP_UNMEASURED,
        medium_low_items=total,
    )


def build_record(pentest_path: Path = PENTEST_EVIDENCE, sast_path: Path = SAST_EVIDENCE) -> dict:
    pentest, pentest_error = load_json(pentest_path)
    sast, sast_error = load_json(sast_path)
    pen_checks, open_items = pentest_checks(pentest, pentest_error)
    sast_c = sast_check(sast, sast_error)
    checks = [pen_checks[0], sast_c, pen_checks[1], ownership_check(pentest, sast)]

    def total(key: str) -> int | None:
        values = [c.get(key) for c in (pen_checks[0], sast_c)]
        return sum(values) if all(isinstance(v, int) for v in values) else None

    crit, high = total("critical_open"), total("high_open")
    medium = None
    if pentest and sast:
        parts = [_count(pentest["summary"], "medium_findings"), _count(sast["summary"], "medium")]
        medium = sum(parts) if all(isinstance(p, int) for p in parts) else None
    verdict = overall_verdict(checks)
    return {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R09-M05",
        "task": "R09-M05-T02",
        "standard": "DoD-15 / Gate G8 Security Assurance",
        "evaluated_at": datetime.now(UTC).isoformat(),
        "inputs": {
            "pentest_evidence": pentest_path.name,
            "pentest_run_at": (pentest or {}).get("timestamp"),
            "sast_evidence": sast_path.name,
            "sast_run_at": (sast or {}).get("timestamp"),
        },
        "summary": {
            "critical_findings_open": crit,
            "high_findings_open": high,
            "medium_findings_open": medium,
            "all_critical_high_remediated": (crit == 0 and high == 0)
            if crit is not None and high is not None
            else None,
            "status": verdict,
        },
        "checks": checks,
        "remediation_actions": open_items,
    }


def render_markdown(record: dict) -> str:
    s = record["summary"]
    lines = [
        "# DoD-15 Security Remediation & Verification Record",
        "",
        "Generated by `tooling/scripts/generate_dod15_remediation.py` at "
        f"{record['evaluated_at']} from the pentest run at {record['inputs']['pentest_run_at']} "
        f"and the security scan at {record['inputs']['sast_run_at']}. Every status below is "
        "computed in that run.",
        "",
        f"**Overall status: {s['status']}** · critical open {s['critical_findings_open']} · "
        f"high open {s['high_findings_open']} · medium open {s['medium_findings_open']}",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    lines += [f"| `{c['id']}` | {c['status']} | {c['detail']} |" for c in record["checks"]]
    lines += [
        "",
        "## Findings in the latest re-test",
        "",
        "| Finding | Severity | Vector | Status |",
        "|---|---|---|:---:|",
    ]
    lines += [
        f"| `{i['finding_code']}` | {i['severity']} | {i['vector']} | {i['status']} |"
        for i in record["remediation_actions"]
    ] or ["| — | — | no findings reported | — |"]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    record = build_record()
    for check in record["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_json = EVIDENCE_DIR / "r09-m05-security-remediation-evidence.json"
    out_json.write_bytes((json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"[+] Security remediation evidence written to: {out_json}")

    SECURITY_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_md = SECURITY_DOCS_DIR / "DoD-15-security-remediation-record.md"
    out_md.write_bytes(render_markdown(record).encode("utf-8"))
    print(f"[+] DoD-15 security remediation record written to: {out_md}")
    print(f"DoD-15 status: {record['summary']['status']}")
    return exit_code(record["summary"]["status"])


if __name__ == "__main__":
    sys.exit(main())
