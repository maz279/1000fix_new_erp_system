# M67 project operations depth — templates, milestone billing and the risk/issue
# register. Projects, milestones, tasks and stage gates live in fix_ppm.py.
#
# A12 workflow audit (2026-11-04) M67-1 / M67-2 / M67-8 / M67-10:
#   - "Mark invoiced" used to move a typed reference; it now CREATES the real
#     customer invoice (account.move, out_invoice) and stores it in invoice_id
#     — invoice_ref stays as a display echo of the move's name;
#   - billing has a ceiling (Σ billing ≤ contract value), cannot be edited
#     once ready, and cannot point at another project's milestone;
#   - risk closure needs mitigation evidence; an escalated or overdue risk
#     publishes project.risk_escalated for the M60 enterprise register (the
#     consumer is shipped by the lead); the overdue-risk cron flags it;
#   - instantiating a template now carries the gates, the WBS and the
#     template link/version (BRU-PPM-19).
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# Escalation thresholds (business decisions, report §7): a risk at or above
# this severity_score (probability x impact, 1..9) is escalated to the M60
# enterprise register as soon as it is opened or reaches the score. A risk
# still open after this many days is escalated by the cron whatever its score.
RISK_ESCALATION_THRESHOLD_PARAM = "fix_ppm.risk_escalation_threshold"
RISK_ESCALATION_THRESHOLD_DEFAULT = 9
RISK_OVERDUE_DAYS_PARAM = "fix_ppm.risk_overdue_days"
RISK_OVERDUE_DAYS_DEFAULT = 7


class FixProjectTemplate(models.Model):
    _name = "fix.project.template"
    _description = "Project Template"
    _order = "project_type, name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_type = fields.Selection(
        [
            ("internal", "Internal"),
            ("client", "Client Project"),
            ("infrastructure", "Infrastructure"),
        ],
        required=True,
        default="internal",
    )
    default_duration_days = fields.Integer(default=90)
    default_budget = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gate_plan = fields.Char(
        help="Comma-separated gates the project must pass, e.g. g1_initiation,g2_planning"
    )
    milestone_plan = fields.Text(help="One milestone per line, in sequence.")
    wbs_plan = fields.Text(help="One task per line; prefix with the milestone name.")
    active = fields.Boolean(default=True)

    def action_instantiate(self):
        """Creates a real project (+ its gates, milestones and tasks) from the
        template, recording which template and revision it came from."""
        self.ensure_one()
        Project = self.env["fix.project"]
        Milestone = self.env["fix.project.milestone"]
        Task = self.env["fix.project.task"]
        Gate = self.env["fix.project.gate"]
        date_end = None
        if self.default_duration_days:
            date_end = fields.Date.add(
                fields.Date.context_today(self), days=self.default_duration_days
            )
        project = Project.create(
            {
                "name": "%s — from template" % self.name,
                "project_type": self.project_type,
                "budget": self.default_budget,
                "date_start": fields.Date.context_today(self),
                "date_end": date_end,
                "state": "draft",
                "template_id": self.id,
                "template_version": (self.write_date or fields.Datetime.now()).isoformat(),
            }
        )
        milestones = {}
        for line in (self.milestone_plan or "").splitlines():
            name = line.strip()
            if name:
                milestone = Milestone.create({"project_id": project.id, "name": name})
                milestones[name] = milestone
        for line in (self.wbs_plan or "").splitlines():
            line = line.strip()
            if not line:
                continue
            milestone = None
            task_name = line
            for ms_name, ms_rec in milestones.items():
                if line.startswith(ms_name):
                    milestone = ms_rec
                    task_name = line[len(ms_name) :].lstrip(":- ")
                    break
            Task.create(
                {
                    "project_id": project.id,
                    "milestone_id": milestone.id if milestone else False,
                    "name": task_name or line,
                }
            )
        for gate_key in (self.gate_plan or "").split(","):
            gate_key = gate_key.strip()
            if gate_key:
                Gate.create({"project_id": project.id, "gate": gate_key})
        return project


class FixProjectBilling(models.Model):
    _name = "fix.project.billing"
    _description = "Milestone Billing"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "due_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    milestone_id = fields.Many2one("fix.project.milestone", string="Milestone")
    customer_id = fields.Many2one("res.partner", string="Customer")
    billing_type = fields.Selection(
        [
            ("milestone", "Milestone"),
            ("time_material", "Time & Material"),
            ("retainer", "Retainer"),
        ],
        required=True,
        default="milestone",
    )
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    due_on = fields.Date(required=True, default=fields.Date.context_today)
    invoiced_on = fields.Date()
    invoice_ref = fields.Char(
        string="Invoice Reference",
        help="Display echo of the invoice's name. The invoice itself is the "
        "account.move in Invoice; the reference is written by Mark Invoiced.",
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        readonly=True,
        copy=False,
        index=True,
        help="The real customer invoice (M20 account.move) created by Mark "
        "Invoiced. M67-1: 'invoiced' without an invoice is fiction.",
    )
    retention_pct = fields.Float(default=0.0)
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("ready", "Ready to Invoice"),
            ("invoiced", "Invoiced"),
            ("paid", "Paid"),
        ],
        required=True,
        default="planned",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "invoice_id",
            "invoiced_on",
            "invoice_ref",
        }

    def _fix_form_locked_fields(self) -> set:
        # M67-2 (bl_08): once the line is ready for invoicing, the amount and
        # the customer it was raised for are pinned.
        locked = super()._fix_form_locked_fields()
        if self and self.state in ("ready", "invoiced", "paid"):
            locked |= {"amount", "customer_id", "project_id", "milestone_id", "retention_pct"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.billing") or "BILL/New"
                )
        return super().create(vals_list)

    @api.constrains("project_id", "milestone_id")
    def _check_milestone_project(self):
        # M67-6 (bl_10): billing another project's milestone bills work the
        # project never delivered.
        for rec in self:
            if rec.milestone_id and rec.milestone_id.project_id != rec.project_id:
                raise ValidationError(
                    "The milestone %s belongs to another project: a billing line may "
                    "only bill a milestone of its own project." % rec.milestone_id.display_name
                )

    @api.constrains("amount", "retention_pct")
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0.0:
                raise ValidationError("A billing amount cannot be negative.")
            if not 0.0 <= rec.retention_pct <= 100.0:
                raise ValidationError("Retention must be between 0 and 100 %.")

    @api.constrains("amount", "project_id")
    def _check_contract_ceiling(self):
        # M67-2 (bl_02): Σ billing of the project may not exceed its approved
        # contract value. Projects with no contract value recorded are checked
        # by the DOFA budget approval instead (never both unchecked).
        for rec in self:
            project = rec.project_id
            ceiling = project.contract_value
            if not ceiling:
                continue
            # search, not the cached one2many: during create() the inverse
            # cache may not carry the line being validated yet.
            total = sum(
                self.env["fix.project.billing"]
                .with_context(active_test=False)
                .search([("project_id", "=", project.id)])
                .mapped("amount")
            )
            if total > ceiling + 0.005:
                raise ValidationError(
                    "Billing %s would take project %s to BDT %.2f of BDT %.2f contract "
                    "value: billing may not exceed the approved contract value."
                    % (rec.name, project.display_name, total, ceiling)
                )

    def write(self, vals):
        # M67-2 (bl_08): the terms are frozen from "ready" onwards.
        pinned = {"amount", "customer_id", "project_id", "milestone_id", "retention_pct"}
        if pinned & set(vals) and not self._fix_guard_open():
            frozen = self.filtered(lambda r: r.state in ("ready", "invoiced", "paid"))
            if frozen:
                raise UserError(
                    "The amount, customer, project and retention of a billing line "
                    "are frozen once it is ready to invoice (M67-2). Cancel the line "
                    "and raise a new one instead."
                )
        return super().write(vals)

    def action_mark_ready(self):
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned billing line can be marked ready")
            if rec.billing_type == "milestone":
                milestone = rec.milestone_id
                if not milestone:
                    raise UserError(
                        "A milestone billing line names no milestone: link it to the "
                        "milestone it bills."
                    )
                if milestone.state != "done" or not milestone.accepted_by_id:
                    raise UserError(
                        "Milestone %s is not an accepted, completed milestone: a "
                        "billable event is raised only on an accepted milestone "
                        "(BRU-PPM-11)." % milestone.display_name
                    )
            if not rec.customer_id:
                raise UserError("Record the customer before raising the billable event.")
            rec._guarded().write({"state": "ready"})

    def _invoice_journal(self):
        self.ensure_one()
        journal = (
            self.env["account.journal"]
            .sudo()
            .search([("type", "=", "sale"), ("company_id", "=", self.company_id.id)], limit=1)
        )
        if not journal:
            raise UserError(
                "No sale journal exists for company %s: configure one before invoicing "
                "project billing." % self.company_id.display_name
            )
        return journal

    def _invoice_line_account(self, journal):
        account = journal.default_account_id
        if not account:
            account = (
                self.env["account.account"]
                .sudo()
                .search(
                    [("account_type", "=", "income"), ("company_id", "=", self.company_id.id)],
                    limit=1,
                )
            )
        if not account:
            raise UserError(
                "No income account found for company %s: set the sale journal's default "
                "account or an income account." % self.company_id.display_name
            )
        return account

    def action_mark_invoiced(self):
        """Creates the real customer invoice (M20) and stores its id (M67-1)."""
        for rec in self:
            if rec.invoice_id:
                raise UserError("%s already carries invoice %s." % (rec.name, rec.invoice_id.name))
            if rec.state != "ready":
                raise UserError("Only a ready billing line can be invoiced")
            if not rec.customer_id:
                raise UserError("Record the customer before invoicing.")
            journal = rec._invoice_journal()
            account = rec._invoice_line_account(journal)
            # The invoice is a system-written financial hand-off (BRU-PPM-02):
            # the checks above ran as the caller, the document is created by
            # the service role, like every engine-posted journal entry.
            move = (
                self.env["account.move"]
                .sudo()
                .create(
                    {
                        "move_type": "out_invoice",
                        "partner_id": rec.customer_id.id,
                        "journal_id": journal.id,
                        "company_id": rec.company_id.id,
                        "currency_id": rec.currency_id.id,
                        "invoice_date": fields.Date.context_today(rec),
                        "ref": "%s — %s" % (rec.name, rec.project_id.display_name),
                        "invoice_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": "%s — %s" % (rec.name, rec.project_id.display_name),
                                    "account_id": account.id,
                                    "quantity": 1,
                                    "price_unit": rec.amount,
                                },
                            )
                        ],
                    }
                )
            )
            rec._guarded().write(
                {
                    "state": "invoiced",
                    "invoice_id": move.id,
                    # a DRAFT move has no sequence name yet; the echo carries
                    # its display name until posting names it (M67-1).
                    "invoice_ref": move.name or move.display_name,
                    "invoiced_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(
                body="Customer invoice %s created for BDT %.2f (account.move %d)."
                % (move.name, rec.amount, move.id)
            )


class FixProjectRisk(models.Model):
    _name = "fix.project.risk"
    _description = "Project Risk / Issue"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "opened_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    project_id = fields.Many2one(
        "fix.project", string="Project", required=True, ondelete="cascade", index=True
    )
    kind = fields.Selection([("risk", "Risk"), ("issue", "Issue")], required=True, default="risk")
    title = fields.Char(required=True)
    description = fields.Text()
    probability = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    impact = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    severity_score = fields.Integer(
        compute="_compute_severity",
        store=True,
        help="probability x impact (1-3 each) -> 1..9; the register sorts by this.",
    )
    owner_id = fields.Many2one("res.users", string="Owner")
    mitigation = fields.Text()
    opened_on = fields.Date(required=True, default=fields.Date.context_today)
    closed_on = fields.Date()
    escalated = fields.Boolean(
        readonly=True,
        copy=False,
        help="The project.risk_escalated event was published for this risk "
        "(hand-off to the M60 enterprise register).",
    )
    state = fields.Selection(
        [("open", "Open"), ("mitigating", "Mitigating"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "closed_on", "escalated"}

    @api.depends("probability", "impact")
    def _compute_severity(self):
        scale = {"low": 1, "medium": 2, "high": 3}
        for rec in self:
            rec.severity_score = scale.get(rec.probability, 1) * scale.get(rec.impact, 1)

    @api.model
    def _escalation_threshold(self) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        try:
            return int(
                icp.get_param(RISK_ESCALATION_THRESHOLD_PARAM) or RISK_ESCALATION_THRESHOLD_DEFAULT
            )
        except (TypeError, ValueError):
            return RISK_ESCALATION_THRESHOLD_DEFAULT

    @api.model
    def _overdue_days(self) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        try:
            return int(icp.get_param(RISK_OVERDUE_DAYS_PARAM) or RISK_OVERDUE_DAYS_DEFAULT)
        except (TypeError, ValueError):
            return RISK_OVERDUE_DAYS_DEFAULT

    def _publish_escalation(self, reason):
        for rec in self.filtered(lambda r: r.state != "closed"):
            if rec.escalated:
                continue
            rec._guarded().write({"escalated": True})
            publish(
                self.env,
                "project.risk_escalated",
                "fix.project.risk",
                rec.id,
                {
                    "risk": rec.name,
                    "title": rec.title,
                    "project": rec.project_id.name,
                    "project_id": rec.project_id.id,
                    "severity": rec.severity_score,
                    "kind": rec.kind,
                    "reason": reason,
                },
            )
            rec.message_post(body="Risk escalated to the enterprise register (M60): %s." % reason)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.project.risk") or "RISK/New"
                )
        recs = super().create(vals_list)
        # M60 hand-off: a MATERIAL risk is escalated the moment it is opened —
        # material means at or above the threshold, not merely opened.
        threshold = recs._escalation_threshold()
        recs.filtered(lambda r: r.severity_score >= threshold)._publish_escalation(
            "severity %d at or above the escalation threshold" % threshold
        )
        return recs

    def write(self, vals):
        result = super().write(vals)
        if {"probability", "impact"} & set(vals):
            # ...and the moment its severity reaches the threshold.
            threshold = self._escalation_threshold()
            self.filtered(lambda r: r.severity_score >= threshold)._publish_escalation(
                "severity raised to %d (threshold %d)" % (threshold, threshold)
            )
        return result

    def action_mitigate(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open risk can move to mitigating")
            if not (rec.mitigation or "").strip():
                raise UserError("Record the mitigation plan before the risk moves to mitigating.")
            rec._guarded().write({"state": "mitigating"})

    def action_close(self):
        for rec in self:
            if rec.state not in ("open", "mitigating"):
                raise UserError("This risk is already closed")
            if not (rec.mitigation or "").strip():
                raise UserError(
                    "A risk cannot be closed with no mitigation recorded: state what "
                    "was done about it (M67-8)."
                )
            rec._guarded().write({"state": "closed", "closed_on": fields.Date.context_today(rec)})

    def action_reopen(self):
        for rec in self:
            if rec.state != "closed":
                raise UserError("Only a closed risk can be reopened.")
            rec._guarded().write({"state": "open", "closed_on": False})

    @api.model
    def cron_escalate_overdue_risks(self):
        """R3/M67-11: escalate risks still open past the overdue window."""
        cutoff = fields.Date.context_today(self) - timedelta(days=self._overdue_days())
        stale = self.sudo().search(
            [("state", "in", ("open", "mitigating")), ("escalated", "=", False)],
        )
        stale.filtered(lambda r: r.opened_on and r.opened_on <= cutoff)._publish_escalation(
            "open longer than the overdue window"
        )
        return True

    @api.model
    def consume_project_risk_escalated(self, event):
        """project.risk_escalated: the in-project echo of the M60 hand-off
        (the enterprise register entry is created by the cd_grc consumer)."""
        risk = self.browse(event.get("aggregate_id") or 0).exists()
        if risk:
            risk.message_post(
                body="Escalation %s delivered to the enterprise risk register consumers."
                % event.get("event_id")
            )
        return True
