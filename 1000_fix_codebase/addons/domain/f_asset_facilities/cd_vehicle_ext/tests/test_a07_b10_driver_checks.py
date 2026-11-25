"""A07 decision B10 (8 Nov 2026): who records a van's daily pre-use check.

A PASSED check unblocks the van for dispatch, and any employee could record one
on any van. Now the van's assigned driver records it, holding the Driver role, as
that driver; a Fleet Officer (or the Logistics Manager) records it for any van.
Live ORM (``odoo_env``, rolled back), as NON-ADMIN users; and through the P03
write route the screen uses.
"""

import types

import odoo.addons.cd_p03_portal.controllers.p03_generic_api as api
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

OFFICER = "fleet.fleet_group_user"
LM = "cd_vehicle_ext.group_logistics_manager"
DRIVER = "cd_vehicle_ext.group_fleet_driver"
OK = {"tyres_ok": True, "lights_ok": True, "fluids_ok": True, "brakes_ok": True}


@pytest.fixture
def d(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)

    def user(login, groups=()):
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "group_ids": [
                        (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                    ],
                    "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                    "default_operating_unit_id": ou.id,
                }
            )
        )

    def driver(name, login_user):
        emp = env["hr.employee"].create({"name": name, "user_id": login_user.id})
        return env["fix.driver"].create(
            {"name": name, "employee_id": emp.id, "license_no": "DL-" + name}
        )

    x = types.SimpleNamespace(env=env)
    x.clerk = user("a7b10_clerk")
    x.officer = user("a7b10_officer", [OFFICER])
    x.lm = user("a7b10_lm", [LM])
    x.karim = user("a7b10_karim", [DRIVER])
    x.rahim = user("a7b10_rahim", [DRIVER])
    x.nodriverrole = user("a7b10_norole")
    brand = env["fleet.vehicle.model.brand"].create({"name": "A7B10 Brand"})
    model = env["fleet.vehicle.model"].create(
        {"name": "A7B10 Van", "brand_id": brand.id, "vehicle_type": "car"}
    )
    x.karim_drv = driver("A7B10 Karim", x.karim)
    x.rahim_drv = driver("A7B10 Rahim", x.rahim)
    x.norole_drv = driver("A7B10 NoRole", x.nodriverrole)
    x.van = env["fleet.vehicle"].create(
        {"model_id": model.id, "license_plate": "A7B10-1", "fix_driver_id": x.karim_drv.id}
    )
    x.van2 = env["fleet.vehicle"].create(
        {"model_id": model.id, "license_plate": "A7B10-2", "fix_driver_id": x.norole_drv.id}
    )
    x.unassigned = env["fleet.vehicle"].create({"model_id": model.id, "license_plate": "A7B10-3"})
    return x


def _check(d, user, van, **kw):
    return d.env["fix.vehicle.check"].with_user(user).create({"vehicle_id": van.id, **OK, **kw})


def _refusal(d, fn):
    try:
        with d.env.cr.savepoint():
            fn()
            d.env.flush_all()
    except (UserError, AccessError, ValidationError) as exc:
        return str(exc)
    return None


def test_any_employee_no_longer_passes_any_van(d):
    for who in (d.clerk, d.rahim):
        for van in (d.van, d.unassigned):
            why = _refusal(d, lambda w=who, v=van: _check(d, w, v))
            assert why and "assigned driver or a Fleet Officer" in why, (who.login, why)
    assert not d.env["fix.vehicle.check"].search([("vehicle_id", "in", (d.van | d.unassigned).ids)])


def test_the_assigned_driver_records_his_own_van_as_himself(d):
    chk = _check(d, d.karim, d.van)
    assert chk.passed and chk.driver_id == d.karim_drv
    # not as another driver
    why = _refusal(d, lambda: _check(d, d.karim, d.van, driver_id=d.rahim_drv.id))
    assert why and "as yourself" in why
    # and not another van
    assert _refusal(d, lambda: _check(d, d.karim, d.van2))


def test_assigned_without_the_driver_role_is_told_what_to_ask_for(d):
    why = _refusal(d, lambda: _check(d, d.nodriverrole, d.van2))
    assert why and "Driver role" in why


def test_a_fleet_officer_or_logistics_manager_records_any_van(d):
    for who in (d.officer, d.lm):
        for van in (d.van, d.van2, d.unassigned):
            _check(d, who, van)


def test_a_failed_check_is_bound_by_the_same_rule(d):
    bad = dict(OK, brakes_ok=False)
    assert _refusal(d, lambda: _check(d, d.clerk, d.van, **bad))
    assert not _check(d, d.karim, d.van, **bad).passed


def _screen_write(d, monkeypatch, user, values):
    """The P03 write route the M46 pre-use form posts to, as the user, cold cache."""
    cls = api.P03GenericApiController
    env = d.env(user=user.id, su=False)
    env.invalidate_all()
    monkeypatch.setattr(api, "request", types.SimpleNamespace(env=env))
    fn = cls.model_write
    return getattr(fn, "original_endpoint", fn)(cls(), model="fix.vehicle.check", values=values)


def test_the_screen_route_applies_it(d, monkeypatch):
    out = _screen_write(d, monkeypatch, d.clerk, {"vehicle_id": d.van.id, **OK})
    assert not out.get("id") and "assigned driver" in str(out), out
    out = _screen_write(d, monkeypatch, d.karim, {"vehicle_id": d.van.id, **OK})
    assert out.get("id"), out
