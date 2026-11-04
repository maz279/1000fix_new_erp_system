# The workspace's read routes (/p03/model/records, /form, /report) are
# `readonly=True`: Odoo serves them on a read-only cursor and, when the
# handler writes, retries the request on a read/write cursor - but only if
# psycopg2's ReadOnlySqlTransaction reaches http.py. The routes used to catch
# every exception and answer "could not be loaded", so a read that must write
# (the A09 identity read log, BRU-HCM-07) would have failed on every employee
# form. The error now propagates.
import itertools
from unittest import mock

import psycopg2
import pytest
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

_SEQ = itertools.count(1)
READ_ONLY = psycopg2.errors.ReadOnlySqlTransaction


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def hr_officer_env(odoo_env, monkeypatch):
    install(monkeypatch)
    n = next(_SEQ)
    user = (
        odoo_env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Read Retry HR %d" % n,
                "login": "read.retry.hr.%d@a09.test" % n,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            odoo_env.ref("base.group_user").id,
                            odoo_env.ref("cd_hr_core.group_hr_officer").id,
                        ],
                    )
                ],
            }
        )
    )
    return odoo_env(user=user.id)


def _call(env, route, **kw):
    with mock.patch.object(api, "request", FakeRequest(env)):
        return getattr(api.P03GenericApiController(), route)(**kw)


def test_a_read_that_must_write_reaches_the_read_write_retry(odoo_env, hr_officer_env):
    emp = odoo_env["hr.employee"].create(
        {"name": "Read Retry Employee", "nid_number": "1234567890"}
    )
    Log = type(odoo_env["fix.hr.identity.access.log"])
    refused = READ_ONLY("cannot execute INSERT in a read-only transaction")
    with mock.patch.object(Log, "create", side_effect=refused), pytest.raises(READ_ONLY):
        _call(
            hr_officer_env,
            "model_form",
            model="hr.employee",
            fields=[{"name": "name"}, {"name": "nid_number"}],
            record_id=emp.id,
        )


def test_other_failures_still_answer_with_a_message(odoo_env, hr_officer_env):
    # an NID on file, so the form read reaches the read log
    emp = odoo_env["hr.employee"].create({"name": "Read Retry Other", "nid_number": "9876543210"})
    Log = type(odoo_env["fix.hr.identity.access.log"])
    with mock.patch.object(Log, "create", side_effect=RuntimeError("boom")):
        res = _call(
            hr_officer_env,
            "model_form",
            model="hr.employee",
            fields=[{"name": "name"}, {"name": "nid_number"}],
            record_id=emp.id,
        )
    assert "error" in res
