# M40 capture audit (19 Nov 2026): the records each sub-module page names.
#
# The workspace's ten M40 pages captured a partner, an authorisation, a
# referral, a deal, a franchise agreement, a rebate or a conflict - and nothing
# else the spec (M40 §5, §9, §10.1) puts on them:
#   p1 Partner Master      no programme / tier (FR-PCM-003/004, BRU-PCM-12),
#                          no named contacts (FR-PCM-009)
#   p2 Recruitment         "+ New" opened a BRAND AUTHORISATION; no onboarding
#                          checklist (FR-PCM-007, BRU-PCM-01), no enablement
#                          (FR-PCM-041)
#   p3 Brand Relations     no obligation (FR-PCM-017), brand audit (016) or
#                          engagement log / brand assessment (020/021, BRU-20)
#   p4 Alliances           "+ New" made a partner; no scheme (030) and no
#                          eligibility check (031, BRU-19), no commitment (032)
#   p5 Referrals           no referral link/code (022), no consented lead (023,
#                          BRU-06), no attribution window (024, BRU-04/05)
#   p6 Deal Registration   no channel precedence rule (029, BRU-10)
#   p7 Resellers           "+ New" made a partner; no allocation (033)
#   p8 Franchise           no territory / exclusivity (035, BRU-16), no
#                          royalty (036, BRU-17)
#   p9 Commercial Terms    no MDF fund ledger or evidenced claim (039, T-09,
#                          BRU-11)
#  p10 Performance         listed conflicts; the technical audits sat on no page
#
# Every state, stamp and computed figure below is guarded (fix.guarded.mixin)
# and moves only through its action, with the role and the segregation of
# duties the spec names. No new domain events: outcomes go to the chatter.
import re
import secrets
from datetime import timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_partner import (
    EARNING_STATES,
    GROUP_MANAGER,
    GROUP_OFFICER,
    GROUP_TIER3,
    fix_not_creator,
    fix_require,
)
from .fix_partner_ops import GROUP_FINANCE

# Business defaults the owner must confirm (report §6).
LEAD_ATTRIBUTION_DAYS = 90  # FR-PCM-024: the attribution window
ROYALTY_MAX_RATE = 0.30  # the highest royalty / levy rate accepted
PARAM_ATTRIBUTION_DAYS = "cd_partner.lead_attribution_days"
# A04 ERP audit M40-F1/F2: the income accounts the franchise invoices credit.
# An OWNER choice: unset, the invoice is refused (fail closed). fix_real has
# no royalty or franchise-fee income account; 400109 "Other Income" is the
# recommended code until one is opened.
PARAM_ACCOUNT = "cd_partner.account_code.%s"
# A04 ERP audit M40-F28: the price_for context key that names the alliance
# eligibility check granting a member-only M11 promotion.
ALLIANCE_CHECK_CTX = "fix_alliance_check_id"
PARTNER_ACCOUNT_ROLES = {
    "royalty_income": "franchise royalty and marketing levy income",
    "franchise_fee_income": "franchise initial fee income",
}


def attribution_days(env):
    """FR-PCM-024: the attribution window in days - the parameter when the
    owner set one, else the programme default (90)."""
    raw = env["ir.config_parameter"].sudo().get_param(PARAM_ATTRIBUTION_DAYS)
    try:
        days = int(raw) if raw not in (None, False, "") else LEAD_ATTRIBUTION_DAYS
    except (TypeError, ValueError):
        days = LEAD_ATTRIBUTION_DAYS
    return days if days > 0 else LEAD_ATTRIBUTION_DAYS


def partner_account(env, company, role):
    """The configured income account of a franchise invoice, or a refusal
    naming the parameter. Never guessed."""
    param = PARAM_ACCOUNT % role
    code = env["ir.config_parameter"].sudo().get_param(param)
    if not code:
        raise UserError(
            "No GL account is configured for %s: set system parameter %s to the account code "
            "(recommended: 400109 Other Income). Nothing is invoiced until it is set."
            % (PARTNER_ACCOUNT_ROLES[role], param)
        )
    account = (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not account:
        raise UserError(
            "System parameter %s names account %s, which %s does not have."
            % (param, code, company.name)
        )
    return account


def dhaka_day(moment):
    """The Asia/Dhaka business day of a UTC datetime."""
    moment = fields.Datetime.to_datetime(moment) or fields.Datetime.now()
    return moment.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Dhaka")).date()


def credit_ex_vat(note):
    """The VAT-exclusive part of an M20 credit note: its amount carries the
    invoice's VAT in the invoice's proportion."""
    inv = note.invoice_id
    total = inv.total_payable or 0.0
    if total <= 0.005:
        return 0.0
    return (note.amount or 0.0) * (inv.taxable_amount or 0.0) / total


def _clean(text):
    return (str(text).strip() if text else "") or False


def _refuse_changes(rec, vals, names, why):
    changed = [
        n
        for n in set(names) & set(vals)
        if n in rec._fields and rec._fix_guard_differs(n, vals[n], rec[n])
    ]
    if changed:
        raise UserError(
            "%s cannot be changed on %s: %s."
            % (
                ", ".join(sorted(rec._fields[n].string or n for n in changed)),
                rec.display_name,
                why,
            )
        )


def _assert_own_attachment(rec, field_name):
    att = rec[field_name].sudo()
    if att and (att.res_model != rec._name or att.res_id != rec.id):
        raise ValidationError(
            "Document %s is not attached to %s: upload it on this record."
            % (att.name, rec.display_name)
        )


def _require_finance(env, what):
    finance = env.ref(GROUP_FINANCE, raise_if_not_found=False)
    if not (env.su or (finance and env.user in finance.sudo().all_user_ids)):
        raise UserError("%s is finance's (Invoicing / Billing role)." % what)


class FixPartnerCaptureBase(models.AbstractModel):
    """Shared freeze: once a record leaves its first state, the fields it
    was decided on stop changing."""

    _name = "fix.partner.capture.base"
    _description = "M40 Capture Register Base"
    _inherit = ["mail.thread", "fix.guarded.mixin"]

    _OPEN_STATES = ("draft",)
    _FROZEN = frozenset()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and "state" in rec._fields and rec.state not in self._OPEN_STATES:
            locked |= set(self._FROZEN)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open() and self._FROZEN:
            for rec in self:
                if "state" in rec._fields and rec.state not in self._OPEN_STATES:
                    _refuse_changes(rec, vals, self._FROZEN, "it is %s" % rec.state)
        return super().write(vals)


# =============================================================== p1 programme
class FixPartnerProgramme(models.Model):
    """FR-PCM-003/004, T-10, BRU-PCM-12: a versioned programme. Published
    terms never change; a change is a new version, and a partner stays bound
    to the version in force at its agreement."""

    _name = "fix.partner.programme"
    _description = "Partner Programme"
    _inherit = ["fix.partner.capture.base"]
    _order = "code, version desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    partner_type = fields.Selection(
        [
            ("brand", "Brand Partner"),
            ("referral", "Referral Partner"),
            ("reseller", "Reseller"),
            ("franchise", "Franchise"),
            ("alliance", "Strategic Alliance"),
        ],
        required=True,
    )
    version = fields.Integer(default=1, readonly=True, copy=False)
    previous_id = fields.Many2one("fix.partner.programme", readonly=True, copy=False)
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    entry_criteria = fields.Text(required=True)
    benefits = fields.Text()
    obligations = fields.Text()
    commercial_terms_ref = fields.Char(
        string="Commercial Terms (M11 reference)",
        help="BRU-PCM-03: M11 holds the rates and M53 pays; the programme names them.",
    )
    exit_conditions = fields.Text()
    tier_ids = fields.One2many("fix.partner.tier", "programme_id", string="Tiers")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("published", "Published"),
            ("superseded", "Superseded"),
            ("retired", "Retired"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    published_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    published_at = fields.Datetime(readonly=True, copy=False)
    partner_count = fields.Integer(compute="_compute_partner_count")

    _FROZEN = frozenset(
        {
            "name",
            "code",
            "partner_type",
            "valid_from",
            "entry_criteria",
            "benefits",
            "obligations",
            "commercial_terms_ref",
            "exit_conditions",
            "company_id",
        }
    )
    _code_version_unique = models.Constraint(
        "UNIQUE (code, version)", "A programme code carries each version once."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version",
            "previous_id",
            "published_by_id",
            "published_at",
        }

    def _compute_partner_count(self):
        data = (
            self.env["fix.partner"]
            .sudo()
            ._read_group([("programme_id", "in", self.ids)], ["programme_id"], ["__count"])
        )
        counts = {prog.id: n for prog, n in data}
        for rec in self:
            rec.partner_count = counts.get(rec.id, 0)

    def action_publish(self):
        fix_require(self.env, [GROUP_MANAGER], "Publishing a partner programme")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft programme is published.")
            fix_not_creator(self.env, rec, "publishing it")
            if not (rec.entry_criteria or "").strip():
                raise ValidationError("A programme states its entry criteria (FR-PCM-003).")
            if not rec.tier_ids:
                raise ValidationError("A programme has at least one tier (FR-PCM-004).")
            older = self.sudo().search(
                [("code", "=", rec.code), ("state", "=", "published"), ("id", "!=", rec.id)]
            )
            if older:
                older._guarded().write({"state": "superseded"})
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
        return True

    def action_new_version(self):
        """A change to published terms: a draft copy with the next version."""
        fix_require(self.env, [GROUP_OFFICER], "Drafting a new programme version")
        self.ensure_one()
        if self.state not in ("published", "superseded"):
            raise UserError("A new version is drafted from a published programme.")
        top = max(self.sudo().search([("code", "=", self.code)]).mapped("version") or [0])
        new = self._guarded().copy({"version": top + 1, "previous_id": self.id, "state": "draft"})
        for tier in self.tier_ids:
            tier.copy({"programme_id": new.id})
        return {"res_id": new.id, "res_model": self._name}

    def action_retire(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Retiring a partner programme")
        if not _clean(reason):
            raise UserError("State why the programme is retired.")
        for rec in self:
            if rec.state not in ("published", "superseded"):
                raise UserError("Only a published programme is retired.")
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired: %s" % _clean(reason))
        return True


class FixPartnerTier(models.Model):
    _name = "fix.partner.tier"
    _description = "Partner Programme Tier"
    _order = "programme_id, sequence, id"

    programme_id = fields.Many2one(
        "fix.partner.programme", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    criteria = fields.Text(required=True)
    benefits = fields.Text()
    commission_ref = fields.Char(string="Commission (M11 reference)")
    notice_days = fields.Integer(default=30)

    @api.constrains("notice_days")
    def _check_notice(self):
        for rec in self:
            if rec.notice_days < 0:
                raise ValidationError("A tier's notice period cannot be negative.")

    def _assert_programme_draft(self, programmes):
        if self.env.su:
            return
        for prog in programmes:
            if prog.state != "draft":
                raise UserError(
                    "Programme %s v%d is %s: its tiers change only in a new version "
                    "(BRU-PCM-12)." % (prog.code, prog.version, prog.state)
                )

    @api.model_create_multi
    def create(self, vals_list):
        progs = self.env["fix.partner.programme"].browse(
            [v.get("programme_id") for v in vals_list if v.get("programme_id")]
        )
        self._assert_programme_draft(progs)
        return super().create(vals_list)

    def write(self, vals):
        self._assert_programme_draft(self.mapped("programme_id"))
        if "programme_id" in vals:
            self._assert_programme_draft(
                self.env["fix.partner.programme"].browse(vals["programme_id"])
            )
        return super().write(vals)


# ================================================================ p1 contacts
class FixPartnerContactRole(models.Model):
    """FR-PCM-009: named contacts with their role and portal scope."""

    _name = "fix.partner.contact.role"
    _description = "Partner Contact Role"
    _inherit = ["mail.thread"]
    _order = "partner_id, role, primary desc, id"

    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    contact_id = fields.Many2one("res.partner", string="Contact Person", required=True)
    role = fields.Selection(
        [
            ("commercial", "Commercial"),
            ("technical", "Technical"),
            ("finance", "Finance"),
            ("escalation", "Escalation"),
        ],
        required=True,
    )
    portal_scope = fields.Selection(
        [("none", "No portal access"), ("view", "View own records"), ("submit", "View and submit")],
        required=True,
        default="none",
    )
    primary = fields.Boolean(string="Primary for this Role")
    email = fields.Char(related="contact_id.email", readonly=True)
    phone = fields.Char(related="contact_id.phone", readonly=True)
    active = fields.Boolean(default=True)

    @api.constrains("partner_id", "contact_id", "role", "primary", "active")
    def _check_unique_role(self):
        for rec in self.filtered("active"):
            same = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("partner_id", "=", rec.partner_id.id),
                    ("role", "=", rec.role),
                    ("active", "=", True),
                ]
            )
            if rec.contact_id in same.mapped("contact_id"):
                raise ValidationError(
                    "%s is already the %s contact of %s."
                    % (rec.contact_id.name, rec.role, rec.partner_id.name)
                )
            if rec.primary and same.filtered("primary"):
                raise ValidationError(
                    "%s already has a primary %s contact." % (rec.partner_id.name, rec.role)
                )
            if rec.contact_id == rec.partner_id.partner_id:
                raise ValidationError("Name a person, not the partner's own party record.")


# ============================================================== p2 onboarding
ONBOARDING_STEPS = [
    ("documents", "Statutory documents"),
    ("agreement", "Partner agreement (M08)"),
    ("training", "Training"),
    ("portal_access", "Portal access"),
    ("banking", "Banking details"),
    ("tax_registration", "Tax registration"),
    ("other", "Other"),
]


class FixPartnerOnboarding(models.Model):
    """FR-PCM-007, BRU-PCM-01: the onboarding checklist. A required step is
    completed on its evidence and never waived; the partner is onboarded only
    once every required step is done."""

    _name = "fix.partner.onboarding"
    _description = "Partner Onboarding Step"
    _inherit = ["fix.partner.capture.base"]
    _order = "partner_id, sequence, id"
    _OPEN_STATES = ("pending",)

    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    sequence = fields.Integer(default=10)
    step = fields.Selection(ONBOARDING_STEPS, required=True)
    name = fields.Char(string="Step Description", required=True)
    required = fields.Boolean(default=True)
    state = fields.Selection(
        [("pending", "Pending"), ("done", "Done"), ("waived", "Waived")],
        required=True,
        default="pending",
        tracking=True,
    )
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence", copy=False, ondelete="restrict"
    )
    note = fields.Char()
    completed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    completed_at = fields.Datetime(readonly=True, copy=False)
    waived_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    waive_reason = fields.Char(readonly=True, copy=False)

    _FROZEN = frozenset({"partner_id", "step", "name", "required", "evidence_attachment_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "completed_by_id",
            "completed_at",
            "waived_by_id",
            "waive_reason",
        }

    @api.constrains("partner_id", "step")
    def _check_one_per_step(self):
        for rec in self.filtered(lambda r: r.step != "other"):
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("partner_id", "=", rec.partner_id.id),
                    ("step", "=", rec.step),
                ]
            ):
                raise ValidationError(
                    "%s already has a '%s' step."
                    % (rec.partner_id.name, dict(ONBOARDING_STEPS)[rec.step])
                )

    @api.constrains("evidence_attachment_id")
    def _check_evidence_is_own(self):
        for rec in self:
            _assert_own_attachment(rec, "evidence_attachment_id")

    def action_complete(self):
        fix_require(self.env, [GROUP_OFFICER], "Completing an onboarding step")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending step is completed.")
            if not rec.evidence_attachment_id:
                raise ValidationError("Attach the evidence of step '%s' first." % rec.name)
            if rec.step == "agreement" and not rec.partner_id.contract_id:
                raise ValidationError(
                    "Link the partner agreement (M08) on the partner before completing this "
                    "step (FR-PCM-008)."
                )
            rec._guarded().write(
                {
                    "state": "done",
                    "completed_by_id": self.env.uid,
                    "completed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_waive(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Waiving an onboarding step")
        reason = _clean(reason)
        if not reason:
            raise UserError("State why the step is waived.")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Only a pending step is waived.")
            if rec.required:
                raise UserError(
                    "Step '%s' is required: it is completed, never waived (BRU-PCM-01)." % rec.name
                )
            fix_not_creator(self.env, rec, "waiving it")
            rec._guarded().write(
                {"state": "waived", "waived_by_id": self.env.uid, "waive_reason": reason}
            )
        return True


class FixPartnerEnablement(models.Model):
    """FR-PCM-041: training and certification, gating programme benefits."""

    _name = "fix.partner.enablement"
    _description = "Partner Enablement & Certification"
    _inherit = ["fix.partner.capture.base"]
    _order = "partner_id, expires_on, id"
    _OPEN_STATES = ("assigned",)

    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    course = fields.Char(required=True)
    required = fields.Boolean(
        default=True, help="A required certification gates the partner's rebates and MDF."
    )
    assigned_on = fields.Date(default=fields.Date.context_today, required=True)
    completed_on = fields.Date()
    certification_ref = fields.Char()
    certificate_attachment_id = fields.Many2one(
        "ir.attachment", string="Certificate", copy=False, ondelete="restrict"
    )
    expires_on = fields.Date()
    state = fields.Selection(
        [("assigned", "Assigned"), ("certified", "Certified"), ("expired", "Expired")],
        required=True,
        default="assigned",
        tracking=True,
    )
    certified_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _FROZEN = frozenset(
        {
            "partner_id",
            "course",
            "required",
            "completed_on",
            "certification_ref",
            "certificate_attachment_id",
            "expires_on",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "certified_by_id"}

    @api.constrains("completed_on", "expires_on", "assigned_on")
    def _check_dates(self):
        for rec in self:
            if rec.expires_on and rec.completed_on and rec.expires_on < rec.completed_on:
                raise ValidationError("A certification expires after it is earned.")

    @api.constrains("certificate_attachment_id")
    def _check_certificate_is_own(self):
        for rec in self:
            _assert_own_attachment(rec, "certificate_attachment_id")

    def action_certify(self):
        fix_require(self.env, [GROUP_OFFICER], "Recording a partner certification")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "assigned":
                raise UserError("Only an assigned course is certified.")
            if not rec.completed_on or not rec.certificate_attachment_id:
                raise ValidationError(
                    "Record the completion date and attach the certificate of %s." % rec.course
                )
            if rec.completed_on > today:
                raise ValidationError("A course is not completed in the future.")
            if rec.expires_on and rec.expires_on < today:
                raise ValidationError("Certificate of %s has already expired." % rec.course)
            rec._guarded().write({"state": "certified", "certified_by_id": self.env.uid})
        return True

    @api.model
    def cron_enablement_expiry(self):
        today = fields.Date.context_today(self)
        lapsed = self.sudo().search(
            [("state", "=", "certified"), ("expires_on", "!=", False), ("expires_on", "<", today)]
        )
        if lapsed:
            lapsed._guarded().write({"state": "expired"})
            for rec in lapsed:
                rec.message_post(body="Certification expired on %s." % rec.expires_on)
        return len(lapsed)


# ========================================================= p3 brand relations
class FixBrandObligation(models.Model):
    """FR-PCM-017: an obligation under a brand authorisation, met on its
    evidence, with a recurring one re-raised for its next due date."""

    _name = "fix.brand.obligation"
    _description = "Brand Authorisation Obligation"
    _inherit = ["fix.partner.capture.base"]
    _order = "due_date, id"
    _OPEN_STATES = ("open", "overdue")

    authorisation_id = fields.Many2one(
        "fix.partner.authorisation", required=True, ondelete="cascade", index=True
    )
    partner_id = fields.Many2one(
        related="authorisation_id.partner_id", store=True, index=True, readonly=True
    )
    brand_id = fields.Many2one(related="authorisation_id.brand_id", store=True, readonly=True)
    obligation_type = fields.Selection(
        [
            ("tooling", "Tooling"),
            ("training", "Training"),
            ("facility", "Facility standard"),
            ("reporting", "Reporting"),
            ("stock", "Stock holding"),
            ("other", "Other"),
        ],
        required=True,
    )
    description = fields.Text(required=True)
    due_date = fields.Date(required=True)
    recurrence = fields.Selection(
        [
            ("none", "One-off"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
        required=True,
        default="none",
    )
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence", copy=False, ondelete="restrict"
    )
    state = fields.Selection(
        [("open", "Open"), ("overdue", "Overdue"), ("met", "Met")],
        required=True,
        default="open",
        tracking=True,
    )
    met_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    met_at = fields.Datetime(readonly=True, copy=False)

    _FROZEN = frozenset()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "met_by_id", "met_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state == "met":
            locked |= {
                "authorisation_id",
                "obligation_type",
                "description",
                "due_date",
                "recurrence",
                "evidence_attachment_id",
            }
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state == "met"):
                _refuse_changes(
                    rec,
                    vals,
                    rec._fix_form_locked_fields() - rec._fix_guarded_fields(),
                    "it is met",
                )
        return super().write(vals)

    @api.constrains("evidence_attachment_id")
    def _check_evidence_is_own(self):
        for rec in self:
            _assert_own_attachment(rec, "evidence_attachment_id")

    _STEP = {"monthly": 1, "quarterly": 3, "annual": 12}

    def action_mark_met(self):
        fix_require(self.env, [GROUP_OFFICER], "Recording an obligation as met")
        for rec in self:
            if rec.state not in ("open", "overdue"):
                raise UserError("Only an open obligation is met.")
            if not rec.evidence_attachment_id:
                raise ValidationError("Attach the evidence that the obligation is met.")
            rec._guarded().write(
                {"state": "met", "met_by_id": self.env.uid, "met_at": fields.Datetime.now()}
            )
            months = self._STEP.get(rec.recurrence)
            if months and rec.authorisation_id.state == "active":
                from dateutil.relativedelta import relativedelta

                rec.sudo().copy(
                    {
                        "due_date": rec.due_date + relativedelta(months=months),
                        "evidence_attachment_id": False,
                        "state": "open",
                    }
                )
        return True

    @api.model
    def cron_obligation_overdue(self):
        today = fields.Date.context_today(self)
        late = self.sudo().search([("state", "=", "open"), ("due_date", "<", today)])
        if late:
            late._guarded().write({"state": "overdue"})
            for rec in late:
                rec.authorisation_id.message_post(
                    body="Obligation overdue since %s: %s" % (rec.due_date, rec.description)
                )
        return len(late)


class FixBrandAudit(models.Model):
    """FR-PCM-016: the brand partner audit calendar - scheduled, conducted
    (findings), responded, closed by a manager who did not schedule it."""

    _name = "fix.brand.audit"
    _description = "Brand Partner Audit"
    _inherit = ["fix.partner.capture.base"]
    _order = "scheduled_on desc, id desc"
    _OPEN_STATES = ("scheduled",)

    name = fields.Char(required=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    authorisation_id = fields.Many2one(
        "fix.partner.authorisation", string="Authorisation Audited", ondelete="set null"
    )
    scheduled_on = fields.Date(required=True)
    scope = fields.Text(required=True)
    auditor_name = fields.Char(string="Brand Auditor")
    conducted_on = fields.Date()
    findings = fields.Text()
    response = fields.Text(string="1000FiX Response")
    m23_ref = fields.Char(string="Quality Finding (M23) Reference")
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("conducted", "Findings Recorded"),
            ("responded", "Responded"),
            ("closed", "Closed"),
        ],
        required=True,
        default="scheduled",
        tracking=True,
    )
    closed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    closed_on = fields.Date(readonly=True, copy=False)

    _FROZEN = frozenset(
        {"brand_id", "authorisation_id", "scheduled_on", "scope", "conducted_on", "findings"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "closed_by_id", "closed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state in ("responded", "closed"):
            locked |= {"response", "m23_ref", "auditor_name"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state in ("responded", "closed")):
                _refuse_changes(
                    rec, vals, {"response", "m23_ref", "auditor_name"}, "it is %s" % rec.state
                )
        return super().write(vals)

    @api.constrains("authorisation_id", "brand_id")
    def _check_authorisation_brand(self):
        for rec in self.filtered("authorisation_id"):
            if rec.authorisation_id.brand_id and rec.authorisation_id.brand_id != rec.brand_id:
                raise ValidationError(
                    "Authorisation %s is not of brand %s."
                    % (rec.authorisation_id.name, rec.brand_id.display_name)
                )

    def action_record_findings(self):
        fix_require(self.env, [GROUP_OFFICER], "Recording brand audit findings")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "scheduled":
                raise UserError("Findings are recorded on a scheduled audit.")
            if not rec.conducted_on or not (rec.findings or "").strip():
                raise ValidationError("Record the date conducted and the brand's findings.")
            if rec.conducted_on > today:
                raise ValidationError("An audit is not conducted in the future.")
            rec._guarded().write({"state": "conducted"})
        return True

    def action_respond(self):
        fix_require(self.env, [GROUP_OFFICER], "Responding to brand audit findings")
        for rec in self:
            if rec.state != "conducted":
                raise UserError("A response follows the recorded findings.")
            if not (rec.response or "").strip():
                raise ValidationError("Write 1000FiX's response to the findings.")
            rec._guarded().write({"state": "responded"})
        return True

    def action_close(self):
        fix_require(self.env, [GROUP_MANAGER], "Closing a brand audit")
        for rec in self:
            if rec.state != "responded":
                raise UserError("An audit closes once its findings are responded to.")
            fix_not_creator(self.env, rec, "closing it")
            rec._guarded().write(
                {
                    "state": "closed",
                    "closed_by_id": self.env.uid,
                    "closed_on": fields.Date.context_today(rec),
                }
            )
        return True


class FixPartnerEngagement(models.Model):
    """FR-PCM-020/021, BRU-PCM-20: the engagement log - append-only, so a
    brand's own assessment of 1000FiX stays verbatim."""

    _name = "fix.partner.engagement"
    _description = "Partner Engagement Log"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "date desc, id desc"

    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    engagement_type = fields.Selection(
        [
            ("meeting", "Meeting"),
            ("bulletin", "Bulletin"),
            ("technical_notice", "Technical notice"),
            ("escalation", "Escalation"),
            ("commitment", "Commitment"),
            ("brand_assessment", "Brand's assessment of 1000FiX"),
        ],
        required=True,
    )
    direction = fields.Selection(
        [("inbound", "From the partner"), ("outbound", "From 1000FiX")],
        required=True,
        default="outbound",
    )
    date = fields.Date(required=True, default=fields.Date.context_today)
    participants = fields.Char()
    summary = fields.Text(required=True)
    commitments = fields.Text()
    commitment_due = fields.Date()
    attachment_id = fields.Many2one("ir.attachment", string="Document", ondelete="restrict")
    logged_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, copy=False
    )

    _LOCKED = frozenset(
        {
            "partner_id",
            "engagement_type",
            "direction",
            "date",
            "participants",
            "summary",
            "commitments",
            "commitment_due",
            "logged_by_id",
        }
    )

    @api.constrains("engagement_type", "direction")
    def _check_assessment_inbound(self):
        for rec in self:
            if rec.engagement_type == "brand_assessment" and rec.direction != "inbound":
                raise ValidationError("A brand's assessment comes from the brand (inbound).")

    def _fix_form_locked_fields(self) -> set:
        return set(self._LOCKED) if self[:1] else {"logged_by_id"}

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            for vals in vals_list:
                vals.pop("logged_by_id", None)
        return super().create(vals_list)

    def write(self, vals):
        if self and not self.env.su:
            for rec in self:
                _refuse_changes(
                    rec, vals, self._LOCKED, "the engagement log is append-only (BRU-PCM-20)"
                )
        return super().write(vals)


# =============================================================== p4 alliances
class FixAllianceScheme(models.Model):
    """FR-PCM-030/032, BRU-PCM-19: an alliance scheme. The benefit is applied
    by an M11 rule the scheme names, never as an ad-hoc discount."""

    _name = "fix.alliance.scheme"
    _description = "Alliance Scheme"
    _inherit = ["fix.partner.capture.base"]
    _order = "valid_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    partner_id = fields.Many2one(
        "fix.partner",
        string="Alliance Partner",
        required=True,
        ondelete="restrict",
        domain="[('partner_type', '=', 'alliance')]",
    )
    member_definition = fields.Text(required=True)
    eligibility_method = fields.Selection(
        [
            ("member_id", "Member ID"),
            ("corporate_email", "Corporate e-mail domain"),
            ("member_list", "Member list"),
            ("partner_api", "Partner API"),
        ],
        required=True,
    )
    benefit_description = fields.Text(required=True)
    # A04 ERP audit M40-F28: the benefit was a typed reference nobody read.
    # It is now the M11 promotion that applies it. A promotion an alliance
    # scheme names is member-only: price_for grants it only under an eligible
    # check of the scheme (fix.alliance.eligibility.check.price_for).
    benefit_promotion_id = fields.Many2one(
        "fix.promotion",
        string="M11 Benefit Promotion",
        ondelete="restrict",
        index=True,
        domain="[('company_id', '=', company_id)]",
        help="The M11 promotion that applies the benefit (BRU-PCM-19): released by pricing, "
        "granted only to members validated by an eligibility check.",
    )
    benefit_ref = fields.Char(
        string="M11 Benefit Rule", related="benefit_promotion_id.code", readonly=True
    )
    volume_commitment = fields.Integer(string="Committed Volume (jobs)")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    check_ids = fields.One2many("fix.alliance.eligibility.check", "scheme_id")
    eligible_count = fields.Integer(compute="_compute_volume", string="Eligible Members Served")
    commitment_pct = fields.Float(compute="_compute_volume", string="Commitment Achieved (%)")

    _FROZEN = frozenset(
        {
            "company_id",
            "code",
            "partner_id",
            "member_definition",
            "eligibility_method",
            "benefit_description",
            "benefit_promotion_id",
            "volume_commitment",
            "valid_from",
        }
    )
    _code_unique = models.Constraint("UNIQUE (code)", "An alliance scheme code is unique.")

    @api.constrains("benefit_promotion_id", "company_id")
    def _check_benefit_promotion(self):
        """A promotion becomes member-only once a scheme names it, so a scheme
        may not take over one the public already used (that would withdraw a
        released public discount through the back door), nor one of another
        company."""
        for rec in self.filtered("benefit_promotion_id"):
            promo = rec.benefit_promotion_id.sudo()
            if promo.company_id != rec.company_id:
                raise ValidationError(
                    "Promotion %s belongs to %s, not to %s."
                    % (promo.code, promo.company_id.name, rec.company_id.name)
                )
            shared = promo.with_context(active_test=False).alliance_scheme_ids - rec
            if promo.use_count and not shared:
                raise ValidationError(
                    "Promotion %s has already been used %d time(s) as a public discount: an "
                    "alliance benefit is its own member-only M11 promotion (BRU-PCM-19)."
                    % (promo.code, promo.use_count)
                )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "activated_by_id"}

    @api.depends("check_ids.result", "volume_commitment")
    def _compute_volume(self):
        for rec in self:
            n = len(rec.check_ids.filtered(lambda c: c.result == "eligible"))
            rec.eligible_count = n
            rec.commitment_pct = (
                (100.0 * n / rec.volume_commitment) if rec.volume_commitment else 0.0
            )

    @api.constrains("valid_from", "valid_to", "volume_commitment")
    def _check_terms(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("Scheme %s ends before it starts." % rec.name)
            if rec.volume_commitment < 0:
                raise ValidationError("A volume commitment cannot be negative.")

    def action_activate(self):
        fix_require(self.env, [GROUP_MANAGER], "Activating an alliance scheme")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft scheme is activated.")
            fix_not_creator(self.env, rec, "activating it")
            if rec.partner_id.partner_type != "alliance" or rec.partner_id.state != "onboarded":
                raise ValidationError(
                    "%s must be an onboarded alliance partner (BRU-PCM-01)." % rec.partner_id.name
                )
            promo = rec.benefit_promotion_id.sudo()
            if not promo:
                raise ValidationError(
                    "Name the M11 promotion that applies the benefit: alliance benefits are never "
                    "ad-hoc discounts (BRU-PCM-19)."
                )
            if promo.state not in ("approved", "active"):
                raise ValidationError(
                    "Promotion %s is %s: pricing releases it (M11, M63) before the scheme that "
                    "grants it is activated." % (promo.code, promo.state)
                )
            rec._guarded().write({"state": "active", "activated_by_id": self.env.uid})
        return True

    def action_close(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Closing an alliance scheme")
        if not _clean(reason):
            raise UserError("State why the scheme is closed.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active scheme is closed.")
            rec._guarded().write({"state": "closed"})
            rec.message_post(body="Closed: %s" % _clean(reason))
        return True


class FixAllianceEligibilityCheck(models.Model):
    """FR-PCM-031: the validation of a member at intake - an immutable log
    entry, possible only under an active scheme inside its validity."""

    _name = "fix.alliance.eligibility.check"
    _description = "Alliance Eligibility Check"
    _inherit = ["fix.guarded.mixin"]
    _order = "checked_at desc, id desc"

    scheme_id = fields.Many2one(
        "fix.alliance.scheme",
        required=True,
        ondelete="restrict",
        index=True,
        domain="[('state', '=', 'active')]",
    )
    customer_id = fields.Many2one("res.partner", string="Customer")
    member_ref = fields.Char(string="Member ID / Proof", required=True)
    result = fields.Selection(
        [("eligible", "Eligible"), ("not_eligible", "Not eligible")], required=True
    )
    evidence_ref = fields.Char(string="How It Was Validated", required=True)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Evidence", ondelete="restrict"
    )
    checked_at = fields.Datetime(readonly=True, default=fields.Datetime.now, copy=False)
    checked_by_id = fields.Many2one(
        "res.users", readonly=True, default=lambda self: self.env.user, copy=False
    )

    _LOCKED = frozenset(
        {
            "scheme_id",
            "customer_id",
            "member_ref",
            "result",
            "evidence_ref",
            "checked_at",
            "checked_by_id",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        return set(self._LOCKED) if self[:1] else {"checked_at", "checked_by_id"}

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.context_today(self)
        for vals in vals_list:
            if not self.env.su:
                vals.pop("checked_at", None)
                vals.pop("checked_by_id", None)
            scheme = self.env["fix.alliance.scheme"].sudo().browse(vals.get("scheme_id"))
            if not scheme or scheme.state != "active":
                raise ValidationError("Only an active alliance scheme validates members.")
            if scheme.valid_from > today or (scheme.valid_to and scheme.valid_to < today):
                raise ValidationError(
                    "Scheme %s is outside its validity: it validates no-one today." % scheme.name
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self.env.su:
            for rec in self:
                _refuse_changes(rec, vals, self._LOCKED, "an eligibility check is a log entry")
        return super().write(vals)

    # ---- A04 ERP audit M40-F28: the check grants the M11 benefit -----------
    def _fix_grants_benefit(self, partner=None, on_date=None):
        """'' when this check grants its scheme's M11 promotion to `partner`
        on `on_date`, else why not. A check grants only when it found the
        member eligible, names the customer it validated (the benefit is that
        customer's), and its scheme is active and in force that day."""
        self.ensure_one()
        check = self.sudo()
        scheme = check.scheme_id
        day = on_date or fields.Date.context_today(self)
        if check.result != "eligible":
            return "check %s found the member not eligible" % check.member_ref
        if not check.customer_id:
            return "check %s names no customer, so its benefit is nobody's" % check.member_ref
        if partner is not None and (
            not partner or partner.commercial_partner_id != check.customer_id.commercial_partner_id
        ):
            return "check %s validated %s, not this customer" % (
                check.member_ref,
                check.customer_id.display_name,
            )
        if scheme.state != "active" or not scheme.benefit_promotion_id:
            return "scheme %s is %s" % (scheme.name, scheme.state)
        if scheme.valid_from > day or (scheme.valid_to and scheme.valid_to < day):
            return "scheme %s is not in force on %s" % (scheme.name, day)
        return ""

    def price_for(self, product, partner=None, channel="service", **kwargs):
        """The M11 price of `product` for the validated member, with the
        scheme's benefit promotion granted (fix.rate.card.price_for under this
        check). Refused when the check grants nothing."""
        self.ensure_one()
        partner = partner or self.sudo().customer_id
        day = fields.Date.to_date(kwargs["date"]) if kwargs.get("date") else None
        why = self._fix_grants_benefit(partner, day)
        if why:
            raise UserError("No alliance benefit: %s (BRU-PCM-19)." % why)
        return (
            self.env["fix.rate.card"]
            .with_context(**{ALLIANCE_CHECK_CTX: self.id})
            .price_for(product, partner=partner, channel=channel, **kwargs)
        )


# =============================================================== p5 referrals
class FixReferralLink(models.Model):
    """FR-PCM-022, T-07: a non-guessable, revocable referral code."""

    _name = "fix.referral.link"
    _description = "Referral Link / Code"
    _inherit = ["fix.partner.capture.base"]
    _order = "id desc"
    _OPEN_STATES = ("active",)

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    campaign_ref = fields.Char(string="Campaign")
    code = fields.Char(readonly=True, copy=False, index=True)
    url_path = fields.Char(compute="_compute_url_path", string="Link Path")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked")],
        required=True,
        default="active",
        tracking=True,
    )
    revoked_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    revoke_reason = fields.Char(readonly=True, copy=False)
    lead_count = fields.Integer(compute="_compute_lead_count", string="Leads")

    _FROZEN = frozenset({"partner_id", "campaign_ref", "valid_from", "valid_to", "company_id"})
    _code_unique = models.Constraint("UNIQUE (code)", "A referral code is unique.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "code", "revoked_by_id", "revoke_reason"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1]:
            locked |= {"partner_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                _refuse_changes(rec, vals, {"partner_id"}, "a code belongs to one partner")
        return super().write(vals)

    @api.depends("code")
    def _compute_url_path(self):
        for rec in self:
            rec.url_path = "/r/%s" % rec.code if rec.code else False

    def _compute_lead_count(self):
        data = (
            self.env["fix.partner.lead"]
            .sudo()
            ._read_group([("link_id", "in", self.ids)], ["link_id"], ["__count"])
        )
        counts = {link.id: n for link, n in data}
        for rec in self:
            rec.lead_count = counts.get(rec.id, 0)

    @api.constrains("valid_from", "valid_to")
    def _check_dates(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("A referral link ends after it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        fix_require(self.env, [GROUP_OFFICER], "Issuing a referral link")
        for vals in vals_list:
            partner = self.env["fix.partner"].sudo().browse(vals.get("partner_id"))
            if partner and partner.state not in EARNING_STATES:
                raise ValidationError(
                    "%s is %s: only an onboarded partner refers (BRU-PCM-01)."
                    % (partner.name, partner.state)
                )
        recs = super().create(vals_list)
        for rec in recs:
            prefix = re.sub(r"[^A-Z0-9]", "", (rec.partner_id.name or "P").upper())[:4] or "P"
            # hex: no "-" inside the random part (token_urlsafe's could split it)
            rec._guarded().write({"code": "%s-%s" % (prefix, secrets.token_hex(8))})
        return recs

    def _is_live(self, day=None):
        self.ensure_one()
        day = day or fields.Date.context_today(self)
        return (
            self.state == "active"
            and self.valid_from <= day
            and (not self.valid_to or self.valid_to >= day)
        )

    def action_revoke(self, reason=None):
        fix_require(self.env, [GROUP_OFFICER], "Revoking a referral link")
        reason = _clean(reason)
        if not reason:
            raise UserError("State why the link is revoked.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active link is revoked.")
            rec._guarded().write(
                {"state": "revoked", "revoked_by_id": self.env.uid, "revoke_reason": reason}
            )
        return True


class FixPartnerLead(models.Model):
    """FR-PCM-023/024/026, BRU-PCM-04/05/06: a lead a partner submits. It is
    created only on the customer's recorded consent; its attribution is
    written at creation and never changes; converted outside its window it
    attributes to no partner, inside it raises the commission referral."""

    _name = "fix.partner.lead"
    _description = "Partner-Submitted Lead"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    partner_id = fields.Many2one(
        "fix.partner", string="Referring Partner", required=True, index=True
    )
    link_id = fields.Many2one(
        "fix.referral.link", string="Referral Link", domain="[('partner_id', '=', partner_id)]"
    )
    customer_name = fields.Char(required=True)
    customer_phone = fields.Char(required=True)
    customer_email = fields.Char()
    customer_id = fields.Many2one("res.partner", string="Customer (M33)")
    service_interest = fields.Char(string="Service Interest")
    consent_given = fields.Boolean(string="Customer Consent Recorded")
    consent_method = fields.Selection(
        [
            ("written", "Written form"),
            ("digital", "Digital (OTP / click)"),
            ("recorded_call", "Recorded call"),
        ]
    )
    consent_at = fields.Datetime(string="Consent Given At")
    consent_attachment_id = fields.Many2one(
        "ir.attachment", string="Consent Evidence", ondelete="restrict"
    )
    attributed_at = fields.Datetime(readonly=True, copy=False)
    attribution_window_days = fields.Integer(readonly=True, copy=False)
    attribution_expires_on = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("submitted", "Submitted"),
            ("qualified", "Qualified"),
            ("converted", "Converted"),
            ("lost", "Lost"),
        ],
        required=True,
        default="submitted",
        tracking=True,
    )
    converted_at = fields.Datetime(readonly=True, copy=False)
    attribution_lapsed = fields.Boolean(readonly=True, copy=False)
    referral_id = fields.Many2one("fix.referral", readonly=True, copy=False)
    loss_reason = fields.Char(readonly=True, copy=False)
    # A04 ERP audit M40-F23: the M07 lead / opportunity the qualified lead is
    # handed to 1000FiX sales as, carrying the partner attribution.
    opportunity_id = fields.Many2one(
        "crm.lead", string="M07 Lead / Opportunity (hand-off)", readonly=True, copy=False
    )

    _ATTRIBUTION = frozenset(
        {
            "partner_id",
            "link_id",
            "consent_given",
            "consent_method",
            "consent_at",
            "consent_attachment_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "attributed_at",
            "attribution_window_days",
            "attribution_expires_on",
            "converted_at",
            "attribution_lapsed",
            "referral_id",
            "loss_reason",
            "opportunity_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec:
            locked |= set(self._ATTRIBUTION)
            if rec.state in ("converted", "lost"):
                locked |= {
                    "customer_name",
                    "customer_phone",
                    "customer_email",
                    "customer_id",
                    "service_interest",
                }
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                _refuse_changes(
                    rec,
                    vals,
                    rec._fix_form_locked_fields() - rec._fix_guarded_fields(),
                    "attribution and consent are written once, at submission (BRU-PCM-04)",
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # who may capture a lead is answered before what a lead needs
        self.check_access("create")
        today = fields.Date.context_today(self)
        days = attribution_days(self.env)
        for vals in vals_list:
            # BRU-PCM-06: no consent, no record - checked before the insert
            if not vals.get("consent_given") or not vals.get("consent_method"):
                raise ValidationError(
                    "Record the customer's consent and how it was given before the lead is "
                    "created (BRU-PCM-06, PDPA)."
                )
            partner = self.env["fix.partner"].sudo().browse(vals.get("partner_id"))
            if not partner or partner.state not in EARNING_STATES:
                raise ValidationError("Only an onboarded partner submits leads (BRU-PCM-01).")
            if vals.get("link_id"):
                link = self.env["fix.referral.link"].sudo().browse(vals["link_id"])
                if link.partner_id != partner:
                    raise ValidationError(
                        "Referral link %s is not %s's." % (link.code, partner.name)
                    )
                if not link._is_live(today):
                    raise ValidationError("Referral link %s is not live." % link.code)
            vals.setdefault("consent_at", fields.Datetime.now())
        recs = super().create(vals_list)
        seq = self.env["ir.sequence"].sudo()
        for rec in recs:
            rec._guarded().write(
                {
                    "name": seq.next_by_code("fix.partner.lead") or "LEAD/%d" % rec.id,
                    "attributed_at": fields.Datetime.now(),
                    "attribution_window_days": days,
                    "attribution_expires_on": today + timedelta(days=days),
                }
            )
        return recs

    def action_qualify(self):
        fix_require(self.env, [GROUP_OFFICER], "Qualifying a partner lead")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted lead is qualified.")
            rec._guarded().write({"state": "qualified"})
            rec._fix_handoff_opportunity()
        return True

    def _fix_handoff_opportunity(self):
        """A04 ERP audit M40-F23 (FR-PCM-023, M07 hand-off): a qualified
        partner lead becomes an M07 record for 1000FiX sales - an opportunity
        on the customer's party when the lead names one, else a lead carrying
        the contact the partner gave (M07 matches it to a party before it
        converts, BRU-CRM-02). The partner attribution is written on it and
        guarded. Idempotent."""
        self.ensure_one()
        if self.opportunity_id or "crm.lead" not in self.env:
            return self.opportunity_id
        Opp = self.env["crm.lead"].sudo().with_company(self.company_id)
        opp = Opp.search([("fix_partner_lead_id", "=", self.id)], limit=1)
        if not opp:
            vals = {
                "name": "%s - %s" % (self.name, self.customer_name),
                "type": "opportunity" if self.customer_id else "lead",
                "contact_name": self.customer_name,
                "phone": self.customer_phone,
                "email_from": self.customer_email or False,
                "company_id": self.company_id.id,
                "lead_source": "referral",
                "fix_partner_id": self.partner_id.id,
                "fix_partner_lead_id": self.id,
                "description": self.service_interest or False,
            }
            if self.customer_id:
                vals["partner_id"] = self.customer_id.id
            opp = Opp.create(vals)
        self._guarded().write({"opportunity_id": opp.id})
        self.message_post(body="Handed to M07 sales as %s %s." % (opp.type, opp.name))
        return opp

    def action_convert(self):
        """The customer bought. Inside the window the referring partner is
        credited through a referral (M53 pays it); outside, nobody is."""
        fix_require(self.env, [GROUP_OFFICER], "Converting a partner lead")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "qualified":
                raise UserError("Qualify the lead before converting it.")
            if not rec.customer_id:
                raise ValidationError("Link the customer's party record (M33) first.")
            vals = {"state": "converted", "converted_at": fields.Datetime.now()}
            if rec.attribution_expires_on and today > rec.attribution_expires_on:
                vals["attribution_lapsed"] = True
                rec.message_post(
                    body="Converted after the attribution window closed on %s: no partner is "
                    "credited (BRU-PCM-05)." % rec.attribution_expires_on
                )
            elif rec.partner_id.state not in EARNING_STATES:
                # A04 ERP audit M40-F9: a partner that left good standing
                # since the lead is credited nothing.
                vals["attribution_lapsed"] = True
                rec.message_post(
                    body="Converted while partner %s is %s: no partner is credited (BRU-PCM-01)."
                    % (rec.partner_id.name, rec.partner_id.state)
                )
            else:
                # the referral carries the lead's consent and the date the
                # lead was attributed (the window runs from it); its name is
                # what the partner typed, never the party master's (M40-F8)
                referral = (
                    self.env["fix.referral"]
                    .sudo()
                    .create(
                        {
                            "name": "%s - %s" % (rec.name, rec.customer_name),
                            "partner_id": rec.partner_id.id,
                            "referred_partner_id": rec.customer_id.id,
                            "company_id": rec.company_id.id,
                            "referred_on": dhaka_day(rec.attributed_at),
                            "consent_given": rec.consent_given,
                            "consent_method": rec.consent_method,
                            "consent_at": rec.consent_at,
                        }
                    )
                )
                vals["referral_id"] = referral.id
            rec._guarded().write(vals)
        return True

    def action_mark_lost(self, reason=None):
        fix_require(self.env, [GROUP_OFFICER], "Closing a partner lead as lost")
        reason = _clean(reason)
        if not reason:
            raise UserError("Give the reason the lead was lost: the partner sees it (FR-PCM-026).")
        for rec in self:
            if rec.state not in ("submitted", "qualified"):
                raise UserError("Only an open lead is lost.")
            rec._guarded().write({"state": "lost", "loss_reason": reason})
        return True


# ======================================================= p6 channel precedence
CHANNELS = [
    ("direct", "Direct sales"),
    ("franchise", "Franchise territory"),
    ("reseller", "Reseller"),
    ("referral", "Referral / alliance partner"),
    ("marketplace", "Marketplace"),
]


class FixChannelConflictRule(models.Model):
    """FR-PCM-029, BRU-PCM-10: the declared precedence between channels, by
    territory. Activated by a Tier 3 officer (CCO) who did not draft it; one
    active rule per territory."""

    _name = "fix.channel.conflict.rule"
    _description = "Channel Precedence Rule"
    _inherit = ["fix.partner.capture.base"]
    _order = "territory, valid_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    scope = fields.Text(required=True, help="Which deals and customers the rule governs.")
    territory = fields.Char(help="Blank = the whole country.")
    first_channel = fields.Selection(CHANNELS, string="1st Precedence", required=True)
    second_channel = fields.Selection(CHANNELS, string="2nd Precedence", required=True)
    third_channel = fields.Selection(CHANNELS, string="3rd Precedence")
    fourth_channel = fields.Selection(CHANNELS, string="4th Precedence")
    fifth_channel = fields.Selection(CHANNELS, string="5th Precedence")
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    precedence = fields.Char(compute="_compute_precedence")

    _FROZEN = frozenset(
        {
            "company_id",
            "name",
            "scope",
            "territory",
            "first_channel",
            "second_channel",
            "third_channel",
            "fourth_channel",
            "fifth_channel",
            "valid_from",
        }
    )
    _ORDER_FIELDS = (
        "first_channel",
        "second_channel",
        "third_channel",
        "fourth_channel",
        "fifth_channel",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id"}

    @api.depends(*_ORDER_FIELDS)
    def _compute_precedence(self):
        labels = dict(CHANNELS)
        for rec in self:
            rec.precedence = " > ".join(labels[rec[f]] for f in self._ORDER_FIELDS if rec[f])

    @api.constrains(*_ORDER_FIELDS)
    def _check_distinct(self):
        for rec in self:
            chosen = [rec[f] for f in self._ORDER_FIELDS if rec[f]]
            if len(chosen) != len(set(chosen)):
                raise ValidationError("A channel appears once in the precedence order.")

    def action_activate(self):
        fix_require(self.env, [GROUP_TIER3], "Activating a channel precedence rule (CCO)")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft rule is activated.")
            fix_not_creator(self.env, rec, "activating it")
            same = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "active"),
                    ("company_id", "=", rec.company_id.id),
                    ("territory", "=", rec.territory or False),
                ]
            )
            if same:
                same._guarded().write({"state": "retired"})
                for old in same:
                    old.message_post(body="Superseded by rule %s." % rec.name)
            rec._guarded().write({"state": "active", "approved_by_id": self.env.uid})
        return True

    def action_retire(self, reason=None):
        fix_require(self.env, [GROUP_TIER3], "Retiring a channel precedence rule (CCO)")
        if not _clean(reason):
            raise UserError("State why the rule is retired.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active rule is retired.")
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired: %s" % _clean(reason))
        return True


# =============================================================== p7 resellers
class FixResellerAllocation(models.Model):
    """FR-PCM-033: stock or service capacity allocated to a reseller, and
    what the reseller has drawn against it."""

    _name = "fix.reseller.allocation"
    _description = "Reseller Allocation"
    _inherit = ["fix.partner.capture.base"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    partner_id = fields.Many2one(
        "fix.partner",
        string="Reseller",
        required=True,
        index=True,
        domain="[('partner_type', '=', 'reseller')]",
    )
    allocation_type = fields.Selection(
        [("stock", "Refurbished stock"), ("capacity", "Service capacity")],
        required=True,
        default="stock",
    )
    item_description = fields.Char(required=True)
    item_ref = fields.Char(string="Item / Lot Reference (M14/M15)")
    # A04 ERP audit M40-F16: the item priced by M11 and moved by a draw.
    product_id = fields.Many2one(
        "product.product", string="Item (M37/M11)", ondelete="restrict", index=True
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Draw From (M15 location)",
        domain="[('usage', '=', 'internal')]",
        help="The stock location a refurbished-stock draw leaves from.",
    )
    qty = fields.Float(string="Allocated Quantity", required=True)
    consumed_qty = fields.Float(string="Drawn", readonly=True, copy=False)
    remaining_qty = fields.Float(compute="_compute_remaining", string="Remaining")
    period = fields.Char(required=True)
    unit_price = fields.Monetary(
        currency_field="currency_id",
        string="Agreed Unit Price",
        readonly=True,
        copy=False,
        help="The M11 reseller price (price_for channel 'reseller'), VAT exclusive, set when "
        "the allocation is made - never typed.",
    )
    price_source = fields.Char(string="Price Source (M11)", readonly=True, copy=False)
    draw_ids = fields.One2many("fix.reseller.draw", "allocation_id", string="Draws")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("allocated", "Allocated"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    allocated_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _FROZEN = frozenset(
        {
            "company_id",
            "partner_id",
            "allocation_type",
            "item_description",
            "item_ref",
            "product_id",
            "location_id",
            "qty",
            "period",
            "currency_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "consumed_qty",
            "allocated_by_id",
            "unit_price",
            "price_source",
        }

    @api.depends("qty", "consumed_qty")
    def _compute_remaining(self):
        for rec in self:
            rec.remaining_qty = (rec.qty or 0.0) - (rec.consumed_qty or 0.0)

    @api.constrains("qty", "unit_price")
    def _check_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError("An allocation is of a positive quantity.")
            if (rec.unit_price or 0.0) < 0:
                raise ValidationError("A unit price cannot be negative.")

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.reseller.allocation")
                    or "RAL/%d" % rec.id
                }
            )
        return recs

    def _fix_m11_price(self):
        """A04 ERP audit M40-F16: the reseller price is M11's (price_for,
        channel 'reseller'), never a typed figure. None = no released price."""
        self.ensure_one()
        if not self.product_id:
            raise ValidationError(
                "Name the item of allocation %s: the reseller price is M11's for that item."
                % self.name
            )
        quote = (
            self.env["fix.rate.card"]
            .sudo()
            .price_for(
                self.product_id,
                partner=self.partner_id.partner_id,
                channel="reseller",
                qty=self.qty,
                date=fields.Date.context_today(self),
                company=self.company_id,
                currency=self.currency_id,
            )
        )
        if quote.get("price") is None:
            raise ValidationError(
                "M11 has no released reseller price for %s: %s"
                % (self.product_id.display_name, quote.get("reason") or "no rate card")
            )
        return quote

    def action_allocate(self):
        fix_require(self.env, [GROUP_MANAGER], "Allocating to a reseller")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft allocation is made.")
            fix_not_creator(self.env, rec, "allocating it")
            if (
                rec.partner_id.partner_type != "reseller"
                or rec.partner_id.state not in EARNING_STATES
            ):
                raise ValidationError(
                    "%s is not an onboarded reseller (BRU-PCM-01)." % rec.partner_id.name
                )
            if rec.allocation_type == "stock" and not rec.location_id:
                raise ValidationError(
                    "Name the M15 location refurbished stock of %s is drawn from." % rec.name
                )
            quote = rec._fix_m11_price()
            rec._guarded().write(
                {
                    "state": "allocated",
                    "allocated_by_id": self.env.uid,
                    "unit_price": quote["price"],
                    "price_source": "%s%s"
                    % (
                        quote.get("source") or "card",
                        (" #%s" % quote["card_id"]) if quote.get("card_id") else "",
                    ),
                }
            )
        return True

    def action_record_draw(self, qty=None):
        """A04 ERP audit M40-F16: a draw is a sale to the reseller - it moves
        the stock out of the M15 location (refurbished stock) and raises the
        draft M20 invoice at the M11 price fixed at allocation."""
        fix_require(self.env, [GROUP_OFFICER], "Recording a reseller draw")
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            raise UserError("Give the quantity drawn as a number.") from None
        if qty <= 0:
            raise UserError("A draw is a positive quantity.")
        draws = self.env["fix.reseller.draw"]
        for rec in self:
            if rec.state != "allocated":
                raise UserError("Draws are recorded against an open allocation.")
            if rec.consumed_qty + qty > rec.qty + 1e-9:
                raise ValidationError(
                    "%s has %.2f left; %.2f cannot be drawn." % (rec.name, rec.remaining_qty, qty)
                )
            if rec.partner_id.state not in EARNING_STATES:
                raise ValidationError(
                    "%s is %s: it draws nothing (BRU-PCM-01)."
                    % (rec.partner_id.name, rec.partner_id.state)
                )
            draw = rec._fix_draw(qty)
            rec._guarded().write({"consumed_qty": rec.consumed_qty + qty})
            rec.message_post(
                body="Drawn %.2f by %s: invoice %s%s."
                % (
                    qty,
                    self.env.user.name,
                    draw.invoice_id.display_name,
                    (", stock move %s" % draw.move_id.display_name) if draw.move_id else "",
                )
            )
            draws |= draw
        return {"res_model": draws._name, "res_ids": draws.ids}

    def _fix_draw(self, qty):
        self.ensure_one()
        Draw = self.env["fix.reseller.draw"].sudo()
        seq = len(self.sudo().draw_ids) + 1
        draw = Draw._guarded().create(
            {"allocation_id": self.id, "sequence": seq, "qty": qty, "unit_price": self.unit_price}
        )
        move = self.env["stock.move"]
        if self.allocation_type == "stock":
            move = self._fix_draw_move(qty, draw)
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            ._fix_draft_invoice_from_source(
                "fix.reseller.draw",
                "fix.reseller.draw/%s" % draw.id,
                self.partner_id.partner_id,
                [
                    {
                        "description": "%s - %s x %.2f (allocation %s)"
                        % (self.item_description, self.product_id.display_name, qty, self.name),
                        "taxable_amount": self.currency_id.round(qty * self.unit_price),
                        "product_id": self.product_id.id,
                    }
                ],
                "Reseller draw %s/%d on allocation %s" % (self.name, seq, self.name),
                company=self.company_id,
            )
        )
        draw._guarded().write({"invoice_id": invoice.id, "move_id": move.id or False})
        return self.env["fix.reseller.draw"].browse(draw.id)

    def _fix_draw_move(self, qty, draw):
        """The stock leaving the M15 location for the reseller (a done move to
        the customer location)."""
        if not self.location_id:
            raise ValidationError("Allocation %s names no M15 location." % self.name)
        dest = self.env.ref("stock.stock_location_customers")
        move = (
            self.env["stock.move"]
            .sudo()
            .create(
                {
                    "product_id": self.product_id.id,
                    "product_uom_qty": qty,
                    "product_uom": self.product_id.uom_id.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": dest.id,
                    "company_id": self.company_id.id,
                    "partner_id": self.partner_id.partner_id.id,
                    "origin": "%s draw %d" % (self.name, draw.sequence),
                }
            )
        )
        move._action_confirm()
        move._action_assign()
        if move.product_uom_qty - move.quantity > 1e-6:
            raise ValidationError(
                "%s has %.2f of %s on hand; the draw of %.2f is refused."
                % (self.location_id.display_name, move.quantity, self.product_id.display_name, qty)
            )
        move.picked = True
        move._action_done()
        return move

    def action_close(self):
        fix_require(self.env, [GROUP_MANAGER], "Closing a reseller allocation")
        for rec in self:
            if rec.state != "allocated":
                raise UserError("Only an open allocation is closed.")
            rec._guarded().write({"state": "closed"})
        return True


class FixResellerDraw(models.Model):
    """A04 ERP audit M40-F16: one draw against a reseller allocation - its
    stock move and its M20 invoice."""

    _name = "fix.reseller.draw"
    _description = "Reseller Draw"
    _inherit = ["fix.guarded.mixin"]
    _order = "allocation_id, sequence"

    allocation_id = fields.Many2one(
        "fix.reseller.allocation", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="allocation_id.company_id", store=True, index=True)
    partner_id = fields.Many2one(related="allocation_id.partner_id", store=True)
    currency_id = fields.Many2one(related="allocation_id.currency_id")
    sequence = fields.Integer(readonly=True)
    qty = fields.Float(readonly=True)
    unit_price = fields.Monetary(currency_field="currency_id", readonly=True)
    move_id = fields.Many2one("stock.move", string="Stock Move", readonly=True)
    invoice_id = fields.Many2one("fix.ar.invoice", string="Invoice (M20)", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "allocation_id",
            "sequence",
            "qty",
            "unit_price",
            "move_id",
            "invoice_id",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError("A reseller draw is recorded by Record Draw on its allocation.")
        return super().create(vals_list)


# =============================================================== p8 franchise
class FixFranchiseTerritory(models.Model):
    """FR-PCM-035, BRU-PCM-16: a franchise territory. An exclusive territory
    shares no district with another active one in the same period."""

    _name = "fix.franchise.territory"
    _description = "Franchise Territory"
    _inherit = ["fix.partner.capture.base"]
    _order = "code, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    districts = fields.Char(
        required=True, help="The districts covered, comma-separated (e.g. Gazipur, Narayanganj)."
    )
    exclusivity = fields.Selection(
        [("exclusive", "Exclusive"), ("shared", "Shared")], required=True, default="exclusive"
    )
    partner_id = fields.Many2one(
        "fix.partner",
        string="Franchisee",
        required=True,
        domain="[('partner_type', '=', 'franchise')]",
    )
    franchise_id = fields.Many2one(
        "fix.partner.franchise",
        string="Franchise Agreement",
        domain="[('partner_id', '=', partner_id)]",
    )
    valid_from = fields.Date(required=True)
    valid_to = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)

    _FROZEN = frozenset(
        {
            "company_id",
            "code",
            "districts",
            "exclusivity",
            "partner_id",
            "franchise_id",
            "valid_from",
            "valid_to",
        }
    )
    _code_unique = models.Constraint("UNIQUE (code)", "A territory code is unique.")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "approved_by_id"}

    def _district_set(self):
        return {d.strip().lower() for d in (self.districts or "").split(",") if d.strip()}

    def _overlaps(self, other):
        far = fields.Date.to_date("9999-12-31")
        return self.valid_from <= (other.valid_to or far) and other.valid_from <= (
            self.valid_to or far
        )

    @api.constrains("valid_from", "valid_to", "franchise_id", "partner_id")
    def _check_terms(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError("Territory %s ends before it starts." % rec.code)
            if rec.franchise_id and rec.franchise_id.partner_id != rec.partner_id:
                raise ValidationError("The agreement is not this franchisee's.")

    def action_activate(self):
        fix_require(self.env, [GROUP_MANAGER], "Activating a franchise territory")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft territory is activated.")
            fix_not_creator(self.env, rec, "activating it")
            if rec.partner_id.partner_type != "franchise" or rec.partner_id.state != "onboarded":
                raise ValidationError("%s is not an onboarded franchisee." % rec.partner_id.name)
            mine = rec._district_set()
            if not mine:
                raise ValidationError("Name the districts the territory covers.")
            others = self.sudo().search([("id", "!=", rec.id), ("state", "=", "active")])
            for other in others:
                if not rec._overlaps(other):
                    continue
                if "exclusive" not in (rec.exclusivity, other.exclusivity):
                    continue
                shared = mine & other._district_set()
                if shared:
                    raise ValidationError(
                        "Territory %s overlaps exclusive territory %s on %s (BRU-PCM-16): "
                        "cross-territory activity needs a documented agreement."
                        % (rec.code, other.code, ", ".join(sorted(shared)))
                    )
            rec._guarded().write({"state": "active", "approved_by_id": self.env.uid})
        return True

    def action_retire(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Retiring a franchise territory")
        if not _clean(reason):
            raise UserError("State why the territory is retired.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active territory is retired.")
            rec._guarded().write({"state": "retired"})
            rec.message_post(body="Retired: %s" % _clean(reason))
        return True


class FixPartnerFranchiseBranch(models.Model):
    """The franchise branch's operating unit: the revenue royalties are
    computed from (BRU-PCM-17)."""

    _inherit = "fix.partner.franchise"

    operating_unit_id = fields.Many2one(
        "operating.unit", string="Franchise Branch (Operating Unit)"
    )
    royalty_rate = fields.Float(string="Royalty Rate", help="Fraction of ERP revenue, e.g. 0.06.")
    marketing_levy_rate = fields.Float(string="Marketing Levy Rate")
    territory_ids = fields.One2many("fix.franchise.territory", "franchise_id", string="Territories")

    # the rates and the branch royalties are computed on are agreement terms
    _FROZEN = frozenset(
        {
            "partner_id",
            "territory",
            "fee",
            "currency_id",
            "start_date",
            "end_date",
            "operating_unit_id",
            "royalty_rate",
            "marketing_levy_rate",
        }
    )

    @api.constrains("royalty_rate", "marketing_levy_rate")
    def _check_rates(self):
        for rec in self:
            for rate in (rec.royalty_rate, rec.marketing_levy_rate):
                if not 0.0 <= (rate or 0.0) <= ROYALTY_MAX_RATE:
                    raise ValidationError(
                        "A royalty or levy rate is between 0 and %d%%." % (ROYALTY_MAX_RATE * 100)
                    )


class FixFranchiseRoyalty(models.Model):
    """FR-PCM-036, BRU-PCM-17: a period's royalty and marketing levy,
    computed from the branch's verified settlements - never self-declared."""

    _name = "fix.franchise.royalty"
    _description = "Franchise Royalty"
    _inherit = ["fix.partner.capture.base"]
    _order = "period_from desc, id desc"

    franchise_id = fields.Many2one(
        "fix.partner.franchise",
        required=True,
        ondelete="restrict",
        index=True,
        domain="[('state', '=', 'active')]",
    )
    partner_id = fields.Many2one(related="franchise_id.partner_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="franchise_id.currency_id", store=True, readonly=True)
    period_from = fields.Date(required=True)
    period_to = fields.Date(required=True)
    revenue_basis = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The branch's M20 revenue of the period, VAT exclusive, net of its credit notes "
        "(A04 ERP audit M40-F19).",
    )
    credited_basis = fields.Monetary(
        string="Credit Notes Netted",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    royalty_rate = fields.Float(readonly=True, copy=False)
    royalty_amount = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    levy_rate = fields.Float(readonly=True, copy=False)
    levy_amount = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    order_count = fields.Integer(readonly=True, copy=False, string="Invoices Counted")
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("invoiced", "Invoiced")],
        required=True,
        default="draft",
        tracking=True,
    )
    computed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    invoice_ref = fields.Char(readonly=True, copy=False)
    # A04 ERP audit M40-F1: the M20 invoice raised for the royalty and levy.
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Invoice (M20)", readonly=True, copy=False
    )
    company_id = fields.Many2one(
        related="franchise_id.partner_id.company_id", store=True, index=True, readonly=True
    )

    _FROZEN = frozenset({"franchise_id", "period_from", "period_to"})
    _period_unique = models.Constraint(
        "UNIQUE (franchise_id, period_from)", "A franchise carries one royalty per period."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "revenue_basis",
            "royalty_rate",
            "royalty_amount",
            "levy_rate",
            "levy_amount",
            "order_count",
            "computed_by_id",
            "invoice_ref",
            "invoice_id",
            "credited_basis",
        }

    @api.constrains("period_from", "period_to")
    def _check_period(self):
        for rec in self:
            if rec.period_to < rec.period_from:
                raise ValidationError("A royalty period ends after it starts.")

    # M20 invoice states that are revenue of the period (a draft is not yet
    # revenue, a cancelled one never was; a written-off one was earned).
    _REVENUE_STATES = ("issued", "paid", "credited", "written_off")

    def _erp_revenue(self):
        """The branch's ERP-recorded revenue for the period, never a
        declaration (BRU-PCM-17).

        A04 ERP audit M40-F19: the basis was the VAT-INCLUSIVE cash settled on
        service orders (15% over) with refunds never netted. It is now the
        branch's M20 invoices of the period (invoice date), VAT exclusive,
        less the VAT-exclusive part of the credit notes issued against the
        branch's invoices in the period. Returns (net basis, credited, count)."""
        self.ensure_one()
        ou = self.franchise_id.operating_unit_id
        if not ou:
            raise ValidationError(
                "Link franchise %s to its branch operating unit: royalties are computed from "
                "ERP revenue, never self-declared (BRU-PCM-17)." % self.franchise_id.name
            )
        invoices = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("operating_unit_id", "=", ou.id),
                    ("state", "in", self._REVENUE_STATES),
                    ("invoice_date", ">=", self.period_from),
                    ("invoice_date", "<=", self.period_to),
                    # the franchise's own royalty invoices are not its revenue
                    ("source_model", "not in", ("fix.franchise.royalty", "fix.partner.franchise")),
                ]
            )
        )
        gross = sum(invoices.mapped("taxable_amount"))
        start = fields.Datetime.to_datetime(self.period_from) - timedelta(hours=6)
        stop = fields.Datetime.to_datetime(self.period_to) + timedelta(days=1, hours=-6)
        notes = (
            self.env["fix.credit.note"]
            .sudo()
            .search(
                [
                    ("invoice_id.operating_unit_id", "=", ou.id),
                    ("state", "=", "issued"),
                    ("issued_at", ">=", start),
                    ("issued_at", "<", stop),
                ]
            )
        )
        credited = round(sum(credit_ex_vat(n) for n in notes), 2)
        return round(gross - credited, 2), credited, len(invoices)

    def action_compute(self):
        fix_require(self.env, [GROUP_OFFICER], "Computing a franchise royalty")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft royalty is computed.")
            if rec.period_to >= today:
                raise UserError("A royalty is computed after its period ends.")
            if rec.franchise_id.state != "active":
                raise ValidationError("Franchise %s is not active." % rec.franchise_id.name)
            basis, credited, count = rec._erp_revenue()
            basis = max(basis, 0.0)
            rate = rec.franchise_id.royalty_rate or 0.0
            levy = rec.franchise_id.marketing_levy_rate or 0.0
            if rate <= 0:
                raise ValidationError("Set the franchise's royalty rate first.")
            cur = rec.franchise_id.currency_id
            rec._guarded().write(
                {
                    "state": "computed",
                    "revenue_basis": basis,
                    "credited_basis": credited,
                    "order_count": count,
                    "royalty_rate": rate,
                    "royalty_amount": cur.round(basis * rate),
                    "levy_rate": levy,
                    "levy_amount": cur.round(basis * levy),
                    "computed_by_id": self.env.uid,
                }
            )
        return True

    def action_raise_invoice(self):
        """A04 ERP audit M40-F1 (AUT-PCM-15): finance raises the M20 invoice
        of the royalty and the marketing levy to the franchisee - one line
        each, VAT determined by M51, crediting the configured royalty income
        account. The invoice is a draft: finance issues it (number, Mushak
        6.3, GL). A typed reference no longer stands for an invoice."""
        _require_finance(self.env, "Raising a royalty invoice")
        invoices = self.env["fix.ar.invoice"]
        for rec in self:
            if rec.state != "computed":
                raise UserError("Only a computed royalty is invoiced.")
            fr = rec.franchise_id.sudo()
            lines = []
            label = "%s to %s" % (rec.period_from, rec.period_to)
            if rec.royalty_amount > 0.005:
                lines.append(
                    {
                        "description": "Franchise royalty %s: %.2f%% of BDT %.2f (%s)"
                        % (fr.name, rec.royalty_rate * 100.0, rec.revenue_basis, label),
                        "taxable_amount": rec.royalty_amount,
                    }
                )
            if rec.levy_amount > 0.005:
                lines.append(
                    {
                        "description": "Marketing levy %s: %.2f%% of BDT %.2f (%s)"
                        % (fr.name, rec.levy_rate * 100.0, rec.revenue_basis, label),
                        "taxable_amount": rec.levy_amount,
                    }
                )
            if not lines:
                raise UserError(
                    "Royalty %s is nil (no revenue in %s): there is nothing to invoice."
                    % (rec.id, label)
                )
            company = fr.partner_id.company_id
            account = partner_account(self.env, company, "royalty_income")
            invoice = (
                self.env["fix.ar.invoice"]
                .sudo()
                ._fix_draft_invoice_from_source(
                    rec._name,
                    "%s/%s" % (rec._name, rec.id),
                    fr.partner_id.partner_id,
                    lines,
                    "Franchise royalty and marketing levy of %s for %s (BRU-PCM-17)"
                    % (fr.name, label),
                    company=company,
                    invoice_date=fields.Date.context_today(self),
                    credit_account=account,
                )
            )
            rec.sudo()._guarded().write(
                {"state": "invoiced", "invoice_id": invoice.id, "invoice_ref": invoice.name}
            )
            rec.sudo().message_post(
                body="Draft M20 invoice %s raised for BDT %.2f + VAT; finance issues it."
                % (invoice.display_name, sum(line["taxable_amount"] for line in lines))
            )
            invoices |= invoice
        return {"res_model": invoices._name, "res_ids": invoices.ids}


# ==================================================================== p9 MDF
class FixMdfFund(models.Model):
    """FR-PCM-039, T-09: a partner's MDF allocation for a period. Claimed,
    approved, paid and the balance are derived from its claims."""

    _name = "fix.mdf.fund"
    _description = "MDF Fund Allocation"
    _inherit = ["fix.partner.capture.base"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, index=True)
    period = fields.Char(required=True)
    allocated = fields.Monetary(currency_field="currency_id", required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        required=True,
        default="draft",
        tracking=True,
    )
    allocated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    claim_ids = fields.One2many("fix.mdf.claim", "fund_id", string="Claims")
    claimed = fields.Monetary(currency_field="currency_id", compute="_compute_ledger")
    approved = fields.Monetary(currency_field="currency_id", compute="_compute_ledger")
    paid = fields.Monetary(currency_field="currency_id", compute="_compute_ledger")
    balance = fields.Monetary(currency_field="currency_id", compute="_compute_ledger")

    _FROZEN = frozenset({"company_id", "partner_id", "period", "allocated", "currency_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "allocated_by_id"}

    @api.depends("allocated", "claim_ids.state", "claim_ids.amount")
    def _compute_ledger(self):
        for rec in self:
            claims = rec.claim_ids.sudo()
            rec.claimed = sum(claims.filtered(lambda c: c.state == "submitted").mapped("amount"))
            rec.approved = sum(
                claims.filtered(lambda c: c.state in ("approved", "paid")).mapped("amount")
            )
            rec.paid = sum(claims.filtered(lambda c: c.state == "paid").mapped("amount"))
            rec.balance = (rec.allocated or 0.0) - rec.claimed - rec.approved

    @api.constrains("allocated")
    def _check_allocated(self):
        for rec in self:
            if rec.allocated <= 0:
                raise ValidationError("An MDF allocation is a positive amount.")

    def action_open(self):
        fix_require(self.env, [GROUP_MANAGER], "Allocating an MDF fund")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft fund is opened.")
            if rec.partner_id.state != "onboarded":
                raise ValidationError("%s is not onboarded (BRU-PCM-01)." % rec.partner_id.name)
            rec._guarded().write({"state": "open", "allocated_by_id": self.env.uid})
        return True

    def action_close(self):
        fix_require(self.env, [GROUP_MANAGER], "Closing an MDF fund")
        for rec in self:
            if rec.state != "open":
                raise UserError("Only an open fund is closed.")
            if rec.claim_ids.filtered(lambda c: c.state in ("draft", "submitted")):
                raise UserError("Decide the fund's open claims before closing it.")
            rec._guarded().write({"state": "closed"})
        return True


class FixMdfClaim(models.Model):
    """FR-PCM-039, BRU-PCM-11: an MDF claim on its evidence, decided by a
    manager who neither allocated the fund nor raised the claim."""

    _name = "fix.mdf.claim"
    _description = "MDF Claim"
    _inherit = ["fix.partner.capture.base"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    fund_id = fields.Many2one(
        "fix.mdf.fund",
        required=True,
        ondelete="restrict",
        index=True,
        domain="[('state', '=', 'open')]",
    )
    partner_id = fields.Many2one(related="fund_id.partner_id", store=True, readonly=True)
    currency_id = fields.Many2one(related="fund_id.currency_id", store=True, readonly=True)
    campaign_id = fields.Many2one("fix.campaign", string="Campaign (M35)", ondelete="restrict")
    amount = fields.Monetary(currency_field="currency_id", required=True)
    description = fields.Text(required=True)
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Proof of Execution", copy=False, ondelete="restrict"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Evidence Review"),
            ("approved", "Payment Instructed"),
            ("refused", "Refused"),
            ("paid", "Paid"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    submitted_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)
    refusal_reason = fields.Char(readonly=True, copy=False)
    payment_ref = fields.Char(readonly=True, copy=False)
    company_id = fields.Many2one(related="fund_id.company_id", store=True, index=True)

    _FROZEN = frozenset(
        {"fund_id", "campaign_id", "amount", "description", "evidence_attachment_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "submitted_by_id",
            "decided_by_id",
            "decided_at",
            "refusal_reason",
            "payment_ref",
        }

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("A claim is for a positive amount.")

    @api.constrains("evidence_attachment_id")
    def _check_evidence_is_own(self):
        for rec in self:
            _assert_own_attachment(rec, "evidence_attachment_id")

    @api.constrains("campaign_id", "fund_id")
    def _check_campaign(self):
        for rec in self.filtered("campaign_id"):
            if rec.fund_id.partner_id not in rec.campaign_id.sudo().partner_ids:
                raise ValidationError(
                    "%s is not a co-marketing partner of campaign %s."
                    % (rec.fund_id.partner_id.name, rec.campaign_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write(
                {
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.mdf.claim")
                    or "MDF/%d" % rec.id
                }
            )
        return recs

    def _assert_within_balance(self):
        fund = self.fund_id.sudo()
        others = fund.claim_ids.filtered(
            lambda c: c.id != self.id and c.state in ("submitted", "approved", "paid")
        )
        left = fund.allocated - sum(others.mapped("amount"))
        if self.amount > left + 1e-6:
            raise ValidationError(
                "Claim %s (%.2f) exceeds what is left of fund %s (%.2f)."
                % (self.name, self.amount, fund.name, left)
            )

    def action_submit(self):
        fix_require(self.env, [GROUP_OFFICER], "Submitting an MDF claim")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft claim is submitted.")
            if rec.fund_id.state != "open":
                raise ValidationError("Fund %s is not open." % rec.fund_id.name)
            if not rec.evidence_attachment_id:
                raise ValidationError("Attach the proof of execution (BRU-PCM-11).")
            rec._assert_within_balance()
            rec._guarded().write({"state": "submitted", "submitted_by_id": self.env.uid})
        return True

    def _assert_decider(self):
        fix_require(self.env, [GROUP_MANAGER], "Deciding an MDF claim")
        fix_not_creator(self.env, self, "deciding it")
        if not self.env.su and self.env.user in (
            self.fund_id.allocated_by_id | self.submitted_by_id
        ):
            raise UserError(
                "Segregation of duties: you allocated the fund or submitted claim %s; "
                "another manager decides it (BRU-PCM-11)." % self.name
            )

    def action_approve(self):
        """A04 ERP audit M40-F3: approval is the payment instruction - it
        publishes partner.mdf_claim_approved, whose M53 consumer accrues the
        claim (Dr MDF expense / Cr partner payable / Cr TDS) and raises the
        pending M50 payout of the net, as for a rebate. Refused while the
        payout accounts are unconfigured (fail closed)."""
        from .fix_partner_ops import assert_payout_accounts

        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a claim under review is approved.")
            rec._assert_decider()
            rec._assert_within_balance()
            if rec.fund_id.partner_id.state not in EARNING_STATES:
                raise ValidationError(
                    "%s is %s: no MDF is paid (BRU-PCM-01)."
                    % (rec.fund_id.partner_id.name, rec.fund_id.partner_id.state)
                )
            assert_payout_accounts(self.env, rec.fund_id.company_id, "partner_mdf_expense")
            rec._guarded().write(
                {
                    "state": "approved",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            publish(
                rec.env,
                "partner.mdf_claim_approved",
                rec._name,
                rec.id,
                {
                    "claim": rec.name,
                    "fund": rec.fund_id.name,
                    "partner_id": rec.fund_id.partner_id.id,
                    "party_id": rec.fund_id.partner_id.partner_id.id,
                    "amount": float(rec.amount or 0.0),
                    "currency": rec.currency_id.name,
                    "approved_by": rec.env.user.id,
                },
            )
        return True

    def action_refuse(self, reason=None):
        reason = _clean(reason)
        if not reason:
            raise UserError("Give the reason for refusing: the partner may appeal it.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a claim under review is refused.")
            rec._assert_decider()
            rec._guarded().write(
                {
                    "state": "refused",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "refusal_reason": reason,
                }
            )
        return True

    def action_record_payment(self, payment_ref=None):
        """A04 ERP audit M40-F3: an MDF claim is paid when its M50 payout
        instruction is executed (the bank confirmed it) - the reference is the
        instruction's, never a typed one."""
        from .fix_partner_ops import executed_payout

        _require_finance(self.env, "Recording an MDF payment")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved claim is paid.")
            pay = executed_payout(rec, "MDF claim %s" % rec.name)
            rec.sudo()._guarded().write(
                {"state": "paid", "payment_ref": pay.bank_reference or pay.name}
            )
        return True


# ============================================ partner: programme, gates, links
class FixPartnerCapture(models.Model):
    _inherit = "fix.partner"

    partner_type = fields.Selection(
        selection_add=[("brand", "Brand Partner")], ondelete={"brand": "set default"}
    )
    programme_id = fields.Many2one(
        "fix.partner.programme",
        string="Programme (version bound)",
        domain="[('state', '=', 'published'), ('partner_type', '=', partner_type)]",
        ondelete="restrict",
    )
    programme_version = fields.Integer(related="programme_id.version", string="Programme Version")
    tier_id = fields.Many2one(
        "fix.partner.tier", string="Tier", domain="[('programme_id', '=', programme_id)]"
    )
    contact_role_ids = fields.One2many("fix.partner.contact.role", "partner_id", string="Contacts")
    pending_tier_id = fields.Many2one(
        "fix.partner.tier", string="Tier After Notice", readonly=True, copy=False
    )
    tier_effective_on = fields.Date(string="Tier Effective On", readonly=True, copy=False)
    onboarding_ids = fields.One2many(
        "fix.partner.onboarding", "partner_id", string="Onboarding Checklist"
    )
    enablement_ids = fields.One2many("fix.partner.enablement", "partner_id", string="Enablement")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"tier_id", "pending_tier_id", "tier_effective_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "prospective":
            locked |= {"programme_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "prospective"):
                _refuse_changes(
                    rec,
                    vals,
                    {"programme_id"},
                    "a partner stays on the programme version in force when it joined (BRU-PCM-12)",
                )
        return super().write(vals)

    @api.constrains("programme_id", "tier_id", "partner_type")
    def _check_programme(self):
        for rec in self:
            prog = rec.programme_id
            if prog and prog.partner_type != rec.partner_type:
                raise ValidationError(
                    "Programme %s is for %s partners." % (prog.name, prog.partner_type)
                )
            if rec.tier_id and rec.tier_id.programme_id != prog:
                raise ValidationError(
                    "Tier %s is not of programme %s." % (rec.tier_id.name, prog.name or "-")
                )

    def action_generate_onboarding(self):
        """FR-PCM-007: the standard checklist, without duplicating a step."""
        fix_require(self.env, [GROUP_OFFICER], "Generating an onboarding checklist")
        steps = self.env["fix.partner.onboarding"]
        for rec in self:
            have = set(rec.onboarding_ids.mapped("step"))
            for seq, (key, label) in enumerate(ONBOARDING_STEPS):
                if key == "other" or key in have:
                    continue
                steps.create(
                    {"partner_id": rec.id, "step": key, "name": label, "sequence": 10 * (seq + 1)}
                )
        return True

    def action_change_tier(self, tier_code=None):
        """FR-PCM-004: a manager moves the partner to another tier of its
        programme, effective after the tier's notice period.

        A04 ERP audit M40-F30: the move took effect at once whatever the
        notice. It is now staged (pending tier, effective date = today + the
        tier's notice days) and applied by the daily job on that date; a tier
        with no notice applies at once."""
        fix_require(self.env, [GROUP_MANAGER], "Moving a partner between tiers")
        code = _clean(tier_code)
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.programme_id:
                raise UserError("%s is on no programme." % rec.name)
            tier = rec.programme_id.tier_ids.filtered(lambda t: t.code == code)
            if not tier:
                raise UserError(
                    "Programme %s has no tier %r (tiers: %s)."
                    % (
                        rec.programme_id.name,
                        code,
                        ", ".join(rec.programme_id.tier_ids.mapped("code")),
                    )
                )
            old = rec.tier_id
            new = tier[0]
            effective = today + timedelta(days=max(new.notice_days, 0))
            if effective <= today:
                rec._guarded().write(
                    {"tier_id": new.id, "pending_tier_id": False, "tier_effective_on": today}
                )
            else:
                rec._guarded().write({"pending_tier_id": new.id, "tier_effective_on": effective})
            rec.message_post(
                body="Tier %s -> %s by %s; effective on %s (%d days' notice)."
                % (old.code or "-", new.code, self.env.user.name, effective, new.notice_days)
            )
        return True

    @api.model
    def cron_apply_tier_changes(self):
        """A04 ERP audit M40-F30: a staged tier move takes effect on its date."""
        today = fields.Date.context_today(self)
        due = self.sudo().search(
            [("pending_tier_id", "!=", False), ("tier_effective_on", "<=", today)]
        )
        for rec in due:
            rec._guarded().write({"tier_id": rec.pending_tier_id.id, "pending_tier_id": False})
            rec.message_post(body="Tier %s in effect from %s." % (rec.tier_id.code, today))
        return len(due)

    def action_onboard(self):
        """BRU-PCM-01: every required onboarding step done, the agreement
        linked once the checklist names one.

        A04 ERP audit M40-F11: a partner with no checklist, no agreement and
        no programme was onboarded. Onboarding now needs all three: the
        partner bound to a published programme version, its M08 agreement in
        force, and a checklist whose required steps are all done."""
        for rec in self:
            src = rec.sudo()
            if not src.programme_id or src.programme_id.state != "published":
                raise ValidationError(
                    "%s cannot be onboarded: bind it to a published programme first "
                    "(FR-PCM-003, BRU-PCM-01)." % rec.name
                )
            contract = src.contract_id
            if not contract or contract.state not in ("active", "expiring"):
                raise ValidationError(
                    "%s cannot be onboarded: its M08 partner agreement is %s - it must be "
                    "executed and in force (BRU-PCM-01)."
                    % (rec.name, contract.state if contract else "missing")
                )
            if not src.onboarding_ids.filtered("required"):
                raise ValidationError(
                    "%s cannot be onboarded: it has no onboarding checklist (Generate "
                    "Onboarding Checklist, FR-PCM-007, BRU-PCM-01)." % rec.name
                )
            pending = rec.sudo().onboarding_ids.filtered(lambda s: s.required and s.state != "done")
            if pending:
                raise ValidationError(
                    "%s cannot be onboarded: required onboarding steps are pending (%s) "
                    "(BRU-PCM-01)." % (rec.name, ", ".join(pending.mapped("name")))
                )
        return super().action_onboard()


class FixPartnerRebateEnablement(models.Model):
    _inherit = "fix.partner.rebate"

    def action_accrue(self):
        """FR-PCM-041: programme benefits wait for required certification."""
        today = fields.Date.context_today(self)
        for rec in self:
            missing = rec.partner_id.sudo().enablement_ids.filtered(
                lambda e: e.required
                and not (e.state == "certified" and (not e.expires_on or e.expires_on >= today))
            )
            if missing:
                raise ValidationError(
                    "%s holds no current certification for %s: benefits are gated on it "
                    "(FR-PCM-041)." % (rec.partner_id.name, ", ".join(missing.mapped("course")))
                )
        return super().action_accrue()
