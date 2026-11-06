# fix_seller_statement.py — Bilingual seller statement with ITA 2023 s.140 withholding certification.
#
# A08 remediation (B4, M53-8, BRU-REV-14/21): a statement was born "issued"
# with a typed certificate number and no payout (2,000 live synthetic rows),
# stayed editable after settlement, and its net was typed (the platform fee
# was never deducted). Now a statement is born DRAFT, is issued only for an
# executed payout run, its net is computed in the published deduction order,
# its certificate number comes from a sequence at issue, and an issued
# statement is immutable (a recalculation is an adjustment on a later one).
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

STATEMENT_FIGURES = (
    "seller_partner_id",
    "payee_type",
    "period",
    "gross_gmv",
    "commission_amount",
    "tds_withheld",
    "platform_fee",
    "clawback_amount",
    "currency_id",
    "company_id",
    "operating_unit_id",
    "date_issued",
)


class FixSellerStatement(models.Model):
    """Bilingual Seller Statement carrying statutory Income Tax Act 2023 s.140 withholding certification.
    Complying with DE-17 & P10-M02-T06."""

    _name = "fix.seller.statement"
    _description = "Seller Settlement Statement / বিক্রেতা নিষ্পত্তিপত্র"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    payee_type = fields.Selection(
        [("marketplace", "Marketplace Seller"), ("partner_referral", "Partner / Referral")],
        string="Payee Type",
        default="marketplace",
        required=True,
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
        string="TDS Withheld (ITA 2023 s.140) / উৎসে কর কর্তন (ধারা ১৪০)",
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
        string="Net Disbursed Amount / প্রদেয় নিট অর্থ",
        currency_field="currency_id",
        compute="_compute_net",
        store=True,
        help="BRU-REV-14: computed in the published deduction order — a seller is paid gross "
        "less commission, platform fee, TDS and clawbacks; a partner its commission less TDS "
        "and clawbacks.",
    )
    settled_by_id = fields.Many2one(
        "res.users", string="Settled By / নিষ্পত্তিকারী", readonly=True, copy=False
    )
    settled_at = fields.Datetime(string="Settled On / নিষ্পত্তির সময়", readonly=True, copy=False)

    withholding_cert_ref = fields.Char(
        string="Withholding Certificate Ref / প্রত্যয়নপত্র নং",
        readonly=True,
        copy=False,
        index=True,
        help="Drawn from the certificate sequence when the statement is issued; never typed.",
    )
    statutory_note = fields.Char(
        string="Statutory Certification / সংবিধিবদ্ধ প্রত্যয়ন",
        default="Certified that tax has been deducted at source under section 140 of the Income "
        "Tax Act 2023. / প্রত্যয়ন করা যাচ্ছে যে, আয়কর আইন ২০২৩ এর ধারা ১৪০ মোতাবেক উৎসে কর "
        "কর্তন করা হয়েছে।",
        readonly=True,
    )

    payout_run_id = fields.Many2one(
        "fix.payout.run", string="Payout Run / পরিশোধ চক্র", ondelete="restrict", index=True
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "settled_by_id",
            "settled_at",
            "withholding_cert_ref",
            "statutory_note",
            "payout_run_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(STATEMENT_FIGURES)
        return locked

    @api.depends(
        "gross_gmv",
        "commission_amount",
        "tds_withheld",
        "platform_fee",
        "clawback_amount",
        "payee_type",
    )
    def _compute_net(self):
        for rec in self:
            deductions = (rec.tds_withheld or 0.0) + (rec.clawback_amount or 0.0)
            if rec.payee_type == "partner_referral":
                rec.net_payable = round((rec.commission_amount or 0.0) - deductions, 2)
            else:
                rec.net_payable = round(
                    (rec.gross_gmv or 0.0)
                    - (rec.commission_amount or 0.0)
                    - (rec.platform_fee or 0.0)
                    - deductions,
                    2,
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.seller.statement")
                    or f"STM/{fields.Date.today().year}/New"
                )
            # the net is computed (BRU-REV-14): a typed figure is ignored
            vals.pop("net_payable", None)
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        vals.pop("net_payable", None)
        if not self._fix_guard_open():
            touched = set(STATEMENT_FIGURES) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "An issued statement is immutable (BRU-REV-21): a recalculation appears as "
                    "an adjustment on a later statement."
                )
        return super().write(vals)

    def action_issue_statement(self):
        """Issue a draft statement to the seller (published for the P07
        seller portal): only for a payout run whose money has moved, with the
        certificate number drawn from its sequence."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Statement %s is already %s" % (rec.name, rec.state))
            if not rec.payout_run_id or rec.payout_run_id.state != "executed":
                raise UserError(
                    "Statement %s is issued for an executed payout run only (%s): a statement "
                    "certifies money that was paid and tax that was withheld."
                    % (rec.name, rec.payout_run_id.name or "no payout run")
                )
            cert = (
                self.env["ir.sequence"].sudo().next_by_code("fix.seller.statement.tds_cert")
                or False
            )
            if not cert:
                raise UserError("The withholding certificate sequence is missing — upgrade M53.")
            rec._guarded().write(
                {"state": "issued", "withholding_cert_ref": cert, "date_issued": fields.Date.today()}
            )
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
        payout run behind it must be executed (bank confirmed)."""
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
            rec._guarded().write(
                {
                    "state": "settled",
                    "settled_by_id": self.env.user.id,
                    "settled_at": fields.Datetime.now(),
                }
            )
