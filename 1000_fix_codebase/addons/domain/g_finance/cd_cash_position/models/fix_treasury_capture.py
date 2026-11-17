# cd_cash_position: M50 sub-module capture audit (2026-11-17).
#
# Five spec records that the M50 workspace had no way to capture:
#
#   * fix.bank.mandate (FR-TRE-002 P0, BRU-TRE-20 H): who may sign on each
#     bank account, up to what amount, alone or jointly, from when to when.
#     Approved by an Accounting Administrator other than the requester, never
#     edited afterwards, and superseded rather than changed, so the full
#     history stays. The old free-text "Authorised Signatories" note on the
#     bank journal could be overwritten by anyone and kept no history.
#   * fix.bank.matching.rule (FR-TRE-008 P0, FR-TRE-010 P0): rules that
#     recognise bank-originated entries (charges, interest, tax deducted on
#     interest, unadvised debits) by narration keywords, direction and amount
#     band. A rule is approved by a second person, frozen, and changed only
#     by a new version. After the document matching layers, auto-match
#     applies the approved rules, so these lines are booked instead of
#     sitting in the exception queue.
#   * fix.settlement.exception (FR-TRE-027 P0, BRU-TRE-10 H): a case for a
#     gateway / MFS settlement line that did not match, with a named owner,
#     the provider's case reference, its age and an approved resolution.
#     Previously the Settlement Exceptions list could not be acted on.
#   * fix.cash.forecast.version (FR-TRE-038 P1, BRU-TRE-26 H): a frozen copy
#     of the 13-week forecast. The forecast was only computed live, so what
#     had been forecast was never kept and accuracy could not be measured.
#   * fix.fx.conversion (FR-TRE-042 P1): a currency conversion between two of
#     our bank accounts, with the rate achieved, the realised difference
#     against the book rate, and the GL entry. The FX page captured nothing.
from __future__ import annotations

import logging
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    require_other_person,
    require_role,
    treasury_account,
    treasury_alert,
)

_logger = logging.getLogger(__name__)

LOCK_EXEMPT = {"message_main_attachment_id"}


def _locked_write(records, vals, open_states, what):
    """Refuse a plain write to a record that has left its editable states."""
    trusted = records.env.su or records._fix_guard_has_token()
    if trusted or not set(vals) - LOCK_EXEMPT:
        return
    if any(rec.state not in open_states for rec in records):
        raise UserError("%s is a record of what was decided and cannot be edited." % what)


# --------------------------------------------------------------------------- mandates
MANDATE_CLASSES = [
    ("sole", "Signs alone"),
    ("any_two", "Jointly with any other signatory"),
    ("joint_with", "Jointly with a named signatory"),
]


class FixBankMandate(models.Model):
    """One signatory's authority on one bank account."""

    _name = "fix.bank.mandate"
    _description = "Bank Mandate (Signatory Authority)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "journal_id, state, valid_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        required=True,
        index=True,
        domain=[("type", "=", "bank")],
    )
    company_id = fields.Many2one(related="journal_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", compute="_compute_currency", string="Currency", store=True
    )
    signatory_id = fields.Many2one("hr.employee", string="Signatory", required=True, index=True)
    signing_class = fields.Selection(
        MANDATE_CLASSES, string="Signing Rule", required=True, default="sole"
    )
    joint_with_ids = fields.Many2many(
        "hr.employee",
        "fix_bank_mandate_joint_rel",
        "mandate_id",
        "employee_id",
        string="Signs Jointly With",
    )
    unlimited = fields.Boolean(string="No Amount Limit")
    limit_amount = fields.Monetary(string="Limit per Instrument", currency_field="currency_id")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    authority_ref = fields.Char(
        string="Board Resolution / Bank Letter",
        required=True,
        help="The board resolution or bank mandate letter that grants this authority.",
    )
    supersedes_id = fields.Many2one(
        "fix.bank.mandate",
        string="Replaces Mandate",
        index=True,
        help="The active mandate this one replaces once approved.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("active", "Active"),
            ("superseded", "Superseded"),
            ("revoked", "Revoked"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    requested_at = fields.Datetime(readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    ended_by_id = fields.Many2one("res.users", string="Ended By", readonly=True, copy=False)
    ended_at = fields.Datetime(readonly=True, copy=False)
    end_reason = fields.Char(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_at",
            "approved_by_id",
            "approved_at",
            "ended_by_id",
            "ended_at",
            "end_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(m.state != "draft" for m in self):
            locked |= {
                "journal_id",
                "signatory_id",
                "signing_class",
                "joint_with_ids",
                "unlimited",
                "limit_amount",
                "valid_from",
                "valid_to",
                "authority_ref",
                "supersedes_id",
            }
        return locked

    @api.depends("journal_id", "signatory_id")
    def _compute_name(self):
        for m in self:
            m.name = "%s / %s" % (m.journal_id.name or "?", m.signatory_id.name or "?")

    @api.depends("journal_id")
    def _compute_currency(self):
        for m in self:
            m.currency_id = m.journal_id.currency_id or m.journal_id.company_id.currency_id

    @api.constrains(
        "journal_id",
        "signing_class",
        "joint_with_ids",
        "unlimited",
        "limit_amount",
        "valid_from",
        "valid_to",
        "supersedes_id",
        "signatory_id",
    )
    def _check_mandate(self):
        for m in self:
            if m.journal_id.type != "bank":
                raise ValidationError("A mandate is given on a bank account.")
            if m.valid_to and m.valid_to < m.valid_from:
                raise ValidationError("The mandate ends before it starts.")
            if not m.unlimited and m.limit_amount <= 0:
                raise ValidationError(
                    "Give the signatory's limit per instrument, or tick No Amount Limit."
                )
            if m.signing_class == "joint_with":
                if not m.joint_with_ids:
                    raise ValidationError("Name who the signatory must sign jointly with.")
                if m.signatory_id in m.joint_with_ids:
                    raise ValidationError("A signatory cannot sign jointly with themselves.")
            if m.supersedes_id and (
                m.supersedes_id.journal_id != m.journal_id or m.supersedes_id == m
            ):
                raise ValidationError("A mandate replaces another mandate on the same account.")

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted mandate")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(m.state != "draft" for m in self):
            raise UserError("A submitted mandate is kept as history; revoke it instead.")
        return super().unlink()

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a bank mandate")
        for m in self:
            if m.state != "draft":
                raise UserError("Only a draft mandate is submitted.")
            if m.supersedes_id and m.supersedes_id.state != "active":
                raise UserError(
                    "%s is not active: there is nothing to replace." % m.supersedes_id.name
                )
            m._guarded().write(
                {
                    "state": "submitted",
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        """BRU-TRE-20: approved by an Accounting Administrator who did not
        request it (the CFO tier, until a CFO group exists)."""
        require_role(self.env, GROUP_ADMIN, "Approving a bank mandate")
        now = fields.Datetime.now()
        for m in self:
            if m.state != "submitted":
                raise UserError("Only a submitted mandate is approved.")
            require_other_person(
                self.env, m.requested_by_id | m.create_uid, "Approving mandate %s" % m.name
            )
            if m.supersedes_id:
                old = m.supersedes_id
                if old.state != "active":
                    raise UserError("%s is no longer active." % old.name)
                old._guarded().write(
                    {
                        "state": "superseded",
                        "ended_by_id": self.env.uid,
                        "ended_at": now,
                        "end_reason": "Replaced by %s (%s)" % (m.name, m.authority_ref),
                    }
                )
            m._guarded().write(
                {"state": "active", "approved_by_id": self.env.uid, "approved_at": now}
            )
            m.journal_id.message_post(
                body="Mandate approved: %s, %s." % (m.name, m._authority_label())
            )
        return True

    def action_reject(self, reason=None):
        require_role(self.env, GROUP_ADMIN, "Rejecting a bank mandate")
        if not (reason or "").strip():
            raise UserError("Say why the mandate is rejected.")
        for m in self:
            if m.state != "submitted":
                raise UserError("Only a submitted mandate is rejected.")
            m._guarded().write(
                {
                    "state": "rejected",
                    "ended_by_id": self.env.uid,
                    "ended_at": fields.Datetime.now(),
                    "end_reason": reason.strip(),
                }
            )
        return True

    def action_revoke(self, reason=None):
        """A signatory leaves or the board withdraws the authority."""
        require_role(self.env, GROUP_ADMIN, "Revoking a bank mandate")
        if not (reason or "").strip():
            raise UserError("Give the reason and the board or bank reference for the revocation.")
        for m in self:
            if m.state != "active":
                raise UserError("Only an active mandate is revoked.")
            m._guarded().write(
                {
                    "state": "revoked",
                    "ended_by_id": self.env.uid,
                    "ended_at": fields.Datetime.now(),
                    "end_reason": reason.strip(),
                }
            )
        return True

    def _authority_label(self):
        self.ensure_one()
        limit = "no limit" if self.unlimited else "up to %.2f" % self.limit_amount
        rule = dict(MANDATE_CLASSES)[self.signing_class]
        if self.signing_class == "joint_with":
            rule = "jointly with %s" % ", ".join(self.joint_with_ids.mapped("name"))
        return "%s, %s" % (rule, limit)


class AccountJournalMandates(models.Model):
    _inherit = "account.journal"

    fix_mandate_ids = fields.One2many("fix.bank.mandate", "journal_id", string="Mandates")
    fix_active_signatories = fields.Char(
        string="Active Signatories", compute="_compute_fix_active_signatories"
    )

    def _compute_fix_active_signatories(self):
        today = fields.Date.context_today(self)
        for journal in self:
            active = journal.fix_mandate_ids.filtered(
                lambda m: m.state == "active"
                and m.valid_from <= today
                and (not m.valid_to or m.valid_to >= today)
            )
            journal.fix_active_signatories = "; ".join(
                "%s (%s)" % (m.signatory_id.name, m._authority_label()) for m in active
            )


# --------------------------------------------------------------------------- matching rules
RULE_CLASSES = [
    ("bank_charge", "Bank charge"),
    ("interest_income", "Interest received"),
    ("interest_expense", "Interest charged"),
    ("tax_on_interest", "Tax deducted on interest (AIT)"),
    ("unadvised", "Unadvised debit (investigate)"),
]
# classification -> (direction it must have, account role it posts to)
RULE_POSTING = {
    "bank_charge": ("debit", "bank_charges"),
    "interest_expense": ("debit", "interest_expense"),
    "tax_on_interest": ("debit", "tax_on_interest"),
    "interest_income": ("credit", "interest_income"),
    "unadvised": ("debit", None),
}


class FixBankMatchingRule(models.Model):
    """A rule that recognises a bank-originated statement line."""

    _name = "fix.bank.matching.rule"
    _description = "Bank Statement Matching Rule"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "sequence, id"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        domain=[("type", "=", "bank")],
        help="Empty: every bank account of the company.",
    )
    sequence = fields.Integer(string="Priority", default=10, help="Lower runs first.")
    classification = fields.Selection(RULE_CLASSES, required=True)
    direction = fields.Selection(
        [("debit", "Money out (debit)"), ("credit", "Money in (credit)")], required=True
    )
    keywords = fields.Char(
        required=True,
        help="Comma-separated words or phrases; the rule applies when the line's narration "
        "or reference contains any of them (case does not matter).",
    )
    amount_min = fields.Float(string="Amount From", help="Empty: no lower bound.")
    amount_max = fields.Float(string="Amount Up To", help="Empty: no upper bound.")
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    version = fields.Integer(default=1, readonly=True, copy=False)
    previous_id = fields.Many2one(
        "fix.bank.matching.rule", string="Previous Version", readonly=True, copy=False
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("retired", "Retired"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
        copy=False,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    line_ids = fields.One2many("fix.bank.statement.line", "matching_rule_id", string="Lines")
    line_count = fields.Integer(string="Lines Classified", compute="_compute_line_count")
    last_test = fields.Char(string="Last Test", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "previous_id",
            "requested_by_id",
            "approved_by_id",
            "approved_at",
            "last_test",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {
                "name",
                "company_id",
                "journal_id",
                "sequence",
                "classification",
                "direction",
                "keywords",
                "amount_min",
                "amount_max",
                "effective_from",
            }
        return locked

    def _compute_line_count(self):
        for rule in self:
            rule.line_count = len(rule.line_ids)

    @api.constrains("classification", "direction", "amount_min", "amount_max", "keywords", "name")
    def _check_rule(self):
        for rule in self:
            want = RULE_POSTING[rule.classification][0]
            if rule.classification != "unadvised" and rule.direction != want:
                raise ValidationError(
                    "%s is money %s the account: set the direction to %s."
                    % (
                        dict(RULE_CLASSES)[rule.classification],
                        "out of" if want == "debit" else "into",
                        "Money out (debit)" if want == "debit" else "Money in (credit)",
                    )
                )
            if rule.classification == "unadvised" and rule.direction != "debit":
                raise ValidationError("An unadvised entry is a debit the bank did not advise.")
            if rule.amount_min < 0 or rule.amount_max < 0:
                raise ValidationError("Amount bounds are positive amounts.")
            if rule.amount_max and rule.amount_min > rule.amount_max:
                raise ValidationError("The lower bound is above the upper bound.")
            if not rule._keyword_list():
                raise ValidationError("Give at least one keyword of three or more characters.")

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted matching rule")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(r.state != "draft" for r in self):
            raise UserError("A submitted rule is kept as history; retire it instead.")
        return super().unlink()

    def _keyword_list(self):
        return [k.strip().lower() for k in (self.keywords or "").split(",") if len(k.strip()) >= 3]

    def _matches(self, line):
        self.ensure_one()
        if self.journal_id and line.journal_id != self.journal_id:
            return False
        if self.company_id != line.company_id or line.date < self.effective_from:
            return False
        if (line.amount < 0) != (self.direction == "debit") or not line.amount:
            return False
        amount = abs(line.amount)
        if self.amount_min and amount < self.amount_min - 0.005:
            return False
        if self.amount_max and amount > self.amount_max + 0.005:
            return False
        text = " ".join(filter(None, [line.narration, line.reference])).lower()
        text = re.sub(r"\s+", " ", text)
        return any(k in text for k in self._keyword_list())

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a matching rule")
        for rule in self:
            if rule.state != "draft":
                raise UserError("Only a draft rule is submitted.")
            rule._guarded().write({"state": "submitted", "requested_by_id": self.env.uid})
        return True

    def action_approve(self):
        """FR-TRE-008: a rule books entries without a person looking at each
        one, so a second person approves it. The approved rule is frozen; a
        new version retires it when that version is approved."""
        require_role(self.env, GROUP_ADMIN, "Approving a matching rule")
        for rule in self:
            if rule.state != "submitted":
                raise UserError("Only a submitted rule is approved.")
            require_other_person(
                self.env, rule.requested_by_id | rule.create_uid, "Approving rule %s" % rule.name
            )
            if rule.classification != "unadvised":
                treasury_account(self.env, rule.company_id, RULE_POSTING[rule.classification][1])
            if rule.previous_id and rule.previous_id.state == "approved":
                rule.previous_id._guarded().write({"state": "retired"})
            rule._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self):
        require_role(self.env, GROUP_ADMIN, "Returning a matching rule")
        self.filtered(lambda r: r.state == "submitted")._guarded().write({"state": "draft"})
        return True

    def action_retire(self):
        require_role(self.env, GROUP_ADMIN, "Retiring a matching rule")
        for rule in self:
            if rule.state != "approved":
                raise UserError("Only an approved rule is retired.")
            rule._guarded().write({"state": "retired"})
        return True

    def action_new_version(self):
        """A draft copy to change; the approved version keeps running until
        the new one is approved."""
        require_role(self.env, GROUP_ACCOUNTANT, "Revising a matching rule")
        for rule in self:
            if rule.state != "approved":
                raise UserError("A new version is made from the approved rule.")
            if self.search_count(
                [("previous_id", "=", rule.id), ("state", "in", ("draft", "submitted"))]
            ):
                raise UserError("A new version of %s is already in progress." % rule.name)
            rule.copy()._guarded().write({"version": rule.version + 1, "previous_id": rule.id})
        return True

    def action_test(self):
        """Dry run: the unmatched imported lines this rule would classify now."""
        require_role(self.env, GROUP_ACCOUNTANT, "Testing a matching rule")
        Line = self.env["fix.bank.statement.line"]
        for rule in self:
            pending = Line.search(
                [
                    ("company_id", "=", rule.company_id.id),
                    ("match_state", "=", "unmatched"),
                    ("statement_file_hash", "!=", False),
                ]
            )
            hits = pending.filtered(rule._matches)
            label = "%s of %s unmatched lines on %s (%.2f)" % (
                len(hits),
                len(pending),
                fields.Date.context_today(rule),
                sum(abs(a) for a in hits.mapped("amount")),
            )
            rule._guarded().write({"last_test": label})
            rule.message_post(body="Test: %s would be classified." % label)
        return True


class FixStatementLineRules(models.Model):
    _inherit = "fix.bank.statement.line"

    matched_kind = fields.Selection(
        selection_add=[("external", "Bank-Originated Entry")],
        ondelete={"external": "set null"},
    )
    matching_rule_id = fields.Many2one(
        "fix.bank.matching.rule", string="Matching Rule", readonly=True, index=True, copy=False
    )
    external_class = fields.Selection(
        RULE_CLASSES, string="Bank-Originated As", readonly=True, copy=False
    )
    external_move_id = fields.Many2one(
        "account.move", string="Bank Entry Posted", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "matching_rule_id",
            "external_class",
            "external_move_id",
        }

    @api.constrains(
        "match_state",
        "matched_kind",
        "matched_payment_id",
        "matched_deposit_id",
        "matched_cheque_id",
        "matched_gateway_id",
        "charge_move_id",
        "external_move_id",
    )
    def _check_matched_to_something(self):
        external = self.filtered(lambda ln: ln.matched_kind == "external" and ln.external_move_id)
        return super(FixStatementLineRules, self - external)._check_matched_to_something()

    def auto_match(self) -> int:
        """The document layers first, then the approved bank-originated
        rules over whatever is still unmatched."""
        matched = super().auto_match()
        return matched + self._fix_apply_rules()

    def action_apply_rules(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Applying the matching rules")
        return self._fix_apply_rules(self.filtered(lambda ln: ln.match_state == "unmatched"))

    def _fix_apply_rules(self, lines=None) -> int:
        if lines is None:
            lines = self.search(
                [
                    ("match_state", "=", "unmatched"),
                    ("statement_file_hash", "!=", False),
                    ("company_id", "in", self.env.companies.ids),
                ]
            )
        lines = lines.filtered(lambda ln: ln.statement_file_hash and not ln.external_class)
        if not lines:
            return 0
        Rule = self.env["fix.bank.matching.rule"].sudo()
        rules = Rule.search(
            [("state", "=", "approved"), ("company_id", "in", lines.company_id.ids)],
            order="sequence, id",
        )
        booked = 0
        for line in lines:
            rule = next((r for r in rules if r._matches(line)), None)
            if not rule:
                continue
            try:
                with self.env.cr.savepoint():
                    booked += line._fix_book_external(rule)
            except (UserError, ValidationError) as exc:
                self.env.invalidate_all(flush=False)
                _logger.warning("matching rule %s skipped line %s: %s", rule.id, line.id, exc)
        return booked

    def _fix_book_external(self, rule) -> int:
        """Post the bank-originated entry the approved rule describes."""
        self.ensure_one()
        from .treasury_common import post_treasury_move

        if rule.classification == "unadvised":
            self._guarded().write({"matching_rule_id": rule.id, "external_class": "unadvised"})
            treasury_alert(
                self,
                "Unadvised bank debit",
                "%s: %.2f on %s (%s) matched rule %s. Ask the bank for the advice before "
                "it is booked."
                % (self.journal_id.name, self.amount, self.date, self.narration or "", rule.name),
            )
            return 0
        bank = bank_account_of(self.journal_id)
        account = treasury_account(self.env, self.company_id, RULE_POSTING[rule.classification][1])
        amount = abs(self.amount)
        label = "%s: %s" % (
            dict(RULE_CLASSES)[rule.classification],
            self.narration or self.reference or "",
        )
        if self.amount < 0:
            lines = [(account, label, amount, 0.0, None), (bank, label, 0.0, amount, None)]
        else:
            lines = [(bank, label, amount, 0.0, None), (account, label, 0.0, amount, None)]
        move = post_treasury_move(
            self.env(su=True),
            self.company_id,
            self.date,
            "BANK %s %s" % (rule.classification.upper(), self.reference or self.id),
            lines,
            source="treasury",
        )
        self._guarded().write(
            {
                "match_state": "auto",
                "matched_kind": "external",
                "matching_rule_id": rule.id,
                "external_class": rule.classification,
                "external_move_id": move.id,
                "is_bank_charge": rule.classification == "bank_charge",
                "charge_move_id": move.id if rule.classification == "bank_charge" else False,
            }
        )
        return 1


# --------------------------------------------------------------------------- settlement exceptions
EXCEPTION_TYPES = [
    ("settled_not_recorded", "Settled, no receipt booked"),
    ("value_mismatch", "Settled at a different value"),
    ("duplicate", "Duplicate transaction"),
    ("refund_chargeback", "Refund / chargeback"),
]
LINE_STATE_TYPE = {
    "missing_receipt": "settled_not_recorded",
    "amount_mismatch": "value_mismatch",
    "duplicate": "duplicate",
    "refund": "refund_chargeback",
}
RESOLUTIONS = [
    ("receipt_booked", "Receipt booked: the line now matches"),
    ("provider_corrected", "Provider corrected its report"),
    ("refund_confirmed", "Refund / chargeback confirmed"),
    ("duplicate_confirmed", "Duplicate confirmed with the provider"),
]
OVERDUE_DAYS = 7  # BRU-TRE-10


class FixSettlementException(models.Model):
    """A case for one settlement line that did not match."""

    _name = "fix.settlement.exception"
    _description = "Settlement Exception Case"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, opened_on, id"

    name = fields.Char(readonly=True, copy=False, default="New")
    line_id = fields.Many2one(
        "fix.gateway.settlement.line",
        string="Settlement Line",
        required=True,
        index=True,
        domain=[("match_state", "!=", "matched")],
    )
    batch_id = fields.Many2one(related="line_id.batch_id", store=True, string="Settlement")
    provider = fields.Selection(related="line_id.provider", store=True)
    company_id = fields.Many2one(related="line_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="line_id.operating_unit_id", store=True, index=True)
    currency_id = fields.Many2one(related="line_id.currency_id")
    trx_id = fields.Char(related="line_id.trx_id", string="Transaction ID")
    exception_type = fields.Selection(EXCEPTION_TYPES, readonly=True)
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True, default=lambda self: self.env.user
    )
    provider_case_ref = fields.Char(string="Provider Case / Ticket")
    opened_on = fields.Date(readonly=True, default=fields.Date.context_today)
    age_days = fields.Integer(compute="_compute_age", string="Age (days)")
    overdue = fields.Boolean(compute="_compute_age", string="Over 7 Days")
    resolution = fields.Selection(RESOLUTIONS, readonly=True, copy=False)
    resolution_note = fields.Char(readonly=True, copy=False)
    proposed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    resolved_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("open", "Open"),
            ("with_provider", "Raised with Provider"),
            ("proposed", "Resolution Proposed"),
            ("resolved", "Resolved"),
        ],
        default="open",
        required=True,
        tracking=True,
        index=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "exception_type",
            "amount",
            "opened_on",
            "resolution",
            "resolution_note",
            "proposed_by_id",
            "resolved_by_id",
            "resolved_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"line_id"}
        return locked

    @api.depends("opened_on", "resolved_on", "state")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for case in self:
            end = case.resolved_on or today
            case.age_days = (end - case.opened_on).days if case.opened_on else 0
            case.overdue = case.state != "resolved" and case.age_days > OVERDUE_DAYS

    @api.constrains("line_id", "owner_id")
    def _check_case(self):
        for case in self:
            if case.line_id.match_state == "matched" and case.state != "resolved":
                raise ValidationError(
                    "%s matched: there is no exception to work." % case.line_id.trx_id
                )
            if self.search_count(
                [
                    ("line_id", "=", case.line_id.id),
                    ("state", "!=", "resolved"),
                    ("id", "!=", case.id),
                ]
            ):
                raise ValidationError(
                    "Settlement line %s already has an open case." % case.line_id.trx_id
                )
            if case.owner_id.share:
                raise ValidationError("The owner is a member of staff.")

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Opening a settlement exception case")
        records = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for case in records:
            case._guarded().write(
                {
                    "name": Seq.next_by_code("fix.settlement.exception") or "SXC/%s" % case.id,
                    "exception_type": LINE_STATE_TYPE.get(
                        case.line_id.match_state, "settled_not_recorded"
                    ),
                    "amount": case.line_id.gross,
                    "opened_on": fields.Date.context_today(case),
                }
            )
        return records

    def write(self, vals):
        _locked_write(self, vals, ("open", "with_provider"), "A case with a proposed resolution")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Settlement exception cases are kept; resolve them instead.")
        return super().unlink()

    def action_raise_with_provider(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Raising a case with the provider")
        for case in self:
            if case.state != "open":
                raise UserError("Only an open case is raised with the provider.")
            if not (case.provider_case_ref or "").strip():
                raise UserError("Record the provider's case or ticket number first.")
            case._guarded().write({"state": "with_provider"})
        return True

    def action_propose(self, resolution=None, note=None):
        require_role(self.env, GROUP_ACCOUNTANT, "Proposing a resolution")
        if resolution not in dict(RESOLUTIONS):
            raise UserError("Choose the resolution: %s." % ", ".join(k for k, _l in RESOLUTIONS))
        if not (note or "").strip():
            raise UserError("Describe the evidence for the resolution.")
        for case in self:
            if case.state not in ("open", "with_provider"):
                raise UserError("A resolution is proposed on an open case.")
            if resolution == "receipt_booked":
                case.line_id.sudo()._match_receipt()
                if case.line_id.match_state != "matched":
                    raise UserError(
                        "Settlement line %s still does not match a booked receipt."
                        % case.line_id.trx_id
                    )
            case._guarded().write(
                {
                    "state": "proposed",
                    "resolution": resolution,
                    "resolution_note": note.strip(),
                    "proposed_by_id": self.env.uid,
                }
            )
        return True

    def action_approve(self):
        """A second person accepts the resolution; the batch re-runs its match."""
        require_role(self.env, GROUP_ADMIN, "Approving a settlement resolution")
        for case in self:
            if case.state != "proposed":
                raise UserError("Only a proposed resolution is approved.")
            require_other_person(
                self.env, case.proposed_by_id, "Approving the resolution of %s" % case.name
            )
            case._guarded().write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.uid,
                    "resolved_on": fields.Date.context_today(case),
                }
            )
            batch = case.line_id.batch_id.sudo()
            if batch.state in ("imported", "exceptions"):
                batch.action_match()
        return True

    def action_return(self, reason=None):
        require_role(self.env, GROUP_ADMIN, "Returning a settlement resolution")
        if not (reason or "").strip():
            raise UserError("Say why the resolution is returned.")
        for case in self:
            if case.state != "proposed":
                raise UserError("Only a proposed resolution is returned.")
            case._guarded().write(
                {
                    "state": "with_provider" if case.provider_case_ref else "open",
                    "resolution": False,
                    "proposed_by_id": False,
                }
            )
            case.message_post(body="Resolution returned: %s" % reason.strip())
        return True

    @api.model
    def _cron_overdue(self):
        """BRU-TRE-10: a line unmatched for more than 7 days is a reportable
        exception with a named owner."""
        today = fields.Date.context_today(self)
        limit = today - timedelta(days=OVERDUE_DAYS)
        Line = self.env["fix.gateway.settlement.line"].sudo()
        for line in Line.search(
            [("match_state", "!=", "matched"), ("batch_id.settlement_date", "<", limit)]
        ):
            if not self.sudo().search_count([("line_id", "=", line.id)]):
                treasury_alert(
                    line.batch_id,
                    "Settlement exception without an owner",
                    "%s %s (%.2f) has been unmatched for over %s days with no case."
                    % (line.provider, line.trx_id, line.gross, OVERDUE_DAYS),
                )
        overdue = self.sudo().search([("state", "!=", "resolved"), ("opened_on", "<", limit)])
        for case in overdue.filtered(lambda c: not c.activity_ids):
            case.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Settlement exception over 7 days",
                note="%s is %s days old." % (case.name, case.age_days),
                user_id=case.owner_id.id,
            )
        return True


class FixGatewayLineCase(models.Model):
    _inherit = "fix.gateway.settlement.line"

    exception_case_ids = fields.One2many(
        "fix.settlement.exception", "line_id", string="Exception Cases"
    )
    open_case_id = fields.Many2one(
        "fix.settlement.exception", compute="_compute_open_case", string="Open Case"
    )

    @api.depends("exception_case_ids.state")
    def _compute_open_case(self):
        for line in self:
            line.open_case_id = line.exception_case_ids.filtered(lambda c: c.state != "resolved")[
                :1
            ]

    def action_open_case(self):
        """Open a case owned by the person who opens it (BRU-TRE-10)."""
        Case = self.env["fix.settlement.exception"]
        for line in self:
            if line.match_state == "matched":
                raise UserError("%s matched: there is no exception to work." % line.trx_id)
            if line.open_case_id:
                raise UserError("%s already has case %s." % (line.trx_id, line.open_case_id.name))
            Case.create({"line_id": line.id, "owner_id": self.env.uid})
        return True


# --------------------------------------------------------------------------- forecast versions
class FixCashForecastVersion(models.Model):
    """A frozen copy of the 13-week forecast (BRU-TRE-26)."""

    _name = "fix.cash.forecast.version"
    _description = "Cash Forecast Version"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "generated_at desc, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    scenario = fields.Selection(
        [("base", "Base case"), ("conservative", "Conservative"), ("stress", "Stress")],
        required=True,
        default="base",
    )
    assumptions = fields.Text(
        required=True,
        help="What this version assumes: collection terms, payment timing, one-off items.",
    )
    generated_at = fields.Datetime(readonly=True, copy=False)
    generated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    week_start = fields.Date(string="First Week", readonly=True, copy=False)
    opening_balance = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    line_ids = fields.One2many("fix.cash.forecast.version.line", "version_id", string="Weeks")
    measured_weeks = fields.Integer(compute="_compute_accuracy", store=True)
    mean_accuracy_pct = fields.Float(
        string="Mean Accuracy %", compute="_compute_accuracy", store=True, digits=(5, 1)
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "generated_at",
            "generated_by_id",
            "week_start",
            "opening_balance",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"company_id", "scenario", "assumptions"}
        return locked

    @api.depends("line_ids.accuracy_pct", "line_ids.measured")
    def _compute_accuracy(self):
        for version in self:
            done = version.line_ids.filtered("measured")
            version.measured_weeks = len(done)
            version.mean_accuracy_pct = (
                round(sum(done.mapped("accuracy_pct")) / len(done), 1) if done else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Saving a cash forecast version")
        records = super().create(vals_list)
        for version in records:
            version._fix_snapshot()
        return records

    def write(self, vals):
        trusted = self.env.su or self._fix_guard_has_token()
        if self and not trusted and set(vals) - LOCK_EXEMPT:
            raise UserError("A forecast version is kept exactly as it was forecast.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Every forecast version is retained (BRU-TRE-26).")
        return super().unlink()

    def _fix_snapshot(self):
        self.ensure_one()
        from .treasury_reports import cash_forecast

        report = cash_forecast(self.with_company(self.company_id).env, weeks=13, trailing=0)
        rows = report.get("rows") or []
        if not rows:
            raise UserError("The forecast returned no weeks.")
        lines = []
        for horizon, row in enumerate(rows):
            inflow = (row.get("ar_in") or 0.0) + (row.get("other_in") or 0.0)
            outflow = sum(
                row.get(k) or 0.0
                for k in ("ap_out", "payments_out", "payouts_out", "debt_out", "recurring_out")
            )
            lines.append(
                (
                    0,
                    0,
                    {
                        "horizon": horizon,
                        "week_start": row["start"],
                        "inflow": round(inflow, 2),
                        "outflow": round(outflow, 2),
                        "forecast_net": row.get("net") or 0.0,
                        "projected_closing": row.get("closing") or 0.0,
                    },
                )
            )
        opening = rows[0].get("closing", 0.0) - (rows[0].get("net") or 0.0)
        Seq = self.env["ir.sequence"].sudo()
        self.sudo()._guarded().write(
            {
                "name": Seq.next_by_code("fix.cash.forecast.version") or "CFV/%s" % self.id,
                "generated_at": fields.Datetime.now(),
                "generated_by_id": self.env.uid,
                "week_start": rows[0]["start"],
                "opening_balance": round(opening, 2),
                "line_ids": lines,
            }
        )

    def action_measure(self):
        """Fill the actual net movement of every week that has ended."""
        require_role(self.env, GROUP_ACCOUNTANT, "Measuring forecast accuracy")
        for version in self:
            version.line_ids._fix_measure()
        return True

    @api.model
    def _cron_measure(self):
        self.sudo().search([("measured_weeks", "<", 13)]).line_ids._fix_measure()
        return True


class FixCashForecastVersionLine(models.Model):
    _name = "fix.cash.forecast.version.line"
    _description = "Cash Forecast Version Week"
    _order = "version_id, horizon"

    version_id = fields.Many2one(
        "fix.cash.forecast.version", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="version_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="version_id.currency_id")
    horizon = fields.Integer(string="Weeks Ahead")
    week_start = fields.Date(required=True)
    inflow = fields.Monetary(currency_field="currency_id")
    outflow = fields.Monetary(currency_field="currency_id")
    forecast_net = fields.Monetary(currency_field="currency_id", string="Forecast Net")
    projected_closing = fields.Monetary(currency_field="currency_id")
    measured = fields.Boolean(readonly=True)
    actual_net = fields.Monetary(currency_field="currency_id", readonly=True)
    variance = fields.Monetary(currency_field="currency_id", readonly=True)
    accuracy_pct = fields.Float(string="Accuracy %", readonly=True, digits=(5, 1))

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("Forecast weeks come only from the forecast itself.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A forecast week is kept exactly as it was forecast.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Every forecast version is retained (BRU-TRE-26).")
        return super().unlink()

    def _fix_measure(self):
        from .treasury_reports import _liquid_journals

        today = fields.Date.context_today(self)
        for line in self.sudo().filtered(lambda ln: not ln.measured):
            end = line.week_start + timedelta(days=6)
            if end >= today:
                continue
            company = line.company_id
            liquid = _liquid_journals(self.env(su=True), company).mapped("default_account_id")
            groups = (
                self.env["account.move.line"]
                .sudo()
                ._read_group(
                    [
                        ("company_id", "=", company.id),
                        ("account_id", "in", liquid.ids),
                        ("parent_state", "=", "posted"),
                        ("date", ">=", line.week_start),
                        ("date", "<=", end),
                    ],
                    [],
                    ["balance:sum"],
                )
            )
            actual = round((groups[0][0] or 0.0) if groups else 0.0, 2)
            forecast = line.forecast_net
            scale = max(abs(actual), abs(forecast))
            accuracy = (
                100.0 if scale < 0.005 else max(0.0, 100.0 * (1 - abs(actual - forecast) / scale))
            )
            line.write(
                {
                    "measured": True,
                    "actual_net": actual,
                    "variance": round(actual - forecast, 2),
                    "accuracy_pct": round(accuracy, 1),
                }
            )


# --------------------------------------------------------------------------- FX conversions
class FixFxConversion(models.Model):
    """A currency conversion between two of our bank accounts."""

    _name = "fix.fx.conversion"
    _description = "FX Conversion"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "deal_date desc, id desc"

    name = fields.Char(readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    company_currency_id = fields.Many2one(related="company_id.currency_id")
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    deal_date = fields.Date(required=True, default=fields.Date.context_today)
    bank_deal_ref = fields.Char(string="Bank Deal Ticket", required=True)
    from_journal_id = fields.Many2one(
        "account.journal", string="Sold From", required=True, domain=[("type", "=", "bank")]
    )
    to_journal_id = fields.Many2one(
        "account.journal", string="Bought Into", required=True, domain=[("type", "=", "bank")]
    )
    from_currency_id = fields.Many2one(
        "res.currency", compute="_compute_currencies", store=True, string="Currency Sold"
    )
    to_currency_id = fields.Many2one(
        "res.currency", compute="_compute_currencies", store=True, string="Currency Bought"
    )
    amount_from = fields.Monetary(
        string="Amount Sold", currency_field="from_currency_id", required=True
    )
    amount_to = fields.Monetary(
        string="Amount Bought", currency_field="to_currency_id", required=True
    )
    rate_achieved = fields.Float(
        string="Rate Achieved",
        compute="_compute_rate",
        store=True,
        digits=(12, 6),
        help="Company currency per unit of the foreign currency.",
    )
    book_rate = fields.Float(string="Book Rate", readonly=True, digits=(12, 6), copy=False)
    realised_difference = fields.Monetary(
        currency_field="company_currency_id",
        readonly=True,
        copy=False,
        help="Positive: gain against the book rate. Negative: loss.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    prepared_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "book_rate",
            "realised_difference",
            "prepared_by_id",
            "approved_by_id",
            "move_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(c.state != "draft" for c in self):
            locked |= {
                "company_id",
                "operating_unit_id",
                "deal_date",
                "bank_deal_ref",
                "from_journal_id",
                "to_journal_id",
                "amount_from",
                "amount_to",
            }
        return locked

    @api.depends("from_journal_id", "to_journal_id", "company_id")
    def _compute_currencies(self):
        for c in self:
            base = c.company_id.currency_id
            c.from_currency_id = c.from_journal_id.currency_id or base
            c.to_currency_id = c.to_journal_id.currency_id or base

    @api.depends("amount_from", "amount_to", "from_currency_id", "to_currency_id")
    def _compute_rate(self):
        for c in self:
            base = c.company_id.currency_id
            if c.from_currency_id == base and c.amount_to:
                c.rate_achieved = c.amount_from / c.amount_to
            elif c.to_currency_id == base and c.amount_from:
                c.rate_achieved = c.amount_to / c.amount_from
            else:
                c.rate_achieved = 0.0

    @api.constrains("from_journal_id", "to_journal_id", "amount_from", "amount_to", "deal_date")
    def _check_conversion(self):
        for c in self:
            if c.from_journal_id == c.to_journal_id:
                raise ValidationError("A conversion moves money between two different accounts.")
            if c.from_journal_id.company_id != c.to_journal_id.company_id or (
                c.from_journal_id.company_id != c.company_id
            ):
                raise ValidationError("Both accounts belong to the same legal entity (BRU-TRE-16).")
            if c.amount_from <= 0 or c.amount_to <= 0:
                raise ValidationError("Both amounts are positive.")
            base = c.company_id.currency_id
            if c.from_currency_id == c.to_currency_id:
                raise ValidationError(
                    "Both accounts are in %s: that is a transfer, not a conversion."
                    % c.from_currency_id.name
                )
            if base not in (c.from_currency_id | c.to_currency_id):
                raise ValidationError(
                    "One side of the conversion is in %s; a cross-currency deal is booked as two."
                    % base.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_role(self.env, GROUP_ACCOUNTANT, "Recording an FX conversion")
        records = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for c in records:
            c._guarded().write({"name": Seq.next_by_code("fix.fx.conversion") or "FXC/%s" % c.id})
        return records

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted FX conversion")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(c.state != "draft" for c in self):
            raise UserError("A submitted conversion is kept; cancel it instead.")
        return super().unlink()

    def _foreign(self):
        self.ensure_one()
        base = self.company_id.currency_id
        if self.from_currency_id != base:
            return self.from_currency_id, self.amount_from
        return self.to_currency_id, self.amount_to

    def _book_value(self):
        """(book rate, company-currency value of the foreign leg at the book rate)."""
        foreign, amount = self._foreign()
        base = self.company_id.currency_id
        value = foreign._convert(amount, base, self.company_id, self.deal_date, round=False)
        rate = value / amount if amount else 0.0
        return rate, round(value, 2)

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting an FX conversion")
        for c in self:
            if c.state != "draft":
                raise UserError("Only a draft conversion is submitted.")
            c._guarded().write({"state": "submitted", "prepared_by_id": self.env.uid})
        return True

    def action_approve(self):
        """Post: the foreign leg at the book rate, the company-currency leg
        at what was actually paid or received, the difference to FX gain or
        loss. Approved by an Accounting Administrator other than the preparer."""
        require_role(self.env, GROUP_ADMIN, "Approving an FX conversion")
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

        from .treasury_common import posting_dims

        for c in self:
            if c.state != "submitted":
                raise UserError("Only a submitted conversion is approved.")
            require_other_person(self.env, c.prepared_by_id | c.create_uid, "Approving %s" % c.name)
            base = c.company_id.currency_id
            rate, book = c._book_value()
            from_acc = bank_account_of(c.from_journal_id)
            to_acc = bank_account_of(c.to_journal_id)
            label = "FX %s %s" % (c.name, c.bank_deal_ref)
            if c.from_currency_id == base:
                # bought foreign currency with company currency
                diff = round(book - c.amount_from, 2)
                lines = [
                    {
                        "account_id": to_acc.id,
                        "name": label,
                        "debit": book,
                        "credit": 0.0,
                        "currency_id": c.to_currency_id.id,
                        "amount_currency": c.amount_to,
                    },
                    {
                        "account_id": from_acc.id,
                        "name": label,
                        "debit": 0.0,
                        "credit": c.amount_from,
                    },
                ]
            else:
                # sold foreign currency for company currency
                diff = round(c.amount_to - book, 2)
                lines = [
                    {"account_id": to_acc.id, "name": label, "debit": c.amount_to, "credit": 0.0},
                    {
                        "account_id": from_acc.id,
                        "name": label,
                        "debit": 0.0,
                        "credit": book,
                        "currency_id": c.from_currency_id.id,
                        "amount_currency": -c.amount_from,
                    },
                ]
            if abs(diff) >= 0.005:
                gain = diff > 0
                account = (
                    c.company_id.income_currency_exchange_account_id
                    if gain
                    else c.company_id.expense_currency_exchange_account_id
                )
                if not account:
                    raise UserError(
                        "%s has no exchange %s account configured in Accounting settings."
                        % (c.company_id.name, "gain" if gain else "loss")
                    )
                lines.append(
                    {
                        "account_id": account.id,
                        "name": "%s realised FX %s" % (label, "gain" if gain else "loss"),
                        "debit": 0.0 if gain else -diff,
                        "credit": diff if gain else 0.0,
                    }
                )
            journal = (
                self.env["account.journal"]
                .sudo()
                .search([("type", "=", "general"), ("company_id", "=", c.company_id.id)], limit=1)
            )
            if not journal:
                raise UserError("%s has no general journal." % c.company_id.name)
            move_vals = {
                "journal_id": journal.id,
                "company_id": c.company_id.id,
                "date": c.deal_date,
                "ref": label,
                "line_ids": [(0, 0, ln) for ln in lines],
            }
            dims = posting_dims(self.env)
            move, _dims = post_with_dimensions(
                self.env(su=True),
                move_vals,
                {i: dict(dims) for i in range(len(lines))},
                source="treasury",
            )
            c._guarded().write(
                {
                    "state": "posted",
                    "approved_by_id": self.env.uid,
                    "book_rate": rate,
                    "realised_difference": diff,
                    "move_id": move.id,
                }
            )
        return True

    def action_cancel(self, reason=None):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling an FX conversion")
        for c in self:
            if c.state not in ("draft", "submitted"):
                raise UserError("A posted conversion is reversed in the GL, not cancelled here.")
            c._guarded().write({"state": "cancelled"})
            if reason:
                c.message_post(body="Cancelled: %s" % reason)
        return True
