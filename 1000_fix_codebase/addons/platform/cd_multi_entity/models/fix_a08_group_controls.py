# cd_multi_entity — A08 group controls (M19-10, M19-12, M19-13), prepared by
# builder B3 for the lead (cd_multi_entity is lead-owned; cd_gl_ext cannot
# extend these models because cd_multi_entity depends on cd_gl_ext).
#
# Apply: copy to addons/platform/cd_multi_entity/models/ and add
# `fix_a08_group_controls` LAST to models/__init__.py.
#
#   IC transaction  state, entries, due lines and match stamps are guarded; the
#                   terms (amount, currency, rule, entities, date) are pinned
#                   once mirrored; the user who posted the mirror never matches
#                   it (I02, I03, C05).
#   Consolidation   run_by_id/closed_by_id/state guarded (C03); eliminations are
#                   created only by action_generate_eliminations, each from a
#                   matched/settled IC transaction (C04); a closed book's lines
#                   and eliminations are frozen (C06).
#   Nil return      state and counts guarded (N03); the period is recounted at
#                   generate and at submit, and the filing is recorded only once
#                   the period is locked (company lock date covers it) (N02).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixIntercompanyTransaction(models.Model):
    _name = "fix.intercompany.transaction"
    _inherit = ["fix.intercompany.transaction", "fix.guarded.mixin"]

    mirrored_by_id = fields.Many2one("res.users", string="Mirror Posted By", readonly=True, copy=False)
    matched_by_id = fields.Many2one("res.users", string="Matched By", readonly=True, copy=False)

    _PINNED = ("amount", "currency_id", "rule_id", "source_entity_id", "target_entity_id", "transaction_date")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "source_move_id",
            "target_move_id",
            "source_due_line_id",
            "target_due_line_id",
            "matched_date",
            "match_difference",
            "mirror_invoice_ref",
            "mirrored_by_id",
            "matched_by_id",
        }

    def write(self, vals):
        pinned = set(self._PINNED) & set(vals)
        if pinned and not self._fix_guard_open() and any(r.state != "draft" for r in self):
            raise UserError(
                "The terms of a mirrored inter-company transaction (%s) are pinned to its "
                "posted entries; reverse it and raise a new one." % ", ".join(sorted(pinned))
            )
        return super().write(vals)

    def action_generate_mirror(self):
        result = super(FixIntercompanyTransaction, self._guarded()).action_generate_mirror()
        self._guarded().write({"mirrored_by_id": self.env.uid})
        return result

    def action_match(self):
        """The counterparty acceptance: the match is decided by someone other
        than the user who posted both sides (I02)."""
        self.ensure_one()
        if not self.env.su and self.mirrored_by_id and self.mirrored_by_id == self.env.user:
            raise UserError(
                "Segregation of duties: %s posted both sides of %s and cannot also match "
                "them; the counterparty entity's accountant matches." % (self.env.user.name, self.reference)
            )
        result = super(FixIntercompanyTransaction, self._guarded()).action_match()
        if self.state == "matched":
            self._guarded().write({"matched_by_id": self.env.uid})
        return result

    def action_mark_settled(self):
        return super(FixIntercompanyTransaction, self._guarded()).action_mark_settled()


_ELIM_TOKEN = object()
_ELIM_KEY = "fix_a08_elimination_run"


class FixConsolidationBook(models.Model):
    _name = "fix.consolidation.book"
    _inherit = ["fix.consolidation.book", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "run_by_id", "run_at", "closed_by_id"}

    def write(self, vals):
        if not self._fix_guard_open() and any(b.state == "closed" for b in self):
            frozen = set(vals) - {"message_main_attachment_id"}
            if frozen:
                raise UserError("A closed consolidation book is frozen.")
        return super().write(vals)

    def action_run_consolidation(self):
        return super(
            FixConsolidationBook, self._guarded().with_context(**{_ELIM_KEY: _ELIM_TOKEN})
        ).action_run_consolidation()

    def action_generate_eliminations(self):
        return super(
            FixConsolidationBook, self._guarded().with_context(**{_ELIM_KEY: _ELIM_TOKEN})
        ).action_generate_eliminations()

    def action_close(self):
        return super(FixConsolidationBook, self._guarded()).action_close()


class FixConsolidationLine(models.Model):
    _inherit = "fix.consolidation.line"

    def _fix_book_open(self, books):
        if self.env.su or self.env.context.get(_ELIM_KEY) is _ELIM_TOKEN:
            return
        if any(b.state == "closed" for b in books):
            raise UserError("A closed consolidation book's lines are frozen.")
        raise UserError("Consolidation lines are produced by Run Consolidation, never typed.")

    @api.model_create_multi
    def create(self, vals_list):
        books = self.env["fix.consolidation.book"].browse([v.get("book_id") for v in vals_list])
        self._fix_book_open(books)
        return super().create(vals_list)

    def write(self, vals):
        self._fix_book_open(self.mapped("book_id"))
        return super().write(vals)

    def unlink(self):
        self._fix_book_open(self.mapped("book_id"))
        return super().unlink()


class FixEliminationEntry(models.Model):
    _inherit = "fix.elimination.entry"

    def _fix_generated_only(self, books):
        if self.env.su or self.env.context.get(_ELIM_KEY) is _ELIM_TOKEN:
            return
        if any(b.state == "closed" for b in books):
            raise UserError("A closed consolidation book's eliminations are frozen.")
        raise UserError(
            "Eliminations come only from matched inter-company transactions (Generate "
            "Eliminations); a typed elimination is refused."
        )

    @api.model_create_multi
    def create(self, vals_list):
        books = self.env["fix.consolidation.book"].browse([v.get("book_id") for v in vals_list])
        self._fix_generated_only(books)
        for vals in vals_list:
            if not vals.get("transaction_id"):
                raise ValidationError("An elimination names the inter-company transaction it removes.")
        return super().create(vals_list)

    def write(self, vals):
        self._fix_generated_only(self.mapped("book_id"))
        return super().write(vals)

    def unlink(self):
        self._fix_generated_only(self.mapped("book_id"))
        return super().unlink()


class FixNilReturnGenerator(models.Model):
    _name = "fix.nil.return.generator"
    _inherit = ["fix.nil.return.generator", "fix.guarded.mixin"]

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "transaction_count",
            "transactions_counted_at",
            "mushak_9_1_nil_payload",
            "tds_nil_payload",
        }

    def _fix_recount(self, what):
        count = self._count_period_transactions()
        if count:
            raise ValidationError(
                "%s refused: entity %s now has %d posted transaction(s) in %s-%02d; a standard "
                "Mushak 9.1 return is due, not a nil return."
                % (what, self.entity_id.code, count, self.period_year, self.period_month)
            )
        self._guarded().write({"transaction_count": 0, "transactions_counted_at": fields.Datetime.now()})

    def action_verify_eligibility(self):
        return super(FixNilReturnGenerator, self._guarded()).action_verify_eligibility()

    def action_generate_nil_packs(self):
        self.ensure_one()
        self._fix_recount("Generating the nil packs")
        return super(FixNilReturnGenerator, self._guarded()).action_generate_nil_packs()

    def action_submit_to_nbr(self):
        self.ensure_one()
        if not (
            self.state == "generated"
            and self.mushak_9_1_nil_payload
            and (self.filing_reference or "").strip()
        ):
            # the original preconditions and their messages come first
            return super(FixNilReturnGenerator, self._guarded()).action_submit_to_nbr()
        _start, end = self._period_bounds()
        lock = self.entity_id.company_id.sudo().fiscalyear_lock_date
        if not lock or lock < end:
            raise UserError(
                "Close and lock %s-%02d (M19 period close) before recording its nil return: "
                "an open period can still receive postings." % (self.period_year, self.period_month)
            )
        self._fix_recount("Recording the NBR filing")
        return super(FixNilReturnGenerator, self._guarded()).action_submit_to_nbr()


# ============================================================ transfer pricing
class FixTransferPriceRate(models.Model):
    """The approved transfer-pricing rate register (BRU-FPA-18, A08 M19-13/I05).

    An inter-company transaction is priced only at an APPROVED rate: an
    accountant proposes the markup of a rule for an effective period (with the
    transfer-pricing study it rests on); an Accounting Administrator other than
    the proposer activates it. Default: no rate approved, so a priced
    transaction (its rule carries a markup) is refused until one is. The rate
    value is the business's to enter; the control is code."""

    _name = "fix.transfer.price.rate"
    _description = "Approved Transfer-Pricing Rate"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "rule_id, date_from desc"

    rule_id = fields.Many2one("fix.intercompany.rule", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="rule_id.company_id", store=True)
    markup_percent = fields.Float(string="Approved Markup (%)", required=True, digits=(16, 4))
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    study_ref = fields.Char(string="Transfer-Pricing Study / Basis", required=True)
    state = fields.Selection(
        [("draft", "Proposed"), ("active", "Approved & Active"), ("retired", "Retired")],
        default="draft",
        required=True,
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    _TERMS = ("rule_id", "markup_percent", "date_from", "date_to", "study_ref")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id", "approved_at"}

    @api.constrains("date_from", "date_to", "markup_percent")
    def _check_terms(self):
        for rate in self:
            if rate.date_to and rate.date_to < rate.date_from:
                raise ValidationError("A transfer-pricing rate ends after it starts.")
            if rate.markup_percent < 0:
                raise ValidationError("A transfer-pricing markup is not negative.")

    def write(self, vals):
        if set(self._TERMS) & set(vals) and not self._fix_guard_open():
            if any(r.state != "draft" for r in self):
                raise UserError(
                    "An approved transfer-pricing rate is frozen; retire it and propose a new one."
                )
        return super().write(vals)

    def action_activate(self):
        for rate in self:
            if rate.state != "draft":
                raise UserError("Only a proposed rate is approved.")
            if not self.env.su:
                if not self.env.user.has_group("account.group_account_manager"):
                    raise UserError(
                        "A transfer-pricing rate is approved by an Accounting Administrator."
                    )
                if self.env.user == rate.create_uid:
                    raise UserError(
                        "Segregation of duties: %s proposed this rate and cannot approve it."
                        % self.env.user.name
                    )
            overlap = self.sudo().search(
                [
                    ("id", "!=", rate.id),
                    ("rule_id", "=", rate.rule_id.id),
                    ("state", "=", "active"),
                    ("date_from", "<=", rate.date_to or fields.Date.to_date("9999-12-31")),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", rate.date_from),
                ],
                limit=1,
            )
            if overlap:
                raise UserError(
                    "Rule %s already has an approved rate over that period (from %s); retire it "
                    "first." % (rate.rule_id.code, overlap.date_from)
                )
            rate._guarded().write(
                {
                    "state": "active",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_retire(self):
        if not self.env.su and not self.env.user.has_group("account.group_account_manager"):
            raise UserError("A transfer-pricing rate is retired by an Accounting Administrator.")
        self.filtered(lambda r: r.state == "active")._guarded().write({"state": "retired"})
        return True

    @api.model
    def _approved_for(self, rule, day):
        return self.sudo().search(
            [
                ("rule_id", "=", rule.id),
                ("state", "=", "active"),
                ("date_from", "<=", day),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", day),
            ],
            order="date_from desc",
            limit=1,
        )


class FixIntercompanyRule(models.Model):
    _inherit = "fix.intercompany.rule"

    tp_rate_ids = fields.One2many(
        "fix.transfer.price.rate", "rule_id", string="Transfer-Pricing Rates"
    )
    transfer_pricing_compliant = fields.Boolean(
        string="Approved Transfer-Pricing Rate in Force",
        compute="_compute_tp_compliant",
        help="True when an approved rate covers today: read from the rate register, never ticked.",
    )

    @api.depends("tp_rate_ids.state", "tp_rate_ids.date_from", "tp_rate_ids.date_to")
    def _compute_tp_compliant(self):
        Rate = self.env["fix.transfer.price.rate"]
        today = fields.Date.context_today(self)
        for rule in self:
            rule.transfer_pricing_compliant = bool(rule.id and Rate._approved_for(rule, today))


class FixIntercompanyTransactionPricing(models.Model):
    _inherit = "fix.intercompany.transaction"

    cost_amount = fields.Monetary(
        string="Cost Before Markup",
        readonly=True,
        copy=False,
        help="The amount entered, before the approved markup was applied at posting.",
    )
    tp_rate_id = fields.Many2one(
        "fix.transfer.price.rate", string="Approved TP Rate Applied", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"cost_amount", "tp_rate_id"}

    def _fix_apply_transfer_price(self):
        """Price the charge at the approved rate in force on its date."""
        self.ensure_one()
        rule = self.rule_id
        if self.scope != "intercompany" or not rule:
            return
        rate = self.env["fix.transfer.price.rate"]._approved_for(rule, self.transaction_date)
        if rule.markup_percent and not rate:
            raise UserError(
                "Rule %s prices this charge at a %.2f%% markup, but no transfer-pricing rate is "
                "approved for %s. An Accounting Administrator other than the proposer approves "
                "the rate first (BRU-FPA-18)."
                % (rule.code, rule.markup_percent, self.transaction_date)
            )
        if not rate:
            return  # a cost recharge, no markup
        if abs(rate.markup_percent - (rule.markup_percent or 0.0)) > 1e-6:
            raise UserError(
                "Rule %s states a %.2f%% markup but the approved rate is %.2f%%; the charge is "
                "priced only at the approved rate."
                % (rule.code, rule.markup_percent, rate.markup_percent)
            )
        cost = self.amount
        priced = self.currency_id.round(cost * (1 + rate.markup_percent / 100.0))
        self._guarded().write({"cost_amount": cost, "amount": priced, "tp_rate_id": rate.id})

    def action_generate_mirror(self):
        if len(self) == 1 and self.state == "draft" and not self.source_move_id:
            self._fix_apply_transfer_price()
        return super().action_generate_mirror()
