# fix_loyalty_stub — STUB-M10-M11-001 Cross-Wave Redemption Stub (CD-M10-01).
# Expiry: R04-M02-T08 (Wave 3). Points become spendable against M11 pricing engine & M20 billing.
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class FixLoyaltyRedemptionStub(models.Model):
    """STUB-M10-M11-001: Bridge between M10 Loyalty and M11/M20 Commercial Pricing.

    In Wave 2, loyalty points accrual rules are self-contained. Direct bill
    offset / invoice deduction connects to M11/M20 in Wave 3 (R04-M02-T08).
    This stub provides an authoritative validation interface that simulates
    and pre-qualifies redemption operations with complete audit logging.
    """
    _name = "fix.loyalty.redemption.stub"
    _description = "Cross-Wave Loyalty Redemption Stub (M10 -> M11/M20)"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # AS-03: Company and Operating Unit scoping
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )

    stub_code = fields.Char(
        string="Stub Identifier",
        default="STUB-M10-M11-001",
        readonly=True,
    )
    expiry_milestone = fields.Char(
        string="Expiry Milestone",
        default="R04-M02-T08",
        readonly=True,
    )
    status = fields.Selection(
        [("active", "Active (Wave 2)"), ("closed", "Closed (Replaced in Wave 3)")],
        default="active",
        readonly=True,
    )

    @api.model
    def check_redemption_eligibility(self, partner_id, order_id, points_to_redeem: int) -> dict:
        """Validate points redemption against a service order estimate.

        In Wave 2, logs execution under STUB-M10-M11-001 and computes BDT discount value.
        In Wave 3 (R04-M02-T08), this connects to M11 discount governance and M20 billing.
        """
        logger.warning(
            "STUB-M10-M11-001 invoked: Partner %s redeeming %d points on Order %s. Expiry at R04-M02-T08.",
            partner_id, points_to_redeem, order_id
        )

        account = self.env["fix.loyalty.account"].search([
            ("partner_id", "=", partner_id),
            ("state", "=", "active"),
        ], limit=1)

        if not account:
            return {
                "eligible": False,
                "reason": "Customer has no active loyalty account.",
                "discount_bdt": 0.0,
            }

        program = account.program_id
        if points_to_redeem < program.min_points_to_redeem:
            return {
                "eligible": False,
                "reason": f"Minimum points required to redeem is {program.min_points_to_redeem}.",
                "discount_bdt": 0.0,
            }

        if account.points_balance < points_to_redeem:
            return {
                "eligible": False,
                "reason": f"Insufficient balance: Account has {account.points_balance} points.",
                "discount_bdt": 0.0,
            }

        discount_bdt = points_to_redeem * program.bdt_per_point
        return {
            "eligible": True,
            "stub_active": True,
            "stub_code": "STUB-M10-M11-001",
            "account_id": account.id,
            "account_no": account.name,
            "points_to_redeem": points_to_redeem,
            "discount_bdt": round(discount_bdt, 2),
            "tier": account.tier_id.name if account.tier_id else "Standard",
        }
