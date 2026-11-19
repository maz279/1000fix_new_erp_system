"""Business-rule gate tests — the audit's three unenforced H rules.

BRU-SRM-04 (QC before Ready), BRU-SRM-07/08 (estimate approval thresholds),
BRU-SRM-02 (warranty-active at creation), BRU-SRM-06 (30-day rework flag).
Source-inspection pattern: these run on the workstation without Odoo.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ORDER = (Path(__file__).resolve().parents[1] / "models" / "fix_service_order.py").read_text(
    encoding="utf-8"
)
ESTIMATE = (Path(__file__).resolve().parents[1] / "models" / "fix_estimate.py").read_text(
    encoding="utf-8"
)


class TestBrmSrm04QcGate(unittest.TestCase):
    """The gate lives in _check_qc_gate, called from _validate_transition (so
    every write path is gated) and from action_ready."""

    # A02 ERP audit M01-F4: the checklist that decides is chosen by
    # _fix_release_checklist (the newest of the current QC round)
    GATE = ORDER[ORDER.index("def _fix_release_checklist") : ORDER.index("def write")]

    def test_ready_checks_checklists(self):
        self.assertIn("qc_checklist_ids", self.GATE)
        ready = ORDER[ORDER.index("def action_ready") : ORDER.index("def action_deliver")]
        self.assertIn("_check_qc_gate", ready)

    def test_transition_check_applies_the_gate(self):
        source = ORDER[ORDER.index("def _validate_transition") : ORDER.index("def _check_qc_gate")]
        self.assertIn('new_state == "ready"', source)
        self.assertIn("_check_qc_gate()", source)

    def test_no_checklist_blocks(self):
        self.assertIn("no QC checklist", self.GATE)

    def test_unpassed_checklist_blocks(self):
        self.assertIn("not passed", self.GATE)


class TestBrmSrm0708ApprovalThresholds(unittest.TestCase):
    def test_thresholds_declared(self):
        self.assertIn("APPROVAL_THRESHOLD = 5000", ESTIMATE)
        self.assertIn("DUAL_APPROVAL_THRESHOLD = 25000", ESTIMATE)

    def test_above_5000_needs_customer_approval(self):
        source = ESTIMATE[
            ESTIMATE.index("def action_approve") : ESTIMATE.index("def action_reject")
        ]
        self.assertIn("customer_approval_ref", source)

    def test_above_25000_needs_both(self):
        source = ESTIMATE[
            ESTIMATE.index("def action_approve") : ESTIMATE.index("def action_reject")
        ]
        self.assertIn("manager_approval_uid", source)
        self.assertIn("BRU-SRM-08", source)

    def test_manager_second_key_ordering(self):
        """BRU-SRM-08: the manager approves AFTER the customer approval —
        the second key cannot be recorded first."""
        source = ESTIMATE[ESTIMATE.index("def action_manager_approve") :]
        self.assertIn("customer approval must be documented", source)


class TestBrmSrm02WarrantyGate(unittest.TestCase):
    def test_order_category_declared(self):
        self.assertIn('("warranty", "Warranty")', ORDER)

    def test_gate_reads_device_warranty_status(self):
        source = ORDER[ORDER.index("def _check_warranty_gate") : ORDER.index("def _flag_rework")]
        self.assertIn("order_category", source)
        self.assertIn("warranty_status", source)

    def test_gate_raises(self):
        source = ORDER[ORDER.index("def _check_warranty_gate") : ORDER.index("def _flag_rework")]
        self.assertIn("raise UserError", source)

    def test_gate_runs_on_create(self):
        create_body = ORDER[ORDER.index("def create") : ORDER.index("def _check_warranty_gate")]
        self.assertIn("_check_warranty_gate()", create_body)


class TestBrmSrm06ReworkFlag(unittest.TestCase):
    def test_30_day_window(self):
        source = ORDER[ORDER.index("def _flag_rework") :]
        self.assertIn("timedelta(days=30)", source)

    def test_links_original(self):
        source = ORDER[ORDER.index("def _flag_rework") :]
        self.assertIn("rework_of_id", source)

    def test_excludes_cancelled(self):
        # A02 ERP audit M01-F21: only a DELIVERED (or closed) repair is an
        # original; cancelled and draft orders are excluded by construction
        source = ORDER[ORDER.index("def _flag_rework") :]
        self.assertIn('("state", "in", ("delivered", "closed"))', source)

    def test_runs_on_create(self):
        create_body = ORDER[ORDER.index("def create") : ORDER.index("def _check_warranty_gate")]
        self.assertIn("_flag_rework()", create_body)


class TestViewSurfacing(unittest.TestCase):
    """The audit's frontend findings: the new fields are surfaced."""

    def test_order_category_on_form(self):
        view = (
            Path(__file__).resolve().parents[1] / "views" / "fix_service_order_views.xml"
        ).read_text(encoding="utf-8")
        self.assertIn('name="order_category"', view)
        self.assertIn('name="is_rework"', view)

    def test_approval_fields_on_estimate_form(self):
        view = (Path(__file__).resolve().parents[1] / "views" / "fix_estimate_views.xml").read_text(
            encoding="utf-8"
        )
        self.assertIn('name="customer_approval_ref"', view)
        self.assertIn('name="manager_approval_uid"', view)

    def test_mdm_rules_surfaced(self):
        mdm = next(
            p
            for p in (Path(__file__).resolve().parents[5] / "addons").rglob("cd_mdm_core")
            if (p / "__manifest__.py").is_file()
        )
        view = (mdm / "views" / "fix_mdm_views.xml").read_text(encoding="utf-8")
        self.assertIn("action_fix_mdm_match_rule", view)
        self.assertIn("action_fix_mdm_golden_rule", view)

    def test_party_hierarchy_surfaced(self):
        party = next(
            p
            for p in (Path(__file__).resolve().parents[5] / "addons").rglob("cd_party_master")
            if (p / "__manifest__.py").is_file()
        )
        view = (party / "views" / "fix_party_workspace_views.xml").read_text(encoding="utf-8")
        self.assertIn("action_fix_party_hierarchy", view)


if __name__ == "__main__":
    unittest.main()
