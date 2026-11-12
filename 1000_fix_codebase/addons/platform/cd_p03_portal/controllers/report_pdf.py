# cd_p03_portal — the professional PDF for every workspace report and list.
#
# 12 Nov 2026: the report screens' "PDF" button printed a hand-built page
# through the BROWSER's print dialog - no logo, no company identity, the
# browser's own date/title/URL ("localhost:8069/odoo/operations") and "1/1"
# stamped on the page, "0 rows" as the body of an empty report. The branded
# server PDF that existed (reportlab, report_bytes.pdf_bytes) was not used by
# the report screens, could not render Bengali, put the totals in as an
# ordinary row and stated the time in UTC.
#
# This renders the document as HTML through Odoo's own wkhtmltopdf engine,
# the way Odoo prints its invoices: a real per-page letterhead and footer,
# the browser's text shaping (Bengali conjuncts), A4 portrait or landscape by
# width. The letterhead comes from brand.py / res.company, so every document
# follows the company record.
from __future__ import annotations

import base64
import datetime
import functools
import html
import logging

import pytz

from . import brand as _brand

_logger = logging.getLogger(__name__)

BRAND_BLUE = "#0406C5"  # the logo's blue
BRAND_MAGENTA = "#FF00C9"  # the logo's frame
INK = "#1F2328"
MUTED = "#5F6368"
RULE = "#D9DCE3"
ZEBRA = "#F6F7FB"
TZ = "Asia/Dhaka"
FONT_STACK = (
    '"Segoe UI", "Noto Sans", "Noto Sans Bengali", "Nirmala UI", "Vrinda", Arial, sans-serif'
)


@functools.lru_cache(maxsize=1)
def _logo_data_uri() -> str:
    """The official logo, embedded (wkhtmltopdf runs with local file access off)."""
    try:
        raw = _brand.logo_path().read_bytes()
    except OSError:
        _logger.exception("letterhead logo missing")
        return ""
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def _esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def local_now(env=None) -> datetime.datetime:
    """Business time: Dhaka, whatever the reader's own zone (servers run UTC;
    a document the company issues states the company's time - it read +08
    for an administrator whose profile zone was elsewhere)."""
    return datetime.datetime.now(pytz.utc).astimezone(pytz.timezone(TZ))


def document_number(module, report, when) -> str:
    """A reference the reader can quote back: RPT-<module>-<yyyymmdd>-<hhmmss>."""
    code = (module or "WS").upper()
    return "RPT-%s-%s" % (code, when.strftime("%Y%m%d-%H%M%S"))


def _cell_text(value) -> str:
    """A cell as the reader should see it (never the literal True/False/None).
    A yes/no reads Yes/No, as the list exports already print it."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if value is None or value == "":
        return "—"
    if isinstance(value, dict):
        return str(value.get("label") or value.get("name") or value.get("key") or "—")
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}" if value != int(value) else f"{int(value):,}"
    return str(value)


def _is_number(value) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _letterhead(env) -> dict:
    lh = dict(_brand.letterhead(env))
    company = env.company
    lh["bin"] = company.partner_id.vat or company.vat or ""
    lh["website"] = (company.website or company.partner_id.website or "").replace("https://", "")
    if lh["website"].startswith("http://"):
        lh["website"] = lh["website"][7:]
    return lh


# Rendered at 150 dpi: at Odoo's usual 96 the Windows build of wkhtmltopdf
# spaces letters apart ("D o c u m e n t"). Odoo then zooms the page by
# 96/150, so the document is scaled back up by the same ratio - the sizes in
# the CSS below are the sizes on paper.
DPI = 150


@functools.lru_cache(maxsize=1)
def _zoom() -> float:
    try:
        from odoo.addons.base.models.ir_actions_report import _wkhtml

        return round(DPI / 96.0, 4) if _wkhtml().dpi_zoom_ratio else 1.0
    except Exception:
        return 1.0


def _base_css(landscape: bool) -> str:
    return """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { zoom: %(zoom)s; }
body { font-family: %(font)s; color: %(ink)s; font-size: 9.5pt; line-height: 1.35; }
""" % {"font": FONT_STACK, "ink": INK, "zoom": _zoom()}


def header_html(env) -> str:
    lh = _letterhead(env)
    logo = _logo_data_uri()
    contact = " · ".join(
        x
        for x in (
            "BIN %s" % lh["bin"] if lh["bin"] else "",
            lh.get("phone") or "",
            lh.get("email") or "",
            lh["website"],
        )
        if x
    )
    return """<!DOCTYPE html><html><head><meta charset="utf-8"/><style>%(css)s
.lh { display: table; width: 100%%; border-bottom: 2px solid %(blue)s; padding-bottom: 6px; }
.lh .l, .lh .r { display: table-cell; vertical-align: bottom; }
.lh .r { text-align: right; }
.lh img { height: 40px; }
.lh .name { font-size: 11.5pt; font-weight: 700; color: %(ink)s; letter-spacing: .1px; }
.lh .line { font-size: 7.6pt; color: %(muted)s; }
.lh .iso { font-size: 7.2pt; color: %(blue)s; font-weight: 600; }
.accent { height: 2px; width: 72px; background: %(magenta)s; margin-top: 2px; }
</style></head><body>
<div class="lh">
  <div class="l">%(logo)s</div>
  <div class="r">
    <div class="name">%(name)s</div>
    <div class="line">%(address)s</div>
    <div class="line">%(contact)s</div>
    <div class="iso">%(iso)s · Hotline %(hotline)s</div>
  </div>
</div>
<div class="accent"></div>
</body></html>""" % {
        "css": _base_css(False),
        "blue": BRAND_BLUE,
        "magenta": BRAND_MAGENTA,
        "ink": INK,
        "muted": MUTED,
        "logo": '<img src="%s" alt="1000FiX"/>' % logo if logo else "<b>%s</b>" % _esc(lh["name"]),
        "name": _esc(lh["name"]),
        "address": _esc(", ".join(lh["address_lines"])),
        "contact": _esc(contact),
        "iso": _esc(_brand.ISO_BADGE),
        "hotline": _esc(_brand.HOTLINE),
    }


def footer_html(env, doc_no: str, generated: str) -> str:
    lh = _letterhead(env)
    return """<!DOCTYPE html><html><head><meta charset="utf-8"/><style>%(css)s
.ft { display: table; width: 100%%; border-top: 1px solid %(rule)s; padding-top: 4px; font-size: 7.2pt; color: %(muted)s; }
.ft div { display: table-cell; width: 33%%; }
.ft .c { text-align: center; }
.ft .r { text-align: right; }
</style><script>
function subst() {
  var vars = {}, q = document.location.search.substring(1).split('&');
  for (var i = 0; i < q.length; i++) { var kv = q[i].split('=', 2); vars[kv[0]] = decodeURIComponent(kv[1] || ''); }
  ['page', 'topage'].forEach(function (k) {
    var els = document.getElementsByClassName(k);
    for (var j = 0; j < els.length; j++) { els[j].textContent = vars[k] || ''; }
  });
}
</script></head><body onload="subst()">
<div class="ft">
  <div>Confidential — for the internal use of %(name)s</div>
  <div class="c">%(doc)s · %(generated)s</div>
  <div class="r">Page <span class="page"></span> of <span class="topage"></span></div>
</div>
</body></html>""" % {
        "css": _base_css(False),
        "rule": RULE,
        "muted": MUTED,
        "name": _esc(lh["name"]),
        "doc": _esc(doc_no),
        "generated": _esc(generated),
    }


def body_html(env, doc) -> str:
    """doc: {title, subtitle, doc_no, meta:[(label, value)], cols, labels,
    rows, totals, notes, count, empty}"""
    cols, labels = doc["cols"], doc["labels"]
    rows, totals = doc["rows"], doc.get("totals") or {}
    numeric = {
        c for c in cols if any(_is_number(r.get(c)) for r in rows) or _is_number(totals.get(c))
    }

    def th(c):
        cls = ' class="num"' if c in numeric else ""
        return "<th%s>%s</th>" % (cls, _esc(labels.get(c, c)))

    def td(c, value):
        cls = ' class="num"' if c in numeric else ""
        return "<td%s>%s</td>" % (cls, _esc(_cell_text(value)))

    body_rows = "".join("<tr>%s</tr>" % "".join(td(c, r.get(c)) for c in cols) for r in rows)
    if not rows:
        body_rows = '<tr class="empty"><td colspan="%d">%s</td></tr>' % (
            max(len(cols), 1),
            _esc(doc.get("empty") or "No records for the selected period and filters."),
        )
    total_row = ""
    if totals and rows:
        cells = []
        for i, c in enumerate(cols):
            value = totals.get(c, "")
            if i == 0 and (value in ("", None)):
                value = "Total"
            cells.append(td(c, value) if value not in ("", None) else "<td></td>")
        total_row = '<tr class="total">%s</tr>' % "".join(cells)

    meta = "".join(
        "<tr><th>%s</th><td>%s</td></tr>" % (_esc(k), _esc(v)) for k, v in doc["meta"] if v
    )
    notes = doc.get("notes") or []
    notes_html = (
        '<div class="notes"><div class="h">Notes</div><ol>%s</ol></div>'
        % "".join("<li>%s</li>" % _esc(n) for n in notes)
        if notes
        else ""
    )
    return """<!DOCTYPE html><html><head><meta charset="utf-8"/><style>%(css)s
.title { margin: 2px 0 0; font-size: 16pt; font-weight: 700; color: %(ink)s; }
.subtitle { font-size: 9pt; color: %(blue)s; font-weight: 600; margin: 1px 0 8px; text-transform: uppercase; letter-spacing: .6px; }
table.meta { border-collapse: collapse; margin: 0 0 10px; font-size: 8.4pt; }
table.meta th { text-align: left; color: %(muted)s; font-weight: 600; padding: 1.5px 14px 1.5px 0; white-space: nowrap; vertical-align: top; }
table.meta td { padding: 1.5px 0; color: %(ink)s; }
table.grid { width: 100%%; border-collapse: collapse; font-size: 8.6pt; }
table.grid thead { display: table-header-group; }
table.grid tr { page-break-inside: avoid; }
table.grid th { background: %(blue)s; color: #fff; text-align: left; font-weight: 600; padding: 5px 6px; border: 1px solid %(blue)s; }
table.grid td { padding: 4px 6px; border-bottom: 1px solid %(rule)s; vertical-align: top; }
table.grid tbody tr:nth-child(even) td { background: %(zebra)s; }
table.grid .num { text-align: right; white-space: nowrap; }
table.grid tr.total td { font-weight: 700; border-top: 2px solid %(blue)s; border-bottom: 2px solid %(blue)s; background: #EEF0FB; }
table.grid tr.empty td { text-align: center; color: %(muted)s; padding: 18px 6px; font-style: italic; background: #fff; }
.count { font-size: 8pt; color: %(muted)s; margin-top: 5px; }
.notes { margin-top: 12px; font-size: 8pt; color: %(muted)s; page-break-inside: avoid; }
.notes .h { font-weight: 700; color: %(ink)s; font-size: 8.4pt; margin-bottom: 2px; }
.notes ol { margin: 0; padding-left: 16px; }
.end { margin-top: 14px; text-align: center; font-size: 7.6pt; color: %(muted)s; letter-spacing: 1px; }
</style></head><body>
<div class="title">%(title)s</div>
<div class="subtitle">%(subtitle)s</div>
<table class="meta">%(meta)s</table>
<table class="grid"><thead><tr>%(head)s</tr></thead><tbody>%(rows)s%(total)s</tbody></table>
<div class="count">%(count)s</div>
%(notes)s
<div class="end">— END OF REPORT —</div>
</body></html>""" % {
        "css": _base_css(False),
        "ink": INK,
        "blue": BRAND_BLUE,
        "muted": MUTED,
        "rule": RULE,
        "zebra": ZEBRA,
        "title": _esc(doc["title"]),
        "subtitle": _esc(doc.get("subtitle") or ""),
        "meta": meta,
        "head": "".join(th(c) for c in cols) if cols else "<th></th>",
        "rows": body_rows,
        "total": total_row,
        "count": _esc(
            "%s record%s" % ("{:,}".format(doc["count"]), "" if doc["count"] == 1 else "s")
        ),
        "notes": notes_html,
    }


def build_document(env, payload, base_name, title=None):
    """Normalise a report pack / list export payload into the document model."""
    meta_in = payload.get("meta") or {}
    now = local_now(env)
    module = meta_in.get("module") or ""
    doc_no = document_number(module or base_name.split("_")[0][:4], meta_in.get("report"), now)
    generated = now.strftime("%d %b %Y, %H:%M") + " (Dhaka time)"
    params = meta_in.get("params") or {}
    meta = [("Document No.", doc_no), ("Company", _letterhead(env)["name"])]
    if params.get("date_from") or params.get("date_to"):
        meta.append(
            ("Period", "%s to %s" % (params.get("date_from") or "…", params.get("date_to") or "…"))
        )
    filters = [
        "%s: %s" % (k.replace("_", " ").title(), v)
        for k, v in sorted(params.items())
        if v
        and k
        not in ("date_from", "date_to", "module_label", "inline", "format", "module", "report")
    ]
    if filters:
        meta.append(("Filters", " · ".join(filters)))
    meta.append(("Generated", generated))
    meta.append(("Generated by", env.user.name or ""))
    return {
        "doc_no": doc_no,
        "generated": generated,
        "title": title or meta_in.get("title") or base_name.replace("_", " ").title(),
        "subtitle": meta_in.get("module_label") or "",
        "meta": meta,
        "cols": payload.get("cols") or [],
        "labels": payload.get("labels") or {},
        "rows": payload.get("rows") or [],
        "totals": meta_in.get("totals") or {},
        "notes": meta_in.get("notes") or payload.get("notes") or [],
        "count": payload.get("count", len(payload.get("rows") or [])),
        "empty": meta_in.get("empty"),
    }


def pdf_bytes(env, payload, base_name, title=None) -> bytes:
    """The professional PDF: letterhead and footer on every page, through
    Odoo's wkhtmltopdf. Raises if the engine is unavailable (the caller
    falls back to the reportlab renderer)."""
    doc = build_document(env, payload, base_name, title=title)
    landscape = len(doc["cols"]) > 6
    Report = env["ir.actions.report"].sudo()
    return Report._run_wkhtmltopdf(
        [body_html(env, doc)],
        header=header_html(env),
        footer=footer_html(env, doc["doc_no"], doc["generated"]),
        landscape=landscape,
        specific_paperformat_args={
            "data-report-margin-top": 36,
            "data-report-header-spacing": 6,
            "data-report-margin-bottom": 16,
            "data-report-dpi": DPI,
        },
    )
