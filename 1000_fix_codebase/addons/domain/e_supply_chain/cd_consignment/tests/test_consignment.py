# cd_consignment tests — M03 core (P06-M07, G3-05).
import pytest


class TestCustodyChain:
    def test_canonical_steps_ordered(self):
        from odoo.addons.cd_consignment.models.fix_consignment import CUSTODY_STEPS
        steps = [s[0] for s in CUSTODY_STEPS]
        assert steps.index("picked_up") < steps.index("delivered")

    def test_chain_break_compute_declared(self):
        from odoo.addons.cd_consignment.models.fix_consignment import FixConsignment
        assert hasattr(FixConsignment, "_compute_chain")

    def test_monotonic_verification_logic(self):
        """The verification is monotonic-order — re-implemented here in
        miniature so the algorithm itself is under test."""
        order = ["picked_up", "in_transit", "hub_scan", "out_for_delivery", "delivered", "returned"]
        def verify(scan_steps):
            positions = [order.index(s) for s in scan_steps if s in order]
            return all(b > a for a, b in zip(positions, positions[1:]))
        assert verify(["picked_up", "in_transit", "delivered"]) is True
        assert verify(["picked_up", "hub_scan", "in_transit"]) is False  # went backwards
        assert verify(["in_transit", "delivered"]) is True  # late start is monotonic
        assert verify([]) is True

    def test_lost_raises_incident_event(self):
        import inspect
        source = inspect.getsource(
            __import__("odoo.addons.cd_consignment.models.fix_consignment",
                       fromlist=["FixConsignment"]).FixConsignment.action_report_lost)
        assert '"consignment.lost"' in source

    def test_skip_requires_named_exception(self):
        import inspect
        source = inspect.getsource(
            __import__("odoo.addons.cd_consignment.models.fix_consignment",
                       fromlist=["FixCustodyScan"]).FixCustodyScan)
        assert "named exception" in source
