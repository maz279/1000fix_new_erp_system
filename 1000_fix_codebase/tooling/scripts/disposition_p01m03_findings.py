#!/usr/bin/env python3
"""disposition_p01m03_findings.py — Task R10-M02-T06 & Traceability Evidence Generator.

1. Classifies any undeclared priority rows in fit-gap-register.csv into the
   established P0/P1/P2 scheme (F-P01M03-4 ruling). ``--dry-run`` measures only
   and never rewrites the register; the register is rewritten only when it
   actually holds undeclared rows.
2. Re-measures the dependency reciprocity drift (F-P01M04-2) by running the
   FF-14 extractor (tooling/architecture-baseline/extract-dependency-graph.ps1)
   and compares it with the ratified baseline.
3. Emits docs/traceability/r10-m02-disposition-register.md and
   docs/traceability/evidence/r10-m02-disposition-evidence.json.
4. Emits RTM evidence files for M25, M26, M32 and M42, each measured from the
   module's CR register (docs/r10/), the RTM seed and the delivery units on disk.

GV-009: every status is computed in this run. The Change Board's ratification
of the rulings is a human approval this tool cannot observe - it is reported
UNMEASURED, so the disposition verdict is never PASS on this tool's word alone.
Verdict: FAIL if any check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
FIT_GAP_CSV = REPO_ROOT / "docs" / "p01-m03" / "registers" / "fit-gap-register.csv"
RTM_SEED_CSV = REPO_ROOT / "docs" / "p01-m03" / "registers" / "rtm-seed.csv"
CR_DIR = REPO_ROOT / "docs" / "r10"
DISPOSITION_MD = REPO_ROOT / "docs" / "traceability" / "r10-m02-disposition-register.md"
DISPOSITION_EVIDENCE = (
    REPO_ROOT / "docs" / "traceability" / "evidence" / "r10-m02-disposition-evidence.json"
)
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DEP_GRAPH_SCRIPT = REPO_ROOT / "tooling" / "architecture-baseline" / "extract-dependency-graph.ps1"

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
VALID_PRIORITIES = ("P0", "P1", "P2")
DISPOSITION_MARKER = "[R10-M02 Disposition: classified"
# Targets the rulings compare against (not measurements): AR-006 section 4
# estimated 55 reciprocity anomalies; the F-P01M04-2 ruling ratifies 53 as
# the baseline, so any re-measured drift from 53 re-opens the finding.
AR006_RECIPROCITY_ESTIMATE = 55
RATIFIED_RECIPROCITY_BASELINE = 53
REPO_PATH_TOKEN = re.compile(
    r"^(?:addons|services|infra|tests|tooling|libs|docs|apps|contracts|db|dags)/"
)

RTM_MODULES: list[dict[str, Any]] = [
    {
        "module_id": "M25",
        "task": "R10-M02-T01",
        "cr_id": "CR-R10M02-01",
        "title": "M25 Business Intelligence & Reporting Traceability Matrix",
        "prefix": "FR-BID",
        "file": "r10-m02-m25-rtm.json",
        "delivery_units": [
            ("addons/domain/j_data_analytics/cd_metric_registry", None, "metric registry"),
            ("infra/compose/docker-compose.superset.yml", None, "Apache Superset"),
            ("services/bi-warehouse", None, "ClickHouse & dbt analytical warehouse"),
        ],
    },
    {
        "module_id": "M26",
        "task": "R10-M02-T02",
        "cr_id": "CR-R10M02-02",
        "title": "M26 AI/ML Services & Model Operations Traceability Matrix",
        "prefix": "FR-AIM",
        "file": "r10-m02-m26-rtm.json",
        "delivery_units": [
            ("services/ml-gateway", None, "FastAPI inference gateway"),
            ("infra/compose/docker-compose.asset-ml.yml", "mlflow:", "MLflow model registry"),
            ("infra/compose/docker-compose.asset-ml.yml", "ollama:", "Ollama local LLM runtime"),
            ("services/stt", None, "Bengali speech-to-text & drift monitoring"),
            ("addons/domain/a_service_delivery/cd_field_service", None, "dispatch ML"),
        ],
    },
    {
        "module_id": "M32",
        "task": "R10-M02-T03",
        "cr_id": "CR-R10M02-03",
        "title": "M32 Conversational AI & Virtual Assistant Traceability Matrix",
        "prefix": "FR-CAI",
        "file": "r10-m02-m32-rtm.json",
        "delivery_units": [
            ("addons/domain/b_customer_engagement/cd_contact_centre", None, "contact centre"),
            (
                "infra/compose/docker-compose.asset-ml.yml",
                "ollama:",
                "Ollama self-hosted assistant",
            ),
            ("services/conversational-ai", None, "benchmark & intent runtime"),
            (
                "addons/domain/b_customer_engagement/cd_contact_centre/models/assistant_engine.py",
                "R07-M04-T04",
                "R07 knowledge upgrade (M61 knowledge-base intents)",
            ),
        ],
    },
    {
        "module_id": "M42",
        "task": "R10-M02-T04",
        "cr_id": "CR-R10M02-04",
        "title": "M42 Supplier Relationship & Performance Traceability Matrix",
        "prefix": "FR-SRM2",
        "file": "r10-m02-m42-rtm.json",
        "delivery_units": [
            (
                "addons/domain/b_customer_engagement/cd_cx_feedback",
                None,
                "Pair 10 scorecard engine",
            ),
            ("addons/domain/e_supply_chain/cd_vendor_portal", None, "P05 supplier portal"),
            ("tests/test_m16_m42_break.py", None, "Pair 10 cycle-break verification"),
        ],
        "break_test": "tests/test_m16_m42_break.py",
    },
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


def classify_priority(row: dict) -> str:
    """Classifies undeclared requirement rows into the standard P0/P1/P2 scheme."""
    current = row.get("priority", "").strip()
    if current in VALID_PRIORITIES:
        return current

    wave = row.get("wave", "").strip()
    module = row.get("module", "").strip()

    # P0: Core statutory, financial, tax, compliance, and foundational service delivery
    p0_modules = {"M19", "M20", "M50", "M51", "M52", "M56", "M60", "M29", "M30", "M01", "M15"}
    if module in p0_modules and wave in ("W1", "W2"):
        return "P0"

    # P2: Advanced optimization, predictive ML, ecosystem growth, or late waves
    p2_modules = {"M13", "M14", "M39", "M46", "M47", "M48"}
    if wave in ("W7", "W8", "W9") or module in p2_modules:
        return "P2"

    # P1: Standard operational business workflows
    return "P1"


def _clean_field(name: str | None) -> str:
    """Header cell without BOM / stray quotes (an earlier rewrite of the
    register wrapped the BOM-prefixed header in literal quotes)."""
    return (name or "").replace("﻿", "").strip().strip('"').strip()


def read_register(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, encoding="utf-8-sig", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = [_clean_field(n) for n in reader.fieldnames or []]
        rows = [
            {_clean_field(k): (v or "") for k, v in raw.items() if k is not None} for raw in reader
        ]
    return fieldnames, rows


def measure_priorities(apply: bool, register: Path | None = None) -> dict[str, Any]:
    """F-P01M03-4: count (and, when ``apply``, classify) undeclared priorities."""
    register = register or FIT_GAP_CSV
    if not register.is_file():
        return {"status": FAIL, "reason": f"fit-gap register missing: {register}"}
    fieldnames, rows = read_register(register)
    if not rows or "priority" not in fieldnames:
        return {"status": FAIL, "reason": "fit-gap register has no rows or no priority column"}
    undeclared_before = [r for r in rows if r.get("priority", "").strip() not in VALID_PRIORITIES]
    classified_now = 0
    if apply and undeclared_before:
        for r in undeclared_before:
            new_p = classify_priority(r)
            r["priority"] = new_p
            r["note"] = (
                r.get("note", "") + f" {DISPOSITION_MARKER} {new_p} per F-P01M03-4 ruling]"
            ).strip()
            classified_now += 1
        with open(register, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(rows)
    undeclared_after = [r for r in rows if r.get("priority", "").strip() not in VALID_PRIORITIES]
    dist = Counter(r.get("priority", "").strip() or "(none)" for r in rows)
    return {
        "status": PASS if not undeclared_after else FAIL,
        "register": register.relative_to(REPO_ROOT).as_posix()
        if register.is_relative_to(REPO_ROOT)
        else str(register),
        "mode": "dry-run (register not rewritten)"
        if not apply
        else ("apply (register rewritten)" if classified_now else "apply (nothing to classify)"),
        "total_requirements": len(rows),
        "undeclared_before_run": len(undeclared_before),
        "classified_this_run": classified_now,
        "undeclared_after_run": len(undeclared_after),
        "rows_carrying_r10_m02_disposition_marker": sum(
            1 for r in rows if DISPOSITION_MARKER in r.get("note", "")
        ),
        "priority_distribution": dict(sorted(dist.items())),
    }


def _powershell() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


def measure_reciprocity(script: Path | None = None, timeout: int = 300) -> dict[str, Any]:
    """F-P01M04-2: run the FF-14 extractor (JSON to a temp dir only) and compare."""
    script = script or DEP_GRAPH_SCRIPT
    shell = _powershell()
    if shell is None:
        return {"status": UNMEASURED, "reason": "no powershell/pwsh to run the FF-14 extractor"}
    if not script.is_file():
        return {"status": UNMEASURED, "reason": f"FF-14 extractor missing: {script}"}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dependency-graph.json"
        cmd = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
        cmd += ["-Json", str(out)]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"status": UNMEASURED, "reason": f"FF-14 extractor not runnable: {exc}"}
        if not out.is_file():
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
            return {
                "status": UNMEASURED,
                "reason": f"FF-14 extractor exit {proc.returncode} wrote no graph: {' | '.join(tail)}",
            }
        try:
            data = json.loads(out.read_text(encoding="utf-8-sig"))
        except ValueError as exc:
            return {"status": FAIL, "reason": f"FF-14 graph JSON unreadable: {exc}"}
    total = data.get("reciprocityTotal")
    if not isinstance(total, int):
        return {"status": FAIL, "reason": "FF-14 graph JSON has no reciprocityTotal"}
    by_module = data.get("reciprocityFailures") or {}
    return {
        "status": PASS if total == RATIFIED_RECIPROCITY_BASELINE else FAIL,
        "extractor_exit_code": proc.returncode,
        "reciprocity_measured": total,
        "reciprocity_by_module": dict(sorted(by_module.items(), key=lambda kv: -kv[1])),
        "ratified_baseline": RATIFIED_RECIPROCITY_BASELINE,
        "ar006_estimate": AR006_RECIPROCITY_ESTIMATE,
        "nodes": data.get("nodes"),
        "edges": data.get("edges"),
    }


def run_pytest_file(target: str, timeout: int = 600) -> dict[str, Any]:
    """PASS iff the file's tests ran green (exit 0); exit 5 (none collected) is UNMEASURED."""
    path = REPO_ROOT / target
    if not path.is_file():
        return {"status": FAIL, "reason": f"{target} missing"}
    cmd = [sys.executable, "-m", "pytest", str(path), "-p", "no:cacheprovider", "-W", "ignore"]
    try:
        proc = subprocess.run(
            cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": UNMEASURED, "reason": f"pytest not runnable: {exc}"}
    if proc.returncode == 5:
        return {"status": UNMEASURED, "reason": f"{target}: no tests collected"}
    return {
        "status": PASS if proc.returncode == 0 else FAIL,
        "exit_code": proc.returncode,
        "output_tail": "" if proc.returncode == 0 else (proc.stdout + proc.stderr)[-600:],
    }


def _seed_ids(prefix: str, module_id: str, seed: Path) -> set[str]:
    if not seed.is_file():
        return set()
    _, rows = read_register(seed)
    pattern = re.compile(rf"^{re.escape(prefix)}-\d{{3}}$")
    return {
        r["requirement"].strip()
        for r in rows
        if pattern.match(r.get("requirement", "").strip()) and r.get("module", "") == module_id
    }


def measure_rtm(spec: dict[str, Any], root: Path = REPO_ROOT, pytest_fn=run_pytest_file) -> dict:
    """One module's traceability, measured from its CR register + RTM seed + disk."""
    module_id, prefix = spec["module_id"], spec["prefix"]
    cr_doc = root / "docs" / "r10" / f"CR-module-register-{module_id}.md"
    seed_ids = _seed_ids(
        prefix, module_id, root / "docs" / "p01-m03" / "registers" / "rtm-seed.csv"
    )
    failures: list[str] = []
    rows: list[tuple[str, list[str]]] = []
    if cr_doc.is_file():
        row_re = re.compile(rf"^\|\s*`({re.escape(prefix)}-\d{{3}})`")
        for line in cr_doc.read_text(encoding="utf-8").splitlines():
            m = row_re.match(line)
            if m:
                rows.append((m.group(1), [c.strip() for c in line.strip().strip("|").split("|")]))
    else:
        failures.append(f"CR register missing: {cr_doc.name}")
    cr_ids = [rid for rid, _ in rows]
    untraced: list[str] = []
    broken_refs: dict[str, list[str]] = {}
    for rid, cells in rows:
        unit = cells[3] if len(cells) > 3 else ""
        refs = sorted(
            {
                tok.strip().split(" ")[0].rstrip("/")
                for cell in cells[3:]
                for tok in re.findall(r"`([^`]+)`", cell)
                if REPO_PATH_TOKEN.match(tok.strip())
            }
        )
        missing_refs = [r for r in refs if not (root / r).exists()]
        if missing_refs:
            broken_refs[rid] = missing_refs
        if rid not in seed_ids or not unit or missing_refs:
            untraced.append(rid)
    not_in_cr = sorted(seed_ids - set(cr_ids))
    if not seed_ids:
        failures.append(f"no {prefix}-### rows for {module_id} in rtm-seed.csv")
    if not_in_cr:
        failures.append(f"{len(not_in_cr)} seeded requirement(s) absent from the CR register")
    if untraced:
        failures.append(f"{len(untraced)} CR row(s) untraced (not seeded / no unit / broken path)")
    units = []
    for path, token, label in spec["delivery_units"]:
        target = root / path
        present = target.exists()
        if present and token:
            present = target.is_file() and token in target.read_text(
                encoding="utf-8", errors="ignore"
            )
        units.append({"unit": label, "path": path, "requires": token, "present": present})
        if not present:
            failures.append(f"delivery unit absent: {path}" + (f" ({token})" if token else ""))
    statuses = [FAIL if failures else PASS]
    data: dict[str, Any] = {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R10-M02",
        "task": spec["task"],
        "title": spec["title"],
        "timestamp": datetime.now(UTC).isoformat(),
        "module_id": module_id,
        "cr_id": spec["cr_id"],
        "requirements_seeded": len(seed_ids),
        "requirements_in_cr_register": len(set(cr_ids)),
        "requirements_count": len(set(cr_ids)) - len(set(untraced)),
        "requirements_range": f"{min(cr_ids)} ... {max(cr_ids)}" if cr_ids else None,
        "untraced_requirements": untraced,
        "broken_path_references": broken_refs,
        "seeded_not_in_cr_register": not_in_cr,
        "delivery_units": units,
        "failures": failures,
    }
    if spec.get("break_test"):
        brk = pytest_fn(spec["break_test"])
        data["pair_10_break_verified"] = brk["status"] == PASS
        data["pair_10_break_test"] = brk
        statuses.append(brk["status"])
    data["verdict"] = data["status"] = derive_verdict(statuses)
    return data


def generate_rtm_evidence_files(pytest_fn=run_pytest_file) -> list[dict[str, Any]]:
    out = []
    for spec in RTM_MODULES:
        data = measure_rtm(spec, pytest_fn=pytest_fn)
        with open(EVIDENCE_DIR / spec["file"], "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        out.append(data)
    return out


def build_disposition(priorities: dict[str, Any], reciprocity: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "priority_classification": priorities,
        "reciprocity_baseline": reciprocity,
        "change_board_ratification": {
            "status": UNMEASURED,
            "reason": "the rulings are recorded by this tool; their Change Board / CTO "
            "ratification is a human approval and no signed minute is observable here",
        },
    }
    findings = [
        {"id": "F-P01M03-4", "class": "Requirements Baseline", "check": "priority_classification"},
        {"id": "F-P01M04-2", "class": "Architecture Reciprocity", "check": "reciprocity_baseline"},
    ]
    for f in findings:
        st = checks[f["check"]]["status"]
        f["state"] = {PASS: "CLOSED", FAIL: "OPEN"}.get(st, "UNVERIFIED")
    verdict = derive_verdict([c["status"] for c in checks.values()])
    return {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R10-M02",
        "task": "R10-M02-T06",
        "title": "Baseline Findings Disposition Evidence",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_requirements": priorities.get("total_requirements"),
        "undeclared_prior_to_run": priorities.get("undeclared_before_run"),
        "undeclared_post_run": priorities.get("undeclared_after_run"),
        "priority_distribution": priorities.get("priority_distribution"),
        "reciprocity_baseline_target": RATIFIED_RECIPROCITY_BASELINE,
        "reciprocity_ar006_estimate": AR006_RECIPROCITY_ESTIMATE,
        "reciprocity_measured": reciprocity.get("reciprocity_measured"),
        "reciprocity_verdict": "ACCEPT_AND_REBASELINE (ruling; ratification UNMEASURED)",
        "findings": findings,
        "open_findings_remaining": sum(1 for f in findings if f["state"] != "CLOSED"),
        "checks": checks,
        "verdict": verdict,
        "status": verdict,
    }


def render_register(ev: dict[str, Any]) -> str:
    pri = ev["checks"]["priority_classification"]
    rec = ev["checks"]["reciprocity_baseline"]
    rat = ev["checks"]["change_board_ratification"]
    date = ev["timestamp"][:10]
    total = pri.get("total_requirements") or 0
    dist = pri.get("priority_distribution") or {}

    def share(key: str) -> str:
        return f"{dist.get(key, 0)} ({dist.get(key, 0) / total * 100:.1f}%)" if total else "n/a"

    by_module = " ".join(f"{k}:{v}" for k, v in (rec.get("reciprocity_by_module") or {}).items())
    state = {f["id"]: f["state"] for f in ev["findings"]}
    lines = [
        "# Milestone R10-M02 — Formal Baseline Findings Disposition Register",
        "",
        "| Attribute | Value |",
        "|---|---|",
        "| **Document ID** | `R10-M02-DISPOSITION-REGISTER` |",
        f"| **Date** | {date} |",
        "| **Authority** | Change Board / Chief Technology Officer / Enterprise Architecture |",
        f"| **Computed Verdict** | **{ev['verdict']}** |",
        f"| **Open / Unverified Findings** | **{ev['open_findings_remaining']}** |",
        f"| **Ratification** | {rat['status']} — {rat['reason']} |",
        "",
        "Every figure below was measured by `tooling/scripts/disposition_p01m03_findings.py` "
        "in this run (GV-009).",
        "",
        "---",
        "",
        "## 1. Ruling 1: Finding `F-P01M03-4` (Priority Classification)",
        "",
        "The Phase 1 baseline (`docs/traceability/PHASE1-AUDIT-iteration3.md`) recorded requirement "
        "rows carrying no priority. **Ruling: FIX & RE-BASELINE** — every undeclared row is "
        "classified into the P0/P1/P2 scheme (`SU-13` MoSCoW-equivalent).",
        "",
        f"- Register: `{pri.get('register', 'fit-gap-register.csv')}` — mode: {pri.get('mode', 'n/a')}",
        f"- Rows measured: **{total}**; undeclared before this run: "
        f"**{pri.get('undeclared_before_run', 'n/a')}**; classified this run: "
        f"**{pri.get('classified_this_run', 'n/a')}**; undeclared after: "
        f"**{pri.get('undeclared_after_run', 'n/a')}**",
        f"- Rows carrying the R10-M02 disposition marker: "
        f"**{pri.get('rows_carrying_r10_m02_disposition_marker', 'n/a')}**",
        f"- Distribution: P0 {share('P0')} · P1 {share('P1')} · P2 {share('P2')}",
        f"- Check: **{pri['status']}** → finding **{state['F-P01M03-4']}**"
        + (f" ({pri['reason']})" if pri.get("reason") else ""),
        "",
        "---",
        "",
        "## 2. Ruling 2: Finding `F-P01M04-2` (Reciprocity Drift)",
        "",
        f"`AR-006` §4 estimated {AR006_RECIPROCITY_ESTIMATE} reciprocity anomalies. "
        f"**Ruling: ACCEPT & RE-BASELINE** at {RATIFIED_RECIPROCITY_BASELINE}; the FF-14 extractor "
        "(`tooling/architecture-baseline/extract-dependency-graph.ps1`) was re-run now and any "
        "drift from the ratified baseline re-opens the finding.",
        "",
        f"- Measured reciprocity anomalies: **{rec.get('reciprocity_measured', 'n/a')}**"
        + (f" ({by_module})" if by_module else ""),
        f"- Check: **{rec['status']}** → finding **{state['F-P01M04-2']}**"
        + (f" ({rec['reason']})" if rec.get("reason") else ""),
        "",
        "---",
        "",
        "## 3. Summary",
        "",
        "| Finding | Class | Ruling | Measured Check | Finding State |",
        "|---|---|---|:---:|:---:|",
        f"| `F-P01M03-4` | Requirements Baseline | Fix & re-baseline | **{pri['status']}** | "
        f"**{state['F-P01M03-4']}** |",
        f"| `F-P01M04-2` | Architecture Reciprocity | Accept & re-baseline | **{rec['status']}** | "
        f"**{state['F-P01M04-2']}** |",
        f"| — | Change Board ratification | — | **{rat['status']}** | — |",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a cp1252 console must not crash the run
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="measure only: never rewrite fit-gap-register.csv (evidence + register md still written)",
    )
    args = parser.parse_args(argv)

    priorities = measure_priorities(apply=not args.dry_run)
    reciprocity = measure_reciprocity()
    evidence = build_disposition(priorities, reciprocity)
    DISPOSITION_MD.write_text(render_register(evidence), encoding="utf-8")
    DISPOSITION_EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    with open(DISPOSITION_EVIDENCE, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    rtms = generate_rtm_evidence_files()

    print("=" * 80)
    print(f"Baseline Findings Disposition: {evidence['verdict']}")
    print(f"Total Requirements Processed: {evidence['total_requirements']}")
    print(
        f"Undeclared Priority (before/after): {evidence['undeclared_prior_to_run']}/{evidence['undeclared_post_run']}"
    )
    print(f"Priority Distribution: {evidence['priority_distribution']}")
    print(
        f"Reciprocity: measured {evidence['reciprocity_measured']} vs ratified baseline "
        f"{RATIFIED_RECIPROCITY_BASELINE} -> {reciprocity['status']}"
        + (f" ({reciprocity['reason']})" if reciprocity.get("reason") else "")
    )
    print(f"Open/Unverified Findings: {evidence['open_findings_remaining']}")
    for rtm in rtms:
        print(
            f"RTM {rtm['module_id']}: {rtm['verdict']} ({rtm['requirements_count']}/"
            f"{rtm['requirements_in_cr_register']} traced)"
            + (f" - {'; '.join(rtm['failures'])}" if rtm["failures"] else "")
        )
    print(f"Disposition Register: {DISPOSITION_MD}")
    print(f"Evidence file: {DISPOSITION_EVIDENCE}")
    overall = derive_verdict([evidence["verdict"]] + [r["verdict"] for r in rtms])
    print(f"Overall (disposition + RTM files): {overall}")
    print("=" * 80)
    return exit_code_for(overall)


if __name__ == "__main__":
    sys.exit(main())
