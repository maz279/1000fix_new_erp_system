# fix.legal.hold — the legal-hold register (A10 D2, M24-6).
#
# The audit found a hold released by any user with the reason wiped and no
# authority recorded, after which the document was destroyed inside
# retention with no trace. The flag on fix.document is now only a shadow of
# this register: every hold is placed and released by a Records Officer with
# the matter reference and the release reason on file.
from odoo import fields, models
from odoo.exceptions import UserError


class FixLegalHold(models.Model):
    """One legal hold over one document: placed, then released."""

    _name = "fix.legal.hold"
    _description = "Legal Hold"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"
    _rec_name = "matter_ref"

    document_id = fields.Many2one(
        "fix.document", required=True, ondelete="restrict", index=True
    )
    matter_ref = fields.Char(
        required=True, tracking=True, help="The case, notice or inquiry this hold answers to"
    )
    placed_by_id = fields.Many2one("res.users", required=True, readonly=True)
    placed_on = fields.Date(required=True, readonly=True)
    released_by_id = fields.Many2one("res.users", readonly=True)
    released_on = fields.Date(readonly=True)
    release_reason = fields.Text(readonly=True)
    state = fields.Selection(
        [("held", "Held"), ("released", "Released")],
        default="held",
        required=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "placed_by_id",
            "placed_on",
            "released_by_id",
            "released_on",
            "release_reason",
            "document_id",
        }

    def action_release(self, reason: str = ""):
        """Releasing a hold is a Records decision with the reason recorded.

        This drives the DOCUMENT's own release (action_release_hold): the
        flag, the register rows and the freeze they impose must always move
        together — releasing the register row alone would leave the document
        frozen forever with no hold behind it."""
        for rec in self:
            if rec.state != "held":
                raise UserError("Hold %s was already released." % rec.matter_ref)
            if not reason or not reason.strip():
                raise UserError("State why the hold is released — the release is part of the record.")
            rec.document_id.action_release_hold(reason)
        return True
