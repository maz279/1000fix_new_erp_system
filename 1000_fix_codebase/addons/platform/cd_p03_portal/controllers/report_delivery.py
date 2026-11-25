# cd_p03_portal — one delivery path for every built-in report (13 Nov 2026).
#
# The estate standard: a built-in report on ANY module page (M01-M67) can be
# downloaded as CSV, Excel or PDF and sent by email, and all of those carry
# the SAME rows, period, filters, totals and notes the screen shows.
#
# Before this file the same pack was resolved by three copied `a08 or a02 or
# ...` chains, the report screen had no Email button at all, and the email
# route's "pack mode" re-ran the pack WITHOUT the user's period or filters
# and dropped its totals and notes - the attachment was not the report on
# the screen. Download, email and the scheduled subscriptions now all build
# their artefact here (HTTP-free, so the cron can use it too).
from __future__ import annotations

import base64
import html
import logging
import re

from . import report_bytes

_logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_RECIPIENTS = 10
FORMATS = ("csv", "xlsx", "pdf")
MAIL_FORMATS = ("xlsx", "pdf")
# a printable document of 14k rows is hundreds of pages of paper: the PDF
# carries the first rows and SAYS so; Excel and CSV carry every row
PDF_MAX_ROWS = 2000


def _areas():
    """The area registries, in the order the workspace has always resolved a
    module code (imported lazily: the subscription model imports this file)."""
    from . import a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12

    return (a08, a02, a03, a04, a05, a06, a07, a09, a10, a12, a11)


def module_fragment(module):
    """The module's controller fragment (e.g. a08.m19), or None."""
    for area in _areas():
        fragment = getattr(area, "MODULES", {}).get(module)
        if fragment is not None:
            return fragment
    return None


def pack_function(module, report):
    """The report pack function for ``module:report``, or None."""
    fragment = module_fragment(module)
    return getattr(fragment, "REPORTS", {}).get(report) if fragment is not None else None


def split_params(params):
    """(pack params, document params): the client's document keys (its module
    title, open-in-tab) are not report filters, so the pack never sees them."""
    params = dict(params or {})
    doc = {k: params.pop(k) for k in list(params) if k in report_bytes.DOC_KEYS}
    # empty values are "not set", as the screen treats them
    return {k: v for k, v in params.items() if v not in (None, "", "All")}, doc


def run_pack(env, module, report, params):
    fn = pack_function(module, report)
    if not fn:
        raise LookupError("Report not available on this surface")
    out = fn(env, **(params or {})) or {}
    out.setdefault("rows", [])
    out.setdefault("cols", [])
    return out


def base_name(module, report):
    return "%s_%s" % (module or "report", (report or "export").replace("/", "_"))


def build(env, module, report, fmt, params=None, module_label=""):
    """Run the pack with the screen's own params and render it.

    Returns ``{data, filename, mimetype, out, count, title}``. ``params`` are
    the pack params (see :func:`split_params`)."""
    if fmt not in FORMATS:
        raise ValueError("format must be csv, xlsx or pdf")
    params = dict(params or {})
    out = run_pack(env, module, report, params)
    cols = out.get("cols") or []
    labels = out.get("labels") if isinstance(out.get("labels"), dict) else {}
    rows = list(out.get("rows") or [])
    name = base_name(module, report)
    module_label = str(module_label or "")[:80]
    if fmt == "xlsx":
        meta_params = dict(params, module=module or "", module_label=module_label)
        data = report_bytes.xlsx_bytes(env, out, cols, labels, name, meta_params)
        mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "pdf":
        notes = list(out.get("notes") or [])
        if len(rows) > PDF_MAX_ROWS:
            notes.append(
                "This document shows the first %s of %s rows; the Excel file carries them all."
                % (f"{PDF_MAX_ROWS:,}", f"{len(rows):,}")
            )
            rows = rows[:PDF_MAX_ROWS]
        payload = {
            "rows": rows,
            "cols": cols,
            "labels": labels,
            "count": len(out.get("rows") or []),
            "meta": {
                "module": module or "",
                "report": report or "",
                "module_label": module_label,
                "params": params,
                "totals": out.get("totals") or {},
                "notes": notes,
                "title": out.get("title"),
                "empty": out.get("empty"),
            },
        }
        data = report_bytes.pdf_bytes(env, payload, name, title=out.get("title"))
        mimetype = "application/pdf"
    else:
        data = csv_bytes(out, cols, labels)
        mimetype = "text/csv; charset=utf-8"
    return {
        "data": data,
        "filename": "%s.%s" % (name, fmt),
        "mimetype": mimetype,
        "out": out,
        "count": len(out.get("rows") or []),
        "title": out.get("title") or name.replace("_", " "),
    }


def csv_bytes(out, cols, labels):
    """Raw values (numbers unformatted) so a spreadsheet can compute; a UTF-8
    BOM so Excel opens Bengali text correctly (repo i18n rule)."""
    import csv
    import io

    buf = io.StringIO()
    buf.write("﻿")
    writer = csv.writer(buf)
    writer.writerow([labels.get(c, c) for c in cols])
    for row in out.get("rows") or []:
        writer.writerow([_csv_cell(row.get(c, "")) for c in cols])
    totals = out.get("totals")
    if totals:
        writer.writerow([_csv_cell(totals.get(c, "")) for c in cols])
    return buf.getvalue().encode("utf-8")


def _csv_cell(value):
    if isinstance(value, dict):
        return value.get("label") or value.get("name") or ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return "" if value is None else value


def parse_recipients(to):
    """(emails, error): 1-10 valid addresses, comma/semicolon/space separated."""
    emails = [e.strip() for e in re.split(r"[;,\s]+", to or "") if e.strip()]
    bad = [e for e in emails if not EMAIL_RE.fullmatch(e)]
    if bad:
        return [], "Not a valid email address: %s" % ", ".join(bad[:3])
    if not emails or len(emails) > MAX_RECIPIENTS:
        return [], "Between 1 and %d recipient emails required" % MAX_RECIPIENTS
    # one copy per address, in the order typed
    return list(dict.fromkeys(emails)), None


def send_mail(env, emails, data, filename, title, count, subject=None, body=None, scope=None):
    """Queue one email with the artefact attached and try to send it now.

    The sender's message is plain text: it is escaped, never trusted as HTML
    (it used to be pasted into the body raw). Times are Dhaka business time.
    An SMTP failure is reported as the mail's state, not raised."""
    from . import brand as _brand
    from . import report_pdf

    lh = _brand.letterhead(env)
    now = report_pdf.local_now(env).strftime("%Y-%m-%d %H:%M")
    attachment = env["ir.attachment"].create(
        {
            "name": filename,
            "datas": base64.b64encode(data).decode(),
            "public": False,
        }
    )
    message = html.escape(body or "Please find the attached report.").replace("\n", "<br/>")
    lines = [
        "<p>%s</p>" % message,
        "<p><b>%s</b>%s<br/>%s rows · generated %s (Dhaka time) by %s</p>"
        % (
            html.escape(title or filename),
            (" · %s" % html.escape(scope)) if scope else "",
            f"{count:,}",
            now,
            html.escape(env.user.name or ""),
        ),
        "<p style='color:#888;font-size:12px'>%s<br/>%s</p>"
        % (html.escape(lh["name"] + " · " + _brand.ISO_BADGE), html.escape(lh["contact_line"])),
    ]
    mail = env["mail.mail"].create(
        {
            "subject": (subject or "").strip()[:200] or "%s — %s" % (lh["name"], title or filename),
            "body_html": "".join(lines),
            "email_to": ", ".join(emails),
            "auto_delete": False,
            "attachment_ids": [(6, 0, [attachment.id])],
        }
    )
    state_before = mail.state
    try:
        mail.send(raise_exception=False)
    except Exception:
        _logger.exception("report email send failed for %s", filename)
    return {
        "ok": True,
        "mail_id": mail.id,
        "recipients": emails,
        "state": mail.state or state_before,
        "attachment": attachment.name,
        "rows": count,
    }


def log_export(env, pack, channel, fmt, count, params):
    """A11 audit E6 / BRU-BID-11: every artefact that leaves the system is
    logged - who, what, which scope, how many rows, by which channel. A
    logging failure never blocks the delivery."""
    try:
        if "fix.bi.export.log" not in env:
            return
        Log = env["fix.bi.export.log"].sudo()
        channels = dict(Log._fields["channel"].selection)
        env["fix.bi.export.log"].sudo().create(
            {
                "user_id": env.user.id,
                "pack": pack,
                "channel": channel if channel in channels else "download",
                "format": fmt,
                "company_ids": ", ".join(env.companies.mapped("name")),
                "row_count": count,
                "params_json": repr(params or {})[:2000],
            }
        )
    except Exception:
        _logger.exception("export log write failed for %s", pack)
