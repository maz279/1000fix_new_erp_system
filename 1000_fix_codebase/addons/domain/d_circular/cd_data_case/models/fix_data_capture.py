# M06 capture audit, second pass (2026-11-18): the records five M06
# sub-module pages had no way to capture, because the records did not exist,
# and the case-intake facts the case form could not take.
#
# The 13 Nov pass gave every page a button. The user still saw pages without
# a RELEVANT capture: each of these pages lists or works on something the
# spec says a person records there, and the estate had no record for it.
#
#   page 10 fix.data.confidentiality.undertaking  FR-DTS-010 (P0), BRU-DTS-12
#           (H), AUT-DTS-01: staff undertakings are recorded per case BEFORE
#           access is granted. Only the customer NDA reference existed; any
#           operator could be named on a case and open its data.
#   page 7  fix.data.retention.hold  FR-DTS-008b (P0), BRU-DTS-06 (H):
#           retention beyond the window only under a documented, approved,
#           time-limited hold. There was no way to hold a case at all: the
#           retention job flagged it for purge whatever the customer or a
#           court had asked.
#   page 6  fix.data.recovered.inventory  FR-DTS-006 (P1), T-02: recovered
#           volumes and file counts BY TYPE and size, never names. Only two
#           totals existed.
#   page 9  fix.data.wipe.request  FR-DTS-019 (P1), FR-DTS-024 (P1),
#           AUT-DTS-08/10, BRU-DTS-10 (H): a destruction request from M14, M18,
#           a customer or a corporate decommission, and the fallback to
#           physical destruction when erasure cannot be verified. Only the
#           certificate existed, so nobody could ASK for a wipe, and a failed
#           wipe went nowhere.
#   page 8  fix.data.backup.run  FR-DTS-012 (P2), AUT-DTS-11: job outcomes,
#           and an incident on two consecutive failures. Plus the restore test
#           (FR-DTS-013) becomes a record a person captures with its scope and
#           evidence; a "passed" test without evidence proved nothing.
#   page 1  FR-DTS-001 / 028: failure symptoms, criticality, the description
#           of the data the customer wants and their declarations, which the
#           case form could not take.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish  # FF-28

from .fix_data_case import (
    GROUP_LAB_MANAGER,
    GROUP_OPERATOR,
    GROUP_Z4_CUSTODIAN,
    _norm_serial,
    _require_role,
)
from .fix_data_case_ext import _resolve_user

CLOSED_CASE = ("purged", "closed", "unrecoverable")
# A hold is time-limited (FR-DTS-008b). The longest single hold is a policy
# number for the owner to set; unset, a hold may run at most 90 days, and a
# longer one is a second, separately approved hold.
HOLD_MAX_DAYS_PARAM = "cd_data_case.retention_hold_max_days"
HOLD_MAX_DAYS_DEFAULT = 90

FILE_TYPES = [
    ("documents", "Documents (Word, PDF, text)"),
    ("spreadsheets", "Spreadsheets"),
    ("presentations", "Presentations"),
    ("images", "Images / Photos"),
    ("video", "Video"),
    ("audio", "Audio"),
    ("email", "Email Stores"),
    ("database", "Databases"),
    ("archives", "Archives (zip, rar, backups)"),
    ("source_code", "Source Code"),
    ("system", "System / Application Files"),
    ("other", "Other"),
]


def _immutable(records, vals, what, allowed=()):
    """Refuse a change to a record of what happened. The workspace form posts
    back every field it shows, so an unchanged value is not a change."""
    if records.env.su:
        return
    guarded = records._fix_guarded_fields()
    for rec in records:
        changed = [
            name
            for name in set(vals) - set(allowed)
            if name in rec._fields and rec._fix_guard_differs(name, vals[name], rec[name])
        ]
        # a workflow-owned field keeps the estate's own refusal
        if guarded & set(changed):
            rec._fix_guard_refuse(guarded & set(changed))
        if changed:
            raise UserError("%s is a record of what happened; it cannot be edited." % what)


def _attachment(env, value):
    if not value:
        return env["ir.attachment"]
    if isinstance(value, models.BaseModel):
        return value
    return env["ir.attachment"].browse(int(value)).exists()


UNDERTAKING = "fix.data.confidentiality.undertaking"


def _undertaking_document(env, value):
    """The signed undertaking file. A02 ERP audit M06-F13: any attachment id
    was accepted - an empty file, or another record's document. It must be a
    non-empty file uploaded for THIS undertaking (not yet filed on any other
    record), by the person recording it; create() then files it here."""
    att = _attachment(env, value)
    if not att:
        return att
    stored = att.sudo()
    if not stored.raw:
        raise UserError("The signed undertaking file is empty: upload the signed document.")
    if stored.res_model and (stored.res_model != UNDERTAKING or stored.res_id):
        raise UserError(
            "The signed undertaking must be a file uploaded for this undertaking, not a "
            "document filed on another record."
        )
    if not env.su and stored.create_uid != env.user:
        raise UserError("Upload the signed undertaking yourself, with this undertaking.")
    return att


# --------------------------------------------------------------------------
# page 10 - staff confidentiality undertakings (FR-DTS-010, BRU-DTS-12)
# --------------------------------------------------------------------------


class FixDataConfidentialityUndertaking(models.Model):
    """One person's (or one party's) undertaking to keep a case confidential.
    A staff member accepts it themself on screen, or a signed form is
    attached; a customer NDA or a partner laboratory's agreement is always
    the signed document."""

    _name = "fix.data.confidentiality.undertaking"
    _description = "Data Case Confidentiality Undertaking"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "signed_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    name = fields.Char(compute="_compute_name", store=True)
    case_id = fields.Many2one(
        "fix.data.recovery.case",
        string="Recovery Case",
        required=True,
        ondelete="restrict",
        index=True,
    )
    undertaking_type = fields.Selection(
        [
            ("staff", "Staff Confidentiality Undertaking"),
            ("customer_nda", "Customer NDA"),
            ("partner_lab", "Partner Laboratory Confidentiality Agreement"),
        ],
        string="Undertaking",
        required=True,
        default="staff",
    )
    user_id = fields.Many2one("res.users", string="Staff Member", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer / Partner Laboratory")
    acknowledged = fields.Boolean(
        string="I have read this case's confidentiality undertaking and accept it",
        help="Only the staff member themself can accept on screen. For anyone else, "
        "attach the undertaking they signed.",
    )
    document_attachment_id = fields.Many2one(
        "ir.attachment", string="Signed Undertaking / NDA (scan)", ondelete="restrict"
    )
    document_reference = fields.Char(string="Document Reference")
    valid_until = fields.Date(string="Valid Until")
    signature_method = fields.Selection(
        [("e_ack", "Accepted on screen by the person"), ("signed_form", "Signed form attached")],
        readonly=True,
    )
    signed_at = fields.Datetime(readonly=True, default=fields.Datetime.now)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked")],
        default="active",
        required=True,
        readonly=True,
        tracking=True,
    )
    revoked_at = fields.Datetime(readonly=True)
    revoked_by_id = fields.Many2one("res.users", readonly=True)
    revoke_reason = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "signature_method",
            "signed_at",
            "recorded_by_id",
            "state",
            "revoked_at",
            "revoked_by_id",
            "revoke_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {
                "case_id",
                "undertaking_type",
                "user_id",
                "partner_id",
                "acknowledged",
                "document_attachment_id",
                "document_reference",
                "valid_until",
            }
        return locked

    @api.depends("case_id.name", "user_id.name", "partner_id.name", "undertaking_type")
    def _compute_name(self):
        for rec in self:
            who = rec.user_id.name or rec.partner_id.name or "-"
            rec.name = "%s - %s" % (rec.case_id.name or "-", who)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            _require_role(
                self.env, GROUP_OPERATOR, "Data Recovery Operator", "Recording an undertaking"
            )
        Case = self.env["fix.data.recovery.case"]
        for vals in vals_list:
            for stamp in self._fix_guarded_fields():
                vals.pop(stamp, None)
            case = Case.browse(vals.get("case_id")).exists()
            if not case:
                raise UserError("Choose the recovery case the undertaking covers.")
            if case.state in CLOSED_CASE:
                raise UserError(
                    "Case %s is %s: no one is given access to it." % (case.name, case.state)
                )
            kind = vals.get("undertaking_type") or "staff"
            document = _undertaking_document(self.env, vals.get("document_attachment_id"))
            if kind == "staff":
                user = self.env["res.users"].sudo().browse(vals.get("user_id")).exists()
                if not user:
                    raise UserError("Name the staff member who gives the undertaking.")
                if user.share:
                    raise UserError("%s is not a staff member." % user.name)
                vals.pop("partner_id", None)
                if user == self.env.user and vals.get("acknowledged") and not document:
                    method = "e_ack"
                elif document:
                    method = "signed_form"
                elif user == self.env.user:
                    raise UserError(
                        "Tick the acceptance box, or attach the undertaking you signed."
                    )
                else:
                    raise UserError(
                        "Only %s can accept the undertaking on screen. To record it for them, "
                        "attach the undertaking they signed." % user.name
                    )
                if self.sudo().search_count(
                    [("case_id", "=", case.id), ("user_id", "=", user.id), ("state", "=", "active")]
                ):
                    raise UserError(
                        "%s already has an active undertaking on case %s." % (user.name, case.name)
                    )
            else:
                if not vals.get("partner_id"):
                    raise UserError("Name the customer or partner laboratory that signed.")
                if not document:
                    raise UserError("Attach the signed NDA or confidentiality agreement.")
                vals.pop("user_id", None)
                method = "signed_form"
            vals["signature_method"] = method
            vals["signed_at"] = fields.Datetime.now()
            vals["recorded_by_id"] = self.env.uid
        records = super(FixDataConfidentialityUndertaking, self._guarded()).create(vals_list)
        for rec in records.filtered("document_attachment_id"):
            # the signed file is filed on the undertaking it evidences
            rec.document_attachment_id.sudo().write({"res_model": rec._name, "res_id": rec.id})
        for rec in records:
            rec.case_id.sudo().message_post(
                body="Confidentiality undertaking recorded: %s (%s, %s)."
                % (
                    rec.user_id.name or rec.partner_id.name,
                    dict(rec._fields["undertaking_type"].selection)[rec.undertaking_type],
                    dict(rec._fields["signature_method"].selection)[rec.signature_method],
                )
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            _immutable(self, vals, "A signed undertaking")
        return super().write(vals)

    def action_revoke(self, reason=None):
        """Withdraw an undertaking (the person leaves the case or the company).
        The person then cannot work the case until a new one is recorded."""
        if not (
            self.env.su
            or self.env.user.has_group(GROUP_LAB_MANAGER)
            or self.env.user.has_group(GROUP_Z4_CUSTODIAN)
        ):
            raise AccessError("Revoking an undertaking is for the lab manager or a Z4 custodian.")
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Give the reason the undertaking is revoked.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Undertaking %s is already revoked." % rec.name)
            rec._guarded().write(
                {
                    "state": "revoked",
                    "revoked_at": fields.Datetime.now(),
                    "revoked_by_id": self.env.uid,
                    "revoke_reason": reason,
                }
            )
        return True


# --------------------------------------------------------------------------
# page 7 - retention hold override (FR-DTS-008b, BRU-DTS-06)
# --------------------------------------------------------------------------


class FixDataRetentionHold(models.Model):
    """Keep a handed-over case's recovered data past its retention date: a
    documented reason, a fixed end date, approved by the lab manager who did
    not ask for it. While approved and running, the case is not purged."""

    _name = "fix.data.retention.hold"
    _description = "Recovered-Data Retention Hold"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    name = fields.Char(compute="_compute_name", store=True)
    case_id = fields.Many2one(
        "fix.data.recovery.case",
        string="Recovery Case",
        required=True,
        ondelete="restrict",
        index=True,
    )
    retention_until = fields.Date(related="case_id.retention_until", string="Retention Ends")
    reason_type = fields.Selection(
        [
            ("customer_request", "Customer Request (in writing)"),
            ("legal_hold", "Legal Hold / Court Order"),
            ("dispute", "Open Dispute or Complaint"),
            ("regulator", "Regulator or Authority Request"),
        ],
        string="Hold Basis",
        required=True,
    )
    reason = fields.Text(string="Why the data must be kept", required=True)
    hold_until = fields.Date(string="Hold Until", required=True)
    document_attachment_id = fields.Many2one(
        "ir.attachment", string="Supporting Document (request, order)", ondelete="restrict"
    )
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("released", "Released"),
            ("expired", "Expired"),
        ],
        default="requested",
        required=True,
        readonly=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda self: self.env.user
    )
    requested_at = fields.Datetime(readonly=True, default=fields.Datetime.now)
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(readonly=True)
    decision_note = fields.Text(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "requested_at",
            "decided_by_id",
            "decided_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {"case_id", "reason_type", "reason", "hold_until", "document_attachment_id"}
        return locked

    @api.depends("case_id.name", "hold_until")
    def _compute_name(self):
        for rec in self:
            rec.name = "Hold %s until %s" % (rec.case_id.name or "-", rec.hold_until or "-")

    def _max_days(self):
        try:
            days = int(
                self.env["ir.config_parameter"].sudo().get_param(HOLD_MAX_DAYS_PARAM)
                or HOLD_MAX_DAYS_DEFAULT
            )
        except ValueError:
            days = HOLD_MAX_DAYS_DEFAULT
        return max(days, 1)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            _require_role(
                self.env, GROUP_OPERATOR, "Data Recovery Operator", "Requesting a retention hold"
            )
        today = fields.Date.context_today(self)
        limit = today + timedelta(days=self._max_days())
        Case = self.env["fix.data.recovery.case"]
        for vals in vals_list:
            for stamp in self._fix_guarded_fields():
                vals.pop(stamp, None)
            case = Case.browse(vals.get("case_id")).exists()
            if not case:
                raise UserError("Choose the handed-over case to hold.")
            if case.state != "handover":
                raise UserError(
                    "Case %s is '%s': a retention hold applies to recovered data that was "
                    "handed over and is still retained." % (case.name, case.state)
                )
            until = fields.Date.to_date(vals.get("hold_until"))
            if not until:
                raise UserError("Give the date the hold ends.")
            if case.retention_until and until <= case.retention_until:
                raise UserError(
                    "Case %s is retained until %s anyway: a hold must end after that."
                    % (case.name, case.retention_until)
                )
            if until > limit:
                raise UserError(
                    "A hold may run at most %d days (until %s). Ask for a further hold when "
                    "this one ends." % (self._max_days(), limit)
                )
            if not (vals.get("reason") or "").strip():
                raise UserError("Document why the data must be kept.")
            if self.sudo().search_count(
                [
                    ("case_id", "=", case.id),
                    ("state", "in", ("requested", "approved")),
                    ("hold_until", ">=", today),
                ]
            ):
                raise UserError("Case %s already has an open retention hold." % case.name)
            vals["requested_by_id"] = self.env.uid
            vals["requested_at"] = fields.Datetime.now()
        records = super(FixDataRetentionHold, self._guarded()).create(vals_list)
        for rec in records:
            rec.case_id.sudo().message_post(
                body="Retention hold requested until %s (%s)." % (rec.hold_until, rec.reason)
            )
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            _immutable(self, vals, "A retention hold request")
        return super().write(vals)

    def _decide(self, state, note=None):
        _require_role(
            self.env, GROUP_LAB_MANAGER, "Data Recovery Lab Manager", "Deciding a retention hold"
        )
        for rec in self:
            if rec.state != "requested":
                raise UserError("Hold %s is %s, not awaiting a decision." % (rec.name, rec.state))
            if not self.env.su and rec.requested_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: you asked for hold %s, so another lab manager "
                    "decides it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": state,
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                    "decision_note": note or False,
                }
            )
            rec.case_id.sudo().message_post(
                body="Retention hold until %s %s by %s."
                % (rec.hold_until, state, self.env.user.name)
            )
        return True

    def action_approve(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.hold_until < today:
                raise UserError("Hold %s already ended on %s." % (rec.name, rec.hold_until))
            if rec.case_id.state != "handover":
                raise UserError("Case %s is no longer retained." % rec.case_id.name)
        return self._decide("approved")

    def action_reject(self, note=None):
        if not (note or "").strip():
            raise UserError("Say why the hold is refused.")
        return self._decide("rejected", note.strip())

    def action_release(self):
        """End a hold early: the case falls back to its retention date."""
        for rec in self:
            if rec.state not in ("requested", "approved"):
                raise UserError("Hold %s is %s." % (rec.name, rec.state))
            if not (
                self.env.su
                or rec.requested_by_id == self.env.user
                or self.env.user.has_group(GROUP_LAB_MANAGER)
            ):
                raise AccessError("A hold is released by whoever asked for it or a lab manager.")
            rec._guarded().write(
                {
                    "state": "released",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
            rec.case_id.sudo().message_post(body="Retention hold %s released." % rec.name)
        return True

    @api.model
    def _expire_ended(self):
        today = fields.Date.context_today(self)
        ended = self.sudo().search(
            [("state", "in", ("requested", "approved")), ("hold_until", "<", today)]
        )
        for rec in ended:
            rec._guarded().write({"state": "expired"})
            rec.case_id.message_post(body="Retention hold %s ended." % rec.name)
        return ended


# --------------------------------------------------------------------------
# page 6 - recovered-data inventory by file type (FR-DTS-006, T-02)
# --------------------------------------------------------------------------


class FixDataRecoveredInventory(models.Model):
    """What was recovered, per kind of file: how many and how much. A fixed
    list of types and two numbers - never a file name (T-02)."""

    _name = "fix.data.recovered.inventory"
    _description = "Recovered-Data Inventory Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "case_id, file_type"

    company_id = fields.Many2one(
        "res.company", related="case_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="case_id.operating_unit_id", store=True, readonly=True
    )
    name = fields.Char(compute="_compute_name", store=True)
    case_id = fields.Many2one(
        "fix.data.recovery.case",
        string="Recovery Case",
        required=True,
        ondelete="cascade",
        index=True,
    )
    file_type = fields.Selection(FILE_TYPES, string="File Type", required=True)
    file_count = fields.Integer(string="Files", required=True)
    size_gb = fields.Float(string="Size (GB)", digits=(16, 3), required=True)
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )
    recorded_at = fields.Datetime(readonly=True, default=fields.Datetime.now)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"recorded_by_id", "recorded_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {"case_id", "file_type"}
            if any(rec.case_id.state not in ("recovering", "recovered") for rec in self):
                locked |= {"file_count", "size_gb"}
        return locked

    @api.depends("case_id.name", "file_type")
    def _compute_name(self):
        labels = dict(FILE_TYPES)
        for rec in self:
            rec.name = "%s - %s" % (rec.case_id.name or "-", labels.get(rec.file_type, "-"))

    @staticmethod
    def _check_numbers(count, size):
        try:
            count, size = int(count), float(size)
        except (TypeError, ValueError):
            raise UserError("Give the number of files and their size in GB.") from None
        if count < 0 or size < 0:
            raise UserError("A file count or size cannot be negative.")
        if count == 0 and size > 0:
            raise UserError("No files cannot take up space: check the count.")

    @staticmethod
    def _open_case(case, what):
        if case.state not in ("recovering", "recovered"):
            raise UserError(
                "Case %s: the recovered-data inventory is recorded during recovery or once the "
                "data is recovered, before handover (the case is '%s'). %s"
                % (case.name, case.state, what)
            )
        case._z4_assert_assigned("Recording the recovered-data inventory")

    @api.model_create_multi
    def create(self, vals_list):
        Case = self.env["fix.data.recovery.case"]
        for vals in vals_list:
            for stamp in self._fix_guarded_fields():
                vals.pop(stamp, None)
            case = Case.browse(vals.get("case_id")).exists()
            if not case:
                raise UserError("Choose the case whose recovered data you are counting.")
            self._open_case(case, "")
            self._check_numbers(vals.get("file_count"), vals.get("size_gb"))
            if self.sudo().search_count(
                [("case_id", "=", case.id), ("file_type", "=", vals.get("file_type"))]
            ):
                raise UserError(
                    "Case %s already has a %s line: correct that line instead."
                    % (
                        case.name,
                        dict(FILE_TYPES).get(vals.get("file_type"), vals.get("file_type")),
                    )
                )
            vals["recorded_by_id"] = self.env.uid
            vals["recorded_at"] = fields.Datetime.now()
        records = super(FixDataRecoveredInventory, self._guarded()).create(vals_list)
        records.mapped("case_id")._sync_inventory_totals()
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if any(
                    k in vals and rec._fix_guard_differs(k, vals[k], rec[k])
                    for k in ("case_id", "file_type")
                ):
                    raise UserError("Record another file type as its own line.")
                if any(
                    k in vals and rec._fix_guard_differs(k, vals[k], rec[k])
                    for k in ("file_count", "size_gb")
                ):
                    self._open_case(rec.case_id, "It is fixed once handed over.")
                    self._check_numbers(
                        vals.get("file_count", rec.file_count), vals.get("size_gb", rec.size_gb)
                    )
        res = super().write(vals)
        self.mapped("case_id")._sync_inventory_totals()
        return res

    def unlink(self):
        cases = self.mapped("case_id")
        if not self.env.su:
            for rec in self:
                self._open_case(rec.case_id, "It is fixed once handed over.")
        res = super().unlink()
        cases.exists()._sync_inventory_totals()
        return res


# --------------------------------------------------------------------------
# page 9 - wipe / destruction requests (FR-DTS-019, FR-DTS-024, BRU-DTS-10)
# --------------------------------------------------------------------------


class FixDataWipeRequest(models.Model):
    """A request to sanitise or destroy one piece of media, from refurbishment
    (M14), recycling (M18), a customer or a corporate decommission. The lab
    answers it with a certificate; when erasure cannot be verified, the next
    certificate must be a physical destruction (BRU-DTS-10)."""

    _name = "fix.data.wipe.request"
    _description = "Data Wipe / Destruction Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    source = fields.Selection(
        [
            ("m14_refurbishment", "Refurbishment / Trade-in (M14)"),
            ("m18_recycling", "Recycling / E-waste (M18)"),
            # A02 pass 2 review N2: a returned rental unit before its next renter
            ("m13_rental", "Rental Turnaround (M13)"),
            ("customer", "Customer Request"),
            ("corporate_decommission", "Corporate Decommission"),
        ],
        string="Requested For",
        required=True,
    )
    source_ref = fields.Char(string="Source Reference (lot, trade-in, project, order)")
    customer_id = fields.Many2one("res.partner", string="Customer / Client")
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    serial_number = fields.Char(string="Media Serial Number", required=True)
    media_description = fields.Char(string="Media (type, make, capacity)")
    confidentiality_level = fields.Selection(
        [("low", "Low"), ("moderate", "Moderate"), ("high", "High")],
        string="Data Confidentiality",
        required=True,
    )
    disposition = fields.Selection(
        [
            ("internal_reuse", "Reuse Inside the Company"),
            ("resale", "Resale / Refurbishment"),
            ("recycling", "Recycling"),
            ("return_customer", "Return to the Customer"),
        ],
        string="Final Disposition",
        required=True,
    )
    notes = fields.Text()
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda self: self.env.user
    )
    requested_at = fields.Datetime(readonly=True, default=fields.Datetime.now)
    certificate_ids = fields.One2many(
        "fix.data.wipe.certificate", "wipe_request_id", string="Certificates"
    )
    certificate_count = fields.Integer(compute="_compute_state", store=True)
    cancelled = fields.Boolean(readonly=True)
    cancel_reason = fields.Text(readonly=True)
    state = fields.Selection(
        [
            ("requested", "Requested"),
            ("in_progress", "Wipe Recorded, Awaiting Verification"),
            ("certified", "Certified"),
            ("physical_required", "Erasure Failed: Physical Destruction Required"),
            ("escalated", "Destruction Failed: Escalated"),
            ("cancelled", "Cancelled"),
        ],
        compute="_compute_state",
        store=True,
        index=True,
    )

    _REQUEST_FIELDS = (
        "source",
        "source_ref",
        "customer_id",
        "device_id",
        "serial_number",
        "media_description",
        "confidentiality_level",
        "disposition",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "requested_by_id",
            "requested_at",
            "cancelled",
            "cancel_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(rec.certificate_ids or rec.cancelled for rec in self):
            locked |= set(self._REQUEST_FIELDS)
        return locked

    @api.depends("cancelled", "certificate_ids.sanitization_status", "certificate_ids.method")
    def _compute_state(self):
        for rec in self:
            certs = rec.certificate_ids.sorted("id")
            rec.certificate_count = len(certs)
            last = certs[-1:] if certs else certs
            if rec.cancelled:
                rec.state = "cancelled"
            elif any(c.sanitization_status == "verified" for c in certs):
                rec.state = "certified"
            elif not last:
                rec.state = "requested"
            elif last.sanitization_status == "pending_verification":
                rec.state = "in_progress"
            elif last.method == "physical_destruction":
                rec.state = "escalated"
            else:
                rec.state = "physical_required"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for stamp in self._fix_guarded_fields():
                vals.pop(stamp, None)
            if vals.get("device_id") and not vals.get("serial_number"):
                device = self.env["fix.device"].sudo().browse(vals["device_id"])
                vals["serial_number"] = (
                    self.env["fix.data.wipe.certificate"]._fix_media_serial(device) or False
                )
            if not _norm_serial(vals.get("serial_number")):
                raise UserError(
                    "Give the media serial number: every certificate is bound to one serial "
                    "(BRU-DTS-11)."
                )
            vals["name"] = (
                self.env["ir.sequence"].sudo().next_by_code("fix.data.wipe.request") or "WRQ/New"
            )
            vals["requested_by_id"] = self.env.uid
            vals["requested_at"] = fields.Datetime.now()
        return super(FixDataWipeRequest, self._guarded()).create(vals_list)

    @api.model
    def _m06_request_for(
        self, consumer, source, serial, disposition, confidentiality="high", **extra
    ):
        """A02 pass 2 review N2: the wipe request a consumer (an M14 trade-in,
        an M18 collection, an M13 turnaround) raises for the device it took
        in, named after it (source_ref), so the certificate that releases the
        device is bound to that consumer. Idempotent: the consumer's open
        request is returned. System write after the consumer's own checks;
        the request names the user whose action raised it."""
        consumer.ensure_one()
        ref = consumer.display_name if "name" not in consumer._fields else consumer.name
        Request = self.sudo()
        existing = Request.search(
            [
                ("source", "=", source),
                ("source_ref", "=", ref),
                ("cancelled", "=", False),
            ],
            order="id desc",
            limit=1,
        )
        if existing:
            return existing.with_env(self.env)
        vals = {
            "source": source,
            "source_ref": ref,
            "serial_number": serial,
            "confidentiality_level": confidentiality,
            "disposition": disposition,
        }
        for key in ("customer_id", "device_id", "company_id", "media_description"):
            if extra.get(key):
                vals[key] = extra[key]
        request = Request.create([vals])
        request.message_post(
            body="Raised by %s %s: the certificate that releases the device answers this "
            "request." % (consumer._description, ref)
        )
        return request.with_env(self.env)

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self:
                if rec.certificate_ids or rec.cancelled:
                    changed = [
                        k
                        for k in self._REQUEST_FIELDS
                        if k in vals and rec._fix_guard_differs(k, vals[k], rec[k])
                    ]
                    if changed:
                        raise UserError(
                            "Request %s is being worked: what it asks for is fixed. Cancel it "
                            "and raise a new one." % rec.name
                        )
        return super().write(vals)

    def action_cancel(self, reason=None):
        reason = (reason or "").strip()
        if not reason:
            raise UserError("Say why the request is cancelled.")
        for rec in self:
            if rec.state != "requested":
                raise UserError(
                    "Request %s is '%s': only a request no wipe was recorded for can be "
                    "cancelled." % (rec.name, rec.state)
                )
            if not (
                self.env.su
                or rec.requested_by_id == self.env.user
                or self.env.user.has_group(GROUP_OPERATOR)
            ):
                raise AccessError("A request is cancelled by whoever raised it or the data lab.")
            rec._guarded().write({"cancelled": True, "cancel_reason": reason})
        return True

    def _notify_failed(self, cert):
        """AUT-DTS-10: erasure could not be verified - physical destruction is
        now mandatory; tell the requester and keep the exception on record."""
        for rec in self:
            if cert.method == "physical_destruction":
                note = (
                    "Physical destruction certificate %s for media %s FAILED verification. "
                    "Escalated: the media must not leave the lab until destruction is verified."
                    % (cert.name, rec.serial_number)
                )
                summary = "Destruction failed: %s" % rec.name
            else:
                note = (
                    "Erasure certificate %s for media %s could not be verified. Physical "
                    "destruction is now mandatory (BRU-DTS-10): record a Physical Destruction "
                    "certificate against this request." % (cert.name, rec.serial_number)
                )
                summary = "Erasure failed, destroy physically: %s" % rec.name
            rec.sudo().message_post(body=note)
            for user in (rec.requested_by_id | cert.technician_id).filtered(
                lambda u: u.active and not u.share
            ):
                rec.sudo().activity_schedule(
                    "mail.mail_activity_data_todo", summary=summary, note=note, user_id=user.id
                )


class FixDataWipeCertificateCapture(models.Model):
    _inherit = "fix.data.wipe.certificate"

    wipe_request_id = fields.Many2one(
        "fix.data.wipe.request",
        string="Answers Request",
        ondelete="restrict",
        index=True,
        help="The wipe or destruction request this certificate answers (M14, M18, customer, "
        "corporate decommission). The serial must match it.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].sanitization_status not in (False, "pending_verification"):
            locked.add("wipe_request_id")
        return locked

    def _check_request(self, request, serial, method):
        if request.state in ("cancelled", "certified", "escalated"):
            raise UserError(
                "Request %s is %s: it takes no further certificate." % (request.name, request.state)
            )
        if request.certificate_ids.filtered(
            lambda c: c.sanitization_status == "pending_verification"
        ):
            raise UserError(
                "Request %s already has a certificate awaiting verification." % request.name
            )
        if serial and _norm_serial(serial) != _norm_serial(request.serial_number):
            raise UserError(
                "Request %s is for media %s, not %s."
                % (request.name, request.serial_number, serial)
            )
        if request.state == "physical_required" and method != "physical_destruction":
            raise UserError(
                "Erasure of media %s could not be verified, so physical destruction is "
                "mandatory (BRU-DTS-10): choose Physical Destruction." % request.serial_number
            )

    @api.model_create_multi
    def create(self, vals_list):
        Request = self.env["fix.data.wipe.request"]
        for vals in vals_list:
            if vals.get("wipe_request_id"):
                request = Request.browse(vals["wipe_request_id"]).exists()
                if not request:
                    raise UserError("The wipe request no longer exists.")
                if not vals.get("serial_number") and not vals.get("device_id"):
                    vals["serial_number"] = request.serial_number
                if not vals.get("device_id") and request.device_id:
                    vals["device_id"] = request.device_id.id
                serial = vals.get("serial_number")
                if not serial and vals.get("device_id"):
                    serial = self._fix_media_serial(
                        self.env["fix.device"].sudo().browse(vals["device_id"])
                    )
                self._check_request(request, serial, vals.get("method"))
        records = super().create(vals_list)
        records._fix_check_after_failure()
        return records

    def _fix_check_after_failure(self):
        """A02 ERP audit M06-F6 (BRU-DTS-10): after a failed erasure of a
        media serial, a new certificate for it - with or without the request -
        is a physical destruction."""
        for cert in self:
            if cert.method != "physical_destruction":
                failed = cert._fix_failed_before()
                if failed:
                    raise UserError(
                        "Erasure of media %s already failed (certificate %s): physical "
                        "destruction is mandatory now (BRU-DTS-10). Choose Physical Destruction."
                        % (cert.serial_number, ", ".join(failed.mapped("name")))
                    )

    def write(self, vals):
        if "wipe_request_id" in vals and not self._fix_guard_open():
            for rec in self:
                if rec._fix_guard_differs(
                    "wipe_request_id", vals["wipe_request_id"], rec.wipe_request_id
                ):
                    if rec.sanitization_status != "pending_verification":
                        raise UserError(
                            "Certificate %s is decided: its request is fixed." % rec.name
                        )
                    request = (
                        self.env["fix.data.wipe.request"].browse(vals["wipe_request_id"]).exists()
                    )
                    if request:
                        rec._check_request(
                            request,
                            vals.get("serial_number", rec.serial_number),
                            vals.get("method", rec.method),
                        )
        result = super().write(vals)
        if {"serial_number", "device_id", "method"} & set(vals) and not self._fix_guard_open():
            # A02 ERP audit M06-F7: a certificate's serial was re-typed after it
            # was linked to a request, with no check against the request.
            for rec in self.filtered("wipe_request_id"):
                request = rec.wipe_request_id
                if _norm_serial(rec.serial_number) != _norm_serial(request.serial_number):
                    raise UserError(
                        "Certificate %s answers request %s for media %s: its serial cannot be "
                        "%s." % (rec.name, request.name, request.serial_number, rec.serial_number)
                    )
            self._fix_check_after_failure()
        return result

    def action_mark_failed(self):
        res = super().action_mark_failed()
        for cert in self.filtered("wipe_request_id"):
            cert.wipe_request_id._notify_failed(cert)
        return res


# --------------------------------------------------------------------------
# page 8 - backup job runs (FR-DTS-012, AUT-DTS-11) and restore tests (013)
# --------------------------------------------------------------------------

_FAILED_RUN = ("failed", "missed")


class FixDataBackupRun(models.Model):
    """One backup job's outcome against a customer's plan. Two failed or
    missed runs in a row raise an incident to the plan's owner."""

    _name = "fix.data.backup.run"
    _description = "Backup Job Run"
    _inherit = ["fix.guarded.mixin"]
    _order = "started_at desc, id desc"

    company_id = fields.Many2one(
        "res.company", related="plan_id.company_id", store=True, readonly=True, index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="plan_id.operating_unit_id", store=True, readonly=True
    )
    name = fields.Char(compute="_compute_name", store=True)
    plan_id = fields.Many2one(
        "fix.data.backup.plan", string="Backup Plan", required=True, ondelete="cascade", index=True
    )
    started_at = fields.Datetime(string="Job Started", required=True, default=fields.Datetime.now)
    ended_at = fields.Datetime(string="Job Ended")
    outcome = fields.Selection(
        [
            ("success", "Succeeded"),
            ("partial", "Completed with Warnings"),
            ("failed", "Failed"),
            ("missed", "Missed (did not run)"),
        ],
        required=True,
    )
    transferred_gb = fields.Float(string="Data Backed Up (GB)", digits=(16, 3))
    error_ref = fields.Char(string="Error / Alert Reference")
    notes = fields.Text()
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", readonly=True, default=lambda self: self.env.user
    )
    incident_raised = fields.Boolean(string="Incident Raised (2nd failure in a row)", readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"recorded_by_id", "incident_raised"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked |= {
                "plan_id",
                "started_at",
                "ended_at",
                "outcome",
                "transferred_gb",
                "error_ref",
                "notes",
            }
        return locked

    @api.depends("plan_id.name", "started_at", "outcome")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s" % (rec.plan_id.name or "-", rec.started_at or "-")

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            for stamp in self._fix_guarded_fields():
                vals.pop(stamp, None)
            start = fields.Datetime.to_datetime(vals.get("started_at")) or now
            end = fields.Datetime.to_datetime(vals.get("ended_at"))
            if start > now + timedelta(minutes=5):
                raise UserError("A backup run is recorded after it happened.")
            if end and end < start:
                raise UserError("The job cannot end before it started.")
            if vals.get("outcome") in ("failed", "partial") and not (
                vals.get("error_ref") or vals.get("notes")
            ):
                raise UserError("Give the error reference or what went wrong.")
            vals["recorded_by_id"] = self.env.uid
        records = super(FixDataBackupRun, self._guarded()).create(vals_list)
        for rec in records:
            rec._raise_incident_on_repeat()
        return records

    def write(self, vals):
        if not self._fix_guard_open():
            _immutable(self, vals, "A backup run")
        return super().write(vals)

    def _raise_incident_on_repeat(self):
        """AUT-DTS-11: the second failed or missed run in a row."""
        self.ensure_one()
        if self.outcome not in _FAILED_RUN:
            return
        previous = self.sudo().search(
            [
                ("plan_id", "=", self.plan_id.id),
                ("id", "!=", self.id),
                ("started_at", "<=", self.started_at),
            ],
            order="started_at desc, id desc",
            limit=1,
        )
        if not previous or previous.outcome not in _FAILED_RUN:
            return
        plan = self.plan_id.sudo()
        note = (
            "Backup plan %s failed twice in a row (%s, then %s). Contact the customer and fix "
            "the job before the recovery point objective is breached."
            % (plan.name, previous.started_at, self.started_at)
        )
        plan.message_post(body=note)
        for user in (plan.create_uid | self.recorded_by_id).filtered(
            lambda u: u.active and not u.share
        ):
            plan.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Backup failing: %s" % plan.name,
                note=note,
                user_id=user.id,
            )
        # runs are append-only for their recorders (no write right): the
        # system stamps the incident
        self.sudo()._guarded().write({"incident_raised": True})


class FixDataBackupPlanCapture(models.Model):
    _inherit = "fix.data.backup.plan"

    run_ids = fields.One2many("fix.data.backup.run", "plan_id", string="Job Runs")
    last_run_outcome = fields.Selection(
        [
            ("success", "Succeeded"),
            ("partial", "Completed with Warnings"),
            ("failed", "Failed"),
            ("missed", "Missed"),
        ],
        compute="_compute_last_run",
        string="Last Job",
    )
    consecutive_failures = fields.Integer(
        compute="_compute_last_run", string="Failed Runs in a Row"
    )

    @api.depends("run_ids.outcome", "run_ids.started_at")
    def _compute_last_run(self):
        for plan in self:
            runs = plan.run_ids.sorted(key=lambda r: (r.started_at, r.id), reverse=True)
            plan.last_run_outcome = runs[:1].outcome or False
            streak = 0
            for run in runs:
                if run.outcome not in _FAILED_RUN:
                    break
                streak += 1
            plan.consecutive_failures = streak


class FixDataBackupTestCapture(models.Model):
    """A restore test as a record a person captures: what was restored, how
    much, and the evidence. A test that 'passed' with nothing to show proves
    nothing (FR-DTS-013, AUT-DTS-12)."""

    _inherit = "fix.data.backup.test"

    operating_unit_id = fields.Many2one(
        "operating.unit", related="plan_id.operating_unit_id", store=True, readonly=True
    )
    scope_tested = fields.Text(string="What Was Restored (scope)")
    evidence_attachment_id = fields.Many2one(
        "ir.attachment", string="Restore Evidence (report, screenshot)", ondelete="restrict"
    )

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            if not self.env.su:
                vals.pop("tested_by", None)
            if vals.get("result") not in ("passed", "partial", "failed"):
                raise UserError("A restore test result is one of: passed, partial, failed")
            when = fields.Datetime.to_datetime(vals.get("tested_at")) or now
            if when > now + timedelta(minutes=5):
                raise UserError("A restore test is recorded after it was run.")
            if (vals.get("restored_gb") or 0) < 0:
                raise UserError("The restored volume cannot be negative.")
            if vals["result"] == "passed" and not vals.get("evidence_attachment_id"):
                raise UserError(
                    "Attach the evidence of the restore (the restore report or a screenshot of "
                    "the restored data): a passed test without evidence proves nothing."
                )
        records = super().create(vals_list)
        today = fields.Date.context_today(self)
        for test in records:
            plan = test.plan_id.sudo()
            plan.next_test_due = today + timedelta(days=plan.test_frequency_days or 90)
            publish(
                self.env,
                "data_case.backup_test_logged",
                "fix.data.backup.plan",
                plan.id,
                {"result": test.result, "restored_gb": float(test.restored_gb or 0.0)},
            )
        return records

    def write(self, vals):
        if not self.env.su:
            for rec in self:
                changed = [
                    n
                    for n in vals
                    if n in rec._fields
                    and rec._fields[n].type not in ("one2many",)
                    and _differs(rec, n, vals[n])
                ]
                if changed:
                    raise UserError(
                        "A restore test is a record of what happened; it cannot be edited."
                    )
        return super().write(vals)


def _differs(rec, name, value):
    field = rec._fields[name]
    try:
        new = field.convert_to_record(field.convert_to_cache(value, rec), rec)
    except Exception:
        return True
    old = rec[name]
    if field.type == "many2one":
        return (new.id or False) != (old.id or False)
    if field.type == "float":
        return abs((new or 0.0) - (old or 0.0)) > 1e-6
    return (new or False) != (old or False)


# --------------------------------------------------------------------------
# the case: intake facts, undertakings gate, holds, per-type inventory
# --------------------------------------------------------------------------


class FixDataRecoveryCaseCapture(models.Model):
    _inherit = "fix.data.recovery.case"

    # FR-DTS-001 / 028: what the customer reports and needs
    failure_symptoms = fields.Text(string="Failure Symptoms (as the customer reports them)")
    criticality = fields.Selection(
        [
            ("standard", "Standard"),
            ("business_critical", "Business-Critical"),
            ("emergency", "Emergency (operations stopped)"),
        ],
        string="Criticality",
        default="standard",
        tracking=True,
    )
    target_data_description = fields.Text(
        string="Data the Customer Needs Back",
        help="Folders, systems or kinds of files the customer names - never file content.",
    )
    customer_declarations = fields.Text(
        string="Customer Declarations",
        help="E.g. that the customer owns the data or may hand it over, and any earlier repair "
        "or recovery attempt elsewhere.",
    )
    prior_recovery_attempt = fields.Boolean(string="Earlier Recovery Attempt Elsewhere (declared)")
    undertaking_ids = fields.One2many(
        "fix.data.confidentiality.undertaking", "case_id", string="Confidentiality Undertakings"
    )
    retention_hold_ids = fields.One2many(
        "fix.data.retention.hold", "case_id", string="Retention Holds"
    )
    inventory_line_ids = fields.One2many(
        "fix.data.recovered.inventory", "case_id", string="Recovered Data by File Type"
    )

    def _has_undertaking(self, user):
        self.ensure_one()
        return bool(
            self.env["fix.data.confidentiality.undertaking"]
            .sudo()
            .search_count(
                [
                    ("case_id", "=", self.id),
                    ("user_id", "=", user.id),
                    ("undertaking_type", "=", "staff"),
                    ("state", "=", "active"),
                    "|",
                    ("valid_until", "=", False),
                    ("valid_until", ">=", fields.Date.context_today(self)),
                ]
            )
        )

    def _require_undertakings(self, users):
        missing = [u for u in users if u and not self._has_undertaking(u)]
        if missing:
            raise AccessError(
                "Case %s: %s has not signed this case's confidentiality undertaking. Access is "
                "granted only after it is recorded (BRU-DTS-12): Access Control & Audit > "
                "Staff Confidentiality Undertaking."
                % (self.name, ", ".join(u.name for u in missing))
            )

    def action_assign_staff(self, technician=None, custodian=None):
        """BRU-DTS-12: no one is named on a case - which is what grants access
        to its data - before their undertaking for THAT case is on record."""
        # The role checks in super() keep their own refusals: a person without
        # the role is refused for that, whatever their undertakings.
        if not self.env.su and self.env.user.has_group(GROUP_OPERATOR):
            for rec in self:
                tech = (
                    _resolve_user(self.env, technician)
                    if technician
                    else rec.assigned_technician_id
                )
                cust = _resolve_user(self.env, custodian) if custodian else rec.z4_custodian_id
                rec._require_undertakings(
                    [
                        tech.filtered(lambda u: u.has_group(GROUP_OPERATOR)),
                        cust.filtered(lambda u: u.has_group(GROUP_Z4_CUSTODIAN)),
                    ]
                )
        return super().action_assign_staff(technician=technician, custodian=custodian)

    def _z4_assert_assigned(self, what):
        """...and a revoked undertaking stops the person working the case."""
        super()._z4_assert_assigned(what)
        if not self.env.su:
            for rec in self:
                rec._require_undertakings([self.env.user])

    # ---- retention holds ---------------------------------------------------
    def _active_retention_hold(self):
        self.ensure_one()
        return (
            self.env["fix.data.retention.hold"]
            .sudo()
            .search(
                [
                    ("case_id", "=", self.id),
                    ("state", "=", "approved"),
                    ("hold_until", ">=", fields.Date.context_today(self)),
                ],
                order="hold_until desc",
                limit=1,
            )
        )

    def _retention_held(self):
        return bool(self._active_retention_hold())

    @api.model
    def cron_retention_purge(self):
        self.env["fix.data.retention.hold"]._expire_ended()
        return super().cron_retention_purge()

    def action_purge(self, certificate=None):
        for rec in self:
            hold = rec._active_retention_hold() if rec.state == "handover" else None
            if hold:
                raise UserError(
                    "Case %s is under an approved retention hold until %s (%s). The data is "
                    "kept until then; release the hold first if it is no longer needed."
                    % (rec.name, hold.hold_until, hold.reason)
                )
        return super().action_purge(certificate)

    # ---- per-type inventory ------------------------------------------------
    def _sync_inventory_totals(self):
        for rec in self:
            lines = rec.inventory_line_ids
            rec._guarded().write(
                {
                    "recovered_files_count": sum(lines.mapped("file_count")),
                    "recovered_volume_gb": round(sum(lines.mapped("size_gb")), 3),
                }
            )

    def action_record_inventory(self, files_count=None, volume_gb=None):
        for rec in self:
            if rec.inventory_line_ids:
                raise UserError(
                    "Case %s's inventory is recorded by file type: its totals are the sum of "
                    "those lines. Correct a line instead." % rec.name
                )
        return super().action_record_inventory(files_count=files_count, volume_gb=volume_gb)
