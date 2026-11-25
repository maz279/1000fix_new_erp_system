"""M36 capture audit, second pass (2026-11-19): the spec records the pages
are about that had nowhere to be captured, driven as NON-ADMIN role holders
(the superuser is trusted by the model guards and would hide a gap).

  p1  technical review / second opinion of an estimate      FR-QTE-009
  p2  terms from the governed library; renewal quotation    FR-QTE-018/024
  p4  CCO + CFO approval of a term deviation                FR-QTE-027, BRU-QTE-08
      Finance override of the credit gate                   FR-QTE-028, BRU-QTE-14
  p5/7 acceptance on a recorded phone call                  FR-QTE-042
  p7  legal hold on a disputed quotation                    BRU-QTE-17
  p9  tender document checklist; outcome with a governed    FR-QTE-046/048,
      loss reason                                           BRU-QTE-15/16
"""

import types
from contextlib import contextmanager
from datetime import timedelta
from unittest import mock

import pytest
from odoo.addons.cd_quotation.models.fix_quote_ops import estimate_untaxed
from odoo.addons.cd_quotation.tests import test_a04_m36_controls as base
from odoo.addons.cd_quotation.tests.test_a04_m36_controls import (
    _approved_estimate,
    _approved_quote,
    _quote,
    _sent_quote,
    _submitted,
    _tender,
    _user,
)
from odoo.addons.cd_workflow_engine.tests.approval_helpers import inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
c = base.c  # the M36 controls fixture: its role holders, branch and customer
FINANCE = "account.group_account_manager"


@contextmanager
def _refused(env, match=None):
    with pytest.raises(REFUSED, match=match), env.cr.savepoint():
        yield


@pytest.fixture
def act(c):
    """The workspace's /p03/model/action and /p03/model/write, as a user."""
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as generic

    ctl = generic.P03GenericApiController()

    def call(user, route, **kw):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        with mock.patch.object(generic, "request", req):
            fn = getattr(generic.P03GenericApiController, route)
            fn = getattr(fn, "original_endpoint", None) or fn
            return fn(ctl, **kw)

    return call


def _ok(res):
    return bool(res) and not res.get("error") and bool(res.get("success") or res.get("id"))


@pytest.fixture
def x(c):
    c.finance = _user(c.env, "m36p2_finance", [FINANCE])
    c.finance2 = _user(c.env, "m36p2_finance2", [FINANCE])
    c.agent = _user(c.env, "m36p2_agent", ["cd_quotation.group_quotation_user"])
    c.tech = _user(c.env, "m36p2_tech")
    return c


def _std(c, code, text, **kw):
    vals = {"code": code, "name": code, "term_type": "term", "text_en": text}
    vals.update(kw)
    return c.env["fix.quotation.standard.term"].with_user(c.manager).create(vals)


def _submit(c, q):
    q.with_user(c.author).action_submit(justification="test")
    task = inbox_task(q, c.t1) or inbox_task(q, c.t2) or inbox_task(q, c.t3)
    task.with_user(task.assigned_user_id).action_approve(comment="ok")
    assert q.state == "approved", q.state


# =========================================================================== p10 / p2 / p4 terms
def test_only_the_commercial_manager_keeps_the_library(x, act):
    c = x
    res = act(
        c.author,
        "model_write",
        model="fix.quotation.standard.term",
        values={"code": "PAY", "name": "Payment", "term_type": "term", "text_en": "50% advance."},
    )
    assert not _ok(res)
    res = act(
        c.manager,
        "model_write",
        model="fix.quotation.standard.term",
        values={"code": "PAY", "name": "Payment", "term_type": "term", "text_en": "50% advance."},
    )
    assert _ok(res), res


def test_a_standard_term_needs_no_approval_and_a_deviation_needs_cco_and_cfo(x, act):
    c = x
    std = _std(c, "WTY", "90 days warranty on parts and labour.")
    q = _quote(c)
    res = act(
        c.author,
        "model_write",
        model="fix.quotation.term",
        values={"quotation_id": q.id, "standard_term_id": std.id, "term_type": "term"},
    )
    assert _ok(res), res
    word = c.env["fix.quotation.term"].browse(res["id"])
    assert word.is_standard and word.deviation_state == "standard"
    assert word.text_en == std.text_en and word.recorded_by_id == c.author
    # own wording without a reason is refused; with one it is a deviation
    with _refused(c.env, match="say why"):
        c.env["fix.quotation.term"].with_user(c.author).create(
            {"quotation_id": q.id, "term_type": "exclusion", "text_en": "No liability for data."}
        )
    dev = (
        c.env["fix.quotation.term"]
        .with_user(c.author)
        .create(
            {
                "quotation_id": q.id,
                "term_type": "term",
                "standard_term_id": std.id,
                "text_en": "180 days warranty on parts and labour.",
                "deviation_reason": "Framework customer asked for 180 days.",
            }
        )
    )
    assert dev.deviation_state == "pending"
    with _refused(c.env, match="CCO and CFO"):
        q.with_user(c.author).action_submit(justification="test")
    # neither the author nor a plain user approves; a stamp is never typed
    for who in (c.author, c.clerk):
        res = act(
            who,
            "model_action",
            model="fix.quotation.term",
            ids=[dev.id],
            method="action_decide_deviation",
            kwargs={"decision": "approve"},
        )
        assert not _ok(res), who.login
    res = act(
        c.manager,
        "model_write",
        model="fix.quotation.term",
        record_id=dev.id,
        values={"commercial_approver_id": c.manager.id},
    )
    dev.invalidate_recordset()
    assert not dev.commercial_approver_id
    # the Commercial Manager signs for the CCO ...
    res = act(
        c.manager,
        "model_action",
        model="fix.quotation.term",
        ids=[dev.id],
        method="action_decide_deviation",
        kwargs={"decision": "approve"},
    )
    assert _ok(res), res
    dev.invalidate_recordset()
    assert dev.commercial_approver_id == c.manager and dev.deviation_state == "pending"
    with _refused(c.env, match="already approved|other approver"):
        dev.with_user(c.manager).action_decide_deviation(decision="approve")
    # ... and Finance for the CFO
    dev.with_user(c.finance).action_decide_deviation(decision="approve")
    assert dev.finance_approver_id == c.finance and dev.deviation_state == "approved"
    _submit(c, q)
    # a Commercial Manager who wrote the quotation does not approve its deviation
    own = _quote(c, user=c.manager)
    mine = (
        c.env["fix.quotation.term"]
        .with_user(c.manager)
        .create({"quotation_id": own.id, "text_en": "Own wording.", "deviation_reason": "r"})
    )
    with _refused(c.env, match="Segregation"):
        mine.with_user(c.manager).action_decide_deviation(decision="approve")
    # an issued version's terms are frozen
    q.with_user(c.author).action_send()
    with _refused(c.env, match="draft"):
        dev.with_user(c.author).write({"text_en": "365 days."})


def test_new_wording_needs_new_approval_and_a_rejection_blocks(x):
    c = x
    q = _quote(c)
    Term = c.env["fix.quotation.term"].with_user(c.author)
    dev = Term.create(
        {"quotation_id": q.id, "text_en": "Site access 24/7.", "deviation_reason": "Bank site."}
    )
    dev.with_user(c.manager).action_decide_deviation(decision="approve")
    dev.with_user(c.finance).action_decide_deviation(decision="approve")
    assert dev.deviation_state == "approved"
    dev.write({"text_en": "Site access 24/7 incl. holidays."})
    assert dev.deviation_state == "pending" and not dev.commercial_approver_id
    with _refused(c.env, match="why"):
        dev.with_user(c.finance).action_decide_deviation(decision="reject")
    dev.with_user(c.finance).action_decide_deviation(decision="reject", note="Cost not priced.")
    assert dev.deviation_state == "rejected"
    with _refused(c.env, match="rejected"):
        q.with_user(c.author).action_submit(justification="test")
    # one person holding both roles signs one slot only: the CCO and the CFO
    # are two people
    both = _user(c.env, "m36p2_both", ["cd_quotation.group_quotation_manager", FINANCE])
    dev2 = Term.create(
        {"quotation_id": q.id, "text_en": "Night work allowed.", "deviation_reason": "Bank."}
    )
    dev2.with_user(both).action_decide_deviation(decision="approve")
    with _refused(c.env, match="already approved|other approver"):
        dev2.with_user(both).action_decide_deviation(decision="approve")
    assert dev2.deviation_state == "pending"
    dev2.with_user(c.finance).action_decide_deviation(decision="approve")
    assert dev2.deviation_state == "approved"
    dev.unlink()
    _submit(c, q)


def test_the_library_knows_every_kind_of_quotation(x):
    """Seeding the library from the live templates failed: three of the four
    are "project" quotations, which a fixed three-type list refused."""
    c = x
    kinds = dict(c.env["fix.quotation"]._fields["quote_type"].selection)
    assert "project" in kinds
    std = _std(c, "PRJ-DEL", "Delivery within 30 days.", quote_type="project")
    assert std.quote_type == "project"
    q = _quote(c, quote_type="project")
    q.with_user(c.author).action_apply_standard_terms()
    assert std in q.term_ids.mapped("standard_term_id")
    contract_q = _quote(c)
    try:
        with c.env.cr.savepoint():
            contract_q.with_user(c.author).action_apply_standard_terms()
    except UserError:
        pass  # nothing else in the library applies to it
    assert std not in contract_q.term_ids.mapped("standard_term_id")


def test_a_mandatory_standard_term_is_attached_before_submission(x, act):
    c = x
    std = _std(c, "VAT", "Prices include VAT at 15%.", mandatory=True, quote_type="contract")
    q = _quote(c)
    with _refused(c.env, match="mandatory standard term"):
        q.with_user(c.author).action_submit(justification="test")
    res = act(
        c.author,
        "model_action",
        model="fix.quotation",
        ids=[q.id],
        method="action_apply_standard_terms",
        kwargs={},
    )
    assert _ok(res), res
    q.invalidate_recordset()
    assert std in q.term_ids.mapped("standard_term_id")
    _submit(c, q)
    # a revision carries the terms into the next version
    q.with_user(c.author).action_send()
    nxt = c.env["fix.quotation"].browse(q.with_user(c.author).action_revise()["res_id"])
    assert std in nxt.term_ids.mapped("standard_term_id")


# =========================================================================== p4 credit gate
def _hold(c, partner, **kw):
    vals = {"customer_id": partner.id, "company_id": c.env.company.id}
    vals.update(kw)
    return c.env["fix.credit.profile"].sudo().create(vals)


def test_a_held_customer_is_not_issued_a_quotation_without_finance(x, act):
    c = x
    q = _approved_quote(c)
    _hold(c, c.customer, credit_hold=True, hold_reason="cheque bounced")
    assert "credit hold" in (q.credit_block_reason or "")
    with _refused(c.env, match="BRU-QTE-14"):
        q.with_user(c.author).action_send()
    # neither the author nor a plain user overrides; Finance does
    for who in (c.author, c.clerk):
        res = act(
            who,
            "model_write",
            model="fix.quotation.credit.override",
            values={"quotation_id": q.id, "reason": "x"},
        )
        assert not _ok(res), who.login
    res = act(
        c.finance,
        "model_write",
        model="fix.quotation.credit.override",
        values={"quotation_id": q.id, "reason": "Cheque replaced; MD confirmed."},
    )
    assert _ok(res), res
    ov = c.env["fix.quotation.credit.override"].browse(res["id"])
    assert ov.granted_by_id == c.finance and ov.version == q.version
    assert "credit hold" in ov.block_reason
    with _refused(c.env):
        ov.with_user(c.finance).write({"reason": "changed"})
    q.with_user(c.author).action_send()
    assert q.state == "sent"
    # a Finance user who wrote the quotation does not override its gate
    dual = _user(c.env, "m36p2_dual", ["cd_quotation.group_quotation_user", FINANCE])
    own = _quote(c, user=dual)
    with _refused(c.env, match="Segregation"):
        c.env["fix.quotation.credit.override"].with_user(dual).create(
            {"quotation_id": own.id, "reason": "mine"}
        )


def test_over_the_limit_is_gated_and_a_customer_within_credit_needs_no_override(x):
    c = x
    q = _approved_quote(c)
    with _refused(c.env, match="no override is needed"):
        c.env["fix.quotation.credit.override"].with_user(c.finance).create(
            {"quotation_id": q.id, "reason": "x"}
        )
    _hold(c, c.customer, credit_limit=1000.0)
    assert "over the credit limit" in (q.credit_block_reason or "")
    with _refused(c.env, match="BRU-QTE-14"):
        q.with_user(c.author).action_send()


def test_acceptance_is_gated_and_a_revoked_override_stops_it(x):
    c = x
    q = _sent_quote(c)
    _hold(c, c.customer, credit_hold=True, hold_reason="legal case")
    with _refused(c.env, match="BRU-QTE-14"):
        q.with_user(c.agent).action_record_phone_acceptance(
            consent_ref="REC-1", called_number="01711000361"
        )
    ov = (
        c.env["fix.quotation.credit.override"]
        .with_user(c.finance)
        .create({"quotation_id": q.id, "reason": "Paid in advance."})
    )
    ov.with_user(c.finance2).action_revoke()
    with _refused(c.env, match="BRU-QTE-14"):
        q.with_user(c.agent).action_record_phone_acceptance(
            consent_ref="REC-1", called_number="01711000361"
        )


# =========================================================================== p5/p7 phone acceptance
def test_phone_acceptance_needs_the_recording_the_customers_number_and_not_the_author(x, act):
    c = x
    q = _sent_quote(c)

    def call(user, **kw):
        return act(
            user,
            "model_action",
            model="fix.quotation",
            ids=[q.id],
            method="action_record_phone_acceptance",
            kwargs=kw,
        )

    res = call(c.author, consent_ref="REC-77", called_number="01711000361")
    assert not _ok(res) and "Segregation" in res["error"]
    res = call(c.agent, consent_ref="", called_number="01711000361")
    assert not _ok(res) and "consent" in res["error"]
    res = call(c.agent, consent_ref="REC-77", called_number="01999999999")
    assert not _ok(res) and "customer's own" in res["error"]
    q.invalidate_recordset()
    assert q.state == "sent"
    res = call(c.agent, consent_ref="REC-77", called_number="+880 1711-000361")
    assert _ok(res), res
    q.invalidate_recordset()
    assert q.state == "accepted" and q.acceptance_method == "phone"
    assert "REC-77" in q.acceptance_ref and q.evidence_hash
    assert q.acceptance_recorded_by == c.agent


# =========================================================================== p7 legal hold
def test_a_quotation_on_legal_hold_is_never_deleted_and_released_by_another(x, act):
    c = x
    q = _quote(c)
    res = act(
        c.author,
        "model_write",
        model="fix.quotation.legal.hold",
        values={
            "quotation_id": q.id,
            "dispute_ref": "CASE-9",
            "reason": "Customer disputes price.",
        },
    )
    assert _ok(res), res
    hold = c.env["fix.quotation.legal.hold"].browse(res["id"])
    assert hold.placed_by_id == c.author and q.legal_hold
    with _refused(c.env, match="already on legal hold"):
        c.env["fix.quotation.legal.hold"].with_user(c.author).create(
            {"quotation_id": q.id, "dispute_ref": "CASE-10", "reason": "again"}
        )
    with _refused(c.env, match="legal hold"):
        q.with_user(c.author).unlink()
    with _refused(c.env, match="legal hold"):
        q.sudo().unlink()
    with _refused(c.env):
        hold.with_user(c.author).unlink()
    # the author is no manager; the manager who placed it does not release it
    with _refused(c.env, match="Commercial Manager"):
        hold.with_user(c.author).action_release(note="settled")
    own = c.env["fix.quotation.legal.hold"].with_user(c.manager)
    hold2_q = _quote(c)
    hold2 = own.create({"quotation_id": hold2_q.id, "dispute_ref": "C2", "reason": "r"})
    with _refused(c.env, match="Segregation"):
        hold2.with_user(c.manager).action_release(note="settled")
    res = act(
        c.manager,
        "model_action",
        model="fix.quotation.legal.hold",
        ids=[hold.id],
        method="action_release",
        kwargs={"note": "Settled in writing."},
    )
    assert _ok(res), res
    hold.invalidate_recordset()
    q.invalidate_recordset()
    assert hold.state == "released" and hold.released_by_id == c.manager and not q.legal_hold


# =========================================================================== p1 technical review
def test_an_estimate_under_review_is_not_quoted_until_the_reviewer_clears_it(x, act):
    c = x
    est = _approved_estimate(c)
    q = _quote(c, estimate_id=est.id, quote_type="service", value=estimate_untaxed(est))
    with _refused(c.env, match="someone else"):
        c.env["fix.estimate.review"].with_user(c.author).create(
            {
                "estimate_id": est.id,
                "reason": "high_value",
                "question": "x",
                "reviewer_id": c.author.id,
            }
        )
    res = act(
        c.author,
        "model_write",
        model="fix.estimate.review",
        values={
            "estimate_id": est.id,
            "reason": "high_value",
            "question": "Is the board replacement justified?",
            "reviewer_id": c.tech.id,
        },
    )
    assert _ok(res), res
    rev = c.env["fix.estimate.review"].browse(res["id"])
    assert rev.state == "requested" and rev.requested_by_id == c.author
    with _refused(c.env, match="technical review"):
        q.with_user(c.author).action_submit(justification="test")
    # only the named reviewer decides, and writes the findings
    res = act(
        c.author,
        "model_action",
        model="fix.estimate.review",
        ids=[rev.id],
        method="action_decide",
        kwargs={"decision": "cleared", "findings": "ok"},
    )
    assert not _ok(res) and "named reviewer" in res["error"]
    with _refused(c.env, match="findings"):
        rev.with_user(c.tech).action_decide(decision="returned")
    rev.with_user(c.tech).action_decide(decision="returned", findings="Board can be reflowed.")
    with _refused(c.env, match="returned"):
        q.with_user(c.author).action_submit(justification="test")
    with _refused(c.env, match="not edited"):
        rev.with_user(c.author).write({"question": "changed"})
    again = (
        c.env["fix.estimate.review"]
        .with_user(c.author)
        .create(
            {
                "estimate_id": est.id,
                "reason": "high_value",
                "question": "Reworked.",
                "reviewer_id": c.tech.id,
            }
        )
    )
    res = act(
        c.tech,
        "model_action",
        model="fix.estimate.review",
        ids=[again.id],
        method="action_decide",
        kwargs={"decision": "cleared", "findings": "Sound."},
    )
    assert _ok(res), res
    q.with_user(c.author).action_submit(justification="cleared by review")
    assert q.approval_state == "pending"


# =========================================================================== p2 renewal
def _contract(c, **kw):
    vals = {
        "name": "M36P2 AMC",
        "family": "amc",
        "customer_id": c.customer.id,
        "operating_unit_id": c.ou.id,
        "company_id": c.env.company.id,
        "date_start": c.today - timedelta(days=330),
        "date_end": c.today + timedelta(days=35),
        "annual_value": 120000.0,
        "escalation_pct": 5.0,
    }
    vals.update(kw)
    contract = c.env["fix.contract"].sudo().create(vals)
    contract._guarded().write({"state": "expiring"})
    return contract


def test_a_renewal_quotation_carries_the_contract_with_escalation(x, act):
    c = x
    contract = _contract(c)
    res = act(
        c.author,
        "model_write",
        model="fix.quotation",
        values={
            "renewal_of_contract_id": contract.id,
            "contract_months": 12,
            "valid_until": str(c.today + timedelta(days=20)),
            "cost_amount": 70000.0,
        },
    )
    assert _ok(res), res
    q = c.env["fix.quotation"].browse(res["id"])
    assert q.quote_type == "contract" and q.customer_id == c.customer
    assert q.contract_start == contract.date_end + timedelta(days=1)
    assert q.value == pytest.approx(126000.0)
    with _refused(c.env, match="in progress"):
        c.env["fix.quotation"].with_user(c.author).create(
            {"renewal_of_contract_id": contract.id, "valid_until": c.today + timedelta(days=5)}
        )
    other = _contract(c, name="Other AMC")
    with _refused(c.env, match="stays on the contract"):
        q.with_user(c.author).write({"renewal_of_contract_id": other.id})
    draft = (
        c.env["fix.contract"]
        .sudo()
        .create(
            {
                "name": "Draft AMC",
                "family": "amc",
                "customer_id": c.customer.id,
                "operating_unit_id": c.ou.id,
                "date_start": c.today,
                "date_end": c.today + timedelta(days=365),
                "annual_value": 1.0,
            }
        )
    )
    with _refused(c.env, match="in force"):
        c.env["fix.quotation"].with_user(c.author).create(
            {"renewal_of_contract_id": draft.id, "valid_until": c.today + timedelta(days=5)}
        )


# =========================================================================== p9 tender pack
def _doc(c, t, **kw):
    vals = {"tender_id": t.id, "document_type": "trade_licence", "name": "Trade licence 2026"}
    vals.update(kw)
    return c.env["fix.tender.document"].with_user(c.coord).create(vals)


def test_a_bid_waits_for_every_required_document_and_the_pack_is_sealed(x, act):
    c = x
    t = _tender(c)
    t.with_user(c.member).action_decide_bid(reason="fits")
    res = act(
        c.coord,
        "model_write",
        model="fix.tender.document",
        values={
            "tender_id": t.id,
            "document_type": "bank_solvency",
            "name": "Solvency certificate",
        },
    )
    assert _ok(res), res
    doc = c.env["fix.tender.document"].browse(res["id"])
    assert doc.state == "missing" and doc.version == 0
    waived = _doc(c, t, document_type="other", name="Optional brochure", required=False)
    assert waived.state == "waived"
    with _refused(c.env, match="BRU-QTE-15"):
        t.with_user(c.coord).action_submit()
    with _refused(c.env):
        _doc(c, t).with_user(c.clerk).write({"name": "x"})
    att = (
        c.env["ir.attachment"]
        .with_user(c.coord)
        .create({"name": "solvency.pdf", "raw": b"%PDF-1.4 solvency"})
    )
    foreign = c.env["ir.attachment"].with_user(c.author).create({"name": "x.pdf", "raw": b"%PDF x"})
    with _refused(c.env, match="uploaded yourself"):
        doc.with_user(c.coord).write({"attachment_id": foreign.id})
    doc.with_user(c.coord).write({"attachment_id": att.id})
    assert doc.state == "ready" and doc.version == 1 and doc.checksum
    assert doc.prepared_by_id == c.coord
    for leftover in t.document_ids.filtered(lambda d: d.state == "missing"):
        up = c.env["ir.attachment"].with_user(c.coord).create({"name": "tl.pdf", "raw": b"tl"})
        leftover.with_user(c.coord).write({"attachment_id": up.id})
    with _refused(c.env, match="expires"):
        _doc(c, t, name="Old licence", valid_until=c.today + timedelta(days=1))
    t.with_user(c.coord).action_submit()
    assert t.state == "submitted" and len(t.submission_pack_hash or "") == 64
    with _refused(c.env, match="frozen"):
        doc.with_user(c.coord).write({"name": "changed"})


def test_a_lost_tender_records_a_governed_reason(x, act):
    c = x
    t = _submitted(c)
    res = act(
        c.coord,
        "model_write",
        model="fix.tender.outcome",
        values={"tender_id": t.id, "result": "lost", "notes": "x"},
    )
    assert not _ok(res)
    res = act(
        c.author,
        "model_write",
        model="fix.tender.outcome",
        values={
            "tender_id": t.id,
            "result": "lost",
            "loss_reason_code": "price",
            "notes": "Lost on price.",
        },
    )
    assert not _ok(res)
    res = act(
        c.coord,
        "model_write",
        model="fix.tender.outcome",
        values={
            "tender_id": t.id,
            "result": "lost",
            "loss_reason_code": "price",
            "awarded_to": "Rival Ltd",
            "winning_value": 650000.0,
            "notes": "Rival bid 7% below; our AMC labour rate is high.",
        },
    )
    assert _ok(res), res
    out = c.env["fix.tender.outcome"].browse(res["id"])
    t.invalidate_recordset()
    assert t.state == "lost" and t.loss_reason_code == "price"
    assert t.awarded_to == "Rival Ltd" and t.winning_value == pytest.approx(650000.0)
    assert out.our_value == pytest.approx(700000.0) and out.price_gap_pct == pytest.approx(7.69)
    with _refused(c.env):
        out.with_user(c.coord).write({"notes": "changed"})
    from odoo.addons.cd_p03_portal.controllers.a04 import m36

    pack = m36.tender_winloss(c.env)
    assert any("Price higher than the winner" in n for n in pack["notes"])
    # Record Loss is no longer a workspace action; a loss any other way is "Other"
    assert "action_record_loss" not in m36.SURFACES["fix.tender"]["actions"]
    t2 = _submitted(c)
    t2.with_user(c.coord).action_record_loss(reason="direct")
    assert t2.loss_reason_code == "other"


def test_an_issuer_cancellation_is_an_outcome_too(x):
    c = x
    t = _submitted(c)
    c.env["fix.tender.outcome"].with_user(c.coord).create(
        {
            "tender_id": t.id,
            "result": "cancelled",
            "loss_reason_code": "price",
            "notes": "Ministry withdrew the tender.",
        }
    )
    assert t.state == "cancelled" and t.loss_reason_code == "issuer_cancelled"


def test_new_records_are_read_by_staff_and_written_only_by_their_roles(x):
    c = x
    for model in (
        "fix.quotation.standard.term",
        "fix.quotation.term",
        "fix.quotation.credit.override",
        "fix.quotation.legal.hold",
        "fix.estimate.review",
        "fix.tender.document",
        "fix.tender.outcome",
    ):
        c.env[model].with_user(c.clerk).check_access("read")
    for model in (
        "fix.quotation.standard.term",
        "fix.quotation.term",
        "fix.quotation.credit.override",
        "fix.quotation.legal.hold",
        "fix.tender.document",
        "fix.tender.outcome",
    ):
        with pytest.raises(AccessError):
            c.env[model].with_user(c.clerk).check_access("create")
