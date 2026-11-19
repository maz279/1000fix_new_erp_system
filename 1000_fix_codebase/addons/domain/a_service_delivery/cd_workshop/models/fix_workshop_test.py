"""M31 sub-module 7 "Testing & Burn-In": the test protocol library and the
recorded test results (FR-WSR-031 / 032 / 035, spec entities fix.test.protocol
and fix.test.result).

Before this, the page's "Test Protocol Result" button filed a generic
evidence attachment (default category: pre-repair photo). No protocol
defined a test or its pass limits, and no measured value could be recorded
(M31 audit, 14 Nov 2026).

A result is judged by the protocol's limits, not typed as "passed": inside
the limits it passes, outside it fails. A check without limits (a visual or
functional check) is judged by the technician's observation.
"""

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_workshop_job import CLOSED_JOB_STATES

LEVELS = [("l1", "L1 - Module Swap"), ("l2", "L2 - Component Level"), ("l3", "L3 - Board Level")]


def _device_types(self):
    return self.env["fix.device.model"]._fields["device_type"].selection


class FixWorkshopTestProtocol(models.Model):
    _name = "fix.workshop.test.protocol"
    _description = "Workshop Test Protocol"
    _inherit = ["mail.thread"]
    _order = "code"
    _rec_name = "name"

    code = fields.Char(string="Protocol Code", required=True, tracking=True)
    name = fields.Char(string="Protocol Name", required=True, tracking=True)
    device_type = fields.Selection(selection=_device_types, string="Device Category", tracking=True)
    repair_level = fields.Selection(LEVELS, string="Repair Level", tracking=True)
    fault_type = fields.Char(
        string="Fault Type",
        help="The fault this protocol verifies, e.g. no power, charging, display.",
    )
    burn_in_minutes = fields.Integer(
        string="Burn-In Duration (minutes)",
        tracking=True,
        help="The protocol duration. Burn-in may be extended, never shortened below it (BRU-WSR-07).",
    )
    pass_criteria = fields.Text(string="Pass Criteria")
    step_ids = fields.One2many("fix.workshop.test.step", "protocol_id", string="Tests", copy=True)
    step_count = fields.Integer(compute="_compute_step_count", string="Tests")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("unique(code)", "A test protocol code must be unique.")

    @api.depends("step_ids")
    def _compute_step_count(self):
        for rec in self:
            rec.step_count = len(rec.step_ids)

    @api.constrains("burn_in_minutes")
    def _check_burn_in(self):
        for rec in self:
            if rec.burn_in_minutes < 0:
                raise ValidationError("A burn-in duration cannot be negative.")

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s · %s" % (rec.code, rec.name) if rec.code else rec.name


class FixWorkshopTestStep(models.Model):
    _name = "fix.workshop.test.step"
    _description = "Workshop Test Protocol Step"
    _order = "protocol_id, sequence, id"

    protocol_id = fields.Many2one(
        "fix.workshop.test.protocol",
        string="Protocol",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    code = fields.Char(string="Test Code")
    name = fields.Char(string="Test", required=True)
    unit = fields.Char(
        string="Unit", help="V, A, °C, %, MΩ … Leave empty for a visual or functional check."
    )
    lower_limit = fields.Float(string="Lower Limit")
    upper_limit = fields.Float(string="Upper Limit")
    has_limits = fields.Boolean(
        string="Measured Against Limits",
        help="Tick when the test passes on a measured value between the limits.",
    )

    @api.constrains("has_limits", "lower_limit", "upper_limit")
    def _check_limits(self):
        for rec in self:
            if rec.has_limits and rec.lower_limit > rec.upper_limit:
                raise ValidationError(
                    "Test %s: the lower limit is above the upper limit." % (rec.name or "")
                )

    @api.depends("protocol_id.code", "code", "name")
    def _compute_display_name(self):
        for rec in self:
            label = "%s %s" % (rec.code, rec.name) if rec.code else rec.name or ""
            rec.display_name = (
                "%s · %s" % (rec.protocol_id.code, label) if rec.protocol_id.code else label
            )


class FixWorkshopTestResult(models.Model):
    _name = "fix.workshop.test.result"
    _description = "Workshop Test Result"
    _inherit = ["mail.thread"]
    _order = "tested_at desc, id desc"

    job_id = fields.Many2one(
        "fix.workshop.job", string="Repair Job", required=True, index=True, ondelete="restrict"
    )
    step_id = fields.Many2one(
        "fix.workshop.test.step", string="Protocol Test", required=True, ondelete="restrict"
    )
    protocol_id = fields.Many2one(
        related="step_id.protocol_id", store=True, string="Protocol", readonly=True
    )
    test_name = fields.Char(related="step_id.name", string="Test", readonly=True)
    unit = fields.Char(related="step_id.unit", string="Unit", readonly=True)
    lower_limit = fields.Float(related="step_id.lower_limit", string="Lower Limit", readonly=True)
    upper_limit = fields.Float(related="step_id.upper_limit", string="Upper Limit", readonly=True)
    has_limits = fields.Boolean(related="step_id.has_limits", readonly=True)
    measured_value = fields.Float(string="Measured Value", tracking=True)
    observed_pass = fields.Boolean(
        string="Check Passed (no limits)",
        tracking=True,
        help="For a visual or functional check without limits: did it pass?",
    )
    passed = fields.Boolean(
        string="Passed",
        compute="_compute_passed",
        store=True,
        help="Inside the protocol's limits, or the observed check for a test without limits.",
    )
    equipment_id = fields.Many2one(
        "fix.equipment",
        string="Instrument Used",
        help="M45 calibration-tracked instrument (FR-WSR-025 / BRU-WSR-09).",
    )
    notes = fields.Text(string="Observations")
    tested_by_id = fields.Many2one(
        "res.users", string="Tested By", readonly=True, default=lambda self: self.env.user
    )
    tested_at = fields.Datetime(string="Tested At", readonly=True, default=fields.Datetime.now)
    company_id = fields.Many2one(related="job_id.company_id", store=True, readonly=True)

    @api.depends(
        "measured_value",
        "observed_pass",
        "step_id.has_limits",
        "step_id.lower_limit",
        "step_id.upper_limit",
    )
    def _compute_passed(self):
        for rec in self:
            step = rec.step_id
            if step.has_limits:
                rec.passed = step.lower_limit <= rec.measured_value <= step.upper_limit
            else:
                rec.passed = rec.observed_pass

    def _m31_check_job_open(self, jobs):
        for job in jobs:
            if job.state in CLOSED_JOB_STATES or job.qc_passed:
                raise UserError(
                    "Job %s has passed QC or is closed: its test results are the record of the "
                    "repair and are not changed." % job.name
                )

    @api.model_create_multi
    def create(self, vals_list):
        Job = self.env["fix.workshop.job"]
        for vals in vals_list:
            # stamped by the system, never typed
            vals.pop("tested_by_id", None)
            vals.pop("tested_at", None)
            self._m31_check_job_open(Job.browse(vals.get("job_id")).exists())
        records = super().create(vals_list)
        for rec in records:
            # A02 ERP audit M31-F16 (BRU-WSR-09): a measurement is evidence
            # only from a fit instrument - the same M45 gate the QC
            # instrument passes (calibrated, in service, issued to the tester
            # or to the job's technician)
            if rec.equipment_id:
                holder = self.env.user.sudo().employee_ids | rec.job_id.sudo().technician_id
                rec.equipment_id.action_assert_usable(holder=holder)
            rec.job_id.message_post(
                body="Test result: %s - %s%s"
                % (
                    rec.step_id.display_name,
                    "%g %s " % (rec.measured_value, rec.unit or "") if rec.has_limits else "",
                    "PASSED" if rec.passed else "FAILED",
                )
            )
        return records

    # A02 ERP audit M31-F15: a recorded result is the measurement. It was
    # editable and deletable until QC, so a failed reading was rewritten or
    # removed before the inspector looked. A result is append-only: a re-test
    # is a new result, and the latest result of each test is what QC judges.
    _MESSAGE_FIELDS = frozenset(
        {"message_follower_ids", "message_ids", "message_main_attachment_id", "activity_ids"}
    )

    def write(self, vals):
        if {"tested_by_id", "tested_at"} & set(vals):
            raise UserError("Who tested and when are stamped by the system.")
        if not self.env.su and set(vals) - self._MESSAGE_FIELDS:
            raise UserError(
                "A recorded test result is the measurement and is not edited: record a re-test "
                "as a new result."
            )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError(
                "A recorded test result is never deleted: record a re-test as a new result."
            )
        return super().unlink()


class FixWorkshopJobTests(models.Model):
    _inherit = "fix.workshop.job"

    test_result_ids = fields.One2many("fix.workshop.test.result", "job_id", string="Test Results")
    test_result_count = fields.Integer(compute="_compute_test_results", string="Tests Recorded")
    test_failed_count = fields.Integer(
        compute="_compute_test_results",
        string="Tests Failed",
        help="Tests whose latest recorded result failed (a passing re-test clears one).",
    )

    def _m31_failed_tests(self):
        """The latest result of each test, where it failed."""
        self.ensure_one()
        latest = {}
        for result in self.sudo().test_result_ids.sorted(
            lambda r: (r.tested_at or fields.Datetime.now(), r.id)
        ):
            latest[result.step_id.id] = result
        return self.env["fix.workshop.test.result"].browse(
            [r.id for r in latest.values() if not r.passed]
        )

    @api.depends("test_result_ids.passed", "test_result_ids.tested_at", "test_result_ids.step_id")
    def _compute_test_results(self):
        for rec in self:
            rec.test_result_count = len(rec.test_result_ids)
            rec.test_failed_count = len(rec._m31_failed_tests())

    def action_pass_qc(self, notes=""):
        """A02 ERP audit M31-F15: QC does not pass a job whose latest
        measured result of any test is a failure (test_failed_count was
        computed and read by nothing)."""
        for rec in self:
            failed = rec._m31_failed_tests()
            if failed:
                raise UserError(
                    "Job %s cannot pass QC: %d test(s) failed on their latest result (%s). "
                    "Rework and re-test, or fail QC."
                    % (rec.name, len(failed), ", ".join(failed.mapped("step_id.display_name")))
                )
        return super().action_pass_qc(notes=notes)
