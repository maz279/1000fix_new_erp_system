# fix_data_case_ext — M06 iteration 2: the lab engines the registry's 12
# screens describe (specialisms, attempt tracking, sealed media custody,
# cleanroom slots, free evaluations, firm quotations, backup plans & restore
# tests) plus the button-friendly case wrappers the back-office form needs.
#
# FILE NAME IS LOAD-BEARING: sorts after fix_data_case.py, so the base
# models exist before these extensions load.
import logging
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_data_case import GROUP_LAB_MANAGER, GROUP_OPERATOR, _norm_serial, _require_role

_logger = logging.getLogger(__name__)

SPECIALISMS = [
    ("logical_recovery", "Logical Recovery"),
    ("hardware_repair", "Hardware / PCB Repair"),
    ("raid_reconstruction", "RAID Reconstruction"),
    ("flash_chipoff", "Flash Chip-Off"),
    ("phone_extraction", "Phone Extraction"),
    ("forensic_imaging", "Forensic Imaging"),
    ("firmware_repair", "Firmware Repair"),
]

# A02 audit M06-5: techniques that open the drive or destroy the original
# (chip-off desolders the NAND). They need the customer's recorded consent and
# a booked cleanroom slot that passed its environmental interlock.
INVASIVE_METHODS = ("head_swap", "chip_off", "donor_parts")

# A02 audit M06-4: quote acceptance needs a customer artefact (a signed
# quotation attached to the quote, or an OTP / portal acceptance reference).
# Whether staff may ever accept without one is a business decision: the
# switch is fail-closed (artefact required) unless set to 0.
PARAM_QUOTE_ARTEFACT = "cd_data_case.quote_acceptance_requires_customer_artefact"


def _param_on(env, key, default=True) -> bool:
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return default
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def _resolve_user(env, value):
    """A user named by id or login (the workspace prompt sends text)."""
    if isinstance(value, models.BaseModel):
        return value
    ref = str(value or "").strip()
    Users = env["res.users"].sudo()
    if not ref:
        return Users
    if ref.isdigit():
        return Users.browse(int(ref)).exists()
    return Users.search([("login", "=", ref)], limit=1)


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

    def _media_release_denial(self) -> str:
        """'' when the customer's media may leave custody (returned or
        destroyed), else why not. A02 ERP audit M06-F10: media went back at
        any stage, in the middle of a recovery. It leaves once the data was
        handed over, the case was found unrecoverable, or the customer declined
        the quotation."""
        self.ensure_one()
        if self.state in ("handover", "purged", "unrecoverable", "closed"):
            return ""
        declined = self.quote_ids.filtered(lambda q: q.state == "declined")
        live = self.quote_ids.filtered(lambda q: q.state in ("draft", "sent", "accepted"))
        if self.state in ("new", "custody") and declined and not live:
            return ""
        return (
            "case %s is '%s': the customer's media stays in custody until the data is handed "
            "over, the case is found unrecoverable or the quotation is declined"
            % (self.name, self.state)
        )


class FixDataRecoveryAttempt(models.Model):
    """Attempt tracking: each recovery technique tried on the media, with
    its outcome — the lab's methodology log (freg 4/5)."""

    _name = "fix.data.recovery.attempt"
    _description = "Data Recovery Attempt"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    destructive = fields.Boolean(
        string="Destructive / Invasive Technique",
        compute="_compute_destructive",
        store=True,
        help="Head swap, chip-off and donor parts open or destroy the original media: "
        "they need the customer's consent and a cleanroom slot that passed its interlock.",
    )

    # what the attempt was, once it finished, is evidence
    _FROZEN_WHEN_FINISHED = ("case_id", "method", "cleanroom_slot_id", "started_at")

    def _fix_guarded_fields(self) -> set:
        # A02 audit M06 (M5): the outcome was forged to success with no
        # finished_at; only action_finish sets them.
        return super()._fix_guarded_fields() | {"outcome", "finished_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].outcome not in (False, "in_progress"):
            locked |= set(self._FROZEN_WHEN_FINISHED)
        return locked

    @api.depends("method")
    def _compute_destructive(self):
        for attempt in self:
            attempt.destructive = attempt.method in INVASIVE_METHODS

    @api.model_create_multi
    def create(self, vals_list):
        # A02 audit M06-5 (D5): attempts were logged on a NEW case, so a
        # chip-off ran before any quote, consent or custody.
        cases = self.env["fix.data.recovery.case"].browse(
            [vals["case_id"] for vals in vals_list if vals.get("case_id")]
        )
        for case in cases:
            if case.state != "recovering":
                raise UserError(
                    "Recovery attempts are logged while case %s is in recovery (it is '%s')."
                    % (case.name, case.state)
                )
            # A02 audit M06-P2: Z4 work is for the case's named staff only
            case._z4_assert_assigned("Logging a recovery attempt")
        return super().create(vals_list)

    def write(self, vals):
        frozen = set(self._FROZEN_WHEN_FINISHED) & set(vals)
        if frozen and not self._fix_guard_open():
            for attempt in self:
                if attempt.outcome != "in_progress" and any(
                    attempt._fix_guard_differs(f, vals[f], attempt[f]) for f in frozen
                ):
                    raise UserError(
                        "Attempt %s is finished: its method, case and cleanroom slot are "
                        "evidence and can no longer change." % attempt.id
                    )
        return super().write(vals)

    @api.constrains("method", "cleanroom_slot_id", "case_id")
    def _check_cleanroom_interlock(self):
        """A02 audit M06-5 (D5): an invasive attempt ran with no cleanroom
        slot and no customer consent; the interlock applied only IF a slot was
        linked. A destructive technique now needs both."""
        for attempt in self:
            if not attempt.destructive:
                continue
            case = attempt.case_id
            if not case.destructive_consent_at:
                raise UserError(
                    "'%s' is a destructive / invasive technique: record the customer's "
                    "consent for destructive work on case %s first." % (attempt.method, case.name)
                )
            slot = attempt.cleanroom_slot_id
            if not slot:
                raise UserError(
                    "FLAW-06.2: invasive recovery method '%s' needs a booked cleanroom slot."
                    % attempt.method
                )
            if slot.state == "cancelled" or slot.case_id != case:
                raise UserError(
                    "FLAW-06.2: cleanroom slot #%s is not booked for case %s."
                    % (slot.id, case.name)
                )
            if not slot.interlock_passed:
                raise UserError(
                    "FLAW-06.2 Cleanroom Environmental Interlock: Invasive recovery method '%s' "
                    "cannot proceed because Cleanroom Slot #%s failed ISO Class 5 particle/airflow limits."
                    % (attempt.method, slot.id)
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
            if final not in dict(type(self).outcome.selection) or final == "in_progress":
                raise UserError(
                    "Attempt %s needs an outcome (success/partial/failed/media_damaged)"
                    % attempt.id
                )
            attempt.case_id._z4_assert_assigned("Finishing a recovery attempt")
            # the slot's interlock and the consent are re-checked at the end
            attempt._check_cleanroom_interlock()
            attempt._guarded().write(
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
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    # A02 ERP audit M06-F11: the seal break the witness has still to confirm
    seal_break_requested_by_id = fields.Many2one(
        "res.users", string="Seal Break Requested By", readonly=True, copy=False
    )
    seal_break_witness_id = fields.Many2one(
        "res.users", string="Witness to Confirm", readonly=True, copy=False
    )
    seal_break_requested_at = fields.Datetime(
        string="Seal Break Requested At", readonly=True, copy=False
    )
    # A02 ERP audit M06-F10 / F9: who took the media back, or what destroyed it
    returned_to_id = fields.Many2one("res.partner", string="Returned To", readonly=True, copy=False)
    destruction_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Destruction Certificate",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )

    _seal_unique = models.Constraint(
        "UNIQUE (seal_number)", "This seal / bag number is already registered"
    )

    def _fix_guarded_fields(self) -> set:
        # A02 audit M06-5 (M1, M3): location='destroyed' and an opened seal
        # with the operator as his own witness were set by field writes.
        return super()._fix_guarded_fields() | {
            "location",
            "seal_state",
            "holder",
            "witness_user_id",
            "witness_verified_at",
            "seal_break_requested_by_id",
            "seal_break_witness_id",
            "seal_break_requested_at",
            "returned_to_id",
            "destruction_certificate_id",
        }

    def _log(self, text, action="media_moved", witness_id=False):
        """Append to the case's append-only custody ledger (single source)."""
        for unit in self:
            unit.case_id._custody_log(
                action,
                "[Media %s] %s" % (unit.seal_number, text),
                media_unit=unit,
                witness_id=witness_id,
            )

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
            unit._guarded().write({"location": location, "holder": who})
            publish(
                self.env,
                "data_case.media_transferred",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number, "location": location},
            )

    def action_break_seal(self, handler="", witness_user_id=None):
        """Open the evidence seal in the lab, under dual custody (FLAW-06.1,
        BRU-DTS-01). A02 audit M06-5 (M2): the witness was optional, so the
        default button broke a seal with one person. A witness is now always
        required, and must be another active internal user.

        A02 ERP audit M06-F11: the witness was only NAMED, never present. The
        technician now asks for the break, naming the witness; the seal opens
        when the witness confirms it in their own session
        (action_confirm_seal_break). Trusted system code still breaks it in
        one step."""
        for unit in self:
            if unit.seal_state != "sealed":
                raise UserError("Seal %s is already %s" % (unit.seal_number, unit.seal_state))
            witness = _resolve_user(self.env, witness_user_id)
            if not witness:
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: Breaking evidence seal %s requires a second "
                    "witness sign-off." % unit.seal_number
                )
            if witness.id == self.env.uid:
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: Witness user must be a different person from the unsealing technician."
                )
            if not witness.active or witness.share:
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: the witness must be an active internal user."
                )
            who = handler or self.env.user.name
            if not self.env.su:
                _require_role(
                    self.env, GROUP_OPERATOR, "Data Recovery Operator", "Breaking an evidence seal"
                )
                unit._guarded().write(
                    {
                        "seal_break_requested_by_id": self.env.uid,
                        "seal_break_witness_id": witness.id,
                        "seal_break_requested_at": fields.Datetime.now(),
                    }
                )
                note = (
                    "%s asks to break evidence seal %s and names %s as witness. The seal opens "
                    "when %s confirms it in their own session (Confirm as Witness)."
                    % (who, unit.seal_number, witness.name, witness.name)
                )
                unit.message_post(body=note)
                unit.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Witness the seal break of %s" % unit.seal_number,
                    note=note,
                    user_id=witness.id,
                )
                continue
            unit._break_seal_now(who, witness)

    def _break_seal_now(self, who, witness):
        self.ensure_one()
        self._log(
            "seal broken by %s (witnessed by %s)" % (who, witness.name),
            action="seal_broken",
            witness_id=witness.id,
        )
        self._guarded().write(
            {
                "seal_state": "opened_in_lab",
                "holder": who,
                "witness_user_id": witness.id,
                "witness_verified_at": fields.Datetime.now(),
                "seal_break_requested_by_id": False,
                "seal_break_witness_id": False,
                "seal_break_requested_at": False,
            }
        )
        publish(
            self.env,
            "data_case.media_seal_broken",
            "fix.data.media.unit",
            self.id,
            {"seal": self.seal_number, "witness_user_id": witness.id},
        )

    def action_confirm_seal_break(self):
        """The named witness confirms, in their own session, the seal break
        another person asked for (A02 ERP audit M06-F11)."""
        for unit in self:
            if unit.seal_state != "sealed":
                raise UserError("Seal %s is already %s" % (unit.seal_number, unit.seal_state))
            witness = unit.seal_break_witness_id
            requester = unit.seal_break_requested_by_id
            if not (witness and requester):
                raise UserError("No seal break of %s awaits a witness." % unit.seal_number)
            if self.env.user != witness:
                raise AccessError(
                    "Only %s, the named witness, confirms the seal break of %s, in their own "
                    "session." % (witness.name, unit.seal_number)
                )
            if requester == witness:
                raise UserError("FLAW-06.1 Dual-Custody Gate: the witness cannot break the seal.")
            # the witness need not hold the lab's write rights: identity is the check
            unit.sudo()._break_seal_now(
                "%s (confirmed by the witness %s in their own session)"
                % (requester.name, witness.name),
                witness,
            )
            unit.sudo().write({"holder": requester.name})
        return True

    def action_break_seal_with_witness(self, witness_user_id=None, handler=""):
        """Strict FLAW-06.1 entry point requiring an explicit distinct witness."""
        self.action_break_seal(handler=handler, witness_user_id=witness_user_id)
        return True

    def action_return(self, handler="", recipient=None):
        """Give the media back to the customer. A02 ERP audit M06-F10: it went
        back at any stage, to anyone. Now by the data lab, once the case allows
        it (_media_release_denial), to the customer or one of its contacts
        (default: the case's handover recipient, else the customer)."""
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Returning media")
        for unit in self:
            if unit.location in ("destroyed", "returned_to_customer"):
                raise UserError("Unit %s is %s" % (unit.seal_number, unit.location))
            case = unit.case_id.sudo()
            denial = case._media_release_denial()
            if denial:
                raise UserError("Media %s cannot be returned: %s." % (unit.seal_number, denial))
            partner = self.env["res.partner"]
            if isinstance(recipient, models.BaseModel):
                partner = recipient
            elif recipient:
                try:
                    partner = self.env["res.partner"].sudo().browse(int(recipient)).exists()
                except (TypeError, ValueError):
                    partner = self.env["res.partner"]
                if not partner:
                    raise UserError("No contact #%s to return the media to." % recipient)
            partner = partner or case.handover_recipient_id or case.customer_id
            if partner.commercial_partner_id != case.customer_id.commercial_partner_id:
                raise UserError(
                    "%s is not the customer %s or one of its contacts: the media goes back "
                    "only to the customer." % (partner.display_name, case.customer_id.name)
                )
            who = handler or self.env.user.name
            unit._log(
                "returned to customer by %s, to %s" % (who, partner.display_name),
                action="media_returned",
            )
            unit._guarded().write(
                {"location": "returned_to_customer", "holder": who, "returned_to_id": partner.id}
            )
            publish(
                self.env,
                "data_case.media_returned",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number},
            )

    def _destruction_certificate(self, certificate):
        """The certificate a destruction rests on: the one passed (record, id
        or reference), else the single verified physical destruction of the
        case's media serial that destroyed nothing else yet."""
        self.ensure_one()
        Cert = self.env["fix.data.wipe.certificate"].sudo()
        if isinstance(certificate, models.BaseModel):
            return certificate.sudo()
        ref = str(certificate or "").strip()
        if ref:
            cert = Cert.browse(int(ref)).exists() if ref.isdigit() else Cert
            cert = cert or Cert.search([("name", "=", ref)], limit=1)
            if not cert:
                raise UserError("No wipe certificate '%s' was found." % ref)
            return cert
        serial = _norm_serial(self.case_id.media_serial_number)
        used = (
            self.sudo()
            .search([("destruction_certificate_id", "!=", False)])
            .mapped("destruction_certificate_id")
        )
        matches = (
            Cert.search(
                [
                    ("sanitization_status", "=", "verified"),
                    ("method", "=", "physical_destruction"),
                ]
            ).filtered(lambda c: serial and _norm_serial(c.serial_number) == serial)
            - used
        )
        if len(matches) != 1:
            raise UserError(
                "Destroying media %s needs its verified physical-destruction certificate%s."
                % (
                    self.seal_number,
                    ": several match, name the one to use" if matches else "",
                )
            )
        return matches

    def action_destroy(self, certificate=None):
        """The media was physically destroyed (A02 ERP audit M06-F9: the
        'destroyed' location was unreachable, so a purged case's drive could
        only stay in the lab). Bound to a VERIFIED physical-destruction
        certificate for the case's media serial, answering a destruction
        request the customer (or the corporate client) raised; one
        certificate destroys one unit."""
        _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Destroying media")
        for unit in self:
            if unit.location in ("destroyed", "returned_to_customer"):
                raise UserError("Unit %s is %s" % (unit.seal_number, unit.location))
            case = unit.case_id.sudo()
            denial = case._media_release_denial()
            if denial:
                raise UserError("Media %s cannot be destroyed: %s." % (unit.seal_number, denial))
            cert = unit._destruction_certificate(certificate)
            if cert.method != "physical_destruction":
                raise UserError(
                    "Certificate %s is an erasure, not a physical destruction." % cert.name
                )
            refusal = cert._fix_certify_denial(case.media_serial_number)
            if refusal:
                raise UserError("Media %s cannot be destroyed: %s." % (unit.seal_number, refusal))
            request = cert.wipe_request_id if "wipe_request_id" in cert._fields else False
            if not request or request.source not in ("customer", "corporate_decommission"):
                raise UserError(
                    "Certificate %s answers no destruction request from the customer: the "
                    "customer's media is destroyed only on the customer's own request." % cert.name
                )
            if self.sudo().search_count(
                [("destruction_certificate_id", "=", cert.id), ("id", "!=", unit.id)]
            ):
                raise UserError("Certificate %s already destroyed another unit." % cert.name)
            unit._log(
                "destroyed under physical-destruction certificate %s" % cert.name,
                action="media_destroyed",
            )
            unit._guarded().write(
                {
                    "location": "destroyed",
                    "holder": False,
                    "destruction_certificate_id": cert.id,
                }
            )
            publish(
                self.env,
                "data_case.media_destroyed",
                "fix.data.media.unit",
                unit.id,
                {"seal": unit.seal_number, "certificate": cert.name},
            )
        return True


class FixDataCleanroomSlot(models.Model):
    """Cleanroom scheduling: bookable ISO-class bench slots for the
    contamination-critical interventions (head swaps, platter transfers)."""

    _name = "fix.data.cleanroom.slot"
    _description = "Cleanroom Slot"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    # the environmental readings a used slot was judged on are evidence
    _FROZEN_AFTER_PLANNED = (
        "case_id",
        "purpose",
        "iso_class",
        "particle_count_per_ft3",
        "laminar_airflow_mps",
        "temperature_c",
        "humidity_pct",
        "telemetry_log_attachment_id",
    )

    def _fix_guarded_fields(self) -> set:
        # A02 audit M06-5 (M4): a failed-interlock slot was forged to 'used'.
        return super()._fix_guarded_fields() | {"state", "interlock_passed"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].state not in (False, "planned"):
            locked |= set(self._FROZEN_AFTER_PLANNED)
        return locked

    def write(self, vals):
        frozen = set(self._FROZEN_AFTER_PLANNED) & set(vals)
        if frozen and not self._fix_guard_open():
            for slot in self:
                if slot.state != "planned" and any(
                    slot._fix_guard_differs(f, vals[f], slot[f]) for f in frozen
                ):
                    raise UserError(
                        "Cleanroom slot #%s is %s: its booking and environmental readings "
                        "can no longer change." % (slot.id, slot.state)
                    )
        return super().write(vals)

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
            slot._guarded().write({"state": "used"})
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
            slot._guarded().write({"state": "cancelled"})


class FixDataEvaluation(models.Model):
    """The free evaluation: what came in, what is recoverable, at what
    confidence — and how long that answer took (the turnaround KPI)."""

    _name = "fix.data.evaluation"
    _description = "Data Recovery Evaluation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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

    # the verdict recovery was started on (A02 audit M06-4) is frozen
    _FROZEN_WHEN_COMPLETE = (
        "case_id",
        "received_at",
        "verdict",
        "recoverability_pct",
        "recommended_specialism",
        "findings",
        "donor_required",
        "donor_estimated_cost_bdt",
    )

    def _fix_guarded_fields(self) -> set:
        # a completed evaluation now gates recovery: only action_complete stamps it
        return super()._fix_guarded_fields() | {"evaluated_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].evaluated_at:
            locked |= set(self._FROZEN_WHEN_COMPLETE)
        return locked

    def write(self, vals):
        frozen = set(self._FROZEN_WHEN_COMPLETE) & set(vals)
        if frozen and not self._fix_guard_open():
            for ev in self:
                if ev.evaluated_at and any(
                    ev._fix_guard_differs(f, vals[f], ev[f]) for f in frozen
                ):
                    raise UserError(
                        "Evaluation of case %s is complete: its verdict is frozen."
                        % ev.case_id.name
                    )
        return super().write(vals)

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
            ev._guarded().write(
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
    # fix.approvable.mixin carries fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    # A02 audit B1: a re-quote that raises the price the customer was quoted
    # (or drops no-data-no-fee) is a routed M63 decision for the lab manager,
    # never the person who raised the price. It cannot be sent before that.
    _approval_domain = "data_quote_requote"
    _approval_apply_method = "action_approve_requote"
    _approval_group = GROUP_LAB_MANAGER
    _approval_routed = True

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
        readonly=True,
        copy=False,
    )
    description = fields.Char(string="Scope")
    valid_until = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("declined", "Declined"),
            ("superseded", "Superseded"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    # A02 audit M06-4 (Q2): staff accepted on the customer's behalf. The
    # acceptance records the customer's artefact and who recorded it.
    sent_at = fields.Datetime(readonly=True, copy=False)
    acceptance_channel = fields.Selection(
        [
            ("signed_document", "Customer-Signed Quotation"),
            ("otp_portal", "Customer OTP / Portal Acceptance"),
            ("staff_recorded", "Staff Recorded (no customer artefact required)"),
        ],
        readonly=True,
        copy=False,
    )
    customer_acceptance_reference = fields.Char(
        string="Customer OTP / Portal Acceptance Reference", readonly=True, copy=False
    )
    accepted_at = fields.Datetime(readonly=True, copy=False)
    accepted_by_id = fields.Many2one(
        "res.users", string="Acceptance Recorded By", readonly=True, copy=False
    )
    superseded_by_id = fields.Many2one(
        "fix.data.quote", string="Superseded By", readonly=True, copy=False
    )
    supersedes_id = fields.Many2one(
        "fix.data.quote", string="Re-quote Of", readonly=True, copy=False
    )
    requote_approved_by_id = fields.Many2one(
        "res.users", string="Price Change Approved By", readonly=True, copy=False
    )
    requote_approved_at = fields.Datetime(
        string="Price Change Approved At", readonly=True, copy=False
    )
    requote_approved_total = fields.Monetary(
        string="Total the Approval Covers",
        currency_field="currency_id",
        readonly=True,
        copy=False,
    )
    requote_approved_ndnf = fields.Boolean(
        string="No-Data-No-Fee at Approval", readonly=True, copy=False
    )

    # A02 audit M06-10 (Q4): a quotation of BDT -5,000 was sent and accepted.
    _amount_not_negative = models.Constraint(
        "CHECK (amount >= 0 AND donor_fee_bdt >= 0)",
        "A quotation amount and donor fee cannot be negative",
    )

    # A02 audit M06-4 (Q3): the price was raised 15k -> 95k after acceptance,
    # with no-data-no-fee dropped. What the customer was sent is frozen; a
    # change is a new quotation (action_requote) and a new acceptance.
    _TERMS = (
        "case_id",
        "amount",
        "currency_id",
        "donor_fee_bdt",
        "no_data_no_fee_applies",
        "description",
        "valid_until",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "signed_quote_attachment_id",
            "sent_at",
            "acceptance_channel",
            "customer_acceptance_reference",
            "accepted_at",
            "accepted_by_id",
            "superseded_by_id",
            "supersedes_id",
            "requote_approved_by_id",
            "requote_approved_at",
            "requote_approved_total",
            "requote_approved_ndnf",
        }

    # ---- evaluation gate (A02 audit M06-P2) ---------------------------------
    @api.model
    def _assert_case_evaluated(self, case):
        """A quotation prices a completed evaluation that found data to recover."""
        evaluations = case.evaluation_ids.filtered("evaluated_at").sorted("evaluated_at")
        if not evaluations:
            raise UserError(
                "Case %s: complete the free evaluation before quoting a price." % case.name
            )
        if evaluations[-1].verdict == "unrecoverable":
            raise UserError(
                "Case %s was evaluated unrecoverable: there is nothing to quote (no data, no "
                "fee). Mark the case unrecoverable and return the media." % case.name
            )

    # ---- the routed price change (A02 audit B1) ----------------------------
    def _quote_total(self) -> float:
        self.ensure_one()
        return (self.amount or 0.0) + (self.donor_fee_bdt or 0.0)

    def _requote_worsens(self) -> list:
        """What this re-quote changes against the customer, else []."""
        self.ensure_one()
        prior = self.supersedes_id
        if not prior:
            return []
        reasons = []
        if self._quote_total() > prior._quote_total() + 0.005:
            reasons.append(
                "the price rises from BDT %.2f to BDT %.2f"
                % (prior._quote_total(), self._quote_total())
            )
        if prior.no_data_no_fee_applies and not self.no_data_no_fee_applies:
            reasons.append("the no-data-no-fee guarantee is dropped")
        return reasons

    def _approval_needed(self) -> bool:
        return self.state == "draft" and bool(self._requote_worsens())

    def _approval_amount(self) -> float:
        prior = self.supersedes_id
        return max(self._quote_total() - prior._quote_total(), 0.0) if prior else 0.0

    def _requote_approval_covers(self) -> bool:
        self.ensure_one()
        return bool(
            self.approval_state == "approved"
            and self.requote_approved_at
            and abs((self.requote_approved_total or 0.0) - self._quote_total()) <= 0.005
            and bool(self.requote_approved_ndnf) == bool(self.no_data_no_fee_applies)
        )

    def action_approve_requote(self):
        """The M63 apply method: only the lab manager's inbox task runs it."""
        self._approval_assert_routed()
        for quote in self:
            if quote.state != "draft" or not quote._requote_worsens():
                raise UserError("Quotation %s has no price change to approve." % quote.name)
            authority = quote._approval_authority_user()
            if not self.env.su and not authority.has_group(GROUP_LAB_MANAGER):
                raise UserError(
                    "Approving a raised re-quote needs the Data Recovery Lab Manager role, "
                    "which %s does not hold." % authority.name
                )
            raisers = (
                quote.create_uid
                | quote.approval_request_id.requested_by_id
                | quote.approval_amount_changed_by_id
            )
            if not self.env.su and quote._approval_acting_users() & raisers:
                raise UserError(
                    "Segregation of duties: the price change on %s must be approved by "
                    "someone who did not raise it." % quote.name
                )
            quote._guarded().write(
                {
                    "requote_approved_by_id": self.env.uid,
                    "requote_approved_at": fields.Datetime.now(),
                    "requote_approved_total": quote._quote_total(),
                    "requote_approved_ndnf": quote.no_data_no_fee_applies,
                }
            )
        return True

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].state not in (False, "draft"):
            locked |= set(self._TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        """A02 ERP audit M06-F5: a fresh quotation on a case that already had
        one side-stepped the re-quote approval (a raised price went out with
        no lab-manager decision). One live quotation per case; a new one only
        through action_requote, and none once the case is past custody."""
        Case = self.env["fix.data.recovery.case"]
        requote = self._fix_guard_has_token()
        seen = set()
        for vals in vals_list:
            if vals.get("case_id"):
                case = Case.browse(vals["case_id"])
                self._assert_case_evaluated(case)
                if case.state not in ("new", "custody"):
                    raise UserError(
                        "Case %s is past quotation ('%s'): no new quotation is raised."
                        % (case.name, case.state)
                    )
                live = case.sudo().quote_ids.filtered(
                    lambda q: q.state in ("draft", "sent", "accepted")
                )
                if not requote and (live or case.id in seen):
                    raise UserError(
                        "Case %s already has a live quotation (%s): change its price or terms "
                        "with Re-quote, which the customer accepts again (and the lab manager "
                        "approves when the price rises)."
                        % (case.name, ", ".join(live.mapped("name")) or "in this batch")
                    )
                seen.add(case.id)
            vals["name"] = self.env["ir.sequence"].next_by_code("fix.data.quote") or "DRQ/New"
        return super().create(vals_list)

    def write(self, vals):
        terms = set(self._TERMS) & set(vals)
        if terms and not self._fix_guard_open():
            for quote in self:
                if quote.state != "draft" and any(
                    quote._fix_guard_differs(f, vals[f], quote[f]) for f in terms
                ):
                    raise UserError(
                        "Quotation %s was sent to the customer: its price and terms are "
                        "frozen. Issue a new quotation (Re-quote) to change them." % quote.name
                    )
        result = super().write(vals)
        if terms:
            # an approved price change covers the price that was approved
            moved = self.filtered(
                lambda q: q.approval_state == "approved" and not q._requote_approval_covers()
            )
            if moved:
                moved._approval_void("the re-quoted price or terms changed after approval")
        return result

    def action_send(self):
        for quote in self:
            if quote.state != "draft":
                raise UserError("Quote %s is not draft" % quote.name)
            self._assert_case_evaluated(quote.case_id)
            worse = quote._requote_worsens()
            if worse and not quote._requote_approval_covers():
                raise UserError(
                    "Re-quote %s cannot be sent: %s. That needs the lab manager's approval "
                    "(Request Approval), and the approval covers the price it was given for."
                    % (quote.name, " and ".join(worse))
                )
            quote._guarded().write({"state": "sent", "sent_at": fields.Datetime.now()})
            publish(
                self.env,
                "data_case.quote_sent",
                "fix.data.quote",
                quote.id,
                {"case": quote.case_id.name, "amount": quote.amount},
            )

    def _signed_quotation(self, signed_attachment_id=None):
        """The customer-signed quotation: a non-empty file attached to THIS
        quote (named, or the latest one uploaded to it)."""
        self.ensure_one()
        Attachment = self.env["ir.attachment"].sudo()
        on_quote = [("res_model", "=", self._name), ("res_id", "=", self.id)]
        if signed_attachment_id:
            try:
                att = Attachment.search([("id", "=", int(signed_attachment_id)), *on_quote])
            except (TypeError, ValueError):
                att = Attachment
            if not att or not att.raw:
                raise UserError(
                    "The signed quotation must be a non-empty file attached to quotation %s."
                    % self.name
                )
            return att
        for att in Attachment.search(on_quote, order="id desc"):
            if att.raw:
                return att
        return Attachment

    def action_accept(self, acceptance_reference=None, signed_attachment_id=None):
        """Record the CUSTOMER's acceptance (A02 audit M06-4, Q2): it needs the
        customer's artefact — a signed quotation attached to this quote, or
        the customer's OTP / portal acceptance reference. Staff cannot accept
        on the customer's behalf unless the business turns the
        `cd_data_case.quote_acceptance_requires_customer_artefact` switch off."""
        required = _param_on(self.env, PARAM_QUOTE_ARTEFACT, True)
        for quote in self:
            if quote.state != "sent":
                raise UserError("Quote %s must be sent before acceptance" % quote.name)
            if quote.valid_until and quote.valid_until < date.today():
                raise UserError("Quote %s expired on %s" % (quote.name, quote.valid_until))
            ref = str(acceptance_reference or "").strip()
            signed = quote._signed_quotation(signed_attachment_id) if not ref else None
            if ref and len(ref) < 6:
                raise UserError(
                    "Quote %s: an OTP / portal acceptance reference has at least 6 characters."
                    % quote.name
                )
            if signed:
                channel = "signed_document"
            elif ref:
                channel = "otp_portal"
            elif not required:
                channel = "staff_recorded"
            else:
                raise UserError(
                    "Quote %s needs the customer's acceptance: attach the customer-signed "
                    "quotation to the quote, or give the customer's OTP / portal acceptance "
                    "reference. Staff cannot accept on the customer's behalf." % quote.name
                )
            quote._guarded().write(
                {
                    "state": "accepted",
                    "acceptance_channel": channel,
                    "signed_quote_attachment_id": signed.id if signed else False,
                    "customer_acceptance_reference": ref or False,
                    "accepted_at": fields.Datetime.now(),
                    "accepted_by_id": self.env.uid,
                }
            )
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
            quote._guarded().write({"state": "declined"})

    def action_requote(self):
        """Change a sent or accepted price or terms the only legitimate way:
        a new draft quotation that the customer must accept again; this one
        is superseded (A02 audit M06-4, Q3)."""
        new_quotes = self.browse()
        for quote in self:
            if quote.state not in ("sent", "accepted"):
                raise UserError(
                    "Only a sent or accepted quotation is re-quoted (%s is '%s'); edit a draft "
                    "directly." % (quote.name, quote.state)
                )
            if quote.case_id.state not in ("new", "custody"):
                raise UserError(
                    "Case %s is past quotation ('%s'): its accepted price stands."
                    % (quote.case_id.name, quote.case_id.state)
                )
            # the one legitimate second quotation: through the guard token
            new = self._guarded().create(
                {
                    "case_id": quote.case_id.id,
                    "currency_id": quote.currency_id.id,
                    "amount": quote.amount,
                    "donor_fee_bdt": quote.donor_fee_bdt,
                    "no_data_no_fee_applies": quote.no_data_no_fee_applies,
                    "description": quote.description,
                    "valid_until": quote.valid_until,
                }
            )
            new._guarded().write({"supersedes_id": quote.id})
            quote._guarded().write({"state": "superseded", "superseded_by_id": new.id})
            new_quotes |= new
        return {"quote_ids": new_quotes.ids}


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
                and (
                    not plan.next_test_due
                    or plan.next_test_due
                    >= fields.Date.context_today(plan.with_context(tz="Asia/Dhaka"))
                )
            )

    test_overdue_notified_on = fields.Date(
        string="Overdue Notice Sent For", readonly=True, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        # A02 audit B4: next_test_due was set only by a logged test, so a new
        # plan was never due. The first test falls due one interval out.
        for vals in vals_list:
            if not vals.get("next_test_due"):
                # the Dhaka business day (date.today() is the UTC day 00-06 BST)
                vals["next_test_due"] = fields.Date.context_today(
                    self.with_context(tz="Asia/Dhaka")
                ) + timedelta(days=vals.get("test_frequency_days") or 90)
        return super().create(vals_list)

    @api.model
    def cron_restore_test_due(self):
        """B4: a to-do for every plan whose restore test is overdue, once per
        due date (idempotent). Plans with no date get one from their creation."""
        # the business day is Dhaka's, whatever the cron user's zone
        today = fields.Date.context_today(self.with_context(tz="Asia/Dhaka"))
        undated = self.sudo().search([("next_test_due", "=", False)])
        for plan in undated:
            start = (plan.create_date or fields.Datetime.now()).date()
            plan.next_test_due = start + timedelta(days=plan.test_frequency_days or 90)
        overdue = self.sudo().search([("next_test_due", "<", today)])
        notified = 0
        for plan in overdue.filtered(lambda p: p.test_overdue_notified_on != p.next_test_due):
            try:
                with self.env.cr.savepoint():
                    note = "Restore test overdue since %s (every %d days)." % (
                        plan.next_test_due,
                        plan.test_frequency_days or 90,
                    )
                    plan.message_post(body=note)
                    user = plan.create_uid
                    if user and user.active and not user.share:
                        plan.activity_schedule(
                            "mail.mail_activity_data_todo",
                            summary="Restore test overdue: %s" % plan.name,
                            note=note,
                            user_id=user.id,
                        )
                    plan.test_overdue_notified_on = plan.next_test_due
                    notified += 1
            except Exception:
                _logger.exception("M06 restore-test reminder failed for plan %s", plan.id)
        return notified

    def action_log_test(
        self, result="passed", restored_gb=0.0, notes="", evidence_attachment_id=None, scope=None
    ):
        """Record a restore test. The test record rolls the plan's next due
        date forward and publishes the event (M06 capture pass 2: the restore
        test is also captured on its own form, with its scope and evidence;
        a passed test needs the evidence). Fail closed on an unknown result."""
        if result not in ("passed", "partial", "failed"):
            raise UserError("A restore test result is one of: passed, partial, failed")
        for plan in self:
            self.env["fix.data.backup.test"].create(
                {
                    "plan_id": plan.id,
                    "result": result,
                    "restored_gb": float(restored_gb or 0.0),
                    "notes": notes or False,
                    "evidence_attachment_id": evidence_attachment_id or False,
                    "scope_tested": scope or False,
                }
            )
        return True


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
