"""cd_demand_plan — capture-model contract tests (CD-M43-01).

Every model the P03 workspace captures into must be reachable (ACL, form
view, window action, menu under the M43 workspace sections) and must carry
the spec's business rules."""
import csv
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
MODELS = MODULE / "models"
SRC = {p.stem: p.read_text(encoding="utf-8") for p in MODELS.glob("*.py")}
ALL_SRC = "\n".join(SRC.values())
VIEWS = "\n".join(p.read_text(encoding="utf-8") for p in (MODULE / "views").glob("*.xml"))

CAPTURE_MODELS = [
    "fix.demand.adjustment", "fix.part.segment", "fix.planning.run",
    "fix.forecast.override", "fix.demand.driver", "fix.forecast.accuracy.review",
    "fix.service.level.target", "fix.lead.time.model", "fix.replenishment.parameter",
    "fix.planned.order", "fix.rebalance.proposal", "fix.network.policy",
    "fix.van.par.recommendation", "fix.planning.simulation",
]


def body(src, start, end=None):
    i = src.index(start)
    j = src.index(end, i + 1) if end else len(src)
    return src[i:j]


class TestCaptureReachability(unittest.TestCase):
    def test_every_capture_model_is_defined(self):
        for m in CAPTURE_MODELS:
            self.assertIn(f'_name = "{m}"', ALL_SRC, m)

    def test_every_capture_model_has_acl(self):
        with (MODULE / "security" / "ir.model.access.csv").open(encoding="utf-8") as fh:
            acl = {row["name"] for row in csv.DictReader(fh)}
        for m in CAPTURE_MODELS + ["fix.lead.time.observation", "fix.demand.plan"]:
            self.assertIn(m, acl, f"{m} has no access rule — the capture form would 403")

    def test_every_capture_model_has_form_action_and_menu(self):
        for m in CAPTURE_MODELS:
            stem = m.replace(".", "_")
            self.assertIn(f'id="view_{stem}_form"', VIEWS, m)
            self.assertIn(f'<field name="res_model">{m}</field>', VIEWS, m)
            self.assertIn(f'id="menu_{stem}"', VIEWS, m)

    def test_menus_sit_under_the_m43_workspace_sections(self):
        parents = set(re.findall(r'parent="([^"]+)"', VIEWS))
        self.assertTrue(parents)
        for p in parents:
            self.assertRegex(p, r"^cd_p03_portal\.menu_p03_ws_demand_plan_s[1-4]$")

    def test_manifest_depends_on_what_it_references(self):
        manifest = (MODULE / "__manifest__.py").read_text(encoding="utf-8")
        for dep in ("cd_inventory", "cd_p03_portal", "cd_event_outbox"):
            self.assertIn(f'"{dep}"', manifest)
        self.assertIn("data/ir_sequence.xml", manifest)


class TestBusinessRules(unittest.TestCase):
    def test_history_adjustment_needs_reason_fr_dpl_003(self):
        b = body(SRC["fix_demand_history"], "def action_apply", "def action_cancel")
        self.assertIn("reason", b)
        self.assertIn('"demand_plan.history.adjusted"', b)

    def test_method_is_computed_not_typed_bru_dpl_04(self):
        self.assertIn('compute="_compute_pattern"', SRC["fix_demand_history"])

    def test_override_keeps_statistical_value_bru_dpl_06(self):
        src = SRC["fix_forecast_management"]
        b = body(src, "def action_apply", "def action_withdraw")
        self.assertIn("rationale", b)
        self.assertIn("override_quantity", b)
        self.assertNotIn("forecast_quantity =", b, "an override must not overwrite the statistical forecast")
        self.assertIn("final_quantity", SRC["fix_demand_plan"])

    def test_accuracy_note_never_edits_the_measure_bru_dpl_16(self):
        b = body(SRC["fix_forecast_management"], "class FixForecastAccuracyReview")
        self.assertNotIn("fix.forecast.accuracy\"", b)
        self.assertIn("method_reselection", b)

    def test_safety_stock_is_computed_bru_dpl_07(self):
        src = SRC["fix_inventory_policy"]
        self.assertRegex(src, r'safety_stock = fields\.Float\([^)]*compute="_compute_parameters"')
        self.assertIn("engine.safety_stock(", src)

    def test_guard_rail_and_versioning_bru_dpl_08_18(self):
        src = SRC["fix_inventory_policy"]
        self.assertIn("engine.requires_planner_review(", body(src, "def action_submit", "def action_approve"))
        pub = body(src, "def action_publish")
        self.assertIn('"superseded"', pub)
        self.assertIn('"demand_plan.parameter.published"', pub)

    def test_inactive_supplier_blocks_release_bru_dpl_11(self):
        b = body(SRC["fix_replenishment"], "def action_release", "def action_mark_converted")
        self.assertIn("suggested_supplier_id.active", b)

    def test_rebalance_requires_net_benefit_bru_dpl_13(self):
        b = body(SRC["fix_replenishment"], "def action_propose", "def action_approve")
        self.assertIn("net_benefit <= 0", b)

    def test_van_par_needs_approval_bru_dpl_12(self):
        b = body(SRC["fix_replenishment"], "class FixVanParRecommendation", "class FixPlanningSimulation")
        self.assertIn('rec.state != "approved"', b)

    def test_simulation_never_writes_elsewhere_bru_dpl_15(self):
        b = body(SRC["fix_replenishment"], "class FixPlanningSimulation")
        self.assertNotIn("publish(", b)
        for other in ("fix.replenishment.parameter", "fix.planned.order"):
            self.assertNotIn(other, b)

    def test_planned_order_lifecycle_matches_spec_8_2(self):
        states = re.findall(r'\("([a-z_]+)", "[^"]+"\)',
                            body(SRC["fix_replenishment"], "PLANNED_ORDER_STATES", "]"))
        self.assertEqual(states, ["projected", "planned", "consolidated", "approved",
                                  "released", "converted", "closed", "cancelled"])


if __name__ == "__main__":
    unittest.main()
