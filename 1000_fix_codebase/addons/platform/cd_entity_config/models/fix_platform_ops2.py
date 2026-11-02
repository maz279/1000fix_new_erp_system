# M30 platform operations (environments, releases), M64 MDM (duplicates, xref),
# M65 localisation (payment gateways). Registered screens in the A12 fragments.
from odoo import api, fields, models
from odoo.exceptions import UserError


class FixPlatformEnvironment(models.Model):
    _name = "fix.platform.environment"
    _description = "Platform Environment"
    _order = "kind, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    kind = fields.Selection(
        [
            ("dev", "Development"),
            ("staging", "Staging"),
            ("production", "Production"),
            ("dr", "Disaster Recovery"),
        ],
        required=True,
        default="staging",
    )
    base_url = fields.Char(required=True)
    database_name = fields.Char()
    release_channel = fields.Selection(
        [("edge", "Edge"), ("stable", "Stable"), ("lts", "LTS")],
        required=True,
        default="stable",
    )
    state = fields.Selection(
        [
            ("provisioning", "Provisioning"),
            ("live", "Live"),
            ("degraded", "Degraded"),
            ("offline", "Offline"),
        ],
        required=True,
        default="live",
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    data_residency = fields.Char(default="BD-Dhaka")
    notes = fields.Char()

    _name_unique = models.Constraint("UNIQUE (name, company_id)", "Environment name is unique")


class FixPlatformRelease(models.Model):
    _name = "fix.platform.release"
    _description = "Release Coordination"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_on desc, id desc"

    version = fields.Char(required=True)
    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    environment_id = fields.Many2one("fix.platform.environment", string="Target Environment")
    planned_on = fields.Date(required=True, default=fields.Date.context_today)
    released_on = fields.Date()
    change_summary = fields.Text()
    rollback_plan = fields.Text()
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_test", "In Test"),
            ("released", "Released"),
            ("rolled_back", "Rolled Back"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )
    owner_id = fields.Many2one("res.users", string="Release Owner")

    _version_unique = models.Constraint(
        "UNIQUE (version, company_id)", "A release version is unique per company"
    )

    def action_release(self):
        for rec in self:
            if rec.state not in ("planned", "in_test"):
                raise UserError("Only a planned or in-test release can be released")
            if not (rec.rollback_plan or "").strip():
                raise UserError("A release must state its rollback plan before it ships")
            rec.write({"state": "released", "released_on": fields.Date.context_today(rec)})


class FixMdmDuplicate(models.Model):
    _name = "fix.mdm.duplicate"
    _description = "Duplicate Record Candidate"
    _order = "score desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    res_model = fields.Char(string="Master Model", required=True, index=True)
    record_a_ref = fields.Char(required=True)
    record_b_ref = fields.Char(required=True)
    score = fields.Float(help="Match score 0-100 from the detection run.")
    match_factors = fields.Char(help="Which fields matched: name, phone, TIN…")
    decision = fields.Selection(
        [
            ("pending", "Pending"),
            ("merged", "Merged"),
            ("kept_separate", "Kept Separate"),
            ("false_positive", "False Positive"),
        ],
        required=True,
        default="pending",
        tracking=True,
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By")
    decided_on = fields.Datetime()
    survivor_ref = fields.Char(help="For a merge: the record that survived.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.mdm.duplicate") or "MDM/DUP/New"
                )
        return super().create(vals_list)

    def action_merge(self):
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            rec.write(
                {
                    "decision": "merged",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                    "survivor_ref": rec.survivor_ref or rec.record_a_ref,
                }
            )

    def action_keep_separate(self):
        for rec in self:
            if rec.decision != "pending":
                raise UserError("This candidate pair is already decided")
            rec.write(
                {
                    "decision": "kept_separate",
                    "decided_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )


class FixMdmXref(models.Model):
    _name = "fix.mdm.xref"
    _description = "Cross-Reference Mapping"
    _order = "code_list, source_value"

    code_list = fields.Char(string="Code List / Domain", required=True, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source_system = fields.Char(required=True)
    source_value = fields.Char(required=True)
    canonical_value = fields.Char(required=True)
    canonical_label = fields.Char()
    confidence = fields.Selection(
        [("verified", "Verified"), ("inferred", "Inferred"), ("disputed", "Disputed")],
        required=True,
        default="verified",
    )
    active = fields.Boolean(default=True)

    _xref_unique = models.Constraint(
        "UNIQUE (code_list, source_system, source_value, company_id)",
        "A source value maps once per domain and system",
    )


class FixPaymentGateway(models.Model):
    _name = "fix.payment.gateway"
    _description = "Payment Gateway Configuration"
    _order = "provider"

    provider = fields.Char(required=True, help="Razorpay, KBZPay, eSewa, bKash, SSLCOMMERZ…")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    country_code = fields.Char(required=True, default="BD")
    mode = fields.Selection(
        [("sandbox", "Sandbox"), ("live", "Live")], required=True, default="sandbox"
    )
    currencies = fields.Char(required=True, default="BDT")
    credential_ref = fields.Char(
        string="Credential Reference",
        required=True,
        help="Pointer into the secret manager (vault://…). API keys are never stored here (SEC-101).",
    )
    settlement_cycle_days = fields.Integer(default=2)
    supports_refund = fields.Boolean(default=True)
    supports_partial_refund = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("suspended", "Suspended")],
        required=True,
        default="draft",
    )
    active = fields.Boolean(default=True)

    _provider_unique = models.Constraint(
        "UNIQUE (provider, country_code, company_id)", "A provider is configured once per country"
    )

    @api.constrains("credential_ref")
    def _check_credential_ref(self):
        for rec in self:
            if not (rec.credential_ref or "").strip().startswith("vault://"):
                raise UserError(
                    "A gateway must reference the secret manager (vault://…); "
                    "keys must never be entered here"
                )

    def action_activate(self):
        for rec in self:
            rec.state = "active"
