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


class FixJournalTemplate(models.Model):
    """A recurring journal entry — the accrual framework's carrier
    (FR-FIN-013/016).

    Monthly/quarterly/yearly schedules generate real entries through the
    posting API; ``auto_reverse`` additionally posts the mirror entry at the
    start of the following period — the D365-style reversing accrual used for
    unbilled WIP and recurring utilities/lease costs. No entry is ever
    invented: a run only fires when ``next_run_date`` is due."""

    _name = "fix.journal.template"
    _description = "Recurring Journal Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

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
    # Generation
    # ------------------------------------------------------------------
    def action_generate_entry(self):
        """Generate the due entry (and its reversal when auto_reverse).

        Debits/credits are swapped on the mirror; every line keeps its
        account and dimensions. Both entries post through the sanctioned
        API, so COA rules and journal.posted events apply."""
        for template in self:
            if template.state != "active":
                raise UserError("Template %s is not active" % template.name)
            run_date = template.next_run_date
            if run_date > fields.Date.today():
                raise UserError("Template %s is not due until %s" % (template.name, run_date))

            move, _dims = template._post_from_template(run_date, reverse=False)
            reversal = template.env["account.move"]
            if template.auto_reverse:
                reversal, _rev_dims = template._post_from_template(
                    template._next_period_start(run_date), reverse=True
                )
            template.write(
                {
                    "last_move_id": move.id,
                    "last_run_date": run_date,
                    "run_count": template.run_count + (2 if reversal else 1),
                    "next_run_date": template._advance(run_date),
                }
            )
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
        )

    @api.model
    def _cron_generate_due_entries(self):
        """Daily cron: generate every ACTIVE template whose next_run_date is
        due. Failures are logged per-template — one bad template must not
        stop the others (the run is not a transaction)."""
        today = fields.Date.today()
        due = self.search([("state", "=", "active"), ("next_run_date", "<=", today)])
        generated = 0
        for template in due:
            try:
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
    cleared for its period movement, each target receives its share. The
    run is computed from POSTED move lines — never from a manual figure."""

    _name = "fix.allocation.rule"
    _description = "GL Allocation Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

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

    def action_run(self, date_from=None, date_to=None):
        """Post the allocation entry for the source account's POSTED movement
        in the window (default: current month to date)."""
        from .fix_gl_ext import post_with_dimensions

        for rule in self:
            if rule.state != "active":
                raise UserError("Allocation rule %s is not active" % rule.name)
            date_to = date_to or fields.Date.today()
            date_from = date_from or date_to.replace(day=1)

            domain = [
                ("company_id", "=", rule.company_id.id),
                ("account_id", "=", rule.source_account_id.id),
                ("parent_state", "=", "posted"),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
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
                    % (rule.source_account_id.display_name, date_from, date_to)
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
            for idx, target in enumerate(rule.line_ids, start=1):
                share = round(movement * target.percent / 100.0, 2)
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "account_id": target.account_id.id,
                            "name": "Allocation %d%% — %s" % (target.percent, rule.name),
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
                "date": date_to,
                "ref": "ALLOCATION: %s (%s..%s)" % (rule.name, date_from, date_to),
                "company_id": rule.company_id.id,
                "line_ids": line_vals,
            }
            move, _dims = post_with_dimensions(
                rule.env, move_vals, dimension_by_line, source="allocation"
            )
            rule.write(
                {"last_run_id": move.id, "last_run_date": date_to, "run_count": rule.run_count + 1}
            )
        return True


class FixAllocationRuleLine(models.Model):
    """One allocation target: account + dimensions + share percentage."""

    _name = "fix.allocation.rule.line"
    _description = "Allocation Rule Target"

    rule_id = fields.Many2one("fix.allocation.rule", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one(
        "account.account", string="Target Account", required=True, index=True
    )
    percent = fields.Float(string="Share %", required=True)
    branch_id = fields.Many2one("fix.branch", string="Branch")
    cost_centre = fields.Char(string="Cost Centre")
    business_line = fields.Char(string="Business Line")
