# A02 ERP audit, stream B4 (20 Nov 2026): the M04 KPIs and report packs, the
# A02 role-center cues and the A02 printable documents.
#
#   M04-F17 / X-13 / X-14  M04 KPIs and packs: company fence, the screen's
#            period, the Dhaka day, gross variance (shortages and overages
#            apart), issue -> call wait, ready_at ageing of READY orders,
#            confirmed counter sales only, by product category
#   X-15     role-center cues: company fence, invoiced ex-VAT revenue, QC
#            first-pass rate over decided checklists, delivered today by
#            delivered_at at the reader's branch, Dhaka fallback timezone
#   X-17     five A02 documents render from real records
#
# Every test runs against the ORM in a rolled-back transaction.
import datetime as dt
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_front_desk.tests.test_a02_p0_m04 import _refused, m04  # noqa: F401
from odoo.addons.cd_p03_portal.controllers import p03_commercial_docs as docs_api
from odoo.addons.cd_p03_portal.controllers import p03_role_center_api as rc
from odoo.addons.cd_p03_portal.controllers.a02 import m04 as m04ctl
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox
from odoo.exceptions import UserError

DHAKA = "Asia/Dhaka"


@pytest.fixture
def b4(m04):  # noqa: F811
    m = m04
    params = m.env["ir.config_parameter"]
    params.set_param("cd_front_desk.open_shift_scope", "branch")
    params.set_param("cd_front_desk.variance_tolerance_bdt", "100")
    params.set_param("cd_front_desk.price_override_tolerance_pct", "0")
    m.denv = m.env(context=dict(m.env.context, tz=DHAKA))
    m.other_company = m.env["res.company"].create({"name": "A02 B4 Other Company"})
    m.env.user.sudo().write({"company_ids": [(4, m.other_company.id)]})
    m.oenv = m.env(context=dict(m.env.context, tz=DHAKA, allowed_company_ids=[m.other_company.id]))
    m.seq = iter(range(1, 1000))
    return m


def _device(m):
    return m.env["fix.device"].create(
        {
            "device_model_id": m.device.device_model_id.id,
            "owner_id": m.customer.id,
            "serial_number": "SN-B4-%s-%d" % (m.device.id, next(m.seq)),
        }
    )


def _order(m, state="ready", branch=None, **stamps):
    order = m.env["fix.service.order"].create(
        {
            "device_id": _device(m).id,
            "customer_id": m.customer.id,
            "branch_id": (branch or m.branch).id,
            "fault_description": "B4 order",
            "service_type": "walk_in",
        }
    )
    sets = {"state": state, **stamps}
    cols = ", ".join("%s = %%s" % k for k in sets)
    m.env.flush_all()
    m.env.cr.execute(
        "UPDATE fix_service_order SET %s WHERE id = %%s" % cols, [*sets.values(), order.id]
    )
    order.invalidate_recordset()
    return order


def _ago(**kw):
    return fields.Datetime.now() - dt.timedelta(**kw)


# ============================================================== M04 KPI row


def test_a_reader_with_no_operating_unit_sees_no_branch(b4):
    """A02 pass 2 review: the M04 tile fence fails closed."""
    m = b4
    nobody = (
        m.env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "B4 no unit", "login": "b4.nounit@a02.test"})
    )
    nobody.sudo().write({"operating_unit_ids": [(5, 0, 0)]})
    renv = m.env(user=nobody.id)
    assert m04ctl._branch_fence(renv, m.env["fix.service.order"]) == [("id", "=", 0)]
    _order(m, ready_at=_ago(days=10))
    assert m04ctl.kpis(renv)["uncollected_7d"] == 0


def test_uncollected_counts_ready_orders_from_ready_at(b4):
    m = b4
    before = m04ctl.kpis(m.denv)["uncollected_7d"]
    _order(m, ready_at=_ago(days=10), write_date=_ago(days=10))  # uncollected
    _order(m, ready_at=_ago(days=2), write_date=_ago(days=30))  # recent: last write is old
    _order(m, state="delivered", ready_at=_ago(days=20))  # delivered: collected
    assert m04ctl.kpis(m.denv)["uncollected_7d"] - before == 1


def test_variance_is_gross_and_open_shifts_exclude_closed(b4):
    m = b4
    k0 = m04ctl.kpis(m.denv)
    short = m.shift()
    m.count(short, d1000=4)  # -1,000
    over = m.shift(branch=m.branch2)
    m.count(over, d1000=5, d500=1)  # +500
    k1 = m04ctl.kpis(m.denv)
    assert round(k1["cash_shortage_today"] - k0["cash_shortage_today"], 2) == -1000.0
    assert round(k1["cash_overage_today"] - k0["cash_overage_today"], 2) == 500.0
    assert round(k1["cash_variance_today"] - k0["cash_variance_today"], 2) == 1500.0
    assert k1["shifts_open"] - k0["shifts_open"] == 2
    approve_via_inbox(short, m.manager, requester=m.cashier)
    short.action_confirm_closed()
    assert m04ctl.kpis(m.denv)["shifts_open"] - k0["shifts_open"] == 1
    # another company's reader sees none of it
    assert m04ctl.kpis(m.oenv)["shifts_open"] == 0


def test_counter_sales_mtd_counts_confirmed_sales_only(b4):
    m = b4
    k0 = m04ctl.kpis(m.denv)
    s = m.shift()
    kept = m.sale(s)
    kept.action_confirm()
    m.sale(s)  # draft
    refunded = m.sale(s)
    refunded.action_confirm()
    refunded.action_request_refund(reason="duplicate")
    approve_via_inbox(refunded, m.manager, requester=m.cashier)
    assert refunded.state == "refunded"
    k1 = m04ctl.kpis(m.denv)
    assert k1["counter_sales_mtd"] - k0["counter_sales_mtd"] == 1
    assert round(k1["counter_sales_mtd_bdt"] - k0["counter_sales_mtd_bdt"], 2) == kept.total


def test_the_wait_is_issue_to_call(b4):
    m = b4
    tok = m.token()
    tok.sudo()._guarded().write(
        {
            "issued_at": _ago(minutes=30),
            "called_at": _ago(minutes=20),
            "served_at": _ago(minutes=5),
            "state": "completed",
        }
    )
    assert round(m04ctl._wait_minutes(tok), 1) == 10.0
    today = str(m04ctl._today(m.denv))
    report = m04ctl._wait_distribution_report(m.denv, date_from=today, date_to=today)
    assert "issued -> token called" in report["notes"][0]
    buckets = {r["bucket"]: r["tokens"] for r in report["rows"]}
    assert buckets["5–15 min"] >= 1
    # a period that ended yesterday holds no token issued today
    yesterday = str(m04ctl._today(m.denv) - dt.timedelta(days=1))
    report = m04ctl._wait_distribution_report(m.denv, date_from=yesterday, date_to=yesterday)
    old = m.env["fix.token.queue"].search_count(
        [
            ("called_at", "!=", False),
            (
                "issued_at",
                ">=",
                m04ctl._utc_start(m.denv, m04ctl._today(m.denv) - dt.timedelta(days=1)),
            ),
            ("issued_at", "<", m04ctl._utc_start(m.denv, m04ctl._today(m.denv))),
        ]
    )
    assert sum(r["tokens"] for r in report["rows"]) <= old


def test_today_is_the_dhaka_day(b4):
    m = b4
    day = dt.date(2026, 11, 20)
    # Dhaka midnight is 18:00 UTC the day before
    assert m04ctl._utc_start(m.denv, day) == dt.datetime(2026, 11, 19, 18, 0)
    no_tz = (
        m.env["res.users"]
        .with_context(no_reset_password=True)
        .create({"name": "B4 no tz", "login": "b4.notz.%d@b4.test" % m.device.id, "tz": False})
    )
    user_env = m.env(user=no_tz.id, context={})
    assert m04ctl._tz(user_env).zone == DHAKA
    assert rc._tz_name(user_env) == DHAKA
    assert rc._local_midnight(user_env, day) == dt.datetime(2026, 11, 19, 18, 0)


# ============================================================== M04 packs


def test_sales_by_category_is_confirmed_dated_and_fenced(b4):
    m = b4
    categ = m.env["product.category"].create({"name": "B4 Accessories %d" % m.device.id})
    m.product.categ_id = categ
    s = m.shift()
    for _i in range(2):
        m.sale(s).action_confirm()
    m.sale(s)  # a draft never counts
    today = str(m04ctl._today(m.denv))
    rows = m04ctl._sales_category_report(m.denv, date_from=today, date_to=today)["rows"]
    row = next(r for r in rows if r["category"] == categ.display_name)
    assert (row["count"], row["quantity"], row["total"]) == (2, 2.0, 2000.0)
    tomorrow = str(m04ctl._today(m.denv) + dt.timedelta(days=1))
    rows = m04ctl._sales_category_report(m.denv, date_from=tomorrow)["rows"]
    assert not [r for r in rows if r["category"] == categ.display_name]
    rows = m04ctl._sales_category_report(m.oenv)["rows"]
    assert not [r for r in rows if r["category"] == categ.display_name]


def test_variance_register_and_daily_cash_respect_period_and_company(b4):
    m = b4
    s = m.shift()
    m.count(s, d1000=4)
    approve_via_inbox(s, m.manager, requester=m.cashier)
    s.action_confirm_closed()
    today = str(s.shift_date)
    reg = m04ctl._variance_register_report(m.denv, date_from=today, date_to=today)
    mine = [r for r in reg["rows"] if r["branch"] == m.branch.name]
    assert mine and mine[0]["shortage"] == -1000.0 and mine[0]["overage"] == 0.0
    assert mine[0]["approved_by"] == m.manager.name
    cash = m04ctl._daily_cash_report(m.denv, date_from=today, date_to=today)
    assert [r for r in cash["rows"] if r["branch"] == m.branch.name]
    assert not [
        r for r in m04ctl._variance_register_report(m.oenv)["rows"] if r["branch"] == m.branch.name
    ]
    later = str(s.shift_date + dt.timedelta(days=1))
    assert not [
        r
        for r in m04ctl._daily_cash_report(m.denv, date_from=later)["rows"]
        if r["branch"] == m.branch.name
    ]


def test_uncollected_ageing_lists_ready_orders_aged_from_ready_at(b4):
    m = b4
    ready = _order(m, ready_at=_ago(days=9), write_date=_ago(days=1))
    delivered = _order(m, state="delivered", ready_at=_ago(days=30))
    rows = m04ctl._uncollected_ageing_report(m.denv)["rows"]
    names = {r["order"]: r for r in rows}
    assert delivered.name not in names
    assert names[ready.name]["days"] in (8, 9, 10)


# ============================================================== role center


def _ctx(m, env=None, branch=None):
    env = env or m.denv
    ctx = rc.P03RoleCenterApiController._context(env, env.user, None, rc._local_today(env))
    if branch:
        ctx["branch_domain"] = [("branch_id", "=", branch.id)]
    return ctx


def test_role_center_cues_are_company_fenced(b4):
    m = b4
    s = m.shift()
    assert rc._count(m.denv, "fix.cash.shift", [("id", "=", s.id)]) == 1
    assert rc._count(m.oenv, "fix.cash.shift", [("id", "=", s.id)]) == 0
    assert rc._kpi_cash_shifts_open(m.oenv, _ctx(m, m.oenv)) == 0


def test_revenue_mtd_is_invoiced_taxable_value(b4):
    m = b4
    ctx = _ctx(m, branch=m.branch)
    before = rc._kpi_revenue_mtd(m.denv, ctx)
    Invoice = m.env["fix.ar.invoice"].sudo()

    def invoice(state, taxable, vat, branch=None):
        inv = Invoice.create(
            {
                "operating_unit_id": m.ou.id,
                "customer_id": m.customer.id,
                "source_model": "manual",
                "source_id": 900000000 + next(m.seq),
                "branch_id": (branch or m.branch).id,
                "invoice_date": rc._local_today(m.denv),
            }
        )
        m.env.flush_all()
        m.env.cr.execute(
            "UPDATE fix_ar_invoice SET state = %s, taxable_amount = %s, vat_amount = %s, "
            "total_payable = %s WHERE id = %s",
            [state, taxable, vat, taxable + vat, inv.id],
        )
        inv.invalidate_recordset()
        return inv

    invoice("issued", 1000.0, 150.0)
    invoice("paid", 200.0, 30.0)
    invoice("draft", 5000.0, 750.0)  # not invoiced
    invoice("issued", 7000.0, 0.0, branch=m.branch2)  # another branch
    assert round(rc._kpi_revenue_mtd(m.denv, ctx) - before, 2) == 1200.0
    assert rc._kpi_revenue_mtd(m.oenv, _ctx(m, m.oenv, branch=m.branch)) == 0.0


def test_first_time_fix_ignores_undecided_checklists(b4):
    m = b4
    Checklist = m.env["fix.qc.checklist"].sudo()

    def checklist(state):
        rec = Checklist.create({"order_id": _order(m, state="qc_pending").id})
        m.env.flush_all()
        m.env.cr.execute("UPDATE fix_qc_checklist SET state = %s WHERE id = %s", [state, rec.id])
        return rec

    checklist("passed")
    checklist("failed")
    m.env.invalidate_all()
    ctx = _ctx(m)
    rate = rc._kpi_first_time_fix(m.denv, ctx)
    passed = rc._count(m.denv, "fix.qc.checklist", [("state", "=", "passed")])
    decided = rc._count(m.denv, "fix.qc.checklist", [("state", "in", ["passed", "failed"])])
    assert rate == round(100.0 * passed / decided, 1)
    checklist("pending")
    checklist("in_progress")
    m.env.invalidate_all()
    assert rc._kpi_first_time_fix(m.denv, ctx) == rate


def test_delivered_today_reads_delivered_at_at_the_readers_branch(b4):
    m = b4
    ctx = _ctx(m, branch=m.branch)
    before = rc._kpi_delivered_today(m.denv, ctx)
    _order(m, state="delivered", delivered_at=_ago(minutes=5))
    _order(m, state="delivered", delivered_at=_ago(days=3), write_date=_ago(minutes=1))
    _order(m, state="delivered", delivered_at=_ago(minutes=5), branch=m.branch2)
    assert rc._kpi_delivered_today(m.denv, ctx) - before == 1


def test_order_cues_follow_the_readers_branch(b4):
    m = b4
    here, there = _ctx(m, branch=m.branch), _ctx(m, branch=m.branch2)
    h0, t0 = rc._kpi_in_repair(m.denv, here), rc._kpi_in_repair(m.denv, there)
    a0 = rc._kpi_awaiting_approval(m.denv, here)
    o0 = rc._kpi_open_orders(m.denv, here)
    _order(m, state="in_repair")
    _order(m, state="awaiting_approval")
    assert rc._kpi_in_repair(m.denv, here) - h0 == 1
    assert rc._kpi_in_repair(m.denv, there) == t0
    assert rc._kpi_awaiting_approval(m.denv, here) - a0 == 1
    assert rc._kpi_open_orders(m.denv, here) - o0 == 2


# ============================================================== documents


def _html(env, report, records):
    html, _kind = env["ir.actions.report"]._render_qweb_html(report, records.ids)
    return html.decode() if isinstance(html, bytes) else html


def _print_url(env, model, record_id, variant=None):
    with mock.patch.object(docs_api, "request", SimpleNamespace(env=env)):
        return docs_api.P03CommercialDocs().doc_print_url(
            model=model, record_id=record_id, variant=variant
        )["url"]


def test_counter_receipt_prints_the_statutory_mushak_or_says_it_is_pending(b4):
    m = b4
    s = m.shift()
    sale = m.sale(s)
    with _refused(m.env, UserError, "not confirmed"):
        sale.action_print_receipt()
    sale.action_confirm()
    html = _html(m.env, "cd_p03_portal.report_a02_counter_receipt", sale)
    assert sale.name in html and m.env.company.name in html and m.product.name in html
    assert "1,000.00" in html
    # the counter's internal reference is never printed as the NBR number
    assert sale.mushak_63_ref not in html
    posted = "mushak_id" in sale._fields and sale.mushak_id
    if posted:
        assert sale.mushak_id.mushak_no in html and "CASH MEMO" in html
        assert "%.2f" % sale.vat_output_amount in html.replace(",", "")
    else:
        assert "Pending: issued when the sale posts" in html
        assert "COUNTER SALE RECEIPT" in html
    # a sale the books have not taken yet: no statutory number, never the internal one
    unposted = m.sale(s)
    unposted.action_confirm()
    if "mushak_id" in unposted._fields:
        m.env.flush_all()
        m.env.cr.execute(
            "UPDATE fix_counter_sale SET mushak_id = NULL, vat_treatment_summary = NULL "
            "WHERE id = %s",
            [unposted.id],
        )
        unposted.invalidate_recordset()
    pending = _html(m.env, "cd_p03_portal.report_a02_counter_receipt", unposted)
    assert "Pending: issued when the sale posts" in pending
    assert "COUNTER SALE RECEIPT" in pending and "CASH MEMO" not in pending
    assert unposted.mushak_63_ref not in pending
    thermal = _html(m.env, "cd_p03_portal.report_a02_counter_receipt_80", sale)
    assert sale.name in thermal and "Thank you for choosing 1000FiX" in thermal
    assert sale.action_print_receipt()["print_url"].endswith(
        "cd_p03_portal.report_a02_counter_receipt/%s" % sale.id
    )
    assert _print_url(m.env, "fix.counter.sale", sale.id, "receipt").endswith(
        "report_a02_counter_receipt_80/%s" % sale.id
    )


def test_wipe_certificate_prints_and_says_when_it_is_not_verified(b4):
    m = b4
    if "fix.data.wipe.certificate" not in m.env:
        pytest.skip("cd_data_case not installed")
    request = (
        m.env["fix.data.wipe.request"]
        .sudo()
        .create(
            {
                "source": "customer",
                "serial_number": "SN-B4-WIPE",
                "confidentiality_level": "high",
                "disposition": "return_customer",
                "customer_id": m.customer.id,
                "media_description": "SSD 512 GB",
            }
        )
    )
    cert = (
        m.env["fix.data.wipe.certificate"]
        .sudo()
        .create(
            {
                "method": "nist_800_88",
                "wipe_request_id": request.id,
                "device_id": m.device.id,
                "serial_number": "SN-B4-WIPE",
                "tool_name": "B4 Wipe Tool 7.1",
                "sector_count": 1000000,
            }
        )
    )
    html = _html(m.env, "cd_p03_portal.report_a02_wipe_certificate", cert)
    # the hash is computed from the evidence (empty until a log is attached)
    if cert.verification_hash:
        assert cert.verification_hash in html
    for text in (
        "DATA SANITIZATION CERTIFICATE",
        cert.name,
        "SN-B4-WIPE",
        "B4 Wipe Tool 7.1",
        "1,000,000",
        m.customer.name,
        "NOT VERIFIED",
    ):
        assert text in html, text
    assert _print_url(m.env, "fix.data.wipe.certificate", cert.id).endswith(
        "report_a02_wipe_certificate/%s" % cert.id
    )


def test_field_service_report_prints_the_visit(b4):
    m = b4
    if "fix.field.order" not in m.env:
        pytest.skip("cd_field_service not installed")
    zone = m.env["fix.zone"].sudo().create({"name": "B4 Zone", "code": "B4Z%d" % m.device.id})
    order = _order(m, state="in_repair")
    fo = (
        m.env["fix.field.order"]
        .sudo()
        .create(
            {
                "order_id": order.id,
                "zone_id": zone.id,
                "customer_address": "House 7, Road 3, Mirpur",
                "district_name": "Dhaka",
                "work_summary": "B4 replaced the compressor relay",
            }
        )
    )
    m.env["fix.field.order.part"].sudo().create(
        {"field_order_id": fo.id, "product_id": m.product.id, "quantity": 2.0}
    )
    html = _html(m.env, "cd_p03_portal.report_a02_field_service", fo)
    for text in (
        "FIELD SERVICE REPORT",
        fo.name,
        order.name,
        m.customer.name,
        "House 7, Road 3, Mirpur",
        "B4 replaced the compressor relay",
        m.product.name,
    ):
        assert text in html, text


def test_consignment_note_prints_contents_and_custody(b4):
    m = b4
    if "fix.consignment" not in m.env:
        pytest.skip("cd_consignment not installed")
    order = _order(m, state="ready")
    cons = (
        m.env["fix.consignment"]
        .sudo()
        .create(
            {
                "scheduled_date": fields.Datetime.now(),
                "consignment_type": "branch_transfer",
                "origin_branch_id": m.branch.id,
                "dest_branch_id": m.branch2.id,
                "service_order_id": order.id,
                "outbound_seal_number": "SEAL-B4-77",
                "declared_value_bdt": 25000.0,
            }
        )
    )
    m.env["fix.custody.scan"].sudo()._guarded().create(
        {
            "consignment_id": cons.id,
            "step": "picked_up",
            "scanned_at": fields.Datetime.now(),
            "location_branch_id": m.branch.id,
        }
    )
    html = _html(m.env, "cd_p03_portal.report_a02_consignment_note", cons)
    for text in (
        "DELIVERY NOTE / WAYBILL",
        cons.name,
        order.name,
        m.branch2.name,
        "SEAL-B4-77",
        "25,000.00",
        "Picked",
    ):
        assert text in html, text


def test_workshop_job_card_prints_the_repair(b4):
    m = b4
    if "fix.workshop.job" not in m.env:
        pytest.skip("cd_workshop not installed")
    ws = (
        m.env["fix.workshop"]
        .sudo()
        .create({"name": "B4 Workshop", "name_bn": "বি৪ ওয়ার্কশপ", "code": "B4W%d" % m.device.id})
    )
    job = (
        m.env["fix.workshop.job"]
        .sudo()
        .create(
            {
                "workshop_id": ws.id,
                "fault_description": "B4 no power after liquid spill",
                "customer_id": m.customer.id,
                "device_id": m.device.id,
                "device_serial": "SN-B4-JOB",
                "diagnostic_findings": "B4 corroded PMIC rail",
                "repair_action_summary": "B4 cleaned and replaced the PMIC",
            }
        )
    )
    line = (
        m.env["fix.workshop.part.line"]
        .sudo()
        .create(
            {
                "job_id": job.id,
                "product_id": m.product.id,
                "quantity": 1.0,
                "fitted_serial_number": "PMIC-B4-1",
            }
        )
    )
    # A02 pass 2 M31-10: the card prints only the parts fitted on the bench
    # (consumed); test setup marks this one fitted
    line._guarded().write({"reservation_state": "consumed"})
    html = _html(m.env, "cd_p03_portal.report_a02_workshop_job", job)
    for text in (
        "WORKSHOP JOB CARD / REPAIR REPORT",
        job.name,
        m.customer.name,
        "SN-B4-JOB",
        "B4 no power after liquid spill",
        "B4 corroded PMIC rail",
        "B4 cleaned and replaced the PMIC",
        m.product.name,
        "PMIC-B4-1",
    ):
        assert text in html, text
    assert _print_url(m.env, "fix.workshop.job", job.id).endswith(
        "report_a02_workshop_job/%s" % job.id
    )
