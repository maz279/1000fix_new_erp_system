# cd_supplier_qualification tests — M42 qualification, activation gate and
# integrity screening (CD-M42-02).
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "models"
       / "fix_supplier_qualification.py").read_text(encoding="utf-8")


def _mod():
    from odoo.addons.cd_supplier_qualification.models import fix_supplier_qualification
    return fix_supplier_qualification


def _declared_fields(cls):
    return {n for n, v in vars(cls).items() if "fields" in type(v).__module__}


class TestQualification:
    def test_versioned_and_unique(self):
        """T-03: re-qualification creates a new version."""
        m = _mod()
        assert hasattr(m.FixSupplierQualification, "_version_unique")
        assert '"superseded"' in SRC

    def test_immutable_once_approved(self):
        assert "An approved qualification is immutable" in SRC

    def test_anti_bribery_condition(self):
        """FR-SRM2-019: the declaration is a qualification condition."""
        body = SRC[SRC.index("def action_submit"):SRC.index("def action_approve")]
        assert "anti_bribery_declared" in body

    def test_scorer_not_sole_approver_at_strict_tiers(self):
        m = _mod()
        assert m.STRICT_TIERS == ("high", "critical")
        assert "the scorer cannot be the" in SRC

    def test_lapse_deactivates(self):
        """FR-SRM2-011: de-activate automatically on lapse."""
        body = SRC[SRC.index("def _cron_expire_qualifications"):]
        assert "action_suspend" in body


class TestActivationGate:
    def test_fails_closed(self):
        """T-01: an error denies, never permits."""
        body = SRC[SRC.index("def check_activation"):SRC.index("def _cron_expire")]
        assert "fail closed" in body
        assert body.count('"allow": False') >= 4

    def test_category_and_entity_scoped(self):
        """T-02: evaluated per (supplier, category, entity, date)."""
        body = SRC[SRC.index("def check_activation"):SRC.index("def _cron_expire")]
        for key in ('"category_id"', '"company_id"', '"valid_from", "<="',
                    '"valid_until", ">="'):
            assert key in body


class TestScreening:
    def test_outcome_rules(self):
        body = SRC[SRC.index("def _compute_outcome"):]
        assert "confirmed_match" in body and '"fail"' in body
        assert '"review"' in body

    def test_coc_version_tracked(self):
        """FR-SRM2-020: acceptance carries a version."""
        assert "code-of-conduct version" in SRC


class TestP03CaptureSpecs:
    def test_specs_reference_declared_fields(self):
        m = _mod()
        for cls in (m.FixSupplierQualification, m.FixSupplierScreening):
            missing = set(cls._p03_capture["fields"]) - _declared_fields(cls)
            assert not missing, f"{cls._name}: {missing}"
        assert m.FixSupplierQualification._p03_capture["form"] == "Qualification Questionnaire"
        assert m.FixSupplierScreening._p03_capture["form"] == "Integrity Screening Declaration"
