#!/usr/bin/env python3
"""
verify_legacy_reference_lookup.py — Legacy Reference Survival & Lookup Verification (measured)
Milestone: R11-M02-T02 (Legacy decommissioning)
Standards: MIG-03, TSS §19.2, FR-SRM-088

FR-SRM-088: "Every migrated record carries its legacy reference, permanently —
legacy order lookup is a live post-cutover requirement, not a migration convenience."

GV-009 — what is measured, and what cannot be:
- For every domain with a committed rehearsal extract and a load report
  (migrations/extracts + loaded-counts.json), EVERY legacy reference the load report
  says was accepted (extract references minus the quarantined ones) is looked up on the
  rehearsal database (migrations/target_db.py: fix_migration, never fix_dev) with a
  read-only, parameterised `SELECT id ... WHERE legacy_reference = %s`. Each lookup is
  timed (perf_counter around execute + fetch); it resolves only when exactly one row
  carries the reference. The table must also carry an index on legacy_reference
  (pg_indexes) - the property a production-volume lookup depends on.
- A domain with no committed extract (fix.service.order) has nothing to look up:
  UNMEASURED. An unreachable database makes every lookup UNMEASURED.
- Lookup after legacy retirement on the PRODUCTION database (and its latency at
  production volume) cannot be observed from this workstation (DE-11 / DE-12):
  UNMEASURED. Rehearsal latencies are reported with the table sizes they were taken at.

Verdict: FAIL if any check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE. Read-only: writes only the evidence JSON and its
Markdown record.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
EXTRACTS_DIR = REPO_ROOT / "migrations" / "extracts"
TARGET_DB_MODULE = REPO_ROOT / "migrations" / "target_db.py"
LOADED_NAME = "loaded-counts.json"
EVIDENCE_NAME = "r11-m02-legacy-reference-verification.json"
MD_NAME = "r11-m02-legacy-lookup-proof.md"

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
INCOMPLETE = "INCOMPLETE"
TARGET_SLA_MS = 50.0

# domain model -> target table (legacy_reference column), committed extract, load-report
# entity. Fixed constants - never user input.
LOOKUP_DOMAINS: list[dict[str, str | None]] = [
    {"domain": "fix.service.order", "table": "fix_service_order", "extract": None, "entity": None},
    {
        "domain": "fix.device",
        "table": "fix_device",
        "extract": "devices_extract.json",
        "entity": "devices",
    },
    {
        "domain": "res.partner",
        "table": "res_partner",
        "extract": "customers_extract.json",
        "entity": "customers",
    },
    {
        "domain": "hr.employee",
        "table": "hr_employee",
        "extract": "employees_extract.json",
        "entity": "employees",
    },
    {
        "domain": "fix.branch",
        "table": "fix_branch",
        "extract": "branches_extract.json",
        "entity": "branches",
    },
]

PRODUCTION_REASON = (
    "lookup after legacy retirement on the production database, at production volume, "
    "cannot be observed from this workstation (DE-11 local-only endpoints; DE-12 no "
    "production data on a workstation)"
)


def derive_verdict(statuses: list[str]) -> str:
    """FAIL if any check failed, INCOMPLETE if any is not PASS, else PASS."""
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return INCOMPLETE
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _check(status: str, detail: str) -> dict[str, str]:
    return {"status": status, "detail": detail}


def _read_json(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, f"{path.name} not found"
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"


def open_rehearsal_db(dsn: str | None = None):
    """Read-only connection to the rehearsal target -> (conn, 'host:port/db').

    Resolution and the DE-12 refusals (never fix_dev) are migrations/target_db.py's; the
    session is set read-only, so no statement of this tool can write.
    """
    os.environ.setdefault("PGCONNECT_TIMEOUT", "5")
    spec = importlib.util.spec_from_file_location("r11_m02_t02_target_db", TARGET_DB_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    conn = module.connect(dsn)
    conn.set_session(readonly=True, autocommit=True)
    return conn, module.describe(module.resolve_dsn(dsn))


def expected_refs(records: list, rejections: list) -> list[str]:
    """Legacy references the load report says were accepted.

    Counted per occurrence: a quarantined duplicate (e.g. a repeated serial) removes one
    occurrence, so the first, accepted record's reference is still expected on the target.
    """
    counts = Counter(
        str(r["legacy_reference"])
        for r in records
        if isinstance(r, dict) and r.get("legacy_reference")
    )
    for rej in rejections:
        ref = rej.get("legacy_reference") if isinstance(rej, dict) else None
        if ref in counts:
            counts[ref] -= 1
    return sorted(ref for ref, n in counts.items() if n > 0)


def lookup(conn, table: str, ref: str) -> tuple[list[Any], float]:
    """Timed read-only lookup by legacy reference -> (row ids, milliseconds)."""
    with conn.cursor() as cur:
        started = time.perf_counter()
        cur.execute(f"SELECT id FROM {table} WHERE legacy_reference = %s", (ref,))
        rows = cur.fetchall()
        elapsed_ms = (time.perf_counter() - started) * 1000.0
    return [row[0] for row in rows], round(elapsed_ms, 3)


def table_facts(conn, table: str) -> tuple[int, bool]:
    """(rows carrying a legacy reference, legacy_reference index present)."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table} WHERE legacy_reference IS NOT NULL")
        rows = int(cur.fetchone()[0])
        cur.execute(
            "SELECT count(*) FROM pg_indexes WHERE schemaname = current_schema() "
            "AND tablename = %s AND indexdef ILIKE %s",
            (table, "%(legacy_reference)%"),
        )
        indexed = int(cur.fetchone()[0]) > 0
    return rows, indexed


def _percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(pct / 100.0 * len(ordered)) - 1)]


def measure_domain(
    spec: dict[str, str | None],
    conn,
    db_reason: str,
    loaded: dict | None,
    loaded_reason: str,
    extracts_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    domain, table = spec["domain"], str(spec["table"])
    result: dict[str, Any] = {
        "domain_model": domain,
        "target_table": table,
        "origin_extract": spec["extract"],
    }
    checks: dict[str, dict[str, str]] = {}
    lookups: list[dict[str, Any]] = []

    facts_error = None
    if conn is not None:
        try:
            rows, indexed = table_facts(conn, table)
        except Exception as exc:  # a failed query is a failed check, not an aborted run
            facts_error = f"table query failed: {exc}"
            result["target_rows_with_legacy_reference"] = None
            checks["legacy_reference_indexed"] = _check(FAIL, facts_error)
        else:
            result["target_rows_with_legacy_reference"] = rows
            checks["legacy_reference_indexed"] = _check(
                PASS if indexed else FAIL,
                f"{table}: index on legacy_reference {'present' if indexed else 'MISSING'}",
            )
    else:
        result["target_rows_with_legacy_reference"] = None
        checks["legacy_reference_indexed"] = _check(UNMEASURED, db_reason)

    refs: list[str] | None = None
    if not spec["extract"]:
        checks["coverage"] = _check(
            UNMEASURED,
            "no committed extract carries legacy references for this domain, so no migrated "
            "record can be looked up",
        )
    else:
        payload, err = _read_json(extracts_dir / str(spec["extract"]))
        if err or not isinstance(payload, list):
            checks["coverage"] = _check(FAIL, err or f"{spec['extract']} holds no record list")
        elif loaded is None:
            checks["coverage"] = _check(UNMEASURED, loaded_reason)
        else:
            rejections = (loaded.get("rejections") or {}).get(spec["entity"]) or []
            refs = expected_refs(payload, rejections)
            if not refs:
                checks["coverage"] = _check(FAIL, "the load report accepted no record to look up")
                refs = None

    if refs is not None and conn is None:
        checks["coverage"] = _check(UNMEASURED, db_reason)
        checks["latency_sla"] = _check(UNMEASURED, db_reason)
    elif refs is not None:
        for ref in refs:
            try:
                ids, ms = lookup(conn, table, ref)
            except Exception as exc:
                lookups.append(
                    {
                        "domain_model": domain,
                        "legacy_reference_queried": ref,
                        "target_record_ids": [],
                        "lookup_duration_ms": None,
                        "status": "LOOKUP_ERROR",
                        "error": str(exc),
                    }
                )
                continue
            status = {0: "LOOKUP_NOT_FOUND", 1: "LOOKUP_SUCCESS"}.get(len(ids), "LOOKUP_AMBIGUOUS")
            lookups.append(
                {
                    "domain_model": domain,
                    "legacy_reference_queried": ref,
                    "target_record_ids": ids,
                    "lookup_duration_ms": ms,
                    "status": status,
                }
            )
        resolved = sum(1 for lk in lookups if lk["status"] == "LOOKUP_SUCCESS")
        bad = [
            f"{lk['legacy_reference_queried']} ({lk['status']})"
            for lk in lookups
            if lk["status"] != "LOOKUP_SUCCESS"
        ]
        checks["coverage"] = _check(
            PASS if resolved == len(refs) else FAIL,
            f"{resolved} of {len(refs)} accepted legacy references resolve to exactly one row"
            + (f"; unresolved: {', '.join(bad[:10])}" if bad else ""),
        )
        timings = [
            lk["lookup_duration_ms"] for lk in lookups if lk["lookup_duration_ms"] is not None
        ]
        worst = max(timings) if timings else None
        checks["latency_sla"] = (
            _check(FAIL, "no lookup completed")
            if worst is None
            else _check(
                PASS if worst < TARGET_SLA_MS else FAIL,
                f"max {worst} ms over {len(timings)} lookups (target < {TARGET_SLA_MS} ms)",
            )
        )
        result.update(
            lookups_tested=len(lookups),
            lookups_resolved=resolved,
            average_lookup_latency_ms=round(sum(timings) / len(timings), 3) if timings else None,
            p95_lookup_latency_ms=_percentile(timings, 95),
            max_lookup_latency_ms=worst,
        )
    result.setdefault("lookups_tested", len(lookups))
    result.setdefault("lookups_resolved", 0)
    result["checks"] = checks
    result["status"] = derive_verdict([c["status"] for c in checks.values()])
    return result, lookups


def build_evidence(
    extracts_dir: Path | None = None,
    connector: Callable[[], tuple] | None = None,
) -> dict[str, Any]:
    extracts_dir = extracts_dir or EXTRACTS_DIR
    connector = connector or open_rehearsal_db
    loaded, lerr = _read_json(extracts_dir / LOADED_NAME)
    loaded_reason = ""
    if lerr or not isinstance(loaded, dict):
        loaded_reason = f"no usable load report ({lerr or 'not an object'}): which records were accepted is not known"
        loaded = None

    conn, target, db_reason = None, None, ""
    try:
        conn, target = connector()
    except Exception as exc:  # unreachable infrastructure is UNMEASURED, never PASS
        db_reason = f"rehearsal database unreachable: {exc}".strip()

    domains: list[dict[str, Any]] = []
    lookups: list[dict[str, Any]] = []
    try:
        for spec in LOOKUP_DOMAINS:
            result, found = measure_domain(
                spec, conn, db_reason, loaded, loaded_reason, extracts_dir
            )
            domains.append(result)
            lookups.extend(found)
    finally:
        if conn is not None:
            conn.close()

    production = _check(UNMEASURED, PRODUCTION_REASON)
    statuses = [c["status"] for d in domains for c in d["checks"].values()]
    statuses.append(production["status"])
    verdict = derive_verdict(statuses)

    timings = [lk["lookup_duration_ms"] for lk in lookups if lk["lookup_duration_ms"] is not None]
    resolved = sum(1 for lk in lookups if lk["status"] == "LOOKUP_SUCCESS")
    sla_statuses = [
        d["checks"]["latency_sla"]["status"] for d in domains if "latency_sla" in d["checks"]
    ]
    return {
        "milestone": "R11-M02",
        "task": "R11-M02-T02",
        "title": "Legacy Reference Survival & Real-Time Lookup Verification (FR-SRM-088 / MIG-03)",
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "governing_standards": ["TSS §19.2", "MIG-03", "FR-SRM-088"],
        "measurement_policy": "GV-009: every lookup below was executed and timed in this run; "
        "what cannot be observed from this workstation is UNMEASURED with its reason",
        "target_database": target,
        "scope": "rehearsal database (synthetic Wave-1 load); production is UNMEASURED",
        "total_sample_lookups_tested": len(lookups),
        "total_successful_resolutions": resolved,
        "resolution_success_rate": f"{resolved / len(lookups) * 100:.1f}%" if lookups else None,
        "performance_metrics": {
            "target_sla_latency_ms": TARGET_SLA_MS,
            "average_lookup_latency_ms": round(sum(timings) / len(timings), 3) if timings else None,
            "p95_lookup_latency_ms": _percentile(timings, 95),
            "max_lookup_latency_ms": max(timings) if timings else None,
            "sla_conformance": derive_verdict(sla_statuses) if sla_statuses else UNMEASURED,
        },
        "verified_domains": [d["domain_model"] for d in domains if d["status"] == PASS],
        "unverified_domains": [d["domain_model"] for d in domains if d["status"] != PASS],
        "production_lookup_after_retirement": production,
        "domains": domains,
        "verdict": verdict,
        "overall_status": verdict,
        "sample_verifications": lookups,
    }


def _md(value: Any) -> str:
    return "n/a" if value is None else str(value).replace("|", "/")


def render_markdown(ev: dict[str, Any]) -> str:
    perf = ev["performance_metrics"]
    out = [
        "# Legacy Reference Survival & Live Lookup Proof (FR-SRM-088 / MIG-03)",
        "",
        "## Task R11-M02-T02 Verification Record",
        "",
        "- **Standard**: `MIG-03` (*Permanent legacy reference on every migrated record*) & "
        "`FR-SRM-088` (*Live legacy lookup*)",
        f"- **Executed**: {ev['timestamp']} against {_md(ev['target_database'])}",
        f"- **Verdict (computed)**: `{ev['verdict']}`",
        f"- **Resolution**: {ev['total_successful_resolutions']} / "
        f"{ev['total_sample_lookups_tested']} lookups resolved "
        f"({_md(ev['resolution_success_rate'])})",
        f"- **Lookup latency (measured)**: avg {_md(perf['average_lookup_latency_ms'])} ms, "
        f"p95 {_md(perf['p95_lookup_latency_ms'])} ms, max {_md(perf['max_lookup_latency_ms'])} ms "
        f"(target < {perf['target_sla_latency_ms']} ms) — `{perf['sla_conformance']}`",
        f"- **Production lookup after retirement**: "
        f"`{ev['production_lookup_after_retirement']['status']}` — "
        f"{ev['production_lookup_after_retirement']['detail']}",
        "",
        "---",
        "",
        "### Domains",
        "",
        "| Domain Model | Table | Rows with legacy ref | Lookups | Resolved | Max ms | Status |",
        "|---|---|---:|---:|---:|---:|:---:|",
    ]
    for d in ev["domains"]:
        out.append(
            f"| `{d['domain_model']}` | `{d['target_table']}` "
            f"| {_md(d.get('target_rows_with_legacy_reference'))} | {d['lookups_tested']} "
            f"| {d['lookups_resolved']} | {_md(d.get('max_lookup_latency_ms'))} | `{d['status']}` |"
        )
    problems = [
        f"- `{d['domain_model']}.{name}` — {c['status']}: {c['detail']}"
        for d in ev["domains"]
        for name, c in d["checks"].items()
        if c["status"] != PASS
    ]
    if problems:
        out += ["", "Checks not passed:", "", *problems]
    out.append("")
    if ev["verdict"] == PASS:
        out += ["Every legacy-reference check above was measured as passed.", ""]
    else:
        out += [
            f"Legacy-reference survival is not established by this record (verdict "
            f"`{ev['verdict']}`).",
            "",
        ]
    return "\n".join(out)


def write_outputs(ev: dict[str, Any]) -> tuple[Path, Path]:
    evidence_dir, docs_dir = Path(EVIDENCE_DIR), Path(DOCS_DIR)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / EVIDENCE_NAME
    md_path = docs_dir / MD_NAME
    json_path.write_bytes((json.dumps(ev, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    md_path.write_bytes(render_markdown(ev).encode("utf-8"))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="R11-M02-T02 legacy-reference lookup (measured)")
    ap.add_argument("--dsn", help="rehearsal database DSN (default: migrations/target_db.py)")
    ap.add_argument("--extracts-dir", type=Path, default=None, help="rehearsal extracts dir")
    args = ap.parse_args(argv)
    ev = build_evidence(args.extracts_dir, lambda: open_rehearsal_db(args.dsn))
    json_path, md_path = write_outputs(ev)
    perf = ev["performance_metrics"]
    print(
        f"R11-M02-T02: {ev['total_successful_resolutions']}/{ev['total_sample_lookups_tested']} "
        f"lookups resolved, avg {perf['average_lookup_latency_ms']} ms, "
        f"max {perf['max_lookup_latency_ms']} ms"
    )
    print(f"Verdict: {ev['verdict']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return exit_code_for(ev["verdict"])


if __name__ == "__main__":
    sys.exit(main())
