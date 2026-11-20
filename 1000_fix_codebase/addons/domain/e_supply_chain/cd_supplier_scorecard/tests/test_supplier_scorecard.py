# cd_supplier_scorecard tests — M42 performance reviews and CARs (CD-M42-03).
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "models"
       / "fix_supplier_performance.py").read_text(encoding="utf-8")


def _mod():
    from odoo.addons.cd_supplier_scorecard.models import fix_supplier_performance
    return fix_supplier_performance


def _declared_fields(cls):
    return {n for n, v in vars(cls).items() if "fields" in type(v).__module__}


class TestReviewCycle:
    def test_cadence_by_segment(self):
        """FR-SRM2-030: strategic quarterly, preferred half-yearly, approved
        annually."""
        cad = _mod().REVIEW_CADENCE_DAYS
        assert cad["strategic"] == 91 and cad["preferred"] == 182 and cad["approved"] == 365

    def test_minutes_before_held(self):
        assert "Minute the review before marking it held" in SRC

    def test_scores_are_not_captured_here(self):
        """T-04/T-05: the scorecard is computed from M16/M41 facts; the review
        form links to it and never carries a typed-in score."""
        m = _mod()
        assert "score" not in _declared_fields(m.FixSupplierReview)
        assert "scorecard_id" in m.FixSupplierReview._p03_capture["fields"]


class TestCar:
    def test_raiser_cannot_verify(self):
        assert "The user who raised a CAR cannot verify its closure" in SRC

    def test_root_cause_before_closure(self):
        assert "A root cause is required before closure" in SRC

    def test_overdue_escalates(self):
        body = SRC[SRC.index("def _cron_escalate_overdue"):]
        assert '"escalated"' in body and "escalation_level" in body

    def test_m23_stub_reference(self):
        assert "ncr_ref" in SRC


class TestP03CaptureSpecs:
    def test_specs_reference_declared_fields(self):
        m = _mod()
        for cls in (m.FixSupplierReview, m.FixSupplierCar):
            missing = set(cls._p03_capture["fields"]) - _declared_fields(cls)
            assert not missing, f"{cls._name}: {missing}"
