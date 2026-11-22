# fix_incentive_scheme — M57: the incentive scheme and its effective-dated
# versions (BRU-PIC-01/02, FR-PIC-026/027).
#
# A09 workflow audit M57 §1.2 row 1 and report "Still open" item 7: there was
# no scheme or version model. The band rates (15/8/4 %) and the score cut-offs
# (0.90/0.75/0.60) were literals in incentive_amount(), the band base was a
# number typed on each run, and a run computed with no approval of any kind.
#
# Now a scheme holds versions; a version holds the rates, the cut-offs, the
# eligibility rules and the band base. A version is approved by the HR
# Director AND THEN the CFO: two routed M63 requests through
# fix.people.approval.mixin, decided by two different people, neither of whom
# prepared or requested it. An approved version is frozen: a change is a new
# version. An incentive run computes only under an approved version in force
# for its period, and pins it (fix_performance.py).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_performance import OFFICER, changed_fields, guard_first, require_group

HR_DIRECTOR = "cd_performance.group_scheme_hr_director"
CFO = "cd_performance.group_scheme_cfo"

# The two signatures BRU-PIC-01 names, in order.
STEP_GROUP = {"hr_review": HR_DIRECTOR, "cfo_review": CFO}


class FixApprovalMatrixPerformance(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("hr_incentive_scheme", "HR: Incentive Scheme Version"),
            ("hr_compensation", "HR: Compensation Proposal"),
        ],
        ondelete={"hr_incentive_scheme": "cascade", "hr_compensation": "cascade"},
    )


class FixIncentiveScheme(models.Model):
    _name = "fix.incentive.scheme"
    _description = "Incentive Scheme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    description = fields.Text()
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    version_ids = fields.One2many("fix.incentive.scheme.version", "scheme_id", string="Versions")
    current_version_id = fields.Many2one(
        "fix.incentive.scheme.version",
        string="Version in Force Today",
        compute="_compute_current_version",
    )

    _code_unique = models.Constraint(
        "UNIQUE (company_id, code)", "A scheme code is unique within a company"
    )

    def _compute_current_version(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.current_version_id = rec._fix_version_for(today)

    def _fix_version_for(self, day):
        """The APPROVED version in force on `day` (latest effective date wins)."""
        self.ensure_one()
        return (
            self.env["fix.incentive.scheme.version"]
            .sudo()
            .search(
                [
                    ("scheme_id", "=", self.id),
                    ("state", "=", "approved"),
                    ("date_from", "<=", day),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", day),
                ],
                order="date_from desc, version_no desc",
                limit=1,
            )
        )

    @api.depends("version_ids.state", "version_ids.band_base", "version_ids.date_from")
    def _compute_readiness(self):
        """M57-F2: what blocks this scheme from computing a run today, said on
        the schemes screen (a draft version with no band base — the seeded v1 —
        warns before anyone opens a run)."""
        for rec in self:
            warnings = []
            versions = rec.sudo().version_ids
            for ver in versions:
                if ver.state == "draft" and (ver.sudo().band_base or 0.0) <= 0:
                    warnings.append(
                        "%s is a draft with band base 0: set the band base and have the HR "
                        "Director and the CFO approve it before any run computes."
                        % ver.display_name
                    )
            if versions and not any(ver.state == "approved" for ver in versions):
                warnings.append("No approved version: a run computes only under one.")
            rec.readiness_warning = " ".join(warnings)

    readiness_warning = fields.Char(
        string="Readiness",
        compute="_compute_readiness",
        help="Why no run can compute under "
        "this scheme yet (draft version, band base 0, no approval).",
    )

    @api.model
    def _fix_scheme_for(self, company):
        """The company's scheme when it has exactly one active scheme."""
        schemes = self.sudo().search(
            [("company_id", "=", company.id), ("active", "=", True)], limit=2
        )
        return schemes if len(schemes) == 1 else self.browse()


class FixIncentiveSchemeVersion(models.Model):
    _name = "fix.incentive.scheme.version"
    _description = "Incentive Scheme Version"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "scheme_id, date_from desc, version_no desc"

    _approval_domain = "hr_incentive_scheme"
    _approval_apply_method = "action_approve"
    _approval_group = HR_DIRECTOR

    name = fields.Char(compute="_compute_name", store=True)
    scheme_id = fields.Many2one(
        "fix.incentive.scheme", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        "res.company", related="scheme_id.company_id", store=True, index=True
    )
    version_no = fields.Integer(string="Version", readonly=True, copy=False)
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    basis = fields.Char(
        string="Source of the Figures",
        help="Where the rates and cut-offs come from (a board minute, a policy, ...). "
        "Version 1 is seeded 'as coded, unsourced': the figures the code used.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # The band base is T5 compensation data (05-04 4-5), as it was on the run.
    band_base = fields.Monetary(
        string="Band Base",
        currency_field="currency_id",
        groups="%s,cd_performance.group_incentive_approver,%s,%s" % (OFFICER, HR_DIRECTOR, CFO),
        help="The amount the band rates are a percentage of.",
    )
    cut_top = fields.Float(string="Top Band From Score", digits=(3, 4), default=0.90)
    cut_mid = fields.Float(string="Middle Band From Score", digits=(3, 4), default=0.75)
    cut_low = fields.Float(string="Lower Band From Score", digits=(3, 4), default=0.60)
    rate_top = fields.Float(string="Top Band Rate %", default=15.0)
    rate_mid = fields.Float(string="Middle Band Rate %", default=8.0)
    rate_low = fields.Float(string="Lower Band Rate %", default=4.0)
    # Eligibility (FR-PIC-028/032). 0 means "not ruled": no minimum, no
    # long-leave proration. Joiners and leavers are always prorated by days.
    min_service_days = fields.Integer(
        string="Minimum Service (days)",
        default=0,
        help="Days of service at the period end before an employee earns an incentive "
        "(0 = no minimum).",
    )
    long_leave_days = fields.Integer(
        string="Long Leave From (days)",
        default=0,
        help="An approved leave of at least this many days is taken out of the paid days "
        "(0 = leave is not prorated).",
    )
    # M57-F9 (FR-PIC-028, AUT-PIC-12, BRU-PIC-15): an employee on an active
    # PIP or under an open disciplinary case earns no incentive of this scheme.
    pip_ineligible = fields.Boolean(
        string="PIP / Disciplinary Ineligible",
        default=True,
        help="True (default): an active PIP or an open disciplinary case makes the "
        "employee ineligible for the incentive of the period.",
    )
    # M57-F10: the two windows, visible and editable as scheme-version terms
    # instead of technical parameters only. 0 = not ruled here: the estate
    # parameter decides (0 = off). OWNER decision D3: recommend 5 / 30 days.
    dispute_days = fields.Integer(
        string="Dispute Window (days)",
        default=0,
        help="Days an employee has to dispute a computed line of a run under this "
        "version (0 = the estate parameter cd_performance.incentive_dispute_days "
        "decides; 0 there too = no window).",
    )
    clawback_days = fields.Integer(
        string="Clawback Window (days)",
        default=0,
        help="A rework or credit within this many days of an order's completion claws "
        "its share of a paid incentive back (0 = the estate parameter "
        "cd_performance.incentive_clawback_days decides; 0 there too = off).",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("hr_review", "Awaiting HR Director"),
            ("cfo_review", "Awaiting CFO"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    hr_director_id = fields.Many2one("res.users", string="HR Director Approval By", readonly=True)
    hr_director_at = fields.Datetime(string="HR Director Approved At", readonly=True)
    cfo_id = fields.Many2one("res.users", string="CFO Approval By", readonly=True)
    cfo_at = fields.Datetime(string="CFO Approved At", readonly=True)
    run_ids = fields.One2many("fix.incentive.run", "scheme_version_id", string="Runs")
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _version_unique = models.Constraint(
        "UNIQUE (scheme_id, version_no)", "A version number is used once per scheme"
    )

    _TERMS = frozenset(
        {
            "scheme_id",
            "date_from",
            "date_to",
            "basis",
            # M57-F23: after both signatures the version's currency and
            # operating unit are frozen too — the meaning of the band base and
            # the unit it belongs to cannot change under an approval.
            "currency_id",
            "operating_unit_id",
            "band_base",
            "cut_top",
            "cut_mid",
            "cut_low",
            "rate_top",
            "rate_mid",
            "rate_low",
            "min_service_days",
            "long_leave_days",
            "pip_ineligible",
            "dispute_days",
            "clawback_days",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "hr_director_id",
            "hr_director_at",
            "cfo_id",
            "cfo_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"version_no"}
        if self and any(rec.state != "draft" for rec in self):
            locked = locked | self._TERMS
        return locked

    @api.depends("scheme_id.code", "version_no")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s v%d" % (rec.scheme_id.code or "?", rec.version_no or 0)

    # ---- validation -----------------------------------------------------------
    @api.constrains("cut_top", "cut_mid", "cut_low", "rate_top", "rate_mid", "rate_low")
    def _check_bands(self):
        for rec in self:
            if not (1 >= rec.cut_top > rec.cut_mid > rec.cut_low >= 0):
                raise ValidationError(
                    "The score cut-offs run 1 >= top > middle > lower >= 0 (got %s / %s / %s)."
                    % (rec.cut_top, rec.cut_mid, rec.cut_low)
                )
            for rate in (rec.rate_top, rec.rate_mid, rec.rate_low):
                if not 0 <= rate <= 100:
                    raise ValidationError("A band rate is a 0-100 percentage.")

    @api.constrains(
        "date_from",
        "date_to",
        "min_service_days",
        "long_leave_days",
        "dispute_days",
        "clawback_days",
    )
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError("A scheme version cannot end before it starts.")
            if (
                rec.min_service_days < 0
                or rec.long_leave_days < 0
                or rec.dispute_days < 0
                or rec.clawback_days < 0
            ):
                raise ValidationError("Eligibility and window days cannot be negative.")

    @api.constrains("band_base")
    def _check_band_base(self):
        for rec in self.sudo():
            if (rec.band_base or 0.0) < 0:
                raise ValidationError("A band base cannot be negative.")

    # ---- the banded amount ------------------------------------------------------
    def _fix_rate_for(self, score):
        """The band rate (a fraction) this version gives `score`."""
        self.ensure_one()
        if not 0 <= score <= 1:
            raise UserError("A composite score is 0..1 (got %s)." % score)
        if score >= self.cut_top:
            return self.rate_top / 100.0
        if score >= self.cut_mid:
            return self.rate_mid / 100.0
        if score >= self.cut_low:
            return self.rate_low / 100.0
        return 0.0

    def _fix_amount_for(self, score):
        self.ensure_one()
        return round((self.sudo().band_base or 0.0) * self._fix_rate_for(score), 2)

    # ---- writes -------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            require_group(self.env, OFFICER, "Drafting an incentive scheme version")
        for vals in vals_list:
            # The number is the scheme's next one, whatever the caller sent.
            if vals.get("scheme_id") and not (self.env.su and vals.get("version_no")):
                last = self.sudo().search(
                    [("scheme_id", "=", vals["scheme_id"])], order="version_no desc", limit=1
                )
                vals["version_no"] = (last.version_no or 0) + 1
        return super().create(vals_list)

    def write(self, vals):
        guard_first(self, vals)
        if not self._fix_guard_open():
            if changed_fields(self, vals, {"version_no"}):
                raise UserError("A scheme version keeps its number.")
            frozen = changed_fields(self.filtered(lambda r: r.state != "draft"), vals, self._TERMS)
            if frozen:
                raise UserError(
                    "A scheme version in approval or approved keeps its terms (%s). A change "
                    "is a new version." % ", ".join(sorted(frozen))
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su and any(rec.state not in ("draft", "rejected") for rec in self):
            raise UserError("An approved or pending scheme version is evidence; it is not deleted.")
        return super().unlink()

    # ---- approval declarations ---------------------------------------------------
    def _approval_subject_employees(self):
        return self.env["hr.employee"]

    def _approval_preparers(self):
        # The requester and the HR Director who signed step one never sign
        # the CFO step.
        return self.mapped("requested_by_id") | self.mapped("hr_director_id")

    def _approval_group_xmlid(self):
        self.ensure_one()
        return STEP_GROUP.get(self.state, HR_DIRECTOR)

    def _approval_group_for(self, rule, tier):
        # BRU-PIC-01 names the two signatures; a matrix row may set the SLA
        # and escalation of each step but not merge them into one group.
        return self.env.ref(self._approval_group_xmlid(), raise_if_not_found=False)

    def _approval_tier(self):
        return False

    def _approval_needed(self) -> bool:
        return self.state in ("draft", "hr_review", "cfo_review")

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Scheme version rejected: %s" % (comment or ""))

    # ---- transitions ----------------------------------------------------------------
    def _fix_assert_complete(self):
        for rec in self:
            if (rec.sudo().band_base or 0.0) <= 0:
                raise UserError(
                    "%s has no band base: set the amount the band rates apply to before "
                    "requesting its approval." % rec.display_name
                )

    def _fix_assert_lawful_window(self):
        """M57-F21 (BRU-PIC-02 for schemes, the rule KPI definitions already
        follow): an approved version never overlaps another approved one, and
        a replacement is never back-dated — its effective date is today or
        later, so a version approved today cannot change an uncomputed past
        period."""
        today = fields.Date.context_today(self)
        for rec in self:
            olds = rec.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("scheme_id", "=", rec.scheme_id.id),
                    ("state", "=", "approved"),
                ]
            )
            if not olds:
                continue
            if rec.date_from < today:
                raise UserError(
                    "BRU-PIC-02: %s takes effect from today or later (%s is in the past); a "
                    "period already measured keeps the version it was measured under, and "
                    "an uncomputed past period keeps the version in force then."
                    % (rec.display_name, rec.date_from)
                )
            for old in olds:
                if old.date_from >= rec.date_from:
                    raise UserError(
                        "%s already starts on %s: a new version starts after it."
                        % (old.display_name, old.date_from)
                    )
                if rec.date_to and rec.date_to >= old.date_from:
                    raise UserError(
                        "%s overlaps %s (in force from %s): one approved version covers a "
                        "day at a time." % (rec.display_name, old.display_name, old.date_from)
                    )

    def _fix_assert_second_decider_feasible(self):
        """M57-F2: the CFO signature needs a lawful second decider — an active
        holder of the CFO group who is neither the requester nor in the HR
        Director group. On production data the two groups hold the same two
        accounts, so no version can be lawfully approved: say so at the
        request, naming the group (owner decision D1: appoint the people)."""
        group = self.env.ref(CFO, raise_if_not_found=False)
        if not group:
            raise UserError(
                "The CFO approval group (%s) does not exist: no scheme version can be "
                "approved." % CFO
            )
        holders = group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
        hrd = self.env.ref(HR_DIRECTOR, raise_if_not_found=False)
        hrd_holders = (
            hrd.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
            if hrd
            else self.env["res.users"]
        )
        excluded = hrd_holders | self.mapped("requested_by_id") | self.mapped("hr_director_id")
        feasible = holders - excluded
        if not feasible:
            raise UserError(
                "No lawful second decider: every active holder of %s also holds %s or "
                "requested this version (%s). Appoint a CFO who is not the HR Director "
                "before requesting the approval (decision D1)."
                % (
                    group.name,
                    hrd.name if hrd else HR_DIRECTOR,
                    ", ".join(holders.mapped("name")) or "no active holder",
                )
            )

    def action_request_approval(self, justification=None):
        """The Incentive Officer routes a draft version to the HR Director."""
        require_group(self.env, OFFICER, "Requesting a scheme version's approval")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft scheme version is sent for approval.")
        self._fix_assert_complete()
        self._fix_assert_lawful_window()
        self._fix_assert_second_decider_feasible()
        for rec in self:
            rec._guarded().write({"state": "hr_review", "requested_by_id": self.env.user.id})
        return super().action_request_approval(justification=justification)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        for rec in self:
            rec._guarded().write(
                {"state": "draft", "hr_director_id": False, "hr_director_at": False}
            )
        return result

    def action_approve(self):
        """Run by the approval engine from an inbox task: the HR Director's
        signature routes the version on to the CFO; the CFO's approves it."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            decider = rec._people_decider()
            if rec.state == "hr_review":
                rec._guarded().write(
                    {
                        "state": "cfo_review",
                        "hr_director_id": decider.id,
                        "hr_director_at": fields.Datetime.now(),
                        "approval_state": "none",
                    }
                )
                # The second signature is its own routed request. It is raised
                # by the HR Director, who is therefore excluded from it.
                rec._fix_request_next_step()
            elif rec.state == "cfo_review":
                if decider == rec.hr_director_id:
                    raise UserError("The HR Director and the CFO are two different people.")
                rec._guarded().write(
                    {"state": "approved", "cfo_id": decider.id, "cfo_at": fields.Datetime.now()}
                )
                rec.message_post(
                    body="Approved by %s (HR Director) and %s (CFO)."
                    % (rec.hr_director_id.name, decider.name)
                )
            else:
                raise UserError("%s is not awaiting a decision." % rec.display_name)
        return True

    def _fix_request_next_step(self):
        """Raise the CFO step's request (private: only the HR Director's routed
        decision raises it)."""
        return super().action_request_approval()

    def action_reset_draft(self):
        require_group(self.env, OFFICER, "Reopening a rejected scheme version")
        for rec in self:
            if rec.state != "rejected":
                raise UserError("Only a rejected scheme version goes back to draft.")
            rec._guarded().write(
                {
                    "state": "draft",
                    "approval_state": "none",
                    "requested_by_id": False,
                    "hr_director_id": False,
                    "hr_director_at": False,
                }
            )
        return True
