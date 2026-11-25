# A10 remediation (2026-11-05), P1-2: the GRC clocks (M60-10).
#
# The audit found licences, obligations and DSRs had NO clock: a trade
# licence five years past its validity stayed 'valid' forever, an obligation
# never came due, and a DSR's statutory deadline was a typed field. Expiry
# and review are now computed daily and announced on the outbox; the DSR
# deadline derives from the request date.
import datetime
import json
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import UserError

GUARD = "changes only through its workflow"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def c(odoo_env):
    saved = getattr(g, "request", None)
    yield types.SimpleNamespace(env=odoo_env)
    g.request = saved


def test_licence_clock_computes_expiry(c):
    Licence = c.env["fix.grc.licence"]
    today = fields.Date.today()
    gone = Licence.create(
        {
            "name": "Gone trade licence",
            "licence_type": "trade",
            "valid_to": today - datetime.timedelta(days=5),
        }
    )
    soon = Licence.create(
        {
            "name": "Soon fire licence",
            "licence_type": "fire",
            "valid_to": today + datetime.timedelta(days=20),
        }
    )
    far = Licence.create(
        {"name": "Far BIN", "licence_type": "bin", "valid_to": today + datetime.timedelta(days=200)}
    )
    held = Licence.create(
        {
            "name": "Suspended past validity",
            "licence_type": "trade",
            "valid_to": today - datetime.timedelta(days=40),
            "state": "suspended",
        }
    )
    assert Licence.cron_licence_expiry() == 2  # gone + soon moved
    assert gone.state == "expired"
    assert soon.state == "expiring"
    assert far.state == "valid"
    assert held.state == "suspended"  # a human decision the clock leaves alone
    (expired_payload,) = _events(c.env, "grc.licence.expired", gone.id)
    assert expired_payload["licence"] == "Gone trade licence"
    assert expired_payload["valid_to"] == str(today - datetime.timedelta(days=5))
    assert _events(c.env, "grc.licence.expiring", soon.id)
    assert not _events(c.env, "grc.licence.expired", far.id)
    # the clock is idempotent: a second sweep the same day moves nothing
    assert Licence.cron_licence_expiry() == 0
    # expiry is never typed: the state stays workflow-locked for a human
    clerk = (
        c.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 P12 Clerk",
                "login": "a10p12.clerk@a10.test",
                "group_ids": [(6, 0, [c.env.ref("base.group_user").id])],
            }
        )
    )
    with pytest.raises(UserError, match=GUARD):
        far.with_user(clerk).write({"state": "expired"})


def test_obligation_clock_nags_until_reviewed(c):
    Obligation = c.env["fix.compliance.obligation"]
    fw = c.env["fix.compliance.framework"].create({"name": "ISO 9001 (clock)", "code": "iso_9001"})
    ob = Obligation.create(
        {
            "framework_id": fw.id,
            "name": "Internal audit programme",
            "clause_reference": "9.2",
            "next_review_date": fields.Date.today() - datetime.timedelta(days=1),
        }
    )
    assert Obligation.cron_obligation_review() == 1
    (payload,) = _events(c.env, "grc.obligation.due", ob.id)
    assert payload == {
        "obligation": "Internal audit programme",
        "clause": "9.2",
        "framework": "ISO 9001 (clock)",
        "due": str(fields.Date.today() - datetime.timedelta(days=1)),
    }
    assert ob.last_review_reminder_on == fields.Date.today()
    # at most once a day
    assert Obligation.cron_obligation_review() == 0
    # the review itself moves the clock forward and the nag stops
    ob.next_review_date = fields.Date.today() + datetime.timedelta(days=90)
    assert Obligation.cron_obligation_review() == 0


def test_dsr_deadline_is_derived_from_the_request_date(c):
    Pdpa = c.env["fix.grc.pdpa"]
    dsr = Pdpa.create({"request_type": "access", "subject_name": "Subject A"})
    assert dsr.due_on == dsr.received_on + datetime.timedelta(days=30)
    # the deadline follows the request date, not the calendar of the handler
    dsr.received_on = fields.Date.today() - datetime.timedelta(days=40)
    assert dsr.due_on == fields.Date.today() - datetime.timedelta(days=10)
    # and it is not typed through the workspace endpoint
    g.request = types.SimpleNamespace(env=c.env(user=dsr.create_uid.id))
    out = _MW(
        g.P03GenericApiController(),
        model="fix.grc.pdpa",
        record_id=dsr.id,
        values={"due_on": str(fields.Date.today() + datetime.timedelta(days=300))},
    )
    assert "error" in out
