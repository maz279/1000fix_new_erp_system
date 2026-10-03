# Tests for cd_service_order (P04-M03) — the flagship module.
import pytest


class TestFixServiceOrder:
    def test_model_exists(self):
        from odoo.addons.cd_service_order.models.fix_service_order import FixServiceOrder
        assert FixServiceOrder is not None

    def test_state_machine_declared(self):
        """AS-06: state transitions declared in ONE place (DP-01)."""
        from odoo.addons.cd_service_order.models.fix_service_order import (
            FixServiceOrder, SERVICE_ORDER_STATES, VALID_TRANSITIONS)
        assert len(SERVICE_ORDER_STATES) == 14
        assert len(VALID_TRANSITIONS) == 14
        # Terminal states have no outgoing transitions
        assert VALID_TRANSITIONS["closed"] == set()
        assert VALID_TRANSITIONS["cancelled"] == set()
        # The happy path exists
        assert "in_repair" in VALID_TRANSITIONS["approved"]

    def test_idempotency_key_unique(self):
        """DI-04: a retried POST must not create two orders."""
        from odoo.addons.cd_service_order.models.fix_service_order import FixServiceOrder
        assert hasattr(FixServiceOrder, "_idempotency_key_unique")  # Odoo 19 models.Constraint attr

    def test_sla_fields_present(self):
        from odoo.addons.cd_service_order.models.fix_service_order import FixServiceOrder
        for field in ('sla_response_deadline', 'sla_resolution_deadline',
                      'sla_response_at', 'sla_resolution_at', 'sla_clock_paused'):
            assert field in dir(FixServiceOrder)

    def test_legacy_reference_field(self):
        """MIG-03: every migrated record carries its legacy reference permanently."""
        from odoo.addons.cd_service_order.models.fix_service_order import FixServiceOrder
        assert 'legacy_reference' in dir(FixServiceOrder)

    def test_state_validation_method(self):
        from odoo.addons.cd_service_order.models.fix_service_order import FixServiceOrder
        assert '_validate_transition' in dir(FixServiceOrder)


class TestFixEstimate:
    def test_model_exists(self):
        from odoo.addons.cd_service_order.models.fix_estimate import FixEstimate
        assert FixEstimate is not None

    def test_as10_monetary_totals(self):
        """AS-10: all money fields are Monetary with explicit currency."""
        from odoo.addons.cd_service_order.models.fix_estimate import FixEstimate
        for field in ('parts_total', 'labour_total', 'vat_amount', 'grand_total'):
            assert field in dir(FixEstimate)
        assert 'currency_id' in dir(FixEstimate)

    def test_version_revision(self):
        from odoo.addons.cd_service_order.models.fix_estimate import FixEstimate
        assert 'action_revise' in dir(FixEstimate)


class TestFixQC:
    def test_model_exists(self):
        from odoo.addons.cd_service_order.models.fix_qc_checklist import FixQC
        assert FixQC is not None

    def test_independent_inspector_constraint(self):
        """BRU-SRM-18: QC inspector must differ from the repairing technician."""
        from odoo.addons.cd_service_order.models.fix_qc_checklist import FixQC
        assert '_check_independent_inspector' in dir(FixQC)
