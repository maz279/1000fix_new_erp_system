# fix.branch.checklist — the branch's daily opening and closing checklist
# (FR-FRD-020 / FR-FRD-024, with the shift handover note of FR-FRD-022).
#
# M04 sub-module audit (13 Nov 2026): the M04 "Open/Close Checklists" screen
# was a report derived from cash shifts and nothing recorded a checklist, so
# the Branch Admin sub-module had no data capture at all. A checklist is
# started with the items the specification names for its type, the counter
# staff tick each item (or write why it is not done), and Complete stamps who
# signed it off and when. A completed checklist is evidence: it is frozen.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_cash_shift import fill_operating_unit

# The items of FR-FRD-020 (opening: safety, equipment, stock, cash, staffing)
# and FR-FRD-024 (closing: cash counted, devices secured, orders updated,
# alarms set). A branch adds its own lines on the form.
CHECKLIST_ITEMS = {
    "opening": (
        ("safety", "Fire exits clear, extinguisher and first-aid kit in place"),
        ("equipment", "Counter PCs, token display, printers and scanners working"),
        ("stock", "Counter-sale stock and sealed accessory bags available"),
        ("cash", "Opening float counted and a cash shift opened"),
        ("staffing", "Rostered counter staff present"),
    ),
    "closing": (
        ("cash", "Cash counted and the shift closed for counting"),
        ("custody", "Customer devices secured in their storage bins"),
        ("orders", "Today's service orders updated"),
        ("security", "Alarm set, safe and doors locked"),
    ),
}

AREAS = [
    ("safety", "Safety"),
    ("equipment", "Equipment"),
    ("stock", "Stock"),
    ("cash", "Cash"),
    ("staffing", "Staffing"),
    ("custody", "Device Custody"),
    ("orders", "Service Orders"),
    ("security", "Security"),
    ("other", "Other"),
]

GROUPS = (
    "cd_front_desk.group_fd_cashier",
    "cd_front_desk.group_fd_branch_manager",
    "cd_front_desk.group_fd_queue_agent",
)


class FixBranchChecklist(models.Model):
    """A branch's opening or closing checklist for one day."""

    _name = "fix.branch.checklist"
    _description = "Branch Opening / Closing Checklist"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "checklist_date desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "completed_by_id", "completed_at"}

    _FROZEN_WHEN_COMPLETED = frozenset(
        {
            "branch_id",
            "operating_unit_id",
            "company_id",
            "checklist_type",
            "checklist_date",
            "line_ids",
            "handover_notes",
        }
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state == "completed" for rec in self):
            return locked | self._FROZEN_WHEN_COMPLETED
        return locked

    name = fields.Char(compute="_compute_name", store=True, string="Checklist")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", required=True, index=True)
    checklist_type = fields.Selection(
        [("opening", "Opening"), ("closing", "Closing")],
        string="Opening or Closing",
        required=True,
        default="opening",
    )
    checklist_date = fields.Date(
        string="Business Day", required=True, default=fields.Date.context_today, index=True
    )
    line_ids = fields.One2many("fix.branch.checklist.line", "checklist_id", string="Items")
    handover_notes = fields.Text(
        string="Handover Notes",
        help="What the incoming team needs to know: open items, pending collections, "
        "equipment faults (FR-FRD-022).",
    )
    open_item_count = fields.Integer(
        compute="_compute_open_items", string="Items Not Done", store=True
    )
    state = fields.Selection(
        [("draft", "In Progress"), ("completed", "Completed")],
        default="draft",
        required=True,
        tracking=True,
    )
    completed_by_id = fields.Many2one("res.users", string="Signed Off By", readonly=True)
    completed_at = fields.Datetime(string="Signed Off At", readonly=True)

    @api.depends("branch_id", "checklist_type", "checklist_date")
    def _compute_name(self):
        types = dict(self._fields["checklist_type"].selection)
        for rec in self:
            rec.name = "%s %s %s" % (
                rec.branch_id.code or rec.branch_id.name or "",
                types.get(rec.checklist_type, ""),
                rec.checklist_date or "",
            )

    @api.depends("line_ids.done")
    def _compute_open_items(self):
        for rec in self:
            rec.open_item_count = len(rec.line_ids.filtered(lambda line: not line.done))

    @api.constrains("branch_id", "checklist_type", "checklist_date")
    def _check_one_per_day(self):
        """One opening and one closing checklist per branch per business day."""
        for rec in self:
            twin = self.sudo().search(
                [
                    ("id", "!=", rec.id),
                    ("branch_id", "=", rec.branch_id.id),
                    ("checklist_type", "=", rec.checklist_type),
                    ("checklist_date", "=", rec.checklist_date),
                ],
                limit=1,
            )
            if twin:
                raise ValidationError(
                    "%s already has its %s checklist for %s (%s): open that one."
                    % (
                        rec.branch_id.display_name,
                        dict(self._fields["checklist_type"].selection)[rec.checklist_type].lower(),
                        rec.checklist_date,
                        twin.name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        fill_operating_unit(self.env, vals_list)
        for vals in vals_list:
            if not vals.get("line_ids"):
                items = CHECKLIST_ITEMS.get(vals.get("checklist_type") or "opening", ())
                vals["line_ids"] = [
                    (0, 0, {"sequence": (i + 1) * 10, "area": area, "name": text})
                    for i, (area, text) in enumerate(items)
                ]
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = self._FROZEN_WHEN_COMPLETED & set(vals)
            for rec in self.filtered(lambda r: r.state == "completed"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Checklist %s is signed off: it can no longer be changed." % rec.name
                    )
        return super().write(vals)

    def action_complete(self):
        """Sign the checklist off: every item is done, or says why it is not."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in GROUPS)):
            raise UserError(
                "Only branch counter staff or a Branch Manager may sign a checklist off."
            )
        for rec in self:
            if rec.state != "draft":
                raise UserError("Checklist %s is already signed off." % rec.name)
            if not rec.line_ids:
                raise UserError("Checklist %s has no items to sign off." % rec.name)
            loose = rec.line_ids.filtered(
                lambda line: not line.done and not (line.note or "").strip()
            )
            if loose:
                raise UserError(
                    "Checklist %s: tick each item, or write why it is not done, before signing "
                    "off. Not done and not explained: %s."
                    % (rec.name, "; ".join(loose.mapped("name")))
                )
            rec._guarded().write(
                {
                    "state": "completed",
                    "completed_by_id": self.env.uid,
                    "completed_at": fields.Datetime.now(),
                }
            )
        return True


class FixBranchChecklistLine(models.Model):
    _name = "fix.branch.checklist.line"
    _description = "Branch Checklist Item"
    _order = "checklist_id, sequence, id"

    checklist_id = fields.Many2one(
        "fix.branch.checklist", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=100)
    area = fields.Selection(AREAS, string="Area", default="other", required=True)
    name = fields.Char(string="Item", required=True)
    done = fields.Boolean(string="Done")
    note = fields.Char(string="Note / Why Not Done")

    def _fd_check_open(self, checklists):
        if self.env.su:
            return
        signed = checklists.filtered(lambda c: c.state == "completed")
        if signed:
            raise UserError(
                "Checklist %s is signed off: its items can no longer be changed."
                % ", ".join(signed.mapped("name"))
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = {v.get("checklist_id") for v in vals_list if v.get("checklist_id")}
        self._fd_check_open(self.env["fix.branch.checklist"].browse(list(ids)))
        return super().create(vals_list)

    def write(self, vals):
        self._fd_check_open(self.checklist_id)
        return super().write(vals)

    def unlink(self):
        self._fd_check_open(self.checklist_id)
        return super().unlink()
