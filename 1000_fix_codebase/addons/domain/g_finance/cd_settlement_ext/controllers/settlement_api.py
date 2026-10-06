# Settlement statement API — the P07 seller surface owned by the
# settlement module (PP5). fix.commission.ledger is the system of
# record for seller earnings; gross/commission/TDS/net are
# backend-computed BN-007 strings (AS-10) and the payout state ships
# with each line — a held payout is visible with its state, never
# explained away (AS-09 applies to statements as much as money).
from odoo import http
from odoo.http import request

import json


def _fmt_bdt(amount):
    """BN-007 South Asian grouping — the portal receives the string (AS-10)."""
    try:
        n = float(amount)
    except (TypeError, ValueError):
        return "0.00"
    whole = int(n)
    frac = f"{n - whole:.2f}"[1:]
    s = str(whole)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        return ",".join(parts) + "," + last3 + frac
    return s + frac


class SettlementApiController(http.Controller):
    """The seller settlement statement API (P07, owned here)."""

    @http.route("/seller/settlements", type="json", auth="user",
                readonly=True)
    def seller_settlements(self, **kwargs):
        """The seller's commission statement lines + totals, newest first.
        `partner_id` scopes the statement to the seller's party; without
        it the session partner is used (EA-05)."""
        partner_id = kwargs.get("partner_id")
        if not partner_id:
            partner_id = request.env.user.partner_id.id
        rows = request.env["fix.commission.ledger"].search(
            [("seller_partner_id", "=", int(partner_id))],
            limit=100, order="id desc")
        lines = [{
            "ref": r.name,
            "source_ref": r.source_ref or "",
            "gross_bdt": _fmt_bdt(r.gross_amount),
            "commission_bdt": _fmt_bdt(r.commission_amount),
            "tds_bdt": _fmt_bdt(r.tds_amount),
            "net_bdt": _fmt_bdt(r.net_payable),
            "state": r.state,
        } for r in rows]
        net_total = sum(r.net_payable for r in rows)
        return {"settlements": {
            "lines": lines,
            "net_total_bdt": _fmt_bdt(net_total),
        }}
