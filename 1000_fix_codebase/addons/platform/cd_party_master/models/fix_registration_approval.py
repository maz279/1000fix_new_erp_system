# fix.registration.approval — multi-tier registration approval (M33,
# FR-CPM-010, BRU-CPM-02). Dealer, corporate and government accounts
# transact only after the client's OWN line manager AND a 1000FiX
# administrator have both approved (Service App SOW).
#
# A03 audit M33-1/M33-3: one user approved both steps (live approval id 2,
# both by uid 1 inside one second), there was no group check on either step,
# and nothing created the approval at all. Now:
#   - res.partner opens it when a party becomes dealer/corporate/government;
#   - each step is a routed M63 request (fix.approvable.mixin, domain
#     party_registration), decided from the approver's inbox only;
#   - the steps are TWO SEQUENTIAL REQUESTS, not one request with the
#     engine's approval_policy='all'. 'all' means "every holder of ONE group
#     must agree": it has no order and no second group, so it cannot say
#     "a line manager first, then a different person from the 1000FiX
#     administrators". Two requests give each step its own group, its own
#     SLA and escalation, and its own history; the administrator request does
#     not exist until the line manager has approved, and it is routed with
#     the line manager, the requester and the creator excluded;
#   - the apply methods re-check the group and segregation of duties, so a
#     change of group membership after routing still cannot let one person
#     decide both steps.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .res_partner import REGISTERED_CLASSES

LM_GROUP = "cd_party_master.group_party_registration_lm"
ADMIN_GROUP = "cd_party_master.group_party_registration_admin"


class FixRegistrationApproval(models.Model):
    """The two-tier approval chain for a dealer / corporate / government
    party: client line manager first, 1000FiX administrator second."""

    _name = "fix.registration.approval"
    _description = "Registration Approval"
    # fix.approvable.mixin already carries fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "requested_at desc, id desc"

    _approval_domain = "party_registration"
    _approval_apply_method = "action_approve_step"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # A plain write approved both steps with a forged decider (A03 audit).
        return super()._fix_guarded_fields() | {
            "lm_state",
            "admin_state",
            "lm_decided_by",
            "lm_on_behalf_of_id",
            "lm_decided_at",
            "admin_decided_by",
            "admin_decided_at",
        }

    def _fix_form_locked_fields(self) -> set:
        # Once raised, an approval is FOR one party and class: re-pointing an
        # approved row at another party would hand it the decision.
        locked = super()._fix_form_locked_fields()
        return locked | {"partner_id", "party_class"} if self else locked

    def write(self, vals):
        if not self._fix_guard_open():
            for name in vals.keys() & {"partner_id", "party_class"}:
                if any(rec._fix_guard_differs(name, vals[name], rec[name]) for rec in self):
                    raise UserError(
                        "A registration approval cannot be moved to another party or "
                        "class. Raise a new one instead."
                    )
        return super().write(vals)

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    party_class = fields.Selection(
        [
            ("dealer", "Dealer"),
            ("corporate", "Corporate"),
            ("government", "Government"),
        ],
        string="Party Class",
        required=True,
        tracking=True,
    )
    lm_state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="Client Line Manager",
        default="pending",
        required=True,
        tracking=True,
    )
    admin_state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        string="1000FiX Administrator",
        default="pending",
        required=True,
        tracking=True,
    )
    current_step = fields.Selection(
        [("lm", "Client Line Manager"), ("admin", "1000FiX Administrator"), ("done", "Decided")],
        string="Awaiting",
        compute="_compute_current_step",
    )
    requested_at = fields.Datetime(
        string="Requested At", default=fields.Datetime.now, readonly=True
    )
    lm_decided_by = fields.Many2one("res.users", string="LM Decided By", readonly=True)
    lm_on_behalf_of_id = fields.Many2one(
        "res.users", string="LM Decided On Behalf Of", readonly=True
    )
    lm_decided_at = fields.Datetime(string="LM Decided At", readonly=True)
    admin_decided_by = fields.Many2one("res.users", string="Admin Decided By", readonly=True)
    admin_decided_at = fields.Datetime(string="Admin Decided At", readonly=True)
    reason = fields.Char(string="Reason / Notes")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("partner_id", "party_class")
    def _compute_display_name(self):
        labels = dict(self._fields["party_class"].selection)
        for approval in self:
            approval.display_name = "Registration: %s (%s)" % (
                approval.partner_id.display_name or "?",
                labels.get(approval.party_class, approval.party_class or "?"),
            )

    @api.depends("lm_state", "admin_state")
    def _compute_current_step(self):
        for approval in self:
            approval.current_step = approval._approval_step() or "done"

    # ---- birth --------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Partner = self.env["res.partner"].sudo()
        for vals in vals_list:
            partner = Partner.browse(vals.get("partner_id") or 0).exists()
            if not partner:
                continue
            if partner._fix_open_registration_approval():
                raise UserError(
                    "%s already has a registration approval in progress." % partner.display_name
                )
            party_class = vals.get("party_class") or (
                partner.party_class if partner.party_class in REGISTERED_CLASSES else False
            )
            if not party_class:
                raise UserError("Choose the party class (dealer, corporate or government).")
            vals["party_class"] = party_class
            if partner.party_class == "individual":
                # A registration raised from the approvals screen classifies the
                # party; _guarded() so the class change does not open a second one.
                partner._guarded().write({"party_class": party_class})
            elif partner.party_class != party_class:
                raise UserError(
                    "%s is classed as %s; a %s registration needs the party class "
                    "changed on the party record first."
                    % (partner.display_name, partner.party_class, party_class)
                )
        approvals = super().create(vals_list)
        for approval in approvals:
            partner = approval.partner_id.sudo()
            if partner.party_status in ("draft", "active"):
                # The only way into 'pending_approval' (A03 audit M33-3).
                partner._guarded().write(
                    {
                        "party_status": "pending_approval",
                        "status_reason": "Registration approval opened (%s)" % approval.party_class,
                        "status_since": fields.Date.context_today(approval),
                    }
                )
            approval._registration_route_first_step()
        return approvals

    def _registration_route_first_step(self):
        """Route the line-manager step. When nobody holds the group yet, the
        party is still created: the approval waits and says why."""
        self.ensure_one()
        try:
            with self.env.cr.savepoint():
                self.action_request_approval()
        except UserError as exc:
            self.message_post(
                body="Registration approval opened but not yet routed: %s Press 'Request "
                "Approval' once a line-manager approver is appointed." % exc.args[0]
            )

    # ---- engine hooks -------------------------------------------------------
    def _approval_step(self):
        """'lm', 'admin', or False when the chain is decided."""
        self.ensure_one()
        if self.lm_state == "pending" and self.admin_state == "pending":
            return "lm"
        if self.lm_state == "approved" and self.admin_state == "pending":
            return "admin"
        return False

    def _approval_needed(self) -> bool:
        return bool(self._approval_step())

    def _approval_group_xmlid(self):
        return ADMIN_GROUP if self._approval_step() == "admin" else LM_GROUP

    def _approval_group_for(self, rule, tier):
        # BRU-CPM-02 fixes WHO decides each step. A fix.approval.matrix row
        # for party_registration tunes the SLA, escalation and final action;
        # its approver group would otherwise route both steps to one group.
        return self.env.ref(self._approval_group_xmlid(), raise_if_not_found=False)

    def _registration_prior_parties(self):
        """Everyone who already acted on this chain: requesters of earlier
        rounds, the line manager (and whom they acted for), earlier approvers."""
        self.ensure_one()
        requests = (
            self.env["fix.approval.request"]
            .sudo()
            .search([("res_model", "=", self._name), ("res_id", "=", self.id)])
        )
        approved = requests.task_ids.filtered(lambda t: t.decision == "approved")
        return (
            self.lm_decided_by
            | self.lm_on_behalf_of_id
            | requests.requested_by_id
            | approved.assigned_user_id
            | approved.on_behalf_of_id
        ).sudo()

    def _approval_excluded(self):
        # The engine already excludes the requester and the creator; the
        # administrator step must also exclude the line manager.
        return super()._approval_excluded() | self._registration_prior_parties()

    def _approval_on_rejected(self, comment):
        self._registration_reject(comment or "rejected in the approval inbox")

    # ---- decisions (run by the engine from the approver's inbox) -------------
    def action_approve_step(self):
        """The engine's apply method: decide whichever step is open."""
        self._approval_assert_routed()
        for approval in self:
            step = approval._approval_step()
            if step == "lm":
                approval.action_lm_approve()
            elif step == "admin":
                approval.action_admin_approve()
            else:
                raise ValidationError("This registration approval is already decided.")
        return True

    def _registration_check_group(self, xmlid: str, step_label: str):
        if self.env.su:
            return
        authority = self._approval_authority_user()
        if not authority.has_group(xmlid):
            raise UserError(
                "The %s step needs the '%s' group, which %s does not hold."
                % (step_label, self.env.ref(xmlid).name, authority.name)
            )

    def action_lm_approve(self):
        self._approval_assert_routed()
        for approval in self:
            if approval.lm_state != "pending":
                raise ValidationError("The line-manager step is already %s" % approval.lm_state)
            approval._registration_check_group(LM_GROUP, "line-manager")
            acting = approval._approval_acting_users()
            if not self.env.su and approval.create_uid in acting:
                raise UserError(
                    "Segregation of duties: you raised this registration request, so "
                    "another person must give the line-manager approval."
                )
            task = approval._approval_task()
            approval._guarded().write(
                {
                    "lm_state": "approved",
                    "lm_decided_by": self.env.user.id,
                    "lm_on_behalf_of_id": task.on_behalf_of_id.id or False,
                    "lm_decided_at": fields.Datetime.now(),
                }
            )
            approval._registration_route_admin_step()
        return True

    def _registration_route_admin_step(self):
        """Open the second request. Raised (and the line manager's decision
        rolled back) when no administrator other than the people who already
        acted can take it: one person must never complete both steps."""
        self.ensure_one()
        task = self._approval_task()
        current = self.approval_request_id
        if current and current.state == "pending" and task.request_id != current:
            # Decided outside the inbox (superuser): close the open round.
            self._approval_void("line-manager step decided outside the approval inbox")
        self._guarded().write({"approval_state": "none"})
        self.action_request_approval()

    def action_admin_approve(self):
        self._approval_assert_routed()
        for approval in self:
            # BRU-CPM-02: the administrator acts only AFTER the client's own
            # line manager — one approval step is not enough.
            if approval.lm_state != "approved":
                raise ValidationError(
                    "The client line manager must approve before the 1000FiX "
                    "administrator (BRU-CPM-02)"
                )
            if approval.admin_state != "pending":
                raise ValidationError("The administrator step is already %s" % approval.admin_state)
            approval._registration_check_group(ADMIN_GROUP, "1000FiX administrator")
            # BRU-CPM-02 is a TWO-person chain. One user did both steps on
            # live approval id 2, and on the probe, inside the same second.
            already = approval._registration_prior_parties() | approval.create_uid
            if not self.env.su and approval._approval_acting_users() & already:
                raise UserError(
                    "Segregation of duties: the 1000FiX administrator approval must "
                    "come from someone other than the requester and the line manager."
                )
            approval._guarded().write(
                {
                    "admin_state": "approved",
                    "admin_decided_by": self.env.user.id,
                    "admin_decided_at": fields.Datetime.now(),
                }
            )
            approval._activate_if_complete()
        return True

    def action_reject(self, reason=None):
        """Direct rejection is for system code only: a person rejects from
        the approval inbox (task Reject, with a comment)."""
        self._approval_assert_routed()
        if not reason:
            raise ValidationError("A rejection needs its reason")
        self._registration_reject(reason)
        return True

    def _registration_reject(self, reason: str):
        for approval in self:
            approval._guarded().write(
                {
                    "lm_state": "rejected" if approval.lm_state == "pending" else approval.lm_state,
                    "admin_state": "rejected",
                    "reason": reason,
                }
            )
            partner = approval.partner_id.sudo()
            if partner.party_status == "pending_approval":
                # Back to unverified: a rejected dealer is refused downstream by
                # res.partner._fix_assert_party_usable until a new approval passes.
                partner._guarded().write(
                    {
                        "party_status": "draft",
                        "status_reason": "Registration rejected: %s" % reason,
                        "status_since": fields.Date.context_today(approval),
                    }
                )

    def _fully_approved(self) -> bool:
        return self.lm_state == "approved" and self.admin_state == "approved"

    def _activate_if_complete(self):
        """Both tiers approved → the party may transact (party.activated)."""
        for approval in self:
            partner = approval.partner_id.sudo()
            if approval._fully_approved() and partner.party_status in (
                "draft",
                "pending_approval",
            ):
                # sudo(): the administrator need not hold Contact rights to
                # complete the chain (the audit's plain user hit an AccessError).
                partner._guarded().write(
                    {
                        "party_status": "active",
                        "status_reason": "Registration approved (line manager + administrator)",
                        "status_since": fields.Date.context_today(approval),
                    }
                )
                from libs.py.fix_events import publish

                publish(
                    self.env,
                    "party.activated",
                    "res.partner",
                    partner.id,
                    {"party_class": approval.party_class, "chain": "line_manager+administrator"},
                )
