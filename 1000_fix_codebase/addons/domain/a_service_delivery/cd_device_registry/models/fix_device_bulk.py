# fix.device.bulk.load — bulk estate registration (FR-AST-039, BRU-AST-18,
# T-10, AUT-AST-11).
#
# M17 capture audit (2026-11-13): the "Bulk Registration" page was a readiness
# report and nothing else - a corporate estate of hundreds of devices could only
# be typed one asset at a time. The spec asks for a validated file upload that
# resolves each row against the existing registry, reports rejects line by
# line, and commits as a set: one bad row rejects the whole batch.
#
# Validation runs every new row through the same registration a person meets on
# the asset form (identifier rules, catalogue model, estate ownership), inside a
# savepoint that is always rolled back, so the reject report names exactly what
# the commit would refuse. The commit repeats it for real, all or nothing.
import base64
import csv
import io
import re
from datetime import date, datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_device import REGISTRY_AGENT_GROUP

MAX_ROWS = 5000

# file header (lower case, spaces and dashes as "_") -> line field
COLUMNS = {
    "serial_number": "serial_number",
    "serial": "serial_number",
    "serial_no": "serial_number",
    "imei_1": "imei_1",
    "imei1": "imei_1",
    "imei": "imei_1",
    "imei_2": "imei_2",
    "imei2": "imei_2",
    "mac_address": "mac_address",
    "mac": "mac_address",
    "legacy_reference": "legacy_reference",
    "legacy_ref": "legacy_reference",
    "asset_number": "legacy_reference",
    "model": "model_ref",
    "model_code": "model_ref",
    "device_model": "model_ref",
    "purchase_date": "purchase_date_raw",
}
IDENTIFIERS = ("serial_number", "imei_1", "imei_2", "mac_address", "legacy_reference")

# a batch of registrations must not queue one chatter notification per device
QUIET = {
    "tracking_disable": True,
    "mail_create_nolog": True,
    "mail_create_nosubscribe": True,
    "mail_notrack": True,
    "mail_notify_force_send": False,
}


class _DryRun(Exception):
    """Raised to roll the validation savepoint back."""


def _cell(value):
    """A spreadsheet cell as text. Excel turns a 15-digit IMEI into a number."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()


def _header(value):
    return re.sub(r"[\s\-/]+", "_", _cell(value).lower()).strip("_")


def _norm(value):
    return (value or "").strip().upper()


class FixDeviceBulkLoad(models.Model):
    _name = "fix.device.bulk.load"
    _description = "Device Bulk Registration"
    _inherit = ["fix.guarded.mixin"]
    _order = "id desc"

    def _fix_guarded_fields(self) -> set:
        # the outcome of the validation and the commit is never typed
        return super()._fix_guarded_fields() | {
            "state",
            "validated_on",
            "validated_by_id",
            "committed_on",
            "committed_by_id",
        }

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    estate_id = fields.Many2one(
        "fix.device.estate", string="Corporate Estate", required=True, ondelete="restrict"
    )
    client_id = fields.Many2one(
        related="estate_id.client_id", store=True, string="Client", readonly=True
    )
    branch_id = fields.Many2one("fix.branch", string="Registered At")
    upload_file = fields.Binary(string="Estate File (CSV or Excel)", attachment=True)
    upload_filename = fields.Char(string="File Name")
    state = fields.Selection(
        [
            ("draft", "Uploaded"),
            ("validated", "Validated: Ready to Commit"),
            ("rejected", "Rejected: See the Lines"),
            ("committed", "Committed"),
        ],
        required=True,
        default="draft",
        index=True,
    )
    line_ids = fields.One2many("fix.device.bulk.line", "load_id", string="Lines")
    line_count = fields.Integer(string="Rows", compute="_compute_counts")
    new_count = fields.Integer(string="New Devices", compute="_compute_counts")
    place_count = fields.Integer(string="Existing Devices Joining", compute="_compute_counts")
    error_count = fields.Integer(string="Rejected Rows", compute="_compute_counts")
    validated_on = fields.Datetime(readonly=True, copy=False)
    validated_by_id = fields.Many2one("res.users", string="Validated By", readonly=True)
    committed_on = fields.Datetime(readonly=True, copy=False)
    committed_by_id = fields.Many2one("res.users", string="Committed By", readonly=True)
    notes = fields.Text()

    @api.depends("line_ids.status")
    def _compute_counts(self):
        for rec in self:
            statuses = rec.line_ids.mapped("status")
            rec.line_count = len(statuses)
            rec.new_count = statuses.count("new") + statuses.count("done")
            rec.place_count = statuses.count("place") + statuses.count("placed")
            rec.error_count = statuses.count("error")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.device.bulk.load") or "DBULK/New"
                )
        records = super().create(vals_list)
        # AUT-AST-11: an uploaded file is validated at once
        for rec in records.filtered("upload_file"):
            rec._validate()
        return records

    def write(self, vals):
        if not self._fix_guard_open() and self.filtered(lambda r: r.state == "committed"):
            raise UserError("A committed bulk registration is a record; it is not changed.")
        result = super().write(vals)
        if {"upload_file", "estate_id", "branch_id"} & set(vals) and not self._fix_guard_open():
            # what was validated is no longer what would be committed
            for rec in self:
                rec._guarded().write({"state": "draft"})
                rec.line_ids.sudo().unlink()
                if rec.upload_file:
                    rec._validate()
        return result

    def unlink(self):
        if self.filtered(lambda r: r.state == "committed"):
            raise UserError("A committed bulk registration cannot be deleted.")
        return super().unlink()

    # ------------------------------------------------------------- the file
    def _rows(self):
        """[(row number, {line field: text})] from the uploaded CSV or XLSX."""
        self.ensure_one()
        if not self.upload_file:
            raise UserError("Upload the estate file (CSV or Excel) first.")
        raw = base64.b64decode(self.upload_file)
        name = (self.upload_filename or "").lower()
        if raw[:2] == b"PK" or name.endswith(".xlsx"):
            import openpyxl

            try:
                book = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
            except Exception as exc:
                raise UserError("The Excel file could not be read: %s" % exc) from exc
            table = [
                [_cell(v) for v in row] for row in book.worksheets[0].iter_rows(values_only=True)
            ]
        else:
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw.decode("cp1252")
            sample = text[:4096]
            delimiter = max((",", ";", "\t"), key=sample.count)
            table = [
                [c.strip() for c in row]
                for row in csv.reader(io.StringIO(text), delimiter=delimiter)
            ]
        table = [(i + 1, row) for i, row in enumerate(table) if any(row)]
        if not table:
            raise UserError("The file has no rows.")
        header_no, header = table[0]
        names = [COLUMNS.get(_header(h)) for h in header]
        if "model_ref" not in names:
            raise UserError(
                "Row %s is the header and needs a Model column (model name or model code), "
                "with Serial Number and/or IMEI 1 columns. Optional: IMEI 2, MAC Address, "
                "Legacy Reference, Purchase Date (YYYY-MM-DD)." % header_no
            )
        if not {"serial_number", "imei_1", "imei_2"} & set(names):
            raise UserError("The file needs a Serial Number or an IMEI column.")
        rows = []
        for number, row in table[1:]:
            values = {}
            for field, cell in zip(names, row, strict=False):
                if field and cell and not values.get(field):
                    values[field] = cell
            if values:
                rows.append((number, values))
        if not rows:
            raise UserError("The file has a header but no device rows.")
        if len(rows) > MAX_ROWS:
            raise UserError(
                "The file has %s rows; split it into files of at most %s." % (len(rows), MAX_ROWS)
            )
        return rows

    def _resolve_model(self, ref, cache):
        """The M37 catalogue model a row names (BRU-AST-12: never free-typed)."""
        key = ref.strip().lower()
        if key not in cache:
            Model = self.env["fix.device.model"]
            found = Model.search([("model_code", "=ilike", ref.strip())])
            if not found:
                found = Model.search([("name", "=ilike", ref.strip())])
            cache[key] = found
        found = cache[key]
        if not found:
            return None, "Model '%s' is not in the device catalogue." % ref
        if len(found) > 1:
            return None, "Model '%s' matches %s catalogue models; use the model code." % (
                ref,
                len(found),
            )
        return found, None

    def _existing(self, line):
        """The active registered device this row's identifiers already name."""
        Device = self.env["fix.device"].sudo()
        hits = Device.browse()
        if line.serial_number:
            self.env.cr.execute(
                "SELECT id FROM fix_device WHERE active AND upper(btrim(serial_number)) = %s",
                (_norm(line.serial_number),),
            )
            hits |= Device.browse([r[0] for r in self.env.cr.fetchall()])
        imeis = [v for v in (line.imei_1, line.imei_2) if v]
        if imeis:
            hits |= Device.search(["|", ("imei_1", "in", imeis), ("imei_2", "in", imeis)])
        return hits

    # ------------------------------------------------------------- validation
    def action_validate(self):
        for rec in self:
            if rec.state == "committed":
                raise UserError("%s is already committed." % rec.name)
            rec._validate()
        return True

    def _validate(self):
        """Stage the file as lines and say, row by row, what the commit would do."""
        self.ensure_one()
        rows = self._rows()
        Line = self.env["fix.device.bulk.line"].sudo()
        self.line_ids.sudo().unlink()
        lines = Line.create(
            [
                {"load_id": self.id, "row_no": number, "company_id": self.company_id.id, **values}
                for number, values in rows
            ]
        )
        verdicts = {}
        models_cache = {}
        seen = {}
        client = self.estate_id.client_id
        for line in lines:
            if not line.model_ref:
                verdicts[line.id] = ("error", "Give the model.", False, False)
                continue
            device_model, problem = self._resolve_model(line.model_ref, models_cache)
            if problem:
                verdicts[line.id] = ("error", problem, False, False)
                continue
            if not (line.serial_number or line.imei_1 or line.imei_2):
                verdicts[line.id] = ("error", "Give the serial number or an IMEI.", False, False)
                continue
            clash = None
            for name in ("serial_number", "imei_1", "imei_2"):
                value = _norm(line[name])
                if not value:
                    continue
                key = ("serial" if name == "serial_number" else "imei", value)
                if key in seen:
                    clash = "%s %s is also on row %s." % (
                        self.env["fix.device.bulk.line"]._fields[name].string,
                        line[name],
                        seen[key],
                    )
                    break
                seen[key] = line.row_no
            if clash:
                verdicts[line.id] = ("error", clash, device_model.id, False)
                continue
            existing = self._existing(line)
            if len(existing) > 1:
                verdicts[line.id] = (
                    "error",
                    "Its identifiers name %s different registered devices; a Quality Manager "
                    "resolves the conflict first." % len(existing),
                    device_model.id,
                    False,
                )
            elif existing:
                if existing.estate_id == self.estate_id:
                    verdicts[line.id] = (
                        "present",
                        "%s is already in this estate." % existing.name,
                        existing.device_model_id.id,
                        existing.id,
                    )
                elif existing._owner_is(client):
                    verdicts[line.id] = (
                        "place",
                        "%s is registered to the client and joins this estate." % existing.name,
                        existing.device_model_id.id,
                        existing.id,
                    )
                else:
                    verdicts[line.id] = (
                        "error",
                        "Already registered to another owner; it joins the estate only after an "
                        "ownership transfer.",
                        device_model.id,
                        False,
                    )
            else:
                verdicts[line.id] = ("new", "", device_model.id, False)
        # The rows that look new are registered for real, as the person who
        # uploaded them, and rolled back: the rules a registration meets decide.
        new_lines = lines.filtered(lambda ln: verdicts[ln.id][0] == "new")
        refusals = {}
        try:
            with self.env.cr.savepoint():
                for line in new_lines:
                    try:
                        with self.env.cr.savepoint():
                            self._register_row(line, verdicts[line.id][2])
                    except Exception as exc:
                        refusals[line.id] = _reason(exc)
                raise _DryRun
        except _DryRun:
            pass
        for line_id, reason in refusals.items():
            verdicts[line_id] = ("error", reason, verdicts[line_id][2], False)
        for line in lines:
            status, message, model_id, device_id = verdicts[line.id]
            line.write(
                {
                    "status": status,
                    "message": message or False,
                    "device_model_id": model_id or False,
                    "device_id": device_id or False,
                }
            )
        errors = sum(1 for v in verdicts.values() if v[0] == "error")
        self._guarded().write(
            {
                "state": "rejected" if errors else "validated",
                "validated_on": fields.Datetime.now(),
                "validated_by_id": self.env.uid,
            }
        )
        return True

    def _register_row(self, line, model_id):
        purchase = False
        if line.purchase_date_raw:
            try:
                purchase = fields.Date.to_date(line.purchase_date_raw[:10])
            except ValueError as exc:
                raise UserError(
                    "Purchase date '%s' is not a date (YYYY-MM-DD)." % line.purchase_date_raw
                ) from exc
        vals = {
            "device_model_id": model_id,
            "owner_id": self.estate_id.client_id.id,
            "estate_id": self.estate_id.id,
            "company_id": self.company_id.id,
            "purchase_date": purchase,
        }
        if self.branch_id:
            vals["branch_id"] = self.branch_id.id
        for name in IDENTIFIERS:
            if line[name]:
                vals[name] = line[name]
        return self.env["fix.device"].with_context(**QUIET).create(vals)

    # ------------------------------------------------------------- commit
    def action_commit(self):
        """BRU-AST-18: every row is registered or placed, or none is."""
        self.ensure_one()
        if not self.env.su and not self.env.user.has_group(REGISTRY_AGENT_GROUP):
            group = self.env.ref(REGISTRY_AGENT_GROUP, raise_if_not_found=False)
            raise UserError(
                "Committing a bulk registration needs the %s role."
                % (group.sudo().name if group else REGISTRY_AGENT_GROUP)
            )
        if self.state != "validated" or self.error_count:
            raise UserError(
                "%s is not validated clean: correct the rejected rows in the file, upload it "
                "again and validate." % self.name
            )
        done = {}
        with self.env.cr.savepoint():
            for line in self.line_ids.sorted("row_no"):
                try:
                    if line.status == "new":
                        done[line.id] = (
                            "done",
                            self._register_row(line, line.device_model_id.id).id,
                        )
                    elif line.status == "place":
                        device = line.device_id.with_context(**QUIET)
                        device.write({"estate_id": self.estate_id.id})
                        done[line.id] = ("placed", device.id)
                except Exception as exc:
                    raise UserError(
                        "Row %s: %s Nothing in %s was registered; validate it again."
                        % (line.row_no, _reason(exc), self.name)
                    ) from exc
        for line in self.line_ids:
            if line.id in done:
                status, device_id = done[line.id]
                line.sudo().write({"status": status, "device_id": device_id})
        self._guarded().write(
            {
                "state": "committed",
                "committed_on": fields.Datetime.now(),
                "committed_by_id": self.env.uid,
            }
        )
        return True


def _reason(exc):
    """A refusal in words a person can act on."""
    if getattr(exc, "pgcode", None) == "23505" or type(exc).__name__ in (
        "IntegrityError",
        "UniqueViolation",
    ):
        return "An identifier is already registered (or repeated in this file)."
    message = getattr(exc, "args", None) and exc.args[0]
    return str(message or exc).strip()


class FixDeviceBulkLine(models.Model):
    _name = "fix.device.bulk.line"
    _description = "Device Bulk Registration Line"
    _order = "load_id desc, row_no"
    _rec_name = "row_no"

    load_id = fields.Many2one(
        "fix.device.bulk.load",
        string="Bulk Registration",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one("res.company", required=True, index=True)
    row_no = fields.Integer(string="File Row")
    serial_number = fields.Char(string="Serial Number")
    imei_1 = fields.Char(string="IMEI 1")
    imei_2 = fields.Char(string="IMEI 2")
    mac_address = fields.Char(string="MAC Address")
    legacy_reference = fields.Char(string="Legacy Reference")
    model_ref = fields.Char(string="Model in File")
    purchase_date_raw = fields.Char(string="Purchase Date in File")
    device_model_id = fields.Many2one("fix.device.model", string="Catalogue Model")
    status = fields.Selection(
        [
            ("new", "Will Be Registered"),
            ("place", "Registered: Will Join the Estate"),
            ("present", "Already in the Estate"),
            ("error", "Rejected"),
            ("done", "Registered"),
            ("placed", "Joined the Estate"),
        ],
        index=True,
    )
    message = fields.Char(string="Why")
    device_id = fields.Many2one("fix.device", string="Device")
