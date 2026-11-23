# ruff: noqa: F811
# A09 ERP audit M59-F11 (2026-11-23): the fitness-for-work status that M59
# Occupational Health publishes was read by nobody outside cd_hse — not by the
# dispatch that sends the technician to a customer's home. cd_field_service
# reads it now: a current "Unfit" status refuses the dispatch and the start of
# the work; Fit-with-restrictions and a lapsed status do not block the call.
#
# The same in-process /p03 paths as the rest of the suite, as non-admin users.
from datetime import timedelta

import pytest
from odoo import fields
from odoo.addons.cd_field_service.tests.test_a02_p0_m02 import p03, w  # noqa: F401
from odoo.exceptions import UserError


def _publish(env, employee, status, restriction=None, valid_from=None, valid_until=None):
    return (
        env["fix.hse.fitness.status"]
        .sudo()
        ._fix_publish(
            employee,
            status,
            restriction,
            valid_from or fields.Date.today(),
            valid_until,
        )
    )


def _dispatch(w, monkeypatch, rec, employee):
    mw, _ma = p03(w, w.ud, monkeypatch)
    res = mw(
        model="fix.dispatch.decision",
        record_id=False,
        values={"field_order_id": rec.id, "technician_id": employee.id},
    )
    w.env.invalidate_all()
    return res


def test_an_unfit_technician_is_not_dispatched(w, monkeypatch):
    if "fix.hse.fitness.status" not in w.env:
        pytest.skip("cd_hse is not installed")
    _publish(w.env, w.ea, "unfit")
    rec = w.fo("pending_dispatch")
    res = _dispatch(w, monkeypatch, rec, w.ea)
    assert not res.get("id") and rec.state == "pending_dispatch" and not rec.technician_id
    assert "unfit" in (res.get("error") or ""), res
    # the other technician is still dispatched normally
    res = _dispatch(w, monkeypatch, rec, w.eb)
    assert res.get("id") and rec.technician_id == w.eb, res


def test_fit_with_restrictions_does_not_block_the_call(w, monkeypatch):
    if "fix.hse.fitness.status" not in w.env:
        pytest.skip("cd_hse is not installed")
    _publish(w.env, w.ea, "restricted", "No lifting over 10 kg")
    rec = w.fo("pending_dispatch")
    res = _dispatch(w, monkeypatch, rec, w.ea)
    assert res.get("id") and rec.technician_id == w.ea, res


def test_a_lapsed_unfit_status_never_blocks(w, monkeypatch):
    if "fix.hse.fitness.status" not in w.env:
        pytest.skip("cd_hse is not installed")
    today = fields.Date.today()
    _publish(
        w.env,
        w.ea,
        "unfit",
        valid_from=today - timedelta(days=30),
        valid_until=today - timedelta(days=1),
    )
    rec = w.fo("pending_dispatch")
    res = _dispatch(w, monkeypatch, rec, w.ea)
    assert res.get("id") and rec.technician_id == w.ea, res


def test_work_does_not_start_for_a_technician_now_unfit(w):
    if "fix.hse.fitness.status" not in w.env:
        pytest.skip("cd_hse is not installed")
    rec = w.fo("arrived", w.ea)
    _publish(w.env, w.ea, "unfit")
    with pytest.raises(UserError) as exc:
        rec.with_user(w.ua).action_start_work()
    assert "unfit" in str(exc.value)
    w.env.invalidate_all()
    assert rec.state == "arrived"
