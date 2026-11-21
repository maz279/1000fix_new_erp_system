# M36 tenders and their bonds (spec §5.5, FR-QTE-043..048).
#
# A04 workflow audit (2026-11-03, M36-7/8/9/10) and the C2-C13 build
# (2026-11-04): a clerk wrote state='won' on a draft tender, submitted at 0%
# compliance with no bid security, won on a bond typed as active with amount
# 0 or on an expired one, and nothing happened downstream. Any clerk released
# the bid security before the award, claimed a draft bond, flipped an encashed
# bond back to released and edited an active bond's amount. Now:
#
#   tender: draft --bid/no-bid decision (Tender Committee, scored, not the
#           preparer)--> [no_bid] | bid --submit (compliance matrix complete,
#           valid bid security when required)--> submitted
#           --request award (award letter + awarded value)--> [M63: a Tender
#           Committee member who neither prepared nor submitted the bid]
#           --> won --> M08 draft contract (+ draft performance security)
#           submitted --record loss (reason)--> lost; pre-decision --> cancelled
#   bond:   draft --activate (bank, guarantee no., expiry, amount in the PPR
#           band)--> active --release (after the award, with the bank's
#           discharge ref) / claim (reason): routed DOFA decision on the
#           amount--> released | claimed (terminal); active --(cron, expiry
#           passed)--> expired. Amount, bank and type are frozen once active.
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_quotation import dhaka_today
from .fix_quote_ops import CONTRACT_FAMILIES

TENDER_COMMITTEE = "cd_quotation.group_tender_committee"

# PPR 2025 (in force 28 Sep 2025; was PPR 2008 r.25): the tender security
# stays valid for the tender validity
# period plus 28 days.
BID_SECURITY_EXTRA_DAYS = 28

# Bond amount bands, in % of their base. Business defaults the business must
# confirm (report §7.4, tender-bond policy under PPR 2025, which replaced PPR 2008):
#   bid          at most 3% of the tender's official estimated cost, a fixed amount (PPR 2025)
#   performance  5% to 10% of the awarded contract value (PPR 2025; the BPPA STDs
#                ask 10%, furnished within 7 working days of the NoA)
#   advance      up to the awarded value
BOND_BANDS = {
    "bid": (0.0, 3.0),
    "performance": (5.0, 10.0),
    "advance": (0.0, 100.0),
}

# Releasing or recording the encashment of a bank guarantee is a money
# decision on its amount: the estate cost ladder (cd_rental_asset
# fix_rental_fleet.py, reused by cd_facility ESTATE_COST_DOFA_THRESHOLDS) —
# Tier 2 up to BDT 250,000, Tier 3 up to 1,000,000, Tier 4 (CFO) above.
BOND_DOFA_THRESHOLDS = [
    (0.0, "tier_0"),
    (250000.0, "tier_2"),
    (1000000.0, "tier_3"),
    (float("inf"), "tier_4"),
]

# AUT-QTE-14: Finance is alerted this many days before a guarantee expires.
BOND_EXPIRY_ALERT_DAYS = 30

COMMERCIAL_MANAGER = "cd_quotation.group_quotation_manager"
# Variation cap (report §6 P2 M36; PPR 2025-style cumulative variation
# limit). BUSINESS DEFAULT THE BUSINESS MUST CONFIRM (report §7.4): 15% of the
# awarded contract value, overridable in this ir.config_parameter. Within the
# cap a variation, or an award that differs from the bid lodged, is decided
# by the Tender Committee; beyond it by the Commercial Manager (CCO).
VARIATION_CAP_PARAM = "cd_quotation.variation_cap_pct"
VARIATION_CAP_DEFAULT = 15.0


def variation_cap_pct(env) -> float:
    raw = env["ir.config_parameter"].sudo().get_param(VARIATION_CAP_PARAM)
    try:
        return float(raw) if raw not in (None, False, "") else VARIATION_CAP_DEFAULT
    except (TypeError, ValueError):
        return VARIATION_CAP_DEFAULT


TENDER_STAMPS = frozenset(
    {
        "state",
        "bid_decision",
        "bid_decision_by",
        "bid_decision_at",
        "bid_decision_reason",
        "submitted_at",
        "submitted_by",
        "award_requested_by",
        "awarded_by",
        "award_date",
        "loss_reason",
        "cancel_reason",
        "converted_res_model",
        "converted_res_id",
        "converted_ref",
    }
)
# Frozen once the bid is submitted (the bid as lodged).
TENDER_BID_TERMS = frozenset(
    {
        "client_name",
        "client_id",
        "reference",
        "due_date",
        "estimated_value",
        "currency_id",
        "bonds_required",
        "bid_security_amount",
        "bid_validity_days",
        "score_fit",
        "score_capacity",
        "score_competition",
        "score_margin",
        "score_risk",
        "bid_value",
    }
)
# Frozen once the outcome is decided.
TENDER_AWARD_TERMS = frozenset(
    {
        "awarded_value",
        "award_ref",
        "awarded_to",
        "winning_value",
        "contract_family",
        "contract_months",
        "performance_security_pct",
        "operating_unit_id",
        "outcome_note",
        "name",
    }
)
TENDER_DECIDED = ("no_bid", "won", "lost", "cancelled")


class FixTender(models.Model):
    _name = "fix.tender"
    _description = "Tender"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "due_date, id"

    # C4/C9: the award is a routed M63 decision of the Tender Committee.
    _approval_domain = "tender_award"
    _approval_group = TENDER_COMMITTEE
    _approval_apply_method = "action_award_approve"
    _approval_routed = True

    name = fields.Char(required=True)
    reference = fields.Char(string="Tender ID / e-GP Ref", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    client_name = fields.Char(string="Tendering Client", required=True)
    client_id = fields.Many2one(
        "res.partner",
        string="Procuring Entity",
        ondelete="restrict",
        help="The party the contract is signed with on an award.",
    )
    due_date = fields.Date(required=True)
    estimated_value = fields.Monetary(
        currency_field="currency_id", help="The official estimated cost (the PPR bond base)."
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # Compliance matrix (FR-QTE-045): computed from the requirements, never typed.
    requirement_ids = fields.One2many(
        "fix.tender.requirement", "tender_id", string="Compliance Matrix"
    )
    compliance_pct = fields.Float(
        string="Compliance %",
        compute="_compute_compliance",
        store=True,
        help="Share of mandatory requirements complied with (or not applicable).",
    )
    open_mandatory_count = fields.Integer(
        string="Open Mandatory Items", compute="_compute_compliance", store=True
    )
    bonds_required = fields.Boolean(string="Bid Security Required")
    bid_security_amount = fields.Monetary(
        string="Bid Security Required (BDT)",
        currency_field="currency_id",
        help="The amount the tender documents require.",
    )
    bid_validity_days = fields.Integer(
        string="Bid Validity (days)",
        help="Tender validity after the deadline; the bid security must cover it plus "
        "28 days (PPR 2025).",
    )
    # Bid / no-bid (FR-QTE-044): scored 1-5, decided by the Tender Committee.
    score_fit = fields.Integer(string="Score: Fit")
    score_capacity = fields.Integer(string="Score: Capacity")
    score_competition = fields.Integer(string="Score: Competition")
    score_margin = fields.Integer(string="Score: Margin")
    score_risk = fields.Integer(string="Score: Risk")
    bid_score = fields.Float(string="Bid Score (avg)", compute="_compute_bid_score", store=True)
    bid_decision = fields.Selection(
        [("pending", "Not decided"), ("bid", "Bid"), ("no_bid", "No bid")],
        default="pending",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    bid_decision_by = fields.Many2one("res.users", readonly=True, copy=False)
    bid_decision_at = fields.Datetime(readonly=True, copy=False)
    bid_decision_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("no_bid", "No Bid"),
            ("submitted", "Submitted"),
            ("won", "Won"),
            ("lost", "Lost"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        readonly=True,
        copy=False,
        tracking=True,
    )
    submitted_at = fields.Datetime(readonly=True, copy=False)
    submitted_by = fields.Many2one("res.users", readonly=True, copy=False)
    # Award evidence (staged by the bid coordinator, pinned by the request).
    award_ref = fields.Char(string="Notification of Award Ref", copy=False)
    awarded_value = fields.Monetary(currency_field="currency_id", copy=False)
    award_requested_by = fields.Many2one("res.users", readonly=True, copy=False)
    awarded_by = fields.Many2one("res.users", string="Award Approved By", readonly=True, copy=False)
    award_date = fields.Date(readonly=True, copy=False)
    awarded_to = fields.Char(string="Awarded To (on a loss)", copy=False)
    winning_value = fields.Monetary(currency_field="currency_id", copy=False)
    loss_reason = fields.Char(readonly=True, copy=False)
    cancel_reason = fields.Char(readonly=True, copy=False)
    outcome_note = fields.Char()
    # Contract hand-off (C8).
    contract_family = fields.Selection(CONTRACT_FAMILIES, default="managed")
    contract_months = fields.Integer(string="Contract Term (months)", default=12)
    performance_security_pct = fields.Float(
        string="Performance Security (%)",
        help="Required by the tender documents, of the contract value; 0 = none.",
    )
    converted_res_model = fields.Char(readonly=True, copy=False)
    converted_res_id = fields.Many2oneReference(
        model_field="converted_res_model", readonly=True, copy=False
    )
    converted_ref = fields.Char(string="Contract", readonly=True, copy=False)
    # Variation control (report §6 P2 M36): the price lodged, how far the
    # award moved from it, and the variation orders on the awarded contract.
    bid_value = fields.Monetary(
        string="Bid Price Lodged",
        currency_field="currency_id",
        help="Our submitted price; frozen once the bid is submitted.",
    )
    award_variation_pct = fields.Float(
        string="Award vs Bid (%)",
        compute="_compute_variation",
        help="How far the awarded value moved from the bid lodged.",
    )
    variation_ids = fields.One2many("fix.tender.variation", "tender_id", string="Variation Orders")
    approved_variation_total = fields.Monetary(
        currency_field="currency_id", compute="_compute_variation"
    )
    contract_value = fields.Monetary(
        string="Contract Value (with variations)",
        currency_field="currency_id",
        compute="_compute_variation",
    )

    @api.depends("bid_value", "awarded_value", "variation_ids.state", "variation_ids.amount")
    def _compute_variation(self):
        for rec in self:
            bid = rec.bid_value or 0.0
            rec.award_variation_pct = (
                round(abs((rec.awarded_value or 0.0) - bid) / bid * 100.0, 2) if bid else 0.0
            )
            approved = rec.variation_ids.filtered(lambda v: v.state == "approved")
            rec.approved_variation_total = sum(approved.mapped("amount"))
            rec.contract_value = (rec.awarded_value or 0.0) + rec.approved_variation_total

    def _award_beyond_cap(self) -> bool:
        self.ensure_one()
        return self.award_variation_pct > variation_cap_pct(self.env) + 1e-6

    @api.depends("requirement_ids.state", "requirement_ids.mandatory")
    def _compute_compliance(self):
        for rec in self:
            mandatory = rec.requirement_ids.filtered("mandatory")
            done = mandatory.filtered(lambda r: r.state in ("complied", "not_applicable"))
            rec.open_mandatory_count = len(mandatory) - len(done)
            rec.compliance_pct = round(len(done) / len(mandatory) * 100.0, 2) if mandatory else 0.0

    @api.depends("score_fit", "score_capacity", "score_competition", "score_margin", "score_risk")
    def _compute_bid_score(self):
        """A04 ERP audit M36-F16: competition and risk are scored 1 (low) to
        5 (high) and count AGAINST the bid: a high-risk, crowded tender used
        to score higher. They enter the average as 6 - score."""
        for rec in self:
            scores = rec._bid_scores()
            if not all(scores):
                rec.bid_score = 0.0
                continue
            fit, capacity, competition, margin, risk = scores
            adjusted = [fit, capacity, 6 - competition, margin, 6 - risk]
            rec.bid_score = round(sum(adjusted) / len(adjusted), 2)

    def _bid_scores(self):
        return [
            self.score_fit,
            self.score_capacity,
            self.score_competition,
            self.score_margin,
            self.score_risk,
        ]

    @api.constrains(
        "score_fit", "score_capacity", "score_competition", "score_margin", "score_risk"
    )
    def _check_scores(self):
        for rec in self:
            if any(s < 0 or s > 5 for s in rec._bid_scores()):
                raise ValidationError("Bid scores run from 1 to 5 (0 = not scored).")

    @api.constrains("bid_security_amount", "estimated_value", "performance_security_pct")
    def _check_bands(self):
        for rec in self:
            if (rec.bid_security_amount or 0.0) < 0 or (rec.estimated_value or 0.0) < 0:
                raise ValidationError("Tender amounts cannot be negative.")
            low, high = BOND_BANDS["bid"]
            if (
                rec.bid_security_amount
                and rec.estimated_value
                and rec.bid_security_amount > rec.estimated_value * high / 100.0 + 0.005
            ):
                raise ValidationError(
                    "A bid security of BDT %.2f is above %.1f%% of the estimated value "
                    "(PPR 2025)." % (rec.bid_security_amount, high)
                )
            pct = rec.performance_security_pct or 0.0
            low, high = BOND_BANDS["performance"]
            if pct and not low <= pct <= high:
                raise ValidationError(
                    "Performance security must be between %.0f%% and %.0f%% of the contract "
                    "value (PPR 2025)." % (low, high)
                )

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        # The computed figures too: a typed compliance_pct=100 would stick.
        return (
            super()._fix_guarded_fields()
            | TENDER_STAMPS
            | {
                "compliance_pct",
                "open_mandatory_count",
                "bid_score",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(t.state != "draft" for t in self):
            locked |= TENDER_BID_TERMS | {"requirement_ids"}
        if self and any(t.state in TENDER_DECIDED for t in self):
            locked |= TENDER_AWARD_TERMS
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "award_ref",
            "client_id",
            "contract_family",
            "contract_months",
            "performance_security_pct",
            "operating_unit_id",
        }

    def write(self, vals):
        if not self._fix_guard_open():
            for terms, frozen_in, why in (
                (TENDER_BID_TERMS, lambda t: t.state != "draft", "the bid has been lodged"),
                (TENDER_AWARD_TERMS, lambda t: t.state in TENDER_DECIDED, "it is decided"),
            ):
                touched = terms & set(vals)
                if not touched:
                    continue
                hit = self.filtered(
                    lambda t, f=frozen_in, n=touched: f(t)
                    and any(t._fix_guard_differs(k, vals[k], t[k]) for k in n)
                )
                if hit:
                    raise UserError(
                        "Tender %s cannot change: %s (%s)." % (hit[0].name, why, hit[0].state)
                    )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "draft" or rec.approval_state != "none":
                raise UserError("Tender %s is %s: cancel it instead." % (rec.name, rec.state))
        return super().unlink()

    # ---- the approval -------------------------------------------------------
    def _approval_amount(self) -> float:
        return self.awarded_value or 0.0

    def _approval_needed(self) -> bool:
        return (
            self.state == "submitted"
            and bool(self.award_requested_by)
            and (self.awarded_value or 0.0) > 0.0
        )

    def _approval_group_xmlid(self):
        # An award beyond the variation cap of the bid lodged is the
        # Commercial Manager's, not the committee's.
        return COMMERCIAL_MANAGER if self._award_beyond_cap() else TENDER_COMMITTEE

    # ---- helpers -----------------------------------------------------------
    def _bonds(self, bond_type=None, state=None):
        domain = [("tender_id", "in", self.ids)]
        if bond_type:
            domain.append(("bond_type", "=", bond_type))
        if state:
            domain.append(("state", "=", state))
        return self.env["fix.tender.bond"].sudo().search(domain)

    def _valid_bid_security(self, cover_until):
        """Active bid bonds of at least the required amount, valid until
        `cover_until` (A04 audit t_06/t_07: an amount-0 bond typed as active,
        or an expired one, satisfied the gate)."""
        self.ensure_one()
        need = self.bid_security_amount or 0.0
        return self._bonds("bid", "active").filtered(
            lambda b: (b.amount or 0.0) > 0.0
            and b.amount + 0.005 >= need
            and b.expires_on
            and b.expires_on >= cover_until
        )

    def _award_problems(self) -> list:
        self.ensure_one()
        problems = []
        if self.state != "submitted":
            problems.append("Only a submitted tender is awarded; this one is %s." % self.state)
        if not (self.award_ref or "").strip():
            problems.append("Record the Notification of Award reference.")
        if (self.awarded_value or 0.0) <= 0.0:
            problems.append("Record the awarded contract value.")
        if not self.client_id:
            problems.append("Link the procuring entity (the contract party).")
        if not self.operating_unit_id:
            problems.append("Set the operating unit the contract belongs to.")
        if self.contract_months <= 0:
            problems.append("State the contract term in months.")
        if self.bonds_required and not self._valid_bid_security(dhaka_today(self)):
            problems.append(
                "No active, unexpired bid security of BDT %.2f or more is on file "
                "(PPA 2006 / PPR 2025 tender security)." % (self.bid_security_amount or 0.0)
            )
        return problems

    # ---- bid / no-bid ------------------------------------------------------
    def _decide_bid(self, decision, reason):
        reason = (reason or "").strip()
        if not self.env.su and not self.env.user.has_group(TENDER_COMMITTEE):
            raise AccessError("The bid / no-bid decision is the Tender Committee's (FR-QTE-044).")
        for rec in self:
            if rec.state != "draft" or rec.bid_decision != "pending":
                raise UserError("Tender %s already has its bid decision." % rec.name)
            if not reason:
                raise UserError("Record the basis of the bid / no-bid decision.")
            if not all(rec._bid_scores()):
                raise UserError(
                    "Score fit, capacity, competition, margin and risk (1-5) before deciding."
                )
            if rec.create_uid == self.env.user and not self.env.su:
                raise UserError(
                    "Segregation of duties: the person who registered the tender does not "
                    "take its bid decision."
                )
            vals = {
                "bid_decision": decision,
                "bid_decision_by": self.env.user.id,
                "bid_decision_at": fields.Datetime.now(),
                "bid_decision_reason": reason,
            }
            if decision == "no_bid":
                vals["state"] = "no_bid"
            rec._guarded().write(vals)
        return True

    def action_decide_bid(self, reason=None):
        return self._decide_bid("bid", reason)

    def action_decide_no_bid(self, reason=None):
        return self._decide_bid("no_bid", reason)

    # ---- submit ------------------------------------------------------------
    # Tender lifecycle (A04 zero-trust audit 2026-10-31, DISC-36.2): the model
    # was a passive stub. Submission now needs the bid decision, a complete
    # compliance matrix (BRU-QTE-15) and, when required, valid bid security.
    def action_submit(self):
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft tender can be submitted")
            if rec.bid_decision != "bid":
                raise UserError(
                    "Tender %s has no 'bid' decision from the Tender Committee." % rec.name
                )
            if rec.due_date and rec.due_date < today:
                raise UserError(
                    "Tender %s: submission deadline %s is already in the past"
                    % (rec.name, rec.due_date)
                )
            if not rec.requirement_ids.filtered("mandatory"):
                raise UserError(
                    "Tender %s has no compliance matrix: register its mandatory requirements."
                    % rec.name
                )
            if rec.open_mandatory_count:
                raise UserError(
                    "Tender %s: %d mandatory compliance item(s) are still open (BRU-QTE-15)."
                    % (rec.name, rec.open_mandatory_count)
                )
            if (rec.bid_value or 0.0) <= 0.0:
                raise UserError("Record the bid price lodged before submitting.")
            if rec.bonds_required:
                if (rec.bid_security_amount or 0.0) <= 0.0:
                    raise UserError("State the bid security the tender documents require.")
                cover = rec.due_date + timedelta(
                    days=(rec.bid_validity_days or 0) + BID_SECURITY_EXTRA_DAYS
                )
                if not rec._valid_bid_security(cover):
                    raise UserError(
                        "Tender %s needs an active bid security of BDT %.2f valid until at "
                        "least %s (bid validity + 28 days, PPR 2025)."
                        % (rec.name, rec.bid_security_amount, cover)
                    )
            rec._guarded().write(
                {
                    "state": "submitted",
                    "submitted_at": fields.Datetime.now(),
                    "submitted_by": self.env.user.id,
                }
            )
            publish(
                self.env,
                "tender.submitted",
                "fix.tender",
                rec.id,
                {
                    "tender": rec.name,
                    "estimated_value": rec.estimated_value,
                    "compliance_pct": rec.compliance_pct,
                },
            )
        return True

    # ---- outcome -----------------------------------------------------------
    def action_request_award(self, justification=None):
        """Route the win to the Tender Committee with its award evidence."""
        for rec in self:
            if rec.approval_state == "pending":
                raise UserError("Tender %s is already awaiting the award decision." % rec.name)
            problems = rec._award_problems()
            if problems:
                raise UserError("Tender %s: %s" % (rec.name, " ".join(problems)))
            if rec._award_beyond_cap() and not (justification or "").strip():
                raise UserError(
                    "Tender %s was awarded %.1f%% away from the bid lodged, beyond the "
                    "%.1f%% variation cap: state why (the Commercial Manager decides)."
                    % (rec.name, rec.award_variation_pct, variation_cap_pct(self.env))
                )
            rec._guarded().write({"award_requested_by": self.env.user.id})
        return self.action_request_approval(justification=justification)

    def action_award_approve(self):
        """The Tender Committee's award decision, run from the M63 inbox only."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        for rec in self:
            if rec._award_beyond_cap():
                if not authority.has_group(COMMERCIAL_MANAGER):
                    raise UserError(
                        "Tender %s was awarded %.1f%% away from the bid lodged, beyond the "
                        "variation cap: the Commercial Manager decides it."
                        % (rec.name, rec.award_variation_pct)
                    )
            elif not authority.has_group(TENDER_COMMITTEE):
                raise UserError("A tender award is decided by a Tender Committee member.")
            # The committee is separate from the people who prepared the bid
            # (the PPR separation of preparer and evaluator, applied to the bidder's side).
            prepared = rec.create_uid | rec.submitted_by | rec.award_requested_by
            if rec._approval_acting_users() & prepared:
                raise UserError(
                    "Segregation of duties: whoever registered, submitted or requested the "
                    "award of tender %s cannot approve it." % rec.name
                )
            problems = rec._award_problems()
            if problems:
                raise UserError("Tender %s: %s" % (rec.name, " ".join(problems)))
        today = dhaka_today(self)
        for rec in self:
            rec._guarded().write(
                {"state": "won", "awarded_by": self.env.user.id, "award_date": today}
            )
            rec._create_contract_safely()
            publish(
                self.env,
                "tender.outcome_recorded",
                "fix.tender",
                rec.id,
                {
                    "tender": rec.name,
                    "result": "won",
                    "awarded_value": rec.awarded_value,
                    "contract_ref": rec.converted_ref or None,
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"award_requested_by": False})
            rec.message_post(body="Award not approved: %s" % comment)

    def _approval_clear_stamp(self, reason):
        res = super()._approval_clear_stamp(reason)
        self.filtered(lambda t: t.state == "submitted")._guarded().write(
            {"award_requested_by": False}
        )
        return res

    def action_record_loss(self, reason=None):
        reason = (reason or "").strip()
        for rec in self:
            if rec.state != "submitted":
                raise UserError(
                    "Tender %s is %s — only a submitted tender can be decided"
                    % (rec.name, rec.state)
                )
            if not reason:
                raise UserError("Record the loss reason (FR-QTE-048).")
            if rec.approval_state == "pending":
                rec._approval_void("the tender was recorded as lost")
            rec._guarded().write({"state": "lost", "loss_reason": reason})
            rec._fix_close_pricing_quotation("tender %s lost: %s" % (rec.name, reason))
            publish(
                self.env,
                "tender.outcome_recorded",
                "fix.tender",
                rec.id,
                {"tender": rec.name, "result": "lost", "awarded_value": 0.0, "contract_ref": None},
            )
        return True

    def action_record_outcome(self, won, note=""):
        """Kept for the workspace: a loss is recorded here; a win is an
        award decision (Request Award), never a direct write."""
        for rec in self:
            if rec.state != "submitted":
                raise UserError(
                    "Tender %s is %s — only a submitted tender can be decided"
                    % (rec.name, rec.state)
                )
        if won:
            raise UserError(
                "A win is recorded by the award decision: stage the award reference and "
                "value, then Request Award (the Tender Committee approves it)."
            )
        return self.action_record_loss(note)

    def action_cancel(self, reason=None):
        reason = (reason or "").strip()
        for rec in self:
            if rec.state in ("won", "lost", "no_bid", "cancelled"):
                raise UserError("Tender %s is already decided (%s)" % (rec.name, rec.state))
            if not reason:
                raise UserError("Record why the tender is withdrawn.")
            if rec.approval_state == "pending":
                rec._approval_void("the tender was cancelled")
            rec._guarded().write({"state": "cancelled", "cancel_reason": reason})
            rec._fix_close_pricing_quotation("tender %s withdrawn: %s" % (rec.name, reason))
        return True

    # ---- C8 hand-off --------------------------------------------------------
    def _create_contract(self):
        """A won tender becomes an M08 draft contract, through M08's own
        create (fix.contract.create, as the superuser service after the award
        checks); M08's activation path takes it from there. A required
        performance security is opened as a draft bond for the amount the
        tender documents set."""
        self.ensure_one()
        if self.converted_res_id:
            return self.converted_res_id
        if "fix.contract" not in self.env:
            raise UserError("M08 Contracts is not installed; the contract cannot be created.")
        months = self.contract_months or 12
        start = self.award_date or dhaka_today(self)
        # A04 ERP audit M36-F1: the award (like the bid) INCLUDES VAT, and the
        # contract bills VAT on top of its value: 115,000 awarded was billed
        # 132,250. The contract carries the award before VAT.
        ex_vat = self._award_ex_vat()
        contract = (
            self.env["fix.contract"]
            .sudo()
            .create(
                {
                    "name": "Tender %s — %s" % (self.name, self.client_id.name),
                    "family": self.contract_family or "managed",
                    "customer_id": self.client_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "company_id": self.company_id.id,
                    "currency_id": self.currency_id.id,
                    "date_start": start,
                    "date_end": start + relativedelta(months=months) - timedelta(days=1),
                    "annual_value": round(ex_vat * 12.0 / months, 2),
                    "term_value": ex_vat,
                    "accepted_total": round(self.awarded_value or 0.0, 2),
                }
            )
        )
        self._fix_contract_terms_from_award(contract)
        self._guarded().write(
            {
                "converted_res_model": contract._name,
                "converted_res_id": contract.id,
                "converted_ref": contract.display_name,
            }
        )
        if self.performance_security_pct and not self._bonds("performance"):
            self.env["fix.tender.bond"].sudo().create(
                {
                    "tender_id": self.id,
                    "bond_type": "performance",
                    "currency_id": self.currency_id.id,
                    "amount": round(
                        (self.awarded_value or 0.0) * self.performance_security_pct / 100.0, 2
                    ),
                }
            )
        return contract.id

    def _award_ex_vat(self) -> float:
        """The awarded value before VAT: in the proportion of the pricing
        quotation (its value over its total payable), else M51's rate."""
        self.ensure_one()
        awarded = self.awarded_value or 0.0
        quote = self.quotation_id.sudo() if "quotation_id" in self._fields else None
        if quote and (quote.amount_total or 0.0) > 0.0:
            return round(awarded * (quote.value or 0.0) / quote.amount_total, 2)
        from decimal import Decimal

        from odoo.addons.cd_billing_engine.models.fix_billing_engine import m51_determine
        from odoo.addons.cd_tax_engine_bd.models import tax_logic

        det = m51_determine(
            self.env,
            [tax_logic.TaxLine(product_code="AMC", qty=Decimal("1"), unit_price=Decimal("100"))],
            on_date=self.award_date or dhaka_today(self),
            company=self.company_id,
        ).lines[0]
        rate = float(det.rate or 0.0) / 100.0
        return round(awarded / (1.0 + rate), 2)

    def _fix_contract_terms_from_award(self, contract):
        """A04 ERP audit M36-F9: the won tender's contract carries the BOQ as
        its scope and the tender's retention and liquidated-damages terms, and
        the pricing quotation is closed as accepted by the award (it stayed
        'approved' for ever)."""
        self.ensure_one()
        vals = {}
        for name in ("retention_pct", "ld_rate_pct_per_day", "ld_cap_pct"):
            if name in self._fields and name in contract._fields:
                vals[name] = self[name] or 0.0
        if "tender_id" in contract._fields:
            vals["tender_id"] = self.id
        if vals:
            contract.sudo().write(vals)
        quote = self.quotation_id.sudo() if "quotation_id" in self._fields else None
        if not quote:
            return
        if hasattr(quote, "_fulfil_contract_scope") and not contract.scope_line_ids:
            quote._fulfil_contract_scope(contract)
        if quote.state not in ("accepted", "cancelled", "superseded"):
            quote._guarded().write(
                {
                    "state": "accepted",
                    "accepted_at": fields.Datetime.now(),
                    "acceptance_method": "tender_award",
                    "acceptance_ref": "NoA %s" % (self.award_ref or self.name),
                    "accepted_value": quote.value,
                    "accepted_total": self.awarded_value,
                    "accepted_version": quote.version,
                    "converted_res_model": contract._name,
                    "converted_res_id": contract.id,
                    "converted_ref": contract.display_name,
                    "converted_at": fields.Datetime.now(),
                }
            )

    def _fix_close_pricing_quotation(self, reason):
        """A lost or withdrawn tender closes its pricing quotation."""
        for rec in self:
            quote = rec.quotation_id.sudo() if "quotation_id" in rec._fields else None
            if quote and quote.state in ("draft", "approved", "sent"):
                if quote.approval_state in ("pending", "approved"):
                    quote._approval_void(reason)
                quote._guarded().write({"state": "cancelled", "cancel_reason": reason})

    def _create_contract_safely(self):
        try:
            with self.env.cr.savepoint():
                return self._create_contract()
        except (UserError, ValidationError, AccessError) as exc:
            self.message_post(
                body="Won; the contract is not created yet: %s" % (exc.args[0] if exc.args else exc)
            )
            return False

    def action_create_contract(self):
        for rec in self:
            if rec.state != "won":
                raise UserError("Only a won tender becomes a contract.")
            rec._create_contract()
        return True


class FixTenderVariation(models.Model):
    """A variation order on an awarded tender's contract (report §6 P2 M36,
    variation cap). Within the cumulative cap the Tender Committee decides
    it; beyond the cap the Commercial Manager. Routed through M63, never the
    person who raised or requested it. An approved variation is handed to
    M08 by the tender.variation_approved event (M08 applies it through its
    own amendment path)."""

    _name = "fix.tender.variation"
    _description = "Tender / Contract Variation Order"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "tender_id, id"

    _approval_domain = "tender_variation"
    _approval_apply_method = "action_approve_variation"
    _approval_routed = True

    name = fields.Char(string="Variation Ref", required=True)
    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="tender_id.company_id", store=True)
    currency_id = fields.Many2one(related="tender_id.currency_id")
    amount = fields.Monetary(
        currency_field="currency_id", help="Change to the contract value (negative = omission)."
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    cumulative_pct = fields.Float(
        string="Cumulative Variation (%)",
        compute="_compute_cumulative",
        help="Approved variations plus this one, in absolute terms, against the " "awarded value.",
    )
    within_cap = fields.Boolean(compute="_compute_cumulative")

    @api.depends("amount", "tender_id.awarded_value", "tender_id.variation_ids.state")
    def _compute_cumulative(self):
        cap = variation_cap_pct(self.env)
        for rec in self:
            base = rec.tender_id.awarded_value or 0.0
            others = rec.tender_id.variation_ids.filtered(
                lambda v, r=rec: v.state == "approved" and v.id != r.id
            )
            moved = sum(abs(v.amount or 0.0) for v in others) + abs(rec.amount or 0.0)
            rec.cumulative_pct = round(moved / base * 100.0, 2) if base else 0.0
            rec.within_cap = bool(base) and rec.cumulative_pct <= cap + 1e-6

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by", "approved_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(v.state != "draft" for v in self):
            locked |= {"name", "tender_id", "amount", "reason"}
        return locked

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"tender_id", "reason"}

    def _approval_amount(self) -> float:
        return abs(self.amount or 0.0)

    def _approval_needed(self) -> bool:
        return self.state == "draft" and bool(self.amount) and self.tender_id.state == "won"

    def _approval_group_xmlid(self):
        return TENDER_COMMITTEE if self.within_cap else COMMERCIAL_MANAGER

    def write(self, vals):
        touched = {"name", "tender_id", "amount", "reason"} & set(vals)
        if touched and not self._fix_guard_open():
            hit = self.filtered(
                lambda v: v.state != "draft"
                and any(v._fix_guard_differs(n, vals[n], v[n]) for n in touched)
            )
            if hit:
                raise UserError(
                    "Variation %s is %s and cannot change." % (hit[0].name, hit[0].state)
                )
        return super().write(vals)

    def unlink(self):
        if any(v.state != "draft" or v.approval_state != "none" for v in self):
            raise UserError("A decided or requested variation is cancelled, not deleted.")
        return super().unlink()

    def _problems(self) -> list:
        self.ensure_one()
        problems = []
        if self.state != "draft":
            problems.append("Variation %s is %s." % (self.name, self.state))
        if self.tender_id.state != "won":
            problems.append("Only an awarded (won) tender is varied.")
        if not self.amount:
            problems.append("State the change to the contract value.")
        if not (self.reason or "").strip():
            problems.append("State the reason for the variation.")
        return problems

    def action_request(self, justification=None):
        for rec in self:
            problems = rec._problems()
            if problems:
                raise UserError(" ".join(problems))
        return self.action_request_approval(justification=justification)

    def action_approve_variation(self):
        """The decision, from the M63 inbox only."""
        self._approval_assert_routed()
        authority = self._approval_authority_user()
        now = fields.Datetime.now()
        for rec in self:
            problems = rec._problems()
            if problems:
                raise UserError(" ".join(problems))
            needed = TENDER_COMMITTEE if rec.within_cap else COMMERCIAL_MANAGER
            if not authority.has_group(needed):
                raise UserError(
                    "Variation %s brings the cumulative variation to %.1f%% of the awarded "
                    "value; %s decides it (cap %.1f%%)."
                    % (
                        rec.name,
                        rec.cumulative_pct,
                        "a Tender Committee member" if rec.within_cap else "the Commercial Manager",
                        variation_cap_pct(self.env),
                    )
                )
            if rec._approval_acting_users() & (
                rec.create_uid | rec.approval_request_id.sudo().requested_by_id
            ):
                raise UserError(
                    "Segregation of duties: whoever raised or requested variation %s cannot "
                    "approve it." % rec.name
                )
            rec._guarded().write(
                {"state": "approved", "approved_by": self.env.user.id, "approved_at": now}
            )
            publish(
                self.env,
                "tender.variation_approved",
                "fix.tender.variation",
                rec.id,
                {
                    "tender": rec.tender_id.name,
                    "variation": rec.name,
                    "amount": rec.amount,
                    "cumulative_pct": rec.cumulative_pct,
                    "contract_ref": rec.tender_id.converted_ref or None,
                },
            )
        return True

    def _approval_on_rejected(self, comment):
        self.filtered(lambda v: v.state == "draft")._guarded().write({"state": "rejected"})

    def action_cancel(self, reason=None):
        if not (reason or "").strip():
            raise UserError("Record why the variation is withdrawn.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft variation is cancelled.")
            if rec.approval_state == "pending":
                rec._approval_void("the variation was withdrawn")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(body="Withdrawn: %s" % reason)
        return True


class FixTenderRequirement(models.Model):
    """One line of the compliance matrix (FR-QTE-045)."""

    _name = "fix.tender.requirement"
    _description = "Tender Compliance Requirement"
    _order = "tender_id, sequence, id"

    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    clause_ref = fields.Char(string="Clause")
    requirement = fields.Char(required=True)
    mandatory = fields.Boolean(default=True)
    owner_id = fields.Many2one("res.users", string="Owner")
    response = fields.Char()
    evidence_ref = fields.Char(string="Evidence Document Ref")
    state = fields.Selection(
        [
            ("open", "Open"),
            ("complied", "Complied"),
            ("deviation", "Deviation"),
            ("not_applicable", "Not applicable"),
        ],
        default="open",
        required=True,
    )

    @api.constrains("state", "evidence_ref", "mandatory")
    def _check_evidence(self):
        for rec in self:
            if rec.mandatory and rec.state == "complied" and not (rec.evidence_ref or "").strip():
                raise ValidationError(
                    "Mandatory requirement '%s' is complied with only against its evidence "
                    "document." % rec.requirement
                )

    def _assert_tender_open(self, tenders):
        if self.env.su:
            return
        lodged = tenders.filtered(lambda t: t.state != "draft")
        if lodged:
            raise UserError(
                "The compliance matrix of tender %s is frozen: the bid is %s."
                % (lodged[0].name, lodged[0].state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v["tender_id"] for v in vals_list if v.get("tender_id")]
        tenders = self.env["fix.tender"].browse(ids).exists()
        self._assert_tender_open(tenders)
        return super().create(vals_list)

    def write(self, vals):
        self._assert_tender_open(self.mapped("tender_id"))
        if "tender_id" in vals:
            self._assert_tender_open(self.env["fix.tender"].browse(vals["tender_id"]).exists())
        return super().write(vals)

    def unlink(self):
        self._assert_tender_open(self.mapped("tender_id"))
        return super().unlink()


BOND_STAMPS = frozenset(
    {
        "state",
        "requested_action",
        "release_ref",
        "claim_reason",
        "activated_at",
        "activated_by",
        "released_at",
        "released_by",
        "claimed_at",
        "claimed_by",
        "expiry_alerted_on",
        # A04 ERP audit M36-F6: the GL entries of the bond's cash legs
        "funding_move_id",
        "release_move_id",
        "claim_move_id",
    }
)
# What the bank issued: frozen once the guarantee is active.
BOND_TERMS = frozenset(
    {
        "tender_id",
        "bond_type",
        "amount",
        "currency_id",
        "bank",
        "guarantee_no",
        "issued_on",
        "expires_on",
        "instrument",
        "margin_amount",
        "charges_amount",
    }
)


class FixTenderBond(models.Model):
    _name = "fix.tender.bond"
    _description = "Tender Bond"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "expires_on, id"

    # C4/C9: release and encashment are routed DOFA decisions on the amount.
    _approval_domain = "tender_bond"
    _approval_apply_method = "action_bond_decision_approve"
    _approval_routed = True

    name = fields.Char(compute="_compute_name", store=True)
    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    bond_type = fields.Selection(
        [
            ("bid", "Bid bond"),
            ("performance", "Performance bond"),
            ("advance", "Advance payment guarantee"),
        ],
        required=True,
        default="bid",
    )
    amount = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    bank = fields.Char()
    guarantee_no = fields.Char(string="Bank Guarantee No.")
    issued_on = fields.Date()
    expires_on = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("released", "Released"),
            ("claimed", "Claimed"),
            ("expired", "Expired"),
        ],
        required=True,
        default="draft",
        readonly=True,
        copy=False,
        tracking=True,
    )
    requested_action = fields.Selection(
        [("none", "None"), ("release", "Release"), ("claim", "Claim (encashment)")],
        default="none",
        required=True,
        readonly=True,
        copy=False,
    )
    release_ref = fields.Char(string="Bank Discharge / Return Ref", readonly=True, copy=False)
    claim_reason = fields.Char(readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)
    activated_by = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)
    released_by = fields.Many2one("res.users", readonly=True, copy=False)
    claimed_at = fields.Datetime(readonly=True, copy=False)
    claimed_by = fields.Many2one("res.users", readonly=True, copy=False)
    expiry_alerted_on = fields.Date(readonly=True, copy=False)
    # A04 audit M36-9 (b_08): a STORED flag computed from the UTC today() froze
    # at False with 5 days left. Live, in Dhaka time, searchable.
    is_expiring_soon = fields.Boolean(
        string="Expiring Soon (30d)",
        compute="_compute_expiry",
        search="_search_expiring_soon",
        help="An active guarantee within 30 days of expiry.",
    )
    days_to_expiry = fields.Integer(compute="_compute_expiry")

    @api.depends("bond_type", "guarantee_no", "tender_id.name")
    def _compute_name(self):
        labels = dict(self._fields["bond_type"].selection)
        for rec in self:
            rec.name = "%s %s (%s)" % (
                labels.get(rec.bond_type, ""),
                rec.guarantee_no or "unissued",
                rec.tender_id.name or "",
            )

    def _compute_expiry(self):
        today = dhaka_today(self)
        for rec in self:
            days = (rec.expires_on - today).days if rec.expires_on else 0
            rec.days_to_expiry = days
            rec.is_expiring_soon = bool(
                rec.state == "active" and rec.expires_on and days <= BOND_EXPIRY_ALERT_DAYS
            )

    def _search_expiring_soon(self, operator, value):
        if operator in ("in", "not in"):
            positive = (True in value) == (operator == "in")
        elif operator in ("=", "!="):
            positive = bool(value) == (operator == "=")
        else:
            raise UserError("Unsupported search on 'Expiring Soon'.")
        limit = dhaka_today(self) + timedelta(days=BOND_EXPIRY_ALERT_DAYS)
        soon = [("state", "=", "active"), ("expires_on", "!=", False), ("expires_on", "<=", limit)]
        if positive:
            return soon
        return [
            "|",
            "|",
            ("state", "!=", "active"),
            ("expires_on", "=", False),
            ("expires_on", ">", limit),
        ]

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | BOND_STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(b.state != "draft" for b in self):
            locked |= BOND_TERMS
        return locked

    def _approval_pinned_fields(self) -> set:
        # requested_action is guarded, so no user re-points a pending request;
        # pinning it would void the request when the decision clears it.
        return super()._approval_pinned_fields() | {"tender_id", "bond_type"}

    def write(self, vals):
        if not self._fix_guard_open():
            touched = BOND_TERMS & set(vals)
            if touched:
                hit = self.filtered(
                    lambda b: b.state != "draft"
                    and any(b._fix_guard_differs(n, vals[n], b[n]) for n in touched)
                )
                if hit:
                    raise UserError(
                        "Bond %s is %s: what the bank issued (amount, bank, guarantee, "
                        "dates, type) is frozen. An extension is recorded with Extend."
                        % (hit[0].name, hit[0].state)
                    )
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Bond %s is %s and cannot be deleted." % (rec.name, rec.state))
        return super().unlink()

    # ---- DOFA --------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount or 0.0

    def _dofa_thresholds(self):
        return BOND_DOFA_THRESHOLDS

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return (
            self.state == "active"
            and self.requested_action in ("release", "claim")
            and super()._approval_needed()
        )

    # ---- helpers -----------------------------------------------------------
    def _band_problems(self) -> list:
        self.ensure_one()
        tender = self.tender_id.sudo()
        low, high = BOND_BANDS[self.bond_type]
        if self.bond_type == "bid":
            base = tender.estimated_value or 0.0
            problems = []
            if base and self.amount > base * high / 100.0 + 0.005:
                problems.append(
                    "BDT %.2f is above %.1f%% of the tender's estimated value BDT %.2f "
                    "(PPR 2025)." % (self.amount, high, base)
                )
            if tender.bid_security_amount and self.amount + 0.005 < tender.bid_security_amount:
                problems.append(
                    "BDT %.2f is below the BDT %.2f the tender requires."
                    % (self.amount, tender.bid_security_amount)
                )
            return problems
        base = tender.awarded_value or 0.0
        if tender.state != "won" or not base:
            return ["A %s secures an awarded contract; the tender is not won." % self.bond_type]
        if not (base * low / 100.0 - 0.005 <= self.amount <= base * high / 100.0 + 0.005):
            return [
                "BDT %.2f is outside %.0f%%-%.0f%% of the awarded value BDT %.2f."
                % (self.amount, low, high, base)
            ]
        return []

    def _release_blockers(self) -> list:
        """Release only after the award (PPR 2025): a bid security
        while its tender is undecided, or a performance security while its
        contract runs, stays with the procuring entity."""
        self.ensure_one()
        tender = self.tender_id.sudo()
        if self.bond_type == "bid":
            if tender.state not in TENDER_DECIDED:
                return [
                    "The bid security is released only after the outcome; tender %s is %s."
                    % (tender.name, tender.state)
                ]
            if (
                tender.state == "won"
                and tender.performance_security_pct
                and not tender._bonds("performance", "active")
            ):
                return [
                    "On a win the bid security is returned once the performance security "
                    "is furnished (active)."
                ]
            return []
        model, res_id = tender.converted_res_model, tender.converted_res_id
        contract = self.env[model].sudo().browse(res_id).exists() if model in self.env else None
        if not contract:
            return ["A %s is released at the end of its contract; none is linked." % self.bond_type]
        if "state" in contract._fields and contract.state not in ("expired", "terminated"):
            return [
                "Contract %s is %s: its %s stays in force."
                % (contract.display_name, contract.state, self.bond_type)
            ]
        return []

    def _event(self, event_type):
        self.ensure_one()
        publish(
            self.env,
            event_type,
            "fix.tender.bond",
            self.id,
            {
                "bond": self.name,
                "tender": self.tender_id.name,
                "bond_type": self.bond_type,
                "amount": self.amount,
                "currency": self.currency_id.name,
                "bank": self.bank or "",
                "guarantee_no": self.guarantee_no or "",
            },
        )

    # ---- lifecycle ---------------------------------------------------------
    def action_activate(self):
        """The bank issued the guarantee: record it with its evidence."""
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft bond is activated; %s is %s." % (rec.name, rec.state))
            problems = []
            if (rec.amount or 0.0) <= 0.0:
                problems.append("The guarantee amount is missing.")
            if not (rec.bank or "").strip() or not (rec.guarantee_no or "").strip():
                problems.append("Record the issuing bank and the guarantee number.")
            if not rec.expires_on or rec.expires_on <= today:
                problems.append("The guarantee must expire after today.")
            if rec.issued_on and rec.issued_on > today:
                problems.append("The issue date cannot be in the future.")
            tender = rec.tender_id.sudo()
            if rec.bond_type == "bid" and tender.state not in ("draft", "submitted"):
                problems.append(
                    "Tender %s is %s: no bid security is lodged now."
                    % (
                        tender.name,
                        tender.state,
                    )
                )
            if not problems:
                problems = rec._band_problems()
            if problems:
                raise UserError("Bond %s: %s" % (rec.name, " ".join(problems)))
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_at": fields.Datetime.now(),
                    "activated_by": self.env.user.id,
                }
            )
            rec._event("tender_bond.activated")
        return True

    def action_release(self, release_ref=None):
        """Ask for the release, with the bank's discharge reference."""
        release_ref = (release_ref or "").strip()
        for rec in self:
            rec._assert_requestable()
            if not release_ref:
                raise UserError("Record the bank's discharge / return reference.")
            blockers = rec._release_blockers()
            if blockers:
                raise UserError("Bond %s: %s" % (rec.name, " ".join(blockers)))
            rec._guarded().write({"requested_action": "release", "release_ref": release_ref})
        return self.action_request_approval(justification="Release: %s" % release_ref)

    def action_claim(self, reason=None):
        """Record that the procuring entity encashed the guarantee: a loss,
        decided like the release."""
        reason = (reason or "").strip()
        for rec in self:
            rec._assert_requestable()
            if not reason:
                raise UserError("Record why the guarantee was encashed.")
            rec._guarded().write({"requested_action": "claim", "claim_reason": reason})
        return self.action_request_approval(justification="Claim: %s" % reason)

    def _assert_requestable(self):
        self.ensure_one()
        if self.state != "active":
            raise UserError(
                "Bond %s is %s: only an active guarantee is released or claimed."
                % (self.name, self.state)
            )
        if self.approval_state == "pending":
            raise UserError("Bond %s already has a decision pending." % self.name)

    def action_bond_decision_approve(self):
        """The DOFA approver's decision, run from the M63 inbox only."""
        self.action_dofa_approve()  # routed; tier from the amount; not the creator
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "active" or rec.requested_action not in ("release", "claim"):
                raise UserError("Bond %s has no pending release or claim." % rec.name)
            if rec.requested_action == "release":
                blockers = rec._release_blockers()
                if blockers:
                    raise UserError("Bond %s: %s" % (rec.name, " ".join(blockers)))
                rec._guarded().write(
                    {
                        "state": "released",
                        "released_at": now,
                        "released_by": self.env.user.id,
                        "requested_action": "none",
                    }
                )
                rec._event("tender_bond.released")
            else:
                rec._guarded().write(
                    {
                        "state": "claimed",
                        "claimed_at": now,
                        "claimed_by": self.env.user.id,
                        "requested_action": "none",
                    }
                )
                rec._event("tender_bond.claimed")
        return True

    def _clear_request(self):
        self.filtered(
            lambda b: b.state == "active" and b.requested_action != "none"
        )._guarded().write(
            {"requested_action": "none", "release_ref": False, "claim_reason": False}
        )

    def _approval_on_rejected(self, comment):
        self._clear_request()

    def _approval_clear_stamp(self, reason):
        res = super()._approval_clear_stamp(reason)
        self._clear_request()
        return res

    def action_extend(self, expires_on=None):
        """The bank extended the guarantee (AUT-QTE-14)."""
        new = fields.Date.to_date(expires_on) if expires_on else False
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active guarantee is extended.")
            if not new or (rec.expires_on and new <= rec.expires_on):
                raise UserError("The new expiry must be later than %s." % rec.expires_on)
            old = rec.expires_on
            rec._guarded().write({"expires_on": new, "expiry_alerted_on": False})
            rec.message_post(body="Guarantee extended from %s to %s." % (old, new))
        return True

    @api.model
    def cron_bond_expiry(self):
        """AUT-QTE-14, daily and idempotent: an active guarantee past its
        expiry becomes expired; one within 30 days alerts its owner once per
        expiry date (an extension re-arms the alert)."""
        today = dhaka_today(self)
        active = self.sudo().search([("state", "=", "active"), ("expires_on", "!=", False)])
        lapsed = active.filtered(lambda b: b.expires_on < today)
        for rec in lapsed:
            rec._guarded().write({"state": "expired", "requested_action": "none"})
            rec.message_post(body="The guarantee expired on %s." % rec.expires_on)
            rec._event("tender_bond.expired")
        soon = (active - lapsed).filtered(
            lambda b: (b.expires_on - today).days <= BOND_EXPIRY_ALERT_DAYS
            and not b.expiry_alerted_on
        )
        for rec in soon:
            owner = rec.activated_by or rec.tender_id.create_uid
            if owner and not owner.share and owner.active:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=rec.expires_on,
                    summary="Bank guarantee expires on %s" % rec.expires_on,
                    note="Extend or recover the guarantee before it lapses (AUT-QTE-14).",
                    user_id=owner.id,
                )
            rec.message_post(body="Expiry alert: the guarantee expires on %s." % rec.expires_on)
            rec._guarded().write({"expiry_alerted_on": today})
        return len(lapsed) + len(soon)
