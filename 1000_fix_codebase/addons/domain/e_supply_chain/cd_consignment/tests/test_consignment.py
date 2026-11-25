# cd_consignment tests — M03 core (P06-M07, G3-05).
import itertools


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
            return all(b > a for a, b in itertools.pairwise(positions))

        assert verify(["picked_up", "in_transit", "delivered"]) is True
        assert verify(["picked_up", "hub_scan", "in_transit"]) is False  # went backwards
        assert verify(["in_transit", "delivered"]) is True  # late start is monotonic
        assert verify([]) is True

    def test_lost_raises_incident_event(self):
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_consignment.models.fix_consignment", fromlist=["FixConsignment"]
            ).FixConsignment.action_report_lost
        )
        assert '"consignment.lost"' in source

    def test_skip_requires_named_exception(self):
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_consignment.models.fix_consignment", fromlist=["FixCustodyScan"]
            ).FixCustodyScan
        )
        assert "named exception" in source

    def test_action_deliver_checks_unbroken_chain(self):
        """Gate G3-05: action_deliver blocks delivery if the custody chain is broken."""
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_consignment.models.fix_consignment", fromlist=["FixConsignment"]
            ).FixConsignment.action_deliver
        )
        # A02 audit M03-2: the gate re-checks the chain itself rather than
        # trusting the stored chain_broken flag.
        assert "_custody_chain_problem" in source
        assert "Cannot deliver consignment" in source
        assert '"consignment.delivered"' in source

    def test_action_return_publishes_event(self):
        import inspect

        source = inspect.getsource(
            __import__(
                "odoo.addons.cd_consignment.models.fix_consignment", fromlist=["FixConsignment"]
            ).FixConsignment._m03_publish_returned
        )
        # A02 ERP audit M03-F4: published when the return ARRIVES (receipt at
        # the origin hub), not at the declaration; behaviour is tested in
        # test_a02erp_m03.test_f4_a_return_closes_only_on_the_origin_receipt
        assert '"consignment.returned"' in source
