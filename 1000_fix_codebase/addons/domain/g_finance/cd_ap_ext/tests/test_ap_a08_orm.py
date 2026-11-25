# cd_ap_ext — A08 M52 live-ORM behaviour (CD-M52-01): vendor tax profile and
# the effective-dated TDS/VDS, the amount-based approval matrix with
# segregation of duties and GL posting, Mushak 6.7/6.8 vendor notes, payment
# runs creating fix.payment.execution rows, the expense policy, per-diem /
# mileage rates, and employee advances with settlement and recovery.
from __future__ import annotations

import base64
import itertools
import json
from datetime import date

import pytest
from odoo.addons.cd_ap_ext.tests.p2p_fixtures import register_supplier
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial, pytest.mark.tax]

_SEQ = itertools.count(1)


def _user(env, ou, *groups):
    n = next(_SEQ)
    return env["res.users"].create(
        {
            "name": "A08 AP User %d" % n,
            "login": "a08-ap-%d@test.local" % n,
            "group_ids": [(6, 0, [env.ref(g).id for g in ("base.group_user", *groups)])],
            "company_id": env.company.id,
            "company_ids": [(6, 0, [env.company.id])],
            "operating_unit_ids": [(6, 0, [ou.id])],
            "default_operating_unit_id": ou.id,
        }
    )


def _evidence(env, name):
    return env["ir.attachment"].create(
        {"name": name, "datas": base64.b64encode(name.encode()).decode()}
    )


def _confirm_bank(a, account):
    """A08 S1: a payee account is paid only after a second person confirms it
    (call-back recorded); a superuser-created account is not confirmed. An
    M42 supplier's account is confirmed through the A06 supplier bank-change
    request, any other payee's through fix.payee.bank.change."""
    env, partner = a["env"], account.partner_id
    supplier = (
        env["fix.supplier"].search([("partner_id", "=", partner.id)], limit=1)
        if "fix.supplier" in env
        else None
    )
    if supplier:
        steward = _user(env, a["ou"], "cd_vendor_portal.group_fix_supplier_steward")
        approver = _user(env, a["ou"], "cd_vendor_portal.group_fix_supplier_approver")
        change = (
            env["fix.supplier.bank.change"]
            .with_user(steward)
            .create(
                {
                    "supplier_id": supplier.id,
                    "acc_number": account.acc_number,
                    "routing_number": account.fix_routing_number or False,
                    "verification_ref": "Called the supplier on the number in its signed form",
                    "evidence_ref": "dms://bank/a08",
                }
            )
        )
        change.with_user(steward).action_propose()
        change.with_user(approver).action_confirm()
        return account
    change = (
        env["fix.payee.bank.change"]
        .with_user(a["acc3"])
        .create(
            {
                "partner_id": partner.id,
                "partner_bank_id": account.id,
                "acc_number": account.acc_number,
                "routing_number": account.fix_routing_number or False,
                "verification_ref": "Called the vendor on the number in its signed form",
            }
        )
    )
    change.with_user(a["acc3"]).action_propose()
    change.with_user(a["mgr2"]).action_confirm()
    return account


def _treasury_executed(execution, ref):
    """Treasury (M50), not under test here: the bank executed the instruction.
    (cd_cash_position's own tests cover prepare / authorise / release.)"""
    execution.sudo()._guarded().write(
        {
            "state": "executed",
            "bank_reference": ref,
            "confirmation_source": "bank_reference",
        }
    )


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


@pytest.fixture
def a08(odoo_env):
    """GL roles configured on dedicated test accounts, three accounting users
    (two accountants, one manager), a filer vendor and a product."""
    env = odoo_env
    company = env.company
    ou = env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    Account = env["account.account"]

    def acc(code, name, kind):
        found = Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        return found or Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [company.id])],
            }
        )

    accounts = {
        "vat_input": acc("990131", "Test input VAT", "asset_current"),
        "vds_payable": acc("990252", "Test VDS payable", "liability_current"),
        "tds_payable": acc("990253", "Test TDS payable", "liability_current"),
        "employee_payable": acc("990230", "Test employee payable", "liability_current"),
        "employee_advance": acc("990141", "Test employee advances", "asset_current"),
        "expense": acc("990600", "Test expense", "expense"),
    }
    icp = env["ir.config_parameter"].sudo()
    for param, code in (
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_tax_engine_bd.account_code.vds_payable", "990252"),
        ("cd_tax_engine_bd.account_code.tds_payable", "990253"),
        ("cd_ap_ext.account_code.employee_payable", "990230"),
        ("cd_ap_ext.account_code.employee_advance", "990141"),
        ("cd_ap_ext.account_code.expense", "990600"),
    ):
        icp.set_param(param, code)
    bank = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
    )
    icp.set_param("cd_ap_ext.payment_journal_code", bank.code)
    vendor = env["res.partner"].create({"name": "Padma Spares Ltd."})
    register_supplier(env, vendor)  # A06 P09: non-PO bills only to active suppliers
    profile = env["fix.vendor.tax.profile"].create(
        {
            "partner_id": vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789012",
            "bin": "9876543210123",
            "psr_reference": "PSR-2026-PADMA",
            "psr_valid_until": "2099-06-30",
            # A08 M52-10: a PSR counts only with the proof attached
            "psr_attachment_ids": [(6, 0, _evidence(env, "PSR-2026-PADMA.pdf").ids)],
        }
    )
    return {
        "env": env,
        "company": company,
        "ou": ou,
        "accounts": accounts,
        "bank": bank,
        "vendor": vendor,
        "profile": profile,
        "product": env["product.product"].create({"name": "Logic board"}),
        "acc1": _user(env, ou, "account.group_account_user"),
        "acc2": _user(env, ou, "account.group_account_user"),
        "acc3": _user(env, ou, "account.group_account_user"),
        "mgr": _user(env, ou, "account.group_account_manager"),
        "mgr2": _user(env, ou, "account.group_account_manager"),
    }


def _bill(a, price, qty=1.0, ref=None, po=None, **vals):
    return a["env"]["fix.vendor.invoice"].create(
        {
            "operating_unit_id": a["ou"].id,
            "vendor_id": a["vendor"].id,
            "invoice_ref": ref or "PS-%d" % next(_SEQ),
            "invoice_date": vals.pop("invoice_date", date(2026, 10, 5)),
            # with no PO a bill is a non-PO bill: a PO-type bill with no order
            # linked is 'unmatched' and is refused at submission (G3-06)
            "bill_type": vals.pop("bill_type", "po" if po else "non_po"),
            "requisition_id": po.id if po else False,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": a["product"].id,
                        "description": "Logic board",
                        "quantity": qty,
                        "unit_price": price,
                        "tds_category": vals.pop("tds_category", "supply_of_goods"),
                    },
                )
            ],
            **vals,
        }
    )


def _issued_po(env, ou, vendor, lines):
    """A PO the way M16 leaves it for the three-way match (A06 S6): approved,
    sent to an active supplier, with POSTED and inspected receipts. lines:
    [(product, qty_ordered, qty_received, unit_price)]. The match reads
    received quantity only from posted receipt lines and the price from the
    approval, so a PO line can no longer be created with a typed qty_received.
    """
    if "fix.supplier" in env and not env["fix.supplier"].search([("partner_id", "=", vendor.id)]):
        supplier = env["fix.supplier"].create(
            {"name": vendor.name, "partner_id": vendor.id, "status": "active"}
        )
        for doc_type in ("trade_licence", "tin", "vat"):
            env["fix.supplier.document"].create(
                {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
            )
    po = env["fix.purchase.order"].create(
        {
            "operating_unit_id": ou.id,
            "vendor_id": vendor.id,
            "line_ids": [
                (0, 0, {"product_id": p.id, "qty_ordered": o, "unit_price": u})
                for p, o, _r, u in lines
            ],
        }
    )
    po.action_record_requisition_exception(reason="AP test PO without requisition")
    po._guarded().write(
        {
            "approval_state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": po._dofa_current_tier(),
            "dofa_approved_amount": po.amount_total,
        }
    )
    po.action_send()
    receive(po, {pol.id: r for pol, (_p, _o, r, _u) in zip(po.line_ids, lines, strict=False) if r})
    return po


def receive(po, quantities):
    """Post a receipt of {po_line_id: qty} and pass its inspection."""
    if not quantities:
        return
    po.action_record_receipt(quantities)
    receipt = po.receipt_ids.sorted("id")[-1]
    for line in receipt.line_ids:
        po.env["fix.procurement.inspection"].create(
            {"receipt_line_id": line.id, "qty_accepted": line.qty_received}
        ).action_confirm()


def _po(a, qty, price):
    """A received PO for the bill (see _issued_po)."""
    return _issued_po(a["env"], a["ou"], a["vendor"], [(a["product"], qty, qty, price)])


def _approve(a, bill):
    bill.with_user(a["acc1"]).action_submit_approval()
    bill.with_user(a["acc2"]).action_approve()
    if bill.approval_state != "approved":
        bill.with_user(a["mgr"]).action_approve()
    return bill


class TestVendorTaxProfile:
    def test_identifier_formats(self, a08):
        with pytest.raises(ValidationError, match="12 digits"), a08["env"].cr.savepoint():
            a08["profile"].tin = "12345"
        with pytest.raises(ValidationError, match="13 digits"), a08["env"].cr.savepoint():
            a08["profile"].bin = "12AB"

    def test_non_filer_suffers_the_multiplier(self, a08):
        filer = _bill(a08, 10000.0, tds_category="service_general")
        assert (filer.tds_amount, filer.line_ids.tds_multiplier) == (1000.0, 1.0)
        assert filer.line_ids.tds_section == "ITA 2023 s.90"
        a08["profile"].psr_valid_until = date(2026, 6, 30)  # expired before the bill
        expired = _bill(a08, 10000.0, tds_category="service_general")
        assert (expired.tds_amount, expired.line_ids.tds_multiplier) == (1500.0, 1.5)
        stranger = a08["env"]["res.partner"].create({"name": "No Profile Traders"})
        none = _bill(a08, 10000.0, vendor_id=stranger.id, tds_category="service_general")
        # A08 M52-10: no PSR and no TIN are two ITA 2023 defaults (s.142,
        # s.143/163), the rule M51's withholding line enforces; this asserted
        # 1,500 while the certificate said 2,250.
        assert (none.tds_amount, none.line_ids.tds_multiplier) == (2250.0, 2.25)
        a08["profile"].write({"psr_valid_until": date(2099, 6, 30), "psr_attachment_ids": False})
        # a valid-dated reference without its proof is no PSR
        typed = _bill(a08, 10000.0, tds_category="service_general")
        assert typed.line_ids.tds_multiplier == 1.5

    def test_payee_type_and_effective_dating(self, a08):
        env = a08["env"]
        a08["profile"].taxpayer_type = "individual"
        consult = _bill(a08, 10000.0, tds_category="professional_fees")
        assert consult.line_ids.tds_rate == 15.0  # individual row
        # a company-specific row from 1 Nov overrides the statutory default
        env["fix.tax.rate"].create(
            {
                "company_id": a08["company"].id,
                "tax_kind": "tds",
                "code": "supply_of_goods",
                "name": "Adviser-corrected supply rate",
                "section": "ITA 2023 s.89",
                "rate": 7.0,
                "date_from": "2026-11-01",
            }
        )
        before = _bill(a08, 1000.0)
        after = _bill(a08, 1000.0, invoice_date=date(2026, 11, 3))
        assert (before.tds_amount, after.tds_amount) == (50.0, 70.0)

    def test_unknown_rate_fails_closed(self, a08):
        with pytest.raises(UserError, match="No effective TDS rate"), a08["env"].cr.savepoint():
            _bill(a08, 1000.0, invoice_date=date(2020, 1, 1))

    def test_vds_from_service_code_capped_at_stated_vat(self, a08):
        rent = a08["env"].ref("cd_tax_engine_bd.tax_rate_vds_rent")
        bill = _bill(a08, 100000.0, vat_amount=15000.0, vds_rate_id=rent.id)
        assert (bill.vds_amount, bill.tds_amount) == (15000.0, 5000.0)
        assert bill.total_payable == 100000.0 + 15000.0 - 5000.0 - 15000.0
        low_vat = _bill(a08, 100000.0, vat_amount=5000.0, vds_rate_id=rent.id)
        assert low_vat.vds_amount == 5000.0


class TestApprovalMatrix:
    def test_two_level_approval_with_segregation_of_duties_posts_the_bill(self, a08):
        env = a08["env"]
        rent = env.ref("cd_tax_engine_bd.tax_rate_vds_rent")
        bill = _bill(
            a08,
            600000.0,
            vat_amount=90000.0,
            vds_rate_id=rent.id,
            supplier_mushak_no="63-000123",
        )
        bill.with_user(a08["acc1"]).action_submit_approval()
        assert (bill.approval_state, bill.approval_levels_required) == ("to_approve", 2)
        with pytest.raises(UserError, match="submitter cannot approve"), env.cr.savepoint():
            bill.with_user(a08["acc1"]).action_approve()
        bill.with_user(a08["acc2"]).action_approve()
        assert (bill.approval_state, bill.approval_level) == ("to_approve", 1)
        with pytest.raises(UserError, match="must be approved by a member"), env.cr.savepoint():
            bill.with_user(a08["acc2"]).action_approve()
        with pytest.raises(UserError, match=r"Bill .* is to_approve"), env.cr.savepoint():
            bill.line_ids.unit_price = 1.0  # locked while awaiting approval
        bill.with_user(a08["mgr"]).action_approve()
        assert bill.approval_state == "approved"
        assert sorted(bill.approval_log_ids.mapped("action")) == ["approve", "approve", "submit"]
        # GL: Dr expense 600,000 + input VAT 90,000 = Cr TDS 30,000 + VDS 90,000 + AP 570,000
        move = bill.move_id
        assert move.state == "posted"
        by_acc = {line.account_id: (line.debit, line.credit) for line in move.line_ids}
        acc = a08["accounts"]
        assert by_acc[acc["vat_input"]] == (90000.0, 0.0)
        assert by_acc[acc["tds_payable"]] == (0.0, 30000.0)
        assert by_acc[acc["vds_payable"]] == (0.0, 90000.0)
        assert sum(move.line_ids.mapped("debit")) == sum(move.line_ids.mapped("credit")) == 690000.0
        # deductions and the input credit are recorded from the posted bill
        kinds = {(w.tax_kind, w.amount, w.state) for w in bill.withholding_line_ids}
        assert kinds == {("tds", 30000.0, "withheld"), ("vds", 90000.0, "withheld")}
        tds = bill.withholding_line_ids.filtered(lambda w: w.tax_kind == "tds")
        assert (tds.section, tds.partner_tin, tds.period) == (
            "ITA 2023 s.89",
            "123456789012",
            "2026-10",
        )
        credit = bill.input_credit_id
        assert (credit.vat_amount, credit.state, credit.claim_period) == (
            90000.0,
            "eligible",
            "2026-10",
        )
        assert _events(env, "vendor_bill.approved", bill.id)[0]["payable"] == 570000.0

    def test_rejection_and_reset(self, a08):
        bill = _bill(a08, 1000.0)
        bill.with_user(a08["acc1"]).action_submit_approval()
        bill.with_user(a08["acc2"]).action_reject()
        assert bill.approval_state == "rejected"
        bill.line_ids.unit_price = 900.0  # editable again
        bill.with_user(a08["acc1"]).action_reset_draft()
        assert bill.approval_state == "draft"

    def test_no_matrix_level_fails_closed(self, a08):
        a08["env"]["fix.ap.approval.rule"].search([]).write({"active": False})
        bill = _bill(a08, 1000.0)
        with pytest.raises(UserError, match="No approval-matrix level"), a08["env"].cr.savepoint():
            bill.action_submit_approval()

    def test_duplicate_reference_is_refused(self, a08):
        _bill(a08, 1000.0, ref="PS-DUP-1")
        dup = _bill(a08, 1000.0, ref="ps-dup-1")
        with pytest.raises(UserError, match="Duplicate prevention"), a08["env"].cr.savepoint():
            dup.action_submit_approval()

    def test_missing_account_fails_closed_and_leaves_nothing(self, a08):
        env = a08["env"]
        env["ir.config_parameter"].sudo().set_param("cd_tax_engine_bd.account_code.vds_payable", "")
        rent = env.ref("cd_tax_engine_bd.tax_rate_vds_rent")
        bill = _bill(a08, 1000.0, vds_rate_id=rent.id)
        bill.with_user(a08["acc1"]).action_submit_approval()
        with pytest.raises(UserError, match="vds_payable"), env.cr.savepoint():
            bill.with_user(a08["acc2"]).action_approve()
        assert (bill.approval_state, bill.move_id) == ("to_approve", env["account.move"])
        assert not bill.withholding_line_ids


class TestVendorNotes:
    def test_credit_note_posts_reduces_input_vat_and_respects_sod(self, a08):
        env = a08["env"]
        bill = _approve(a08, _bill(a08, 20000.0, vat_amount=3000.0, supplier_mushak_no="63-1"))
        note = (
            env["fix.vendor.note"]
            .with_user(a08["acc1"])
            .create(
                {
                    "invoice_id": bill.id,
                    "note_type": "decrease",
                    "mushak_ref": "67-0042",
                    "note_date": "2026-10-20",
                    "amount": 2000.0,
                    "vat_amount": 300.0,
                }
            )
        )
        assert (note.name, note.signed_total) == (
            "Mushak 6.7 67-0042 (%s)" % bill.invoice_ref,
            -2300.0,
        )
        with pytest.raises(UserError, match="creator cannot approve"), env.cr.savepoint():
            note.with_user(a08["acc1"]).action_approve()
        note.with_user(a08["acc2"]).action_approve()
        assert note.state == "approved" and note.move_id.state == "posted"
        adj = note.input_credit_id
        assert (adj.adjustment_type, adj.signed_vat, adj.state) == ("decrease", -300.0, "eligible")

    def test_credit_notes_cannot_exceed_the_bill(self, a08):
        bill = _approve(a08, _bill(a08, 1000.0))
        with pytest.raises(ValidationError, match="cannot exceed"), a08["env"].cr.savepoint():
            a08["env"]["fix.vendor.note"].create(
                {"invoice_id": bill.id, "mushak_ref": "67-9", "amount": 1500.0}
            )


class TestPaymentRun:
    def test_full_cycle_nets_notes_and_creates_executions(self, a08):
        env = a08["env"]
        po = _po(a08, 2.0, 50000.0)
        bill = _approve(a08, _bill(a08, 50000.0, qty=2.0, po=po, payment_term_days=0))
        assert bill.match_state == "matched"
        note = env["fix.vendor.note"].create(
            {"invoice_id": bill.id, "mushak_ref": "67-77", "amount": 10000.0}
        )
        note.with_user(a08["acc2"]).action_approve()
        # PO-type, no PO: refused at submission (G3-06), and never paid even when
        # approved and posted, as a bill approved before that gate is (system
        # code sets the state; the other bill's entry stands in for its own)
        unmatched = _bill(a08, 5000.0, bill_type="po", payment_term_days=0)
        with pytest.raises(UserError, match="G3-06"), env.cr.savepoint():
            unmatched.with_user(a08["acc1"]).action_submit_approval()
        unmatched._guarded().write({"approval_state": "approved", "move_id": bill.move_id.id})
        run = env["fix.payment.run"].create({"rail": "beftn", "due_by": "2026-10-31"})
        run.with_user(a08["acc1"]).action_propose()
        line = run.line_ids
        assert line.bill_ids == bill and unmatched not in run.line_ids.bill_ids
        # 100,000 - 5% TDS (5,000) - credit note 10,000
        assert (line.gross_amount, line.tds_amount, line.notes_amount, line.amount) == (
            100000.0,
            5000.0,
            -10000.0,
            85000.0,
        )
        # A08 S1: an unpayable payee drops out of the proposal with its reason, so it
        # does not stop the run for other vendors; with no payable line there is no run
        assert line.state == "skipped" and "no bank account" in line.skip_reason
        with pytest.raises(UserError, match="Nothing payable"), env.cr.savepoint():
            run.with_user(a08["acc1"]).action_submit()
        acct = env["res.partner.bank"].create(
            {"partner_id": a08["vendor"].id, "acc_number": "0123456789"}
        )
        run.with_user(a08["acc1"]).action_propose()
        assert "no routing number" in run.line_ids.skip_reason
        acct.fix_routing_number = "175260346"
        run.with_user(a08["acc1"]).action_propose()
        # the account is not paid until a second person confirms it
        assert "not confirmed" in run.line_ids.skip_reason
        with pytest.raises(UserError, match="Nothing payable"), env.cr.savepoint():
            run.with_user(a08["acc1"]).action_submit()
        _confirm_bank(a08, acct)
        run.with_user(a08["acc1"]).action_propose()
        assert run.line_ids.state == "proposed" and not run.line_ids.skip_reason
        run.with_user(a08["acc1"]).action_submit()
        with pytest.raises(UserError, match="accounting manager"), env.cr.savepoint():
            run.with_user(a08["acc2"]).action_approve()
        run.with_user(a08["mgr"]).action_approve()
        # BRU-APE-06: the preparer (acc1) does not release; a third person does
        with pytest.raises(UserError, match="BRU-APE-06"), env.cr.savepoint():
            run.with_user(a08["acc1"]).action_release()
        run.with_user(a08["acc2"]).action_release()
        execution = run.line_ids.execution_id.sudo()
        assert (execution.source_model, execution.source_id, execution.amount) == (
            "fix.payment.run.line",
            run.line_ids.id,
            85000.0,
        )
        assert (execution.rail, execution.partner_bank_id, execution.journal_id) == (
            "beftn",
            acct,
            a08["bank"],
        )
        assert execution.source_posts_gl  # treasury must not post a second credit
        assert (bill.payment_state, note.state, run.state) == ("in_run", "applied", "released")
        run.action_sync_bank_status()
        assert run.state == "released"  # the bank has not confirmed yet
        _treasury_executed(execution, "BEFTN-TRX-0001")
        assert not execution.move_id  # the run's own entry is the only posting
        run.action_sync_bank_status()
        assert (bill.payment_state, run.line_ids.state, run.state) == ("paid", "paid", "done")
        pay = run.line_ids.move_id
        assert pay.state == "posted" and sum(pay.line_ids.mapped("debit")) == 85000.0

    def test_rtgs_minimum_is_master_data(self, a08):
        env = a08["env"]
        po = _po(a08, 1.0, 20000.0)
        _approve(a08, _bill(a08, 20000.0, po=po, payment_term_days=0))
        env["res.partner.bank"].create(
            {"partner_id": a08["vendor"].id, "acc_number": "77", "fix_routing_number": "175260346"}
        )
        run = env["fix.payment.run"].create({"rail": "rtgs", "due_by": "2026-10-31"})
        run.action_propose()
        assert "below the BD-RTGS minimum" in run.line_ids.skip_reason
        with pytest.raises(UserError, match="Nothing payable"), env.cr.savepoint():
            run.action_submit()

    def test_nothing_due_is_refused(self, a08):
        run = a08["env"]["fix.payment.run"].create({"due_by": "2000-01-01"})
        with pytest.raises(UserError, match="No approved, matched"), a08["env"].cr.savepoint():
            run.action_propose()


class TestNonPoBills:
    """Rent, utilities and other service bills have no purchase order: they are
    paid on the approval matrix (two-way control), never blocked forever by a
    three-way match that cannot exist."""

    def test_non_po_bill_is_payable_after_approval_only(self, a08):
        env = a08["env"]
        rent = _bill(
            a08, 30000.0, bill_type="non_po", payment_term_days=0, tds_category="rent_commercial"
        )
        assert (rent.match_state, rent.match_detail) == (
            "not_required",
            "Non-PO bill: controlled by the approval matrix",
        )
        no_po = _bill(a08, 5000.0, bill_type="po", payment_term_days=0)  # PO-type, no PO
        assert no_po.match_state == "unmatched"
        # refused at submission (G3-06); not paid even when approved, as a bill
        # approved before that gate is
        with pytest.raises(UserError, match="G3-06"), env.cr.savepoint():
            no_po.with_user(a08["acc1"]).action_submit_approval()
        no_po._guarded().write({"approval_state": "approved"})
        run = env["fix.payment.run"].create({"rail": "beftn", "due_by": "2026-10-31"})
        with pytest.raises(UserError), env.cr.savepoint():
            run.with_user(a08["acc1"]).action_propose()  # nothing approved and payable yet
        _approve(a08, rent)
        no_po._guarded().write({"move_id": rent.move_id.id})  # a posted entry stands in for its own
        run.with_user(a08["acc1"]).action_propose()
        assert rent in run.line_ids.bill_ids and no_po not in run.line_ids.bill_ids

    def test_non_po_bill_cannot_carry_a_purchase_order(self, a08):
        env = a08["env"]
        po = _po(a08, 1.0, 1000.0)
        with pytest.raises(ValidationError, match="three-way match"), env.cr.savepoint():
            _bill(a08, 1000.0, po=po, bill_type="non_po")

    def test_non_po_bills_are_not_match_exceptions(self, a08):
        env = a08["env"]
        rent = _bill(a08, 1000.0, bill_type="non_po")
        exceptions = env["fix.vendor.invoice"].search(
            [("match_state", "in", ("unmatched", "blocked"))]
        )
        assert rent not in exceptions


class TestEmployeeExpense:
    @pytest.fixture
    def staff(self, a08):
        env = a08["env"]
        grade = env["fix.expense.grade"].create({"name": "Field technician"})
        employee = env["hr.employee"].create(
            {"name": "Technician Karim", "expense_grade_id": grade.id}
        )
        employee.bank_account_ids = env["res.partner.bank"].create(
            {
                "partner_id": employee.work_contact_id.id,
                "acc_number": "2050001",
                "fix_routing_number": "175260346",
            }
        )
        return {**a08, "grade": grade, "employee": employee}

    def _claim(self, s, lines, **vals):
        return s["env"]["fix.expense.claim"].create(
            {
                "operating_unit_id": s["ou"].id,
                "employee_id": s["employee"].id,
                "description": "Site visit Chattogram",
                "expense_date": "2026-10-10",
                "line_ids": [(0, 0, {"cost_centre": "CC-T", **line}) for line in lines],
                **vals,
            }
        )

    def test_per_diem_and_mileage_from_the_rate_master(self, staff):
        env = staff["env"]
        per_diem = env.ref("cd_ap_ext.expense_category_per_diem")
        mileage = env.ref("cd_ap_ext.expense_category_mileage")
        env["fix.expense.rate"].create(
            {"rate_type": "per_diem", "rate": 800.0, "date_from": "2026-07-01"}
        )
        env["fix.expense.rate"].create(
            {
                "rate_type": "per_diem",
                "grade_id": staff["grade"].id,
                "location": "Chattogram",
                "rate": 1200.0,
                "date_from": "2026-07-01",
            }
        )
        env["fix.expense.rate"].create(
            {
                "rate_type": "mileage",
                "vehicle": "motorcycle",
                "rate": 6.0,
                "date_from": "2026-07-01",
            }
        )
        claim = self._claim(
            staff,
            [
                {
                    "category_id": per_diem.id,
                    "date": "2026-10-10",
                    "location": "Chattogram",
                    "quantity": 2,
                },
                {
                    "category_id": mileage.id,
                    "date": "2026-10-10",
                    "vehicle": "motorcycle",
                    "quantity": 150,
                },
            ],
        )
        assert claim.line_ids.mapped("unit_amount") == [1200.0, 6.0]
        assert claim.amount == 2400.0 + 900.0
        claim.line_ids[0].unit_amount = 5000.0  # per-diem comes from the master only
        assert claim.line_ids[0].unit_amount == 1200.0
        with pytest.raises(UserError, match="No mileage rate"), env.cr.savepoint():
            self._claim(
                staff,
                [
                    {
                        "category_id": mileage.id,
                        "date": "2026-10-10",
                        "vehicle": "car",
                        "quantity": 5,
                    }
                ],
            )

    def test_policy_enforced_on_submit_then_sod_approval_posts(self, staff):
        env = staff["env"]
        hotel = env.ref("cd_ap_ext.expense_category_accommodation")
        env["fix.expense.policy"].create(
            {
                "category_id": hotel.id,
                "grade_id": staff["grade"].id,
                "limit_per_line": 4000.0,
                "receipt_required_above": 1000.0,
            }
        )
        claim = self._claim(
            staff, [{"category_id": hotel.id, "unit_amount": 4500.0, "date": "2026-10-10"}]
        )
        with pytest.raises(UserError, match="Expense policy breached") as err, env.cr.savepoint():
            claim.with_user(staff["acc1"]).action_submit()
        assert "above the per-expense limit 4000.00" in str(err.value)
        assert "receipt required above BDT 1000.00" in str(err.value)
        claim.line_ids.write(
            {
                "unit_amount": 3500.0,
                "receipt_attachment_ids": [
                    (0, 0, {"name": "hotel.pdf", "datas": "UERG", "res_model": "fix.expense.claim"})
                ],
            }
        )
        claim.with_user(staff["acc1"]).action_submit()
        assert claim.state == "submitted"
        with pytest.raises(UserError, match="Segregation of duties"), env.cr.savepoint():
            claim.with_user(staff["acc1"]).action_approve()
        claim.with_user(staff["acc2"]).action_approve()
        assert claim.state == "approved" and claim.move_id.state == "posted"
        credit = claim.move_id.line_ids.filtered(lambda line: line.credit)
        assert (credit.account_id, credit.credit) == (staff["accounts"]["employee_payable"], 3500.0)
        assert _events(env, "payment.requested", claim.id)[0]["amount"] == 3500.0

    def test_advance_disbursement_settlement_and_recovery(self, staff):
        env = staff["env"]
        advance = (
            env["fix.employee.advance"]
            .with_user(staff["acc1"])
            .create(
                {
                    "operating_unit_id": staff["ou"].id,
                    "employee_id": staff["employee"].id,
                    "purpose": "Parts float, Sylhet trip",
                    "amount": 5000.0,
                }
            )
        )
        with pytest.raises(UserError, match="Segregation of duties"), env.cr.savepoint():
            advance.with_user(staff["acc1"]).action_approve()
        advance.with_user(staff["acc2"]).action_approve()
        execution = advance.execution_id.sudo()
        assert execution.amount == 5000.0
        assert execution.source_posts_gl and execution.journal_id == staff["bank"]
        with pytest.raises(UserError, match="no bank confirmation"), env.cr.savepoint():
            advance.action_confirm_disbursement()
        execution._guarded().write({"state": "sent"})  # treasury released it (M50)
        with pytest.raises(UserError, match="no bank confirmation"), env.cr.savepoint():
            advance.action_confirm_disbursement()  # sent, not yet confirmed by the bank
        _treasury_executed(execution, "BEFTN-77")
        advance.action_confirm_disbursement()
        assert advance.state == "disbursed" and advance.disbursement_move_id.state == "posted"
        other = env.ref("cd_ap_ext.expense_category_other")
        claim = self._claim(
            staff, [{"category_id": other.id, "unit_amount": 3000.0}], advance_id=advance.id
        )
        claim.with_user(staff["acc1"]).action_submit()
        claim.with_user(staff["acc2"]).action_approve()
        assert _events(env, "payment.requested", claim.id) == []  # settled via the advance
        advance.action_settle()
        assert (advance.settled_amount, advance.balance, advance.state) == (
            3000.0,
            2000.0,
            "disbursed",
        )
        with pytest.raises(UserError, match="recovery method"), env.cr.savepoint():
            advance.action_record_recovery()
        # F11 / E3-17 (owner decision 12 Nov 2026): cash handed back debits Cash in
        # Hand, not the payment bank journal (it used to land on the bank GL)
        Account = env["account.account"]
        cash = Account.search(
            [("code", "=", "990109"), ("company_ids", "in", env.company.id)], limit=1
        ) or Account.create(
            {
                "code": "990109",
                "name": "Test cash in hand",
                "account_type": "asset_cash",
                "company_ids": [(6, 0, [env.company.id])],
            }
        )
        env["ir.config_parameter"].sudo().set_param(
            "cd_cash_position.account_code.branch_cash", "990109"
        )
        advance.recovery_method = "cash"
        advance.action_record_recovery()
        assert (advance.recovered_amount, advance.balance, advance.state) == (
            2000.0,
            0.0,
            "settled",
        )
        debit = advance.recovery_move_id.line_ids.filtered(lambda ml: ml.debit)
        assert (debit.account_id, debit.debit) == (cash, 2000.0)
