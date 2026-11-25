# The customer's own rating of the counter handover (A02 pass 2, M04-06).
#
# FR-FRD-029 asks the CUSTOMER for a quick 1-5 rating at the counter. The
# staff being rated typed it. The counter now opens a one-time link for the
# order (fix.service.order.action_request_counter_rating) on the counter
# tablet or the customer's phone; this page takes the stars and a comment,
# once, and the link closes. The token is the only key: it is random, single
# use and expires (cd_front_desk.counter_rating_link_hours, default 24).
from html import escape

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

_PAGE = """<!doctype html>
<html lang="bn"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>1000FiX — Rate our service</title>
<style>
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;padding:24px 16px;
background:#f6f7f9;color:#1d2433}
main{max-width:480px;margin:0 auto;background:#fff;border-radius:12px;padding:24px;
box-shadow:0 1px 3px rgba(0,0,0,.08)}
h1{font-size:20px;margin:0 0 8px}p{margin:0 0 16px;line-height:1.5}
.stars{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.stars button{min-width:52px;min-height:52px;font-size:20px;border:1px solid #c7ccd6;
border-radius:10px;background:#fff;cursor:pointer}
.stars button:focus{outline:2px solid #1f6feb;outline-offset:2px}
textarea{width:100%%;min-height:80px;box-sizing:border-box;border:1px solid #c7ccd6;
border-radius:8px;padding:8px;font:inherit}
</style></head><body><main>%s</main></body></html>"""


def _page(body):
    return request.make_response(
        _PAGE % body, headers=[("Content-Type", "text/html; charset=utf-8")]
    )


class CounterRatingController(http.Controller):
    @http.route(
        "/fix/counter-rating/<string:token>",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,
        sitemap=False,
    )
    def counter_rating(self, token, rating=None, feedback=None, **_kw):
        Order = request.env["fix.service.order"].sudo()
        if request.httprequest.method == "POST":
            try:
                Order._fd_take_customer_rating(token, rating, feedback)
            except UserError as exc:
                return _page("<h1>Thank you</h1><p>%s</p>" % escape(str(exc.args[0])))
            return _page(
                "<h1>ধন্যবাদ — Thank you</h1><p>Your rating was recorded. We appreciate it.</p>"
            )
        order = Order._fd_order_for_rating(token)
        if not order:
            return _page("<h1>Thank you</h1><p>This rating link is no longer open.</p>")
        buttons = "".join(
            '<button type="submit" name="rating" value="%d" aria-label="%d of 5">%d ★</button>'
            % (n, n, n)
            for n in range(1, 6)
        )
        return _page(
            "<h1>আমাদের সেবা কেমন ছিল? How was our service?</h1>"
            "<p>Order %s. Tap 1 (poor) to 5 (excellent).</p>"
            '<form method="post">'
            '<label for="fb">Comment (optional)</label>'
            '<textarea id="fb" name="feedback" maxlength="500"></textarea>'
            '<div class="stars" role="group" aria-label="Rating">%s</div>'
            "</form>" % (escape(order.name or ""), buttons)
        )
