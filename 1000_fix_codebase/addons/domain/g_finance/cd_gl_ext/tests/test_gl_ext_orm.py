# cd_gl_ext — live-ORM behaviour of the M19 core (DoD-03 statutory set).
#
# Runs against the rolled-back `fix_test` database (addons/conftest.py
# `odoo_env`). Every money expectation is written out by hand as a Decimal.
from __future__ import annotations

import hashlib
import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from odoo.addons.cd_gl_ext.tests.test_e3_vat_close_step import reconciled_vat_return
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

D = Decimal

SAMPLE_CSV = """account_code,entity_code,account_name,account_type,account_subtype,is_postable,is_control_account,control_subledger,requires_dimension,statutory_group,active
1-00-00-000,EN-01,Total Assets,asset,current_asset,FALSE,FALSE,,,Assets,TRUE
1-10-00-000,EN-01,Current Assets,asset,current_asset,FALSE,FALSE,,,Assets,TRUE
1-10-10-010,EN-01,Cash in Hand,asset,cash,TRUE,FALSE,,cost_centre;branch,Cash & Bank,TRUE
1-20-10-010,EN-01,Trade Debtors,asset,receivable,TRUE,TRUE,receivable,branch,Receivables,TRUE
2-00-00-000,EN-01,Total Liabilities,liability,liability,FALSE,FALSE,,,Liabilities,TRUE
2-10-10-010,EN-01,Trade Creditors,liability,payable,TRUE,TRUE,payable,,Payables,TRUE
3-00-00-000,EN-01,Total Equity,equity,equity,FALSE,FALSE,,,Equity,TRUE
3-10-10-010,EN-01,Share Capital,equity,equity,TRUE,FALSE,,,Equity,TRUE
"""


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _account(env, code="1-10-10-010", **overrides):
    vals = {
        "account_code": code,
        "name": "Cash in hand - branch",
        "account_type": "asset",
        "account_subtype": "cash",
        "is_postable": True,
        "statutory_group": "Current assets",
    }
    vals.update(overrides)
    return env["fix.chart.account"].create(vals)


# --------------------------------------------------------------------------- fix.chart.account


@pytest.mark.unlinked_chart
class TestChartAccountConstraints:
    def test_valid_leaf_account_defaults_to_bdt(self, odoo_env):
        acc = _account(odoo_env, requires_dimension="branch;cost_centre")
        assert acc.currency_id == odoo_env.ref("base.BDT")
        assert acc.active is True
        assert acc.company_id == odoo_env.company

    def test_postable_summary_account_refused_coa01(self, odoo_env):
        with pytest.raises(ValidationError, match="ERR-COA-001"), odoo_env.cr.savepoint():
            _account(odoo_env, code="1-10-10-000")

    def test_type_block_must_match_account_type(self, odoo_env):
        with pytest.raises(ValidationError, match="HIER-TYPE"), odoo_env.cr.savepoint():
            _account(odoo_env, code="2-10-10-010")  # liability block, asset type

    def test_writing_account_type_revalidates(self, odoo_env):
        """Regression: account_type was not in @api.constrains, so a write
        could put an asset type on a liability code unchecked."""
        acc = _account(odoo_env)
        with pytest.raises(ValidationError, match="HIER-TYPE"), odoo_env.cr.savepoint():
            acc.write({"account_type": "expense"})

    def test_writing_control_flag_without_subledger_revalidates(self, odoo_env):
        """Regression: is_control_account/control_subledger were not
        constrained fields — CTRL-REQ could be bypassed on write."""
        acc = _account(odoo_env)
        with pytest.raises(ValidationError, match="CTRL-REQ"), odoo_env.cr.savepoint():
            acc.write({"is_control_account": True})

    def test_writing_unknown_dimension_revalidates(self, odoo_env):
        acc = _account(odoo_env)
        with pytest.raises(ValidationError, match="DIM-FMT"), odoo_env.cr.savepoint():
            acc.write({"requires_dimension": "branch;project"})

    def test_blank_dimension_items_are_ignored(self, odoo_env):
        acc = _account(odoo_env, requires_dimension="branch;")
        assert acc.requires_dimension == "branch;"

    def test_archive_refused_with_non_zero_balance_coa04(self, odoo_env):
        acc = _account(odoo_env, balance=1250.5)
        with (
            pytest.raises(UserError, match=r"non-zero balance 1250\.50 BDT \(COA-04\)"),
            odoo_env.cr.savepoint(),
        ):
            acc.action_archive()
        assert acc.active is True

    def test_archive_with_zero_balance(self, odoo_env):
        acc = _account(odoo_env)
        acc.action_archive()
        assert acc.active is False


# --------------------------------------------------------------------------- fix.chart.loader


@pytest.mark.unlinked_chart
class TestChartLoader:
    def test_load_sample_chart_creates_accounts_and_event(self, odoo_env):
        loader = odoo_env["fix.chart.loader"].create({})
        result = loader.action_load_from_csv(SAMPLE_CSV)

        expected_sha = hashlib.sha256(SAMPLE_CSV.encode("utf-8")).hexdigest()
        assert result == {
            "status": "loaded",
            "account_count": 8,
            "postable_count": 4,
            "sha256": expected_sha,
        }
        assert loader.state == "loaded"
        assert (loader.account_count, loader.postable_count, loader.control_count) == (8, 4, 2)
        assert loader.checksum == expected_sha
        cash = odoo_env["fix.chart.account"].search([("account_code", "=", "1-10-10-010")])
        assert cash.requires_dimension == "branch;cost_centre"  # sorted on load
        debtors = odoo_env["fix.chart.account"].search([("account_code", "=", "1-20-10-010")])
        assert (debtors.is_control_account, debtors.control_subledger) == (True, "receivable")
        assert _events(odoo_env, "coa.loaded", loader.id) == [
            {
                "company_id": odoo_env.company.id,
                "account_count": 8,
                "postable_count": 4,
                "sha256": expected_sha,
            }
        ]

    def test_reload_updates_in_place_with_operating_unit(self, odoo_env):
        ou = odoo_env["operating.unit"].search([], limit=1)
        loader = odoo_env["fix.chart.loader"].create({"operating_unit_id": ou.id})
        loader.action_load_from_csv(SAMPLE_CSV)
        renamed = SAMPLE_CSV.replace("Share Capital", "Paid-up share capital")
        loader.action_load_from_csv(renamed)
        capital = odoo_env["fix.chart.account"].search([("account_code", "=", "3-10-10-010")])
        assert len(capital) == 1
        assert capital.name == "Paid-up share capital"
        assert capital.operating_unit_id == ou

    def test_reload_after_archiving_an_account(self, odoo_env):
        """Regression: the existence check ignored archived accounts, so a
        reload tried to re-create an archived code and hit the
        (company, account_code) unique key."""
        loader = odoo_env["fix.chart.loader"].create({})
        loader.action_load_from_csv(SAMPLE_CSV)
        capital = odoo_env["fix.chart.account"].search([("account_code", "=", "3-10-10-010")])
        capital.action_archive()
        loader.action_load_from_csv(SAMPLE_CSV)
        all_capital = (
            odoo_env["fix.chart.account"]
            .with_context(active_test=False)
            .search([("account_code", "=", "3-10-10-010")])
        )
        assert all_capital == capital
        assert capital.active is True  # the CSV row says active=TRUE

    def test_invalid_chart_is_refused_and_writes_nothing(self, odoo_env):
        orphan = SAMPLE_CSV.replace("3-00-00-000,EN-01,Total Equity", "3-90-00-000,EN-01,Equity")
        loader = odoo_env["fix.chart.loader"].create({})
        with pytest.raises(UserError, match="PARENT-MISSING"), odoo_env.cr.savepoint():
            loader.action_load_from_csv(orphan)
        assert odoo_env["fix.chart.account"].search_count([]) == 0
        assert loader.state == "draft"

    def test_load_default_statutory_file(self, odoo_env):
        loader = odoo_env["fix.chart.loader"].create({})
        result = loader.action_load_from_csv()
        # MD-035_Chart_of_Accounts_Bangladesh.csv: 79 rows, 60 postable, 28 control
        assert (result["account_count"], result["postable_count"]) == (79, 60)
        assert loader.control_count == 28
        suspense = odoo_env["fix.chart.account"].search([("account_code", "=", "1-10-99-999")])
        assert suspense.name == "Inventory valuation suspense"

    def test_missing_master_file_raises(self, odoo_env):
        loader = odoo_env["fix.chart.loader"].create({"source_file": "no/such/file.csv"})
        with pytest.raises(UserError, match="Master data file not found"), odoo_env.cr.savepoint():
            loader.action_load_from_csv()

    def test_reconcile_without_accounts_raises(self, odoo_env):
        company = odoo_env["res.company"].create({"name": "Empty Chart Co"})
        loader = odoo_env["fix.chart.loader"].create({"company_id": company.id})
        with pytest.raises(UserError, match="No accounts loaded"), odoo_env.cr.savepoint():
            loader.action_reconcile_chart()

    def _ledger_chart(self, env, legs, link=True):
        """A fresh company with the sample chart loaded, each statutory
        account linked to a real Odoo account, and ONE posted entry made of
        `legs` = {statutory code or 'UNMAPPED': signed amount (+ debit)}."""
        company = env["res.company"].create({"name": "CoA Recon Test Co"})
        loader = env["fix.chart.loader"].create({"company_id": company.id})
        loader.action_load_from_csv(SAMPLE_CSV)
        journal = env["account.journal"].create(
            {"name": "Recon", "code": "RCN", "type": "general", "company_id": company.id}
        )
        types = {"1": "asset_current", "2": "liability_current", "3": "equity"}
        accounts = {}
        for n, code in enumerate(sorted(legs), start=1):
            odoo_account = env["account.account"].create(
                {
                    "code": "77%04d" % n,
                    "name": "Recon %s" % code,
                    "account_type": types.get(code[0], "asset_current"),
                    "company_ids": [(6, 0, company.ids)],
                }
            )
            accounts[code] = odoo_account
            if link and code != "UNMAPPED":
                env["fix.chart.account"].search(
                    [("company_id", "=", company.id), ("account_code", "=", code)]
                ).odoo_account_id = odoo_account
        move = env["account.move"].create(
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": date(2026, 3, 1),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": code,
                            "account_id": accounts[code].id,
                            "debit": max(amount, 0.0),
                            "credit": max(-amount, 0.0),
                        },
                    )
                    for code, amount in legs.items()
                ],
            }
        )
        move.action_post()
        return loader

    def test_reconcile_balanced_trial_balance(self, odoo_env):
        # Assets 1,500.00 (cash 1,000.00 + debtors 500.00)
        # = liabilities 400.00 + equity 1,100.00 — from the posted ledger
        loader = self._ledger_chart(
            odoo_env,
            {
                "1-10-10-010": 1000.0,
                "1-20-10-010": 500.0,
                "2-10-10-010": -400.0,
                "3-10-10-010": -1100.0,
            },
        )
        result = loader.action_reconcile_chart()
        assert result["reconciled"] is True
        assert _money(result["total_assets"]) == D("1500.00")
        assert _money(result["total_liabilities"]) == D("400.00")
        assert _money(result["total_equity"]) == D("1100.00")
        assert _money(result["discrepancy"]) == D("0.00")
        assert result["unmapped_ledger_accounts"] == 0
        assert loader.state == "reconciled" and loader.reconciled_at
        assert loader.linked_count == 4

    def test_unmapped_ledger_balance_is_not_marked_reconciled(self, odoo_env):
        """Regression: the loader was stamped 'reconciled' whatever the
        discrepancy (MD-035 §6 requires an exact reconciliation), and the
        reconciliation read typed-in balances instead of the ledger."""
        loader = self._ledger_chart(
            odoo_env, {"1-10-10-010": 1000.0, "2-10-10-010": -400.0, "UNMAPPED": -600.0}
        )
        result = loader.action_reconcile_chart()
        assert result["reconciled"] is False
        assert _money(result["discrepancy"]) == D("600.00")  # 1000 - 400
        assert result["unmapped_ledger_accounts"] == 1
        assert _money(result["unmapped_ledger_balance"]) == D("600.00")
        assert loader.state == "loaded"
        assert (loader.unmapped_ledger_count, _money(loader.recon_discrepancy)) == (
            1,
            D("600.00"),
        )

    def test_typed_balances_are_not_the_ledger(self, odoo_env):
        company = odoo_env["res.company"].create({"name": "CoA Typed Balance Co"})
        loader = odoo_env["fix.chart.loader"].create({"company_id": company.id})
        loader.action_load_from_csv(SAMPLE_CSV)
        odoo_env["fix.chart.account"].search(
            [("company_id", "=", company.id), ("account_code", "=", "1-10-10-010")]
        ).balance = 1000.0
        result = loader.action_reconcile_chart()
        assert result["total_assets"] == 0.0  # the typed 1,000 is not a posting

    def test_archive_refused_while_the_linked_ledger_carries_a_balance(self, odoo_env):
        loader = self._ledger_chart(odoo_env, {"1-10-10-010": 250.0, "3-10-10-010": -250.0})
        cash = odoo_env["fix.chart.account"].search(
            [("company_id", "=", loader.company_id.id), ("account_code", "=", "1-10-10-010")]
        )
        assert cash.balance == 0.0
        with pytest.raises(UserError, match=r"ledger balance 250.00"), odoo_env.cr.savepoint():
            cash.action_archive()
        assert cash.active


# --------------------------------------------------------------------------- fix.period.close


def _close(env, period_end=date(2026, 9, 30), **vals):
    return env["fix.period.close"].create({"period_end": period_end, **vals})


class TestPeriodClose:
    def test_target_and_default_sla(self, odoo_env):
        close = _close(odoo_env)
        assert close.target_completion_date == date(2026, 10, 5)
        assert close.sla_status == "within_sla"
        assert close.close_duration_days == 0.0
        assert close.currency_id == odoo_env.ref("base.BDT")

    def test_target_is_empty_without_period_end(self, odoo_env):
        draft = odoo_env["fix.period.close"].new({})
        assert draft.target_completion_date is False

    def test_standard_steps_and_ready_gate(self, odoo_env):
        close = _close(odoo_env)
        assert close.action_generate_standard_steps() is True
        assert close.state == "in_progress"
        assert len(close.line_ids) == 10
        assert close.line_ids.filtered(lambda s: not s.blocking).mapped("sequence") == [70]

        with (
            pytest.raises(UserError, match="Close steps still open: Subledger Cut-Off"),
            odoo_env.cr.savepoint(),
        ):
            close.action_ready()

        reconciled_vat_return(odoo_env, close.company_id, close.period_end)  # C10
        close.line_ids.filtered("blocking").action_mark_done("TB-2026-09")
        assert set(close.line_ids.filtered("blocking").mapped("evidence_ref")) == {"TB-2026-09"}
        close.suspense_closing = 2500.0
        with (
            pytest.raises(UserError, match=r"Suspense account must be zero .* balance: 2500\.00"),
            odoo_env.cr.savepoint(),
        ):
            close.action_ready()

        close.suspense_closing = 0.0
        close.action_ready()
        assert close.state == "ready_to_close"

    def test_close_requires_ready_check(self, odoo_env):
        close = _close(odoo_env)
        with (
            pytest.raises(UserError, match="Run the ready check before closing"),
            odoo_env.cr.savepoint(),
        ):
            close.action_close()

    def test_close_within_sla_publishes_event(self, odoo_env):
        period_end = date.today() - timedelta(days=2)
        close = _close(odoo_env, period_end=period_end, state="ready_to_close")
        close.action_close()
        assert close.state == "closed"
        assert close.close_duration_days == 2.0
        assert close.sla_status == "within_sla"
        assert _events(odoo_env, "period.closed", close.id) == [
            {
                "company_id": odoo_env.company.id,
                "period_end": str(period_end),
                "duration_days": 2.0,
                "sla_status": "within_sla",
                "step_count": 0,
            }
        ]

    def test_breached_close_logs_and_reports(self, odoo_env, caplog):
        period_end = date.today() - timedelta(days=9)
        close = _close(odoo_env, period_end=period_end, state="ready_to_close")
        with caplog.at_level(logging.WARNING):
            close.action_close()
        assert close.sla_status == "breached"
        assert close.close_duration_days == 9.0
        assert "G3-04 breach: close took 9.0 days (target 5)" in caplog.text
        report = odoo_env["fix.period.close"].action_fail_close_target()
        assert [(r["id"], r["close_duration_days"]) for r in report] == [(close.id, 9.0)]

    @staticmethod
    def _suspense_company(odoo_env):
        """A private company with the suspense (110999) and inventory accounts
        and a journal - the cutover entry is a real posted move."""
        company = _fresh_company(odoo_env, "suspense")
        env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
        accounts = env["account.account"].with_company(company)

        def acc(code, account_type):
            return accounts.create(
                {
                    "code": code,
                    "name": code,
                    "account_type": account_type,
                    "company_ids": [(6, 0, company.ids)],
                }
            )

        suspense_acc = acc("110999", "asset_current")
        inventory_acc = acc("110100", "asset_current")
        journal = env["account.journal"].create(
            {"name": "Cutover", "code": "CUT", "type": "general", "company_id": company.id}
        )

        def cutover(amount, post=True):
            move = env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "date": date(2026, 9, 30),
                    "line_ids": [
                        (0, 0, {"name": "inv", "account_id": inventory_acc.id, "debit": amount}),
                        (0, 0, {"name": "susp", "account_id": suspense_acc.id, "credit": amount}),
                    ],
                }
            )
            if post:
                move.action_post()
            return move

        part = env["fix.spare.part"].create(
            {"name": "LCD panel", "part_number": "LCD-14", "part_category": "display"}
        )
        return env, company, part, cutover

    def test_inventory_suspense_cutover(self, odoo_env):
        env, company, part, cutover = self._suspense_company(odoo_env)
        suspense = env["fix.inventory.valuation.suspense"]
        e1 = suspense.create({"product_id": part.id, "quantity": 2.0, "unit_cost": 600.0})
        e2 = suspense.create({"product_id": part.id, "quantity": 1.0, "unit_cost": 800.0})
        close = _close(env, company_id=company.id, suspense_closing=2000.0)
        move = cutover(2000.0)
        close.cutover_move_id = move

        result = close.action_reconcile_inventory_suspense()

        assert result == {
            "reconciled_entries": 2,
            "total_valuation": 2000.0,  # 2 x 600.00 + 1 x 800.00
            "voucher_ref": move.name,
            "status": "zero_cleared",
        }
        assert (e1 | e2).mapped("status") == ["reconciled", "reconciled"]
        assert set((e1 | e2).mapped("gl_cutover_ref")) == {move.name}
        assert close.suspense_closing == 0.0
        assert close.suspense_reconciled is True
        assert close.cutover_voucher_ref == move.name
        (event,) = _events(env, "inventory.suspense.reconciled", close.id)
        assert event["total_valuation_cleared"] == 2000.0
        assert event["suspense_balance"] == 0.0

    def test_suspense_is_not_reconciled_by_a_status_write(self, odoo_env):
        """Regression: entries were marked reconciled against an invented
        voucher GL-CUTOVER-W2-M15-<id> and the suspense forced to zero with
        no journal entry at all."""
        env, company, part, cutover = self._suspense_company(odoo_env)
        entry = env["fix.inventory.valuation.suspense"].create(
            {"product_id": part.id, "quantity": 2.0, "unit_cost": 600.0}
        )
        close = _close(env, company_id=company.id, suspense_closing=1200.0)
        with (
            pytest.raises(UserError, match="Post the suspense cutover journal entry"),
            env.cr.savepoint(),
        ):
            close.action_reconcile_inventory_suspense()
        close.cutover_move_id = cutover(1200.0, post=False)
        with pytest.raises(UserError, match="must be a POSTED entry"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        close.cutover_move_id = cutover(1000.0)
        with pytest.raises(UserError, match="does not clear the suspense"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert entry.status == "pending_gl_cutover"
        assert (close.suspense_closing, close.suspense_reconciled) == (1200.0, False)

    def test_suspense_cutover_nets_consumption_as_stock_out(self, odoo_env):
        """E2E2 (fix_real_e2e, 11 Nov): a receipt (+30,000 into stock) and a job
        consumption of 1,500 (stored as the VALUE CONSUMED, cd_inventory
        STOCK_EFFECT -1) move stock by +28,500. The cutover that moves the
        suspense by that net value clears it; one sized on the raw sum of the
        rows (31,500, the consumption counted as stock in) does not."""
        env, company, part, cutover = self._suspense_company(odoo_env)
        suspense = env["fix.inventory.valuation.suspense"]
        receipt = suspense.create(
            {"product_id": part.id, "quantity": 20.0, "unit_cost": 1500.0, "entry_type": "receipt"}
        )
        issue = suspense.create(
            {
                "product_id": part.id,
                "quantity": 1.0,
                "unit_cost": 1500.0,
                "entry_type": "consumption",
            }
        )
        close = _close(env, company_id=company.id)
        close.cutover_move_id = cutover(31500.0)
        with pytest.raises(UserError, match="does not clear the suspense"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert (receipt | issue).mapped("status") == ["pending_gl_cutover"] * 2
        move = cutover(28500.0)
        close.cutover_move_id = move
        result = close.action_reconcile_inventory_suspense()
        assert result["status"] == "zero_cleared" and result["total_valuation"] == 28500.0
        assert (receipt | issue).mapped("status") == ["reconciled", "reconciled"]
        assert close.suspense_closing == 0.0 and close.cutover_voucher_ref == move.name

    def test_suspense_account_must_exist_in_the_chart(self, odoo_env):
        env, company, part, cutover = self._suspense_company(odoo_env)
        entry = env["fix.inventory.valuation.suspense"].create(
            {"product_id": part.id, "quantity": 1.0, "unit_cost": 500.0}
        )
        entry.suspense_account_code = "999999"
        close = _close(env, company_id=company.id, suspense_closing=500.0)
        close.cutover_move_id = cutover(500.0)
        with pytest.raises(UserError, match="999999 are not in the chart"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert entry.status == "pending_gl_cutover"

    def test_suspense_without_pending_entries_needs_no_voucher(self, odoo_env):
        env, company, _part, _cutover = self._suspense_company(odoo_env)
        close = _close(env, company_id=company.id)
        result = close.action_reconcile_inventory_suspense()
        assert result["status"] == "zero_cleared" and result["voucher_ref"] == ""
        assert (close.suspense_closing, close.suspense_reconciled) == (0.0, True)

    # G1 (owner decision 12 Nov 2026): a return to vendor leaves stock at its
    # average cost (rtv row, -5 x 1,487.50) while the vendor credits the
    # billed 1,480.00 (Dr AP / Cr GRNI 7,400). The 37.50 difference is a
    # price_variance row: no stock movement, cleared by the cut-over from the
    # suspense account to the PPV account it names.
    @classmethod
    def _ppv_world(cls, odoo_env, variance, ppv_code="600907"):
        env, company, part, _cutover = cls._suspense_company(odoo_env)
        Account = env["account.account"].with_company(company)
        ppv = Account.create(
            {
                "code": "600907",
                "name": "Purchase Price Variance",
                "account_type": "expense_direct_cost",
                "company_ids": [(6, 0, company.ids)],
            }
        )
        suspense_acc = Account.search([("code", "=", "110999"), ("company_ids", "in", company.id)])
        inventory_acc = Account.search([("code", "=", "110100"), ("company_ids", "in", company.id)])
        journal = env["account.journal"].search(
            [("company_id", "=", company.id), ("code", "=", "CUT")], limit=1
        )
        Suspense = env["fix.inventory.valuation.suspense"]
        rows = Suspense.create(
            {
                "product_id": part.id,
                "quantity": -5.0,
                "unit_cost": 1487.5,
                "entry_type": "rtv",
                "source_ref": "RTV/G1",
            }
        ) | Suspense.create(
            {
                "product_id": part.id,
                "quantity": 5.0,
                "unit_cost": round(variance / 5.0, 4),
                "total_valuation": variance,
                "entry_type": "price_variance",
                "source_ref": "RTV/G1",
                "clearing_account_code": ppv_code,
            }
        )

        def move(*lines):
            entry = env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "date": date(2026, 9, 30),
                    "line_ids": [
                        (0, 0, {"name": "g1", "account_id": acc.id, "debit": dr, "credit": cr})
                        for acc, dr, cr in lines
                    ],
                }
            )
            entry.action_post()
            return entry

        accounts = {"ppv": ppv, "suspense": suspense_acc, "inventory": inventory_acc}
        return env, company, rows, accounts, move

    def test_g1_cutover_clears_the_price_variance_to_the_ppv_account(self, odoo_env):
        env, company, rows, acc, move = self._ppv_world(odoo_env, 37.5)
        close = _close(env, company_id=company.id)
        # the stock leg alone leaves the variance in the suspense account
        close.cutover_move_id = move(
            (acc["suspense"], 7437.5, 0.0), (acc["inventory"], 0.0, 7437.5)
        )
        with pytest.raises(UserError, match="600907"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert rows.mapped("status") == ["pending_gl_cutover"] * 2
        # Dr suspense 7,437.50 / Cr Inventory 7,437.50; Dr PPV 37.50 / Cr suspense 37.50
        entry = move(
            (acc["suspense"], 7437.5, 0.0),
            (acc["inventory"], 0.0, 7437.5),
            (acc["ppv"], 37.5, 0.0),
            (acc["suspense"], 0.0, 37.5),
        )
        close.cutover_move_id = entry
        result = close.action_reconcile_inventory_suspense()
        assert result["status"] == "zero_cleared" and result["total_valuation"] == 7437.5
        assert rows.mapped("status") == ["reconciled", "reconciled"]
        assert set(rows.mapped("gl_cutover_ref")) == {entry.name}
        (event,) = _events(env, "inventory.suspense.reconciled", close.id)
        assert event["price_variance_cleared"] == 37.5

    def test_g1_cutover_refuses_the_variance_booked_the_wrong_way(self, odoo_env):
        env, company, rows, acc, move = self._ppv_world(odoo_env, 37.5)
        close = _close(env, company_id=company.id)
        close.cutover_move_id = move(
            (acc["suspense"], 7475.0, 0.0),
            (acc["inventory"], 0.0, 7437.5),
            (acc["ppv"], 0.0, 37.5),
        )
        with pytest.raises(UserError, match="does not clear"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert rows.mapped("status") == ["pending_gl_cutover"] * 2

    def test_g1_a_favourable_variance_is_credited_to_ppv(self, odoo_env):
        """The vendor credited more than the stock's average cost: a gain."""
        env, company, rows, acc, move = self._ppv_world(odoo_env, -20.0)
        close = _close(env, company_id=company.id)
        close.cutover_move_id = move(
            (acc["suspense"], 7457.5, 0.0),
            (acc["inventory"], 0.0, 7437.5),
            (acc["ppv"], 0.0, 20.0),
        )
        result = close.action_reconcile_inventory_suspense()
        assert result["status"] == "zero_cleared"
        assert rows.mapped("status") == ["reconciled", "reconciled"]

    def test_g1_the_ppv_account_must_exist_in_the_chart(self, odoo_env):
        env, company, rows, acc, move = self._ppv_world(odoo_env, 37.5, ppv_code="600999")
        close = _close(env, company_id=company.id)
        close.cutover_move_id = move(
            (acc["suspense"], 7437.5, 0.0),
            (acc["inventory"], 0.0, 7437.5),
            (acc["ppv"], 37.5, 0.0),
            (acc["suspense"], 0.0, 37.5),
        )
        with pytest.raises(UserError, match="600999"), env.cr.savepoint():
            close.action_reconcile_inventory_suspense()
        assert rows.mapped("status") == ["pending_gl_cutover"] * 2

    def test_close_line_state_machine(self, odoo_env):
        close = _close(odoo_env)
        line = odoo_env["fix.period.close.line"].create({"close_id": close.id, "name": "Bank rec"})
        assert line.action_set_state("in_progress") is True
        assert line.state == "in_progress"
        with pytest.raises(UserError, match="Invalid state: approved"), odoo_env.cr.savepoint():
            line.action_set_state("approved")
        # Regression: without evidence the step was marked done as "VERIFIED"
        with (
            pytest.raises(UserError, match="Provide the evidence reference"),
            odoo_env.cr.savepoint(),
        ):
            line.action_mark_done()
        # A08 M19-5: "done" is reached only through Mark Done, with evidence
        with (
            pytest.raises(UserError, match="completed with its evidence"),
            odoo_env.cr.savepoint(),
        ):
            line.action_set_state("done")
        assert (line.state, line.evidence_ref) == ("in_progress", False)
        assert line.action_mark_done("BANKREC-2026-09-14") is True
        assert (line.state, line.evidence_ref) == ("done", "BANKREC-2026-09-14")


# --------------------------------------------------------------------------- dimensions / seam


def _misc_move_vals(env, amount=750.0):
    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1
    )
    accounts = env["account.account"].search([("account_type", "=", "income")], limit=1)
    expense = env["account.account"].search([("account_type", "=", "expense")], limit=1)
    return {
        "journal_id": journal.id,
        "date": date(2026, 10, 15),
        "ref": "DIM-TEST",
        "line_ids": [
            (0, 0, {"name": "Dr", "account_id": expense.id, "debit": amount, "credit": 0.0}),
            (0, 0, {"name": "Cr", "account_id": accounts.id, "debit": 0.0, "credit": amount}),
        ],
    }


def _fresh_company(env, label):
    """A private company per test: the shared fix_test database is used by
    concurrent suites, so these tests never write the main company's row or
    take its one-per-company keys (fix.entity, OU codes)."""
    return env["res.company"].create({"name": f"GL ORM {label} Test Co"})


def _branch(env, ou, code="DHK01"):
    company = _fresh_company(env, f"branch {code}")
    entity = env["fix.entity"].create(
        {"code": f"EN-{code}", "legal_name": "1000FiX Test Entity", "company_id": company.id}
    )
    return env["fix.branch"].create(
        {"code": code, "name": "Dhaka", "entity_id": entity.id, "operating_unit_id": ou.id}
    )


def _bare_company_move_vals(env, company, amount=100.0):
    """A chart-less company with just a journal and two accounts."""
    journal = env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    accounts = env["account.account"].with_company(company)
    expense = accounts.create(
        {
            "name": "Expense",
            "code": "500001",
            "account_type": "expense",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    income = accounts.create(
        {
            "name": "Income",
            "code": "400001",
            "account_type": "income",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    return {
        "journal_id": journal.id,
        "company_id": company.id,
        "date": date(2026, 10, 15),
        "line_ids": [
            (0, 0, {"name": "Dr", "account_id": expense.id, "debit": amount, "credit": 0.0}),
            (0, 0, {"name": "Cr", "account_id": income.id, "debit": 0.0, "credit": amount}),
        ],
    }


@pytest.mark.unlinked_chart  # the API's own mechanics, with a sparse dimension map
class TestPostWithDimensions:
    def test_posts_move_and_attaches_dimensions(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
        branch = _branch(odoo_env, ou)
        move, dims = post_with_dimensions(
            odoo_env,
            _misc_move_vals(odoo_env, 750.0),
            {0: {"branch_id": branch.id, "cost_centre": "CC-01"}},
        )
        assert move.state == "posted"
        assert len(dims) == 1  # line 1 carries no dimension request
        assert dims.move_line_id == move.line_ids[0]
        assert dims.operating_unit_id == ou  # company OU fallback
        assert (dims.branch_id, dims.cost_centre) == (branch, "CC-01")
        (event,) = _events(odoo_env, "journal.posted", move.id)
        assert _money(event["amount"]) == D("750.00")
        assert event["line_count"] == 2

    def test_branch_outside_operating_unit_is_refused(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        ou = odoo_env["operating.unit"].search([("company_id", "=", odoo_env.company.id)], limit=1)
        other_company = _fresh_company(odoo_env, "Chattogram")
        other_ou = odoo_env["operating.unit"].create(
            {
                "name": "Chattogram OU",
                "code": "CTG",
                "company_id": other_company.id,
                "partner_id": other_company.partner_id.id,
            }
        )
        branch = _branch(odoo_env, ou)
        with (
            pytest.raises(ValidationError, match="does not belong to operating unit"),
            odoo_env.cr.savepoint(),
        ):
            post_with_dimensions(
                odoo_env,
                _misc_move_vals(odoo_env),
                {0: {"branch_id": branch.id, "operating_unit_id": other_ou.id}},
            )

    def test_company_without_operating_unit_is_refused(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "no OU")
        env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
        with (
            pytest.raises(UserError, match="GL ORM no OU Test Co has no operating unit"),
            odoo_env.cr.savepoint(),
        ):
            post_with_dimensions(
                env, _bare_company_move_vals(env, company), {0: {"cost_centre": "X"}}
            )

    def test_fixed_asset_seam_consumed(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        move, _dims = post_with_dimensions(odoo_env, _misc_move_vals(odoo_env), {})
        ou = odoo_env["operating.unit"].search([], limit=1)
        seam = odoo_env["fix.fixed.asset.seam"].create(
            {
                "name": "CAP-0001",
                "operating_unit_id": ou.id,
                "move_line_id": move.line_ids[0].id,
                "amount": 750.0,
            }
        )
        assert seam.consumed is False
        seam.action_mark_consumed()
        assert seam.consumed is True


# --------------------------------------------------------------------------- fiscal-year bridge


class TestFiscalYearBridge:
    @pytest.fixture
    def company(self, odoo_env):
        return _fresh_company(odoo_env, "lock")

    def _bridge(self, env, company, period_end, state="closed"):
        close = _close(env, period_end=period_end, company_id=company.id)
        close.state = state
        return env["fix.fiscal.period.bridge"].create(
            {"company_id": company.id, "period_close_id": close.id}
        )

    def test_lock_refused_before_close(self, odoo_env, company):
        bridge = self._bridge(odoo_env, company, date(2026, 9, 30), state="ready_to_close")
        with (
            pytest.raises(UserError, match="before period close is completed"),
            odoo_env.cr.savepoint(),
        ):
            bridge.action_lock_journals()
        assert bridge.is_locked is False

    def test_lock_sets_company_global_lock_date(self, odoo_env, company):
        """Regression: the lock wrote journal fields that do not exist in
        Odoo 19 (hasattr() was always False), so a closed period stayed
        open for posting. The company Global Lock Date is now set."""
        assert company.fiscalyear_lock_date is False
        bridge = self._bridge(odoo_env, company, date(2026, 9, 30))
        result = bridge.action_lock_journals()
        assert result == {"status": "locked", "date": "2026-09-30", "lock_date": "2026-09-30"}
        assert company.fiscalyear_lock_date == date(2026, 9, 30)
        assert bridge.is_locked is True
        assert isinstance(bridge.locked_at, datetime)

    def test_lock_never_moves_backwards(self, odoo_env, company):
        company.fiscalyear_lock_date = date(2026, 9, 30)
        bridge = self._bridge(odoo_env, company, date(2026, 8, 31))
        result = bridge.action_lock_journals()
        assert result["lock_date"] == "2026-09-30"
        assert company.fiscalyear_lock_date == date(2026, 9, 30)

    def test_lock_advances_an_older_lock(self, odoo_env, company):
        company.fiscalyear_lock_date = date(2026, 8, 31)
        bridge = self._bridge(odoo_env, company, date(2026, 9, 30))
        bridge.action_lock_journals()
        assert company.fiscalyear_lock_date == date(2026, 9, 30)

    @staticmethod
    def _ledger(odoo_env):
        """A private company with a fiscal year and real posted entries:
        prior year sale 300 (cash/income), this year sale 1,000 and
        expense 400 (cash), plus an unposted draft that must be ignored."""
        company = _fresh_company(odoo_env, "report")
        env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=company.ids))
        accounts = env["account.account"].with_company(company)

        def acc(code, account_type):
            return accounts.create(
                {
                    "code": code,
                    "name": code,
                    "account_type": account_type,
                    "company_ids": [(6, 0, company.ids)],
                }
            )

        cash, income, expense = (
            acc("100100", "asset_cash"),
            acc("400100", "income"),
            acc("500100", "expense"),
        )
        journal = env["account.journal"].create(
            {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
        )

        def move(day, dr, cr, amount, post=True):
            m = env["account.move"].create(
                {
                    "journal_id": journal.id,
                    "date": day,
                    "line_ids": [
                        (0, 0, {"name": "dr", "account_id": dr.id, "debit": amount}),
                        (0, 0, {"name": "cr", "account_id": cr.id, "credit": amount}),
                    ],
                }
            )
            if post:
                m.action_post()

        move(date(2025, 6, 1), cash, income, 300.0)
        move(date(2026, 2, 10), cash, income, 1000.0)
        move(date(2026, 3, 5), expense, cash, 400.0)
        move(date(2026, 3, 6), expense, cash, 999.0, post=False)
        fy = env["account.fiscal.year"].create(
            {
                "name": "FY2026",
                "date_from": date(2026, 1, 1),
                "date_to": date(2026, 12, 31),
                "company_id": company.id,
            }
        )
        return env, company, fy

    def _report(self, env, company, fy, report_type):
        report = env["fix.financial.report.bridge"].create(
            {
                "name": "Stmt",
                "report_type": report_type,
                "company_id": company.id,
                "fiscal_year_id": fy.id,
            }
        )
        result = report.action_generate_report()
        assert report.generated_at
        return result, json.loads(report.report_data)

    def test_trial_balance_is_computed_from_the_posted_ledger(self, odoo_env):
        """Regression: the generator wrote the constant {"status": "computed"}
        without reading a single journal item."""
        env, company, fy = self._ledger(odoo_env)
        result, data = self._report(env, company, fy, "trial_balance")
        # Three accounts moved in the year. The fourth line is the 2025 sale brought
        # forward: 300 on the bank, and its profit as the earlier years' result (this
        # chart has no undistributed-earnings account). It used to be dropped.
        assert result == {"status": "generated", "type": "trial_balance", "line_count": 4}
        by_code = {r["account_code"]: r for r in data["lines"]}
        assert (by_code["100100"]["debit"], by_code["100100"]["credit"]) == (1000.0, 400.0)
        assert (by_code["100100"]["opening_balance"], by_code["100100"]["balance"]) == (
            300.0,
            900.0,
        )
        assert (by_code[""]["opening_balance"], by_code[""]["balance"]) == (-300.0, -300.0)
        assert by_code["400100"]["balance"] == -1000.0  # FY only: prior-year 300 excluded
        assert by_code["500100"]["balance"] == 400.0  # the 999 draft is not posted
        assert (data["total_debit"], data["total_credit"], data["balanced"]) == (
            1400.0,
            1400.0,
            True,
        )
        assert (data["date_from"], data["date_to"]) == ("2026-01-01", "2026-12-31")

    def test_pnl_and_balance_sheet(self, odoo_env):
        env, company, fy = self._ledger(odoo_env)
        _result, pnl = self._report(env, company, fy, "pnl")
        assert sorted(r["account_code"] for r in pnl["lines"]) == ["400100", "500100"]
        assert pnl["net_profit"] == 600.0  # 1,000 - 400
        _result, bs = self._report(env, company, fy, "balance_sheet")
        assert [r["account_code"] for r in bs["lines"]] == ["100100"]
        assert bs["lines"][0]["balance"] == 900.0  # cumulative: 300 + 1,000 - 400
        assert bs["unclosed_profit_and_loss"] == 900.0
        assert bs["balanced"] is True

    def test_report_over_an_explicit_period_records_its_headline(self, odoo_env):
        env, company, _fy = self._ledger(odoo_env)
        report = env["fix.financial.report.bridge"].create(
            {
                "name": "PL Q1",
                "report_type": "pnl",
                "company_id": company.id,
                "date_from": date(2026, 1, 1),
                "date_to": date(2026, 3, 31),
            }
        )
        result = report.action_generate_report()
        assert result["line_count"] == 2
        assert report.headline_amount == 600.0
        assert report.line_count == 2 and report.generated_by_id == env.user
        bs = env["fix.financial.report.bridge"].create(
            {
                "name": "BS",
                "report_type": "balance_sheet",
                "company_id": company.id,
                "date_to": date(2026, 12, 31),
            }
        )
        bs.action_generate_report()
        assert bs.headline_amount == 900.0 and bs.is_balanced
        backwards = env["fix.financial.report.bridge"].create(
            {
                "name": "Bad",
                "report_type": "pnl",
                "company_id": company.id,
                "date_from": date(2026, 3, 1),
                "date_to": date(2026, 1, 1),
            }
        )
        with pytest.raises(UserError, match="must not be after"), env.cr.savepoint():
            backwards.action_generate_report()

    def test_report_refuses_another_companys_fiscal_year(self, odoo_env):
        env, _company, fy = self._ledger(odoo_env)
        other = env["res.company"].create({"name": "GL Other FY Co"})
        report = env["fix.financial.report.bridge"].create(
            {
                "name": "TB",
                "report_type": "trial_balance",
                "company_id": other.id,
                "fiscal_year_id": fy.id,
            }
        )
        with pytest.raises(UserError, match="belongs to"), env.cr.savepoint():
            report.action_generate_report()
        assert not report.generated_at

    def test_report_refuses_without_fiscal_year_or_engine(self, odoo_env):
        Bridge = odoo_env["fix.financial.report.bridge"]
        report = Bridge.create({"name": "Statutory BS", "report_type": "balance_sheet"})
        with pytest.raises(UserError, match="Select the fiscal year"), odoo_env.cr.savepoint():
            report.action_generate_report()
        cash_flow = Bridge.create({"name": "CF", "report_type": "cash_flow"})
        with (
            pytest.raises(UserError, match="not computed by this bridge"),
            odoo_env.cr.savepoint(),
        ):
            cash_flow.action_generate_report()
        assert not report.report_data and not cash_flow.generated_at
