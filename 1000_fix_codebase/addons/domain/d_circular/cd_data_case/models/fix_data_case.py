# fix_data_case — M06: data recovery, wipe certificates (P09-M05).
# The most residency-sensitive module: recovered data lives ONLY in Z4.
#
# A02 workflow audit (2026-11-03), P0: every lifecycle, custody, evidence and
# approval field below changed by a plain field write (M06-1..M06-6). They
# are now guarded (fix.guarded.mixin) and change only through the transition
# methods, which check the state, the role and segregation of duties.
import hashlib

from odoo import api, fields, models
from odoo.exceptions import AccessDenied, AccessError, UserError
from odoo.http import request

from libs.py.fix_events import publish

WIPE_METHODS = [
    ("nist_800_88", "NIST SP 800-88 (Clear)"),
    ("nist_800_88_purge", "NIST SP 800-88 (Purge)"),
    ("cryptographic_erase", "Cryptographic Erase"),
    ("physical_destruction", "Physical Destruction"),
]

# A02 audit M06 (A3): the module had no group at all, so every internal user
# was operator, wipe verifier and Z4 accessor at once.
GROUP_OPERATOR = "cd_data_case.group_data_recovery_operator"
GROUP_WIPE_VERIFIER = "cd_data_case.group_wipe_verifier"
GROUP_Z4_CUSTODIAN = "cd_data_case.group_z4_custodian"
# A02 audit B1: approves a re-quote that raises the price (M63 inbox).
GROUP_LAB_MANAGER = "cd_data_case.group_data_lab_manager"

CUSTODY_ACTIONS = [
    ("custody_taken", "Custody Taken"),
    ("custody_transfer", "Custody Transfer"),
    ("routed_z4", "Routed to Z4"),
    ("media_moved", "Media Moved"),
    ("seal_broken", "Seal Broken"),
    ("media_returned", "Media Returned"),
    ("handover", "Handover"),
    ("purged", "Purged"),
    ("unrecoverable", "Marked Unrecoverable"),
    ("closed", "Closed"),
    # A02 audit M06-P2: named Z4 staff, and imaging as a recorded step
    ("z4_assigned", "Z4 Staff Assigned"),
    ("imaged", "Forensic Image Recorded"),
    ("image_verified", "Forensic Image Verified"),
    # A02 ERP audit M06-F9: a unit destroyed under a physical-destruction
    # certificate, and the witness's own confirmation of a seal break (F11)
    ("media_destroyed", "Media Destroyed"),
    # A02 pass 2 M06-01 / M06-03: a lab-manager customer correction, and the
    # first half of a two-person custody move (the receiver confirms it)
    ("customer_corrected", "Customer Corrected (Lab Manager)"),
    ("custody_requested", "Custody Hand-off Requested"),
    # A02 pass 2 review: the requester withdraws a hand-off not yet confirmed
    ("custody_withdrawn", "Custody Hand-off Withdrawn"),
]


def _norm_serial(value) -> str:
    """A media serial compared without spaces or case (labels vary)."""
    return "".join(str(value or "").split()).upper()


def _require_role(env, xmlid, role, action):
    """Refuse `action` unless the acting user holds `xmlid`. Superuser code
    (crons, sudo service calls) is trusted, as fix.guarded.mixin trusts it."""
    if env.su or env.user.has_group(xmlid):
        return
    group = env.ref(xmlid, raise_if_not_found=False)
    if group and not group.sudo().user_ids:
        raise AccessError(
            "%s needs the '%s' role, and no one holds it yet. Appointing it is a "
            "business decision: ask an administrator to add the right person." % (action, role)
        )
    raise AccessError("%s needs the '%s' role." % (action, role))


class FixZ4AccessAudit(models.Model):
    """SC-002 / SC-007: Per-read immutable audit log on every Z4 access.
    Statutory Bangladesh sovereign data access record. Append-only."""

    _name = "fix.z4.access.audit"
    _description = "Z4 Sovereign Data Per-Read Access Audit Log"
    _order = "access_time desc"

    case_id = fields.Many2one(
        "fix.data.recovery.case",
        string="Data Recovery Case",
        required=True,
        ondelete="cascade",
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="case_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        related="case_id.operating_unit_id",
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Accessor",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )
    user_name = fields.Char(string="Accessor Name", readonly=True)
    access_time = fields.Datetime(
        string="Access Timestamp", default=fields.Datetime.now, readonly=True, index=True
    )
    access_type = fields.Selection(
        [
            ("metadata_read", "Metadata Read"),
            ("file_list_read", "Recovered File List Read"),
            ("file_download", "Recovered Data Download"),
            ("preview_read", "Media File Preview"),
            ("export", "Customer Handover Export"),
        ],
        string="Access Type",
        required=True,
        readonly=True,
    )
    purpose = fields.Char(string="Statutory Justification / Purpose", required=True, readonly=True)
    ip_address = fields.Char(string="Client IP Address", readonly=True)
    # A02 audit M06-3: defaulted to True, so any row claimed a step-up. Only
    # the access action, after the TOTP check, sets it.
    step_up_verified = fields.Boolean(string="Step-Up 2FA Verified", default=False, readonly=True)
    sha256_audit_hash = fields.Char(string="Audit Entry SHA-256 Hash", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        import time

        # A02 audit M06-3 (Z1): any internal user created "immutable" rows
        # naming another user as accessor with step_up_verified=True. Rows are
        # written only by action_access_recovered_data, through sudo (the ACL
        # grants create to no one).
        if not self.env.su:
            raise AccessError(
                "Z4 access audit rows are written only by the Z4 step-up access "
                "action; they cannot be created by hand."
            )
        for vals in vals_list:
            if not vals.get("user_name"):
                user = self.env["res.users"].browse(vals.get("user_id", self.env.uid))
                vals["user_name"] = user.name or "Technician"
            seed = (
                f"{vals.get('case_id')}-{vals.get('user_id')}-"
                f"{vals.get('access_type')}-{vals.get('purpose')}-"
                f"{vals.get('ip_address')}-{time.time()}"
            )
            vals["sha256_audit_hash"] = hashlib.sha256(seed.encode()).hexdigest()
        return super().create(vals_list)

    def write(self, vals):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. "
            "Modifications are strictly prohibited."
        )

    def unlink(self):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. "
            "Deletion is strictly prohibited."
        )


class FixDataCustodyEvent(models.Model):
    """A02 audit M06-6 (A5): the chain of custody as an append-only ledger.

    The chain was a writable Text field: it was rewritten through the P03
    form and the ORM, and 91 live cases sat in custody with an empty chain.
    A row is written only by a custody action of the case or a media unit
    (the in-process guard token), stamped by the server with the acting user,
    the time and the media serial, and hash-linked to the row before it.
    Rows can never be changed or deleted."""

    _name = "fix.data.custody.event"
    _description = "Data Case Chain-of-Custody Event"
    _inherit = ["fix.guarded.mixin"]
    _order = "case_id, id"

    case_id = fields.Many2one(
        "fix.data.recovery.case", required=True, ondelete="restrict", index=True, readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", readonly=True)
    media_unit_id = fields.Many2one(
        "fix.data.media.unit", string="Media Unit", ondelete="restrict", readonly=True
    )
    action = fields.Selection(CUSTODY_ACTIONS, required=True, readonly=True)
    description = fields.Char(required=True, readonly=True)
    actor_id = fields.Many2one("res.users", string="Recorded By", required=True, readonly=True)
    event_at = fields.Datetime(string="Recorded At", required=True, readonly=True)
    media_serial = fields.Char(string="Media Serial", readonly=True)
    witness_id = fields.Many2one("res.users", string="Witness", readonly=True)
    prev_hash = fields.Char(string="Previous Entry Hash", readonly=True)
    entry_hash = fields.Char(string="Entry Hash (SHA-256)", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Chain-of-custody events are recorded only by the custody actions "
                "(take custody, transfer, break seal, return, handover, purge)."
            )
        now = fields.Datetime.now()
        last_hash = {}
        Case = self.env["fix.data.recovery.case"].sudo()
        for vals in vals_list:
            case = Case.browse(vals["case_id"])
            # server-stamped: what the caller sent for these is ignored
            vals.update(
                actor_id=self.env.uid,
                event_at=now,
                media_serial=case.media_serial_number or False,
                company_id=case.company_id.id,
                operating_unit_id=case.operating_unit_id.id or False,
            )
            witness = vals.get("witness_id") or False
            if vals.get("action") == "seal_broken" and not self._seal_break_witnessed(
                vals, witness
            ):
                raise UserError(
                    "FLAW-06.1 Dual-Custody Gate: a seal break is recorded only with a "
                    "second witness who is not the person breaking the seal."
                )
            if case.id not in last_hash:
                last = self.sudo().search([("case_id", "=", case.id)], order="id desc", limit=1)
                last_hash[case.id] = last.entry_hash or ""
            vals["prev_hash"] = last_hash[case.id] or False
            seed = "|".join(
                str(part or "")
                for part in (
                    last_hash[case.id],
                    case.id,
                    vals.get("media_unit_id"),
                    vals.get("action"),
                    vals.get("description"),
                    self.env.uid,
                    now,
                    vals["media_serial"],
                    witness,
                )
            )
            vals["entry_hash"] = hashlib.sha256(seed.encode()).hexdigest()
            last_hash[case.id] = vals["entry_hash"]
        return super().create(vals_list)

    def _seal_break_witnessed(self, vals, witness) -> bool:
        """A seal break is recorded with a witness who is not the person
        breaking it. A02 ERP audit M06-F11: the witness confirms in their own
        session, so the event is written BY the witness, for the break another
        person asked for and named them on."""
        if not witness:
            return False
        if witness != self.env.uid:
            return True
        unit = (
            self.env["fix.data.media.unit"].sudo().browse(vals.get("media_unit_id") or 0).exists()
        )
        return bool(
            unit
            and unit.seal_break_witness_id.id == witness
            and unit.seal_break_requested_by_id
            and unit.seal_break_requested_by_id.id != witness
        )

    def write(self, vals):
        raise UserError("The chain of custody is append-only: a recorded event cannot be changed.")

    def unlink(self):
        raise UserError("The chain of custody is append-only: a recorded event cannot be deleted.")


class FixDataRecoveryCase(models.Model):
    """Journey 11: data recovery case -> custody -> recovery -> handover ->
    purge certificate. ALL recovered data routes to Z4 (SC-007, FF-09)."""

    _name = "fix.data.recovery.case"
    _description = "Data Recovery Case"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    media_type = fields.Selection(
        [
            ("hdd", "HDD"),
            ("ssd", "SSD"),
            ("usb", "USB Drive"),
            ("sd_card", "SD Card"),
            ("phone", "Phone Storage"),
            ("other", "Other"),
        ],
        required=True,
        default="hdd",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("custody", "In Custody"),
            ("recovering", "Recovering"),
            ("recovered", "Recovered"),
            ("handover", "Handover"),
            ("purged", "Purged"),
            ("closed", "Closed"),
            ("unrecoverable", "Unrecoverable"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    custody_event_ids = fields.One2many(
        "fix.data.custody.event", "case_id", string="Custody Ledger", readonly=True
    )
    # A02 audit M06-6: a read-only rendering of the append-only ledger, kept
    # for the screens that show the chain as text.
    custody_chain = fields.Text(
        string="Chain of Custody Log",
        compute="_compute_custody_chain",
        help="Every hand-off logged: who, when, where (rendered from the append-only ledger)",
    )
    residency_zone = fields.Selection(
        [("z4", "Z4 (Residency-Classified)"), ("pending", "Pending Routing")],
        default="pending",
        required=True,
        help="SC-007: recovered customer data lives ONLY in Z4. Set by the routing step.",
    )
    purge_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Purge Certificate",
        ondelete="set null",
        help="The wipe operator's verified certificate; required to purge",
    )
    # A02 audit M06-5: destructive or invasive techniques (chip-off, head
    # swap, donor parts) ran with no customer consent; there was no field.
    destructive_consent_at = fields.Datetime(
        string="Destructive-Work Consent Recorded At", readonly=True, copy=False
    )
    destructive_consent_by_id = fields.Many2one(
        "res.users", string="Consent Recorded By", readonly=True, copy=False
    )
    destructive_consent_reference = fields.Char(
        string="Customer Consent Reference (OTP / Portal / Form)", readonly=True, copy=False
    )
    destructive_consent_attachment_id = fields.Many2one(
        "ir.attachment", string="Signed Destructive-Work Consent", readonly=True, copy=False
    )
    audit_ids = fields.One2many(
        "fix.z4.access.audit", "case_id", string="Z4 Access Audits", readonly=True
    )
    audit_count = fields.Integer(
        string="Total Access Reads", compute="_compute_audit_count", readonly=True
    )

    # --- A02 Enterprise Data Capture (M06 6-Tab Data Recovery Specification) ---
    form_factor = fields.Selection(
        [
            ("35_desktop", "3.5-inch Desktop HDD"),
            ("25_mobile", "2.5-inch Mobile HDD / SATA SSD"),
            ("m2_nvme", "M.2 NVMe / PCIe Blade"),
            ("nand_monolith", "Monolith Flash / eMMC / UFS BGA"),
            ("enterprise_raid", "Enterprise SAS / Multi-Disk RAID Array"),
        ],
        string="Storage Media Form Factor",
        default="25_mobile",
    )
    interface_type = fields.Selection(
        [
            ("sata", "SATA III (6 Gbps)"),
            ("nvme_pcie", "NVMe PCIe Gen3/Gen4/Gen5"),
            ("sas", "Enterprise SAS"),
            ("usb", "USB 3.x / Type-C Bridge"),
            ("ufs_emmc", "Embedded UFS / eMMC / Apple NAND"),
        ],
        string="Physical Interface Protocol",
        default="sata",
    )
    capacity_gb = fields.Float(string="Raw Storage Capacity (GB)", default=512.0)
    media_serial_number = fields.Char(string="Storage Media Factory S/N", tracking=True)
    firmware_revision = fields.Char(string="Controller / ROM Firmware Version")
    nda_reference = fields.Char(
        string="PDPA / Corporate NDA Reference",
        tracking=True,
    )
    nda_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Signed Confidentiality & NDA Document (PDF)",
    )
    donor_drive_serial = fields.Char(
        string="Matched Donor Drive / Head Stack S/N",
        tracking=True,
    )
    donor_microcode_match = fields.Boolean(
        string="Donor Head-Map & Microcode Verified",
        default=False,
    )
    donor_cost_bdt = fields.Float(
        string="Donor Media Procurement Cost (BDT)",
        default=0.0,
    )
    write_blocker_serial = fields.Char(
        string="Hardware Write-Blocker / PC-3000 Port ID",
        tracking=True,
    )
    # A02 audit M06-P2: free text the P03 form could write. Set only by
    # action_record_image, verified by action_verify_image, then frozen.
    image_sha256_hash = fields.Char(
        string="Bit-Stream Forensic Clone SHA-256 Digest",
        tracking=True,
        readonly=True,
        copy=False,
    )
    recovered_files_count = fields.Integer(
        string="Total Recovered Files Count",
        default=0,
    )
    recovered_volume_gb = fields.Float(
        string="Recovered Data Volume (GB)",
        default=0.0,
    )
    encrypted_target_serial = fields.Char(
        string="Encrypted Handover Target Drive S/N (AES-256)",
    )

    # the media serial is the key a wipe certificate binds to (BRU-DTS-11):
    # once custody is taken it cannot be re-typed to match another certificate
    _FROZEN_AFTER_INTAKE = ("media_serial_number",)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "residency_zone",
            "purge_certificate_id",
            "custody_chain",
            "destructive_consent_at",
            "destructive_consent_by_id",
            "destructive_consent_reference",
            "destructive_consent_attachment_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].state not in (False, "new"):
            locked |= set(self._FROZEN_AFTER_INTAKE)
        return locked

    @api.depends("audit_ids")
    def _compute_audit_count(self):
        for rec in self:
            rec.audit_count = len(rec.audit_ids)

    @api.depends(
        "custody_event_ids",
        "custody_event_ids.description",
        "custody_event_ids.event_at",
    )
    def _compute_custody_chain(self):
        for rec in self:
            lines = [
                "%s (%s): %s"
                % (
                    event.event_at.strftime("%Y-%m-%d %H:%M:%S") if event.event_at else "",
                    event.actor_id.name or "",
                    event.description,
                )
                for event in rec.sudo().custody_event_ids.sorted("id")
            ]
            rec.custody_chain = "\n".join(lines) or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.data.recovery.case") or "DRC/New"
            )
        return super().create(vals_list)

    def write(self, vals):
        frozen = set(self._FROZEN_AFTER_INTAKE) & set(vals)
        if frozen and not self._fix_guard_open():
            for rec in self:
                if rec.state != "new" and any(
                    rec._fix_guard_differs(name, vals[name], rec[name]) for name in frozen
                ):
                    raise UserError(
                        "Case %s is in custody: its media serial number is the key the wipe "
                        "certificate binds to and can no longer be changed." % rec.name
                    )
        return super().write(vals)

    # ------------------------------------------------------------ custody

    def _custody_log(self, action, description, media_unit=None, witness_id=False):
        """Append one event per case to the custody ledger (A02 audit M06-6)."""
        Event = self.env["fix.data.custody.event"]._guarded()
        for rec in self:
            Event.create(
                {
                    "case_id": rec.id,
                    "media_unit_id": media_unit.id if media_unit else False,
                    "action": action,
                    "description": description,
                    "witness_id": witness_id or False,
                }
            )

    def action_take_custody(self, handler=None):
        """The chain of custody begins: every hand-off is logged.

        A02 audit M06-2 (D2): with no state guard this re-opened a PURGED
        case. Custody is taken once, at intake."""
        for rec in self:
            if rec.state != "new":
                raise UserError(
                    "Custody of case %s is taken once, at intake; the case is already '%s'."
                    % (rec.name, rec.state)
                )
            who = (handler or "").strip() or self.env.user.name
            rec._custody_log("custody_taken", f"custody taken by {who}")
            rec._guarded().write({"state": "custody"})
            publish(
                self.env,
                "data_case.custody_taken",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name, "handler": who},
            )

    def action_log_custody_transfer(self, handler, role="Technician", location="Z4 Lab", notes=""):
        """Structured hand-off in chain of custody."""
        for rec in self:
            if rec.state not in ("custody", "recovering", "recovered", "handover"):
                raise UserError(
                    "A custody transfer is logged while the case is held (case %s is '%s')."
                    % (rec.name, rec.state)
                )
            note_str = f" - {notes}" if notes else ""
            rec._custody_log(
                "custody_transfer",
                f"[Custody Transfer] Handed to {handler} ({role}) at {location}{note_str}",
            )
            publish(
                self.env,
                "data_case.custody_transferred",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name, "handler": handler, "location": location},
            )

    def action_route_to_z4(self):
        """SC-007: route the case's recovered-data workspace to Z4.

        A02 audit M06-9: `residency_zone` was a label any user typed to 'z4'
        to satisfy the recovery gate. Only this step sets it now."""
        for rec in self:
            if rec.state not in ("new", "custody"):
                raise UserError(
                    "Z4 routing happens before recovery starts (case %s is '%s')."
                    % (rec.name, rec.state)
                )
            if rec.residency_zone == "z4":
                raise UserError("Case %s is already routed to Z4." % rec.name)
            rec._guarded().write({"residency_zone": "z4"})
            rec._custody_log("routed_z4", "recovered-data workspace routed to Z4")

    def action_record_destructive_consent(self, reference=None, attachment_id=None):
        """Record the customer's consent to destructive or invasive work
        (A02 audit M06-5): a signed consent form attached to the case, or the
        customer's OTP / portal consent reference. Staff cannot consent for
        the customer, so an artefact is always required."""
        for rec in self:
            if rec.state not in ("custody", "recovering"):
                raise UserError(
                    "Destructive-work consent is recorded while the case is held for "
                    "recovery (case %s is '%s')." % (rec.name, rec.state)
                )
            if rec.destructive_consent_at:
                raise UserError("Case %s already has a recorded consent." % rec.name)
            attachment = rec._customer_artefact(attachment_id)
            ref = str(reference or "").strip()
            if not attachment and len(ref) < 6:
                raise UserError(
                    "Case %s: record the customer's consent with an artefact — a signed "
                    "consent form attached to the case, or the customer's OTP / portal "
                    "consent reference (at least 6 characters)." % rec.name
                )
            rec._guarded().write(
                {
                    "destructive_consent_at": fields.Datetime.now(),
                    "destructive_consent_by_id": self.env.uid,
                    "destructive_consent_reference": ref or False,
                    "destructive_consent_attachment_id": attachment.id or False,
                }
            )
            rec.message_post(
                body="Customer consent to destructive / invasive recovery recorded (%s)."
                % ("signed form %s" % attachment.name if attachment else "reference %s" % ref)
            )

    def _customer_artefact(self, attachment_id):
        """The customer's signed document: an attachment ON this record."""
        self.ensure_one()
        if not attachment_id:
            return self.env["ir.attachment"]
        try:
            att = self.env["ir.attachment"].sudo().browse(int(attachment_id)).exists()
        except (TypeError, ValueError):
            att = self.env["ir.attachment"]
        if not att or att.res_model != self._name or att.res_id != self.id or not att.raw:
            raise UserError(
                "The customer's signed document must be a non-empty file attached to %s."
                % self.display_name
            )
        return att

    # ----------------------------------------------------------- recovery

    def action_start_recovery(self):
        for rec in self:
            if rec.state != "custody":
                raise UserError("Recovery starts from custody")
            if rec.residency_zone != "z4":
                raise UserError(
                    "SC-007: recovered data must be routed to Z4 BEFORE "
                    "recovery starts. Not transiently, not in a cache."
                )
            # A02 audit M06-4 (D4): recovery started with no evaluation and no
            # accepted quote, i.e. with no customer approval of the price.
            evaluations = rec.evaluation_ids.filtered("evaluated_at").sorted("evaluated_at")
            if not evaluations:
                raise UserError(
                    "Case %s: complete the free evaluation before recovery starts." % rec.name
                )
            if evaluations[-1].verdict == "unrecoverable":
                raise UserError(
                    "Case %s was evaluated unrecoverable: mark it unrecoverable and return "
                    "the media instead." % rec.name
                )
            if not rec.quote_ids.filtered(lambda q: q.state == "accepted"):
                raise UserError(
                    "Case %s: recovery starts only after the customer has accepted the "
                    "quotation." % rec.name
                )
            rec._z4_assert_assigned("Starting recovery")
            rec._guarded().write({"state": "recovering"})

    def action_recovered(self):
        for rec in self:
            # A02 audit M06-2 (D3): NEW -> RECOVERED in one click.
            if rec.state != "recovering":
                raise UserError(
                    "Only a case in recovery can be marked recovered (case %s is '%s')."
                    % (rec.name, rec.state)
                )
            if not rec.attempt_ids.filtered(lambda a: a.outcome in ("success", "partial")):
                raise UserError("Case %s: no finished recovery attempt recovered data." % rec.name)
            rec._z4_assert_assigned("Marking the data recovered")
            rec._assert_verified_image()
            rec._guarded().write({"state": "recovered"})
            publish(
                self.env,
                "data_case.recovered",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name},
            )

    def action_mark_unrecoverable(self, reason=""):
        """NO RECOVERY (spec 8.1 step 6): return the media, no fee.

        A02 audit M06-7: the KPI and two reports counted this state, but no
        method set it."""
        for rec in self:
            if rec.state not in ("custody", "recovering"):
                raise UserError(
                    "Only a case held for recovery can be marked unrecoverable (case %s is '%s')."
                    % (rec.name, rec.state)
                )
            if rec.attempt_ids.filtered(lambda a: a.outcome == "in_progress"):
                raise UserError("Case %s has an attempt still in progress." % rec.name)
            evaluations = rec.evaluation_ids.filtered("evaluated_at").sorted("evaluated_at")
            judged = evaluations and evaluations[-1].verdict == "unrecoverable"
            failed = rec.attempt_ids.filtered(lambda a: a.outcome in ("failed", "media_damaged"))
            if not (judged or failed):
                raise UserError(
                    "Case %s: an unrecoverable verdict needs an evaluation that says so or a "
                    "failed recovery attempt." % rec.name
                )
            note = " - %s" % reason if reason else ""
            rec._custody_log("unrecoverable", "case marked unrecoverable%s" % note)
            rec._guarded().write({"state": "unrecoverable"})
            # A02 ERP audit M06-F1: billing hears of the outcome (under
            # no-data-no-fee only the donor fee is owed)
            publish(
                self.env,
                "data_case.unrecoverable",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name},
            )

    # action_handover lives in fix_data_case_secure (A02 audit M06-P2): a
    # verified recipient, a signed receipt and the confirmed target drive.

    def action_close(self):
        """CLOSED (spec 8.1 step 9): after the purge, after an unrecoverable
        verdict, or after the customer declined the quotation. Unreachable
        before (A02 audit M06-7)."""
        for rec in self:
            declined = (
                rec.state == "custody"
                and rec.quote_ids.filtered(lambda q: q.state == "declined")
                and not rec.quote_ids.filtered(lambda q: q.state in ("sent", "accepted"))
            )
            if rec.state not in ("purged", "unrecoverable") and not declined:
                raise UserError(
                    "Case %s closes after the purge, an unrecoverable verdict or a declined "
                    "quotation (it is '%s')." % (rec.name, rec.state)
                )
            # A02 ERP audit M06-F9: a purged case closed with the customer's
            # drive still in the lab. Every case closes only once its media
            # went back to the customer or was destroyed under a certificate.
            held = rec.media_unit_ids.filtered(
                lambda u: u.location not in ("returned_to_customer", "destroyed")
            )
            if held:
                raise UserError(
                    "Case %s: return the customer's media first, or destroy it under a "
                    "verified physical-destruction certificate (%s)."
                    % (rec.name, ", ".join(held.mapped("seal_number")))
                )
            rec._custody_log("closed", "case closed")
            rec._guarded().write({"state": "closed"})

    def action_access_recovered_data(
        self,
        step_up_token,
        access_type="file_list_read",
        purpose="Technician File List Inspection",
        ip_address="127.0.0.1",
    ):
        """SC-002: Step-up authentication and per-read access logging for Z4 sovereign data.
        Validates 2FA step-up token and writes an immutable audit log entry."""
        self.ensure_one()
        # A02 audit M06-3: Z4 access is for named custodians, not every user.
        _require_role(self.env, GROUP_Z4_CUSTODIAN, "Z4 Custodian", "Access to Z4 recovered data")
        # ...and the custodian or technician named on THIS case (A02 audit M06-P2)
        self._z4_assert_assigned("Access to Z4 recovered data")
        if self.residency_zone != "z4":
            raise UserError("SC-007: Recovered data exists strictly within Z4 sovereign residency.")
        if self.state not in ("recovering", "recovered", "handover"):
            raise UserError(f"Cannot access recovered data while case is in '{self.state}' state.")

        # Step-up authentication (2FA/TOTP): the ACCESSOR's own auth_totp code,
        # verified cryptographically. There are no fixed bypass tokens and every
        # failure mode is a refusal (fail closed).
        code = str(step_up_token or "").strip()
        if len(code) == 6 and code.isdigit():
            denial = self._step_up_denial(int(code))
        else:
            denial = "a 6-digit authenticator code is required"
        if denial:
            raise UserError(
                "Access Denied: Valid step-up authentication (2FA/TOTP) required "
                f"to access Z4 recovered data (SC-002 / SC-007): {denial}."
            )

        # Per-read immutable audit log, written by this action only (the ACL
        # grants create to no one: A02 audit M06-3)
        audit = (
            self.env["fix.z4.access.audit"]
            .sudo()
            .create(
                {
                    "case_id": self.id,
                    "user_id": self.env.uid,
                    "access_type": access_type,
                    "purpose": purpose,
                    "ip_address": ip_address,
                    "step_up_verified": True,
                }
            )
        )

        publish(
            self.env,
            "data_case.z4_accessed",
            "fix.data.recovery.case",
            self.id,
            {"case": self.name, "audit_id": audit.id, "access_type": access_type},
        )

        # The recovered files ARE the case's stored attachments: the listing
        # reports what is on record (an empty list when nothing is stored),
        # never invented file names or sizes.
        # read with the accessor's own rights (they just passed step-up)
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)], order="id"
        )
        return {
            "status": "granted",
            "audit_hash": audit.sha256_audit_hash,
            "case": self.name,
            "access_type": access_type,
            "files": [
                {"filename": att.name, "size_bytes": att.file_size, "zone": self.residency_zone}
                for att in attachments
            ],
        }

    def _step_up_denial(self, code):
        """Verify a 6-digit TOTP `code` for the acting user through Odoo's
        auth_totp (`_check_credentials` type "totp": the user's own secret,
        rate-limited, replay-protected). Returns None when verified, else the
        reason for refusing. Fails closed when auth_totp is unavailable, the
        user has no TOTP enrolled, or there is no interactive request."""
        user = self.env.user
        if "totp_enabled" not in user._fields:
            return "two-factor authentication (auth_totp) is not available"
        if not user.sudo().totp_enabled:
            return "the accessor has no authenticator (TOTP) enrolled"
        if not request:
            return "step-up verification requires an interactive session"
        try:
            user._check_credentials({"type": "totp", "token": code}, {"interactive": True})
        except AccessDenied as exc:
            return str(exc) or "the authenticator code was not accepted"
        return None

    def _purge_certificate(self, certificate):
        """The certificate a purge closes on: the one passed (a record, an id
        or its reference), the one already linked, or the single verified,
        unused certificate for this case's media serial (A02 audit M06-8: the
        UI had no legitimate way to pass one)."""
        self.ensure_one()
        Cert = self.env["fix.data.wipe.certificate"]
        if isinstance(certificate, models.BaseModel):
            return certificate
        ref = str(certificate or "").strip()
        if ref:
            cert = Cert.browse(int(ref)).exists() if ref.isdigit() else Cert
            cert = cert or Cert.search([("name", "=", ref)], limit=1)
            if not cert:
                raise UserError("No wipe certificate '%s' was found." % ref)
            return cert
        if self.purge_certificate_id:
            return self.purge_certificate_id
        serial = _norm_serial(self.media_serial_number)
        used = self.sudo().search([("purge_certificate_id", "!=", False)]).purge_certificate_id
        matches = Cert.browse()
        if serial:
            matches = (
                Cert.search(
                    [
                        ("sanitization_status", "=", "verified"),
                        ("serial_number", "=ilike", (self.media_serial_number or "").strip()),
                    ]
                ).filtered(lambda c: _norm_serial(c.serial_number) == serial)
                - used
            )
        if len(matches) > 1:
            raise UserError(
                "Several verified certificates match media %s: pass the certificate "
                "reference to purge." % self.media_serial_number
            )
        if not matches:
            raise UserError(
                "Purge needs the wipe operator's fix.data.wipe.certificate "
                "(sector count, method and wipe-tool log)"
            )
        return matches

    def _m06_purge_denial(self, cert) -> str:
        """'' when ``cert`` proves this case's purge, else why not. Refined
        by fix_data_case_a02r2 (A02 pass 2 M06-04, D15)."""
        self.ensure_one()
        return cert._fix_certify_denial(self.media_serial_number)

    def action_purge(self, certificate=None):
        """Close the case on the wipe operator's VERIFIED fix.data.wipe.certificate
        (its evidence - sector count, method, tool log - is entered by the
        operator and hash-verified there). Nothing is certified here: a case
        without a verified certificate cannot be marked purged. The statutory
        processing record is preserved even after the data is destroyed
        (NFR-095: the certificate is statutory_record_retained)."""
        for rec in self:
            if rec.state != "handover":
                raise UserError("Purge from handover")
            cert = rec._purge_certificate(certificate)
            # A02 audit M06-1 (W4, W5): the certificate must still be verified,
            # its log unchanged since verification, and bound to THIS case
            # (A02 pass 2 M06-04: the lab's purge certificate of this case).
            denial = rec._m06_purge_denial(cert)
            if denial:
                raise UserError("Case %s cannot be purged: %s." % (rec.name, denial))
            if rec.sudo().search_count(
                [("purge_certificate_id", "=", cert.id), ("id", "!=", rec.id)]
            ):
                raise UserError(
                    "Wipe certificate %s already closed another case: one certificate "
                    "purges one case." % cert.name
                )
            if not cert.statutory_record_retained:
                raise UserError("NFR-095: the purge certificate must be statutorily retained")
            rec._guarded().write({"state": "purged", "purge_certificate_id": cert.id})
            rec._custody_log("purged", "recovered data purged under certificate %s" % cert.name)
            publish(
                self.env,
                "data_case.purged",
                "fix.data.recovery.case",
                rec.id,
                {"certificate": cert.name, "verification_hash": cert.verification_hash},
            )


class FixDataWipeCertificate(models.Model):
    """The secure data-wipe and destruction certificate (P09-M05-T02).
    Consumed by M14 trade-in and M18 e-waste."""

    _name = "fix.data.wipe.certificate"
    _description = "Data Wipe Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    serial_number = fields.Char(
        string="Storage Media Serial Number",
        help="The one media serial this certificate certifies (BRU-DTS-11): a purge or "
        "release of any other serial is refused.",
    )
    technician_id = fields.Many2one(
        "res.users",
        string="Certifying Technician",
        default=lambda self: self.env.user,
        readonly=True,
    )
    # Operator inputs: nothing defaults to a plausible-looking wipe result.
    method = fields.Selection(WIPE_METHODS, required=True)
    sector_count = fields.Integer(
        string="Total Overwritten Sectors",
        help="As reported by the wipe tool (not applicable to physical destruction)",
    )
    duration_seconds = fields.Integer(string="Sanitization Duration (s)")
    tool_name = fields.Char(string="Wipe Tool / Version")
    wipe_log_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Wipe Tool Output / Log",
        ondelete="restrict",
        help="The wipe tool's report (or destruction evidence) the certificate attests to",
    )
    sanitization_status = fields.Selection(
        [
            ("pending_verification", "Pending Verification"),
            ("verified", "Pass - Evidence Verified"),
            ("failed", "Sanitization Incomplete"),
        ],
        default="pending_verification",
        required=True,
        readonly=True,
        tracking=True,
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(readonly=True)
    # A02 audit M06-1 (W5): the log was swapped after verification and the
    # purge still passed. The evidence hash is pinned when verified; any
    # later change to the log content voids the verification at every gate.
    verified_hash = fields.Char(
        string="Evidence Hash Pinned at Verification", readonly=True, copy=False
    )
    evidence_intact = fields.Boolean(
        string="Evidence Unchanged Since Verification",
        compute="_compute_evidence_intact",
        help="False when the wipe log no longer matches the hash pinned at verification",
    )
    statutory_record_retained = fields.Boolean(
        string="Statutory Processing Record Retained",
        default=True,
        readonly=True,
        help="NFR-095: Preserved permanently in statutory archive even post-purge",
    )
    certified_by = fields.Char(string="Certified By")
    certified_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    verification_hash = fields.Char(
        compute="_compute_verification_hash",
        store=True,
        readonly=True,
        help="SHA-256 over the wipe evidence (tool log content, method, sector "
        "count, media serial): anyone holding the log can re-derive it. Empty "
        "until evidence is attached.",
    )

    _EVIDENCE_FIELDS = (
        "method",
        "sector_count",
        "serial_number",
        "wipe_log_attachment_id",
        "tool_name",
        "duration_seconds",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "sanitization_status",
            "verified_by_id",
            "verified_at",
            "verified_hash",
            "technician_id",
            "statutory_record_retained",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].sanitization_status not in (False, "pending_verification"):
            locked |= set(self._EVIDENCE_FIELDS) | {"device_id"}
        return locked

    def _evidence_digest(self) -> str:
        """sha256 over the actual evidence; '' when there is no log."""
        self.ensure_one()
        log = self.wipe_log_attachment_id
        if not log:
            return ""
        digest = hashlib.sha256()
        digest.update(log.sudo().raw or b"")
        for part in (self.method, self.sector_count, self.serial_number):
            digest.update(b"|" + str(part or "").encode())
        return digest.hexdigest()

    @api.depends("wipe_log_attachment_id", "method", "sector_count", "serial_number")
    def _compute_verification_hash(self):
        for rec in self:
            rec.verification_hash = rec._evidence_digest() or False

    def _compute_evidence_intact(self):
        for rec in self:
            rec.evidence_intact = bool(
                rec.verified_hash and rec.sudo()._evidence_digest() == rec.verified_hash
            )

    @api.model
    def _fix_media_serial(self, device) -> str:
        """The media serial of a registered device (serial number, else IMEI)."""
        return (device.serial_number or device.imei_1 or "") if device else ""

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.data.wipe.certificate") or "DWC/New"
            )
            if not vals.get("certified_by"):
                vals["certified_by"] = self.env.user.name or False
            # a certificate is never BORN verified: verification checks evidence
            for stamp in ("sanitization_status", "verified_by_id", "verified_at", "verified_hash"):
                vals.pop(stamp, None)
            if vals.get("device_id") and not vals.get("serial_number"):
                device = self.env["fix.device"].sudo().browse(vals["device_id"])
                vals["serial_number"] = self._fix_media_serial(device) or False
        records = super().create(vals_list)
        # fix the evidence hash NOW (not lazily at first read): a log edited
        # between attachment and verification is then detected as tampering
        records.mapped("verification_hash")
        return records

    def write(self, vals):
        evidence_change = any(f in vals for f in self._EVIDENCE_FIELDS)
        if evidence_change:
            for rec in self:
                if rec.sanitization_status == "verified":
                    raise UserError(
                        "Certificate %s is verified: its wipe evidence is frozen" % rec.name
                    )
        res = super().write(vals)
        if evidence_change:
            self.mapped("verification_hash")
        return res

    def _evidence_gaps(self) -> list[str]:
        self.ensure_one()
        gaps = []
        if not self.method:
            gaps.append("wipe method")
        if self.method != "physical_destruction" and self.sector_count <= 0:
            gaps.append("overwritten sector count from the wipe tool")
        if not self.wipe_log_attachment_id:
            gaps.append("wipe tool output / log attachment")
        elif not self.wipe_log_attachment_id.sudo().raw:
            gaps.append("a non-empty wipe tool log")
        if not (self.serial_number or "").strip():
            # A02 audit M06-1 (W4): BRU-DTS-11, no blanket certificates
            gaps.append("the media serial number it certifies")
        return gaps

    def _verifier_check(self):
        """A02 audit M06-1 (W3): the operator verified his own certificate.
        Verification needs the wipe-verifier role and a second identity
        (spec 13 SoD, FR-DTS-022): never the technician who recorded it."""
        self.ensure_one()
        _require_role(
            self.env, GROUP_WIPE_VERIFIER, "Wipe Certificate Verifier", "Verifying a certificate"
        )
        if self.env.su:
            return
        user = self.env.user
        if user in (self.technician_id | self.create_uid):
            raise UserError(
                "Segregation of duties: %s recorded certificate %s, so a second, "
                "independent verifier must verify it." % (user.name, self.name)
            )

    def action_verify(self):
        """Verify the certificate against the operator's evidence. Refuses
        (fail closed) when any evidence is missing; the hash is re-derived
        from the stored log content and pinned."""
        for rec in self:
            if rec.sanitization_status != "pending_verification":
                raise UserError(
                    "Only a pending certificate can be verified (%s is '%s')"
                    % (rec.name, rec.sanitization_status)
                )
            rec._verifier_check()
            gaps = rec._evidence_gaps()
            if gaps:
                raise UserError(
                    "Certificate %s cannot be verified - missing: %s" % (rec.name, ", ".join(gaps))
                )
            digest = rec._evidence_digest()
            if rec.verification_hash != digest:
                raise UserError("Certificate %s: evidence hash mismatch" % rec.name)
            rec._guarded().write(
                {
                    "sanitization_status": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                    "verified_hash": digest,
                }
            )
        return True

    def action_mark_failed(self):
        """Erasure could not be verified. A02 ERP audit M06-F22: anyone could
        fail any certificate. It is the verifier's decision, or the operator's
        who recorded the wipe and saw it fail; only a pending certificate."""
        for rec in self:
            if rec.sanitization_status != "pending_verification":
                raise UserError(
                    "Only a certificate awaiting verification can be failed (%s is '%s')."
                    % (rec.name, rec.sanitization_status)
                )
            user = self.env.user
            if not (
                self.env.su
                or user.has_group(GROUP_WIPE_VERIFIER)
                or (user == rec.technician_id and user.has_group(GROUP_OPERATOR))
            ):
                raise AccessError(
                    "Failing wipe certificate %s is for a Wipe Certificate Verifier, or for the "
                    "operator who recorded it." % rec.name
                )
            rec._guarded().write({"sanitization_status": "failed"})
            rec.message_post(body="Marked failed by %s." % user.name)
        return True

    def _fix_failed_before(self):
        """Certificates for the same media serial that failed before this
        one was recorded."""
        self.ensure_one()
        serial = _norm_serial(self.serial_number)
        if not serial:
            return self.browse()
        domain = [("sanitization_status", "=", "failed"), ("serial_number", "!=", False)]
        if self.id:
            domain.append(("id", "<", self.id))
        return (
            self.sudo().search(domain).filtered(lambda c: _norm_serial(c.serial_number) == serial)
        )

    def _fix_certify_denial(self, serial) -> str:
        """'' when this certificate lets the media `serial` be purged or
        released, else why not. Used by the purge and by the M14 trade-in,
        M18 e-waste and rental gates (A02 audit M06-1): verified through
        action_verify, its log unchanged since, and bound to that one serial,
        so one certificate cannot purge or release two different drives."""
        if not self:
            return "no M06 data wipe certificate is attached"
        self.ensure_one()
        cert = self.sudo()
        if cert.sanitization_status != "verified":
            return "wipe certificate %s is '%s', not verified" % (
                cert.name,
                cert.sanitization_status,
            )
        if not (cert.verified_by_id and cert.verified_at and cert.verified_hash):
            return (
                "wipe certificate %s was never verified through its verification step "
                "(no verifier or pinned evidence hash)" % cert.name
            )
        if cert._evidence_digest() != cert.verified_hash:
            return (
                "the wipe log of certificate %s changed after verification, so the "
                "verification is void" % cert.name
            )
        bound, wanted = _norm_serial(cert.serial_number), _norm_serial(serial)
        if not bound:
            return "wipe certificate %s is not bound to a media serial" % cert.name
        if not wanted:
            return "the item has no media serial to match certificate %s against" % cert.name
        if bound != wanted:
            return "wipe certificate %s certifies media %s, not %s" % (
                cert.name,
                cert.serial_number,
                serial,
            )
        # A02 ERP audit M06-F6 (BRU-DTS-10): once erasure of this media failed,
        # only a physical destruction certifies it. A fresh erasure certificate
        # raised without the request released the media all the same.
        failed = cert._fix_failed_before()
        if failed and cert.method != "physical_destruction":
            return (
                "erasure of media %s already failed (certificate %s): only a verified "
                "physical destruction certifies it now (BRU-DTS-10)"
                % (cert.serial_number, ", ".join(failed.mapped("name")))
            )
        return ""

    def _fix_certifies(self, serial) -> bool:
        """True when this certificate certifies the media `serial`."""
        return not self._fix_certify_denial(serial)

    def unlink(self):
        for rec in self:
            if rec.statutory_record_retained:
                raise UserError(
                    "NFR-095: Data Wipe Certificates are permanent statutory processing "
                    "records and cannot be deleted."
                )
        return super().unlink()
