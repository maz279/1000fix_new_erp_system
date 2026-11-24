# cd_billing_engine — the finance approval ladder (A08 S3 / P1-1, B4).
#
# A08 audit (2026-11-04), M20-1/-7, M53-3: a credit note of BDT 25,000 or less
# was approved at submit with no approver recorded, its raiser issued it, and
# above 25,000 only an IT administrator (base.group_system) could approve. A
# payout run of BDT 8.5 million was approved by one finance manager.
#
# fix.finance.dofa.mixin is the one ladder every amount-bearing finance
# approval of B4 uses (credit notes, AR write-offs, payout runs):
#
#   amount <= the direct band   tier_0: a second Accountant (Finance Officer,
#                               account.group_account_user) approves directly;
#   above the band              routed through M63 (fix.dofa.mixin) to the
#                               Accounting Administrator (Finance Manager,
#                               account.group_account_manager) — never
#                               base.group_system;
#   above the CFO band          routed to DOFA Tier 4 (CFO), when configured.
#
# The bands are configuration (system parameters named by each model); the
# M30 DOFA ladder (fix.dofa.ladder, the ONE DoA table) overrides them when
# ruled for the model. At every amount the approver is never the creator, the
# requester, whoever last changed the amount, or anyone the model names
# (preparer, payee-changer): checked when routing AND again when deciding.
# Superuser code (crons, seeds, relay consumers) is trusted, as the guard
# trusts it.
import logging

from odoo import fields, models
from odoo.addons.cd_entity_config.models.fix_dofa import DOFA_TIERS, TIER_GROUP
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)

GROUP_ACCOUNTANT = "account.group_account_user"
GROUP_ADMINISTRATOR = "account.group_account_manager"


def float_param(env, key, default):
    """A numeric system parameter, or the documented default."""
    raw = env["ir.config_parameter"].sudo().get_param(key) if key else None
    if raw in (None, False, ""):
        return float(default or 0.0)
    try:
        return float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number (%r); using %s", key, raw, default)
        return float(default or 0.0)


def holds(user, xmlid) -> bool:
    """The user holds the role. The Accounting Administrator does every
    Accountant duty (Odoo 19's group does not imply group_account_user)."""
    if user.has_group(xmlid):
        return True
    return xmlid == GROUP_ACCOUNTANT and user.has_group(GROUP_ADMINISTRATOR)


def has_role(env, xmlid) -> bool:
    """Superuser code (crons, seeds, service calls) is trusted."""
    return env.su or holds(env.user, xmlid)


def require_role(env, xmlid, what):
    if not has_role(env, xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        raise AccessError(
            "%s needs the %s role, which you do not hold." % (what, group.name if group else xmlid)
        )


class FixFinanceDofaMixin(models.AbstractModel):
    """Routed, amount-tiered finance approval with the M20/M53 defences."""

    _name = "fix.finance.dofa.mixin"
    _inherit = ["fix.dofa.mixin"]
    _description = "Finance Approval (DOFA ladder, routed)"

    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    # Per model: the system parameters of the ladder and their defaults.
    # _fin_direct_param None = no direct band (every amount is routed).
    _fin_direct_param = None
    _fin_direct_default = 0.0
    _fin_cfo_param = None
    _fin_cfo_default = 0.0
    _fin_what = "This approval"

    fin_approved_by_id = fields.Many2one(
        "res.users", string="Approved By (finance)", readonly=True, copy=False
    )
    fin_approved_at = fields.Datetime(string="Approved On (finance)", readonly=True, copy=False)
    fin_approved_amount = fields.Float(
        string="Amount Approved (finance)",
        readonly=True,
        copy=False,
        help="The amount the approver signed off. A later amount above it is not covered.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "fin_approved_by_id",
            "fin_approved_at",
            "fin_approved_amount",
        }

    # ---- the ladder ---------------------------------------------------------
    def _fin_direct_limit(self):
        if not self._fin_direct_param:
            return None
        return float_param(self.env, self._fin_direct_param, self._fin_direct_default)

    def _dofa_thresholds(self):
        direct = self._fin_direct_limit()
        cfo = float_param(self.env, self._fin_cfo_param, self._fin_cfo_default)
        ladder = []
        if direct is not None:
            ladder.append((direct, "tier_0"))
        floor = direct if direct is not None else 0.0
        if cfo and cfo > floor:
            ladder.append((cfo, "tier_2"))
            ladder.append((float("inf"), "tier_4"))
        else:
            ladder.append((float("inf"), "tier_2"))
        return ladder

    def _approval_authority_group(self, tier):
        """The coded deciding group: CFO / MD for DOFA tiers 4-5, the
        Accounting Administrator below them. Never read from the rule book."""
        xmlid = TIER_GROUP.get(tier) if tier in ("tier_4", "tier_5") else GROUP_ADMINISTRATOR
        group = self.env.ref(xmlid, raise_if_not_found=False)
        return group if group and group._name == "res.groups" else None

    def _approval_resolve(self, rule, tier):
        # The coded finance group, without the DOFA "lowest competent tier"
        # narrowing (it looks at DOFA tier groups the finance roles do not hold).
        group = self._approval_group_for(rule, tier)
        users = self._approval_holders(group)
        return self._approval_substitutes(users)

    # ---- who may never decide ----------------------------------------------
    def _fin_requester(self):
        """Per model: the user who asked for the approval (submitter, preparer)."""
        return self.env["res.users"]

    def _fin_extra_conflicts(self):
        """Per model: further users who must not decide (payee-changer…)."""
        return self.env["res.users"]

    def _fin_conflicted_users(self):
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.create_uid
            | rec.approval_amount_changed_by_id
            | rec.approval_request_id.requested_by_id
            | rec._fin_requester()
            | rec._fin_extra_conflicts()
        ).sudo()

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._fin_conflicted_users()).sudo()

    def _fin_assert_decider(self, group_xmlid, tier_label):
        """The deciding user (and the absent approver a delegate acts for)
        holds the group and is not conflicted."""
        self.ensure_one()
        if self.env.su:
            return
        task = self._approval_task()
        authority = task.on_behalf_of_id or self.env.user
        if not holds(authority, group_xmlid):
            group = self.env.ref(group_xmlid, raise_if_not_found=False)
            raise AccessError(
                "%s of %s needs %s (%s), which you do not hold."
                % (
                    self._fin_what,
                    self._dofa_amount_label(),
                    group.name if group else group_xmlid,
                    tier_label,
                )
            )
        clash = (self.env.user | task.on_behalf_of_id) & self._fin_conflicted_users()
        if clash:
            raise UserError(
                "Segregation of duties: %s raised, requested, prepared or changed %s and "
                "cannot approve it." % (", ".join(clash.mapped("name")), self.display_name)
            )

    # ---- per-model hooks ----------------------------------------------------
    def _fin_before_approve(self):
        """Per model: the state and content checks that must hold to approve."""
        return None

    def _fin_after_approve(self):
        """Per model: what the approval does (state, pinned snapshot)."""
        return None

    def _fin_stamp(self):
        self.ensure_one()
        self.sudo()._guarded().write(
            {
                "fin_approved_by_id": self.env.uid,
                "fin_approved_at": fields.Datetime.now(),
                "fin_approved_amount": abs(self._dofa_amount() or 0.0),
            }
        )

    # ---- the two approval paths ---------------------------------------------
    def _fin_approve_direct(self):
        """Within the direct band: a second Accountant approves, no M63 request."""
        for rec in self:
            tier = rec._dofa_current_tier()
            if tier != "tier_0":
                raise UserError(
                    "%s of %s is above the direct approval band and is approved from the "
                    "M63 approval inbox (%s): request approval."
                    % (rec._fin_what, rec._dofa_amount_label(), dict(DOFA_TIERS)[tier])
                )
            rec._fin_assert_decider(GROUP_ACCOUNTANT, "Finance Officer band")
            rec._fin_before_approve()
            rec._fin_stamp()
            rec._fin_after_approve()
        return True

    def action_dofa_approve(self):
        """The engine's apply method (from the approver's inbox task): the coded
        finance group of the live tier, never a conflicted user. The stamps are
        written as the system after those checks; they name the approver."""
        self._approval_assert_routed()
        for rec in self:
            tier = rec._dofa_current_tier()
            if tier == "tier_0":
                raise UserError(
                    "Nothing to route: %s is within the direct approval band."
                    % rec._dofa_amount_label()
                )
            group = rec._approval_authority_group(tier)
            xmlid = TIER_GROUP.get(tier) if tier in ("tier_4", "tier_5") else GROUP_ADMINISTRATOR
            if group is None:
                raise UserError("The approving group %s is not installed." % xmlid)
            rec._fin_assert_decider(xmlid, dict(DOFA_TIERS)[tier])
            rec._fin_before_approve()
            rec.sudo()._guarded().write(
                {
                    "dofa_approved": True,
                    "dofa_approved_by": self.env.uid,
                    "dofa_approved_at": fields.Datetime.now(),
                    "dofa_approved_tier": tier,
                    "dofa_approved_amount": abs(rec._dofa_amount() or 0.0),
                }
            )
            rec._fin_stamp()
            rec._fin_after_approve()
            if hasattr(rec, "message_post"):
                rec.sudo().message_post(
                    body="%s %s approved by %s (%s)."
                    % (
                        rec._fin_what,
                        rec._dofa_amount_label(),
                        self.env.user.name,
                        dict(DOFA_TIERS)[tier],
                    )
                )
        return True

    def _fin_route(self, justification):
        """Hand an above-band record to M63; within the band nothing is routed."""
        for rec in self:
            if rec._dofa_current_tier() == "tier_0":
                continue
            if rec.approval_state == "pending":
                continue
            try:
                rec.action_request_approval(justification=justification)
            except UserError as exc:
                if not rec.env.su:
                    raise
                # A system caller (relay, concession closure) raised the
                # record: it waits for finance to request the approval once an
                # approver is appointed, rather than failing the caller.
                if hasattr(rec, "message_post"):
                    rec.message_post(body="Approval not yet requested: %s" % exc)
        return True

    def _fin_assert_approved(self):
        """The approval still covers the record (direct or routed)."""
        for rec in self:
            if rec.env.su and not rec.fin_approved_by_id and rec._dofa_current_tier() == "tier_0":
                continue
            if not rec.fin_approved_by_id:
                raise UserError("%s %s has not been approved." % (rec._fin_what, rec.display_name))
            current = abs(rec._dofa_amount() or 0.0)
            if current > (rec.fin_approved_amount or 0.0) + 0.005:
                raise UserError(
                    "%s was approved for %.2f but now stands at %s; it must be approved again."
                    % (rec._fin_what, rec.fin_approved_amount or 0.0, rec._dofa_amount_label())
                )
            if rec._dofa_current_tier() != "tier_0":
                rec._dofa_assert_approved(rec._fin_what)

    def _fin_void(self, reason):
        """Withdraw a finance approval and any routed request."""
        for rec in self:
            if rec.approval_state in ("pending", "approved", "returned"):
                rec._approval_void(reason)
            if rec.dofa_approved:
                rec._dofa_void_approval(reason)
            if rec.fin_approved_by_id:
                rec.sudo()._guarded().write(
                    {
                        "fin_approved_by_id": False,
                        "fin_approved_at": False,
                        "fin_approved_amount": 0.0,
                    }
                )
