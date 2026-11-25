# A02 ERP audit, pass 2 (20 Nov 2026): the M01 workspace (stream S1).
#
# - M01-01: the job card is the server's report, never the browser's
#   "Mushak 6.3" with a flat 15% VAT; print_url maps the order's documents.
# - M01-11: job sheet / job card / challan-gate pass / service report.
# - M01-16 / X5-17: the KPI row measures the right populations, uncapped.
# - X5-01: the counter payment asks the tender, with the drawer's own keys.
# - X5-19: the order record shows what it drove (read-only grids).
import itertools
import re
from datetime import timedelta
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_commercial_docs as docs
from odoo.addons.cd_p03_portal.controllers.a02 import m01

_SEQ = itertools.count(1)
SRC = Path(__file__).resolve().parents[1] / "static" / "src"
M01_JS = SRC / "a02" / "m01.js"


def _js():
    return M01_JS.read_text(encoding="utf-8")


# ========================================================= M01-01 / M01-11
def test_m01_01_the_workspace_has_no_client_side_mushak_job_card():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    js = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    assert "jobCardModalOpen" not in xml and "jobCardModalOpen" not in js
    assert "Statutory NBR Mushak 6.3 15% VAT Compliant" not in xml
    assert "PRINTABLE JOB CARD & MUSHAK 6.3" not in xml
    body = js[js.index("async openJobCardModal()") :][:600]
    assert 'docPrint("fix.service.order", rec.order_id, "jobcard")' in body


def test_m01_11_every_order_document_is_a_server_report(odoo_env):
    for variant in ("a4", "jobsheet", "jobcard", "challan", "gatepass", "service_report"):
        name = docs.SERVICE_ORDER_DOCUMENTS[variant]
        report = odoo_env["ir.actions.report"].sudo()._get_report_from_name(name)
        assert report and report.model == "fix.service.order", variant
    prints = set(re.findall(r"print: '(\w+)'", _js()))
    assert {"jobsheet", "jobcard", "challan", "service_report"} <= prints
    assert prints <= set(docs.SERVICE_ORDER_DOCUMENTS)


def test_m01_11_the_job_card_and_service_report_carry_no_vat(odoo_env):
    order = _order(odoo_env)
    Report = odoo_env["ir.actions.report"].sudo()
    for name in ("cd_service_order.report_jobcard", "cd_doc_suite.report_service_report"):
        html, _kind = Report._render_qweb_html(name, order.ids)
        text = html.decode() if isinstance(html, bytes) else html
        assert "Mushak" not in text and "VAT" not in text, name
        assert order.name in text


# ================================================================== X5-01
def test_x5_01_counter_payment_asks_the_tender_with_the_drawer_keys():
    from odoo.addons.cd_front_desk.models.fix_service_order_drawer import SETTLEMENT_TENDERS

    src = _js()
    block = src[src.index("{ id: 'settle_counter'") :]
    block = block[: block.index("] },") + 4]
    assert "kwarg: 'tender'" in block
    label = re.search(r"kwarg: 'tender', label: '([^']+)'", block).group(1)
    named = set(re.findall(r"[a-z]+", label.split(":", 1)[1])) - {"or"}
    assert named == {"cash", "bkash", "nagad", "rocket", "upay", "card"}
    assert named <= dict(SETTLEMENT_TENDERS).keys()


# ================================================================== X5-19
def test_x5_19_the_order_record_shows_its_children_read_only(odoo_env):
    src = _js()
    record = src[src.index("'M01-order': {") : src.index("'M01-types':")]
    grids = re.findall(r"\{ field: '(\w+)', tab: 'related'[^}]*readonlyGrid: true", record)
    assert set(grids) == {
        "estimate_ids",
        "fault_line_ids",
        "workshop_job_ids",
        "field_order_ids",
        "consignment_ids",
    }
    Order = odoo_env["fix.service.order"]
    for name in grids:
        assert Order._fields[name].type == "one2many"
    assert "{ id: 'related'" in record


# ============================================================= M01-16 / X5-17
def _order(env, **vals):
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if not branch:
        ou = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
            {
                "name": "A02R2 KPI OU",
                "code": "A2RKOU",
                "company_id": env.company.id,
                "partner_id": env.company.partner_id.id,
            }
        )
        entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
            {"legal_name": "A02R2 KPI Entity", "code": "A2RKE", "company_id": env.company.id}
        )
        branch = env["fix.branch"].create(
            {
                "name": "A02R2 KPI Branch",
                "code": "A2RK-BR",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )
    partner = env["res.partner"].create({"name": "A02R2 KPI customer"})
    n = next(_SEQ)
    brand = env["fix.brand"].create({"name": "A02R2KPI%d" % n, "code": "A2RK%d" % n})
    model = env["fix.device.model"].create({"name": "A02R2 KPI model %d" % n, "brand_id": brand.id})
    dev = env["fix.device"].create({"device_model_id": model.id, "owner_id": partner.id})
    base = {
        "device_id": dev.id,
        "customer_id": partner.id,
        "branch_id": branch.id,
        "fault_description": "kpi",
    }
    order = env["fix.service.order"].create(base)
    state = vals.pop("state", None)
    if state:  # a legacy row in that state: the transition map is not under test
        env.cr.execute("UPDATE fix_service_order SET state=%s WHERE id=%s", (state, order.id))
        order.invalidate_recordset()
    order._guarded().write(vals)
    return order


def test_m01_16_rework_rate_is_over_the_period_deliveries(odoo_env):
    env = odoo_env
    base = m01.kpis(env)
    now = fields.Datetime.now()
    for _i in range(3):
        _order(env, state="delivered", delivered_at=now - timedelta(days=1))
    _order(env, state="delivered", delivered_at=now - timedelta(days=1), is_rework=True)
    # an open rework does not move a rate of DELIVERED work
    _order(env, state="in_repair", is_rework=True)
    after = m01.kpis(env)
    Order = env["fix.service.order"].sudo()
    since = now - timedelta(days=30)
    dom = [
        ("company_id", "in", env.companies.ids),
        ("state", "in", ("delivered", "closed")),
        ("delivered_at", ">=", since),
    ]
    expected = round(
        100.0 * Order.search_count([*dom, ("is_rework", "=", True)]) / Order.search_count(dom), 1
    )
    assert after["rework_rate"] == expected
    assert after["delivered_not_closed"] == base["delivered_not_closed"] + 4


def test_m01_16_kpis_read_without_a_cap(odoo_env):
    """X5-17: TAT read the newest 500 resolved orders (limit=500)."""
    from odoo import models

    original = models.BaseModel.search
    capped = []

    def spy(self, domain, offset=0, limit=None, order=None):
        if self._name == "fix.service.order" and limit:
            capped.append(limit)
        return original(self, domain, offset=offset, limit=limit, order=order)

    with mock.patch.object(models.BaseModel, "search", spy):
        m01.kpis(odoo_env)
    assert not capped, "a KPI read a capped subset of the orders"


def test_m01_16_at_risk_reads_the_clock_warning_point(odoo_env):
    env = odoo_env
    Instance = env.get("fix.sla.kpi.instance")
    if Instance is None:
        pytest.skip("no SLA instances")
    order = _order(env, state="in_repair")
    now = fields.Datetime.now()
    before = m01.kpis(env)["sla_at_risk"]
    inst = Instance.sudo().search(
        [
            ("res_model", "=", order._name),
            ("res_id", "=", order.id),
            ("kpi_code", "=", "resolution"),
        ],
        limit=1,
    )
    if not inst:
        policy = env["fix.sla.policy"].sudo().search([], limit=1)
        if not policy:
            pytest.skip("no SLA policy")
        inst = Instance.sudo().create(
            {
                "res_model": order._name,
                "res_id": order.id,
                "policy_id": policy.id,
                "kpi_code": "resolution",
                "target_hours": 10,
                "started_at": now - timedelta(hours=9),
                "target_at": now + timedelta(hours=1),
                "warn_at": now - timedelta(hours=1),
            }
        )
    else:
        inst._guarded().write(
            {"warn_at": now - timedelta(hours=1), "target_at": now + timedelta(hours=1)}
        )
    # past its warning point, not yet breached: at risk
    assert m01.kpis(env)["sla_at_risk"] == before + 1
