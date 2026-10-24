#!/usr/bin/env python3
"""migrations/load_workshop_wip.py — Wave-2 M31 Workshop Open WIP Migration Loader (ETL-6).

Specifications:
  - Roadmap: Milestone R03-M02-T04 (R03_Field_Operations_Inventory_Offline_Engine.md)
  - Ruling: P01-M07-T06 (TSS §19.1) — History is NOT migrated; only OPEN WIP tickets from
    physical paper job cards are captured into active fix.workshop.job records.
  - Standards:
      MIG-02: Control totals reconciliation (target 100% of open WIP paper cards captured)
      MIG-03: Permanent legacy_reference ('LEG:JOB-CARD:<hub>:<card_number>')
      AS-06: Unified state machine — open states only (intake, diagnostic, waiting_parts, in_repair, burn_in, qc_pending)

GV-009: the loader writes fix.workshop.job through an Odoo environment (`env`). Without
one it only VALIDATES the extract (mode "dry_run", status DRY_RUN_NOT_LOADED): it never
reports a card as processed/created or the run as reconciled when nothing was loaded.
With an env, the status is derived from a read-back of the jobs by legacy reference.
A card whose workshop is not on the target is rejected (listed) - the loader never
creates master data (workshops) from a paper card, and never invents field values.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"


def generate_workshop_wip_extract(out_dir: Path = EXTRACTS_DIR) -> Path:
    """Generate synthetic physical paper job card extract for open WIP across 5 depots.

    `out_dir` defaults to the committed migrations/extracts; tests pass a tmp dir.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    extract_path = out_dir / "workshop_wip_extract.json"

    hubs = [
        ("TEJGAON", "WS-TEJGAON-01", "Central Workshop Tejgaon", 15),
        ("DHANMONDI", "WS-DHANMONDI-01", "Dhanmondi Hub Workshop", 8),
        ("CHATTOGRAM", "WS-CTG-01", "Chattogram Central Depot", 10),
        ("BOGURA", "WS-BOGURA-01", "Bogura Regional Hub", 6),
        ("SYLHET", "WS-SYLHET-01", "Sylhet Hub Workshop", 6),
    ]

    faults = [
        ("Screen cracked & touch unresponsive", "l1", "in_repair"),
        ("Battery draining fast & swelling", "l1", "waiting_parts"),
        ("No power / Charging port loose", "l2", "diagnostic"),
        ("Backlight IC failed / Display blank", "l2", "in_repair"),
        ("Motherboard water damage / Short circuit", "l3", "in_repair"),
        ("Power management PMIC burned / No boot", "l3", "diagnostic"),
        ("Audio codec failure / No microphone", "l2", "burn_in"),
        ("BGA processor reballing required", "l3", "burn_in"),
        ("Display replacement completed — awaiting final check", "l1", "qc_pending"),
        ("Inverter board repair finished", "l2", "qc_pending"),
    ]

    brands = [
        ("Samsung", "Galaxy S23 Ultra", "SM-S918B"),
        ("Apple", "iPhone 14 Pro", "A2890"),
        ("Dell", "Latitude 5430", "LAT-5430"),
        ("HP", "EliteBook 840 G8", "EB-840G8"),
        ("Lenovo", "ThinkPad T14 Gen 3", "TP-T14"),
        ("Walton", "Primo RX9", "W-RX9"),
        ("Gree", "Lomo Inverter AC 1.5T", "G-LOMO-15"),
    ]

    open_cards = []
    card_sequence = 1001

    for hub_code, ws_code, ws_name, count in hubs:
        for i in range(count):
            card_no = f"JC-{hub_code[:3]}-2026-{card_sequence}"
            fault_text, repair_level, state = faults[(card_sequence) % len(faults)]
            brand, model_name, default_code = brands[(card_sequence) % len(brands)]
            serial_no = f"SN-{brand[:3].upper()}-{hub_code[:3]}-{card_sequence:05d}"
            tech_badge = f"TECH-{hub_code[:3]}-{(i % 3) + 1:02d}"
            bench_code = f"BENCH-{hub_code[:3]}-{repair_level.upper()}-{(i % 2) + 1:02d}"

            open_cards.append(
                {
                    "paper_card_no": card_no,
                    "hub_code": hub_code,
                    "workshop_code": ws_code,
                    "workshop_name": ws_name,
                    "intake_date": "2026-10-15T09:30:00Z",
                    "customer_name": f"Customer {hub_code} {i + 1}",
                    "customer_phone": f"+880171{card_sequence:06d}",
                    "device_brand": brand,
                    "device_model": model_name,
                    "device_code": default_code,
                    "serial_number": serial_no,
                    "reported_fault": fault_text,
                    "repair_level": repair_level,
                    "state": state,
                    "assigned_technician_badge": tech_badge,
                    "assigned_technician_name": f"Technician {tech_badge}",
                    "bench_code": bench_code,
                    "estimated_cost": 2500.0 + (i * 350.0),
                    "legacy_reference": f"LEG:JOB-CARD:{hub_code}:{card_no}",
                }
            )
            card_sequence += 1

    extract_path.write_text(
        json.dumps(open_cards, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    logger.info("Generated %d open workshop paper job cards at %s", len(open_cards), extract_path)
    return extract_path


OPEN_STATES = frozenset(
    {"intake", "diagnostic", "waiting_parts", "in_repair", "burn_in", "qc_pending"}
)


class WorkshopWIPMigrator:
    """ETL-6: migrates open workshop WIP paper cards into fix.workshop.job (Odoo env)."""

    def __init__(self, env: Any = None):
        self.env = env
        self.stats: dict[str, Any] = {
            "mode": "dry_run" if env is None else "load",
            "total_extracted": 0,
            "validated": 0,
            "skipped_closed": 0,
            "created_jobs": 0,
            "already_present": 0,
            "rejected": 0,
            "errors": 0,
            "rejections": [],
        }

    def load_data(self, extract_file: Path | None = None) -> list[dict[str, Any]]:
        path = extract_file or (EXTRACTS_DIR / "workshop_wip_extract.json")
        if not path.exists():
            # never generate synthetic cards silently and load them as if extracted
            raise FileNotFoundError(
                f"workshop WIP extract not found: {path} "
                "(generate the synthetic one with generate_workshop_wip_extract())"
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        self.stats["total_extracted"] = len(data)
        return data

    def _reject(self, row: dict[str, Any], reason: str) -> None:
        self.stats["rejections"].append(
            {"legacy_reference": row.get("legacy_reference"), "reason": reason}
        )

    def run_migration(self, extract_file: Path | None = None) -> dict[str, Any]:
        records = self.load_data(extract_file)
        logger.info("Starting Workshop WIP migration for %d cards...", len(records))

        open_refs = []
        for row in records:
            card_no = row.get("paper_card_no")
            state = row.get("state")

            # P01-M07-T06 Ruling Check: Only open WIP is migrated
            if state not in OPEN_STATES:
                logger.warning(
                    "P01-M07-T06 Ruling: Historical card %s in closed/delivered state '%s' skipped.",
                    card_no,
                    state,
                )
                self.stats["skipped_closed"] += 1
                self._reject(row, f"P01-M07-T06: card in closed state {state!r} is not migrated")
                continue
            if not row.get("legacy_reference"):
                self.stats["rejected"] += 1
                self._reject(row, "card without legacy_reference (MIG-03)")
                continue

            self.stats["validated"] += 1
            open_refs.append(row["legacy_reference"])
            if self.env is None:
                continue  # dry run: validated only, nothing loaded
            try:
                outcome = self._migrate_single_card(row)
            except Exception as e:
                logger.error("Failed to migrate card %s: %s", card_no, str(e))
                self.stats["errors"] += 1
                self._reject(row, f"load error: {e}")
                continue
            if outcome == "created":
                self.stats["created_jobs"] += 1
            elif outcome == "present":
                self.stats["already_present"] += 1
            else:
                self.stats["rejected"] += 1
                self._reject(row, outcome)

        if self.env is None:
            self.stats["loaded_in_target"] = 0
            self.stats["reconciliation_percent"] = None
            self.stats["status"] = "DRY_RUN_NOT_LOADED"
            return self.stats

        # read back what the target really holds for the eligible cards
        loaded = self.env["fix.workshop.job"].search_count([("legacy_reference", "in", open_refs)])
        eligible = len(open_refs)
        self.stats["loaded_in_target"] = loaded
        self.stats["reconciliation_percent"] = (
            round(loaded / eligible * 100.0, 2) if eligible else None
        )
        complete = eligible > 0 and loaded == eligible and not self.stats["errors"]
        self.stats["status"] = "RECONCILED_100_PERCENT" if complete else "PARTIAL_RECONCILIATION"
        return self.stats

    def _migrate_single_card(self, row: dict[str, Any]) -> str:
        """Create one fix.workshop.job; return 'created', 'present' or a rejection reason."""
        JobModel = self.env["fix.workshop.job"]
        WorkshopModel = self.env["fix.workshop"]
        legacy_ref = row["legacy_reference"]

        # Idempotency check (DI-04)
        if JobModel.search([("legacy_reference", "=", legacy_ref)], limit=1):
            return "present"

        workshop = WorkshopModel.search([("code", "=", row.get("workshop_code"))])
        if len(workshop) != 1:
            return f"workshop {row.get('workshop_code')!r} not found on target (fix.workshop.code)"

        JobModel.create(
            {
                "name": f"WSJ-{row['paper_card_no']}",
                "workshop_id": workshop.id,
                "repair_level": row["repair_level"],
                "state": row["state"],
                "device_serial": row.get("serial_number"),
                "fault_description": row["reported_fault"],
                "legacy_reference": legacy_ref,
                "intake_date": row.get("intake_date"),
            }
        )
        return "created"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    migrator = WorkshopWIPMigrator()
    result = migrator.run_migration()
    pct = result["reconciliation_percent"]
    print("\n" + "=" * 60)
    print("ETL-6 Workshop WIP Migration Summary")
    print("=" * 60)
    print(f"Mode                        : {result['mode']}")
    print(f"Total Extracted Paper Cards : {result['total_extracted']}")
    print(f"Validated Open WIP Cards    : {result['validated']}")
    print(f"Skipped Closed (P01-M07-T06): {result['skipped_closed']}")
    print(f"Created Jobs                : {result['created_jobs']}")
    print(f"Loaded In Target (read-back): {result['loaded_in_target']}")
    print(f"Rejected / Errors           : {result['rejected']} / {result['errors']}")
    print(f"Reconciliation              : {'n/a' if pct is None else f'{pct:.2f}%'}")
    print(f"Status                      : {result['status']}")
    print("=" * 60 + "\n")
    return 0 if result["status"] == "RECONCILED_100_PERCENT" else 1


if __name__ == "__main__":
    sys.exit(main())
