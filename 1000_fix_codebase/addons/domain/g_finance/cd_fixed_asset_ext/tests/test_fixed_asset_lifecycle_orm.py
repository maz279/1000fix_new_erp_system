# cd_fixed_asset_ext — live-ORM behaviour of the M49 capex, transfer,
# revaluation/impairment, disposal, physical verification and IFRS 16 lease
# documents.
from __future__ import annotations

from datetime import date

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

from ..models.fix_lease import lease_present_value
from .conftest import balance

pytestmark = [pytest.mark.financial]


def _active_asset(m49, **vals):
    base = {
        "name": "Spectrum analyser",
        "category_id": m49["category"].id,
        "gross": 100000.0,
        "salvage": 0.0,
        "life_months": 50,
        "purchase_date": date(2026, 1, 1),
        "state": "active",
    }
    base.update(vals)
    return m49["env"]["fix.fixed.asset"].create(base)


def _depreciate(m49, asset, month):
    run = m49["env"]["fix.asset.depreciation.run"].create(
        {"period_start": date(2026, month, 1), "asset_ids": [(6, 0, asset.ids)]}
    )
    run.action_compute()
    run.action_post()
    return run


# ---------------------------------------------------------------- capex
class TestCapex:
    def _budget(self, m49, amount=1000000.0):
        env, users = m49["env"], m49["users"]
        budget = (
            env["fix.capex.budget"]
            .with_user(users["accountant"])
            .create(
                {
                    "name": "FY2026-27 Capex",
                    "fiscal_year": "FY2026-27",
                    "date_from": date(2026, 7, 1),
                    "date_to": date(2027, 6, 30),
                    "amount": amount,
                }
            )
        )
        return budget.with_env(env)

    def test_request_to_cwip_to_asset_consumes_budget(self, m49):
        env, users, cat = m49["env"], m49["users"], m49["category"]
        budget = self._budget(m49)
        with pytest.raises(UserError, match="segregation of duties"), env.cr.savepoint():
            budget.with_user(users["accountant"]).sudo().action_approve()
        budget.with_user(users["manager"]).action_approve()
        assert budget.approved_by_id == users["manager"]

        req = (
            env["fix.capex.request"]
            .with_user(users["manager"])
            .create(
                {
                    "title": "Diagnostic benches for Mirpur",
                    "budget_id": budget.id,
                    "category_id": cat.id,
                    "amount": 400000.0,
                    "request_date": date(2026, 8, 1),
                }
            )
        )
        assert req.name.startswith("CAPEX/")
        req.action_submit()
        with pytest.raises(UserError, match="segregation of duties"), env.cr.savepoint():
            req.with_user(users["manager"]).action_approve()
        with pytest.raises(UserError, match="accounting manager"), env.cr.savepoint():
            req.with_user(users["accountant"]).action_approve()
        req.with_user(users["manager2"]).action_approve()
        assert (req.state, budget.committed_amount, budget.available_amount) == (
            "approved",
            400000.0,
            600000.0,
        )
        res = req.with_user(users["accountant"]).action_create_cwip()
        cwip = env["fix.cwip.entry"].browse(res["cwip_ids"])
        assert (req.state, cwip.capex_request_id, cwip.category_id) == ("cwip", req, cat)
        cwip.amount = 450000.0
        with pytest.raises(UserError, match="supplementary capex"), env.cr.savepoint():
            cwip.action_capitalise()
        cwip.amount = 380000.0
        asset = cwip.action_capitalise()
        assert (req.state, asset.capex_request_id, budget.actual_amount) == (
            "capitalised",
            req,
            380000.0,
        )

    def test_approval_refused_above_available_budget(self, m49):
        env, users = m49["env"], m49["users"]
        budget = self._budget(m49, amount=100000.0)
        budget.with_user(users["manager"]).action_approve()
        req = env["fix.capex.request"].create(
            {
                "title": "Van",
                "budget_id": budget.id,
                "amount": 150000.0,
                "request_date": date(2026, 9, 1),
            }
        )
        req.action_submit()
        with pytest.raises(UserError, match="exceeds the budget"), env.cr.savepoint():
            req.with_user(users["manager"]).action_approve()
        req.with_user(users["manager"]).action_reject()
        assert req.state == "rejected"

    def test_submit_needs_budget_and_amount(self, m49):
        env = m49["env"]
        with pytest.raises(ValidationError), env.cr.savepoint():
            env["fix.capex.request"].create({"title": "Zero", "amount": 0.0})
        req = env["fix.capex.request"].create({"title": "No budget", "amount": 10.0})
        with pytest.raises(UserError, match="capital budget"), env.cr.savepoint():
            req.action_submit()


# ---------------------------------------------------------------- transfers
class TestTransfer:
    def test_branch_and_custodian_move_with_history(self, m49):
        env = m49["env"]
        ous = env["operating.unit"].create(
            [
                {
                    "name": f"M49 Branch {code}",
                    "code": f"M49{code}",
                    "partner_id": env.company.partner_id.id,
                    "company_id": env.company.id,
                }
                for code in ("TA", "TB")
            ]
        )
        emp = env["hr.employee"].create({"name": "Technician M49"})
        asset = _active_asset(m49, operating_unit_id=ous[0].id)
        tr = env["fix.asset.transfer"].create(
            {"asset_id": asset.id, "operating_unit_id": ous[1].id, "to_custodian_id": emp.id}
        )
        tr.action_confirm()
        assert (asset.operating_unit_id, asset.custodian_id) == (ous[1], emp)
        assert (tr.from_operating_unit_id, tr.state) == (ous[0], "done")
        assert asset.transfer_ids == tr
        same = env["fix.asset.transfer"].create({"asset_id": asset.id})
        with pytest.raises(UserError, match="nothing would move"), env.cr.savepoint():
            same.action_confirm()


# ---------------------------------------------------------------- revaluation
class TestRevaluationImpairment:
    def _doc(self, m49, asset, kind, value):
        users = m49["users"]
        return (
            m49["env"]["fix.asset.revaluation"]
            .with_user(users["manager"])
            .create({"asset_id": asset.id, "kind": kind, "new_value": value})
            .with_env(m49["env"])
        )

    def test_revaluation_up_then_down_and_impairment(self, m49):
        env, acc, users = m49["env"], m49["accounts"], m49["users"]
        asset = _active_asset(m49)
        _depreciate(m49, asset, 1)  # 2,000 -> NBV 98,000
        up = self._doc(m49, asset, "revaluation", 110000.0)
        with pytest.raises(UserError, match="segregation of duties"), env.cr.savepoint():
            up.with_user(users["manager"]).action_post()
        up.with_user(users["manager2"]).action_post()
        assert (up.cost_delta, up.surplus_amount, up.pl_amount) == (12000.0, 12000.0, 0.0)
        assert balance(env, acc["surplus"]) == -12000.0
        assert asset.book_nbv == 110000.0 and asset.revaluation_surplus == 12000.0
        # decrease: first against the surplus (IAS 16.40), the rest to P&L
        down = self._doc(m49, asset, "revaluation", 90000.0)
        down.with_user(users["manager2"]).action_post()
        assert (down.surplus_amount, down.pl_amount) == (-12000.0, 8000.0)
        assert balance(env, acc["impair"]) == 8000.0
        # impairment (IAS 36): no surplus left -> all to P&L, via accumulated
        imp = self._doc(m49, asset, "impairment", 85000.0)
        imp.with_user(users["manager2"]).action_post()
        assert (imp.accum_delta, imp.pl_amount, asset.book_nbv) == (5000.0, 5000.0, 85000.0)
        # reversal capped at the net impairment recognised
        too_much = self._doc(m49, asset, "impairment_reversal", 95000.0)
        with pytest.raises(UserError, match="capped"), env.cr.savepoint():
            too_much.with_user(users["manager2"]).action_post()
        rev = self._doc(m49, asset, "impairment_reversal", 88000.0)
        rev.with_user(users["manager2"]).action_post()
        assert (rev.accum_delta, asset.book_nbv) == (-3000.0, 88000.0)
        # next month's charge re-spreads the new carrying amount
        assert asset._book_amount(date(2026, 2, 1)) == round(88000.0 / 49, 2)

    def test_impairment_needs_a_lower_recoverable_amount(self, m49):
        asset = _active_asset(m49)
        doc = self._doc(m49, asset, "impairment", 120000.0)
        with pytest.raises(UserError, match="no impairment"), m49["env"].cr.savepoint():
            doc.with_user(m49["users"]["manager2"]).action_post()


# ---------------------------------------------------------------- disposal
class TestDisposal:
    def test_sale_with_gain_and_write_off_with_loss(self, m49):
        env, acc, users = m49["env"], m49["accounts"], m49["users"]
        asset = _active_asset(m49)
        _depreciate(m49, asset, 1)  # NBV 98,000
        sale = (
            env["fix.asset.disposal"]
            .with_user(users["manager"])
            .create(
                {
                    "asset_id": asset.id,
                    "kind": "sale",
                    "proceeds": 100000.0,
                    "proceeds_account_id": acc["proceeds"].id,
                    "date": date(2026, 2, 15),
                }
            )
            .with_env(env)
        )
        with pytest.raises(UserError, match="Approve the disposal"), env.cr.savepoint():
            sale.action_post()
        with pytest.raises(UserError, match="segregation of duties"), env.cr.savepoint():
            sale.with_user(users["manager"]).action_approve()
        sale.with_user(users["manager2"]).action_approve()
        sale.with_user(users["accountant"]).action_post()
        assert (sale.cost, sale.accumulated, sale.nbv, sale.gain_loss) == (
            100000.0,
            2000.0,
            98000.0,
            2000.0,
        )
        assert (asset.state, asset.disposal_date) == ("disposed", date(2026, 2, 15))
        assert balance(env, acc["gain"]) == -2000.0
        assert balance(env, acc["asset"]) == -100000.0  # cost removed (acquired outside M49)
        assert balance(env, acc["accum"]) == 0.0

        lost = _active_asset(m49, name="Lost multimeter", gross=5000.0)
        wo = lost.action_dispose()
        doc = env["fix.asset.disposal"].browse(wo["disposal_ids"])
        doc.with_user(users["manager2"]).action_approve()
        doc.action_post()
        assert (doc.gain_loss, lost.state) == (-5000.0, "disposed")
        assert balance(env, acc["loss"]) == 5000.0

    def test_write_off_has_no_proceeds(self, m49):
        asset = _active_asset(m49)
        with pytest.raises(ValidationError, match="no proceeds"), m49["env"].cr.savepoint():
            m49["env"]["fix.asset.disposal"].create(
                {"asset_id": asset.id, "kind": "write_off", "proceeds": 10.0}
            )


# ---------------------------------------------------------------- verification
class TestPhysicalVerification:
    def test_campaign_scan_found_unregistered_and_missing(self, m49):
        env = m49["env"]
        company = env["res.company"].create({"name": "M49 Verification Co"})
        cat = m49["category"].copy({"company_id": company.id, "code": "VERIFY"})
        Asset = env["fix.fixed.asset"]
        a = Asset.create(
            {
                "name": "A",
                "category_id": cat.id,
                "gross": 10.0,
                "life_months": 10,
                "purchase_date": date(2026, 1, 1),
                "state": "active",
                "company_id": company.id,
            }
        )
        b = Asset.create(
            {
                "name": "B",
                "category_id": cat.id,
                "gross": 10.0,
                "life_months": 10,
                "purchase_date": date(2026, 1, 1),
                "state": "active",
                "company_id": company.id,
            }
        )
        camp = env["fix.asset.verification.campaign"].create(
            {"name": "Q3 count", "company_id": company.id}
        )
        with pytest.raises(UserError, match="Start the campaign"), env.cr.savepoint():
            camp.action_record_scan(a.code)
        camp.action_start()
        assert camp.expected_count == 2 and camp.pending_count == 2
        assert camp.action_record_scan(a.code)["result"] == "found"
        assert camp.action_record_scan("UNKNOWN-TAG-1")["result"] == "unregistered"
        camp.action_close()
        assert (camp.found_count, camp.missing_count, camp.unregistered_count) == (1, 1, 1)
        assert camp.line_ids.filtered(lambda ln: ln.asset_id == b).result == "missing"


# ---------------------------------------------------------------- leases
class TestLease:
    def _lease(self, m49, **vals):
        env, acc, cat = m49["env"], m49["accounts"], m49["category"]
        if "rou_cat" not in m49:
            m49["rou_cat"] = cat.copy({"code": "ROU-T", "name": "Test ROU", "tax_rate_code": False})
        rou_cat = m49["rou_cat"]
        base = {
            "name": "Elephant Rd branch",
            "category_id": rou_cat.id,
            "commencement_date": date(2026, 7, 1),
            "term_months": 24,
            "payment_amount": 50000.0,
            "payment_timing": "advance",
            "ibr_percent": 12.0,
            "initial_direct_costs": 10000.0,
            "liability_account_id": acc["liability"].id,
            "interest_account_id": acc["interest"].id,
            "payment_account_id": acc["rent"].id,
        }
        base.update(vals)
        return env["fix.lease"].create(base)

    def test_recognition_schedule_and_monthly_postings(self, m49):
        env, acc = m49["env"], m49["accounts"]
        lease = self._lease(m49)
        pv = lease_present_value(50000.0, 24, 0.01, True)
        assert lease.pv_preview == pv
        lease.action_activate()
        assert (lease.state, lease.initial_liability, lease.rou_amount) == (
            "active",
            pv,
            round(pv + 10000.0, 2),
        )
        lines = lease.schedule_line_ids.sorted("sequence")
        assert len(lines) == 24 and lines[-1].closing == 0.0
        assert round(sum(lines.mapped("principal")), 2) == pv
        assert lines[0].interest == round((pv - 50000.0) * 0.01, 2)
        assert round(sum(lines.mapped("depreciation")), 2) == lease.rou_amount
        rou = lease.asset_id
        assert (rou.gross, rou.life_months, rou.lease_id) == (lease.rou_amount, 24, lease)
        assert balance(env, acc["liability"]) == -pv
        # month 2 cannot post before month 1
        with pytest.raises(UserError, match="earlier months"), env.cr.savepoint():
            lines[1].action_post()
        lines[0].action_post()
        assert balance(env, acc["interest"]) == lines[0].interest
        assert balance(env, acc["liability"]) == -lines[0].closing
        dep = rou.depreciation_line_ids
        assert (dep.period_start, dep.amount) == (date(2026, 7, 1), lines[0].depreciation)
        with pytest.raises(UserError, match="already posted"), env.cr.savepoint():
            lines[0].action_post()
        assert lease.liability_balance == lines[0].closing

    def test_post_due_posts_up_to_this_month(self, m49):
        # see the note on context_today in test_fixed_asset_orm.py
        today = fields.Date.context_today(m49["env"].user) if "env" in m49 else fields.Date.today()
        lease = self._lease(m49, commencement_date=date(today.year, today.month, 1), term_months=6)
        lease.action_activate()
        lease.action_post_due()
        assert lease.schedule_line_ids.filtered(lambda ln: ln.state == "posted").mapped(
            "sequence"
        ) == [1]

    def test_exempt_and_unconfigured_leases_are_refused(self, m49):
        env = m49["env"]
        short = self._lease(m49, term_months=12, exemption="short_term")
        with pytest.raises(UserError, match="exempt"), env.cr.savepoint():
            short.action_activate()
        with pytest.raises(ValidationError, match="12 months or less"), env.cr.savepoint():
            self._lease(m49, term_months=24, exemption="short_term")
        bare = self._lease(m49, liability_account_id=False)
        with pytest.raises(UserError, match="Lease Liability Account"), env.cr.savepoint():
            bare.action_activate()
        assert not bare.schedule_line_ids and bare.state == "draft"
