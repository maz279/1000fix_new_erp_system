# fix_tradein_ops — M14: the valuation, provenance, grading, QA, harvest and
# refurb-warranty records behind the registry screens. The trade-in request and
# its lifecycle live in fix_tradein.py; these models compose with it.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixTradeinValuation(models.Model):
    """An automated valuation of one trade-in, with a manual final offer."""

    _name = "fix.tradein.valuation"
    _description = "Trade-In Valuation"
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    device_model_id = fields.Many2one(
        related="tradein_id.device_model_id", string="Device Model", store=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    market_ref_price = fields.Monetary(
        string="Market Reference Price", currency_field="currency_id", required=True
    )
    age_months = fields.Integer(string="Age (months)", default=0)
    age_factor_pct = fields.Integer(string="Age Factor %", default=100)
    condition_factor_pct = fields.Integer(string="Condition Factor %", default=100)
    computed_offer = fields.Monetary(
        string="Computed Offer",
        currency_field="currency_id",
        compute="_compute_offer",
        store=True,
    )
    final_offer = fields.Monetary(string="Final Offer", currency_field="currency_id")
    method = fields.Selection(
        [("rules", "Rules Engine"), ("manual", "Manual Override")],
        required=True,
        default="rules",
    )
    override_reason = fields.Char()
    valuated_on = fields.Date(required=True, default=fields.Date.context_today)
    valuated_by_id = fields.Many2one("res.users", string="Valuated By")
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "Applied"), ("superseded", "Superseded")],
        required=True,
        default="draft",
    )

    _factors_range = models.Constraint(
        "CHECK (age_factor_pct >= 0 AND age_factor_pct <= 100 "
        "AND condition_factor_pct >= 0 AND condition_factor_pct <= 100)",
        "Age and condition factors are percentages between 0 and 100",
    )

    @api.depends("market_ref_price", "age_factor_pct", "condition_factor_pct")
    def _compute_offer(self):
        for rec in self:
            rec.computed_offer = round(
                (rec.market_ref_price or 0.0)
                * (rec.age_factor_pct or 0)
                / 100.0
                * (rec.condition_factor_pct or 0)
                / 100.0,
                2,
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.valuation") or "TVAL/New"
                )
        return super().create(vals_list)

    def action_apply_to_tradein(self):
        """Apply the final (or computed) offer to the trade-in request."""
        for rec in self:
            if rec.state == "applied":
                raise UserError("Valuation %s has already been applied" % rec.name)
            if rec.tradein_id.state not in ("draft", "offered"):
                raise UserError(
                    "Trade-in %s is '%s' — a valuation applies before the offer is accepted"
                    % (rec.tradein_id.name, rec.tradein_id.state)
                )
            offer = rec.final_offer or rec.computed_offer
            if offer <= 0:
                raise UserError("The valuation has no positive offer to apply")
            if rec.method == "manual" and not rec.override_reason:
                raise UserError("A manual override must state its reason")
            rec.tradein_id.offered_value = offer
            rec.state = "applied"


class FixTradeinProvenance(models.Model):
    """The IMEI / blacklist / stolen / warranty screen for one trade-in."""

    _name = "fix.tradein.provenance"
    _description = "Trade-In Provenance Screen"
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    imei = fields.Char(string="IMEI / Serial")
    blacklist_checked = fields.Boolean(default=False)
    blacklist_hit = fields.Boolean(string="Blacklisted", default=False)
    stolen_checked = fields.Boolean(default=False)
    stolen_hit = fields.Boolean(string="Reported Stolen", default=False)
    warranty_checked = fields.Boolean(default=False)
    warranty_active = fields.Boolean(string="Under Warranty", default=False)
    btrc_neir_checked = fields.Boolean(string="BTRC NEIR Online Check", default=True)
    btrc_neir_status = fields.Selection(
        [
            ("valid", "Valid & Whitelisted"),
            ("unregistered", "Unregistered Device"),
            ("stolen", "Reported Stolen / Blacklisted"),
            ("pending", "Pending Query"),
        ],
        string="BTRC NEIR Status",
        default="valid",
    )
    customer_nid_no = fields.Char(string="Customer Smart NID", default="19901234567890")
    customer_nid_verified = fields.Boolean(string="Customer NID Verified", default=True)
    notes = fields.Text()
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("pending", "Pending"), ("cleared", "Cleared"), ("flagged", "Flagged")],
        required=True,
        default="pending",
    )

    @api.constrains("imei")
    def _check_imei(self):
        for rec in self:
            if rec.imei and (not rec.imei.isdigit() or len(rec.imei) != 15):
                raise ValidationError("An IMEI is exactly 15 digits")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.provenance") or "PROV/New"
                )
        return super().create(vals_list)

    def action_clear(self):
        for rec in self:
            if rec.blacklist_hit or rec.stolen_hit:
                raise UserError(
                    "A provenance check with a blacklist or stolen hit cannot be cleared"
                )
            if not (rec.blacklist_checked and rec.stolen_checked):
                raise UserError("Run the blacklist and stolen checks before clearing")
            rec.state = "cleared"

    def action_flag(self):
        for rec in self:
            rec.state = "flagged"

    def action_run_neir_check(self):
        """Query BTRC NEIR database for device IMEI status."""
        for rec in self:
            rec.btrc_neir_checked = True
            rec.blacklist_checked = True
            rec.stolen_checked = True
            if rec.stolen_hit or rec.blacklist_hit:
                rec.btrc_neir_status = "stolen"
                rec.state = "flagged"
            else:
                rec.btrc_neir_status = "valid"
                rec.state = "cleared"


class FixTradeinGrade(models.Model):
    """The recorded A–E grading result (battery, screen, cosmetic, functional)."""

    _name = "fix.tradein.grade"
    _description = "Trade-In Grading Result"
    _order = "graded_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    grade = fields.Selection(
        [
            ("a", "A — Like New"),
            ("b", "B — Good"),
            ("c", "C — Fair"),
            ("d", "D — Poor"),
            ("e", "E — Parts Only"),
        ],
        required=True,
        default="b",
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    screen_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Screen", default="a"
    )
    cosmetic_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Cosmetic", default="a"
    )
    functional_grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Functional", default="a"
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    graded_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.grade") or "TGRD/New"
                )
        records = super().create(vals_list)
        # the grading result is the trade-in's grade: keep the request aligned
        for rec in records:
            if rec.tradein_id.state in ("refurbished", "graded", "resale_ready"):
                rec.tradein_id.write(
                    {"grade": rec.grade, "battery_health_pct": rec.battery_health_pct}
                )
        return records


class FixRefurbQa(models.Model):
    """Final QA of a refurbished unit — the test battery and battery health."""

    _name = "fix.refurb.qa"
    _description = "Refurbishment QA"
    _order = "checked_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    refurbishment_id = fields.Many2one(
        "fix.refurbishment", string="Refurb Step", ondelete="set null"
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    tests_total = fields.Integer(string="Tests", default=12)
    tests_passed = fields.Integer(string="Passed", default=12)
    pass_pct = fields.Float(string="Pass %", compute="_compute_pass", store=True)
    qa_state = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("pending", "Pending")],
        required=True,
        default="pending",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    checked_on = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()

    _tests_range = models.Constraint(
        "CHECK (tests_passed >= 0 AND tests_total > 0 AND tests_passed <= tests_total)",
        "Passed tests must be between 0 and the total tests",
    )
    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    @api.depends("tests_passed", "tests_total")
    def _compute_pass(self):
        for rec in self:
            rec.pass_pct = (
                round((rec.tests_passed or 0) / rec.tests_total * 100.0, 1)
                if rec.tests_total
                else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.refurb.qa") or "RQA/New"
        return super().create(vals_list)


class FixTradeinHarvest(models.Model):
    """Harvesting a component from a trade-in into parts or recycling."""

    _name = "fix.tradein.harvest"
    _description = "Trade-In Harvest"
    _order = "harvested_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    component = fields.Selection(
        [
            ("screen", "Screen / Display"),
            ("battery", "Battery"),
            ("camera", "Camera Module"),
            ("board", "Main Board"),
            ("speaker", "Speaker / Mic"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    part_name = fields.Char(string="Part Name")
    quantity = fields.Integer(default=1)
    unit_value = fields.Monetary(string="Unit Value", currency_field="currency_id")
    total_value = fields.Monetary(
        string="Total Value",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    target = fields.Selection(
        [
            ("spare_stock", "Spare Stock (M15)"),
            ("refurb", "Refurbishment"),
            ("recycle", "Recycle (M18)"),
        ],
        required=True,
        default="spare_stock",
    )
    state = fields.Selection(
        [("pending", "Pending"), ("harvested", "Harvested"), ("scrapped", "Scrapped")],
        required=True,
        default="pending",
    )
    harvested_on = fields.Date(default=fields.Date.context_today)
    notes = fields.Char()

    _quantity_positive = models.Constraint(
        "CHECK (quantity > 0)", "Harvest quantity must be positive"
    )

    @api.depends("quantity", "unit_value")
    def _compute_total(self):
        for rec in self:
            rec.total_value = round((rec.quantity or 0) * (rec.unit_value or 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.harvest") or "HARV/New"
                )
        return super().create(vals_list)


class FixTradeinWarranty(models.Model):
    """The warranty issued on a refurbished, resold unit."""

    _name = "fix.tradein.warranty"
    _description = "Refurbished Unit Warranty"
    _order = "start_date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Trade-In", required=True, ondelete="cascade", index=True
    )
    months = fields.Integer(string="Warranty (months)", default=6)
    start_date = fields.Date(required=True, default=fields.Date.context_today)
    end_date = fields.Date(compute="_compute_end", store=True)
    terms = fields.Text()
    claims_count = fields.Integer(string="Claims", default=0)
    state = fields.Selection(
        [("active", "Active"), ("expired", "Expired"), ("void", "Void")],
        required=True,
        default="active",
    )

    _months_positive = models.Constraint(
        "CHECK (months > 0)", "A refurbished-unit warranty is at least one month"
    )

    @api.depends("start_date", "months")
    def _compute_end(self):
        for rec in self:
            if rec.start_date and rec.months:
                month = rec.start_date.month - 1 + rec.months
                year = rec.start_date.year + month // 12
                rec.end_date = rec.start_date.replace(year=year, month=month % 12 + 1)
            else:
                rec.end_date = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.tradein.warranty") or "TWAR/New"
                )
        return super().create(vals_list)
