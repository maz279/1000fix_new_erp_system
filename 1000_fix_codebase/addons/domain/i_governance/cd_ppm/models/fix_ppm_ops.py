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
#
# A12 finish build (2026-11-07), findings F4-F6, F9, F14-F16, F19:
#   - the project manager stops at "ready". A Finance user invoices the line: the
#     invoice is posted through the M19 API (source "ar"), so "invoiced" means
#     posted, with its dimensions and its posting log;
#   - the line follows its move: reset, cancelled, deleted or reversed reopens it,
#     and "paid" follows the move's payment state (lifecycle row 10);
#   - retention is deducted on the invoice as its own line, and the ceiling is
#     measured on what the customer is invoiced, in the project's currency;
#   - a line can be cancelled, which takes it out of the ceiling and the closure;
#   - the risk owner and a sponsor work a risk; at or above the closure threshold
#     only a sponsor who does not manage the project closes it.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_ppm import FINANCE_GROUP, PM_GROUP, SPONSOR_GROUP, ppm_convert

# Escalation thresholds (business decisions, report §7): a risk at or above
# this severity_score (probability x impact, 1..9) is escalated to the M60
# enterprise register as soon as it is opened or reaches the score. A risk
# still open after this many days is escalated by the cron whatever its score.
RISK_ESCALATION_THRESHOLD_PARAM = "fix_ppm.risk_escalation_threshold"
RISK_ESCALATION_THRESHOLD_DEFAULT = 9
RISK_OVERDUE_DAYS_PARAM = "fix_ppm.risk_overdue_days"
RISK_OVERDUE_DAYS_DEFAULT = 7
# At or above this severity only a sponsor closes the risk (F19, report B6).
RISK_SPONSOR_CLOSE_PARAM = "fix_ppm.risk_sponsor_close_threshold"
RISK_SPONSOR_CLOSE_DEFAULT = 9

# Terms frozen once a billing line is ready to invoice.
BILLING_PINNED = {
    "amount",
    "project_id",
    "milestone_id",
    "retention_pct",
    "currency_id",
    "billing_type",
}
# A move in this payment state has been paid by the customer. in_payment: the
# payment is registered and waits only for the bank statement to match it.
PAID_PAYMENT_STATES = ("paid", "in_payment")


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
    # F16: state, invoice_ref and invoiced_on follow the invoice. Everything
    # that happens to the move reaches the line in the same transaction, whoever
    # did it and from whichever screen, with no cron to wait for.
    invoiced_on = fields.Date(compute="_compute_invoice_status", store=True, readonly=False)
    invoice_ref = fields.Char(
        string="Invoice Reference",
        compute="_compute_invoice_status",
        store=True,
        readonly=False,
        help="Display echo of the posted invoice's number. The invoice itself is the "
        "account.move in Invoice.",
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        readonly=True,
        copy=False,
        index=True,
        help="The real customer invoice (M20 account.move), posted through the M19 API "
        "by Finance. M67-1: 'invoiced' without an invoice is fiction.",
    )
    retention_pct = fields.Float(default=0.0)
    retention_amount = fields.Monetary(
        string="Retention",
        currency_field="currency_id",
        compute="_compute_net_amount",
        help="Held back from the customer on the invoice. Bill it with its own line "
        "when the retention is released.",
    )
    net_amount = fields.Monetary(
        string="Net Billed",
        currency_field="currency_id",
        compute="_compute_net_amount",
        help="What the customer is invoiced: the amount less retention.",
    )
    ready_by_id = fields.Many2one("res.users", string="Marked Ready By", readonly=True, copy=False)
    cancel_reason = fields.Char(string="Cancelled Because", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("planned", "Planned"),
            ("ready", "Ready to Invoice"),
            ("invoiced", "Invoiced"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="planned",
        tracking=True,
        compute="_compute_invoice_status",
        store=True,
        readonly=False,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "invoice_id",
            "invoiced_on",
            "invoice_ref",
            "ready_by_id",
            "cancel_reason",
        }

    def _billing_frozen_fields(self) -> set:
        """F15: everything the line was raised for, from "ready" on. A customer
        left blank on a legacy ready line stays open, or the line is stranded."""
        self.ensure_one()
        if self.state not in ("ready", "invoiced", "paid", "cancelled"):
            return set()
        return BILLING_PINNED | ({"customer_id"} if self.customer_id else set())

    def _fix_form_locked_fields(self) -> set:
        # M67-2 (bl_08): once the line is ready for invoicing, its terms are pinned.
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= self._billing_frozen_fields()
        return locked

    @api.depends("invoice_id", "invoice_id.state", "invoice_id.payment_state", "invoice_id.name")
    def _compute_invoice_status(self):
        for rec in self:
            state, ref, invoiced_on = rec.state or "planned", rec.invoice_ref, rec.invoiced_on
            move = rec.invoice_id
            if state != "cancelled":
                if move.state == "posted" and move.payment_state != "reversed":
                    state = "paid" if move.payment_state in PAID_PAYMENT_STATES else "invoiced"
                    ref = move.name
                    invoiced_on = move.invoice_date
                elif state in ("invoiced", "paid"):
                    # Deleted, cancelled, reset to draft or reversed: the revenue
                    # is gone, so the line goes back to Finance's queue.
                    state, ref, invoiced_on = "ready", False, False
            rec.state = state
            rec.invoice_ref = ref
            rec.invoiced_on = invoiced_on

    @api.depends("amount", "retention_pct")
    def _compute_net_amount(self):
        for rec in self:
            held = (rec.amount or 0.0) * (rec.retention_pct or 0.0) / 100.0
            rec.retention_amount = held
            rec.net_amount = (rec.amount or 0.0) - held

    def _amount_in_project_currency(self, amount):
        """F15: `amount` of this line in its project's currency."""
        self.ensure_one()
        return ppm_convert(
            self.env,
            amount,
            self.currency_id,
            self.project_id.currency_id,
            self.company_id,
            self.due_on or fields.Date.context_today(self),
        )

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

    def _assert_within_ceiling(self):
        """M67-2 (bl_02), F8, F15: the project's billing stays under its ceiling,
        with every line converted to the project's currency."""
        for rec in self.filtered(lambda r: r.state != "cancelled"):
            project = rec.project_id.sudo()
            ceiling = project._billing_ceiling()
            total = project._billing_committed()
            if total > ceiling + 0.005:
                raise ValidationError(
                    "Billing %s would take project %s to BDT %.2f of BDT %.2f contract value "
                    "(the budget stands in where no contract is recorded): billing may not "
                    "exceed the approved contract value."
                    % (rec.name, project.display_name, total, ceiling)
                )

    @api.constrains("amount", "project_id", "currency_id", "retention_pct")
    def _check_contract_ceiling(self):
        self._assert_within_ceiling()

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                changed = {
                    name
                    for name in rec._billing_frozen_fields() & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                }
                if changed:
                    raise UserError(
                        "The %s of a billing line are frozen once it is ready to invoice "
                        "(M67-2). Cancel the line and raise a new one instead."
                        % ", ".join(sorted(rec._fields[n].string for n in changed))
                    )
                # F15, BRU-PPM-11: retyping a milestone line skipped the acceptance
                # gate. What is billed on acceptance stays billed on acceptance.
                if (
                    "billing_type" in vals
                    and rec.billing_type == "milestone"
                    and vals["billing_type"] != "milestone"
                ):
                    raise UserError(
                        "%s bills a milestone, so it needs that milestone's acceptance. "
                        "Cancel it and raise a new line if this work is not milestone work."
                        % rec.name
                    )
        return super().write(vals)

    def action_mark_ready(self):
        """F14: the project manager's last step. Finance raises the invoice."""
        for rec in self:
            if rec.state != "planned":
                raise UserError("Only a planned billing line can be marked ready")
            if rec.project_id.state != "active":
                raise UserError(
                    "Project %s is %s: only an active project raises billing."
                    % (rec.project_id.display_name, rec.project_id.state)
                )
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
            # A legacy line can stand above a ceiling it never met.
            rec._assert_within_ceiling()
            rec._guarded().write({"state": "ready", "ready_by_id": self.env.user.id})

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

    def _invoice_lines(self, account):
        """The invoice's lines. F16: retention is deducted on the invoice as its
        own line, so the customer sees the gross, the deduction and the net."""
        self.ensure_one()
        label = "%s — %s" % (self.name, self.project_id.display_name)
        lines = [
            (
                0,
                0,
                {"name": label, "account_id": account.id, "quantity": 1, "price_unit": self.amount},
            )
        ]
        if self.retention_amount:
            lines.append(
                (
                    0,
                    0,
                    {
                        "name": "Retention held %.2f%% — %s" % (self.retention_pct, self.name),
                        "account_id": account.id,
                        "quantity": 1,
                        "price_unit": -self.retention_amount,
                    },
                )
            )
        return lines

    def _invoice_draft(self):
        """This line's draft invoice: one a reset left behind, or a new one."""
        self.ensure_one()
        if self.invoice_id.state == "draft":
            return self.invoice_id
        journal = self._invoice_journal()
        account = self._invoice_line_account(journal)
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer_id.id,
                "journal_id": journal.id,
                "company_id": self.company_id.id,
                "currency_id": self.currency_id.id,
                "invoice_date": fields.Date.context_today(self),
                "ref": "%s — %s" % (self.name, self.project_id.display_name),
                "invoice_line_ids": self._invoice_lines(account),
            }
        )

    def _invoice_dimensions(self, move):
        """Every line of the invoice carries its project (the M19 project
        dimension). Skipped only for a company with no operating unit, where
        M19 could not store a dimension row at all."""
        company = self.company_id
        if not self.env["operating.unit"].sudo().search_count([("company_id", "=", company.id)]):
            return None
        code = self.project_id.code
        return {index: {"project_ref": code} for index in range(len(move.line_ids))}

    def _billing_assert_finance(self, what):
        """F14: a Finance user who did not manage the project or ready this line."""
        if self.env.su:
            return
        if not self.env.user.has_group(FINANCE_GROUP):
            raise AccessError(
                "%s is done by Finance: you hold no invoicing role. The project manager "
                "stops at Ready to Invoice." % what
            )
        for rec in self:
            record = rec.sudo()
            if self.env.user in (record.project_id._ppm_delivery_users() | record.ready_by_id):
                raise UserError(
                    "Segregation of duties: you run %s or marked %s ready, so another Finance "
                    "user raises its invoice." % (record.project_id.display_name, record.name)
                )

    def action_mark_invoiced(self):
        """F6/F14: Finance raises the customer invoice and posts it through M19.
        The checks run as the caller; the document is written by the service role,
        like every engine-posted entry. A posting refused by the chart leaves
        nothing behind: "invoiced" means posted."""
        self.check_access("read")
        self._billing_assert_finance("Invoicing a project's billing")
        for rec in self.sudo():
            move = rec.invoice_id
            if move.state == "posted" and move.payment_state != "reversed":
                raise UserError("%s already carries invoice %s." % (rec.name, move.name))
            if rec.state != "ready":
                raise UserError("Only a ready billing line can be invoiced")
            if not rec.customer_id:
                raise UserError("Record the customer before invoicing.")
            rec._assert_within_ceiling()
            # The line's company, not the Finance user's current one.
            move = rec.with_company(rec.company_id)._invoice_draft()
            # The in-process posting API of M19: COA rules, dimensions, the posting
            # log and journal.posted, under the AR sub-ledger's source.
            move._fix_m19_post(
                source="ar",
                source_ref=rec.name,
                dimension_by_line=rec._invoice_dimensions(move),
            )
            rec._guarded().write({"invoice_id": move.id})
            rec.message_post(
                body="Customer invoice %s posted for %s %.2f by %s."
                % (move.name, rec.currency_id.name, move.amount_total, self.env.user.name)
            )

    def action_cancel(self, reason=None):
        """F9: a mistaken line leaves the ceiling and the closure with a reason.
        Billed revenue is not cancelled here: Finance reverses the invoice, which
        reopens the line."""
        if not (reason or "").strip():
            raise UserError("State why this billing line is cancelled.")
        self.check_access("read")
        user = self.env.user
        if not (self.env.su or user.has_group(PM_GROUP) or user.has_group(FINANCE_GROUP)):
            raise AccessError("A billing line is cancelled by a project manager or by Finance.")
        for rec in self.sudo():
            if rec.state not in ("planned", "ready"):
                raise UserError(
                    "%s is %s. Finance reverses the invoice first; that reopens the line."
                    % (rec.name, rec.state)
                )
            # A draft left on the line must not be posted later by someone else.
            if rec.invoice_id.state == "draft":
                rec.invoice_id.button_cancel()
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
            rec.message_post(body="Billing line cancelled by %s: %s" % (user.name, reason))


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

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "closed":
            locked.add("mitigation")
        return locked

    @api.depends("probability", "impact")
    def _compute_severity(self):
        scale = {"low": 1, "medium": 2, "high": 3}
        for rec in self:
            rec.severity_score = scale.get(rec.probability, 1) * scale.get(rec.impact, 1)

    @api.model
    def _int_param(self, key, default) -> int:
        icp = self.env["ir.config_parameter"].sudo()
        try:
            return int(icp.get_param(key) or default)
        except (TypeError, ValueError):
            return default

    @api.model
    def _escalation_threshold(self) -> int:
        return self._int_param(RISK_ESCALATION_THRESHOLD_PARAM, RISK_ESCALATION_THRESHOLD_DEFAULT)

    @api.model
    def _overdue_days(self) -> int:
        return self._int_param(RISK_OVERDUE_DAYS_PARAM, RISK_OVERDUE_DAYS_DEFAULT)

    @api.model
    def _sponsor_close_threshold(self) -> int:
        return self._int_param(RISK_SPONSOR_CLOSE_PARAM, RISK_SPONSOR_CLOSE_DEFAULT)

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
                    # F5: the register scores likelihood and impact separately;
                    # without them severity 9 landed as 3 x 3 = 9 of 25.
                    "probability": rec.probability,
                    "impact": rec.impact,
                    "mitigation": rec.mitigation or "",
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
        if "mitigation" in vals and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "closed"):
                if rec._fix_guard_differs("mitigation", vals["mitigation"], rec.mitigation):
                    raise UserError(
                        "The mitigation of closed risk %s is what it was closed on. Reopen the "
                        "risk to change it." % rec.name
                    )
        result = super().write(vals)
        if {"probability", "impact"} & set(vals):
            # ...and the moment its severity reaches the threshold.
            threshold = self._escalation_threshold()
            for rec in self.filtered(lambda r: r.severity_score >= threshold):
                rec._publish_escalation(
                    "severity raised to %d (threshold %d)" % (rec.severity_score, threshold)
                )
        return result

    def _risk_worker(self):
        """F19: a project manager, a sponsor or the risk's own owner works a risk.
        The owner and the sponsor hold no write on the register, so the transition
        runs as the service role once this check has passed."""
        self.check_access("read")
        if self.env.su:
            return self
        user = self.env.user
        if not (user.has_group(PM_GROUP) or user.has_group(SPONSOR_GROUP)):
            for rec in self:
                if rec.sudo().owner_id != user:
                    raise AccessError(
                        "Risk %s is worked by its owner, a project manager or a sponsor." % rec.name
                    )
        return self.sudo()

    def _risk_assert_may_close(self):
        """F19: a severe risk is not closed by the person whose project carries it."""
        if self.env.su:
            return
        threshold = self._sponsor_close_threshold()
        for rec in self.sudo().filtered(lambda r: r.severity_score >= threshold):
            user = self.env.user
            if user in rec.project_id._ppm_delivery_users() or not user.has_group(SPONSOR_GROUP):
                raise UserError(
                    "Risk %s has severity %d: at or above %d a sponsor who does not manage the "
                    "project closes it." % (rec.name, rec.severity_score, threshold)
                )

    def action_mitigate(self, mitigation=None):
        """F4: the button prompts for the mitigation, and this stores it."""
        for rec in self._risk_worker():
            if rec.state != "open":
                raise UserError("Only an open risk can move to mitigating")
            vals = {"state": "mitigating"}
            if (mitigation or "").strip():
                vals["mitigation"] = mitigation.strip()
            elif not (rec.mitigation or "").strip():
                raise UserError("Record the mitigation plan before the risk moves to mitigating.")
            rec._guarded().write(vals)

    def action_close(self, mitigation=None):
        self._risk_assert_may_close()
        for rec in self._risk_worker():
            if rec.state not in ("open", "mitigating"):
                raise UserError("This risk is already closed")
            vals = {"state": "closed", "closed_on": fields.Date.context_today(rec)}
            if (mitigation or "").strip():
                vals["mitigation"] = mitigation.strip()
            elif not (rec.mitigation or "").strip():
                raise UserError(
                    "A risk cannot be closed with no mitigation recorded: state what "
                    "was done about it (M67-8)."
                )
            rec._guarded().write(vals)

    def action_reopen(self):
        for rec in self._risk_worker():
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
        """project.risk_escalated: the in-project echo of the M60 hand-off. This
        consumer only knows the event left the project. The cd_grc consumer posts
        on the risk when the register entry exists: live, this echo said
        "delivered" on all three events while that consumer was dead."""
        risk = self.browse(event.get("aggregate_id") or 0).exists()
        if risk:
            risk.message_post(
                body="Escalation %s handed to the event relay for the enterprise risk "
                "register." % event.get("event_id")
            )
        return True
