# fix.so.approval — the M01 approvals as routed M63 requests (A02 audit B1).
#
# Three M01 approvals were decided by whoever pressed the button and held the
# group: the BRU-SRM-08 branch-manager key on an estimate, a goodwill
# (zero-charge) repair and a zero-charge rework. They had no request, no named
# approver, no deadline, no delegate and no history.
#
# Each is now a request record here, routed by the M63 engine
# (fix.approvable.mixin, _approval_routed): the requester asks, the engine
# routes to the competent holders (minus requester and the order's and
# estimate's creators), and the approver decides from the inbox. The decision
# runs the target's own approve method (action_manager_approve,
# action_approve_goodwill, action_approve_rework) with this request in
# context; pressed directly, those methods refuse.
#
# A request of its own, not the estimate's approval_state: fix.estimate
# already routes its discount DOFA through the engine, and one record carries
# one approval at a time.
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.models import BaseModel

# The in-process key action_apply puts in context: a recordset, which a
# JSON-RPC caller cannot forge (the engine's TASK_KEY works the same way).
ROUTED_KEY = "fix_so_approval_request"
TASK_KEY = "fix_approval_task"  # cd_workflow_engine.models.fix_approval_engine

ROUTED_MESSAGE = (
    "%s is approved from the approver's inbox, not directly. Use %s: the approval "
    "engine (M63) routes it to someone who holds the required authority."
)
KINDS = [
    ("manager_key", "Branch-Manager Key (BRU-SRM-08)"),
    ("goodwill", "Goodwill Repair (FR-SRM-075)"),
    ("rework", "Zero-Charge Rework (BRU-SRM-06)"),
]
_REQUEST_LABEL = {
    "manager_key": "Request Manager Key",
    "goodwill": "Request Goodwill",
    "rework": "Request Rework Approval",
}
COMMERCIAL_APPROVER = "cd_service_order.group_so_commercial_approver"


class FixSoApproval(models.Model):
    _name = "fix.so.approval"
    _description = "M01 Approval Request"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "service_order_approval"
    _approval_apply_method = "action_apply"
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # What was asked for and the amount it covers are the request.
        return super()._fix_guarded_fields() | {
            "kind",
            "order_id",
            "estimate_id",
            "amount",
            "reason",
        }

    name = fields.Char(compute="_compute_name", store=True)
    kind = fields.Selection(KINDS, required=True, readonly=True)
    order_id = fields.Many2one(
        "fix.service.order", required=True, readonly=True, index=True, ondelete="cascade"
    )
    estimate_id = fields.Many2one("fix.estimate", readonly=True, index=True, ondelete="cascade")
    company_id = fields.Many2one(related="order_id.company_id", store=True)
    branch_id = fields.Many2one(related="order_id.branch_id", store=True)
    operating_unit_id = fields.Many2one(related="order_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="order_id.currency_id")
    amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="What the approval covers, pinned at the request: the estimate total "
        "(manager key) or the amount waived (goodwill, rework). A higher amount "
        "at decision time is refused; request again.",
    )
    reason = fields.Text(readonly=True)

    @api.depends("kind", "order_id.name", "estimate_id.version")
    def _compute_name(self):
        labels = dict(KINDS)
        for rec in self:
            target = rec.order_id.name or ""
            if rec.estimate_id:
                target = "%s v%d" % (target, rec.estimate_id.version)
            rec.name = "%s: %s" % (labels.get(rec.kind, rec.kind or ""), target)

    # ---- engine hooks -----------------------------------------------------
    def _approval_amount(self) -> float:
        return self.amount or 0.0

    def _approval_tier(self):
        # The BRU-SRM-08 second key is a branch manager: DOFA Tier 2, with the
        # engine's escalation to Tier 3. Goodwill and rework use their group.
        return "tier_2" if self.kind == "manager_key" else False

    def _approval_group_xmlid(self):
        return COMMERCIAL_APPROVER if self.kind in ("goodwill", "rework") else None

    def _approval_excluded(self):
        """Nor the people who raised the order or prepared the estimate: the
        actions' own segregation-of-duties checks would refuse them anyway."""
        excluded = super()._approval_excluded()
        return excluded | (self.order_id.create_uid | self.estimate_id.create_uid).sudo()

    # ---- requester side ---------------------------------------------------
    @api.model
    def _fix_open(self, kind, order, reason, estimate=None):
        """Create the request and route it. One live request per target."""
        live = self.search(
            [
                ("kind", "=", kind),
                ("order_id", "=", order.id),
                ("estimate_id", "=", estimate.id if estimate else False),
                ("approval_state", "=", "pending"),
            ],
            limit=1,
        )
        if live:
            raise UserError("%s is already awaiting approval." % live.name)
        amount = estimate.grand_total if kind == "manager_key" else order._fix_amount_due()
        req = self._guarded().create(
            {
                "kind": kind,
                "order_id": order.id,
                "estimate_id": estimate.id if estimate else False,
                "amount": amount,
                "reason": reason,
            }
        )
        req.action_request_approval(justification=reason)
        (estimate or order).message_post(
            body="%s requested by %s; routed to the approver's inbox."
            % (dict(KINDS)[kind], self.env.user.name)
        )
        return req

    # ---- the decision -----------------------------------------------------
    def action_apply(self):
        """The engine runs this when the approver approves from the inbox."""
        self._approval_assert_routed()
        for req in self:
            if req.kind == "manager_key":
                target, current = req.estimate_id, req.estimate_id.grand_total
            else:
                target, current = req.order_id, req.order_id._fix_amount_due()
            if (current or 0.0) > (req.amount or 0.0) + 0.005:
                raise UserError(
                    "%s was requested for BDT %.2f; it now stands at BDT %.2f. Request it "
                    "again on the new amount." % (req.name, req.amount, current)
                )
            routed = target.with_context(**{ROUTED_KEY: req})
            if req.kind == "manager_key":
                routed.action_manager_approve()
            elif req.kind == "goodwill":
                routed.action_approve_goodwill(req.reason)
            else:
                routed.action_approve_rework(req.reason)
        return True

    # ---- helpers the targets call -------------------------------------------
    @api.model
    def _fix_assert_routed(self, target, kind):
        """Refuse a direct press of the target's approve method: only this
        request's action_apply, deciding a task from the inbox, may run it.
        Superuser service code stays trusted, as by the engine."""
        if self.env.su:
            return
        req = self.env.context.get(ROUTED_KEY)
        field = "estimate_id" if kind == "manager_key" else "order_id"
        own = isinstance(req, BaseModel) and req._name == self._name and len(req) == 1
        task = req._approval_task() if own else None
        if not (
            task
            and req.kind == kind
            and req[field] == target
            and task.res_model == req._name
            and task.res_id == req.id
        ):
            raise UserError(ROUTED_MESSAGE % (dict(KINDS)[kind], _REQUEST_LABEL[kind]))

    @api.model
    def _fix_authority_user(self):
        """Whose authority covers the decision: the absent approver when a
        delegate decides on their behalf (M63 substitution)."""
        task = self.env.context.get(TASK_KEY)
        if isinstance(task, BaseModel) and task._name == "fix.workflow.task":
            return task.on_behalf_of_id or self.env.user
        return self.env.user

    @api.model
    def _fix_acting_users(self):
        task = self.env.context.get(TASK_KEY)
        if isinstance(task, BaseModel) and task._name == "fix.workflow.task":
            return self.env.user | task.on_behalf_of_id
        return self.env.user


class FixApprovalMatrixServiceOrderApproval(models.Model):
    _inherit = "fix.approval.matrix"

    # A02 audit B1: lets a DoA matrix row target this routed approval.
    decision_domain = fields.Selection(
        selection_add=[("service_order_approval", "Service Order Manager Key / Goodwill / Rework")],
        ondelete={"service_order_approval": "cascade"},
    )
