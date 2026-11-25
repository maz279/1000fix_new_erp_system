# A09 ERP builder stream B2b — statutory figures of the Labour (Amendment)
# Act 2026 (M21-F5 / M55-F2, M21-F6) and their opt-in application to EXISTING
# data.
#
# The 2026 figures (maternity 120 days = 60/60 split, festival holidays 13,
# death-benefit qualifying service 1 year, casual/sick charging the holidays
# inside them per BLR 2015 r.106) reach existing rows ONLY through
# res.company._apply_labour_act_2026_figures() / the gated 19.0.0.7.0
# post-migrate (cd_hr_core.apply_labour_act_2026_figures == 'approved'); a
# value the owner changed is never overwritten, and a second run moves
# nothing. Seeds for fresh installs carry the figures in
# statutory_leave_data.xml (noupdate: never re-applied to an existing DB).
import importlib.util
import itertools
from datetime import timedelta
from pathlib import Path

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import UserError

LEAVE = "fix.leave.request"
PARAM = "cd_hr_core.apply_labour_act_2026_figures"
MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "19.0.0.7.0" / "post-migrate.py"
_SEQ = itertools.count(1)


def _user(env, *groups):
    n = next(_SEQ)
    ids = [env.ref("base.group_user").id] + [env.ref(g).id for g in groups]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "B2b Statutory User %d" % n,
                "login": "a09-b2b-stat-%d@test.local" % n,
                "group_ids": [(6, 0, ids)],
            }
        )
    )


def _contract(env, emp, joined):
    return env["fix.employment.contract"].create(
        {
            "employee_id": emp.id,
            "company_id": env.company.id,
            "contract_type": "permanent",
            "joining_date": joined,
            "basic_monthly": 30000.0,
            "state": "active",
        }
    )


def _unset_param(env):
    env["ir.config_parameter"].sudo().search([("key", "=", PARAM)]).unlink()


def _load_migration():
    spec = importlib.util.spec_from_file_location("b2b_post_migrate_2026", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def x(odoo_env):
    """A female employee with a manager, for the maternity split checks."""
    env = odoo_env
    mgr_u, fem_u = (_user(env) for _ in range(2))
    e_mgr = env["hr.employee"].create({"name": "B2b Stat Manager", "user_id": mgr_u.id})
    e_fem = env["hr.employee"].create(
        {"name": "B2b Stat Mother", "user_id": fem_u.id, "parent_id": e_mgr.id, "sex": "female"}
    )
    _contract(env, e_fem, fields.Date.today() - relativedelta(years=1))
    types = {t.code: t for t in env["fix.leave.type"].search([("company_id", "=", env.company.id)])}
    return type(
        "X",
        (),
        {
            "env": env,
            "mgr_u": mgr_u,
            "fem_u": fem_u,
            "e_fem": e_fem,
            "lt": types,
            "today": fields.Date.today(),
        },
    )()


def _draft(x, code, d_from, d_to, **kw):
    return x.env[LEAVE].create(
        {
            "employee_id": x.e_fem.id,
            "leave_type_id": x.lt[code].id,
            "date_from": d_from,
            "date_to": d_to,
            **kw,
        }
    )


# ---- the gated application of the 2026 figures -------------------------------


def test_apply_2026_figures_moves_untouched_values_and_spares_owner_changes(odoo_env):
    env = odoo_env
    mat = env.ref("cd_hr_core.leave_type_maternity")
    fes = env.ref("cd_hr_core.leave_type_festival")
    cas = env.ref("cd_hr_core.leave_type_casual")
    sic = env.ref("cd_hr_core.leave_type_sick")
    # a company whose owner already ruled its own maternity figure (116)
    other = env["res.company"].create({"name": "B2b Other Co"})
    other_mat = env["fix.leave.type"].create(
        {
            "company_id": other.id,
            "code": "maternity",
            "name": "Owner Maternity",
            "entitlement_days": 116,
            "maternity": True,
        }
    )
    # the untouched pre-Act values everywhere
    mat.write({"entitlement_days": 112})
    fes.write({"entitlement_days": 11})
    cas.write({"excludes_holidays": True})
    sic.write({"excludes_holidays": True})
    env.company.write({"fix_hr_death_benefit_min_service_years": 2.0})
    other.write({"fix_hr_death_benefit_min_service_years": 1.5})  # owner-changed

    result = env["res.company"].sudo()._apply_labour_act_2026_figures()

    assert mat.entitlement_days == 120, "s.46: maternity 112 -> 120"
    assert fes.entitlement_days == 13, "s.118(1): festival 11 -> 13"
    assert not cas.excludes_holidays and not sic.excludes_holidays, "BLR r.106"
    assert env.company.fix_hr_death_benefit_min_service_years == 1.0, "s.19: 2 -> 1 year"
    # owner-changed values are left alone
    assert other_mat.entitlement_days == 116
    assert other.fix_hr_death_benefit_min_service_years == 1.5
    # the counts describe the moves, and the switch turns on with the data
    assert result["maternity_types"] >= 1 and result["festival_types"] >= 1
    assert result["casual_sick_types"] >= 2 and result["death_benefit_companies"] >= 1
    assert (
        env["ir.config_parameter"].sudo().get_param(PARAM) == "approved"
    ), "the floors switch together with the data"


def test_apply_2026_figures_is_idempotent(odoo_env):
    env = odoo_env
    env.ref("cd_hr_core.leave_type_maternity").write({"entitlement_days": 112})
    env.ref("cd_hr_core.leave_type_festival").write({"entitlement_days": 11})
    first = env["res.company"].sudo()._apply_labour_act_2026_figures()
    second = env["res.company"].sudo()._apply_labour_act_2026_figures()
    assert first["maternity_types"] >= 1 and first["festival_types"] >= 1
    assert second["maternity_types"] == 0 and second["festival_types"] == 0
    assert second["casual_sick_types"] == 0 and second["death_benefit_companies"] == 0
    assert env.ref("cd_hr_core.leave_type_maternity").entitlement_days == 120


def test_apply_2026_figures_needs_the_hr_officer_role(odoo_env):
    env = odoo_env
    plain = _user(env)
    with pytest.raises(UserError, match="HR Officer"), env.cr.savepoint():
        env["res.company"].with_user(plain)._apply_labour_act_2026_figures()
    officer = _user(env, "cd_hr_core.group_hr_officer")
    env.ref("cd_hr_core.leave_type_maternity").write({"entitlement_days": 112})
    env["res.company"].with_context(tracking_disable=True).with_user(
        officer
    )._apply_labour_act_2026_figures()
    assert env.ref("cd_hr_core.leave_type_maternity").entitlement_days == 120


def test_post_migrate_does_nothing_until_the_owner_approves(odoo_env):
    env = odoo_env
    migration = _load_migration()
    mat = env.ref("cd_hr_core.leave_type_maternity")
    fes = env.ref("cd_hr_core.leave_type_festival")

    def _to_pre_act():
        mat.write({"entitlement_days": 112})
        fes.write({"entitlement_days": 11})
        env.company.write({"fix_hr_death_benefit_min_service_years": 2.0})

    # parameter absent: nothing changes
    _unset_param(env)
    _to_pre_act()
    migration.migrate(env.cr, "19.0.0.7.0")
    env.invalidate_all()
    assert mat.entitlement_days == 112 and fes.entitlement_days == 11
    assert env.company.fix_hr_death_benefit_min_service_years == 2.0
    assert not env["ir.config_parameter"].sudo().get_param(PARAM)
    # parameter present but not the approval word: still nothing
    env["ir.config_parameter"].sudo().set_param(PARAM, "yes")
    _to_pre_act()
    migration.migrate(env.cr, "19.0.0.7.0")
    env.invalidate_all()
    assert mat.entitlement_days == 112 and fes.entitlement_days == 11
    # approved: the figures move, and a second run is a no-op (idempotent)
    env["ir.config_parameter"].sudo().set_param(PARAM, "approved")
    _to_pre_act()
    migration.migrate(env.cr, "19.0.0.7.0")
    env.invalidate_all()
    assert mat.entitlement_days == 120 and fes.entitlement_days == 13
    assert env.company.fix_hr_death_benefit_min_service_years == 1.0
    # a second run without any reset moves nothing (only pre-Act values move)
    migration.migrate(env.cr, "19.0.0.7.0")
    env.invalidate_all()
    assert mat.entitlement_days == 120 and fes.entitlement_days == 13
    assert env.company.fix_hr_death_benefit_min_service_years == 1.0


# ---- the maternity split: 60/60 under the 2026 Act, 56/56 until approved ------


def _submit_maternity(x, before, after):
    conf = x.today + timedelta(days=200)
    lv = _draft(
        x,
        "maternity",
        conf - timedelta(days=before),
        conf + timedelta(days=after - 1),
        expected_confinement_date=conf,
    )
    lv.action_submit()
    return lv


def test_maternity_split_is_60_60_once_the_2026_figures_are_approved(x):
    # a type ABOVE the statutory 120 proves the cap: without the 2026 switch
    # the split is entitlement//2 (65/65 for a 130-day type); with it, the Act
    # caps each side at 60
    x.lt["maternity"].write({"entitlement_days": 130})
    x.env["ir.config_parameter"].sudo().set_param(PARAM, "approved")
    with pytest.raises(UserError, match="days before"), x.env.cr.savepoint():
        _submit_maternity(x, before=61, after=60)
    with pytest.raises(UserError, match="days after the confinement"), x.env.cr.savepoint():
        _submit_maternity(x, before=60, after=61)
    lv = _submit_maternity(x, before=60, after=60)
    lv.with_user(x.mgr_u).action_inbox_approve()
    assert (lv.state, lv.days) == ("approved", 120), "s.46: 60 days before + 60 after"
    x.env.flush_all()
    x.env["ir.config_parameter"].sudo().set_param(PARAM, False)


def test_maternity_split_keeps_today_behaviour_until_the_owner_approves(x):
    # the switch off: the split is entitlement//2 of the CURRENT type value
    # (112 -> 56/56), exactly today's behaviour
    x.lt["maternity"].write({"entitlement_days": 112})
    _unset_param(x.env)
    with pytest.raises(UserError, match="days before"), x.env.cr.savepoint():
        _submit_maternity(x, before=57, after=56)
    lv = _submit_maternity(x, before=56, after=56)
    lv.with_user(x.mgr_u).action_inbox_approve()
    assert (lv.state, lv.days) == ("approved", 112)
