# M34 — the customer portal's complaint routes (A03 audit M34-8).
#
# cd_customer_portal had no complaint endpoint, so a customer could not raise
# one online. These routes are thin: the session decides WHO (auth="user"),
# and fix.complaint's portal_* methods decide WHAT that user may do (only
# their own partner's complaints and orders). The error shape matches
# cd_customer_portal ({"error": {"code", "message"}}).
from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request

SUBMIT_KEYS = (
    "subject",
    "description",
    "category",
    "service_order_id",
    "description_bn",
    "request_ref",
    "partner_id",
)


def _error(code, message):
    return {"error": {"code": code, "message": message}}


class CxComplaintPortal(http.Controller):
    @http.route("/customer/complaints", type="jsonrpc", auth="user", readonly=True)
    def complaints(self, partner_id=None, **kwargs):
        try:
            return {
                "complaints": request.env["fix.complaint"].portal_list_complaints(
                    partner_id=partner_id
                )
            }
        except (AccessError, UserError) as exc:
            return _error("refused", str(exc.args[0] if exc.args else exc))

    @http.route("/customer/complaints/submit", type="jsonrpc", auth="user", readonly=False)
    def submit(self, **kwargs):
        values = {k: kwargs.get(k) for k in SUBMIT_KEYS if kwargs.get(k) not in (None, "")}
        try:
            return {"complaint": request.env["fix.complaint"].portal_submit_complaint(**values)}
        except (AccessError, UserError) as exc:
            return _error("refused", str(exc.args[0] if exc.args else exc))

    @http.route("/customer/complaints/decision", type="jsonrpc", auth="user", readonly=False)
    def decision(self, complaint_id=None, accept=None, note=None, partner_id=None, **kwargs):
        try:
            return {
                "complaint": request.env["fix.complaint"].portal_complaint_decision(
                    complaint_id=complaint_id, accept=bool(accept), note=note, partner_id=partner_id
                )
            }
        except (AccessError, UserError) as exc:
            return _error("refused", str(exc.args[0] if exc.args else exc))
