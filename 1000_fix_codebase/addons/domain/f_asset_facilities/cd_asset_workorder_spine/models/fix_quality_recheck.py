# fix_quality_recheck — A07 P1 wiring (2026-11-04): an M45 impact assessment
# reaches the M01 service orders whose measurements it puts in doubt.
#
# BRU-EAM-03 / ISO 9001 7.1.5.2: when a test instrument is found out of
# tolerance, every result it produced since its last good calibration is
# suspect. M45 lists those uses (fix.calibration.impact.usage_ids) and
# publishes equipment.impact_assessment_raised, but no service order ever
# heard of it: a phone passed QC on a drifting meter went back to its owner
# with nothing on its order. Now each service order behind a listed use gets
# ONE re-check flag per impact (this model) and an activity for the person on
# the order; the Quality Manager's disposition (impact_assessment_closed) is
# recorded on the flag. The order's state is never touched.
from odoo import api, fields, models
from odoo.exceptions import UserError

ROLE_QM = "cd_equipment_register.group_quality_manager"
RECHECK_SYSTEM_FIELDS = {
    "name",
    "order_id",
    "impact_id",
    "job_refs",
    "use_count",
    "state",
    "disposition",
    "disposition_note",
    "decided_on",
    "activity_id",
}
DONE_DISPOSITIONS = ("valid", "retested")


def _impact_dispositions(self):
    return self.env["fix.calibration.impact"]._fields["disposition"].selection


class FixServiceOrderRecheck(models.Model):
    _name = "fix.service.order.recheck"
    _description = "Service Order Quality Re-Check (M45 Impact)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "state, id desc"

    _order_impact_once = models.Constraint(
        "UNIQUE (order_id, impact_id)", "One re-check per service order and impact assessment."
    )

    name = fields.Char(required=True, readonly=True)
    order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    impact_id = fields.Many2one(
        "fix.calibration.impact",
        string="Impact Assessment (M45)",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    equipment_id = fields.Many2one(related="impact_id.equipment_id", string="Instrument")
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    job_refs = fields.Char(string="Suspect Uses", readonly=True)
    use_count = fields.Integer(string="Uses", readonly=True)
    state = fields.Selection(
        [("open", "Re-Check Required"), ("decided", "Disposition Recorded")],
        default="open",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    disposition = fields.Selection(_impact_dispositions, readonly=True)
    disposition_note = fields.Text(readonly=True)
    decided_on = fields.Datetime(readonly=True)
    activity_id = fields.Many2one("mail.activity", readonly=True, ondelete="set null")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | RECHECK_SYSTEM_FIELDS

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("A quality re-check is raised from an M45 impact assessment only.")
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A quality re-check is part of the order's quality record.")
        return super().unlink()

    # ------------------------------------------------------------ resolution
    @api.model
    def _recheck_orders(self, impact, payload):
        """{service order: [use references]} from the impact's own uses (the
        record M45 keeps), plus the event's source_refs; and the references
        that match no service order (reported, never guessed)."""
        SO = self.env["fix.service.order"].sudo()
        Job = self.env["fix.workshop.job"].sudo() if "fix.workshop.job" in self.env else None
        found, unmatched = {}, []

        def add(order, ref):
            found.setdefault(order, [])
            if ref and ref not in found[order]:
                found[order].append(ref)

        def from_source(model, res_id, ref):
            if model == "fix.workshop.job" and Job is not None:
                job = Job.browse(int(res_id)).exists()
                if job and job.order_id:
                    add(job.order_id, ref or job.name)
                    return True
            if model == "fix.service.order":
                order = SO.browse(int(res_id)).exists()
                if order:
                    add(order, ref or order.name)
                    return True
            return False

        for use in impact.sudo().usage_ids:
            ref = use.job_ref
            if use.source_model and from_source(use.source_model, use.source_res_id, ref):
                continue
            names = [n for n in (use.service_order_ref, use.job_ref) if n]
            order = SO.search([("name", "in", names)], limit=1) if names else SO
            if not order and Job is not None and use.job_ref:
                order = Job.search([("name", "=", use.job_ref)], limit=1).order_id
            if order:
                add(order, ref)
            else:
                unmatched.append(ref)
        for src in payload.get("source_refs") or []:
            if isinstance(src, dict) and src.get("model") and src.get("id"):
                from_source(src["model"], src["id"], None)
        return found, unmatched

    @api.model
    def _recheck_assignee(self, order):
        """The person who acts on the order: its technician, else whoever
        raised it, else a Quality Manager. Never the superuser."""
        candidates = order.technician_id.user_id | order.create_uid
        group = self.env.ref(ROLE_QM, raise_if_not_found=False)
        if group:
            candidates |= group.sudo().user_ids.filtered(
                lambda u: order.company_id in u.company_ids
            )
        for user in candidates:
            if user.active and user._is_internal() and not user._is_superuser():
                return user
        return self.env["res.users"]

    # ------------------------------------------------------------ consumers
    @api.model
    def consume_impact_assessment_raised(self, event):
        """equipment.impact_assessment_raised -> each service order behind a
        suspect use: one re-check flag and one activity. Idempotent per
        (order, impact)."""
        impact = (
            self.env["fix.calibration.impact"].sudo().browse(event.get("aggregate_id")).exists()
        )
        if not impact:
            return False
        payload = event.get("payload") or {}
        found, unmatched = self._recheck_orders(impact, payload)
        Recheck = self.sudo()._guarded()
        for order, refs in found.items():
            if Recheck.search_count([("order_id", "=", order.id), ("impact_id", "=", impact.id)]):
                continue
            text = (
                "Quality re-check: test instrument %s was found out of tolerance (impact "
                "assessment %s, suspect from %s to %s%s). Measurements on this order (%s) may "
                "be wrong: re-check them before delivery or warranty submission. The Quality "
                "Manager records the disposition in M45."
                % (
                    impact.equipment_id.code,
                    impact.name,
                    impact.period_from or "first use",
                    impact.period_to,
                    ", NCR %s" % impact.ncr_ref if impact.ncr_ref else "",
                    ", ".join(refs) or order.name,
                )
            )
            line = Recheck.create(
                {
                    "name": "%s / %s" % (order.name, impact.name),
                    "order_id": order.id,
                    "impact_id": impact.id,
                    "job_refs": ", ".join(refs),
                    "use_count": len(refs) or 1,
                }
            )
            user = self._recheck_assignee(order)
            if user:
                activity = order.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary="Quality re-check (%s)" % impact.name,
                    note=text,
                )
                line.write({"activity_id": activity.id})
            order.sudo().message_post(body=text)
        if unmatched:
            note = "No service order found for use(s): %s." % ", ".join(unmatched)
            if note not in "\n".join(impact.message_ids.mapped("body")):
                impact.message_post(body=note)
        return True

    @api.model
    def consume_impact_assessment_closed(self, event):
        """equipment.impact_assessment_closed -> the disposition on each open
        flag of that impact. A 'valid' or 're-tested' disposition completes the
        re-check activity; a recall leaves it open for the order's person."""
        impact = (
            self.env["fix.calibration.impact"].sudo().browse(event.get("aggregate_id")).exists()
        )
        if not impact or impact.state != "closed":
            return False
        labels = dict(impact._fields["disposition"].selection)
        for line in self.sudo().search([("impact_id", "=", impact.id), ("state", "=", "open")]):
            text = "Impact assessment %s closed by %s: %s. %s" % (
                impact.name,
                impact.decided_by_id.name or "-",
                labels.get(impact.disposition, impact.disposition or "-"),
                impact.disposition_note or "",
            )
            line._guarded().write(
                {
                    "state": "decided",
                    "disposition": impact.disposition,
                    "disposition_note": impact.disposition_note,
                    "decided_on": impact.decided_on or fields.Datetime.now(),
                }
            )
            activity = line.activity_id.sudo().exists()
            if activity and impact.disposition in DONE_DISPOSITIONS:
                activity.action_feedback(feedback=text)
            elif activity:
                activity.write({"note": "%s<br/>%s" % (activity.note or "", text)})
            line.order_id.sudo().message_post(body=text)
        return True


class FixServiceOrderQualityRecheck(models.Model):
    _inherit = "fix.service.order"

    quality_recheck_ids = fields.One2many(
        "fix.service.order.recheck", "order_id", string="Quality Re-Checks", readonly=True
    )
    quality_recheck_required = fields.Boolean(
        string="Quality Re-Check Required",
        compute="_compute_quality_recheck",
        store=True,
        index=True,
        help="An M45 impact assessment put a measurement on this order in doubt and its "
        "disposition is not recorded yet.",
    )

    @api.depends("quality_recheck_ids.state")
    def _compute_quality_recheck(self):
        for rec in self:
            rec.quality_recheck_required = any(
                line.state == "open" for line in rec.quality_recheck_ids
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"quality_recheck_required"}
