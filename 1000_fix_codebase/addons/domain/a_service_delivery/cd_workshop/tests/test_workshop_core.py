# Tests for cd_workshop (M31, CD-M31-01, CD-M31-02, CD-M31-03).
import inspect
import pytest
from unittest.mock import MagicMock


class TestWorkshopCore:
    def test_models_exist(self):
        """M31: verify all 5 core models are importable and defined."""
        from odoo.addons.cd_workshop.models.fix_workshop import FixWorkshop
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob
        from odoo.addons.cd_workshop.models.fix_workshop_part_line import FixWorkshopPartLine
        from odoo.addons.cd_workshop.models.fix_workshop_evidence import FixWorkshopEvidence

        assert FixWorkshop is not None
        assert FixWorkshopBench is not None
        assert FixWorkshopJob is not None
        assert FixWorkshopPartLine is not None
        assert FixWorkshopEvidence is not None

    def test_job_state_machine_declared(self):
        """AS-06 / DP-01: state transitions declared in one place with valid graph."""
        from odoo.addons.cd_workshop.models.fix_workshop_job import (
            WORKSHOP_JOB_STATES, VALID_JOB_TRANSITIONS
        )
        assert len(WORKSHOP_JOB_STATES) == 11
        assert len(VALID_JOB_TRANSITIONS) == 11

        # Terminal states
        assert VALID_JOB_TRANSITIONS["delivered"] == set()
        assert VALID_JOB_TRANSITIONS["cancelled"] == set()

        # Happy path transitions
        assert "intake" in VALID_JOB_TRANSITIONS["draft"]
        assert "in_repair" in VALID_JOB_TRANSITIONS["waiting_parts"]
        assert "burn_in" in VALID_JOB_TRANSITIONS["in_repair"]
        assert "qc_pending" in VALID_JOB_TRANSITIONS["burn_in"]
        assert "ready" in VALID_JOB_TRANSITIONS["qc_pending"]
        assert "delivered" in VALID_JOB_TRANSITIONS["ready"]

        # Rework loop exists
        assert "qc_failed" in VALID_JOB_TRANSITIONS["qc_pending"]
        assert "in_repair" in VALID_JOB_TRANSITIONS["qc_failed"]

    def test_bench_routing_level_logic(self):
        """CD-M31-02: bench capability level validation logic."""
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.exceptions import UserError

        bench = MagicMock()
        bench.repair_level = "l1"
        bench.state = "available"
        bench.max_concurrent_jobs = 1
        bench.current_job_count = 0
        bench.code = "BENCH-TEST-L1"

        job = MagicMock()
        job.name = "JOB-001"
        job.repair_level = "l2"  # Requires L2, bench is L1 -> should reject

        with pytest.raises(UserError, match="requires L2 capability, but bench BENCH-TEST-L1 is only L1"):
            FixWorkshopBench.action_assign_job(bench, job)

    def test_bench_capacity_limit_logic(self):
        """CD-M31-02: bench capacity limit prevents over-allocation."""
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.exceptions import UserError

        bench = MagicMock()
        bench.repair_level = "l2"
        bench.state = "occupied"
        bench.max_concurrent_jobs = 1
        bench.current_job_count = 1
        bench.code = "BENCH-TEST-FULL"

        job = MagicMock()
        job.name = "JOB-002"
        job.repair_level = "l2"

        with pytest.raises(UserError, match="maximum concurrent job capacity"):
            FixWorkshopBench.action_assign_job(bench, job)

    def test_evidence_attachment_delegates_to_cd_document_core(self):
        """AS-01 / MV-02: verify evidence attachment strictly calls fix.document.attach."""
        from odoo.addons.cd_workshop.models.fix_workshop_evidence import FixWorkshopEvidence

        # Source code inspection ensuring AS-01 unified attachment API call
        source = inspect.getsource(FixWorkshopEvidence.create_evidence)
        assert 'self.env["fix.document"].attach' in source
        assert 'document_type="evidence_pack"' in source
        assert 'res_model="fix.workshop.job"' in source
        assert 'isolation_tier=isolation_tier' in source

    def test_cross_wave_stub_m22_certification(self):
        """GV-005 / STUB-M31-M22-001: M31 -> M22 certification stub returns eligible with log until R06-M02."""
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob

        mock_self = MagicMock()
        mock_tech = MagicMock()
        mock_tech.name = "Rafiqul Islam"
        mock_tech.id = 12
        mock_tech.active = True

        result = FixWorkshopJob._check_technician_certification(mock_self, mock_tech, "l3")
        assert result is True

        source = inspect.getsource(FixWorkshopJob._check_technician_certification)
        assert "STUB-M31-M22-001" in source
        assert "R06-M02" in source

    def test_bru_srm_18_independent_qc_inspector(self):
        """BRU-SRM-18: repairing technician cannot perform own QC inspection."""
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob
        from odoo.exceptions import ValidationError

        mock_job = MagicMock()
        mock_tech = MagicMock()
        mock_tech.id = 99
        mock_tech.name = "Tanvir Ahmed"
        mock_job.technician_id = mock_tech
        mock_job.qc_inspector_id = mock_tech  # Same person!
        mock_job.env.user.employee_id = mock_tech

        with pytest.raises(ValidationError, match="BRU-SRM-18 Violation"):
            FixWorkshopJob._run_qc_inspection(mock_job, passed=True)

        source = inspect.getsource(FixWorkshopJob._run_qc_inspection)
        assert "STUB-M31-M23-001" in source
        assert "R06-M04" in source

    def test_burn_in_gate_for_l2_l3(self):
        """CD-M31-03: L2/L3 jobs require burn-in to pass before entering QC."""
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob
        from odoo.exceptions import UserError

        mock_job = MagicMock()
        mock_job.__iter__.return_value = [mock_job]
        mock_job.state = "in_repair"
        mock_job.repair_level = "l2"
        mock_job.burn_in_passed = False
        mock_job.name = "WSJ/2026/00042"
        mock_job._validate_transition = MagicMock()

        with pytest.raises(UserError, match="requires burn-in test to pass before QC"):
            FixWorkshopJob.action_transition(mock_job, "qc_pending")

    def test_monetary_costing_totals(self):
        """AS-10: Monetary total calculations."""
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob

        mock_job = MagicMock()
        mock_job.__iter__.return_value = [mock_job]
        line1 = MagicMock()
        line1.subtotal = 3500.0
        line2 = MagicMock()
        line2.subtotal = 1200.0
        mock_job.part_line_ids = [line1, line2]
        mock_job.labour_total = 800.0

        FixWorkshopJob._compute_totals(mock_job)
        assert mock_job.parts_total == 4700.0
        assert mock_job.total_repair_cost == 5500.0

    def test_constraints_declared(self):
        """Odoo 19 models.Constraint attributes."""
        from odoo.addons.cd_workshop.models.fix_workshop import FixWorkshop
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob

        assert hasattr(FixWorkshop, "_code_unique")
        assert hasattr(FixWorkshopBench, "_code_unique")
        assert hasattr(FixWorkshopJob, "_legacy_ref_unique")

    def test_bengali_fields_present(self):
        """DoD-08 / FF-25: Bengali naming fields present across workshop models."""
        from odoo.addons.cd_workshop.models.fix_workshop import FixWorkshop
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob

        assert "name_bn" in dir(FixWorkshop)
        assert "name_bn" in dir(FixWorkshopBench)
        assert "name_bn" in dir(FixWorkshopJob)

    def test_event_publish_sources(self):
        """AS-08: Events published from bench allocation, job transition, and evidence recording."""
        from odoo.addons.cd_workshop.models.fix_workshop_bench import FixWorkshopBench
        from odoo.addons.cd_workshop.models.fix_workshop_job import FixWorkshopJob
        from odoo.addons.cd_workshop.models.fix_workshop_evidence import FixWorkshopEvidence

        bench_src = inspect.getsource(FixWorkshopBench._emit_bench_assigned)
        assert "workshop.bench.assigned" in bench_src

        job_src = inspect.getsource(FixWorkshopJob._emit_job_transitioned)
        assert "workshop.job.transitioned" in job_src

        qc_src = inspect.getsource(FixWorkshopJob._emit_qc_completed)
        assert "workshop.qc.completed" in qc_src

        evid_src = inspect.getsource(FixWorkshopEvidence._emit_evidence_recorded)
        assert "workshop.evidence.recorded" in evid_src
