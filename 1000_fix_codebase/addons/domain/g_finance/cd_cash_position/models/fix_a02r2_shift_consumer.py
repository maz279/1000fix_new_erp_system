# M04 shift.closed reaches M50 (A02 ERP pass 2, X5-14, 20 Nov 2026).
#
# M04 spec §12 routes shift.closed to M50; M50 FR-TRE-016 / BRU-TRE-03:
# "a shift variance above the first threshold escalates to the branch
# manager; above the second, to the Finance Manager, with the counter, the
# cashier and the value named". M04 enforces the first threshold itself (a
# variance beyond cd_front_desk.variance_tolerance_bdt cannot reconcile
# without a Branch Manager's approval). The consolidation reads the shifts
# directly (FR-TRE-014: fix_cash_position / treasury_reports), but nothing
# took the second step: no Finance Manager ever heard of a large variance.
#
# This consumer raises the M50 treasury alert (a chatter note and a to-do for
# each Accounting Administrator of the shift's company, treasury_common) once
# per shift whose variance is above the second threshold:
# cd_cash_position.shift_variance_escalation_threshold. The spec leaves the
# figure open (M50 Q-04); until finance sets it, the second threshold is the
# M04 tolerance, so every variance a Branch Manager must approve reaches
# finance too (fail towards visibility).
from odoo import api, models
from odoo.exceptions import AccessError

from .treasury_common import float_param, treasury_alert

PARAM_SHIFT_ESCALATION = "cd_cash_position.shift_variance_escalation_threshold"
M04_TOLERANCE_PARAM = "cd_front_desk.variance_tolerance_bdt"
M04_DEFAULT_TOLERANCE = 100.0


class FixA02r2TreasuryConsumers(models.AbstractModel):
    """R8 consumer of the M04 shift close (no table of its own)."""

    _name = "fix.a02r2.treasury.consumers"
    _description = "A02 Treasury Event Consumers (shift close)"

    @api.model
    def _shift_escalation_threshold(self) -> float:
        tolerance = float_param(self.env, M04_TOLERANCE_PARAM, M04_DEFAULT_TOLERANCE)
        return float_param(self.env, PARAM_SHIFT_ESCALATION, tolerance)

    @api.model
    def consume_shift_closed(self, event: dict) -> dict:
        if not self.env.su:
            raise AccessError("Treasury consumers run only from the event relay (X5-14).")
        payload = event.get("payload") or {}
        shift_id = payload.get("shift_id") or event.get("aggregate_id")
        try:
            shift = self.env["fix.cash.shift"].sudo().browse(int(shift_id or 0)).exists()
        except (TypeError, ValueError):
            shift = None
        if not shift:
            return {"escalated": False, "reason": "no cash shift"}
        variance = round(shift.variance or 0.0, 2)  # the record's, not the payload's
        threshold = self._shift_escalation_threshold()
        if abs(variance) <= threshold + 0.005:
            return {"escalated": False, "variance": variance, "threshold": threshold}
        summary = "Shift variance above the Finance Manager threshold: shift #%s" % shift.id
        note = (
            "Branch %s, shift #%s, operator %s: counted BDT %.2f against expected BDT %.2f, a "
            "variance of BDT %+.2f (second threshold BDT %.2f, BRU-TRE-03 / FR-TRE-016)."
            % (
                shift.branch_id.display_name or "-",
                shift.id,
                shift.operator_id.name or "-",
                shift.closing_counted or 0.0,
                shift.expected_closing or 0.0,
                variance,
                threshold,
            )
        )
        activities = treasury_alert(shift, summary, note)
        return {"escalated": True, "variance": variance, "notified": len(activities)}
