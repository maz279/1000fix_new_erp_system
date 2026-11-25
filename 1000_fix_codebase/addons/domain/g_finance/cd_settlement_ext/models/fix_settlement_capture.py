# cd_settlement_ext: M53 sub-module capture audit (2026-11-17).
#
# Two spec records that the M53 workspace had no way to capture:
#
#   * fix.revenue.presentation (FR-REV-007 P0, BRU-REV-08/09 H, AUT-REV-22):
#     the declared principal-or-agent position per arrangement, with the
#     D-03 decision and the external opinion behind it, approved by an
#     Accounting Administrator who did not request it and then frozen; a
#     change is a new declaration that supersedes the old one from its date.
#     Page 5 "Principal vs Agent" captured nothing, while the posting engine
#     booked every marketplace sale as an agent (net) with no declaration at
#     all. A marketplace commission now accrues to the GL only under a
#     declared AGENT position in force on its date; with no declaration, or
#     a principal one (the gross presentation is not built), it is refused.
#   * fix.payout.hold (FR-REV-035 P0, BRU-REV-16 H; FR-REV-039 P0,
#     BRU-REV-17 H): a hold on a payee's payout for a reason from the
#     controlled list (settlement dispute, quality investigation, KYC, tax
#     status, other), with a named raiser, released only by an Accounting
#     Administrator other than the raiser, with a reason (and, for a dispute,
#     its coded outcome). A dispute names the disputed commission lines and
#     holds only them; other reasons hold the named lines or, with none
#     named, the whole payee. The only hold before was M12's automatic flag
#     for an open marketplace dispute or chargeback: nobody could hold a
#     payout for quality, KYC or tax, nor hold just the disputed lines.
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
    GROUP_ACCOUNTANT,
    GROUP_ADMINISTRATOR,
    require_role,
)
from odoo.addons.cd_cash_position.models.treasury_common import require_other_person
from odoo.exceptions import UserError, ValidationError

LOCK_EXEMPT = {"message_main_attachment_id"}


def _locked_write(records, vals, open_states, what):
    trusted = records.env.su or records._fix_guard_has_token()
    if trusted or not set(vals) - LOCK_EXEMPT:
        return
    if any(rec.state not in open_states for rec in records):
        raise UserError("%s is a record of what was decided and cannot be edited." % what)


# --------------------------------------------------------------------------- presentation
ARRANGEMENTS = [
    ("marketplace", "Marketplace third-party sales"),
    ("courier", "Courier revenue share"),
    ("brand", "Brand partner revenue share"),
]
POSITIONS = [
    ("agent", "Agent: commission only, net (seller share is a liability)"),
    ("principal", "Principal: gross revenue, seller share is a cost"),
]


class FixRevenuePresentation(models.Model):
    """The declared principal-or-agent position of one arrangement (D-03)."""

    _name = "fix.revenue.presentation"
    _description = "Principal / Agent Position (IFRS 15, D-03)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "arrangement, effective_from desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    arrangement = fields.Selection(ARRANGEMENTS, required=True, default="marketplace", index=True)
    position = fields.Selection(POSITIONS, required=True, default="agent")
    decision_ref = fields.Char(
        string="D-03 Decision Record",
        required=True,
        help="The CEO / CFO / Legal decision that settles the commercial model (D-03).",
    )
    opinion_ref = fields.Char(
        string="External Opinion",
        required=True,
        help="The external accounting / tax opinion the position rests on (BRU-REV-09).",
    )
    effective_from = fields.Date(required=True, default=fields.Date.context_today)
    effective_to = fields.Date(readonly=True, copy=False)
    note = fields.Text(string="Basis (control indicators)")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("active", "In Force"),
            ("superseded", "Superseded"),
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
    reject_reason = fields.Char(readonly=True, copy=False)

    STAMPS = {
        "state",
        "requested_by_id",
        "requested_at",
        "approved_by_id",
        "approved_at",
        "reject_reason",
        "effective_to",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(p.state != "draft" for p in self):
            locked |= {
                "company_id",
                "arrangement",
                "position",
                "decision_ref",
                "opinion_ref",
                "effective_from",
                "note",
            }
        return locked

    @api.depends("arrangement", "position", "effective_from")
    def _compute_name(self):
        arr, pos = dict(ARRANGEMENTS), {"agent": "Agent", "principal": "Principal"}
        for p in self:
            p.name = "%s: %s from %s" % (
                arr.get(p.arrangement, "?"),
                pos.get(p.position, "?"),
                p.effective_from or "?",
            )

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A submitted principal / agent position")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(p.state != "draft" for p in self):
            raise UserError("A submitted position is kept as history; a new one supersedes it.")
        return super().unlink()

    def action_submit(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Submitting a principal / agent position")
        for p in self:
            if p.state != "draft":
                raise UserError("Only a draft position is submitted.")
            p._guarded().write(
                {
                    "state": "submitted",
                    "requested_by_id": self.env.uid,
                    "requested_at": fields.Datetime.now(),
                }
            )
        return True

    def action_approve(self):
        """BRU-REV-09: declared once, with its basis, by an Accounting
        Administrator who did not request it (the CFO tier until a CFO group
        exists); the position in force before it ends the day before."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Approving a principal / agent position")
        now = fields.Datetime.now()
        for p in self:
            if p.state != "submitted":
                raise UserError("Only a submitted position is approved.")
            require_other_person(
                self.env, p.requested_by_id | p.create_uid, "Approving position %s" % p.name
            )
            for old in self.sudo().search(
                [
                    ("id", "!=", p.id),
                    ("company_id", "=", p.company_id.id),
                    ("arrangement", "=", p.arrangement),
                    ("state", "=", "active"),
                ]
            ):
                if old.effective_from >= p.effective_from:
                    raise UserError(
                        "%s is in force from %s: a new position takes effect after it."
                        % (old.name, old.effective_from)
                    )
                old._guarded().write(
                    {
                        "state": "superseded",
                        "effective_to": p.effective_from - timedelta(days=1),
                    }
                )
            p._guarded().write(
                {"state": "active", "approved_by_id": self.env.uid, "approved_at": now}
            )
        return True

    def action_reject(self, reason=""):
        require_role(self.env, GROUP_ADMINISTRATOR, "Rejecting a principal / agent position")
        if not (reason or "").strip():
            raise UserError("State why the position is rejected.")
        for p in self:
            if p.state != "submitted":
                raise UserError("Only a submitted position is rejected.")
            require_other_person(self.env, p.requested_by_id, "Rejecting position %s" % p.name)
            p._guarded().write({"state": "rejected", "reject_reason": reason.strip()[:250]})
        return True

    @api.model
    def _in_force(self, company, arrangement, on_date):
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("arrangement", "=", arrangement),
                ("state", "in", ("active", "superseded")),
                ("effective_from", "<=", on_date),
                "|",
                ("effective_to", "=", False),
                ("effective_to", ">=", on_date),
            ],
            order="effective_from desc",
            limit=1,
        )


class FixCommissionLedgerPresentation(models.Model):
    _inherit = "fix.commission.ledger"

    def _fix_assert_presentation(self):
        """BRU-REV-09 / AUT-REV-22: marketplace revenue is accounted for only
        under the declared position in force on the commission's date."""
        Position = self.env["fix.revenue.presentation"]
        for rec in self.filtered(lambda r: r.source_type == "marketplace" and r.state == "earned"):
            on = fields.Date.to_date(rec.create_date) or fields.Date.context_today(rec)
            position = Position._in_force(rec.company_id, "marketplace", on)
            if not position:
                raise UserError(
                    "Commission %s is marketplace revenue and %s has no principal / agent "
                    "position in force on %s: it is not accounted for until D-03 is declared "
                    "on the Principal vs Agent page (BRU-REV-09)."
                    % (rec.name, rec.company_id.name, on)
                )
            if position.position != "agent":
                raise UserError(
                    "%s declares the marketplace PRINCIPAL; this ledger books the agent (net) "
                    "presentation only (FF-91). The gross presentation and M51's VAT base "
                    "must be built before commission %s can accrue." % (position.name, rec.name)
                )

    def action_post_to_gl(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Accruing a commission")
        rows = self.filtered(lambda r: r.source_type == "marketplace" and r.state == "earned")
        # the row's own refusals first (no order, no rate, no scheme), as before
        rows._fix_assert_source()
        rows._fix_ensure_scheme()
        rows._fix_assert_presentation()
        return super().action_post_to_gl()


# --------------------------------------------------------------------------- payout hold
HOLD_REASONS = [
    ("settlement_dispute", "Settlement dispute (payee disputes lines)"),
    ("quality", "Quality investigation"),
    ("kyc", "KYC / onboarding incomplete"),
    ("tax", "Tax status"),
    ("other", "Other (stated)"),
]
OUTCOMES = [
    ("upheld", "Dispute upheld (adjusted)"),
    ("partly_upheld", "Dispute partly upheld"),
    ("rejected", "Dispute rejected"),
    ("resolved", "Cause resolved"),
]


class FixPayoutHold(models.Model):
    """A hold on a payee's payout: lines or the whole payee (FR-REV-035)."""

    _name = "fix.payout.hold"
    _description = "Payout Hold / Settlement Dispute"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, raised_at desc, id desc"

    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    partner_id = fields.Many2one("res.partner", string="Payee", required=True, index=True)
    reason = fields.Selection(HOLD_REASONS, required=True, default="quality")
    commission_ids = fields.Many2many(
        "fix.commission.ledger",
        "fix_payout_hold_commission_rel",
        "hold_id",
        "commission_id",
        string="Lines Held (empty = the whole payee)",
    )
    statement_id = fields.Many2one("fix.seller.statement", string="Disputed Statement", index=True)
    note = fields.Text(string="Details", required=True)
    scope = fields.Selection(
        [("lines", "Named lines only"), ("payee", "Whole payee")],
        compute="_compute_scope",
        store=True,
    )
    held_amount = fields.Monetary(
        string="Amount Held (net)",
        currency_field="currency_id",
        compute="_compute_held",
        help="The net payable of the lines held, or of every unpaid accrued line of the payee.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Holding"), ("released", "Released")],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    raised_by_id = fields.Many2one("res.users", string="Raised By", readonly=True, copy=False)
    raised_at = fields.Datetime(readonly=True, copy=False)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)
    release_reason = fields.Char(readonly=True, copy=False)
    outcome = fields.Selection(OUTCOMES, readonly=True, copy=False)
    adjustment_id = fields.Many2one(
        "fix.settlement.adjustment",
        string="Adjustment Raised",
        readonly=True,
        copy=False,
        help="The clawback / adjustment that carried an upheld dispute.",
    )

    STAMPS = {
        "name",
        "state",
        "raised_by_id",
        "raised_at",
        "released_by_id",
        "released_at",
        "release_reason",
        "outcome",
        "adjustment_id",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(h.state != "draft" for h in self):
            locked |= {
                "company_id",
                "partner_id",
                "reason",
                "commission_ids",
                "statement_id",
                "note",
            }
        return locked

    @api.depends("commission_ids")
    def _compute_scope(self):
        for h in self:
            h.scope = "lines" if h.commission_ids else "payee"

    @api.depends("commission_ids.net_payable", "partner_id", "state")
    def _compute_held(self):
        Ledger = self.env["fix.commission.ledger"].sudo()
        for h in self:
            rows = h.commission_ids
            if not rows and h.partner_id:
                rows = Ledger.search(
                    [
                        ("company_id", "=", h.company_id.id),
                        ("seller_partner_id", "child_of", h.partner_id.commercial_partner_id.id),
                        ("state", "in", ("earned", "accrued")),
                    ]
                )
            h.held_amount = round(sum(rows.mapped("net_payable")), 2)

    @api.constrains("reason", "commission_ids", "partner_id", "statement_id", "company_id")
    def _check_hold(self):
        for h in self:
            if h.reason == "settlement_dispute" and not h.commission_ids:
                raise ValidationError(
                    "A settlement dispute names the disputed lines: only they are held "
                    "(BRU-REV-17)."
                )
            payee = h.partner_id.commercial_partner_id
            foreign = h.commission_ids.filtered(
                lambda c, p=payee, co=h.company_id: c.seller_partner_id.commercial_partner_id != p
                or c.company_id != co
            )
            if foreign:
                raise ValidationError(
                    "Lines %s are not this payee's in this company."
                    % ", ".join(foreign.mapped("name"))
                )
            if h.statement_id and h.statement_id.seller_partner_id.commercial_partner_id != payee:
                raise ValidationError("The disputed statement is another payee's.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        Seq = self.env["ir.sequence"].sudo()
        for rec in records.filtered(lambda r: r.name == "New"):
            rec._guarded().write({"name": Seq.next_by_code("fix.payout.hold") or "PHD/%s" % rec.id})
        return records

    def write(self, vals):
        _locked_write(self, vals, ("draft",), "A raised payout hold")
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(h.state != "draft" for h in self):
            raise UserError("A raised hold is kept as history: release it instead.")
        return super().unlink()

    def action_raise(self):
        """The hold takes effect at once, with its raiser named (BRU-REV-16)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Raising a payout hold")
        Run = self.env["fix.payout.run"].sudo()
        for h in self:
            if h.state != "draft":
                raise UserError("Only a draft hold is raised.")
            paid = h.commission_ids.filtered(lambda c: c.state == "paid")
            if paid:
                raise UserError("Lines %s are already paid." % ", ".join(paid.mapped("name")))
            payee_rows = h.commission_ids or self.env["fix.commission.ledger"].sudo().search(
                [
                    ("company_id", "=", h.company_id.id),
                    ("seller_partner_id", "child_of", h.partner_id.commercial_partner_id.id),
                ]
            )
            approved = Run.search(
                [
                    ("state", "in", ("approved", "executing", "file_generated")),
                    ("commission_ids", "in", payee_rows.ids or [0]),
                ],
                limit=1,
            )
            if approved:
                raise UserError(
                    "Payout run %s is already approved for these lines: cancel the run or drop "
                    "the payee from it; a hold acts before approval." % approved.name
                )
            h._guarded().write(
                {
                    "state": "active",
                    "raised_by_id": self.env.uid,
                    "raised_at": fields.Datetime.now(),
                }
            )
            h.message_post(body="Payout hold raised by %s: %s" % (self.env.user.name, h.note))
        return True

    def action_release(self, reason="", outcome=None):
        """Released by an Accounting Administrator who did not raise it, with
        a reason; a dispute also records its coded outcome."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Releasing a payout hold")
        if not (reason or "").strip():
            raise UserError("State why the hold is released.")
        for h in self:
            if h.state != "active":
                raise UserError("Only an active hold is released.")
            require_other_person(self.env, h.raised_by_id, "Releasing hold %s" % h.name)
            code = outcome or ("resolved" if h.reason != "settlement_dispute" else None)
            if h.reason == "settlement_dispute" and code not in (
                "upheld",
                "partly_upheld",
                "rejected",
            ):
                raise UserError(
                    "A settlement dispute is released with its outcome: upheld, partly_upheld "
                    "or rejected."
                )
            if code not in dict(OUTCOMES):
                raise UserError("Unknown outcome %s." % code)
            h._guarded().write(
                {
                    "state": "released",
                    "released_by_id": self.env.uid,
                    "released_at": fields.Datetime.now(),
                    "release_reason": reason.strip()[:250],
                    "outcome": code,
                }
            )
        return True

    @api.model
    def _active_for(self, company, partners):
        if not partners:
            return self.browse()
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "active"),
                ("partner_id", "child_of", partners.commercial_partner_id.ids),
            ]
        )


class FixPayoutRunHold(models.Model):
    _inherit = "fix.payout.run"

    def _fix_held_payees(self, partners):
        """M12's automatic dispute flag, plus every whole-payee payout hold."""
        held = super()._fix_held_payees(partners)
        company = self[:1].company_id or self.env.company
        holds = self.env["fix.payout.hold"]._active_for(company, partners)
        return held | holds.filtered(lambda h: h.scope == "payee").mapped(
            "partner_id.commercial_partner_id"
        )

    def _fix_held_lines(self):
        self.ensure_one()
        holds = self.env["fix.payout.hold"]._active_for(
            self.company_id, self.commission_ids.mapped("seller_partner_id")
        )
        return holds.filtered(lambda h: h.scope == "lines").mapped("commission_ids")

    def action_collect_accrued(self):
        result = super().action_collect_accrued()
        for run in self:
            held = run._fix_held_lines() & run.commission_ids
            if held:
                # BRU-REV-17: only the held lines wait; the rest of the payee is paid
                run.commission_ids = [(3, c.id) for c in held]
        return result

    def _fix_check_rows(self):
        super()._fix_check_rows()
        held = self._fix_held_lines() & self.commission_ids
        if held:
            raise UserError(
                "Payout run %s pays %s, on a payout hold (FR-REV-035): remove them or release "
                "the hold first." % (self.name, ", ".join(held.mapped("name")))
            )
