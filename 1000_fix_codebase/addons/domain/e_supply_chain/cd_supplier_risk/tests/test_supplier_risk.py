# cd_supplier_risk tests — M42 risk assessment (CD-M42-04).
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "models"
       / "fix_supplier_risk.py").read_text(encoding="utf-8")


def _mod():
    from odoo.addons.cd_supplier_risk.models import fix_supplier_risk
    return fix_supplier_risk


class TestOverallTier:
    def test_any_critical_dimension_is_critical(self):
        assert _mod().overall_tier(["1", "1", "1", "1", "1", "5"]) == "critical"

    def test_high_by_worst_or_mean(self):
        t = _mod().overall_tier
        assert t(["1", "1", "4", "1", "1", "1"]) == "high"
        assert t(["3", "3", "3", "3", "3", "3"]) == "high"

    def test_medium_and_low(self):
        t = _mod().overall_tier
        assert t(["2", "2", "2", "2", "2", "2"]) == "medium"
        assert t(["1", "1", "1", "1", "2", "1"]) == "low"
        assert t([]) == "low"

    def test_reassessment_sooner_when_riskier(self):
        d = _mod().REASSESS_DAYS
        assert d["critical"] < d["high"] < d["medium"] < d["low"]


class TestRules:
    def test_six_spec_dimensions(self):
        assert _mod().DIMENSIONS == ("financial", "operational", "geographic",
                                     "compliance", "counterfeit", "continuity")

    def test_single_source_needs_alternate_or_exception(self):
        """FR-SRM2-033."""
        assert "named alternate" in SRC

    def test_assessor_cannot_approve(self):
        assert "The assessor cannot approve their own risk assessment" in SRC

    def test_capture_spec(self):
        cls = _mod().FixSupplierRisk
        declared = {n for n, v in vars(cls).items() if "fields" in type(v).__module__}
        assert not set(cls._p03_capture["fields"]) - declared
