# fix_device_lineage — M17 identifier history (FR-AST-002), NEIR status per
# IMEI (B4) and duplicate-merge lineage (FR-AST-007, BRU-AST-04).
#
# A07 audit (2026-11-04), P2: an IMEI could be rewritten or moved with no
# trail (M17-2), and a merge archived the duplicate but left its history,
# warranties and orders on the dead record, published nothing and could not
# be reversed (M17-3, live DIDR/2026/0002). Every row here is written by
# registry service code only; users read them.
import json
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import SQL
from psycopg2 import IntegrityError

from .fix_device import BRANCH_MANAGER_GROUP, NEIR_ON_TRANSFER_PARAM, QUALITY_MANAGER_GROUP

IDENTIFIER_TYPES = [
    ("serial_number", "Serial Number"),
    ("imei_1", "IMEI 1"),
    ("imei_2", "IMEI 2"),
]
NEIR_STATES = [
    ("not_checked", "Not checked"),
    ("registered", "Registered on NEIR"),
    ("deregistration_pending", "De-registration pending"),
    ("deregistered", "De-registered"),
    ("blocked", "Blocked / blacklisted"),
]
# Worst first: the device shows the worst status of its current IMEIs.
_NEIR_RANK = ["blocked", "deregistration_pending", "deregistered", "registered", "not_checked"]
# Spec FR-AST-007: "reversible for a configurable period". The spec gives no
# number; 30 days is a default the business must confirm (B2).
MERGE_REVERSAL_DAYS_PARAM = "cd_device_registry.merge_reversal_days"
MERGE_REVERSAL_DAYS_DEFAULT = 30
# Tables whose device link is the lineage itself, never re-pointed by a merge.
_NOT_REPOINTED = {
    ("fix.device.identity", "primary_device_id"),
    ("fix.device.identity", "duplicate_device_id"),
    ("fix.device.merge", "survivor_id"),
    ("fix.device.merge", "merged_id"),
    ("fix.device.identifier", "device_id"),
}


def _insert_only(records, verb):
    if not records._fix_guard_open():
        raise UserError(
            "%s is a permanent registry record written by the registry itself; it cannot be "
            "%s by hand." % (records._description, verb)
        )


class FixDeviceIdentifier(models.Model):
    """One identifier value bound to a device, with its source and capture
    date; a correction supersedes the row and never deletes it."""

    _name = "fix.device.identifier"
    _description = "Device Identifier History"
    _inherit = ["fix.guarded.mixin"]
    _order = "device_id, identifier_type, captured_at desc, id desc"
    _rec_name = "value"

    # cascade, as the ownership trail: only an administrator deletes a device,
    # and its identifiers go with it; a user never deletes either.
    device_id = fields.Many2one(
        "fix.device", string="Device", required=True, ondelete="cascade", index=True
    )
    identifier_type = fields.Selection(IDENTIFIER_TYPES, required=True, index=True)
    value = fields.Char(required=True, index=True)
    value_normalised = fields.Char(index=True)
    source = fields.Selection(
        [
            ("registration", "Registration"),
            ("capture", "Captured later (intake)"),
            ("correction", "Correction"),
            ("backfill", "Recorded from the device record (captured before history existed)"),
        ],
        required=True,
    )
    captured_by_id = fields.Many2one("res.users", string="Captured By")
    captured_at = fields.Datetime(string="Captured At", required=True)
    is_current = fields.Boolean(string="Current", default=True, index=True)
    superseded_at = fields.Datetime(string="Superseded At")
    superseded_by_id = fields.Many2one("res.users", string="Superseded By")
    supersede_reason = fields.Char(string="Correction Reason")
    # B4: the BTRC NEIR status of an IMEI, as last recorded with a reference.
    neir_status = fields.Selection(NEIR_STATES, string="NEIR Status", default="not_checked")
    neir_reference = fields.Char(string="NEIR Reference")
    neir_checked_at = fields.Datetime(string="NEIR Recorded At")
    neir_checked_by_id = fields.Many2one("res.users", string="NEIR Recorded By")

    @api.model_create_multi
    def create(self, vals_list):
        _insert_only(self, "created")
        return super().create(vals_list)

    def write(self, vals):
        _insert_only(self, "edited")
        return super().write(vals)

    def unlink(self):
        _insert_only(self, "deleted")
        return super().unlink()

    def action_record_neir_status(self, status=None, reference=None):
        """Record the NEIR result of an IMEI (Branch Manager, with the BTRC or
        operator reference). Only IMEI rows carry a NEIR status."""
        if status not in dict(NEIR_STATES):
            raise UserError("Unknown NEIR status %r." % (status,))
        if not (reference or "").strip():
            raise UserError("Give the NEIR / BTRC reference for this result.")
        for rec in self:
            rec.device_id._assert_role(BRANCH_MANAGER_GROUP, "Recording a NEIR result")
            if rec.identifier_type not in ("imei_1", "imei_2") or not rec.is_current:
                raise UserError("A NEIR result is recorded on a current IMEI only.")
            # users read identifier rows only; the result is written by the registry
            rec.sudo()._guarded().write(
                {
                    "neir_status": status,
                    "neir_reference": reference.strip(),
                    "neir_checked_at": fields.Datetime.now(),
                    "neir_checked_by_id": self.env.uid,
                }
            )
            rec.device_id._publish(
                "device.neir_status_recorded",
                {
                    "device_id": rec.device_id.id,
                    "imei": rec.value,
                    "neir_status": status,
                    "reference": reference.strip(),
                    "recorded_by": self.env.uid,
                },
            )
        return True

    # P03 buttons: one typed value (the reference) per action.
    def action_neir_registered(self, reference=None):
        return self.action_record_neir_status("registered", reference)

    def action_neir_deregistered(self, reference=None):
        return self.action_record_neir_status("deregistered", reference)

    def action_neir_blocked(self, reference=None):
        return self.action_record_neir_status("blocked", reference)


class FixDeviceMerge(models.Model):
    """The lineage of an approved merge: both records, who approved it, the
    reference map of every row re-pointed, and its reversal."""

    _name = "fix.device.merge"
    _description = "Device Merge Lineage"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "merged_at desc, id desc"

    name = fields.Char(related="identity_id.name", store=True)
    company_id = fields.Many2one(related="survivor_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="survivor_id.operating_unit_id", store=True, index=True, string="Operating Unit"
    )
    identity_id = fields.Many2one(
        "fix.device.identity", string="Resolution", required=True, ondelete="restrict"
    )
    survivor_id = fields.Many2one(
        "fix.device", string="Surviving Device", required=True, ondelete="restrict", index=True
    )
    merged_id = fields.Many2one(
        "fix.device", string="Merged Device", required=True, ondelete="restrict", index=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By")
    requested_by_id = fields.Many2one("res.users", string="Requested By")
    reason = fields.Text(string="Justification")
    merged_at = fields.Datetime(required=True)
    reversible_until = fields.Date(string="Reversible Until")
    reference_map = fields.Text(
        string="Reference Map",
        help="JSON: model -> field -> ids re-pointed from the merged device to the survivor.",
    )
    rows_repointed = fields.Integer(string="Rows Re-pointed")
    state = fields.Selection(
        [("merged", "Merged"), ("reversed", "Reversed")], required=True, default="merged"
    )
    reversed_at = fields.Datetime()
    reversed_by_id = fields.Many2one("res.users", string="Reversed By")
    reversal_reason = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        _insert_only(self, "created")
        return super().create(vals_list)

    def write(self, vals):
        _insert_only(self, "edited")
        return super().write(vals)

    def unlink(self):
        _insert_only(self, "deleted")
        return super().unlink()

    # ---- re-pointing --------------------------------------------------
    @api.model
    def _device_links(self):
        """(model, field, table, column) of every stored many2one to fix.device."""
        out = []
        for name in sorted(self.env.registry):
            model = self.env[name]
            if model._abstract or not model._auto or model._table_query:
                continue
            for fname, field in model._fields.items():
                if (
                    field.type == "many2one"
                    and field.comodel_name == "fix.device"
                    and field.store
                    and not field.inherited
                    and (name, fname) not in _NOT_REPOINTED
                ):
                    out.append((name, fname, model._table, fname))
        return out

    def _move(self, refmap, source, target):
        """Move the rows in `refmap` from `source` to `target` (raw SQL: the
        guards that freeze history are for users, and this is the registry's
        own lineage service). Returns the ids actually moved per model/field."""
        cr = self.env.cr
        moved = {}
        self.env.flush_all()
        for model_name, by_field in refmap.items():
            if model_name not in self.env.registry:
                continue
            model = self.env[model_name]
            for fname, ids in by_field.items():
                field = model._fields.get(fname)
                if not ids or not field or not field.store:
                    continue
                try:
                    with cr.savepoint():
                        cr.execute(
                            SQL(
                                "UPDATE %s SET %s = %s WHERE id = ANY(%s) AND %s = %s RETURNING id",
                                SQL.identifier(model._table),
                                SQL.identifier(fname),
                                target.id,
                                list(ids),
                                SQL.identifier(fname),
                                source.id,
                            )
                        )
                        done = [r[0] for r in cr.fetchall()]
                except IntegrityError:
                    # A unique key (one row per device) keeps that row where it is.
                    done = []
                if done:
                    moved.setdefault(model_name, {})[fname] = done
                    recs = model.browse(done)
                    recs.invalidate_recordset([fname])
                    recs.modified([fname])
        self.env.invalidate_all()
        return moved

    @api.model
    def _record(self, identity):
        """Re-point every row of the duplicate to the survivor and keep the
        lineage. Called by fix.device.identity.action_merge (service code)."""
        survivor, dup = identity.primary_device_id, identity.duplicate_device_id
        cr = self.env.cr
        self.env.flush_all()
        found = {}
        for model_name, fname, table, column in self._device_links():
            cr.execute(
                SQL(
                    "SELECT id FROM %s WHERE %s = %s",
                    SQL.identifier(table),
                    SQL.identifier(column),
                    dup.id,
                )
            )
            ids = [r[0] for r in cr.fetchall()]
            if ids:
                found.setdefault(model_name, {})[fname] = ids
        # Documents hang off a device by model and id, not a many2one, so the
        # sweep above never saw them: the merge left them on the archived row.
        cr.execute(
            "SELECT id FROM fix_document WHERE res_model = 'fix.device' AND res_id = %s", (dup.id,)
        )
        documents = [r[0] for r in cr.fetchall()]
        if documents:
            found.setdefault("fix.document", {})["res_id"] = documents
        moved = self._move(found, dup, survivor)
        days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(MERGE_REVERSAL_DAYS_PARAM, MERGE_REVERSAL_DAYS_DEFAULT)
            or 0
        )
        req = identity.approval_request_id.sudo()
        lineage = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "identity_id": identity.id,
                    "survivor_id": survivor.id,
                    "merged_id": dup.id,
                    "approved_by_id": self.env.uid,
                    "requested_by_id": req.requested_by_id.id or False,
                    "reason": req.justification or identity.match_reason,
                    "merged_at": fields.Datetime.now(),
                    "reversible_until": fields.Date.context_today(self) + timedelta(days=days),
                    "reference_map": json.dumps(moved, sort_keys=True),
                    "rows_repointed": sum(len(i) for f in moved.values() for i in f.values()),
                }
            )
        )
        survivor._publish(
            "device.merged",
            {
                "resolution": identity.name,
                "survivor_id": survivor.id,
                "merged_id": dup.id,
                "approved_by": self.env.uid,
                "reference_map": {m: {f: len(i) for f, i in v.items()} for m, v in moved.items()},
                "reversible_until": str(lineage.reversible_until),
            },
        )
        return lineage

    def action_reverse(self, reason=None):
        """Undo a merge inside its window (BRU-AST-04): the rows the merge
        moved go back, the duplicate is restored, the resolution reads
        reversed. A Device Quality Manager decides it, with a reason."""
        if not (reason or "").strip():
            raise UserError("Give the reason the merge is reversed.")
        today = fields.Date.context_today(self)
        for rec in self:
            rec.survivor_id._assert_role(QUALITY_MANAGER_GROUP, "Reversing a device merge")
            if rec.state != "merged":
                raise UserError("%s is already reversed." % rec.display_name)
            if rec.reversible_until and today > rec.reversible_until:
                raise UserError(
                    "The reversal window of %s closed on %s."
                    % (rec.display_name, rec.reversible_until)
                )
            refmap = json.loads(rec.reference_map or "{}")
            svc = rec.sudo()
            svc._move(refmap, svc.survivor_id, svc.merged_id)
            svc.merged_id._guarded().write({"active": True})
            svc.identity_id._guarded().write({"state": "reversed"})
            svc._guarded().write(
                {
                    "state": "reversed",
                    "reversed_at": fields.Datetime.now(),
                    "reversed_by_id": self.env.uid,
                    "reversal_reason": reason.strip(),
                }
            )
            svc.merged_id.message_post(
                body="Merge %s reversed by %s: %s" % (rec.display_name, self.env.user.name, reason)
            )
            svc.survivor_id._publish(
                "device.merge_reversed",
                {
                    "resolution": rec.name,
                    "survivor_id": rec.survivor_id.id,
                    "merged_id": rec.merged_id.id,
                    "reason": reason.strip(),
                    "reversed_by": self.env.uid,
                },
            )
        return True


class FixDeviceLineage(models.Model):
    _inherit = "fix.device"

    identifier_ids = fields.One2many(
        "fix.device.identifier", "device_id", string="Identifier History"
    )
    neir_status = fields.Selection(
        NEIR_STATES,
        string="NEIR Status",
        compute="_compute_neir_status",
        help="The worst NEIR status recorded on the device's current IMEIs (B4).",
    )

    @api.depends("identifier_ids.neir_status", "identifier_ids.is_current")
    def _compute_neir_status(self):
        for rec in self:
            states = {
                i.neir_status
                for i in rec.identifier_ids
                if i.is_current and i.identifier_type in ("imei_1", "imei_2")
            }
            rec.neir_status = next((s for s in _NEIR_RANK if s in states), "not_checked")

    @api.model
    def resolve_identifier(self, code):
        """The device an identifier a person holds belongs to: the registered one,
        or the survivor when it was merged away (FR-AST-004, the intake lookup).
        The match is normalised for case and spacing, across archived devices, and
        the caller's own record rules decide whether the answer may be read."""
        code = (code or "").strip()
        if not code:
            return self.browse()
        self.flush_model(["serial_number", "imei_1", "imei_2", "active"])
        self.env.cr.execute(
            "SELECT id FROM fix_device WHERE upper(btrim(serial_number)) = upper(%s) "
            "OR imei_1 = %s OR imei_2 = %s ORDER BY active DESC NULLS LAST, id DESC LIMIT 1",
            (code, code, code),
        )
        row = self.env.cr.fetchone()
        if not row:
            return self.browse()
        device = self.sudo().with_context(active_test=False).browse(row[0])
        survivor = device._merge_survivor()
        return self.browse(survivor.ids)._filtered_access("read")

    @api.model
    def _identifier_backfill(self):
        """A row in the identifier history for every identifier a device already
        carries that has none (A07 operability M17: 0 rows against 53 IMEIs, so
        the NEIR actions had nothing to act on). It records what the device row
        says and nothing new; run again it adds nothing. Who captured it is not
        known, so it is left empty rather than guessed. Returns the rows added."""
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT device_id, identifier_type FROM fix_device_identifier WHERE is_current"
        )
        known = set(self.env.cr.fetchall())
        Identifier = self.env["fix.device.identifier"].sudo()._guarded()
        devices = (
            self.sudo()
            .with_context(active_test=False)
            .search(
                [
                    "|",
                    "|",
                    ("serial_number", "!=", False),
                    ("imei_1", "!=", False),
                    ("imei_2", "!=", False),
                ]
            )
        )
        now = fields.Datetime.now()
        vals = [
            {
                "device_id": device.id,
                "identifier_type": name,
                "value": device[name],
                "value_normalised": device[name].strip().upper(),
                "source": "backfill",
                "captured_at": device.create_date or now,
            }
            for device in devices
            for name, _label in IDENTIFIER_TYPES
            if device[name] and (device.id, name) not in known
        ]
        if vals:
            Identifier.create(vals)
        return len(vals)

    def _identifier_capture(self, names, source):
        """Record the current value of each named identifier (first capture)."""
        Identifier = self.env["fix.device.identifier"].sudo()._guarded()
        now = fields.Datetime.now()
        for rec in self:
            vals = [
                {
                    "device_id": rec.id,
                    "identifier_type": name,
                    "value": rec[name],
                    "value_normalised": rec[name].strip().upper(),
                    "source": source,
                    "captured_by_id": self.env.uid,
                    "captured_at": now,
                }
                for name in names
                if rec[name]
            ]
            if vals:
                Identifier.create(vals)

    def _identifier_supersede(self, name, old, new, reason):
        """A correction: the old value's row is superseded (created first, as
        a backfill, when it predates the history), the new value captured."""
        self.ensure_one()
        Identifier = self.env["fix.device.identifier"].sudo()._guarded()
        current = Identifier.search(
            [("device_id", "=", self.id), ("identifier_type", "=", name), ("is_current", "=", True)]
        )
        now = fields.Datetime.now()
        if not current and old:
            current = Identifier.create(
                {
                    "device_id": self.id,
                    "identifier_type": name,
                    "value": old,
                    "value_normalised": old.strip().upper(),
                    "source": "backfill",
                    "captured_at": self.create_date or now,
                }
            )
        current.write(
            {
                "is_current": False,
                "superseded_at": now,
                "superseded_by_id": self.env.uid,
                "supersede_reason": reason,
            }
        )
        if new:
            Identifier.create(
                {
                    "device_id": self.id,
                    "identifier_type": name,
                    "value": new,
                    "value_normalised": new.strip().upper(),
                    "source": "correction",
                    "captured_by_id": self.env.uid,
                    "captured_at": now,
                }
            )

    def _neir_assert_not_blocked(self, what):
        for rec in self:
            if rec.neir_status == "blocked":
                raise UserError(
                    "An IMEI of %s is blocked on the NEIR register; it cannot %s."
                    % (rec.display_name, what)
                )

    def _neir_on_transfer(self, old_owner, new_owner):
        """B4: when the business switches NEIR de-registration on, a transfer
        marks the IMEIs de-registration pending and tells the bridge."""
        param = self.env["ir.config_parameter"].sudo().get_param(NEIR_ON_TRANSFER_PARAM, "0")
        if str(param).strip().lower() not in ("1", "true", "yes", "on"):
            return
        for rec in self:
            rows = rec.identifier_ids.sudo().filtered(
                lambda i: i.is_current and i.identifier_type in ("imei_1", "imei_2")
            )
            if not rows:
                continue
            rows._guarded().write({"neir_status": "deregistration_pending"})
            rec._publish(
                "device.neir_deregistration_required",
                {
                    "device_id": rec.id,
                    "imeis": rows.mapped("value"),
                    "from_owner_id": old_owner.id or None,
                    "to_owner_id": new_owner.id,
                },
            )
