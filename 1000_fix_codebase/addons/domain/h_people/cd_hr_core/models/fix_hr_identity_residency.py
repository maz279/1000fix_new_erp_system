# cd_hr_core — personal identifiers in the Bangladesh-resident store (A09
# workflow audit M21-A6 / M21-9, report P2; BRU-HCM-06 "NID/TIN only in the
# resident store", BRU-HCM-07 "S3 fields access-logged"; FF-09 "residency
# fields only via libs/py/fix_residency").
#
# The audit found the NID and the e-TIN in clear in hr_employee [E A6], and a
# docstring claiming the opposite; the passport, the nominee's NID and every
# dependant's NID sat in clear beside them. Here, following
# fix.identity.document and the residency.mixin (cd_rbac_ext), for
#   hr.employee:      nid_number, tin_number, birth_reg_number, passport_number,
#                     nominee_nid;
#   fix.hr.dependant: nid:
#
#   * the value goes to Z4 through libs/py/fix_residency, the only client. The
#     regional row keeps one pointer (`residency_ref`, a UUID) and, per
#     identifier, an HMAC-SHA256 of the normalised value keyed by an
#     ir.config_parameter created at install. The hash serves uniqueness and
#     duplicate detection; it never serves the value back;
#   * the ORM API is unchanged: each field is read (a compute), written (an
#     inverse) and searched with = (a search method) from Python and the forms,
#     so the hire copy, the duplicate check and Form 6(a) keep working;
#   * the format, where one exists, is checked at write time BEFORE the value
#     is routed; a duplicate NID or e-TIN is refused through the hash first;
#   * every read of a value is logged: who, which employee (the dependant's
#     employee for a dependant), which field, when (fix.hr.identity.access.log,
#     append-only, HR Manager reads it). The compute runs record by record
#     (recursive=True), so a read of one record never logs its neighbours;
#   * the forms post every field they show, so an unchanged echo is no change.
#     On a local machine the store answers a synthetic value (DE-12: local is
#     synthetic-only); that echo is recognised as the stored value;
#   * the clear columns left from before are moved by the post-migrate and,
#     for rows the store could not take at that moment, by a daily cron. The
#     hash is set first, so duplicates are caught even before the move.
import hashlib
import hmac
import logging
import secrets
import uuid

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import SQL

from .fix_hr_controls_common import BIRTH_REG_RE, NID_RE, TIN_RE, mask  # noqa: F401

_logger = logging.getLogger(__name__)

HR_PRIVATE = "hr.group_hr_user"
HASH_KEY_PARAM = "cd_hr_core.identity_hash_key"
# field -> (hash kind, Z4 key prefix, hash field, format or None, format label,
#           unique, label)
# No passport format is defined in any repository source, so none is checked.
IDENTITY = {
    "nid_number": ("nid", "hr nid", "nid_hash", NID_RE, "NID (10, 13 or 17 digits)", True, "NID"),
    "tin_number": ("tin", "hr tin", "tin_hash", TIN_RE, "e-TIN (12 digits)", True, "e-TIN"),
    "birth_reg_number": (
        "brn",
        "hr brn",
        "birth_reg_hash",
        BIRTH_REG_RE,
        "Birth registration number (17 digits)",
        False,
        "birth registration number",
    ),
    "passport_number": (
        "passport",
        "hr passport",
        "passport_hash",
        None,
        "",
        False,
        "passport number",
    ),
    "nominee_nid": (
        "nominee_nid",
        "hr nominee nid",
        "nominee_nid_hash",
        NID_RE,
        "Nominee NID / birth registration (10, 13 or 17 digits)",
        False,
        "nominee NID",
    ),
}
DEPENDANT_IDENTITY = {
    "nid": (
        "dependant_nid",
        "hr dependant nid",
        "nid_hash",
        NID_RE,
        "Dependant NID / birth registration (10, 13 or 17 digits)",
        False,
        "dependant NID",
    ),
}
LOG_FIELDS = [
    ("nid_number", "NID"),
    ("tin_number", "e-TIN"),
    ("birth_reg_number", "Birth Registration Number"),
    ("passport_number", "Passport Number"),
    ("nominee_nid", "Nominee NID"),
    ("nid", "Dependant / Nominee NID"),
]
# what a pre-move tracking value becomes (the value itself is in Z4 now)
SCRUBBED = "[held in the Bangladesh-resident store]"


def normalise(value):
    return str(value or "").strip()


def _client():
    # Resolved at call time so a test can stand an in-memory store in for it.
    from libs.py.fix_residency import get_client

    return get_client()


def _identity_field(string, help_text, field, groups=None):
    """A residency-held identifier: computed, inversed, searchable. recursive=True
    computes it record by record, so the read log names exactly the record read."""
    kwargs = {"groups": groups} if groups else {}
    return fields.Char(
        string=string,
        help=help_text + " Held in the Bangladesh-resident store; every read is logged.",
        compute="_compute_%s" % field,
        inverse="_inverse_%s" % field,
        search="_search_%s" % field,
        recursive=True,
        **kwargs,
    )


class FixHrIdentityResidencyMixin(models.AbstractModel):
    """The residency mechanism, shared by the employee and the dependant."""

    _name = "fix.hr.identity.residency.mixin"
    _description = "Residency-Held Personal Identifiers"

    # {field: spec} as IDENTITY; set by each model
    _fix_identity_fields: dict = {}

    def _fix_identity_subject(self):
        """The employee a read of this record is logged against."""
        raise NotImplementedError

    def _fix_identity_note(self, label, removed=False):
        """The change is on the employee's history; its value never is."""
        self.ensure_one()
        subject = self._fix_identity_subject().sudo()
        if subject:
            subject.message_post(
                body="%s %s (the value is held in the Bangladesh-resident store)."
                % (label[:1].upper() + label[1:], "removed" if removed else "recorded"),
                subtype_xmlid="mail.mt_note",
                author_id=self.env.user.partner_id.id,
            )

    # ---- the keyed hash ---------------------------------------------------------
    @api.model
    def _fix_identity_ensure_hash_key(self):
        """Create the HMAC key once (module install / upgrade). Idempotent."""
        Param = self.env["ir.config_parameter"].sudo()
        if not Param.get_param(HASH_KEY_PARAM):
            Param.set_param(HASH_KEY_PARAM, secrets.token_hex(32))
        return True

    @api.model
    def _fix_identity_hash(self, kind, value):
        key = self.env["ir.config_parameter"].sudo().get_param(HASH_KEY_PARAM)
        if not key:
            # Never mint a key here: a new key silently breaks every duplicate check.
            raise UserError("The identity hash key is missing: upgrade the Core HR module.")
        message = ("%s:%s" % (kind, normalise(value))).encode()
        return hmac.new(key.encode(), message, hashlib.sha256).hexdigest()

    # ---- the clear columns left from before (moved by the migration) ------------
    @api.model
    def _fix_identity_legacy_columns(self, refresh=False):
        """The pre-residency clear columns still present on this model's table."""
        cache = getattr(self.pool, "_fix_identity_legacy_cols", None)
        if not isinstance(cache, dict):
            cache = self.pool._fix_identity_legacy_cols = {}
        if self._table not in cache or refresh:
            self.env.cr.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = %s AND column_name IN %s",
                (self._table, tuple(self._fix_identity_fields)),
            )
            cache[self._table] = frozenset(row[0] for row in self.env.cr.fetchall())
        return cache[self._table]

    def _fix_identity_legacy_value(self, name):
        """A value not yet moved out of the clear column (False once moved)."""
        self.ensure_one()
        if name not in self._fix_identity_legacy_columns() or not isinstance(self.id, int):
            return False
        self.env.cr.execute(
            SQL(
                "SELECT %s FROM %s WHERE id = %s",
                SQL.identifier(name),
                SQL.identifier(self._table),
                self.id,
            )
        )
        row = self.env.cr.fetchone()
        return normalise(row[0]) if row and normalise(row[0]) else False

    def _fix_identity_null_legacy(self, name):
        if name in self._fix_identity_legacy_columns() and self.ids:
            self.env.cr.execute(
                SQL(
                    "UPDATE %s SET %s = NULL WHERE id IN %s AND %s IS NOT NULL",
                    SQL.identifier(self._table),
                    SQL.identifier(name),
                    tuple(self.ids),
                    SQL.identifier(name),
                )
            )

    # ---- read: through the residency client, logged -----------------------------
    def _fix_identity_compute(self, name):
        _kind, prefix, hash_field, *_rest = self._fix_identity_fields[name]
        Log = self.env["fix.hr.identity.access.log"].sudo()
        purpose = (self.env.context.get("fix_identity_read_purpose") or "read")[:120]
        for record in self:
            value = False
            # an onchange (new) record shows its origin's value, never a blank
            # that a save would then write back as "remove the NID"
            rec = record if isinstance(record.id, int) else record._origin
            if rec and isinstance(rec.id, int):
                srec = rec.sudo()
                value = rec._fix_identity_legacy_value(name)
                if not value and srec[hash_field] and srec.residency_ref:
                    try:
                        value = normalise(_client().get("%s:%s" % (prefix, srec.residency_ref)))
                    except Exception as exc:  # the store is down: nothing is revealed
                        _logger.warning(
                            "identity read of %s.%s %s failed: %s", self._name, name, rec.id, exc
                        )
                        value = False
                if value:
                    subject = srec._fix_identity_subject()
                    Log.create(
                        {
                            "employee_id": subject.id or False,
                            "employee_name": subject.name or "",
                            "record_model": self._name,
                            "record_id": rec.id,
                            "field_name": name,
                            "user_id": self.env.uid,
                            "as_superuser": bool(self.env.su),
                            "purpose": purpose,
                            "company_id": srec.company_id.id or self.env.company.id,
                        }
                    )
            record[name] = value or False

    def _fix_identity_unchanged(self, name, value):
        """Would writing `value` leave this identifier as it is?

        True for the value already held (by its hash) and for the echo of what
        the store answered (a synthetic value on a local machine)."""
        self.ensure_one()
        kind, prefix, hash_field, *_rest = self._fix_identity_fields[name]
        srec = self.sudo()
        value = normalise(value)
        legacy = self._fix_identity_legacy_value(name)
        if legacy:
            return value == legacy
        if not value:
            return not srec[hash_field]
        if not srec[hash_field]:
            return False
        if self._fix_identity_hash(kind, value) == srec[hash_field]:
            return True
        if srec.residency_ref:
            try:
                served = normalise(_client().get("%s:%s" % (prefix, srec.residency_ref)))
            except Exception:
                return False
            return bool(served) and value == served
        return False

    # ---- write: format, duplicates, then route ----------------------------------
    def _fix_identity_store(self, name):
        kind, prefix, hash_field, pattern, fmt_label, unique, label = self._fix_identity_fields[
            name
        ]
        Model = self.sudo().with_context(active_test=False)
        for rec in self.filtered("id"):
            value = normalise(rec[name])
            srec = rec.sudo()
            legacy = rec._fix_identity_legacy_value(name)
            if not legacy and rec._fix_identity_unchanged(name, value):
                continue
            if not value:
                if srec.residency_ref and srec[hash_field]:
                    try:
                        _client().erase("%s:%s" % (prefix, srec.residency_ref))
                    except Exception as exc:
                        raise UserError(
                            "The Bangladesh-resident identity store is unreachable: the %s "
                            "was not removed. Try again later." % label
                        ) from exc
                srec._guarded().write({hash_field: False})
                rec._fix_identity_null_legacy(name)
                rec._fix_identity_note(label, removed=True)
                continue
            # 1. the format, before anything leaves the ERP
            if pattern is not None and not pattern.match(value):
                raise ValidationError("%s: %r is not valid." % (fmt_label, value))
            # 2. one person, one employee record (through the hash)
            digest = rec._fix_identity_hash(kind, value)
            if unique and Model.search_count([(hash_field, "=", digest), ("id", "!=", rec.id)]):
                raise ValidationError(
                    "This %s is already recorded on another employee: one person, "
                    "one employee record." % label
                )
            # 3. route the value to Z4; the regional row keeps the pointer and hash
            ref = srec.residency_ref or str(uuid.uuid4())
            try:
                _client().put("%s:%s" % (prefix, ref), value)
            except Exception as exc:
                raise UserError(
                    "The Bangladesh-resident identity store is unreachable: the %s was not "
                    "saved (it is never kept in the regional database). Try again later." % label
                ) from exc
            srec._guarded().write({hash_field: digest, "residency_ref": ref})
            rec._fix_identity_null_legacy(name)
            rec._fix_identity_note(label)

    # ---- search with = (and the whole value for ilike) ---------------------------
    def _fix_identity_domain(self, name, operator, value):
        kind, _prefix, hash_field, *_rest = self._fix_identity_fields[name]

        def hashed(v):
            return self._fix_identity_hash(kind, v) if normalise(v) else False

        if operator in ("in", "not in"):
            single = value is None or isinstance(value, str | bool | int)
            values = [value] if single else list(value)
            return [(hash_field, operator, [hashed(v) for v in values])]
        if operator in ("=", "!="):
            return [(hash_field, operator, hashed(value))]
        # an identifier is matched whole: "ilike 1234567890" finds that NID only
        if operator in ("ilike", "=ilike", "like", "=like") and normalise(value):
            return [(hash_field, "=", hashed(value))]
        if operator in ("not ilike", "not like", "not =ilike") and normalise(value):
            return [(hash_field, "!=", hashed(value))]
        raise UserError(
            "%s is searched by its whole value (=, !=, in): it is not held in this database."
            % self._fields[name].string
        )

    # ---- the move out of the clear columns (post-migrate and cron) ---------------
    @api.model
    def _fix_identity_move_table(self):
        """Move every clear identifier left in this model's table to Z4 and null
        the column. Idempotent. A row the store cannot take now is logged and
        left (its hash is set already), so a later run moves it. Superuser only."""
        if not self.env.su:
            raise AccessError("The identity move runs from the module upgrade or its cron only.")
        self._fix_identity_ensure_hash_key()
        cr = self.env.cr
        spec = self._fix_identity_fields
        table = SQL.identifier(self._table)
        cols = sorted(self._fix_identity_legacy_columns(refresh=True))
        result = {"moved": 0, "left": 0, "invalid_format": 0, "tracking_scrubbed": 0}
        if cols:
            self.flush_model()
            present = SQL(" OR ").join(
                SQL("COALESCE(TRIM(%s), '') <> ''", SQL.identifier(c)) for c in cols
            )
            cr.execute(
                SQL(
                    "SELECT id, residency_ref, %s FROM %s WHERE %s ORDER BY id",
                    SQL(", ").join(SQL.identifier(c) for c in cols),
                    table,
                    present,
                )
            )
            for row in cr.fetchall():
                rec_id, ref = row[0], row[1] or str(uuid.uuid4())
                values = {
                    c: normalise(v) for c, v in zip(cols, row[2:], strict=True) if normalise(v)
                }
                # 1. pointer and hashes first (no store needed): duplicates are
                #    detected from now on, whatever happens to the move
                sets = [SQL("residency_ref = %s", ref)]
                for col, value in values.items():
                    kind, _prefix, hash_field, pattern, *_r = spec[col]
                    if pattern is not None and not pattern.match(value):
                        result["invalid_format"] += 1
                    sets.append(
                        SQL(
                            "%s = %s",
                            SQL.identifier(hash_field),
                            self._fix_identity_hash(kind, value),
                        )
                    )
                cr.execute(
                    SQL("UPDATE %s SET %s WHERE id = %s", table, SQL(", ").join(sets), rec_id)
                )
                # 2. the values to Z4, then the clear columns nulled
                try:
                    client = _client()
                    for col, value in values.items():
                        client.put("%s:%s" % (spec[col][1], ref), value)
                except Exception as exc:
                    result["left"] += 1
                    _logger.warning(
                        "identity move: %s %s left for a later run (%s)", self._name, rec_id, exc
                    )
                    continue
                cr.execute(
                    SQL(
                        "UPDATE %s SET %s WHERE id = %s",
                        table,
                        SQL(", ").join(SQL("%s = NULL", SQL.identifier(c)) for c in cols),
                        rec_id,
                    )
                )
                result["moved"] += 1
        # 3. the values an old tracking wrote on the chatter
        cr.execute(
            """
            UPDATE mail_tracking_value v
               SET old_value_char = CASE WHEN COALESCE(v.old_value_char, '') <> ''
                                         THEN %(s)s ELSE v.old_value_char END,
                   new_value_char = CASE WHEN COALESCE(v.new_value_char, '') <> ''
                                         THEN %(s)s ELSE v.new_value_char END
              FROM ir_model_fields f
             WHERE v.field_id = f.id
               AND f.model = %(model)s
               AND f.name IN %(names)s
               AND (COALESCE(v.old_value_char, '') NOT IN ('', %(s)s)
                    OR COALESCE(v.new_value_char, '') NOT IN ('', %(s)s))
            """,
            {"s": SCRUBBED, "model": self._name, "names": tuple(spec)},
        )
        result["tracking_scrubbed"] = cr.rowcount
        self.invalidate_model()
        return result


class HrEmployeeIdentityResidency(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee", "fix.hr.identity.residency.mixin"]

    _fix_identity_fields = IDENTITY

    residency_ref = fields.Char(
        string="Identity Residency Reference",
        readonly=True,
        copy=False,
        index=True,
        groups=HR_PRIVATE,
        help="UUID pointer to this employee's identifiers in the Bangladesh-resident "
        "store (Z4); the values never enter the regional database",
    )
    nid_hash = fields.Char(readonly=True, copy=False, index=True, groups=HR_PRIVATE)
    tin_hash = fields.Char(readonly=True, copy=False, index=True, groups=HR_PRIVATE)
    birth_reg_hash = fields.Char(readonly=True, copy=False, index=True, groups=HR_PRIVATE)
    passport_hash = fields.Char(readonly=True, copy=False, index=True, groups=HR_PRIVATE)
    nominee_nid_hash = fields.Char(readonly=True, copy=False, index=True, groups=HR_PRIVATE)

    nid_number = _identity_field(
        "National ID (NID / Smart Card)",
        "10-digit smart card, 13-digit or 17-digit national identity number.",
        "nid_number",
        HR_PRIVATE,
    )
    tin_number = _identity_field(
        "e-TIN Number",
        "12-digit Taxpayer Identification Number for NBR withholding (Form 23).",
        "tin_number",
        HR_PRIVATE,
    )
    birth_reg_number = _identity_field(
        "17-Digit Birth Registration Number",
        "Birth Registration Certificate number (BRIS).",
        "birth_reg_number",
        HR_PRIVATE,
    )
    passport_number = _identity_field(
        "International Passport Number",
        "International passport number.",
        "passport_number",
        HR_PRIVATE,
    )
    nominee_nid = _identity_field(
        "Nominee National ID / Birth Reg",
        "The statutory nominee's NID or birth registration number.",
        "nominee_nid",
        HR_PRIVATE,
    )

    def _fix_guarded_fields(self) -> set:
        # a forged hash would block someone else's hire or hide a duplicate
        return (
            super()._fix_guarded_fields()
            | {spec[2] for spec in IDENTITY.values()}
            | {"residency_ref"}
        )

    def _fix_identity_subject(self):
        return self

    # ---- one method per field: a shared compute would compute (and log) all of
    # them when one is read; a shared inverse could not tell which was written
    def _compute_nid_number(self):
        self._fix_identity_compute("nid_number")

    def _compute_tin_number(self):
        self._fix_identity_compute("tin_number")

    def _compute_birth_reg_number(self):
        self._fix_identity_compute("birth_reg_number")

    def _compute_passport_number(self):
        self._fix_identity_compute("passport_number")

    def _compute_nominee_nid(self):
        self._fix_identity_compute("nominee_nid")

    def _inverse_nid_number(self):
        self._fix_identity_store("nid_number")

    def _inverse_tin_number(self):
        self._fix_identity_store("tin_number")

    def _inverse_birth_reg_number(self):
        self._fix_identity_store("birth_reg_number")

    def _inverse_passport_number(self):
        self._fix_identity_store("passport_number")

    def _inverse_nominee_nid(self):
        self._fix_identity_store("nominee_nid")

    def _search_nid_number(self, operator, value):
        return self._fix_identity_domain("nid_number", operator, value)

    def _search_tin_number(self, operator, value):
        return self._fix_identity_domain("tin_number", operator, value)

    def _search_birth_reg_number(self, operator, value):
        return self._fix_identity_domain("birth_reg_number", operator, value)

    def _search_passport_number(self, operator, value):
        return self._fix_identity_domain("passport_number", operator, value)

    def _search_nominee_nid(self, operator, value):
        return self._fix_identity_domain("nominee_nid", operator, value)

    @api.constrains("nid_hash", "tin_hash")
    def _check_identity_hash_unique(self):
        Employee = self.sudo().with_context(active_test=False)
        for rec in self.sudo():
            for name in ("nid_number", "tin_number"):
                hash_field, label = IDENTITY[name][2], IDENTITY[name][6]
                if rec[hash_field] and Employee.search_count(
                    [(hash_field, "=", rec[hash_field]), ("id", "!=", rec.id)]
                ):
                    raise ValidationError(
                        "This %s is already recorded on another employee: one person, "
                        "one employee record." % label
                    )

    @api.model
    def _fix_identity_move_clear_values(self):
        """Every clear identifier of the employees and their dependants, and the
        numbers decided master changes still hold (post-migrate and cron)."""
        if not self.env.su:
            raise AccessError("The identity move runs from the module upgrade or its cron only.")
        totals = self._fix_identity_move_table()
        dependants = self.env["fix.hr.dependant"]._fix_identity_move_table()
        for key, count in dependants.items():
            totals[key] += count
        totals["dependants_moved"] = dependants["moved"]
        self.env["fix.hr.master.change"]._fix_scrub_closed_identity_proposals()
        _logger.info("identity move: %s", totals)
        return totals

    @api.model
    def _cron_identity_residency_move(self):
        """Daily: move the rows the post-migrate could not (store down then)."""
        return self.sudo()._fix_identity_move_clear_values()


class FixHrDependantIdentityResidency(models.Model):
    _name = "fix.hr.dependant"
    _inherit = ["fix.hr.dependant", "fix.guarded.mixin", "fix.hr.identity.residency.mixin"]

    _fix_identity_fields = DEPENDANT_IDENTITY

    residency_ref = fields.Char(
        string="Identity Residency Reference", readonly=True, copy=False, index=True
    )
    nid_hash = fields.Char(readonly=True, copy=False, index=True)
    nid = _identity_field(
        "NID", "The dependant's or nominee's NID or birth registration number.", "nid"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"nid_hash", "residency_ref"}

    def _fix_identity_subject(self):
        return self.employee_id

    def _compute_nid(self):
        self._fix_identity_compute("nid")

    def _inverse_nid(self):
        self._fix_identity_store("nid")

    def _search_nid(self, operator, value):
        return self._fix_identity_domain("nid", operator, value)


class FixHrIdentityAccessLog(models.Model):
    """Who read which employee's identifier (or their dependant's), and when
    (BRU-HCM-07). Written by the read path only; never edited or deleted."""

    _name = "fix.hr.identity.access.log"
    _description = "Employee Identity Read Log"
    _order = "id desc"

    employee_id = fields.Many2one("hr.employee", readonly=True, index=True, ondelete="set null")
    employee_name = fields.Char(readonly=True)
    record_model = fields.Char(readonly=True, help="hr.employee, or fix.hr.dependant")
    record_id = fields.Integer(readonly=True)
    field_name = fields.Selection(LOG_FIELDS, required=True, readonly=True)
    user_id = fields.Many2one(
        "res.users", string="Read By", required=True, readonly=True, index=True, ondelete="restrict"
    )
    as_superuser = fields.Boolean(string="Read in a Superuser Context", readonly=True)
    purpose = fields.Char(readonly=True, help="As declared by the calling code")
    company_id = fields.Many2one("res.company", readonly=True, index=True)
    read_at = fields.Datetime(default=fields.Datetime.now, required=True, readonly=True)

    @api.depends("read_at", "purpose")
    def _compute_display_name(self):
        """A row has no name field (A09 ERP audit UI-F10): without this every
        row read "fix.hr.identity.access.log,<id>". The label carries the
        number, the time and the declared purpose only - never the identifier
        (the log never holds it) nor the employee it was read for."""
        for rec in self:
            when = ""
            if rec.read_at:
                local = rec.with_context(tz=rec.env.context.get("tz") or "Asia/Dhaka")
                when = fields.Datetime.context_timestamp(local, rec.read_at).strftime(
                    "%Y-%m-%d %H:%M"
                )
            rec.display_name = "Identity read #%s · %s · %s" % (
                rec.id or "",
                when,
                (rec.purpose or "read")[:60],
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The identity read log is written by the read path only.")
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError("The identity read log is append-only (BRU-HCM-07).")

    def unlink(self):
        raise AccessError("The identity read log is append-only (BRU-HCM-07).")
