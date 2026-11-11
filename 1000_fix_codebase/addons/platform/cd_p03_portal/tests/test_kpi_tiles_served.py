# P03 module-home KPI tiles: every tile is served or declared sourceless.
#
# A headless walk of the real estate found 74 module-home tiles showing "—"
# under the caption "wired with module phase": a promise of a value that no
# phase was going to deliver. Each tile now falls into one of these classes:
#
#   * served     — its `m` key is IN the payload of the module's KPI route
#                  (the route the workspace's openModule() picks). Counts and
#                  sums are numbers even before the first row (0). Ratios,
#                  percentages and averages are None exactly while their
#                  denominator is empty — "0% CSAT" with no surveys would be a
#                  false statement — and the tile then reads "No activity yet";
#   * sourceless — the fragment marks it `src: false` because the estate holds
#                  no data to compute it (no ML ground truth, no latency log...).
#                  The tile shows "—" with the caption "No data source".
#
# The registry is evaluated with node (the real ES-module fragments), and the
# route map is read from p03_workspace.js, so neither can drift from the test.
from __future__ import annotations

import contextlib
import datetime
import inspect
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest
from odoo import fields, http
from odoo.addons.cd_p03_portal.controllers.a02 import m31
from odoo.addons.cd_p03_portal.controllers.a03 import m27, m32, m34, m35
from odoo.addons.cd_p03_portal.controllers.a04 import m09, m11, m36, m37, m38, m39
from odoo.addons.cd_p03_portal.controllers.a07 import m48
from odoo.addons.cd_p03_portal.controllers.a08 import m19
from odoo.addons.cd_p03_portal.controllers.a12 import m28

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
FINANCE_ROUTE = "/p03/finance/kpis"
NUM = (int, float)


# --------------------------------------------------------------------------- denominators
# Each ratio / average below is paired with a predicate saying whether its
# denominator holds any row on the database under test, read independently
# of the endpoint's own expression. `None` as the predicate marks a count or
# a sum: it must always be a value.


def _fenced(env, model, domain):
    return env[model].sudo().search_count([("company_id", "in", env.companies.ids), *domain])


def _income_mtd(env):
    lines = env["account.move.line"].search(
        [
            ("parent_state", "=", "posted"),
            ("date", ">=", m19._month_start()),
            ("company_id", "=", env.company.id),
            ("account_id.account_type", "=", "income"),
        ]
    )
    return -sum(lines.mapped("balance")) > 0.005


def _ar(env, domain):
    return env["fix.ar.invoice"].search(domain)


def _quote_cycles(env):
    stamps = {}
    for review in env["fix.quote.review"].sudo().search([("reviewed_at", "!=", False)]):
        stamps.setdefault(review.quotation_id.id, []).append(review.reviewed_at)
    return any(len(v) >= 2 for v in stamps.values())


def _fpa(env):
    from odoo.addons.cd_fpa.models.fix_fpa_engine import fy_window

    today = fields.Date.context_today(env.user)
    d_from, _fy_to = fy_window(today)
    return env["fix.fpa.engine"], d_from, today


def _sla_finished(env):
    if "fix.sla.kpi.instance" not in env:
        return False
    return bool(
        env["fix.sla.kpi.instance"]
        .sudo()
        .search_count(
            [
                ("res_model", "=", "fix.complaint"),
                ("kpi_code", "=", "resolution"),
                ("state", "in", ("succeeded", "breached")),
            ]
        )
    )


def _paid_90d(env):
    since = datetime.date.today() - datetime.timedelta(days=90)
    paid = _ar(env, [("state", "in", ("paid", "credited")), ("paid_date", ">=", since)])
    return bool(paid.filtered(lambda i: i.paid_date and i.invoice_date))


WIRED = {
    "M03": {
        "on_time_delivery": (
            NUM,
            lambda e: _fenced(e, "fix.consignment", [("state", "=", "delivered")]),
        ),
        "avg_round_trip": (
            NUM,
            lambda e: _fenced(e, "fix.consignment", [("state", "=", "delivered")]),
        ),
    },
    "M04": {
        "avg_wait_min": (
            NUM,
            lambda e: _fenced(
                e,
                "fix.token.queue",
                [
                    ("state", "=", "completed"),
                    ("served_at", "!=", False),
                    ("called_at", "!=", False),
                ],
            ),
        ),
    },
    "M05": {
        "remote_resolution": (
            NUM,
            lambda e: _fenced(e, "fix.msp.alert", [("state", "in", ("ticketed", "resolved"))]),
        ),
        "patch_compliance": (NUM, lambda e: _fenced(e, "fix.msp.patch.update", [])),
    },
    "M06": {
        "recovery_success": (
            NUM,
            lambda e: _fenced(
                e, "fix.data.recovery.case", [("state", "in", ("recovered", "unrecoverable"))]
            ),
        ),
        "eval_turnaround": (
            NUM,
            lambda e: e["fix.data.evaluation"].sudo().search_count([("evaluated_at", "!=", False)]),
        ),
    },
    "M08": {
        "renewal_rate": (
            NUM,
            lambda e: e["fix.contract.renewal"]
            .sudo()
            .search_count([("state", "in", ("won", "lost"))]),
        ),
        "entitlement_utilisation": (
            NUM,
            lambda e: sum(
                e["fix.contract.entitlement"].sudo().search([]).mapped("quantity_included")
            ),
        ),
    },
    "M09": {
        "first_submission_approval": (
            NUM,
            lambda e: m09._claims(e).filtered(lambda c: c.state in m09.DECIDED),
        ),
        "reimbursement_days": (
            NUM,
            lambda e: m09._claims(e).filtered(lambda c: c.submitted_at and c.decided_at),
        ),
        "claims_under_72h": (NUM, lambda e: m09._claims(e)),
    },
    "M10": {
        "breakage": (
            NUM,
            lambda e: sum(
                e["fix.loyalty.account"].sudo().search([]).mapped("lifetime_points_earned")
            ),
        ),
    },
    "M11": {
        "realised_margin": (
            NUM,
            lambda e: any(m11._cost_of(c) is not None and c.unit_price for c in m11._cards(e)),
        ),
        "discount_leaks_mtd": (NUM, None),
    },
    "M12": {
        "job_fill_rate": (
            NUM,
            lambda e: sum(e["fix.seller.score"].search([]).mapped("quotes_decided")),
        ),
    },
    "M19": {
        "revenue_mtd": (NUM, None),
        "gross_margin_mtd": (str, _income_mtd),
    },
    "M20": {
        "dso": (NUM, _paid_90d),
        "auto_generated_pct": (NUM, lambda e: _ar(e, [("state", "!=", "draft")])),
        "within_1h_pct": (
            NUM,
            lambda e: _ar(e, [("state", "!=", "draft")]).filtered(lambda i: i.generation_seconds),
        ),
    },
    "M23": {
        "first_pass_qc": (
            NUM,
            lambda e: e["fix.qc.checklist"].search_count([("state", "in", ("passed", "failed"))]),
        ),
    },
    "M26": {
        "override_rate": (
            NUM,
            lambda e: e["fix.ml.inference.run"].search_count([("suggested_value", "!=", False)]),
        ),
    },
    "M27": {
        "service_level_pct": (
            NUM,
            lambda e: m27._all(e).filtered(lambda c: c.queued_at and c.answered_at),
        ),
        "avg_handle_time_sec": (
            NUM,
            lambda e: m27._all(e).filtered(lambda c: c.answered_at and c.ended_at),
        ),
        "fcr_rate": (NUM, lambda e: m27._all(e).filtered(lambda c: c.queued_at and c.answered_at)),
        "abandonment_rate": (NUM, lambda e: m27._all(e)),
        "active_calls": (NUM, None),
        "queued_contacts": (NUM, None),
    },
    "M28": {
        "api_p95": (
            NUM,
            lambda e: m28._measured(e, "api")[0].filtered(lambda ln: ln.latency_ms),
        ),
    },
    "M31": {
        "first_pass_yield": (
            NUM,
            lambda e: m31._jobs(e).search_count(
                [("company_id", "in", e.companies.ids), ("state", "=", "delivered")]
            ),
        ),
        "avg_bench_days": (
            NUM,
            lambda e: m31._jobs(e).search_count(
                [
                    ("company_id", "in", e.companies.ids),
                    ("state", "=", "delivered"),
                    ("completed_at", "!=", False),
                ]
            ),
        ),
        "parts_fitment": (NUM, lambda e: e["fix.workshop.part.line"].sudo().search_count([])),
    },
    "M32": {
        "faq_automation": (NUM, lambda e: m32._convs(e)),
        "ai_fcr": (NUM, lambda e: m32._convs(e)),
        "bengali_sessions": (
            NUM,
            lambda e: e["fix.conversation.turn"].sudo().search_count([]),
        ),
        "avg_turns": (NUM, lambda e: m32._convs(e)),
    },
    "M34": {
        "csat": (NUM, lambda e: m34._responses(e)),
        "nps": (NUM, lambda e: m34._responses(e)),
        "complaint_sla_met": (NUM, _sla_finished),
        "survey_response": (NUM, lambda e: e["fix.survey"].sudo().search_count([])),
    },
    "M35": {
        "cac": (
            NUM,
            lambda e: m35._responses(e).filtered(lambda r: r.conversion_status == "converted"),
        ),
        "attributed_revenue": (NUM, None),
        "open_rate": (NUM, lambda e: sum(m35._campaigns(e).mapped("recipient_count"))),
        "consent_safe_reach": (NUM, None),
    },
    "M36": {
        "conversion": (NUM, lambda e: m36._quotes(e)),
        "avg_turnaround": (NUM, _quote_cycles),
    },
    "M37": {
        "rbom_coverage": (
            NUM,
            lambda e: m37._items(e).filtered(lambda i: i.item_type == "service"),
        ),
    },
    "M38": {
        "conversion": (NUM, lambda e: m38._carts(e)),
        "cart_abandon": (NUM, lambda e: m38._carts(e)),
        "bkash_share": (NUM, lambda e: m38._orders(e)),
        "rma_rate": (NUM, lambda e: m38._orders(e)),
    },
    "M39": {
        "churn_logo": (NUM, lambda e: m39._subs(e)),
    },
    "M48": {
        "prediction_precision": (
            NUM,
            lambda e: m48._visible(e, "fix.predictive.maintenance").filtered(
                lambda p: p.outcome in ("confirmed", "false_alarm")
            ),
        ),
        "retention_compression": (
            NUM,
            lambda e: m48._visible(e, "fix.iot.downsample", [("state", "=", "active")]).filtered(
                lambda p: p.raw_points_rolled > 0
            ),
        ),
    },
    "M54": {
        # a variance needs a plan to vary from: None with no approved line
        "fpa_budget_variance_fytd": (
            NUM,
            lambda e: (lambda eng, a, b: eng.approved_budget_lines(a, b))(*_fpa(e)),
        ),
        "fpa_branch_top": (str, None),
        "fpa_negative_branches": (NUM, None),
        "fpa_job_costing_coverage": (
            str,
            lambda e: (lambda eng, a, b: eng.job_costs(a, b))(*_fpa(e)),
        ),
    },
    "M58": {
        "time_to_fill": (
            NUM,
            lambda e: e["fix.candidate"].search_count(
                [("state", "=", "hired"), ("requisition_id", "!=", False)]
            ),
        ),
    },
}

# No model in the estate records these; the tiles say so (src: false).
NO_SOURCE = {
    "M03": {"rider_shifts_open"},  # no rider-shift model
    "M11": {"brand_reimb_rates"},  # no brand reimbursement-rate ledger
    "M12": {"marketplace_share", "seller_nps"},  # no cross-channel GMV; no seller survey
    "M24": {"search_p95"},  # no search latency log
    "M25": {"load_time_p95", "spreadsheets_retired"},  # no dashboard timing; no register
    "M26": {"auto_assign_rate", "demand_mape", "fault_f1", "churn_auc"},  # no ground truth
    "M32": {"handoff_precision"},  # no labelled should-have-handed-off truth
    "M36": {"declined_conversion"},  # diagnostic fee not linked to quotes
    "M39": {"nrr"},  # no dated MRR history (churn has no date)
}


# --------------------------------------------------------------------------- registry


@pytest.fixture(scope="module")
def modules(tmp_path_factory):
    """Every P03 module's area and KPI tiles, from the real ES-module registry."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_registry_kpis")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    probe = tmp / "probe.mjs"
    probe.write_text(
        "import * as M from './meta.mjs';\n"
        "const out = {};\n"
        "for (const [mid, mod] of Object.entries(M.P03_MODULES)) {\n"
        "  out[mid] = {area: mod.area, kpis: mod.kpis || []};\n"
        "}\n"
        "console.log(JSON.stringify(out));\n",
        "utf-8",
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)],
        capture_output=True,
        encoding="utf-8",  # Bengali labels: never the Windows ANSI codepage
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)


def _route_maps():
    """openModule()'s KPI route choice, read from p03_workspace.js."""
    js = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    start = js.index("openModule(mid)")
    body = js[start : js.index("openFreg(", start)]
    by_mid = dict(re.findall(r'mid === "(M\d\d)" \? "(/p03/[\w/]+)"', body))
    by_area = dict(re.findall(r'mod\.area === "(A\d\d)" \? "(/p03/[\w/]+)"', body))
    assert f': "{FINANCE_ROUTE}"' in body, "openModule() lost its default KPI route"
    return by_mid, by_area


def _route_for(mid, area):
    by_mid, by_area = _route_maps()
    return by_mid.get(mid) or by_area.get(area) or FINANCE_ROUTE


# --------------------------------------------------------------------------- endpoints


class _FakeRequest:
    def __init__(self, env):
        self.env = env


def _controller_modules():
    import odoo.addons.cd_p03_portal.controllers  # noqa: F401 - loads every controller

    prefix = "odoo.addons.cd_p03_portal.controllers"
    return [m for n, m in list(sys.modules.items()) if n.startswith(prefix) and m is not None]


def _endpoint(path):
    """The controller method that serves `path` (its @http.route)."""
    for module in _controller_modules():
        for _name, cls in inspect.getmembers(module, inspect.isclass):
            if not issubclass(cls, http.Controller) or cls.__module__ != module.__name__:
                continue
            for attr, fn in vars(cls).items():
                routing = getattr(fn, "original_routing", None)
                if routing and path in (routing.get("routes") or []):
                    return getattr(cls(), attr)
    raise AssertionError(f"no controller serves {path}")


@contextlib.contextmanager
def _as_request(env):
    with contextlib.ExitStack() as stack:
        for module in _controller_modules():
            if hasattr(module, "request"):
                stack.enter_context(mock.patch.object(module, "request", _FakeRequest(env)))
        yield


def _served(env, mid, area):
    """The module's payload as the browser receives it: through a JSON round
    trip, so a key the route drops (instead of sending null) is caught."""
    with _as_request(env):
        res = _endpoint(_route_for(mid, area))(module=mid)
    assert isinstance(res, dict), (mid, res)
    res = json.loads(json.dumps(res, default=str))
    return res.get(mid) or {}


# --------------------------------------------------------------------------- tests


def test_route_map_reads_from_the_workspace():
    by_mid, by_area = _route_maps()
    assert by_mid["M28"] == "/p03/platform/kpis"
    assert by_mid["M26"] == "/p03/ml/kpis"
    assert by_mid["M06"] == "/p03/data/kpis"
    assert by_area["A10"] == "/p03/grc/kpis"
    assert _route_for("M27", "A03") == FINANCE_ROUTE


@pytest.mark.parametrize("mid", sorted(WIRED))
def test_wired_metrics_are_served_and_none_only_without_a_denominator(modules, odoo_env, mid):
    """Each wired key is IN its route's payload. A count or sum is always a
    value; a ratio / average is None exactly when its denominator is empty on
    this database, and a real value otherwise."""
    served = _served(odoo_env, mid, modules[mid]["area"])
    tiles = {k.get("m"): k for k in modules[mid]["kpis"]}
    for key, (kind, denominator) in WIRED[mid].items():
        assert key in tiles, f"{mid}: no tile names metric {key!r}"
        assert tiles[key].get("src") is not False, f"{mid}.{key} is wired but marked sourceless"
        assert key in served, f"{mid}: the route's payload does not carry {key!r}"
        value = served[key]
        if denominator is not None and not denominator(odoo_env):
            assert value is None, f"{mid}.{key} = {value!r} with an empty denominator"
            continue
        assert value is not None, f"{mid}.{key} is None but its denominator has rows"
        assert isinstance(value, kind) and not isinstance(value, bool), f"{mid}.{key} = {value!r}"


def test_a_ratio_is_none_until_its_denominator_has_rows_then_a_real_number(modules, odoo_env):
    """M06 Recovery Success (recovered / decided cases, fenced to the caller's
    companies): None in a company with no decided case, then the real share
    once recovered and unrecoverable cases exist — a genuine figure, not 0."""
    company = odoo_env["res.company"].create({"name": "KPI tile probe co"})
    env = odoo_env(context=dict(odoo_env.context, allowed_company_ids=[company.id]))
    assert env.companies == company
    area = modules["M06"]["area"]

    empty = _served(env, "M06", area)
    assert "recovery_success" in empty and empty["recovery_success"] is None
    # counts in the same payload still read 0, not None
    assert empty["active_cases"] == 0

    Case = env["fix.data.recovery.case"]
    customer = env["res.partner"].create({"name": "KPI tile probe customer"})
    states = ("recovered", "recovered", "recovered", "unrecoverable")
    for state in states:
        case = Case.create({"customer_id": customer.id, "company_id": company.id})
        case.write({"state": state})  # trusted (superuser) write plants the outcome
    seeded = _served(env, "M06", area)
    assert seeded["recovery_success"] == 75.0


def test_sourceless_tiles_are_marked(modules):
    for mid, keys in NO_SOURCE.items():
        tiles = {k.get("m"): k for k in modules[mid]["kpis"]}
        for key in keys:
            assert key in tiles, f"{mid}: no tile names {key!r}"
            assert tiles[key].get("src") is False, f"{mid}.{key} must be marked src: false"
    marked = {
        (mid, k.get("m"))
        for mid, mod in modules.items()
        for k in mod["kpis"]
        if k.get("src") is False
    }
    declared = {(mid, key) for mid, keys in NO_SOURCE.items() for key in keys}
    assert marked == declared, "src:false tiles drifted from the declared no-source list"


def test_every_module_tile_is_served_or_declared_sourceless(modules, odoo_env):
    """Every KPI tile in every module: an `m` key present in the module's
    route payload (null included: "No activity yet"), or an explicit
    `src: false`. A sourceless key must not hold a value (a real metric hidden
    behind "No data source" is the opposite error)."""
    problems = []
    for mid, mod in sorted(modules.items()):
        kpis = mod["kpis"]
        if not kpis:
            continue
        if not any(k.get("m") for k in kpis):
            problems.append(f"{mid}: tiles with no metric keys at all")
            continue
        served = _served(odoo_env, mid, mod["area"])
        for kpi in kpis:
            key = kpi.get("m")
            if kpi.get("src") is False:
                if served.get(key) is not None:
                    problems.append(f"{mid}.{key}: marked sourceless but served {served[key]!r}")
                continue
            if not key:
                problems.append(f"{mid} tile {kpi['l']!r}: no metric key and no src:false")
            elif key not in served:
                problems.append(f"{mid}.{key}: tile {kpi['l']!r} names a metric not served")
    assert not problems, "\n".join(problems)


def test_tile_has_four_honest_states():
    xml = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
    i18n = (SRC / "p03_i18n.js").read_text(encoding="utf-8")
    js = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    for text in (xml, i18n):
        assert "wired with module phase" not in text
        assert "read_group phase" not in text
    assert "kpiCaption(kpi)" in xml and "kpiTitle(kpi)" in xml
    for en, bn in (
        ("No data source", "কোনো ডেটা উৎস নেই"),
        ("No activity yet", "এখনো কোনো কার্যক্রম নেই"),
        ("No value served", None),
        ("Live from Odoo", None),
    ):
        assert f'"{en}":' in i18n, en
        if bn:
            assert f'"{en}": "{bn}"' in i18n
    body = js[js.index("kpiState(kpi) {") : js.index("kpiCaption(kpi) {")]
    # a key present with null is "no activity", absent is "no value served"
    assert "hasOwnProperty.call(p, kpi.m)" in body
    assert '"noactivity"' in body and '"unserved"' in body and '"nosource"' in body
    assert "kpi.src === false" in js
