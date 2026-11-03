# fix_equipment_ops — M45: kits, issue/return custody, transfers, physical
# verification, out-of-service enforcement, PM/corrective jobs and usage capture.
# The equipment register and calibration records live in fix_equipment.py.
#
# A07 audit (2026-11-03) D1: every workflow field below (issue, transfer,
# verification, out-of-service and PM state, and the equipment's operational
# status) was writable by any internal user, through the ORM and the P03 form.
# Each model now names its guarded fields (fix.guarded.mixin) and moves them
# only in its transition methods, through `_guarded()`. A record in a terminal
# state is frozen for users. Superuser code (seeds, data loads, sudo service
# calls) stays trusted.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixEquipmentExtend(models.Model):
    _inherit = "fix.equipment"

    operational_status = fields.Selection(
        [
            ("available", "Available"),
            ("issued", "Issued"),
            ("out_of_service", "Out of Service"),
            ("retired", "Retired"),
        ],
        required=True,
        default="available",
        index=True,
    )

    def _m45_released_status(self):
        """The status an item returns to when a hold on it ends: out of
        service while another out-of-service record is open, issued while an
        issue is open, otherwise available."""
        self.ensure_one()
        rec = self.sudo()
        if rec.env["fix.equipment.oos"].search_count(
            [("equipment_id", "=", rec.id), ("state", "=", "open")]
        ):
            return "out_of_service"
        if rec.env["fix.equipment.issue"].search_count(
            [("equipment_id", "=", rec.id), ("state", "=", "issued")]
        ):
            return "issued"
        return "available"


class FixCalibrationExtend(models.Model):
    _inherit = "fix.calibration"

    certificate_ref = fields.Char(string="Certificate Reference")
    trace_no = fields.Char(string="Trace Number")


class FixEquipmentKit(models.Model):
    _name = "fix.equipment.kit"
    _description = "Equipment Kit"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    description = fields.Text()
    line_ids = fields.One2many("fix.equipment.kit.line", "kit_id", string="Equipment")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("UNIQUE (code)", "Kit code must be unique")


class FixEquipmentKitLine(models.Model):
    _name = "fix.equipment.kit.line"
    _description = "Kit Line"
    _order = "kit_id, id"

    kit_id = fields.Many2one("fix.equipment.kit", required=True, ondelete="cascade", index=True)
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade"
    )

    _unique_equipment = models.Constraint(
        "UNIQUE (kit_id, equipment_id)", "An equipment item appears once per kit"
    )


# An issue that has been returned is closed custody history.
ISSUE_RETURNED_FROZEN = {
    "equipment_id",
    "custodian_id",
    "reference",
    "issued_on",
    "due_on",
    "condition_out",
    "condition_in",
    "return_condition",
}


class FixEquipmentIssue(models.Model):
    _name = "fix.equipment.issue"
    _description = "Equipment Issue / Return"
    _inherit = ["fix.guarded.mixin"]
    _order = "issued_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    custodian_id = fields.Many2one("hr.employee", string="Custodian", required=True)
    reference = fields.Char(string="Job / Ticket Ref")
    issued_on = fields.Date(required=True, default=fields.Date.context_today)
    due_on = fields.Date()
    returned_on = fields.Date(readonly=True)
    condition_out = fields.Char()
    condition_in = fields.Char(help="What the returner found: describe any damage.")
    # A07 audit (2026-11-03) M45-5, BRU-EAM-10: action_return took no condition,
    # so a damaged return went straight back to available. The returner states
    # the condition; a damaged item goes out of service, never to available.
    return_condition = fields.Selection(
        [("good", "Serviceable"), ("damaged", "Damaged / Faulty")],
        string="Condition on Return",
    )
    state = fields.Selection(
        [("issued", "Issued"), ("returned", "Returned")], required=True, default="issued"
    )
    # A07 audit (2026-11-03) M45-5 / D9: is_overdue was STORED and depended on
    # due_on/state only, so it never turned True as the due date passed (live
    # issues due 30 Oct still read False). It is computed at read time now,
    # with a search method so the overdue filters and KPIs keep working.
    is_overdue = fields.Boolean(compute="_compute_overdue", search="_search_is_overdue")

    def _fix_guarded_fields(self) -> set:
        # M45-5: an issue forged to "returned" by write left the item "issued"
        # with no return date; only action_return closes an issue.
        guarded = super()._fix_guarded_fields() | {"state", "returned_on"}
        if any(rec.state == "returned" for rec in self):
            guarded |= ISSUE_RETURNED_FROZEN
        return guarded

    @api.depends("due_on", "state")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_on and rec.state == "issued" and rec.due_on < today)

    def _search_is_overdue(self, operator, value):
        # the ORM hands boolean conditions over as in / not in [True]; the
        # negative form is derived by the ORM from this positive one
        if operator != "in":
            return NotImplemented
        today = fields.Date.context_today(self)
        overdue = [("state", "=", "issued"), ("due_on", "!=", False), ("due_on", "<", today)]
        if True in value:
            return overdue
        return ["!", "&", "&", *overdue]

    # A07 audit (2026-11-03) M45-4 / M45-5: issuing never looked at the
    # instrument. An overdue, failed or never-calibrated item was issued; an
    # OUT-OF-SERVICE item was issued and create() overwrote its status to
    # "issued", erasing the out-of-service state; a retired item was issued;
    # and the same item was issued to two custodians at once.
    def _m45_check_issuable(self):
        for rec in self:
            equipment = rec.equipment_id.sudo()
            if rec.state != "issued":
                continue
            # custody truth holds for every caller, superuser included: these
            # are facts about the item, not approvals
            if equipment.operational_status in ("out_of_service", "retired"):
                label = dict(equipment._fields["operational_status"].selection).get(
                    equipment.operational_status
                )
                raise UserError("%s is %s and cannot be issued" % (equipment.name, label.lower()))
            if (
                self.env["fix.equipment.transfer"]
                .sudo()
                .search_count([("equipment_id", "=", equipment.id), ("state", "=", "dispatched")])
            ):
                raise UserError(
                    "%s is in transit to another branch and cannot be issued until the "
                    "transfer is received" % equipment.name
                )
            # fitness: superuser code (seeds, data loads, sudo service calls)
            # stays trusted; every user path is checked. The item's own status
            # was checked above (a second open issue is the constraint below).
            if not self.env.su:
                problem = equipment._m45_calibration_problem()
                if problem:
                    raise UserError("Cannot issue: " + problem)

    @api.constrains("equipment_id", "state")
    def _check_one_open_issue(self):
        """BRU-EAM-07: exactly one named holder at a time."""
        for rec in self.filtered(lambda r: r.state == "issued"):
            others = self.sudo().search_count(
                [
                    ("equipment_id", "=", rec.equipment_id.id),
                    ("state", "=", "issued"),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise ValidationError(
                    "%s is already issued; return it before issuing it again"
                    % rec.equipment_id.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.issue") or "EISS/New"
                )
        records = super().create(vals_list)
        for rec in records:
            if rec.state == "issued":
                rec._m45_check_issuable()
                rec.equipment_id._guarded().write({"operational_status": "issued"})
        return records

    def write(self, vals):
        if "equipment_id" not in vals:
            return super().write(vals)
        before = {rec.id: rec.equipment_id for rec in self}
        res = super().write(vals)
        for rec in self.filtered(lambda r: r.state == "issued"):
            old = before.get(rec.id)
            if old and old != rec.equipment_id:
                rec._m45_check_issuable()
                rec.equipment_id._guarded().write({"operational_status": "issued"})
                if old.operational_status == "issued":
                    old._guarded().write({"operational_status": old._m45_released_status()})
        return res

    def action_return(self, condition=None):
        """Close the issue with the item's condition (BRU-EAM-10): a
        serviceable item goes back to available, a damaged one out of
        service. `condition` may be passed, or set on the issue first."""
        conditions = dict(self._fields["return_condition"].selection)
        if condition is not None and condition not in conditions:
            raise UserError("Condition on return must be one of: %s" % ", ".join(conditions))
        for rec in self:
            if rec.state != "issued":
                raise UserError("Return an issued item")
            cond = condition or rec.return_condition
            if not cond and not self.env.su:
                raise UserError(
                    "Record the condition of %s on return (serviceable or damaged) before "
                    "returning it." % rec.equipment_id.name
                )
            vals = {"state": "returned", "returned_on": fields.Date.context_today(self)}
            if cond:
                vals["return_condition"] = cond
            rec._guarded().write(vals)
            equipment = rec.equipment_id
            if cond == "damaged":
                # the hold is opened by the returner, so the returner cannot
                # also resolve it (see fix.equipment.oos.action_resolve)
                self.env["fix.equipment.oos"].create(
                    {
                        "equipment_id": equipment.id,
                        "reason": "Returned damaged (%s): %s"
                        % (rec.name, (rec.condition_in or "").strip() or "no detail recorded"),
                    }
                )
            elif equipment.operational_status == "issued":
                # an item put out of service while it was out on issue stays out
                # of service; only the issued status is released (A07 M45-5)
                equipment._guarded().write({"operational_status": equipment._m45_released_status()})
        return True


TRANSFER_STATES = [
    ("draft", "Draft"),
    ("dispatched", "Dispatched (in transit)"),
    ("received", "Received"),
    ("cancelled", "Cancelled"),
    # before the A07 P0 build a transfer was born "posted" and moved nothing;
    # those rows stay as they are, closed
    ("posted", "Posted (legacy, moved nothing)"),
]
TRANSFER_CLOSED = ("received", "cancelled", "posted")


class FixEquipmentTransfer(models.Model):
    """Inter-branch transfer (FR-EAM-016, BRU-EAM-22).

    A07 audit (2026-11-03) M45-8: a transfer was born "posted", changed
    neither the equipment's branch nor its custodian, took a typed from-branch
    and posted for issued or out-of-service items. It now runs draft ->
    dispatched -> received: the sender stays accountable until a different
    user confirms receipt, and only the receipt moves the equipment."""

    _name = "fix.equipment.transfer"
    _description = "Equipment Transfer"
    _inherit = ["fix.guarded.mixin"]
    _order = "transfer_date desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    from_branch_id = fields.Many2one(
        "fix.branch", string="From Branch", help="Where the item sits: taken from the register."
    )
    to_branch_id = fields.Many2one("fix.branch", string="To Branch", required=True)
    from_custodian_id = fields.Many2one(
        "hr.employee", string="From Custodian", help="Taken from the register."
    )
    to_custodian_id = fields.Many2one("hr.employee", string="To Custodian")
    transfer_date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(TRANSFER_STATES, required=True, default="draft")
    notes = fields.Char()
    dispatched_by_id = fields.Many2one("res.users", string="Dispatched By", readonly=True)
    dispatched_on = fields.Date(readonly=True)
    received_by_id = fields.Many2one("res.users", string="Received By", readonly=True)
    received_on = fields.Date(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "dispatched_by_id",
            "dispatched_on",
            "received_by_id",
            "received_on",
        }
        if self:
            # the origin is the register's, and the item is fixed once raised
            guarded |= {"equipment_id", "from_branch_id", "from_custodian_id"}
        if any(rec.state != "draft" for rec in self):
            # what was dispatched is what the receiver confirms
            guarded |= {"to_branch_id", "to_custodian_id", "transfer_date"}
        if any(rec.state in TRANSFER_CLOSED for rec in self):
            guarded |= {"notes"}
        return guarded

    def _m45_check_movable(self, equipment):
        """Custody truth, for every caller: an item out on issue, out of
        service or retired does not travel."""
        equipment = equipment.sudo()
        if equipment.operational_status != "available":
            label = dict(equipment._fields["operational_status"].selection).get(
                equipment.operational_status
            )
            raise UserError(
                "%s is %s and cannot be transferred: only an available item travels"
                % (equipment.name, label.lower())
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.transfer") or "ETRF/New"
                )
            equipment = self.env["fix.equipment"].sudo().browse(vals.get("equipment_id"))
            if not equipment.exists():
                continue
            self._m45_check_movable(equipment)
            origin = {
                "from_branch_id": equipment.branch_id.id or False,
                "from_custodian_id": equipment.custodian_id.id or False,
            }
            for key, actual in origin.items():
                typed = vals.get(key) or False
                if not self.env.su and typed and typed != actual:
                    raise UserError(
                        "%s is registered at %s with %s: a transfer starts from where the "
                        "item is, not from a typed origin"
                        % (
                            equipment.name,
                            equipment.branch_id.name or "no branch",
                            equipment.custodian_id.name or "no custodian",
                        )
                    )
                if not self.env.su or key not in vals:
                    vals[key] = actual
        return super().create(vals_list)

    def action_dispatch(self):
        """The sender hands the item over; it stays theirs until receipt."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Dispatch a draft transfer")
            equipment = rec.equipment_id.sudo()
            rec._m45_check_movable(equipment)
            if self.sudo().search_count(
                [
                    ("equipment_id", "=", equipment.id),
                    ("state", "=", "dispatched"),
                    ("id", "!=", rec.id),
                ]
            ):
                raise UserError("%s is already in transit" % equipment.name)
            if (rec.to_branch_id or False) == (equipment.branch_id or False) and (
                rec.to_custodian_id or False
            ) == (equipment.custodian_id or False):
                raise UserError(
                    "%s is already at %s with that custodian: there is nothing to transfer"
                    % (equipment.name, equipment.branch_id.name or "no branch")
                )
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "dispatched_by_id": self.env.user.id,
                    "dispatched_on": fields.Date.context_today(self),
                    "from_branch_id": equipment.branch_id.id or False,
                    "from_custodian_id": equipment.custodian_id.id or False,
                }
            )
        return True

    def action_receive(self):
        """Receipt confirmed by someone other than the sender (BRU-EAM-22);
        only now do the equipment's branch and custodian move."""
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Confirm receipt of a dispatched transfer")
            if not self.env.su and rec.dispatched_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you dispatched %s, so its receipt must be "
                    "confirmed by someone at the receiving end." % rec.equipment_id.name
                )
            rec._guarded().write(
                {
                    "state": "received",
                    "received_by_id": self.env.user.id,
                    "received_on": fields.Date.context_today(self),
                }
            )
            equipment = rec.equipment_id
            moved = {"branch_id": rec.to_branch_id.id}
            if rec.to_custodian_id:
                moved["custodian_id"] = rec.to_custodian_id.id
            equipment._guarded().write(moved)
        return True

    def action_cancel(self):
        """Withdraw a transfer that has not been received; nothing moves."""
        for rec in self:
            if rec.state not in ("draft", "dispatched"):
                raise UserError("Only a draft or dispatched transfer can be cancelled")
            rec._guarded().write({"state": "cancelled"})
        return True


class FixEquipmentVerification(models.Model):
    _name = "fix.equipment.verification"
    _description = "Equipment Physical Verification"
    _inherit = ["fix.guarded.mixin"]
    _order = "verified_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    campaign_ref = fields.Char(string="Campaign", required=True)
    verified_on = fields.Date(required=True, default=fields.Date.context_today)
    location = fields.Char()
    found = fields.Boolean(default=True)
    condition = fields.Char()
    verifier_id = fields.Many2one("hr.employee", string="Verifier")
    state = fields.Selection(
        [("verified", "Verified"), ("missing", "Missing")], required=True, default="verified"
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-6: a "missing" result (the recorded loss)
        # was rewritten to verified/found by any user. The result follows
        # `found`, and a missing result is final for users.
        guarded = super()._fix_guarded_fields() | {"state"}
        if self:
            guarded |= {"equipment_id", "verified_on"}
        if any(rec.state == "missing" for rec in self):
            guarded |= {"found", "campaign_ref", "location", "condition", "verifier_id"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.verification") or "EVER/New"
                )
            # the result is derived from what was found, never typed
            vals["state"] = "missing" if vals.get("found") is False else "verified"
        records = super(FixEquipmentVerification, self._guarded()).create(vals_list)
        return records.with_env(self.env)

    def write(self, vals):
        res = super().write(vals)
        if "found" in vals and not vals["found"]:
            # found -> not found after the count: the result follows (M45 D2)
            self.filtered(lambda r: not r.found and r.state == "verified")._guarded().write(
                {"state": "missing"}
            )
        return res


class FixEquipmentOutOfService(models.Model):
    _name = "fix.equipment.oos"
    _description = "Out-of-Service Record"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    reason = fields.Char(required=True)
    started_on = fields.Date(required=True, default=fields.Date.context_today)
    resolved_on = fields.Date(readonly=True)
    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True)
    resolution_calibration_id = fields.Many2one(
        "fix.calibration",
        string="Re-calibration",
        readonly=True,
        help="The passing calibration, recorded after the item went out of service, that "
        "returned it to service.",
    )
    state = fields.Selection(
        [("open", "Open"), ("resolved", "Resolved")], required=True, default="open"
    )

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-7: the OOS state was forged to "resolved"
        # through P03, and a back-dated start would let an older pass count as
        # the re-calibration.
        guarded = super()._fix_guarded_fields() | {
            "state",
            "started_on",
            "resolved_on",
            "resolved_by_id",
            "resolution_calibration_id",
        }
        if self:
            guarded |= {"equipment_id"}
        if any(rec.state == "resolved" for rec in self):
            guarded |= {"reason"}
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.equipment.oos") or "EOOS/New"
                )
        records = super().create(vals_list)
        for rec in records:
            if rec.equipment_id.sudo().operational_status == "retired":
                raise UserError("%s is retired: it is out of use for good" % rec.equipment_id.name)
            rec.equipment_id._guarded().write({"operational_status": "out_of_service"})
        return records

    def _m45_recalibration(self):
        """The passing calibration that returns the item to service: the
        latest one, current, dated on or after the start and recorded after
        the hold was opened. None when there is no such calibration."""
        self.ensure_one()
        equipment = self.equipment_id.sudo()
        latest = equipment._m45_latest_calibration()
        if (
            latest
            and equipment.calibration_state == "current"
            and latest.calibrated_on >= self.started_on
            and latest.create_date >= self.create_date
        ):
            return latest
        return None

    def action_resolve(self):
        """Back to service only with a re-calibration, by someone other than
        the person who opened the hold (spec §8.1, SOD-07)."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Resolve an open out-of-service record")
            equipment = rec.equipment_id
            if equipment.sudo().operational_status == "retired":
                raise UserError("%s is retired and cannot return to service" % equipment.name)
            recal = rec._m45_recalibration()
            if not self.env.su:
                if rec.create_uid == self.env.user:
                    raise UserError(
                        "Segregation of duties: you opened %s, so another person must "
                        "accept the re-calibration and return the item to service." % rec.name
                    )
                if not recal:
                    raise UserError(
                        "%s cannot return to service without a passing calibration "
                        "recorded after it went out of service (on or after %s)."
                        % (equipment.name, rec.started_on)
                    )
            rec._guarded().write(
                {
                    "state": "resolved",
                    "resolved_on": fields.Date.context_today(self),
                    "resolved_by_id": self.env.user.id,
                    "resolution_calibration_id": recal.id if recal else False,
                }
            )
            if equipment.sudo().operational_status == "out_of_service":
                equipment._guarded().write({"operational_status": equipment._m45_released_status()})
        return True


class FixEquipmentPm(models.Model):
    _name = "fix.equipment.pm"
    _description = "Equipment PM / Corrective Job"
    _inherit = ["fix.guarded.mixin"]
    _order = "scheduled_on desc, id desc"

    name = fields.Char(required=True, default="New")
    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    pm_type = fields.Selection(
        [("preventive", "Preventive"), ("corrective", "Corrective")],
        required=True,
        default="preventive",
    )
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    done_on = fields.Date(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(currency_field="currency_id")
    technician_id = fields.Many2one("hr.employee", string="Technician")
    state = fields.Selection([("open", "Open"), ("done", "Done")], required=True, default="open")
    notes = fields.Char()

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M45-11: a PM job was forged to "done" by write;
        # a done job is the maintenance record and is frozen.
        guarded = super()._fix_guarded_fields() | {"state", "done_on"}
        if any(rec.state == "done" for rec in self):
            guarded |= {
                "equipment_id",
                "pm_type",
                "scheduled_on",
                "currency_id",
                "cost",
                "technician_id",
                "notes",
            }
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.equipment.pm") or "EPM/New"
        return super().create(vals_list)

    def action_done(self):
        """A07 audit (2026-11-03) M45-11: completion needed no evidence. A job
        is done with what was found and done (notes) and who did it."""
        for rec in self:
            if rec.state != "open":
                raise UserError("Complete an open job")
            if not self.env.su:
                missing = [
                    label
                    for ok, label in (
                        ((rec.notes or "").strip(), "completion notes"),
                        (rec.technician_id, "the technician"),
                    )
                    if not ok
                ]
                if missing:
                    raise UserError(
                        "Record %s on %s before marking it done."
                        % (" and ".join(missing), rec.name)
                    )
            rec._guarded().write({"state": "done", "done_on": fields.Date.context_today(self)})
        return True


class FixEquipmentUsage(models.Model):
    _name = "fix.equipment.usage"
    _description = "Equipment Usage per Job"
    _order = "used_on desc, id desc"

    equipment_id = fields.Many2one(
        "fix.equipment", string="Equipment", required=True, ondelete="cascade", index=True
    )
    job_ref = fields.Char(string="Job / Work Order", required=True)
    service_order_ref = fields.Char(string="Service Order")
    used_on = fields.Date(required=True, default=fields.Date.context_today)
    uses = fields.Integer(string="Uses", default=1)
    qc_result = fields.Selection(
        [("pass", "Pass"), ("fail", "Fail"), ("na", "Not a QC use")],
        required=True,
        default="na",
    )
    notes = fields.Char()

    _uses_positive = models.Constraint("CHECK (uses > 0)", "Usage count must be positive")

    # A07 audit (2026-11-03) M45-4 (BRU-EAM-02): usage was recorded on overdue
    # and out-of-service instruments; the fitness gate was only a button. A use
    # is the instrument being put to work, so the gate runs on every user path.
    # Superuser code (seeds, sudo service calls) stays trusted.
    def _m45_check_fit_for_use(self):
        if self.env.su:
            return
        for rec in self:
            rec.equipment_id.action_assert_usable()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._m45_check_fit_for_use()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "equipment_id" in vals:
            self._m45_check_fit_for_use()
        return res
