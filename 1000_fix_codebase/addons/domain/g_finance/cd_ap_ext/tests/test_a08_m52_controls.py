# cd_ap_ext — A08 M52 controls (A08 workflow audit, 2026-11-04).
#
# One test per gap probe of working/A08_evidence/probes/m52/probe_m52.py, named
# after the probe id: each runs the probe's attack as a NON-ADMIN user holding
# the real finance role (created in the rolled-back transaction) and asserts
# the control now holds; proper-path tests show the legitimate maker and
# checker can still do the job. Treasury (M50) execution steps that are not
# under test are driven as the superuser and labelled.
from __future__ import annotations

import base64
import itertools
import json
from datetime import date

import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
BILL = "account.group_account_invoice"
BUYER = "cd_requisition.group_fix_procurement_buyer"
D = date(2026, 10, 1)
DUE_BY = date(2026, 10, 2)
_SEQ = itertools.count(1)


class Ctx:
    pass


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "company_id": env.company.id,
                "company_ids": [(6, 0, [env.company.id])],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def refused(env, fn):
    """The exception that refused fn (in a savepoint), or None if it ran."""
    try:
        with env.cr.savepoint():
            fn()
    except REFUSED as exc:
        return exc
    return None


def balance(env, account):
    env.flush_all()
    lines = env["account.move.line"].search(
        [("account_id", "=", account.id), ("parent_state", "=", "posted")]
    )
    return round(sum(lines.mapped("debit")) - sum(lines.mapped("credit")), 2)


def _file(env, name, content):
    return env["ir.attachment"].create(
        {"name": name, "datas": base64.b64encode(content.encode()).decode()}
    )


def confirm_bank(c, partner, acc_number, proposer=None, confirmer=None):
    """S1 proper path: an accountant proposes the account with the call-back
    on record, a different accounting manager confirms it."""
    change = (
        c.env["fix.payee.bank.change"]
        .with_user(proposer or c.acc3)
        .create(
            {
                "partner_id": partner.id,
                "acc_number": acc_number,
                "routing_number": "175260346",
                "verification_ref": "Called %s on the number in the signed vendor form, "
                "26 Oct 2026 11:05; account confirmed" % partner.name,
            }
        )
    )
    change.with_user(proposer or c.acc3).action_propose()
    change.with_user(confirmer or c.mgr2).action_confirm()
    return change.result_bank_id


def treasury_execute(c, execution, ref="A08M52-BEFTN-1"):
    """Treasury (M50), not under test here: the bank executed the instruction
    (statement-confirmed). Driven as the superuser."""
    ex = execution.sudo()
    ex._guarded().write(
        {
            "state": "executed",
            "bank_reference": ref,
            "confirmation_source": "bank_reference",
            "executed_at": fields.Datetime.now(),
        }
    )


def treasury_fail(c, execution):
    """Treasury (M50), not under test: the bank rejected the instruction."""
    execution.sudo()._guarded().write({"state": "failed", "failure_reason": "account closed"})


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.company = env.company
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    Account = env["account.account"]

    def acc(code, name, kind):
        found = Account.search([("code", "=", code), ("company_ids", "in", x.company.id)], limit=1)
        return found or Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [x.company.id])],
            }
        )

    x.a = {
        "vat_input": acc("990131", "Test input VAT", "asset_current"),
        "vds_payable": acc("990252", "Test VDS payable", "liability_current"),
        "tds_payable": acc("990253", "Test TDS payable", "liability_current"),
        "employee_payable": acc("990230", "Test employee payable", "liability_current"),
        "employee_advance": acc("990141", "Test employee advances", "asset_current"),
        "salary_payable": acc("990231", "Test salaries payable", "liability_current"),
        "expense": acc("990600", "Test expense", "expense"),
    }
    icp = env["ir.config_parameter"].sudo()
    for param, code in (
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_tax_engine_bd.account_code.vds_payable", "990252"),
        ("cd_tax_engine_bd.account_code.tds_payable", "990253"),
        ("cd_ap_ext.account_code.employee_payable", "990230"),
        ("cd_ap_ext.account_code.employee_advance", "990141"),
        ("cd_ap_ext.account_code.salary_payable", "990231"),
        ("cd_ap_ext.account_code.expense", "990600"),
    ):
        icp.set_param(param, code)
    x.bank = env["account.journal"].search(
        [("company_id", "=", x.company.id), ("type", "=", "bank")], limit=1
    )
    icp.set_param("cd_ap_ext.payment_journal_code", x.bank.code)
    x.ap = Account.search([("code", "=", "211000"), ("company_ids", "in", x.company.id)], limit=1)
    x.acc1 = _user(env, "a08b2_acc1", [ACC])
    x.acc2 = _user(env, "a08b2_acc2", [ACC])
    x.acc3 = _user(env, "a08b2_acc3", [ACC])
    x.mgr = _user(env, "a08b2_mgr", [MGR])
    x.mgr2 = _user(env, "a08b2_mgr2", [MGR])
    x.bill = _user(env, "a08b2_bill", [BILL])
    x.plain = _user(env, "a08b2_plain")
    x.p2 = _user(env, "a08b2_plain2")
    x.vendor = env["res.partner"].create({"name": "A08B2 Padma Spares Ltd."})
    x.profile = env["fix.vendor.tax.profile"].create(
        {
            "partner_id": x.vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789012",
            "bin": "9876543210123",
            "psr_reference": "PSR-A08B2",
            "psr_valid_until": "2099-06-30",
            "psr_attachment_ids": [(6, 0, _file(env, "psr.pdf", "PSR-A08B2").ids)],
        }
    )
    x.vbank = confirm_bank(x, x.vendor, "A08B2-VENDOR-001")
    x.accomplice = env["res.partner"].create({"name": "A08B2 Accomplice"})
    x.abank = env["res.partner.bank"].create(
        {
            "partner_id": x.accomplice.id,
            "acc_number": "A08B2-ACCOMPLICE-999",
            "fix_routing_number": "175260346",
        }
    )
    x.product = env["product.product"].create({"name": "A08B2 Logic board"})
    x.grade = env["fix.expense.grade"].create({"name": "A08B2 Field technician"})
    x.emp_plain = env["hr.employee"].create(
        {"name": "A08B2 Plain Employee", "user_id": x.plain.id, "expense_grade_id": x.grade.id}
    )
    ebank = confirm_bank(x, x.emp_plain.work_contact_id, "A08B2-EMP-001")
    for name in ("bank_account_ids", "primary_bank_account_id"):
        if name in x.emp_plain._fields:
            x.emp_plain[name] = ebank
    x.emp_p2 = env["hr.employee"].create(
        {"name": "A08B2 Plain2 Employee", "user_id": x.p2.id, "expense_grade_id": x.grade.id}
    )
    x.emp_nouser = env["hr.employee"].create(
        {"name": "A08B2 No-login Employee", "expense_grade_id": x.grade.id}
    )
    x.hotel = env.ref("cd_ap_ext.expense_category_accommodation")
    x.other = env.ref("cd_ap_ext.expense_category_other")
    env["fix.expense.policy"].create(
        {
            "category_id": x.hotel.id,
            "grade_id": x.grade.id,
            "limit_per_line": 4000.0,
            "receipt_required_above": 1000.0,
        }
    )
    return x


def bill(c, price, by=None, qty=1.0, ref=None, po=None, vendor=None, **vals):
    return (
        c.env["fix.vendor.invoice"]
        .with_user(by or c.acc1)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": (vendor or c.vendor).id,
                "invoice_ref": ref or "A08B2-%d" % next(_SEQ),
                "invoice_date": vals.pop("invoice_date", D),
                "payment_term_days": vals.pop("payment_term_days", 0),
                "bill_type": vals.pop("bill_type", "po" if po else "non_po"),
                "requisition_id": po.id if po else False,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "A08B2 Logic board",
                            "quantity": qty,
                            "unit_price": price,
                            "tds_category": vals.pop("tds_category", "service_general"),
                            "tds_exempt": vals.pop("tds_exempt", False),
                        },
                    )
                ],
                **vals,
            }
        )
    )


def approve(c, b, submit_by=None, approve_by=None):
    b.with_user(submit_by or c.acc1).action_submit_approval()
    b.with_user(approve_by or c.acc2).action_approve()
    if b.approval_state != "approved":
        b.with_user(c.mgr).action_approve()
    return b


def issued_po(c, qty, price, received=0.0, by=None):
    """A PO as M16 leaves it: approved and sent (superuser), optionally with a
    posted, inspected receipt."""
    env = c.env
    if "fix.supplier" in env and not env["fix.supplier"].search([("partner_id", "=", c.vendor.id)]):
        supplier = env["fix.supplier"].create(
            {"name": c.vendor.name, "partner_id": c.vendor.id, "status": "active"}
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
            )
    po = (
        env["fix.purchase.order"]
        .with_user(by or env.user)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "line_ids": [
                    (0, 0, {"product_id": c.product.id, "qty_ordered": qty, "unit_price": price})
                ],
            }
        )
    ).sudo()
    po.action_record_requisition_exception(reason="A08 B2 test PO without requisition")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    po.action_send()
    if received:
        po.action_record_receipt({po.line_ids.id: received})
        receipt = po.receipt_ids.sorted("id")[-1]
        for line in receipt.line_ids:
            env["fix.procurement.inspection"].create(
                {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
            ).action_confirm()
    return env["fix.purchase.order"].browse(po.id)


def run(c, by=None):
    return (
        c.env["fix.payment.run"].with_user(by or c.acc1).create({"rail": "beftn", "due_by": DUE_BY})
    )


def approved_run(c, b=None, preparer=None):
    if b is None:
        approve(c, bill(c, 10000.0))
    r = run(c, by=preparer)
    r.with_user(preparer or c.acc1).action_propose()
    r.with_user(preparer or c.acc1).action_submit()
    r.with_user(c.mgr).action_approve()
    return r


def claim(c, by, employee, lines=None, **vals):
    v = {
        "operating_unit_id": c.ou.id,
        "employee_id": employee.id,
        "description": "A08B2 site visit",
        "expense_date": D,
    }
    if lines is not None:
        v["line_ids"] = [(0, 0, {"cost_centre": "A08B2", **ln}) for ln in lines]
    v.update(vals)
    return c.env["fix.expense.claim"].with_user(by).create(v)


def advance(c, by, employee, amount=5000.0, **vals):
    v = {
        "operating_unit_id": c.ou.id,
        "employee_id": employee.id,
        "purpose": "A08B2 parts float",
        "amount": amount,
    }
    v.update(vals)
    return c.env["fix.employee.advance"].with_user(by).create(v)


def disbursed_advance(c, amount=5000.0, **vals):
    adv = advance(c, c.acc2, c.emp_plain, amount, **vals)
    adv.with_user(c.acc1).action_approve()
    treasury_execute(c, adv.execution_id)
    adv.with_user(c.acc1).action_confirm_disbursement()
    return adv


@pytest.fixture
def p03(c):
    import types

    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()
    mw = getattr(
        g.P03GenericApiController.model_write,
        "original_endpoint",
        g.P03GenericApiController.model_write,
    )
    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req

    try:
        yield types.SimpleNamespace(write=lambda user, **kw: (as_user(user), mw(ctl, **kw))[1])
    finally:
        g.request, s.request = old_g, old_s


# ============================================================ reference runs
def test_ref_01_bill_approval_posts_gl(c):
    """Proper path: 10,000 non-PO service bill, 10% TDS s.90; acc1 submits, acc2
    approves -> Dr expense 10,000 / Cr TDS 1,000 / Cr AP 9,000; the TDS
    deduction sent to the return is the GL figure."""
    b = approve(c, bill(c, 10000.0))
    assert b.approval_state == "approved" and b.move_id.state == "posted"
    assert (b.tds_amount, b.total_payable) == (1000.0, 9000.0)
    debit = sum(b.move_id.line_ids.mapped("debit"))
    assert debit == sum(b.move_id.line_ids.mapped("credit")) == 10000.0
    w = b.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    assert (w.amount, w.multiplier, w.psr_received) == (1000.0, 1.0, True)


def test_ref_02_payment_run_full_cycle_three_people(c):
    """Proper path: acc1 prepares, mgr approves, acc2 (a third person)
    releases -> one pinned execution for 9,000 to the vendor's confirmed
    account; treasury executes; the sync posts Dr AP / Cr bank and pays."""
    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    snap = json.loads(r.approved_snapshot)
    assert (r.approved_total, snap[0]["acc_number"]) == (9000.0, "A08B2VENDOR001")
    r.with_user(c.acc2).action_release()
    ex = r.line_ids.execution_id.sudo()
    assert (ex.amount, ex.partner_bank_id, ex.source_model) == (
        9000.0,
        c.vbank,
        "fix.payment.run.line",
    )
    assert (r.released_by, b.payment_state) == (c.acc2, "in_run")
    treasury_execute(c, ex)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (b.payment_state, r.state, r.line_ids.move_id.state) == ("paid", "done", "posted")
    lock = c.env["fix.ap.bill.payment"].sudo().search([("bill_id", "=", b.id)])
    assert lock.state == "paid"


def test_bill_payment_requested_payload(c):
    """Proper path: an approved, posted, non-PO bill raises payment.requested
    with what M50's consumer needs (payee, amount, OU, company, approver)."""
    b = approve(c, bill(c, 5000.0))
    b.with_user(c.acc1).action_request_payment()
    events = (
        c.env["fix.event.outbox"]
        .sudo()
        .search(
            [
                ("event_type", "=", "payment.requested"),
                ("aggregate", "=", "fix.vendor.invoice"),
                ("aggregate_id", "=", b.id),
            ]
        )
    )
    payload = json.loads(events.payload)
    assert payload == {
        "vendor_id": c.vendor.id,
        "amount": 4500.0,  # 5,000.00 - 10% TDS 500.00
        "currency": "BDT",
        "invoice_ref": b.invoice_ref,
        "operating_unit_id": c.ou.id,
        "company_id": c.company.id,
        "payee_partner_id": c.vendor.id,
        "approved_by": c.acc2.id,
    }


# ============================================================ approval matrix (F3, M52-2/-3/-11)
def test_m52_01_submitter_cannot_approve(c):
    b = bill(c, 10000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(c.acc1).action_approve())


def test_m52_01b_submitter_who_is_not_the_creator_cannot_approve(c):
    """Mutation check: with the creator as the submitter a second rule also refuses,
    which hid the submitter rule. Here only the submitter rule applies."""
    b = bill(c, 10000.0, by=c.acc2)
    b.with_user(c.acc1).action_submit_approval()
    assert "submitter" in str(refused(c.env, lambda: b.with_user(c.acc1).action_approve()))
    b.with_user(c.acc3).action_approve()
    assert b.approval_state == "approved"


def test_m52_02_level_two_needs_manager(c):
    b = bill(c, 600000.0)
    b.with_user(c.acc1).action_submit_approval()
    b.with_user(c.acc2).action_approve()
    assert b.approval_levels_required == 2 and b.approval_state == "to_approve"
    assert refused(c.env, lambda: b.with_user(c.acc3).action_approve())
    b.with_user(c.mgr).action_approve()
    assert b.approval_state == "approved" and b.move_id.state == "posted"


def test_m52_03_accountant_cannot_write_approval_state(c):
    b = bill(c, 50000.0)
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"approval_state": "approved"}))
    assert b.approval_state == "draft"


def test_m52_04_submitted_by_cannot_be_rewritten(c):
    b = bill(c, 10000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"submitted_by": c.acc2.id}))
    assert refused(c.env, lambda: b.with_user(c.acc1).action_approve())
    assert b.submitted_by == c.acc1 and b.approval_state == "to_approve"


def test_m52_05_creator_cannot_approve_when_colleague_submits(c):
    b = bill(c, 10000.0, by=c.acc1)
    b.with_user(c.acc2).action_submit_approval()
    err = refused(c.env, lambda: b.with_user(c.acc1).action_approve())
    assert err and "Segregation of duties" in str(err)
    b.with_user(c.acc3).action_approve()  # a third person approves
    assert b.approval_state == "approved"


def test_m52_06_levels_are_rederived_not_trusted(c):
    """The forged write is refused; and even a stored count of 1 (forced by
    system code) does not let one accountant post a 600,000 bill."""
    b = bill(c, 600000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"approval_levels_required": 1}))
    b.sudo()._guarded().write({"approval_levels_required": 1})
    b.with_user(c.acc2).action_approve()
    assert b.approval_state == "to_approve" and not b.move_id
    assert b.approval_levels_required == 2


def test_m52_07_bill_type_locked_after_submission(c):
    """An unmatched PO bill is now refused at submission (G3-06). The lock is
    still shown on one that is approved, as bills approved before that gate
    are: system code sets the state."""
    b = bill(c, 80000.0, bill_type="po")
    assert b.match_state == "unmatched"
    assert "G3-06" in str(refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval()))
    b.sudo()._guarded().write({"approval_state": "approved"})
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"bill_type": "non_po"}))
    r = run(c)
    assert refused(c.env, lambda: r.with_user(c.acc1).action_propose())  # nothing payable


def test_m52_08_matrix_changes_need_a_second_manager(c):
    rules = c.env["fix.ap.approval.rule"].search([("company_id", "=", c.company.id)])
    level2 = rules.filtered(lambda r: r.level == 2)
    plain_group = c.env.ref("base.group_user")
    assert refused(c.env, lambda: level2.with_user(c.mgr).write({"group_id": plain_group.id}))
    assert refused(c.env, lambda: level2.with_user(c.mgr).write({"amount_min": 99999999}))
    assert refused(
        c.env,
        lambda: (
            c.env["fix.ap.approval.rule"]
            .with_user(c.mgr)
            .create({"name": "x", "level": 3, "amount_min": 0, "group_id": plain_group.id})
        ),
    )
    # proper path: mgr proposes, mgr2 confirms; the proposer cannot confirm
    Change = c.env["fix.ap.approval.rule.change"]
    change = Change.with_user(c.mgr).create(
        {"rule_id": level2.id, "amount_min": 750000.0, "reason": "CFO memo 2026-11: L2 from 750k"}
    )
    assert refused(c.env, lambda: change.with_user(c.mgr).action_apply())
    change.with_user(c.mgr2).action_apply()
    assert (level2.amount_min, level2.group_id, change.state) == (
        750000.0,
        c.env.ref(MGR),
        "applied",
    )
    # a matrix level is always decided by an accounting group, even with two
    # managers: refused at the proposal
    assert refused(
        c.env,
        lambda: Change.with_user(c.mgr).create(
            {"rule_id": level2.id, "group_id": plain_group.id, "reason": "probe"}
        ),
    )
    assert refused(c.env, lambda: Change.with_user(c.acc1).create({"reason": "x"}))


def test_m52_09_manager_can_clear_level_one(c):
    """M52-11: a pure accounting manager signs level 1 (one live accountant was
    the only level-1 approver); still one user, one level."""
    b = bill(c, 10000.0)
    b.with_user(c.acc1).action_submit_approval()
    b.with_user(c.mgr).action_approve()
    assert b.approval_state == "approved"
    big = bill(c, 600000.0)
    big.with_user(c.acc1).action_submit_approval()
    big.with_user(c.mgr).action_approve()
    assert refused(c.env, lambda: big.with_user(c.mgr).action_approve())  # one level each
    big.with_user(c.mgr2).action_approve()
    assert big.approval_state == "approved"
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.higher_level_may_approve_lower", "0")
    off = bill(c, 10000.0)
    off.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: off.with_user(c.mgr).action_approve())


def test_m52_06b_ruled_dofa_ladder_overrides_the_matrix_bands(c):
    """P1-1: the AP matrix bands are the default ladder; an M30 DOFA ladder
    ruled for fix.vendor.invoice decides how many levels an amount needs.

    Composition with the A12 M30-5 platform guard: a ladder may only target
    a model that carries fix.dofa.mixin, and fix.vendor.invoice does not
    (yet) — its approval-levels engine reads the ladder but the model has
    not adopted the mixin. Until it does (the recorded follow-up), the
    platform refuses the ruling and the matrix bands stand."""
    small = bill(c, 200000.0)
    small.with_user(c.acc1).action_submit_approval()
    assert small.approval_levels_required == 1  # matrix default: L2 from 500,000
    with pytest.raises(ValidationError, match="does not carry fix.dofa.mixin"):
        c.env["fix.dofa.ladder"].create(
            {
                "name": "AP bills - CFO ruling",
                "target_model": "fix.vendor.invoice",
                "basis": "ruling",
                "company_id": c.company.id,
                "threshold_ids": [
                    (0, 0, {"upper_bound": 100000.0, "tier": "tier_1"}),
                    (0, 0, {"upper_bound": 1e12, "tier": "tier_2"}),
                ],
            }
        )
    # the matrix default still governs
    b = bill(c, 200000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert b.approval_levels_required == 1
    b.with_user(c.acc2).action_approve()
    assert b.approval_state == "approved"


def test_m52_10_billing_user_cannot_create_or_approve(c):
    assert refused(c.env, lambda: bill(c, 1000.0, by=c.bill))
    b = bill(c, 1000.0)
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(c.bill).action_approve())


# ============================================================ TDS (M52-10)
def test_m52_11_tds_exempt_needs_a_certificate(c):
    b = bill(c, 100000.0, tds_exempt=True)
    assert b.tds_amount == 10000.0  # the tick alone exempts nothing
    err = refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    assert err and "exemption certificate" in str(err)
    c.profile.write(
        {
            "tds_exempt_certificate_ref": "NBR/EX/2026/0042",
            "tds_exempt_valid_until": "2027-06-30",
            "tds_exempt_attachment_ids": [(6, 0, _file(c.env, "ex.pdf", "EX-42").ids)],
        }
    )
    evidenced = bill(c, 100000.0, tds_exempt=True)
    assert evidenced.tds_amount == 0.0
    evidenced.with_user(c.acc1).action_submit_approval()


def test_m52_12_tds_gl_equals_withholding_line_no_tin(c):
    v = c.env["res.partner"].create({"name": "A08B2 No-TIN vendor"})
    b = approve(c, bill(c, 10000.0, vendor=v))
    gl_tds = -balance(c.env, c.a["tds_payable"])
    w = b.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
    # no PSR (s.142) and no TIN (s.143/163): 10% x 1.5 x 1.5, on BOTH records
    assert (b.tds_amount, w.amount, w.multiplier) == (2250.0, 2250.0, 2.25)
    assert gl_tds == 2250.0 and w.statutory_shortfall == 0.0


def test_m52_14_typed_psr_without_evidence_is_no_psr(c):
    v = c.env["res.partner"].create({"name": "A08B2 Non-filer"})
    prof = (
        c.env["fix.vendor.tax.profile"]
        .with_user(c.acc1)
        .create(
            {
                "partner_id": v.id,
                "taxpayer_type": "company",
                "tin": "111111111111",
                "psr_reference": "x",
                "psr_valid_until": "2099-12-31",
            }
        )
    )
    b = bill(c, 10000.0, vendor=v)
    assert (b.line_ids.tds_multiplier, b.tds_amount) == (1.5, 1500.0)
    prof.with_user(c.acc1).write(
        {"psr_attachment_ids": [(6, 0, _file(c.env(user=c.acc1.id), "p.pdf", "PSR").ids)]}
    )
    assert bill(c, 10000.0, vendor=v).tds_amount == 1000.0


# ============================================================ three-way match hand-off
def test_m52_13_duplicate_reference_refused(c):
    bill(c, 1000.0, ref="A08B2-DUP")
    d = bill(c, 1000.0, ref="a08b2-dup")
    assert refused(c.env, lambda: d.with_user(c.acc1).action_submit_approval())


def test_m52_15_blocked_bill_not_payable(c):
    """Blocked: not submitted (G3-06 at submission), and not paid even when
    approved, as a bill approved before that gate is (system code sets it)."""
    p = issued_po(c, 1.0, 1000.0, received=1.0)
    b = bill(c, 1500.0, po=p)
    assert b.match_state == "blocked"
    assert "G3-06" in str(refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval()))
    b.sudo()._guarded().write({"approval_state": "approved"})
    assert "G3-06" in str(refused(c.env, lambda: b.with_user(c.acc1).action_request_payment()))


def test_m52_16_plain_user_cannot_retype_po_to_match(c):
    p = issued_po(c, 10.0, 1000.0)
    b = bill(c, 1500.0, qty=10.0, po=p)  # blocked: it is not submitted (G3-06)
    assert b.match_state == "blocked"
    refused(
        c.env,
        lambda: p.line_ids.with_user(c.plain).write({"unit_price": 1500.0, "qty_received": 10.0}),
    )
    b.invalidate_recordset()
    assert b.match_state == "blocked"


def test_m52_17_match_needs_a_posted_receipt(c):
    p = issued_po(c, 5.0, 2000.0)  # sent, nothing received
    assert bill(c, 2000.0, qty=5.0, po=p).match_state == "blocked"
    p2 = issued_po(c, 5.0, 2000.0, received=5.0)
    assert bill(c, 2000.0, qty=5.0, po=p2).match_state == "matched"


def test_m52_18_vendor_creator_cannot_approve_vendor_bill(c):
    accpm = _user(c.env, "a08b2_accpm", [ACC, "base.group_partner_manager"])
    v = c.env["res.partner"].with_user(accpm).create({"name": "A08B2 Vendor made by accpm"})
    b = bill(c, 10000.0, vendor=v)
    b.with_user(c.acc1).action_submit_approval()
    err = refused(c.env, lambda: b.with_user(accpm).action_approve())
    assert err and "SOD-01" in str(err)
    b.with_user(c.acc2).action_approve()
    assert b.approval_state == "approved"


def test_m52_19_po_raiser_receiver_and_approver_never_one_user(c):
    """SOD-02: the buyer who raised the PO cannot also receive it (A06) nor,
    having raised and received it, approve its bill."""
    buyer = _user(c.env, "a08b2_buyer", [ACC, BUYER])
    p = issued_po(c, 4.0, 2500.0, by=buyer)
    assert p.create_uid == buyer
    assert refused(c.env, lambda: p.with_user(buyer).action_record_receipt({p.line_ids.id: 4.0}))
    p.sudo().action_record_receipt({p.line_ids.id: 4.0})
    receipt = p.sudo().receipt_ids.sorted("id")[-1]
    receipt._guarded().write({"receiver_id": buyer.id})  # as if he had received it
    for line in receipt.line_ids:
        c.env["fix.procurement.inspection"].create(
            {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
        ).action_confirm()
    b = bill(c, 2500.0, qty=4.0, po=p)
    assert b.match_state == "matched"
    b.with_user(c.acc1).action_submit_approval()
    assert refused(c.env, lambda: b.with_user(buyer).action_approve())
    b.with_user(c.acc2).action_approve()
    assert b.approval_state == "approved"


# ============================================================ payment runs (F2, M52-1/-4/-6)
def test_m52_20_run_state_cannot_be_forged(c):
    approve(c, bill(c, 10000.0))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    assert refused(c.env, lambda: r.with_user(c.acc1).write({"state": "approved"}))
    assert refused(c.env, lambda: r.with_user(c.acc1).action_release())
    assert r.state == "proposed" and not r.line_ids.execution_id


def test_m52_21_preparer_cannot_be_rewritten_or_approve(c):
    approve(c, bill(c, 10000.0))
    r = run(c, by=c.mgr)
    r.with_user(c.mgr).action_propose()
    r.with_user(c.mgr).action_submit()
    assert refused(c.env, lambda: r.with_user(c.mgr).write({"prepared_by": c.acc1.id}))
    assert refused(c.env, lambda: r.with_user(c.mgr).action_approve())
    r.with_user(c.mgr2).action_approve()
    assert r.approved_by == c.mgr2


def test_m52_22_payee_bank_cannot_be_swapped(c):
    r = approved_run(c)
    line = r.line_ids
    assert refused(c.env, lambda: line.with_user(c.acc1).write({"bank_account_id": c.abank.id}))
    assert refused(c.env, lambda: r.with_user(c.acc2).action_release()) is None
    assert line.execution_id.sudo().partner_bank_id == c.vbank
    # before approval too: a line pays the vendor's own account only
    approve(c, bill(c, 5000.0))
    r2 = run(c)
    r2.with_user(c.acc1).action_propose()
    assert refused(
        c.env, lambda: r2.line_ids.with_user(c.acc1).write({"bank_account_id": c.abank.id})
    )


def test_m52_23_accountant_cannot_edit_vendor_bank(c):
    approved_run(c)
    assert refused(c.env, lambda: c.vbank.with_user(c.acc1).write({"acc_number": "SWAP-777"}))


def test_m52_23b_vendor_bank_edited_after_approval_blocks_release(c):
    pm = _user(c.env, "a08b2_pm", ["base.group_partner_manager"])
    r = approved_run(c)
    # A12 M64 refuses this edit first when its direct-edit block is on; this
    # test pins the A08 layer behind it, so that layer must see the edit.
    c.env["ir.config_parameter"].sudo().set_param("fix.mdm.enforce_direct_edit_block", "off")
    c.vbank.with_user(pm).write({"acc_number": "A08B2-SWAPPED-888"})
    assert not c.vbank.fix_confirmed and c.vbank.fix_changed_by_id == pm
    err = refused(c.env, lambda: r.with_user(c.acc2).action_release())
    assert err and not r.line_ids.execution_id
    with pytest.raises(UserError, match=r"not confirmed|changed after"):
        c.env["res.partner.bank"]._fix_assert_payable_bank(c.vbank)
    # the changer cannot re-confirm it; someone else verifies it again
    change = (
        c.env["fix.payee.bank.change"]
        .with_user(c.acc3)
        .create(
            {
                "partner_id": c.vendor.id,
                "partner_bank_id": c.vbank.id,
                "acc_number": "A08B2-SWAPPED-888",
                "verification_ref": "Called vendor CFO on file number",
            }
        )
    )
    change.with_user(c.acc3).action_propose()
    assert refused(c.env, lambda: change.with_user(c.acc3).action_confirm())
    change.with_user(c.mgr2).action_confirm()
    assert c.env["res.partner.bank"]._fix_assert_payable_bank(c.vbank)
    # the run approved the OLD number: still refused, the approval is void
    assert refused(c.env, lambda: r.with_user(c.acc2).action_release())


def test_m52_24_bill_cannot_be_added_after_approval(c):
    b1 = approve(c, bill(c, 10000.0))
    r = approved_run(c, b1)
    b2 = approve(c, bill(c, 200000.0))
    assert refused(c.env, lambda: r.line_ids.with_user(c.acc1).write({"bill_ids": [(4, b2.id)]}))
    assert refused(
        c.env,
        lambda: (
            c.env["fix.payment.run.line"]
            .with_user(c.acc1)
            .create(
                {
                    "run_id": r.id,
                    "partner_id": c.vendor.id,
                    "operating_unit_id": c.ou.id,
                    "bill_ids": [(6, 0, b2.ids)],
                    "bank_account_id": c.vbank.id,
                }
            )
        ),
    )
    r.with_user(c.acc2).action_release()
    assert r.line_ids.execution_id.sudo().amount == 9000.0


def test_m52_25_bill_is_never_paid_twice(c):
    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    r.with_user(c.acc2).action_release()
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"payment_state": "not_paid"}))
    # even if system code resets the field, the payment lock keeps it out
    b.sudo()._guarded().write({"payment_state": "not_paid"})
    assert refused(c.env, lambda: run(c).with_user(c.acc1).action_propose())
    assert refused(c.env, lambda: b.with_user(c.acc1).action_request_payment())
    Lock = c.env["fix.ap.bill.payment"].sudo()
    with pytest.raises(Exception), c.env.cr.savepoint():  # noqa: B017 - the unique index
        Lock.create({"company_id": c.company.id, "bill_id": b.id, "amount": 1.0})
        c.env.flush_all()


def test_m52_25b_failed_payment_returns_the_bill(c):
    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    r.with_user(c.acc2).action_release()
    treasury_fail(c, r.line_ids.execution_id)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (b.payment_state, r.line_ids.state) == ("not_paid", "failed")
    r2 = approved_run(c, b)
    assert b in r2.line_ids.bill_ids


def test_m52_25c_prepared_waits_and_bounce_after_clearing_is_reversed(c):
    """B1 states: a prepared instruction keeps the line waiting; a payment
    failed AFTER execution (bounce after clearing) reverses the run's own
    payment entry (source_posts_gl) and reopens the bill."""
    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    r.with_user(c.acc2).action_release()
    ex = r.line_ids.execution_id.sudo()
    ex._guarded().write({"state": "prepared"})  # treasury (M50), not under test
    r.with_user(c.acc2).action_sync_bank_status()
    assert (r.line_ids.state, b.payment_state) == ("sent", "in_run")
    treasury_execute(c, ex)
    r.with_user(c.acc2).action_sync_bank_status()
    assert (b.payment_state, r.state) == ("paid", "done")
    ap0 = balance(c.env, c.ap)
    treasury_fail(c, ex)  # the bank returned it after clearing
    r.with_user(c.acc2).action_sync_bank_status()
    line = r.line_ids
    assert (line.state, b.payment_state) == ("failed", "not_paid")
    assert line.reversal_move_id.state == "posted"
    assert balance(c.env, c.ap) == ap0 - 9000.0  # the liability is open again
    r.with_user(c.acc2).action_sync_bank_status()  # idempotent
    assert len(line.reversal_move_id) == 1
    assert b in approved_run(c, b).line_ids.bill_ids


def test_m52_25d_cancelled_instruction_returns_the_bill(c):
    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    r.with_user(c.acc2).action_release()
    r.line_ids.execution_id.sudo()._guarded().write({"state": "cancelled"})
    r.with_user(c.acc2).action_sync_bank_status()
    assert (r.line_ids.state, b.payment_state, r.state) == ("failed", "not_paid", "done")


def test_m52_53b_disbursement_bounce_is_reversed(c):
    adv = disbursed_advance(c)
    assert balance(c.env, c.a["employee_advance"]) == 5000.0
    treasury_fail(c, adv.execution_id)
    adv.with_user(c.acc1).action_sync_disbursement()
    assert adv.state == "approved" and adv.disbursement_reversal_move_id.state == "posted"
    assert balance(c.env, c.a["employee_advance"]) == 0.0
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_settle())


def test_executions_only_through_the_treasury_contract(c):
    """B1: an execution is requested through _fix_request_payment; a direct
    create by a finance user is refused."""
    adv = advance(c, c.acc2, c.emp_plain, 5000.0)
    adv.with_user(c.acc1).action_approve()
    ex = adv.execution_id.sudo()
    assert (ex.source_model, ex.source_id, ex.amount, ex.state) == (
        "fix.employee.advance",
        adv.id,
        5000.0,
        "pending",
    )
    assert refused(
        c.env,
        lambda: (
            c.env["fix.payment.execution"]
            .with_user(c.acc1)
            .create(
                {
                    "source_model": "fix.employee.advance",
                    "source_id": adv.id + 100000,
                    "payee": "x",
                    "amount": 1.0,
                    "operating_unit_id": c.ou.id,
                    "source_posts_gl": True,
                }
            )
        ),
    )


def test_m52_26_bill_without_posted_liability_is_never_paid(c):
    b = bill(c, 30000.0)
    assert refused(c.env, lambda: b.with_user(c.acc1).write({"approval_state": "approved"}))
    b.sudo()._guarded().write({"approval_state": "approved"})  # system-forged, no GL
    r = run(c)
    assert refused(c.env, lambda: r.with_user(c.acc1).action_propose())
    assert refused(c.env, lambda: b.with_user(c.acc1).action_request_payment())


def test_m52_27_vendor_note_creator_cannot_be_forged(c):
    b = approve(c, bill(c, 20000.0))
    note = (
        c.env["fix.vendor.note"]
        .with_user(c.acc1)
        .create(
            {
                "invoice_id": b.id,
                "note_type": "increase",
                "mushak_ref": "68-A08",
                "note_date": "2026-10-20",
                "amount": 15000.0,
            }
        )
    )
    assert refused(c.env, lambda: note.with_user(c.acc1).write({"created_by": c.acc2.id}))
    assert refused(c.env, lambda: note.with_user(c.acc1).action_approve())
    assert refused(c.env, lambda: note.with_user(c.acc1).write({"state": "approved"}))
    note.with_user(c.acc2).action_approve()
    assert note.state == "approved" and note.move_id.state == "posted"
    assert refused(c.env, lambda: note.with_user(c.acc2).write({"amount": 1.0}))


def test_m52_28_billing_user_cannot_release(c):
    r = approved_run(c)
    assert refused(c.env, lambda: r.with_user(c.bill).action_release())


def test_m52_29_preparer_and_approver_cannot_release(c):
    r = approved_run(c)
    err = refused(c.env, lambda: r.with_user(c.acc1).action_release())
    assert err and "BRU-APE-06" in str(err)
    assert refused(c.env, lambda: r.with_user(c.mgr).action_release())
    r.with_user(c.acc2).action_release()
    assert r.state == "released"


# ============================================================ P03 surface (M52-13)
def test_m52_30_surfaces_declare_writable_and_forms_offer_no_workflow_field(c):
    from odoo.addons.cd_p03_portal.controllers import (
        a08,  # noqa: F401 - fills writable
        form_fields,
    )
    from odoo.addons.cd_p03_portal.controllers.a08 import m52 as surf

    missing = [m for m, conf in surf.SURFACES.items() if "writable" not in conf]
    assert not missing
    offered = form_fields.editable_by_model()
    for model in surf.SURFACES:
        Model = c.env[model]
        if not hasattr(Model, "_fix_guarded_fields"):
            continue
        bad = offered.get(model, set()) & Model._fix_guarded_fields()
        assert not bad, "%s form offers workflow fields %s" % (model, bad)


def test_m52_31_p03_write_bill_approved_refused(c, p03):
    b = bill(c, 25000.0)
    p03.write(
        c.acc1, model="fix.vendor.invoice", record_id=b.id, values={"approval_state": "approved"}
    )
    b.invalidate_recordset()
    assert b.approval_state == "draft"


def test_m52_32_p03_write_run_and_claim_state_refused(c, p03):
    approve(c, bill(c, 10000.0))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    p03.write(c.acc1, model="fix.payment.run", record_id=r.id, values={"state": "approved"})
    cl = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.hotel.id, "unit_amount": 900.0, "date": D}]
    )
    p03.write(c.plain, model="fix.expense.claim", record_id=cl.id, values={"state": "submitted"})
    r.invalidate_recordset()
    cl.invalidate_recordset()
    assert (r.state, cl.state) == ("proposed", "draft")


# ============================================================ expense claims (F6, M52-7)
def test_m52_40_plain_user_cannot_write_claim_approval(c):
    cl = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": 500.0, "date": D}]
    )
    assert refused(c.env, lambda: cl.with_user(c.plain).write({"state": "approved"}))
    assert refused(c.env, lambda: cl.with_user(c.plain).write({"approved_by": c.acc1.id}))


def test_m52_41_policy_cannot_be_skipped_by_writing_state(c):
    cl = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.hotel.id, "unit_amount": 9000.0, "date": D}]
    )
    assert refused(c.env, lambda: cl.with_user(c.plain).action_submit())
    assert refused(c.env, lambda: cl.with_user(c.plain).write({"state": "submitted"}))
    assert cl.state == "draft"


def test_m52_42_lineless_claim_refused(c):
    assert refused(c.env, lambda: claim(c, c.plain, c.emp_plain, None, amount=24999.0))
    cl = claim(c, c.plain, c.emp_plain, None)
    err = refused(c.env, lambda: cl.with_user(c.plain).action_submit())
    assert err and "at least one expense line" in str(err)


def test_m52_43_split_claims_are_summed_for_the_threshold(c):
    cls = [
        claim(
            c,
            c.plain,
            c.emp_plain,
            [
                {
                    "category_id": c.other.id,
                    "unit_amount": 20000.0,
                    "date": D,
                    "receipt_attachment_ids": [
                        (6, 0, _file(c.env(user=c.plain.id), "r%d.pdf" % i, "RCPT-%d" % i).ids)
                    ],
                }
            ],
        )
        for i in range(2)
    ]
    for cl in cls:
        cl.with_user(c.plain).action_submit()
    err = refused(c.env, lambda: cls[1].with_user(c.acc1).action_approve())
    assert err and "40000.00" in str(err)
    cls[0].with_user(c.mgr).action_approve()
    cls[1].with_user(c.mgr).action_approve()
    assert [cl.state for cl in cls] == ["approved", "approved"]


def test_m52_44_claim_state_cannot_be_forged_to_settle_an_advance(c):
    adv = disbursed_advance(c)
    cl = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.other.id, "unit_amount": 5000.0, "date": D}],
        advance_id=adv.id,
    )
    assert refused(c.env, lambda: cl.with_user(c.acc1).write({"state": "approved"}))
    cl.sudo()._guarded().write({"state": "approved"})  # system-forged, no GL
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_settle())
    assert (adv.settled_amount, adv.state) == (0.0, "disbursed")


def test_m52_45_claim_amount_cannot_be_raised(c):
    adv = disbursed_advance(c)
    cl = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.other.id, "unit_amount": 1000.0, "date": D}],
        advance_id=adv.id,
    )
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    assert refused(c.env, lambda: cl.with_user(c.plain).write({"amount": 5000.0}))
    assert refused(c.env, lambda: cl.line_ids.with_user(c.plain).write({"unit_amount": 5000.0}))
    adv.invalidate_recordset()
    assert (cl.amount, adv.balance) == (1000.0, 4000.0)


def test_m52_46_plain_user_cannot_touch_colleagues_claims(c):
    cl = claim(c, c.p2, c.emp_p2, [{"category_id": c.other.id, "unit_amount": 800.0, "date": D}])
    cl.with_user(c.p2).action_submit()
    assert refused(c.env, lambda: cl.with_user(c.plain).action_reject())
    cl2 = claim(c, c.p2, c.emp_p2, [{"category_id": c.other.id, "unit_amount": 800.0, "date": D}])
    assert refused(
        c.env,
        lambda: cl2.with_user(c.plain).write(
            {"description": "edited", "employee_id": c.emp_plain.id}
        ),
    )
    assert not c.env["fix.expense.claim"].with_user(c.plain).search([("id", "in", (cl | cl2).ids)])
    assert refused(c.env, lambda: cl.with_user(c.p2).action_reject())  # nor reject his own


def test_m52_47_plain_user_cannot_file_for_a_colleague(c):
    err = refused(
        c.env,
        lambda: claim(
            c, c.plain, c.emp_p2, [{"category_id": c.other.id, "unit_amount": 800.0, "date": D}]
        ),
    )
    assert err
    own = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": 800.0, "date": D}]
    )
    own.with_user(c.plain).action_submit()  # proper path: his own claim
    assert own.state == "submitted"


def test_m52_48_accountant_cannot_approve_a_claim_he_raised(c):
    cl = claim(
        c, c.acc1, c.emp_nouser, [{"category_id": c.other.id, "unit_amount": 900.0, "date": D}]
    )
    cl.with_user(c.acc1).action_submit()
    assert refused(c.env, lambda: cl.with_user(c.acc1).write({"submitted_by": c.acc2.id}))
    assert refused(c.env, lambda: cl.with_user(c.acc1).action_approve())
    cl.with_user(c.acc2).action_approve()
    assert cl.approved_by == c.acc2


def test_m52_48b_line_manager_approves_before_finance(c):
    lm = _user(c.env, "a08b2_linemgr")
    boss = c.env["hr.employee"].create({"name": "A08B2 Line Manager", "user_id": lm.id})
    c.emp_p2.parent_id = boss
    cl = claim(c, c.p2, c.emp_p2, [{"category_id": c.other.id, "unit_amount": 700.0, "date": D}])
    cl.with_user(c.p2).action_submit()
    err = refused(c.env, lambda: cl.with_user(c.acc1).action_approve())
    assert err and "line manager" in str(err)
    assert refused(c.env, lambda: cl.with_user(c.p2).action_manager_approve())
    cl.with_user(lm).action_manager_approve()
    cl.with_user(c.acc1).action_approve()
    assert (cl.manager_approved_by, cl.approved_by, cl.state) == (lm, c.acc1, "approved")


def test_m52_49_same_receipt_claimed_once(c):
    def one():
        cl = claim(
            c,
            c.plain,
            c.emp_plain,
            [
                {
                    "category_id": c.hotel.id,
                    "unit_amount": 3500.0,
                    "date": D,
                    "receipt_attachment_ids": [
                        (6, 0, _file(c.env(user=c.plain.id), "hotel.pdf", "HOTEL-RECEIPT").ids)
                    ],
                }
            ],
        )
        cl.with_user(c.plain).action_submit()
        cl.with_user(c.acc1).action_approve()
        return cl

    first = one()
    assert first.state == "approved"
    err = refused(c.env, one)
    assert err and "already claimed" in str(err)


# ============================================================ advances (M52-8)
def test_m52_50_advance_requester_cannot_approve(c):
    adv = advance(c, c.acc1, c.emp_plain)
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_approve())


def test_m52_51_advance_requester_cannot_be_forged(c):
    adv = advance(c, c.acc1, c.emp_nouser, 40000.0)
    assert refused(c.env, lambda: adv.with_user(c.acc1).write({"requested_by": c.acc2.id}))
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_approve())
    assert not adv.execution_id


def test_m52_52_advance_amount_pinned_after_approval(c):
    adv = advance(c, c.acc2, c.emp_plain, 5000.0)
    adv.with_user(c.acc1).action_approve()
    assert adv.approved_amount == 5000.0 and adv.execution_id.sudo().amount == 5000.0
    assert refused(c.env, lambda: adv.with_user(c.acc1).write({"amount": 50000.0}))
    treasury_execute(c, adv.execution_id)
    adv.with_user(c.acc1).action_confirm_disbursement()
    assert adv.disbursement_move_id.amount_total == 5000.0


def test_m52_53_advance_state_cannot_be_forged_disbursed(c):
    adv = advance(c, c.acc2, c.emp_plain, 30000.0)
    adv.with_user(c.acc1).action_approve()
    assert refused(c.env, lambda: adv.with_user(c.acc1).write({"state": "disbursed"}))
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_confirm_disbursement())
    assert adv.state == "approved" and not adv.disbursement_move_id


def test_m52_54_advance_settles_once(c):
    adv = disbursed_advance(c)
    cl = claim(
        c,
        c.plain,
        c.emp_plain,
        [{"category_id": c.other.id, "unit_amount": 3000.0, "date": D}],
        advance_id=adv.id,
    )
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    adv.with_user(c.acc1).action_settle()
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_settle())
    assert balance(c.env, c.a["employee_advance"]) == 2000.0
    assert balance(c.env, c.a["employee_payable"]) == 0.0
    assert (adv.settled_posted, adv.balance) == (3000.0, 2000.0)


def test_m52_55_second_advance_blocked_while_first_open(c):
    a1 = advance(c, c.acc2, c.emp_plain, 5000.0)
    a1.with_user(c.acc1).action_approve()
    a2 = advance(c, c.acc2, c.emp_plain, 5000.0)
    err = refused(c.env, lambda: a2.with_user(c.acc1).action_approve())
    assert err and a1.name in str(err)


def test_m52_56_payroll_recovery_requested_once_and_confirmed(c):
    adv = disbursed_advance(c, recovery_method="payroll")
    adv.with_user(c.acc1).action_record_recovery()
    assert adv.recovery_state == "requested" and adv.recovery_requested_amount == 5000.0
    assert refused(c.env, lambda: adv.with_user(c.acc1).action_record_recovery())
    assert refused(
        c.env, lambda: adv.with_user(c.plain).action_confirm_payroll_recovery(5000.0, "PS/1")
    )
    # payroll (A09) confirms the deduction it made
    adv.sudo().action_confirm_payroll_recovery(5000.0, "PAYSLIP/2026/11/0042")
    assert (adv.recovered_amount, adv.balance, adv.state) == (5000.0, 0.0, "settled")
    assert balance(c.env, c.a["employee_advance"]) == 0.0


def test_m52_56b_payroll_recovery_has_a_registered_consumer(c):
    """Wiring; the behaviour is test_a08_m52_operability's
    test_m52_8_payroll_recovery_from_the_screen."""
    consumers = (
        c.env["fix.event.consumer"]
        .sudo()
        .search_count([("event_type", "=", "advance.recovery_requested")])
    )
    assert consumers


# ============================================================ wiring (M52-9)
def test_m52_60_payment_requested_reaches_treasury(c):
    """An approved claim's payment.requested is consumed by M50's registered
    consumer into a pinned execution for the claim amount."""
    cl = claim(
        c, c.plain, c.emp_plain, [{"category_id": c.other.id, "unit_amount": 700.0, "date": D}]
    )
    cl.with_user(c.plain).action_submit()
    cl.with_user(c.acc1).action_approve()
    Outbox = c.env["fix.event.outbox"].sudo()
    event = Outbox.search(
        [
            ("event_type", "=", "payment.requested"),
            ("aggregate", "=", "fix.expense.claim"),
            ("aggregate_id", "=", cl.id),
        ]
    )
    payload = json.loads(event.payload)
    assert (payload["amount"], payload["approved_by"]) == (700.0, c.acc1.id)
    subs = c.env["fix.event.consumer"].sudo().search([("event_type", "=", "payment.requested")])
    assert subs, "M50 registers a payment.requested consumer (B1 contract)"
    for sub in subs:
        assert Outbox._relay_deliver(sub, event) == ""
    ex = (
        c.env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", "fix.expense.claim"), ("source_id", "=", cl.id)])
    )
    assert len(ex) == 1 and ex.amount == 700.0


# ============================================================ S1 bank master
def test_s1_bank_confirmation_is_system_set_and_two_person(c):
    nb = c.env["res.partner.bank"].create({"partner_id": c.vendor.id, "acc_number": "A08B2-NEW-1"})
    assert not nb.fix_confirmed
    assert refused(
        c.env, lambda: nb.write({"fix_confirmed": True})
    )  # not even admin code via write
    pm = _user(c.env, "a08b2_pm2", ["base.group_partner_manager"])
    assert refused(c.env, lambda: nb.with_user(pm).write({"fix_confirmed": True}))
    change = (
        c.env["fix.payee.bank.change"]
        .with_user(c.acc3)
        .create({"partner_id": c.vendor.id, "partner_bank_id": nb.id, "acc_number": "A08B2-NEW-1"})
    )
    err = refused(c.env, lambda: change.with_user(c.acc3).action_propose())
    assert err and "call-back" in str(err)
    change.with_user(c.acc3).write({"verification_ref": "Called on file number"})
    change.with_user(c.acc3).action_propose()
    assert refused(c.env, lambda: change.with_user(c.acc3).write({"acc_number": "OTHER"}))
    assert refused(c.env, lambda: change.with_user(c.acc1).action_confirm())  # not a manager
    change.with_user(c.mgr).action_confirm()
    assert nb.fix_confirmed and nb.fix_confirmed_by_id == c.mgr
    assert nb.fix_verification_ref == "Called on file number"


def test_s1_cooling_off_before_first_payment(c):
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.bank_cooling_off_hours", "48")
    with pytest.raises(UserError, match="cooling-off"):
        c.env["res.partner.bank"]._fix_assert_payable_bank(c.vbank)
    approve(c, bill(c, 10000.0))
    r = run(c)
    r.with_user(c.acc1).action_propose()
    # the payee drops out of the run with the reason, so nothing is payable yet
    assert "cooling-off" in r.line_ids.skip_reason
    assert refused(c.env, lambda: r.with_user(c.acc1).action_submit())
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.bank_cooling_off_hours", "0")
    r.with_user(c.acc1).action_propose()  # the wait is over: propose again
    r.with_user(c.acc1).action_submit()
    assert r.state == "to_approve"


def test_s1_supplier_accounts_go_through_m42(c):
    if "fix.supplier" not in c.env:
        pytest.skip("cd_vendor_portal not installed")
    c.env["fix.supplier"].create(
        {"name": c.vendor.name, "partner_id": c.vendor.id, "status": "active"}
    )
    change = (
        c.env["fix.payee.bank.change"]
        .with_user(c.acc3)
        .create(
            {
                "partner_id": c.vendor.id,
                "acc_number": "A08B2-SUP-2",
                "verification_ref": "Called",
            }
        )
    )
    err = refused(c.env, lambda: change.with_user(c.acc3).action_propose())
    assert err and "M42 supplier" in str(err)


def test_kpis_and_reports_read_as_the_caller(c):
    from odoo.addons.cd_p03_portal.controllers.a08 import m52 as surf

    b = approve(c, bill(c, 10000.0))
    r = approved_run(c, b)
    out = surf.kpis(c.env(user=c.acc1.id))
    assert out["vendor_bills_open"] >= 1 and out["match_exceptions"] is not None
    assert out["expense_claims_pending"] is not None
    # the run summary read every run as superuser: a plain user (no AP role)
    # now gets nothing, an accountant gets the runs of his companies
    assert surf.payment_run_summary(c.env(user=c.plain.id))["rows"] == []
    names = [row["run"] for row in surf.payment_run_summary(c.env(user=c.acc1.id))["rows"]]
    assert r.name in names
    assert surf.tds_register(c.env(user=c.plain.id))["rows"] == []


# ============================================================ B5 hand-offs (M51 / M49)
def _cwip(c, with_account=True):
    Account = c.env["account.account"]
    n = next(_SEQ)
    cwip_acc = Account.create(
        {
            "code": "9901%02d" % (n % 100),
            "name": "Test CWIP %d" % n,
            "account_type": "asset_non_current",
            "company_ids": [(6, 0, [c.company.id])],
        }
    )
    cat = c.env["fix.asset.category"].create(
        {
            "company_id": c.company.id,
            "name": "A08B2 Workshop equipment %d" % n,
            "code": "B2W%d" % n,
            "cwip_account_id": cwip_acc.id if with_account else False,
        }
    )
    cw = c.env["fix.cwip.entry"].create(
        {"company_id": c.company.id, "name": "A08B2 Bench line %d" % n, "category_id": cat.id}
    )
    return cw, cwip_acc


def _capital_bill(c, cw, price):
    b = bill(c, price)
    b.line_ids.write({"cwip_id": cw.id})
    return b


def test_b5_capital_bill_books_posted_cost_to_cwip(c):
    """M49-3: a capital bill line debits the project's CWIP account and the
    posted item is booked to the project; CWIP cost comes from posted bills."""
    cw, cwip_acc = _cwip(c)
    b = approve(c, _capital_bill(c, cw, 90000.0))
    item = b.move_id.line_ids.filtered(lambda ml: ml.account_id == cwip_acc)
    assert item.debit == 90000.0
    assert cw.cost_line_ids == item and cw.amount == 90000.0
    with pytest.raises(UserError), c.env.cr.savepoint():  # booked once
        cw.sudo()._fix_book_cost(item)


def test_b5_capital_line_needs_an_open_project_with_a_cwip_account(c):
    cw, _acc = _cwip(c, with_account=False)
    b = _capital_bill(c, cw, 5000.0)
    err = refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    assert err and "CWIP account" in str(err)


def test_b5_vendor_note_credit_links_the_original_6_3_credit(c):
    b = bill(c, 20000.0, vat_amount=3000.0, supplier_mushak_no="63-B2-1")
    c.profile.bin = "9876543210123"
    approve(c, b)
    assert b.input_credit_id
    note = (
        c.env["fix.vendor.note"]
        .with_user(c.acc1)
        .create(
            {
                "invoice_id": b.id,
                "note_type": "increase",
                "mushak_ref": "68-B2-1",
                "note_date": "2026-10-20",
                "amount": 1000.0,
                "vat_amount": 150.0,
            }
        )
    )
    note.with_user(c.acc2).action_approve()
    assert note.input_credit_id.original_credit_id == b.input_credit_id


def test_b5_certificate_names_a_bill_only_for_ap_sources(c):
    Cert = c.env["fix.withholding.certificate"]
    assert not Cert._fields["vendor_invoice_id"].required
    with pytest.raises(ValidationError, match="names the vendor bill"):
        Cert.new({"source_model": False})._check_vendor_invoice()
    with pytest.raises(ValidationError, match="names the vendor bill"):
        Cert.new({"source_model": "fix.vendor.invoice"})._check_vendor_invoice()
    Cert.new({"source_model": "fix.tradein", "source_ref": "TRADEIN-1"})._check_vendor_invoice()


def test_b5_deductions_go_through_the_posted_liability(c):
    """M51-8: the bill's deductions are recorded against its posted entry;
    a typed deduction is refused."""
    b = approve(c, bill(c, 10000.0))
    w = b.withholding_line_ids
    assert w and all(line.move_id == b.move_id for line in w)
    vals = {
        "tax_kind": "tds",
        "rate_id": w.rate_id.id,
        "partner_id": c.vendor.id,
        "document_date": D,
        "base_amount": 1.0,
        "amount": 0.1,
    }
    assert refused(c.env, lambda: c.env["fix.withholding.line"].with_user(c.acc1).create(vals))
