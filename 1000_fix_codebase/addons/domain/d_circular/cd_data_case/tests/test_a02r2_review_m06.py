# ruff: noqa: F811 (the m6 fixture is imported, and named as test parameters)
"""A02 pass 2 independent review (21 Nov 2026) - M06 Data Services.

B3  the two-person custody rule cannot be skipped, nor a witness named, by a
    context key a client sends;
B4  a case-purge certificate cannot pass as a device certificate by context;
B5  the case read log cannot be switched off by context;
P1  the M06 P03 surfaces read as the caller and log the reads; the waiver and
    the credit approval go through M20's own actions as the caller; every
    certificate consumer is bound; a blank media kind is judged by the D16
    matrix as the strictest kind;
P2  an unconfirmed hand-off can be withdrawn; the D17 KPI leaves out cases
    on a retention hold.

Every control runs as non-admin users (the ``m6`` fixture). ``odoo_env``
rolls back.
"""

from datetime import timedelta
from unittest import mock

import pytest
from odoo.addons.cd_data_case.tests.test_a02_p1p2_cd_data_case import (  # noqa: F401
    CASE,
    _FakeRequest,
    m6,
)
from odoo.exceptions import AccessError, UserError

from .test_a02_erp_b1_m06 import _cert, _request

CERT = "fix.data.wipe.certificate"
FORGED = "m06_custody_confirming"


def _forged(m6):
    return {FORGED: True, "m06_custody_witness": m6.tech2.id}


def _user(m6, key, *groups):
    ref = m6.env.ref
    return (
        m6.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A02 RV M06 %s %d" % (key, m6.n),
                "login": "a02.rv.m06.%s.%d@a02.test" % (key, m6.n),
                "group_ids": [(6, 0, [ref("base.group_user").id] + [ref(g).id for g in groups])],
            }
        )
    )


def _sealed(m6, case):
    m6.env["fix.data.media.unit"].with_user(m6.tech).create(
        {"case_id": case.id, "seal_number": "RV-SEAL-%d" % case.id}
    )
    return case


# ===================================================== B3 custody by context
def test_review_b3_a_client_context_does_not_confirm_custody(m6):
    case = _sealed(m6, m6.new_case())
    forged = _forged(m6)
    case.with_user(m6.custodian).with_context(**forged).action_take_custody(m6.tech.login)
    # still a request the named receiver confirms, not custody taken alone
    assert case.state == "new" and case.custody_request_to_id == m6.tech
    assert not case.sudo().custody_event_ids.filtered("witness_id")
    case.with_user(m6.tech).action_confirm_custody()
    assert case.state == "custody"
    taken = case.sudo().custody_event_ids.filtered(lambda e: e.action == "custody_taken")
    assert taken.witness_id == m6.custodian  # the real requester, never the forged one
    # a custody transfer with the same context is still a request
    case.with_user(m6.tech).with_context(**forged).action_log_custody_transfer(m6.custodian.login)
    assert case.custody_request_to_id == m6.custodian
    assert not case.sudo().custody_event_ids.filtered(lambda e: e.action == "custody_transfer")


def test_review_b3_a_client_context_does_not_move_or_return_media(m6):
    case = m6.custody(m6.new_case())
    unit = case.media_unit_ids.with_user(m6.tech)
    unit.with_context(**_forged(m6)).action_transfer("vault", handler=m6.custodian.login)
    assert unit.location == "reception" and unit.pending_location == "vault"
    unit.with_user(m6.custodian).action_confirm_move()
    moved = case.sudo().custody_event_ids.filtered(lambda e: e.action == "media_moved")
    assert (moved.actor_id, moved.witness_id) == (m6.custodian, m6.tech)


def test_review_b3_a_witness_is_never_read_from_the_context(m6):
    case = m6.custody(m6.new_case())
    other = m6.env["res.partner"].create({"name": "RV Right Owner %d" % case.id})
    case.with_user(m6.manager2).with_context(
        m06_custody_witness=m6.tech2.id
    ).action_correct_customer(other.id, "the desk typed the wrong customer")
    event = case.sudo().custody_event_ids.filtered(lambda e: e.action == "customer_corrected")
    assert event and not event.witness_id


# ===================================================== B4 purge cert by context
def test_review_b4_a_purge_certificate_never_passes_as_a_device_certificate(m6):
    case = m6.handed_over(m6.new_case())
    cert = m6.purge_cert(case)
    denial = cert.with_context(m06_case_purge=True)._fix_certify_denial(cert.serial_number)
    assert "data-case purge" in denial
    # the lab's own purge path still accepts it
    case.action_purge(cert)
    assert case.state == "purged"


# ===================================================== B5 read log by context
def test_review_b5_the_read_log_cannot_be_switched_off(m6):
    case = m6.new_case()
    case.with_user(m6.tech).with_context(m06_no_read_log=True).read(["name"])
    logs = m6.env["fix.data.case.read.log"].sudo().search([("case_id", "=", case.id)])
    assert logs.mapped("user_id") == m6.tech


# ===================================================== P1 P03 scoping
def _p03(m6, who, method, **kwargs):
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    with mock.patch.object(api, "request", _FakeRequest(m6.env(user=who.id))):
        return getattr(api.P03GenericApiController(), method)(**kwargs)


def test_review_p1_m06_screens_read_as_the_caller_and_log_it(m6):
    staffed = m6.new_case()
    Log = m6.env["fix.data.case.read.log"].sudo()
    # an operator not named on the case does not list it, nor open it by id
    res = _p03(
        m6,
        m6.tech2,
        "model_records",
        model=CASE,
        cols=["name", "customer_id"],
        domain=[("id", "=", staffed.id)],
    )
    assert "error" in res or not res["rows"], res
    res = _p03(
        m6, m6.tech2, "model_form", model=CASE, fields=[{"name": "name"}], record_id=staffed.id
    )
    assert "error" in res, res
    assert not Log.search([("case_id", "=", staffed.id), ("user_id", "=", m6.tech2.id)])
    # its technician lists it and opens it: both reads land in the log
    res = _p03(
        m6,
        m6.tech,
        "model_records",
        model=CASE,
        cols=["name", "customer_id"],
        domain=[("id", "=", staffed.id)],
    )
    assert [r["id"] for r in res["rows"]] == [staffed.id]
    assert Log.search([("case_id", "=", staffed.id), ("user_id", "=", m6.tech.id)])
    m6.env.cr.execute("DELETE FROM fix_data_case_read_log WHERE case_id = %s", (staffed.id,))
    res = _p03(
        m6, m6.tech, "model_form", model=CASE, fields=[{"name": "name"}], record_id=staffed.id
    )
    assert res["record"]["name"] == staffed.name
    assert Log.search([("case_id", "=", staffed.id), ("user_id", "=", m6.tech.id)])


def test_review_p1_the_sensitive_m06_surfaces_are_caller_scoped():
    from odoo.addons.cd_p03_portal.controllers.a02 import m06 as ctrl

    for model in (
        CASE,
        "fix.data.media.unit",
        "fix.data.recovery.attempt",
        "fix.data.quote",
        "fix.data.custody.event",
        "fix.data.case.read.log",
    ):
        conf = ctrl.SURFACES[model]
        assert conf.get("caller_scoped") or conf.get("rules"), model


# ===================================================== P1 finance through M20
def _billed(m6, issue=False):
    if "fix.data.case.billing" not in m6.env:
        pytest.skip("M20 billing (cd_settlement_ext) is not installed")
    case = m6.recovered(m6.new_case())
    m6.env["fix.data.case.billing"].sudo()._bill_case(
        {"aggregate_id": case.id, "payload": {"case": case.name}}, "recovered"
    )
    invoice = case._data_invoice()
    assert invoice and invoice.state == "draft"
    if issue:
        invoice.action_issue()
        assert invoice.state == "issued"
    return case, invoice


def test_review_p1_a_waiver_leaves_an_issued_invoice_to_an_accounting_administrator(m6):
    admin = _user(m6, "acctadmin", "account.group_account_manager")
    case, invoice = _billed(m6, issue=True)
    case.with_user(m6.manager2).action_waive_charge(note="lab error, goodwill waiver")
    assert case.settlement_exception == "charge_waived"
    # the lab manager is no Accounting Administrator: M20's cancel rule stands
    assert invoice.state == "issued"
    assert admin in invoice.activity_ids.mapped("user_id")


def test_review_p1_a_lab_manager_who_is_an_accounting_administrator_cancels_it(m6):
    case, invoice = _billed(m6, issue=True)
    m6.manager2.sudo().write({"group_ids": [(4, m6.env.ref("account.group_account_manager").id)]})
    case.with_user(m6.manager2).action_waive_charge(note="lab error, goodwill waiver")
    assert invoice.state == "cancelled" and invoice.cancelled_by_id == m6.manager2


def test_review_p1_a_credit_approval_issues_as_the_decider_with_the_issue_checks(m6):
    finance = _user(m6, "credit", "account.group_account_manager")
    case, invoice = _billed(m6)
    Invoice = type(m6.env["fix.ar.invoice"])
    problems = mock.patch.object(Invoice, "_fix_issue_problems", lambda self: ["the buyer's BIN"])
    with problems, pytest.raises(UserError, match="cannot be issued"), m6.env.cr.savepoint():
        case.with_user(finance).action_approve_credit(note="on-account corporate customer")
    m6.env.invalidate_all()
    assert invoice.state == "draft" and not case.settlement_exception
    case.with_user(finance).action_approve_credit(note="on-account corporate customer")
    assert invoice.state == "issued" and invoice.issued_by_id == finance
    # a non-finance user is refused the decision itself
    other, _inv = _billed(m6)
    with pytest.raises(AccessError):
        other.with_user(m6.manager2).action_approve_credit(note="on-account corporate customer")


# ===================================================== P1 consumer binding
def test_review_p1_a_destruction_certificate_is_bound_to_its_case(m6):
    case = m6.handed_over(m6.new_case())
    unit = case.sudo().media_unit_ids.with_user(m6.tech)
    other = m6.new_case(serial="WD-RV-OTH-%d" % m6.n)
    serial = case.media_serial_number
    req = _request(m6, serial)
    req.sudo().write({"source_ref": other.name})
    foreign = _cert(m6, serial, method="physical_destruction", request=req)
    with pytest.raises(UserError, match="no wipe request raised for"):
        unit.action_destroy(foreign)
    assert unit.location != "destroyed"
    own = _request(m6, serial)
    own.sudo().write({"source_ref": case.name})
    unit.action_destroy(_cert(m6, serial, method="physical_destruction", request=own))
    assert unit.location == "destroyed"


# ===================================================== P1 D16 blank media kind
def test_review_p1_a_blank_media_kind_is_judged_as_the_strictest(m6):
    consumer = m6.new_case(serial="WD-RV-MX-%d" % m6.n)
    serial = "SN-RV-MX-%d" % m6.n
    req = _request(m6, serial)
    req.sudo().write(
        {"source_ref": consumer.name, "confidentiality_level": "moderate", "disposition": "resale"}
    )
    clear = _cert(m6, serial, method="nist_800_88", request=req)  # no media kind recorded
    since = clear.verified_at - timedelta(days=1)
    denial = clear._fix_certify_denial(serial, consumer=consumer, since=since)
    assert "sanitisation matrix" in denial and "strictest" in denial
    purge = _cert(m6, "%s-P" % serial, method="nist_800_88_purge")
    assert purge._fix_certify_denial("%s-P" % serial, consumer=consumer, since=since) == ""


# ===================================================== P2 withdraw a hand-off
def test_review_p2_the_requester_withdraws_an_unconfirmed_hand_off(m6):
    case = _sealed(m6, m6.new_case())
    case.with_user(m6.custodian).action_take_custody(m6.tech.login)
    with pytest.raises(AccessError, match="withdraws it"):
        case.with_user(m6.tech).action_withdraw_handoff()
    case.with_user(m6.custodian).action_withdraw_handoff(reason="wrong colleague named")
    assert not case.custody_request_kind and case.state == "new"
    assert not case.sudo().activity_ids.filtered(lambda a: a.user_id == m6.tech)
    with pytest.raises(UserError, match="no custody hand-off"):
        case.with_user(m6.tech).action_confirm_custody()
    assert case.sudo().custody_event_ids.filtered(lambda e: e.action == "custody_withdrawn")
    # a media move likewise
    m6.custody(case, giver=m6.custodian, receiver=m6.tech)
    unit = case.media_unit_ids.with_user(m6.tech)
    unit.action_transfer("vault", handler=m6.custodian.login)
    unit.action_withdraw_move()
    assert not unit.pending_kind and unit.location == "reception"
    with pytest.raises(UserError, match="no move to confirm"):
        unit.with_user(m6.custodian).action_confirm_move()


# ===================================================== P2 D17 KPI
def test_review_p2_the_purge_overdue_kpi_leaves_out_held_cases(m6):
    from odoo.addons.cd_p03_portal.controllers.a02 import m06 as ctrl

    case = m6.handed_over(m6.new_case())
    case._guarded().write({"retention_until": case.handover_at.date() - timedelta(days=2)})
    assert ctrl.kpis(m6.env)["purge_overdue"] >= 1
    with mock.patch.object(type(case), "_retention_held", lambda self: True):
        assert ctrl.kpis(m6.env)["purge_overdue"] == 0
