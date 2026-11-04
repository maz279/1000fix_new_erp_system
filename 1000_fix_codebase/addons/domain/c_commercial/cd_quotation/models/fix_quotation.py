# cd_quotation — M36 Quotation & Estimation (P06-M06-T05/T07, CD-M36-02).
#
# T07: ONE estimate concept, not two — this module EXTENDS M01's
# fix.estimate (AS-01: a single estimate model across the estate) with the
# quotation lifecycle: sent -> negotiated -> accepted/declined, the
# approval loop (CD-M36-03) and tender seam data.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

# BRU-PRC-06, the ONE discount ladder (A04 build 2026-11-04, report §6 P2
# M11): the released bands of fix.discount.policy (cd_rate_card,
# discount_ladder()/tier_for_discount()). This copy of the spec's default is
# used only when cd_rate_card is not installed: <=10% the agent's own
# authority, <=20% branch manager (Tier 2), <=35% sales manager (Tier 3),
# above that the CCO (Tier 4).
SPEC_DISCOUNT_LADDER = (
    (10.0, "tier_0"),
    (20.0, "tier_2"),
    (35.0, "tier_3"),
    (float("inf"), "tier_4"),
)
TIER_GROUP = {
    "tier_1": "cd_entity_config.group_dofa_tier_1",
    "tier_2": "cd_entity_config.group_dofa_tier_2",
    "tier_3": "cd_entity_config.group_dofa_tier_3",
    "tier_4": "cd_entity_config.group_dofa_tier_4",
    "tier_5": "cd_entity_config.group_dofa_tier_5",
}
TIER_LABEL = {
    "tier_1": "a team lead (DOFA Tier 1)",
    "tier_2": "a branch manager (DOFA Tier 2)",
    "tier_3": "a sales manager / commercial director (DOFA Tier 3)",
    "tier_4": "the CCO (DOFA Tier 4)",
    "tier_5": "the Managing Director (DOFA Tier 5)",
}

# The estimate's quotation stamps change only through its actions (A04 audit
# 2026-11-03, M36-2): quotation_state was a free field, and A02's own
# whitelist let the workspace write quotation_state='accepted' on a DRAFT
# estimate.
ESTIMATE_QUOTE_STAMPS = frozenset(
    {
        "quotation_state",
        "sent_at",
        "accepted_at",
        "declined_at",
        "quotation_accepted_by",
        "quotation_decline_reason",
    }
)


def dhaka_today(record):
    """Today in the user's timezone, Dhaka when none is set (A04 audit
    M36-9: fields.Date.today() is the UTC date, wrong six hours a day)."""
    tz = record.env.context.get("tz") or record.env.user.tz or "Asia/Dhaka"
    return fields.Date.context_today(record.with_context(tz=tz))


def dhaka_date(record, stamp):
    """The calendar date of a UTC datetime stamp, in Dhaka time."""
    if not stamp:
        return False
    tz = record.env.context.get("tz") or record.env.user.tz or "Asia/Dhaka"
    return fields.Datetime.context_timestamp(record.with_context(tz=tz), stamp).date()


class FixApprovalMatrixQuotation(models.Model):
    """M36 decision domains on the DoA register (A04 audit 2026-11-03, C4/C9)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("quotation", "Quotation Internal Approval"),
            ("tender_award", "Tender Award"),
            ("tender_bond", "Tender Bond Release / Claim"),
            ("tender_variation", "Tender / Contract Variation"),
        ],
        ondelete=dict.fromkeys(
            ("quotation", "tender_award", "tender_bond", "tender_variation"), "cascade"
        ),
    )


class FixEstimate(models.Model):
    """Extend M01's estimate with the M36 quotation lifecycle."""

    _inherit = "fix.estimate"

    quotation_state = fields.Selection(
        [
            ("internal", "Internal Estimate"),
            ("quoted", "Quoted to Customer"),
            ("negotiating", "Negotiating"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("expired", "Expired"),
        ],
        string="Quotation State",
        default="internal",
        readonly=True,
        copy=False,
        tracking=True,
        help="M01 created the estimate; M36 quotes it — one record, one lifecycle. "
        "Changes only through Quote / Accept / Decline.",
    )
    valid_days = fields.Integer(
        default=15,
        help="Quotation validity window in days (BRU-SRM-13: "
        "expired estimates are re-issued, never extended)",
    )
    sent_at = fields.Datetime(readonly=True, copy=False)
    accepted_at = fields.Datetime(readonly=True, copy=False)
    declined_at = fields.Datetime(readonly=True, copy=False)
    quotation_accepted_by = fields.Many2one(
        "res.users", string="Acceptance Recorded By", readonly=True, copy=False
    )
    quotation_decline_reason = fields.Char(
        string="Quotation Decline Reason", readonly=True, copy=False
    )
    approval_ids = fields.One2many(
        "fix.discount.approval", "quotation_id", string="Discount Approvals"
    )
    tender_ref = fields.Char(
        string="Tender Reference",
        index=True,
        help="Tender management seam (CD-M36-05, P04 portal W4+)",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | ESTIMATE_QUOTE_STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(e.quotation_state != "internal" for e in self):
            # BRU-SRM-13: a quoted validity window is never extended.
            locked.add("valid_days")
        return locked

    def write(self, vals):
        if "valid_days" in vals and not self._fix_guard_open():
            quoted = self.filtered(
                lambda e: e.quotation_state != "internal" and e.valid_days != vals["valid_days"]
            )
            if quoted:
                raise UserError(
                    "The validity window of a quoted estimate cannot change (BRU-SRM-13: "
                    "an expired quotation is re-issued, never extended). Revise the estimate."
                )
        return super().write(vals)

    def _quotation_valid_until(self):
        """The last day the customer may accept: the Dhaka date it was sent
        plus the validity window."""
        self.ensure_one()
        sent = dhaka_date(self, self.sent_at)
        return sent + timedelta(days=self.valid_days) if sent else False

    def _quotation_discount_blockers(self) -> list:
        """Why the discount on this estimate may not be quoted (A04 audit
        M36-3/M36-5: a discount request was free-typed and never compared with
        the estimate it approved). A pending request blocks; the latest
        decided request must be an approval that covers the discount the
        estimate actually carries."""
        self.ensure_one()
        requests = self.sudo().approval_ids.sorted("id")
        if requests.filtered(lambda a: a.state == "pending"):
            return ["A pending discount approval blocks quoting."]
        decided = requests.filtered(lambda a: a.state in ("approved", "rejected"))
        if not decided:
            return []
        last = decided[-1]
        if last.state == "rejected":
            return ["The last discount request on this estimate was rejected."]
        if not last.covers(self.discount_pct or 0.0):
            return [
                "The discount approved (%.2f%%) does not cover the %.2f%% on the estimate; "
                "request approval for the discount it carries."
                % (last.approved_pct, self.discount_pct or 0.0)
            ]
        return []

    def action_quote(self):
        for estimate in self:
            if estimate.state != "approved":
                raise UserError("Only an approved estimate can be quoted (one concept, one flow)")
            if estimate.quotation_state not in ("internal", "expired"):
                raise UserError(
                    "Estimate %s is already %s; revise it to quote a new version."
                    % (estimate.display_name, estimate.quotation_state)
                )
            blockers = estimate._quotation_discount_blockers()
            if blockers:
                raise UserError(" ".join(blockers))
            estimate._guarded().write(
                {"quotation_state": "quoted", "sent_at": fields.Datetime.now()}
            )
            publish(
                self.env,
                "quotation.sent",
                "fix.estimate",
                estimate.id,
                {
                    "version": estimate.version,
                    "grand_total": estimate.grand_total,
                    "valid_days": estimate.valid_days,
                },
            )

    def action_negotiate(self):
        """The customer came back with a counter: the quote stays live."""
        for estimate in self:
            if estimate.quotation_state != "quoted":
                raise UserError("Only a quoted quotation goes into negotiation")
            estimate._guarded().write({"quotation_state": "negotiating"})

    def action_accept(self):
        """Record the customer's acceptance, inside the validity window
        (BRU-QTE-03; A04 audit M36 eq_07: a quote sent 30 days ago on a
        15-day window was accepted)."""
        today = dhaka_today(self)
        for estimate in self:
            if estimate.quotation_state not in ("quoted", "negotiating"):
                raise UserError("Only a quoted quotation can be accepted")
            if estimate.state != "approved":
                raise UserError(
                    "Estimate %s is %s; only the approved estimate the customer was quoted "
                    "can be accepted." % (estimate.display_name, estimate.state)
                )
            valid_until = estimate._quotation_valid_until()
            if not valid_until or today > valid_until:
                raise UserError(
                    "This quotation was valid until %s (BRU-QTE-03): acceptance is "
                    "impossible after expiry. Re-issue it at current prices."
                    % (valid_until or "an unknown date")
                )
            estimate._guarded().write(
                {
                    "quotation_state": "accepted",
                    "accepted_at": fields.Datetime.now(),
                    "quotation_accepted_by": self.env.user.id,
                }
            )
            publish(
                self.env,
                "quotation.accepted",
                "fix.estimate",
                estimate.id,
                {
                    "version": estimate.version,
                    "grand_total": estimate.grand_total,
                },
            )

    def action_decline(self, reason=None):
        """BRU-QTE-16: a declined quotation records why. An accepted quote is
        a decision already taken (A04 audit eq_06: action_decline flipped an
        ACCEPTED quotation, with no reason)."""
        reason = (reason or "").strip()
        for estimate in self:
            if estimate.quotation_state not in ("quoted", "negotiating"):
                raise UserError(
                    "Only a live (quoted or negotiating) quotation can be declined; this one "
                    "is %s." % estimate.quotation_state
                )
            if not reason:
                raise UserError("Record why the customer declined (BRU-QTE-16).")
            estimate._guarded().write(
                {
                    "quotation_state": "declined",
                    "declined_at": fields.Datetime.now(),
                    "quotation_decline_reason": reason,
                }
            )

    @api.model
    def _cron_expire_quoted_estimates(self):
        """BRU-QTE-03/AUT-QTE-06: a quoted estimate past its window expires.
        Called by fix.quotation's expiry cron."""
        today = dhaka_today(self)
        live = self.sudo().search([("quotation_state", "in", ("quoted", "negotiating"))])
        stale = live.filtered(
            lambda e: e._quotation_valid_until() and e._quotation_valid_until() < today
        )
        for estimate in stale:
            estimate._guarded().write({"quotation_state": "expired"})
        return len(stale)

    @api.constrains("valid_days")
    def _check_validity(self):
        for estimate in self:
            if estimate.valid_days <= 0:
                raise UserError("The quotation validity window must be positive")


class FixDiscountApproval(models.Model):
    """T03 (P06-M06): discount governance — an agent-entered discount above
    the delegated authority requires approval BEFORE the quote is sent. A
    segregation-of-duties control attached to the unified estimate."""

    _name = "fix.discount.approval"
    _description = "Discount Approval"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]

    # A03 audit R7: a discount above the agent's 5% is approved from the
    # approver's M63 inbox (Request Approval), not by pressing Approve.
    _approval_domain = "discount"
    _approval_apply_method = "action_approve"
    _approval_routed = True

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    quotation_id = fields.Many2one(
        "fix.estimate", string="Quotation", required=True, ondelete="cascade"
    )
    discount_pct = fields.Float(string="Discount (%)", required=True)
    justification = fields.Text(required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
        required=True,
        tracking=True,
    )
    approved_by = fields.Many2one("res.users", readonly=True)
    approved_pct = fields.Float(
        string="Approved Discount (%)",
        readonly=True,
        copy=False,
        help="The discount the decision covered. A higher discount on the estimate is "
        "not covered by it (A04 audit M36-3).",
    )
    rejection_reason = fields.Char(readonly=True)
    # The band and tier come from the single M11 ladder (BRU-PRC-06); the
    # module's own 5% / 10% constants are retired (A04 build 2026-11-04).

    @api.depends("discount_pct", "quotation_id")
    def _compute_name(self):
        # A04 audit M36-13: the request displayed as "fix.discount.approval,541".
        for rec in self:
            rec.name = "%.2f%% discount on %s" % (
                rec.discount_pct or 0.0,
                rec.quotation_id.display_name or "an estimate",
            )

    def _fix_guarded_fields(self) -> set:
        # A 15% approval was set by writing state='approved' (A03 audit).
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by",
            "approved_pct",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(a.state != "pending" for a in self):
            locked |= {"discount_pct", "quotation_id", "justification"}
        return locked

    def _approval_pinned_fields(self) -> set:
        # The request approves a discount on ONE estimate.
        return super()._approval_pinned_fields() | {"quotation_id"}

    @api.model_create_multi
    def create(self, vals_list):
        Estimate = self.env["fix.estimate"].sudo()
        for vals in vals_list:
            # A04 audit M36-5 (da_10): a 2% request auto-approved on an estimate
            # carrying a 40% discount. A request covers at least the discount
            # the estimate already carries.
            estimate = Estimate.browse(vals.get("quotation_id")).exists()
            actual = estimate.discount_pct if estimate else 0.0
            if actual and actual > (vals.get("discount_pct") or 0.0):
                vals["discount_pct"] = round(actual, 2)
        records = super().create(vals_list)
        for rec in records:
            if rec._discount_tier() == "tier_0":
                # within the agent's own band of the ladder
                rec._guarded().write({"state": "approved", "approved_pct": rec.discount_pct})
        return records

    def write(self, vals):
        # A04 audit M36-3 (da_07/da_08): an 8% approval edited to 40%, and a 3%
        # auto-approval edited to 45%, still read approved. A decided request
        # is frozen; a new discount is a new request.
        watched = {"discount_pct", "quotation_id", "justification"} & set(vals)
        if watched and not self._fix_guard_open():
            decided = self.filtered(
                lambda a: a.state != "pending"
                and any(a._fix_guard_differs(n, vals[n], a[n]) for n in watched)
            )
            if decided:
                raise UserError(
                    "A decided discount request cannot change: it covers the %.2f%% it was "
                    "decided for. Raise a new request for a different discount."
                    % decided[0].approved_pct
                )
        return super().write(vals)

    def covers(self, pct: float) -> bool:
        """True when this request approves a discount of `pct` percent."""
        self.ensure_one()
        return self.state == "approved" and (pct or 0.0) <= (self.approved_pct or 0.0) + 1e-6

    def _discount_tier(self) -> str:
        """The DOFA tier the single ladder gives this discount."""
        self.ensure_one()
        Policy = self.env.get("fix.discount.policy")
        if Policy is not None and hasattr(Policy, "tier_for_discount"):
            return Policy.sudo().tier_for_discount(self.discount_pct, company=self.company_id)
        for bound, tier in SPEC_DISCOUNT_LADDER:
            if (self.discount_pct or 0.0) <= bound:
                return tier
        return SPEC_DISCOUNT_LADDER[-1][1]

    def _approval_needed(self) -> bool:
        return self.state == "pending" and self._discount_tier() != "tier_0"

    def _approval_amount(self) -> float:
        return self.discount_pct

    def _approval_tier(self):
        tier = self._discount_tier()
        return tier if tier in TIER_GROUP else False

    def _approval_group_xmlid(self):
        return TIER_GROUP.get(self._discount_tier())

    def _approval_on_rejected(self, comment):
        for approval in self.filtered(lambda a: a.state == "pending"):
            approval._guarded().write({"state": "rejected", "rejection_reason": comment})

    def action_approve(self):
        self._approval_assert_routed()
        for approval in self:
            if approval.state != "pending":
                raise UserError("Only a pending discount request can be approved")
            # The tier of the single ladder (BRU-PRC-06). It was "anyone" and
            # "base.group_system" (an IT admin role), with no segregation of
            # duties (A03 audit).
            tier = approval._discount_tier()
            needed = TIER_GROUP.get(tier)
            # A delegate decides with the absent approver's authority.
            if not needed or not approval._approval_authority_user().has_group(needed):
                raise UserError(
                    "A %.2f%% discount requires approval by %s (the discount ladder, "
                    "BRU-PRC-06)." % (approval.discount_pct, TIER_LABEL.get(tier, tier))
                )
            if approval.create_uid in approval._approval_acting_users():
                raise UserError(
                    "Segregation of duties: you requested this discount, so someone "
                    "else must approve it."
                )
            approval._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.user.id,
                    "approved_pct": approval.discount_pct,
                }
            )
            publish(
                self.env,
                "discount.approved",
                "fix.discount.approval",
                approval.id,
                {"pct": approval.discount_pct},
            )

    def action_reject(self, reason=None):
        """There was no way to refuse a discount request. Since R7 a rejection
        is an approver's decision, taken from their M63 inbox."""
        self._approval_assert_routed()
        if not (reason or "").strip():
            raise UserError("A rejected discount request needs its reason")
        for approval in self:
            if approval.state != "pending":
                raise UserError("Only a pending discount request can be rejected")
            approval._guarded().write({"state": "rejected", "rejection_reason": reason})
