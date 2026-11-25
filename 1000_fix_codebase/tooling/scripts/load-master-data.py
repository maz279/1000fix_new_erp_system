#!/usr/bin/env python3
"""
load-master-data.py - Milestone R02-M04 Task T05:
Parse, validate, load and formally baseline the 48 MD-* Master Data content sets
across the 10 load tiers defined in MD-048, resolving Blocker B-14 and generating
the Master Data Approval Register (docs/traceability/master-data-approval-register.md).

GV-009: approval is never asserted by this script. A dataset counts as approved only
when its own frontmatter `status` is an approved state (APPROVED_FRONTMATTER_STATES);
B-14 is RESOLVED only when every check below is PASS in this run:

  inventory              every dataset in TIER_MAP has an MD-* file, none unassigned
  frontmatter_integrity  frontmatter parses and its id matches the file name
  seed_rows_present      every dataset has >= 1 section-9 CSV row
  approval               every dataset's frontmatter status is an approved state
  database_load          rows upserted into fix_master_data_register/_payload
                         (UNMEASURED with --dry-run: no database connection is made)

Modes:
  (default)   load into PostgreSQL (PGDATABASE, default fix_migration) and write
              migrations/extracts/master-data-loaded.json + the register.
  --dry-run   parse and evaluate only - NO database connection, nothing written under
              migrations/; writes docs/traceability/evidence/master-data-baseline-latest.json
              and the register.
Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5433"))
# Default target: the dedicated Wave-1 rehearsal database (never fix_dev, DE-12);
# PGDATABASE overrides. Build it: python tooling/scripts/build-test-db.py --db fix_migration
DB_NAME = os.environ.get("PGDATABASE", "fix_migration")
DB_USER = os.environ.get("PGUSER", "fix")
DB_PASS = os.environ.get("PGPASSWORD", "change-me-dev-only")


def find_dirs():
    current = Path(__file__).resolve().parent
    for p in [current, *current.parents]:
        if p.name == "1000_fix_codebase":
            return p, p.parent
    return Path.cwd(), Path.cwd().parent


CODEBASE_DIR, PROJECT_DIR = find_dirs()
MD_ROOT = PROJECT_DIR / "project_content" / "02_Master_Data_and_Configuration"
OUTPUT_REGISTER = CODEBASE_DIR / "docs" / "traceability" / "master-data-approval-register.md"
OUTPUT_JSON = CODEBASE_DIR / "migrations" / "extracts" / "master-data-loaded.json"
DRY_RUN_EVIDENCE = (
    CODEBASE_DIR / "docs" / "traceability" / "evidence" / "master-data-baseline-latest.json"
)

# Frontmatter `status` values that mean the dataset has been approved/baselined.
APPROVED_FRONTMATTER_STATES = {"approved", "baselined"}
EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}

TIER_MAP = {
    0: ["MD-001", "MD-006", "MD-023", "MD-039"],
    1: ["MD-002", "MD-035", "MD-036", "MD-041"],
    2: ["MD-003", "MD-005", "MD-007", "MD-004"],
    3: ["MD-009", "MD-008", "MD-012", "MD-042"],
    4: ["MD-037", "MD-038", "MD-040", "MD-044"],
    5: ["MD-021", "MD-019", "MD-022", "MD-024", "MD-025", "MD-026", "MD-027", "MD-020"],
    6: ["MD-014", "MD-028", "MD-029", "MD-030", "MD-031", "MD-032"],
    7: ["MD-013", "MD-015", "MD-016", "MD-017"],
    8: ["MD-010", "MD-011", "MD-045", "MD-046", "MD-047"],
    9: ["MD-018", "MD-033", "MD-034", "MD-043", "MD-048"],
}

TIER_NAMES = {
    0: "0 — Foundation",
    1: "1 — Entity and chart",
    2: "2 — Network",
    3: "3 — Workforce structure",
    4: "4 — Tax and finance config",
    5: "5 — Catalogue",
    6: "6 — Commercial",
    7: "7 — Party and ecosystem",
    8: "8 — Competency and asset",
    9: "9 — Deferred",
}

TIER_RATIONALE = {
    0: "No foreign key dependencies",
    1: "Legal entities before financial accounts",
    2: "Branches before zones and storage locations",
    3: "Roles before positions before employees",
    4: "CoA before Mushak tax codes and numbering sequences",
    5: "Device categories before items and spare parts",
    6: "Customer segments before SLAs and price lists",
    7: "Customers and vendors after commercial terms",
    8: "Skills, authorisations, and test equipment",
    9: "Marketplace, subscriptions, loyalty, and workbook index",
}


def expected_dataset_ids() -> list[str]:
    return [did for tier in sorted(TIER_MAP) for did in TIER_MAP[tier]]


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def get_db():
    import psycopg2

    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def ensure_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fix_master_data_register (
            id SERIAL PRIMARY KEY,
            dataset_id VARCHAR(32) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            domain VARCHAR(100) NOT NULL,
            owning_module VARCHAR(64),
            tier INTEGER NOT NULL,
            wave VARCHAR(16) NOT NULL,
            owner VARCHAR(100),
            approver VARCHAR(100),
            content_class VARCHAR(16),
            priority VARCHAR(16),
            status VARCHAR(64) NOT NULL,
            approval_status VARCHAR(64) NOT NULL,
            row_count INTEGER DEFAULT 0,
            sha256_hash VARCHAR(64) NOT NULL,
            loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            sample_columns JSONB,
            metadata JSONB
        );
        CREATE INDEX IF NOT EXISTS idx_fmdr_tier ON fix_master_data_register(tier);
        CREATE INDEX IF NOT EXISTS idx_fmdr_dataset ON fix_master_data_register(dataset_id);

        CREATE TABLE IF NOT EXISTS fix_master_data_payload (
            id SERIAL PRIMARY KEY,
            dataset_id VARCHAR(32) NOT NULL REFERENCES fix_master_data_register(dataset_id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            payload JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT uq_fmd_payload UNIQUE (dataset_id, row_index)
        );
        CREATE INDEX IF NOT EXISTS idx_fmdp_dataset ON fix_master_data_payload(dataset_id);
    """)


def approval_status_text(fm_status: str, approved: bool) -> str:
    """Approval as read from the dataset's own frontmatter (fits VARCHAR(64))."""
    label = "APPROVED" if approved else "NOT APPROVED"
    return f"{label} (frontmatter status: {fm_status})"[:64]


def parse_md_file(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # Frontmatter
    fm = {}
    frontmatter_problems = []
    fm_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except Exception as e:
            print(f"Warning: Failed to parse YAML frontmatter in {file_path.name}: {e}")
            frontmatter_problems.append(f"frontmatter YAML unparseable: {e}")
        if not isinstance(fm, dict):
            frontmatter_problems.append("frontmatter is not a mapping")
            fm = {}
    else:
        frontmatter_problems.append("no frontmatter block")

    file_id = file_path.stem.split("_")[0]
    dataset_id = fm.get("id", file_id)
    if dataset_id != file_id:
        frontmatter_problems.append(f"frontmatter id {dataset_id!r} != file name id {file_id!r}")
    title = fm.get("title", file_path.stem)
    owner = fm.get("owner", "MDM Lead")
    approver = fm.get("approver", "MDM Lead")
    content_class = fm.get("content_class", "C")
    priority = fm.get("priority", "P0")
    wave = fm.get("wave", "W1")

    # Approval is read from the dataset's own frontmatter - never asserted here.
    fm_status = str(fm.get("status") or "").strip() or "UNKNOWN"
    approved = fm_status.lower() in APPROVED_FRONTMATTER_STATES

    # Owning module from traces_to or text
    owning_module = None
    traces = fm.get("traces_to", [])
    if isinstance(traces, list):
        for t in traces:
            if isinstance(t, str) and re.match(r"^M\d+", t):
                owning_module = t
                break

    # Purpose
    purpose = fm.get("purpose", "")

    # Domain from parent directory
    domain_dir = file_path.parent.name
    domain_map = {
        "02A_Organisation_and_Network": "Organisation & Network",
        "02B_Party_and_Ecosystem": "Party & Ecosystem",
        "02C_Catalogue_and_Technical": "Catalogue & Technical",
        "02D_Commercial_and_Pricing": "Commercial & Pricing",
        "02E_Finance_and_Statutory": "Finance & Statutory",
        "02F_Workforce_and_Asset": "Workforce & Asset",
    }
    domain = domain_map.get(domain_dir, "General Master Data")

    # Row data CSV: section 9 of every MD-* file, whatever its title ("Sample rows",
    # or e.g. MD-017 "Verified brand partner rows (18 counterparties)")
    csv_rows = []
    headers = []
    ragged_rows = 0
    sample_match = re.search(r"## 9\.[^\n]*\n\s*```(?:csv)?\s*\n(.*?)\n```", text, re.DOTALL)
    if sample_match:
        csv_text = sample_match.group(1).strip()
        reader = csv.reader(io.StringIO(csv_text))
        all_lines = list(reader)
        if len(all_lines) >= 1:
            headers = [h.strip() for h in all_lines[0]]
            for row in all_lines[1:]:
                if row and any(field.strip() for field in row):
                    if len(row) != len(headers):
                        ragged_rows += 1
                    # Pad or trim row to match headers
                    padded_row = (row + [""] * len(headers))[: len(headers)]
                    row_dict = {headers[i]: padded_row[i].strip() for i in range(len(headers))}
                    csv_rows.append(row_dict)

    return {
        "dataset_id": dataset_id,
        "title": title,
        "domain": domain,
        "owning_module": owning_module,
        "owner": owner,
        "approver": approver,
        "content_class": content_class,
        "priority": priority,
        "wave": wave,
        "status": fm_status[:64],
        "approved": approved,
        "approval_status": approval_status_text(fm_status, approved),
        "frontmatter_problems": frontmatter_problems,
        "ragged_rows": ragged_rows,
        "sha256": sha256,
        "headers": headers,
        "sample_rows": csv_rows,
        "row_count": len(csv_rows),
        "metadata": {
            "source_file": str(file_path.relative_to(PROJECT_DIR)),
            "purpose": purpose[:200] if purpose else "",
            "traces_to": traces,
        },
    }


def parse_all(verbose: bool = True) -> dict[str, dict]:
    """Parse every MD-* specification under MD_ROOT, keyed by dataset id."""
    if not MD_ROOT.exists():
        raise FileNotFoundError(f"Master data root path not found: {MD_ROOT}")
    md_files = sorted(MD_ROOT.rglob("MD-*.md"))
    if verbose:
        print(f"[*] Discovered {len(md_files)} Master Data specifications under {MD_ROOT.name}/")
    parsed_data = {}
    for mf in md_files:
        info = parse_md_file(mf)
        parsed_data[info["dataset_id"]] = info
    return parsed_data


def summary_row(tier: int, item: dict) -> dict:
    return {
        "tier": tier,
        "tier_name": TIER_NAMES.get(tier, f"Tier {tier}"),
        "dataset_id": item["dataset_id"],
        "title": item["title"],
        "domain": item["domain"],
        "module": item["owning_module"] or "M64",
        "wave": item["wave"],
        "rows": item["row_count"],
        "sha256": item["sha256"],
        "approver": item["approver"],
        "frontmatter_status": item["status"],
        "approved": item["approved"],
        "approval_status": item["approval_status"],
    }


def tiered_summary(parsed_data: dict[str, dict]) -> list[dict]:
    """The datasets in MD-048 tier order (no database involved)."""
    return [
        summary_row(tier, parsed_data[did])
        for tier in range(10)
        for did in TIER_MAP.get(tier, [])
        if did in parsed_data
    ]


def load_master_data(conn, verbose: bool = True) -> tuple[list[dict], int]:
    """Parse the MD-* sets and upsert them, tier by tier, into the register tables.

    Commits on `conn`. Used by main() and by the Wave-1 rehearsal pipeline
    (migrations/pipeline.py), which passes its own fix_migration connection.
    """
    from psycopg2.extras import Json

    def log(*args) -> None:
        if verbose:
            print(*args)

    parsed_data = parse_all(verbose=verbose)

    cur = conn.cursor()

    ensure_tables(cur)

    loaded_summary = []
    total_sample_rows = 0

    log(f"\n--- Executing Tiered Master Data Load into PostgreSQL ({conn.info.dbname}) ---")
    for tier in range(10):
        dataset_ids = TIER_MAP.get(tier, [])
        tier_label = TIER_NAMES.get(tier, f"Tier {tier}")
        log(f"\n[Tier {tier}] {tier_label} ({len(dataset_ids)} datasets)")

        for did in dataset_ids:
            item = parsed_data.get(did)
            if not item:
                print(f"  [WARN] Dataset {did} listed in Tier {tier} but markdown file not found!")
                continue

            # Upsert into fix_master_data_register
            cur.execute(
                """
                INSERT INTO fix_master_data_register (
                    dataset_id, title, domain, owning_module, tier, wave, owner, approver,
                    content_class, priority, status, approval_status, row_count, sha256_hash,
                    loaded_at, sample_columns, metadata
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    NOW(), %s, %s
                )
                ON CONFLICT (dataset_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    domain = EXCLUDED.domain,
                    owning_module = EXCLUDED.owning_module,
                    tier = EXCLUDED.tier,
                    wave = EXCLUDED.wave,
                    owner = EXCLUDED.owner,
                    approver = EXCLUDED.approver,
                    content_class = EXCLUDED.content_class,
                    priority = EXCLUDED.priority,
                    status = EXCLUDED.status,
                    approval_status = EXCLUDED.approval_status,
                    row_count = EXCLUDED.row_count,
                    sha256_hash = EXCLUDED.sha256_hash,
                    loaded_at = NOW(),
                    sample_columns = EXCLUDED.sample_columns,
                    metadata = EXCLUDED.metadata;
            """,
                (
                    item["dataset_id"],
                    item["title"],
                    item["domain"],
                    item["owning_module"],
                    tier,
                    item["wave"],
                    item["owner"],
                    item["approver"],
                    item["content_class"],
                    item["priority"],
                    item["status"],
                    item["approval_status"],
                    item["row_count"],
                    item["sha256"],
                    Json(item["headers"]),
                    Json(item["metadata"]),
                ),
            )

            # Delete old payload rows and insert sample rows
            cur.execute(
                "DELETE FROM fix_master_data_payload WHERE dataset_id = %s", (item["dataset_id"],)
            )
            for idx, row in enumerate(item["sample_rows"]):
                cur.execute(
                    """
                    INSERT INTO fix_master_data_payload (dataset_id, row_index, payload)
                    VALUES (%s, %s, %s)
                """,
                    (item["dataset_id"], idx + 1, Json(row)),
                )

            total_sample_rows += item["row_count"]
            loaded_summary.append(summary_row(tier, item))
            log(
                f"  + {item['dataset_id']:<8} {item['title'][:40]:<40} | Module: {item['owning_module'] or 'M64':<5} | Rows: {item['row_count']:<3} | {item['approval_status']}"
            )

    conn.commit()
    cur.close()
    return loaded_summary, total_sample_rows


def evaluate_baseline(parsed_data: dict[str, dict], db_load: dict) -> dict:
    """Derive every check, the overall verdict and the B-14 status from observations.

    db_load: {"status": PASS|FAIL|UNMEASURED, "detail": str, "loaded_datasets": int|None}
    """
    expected = expected_dataset_ids()
    checks = []

    missing = [did for did in expected if did not in parsed_data]
    unassigned = sorted(did for did in parsed_data if did not in expected)
    problems = []
    if missing:
        problems.append(f"no MD-* file for {missing}")
    if unassigned:
        problems.append(f"MD-* files not assigned to a load tier: {unassigned}")
    checks.append(
        {
            "check": "inventory",
            "status": "FAIL" if problems else "PASS",
            "detail": "; ".join(problems)
            or f"{len(expected)}/{len(expected)} tiered datasets have a specification file",
        }
    )

    fm_bad = {
        did: item["frontmatter_problems"]
        for did, item in parsed_data.items()
        if item["frontmatter_problems"]
    }
    checks.append(
        {
            "check": "frontmatter_integrity",
            "status": "FAIL" if fm_bad else "PASS",
            "detail": f"problems: {fm_bad}"
            if fm_bad
            else f"{len(parsed_data)} frontmatter blocks parsed, ids match file names",
        }
    )

    no_rows = sorted(did for did, item in parsed_data.items() if item["row_count"] == 0)
    ragged = {did: item["ragged_rows"] for did, item in parsed_data.items() if item["ragged_rows"]}
    row_problems = []
    if no_rows:
        row_problems.append(f"no section-9 CSV rows: {no_rows}")
    if ragged:
        row_problems.append(f"rows with a column count different from the header: {ragged}")
    checks.append(
        {
            "check": "seed_rows_present",
            "status": "FAIL" if row_problems else "PASS",
            "detail": "; ".join(row_problems)
            or f"{sum(i['row_count'] for i in parsed_data.values())} rows parsed, all well-formed",
        }
    )

    by_status: dict[str, int] = {}
    for item in parsed_data.values():
        by_status[item["status"]] = by_status.get(item["status"], 0) + 1
    approved = sorted(did for did in expected if parsed_data.get(did, {}).get("approved"))
    not_approved = [did for did in expected if did not in approved]
    checks.append(
        {
            "check": "approval",
            "status": "FAIL" if not_approved else "PASS",
            "detail": (
                f"{len(approved)}/{len(expected)} datasets approved per frontmatter status "
                f"(statuses observed: {by_status}; approved states: "
                f"{sorted(APPROVED_FRONTMATTER_STATES)})"
            ),
            "approved_count": len(approved),
            "not_approved": not_approved,
        }
    )

    checks.append({"check": "database_load", **db_load})

    statuses = [c["status"] for c in checks]
    verdict = overall_verdict(statuses)
    if verdict == "PASS":
        b14 = "RESOLVED - every check passed in this run"
    else:
        open_checks = [c["check"] for c in checks if c["status"] != "PASS"]
        b14 = f"OPEN - checks not passed: {open_checks}"
    return {
        "verdict": verdict,
        "b14_resolution": b14,
        "checks": checks,
        "approved_count": len(approved),
        "expected_datasets": len(expected),
        "frontmatter_status_counts": by_status,
    }


def generate_markdown_register(datasets, total_rows, evaluation, mode, out_path=None):
    """Write the register; every status in it is computed by evaluate_baseline()."""
    out_path = out_path or OUTPUT_REGISTER
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    verdict = evaluation["verdict"]
    expected = evaluation["expected_datasets"]
    db_check = next(c for c in evaluation["checks"] if c["check"] == "database_load")
    tiers_covered = len({d["tier"] for d in datasets})
    loaded_line = (
        f"- **Seed Records Loaded into `{DB_NAME}`:** {total_rows}"
        if db_check["status"] == "PASS"
        else f"- **Database Load:** {db_check['status']} - {db_check['detail']}"
    )

    lines = [
        "---",
        "id: REG-MD-01",
        "title: Master Data Approval and B-14 Escalation Register",
        "project: 1000FiX ERP System v2.0",
        "milestone: R02-M04",
        "task: R02-M04-T05",
        f"verdict: {verdict}",
        f"b14_status: {json.dumps(evaluation['b14_resolution'])}",
        f"date: {today}",
        f"mode: {mode}",
        "generated_by: tooling/scripts/load-master-data.py (statuses computed from the MD-* frontmatter)",
        "classification: CONFIDENTIAL — Internal Use Only",
        "---",
        "",
        "# Master Data Approval and B-14 Escalation Register",
        "",
        "## Summary & B-14 Status",
        "",
        "> Blocker `B-14`: *48 MD-* master-data content files — Odoo cannot be configured "
        "without them.*",
        f"> Computed verdict of this run: **{verdict}**. B-14: **{evaluation['b14_resolution']}**.",
        "> A dataset counts as approved only when its own frontmatter `status` is one of "
        f"{', '.join(f'`{s}`' for s in sorted(APPROVED_FRONTMATTER_STATES))}.",
        "",
        "### Key Metrics",
        f"- **Specifications Found:** {len(datasets)} / {expected}",
        f"- **Approved per Frontmatter:** {evaluation['approved_count']} / {expected} "
        f"(statuses observed: {evaluation['frontmatter_status_counts']})",
        f"- **Seed Rows Parsed:** {sum(d['rows'] for d in datasets)}",
        loaded_line,
        f"- **Load Tiers Covered:** {tiers_covered} / {len(TIER_MAP)}",
        "",
        "### Checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    for c in evaluation["checks"]:
        detail = str(c["detail"]).replace("|", "\\|")
        lines.append(f"| `{c['check']}` | **{c['status']}** | {detail} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Load Tier Architecture (per MD-048)",
            "",
            "| Tier | Name | Datasets | Rationale |",
            "|:---:|---|---|---|",
        ]
    )
    for tier in sorted(TIER_MAP):
        ids = ", ".join(f"`{did}`" for did in TIER_MAP[tier])
        name = TIER_NAMES[tier].split("—", 1)[-1].strip()
        lines.append(f"| **{tier}** | {name} | {ids} | {TIER_RATIONALE.get(tier, '')} |")

    lines.extend(
        [
            "",
            "---",
            "",
            f"## Master Data Approval Register ({len(datasets)} Datasets)",
            "",
            "| Tier | Dataset ID | Title | Domain | Module | Wave | Sample Rows | Checksum (SHA-256) | Approval (frontmatter) | Approver |",
            "|:---:|:---:|---|---|:---:|:---:|:---:|:---:|:---:|---|",
        ]
    )
    for d in datasets:
        lines.append(
            f"| T{d['tier']} | `{d['dataset_id']}` | {d['title']} | {d['domain']} | `{d['module']}` | {d['wave']} | {d['rows']} | `{d['sha256'][:8]}...` | **{d['approval_status']}** | {d['approver']} |"
        )

    rollup: dict[str, list[int]] = {}
    for d in datasets:
        entry = rollup.setdefault(str(d["approver"]), [0, 0])
        entry[0] += 1
        entry[1] += 1 if d["approved"] else 0
    lines.extend(
        [
            "",
            "---",
            "",
            "## Sign-Off by Approver (computed from frontmatter)",
            "",
            "| Approver | Datasets | Approved | Status |",
            "|---|:---:|:---:|:---:|",
        ]
    )
    for approver in sorted(rollup):
        total, done = rollup[approver]
        status = "SIGNED OFF" if done == total else f"PENDING ({total - done} outstanding)"
        lines.append(f"| {approver} | {total} | {done} | **{status}** |")
    lines.extend(
        [
            "",
            "---",
            "*1000FiX Services Limited · ERP Programme v2.0 · Milestone R02-M04 · generated "
            f"{datetime.now(UTC).isoformat(timespec='seconds')}*",
            "",
        ]
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes("\n".join(lines).encode("utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(payload, indent=2).encode("utf-8"))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="parse and evaluate only: no DB connection, nothing written under migrations/",
    )
    args = parser.parse_args(argv)
    mode = "dry-run" if args.dry_run else "load"

    print("================================================================================")
    print("  1000FiX ERP v2.0 - Master Data Loader & B-14 Approval Register Generator")
    print(f"  Milestone R02-M04 Task T05: 48 MD-* Content Sets across 10 Load Tiers ({mode})")
    print("================================================================================")

    if not MD_ROOT.exists():
        print(f"Error: Master data root path not found: {MD_ROOT}")
        return EXIT_CODES["FAIL"]

    parsed_data = parse_all()
    total_sample_rows = sum(item["row_count"] for item in parsed_data.values())

    if args.dry_run:
        summary = tiered_summary(parsed_data)
        db_load = {
            "status": "UNMEASURED",
            "detail": "dry run: no database connection made, nothing loaded",
            "loaded_datasets": None,
        }
        out_json = DRY_RUN_EVIDENCE
    else:
        summary = tiered_summary(parsed_data)
        try:
            conn = get_db()
        except Exception as exc:  # unreachable DB -> UNMEASURED, never a claimed load
            db_load = {
                "status": "UNMEASURED",
                "detail": f"cannot connect to {DB_HOST}:{DB_PORT}/{DB_NAME}: {type(exc).__name__}: {exc}",
                "loaded_datasets": None,
            }
        else:
            conn.autocommit = False
            try:
                summary, total_sample_rows = load_master_data(conn)
            except Exception as exc:
                conn.rollback()
                db_load = {
                    "status": "FAIL",
                    "detail": f"load failed: {type(exc).__name__}: {exc}",
                    "loaded_datasets": 0,
                }
            else:
                expected = len(expected_dataset_ids())
                db_load = {
                    "status": "PASS" if len(summary) == expected else "FAIL",
                    "detail": f"{len(summary)}/{expected} datasets and {total_sample_rows} rows "
                    f"upserted into {DB_NAME}",
                    "loaded_datasets": len(summary),
                }
            finally:
                conn.close()
        out_json = OUTPUT_JSON

    evaluation = evaluate_baseline(parsed_data, db_load)

    for c in evaluation["checks"]:
        print(f"  [{c['status']}] {c['check']}: {c['detail']}")
    print(f"\n[{evaluation['verdict']}] B-14: {evaluation['b14_resolution']}")

    _write_json(
        out_json,
        {
            "mode": mode,
            "verdict": evaluation["verdict"],
            "b14_resolution": evaluation["b14_resolution"],
            "checks": evaluation["checks"],
            "total_datasets": len(summary),
            "expected_datasets": evaluation["expected_datasets"],
            "approved_datasets": evaluation["approved_count"],
            "frontmatter_status_counts": evaluation["frontmatter_status_counts"],
            "total_seed_rows": total_sample_rows,
            "generated_at": datetime.now(UTC).isoformat(),
            "datasets": summary,
        },
    )
    print(f"[+] Output JSON saved to: {out_json}")

    generate_markdown_register(summary, total_sample_rows, evaluation, mode)
    print(f"[+] Master Data Approval Register generated at: {OUTPUT_REGISTER}")
    print("================================================================================")
    return EXIT_CODES.get(evaluation["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
