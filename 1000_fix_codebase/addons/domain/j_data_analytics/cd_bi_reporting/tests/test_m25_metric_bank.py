# The M25 metric-bank fixes (deep audit B2, Nov 2026), each pinned by a test
# that failed on the old behaviour:
#
#   D-L01/A1-F07  the AR figures include the legacy take-on M20 reads, gated
#                 on the finance entitlement, and the Finance Pack carries a
#                 GL tie-out that reconciles to the trial balance;
#   A1-F01        one failing metric source (a real aborted SQL statement)
#                 withholds only its own tiles — the bank, the packs and the
#                 /p03/model/report route keep answering;
#   A1-F05        the cockpit's usage telemetry survives a failing source;
#   A1-F04        packs apply their period (as-of date_to) or refuse a
#                 mismatched date_from instead of silently ignoring it;
#   A1-F03        honest bases: dashboards_live counts certified dashboards,
#                 standard_reports is the canonical six, weekly usage counts
#                 BI content views;
#   A1-F13        the commercial board counts leads per pipeline;
#   A1-F10        the report-key library lives in the domain module and an
#                 unknown key is refused by every validator;
#   A1-F08        the module's content models are company-isolated.
from datetime import date

import pytest
from odoo.addons.cd_bi_reporting.models.fix_bi_library import (
    REPORT_LIBRARY_KEYS,
    STANDARD_LIBRARY_KEYS,
)
from odoo.addons.cd_p03_portal.controllers.a11 import m25
from odoo.exceptions import UserError, ValidationError

FINANCE = "cd_bi_reporting.group_bi_finance"
COMPANY_WIDE = "cd_bi_reporting.group_bi_company_wide"
AUTHOR = "cd_bi_reporting.group_bi_author"

# a take-on date far enough in the past that the residual is > 60 days old
OLD_TAKEON = date(2026, 7, 1)
FRESH_TAKEON = date(2026, 11, 20)
AS_OF = date(2026, 11, 30)


class Ctx:
    pass


@pytest.fixture
def c(odoo_env):
    if "fix.bi.dashboard" not in odoo_env or "fix.ar.invoice" not in odoo_env:
        pytest.skip("cd_bi_reporting / cd_billing_engine not installed")
    env0 = odoo_env
    tag = "%s" % (date.today().strftime("%H%M%S%f"))
    x = Ctx()
    x.company = env0["res.company"].create({"name": "B2 M25 Co %s" % tag})
    # the caller's companies are exactly this company, so the bank's numbers
    # below are deterministic regardless of what the rest of the DB holds
    x.env = env0(context=dict(env0.context, allowed_company_ids=x.company.ids))
    x.ou = x.env["operating.unit"].create(
        {
            "name": "B2 M25 OU %s" % tag,
            "code": "B2%s" % tag[:6],
            "company_id": x.company.id,
            "partner_id": x.company.partner_id.id,
        }
    )
    Account = x.env["account.account"].with_company(x.company)
    x.ar = Account.create(
        {
            "name": "Trade Receivables control",
            "code": "121000",
            "account_type": "asset_receivable",
            "company_ids": [(6, 0, x.company.ids)],
        }
    )
    x.contra = Account.create(
        {
            "name": "Legacy take-on contra",
            "code": "299901",
            "account_type": "liability_current",
            "company_ids": [(6, 0, x.company.ids)],
        }
    )
    x.mig = x.env["account.journal"].create(
        {"name": "Legacy Take-on", "code": "MIG", "type": "general", "company_id": x.company.id}
    )
    x.partner_a = x.env["res.partner"].create({"name": "B2 M25 Customer A %s" % tag})
    x.partner_b = x.env["res.partner"].create({"name": "B2 M25 Customer B %s" % tag})

    def user(login, *xmlids):
        groups = [x.env.ref("base.group_user").id] + [x.env.ref(g).id for g in xmlids]
        return (
            x.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": "%s-%s@b2m25.test" % (login, tag),
                    "company_id": x.company.id,
                    "company_ids": [(6, 0, x.company.ids)],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    x.fin = user("fin", FINANCE)
    x.wide = user("wide", COMPANY_WIDE)
    x.plain = user("plain")
    x.author = user("author", AUTHOR)
    x.env_fin = x.env(user=x.fin.id)
    x.env_wide = x.env(user=x.wide.id)
    x.env_plain = x.env(user=x.plain.id)
    x.env_author = x.env(user=x.author.id)
    return x


def _takeon(c, partner, amount, when):
    """A legacy take-on line on the AR control (journal MIG), posted the way
    cd_gl_ext's own tests post it."""
    move = c.env["account.move"].create(
        {
            "journal_id": c.mig.id,
            "company_id": c.company.id,
            "date": when,
            "move_type": "entry",
            "ref": "B2 take-on probe",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": c.ar.id,
                        "partner_id": partner.id,
                        "date_maturity": when,
                        "name": "Legacy take-on %s" % partner.name,
                        "debit": amount,
                        "credit": 0.0,
                    },
                ),
                (
                    0,
                    0,
                    {"account_id": c.contra.id, "name": "contra", "debit": 0.0, "credit": amount},
                ),
            ],
        }
    )
    move.action_post()
    return move


_SOURCE_SEQ = iter(range(9_000_001, 9_000_100))


def _issued_invoice(c, taxable, residual, when):
    """An issued invoice with a residual, forced the way the AR ledger would
    hold it (the state machine is not this suite's subject). source_id is
    unique per probe: fix_ar_invoice_source_key_unique."""
    inv = c.env["fix.ar.invoice"].create(
        {
            "customer_id": c.partner_a.id,
            "operating_unit_id": c.ou.id,
            "source_model": "fix.service.order",
            "source_id": next(_SOURCE_SEQ),
            "invoice_date": when,
            "company_id": c.company.id,
        }
    )
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_ar_invoice SET state='issued', amount_residual=%s, taxable_amount=%s "
        "WHERE id=%s",
        (residual, taxable, inv.id),
    )
    c.env.invalidate_all()
    return inv


def _finance_rows(c, **kw):
    out = m25.finance_pack(c.env_fin, **kw)
    return {r["metric"]: r["value"] for r in out["rows"]}


# --------------------------------------------------------------- D-L01 / F07


def test_takeon_joins_the_ar_and_ties_to_the_gl(c):
    """The live defect: 15.4 crore of migrated open receivables reported as
    AR 0 because the tiles summed only fix.ar.invoice. With a posted take-on
    journal the figures carry it, and the GL tie-out closes to ~0."""
    _takeon(c, c.partner_a, 5000.0, OLD_TAKEON)  # 152 days old at 2026-11-30
    _takeon(c, c.partner_b, 3000.0, FRESH_TAKEON)  # 10 days old
    rows = _finance_rows(c, date_to=str(AS_OF))
    print(
        "AR EVIDENCE (take-on only): invoices=%s takeon=%s total=%s gl=%s difference=%s overdue60=%s"
        % (
            rows["AR outstanding — open invoices (৳)"],
            rows["AR outstanding — legacy take-on (৳)"],
            rows["AR outstanding — total (৳)"],
            rows["AR per general ledger — receivable control accounts (৳)"],
            rows["Difference (AR total − GL) (৳)"],
            rows["Overdue > 60d (৳)"],
        )
    )
    assert rows["AR outstanding — open invoices (৳)"] == 0.0
    assert rows["AR outstanding — legacy take-on (৳)"] == 8000.0
    assert rows["AR outstanding — total (৳)"] == 8000.0
    # the take-on is aged from its OWN date on the M20 basis: only the July
    # line is past 60 days
    assert rows["Overdue > 60d (৳)"] == 5000.0
    # the GL tie-out: the take-on IS the GL, so the difference is ~0
    assert rows["AR per general ledger — receivable control accounts (৳)"] == 8000.0
    assert abs(rows["Difference (AR total − GL) (৳)"]) < 0.01


def test_invoice_leg_bridges_to_the_gl(c):
    """An issued operational invoice adds to the AR total but not to the GL —
    the difference row states the bridge instead of hiding it."""
    _takeon(c, c.partner_a, 2000.0, FRESH_TAKEON)
    _issued_invoice(c, 50000.0, 50000.0, date.today())
    rows = _finance_rows(c, date_to=str(AS_OF))
    print(
        "AR EVIDENCE (invoice + take-on): invoices=%s takeon=%s total=%s gl=%s difference=%s"
        % (
            rows["AR outstanding — open invoices (৳)"],
            rows["AR outstanding — legacy take-on (৳)"],
            rows["AR outstanding — total (৳)"],
            rows["AR per general ledger — receivable control accounts (৳)"],
            rows["Difference (AR total − GL) (৳)"],
        )
    )
    assert rows["AR outstanding — open invoices (৳)"] == 50000.0
    assert rows["AR outstanding — legacy take-on (৳)"] == 2000.0
    assert rows["AR outstanding — total (৳)"] == 52000.0
    assert rows["AR per general ledger — receivable control accounts (৳)"] == 2000.0
    assert rows["Difference (AR total − GL) (৳)"] == 50000.0


def test_the_ar_tiles_are_withheld_without_the_finance_entitlement(c):
    """The take-on is a sudo GL read inside M20's helper: a caller without
    the BI finance / company-wide groups gets '—' (None), never the figure —
    and the rest of the bank still measures."""
    _takeon(c, c.partner_a, 5000.0, FRESH_TAKEON)
    m = m25._metrics(c.env_plain)
    for key in (
        "ar_outstanding_invoices",
        "ar_outstanding_takeon",
        "ar_outstanding",
        "overdue_gt_60d_invoices",
        "overdue_gt_60d_takeon",
        "overdue_gt_60d",
    ):
        assert m[key] is None, "plain caller must not see %s" % key
    m2 = m25._metrics(c.env_fin)
    assert m2["ar_outstanding"] == 5000.0
    assert isinstance(m2["open_orders"], int)


# ------------------------------------------------------------------- A1-F01


def _boom(self, domain, *args, **kwargs):
    """A REAL aborted SQL statement — the reference estate's failure mode (a
    missing crm.lead column), not a synthetic exception."""
    self.env.cr.execute("SELECT fix_no_such_column FROM crm_lead LIMIT 1")
    self.env.cr.fetchone()
    return 0


def test_one_failing_source_withholds_only_its_own_tiles(c, monkeypatch):
    from odoo.addons.cd_p03_portal.controllers.a11 import m25 as ctl

    monkeypatch.setattr(type(c.env["crm.lead"]), "search_count", _boom)
    m = m25._metrics(c.env_wide)
    assert m["leads_open"] is None and m["pipeline_value"] is None
    # every metric computed AFTER the broken probe still answers — on the old
    # code the aborted transaction nulled them all
    assert isinstance(m["loyalty_members"], int)
    assert isinstance(m["requisitions_open"], int)
    assert isinstance(m["dunning_active"], int)
    # the report route keeps answering through the broken source
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    class FakeRequest:
        def __init__(self, env):
            self.env = env

    monkeypatch.setattr(api, "request", FakeRequest(c.env_wide))
    monkeypatch.setattr(ctl, "request", FakeRequest(c.env_wide))
    out = api.P03GenericApiController().model_report(module="M25", report="service_kpi_pack")
    assert "rows" in out and not out.get("error"), out


# ------------------------------------------------------------------- A1-F05


def test_usage_telemetry_survives_a_failing_metric_source(c, monkeypatch):
    """The cockpit view is logged even when a metric source breaks — on the
    old code the aborted transaction silently destroyed the telemetry row."""
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
    from odoo.addons.cd_p03_portal.controllers.a11 import m25 as ctl

    class FakeRequest:
        def __init__(self, env):
            self.env = env
            self.httprequest = type("H", (), {"headers": {}})()

    monkeypatch.setattr(type(c.env["crm.lead"]), "search_count", _boom)
    monkeypatch.setattr(api, "request", FakeRequest(c.env_wide))
    monkeypatch.setattr(ctl, "request", FakeRequest(c.env_wide))
    payload = ctl.P03BiApi().bi_role(role="ceo")
    assert payload["role"] == "ceo"
    row = c.env["fix.bi.content.usage"].search(
        [("content_ref", "=", "M25:ceo"), ("user_id", "=", c.wide.id)], limit=1
    )
    assert row, "the cockpit view was not logged (FR-BID-033 telemetry lost)"


# ------------------------------------------------------------------- A1-F04


def test_a_past_month_is_measured_as_of_that_month(c):
    _issued_invoice(c, 1200.0, 1200.0, date(2026, 10, 14))
    _issued_invoice(c, 3000.0, 3000.0, date(2026, 11, 5))
    october = m25.executive_pack(c.env_wide, date_to="2026-10-31")
    rows = {r["metric"]: r["value"] for r in october["rows"]}
    assert rows["Invoices issued MTD"] == 1
    assert rows["Invoiced taxable MTD (৳)"] == 1200.0
    # the November run of the same company does not count October
    november = m25.executive_pack(c.env_wide, date_to="2026-11-30")
    rows_now = {r["metric"]: r["value"] for r in november["rows"]}
    assert rows_now["Invoices issued MTD"] == 1
    assert rows_now["Invoiced taxable MTD (৳)"] == 3000.0


def test_a_mismatched_date_from_is_refused(c):
    """Before, the pack accepted any period and stamped a run with a window
    it never applied; now the MTD contract is enforced loudly."""
    with pytest.raises(UserError, match="month-to-date"):
        m25.executive_pack(c.env_wide, date_from="2026-10-15", date_to="2026-10-31")
    with pytest.raises(UserError, match="month-to-date"):
        m25.finance_pack(c.env_fin, date_from="2026-11-02", date_to="2026-11-30")
    # the first of the month IS accepted
    out = m25.executive_pack(c.env_wide, date_from="2026-11-01", date_to="2026-11-30")
    assert "rows" in out


# ------------------------------------------------------------------- A1-F03


def test_kpi_strip_honest_bases(c, monkeypatch):
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
    from odoo.addons.cd_p03_portal.controllers.a11 import m25 as ctl

    class FakeRequest:
        def __init__(self, env):
            self.env = env

    usage = c.env["fix.bi.content.usage"]
    usage.create(
        {
            "content_type": "role_dashboard",
            "content_ref": "M25:ceo",
            "user_id": c.plain.id,
            "company_id": c.company.id,
            "device_class": "desktop",
        }
    )
    usage.create(
        {
            "content_type": "role_dashboard",
            "content_ref": "M25:cfo",
            "user_id": c.fin.id,
            "company_id": c.company.id,
            "device_class": "desktop",
        }
    )
    # two dashboards: a draft and one certified through the lifecycle context
    Dash = c.env["fix.bi.dashboard"]
    Dash.create({"name": "Draft only", "role": "ceo", "company_id": c.company.id})
    certified = Dash.create({"name": "Live one", "role": "coo", "company_id": c.company.id})
    certified.with_context(bi_lifecycle_engine=True).write(
        {"state": "certified", "certified_by": c.env.ref("base.user_admin").id}
    )
    monkeypatch.setattr(ctl, "request", FakeRequest(c.env_wide))
    monkeypatch.setattr(api, "request", FakeRequest(c.env_wide))
    out = ctl.P03BiApi().bi_kpis()["M25"]
    assert out["dashboards_live"] == 1, "drafts must not count as live dashboards"
    assert out["standard_reports"] == len(STANDARD_LIBRARY_KEYS) == 6
    assert out["weekly_manager_usage"] == 2, "usage = distinct BI viewers in 7 days"
    assert out["approved_quotes_mtd"] == out["revenue_mtd"]


def test_weekly_note_says_created_not_approved(c):
    note = " ".join(m25.weekly_exec_review(c.env_wide)["notes"])
    assert "created" in note and "approved in the week" not in note


# ------------------------------------------------------------------- A1-F13


def test_commercial_board_counts_leads_per_pipeline(c):
    Pipeline = c.env["fix.pipeline"]
    p1 = Pipeline.create(
        {
            "code": "B2P1%s" % c.company.id,
            "name": "B2 Pipeline One",
            "revenue_stream": "msp",
            "company_id": c.company.id,
        }
    )
    p2 = Pipeline.create(
        {
            "code": "B2P2%s" % c.company.id,
            "name": "B2 Pipeline Two",
            "revenue_stream": "amc",
            "company_id": c.company.id,
        }
    )
    Lead = c.env["crm.lead"]
    Lead.create(
        {
            "name": "opp a",
            "type": "opportunity",
            "company_id": c.company.id,
            "pipeline_id": p1.id,
            "expected_revenue": 100.0,
        }
    )
    Lead.create(
        {
            "name": "opp b",
            "type": "opportunity",
            "company_id": c.company.id,
            "pipeline_id": p1.id,
            "expected_revenue": 30.0,
        }
    )
    Lead.create(
        {
            "name": "opp c",
            "type": "opportunity",
            "company_id": c.company.id,
            "pipeline_id": p2.id,
            "expected_revenue": 50.0,
        }
    )
    rows = {r["pipeline"]: r for r in m25.commercial_board(c.env_wide)["rows"]}
    assert rows[p1.code]["open_opportunities"] == 2
    assert rows[p1.code]["open_value"] == 130.0
    assert rows[p2.code]["open_opportunities"] == 1
    assert rows[p2.code]["open_value"] == 50.0


# ------------------------------------------------------------------- A1-F06


def test_money_columns_carry_the_currency(c):
    pack = m25.branch_league(c.env_wide)
    assert pack["kinds"].get("invoiced_mtd") == "monetary"
    assert pack["labels"]["invoiced_mtd"].endswith("(৳)")
    finance = m25.finance_pack(c.env_fin)
    assert any(r["metric"] == "AR outstanding — total (৳)" for r in finance["rows"])
    board = m25.commercial_board(c.env_wide)
    assert board["kinds"].get("open_value") == "monetary"
    assert board["labels"]["open_value"].endswith("(৳)")


# ------------------------------------------------------------------- A1-F02


def test_exec_board_shows_branch_display_names(c):
    entity = c.env["fix.entity"].create(
        {"legal_name": "B2 M25 Entity", "code": "EB2%s" % c.company.id, "company_id": c.company.id}
    )
    branch = c.env["fix.branch"].create(
        {
            "name": "B2 Gulshan CSC",
            "code": "B2G",
            "entity_id": entity.id,
            "operating_unit_id": c.ou.id,
        }
    )
    brand = c.env["fix.brand"].create({"name": "B2Brand", "code": "B2B"})
    model = c.env["fix.device.model"].create({"name": "B2 model", "brand_id": brand.id})
    device = c.env["fix.device"].create({"device_model_id": model.id, "owner_id": c.partner_a.id})
    c.env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": c.partner_a.id,
            "branch_id": branch.id,
            "operating_unit_id": c.ou.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "B2 M25 exec board probe",
        }
    )
    branches = m25._exec_payload(c.env_wide)["branches"]
    assert branches, "the probe order should group under its branch"
    for row in branches:
        assert not str(row["branch"]).startswith("fix.branch("), row
    assert any(row["branch"].startswith("B2 Gulshan CSC") for row in branches)


# ------------------------------------------------------------------- A1-F10


def test_the_controller_library_is_the_domain_library(c):
    assert set(m25.REPORTS) == set(REPORT_LIBRARY_KEYS)
    assert m25.STANDARD_REPORTS and len(m25.STANDARD_REPORTS) == 6


def test_unknown_report_keys_are_refused_everywhere(c):
    with pytest.raises(ValidationError, match="not in the M25 report library"):
        c.env["fix.bi.distribution.schedule"].create(
            {"name": "bad key", "report_key": "M25:no_such_pack", "recipients": c.wide.login}
        )
    with pytest.raises(ValidationError, match="not in the M25 report library"):
        c.env["fix.bi.manual.pack"].create(
            {
                "name": "B2 pack",
                "function_area": "service",
                "frequency": "weekly",
                "owner_id": c.author.id,
                "replacement_report_key": "M25:no_such_pack",
            }
        )
    with pytest.raises(ValidationError, match="metric bank"):
        c.env["fix.bi.alert.subscription"].create(
            {
                "name": "bad metric",
                "metric_key": "no_such_metric",
                "threshold": 1,
                "recipients": "x@y.example",
            }
        )


# ------------------------------------------------------------------- A1-F08


def test_content_models_are_company_isolated(c):
    """A dashboard of ANOTHER company is invisible to this company's user —
    the three content models carried company_id with no ir.rule."""
    other = c.env["res.company"].create({"name": "B2 Other Co"})
    c.env["fix.bi.dashboard"].create(
        {"name": "Other company's dashboard", "role": "ceo", "company_id": other.id}
    )
    c.env_author["fix.bi.dashboard"].create(
        {"name": "Own company dashboard", "role": "ceo", "company_id": c.company.id}
    )
    visible = c.env_author["fix.bi.dashboard"].search_count([])
    assert visible == 1, "the other company's dashboard leaked across the company rule"


# ------------------------------------------------------------------ A3-F03


def test_degraded_data_entity_warns_every_cockpit(c):
    if "fix.data.entity" not in c.env:
        pytest.skip("cd_metric_registry (M62) not installed")
    entity = c.env["fix.data.entity"].create(
        {"name": "B2 Customer Master %s" % c.company.id, "company_id": c.company.id}
    )
    entity.write({"degraded": True})
    notes = m25._quality_incident_notes(c.env_wide)
    assert notes and entity.name in notes[0] and "may be affected" in notes[0]
