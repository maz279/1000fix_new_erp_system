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
# Until the registry supervisor role exists (P1), identifier correction is an
# administrator act.
IDENTIFIER_CORRECTION_GROUP = "base.group_system"
# A07 audit (2026-11-03), M17-8/M17-3: scrapping a customer's device and
# merging two devices are not money decisions, so they carry no DOFA amount.
# The spec's decider is the branch manager (BRU-AST-09/19); no such role group
# exists yet (P1), so the DOFA tier whose label matches is used:
# "Tier 2 - Branch / Operations Manager". A default the business must confirm.
DEVICE_DECISION_GROUP = "cd_entity_config.group_dofa_tier_2"
# A lost or scrapped device is not in anyone's hands to scrap or hand on.
NOT_SCRAPPABLE = ("lost", "scrapped")


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
        }

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)

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
            ("registered", "Registered"),
            ("in_service", "In Service"),
            ("repaired", "Repaired"),
            ("returned", "Returned to Owner"),
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
    estimated_residual_value_bdt = fields.Monetary(
        string="Estimated Residual Value (BDT)",
        currency_field="currency_id",
        default=0.0,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.BDT", raise_if_not_found=False)
        or self.env.company.currency_id,
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

    @api.constrains("serial_number", "imei_1")
    def _check_identity_format(self):
        for rec in self:
            if rec.imei_1 and (not rec.imei_1.isdigit() or len(rec.imei_1) != 15):
                raise ValidationError(
                    f"IMEI must be exactly 15 digits, got {len(rec.imei_1)}: {rec.imei_1}"
                )

    # Events (T08)
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("device.registered", rec)
        return records

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
        return locked

    def write(self, vals):
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
        result = super().write(vals)
        if "owner_id" in vals:
            for rec in self:
                self._emit("device.transferred", rec)
        if "warranty_id" in vals:
            for rec in self:
                self._emit("device.warranty_updated", rec)
        return result

    def action_transfer_ownership(self, new_owner_id: int, transfer_type="sale", notes=None):
        """Transfer ownership (T05: portal P01 exposes this in Phase 5).

        BRU-AST-09: a device flagged lost/stolen or scrapped is never handed on.
        The owner and the ownership trail are written together, through the guard,
        so neither can be changed without the other."""
        self.ensure_one()
        if self.state in ("lost", "scrapped"):
            raise UserError(
                "%s is %s and cannot change owner."
                % (self.display_name, dict(self._fields["state"].selection)[self.state])
            )
        new_owner = self.env["res.partner"].browse(int(new_owner_id)).exists()
        if not new_owner:
            raise UserError("The new owner does not exist.")
        old_owner = self.owner_id
        if old_owner == new_owner:
            raise UserError("%s already belongs to %s." % (self.display_name, new_owner.name))
        self._guarded().write({"owner_id": new_owner.id, "state": "transferred"})
        self.env["fix.device.ownership"]._guarded().create(
            {
                "device_id": self.id,
                "from_partner_id": old_owner.id if old_owner else False,
                "to_partner_id": new_owner.id,
                "transfer_date": fields.Date.context_today(self),
                "transfer_type": transfer_type,
                "notes": notes,
            }
        )
        # A scrap requested for the old owner's device is not the new owner's.
        self._approval_void("the device changed owner while scrap approval was pending")

    def action_correct_identifier(self, field_name: str, value, reason: str):
        """Privileged correction of a serial number or IMEI (e.g. a board swap or
        a mis-keyed intake). The old value is kept in the chatter with the reason."""
        self.ensure_one()
        if field_name not in IDENTIFIER_FIELDS:
            raise UserError("Only the serial number and IMEIs are corrected this way.")
        if not self.env.su and not self.env.user.has_group(IDENTIFIER_CORRECTION_GROUP):
            raise AccessError("Only an administrator can correct a device identifier.")
        if not (reason or "").strip():
            raise UserError("A reason is required to correct a device identifier.")
        old = self[field_name]
        self._guarded().write({field_name: value or False})
        self.message_post(
            body="%s corrected from %s to %s. Reason: %s"
            % (self._fields[field_name].string, old or "(empty)", value or "(empty)", reason)
        )

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
            rec._guarded().write(
                {
                    "lost_prior_state": rec.state,
                    "state": "lost",
                    "lost_reason": reason.strip(),
                    "lost_flagged_by_id": self.env.uid,
                    "lost_flagged_at": fields.Datetime.now(),
                    "lost_cleared_by_id": False,
                    "lost_cleared_at": False,
                }
            )
            rec._approval_void("the device was flagged lost while scrap approval was pending")
            rec.message_post(body="Flagged lost/stolen by %s: %s" % (self.env.user.name, reason))
        return True

    def action_clear_lost(self, reason=None):
        """Clear a lost/stolen flag. SoD: never by the user who raised it (the
        flagger clearing his own flag was the laundering path, M17-2)."""
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
        return super().action_request_approval(justification=justification)

    def action_scrap(self):
        """Scrap the device: the M63 apply method, reached only from the
        approver's inbox (a direct press is refused). Tier 2 authority is
        checked on the approver - the absent one when a delegate decides - and
        the requester never scraps the device he asked to scrap."""
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
                        "Scrapping a device requires DOFA Tier 2 (Branch / Operations "
                        "Manager) authority, which %s does not hold." % authority.name
                    )
                if acting & rec.approval_request_id.sudo().requested_by_id:
                    raise UserError("You requested this scrap, so someone else must approve it.")
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

    def add_history(self, event_type: str, description: str, order_id=None):
        """Add a permanent history entry (T07)."""
        self.env["fix.device.history"].create(
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
            lambda w: w.status == "active"
            and w.start_date
            and w.end_date
            and w.start_date <= day <= w.end_date
            and w.verification_state == "unverified"
        )

    def get_compatible_parts(self, category=None):
        """M17 W2: Query spare parts compatibility matrix for this device model."""
        self.ensure_one()
        domain = [("model_id", "=", self.device_model_id.id), ("active", "=", True)]
        if category:
            domain.append(("category", "=", category))
        return self.env["fix.device.part.compatibility"].search(domain)
