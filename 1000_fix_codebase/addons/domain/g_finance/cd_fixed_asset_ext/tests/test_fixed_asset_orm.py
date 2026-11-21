# cd_fixed_asset_ext — live-ORM behaviour of the M49 register, CWIP and the
# dual-book depreciation run.
#
# A08 (2026-11-04): assets come into service from a source (the M19
# capitalisation seam, CWIP capitalisation of an approved capex, a lease);
# CWIP cost is the posted cost booked to the project; the tax book charges the
# annual written-down value from the M51 Third Schedule master; asset.capitalized
# is published on capitalisation only. Tests that asserted the old behaviour
# (draft assets publishing asset.capitalized, typed CWIP amounts, monthly
# compounding of the tax book) were rewritten to the controlled paths.
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

from .conftest import balance, fixture_ou

pytestmark = [pytest.mark.financial]

D = Decimal


def _money(value) -> Decimal:
    return D(str(value)).quantize(D("0.01"))


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _asset(env, **vals):
    base = {
        "name": "Diagnostic bench DHK-01",
        "category": "workshop_equipment",
        "gross": 120000.0,
        "salvage": 20000.0,
        "life_months": 50,
        "purchase_date": date(2026, 7, 1),
        # FIN-01: depreciation posts on the asset's own branch (no first-OU fallback)
        "operating_unit_id": fixture_ou(env).id,
    }
    base.update(vals)
    return env["fix.fixed.asset"].create(base)


def _post(env, lines, when):
    journal = env["account.journal"].search(
        [("company_id", "=", env.company.id), ("type", "=", "general")], limit=1
    )
    move = env["account.move"].create(
        {
            "journal_id": journal.id,
            "date": when,
            "line_ids": [
                (0, 0, {"account_id": a.id, "name": "m49", "debit": dr, "credit": cr})
                for a, dr, cr in lines
            ],
        }
    )
    move.action_post()
    return move


def _seam(m49, gross, when):
    """The M19 capitalisation seam of a posted acquisition (arrangement)."""
    env, acc = m49["env"], m49["accounts"]
    move = _post(env, [(acc["asset"], gross, 0.0), (acc["proceeds"], 0.0, gross)], when)
    line = move.line_ids.filtered(lambda ln: ln.account_id == acc["asset"])
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return env["fix.fixed.asset.seam"].create(
        {
            "operating_unit_id": ou.id,
            "name": "SEAM %s" % move.id,
            "move_line_id": line.id,
            "amount": gross,
        }
    )


# context_today, not Date.today(): the product dates these records with
# fields.Date.context_today, and Bangladesh runs UTC+6 — between 18:00
# UTC and midnight the two disagree, and on the 1st they disagree by a
# MONTH (found 2026-11-01).
def _this_month(env=None):
    today = fields.Date.context_today(env.user) if env else fields.Date.today()
    return today.replace(day=1)


class TestFixedAsset:
    def test_straight_line_depreciation_and_no_event_for_a_draft(self, odoo_env):
        asset = _asset(odoo_env)
        assert _money(asset.monthly_depreciation) == D("2000.00")  # (120,000 - 20,000) / 50
        assert asset.state == "draft"
        assert asset.code and asset.code.startswith("FA-")
        assert asset.depreciation_start == date(2026, 7, 1)
        # A08 M49-11: a draft register entry is not a capitalisation
        assert _events(odoo_env, "asset.capitalized", asset.id) == []

    def test_category_defaults_life_salvage_and_label(self, m49):
        cat = m49["category"]
        cat.salvage_percent = 10.0
        asset = m49["env"]["fix.fixed.asset"].create(
            {
                "name": "Scope",
                "category_id": cat.id,
                "gross": 50000.0,
                "purchase_date": date(2026, 7, 9),
            }
        )
        assert (asset.life_months, asset.salvage, asset.category) == (50, 5000.0, cat.name)

    def test_rounding_and_recompute(self, odoo_env):
        asset = _asset(odoo_env, gross=1000.0, salvage=0.0, life_months=3)
        assert _money(asset.monthly_depreciation) == D("333.33")
        asset.life_months = 0
        assert asset.monthly_depreciation == 0.0

    def test_invalid_depreciation_inputs_are_validation_errors(self, odoo_env):
        with pytest.raises(ValidationError, match="salvage above gross"), odoo_env.cr.savepoint():
            _asset(odoo_env, gross=100.0, salvage=200.0)

    def test_activation_needs_a_category_and_a_source(self, m49):
        env = m49["env"]
        bare = _asset(env)
        with pytest.raises(UserError, match="Choose the asset category"), env.cr.savepoint():
            bare.action_activate()
        no_source = _asset(env, category_id=m49["category"].id)
        with pytest.raises(UserError, match="no source"), env.cr.savepoint():
            no_source.action_activate()
        asset = _asset(
            env, category_id=m49["category"].id, seam_id=_seam(m49, 120000.0, date(2026, 7, 1)).id
        )
        asset.action_activate()
        assert asset.state == "active" and asset.seam_id.consumed
        (event,) = _events(env, "asset.capitalized", asset.id)
        assert event["gross"] == 120000.0 and event["move_id"] == asset.acquisition_move_id.id

    def test_accrue_month_posts_gl_and_is_idempotent(self, m49):
        """Defect fixed: the accrual only published an event — no GL entry
        and no protection against a second accrual in the same month."""
        env, acc = m49["env"], m49["accounts"]
        asset = _asset(
            env,
            category_id=m49["category"].id,
            purchase_date=date(2026, 1, 1),
            seam_id=_seam(m49, 120000.0, date(2026, 1, 1)).id,
        )
        with pytest.raises(UserError, match="Only ACTIVE assets accrue"), env.cr.savepoint():
            asset.action_accrue_month()
        asset.action_activate()
        asset.action_accrue_month()
        line = asset.depreciation_line_ids
        assert (line.book, line.period_start, line.amount, line.state) == (
            "book",
            _this_month(env),
            2000.0,
            "posted",
        )
        assert line.move_id.state == "posted"
        assert balance(env, acc["expense"]) == 2000.0
        assert balance(env, acc["accum"]) == -2000.0
        assert _events(env, "depreciation.accrued", asset.id) == [
            {"asset": "Diagnostic bench DHK-01", "amount": 2000.0, "move_id": line.move_id.id}
        ]
        with pytest.raises(UserError, match="already depreciated"), env.cr.savepoint():
            asset.action_accrue_month()
        assert balance(env, acc["expense"]) == 2000.0
        assert (asset.accumulated_depreciation, asset.book_nbv) == (2000.0, 118000.0)

    def test_dispose_opens_a_draft_disposal(self, m49):
        env = m49["env"]
        asset = _asset(env, category_id=m49["category"].id, state="active")
        res = asset.action_dispose()
        disposal = env["fix.asset.disposal"].browse(res["disposal_ids"])
        assert (disposal.state, disposal.kind, asset.state) == ("draft", "write_off", "active")
        assert asset.action_dispose()["disposal_ids"] == disposal.ids  # no duplicate draft


class TestDepreciationRun:
    def test_book_run_posts_per_category_and_skips_charged_assets(self, m49):
        env, acc = m49["env"], m49["accounts"]
        cat = m49["category"]
        a = _asset(
            env, name="A", category_id=cat.id, state="active", purchase_date=date(2026, 1, 5)
        )
        b = _asset(
            env,
            name="B",
            category_id=cat.id,
            state="active",
            purchase_date=date(2026, 1, 5),
            gross=60000.0,
            salvage=0.0,
            life_months=12,
        )
        period = date(2026, 3, 1)
        run = env["fix.asset.depreciation.run"].create(
            {"book": "book", "period_start": period, "asset_ids": [(6, 0, (a | b).ids)]}
        )
        run.action_compute()
        assert run.state == "computed"
        assert sorted(run.line_ids.mapped("amount")) == [2000.0, 5000.0]
        run.action_post()
        assert run.state == "posted" and len(run.move_ids) == 1
        assert run.move_ids.date == date(2026, 3, 31)
        assert balance(env, acc["expense"]) == 7000.0
        # a second run for the same month charges nothing twice
        again = env["fix.asset.depreciation.run"].create(
            {"book": "book", "period_start": period, "asset_ids": [(6, 0, (a | b).ids)]}
        )
        again.action_compute()
        assert not again.line_ids
        assert "already charged" in again.note
        with pytest.raises(UserError, match="nothing to post"), env.cr.savepoint():
            again.action_post()

    def test_unique_line_per_asset_book_month(self, m49):
        env = m49["env"]
        asset = _asset(env, category_id=m49["category"].id, state="active")
        run = env["fix.asset.depreciation.run"].create({"period_start": date(2026, 8, 1)})
        Line = env["fix.asset.depreciation.line"]
        Line.create(
            {
                "run_id": run.id,
                "asset_id": asset.id,
                "book": "book",
                "period_start": date(2026, 8, 1),
                "amount": 1.0,
            }
        )
        with pytest.raises(Exception, match=r"unique|duplicate|once per book"), env.cr.savepoint():
            Line.create(
                {
                    "run_id": run.id,
                    "asset_id": asset.id,
                    "book": "book",
                    "period_start": date(2026, 8, 1),
                    "amount": 1.0,
                }
            )
            env.flush_all()

    def test_missing_accounts_fail_closed(self, m49):
        env = m49["env"]
        m49["category"].expense_account_id = False
        asset = _asset(env, category_id=m49["category"].id, state="active")
        run = env["fix.asset.depreciation.run"].create(
            {"period_start": date(2026, 9, 1), "asset_ids": [(6, 0, asset.ids)]}
        )
        run.action_compute()
        moves_before = env["account.move"].search_count([])
        with pytest.raises(UserError, match="Depreciation Expense Account"), env.cr.savepoint():
            run.action_post()
        assert env["account.move"].search_count([]) == moves_before
        assert run.state == "computed"

    def test_tax_book_annual_wdv_no_gl(self, m49):
        """A08 M49-8: the M51 Third Schedule rate, refused until the adviser
        confirms it, charged on the annual written-down value."""
        env = m49["env"]
        asset = _asset(
            env,
            category_id=m49["category"].id,
            state="active",
            gross=120000.0,
            salvage=0.0,
            purchase_date=date(2026, 8, 1),
        )
        rate = env["fix.tax.rate"].find_rate("depreciation", "ITA3-PLANT", date(2026, 8, 1))
        assert rate.verify_with_adviser  # seeded master data awaits the adviser
        run = env["fix.asset.depreciation.run"].create(
            {"book": "tax", "period_start": date(2026, 8, 1), "asset_ids": [(6, 0, asset.ids)]}
        )
        with pytest.raises(UserError, match="not yet confirmed"), env.cr.savepoint():
            run.action_compute()
        rate.action_record_adviser_verification("ADV-TEST")
        run.action_compute()
        expected = round(120000.0 * rate.rate / 100.0 / 12.0, 2)
        assert run.line_ids.amount == expected
        run.action_post()
        assert not run.move_ids and run.line_ids.state == "posted"
        nxt = env["fix.asset.depreciation.run"].create(
            {"book": "tax", "period_start": date(2026, 9, 1), "asset_ids": [(6, 0, asset.ids)]}
        )
        nxt.action_compute()
        # the same month of the same tax year: the opening WDV does not compound
        assert nxt.line_ids.amount == expected
        assert asset.tax_wdv == round(120000.0 - expected, 2)

    def test_tax_run_without_rate_fails_closed(self, m49):
        env = m49["env"]
        m49["category"].tax_rate_code = "NO-SUCH-CLASS"
        asset = _asset(env, category_id=m49["category"].id, state="active")
        run = env["fix.asset.depreciation.run"].create(
            {"book": "tax", "period_start": date(2026, 8, 1), "asset_ids": [(6, 0, asset.ids)]}
        )
        with pytest.raises(UserError, match="NO-SUCH-CLASS"), env.cr.savepoint():
            run.action_compute()

    def test_period_must_start_on_the_first(self, odoo_env):
        with pytest.raises(ValidationError, match="starts on the 1st"), odoo_env.cr.savepoint():
            odoo_env["fix.asset.depreciation.run"].create({"period_start": date(2026, 8, 2)})

    def test_last_month_lands_on_salvage(self, m49):
        env = m49["env"]
        asset = _asset(
            env,
            category_id=m49["category"].id,
            state="active",
            gross=1000.0,
            salvage=0.0,
            life_months=3,
            purchase_date=date(2026, 1, 1),
        )
        for month in (1, 2, 3, 4):
            run = env["fix.asset.depreciation.run"].create(
                {"period_start": date(2026, month, 1), "asset_ids": [(6, 0, asset.ids)]}
            )
            run.action_compute()
            if run.line_ids:
                run.action_post()
        amounts = asset.depreciation_line_ids.sorted("period_start").mapped("amount")
        assert len(amounts) == 3 and round(sum(amounts), 2) == 1000.0  # 4th month: nothing left
        assert asset.book_nbv == 0.0


def _approved_request(env, amount, category=None):
    """An approved capex request (system arrangement of the routed approval,
    which test_a08_m49_controls exercises through the M63 inbox)."""
    return env["fix.capex.request"].create(
        {
            "title": "Capex %s" % amount,
            "amount": amount,
            "category_id": category.id if category else False,
            "state": "approved",
            "dofa_approved": True,
            "dofa_approved_tier": "tier_5",
            "dofa_approved_amount": amount,
            "operating_unit_id": fixture_ou(env).id,
        }
    )


class TestCwip:
    def _cwip(self, m49, name, amount, ou=None, category=None):
        """A CWIP project of an approved capex, with `amount` of posted cost
        booked to it (A08 M49-3: never a typed amount)."""
        env, acc = m49["env"], m49["accounts"]
        cat = category or m49["category"]
        req = _approved_request(env, max(amount, 1.0) * 2, category)
        cw = env["fix.cwip.entry"].browse(req.action_create_cwip()["cwip_ids"])
        ou = ou or fixture_ou(env)
        cw.write({"name": name, "operating_unit_id": ou.id, "category_id": cat.id})
        if amount:
            bill = _post(
                env,
                [(acc["cwip"], amount, 0.0), (acc["proceeds"], 0.0, amount)],
                fields.Date.context_today(env.user),
            )
            cw._fix_book_cost(bill.line_ids.filtered(lambda ln: ln.account_id == acc["cwip"]))
        if not category:
            cw.category_id = False
        return cw

    def test_capitalise_every_entry_and_post_reclass(self, m49):
        env, acc, cat = m49["env"], m49["accounts"], m49["category"]
        ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
        a = self._cwip(m49, "Server room fit-out", 450000.0, ou=ou)
        b = self._cwip(m49, "Van racking", 60000.0)
        assets = (a | b).action_capitalise(cat, 60, salvage=6000.0)
        assert len(assets) == 2
        assert (a.state, b.state) == ("capitalised", "capitalised")
        fit_out = a.asset_id
        assert (fit_out.state, fit_out.category_id, fit_out.operating_unit_id) == (
            "active",
            cat,
            ou,
        )
        assert _money(fit_out.monthly_depreciation) == D("7400.00")
        assert balance(env, acc["asset"]) == 510000.0
        assert balance(env, acc["cwip"]) == 0.0  # booked cost in, capitalised out
        (event,) = _events(env, "asset.capitalized", fit_out.id)
        assert (event["gross"], event["cwip_id"], event["move_id"]) == (
            450000.0,
            a.id,
            a.move_id.id,
        )

    def test_category_by_code_and_record_fields(self, m49):
        cat = m49["category"]
        entry = self._cwip(m49, "Workshop", 90000.0, category=cat)
        entry.life_months = 36
        asset = entry.action_capitalise()
        assert (asset.category_id, asset.life_months) == (cat, 36)
        other = self._cwip(m49, "Bench", 1000.0)
        assert other.action_capitalise(cat.code).category_id == cat

    def test_refusals(self, m49):
        env, cat = m49["env"], m49["category"]
        empty = self._cwip(m49, "Nothing yet", 0.0, category=cat)
        with pytest.raises(UserError, match="Nothing accumulated"), env.cr.savepoint():
            empty.action_capitalise()
        no_cat = self._cwip(m49, "No category", 10.0)
        with pytest.raises(UserError, match="Choose the asset category"), env.cr.savepoint():
            no_cat.action_capitalise()
        done = self._cwip(m49, "Done", 10.0, category=cat)
        done.action_capitalise()
        with pytest.raises(UserError, match="already capitalised"), env.cr.savepoint():
            done.action_capitalise()

    def test_missing_cwip_account_fails_closed(self, m49):
        env, cat = m49["env"], m49["category"]
        entry = self._cwip(m49, "Fit-out", 1000.0, category=cat)
        cat.cwip_account_id = False
        with pytest.raises(UserError, match="CWIP Account"), env.cr.savepoint():
            entry.action_capitalise()
        assert entry.state == "open" and not entry.asset_id

    def test_accountant_role_required(self, m49):
        env, cat = m49["env"], m49["category"]
        entry = self._cwip(m49, "Fit-out", 1000.0, category=cat)
        reader = m49["users"]["reader"]
        with pytest.raises(Exception), env.cr.savepoint():  # noqa: B017 — ACL or role refusal
            entry.with_user(reader).action_capitalise()
