"""cd_fpa tests - P09-M07 (CD-M54-01).

The former source-grep checks (inspect.getsource ... assertIn) are replaced by
checks on the registry and the ORM: the A08 audit found that a stored, typeable
"Actual" passed them while the figure was decorative (M54-7)."""

import odoo.fields as f
from odoo.addons.cd_fpa.models.fix_fpa import FixBudget


def test_budget_actual_is_computed_from_the_ledger(odoo_env):
    field = odoo_env["fix.budget"]._fields["actual_amount"]
    assert field.compute and not field.store
    assert odoo_env["fix.budget"]._fields["variance"].compute


def test_budget_no_m49_relation():
    assert not isinstance(getattr(FixBudget, "actual_amount", None), f.Many2one)


def test_allocation_total_is_direct_plus_allocated(odoo_env):
    rec = (
        odoo_env["fix.cost.allocation"]
        ._guarded()
        .create({"name": "t", "direct_cost": 1000.0, "allocated_overhead": 250.0})
    )
    assert rec.total_cost == 1250.0
