# fix_grc_dsr_api — the PDPA data-subject-request intake (A10 deep audit
# 2026-11-23, D-A10-9).
#
# The 30-day DSR clock existed (fix.grc.pdpa + cron_dsr_overdue) but NOTHING
# created a request automatically: the register had no producer anywhere in
# the estate (M33 is data recovery, not data-subject requests; the contact
# centre classifies no DSR intent). A request arriving at a branch or the
# contact centre had to be retyped by a Compliance Officer — or was lost.
#
# This route is the intake: any authenticated internal user files the request;
# the register opens with received_on=today, which derives the 30-day SLA and
# arms the daily overdue clock. Filing is not disposition — fulfil/refuse stay
# the Compliance Officer's acts (A10 R1).
import logging

from odoo import fields, http
from odoo.http import request

from libs.py.fix_api_edge import api_edge

_logger = logging.getLogger(__name__)

REQUEST_TYPES = ("access", "erasure", "correction", "portability", "objection")


class FixGrcDsrApi(http.Controller):
    @api_edge("/api/pdpa/dsr")
    @http.route("/api/pdpa/dsr", type="json", auth="user", methods=["POST"])
    def create_dsr(self, request_type=None, subject_name=None, contact=None, notes=None):
        user = request.env.user
        if not user or user._is_public():
            return {"error": "unauthenticated", "message": "Authentication is required"}
        if request_type not in REQUEST_TYPES:
            return {
                "error": "invalid_type",
                "message": "request_type must be one of: %s" % ", ".join(REQUEST_TYPES),
            }
        if not (subject_name or "").strip():
            return {"error": "missing_subject", "message": "Name the data subject"}
        dsr = (
            request.env["fix.grc.pdpa"]
            .sudo()
            .create(
                {
                    "request_type": request_type,
                    "subject_name": subject_name.strip()[:200],
                    "received_on": fields.Date.context_today(request.env["fix.grc.pdpa"]),
                    "notes": "Filed through the intake API by %s. Contact: %s. %s"
                    % (user.name, (contact or "—")[:120], (notes or "")[:400]),
                }
            )
        )
        dsr.message_post(
            body="Data-subject request received (%s) and filed by %s. The 30-day clock is "
            "running; a Compliance Officer records the outcome." % (request_type, user.name)
        )
        return {
            "id": dsr.id,
            "name": dsr.name,
            "due_on": str(dsr.due_on),
            "state": dsr.outcome,
            "message": "Request filed; the 30-day PDPA window closes on %s." % dsr.due_on,
        }
