# m09_device — A07 P1 (2026-11-04), probe m17_71 (D8): device.transferred and
# device.warranty_updated reach the M09 warranty claims they affect.
#
# A warranty claim's evidence pack (purchase proof, serial) and its cover were
# assembled against the device as it was. When the device then changes owner
# or warranty in M17, an open claim (draft / ready) was still submitted to the
# brand on the old facts, and the brand rejects such a claim (T05: an
# incomplete claim is a rejected claim). Each open claim of the device is now
# put on a re-check: submission is refused until the claims officer confirms
# the evidence and cover against the device as it now is, with a note.
#
# device.registered has no consumer here on purpose: a device that has just
# been registered has no claim, and the other readers of a registration (M01
# intake, the party view) read the device itself.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import event_source

OPEN_CLAIM_STATES = ("draft", "ready")
_RECHECK_FIELDS = {
    "device_recheck_required",
    "device_recheck_reason",
    "device_recheck_since",
    "device_recheck_confirmed_by_id",
    "device_recheck_confirmed_on",
}


def _warranty_label(device):
    latest = device.warranty_id.sorted("id")[-1:]
    if not latest:
        return "warranty removed"
    return "warranty changed (latest: %s, %s to %s)" % (
        latest.status or "-",
        latest.start_date or "-",
        latest.end_date or "-",
    )


class FixWarrantyClaimBridge(models.Model):
    _inherit = "fix.warranty.claim"

    device_recheck_required = fields.Boolean(
        string="Device Changed: Re-check", readonly=True, copy=False, index=True
    )
    device_recheck_reason = fields.Text(string="Device Changes", readonly=True, copy=False)
    device_recheck_since = fields.Datetime(readonly=True, copy=False)
    device_recheck_confirmed_by_id = fields.Many2one(
        "res.users", string="Re-checked By", readonly=True, copy=False
    )
    device_recheck_confirmed_on = fields.Datetime(string="Re-checked On", readonly=True, copy=False)

    def write(self, vals):
        if not self.env.su and _RECHECK_FIELDS & set(vals):
            raise UserError(
                "The device re-check of a claim is set by M17 changes and cleared by "
                "Confirm Device Re-check only."
            )
        return super().write(vals)

    def action_submit(self):
        for claim in self:
            if claim.device_recheck_required:
                raise UserError(
                    "Claim %s: the device changed after the claim was assembled (%s). Confirm "
                    "the evidence pack and the cover against the device as it now is (Confirm "
                    "Device Re-check) before submitting."
                    % (
                        claim.claim_no,
                        (claim.device_recheck_reason or "").strip().splitlines()[-1:],
                    )
                )
        return super().action_submit()

    def action_confirm_device_recheck(self, note=None):
        """The claims officer re-checked purchase proof, owner and cover."""
        text = (note or "").strip()
        if not text:
            raise UserError("Say what was re-checked (owner, purchase proof, cover).")
        for claim in self:
            if not claim.device_recheck_required:
                raise UserError("Claim %s has no device change to re-check." % claim.claim_no)
            if claim.state not in OPEN_CLAIM_STATES:
                raise UserError("Claim %s is no longer open." % claim.claim_no)
            claim.sudo().write(
                {
                    "device_recheck_required": False,
                    "device_recheck_confirmed_by_id": self.env.uid,
                    "device_recheck_confirmed_on": fields.Datetime.now(),
                }
            )
            claim.message_post(body="Device re-checked by %s: %s" % (self.env.user.name, text))
        return True

    @api.model
    def _bridge_flag_claims(self, event, what):
        device = event_source(self.env, event, "fix.device")
        if not device:
            return self.browse()
        claims = self.sudo().search(
            [("device_id", "=", device.id), ("state", "in", OPEN_CLAIM_STATES)]
        )
        tag = "[%s]" % (event.get("event_id") or "")
        for claim in claims:
            if tag != "[]" and tag in (claim.device_recheck_reason or ""):
                continue  # redelivery
            line = "%s %s %s" % (
                fields.Datetime.now().strftime("%Y-%m-%d %H:%M"),
                tag,
                what(device),
            )
            claim.write(
                {
                    "device_recheck_required": True,
                    "device_recheck_reason": "%s\n%s" % (claim.device_recheck_reason or "", line),
                    "device_recheck_since": claim.device_recheck_since
                    if claim.device_recheck_required
                    else fields.Datetime.now(),
                }
            )
            claim.message_post(body="M17: %s. Re-check before submitting." % what(device))
        return claims

    @api.model
    def consume_device_transferred(self, event):
        """device.transferred -> open claims of the device need a re-check."""
        return self._bridge_flag_claims(
            event,
            lambda d: "owner changed to %s" % (d.owner_id.display_name or "nobody"),
        )

    @api.model
    def consume_device_warranty_updated(self, event):
        """device.warranty_updated -> open claims of the device need a re-check."""
        return self._bridge_flag_claims(
            event,
            _warranty_label,
        )
