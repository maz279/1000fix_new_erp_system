# fix_stock_provisional — imported stock at a provisional cost (A06 ERP audit
# M44-17; spec BRU-ITC-01 / AC-08).
#
# An import is received into M15 at its PROVISIONAL landed cost (the goods at
# the commitment rate plus the posted estimate); the final cost arrives later
# from the paid Bills of Entry and the reconciled cost documents. Until then
# M15 did not say so: the bucket's cost looked final. Now:
#   - the receipt that brings the stock in is flagged provisional (who set it,
#     from which source document, since when), and so is every bucket it
#     filled, until the source finalises the landed cost (_fix_clear_provisional);
#   - a daily job escalates a receipt still provisional after N days
#     (cd_inventory.provisional_cost_escalation_days, default 30) once: a to-do
#     for the Inventory Controllers on the source document and the event
#     stock.provisional_cost_overdue.
# Owned by the M43/M44 builder stream; the rest of cd_inventory is untouched.
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

PARAM_ESCALATION_DAYS = "cd_inventory.provisional_cost_escalation_days"
DEFAULT_ESCALATION_DAYS = 30
CONTROLLER_GROUP = "cd_wms_structure.group_inventory_controller"


class FixStockReceiptProvisional(models.Model):
    _inherit = "fix.stock.receipt"

    cost_provisional = fields.Boolean(
        string="Provisional Cost",
        readonly=True,
        copy=False,
        index=True,
        help="Received at a provisional landed cost; the final cost is not applied yet.",
    )
    provisional_since = fields.Date(string="Provisional Since", readonly=True, copy=False)
    provisional_reason = fields.Char(string="Provisional Because", readonly=True, copy=False)
    provisional_escalated_on = fields.Date(
        string="Provisional Cost Escalated On", readonly=True, copy=False
    )
    cost_finalised_on = fields.Date(string="Cost Finalised On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "cost_provisional",
            "provisional_since",
            "provisional_reason",
            "provisional_escalated_on",
            "cost_finalised_on",
        }

    def _fix_mark_provisional(self, reason):
        """Called by the module that received the stock (M44): the receipt
        and the buckets it filled carry a provisional cost."""
        today = fields.Date.context_today(self)
        for rec in self.sudo():
            rec._guarded().write(
                {
                    "cost_provisional": True,
                    "provisional_since": rec.received_on or today,
                    "provisional_reason": reason,
                    "cost_finalised_on": False,
                }
            )
            rec._fix_provisional_buckets()._guarded().write({"cost_provisional": True})

    def _fix_clear_provisional(self):
        """The final landed cost is applied: the receipt is final, and each
        bucket is final once no other provisional receipt still fills it."""
        today = fields.Date.context_today(self)
        for rec in self.sudo().filtered("cost_provisional"):
            rec._guarded().write({"cost_provisional": False, "cost_finalised_on": today})
            for bucket in rec._fix_provisional_buckets():
                others = self.sudo().search_count(
                    [
                        ("id", "!=", rec.id),
                        ("cost_provisional", "=", True),
                        ("location_id", "=", bucket.location_id.id),
                        ("line_ids.part_id", "=", bucket.part_id.id),
                    ]
                )
                if not others:
                    bucket._guarded().write({"cost_provisional": False})

    def _fix_provisional_buckets(self):
        self.ensure_one()
        Onhand = self.env["fix.stock.onhand"].sudo()
        buckets = Onhand.browse()
        for part in self.line_ids.mapped("part_id"):
            buckets |= Onhand.search(
                [("part_id", "=", part.id), ("location_id", "=", self.location_id.id)]
            )
        return buckets

    @api.model
    def _cron_escalate_provisional(self):
        """Daily: a receipt still at a provisional cost after the escalation
        window is escalated once to the Inventory Controllers."""
        raw = self.env["ir.config_parameter"].sudo().get_param(PARAM_ESCALATION_DAYS)
        try:
            days = int(raw) if raw not in (None, False, "") else DEFAULT_ESCALATION_DAYS
        except (TypeError, ValueError):
            days = DEFAULT_ESCALATION_DAYS
        today = fields.Date.context_today(self)
        late = self.sudo().search(
            [
                ("cost_provisional", "=", True),
                ("provisional_since", "<=", today - timedelta(days=days)),
                ("provisional_escalated_on", "=", False),
            ]
        )
        group = self.env.ref(CONTROLLER_GROUP, raise_if_not_found=False)
        controllers = (
            group.sudo().all_user_ids.filtered("active") if group else self.env["res.users"]
        )
        for rec in late:
            note = (
                "Receipt %s (%s) has carried a provisional landed cost since %s (%d days): "
                "finalise the landed cost so the stock is valued at its final cost."
                % (
                    rec.name,
                    rec.source_ref or rec.provisional_reason or "-",
                    rec.provisional_since,
                    days,
                )
            )
            source = (
                self.env[rec.source_model].sudo().browse(rec.source_res_id).exists()
                if rec.source_model in self.env and rec.source_res_id
                else None
            )
            users = controllers or rec.create_uid
            if source is not None and hasattr(source, "activity_schedule"):
                for user in users:
                    source.activity_schedule(
                        "mail.mail_activity_data_todo",
                        summary="Provisional landed cost overdue",
                        note=note,
                        user_id=user.id,
                    )
            if source is not None and hasattr(source, "message_post"):
                source.message_post(body=note)
            try:
                from libs.py.fix_events import publish

                publish(
                    self.env,
                    "stock.provisional_cost_overdue",
                    "fix.stock.receipt",
                    rec.id,
                    {"receipt": rec.name, "since": str(rec.provisional_since), "days": days},
                )
            except Exception:  # an outbox failure never stops the sweep
                _logger.exception("provisional cost event failed for receipt %s", rec.name)
            rec._guarded().write({"provisional_escalated_on": today})
        return len(late)


class FixStockOnhandProvisional(models.Model):
    _inherit = "fix.stock.onhand"

    cost_provisional = fields.Boolean(
        string="Provisional Cost",
        readonly=True,
        copy=False,
        index=True,
        help="Holds imported stock whose landed cost is not final yet (M44-17).",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"cost_provisional"}
