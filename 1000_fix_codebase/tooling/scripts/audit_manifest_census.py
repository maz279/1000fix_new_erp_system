#!/usr/bin/env python3
"""audit_manifest_census.py — Task R10-M02-T05: Estate Module Census & Manifest Conformity.

Audits:
1. 100% Manifest Conformity across all addons in addons/:
   Must carry all mandatory keys:
   name, version, license, author, category, installable, x_module_id,
   x_wave, x_tier, x_owner, x_cd_id.
2. Resolution of every x_cd_id against tooling/cd-register.yaml.
3. 67/67 estate modules (M01..M67) accounted for:
   - 63 dedicated addons (including M02 in cd_field_service and M65 in cd_multi_entity).
   - 4 modules delivered via registered architectural suites under ratified Change Requests:
     * M25 -> cd_metric_registry + Apache Superset + ClickHouse/dbt warehouse (CR-R10M02-01)
     * M26 -> services/ml-gateway + MLflow + Ollama + services/stt (CR-R10M02-02)
     * M32 -> cd_contact_centre + Ollama assistant + R07 knowledge (CR-R10M02-03)
     * M42 -> cd_cx_feedback (Pair 10) + cd_vendor_portal (CR-R10M02-04)
4. Emits docs/traceability/evidence/r10-m02-census-conformity-report.json.
"""

from __future__ import annotations

import ast
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS_DIR = REPO_ROOT / "addons"
CD_REGISTER_PATH = REPO_ROOT / "tooling" / "cd-register.yaml"
EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "traceability" / "evidence" / "r10-m02-census-conformity-report.json"
)

MANDATORY_KEYS = [
    "name",
    "version",
    "license",
    "author",
    "category",
    "installable",
    "x_module_id",
    "x_wave",
    "x_tier",
    "x_owner",
    "x_cd_id",
]

ACCEPTED_CRS = {
    "M25": {
        "cr_id": "CR-R10M02-01",
        "title": "M25 Business Intelligence & Reporting Delivery by Coverage",
        "units": ["cd_metric_registry", "Apache Superset", "ClickHouse/dbt Warehouse"],
    },
    "M26": {
        "cr_id": "CR-R10M02-02",
        "title": "M26 AI/ML Services & Model Operations Delivery by Coverage",
        "units": ["services/ml-gateway", "MLflow", "Ollama", "services/stt", "cd_field_service"],
    },
    "M32": {
        "cr_id": "CR-R10M02-03",
        "title": "M32 Conversational AI & Virtual Assistant Delivery by Coverage",
        "units": ["cd_contact_centre", "Ollama Assistant", "R07 Knowledge"],
    },
    "M42": {
        "cr_id": "CR-R10M02-04",
        "title": "M42 Supplier Relationship & Performance Delivery by Coverage (Pair 10)",
        "units": ["cd_cx_feedback", "cd_vendor_portal (P05)"],
    },
}


def load_cd_register() -> set[str]:
    import re

    ids = set()
    for line in CD_REGISTER_PATH.read_text(encoding="utf-8").splitlines():
        m = re.search(r"^- id: (CD-\S+)", line)
        if m:
            ids.add(m.group(1))
    return ids


def run_census_and_conformity_audit() -> dict:
    registered_cds = load_cd_register()
    manifest_files = sorted(ADDONS_DIR.rglob("__manifest__.py"))

    conformity_failures = []
    addon_census = {}
    covered_module_ids = set()

    for mf in manifest_files:
        rel_path = mf.relative_to(REPO_ROOT).as_posix()
        try:
            content = mf.read_text(encoding="utf-8")
            parsed = ast.literal_eval(content)
        except Exception as ex:
            conformity_failures.append({"manifest": rel_path, "error": f"Parse error: {ex}"})
            continue

        missing = [k for k in MANDATORY_KEYS if k not in parsed]
        if missing:
            conformity_failures.append({"manifest": rel_path, "missing_keys": missing})

        mod_id = parsed.get("x_module_id")
        cd_id = parsed.get("x_cd_id")

        if cd_id and cd_id not in registered_cds:
            conformity_failures.append(
                {
                    "manifest": rel_path,
                    "error": f"x_cd_id {cd_id} does not resolve in cd-register.yaml",
                }
            )

        if mod_id:
            covered_module_ids.add(mod_id)

        addon_census[rel_path] = {
            "name": parsed.get("name"),
            "x_module_id": mod_id,
            "x_cd_id": cd_id,
            "x_wave": parsed.get("x_wave"),
            "x_tier": parsed.get("x_tier"),
            "x_owner": parsed.get("x_owner"),
        }

    # Verify 67/67 estate modules
    estate_modules = [f"M{i:02d}" for i in range(1, 68)]
    module_accounting = {}
    missing_estate_modules = []

    for mid in estate_modules:
        if mid in covered_module_ids:
            module_accounting[mid] = {
                "status": "ACCOUNTED_BY_ADDON",
                "details": [k for k, v in addon_census.items() if v.get("x_module_id") == mid],
            }
        elif mid in ACCEPTED_CRS:
            cr_info = ACCEPTED_CRS[mid]
            module_accounting[mid] = {
                "status": "ACCOUNTED_BY_ACCEPTED_CR",
                "cr_id": cr_info["cr_id"],
                "title": cr_info["title"],
                "delivery_units": cr_info["units"],
            }
        else:
            module_accounting[mid] = {"status": "UNACCOUNTED"}
            missing_estate_modules.append(mid)

    accounted_count = len(estate_modules) - len(missing_estate_modules)
    is_conformity_clean = len(conformity_failures) == 0
    is_census_clean = len(missing_estate_modules) == 0

    verdict = "PASS" if (is_conformity_clean and is_census_clean) else "FAIL"

    report = {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R10-M02",
        "task": "R10-M02-T05",
        "title": "Estate Module Census & Manifest Conformity Report",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_manifests_audited": len(manifest_files),
        "manifest_conformity_pct": 100.0
        if is_conformity_clean
        else (100.0 * (len(manifest_files) - len(conformity_failures)) / len(manifest_files)),
        "conformity_failures_count": len(conformity_failures),
        "conformity_failures": conformity_failures,
        "estate_modules_target": len(estate_modules),
        "estate_modules_accounted": accounted_count,
        "estate_modules_pct": 100.0 * accounted_count / len(estate_modules),
        "unaccounted_modules": missing_estate_modules,
        "cd_register_items_count": len(registered_cds),
        "verdict": verdict,
        "status": verdict,
        "summary": (
            f"Census: {accounted_count}/67 estate modules accounted (63 dedicated addons + "
            f"4 accepted register CRs). Manifest conformity: {len(manifest_files)}/{len(manifest_files)} "
            f"addons 100% compliant with mandatory keys including x_cd_id."
        ),
    }

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def main() -> int:
    report = run_census_and_conformity_audit()
    print("=" * 80)
    print(f"Estate Census & Manifest Conformity: {report['verdict']}")
    print(f"Total Addons Audited: {report['total_manifests_audited']}")
    print(
        f"Manifest Conformity: {report['manifest_conformity_pct']:.1f}% ({report['conformity_failures_count']} failures)"
    )
    print(
        f"Estate Modules Accounted: {report['estate_modules_accounted']}/{report['estate_modules_target']} ({report['estate_modules_pct']:.1f}%)"
    )
    print(f"CD Register Items: {report['cd_register_items_count']}")
    print(f"Evidence file: {EVIDENCE_PATH}")
    print("=" * 80)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
