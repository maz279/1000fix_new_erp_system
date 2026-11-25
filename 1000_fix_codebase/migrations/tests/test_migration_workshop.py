# Migration Tests for ETL-6 (M31 Workshop Open WIP Paper Cards Migration).
import json
from pathlib import Path

import pytest

from migrations.load_workshop_wip import WorkshopWIPMigrator, generate_workshop_wip_extract

MIGRATIONS_DIR = Path(__file__).resolve().parents[1]
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"


class TestWorkshopWIPMigration:
    def test_extract_generation(self, tmp_path):
        """Verify workshop open WIP extract generates valid records (into tmp, never the
        committed migrations/extracts) and matches the committed extract."""
        path = generate_workshop_wip_extract(tmp_path)
        assert path.parent == tmp_path
        assert path.exists()
        committed = json.loads((EXTRACTS_DIR / "workshop_wip_extract.json").read_text("utf-8"))
        assert json.loads(path.read_text(encoding="utf-8")) == committed
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
            assert stats["validated"] == 1
            assert stats["skipped_closed"] == 2  # Both historical cards rejected
            assert len(stats["rejections"]) == 2
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_dry_run_never_claims_a_load(self):
        """GV-009: without an Odoo env nothing is loaded - and nothing is claimed."""
        migrator = WorkshopWIPMigrator()
        stats = migrator.run_migration()
        assert stats["mode"] == "dry_run"
        assert stats["total_extracted"] == 45
        assert stats["validated"] == 45
        assert stats["created_jobs"] == stats["loaded_in_target"] == 0
        assert stats["reconciliation_percent"] is None
        assert stats["status"] == "DRY_RUN_NOT_LOADED"

    def test_missing_extract_is_not_silently_generated(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            WorkshopWIPMigrator().run_migration(extract_file=tmp_path / "absent.json")
        assert not (tmp_path / "absent.json").exists()

    def test_env_load_status_is_derived_from_the_read_back(self, tmp_path):
        """With an env the status comes from the jobs actually found by legacy reference;
        a card whose workshop is not on the target is rejected, never auto-created."""
        cards = [
            {
                "paper_card_no": f"JC-T-{n}",
                "hub_code": "TEJGAON",
                "workshop_code": code,
                "state": "in_repair",
                "repair_level": "l1",
                "reported_fault": "x",
                "legacy_reference": f"LEG:JOB-CARD:TEJGAON:JC-T-{n}",
            }
            for n, code in ((1, "WS-OK"), (2, "WS-OK"), (3, "WS-MISSING"))
        ]
        path = tmp_path / "cards.json"
        path.write_text(json.dumps(cards), encoding="utf-8")
        env = _FakeEnv(workshops={"WS-OK"})
        stats = WorkshopWIPMigrator(env).run_migration(extract_file=path)
        assert stats["mode"] == "load"
        assert (stats["created_jobs"], stats["rejected"], stats["loaded_in_target"]) == (2, 1, 2)
        assert stats["reconciliation_percent"] == round(2 / 3 * 100, 2)
        assert stats["status"] == "PARTIAL_RECONCILIATION"
        assert "WS-MISSING" in stats["rejections"][0]["reason"]
        assert env.workshops_created == 0
        # second run: nothing new created, status from the same read-back
        again = WorkshopWIPMigrator(env).run_migration(extract_file=path)
        assert (again["created_jobs"], again["already_present"]) == (0, 2)
        assert len(env.jobs) == 2


class _FakeRecords(list):
    @property
    def id(self):
        return self[0]["id"]


class _FakeJobModel:
    def __init__(self, env):
        self.env = env

    def search(self, domain, limit=None):
        ((_, _, ref),) = domain
        return _FakeRecords(j for j in self.env.jobs if j["legacy_reference"] == ref)

    def search_count(self, domain):
        ((_, _, refs),) = domain
        return sum(1 for j in self.env.jobs if j["legacy_reference"] in refs)

    def create(self, vals):
        self.env.jobs.append({**vals, "id": len(self.env.jobs) + 1})


class _FakeWorkshopModel:
    def __init__(self, env):
        self.env = env

    def search(self, domain):
        ((_, _, code),) = domain
        return _FakeRecords([{"id": 1}] if code in self.env.workshops else [])

    def create(self, vals):
        self.env.workshops_created += 1


class _FakeEnv:
    def __init__(self, workshops):
        self.workshops = workshops
        self.workshops_created = 0
        self.jobs: list[dict] = []

    def __getitem__(self, name):
        models = {"fix.workshop.job": _FakeJobModel, "fix.workshop": _FakeWorkshopModel}
        return models[name](self)

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
