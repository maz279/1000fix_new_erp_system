"""Owner decisions of 20 Nov 2026 that are code (A02 ERP audit O5, O6, O8).

- O5: the repair technicians (workshop and field) read a captured passcode to
  test the device; a counter clerk still cannot; it is purged at hand-over.
- O6: a repair carries 90 days of warranty on every category.
- O8: a new field route starts at the configured default depot.
``odoo_env`` rolls back after each test.
"""

# ruff: noqa: F811  (the imported fixture is used as a parameter)
import pytest
from odoo.addons.cd_service_order.tests.test_a02_p0_m01 import _user, order, w  # noqa: F401
from odoo.exceptions import AccessError


def test_o5_repair_technicians_read_the_passcode_clerks_do_not(w):
    o = order(w)
    o.with_user(w.clerk).action_record_passcode("4321", "yes")
    bench = _user(w.env, "bench", ["cd_workshop.group_fix_workshop_user"])
    field = _user(w.env, "field", ["cd_field_service.group_fix_field_service_user"])
    assert o.with_user(bench).passcode_value == "4321"
    assert o.with_user(field).passcode_value == "4321"
    with pytest.raises(AccessError):
        o.with_user(w.clerk).read(["passcode_value"])


def test_o6_a_repair_carries_90_days_of_warranty(w):
    assert order(w).service_warranty_days == 90


def test_o8_a_new_route_starts_at_the_default_depot(w):
    if "fix.field.route" not in w.env:
        pytest.skip("cd_field_service not installed")
    params = w.env["ir.config_parameter"].sudo()
    params.set_param("cd_field_service.default_depot", "23.7905,90.3735")
    Route = w.env["fix.field.route"].sudo()
    assert Route._default_depot() == (23.7905, 90.3735)
    params.set_param("cd_field_service.default_depot", "nonsense")
    assert Route._default_depot() == (0.0, 0.0)
    params.set_param("cd_field_service.default_depot", "123,456")  # off the globe
    assert Route._default_depot() == (0.0, 0.0)
