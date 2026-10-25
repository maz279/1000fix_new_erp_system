# fix_seller_statement.py — Bilingual seller statement with ITA 2023 §52 withholding certification.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish


class FixSellerStatement(models.Model):
    """Bilingual Seller Statement carrying statutory Income Tax Act 2023 §52 withholding certification.
    Complying with DE-17 & P10-M02-T06."""

    _name = "fix.seller.statement"
    _description = "Seller Settlement Statement / বিক্রেতা নিষ্পত্তিপত্র"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

    name = fields.Char(
        string="Statement ID / বিবরণী নং", required=True, copy=False, readonly=True, default="New"
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit / অপারেটিং ইউনিট")
    seller_partner_id = fields.Many2one(
        "res.partner", string="Seller / বিক্রেতা", required=True, index=True
    )
    period = fields.Char(string="Settlement Period / নিষ্পত্তির মেয়াদ", required=True, index=True)
    date_issued = fields.Date(string="Issue Date / ইস্যু তারিখ", default=fields.Date.context_today)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )

    # Financial figures (English + Bengali)
    gross_gmv = fields.Monetary(
        string="Gross Marketplace Sales / মোট বিক্রয় মূল্য",
        currency_field="currency_id",
        required=True,
    )
    commission_amount = fields.Monetary(
        string="Platform Commission / প্ল্যাটফর্ম কমিশন", currency_field="currency_id", required=True
    )
    tds_withheld = fields.Monetary(
        string="TDS Withheld (ITA 2023 §52) / উৎসে কর কর্তন (ধারা ৫২)",
        currency_field="currency_id",
        required=True,
    )
    platform_fee = fields.Monetary(
        string="Platform Processing Fee / প্ল্যাটফর্ম ফি", currency_field="currency_id", default=0.0
    )
    clawback_amount = fields.Monetary(
        string="Clawback Recovered / ফেরত আদায়", currency_field="currency_id", default=0.0
    )
    net_payable = fields.Monetary(
        string="Net Disbursed Amount / প্রদেয় নিট অর্থ", currency_field="currency_id", required=True
    )
    settled_by_id = fields.Many2one(
        "res.users", string="Settled By / নিষ্পত্তিকারী", readonly=True, copy=False
    )
    settled_at = fields.Datetime(string="Settled On / নিষ্পত্তির সময়", readonly=True, copy=False)

    withholding_cert_ref = fields.Char(
        string="Withholding Certificate Ref / প্রত্যয়নপত্র নং", required=True, index=True
    )
    statutory_note = fields.Char(
        string="Statutory Certification / সংবিধিবদ্ধ প্রত্যয়ন",
        default="Certified that tax has been deducted at source under Section 52 of the Income Tax Act 2023. / "
        "প্রত্যয়ন করা যাচ্ছে যে, আয়কর আইন ২০২৩ এর ধারা ৫২ মোতাবেক উৎসে কর কর্তন করা হয়েছে।",
        readonly=True,
    )

    payout_run_id = fields.Many2one(
        "fix.payout.run", string="Payout Run / পরিশোধ চক্র", ondelete="cascade", index=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft / খসড়া"),
            ("issued", "Issued / প্রদানকৃত"),
            ("settled", "Settled / নিষ্পত্তিকৃত"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.seller.statement")
                    or f"STM/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    def action_issue_statement(self):
        """Issue a draft statement to the seller (published for the P07
        seller portal)."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Statement %s is already %s" % (rec.name, rec.state))
            rec.state = "issued"
            publish(
                self.env,
                "seller.statement_issued",
                "fix.seller.statement",
                rec.id,
                {
                    "statement_ref": rec.name,
                    "seller": rec.seller_partner_id.name,
                    "period": rec.period,
                    "gross_gmv": float(rec.gross_gmv),
                    "tds_withheld": float(rec.tds_withheld),
                    "net_disbursed": float(rec.net_payable),
                    "cert_ref": rec.withholding_cert_ref,
                },
            )

    def action_settle_statement(self):
        """Close an issued statement once its money has really moved: the
        payout run behind it must be executed (bank / rail confirmed)."""
        for rec in self:
            if rec.state != "issued":
                raise UserError(
                    "Only an issued statement can be settled (%s is %s)" % (rec.name, rec.state)
                )
            if not rec.payout_run_id or rec.payout_run_id.state != "executed":
                raise UserError(
                    "Statement %s cannot be settled: its payout run is not confirmed as paid "
                    "(%s)" % (rec.name, rec.payout_run_id.name or "no payout run")
                )
            rec.write(
                {
                    "state": "settled",
                    "settled_by_id": self.env.user.id,
                    "settled_at": fields.Datetime.now(),
                }
            )
