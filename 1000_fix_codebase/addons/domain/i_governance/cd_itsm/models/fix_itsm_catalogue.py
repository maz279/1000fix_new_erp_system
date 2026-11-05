# M66 ITSM depth — service catalogue, problem management, licence register and
# the CMDB configuration items. Tickets, changes and assets live in fix_itsm.py /
# fix_itsm_ops.py.
#
# A12 workflow audit (2026-11-04) M66-10/11/13: the problem register's state
# was a plain write and "known error" needed no workaround; the licence
# register accepted more assigned seats than owned (and negative counts); a
# CMDB CI could sit "in service" on a retired asset. All four closed here.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

LICENCE_EXPIRING_DAYS = 30


class FixItsmCatalogue(models.Model):
    _name = "fix.itsm.catalogue"
    _description = "IT Service Catalogue Item"
    _order = "category, name"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    category = fields.Selection(
        [
            ("access", "Access & Accounts"),
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("network", "Network & Connectivity"),
            ("support", "Support & Advice"),
        ],
        required=True,
        default="support",
    )
    description = fields.Text()
    fulfilment_team = fields.Char()
    target_hours = fields.Float(string="Target fulfilment (hours)", default=8.0)
    cost_per_request = fields.Monetary(string="Cost per request", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    requires_approval = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code, company_id)", "Catalogue code is unique")


class FixItsmProblem(models.Model):
    _name = "fix.itsm.problem"
    _description = "IT Problem"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    title = fields.Char(required=True)
    description = fields.Text()
    root_cause = fields.Text()
    workaround = fields.Text()
    severity = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
        tracking=True,
    )
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    owner_id = fields.Many2one("res.users", string="Problem Owner")
    known_error = fields.Boolean(help="A documented cause + workaround exists.")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("investigating", "Investigating"),
            ("known_error", "Known Error"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        required=True,
        default="open",
        tracking=True,
    )
    resolved_on = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "known_error", "resolved_on"}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.itsm.problem") or "PRB/New"
        return super().create(vals_list)

    def action_investigate(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Investigate an open problem.")
            rec._guarded().write({"state": "investigating"})

    def action_known_error(self):
        """M66-10: a known error is a DOCUMENTED cause + workaround. From open
        or investigating only; both texts are required."""
        for rec in self:
            if rec.state not in ("open", "investigating"):
                raise UserError(
                    "Mark a problem as known error while it is open or under "
                    "investigation (M66-10)."
                )
            if not (rec.root_cause or "").strip():
                raise UserError("A known error needs its root cause documented first")
            if not (rec.workaround or "").strip():
                raise UserError(
                    "A known error needs its workaround documented (M66-10): the "
                    "register exists so the service desk can work around the fault."
                )
            rec._guarded().write({"state": "known_error", "known_error": True})

    def action_resolve(self):
        for rec in self:
            if rec.state not in ("investigating", "known_error"):
                raise UserError("Resolve a problem that is being investigated")
            if not (rec.root_cause or "").strip():
                raise UserError(
                    "A resolved problem names its root cause (M66-10): without it the "
                    "resolution cannot prevent recurrence."
                )
            rec._guarded().write({"state": "resolved", "resolved_on": fields.Datetime.now()})

    def action_close(self):
        for rec in self:
            if rec.state != "resolved":
                raise UserError("Close a resolved problem")
            rec._guarded().write({"state": "closed"})


class FixItsmLicence(models.Model):
    _name = "fix.itsm.licence"
    _description = "Software Licence"
    _order = "renewal_on, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    vendor = fields.Char(required=True)
    licence_type = fields.Selection(
        [
            ("per_user", "Per User"),
            ("per_device", "Per Device"),
            ("site", "Site / Enterprise"),
            ("subscription", "Subscription"),
        ],
        required=True,
        default="per_user",
    )
    seats_owned = fields.Integer(required=True, default=0)
    seats_assigned = fields.Integer(default=0)
    unit_cost = fields.Monetary(string="Unit cost", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    annual_cost = fields.Monetary(compute="_compute_cost", store=True, currency_field="currency_id")
    purchased_on = fields.Date()
    renewal_on = fields.Date()
    utilisation_pct = fields.Float(compute="_compute_utilisation", store=True)
    state = fields.Selection(
        [("active", "Active"), ("expiring", "Expiring"), ("expired", "Expired")],
        required=True,
        default="active",
        compute="_compute_state",
        store=True,
        help="M66-11: the licence status is the renewal date, not an opinion — "
        "expired once the renewal date passes, expiring within %d days of it."
        % LICENCE_EXPIRING_DAYS,
    )

    @api.depends("seats_owned", "unit_cost", "licence_type")
    def _compute_cost(self):
        for rec in self:
            if rec.licence_type == "subscription":
                rec.annual_cost = rec.unit_cost or 0.0
            else:
                rec.annual_cost = (rec.seats_owned or 0) * (rec.unit_cost or 0.0)

    @api.depends("seats_owned", "seats_assigned")
    def _compute_utilisation(self):
        for rec in self:
            rec.utilisation_pct = (
                round(100.0 * (rec.seats_assigned or 0) / rec.seats_owned, 1)
                if rec.seats_owned
                else 0.0
            )

    @api.depends("renewal_on")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.renewal_on and rec.renewal_on < today:
                rec.state = "expired"
            elif rec.renewal_on and rec.renewal_on <= fields.Date.add(
                today, days=LICENCE_EXPIRING_DAYS
            ):
                rec.state = "expiring"
            else:
                rec.state = "active"

    @api.constrains("seats_owned", "seats_assigned")
    def _check_seats(self):
        """M66-11: the register cannot show more seats in use than the company
        owns, and it owns a non-negative count."""
        for rec in self:
            if rec.seats_owned < 0:
                raise ValidationError("A licence owns a non-negative number of seats.")
            if rec.seats_assigned < 0:
                raise ValidationError("A licence has a non-negative number of seats assigned.")
            if rec.seats_assigned > rec.seats_owned:
                raise ValidationError(
                    "%s: %d seats assigned but only %d owned (M66-11). Assign fewer "
                    "seats or buy more." % (rec.name, rec.seats_assigned, rec.seats_owned)
                )


class FixItsmCi(models.Model):
    _name = "fix.itsm.ci"
    _description = "Configuration Item (CMDB)"
    _order = "ci_class, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    ci_class = fields.Selection(
        [
            ("server", "Server"),
            ("network", "Network Device"),
            ("endpoint", "Endpoint"),
            ("application", "Application"),
            ("database", "Database"),
            ("service", "Business Service"),
        ],
        required=True,
        default="server",
    )
    ci_key = fields.Char(required=True, help="Stable identifier (hostname, app key, service code).")
    environment_id = fields.Many2one("fix.platform.environment", string="Environment")
    owner_id = fields.Many2one("res.users", string="Owner")
    depends_on = fields.Char(help="Comma-separated upstream CI keys this item depends on.")
    criticality = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
        required=True,
        default="medium",
    )
    support_hours = fields.Selection(
        [("business", "Business hours"), ("extended", "Extended (07:00-23:00)"), ("24x7", "24x7")],
        required=True,
        default="business",
    )
    life_status = fields.Selection(
        [("in_service", "In Service"), ("maintenance", "Maintenance"), ("retired", "Retired")],
        required=True,
        default="in_service",
    )
    asset_id = fields.Many2one("fix.itsm.asset", string="Linked Asset")

    _ci_unique = models.Constraint("UNIQUE (ci_key, company_id)", "CI key is unique per company")

    @api.constrains("life_status", "asset_id")
    def _check_asset_life(self):
        """M66-13: nothing runs in service on retired hardware — the CMDB must
        not describe service the asset register has already ended."""
        for rec in self:
            if rec.life_status == "in_service" and rec.asset_id and rec.asset_id.state == "retired":
                raise ValidationError(
                    "CI %s is in service but its asset %s is retired (M66-13). Retire "
                    "the CI or relink it to live hardware." % (rec.ci_key, rec.asset_id.asset_tag)
                )
