# M36 capture audit, second pass (2026-11-19).
#
# After the first pass every page had a "+ New", but read against the spec
# (§5 FR-QTE-001..048, §9 BRU-QTE-01..18, §10.1 owned entities) eight records
# the pages are about still had nowhere to be captured, and the rules that
# depend on them did not run:
#
#   p1  FR-QTE-009       no technical review / second opinion of an estimate
#   p2  FR-QTE-018       terms, assumptions and exclusions were free text: no
#                        governed library, nothing marked a term non-standard
#   p2  FR-QTE-024       no renewal quotation from an expiring contract
#   p4  FR-QTE-027       a non-standard term needed nobody's approval
#       BRU-QTE-08       (CCO + CFO)
#   p4  FR-QTE-028       a customer on credit hold or over the limit was
#       BRU-QTE-14       quoted and accepted like any other (no Finance override)
#   p5/7 FR-QTE-042      no acceptance on a recorded phone call
#   p7  BRU-QTE-17/T-14  no legal hold on a disputed quotation
#   p9  FR-QTE-046       no tender document checklist; submission did not wait
#       BRU-QTE-15       for a required document
#   p9  FR-QTE-048       a lost tender recorded free text, not a governed reason
#       BRU-QTE-16
#
# Every record below is captured by its own workspace form; the workflow
# effects run through methods, never through typed state.
import hashlib
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.exceptions import UserError, ValidationError

from .fix_quotation import dhaka_today
from .fix_quote_with_customer import _changed

AUTHOR = "cd_quotation.group_quotation_user"
MANAGER = "cd_quotation.group_quotation_manager"
BID = "cd_quotation.group_bid_coordinator"
# The spec names the CCO and the CFO (BRU-QTE-08). The estate has no such
# roles: the Commercial Manager (Quotations) and the Accounting Administrator
# stand in until the owner names them (report §4).
FINANCE = "account.group_account_manager"

TERM_TYPES = [
    ("term", "Commercial term"),
    ("assumption", "Assumption"),
    ("exclusion", "Exclusion"),
]


def _quote_types(model):
    """Every kind of quotation fix.quotation knows, including the ones other
    files add (P2 "project"): a fixed list refused the live templates' types."""
    return model.env["fix.quotation"]._fields["quote_type"].selection


DEVIATION_STATES = [
    ("standard", "Standard (no approval needed)"),
    ("pending", "Deviation awaiting approval"),
    ("approved", "Deviation approved (CCO + CFO)"),
    ("rejected", "Deviation rejected"),
]


def _has(env, xmlid):
    return env.su or env.user.has_group(xmlid)


def _norm(text):
    return " ".join((text or "").split())


# =============================================================================
# p10 / p2 / p4 — governed terms (FR-QTE-018/027, BRU-QTE-08)
# =============================================================================
class FixQuotationStandardTerm(models.Model):
    """The governed library of standard terms, assumptions and exclusions.
    Only the Commercial Manager maintains it; a term quoted word for word
    from it needs no approval."""

    _name = "fix.quotation.standard.term"
    _description = "Quotation Standard Term (governed library)"
    _order = "quote_type, term_type, sequence, id"

    code = fields.Char(required=True, index=True)
    name = fields.Char(string="Title", required=True)
    term_type = fields.Selection(TERM_TYPES, string="Kind", required=True, default="term")
    quote_type = fields.Selection(
        _quote_types, string="Applies To", help="Empty: every kind of quotation."
    )
    text_en = fields.Text(string="Wording (English)", required=True)
    text_bn = fields.Text(string="Wording (Bengali)")
    mandatory = fields.Boolean(
        help="Every quotation of this kind must carry it before it is submitted."
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )

    _code_unique = models.Constraint(
        "UNIQUE (code, company_id)", "A standard term code is unique per company."
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s - %s" % (rec.code or "?", rec.name or "")

    def _assert_steward(self):
        if not _has(self.env, MANAGER):
            raise UserError(_("Only the Commercial Manager maintains the standard terms library."))

    @api.model_create_multi
    def create(self, vals_list):
        self._assert_steward()
        for vals in vals_list:
            if not _norm(vals.get("text_en")):
                raise ValidationError(_("A standard term needs its English wording."))
        return super().create(vals_list)

    def write(self, vals):
        self._assert_steward()
        if "text_en" in vals and not _norm(vals["text_en"]):
            raise ValidationError(_("A standard term needs its English wording."))
        return super().write(vals)

    def unlink(self):
        self._assert_steward()
        if (
            self.env["fix.quotation.term"]
            .sudo()
            .search_count([("standard_term_id", "in", self.ids)])
        ):
            raise UserError(_("A standard term already quoted is archived, not deleted."))
        return super().unlink()


class FixQuotationTerm(models.Model):
    """A term, assumption or exclusion on one quotation (spec entity
    fix.quotation.term). Wording that is not the library's word for word is a
    deviation: approved by the Commercial Manager AND Finance (two people,
    neither the author) before the quotation can be submitted or issued."""

    _name = "fix.quotation.term"
    _description = "Quotation Term / Assumption / Exclusion"
    _inherit = ["mail.thread"]
    _order = "quotation_id, term_type, sequence, id"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    customer_id = fields.Many2one(
        "res.partner", related="quotation_id.customer_id", store=True, string="Customer"
    )
    quotation_state = fields.Selection(related="quotation_id.state", string="Quotation State")
    sequence = fields.Integer(default=10)
    standard_term_id = fields.Many2one(
        "fix.quotation.standard.term",
        string="Standard Term",
        help="Empty, or wording changed: a deviation that needs approval.",
    )
    term_type = fields.Selection(TERM_TYPES, string="Kind", required=True, default="term")
    text_en = fields.Text(string="Wording (English)")
    text_bn = fields.Text(string="Wording (Bengali)")
    deviation_reason = fields.Char(string="Why the Standard Wording Does Not Fit")
    is_standard = fields.Boolean(compute="_compute_is_standard", store=True)
    deviation_state = fields.Selection(
        DEVIATION_STATES, compute="_compute_is_standard", store=True, string="Approval"
    )
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    commercial_approver_id = fields.Many2one(
        "res.users", string="Approved (Commercial / CCO)", readonly=True, copy=False
    )
    commercial_approved_at = fields.Datetime(readonly=True, copy=False)
    finance_approver_id = fields.Many2one(
        "res.users", string="Approved (Finance / CFO)", readonly=True, copy=False
    )
    finance_approved_at = fields.Datetime(readonly=True, copy=False)
    rejected_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    rejection_note = fields.Char(readonly=True, copy=False)
    # the decision form's inputs (never stored)
    decision_choice = fields.Selection(
        [("approve", "Approve the deviation"), ("reject", "Reject the deviation")],
        string="Decision",
        compute="_compute_inputs",
    )
    decision_note = fields.Char(string="Decision Note", compute="_compute_inputs")

    # The library wording at the time the term is written decides; a later
    # library edit does not turn a quoted term into a deviation.
    @api.depends(
        "standard_term_id",
        "text_en",
        "text_bn",
        "commercial_approver_id",
        "finance_approver_id",
        "rejected_by_id",
    )
    def _compute_is_standard(self):
        for rec in self:
            std = rec.standard_term_id
            rec.is_standard = bool(
                std
                and _norm(rec.text_en) == _norm(std.text_en)
                and (not rec.text_bn or _norm(rec.text_bn) == _norm(std.text_bn))
            )
            if rec.is_standard:
                rec.deviation_state = "standard"
            elif rec.rejected_by_id:
                rec.deviation_state = "rejected"
            elif rec.commercial_approver_id and rec.finance_approver_id:
                rec.deviation_state = "approved"
            else:
                rec.deviation_state = "pending"

    def _compute_inputs(self):
        for rec in self:
            rec.decision_choice = False
            rec.decision_note = False

    @api.depends("quotation_id.name", "term_type", "standard_term_id.code")
    def _compute_display_name(self):
        kinds = dict(TERM_TYPES)
        for rec in self:
            rec.display_name = "%s · %s%s" % (
                rec.quotation_id.name or "",
                kinds.get(rec.term_type, ""),
                " %s" % rec.standard_term_id.code if rec.standard_term_id else "",
            )

    # ---- create / write ------------------------------------------------------
    def _assert_quote_draft(self, quotes):
        if self.env.su:
            return
        for quote in quotes:
            if quote.state != "draft" or quote.approval_state == "pending":
                raise UserError(
                    _(
                        "Quotation %(q)s is %(s)s: its terms are set while it is a draft not "
                        "awaiting approval (revise an issued one).",
                        q=quote.name,
                        s=quote.state if quote.state != "draft" else "awaiting approval",
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        Std = self.env["fix.quotation.standard.term"]
        for vals in vals_list:
            quote = Quote.browse(vals.get("quotation_id")).exists()
            if not quote:
                raise UserError(_("Name the quotation the term belongs to."))
            self._assert_quote_draft(quote)
            std = Std.browse(vals.get("standard_term_id")).exists()
            if std:
                vals.setdefault("term_type", std.term_type)
                if not _norm(vals.get("text_en")):
                    vals["text_en"] = std.text_en
                if not _norm(vals.get("text_bn")) and std.text_bn:
                    vals["text_bn"] = std.text_bn
            for stamp in (
                "commercial_approver_id",
                "commercial_approved_at",
                "finance_approver_id",
                "finance_approved_at",
                "rejected_by_id",
                "rejection_note",
            ):
                if not self.env.su:
                    vals.pop(stamp, None)
            vals["recorded_by_id"] = False if self.env.su else self.env.user.id
        records = super().create(vals_list)
        records._check_wording()
        return records

    def write(self, vals):
        if not self.env.su:
            self._assert_quote_draft(self.quotation_id)
            if "quotation_id" in vals and _changed(self, {"quotation_id": vals["quotation_id"]}):
                raise UserError(_("A term stays on the quotation it was written for."))
            wording = _changed(
                self,
                {k: v for k, v in vals.items() if k in ("text_en", "text_bn", "standard_term_id")},
            )
            for stamp in (
                "commercial_approver_id",
                "commercial_approved_at",
                "finance_approver_id",
                "finance_approved_at",
                "rejected_by_id",
                "rejection_note",
                "recorded_by_id",
            ):
                if stamp in vals and _changed(self, {stamp: vals[stamp]}):
                    raise UserError(_("Approvals are given with Decide a Term Deviation."))
                vals = {k: v for k, v in vals.items() if k != stamp}
            if wording:
                # new wording, new approval
                vals = dict(
                    vals,
                    commercial_approver_id=False,
                    commercial_approved_at=False,
                    finance_approver_id=False,
                    finance_approved_at=False,
                    rejected_by_id=False,
                    rejection_note=False,
                )
        res = super().write(vals)
        self._check_wording()
        return res

    def unlink(self):
        self._assert_quote_draft(self.quotation_id)
        return super().unlink()

    def _check_wording(self):
        for rec in self:
            if not _norm(rec.text_en):
                raise ValidationError(_("Write the term's wording (English)."))
            if not rec.is_standard and not _norm(rec.deviation_reason):
                raise ValidationError(
                    _(
                        "This wording is not the standard term's: say why the standard "
                        "wording does not fit (it goes to the CCO and CFO for approval)."
                    )
                )
        return True

    # ---- the deviation decision (FR-QTE-027, BRU-QTE-08) -------------------------
    def action_decide_deviation(self, decision=None, note=None):
        """Each approver signs the slot their role holds: the Commercial
        Manager (CCO) and Finance (CFO). Two different people, neither the
        quotation's author nor whoever wrote the term. Either may reject."""
        note = (note or "").strip()
        user = self.env.user
        now = fields.Datetime.now()
        for rec in self:
            if rec.deviation_state != "pending":
                raise UserError(_("Term %s awaits no approval.") % rec.display_name)
            if rec.quotation_id.state != "draft":
                raise UserError(_("The quotation is no longer a draft."))
            if decision not in ("approve", "reject"):
                raise UserError(_("Choose the decision: approve or reject."))
            if not self.env.su and user in (rec.quotation_id.create_uid | rec.recorded_by_id):
                raise UserError(
                    _(
                        "Segregation of duties: the author of the quotation or of the term "
                        "does not approve its deviation."
                    )
                )
            commercial = _has(self.env, MANAGER)
            finance = _has(self.env, FINANCE)
            if not (commercial or finance):
                raise UserError(
                    _(
                        "A non-standard term is approved by the Commercial Manager (CCO) and "
                        "Finance (CFO) only."
                    )
                )
            if decision == "reject":
                if not note:
                    raise UserError(_("Say why the deviation is rejected."))
                rec.sudo().write({"rejected_by_id": user.id, "rejection_note": note})
                rec.sudo().message_post(
                    author_id=self.env.user.partner_id.id,
                    body=_("Deviation rejected by %s: %s") % (user.name, note),
                )
                continue
            vals = {}
            if commercial and not rec.commercial_approver_id and rec.finance_approver_id != user:
                vals = {"commercial_approver_id": user.id, "commercial_approved_at": now}
            elif finance and not rec.finance_approver_id and rec.commercial_approver_id != user:
                vals = {"finance_approver_id": user.id, "finance_approved_at": now}
            if not vals:
                raise UserError(
                    _(
                        "You have already approved this deviation, or your role's approval "
                        "is given: the other approver (%s) decides."
                    )
                    % (_("Finance / CFO") if rec.commercial_approver_id else _("Commercial / CCO"))
                )
            rec.sudo().write(vals)
            rec.sudo().message_post(
                author_id=self.env.user.partner_id.id,
                body=_("Deviation approved by %(u)s (%(r)s).")
                % {
                    "u": user.name,
                    "r": _("Commercial / CCO")
                    if "commercial_approver_id" in vals
                    else _("Finance / CFO"),
                },
            )
        return True


# =============================================================================
# p4 — the credit gate and its Finance override (FR-QTE-028, BRU-QTE-14)
# =============================================================================
class FixQuotationCreditOverride(models.Model):
    """Finance lets one quotation version be issued and accepted although the
    customer is on credit hold or would go over the credit limit."""

    _name = "fix.quotation.credit.override"
    _description = "Quotation Credit Override (Finance)"
    _inherit = ["mail.thread"]
    _order = "id desc"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    customer_id = fields.Many2one(
        "res.partner", related="quotation_id.customer_id", store=True, string="Customer"
    )
    currency_id = fields.Many2one(related="quotation_id.currency_id")
    version = fields.Integer(string="Quotation Version", readonly=True)
    amount_total = fields.Monetary(
        string="Quotation Total (incl. VAT)", readonly=True, currency_field="currency_id"
    )
    block_reason = fields.Char(string="What the Gate Found", readonly=True)
    reason = fields.Text(string="Why Finance Lets It Through", required=True)
    granted_by_id = fields.Many2one("res.users", string="Granted By", readonly=True)
    granted_at = fields.Datetime(readonly=True)
    revoked = fields.Boolean(readonly=True)

    @api.depends("quotation_id.name", "version")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = _("Credit override %(q)s v%(v)s") % {
                "q": rec.quotation_id.name or "",
                "v": rec.version or 0,
            }

    @api.model_create_multi
    def create(self, vals_list):
        if not _has(self.env, FINANCE):
            raise UserError(_("Only Finance (Accounting Administrator) overrides the credit gate."))
        Quote = self.env["fix.quotation"]
        for vals in vals_list:
            quote = Quote.browse(vals.get("quotation_id")).exists()
            if not quote:
                raise UserError(_("Name the quotation Finance lets through."))
            if quote.state not in ("draft", "approved", "sent"):
                raise UserError(_("Quotation %s is already decided.") % quote.name)
            if not self.env.su and quote.create_uid == self.env.user:
                raise UserError(
                    _("Segregation of duties: the quotation's author does not override its gate.")
                )
            blocked = quote._credit_block_reason()
            if not blocked:
                raise UserError(
                    _("Customer %s is within credit and not on hold: no override is needed.")
                    % quote.customer_id.display_name
                )
            if not _norm(vals.get("reason")):
                raise ValidationError(_("Say why Finance lets this quotation through."))
            if self.sudo().search_count(
                [
                    ("quotation_id", "=", quote.id),
                    ("version", "=", quote.version),
                    ("revoked", "=", False),
                ]
            ):
                raise UserError(_("Quotation %s already has a credit override.") % quote.name)
            vals.update(
                {
                    "version": quote.version,
                    "amount_total": quote.amount_total,
                    "block_reason": blocked,
                    "granted_by_id": False if self.env.su else self.env.user.id,
                    "granted_at": fields.Datetime.now(),
                    "revoked": False,
                }
            )
        records = super().create(vals_list)
        for rec in records:
            rec.quotation_id.sudo().message_post(
                author_id=self.env.user.partner_id.id,
                body=_("Credit gate overridden by Finance (%(b)s): %(r)s")
                % {"b": rec.block_reason, "r": rec.reason},
            )
        return records

    def write(self, vals):
        if not self.env.su:
            raise UserError(_("A credit override is a record: revoke it and grant a new one."))
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(_("A credit override is kept with its quotation; revoke it instead."))
        return super().unlink()

    def action_revoke(self):
        if not _has(self.env, FINANCE):
            raise UserError(_("Only Finance revokes a credit override."))
        for rec in self:
            if rec.quotation_id.state not in ("draft", "approved", "sent"):
                raise UserError(_("The quotation is already decided."))
            rec.sudo().write({"revoked": True})
            rec.quotation_id.sudo().message_post(
                author_id=self.env.user.partner_id.id, body=_("Credit override revoked by Finance.")
            )
        return True


# =============================================================================
# p7 — legal hold (BRU-QTE-17, T-14)
# =============================================================================
class FixQuotationLegalHold(models.Model):
    _name = "fix.quotation.legal.hold"
    _description = "Quotation Legal Hold"
    _inherit = ["mail.thread"]
    _order = "id desc"

    quotation_id = fields.Many2one("fix.quotation", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="quotation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="quotation_id.operating_unit_id", store=True, index=True
    )
    customer_id = fields.Many2one(
        "res.partner", related="quotation_id.customer_id", store=True, string="Customer"
    )
    version = fields.Integer(string="Quotation Version", readonly=True)
    dispute_ref = fields.Char(string="Dispute / Case Ref", required=True)
    reason = fields.Text(string="What Is Disputed", required=True)
    state = fields.Selection(
        [("active", "On hold"), ("released", "Released")],
        default="active",
        required=True,
        readonly=True,
    )
    placed_by_id = fields.Many2one("res.users", string="Placed By", readonly=True)
    placed_at = fields.Datetime(readonly=True)
    released_by_id = fields.Many2one("res.users", string="Released By", readonly=True)
    released_at = fields.Datetime(readonly=True)
    release_note = fields.Char(string="Why It Is Released", compute="_compute_inputs")
    release_reason = fields.Char(readonly=True)

    def _compute_inputs(self):
        for rec in self:
            rec.release_note = False

    @api.depends("quotation_id.name", "dispute_ref")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (rec.quotation_id.name or "", rec.dispute_ref or "")

    @api.model_create_multi
    def create(self, vals_list):
        Quote = self.env["fix.quotation"]
        for vals in vals_list:
            quote = Quote.browse(vals.get("quotation_id")).exists()
            if not quote:
                raise UserError(_("Name the quotation under dispute."))
            if not _norm(vals.get("dispute_ref")) or not _norm(vals.get("reason")):
                raise ValidationError(_("Give the dispute reference and what is disputed."))
            if self.sudo().search_count(
                [("quotation_id", "=", quote.id), ("state", "=", "active")]
            ):
                raise UserError(_("Quotation %s is already on legal hold.") % quote.name)
            vals.update(
                {
                    "version": quote.version,
                    "state": "active",
                    "placed_by_id": False if self.env.su else self.env.user.id,
                    "placed_at": fields.Datetime.now(),
                }
            )
            for stamp in ("released_by_id", "released_at", "release_reason"):
                vals.pop(stamp, None)
        records = super().create(vals_list)
        for rec in records:
            rec.quotation_id.sudo().message_post(
                author_id=self.env.user.partner_id.id,
                body=_("Legal hold placed (%(d)s): %(r)s")
                % {"d": rec.dispute_ref, "r": rec.reason},
            )
        return records

    def write(self, vals):
        if not self.env.su:
            raise UserError(_("A legal hold is changed only by releasing it."))
        return super().write(vals)

    def unlink(self):
        if not self.env.su or self.filtered(lambda h: h.state == "active"):
            raise UserError(_("A legal hold is never deleted; release it."))
        return super().unlink()

    def action_release(self, note=None):
        """The Commercial Manager releases a hold, never the person who placed it."""
        note = (note or "").strip()
        if not _has(self.env, MANAGER):
            raise UserError(_("Only the Commercial Manager releases a legal hold."))
        for rec in self:
            if rec.state != "active":
                raise UserError(_("Hold %s is already released.") % rec.display_name)
            if not self.env.su and rec.placed_by_id == self.env.user:
                raise UserError(
                    _("Segregation of duties: whoever placed the hold does not release it.")
                )
            if not note:
                raise UserError(_("Say why the dispute no longer needs the hold."))
            rec.sudo().write(
                {
                    "state": "released",
                    "released_by_id": self.env.user.id,
                    "released_at": fields.Datetime.now(),
                    "release_reason": note,
                }
            )
            rec.quotation_id.sudo().message_post(
                author_id=self.env.user.partner_id.id, body=_("Legal hold released: %s") % note
            )
        return True


# =============================================================================
# p1 — technical review / second opinion of an estimate (FR-QTE-009)
# =============================================================================
class FixEstimateReview(models.Model):
    _name = "fix.estimate.review"
    _description = "Estimate Technical Review (second opinion)"
    _inherit = ["mail.thread"]
    _order = "id desc"

    estimate_id = fields.Many2one("fix.estimate", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="estimate_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="estimate_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="estimate_id.currency_id")
    estimate_total = fields.Monetary(
        related="estimate_id.grand_total", string="Estimate Total", currency_field="currency_id"
    )
    reason = fields.Selection(
        [
            ("high_value", "High value"),
            ("contentious", "Contentious / disputed diagnosis"),
            ("unusual_scope", "Unusual or non-catalogue scope"),
            ("customer_request", "Customer asked for a second opinion"),
        ],
        string="Why a Review",
        required=True,
    )
    question = fields.Text(string="What the Reviewer Should Check", required=True)
    reviewer_id = fields.Many2one(
        "res.users",
        string="Senior Technician / Specialist",
        required=True,
        domain=[("share", "=", False)],
    )
    state = fields.Selection(
        [
            ("requested", "Awaiting review"),
            ("cleared", "Cleared"),
            ("returned", "Returned for rework"),
        ],
        default="requested",
        required=True,
        readonly=True,
    )
    requested_by_id = fields.Many2one("res.users", string="Requested By", readonly=True)
    findings = fields.Text(readonly=True)
    decided_at = fields.Datetime(readonly=True)
    # the decision form's inputs (never stored)
    decision_choice = fields.Selection(
        [("cleared", "Cleared: the build-up is sound"), ("returned", "Return for rework")],
        string="Outcome",
        compute="_compute_inputs",
    )
    findings_entry = fields.Text(string="Findings", compute="_compute_inputs")

    def _compute_inputs(self):
        for rec in self:
            rec.decision_choice = False
            rec.findings_entry = False

    @api.depends("estimate_id", "reason")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = _("Review of %s") % (rec.estimate_id.display_name or "")

    @api.model_create_multi
    def create(self, vals_list):
        Estimate = self.env["fix.estimate"]
        for vals in vals_list:
            est = Estimate.browse(vals.get("estimate_id")).exists()
            if not est:
                raise UserError(_("Name the estimate to review."))
            if est.state not in ("draft", "sent", "approved"):
                raise UserError(
                    _("Estimate %(e)s is %(s)s: there is nothing left to review.")
                    % {"e": est.display_name, "s": est.state}
                )
            if not self.env.su and vals.get("reviewer_id") == self.env.user.id:
                raise UserError(_("A second opinion comes from someone else."))
            if self.sudo().search_count(
                [("estimate_id", "=", est.id), ("state", "=", "requested")]
            ):
                raise UserError(_("Estimate %s already awaits its review.") % est.display_name)
            vals.update(
                {
                    "state": "requested",
                    "requested_by_id": False if self.env.su else self.env.user.id,
                }
            )
            for stamp in ("findings", "decided_at"):
                vals.pop(stamp, None)
        records = super().create(vals_list)
        for rec in records:
            rec.sudo().message_subscribe(partner_ids=rec.reviewer_id.partner_id.ids)
        return records

    def write(self, vals):
        if not self.env.su:
            if self.filtered(lambda r: r.state != "requested"):
                raise UserError(_("A decided review is a record: it is not edited."))
            if _changed(
                self, {k: v for k, v in vals.items() if k in ("estimate_id", "reviewer_id")}
            ):
                if self.filtered(lambda r: r.requested_by_id != self.env.user):
                    raise UserError(_("Only whoever asked for the review changes who reviews it."))
                if vals.get("reviewer_id") == self.env.user.id:
                    raise UserError(_("A second opinion comes from someone else."))
        return super().write(vals)

    def unlink(self):
        if not self.env.su and self.filtered(lambda r: r.state != "requested"):
            raise UserError(_("A decided review is kept with its estimate."))
        return super().unlink()

    def action_decide(self, decision=None, findings=None):
        findings = (findings or "").strip()
        for rec in self:
            if rec.state != "requested":
                raise UserError(_("This review is already decided."))
            if not self.env.su and rec.reviewer_id != self.env.user:
                raise UserError(
                    _("Only the named reviewer (%s) records the outcome.") % rec.reviewer_id.name
                )
            if decision not in ("cleared", "returned"):
                raise UserError(_("Choose the outcome: cleared or returned."))
            if not findings:
                raise UserError(_("Write the reviewer's findings."))
            rec.sudo().write(
                {"state": decision, "findings": findings, "decided_at": fields.Datetime.now()}
            )
            rec.sudo().message_post(
                author_id=self.env.user.partner_id.id,
                body=_("Technical review %s: %s") % (decision, findings),
            )
        return True


class FixEstimateReviews(models.Model):
    _inherit = "fix.estimate"

    review_ids = fields.One2many("fix.estimate.review", "estimate_id", string="Technical Reviews")

    def _review_blocker(self):
        """The latest review decides: awaiting, or returned for rework, stops
        the estimate becoming a quotation (FR-QTE-009)."""
        self.ensure_one()
        latest = self.sudo().review_ids.sorted("id", reverse=True)[:1]
        if latest.state == "requested":
            return _("Estimate %s awaits its technical review.") % self.display_name
        if latest.state == "returned":
            return (
                _("Estimate %s was returned by its technical review; rework it and ask again.")
                % self.display_name
            )
        return False


# =============================================================================
# p9 — tender document checklist (FR-QTE-046, BRU-QTE-15)
# =============================================================================
TENDER_DOC_TYPES = [
    ("tender_security", "Tender / bid security"),
    ("trade_licence", "Trade licence"),
    ("etin", "e-TIN / tax return certificate"),
    ("bin", "VAT registration (BIN)"),
    ("bank_solvency", "Bank solvency certificate"),
    ("experience", "Experience / completion certificate"),
    ("manufacturer_auth", "Manufacturer's authorisation"),
    ("technical", "Technical specification / brochure"),
    ("price_schedule", "Price schedule (BOQ)"),
    ("power_of_attorney", "Power of attorney"),
    ("declaration", "Declaration / undertaking"),
    ("other", "Other annexe"),
]


class FixTenderDocument(models.Model):
    _name = "fix.tender.document"
    _description = "Tender Submission Document (checklist)"
    _order = "tender_id, sequence, id"

    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="tender_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="tender_id.operating_unit_id", store=True, index=True
    )
    tender_state = fields.Selection(related="tender_id.state", string="Tender State")
    sequence = fields.Integer(default=10)
    document_type = fields.Selection(TENDER_DOC_TYPES, string="Document", required=True)
    name = fields.Char(string="Title / Annexe No.", required=True)
    required = fields.Boolean(default=True)
    attachment_id = fields.Many2one("ir.attachment", string="The Document (upload)")
    reference = fields.Char(string="Issuing Ref / Certificate No.")
    valid_until = fields.Date()
    state = fields.Selection(
        [("missing", "Missing"), ("ready", "Ready"), ("waived", "Not required by the issuer")],
        compute="_compute_state",
        store=True,
    )
    version = fields.Integer(readonly=True, default=0)
    checksum = fields.Char(string="Document Checksum", readonly=True)
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True)

    @api.depends("required", "attachment_id", "valid_until")
    def _compute_state(self):
        for rec in self:
            if rec.attachment_id:
                rec.state = "ready"
            else:
                rec.state = "missing" if rec.required else "waived"

    def _assert_tender_open(self, tenders):
        if self.env.su:
            return
        if not _has(self.env, BID):
            raise UserError(_("The Bid Coordinator assembles the submission pack."))
        lodged = tenders.filtered(lambda t: t.state != "draft")
        if lodged:
            raise UserError(
                _("The submission pack of tender %(t)s is frozen: the bid is %(s)s.")
                % {"t": lodged[0].name, "s": lodged[0].state}
            )

    def _stamp_upload(self, vals):
        att = self.env["ir.attachment"].browse(vals.get("attachment_id")).exists()
        if att:
            if not self.env.su and att.create_uid != self.env.user:
                raise UserError(_("Attach a document you uploaded yourself."))
            vals["checksum"] = att.sudo().checksum or (
                hashlib.sha256(att.sudo().raw).hexdigest() if att.sudo().raw else False
            )
            vals["prepared_by_id"] = False if self.env.su else self.env.user.id
        return att

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v["tender_id"] for v in vals_list if v.get("tender_id")]
        self._assert_tender_open(self.env["fix.tender"].browse(ids).exists())
        for vals in vals_list:
            for stamp in ("version", "checksum", "prepared_by_id"):
                vals.pop(stamp, None)
            if self._stamp_upload(vals):
                vals["version"] = 1
        records = super().create(vals_list)
        records._check_dates()
        return records

    def write(self, vals):
        self._assert_tender_open(self.mapped("tender_id"))
        if "tender_id" in vals and _changed(self, {"tender_id": vals["tender_id"]}):
            raise UserError(_("A document stays on its tender's checklist."))
        if not self.env.su:
            for stamp in ("version", "checksum", "prepared_by_id"):
                vals.pop(stamp, None)
        if "attachment_id" in vals and _changed(self, {"attachment_id": vals["attachment_id"]}):
            for rec in self:
                one = dict(vals)
                rec._stamp_upload(one)
                one["version"] = (rec.version or 0) + 1 if one.get("attachment_id") else rec.version
                if not one.get("attachment_id"):
                    one.update({"checksum": False})
                super(FixTenderDocument, rec).write(one)
            self._check_dates()
            return True
        res = super().write(vals)
        self._check_dates()
        return res

    def unlink(self):
        self._assert_tender_open(self.mapped("tender_id"))
        return super().unlink()

    def _check_dates(self):
        for rec in self:
            if (
                rec.valid_until
                and rec.tender_id.due_date
                and rec.valid_until < rec.tender_id.due_date
            ):
                raise ValidationError(
                    _("%(d)s expires on %(v)s, before the submission deadline %(t)s.")
                    % {"d": rec.name, "v": rec.valid_until, "t": rec.tender_id.due_date}
                )


# =============================================================================
# p9 — tender outcome with a governed loss reason (FR-QTE-048, BRU-QTE-16)
# =============================================================================
TENDER_LOSS_REASONS = [
    ("price", "Price higher than the winner"),
    ("technical", "Technically non-responsive"),
    ("documents", "Disqualified: documents incomplete"),
    ("bid_security", "Disqualified: bid security"),
    ("eligibility", "Experience / eligibility not met"),
    ("late", "Late or incomplete submission"),
    ("issuer_cancelled", "Tender cancelled by the issuer"),
    ("other", "Other"),
]


class FixTenderOutcome(models.Model):
    """The outcome of a submitted tender that was not won (spec entity
    fix.tender.outcome). A win is the Tender Committee's award decision."""

    _name = "fix.tender.outcome"
    _description = "Tender Outcome (loss analysis)"
    _order = "id desc"

    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="tender_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="tender_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="tender_id.currency_id")
    client_name = fields.Char(related="tender_id.client_name", string="Issuer")
    result = fields.Selection(
        [("lost", "Lost to another bidder"), ("cancelled", "Cancelled by the issuer")],
        required=True,
        default="lost",
    )
    loss_reason_code = fields.Selection(
        TENDER_LOSS_REASONS, string="Loss Reason (governed)", required=True
    )
    awarded_to = fields.Char(string="Awarded To")
    winning_value = fields.Monetary(
        string="Winning Price (where disclosed)", currency_field="currency_id"
    )
    our_value = fields.Monetary(string="Our Bid", readonly=True, currency_field="currency_id")
    price_gap_pct = fields.Float(string="Our Price vs Winner (%)", readonly=True)
    notes = fields.Text(string="What Was Learned", required=True)
    recorded_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)

    @api.depends("tender_id.name", "result")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (rec.tender_id.name or "", rec.result or "")

    @api.model_create_multi
    def create(self, vals_list):
        if not (_has(self.env, BID) or _has(self.env, MANAGER)):
            raise UserError(_("The Bid Coordinator records a tender's outcome."))
        Tender = self.env["fix.tender"]
        labels = dict(TENDER_LOSS_REASONS)
        prepared = []
        for vals in vals_list:
            tender = Tender.browse(vals.get("tender_id")).exists()
            if not tender:
                raise UserError(_("Name the tender."))
            if tender.state != "submitted":
                raise UserError(
                    _("Tender %(t)s is %(s)s: an outcome is recorded for a submitted bid.")
                    % {"t": tender.name, "s": tender.state}
                )
            code = vals.get("loss_reason_code")
            if code not in labels:
                raise UserError(_("Choose the loss reason from the governed list (BRU-QTE-16)."))
            if vals.get("result") == "cancelled" and code != "issuer_cancelled":
                vals["loss_reason_code"] = code = "issuer_cancelled"
            if not _norm(vals.get("notes")):
                raise ValidationError(_("Write what was learned from the outcome."))
            ours = tender.bid_value or 0.0
            win = vals.get("winning_value") or 0.0
            if win < 0:
                raise ValidationError(_("A winning price cannot be negative."))
            vals.update(
                {
                    "our_value": ours,
                    "price_gap_pct": round((ours - win) / win * 100.0, 2) if win else 0.0,
                    "recorded_by_id": False if self.env.su else self.env.user.id,
                }
            )
            prepared.append((tender, vals))
        records = super().create(vals_list)
        for (tender, _vals), rec in zip(prepared, records, strict=True):
            reason = "%s: %s" % (labels[rec.loss_reason_code], _norm(rec.notes))
            ctx = tender.with_context(fix_tender_loss_code=rec.loss_reason_code)
            # a loss is stamped by action_record_loss from the context; a
            # cancellation has no such hook, so it is stamped here
            stamp = {
                "awarded_to": rec.awarded_to or False,
                "winning_value": rec.winning_value or 0.0,
            }
            if rec.result == "cancelled":
                ctx.action_cancel(reason=reason)
                stamp["loss_reason_code"] = rec.loss_reason_code
            else:
                ctx.action_record_loss(reason=reason)
            tender._guarded().write(stamp)
        return records

    def write(self, vals):
        if not self.env.su:
            raise UserError(_("A tender outcome is a record: it is not edited."))
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(_("A tender outcome is kept with its tender."))
        return super().unlink()


class FixTenderCapture2(models.Model):
    _inherit = "fix.tender"

    document_ids = fields.One2many("fix.tender.document", "tender_id", string="Submission Pack")
    outcome_ids = fields.One2many("fix.tender.outcome", "tender_id", string="Outcome")
    loss_reason_code = fields.Selection(
        TENDER_LOSS_REASONS, string="Loss Reason (governed)", readonly=True, copy=False
    )
    missing_document_count = fields.Integer(string="Documents Missing", compute="_compute_pack")
    submission_pack_hash = fields.Char(
        string="Submission Pack Hash (SHA-256)", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"loss_reason_code", "submission_pack_hash"}

    @api.depends("document_ids.state")
    def _compute_pack(self):
        for rec in self:
            rec.missing_document_count = len(
                rec.document_ids.filtered(lambda d: d.state == "missing")
            )

    def _pack_digest(self):
        self.ensure_one()
        rows = [
            "%s|%s|%s|%s" % (d.document_type, d.name, d.version, d.checksum or "")
            for d in self.document_ids.sorted(lambda d: (d.sequence, d.id))
        ]
        return hashlib.sha256("\n".join(rows).encode()).hexdigest()

    def action_submit(self):
        """BRU-QTE-15: no submission while a required document is missing;
        the pack submitted is sealed by its hash."""
        today = dhaka_today(self)
        for rec in self.filtered(lambda t: t.state == "draft"):
            missing = rec.document_ids.filtered(lambda d: d.state == "missing")
            if missing:
                raise UserError(
                    _("Tender %(t)s: %(n)d required document(s) are missing (BRU-QTE-15): %(d)s.")
                    % {"t": rec.name, "n": len(missing), "d": ", ".join(missing.mapped("name"))}
                )
            stale = rec.document_ids.filtered(
                lambda d: d.state == "ready" and d.valid_until and d.valid_until < today
            )
            if stale:
                raise UserError(
                    _("Tender %(t)s: %(d)s expired; attach a current one.")
                    % {"t": rec.name, "d": ", ".join(stale.mapped("name"))}
                )
        res = super().action_submit()
        for rec in self.filtered(lambda t: t.state == "submitted" and t.document_ids):
            rec._guarded().write({"submission_pack_hash": rec._pack_digest()})
        return res

    def action_record_loss(self, reason=None):
        """Every loss carries a governed reason (BRU-QTE-16). The workspace
        records it with Record a Tender Outcome, which names the reason; a
        loss recorded any other way is filed under the governed "Other"."""
        res = super().action_record_loss(reason=reason)
        code = self.env.context.get("fix_tender_loss_code") or "other"
        for rec in self.filtered(lambda t: t.state == "lost" and not t.loss_reason_code):
            rec._guarded().write({"loss_reason_code": code})
        return res


# =============================================================================
# fix.quotation — the gates and the captures above, and the phone acceptance
# =============================================================================
class FixQuotationCapture2(models.Model):
    _inherit = "fix.quotation"

    term_ids = fields.One2many("fix.quotation.term", "quotation_id", string="Terms", copy=True)
    credit_override_ids = fields.One2many(
        "fix.quotation.credit.override", "quotation_id", string="Credit Overrides"
    )
    legal_hold_ids = fields.One2many(
        "fix.quotation.legal.hold", "quotation_id", string="Legal Holds"
    )
    legal_hold = fields.Boolean(string="On Legal Hold", compute="_compute_legal_hold")
    credit_block_reason = fields.Char(string="Credit Gate", compute="_compute_credit_gate")
    renewal_of_contract_id = fields.Many2one(
        "fix.contract",
        string="Renewal Of Contract",
        index=True,
        copy=False,
        domain=[("state", "in", ("active", "expiring", "expired"))],
        help="FR-QTE-024: the expiring contract this quotation renews.",
    )
    acceptance_method = fields.Selection(
        selection_add=[("phone", "Phone call with recorded consent")],
        ondelete={"phone": "set null"},
    )
    # the phone acceptance form's inputs (never stored)
    phone_consent_ref = fields.Char(
        string="Call Recording / Consent Ref", compute="_compute_capture2_inputs"
    )
    phone_called_number = fields.Char(string="Number Called", compute="_compute_capture2_inputs")

    def _compute_capture2_inputs(self):
        for rec in self:
            rec.phone_consent_ref = False
            rec.phone_called_number = False

    @api.depends("legal_hold_ids.state")
    def _compute_legal_hold(self):
        for rec in self:
            rec.legal_hold = any(h.state == "active" for h in rec.sudo().legal_hold_ids)

    @api.depends("customer_id", "amount_total", "company_id")
    def _compute_credit_gate(self):
        for rec in self:
            rec.credit_block_reason = rec._credit_block_reason() or False

    # ---- credit gate -------------------------------------------------------------
    def _credit_block_reason(self):
        """What M20's credit profile says against this customer: on hold, or
        the open receivables plus this quotation over the limit."""
        self.ensure_one()
        if not self.customer_id or "fix.credit.profile" not in self.env:
            return False
        partner = self.customer_id.commercial_partner_id or self.customer_id
        profile = (
            self.env["fix.credit.profile"]
            .sudo()
            .search(
                [
                    ("customer_id", "in", (partner | self.customer_id).ids),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )
        if not profile:
            return False
        if profile.credit_hold:
            return _("on credit hold (%s)") % (profile.hold_reason or _("no reason recorded"))
        if profile.credit_limit and (profile.exposure or 0.0) + (self.amount_total or 0.0) > (
            profile.credit_limit + 0.005
        ):
            return _(
                "over the credit limit: open BDT %(e).2f + this quotation BDT %(q).2f > limit BDT %(l).2f"
            ) % {
                "e": profile.exposure or 0.0,
                "q": self.amount_total or 0.0,
                "l": profile.credit_limit,
            }
        return False

    def _assert_credit_gate(self, what):
        for rec in self:
            blocked = rec._credit_block_reason()
            if not blocked:
                continue
            override = rec.sudo().credit_override_ids.filtered(
                lambda o, rec=rec: o.version == rec.version and not o.revoked
            )
            if not override:
                raise UserError(
                    _(
                        "%(w)s: customer %(c)s is %(b)s (BRU-QTE-14). Finance records a Credit "
                        "Override first."
                    )
                    % {"w": what, "c": rec.customer_id.display_name, "b": blocked}
                )

    def action_send(self):
        self._assert_credit_gate(_("Issuing"))
        return super().action_send()

    def _accept(self, method, ref):
        self._assert_credit_gate(_("Accepting"))
        return super()._accept(method, ref)

    # ---- terms, technical review: the readiness guard ------------------------------
    def _readiness_problems(self) -> list:
        problems = super()._readiness_problems()
        terms = self.sudo().term_ids
        for term in terms.filtered(lambda t: t.deviation_state == "pending"):
            problems.append(
                "Non-standard %s '%s' awaits CCO and CFO approval (BRU-QTE-08)."
                % (dict(TERM_TYPES).get(term.term_type), (term.text_en or "")[:60])
            )
        for term in terms.filtered(lambda t: t.deviation_state == "rejected"):
            problems.append(
                "Non-standard term '%s' was rejected: remove or replace it."
                % (term.text_en or "")[:60]
            )
        mandatory = (
            self.env["fix.quotation.standard.term"]
            .sudo()
            .search(
                [
                    ("mandatory", "=", True),
                    ("company_id", "=", self.company_id.id),
                    "|",
                    ("quote_type", "=", False),
                    ("quote_type", "=", self.quote_type),
                ]
            )
        )
        missing = mandatory - terms.mapped("standard_term_id")
        if missing:
            problems.append(
                "Attach the mandatory standard term(s): %s." % ", ".join(missing.mapped("code"))
            )
        est = self.estimate_id.sudo()
        if est:
            blocker = est._review_blocker()
            if blocker:
                problems.append(blocker)
        return problems

    def action_apply_standard_terms(self):
        """Attach every active standard term for this kind of quotation that
        is not on it yet, word for word (no approval needed)."""
        Std = self.env["fix.quotation.standard.term"].sudo()
        Term = self.env["fix.quotation.term"]
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Terms are set while the quotation is a draft."))
            have = rec.term_ids.mapped("standard_term_id")
            library = Std.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    "|",
                    ("quote_type", "=", False),
                    ("quote_type", "=", rec.quote_type),
                ]
            )
            add = library - have
            if not add:
                raise UserError(_("Every standard term for this quotation is already on it."))
            Term.create(
                [
                    {
                        "quotation_id": rec.id,
                        "standard_term_id": std.id,
                        "term_type": std.term_type,
                        "sequence": std.sequence,
                    }
                    for std in add
                ]
            )
        return True

    # ---- phone acceptance (FR-QTE-042) -----------------------------------------
    def action_record_phone_acceptance(self, consent_ref=None, called_number=None):
        """Acceptance taken on a call: the call recording / consent reference
        is required, the agent is not the author, and the number called is
        the customer's own."""
        consent_ref = (consent_ref or "").strip()
        called = "".join(ch for ch in (called_number or "") if ch.isdigit())
        for rec in self:
            if rec.state != "sent":
                raise UserError(_("Issue the quotation to the customer first."))
            if not consent_ref:
                raise UserError(_("Give the call recording or consent reference (FR-QTE-042)."))
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError(
                    _(
                        "Segregation of duties: the author of a quotation cannot record the "
                        "customer's acceptance of it."
                    )
                )
            partner = rec.customer_id
            known = {
                "".join(ch for ch in (n or "") if ch.isdigit())[-10:]
                for n in (
                    partner.phone,
                    getattr(partner, "mobile", False),
                    fix_otp_util.bd_mobile(partner) if partner else False,
                )
                if n
            } - {""}
            if not called or called[-10:] not in known:
                raise UserError(_("The number called must be the customer's own phone on record."))
            rec._accept(
                "phone", "PHONE %s (consent %s)" % (called[-4:].rjust(10, "*"), consent_ref)
            )
        return True

    # ---- legal hold: never deleted (BRU-QTE-17) ----------------------------------
    def unlink(self):
        held = self.sudo().filtered("legal_hold")
        if held:
            raise UserError(
                _("Quotation %s is on legal hold (BRU-QTE-17): it cannot be deleted.")
                % held[0].name
            )
        return super().unlink()

    # ---- renewal quotation (FR-QTE-024, BRU-QTE-18) ------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Contract = self.env["fix.contract"]
        for vals in vals_list:
            contract = Contract.browse(vals.get("renewal_of_contract_id")).exists()
            if not contract:
                continue
            contract = contract.sudo()
            if contract.state not in ("active", "expiring", "expired"):
                raise UserError(
                    _("Contract %(c)s is %(s)s: only a contract in force or just ended is renewed.")
                    % {"c": contract.code, "s": contract.state}
                )
            if self.sudo().search_count(
                [
                    ("renewal_of_contract_id", "=", contract.id),
                    ("state", "in", ("draft", "approved", "sent")),
                ]
            ):
                raise UserError(
                    _("Contract %s already has a renewal quotation in progress.") % contract.code
                )
            months = vals.get("contract_months") or 12
            factor = 1.0 + (contract.escalation_pct or 0.0) / 100.0
            vals.update(
                {
                    "quote_type": "contract",
                    "customer_id": contract.customer_id.id,
                    "operating_unit_id": contract.operating_unit_id.id,
                    "company_id": contract.company_id.id,
                    "currency_id": contract.currency_id.id,
                    "contract_family": contract.family
                    if contract.family in dict(self._fields["contract_family"].selection)
                    else "amc",
                    "contract_months": months,
                    "contract_start": contract.date_end + timedelta(days=1),
                }
            )
            if not vals.get("line_ids"):
                scope = contract.scope_line_ids if "scope_line_ids" in contract else []
                if scope:
                    vals["line_ids"] = [
                        (
                            0,
                            0,
                            {
                                "line_type": ln.line_type or "service",
                                "product_id": ln.product_id.id or False,
                                "description": ln.description,
                                "quantity": ln.quantity or 1.0,
                                "unit_price": round((ln.unit_price or 0.0) * factor, 2),
                                "discount_pct": ln.discount_pct or 0.0,
                            },
                        )
                        for ln in scope
                    ]
                else:
                    vals["line_ids"] = [
                        (
                            0,
                            0,
                            {
                                "line_type": "service",
                                "description": _(
                                    "Renewal of %(c)s for %(m)d months (escalation %(e).1f%%)"
                                )
                                % {
                                    "c": contract.code,
                                    "m": months,
                                    "e": contract.escalation_pct or 0.0,
                                },
                                "quantity": 1.0,
                                "unit_price": round(
                                    (contract.annual_value or 0.0) * factor * months / 12.0, 2
                                ),
                            },
                        )
                    ]
        return super().create(vals_list)

    def write(self, vals):
        if (
            "renewal_of_contract_id" in vals
            and not self.env.su
            and _changed(self, {"renewal_of_contract_id": vals["renewal_of_contract_id"]})
        ):
            raise UserError(_("A renewal quotation stays on the contract it renews."))
        return super().write(vals)

    def _convert(self):
        res = super()._convert()
        for rec in self.filtered("renewal_of_contract_id"):
            if rec.converted_res_model != "fix.contract" or not rec.converted_res_id:
                continue
            new = self.env["fix.contract"].sudo().browse(rec.converted_res_id)
            old = rec.renewal_of_contract_id.sudo()
            live = old.renewal_ids.filtered(lambda r: r.state not in ("terminated", "expired"))
            if new.exists() and not new.renewed_from_id and not (live - new):
                new._guarded().write({"renewed_from_id": old.id})
                old.sudo().message_post(
                    author_id=self.env.user.partner_id.id,
                    body=_("Renewed by quotation %(q)s v%(v)d: %(n)s")
                    % {"q": rec.name, "v": rec.version, "n": new.display_name},
                )
        return res
