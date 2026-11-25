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
            partner_id,
            points_to_redeem,
            order_id,
        )

        account = self.env["fix.loyalty.account"].search(
            [
                ("partner_id", "=", partner_id),
                ("state", "=", "active"),
            ],
            limit=1,
        )

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

        # REQ-10.5: a points discount never exceeds 20% of the net labour
        # charges on the order, so a redemption cannot drive the repair's gross
        # margin negative. Parts and diagnostic fees are outside the cap.
        cap = self._labour_discount_cap(order_id)
        if cap is not None and discount_bdt > cap:
            return {
                "eligible": False,
                "reason": (
                    "Redemption capped: BDT %.2f exceeds 20%% of net labour "
                    "charges (BDT %.2f) on this order (REQ-10.5)." % (discount_bdt, cap)
                ),
                "discount_bdt": 0.0,
                "max_discount_bdt": round(cap, 2),
            }

        # An eligibility check is NOT a redemption: nothing is deducted or
        # applied until execute_redemption offsets a real draft invoice.
        return {
            "eligible": True,
            "redemption_mode": "invoice_offset",
            "stub_code": "STUB-M10-M11-001",
            "account_id": account.id,
            "account_no": account.name,
            "points_to_redeem": points_to_redeem,
            "discount_bdt": round(discount_bdt, 2),
            "tier": account.tier_id.name if account.tier_id else "Standard",
        }

    # REQ-10.5: the ceiling a points discount may reach on one repair order.
    _LABOUR_DISCOUNT_CAP_PCT = 0.20

    @api.model
    def _labour_discount_cap(self, order_id):
        """20% of net labour on the order's latest estimate, or None when the
        order carries no estimate to measure labour against."""
        if not order_id:
            return None
        estimate = self.env["fix.estimate"].search(
            [("order_id", "=", order_id)], order="version desc, id desc", limit=1
        )
        if not estimate or estimate.labour_total <= 0:
            return None
        return estimate.labour_total * self._LABOUR_DISCOUNT_CAP_PCT

    def _redeemable_invoice(self, partner_id, invoice_id, discount_bdt):
        """The M20 invoice the points offset: it must exist, belong to the
        redeeming customer, still be a DRAFT (an issued invoice already has
        its Mushak 6.3 - its total is fixed), carry no earlier redemption, and
        be worth at least the discount."""
        if not invoice_id:
            raise UserError(
                "Points are redeemed only against a customer invoice - "
                "no invoice was given, so nothing is deducted"
            )
        invoice = self.env["fix.ar.invoice"].browse(invoice_id).exists()
        if not invoice:
            raise UserError("Invoice %s does not exist" % invoice_id)
        if invoice.customer_id.id != partner_id:
            raise UserError("Invoice %s belongs to another customer" % invoice.display_name)
        if invoice.state != "draft":
            raise UserError(
                "Invoice %s is '%s': points offset a DRAFT invoice only"
                % (invoice.display_name, invoice.state)
            )
        if invoice.loyalty_points_redeemed or invoice.loyalty_discount_amount:
            raise UserError(
                "Invoice %s already carries a loyalty redemption" % invoice.display_name
            )
        gross = invoice.taxable_amount + invoice.vat_amount
        if discount_bdt > gross:
            raise UserError(
                "The loyalty discount (BDT %.2f) exceeds invoice %s (BDT %.2f)"
                % (discount_bdt, invoice.display_name, gross)
            )
        return invoice

    @api.model
    def execute_redemption(
        self, partner_id, order_id=None, invoice_id=None, points_to_redeem: int = 0
    ) -> dict:
        """Wave 3 (R04-M02-T08): redeem points as a discount on the customer's
        draft M20 invoice. The invoice is validated FIRST; the posted ledger
        line and the invoice offset are written in the same transaction, so
        points are never deducted without the discount landing."""
        eligibility = self.check_redemption_eligibility(partner_id, order_id, points_to_redeem)
        if not eligibility.get("eligible"):
            raise UserError(eligibility.get("reason", "Loyalty redemption not eligible"))

        account = self.env["fix.loyalty.account"].browse(eligibility["account_id"])
        discount_bdt = eligibility["discount_bdt"]
        invoice = self._redeemable_invoice(partner_id, invoice_id, discount_bdt)

        # Post immutable audit ledger line (action_post updates account points and emits event)
        ledger_line = self.env["fix.loyalty.ledger"].create(
            {
                "account_id": account.id,
                "company_id": account.company_id.id,
                "operating_unit_id": account.operating_unit_id.id,
                "transaction_type": "redemption",
                "points": -abs(points_to_redeem),
                "service_order_id": order_id if order_id else False,
                "order_amount_bdt": discount_bdt,
                "notes": f"Redeemed {points_to_redeem} pts (BDT {discount_bdt:.2f}) "
                f"on Invoice {invoice.display_name}",
            }
        )
        ledger_line.action_post()

        # M20 billing: the discount lands on the invoice (total_payable recomputes).
        # Only these two fields, after _redeemable_invoice checked owner, state
        # and amount: a cashier redeems points without holding invoice write
        # rights (those belong to accounting users).
        invoice.sudo().write(
            {
                "loyalty_points_redeemed": points_to_redeem,
                "loyalty_discount_amount": discount_bdt,
            }
        )

        # Transition stub record state to closed
        active_stubs = self.search([("stub_code", "=", "STUB-M10-M11-001")])
        if active_stubs:
            active_stubs.write({"status": "closed"})

        logger.info(
            "STUB-M10-M11-001 CLOSED: Redeemed %d points (BDT %.2f) for Partner %s on Invoice %s.",
            points_to_redeem,
            discount_bdt,
            partner_id,
            invoice_id,
        )

        return {
            "status": "closed",
            "stub_status": "closed",
            "stub_code": "STUB-M10-M11-001",
            "partner_id": partner_id,
            "points_redeemed": points_to_redeem,
            "discount_bdt": discount_bdt,
            "account_balance_after": account.points_balance,
            "invoice_id": invoice.id,
            "invoice_total_payable": invoice.total_payable,
            "ledger_id": ledger_line.id,
        }
