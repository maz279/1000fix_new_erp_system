# Migration Tests for ETL-6 (M31 Workshop Open WIP Paper Cards Migration).
import json
import pytest
from pathlib import Path

from migrations.load_workshop_wip import WorkshopWIPMigrator, generate_workshop_wip_extract

MIGRATIONS_DIR = Path(__file__).resolve().parents[1]
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"


class TestWorkshopWIPMigration:
    def test_extract_generation(self):
        """Verify workshop open WIP extract generates valid records."""
        path = generate_workshop_wip_extract()
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 45

    def test_p01_m07_t06_ruling_enforcement(self):
        """Verify closed historical cards are rejected per P01-M07-T06 ruling."""
        migrator = WorkshopWIPMigrator()
        test_cards = [
            {
                "paper_card_no": "JC-TEST-001",
                "hub_code": "TEJGAON",
                "state": "in_repair",
                "legacy_reference": "LEG:JOB-CARD:TEJGAON:JC-TEST-001",
            },
            {
                "paper_card_no": "JC-TEST-002",
                "hub_code": "TEJGAON",
                "state": "delivered",  # Closed historical! Must be rejected
                "legacy_reference": "LEG:JOB-CARD:TEJGAON:JC-TEST-002",
            },
            {
                "paper_card_no": "JC-TEST-003",
                "hub_code": "TEJGAON",
                "state": "cancelled",  # Closed historical! Must be rejected
                "legacy_reference": "LEG:JOB-CARD:TEJGAON:JC-TEST-003",
            },
        ]

        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(json.dumps(test_cards))
            tmp_path = Path(f.name)

        try:
            stats = migrator.run_migration(extract_file=tmp_path)
            assert stats["total_extracted"] == 3
            assert stats["processed"] == 1
            assert stats["skipped_closed"] == 2  # Both historical cards rejected
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_full_reconciliation_total(self):
        """MIG-02 / G2-04: Verify 100% control totals reconciliation on full extract."""
        migrator = WorkshopWIPMigrator()
        stats = migrator.run_migration()
        assert stats["total_extracted"] == 45
        assert stats["processed"] == 45
        assert stats["errors"] == 0
        assert stats["reconciliation_percent"] == 100.0
        assert stats["status"] == "RECONCILED_100_PERCENT"

    def test_legacy_reference_pattern(self):
        """MIG-03: Verify all legacy references follow LEG:JOB-CARD:<hub>:<card> pattern."""
        path = EXTRACTS_DIR / "workshop_wip_extract.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data:
            ref = row["legacy_reference"]
            assert ref.startswith("LEG:JOB-CARD:")
            parts = ref.split(":")
            assert len(parts) == 4
            assert parts[2] == row["hub_code"]
            assert parts[3] == row["paper_card_no"]
