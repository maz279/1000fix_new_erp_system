# fix_import_ops — M44: proforma invoices, letters of credit and LCA, HS
# classification, IRC eligibility, shipping documents, arrivals, bills of entry
# with the duty cascade, and landed-cost sheets. The import order itself lives
# in fix_import_order.py.
from odoo import api, fields, models
from odoo.exceptions import UserError

_DUTY_FIELDS = ("cd_amount", "rd_amount", "sd_amount", "vat_amount", "at_amount", "ait_amount")


class FixImportOrderExtend(models.Model):
    _inherit = "fix.import.order"

    incoterm = fields.Selection(
        [
            ("fob", "FOB — Free on Board"),
            ("cif", "CIF — Cost, Insurance & Freight"),
            ("cfr", "CFR — Cost & Freight"),
            ("exw", "EXW — Ex Works"),
            ("ddp", "DDP — Delivered Duty Paid"),
        ],
        default="fob",
    )
    fx_rate = fields.Float(string="FX Rate (BDT per unit)", default=1.0)
    shipment_mode = fields.Selection(
        [("sea", "Sea Freight"), ("air", "Air Freight"), ("courier", "Courier")],
        default="sea",
    )


class FixImportProforma(models.Model):
    _name = "fix.import.proforma"
    _rec_name = "proforma_no"
    _description = "Proforma Invoice"
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    proforma_no = fields.Char(string="Proforma No", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date()
    state = fields.Selection(
        [("received", "Received"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="received",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.import.proforma") or "IPF/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            rec.state = "approved"


class FixImportLc(models.Model):
    _name = "fix.import.lc"
    _rec_name = "lc_no"
    _description = "Letter of Credit"
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    lc_no = fields.Char(string="LC No", required=True)
    bank = fields.Char(string="Issuing Bank")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="LC Amount", currency_field="currency_id")
    opened_on = fields.Date(default=fields.Date.context_today)
    expiry = fields.Date()
    margin_pct = fields.Float(string="Margin %", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("applied", "Applied"),
            ("opened", "Opened"),
            ("amended", "Amended"),
            ("closed", "Closed"),
        ],
        required=True,
        default="draft",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.import.lc") or "ILC/New"
        return super().create(vals_list)

    def action_apply(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Apply a draft LC")
            rec.state = "applied"

    def action_open(self):
        for rec in self:
            if rec.state not in ("applied", "amended"):
                raise UserError("Open an applied LC")
            rec.write({"state": "opened", "opened_on": fields.Date.context_today(self)})

    def action_close(self):
        for rec in self:
            if rec.state != "opened":
                raise UserError("Close an opened LC")
            rec.state = "closed"


class FixImportLca(models.Model):
    _name = "fix.import.lca"
    _rec_name = "lca_no"
    _description = "Letter of Credit Authorisation"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    lc_id = fields.Many2one(
        "fix.import.lc", string="Letter of Credit", required=True, ondelete="cascade", index=True
    )
    lca_no = fields.Char(string="LCA No", required=True)
    bank = fields.Char(string="Dealer Bank")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    state = fields.Selection(
        [("applied", "Applied"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="applied",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.import.lca") or "ILCA/New"
        return super().create(vals_list)

    def action_approve(self):
        for rec in self:
            if rec.state != "applied":
                raise UserError("Approve an applied LCA")
            rec.state = "approved"


class FixImportHs(models.Model):
    _name = "fix.import.hs"
    _rec_name = "hs_code"
    _description = "HS Classification"
    _order = "hs_code"

    name = fields.Char(required=True, default="New")
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="cascade", index=True
    )
    hs_code = fields.Char(string="HS Code", required=True)
    description = fields.Char()
    cd_pct = fields.Float(string="Customs Duty %", default=0.0)
    rd_pct = fields.Float(string="Regulatory Duty %", default=0.0)
    sd_pct = fields.Float(string="Supplementary Duty %", default=0.0)
    vat_pct = fields.Float(string="VAT %", default=15.0)
    at_pct = fields.Float(string="Advance Tax %", default=0.0)
    ait_pct = fields.Float(string="AIT %", default=0.0)
    ruling_ref = fields.Char(string="Ruling Reference")
    state = fields.Selection(
        [("draft", "Draft"), ("ruled", "Ruled")], required=True, default="draft"
    )

    _product_unique = models.Constraint("UNIQUE (product_id)", "One HS classification per product")
    _rates_range = models.Constraint(
        "CHECK (cd_pct >= 0 AND rd_pct >= 0 AND sd_pct >= 0 AND vat_pct >= 0 "
        "AND at_pct >= 0 AND ait_pct >= 0)",
        "Duty and tax rates cannot be negative",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.import.hs") or "IHS/New"
        return super().create(vals_list)

    def action_rule(self):
        for rec in self:
            if not rec.hs_code:
                raise UserError("Record the HS code before ruling")
            rec.write({"state": "ruled"})


class FixImportIrc(models.Model):
    _name = "fix.import.irc"
    _rec_name = "irc_no"
    _description = "Import Registration Certificate"
    _order = "valid_to desc, id desc"

    name = fields.Char(required=True, default="New")
    irc_no = fields.Char(string="IRC No", required=True)
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    restrictions = fields.Text(string="Restricted Items / Conditions")
    state = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired"), ("suspended", "Suspended")],
        required=True,
        default="valid",
    )
    is_valid = fields.Boolean(compute="_compute_is_valid", store=True)

    @api.depends("state", "valid_to")
    def _compute_is_valid(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_valid = bool(
                rec.state == "valid" and (not rec.valid_to or rec.valid_to >= today)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.import.irc") or "IIRC/New"
        return super().create(vals_list)


class FixImportShipdoc(models.Model):
    _name = "fix.import.shipdoc"
    _rec_name = "ref"
    _description = "Shipping Document"
    _order = "received_on desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    doc_type = fields.Selection(
        [
            ("bl", "Bill of Lading"),
            ("invoice", "Commercial Invoice"),
            ("packing", "Packing List"),
            ("coo", "Certificate of Origin"),
            ("insurance", "Insurance Certificate"),
            ("other", "Other"),
        ],
        required=True,
        default="bl",
    )
    ref = fields.Char(string="Document Reference")
    received_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("pending", "Pending"), ("received", "Received"), ("verified", "Verified")],
        required=True,
        default="pending",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.import.shipdoc") or "ISD/New"
                )
        return super().create(vals_list)

    def action_receive(self):
        for rec in self:
            if rec.state != "pending":
                raise UserError("Receive a pending document")
            rec.state = "received"


class FixImportArrival(models.Model):
    _name = "fix.import.arrival"
    _description = "Shipment Arrival"
    _order = "eta desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    vessel = fields.Char(string="Vessel / Flight")
    bl_no = fields.Char(string="B/L No")
    port = fields.Char(string="Port", default="Chattogram")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    arrival_date = fields.Date(string="Arrival")
    free_days = fields.Integer(string="Free Days", default=7)
    demurrage_days = fields.Integer(string="Demurrage Days", default=0)
    cleared_on = fields.Date(string="Cleared On")
    state = fields.Selection(
        [("in_transit", "In Transit"), ("arrived", "Arrived"), ("cleared", "Cleared")],
        required=True,
        default="in_transit",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.import.arrival") or "IARR/New"
                )
        return super().create(vals_list)

    def action_arrive(self):
        for rec in self:
            if rec.state != "in_transit":
                raise UserError("Mark an in-transit shipment arrived")
            arrival = fields.Date.context_today(self)
            late = 0
            if rec.eta and arrival > rec.eta:
                late = max((arrival - rec.eta).days - (rec.free_days or 0), 0)
            rec.write({"state": "arrived", "arrival_date": arrival, "demurrage_days": late})

    def action_clear(self):
        for rec in self:
            if rec.state != "arrived":
                raise UserError("Clear an arrived shipment")
            rec.write({"state": "cleared", "cleared_on": fields.Date.context_today(self)})


class FixImportBoe(models.Model):
    _name = "fix.import.boe"
    _rec_name = "boe_no"
    _description = "Bill of Entry"
    _order = "assessed_on desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    boe_no = fields.Char(string="Bill of Entry No", required=True)
    asycuda_ref = fields.Char(string="ASYCUDA Reference")
    assessed_on = fields.Date()
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    line_ids = fields.One2many("fix.import.boe.line", "boe_id", string="Lines")
    cd_amount = fields.Monetary(compute="_compute_totals", store=True, string="CD")
    rd_amount = fields.Monetary(compute="_compute_totals", store=True, string="RD")
    sd_amount = fields.Monetary(compute="_compute_totals", store=True, string="SD")
    vat_amount = fields.Monetary(compute="_compute_totals", store=True, string="VAT")
    at_amount = fields.Monetary(compute="_compute_totals", store=True, string="AT")
    ait_amount = fields.Monetary(compute="_compute_totals", store=True, string="AIT")
    total_tax = fields.Monetary(compute="_compute_totals", store=True, string="Total Duty & Tax")
    state = fields.Selection(
        [("draft", "Draft"), ("assessed", "Assessed"), ("paid", "Paid")],
        required=True,
        default="draft",
    )

    @api.depends(
        "line_ids.cd_amount",
        "line_ids.rd_amount",
        "line_ids.sd_amount",
        "line_ids.vat_amount",
        "line_ids.at_amount",
        "line_ids.ait_amount",
    )
    def _compute_totals(self):
        for rec in self:
            for fname in (*_DUTY_FIELDS, "total_tax"):
                if fname == "total_tax":
                    rec.total_tax = round(
                        sum(getattr(line, f) for line in rec.line_ids for f in _DUTY_FIELDS),
                        2,
                    )
                else:
                    setattr(rec, fname, round(sum(rec.line_ids.mapped(fname)), 2))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.import.boe") or "IBOE/New"
        return super().create(vals_list)

    def action_assess(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Assess a draft bill of entry")
            if not rec.line_ids:
                raise UserError("A bill of entry needs at least one line")
            for line in rec.line_ids:
                if not line.hs_id:
                    raise UserError("Every BOE line needs an HS classification before assessment")
                if (line.assessable_value or 0.0) <= 0:
                    raise UserError("Every BOE line needs a positive assessable value")
            rec.write({"state": "assessed", "assessed_on": fields.Date.context_today(self)})

    def action_pay(self):
        for rec in self:
            if rec.state != "assessed":
                raise UserError("Pay an assessed bill of entry")
            rec.state = "paid"


class FixImportBoeLine(models.Model):
    _name = "fix.import.boe.line"
    _description = "Bill of Entry Line"
    _order = "boe_id, id"

    boe_id = fields.Many2one("fix.import.boe", required=True, ondelete="cascade", index=True)
    hs_id = fields.Many2one("fix.import.hs", string="HS Classification", ondelete="restrict")
    description = fields.Char()
    assessable_value = fields.Float(string="Assessable Value")
    currency_id = fields.Many2one(related="boe_id.currency_id")
    cd_amount = fields.Monetary(compute="_compute_amounts", store=True, string="CD")
    rd_amount = fields.Monetary(compute="_compute_amounts", store=True, string="RD")
    sd_amount = fields.Monetary(compute="_compute_amounts", store=True, string="SD")
    vat_amount = fields.Monetary(compute="_compute_amounts", store=True, string="VAT")
    at_amount = fields.Monetary(compute="_compute_amounts", store=True, string="AT")
    ait_amount = fields.Monetary(compute="_compute_amounts", store=True, string="AIT")

    @api.depends("assessable_value", "hs_id")
    def _compute_amounts(self):
        for rec in self:
            base = rec.assessable_value or 0.0
            hs = rec.hs_id
            rec.cd_amount = round(base * ((hs.cd_pct or 0.0) / 100.0), 2) if hs else 0.0
            rec.rd_amount = round(base * ((hs.rd_pct or 0.0) / 100.0), 2) if hs else 0.0
            # SD is charged on the duty-inclusive value; VAT on value + CD + RD + SD
            sd = base * ((hs.sd_pct or 0.0) / 100.0) if hs else 0.0
            rec.sd_amount = round(sd, 2)
            vat_base = base + rec.cd_amount + rec.rd_amount + sd
            rec.vat_amount = round(vat_base * ((hs.vat_pct or 0.0) / 100.0), 2) if hs else 0.0
            rec.at_amount = round(base * ((hs.at_pct or 0.0) / 100.0), 2) if hs else 0.0
            rec.ait_amount = round(base * ((hs.ait_pct or 0.0) / 100.0), 2) if hs else 0.0


class FixImportLanded(models.Model):
    _name = "fix.import.landed"
    _description = "Landed Cost Sheet"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    order_id = fields.Many2one(
        "fix.import.order", string="Import Order", required=True, ondelete="cascade", index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    freight = fields.Monetary(currency_field="currency_id")
    insurance = fields.Monetary(currency_field="currency_id")
    duty = fields.Monetary(currency_field="currency_id")
    clearing_charges = fields.Monetary(currency_field="currency_id")
    other_charges = fields.Monetary(currency_field="currency_id")
    total_landed = fields.Monetary(compute="_compute_total", store=True, string="Total Landed")
    allocation_method = fields.Selection(
        [("value", "By Value"), ("qty", "By Quantity"), ("weight", "By Weight")],
        required=True,
        default="value",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("finalised", "Finalised")], required=True, default="draft"
    )

    @api.depends("freight", "insurance", "duty", "clearing_charges", "other_charges")
    def _compute_total(self):
        for rec in self:
            rec.total_landed = round(
                (rec.freight or 0.0)
                + (rec.insurance or 0.0)
                + (rec.duty or 0.0)
                + (rec.clearing_charges or 0.0)
                + (rec.other_charges or 0.0),
                2,
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.import.landed") or "ILND/New"
                )
        return super().create(vals_list)

    def action_finalise(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Finalise a draft landed-cost sheet")
            rec.state = "finalised"
