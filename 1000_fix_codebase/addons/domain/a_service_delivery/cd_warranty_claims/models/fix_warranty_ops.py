# M09 warranty operations: warranty transfers, recall campaigns and claim
# appeals on top of fix.warranty / .claim / .evidence / .product / .provision.
#
# A04 workflow audit (2026-11-03) M09-8/-9/-10, C2-C3 build (2026-11-04): the
# three models had no methods. An appeal was "upheld" by a free write that
# re-opened nothing, a transfer was created straight "effective" from a
# stranger to a stranger and moved no device, and a recall was created
# "completed" with 500 of 100 units covered. Each now has a lifecycle whose
# state only its actions change (fix.guarded.mixin), with the roles of
# security/cd_warranty_claims_groups.xml and segregation of duties.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_warranty_claims import CLERK_GROUP, OFFICER_GROUP, _assert_role

APPEALABLE_CLAIM_STATES = ("rejected", "partially_approved")


class FixWarrantyTransfer(models.Model):
    """A warranty follows its device to a new owner (the cover has no owner
    of its own): approved by a Claim Decision Officer other than the person
    who recorded it, then effected, which re-owns the device through M17."""

    _name = "fix.warranty.transfer"
    _description = "Warranty Transfer"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "effective_date desc, id desc"

    name = fields.Char(required=True)
    warranty_id = fields.Many2one("fix.warranty", required=True, ondelete="cascade", index=True)
    device_id = fields.Many2one(related="warranty_id.device_id", string="Device")
    from_partner_id = fields.Many2one("res.partner", string="From Customer")
    to_partner_id = fields.Many2one("res.partner", string="To Customer")
    effective_date = fields.Date(required=True)
    evidence_document_id = fields.Many2one(
        "fix.document",
        string="Transfer Evidence",
        help="The sale receipt, deed or signed hand-over the new owner accepted",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("effective", "Effective"),
            ("void", "Void"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    effected_by_id = fields.Many2one("res.users", string="Effected By", readonly=True)
    effected_at = fields.Datetime(readonly=True)
    note = fields.Char()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_at",
            "effected_by_id",
            "effected_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {
                "name",
                "warranty_id",
                "from_partner_id",
                "to_partner_id",
                "effective_date",
                "evidence_document_id",
            }
        return locked

    @api.constrains("warranty_id", "from_partner_id", "to_partner_id", "state")
    def _check_parties(self):
        for rec in self.filtered(lambda r: r.state in ("draft", "approved")):
            owner = rec.sudo().warranty_id.device_id.owner_id
            if not (rec.from_partner_id and rec.to_partner_id):
                raise ValidationError("A warranty transfer names the current and the new owner.")
            if rec.from_partner_id != owner:
                raise ValidationError(
                    "A warranty is transferred FROM the device's current owner (%s), not %s."
                    % (owner.display_name or "nobody", rec.from_partner_id.display_name)
                )
            if rec.to_partner_id == rec.from_partner_id:
                raise ValidationError("A warranty transfer needs a new owner.")

    def write(self, vals):
        if (
            not self._fix_guard_open()
            and set(vals) - {"note"}
            and self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError(
                "A warranty transfer is edited only while it is a draft; void it and "
                "record a new one."
            )
        return super().write(vals)

    def action_approve(self):
        for rec in self:
            _assert_role(self.env, OFFICER_GROUP, "Approving a warranty transfer")
            if rec.state != "draft":
                raise UserError("Only a draft warranty transfer is approved.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: the person who recorded transfer %s does not "
                    "approve it." % rec.name
                )
            rec._check_parties()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_effect(self):
        """Move the device (and so its warranty) to the new owner, through
        M17's ownership transfer and its trail."""
        for rec in self:
            _assert_role(self.env, OFFICER_GROUP, "Effecting a warranty transfer")
            if rec.state != "approved":
                raise UserError("Only an approved warranty transfer takes effect.")
            if not rec.evidence_document_id:
                raise UserError(
                    "Attach the transfer evidence the new owner accepted before %s takes "
                    "effect." % rec.name
                )
            rec._check_parties()
            device = rec.sudo().warranty_id.device_id
            # M17's own transfer writes the owner and the ownership trail
            # together. It runs as superuser after this method's own checks
            # (officer role, four-eyes approval, current owner, evidence).
            device.action_transfer_ownership(
                new_owner_id=rec.to_partner_id.id,
                transfer_type="sale",
                reason="Warranty transfer %s" % rec.name,
                evidence_document_id=rec.evidence_document_id.id,
                channel="back_office",
            )
            rec._guarded().write(
                {
                    "state": "effective",
                    "effected_by_id": self.env.uid,
                    "effected_at": fields.Datetime.now(),
                }
            )
        return True

    def action_void(self):
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Voiding a warranty transfer")
            if rec.state not in ("draft", "approved"):
                raise UserError("An effective or void transfer cannot be voided.")
            rec._guarded().write({"state": "void"})
        return True


class FixWarrantyRecall(models.Model):
    _name = "fix.warranty.recall"
    _description = "Warranty Recall Campaign"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "launched_on desc, id desc"

    name = fields.Char(required=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", index=True)
    product_ref = fields.Char(string="Product / Model Reference")
    affected_units = fields.Integer(required=True, default=0)
    covered_units = fields.Integer(
        default=0, help="Units actually contacted / serviced under the recall."
    )
    launched_on = fields.Date()
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    completed_by_id = fields.Many2one("res.users", string="Completed By", readonly=True)
    note = fields.Char()
    # A10 P1-7 (M61-4): the campaign a distributed recall bulletin becomes.
    # Set only by the event relay's consumer; manual campaigns keep it empty.
    bulletin_id = fields.Many2one(
        "fix.knowledge.bulletin",
        string="Source Bulletin",
        index=True,
        ondelete="set null",
        copy=False,
    )

    _one_campaign_per_bulletin = models.Constraint(
        "UNIQUE (bulletin_id)",
        "One recall campaign per bulletin (A10 P1-7).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "launched_on", "completed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state in ("completed", "cancelled"):
            locked |= {"affected_units", "covered_units", "brand_id", "product_ref", "name"}
        return locked

    @api.constrains("affected_units", "covered_units")
    def _check_units(self):
        for rec in self:
            if rec.affected_units < 0 or rec.covered_units < 0:
                raise ValidationError("Recall unit counts cannot be negative.")
            if rec.covered_units > rec.affected_units:
                raise ValidationError(
                    "Recall %s covers %d units of %d affected: coverage cannot exceed the "
                    "affected population." % (rec.name, rec.covered_units, rec.affected_units)
                )

    def write(self, vals):
        if (
            not self._fix_guard_open()
            and set(vals) - {"note"}
            and self.filtered(lambda r: r.state in ("completed", "cancelled"))
        ):
            raise UserError("A completed or cancelled recall is closed for edits.")
        return super().write(vals)

    def action_launch(self):
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Launching a recall")
            if rec.state != "planned":
                raise UserError("Only a planned recall is launched.")
            if rec.affected_units <= 0:
                raise UserError("Record the affected units before launching recall %s." % rec.name)
            rec._guarded().write(
                {
                    "state": "active",
                    "launched_on": rec.launched_on or fields.Date.context_today(rec),
                }
            )
        return True

    def action_complete(self):
        for rec in self:
            _assert_role(self.env, OFFICER_GROUP, "Completing a recall")
            if rec.state != "active":
                raise UserError("Only an active recall is completed.")
            rec._guarded().write({"state": "completed", "completed_by_id": self.env.uid})
        return True

    def action_cancel(self):
        for rec in self:
            _assert_role(self.env, CLERK_GROUP, "Cancelling a recall")
            if rec.state not in ("planned", "active"):
                raise UserError("Only a planned or active recall is cancelled.")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixClaimAppeal(models.Model):
    """An appeal against a rejected (or partly approved) claim. Decided by a
    Claim Decision Officer who neither raised the appeal nor recorded the
    decision appealed against; an upheld appeal re-submits the claim."""

    _name = "fix.claim.appeal"
    _description = "Warranty Claim Appeal"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    claim_id = fields.Many2one("fix.warranty.claim", required=True, ondelete="cascade", index=True)
    reason = fields.Text(required=True)
    decision = fields.Selection(
        [
            ("pending", "Pending"),
            ("upheld", "Upheld (claim re-opened)"),
            ("rejected", "Appeal rejected"),
        ],
        required=True,
        default="pending",
        tracking=True,
    )
    decided_at = fields.Datetime(readonly=True)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decision_note = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "decision",
            "decided_at",
            "decided_by_id",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"claim_id"}
            if self.decision != "pending":
                locked |= {"name", "reason"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, CLERK_GROUP, "Raising a claim appeal")
        for vals in vals_list:
            claim = self.env["fix.warranty.claim"].browse(vals.get("claim_id")).exists()
            if not claim or claim.state not in APPEALABLE_CLAIM_STATES:
                raise ValidationError(
                    "Only a rejected or partly approved claim is appealed (claim %s is %s)."
                    % (claim.claim_no if claim else "?", claim.state if claim else "missing")
                )
            if claim.appeal_ids.filtered(lambda a: a.decision == "pending"):
                raise ValidationError("Claim %s already has an open appeal." % claim.claim_no)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            if "claim_id" in vals and any(r.claim_id.id != vals["claim_id"] for r in self):
                raise UserError("An appeal stays on the claim it was raised against.")
            if self.filtered(lambda r: r.decision != "pending"):
                raise UserError("A decided appeal is final.")
        return super().write(vals)

    def _assert_decider(self):
        self.ensure_one()
        _assert_role(self.env, OFFICER_GROUP, "Deciding a claim appeal")
        if self.decision != "pending":
            raise UserError("Appeal %s is already decided." % self.name)
        if self.claim_id.state not in APPEALABLE_CLAIM_STATES:
            raise UserError(
                "Claim %s is %s: it is no longer open to appeal."
                % (self.claim_id.claim_no, self.claim_id.state)
            )
        if not self.env.su and self.env.user in (
            self.create_uid | self.claim_id.sudo().decided_by_id
        ):
            raise UserError(
                "Segregation of duties: whoever raised the appeal or recorded the decision "
                "appealed against does not decide it."
            )

    def _decide(self, decision, note):
        if not (note or "").strip():
            raise UserError("Give the reason for the appeal decision.")
        for rec in self:
            rec._assert_decider()
            rec._guarded().write(
                {
                    "decision": decision,
                    "decided_at": fields.Datetime.now(),
                    "decided_by_id": self.env.uid,
                    "decision_note": note,
                }
            )
            if decision == "upheld":
                rec.claim_id._reopen_for_appeal(rec)
            publish(
                self.env,
                "warranty_claim.appeal_decided",
                "fix.warranty.claim",
                rec.claim_id.id,
                {
                    "claim_no": rec.claim_id.claim_no,
                    "appeal": rec.name,
                    "decision": decision,
                    "claim_state": rec.claim_id.state,
                },
            )
        return True

    def action_uphold(self, note=None):
        """The appeal stands: the claim goes back to the brand."""
        return self._decide("upheld", note)

    def action_reject_appeal(self, note=None):
        return self._decide("rejected", note)
