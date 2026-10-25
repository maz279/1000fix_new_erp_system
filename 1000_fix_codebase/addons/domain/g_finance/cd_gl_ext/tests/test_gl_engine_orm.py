# cd_gl_ext — live-ORM behaviour of the M19 GL engine additions (DoD-03):
# posting-rule enforcement, chart linking, recurring/reversing templates,
# allocation rules, the immutable posting log, the SoD review flow and the
# statement computations (TB / P&L / cash flow / consolidation).
#
# Runs against the rolled-back `fix_test` database (addons/conftest.py
# `odoo_env`). Every money expectation is written out by hand as a Decimal.
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from odoo.exceptions import UserError, ValidationError

pytestmark = [pytest.mark.financial]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _fresh_company(env, label):
    return env["res.company"].create({"name": f"GL Engine {label} Test Co"})


def _company_accounts(env, company):
    """A chart-less company with an operating unit (AS-03), a journal and one
    account of each kind."""
    env["operating.unit"].create(
        {
            "name": f"OU {company.name}",
            "code": f"OU-{company.id}",
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    journal = env["account.journal"].create(
        {"name": "Misc", "code": "MSC", "type": "general", "company_id": company.id}
    )
    Account = env["account.account"].with_company(company)
    expense = Account.create(
        {
            "name": "Expense",
            "code": "500001",
            "account_type": "expense",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    income = Account.create(
        {
            "name": "Income",
            "code": "400001",
            "account_type": "income",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    cash = Account.create(
        {
            "name": "Bank",
            "code": "101401",
            "account_type": "asset_cash",
            "company_ids": [(6, 0, company.ids)],
        }
    )
    return {"journal": journal, "expense": expense, "income": income, "cash": cash}


def _statutory(env, company, odoo_account, **overrides):
    """A statutory chart account LINKED to an Odoo account — what turns the
    MD-035 posting rules on for that account."""
    vals = {
        "company_id": company.id,
        "account_code": "1-10-20-010",
        "name": "Operating bank account - BDT",
        "account_type": "asset",
        "account_subtype": "bank",
        "is_postable": True,
        "statutory_group": "Cash & Bank",
        "odoo_account_id": odoo_account.id,
    }
    vals.update(overrides)
    return env["fix.chart.account"].create(vals)


def _move_vals(journal, lines):
    return {
        "journal_id": journal.id,
        "company_id": journal.company_id.id,
        "date": date(2026, 10, 15),
        "line_ids": [(0, 0, {"name": "L%d" % i, **line}) for i, line in enumerate(lines)],
    }


# --------------------------------------------------------------------------- chart linking


class TestChartLinking:
    def test_action_link_odoo_accounts_links_mapped_pairs(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_chart_loader import ODOO_CHART_MAPPING

        company = _fresh_company(odoo_env, "link")
        Account = odoo_env["account.account"].with_company(company)
        odoo_bank = Account.create(
            {
                "name": "Bank",
                "code": "101401",
                "account_type": "asset_cash",
                "company_ids": [(6, 0, company.ids)],
            }
        )
        statutory = odoo_env["fix.chart.account"].create(
            {
                "company_id": company.id,
                "account_code": ODOO_CHART_MAPPING["101401"],
                "name": "Operating bank account - BDT",
                "account_type": "asset",
                "account_subtype": "bank",
                "is_postable": True,
                "statutory_group": "Cash & Bank",
            }
        )
        assert statutory.odoo_account_id.id is False
        loader = odoo_env["fix.chart.loader"].create({"company_id": company.id})
        result = loader.action_link_odoo_accounts()
        assert statutory.odoo_account_id.id == odoo_bank.id
        assert result["linked"] >= 1

    def test_link_reports_unmatched_pairs(self, odoo_env):
        company = _fresh_company(odoo_env, "link-miss")
        loader = odoo_env["fix.chart.loader"].create({"company_id": company.id})
        result = loader.action_link_odoo_accounts()
        assert result["status"] == "linked"
        # nothing exists for this company: every pair is reported unmatched
        assert len(result["unmatched"]) >= 1


# --------------------------------------------------------------------------- posting rules


class TestPostingRuleEnforcement:
    def test_unmapped_account_posts_without_statutory_check(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "unmapped")
        accs = _company_accounts(odoo_env, company)
        move, _dims = post_with_dimensions(
            odoo_env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": 100.0, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": 100.0},
                ],
            ),
            {},
            source="manual",
        )
        assert move.state == "posted"

    def test_control_account_refuses_direct_manual_post_coa02(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "control")
        accs = _company_accounts(odoo_env, company)
        _statutory(
            odoo_env,
            company,
            accs["income"],
            account_code="1-20-10-010",
            name="Trade receivables - retail repair",
            account_type="asset",
            account_subtype="receivable",
            is_control_account=True,
            control_subledger="receivable",
            statutory_group="Receivables",
        )
        with pytest.raises(UserError, match="COA-02"), odoo_env.cr.savepoint():
            post_with_dimensions(
                odoo_env,
                _move_vals(
                    accs["journal"],
                    [
                        {"account_id": accs["expense"].id, "debit": 50.0, "credit": 0.0},
                        {"account_id": accs["income"].id, "debit": 0.0, "credit": 50.0},
                    ],
                ),
                {},
                source="manual",
            )

    def test_engine_source_posts_on_control_account(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "control-engine")
        accs = _company_accounts(odoo_env, company)
        _statutory(
            odoo_env,
            company,
            accs["income"],
            account_code="1-20-10-010",
            name="Trade receivables - retail repair",
            account_type="asset",
            account_subtype="receivable",
            is_control_account=True,
            control_subledger="receivable",
            statutory_group="Receivables",
        )
        move, _dims = post_with_dimensions(
            odoo_env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": 50.0, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": 50.0},
                ],
            ),
            {},
            source="settlement",
        )
        assert move.state == "posted"

    def test_required_dimension_missing_refuses_coa03(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "dims")
        accs = _company_accounts(odoo_env, company)
        _statutory(odoo_env, company, accs["cash"], requires_dimension="branch;cost_centre")
        with pytest.raises(UserError, match="COA-03"), odoo_env.cr.savepoint():
            post_with_dimensions(
                odoo_env,
                _move_vals(
                    accs["journal"],
                    [
                        {"account_id": accs["cash"].id, "debit": 10.0, "credit": 0.0},
                        {"account_id": accs["income"].id, "debit": 0.0, "credit": 10.0},
                    ],
                ),
                {0: {"cost_centre": "CC-01"}},  # branch missing
                source="manual",
            )

    def test_required_dimension_present_posts(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "dims-ok")
        accs = _company_accounts(odoo_env, company)
        _statutory(odoo_env, company, accs["cash"], requires_dimension="cost_centre")
        move, dims = post_with_dimensions(
            odoo_env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["cash"].id, "debit": 10.0, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": 10.0},
                ],
            ),
            {0: {"cost_centre": "CC-01", "business_line": "ICT"}},
            source="manual",
        )
        assert move.state == "posted"
        assert dims.cost_centre == "CC-01"
        assert dims.business_line == "ICT"

    def test_non_postable_statutory_account_refuses_coa01(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "nonpostable")
        accs = _company_accounts(odoo_env, company)
        _statutory(odoo_env, company, accs["cash"], is_postable=False)
        with pytest.raises(UserError, match="ERR-COA-001"), odoo_env.cr.savepoint():
            post_with_dimensions(
                odoo_env,
                _move_vals(
                    accs["journal"],
                    [
                        {"account_id": accs["cash"].id, "debit": 10.0, "credit": 0.0},
                        {"account_id": accs["income"].id, "debit": 0.0, "credit": 10.0},
                    ],
                ),
                {},
                source="manual",
            )

    def test_archived_statutory_account_refuses(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "archived")
        accs = _company_accounts(odoo_env, company)
        _statutory(odoo_env, company, accs["cash"], active=False)
        with pytest.raises(UserError, match="archived"), odoo_env.cr.savepoint():
            post_with_dimensions(
                odoo_env,
                _move_vals(
                    accs["journal"],
                    [
                        {"account_id": accs["cash"].id, "debit": 10.0, "credit": 0.0},
                        {"account_id": accs["income"].id, "debit": 0.0, "credit": 10.0},
                    ],
                ),
                {},
                source="manual",
            )


# --------------------------------------------------------------------------- posting log + SoD


class TestPostingLogAndReview:
    def _users(self, env):
        # Both users may see every company: the entry belongs to a fresh
        # per-test company, and multi-company record rules on account.account
        # would otherwise deny the read before any SoD check runs.
        all_companies = [(6, 0, env["res.company"].search([]).ids)]
        maker = env["res.users"].create(
            {
                "name": "GL Maker",
                "login": "gl-maker@test.local",
                "email": "gl-maker@test.local",
                "company_ids": all_companies,
                "group_ids": [(6, 0, [env.ref("account.group_account_user").id])],
            }
        )
        checker = env["res.users"].create(
            {
                "name": "GL Checker",
                "login": "gl-checker@test.local",
                "email": "gl-checker@test.local",
                "company_ids": all_companies,
                "group_ids": [(6, 0, [env.ref("account.group_account_manager").id])],
            }
        )
        return maker, checker

    def test_post_creates_immutable_log(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "log")
        accs = _company_accounts(odoo_env, company)
        move, _dims = post_with_dimensions(
            odoo_env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": 25.0, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": 25.0},
                ],
            ),
            {},
            source="manual",
        )
        log = odoo_env["fix.journal.posting.log"].search([("move_id", "=", move.id)])
        assert len(log) == 1
        assert log.source == "manual" and log.state == "posted"
        assert _money(log.amount) == D("25.00")
        with pytest.raises(UserError, match="immutable"), odoo_env.cr.savepoint():
            log.write({"note": "tamper"})
        with pytest.raises(UserError, match="immutable"), odoo_env.cr.savepoint():
            log.unlink()

    def test_draft_then_approve_flow_with_sod(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import (
            approve_journal_entry,
            create_journal_entry_draft,
        )

        company = _fresh_company(odoo_env, "sod")
        accs = _company_accounts(odoo_env, company)
        # users AFTER the company: their allowed companies must include it
        maker, checker = self._users(odoo_env)
        move_vals = _move_vals(
            accs["journal"],
            [
                {"account_id": accs["expense"].id, "debit": 80.0, "credit": 0.0},
                {"account_id": accs["income"].id, "debit": 0.0, "credit": 80.0},
            ],
        )
        move, log = create_journal_entry_draft(odoo_env(user=maker.id), move_vals, {})
        assert move.state == "draft"
        assert log.state == "requested"
        assert log.requested_by == maker

        # SoD: the maker cannot approve their own entry
        with pytest.raises(UserError, match="Segregation of duties"), odoo_env.cr.savepoint():
            approve_journal_entry(odoo_env(user=maker.id), move, {})

        posted, dims = approve_journal_entry(odoo_env(user=checker.id), move, {})
        assert posted.state == "posted"
        assert log.state == "posted"
        assert log.posted_by == checker
        assert dims is not None

    def test_approve_requires_manager_group(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import (
            approve_journal_entry,
            create_journal_entry_draft,
        )

        company = _fresh_company(odoo_env, "sod-group")
        accs = _company_accounts(odoo_env, company)
        maker, _checker = self._users(odoo_env)
        stranger = odoo_env["res.users"].create(
            {
                "name": "GL Stranger",
                "login": "gl-stranger@test.local",
                "email": "gl-stranger@test.local",
                "company_ids": [(6, 0, odoo_env["res.company"].search([]).ids)],
                "group_ids": [(6, 0, [odoo_env.ref("account.group_account_user").id])],
            }
        )
        move, _log = create_journal_entry_draft(
            odoo_env(user=maker.id),
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": 40.0, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": 40.0},
                ],
            ),
            {},
        )
        with pytest.raises(UserError, match="accounting manager"), odoo_env.cr.savepoint():
            approve_journal_entry(odoo_env(user=stranger.id), move, {})


# --------------------------------------------------------------------------- templates


class TestJournalTemplates:
    def _template(self, env, company, accs, **overrides):
        vals = {
            "name": "Branch utilities accrual",
            "company_id": company.id,
            "journal_id": accs["journal"].id,
            "schedule": "monthly",
            "next_run_date": date(2026, 10, 1),
            "state": "active",
            "memo": "ACCRUAL-UTIL",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": accs["expense"].id,
                        "debit": 300.0,
                        "credit": 0.0,
                        "cost_centre": "CC-UTIL",
                    },
                ),
                (0, 0, {"account_id": accs["income"].id, "debit": 0.0, "credit": 300.0}),
            ],
        }
        vals.update(overrides)
        return env["fix.journal.template"].create(vals)

    def test_generate_entry_posts_and_advances(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl")
        accs = _company_accounts(odoo_env, company)
        template = self._template(odoo_env, company, accs)
        template.action_generate_entry()
        assert template.last_move_id.state == "posted"
        assert template.last_move_id.ref == "ACCRUAL-UTIL"
        assert template.run_count == 1
        assert template.next_run_date == date(2026, 11, 1)
        log = odoo_env["fix.journal.posting.log"].search(
            [("move_id", "=", template.last_move_id.id)]
        )
        assert log.source == "template" and log.template_id == template
        dim = odoo_env["fix.journal.dimension"].search(
            [("move_line_id", "in", template.last_move_id.line_ids.ids)]
        )
        assert dim.cost_centre == "CC-UTIL"

    def test_auto_reverse_generates_mirror_next_period(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl-rev")
        accs = _company_accounts(odoo_env, company)
        template = self._template(odoo_env, company, accs, auto_reverse=True)
        template.action_generate_entry()
        assert template.run_count == 2
        moves = odoo_env["account.move"].search(
            [("ref", "like", "ACCRUAL-UTIL"), ("company_id", "=", company.id)]
        )
        reversal = moves.filtered(lambda m: m.ref.startswith("REVERSAL"))
        assert len(reversal) == 1
        assert reversal.date == date(2026, 11, 1)
        original_line = template.last_move_id.line_ids[0]
        reversal_line = reversal.line_ids[0]
        assert _money(original_line.debit) == _money(reversal_line.credit)

    def test_not_due_refused(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl-future")
        accs = _company_accounts(odoo_env, company)
        template = self._template(odoo_env, company, accs, next_run_date=date(2099, 1, 1))
        with pytest.raises(UserError, match="not due"), odoo_env.cr.savepoint():
            template.action_generate_entry()

    def test_unbalanced_template_refused(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl-bal")
        accs = _company_accounts(odoo_env, company)
        with pytest.raises(ValidationError, match="not balanced"), odoo_env.cr.savepoint():
            self._template(
                odoo_env,
                company,
                accs,
                line_ids=[
                    (0, 0, {"account_id": accs["expense"].id, "debit": 100.0, "credit": 0.0}),
                    (0, 0, {"account_id": accs["income"].id, "debit": 0.0, "credit": 90.0}),
                ],
            )

    def test_cron_generates_only_due_templates(self, odoo_env):
        company = _fresh_company(odoo_env, "cron")
        accs = _company_accounts(odoo_env, company)
        due = self._template(odoo_env, company, accs)
        not_due = self._template(
            odoo_env,
            company,
            accs,
            name="Future accrual",
            next_run_date=date(2099, 1, 1),
        )
        generated = odoo_env["fix.journal.template"]._cron_generate_due_entries()
        assert generated == 1
        assert due.run_count == 1
        assert not_due.run_count == 0

    def _users(self, env, company):
        def user(login, group):
            return env["res.users"].create(
                {
                    "name": login,
                    "login": "%s-%s@test.local" % (login, company.id),
                    "company_id": company.id,
                    "company_ids": [(6, 0, company.ids)],
                    "group_ids": [(6, 0, [env.ref(group).id])],
                }
            )

        return (
            user("tmpl-maker", "account.group_account_manager"),
            user("tmpl-checker", "account.group_account_manager"),
            user("tmpl-clerk", "account.group_account_user"),
        )

    def test_activation_is_a_manager_approval_with_sod(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl-sod")
        accs = _company_accounts(odoo_env, company)
        maker, checker, clerk = self._users(odoo_env, company)
        template = self._template(odoo_env(user=maker.id), company, accs, state="draft").with_user(
            maker
        )
        with pytest.raises(UserError, match="not active"), odoo_env.cr.savepoint():
            template.action_generate_entry()
        with pytest.raises(UserError, match="Only an accounting manager"), odoo_env.cr.savepoint():
            template.with_user(clerk).action_activate()
        with pytest.raises(UserError, match="Segregation of duties"), odoo_env.cr.savepoint():
            template.action_activate()
        assert template.state == "draft"
        assert template.with_user(checker).action_activate() is True
        assert template.state == "active" and template.activated_by_id == checker

    def test_pause_stops_generation(self, odoo_env):
        company = _fresh_company(odoo_env, "tmpl-pause")
        accs = _company_accounts(odoo_env, company)
        template = self._template(odoo_env, company, accs)
        assert template.action_pause() is True
        assert template.state == "paused"
        with pytest.raises(UserError, match="Only an active template"), odoo_env.cr.savepoint():
            template.action_pause()
        assert odoo_env["fix.journal.template"]._cron_generate_due_entries() >= 0
        assert template.run_count == 0
        template.action_activate()  # superuser: the approval step itself
        assert template.state == "active"


# --------------------------------------------------------------------------- allocations


class TestAllocationRules:
    def _rule(self, env, company, accs, source, lines):
        return env["fix.allocation.rule"].create(
            {
                "name": "Rent allocation",
                "company_id": company.id,
                "journal_id": accs["journal"].id,
                "source_account_id": source.id,
                "state": "active",
                "line_ids": lines,
            }
        )

    def test_run_posts_clearing_and_targets(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(odoo_env, "alloc")
        accs = _company_accounts(odoo_env, company)
        target = (
            odoo_env["account.account"]
            .with_company(company)
            .create(
                {
                    "name": "Rent - Branch B",
                    "code": "612002",
                    "account_type": "expense",
                    "company_ids": [(6, 0, company.ids)],
                }
            )
        )
        # 1000 of posted rent movement to allocate
        post_with_dimensions(
            odoo_env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": 1000.0, "credit": 0.0},
                    {"account_id": accs["cash"].id, "debit": 0.0, "credit": 1000.0},
                ],
            ),
            {},
            source="api",
        )
        rule = self._rule(
            odoo_env,
            company,
            accs,
            accs["expense"],
            [
                (0, 0, {"account_id": accs["expense"].id, "percent": 60.0, "cost_centre": "CC-A"}),
                (0, 0, {"account_id": target.id, "percent": 40.0, "cost_centre": "CC-B"}),
            ],
        )
        rule.action_run(date(2026, 10, 1), date(2026, 10, 31))
        assert rule.run_count == 1
        move = rule.last_run_id
        assert move.state == "posted"
        source_line = move.line_ids.filtered(
            lambda ln: ln.account_id == accs["expense"] and "clearing" in ln.name
        )
        target_b = move.line_ids.filtered(lambda ln: ln.account_id == target)
        assert _money(source_line.credit) == D("1000.00")
        assert _money(target_b.debit) == D("400.00")
        dims = odoo_env["fix.journal.dimension"].search([("move_line_id", "in", move.line_ids.ids)])
        assert set(dims.mapped("cost_centre")) == {"CC-A", "CC-B"}

    def test_percent_must_total_100(self, odoo_env):
        company = _fresh_company(odoo_env, "alloc-pct")
        accs = _company_accounts(odoo_env, company)
        with pytest.raises(ValidationError, match="100"), odoo_env.cr.savepoint():
            self._rule(
                odoo_env,
                company,
                accs,
                accs["expense"],
                [
                    (0, 0, {"account_id": accs["expense"].id, "percent": 60.0}),
                    (0, 0, {"account_id": accs["income"].id, "percent": 50.0}),
                ],
            )

    def test_no_movement_refused(self, odoo_env):
        company = _fresh_company(odoo_env, "alloc-empty")
        accs = _company_accounts(odoo_env, company)
        rule = self._rule(
            odoo_env,
            company,
            accs,
            accs["expense"],
            [(0, 0, {"account_id": accs["expense"].id, "percent": 100.0})],
        )
        with pytest.raises(UserError, match="no posted movement"), odoo_env.cr.savepoint():
            rule.action_run(date(2026, 10, 1), date(2026, 10, 31))


# --------------------------------------------------------------------------- statements


class TestStatementComputations:
    def _posted_company(self, env, label, income=500.0, expense=300.0):
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        company = _fresh_company(env, label)
        accs = _company_accounts(env, company)
        post_with_dimensions(
            env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["cash"].id, "debit": income, "credit": 0.0},
                    {"account_id": accs["income"].id, "debit": 0.0, "credit": income},
                ],
            ),
            {},
            source="api",
        )
        post_with_dimensions(
            env,
            _move_vals(
                accs["journal"],
                [
                    {"account_id": accs["expense"].id, "debit": expense, "credit": 0.0},
                    {"account_id": accs["cash"].id, "debit": 0.0, "credit": expense},
                ],
            ),
            {},
            source="api",
        )
        return company, accs

    def test_trial_balance_balanced(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_trial_balance

        company, _accs = self._posted_company(odoo_env, "tb")
        tb = compute_trial_balance(odoo_env, company, date(2026, 1, 1), date(2026, 12, 31))
        assert tb["balanced"] is True
        assert _money(tb["total_debit"]) == _money(tb["total_credit"])

    def test_pnl_net_profit(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_pnl

        company, _accs = self._posted_company(odoo_env, "pnl", income=500.0, expense=300.0)
        pnl = compute_pnl(odoo_env, company, date(2026, 1, 1), date(2026, 12, 31))
        assert _money(pnl["net_profit"]) == D("200.00")

    def test_cash_flow_categories_and_closing(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_cash_flow

        company, _accs = self._posted_company(odoo_env, "cf", income=500.0, expense=300.0)
        cf = compute_cash_flow(odoo_env, company, date(2026, 1, 1), date(2026, 12, 31))
        assert cf["basis"].startswith("posted cash/bank")
        # 500 in from the income entry, 300 out to the expense entry
        assert _money(cf["net_movement"]) == D("200.00")
        assert _money(cf["closing_cash"]) == D("200.00")
        categories = {c["category"]: c["amount"] for c in cf["categories"]}
        assert _money(categories.get("Operating Activities", 0.0)) == D("200.00")

    def test_cash_flow_fallback_when_no_gl_cash_movement(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_cash_flow

        company = _fresh_company(odoo_env, "cf-empty")
        cf = compute_cash_flow(odoo_env, company, date(2026, 1, 1), date(2026, 12, 31))
        assert "payment executions" in cf["basis"]
        assert _money(cf["net_movement"]) == D("0.00")

    def test_consolidated_sums_companies(self, odoo_env):
        from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import compute_consolidated

        self._posted_company(odoo_env, "consol-a", income=500.0, expense=300.0)
        self._posted_company(odoo_env, "consol-b", income=200.0, expense=100.0)
        report = compute_consolidated(odoo_env, date(2026, 1, 1), date(2026, 12, 31), "pnl")
        assert report["company_count"] >= 2
        assert _money(report["net_profit"]) >= D("300.00")  # 200 + 100 from the two above
        assert len(report["per_company"]) == report["company_count"]
        assert "eliminations not applied" in report["basis"]
