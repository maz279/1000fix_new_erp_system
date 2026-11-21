# A04 ERP integration (21 Nov 2026): the monthly AR ageing cron
# (cd_billing_engine.ir_cron_ar_aging_snapshot, live on fix_real and fix_dev)
# called fix.ar.aging.snapshot._cron_monthly_snapshot(), which did not exist:
# every run failed and no month-end ageing evidence was ever kept.
from datetime import timedelta

from odoo import fields


def test_the_month_end_ageing_cron_resolves_and_captures_once(odoo_env):
    env = odoo_env
    cron = env.ref("cd_billing_engine.ir_cron_ar_aging_snapshot")
    assert cron.active and "_cron_monthly_snapshot" in cron.code
    Snap = env["fix.ar.aging.snapshot"]
    today = fields.Date.context_today(Snap.with_context(tz="Asia/Dhaka"))
    month_end = today.replace(day=1) - timedelta(days=1)
    made = Snap._cron_monthly_snapshot()
    assert made and set(made.mapped("as_of_date")) == {month_end}
    assert set(made.mapped("state")) == {"captured"}
    mine = made.filtered(lambda s: s.company_id == env.company)
    assert len(mine) == 1
    # a second run in the same month captures nothing twice
    assert not Snap._cron_monthly_snapshot()


def test_the_cron_runs_through_its_server_action(odoo_env):
    """What the scheduler actually executes: the cron's own code."""
    cron = odoo_env.ref("cd_billing_engine.ir_cron_ar_aging_snapshot")
    cron.ir_actions_server_id.sudo().run()  # raised AttributeError before the fix
