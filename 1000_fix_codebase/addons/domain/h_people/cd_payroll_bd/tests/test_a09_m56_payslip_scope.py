# M56-F19 (A09 ERP audit 2026-11-23): the generated operating-unit rule on
# fix.payslip filtered a column the calculation never set, so it always passed
# (false assurance; isolation was company-level only, which IS the design).
# The model now carries two explicit rules instead: payroll roles read every
# slip of their companies; any other internal user is restricted to the slips
# whose cost unit is theirs.
from pathlib import Path

SECURITY = Path(__file__).resolve().parents[1] / "security"


def test_the_payslip_scope_is_company_wide_for_payroll_and_cost_unit_for_others(odoo_env):
    rules = odoo_env["ir.rule"].sudo().search([("model_id.model", "=", "fix.payslip")])
    names = rules.mapped("name")
    # the dead generated rule is not deployed
    assert not [n for n in names if n.endswith("allowed operating units (internal users)")], names
    payroll = rules.filtered(lambda r: r.name == "fix.payslip: payroll runs the whole company")
    assert payroll, names
    assert payroll.domain_force.strip() == "[(1, '=', 1)]"
    want = {
        odoo_env.ref("cd_payroll_bd.group_payroll_officer").id,
        odoo_env.ref("cd_payroll_bd.group_payroll_manager").id,
        odoo_env.ref("cd_payroll_bd.group_payroll_release").id,
    }
    assert want <= set(payroll.groups.ids)
    cost = rules.filtered(
        lambda r: r.name == "fix.payslip: other internal users see their cost units"
    )
    assert cost and "cost_operating_unit_id" in cost.domain_force
    assert odoo_env.ref("base.group_user") in cost.groups
    # the generator agrees: its file no longer emits the payslip unit rule
    text = (SECURITY / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    assert "fix.payslip: allowed operating units" not in text
