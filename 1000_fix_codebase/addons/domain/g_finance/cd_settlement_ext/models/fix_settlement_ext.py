# fix_settlement_ext — M53 W7: commission ledger + payout runs (P10-M02).
from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError

from libs.py.fix_events import publish


class FixCommissionLedger(models.Model):
    """M53 W7: commission ledger consuming commission.earned events.
    The M12<->M53 break: M53 CONSUMES events; M12 never calls M53."""
    _name = "fix.commission.ledger"
    _description = "Commission Ledger Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default="New")
    seller_partner_id = fields.Many2one("res.partner", string="Seller (Party)",
                                         required=True, index=True)
    source_ref = fields.Char(string="Source Reference")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    gross_amount = fields.Monetary(string="Gross Amount",
                                    currency_field="currency_id", required=True)
    commission_rate = fields.Float(string="Commission Rate", default=0.10)
    commission_amount = fields.Monetary(string="Commission Amount",
                                        currency_field="currency_id",
                                        compute="_compute_commission", store=True)
    tds_amount = fields.Monetary(string="TDS Withheld",
                                  currency_field="currency_id")
    net_payable = fields.Monetary(string="Net Payable",
                                  currency_field="currency_id",
                                  compute="_compute_net", store=True)
    state = fields.Selection([("earned", "Earned"), ("accrued", "Accrued"),
                              ("paid", "Paid")],
                              default="earned", required=True, tracking=True)

    @api.depends("gross_amount", "commission_rate")
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = rec.gross_amount * rec.commission_rate

    @api.depends("commission_amount", "tds_amount")
    def _compute_net(self):
        for rec in self:
            rec.net_payable = rec.commission_amount - rec.tds_amount

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.commission.ledger") or "COM/New"
        return super().create(vals_list)

    def action_post_to_gl(self):
        for rec in self:
            rec.state = "accrued"
            publish(self.env, "commission.accrued", "fix.commission.ledger",
                    rec.id, {"seller": rec.seller_partner_id.name,
                             "amount": float(rec.commission_amount)})


class FixPayoutRun(models.Model):
    """Payout run: money to 500-2,000 sellers. SoD is not optional."""
    _name = "fix.payout.run"
    _description = "Payout Run"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M53",
        "form": "Payout Run",
        "fields": ["name", "period", "commission_ids"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    period = fields.Char(required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    total_payable = fields.Monetary(compute="_compute_total",
                                     string="Total Payable",
                                     currency_field="currency_id")
    total_tds = fields.Monetary(compute="_compute_total",
                                string="Total TDS Withheld",
                                currency_field="currency_id")
    state = fields.Selection([("draft", "Draft"), ("approved", "Approved"),
                              ("executed", "Executed")],
                              default="draft", required=True, tracking=True)
    prepared_by_id = fields.Many2one("res.users", string="Prepared By",
                                     default=lambda self: self.env.user,
                                     readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By",
                                     readonly=True)
    approved_date = fields.Datetime(string="Approved Date", readonly=True)
    sod_verified = fields.Boolean(string="SoD Verified", readonly=True, default=False)
    commission_ids = fields.Many2many("fix.commission.ledger",
                                       string="Commissions")

    @api.depends("commission_ids.net_payable", "commission_ids.tds_amount")
    def _compute_total(self):
        for rec in self:
            rec.total_payable = sum(rec.commission_ids.mapped("net_payable"))
            rec.total_tds = sum(rec.commission_ids.mapped("tds_amount"))

    def action_approve(self):
        """Two-person Segregation of Duties (SoD) gate.
        Rule 1: Preparer cannot approve their own payout run.
        Rule 2: Approver must possess financial managerial authority."""
        for rec in self:
            if not rec.commission_ids:
                raise UserError("No commissions in this payout run")
            if rec.prepared_by_id and self.env.user.id == rec.prepared_by_id.id:
                raise UserError("SoD Violation: Preparer cannot approve their own payout run.")
            if not (self.env.user.has_group("account.group_account_manager") or
                    self.env.user.has_group("base.group_system")):
                raise AccessError("SoD Violation: Only Finance Managers can approve payout runs.")
            rec.write({
                "state": "approved",
                "approved_by_id": self.env.user.id,
                "approved_date": fields.Datetime.now(),
                "sod_verified": True,
            })
            publish(self.env, "payout.approved", "fix.payout.run",
                    rec.id, {
                        "total": float(rec.total_payable),
                        "tds": float(rec.total_tds),
                        "approved_by": self.env.user.name,
                    })

    def action_execute(self):
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve before executing")
            rec.state = "executed"
            rec.commission_ids.write({"state": "paid"})
            publish(self.env, "payout.executed", "fix.payout.run",
                    rec.id, {
                        "sellers": len(rec.commission_ids),
                        "total_disbursed": float(rec.total_payable),
                        "tds_withheld": float(rec.total_tds),
                    })
