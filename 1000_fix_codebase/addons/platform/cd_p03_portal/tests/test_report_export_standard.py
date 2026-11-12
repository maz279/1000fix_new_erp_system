# Every built-in report of M01-M67 exports and can be emailed (13 Nov 2026).
#
# The user found some module reports offered Excel/PDF and email and many did
# not. The sweep over all 67 modules found 396 report screens: 384 generic
# report screens had CSV/Excel/PDF but no Email; the M19 Trial Balance, P&L,
# Balance Sheet, Cash Flow, Consolidated P&L, Dimensions and Close Checklist
# and the M20 AR Aging and Revenue Leakage had no export at all; the M20
# Customer Statement had a browser-built CSV only. The email route's report
# mode re-ran the pack without the user's period or filters and dropped its
# totals, and list exports ignored the screen's scope.
#
# The standard: ONE action bar (cd_p03_portal.ReportActions: CSV, Excel, PDF,
# Email) on every report screen, all reading the engine's `reportTarget`, and
# ONE server path (controllers/report_delivery.py) for download, email and the
# scheduled subscriptions.
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "static" / "src"
IMPORT = re.compile(r'from\s+"(\./a\d\d/\w+)"')
MODULES = ["M%02d" % n for n in range(1, 68)]

# the screen kinds that ARE a report: each must carry the bar, and the
# engine must say which pack it is
REPORT_KINDS = (
    "table_report",
    "statement",
    "dimensions",
    "close",
    "coa",
    "ar_aging",
    "ar_leakage",
    "ar_statements",
)

PROBE = """
import * as M from './meta.mjs';
const { P03_MODULES, P03_DATA_SCREENS, P03_REPORT_ROUTES } = M;
const t = (s) => s;
const target = function %(target)s;
function resolve(sid) {
  const cfg = P03_DATA_SCREENS[sid];
  if (!cfg) return { sid, kind: null, target: null };
  const gl = {
    kind: cfg.kind, cfg, report: cfg.report || null,
    reportCfg: cfg.kind === 'table_report' ? cfg : null, reportFilters: {},
    stmtFrom: '2026-07-01', stmtTo: '2026-11-30', selectedCloseId: null,
    stmtCustomer: 7, arFrom: '2026-11-01', arTo: '2026-11-30',
    data: { title: 'T', statement: {} }, title: sid,
  };
  const self = { state: { gl }, glTitle: sid, t };
  return { sid, kind: cfg.kind, cfgModule: cfg.module || null, target: target.call(self) };
}
const out = {};
for (const [mid, mod] of Object.entries(P03_MODULES)) {
  const chips = (mod.reports || []).map((rep) =>
    Object.assign({ rep }, resolve(P03_REPORT_ROUTES[mid + ':' + rep])));
  const badged = [];
  for (const g of mod.groups) for (const s of g.screens) {
    if (s.t === 'r') badged.push(resolve(s.id));
  }
  out[mid] = { chips, badged };
}
console.log(JSON.stringify(out));
"""


def _getter(engine, name):
    m = re.search(r"^    get %s\(\) (\{\n.*?\n    \})\n" % name, engine, re.S | re.M)
    assert m, "p03_workspace.js no longer defines get %s()" % name
    return "() " + m.group(1)


@pytest.fixture(scope="module")
def estate(tmp_path_factory):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the ES-module registry")
    tmp = tmp_path_factory.mktemp("p03_report_standard")
    for area in sorted(d for d in SRC.iterdir() if re.fullmatch(r"a\d\d", d.name)):
        (tmp / area.name).mkdir()
        for js in area.glob("*.js"):
            (tmp / area.name / (js.stem + ".mjs")).write_text(
                js.read_text(encoding="utf-8"), "utf-8"
            )
    meta = (SRC / "p03_modules_meta.js").read_text(encoding="utf-8")
    (tmp / "meta.mjs").write_text(IMPORT.sub(r'from "\1.mjs"', meta), "utf-8")
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
    probe = tmp / "probe.mjs"
    # the getter becomes a plain function called with `this` = a stub engine
    probe.write_text(PROBE % {"target": _getter(engine, "reportTarget")}, "utf-8")
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary and our own probe file
        [node, str(probe)], capture_output=True, encoding="utf-8", check=True, timeout=120
    )
    return json.loads(out.stdout)


def _registry():
    from odoo.addons.cd_p03_portal.controllers import report_delivery

    return report_delivery


def test_the_estate_has_67_modules(estate):
    assert sorted(estate) == MODULES


@pytest.mark.parametrize("mid", MODULES)
def test_every_built_in_report_names_a_pack_that_exists(estate, mid):
    """Each report chip on the module page, and each screen the module badges
    as a report, opens a report screen the engine can export and email: it
    resolves to a module:report pack the server serves."""
    rd = _registry()
    bad = []
    for x in estate[mid]["chips"] + estate[mid]["badged"]:
        name = x.get("rep") or x["sid"]
        if x["kind"] == "model_list":
            continue  # a list screen: its own Excel/PDF/Email bar (below)
        if x["kind"] not in REPORT_KINDS:
            bad.append("%s opens a %s screen, which has no report bar" % (name, x["kind"]))
        elif not x["target"]:
            bad.append("%s: the engine names no pack for it" % name)
        elif not rd.pack_function(x["target"]["module"], x["target"]["report"]):
            bad.append(
                "%s: pack %s:%s does not exist"
                % (name, x["target"]["module"], x["target"]["report"])
            )
        elif x["kind"] == "table_report" and x["target"]["module"] != x["cfgModule"]:
            bad.append(
                "%s exports %s, the screen reads %s" % (name, x["target"]["module"], x["cfgModule"])
            )
    assert not bad, "\n  ".join(bad)


def test_the_count_matches_the_sweep(estate):
    chips = [x for m in MODULES for x in estate[m]["chips"]]
    assert len(chips) >= 390
    kinds = {x["kind"] for x in chips}
    assert kinds <= set(REPORT_KINDS) | {"model_list"}, kinds


# --- the screens ------------------------------------------------------------------------

XML = (SRC / "p03_workspace.xml").read_text(encoding="utf-8")
ENGINE = (SRC / "p03_workspace.js").read_text(encoding="utf-8").replace("\r\n", "\n")
CALL = '<t t-call="cd_p03_portal.ReportActions"/>'


def _kind_block(kind):
    start = XML.index("state.gl.kind === '%s'" % kind)
    end = XML.find("<!-- ============", start)
    return XML[start : end if end != -1 else len(XML)]


@pytest.mark.parametrize("kind", REPORT_KINDS)
def test_every_report_screen_kind_carries_the_bar(kind):
    assert CALL in _kind_block(kind), "the %s screen has no export/email bar" % kind


def test_the_bar_offers_csv_excel_pdf_and_email():
    bar = XML[XML.index('<t t-name="cd_p03_portal.ReportActions">') :]
    bar = bar[: bar.index("</t>\n\n</templates>")]
    for action in ("csv", "xlsx", "pdf", "email"):
        assert 'data-report-action="%s"' % action in bar
    assert "this.exportReport('csv')" in bar and "this.exportReport('xlsx')" in bar
    assert "this.printReportPdf()" in bar and "this.reportEmailOpen()" in bar


def test_a_list_screen_keeps_its_own_excel_pdf_and_email():
    block = _kind_block("model_list")
    for needle in ("mlExportServer('xlsx')", "mlExportServer('pdf')", "mlEmailOpen()"):
        assert needle in block


def _method(sig):
    m = re.search(r"^    (%s \{\n.*?\n    \})\n" % re.escape(sig), ENGINE, re.S | re.M)
    assert m, sig
    return m.group(1)


def test_screen_download_and_email_are_one_query():
    """The report screen loads with reportTarget's params, the download sends
    them and the email dialog captures them - none rebuilds its own."""
    load = ENGINE[ENGINE.index('} else if (gl.kind === "table_report") {') :]
    load = load[: load.index("} else if", 10)]
    assert "this.reportTarget" in load and "params: target.params" in load
    export = _method("exportReport(format, inline)")
    assert "this.reportTarget" in export and "target.params" in export
    email = _method("reportEmailOpen()")
    assert "this.reportTarget" in email and "params: Object.assign({}, target.params" in email
    send = _method("async mlEmailSend()")
    assert '"/p03/model/report/email"' in send and "params: dlg.params" in send


def test_list_exports_and_email_carry_the_screens_scope():
    export = _method("mlExportServer(fmt)")
    assert "this.mlScope" in export and "JSON.stringify(scope.domain)" in export
    send = _method("async mlEmailSend()")
    assert "this.mlScope" in send


# --- the server ---------------------------------------------------------------------------


class FakeRequest:
    def __init__(self, env):
        self.env = env

    def make_response(self, data, headers=None, status=200):
        from types import SimpleNamespace

        return SimpleNamespace(data=data, headers=dict(headers or []), status=status)


@pytest.fixture
def api(odoo_env):
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api

    with mock.patch.object(p03_generic_api, "request", FakeRequest(odoo_env)):
        yield p03_generic_api.P03GenericApiController()


def _pdf_text(data):
    from PyPDF2 import PdfReader

    return " ".join(
        " ".join((page.extract_text() or "").split()) for page in PdfReader(io.BytesIO(data)).pages
    )


@pytest.mark.parametrize("mid", MODULES)
def test_every_pack_of_the_module_builds_excel_and_csv(odoo_env, estate, mid):
    """Every built-in report renders as the documents its buttons give, with
    the params the screen sends (superuser: the pack's own logic, not ACLs)."""
    rd = _registry()
    failed = []
    seen = set()
    for x in estate[mid]["chips"] + estate[mid]["badged"]:
        tgt = x["target"]
        if not tgt or (tgt["module"], tgt["report"]) in seen:
            continue
        seen.add((tgt["module"], tgt["report"]))
        params = {k: v for k, v in tgt["params"].items() if k != "customer_id"}
        for fmt in ("xlsx", "csv"):
            try:
                with odoo_env.cr.savepoint():
                    art = rd.build(odoo_env, tgt["module"], tgt["report"], fmt, params, mid)
                assert art["data"][:2] == b"PK" if fmt == "xlsx" else art["data"]
            except Exception as exc:  # report every pack, not just the first
                failed.append("%s:%s %s -> %r" % (tgt["module"], tgt["report"], fmt, exc))
    assert not failed, "\n  ".join(failed)


NEW_PACKS = [
    ("M19", "trial_balance"),
    ("M19", "pnl"),
    ("M19", "balance_sheet"),
    ("M19", "cash_flow"),
    ("M19", "consolidated_pnl"),
    ("M19", "journal_dimensions"),
    ("M19", "close_checklist"),
    ("M20", "ar_aging"),
    ("M20", "revenue_leakage"),
    ("M20", "customer_statement"),
]


@pytest.mark.parametrize(("module", "report"), NEW_PACKS)
def test_the_former_bespoke_reports_print_as_company_pdfs(odoo_env, module, report):
    rd = _registry()
    art = rd.build(odoo_env, module, report, "pdf", {"date_to": "2026-11-30"}, module)
    assert art["data"][:5] == b"%PDF-"
    text = _pdf_text(art["data"])
    assert "Hotline 16743" in text
    # notes print for the reader, never a model or field name
    assert not re.search(r"(account|fix)\.[a-z_]+\.[a-z_]+", text), text[:400]


def test_the_bespoke_finance_packs_keep_the_finance_gate(odoo_env):
    from odoo.exceptions import AccessError

    clerk = odoo_env["res.users"].create(
        {
            "name": "Report Standard Clerk",
            "login": "report-standard-%s@test.local" % uuid.uuid4().hex[:8],
            "group_ids": [(6, 0, [odoo_env.ref("base.group_user").id])],
        }
    )
    rd = _registry()
    for report in ("trial_balance", "pnl", "balance_sheet", "cash_flow", "journal_dimensions"):
        with pytest.raises(AccessError):
            rd.run_pack(odoo_env(user=clerk), "M19", report, {})


def test_the_emailed_report_is_the_report_on_screen(odoo_env, api):
    """Period and filters ride the email; the attachment is the PDF document
    with them; the sender's message is text, never HTML."""
    res = api.model_report_email(
        module="M19",
        report="trial_balance",
        params={"date_from": "2026-07-01", "date_to": "2026-10-31", "module_label": "x"},
        module_label="M19 · Financial Accounting & GL",
        to="cfo@example.com; controller@example.com",
        subject="TB for review",
        body="Please review <script>alert(1)</script>\nThanks",
        format="pdf",
    )
    assert res.get("ok"), res
    assert res["recipients"] == ["cfo@example.com", "controller@example.com"]
    mail = odoo_env["mail.mail"].browse(res["mail_id"])
    assert mail.subject == "TB for review"
    assert "<script>" not in mail.body_html and "&lt;script&gt;" in mail.body_html
    assert "Dhaka time" in mail.body_html and "2026-07-01 → 2026-10-31" in mail.body_html
    data = base64.b64decode(mail.attachment_ids[0].datas)
    text = _pdf_text(data)
    assert "2026-07-01 to 2026-10-31" in text, text[:400]
    assert "Trial Balance" in text
    log = odoo_env["fix.bi.export.log"].search([("pack", "=", "M19:trial_balance")], limit=1)
    if log and "email" in dict(log._fields["channel"].selection):
        assert log.channel == "email"


def test_email_refuses_bad_recipients_and_unknown_reports(api):
    assert "error" in api.model_report_email(module="M19", report="pnl", to="not-an-email")
    assert "error" in api.model_report_email(module="M19", report="pnl", to="")
    many = ",".join("a%d@example.com" % i for i in range(11))
    assert "error" in api.model_report_email(module="M19", report="pnl", to=many)
    assert "error" in api.model_report_email(module="M19", report="nope", to="a@example.com")
    assert "error" in api.model_report_email(
        module="M19", report="pnl", to="a@example.com", format="csv"
    )


def test_the_old_list_email_pack_mode_now_carries_the_period(odoo_env, api):
    res = api.model_list_email(
        module="M19",
        report="trial_balance",
        params={"date_from": "2026-08-01", "date_to": "2026-08-31"},
        to="cfo@example.com",
        format="xlsx",
    )
    assert res.get("ok"), res
    from openpyxl import load_workbook

    mail = odoo_env["mail.mail"].browse(res["mail_id"])
    wb = load_workbook(io.BytesIO(base64.b64decode(mail.attachment_ids[0].datas)))
    cells = " ".join(str(c.value) for row in wb.active.iter_rows() for c in row if c.value)
    assert "2026-08-01" in cells and "2026-08-31" in cells


def test_a_list_export_carries_only_the_screens_rows(odoo_env, api):
    tag = "RptStd%s" % uuid.uuid4().hex[:8]
    for n in ("alpha", "beta", "gamma"):
        odoo_env["res.partner"].create({"name": "%s %s" % (tag, n)})
    scope = api._list_scope(domain=json.dumps([["name", "ilike", "%s beta" % tag]]), search=tag)
    payload, err = api._model_list_export_payload("res.partner", "name", None, scope=scope)
    assert not err, err
    assert [r["name"] for r in payload["rows"]] == ["%s beta" % tag]
    # and the email of that list attaches the same rows
    res = api.model_list_email(
        model="res.partner",
        cols="name",
        to="ops@example.com",
        format="xlsx",
        domain=[["name", "ilike", "%s beta" % tag]],
        search=tag,
        title="Parties",
    )
    assert res.get("ok"), res
    from openpyxl import load_workbook

    mail = odoo_env["mail.mail"].browse(res["mail_id"])
    wb = load_workbook(io.BytesIO(base64.b64decode(mail.attachment_ids[0].datas)))
    names = [c.value for row in wb.active.iter_rows() for c in row if isinstance(c.value, str)]
    assert "%s beta" % tag in names
    assert "%s alpha" % tag not in names and "%s gamma" % tag not in names


def test_a_malformed_list_domain_exports_the_unscoped_screen_not_an_error(api):
    assert api._list_scope(domain="{not json")["domain"] == []
    assert api._list_scope(domain='{"a": 1}')["domain"] == []
