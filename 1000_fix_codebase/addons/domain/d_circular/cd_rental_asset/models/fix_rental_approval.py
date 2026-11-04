# fix.rental.charge.approval — the damage CHARGE against a rental customer as
# a routed M63 approval (A05 audit E5/E11, finding M13-8).
#
# The inspector typed a damage cost and the close deducted it from the
# customer's deposit, disputed or not; nobody approved the charge (DOFA
# covered only the waiver). A charge is now a request here, tiered on the
# amount charged (fix.dofa.mixin) and decided from the approver's inbox: the
# requester, the inspector who assessed the damage and whoever last moved its
# cost never decide it. The approval pins the amount; a changed cost or a new
# dispute voids it. A disputed charge holds the close until this approval -
# the approver's decision on the dispute - is granted.
#
# A request of its own, not the damage line's approval_state: the line
# already routes its WAIVER through the engine, and one record carries one
# approval at a time.
from odoo import api, fields, models
from odoo.exceptions import UserError

CHARGE_THRESHOLDS = [
    (50000.0, "tier_1"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]


class FixRentalChargeApproval(models.Model):
    _name = "fix.rental.charge.approval"
    _description = "Rental Damage Charge Approval"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "id desc"

    _approval_routed = True
    _approval_domain = "rental_damage_charge"

    name = fields.Char(compute="_compute_name", store=True)
    damage_id = fields.Many2one(
        "fix.rental.damage", required=True, readonly=True, index=True, ondelete="cascade"
    )
    reservation_id = fields.Many2one(related="damage_id.reservation_id", store=True, index=True)
    company_id = fields.Many2one(related="damage_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="damage_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="damage_id.reservation_id.customer_id", store=True)
    currency_id = fields.Many2one(related="damage_id.currency_id")
    amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="The charge put on the customer, pinned when the approval was requested",
    )

    @api.depends("damage_id", "amount")
    def _compute_name(self):
        for rec in self:
            rec.name = "Damage charge %.2f — %s" % (
                rec.amount or 0.0,
                rec.damage_id.reservation_id.name or "",
            )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {"damage_id", "amount"}

    def _dofa_thresholds(self):
        return CHARGE_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (rental damage charge)" % self._dofa_amount()

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_excluded(self):
        """The inspector who assessed the damage and whoever last changed its
        amount are excluded as well as the requester and creator."""
        excluded = super()._approval_excluded()
        damage = self.damage_id.sudo()
        return (excluded | damage.create_uid | damage.approval_amount_changed_by_id).sudo()

    def action_dofa_approve(self):
        self._dofa_route_guard()
        for rec in self:
            damage = rec.damage_id.sudo()
            if damage.create_uid and damage.create_uid in rec._dofa_acting_users():
                raise UserError(
                    "Segregation of duties: you assessed this damage and cannot approve "
                    "its charge."
                )
            if abs(damage._chargeable() - (rec.amount or 0.0)) > 0.005:
                raise UserError(
                    "The damage charge is now %.2f, not the %.2f this approval was "
                    "requested for. Request it again." % (damage._chargeable(), rec.amount)
                )
            if damage.disputed and not (
                (damage.settlement_notes or "").strip() or (rec.dofa_justification or "").strip()
            ):
                raise UserError(
                    "The customer disputes this charge: record the resolution in the "
                    "settlement notes (or the justification) before approving it."
                )
        result = super().action_dofa_approve()
        for rec in self:
            rec.damage_id._on_charge_approved(self.env.user)
        return result


class FixApprovalMatrixRental(models.Model):
    _inherit = "fix.approval.matrix"

    # A05 audit E11: lets a DoA matrix row target the M13 routed approvals.
    decision_domain = fields.Selection(
        selection_add=[
            ("rental_damage_charge", "Rental Damage Charge"),
            ("rental_damage_waiver", "Rental Damage Waiver"),
            ("rental_asset_retirement", "Rental Fleet Asset Retirement"),
        ],
        ondelete={
            "rental_damage_charge": "cascade",
            "rental_damage_waiver": "cascade",
            "rental_asset_retirement": "cascade",
        },
    )
