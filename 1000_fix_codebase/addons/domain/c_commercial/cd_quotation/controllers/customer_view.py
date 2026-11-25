# M36 the customer's one-screen approval page (FR-QTE-034, T-05; capture
# audit pass 3, 2026-11-19).
#
# Served by the token the agent sent with "Send Customer Approval Link". The
# page carries the price, the lines, VAT and the terms in Bengali and English,
# never cost or margin (BRU-QTE-13). Approval is never a bare tap: the
# customer asks for a code on their own phone and types it back, which runs the
# same acceptance as Accept by Customer Code (evidence pack, credit gate,
# validity). A new link for the same quotation replaces the old one.
from markupsafe import escape
from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

_STATES = {
    "sent": ("Awaiting your decision", "আপনার সিদ্ধান্তের অপেক্ষায়"),
    "accepted": ("Accepted - thank you", "গৃহীত - ধন্যবাদ"),
    "declined": ("Declined", "প্রত্যাখ্যাত"),
    "expired": ("Expired - ask us for a new quotation", "মেয়াদোত্তীর্ণ - নতুন কোটেশনের জন্য যোগাযোগ করুন"),
    "superseded": ("Replaced by a newer version", "নতুন সংস্করণ দ্বারা প্রতিস্থাপিত"),
    "cancelled": ("Withdrawn", "প্রত্যাহার করা হয়েছে"),
}


def _money(value):
    return f"{value or 0.0:,.2f}"


class QuotationCustomerView(http.Controller):
    def _page(self, quote, message=None, error=None, status=200):
        v = quote._customer_view()
        en, bn = _STATES.get(v["state"], (v["state"], v["state"]))
        rows = []
        for ln in v["lines"]:
            if ln["section"]:
                rows.append(
                    '<tr class="s"><td colspan="4">%s</td></tr>' % escape(ln["description"])
                )
            else:
                rows.append(
                    "<tr><td>%s</td><td class=n>%g</td><td class=n>%s</td><td class=n>%s</td></tr>"
                    % (
                        escape(ln["description"]),
                        ln["quantity"],
                        _money(ln["unit_price"]),
                        _money(ln["subtotal"]),
                    )
                )
        terms = "".join(
            "<li>%s%s</li>"
            % (escape(en_t or ""), ("<br><span lang=bn>%s</span>" % escape(bn_t)) if bn_t else "")
            for en_t, bn_t in v["terms"]
        )
        token = escape(quote.sudo().access_token or "")
        csrf = escape(request.csrf_token())
        actions = ""
        if v["state"] == "sent":
            actions = (
                '<form method="post" action="/quote/view/%(t)s/code"><input type=hidden name=csrf_token value="%(c)s">'
                "<button>Send me an approval code / অনুমোদন কোড পাঠান</button></form>"
                '<form method="post" action="/quote/view/%(t)s/accept"><input type=hidden name=csrf_token value="%(c)s">'
                "<label>Code from your phone / ফোনে পাওয়া কোড <input name=code inputmode=numeric autocomplete=one-time-code required maxlength=8></label>"
                "<button>Approve / অনুমোদন করুন</button></form>"
            ) % {"t": token, "c": csrf}
        note = ""
        if message:
            note = '<p class="ok" role="status">%s</p>' % escape(message)
        if error:
            note = '<p class="err" role="alert">%s</p>' % escape(error)
        html = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>%(name)s v%(ver)s</title>
<style>body{font:16px/1.45 system-ui,sans-serif;margin:0;padding:16px;max-width:640px;color:#1b1b1b;background:#fff}
h1{font-size:20px;margin:0 0 4px}table{width:100%%;border-collapse:collapse;margin:12px 0}
td,th{border-bottom:1px solid #ddd;padding:6px 4px;text-align:left}.n{text-align:right}
tr.s td{font-weight:600;background:#f3f3f3}.tot td{font-weight:600}
button{min-height:44px;padding:8px 14px;margin:6px 0;font-size:16px}input{min-height:40px;font-size:18px;width:9em}
.ok{color:#0a5c2b}.err{color:#a10000}label{display:block;margin-top:8px}</style></head><body>
<p>%(company)s</p><h1>%(name)s v%(ver)s</h1><p>%(customer)s &middot; <strong>%(en)s</strong> / <span lang=bn>%(bn)s</span></p>
<p>Valid until / মেয়াদ: %(valid)s</p>%(note)s
<table><thead><tr><th>Item / বিবরণ</th><th class=n>Qty</th><th class=n>Unit</th><th class=n>Amount</th></tr></thead>
<tbody>%(rows)s</tbody><tfoot>
<tr><td colspan=3>Before VAT / ভ্যাট ব্যতীত</td><td class=n>%(value)s</td></tr>
<tr><td colspan=3>VAT / ভ্যাট</td><td class=n>%(vat)s</td></tr>
<tr class=tot><td colspan=3>Total %(cur)s / মোট</td><td class=n>%(total)s</td></tr></tfoot></table>
%(terms)s%(actions)s</body></html>""" % {
            "company": escape(v["company"]),
            "name": escape(v["name"]),
            "ver": v["version"],
            "customer": escape(v["customer"] or ""),
            "en": escape(en),
            "bn": escape(bn),
            "valid": escape(str(v["valid_until"] or "-")),
            "note": note,
            "rows": "".join(rows),
            "value": _money(v["value"]),
            "vat": _money(v["vat"]),
            "total": _money(v["total"]),
            "cur": escape(v["currency"] or ""),
            "terms": ("<h2>Terms / শর্তাবলি</h2><ul>%s</ul>" % terms) if terms else "",
            "actions": actions,
        }
        return request.make_response(
            html,
            headers=[
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "no-store"),
                ("X-Robots-Tag", "noindex"),
                ("Referrer-Policy", "no-referrer"),
            ],
            status=status,
        )

    def _quote(self, token):
        quote = request.env["fix.quotation"].sudo()._from_token(token)
        if not quote:
            raise request.not_found()
        return quote

    @http.route(
        "/quote/view/<string:token>", type="http", auth="public", methods=["GET"], sitemap=False
    )
    def view(self, token, **kw):
        quote = self._quote(token)
        if quote.state == "sent":
            quote._record_view()
        return self._page(quote)

    @http.route(
        "/quote/view/<string:token>/code",
        type="http",
        auth="public",
        methods=["POST"],
        sitemap=False,
    )
    def send_code(self, token, **kw):
        quote = self._quote(token)
        try:
            with request.env.cr.savepoint():
                quote.sudo().action_send_acceptance_otp()
        except (UserError, ValidationError) as exc:
            return self._page(quote, error=exc.args[0] if exc.args else str(exc), status=400)
        return self._page(
            quote, message="A code was sent to your phone. / আপনার ফোনে কোড পাঠানো হয়েছে।"
        )

    @http.route(
        "/quote/view/<string:token>/accept",
        type="http",
        auth="public",
        methods=["POST"],
        sitemap=False,
    )
    def accept(self, token, code=None, **kw):
        quote = self._quote(token)
        if quote.state != "sent":
            return self._page(
                quote, error="This quotation is no longer awaiting a decision.", status=409
            )
        if quote.valid_until and quote.valid_until < fields.Date.context_today(quote):
            return self._page(quote, error="This quotation has expired.", status=409)
        try:
            with request.env.cr.savepoint():
                res = quote.sudo().action_verify_acceptance_otp(otp=(code or "").strip())
        except (UserError, ValidationError) as exc:
            return self._page(quote, error=exc.args[0] if exc.args else str(exc), status=400)
        if isinstance(res, dict) and not res.get("verified", True):
            return self._page(quote, error=res.get("warning") or res.get("error"), status=400)
        quote.invalidate_recordset()
        return self._page(quote, message="Approved. Thank you. / অনুমোদিত। ধন্যবাদ।")
