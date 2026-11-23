# cd_ap_ext — A08 wave 5: consignment settlement (M52-F3 / FR-APE-030 P0)
# and retention money (M52-F4 / FR-APE-027, BRU-APE-20).
#
# Live ORM on the wave-5 test database, every test in a transaction that is
# rolled back. The probes are the audit's own gaps:
#   * a brand settlement gathers M15's consumed consignment quantities, pays
#     rate x quantity exactly, posts Dr expense (+ input VAT) / Cr AP with
#     OU / branch / brand dimensions, and needs a second person to approve;
#   * retention withholds the exact percentage, posts the split (Cr retention
#     payable, AP net of it), is absent from the normal payable ageing, and is
#     released only through the approved maker-checker action;
#   * a missing GL account role fails closed naming its system parameter.
from __future__ import annotations

import base64
import itertools
from datetime import date, datetime

import pytest
from odoo import fields
from odoo.addons.cd_ap_ext.models.fix_ap_capture import BUCKETS, ageing_by_vendor
from odoo.exceptions import AccessError, UserError, ValidationError

pytestmark = [pytest.mark.financial]

REFUSED = (UserError, ValidationError, AccessError)
ACC = "account.group_account_user"
MGR = "account.group_account_manager"
BILL = "account.group_account_invoice"
_SEQ = itertools.count(1)

D = date(2026, 10, 1)
PERIOD_START = date(2026, 11, 1)
PERIOD_END = date(2026, 11, 30)
SETTLED_ON = date(2026, 11, 20)
FUTURE_RELEASE = date(2026, 11, 30)


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


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.company = env.company
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    Account = env["account.account"]

    def acc(code, name, kind):
        return Account.create(
            {
                "code": code,
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, [x.company.id])],
            }
        )

    x.a = {
        "expense": acc("990600", "Wave5 expense / consumption", "expense"),
        "ap": acc("990101", "Wave5 AP control", "liability_payable"),
        "vat_input": acc("990131", "Wave5 input VAT", "asset_current"),
        "retention_payable": acc("990255", "Wave5 retention payable", "liability_current"),
    }
    icp = env["ir.config_parameter"].sudo()
    for param, code in (
        ("cd_ap_ext.account_code.expense", "990600"),
        ("cd_ap_ext.account_code.ap", "990101"),
        ("cd_tax_engine_bd.vat_input_account_code", "990131"),
        ("cd_ap_ext.account_code.retention_payable", "990255"),
    ):
        icp.set_param(param, code)
    x.bank = env["account.journal"].search(
        [("company_id", "=", x.company.id), ("type", "=", "bank")], limit=1
    )
    icp.set_param("cd_ap_ext.payment_journal_code", x.bank.code)
    # the limit is optional: start with none, a test sets one
    icp.set_param("cd_ap_ext.retention_max_percent", "")

    x.acc1 = _user(env, "a08w5_acc1", [ACC])
    x.acc2 = _user(env, "a08w5_acc2", [ACC])
    x.mgr = _user(env, "a08w5_mgr", [MGR])

    # a sub-contractor whose tax profile supports a clean 10 % TDS determination
    x.vendor = env["res.partner"].create({"name": "A08W5 Nabin Builders"})
    env["fix.vendor.tax.profile"].create(
        {
            "partner_id": x.vendor.id,
            "taxpayer_type": "company",
            "tin": "123456789012",
            "bin": "9876543210123",
            "psr_reference": "PSR-A08W5",
            "psr_valid_until": "2099-06-30",
            "psr_attachment_ids": [(6, 0, _file(env, "psr.pdf", "PSR-A08W5").ids)],
        }
    )
    env["fix.supplier"].create(
        {
            "name": x.vendor.name,
            "partner_id": x.vendor.id,
            "status": "active",
            "company_id": x.company.id,
        }
    )
    x.product = env["product.product"].create({"name": "A08W5 fabricated part"})

    # the branch dimension
    entity = env["fix.entity"].sudo().search([("company_id", "=", x.company.id)], limit=1)
    if not entity:
        entity = (
            env["fix.entity"]
            .sudo()
            .create({"code": "W5E", "legal_name": x.company.name, "company_id": x.company.id})
        )
    x.branch = (
        env["fix.branch"]
        .sudo()
        .create(
            {
                "code": "W5B",
                "name": "A08W5 Branch",
                "entity_id": entity.id,
                "operating_unit_id": x.ou.id,
            }
        )
    )
    return x


def bill(c, price, by=None, qty=1.0, **vals):
    return (
        c.env["fix.vendor.invoice"]
        .with_user(by or c.acc1)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": c.vendor.id,
                "invoice_ref": "A08W5-%d" % next(_SEQ),
                "invoice_date": vals.pop("invoice_date", D),
                "payment_term_days": vals.pop("payment_term_days", 0),
                "bill_type": "non_po",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": c.product.id,
                            "description": "A08W5 sub-contract work",
                            "quantity": qty,
                            "unit_price": price,
                            "tds_category": vals.pop("tds_category", "service_general"),
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


# ============================================================ consignment
def _world(c):
    """A brand, its part, a store, a technician and two consumed consignment
    issues that M15 would have recorded on warranty jobs."""
    env = c.env
    brand = env["fix.brand"].create({"name": "A08W5 Brand", "code": "W5BR"})
    part = env["fix.spare.part"].create(
        {
            "name": "A08W5 display assembly",
            "part_number": "W5-PART-1",
            "brand_id": brand.id,
            "product_id": c.product.id,
            "company_id": c.company.id,
        }
    )
    location = env["fix.stock.location"].create(
        {"name": "A08W5 Central", "code": "W5CEN", "company_id": c.company.id}
    )
    tech = env["hr.employee"].create({"name": "A08W5 Technician"})
    Consumption = env["fix.stock.consumption"].sudo()
    first = Consumption.create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "service_order_ref": "W5-JOB-1",
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": tech.id,
            "quantity": 3.0,
            "scanned_code": part.part_number,
            "ownership_class": "consignment",
            "state": "consumed",
            "consumed_at": datetime(2026, 11, 10, 9, 0),
        }
    )
    second = Consumption.create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "service_order_ref": "W5-JOB-2",
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": tech.id,
            "quantity": 2.0,
            "scanned_code": part.part_number,
            "ownership_class": "consignment",
            "state": "consumed",
            "consumed_at": datetime(2026, 11, 15, 9, 0),
        }
    )
    # a third issue OUTSIDE the period: never gathered
    Consumption.create(
        {
            "company_id": c.company.id,
            "operating_unit_id": c.ou.id,
            "service_order_ref": "W5-JOB-3",
            "product_id": part.id,
            "location_id": location.id,
            "technician_id": tech.id,
            "quantity": 9.0,
            "scanned_code": part.part_number,
            "ownership_class": "consignment",
            "state": "consumed",
            "consumed_at": datetime(2026, 12, 5, 9, 0),
        }
    )
    partner = env["res.partner"].create({"name": "A08W5 Brand Partner"})
    brand_supplier = env["fix.supplier"].create(
        {
            "name": partner.name,
            "partner_id": partner.id,
            "status": "active",
            "company_id": c.company.id,
        }
    )
    agreement = env["fix.supplier.agreement"].create(
        {
            "supplier_id": brand_supplier.id,
            "agreement_type": "consignment",
            "reference": "W5-CONSIGN-1",
            "term_from": date(2026, 1, 1),
            "term_to": date(2027, 12, 31),
            "settlement_trigger": "consumption",
            "settlement_cadence": "monthly",
        }
    )
    agreement.sudo().write({"state": "active"})
    price = env["fix.supplier.price.list"].create(
        {
            "agreement_id": agreement.id,
            "product_id": c.product.id,
            "price": 250.0,
            "valid_from": date(2026, 1, 1),
        }
    )
    price.sudo().write({"state": "approved"})
    return brand, partner, (first, second)


def _settlement(c, brand, partner):
    return (
        c.env["fix.ap.consignment.settlement"]
        .with_user(c.acc1)
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "brand_id": brand.id,
                "partner_id": partner.id,
                "period_start": PERIOD_START,
                "period_end": PERIOD_END,
                "settlement_date": SETTLED_ON,
            }
        )
    )


def test_consignment_settlement_rate_times_qty_posts_with_dims_and_second_person(c):
    """FR-APE-030 P0 / AUT-APE-10/11: 3 x 250 + 2 x 250 = 1,250 payable; the
    posting is Dr expense / Cr AP control with OU, branch and brand; the
    submitter cannot approve."""
    brand, partner, _issues = _world(c)
    settlement = _settlement(c, brand, partner)
    settlement.with_user(c.acc1).action_gather()

    assert len(settlement.line_ids) == 2
    assert settlement.quantity_total == 5.0
    assert [line.rate for line in settlement.line_ids] == [250.0, 250.0]
    assert [line.value for line in settlement.line_ids] == [750.0, 500.0]
    assert settlement.value_untaxed == 1250.0
    assert settlement.vat_amount == 0.0  # no tax profile on the brand party
    assert settlement.total_payable == 1250.0
    assert all(line.rate_source == "agreement" for line in settlement.line_ids)

    settlement.with_user(c.acc1).action_submit()
    exc = refused(c.env, lambda: settlement.with_user(c.acc1).action_approve())
    assert exc and "Segregation of duties" in str(exc)
    assert settlement.state == "submitted"

    settlement.with_user(c.acc2).action_approve()
    assert settlement.state == "approved" and settlement.move_id.state == "posted"
    move = settlement.move_id
    lines = move.line_ids
    expense = lines.filtered(lambda m: m.account_id == c.a["expense"])
    payable = lines.filtered(lambda m: m.account_id == c.a["ap"])
    assert round(sum(expense.mapped("debit")), 2) == 1250.0
    assert round(sum(expense.mapped("credit")), 2) == 0.0
    assert round(sum(payable.mapped("credit")), 2) == 1250.0
    assert round(sum(payable.mapped("debit")), 2) == 0.0

    dims = c.env["fix.journal.dimension"].sudo().search([("move_line_id", "in", lines.ids)])
    assert len(dims) == len(lines)
    assert set(dims.mapped("operating_unit_id").ids) == {c.ou.id}
    assert set(dims.mapped("branch_id").ids) == {c.branch.id}
    assert set(dims.mapped("brand")) == {brand.name}

    # an overlapping period cannot settle the same issues twice
    other = (
        c.env["fix.ap.consignment.settlement"]
        .with_user(c.acc1)
        .create(
            {
                "company_id": c.company.id,
                "operating_unit_id": c.ou.id,
                "branch_id": c.branch.id,
                "brand_id": brand.id,
                "partner_id": partner.id,
                "period_start": date(2026, 11, 10),
                "period_end": date(2026, 11, 20),
                "settlement_date": SETTLED_ON,
            }
        )
    )
    exc = refused(c.env, lambda: other.with_user(c.acc1).action_gather())
    assert isinstance(exc, UserError)
    assert "no unsettled consignment consumption" in str(exc)


def test_consignment_settlement_vat_follows_the_partner_profile(c):
    """VAT treatment follows the brand's M51 profile: a VAT-registered brand
    (BIN, not turnover-enlisted) is charged the standard 15 %; the posting is
    Dr expense + Dr input VAT / Cr AP."""
    brand, partner, _issues = _world(c)
    profile = c.env["fix.vendor.tax.profile"].create(
        {
            "partner_id": partner.id,
            "taxpayer_type": "company",
            "bin": "1234567890123",
        }
    )
    settlement = _settlement(c, brand, partner)
    settlement.with_user(c.acc1).action_gather()
    assert settlement.vat_registered is True
    assert settlement.vat_rate == 15.0
    assert settlement.vat_amount == 187.50  # 1,250 x 15 %
    assert settlement.total_payable == 1437.50
    assert settlement.tax_profile_id == profile

    settlement.with_user(c.acc1).action_submit()
    settlement.with_user(c.acc2).action_approve()
    lines = settlement.move_id.line_ids
    expense = lines.filtered(lambda m: m.account_id == c.a["expense"])
    vat = lines.filtered(lambda m: m.account_id == c.a["vat_input"])
    payable = lines.filtered(lambda m: m.account_id == c.a["ap"])
    assert round(sum(expense.mapped("debit")), 2) == 1250.0
    assert round(sum(vat.mapped("debit")), 2) == 187.50
    assert round(sum(payable.mapped("credit")), 2) == 1437.50


def test_consignment_settlement_missing_expense_role_fails_closed(c):
    """FR-APE-030: with the expense role unset the approval refuses before
    anything posts, naming cd_ap_ext.account_code.expense."""
    brand, partner, _issues = _world(c)
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.account_code.expense", "")
    settlement = _settlement(c, brand, partner)
    settlement.with_user(c.acc1).action_gather()
    settlement.with_user(c.acc1).action_submit()
    exc = refused(c.env, lambda: settlement.with_user(c.acc2).action_approve())
    assert exc and "cd_ap_ext.account_code.expense" in str(exc)
    settlement.invalidate_recordset()
    assert settlement.state == "submitted" and not settlement.move_id
    assert balance(c.env, c.a["expense"]) == 0.0


# ============================================================ retention
def test_retention_withholds_exact_percentage_posts_split_and_skips_ageing(c):
    """FR-APE-027 / BRU-APE-20: a 10 % retention on a 100,000 bill withholds
    exactly 10,000: Dr expense 100,000 / Cr TDS 10,000 / Cr retention 10,000 /
    Cr AP 80,000. The payable ageing shows 80,000, never the withheld 10,000,
    and the register holds the 10,000 with its release date."""
    b = bill(c, 100000.0, retention_percent=10.0, retention_release_date=FUTURE_RELEASE)
    assert b.retention_amount == 10000.0
    assert b.total_payable == 80000.0
    approve(c, b)
    assert b.approval_state == "approved" and b.move_id.state == "posted"
    assert round(sum(b.move_id.line_ids.mapped("debit")), 2) == 100000.0
    assert round(sum(b.move_id.line_ids.mapped("credit")), 2) == 100000.0
    assert (
        round(
            sum(b.move_id.line_ids.filtered(lambda m: m.account_id == c.a["ap"]).mapped("credit")),
            2,
        )
        == 80000.0
    )
    assert (
        round(
            sum(
                b.move_id.line_ids.filtered(
                    lambda m: m.account_id == c.a["retention_payable"]
                ).mapped("credit")
            ),
            2,
        )
        == 10000.0
    )
    # TDS is still computed on the gross: 10 % s.90 with a valid PSR
    assert b.tds_amount == 10000.0

    retention = b.retention_ids
    assert len(retention) == 1
    assert retention.withheld_amount == 10000.0
    assert retention.release_due_date == FUTURE_RELEASE
    assert retention.state == "held"

    rows, _note = ageing_by_vendor(c.env, c.company, date(2026, 11, 23))
    row = rows[c.vendor.commercial_partner_id.display_name]
    assert round(sum(row[key] for key in dict(BUCKETS)), 2) == 80000.0

    # the money is on the retention liability seat, not on the AP control
    assert balance(c.env, c.a["retention_payable"]) == -10000.0
    assert balance(c.env, c.a["ap"]) == -80000.0


def test_retention_releases_only_through_the_approved_action(c):
    """BRU-APE-20: no direct write of the release, no release without a
    request, no early release without certified completion; then an accountant
    requests and a different Accounting Administrator releases, posting Dr
    retention payable / Cr bank."""
    b = bill(c, 100000.0, retention_percent=10.0, retention_release_date=FUTURE_RELEASE)
    approve(c, b)
    retention = b.retention_ids
    assert retention.state == "held"

    # a direct write of the release fields is refused
    exc = refused(
        c.env,
        lambda: retention.with_user(c.mgr).write(
            {"released_amount": 10000.0, "released_at": fields.Datetime.now()}
        ),
    )
    assert exc is not None
    # release without a request is refused
    exc = refused(c.env, lambda: retention.with_user(c.mgr).action_release())
    assert exc and "request its release" in str(exc)
    # early release without certified completion is refused
    exc = refused(c.env, lambda: retention.with_user(c.acc1).action_request_release())
    assert exc and "BRU-APE-20" in str(exc)

    # certified completion recorded, then the maker-checker release
    retention.with_user(c.mgr).write(
        {"release_condition": "certified", "certificate_ref": "W5-CC-1"}
    )
    retention.with_user(c.acc1).action_request_release()
    assert retention.state == "release_requested"
    # the requester (an accountant, and a maker of the bill) cannot release
    exc = refused(c.env, lambda: retention.with_user(c.acc1).action_release())
    assert exc is not None
    assert retention.state == "release_requested"

    retention.with_user(c.mgr).action_release()
    assert retention.state == "released"
    assert retention.released_amount == 10000.0
    assert retention.release_move_id.state == "posted"
    assert balance(c.env, c.a["retention_payable"]) == 0.0
    assert balance(c.env, c.a["ap"]) == -80000.0
    bank = c.env["account.move.line"].search(
        [
            ("move_id", "=", retention.release_move_id.id),
            ("account_id", "=", retention.release_move_id.journal_id.default_account_id.id),
        ]
    )
    assert round(sum(bank.mapped("credit")), 2) == 10000.0

    # released retention is final
    exc = refused(c.env, lambda: retention.with_user(c.mgr).write({"certificate_ref": "tampered"}))
    assert exc is not None


def test_retention_limit_and_missing_role_fail_closed(c):
    """FR-APE-027: the configured ceiling is enforced, and an unset
    cd_ap_ext.account_code.retention_payable refuses the posting, naming it."""
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.retention_max_percent", "5")
    b = bill(c, 100000.0, retention_percent=10.0, retention_release_date=FUTURE_RELEASE)
    exc = refused(c.env, lambda: b.with_user(c.acc1).action_submit_approval())
    assert exc and "cd_ap_ext.retention_max_percent" in str(exc)

    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.retention_max_percent", "")
    c.env["ir.config_parameter"].sudo().set_param("cd_ap_ext.account_code.retention_payable", "")
    b.with_user(c.acc1).action_submit_approval()
    exc = refused(c.env, lambda: b.with_user(c.acc2).action_approve())
    assert exc and "cd_ap_ext.account_code.retention_payable" in str(exc)
    b.invalidate_recordset()
    assert not b.move_id
    assert balance(c.env, c.a["retention_payable"]) == 0.0
