# cd_gl_ext — M19 capture audit, second pass (19 Nov 2026).
#
# The M19 spec (§5, §8.3, §9, §10.1) names five records a finance person
# enters that had no model, so their sub-module pages could capture nothing:
#
#   page 1  fix.gl.crossvalidation.rule  FR-FIN-004 / BRU-FIN-22 (H): a
#           dimension combination a rule forbids is refused at posting, on
#           every path of the posting API.
#   page 3  fix.gl.posting.rule          FR-FIN-008/009/010, BRU-FIN-17/18 (H):
#           versioned, tested against fixtures, approved by an accounting
#           manager who did not write it, never edited in place. While a
#           version governs a sub-ledger source, that source may post only to
#           the rule's accounts, and the posting log names the version.
#   page 4  account.fiscal.year          FR-FIN-018 / BRU-FIN-19 (H): July–June.
#   page 6  fix.currency.rate.entry      FR-FIN-033: dated rates by type, entered
#           by one person and approved by another; an approved spot or closing
#           rate becomes the rate the ledger and the FX revaluation use.
#   page 8  fix.auditor.access.grant     FR-FIN-043 / BRU-FIN-26 (H): read-only,
#           time-limited, scoped to entities and periods, logged.
#
# AS-10: amounts are Monetary with a currency; rates are Float (a rate is not
# an amount).
from __future__ import annotations

from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_gl_ext import ACCOUNT_MANAGER, ACCOUNT_USER, require_role

AUDITOR_GROUP = "cd_gl_ext.group_external_auditor"
PARAM_AUDIT_MAX_DAYS = "cd_gl_ext.auditor_access_max_days"
DEFAULT_AUDIT_MAX_DAYS = 90
# groups that can change the books: an external auditor holds none of them
WRITE_GROUPS = (
    "account.group_account_invoice",
    "account.group_account_user",
    "account.group_account_manager",
    "base.group_system",
    "base.group_erp_manager",
)

DIMENSIONS = [
    ("branch", "Branch (code)"),
    ("cost_centre", "Cost Centre"),
    ("business_line", "Business Line"),
    ("project", "Project / Contract"),
    ("brand", "Brand / OEM"),
    ("channel", "Service Channel"),
]
_DIM_KEY = {"project": "project_ref"}


def _require_manager(env, what):
    if env.su:
        return
    if not env.user.has_group(ACCOUNT_MANAGER):
        raise AccessError("%s is done by an Accounting Administrator." % what)


def _not_maker(env, makers, what):
    """Segregation of duties: whoever wrote it does not approve it."""
    if env.su:
        return
    if env.user in makers:
        raise UserError(
            "Segregation of duties: %s wrote or last changed this and cannot also %s it."
            % (env.user.name, what)
        )


def _split(values):
    return {v.strip().lower() for v in (values or "").replace(";", ",").split(",") if v.strip()}


# =============================================================== page 1
class FixGlCrossValidationRule(models.Model):
    """A forbidden or required dimension combination (FR-FIN-004).

    'deny': a line on a matching account must NOT carry one of the values
    (a rental-revenue account with the repair business line).
    'allow_only': a line on a matching account MUST carry one of the values.
    Active rules are checked on every posting path (BRU-FIN-22), including
    sub-ledger postings and the API. Terms freeze once active: retire the rule
    and write a new one."""

    _name = "fix.gl.crossvalidation.rule"
    _description = "GL Dimension Cross-Validation Rule"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "account_prefix, id desc"

    name = fields.Char(string="Rule", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    account_prefix = fields.Char(
        string="Account Code Starts With",
        required=True,
        help="Every ledger account whose code starts with this applies (e.g. 4102 = rental revenue).",
    )
    dimension = fields.Selection(DIMENSIONS, required=True)
    effect = fields.Selection(
        [
            ("deny", "Must NOT carry any of the values"),
            ("allow_only", "Must carry one of the values"),
        ],
        required=True,
        default="deny",
    )
    values = fields.Char(
        string="Values", required=True, help="Comma-separated. Branches by their branch code."
    )
    active_from = fields.Date(required=True, default=fields.Date.context_today)
    note = fields.Text(string="Why")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    last_edited_by_id = fields.Many2one("res.users", string="Last Edited By", readonly=True)
    activated_by_id = fields.Many2one("res.users", string="Activated By", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)

    _TERMS = ("company_id", "account_prefix", "dimension", "effect", "values", "active_from")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "last_edited_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._TERMS) | {"name"}
        return locked

    @api.constrains("account_prefix", "values")
    def _check_terms(self):
        for rule in self:
            if not (rule.account_prefix or "").strip():
                raise ValidationError("Name the account code the rule applies to.")
            if not _split(rule.values):
                raise ValidationError("Name at least one dimension value.")

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        if not self.env.su:
            rules._guarded().write({"last_edited_by_id": self.env.uid})
        return rules

    def write(self, vals):
        if set(vals) & (set(self._TERMS) | {"name"}) and not self._fix_guard_open():
            if any(r.state != "draft" for r in self):
                raise UserError(
                    "An active or retired cross-validation rule is never edited: retire it and "
                    "write a new one."
                )
            res = super().write(vals)
            self._guarded().write({"last_edited_by_id": self.env.uid})
            return res
        return super().write(vals)

    def unlink(self):
        if any(r.state != "draft" for r in self) and not self.env.su:
            raise UserError("Only a draft rule is deleted; an active rule is retired.")
        return super().unlink()

    def action_activate(self):
        _require_manager(self.env, "Activating a cross-validation rule")
        for rule in self:
            if rule.state != "draft":
                raise UserError("Only a draft rule is activated.")
            _not_maker(self.env, rule.create_uid | rule.last_edited_by_id, "activate")
            rule._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            rule.message_post(body="Activated by %s." % self.env.user.name)
        return True

    def action_retire(self):
        _require_manager(self.env, "Retiring a cross-validation rule")
        for rule in self:
            if rule.state != "active":
                raise UserError("Only an active rule is retired.")
            rule._guarded().write({"state": "retired"})
            rule.message_post(body="Retired by %s." % self.env.user.name)
        return True

    # ---------------------------------------------------------------- check
    def _line_value(self, dims, dimension):
        if dimension == "branch":
            branch = dims.get("branch_id") or dims.get("branch")
            if not branch:
                return set()
            if isinstance(branch, int):
                rec = self.env["fix.branch"].sudo().browse(branch).exists()
                return {v.lower() for v in (rec.code, rec.name) if v} if rec else set()
            return {str(branch).lower()}
        value = dims.get(_DIM_KEY.get(dimension, dimension)) or dims.get(dimension)
        return {str(value).strip().lower()} if value else set()

    @api.model
    def _check_move(self, move, dimension_by_line):
        """Refuse `move` when a line breaks an active rule (BRU-FIN-22)."""
        rules = self.sudo().search(
            [
                ("state", "=", "active"),
                ("company_id", "=", move.company_id.id),
                ("active_from", "<=", move.date or fields.Date.context_today(self)),
            ]
        )
        if not rules:
            return
        dimension_by_line = dimension_by_line or {}
        for idx, line in enumerate(move.line_ids):
            code = line.account_id.with_company(move.company_id).code or ""
            dims = dict(dimension_by_line.get(idx) or {})
            for rule in rules:
                if not code.startswith(rule.account_prefix.strip()):
                    continue
                carried = self._line_value(dims, rule.dimension)
                wanted = _split(rule.values)
                label = dict(DIMENSIONS)[rule.dimension]
                if rule.effect == "deny" and carried & wanted:
                    raise UserError(
                        "Posting refused by cross-validation rule '%s': account %s may not carry "
                        "%s %s." % (rule.name, code, label, ", ".join(sorted(carried & wanted)))
                    )
                if rule.effect == "allow_only" and not carried & wanted:
                    raise UserError(
                        "Posting refused by cross-validation rule '%s': account %s must carry "
                        "%s %s (it carries %s)."
                        % (
                            rule.name,
                            code,
                            label,
                            " or ".join(sorted(wanted)),
                            ", ".join(sorted(carried)) or "none",
                        )
                    )


# =============================================================== page 3
def _posting_sources(env):
    return [
        s for s in env["fix.journal.posting.log"]._fields["source"].selection if s[0] != "manual"
    ]


class FixGlPostingRule(models.Model):
    """The versioned rule by which a sub-ledger source posts (FR-FIN-009).

    Lifecycle (spec §8.3): Draft → Tested (every fixture passes) → Active
    (approved by an Accounting Administrator who neither wrote nor last
    changed it, BRU-FIN-17) → Superseded by the next version, which is
    retained permanently. Never edited in place once tested (BRU-FIN-18): a
    change is a new version. The version in force for a posting is the
    latest active or superseded one effective on the posting date."""

    _name = "fix.gl.posting.rule"
    _description = "GL Posting Rule (versioned)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "source, version desc"
    _rec_name = "code"

    code = fields.Char(string="Rule Version", compute="_compute_code", store=True)
    name = fields.Char(string="Description", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    source = fields.Selection(
        selection=lambda self: _posting_sources(self.env),
        string="Sub-ledger Source",
        required=True,
        index=True,
    )
    version = fields.Integer(readonly=True, copy=False, default=0)
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("tested", "Tested"),
            ("active", "Active"),
            ("superseded", "Superseded"),
            ("retired", "Retired"),
        ],
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    line_ids = fields.One2many(
        "fix.gl.posting.rule.line", "rule_id", string="Posting Lines", copy=True
    )
    fixture_ids = fields.One2many(
        "fix.gl.posting.rule.fixture", "rule_id", string="Test Fixtures", copy=True
    )
    last_test_at = fields.Datetime(readonly=True, copy=False)
    last_test_result = fields.Text(readonly=True, copy=False)
    last_edited_by_id = fields.Many2one(
        "res.users", string="Last Edited By", readonly=True, copy=False
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    previous_version_id = fields.Many2one(
        "fix.gl.posting.rule", string="Previous Version", readonly=True, copy=False
    )
    posting_count = fields.Integer(compute="_compute_posting_count", string="Postings")

    _TERMS = ("name", "company_id", "source", "effective_from")

    @api.depends("source", "version")
    def _compute_code(self):
        for rule in self:
            rule.code = "PR-%s-v%d" % ((rule.source or "?").upper(), rule.version or 0)

    def _compute_posting_count(self):
        Log = self.env["fix.journal.posting.log"].sudo()
        for rule in self:
            rule.posting_count = Log.search_count([("posting_rule_id", "=", rule.id)])

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "last_test_at",
            "last_test_result",
            "last_edited_by_id",
            "approved_by_id",
            "approved_at",
            "previous_version_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        for rule in rules:
            last = self.sudo().search(
                [
                    ("company_id", "=", rule.company_id.id),
                    ("source", "=", rule.source),
                    ("id", "!=", rule.id),
                ],
                order="version desc",
                limit=1,
            )
            vals = {"version": (last.version or 0) + 1}
            if not self.env.su:
                vals["last_edited_by_id"] = self.env.uid
            rule._guarded().write(vals)
        return rules

    def _assert_editable(self):
        if self._fix_guard_open():
            return
        if any(r.state != "draft" for r in self):
            raise UserError(
                "A tested or approved posting rule is never edited in place (BRU-FIN-18): "
                "make a new version."
            )

    def _content_changed(self):
        if not self.env.su and not self._fix_guard_has_token():
            self._guarded().write({"last_edited_by_id": self.env.uid})

    def write(self, vals):
        if set(vals) & (set(self._TERMS) | {"line_ids", "fixture_ids"}):
            self._assert_editable()
            res = super().write(vals)
            self._content_changed()
            return res
        return super().write(vals)

    def unlink(self):
        if any(r.state != "draft" for r in self) and not self.env.su:
            raise UserError("Only a draft posting rule is deleted; prior versions are kept.")
        return super().unlink()

    # ------------------------------------------------------------ fixtures
    def _generate(self, amount):
        """{account_id: [debit, credit]} the rule produces for `amount`."""
        self.ensure_one()
        currency = self.company_id.currency_id
        out = {}
        for line in self.line_ids:
            value = currency.round(amount * line.share_percent / 100.0)
            slot = out.setdefault(line.account_id.id, [0.0, 0.0])
            slot[0 if line.side == "debit" else 1] += value
        return out

    def _structure_errors(self):
        self.ensure_one()
        errors = []
        for side in ("debit", "credit"):
            lines = self.line_ids.filtered(lambda line, s=side: line.side == s)
            if not lines:
                errors.append("the rule has no %s line" % side)
            elif abs(sum(lines.mapped("share_percent")) - 100.0) > 0.001:
                errors.append(
                    "the %s shares add up to %s%%, not 100%%"
                    % (side, sum(lines.mapped("share_percent")))
                )
        if not self.fixture_ids:
            errors.append("no test fixture is attached")
        return errors

    def _run_fixtures(self):
        """(passed, report) of every fixture case against the rule's lines."""
        self.ensure_one()
        currency = self.company_id.currency_id
        report, passed = [], True
        for amount in sorted(set(self.fixture_ids.mapped("sample_amount"))):
            rows = self.fixture_ids.filtered(lambda f, a=amount: f.sample_amount == a)
            expected = {}
            for row in rows:
                slot = expected.setdefault(row.account_id.id, [0.0, 0.0])
                slot[0] += row.expected_debit
                slot[1] += row.expected_credit
            got = self._generate(amount)
            ok = set(got) == set(expected) and all(
                currency.is_zero(got[a][0] - expected[a][0])
                and currency.is_zero(got[a][1] - expected[a][1])
                for a in got
            )
            passed &= ok
            report.append(
                "%s %s: %s"
                % (
                    "PASS" if ok else "FAIL",
                    amount,
                    "as expected" if ok else "expected %s, got %s" % (expected, got),
                )
            )
        return passed, "\n".join(report)

    def action_run_tests(self):
        require_role(self.env, ACCOUNT_USER, "Testing a posting rule")
        for rule in self:
            if rule.state != "draft":
                raise UserError("Only a draft rule is tested; a tested rule is frozen.")
            errors = rule._structure_errors()
            if errors:
                raise UserError(
                    "Posting rule %s cannot be tested: %s." % (rule.code, "; ".join(errors))
                )
            passed, report = rule._run_fixtures()
            vals = {"last_test_at": fields.Datetime.now(), "last_test_result": report}
            if passed:
                vals["state"] = "tested"
            rule._guarded().write(vals)
            rule.message_post(
                body="Fixtures run by %s: %s"
                % (self.env.user.name, "all pass" if passed else "FAILED")
            )
        return True

    def action_approve(self):
        """Approve and activate (BRU-FIN-17). The previous active version of
        the source is superseded — kept, since earlier postings name it."""
        _require_manager(self.env, "Approving a posting rule")
        for rule in self:
            if rule.state != "tested":
                raise UserError("A posting rule is approved only after its fixtures pass (Tested).")
            _not_maker(self.env, rule.create_uid | rule.last_edited_by_id, "approve")
            passed, report = rule._run_fixtures()
            if not passed:
                raise UserError("The fixtures no longer pass:\n%s" % report)
            current = self.sudo().search(
                [
                    ("company_id", "=", rule.company_id.id),
                    ("source", "=", rule.source),
                    ("state", "=", "active"),
                    ("id", "!=", rule.id),
                ]
            )
            if current and any(c.effective_from > rule.effective_from for c in current):
                raise UserError(
                    "A newer version is effective from a later date; a version cannot take "
                    "effect before the one it replaces."
                )
            current._guarded().write({"state": "superseded"})
            rule._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "previous_version_id": current[:1].id or False,
                }
            )
            rule.message_post(body="Approved and activated by %s." % self.env.user.name)
        return True

    def action_retire(self):
        _require_manager(self.env, "Retiring a posting rule")
        for rule in self:
            if rule.state != "active":
                raise UserError("Only the active version is retired.")
            rule._guarded().write({"state": "retired"})
        return True

    def action_new_version(self):
        require_role(self.env, ACCOUNT_USER, "Drafting a new posting-rule version")
        self.ensure_one()
        if self.state == "draft":
            raise UserError("This version is still a draft: edit it.")
        new = self.copy(
            {"effective_from": max(self.effective_from, fields.Date.context_today(self))}
        )
        return {"res_model": self._name, "res_id": new.id, "code": new.code}

    # ----------------------------------------------------------- the engine
    @api.model
    def _in_force(self, company, source, on_date):
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("source", "=", source),
                ("state", "in", ("active", "superseded")),
                ("effective_from", "<=", on_date),
            ],
            order="effective_from desc, version desc",
            limit=1,
        )

    @api.model
    def _govern(self, move, source):
        """The version governing `move` for `source` (FR-FIN-008/010), after
        refusing any line on an account the version does not post to."""
        if source == "manual":
            return self.browse()
        rule = self._in_force(move.company_id, source, move.date or fields.Date.context_today(self))
        if not rule:
            return rule
        allowed = rule.line_ids.mapped("account_id")
        stray = move.line_ids.mapped("account_id") - allowed
        if stray:
            raise UserError(
                "Posting refused: posting rule %s governs %s postings and does not post to %s."
                % (rule.code, source, ", ".join(stray.mapped("display_name")))
            )
        return rule


class FixGlPostingRuleLine(models.Model):
    _name = "fix.gl.posting.rule.line"
    _description = "GL Posting Rule Line"
    _order = "rule_id, side desc, id"

    rule_id = fields.Many2one("fix.gl.posting.rule", required=True, ondelete="cascade", index=True)
    side = fields.Selection([("debit", "Debit"), ("credit", "Credit")], required=True)
    account_id = fields.Many2one("account.account", required=True, ondelete="restrict")
    share_percent = fields.Float(string="Share of Amount (%)", default=100.0, required=True)
    label = fields.Char()

    @api.constrains("share_percent")
    def _check_share(self):
        for line in self:
            if not 0 < line.share_percent <= 100:
                raise ValidationError("A line's share is between 0 and 100%.")

    def _guard_parent(self, rules):
        rules._assert_editable()

    @api.model_create_multi
    def create(self, vals_list):
        rules = self.env["fix.gl.posting.rule"].browse(
            [v.get("rule_id") for v in vals_list if v.get("rule_id")]
        )
        self._guard_parent(rules)
        lines = super().create(vals_list)
        lines.rule_id._content_changed()
        return lines

    def write(self, vals):
        self._guard_parent(self.rule_id)
        res = super().write(vals)
        self.rule_id._content_changed()
        return res

    def unlink(self):
        rules = self.rule_id
        self._guard_parent(rules)
        res = super().unlink()
        rules.exists()._content_changed()
        return res


class FixGlPostingRuleFixture(models.Model):
    """One expected ledger line for a sample amount; the rows sharing a
    sample amount are one test case."""

    _name = "fix.gl.posting.rule.fixture"
    _description = "GL Posting Rule Test Fixture"
    _order = "rule_id, sample_amount, id"

    rule_id = fields.Many2one("fix.gl.posting.rule", required=True, ondelete="cascade", index=True)
    currency_id = fields.Many2one(related="rule_id.company_id.currency_id")
    sample_amount = fields.Monetary(
        string="Sample Event Amount", required=True, currency_field="currency_id"
    )
    account_id = fields.Many2one(
        "account.account", string="Expected Account", required=True, ondelete="restrict"
    )
    expected_debit = fields.Monetary(currency_field="currency_id")
    expected_credit = fields.Monetary(currency_field="currency_id")

    @api.model_create_multi
    def create(self, vals_list):
        rules = self.env["fix.gl.posting.rule"].browse(
            [v.get("rule_id") for v in vals_list if v.get("rule_id")]
        )
        rules._assert_editable()
        rows = super().create(vals_list)
        rows.rule_id._content_changed()
        return rows

    def write(self, vals):
        self.rule_id._assert_editable()
        res = super().write(vals)
        self.rule_id._content_changed()
        return res

    def unlink(self):
        rules = self.rule_id
        rules._assert_editable()
        res = super().unlink()
        rules.exists()._content_changed()
        return res


class FixJournalPostingLogRule(models.Model):
    _inherit = "fix.journal.posting.log"

    posting_rule_id = fields.Many2one(
        "fix.gl.posting.rule", string="Posting Rule Version", readonly=True, ondelete="restrict"
    )


# =============================================================== page 4
class AccountFiscalYear(models.Model):
    _inherit = "account.fiscal.year"

    @api.constrains("date_from", "date_to")
    def _check_july_june(self):
        """BRU-FIN-19 (H): the fiscal year runs 1 July to 30 June."""
        for fy in self:
            if not fy.date_from or not fy.date_to:
                continue
            if (fy.date_from.month, fy.date_from.day) != (7, 1) or fy.date_to != (
                fy.date_from + relativedelta(years=1, days=-1)
            ):
                raise ValidationError(
                    "The Bangladesh fiscal year runs 1 July to 30 June (BRU-FIN-19); %s runs %s to %s."
                    % (fy.name, fy.date_from, fy.date_to)
                )


# =============================================================== page 6
class FixCurrencyRateEntry(models.Model):
    """A dated exchange rate by type (FR-FIN-033), entered by one person and
    approved by an Accounting Administrator who did not enter it. An approved
    spot or closing rate is published to the ledger's rate table, which the
    FX revaluation and every conversion read; a closing rate wins over a spot
    rate of the same day. Average and statutory/customs rates are kept here
    for reporting and customs only."""

    _name = "fix.currency.rate.entry"
    _description = "Exchange Rate (approved)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "rate_date desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company.root_id
    )
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    rate_type = fields.Selection(
        [
            ("spot", "Spot"),
            ("closing", "Closing (period end)"),
            ("average", "Average"),
            ("statutory", "Statutory / Customs"),
        ],
        required=True,
        default="spot",
    )
    rate_date = fields.Date(required=True, default=fields.Date.context_today)
    rate_bdt = fields.Float(string="BDT per 1 Unit", digits=(16, 6), required=True)
    source = fields.Selection(
        [
            ("bangladesh_bank", "Bangladesh Bank"),
            ("treasury", "Treasury (M50) bank rate"),
            ("manual", "Manual override"),
        ],
        required=True,
        default="bangladesh_bank",
    )
    source_ref = fields.Char(string="Source Reference")
    override_reason = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    entered_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)
    published_rate_id = fields.Many2one(
        "res.currency.rate", string="Ledger Rate", readonly=True, copy=False
    )

    _TERMS = (
        "company_id",
        "currency_id",
        "rate_type",
        "rate_date",
        "rate_bdt",
        "source",
        "source_ref",
        "override_reason",
    )

    @api.depends("currency_id", "rate_type", "rate_date", "rate_bdt")
    def _compute_name(self):
        for r in self:
            r.name = "%s %s %s = %s BDT" % (
                r.currency_id.name or "",
                r.rate_type or "",
                r.rate_date or "",
                r.rate_bdt or 0,
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "entered_by_id",
            "approved_by_id",
            "approved_at",
            "reject_reason",
            "published_rate_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(r.state != "draft" for r in self):
            locked |= set(self._TERMS)
        return locked

    @api.constrains("rate_bdt", "currency_id", "source", "override_reason")
    def _check_rate(self):
        for r in self:
            if r.rate_bdt <= 0:
                raise ValidationError("An exchange rate is greater than zero.")
            if r.currency_id == r.company_id.currency_id:
                raise ValidationError("The functional currency has no rate against itself.")
            if r.source == "manual" and not (r.override_reason or "").strip():
                raise ValidationError("A manual override states why the official rate is not used.")

    def write(self, vals):
        if (
            set(vals) & set(self._TERMS)
            and not self._fix_guard_open()
            and any(r.state != "draft" for r in self)
        ):
            raise UserError("A submitted rate is frozen; enter a new rate instead.")
        return super().write(vals)

    def unlink(self):
        if any(r.state not in ("draft", "rejected") for r in self) and not self.env.su:
            raise UserError("A submitted or approved rate is kept as evidence.")
        return super().unlink()

    def action_submit(self):
        require_role(self.env, ACCOUNT_USER, "Entering an exchange rate")
        for r in self:
            if r.state != "draft":
                raise UserError("Only a draft rate is submitted.")
            r._guarded().write({"state": "submitted", "entered_by_id": self.env.uid})
        return True

    def action_approve(self):
        _require_manager(self.env, "Approving an exchange rate")
        for r in self:
            if r.state != "submitted":
                raise UserError("The rate is not awaiting approval.")
            _not_maker(self.env, r.create_uid | r.entered_by_id, "approve")
            clash = self.sudo().search(
                [
                    ("id", "!=", r.id),
                    ("state", "=", "approved"),
                    ("company_id", "=", r.company_id.id),
                    ("currency_id", "=", r.currency_id.id),
                    ("rate_type", "=", r.rate_type),
                    ("rate_date", "=", r.rate_date),
                ],
                limit=1,
            )
            if clash:
                raise UserError(
                    "An approved %s rate for %s on %s already exists (%s)."
                    % (r.rate_type, r.currency_id.name, r.rate_date, clash.name)
                )
            r._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
            r._publish()
        return True

    def action_reject(self, reason=None):
        _require_manager(self.env, "Rejecting an exchange rate")
        for r in self:
            if r.state != "submitted":
                raise UserError("The rate is not awaiting approval.")
            r._guarded().write({"state": "rejected", "reject_reason": (reason or "Rejected")[:200]})
        return True

    def _publish(self):
        """Write the approved spot/closing rate into the ledger's rate table."""
        Rate = self.env["res.currency.rate"].sudo()
        for r in self:
            if r.rate_type not in ("spot", "closing"):
                continue
            row = Rate.search(
                [
                    ("currency_id", "=", r.currency_id.id),
                    ("name", "=", r.rate_date),
                    ("company_id", "=", r.company_id.id),
                ],
                limit=1,
            )
            if r.rate_type == "spot" and row:
                closing = self.sudo().search_count(
                    [
                        ("published_rate_id", "=", row.id),
                        ("rate_type", "=", "closing"),
                        ("state", "=", "approved"),
                    ]
                )
                if closing:
                    r.message_post(body="Not published: the closing rate of the day stands.")
                    continue
            vals = {"rate": 1.0 / r.rate_bdt}
            if row:
                row.write(vals)
            else:
                row = Rate.create(
                    dict(
                        vals,
                        currency_id=r.currency_id.id,
                        name=r.rate_date,
                        company_id=r.company_id.id,
                    )
                )
            # the inverse makes the stored rate exact against the company currency
            row.with_company(r.company_id).inverse_company_rate = r.rate_bdt
            r._guarded().write({"published_rate_id": row.id})
        return True


# =============================================================== page 8
class FixAuditorAccessGrant(models.Model):
    """Scoped, read-only, time-limited external auditor access (FR-FIN-043,
    BRU-FIN-26). Granted by an Accounting Administrator who did not request
    it, to a dedicated login that holds no right to change the books. While
    active the login holds the External Auditor group: read-only accounting,
    journal items limited to the granted entities and audited period. It
    lapses by itself at the end of the window (daily job) or on revocation;
    sign-ins in the window are counted from the login log."""

    _name = "fix.auditor.access.grant"
    _description = "External Auditor Access Grant"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    user_id = fields.Many2one(
        "res.users", string="Auditor Login", required=True, ondelete="restrict"
    )
    audit_firm_id = fields.Many2one("res.partner", string="Audit Firm")
    engagement_ref = fields.Char(string="Engagement Letter Ref", required=True)
    company_ids = fields.Many2many("res.company", string="Entities in Scope", required=True)
    period_from = fields.Date(string="Audited Period From", required=True)
    period_to = fields.Date(string="Audited Period To", required=True)
    valid_from = fields.Date(string="Access From", required=True, default=fields.Date.context_today)
    valid_to = fields.Date(string="Access Until", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired"), ("revoked", "Revoked")],
        default="draft",
        required=True,
        tracking=True,
    )
    granted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    granted_at = fields.Datetime(readonly=True, copy=False)
    ended_by_id = fields.Many2one("res.users", string="Revoked By", readonly=True, copy=False)
    ended_at = fields.Datetime(readonly=True, copy=False)
    end_reason = fields.Char(readonly=True, copy=False)
    login_count = fields.Integer(compute="_compute_access_log", string="Sign-ins in Window")
    last_login = fields.Datetime(compute="_compute_access_log", string="Last Sign-in")

    _TERMS = (
        "user_id",
        "audit_firm_id",
        "engagement_ref",
        "company_ids",
        "period_from",
        "period_to",
        "valid_from",
        "valid_to",
    )

    @api.depends("user_id", "audit_firm_id", "valid_to")
    def _compute_name(self):
        for g in self:
            g.name = "Audit access %s%s until %s" % (
                g.user_id.name or "",
                " (%s)" % g.audit_firm_id.name if g.audit_firm_id else "",
                g.valid_to or "",
            )

    def _compute_access_log(self):
        Log = self.env["res.users.log"].sudo()
        for g in self:
            if not g.user_id or not g.granted_at:
                g.login_count, g.last_login = 0, False
                continue
            end = fields.Datetime.to_datetime(g.ended_at or (g.valid_to + timedelta(days=1)))
            rows = Log.search(
                [
                    ("create_uid", "=", g.user_id.id),
                    ("create_date", ">=", g.granted_at),
                    ("create_date", "<", end),
                ],
                order="create_date desc",
            )
            g.login_count = len(rows)
            g.last_login = rows[:1].create_date

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "granted_by_id",
            "granted_at",
            "ended_by_id",
            "ended_at",
            "end_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(g.state != "draft" for g in self):
            locked |= set(self._TERMS)
        return locked

    @api.constrains("period_from", "period_to", "valid_from", "valid_to")
    def _check_dates(self):
        max_days = int(
            self.env["ir.config_parameter"].sudo().get_param(PARAM_AUDIT_MAX_DAYS)
            or DEFAULT_AUDIT_MAX_DAYS
        )
        for g in self:
            if g.period_from > g.period_to:
                raise ValidationError("The audited period ends after it starts.")
            if g.valid_from > g.valid_to:
                raise ValidationError("Access ends after it starts.")
            if (g.valid_to - g.valid_from).days > max_days:
                raise ValidationError(
                    "External auditor access is time-limited: at most %d days (%s)."
                    % (max_days, PARAM_AUDIT_MAX_DAYS)
                )

    def write(self, vals):
        if (
            set(vals) & set(self._TERMS)
            and not self._fix_guard_open()
            and any(g.state != "draft" for g in self)
        ):
            raise UserError("A granted access is frozen; revoke it and grant a new one.")
        return super().write(vals)

    def unlink(self):
        if any(g.state != "draft" for g in self) and not self.env.su:
            raise UserError("A granted access is kept as evidence.")
        return super().unlink()

    def action_grant(self):
        _require_manager(self.env, "Granting external auditor access")
        today = fields.Date.context_today(self)
        group = self.env.ref(AUDITOR_GROUP)
        for g in self:
            if g.state != "draft":
                raise UserError("Only a draft grant is granted.")
            _not_maker(self.env, g.create_uid, "grant")
            if g.valid_to < today:
                raise UserError("The access window has already ended.")
            user = g.user_id.sudo()
            if user.share:
                raise UserError(
                    "The auditor needs an internal (read-only) login, not a portal one."
                )
            for xmlid in WRITE_GROUPS:
                if user.has_group(xmlid):
                    raise UserError(
                        "%s holds %s and could change the books: an external auditor's login is "
                        "read-only (BRU-FIN-26). Use a dedicated login."
                        % (user.name, self.env.ref(xmlid).display_name)
                    )
            outside = user.company_ids - g.company_ids
            if outside:
                raise UserError(
                    "%s may open entities outside the grant (%s): narrow the login's companies "
                    "first." % (user.name, ", ".join(outside.mapped("name")))
                )
            other = self.sudo().search(
                [("user_id", "=", user.id), ("state", "=", "active"), ("id", "!=", g.id)], limit=1
            )
            if other:
                raise UserError("%s already holds an active grant (%s)." % (user.name, other.name))
            g._guarded().write(
                {
                    "state": "active",
                    "granted_by_id": self.env.uid,
                    "granted_at": fields.Datetime.now(),
                }
            )
            user.write({"group_ids": [(4, group.id)]})
            g.message_post(body="Read-only access granted by %s." % self.env.user.name)
        return True

    def _end(self, state, reason):
        group = self.env.ref(AUDITOR_GROUP)
        for g in self:
            g._guarded().write(
                {
                    "state": state,
                    "ended_by_id": self.env.uid if state == "revoked" else False,
                    "ended_at": fields.Datetime.now(),
                    "end_reason": reason[:200],
                }
            )
            still = self.sudo().search_count(
                [("user_id", "=", g.user_id.id), ("state", "=", "active")]
            )
            if not still:
                g.user_id.sudo().write({"group_ids": [(3, group.id)]})
            g.message_post(body="Access ended (%s): %s" % (state, reason))

    def action_revoke(self, reason=None):
        _require_manager(self.env, "Revoking external auditor access")
        for g in self:
            if g.state != "active":
                raise UserError("Only an active grant is revoked.")
        self._end("revoked", reason or "Revoked by %s" % self.env.user.name)
        return True

    @api.model
    def _cron_expire(self):
        due = self.sudo().search(
            [("state", "=", "active"), ("valid_to", "<", fields.Date.context_today(self))]
        )
        due._end("expired", "Access window ended")
        return len(due)


class ResUsersAuditScope(models.Model):
    _inherit = "res.users"

    fix_audit_period_from = fields.Date(compute="_compute_fix_audit_scope", compute_sudo=True)
    fix_audit_period_to = fields.Date(compute="_compute_fix_audit_scope", compute_sudo=True)
    fix_audit_company_ids = fields.Many2many(
        "res.company", compute="_compute_fix_audit_scope", compute_sudo=True
    )

    def _compute_fix_audit_scope(self):
        Grant = self.env["fix.auditor.access.grant"].sudo()
        for user in self:
            grant = Grant.search([("user_id", "=", user.id), ("state", "=", "active")], limit=1)
            user.fix_audit_period_from = grant.period_from
            user.fix_audit_period_to = grant.period_to
            user.fix_audit_company_ids = grant.company_ids
