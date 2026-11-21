"""A07 ERP audit, finishing stream R2a (2026-11-21): the money glue between
the module streams' facts and the S6 posting.

Live ORM, rolled back. Reuses the S6 money fixture (accounts per test, wired
through the account-role parameters the seed sets on fix_real / fix_dev).
Each test names what it proves.
"""

from __future__ import annotations

import itertools
from datetime import timedelta

import pytest
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import month_start
from odoo.addons.cd_p03_portal.controllers.a07 import m46 as m46_reports

from .test_a07_s6_money import (  # noqa: F401 - the shared money fixture
    MOD,
    P,
    _as,
    _bill,
    _entry,
    _lease,
    _post_bill,
    _refused,
    _van,
    m,
)

_SEQ = itertools.count(1)


@pytest.fixture
def r(m):  # noqa: F811 - the S6 fixture, extended
    """The S6 fixture plus the R2a roles: deposit / advance settlements, the
    break penalty, licence kinds, the fit-out CWIP and the service charge."""
    Account = m.env["account.account"]
    icp = m.env["ir.config_parameter"].sudo()

    def acc(code, name, kind):
        return Account.create(
            {
                "code": "R2A%02d%s" % (m.tag, code),
                "name": name,
                "account_type": kind,
                "company_ids": [(6, 0, m.co.ids)],
            }
        )

    m.r = {
        "deposit": acc("01", "Security Deposit", "asset_current"),
        "advance": acc("02", "Advance House Rent", "asset_current"),
        "write_off": acc("03", "Others - Provision & Write off", "expense"),
        "penalty": acc("04", "Lease Break Penalty", "expense"),
        "lic": acc("05", "Legal & License fee", "expense"),
        "lic_trade": acc("06", "Trade License Fees", "expense"),
        "lic_pen": acc("07", "Penalty Expense (licence)", "expense"),
        "cwip": acc("08", "Capital Work in Progress", "asset_fixed"),
        "service": acc("09", "Service Charge Expense", "expense"),
        "payable": acc("10", "Trade payables", "liability_payable"),
        "fit": acc("11", "Leasehold Improvement", "asset_fixed"),
        "fit_acc": acc("12", "Amortisation on Leasehold Improvement", "asset_fixed"),
        "fit_dep": acc("13", "Amortisation expense", "expense_depreciation"),
        "insurance": acc("14", "Insurance", "expense"),
    }
    for key, name in (
        ("deposit", "deposit"),
        ("deposit.write_off", "write_off"),
        ("advance_rent", "advance"),
        ("advance_rent.write_off", "write_off"),
        ("lease_rent.break_penalty", "penalty"),
        ("licence_fee", "lic"),
        ("licence_fee.trade", "lic_trade"),
        ("licence_fee.penalty", "lic_pen"),
        ("facility_work_order.fit_out", "cwip"),
        ("lease_rent.service_charge", "service"),
        ("vehicle_insurance", "insurance"),
    ):
        icp.set_param(P + "account." + key, m.r[name].code)
    icp.set_param(P + "account.deposit.adjusted", m.a["clearing"].code)
    icp.set_param("cd_ap_ext.account_code.ap", m.r["payable"].code)
    m.site = m.env["fix.site"].create(
        {
            "name": "R2A Site %s" % m.tag,
            "company_id": m.co.id,
            "operating_unit_id": m.ou.id,
            "state": "active",
        }
    )
    return m


def _lines(move, account):
    return move.line_ids.filtered(lambda ln: ln.account_id == account)


def _site_lease(r, **kw):
    vals = {
        "site_id": r.site.id,
        "lessor_id": r.landlord.id,
        "start_date": month_start(r.today),
        "end_date": month_start(r.today) + timedelta(days=3 * 365),
        "monthly_rent": 50000.0,
    }
    vals.update(kw)
    # a migrated / superuser-recorded lease is recorded active (D6 trusted path)
    return r.env["fix.site.lease"].sudo()._guarded().create(vals)


def _charge(r, kind, amount, lease=None, **kw):
    return (
        r.env["fix.site.charge"]
        .sudo()
        ._guarded()
        ._charge_raise(r.site, kind, amount, lease=lease, vendor=r.landlord, **kw)
    )


def _cost_entry(r, record):
    return r.env["fix.asset.cost.entry"].search(
        [("source_model", "=", record._name), ("source_res_id", "=", record.id)]
    )


# ============================================================ M47-08 settlements
def test_deposit_settlements_post_their_own_entry_on_the_branch(r):
    """M47-08 / R2a: a deposit refunded, adjusted or written off (M47 raises
    them "internal") posts its own entry crediting the deposit account; it is
    never "recorded only" and never debits and credits the same account."""
    lease = _site_lease(r)
    paid = _cost_entry(r, _charge(r, "deposit_paid", 100000.0, lease=lease))
    assert paid.state == "pending" and paid.account_id == r.r["deposit"]
    # write-off: Dr Others - Provision & Write off / Cr Security Deposit
    wo = _cost_entry(
        r, _charge(r, "deposit_write_off", 10000.0, lease=lease, payment_method="internal")
    )
    assert wo.state == "posted" and wo.account_id == r.r["write_off"]
    assert _lines(wo.move_id, r.r["write_off"]).debit == 10000.0
    assert _lines(wo.move_id, r.r["deposit"]).credit == 10000.0
    # adjusted against dues: Dr the rent clearing / Cr Security Deposit
    adj = _cost_entry(
        r, _charge(r, "deposit_adjusted", 20000.0, lease=lease, payment_method="internal")
    )
    assert adj.state == "posted" and _lines(adj.move_id, r.a["clearing"]).debit == 20000.0
    assert _lines(adj.move_id, r.r["deposit"]).credit == 20000.0
    # refunded: the landlord owes it (Dr its payable, AP collects) / Cr Security Deposit
    ref = _cost_entry(
        r, _charge(r, "deposit_refund", 30000.0, lease=lease, payment_method="internal")
    )
    debit = _lines(ref.move_id, r.r["payable"])
    assert ref.state == "posted" and debit.debit == 30000.0 and debit.partner_id == r.landlord
    assert _lines(ref.move_id, r.r["deposit"]).credit == 30000.0
    from .test_a07_s6_money import _ou

    assert _ou(r, ref.move_id.line_ids) == r.ou


def test_a_settlement_without_its_role_is_not_posted_to_the_deposit_itself(r):
    """Fail closed: an unset write-off role leaves the settlement pending with
    the reason; it never falls back to the deposit account it credits."""
    r.env["ir.config_parameter"].sudo().set_param(P + "account.deposit.write_off", "")
    lease = _site_lease(r)
    wo = _cost_entry(
        r, _charge(r, "deposit_write_off", 5000.0, lease=lease, payment_method="internal")
    )
    assert wo.state == "pending" and not wo.move_id and wo.account_id != r.r["deposit"]
    assert any("deposit.write_off" in (b or "") for b in wo.message_ids.mapped("body"))
    _refused(
        _as(r, r.acct, "fix.asset.cost.entry").browse(wo.id).action_post_direct,
        match="deposit.write_off",
    )


# ============================================================ break penalty / licences
def test_break_penalty_of_a_commenced_lease_is_not_rent_clearing(r):
    """D5(a) clears the RENT of a commenced IFRS 16 lease; a break penalty on
    the same lease is its own role (500908), never the clearing."""
    lease = _site_lease(r)
    contract = _lease(r, commencement_date=month_start(r.today))
    contract.sudo().write({"site_lease_id": lease.id})
    _as(r, r.acct, "fix.lease").browse(contract.id).action_activate()
    penalty = _cost_entry(r, _charge(r, "lease_break_penalty", 70000.0, lease=lease))
    assert penalty.subtype == "break_penalty"
    assert penalty.account_id == r.r["penalty"] and penalty.account_id != r.a["clearing"]
    bill = _bill(r, r.landlord, [70000.0], ref="PEN-1")
    # no rent variance gate for a penalty: matched at its own figure
    _as(r, r.acct, "fix.asset.cost.entry").browse(penalty.id).action_match_bill(bill.id)
    move = _post_bill(bill)
    assert _lines(move, r.r["penalty"]).debit == 70000.0
    assert not _lines(move, r.a["clearing"])


@pytest.mark.parametrize(
    ("subtype", "account"),
    [("trade", "lic_trade"), ("fire", "lic"), ("agent", "lic"), ("penalty", "lic_pen")],
)
def test_licence_fee_kinds_take_their_account_roles(r, subtype, account):
    """D3: trade licence 500503, other licences 500209, late penalty 500121."""
    entry = _entry(r, "licence_fee", 1200.0, subtype=subtype)
    assert entry.account_id == r.r[account]


def test_a_fit_out_cost_is_never_expensed_for_want_of_its_role(r):
    """D1: a capitalised fit-out's cost is CWIP; without the fit_out role it
    has no account (refused at the match), never the repair expense."""
    entry = _entry(r, "facility_work_order", 9000.0, subtype="fit_out")
    assert entry.account_id == r.r["cwip"]
    r.env["ir.config_parameter"].sudo().set_param(P + "account.facility_work_order.fit_out", "")
    r.env["ir.config_parameter"].sudo().set_param(
        P + "account.facility_work_order", r.a["repair"].code
    )
    blind = _entry(r, "facility_work_order", 9000.0, subtype="fit_out")
    assert not blind.account_id
    _refused(
        _as(r, r.acct, "fix.asset.cost.entry").browse(blind.id).action_match_bill,
        _bill(r, r.vendor, [9000.0]).id,
        match="fit_out",
    )
    project = _entry(r, "facility_work_order", 9000.0, subtype="project")
    assert project.account_id == r.a["repair"]  # a non-capital project falls back


# ============================================================ M47-28 rent components
def test_rent_payment_splits_service_charge_and_adjusted_advance(r):
    """M47-28 / M47-08: the payment is rent + service charge - advance adjusted.
    Once the landlord's bill posts it, the service charge is expensed apart and
    the adjusted advance is consumed from the advance account, so the rent
    account carries the rent alone."""
    lease = _site_lease(
        r,
        service_charge=5000.0,
        advance_rent_amount=30000.0,
        advance_adjust_monthly=10000.0,
    )
    _charge(r, "advance_paid", 30000.0, lease=lease)
    row = lease.schedule_ids.filtered(lambda s: not s.historical).sorted("due_date")[0]
    row.sudo()._schedule_send()
    assert row.advance_adjusted == 10000.0 and row.service_charge_due == 5000.0
    sub = r.env.ref("%s.consumer_lease_rent_payment_requested" % MOD)
    Outbox = r.env["fix.event.outbox"]
    for ev in Outbox.search(
        [("event_type", "=", "lease.rent_payment_requested"), ("aggregate_id", "=", row.id)]
    ):
        assert Outbox._relay_deliver(sub, ev) == ""
    entry = _cost_entry(r, row)
    net = row.rent_due + 5000.0 - 10000.0
    assert entry.amount == net and entry.account_id == r.a["rent"]
    bill = _bill(r, r.landlord, [net], ref="RENT-R2A")
    _as(r, r.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill(bill.id)
    move = _post_bill(bill)
    comp = entry.component_move_id
    assert entry.state == "posted" and comp
    assert _lines(comp, r.r["service"]).debit == 5000.0
    assert _lines(comp, r.r["advance"]).credit == 10000.0
    rent_lines = _lines(move, r.a["rent"]) | _lines(comp, r.a["rent"])
    assert round(sum(rent_lines.mapped("balance")), 2) == row.rent_due
    # posted once, however often the bill's posting is replayed
    entry._m52_after_posted(move.date, move.name)
    assert entry.component_move_id == comp


# ============================================================ D6 draft leases
def test_a_lease_awaiting_approval_reaches_ifrs16_only_once_recorded(r):
    """D6: a lease awaiting the approval of its commitment drafts no IFRS 16
    contract, whatever event arrives; once recorded it does."""
    lease = _site_lease(r)
    lease.sudo()._guarded().write({"state": "draft"})
    Lease = r.env["fix.lease"].sudo()
    event = {"aggregate": "fix.site.lease", "aggregate_id": lease.id, "payload": {}}
    assert not Lease.consume_lease_recorded(event)
    extract = {
        "commencement": str(lease.start_date),
        "end_date": str(lease.end_date),
        "monthly_rent": 50000.0,
    }
    Lease.consume_lease_extract_published(
        dict(event, payload={"version": 1, "reason": "recorded", "extract": extract})
    )
    assert not Lease.search([("site_lease_id", "=", lease.id)])
    lease.sudo()._guarded().write({"state": "active"})
    contract = Lease.consume_lease_recorded(event)
    assert contract and contract.state == "draft" and contract.site_lease_id == lease


# ============================================================ D5(d) leased vehicles
def test_leased_vehicle_is_drafted_from_its_contract_with_the_exemptions(r):
    """FIN-09 / D5(d,e): the contract start and the monthly rent on the vehicle
    draft the IFRS 16 lease; 12 months or less is short-term, BDT 500,000 or
    less new is low-value."""
    start = month_start(r.today)
    van = _van(
        r,
        "R2A-L1-%s" % r.tag,
        fix_ownership_basis="leased",
        fix_contract_ref="LC-R2A-1",
        fix_contract_start=start,
        fix_contract_end=start + timedelta(days=3 * 365 - 1),
        fix_lease_monthly_rent=40000.0,
        acquisition_date=start - timedelta(days=90),
    )
    lease = r.env["fix.lease"].search([("vehicle_id", "=", van.id)])
    assert (lease.state, lease.exemption, lease.commencement_date) == ("draft", "none", start)
    assert lease.payment_amount == 40000.0 and lease.term_months == 36
    assert lease.operating_unit_id == r.ou
    short = _van(
        r,
        "R2A-L2-%s" % r.tag,
        fix_ownership_basis="leased",
        fix_contract_ref="LC-R2A-2",
        fix_contract_start=start,
        fix_contract_end=start + timedelta(days=300),
        fix_lease_monthly_rent=20000.0,
    )
    assert r.env["fix.lease"].search([("vehicle_id", "=", short.id)]).exemption == "short_term"
    cheap = _van(
        r,
        "R2A-L3-%s" % r.tag,
        fix_ownership_basis="leased",
        fix_contract_ref="LC-R2A-3",
        fix_contract_start=start,
        fix_contract_end=start + timedelta(days=3 * 365),
        fix_lease_monthly_rent=8000.0,
        net_car_value=350000.0,
    )
    assert r.env["fix.lease"].search([("vehicle_id", "=", cheap.id)]).exemption == "low_value"
    # a rent change on the draft follows the vehicle
    van.write({"fix_lease_monthly_rent": 42000.0})
    assert lease.payment_amount == 42000.0
    with pytest.raises(Exception, match="negative"), r.env.cr.savepoint():
        van.write({"fix_lease_monthly_rent": -1.0})


# ============================================================ FIN-20 cost per km
def test_cost_per_km_reads_the_ledger_costs_of_the_vehicle(r):
    """FIN-20: insurance and fines posted for a vehicle are in its running
    cost; a cost entry not yet posted is shown apart, never counted."""
    van = _van(r, "R2A-TCO-%s" % r.tag)
    vehicle_vals = {"vehicle_id": van.id, "vendor_id": False, "payment_method": "petty_cash"}
    insurance = _entry(r, "vehicle_insurance", 12000.0, **vehicle_vals)
    fine = _entry(r, "vehicle_fine", 3000.0, **vehicle_vals)
    assert insurance.state == "posted" and fine.state == "posted"
    pending = _entry(r, "vehicle_insurance_excess", 800.0, vehicle_id=van.id)
    assert pending.state == "pending"
    env = r.env(context=dict(r.env.context, allowed_company_ids=r.co.ids))
    report = m46_reports.cost_per_km(env, date_from=str(r.today - timedelta(days=5)))
    row = next(x for x in report["rows"] if x["plate"] == van.license_plate)
    assert row["insurance"] == 12000.0 and row["fines"] == 3000.0
    assert row["unposted"] == 800.0
    assert row["total_cost"] == 15000.0


# ============================================================ BRU-EAM-09 exit
def test_exit_clearance_waits_for_an_unrecovered_recharge(r):
    """D9/D20 / BRU-EAM-09: an HR-approved recharge still on 100049 holds the
    leaver's exit clearance; once collected, it clears."""
    r.a["emp_rec"].reconcile = True
    eq = r.env["fix.equipment"].create(
        {
            "code": "R2A-EQ-%s" % r.tag,
            "name": "R2A meter",
            "company_id": r.co.id,
            "operating_unit_id": r.ou.id,
            "acquisition_cost": 4000.0,
        }
    )
    loss = (
        r.env["fix.equipment.loss"]
        .sudo()
        .create({"equipment_id": eq.id, "kind": "lost", "circumstances": "left in a rickshaw"})
    )
    loss.sudo()._guarded().write({"recharge_employee_id": r.employee.id, "recharge_amount": 1500.0})
    rec = (
        r.env["fix.asset.recovery"]
        .sudo()
        .consume_equipment_recharge_requested(
            {
                "event_type": "equipment.recharge_requested",
                "aggregate": "fix.equipment.loss",
                "aggregate_id": loss.id,
                "payload": {"hr_approved_by_id": r.hr.id, "hr_approved_on": str(r.today)},
            }
        )
    )
    assert rec.state == "approved" and rec._recovery_outstanding() == 1500.0
    ex = r.env["fix.hr.exit"].create(
        {
            "employee_id": r.employee.id,
            "notice_date": r.today - timedelta(days=40),
            "last_working_day": r.today + timedelta(days=5),
            "clearance_it": True,
            "clearance_finance": True,
            "clearance_hr": True,
            "clearance_assets": True,
        }
    )
    _refused(ex.action_clear, match="recovery %s" % rec.name)
    # the leaver pays it back: the receivable is collected (reconciled)
    receivable = rec.move_id.line_ids.filtered(lambda ln: ln.account_id == r.a["emp_rec"])
    pay = r.env["account.move"].create(
        {
            "journal_id": r.journal.id,
            "line_ids": [
                (0, 0, {"account_id": r.a["petty"].id, "name": "repaid", "debit": 1500.0}),
                (
                    0,
                    0,
                    {
                        "account_id": r.a["emp_rec"].id,
                        "name": "repaid",
                        "credit": 1500.0,
                        "partner_id": receivable.partner_id.id,
                    },
                ),
            ],
        }
    )
    pay.action_post()
    (receivable | pay.line_ids.filtered(lambda ln: ln.account_id == r.a["emp_rec"])).reconcile()
    assert rec._recovery_outstanding() == 0.0
    assert not [h for h in ex._spine_assets_held() if "recovery" in h]
    ex.action_confirm_notice()
    ex.action_clear()
    assert ex.state == "cleared"


# ============================================================ FIN-26 branch rules
def _branch(r, code, ou):
    entity = r.env["fix.entity"].search([("company_id", "=", r.co.id)], limit=1) or r.env[
        "fix.entity"
    ].create({"code": "R2AE", "legal_name": "R2A entity", "company_id": r.co.id})
    return r.env["fix.branch"].create(
        {"name": "R2A %s" % code, "code": code, "entity_id": entity.id, "operating_unit_id": ou.id}
    )


def test_fin26_kits_audits_profiles_and_bulk_loads_follow_the_branch_unit(r):
    """FIN-26: a user of one branch neither reads nor finds another branch's
    kit, audit, equipment profile or bulk device load; a kit with no branch
    stays visible across the company (optional link)."""
    mine, other = _branch(r, "R2AB1", r.ou), _branch(r, "R2AB2", r.ou2)
    user = (
        r.env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "R2A branch user",
                "login": "r2a_branch_%s" % r.tag,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            r.env.ref("base.group_user").id,
                            r.env.ref("cd_equipment_register.group_equipment_custodian").id,
                        ],
                    )
                ],
                "company_ids": [(6, 0, r.co.ids)],
                "company_id": r.co.id,
                "assigned_operating_unit_ids": [(6, 0, r.ou.ids)],
                "default_operating_unit_id": r.ou.id,
            }
        )
    )
    Kit = r.env["fix.equipment.kit"].sudo()
    kits = {
        name: Kit.create(
            {
                "name": "R2A kit %s" % name,
                "code": "R2AK%s%s" % (name, r.tag),
                "company_id": r.co.id,
                **vals,
            }
        )
        for name, vals in (
            ("mine", {"branch_id": mine.id}),
            ("other", {"branch_id": other.id}),
            ("none", {}),
        )
    }
    seen = _as(r, user, "fix.equipment.kit").search([("id", "in", [k.id for k in kits.values()])])
    assert set(seen.ids) == {kits["mine"].id, kits["none"].id}
    Rule = r.env["ir.rule"].with_user(user)
    for model in ("fix.equipment.audit", "fix.branch.equipment.profile", "fix.device.bulk.load"):
        domain = Rule._compute_domain(model, "read")
        Model = r.env[model]
        assert Model.new({"branch_id": mine.id, "company_id": r.co.id}).filtered_domain(
            domain
        ), model
        assert not Model.new({"branch_id": other.id, "company_id": r.co.id}).filtered_domain(
            domain
        ), model


# ============================================================ M47-11 fit-out CWIP
def test_fit_out_cost_books_to_cwip_and_capitalises_on_m47_facts(r):
    """M47-11 / D1: a capitalised fit-out's posted cost line is booked to the
    project's CWIP (opened from its approved capex), and M47's completion
    (capitalisation_requested_on + _m47_capitalisation_facts) capitalises it
    over the shorter of the useful life and the remaining lease."""
    env = r.env
    category = env["fix.asset.category"].create(
        {
            "company_id": r.co.id,
            "code": "R2AFIT%s" % r.tag,
            "name": "R2A Fit-out",
            "useful_life_months": 120,
            "journal_id": r.journal.id,
            "asset_account_id": r.r["fit"].id,
            "accumulated_account_id": r.r["fit_acc"].id,
            "expense_account_id": r.r["fit_dep"].id,
            "cwip_account_id": r.r["cwip"].id,
        }
    )
    _site_lease(r)  # active: about 36 months left
    req = env["fix.capex.request"].create(
        {
            "title": "R2A fit-out capex",
            "amount": 500000.0,
            "company_id": r.co.id,
            "operating_unit_id": r.ou.id,
            "category_id": category.id,
            "state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_5",
            "dofa_approved_amount": 500000.0,
        }
    )
    project = env["fix.site.project"].create(
        {"site_id": r.site.id, "project_type": "open", "budget": 500000.0}
    )
    project.sudo().write({"capex_request_id": req.id})
    cost = (
        env["fix.site.project.cost"]
        .sudo()
        .create(
            {
                "project_id": project.id,
                "description": "Shopfront and racking",
                "vendor_id": r.vendor.id,
                "invoice_ref": "FIT-R2A-1",
                "amount": 200000.0,
            }
        )
    )
    entry = env["fix.asset.cost.entry"]._m52_queue(
        cost,
        {
            "cost_type": "facility_work_order",
            "subtype": "fit_out",
            "company_id": r.co.id,
            "operating_unit_id": r.ou.id,
            "site_id": r.site.id,
            "amount": 200000.0,
            "cost_date": r.today,
            "vendor_id": r.vendor.id,
            "invoice_ref": "FIT-R2A-1",
            "payment_method": "vendor_bill",
        },
    )
    assert entry.account_id == r.r["cwip"]
    bill = _bill(r, r.vendor, [200000.0], ref="FIT-R2A-1")
    _as(r, r.acct, "fix.asset.cost.entry").browse(entry.id).action_match_bill(bill.id)
    move = _post_bill(bill)
    assert _lines(move, r.r["cwip"]).debit == 200000.0
    cwip = req.cwip_ids
    assert len(cwip) == 1 and cwip.amount == 200000.0 and cwip.operating_unit_id == r.ou
    assert project.cwip_res_id == cwip.id
    # a project M47 did not ask to capitalise is left alone
    Capex = env["fix.capex.request"].sudo()
    assert not Capex._bridge_capitalise_site_project(project)
    project.sudo()._guarded().write(
        {"state": "done", "done_on": r.today, "capitalisation_requested_on": r.today}
    )
    facts = project._m47_capitalisation_facts()
    asset = Capex._bridge_capitalise_site_project(project)
    assert asset.gross == 200000.0 and asset.operating_unit_id == r.ou
    assert asset.life_months == facts["life_months"] and asset.life_months < 120
    assert cwip.state == "capitalised"
