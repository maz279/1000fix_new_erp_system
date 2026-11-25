# Migration Tests for R06-M02-T05 (Attendance Opening Balances per TSS 19.1).
import json
import tempfile
from pathlib import Path

from migrations.load_attendance_opening import (
    AttendanceOpeningMigrator,
    generate_attendance_opening_extract,
)

MIGRATIONS_DIR = Path(__file__).resolve().parents[1]
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"


class TestAttendanceOpeningMigration:
    """Test suite asserting R06-M02-T05 / TSS 19.1 attendance opening balances migration."""

    def test_extract_generation_and_schema(self):
        """Verify attendance opening extract exists with valid schema."""
        path = generate_attendance_opening_extract()
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data) == 20
        first = data[0]
        assert "legacy_reference" in first
        assert "employee_code" in first
        assert "present_days" in first
        assert "opening_overtime_hours" in first
        assert first["legacy_reference"].startswith("LEG:SIGNIN_BOOK:")

    def test_tss19_1_non_migration_ruling_enforcement(self):
        """Verify closed historical attendance cards are rejected per TSS 19.1."""
        migrator = AttendanceOpeningMigrator()
        test_records = [
            {
                "legacy_reference": "LEG:SIGNIN_BOOK:TEJGAON:TEST-001",
                "employee_code": "TEST-001",
                "status": "active",
                "is_historical": False,
            },
            {
                "legacy_reference": "LEG:SIGNIN_BOOK:TEJGAON:TEST-002",
                "employee_code": "TEST-002",
                "status": "closed",  # Closed legacy card! Must be rejected
                "is_historical": False,
            },
            {
                "legacy_reference": "LEG:SIGNIN_BOOK:TEJGAON:TEST-003",
                "employee_code": "TEST-003",
                "status": "active",
                "is_historical": True,  # Historical punch card! Must be rejected
            },
        ]

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write(json.dumps(test_records))
            tmp_path = Path(f.name)

        try:
            stats = migrator.run_migration(extract_file=tmp_path)
            assert stats["mode"] == "dry_run"
            assert stats["total_extracted"] == 3
            assert stats["validated"] == 1
            assert stats["skipped_historical"] == 2  # Both historical/closed rejected
            assert len(stats["rejections"]) == 2
            # GV-009: a run without a target loads nothing and claims nothing
            assert stats["accepted"] == stats["loaded_count"] == 0
            assert stats["reconciled"] is None
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_full_extract_dry_run_validates_without_claiming_a_load(self):
        """R06-M02-T05: the dry run validates all 20 active balances and loads none."""
        migrator = AttendanceOpeningMigrator()
        stats = migrator.run_migration()
        assert stats["mode"] == "dry_run"
        assert stats["total_extracted"] == 20
        assert stats["validated"] == 20
        assert stats["skipped_historical"] == 0
        assert stats["accepted"] == stats["loaded_count"] == 0
        assert stats["reconciled"] is None

    def test_pipeline_load_quarantines_unknown_employees(self, pipeline_run):
        """The pipeline's real load: every opening balance is dispositioned and a balance
        whose employee is not on the target is quarantined with its reason."""
        counts = json.loads(pipeline_run[1].read_text(encoding="utf-8"))
        accepted = counts["accepted_records"]["attendance_opening"]
        quarantined = counts["quarantined_records"]["attendance_opening"]
        assert accepted + quarantined == 20
        reasons = counts["rejections"].get("attendance_opening", [])
        assert len(reasons) == quarantined
        assert all("not found on target" in r["reason"] for r in reasons)
