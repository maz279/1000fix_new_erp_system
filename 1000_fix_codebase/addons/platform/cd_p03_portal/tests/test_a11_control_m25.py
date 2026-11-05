# A11 audit, module M25 Business Intelligence (cd_bi_reporting + controllers/a11/m25.py).
#
# Convention (A05 style): a pytest PASS means the CONTROL HELD; a FAIL means a
# GAP (the assertion message names it). Tests whose name contains `_ref_` are
# labelled REFERENCE runs (admin/superuser, or a correctness baseline) and are
# counted separately. Everything runs inside the `odoo_env` fixture, which rolls
# the transaction back. Attacks run as NON-ADMIN users created in the
# transaction (base.group_user + one operating unit). Investigation only.
import datetime
import json
import types

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
OPEN = (
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
    "ready",
)


class Ctx:
    pass


_PGTYPE = {
    "char": "varchar",
    "selection": "varchar",
    "text": "text",
    "html": "text",
    "integer": "int4",
    "many2one": "int4",
    "boolean": "bool",
    "float": "numeric",
    "monetary": "numeric",
    "date": "date",
    "datetime": "timestamp",
    "json": "jsonb",
}


def heal_schema(env, models):
    """Other sessions' uncommitted work (outside A11) adds fields whose columns are not yet in
    fix_test_a11c (e.g. fix_device.approval_state). Add the missing columns INSIDE the test
    transaction (PostgreSQL DDL is transactional, so the rollback removes them). Returns what was added."""
    added = []
    for name in models:
        M = env[name]
        env.cr.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s", (M._table,)
        )
        have = {r[0] for r in env.cr.fetchall()}
        for fname, f in M._fields.items():
            if f.store and f.column_type and fname not in have and f.type in _PGTYPE:
                env.cr.execute(
                    'ALTER TABLE "%s" ADD COLUMN "%s" %s' % (M._table, fname, _PGTYPE[f.type])
                )
                added.append("%s.%s" % (M._table, fname))
    if added:
        print("SCHEMA_HEAL (rolled back):", added)
    return added


def _user(env, login, ou, company, extra=()):
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in extra]
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, groups)],
                "company_id": company.id,
                "company_ids": [(6, 0, company.ids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def _branch(env, ou, code):
    entity = env["fix.entity"].search([("company_id", "=", ou.company_id.id)], limit=1) or env[
        "fix.entity"
    ].create(
        {"legal_name": "A11 Entity %s" % code, "code": "E%s" % code, "company_id": ou.company_id.id}
    )
    return env["fix.branch"].create(
        {
            "name": "A11 Branch %s" % code,
            "code": "B%s" % code,
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.healed = heal_schema(
        env,
        [
            "fix.device",
            "fix.service.order",
            "fix.estimate",
            "fix.estimate.line",
            "fix.ar.invoice",
            "fix.complaint",
            "crm.lead",
            "hr.employee",
            "res.partner",
            "fix.branch",
            "fix.entity",
            "res.users",
            "operating.unit",
            "res.company",
        ],
    )
    x.co = env.company
    x.ou_a = env["operating.unit"].search([("company_id", "=", x.co.id)], limit=1)
    x.ou_b = env["operating.unit"].create(
        {
            "name": "A11 OU B",
            "code": "A11OUB",
            "company_id": x.co.id,
            "partner_id": x.co.partner_id.id,
        }
    )
    x.co_b = env["res.company"].create({"name": "A11 Probe Company B"})
    x.ou_cb = env["operating.unit"].create(
        {
            "name": "A11 OU CoB",
            "code": "A11OUCB",
            "company_id": x.co_b.id,
            "partner_id": x.co_b.partner_id.id,
        }
    )
    x.clerk = _user(env, "a11m25_clerk", x.ou_a, x.co)
    x.clerk2 = _user(env, "a11m25_clerk2", x.ou_a, x.co)
    x.customer = env["res.partner"].create({"name": "A11 M25 Customer"})
    x.br_a = _branch(env, x.ou_a, "A11A")
    x.br_b = _branch(env, x.ou_b, "A11B")
    brand = env["fix.brand"].create({"name": "A11M25Brand", "code": "A11M25"})
    model = env["fix.device.model"].create({"name": "A11M25 model", "brand_id": brand.id})
    x.device = env["fix.device"].create({"device_model_id": model.id, "owner_id": x.customer.id})
    x.orders_a = env["fix.service.order"]
    x.orders_b = env["fix.service.order"]
    for i in range(2):
        x.orders_a |= _order(x, x.br_a, x.ou_a, "A%d" % i)
    for i in range(3):
        x.orders_b |= _order(x, x.br_b, x.ou_b, "B%d" % i)
    env.flush_all()
    return x


def _order(x, branch, ou, tag):
    return x.env["fix.service.order"].create(
        {
            "device_id": x.device.id,
            "customer_id": x.customer.id,
            "branch_id": branch.id,
            "operating_unit_id": ou.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "A11 M25 probe %s" % tag,
        }
    )


def m25():
    import odoo.addons.cd_p03_portal.controllers.a11.m25 as mod

    return mod


def sql1(env, q, args=()):
    env.flush_all()
    env.cr.execute(q, args)
    return env.cr.fetchone()[0]


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    mod = m25()
    ctl = g.P03GenericApiController()

    def raw(fn):
        return getattr(fn, "original_endpoint", fn)

    req = types.SimpleNamespace(env=c.env(user=c.clerk.id))
    old = (getattr(g, "request", None), getattr(s, "request", None), getattr(mod, "request", None))
    g.request = s.request = mod.request = req
    try:
        yield types.SimpleNamespace(
            write=lambda **kw: raw(g.P03GenericApiController.model_write)(ctl, **kw),
            action=lambda **kw: raw(g.P03GenericApiController.model_action)(ctl, **kw),
            records=lambda **kw: raw(g.P03GenericApiController.model_records)(ctl, **kw),
            report=lambda **kw: raw(g.P03GenericApiController.model_report)(ctl, **kw),
            bi_kpis=lambda **kw: raw(mod.P03BiApi.bi_kpis)(mod.P03BiApi(), **kw),
            bi_role=lambda **kw: raw(mod.P03BiApi.bi_role)(mod.P03BiApi(), **kw),
            # switch the caller the surfaces see (l06: the BI operator leg)
            as_user=lambda u: setattr(req, "env", c.env(user=u.id)),
        )
    finally:
        g.request, s.request, mod.request = old


# ====================================================================== KPI correctness / scope
def test_m25_k01_ref_open_orders_matches_sql_company_wide(c):
    """REFERENCE: for a company-wide reader the open-orders KPI equals direct SQL."""
    m = m25()._metrics(c.env)
    sql = sql1(
        c.env,
        "SELECT count(*) FROM fix_service_order WHERE state = ANY(%s) AND company_id = %s",
        (list(OPEN), c.co.id),
    )
    assert m["open_orders"] == sql, "KPI open_orders=%s vs SQL %s" % (m["open_orders"], sql)


def test_m25_k02_kpi_scoped_to_users_operating_unit(c):
    """Attack: clerk (OU A only) reads the BI metric bank. BRU-BID-02: analytical scope is
    inherited from the user's ERP scope. Safe: open_orders == what the clerk may search."""
    cenv = c.env(user=c.clerk.id)
    own = cenv["fix.service.order"].search_count([("state", "in", list(OPEN))])
    m = m25()._metrics(cenv)
    assert m["open_orders"] == own, (
        "GAP: BI open_orders for an OU-A clerk = %d, but the clerk's own record rules allow %d "
        "(the KPI reads sudo() + company only, so OU B's %d orders leak into OU A's dashboard)"
        % (m["open_orders"], own, len(c.orders_b))
    )


def test_m25_k03_p03_bi_kpis_route_scoped(c, p03):
    """Attack (c) path: /p03/bi/kpis in-process as the clerk. Safe: open_orders == clerk's scope."""
    cenv = c.env(user=c.clerk.id)
    own = cenv["fix.service.order"].search_count([("state", "in", list(OPEN))])
    out = p03.bi_kpis()
    assert out["M25"]["open_orders"] == own, (
        "GAP: /p03/bi/kpis returned open_orders=%s to the OU-A clerk; their scope allows %d"
        % (out["M25"]["open_orders"], own)
    )


def test_m25_k04_complaints_kpi_company_scoped(c):
    """Attack: a complaint of company B; clerk is company A only. Safe: not counted."""
    before = m25()._metrics(c.env(user=c.clerk.id))["complaints_open"]
    c.env["fix.complaint"].create(
        {
            "name": "A11 CoB complaint",
            "description": "probe",
            "customer_id": c.customer.id,
            "company_id": c.co_b.id,
            "operating_unit_id": c.ou_cb.id,
        }
    )
    after = m25()._metrics(c.env(user=c.clerk.id))["complaints_open"]
    assert after == before, (
        "GAP: company-B complaint counted on company-A clerk's Quality/CEO dashboard "
        "(complaints_open %s -> %s; fix.complaint read with sudo().search_count, no company filter)"
        % (before, after)
    )


def test_m25_k05_pipeline_value_company_scoped(c):
    """Attack: a company-B opportunity worth 987,654. Safe: absent from company A's pipeline value."""
    before = m25()._metrics(c.env(user=c.clerk.id))["pipeline_value"] or 0
    c.env["crm.lead"].create(
        {
            "name": "A11 CoB opp",
            "type": "opportunity",
            "company_id": c.co_b.id,
            "expected_revenue": 987654,
        }
    )
    after = m25()._metrics(c.env(user=c.clerk.id))["pipeline_value"] or 0
    assert after == before, (
        "GAP: company-B opportunity adds %.0f to company-A clerk's CEO/CCO 'Pipeline Value' (%s -> %s)"
        % (after - before, before, after)
    )


def test_m25_k06_headcount_company_scoped(c):
    """Attack: an employee of company B. Safe: not in company A's People Analytics headcount."""
    before = m25()._metrics(c.env(user=c.clerk.id))["employees_active"]
    c.env["hr.employee"].create({"name": "A11 CoB employee", "company_id": c.co_b.id})
    after = m25()._metrics(c.env(user=c.clerk.id))["employees_active"]
    assert after == before, "GAP: company-B employee counted in company-A headcount (%s -> %s)" % (
        before,
        after,
    )


def test_m25_k07_tiles_need_source_read_access(c):
    """Attack: the clerk holds NO read ACL on fix.dunning, hr.attendance (others') or res.users.log.
    Safe: the corresponding tiles are withheld ('—'/None) for them."""
    cenv = c.env(user=c.clerk.id)
    leaks = []
    m = m25()._metrics(cenv)
    if not cenv["fix.dunning"].has_access("read") and m.get("dunning_active") is not None:
        leaks.append("dunning_active=%s (no fix.dunning read ACL)" % m["dunning_active"])
    att_own = (
        cenv["hr.attendance"].search_count([]) if cenv["hr.attendance"].has_access("read") else 0
    )
    if (
        m.get("present_today") is not None
        and m["present_today"] != att_own
        and m["present_today"] > att_own
    ):
        leaks.append("present_today=%s (own attendance rows=%s)" % (m["present_today"], att_own))
    usage = m25()._weekly_usage(cenv)
    if not cenv["res.users.log"].has_access("read") and usage is not None:
        leaks.append("weekly_manager_usage=%s (no res.users.log read ACL)" % usage)
    assert not leaks, (
        "GAP: tiles computed with sudo from sources the clerk cannot read: " + "; ".join(leaks)
    )


def test_m25_k08_finance_pack_report_scoped(c, p03):
    """Attack (c): /p03/model/report M25 finance_pack as the clerk; AR invoice of OU B (residual 50,000).
    Safe: the OU-B invoice is not in the clerk's AR outstanding."""
    inv = c.env["fix.ar.invoice"].create(
        {
            "customer_id": c.customer.id,
            "operating_unit_id": c.ou_b.id,
            "branch_id": c.br_b.id,
            "source_model": "fix.service.order",
            "source_id": c.orders_b[0].id,
            "invoice_date": datetime.date.today(),
        }
    )
    # force it to an issued invoice with a residual, as the AR ledger would hold it
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_ar_invoice SET state='issued', amount_residual=50000, taxable_amount=50000 WHERE id=%s",
        (inv.id,),
    )
    c.env.invalidate_all()
    own_visible = c.env(user=c.clerk.id)["fix.ar.invoice"].search_count([("id", "=", inv.id)])
    out = p03.report(module="M25", report="finance_pack")
    ar = [r for r in out.get("rows", []) if r["metric"] == "AR outstanding"]
    val = ar[0]["value"] if ar else None
    assert own_visible == 1 or not val, (
        "GAP: OU-A clerk cannot read the OU-B invoice (search_count=%d) but the Finance Pack "
        "(downloadable via /p03/model/report/export) shows AR outstanding %s including it"
        % (own_visible, val)
    )


def test_m25_k09_delivered_mtd_is_delivery_dated(c):
    """Business logic: 'Delivered MTD' should count orders DELIVERED this month. Attack: an
    order delivered 2025-01-15 receives any later edit (write_date = now)."""
    o = c.orders_a[0]
    c.env.flush_all()
    c.env.cr.execute(
        "UPDATE fix_service_order SET state='delivered', delivered_at='2025-01-15', write_date='2025-01-15' "
        "WHERE id=%s",
        (o.id,),
    )
    c.env.invalidate_all()
    before = m25()._metrics(c.env)["delivered_mtd"]
    c.env.cr.execute("UPDATE fix_service_order SET write_date=now() WHERE id=%s", (o.id,))
    c.env.invalidate_all()
    after = m25()._metrics(c.env)["delivered_mtd"]
    assert after == before, (
        "GAP: an order delivered on 2025-01-15 counts in 'Delivered MTD' once anyone edits it "
        "(%s -> %s; the KPI filters write_date, not delivered_at/closed_at)" % (before, after)
    )


def test_m25_k10_revenue_tile_named_what_it_measures(c):
    """Business logic (E5/M25-3): the money tile measures the value of
    APPROVED QUOTES and is named exactly that. An approved estimate moves it —
    but never the invoiced figures, and no presentation calls it 'Revenue'."""
    before = m25()._metrics(c.env)
    est = c.env["fix.estimate"].create(
        {
            "order_id": c.orders_a[1].id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "A11 part",
                        "line_type": "part",
                        "quantity": 1,
                        "unit_price": 40000,
                    },
                )
            ],
        }
    )
    c.env.flush_all()
    c.env.cr.execute("UPDATE fix_estimate SET state='approved' WHERE id=%s", (est.id,))
    c.env.invalidate_all()
    after = m25()._metrics(c.env)
    assert after["revenue_mtd"] == before["revenue_mtd"] + est.grand_total, (
        "the approved-quote tile must move by the quote's grand_total (%s -> %s, quote %.0f)"
        % (before["revenue_mtd"], after["revenue_mtd"], est.grand_total)
    )
    assert after["invoiced_mtd"] == before["invoiced_mtd"], "an un-invoiced quote is not an invoice"
    assert (
        after["invoiced_taxable_mtd"] == before["invoiced_taxable_mtd"]
    ), "an un-invoiced quote must not move invoiced taxable value"
    # every presentation names it what it measures (executive pack, company-wide reader)
    wide = _user(
        c.env, "a11m25_wide", c.ou_a, c.co, extra=("cd_bi_reporting.group_bi_company_wide",)
    )
    rows = m25().executive_pack(c.env(user=wide.id))["rows"]
    labels = [r["metric"] for r in rows]
    assert any("Approved quotes MTD" in lab for lab in labels), (
        "the quote tile must be named as quotes: %s" % labels
    )
    assert not any(lab.strip().lower().startswith("revenue") for lab in labels), (
        "no executive row may claim booked revenue: %s" % labels
    )
    quote_row = next(r for r in rows if "Approved quotes MTD" in r["metric"])
    assert "estimate" in quote_row["basis"], (
        "the basis must state the source: %r" % quote_row["basis"]
    )


def test_m25_k11_dashboards_live_is_measured(c, p03):
    """Typed KPI: 'Dashboards Live' with ZERO saved dashboards in the company. Safe: 0."""
    c.env["fix.bi.dashboard"].search([]).unlink()
    out = p03.bi_kpis()["M25"]
    assert out["dashboards_live"] == 0, (
        "GAP: dashboards_live=%s with 0 saved dashboards (hard-coded '9 +' in m25.py), "
        "standard_reports=%s is a constant" % (out["dashboards_live"], out["standard_reports"])
    )


def test_m25_k12_scheduled_distributions_company_scoped(c, p03):
    """(G8 + scoping) recipients are an INTERNAL allow-list — every address
    must be an active internal user of the schedule's own company — and a
    company-B schedule never moves company A's KPI."""
    ops_b = _user(c.env, "a11m25_cob_ops", c.ou_cb, c.co_b)
    ops_b.write({"email": "ops@cob.example"})
    # an external address is refused outright (the allow-list is the control)
    with pytest.raises(REFUSED, match="not an active internal user"):
        c.env["fix.bi.distribution.schedule"].with_company(c.co_b).create(
            {
                "name": "CoB pack ext",
                "report_key": "M25:finance_pack",
                "recipients": "cfo@cob.example",
            }
        )
    before = p03.bi_kpis()["M25"]["scheduled_distributions"]
    c.env["fix.bi.distribution.schedule"].with_company(c.co_b).create(
        {"name": "CoB pack", "report_key": "M25:finance_pack", "recipients": "ops@cob.example"}
    )
    after = p03.bi_kpis()["M25"]["scheduled_distributions"]
    assert after == before, (
        "GAP: a company-B schedule moves company A's 'Scheduled Distributions' %s -> %s "
        "(KPI not caller-company scoped)" % (before, after)
    )


# ====================================================================== distribution / exfiltration
def test_m25_s01_clerk_cannot_create_schedule_orm(c):
    """Attack (b): plain user creates a schedule mailing the Finance Pack to an outside address."""
    with pytest.raises(AccessError):
        c.env["fix.bi.distribution.schedule"].with_user(c.clerk).create(
            {"name": "x", "report_key": "M25:finance_pack", "recipients": "drop@evil.example"}
        )


def test_m25_s02_clerk_cannot_create_schedule_p03(c, p03):
    """Attack (c): same through /p03/model/write (the form the screen offers)."""
    out = p03.write(
        model="fix.bi.distribution.schedule",
        values={
            "name": "x",
            "report_key": "M25:finance_pack",
            "recipients": "drop@evil.example",
            "cadence": "daily",
            "format": "csv",
        },
    )
    assert "error" in out, "GAP: clerk created distribution schedule %s via P03" % out


def test_m25_s03_ref_schedule_validates_recipients_and_report(c):
    """REFERENCE (admin, the only role allowed): a schedule to an external domain for a report key
    that does not exist, and for another area's payroll report. Safe: refused (recipient domain
    whitelist, report existence and the recipients' own entitlement to the content)."""
    admin = c.env.ref("base.user_admin")
    try:
        s = (
            c.env["fix.bi.distribution.schedule"]
            .with_user(admin)
            .create(
                {
                    "name": "exfil",
                    "report_key": "M09:payroll_register_full",
                    "recipients": "drop@evil.example, x@gmail.com",
                }
            )
        )
    except REFUSED:
        return
    pytest.fail(
        "GAP (reference): schedule %s accepted with external recipients %r and report_key %r — no "
        "domain allow-list, no report-key check, no recipient-entitlement check (BRU-BID-02/03/11)"
        % (s.id, s.recipients, s.report_key)
    )


def test_m25_s04_distribution_and_alert_have_a_runner(c):
    """Wiring: a schedule/alert must be executed by something (cron or method)."""
    crons = (
        c.env["ir.cron"]
        .sudo()
        .search(
            [
                (
                    "model_id.model",
                    "in",
                    [
                        "fix.bi.distribution.schedule",
                        "fix.bi.alert.subscription",
                        "fix.bi.sync.config",
                    ],
                )
            ]
        )
    )
    methods = [
        n
        for n in dir(type(c.env["fix.bi.distribution.schedule"]))
        if n.startswith(("action_send", "cron_", "_cron", "action_run"))
    ] + [
        n
        for n in dir(type(c.env["fix.bi.alert.subscription"]))
        if n.startswith(("cron_", "_cron", "action_eval", "action_check"))
    ]
    assert crons and methods, (
        "GAP (wiring): %d crons and methods %s for distribution/alerts/sync — schedules never send, "
        "alerts never evaluate (last_value/last_checked_at stay empty), sync never runs on cadence"
        % (len(crons), methods)
    )


def test_m25_s05_ref_alert_metric_key_validated(c):
    """REFERENCE (admin): an alert on a metric key that no dashboard computes. Safe: refused."""
    admin = c.env.ref("base.user_admin")
    try:
        a = (
            c.env["fix.bi.alert.subscription"]
            .with_user(admin)
            .create(
                {
                    "name": "x",
                    "metric_key": "no_such_metric",
                    "threshold": 1,
                    "recipients": "x@evil.example",
                }
            )
        )
    except REFUSED:
        return
    keys = set(m25()._metrics(c.env))
    pytest.fail(
        "GAP (reference): alert %s on metric_key 'no_such_metric' accepted (known keys: %d)"
        % (a.id, len(keys))
    )


# ====================================================================== sync config / log
def test_m25_c01_clerk_cannot_edit_sync_config_orm(c):
    """Attack (b): clerk retargets the BI sync (target_workspace, dataset_scope=full)."""
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    with pytest.raises(AccessError):
        cfg.with_user(c.clerk).write(
            {"target_workspace": "https://evil.example/ingest", "dataset_scope": "full"}
        )


def test_m25_c02_clerk_cannot_edit_sync_config_p03(c, p03):
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    out = p03.write(
        model="fix.bi.sync.config",
        record_id=cfg.id,
        values={"target_workspace": "https://evil.example/ingest", "dataset_scope": "full"},
    )
    assert "error" in out, "GAP: clerk retargeted BI sync config via P03: %s" % out


def test_m25_c03_ref_sync_transport_fail_closed(c):
    """REFERENCE (E7 decision): the config holds NO credential field — the
    outbound transport stays disabled until operator credentials are
    provisioned (fail-closed), and 'Test connection' says exactly that instead
    of claiming external reachability it cannot have."""
    f = c.env["fix.bi.sync.config"]._fields
    cred = [
        n
        for n in f
        if any(k in n for k in ("secret", "token", "password", "client_id", "endpoint", "url"))
    ]
    assert not cred, "no credential may live on the sync config: %s" % cred
    help_txt = (f["target_workspace"].help or "").lower()
    assert "credentials" in help_txt and "disabled" in help_txt, (
        "target_workspace must say the transport is disabled until credentials exist: %r" % help_txt
    )
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    cfg.action_test_connection()
    assert cfg.last_test_status == "ok"
    assert "fail-closed" in (cfg.last_test_note or ""), (
        "the test must disclose the fail-closed transport, not claim reachability: %r"
        % cfg.last_test_note
    )


def test_m25_l01_clerk_cannot_forge_sync_log_orm(c):
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    with pytest.raises(AccessError):
        c.env["fix.bi.sync.log"].with_user(c.clerk).create(
            {"config_id": cfg.id, "status": "success", "snapshot_json": '{"orders_open": 0}'}
        )


def test_m25_l02_clerk_cannot_forge_sync_log_p03(c, p03):
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    out = p03.write(
        model="fix.bi.sync.log",
        values={"config_id": cfg.id, "status": "success", "snapshot_json": '{"orders_open": 0}'},
    )
    assert "error" in out, "GAP: clerk created a sync log via P03: %s" % out


def test_m25_l03_clerk_run_sync_is_authorised_and_scoped(c, p03):
    """Attack (c): clerk presses 'Run sync' via /p03/model/action. Safe: refused (no BI role), or the
    snapshot equals the company dataset it claims to be."""
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    out = p03.action(model="fix.bi.sync.config", ids=[cfg.id], method="action_run_sync")
    if not out.get("success"):
        return
    log = c.env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)], limit=1)
    snap = json.loads(log.snapshot_json)
    company = m25()._metrics(c.env)["open_orders"]
    assert snap["orders_open"] == company, (
        "GAP: a plain clerk wrote the company 'certified' snapshot (log %s, created via sudo, freshness "
        "reset to %s min) and it records orders_open=%s (clerk's OU only) vs company %s"
        % (log.id, c.env["fix.bi.sync.log"].freshness_minutes(), snap["orders_open"], company)
    )


def test_m25_l04_ref_sync_log_immutable(c):
    """REFERENCE (admin): a success log is edited after the fact (status, snapshot, ran_at)."""
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    cfg.action_run_sync()
    log = c.env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)], limit=1)
    admin = c.env.ref("base.user_admin")
    try:
        log.with_user(admin).write(
            {"snapshot_json": '{"orders_open": 1}', "ran_at": "2030-01-01 00:00:00"}
        )
    except REFUSED:
        return
    pytest.fail(
        "GAP (reference): admin rewrote sync log %s snapshot and set ran_at to 2030 (log is not "
        "immutable; freshness now %s min)" % (log.id, c.env["fix.bi.sync.log"].freshness_minutes())
    )


def test_m25_l05_freshness_company_scoped(c):
    """Freshness of company A must not be refreshed by a company-B run. The
    log is append-only (E7/M25-10), so the control COMPARES readings across
    the run instead of clearing them."""
    before = c.env["fix.bi.sync.log"].with_user(c.clerk).freshness_minutes()
    cfg_b = c.env["fix.bi.sync.config"].create({"name": "CoB cfg", "company_id": c.co_b.id})
    c.env["fix.bi.sync.log"].create({"config_id": cfg_b.id, "status": "success"})
    after = c.env["fix.bi.sync.log"].with_user(c.clerk).freshness_minutes()
    assert after == before, (
        "GAP: a company-B run moved company A's 'BI Data Freshness' %s -> %s min "
        "(freshness_minutes reads with no company filter)" % (before, after)
    )


def test_m25_l06_test_connection_usable_by_bi_operator(c, p03):
    """Wiring (E7): 'Test connection' is a real whitelisted action for a BI
    operator; a plain user is refused — the operator role is the boundary."""
    cfg = c.env["fix.bi.sync.config"].create({"name": "A11 cfg"})
    out = p03.action(model="fix.bi.sync.config", ids=[cfg.id], method="action_test_connection")
    assert out.get("error"), "GAP: a plain clerk ran the BI sync's test action: %s" % out
    ops = _user(c.env, "a11m25_biops", c.ou_a, c.co, extra=("cd_bi_reporting.group_bi_operator",))
    p03.as_user(ops)
    out = p03.action(model="fix.bi.sync.config", ids=[cfg.id], method="action_test_connection")
    assert out.get("success") and cfg.last_test_status == "ok", (
        "WIRING: the whitelisted action fails for the BI operator role (%s)" % out.get("error")
    )


def test_m25_d01_clerk_cannot_create_dashboard(c, p03):
    out = p03.write(model="fix.bi.dashboard", values={"name": "mine", "role": "cfo"})
    assert "error" in out, "GAP: clerk created a dashboard: %s" % out


def test_m25_d02_dashboard_form_usable(c, p03):
    """Wiring: the module's only CREATE button opens the Dashboard form. Plain users are refused, and
    there is no BI author/analyst group in the module, so only system admins can save one."""
    groups = c.env["res.groups"].sudo().search([("name", "ilike", "BI")])
    acl = (
        c.env["ir.model.access"]
        .sudo()
        .search([("model_id.model", "=", "fix.bi.dashboard"), ("perm_create", "=", True)])
    )
    names = acl.mapped("group_id.name")
    assert any(n not in ("Administrator", "Role / Administrator", "Settings") for n in names), (
        "WIRING: fix.bi.dashboard create granted only to %s; BI groups found: %s — the Dashboard "
        "Builder, Schedule and Alert forms are usable by admins only"
        % (names, groups.mapped("name"))
    )
