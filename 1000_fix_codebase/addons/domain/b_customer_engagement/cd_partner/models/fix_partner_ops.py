# M40 partner programmes: brand authorisations, deal registrations, rebates,
# franchise agreements, channel conflicts and technical audits on top of
# fix.partner / fix.referral.
#
# A04 workflow audit (2026-11-03) M40-1..6/11/12: none of these had a real
# lifecycle. A clerk wrote a deal "won", an authorisation "active" with a
# typed certificate for a prospective partner, a rebate "paid" (and raised it
# from 3,000 to 5,000,000 afterwards, at a 250% rate), a franchise "active"
# with its end before its start; the rebate audit gate had a caller-supplied
# bypass (skip_audit_score_check); and a conflict ruling was forged by
# writing the state, decision and arbitrator, then changed after the ruling.
# Every state, stamp, ruling and amount here is now guarded
# (fix.guarded.mixin) and moves only through the actions below, each with its
# role and segregation of duties; the rebate payout is a routed DOFA approval
# (M63) with the amount pinned.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_partner import (
    AUDIT_PASS_SCORE,
    AUDIT_VALIDITY_DAYS,
    EARNING_STATES,
    GROUP_MANAGER,
    GROUP_OFFICER,
    GROUP_REBATE_APPROVER,
    GROUP_TIER3,
    fix_not_creator,
    fix_require,
)

# A04 audit (2026-11-04): business defaults the business must confirm (report
# §7.5). BRU-PCM-09: a registered deal is protected for 90 days, with a
# warning 30 days before it lapses; an authorisation warns 30 days ahead.
DEAL_PROTECTION_DAYS = 90
EXPIRY_WARNING_DAYS = 30
# A04 ERP audit M40-F14 (AUT-PCM-04, BRU-PCM-07): a brand authorisation
# escalates at T-180, T-90 and T-30 days, each threshold once, to a wider
# audience: the channel managers (Finance Director's delegate), DOFA Tier 3
# (CCO), DOFA Tier 5 (CEO). The audience per threshold is an OWNER mapping.
AUTHORISATION_WARNINGS = (
    (180, GROUP_MANAGER),
    (90, "cd_entity_config.group_dofa_tier_3"),
    (30, "cd_entity_config.group_dofa_tier_5"),
)
# A04 ERP audit M40-F12: M20 invoice states that count as paid revenue.
REBATE_BASIS_STATES = ("paid",)
# A04 ERP audit M40-F3/F13: the settlement account roles a partner payout
# accrues to (cd_settlement_ext.account_code.<role>). The expense roles have
# no default: unset, the approval is refused (fail closed). Recommended on
# fix_real: partner_rebate_payout 500306 Sales Commission, partner_mdf_expense
# 500210 Marketing Expense; partner_payable is 32656556, tds_payable 200905.
PAYOUT_ACCOUNT_PARAM = "cd_settlement_ext.account_code.%s"
PAYOUT_ROLE_LABELS = {
    "partner_rebate_payout": "Channel partner rebate expense",
    "partner_mdf_expense": "Partner market development fund (MDF) expense",
    "partner_payable": "Partner payable",
    "tds_payable": "TDS withheld liability",
}
PAYOUT_ROLE_DEFAULTS = {"tds_payable": "210100"}


def payout_account(env, company, role):
    """The configured settlement account of a payout role, or a refusal that
    names the parameter to set. Never guessed."""
    param = PAYOUT_ACCOUNT_PARAM % role
    code = env["ir.config_parameter"].sudo().get_param(param) or PAYOUT_ROLE_DEFAULTS.get(role)
    if not code:
        raise UserError(
            "No GL account is configured for %s in %s: set system parameter %s. Nothing is "
            "approved for payment until it is (fail closed)."
            % (PAYOUT_ROLE_LABELS.get(role, role), company.name, param)
        )
    account = (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not account:
        raise UserError(
            "%s names account %s, which %s does not have (%s)."
            % (param, code, company.name, PAYOUT_ROLE_LABELS.get(role, role))
        )
    return account


def assert_payout_accounts(env, company, expense_role):
    """Refuse unless the expense, payable and TDS accounts of a payout exist."""
    for role in (expense_role, "partner_payable", "tds_payable"):
        payout_account(env, company, role)


def executed_payout(rec, label):
    """The M50 payout instruction raised for `rec`, refused unless executed."""
    if "fix.payment.execution" not in rec.env:
        raise UserError("%s: the M50 payment module is not installed." % label)
    pay = (
        rec.env["fix.payment.execution"]
        .sudo()
        .search([("source_model", "=", rec._name), ("source_id", "=", rec.id)], limit=1)
    )
    if not pay:
        raise UserError(
            "%s has no M50 payout instruction yet (the approval's hand-off raises it): nothing "
            "is paid before it is." % label
        )
    if pay.state != "executed":
        raise UserError(
            "%s: payout %s is %s - it is paid when treasury's instruction is executed and the "
            "bank confirms it, not on a typed reference." % (label, pay.name, pay.state)
        )
    return pay


# A04 ERP audit M40-F26: where a market development fund is raised now.
MDF_POINTER = (
    "A market development fund is no longer raised as a rebate: allocate it on an MDF Fund "
    "(M40 > MDF Funds) and pay it on an evidenced MDF Claim (M40 > MDF Claims), which "
    "accrues it and raises its M50 payout (M40-F26, one MDF mechanism)."
)

# The highest rebate / MDF rate accepted, as a fraction. Report §7.5 leaves
# the bound to the business; 20% is the default until it rules.
REBATE_MAX_RATE = 0.20
# The rebate payout ladder reuses the estate's third-party payout ladder (the
# M03 damage-claim payout): Tier 2 up to BDT 15,000, Tier 3 up to 50,000,
# Tier 4 above. A default the business must confirm.
REBATE_DOFA_THRESHOLDS = [
    (15000.0, "tier_2"),
    (50000.0, "tier_3"),
    (float("inf"), "tier_4"),
]
# Who records that an approved rebate was actually paid: finance.
GROUP_FINANCE = "account.group_account_invoice"


def _refuse_frozen(rec, vals, frozen, why):
    changed = [
        n
        for n in frozen & set(vals)
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


class FixApprovalMatrixPartner(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("partner_rebate", "Partner Rebate / MDF Payout")],
        ondelete={"partner_rebate": "cascade"},
    )


class FixPartnerAudit(models.Model):
    """A04 audit M40-2: the technical audit behind the 85% rebate gate.

    The score used to be a field anyone typed (default 85, a pass). It is now
    the result of an audit with its evidence, submitted by the auditor and
    approved by a channel manager who is not the auditor."""

    _name = "fix.partner.audit"
    _description = "Partner Technical Audit"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "audit_date desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    # A04 ERP audit M40-F27: the child registers carry their partner's company.
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    audit_date = fields.Date(required=True, default=fields.Date.context_today)
    score = fields.Float(string="Audit Score (%)", required=True, default=0.0)
    findings = fields.Text()
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Audit Report", copy=False, ondelete="restrict"
    )
    auditor_id = fields.Many2one(
        "res.users", string="Auditor", readonly=True, copy=False, default=lambda self: self.env.user
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    rejection_reason = fields.Char(readonly=True, copy=False)
    valid_until = fields.Date(compute="_compute_valid_until")

    _FROZEN = frozenset({"partner_id", "audit_date", "score", "findings", "evidence_attachment_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "auditor_id",
            "approved_by_id",
            "approved_at",
            "rejection_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "draft":
            locked |= self._FROZEN
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                _refuse_frozen(rec, vals, self._FROZEN, "the audit is %s" % rec.state)
        return super().write(vals)

    @api.depends("audit_date")
    def _compute_valid_until(self):
        for rec in self:
            rec.valid_until = (
                rec.audit_date + timedelta(days=AUDIT_VALIDITY_DAYS) if rec.audit_date else False
            )

    @api.constrains("score")
    def _check_score(self):
        for rec in self:
            if not 0.0 <= rec.score <= 100.0:
                raise ValidationError("An audit score is between 0 and 100%.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.partner.audit") or "New"
        return super().create(vals_list)

    def action_submit(self):
        fix_require(self.env, [GROUP_OFFICER], "Submitting a technical audit")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft audit can be submitted.")
            if not rec.evidence_attachment_id:
                raise UserError("Attach the audit report before submitting the audit.")
            rec._guarded().write({"state": "submitted", "auditor_id": self.env.uid})
        return True

    def action_approve(self):
        fix_require(self.env, [GROUP_MANAGER], "Approving a technical audit")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted audit can be approved.")
            fix_not_creator(self.env, rec, "approving it")
            if not self.env.su and rec.auditor_id == self.env.user:
                raise UserError(
                    "Segregation of duties: the auditor does not approve their own audit."
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Rejecting a technical audit")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a submitted audit can be rejected.")
            rec._guarded().write({"state": "rejected", "rejection_reason": reason or False})
        return True


class FixPartnerAuthorisation(models.Model):
    """BRU-PCM-07/08: a brand authorisation is active only between its dates,
    on a certificate document, for an onboarded partner; it lapses by itself
    and warns before it does."""

    _name = "fix.partner.authorisation"
    _description = "Partner Brand Authorisation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "valid_to, id"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    brand_id = fields.Many2one("fix.brand", string="Brand", index=True)
    scope = fields.Char(help="What the authorisation covers (service types, product lines).")
    valid_from = fields.Date(required=True)
    valid_to = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired"), ("revoked", "Revoked")],
        required=True,
        default="draft",
        tracking=True,
    )
    certificate_ref = fields.Char()
    certificate_attachment_id = fields.Many2one(
        "ir.attachment", string="Certificate Document", copy=False, ondelete="restrict"
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)
    revoked_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    revoke_reason = fields.Char(readonly=True, copy=False)
    expiry_warned = fields.Boolean(readonly=True, copy=False)
    # A04 ERP audit M40-F14: the smallest escalation threshold (days) fired
    expiry_warned_days = fields.Integer(readonly=True, copy=False)

    _FROZEN = frozenset(
        {
            "partner_id",
            "brand_id",
            "scope",
            "valid_from",
            "valid_to",
            "certificate_ref",
            "certificate_attachment_id",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "revoked_by_id",
            "revoke_reason",
            "expiry_warned",
            "expiry_warned_days",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "draft":
            locked |= self._FROZEN
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                _refuse_frozen(rec, vals, self._FROZEN, "the authorisation is %s" % rec.state)
        return super().write(vals)

    # ---- A04 ERP audit M40-F14 (BRU-PCM-08): the brand-work gate ----------
    @api.model
    def fix_brand_authorisation(self, brand, on_date=None, company=None):
        """The active authorisation that covers work on `brand` (fix.brand
        record or id) on `on_date`, held by an onboarded brand partner, or an
        empty recordset. M09 / M01 call this before brand work."""
        brand_id = brand.id if hasattr(brand, "id") else int(brand or 0)
        if not brand_id:
            return self.browse()
        day = on_date or fields.Date.context_today(self)
        dom = [
            ("brand_id", "=", brand_id),
            ("state", "=", "active"),
            ("valid_from", "<=", day),
            ("valid_to", ">=", day),
            ("partner_id.state", "in", EARNING_STATES),
        ]
        if company:
            dom.append(("partner_id.company_id", "=", company.id))
        return self.sudo().search(dom, order="valid_to desc", limit=1)

    @api.model
    def fix_assert_brand_authorised(self, brand, what, on_date=None, company=None):
        """Refuse `what` on a brand with no valid authorisation (BRU-PCM-08)."""
        auth = self.fix_brand_authorisation(brand, on_date=on_date, company=company)
        if not auth:
            name = brand.display_name if hasattr(brand, "display_name") else brand
            raise UserError(
                "%s refused: 1000FiX holds no valid brand authorisation for %s on %s - the "
                "authorisation lapsed, was revoked or was never activated (BRU-PCM-08)."
                % (what, name, on_date or fields.Date.context_today(self))
            )
        return auth

    @api.constrains("valid_from", "valid_to")
    def _check_dates(self):
        for rec in self:
            if rec.valid_from and rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError(
                    "Authorisation %s ends (%s) before it starts (%s)."
                    % (rec.name, rec.valid_to, rec.valid_from)
                )

    def action_activate(self):
        fix_require(self.env, [GROUP_MANAGER], "Activating a brand authorisation")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft authorisation can be activated.")
            fix_not_creator(self.env, rec, "activating it")
            if rec.partner_id.state not in EARNING_STATES:
                raise ValidationError(
                    "Partner %s is %s: only an onboarded partner holds a brand "
                    "authorisation (BRU-PCM-01)." % (rec.partner_id.name, rec.partner_id.state)
                )
            if not (rec.certificate_ref or "").strip() or not rec.certificate_attachment_id:
                raise ValidationError(
                    "Activate on the brand's certificate: its number and the certificate "
                    "document."
                )
            if rec.valid_to < today:
                raise ValidationError(
                    "Authorisation %s already lapsed on %s." % (rec.name, rec.valid_to)
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
        return True

    def action_revoke(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Revoking a brand authorisation")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("State why the authorisation is revoked.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active authorisation can be revoked.")
            rec._guarded().write(
                {"state": "revoked", "revoked_by_id": self.env.uid, "revoke_reason": reason}
            )
        return True

    @api.model
    def cron_authorisation_expiry(self):
        """A04 audit C10: an active authorisation lapses once its validity
        ends. A04 ERP audit M40-F14 (AUT-PCM-04): it escalates at T-180, T-90
        and T-30 days (partner.authorisation_expiring, once per threshold,
        consumed below), not only at 30. Idempotent."""
        today = fields.Date.context_today(self)
        active = self.sudo().search([("state", "=", "active")])
        lapsed = active.filtered(lambda a: a.valid_to < today)
        if lapsed:
            lapsed._guarded().write({"state": "expired"})
        warned = 0
        for auth in active - lapsed:
            days_left = (auth.valid_to - today).days
            due = [d for d, _g in AUTHORISATION_WARNINGS if days_left <= d]
            if not due:
                continue
            threshold = min(due)
            if auth.expiry_warned_days and auth.expiry_warned_days <= threshold:
                continue
            publish(
                auth.env,
                "partner.authorisation_expiring",
                "fix.partner.authorisation",
                auth.id,
                {
                    "authorisation": auth.name,
                    "partner_id": auth.partner_id.id,
                    "brand_id": auth.brand_id.id or None,
                    "valid_to": fields.Date.to_string(auth.valid_to),
                    "days_left": days_left,
                    "threshold": threshold,
                },
            )
            auth._guarded().write(
                {"expiry_warned": threshold <= EXPIRY_WARNING_DAYS, "expiry_warned_days": threshold}
            )
            warned += 1
        return len(lapsed) + warned

    @api.model
    def consume_partner_authorisation_expiring(self, event: dict) -> dict:
        """A04 ERP audit X3 / M40-F14: the escalation reaches people. Each
        threshold opens a to-do on the authorisation for the holders of its
        audience (180: channel managers, 90: DOFA Tier 3, 30: DOFA Tier 5).
        Relay only; idempotent per (authorisation, threshold)."""
        if not self.env.su:
            raise AccessError("Partner consumers run only from the event relay.")
        try:
            auth = self.sudo().browse(int(event.get("aggregate_id") or 0)).exists()
        except (TypeError, ValueError):
            auth = self.browse()
        if not auth:
            raise UserError("Authorisation hand-off refused: no such authorisation.")
        payload = event.get("payload") or {}
        try:
            threshold = int(payload.get("threshold") or EXPIRY_WARNING_DAYS)
        except (TypeError, ValueError):
            threshold = EXPIRY_WARNING_DAYS
        group_xmlid = dict(AUTHORISATION_WARNINGS).get(threshold, GROUP_MANAGER)
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        users = (group.sudo().all_user_ids if group else self.env["res.users"]).filtered(
            lambda u: not u.share and u.active
        )
        summary = "Brand authorisation %s expires in %d days (T-%d)" % (
            auth.name,
            max((auth.valid_to - fields.Date.context_today(self)).days, 0),
            threshold,
        )
        Activity = self.env["mail.activity"].sudo()
        model_id = self.env["ir.model"]._get_id(self._name)
        made = 0
        for user in users:
            if Activity.search_count(
                [
                    ("res_model_id", "=", model_id),
                    ("res_id", "=", auth.id),
                    ("user_id", "=", user.id),
                    ("summary", "=", summary[:100]),
                ]
            ):
                continue
            auth.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=auth.valid_to,
                summary=summary[:100],
                note="Renew the authorisation of %s with %s before %s: work on the brand stops "
                "when it lapses (BRU-PCM-08)."
                % (auth.brand_id.name or "the brand", auth.partner_id.name, auth.valid_to),
                user_id=user.id,
            )
            made += 1
        auth.message_post(body="%s: escalated to %d holder(s)." % (summary, len(users)))
        return {"model": auth._name, "id": auth.id, "activities": made}


class FixPartnerDeal(models.Model):
    """BRU-PCM-09: Submitted -> conflict check -> (Review) -> Protected ->
    Won / Lost / Expired. One end customer is protected for one partner at a
    time; a clash is raised as a channel conflict for a Tier 3 ruling."""

    _name = "fix.partner.deal"
    _description = "Partner Deal Registration"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "registered_on desc, id desc"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    customer_id = fields.Many2one("res.partner", string="End Customer")
    value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    registered_on = fields.Date(required=True)
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("conflict", "In Conflict Review"),
            ("approved", "Approved (Protected)"),
            ("won", "Won"),
            ("lost", "Lost"),
            ("expired", "Expired"),
            ("declined", "Declined"),
        ],
        required=True,
        default="registered",
        tracking=True,
    )
    note = fields.Char()
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    protected_until = fields.Date(readonly=True, copy=False)
    conflict_id = fields.Many2one("fix.partner.conflict", readonly=True, copy=False)
    decline_reason = fields.Char(readonly=True, copy=False)
    expiry_warned = fields.Boolean(readonly=True, copy=False)
    # A04 ERP audit M40-F23: the M07 opportunity a won deal hands to 1000FiX
    # sales, carrying the partner attribution.
    opportunity_id = fields.Many2one(
        "crm.lead", string="M07 Opportunity (hand-off)", readonly=True, copy=False, index=True
    )

    _FROZEN = frozenset({"partner_id", "customer_id", "currency_id", "registered_on"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "approved_at",
            "protected_until",
            "conflict_id",
            "decline_reason",
            "expiry_warned",
            "opportunity_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "registered":
            locked |= self._FROZEN
        if rec and rec.state in ("won", "lost", "expired", "declined"):
            locked |= {"value"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "registered"):
                frozen = rec._fix_form_locked_fields() - rec._fix_guarded_fields()
                _refuse_frozen(rec, vals, frozen, "the deal is %s" % rec.state)
        return super().write(vals)

    def _fix_rivals(self):
        """Other partners' deals that hold the same end customer (its whole
        commercial entity).

        A04 ERP audit M40-F23: only another partner's PROTECTED deal was
        checked, so two partners could both register, and the first approved
        won by speed. A rival is now another partner's protected deal (not
        lapsed), or its open registration (registered / in conflict review)
        made BEFORE this one - first registered, first heard."""
        self.ensure_one()
        if not self.customer_id:
            return self.browse()
        today = fields.Date.context_today(self)
        commercial = self.customer_id.commercial_partner_id
        mine = (self.registered_on or today, self.id or 0)

        def holds(deal):
            if deal.state == "approved":
                return not deal.protected_until or deal.protected_until >= today
            return (deal.registered_on or today, deal.id) < mine

        return (
            self.sudo()
            .search(
                [
                    ("id", "!=", self.id),
                    ("state", "in", ("registered", "conflict", "approved")),
                    ("partner_id", "!=", self.partner_id.id),
                    ("customer_id", "child_of", commercial.id),
                ]
            )
            .filtered(holds)
        )

    def _fix_rival_leads(self):
        """A04 ERP audit M40-F23: other partners' OPEN leads (submitted or
        qualified, inside their attribution window) on the same customer."""
        self.ensure_one()
        if not self.customer_id:
            return self.env["fix.partner.lead"]
        today = fields.Date.context_today(self)
        return (
            self.env["fix.partner.lead"]
            .sudo()
            .search(
                [
                    ("partner_id", "!=", self.partner_id.id),
                    ("state", "in", ("submitted", "qualified")),
                    ("customer_id", "child_of", self.customer_id.commercial_partner_id.id),
                    ("company_id", "=", self.company_id.id),
                ]
            )
            .filtered(
                lambda lead: not lead.attribution_expires_on or lead.attribution_expires_on >= today
            )
        )

    def _fix_rival_opportunities(self):
        """A04 ERP audit M40-F23: the customer's OPEN M07 opportunities (not
        won, not archived) that are not this partner's own hand-off. One with
        no partner attribution is 1000FiX's direct sale."""
        self.ensure_one()
        if not self.customer_id:
            return self.env["crm.lead"]
        opps = (
            self.env["crm.lead"]
            .sudo()
            .search(
                [
                    ("type", "=", "opportunity"),
                    ("active", "=", True),
                    ("probability", "<", 100),
                    ("partner_id", "child_of", self.customer_id.commercial_partner_id.id),
                    ("company_id", "in", (False, self.company_id.id)),
                ]
            )
        )
        return opps.filtered(
            lambda o: not (o.stage_id and o.stage_id.is_won) and o.fix_partner_id != self.partner_id
        )

    def _fix_clash(self):
        """(partner A, partner B, description lines) of every clash, or None.
        Partner A is the rival partner; a direct M07 opportunity's clash names
        this deal's partner as A and no partner B (a 'direct' ruling keeps the
        account direct, a 'partner A' ruling gives it to the partner)."""
        self.ensure_one()
        deals = self._fix_rivals()
        leads = self._fix_rival_leads()
        opps = self._fix_rival_opportunities() or []
        lines = ["Protected / earlier deal %s of %s" % (d.name, d.partner_id.name) for d in deals]
        lines += ["Open lead %s of %s" % (lead.name, lead.partner_id.name) for lead in leads]
        lines += [
            "M07 opportunity %s (%s)"
            % (o.name, o.fix_partner_id.name if o.fix_partner_id else "direct sale")
            for o in opps
        ]
        if not lines:
            return None
        rival = (
            deals[:1].partner_id
            or leads[:1].partner_id
            or next((o.fix_partner_id for o in opps if o.fix_partner_id), None)
        )
        if rival and rival != self.partner_id:
            return rival, self.partner_id, lines
        return self.partner_id, self.env["fix.partner"], lines

    def _fix_ruling_for(self, conflict):
        """'win', 'lose' or 'split' for this deal's partner under a ruling."""
        decision = conflict.dofa_decision
        if decision == "split":
            return "split"
        winner = {"partner_a": conflict.partner_a_id, "partner_b": conflict.partner_b_id}.get(
            decision
        )
        return "win" if winner == self.partner_id else "lose"

    def action_approve(self):
        """Approve and protect the registration: a channel manager who did not
        register it, for an onboarded partner, after the conflict check. A
        clash with another partner's protected deal raises a channel conflict
        and the deal waits for its Tier 3 ruling."""
        fix_require(self.env, [GROUP_MANAGER], "Approving a deal registration")
        today = fields.Date.context_today(self)
        result = {}
        for rec in self:
            if rec.state not in ("registered", "conflict"):
                raise UserError("Only a registered deal can be approved.")
            fix_not_creator(self.env, rec, "approving it")
            if rec.partner_id.state not in EARNING_STATES:
                raise ValidationError(
                    "Partner %s is %s: only an onboarded partner registers deals "
                    "(BRU-PCM-01)." % (rec.partner_id.name, rec.partner_id.state)
                )
            if not rec.customer_id:
                raise ValidationError("A deal registration names its end customer.")
            rivals = rec._fix_rivals()
            if rec.state == "conflict":
                conflict = rec.conflict_id.sudo()
                if conflict.state not in ("mediated", "closed") or not conflict.arbitrated_at:
                    raise UserError(
                        "Deal %s waits for the Tier 3 ruling on conflict %s."
                        % (rec.name, conflict.name)
                    )
                ruling = rec._fix_ruling_for(conflict)
                if ruling == "lose":
                    raise UserError(
                        "Conflict %s was ruled for the other partner; decline deal %s."
                        % (conflict.name, rec.name)
                    )
                if ruling == "win":
                    rivals._guarded().write(
                        {
                            "state": "declined",
                            "decline_reason": "Lost channel-conflict ruling %s" % conflict.name,
                        }
                    )
            else:
                # A04 ERP audit M40-F23: every partner's open or protected
                # deal and open lead, and the customer's open M07
                # opportunities, are checked before the deal is protected.
                clash = rec._fix_clash()
                if clash:
                    partner_a, partner_b, lines = clash
                    conflict = (
                        self.env["fix.partner.conflict"]
                        .sudo()
                        .create(
                            {
                                "name": "Deal clash: %s" % rec.customer_id.display_name,
                                "partner_a_id": partner_a.id,
                                "partner_b_id": partner_b.id or False,
                                "customer_id": rec.customer_id.id,
                                "description": "Deal %s of %s clashes with: %s."
                                % (rec.name, rec.partner_id.name, "; ".join(lines)),
                            }
                        )
                    )
                    rec._guarded().write({"state": "conflict", "conflict_id": conflict.id})
                    result[rec.id] = conflict.name
                    continue
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "protected_until": today + timedelta(days=DEAL_PROTECTION_DAYS),
                }
            )
        if result:
            return {"conflict": result}
        return True

    def action_decline(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Declining a deal registration")
        for rec in self:
            if rec.state not in ("registered", "conflict"):
                raise UserError("Only a registered deal can be declined.")
            rec._guarded().write({"state": "declined", "decline_reason": reason or False})
        return True

    def action_mark_won(self):
        fix_require(self.env, [GROUP_OFFICER], "Recording a won deal")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved (protected) deal can be won.")
            if rec.protected_until and rec.protected_until < today:
                raise UserError("Deal %s lapsed on %s." % (rec.name, rec.protected_until))
            rec._guarded().write({"state": "won"})
            rec._fix_handoff_opportunity()
        return True

    def _fix_handoff_opportunity(self):
        """A04 ERP audit M40-F23: a won deal hands 1000FiX sales an M07
        opportunity on the end customer, carrying the partner attribution
        (fix_partner_id / fix_partner_deal_id, guarded on crm.lead).
        Idempotent: one opportunity per deal."""
        self.ensure_one()
        if self.opportunity_id or "crm.lead" not in self.env:
            return self.opportunity_id
        Opp = self.env["crm.lead"].sudo().with_company(self.company_id)
        opp = Opp.search([("fix_partner_deal_id", "=", self.id)], limit=1) or Opp.create(
            {
                "name": "%s (partner deal %s)" % (self.customer_id.display_name, self.name),
                "type": "opportunity",
                "partner_id": self.customer_id.id,
                "expected_revenue": self.value or 0.0,
                "company_id": self.company_id.id,
                "lead_source": "referral",
                "fix_partner_id": self.partner_id.id,
                "fix_partner_deal_id": self.id,
                "description": "Won by channel partner %s on deal registration %s."
                % (self.partner_id.name, self.name),
            }
        )
        self._guarded().write({"opportunity_id": opp.id})
        self.message_post(body="Handed to M07 sales as opportunity %s." % opp.name)
        return opp

    def action_mark_lost(self):
        fix_require(self.env, [GROUP_OFFICER], "Recording a lost deal")
        for rec in self:
            if rec.state not in ("registered", "approved"):
                raise UserError("Only an open deal can be lost.")
            rec._guarded().write({"state": "lost"})
        return True

    @api.model
    def cron_deal_expiry(self):
        """A04 audit C10 (BRU-PCM-09): a protected deal not won within 90 days
        expires; 30 days before, partner.deal_expiring is published once.
        Idempotent."""
        today = fields.Date.context_today(self)
        approved = self.sudo().search(
            [("state", "=", "approved"), ("protected_until", "!=", False)]
        )
        lapsed = approved.filtered(lambda d: d.protected_until < today)
        if lapsed:
            lapsed._guarded().write({"state": "expired"})
        soon = (approved - lapsed).filtered(
            lambda d: not d.expiry_warned
            and d.protected_until <= today + timedelta(days=EXPIRY_WARNING_DAYS)
        )
        for deal in soon:
            publish(
                deal.env,
                "partner.deal_expiring",
                "fix.partner.deal",
                deal.id,
                {
                    "deal": deal.name,
                    "partner_id": deal.partner_id.id,
                    "customer_id": deal.customer_id.id or None,
                    "protected_until": fields.Date.to_string(deal.protected_until),
                },
            )
        if soon:
            soon._guarded().write({"expiry_warned": True})
        return len(lapsed) + len(soon)


class FixPartnerRebate(models.Model):
    """BRU-PCM-03/11: draft -> accrued (channel officer) -> approved (M63
    inbox: a rebate approver holding the DOFA tier of the amount, not its
    creator, on a current technical audit of at least 85%) -> paid (finance
    records the payout). The amount is pinned once accrued."""

    _name = "fix.partner.rebate"
    _description = "Partner Rebate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "period desc, id desc"

    _approval_domain = "partner_rebate"
    _approval_apply_method = "action_approve_payout"
    _approval_routed = True

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    period = fields.Char(required=True)
    # A04 ERP audit M40-F12: the period the basis is measured over, and the
    # basis itself COMPUTED from the partner's paid M20 invoices at accrual
    # (VAT exclusive, net of credit notes) - never typed.
    period_from = fields.Date(string="Period From")
    period_to = fields.Date(string="Period To")
    basis = fields.Monetary(
        currency_field="currency_id", string="Rebate Basis", readonly=True, copy=False
    )
    basis_invoice_count = fields.Integer(string="Paid Invoices Counted", readonly=True, copy=False)
    rate = fields.Float(required=True, default=0.0, help="Fraction, e.g. 0.03 = 3%.")
    amount = fields.Monetary(currency_field="currency_id", compute="_compute_amount", store=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    # A04 ERP audit M40-F26: ONE MDF mechanism - the fund and its evidenced
    # claims (fix.mdf.fund / fix.mdf.claim). 'mdf' stays a value only so the
    # rows raised before 21 Nov 2026 keep their history; a new or re-kinded
    # one is refused with a pointer (MDF_POINTER).
    kind = fields.Selection(
        [("rebate", "Volume rebate"), ("mdf", "Market development fund (legacy)")],
        required=True,
        default="rebate",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("accrued", "Accrued"),
            ("approved", "Payout Approved"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    # Gated Behind Technical Audit Score >= 85% (FLAW-40.1): the partner's
    # current APPROVED technical audit (fix.partner.audit), shown here.
    technical_audit_score = fields.Float(
        string="Partner Audit Score (%)",
        related="partner_id.technical_audit_score",
        readonly=True,
    )
    audit_id = fields.Many2one(
        "fix.partner.audit", string="Audit Relied On", readonly=True, copy=False
    )
    accrued_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    accrued_at = fields.Datetime(readonly=True, copy=False)
    paid_ref = fields.Char(string="Payout Reference", readonly=True, copy=False)
    paid_at = fields.Datetime(readonly=True, copy=False)
    paid_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    # M40-comarketing (12 Nov 2026): the campaign a market development fund
    # pays for. Optional, MDF only, and the partner must co-fund the campaign
    # (fix.campaign.partner_ids); pinned with the amount once accrued.
    campaign_id = fields.Many2one(
        "fix.campaign",
        string="Co-Marketing Campaign",
        ondelete="restrict",
        index=True,
        domain="[('partner_ids', 'in', [partner_id])]",
    )

    _FROZEN = frozenset(
        {
            "partner_id",
            "period",
            "period_from",
            "period_to",
            "basis",
            "rate",
            "kind",
            "currency_id",
            "campaign_id",
        }
    )

    @api.depends("basis", "rate")
    def _compute_amount(self):
        for rec in self:
            rec.amount = round((rec.basis or 0.0) * (rec.rate or 0.0), 2)

    @api.constrains("rate", "basis")
    def _check_bounds(self):
        for rec in self:
            if not 0.0 <= (rec.rate or 0.0) <= REBATE_MAX_RATE:
                raise ValidationError(
                    "A rebate rate is between 0 and %d%% (got %.1f%%)."
                    % (REBATE_MAX_RATE * 100, (rec.rate or 0.0) * 100)
                )
            if (rec.basis or 0.0) < 0:
                raise ValidationError("A rebate basis cannot be negative.")

    @api.constrains("campaign_id", "kind", "partner_id")
    def _check_campaign(self):
        for rec in self.filtered("campaign_id"):
            if rec.kind != "mdf":
                raise ValidationError(
                    "Only a market development fund names a campaign; %s is a volume rebate."
                    % rec.name
                )
            if rec.partner_id not in rec.campaign_id.sudo().partner_ids:
                raise ValidationError(
                    "%s is not a co-marketing partner of campaign %s: name the partner on the "
                    "campaign first." % (rec.partner_id.name, rec.campaign_id.name)
                )

    # ------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "amount",
            "basis",
            "basis_invoice_count",
            "audit_id",
            "accrued_by_id",
            "accrued_at",
            "paid_ref",
            "paid_at",
            "paid_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        rec = self[:1]
        if rec and rec.state != "draft":
            locked |= self._FROZEN | {"name"}
        if rec and rec.state not in ("draft", "accrued"):
            locked |= {"dofa_justification"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        # A04 ERP audit M40-F26: no new MDF rebate, whoever asks (seeds too)
        if any(vals.get("kind") == "mdf" for vals in vals_list):
            raise ValidationError(MDF_POINTER)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("kind") == "mdf" and any(rec.kind != "mdf" for rec in self):
            raise ValidationError(MDF_POINTER)
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                _refuse_frozen(
                    rec, vals, self._FROZEN, "the rebate is %s and its amount is pinned" % rec.state
                )
        return super().write(vals)

    @api.model
    def _fix_migrate_mdf_rebates(self):
        """A04 ERP audit M40-F26 data step (post-migrate 19.0.0.3.2, and safe
        to re-run). An MDF raised as a rebate that has not been approved is
        cancelled, with its pending approval voided and a note pointing at
        the MDF fund / claim registers - no money had moved on it. An
        approved one is left to finish on the payout path it is already on
        (its M50 instruction), and a paid one is history. Returns the ids
        cancelled. fix_real holds 0 such rows (20 Nov 2026)."""
        legacy = self.sudo().search([("kind", "=", "mdf"), ("state", "in", ("draft", "accrued"))])
        for rec in legacy:
            if rec.approval_state == "pending":
                rec._approval_void("MDF moved to the MDF fund / claim registers (M40-F26)")
            rec._guarded().write({"state": "cancelled"})
            rec.message_post(
                body="Cancelled by the M40-F26 migration: market development funds are allocated "
                "on an MDF Fund and paid on evidenced MDF Claims. Re-raise this one there."
            )
        return legacy.ids

    # ------------------------------------------------------------ DOFA
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return self.amount or 0.0

    def _dofa_thresholds(self):
        return REBATE_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "%s %s payout of BDT %.2f" % (
            dict(self._fields["kind"].selection).get(self.kind, "rebate"),
            self.name,
            self.amount or 0.0,
        )

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return self.state == "accrued" and super()._approval_needed()

    def _approval_holders(self, group):
        users = super()._approval_holders(group)
        approvers = self.env.ref(GROUP_REBATE_APPROVER, raise_if_not_found=False)
        return users & approvers.sudo().all_user_ids if approvers else users.browse()

    def _dofa_void_approval(self, reason: str):
        approved = self.filtered(lambda r: r.state == "approved")
        result = super()._dofa_void_approval(reason)
        approved._guarded().write({"state": "accrued", "audit_id": False})
        return result

    # ------------------------------------------------------------ basis
    def _fix_paid_basis(self):
        """A04 ERP audit M40-F12: the partner's PAID M20 invoices dated in the
        period, VAT exclusive, less the VAT-exclusive part of the credit notes
        issued against them. Returns (basis, invoice count)."""
        self.ensure_one()
        if not (self.period_from and self.period_to) or self.period_to < self.period_from:
            raise ValidationError(
                "Give rebate %s its period (from / to dates): the basis is measured from the "
                "partner's paid invoices of that period." % self.name
            )
        party = self.partner_id.sudo().partner_id.commercial_partner_id
        invoices = (
            self.env["fix.ar.invoice"]
            .sudo()
            .search(
                [
                    ("customer_id", "child_of", party.id),
                    ("company_id", "=", self.partner_id.company_id.id),
                    ("state", "in", REBATE_BASIS_STATES),
                    ("invoice_date", ">=", self.period_from),
                    ("invoice_date", "<=", self.period_to),
                ]
            )
        )
        gross = sum(invoices.mapped("taxable_amount"))
        credited = 0.0
        for note in invoices.mapped("credit_note_ids").filtered(lambda n: n.state == "issued"):
            total = note.invoice_id.total_payable or 0.0
            if total > 0.005:
                credited += (note.amount or 0.0) * note.invoice_id.taxable_amount / total
        return round(max(gross - credited, 0.0), 2), len(invoices)

    # ------------------------------------------------------------ lifecycle
    def action_accrue(self):
        fix_require(self.env, [GROUP_OFFICER], "Accruing a rebate")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft rebate can be accrued.")
            if rec.partner_id.state not in EARNING_STATES:
                raise ValidationError(
                    "Partner %s is %s: only an onboarded partner earns a rebate (BRU-PCM-01)."
                    % (rec.partner_id.name, rec.partner_id.state)
                )
            basis, count = rec._fix_paid_basis()
            if basis <= 0 or (rec.rate or 0.0) <= 0:
                raise ValidationError(
                    "A rebate accrues on a positive basis and rate: %s has %d paid invoice(s) "
                    "worth BDT %.2f in %s to %s."
                    % (rec.name, count, basis, rec.period_from, rec.period_to)
                )
            rec._guarded().write(
                {
                    "basis": basis,
                    "basis_invoice_count": count,
                    "state": "accrued",
                    "accrued_by_id": self.env.uid,
                    "accrued_at": fields.Datetime.now(),
                }
            )
        return True

    def action_approve_payout(self):
        """Approve the payout, from the approver's M63 inbox only.

        A04 audit M40-1/2/3: the payout went from any state straight to paid
        with no role, the 85% audit gate had a caller-controlled bypass
        (skip_audit_score_check, removed) and read a self-typed score. The
        gate now reads the partner's current approved technical audit."""
        self._approval_assert_routed()
        fix_require(self.env, [GROUP_REBATE_APPROVER], "Approving a rebate payout")
        for rec in self:
            if rec.state != "accrued":
                raise UserError("Only an accrued rebate can be approved for payout.")
            if rec.partner_id.state not in EARNING_STATES:
                raise ValidationError("Partner %s is no longer onboarded." % rec.partner_id.name)
            audit = rec.partner_id._fix_current_audit()
            score = audit.score if audit else 0.0
            if score < AUDIT_PASS_SCORE:
                raise ValidationError(
                    "Rebate payout approval blocked: Partner '%s' technical audit score is %.1f%% "
                    "(minimum %.1f%% technical compliance required under Channel Governance Rules / "
                    "FLAW-40.1, from an approved audit of the last %d days)."
                    % (rec.partner_id.name, score, AUDIT_PASS_SCORE, AUDIT_VALIDITY_DAYS)
                )
            # A04 ERP audit M40-F13: no payout is approved that the ledger
            # cannot accrue (expense, partner payable and TDS accounts).
            assert_payout_accounts(
                self.env,
                rec.partner_id.company_id,
                "partner_mdf_expense" if rec.kind == "mdf" else "partner_rebate_payout",
            )
            rec.action_dofa_approve()
            rec._guarded().write({"state": "approved", "audit_id": audit.id})
            publish(
                rec.env,
                "partner.rebate_approved",
                "fix.partner.rebate",
                rec.id,
                {
                    "rebate_id": rec.id,
                    "rebate": rec.name,
                    "partner_id": rec.partner_id.id,
                    "party_id": rec.partner_id.partner_id.id,
                    "kind": rec.kind,
                    "period": rec.period,
                    "amount": float(rec.amount or 0.0),
                    "currency": rec.currency_id.name,
                    "approved_by": rec.env.user.id,
                },
            )
        return True

    def action_record_payout(self, payment_ref=None):
        """Finance records that the approved amount was paid.

        A04 ERP audit M40-F13: a typed reference stood for the payment. The
        rebate is now paid when the M50 instruction raised by its approval
        hand-off is executed (bank confirmed); the reference is that
        instruction's bank reference."""
        finance = self.env.ref(GROUP_FINANCE, raise_if_not_found=False)
        if not (self.env.su or (finance and self.env.user in finance.sudo().all_user_ids)):
            raise UserError("Recording a rebate payout is finance's (Invoicing / Billing role).")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved rebate is paid.")
            rec._dofa_assert_approved("The rebate payout")
            pay = executed_payout(rec, "Rebate %s" % rec.name)
            ref = pay.bank_reference or pay.name
            # sudo after the finance check: finance records the payout without
            # holding the channel roles' write access.
            rec.sudo()._guarded().write(
                {
                    "state": "paid",
                    "paid_ref": ref,
                    "paid_at": fields.Datetime.now(),
                    "paid_by_id": self.env.uid,
                }
            )
        return True

    def action_cancel(self):
        fix_require(self.env, [GROUP_OFFICER], "Cancelling a rebate")
        for rec in self:
            if rec.state not in ("draft", "accrued"):
                raise UserError("Only a draft or accrued rebate can be cancelled.")
            if rec.approval_state == "pending":
                rec._approval_void("the rebate was cancelled by %s" % self.env.user.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixPartnerFranchise(models.Model):
    _name = "fix.partner.franchise"
    _description = "Franchise Agreement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "start_date, id"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    territory = fields.Char(required=True)
    fee = fields.Monetary(currency_field="currency_id")
    # A04 ERP audit M40-F2: the M20 invoice of the initial fee.
    fee_invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Initial Fee Invoice (M20)", readonly=True, copy=False
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("terminated", "Terminated")],
        required=True,
        default="draft",
        tracking=True,
    )
    activated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    activated_at = fields.Datetime(readonly=True, copy=False)
    terminated_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    terminated_at = fields.Datetime(readonly=True, copy=False)
    termination_reason = fields.Char(readonly=True, copy=False)

    _FROZEN = frozenset({"partner_id", "territory", "fee", "currency_id", "start_date", "end_date"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_by_id",
            "activated_at",
            "terminated_by_id",
            "terminated_at",
            "termination_reason",
            "fee_invoice_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "draft":
            locked |= self._FROZEN
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                _refuse_frozen(rec, vals, self._FROZEN, "the agreement is %s" % rec.state)
        return super().write(vals)

    def _fix_bill_initial_fee(self):
        """A04 ERP audit M40-F2: the initial fee is billed at activation - a
        draft M20 invoice to the franchisee (VAT by M51), crediting the
        configured franchise-fee income account. partner.franchise_activated
        had no consumer: a BDT 750,000 fee produced no invoice."""
        from .fix_partner_capture import partner_account

        self.ensure_one()
        if (self.fee or 0.0) <= 0.005:
            return self.env["fix.ar.invoice"]
        company = self.partner_id.sudo().company_id
        account = partner_account(self.env, company, "franchise_fee_income")
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            ._fix_draft_invoice_from_source(
                self._name,
                "%s/%s/initial-fee" % (self._name, self.id),
                self.partner_id.sudo().partner_id,
                [
                    {
                        "description": "Franchise initial fee - %s (%s)"
                        % (self.name, self.territory),
                        "taxable_amount": self.fee,
                    }
                ],
                "Franchise agreement %s activated: initial fee (FR-PCM-036)" % self.name,
                company=company,
                invoice_date=fields.Date.context_today(self),
                credit_account=account,
            )
        )
        self._guarded().write({"fee_invoice_id": invoice.id})
        return invoice

    @api.constrains("start_date", "end_date", "fee")
    def _check_terms(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    "Franchise %s ends (%s) before it starts (%s)."
                    % (rec.name, rec.end_date, rec.start_date)
                )
            if (rec.fee or 0.0) < 0:
                raise ValidationError("A franchise fee cannot be negative.")

    def action_activate(self):
        """A channel manager who did not draft the agreement activates it, for
        an onboarded franchise partner whose documents a KYC officer verified.
        The fee goes to M20 for invoicing (partner.franchise_activated)."""
        fix_require(self.env, [GROUP_MANAGER], "Activating a franchise agreement")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft agreement can be activated.")
            fix_not_creator(self.env, rec, "activating it")
            partner = rec.partner_id
            if partner.state != "onboarded":
                raise ValidationError(
                    "Franchise partner must be in 'onboarded' status before activating the franchise agreement."
                )
            if (
                not partner.has_trade_license_doc
                or not partner.has_bank_solvency_doc
                or not partner.kyc_verified
            ):
                raise ValidationError(
                    "Franchise agreement activation requires verified Trade License and Bank Solvency Certificate on the partner record."
                )
            rec._guarded().write(
                {
                    "state": "active",
                    "activated_by_id": self.env.uid,
                    "activated_at": fields.Datetime.now(),
                }
            )
            rec._fix_bill_initial_fee()
            publish(
                rec.env,
                "partner.franchise_activated",
                "fix.partner.franchise",
                rec.id,
                {
                    "franchise_id": rec.id,
                    "franchise": rec.name,
                    "partner_id": partner.id,
                    "party_id": partner.partner_id.id,
                    "territory": rec.territory,
                    "fee": float(rec.fee or 0.0),
                    "currency": rec.currency_id.name,
                    "start_date": fields.Date.to_string(rec.start_date),
                    "end_date": fields.Date.to_string(rec.end_date) if rec.end_date else None,
                },
            )
        return True

    def action_terminate(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Terminating a franchise agreement")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("State why the franchise agreement is terminated.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only an active agreement can be terminated.")
            rec._guarded().write(
                {
                    "state": "terminated",
                    "terminated_by_id": self.env.uid,
                    "terminated_at": fields.Datetime.now(),
                    "termination_reason": reason,
                }
            )
        return True


class FixPartnerConflict(models.Model):
    _name = "fix.partner.conflict"
    _description = "Channel Conflict"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True)
    partner_a_id = fields.Many2one("fix.partner", string="Partner A", required=True)
    company_id = fields.Many2one(related="partner_a_id.company_id", store=True, index=True)
    partner_b_id = fields.Many2one("fix.partner", string="Partner B")
    customer_id = fields.Many2one("res.partner", string="Contested Customer")
    description = fields.Text(required=True)
    state = fields.Selection(
        [("open", "Open"), ("mediated", "Mediated"), ("closed", "Closed")],
        required=True,
        default="open",
        tracking=True,
    )
    resolution = fields.Char()
    # DOFA Arbitration & Commercial Conflict Governance (FLAW-40.2)
    dofa_arbitrator_id = fields.Many2one("res.users", string="DOFA Arbitrator", readonly=True)
    dofa_decision = fields.Selection(
        [
            ("partner_a", "Awarded to Partner A"),
            ("partner_b", "Awarded to Partner B"),
            ("split", "Split Commission / Revenue"),
            ("direct", "Retained as Direct Corporate Account"),
        ],
        string="DOFA Ruling",
    )
    arbitration_notes = fields.Text(string="Arbitration Rationale")
    arbitrated_at = fields.Datetime(string="Ruling Issued", readonly=True, copy=False)

    _FROZEN = frozenset({"partner_a_id", "partner_b_id", "customer_id", "description"})

    def _fix_guarded_fields(self) -> set:
        # A04 audit M40-6: the ruling, its arbitrator and its time are written
        # only by action_mediate; written by hand they forged a ruling the
        # arbitrator never gave, and changed it after he had.
        return super()._fix_guarded_fields() | {
            "state",
            "dofa_arbitrator_id",
            "dofa_decision",
            "arbitration_notes",
            "arbitrated_at",
            "resolution",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self[:1] and self[:1].state != "open":
            locked |= self._FROZEN
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "open"):
                _refuse_frozen(rec, vals, self._FROZEN, "the conflict was ruled on")
        return super().write(vals)

    def action_mediate(self, dofa_decision, dofa_arbitrator_id=None, notes=None):
        """Rule on a contested customer, and record who ruled (DISC-40.2).

        The ruling moves revenue between two partners, so it carries the same
        authority the rest of the estate uses. Before the A04 audit of
        2026-11-01 it carried none: any user could call it, the caller chose
        which user to record as the arbitrator, and no rationale was required
        — so `dofa_arbitrator_id` recorded whoever the caller nominated rather
        than whoever decided. A ruling is given once (A04 audit M40-6).
        """
        valid = dict(self._fields["dofa_decision"].selection)
        for rec in self:
            if rec.state != "open":
                raise UserError("Conflict %s is already %s." % (rec.name, rec.state))
            if dofa_decision not in valid:
                raise UserError(
                    "Unknown ruling %r. Valid rulings: %s"
                    % (dofa_decision, ", ".join(sorted(valid)))
                )
            if not (notes or "").strip():
                raise UserError(
                    "Record the arbitration rationale: a ruling that moves "
                    "revenue between partners has to say why."
                )
            if not self.env.user.has_group("cd_entity_config.group_dofa_tier_3"):
                raise UserError(
                    "Channel-conflict arbitration requires DOFA Tier 3 "
                    "(Commercial Director) authority."
                )
            # fix.partner carries no account-manager field, so the available
            # signal is who raised the conflict. Same rule as fix.dofa.mixin:
            # the person who brought it cannot also rule on it.
            if rec.create_uid and rec.create_uid.id == self.env.user.id:
                raise UserError(
                    "Segregation of duties: %s raised this conflict and cannot "
                    "arbitrate it." % self.env.user.name
                )
            if dofa_arbitrator_id and dofa_arbitrator_id != self.env.user.id:
                raise UserError(
                    "The arbitrator is whoever issues the ruling. It cannot be "
                    "attributed to another user."
                )
            # sudo after the checks: the Tier 3 arbitrator need not hold the
            # channel officer's write access to record the ruling.
            rec.sudo()._guarded().write(
                {
                    "state": "mediated",
                    "dofa_decision": dofa_decision,
                    "dofa_arbitrator_id": self.env.user.id,
                    "arbitration_notes": notes,
                    "arbitrated_at": fields.Datetime.now(),
                    "resolution": valid[dofa_decision],
                }
            )
        return True

    # One button per ruling for the workspace, which prompts for one value
    # (the rationale); each is action_mediate with its decision.
    def action_rule_partner_a(self, notes=None):
        return self.action_mediate("partner_a", notes=notes)

    def action_rule_partner_b(self, notes=None):
        return self.action_mediate("partner_b", notes=notes)

    def action_rule_split(self, notes=None):
        return self.action_mediate("split", notes=notes)

    def action_rule_direct(self, notes=None):
        return self.action_mediate("direct", notes=notes)

    def action_close(self):
        # A04 zero-trust audit 2026-10-31: closing requires a mediated DOFA
        # ruling — an open conflict must never be closed without adjudication.
        # A04 workflow audit M40-6: the ruling must be the one action_mediate
        # recorded (the fields are guarded, so it can be no other).
        fix_require(self.env, [GROUP_OFFICER, GROUP_TIER3], "Closing a channel conflict")
        for rec in self:
            if rec.state == "open":
                raise UserError(
                    "Conflict %s is still OPEN — record the DOFA mediation "
                    "decision (action_mediate) before closing" % rec.name
                )
            if rec.state != "mediated" or not (
                rec.arbitrated_at and rec.dofa_arbitrator_id and rec.dofa_decision
            ):
                raise UserError("Conflict %s carries no recorded ruling to close on." % rec.name)
            rec.sudo()._guarded().write({"state": "closed"})
        return True

    _distinct_parties = models.Constraint(
        "CHECK (partner_b_id IS NULL OR partner_b_id <> partner_a_id)",
        "A channel conflict must name two different partners",
    )
