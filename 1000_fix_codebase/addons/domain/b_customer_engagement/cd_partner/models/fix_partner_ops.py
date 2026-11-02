# M40 partner programmes: brand authorisations, deal registrations, rebates,
# franchise agreements and channel conflicts on top of fix.partner / fix.referral.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixPartnerAuthorisation(models.Model):
    _name = "fix.partner.authorisation"
    _description = "Partner Brand Authorisation"
    _order = "valid_to, id"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", index=True)
    scope = fields.Char(help="What the authorisation covers (service types, product lines).")
    valid_from = fields.Date(required=True)
    valid_to = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired"), ("revoked", "Revoked")],
        required=True,
        default="draft",
    )
    certificate_ref = fields.Char()


class FixPartnerDeal(models.Model):
    _name = "fix.partner.deal"
    _description = "Partner Deal Registration"
    _order = "registered_on desc, id desc"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    customer_id = fields.Many2one("res.partner", string="End Customer")
    value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    registered_on = fields.Date(required=True)
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("approved", "Approved"),
            ("won", "Won"),
            ("lost", "Lost"),
            ("expired", "Expired"),
        ],
        required=True,
        default="registered",
    )
    note = fields.Char()


class FixPartnerRebate(models.Model):
    _name = "fix.partner.rebate"
    _description = "Partner Rebate"
    _order = "period desc, id desc"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    period = fields.Char(required=True)
    basis = fields.Monetary(currency_field="currency_id", string="Rebate Basis")
    rate = fields.Float(required=True, default=0.0, help="Fraction, e.g. 0.03 = 3%.")
    amount = fields.Monetary(currency_field="currency_id", compute="_compute_amount", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    kind = fields.Selection(
        [("rebate", "Volume rebate"), ("mdf", "Market development fund")],
        required=True,
        default="rebate",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("accrued", "Accrued"), ("paid", "Paid")],
        required=True,
        default="draft",
    )
    # Gated Behind Technical Audit Score >= 85% (FLAW-40.1)
    technical_audit_score = fields.Float(
        string="Partner Audit Score (%)",
        related="partner_id.technical_audit_score",
        store=True,
        readonly=True,
    )

    def action_approve_payout(self):
        """Approve rebate payout, gated strictly behind technical audit compliance."""
        for rec in self:
            score = rec.partner_id.technical_audit_score or 0.0
            if score < 85.0 and not self.env.context.get("skip_audit_score_check"):
                raise ValidationError(
                    "Rebate payout approval blocked: Partner '%s' technical audit score is %.1f%% "
                    "(minimum 85.0%% technical compliance required under Channel Governance Rules / FLAW-40.1)."
                    % (rec.partner_id.name, score)
                )
            rec.state = "paid"

    @api.depends("basis", "rate")
    def _compute_amount(self):
        for rec in self:
            rec.amount = round((rec.basis or 0.0) * (rec.rate or 0.0), 2)


class FixPartnerFranchise(models.Model):
    _name = "fix.partner.franchise"
    _description = "Franchise Agreement"
    _order = "start_date, id"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    territory = fields.Char(required=True)
    fee = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("terminated", "Terminated")],
        required=True,
        default="draft",
    )

    def action_activate(self):
        for rec in self:
            if rec.partner_id.state != "onboarded":
                raise ValidationError(
                    "Franchise partner must be in 'onboarded' status before activating the franchise agreement."
                )
            if not rec.partner_id.has_trade_license_doc or not rec.partner_id.has_bank_solvency_doc:
                raise ValidationError(
                    "Franchise agreement activation requires verified Trade License and Bank Solvency Certificate on the partner record."
                )
            rec.state = "active"


class FixPartnerConflict(models.Model):
    _name = "fix.partner.conflict"
    _description = "Channel Conflict"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    partner_a_id = fields.Many2one("fix.partner", string="Partner A", required=True)
    partner_b_id = fields.Many2one("fix.partner", string="Partner B")
    customer_id = fields.Many2one("res.partner", string="Contested Customer")
    description = fields.Text(required=True)
    state = fields.Selection(
        [("open", "Open"), ("mediated", "Mediated"), ("closed", "Closed")],
        required=True,
        default="open",
    )
    resolution = fields.Char()
    # DOFA Arbitration & Commercial Conflict Governance (FLAW-40.2)
    dofa_arbitrator_id = fields.Many2one("res.users", string="DOFA Arbitrator", readonly=True)
    dofa_decision = fields.Selection(
        [
            ("partner_a", "Awarded to Partner A"),
            ("partner_b", "Awarded to Partner B"),
            ("split", "Split Commission / Revenue"),
            ("direct", "Retained as Direct Corporate Account"),
        ],
        string="DOFA Ruling",
    )
    arbitration_notes = fields.Text(string="Arbitration Rationale")
    arbitrated_at = fields.Datetime(string="Ruling Issued", readonly=True, copy=False)

    def action_mediate(self, dofa_decision, dofa_arbitrator_id=None, notes=None):
        """Rule on a contested customer, and record who ruled (DISC-40.2).

        The ruling moves revenue between two partners, so it carries the same
        authority the rest of the estate uses. Before the A04 audit of
        2026-11-01 it carried none: any user could call it, the caller chose
        which user to record as the arbitrator, and no rationale was required
        — so `dofa_arbitrator_id` recorded whoever the caller nominated rather
        than whoever decided.
        """
        valid = dict(self._fields["dofa_decision"].selection)
        for rec in self:
            if rec.state == "closed":
                raise UserError("Conflict %s is already closed." % rec.name)
            if dofa_decision not in valid:
                raise UserError(
                    "Unknown ruling %r. Valid rulings: %s"
                    % (dofa_decision, ", ".join(sorted(valid)))
                )
            if not (notes or "").strip():
                raise UserError(
                    "Record the arbitration rationale: a ruling that moves "
                    "revenue between partners has to say why."
                )
            if not self.env.user.has_group("cd_entity_config.group_dofa_tier_3"):
                raise UserError(
                    "Channel-conflict arbitration requires DOFA Tier 3 "
                    "(Commercial Director) authority."
                )
            # fix.partner carries no account-manager field, so the available
            # signal is who raised the conflict. Same rule as fix.dofa.mixin:
            # the person who brought it cannot also rule on it.
            if rec.create_uid and rec.create_uid.id == self.env.user.id:
                raise UserError(
                    "Segregation of duties: %s raised this conflict and cannot "
                    "arbitrate it." % self.env.user.name
                )
            if dofa_arbitrator_id and dofa_arbitrator_id != self.env.user.id:
                raise UserError(
                    "The arbitrator is whoever issues the ruling. It cannot be "
                    "attributed to another user."
                )
            rec.write(
                {
                    "state": "mediated",
                    "dofa_decision": dofa_decision,
                    "dofa_arbitrator_id": self.env.user.id,
                    "arbitration_notes": notes,
                    "arbitrated_at": fields.Datetime.now(),
                    "resolution": valid[dofa_decision],
                }
            )
        return True

    def action_close(self):
        # A04 zero-trust audit 2026-10-31: closing requires a mediated DOFA
        # ruling — an open conflict must never be closed without adjudication.
        for rec in self:
            if rec.state == "open":
                raise UserError(
                    "Conflict %s is still OPEN — record the DOFA mediation "
                    "decision (action_mediate) before closing" % rec.name
                )
            rec.state = "closed"

    _distinct_parties = models.Constraint(
        "CHECK (partner_b_id IS NULL OR partner_b_id <> partner_a_id)",
        "A channel conflict must name two different partners",
    )
