# Settlement statement API — the P07 seller surface owned by the
# settlement module (PP5). fix.commission.ledger is the system of
# record for seller earnings; gross/commission/TDS/net are
# backend-computed BN-007 strings (AS-10) and the payout state ships
# with each line — a held payout is visible with its state, never
# explained away (AS-09 applies to statements as much as money).

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from odoo import http
from odoo.http import request


def _fmt_bdt(amount):
    """BN-007 South Asian grouping — the portal receives the string (AS-10).

    Rounded half-up to the paisa BEFORE splitting (the float split printed
    999.999 as "999.00" and -1234.5 as "-1,2340.50")."""
    try:
        value = Decimal(str(amount)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    except (TypeError, ValueError, InvalidOperation):
        return "0.00"
    sign = "-" if value < 0 else ""
    whole, frac = f"{abs(value):.2f}".split(".")
    if len(whole) > 3:
        rest, last3 = whole[:-3], whole[-3:]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        parts.insert(0, rest)
        whole = ",".join(parts) + "," + last3
    return f"{sign}{whole}.{frac}"


class SettlementApiController(http.Controller):
    """The seller settlement statement API (P07, owned here)."""

    @http.route("/seller/settlements", type="jsonrpc", auth="user", readonly=True)
    def seller_settlements(self, **kwargs):
        """The seller's commission statement lines + totals, newest first.
        `partner_id` scopes the statement to the seller's party; without
        it the session partner is used (EA-05).
        Anti-IDOR: Portal users cannot view another partner's statements."""
        user = request.env.user
        partner_id = kwargs.get("partner_id")
        if not partner_id:
            partner_id = request.env.user.partner_id.id
        else:
            try:
                partner_id = int(partner_id)
            except (TypeError, ValueError):
                return {"error": {"code": "bad_request", "message": "partner_id must be an id"}}
            # The old elif was unreachable (it re-tested the group the first
            # branch had excluded), so a portal user's foreign partner_id was
            # silently swapped instead of refused. Refuse it explicitly.
            if partner_id != user.partner_id.id and not user.has_group("base.group_user"):
                return {
                    "error": {"code": "access_denied", "message": "Cross-tenant access forbidden"}
                }
        rows = request.env["fix.commission.ledger"].search(
            [("seller_partner_id", "=", partner_id)], limit=100, order="id desc"
        )
        lines = [
            {
                "ref": r.name,
                "source_ref": r.source_ref or "",
                "gross_bdt": _fmt_bdt(r.gross_amount),
                "commission_bdt": _fmt_bdt(r.commission_amount),
                "tds_bdt": _fmt_bdt(r.tds_amount),
                "net_bdt": _fmt_bdt(r.net_payable),
                "state": r.state,
            }
            for r in rows
        ]
        net_total = sum((Decimal(str(r.net_payable)) for r in rows), Decimal("0"))
        return {
            "settlements": {
                "lines": lines,
                "net_total_bdt": _fmt_bdt(net_total),
            }
        }
