# M07 capture audit, second pass (2026-11-18): the records five M07
# sub-module pages had no way to capture, because the records did not exist.
#
# The 13 Nov pass gave all ten pages a "+ New". Read against the spec
# (FR-CRM-001..046, BRU-CRM-01..14, owned entities section 10.1), five pages
# still had nowhere to put something a person decides:
#
#   page 1  fix.lead.qualification  FR-CRM-002 (P1), lead lifecycle 8.1,
#                                   FR-CRM-007/008: the need / authority /
#                                   budget / timing assessment, and the
#                                   outcome (qualified, disqualified with a
#                                   reason, returned to nurture). A lead was
#                                   converted straight from "captured"; the
#                                   form's "Kernel Match & Conversion" tab
#                                   showed no field at all.
#   page 2  fix.opportunity.team    FR-CRM-013, spec entity: contributors on a
#                                   pursuit with their roles. Not built.
#   page 3  fix.sales.quota         FR-CRM-023, spec entity fix.quota: the
#                                   target the forecast is read against, with
#                                   attainment. Not built.
#   page 5  fix.account.eligibility FR-CRM-027 (P1), BRU-CRM-09 (A): the
#                                   published dedicated-manager criteria (open
#                                   question Q-01 is the CCO's to answer -
#                                   this record is where the answer goes), and
#                                   a dedicated assignment outside them only
#                                   with a reason and a sales manager's
#                                   approval. Anyone could pick "Dedicated".
#   page 6  fix.qbr.action          FR-CRM-037/038: agreed actions tracked
#                                   across reviews, and an accepted
#                                   recommendation raised as an opportunity.
#                                   The actions existed only as lines inside
#                                   each QBR, and nothing turned one into a
#                                   pursuit.
import re
from datetime import date, datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

LOCAL_TZ = "Asia/Dhaka"
MANAGER_GROUP = "sales_team.group_sale_manager"

BANT_LEVELS = [
    ("confirmed", "Confirmed"),
    ("partial", "Partly Established"),
    ("unknown", "Not Established"),
]
QUALIFICATION_OUTCOMES = [
    ("qualified", "Qualified: convert to an opportunity"),
    ("disqualified", "Disqualified"),
    ("nurture", "Not Ready: return to marketing nurture"),
]
DISQUALIFY_REASONS = [
    ("no_need", "No real need"),
    ("no_budget", "No budget"),
    ("no_authority", "Cannot reach the decision maker"),
    ("no_fit", "Not a service we offer"),
    ("competitor", "Committed to a competitor"),
    ("unreachable", "Contact unreachable"),
    ("duplicate", "Duplicate of an existing pursuit"),
    ("other", "Other (explain in the notes)"),
]
TEAM_ROLES = [
    ("technical", "Technical / Solution Lead"),
    ("commercial", "Commercial / Pricing"),
    ("presales", "Pre-Sales"),
    ("executive_sponsor", "Executive Sponsor"),
    ("delivery", "Delivery Lead"),
    ("other", "Other Contributor"),
]
PERIOD_RE = re.compile(r"^(\d{4})(?:-(?:Q([1-4])|(0[1-9]|1[0-2])))?$")


def _is_manager(env):
    return env.su or env.user.has_group(MANAGER_GROUP)


def _period_bounds(period):
    """(first day, day after the last) of 'YYYY', 'YYYY-Qn' or 'YYYY-MM'."""
    match = PERIOD_RE.match((period or "").strip())
    if not match:
        raise ValidationError(
            "Write the period as a year (2026), a quarter (2026-Q4) or a month (2026-11)."
        )
    year, quarter, month = match.groups()
    year = int(year)
    if quarter:
        start = date(year, 3 * (int(quarter) - 1) + 1, 1)
        return start, start + relativedelta(months=3)
    if month:
        start = date(year, int(month), 1)
        return start, start + relativedelta(months=1)
    return date(year, 1, 1), date(year + 1, 1, 1)


def _utc_bounds(start, end):
    """The UTC datetimes that bound local Dhaka dates [start, end): a deal
    closed at 01:00 Dhaka on the 1st belongs to the new month."""
    tz = pytz.timezone(LOCAL_TZ)
    lo = tz.localize(datetime.combine(start, time.min)).astimezone(pytz.utc)
    hi = tz.localize(datetime.combine(end, time.min)).astimezone(pytz.utc)
    return lo.replace(tzinfo=None), hi.replace(tzinfo=None)


# --------------------------------------------------------------------- page 1
class CrmLeadCapture(models.Model):
    _inherit = "crm.lead"

    qualification_state = fields.Selection(
        [
            ("captured", "Captured"),
            ("qualified", "Qualified"),
            ("disqualified", "Disqualified"),
            ("recycled", "Returned to Nurture"),
        ],
        string="Qualification",
        default="captured",
        tracking=True,
        copy=False,
        help="Set only by a qualification assessment (FR-CRM-002); a lead "
        "converts to an opportunity once qualified.",
    )
    qualification_ids = fields.One2many(
        "fix.lead.qualification", "lead_id", string="Qualification Assessments"
    )
    # page 2: the pursuit team (FR-CRM-013)
    team_member_ids = fields.One2many(
        "fix.opportunity.team", "lead_id", string="Opportunity Team", copy=False
    )
    # page 6: an opportunity raised from an accepted QBR recommendation
    lead_source = fields.Selection(
        selection_add=[("qbr", "QBR Recommendation")],
        ondelete={"qbr": "set default"},
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"qualification_state"}

    def action_convert_to_opportunity(self):
        """FR-CRM-007 converts a QUALIFIED lead (lifecycle 8.1: captured ->
        qualifying -> qualified -> converted). It used to convert one
        straight from capture, with nothing recorded about why it was worth
        pursuing."""
        for lead in self:
            if lead.type == "lead" and lead.qualification_state != "qualified":
                raise UserError(
                    "Qualify '%s' first: record the need, authority, budget and "
                    "timing assessment with + Qualify a Lead (FR-CRM-002). Only a "
                    "qualified lead becomes an opportunity." % lead.name
                )
        return super().action_convert_to_opportunity()


class FixLeadQualification(models.Model):
    """The need / authority / budget / timing assessment of one lead and its
    outcome. A record of a judgement made: it is never edited; a later
    assessment supersedes it while the lead is still open."""

    _name = "fix.lead.qualification"
    _description = "Lead Qualification Assessment"
    _inherit = ["mail.thread"]
    _order = "assessed_at desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    lead_id = fields.Many2one(
        "crm.lead",
        string="Lead",
        required=True,
        index=True,
        ondelete="restrict",
        domain=[("type", "=", "lead")],
    )
    partner_id = fields.Many2one(related="lead_id.partner_id", string="Customer / Party")
    need = fields.Selection(BANT_LEVELS, string="Need", required=True)
    authority = fields.Selection(BANT_LEVELS, string="Authority", required=True)
    budget = fields.Selection(BANT_LEVELS, string="Budget", required=True)
    timing = fields.Selection(BANT_LEVELS, string="Timing", required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, required=True
    )
    budget_bdt = fields.Monetary(string="Indicated Budget (BDT)")
    decision_by = fields.Date(string="Decision Expected By")
    outcome = fields.Selection(QUALIFICATION_OUTCOMES, string="Outcome", required=True)
    disqualify_reason = fields.Selection(DISQUALIFY_REASONS, string="Disqualification Reason")
    notes = fields.Text(string="Assessment Notes")
    assessed_by = fields.Many2one(
        "res.users", string="Assessed By", readonly=True, default=lambda self: self.env.user
    )
    assessed_at = fields.Datetime(string="Assessed On", readonly=True, default=fields.Datetime.now)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("lead_id", "outcome")
    def _compute_name(self):
        labels = dict(QUALIFICATION_OUTCOMES)
        for rec in self:
            rec.name = "%s: %s" % (
                rec.lead_id.name or "Lead",
                (labels.get(rec.outcome) or "").split(":")[0],
            )

    @staticmethod
    def _check_outcome(vals):
        outcome = vals.get("outcome")
        if outcome == "qualified":
            missing = [
                label
                for key, label in (
                    ("authority", "authority"),
                    ("budget", "budget"),
                    ("timing", "timing"),
                )
                if vals.get(key) == "unknown"
            ]
            if vals.get("need") != "confirmed":
                missing.insert(0, "a confirmed need")
            if missing:
                raise ValidationError(
                    "A lead is qualified only with a confirmed need and at least a "
                    "partly established authority, budget and timing. Not yet "
                    "established: %s." % ", ".join(missing)
                )
        elif outcome == "disqualified":
            reason = vals.get("disqualify_reason")
            if not reason:
                raise ValidationError("Say why the lead is disqualified (lifecycle 8.1).")
            if reason == "other" and not (vals.get("notes") or "").strip():
                raise ValidationError("Explain the 'Other' disqualification reason in the notes.")
        if outcome != "disqualified" and vals.get("disqualify_reason"):
            raise ValidationError(
                "A disqualification reason only goes with a Disqualified outcome."
            )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            lead = self.env["crm.lead"].browse(vals.get("lead_id")).exists()
            if not lead:
                raise ValidationError("Choose the lead being assessed.")
            if lead.type != "lead":
                raise ValidationError(
                    "'%s' is already an opportunity; qualification is the lead's step." % lead.name
                )
            if not lead.active or lead.qualification_state in ("disqualified", "recycled"):
                raise ValidationError(
                    "'%s' is closed (%s). Restore it before assessing it again."
                    % (
                        lead.name,
                        dict(lead._fields["qualification_state"].selection).get(
                            lead.qualification_state, "archived"
                        ),
                    )
                )
            self._check_outcome(vals)
            vals["company_id"] = (lead.company_id or self.env.company).id
            if not self.env.su:
                vals["assessed_by"] = self.env.uid
                vals["assessed_at"] = fields.Datetime.now()
        records = super().create(vals_list)
        state_of = {"qualified": "qualified", "disqualified": "disqualified", "nurture": "recycled"}
        for rec in records:
            lead = rec.lead_id
            lead._guarded().write({"qualification_state": state_of[rec.outcome]})
            if rec.outcome == "qualified":
                lead.message_post(body="Qualified by %s (FR-CRM-002)." % rec.assessed_by.name)
            elif rec.outcome == "disqualified":
                lead.message_post(
                    body="Disqualified by %s: %s. %s"
                    % (
                        rec.assessed_by.name,
                        dict(DISQUALIFY_REASONS)[rec.disqualify_reason],
                        rec.notes or "",
                    )
                )
                lead.action_archive()
            else:
                lead.message_post(
                    body="Not ready to buy: returned to marketing nurture by %s "
                    "(FR-CRM-008). %s" % (rec.assessed_by.name, rec.notes or "")
                )
                lead.action_archive()
        return records

    def write(self, vals):
        if not self.env.su:
            raise UserError(
                "A qualification assessment is a record of a judgement made; it "
                "cannot be edited. Record a new assessment instead."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A qualification assessment cannot be deleted.")
        return super().unlink()


# --------------------------------------------------------------------- page 2
class FixOpportunityTeam(models.Model):
    """A contributor on a pursued opportunity and the role they play
    (FR-CRM-013). The opportunity's owner is its salesperson, not a member."""

    _name = "fix.opportunity.team"
    _description = "Opportunity Team Member"
    _order = "lead_id, id"

    lead_id = fields.Many2one(
        "crm.lead",
        string="Opportunity",
        required=True,
        index=True,
        ondelete="cascade",
        domain=[("type", "=", "opportunity")],
    )
    user_id = fields.Many2one(
        "res.users", string="Contributor", required=True, domain=[("share", "=", False)]
    )
    role = fields.Selection(TEAM_ROLES, string="Role", required=True)
    notes = fields.Char(string="Responsibility")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    _member_unique = models.Constraint(
        "UNIQUE (lead_id, user_id)",
        "A person is on an opportunity's team once; change their role instead.",
    )

    def _check_editable(self, leads):
        for lead in leads:
            if lead.type != "opportunity":
                raise ValidationError(
                    "'%s' is a lead; a pursuit team forms once it is an opportunity." % lead.name
                )
            if not lead.active or lead.stage_id.is_won:
                raise ValidationError(
                    "'%s' is closed; its team is part of the record now." % lead.name
                )
            if not (_is_manager(self.env) or lead.user_id == self.env.user):
                raise AccessError(
                    "Only the opportunity's owner (%s) or a sales manager may change "
                    "its team." % (lead.user_id.name or "unassigned")
                )

    def _check_members(self):
        for member in self:
            lead = member.lead_id
            if member.user_id == lead.user_id:
                raise ValidationError(
                    "%s already owns '%s'; the team lists the other contributors."
                    % (member.user_id.name, lead.name)
                )
            if member.user_id.share:
                raise ValidationError("A team member is a member of staff, not a portal user.")
            sponsors = lead.team_member_ids.filtered(lambda m: m.role == "executive_sponsor")
            if len(sponsors) > 1:
                raise ValidationError(
                    "'%s' has one executive sponsor; change the existing sponsor's "
                    "role first." % lead.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        leads = self.env["crm.lead"].browse([v.get("lead_id") for v in vals_list]).exists()
        self._check_editable(leads)
        for vals in vals_list:
            lead = self.env["crm.lead"].browse(vals.get("lead_id"))
            vals["company_id"] = (lead.company_id or self.env.company).id
        records = super().create(vals_list)
        records._check_members()
        return records

    def write(self, vals):
        self._check_editable(self.mapped("lead_id"))
        if "lead_id" in vals and any(m.lead_id.id != vals["lead_id"] for m in self):
            raise ValidationError("A team member stays on the opportunity they were added to.")
        res = super().write(vals)
        self._check_members()
        return res

    def unlink(self):
        self._check_editable(self.mapped("lead_id"))
        return super().unlink()


# --------------------------------------------------------------------- page 3
class FixSalesQuota(models.Model):
    """A seller's target for a period, optionally for one pipeline, and how
    much of it won deals have met (FR-CRM-023, spec entity fix.quota)."""

    _name = "fix.sales.quota"
    _description = "Sales Quota"
    _inherit = ["mail.thread"]
    _order = "period desc, owner_id, id"

    name = fields.Char(compute="_compute_name", store=True)
    owner_id = fields.Many2one(
        "res.users", string="Seller", required=True, index=True, tracking=True
    )
    period = fields.Char(string="Period (2026, 2026-Q4 or 2026-11)", required=True, tracking=True)
    pipeline_id = fields.Many2one(
        "fix.pipeline", string="Pipeline (empty = every stream)", tracking=True
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, required=True
    )
    target_value = fields.Monetary(string="Target (BDT)", required=True, tracking=True)
    achieved_value = fields.Monetary(string="Won (BDT)", compute="_compute_attainment")
    won_count = fields.Integer(string="Deals Won", compute="_compute_attainment")
    attainment_pct = fields.Float(string="Attainment %", compute="_compute_attainment")
    set_by = fields.Many2one("res.users", string="Set By", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("owner_id", "period", "pipeline_id")
    def _compute_name(self):
        for quota in self:
            quota.name = "%s %s%s" % (
                quota.owner_id.name or "",
                quota.period or "",
                " / %s" % quota.pipeline_id.name if quota.pipeline_id else "",
            )

    def _won_deals(self):
        self.ensure_one()
        start, end = _period_bounds(self.period)
        lo, hi = _utc_bounds(start, end)
        domain = [
            ("type", "=", "opportunity"),
            ("user_id", "=", self.owner_id.id),
            ("stage_id.is_won", "=", True),
            ("date_closed", ">=", lo),
            ("date_closed", "<", hi),
        ]
        if self.pipeline_id:
            domain.append(("pipeline_id", "=", self.pipeline_id.id))
        # attainment is the seller's whole result, whoever reads it
        return self.env["crm.lead"].sudo().search(domain)

    @api.depends("owner_id", "period", "pipeline_id", "target_value")
    def _compute_attainment(self):
        for quota in self:
            deals = quota._won_deals() if quota.owner_id and quota.period else []
            won = sum(d.expected_revenue for d in deals)
            quota.achieved_value = won
            quota.won_count = len(deals)
            quota.attainment_pct = (
                round(100.0 * won / quota.target_value, 1) if quota.target_value else 0.0
            )

    def _check_quota(self, vals_list):
        if not _is_manager(self.env):
            raise AccessError("Quotas are set by a sales manager, not by the seller (FR-CRM-023).")
        for vals in vals_list:
            if vals.get("owner_id") == self.env.uid and not self.env.su:
                raise AccessError("Nobody sets their own quota; ask another sales manager.")
            if "period" in vals:
                _period_bounds(vals["period"])
            if "target_value" in vals and (vals["target_value"] or 0.0) <= 0:
                raise ValidationError("A quota target is an amount above zero.")

    def _check_unique(self):
        for quota in self:
            clash = self.search_count(
                [
                    ("id", "!=", quota.id),
                    ("owner_id", "=", quota.owner_id.id),
                    ("period", "=", quota.period),
                    ("pipeline_id", "=", quota.pipeline_id.id or False),
                    ("company_id", "=", quota.company_id.id),
                ]
            )
            if clash:
                raise ValidationError(
                    "%s already has a quota for %s%s; change that one."
                    % (
                        quota.owner_id.name,
                        quota.period,
                        " in %s" % quota.pipeline_id.name if quota.pipeline_id else "",
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals, period=(vals.get("period") or "").strip()) for vals in vals_list]
        self._check_quota(vals_list)
        for vals in vals_list:
            vals["set_by"] = self.env.uid
        records = super().create(vals_list)
        records._check_unique()
        return records

    def write(self, vals):
        vals = dict(vals)
        if "period" in vals:
            vals["period"] = (vals["period"] or "").strip()
        if (
            "owner_id" not in vals
            and not self.env.su
            and self.env.uid in self.mapped("owner_id").ids
        ):
            raise AccessError("Nobody sets their own quota; ask another sales manager.")
        self._check_quota([vals])
        vals["set_by"] = self.env.uid
        res = super().write(vals)
        self._check_unique()
        return res

    def unlink(self):
        if not _is_manager(self.env):
            raise AccessError("Quotas are removed by a sales manager.")
        return super().unlink()


# --------------------------------------------------------------------- page 5
class FixAccountEligibility(models.Model):
    """The published dedicated-account-manager criteria (FR-CRM-027,
    BRU-CRM-09). Open question Q-01 - which measures, which thresholds - is
    the CCO's to answer; this record is where the answer is published. An
    account meeting ANY criterion set here qualifies."""

    _name = "fix.account.eligibility"
    _description = "Dedicated Account Manager Eligibility Criteria"
    _inherit = ["mail.thread"]
    _order = "effective_from desc, id desc"

    name = fields.Char(string="Criteria Name", required=True, tracking=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, required=True
    )
    min_annual_spend_bdt = fields.Monetary(
        string="Annual Spend At Least (BDT)",
        tracking=True,
        help="Posted customer invoices less credit notes over the last 12 months. 0 = not used.",
    )
    min_acv_bdt = fields.Monetary(
        string="Annual Contract Value At Least (BDT)",
        tracking=True,
        help="The key account's annual contract value. 0 = not used.",
    )
    strategic_qualifies = fields.Boolean(
        string="Strategic-Tier Accounts Qualify", default=True, tracking=True
    )
    effective_from = fields.Date(
        string="Effective From", required=True, default=fields.Date.context_today, tracking=True
    )
    active = fields.Boolean(default=True, tracking=True)
    published_by = fields.Many2one("res.users", string="Published By", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    def _check_publish(self):
        if not _is_manager(self.env):
            raise AccessError(
                "The dedicated-manager criteria are published by the CCO (a sales manager)."
            )

    def _check_criteria(self):
        for crit in self:
            if crit.min_annual_spend_bdt < 0 or crit.min_acv_bdt < 0:
                raise ValidationError("A threshold is zero (not used) or a positive amount.")
            if not (crit.min_annual_spend_bdt or crit.min_acv_bdt or crit.strategic_qualifies):
                raise ValidationError(
                    "Set at least one criterion: annual spend, contract value or strategic tier."
                )

    @api.model_create_multi
    def create(self, vals_list):
        self._check_publish()
        vals_list = [dict(vals, published_by=self.env.uid) for vals in vals_list]
        records = super().create(vals_list)
        records._check_criteria()
        # one set of criteria is in force at a time: the new one supersedes
        for crit in records.filtered("active"):
            older = self.search(
                [("id", "not in", records.ids), ("company_id", "=", crit.company_id.id)]
            )
            if older:
                older.write({"active": False})
                crit.message_post(body="Supersedes: %s" % ", ".join(older.mapped("name")))
        return records

    def write(self, vals):
        self._check_publish()
        res = super().write(dict(vals, published_by=self.env.uid))
        self._check_criteria()
        return res

    def unlink(self):
        raise UserError("Published criteria are archived, not deleted.")

    @api.model
    def _current(self, company=None):
        company = company or self.env.company
        return self.sudo().search([("company_id", "=", company.id)], limit=1)

    @api.model
    def _evaluate(self, partner, company=None):
        """(eligible, basis): whether ``partner`` meets the criteria in force,
        and the measured figures that say why."""
        crit = self._current(company)
        if not crit:
            return False, "No dedicated-manager criteria are published"
        commercial = partner.commercial_partner_id
        met, measured = [], []
        account = (
            self.env["fix.account"].sudo().search([("partner_id", "=", commercial.id)], limit=1)
        )
        if crit.strategic_qualifies:
            measured.append("tier %s" % (account.tier or "none"))
            if account.tier == "strategic":
                met.append("strategic tier")
        if crit.min_acv_bdt:
            acv = account.acv_bdt or 0.0
            measured.append("ACV BDT %s" % f"{acv:,.0f}")
            if acv >= crit.min_acv_bdt:
                met.append("contract value")
        if crit.min_annual_spend_bdt:
            since = fields.Date.context_today(self) - timedelta(days=365)
            # cd_crm_ext does not depend on accounting; no ledger, no spend
            moves = (
                self.env["account.move"]
                .sudo()
                .search(
                    [
                        ("move_type", "in", ("out_invoice", "out_refund")),
                        ("state", "=", "posted"),
                        ("commercial_partner_id", "=", commercial.id),
                        ("invoice_date", ">=", since),
                    ]
                )
                if "account.move" in self.env
                else []
            )
            spend = sum(m.amount_total_signed for m in moves)
            measured.append("12-month spend BDT %s" % f"{spend:,.0f}")
            if spend >= crit.min_annual_spend_bdt:
                met.append("annual spend")
        basis = "%s: %s" % (crit.name, "; ".join(measured))
        if met:
            return True, "Eligible on %s (%s)" % (", ".join(met), basis)
        return False, "Below the criteria (%s)" % basis


class FixAccountAssignmentEligibility(models.Model):
    _inherit = "fix.account.assignment"

    eligibility_basis = fields.Char(string="Eligibility Basis", readonly=True, copy=False)
    exception_reason = fields.Char(
        string="Exception Reason (BRU-CRM-09)",
        help="Why a dedicated manager is assigned to an account outside the "
        "published criteria. Only a sales manager (the CCO) may approve it.",
    )
    exception_approved_by = fields.Many2one(
        "res.users", string="Exception Approved By", readonly=True, copy=False
    )

    STAMPS = ("eligibility_basis", "exception_approved_by")

    def _stamp_dedicated(self):
        """FR-CRM-027 / BRU-CRM-09 on every dedicated assignment."""
        Eligibility = self.env["fix.account.eligibility"]
        for asg in self.filtered(lambda a: a.assignment_type == "dedicated"):
            eligible, basis = Eligibility._evaluate(asg.partner_id, asg.company_id)
            stamp = {"eligibility_basis": basis[:250], "exception_approved_by": False}
            if not eligible:
                if not (asg.exception_reason or "").strip():
                    raise ValidationError(
                        "%s does not meet the dedicated-manager criteria (%s). Give an "
                        "exception reason; a sales manager (the CCO) approves it "
                        "(BRU-CRM-09)." % (asg.partner_id.name, basis)
                    )
                if not _is_manager(self.env):
                    raise AccessError(
                        "A dedicated manager outside the published criteria is an "
                        "exception only a sales manager (the CCO) may approve "
                        "(BRU-CRM-09). Ask one to record this assignment."
                    )
                stamp["exception_approved_by"] = self.env.uid
            super(FixAccountAssignmentEligibility, asg.sudo()).write(stamp)

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [
            {k: v for k, v in vals.items() if self.env.su or k not in self.STAMPS}
            for vals in vals_list
        ]
        records = super().create(vals_list)
        records._stamp_dedicated()
        return records

    def write(self, vals):
        if not self.env.su:
            vals = {k: v for k, v in vals.items() if k not in self.STAMPS}
        res = super().write(vals)
        if {"assignment_type", "partner_id", "exception_reason"} & set(vals):
            self._stamp_dedicated()
        return res


# --------------------------------------------------------------------- page 6
class FixQbrActionTracking(models.Model):
    _inherit = "fix.qbr.action"

    partner_id = fields.Many2one(related="qbr_id.partner_id", string="Account")
    qbr_period = fields.Char(related="qbr_id.period", string="Review")
    opportunity_id = fields.Many2one(
        "crm.lead", string="Opportunity Raised", readonly=True, copy=False, index=True
    )

    def write(self, vals):
        if "opportunity_id" in vals and not self.env.su:
            raise UserError("The opportunity is linked by Raise Opportunity, not typed.")
        return super().write(vals)

    def action_raise_opportunity(self):
        """FR-CRM-038: a recommendation the client accepted at the review
        becomes a pursuit on the account, once."""
        for action in self:
            if action.opportunity_id:
                raise UserError(
                    "'%s' was already raised as %s."
                    % (action.description, action.opportunity_id.display_name)
                )
            if action.qbr_id.state != "held":
                raise UserError(
                    "Raise an opportunity from a review that was held: the client "
                    "accepts a recommendation at the meeting."
                )
            if action.state == "cancelled":
                raise UserError("'%s' was cancelled." % action.description)
        for action in self:
            qbr = action.qbr_id
            opportunity = (
                self.env["crm.lead"]
                .with_context(default_type="opportunity")
                .create(
                    {
                        "name": action.description,
                        "type": "opportunity",
                        "partner_id": qbr.partner_id.id,
                        "user_id": (action.owner_internal or self.env.user).id,
                        "lead_source": "qbr",
                        "is_cross_sell": True,
                        "description": "Accepted at the %s business review of %s."
                        % (qbr.period, qbr.partner_id.name),
                    }
                )
            )
            super(FixQbrActionTracking, action.sudo()).write({"opportunity_id": opportunity.id})
            qbr.message_post(
                body="Recommendation '%s' raised as opportunity %s."
                % (action.description, opportunity.display_name)
            )
        return True
