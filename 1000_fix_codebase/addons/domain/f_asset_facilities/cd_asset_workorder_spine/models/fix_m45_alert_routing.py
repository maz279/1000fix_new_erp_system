# fix_m45_alert_routing — A07 ERP audit (2026-11-20) M45-11 / M45-23.
#
# The asset alert table routes each event to ONE role. Two M45 ladders need
# more than that:
#   - custody overdue (AUT-EAM-08): the holder is told first, the branch
#     manager at +3 days and the Quality Manager at +7. Every level went to the
#     Equipment Custodian group.
#   - calibration due (AUT-EAM-02): the Quality Manager from 15 days before the
#     due date, the Operations Director from 7. calibration_due only raised a
#     work order; nobody was escalated to.
# Each level is its own alert row, addressed to the person or role of that
# level, and acknowledged by them.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_asset_alert import BRANCH_LEAD, CUSTODIAN, OPS_DIRECTOR, QUALITY

CUSTODY_LEVELS = {
    1: (CUSTODIAN, "Issued equipment is overdue: the holder must return it"),
    2: (BRANCH_LEAD, "Issued equipment is 3+ days overdue: branch manager escalation"),
    3: (QUALITY, "Issued equipment is 7+ days overdue: Quality Manager escalation"),
}
CALIBRATION_ESCALATION = {
    "quality_manager": (QUALITY, "Calibration due within 15 days"),
    "ops_director": (OPS_DIRECTOR, "Calibration due within 7 days: Operations Director"),
}


class FixAssetAlertM45(models.Model):
    _inherit = "fix.asset.alert"

    role_group_xmlid = fields.Char(string="Role (technical)", readonly=True)
    addressee_ids = fields.Many2many(
        "res.users",
        "fix_asset_alert_addressee_rel",
        "alert_id",
        "user_id",
        string="Addressed To",
        readonly=True,
        help="The people this level of the ladder is addressed to by name (the holder, "
        "the branch manager).",
    )

    @api.model
    def _m45_raise(self, event, group_xmlid, text, users=None):
        """One open alert per record, event and ladder level (its role)."""
        Alert = self.sudo()
        res_model = event.get("aggregate") or False
        res_id = event.get("aggregate_id") or 0
        now = fields.Datetime.now()
        existing = Alert.search(
            [
                ("event_type", "=", event["event_type"]),
                ("res_model", "=", res_model),
                ("res_id", "=", res_id),
                ("role_group_xmlid", "=", group_xmlid),
                ("state", "=", "open"),
            ],
            limit=1,
        )
        if existing:
            existing.write({"raise_count": existing.raise_count + 1, "last_raised_on": now})
            return existing
        record = False
        if res_model in self.env and res_id:
            record = self.env[res_model].sudo().browse(res_id).exists()
        label = record.display_name if record else "%s #%s" % (res_model or "", res_id)
        company = (
            event.get("company_id")
            or (record and "company_id" in record._fields and record.company_id.id)
            or self.env.company.id
        )
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        named = (users or self.env["res.users"]).filtered(lambda u: u.active and not u.share)
        holders = named
        if not holders and group:
            holders = group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
        alert = Alert.create(
            {
                "name": "%s: %s" % (text, label),
                "module": "M45",
                "event_type": event["event_type"],
                "res_model": res_model,
                "res_id": res_id,
                "record_label": label,
                "role_group": group.display_name if group else group_xmlid,
                "role_group_xmlid": group_xmlid,
                "addressee_ids": [(6, 0, named.ids)],
                "no_holder": not holders,
                "last_raised_on": now,
                "company_id": company,
            }
        )
        todo = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if todo:
            for user in holders:
                alert.activity_schedule(
                    activity_type_id=todo.id, summary=alert.name[:200], user_id=user.id
                )
        return alert

    @api.model
    def consume_asset_alert(self, event):
        if event.get("event_type") != "equipment.custody_overdue":
            return super().consume_asset_alert(event)
        payload = event.get("payload") or {}
        try:
            level = int(payload.get("escalation_level") or 1)
        except (TypeError, ValueError):
            level = 1
        group_xmlid, text = CUSTODY_LEVELS.get(min(max(level, 1), 3))
        Users = self.env["res.users"].sudo()
        users = Users.browse()
        if level <= 1 and payload.get("holder_user_id"):
            users = Users.browse(int(payload["holder_user_id"])).exists()
        elif level == 2 and payload.get("branch_manager_id"):
            users = Users.browse(int(payload["branch_manager_id"])).exists()
        self._m45_raise(event, group_xmlid, text, users)
        return True

    def action_acknowledge(self):
        """A ladder alert is acknowledged by the person or role it is addressed to."""
        laddered = self.sudo().filtered("role_group_xmlid")
        for rec in laddered:
            if rec.state != "open":
                raise UserError("%s is already acknowledged." % rec.name)
            user = self.env.user
            if not (
                self.env.su or user in rec.addressee_ids or user.has_group(rec.role_group_xmlid)
            ):
                raise UserError("Acknowledging this alert needs the %s role." % rec.role_group)
            rec.write(
                {
                    "state": "acknowledged",
                    "acknowledged_by_id": user.id,
                    "acknowledged_on": fields.Datetime.now(),
                }
            )
            rec.activity_ids.action_feedback(feedback="Acknowledged")
        rest = self - self.browse(laddered.ids)
        if rest:
            return super(FixAssetAlertM45, rest).action_acknowledge()
        return True


class FixMaintenanceDemandM45Escalation(models.Model):
    _inherit = "fix.maintenance.demand"

    @api.model
    def consume_equipment_calibration_due(self, event):
        """The work order as before, plus the AUT-EAM-02 escalation alert."""
        result = super().consume_equipment_calibration_due(event)
        payload = event.get("payload") or {}
        route = CALIBRATION_ESCALATION.get(payload.get("escalate_to"))
        if route:
            self.env["fix.asset.alert"]._m45_raise(event, route[0], route[1])
        return result
