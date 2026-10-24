# fix.intercompany — Inter-Company Transaction Rules & Mirror Matching (CD-M65-03).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixIntercompanyRule(models.Model):
    """Rules governing inter-company commercial transactions, transfer pricing, and mirror generation."""

    _name = "fix.intercompany.rule"
    _description = "Inter-Company Transaction Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    _code_unique = models.Constraint("UNIQUE (code)", "Intercompany rule code must be unique")

    name = fields.Char(string="Rule Name", required=True, tracking=True)
    code = fields.Char(string="Rule Code", required=True, size=20, tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    source_entity_id = fields.Many2one(
        "fix.entity", string="Selling / Supplying Entity", required=True, tracking=True
    )
    target_entity_id = fields.Many2one(
        "fix.entity", string="Purchasing / Receiving Entity", required=True, tracking=True
    )
    transaction_type = fields.Selection(
        [
            ("sale_purchase", "Goods Sale / Purchase"),
            ("shared_service", "Shared IT / Back-Office Service"),
            ("management_fee", "Management / Advisory Fee"),
            ("loan_interest", "Inter-Company Loan / Financing"),
        ],
        string="Transaction Category",
        required=True,
        default="shared_service",
        tracking=True,
    )

    auto_mirror = fields.Boolean(
        string="Auto-Mirror Generation",
        default=True,
        help="Automatically generate counterparty AP bill upon posting source AR invoice",
    )
    markup_percent = fields.Float(
        string="Transfer Pricing Markup (%)",
        default=5.0,
        help="Arm's length markup percentage compliant with NBR regulations",
    )
    transfer_pricing_compliant = fields.Boolean(
        string="Transfer Pricing Compliant (ITA 2023 s.107)",
        default=True,
        help="Certifies arm's length transfer pricing documentation is maintained on file",
    )
    documentation_ref = fields.Char(string="TP Documentation Ref", default="TP-M65-2026-001")
    active = fields.Boolean(default=True)

    @api.constrains("source_entity_id", "target_entity_id")
    def _check_different_entities(self):
        for rec in self:
            if (
                rec.source_entity_id
                and rec.target_entity_id
                and rec.source_entity_id == rec.target_entity_id
            ):
                raise ValidationError("Source and target entities must be distinct legal entities.")


class FixIntercompanyTransaction(models.Model):
    """Recorded inter-company transaction tracked for settlement and consolidation elimination."""

    _name = "fix.intercompany.transaction"
    _description = "Inter-Company Transaction"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "transaction_date desc, id desc"

    _ref_unique = models.Constraint(
        "UNIQUE (reference)", "Intercompany transaction reference must be unique"
    )

    name = fields.Char(string="Description", required=True)
    reference = fields.Char(
        string="Transaction Ref",
        required=True,
        size=32,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.intercompany.tx")
        or "IC-TXN-2026",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    rule_id = fields.Many2one("fix.intercompany.rule", string="Applicable Rule")
    source_entity_id = fields.Many2one("fix.entity", string="Originating Entity", required=True)
    target_entity_id = fields.Many2one("fix.entity", string="Counterparty Entity", required=True)
    transaction_date = fields.Date(string="Date", default=fields.Date.context_today)
    amount = fields.Monetary(string="Transaction Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False),
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending_matching", "Pending Counterparty Match"),
            ("matched", "Matched & Reconciled"),
            ("settled", "Settled"),
            ("disputed", "Disputed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    matched_date = fields.Datetime(string="Matched Timestamp")
    mirror_invoice_ref = fields.Char(string="Mirror Bill Reference")

    def action_generate_mirror(self):
        """Generate corresponding counterparty AP mirror reference."""
        self.ensure_one()
        if not self.mirror_invoice_ref:
            mirror_ref = f"MIRROR-AP-{self.reference}"
            self.write(
                {
                    "mirror_invoice_ref": mirror_ref,
                    "state": "pending_matching",
                }
            )
        return True

    def action_match(self):
        """Match and confirm reconciliation between both entities."""
        self.ensure_one()
        self.write(
            {
                "state": "matched",
                "matched_date": fields.Datetime.now(),
            }
        )
        return True
