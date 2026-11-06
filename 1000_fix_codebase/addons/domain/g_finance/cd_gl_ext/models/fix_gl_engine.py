# cd_gl_ext — M19 GL engine: posting log, recurring/reversing journal
# templates, allocation rules (CD-M19-01 / FR-FIN-008..017, FR-FIN-026).
#
# Everything posts through post_with_dimensions() in fix_gl_ext — the single
# sanctioned posting API — so COA rules, dimensions and journal.posted events
# apply identically to manual, templated and allocated entries.
#
# AS-10: every amount below is fields.Monetary with an explicit currency_id.
from __future__ import annotations

import logging
from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Posting sources that are DIRECT manual-style postings for COA-02 (control
# accounts may not receive these). Engine/subledger sources — settlement,
# suspense cutovers, the platform API — may legitimately hit control accounts.
MANUAL_SOURCES = ("manual", "template", "allocation")


class FixJournalPostingLog(models.Model):
    """The immutable record of every posting through the GL API (FR-FIN-042).

    One row per journal entry the platform posts or queues for review:
    who requested it, who posted it, from which surface. Rows are append-only
    — write and unlink are refused (the audit trail is evidence, not state)."""

    _name = "fix.journal.posting.log"
    _description = "Journal Posting Log"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", required=True, ondelete="restrict", index=True
    )
    move_name = fields.Char(string="Entry No", readonly=True)
    source = fields.Selection(
        [
            ("manual", "Manual (workspace)"),
            ("template", "Journal Template"),
            ("allocation", "Allocation Rule"),
            ("suspense", "Suspense Cutover"),
            ("settlement", "Settlement Engine"),
            ("api", "Platform API"),
            ("ar", "AR Engine (M20)"),
            ("receipt", "AR Receipt (M20)"),
            ("intercompany", "Inter-Company / Inter-Branch (M65)"),
            ("fx_revaluation", "FX Revaluation (M19)"),
            ("exchange", "Exchange Difference / Cash Basis (Odoo)"),
            ("cost_allocation", "Cost Allocation (M54)"),
            ("impairment", "AR Impairment (M20)"),
            ("asset", "Fixed Assets (M49)"),
        ],
        required=True,
        default="api",
    )
    state = fields.Selection(
        [("requested", "Awaiting Review"), ("posted", "Posted")],
        required=True,
        default="posted",
    )
    requested_by = fields.Many2one("res.users", string="Requested By", readonly=True)
    posted_by = fields.Many2one("res.users", string="Posted By", readonly=True)
    posted_at = fields.Datetime(string="Posted At", readonly=True)
    template_id = fields.Many2one("fix.journal.template", string="Template", ondelete="set null")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id")
    note = fields.Char(string="Note")
    source_ref = fields.Char(
        string="Source Document", readonly=True, help="The sub-ledger document that posted"
    )

    # The log is append-only evidence: no write, no unlink. The force_edit
    # context exists solely for the posting API's own state transition
    # (requested -> posted) and for test fixtures.
    def write(self, vals):
        if not self.env.context.get("force_edit"):
            raise UserError(
                "The posting log is immutable audit evidence (FR-FIN-042) — "
                "entries cannot be edited."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.context.get("force_edit"):
            raise UserError(
                "The posting log is immutable audit evidence (FR-FIN-042) — "
                "entries cannot be deleted."
            )
        return super().unlink()


# Shared by templates and allocation rules: who may approve a rule that posts
# unattended, and what counts as its content (A08 M19-9, M19-14).
_CONTENT_TOKEN = object()
_CONTENT_KEY = "fix_m19_rule_content"


def _content_snapshot(lines, fields_):
    import json

    def val(line, name):
        value = line[name]
        return value.id if isinstance(value, models.BaseModel) else value

    return json.dumps(sorted([[val(line, f) for f in fields_] for line in lines]), default=str)


class FixGlRuleApprovalMixin(models.AbstractModel):
    """A posting rule (recurring template, allocation rule) posts without
    further review once active, so activation is the approval (BRU-FIN-17):
    an Accounting Administrator who neither wrote nor last edited the rule.
    The activation covers the content it saw; any later change of that
    content returns the rule to draft."""

    _name = "fix.gl.rule.approval.mixin"
    _description = "GL Posting Rule Activation"
    _inherit = ["fix.guarded.mixin"]

    _rule_content_fields = ()
    _rule_line_fields = ()

    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(string="Activated At", readonly=True, copy=False)
    activation_snapshot = fields.Text(readonly=True, copy=False)
    last_edited_by_id = fields.Many2one(
        "res.users",
        string="Content Last Edited By",
        readonly=True,
        copy=False,
        help="Whoever last changed the rule's content; they never activate it.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "activation_snapshot",
            "last_edited_by_id",
        }

    def _rule_snapshot(self) -> str:
        self.ensure_one()
        head = [
            self[f].id if isinstance(self[f], models.BaseModel) else self[f]
            for f in self._rule_content_fields
        ]
        return "%s|%s" % (head, _content_snapshot(self.line_ids, self._rule_line_fields))

    def _rule_content_changed(self):
        """Content changed by a user: remember who, and void an activation."""
        if self.env.context.get(_CONTENT_KEY) is _CONTENT_TOKEN:
            return
        for rule in self.exists():
            vals = {}
            if not self.env.su:
                vals["last_edited_by_id"] = self.env.uid
            if rule.state != "draft":
                vals.update(
                    {
                        "state": "draft",
                        "activated_by_id": False,
                        "activated_at": False,
                        "activation_snapshot": False,
                    }
                )
                rule.message_post(
                    body="Content changed after activation by %s: returned to draft; it must be "
                    "activated again." % self.env.user.name
                )
            if vals:
                rule._guarded().write(vals)

    def write(self, vals):
        content = set(vals) & (set(self._rule_content_fields) | {"line_ids"})
        if content and not self._fix_guard_has_token():
            res = super(
                FixGlRuleApprovalMixin, self.with_context(**{_CONTENT_KEY: _CONTENT_TOKEN})
            ).write(vals)
            self._rule_content_changed()
            return res
        return super().write(vals)

    def _rule_activate(self, what):
        for rule in self:
            if rule.state == "active":
                continue
            if not self.env.su:
                if not self.env.user.has_group("account.group_account_manager"):
                    raise UserError("Only an accounting manager can activate a %s." % what)
                conflicted = rule.create_uid | rule.last_edited_by_id
                if self.env.user in conflicted:
                    raise UserError(
                        "Segregation of duties: %s wrote or last changed %s %s and cannot also "
                        "activate it." % (self.env.user.name, what, rule.name)
                    )
            rule._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                    "activation_snapshot": rule._rule_snapshot(),
                }
            )
            rule.message_post(body="%s activated by %s." % (what.capitalize(), self.env.user.name))
        return True

    def _rule_assert_active(self, what):
        for rule in self:
            if rule.state != "active" or not rule.activated_by_id:
                raise UserError("%s %s is not active" % (what.capitalize(), rule.name))
            if rule.activation_snapshot != rule._rule_snapshot():
                raise UserError(
                    "%s %s changed after it was activated; it must be activated again."
                    % (what.capitalize(), rule.name)
                )


class FixGlRuleLineMixin(models.AbstractModel):
    """Line changes count as the parent rule's content."""

    _name = "fix.gl.rule.line.mixin"
    _description = "GL Posting Rule Line"
    _rule_parent = None

    def _parents(self):
        return self.mapped(self._rule_parent)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._parents()._rule_content_changed()
        return lines

    def write(self, vals):
        parents = self._parents()
        res = super().write(vals)
        line_fields = set(parents._rule_line_fields) if parents else set()
        if set(vals) & (line_fields | {self._rule_parent}):
            (parents | self._parents())._rule_content_changed()
        return res

    def unlink(self):
        parents = self._parents()
        res = super().unlink()
        parents.exists()._rule_content_changed()
        return res


class FixJournalTemplate(models.Model):
    """A recurring journal entry — the accrual framework's carrier
    (FR-FIN-013/016).

    Monthly/quarterly/yearly schedules generate real entries through the
    posting API; ``auto_reverse`` additionally posts the mirror entry at the
    start of the following period — the D365-style reversing accrual used for
    unbilled WIP and recurring utilities/lease costs. No entry is ever
    invented: a run only fires when ``next_run_date`` is due, and only for a
    template whose activation still covers its content."""

    _name = "fix.journal.template"
    _description = "Recurring Journal Template"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.gl.rule.approval.mixin"]
    _order = "name"

    _rule_content_fields = (
        "journal_id",
        "company_id",
        "currency_id",
        "memo",
        "schedule",
        "next_run_date",
        "auto_reverse",
    )
    _rule_line_fields = (
        "account_id",
        "debit",
        "credit",
        "branch_id",
        "cost_centre",
        "business_line",
    )

    name = fields.Char(string="Template Name", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain=[("type", "in", ("general", "bank", "cash"))],
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    memo = fields.Char(string="Entry Reference", help="Reference written on every generated entry")
    schedule = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("yearly", "Yearly"),
        ],
        required=True,
        default="monthly",
    )
    next_run_date = fields.Date(string="Next Run Date", required=True)
    auto_reverse = fields.Boolean(
        string="Auto-Reversing (Accrual)",
        help="Post the mirror entry at the start of the following period — "
        "the reversing accrual pattern for WIP, utilities and leases",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("paused", "Paused")],
        required=True,
        default="draft",
        tracking=True,
    )
    line_ids = fields.One2many("fix.journal.template.line", "template_id", string="Template Lines")
    last_move_id = fields.Many2one("account.move", string="Last Generated Entry", readonly=True)
    last_run_date = fields.Date(string="Last Run", readonly=True)
    run_count = fields.Integer(string="Entries Generated", readonly=True, default=0)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"last_move_id", "last_run_date", "run_count"}

    @api.constrains("line_ids")
    def _check_balanced(self):
        for template in self:
            debit = sum(template.line_ids.mapped("debit"))
            credit = sum(template.line_ids.mapped("credit"))
            if not template.line_ids:
                raise ValidationError("Template %s has no lines" % template.name)
            if round(debit - credit, 2) != 0.0:
                raise ValidationError(
                    "Template %s is not balanced: debit %.2f vs credit %.2f"
                    % (template.name, debit, credit)
                )

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------
    def _advance(self, run_date: date) -> date:
        if self.schedule == "monthly":
            return date(run_date.year + (run_date.month == 12), run_date.month % 12 + 1, 1)
        if self.schedule == "quarterly":
            quarter_month = ((run_date.month - 1) // 3 + 1) * 3 + 1  # next quarter start
            year = run_date.year + (1 if quarter_month > 12 else 0)
            return date(year, (quarter_month - 1) % 12 + 1, 1)
        return date(run_date.year + 1, 1, 1)

    def _next_period_start(self, run_date: date) -> date:
        """First day of the period FOLLOWING the run period — where an
        auto-reversing accrual's mirror entry lands."""
        return self._advance(date(run_date.year, run_date.month, 1))

    # ------------------------------------------------------------------
    # Approval (a template posts unattended once active)
    # ------------------------------------------------------------------
    def action_activate(self):
        """Approve a draft/paused template for automatic generation. An
        active template posts without further review, so activation is the
        checker step: accounting manager only, never the template's author or
        its last editor (segregation of duties, FR-FIN-015, BRU-FIN-17)."""
        return self._rule_activate("recurring journal template")

    def action_pause(self):
        """Stop automatic generation (the cron skips paused templates)."""
        for template in self:
            if template.state != "active":
                raise UserError("Only an active template can be paused.")
            template._guarded().write({"state": "paused"})
        return True

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def action_generate_entry(self):
        """Generate the due entry (and its reversal when auto_reverse).

        Debits/credits are swapped on the mirror; every line keeps its
        account and dimensions. Both entries post through the sanctioned
        API, so COA rules and journal.posted events apply."""
        today = fields.Date.context_today(self)
        for template in self:
            template._rule_assert_active("template")
            run_date = template.next_run_date
            if run_date > today:
                raise UserError("Template %s is not due until %s" % (template.name, run_date))

            move, _dims = template._post_from_template(run_date, reverse=False)
            reversal = template.env["account.move"]
            if template.auto_reverse:
                reversal, _rev_dims = template._post_from_template(
                    template._next_period_start(run_date), reverse=True
                )
            runner = template._guarded().with_context(**{_CONTENT_KEY: _CONTENT_TOKEN})
            runner.write(
                {
                    "last_move_id": move.id,
                    "last_run_date": run_date,
                    "run_count": template.run_count + (2 if reversal else 1),
                    "next_run_date": template._advance(run_date),
                }
            )
            # The run itself moved the schedule on: the activation still covers it.
            runner.write({"activation_snapshot": template._rule_snapshot()})
        return True

    def _post_from_template(self, entry_date: date, reverse: bool):
        from .fix_gl_ext import post_with_dimensions

        self.ensure_one()
        move_vals = {
            "journal_id": self.journal_id.id,
            "date": entry_date,
            "ref": ("REVERSAL: " if reverse else "") + (self.memo or self.name),
            "company_id": self.company_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": line.account_id.id,
                        "name": ("Reversal — " if reverse else "") + (line.label or self.name),
                        "debit": line.credit if reverse else line.debit,
                        "credit": line.debit if reverse else line.credit,
                    },
                )
                for line in self.line_ids
            ],
        }
        dimension_by_line = {
            idx: {
                "branch_id": line.branch_id.id or False,
                "cost_centre": line.cost_centre or False,
                "business_line": line.business_line or False,
            }
            for idx, line in enumerate(self.line_ids)
        }
        return post_with_dimensions(
            self.env,
            move_vals,
            dimension_by_line,
            source="template",
            template=self,
            source_ref=self.name,
        )

    @api.model
    def _cron_generate_due_entries(self):
        """Daily cron: generate every ACTIVE template whose next_run_date is
        due. Failures are logged per-template — one bad template must not
        stop the others (the run is not a transaction)."""
        today = fields.Date.context_today(self)
        due = self.search([("state", "=", "active"), ("next_run_date", "<=", today)])
        generated = 0
        for template in due:
            try:
                with self.env.cr.savepoint():
                    template.action_generate_entry()
                generated += 1
            except UserError as exc:
                _logger.error("GL template %s failed to generate: %s", template.name, exc)
        if generated:
            _logger.info("GL template cron generated %d entries", generated)
        return generated


class FixJournalTemplateLine(models.Model):
    """One line of a recurring journal template."""

    _name = "fix.journal.template.line"
    _description = "Journal Template Line"
    _inherit = ["fix.gl.rule.line.mixin"]
    _rule_parent = "template_id"

    template_id = fields.Many2one(
        "fix.journal.template", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one("account.account", string="Account", required=True, index=True)
    label = fields.Char(string="Line Label")
    currency_id = fields.Many2one(related="template_id.currency_id", store=True)
    debit = fields.Monetary(string="Debit", currency_field="currency_id")
    credit = fields.Monetary(string="Credit", currency_field="currency_id")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    cost_centre = fields.Char(string="Cost Centre")
    business_line = fields.Char(string="Business Line")

    @api.constrains("debit", "credit")
    def _check_one_side(self):
        for line in self:
            if line.debit and line.credit:
                raise ValidationError(
                    "A template line carries either a debit or a credit, not both"
                )


class FixAllocationRule(models.Model):
    """A GL allocation rule — distribute a source account's period movement
    across target accounts/dimensions by fixed percentages (FR-FIN-026,
    the D365 ledger-allocation pattern: shared rent/utilities/overhead split
    across branches and cost centres).

    Running the rule posts ONE balancing entry: the source account is
    cleared for its period movement, each target receives its share, the
    last target takes the rounding remainder. The run is computed from
    POSTED move lines — never from a manual figure — and only for a rule an
    Accounting Administrator other than its author activated."""

    _name = "fix.allocation.rule"
    _description = "GL Allocation Rule"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.gl.rule.approval.mixin"]
    _order = "name"

    _rule_content_fields = ("journal_id", "company_id", "source_account_id", "currency_id")
    _rule_line_fields = ("account_id", "percent", "branch_id", "cost_centre", "business_line")

    name = fields.Char(string="Rule Name", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        domain=[("type", "in", ("general", "bank", "cash"))],
    )
    source_account_id = fields.Many2one(
        "account.account", string="Source Account", required=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], required=True, default="draft", tracking=True
    )
    line_ids = fields.One2many("fix.allocation.rule.line", "rule_id", string="Targets")
    last_run_id = fields.Many2one("account.move", string="Last Allocation Entry", readonly=True)
    last_run_date = fields.Date(string="Last Run", readonly=True)
    run_count = fields.Integer(string="Runs", readonly=True, default=0)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"last_run_id", "last_run_date", "run_count"}

    @api.constrains("line_ids")
    def _check_percent(self):
        for rule in self:
            if not rule.line_ids:
                raise ValidationError("Allocation rule %s has no targets" % rule.name)
            total = sum(rule.line_ids.mapped("percent"))
            if round(total - 100.0, 2) != 0.0:
                raise ValidationError(
                    "Allocation rule %s targets sum to %.2f%% — they must total 100%%"
                    % (rule.name, total)
                )

    def action_activate(self):
        self._check_percent()
        return self._rule_activate("allocation rule")

    def action_deactivate(self):
        for rule in self:
            if rule.state != "active":
                raise UserError("Allocation rule %s is not active." % rule.name)
            rule._guarded().write(
                {"state": "draft", "activated_by_id": False, "activated_at": False}
            )
        return True

    def action_run(self, date_from=None, date_to=None):
        """Post the allocation entry for the source account's POSTED movement
        in the window (default: current month to date, in the Dhaka calendar)."""
        from .fix_gl_ext import post_with_dimensions

        for rule in self:
            rule._rule_assert_active("allocation rule")
            rule._check_percent()
            run_to = date_to or fields.Date.context_today(rule)
            run_from = date_from or run_to.replace(day=1)

            domain = [
                ("company_id", "=", rule.company_id.id),
                ("account_id", "=", rule.source_account_id.id),
                ("parent_state", "=", "posted"),
                ("date", ">=", run_from),
                ("date", "<=", run_to),
            ]
            groups = rule.env["account.move.line"]._read_group(
                domain, [], ["debit:sum", "credit:sum"]
            )
            debit = sum(g[0] or 0.0 for g in groups)
            credit = sum(g[1] or 0.0 for g in groups)
            movement = round(debit - credit, 2)
            if movement == 0.0:
                raise UserError(
                    "Source account %s has no posted movement between %s and %s — "
                    "nothing to allocate."
                    % (rule.source_account_id.display_name, run_from, run_to)
                )

            line_vals = [
                (
                    0,
                    0,
                    {
                        "account_id": rule.source_account_id.id,
                        "name": "Allocation clearing — %s" % rule.name,
                        "debit": round(-movement, 2) if movement < 0 else 0.0,
                        "credit": round(movement, 2) if movement > 0 else 0.0,
                    },
                )
            ]
            dimension_by_line = {0: {}}
            targets = rule.line_ids.sorted(lambda t: (t.sequence, t.id))
            allocated = 0.0
            for idx, target in enumerate(targets, start=1):
                if idx == len(targets):
                    # The last target takes the rounding remainder, so the entry
                    # balances to the cent (10.01 at 33.33/33.33/33.34).
                    share = round(movement - allocated, 2)
                else:
                    share = round(movement * target.percent / 100.0, 2)
                allocated = round(allocated + share, 2)
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "account_id": target.account_id.id,
                            "name": "Allocation %s%% — %s" % (target.percent, rule.name),
                            "debit": round(share, 2) if share > 0 else 0.0,
                            "credit": round(-share, 2) if share < 0 else 0.0,
                        },
                    )
                )
                dimension_by_line[idx] = {
                    "branch_id": target.branch_id.id or False,
                    "cost_centre": target.cost_centre or False,
                    "business_line": target.business_line or False,
                }

            move_vals = {
                "journal_id": rule.journal_id.id,
                "date": run_to,
                "ref": "ALLOCATION: %s (%s..%s)" % (rule.name, run_from, run_to),
                "company_id": rule.company_id.id,
                "line_ids": line_vals,
            }
            move, _dims = post_with_dimensions(
                rule.env, move_vals, dimension_by_line, source="allocation", source_ref=rule.name
            )
            rule._guarded().write(
                {"last_run_id": move.id, "last_run_date": run_to, "run_count": rule.run_count + 1}
            )
        return True


class FixAllocationRuleLine(models.Model):
    """One allocation target: account + dimensions + share percentage. The
    rule's targets total 100% after every change of a line, not only when the
    rule is saved (A08 M19-14: a line write left a rule at 50%)."""

    _name = "fix.allocation.rule.line"
    _description = "Allocation Rule Target"
    _inherit = ["fix.gl.rule.line.mixin"]
    _rule_parent = "rule_id"

    rule_id = fields.Many2one("fix.allocation.rule", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one(
        "account.account", string="Target Account", required=True, index=True
    )
    percent = fields.Float(string="Share %", required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    cost_centre = fields.Char(string="Cost Centre")
    business_line = fields.Char(string="Business Line")

    @api.constrains("percent", "rule_id")
    def _check_line_percent(self):
        for line in self:
            if line.percent <= 0 or line.percent > 100:
                raise ValidationError("A target share is above 0% and at most 100%.")
        # Inside the rule's own save the rule constraint checks the total once
        # every command has run; a direct line change is checked here.
        if self.env.context.get(_CONTENT_KEY) is not _CONTENT_TOKEN:
            self.mapped("rule_id")._check_percent()

    def unlink(self):
        rules = self.mapped("rule_id")
        in_rule_save = self.env.context.get(_CONTENT_KEY) is _CONTENT_TOKEN
        res = super().unlink()
        if not in_rule_save:
            rules.exists()._check_percent()
        return res
