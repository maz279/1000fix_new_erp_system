# A04 ERP audit (20 Nov 2026), stream B5 - M40 partner standing, rate
# governance and the brand link.
#
#   M40-F5   one channel manager set a 100% commission rate alone: a rate is
#            now proposed (fix.partner.rate.change) and takes effect only when
#            a DOFA Tier 3 approver other than the proposer approves it from
#            the M63 inbox;
#   M40-F9   a suspended partner's portal user kept submitting: suspension,
#            exit and dormancy revoke the P12 portal role (BRU-PCM-13), and
#            reinstatement restores exactly the users it removed;
#   M40-F24  the spec's standings (FR-PCM-010): probation, dormant (daily job
#            on the owner's dormancy window; no window = no job), exiting and
#            exited (BRU-PCM-15: never with commission, rebate or MDF unpaid);
#   M40-F20  a brand partner names its M37 brand; when the brand master names
#            its OEM party (fix.brand.partner_id), the two must agree;
#   M40-F27  the child registers carry their partner's company.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_partner import (
    GROUP_MANAGER,
    GROUP_TIER3,
    fix_not_creator,
    fix_require,
)

GROUP_PORTAL = "cd_partner.group_fix_partner_portal"
PARAM_DORMANCY_DAYS = "cd_partner.dormancy_days"
# a rate change is decided by DOFA Tier 3 (CCO / Commercial Director) - an
# OWNER default until the M30 ladder rules otherwise
RATE_CHANGE_THRESHOLDS = [(float("inf"), "tier_3")]


class FixApprovalMatrixRateChange(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("partner_commission_rate", "Partner Commission Rate Change")],
        ondelete={"partner_commission_rate": "cascade"},
    )


class FixPartnerRateChange(models.Model):
    """A04 ERP audit M40-F5: a proposed commission rate, applied only by its
    routed DOFA approval."""

    _name = "fix.partner.rate.change"
    _description = "Partner Commission Rate Change"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "id desc"

    _approval_domain = "partner_commission_rate"
    _approval_apply_method = "action_apply"
    _approval_routed = True

    partner_id = fields.Many2one("fix.partner", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
    current_rate = fields.Float(string="Rate Before", readonly=True, copy=False)
    proposed_rate = fields.Float(string="Proposed Rate", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("applied", "Applied"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
        tracking=True,
    )
    applied_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    applied_at = fields.Datetime(readonly=True, copy=False)

    _FROZEN = frozenset({"partner_id", "proposed_rate"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "current_rate",
            "applied_by_id",
            "applied_at",
        }

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if (
                    rec.state != "draft" or rec.approval_state in ("pending", "approved")
                ) and self._FROZEN & set(vals):
                    raise UserError(
                        "Rate change %s is %s: propose a new one instead."
                        % (rec.display_name, rec.approval_state or rec.state)
                    )
        return super().write(vals)

    @api.constrains("proposed_rate")
    def _check_rate(self):
        for rec in self:
            if not 0 < rec.proposed_rate <= 1:
                raise ValidationError("A commission rate is above 0 and at most 1 (100%).")

    @api.model_create_multi
    def create(self, vals_list):
        fix_require(self.env, [GROUP_MANAGER], "Proposing a commission rate")
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"current_rate": rec.partner_id.sudo().commission_rate})
        return recs

    @api.depends("partner_id.name", "proposed_rate")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s: %.2f%%" % (rec.partner_id.name or "?", rec.proposed_rate * 100)

    # ---- DOFA: a rate is not money; every change is a Tier 3 decision
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return (self.proposed_rate or 0.0) * 100.0

    def _dofa_thresholds(self):
        return RATE_CHANGE_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "commission rate %.2f%%" % ((self.proposed_rate or 0.0) * 100.0)

    @api.depends("proposed_rate")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        return self.state == "draft" and super()._approval_needed()

    def action_apply(self):
        """From the approver's M63 inbox only: the rate takes effect."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Rate change %s is %s." % (rec.display_name, rec.state))
            fix_not_creator(self.env, rec, "approving it")
            rec.action_dofa_approve()
            partner = rec.partner_id.sudo()
            old = partner.commission_rate
            partner._guarded().write({"commission_rate": rec.proposed_rate})
            partner.message_post(
                body="Commission rate %.4f -> %.4f: proposed by %s, approved by %s (%s)."
                % (
                    old,
                    rec.proposed_rate,
                    rec.create_uid.name,
                    self.env.user.name,
                    rec.display_name,
                )
            )
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by_id": self.env.uid,
                    "applied_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a proposed rate change is cancelled.")
            if rec.approval_state == "pending":
                rec._approval_void("cancelled by %s" % self.env.user.name)
            rec._guarded().write({"state": "cancelled"})
        return True


class FixPartnerStanding(models.Model):
    _inherit = "fix.partner"

    brand_id = fields.Many2one(
        "fix.brand",
        string="Brand (M37)",
        index=True,
        help="A brand partner's M37 brand. The OEM party M09 bills is the brand master's.",
    )
    portal_revoked_user_ids = fields.Many2many(
        "res.users",
        "fix_partner_portal_revoked_rel",
        "partner_id",
        "user_id",
        string="Portal Users Revoked",
        readonly=True,
        copy=False,
    )
    standing_reason = fields.Char(string="Standing Reason", readonly=True, copy=False)
    standing_changed_at = fields.Datetime(readonly=True, copy=False)
    exited_on = fields.Date(readonly=True, copy=False)

    _brand_unique = models.Constraint(
        "UNIQUE (brand_id)", "One brand is represented by one brand partner."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "portal_revoked_user_ids",
            "standing_reason",
            "standing_changed_at",
            "exited_on",
        }

    @api.constrains("brand_id", "partner_type", "partner_id")
    def _check_brand(self):
        for rec in self.filtered("brand_id"):
            if rec.partner_type != "brand":
                raise ValidationError("Only a brand partner names a brand (%s)." % rec.name)
            brand = rec.brand_id.sudo()
            oem = brand.partner_id if "partner_id" in brand._fields else False
            if oem and oem.commercial_partner_id != rec.partner_id.commercial_partner_id:
                raise ValidationError(
                    "Brand %s bills %s (M37 brand master), not %s: the brand partner is the "
                    "brand's own OEM party."
                    % (brand.name, oem.display_name, rec.partner_id.display_name)
                )

    # ---- portal (BRU-PCM-13) -----------------------------------------
    def _fix_portal_users(self):
        self.ensure_one()
        group = self.env.ref(GROUP_PORTAL)
        commercial = self.sudo().partner_id.commercial_partner_id
        return (
            self.env["res.users"]
            .sudo()
            .search([("partner_id", "child_of", commercial.id), ("share", "=", True)])
            .filtered(lambda u: group in u.group_ids)
        )

    def _fix_revoke_portal(self, why):
        group = self.env.ref(GROUP_PORTAL).sudo()
        for rec in self:
            users = rec._fix_portal_users()
            if users:
                group.write({"user_ids": [(3, u.id) for u in users]})
            rec._guarded().sudo().write({"portal_revoked_user_ids": [(4, u.id) for u in users]})
            rec.sudo().message_post(
                body="P12 portal access revoked (%s): %s."
                % (why, ", ".join(users.mapped("login")) or "no portal user")
            )

    def _fix_restore_portal(self):
        group = self.env.ref(GROUP_PORTAL).sudo()
        for rec in self:
            users = rec.sudo().portal_revoked_user_ids.filtered("active")
            if users:
                group.write({"user_ids": [(4, u.id) for u in users]})
            rec._guarded().sudo().write({"portal_revoked_user_ids": [(5, 0, 0)]})

    def _fix_standing(self, state, reason):
        # sudo after each caller's role check: a CCO (Tier 3) decides an exit
        # without holding the channel officer's write access
        self.sudo()._guarded().write(
            {
                "state": state,
                "standing_reason": reason or False,
                "standing_changed_at": fields.Datetime.now(),
            }
        )

    def action_suspend(self, reason=None):
        result = super().action_suspend(reason=reason)
        self._fix_revoke_portal("suspended")
        return result

    def action_reinstate(self, reason=None):
        result = super().action_reinstate(reason=reason)
        self._fix_restore_portal()
        return result

    # ---- probation ---------------------------------------------------
    def action_probation(self, reason=None):
        """FR-PCM-010: performance or compliance below threshold, with a
        remediation plan. The partner keeps earning."""
        fix_require(self.env, [GROUP_MANAGER], "Putting a partner on probation")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("State the remediation plan the probation runs on.")
        for rec in self:
            if rec.state != "onboarded":
                raise UserError("Only an active (onboarded) partner is put on probation.")
            rec._fix_standing("probation", reason)
            rec.message_post(body="On probation: %s" % reason)
        return True

    def action_end_probation(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Ending a partner's probation")
        for rec in self:
            if rec.state != "probation":
                raise UserError("Only a partner on probation is returned to active.")
            rec._fix_standing("onboarded", reason)
        return True

    # ---- dormancy ----------------------------------------------------
    def _fix_last_activity(self):
        """The last qualifying activity: a referral, lead, deal or draw."""
        self.ensure_one()
        stamps = [self.onboarded_at or self.create_date]
        for model, field in (
            ("fix.referral", "partner_id"),
            ("fix.partner.lead", "partner_id"),
            ("fix.partner.deal", "partner_id"),
            ("fix.reseller.draw", "partner_id"),
        ):
            last = (
                self.env[model]
                .sudo()
                .search([(field, "=", self.id)], order="create_date desc", limit=1)
            )
            if last:
                stamps.append(last.create_date)
        return max(s for s in stamps if s)

    @api.model
    def cron_partner_dormancy(self):
        """AUT-PCM-17: an active partner with no qualifying activity in the
        owner's window goes dormant and loses the portal. With no window set
        (cd_partner.dormancy_days) nothing happens - an OWNER figure."""
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_DORMANCY_DAYS)
        try:
            days = int(raw) if raw else 0
        except (TypeError, ValueError):
            days = 0
        if days <= 0:
            return 0
        cutoff = fields.Datetime.now() - timedelta(days=days)
        dormant = self.browse()
        for rec in self.sudo().search([("state", "=", "onboarded")]):
            if rec._fix_last_activity() < cutoff:
                rec._fix_standing("dormant", "No qualifying activity in %d days" % days)
                dormant |= rec
        if dormant:
            dormant._fix_revoke_portal("dormant")
        return len(dormant)

    def action_reactivate(self, reason=None):
        fix_require(self.env, [GROUP_MANAGER], "Reactivating a dormant partner")
        for rec in self:
            if rec.state != "dormant":
                raise UserError("Only a dormant partner is reactivated.")
            rec._fix_standing("onboarded", reason)
            rec._fix_restore_portal()
        return True

    # ---- exit ----------------------------------------------------------
    def action_start_exit(self, reason=None):
        """FR-PCM-010: agreement terminated, not renewed, or a voluntary exit
        (CCO). The portal is revoked at once (BRU-PCM-13)."""
        fix_require(self.env, [GROUP_TIER3], "Starting a partner's exit (CCO)")
        reason = (str(reason).strip() if reason else "") or False
        if not reason:
            raise UserError("State why the partner exits.")
        for rec in self:
            if rec.state in ("exiting", "exited", "prospective", "qualifying"):
                raise UserError("Partner %s is %s." % (rec.name, rec.state))
            rec._fix_standing("exiting", reason)
            rec._fix_revoke_portal("exiting")
        return True

    def _fix_unsettled(self):
        """BRU-PCM-15: what is still owed to (or by) the partner."""
        self.ensure_one()
        open_items = []
        Referral = self.env["fix.referral"].sudo()
        refs = Referral.search([("partner_id", "=", self.id), ("state", "!=", "submitted")])
        for ref in refs:
            if ref.state == "converted":
                open_items.append("referral %s (converted, commission not earned)" % ref.name)
            elif "payout_state" in ref._fields and ref.payout_state not in ("paid", "void"):
                open_items.append(
                    "referral %s (commission %s)" % (ref.name, ref.payout_state or "not accrued")
                )
        for reb in (
            self.env["fix.partner.rebate"]
            .sudo()
            .search([("partner_id", "=", self.id), ("state", "in", ("accrued", "approved"))])
        ):
            open_items.append("rebate %s (%s)" % (reb.name, reb.state))
        for claim in (
            self.env["fix.mdf.claim"]
            .sudo()
            .search([("partner_id", "=", self.id), ("state", "in", ("submitted", "approved"))])
        ):
            open_items.append("MDF claim %s (%s)" % (claim.name, claim.state))
        return open_items

    def action_complete_exit(self):
        fix_require(self.env, [GROUP_TIER3], "Completing a partner's exit (CCO)")
        for rec in self:
            if rec.state != "exiting":
                raise UserError("Only an exiting partner exits.")
            unsettled = rec._fix_unsettled()
            if unsettled:
                raise ValidationError(
                    "%s cannot exit: settle first (BRU-PCM-15): %s."
                    % (rec.name, "; ".join(unsettled))
                )
            rec.sudo()._guarded().write(
                {"state": "exited", "exited_on": fields.Date.context_today(self)}
            )
            rec._fix_revoke_portal("exited")
        return True


class FixPartnerAuthorisationActivities(models.Model):
    _name = "fix.partner.authorisation"
    _inherit = ["fix.partner.authorisation", "mail.activity.mixin"]


class FixPartnerChildCompany(models.Model):
    _inherit = "fix.partner.onboarding"

    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)


class FixPartnerEnablementCompany(models.Model):
    _inherit = "fix.partner.enablement"

    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)


class FixPartnerContactRoleCompany(models.Model):
    _inherit = "fix.partner.contact.role"

    company_id = fields.Many2one(related="partner_id.company_id", store=True, index=True)
