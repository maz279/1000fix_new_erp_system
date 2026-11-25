# fix.sla.policy + fix.diagnostic.node — the two masters the service-order
# core references (P04-M03-T04/T05). Found dangling by the relation-integrity
# audit: sla_policy_id and diagnostic_tree_id pointed at models that were
# never written — Odoo's registry load would crash on cd_service_order.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixSlaPolicy(models.Model):
    """An SLA policy: response and resolution targets for one service type
    and priority. The clock ENGINE (services/sla-engine, Phase 5) consumes
    these targets against the branch working calendar; the policy itself is
    estate-wide master data (no OU — a promise made in one branch is the
    promise)."""

    _name = "fix.sla.policy"
    _description = "SLA Policy"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "SLA policy code must be unique")

    code = fields.Char(string="SLA Code", required=True, size=16)
    name = fields.Char(string="SLA Policy", required=True)
    service_type = fields.Selection(
        [
            ("walk_in", "Walk-in"),
            ("collection", "Collection/Delivery"),
            ("onsite", "On-site"),
            ("mail_in", "Mail-in"),
            ("corporate", "Corporate/Bulk"),
        ],
        string="Service Type",
        required=True,
    )
    priority = fields.Selection(
        [("normal", "Normal"), ("high", "High"), ("urgent", "Urgent"), ("emergency", "Emergency")],
        string="Priority",
        required=True,
        default="normal",
    )
    # Targets in HOURS of business time (fix.working.calendar); the engine
    # converts hours to deadlines per branch calendar. BRU-SRM-10: Gold and
    # Diamond members map to priority-1 policies automatically.
    response_hours = fields.Float(
        string="Response Target (hours)",
        required=True,
        help="Assignment to first action, business hours",
    )
    resolution_hours = fields.Float(
        string="Resolution Target (hours)", required=True, help="Intake to ready, business hours"
    )
    escalation_template_id = fields.Many2one(
        "mail.template",
        string="Escalation Template",
        help="NT-020 escalation template fired on breach / near-breach",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True, tracking=True)

    @api.constrains("response_hours", "resolution_hours")
    def _check_targets(self):
        for policy in self:
            if policy.response_hours <= 0 or policy.resolution_hours <= 0:
                raise ValidationError("SLA targets must be positive (business hours)")
            if policy.response_hours > policy.resolution_hours:
                raise ValidationError("Response target cannot exceed resolution target")


class FixDiagnosticNode(models.Model):
    """A node in the guided diagnostic decision tree (T05). Non-terminal
    nodes pose a question; terminal nodes carry the fault code and the
    recommended action. Trees are versionless masters: correcting a tree is
    an edit, because work orders store the traversed node, not a snapshot."""

    _name = "fix.diagnostic.node"
    _description = "Diagnostic Tree Node"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"

    name = fields.Char(string="Question / Symptom", required=True)
    code = fields.Char(string="Node Code", required=True, size=24, index=True)
    parent_id = fields.Many2one(
        "fix.diagnostic.node", string="Parent Node", index=True, ondelete="restrict"
    )
    children_ids = fields.One2many("fix.diagnostic.node", "parent_id", string="Answers / Children")
    is_terminal = fields.Boolean(
        string="Terminal Node",
        compute="_compute_is_terminal",
        store=True,
        help="A node with no children ends a diagnostic path",
    )
    fault_code = fields.Char(
        string="Fault Code", help="Set on terminal nodes: feeds work_order.diagnosed_fault_code"
    )
    recommended_action = fields.Text(string="Recommended Action")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "Diagnostic node code must be unique")

    @api.depends("children_ids")
    def _compute_is_terminal(self):
        for node in self:
            node.is_terminal = not node.children_ids

    @api.constrains("is_terminal", "fault_code")
    def _check_terminal(self):
        for node in self:
            if node.is_terminal and not node.fault_code:
                raise ValidationError("A terminal diagnostic node must carry a fault code")
            if not node.is_terminal and node.fault_code:
                raise ValidationError("Only terminal nodes carry a fault code")

    @api.constrains("parent_id")
    def _check_no_cycle(self):
        for node in self:
            seen, walk = {node.id}, node.parent_id
            while walk:
                if walk.id in seen:
                    raise ValidationError("Diagnostic tree contains a cycle")
                seen.add(walk.id)
                walk = walk.parent_id
