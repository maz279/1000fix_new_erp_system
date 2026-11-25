# M35 capture audit, second pass (2026-11-19): what the spec says each
# sub-module page records, and the first pass did not give it.
#
# Spec: 03_Modules/B_.../M35_Marketing_Campaigns_and_Demand_Generation.md
#   §5 FR-MKT-001..040, §8.1 lifecycle, §9 BRU-MKT-05/06/08/09/10/11/13,
#   §10.1 fix.campaign.programme, fix.attribution.result, fix.content.asset,
#   fix.ab.test, fix.ad.placement, §11 AUT-MKT-01/06/07/08/09/11/12/14,
#   §6 T-07/T-09/T-10.
#
# The first pass (2026-11-14) gave every page a "+ New" for the list it
# shows. Read against the spec, the pages still could not record:
#   1 Planning & Approval: a campaign's type, objective and success measure
#     (FR-MKT-001/004), its programme (FR-MKT-005), the capacity check and the
#     Operations Director's override (FR-MKT-006, BRU-MKT-05) and an
#     emergency stop (FR-MKT-008, BRU-MKT-13). A forward calendar with
#     conflicts (FR-MKT-007) did not exist.
#   2 Audience: suppression of recent recipients, open complaints and credit
#     hold (FR-MKT-013, BRU-MKT-08); intersect logic (FR-MKT-010).
#   3 Journeys: priority between conflicting journeys (FR-MKT-020,
#     BRU-MKT-06); exit on conversion or complaint (FR-MKT-019, AUT-MKT-07/08);
#     a manual exit.
#   4 Content: the creative held only a file reference. No English or Bengali
#     copy (BRU-MKT-10), no expiry (BRU-MKT-09), no version (FR-MKT-024/028),
#     no SMS segment cost (T-10), no personalisation check (FR-MKT-026), no
#     tracked landing page (FR-MKT-029).
#   5 Experimentation: a winner was named without the figures, so nothing
#     showed it was significant (FR-MKT-031, entity field `significance`).
#   6 Budget & Attribution: no committed spend (FR-MKT-033), no 80/100%
#     budget alert (AUT-MKT-12), no measured result against the holdout
#     (FR-MKT-036/037, AUT-MKT-11, entity fix.attribution.result).
#   7 Portal Advertising: no position or page context; two ads could take the
#     same slot at the same time.
import math
import re
from datetime import timedelta
from urllib.parse import urlencode, urlsplit

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

# imported for their models: this file extends what they define
from . import fix_campaign_capture, fix_journey_runtime  # noqa: F401

CAPACITY_OVERRIDE = "cd_campaign.group_capacity_override"
CAPACITY_REQUIRED_PARAM = "cd_campaign.capacity_check_required"
SIGNIFICANCE_ALPHA_PARAM = "cd_campaign.experiment_alpha"
SIGNIFICANCE_ALPHA_DEFAULT = 0.05
CREATIVE_EXPIRY_NOTICE_DAYS = 7

CAMPAIGN_TYPES = [
    ("acquisition", "Acquisition"),
    ("retention", "Retention"),
    ("win_back", "Win-back"),
    ("cross_sell", "Cross-sell"),
    ("upsell", "Upsell"),
    ("seasonal", "Seasonal"),
    ("event", "Event"),
    ("referral", "Referral"),
    ("co_marketing", "Brand co-marketing"),
    ("reactivation", "Reactivation"),
]

SUCCESS_MEASURES = [
    ("responses", "Responses"),
    ("leads", "Leads generated"),
    ("conversions", "Conversions"),
    ("revenue", "Revenue (BDT)"),
    ("reach", "Reach"),
]

# Open = the complaint is not yet resolved (BRU-MKT-08).
COMPLAINT_RESOLVED = ("accepted", "closed", "rejected")

NEW_AUDIENCE_FIELDS = frozenset(
    {
        "intersect_segment_ids",
        "suppress_recent_days",
        "suppress_open_complaints",
        "suppress_credit_hold",
    }
)

# FR-MKT-026: the variables a message may personalise with. M27 renders them;
# an unknown one would reach a customer as "{foo}".
ALLOWED_VARIABLES = ("name", "device", "service", "branch", "expiry_date", "points", "voucher")
_PLACEHOLDER = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
_BENGALI = re.compile(r"[ঀ-৿]")
# GSM 03.38 basic set: anything outside it sends as UCS-2 (70 chars a segment).
_GSM7 = set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
    "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà^{}\\[~]|€"
)

CREATIVE_TEXT_FIELDS = frozenset(
    {"subject_en", "subject_bn", "body_en", "body_bn", "reference_bn", "expires_on"}
)


def sms_segments(text):
    """How many SMS segments a body costs (spec T-10)."""
    text = text or ""
    if not text:
        return 0
    if set(text) <= _GSM7:
        single, multi = 160, 153
    else:
        single, multi = 70, 67
    return 1 if len(text) <= single else math.ceil(len(text) / multi)


def two_proportion_p_value(n_a, x_a, n_b, x_b):
    """Two-sided p-value of a two-proportion z-test (FR-MKT-031)."""
    if not n_a or not n_b:
        return 1.0
    p_pool = (x_a + x_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return 1.0
    z = abs(x_a / n_a - x_b / n_b) / se
    return math.erfc(z / math.sqrt(2))


# ---------------------------------------------------------------------------
# 1 Planning & Approval
# ---------------------------------------------------------------------------
class FixCampaignProgramme(models.Model):
    """FR-MKT-005 / FR-MKT-032: campaigns grouped for budget and roll-up."""

    _name = "fix.campaign.programme"
    _description = "Campaign Programme"
    _inherit = ["mail.thread"]
    _order = "date_from desc, code"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True)
    date_from = fields.Date(string="Period From", required=True)
    date_to = fields.Date(string="Period To", required=True)
    owner_id = fields.Many2one(
        "res.users", string="Owner", required=True, default=lambda self: self.env.user
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
    )
    budget = fields.Monetary(
        string="Programme Budget",
        currency_field="currency_id",
        tracking=True,
        help="The campaigns' budgets together may not exceed it. Zero: not capped.",
    )
    campaign_ids = fields.One2many("fix.campaign", "programme_id", string="Campaigns")
    campaign_count = fields.Integer(compute="_compute_rollup")
    planned_budget = fields.Monetary(
        string="Campaign Budgets", currency_field="currency_id", compute="_compute_rollup"
    )
    actual_spend = fields.Monetary(
        string="Actual Spend", currency_field="currency_id", compute="_compute_rollup"
    )
    budget_unallocated = fields.Monetary(
        string="Not Yet Allocated", currency_field="currency_id", compute="_compute_rollup"
    )

    _code_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A programme code is used once per company."
    )

    @api.constrains("date_from", "date_to")
    def _check_period(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError("A programme ends after it starts.")

    @api.constrains("budget")
    def _check_budget(self):
        for rec in self:
            if (rec.budget or 0.0) < 0:
                raise ValidationError("A programme budget is not negative.")
            rec._assert_budget_covers()

    def _assert_budget_covers(self):
        for rec in self:
            planned = sum(rec.campaign_ids.mapped("budget"))
            if rec.budget and planned > rec.budget + 0.005:
                raise ValidationError(
                    "The campaigns of %s plan BDT %.2f against a programme budget of "
                    "BDT %.2f (FR-MKT-032)." % (rec.name, planned, rec.budget)
                )

    @api.depends("campaign_ids.budget", "budget")
    def _compute_rollup(self):
        for rec in self:
            rec.campaign_count = len(rec.campaign_ids)
            rec.planned_budget = sum(rec.campaign_ids.mapped("budget"))
            rec.actual_spend = sum(rec.campaign_ids.mapped("actual_spend"))
            rec.budget_unallocated = (rec.budget or 0.0) - rec.planned_budget


class FixCampaignCapacityCheck(models.Model):
    """FR-MKT-006 / BRU-MKT-05: projected demand against operational capacity.

    The spec reads capacity from an M02 projection (T-08). The estate has no
    such projection, so the planner records the figure and says where it comes
    from; the check, the block and the override are what this record enforces.
    """

    _name = "fix.campaign.capacity.check"
    _description = "Campaign Capacity Check"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "id desc"
    _rec_name = "display_label"

    campaign_id = fields.Many2one(
        "fix.campaign", required=True, ondelete="cascade", index=True, string="Campaign"
    )
    company_id = fields.Many2one(related="campaign_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="campaign_id.operating_unit_id", store=True)
    reach_basis = fields.Integer(
        string="Estimated Reach Used",
        readonly=True,
        help="The campaign's post-suppression reach when the check was made.",
    )
    expected_response_pct = fields.Float(
        string="Expected Response (%)",
        required=True,
        digits=(16, 2),
        help="Share of the reached audience expected to book work.",
    )
    projected_jobs = fields.Integer(string="Projected Jobs", compute="_compute_result", store=True)
    available_capacity = fields.Integer(
        string="Capacity Available (jobs)",
        required=True,
        help="Jobs the branches can take in the campaign window.",
    )
    capacity_source = fields.Char(
        string="Where The Capacity Figure Comes From",
        required=True,
        help="For example the M02 roster for the window, or the branch plan.",
    )
    result = fields.Selection(
        [("sufficient", "Capacity sufficient"), ("insufficient", "Capacity insufficient")],
        compute="_compute_result",
        store=True,
    )
    state = fields.Selection(
        [("checked", "Checked"), ("overridden", "Overridden")],
        default="checked",
        required=True,
        readonly=True,
    )
    override_reason = fields.Char(readonly=True)
    override_by_id = fields.Many2one("res.users", string="Overridden By", readonly=True)
    override_at = fields.Datetime(string="Overridden At", readonly=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "reach_basis",
            "state",
            "override_reason",
            "override_by_id",
            "override_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            # a check is evidence: a different figure is a new check
            locked |= {
                "campaign_id",
                "expected_response_pct",
                "available_capacity",
                "capacity_source",
            }
        return locked

    @api.depends("campaign_id.name", "result", "state")
    def _compute_display_label(self):
        labels = dict(self._fields["result"].selection)
        for rec in self:
            rec.display_label = "%s · %s%s" % (
                rec.campaign_id.name or "?",
                labels.get(rec.result, ""),
                " (overridden)" if rec.state == "overridden" else "",
            )

    @api.depends("reach_basis", "expected_response_pct", "available_capacity")
    def _compute_result(self):
        for rec in self:
            rec.projected_jobs = math.ceil(
                (rec.reach_basis or 0) * (rec.expected_response_pct or 0) / 100.0
            )
            rec.result = (
                "sufficient"
                if rec.projected_jobs <= (rec.available_capacity or 0)
                else "insufficient"
            )

    @api.constrains("expected_response_pct", "available_capacity")
    def _check_figures(self):
        for rec in self:
            if not 0 < (rec.expected_response_pct or 0) <= 100:
                raise ValidationError("The expected response is above 0% and at most 100%.")
            if (rec.available_capacity or 0) < 0:
                raise ValidationError("Capacity is not negative.")

    @api.model_create_multi
    def create(self, vals_list):
        Campaign = self.env["fix.campaign"]
        for vals in vals_list:
            campaign = Campaign.browse(vals.get("campaign_id"))
            if not campaign.exists():
                raise UserError("Name the campaign being checked.")
            if campaign.state != "draft":
                raise UserError("Capacity is checked before launch, on a draft campaign.")
            if not campaign.estimated_at:
                raise UserError(
                    "Estimate %s's audience first: capacity is checked against the "
                    "post-suppression reach (spec §8.1)." % campaign.name
                )
            vals["reach_basis"] = campaign.estimated_reach
        recs = super(FixCampaignCapacityCheck, self._guarded()).create(vals_list)
        for rec in recs:
            rec.campaign_id.message_post(
                body="Capacity check: %d projected jobs against %d available (%s): %s."
                % (
                    rec.projected_jobs,
                    rec.available_capacity,
                    rec.capacity_source,
                    dict(rec._fields["result"].selection)[rec.result],
                )
            )
        return recs

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {
                "campaign_id",
                "expected_response_pct",
                "available_capacity",
                "capacity_source",
            }
            for rec in self:
                if any(
                    n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in frozen & set(vals)
                ):
                    raise UserError("A capacity check is not edited: record a new check.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A capacity check is evidence and is kept.")
        return super().unlink()

    def action_override(self, reason=None):
        """BRU-MKT-05 (class A): the Operations Director lets it launch anyway."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the campaign may launch beyond capacity.")
        if not (self.env.su or self.env.user.has_group(CAPACITY_OVERRIDE)):
            raise UserError(
                "Only the Operations Director (Capacity Override) overrides a capacity check."
            )
        for rec in self:
            if rec.result != "insufficient" or rec.state != "checked":
                raise UserError("Only an insufficient check that stands is overridden.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    "Segregation of duties: the person who made the check cannot override it."
                )
            rec._guarded().write(
                {
                    "state": "overridden",
                    "override_reason": reason,
                    "override_by_id": self.env.user.id,
                    "override_at": fields.Datetime.now(),
                }
            )
            rec.campaign_id.message_post(
                body="Capacity check overridden by %s: %s" % (self.env.user.name, reason)
            )
        return True


class FixCampaignPassTwo(models.Model):
    """The campaign's definition, suppression, capacity, stop and measurement."""

    _inherit = "fix.campaign"

    state = fields.Selection(
        selection_add=[("halted", "Halted (emergency stop)")],
        ondelete={"halted": "set default"},
    )
    # FR-MKT-001 / 004 / 005
    campaign_type = fields.Selection(CAMPAIGN_TYPES, string="Campaign Type", tracking=True)
    objective = fields.Text(string="Objective")
    success_measure = fields.Selection(SUCCESS_MEASURES, string="Success Measure")
    success_target = fields.Float(string="Success Target", digits=(16, 2))
    programme_id = fields.Many2one(
        "fix.campaign.programme", string="Programme", index=True, ondelete="restrict"
    )
    # FR-MKT-029
    landing_page_url = fields.Char(string="Landing Page")
    tracked_url = fields.Char(string="Tracked Link", compute="_compute_tracked_url")
    # FR-MKT-010 / 013, BRU-MKT-08
    intersect_segment_ids = fields.Many2many(
        "fix.segment",
        "fix_campaign_segment_intersect_rel",
        "campaign_id",
        "segment_id",
        string="Must Also Be In",
        help="Only parties who are also current members of every one of these "
        "segments are kept (intersect).",
    )
    suppress_recent_days = fields.Integer(
        string="Suppress Recent Recipients (days)",
        default=0,
        help="Leave out anyone who received another campaign that started in the "
        "last N days. 0: off.",
    )
    suppress_open_complaints = fields.Boolean(
        string="Suppress Open Complaints",
        default=True,
        help="BRU-MKT-08: a party with an unresolved complaint receives no promotion.",
    )
    suppress_credit_hold = fields.Boolean(
        string="Suppress Credit Hold",
        default=False,
        help="Leave out customers on credit hold.",
    )
    intersect_segment_names = fields.Char(
        string="Segments Intersected", compute="_compute_intersect_names"
    )
    # FR-MKT-006
    capacity_check_ids = fields.One2many(
        "fix.campaign.capacity.check", "campaign_id", string="Capacity Checks"
    )
    capacity_check_result = fields.Selection(
        [
            ("none", "Not checked"),
            ("sufficient", "Sufficient"),
            ("insufficient", "Insufficient: launch blocked"),
            ("overridden", "Insufficient, overridden"),
        ],
        string="Capacity",
        compute="_compute_capacity_check_result",
    )
    # FR-MKT-007
    calendar_conflicts = fields.Char(
        string="Calendar Conflicts", compute="_compute_calendar_conflicts"
    )
    # FR-MKT-008, BRU-MKT-13
    halt_reason = fields.Char(string="Why It Was Stopped", readonly=True, copy=False)
    halted_by_id = fields.Many2one("res.users", string="Stopped By", readonly=True, copy=False)
    halted_at = fields.Datetime(string="Stopped At", readonly=True, copy=False)
    halt_cancelled_count = fields.Integer(
        string="Queued Messages Cancelled", readonly=True, copy=False
    )
    # FR-MKT-033, AUT-MKT-12
    committed_spend = fields.Monetary(
        string="Committed (not yet invoiced)",
        currency_field="currency_id",
        compute="_compute_committed",
    )
    budget_available = fields.Monetary(
        string="Budget Available",
        currency_field="currency_id",
        compute="_compute_committed",
        help="Budget less actual and committed spend.",
    )
    budget_alert_80_at = fields.Datetime(readonly=True, copy=False)
    # FR-MKT-036 / 037
    result_ids = fields.One2many("fix.attribution.result", "campaign_id", string="Measured Results")
    measured_at = fields.Datetime(string="Last Measured", compute="_compute_measured", store=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "halt_reason",
            "halted_by_id",
            "halted_at",
            "halt_cancelled_count",
            "budget_alert_80_at",
        }

    @api.depends("intersect_segment_ids")
    def _compute_intersect_names(self):
        for rec in self:
            rec.intersect_segment_names = ", ".join(rec.intersect_segment_ids.mapped("name"))

    @api.depends("landing_page_url", "utm_source", "utm_medium", "utm_campaign")
    def _compute_tracked_url(self):
        for rec in self:
            url = (rec.landing_page_url or "").strip()
            if not url:
                rec.tracked_url = False
                continue
            query = urlencode(
                {
                    "utm_source": rec.utm_source or "",
                    "utm_medium": rec.utm_medium or "",
                    "utm_campaign": rec.utm_campaign or "",
                }
            )
            rec.tracked_url = "%s%s%s" % (url, "&" if "?" in url else "?", query)

    @api.constrains("landing_page_url")
    def _check_landing_page(self):
        for rec in self:
            url = (rec.landing_page_url or "").strip()
            if url and (urlsplit(url).scheme != "https" or not urlsplit(url).netloc):
                raise ValidationError("A landing page is a full https:// address.")

    @api.constrains("suppress_recent_days")
    def _check_recent_days(self):
        for rec in self:
            if not 0 <= (rec.suppress_recent_days or 0) <= 365:
                raise ValidationError("Recent-recipient suppression is 0 to 365 days.")

    @api.constrains("programme_id", "budget", "start_date", "end_date")
    def _check_programme(self):
        for rec in self.filtered("programme_id"):
            prog = rec.programme_id
            if rec.start_date and rec.start_date < prog.date_from:
                raise ValidationError(
                    "%s starts before its programme %s does." % (rec.name, prog.name)
                )
            if rec.end_date and rec.end_date > prog.date_to:
                raise ValidationError(
                    "%s ends after its programme %s does." % (rec.name, prog.name)
                )
            prog._assert_budget_covers()

    @api.constrains("success_target")
    def _check_success_target(self):
        for rec in self:
            if (rec.success_target or 0.0) < 0:
                raise ValidationError("A success target is not negative.")

    def _compute_capacity_check_result(self):
        for rec in self:
            last = rec.capacity_check_ids.sorted("id", reverse=True)[:1]
            if not last:
                rec.capacity_check_result = "none"
            elif last.state == "overridden":
                rec.capacity_check_result = "overridden"
            else:
                rec.capacity_check_result = last.result

    def _compute_calendar_conflicts(self):
        """FR-MKT-007: another live or planned campaign on the same channel,
        in an overlapping window, aimed at a shared segment (or at everyone)."""
        live = ("draft", "running", "paused")
        for rec in self:
            if rec.state not in live or not rec.start_date or not rec.end_date:
                rec.calendar_conflicts = False
                continue
            others = self.sudo().search(
                [
                    ("id", "!=", rec.id or 0),
                    ("state", "in", live),
                    ("channel", "=", rec.channel),
                    ("start_date", "<=", rec.end_date),
                    ("end_date", ">=", rec.start_date),
                ]
            )
            mine = rec.segment_ids
            clash = others.filtered(
                lambda o, mine=mine, everyone=rec.target_audience_type != "segments": everyone
                or o.target_audience_type != "segments"
                or bool(o.segment_ids & mine)
            )
            rec.calendar_conflicts = ", ".join(clash.mapped("name")[:5]) or False

    def _compute_committed(self):
        for rec in self:
            committed = rec._committed_spend()
            rec.committed_spend = committed
            rec.budget_available = (rec.budget or 0.0) - rec.actual_spend - committed

    def _compute_measured(self):
        for rec in self:
            rec.measured_at = max(rec.result_ids.mapped("measured_at"), default=False)

    # ------------------------------------------------------------------
    # Audience: intersect and suppression
    # ------------------------------------------------------------------
    def write(self, vals):
        touched = NEW_AUDIENCE_FIELDS & set(vals)
        if touched and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in touched):
                    raise UserError("The audience of %s is fixed once it has launched." % rec.name)
        res = super().write(vals)
        if touched:
            stale = self.filtered(lambda r: r.state == "draft" and r.estimated_at)
            if stale:
                stale._guarded().write(
                    {"estimated_reach": 0, "estimated_at": False, "estimate_breakdown": False}
                )
        return res

    def _suppressed(self):
        """FR-MKT-013: who this campaign leaves out, by reason (party ids)."""
        self.ensure_one()
        out = {}
        if self.suppress_recent_days:
            since = fields.Date.context_today(self) - timedelta(days=self.suppress_recent_days)
            recent = (
                self.sudo()
                .search(
                    [
                        ("id", "!=", self.id or 0),
                        ("start_date", ">=", since),
                        ("state", "in", ("running", "paused", "completed", "halted")),
                    ]
                )
                .mapped("recipient_ids")
            )
            out["recent"] = set(recent.ids)
        if self.suppress_open_complaints and "fix.complaint" in self.env:
            rows = (
                self.env["fix.complaint"].sudo().search([("state", "not in", COMPLAINT_RESOLVED)])
            )
            out["complaint"] = set(rows.mapped("customer_id").ids)
        if self.suppress_credit_hold and "fix.credit.profile" in self.env:
            rows = self.env["fix.credit.profile"].sudo().search([("credit_hold", "=", True)])
            out["credit_hold"] = set(rows.mapped("customer_id").ids)
        return out

    def _audience_domain(self):
        domain = super()._audience_domain()
        for seg in self.intersect_segment_ids:
            ids = self._segment_members(seg)
            domain = [*domain, ("id", "in", sorted(ids) or [0])]
        if not self.env.context.get("m35_unsuppressed"):
            gone = set().union(set(), *self._suppressed().values())
            if gone:
                domain = [*domain, ("id", "not in", sorted(gone))]
        return domain

    def action_estimate_audience(self):
        res = super().action_estimate_audience()
        labels = {
            "recent": "recent recipients",
            "complaint": "open complaints",
            "credit_hold": "credit hold",
        }
        Partner = self.env["res.partner"]
        for rec in self:
            base = set(
                Partner.search(rec.with_context(m35_unsuppressed=True)._audience_domain()).ids
            )
            parts = []
            for key, ids in rec._suppressed().items():
                hit = len(base & ids)
                if hit:
                    parts.append("%d %s" % (hit, labels[key]))
            if parts:
                rec._guarded().write(
                    {
                        "estimate_breakdown": "Suppressed first: %s. Then %s"
                        % (", ".join(parts), rec.estimate_breakdown or "")
                    }
                )
        return res

    # ------------------------------------------------------------------
    # Launch gates: capacity, expired content
    # ------------------------------------------------------------------
    def _assert_capacity(self):
        """BRU-MKT-05: an insufficient check blocks launch until overridden."""
        self.ensure_one()
        result = self.capacity_check_result
        required = self.env["ir.config_parameter"].sudo().get_param(CAPACITY_REQUIRED_PARAM, "0")
        if result == "none" and required in ("1", "True", "true"):
            raise UserError("Launch blocked: %s has no capacity check (FR-MKT-006)." % self.name)
        if result == "insufficient":
            raise UserError(
                "Launch blocked: the projected demand of %s exceeds capacity. Reschedule, "
                "narrow the audience and check again, or have the Operations Director "
                "override the check (BRU-MKT-05)." % self.name
            )

    def action_launch(self):
        for rec in self:
            if rec.state == "draft":
                rec._assert_capacity()
        return super().action_launch()

    def _assert_creatives_approved(self):
        super()._assert_creatives_approved()
        expired = self.creative_ids.filtered(lambda c: c.state != "retired" and c.is_expired)
        if expired:
            raise UserError(
                "Blocked: creative %s has expired and cannot be used by a live campaign "
                "(BRU-MKT-09). Retire it or approve a new version."
                % ", ".join(expired.mapped("name"))
            )

    # ------------------------------------------------------------------
    # FR-MKT-008 / BRU-MKT-13 / T-07: emergency stop
    # ------------------------------------------------------------------
    def action_emergency_stop(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the campaign is stopped.")
        for rec in self:
            if rec.state not in ("running", "paused"):
                raise UserError("Only a running or paused campaign is stopped.")
            journeys = rec.journey_ids.filtered(lambda j: j.state == "active")
            journeys._pause_for_campaign()
            rec.journey_ids._guarded().write({"paused_by_campaign": False})
            members = (
                self.env["fix.campaign.journey.member"]
                .sudo()
                .search(
                    [
                        ("journey_id", "in", rec.journey_ids.ids),
                        ("state", "in", ("active", "suppressed")),
                    ]
                )
            )
            members.write(
                {
                    "state": "exited",
                    "exit_reason": "Campaign halted: %s" % reason,
                    "exited_at": fields.Datetime.now(),
                    "next_action_at": False,
                }
            )
            all_members = (
                self.env["fix.campaign.journey.member"]
                .sudo()
                .search([("journey_id", "in", rec.journey_ids.ids)])
            )
            queued = (
                self.env["fix.notif.delivery"]
                .sudo()
                .search(
                    [
                        ("state", "=", "queued"),
                        "|",
                        "&",
                        ("source_model", "=", "fix.campaign"),
                        ("source_id", "=", rec.id),
                        "&",
                        ("source_model", "=", "fix.campaign.journey.member"),
                        ("source_id", "in", all_members.ids or [0]),
                    ]
                )
            )
            queued.action_cancel("campaign %s halted: %s" % (rec.name, reason))
            rec._guarded().write(
                {
                    "state": "halted",
                    "halt_reason": reason,
                    "halted_by_id": self.env.user.id,
                    "halted_at": fields.Datetime.now(),
                    "halt_cancelled_count": len(queued),
                }
            )
            rec.message_post(
                body="EMERGENCY STOP by %s: %s. %d queued message(s) cancelled, %d journey "
                "member(s) exited." % (self.env.user.name, reason, len(queued), len(members))
            )
        return True

    def action_resume(self):
        if self.filtered(lambda r: r.state == "halted"):
            raise UserError("A halted campaign does not resume: plan a new campaign.")
        return super().action_resume()

    # ------------------------------------------------------------------
    # FR-MKT-033 / AUT-MKT-12: committed spend and budget alerts
    # ------------------------------------------------------------------
    def _committed_spend(self) -> float:
        if not self.id:
            return 0.0
        rows = (
            self.env["fix.campaign.spend"]
            .sudo()
            .search(
                [
                    ("campaign_id", "=", self.id),
                    ("state", "=", "recorded"),
                    ("stage", "=", "committed"),
                ]
            )
        )
        return sum(rows.mapped("amount"))

    def _recorded_spend(self) -> float:
        # actual spend: a commitment is not spent until it is invoiced
        return super()._recorded_spend() - self._committed_spend()

    def _budget_alerts(self):
        """AUT-MKT-12: tell the owner at 80%; pause the campaign at 100%."""
        for rec in self:
            if not rec.budget:
                continue
            used = (rec._recorded_spend() + rec._committed_spend()) / rec.budget * 100.0
            if used >= 80.0 and not rec.budget_alert_80_at:
                rec._guarded().write({"budget_alert_80_at": fields.Datetime.now()})
                rec.message_post(
                    body="Budget alert: %.1f%% of the approved budget is spent or committed."
                    % used,
                    partner_ids=rec.create_uid.partner_id.ids,
                )
            if used >= 100.0 - 1e-6 and rec.state == "running":
                rec.action_pause()
                rec.message_post(
                    body="Paused: the approved budget is fully spent or committed. Raise the "
                    "budget and have it approved again to resume (AUT-MKT-12)."
                )

    # ------------------------------------------------------------------
    # FR-MKT-036 / 037, AUT-MKT-11: measure against the holdout
    # ------------------------------------------------------------------
    def action_measure(self):
        Result = self.env["fix.attribution.result"].sudo()
        for rec in self:
            if rec.state not in ("completed", "halted"):
                raise UserError("Measure a campaign once it has completed or been stopped.")
            Result._measure(rec)
        return True

    @api.model
    def cron_retire_expired_creatives(self):
        return self.env["fix.campaign.creative"].sudo()._cron_expiry()


# ---------------------------------------------------------------------------
# 3 Journeys
# ---------------------------------------------------------------------------
class FixCampaignJourneyPriority(models.Model):
    """FR-MKT-019 / 020, BRU-MKT-06/07/08: conflict priority and exits."""

    _inherit = "fix.campaign.journey"

    priority = fields.Integer(
        string="Priority (1 = highest)",
        default=5,
        help="Between journeys of the same conflict group, the higher priority wins.",
    )
    conflict_group = fields.Char(
        string="Conflict Group",
        help="Journeys sharing a group never message one party at the same time "
        "(BRU-MKT-06). Empty: no conflict.",
    )
    exit_on_complaint = fields.Boolean(
        string="Exit On Complaint", default=True, help="BRU-MKT-08 / AUT-MKT-07."
    )
    exit_on_conversion = fields.Boolean(
        string="Exit On Conversion", default=True, help="AUT-MKT-08."
    )

    @api.constrains("priority")
    def _check_priority(self):
        for rec in self:
            if not 1 <= (rec.priority or 0) <= 99:
                raise ValidationError("A journey's priority is 1 (highest) to 99.")

    def _enrol(self, partners, source="launch", source_event_id=None):
        self.ensure_one()
        gone = set().union(set(), *self.campaign_id._suppressed().values())
        # BRU-MKT-14: the holdout is kept out of every journey of the campaign
        gone |= set(self.campaign_id.holdout_partner_ids.ids)
        partners = partners.filtered(lambda p: p.id not in gone)
        if self.conflict_group and partners:
            Member = self.env["fix.campaign.journey.member"].sudo()
            rivals = Member.search(
                [
                    ("partner_id", "in", partners.ids),
                    ("state", "=", "active"),
                    ("journey_id", "!=", self.id),
                    ("journey_id.conflict_group", "=", self.conflict_group),
                    ("journey_id.state", "=", "active"),
                ]
            )
            blocked = rivals.filtered(lambda m: m.journey_id.priority <= self.priority)
            outranked = rivals - blocked
            if outranked:
                outranked.write(
                    {
                        "state": "exited",
                        "exit_reason": "Entered higher-priority journey %s (BRU-MKT-06)."
                        % self.name,
                        "exited_at": fields.Datetime.now(),
                        "next_action_at": False,
                    }
                )
            skip = set(blocked.mapped("partner_id").ids)
            if skip:
                self.campaign_id.message_post(
                    body="%d party/parties not entered into %s: already in a journey of "
                    "equal or higher priority in group %s."
                    % (len(skip), self.name, self.conflict_group)
                )
            partners = partners.filtered(lambda p: p.id not in skip)
        return super()._enrol(partners, source=source, source_event_id=source_event_id)

    def _runtime_member_still_eligible(self, member):
        eligible, reason = super()._runtime_member_still_eligible(member)
        if not eligible:
            return eligible, reason
        party = member.partner_id
        if self.exit_on_complaint and party and "fix.complaint" in self.env:
            open_complaint = (
                self.env["fix.complaint"]
                .sudo()
                .search_count(
                    [("customer_id", "=", party.id), ("state", "not in", COMPLAINT_RESOLVED)]
                )
            )
            if open_complaint:
                return False, "Party raised a complaint that is not resolved (BRU-MKT-08)."
        if self.exit_on_conversion and party:
            converted = (
                self.env["fix.campaign.touch"]
                .sudo()
                .search_count(
                    [
                        ("partner_id", "=", party.id),
                        ("campaign_id", "=", self.campaign_id.id),
                        ("touch_type", "=", "conversion"),
                        ("occurred_at", ">=", member.entered_at),
                    ]
                )
            )
            if converted:
                return False, "Party converted (AUT-MKT-08)."
        return True, ""


class FixCampaignJourneyMemberExit(models.Model):
    _inherit = "fix.campaign.journey.member"

    def action_exit_member(self, reason=None):
        """FR-MKT-019: take a party out of a journey for good, with the reason."""
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the party leaves the journey.")
        for rec in self:
            if rec.state not in ("active", "suppressed"):
                raise UserError("%s has already left the journey." % rec.partner_id.name)
        self.sudo().write(
            {
                "state": "exited",
                "exit_reason": "Exited by %s: %s" % (self.env.user.name, reason),
                "exited_at": fields.Datetime.now(),
                "next_action_at": False,
            }
        )
        return True


# ---------------------------------------------------------------------------
# 4 Content
# ---------------------------------------------------------------------------
class FixCampaignCreativeContent(models.Model):
    """FR-MKT-024..028, BRU-MKT-09/10, T-09/T-10, AUT-MKT-14."""

    _inherit = "fix.campaign.creative"

    subject_en = fields.Char(string="Subject / Headline (English)")
    subject_bn = fields.Char(string="Subject / Headline (Bengali)")
    body_en = fields.Text(string="Copy (English)")
    body_bn = fields.Text(string="Copy (Bengali)")
    reference_bn = fields.Char(
        string="Bengali Version Reference",
        help="The Bengali version of an image, video or landing page (BRU-MKT-10).",
    )
    expires_on = fields.Date(
        string="Expires On", help="After this date no live campaign may use it (BRU-MKT-09)."
    )
    is_expired = fields.Boolean(string="Expired", compute="_compute_is_expired")
    expiry_notified = fields.Boolean(readonly=True, copy=False)
    version = fields.Integer(
        string="Approved Version",
        readonly=True,
        copy=False,
        default=0,
        help="Counts approvals: each approved edit is a new version (FR-MKT-028).",
    )
    placeholders = fields.Char(string="Personalisation Used", compute="_compute_content_checks")
    sms_segments_en = fields.Integer(
        string="SMS Segments (English)", compute="_compute_content_checks"
    )
    sms_segments_bn = fields.Integer(
        string="SMS Segments (Bengali)", compute="_compute_content_checks"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"version", "expiry_notified"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self._content_frozen():
            locked |= CREATIVE_TEXT_FIELDS
        return locked

    def write(self, vals):
        if not self.env.su and CREATIVE_TEXT_FIELDS & set(vals):
            frozen = self.filtered(lambda r: r._content_frozen())
            for rec in frozen:
                if any(
                    rec._fix_guard_differs(n, vals[n], rec[n])
                    for n in CREATIVE_TEXT_FIELDS & set(vals)
                ):
                    raise UserError(
                        "Creative '%s' is approved or awaiting approval. Withdraw it before "
                        "editing its copy or expiry." % rec.name
                    )
        return super().write(vals)

    def _compute_is_expired(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_expired = bool(rec.expires_on and rec.expires_on < today)

    @api.depends("subject_en", "subject_bn", "body_en", "body_bn")
    def _compute_content_checks(self):
        for rec in self:
            found = set()
            for text in (rec.subject_en, rec.subject_bn, rec.body_en, rec.body_bn):
                found |= set(_PLACEHOLDER.findall(text or ""))
            rec.placeholders = ", ".join("{%s}" % p for p in sorted(found)) or False
            rec.sms_segments_en = sms_segments(rec.body_en)
            rec.sms_segments_bn = sms_segments(rec.body_bn)

    def _assert_publishable(self):
        """What the approver must be able to see before approving it."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.asset_type == "copy":
                if not (rec.body_en or "").strip() or not (rec.body_bn or "").strip():
                    raise UserError(
                        "Creative '%s' needs its copy in both English and Bengali before "
                        "approval (BRU-MKT-10)." % rec.name
                    )
            elif not (rec.reference_bn or "").strip():
                raise UserError(
                    "Creative '%s' needs its Bengali version as well as the English one "
                    "before approval (BRU-MKT-10)." % rec.name
                )
            bn_text = " ".join(filter(None, [rec.subject_bn, rec.body_bn]))
            if bn_text and not _BENGALI.search(bn_text):
                raise UserError(
                    "The Bengali copy of '%s' contains no Bengali script: check it renders "
                    "as Bengali (T-10)." % rec.name
                )
            en = set(_PLACEHOLDER.findall("%s %s" % (rec.subject_en or "", rec.body_en or "")))
            bn = set(_PLACEHOLDER.findall("%s %s" % (rec.subject_bn or "", rec.body_bn or "")))
            unknown = (en | bn) - set(ALLOWED_VARIABLES)
            if unknown:
                raise UserError(
                    "Creative '%s' uses %s, which the message service cannot fill. Use: %s "
                    "(FR-MKT-026)."
                    % (
                        rec.name,
                        ", ".join("{%s}" % u for u in sorted(unknown)),
                        ", ".join("{%s}" % a for a in ALLOWED_VARIABLES),
                    )
                )
            if en != bn:
                raise UserError(
                    "The English and Bengali copy of '%s' personalise differently: both must "
                    "use the same variables." % rec.name
                )
            if not rec.expires_on:
                raise UserError(
                    "Give creative '%s' an expiry date: content is approved for a period "
                    "(FR-MKT-024)." % rec.name
                )
            if rec.expires_on < today:
                raise UserError("Creative '%s' has already expired." % rec.name)

    def action_request_approval(self, justification=None):
        self.filtered(lambda r: r.state == "draft")._assert_publishable()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        # who may approve is decided before what is approved: pressed outside
        # the approver's inbox, the routing refusal answers first (a content
        # error told an unauthorised user what to fix to get it through)
        for rec in self:
            rec._approval_assert_routed()
        self._assert_publishable()
        res = super().action_approve()
        for rec in self:
            rec._guarded().write({"version": (rec.version or 0) + 1, "expiry_notified": False})
        return res

    def _cron_expiry(self):
        """AUT-MKT-14: warn the owner a week ahead; retire it when it expires."""
        today = fields.Date.context_today(self)
        soon = self.search(
            [
                ("state", "=", "approved"),
                ("expires_on", "!=", False),
                ("expires_on", ">=", today),
                ("expires_on", "<=", today + timedelta(days=CREATIVE_EXPIRY_NOTICE_DAYS)),
                ("expiry_notified", "=", False),
            ]
        )
        for rec in soon:
            rec.message_post(
                body="Creative '%s' expires on %s." % (rec.name, rec.expires_on),
                partner_ids=rec.create_uid.partner_id.ids,
            )
            rec._guarded().write({"expiry_notified": True})
        expired = self.search([("state", "in", ("draft", "approved")), ("expires_on", "<", today)])
        for rec in expired:
            rec.action_retire()
            rec.message_post(
                body="Retired: the creative expired on %s (BRU-MKT-09)." % rec.expires_on
            )
        return {"notified": len(soon), "retired": len(expired)}


# ---------------------------------------------------------------------------
# 5 Experimentation
# ---------------------------------------------------------------------------
class FixCampaignExperimentResult(models.Model):
    """FR-MKT-031: the winner is declared on the figures, at a stated significance."""

    _inherit = "fix.campaign.experiment"

    a_sample = fields.Integer(string="Variant A: Reached", readonly=True, copy=False)
    a_conversions = fields.Integer(string="Variant A: Converted", readonly=True, copy=False)
    b_sample = fields.Integer(string="Variant B: Reached", readonly=True, copy=False)
    b_conversions = fields.Integer(string="Variant B: Converted", readonly=True, copy=False)
    a_rate = fields.Float(
        string="Variant A Rate (%)", compute="_compute_rates", store=True, digits=(16, 2)
    )
    b_rate = fields.Float(
        string="Variant B Rate (%)", compute="_compute_rates", store=True, digits=(16, 2)
    )
    p_value = fields.Float(string="p-value", compute="_compute_rates", store=True, digits=(16, 4))
    significance = fields.Float(
        string="Confidence (%)", compute="_compute_rates", store=True, digits=(16, 1)
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "a_sample",
            "a_conversions",
            "b_sample",
            "b_conversions",
        }

    @api.depends("a_sample", "a_conversions", "b_sample", "b_conversions")
    def _compute_rates(self):
        for rec in self:
            if rec.a_sample and rec.b_sample:
                rec.a_rate = rec.a_conversions / rec.a_sample * 100.0
                rec.b_rate = rec.b_conversions / rec.b_sample * 100.0
                p = two_proportion_p_value(
                    rec.a_sample, rec.a_conversions, rec.b_sample, rec.b_conversions
                )
                rec.p_value = p
                rec.significance = (1 - p) * 100.0
            else:
                rec.a_rate = rec.b_rate = rec.p_value = rec.significance = 0.0

    def action_conclude(
        self,
        winner=None,
        note=None,
        a_sample=None,
        a_conversions=None,
        b_sample=None,
        b_conversions=None,
    ):
        if winner not in ("a", "b", "none"):
            raise UserError("Name the winner: Variant A, Variant B, or no significant difference.")
        if not (note or "").strip():
            raise UserError("Record the finding: the figures the winner was judged on.")
        try:
            n_a, x_a, n_b, x_b = (
                int(v) for v in (a_sample, a_conversions, b_sample, b_conversions)
            )
        except (TypeError, ValueError) as exc:
            raise UserError(
                "Enter how many each variant reached and how many converted: the winner is "
                "judged on those figures (FR-MKT-031)."
            ) from exc
        if n_a <= 0 or n_b <= 0 or not 0 <= x_a <= n_a or not 0 <= x_b <= n_b:
            raise UserError("Each variant reached someone, and converted no more than it reached.")
        alpha = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(SIGNIFICANCE_ALPHA_PARAM, SIGNIFICANCE_ALPHA_DEFAULT)
        )
        p = two_proportion_p_value(n_a, x_a, n_b, x_b)
        better = "a" if x_a / n_a > x_b / n_b else "b"
        if winner in ("a", "b"):
            if p >= alpha:
                raise UserError(
                    "The difference is not significant (p = %.4f, needs below %.2f): record "
                    "'No significant difference' or keep the experiment running." % (p, alpha)
                )
            if winner != better:
                raise UserError("The variant named converted less than the other one.")
        elif winner == "none" and p < alpha:
            raise UserError(
                "The difference is significant (p = %.4f): name Variant %s as the winner."
                % (p, better.upper())
            )
        for rec in self:
            if rec.state != "running":
                raise UserError("Conclude a running experiment.")
        self._guarded().write(
            {"a_sample": n_a, "a_conversions": x_a, "b_sample": n_b, "b_conversions": x_b}
        )
        return super().action_conclude(winner=winner, note=note)


# ---------------------------------------------------------------------------
# 6 Budget & Attribution
# ---------------------------------------------------------------------------
class FixCampaignSpendStage(models.Model):
    """FR-MKT-033: committed (PO raised) and actual (invoiced) spend."""

    _inherit = "fix.campaign.spend"

    stage = fields.Selection(
        [("committed", "Committed (order placed)"), ("incurred", "Incurred (invoiced)")],
        string="Stage",
        default="incurred",
        required=True,
    )
    incurred_on = fields.Date(string="Invoiced On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"incurred_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {"stage"}
        return locked

    def write(self, vals):
        if (
            "stage" in vals
            and not self._fix_guard_open()
            and any(rec._fix_guard_differs("stage", vals["stage"], rec.stage) for rec in self)
        ):
            raise UserError("A commitment becomes actual through Mark Invoiced.")
        return super().write(vals)

    def _assert_within_budget(self):
        """BRU-MKT-11 counts what is committed as well as what is spent."""
        for rec in self:
            campaign = rec.campaign_id
            total = campaign._recorded_spend() + campaign._committed_spend()
            if total > (campaign.budget or 0.0) + 0.005:
                raise UserError(
                    "Recording BDT %.2f takes %s to BDT %.2f spent and committed against a "
                    "budget of BDT %.2f. Raise the budget and have it approved again first "
                    "(BRU-MKT-11)." % (rec.amount, campaign.name, total, campaign.budget or 0.0)
                )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        recs.mapped("campaign_id")._budget_alerts()
        return recs

    def action_mark_incurred(self, reference=None):
        for rec in self:
            if rec.state != "recorded" or rec.stage != "committed":
                raise UserError("Only a recorded commitment is marked invoiced.")
        vals = {"stage": "incurred", "incurred_on": fields.Date.context_today(self)}
        if (reference or "").strip():
            vals["reference"] = reference.strip()
        self._guarded().write(vals)
        for rec in self:
            rec.campaign_id.message_post(
                body="Commitment invoiced: %s, BDT %.2f." % (rec.name, rec.amount)
            )
        return True


class FixAttributionResult(models.Model):
    """FR-MKT-036 / 037, AUT-MKT-11: attributed and incremental revenue.

    A measurement, never typed: action_measure on the campaign creates one,
    and measuring again adds a new row rather than changing the old one.
    Revenue is what the estate invoiced (posted customer invoices less
    refunds) to each group in the campaign window plus the model's lookback.
    """

    _name = "fix.attribution.result"
    _description = "Campaign Measured Result"
    _order = "measured_at desc, id desc"
    _rec_name = "display_label"

    campaign_id = fields.Many2one("fix.campaign", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="campaign_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="campaign_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="campaign_id.currency_id")
    model_id = fields.Many2one("fix.attribution.model", string="Attribution Model", readonly=True)
    method = fields.Char(string="Method", readonly=True)
    measured_at = fields.Datetime(readonly=True)
    measured_by_id = fields.Many2one("res.users", string="Measured By", readonly=True)
    window_from = fields.Date(readonly=True)
    window_to = fields.Date(readonly=True)
    window_closed = fields.Boolean(
        string="Window Closed", readonly=True, help="False: measured before the lookback ended."
    )
    treated_count = fields.Integer(string="Reached", readonly=True)
    holdout_count = fields.Integer(string="Held Out", readonly=True)
    treated_converters = fields.Integer(string="Reached Who Bought", readonly=True)
    holdout_converters = fields.Integer(string="Held Out Who Bought", readonly=True)
    treated_rate = fields.Float(string="Reached Buy Rate (%)", readonly=True, digits=(16, 2))
    holdout_rate = fields.Float(string="Held-Out Buy Rate (%)", readonly=True, digits=(16, 2))
    treated_revenue = fields.Monetary(string="Revenue From Reached", readonly=True)
    holdout_baseline = fields.Monetary(
        string="Holdout Baseline",
        readonly=True,
        help="What the reached group would have spent anyway, at the holdout's rate per head.",
    )
    incremental_revenue = fields.Monetary(readonly=True)
    incremental_conversions = fields.Float(readonly=True, digits=(16, 1))
    attributed_conversions = fields.Float(readonly=True, digits=(16, 2))
    attributed_revenue = fields.Monetary(readonly=True)
    revenue_basis = fields.Char(readonly=True)
    cost = fields.Monetary(string="Campaign Cost", readonly=True)
    roi_incremental = fields.Float(
        string="Incremental ROI (%)",
        readonly=True,
        digits=(16, 1),
        help="(Incremental revenue - cost) / cost.",
    )
    note = fields.Text(readonly=True)
    display_label = fields.Char(compute="_compute_display_label", store=True)

    @api.depends("campaign_id.name", "measured_at")
    def _compute_display_label(self):
        for rec in self:
            rec.display_label = "%s · %s" % (rec.campaign_id.name or "?", rec.measured_at or "")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("m35_measuring"):
            raise UserError("A result is measured from the campaign (Measure), never typed.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.context.get("m35_measuring"):
            raise UserError("A measured result is kept as it was measured: measure again instead.")
        return super().write(vals)

    def unlink(self):
        raise UserError("A measured result is kept.")

    def _revenue_by_party(self, partner_ids, date_from, date_to):
        if not partner_ids or "account.move" not in self.env:
            return {}
        moves = (
            self.env["account.move"]
            .sudo()
            .search(
                [
                    ("move_type", "in", ("out_invoice", "out_refund")),
                    ("state", "=", "posted"),
                    ("partner_id", "in", list(partner_ids)),
                    ("invoice_date", ">=", date_from),
                    ("invoice_date", "<=", date_to),
                ]
            )
        )
        out = {}
        for move in moves:
            out[move.partner_id.id] = out.get(move.partner_id.id, 0.0) + move.amount_untaxed_signed
        return out

    @api.model
    def _measure(self, campaign):
        model = campaign.attribution_model_id or self.env["fix.attribution.model"].sudo()._current()
        method = model.method if model else "position"
        lookback = model.lookback_days if model else 90
        start = campaign.start_date or fields.Date.context_today(self)
        end = (
            (campaign.halted_at.date() if campaign.halted_at else None)
            or campaign.end_date
            or start
        )
        window_to = end + timedelta(days=lookback)
        today = fields.Date.context_today(self)
        treated = set(campaign.recipient_ids.ids)
        held = set(campaign.holdout_partner_ids.ids)
        rev_t = self._revenue_by_party(treated, start, window_to)
        rev_h = self._revenue_by_party(held, start, window_to)
        treated_revenue = sum(rev_t.values())
        holdout_revenue = sum(rev_h.values())
        conv_t = len([v for v in rev_t.values() if v > 0])
        conv_h = len([v for v in rev_h.values() if v > 0])
        rate_t = conv_t / len(treated) * 100.0 if treated else 0.0
        rate_h = conv_h / len(held) * 100.0 if held else 0.0
        notes = []
        if held and treated:
            baseline = holdout_revenue / len(held) * len(treated)
            incremental = treated_revenue - baseline
            incremental_conv = (rate_t - rate_h) / 100.0 * len(treated)
        else:
            baseline = incremental = incremental_conv = 0.0
            notes.append(
                "No holdout or no addressed recipients: incremental effect cannot be "
                "measured, only attributed revenue."
            )
        attributed = (
            self.env["fix.campaign.touch"]
            .sudo()
            .attribute(
                model=method,
                date_from=fields.Datetime.to_datetime(start),
                date_to=fields.Datetime.to_datetime(window_to) + timedelta(days=1),
                lookback_days=lookback,
            )
        )
        row = next((r for r in attributed["rows"] if r["campaign_id"] == campaign.id), None)
        cost = campaign.actual_spend + campaign.committed_spend
        if window_to >= today:
            notes.append("Measured before the attribution window closes on %s." % window_to)
        if "account.move" not in self.env:
            notes.append("Invoicing is not installed: revenue is not measured.")
        vals = {
            "campaign_id": campaign.id,
            "model_id": model.id if model else False,
            "method": method,
            "measured_at": fields.Datetime.now(),
            "measured_by_id": self.env.uid,
            "window_from": start,
            "window_to": window_to,
            "window_closed": window_to < today,
            "treated_count": len(treated),
            "holdout_count": len(held),
            "treated_converters": conv_t,
            "holdout_converters": conv_h,
            "treated_rate": rate_t,
            "holdout_rate": rate_h,
            "treated_revenue": treated_revenue,
            "holdout_baseline": baseline,
            "incremental_revenue": incremental,
            "incremental_conversions": incremental_conv,
            "attributed_conversions": row["attributed_conversions"] if row else 0.0,
            "attributed_revenue": row["attributed_revenue"] if row else 0.0,
            "revenue_basis": row["revenue_basis"] if row else "no conversion credited",
            "cost": cost,
            "roi_incremental": ((incremental - cost) / cost * 100.0) if cost else 0.0,
            "note": " ".join(notes) or False,
        }
        result = self.with_context(m35_measuring=True).create(vals)
        campaign.message_post(
            body="Measured: incremental revenue BDT %.2f against cost BDT %.2f; attributed "
            "conversions %.2f." % (incremental, cost, vals["attributed_conversions"])
        )
        return result


# ---------------------------------------------------------------------------
# 7 Portal Advertising
# ---------------------------------------------------------------------------
class FixCampaignAdSlot(models.Model):
    """FR-MKT-030 (§10.1 page_context, position): one ad per slot at a time."""

    _inherit = "fix.campaign.ad"

    position = fields.Integer(string="Position (1 = first)", default=1)
    page_context = fields.Char(
        string="Page Context", help="Which page or section of the surface, e.g. 'AC repair'."
    )

    @api.constrains("position", "placement", "page_context", "active_from", "active_to", "active")
    def _check_slot_free(self):
        for rec in self.filtered("active"):
            if (rec.position or 0) < 1:
                raise ValidationError("A position is 1 or more.")
            if rec.active_from and rec.active_to and rec.active_to < rec.active_from:
                continue  # the window check refuses it
            others = self.search(
                [
                    ("id", "!=", rec.id),
                    ("active", "=", True),
                    ("placement", "=", rec.placement),
                    ("position", "=", rec.position),
                    ("page_context", "=", rec.page_context or False),
                ]
            )
            far = fields.Date.to_date("9999-12-31")
            near = fields.Date.to_date("1900-01-01")
            for o in others:
                if (rec.active_from or near) <= (o.active_to or far) and (
                    o.active_from or near
                ) <= (rec.active_to or far):
                    raise ValidationError(
                        "%s already holds that slot in an overlapping window." % o.name
                    )
