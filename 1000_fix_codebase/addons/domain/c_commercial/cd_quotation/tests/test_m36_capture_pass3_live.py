"""M36 capture audit, third pass (2026-11-19), driven as non-admin role
holders through the workspace endpoints, and the customer page as the public
user:

  p2  bulk estate quotation from an asset upload             FR-QTE-021/022
  p3  comparison with the previous version                   FR-QTE-013
  p5  the customer's approval link and one-screen page       FR-QTE-034, T-05
      expiry reminders and the unviewed follow-up            AUT-QTE-04/05
      renewal quotations drafted at the contract lead time    AUT-QTE-10, BRU-QTE-18
"""

import base64
import types
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_quotation.tests import test_a04_m36_controls as base
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (
    _approved_quote,
    _quote,
    _sent_quote,
    _user,
)
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
c = base.c  # the M36 controls fixture

CSV = (
    "Asset Tag,Description,Site,Department,Cost Centre,Qty,Unit Price\n"
    "AT-001,Server AMC,Motijheel,IT,CC-10,1,12000\n"
    "AT-002,UPS AMC,Motijheel,Admin,CC-20,2,1500\n"
    "AT-003,Printer AMC,Gulshan,Admin,CC-20,1,800\n"
)


@contextmanager
def _refused(env, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        yield


def _ok(res):
    return bool(res) and not res.get("error") and bool(res.get("success") or res.get("id"))


@pytest.fixture
def act(c):
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as generic

    ctl = generic.P03GenericApiController()

    def call(user, route, **kw):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        with mock.patch.object(generic, "request", req):
            fn = getattr(generic.P03GenericApiController, route)
            fn = getattr(fn, "original_endpoint", None) or fn
            return fn(ctl, **kw)

    return call


@pytest.fixture
def x(c):
    c.agent = _user(c.env, "m36p3_agent", ["cd_quotation.group_quotation_user"])
    return c


# =========================================================================== p2 estate
def test_an_estate_quotation_is_priced_per_asset_from_the_upload(x, act):
    c = x
    res = act(
        c.author,
        "model_write",
        model="fix.quotation",
        values={
            "customer_id": c.customer.id,
            "quote_type": "contract",
            "operating_unit_id": c.ou.id,
            "valid_until": str(c.today + timedelta(days=15)),
            "cost_amount": 9000.0,
            "estate_file": base64.b64encode(CSV.encode()).decode(),
            "estate_filename": "estate.csv",
        },
    )
    assert _ok(res), res
    q = c.env["fix.quotation"].browse(res["id"])
    priced = q.line_ids.filtered(lambda ln: not ln.display_type)
    sections = q.line_ids.filtered(lambda ln: ln.display_type == "line_section")
    assert len(priced) == 3 and sorted(sections.mapped("description")) == ["Gulshan", "Motijheel"]
    assert q.value == pytest.approx(12000 + 3000 + 800)
    ups = priced.filtered(lambda ln: ln.asset_ref == "AT-002")
    assert ups.quantity == 2 and ups.cost_centre == "CC-20" and "AT-002" in ups.description
    assert "Motijheel - 2 asset(s), BDT 15000.00" in q.estate_breakdown
    assert "CC-20 - 2 asset(s), BDT 3800.00" in q.estate_breakdown


def test_a_bad_asset_list_is_refused_with_its_rows(x):
    c = x
    bad = "Description,Unit Price\nServer AMC,abc\n"
    with _refused(c.env, match="not a number"):
        _quote(
            c,
            line_ids=False,
            estate_file=base64.b64encode(bad.encode()),
            estate_filename="bad.csv",
        )
    with _refused(c.env, match="Description and Unit Price"):
        _quote(
            c,
            line_ids=False,
            estate_file=base64.b64encode(b"Name,Cost\nx,1\n"),
            estate_filename="bad.csv",
        )


# =========================================================================== p3 compare
def test_the_comparison_names_what_changed(x, act):
    c = x
    q = _sent_quote(c)
    nxt = c.env["fix.quotation"].browse(q.with_user(c.author).action_revise()["res_id"])
    line = nxt.line_ids[:1]
    line.with_user(c.author).write({"unit_price": 13500.0})
    nxt.with_user(c.author).write(
        {
            "line_ids": [
                (0, 0, {"description": "Spare kit", "line_type": "recurring", "unit_price": 500.0})
            ]
        }
    )
    nxt.invalidate_recordset()
    diff = nxt.version_diff
    assert "unit price BDT 15000.00 before, BDT 13500.00 now" in diff
    assert "Added: Spare kit" in diff and "Price before VAT" in diff
    assert not q.version_diff  # version 1 has nothing before it
    res = act(
        c.agent,
        "model_action",
        model="fix.quotation",
        ids=[nxt.id],
        method="action_record_version_comparison",
        kwargs={},
    )
    assert _ok(res), res
    assert any("Compared with v1" in (m.body or "") for m in nxt.message_ids)
    with _refused(c.env, match="no previous version"):
        q.with_user(c.agent).action_record_version_comparison()


# =========================================================================== p5 approval link
class _Req:
    """Enough of werkzeug's request for the public controller, as the public user."""

    def __init__(self, env, path):
        self.env = env
        self.httprequest = types.SimpleNamespace(path=path)

    def make_response(self, html, headers=None, status=200):
        return types.SimpleNamespace(html=html, status=status, headers=dict(headers or []))

    def csrf_token(self):
        return "csrf"

    def not_found(self):
        return LookupError("404")


def _page(c, method, token, **kw):
    from odoo.addons.cd_quotation.controllers import customer_view

    public = c.env(user=c.env.ref("base.public_user").id)
    with mock.patch.object(customer_view, "request", _Req(public, "/quote/view/%s" % token)):
        ctl = customer_view.QuotationCustomerView()
        fn = getattr(customer_view.QuotationCustomerView, method)
        fn = getattr(fn, "original_endpoint", None) or fn
        return fn(ctl, token, **kw)


def test_the_customer_approves_on_the_link_with_the_code_on_their_phone(x, act, monkeypatch):
    c = x
    codes = []
    monkeypatch.setattr(
        fix_otp_util, "dispatch_otp", lambda phone, code, ttl, language="bn": codes.append(code)
    )
    q = _sent_quote(c, cost_amount=9876.0)
    draft = _approved_quote(c)
    with _refused(c.env, match="Issue the quotation"):
        draft.with_user(c.agent).action_send_approval_link(channel="whatsapp")
    with _refused(c.env, match="channel"):
        q.with_user(c.agent).action_send_approval_link(channel="counter")
    res = act(
        c.agent,
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_send_approval_link",
        kwargs={"channel": "whatsapp"},
    )
    assert _ok(res), res
    token = q.sudo().access_token
    assert token and res["result"]["link"].endswith("/quote/view/%s" % token)
    link = q.delivery_ids.filtered(lambda d: (d.delivery_ref or "").endswith(token))
    assert link.channel == "whatsapp" and link.recipient == "01711000361"
    # a guessed or malformed token is a 404, not a page
    for bad in ("x" * 32, "../../etc", ""):
        with pytest.raises(LookupError):
            _page(c, "view", bad)
    # the format is checked before any lookup: a token never reaches the
    # search as a pattern or a too-short guess
    from odoo.addons.cd_quotation.models import fix_quote_capture3

    Quote = c.env["fix.quotation"]
    with mock.patch.object(type(Quote), "search", side_effect=AssertionError("searched")):
        for bad in ("short", "a b c d e f g h i j k l m n o p", "%" * 30, "x" * 65):
            assert not Quote._from_token(bad)
    assert fix_quote_capture3.APPROVAL_PATH == "/quote/view/%s"
    page = _page(c, "view", token)
    assert page.status == 200 and q.name in page.html
    # BRU-QTE-13: never cost or margin on a customer surface
    body = page.html.split("</style>", 1)[1]
    assert "9876" not in body and "9,876" not in body
    assert "margin" not in body.lower() and "cost" not in body.lower()
    assert page.headers["Cache-Control"] == "no-store"
    link.invalidate_recordset()
    assert link.view_count == 1 and link.first_viewed_at
    # approval is the customer's code, never a bare tap
    page = _page(c, "accept", token, code="")
    assert page.status == 400 and q.state == "sent"
    page = _page(c, "send_code", token)
    assert page.status == 200 and codes
    wrong = "000000" if codes[-1] != "000000" else "111111"
    page = _page(c, "accept", token, code=wrong)
    assert page.status == 400 and q.state == "sent"
    page = _page(c, "accept", token, code=codes[-1])
    q.invalidate_recordset()
    assert page.status == 200, page.html.split('role="alert">')[-1][:300]
    assert page.status == 200 and q.state == "accepted" and q.acceptance_method == "otp"
    assert "<form" not in page.html  # nothing left to do on the page
    page = _page(c, "accept", token, code=codes[-1])
    assert page.status == 409
    # a new link replaces the old one
    q2 = _sent_quote(c)
    q2.with_user(c.agent).action_send_approval_link(channel="sms")
    old = q2.sudo().access_token
    q2.with_user(c.agent).action_send_approval_link(channel="email")
    with pytest.raises(LookupError):
        _page(c, "view", old)


# =========================================================================== automations
def test_expiry_reminders_are_sent_once_and_stop_on_a_decision(x):
    c = x
    q = _sent_quote(c, valid_until=c.today + timedelta(days=2))
    q.sudo().delivery_ids.unlink()
    c.env["fix.quotation.delivery"].sudo().create({"quotation_id": q.id, "channel": "whatsapp"})
    Quote = c.env["fix.quotation"]
    Quote.cron_quotation_followups()
    reminders = q.delivery_ids.filtered(lambda d: "reminder" in (d.note or "").lower())
    assert len(reminders) == 1 and reminders.channel == "whatsapp" and q.reminders_sent == "2"
    Quote.cron_quotation_followups()
    assert len(q.delivery_ids.filtered(lambda d: "reminder" in (d.note or "").lower())) == 1
    decided = _sent_quote(c, valid_until=c.today + timedelta(days=1))
    decided.with_user(c.author).action_decline(code="price", reason="too dear")
    Quote.cron_quotation_followups()
    assert not decided.delivery_ids.filtered(lambda d: "reminder" in (d.note or "").lower())


def test_an_unviewed_quotation_gets_one_follow_up(x):
    c = x
    q = _sent_quote(c)
    q.sudo()._guarded().write({"sent_at": fields.Datetime.now() - timedelta(hours=25)})
    Quote = c.env["fix.quotation"]
    Quote.cron_quotation_followups()
    acts = q.activity_ids.filtered(lambda a: "not viewed" in (a.summary or ""))
    assert len(acts) == 1 and acts.user_id == q.create_uid and q.unviewed_followup_at
    Quote.cron_quotation_followups()
    assert len(q.activity_ids.filtered(lambda a: "not viewed" in (a.summary or ""))) == 1
    seen = _sent_quote(c)
    seen.sudo()._guarded().write({"sent_at": fields.Datetime.now() - timedelta(hours=25)})
    c.env["fix.quotation.delivery"].sudo().create(
        {
            "quotation_id": seen.id,
            "channel": "sms",
            "first_viewed_at": fields.Datetime.now(),
            "view_count": 1,
        }
    )
    Quote.cron_quotation_followups()
    assert not seen.activity_ids.filtered(lambda a: "not viewed" in (a.summary or ""))


def test_a_renewal_quotation_is_drafted_inside_the_lead_time_once(x):
    c = x
    owner = c.author
    contract = (
        c.env["fix.contract"]
        .with_user(owner)
        .sudo()
        .create(
            {
                "name": "M36P3 AMC",
                "family": "amc",
                "customer_id": c.customer.id,
                "operating_unit_id": c.ou.id,
                "date_start": c.today - timedelta(days=300),
                "date_end": c.today + timedelta(days=64),
                "annual_value": 100000.0,
                "escalation_pct": 10.0,
                "renewal_lead_days": 90,
            }
        )
    )
    contract._guarded().write({"state": "active"})
    far = (
        c.env["fix.contract"]
        .sudo()
        .create(
            {
                "name": "M36P3 far",
                "family": "amc",
                "customer_id": c.customer.id,
                "operating_unit_id": c.ou.id,
                "date_start": c.today,
                "date_end": c.today + timedelta(days=365),
                "annual_value": 1.0,
            }
        )
    )
    far._guarded().write({"state": "active"})
    Quote = c.env["fix.quotation"]
    Quote.cron_renewal_quotations()
    q = Quote.sudo().search([("renewal_of_contract_id", "=", contract.id)])
    assert len(q) == 1 and q.state == "draft" and q.create_uid == owner
    assert q.value == pytest.approx(round(100000.0 * 1.1 * q.contract_months / 12.0, 2))
    assert q.activity_ids.filtered(lambda a: "Renewal quotation drafted" in (a.summary or ""))
    assert not Quote.sudo().search([("renewal_of_contract_id", "=", far.id)])
    Quote.cron_renewal_quotations()
    assert Quote.sudo().search_count([("renewal_of_contract_id", "=", contract.id)]) == 1
