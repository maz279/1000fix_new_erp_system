# fix_m45_qc_gate — A07 ERP audit (2026-11-20) M45-13, owner decision D7(c).
#
# cd_workshop.qc_requires_instrument is ON on fix_real while the M45 register
# holds no instrument, so the first real workshop job could never pass QC. The
# owner kept the switch ON and narrowed it:
#   - it applies only to jobs whose QC procedure is a MEASUREMENT: a test
#     protocol of the job's device category (or one the job was tested under)
#     with a measured step (limits and a unit), or one a Quality Manager marked
#     as needing a measuring instrument;
#   - while no qualifying instrument exists (a measurement-critical item of the
#     company, in calibration and in service), a Quality Manager may waive the
#     instrument for one job, with a reason recorded on the job.
# The gate itself stays in cd_workshop (_run_qc_inspection); this file only
# narrows _m31_qc_requires_instrument. cd_workshop depends on M45, not the other
# way round, so the override lives in the spine, which loads after both.
from odoo import api, fields, models
from odoo.exceptions import UserError

ROLE_QM = "cd_equipment_register.group_quality_manager"
WAIVER_FIELDS = {
    "qc_instrument_waiver_reason",
    "qc_instrument_waiver_by_id",
    "qc_instrument_waiver_at",
}


class FixWorkshopTestProtocolInstrument(models.Model):
    _inherit = "fix.workshop.test.protocol"

    requires_measuring_instrument = fields.Boolean(
        string="Needs a Measuring Instrument",
        compute="_compute_requires_measuring_instrument",
        store=True,
        readonly=False,
        help="QC under this protocol is a measurement: the inspector names a calibrated "
        "test instrument (BRU-EAM-15). Ticked when a step has limits; a Quality Manager may "
        "tick it for a protocol of visual checks made with an instrument.",
    )

    @api.depends("step_ids.has_limits")
    def _compute_requires_measuring_instrument(self):
        for rec in self:
            rec.requires_measuring_instrument = any(rec.step_ids.mapped("has_limits"))


class FixWorkshopJobM45Gate(models.Model):
    _inherit = "fix.workshop.job"

    qc_instrument_waiver_reason = fields.Text(
        string="QC Instrument Waiver",
        readonly=True,
        copy=False,
        help="Why this job's QC passed without a calibrated instrument (no qualifying "
        "instrument was registered). Recorded by a Quality Manager.",
    )
    qc_instrument_waiver_by_id = fields.Many2one(
        "res.users", string="Waived By", readonly=True, copy=False
    )
    qc_instrument_waiver_at = fields.Datetime(string="Waived On", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | WAIVER_FIELDS

    # ---- which QC needs an instrument -------------------------------------
    def _m45_qc_protocols(self):
        """The QC procedure of the job: the protocols it was tested under, and
        the active protocols of its device category."""
        self.ensure_one()
        Protocol = self.env["fix.workshop.test.protocol"].sudo()
        protocols = Protocol.browse()
        if "test_result_ids" in self._fields:
            protocols |= self.sudo().test_result_ids.mapped("protocol_id")
        job = self.sudo()
        device = job.device_id or job.order_id.device_id
        device_type = device.device_type if device else False
        if device_type:
            protocols |= Protocol.search([("device_type", "=", device_type)])
        return protocols

    def _m45_qc_needs_instrument(self) -> bool:
        self.ensure_one()
        return any(self._m45_qc_protocols().mapped("requires_measuring_instrument"))

    def _m45_qualifying_instruments(self):
        """Measurement-critical instruments of the job's company (and OU, when
        both carry one) that are in calibration and in service."""
        self.ensure_one()
        domain = [
            ("company_id", "=", self.company_id.id or self.env.company.id),
            ("measurement_critical", "=", True),
            ("operational_status", "in", ("available", "issued")),
        ]
        items = self.env["fix.equipment"].sudo().search(domain)
        if self.operating_unit_id:
            items = items.filtered(
                lambda e: not e.operating_unit_id or e.operating_unit_id == self.operating_unit_id
            )
        return items.filtered(lambda e: not e._m45_calibration_problem())

    def _m31_qc_requires_instrument(self) -> bool:
        if not super()._m31_qc_requires_instrument():
            return False
        if len(self) != 1:
            return True
        if self.qc_instrument_waiver_reason:
            return False
        return self._m45_qc_needs_instrument()

    def action_waive_qc_instrument(self, reason=None):
        """D7(c): a Quality Manager lets this job pass QC without an instrument
        while no qualifying instrument exists. The reason is kept on the job.
        Not the repairing technician, and never once an instrument exists."""
        if not self.env.su and not self.env.user.has_group(ROLE_QM):
            raise UserError("Waiving the QC instrument needs the Quality Manager role.")
        text = reason.strip() if isinstance(reason, str) else ""
        if not text:
            raise UserError("State why QC passes without a measuring instrument.")
        # the Quality Manager need not hold a workshop role: after the role
        # check the job is read and stamped as the system, on the QM's name
        actor = self.env.user
        for rec in self.sudo():
            if rec.qc_passed or rec.state in ("ready", "delivered", "closed", "cancelled"):
                raise UserError("%s has already been through QC." % rec.name)
            if rec.qc_instrument_waiver_reason:
                raise UserError("%s already has an instrument waiver." % rec.name)
            if not rec._m45_qc_needs_instrument():
                raise UserError(
                    "%s's QC procedure needs no measuring instrument: there is nothing to "
                    "waive." % rec.name
                )
            available = rec._m45_qualifying_instruments()
            if available:
                raise UserError(
                    "A calibrated instrument is registered (%s): name it on the QC instead "
                    "of waiving it." % ", ".join(available[:3].mapped("code"))
                )
            if not self.env.su and rec.technician_id.user_id == actor:
                raise UserError(
                    "Segregation of duties: you repaired %s, so another Quality Manager "
                    "waives its QC instrument." % rec.name
                )
            rec._guarded().write(
                {
                    "qc_instrument_waiver_reason": text,
                    "qc_instrument_waiver_by_id": actor.id,
                    "qc_instrument_waiver_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="QC instrument waived by %s (no qualifying calibrated instrument "
                "registered): %s" % (actor.name, text)
            )
        return True
