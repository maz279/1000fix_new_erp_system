# A09 · People & Workforce · second-wave audit fixes (23 Nov 2026), the part
# served by the portal: UI-F12 (the identity read log pack's row cap - it
# stopped at 2000 and titled itself "2000 reads" as though that were the whole
# log; production held 5321) and its access rule (a caller who may not read
# the log gets no row count).
#
# Evidence standard: the workspace paths go through the real /p03 controller
# as freshly created NON-admin users, with the cache cleared and a fresh env.
from __future__ import annotations

import itertools
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.addons.cd_p03_portal.controllers.a09 import m21

_SEQ = itertools.count(1)


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    """Call one /p03 route of the real controller for `env`'s user."""
    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


def _user(env, *groups):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A09 W2 User %d" % n,
                "login": "a09-w2-%d@test.local" % n,
                "tz": "Asia/Dhaka",
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _emp(env, **vals):
    n = next(_SEQ)
    return env["hr.employee"].create({"name": "A09 W2 Employee %d" % n, **vals})


def _log(env, when, purpose):
    """A row of the identity read log (written by the read path only)."""
    return (
        env["fix.hr.identity.access.log"]
        .sudo()
        .create(
            {
                "field_name": "nid_number",
                "employee_name": "A09 W2 log check",
                "user_id": env.uid,
                "purpose": purpose,
                "read_at": when,
            }
        )
    )


# ============================================================ UI-F12
def test_identity_log_pack_says_how_many_reads_it_leaves_out(odoo_env, monkeypatch, call):
    """The pack stopped at its cap and titled itself "<cap> reads" as though
    that were the whole log (production: 2000 of 5321). Past the cap the
    title reads "first N of TOTAL" and a note says how many are left out."""
    env = odoo_env(context=dict(odoo_env.context, tz="Asia/Dhaka"))
    hrm = _user(env, "hr.group_hr_manager")
    monkeypatch.setattr(m21, "IDENTITY_LOG_CAP", 3)
    day = "2001-02-03"  # a day nothing else in the test database was logged
    period = {"date_from": day, "date_to": day}
    before = call(
        env(user=hrm.id), "model_report", module="M21", report="identity_access_log", params=period
    )
    assert not before.get("error"), before
    assert not before["rows"], "the test's own day already carries log rows"
    # five reads that Dhaka day (04:00-08:00 UTC), and one on another day
    for i in range(5):
        _log(env, "2001-02-03 %02d:00:00" % (4 + i), "w2 cap %d" % i)
    _log(env, "2001-02-05 04:00:00", "w2 cap other day")
    env.flush_all()
    env.invalidate_all()

    pack = call(
        env(user=hrm.id), "model_report", module="M21", report="identity_access_log", params=period
    )
    assert not pack.get("error"), pack
    assert len(pack["rows"]) == m21.IDENTITY_LOG_CAP
    assert pack["title"] == "Identity Read Log — first 3 of 5 reads", pack["title"]
    cut = [n for n in pack["notes"] if "not shown" in n]
    assert len(cut) == 1 and "first 3 (newest first) of the 5 reads" in cut[0], pack["notes"]
    assert "the other 2 are not shown" in cut[0]
    # the period's newest reads, and only the period's
    assert [r["read_at"] for r in pack["rows"]] == [
        "2001-02-03 14:00",
        "2001-02-03 13:00",
        "2001-02-03 12:00",
    ]
    assert all(r["purpose"].startswith("w2 cap ") for r in pack["rows"])

    # the reader pages through the log by period: the other day is served
    # whole, titled with its true count and without a cap note
    other = call(
        env(user=hrm.id),
        "model_report",
        module="M21",
        report="identity_access_log",
        params={"date_from": "2001-02-04", "date_to": "2001-02-06"},
    )
    assert not other.get("error"), other
    assert [r["purpose"] for r in other["rows"]] == ["w2 cap other day"]
    assert other["title"] == "Identity Read Log — 1 read", other["title"]
    assert not [n for n in other["notes"] if "not shown" in n]


def test_identity_log_pack_is_still_the_hr_managers(odoo_env, monkeypatch, call):
    """The count is read as the caller too: a user who may not read the log
    gets no row count from the pack."""
    env = odoo_env
    plain = _user(env)
    officer = _user(env, "cd_hr_core.group_hr_officer")
    monkeypatch.setattr(m21, "IDENTITY_LOG_CAP", 3)
    _log(env, "2001-02-03 04:00:00", "w2 refused")
    env.flush_all()
    env.invalidate_all()
    for user in (plain, officer):
        res = call(
            env(user=user.id),
            "model_report",
            module="M21",
            report="identity_access_log",
            params={"date_from": "2001-02-03", "date_to": "2001-02-03"},
        )
        assert res.get("error"), res
