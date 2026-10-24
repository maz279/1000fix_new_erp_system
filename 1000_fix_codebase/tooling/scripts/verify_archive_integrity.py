#!/usr/bin/env python3
"""
verify_archive_integrity.py — 8-Class Archive Integrity & Restorability Verification (measured)
Milestone: R11-M02-T04 (Legacy decommissioning)
Standards: DA-006, ISO 15489-1:2016, RL-006 DCM-22..DCM-26

DCM-25: "D3 is reached when a person reads a sample, not when data is copied."
DCM-18: "Retention is computed from a trigger, never stored as a date at creation."

ARCHIVE_CLASSES below is the DECLARED archive plan (class, covered sources, format, path
inside the Z7-S3-ARCHIVE store, sample object, retention class). Per class this tool
MEASURES, in this run:
- archive_present: the archive file exists under the mounted archive store
  (--archive-root or R11_ARCHIVE_ROOT). No store mounted -> UNMEASURED; store mounted but
  file missing -> FAIL.
- checksum: sha256 and size of the archive are computed; they are compared with the
  archive-time fixity record `<archive>.sha256` (first token). Mismatch -> FAIL; no fixity
  record to compare against -> UNMEASURED.
- machine_restore_drill: an unencrypted archive is opened and fully read (zip CRC test,
  tar member walk, gzip decompress, parquet metadata) and the sample object must be in it.
  Encrypted archives (AES / GPG) need Vault-custodied keys this tool does not hold ->
  UNMEASURED; a format whose reader is not installed -> UNMEASURED.
- human_sample_read (DCM-25) is a person reading a sample -> always UNMEASURED here.
- retention_clock (DCM-18) runs from the decommission trigger event, which this tool
  cannot observe -> UNMEASURED; no disposal date is computed from an invented trigger.
Nothing is copied, restored to a database, decrypted or deleted.

Verdict: FAIL if any check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE. Writes only the evidence JSON and its Markdown record.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
EVIDENCE_NAME = "r11-m02-archive-register.json"
MD_NAME = "r11-m02-archive-integrity-proof.md"
ARCHIVE_STORE = "Z7-S3-ARCHIVE"
ARCHIVE_ROOT_ENV = "R11_ARCHIVE_ROOT"

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
INCOMPLETE = "INCOMPLETE"
CHUNK = 1024 * 1024

HUMAN_READ_REASON = (
    "DCM-25: D3 is reached when a person reads a sample; a person's read cannot be observed "
    "by this tool"
)
RETENTION_REASON = (
    "DCM-18: the retention clock runs from the decommission trigger event; that event is not "
    "observable here, so no trigger or disposal date is recorded"
)
ENCRYPTED_REASON = (
    "the archive is encrypted; its keys are Vault-custodied and not available to this tool, "
    "so it cannot be opened for a restore drill"
)

ARCHIVE_CLASSES = [
    {
        "class_id": "ARCH-CL-01",
        "class_name": "Database Dumps (MySQL & MS SQL)",
        "sources": ["SRC-01", "SRC-02"],
        "archive_format": "tar.gz + AES-256",
        "archive_path": "Z7-S3-ARCHIVE/databases/tracker_dumps_20261021.tar.gz.enc",
        "sample_table": "tbl_service_repair_orders",
        "retention_class": "RC-04 (Service Orders)",
        "retention_years": 5,
        "custodian": "Lead Data Steward (Mohammad Ali)",
    },
    {
        "class_id": "ARCH-CL-02",
        "class_name": "Branch Service Order Spreadsheets (excluding retained / purged sources)",
        # SRC-03..SRC-26 less SRC-20..SRC-22 (K, retained) and SRC-23 (P, purged) in the
        # decommission register (tooling/scripts/execute_legacy_decommission.py)
        "sources": [f"SRC-{n:02d}" for n in (*range(3, 20), 24, 25, 26)],
        "archive_format": "zip (Normalized XLSX/CSV)",
        "archive_path": "Z7-S3-ARCHIVE/spreadsheets/branch_order_sheets_bundle.zip",
        "sample_table": "dhanmondi_2024_service_log.xlsx",
        "retention_class": "RC-04 (Service Orders)",
        "retention_years": 5,
        "custodian": "Branch Operations Lead (Tariqul Islam)",
    },
    {
        "class_id": "ARCH-CL-03",
        "class_name": "Accounting History & Cash Books",
        "sources": ["SRC-27", "SRC-28", "SRC-29", "SRC-30"],
        "archive_format": "xml.gz + AES-256",
        "archive_path": "Z7-S3-ARCHIVE/finance/tally_and_cashbooks_20261021.xml.gz",
        "sample_table": "tally_company_a_journal_vouchers.xml",
        "retention_class": "RC-01 (Statutory General Ledger)",
        "retention_years": 7,
        "custodian": "Financial Controller (Mustafizur Rahman)",
    },
    {
        "class_id": "ARCH-CL-04",
        "class_name": "HR & Historic Payroll Records",
        "sources": ["SRC-32", "SRC-33", "SRC-34"],
        "archive_format": "tar.gz + GPG",
        "archive_path": "Z7-S3-ARCHIVE/hr/payroll_historic_2025_2026.tar.gz.gpg",
        "sample_table": "payroll_salary_sheet_fy25_26.xlsx",
        "retention_class": "RC-03 (Payroll & Statutory TDS)",
        "retention_years": 7,
        "custodian": "Head of HR (Nasreen Sultana)",
    },
    {
        "class_id": "ARCH-CL-05",
        "class_name": "WordPress CMS & Technical Media",
        "sources": ["SRC-35", "SRC-36"],
        "archive_format": "tar.zst",
        "archive_path": "Z7-S3-ARCHIVE/cms/wordpress_content_and_media.tar.zst",
        "sample_table": "wp_posts_and_manuals_metadata.json",
        "retention_class": "DC-14 (Web & Digital Assets)",
        "retention_years": 3,
        "custodian": "Marketing & Content Head (Shumona Akter)",
    },
    {
        "class_id": "ARCH-CL-06",
        "class_name": "Inventory SKU & Spare Parts Crosswalks",
        "sources": ["SRC-37", "SRC-38", "SRC-39", "SRC-40"],
        "archive_format": "csv.gz",
        "archive_path": "Z7-S3-ARCHIVE/inventory/parts_catalog_and_crosswalks.csv.gz",
        "sample_table": "parts_master_sku_catalog.csv",
        "retention_class": "RC-08 (Inventory & Asset History)",
        "retention_years": 5,
        "custodian": "Warehouse Operations Lead (Mahbub Alam)",
    },
    {
        "class_id": "ARCH-CL-07",
        "class_name": "Contact Histories & Warranty Registrations",
        "sources": ["SRC-42", "SRC-43"],
        "archive_format": "parquet.snappy",
        "archive_path": "Z7-S3-ARCHIVE/contacts/warranty_registrations_partitioned.parquet",
        "sample_table": "warranty_card_registrations_2020_2026.parquet",
        "retention_class": "RC-06 (Customer Warranty Records)",
        "retention_years": 5,
        "custodian": "Warranty Operations Lead (Imtiaz Ahmed)",
    },
    {
        "class_id": "ARCH-CL-08",
        "class_name": "Scanned RMA & Environmental Disposal Evidence",
        "sources": ["SRC-45", "SRC-46", "SRC-47", "SRC-48"],
        "archive_format": "pdf_manifest.zip",
        "archive_path": "Z7-S3-ARCHIVE/evidence_scans/rma_and_disposal_certs.zip",
        "sample_table": "disposal_doe_clearance_certificates.pdf",
        "retention_class": "RC-18 (Regulatory & Environmental Certs)",
        "retention_years": 5,
        "custodian": "E-Waste Compliance Officer (Tareq Hasan)",
    },
]


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


def store_relative(archive_path: str) -> str:
    """Path inside the archive store ('Z7-S3-ARCHIVE/a/b' -> 'a/b')."""
    prefix = ARCHIVE_STORE + "/"
    return archive_path[len(prefix) :] if archive_path.startswith(prefix) else archive_path


def is_encrypted(ac: dict[str, Any]) -> bool:
    fmt = str(ac.get("archive_format", "")).upper()
    path = str(ac.get("archive_path", "")).lower()
    return "AES" in fmt or "GPG" in fmt or path.endswith((".enc", ".gpg"))


def sha256_and_size(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while block := fh.read(CHUNK):
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def read_fixity(path: Path) -> str | None:
    """Archive-time sha256 recorded next to the archive (`<archive>.sha256`), if any."""
    fixity = path.with_name(path.name + ".sha256")
    if not fixity.is_file():
        return None
    tokens = fixity.read_text(encoding="utf-8", errors="replace").split()
    return tokens[0].lower() if tokens else ""


def _tar_drill(tf: tarfile.TarFile, sample: str) -> tuple[dict[str, str], int]:
    """Read every member of an open tar stream fully; the sample object must be in it."""
    count, found = 0, False
    for member in tf:
        count += 1
        found = found or Path(member.name).name == sample
        if member.isfile():
            extracted = tf.extractfile(member)
            if extracted is not None:
                while extracted.read(CHUNK):
                    pass
    return (
        _check(
            PASS if found else FAIL,
            f"{count} tar members read; sample {sample!r} " + ("present" if found else "MISSING"),
        ),
        count,
    )


def restore_drill(path: Path, ac: dict[str, Any]) -> tuple[dict[str, str], int | None]:
    """Open and fully read an unencrypted archive; -> (check, objects/lines read)."""
    if is_encrypted(ac):
        return _check(UNMEASURED, ENCRYPTED_REASON), None
    sample = str(ac.get("sample_table") or "")
    name = path.name.lower()
    try:
        if name.endswith(".zip"):
            with zipfile.ZipFile(path) as zf:
                bad = zf.testzip()
                members = zf.namelist()
            if bad is not None:
                return _check(FAIL, f"zip CRC failure in member {bad!r}"), len(members)
            found = any(Path(m).name == sample for m in members)
            return (
                _check(
                    PASS if found else FAIL,
                    f"{len(members)} members CRC-verified; sample {sample!r} "
                    + ("present" if found else "MISSING"),
                ),
                len(members),
            )
        if name.endswith((".tar.gz", ".tgz", ".tar")):
            with tarfile.open(path, "r:*") as tf:
                return _tar_drill(tf, sample)
        if name.endswith(".tar.zst"):
            try:
                import zstandard
            except ImportError:
                return _check(UNMEASURED, "zstandard is not installed: .tar.zst not readable"), None
            with (
                path.open("rb") as fh,
                zstandard.ZstdDecompressor().stream_reader(fh) as reader,
                tarfile.open(fileobj=reader, mode="r|") as tf,
            ):
                return _tar_drill(tf, sample)
        if name.endswith(".gz"):
            lines = 0
            with gzip.open(path, "rb") as gz:
                for _ in gz:
                    lines += 1
            return (
                _check(
                    PASS if lines else FAIL,
                    f"decompressed {lines} lines" if lines else "archive decompresses to nothing",
                ),
                lines,
            )
        if name.endswith(".parquet"):
            try:
                import pyarrow.parquet as pq
            except ImportError:
                return _check(UNMEASURED, "pyarrow is not installed: parquet not readable"), None
            rows = pq.ParquetFile(path).metadata.num_rows
            return _check(PASS if rows else FAIL, f"parquet metadata read: {rows} rows"), rows
    except Exception as exc:  # any read error is a failed drill, not an aborted run
        return _check(FAIL, f"archive unreadable: {exc}"), None
    return _check(UNMEASURED, f"no restore drill for format of {path.name!r}"), None


def verify_class(ac: dict[str, Any], archive_root: Path | None, root_reason: str) -> dict:
    checks: dict[str, dict[str, str]] = {}
    measured_sha, size, records_read, fixity = None, None, None, None
    local_path = None
    drill_executed = False
    if archive_root is None:
        checks["archive_present"] = _check(UNMEASURED, root_reason)
    else:
        local_path = archive_root / store_relative(ac["archive_path"])
        if local_path.is_file():
            checks["archive_present"] = _check(PASS, f"{local_path.name} present in the store")
        else:
            checks["archive_present"] = _check(FAIL, f"{ac['archive_path']} not in the store")
            local_path = None
    if local_path is None:
        reason = checks["archive_present"]["detail"]
        status = UNMEASURED if checks["archive_present"]["status"] == UNMEASURED else FAIL
        checks["checksum"] = _check(status, reason)
        checks["machine_restore_drill"] = _check(status, reason)
    else:
        try:
            measured_sha, size = sha256_and_size(local_path)
            fixity = read_fixity(local_path)
        except OSError as exc:
            checks["checksum"] = _check(FAIL, f"archive unreadable: {exc}")
        else:
            if fixity is None:
                checks["checksum"] = _check(
                    UNMEASURED,
                    f"sha256 measured, but no archive-time fixity record "
                    f"({local_path.name}.sha256) to compare it with",
                )
            else:
                checks["checksum"] = _check(
                    PASS if fixity == measured_sha else FAIL,
                    "sha256 matches the archive-time fixity record"
                    if fixity == measured_sha
                    else f"sha256 {measured_sha[:12]}... != fixity record {fixity[:12]}...",
                )
        checks["machine_restore_drill"], records_read = restore_drill(local_path, ac)
        drill_executed = checks["machine_restore_drill"]["status"] in (PASS, FAIL)
    checks["human_sample_read"] = _check(UNMEASURED, HUMAN_READ_REASON)
    checks["retention_clock"] = _check(UNMEASURED, RETENTION_REASON)
    status = derive_verdict([c["status"] for c in checks.values()])
    return {
        "archive_class_id": ac["class_id"],
        "archive_class_name": ac["class_name"],
        "covered_sources": list(ac["sources"]),
        "storage_path": ac["archive_path"],
        "archive_format": ac["archive_format"],
        "measured_size_bytes": size,
        "formatted_size": None if size is None else f"{size / (1024 * 1024):.2f} MB",
        "sha256_checksum": measured_sha,
        "fixity_record_checksum": fixity,
        "restorability_drill": {
            "sample_object_expected": ac["sample_table"],
            "drill_executed": drill_executed,
            "records_read_and_verified": records_read,
            "data_integrity_check": checks["machine_restore_drill"]["status"],
            "human_sample_read_status": checks["human_sample_read"]["status"],
        },
        "retention_governance": {
            "governing_standard": "DA-006 / LG-009",
            "retention_class": ac["retention_class"],
            "retention_period_years": ac["retention_years"],
            "retention_trigger_event": "PRODUCTION_CUTOVER_AND_DECOMMISSION",
            "trigger_date": None,
            "statutory_disposal_date": None,
            "retention_clock_status": checks["retention_clock"]["status"],
        },
        "custodian_role": ac["custodian"],
        "checks": checks,
        "verification_status": status,
    }


def resolve_archive_root(archive_root: str | Path | None) -> tuple[Path | None, str]:
    raw = archive_root if archive_root is not None else os.environ.get(ARCHIVE_ROOT_ENV)
    if not raw:
        return None, (
            f"the {ARCHIVE_STORE} archive store is not mounted on this workstation "
            f"(pass --archive-root or set {ARCHIVE_ROOT_ENV})"
        )
    root = Path(raw)
    if not root.is_dir():
        return None, f"archive store root {root} is not a mounted directory"
    return root, ""


def build_evidence(archive_root: str | Path | None = None) -> dict[str, Any]:
    root, root_reason = resolve_archive_root(archive_root)
    classes = [verify_class(ac, root, root_reason) for ac in ARCHIVE_CLASSES]
    executed = [c for c in classes if c["restorability_drill"]["drill_executed"]]
    tested = len(executed)
    restorable = sum(1 for c in executed if c["checks"]["machine_restore_drill"]["status"] == PASS)
    present = sum(1 for c in classes if c["checks"]["archive_present"]["status"] == PASS)
    sizes = [c["measured_size_bytes"] for c in classes if c["measured_size_bytes"] is not None]
    verdict = derive_verdict([chk["status"] for c in classes for chk in c["checks"].values()])
    return {
        "milestone": "R11-M02",
        "task": "R11-M02-T04",
        "title": "8-Class Legacy Archive Integrity & Restorability Verification Register",
        "execution_timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "governing_standards": ["DA-006", "ISO 15489-1:2016", "RL-006 DCM-22..DCM-26"],
        "measurement_policy": "GV-009: every status is measured in this run; what cannot be "
        "observed from this workstation is UNMEASURED with its reason",
        "archive_store": ARCHIVE_STORE,
        "archive_store_mounted": root is not None,
        "archive_store_reason": root_reason or None,
        "total_archive_classes": len(classes),
        "total_archive_classes_present": present,
        "total_archive_classes_tested": tested,
        "total_archive_classes_restorable": restorable,
        "total_measured_archive_bytes": sum(sizes) if sizes else None,
        "formatted_total_archive_volume": (
            f"{sum(sizes) / (1024 * 1024 * 1024):.2f} GB" if sizes else None
        ),
        "restorability_success_rate": f"{restorable / tested * 100:.1f}%" if tested else None,
        "retention_clock_policy": "DA-006 / DCM-18: computed from the trigger event only",
        "verdict": verdict,
        "overall_status": verdict,
        "archive_classes": classes,
    }


def _md(value: Any) -> str:
    return "n/a" if value is None else str(value).replace("|", "/")


def render_markdown(ev: dict[str, Any]) -> str:
    out = [
        "# Legacy Archive Integrity & Restorability Verification (DA-006 / ISO 15489)",
        "",
        "## Task R11-M02-T04 Verification Record",
        "",
        f"- **Execution Timestamp**: {ev['execution_timestamp']}",
        f"- **Verdict (computed)**: `{ev['verdict']}`",
        f"- **Archive store mounted**: {ev['archive_store_mounted']}"
        + (f" — {ev['archive_store_reason']}" if ev["archive_store_reason"] else ""),
        f"- **Restore drills executed**: {ev['total_archive_classes_tested']} / "
        f"{ev['total_archive_classes']}; restorable: {ev['total_archive_classes_restorable']} "
        f"({_md(ev['restorability_success_rate'])})",
        f"- **Measured archive volume**: {_md(ev['formatted_total_archive_volume'])}",
        "",
        "---",
        "",
        "### 8-Class Archive Register",
        "",
        "| Class ID | Class Name | Size | SHA-256 | Present | Checksum | Restore drill "
        "| Human read | Retention clock | Status |",
        "|---|---|---:|---|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for c in ev["archive_classes"]:
        ch = c["checks"]
        sha = f"`{c['sha256_checksum'][:16]}...`" if c["sha256_checksum"] else "n/a"
        out.append(
            f"| **{c['archive_class_id']}** | {_md(c['archive_class_name'])} "
            f"| {_md(c['formatted_size'])} | {sha} | `{ch['archive_present']['status']}` "
            f"| `{ch['checksum']['status']}` | `{ch['machine_restore_drill']['status']}` "
            f"| `{ch['human_sample_read']['status']}` | `{ch['retention_clock']['status']}` "
            f"| `{c['verification_status']}` |"
        )
    reasons = sorted(
        {
            f"- {name}: {c['detail']}"
            for cls in ev["archive_classes"]
            for name, c in cls["checks"].items()
            if c["status"] == UNMEASURED
        }
    )
    failures = [
        f"- `{cls['archive_class_id']}.{name}`: {c['detail']}"
        for cls in ev["archive_classes"]
        for name, c in cls["checks"].items()
        if c["status"] == FAIL
    ]
    if failures:
        out += ["", "Failed checks:", "", *failures]
    if reasons:
        out += ["", "UNMEASURED, and why:", "", *reasons]
    out.append("")
    if ev["verdict"] == PASS:
        out += ["Every archive check above was measured as passed.", ""]
    else:
        out += [
            f"Archive integrity and restorability are not established by this record "
            f"(verdict `{ev['verdict']}`).",
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
    ap = argparse.ArgumentParser(description="R11-M02-T04 archive integrity (measured)")
    ap.add_argument(
        "--archive-root",
        default=None,
        help=f"local mount of the {ARCHIVE_STORE} store (default: ${ARCHIVE_ROOT_ENV})",
    )
    args = ap.parse_args(argv)
    ev = build_evidence(args.archive_root)
    json_path, md_path = write_outputs(ev)
    print(
        f"R11-M02-T04: {ev['total_archive_classes_tested']}/{ev['total_archive_classes']} restore "
        f"drills executed, {ev['total_archive_classes_restorable']} restorable"
    )
    print(f"Verdict: {ev['verdict']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return exit_code_for(ev["verdict"])


if __name__ == "__main__":
    sys.exit(main())
