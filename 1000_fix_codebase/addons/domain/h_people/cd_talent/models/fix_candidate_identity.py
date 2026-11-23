# fix_candidate_identity — M58: a candidate's government identifiers (NID,
# birth registration number, passport number) in the Bangladesh-resident store.
#
# A09 ERP audit M58-F4 (2026-11-23): the NID sat in clear in fix_candidate for
# the whole pipeline, readable by every role with candidate read, while the
# estate had already moved the employees' identifiers to the store (M21-A6).
# Spec T-04 / AC-13: "NID and other sensitive identifiers reside in the
# Bangladesh-resident store, both for candidates and for employees".
#
# The same mechanism as cd_hr_core (fix_hr_identity_residency.py), through
# libs/py/fix_residency, the only client of the store (FF-09):
#   * the value goes to the store; the row keeps one pointer per identifier
#     and its HMAC-SHA256 under the key shared with M21. One NID hashes the
#     same on a candidate and on an employee, so "the same person is already
#     hired" is answered from the hashes, never from the store;
#   * the ORM API is unchanged: read (a compute), write (an inverse) and
#     search with = / != (a search method);
#   * only Recruitment and a Background Verifier read a value (field groups).
#     Everyone else sees the last four digits (`*_masked`), kept on the row
#     when the value is written, so no display ever reads the store;
#   * every read of a value is logged (fix.hr.identity.access.log);
#   * a hire copies an identifier to the employee only when the store serves
#     it back intact (the same hash), then releases the candidate's copy. The
#     candidate keeps its hash, so the same person is never hired twice even
#     when the copy could not be made;
#   * the format is checked before anything leaves the ERP; a store that
#     cannot be reached refuses the write (the value is never kept here);
#   * the clear columns left from before are moved out by the post-migrate
#     and, for rows the store could not take then, by the erasure cron.
# The retention period itself (M58-F3: how long an unsuccessful applicant's
# data is kept) is a business figure and stays an owner decision; the erasure
# cron enforces it once set.
import hashlib
import hmac
import logging
import uuid

from odoo import api, fields, models
from odoo.addons.cd_hr_core.models.fix_hr_controls_common import BIRTH_REG_RE, NID_RE
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import SQL

_logger = logging.getLogger(__name__)

HASH_KEY_PARAM = "cd_hr_core.identity_hash_key"
# Who reads a value back. Everyone else sees only the last four digits.
READERS = "cd_talent.group_talent,cd_talent.group_background_verifier"
# field: (hash kind, store key prefix, hash field, pointer field, format,
#        format message or None, label). The hash kinds are M21's, so the
# hashes of one value agree on a candidate and on an employee.
CANDIDATE_IDENTITY = {
    "nid_number": (
        "nid",
        "candidate nid",
        "nid_hash",
        "nid_ref",
        NID_RE,
        "An NID number is 10, 13 or 17 digits.",
        "NID",
    ),
    "birth_reg_number": (
        "brn",
        "candidate brn",
        "birth_reg_hash",
        "birth_reg_ref",
        BIRTH_REG_RE,
        "A birth registration number is 17 digits.",
        "birth registration number",
    ),
    "passport_number": (
        "passport",
        "candidate passport",
        "passport_hash",
        "passport_ref",
        None,
        None,
        "passport number",
    ),
}
HASH_FIELDS = tuple(spec[2] for spec in CANDIDATE_IDENTITY.values())
REF_FIELDS = tuple(spec[3] for spec in CANDIDATE_IDENTITY.values())
MASKED_FIELDS = tuple("%s_masked" % name for name in CANDIDATE_IDENTITY)


def normalise(value):
    return str(value or "").strip()


def _client():
    # Resolved at call time so a test can stand an in-memory store in for it.
    from libs.py.fix_residency import get_client

    return get_client()


def _identity_field(string, help_text, name):
    """A store-held identifier: computed, inversed, searchable. recursive=True
    computes it record by record, so the read log names exactly the record
    read."""
    return fields.Char(
        string=string,
        help=help_text,
        compute="_compute_%s" % name,
        inverse="_inverse_%s" % name,
        search="_search_%s" % name,
        recursive=True,
        groups=READERS,
    )


class FixCandidateIdentity(models.Model):
    """The candidate's government identifiers, held in the resident store."""

    _inherit = "fix.candidate"

    birth_reg_hash = fields.Char(
        string="Birth Registration Hash", readonly=True, copy=False, index=True
    )
    passport_hash = fields.Char(string="Passport Hash", readonly=True, copy=False, index=True)
    nid_ref = fields.Char(
        string="NID Residency Reference",
        readonly=True,
        copy=False,
        index=True,
        help="Pointer to the NID in the Bangladesh-resident store while this candidate holds it; "
        "cleared when the value leaves (the hire, an erasure).",
    )
    birth_reg_ref = fields.Char(
        string="Birth Registration Residency Reference", readonly=True, copy=False, index=True
    )
    passport_ref = fields.Char(
        string="Passport Residency Reference", readonly=True, copy=False, index=True
    )
    identity_last4 = fields.Json(
        string="Identifiers on File (last 4 digits)",
        readonly=True,
        copy=False,
        help="The last four digits of each identifier on file, for display. Set when the value is "
        "written; a display never reads the store.",
    )
    nid_number = _identity_field(
        "NID Number",
        "10-, 13- or 17-digit National ID. Held in the Bangladesh-resident store: the record keeps "
        "its keyed hash and a pointer, and every read is logged.",
        "nid_number",
    )
    birth_reg_number = _identity_field(
        "Birth Registration No. (17 digits)",
        "When the candidate has no NID. Held in the Bangladesh-resident store: the record keeps its "
        "keyed hash and a pointer, and every read is logged.",
        "birth_reg_number",
    )
    passport_number = _identity_field(
        "Passport No.",
        "Held in the Bangladesh-resident store: the record keeps its keyed hash and a pointer, and "
        "every read is logged.",
        "passport_number",
    )
    nid_number_masked = fields.Char(
        string="NID on File (last 4 digits)", compute="_compute_identity_masked"
    )
    birth_reg_number_masked = fields.Char(
        string="Birth Registration on File (last 4 digits)", compute="_compute_identity_masked"
    )
    passport_number_masked = fields.Char(
        string="Passport on File (last 4 digits)", compute="_compute_identity_masked"
    )

    def _fix_guarded_fields(self) -> set:
        # a forged hash or pointer would hide a duplicate or point at someone else's identifier
        return (
            super()._fix_guarded_fields()
            | {"birth_reg_hash", "passport_hash", "identity_last4"}
            | set(REF_FIELDS)
        )

    # ---- the keyed hash (the key and the message are M21's) --------------------
    def _fix_identity_hash(self, kind, value):
        key = self.env["ir.config_parameter"].sudo().get_param(HASH_KEY_PARAM)
        if not key:
            # never minted at hash time: a new key silently breaks every duplicate check
            raise UserError("The identity hash key is missing: upgrade the Talent module.")
        return hmac.new(
            key.encode(), ("%s:%s" % (kind, normalise(value))).encode(), hashlib.sha256
        ).hexdigest()

    @api.depends("identity_last4")
    def _compute_identity_masked(self):
        for rec in self:
            last4 = dict(rec.sudo().identity_last4 or {})
            for name in CANDIDATE_IDENTITY:
                rec["%s_masked" % name] = "***%s" % last4[name] if last4.get(name) else False

    # ---- the clear columns left from before (moved by the migration / cron) ----
    @api.model
    def _fix_identity_legacy_columns(self, refresh=False):
        """The pre-residency clear columns still present on this table. They
        are no longer fields: nothing reads them through the ORM."""
        cache = getattr(self.pool, "_fix_candidate_identity_legacy_cols", None)
        if not isinstance(cache, dict):
            cache = self.pool._fix_candidate_identity_legacy_cols = {}
        if self._table not in cache or refresh:
            self.env.cr.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = %s AND column_name IN %s",
                (self._table, tuple(CANDIDATE_IDENTITY)),
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

    def _fix_identity_legacy_ids(self, name):
        """The rows whose clear value is still in the column `name`."""
        if name not in self._fix_identity_legacy_columns():
            return []
        self.env.cr.execute(
            SQL(
                "SELECT id FROM %s WHERE COALESCE(TRIM(%s), '') <> ''",
                SQL.identifier(self._table),
                SQL.identifier(name),
            )
        )
        return [row[0] for row in self.env.cr.fetchall()]

    def _fix_identity_null_legacy(self, name):
        if name in self._fix_identity_legacy_columns() and isinstance(self.id, int):
            self.env.cr.execute(
                SQL(
                    "UPDATE %s SET %s = NULL WHERE id = %s",
                    SQL.identifier(self._table),
                    SQL.identifier(name),
                    self.id,
                )
            )

    # ---- read: through the store, logged ---------------------------------------
    def _fix_identity_served(self, name):
        """What the store holds for this row's identifier (False: none, or the
        store is down, in which case nothing is revealed)."""
        self.ensure_one()
        _kind, prefix, _hash_field, ref_field, *_rest = CANDIDATE_IDENTITY[name]
        ref = self.sudo()[ref_field]
        if not ref:
            return False
        try:
            return normalise(_client().get("%s:%s" % (prefix, ref)))
        except Exception as exc:  # the store is down: nothing is revealed
            _logger.warning("identity read of %s.%s %s failed: %s", self._name, name, self.id, exc)
            return False

    def _fix_identity_log(self, name, purpose):
        """Who read which candidate's identifier, when (as M21's read log)."""
        self.ensure_one()
        srec = self.sudo()
        self.env["fix.hr.identity.access.log"].sudo().create(
            {
                "employee_id": srec.employee_id.id or False,
                "employee_name": srec.name or "",
                "record_model": self._name,
                "record_id": self.id,
                "field_name": name,
                "user_id": self.env.uid,
                "as_superuser": bool(self.env.su),
                "purpose": (purpose or "read")[:120],
                "company_id": srec.company_id.id or self.env.company.id,
            }
        )

    def _fix_identity_compute(self, name):
        purpose = self.env.context.get("fix_identity_read_purpose") or "read"
        for record in self:
            value = False
            # a form's new record shows its origin's value, never a blank that
            # a save would then write back as "remove the identifier"
            rec = record if isinstance(record.id, int) else record._origin
            if rec and isinstance(rec.id, int):
                srec = rec.sudo()
                value = srec._fix_identity_legacy_value(name)
                if (
                    not value
                    and srec[CANDIDATE_IDENTITY[name][2]]
                    and srec[CANDIDATE_IDENTITY[name][3]]
                ):
                    value = srec._fix_identity_served(name)
                if value:
                    srec._fix_identity_log(name, purpose)
            record[name] = value or False

    def _compute_nid_number(self):
        self._fix_identity_compute("nid_number")

    def _compute_birth_reg_number(self):
        self._fix_identity_compute("birth_reg_number")

    def _compute_passport_number(self):
        self._fix_identity_compute("passport_number")

    def _fix_identity_unchanged(self, name, value):
        """Would writing `value` leave this identifier as it is? True for the
        value already held (by its hash) and for the echo of what the store
        answered (a synthetic value on a local machine)."""
        self.ensure_one()
        kind, _prefix, hash_field, ref_field, *_rest = CANDIDATE_IDENTITY[name]
        srec = self.sudo()
        value = normalise(value)
        legacy = self._fix_identity_legacy_value(name)
        if legacy:
            return value == legacy
        if not value:
            return not srec[ref_field]
        if not srec[ref_field]:
            # nothing is held (never, or since a release): any value is a new write
            return False
        if srec[hash_field] and self._fix_identity_hash(kind, value) == srec[hash_field]:
            return True
        return bool(srec._fix_identity_served(name)) and value == srec._fix_identity_served(name)

    # ---- write: format and retention, then the store ---------------------------
    def _fix_identity_last4(self, name, value):
        last4 = dict(self.sudo().identity_last4 or {})
        if value:
            last4[name] = value[-4:]
        else:
            last4.pop(name, None)
        self.sudo()._guarded().write({"identity_last4": last4})

    def _fix_identity_release(self, name, to_employee=False):
        """The value leaves this candidate: erased in the store, pointer
        cleared. The keyed hash stays when the value went to the employee
        master (the same person is never hired twice); an erasure clears it."""
        self.ensure_one()
        _kind, prefix, hash_field, ref_field, _pattern, _message, label = CANDIDATE_IDENTITY[name]
        srec = self.sudo()
        ref = srec[ref_field]
        if ref:
            try:
                _client().erase("%s:%s" % (prefix, ref))
            except Exception as exc:
                raise UserError(
                    "The Bangladesh-resident identity store is unreachable: the %s was not "
                    "removed. Try again later." % label
                ) from exc
        vals = {ref_field: False}
        if not to_employee:
            vals[hash_field] = False
        srec._guarded().write(vals)
        srec._fix_identity_last4(name, False)
        self._fix_identity_null_legacy(name)

    def _fix_identity_store(self, name):
        kind, prefix, hash_field, ref_field, pattern, message, label = CANDIDATE_IDENTITY[name]
        for rec in self.filtered("id"):
            value = normalise(rec[name])
            srec = rec.sudo()
            if not srec._fix_identity_legacy_value(name) and rec._fix_identity_unchanged(
                name, value
            ):
                continue
            if not value:
                srec._fix_identity_release(name, to_employee=bool(srec.employee_id))
                continue
            # 1. the format, before anything leaves the ERP
            if pattern is not None and not pattern.match(value):
                raise ValidationError(message)
            # 2. route the value to the store; the row keeps the pointer and the hash
            digest = srec._fix_identity_hash(kind, value)
            ref = srec[ref_field] or str(uuid.uuid4())
            try:
                _client().put("%s:%s" % (prefix, ref), value)
            except Exception as exc:
                raise UserError(
                    "The Bangladesh-resident identity store is unreachable: the %s was not saved "
                    "(it is never kept in the regional database). Try again later." % label
                ) from exc
            srec._guarded().write({hash_field: digest, ref_field: ref})
            srec._fix_identity_last4(name, value)
            rec._fix_identity_null_legacy(name)

    def _inverse_nid_number(self):
        self._fix_identity_store("nid_number")

    def _inverse_birth_reg_number(self):
        self._fix_identity_store("birth_reg_number")

    def _inverse_passport_number(self):
        self._fix_identity_store("passport_number")

    def _fix_identity_erase(self):
        """Anonymisation (the erasure cron): every identifier leaves the store,
        its pointer and hash are cleared. A store that cannot be reached leaves
        that value for the next run and does not stop the rest of the record
        from being anonymised - the cron is idempotent. (M58-F3: whether a
        candidate's data is kept at all - the retention period - is the
        owner's decision, recorded in the audit report; this method is how the
        period is enforced once it is set.)"""
        self.ensure_one()
        for name in CANDIDATE_IDENTITY:
            try:
                self._fix_identity_release(name, to_employee=False)
            except UserError as exc:
                _logger.warning(
                    "erasure of candidate %s: the %s could not be removed now (%s)",
                    self.id,
                    CANDIDATE_IDENTITY[name][6],
                    exc,
                )

    # ---- search with = (and the whole value for ilike) ---------------------------
    def _fix_identity_search(self, name, operator, value):
        kind, _prefix, hash_field, ref_field, *_rest = CANDIDATE_IDENTITY[name]

        def hashed(v):
            return self._fix_identity_hash(kind, v) if normalise(v) else False

        if operator in ("in", "not in"):
            single = value is None or isinstance(value, str | bool | int)
            values = [value] if single else list(value)
            return [(hash_field, operator, [hashed(v) for v in values])]
        if operator in ("=", "!="):
            if not normalise(value):
                # "has / has not the identifier": a row holds one by its pointer, or in a clear
                # column not yet moved to the store
                held = [(ref_field, "!=", False)]
                legacy = self._fix_identity_legacy_ids(name)
                if legacy:
                    held = ["|", (ref_field, "!=", False), ("id", "in", legacy)]
                return held if operator == "!=" else ["!", *held]
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

    def _search_nid_number(self, operator, value):
        return self._fix_identity_search("nid_number", operator, value)

    def _search_birth_reg_number(self, operator, value):
        return self._fix_identity_search("birth_reg_number", operator, value)

    def _search_passport_number(self, operator, value):
        return self._fix_identity_search("passport_number", operator, value)

    def write(self, vals):
        touched = set(CANDIDATE_IDENTITY) & set(vals)
        if touched and not self._fix_guard_open():
            for rec in self:
                if rec.id and rec.state == "hired":
                    raise UserError(
                        "%s is hired: their %s lives on the employee master, not here."
                        % (
                            rec.name,
                            ", ".join(
                                CANDIDATE_IDENTITY[n][6] for n in CANDIDATE_IDENTITY if n in touched
                            ),
                        )
                    )
                if rec.id and rec.erased:
                    raise UserError("%s was erased: nothing is added back." % rec.name)
        return super().write(vals)

    def unlink(self):
        # a deleted candidate leaves no identifier behind in the store
        for rec in self.sudo():
            for name in CANDIDATE_IDENTITY:
                if rec[CANDIDATE_IDENTITY[name][3]]:
                    rec._fix_identity_release(name, to_employee=bool(rec.employee_id))
        return super().unlink()

    # ---- the hire hand-off (I6) ----------------------------------------------------
    def _fix_release_identity(self, employee):
        """The hire (action_hire): each identifier the store serves back intact
        is copied to the employee master, and the candidate's copy is then
        released. A value the store does not serve back intact (it cannot be
        checked against the hash) is not copied anywhere: the candidate keeps
        it, and the hire is logged for Recruitment."""
        self.ensure_one()
        emp = employee.sudo()
        srec = self.sudo()
        for name, (
            kind,
            _prefix,
            hash_field,
            ref_field,
            _pattern,
            _message,
            label,
        ) in CANDIDATE_IDENTITY.items():
            if not srec[ref_field]:
                continue
            digest = srec[hash_field]
            served = srec._fix_identity_served(name)
            if served:
                srec._fix_identity_log(name, "hire copy")
            if (
                served
                and digest
                and name in emp._fields
                and self._fix_identity_hash(kind, served) == digest
            ):
                emp.write({name: served})
                srec._fix_identity_release(name, to_employee=True)
            else:
                _logger.warning(
                    "hire of candidate %s: the store did not serve its %s back intact; it was not "
                    "copied to the employee and stays with the candidate",
                    self.id,
                    label,
                )
                srec.message_post(
                    body="The %s was not copied to the employee master: the identity store did not "
                    "serve it back intact. It stays with this candidate record." % label
                )

    def _fix_take_back_identity(self, employee):
        """A reversed hire (M58-F5): the identifiers this hire copied to the
        employee return to the candidate, and the employee's copies are
        erased. A value the store does not serve back intact is left where it
        is: nothing is destroyed on a value that cannot be checked."""
        self.ensure_one()
        emp = employee.sudo()
        srec = self.sudo()
        for name, (
            kind,
            prefix,
            hash_field,
            ref_field,
            _pattern,
            _message,
            label,
        ) in CANDIDATE_IDENTITY.items():
            digest = srec[hash_field]
            if (
                not digest
                or srec[ref_field]
                or name not in emp._fields
                or emp[hash_field] != digest
            ):
                continue
            served = normalise(emp[name])
            if not served or self._fix_identity_hash(kind, served) != digest:
                _logger.warning(
                    "reversal of hire %s: the store did not serve the employee's %s back intact; it "
                    "was not moved back to the candidate and was left on the employee",
                    emp.id,
                    label,
                )
                srec.message_post(
                    body="The %s was not moved back from employee %s: the identity store did not "
                    "serve it back intact." % (label, emp.name)
                )
                continue
            ref = str(uuid.uuid4())
            try:
                _client().put("%s:%s" % (prefix, ref), served)
            except Exception as exc:
                raise UserError(
                    "The Bangladesh-resident identity store is unreachable: the %s was not moved "
                    "back to the candidate. Try again later." % label
                ) from exc
            srec._guarded().write({ref_field: ref})
            srec._fix_identity_last4(name, served)
            srec._fix_identity_log(name, "hire reversed: returned to the candidate")
            emp.write({name: False})  # M21's inverse erases the employee's copy

    # ---- the move out of the clear columns (post-migrate and erasure cron) --------
    @api.model
    def _fix_identity_move_clear_values(self):
        """Move every identifier still in a clear column of fix_candidate to the
        store and null the column. Idempotent. A row the store cannot take now
        is left as it is, for the next run. The identifier of a hired candidate
        that the employee master already holds (the same hash) is dropped, as
        the hire itself did. Superuser only (the upgrade or the cron)."""
        if not self.env.su:
            raise AccessError("The identity move runs from the module upgrade or its cron only.")
        self._fix_ensure_identity_hash_key()
        spec = CANDIDATE_IDENTITY
        result = {"moved": 0, "dropped_on_hired": 0, "left": 0}
        cols = sorted(self._fix_identity_legacy_columns(refresh=True))
        if not cols:
            return result
        self.flush_model()
        cr = self.env.cr
        table = SQL.identifier(self._table)
        present = SQL(" OR ").join(
            SQL("COALESCE(TRIM(%s), '') <> ''", SQL.identifier(c)) for c in cols
        )
        cr.execute(
            SQL(
                "SELECT id, state, employee_id, %s FROM %s WHERE %s ORDER BY id",
                SQL(", ").join(SQL.identifier(c) for c in cols),
                table,
                present,
            )
        )
        Employee = self.env["hr.employee"].sudo()
        last4 = {}
        for row in cr.fetchall():
            rec_id, state, emp_id = row[0], row[1], row[2]
            values = {c: normalise(v) for c, v in zip(cols, row[3:], strict=True) if normalise(v)}
            hashes = {c: self._fix_identity_hash(spec[c][0], v) for c, v in values.items()}
            keep = dict(values)
            if state == "hired" and emp_id:
                emp = Employee.browse(emp_id)
                for c, digest in hashes.items():
                    if spec[c][2] in emp._fields and emp[spec[c][2]] == digest:
                        keep.pop(c)  # the employee master holds it
            refs = {c: str(uuid.uuid4()) for c in keep}
            try:
                client = _client()
                for c, value in keep.items():
                    client.put("%s:%s" % (spec[c][1], refs[c]), value)
            except Exception as exc:
                result["left"] += 1
                _logger.warning(
                    "identity move: candidate %s left for a later run (%s)", rec_id, exc
                )
                continue  # nothing of this row was changed
            sets = [SQL("%s = %s", SQL.identifier(spec[c][2]), d) for c, d in hashes.items()]
            sets += [
                SQL("%s = %s", SQL.identifier(spec[c][3]), r)
                if c in keep
                else SQL("%s = NULL", SQL.identifier(spec[c][3]))
                for c, r in refs.items()
            ] + [SQL("%s = NULL", SQL.identifier(spec[c][3])) for c in hashes if c not in keep]
            sets += [SQL("%s = NULL", SQL.identifier(c)) for c in cols]
            cr.execute(SQL("UPDATE %s SET %s WHERE id = %s", table, SQL(", ").join(sets), rec_id))
            result["moved"] += len(keep)
            result["dropped_on_hired"] += len(hashes) - len(keep)
            last4[rec_id] = {c: v[-4:] for c, v in keep.items()}
        self.invalidate_model()
        for rec_id, digits in last4.items():
            self.browse(rec_id)._fix_identity_last4_digits(digits)
        return result

    def _fix_identity_last4_digits(self, digits):
        self.ensure_one()
        self.sudo()._guarded().write({"identity_last4": dict(digits)})
