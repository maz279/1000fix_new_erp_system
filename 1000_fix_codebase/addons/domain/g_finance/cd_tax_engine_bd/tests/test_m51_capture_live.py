# cd_tax_engine_bd: M51 capture audit (2026-11-17), the new records on a real
# database. Every decision runs as a NON-ADMIN user holding the real finance
# role (the users of test_a08_m51_controls' fixture): acct/acct2 are
# Accountants, mgr/mgr2 Accounting Administrators, filer the Tax Return
# Filing Approver (the CFO appointment). Arrangement that is not under test
# is done as superuser and says so. Everything rolls back (odoo_env).
from __future__ import annotations

import base64
from datetime import timedelta

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from . import test_a08_m51_controls as _base

# the shared fixture and helpers of the M51 control tests
c = _base.c
p03 = _base.p03
_SEQ = _base._SEQ
_filed_return = _base._filed_return

pytestmark = [pytest.mark.tax, pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
FILE = base64.b64encode(b"%PDF-1.4 evidence").decode()
MKT = "fix.marketplace.tax.model"
AMD = "fix.vat.return.amendment"
NOTICE = "fix.tax.notice"


# ------------------------------------------------------------- marketplace model
def _proposal(c, user=None, **kw):
    vals = {
        "company_id": c.co.id,
        "model": "agent",
        "rate": 15.0,
        "external_opinion_ref": "OPINION-D03-%s" % next(_SEQ),
        "opinion_file": FILE,
        "opinion_filename": "d03.pdf",
        "date_from": c.today - timedelta(days=10),
    }
    vals.update(kw)
    return c.as_(user or c.mgr)[MKT].create(vals)


def test_marketplace_vat_is_refused_until_a_model_is_declared(c):
    """BRU-TAX-17: absent, never defaulted."""
    with pytest.raises(UserError, match="BRU-TAX-17"):
        c.cenv[MKT].get_declared(c.co)
    with pytest.raises(UserError, match="D-03"):
        c.cenv[MKT].determine(1000.0, 150.0, company=c.co)
    # a proposal is not in force either
    _proposal(c)
    with pytest.raises(UserError, match="BRU-TAX-17"):
        c.cenv[MKT].get_declared(c.co)


def test_marketplace_model_is_declared_by_opinion_and_cfo_and_then_frozen(c):
    with pytest.raises(AccessError):
        _proposal(c, user=c.acct)  # an accountant does not declare the position
    row = _proposal(c)
    assert row.state == "proposed" and row.basis_of_charge == "commission"
    with pytest.raises(UserError):
        row.with_user(c.filer).action_activate()  # not before the opinion is recorded
    row.with_user(c.mgr).action_record_adviser_verification(reference="Opinion letter 7/2026")
    with pytest.raises(UserError):
        row.with_user(c.mgr).action_activate()  # an administrator is not the CFO
    row.with_user(c.filer).action_activate()
    assert row.state == "active" and row.signoff_state == "signed"
    assert row.cfo_signed_by_id == c.filer
    got = c.cenv[MKT].determine(1000.0, 150.0, company=c.co)
    assert (got["model"], got["base"], got["vat"]) == ("agent", 150.0, 22.5)
    with pytest.raises(UserError, match="BRU-TAX-23"):
        row.with_user(c.mgr).write({"model": "principal"})


def test_the_cfo_who_proposed_or_confirmed_does_not_activate(c):
    c.filer.sudo().write({"group_ids": [(4, c.env.ref(_base.MGR).id)]})
    row = _proposal(c, user=c.filer)
    row.with_user(c.mgr).action_record_adviser_verification(reference="Opinion 1")
    with pytest.raises(UserError, match="Segregation"):
        row.with_user(c.filer).action_activate()


def test_marketplace_activation_needs_the_opinion_file(c):
    row = _proposal(c, opinion_file=False, opinion_filename=False)
    row.with_user(c.mgr).action_record_adviser_verification(reference="Opinion 2")
    with pytest.raises(UserError, match="opinion"):
        row.with_user(c.filer).action_activate()


def test_the_declared_model_cannot_vary(c):
    """BRU-TAX-16: two positions in force for one company never coexist."""
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _proposal(c, rate=0.0)
    first = (
        c.cenv[MKT]
        .sudo()
        .create(  # arrangement: a position in force
            {
                "company_id": c.co.id,
                "model": "principal",
                "rate": 15.0,
                "external_opinion_ref": "OP-A",
                "date_from": c.today - timedelta(days=30),
            }
        )
    )
    with pytest.raises(ValidationError, match="BRU-TAX-16"), c.env.cr.savepoint():
        c.cenv[MKT].sudo().create(
            {
                "company_id": c.co.id,
                "model": "agent",
                "rate": 15.0,
                "external_opinion_ref": "OP-B",
                "date_from": c.today - timedelta(days=5),
            }
        )
    # a change is a new proposal whose activation closes the old window
    new = _proposal(c, date_from=c.today)
    new.with_user(c.mgr).action_record_adviser_verification(reference="Opinion 3")
    new.with_user(c.filer).action_activate()
    assert first.date_to == c.today - timedelta(days=1)
    assert c.cenv[MKT].get_declared(c.co) == new


# ---------------------------------------------------------------- 9.1 amendment
def _amendment(c, ret, user=None, **kw):
    vals = {
        "return_id": ret.id,
        "reason_type": "self_identified",
        "reason": "A Mushak 6.3 of the period was left out of the register",
        "amended_output_vat": 1800.0,
        "amended_input_vat": 900.0,
    }
    vals.update(kw)
    return c.as_(user or c.acct)[AMD].create(vals)


def _vat_challan(c, amount):
    """Arrangement (superuser): the challan that paid the additional VAT."""
    return (
        c.cenv["fix.tax.challan"]
        .sudo()
        .create(
            {
                "company_id": c.co.id,
                "challan_no": "AMD-CH-%s" % next(_SEQ),
                "challan_date": c.today,
                "tax_kind": "vat",
                "payment_mode": c.cenv["fix.tax.challan"]._fields["payment_mode"].selection[0][0],
                "amount": amount,
            }
        )
    )


def test_a_draft_return_is_not_amended(c):
    draft = _base._vat_return(c)
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _amendment(c, draft)


def test_a_filed_return_is_amended_with_evidence_cfo_approval_and_filing(c):
    ret = _filed_return(c)
    net_before = ret.net_payable
    amd = _amendment(c, ret)
    assert amd.name.startswith("VRA/")
    with pytest.raises(UserError, match="working papers"):
        amd.with_user(c.acct).action_submit()
    amd.with_user(c.acct).write({"evidence_file": FILE, "evidence_filename": "wp.xlsx"})
    amd.with_user(c.acct).action_submit()
    assert amd.state == "submitted" and amd.prepared_by_id == c.acct
    assert amd.previous_net == net_before
    assert amd.difference == round(900.0 - net_before, 2)
    with pytest.raises(UserError):
        amd.with_user(c.acct).write({"amended_output_vat": 99.0})  # frozen once submitted
    with pytest.raises(UserError):
        amd.with_user(c.mgr).action_approve()  # an administrator is not the CFO
    amd.with_user(c.filer).action_approve()
    assert amd.state == "approved" and amd.approved_by_id == c.filer
    with pytest.raises(UserError, match="acknowledgement"):
        amd.with_user(c.filer).action_mark_filed(reference="IVAS-AMD-1")
    amd.with_user(c.filer).write({"ack_file": FILE, "ack_filename": "ack.pdf"})
    if amd.difference > 0:
        with pytest.raises(UserError, match="challan"):
            amd.with_user(c.filer).action_mark_filed(reference="IVAS-AMD-1")
        amd.with_user(c.filer).write({"challan_id": _vat_challan(c, amd.difference).id})
    amd.with_user(c.filer).action_mark_filed(reference="IVAS-AMD-1")
    assert amd.state == "filed" and amd.nbr_acknowledgement == "IVAS-AMD-1"
    # the filed return itself is untouched (BRU-TAX-15)
    ret.invalidate_recordset()
    assert ret.state == "filed" and ret.net_payable == net_before
    assert ret.nbr_confirmation == "ACK-STUB-1"
    assert ret.amendment_count == 1 and ret.amended_net_payable == 900.0
    # a second amendment starts from the net as last amended
    second = _amendment(c, ret, amended_output_vat=1700.0, evidence_file=FILE)
    second.with_user(c.acct).action_submit()
    assert second.previous_net == 900.0 and second.difference == -100.0


def test_the_preparer_of_an_amendment_does_not_approve_it(c):
    ret = _filed_return(c)
    amd = _amendment(c, ret, user=c.filer, evidence_file=FILE)
    amd.with_user(c.filer).action_submit()
    with pytest.raises(UserError, match="Segregation"):
        amd.with_user(c.filer).action_approve()
    with pytest.raises(UserError, match="why"):
        amd.with_user(c.filer).action_reject(reason="")


def test_amendment_state_and_stamps_are_never_typed(c):
    ret = _filed_return(c)
    amd = _amendment(c, ret, evidence_file=FILE)
    for vals in ({"state": "filed"}, {"approved_by_id": c.filer.id}, {"difference": 1.0}):
        with pytest.raises(UserError):
            amd.with_user(c.acct).write(vals)
    amd.with_user(c.acct).action_submit()
    other = _amendment(c, ret, user=c.acct2, evidence_file=FILE)
    with pytest.raises(UserError, match="in progress"):
        other.with_user(c.acct2).action_submit()


def test_an_nbr_reason_names_its_notice(c):
    ret = _filed_return(c)
    amd = _amendment(c, ret, reason_type="nbr_query", evidence_file=FILE)
    with pytest.raises(UserError, match="notice"):
        amd.with_user(c.acct).action_submit()
    amd.with_user(c.acct).write({"notice_id": _notice(c).id})
    amd.with_user(c.acct).action_submit()
    assert amd.state == "submitted"


# -------------------------------------------------------------------- NBR notices
def _notice(c, user=None, **kw):
    vals = {
        "company_id": c.co.id,
        "notice_type": "query",
        "tax_kind": "vat",
        "authority": "VAT Circle Gulshan",
        "notice_ref": "NBR/Q/%s" % next(_SEQ),
        "received_on": c.today,
        "period_from": c.today.replace(day=1),
        "period_to": c.today,
        "subject": "Explain the input credit claimed in the period",
        "response_due": c.today + timedelta(days=15),
    }
    vals.update(kw)
    return c.as_(user or c.acct)[NOTICE].create(vals)


def test_a_notice_opens_a_response_task_and_checks_its_dates(c):
    n = _notice(c)
    assert n.name.startswith("TXN/") and n.owner_id == c.acct and n.state == "open"
    todo = n.activity_ids.filtered(lambda a: a.user_id == c.acct)
    assert todo and todo[0].date_deadline == n.response_due
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _notice(c, response_due=c.today - timedelta(days=1))
    with pytest.raises(ValidationError), c.env.cr.savepoint():
        _notice(c, period_from=c.today, period_to=c.today - timedelta(days=3))
    with pytest.raises(AccessError):
        _notice(c, user=c.plain)


def test_notice_generates_its_audit_pack_once(c):
    n = _notice(c)
    n.with_user(c.acct).action_generate_pack()
    pack = n.audit_pack_id
    assert pack and pack.state == "generated"
    assert (pack.date_from, pack.date_to) == (n.period_from, n.period_to)
    with pytest.raises(UserError, match="already"):
        n.with_user(c.acct).action_generate_pack()


def test_notice_response_then_closure_by_a_second_person(c):
    n = _notice(c, user=c.mgr)
    with pytest.raises(UserError, match="response"):
        n.with_user(c.mgr).action_record_response()
    n.with_user(c.mgr).write(
        {
            "response_ref": "OUR/RESP/1",
            "response_on": c.today,
            "response_file": FILE,
            "response_filename": "reply.pdf",
        }
    )
    n.with_user(c.mgr).action_record_response()
    assert n.state == "responded" and n.responded_by_id == c.mgr
    with pytest.raises(UserError):
        n.with_user(c.mgr).write({"subject": "rewritten"})  # the notice is frozen
    n.with_user(c.mgr).write({"outcome": "assessed"})
    with pytest.raises(UserError, match="Segregation"):
        n.with_user(c.mgr).action_close()
    with pytest.raises(UserError, match="assessed"):
        n.with_user(c.mgr2).action_close()
    n.with_user(c.mgr2).write({"assessed_amount": 25000.0})
    with pytest.raises(UserError):
        n.with_user(c.acct).action_close()  # an accountant does not close
    n.with_user(c.mgr2).action_close()
    assert n.state == "closed" and n.closed_by_id == c.mgr2
    with pytest.raises(UserError):
        n.with_user(c.mgr2).write({"outcome": "withdrawn"})


def test_an_overdue_notice_escalates(c):
    n = _notice(c)
    # arrangement (superuser): the deadline has passed
    n.sudo().write({"received_on": c.today - timedelta(days=20)})
    n.sudo().write({"response_due": c.today - timedelta(days=1)})
    assert n.overdue
    c.cenv[NOTICE]._cron_notice_deadlines()
    escalated = n.activity_ids.filtered(lambda a: "overdue" in (a.summary or ""))
    assert c.mgr in escalated.mapped("user_id")


def test_notice_via_the_workspace_refuses_a_typed_state(c, p03):
    n = _notice(c)
    res = p03.write(c.acct, model=NOTICE, record_id=n.id, values={"state": "closed"})
    n.invalidate_recordset()
    assert n.state == "open" and "error" in res, res


# -------------------------------------------------------------- NID threshold
def test_m20_reads_the_nid_threshold_from_m51(c):
    """FR-TAX-044: M51 owns the high-value cash threshold; M20 applies it."""
    if "fix.ar.receipt" not in c.env:
        pytest.skip("cd_billing_engine is not installed")
    Receipt = c.env["fix.ar.receipt"].with_company(c.co)
    assert Receipt._nid_threshold() == 50000  # the seeded statutory default
    icp = c.env["ir.config_parameter"].sudo()
    icp.set_param("cd_billing_engine.nid_cash_threshold", "1000")  # legacy: not read
    assert Receipt._nid_threshold() == 50000
    # arrangement (superuser): a company row in force overrides the default
    c.env["fix.tax.parameter"].sudo().create(
        {
            "company_id": c.co.id,
            "key": "nid_cash_threshold",
            "value": 20000,
            "date_from": c.today - timedelta(days=1),
        }
    )
    assert Receipt._nid_threshold() == 20000
