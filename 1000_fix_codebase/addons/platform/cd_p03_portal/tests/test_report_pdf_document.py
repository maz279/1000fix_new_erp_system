# The workspace report PDF is a company document (12 Nov 2026).
#
# The report screens' "PDF" printed a page built in the browser through the
# browser's print dialog: no logo, no company identity, the browser's own
# date / title / "localhost:8069/odoo/operations" / "1/1" stamped on the page,
# "0 rows" as the body of an empty report, technical notes. The server PDF
# that existed was never called by those screens, could not shape Bengali,
# printed the totals as an ordinary row and stated UTC.
#
# These tests render real PDFs (Odoo's wkhtmltopdf) and read the text back.
from __future__ import annotations

import io
import re
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_p03_portal.controllers import a02, brand, report_bytes, report_pdf
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

SRC = Path(__file__).resolve().parents[1] / "static" / "src"


def _pdf_text(data: bytes) -> tuple[str, list]:
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join(p.extract_text() or "" for p in reader.pages), reader.pages


def _payload(rows=None, cols=None, **meta):
    cols = cols or ["measure", "orders"]
    return {
        "rows": rows if rows is not None else [],
        "cols": cols,
        "labels": {"measure": "Measure", "orders": "Orders", "amount": "Amount (BDT)"},
        "count": len(rows or []),
        "meta": {"module": "M01", "module_label": "M01 · Service Requests & Orders", **meta},
    }


# --- the document model ------------------------------------------------------


def test_the_document_states_what_it_is(odoo_env):
    doc = report_pdf.build_document(
        odoo_env,
        _payload(
            params={"date_from": "2026-07-01", "date_to": "2027-06-30", "channel": "walk_in"},
            report="channel_intake",
            title="Daily Intake by Channel",
        ),
        "M01_channel_intake",
    )
    assert re.fullmatch(r"RPT-M01-\d{8}-\d{6}", doc["doc_no"])
    meta = dict(doc["meta"])
    assert meta["Document No."] == doc["doc_no"]
    assert meta["Company"] == brand.letterhead(odoo_env)["name"]
    assert meta["Period"] == "2026-07-01 to 2027-06-30"
    assert meta["Filters"] == "Channel: walk_in"
    assert meta["Generated"].endswith("(Dhaka time)")
    assert doc["subtitle"] == "M01 · Service Requests & Orders"
    assert doc["title"] == "Daily Intake by Channel"


def test_business_time_is_dhaka_whatever_the_readers_zone(odoo_env):
    """It read +08 for an administrator whose profile zone was elsewhere."""
    odoo_env.user.tz = "Asia/Singapore"
    now = report_pdf.local_now(odoo_env)
    assert now.utcoffset().total_seconds() == 6 * 3600


def test_the_client_keys_are_not_report_filters(odoo_env):
    doc = report_pdf.build_document(
        odoo_env, _payload(params={"module_label": "x", "inline": "1"}), "M01_x"
    )
    assert "Filters" not in dict(doc["meta"])


# --- the body ------------------------------------------------------------------


def test_numbers_are_formatted_and_right_aligned_and_totals_are_a_totals_line(odoo_env):
    rows = [{"measure": "Walk-in", "amount": 1234567.5}, {"measure": "Hotline", "amount": 300}]
    doc = report_pdf.build_document(
        odoo_env,
        _payload(rows=rows, cols=["measure", "amount"], totals={"amount": 1234867.5}),
        "M01_x",
    )
    html = report_pdf.body_html(odoo_env, doc)
    assert '<th class="num">Amount (BDT)</th>' in html
    assert '<td class="num">1,234,567.50</td>' in html
    assert '<td class="num">300</td>' in html
    assert '<tr class="total"><td>Total</td><td class="num">1,234,867.50</td></tr>' in html
    assert "2 records" in html


def test_an_empty_report_says_so_in_words(odoo_env):
    html = report_pdf.body_html(odoo_env, report_pdf.build_document(odoo_env, _payload(), "x"))
    assert "No records for the selected period and filters." in html
    assert "0 records" in html
    assert "0 rows" not in html


def test_a_yes_no_value_reads_yes_or_no(odoo_env):
    assert report_pdf._cell_text(True) == "Yes"
    assert report_pdf._cell_text(False) == "No"
    assert report_pdf._cell_text(None) == "—"
    assert report_pdf._cell_text({"key": "x", "label": "Walk-in"}) == "Walk-in"


# --- letterhead and footer, on every page -----------------------------------------


def test_the_letterhead_carries_the_official_logo_and_the_company(odoo_env):
    header = report_pdf.header_html(odoo_env)
    logo = brand.logo_path().read_bytes()
    import base64

    assert 'src="data:image/png;base64,%s"' % base64.b64encode(logo).decode() in header
    lh = brand.letterhead(odoo_env)
    assert lh["name"] in header
    for line in lh["address_lines"]:
        assert line.replace("&", "&amp;") in header
    assert brand.ISO_BADGE in header and brand.HOTLINE in header


def test_the_footer_numbers_pages_and_carries_no_browser_url(odoo_env):
    footer = report_pdf.footer_html(odoo_env, "RPT-M01-20261112-101010", "12 Nov 2026, 10:10")
    assert '<span class="page"></span> of <span class="topage"></span>' in footer
    assert "RPT-M01-20261112-101010" in footer and "Confidential" in footer
    assert "localhost" not in footer and "odoo/operations" not in footer


# --- a real document -----------------------------------------------------------


def _render(env, payload, title="Daily Intake by Channel"):
    try:
        return report_pdf.pdf_bytes(env, payload, "M01_channel_intake", title=title)
    except Exception as exc:  # pragma: no cover - a server without wkhtmltopdf
        pytest.skip("wkhtmltopdf is not available here: %s" % exc)


def test_a_rendered_report_reads_as_a_company_document(odoo_env):
    data = _render(
        odoo_env,
        _payload(
            rows=[{"measure": "Resolved on time", "orders": 12}],
            params={"date_from": "2026-07-01", "date_to": "2027-06-30"},
            notes=["On time means the order was resolved before its SLA deadline."],
        ),
    )
    assert data[:5] == b"%PDF-"
    text, pages = _pdf_text(data)
    flat = " ".join(text.split())
    assert "Daily Intake by Channel" in flat
    assert "SERVICE REQUESTS & ORDERS" in flat.upper()
    assert brand.letterhead(odoo_env)["name"] in flat
    assert "Page 1 of 1" in flat
    assert "Resolved on time" in flat and "END OF REPORT" in flat
    assert "localhost" not in flat and "odoo/operations" not in flat
    assert "1/1" not in flat
    assert float(pages[0].mediabox.width) < float(pages[0].mediabox.height)  # portrait


def test_a_wide_report_turns_landscape_and_pages_are_numbered(odoo_env):
    cols = ["c%d" % i for i in range(8)]
    rows = [{c: "row %d" % n for c in cols} for n in range(120)]
    payload = {
        "rows": rows,
        "cols": cols,
        "labels": {},
        "count": len(rows),
        "meta": {"module": "M01"},
    }
    text, pages = _pdf_text(_render(odoo_env, payload, title="Wide"))
    assert len(pages) >= 2
    assert float(pages[0].mediabox.width) > float(pages[0].mediabox.height)
    assert "Page 1 of %d" % len(pages) in " ".join(text.split())
    # the column header repeats on every page
    assert all("c0" in (p.extract_text() or "") for p in pages)


def test_without_the_engine_the_document_still_comes_out(odoo_env):
    with mock.patch.object(report_pdf, "pdf_bytes", side_effect=OSError("no wkhtmltopdf")):
        data = report_bytes.pdf_bytes(
            odoo_env, _payload(rows=[{"measure": "x", "orders": 1}], totals={"orders": 1}), "M01_x"
        )
    assert data[:5] == b"%PDF-"


# --- the route the screens call ---------------------------------------------------------


class FakeRequest:
    def __init__(self, env):
        self.env = env

    def make_response(self, data, headers=None, status=200):
        return SimpleNamespace(data=data, headers=dict(headers or []), status=status)


def test_the_print_button_gets_an_inline_company_pdf_and_the_report_no_client_keys(odoo_env):
    seen = {}

    def pack(env, **params):
        seen.update(params)
        return {
            "title": "Daily Intake by Channel",
            "cols": ["day", "orders"],
            "labels": {"day": "Day", "orders": "Orders"},
            "rows": [{"day": "2026-11-12", "orders": 3}],
            "totals": {"orders": 3},
            "notes": ["Service orders received in the period."],
        }

    with (
        mock.patch.dict(a02.MODULES["M01"].REPORTS, {"probe_pack": pack}),
        mock.patch.object(api, "request", FakeRequest(odoo_env)),
        mock.patch.object(api, "_log_report_export", lambda *a, **k: None),
    ):
        # the route's own function: the http wrapper insists on a werkzeug Response
        export = api.P03GenericApiController.model_report_export.original_endpoint
        res = export(
            api.P03GenericApiController(),
            module="M01",
            report="probe_pack",
            format="pdf",
            date_from="2026-11-01",
            date_to="2026-11-30",
            module_label="M01 · Service Requests & Orders",
            inline="1",
        )
    if res.status != 200 or not isinstance(res.data, bytes):
        pytest.fail("export answered %s" % res.status)
    assert res.headers["Content-Type"] == "application/pdf"
    assert res.headers["Content-Disposition"].startswith("inline;")
    assert seen == {"date_from": "2026-11-01", "date_to": "2026-11-30"}
    flat = " ".join(_pdf_text(res.data)[0].split())
    assert "2026-11-01 to 2026-11-30" in flat
    assert "Total" in flat


# --- the screens -----------------------------------------------------------------------


def test_the_report_pdf_button_opens_the_server_document():
    engine = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
    body = engine[engine.index("    printReportPdf() {") :]
    body = body[: body.index("\n    }\n")]
    assert 'this.exportReport("pdf", true)' in body
    assert "_reportPrintHtml" not in engine and "window.print" not in body
    export = engine[engine.index("    exportReport(format, inline) {") :]
    export = export[: export.index("\n    }\n")]
    assert 'params.set("module_label"' in export and 'params.set("inline", "1")' in export
