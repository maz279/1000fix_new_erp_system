# fix.device — THE device model (P04-M01-T02/T03).
# Serial number and IMEI uniqueness: a collision at 5 million assets is a
# data-integrity failure, not an edge case. Duplicate detection enforced.
import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

logger = logging.getLogger(__name__)

# A07 audit (2026-11-03), M17-1/M17-2: any internal user could hand a
# customer's device to someone else by writing `owner_id`, and could rewrite a
# serviced phone's IMEI or move it onto another device, leaving no trail - the
# laundering path for a stolen handset. Once set, the owner changes only through
# `action_transfer_ownership` and an identifier only through
# `action_correct_identifier`; first capture at registration stays open.
IDENTIFIER_FIELDS = ("serial_number", "imei_1", "imei_2")

# A07 audit (2026-11-04), P1 roles (M17-17, D7): the spec's §13 roles
# (security/fix_device_registry_groups.xml). The managers imply the agent.
REGISTRY_AGENT_GROUP = "cd_device_registry.group_device_registry_user"
BRANCH_MANAGER_GROUP = "cd_device_registry.group_device_branch_manager"
QUALITY_MANAGER_GROUP = "cd_device_registry.group_device_quality_manager"
# R32 handles identifier conflicts (BRU-AST-05); a corrected serial or IMEI
# is that decision. It was `base.group_system` until the role existed.
IDENTIFIER_CORRECTION_GROUP = QUALITY_MANAGER_GROUP
# A07 audit (2026-11-03), M17-8/M17-3: scrapping a customer's device and
# merging two devices are not money decisions, so they carry no DOFA amount.
# P0 used DOFA Tier 2 as a stand-in. The spec names the Quality Manager for
# both: BRU-AST-04 (merge approval) and §8.1 "End of life -> Recycled".
DEVICE_DECISION_GROUP = QUALITY_MANAGER_GROUP
# A lost or scrapped device is not in anyone's hands to scrap or hand on.
NOT_SCRAPPABLE = ("lost", "scrapped")
# BRU-AST-03: a provisional identity reaches no warranty claim or invoice, and
# is not handed on until it is resolved.
NOT_RESOLVED = ("provisional",)
# A07 P2, business decision B4 (BTRC NEIR de-registration on transfer): on or
# off. Off by default; when on, a transfer marks the device's IMEIs
# "de-registration pending" and publishes device.neir_deregistration_required.
NEIR_ON_TRANSFER_PARAM = "cd_device_registry.neir_deregistration_on_transfer"
LIFECYCLE_STAGES = ("active", "vintage", "end_of_life", "obsolete")
# A07 operability (2026-11-07): which M24 document types can stand as evidence.
# FR-AST-017/018 ask for a supporting document; the transfer picker offered an
# Employment Contract. A sale deed is uploaded on the form (asset_document).
TRANSFER_EVIDENCE_TYPES = ("asset_document", "invoice", "signature_certificate", "evidence_pack")
CUSTODY_EVIDENCE_TYPES = ("custody_photo", "evidence_pack")
WARRANTY_PROOF_TYPES = ("warranty_card", "invoice", "asset_document")


def luhn_ok(digits: str) -> bool:
    """The IMEI check digit (ISO/IEC 7812 Luhn) holds for a 15-digit string."""
    if not digits or not digits.isdigit():
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _strip_identifiers(vals) -> None:
    """Registration trims what the scanner or the clerk padded: ' SN-1 ' and
    'SN-1' are one identifier (spec §8.2 normalised match)."""
    for name in (*IDENTIFIER_FIELDS, "mac_address"):
        value = vals.get(name)
        if isinstance(value, str):
            vals[name] = value.strip() or False


def take_upload(vals, file_field, name_field):
    """Lift a staged file off a form's values: (file, file name), or (None, None).
    The two fields are not stored; the file becomes a governed document."""
    data = vals.pop(file_field, None)
    name = vals.pop(name_field, None)
    return (data, (name or "").strip()) if data else (None, None)


def document_from_upload(env, device, data, filename, doc_type, fallback, res_model, res_id):
    """A file a person uploaded on an M17 form, as the fix.document the evidence
    rules read. Created as the caller, so the document's own ACL applies."""
    name = filename or fallback
    return env["fix.document"].create(
        {
            "name": name,
            "upload_file": data,
            "upload_filename": name,
            "document_type": doc_type,
            "company_id": device.company_id.id or env.company.id,
            "operating_unit_id": device.operating_unit_id.id or False,
            "res_model": res_model,
            "res_id": res_id,
        }
    )


def bind_evidence(doc, records, what: str, types=None) -> None:
    """Evidence must be about THESE records (e.g. the device or its warranty).
    A document filed against another record (a res.partner, another device) is
    refused; an unfiled one is filed against the first record now, so the same
    paper cannot later prove something else (A07 audit M17-13: a "proof" filed
    on another customer verified cover). `types` names the document types that
    can stand as this evidence."""
    doc = doc.sudo().exists()
    if not doc:
        raise UserError("Attach the %s first." % what)
    if types and doc.document_type not in types:
        labels = dict(doc._fields["document_type"].selection)
        raise UserError(
            "%s is a %s document, which cannot serve as %s. Upload the file on this form, or "
            "choose one of type: %s."
            % (
                doc.name,
                labels.get(doc.document_type, doc.document_type),
                what,
                ", ".join(labels[t] for t in types),
            )
        )
    allowed = {(r._name, r.id) for r in records}
    if doc.res_model and doc.res_id:
        if (doc.res_model, doc.res_id) not in allowed:
            raise UserError(
                "The %s %s is filed against another record (%s #%s). Attach a document "
                "for this %s."
                % (what, doc.name, doc.res_model, doc.res_id, records[0]._description)
            )
        return
    doc.write({"res_model": records[0]._name, "res_id": records[0].id})


class FixDevice(models.Model):
    """A physical device registered in the 1000FiX estate.

    The device IS the transacting entity — service orders, warranty claims,
    ownership transfers and device history all reference this record.
    """

    _name = "fix.device"
    _description = "Device"
    # fix.approvable.mixin already carries fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"
    # A device is found by any identifier a person holds, not only its label.
    _rec_names_search = ["name", "serial_number", "imei_1", "imei_2", "legacy_reference"]

    # A07 audit (2026-11-03) M17-8: `state='scrapped'` was a plain write. Scrap
    # is now a routed M63 decision: Request Approval (the reason is the
    # justification), and a Tier 2 holder who neither requested it nor
    # registered the device scraps it from the approval inbox.
    _approval_domain = "device_scrap"
    _approval_apply_method = "action_scrap"
    _approval_group = DEVICE_DECISION_GROUP
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # Every state was writable by any user: scrapped, lost and cleared by
        # the flagger himself, transferred with no ownership row; and a plain
        # archive made a customer's device vanish from the register (M17-8,
        # M17-2). They move only through the actions below, the transfer and
        # the merge; superuser service code stays trusted.
        return super()._fix_guarded_fields() | {
            "state",
            "active",
            "lost_prior_state",
            "lost_reason",
            "lost_flagged_by_id",
            "lost_flagged_at",
            "lost_cleared_by_id",
            "lost_cleared_at",
            "scrapped_by_id",
            "scrapped_at",
            # A07 P1/P2 (2026-11-04) M17-8, BRU-AST-19: the hardware lifecycle
            # stage and end of life move only through action_set_lifecycle_stage
            # (Branch Manager, reason, customer instruction); a provisional
            # identity is confirmed only by action_confirm_identity.
            "lifecycle_stage",
            "end_of_support_date",
            "lifecycle_decided_by_id",
            "lifecycle_decided_at",
            "lifecycle_reason",
            "identity_confirmed_by_id",
            "identity_confirmed_at",
            "identifier_warning",
        }

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    # A07 audit (2026-11-04) M17-6: a device a clerk registered got no
    # operating unit, and the OU rule lets NULL through, so every internal user
    # in every unit read its owner and IMEI (645/695 live devices). A user's
    # registration lands in the user's default unit; superuser service code
    # (portal self-registration, seeds) still sets its own.
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
        default=lambda self: (
            False if self.env.su else self.env.user.default_operating_unit_id.id or False
        ),
    )

    # Identity (T03: uniqueness enforced, duplicates rejected)
    serial_number = fields.Char(
        string="Serial Number",
        index=True,
        tracking=True,
        help="Manufacturer serial number — unique when present",
    )
    imei_1 = fields.Char(
        string="IMEI 1",
        index=True,
        tracking=True,
        help="Primary IMEI for mobile devices — unique when present",
    )
    imei_2 = fields.Char(string="IMEI 2 (Dual SIM)", index=True, tracking=True)
    # FR-AST-003: a failed check digit warns, it does not block capture (live,
    # 47 of 53 IMEIs fail it; many are dummies typed at intake).
    identifier_warning = fields.Char(
        string="Identifier Warning",
        compute="_compute_identifier_warning",
        store=True,
        help="Structural problems with the captured identifiers (IMEI Luhn check digit). "
        "Capture is not blocked; the stewardship list reads this.",
    )
    mac_address = fields.Char(string="MAC Address", index=True)
    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        copy=False,
        help="MIG-03: permanent source system reference (FR-SRM-088)",
    )

    # Classification (references the M37 catalogue kernel)
    device_model_id = fields.Many2one(
        "fix.device.model", string="Device Model", required=True, ondelete="restrict", index=True
    )
    brand_id = fields.Many2one(related="device_model_id.brand_id", store=True, string="Brand")
    device_type = fields.Selection(
        related="device_model_id.device_type", store=True, string="Device Type"
    )

    # Current owner (linked to the party kernel)
    owner_id = fields.Many2one(
        "res.partner",
        string="Current Owner",
        domain=[("is_company", "=", False)],
        tracking=True,
        help="The party currently owning this device",
    )
    purchase_date = fields.Date(string="Purchase Date")
    purchase_channel = fields.Selection(
        [
            ("1000fix", "1000FiX"),
            ("brand_store", "Brand Store"),
            ("third_party", "Third Party"),
            ("online", "Online"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
    )

    # Warranty status (T04: consumed by M09 in Phase 7)
    warranty_id = fields.One2many("fix.warranty", "device_id", string="Warranty")
    warranty_status = fields.Selection(
        [
            ("in_warranty", "In Warranty"),
            ("out_of_warranty", "Out of Warranty"),
            ("extended", "Extended Warranty"),
            ("unknown", "Unknown"),
        ],
        # Not stored: the label depends on today's date, and a stored value froze
        # at the warranty's last write - on 3 Nov 2026 50 devices read
        # "in_warranty" with no running cover (A07 audit M17-5).
        compute="_compute_warranty_status",
        search="_search_warranty_status",
        help="Derived from the warranty record's dates and status",
    )

    # Device state
    state = fields.Selection(
        [
            # A07 P2 (2026-11-04) BRU-AST-03 / FR-AST-005: identified
            # incompletely at intake; usable for intake and diagnosis, blocked
            # from warranty and transfer until action_confirm_identity.
            ("provisional", "Provisional (identity unresolved)"),
            ("registered", "Registered"),
            ("transferred", "Ownership Transferred"),
            ("scrapped", "Scrapped"),
            ("lost", "Lost/Stolen"),
        ],
        default="registered",
        required=True,
        tracking=True,
        index=True,
    )
    # BRU-AST-09: who flagged the device lost and when, and who cleared it -
    # never the same person. The state before the flag is what clearing restores.
    lost_prior_state = fields.Char(string="State Before Lost Flag", readonly=True, copy=False)
    lost_reason = fields.Char(string="Lost / Stolen Report", readonly=True, copy=False)
    lost_flagged_by_id = fields.Many2one(
        "res.users", string="Flagged Lost By", readonly=True, copy=False
    )
    lost_flagged_at = fields.Datetime(string="Flagged Lost At", readonly=True, copy=False)
    lost_cleared_by_id = fields.Many2one(
        "res.users", string="Lost Flag Cleared By", readonly=True, copy=False
    )
    lost_cleared_at = fields.Datetime(string="Lost Flag Cleared At", readonly=True, copy=False)
    scrapped_by_id = fields.Many2one("res.users", string="Scrapped By", readonly=True, copy=False)
    scrapped_at = fields.Datetime(string="Scrapped At", readonly=True, copy=False)
    identity_confirmed_by_id = fields.Many2one(
        "res.users", string="Identity Confirmed By", readonly=True, copy=False
    )
    identity_confirmed_at = fields.Datetime(
        string="Identity Confirmed At", readonly=True, copy=False
    )
    # A07 operability (2026-11-07) FR-AST-005: create honoured state='provisional'
    # but no form could send it. The form sends this choice and the reason.
    register_provisional = fields.Boolean(string="Register as Provisional", store=False)
    provisional_reason = fields.Char(
        string="Why the Identity Is Unconfirmed",
        copy=False,
        help="Recorded at registration: why neither a serial nor an IMEI could be confirmed.",
    )
    # A07 operability (2026-11-07) BRU-AST-05: the correction the Quality Manager
    # stages on the asset form; Correct Identifier checks and clears it.
    correction_field = fields.Selection(
        [
            ("serial_number", "Serial Number"),
            ("imei_1", "IMEI 1"),
            ("imei_2", "IMEI 2"),
        ],
        string="Identifier to Correct",
        copy=False,
    )
    correction_value = fields.Char(string="Corrected Value", copy=False)
    correction_reason = fields.Char(string="Correction Reason", copy=False)

    # A07 P1 (2026-11-04) M17-1, FR-AST-017/018: the transfer the P03 asset form
    # stages. A user fills the recipient, reason and evidence, then presses
    # Transfer Ownership; the action checks them and clears them.
    transfer_to_partner_id = fields.Many2one(
        "res.partner", string="Transfer To", copy=False, help="The acquiring party."
    )
    transfer_type_pending = fields.Selection(
        [
            ("sale", "Sale"),
            ("gift", "Gift"),
            ("return", "Return"),
            ("corporate", "Corporate Reallocation"),
        ],
        string="Transfer Type",
        copy=False,
    )
    transfer_reason = fields.Char(string="Transfer Reason", copy=False)
    transfer_evidence_document_id = fields.Many2one(
        "fix.document",
        string="Transfer Evidence",
        copy=False,
        help="The sale receipt, deed or signed hand-over that supports the transfer.",
    )
    # A07 operability (2026-11-07): the only live evidence was six seeded rows.
    # A file uploaded here becomes the fix.document above.
    transfer_evidence_file = fields.Binary(string="Upload Transfer Evidence", store=False)
    transfer_evidence_filename = fields.Char(string="Evidence File Name", store=False)

    # Branch scope
    branch_id = fields.Many2one("fix.branch", string="Registered At")

    # History (T07: every service order, permanently)
    history_ids = fields.One2many("fix.device.history", "device_id", string="Device History")

    # Documents (T06: through the M24-core attachment API)
    document_ids = fields.One2many(
        "fix.document", "res_id", domain=[("res_model", "=", "fix.device")], string="Documents"
    )

    # M17 W2 Completion Slice: Device Lifecycle Management
    lifecycle_stage = fields.Selection(
        [
            ("active", "Active Lifecycle"),
            ("vintage", "Vintage (Limited Parts Support)"),
            ("end_of_life", "End of Life (No OEM Parts)"),
            ("obsolete", "Obsolete / Recycle Only"),
        ],
        default="active",
        required=True,
        tracking=True,
        help="M17 W2: device hardware lifecycle progression affecting spare parts availability",
    )
    end_of_support_date = fields.Date(string="End of Support Date", tracking=True)
    # BRU-AST-19 / FR-AST-048: who decided the stage, why, and (end of life of a
    # customer-owned device) what the customer instructed.
    lifecycle_decided_by_id = fields.Many2one(
        "res.users", string="Lifecycle Decided By", readonly=True, copy=False
    )
    lifecycle_decided_at = fields.Datetime(string="Lifecycle Decided At", readonly=True, copy=False)
    lifecycle_reason = fields.Char(string="Lifecycle Decision Basis", readonly=True, copy=False)
    eol_customer_instruction = fields.Selection(
        [
            ("refurbish", "Customer agreed: refurbish and resell (M14)"),
            ("recycle", "Customer agreed: recycle / dispose (M18)"),
            ("return_as_is", "Customer takes it back unrepaired"),
        ],
        string="Customer End-of-Life Instruction",
        copy=False,
        help="Required before a customer-owned device is made obsolete (BRU-AST-19).",
    )
    estimated_residual_value_bdt = fields.Monetary(
        string="Estimated Residual Value (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: (
            self.env.ref("base.BDT", raise_if_not_found=False) or self.env.company.currency_id
        ),
    )

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char(compute="_compute_name", store=True)

    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _serial_unique_when_set = models.Constraint(
        "UNIQUE (serial_number)", "This serial number is already registered (duplicate detection)."
    )
    _imei1_unique_when_set = models.Constraint(
        "UNIQUE (imei_1)", "This IMEI is already registered (duplicate detection)."
    )

    @api.depends("device_model_id", "serial_number")
    def _compute_name(self):
        for rec in self:
            parts = [rec.device_model_id.name or "Device"]
            if rec.serial_number:
                parts.append(f"S/N {rec.serial_number}")
            rec.name = " — ".join(parts)

    @api.depends("warranty_id.end_date", "warranty_id.status")
    def _compute_warranty_status(self):
        # `datetime.date.today()` - the DEVELOPER MACHINE's date - decided the
        # warranty label every user reads, while `is_under_warranty` (the gate
        # that accepts or refuses the order) decides on the Bangladesh date.
        # The two disagreed for the first six hours of every Dhaka day: a device
        # could read "in_warranty" and still be refused a warranty order, with
        # the refusal quoting the contradictory label back at the user
        # (A04 audit, 2026-11-01). One date basis, and it is the business's.
        for rec in self:
            today = fields.Date.context_today(rec)
            # Any running active warranty wins: the old loop stopped at the FIRST
            # active record in iteration order, so an expired-by-date record read
            # before a running one made a covered device "out_of_warranty".
            active = rec.warranty_id.filtered(lambda w: w.status == "active")
            if any(w.end_date and w.end_date >= today for w in active):
                rec.warranty_status = "in_warranty"
            elif active:
                rec.warranty_status = "out_of_warranty"
            else:
                rec.warranty_status = "unknown"

    def _search_warranty_status(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            raise UserError("Unsupported search on Warranty Status: %s" % operator)
        wanted = {value} if operator in ("=", "!=") else set(value or ())
        today = fields.Date.context_today(self)
        Warranty = self.env["fix.warranty"].sudo().with_context(active_test=False)
        active = Warranty.search([("status", "=", "active")])
        running = set(active.filtered(lambda w: w.end_date and w.end_date >= today).device_id.ids)
        with_active = set(active.device_id.ids)
        ids = set()
        if "in_warranty" in wanted:
            ids |= running
        if "out_of_warranty" in wanted:
            ids |= with_active - running
        domain = [("id", "in", list(ids))]
        if "unknown" in wanted:
            domain = ["|", ("id", "not in", list(with_active)), *domain]
        return ["!", *domain] if operator in ("!=", "not in") else domain

    def init(self):
        # The normalised serial match below runs on every registration; at the
        # spec's 5 million assets it needs its own index.
        self.env.cr.execute(
            "CREATE INDEX IF NOT EXISTS fix_device_serial_norm_idx "
            "ON fix_device (upper(btrim(serial_number))) WHERE serial_number IS NOT NULL"
        )

    @api.constrains("serial_number", "imei_1", "imei_2")
    def _check_identity_format(self):
        # A07 audit M17-9: IMEI-2 had no format check ("NOT-AN-IMEI" stored).
        for rec in self:
            for name in ("imei_1", "imei_2"):
                value = rec[name]
                if value and (not value.isdigit() or len(value) != 15):
                    raise ValidationError(
                        f"IMEI must be exactly 15 digits, got {len(value)}: {value}"
                    )
            if rec.imei_1 and rec.imei_1 == rec.imei_2:
                raise ValidationError("IMEI 1 and IMEI 2 of one device cannot be the same.")

    @api.constrains("serial_number", "imei_1", "imei_2")
    def _check_identifier_collisions(self):
        """BRU-AST-05: one identifier never resolves to two assets. The DB
        UNIQUE keys caught only the exact same field: 'a7-dupe' and ' A7-DUPE '
        registered beside 'A7-DUPE', and one device's IMEI-2 was another's
        IMEI-1 (A07 audit M17-9). Checked in SQL across archived devices too,
        as the UNIQUE keys are, so a device the user cannot see still counts."""
        self.flush_model(["serial_number", "imei_1", "imei_2"])
        cr = self.env.cr
        for rec in self:
            if rec.serial_number:
                cr.execute(
                    "SELECT id FROM fix_device WHERE id != %s AND serial_number IS NOT NULL "
                    "AND upper(btrim(serial_number)) = upper(btrim(%s)) LIMIT 1",
                    (rec.id, rec.serial_number),
                )
                if cr.fetchone():
                    raise ValidationError(
                        "Serial number %s is already registered on another device (a case or "
                        "spacing variant of the same identifier)." % rec.serial_number
                    )
            imeis = [v for v in (rec.imei_1, rec.imei_2) if v]
            if imeis:
                cr.execute(
                    "SELECT id FROM fix_device WHERE id != %s "
                    "AND (imei_1 = ANY(%s) OR imei_2 = ANY(%s)) LIMIT 1",
                    (rec.id, imeis, imeis),
                )
                if cr.fetchone():
                    raise ValidationError(
                        "IMEI %s is already registered on another device. One IMEI resolves "
                        "to one asset (BRU-AST-05): raise an identity resolution instead."
                        % ", ".join(imeis)
                    )

    @api.depends("imei_1", "imei_2")
    def _compute_identifier_warning(self):
        for rec in self:
            warnings = [
                "%s fails the IMEI check digit (Luhn)" % label
                for label, value in (("IMEI 1", rec.imei_1), ("IMEI 2", rec.imei_2))
                if value and value.isdigit() and len(value) == 15 and not luhn_ok(value)
            ]
            rec.identifier_warning = "; ".join(warnings) or False

    def _check_estate_belongs_to_owner(self):
        """A07 audit M17-14: an individual's device sat in another client's
        corporate estate, so the estate's contract covered a device the client
        does not own (60/60 live). A device joins an estate only when its owner
        is the estate's client or one of its contacts. Called from a user's
        create/write (constraints run as superuser, so this is not one);
        superuser service code (migration, the party-merge consumer) is trusted."""
        for rec in self.filtered("estate_id"):
            if not rec._owner_is(rec.estate_id.client_id):
                raise ValidationError(
                    "%s belongs to %s, not to %s, so it cannot sit in the estate %s."
                    % (
                        rec.display_name,
                        rec.owner_id.name or "nobody",
                        rec.estate_id.client_id.name,
                        rec.estate_id.name,
                    )
                )

    def _owner_is(self, partner) -> bool:
        """The device's owner is `partner` or a contact of the same commercial
        entity (an employee of the corporate client)."""
        self.ensure_one()
        owner = self.owner_id
        return bool(
            owner and partner and owner.commercial_partner_id == partner.commercial_partner_id
        )

    # Events (T08)
    @api.model_create_multi
    def create(self, vals_list):
        provisional = []
        uploads = []
        trusted = self._fix_guard_open()
        for vals in vals_list:
            _strip_identifiers(vals)
            uploads.append(
                take_upload(vals, "transfer_evidence_file", "transfer_evidence_filename")
            )
            if vals.pop("register_provisional", False):
                vals["state"] = "provisional"
            is_provisional = vals.get("state") == "provisional"
            if not is_provisional:
                vals.pop("provisional_reason", None)
            if not trusted:
                self._check_registration(vals, is_provisional)
            self._refuse_merged_identifiers(vals)
            # A provisional identity is a registration choice, not a forged
            # state: the guard would refuse a non-default state, so it is set
            # through the transition right after the insert.
            flag = is_provisional and not trusted
            if flag:
                vals.pop("state")
            provisional.append(flag)
        records = super().create(vals_list)
        if not self.env.su:
            records._check_estate_belongs_to_owner()
        for rec, flag, upload in zip(records, provisional, uploads, strict=True):
            if flag:
                rec._guarded().write({"state": "provisional"})
                rec.message_post(
                    body="Registered as provisional by %s: %s"
                    % (self.env.user.name, rec.provisional_reason)
                )
            if upload[0]:
                rec._attach_transfer_evidence(*upload)
            rec._identifier_capture(IDENTIFIER_FIELDS, "registration")
            self._emit("device.registered", rec)
            if rec.state == "provisional":
                rec._publish(
                    "device.provisional_raised",
                    {
                        "device_id": rec.id,
                        "branch_id": rec.branch_id.id or None,
                        "missing": [n for n in IDENTIFIER_FIELDS if not rec[n]],
                    },
                )
        return records

    @api.model
    def _check_registration(self, vals, is_provisional):
        """A07 operability M17-20: a device saved in Registered with no identifier
        at all, so nothing could ever find it again. Service code is trusted."""
        if is_provisional:
            if not (vals.get("provisional_reason") or "").strip():
                raise UserError(
                    "Say why the identity cannot be confirmed before registering the device as "
                    "provisional."
                )
            return
        if not (vals.get("serial_number") or vals.get("imei_1") or vals.get("imei_2")):
            raise UserError(
                "Give the serial number or an IMEI. If neither can be read, register the device "
                "as provisional and say why."
            )

    def _attach_transfer_evidence(self, data, filename):
        self.ensure_one()
        doc = document_from_upload(
            self.env,
            self,
            data,
            filename,
            "asset_document",
            "Transfer evidence - %s" % self.display_name,
            self._name,
            self.id,
        )
        self.write({"transfer_evidence_document_id": doc.id})
        return doc

    def _merge_survivor(self):
        """The active device this merged duplicate now lives on, following a
        chain of merges. Empty when it was not merged, or the merge was reversed."""
        self.ensure_one()
        Merge = self.env["fix.device.merge"].sudo()
        device = self.sudo().with_context(active_test=False)
        for _hop in range(20):
            if device.active:
                return device
            row = Merge.search(
                [("merged_id", "=", device.id), ("state", "=", "merged")],
                order="merged_at desc, id desc",
                limit=1,
            )
            if not row:
                break
            device = row.survivor_id.with_context(active_test=False)
        return self.browse()

    def _refuse_merged_identifiers(self, vals):
        """A07 operability: a merged duplicate keeps its identifiers, and the
        unique keys count archived rows, so a later intake of that phone met a
        bare "duplicate" refusal that named nothing. A person is told which
        device it now is. Service code falls through to the same database keys,
        so a customer on the portal is not told about another record."""
        if self.env.su:
            return
        serial = vals.get("serial_number") or None
        imeis = [v for v in (vals.get("imei_1"), vals.get("imei_2")) if v]
        if not serial and not imeis:
            return
        self.flush_model(["serial_number", "imei_1", "imei_2", "active"])
        self.env.cr.execute(
            "SELECT id FROM fix_device WHERE active IS NOT TRUE AND id != ALL(%s) AND ("
            "(%s::varchar IS NOT NULL AND upper(btrim(serial_number)) = upper(btrim(%s::varchar))) "
            "OR imei_1 = ANY(%s::varchar[]) OR imei_2 = ANY(%s::varchar[])) ORDER BY id DESC",
            (list(self.ids), serial, serial, imeis, imeis),
        )
        for (dup_id,) in self.env.cr.fetchall():
            dup = self.sudo().with_context(active_test=False).browse(dup_id)
            survivor = dup._merge_survivor()
            if survivor:
                raise UserError(
                    "This identifier belongs to %s, which was merged into %s. Use %s; it is not "
                    "registered again." % (dup.name, survivor.display_name, survivor.display_name)
                )

    def _fix_locked_identity(self, vals) -> set:
        """The owner/identifier fields in ``vals`` that would CHANGE a value
        already set on one of these devices. Filling an empty one is first
        capture (registration, or the first IMEI read at intake) and stays open."""
        names = {"owner_id", *IDENTIFIER_FIELDS} & set(vals)
        return {
            name
            for rec in self
            for name in names
            if rec[name] and rec._fix_guard_differs(name, vals[name], rec[name])
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1:
            locked |= {n for n in ("owner_id", *IDENTIFIER_FIELDS) if self[n]}
            # recorded once, at registration
            locked |= {"register_provisional", "provisional_reason"}
        return locked

    def write(self, vals):
        _strip_identifiers(vals)
        upload = take_upload(vals, "transfer_evidence_file", "transfer_evidence_filename")
        vals.pop("register_provisional", None)
        # First capture of an empty identifier (the IMEI read at intake) is
        # recorded in the identifier history; a correction records itself.
        captured = {
            rec.id: [n for n in IDENTIFIER_FIELDS if vals.get(n) and not rec[n]] for rec in self
        }
        if not self._fix_guard_open():
            locked = self._fix_locked_identity(vals)
            if "owner_id" in locked:
                raise UserError(
                    "The owner of a device changes only through an ownership transfer, "
                    "which records who it passed from and to."
                )
            if locked:
                raise UserError(
                    "%s of a registered device cannot be overwritten. Use the identifier "
                    "correction, which needs a reason and keeps the old value on record."
                    % ", ".join(sorted(self._fields[n].string for n in locked))
                )
            if "provisional_reason" in vals and any(
                rec._fix_guard_differs(
                    "provisional_reason", vals["provisional_reason"], rec.provisional_reason
                )
                for rec in self
            ):
                raise UserError("The provisional reason is recorded at registration.")
        if len(self) == 1:
            self._refuse_merged_identifiers(vals)
        result = super().write(vals)
        if upload[0]:
            for rec in self:
                rec._attach_transfer_evidence(*upload)
        if not self.env.su and vals.get("estate_id"):
            self._check_estate_belongs_to_owner()
        for rec in self:
            if captured.get(rec.id):
                rec._identifier_capture(captured[rec.id], "capture")
        if "owner_id" in vals:
            for rec in self:
                self._emit("device.transferred", rec)
        if "warranty_id" in vals:
            for rec in self:
                self._emit("device.warranty_updated", rec)
        return result

    def _assert_role(self, xmlid, what):
        """Superuser service code is trusted; a user needs the spec's role."""
        if self.env.su or self.env.user.has_group(xmlid):
            return
        group = self.env.ref(xmlid, raise_if_not_found=False)
        raise AccessError(
            "%s needs the %s role, which %s does not hold."
            % (what, group.sudo().name if group else xmlid, self.env.user.name)
        )

    def _assert_handable(self, what):
        """BRU-AST-09 / BRU-AST-03: nothing is handed on while the device is
        lost, stolen, scrapped, provisional or blocked on the NEIR register."""
        for rec in self:
            if rec.state in NOT_SCRAPPABLE or rec.state in NOT_RESOLVED:
                raise UserError(
                    "%s is %s and cannot %s." % (rec.display_name, rec._state_label(), what)
                )
            rec._neir_assert_not_blocked(what)

    def assert_identity_resolved(self, what="be used for this"):
        """BRU-AST-03 for M01/M09: a provisional identity reaches no warranty
        claim or customer invoice. Callers name what they were about to do."""
        for rec in self:
            if rec.state in NOT_RESOLVED:
                raise UserError(
                    "%s has a provisional identity and cannot %s until its identity is "
                    "confirmed (BRU-AST-03)." % (rec.display_name, what)
                )
        return True

    def action_transfer_ownership(
        self,
        new_owner_id=None,
        transfer_type=None,
        notes=None,
        reason=None,
        evidence_document_id=None,
        channel=None,
        evidence_file=None,
        evidence_filename=None,
    ):
        """Transfer ownership (T05: portal P01 exposes this in Phase 5).

        BRU-AST-09: a device flagged lost/stolen or scrapped is never handed on.
        The owner and the ownership trail are written together, through the guard,
        so neither can be changed without the other.

        A07 audit (2026-11-04) M17-1, FR-AST-017/018: any internal user ran this
        with no reason, no evidence and no role. A user now needs the Device
        Registry Agent role, a reason and a supporting evidence document (sale
        receipt, deed, signed hand-over), filed against this device and not used
        for another transfer; and a technician never re-owns a device in his own
        custody (§13). No acceptance by the new owner is recorded: the spec asks
        for the evidence, and a separate acceptance step does not exist.
        Superuser service code is trusted: the customer portal transfers as the
        authenticated owner, whose own request is the evidence.

        With no arguments it takes the transfer staged on the device (the P03
        asset form: Transfer To, Type, Reason, Evidence).

        M17 capture audit (2026-11-13): the Ownership & Custody page records a
        transfer in one step (pick the device, then fill the transfer), so the
        evidence may also arrive as an uploaded file (``evidence_file``), filed
        on this device exactly as the asset form's upload is."""
        self.ensure_one()
        if evidence_file and not evidence_document_id:
            evidence_document_id = self._attach_transfer_evidence(
                evidence_file, (evidence_filename or "").strip() or "transfer-evidence"
            ).id
        staged = not new_owner_id
        new_owner_id = new_owner_id or self.transfer_to_partner_id.id
        transfer_type = transfer_type or self.transfer_type_pending
        if not transfer_type:
            # A blank type on the form read as a sale nobody declared.
            if staged:
                raise UserError("Choose the Transfer Type on the asset form.")
            transfer_type = "sale"
        reason = (reason or notes or self.transfer_reason or "").strip()
        evidence = self.env["fix.document"]
        if evidence_document_id:
            evidence = evidence.browse(int(evidence_document_id))
        elif self.transfer_evidence_document_id:
            evidence = self.transfer_evidence_document_id
        if self.state in ("lost", "scrapped"):
            raise UserError(
                "%s is %s and cannot change owner."
                % (self.display_name, dict(self._fields["state"].selection)[self.state])
            )
        self._assert_handable("change owner")
        new_owner = self.env["res.partner"].browse(int(new_owner_id or 0)).exists()
        if not new_owner:
            raise UserError(
                "Name the new owner%s." % (" in Transfer To on the asset form" if staged else "")
            )
        old_owner = self.owner_id
        if old_owner == new_owner:
            raise UserError("%s already belongs to %s." % (self.display_name, new_owner.name))
        if not self.env.su:
            self._assert_role(REGISTRY_AGENT_GROUP, "Recording an ownership transfer")
            if not reason:
                raise UserError("Give the reason for the ownership transfer.")
            if not evidence:
                raise UserError(
                    "Attach the transfer evidence (sale receipt, deed or signed hand-over) "
                    "before transferring %s." % self.display_name
                )
            bind_evidence(evidence, [self], "transfer evidence", TRANSFER_EVIDENCE_TYPES)
            used = (
                self.env["fix.device.ownership"]
                .sudo()
                .search([("evidence_document_id", "=", evidence.id)], limit=1)
            )
            if used:
                raise UserError(
                    "%s already supports the transfer of %s on %s. Each transfer needs its own "
                    "evidence." % (evidence.sudo().name, used.device_id.name, used.transfer_date)
                )
            self._assert_not_own_custody()
        vals = {
            "owner_id": new_owner.id,
            "state": "transferred",
            "transfer_to_partner_id": False,
            "transfer_type_pending": False,
            "transfer_reason": False,
            "transfer_evidence_document_id": False,
        }
        if self.estate_id and not self._owner_is_partner(new_owner, self.estate_id.client_id):
            # The new owner is outside the corporate client: the device leaves
            # the estate with its owner (FR-AST-038 placement ends).
            vals["estate_id"] = False
        self._guarded().write(vals)
        today = fields.Date.context_today(self)
        row = (
            self.env["fix.device.ownership"]
            ._guarded()
            .create(
                {
                    "device_id": self.id,
                    "from_partner_id": old_owner.id if old_owner else False,
                    "to_partner_id": new_owner.id,
                    "transfer_date": today,
                    "transfer_type": transfer_type,
                    "notes": notes,
                    "reason": reason or False,
                    "evidence_document_id": evidence.id or False,
                    "recorded_by_id": self.env.uid,
                    "channel": channel or ("system" if self.env.su else "back_office"),
                }
            )
        )
        # A scrap requested for the old owner's device is not the new owner's.
        self._approval_void("the device changed owner while scrap approval was pending")
        self._neir_on_transfer(old_owner, new_owner)
        self._publish(
            "device.ownership_transferred",
            {
                "device_id": self.id,
                "ownership_id": row.id,
                "from_owner_id": old_owner.id or None,
                "to_owner_id": new_owner.id,
                "transfer_type": transfer_type,
                "reason": reason or None,
                "effective_date": str(today),
                "evidence_document_id": evidence.id or None,
                "recorded_by": self.env.uid,
            },
        )
        return True

    @staticmethod
    def _owner_is_partner(owner, partner) -> bool:
        return bool(
            owner and partner and owner.commercial_partner_id == partner.commercial_partner_id
        )

    def _assert_not_own_custody(self):
        """§13 SoD: a technician may not change the ownership of an asset in
        their own custody (the latest custody event names them custodian)."""
        last = (
            self.env["fix.device.custody"]
            .sudo()
            .search([("device_id", "=", self.id)], order="event_date desc, id desc", limit=1)
        )
        if last and last.custodian_id.user_id == self.env.user:
            raise UserError(
                "Segregation of duties: %s is in your custody (%s), so someone else records "
                "its ownership transfer." % (self.display_name, last.name)
            )

    def action_correct_identifier(self, field_name=None, value=None, reason=None):
        """Privileged correction of a serial number or IMEI (e.g. a board swap or
        a mis-keyed intake). The old value stays in the identifier history
        (fix.device.identifier, superseded with the reason) and the chatter.

        A07 operability (2026-11-07): the form note and the refusal sent a person
        here, and no button or surface reached it. With no arguments it takes the
        correction staged on the asset form (which identifier, value, reason)."""
        self.ensure_one()
        if not self.env.su and not self.env.user.has_group(IDENTIFIER_CORRECTION_GROUP):
            raise AccessError(
                "Only a Device Quality Manager can correct a device identifier (BRU-AST-05)."
            )
        staged = not field_name
        field_name = field_name or self.correction_field
        value = value if not staged else self.correction_value
        reason = reason or (self.correction_reason if staged else None)
        if staged and not field_name:
            raise UserError(
                "Choose which identifier to correct under Identifier Correction on the asset form."
            )
        if field_name not in IDENTIFIER_FIELDS:
            raise UserError("Only the serial number and IMEIs are corrected this way.")
        if not (reason or "").strip():
            raise UserError("A reason is required to correct a device identifier.")
        if staged and not (value or "").strip():
            raise UserError("Type the new value under Identifier Correction on the asset form.")
        old = self[field_name]
        if not old:
            raise UserError(
                "%s is empty: capture it on the asset form; a correction replaces a value."
                % self._fields[field_name].string
            )
        value = (value or "").strip() or False
        self._refuse_merged_identifiers({field_name: value})
        self._guarded().write(
            {
                field_name: value,
                "correction_field": False,
                "correction_value": False,
                "correction_reason": False,
            }
        )
        self._identifier_supersede(field_name, old, value, reason.strip())
        self.message_post(
            body="%s corrected from %s to %s. Reason: %s"
            % (self._fields[field_name].string, old or "(empty)", value or "(empty)", reason)
        )
        self._publish(
            "device.identifier_corrected",
            {
                "device_id": self.id,
                "identifier_type": field_name,
                "old_value": old,
                "new_value": value or None,
                "reason": reason.strip(),
                "corrected_by": self.env.uid,
            },
        )
        return True

    def action_confirm_identity(self):
        """Provisional -> Registered (spec §8.1): an agent confirms the
        identity once a verified identifier is captured."""
        for rec in self:
            if rec.state != "provisional":
                raise UserError("Only a provisional identity is confirmed.")
            rec._assert_role(REGISTRY_AGENT_GROUP, "Confirming a device identity")
            if not (rec.serial_number or rec.imei_1 or rec.imei_2):
                raise UserError(
                    "Capture the serial number or an IMEI of %s before confirming its identity."
                    % rec.display_name
                )
            rec._guarded().write(
                {
                    "state": "registered",
                    "identity_confirmed_by_id": self.env.uid,
                    "identity_confirmed_at": fields.Datetime.now(),
                }
            )
            rec._publish(
                "device.identity_confirmed",
                {
                    "device_id": rec.id,
                    "serial_number": rec.serial_number or None,
                    "imei_1": rec.imei_1 or None,
                    "confirmed_by": self.env.uid,
                },
            )
        return True

    def action_set_lifecycle_stage(self, stage=None, reason=None):
        """Move the hardware lifecycle stage (BRU-AST-19, FR-AST-048).

        A07 audit M17-8: `lifecycle_stage='obsolete'` was a plain write with no
        decision or approver. Now a Branch Manager decides it with a reason,
        and a customer-owned device is made obsolete only with the customer's
        instruction recorded on the asset. Obsolete is final."""
        if stage not in LIFECYCLE_STAGES:
            raise UserError("Unknown lifecycle stage %r." % (stage,))
        if not (reason or "").strip():
            raise UserError("Give the basis for the lifecycle decision.")
        labels = dict(self._fields["lifecycle_stage"].selection)
        for rec in self:
            rec._assert_role(BRANCH_MANAGER_GROUP, "Setting a device's lifecycle stage")
            if rec.lifecycle_stage == stage:
                raise UserError("%s is already %s." % (rec.display_name, labels[stage]))
            if rec.lifecycle_stage == "obsolete":
                raise UserError("%s is obsolete; that decision is final." % rec.display_name)
            if stage == "obsolete" and rec.owner_id and not rec.eol_customer_instruction:
                raise UserError(
                    "%s belongs to %s: record the customer's end-of-life instruction first "
                    "(BRU-AST-19)." % (rec.display_name, rec.owner_id.name)
                )
            old = rec.lifecycle_stage
            vals = {
                "lifecycle_stage": stage,
                "lifecycle_decided_by_id": self.env.uid,
                "lifecycle_decided_at": fields.Datetime.now(),
                "lifecycle_reason": reason.strip(),
            }
            if stage in ("end_of_life", "obsolete") and not rec.end_of_support_date:
                vals["end_of_support_date"] = fields.Date.context_today(rec)
            rec._guarded().write(vals)
            rec.message_post(
                body="Lifecycle %s -> %s by %s: %s"
                % (labels[old], labels[stage], self.env.user.name, reason.strip())
            )
            rec._publish(
                "device.lifecycle_changed",
                {
                    "device_id": rec.id,
                    "from_stage": old,
                    "to_stage": stage,
                    "reason": reason.strip(),
                    "customer_instruction": rec.eol_customer_instruction or None,
                    "decided_by": self.env.uid,
                },
            )
        return True

    # P03 buttons: one typed value (the reason) per action.
    def action_set_vintage(self, reason=None):
        return self.action_set_lifecycle_stage("vintage", reason)

    def action_set_end_of_support(self, reason=None):
        return self.action_set_lifecycle_stage("end_of_life", reason)

    def action_set_obsolete(self, reason=None):
        return self.action_set_lifecycle_stage("obsolete", reason)

    def action_return_to_active(self, reason=None):
        """A vintage device whose parts supply came back (a Branch Manager, with
        a basis). End of life and obsolete do not come back this way."""
        for rec in self:
            if rec.lifecycle_stage != "vintage":
                raise UserError(
                    "%s is not vintage; only a vintage device returns to active." % rec.display_name
                )
        return self.action_set_lifecycle_stage("active", reason)

    # ---- lifecycle actions (A07 audit 2026-11-03, M17-8 / M17-2) ----------
    def _state_label(self):
        return dict(self._fields["state"].selection).get(self.state, self.state)

    def action_mark_lost(self, reason=None):
        """Flag the device lost or stolen (BRU-AST-09). Any internal user may
        raise the flag - holding a reported device is the safe side - but who
        and when are stamped, and someone else must clear it."""
        if not (reason or "").strip():
            raise UserError("Say how the loss or theft was reported.")
        for rec in self:
            if rec.state in NOT_SCRAPPABLE:
                raise UserError("%s is already %s." % (rec.display_name, rec._state_label()))
            rec._flag_lost(reason.strip(), "registry")
            rec._custody_flag_event("lost", reason.strip())
        return True

    def _custody_flag_event(self, event, note):
        """A07 operability M17-12: the flag and its clearance reach the custody
        chain, which said nothing of a device flagged from the registry. The last
        custodian is carried over, so a flag cannot wipe the check that a
        technician never re-owns a device in his own custody."""
        self.ensure_one()
        Custody = self.env["fix.device.custody"].sudo()
        last = Custody.search(
            [("device_id", "=", self.id)], order="event_date desc, id desc", limit=1
        )
        Custody._guarded().create(
            {
                "device_id": self.id,
                "event": event,
                "custodian_id": last.custodian_id.id or False,
                "reference": "Registry flag",
                "notes": note,
            }
        )

    def _flag_lost(self, reason, source):
        """Put the device in the lost/stolen register (FR-AST-023), from the
        registry button or a 'Reported Lost' custody event (A07 audit M17-4:
        custody said lost while the registry said registered)."""
        self.ensure_one()
        self._guarded().write(
            {
                "lost_prior_state": self.state,
                "state": "lost",
                "lost_reason": reason,
                "lost_flagged_by_id": self.env.uid,
                "lost_flagged_at": fields.Datetime.now(),
                "lost_cleared_by_id": False,
                "lost_cleared_at": False,
            }
        )
        self._approval_void("the device was flagged lost while scrap approval was pending")
        self.message_post(body="Flagged lost/stolen by %s: %s" % (self.env.user.name, reason))
        self._publish(
            "device.flagged",
            {
                "device_id": self.id,
                "flag": "lost",
                "reason": reason,
                "source": source,
                "serial_number": self.serial_number or None,
                "imei_1": self.imei_1 or None,
                "imei_2": self.imei_2 or None,
                "flagged_by": self.env.uid,
            },
        )

    def action_clear_lost(self, reason=None):
        """Clear a lost/stolen flag. BRU-AST-09: the Branch Manager clears it
        (A07 P1; any other user did in P0), and SoD: never the user who raised
        it (the flagger clearing his own flag was the laundering path, M17-2)."""
        if not (reason or "").strip():
            raise UserError("Say how the device was recovered or the report withdrawn.")
        for rec in self:
            if rec.state != "lost":
                raise UserError("Only a device flagged lost can be cleared.")
            if not self.env.su and rec.lost_flagged_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you flagged %s lost, so another user must "
                    "clear the flag." % rec.display_name
                )
            rec._assert_role(BRANCH_MANAGER_GROUP, "Clearing a lost/stolen flag")
            restore = rec.lost_prior_state
            if restore not in dict(rec._fields["state"].selection) or restore in NOT_SCRAPPABLE:
                restore = "registered"
            rec._guarded().write(
                {
                    "state": restore,
                    "lost_cleared_by_id": self.env.uid,
                    "lost_cleared_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Lost/stolen flag cleared by %s (back to %s): %s"
                % (self.env.user.name, rec._state_label(), reason)
            )
            rec._custody_flag_event("found", reason.strip())
            rec._publish(
                "device.flag_cleared",
                {
                    "device_id": rec.id,
                    "flag": "lost",
                    "reason": reason.strip(),
                    "restored_state": restore,
                    "cleared_by": self.env.uid,
                },
            )
        return True

    def _approval_needed(self) -> bool:
        return self.state not in NOT_SCRAPPABLE

    def action_request_approval(self, justification=None):
        """Request scrap approval. The justification IS the scrap reason, and
        the approver reads it, so it is required."""
        if not (justification or "").strip():
            raise UserError("State why the device should be scrapped.")
        for rec in self:
            if rec.state in NOT_SCRAPPABLE:
                raise UserError(
                    "%s is %s and cannot be scrapped." % (rec.display_name, rec._state_label())
                )
            # A request the approver could never apply is refused when it is made.
            rec._assert_scrap_instruction()
        return super().action_request_approval(justification=justification)

    def _assert_scrap_instruction(self):
        """BRU-AST-19: a customer-owned device reaches its end only with the
        customer's instruction on record, whichever way it gets there."""
        self.ensure_one()
        if self.owner_id and not self.eol_customer_instruction:
            raise UserError(
                "%s belongs to %s: record the customer's end-of-life instruction on the asset "
                "form before it is scrapped (BRU-AST-19)." % (self.display_name, self.owner_id.name)
            )

    def action_scrap(self):
        """Scrap the device: the M63 apply method, reached only from the
        approver's inbox (a direct press is refused). Quality Manager authority
        (P0: DOFA Tier 2 as a stand-in) is checked on the approver - the absent
        one when a delegate decides - and the requester never scraps the device
        he asked to scrap."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state in NOT_SCRAPPABLE:
                raise UserError(
                    "%s is %s and cannot be scrapped." % (rec.display_name, rec._state_label())
                )
            if not trusted:
                if not authority.has_group(DEVICE_DECISION_GROUP):
                    raise UserError(
                        "Scrapping a device requires the Device Quality Manager role, "
                        "which %s does not hold." % authority.name
                    )
                if acting & rec.approval_request_id.sudo().requested_by_id:
                    raise UserError("You requested this scrap, so someone else must approve it.")
                rec._assert_scrap_instruction()
            rec._guarded().write(
                {
                    "state": "scrapped",
                    "scrapped_by_id": self.env.uid,
                    "scrapped_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Scrapped by %s. Reason: %s"
                % (self.env.user.name, rec.approval_request_id.sudo().justification or "-")
            )
        return True

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.device",
            rec.id,
            {
                "device_id": rec.id,
                "serial_number": rec.serial_number,
                "brand": rec.brand_id.name if rec.brand_id else None,
                "model": rec.device_model_id.name,
                "owner_id": rec.owner_id.id if rec.owner_id else None,
            },
        )

    def _publish(self, event_type: str, payload: dict) -> None:
        from libs.py.fix_events import publish

        publish(self.env, event_type, self._name, self.id, payload)

    def add_history(self, event_type: str, description: str, order_id=None):
        """Add a permanent history entry (T07). The registry's own write path:
        a history row is otherwise insert-refused for users (M17-7)."""
        self.env["fix.device.history"]._guarded().create(
            {
                "device_id": self.id,
                "event_type": event_type,
                "description": description,
                "service_order_id": order_id,
                "date": fields.Datetime.now(),
            }
        )

    def is_under_warranty(self, on_date=None, require_verified=False):
        """BRU-SRM-02 / WTY-01: True when an ACTIVE warranty record of this device
        covers ``on_date`` (default: today), start and end dates included.

        Decided on the date itself, not on the stored ``warranty_status`` (that
        value is frozen at its last recompute: a warranty that ended since still
        reads "in_warranty"). Expired, voided and pending records never cover.

        ``require_verified`` additionally demands that a person has checked the
        purchase proof (``verification_state == "verified"``). It defaults to
        False so the gate keeps today's business outcome: unverified cover is
        still cover, and withdrawing it from live customers is a commercial
        decision, not an engineering one. The parameter exists so the exposure
        can be MEASURED - see ``unverified_warranty_cover`` below and
        ``fix.service.order.warranty_cover_unverified``.

        The default date is ``context_today``, not UTC ``today``: Bangladesh is
        UTC+6, so for the first six hours of every local day UTC is still on the
        previous date, and on the 1st of a month it is in the previous MONTH -
        which silently decided cover on the wrong side of an expiry boundary.
        """
        self.ensure_one()
        if self.state in NOT_RESOLVED:
            # BRU-AST-03: a provisional identity reaches no warranty claim.
            return False
        day = on_date or fields.Date.context_today(self)
        return any(
            w.status == "active"
            and w.start_date
            and w.end_date
            and w.start_date <= day <= w.end_date
            and (not require_verified or w.verification_state == "verified")
            for w in self.warranty_id
        )

    def unverified_warranty_cover(self, on_date=None):
        """The warranty records covering ``on_date`` that nobody has verified.

        A04 audit 2026-11-01: 53 of 55 live warranty rows were ACTIVE with
        ``verified_at`` empty, and the warranty gate never looked at that - so
        53 devices could draw a free warranty repair with no proof on file and
        nothing in the system recorded the exposure. This makes it queryable.
        """
        self.ensure_one()
        day = on_date or fields.Date.context_today(self)
        return self.warranty_id.filtered(
            lambda w: (
                w.status == "active"
                and w.start_date
                and w.end_date
                and w.start_date <= day <= w.end_date
                and w.verification_state == "unverified"
            )
        )

    def get_compatible_parts(self, category=None):
        """M17 W2: Query spare parts compatibility matrix for this device model."""
        self.ensure_one()
        domain = [("model_id", "=", self.device_model_id.id), ("active", "=", True)]
        if category:
            domain.append(("category", "=", category))
        return self.env["fix.device.part.compatibility"].search(domain)
