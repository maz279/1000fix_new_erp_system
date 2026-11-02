# fix_data_case_ext — M06 iteration 2: the lab engines the registry's 12
# screens describe (specialisms, attempt tracking, sealed media custody,
# cleanroom slots, free evaluations, firm quotations, backup plans & restore
# tests) plus the button-friendly case wrappers the back-office form needs.
#
# FILE NAME IS LOAD-BEARING: sorts after fix_data_case.py, so the base
# models exist before these extensions load.
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

SPECIALISMS = [
    ("logical_recovery", "Logical Recovery"),
    ("hardware_repair", "Hardware / PCB Repair"),
    ("raid_reconstruction", "RAID Reconstruction"),
    ("flash_chipoff", "Flash Chip-Off"),
    ("phone_extraction", "Phone Extraction"),
    ("forensic_imaging", "Forensic Imaging"),
    ("firmware_repair", "Firmware Repair"),
]


class FixDataRecoveryCaseExt(models.Model):
    """Case polish: the 7 specialisms the registry names, the intake clock
    for cycle-time reporting, and no-arg wrappers so the back-office form's
    buttons can run the journey (the parameterised actions stay canonical
    for the workspace prompts)."""

    _inherit = "fix.data.recovery.case"

    specialism = fields.Selection(
        SPECIALISMS,
        string="Specialism",
        help="The lab discipline this case is worked under (one of the 7)",
    )
    received_at = fields.Datetime(
        string="Media Received At",
        default=fields.Datetime.now,
        help="Clock start for the case cycle-time report",
    )
    attempt_ids = fields.One2many("fix.data.recovery.attempt", "case_id", string="Attempts")
    attempt_count = fields.Integer(compute="_compute_attempt_count", string="Attempts")
    media_unit_ids = fields.One2many("fix.data.media.unit", "case_id", string="Sealed Media")
    evaluation_ids = fields.One2many("fix.data.evaluation", "case_id", string="Evaluations")
    quote_ids = fields.One2many("fix.data.quote", "case_id", string="Quotations")

    @api.depends("attempt_ids")
    def _compute_attempt_count(self):
        for rec in self:
            rec.attempt_count = len(rec.attempt_ids)

    # ---- button-friendly wrappers (form buttons pass no arguments) ----
    def action_take_custody_me(self):
        self.action_take_custody(self.env.user.name)

    def action_transfer_me(self):
        self.action_log_custody_transfer(self.env.user.name, role="Technician", location="Z4 Lab")

    def action_handover_me(self):
        self.action_handover(self.env.user.name)


class FixDataRecoveryAttempt(models.Model):
    """Attempt tracking: each recovery technique tried on the media, with
    its outcome — the lab's methodology log (freg 4/5)."""

    _name = "fix.data.recovery.attempt"
    _description = "Data Recovery Attempt"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "case_id, sequence, id"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, ondelete="cascade", index=True
    )
    sequence = fields.Integer(default=10)
    method = fields.Selection(
        [
            ("software_scan", "Software Scan"),
            ("firmware_repair", "Firmware Repair"),
            ("head_swap", "Head Assembly Swap"),
            ("pcb_transplant", "PCB Transplant"),
            ("chip_off", "Chip-Off"),
            ("raid_rebuild", "RAID Rebuild"),
            ("donor_parts", "Donor Parts"),
        ],
        required=True,
    )
    specialism = fields.Selection(
        SPECIALISMS, related="case_id.specialism", store=True, readonly=True
    )
    started_at = fields.Datetime(default=fields.Datetime.now, required=True)
    finished_at = fields.Datetime(readonly=True)
    outcome = fields.Selection(
        [
            ("in_progress", "In Progress"),
            ("success", "Full Recovery"),
            ("partial", "Partial Recovery"),
            ("failed", "Failed"),
            ("media_damaged", "Media Damaged"),
        ],
        default="in_progress",
        required=True,
        tracking=True,
    )
    notes = fields.Char()
    cleanroom_slot_id = fields.Many2one(
        "fix.data.cleanroom.slot",
        string="Cleanroom Slot",
        help="Required for invasive interventions (head_swap, chip_off, donor_parts)",
    )
    donor_part_used = fields.Char(string="Donor Part / Head Serial")
    bad_sectors_encountered = fields.Integer(string="Bad Sectors Encountered", default=0)
    imaged_pct = fields.Float(string="Imaged Sectors (%)", default=0.0)
    attempt_report_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attempt Log / Clone Map Evidence",
    )

    @api.constrains("method", "cleanroom_slot_id")
    def _check_cleanroom_interlock(self):
        for attempt in self:
            if (
                attempt.method in ("head_swap", "chip_off", "donor_parts")
                and attempt.cleanroom_slot_id
                and not attempt.cleanroom_slot_id.interlock_passed
            ):
                raise UserError(
                    "FLAW-06.2 Cleanroom Environmental Interlock: Invasive recovery method '%s' "
                    "cannot proceed because Cleanroom Slot #%s failed ISO Class 5 particle/airflow limits."
                    % (attempt.method, attempt.cleanroom_slot_id.id)
                )

    @api.depends("case_id", "sequence")
    def _compute_display_name(self) -> None:
        for attempt in self:
            attempt.display_name = "Attempt #%s — %s" % (
                attempt.id,
                dict(type(self).method.selection).get(attempt.method, attempt.method or "…"),
            )

    def action_finish(self, outcome=None, notes=""):
        """Close an in-progress attempt with its outcome. ``outcome`` may be
        omitted when the field already carries the verdict (the form path)."""
        for attempt in self:
            if attempt.outcome != "in_progress":
                raise UserError("Attempt %s already finished (%s)" % (attempt.id, attempt.outcome))
            final = outcome or attempt.outcome
            if final == "in_progress":
                raise UserError(
                    "Attempt %s needs an outcome (full/partial/failed/media damaged)" % attempt.id
                )
            attempt.write(
                {
                    "outcome": final,
                    "finished_at": fields.Datetime.now(),
                    "notes": notes or attempt.notes,
                }
            )
            publish(
                self.env,
                "data_case.attempt_finished",
                "fix.data.recovery.attempt",
                attempt.id,
                {"case": attempt.case_id.name, "outcome": final},
            )


class FixDataMediaUnit(models.Model):
    """Sealed media custody: one row per physical sealed unit (bag) in a
    case. Location moves append to the case's canonical chain-of-custody
    log and publish events — the audit trail stays single-source."""

    _name = "fix.data.media.unit"
    _description = "Sealed Media Unit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "case_id desc, id desc"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, ondelete="cascade", index=True
    )
    seal_number = fields.Char(required=True, string="Seal / Bag Number")
    media_label = fields.Char(string="Media Label", help="e.g. WDC WD10EZEX 1TB")
    media_type = fields.Selection(
        related="case_id.media_type", store=True, readonly=True, string="Media Type"
    )
    location = fields.Selection(
        [
            ("reception", "Reception"),
            ("z4_lab", "Z4 Lab"),
            ("cleanroom", "Cleanroom"),
            ("vault", "Evidence Vault"),
            ("returned_to_customer", "Returned to Customer"),
            ("destroyed", "Destroyed"),
        ],
        default="reception",
        required=True,
        tracking=True,
    )
    seal_state = fields.Selection(
        [
            ("sealed", "Sealed"),
            ("opened_in_lab", "Opened in Lab"),
            ("broken_on_receipt", "Broken on Receipt"),
        ],
        default="sealed",
        required=True,
    )
    holder = fields.Char(string="Current Holder", help="Who physically holds the unit now")
    witness_user_id = fields.Many2one(
        "res.users",
        string="Dual-Custody Witness",
        tracking=True,
        help="FLAW-06.1: Second witness user who verified unsealing of evidence bag in lab",
    )
    witness_verified_at = fields.Datetime(
        string="Witness Verified At",
        readonly=True,
    )
    write_blocker_serial = fields.Char(
        string="Hardware Write-Blocker S/N",
        help="Tableau / Atola hardware write-blocker serial number used prior to imaging",
    )
    source_sha256_hash = fields.Char(
        string="Source Media SHA-256",
    )
    evidence_photo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Evidence Bag / Seal Photo",
    )

    _seal_unique = models.Constraint(
        "UNIQUE (seal_number)", "This seal / bag number is already registered"
    )

    def _log(self, text):
        """Append to the case's append-only custody chain (single source)."""
        stamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for unit in self:
            unit.case_id.custody_chain = (
                unit.case_id.custody_chain or ""
            ) + "\n%s: [Media %s] %s" % (stamp, unit.seal_number, text)

    def action_transfer(self, location, handler=""):
        """Move the unit to a new physical location; the case's chain of
        custody records it."""
        for unit in self:
            if not location or location not in dict(type(self).location.selection):
                raise UserError("Pick a valid location for media unit %s" % unit.seal_number)
            if location == "destroyed":
                raise UserError(
                    "Destruction is certified by fix.data.wipe.certificate — "
                    "not by a custody move"
                )
            who = handler or self.env.user.name
            unit._log("moved to %s by %s" % (dict(type(self).location.selection)[location], who))
            unit.write({"location": location, "holder": who})
            publish(
                self.env,
                "data_case.media_transferred",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number, "location": location},
            )

    def action_break_seal(self, handler="", witness_user_id=None):
        for unit in self:
            if unit.seal_state != "sealed":
                raise UserError("Seal %s is already %s" % (unit.seal_number, unit.seal_state))
            witness_id = witness_user_id or (
                unit.witness_user_id.id if unit.witness_user_id else None
            )
            if witness_id and witness_id == self.env.uid:
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: Witness user must be a different person from the unsealing technician."
                )
            who = handler or self.env.user.name
            witness_suffix = ""
            vals = {"seal_state": "opened_in_lab", "holder": who}
            if witness_id:
                witness_user = self.env["res.users"].browse(witness_id)
                witness_suffix = " (witnessed by %s)" % (witness_user.name or witness_id)
                vals["witness_user_id"] = witness_id
                vals["witness_verified_at"] = fields.Datetime.now()
            unit._log("seal broken by %s%s" % (who, witness_suffix))
            unit.write(vals)
            publish(
                self.env,
                "data_case.media_seal_broken",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number, "witness_user_id": witness_id or False},
            )

    def action_break_seal_with_witness(self, witness_user_id=None, handler=""):
        """Strict FLAW-06.1 entry point requiring an explicit distinct witness."""
        for unit in self:
            wid = witness_user_id or (unit.witness_user_id.id if unit.witness_user_id else None)
            if not wid:
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: Breaking evidence seal %s requires a second witness sign-off."
                    % unit.seal_number
                )
            unit.action_break_seal(handler=handler, witness_user_id=wid)
        return True

    def action_return(self, handler=""):
        for unit in self:
            if unit.location == "destroyed":
                raise UserError("Unit %s is destroyed" % unit.seal_number)
            who = handler or self.env.user.name
            unit._log("returned to customer by %s" % who)
            unit.write({"location": "returned_to_customer", "holder": who})
            publish(
                self.env,
                "data_case.media_returned",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number},
            )


class FixDataCleanroomSlot(models.Model):
    """Cleanroom scheduling: bookable ISO-class bench slots for the
    contamination-critical interventions (head swaps, platter transfers)."""

    _name = "fix.data.cleanroom.slot"
    _description = "Cleanroom Slot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_at desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    case_id = fields.Many2one("fix.data.recovery.case", string="Case", ondelete="set null")
    technician_id = fields.Many2one("hr.employee", string="Technician")
    purpose = fields.Selection(
        [
            ("head_swap", "Head Assembly Swap"),
            ("pcb_transplant", "PCB Transplant"),
            ("chip_off", "Chip-Off"),
            ("platter_transfer", "Platter Transfer"),
            ("forensic_imaging", "Forensic Imaging"),
            ("inspection", "Inspection"),
        ],
        required=True,
    )
    iso_class = fields.Selection(
        [("iso_5", "ISO Class 5 (100)"), ("iso_7", "ISO Class 7 (10,000)")],
        default="iso_5",
        required=True,
    )
    start_at = fields.Datetime(required=True)
    end_at = fields.Datetime(required=True)
    state = fields.Selection(
        [("planned", "Planned"), ("used", "Used"), ("cancelled", "Cancelled")],
        default="planned",
        required=True,
        tracking=True,
    )
    particle_count_per_ft3 = fields.Integer(
        string="Particle Count (≥0.5µm / ft³)",
        default=45,
        tracking=True,
        help="FLAW-06.2: ISO Class 5 (Class 100) requires <= 100 particles/ft³",
    )
    laminar_airflow_mps = fields.Float(
        string="Laminar Airflow Velocity (m/s)",
        default=0.45,
        help="ISO 14644-1 target: 0.45 m/s ±20% (0.36 - 0.54 m/s)",
    )
    temperature_c = fields.Float(string="Cleanroom Temp (°C)", default=21.0)
    humidity_pct = fields.Float(string="Relative Humidity (%)", default=42.0)
    interlock_passed = fields.Boolean(
        string="Environmental Interlock Passed",
        compute="_compute_interlock_passed",
        store=True,
    )
    notes = fields.Text(string="Environmental Telemetry Notes")
    telemetry_log_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Particle Counter Log Attachment",
    )

    @api.depends("iso_class", "particle_count_per_ft3", "laminar_airflow_mps")
    def _compute_interlock_passed(self):
        for slot in self:
            max_particles = 100 if slot.iso_class == "iso_5" else 10000
            particles_ok = (slot.particle_count_per_ft3 or 0) <= max_particles
            airflow_ok = 0.30 <= (slot.laminar_airflow_mps or 0.45) <= 0.60
            slot.interlock_passed = bool(particles_ok and airflow_ok)

    @api.constrains("start_at", "end_at")
    def _check_window(self):
        for slot in self:
            if slot.end_at <= slot.start_at:
                raise UserError("Cleanroom slot must end after it starts")

    def action_use(self):
        for slot in self:
            if slot.state != "planned":
                raise UserError("Slot is not planned")
            if not slot.interlock_passed:
                raise UserError(
                    "FLAW-06.2 Cleanroom Interlock Gate: Cannot use Cleanroom Slot #%s — "
                    "particle count (%s/ft³) or laminar airflow (%s m/s) violates %s environmental limits."
                    % (
                        slot.id,
                        slot.particle_count_per_ft3,
                        slot.laminar_airflow_mps,
                        slot.iso_class,
                    )
                )
            slot.state = "used"
            publish(
                self.env,
                "data_case.cleanroom_slot_used",
                "fix.data.cleanroom.slot",
                slot.id,
                {"purpose": slot.purpose, "particle_count": slot.particle_count_per_ft3},
            )

    def action_cancel(self):
        for slot in self:
            if slot.state != "planned":
                raise UserError("Only a planned slot can be cancelled")
            slot.state = "cancelled"


class FixDataEvaluation(models.Model):
    """The free evaluation: what came in, what is recoverable, at what
    confidence — and how long that answer took (the turnaround KPI)."""

    _name = "fix.data.evaluation"
    _description = "Data Recovery Evaluation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "received_at desc"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, ondelete="cascade", index=True
    )
    received_at = fields.Datetime(default=fields.Datetime.now, required=True)
    evaluated_at = fields.Datetime(readonly=True)
    findings = fields.Text()
    recoverability_pct = fields.Integer(
        string="Recoverability %", help="The lab's confidence estimate 0-100"
    )
    verdict = fields.Selection(
        [
            ("recoverable", "Recoverable"),
            ("partial", "Partially Recoverable"),
            ("unrecoverable", "Unrecoverable"),
            ("no_media_damage", "No Media Damage (logical only)"),
        ]
    )
    recommended_specialism = fields.Selection(SPECIALISMS, string="Recommended Specialism")
    donor_required = fields.Boolean(string="Donor Part Required", default=False)
    donor_estimated_cost_bdt = fields.Float(string="Donor Part Est. Cost (BDT)", default=0.0)
    evaluation_report_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Evaluation Diagnostic Report",
    )
    eval_hours = fields.Float(
        compute="_compute_eval_hours",
        store=True,
        string="Turnaround (h)",
        help="Hours from media received to verdict — the Eval Turnaround KPI",
    )

    @api.depends("received_at", "evaluated_at")
    def _compute_eval_hours(self):
        for ev in self:
            ev.eval_hours = (
                round((ev.evaluated_at - ev.received_at).total_seconds() / 3600.0, 1)
                if ev.evaluated_at and ev.received_at
                else 0.0
            )

    def action_complete(self, notes=""):
        """Stamp the verdict from the already-filled fields (the form path
        sets verdict/recoverability/findings first; fail closed without a
        verdict)."""
        for ev in self:
            if ev.evaluated_at:
                raise UserError("Evaluation already completed")
            if not ev.verdict:
                raise UserError("Set a verdict before completing the evaluation")
            ev.write(
                {
                    "evaluated_at": fields.Datetime.now(),
                    "findings": (notes or "") or (ev.findings or ""),
                }
            )
            if ev.recommended_specialism and ev.case_id.specialism != ev.recommended_specialism:
                ev.case_id.specialism = ev.recommended_specialism
            publish(
                self.env,
                "data_case.evaluated",
                "fix.data.evaluation",
                ev.id,
                {"case": ev.case_id.name, "verdict": ev.verdict},
            )


class FixDataQuote(models.Model):
    """The firm quotation after the evaluation (no-data-no-fee economics:
    only an accepted quote becomes revenue)."""

    _name = "fix.data.quote"
    _description = "Data Recovery Quotation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, ondelete="cascade", index=True
    )
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id")
    donor_fee_bdt = fields.Float(
        string="Non-Refundable Donor Fee (BDT)",
        default=0.0,
        help="Upfront donor hardware procurement fee (excluded from No-Data-No-Fee waiver)",
    )
    no_data_no_fee_applies = fields.Boolean(
        string="No-Data-No-Fee Guarantee",
        default=True,
    )
    signed_quote_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Quotation / Authorization PDF",
    )
    description = fields.Char(string="Scope")
    valid_until = fields.Date()
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("declined", "Declined")],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.data.quote") or "DRQ/New"
        return super().create(vals_list)

    def action_send(self):
        for quote in self:
            if quote.state != "draft":
                raise UserError("Quote %s is not draft" % quote.name)
            quote.state = "sent"
            publish(
                self.env,
                "data_case.quote_sent",
                "fix.data.quote",
                quote.id,
                {"case": quote.case_id.name, "amount": quote.amount},
            )

    def action_accept(self):
        for quote in self:
            if quote.state != "sent":
                raise UserError("Quote %s must be sent before acceptance" % quote.name)
            if quote.valid_until and quote.valid_until < date.today():
                raise UserError("Quote %s expired on %s" % (quote.name, quote.valid_until))
            quote.state = "accepted"
            publish(
                self.env,
                "data_case.quote_accepted",
                "fix.data.quote",
                quote.id,
                {"case": quote.case_id.name, "amount": quote.amount},
            )

    def action_decline(self):
        for quote in self:
            if quote.state not in ("draft", "sent"):
                raise UserError("Quote %s cannot be declined from '%s'" % (quote.name, quote.state))
            quote.state = "declined"


class FixDataBackupPlan(models.Model):
    """The customer's backup plan (3-2-1 & friends) with RPO/RTO targets and
    a restore-test register — compliance = a passing recent test."""

    _name = "fix.data.backup.plan"
    _description = "Backup Plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    plan_type = fields.Selection(
        [
            ("rule_321", "3-2-1 Rule"),
            ("disk_image", "Disk Image"),
            ("cloud_hybrid", "Cloud Hybrid"),
            ("nas_local", "Local NAS"),
            ("offline_vault", "Offline Vault"),
        ],
        default="rule_321",
        required=True,
    )
    rpo_hours = fields.Integer(string="RPO (h)", help="Maximum acceptable data-loss window")
    rto_hours = fields.Integer(string="RTO (h)", help="Maximum acceptable restore time")
    encryption_standard = fields.Selection(
        [
            ("aes_256_gcm", "AES-256-GCM"),
            ("aes_256_xts", "AES-256-XTS (BitLocker / LUKS)"),
            ("chacha20", "ChaCha20-Poly1305"),
        ],
        string="Backup Encryption Standard",
        default="aes_256_gcm",
    )
    immutable_worm_enabled = fields.Boolean(
        string="Immutable WORM / Object Lock Enabled",
        default=True,
    )
    offsite_vault_location = fields.Char(string="Offsite / Cloud Vault Location")
    dr_runbook_attachment_id = fields.Many2one(
        "ir.attachment",
        string="DR Runbook / Restore Verification Log",
    )
    test_frequency_days = fields.Integer(default=90, string="Test Frequency (days)")
    next_test_due = fields.Date(readonly=True)
    test_ids = fields.One2many("fix.data.backup.test", "plan_id", string="Restore Tests")
    # non-stored on purpose: a new child row alone does not re-trigger the
    # stored compute (the second next_test_due write is a no-op), so these
    # recompute on every read — always in step with the test register.
    last_test_date = fields.Datetime(compute="_compute_last_test", string="Last Restore Test")
    last_test_result = fields.Selection(
        [("passed", "Passed"), ("partial", "Partial"), ("failed", "Failed")],
        compute="_compute_last_test",
        string="Last Test Result",
    )
    compliant = fields.Boolean(
        compute="_compute_last_test",
        string="Restore-Test Compliant",
        help="True when the latest restore test passed and the next one is not overdue",
    )

    @api.depends("test_ids", "next_test_due")
    def _compute_last_test(self):
        for plan in self:
            # id as tiebreaker: two tests in the same second still order
            tests = plan.test_ids.sorted(
                key=lambda t: (t.tested_at or fields.Datetime.now(), t.id), reverse=True
            )
            last = tests[:1]
            plan.last_test_date = last.tested_at if last else False
            plan.last_test_result = last.result if last else False
            plan.compliant = bool(
                last
                and last.result == "passed"
                and (not plan.next_test_due or plan.next_test_due >= date.today())
            )

    def action_log_test(self, result="passed", restored_gb=0.0, notes=""):
        """Record a restore test; the next due date rolls forward by the
        plan's test frequency. Fail closed on an unknown result."""
        if result not in ("passed", "partial", "failed"):
            raise UserError("A restore test result is one of: passed, partial, failed")
        for plan in self:
            self.env["fix.data.backup.test"].create(
                {
                    "plan_id": plan.id,
                    "result": result,
                    "restored_gb": float(restored_gb or 0.0),
                    "notes": notes or False,
                }
            )
            plan.next_test_due = date.today() + timedelta(days=plan.test_frequency_days or 90)
            publish(
                self.env,
                "data_case.backup_test_logged",
                "fix.data.backup.plan",
                plan.id,
                {"result": result, "restored_gb": float(restored_gb or 0.0)},
            )


class FixDataBackupTest(models.Model):
    """One restore test against a backup plan."""

    _name = "fix.data.backup.test"
    _description = "Backup Restore Test"
    _order = "tested_at desc"

    plan_id = fields.Many2one("fix.data.backup.plan", required=True, ondelete="cascade")
    tested_at = fields.Datetime(default=fields.Datetime.now, required=True)
    tested_by = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True, string="Tested By"
    )
    result = fields.Selection(
        [("passed", "Passed"), ("partial", "Partial"), ("failed", "Failed")], required=True
    )
    restored_gb = fields.Float(string="Restored (GB)")
    notes = fields.Char()
    company_id = fields.Many2one(
        "res.company", related="plan_id.company_id", store=True, readonly=True, index=True
    )
