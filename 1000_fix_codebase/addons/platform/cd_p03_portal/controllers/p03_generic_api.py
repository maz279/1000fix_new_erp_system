# P03 generic model API — the read/action endpoints behind the in-workspace
# model_list screens for the A08 finance modules (M52/M50/M51/M53/M49/M54).
#
# Two endpoints only, both strictly whitelisted:
#   /p03/model/records (read)  — configurable columns, safe domains
#   /p03/model/action  (write) — ONLY the headless workflow actions that
#                                already exist on the models, each wrapped in
#                                a savepoint (a refusal leaves nothing behind
#                                — the M19 leaked-draft rule).
#
# Nothing here invents data: rows are live reads of the real models; actions
# are the SAME methods the Odoo forms would call. Internal-user only (NVR-22).
import datetime
import logging

import psycopg2
import pytz
from odoo import fields, http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Domain
from odoo.http import request

from . import report_bytes, report_delivery
from .a02 import SURFACES as _A02_SURFACES
from .a03 import SURFACES as _A03_SURFACES
from .a04 import SURFACES as _A04_SURFACES
from .a05 import SURFACES as _A05_SURFACES
from .a06 import SURFACES as _A06_SURFACES
from .a07 import SURFACES as _A07_SURFACES
from .a08 import SURFACES as _A08_SURFACES
from .a09 import SURFACES as _A09_SURFACES
from .a10 import SURFACES as _A10_SURFACES
from .a11 import SURFACES as _A11_SURFACES
from .a12 import SURFACES as _A12_SURFACES
from .p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)


def _log_report_export(module, report, fmt, out, params):
    """A11 audit E6 / BRU-BID-11: every pack download is logged — who, what,
    which scope, how many rows. The audit row itself is append-only (see
    fix.bi.export.log). A logging failure must never block the download."""
    try:
        env = request.env
        if "fix.bi.export.log" not in env:
            return
        env["fix.bi.export.log"].sudo().create(
            {
                "user_id": env.user.id,
                "pack": "%s:%s" % (module or "?", report or "?"),
                "channel": "download",
                "format": fmt,
                "company_ids": ", ".join(env.companies.mapped("name")),
                "row_count": len(out.get("rows") or []),
                "params_json": repr(params or {})[:2000],
            }
        )
    except Exception:
        _logger.exception("export log write failed for %s:%s", module, report)


def _readonly_changed(rec, field, value) -> bool:
    """Would writing `value` change read-only `field` on `rec`?

    The form posts every field it shows, read-only ones included, so an
    unchanged echo must pass. The comparison is deliberately lenient about
    representation (a datetime-local input drops the seconds; many2one
    arrives as an id) and strict about meaning."""
    current = rec[field.name]
    kind = field.type
    if kind == "many2one":
        return (value or False) != (current.id or False)
    if kind in ("one2many", "many2many", "binary", "properties", "json"):
        return False  # not editable through the generic form; dropped below
    if kind in ("float", "monetary", "integer"):
        try:
            return abs(float(value or 0) - float(current or 0)) > 0.005
        except (TypeError, ValueError):
            return True
    if kind == "datetime":
        return str(value or "").replace("T", " ")[:16] != str(current or "")[:16]
    if kind == "date":
        return str(value or "")[:10] != str(current or "")[:10]
    if kind == "boolean":
        return bool(value) != bool(current)
    return (value or "") != (current or "")


# A many2one whose comodel holds more rows than this is searched on the server
# as the user types: a select of the first 300 of 15,000 customers hid the rest.
PICKER_LIMIT = 300
# 1000 FiX runs on Dhaka time; a user with no zone set must not read UTC.
DEFAULT_TZ = "Asia/Dhaka"


def _not_null_label(env, model, exc):
    """The label of the required column a NOT NULL violation names, looked up
    on the saved model or one of its one2many children (a line grid); False
    when it cannot be told."""
    diag = getattr(exc, "diag", None)
    column = getattr(diag, "column_name", None)
    table = getattr(diag, "table_name", None)
    if not column or model not in env:
        return False
    candidates = [env[model]]
    for field in env[model]._fields.values():
        if field.type == "one2many" and field.comodel_name in env:
            candidates.append(env[field.comodel_name])
    for rec_model in candidates:
        if table and rec_model._table != table:
            continue
        field = rec_model._fields.get(column)
        if field:
            # the plain attribute: the transaction may be aborted, so no query
            label = field.string or column
            if rec_model._name != model:
                return "%s (on a line)" % label
            return label
    return False


def _user_tz(env):
    try:
        return pytz.timezone(env.user.tz or env.context.get("tz") or DEFAULT_TZ)
    except pytz.UnknownTimeZoneError:
        return pytz.timezone(DEFAULT_TZ)


def _datetime_to_local(env, value) -> str:
    """A stored (UTC) datetime as the user's wall clock."""
    if not value:
        return ""
    moment = fields.Datetime.to_datetime(value)
    return pytz.utc.localize(moment).astimezone(_user_tz(env)).strftime("%Y-%m-%d %H:%M:%S")


def _datetime_to_utc(env, text):
    """What a person typed or a form echoed (their wall clock) as stored UTC."""
    if not text or not isinstance(text, str):
        return text
    try:
        moment = datetime.datetime.fromisoformat(text.replace("T", " ", 1)[:19])
    except ValueError:
        return text
    return (
        _user_tz(env)
        .localize(moment)
        .astimezone(pytz.utc)
        .replace(tzinfo=None)
        .strftime("%Y-%m-%d %H:%M:%S")
    )


def _picker_domain(env, surface, comodel, name) -> list:
    """Which rows a many2one offers: what its surface declares under `pickers`
    (an insurer is not every partner), fenced to the caller's companies. The
    domain is never taken from the browser: these reads run sudo, so a domain
    from the client would let it search any column of any comodel."""
    domain = list(((surface or {}).get("pickers") or {}).get(name) or [])
    if "company_id" in env[comodel]._fields:
        domain += ["|", ("company_id", "=", False), ("company_id", "in", env.companies.ids)]
    return domain


def _company_fence(env, model, surface) -> list:
    """The company fence every list read ANDs in — rows, their count and every
    export, since those all go through model_records. A row with no company is
    a shared one (a statutory pack, a global tax rate, an IoT adapter, a party
    used by every company): the picker above has always offered it, so the
    list must show it too, or the row can be picked but never found. A surface
    may name more than one company path: a counterparty accountant holding
    only the target company sees the charge she accepts."""
    if "company_id" not in env[model]._fields:
        return []
    paths = (surface or {}).get("company_paths") or ("company_id",)
    leaves = [("company_id", "=", False)]
    leaves += [(path, "in", env.companies.ids) for path in paths]
    return ["|"] * (len(leaves) - 1) + leaves


def _picker_source(env, comodel, surface=None, name=None):
    """Where a picker reads. Names are read sudo, since a clerk may pick a partner they
    hold no ACL on. A comodel whose own screens are fenced by record rules is read as the
    caller instead, or a picker would hand over the rows those screens hide - unless the
    form's surface names the field under `picker_names`: then only names are offered,
    sudo, filtered by the surface's own server-side `pickers` domain (M29 New User:
    an Access Approver picks the joiner by name without HR rights to the employee
    master, and is offered only employees with no login yet)."""
    if comodel == "ir.attachment":
        # never sudo: a file name is the file's content to a reader (payslips,
        # contracts, IDs) - M03 audit 2026-11-13
        return env[comodel]
    if name and name in ((surface or {}).get("picker_names") or ()):
        return env[comodel].sudo()
    return env[comodel] if (SURFACES.get(comodel) or {}).get("rules") else env[comodel].sudo()


# An evidence field (a many2one to ir.attachment: signed waybill, POD scan,
# damage photo) is an UPLOAD, not a choice. M03 audit 2026-11-13: the form
# offered a dropdown of every attachment name in the company, read as
# superuser, and no way to attach a new file - so a courier POD could never
# be recorded. The browser sends {"upload": <base64>, "filename": <name>}.
UPLOAD_MAX_BYTES = 10 * 1024 * 1024


def _is_upload(value) -> bool:
    return isinstance(value, dict) and "upload" in value


def _store_upload(env, value):
    """Create the caller's attachment for one upload and return it. It is
    linked to its record by _link_uploads once the record is saved."""
    data = value.get("upload") or ""
    if isinstance(data, str) and data.startswith("data:"):
        data = data.split(",", 1)[1] if "," in data else ""
    if not data:
        raise UserError("The uploaded file is empty.")
    if len(data) * 3 // 4 > UPLOAD_MAX_BYTES:
        raise UserError("The file is larger than 10 MB.")
    name = str(value.get("filename") or "upload").strip()[:200] or "upload"
    return env["ir.attachment"].create({"name": name, "datas": data})


def _link_uploads(attachments, model, res_id):
    """Attach the uploads to the record they evidence. sudo: the caller has
    just written that record (its ACL and rules applied), and linking may
    need write access on the record that the caller's attachment ACL checks
    again with stricter rights (a rider cannot edit a consignment header)."""
    if attachments:
        attachments.sudo().write({"res_model": model, "res_id": res_id})


def _child_value_changed(rec, field, value) -> bool:
    """Would this value change a child row? A form re-sends every row it shows,
    so an unchanged echo must not reach a guarded grid (a calibration's readings
    are insert-only, and the echo made every save of its parent refuse)."""
    if field.type in ("one2many", "many2many"):
        return True
    if field.type == "binary":
        current = rec[field.name]
        current = current.decode() if isinstance(current, bytes) else current
        return (value or False) != (current or False)
    return _readonly_changed(rec, field, value)


def _locked_fields(records) -> set:
    """Workflow-locked fields for these records (an empty recordset = a new
    one): fix.guarded.mixin's guarded fields plus whatever the model freezes
    by state. Models without the guard lock nothing beyond `readonly`."""
    hook = getattr(records, "_fix_form_locked_fields", None)
    return set(hook()) if hook else set()


def _read_policy(env, model, names) -> dict:
    """A12 M29 E28: {field: hidden | full | last4 | hash} for this caller, from the
    field rules and the sensitive-field classification. Empty for a cleared caller."""
    if "fix.field.rule" not in env:
        return {}
    return env["fix.field.rule"]._fix_read_policy(model, names)


def _gate(env, need, model=None, module=None):
    """M29 per-module permissions (capture audit 2026-11-14): None when the
    caller may, else the refusal. A user with no narrowed row for the module is
    governed by their roles alone; the Odoo access rules apply either way."""
    if env.su:
        return None
    if module is None and model:
        from ..models.fix_jml_event_permissions import model_module_map

        module = model_module_map().get(model)
    if not module or "fix.module.permission" not in env:
        return None
    return env["fix.module.permission"]._fix_refusal(env.user, module, need)


# A08 (finance) + A02 (service operations) + A03 (customer experience) + A11
# (insights) surfaces, merged: the generic endpoints serve exactly what the
# per-module files declare.
SURFACES = dict(_A08_SURFACES)
for _model, _conf in _A02_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A03_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A04_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A05_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A06_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A07_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A09_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A10_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A12_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf
for _model, _conf in _A11_SURFACES.items():
    if _model in SURFACES:
        raise ValueError("surface %s is declared by two areas" % _model)
    SURFACES[_model] = _conf

# fields never returned over the generic endpoint
_BLOCKED_FIELDS = {"access_token", "write_uid", "create_uid"}
_FAILED = "The request could not be completed — try again or contact Finance support."
# Hard ceiling for an explicit limit override (the export path): an artefact
# must carry the whole grid the screen serves — the real item master is
# 14k+ rows — while a stray request cannot ask for the estate unbounded.
_EXPORT_MAX_ROWS = 50_000


# what a picker's filter may test. The filter arrives from the client and runs
# under sudo, so a free text or amount test would let any internal user guess a
# field they cannot read, one character at a time (a bank account number, say).
_CHOICE_DOMAIN_TYPES = {"selection", "boolean", "many2one", "many2many", "one2many"}
_CHOICE_DOMAIN_OPERATORS = {"=", "!=", "in", "not in", ">"}
_CHOICE_DOMAIN_NUMERIC = {"float", "integer"}


def _choice_domain(env, comodel, domain):
    """A picker's declared filter, checked, or a refusal. Allows workflow tests
    (state, flags, links) and "this quantity is above zero"; nothing that can
    read a value out of a field one guess at a time."""
    domain = domain or []
    if not isinstance(domain, list | tuple):
        raise UserError("This list's filter is not valid")
    try:
        # well formed, or a dangling "|" would OR past the company fence it is ANDed with
        Domain(list(domain))
    except (ValueError, TypeError) as exc:
        raise UserError("This list's filter is not valid") from exc
    for leaf in domain:
        if leaf in ("&", "|", "!"):
            continue
        if not isinstance(leaf, list | tuple) or len(leaf) != 3:
            raise UserError("This list's filter is not valid")
        path, operator, value = leaf
        if not isinstance(path, str) or operator not in _CHOICE_DOMAIN_OPERATORS:
            raise UserError("This list's filter is not valid")
        model = env[comodel]
        target = None
        for index, part in enumerate(path.split(".")):
            target = model._fields.get(part)
            if target is None or target.groups:
                raise UserError("This list's filter is not valid")
            if index < path.count("."):
                if not target.relational:
                    raise UserError("This list's filter is not valid")
                model = env[target.comodel_name]
        numeric_zero = target.type in _CHOICE_DOMAIN_NUMERIC and operator == ">" and value == 0
        if target.type not in _CHOICE_DOMAIN_TYPES and not numeric_zero:
            raise UserError("This list's filter is not valid")
        if target.type in _CHOICE_DOMAIN_TYPES and operator == ">":
            raise UserError("This list's filter is not valid")
    return list(domain)


class P03GenericApiController(http.Controller):
    """Whitelisted generic reads + workflow actions for the A08 model screens."""

    # allowed UI-language codes the workspace may request labels in (audit D3)
    _LANGS = {"en": "en_US", "en_US": "en_US", "bn": "bn_BD", "bn_BD": "bn_BD"}

    @http.route("/p03/model/records", type="jsonrpc", auth="user", readonly=True)
    def model_records(
        self,
        model=None,
        cols=None,
        domain=None,
        state_filter=None,
        lang=None,
        search=None,
        offset=0,
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        refused = _gate(env, "view", model=model)
        if refused:
            return {"error": refused}
        try:
            # bilingual headers: labels follow the workspace UI language when
            # the module ships a translation (Odoo falls back to English).
            # Odoo 19: Environment has no with_context — env(context=...).
            lang_code = self._LANGS.get(lang)
            if lang_code and lang_code != env.context.get("lang"):
                env = env(context={**env.context, "lang": lang_code})
            # The company-wide read below runs sudo (an accountant sees every
            # operating unit), so the caller must first hold READ access on the
            # model itself: finance/payroll ACL groups still decide who sees it.
            env[model].check_access("read")
            fields_meta = env[model].fields_get(
                [c for c in (cols or []) if c not in _BLOCKED_FIELDS],
                attributes=["string", "type", "selection"],
            )
            # drop unknown columns defensively
            cols = [c for c in (cols or []) if c in fields_meta]
            if "id" not in cols:
                cols = ["id", *cols]
            search_domain = list(domain or [])
            # a surface may pin a BASE DOMAIN every read respects (2026-11-09:
            # the M33 party register is scoped to customer parties — login
            # and staff partners never mix into the customer grid/export).
            base_domain = conf.get("base_domain")
            if base_domain:
                search_domain = list(base_domain) + search_domain
            if state_filter:
                state_field = kw.get("state_field")
                if state_field and state_filter not in ("__all", "__all__", "all", ""):
                    search_domain.append((state_field, "=", state_filter))
            # Finance list screens are COMPANY-wide reads (an accountant sees
            # every operating unit's bills — the M19 CoA sudo-read pattern).
            # A surface may opt OUT of the sudo read with "rules": True (the
            # A09 pattern — people data, M29 res.users / res.device.log;
            # the A10 pattern — W1, an investigator sees only their assigned
            # whistle reports, never the whole register the ACL alone would
            # allow) or "caller_scoped": True (the A11 pattern — M26 X03,
            # the PdM prediction list): either way its rows are read AS THE
            # CALLER, so the caller's ACLs and OU record rules apply and one
            # unit's rows never leak onto another unit's screen. Writes
            # below keep the calling user's context (SoD/permissions apply).
            rec_model = (
                env[model]
                if (conf.get("rules") or conf.get("caller_scoped"))
                else env[model].sudo()
            )
            search_domain += _company_fence(env, model, conf)
            search_domain += self._records_search_domain(env[model], cols, search)
            offset = max(int(offset or 0), 0)
            effective_limit = min(int(kw.get("limit") or conf["limit"]), _EXPORT_MAX_ROWS)
            records = rec_model.search(
                search_domain, order=conf["order"], limit=effective_limit, offset=offset
            )
            raw = records.read(cols) if records else []
            rows = []
            for rec in raw:
                row = {}
                for c in cols:
                    v = rec.get(c)
                    meta = fields_meta.get(c, {})
                    if meta.get("type") in ("many2one",) and isinstance(v, list | tuple):
                        row[c] = {"id": v[0], "name": v[1]} if v else None
                    elif meta.get("type") == "selection":
                        labels = dict(meta.get("selection") or [])
                        # an unset selection is an EMPTY cell, not the literal
                        # "false" (the label lookup returns False and the grid
                        # printed it — M13 turnaround regrade, audit D4 class)
                        row[c] = {"key": v, "label": labels.get(v, v)} if v else ""
                    elif meta.get("type") == "datetime" and v:
                        row[c] = _datetime_to_local(env, v)[:16]
                    elif v is False and meta.get("type") != "boolean":
                        # Odoo returns `false` for EVERY empty field; only a
                        # BOOLEAN false is a real ✗ — an empty phone/name is
                        # a blank, never "✗" (audit D16, user's PDF)
                        row[c] = ""
                    else:
                        row[c] = v
                rows.append(row)
            policy = _read_policy(env, model, cols)
            if policy:
                for row in rows:
                    env["fix.field.rule"]._fix_apply_policy(row, policy)
            # total beyond the page: "200 of 15,413" — a bare "200 records"
            # reads as the whole base when the limit clipped it
            total = (
                rec_model.search_count(search_domain)
                if offset or len(rows) >= effective_limit
                else len(rows)
            )
            return {
                "model": model,
                "rows": rows,
                "count": len(rows),
                "total": total,
                "offset": offset,
                "labels": {c: fields_meta[c]["string"] for c in cols if c in fields_meta},
                # column types so the grid formats by FIELD TYPE, never by
                # magnitude (a ৳800 damage figure must not read as "800", and
                # a 1,500 count must not gain a ৳ prefix)
                "kinds": {c: fields_meta[c]["type"] for c in cols if c in fields_meta},
            }
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except psycopg2.errors.ReadOnlySqlTransaction:
            raise  # http.py retries a read-only route on a read/write cursor
        except Exception:
            _logger.exception("p03 model_records failed for %s", model)
            return {"error": _FAILED}

    @staticmethod
    def _records_search_domain(records, cols, term) -> list:
        """Quick Find on the server, so it reaches rows beyond the loaded page.
        It searches only the columns the screen shows, and only those SQL can
        search; a selection is matched on its label."""
        term = (term or "").strip()
        if not term:
            return []
        parts = []
        for name in cols:
            field = records._fields.get(name)
            if not field or not (field.store or field.search):
                continue
            if field.type in ("char", "text", "html", "many2one"):
                parts.append((name, "ilike", term))
            elif field.type == "selection":
                keys = [
                    key
                    for key, label in field._description_selection(records.env)
                    if term.lower() in str(label).lower()
                ]
                if keys:
                    parts.append((name, "in", keys))
        if not parts:
            return []
        return ["|"] * (len(parts) - 1) + parts

    @http.route("/p03/model/lookup", type="jsonrpc", auth="user", readonly=True)
    def model_lookup(self, model=None, field=None, term=None, limit=30, **kw):
        """A many2one search box: a declared form field's choices, as the user types."""
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        try:
            env[model].check_access("read")
            spec = env[model]._fields.get(field)
            writable = conf.get("writable")
            if (
                not spec
                or spec.type not in ("many2one", "many2many")
                or spec.comodel_name == "ir.attachment"
                or (writable is not None and field not in writable)
            ):
                return {"error": "This field cannot be searched on this screen."}
            declared = _choice_domain(env, spec.comodel_name, kw.get("domain"))
            domain = Domain.AND(
                [Domain(declared), Domain(_picker_domain(env, conf, spec.comodel_name, field))]
            )
            found = _picker_source(env, spec.comodel_name, conf, field).name_search(
                term or "", domain, limit=min(int(limit or 30), 50)
            )
            return {"rows": [{"id": row[0], "label": row[1]} for row in found]}
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except psycopg2.errors.ReadOnlySqlTransaction:
            raise
        except Exception:
            _logger.exception("p03 model_lookup failed for %s.%s", model, field)
            return {"error": _FAILED}

    @http.route("/p03/model/report", type="jsonrpc", auth="user", readonly=True)
    def model_report(self, module=None, report=None, params=None, **kw):
        """A module's declared report: controllers/<area>/<module>.py REPORTS
        maps name -> fn(env, **params) returning {cols, labels, rows,
        totals?, notes?, title?, empty?}. The function reads with the
        caller's env, so the models' own access rules apply."""
        _require_internal(request.env)
        if not report_delivery.pack_function(module, report):
            return {"error": "Report not available on this surface"}
        refused = _gate(request.env, "view", module=module)
        if refused:
            return {"error": refused}
        try:
            pack_params, _doc = report_delivery.split_params(params)
            return report_delivery.run_pack(request.env, module, report, pack_params)
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except psycopg2.errors.ReadOnlySqlTransaction:
            raise  # http.py retries a read-only route on a read/write cursor
        except Exception:
            _logger.exception("p03 model_report %s.%s failed", module, report)
            return {"error": _FAILED}

    @http.route("/p03/model/report/export", type="http", auth="user")
    def model_report_export(self, module=None, report=None, format="csv", **params):
        """Download any built-in module report as CSV, Excel or PDF.

        The payload is EXACTLY the one /p03/model/report serves (same function,
        same caller ACL, same period and filters) - the export cannot drift
        from the screen. CSV values are raw so spreadsheets can compute; the
        XLSX workbook and the PDF are the company documents: letterhead,
        report meta (company, period, filters, generated by/at), data, totals
        and notes. ``inline=1`` opens the PDF in a tab to view or print."""
        _require_internal(request.env)
        if format not in report_delivery.FORMATS:
            return self._plain(400, "format must be csv, xlsx or pdf")
        if not report_delivery.pack_function(module, report):
            return self._plain(404, "Report not available on this surface")
        refused = _gate(request.env, "print" if format == "pdf" else "export", module=module)
        if refused:
            return self._plain(403, refused)
        pack_params, doc = report_delivery.split_params(params)
        try:
            art = report_delivery.build(
                request.env, module, report, format, pack_params, doc.get("module_label")
            )
        except (UserError, AccessError) as exc:
            return self._plain(403, _user_error(exc))
        report_delivery.log_export(
            request.env, "%s:%s" % (module, report), "download", format, art["count"], pack_params
        )
        inline = format == "pdf" and doc.get("inline") in ("1", "true", "True")
        return request.make_response(
            art["data"],
            headers=[
                ("Content-Type", art["mimetype"]),
                (
                    "Content-Disposition",
                    '%s; filename="%s"' % ("inline" if inline else "attachment", art["filename"]),
                ),
            ],
        )

    @http.route("/p03/model/report/email", type="jsonrpc", auth="user", readonly=False)
    def model_report_email(
        self,
        module=None,
        report=None,
        params=None,
        module_label=None,
        to=None,
        subject=None,
        body=None,
        format="pdf",
        **kw,
    ):
        """Email a built-in report as an Excel or PDF attachment - the SAME
        document the download buttons give for the same period and filters."""
        _require_internal(request.env)
        env = request.env
        refused = _gate(env, "email", module=module)
        if refused:
            return {"error": refused}
        if format not in report_delivery.MAIL_FORMATS:
            return {"error": "Attachment format must be xlsx or pdf"}
        emails, err = report_delivery.parse_recipients(to)
        if err:
            return {"error": err}
        if not report_delivery.pack_function(module, report):
            return {"error": "Report not available on this surface"}
        pack_params, _doc = report_delivery.split_params(params)
        try:
            art = report_delivery.build(env, module, report, format, pack_params, module_label)
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 report email %s.%s failed to build", module, report)
            return {"error": _FAILED}
        scope = []
        if pack_params.get("date_from") or pack_params.get("date_to"):
            scope.append(
                "%s → %s" % (pack_params.get("date_from") or "…", pack_params.get("date_to") or "…")
            )
        result = report_delivery.send_mail(
            env,
            emails,
            art["data"],
            art["filename"],
            art["title"],
            art["count"],
            subject=subject,
            body=body,
            scope=" · ".join(scope) or None,
        )
        report_delivery.log_export(
            env,
            "%s:%s" % (module, report),
            "email",
            format,
            art["count"],
            dict(pack_params, recipients=len(emails)),
        )
        return result

    @staticmethod
    def _plain(status, text):
        return request.make_response(
            text, status=status, headers=[("Content-Type", "text/plain; charset=utf-8")]
        )

    # ------------------------------------------------------------------
    # List-grid export suite (user directive 2026-11-07): every model_list
    # screen downloads as a branded Excel workbook, PDF or CSV, and can be
    # sent by email as an attachment — all from EXACTLY the payload
    # /p03/model/records serves, so an export can never drift from the grid.
    # ------------------------------------------------------------------
    def _ml_flat_cell(self, v):
        """One model_list cell to its printable form: booleans Yes/No,
        selection labels, many2one names — the same text the grid shows."""
        if v is None or v == "":
            return ""
        if isinstance(v, bool):
            return "Yes" if v else "No"
        if isinstance(v, dict):
            return v.get("label") or v.get("name") or ""
        return v

    @staticmethod
    def _list_scope(domain=None, state_field=None, state_filter=None, search=None):
        """The screen's own scope, as the grid read it: its declared domain
        (a scoped view such as the Unassigned Queue), the status pill and the
        Quick Find text. A GET export carries the domain as JSON. Without this
        an export of a scoped screen used to carry the WHOLE model."""
        if isinstance(domain, str):
            import json

            try:
                domain = json.loads(domain) if domain.strip() else []
            except ValueError:
                domain = None
        if not isinstance(domain, list):
            domain = []
        return {
            "domain": domain,
            "state_field": state_field or None,
            "state_filter": state_filter or None,
            "search": (search or "").strip() or None,
        }

    def _model_list_export_payload(self, model, cols, lang, limit=None, scope=None):
        """{rows (flattened), labels, title, count} for a served model —
        the /p03/model/records read, reused verbatim with the screen's scope.
        The export passes an explicit limit so the artefact carries the WHOLE
        grid the screen serves (the real item master is 14k+ rows), never one
        UI page."""
        scope = scope or self._list_scope()
        col_list = cols if isinstance(cols, list) else [c for c in (cols or "").split(",") if c]
        data = self.model_records(
            model=model,
            cols=col_list or None,
            domain=scope["domain"],
            state_filter=scope["state_filter"],
            state_field=scope["state_field"],
            search=scope["search"],
            lang=lang,
            limit=limit or _EXPORT_MAX_ROWS,
        )
        if data.get("error"):
            return None, data["error"]
        cols_out = [c for c in (col_list or list(data["labels"].keys())) if c in data["labels"]]
        rows = [{c: self._ml_flat_cell(r.get(c)) for c in cols_out} for r in data.get("rows") or []]
        return {
            "rows": rows,
            "cols": cols_out,
            "labels": data["labels"],
            "count": data.get("count", len(rows)),
        }, None

    def _list_artifact(self, fmt, payload, model, title=None, module=None, module_label=None):
        """(bytes, filename, mimetype) of a list grid - one builder for the
        download buttons and the email, so the attachment IS the download."""
        name = "%s_list_export" % (model or "records").replace(".", "_")
        title = str(title or "")[:120] or (model or "records").replace(".", " ").title()
        if fmt == "xlsx":
            out = dict(payload, title=title, notes=[])
            meta = {"module": module or "", "module_label": str(module_label or "")[:80]}
            data = report_bytes.xlsx_bytes(
                request.env, out, payload["cols"], payload["labels"], name, meta
            )
            return (
                data,
                name + ".xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        if fmt == "pdf":
            rows = payload["rows"]
            notes = []
            if len(rows) > report_delivery.PDF_MAX_ROWS:
                notes.append(
                    "This document shows the first %s of %s rows; the Excel file carries them all."
                    % (f"{report_delivery.PDF_MAX_ROWS:,}", f"{len(rows):,}")
                )
                rows = rows[: report_delivery.PDF_MAX_ROWS]
            pdf_payload = dict(
                payload,
                rows=rows,
                notes=notes,
                meta={
                    "module": module or "",
                    "module_label": str(module_label or "")[:80],
                    "title": title,
                    "notes": notes,
                },
            )
            data = report_bytes.pdf_bytes(request.env, pdf_payload, name, title=title)
            return data, name + ".pdf", "application/pdf"
        data = report_delivery.csv_bytes(payload, payload["cols"], payload["labels"])
        return data, name + ".csv", "text/csv; charset=utf-8"

    @http.route("/p03/model/list/export", type="http", auth="user")
    def model_list_export(
        self,
        model=None,
        format="xlsx",
        cols=None,
        lang=None,
        domain=None,
        state_field=None,
        state_filter=None,
        search=None,
        **kw,
    ):
        """Download any model_list grid as a branded XLSX / PDF / CSV - the
        rows the screen shows (its scope, status filter and search), with the
        official 1000 FiX letterhead (logo, address, ISO badge)."""
        _require_internal(request.env)
        if format not in ("xlsx", "pdf", "csv"):
            return request.make_response("format must be xlsx, pdf or csv", status=400)
        refused = _gate(request.env, "print" if format == "pdf" else "export", model=model)
        if refused:
            return request.make_response(refused, status=403)
        scope = self._list_scope(domain, state_field, state_filter, search)
        payload, err = self._model_list_export_payload(model, cols, lang, scope=scope)
        if err:
            return request.make_response(err, status=400)
        _log_report_export(model or "list", "model_list:%s" % model, format, payload, scope)
        data, filename, mimetype = self._list_artifact(
            format, payload, model, kw.get("title"), kw.get("module"), kw.get("module_label")
        )
        inline = format == "pdf" and kw.get("inline") in ("1", "true", "True")
        return request.make_response(
            data,
            headers=[
                ("Content-Type", mimetype),
                (
                    "Content-Disposition",
                    '%s; filename="%s"' % ("inline" if inline else "attachment", filename),
                ),
            ],
        )

    @http.route("/p03/model/list/email", type="jsonrpc", auth="user", readonly=False)
    def model_list_email(
        self,
        model=None,
        module=None,
        report=None,
        to=None,
        subject=None,
        body=None,
        format="xlsx",
        cols=None,
        lang=None,
        domain=None,
        state_field=None,
        state_filter=None,
        search=None,
        title=None,
        module_label=None,
        params=None,
        **kw,
    ):
        """Email a model_list grid as a branded attachment (XLSX or PDF) - the
        same rows and document the download buttons give. A report pack
        (module + report) takes the report email's path. Recipients are
        validated; the mail is queued through Odoo's own mail.mail (an SMTP
        failure reports the mail's state honestly)."""
        _require_internal(request.env)
        env = request.env
        if module and report:
            return self.model_report_email(
                module=module,
                report=report,
                params=params,
                module_label=module_label,
                to=to,
                subject=subject,
                body=body,
                format=format,
            )
        if format not in report_delivery.MAIL_FORMATS:
            return {"error": "Attachment format must be xlsx or pdf"}
        refused = _gate(env, "email", model=model)
        if refused:
            return {"error": refused}
        emails, err = report_delivery.parse_recipients(to)
        if err:
            return {"error": err}
        scope = self._list_scope(domain, state_field, state_filter, search)
        payload, err = self._model_list_export_payload(model, cols, lang, scope=scope)
        if err:
            return {"error": err}
        data, filename, _mimetype = self._list_artifact(
            format, payload, model, title, module, module_label
        )
        result = report_delivery.send_mail(
            env,
            emails,
            data,
            filename,
            str(title or "")[:120] or (model or "records").replace(".", " ").title(),
            payload["count"],
            subject=subject,
            body=body,
            scope=module_label or None,
        )
        report_delivery.log_export(
            env,
            "%s:model_list:%s" % (module or "list", model),
            "email",
            format,
            payload["count"],
            dict(scope, recipients=len(emails)),
        )
        return result

    # brand-60 (tokens.json color.brand.60) — the workbook accent
    _XLSX_BRAND = "0E7A6E"
    _XLSX_INK = "242424"
    _XLSX_GREY = "F5F5F5"

    def _report_meta(self, params):
        """Compatibility shim: the meta block now lives in report_bytes."""
        return report_bytes._report_meta(request.env, params)

    def _report_xlsx(self, out, cols, labels, base_name, params):
        """Branded XLSX download — the shared byte-builder (report_bytes)
        wrapped in an HTTP response (downloads, email and the scheduled
        subscriptions render the identical artefact)."""
        data = report_bytes.xlsx_bytes(request.env, out, cols, labels, base_name, params)
        return request.make_response(
            data,
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", 'attachment; filename="%s.xlsx"' % base_name),
            ],
        )

    @http.route("/p03/model/form", type="jsonrpc", auth="user", readonly=True)
    def model_form(
        self,
        model=None,
        fields=None,
        record_id=None,
        lang=None,
        lines=None,
        status_field=None,
        grids=None,
        **kw,
    ):
        """Schema + values for a D365 in-workspace form screen.

        fields: [{name, type?, label?, required?, readonly?}] declared by the
        module fragment (order preserved). Returns per-field metadata from the
        model (labels/types/selection) and, when record_id is given, the
        record's values plus the choices for many2one fields.

        lines (optional): {field, fields:[{name,label,type?}]} — a declared
        one2many child grid (allocation targets, template lines). Returns the
        child field metadata and, for an existing record, its rows.

        grids (optional): [{field, fields:[...]}] - several such child grids
        on one form (a candidate's education, training, experience and
        documents, 18 Nov 2026), each returned under its field name. A file
        cell in a grid row is served as a link, never as its bytes.
        """
        _require_internal(request.env)
        env = request.env
        lang_code = self._LANGS.get(lang)
        if lang_code and lang_code != env.context.get("lang"):
            env = env(context={**env.context, "lang": lang_code})
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        refused = _gate(env, "view" if record_id else "create", model=model)
        if refused:
            return {"error": refused}
        try:
            env[model].check_access("read")
            rec = None
            if record_id:
                if conf.get("rules") or conf.get("caller_scoped"):
                    # W1-class surfaces: the record rule decides — browsing a
                    # record the caller may not see (an investigator opening
                    # another's whistleblowing report by ID; A09 audit M21-5,
                    # another company's NID by id) fails read access cleanly
                    # instead of leaking it through sudo.
                    rec = env[model].browse(int(record_id)).exists()
                    if rec:
                        rec.check_access("read")
                else:
                    rec = env[model].sudo().browse(int(record_id)).exists()
            out_fields = self._form_field_meta(env, model, fields, rec or None)
            policy = _read_policy(env, model, [f["name"] for f in out_fields])
            out_fields = [f for f in out_fields if policy.get(f["name"]) != "hidden"]
            record = None
            if rec:
                record = self._form_record(rec, out_fields)
                if policy:
                    env["fix.field.rule"]._fix_apply_policy(record, policy)
            for entry in out_fields:
                if entry["name"] in policy:
                    # masked: shown as text, never an input the save could write back
                    entry.update(readonly=True, type="char", required=False, choices=[])
            line_payload = None
            if lines and lines.get("field"):
                line_payload = self._form_lines(env, model, lines, record_id)
            grid_payload = {}
            for grid in grids or []:
                if isinstance(grid, dict) and grid.get("field"):
                    grid_payload[grid["field"]] = self._form_lines(
                        env, model, grid, record_id, files_as_links=True
                    )
            # The form's status pill reads a workflow field that is usually NOT
            # one of its inputs (a state is never editable), so it is served on
            # its own; without this the pill never rendered on such a form.
            status_value = None
            status_meta = rec._fields.get(status_field) if rec and status_field else None
            if status_meta and status_meta.type in ("selection", "char", "boolean"):
                status_value = rec[status_field]
            return {
                "model": model,
                "fields": out_fields,
                "record": record,
                "defaults": {} if rec else self._form_defaults(env, model, out_fields),
                "lines": line_payload,
                "grids": grid_payload,
                "status_value": status_value,
                "title": conf.get("form_title") or env[model]._description,
            }
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except psycopg2.errors.ReadOnlySqlTransaction:
            # a read that must write (A09 identity read log) on the read-only
            # cursor: http.py retries the route on a read/write cursor
            raise
        except Exception:
            _logger.exception("p03 model_form failed for %s", model)
            return {"error": "The form data could not be loaded — see the server log."}

    @staticmethod
    def _form_defaults(env, model, out_fields) -> dict:
        """A new form must show what will really be saved. A tick box defaulting
        to True drew unticked, and an untouched box posted nothing, so a count
        leaving "Found" at No was stored as found (and could clear a loss)."""
        # Also a date, a choice and a reference the model fills by itself: a
        # proforma showed Currency and Issued On empty although BDT and today
        # are what the save stores (12 Nov 2026). Values take the record's
        # own shape (a reference as {id, label}, a date as YYYY-MM-DD).
        kinds = ("boolean", "selection", "date", "many2one")
        by_name = {f["name"]: f for f in out_fields if f["type"] in kinds and not f["readonly"]}
        if not by_name:
            return {}
        raw = env[model].default_get(list(by_name))
        out = {}
        for name, value in raw.items():
            kind = by_name[name]["type"]
            if kind == "boolean":
                out[name] = value
            elif value in (None, False, ""):
                continue
            elif kind == "many2one":
                comodel = env[model]._fields[name].comodel_name
                try:
                    target = (
                        env[comodel].browse(value if isinstance(value, int) else value[0]).exists()
                    )
                    if target:
                        out[name] = {"id": target.id, "label": target.display_name}
                except (AccessError, UserError):
                    continue  # a default the user may not read is saved, not shown
            elif kind == "date":
                out[name] = str(value)[:10]
            else:
                out[name] = value
        # the form's own default overrides the model's (an import PO in USD)
        for name, entry in by_name.items():
            ref = entry.get("default_ref")
            if not ref:
                continue
            target = env.ref(ref, raise_if_not_found=False)
            comodel = env[model]._fields[name].comodel_name
            if target and target._name == comodel:
                out[name] = {"id": target.id, "label": target.sudo().display_name}
        return out

    def _form_field_meta(self, env, model, fields, record=None):
        """Per-field metadata (label, type, required, choices) preserving the
        fragment's declared order. many2one choices come from the comodel.

        A field the model locks for this record (state, an approval stamp, a
        posted ledger line's points) is served read-only, so the form never
        offers an input the save would refuse (A03 workflow audit, R3/R5)."""
        names = [f.get("name") for f in (fields or []) if f.get("name")]
        meta = env[model].fields_get(
            names, attributes=["string", "type", "selection", "required", "readonly"]
        )
        locked = _locked_fields(record if record is not None else env[model])
        out_fields = []
        for spec in fields or []:
            name = spec.get("name")
            m = meta.get(name)
            if not m:
                continue
            field_type = spec.get("type") or m["type"]
            if m["type"] == "many2one" and env[model]._fields[name].comodel_name == "ir.attachment":
                field_type = "attachment"  # an upload, never a list of files
            entry = {
                "name": name,
                "label": spec.get("label") or m["string"],
                "type": field_type,
                "required": bool(spec.get("required") or m.get("required")),
                "readonly": bool(spec.get("readonly") or m.get("readonly") or name in locked),
            }
            # `defaultRef`: a form's own default for a reference, by XML id
            # (the import purchase order starts in USD, the model's BDT is the
            # local order's) - applied to a NEW record only (_form_defaults)
            if spec.get("defaultRef") and field_type == "many2one":
                entry["default_ref"] = spec["defaultRef"]
            if field_type == "selection":
                entry["choices"] = [
                    {"key": k, "label": v}
                    for k, v in (spec.get("choices") or m.get("selection") or [])
                ]
            if field_type in ("many2one", "many2many"):
                comodel = env[model]._fields[name].comodel_name
                entry["comodel"] = comodel
                # A06 fragments declare a filter (parts in stock), checked by
                # _choice_domain; the surface declares its own and fences the
                # caller's companies (A07). Both apply, combined as parsed domains.
                declared = _choice_domain(env, comodel, spec.get("domain"))
                domain = Domain.AND(
                    [
                        Domain(declared),
                        Domain(_picker_domain(env, SURFACES.get(model), comodel, name)),
                    ]
                )
                options = _picker_source(env, comodel, SURFACES.get(model), name)
                if declared:
                    entry["choice_domain"] = declared
                # A longer list used to stop silently at the limit: 15,522
                # partners offered the first 300, and a record whose value lay
                # beyond them showed blank. A header many2one becomes a search
                # box (remote, no list sent); a many2many or a grid cell gets a
                # search input beside what it shows (truncated).
                over = options.search_count(domain, limit=PICKER_LIMIT + 1) > PICKER_LIMIT
                entry["remote"] = field_type == "many2one" and over
                entry["truncated"] = over
                entry["choices"] = (
                    []
                    if entry["remote"]
                    else [
                        {"id": r["id"], "label": r["display_name"]}
                        for r in options.search_read(domain, ["display_name"], limit=PICKER_LIMIT)
                    ]
                )
                if record is not None and field_type == "many2one" and len(record) == 1:
                    current = record[name]
                    if current and all(c["id"] != current.id for c in entry["choices"]):
                        entry["choices"].insert(
                            0, {"id": current.id, "label": current.sudo().display_name}
                        )
            out_fields.append(entry)
        return out_fields

    def _form_record(self, rec, out_fields):
        record = {"id": rec.id}
        for entry in out_fields:
            value = rec[entry["name"]]
            if entry["type"] == "attachment":
                record[entry["name"]] = (
                    {
                        "id": value.id,
                        "label": value.sudo().name or "file",
                        "url": "/web/content/%d?download=true" % value.id,
                    }
                    if value
                    else None
                )
            elif entry["type"] == "many2one":
                record[entry["name"]] = (
                    {"id": value.id, "label": value.display_name} if value else None
                )
            elif entry["type"] == "many2many":
                record[entry["name"]] = [{"id": r.id, "label": r.display_name} for r in value]
            elif entry["type"] in ("date",):
                record[entry["name"]] = str(value) if value else ""
            elif entry["type"] == "datetime":
                record[entry["name"]] = _datetime_to_local(rec.env, value)
            elif entry["type"] == "monetary":
                record[entry["name"]] = float(value or 0.0)
            else:
                record[entry["name"]] = value if value is not False else ""
        return record

    def _form_lines(self, env, model, lines, record_id, files_as_links=False):
        """A declared one2many child grid: field meta + existing rows.

        files_as_links: a binary cell is served as {stored, filename, size,
        url} (the record's own /web/content link), so a grid of scanned
        certificates does not ship every file to the browser."""
        field_name = lines.get("field")
        field = env[model]._fields.get(field_name)
        if not field or field.type != "one2many":
            raise UserError("This form's child grid is not a one2many")
        comodel = field.comodel_name
        out_fields = self._form_field_meta(env, comodel, lines.get("fields"))
        rows = []
        if record_id:
            # the parent surface's "rules" flag governs its child grid too
            conf = SURFACES.get(model) or {}
            read_model = env[model] if conf.get("rules") else env[model].sudo()
            rec = read_model.browse(int(record_id)).exists()
            if rec:
                binaries = [m["name"] for m in out_fields if m["type"] == "binary"]
                plain = (
                    [m for m in out_fields if m["type"] != "binary"]
                    if files_as_links
                    else out_fields
                )
                for child in rec[field_name]:
                    row = self._form_record(child, plain)
                    if files_as_links:
                        sized = child.with_context(bin_size=True)
                        for name in binaries:
                            row[name] = self._grid_file(sized, name)
                    rows.append(row)
                # a row's value beyond the choice limit must still display
                for meta in out_fields:
                    if meta["type"] != "many2one":
                        continue
                    known = {c["id"] for c in meta["choices"]}
                    for row in rows:
                        value = row.get(meta["name"])
                        if value and value["id"] not in known:
                            known.add(value["id"])
                            meta["choices"].append({"id": value["id"], "label": value["label"]})
        return {"field": field_name, "model": comodel, "fields": out_fields, "rows": rows}

    @staticmethod
    def _grid_file(child, name):
        """A stored file of a grid row, as a link (None when there is none)."""
        size = child[name]
        if not size:
            return None
        fname = ""
        fname_field = None
        for cand in (
            name + "_filename",
            name.removesuffix("_file") + "_filename",
            name.removesuffix("_file") + "_name",
            "file_name",
        ):
            if cand in child._fields and child[cand]:
                fname, fname_field = child[cand], cand
                break
        size = size.decode() if isinstance(size, bytes) else str(size)
        return {
            "stored": True,
            "filename": fname or name,
            "size": size,
            "url": "/web/content/%s/%d/%s?download=true%s"
            % (
                child._name,
                child.id,
                name,
                "&filename_field=%s" % fname_field if fname_field else "",
            ),
        }

    @http.route("/p03/model/choices", type="jsonrpc", auth="user", readonly=True)
    def model_choices(
        self, model=None, field=None, q=None, parent_model=None, parent_field=None, **kw
    ):
        """Server search for a many2one input whose list exceeds the choice
        limit. Serves only a field of a served model, or of the child grid a
        served model declares; returns ids and display names, as the form does.
        The domain is the one the fragment's field spec declares."""
        _require_internal(request.env)
        env = request.env
        served = model in SURFACES
        if not served and parent_model in SURFACES and parent_field:
            parent = env[parent_model]._fields.get(parent_field)
            served = bool(parent and parent.type == "one2many" and parent.comodel_name == model)
        if not served or model not in env:
            return {"error": "Model not served by the workspace screens"}
        target = env[model]._fields.get(field)
        if not target or target.type not in ("many2one", "many2many"):
            return {"error": "This field has no choices"}
        try:
            env[model].check_access("read")
            comodel = target.comodel_name
            declared = _choice_domain(env, comodel, kw.get("domain"))
            domain = Domain.AND(
                [Domain(declared), Domain(_picker_domain(env, SURFACES.get(model), comodel, field))]
            )
            found = _picker_source(env, comodel, SURFACES.get(model), field).name_search(
                name=(q or "").strip(), domain=domain, limit=50
            )
            return {"choices": [{"id": i, "label": label} for i, label in found]}
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except psycopg2.errors.ReadOnlySqlTransaction:
            raise
        except Exception:
            _logger.exception("p03 model_choices failed for %s.%s", model, field)
            return {"error": _FAILED}

    @http.route("/p03/model/write", type="jsonrpc", auth="user")
    def model_write(self, model=None, record_id=None, values=None, lines=None, grids=None, **kw):
        """Create/update one record from a D365 in-workspace form.

        The caller's own ACL applies (no sudo on write); the whole write runs
        in a savepoint so a refusal leaves nothing behind — the M19 leaked-
        draft rule. Only models declared in SURFACES are accepted.

        lines (optional): {field, rows:[{id?, values}], removed:[id]} — the
        declared one2many child grid, applied in the SAME write as the header
        so a rule refusal (targets must total 100%) leaves nothing behind.
        """
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        refused = _gate(env, "edit" if record_id else "create", model=model)
        if refused:
            return {"error": refused}
        vals = self._coerce_vals(values)
        self._datetimes_to_utc(env, model, vals)
        # What the form may not set (A03 audit: this endpoint wrote
        # dofa_approved, released_by, executed_by... as sent):
        #  - read-only fields and fields the model locks for this record
        #    (fix.guarded.mixin), which change only through an action;
        #  - on a surface that declares `writable` (R3), any field no
        #    workspace form offers for editing.
        # The form posts every field it shows, so on edit an unchanged echo
        # is dropped and only a CHANGE is refused. On create they are dropped
        # so the model's defaults and computes apply.
        fields_meta = env[model]._fields
        # E28: what this caller cannot read, this caller cannot echo back or
        # overwrite blind: a field the model restricts by group, and on an existing
        # record a hidden or masked one (the form shows ***, not the value)
        readable = env[model].fields_get(list(vals), attributes=["type"])
        vals = {k: v for k, v in vals.items() if k in readable or k not in fields_meta}
        if record_id:
            for name in _read_policy(env, model, list(vals)):
                vals.pop(name, None)
        current = env[model].browse(int(record_id)).exists() if record_id else env[model]
        if record_id and not current:
            return {"error": "Record not found"}
        # a many2many input posts the ids it holds: the whole selection, replaced
        for key, value in list(vals.items()):
            is_many = getattr(fields_meta.get(key), "type", "") == "many2many"
            if (
                is_many
                and isinstance(value, list)
                and all(isinstance(v, int | dict) for v in value)
            ):
                ids = [v["id"] if isinstance(v, dict) else v for v in value]
                vals[key] = [(6, 0, ids)]
        locked = _locked_fields(current)
        workflow = [
            k for k in vals if k in fields_meta and (fields_meta[k].readonly or k in locked)
        ]
        writable = conf.get("writable")
        off_screen = (
            [] if writable is None else [k for k in vals if k not in writable and k not in workflow]
        )
        if lines and lines.get("field") and writable is not None and lines["field"] not in writable:
            return {"error": "This screen does not edit %s." % lines["field"]}
        grids = [g for g in (grids or []) if isinstance(g, dict) and g.get("field")]
        for grid in grids:
            if writable is not None and grid["field"] not in writable:
                return {"error": "This screen does not edit %s." % grid["field"]}
        if record_id:
            for names, why in (
                (workflow, "is read-only and changes only through its workflow action."),
                (off_screen, "is not editable on this screen."),
            ):
                changed = [
                    k
                    for k in names
                    if k not in fields_meta or _readonly_changed(current, fields_meta[k], vals[k])
                ]
                if changed:
                    return {
                        "error": "%s %s"
                        % (
                            ", ".join(
                                (fields_meta[k].string if k in fields_meta else k) or k
                                for k in changed
                            ),
                            why,
                        )
                    }
        for k in workflow + off_screen:
            vals.pop(k)
        if not record_id:
            # On CREATE an unset many2one must be OMITTED, not sent as NULL: the
            # model's own default (usually the current company) then applies.
            # Sending an explicit NULL hit a NOT NULL company column and turned a
            # plain create into a NotNullViolation. On write the key is kept so a
            # user can still clear a relation.
            fields_meta = env[model]._fields
            vals = {
                k: v
                for k, v in vals.items()
                if not (
                    getattr(fields_meta.get(k), "type", "") == "many2one"
                    and v in (False, None, "", 0)
                )
            }
        try:
            with env.cr.savepoint():
                # an evidence upload becomes the caller's attachment, linked to
                # the record below (in this savepoint: a refusal keeps no file)
                uploads = env["ir.attachment"]
                for key, value in list(vals.items()):
                    if not _is_upload(value):
                        continue
                    spec = env[model]._fields.get(key)
                    if getattr(spec, "comodel_name", None) != "ir.attachment":
                        return {"error": "This field does not take a file."}
                    attachment = _store_upload(env, value)
                    uploads |= attachment
                    vals[key] = attachment.id
                for spec in ([lines] if lines and lines.get("field") else []) + grids:
                    field = env[model]._fields.get(spec.get("field"))
                    if not field or field.type != "one2many":
                        return {"error": "This form's child grid is not a one2many"}
                    commands = self._grid_commands(env, field, spec)
                    if commands:
                        vals[spec["field"]] = commands
                if record_id:
                    env[model].check_access("write")
                    rec = env[model].browse(int(record_id)).exists()
                    if not rec:
                        return {"error": "Record not found"}
                    rec.write(vals)
                else:
                    env[model].check_access("create")
                    rec = env[model].create(vals)
                _link_uploads(uploads, model, rec.id)
                return {"id": rec.id, "display_name": rec.display_name}
        except (UserError, AccessError, ValidationError) as exc:
            return {"error": _user_error(exc)}
        except Exception as exc:
            # IntegrityError (a UNIQUE/check constraint) is a RULE refusal, not
            # a server fault: say so instead of the generic support message.
            # A CHECK constraint carries an authored message (e.g. "a channel
            # conflict must name two different partners") — surface it as-is;
            # a UNIQUE violation names internal columns, so stay generic.
            if type(exc).__name__ == "CheckViolation":
                # Odoo registers the authored models.Constraint message on
                # ir.model.constraint — use it instead of Postgres' raw text
                # (which names internal tables and constraint ids).
                cname = (getattr(getattr(exc, "diag", None), "constraint_name", "") or "").strip()
                message = False
                if cname:
                    message = (
                        env["ir.model.constraint"]
                        .sudo()
                        .search([("name", "=", cname)], limit=1)
                        .message
                    )
                if message:
                    return {"error": "This record breaks a data rule — %s" % message}
            if type(exc).__name__ == "NotNullViolation":
                # Name the blank required field instead of "NotNullViolation":
                # a header or line field the form left empty (fix_real 12 Nov:
                # a PO with no vendor, a counter sale with no operating unit).
                missing = _not_null_label(env, model, exc)
                if missing:
                    return {"error": "%s is required: fill it in and save again." % missing}
            if "Integrity" in type(exc).__name__ or "constraint" in str(exc).lower():
                return {
                    "error": "This record breaks a data rule — a duplicate or a "
                    "required relation is missing (%s)" % type(exc).__name__
                }
            _logger.exception("p03 model_write failed for %s", model)
            return {"error": "The save could not be completed: %s" % exc}

    @staticmethod
    def _datetimes_to_utc(env, model, vals):
        """The form shows and posts the user's wall clock; the database holds UTC.
        A ping typed as 10:00 in Dhaka was stored six hours ahead."""
        spec = env[model]._fields
        for key, value in vals.items():
            if getattr(spec.get(key), "type", "") == "datetime":
                vals[key] = _datetime_to_utc(env, value)

    def _grid_commands(self, env, field, spec):
        """One2many commands for a child grid: {rows:[{id?, values}], removed}.
        An unchanged echo of an existing row is not rewritten."""
        commands = [(2, int(i)) for i in (spec.get("removed") or [])]
        children = env[field.comodel_name]
        for row in spec.get("rows") or []:
            row_vals = self._coerce_vals(row.get("values"))
            # a stored file comes back as its link: it is kept, not rewritten
            row_vals = {
                k: v for k, v in row_vals.items() if not (isinstance(v, dict) and v.get("stored"))
            }
            self._datetimes_to_utc(env, field.comodel_name, row_vals)
            if not row_vals:
                continue
            if row.get("id"):
                child = children.browse(int(row["id"])).exists()
                row_vals = {
                    k: v
                    for k, v in row_vals.items()
                    if k not in children._fields
                    or not child
                    or _child_value_changed(child, children._fields[k], v)
                }
                if row_vals:
                    commands.append((1, int(row["id"]), row_vals))
            else:
                commands.append((0, 0, row_vals))
        return commands

    @staticmethod
    def _coerce_vals(values):
        vals = {}
        for key, value in (values or {}).items():
            # many2one arrives as {id,label} or a bare id
            if isinstance(value, dict) and "id" in value:
                vals[key] = value["id"] or False
            elif (
                isinstance(value, str)
                and len(value) >= 16
                and value[4:5] == "-"
                and value[10:11] == "T"
            ):
                # <input type="datetime-local"> sends 2026-10-27T12:00; the
                # ORM's datetime converter rejects the T separator (surfaces
                # as a generic save failure). Normalise to Odoo's format.
                iso = value.replace("T", " ", 1)
                if len(iso) == 16:
                    iso += ":00"
                vals[key] = iso
            elif isinstance(value, str) and value.startswith("data:"):
                vals[key] = value.split(",", 1)[1] if "," in value else value
            else:
                vals[key] = value
        return vals

    @http.route("/p03/model/action", type="jsonrpc", auth="user")
    def model_action(self, model=None, ids=None, method=None, kwargs=None, **kw):
        _require_internal(request.env)
        env = request.env
        allowed = SURFACES.get(model, {}).get("actions", set())
        if method not in allowed:
            return {"success": False, "error": "Action not available for this surface"}
        refused = _gate(env, "approve", model=model)
        if refused:
            return {"success": False, "error": refused}
        try:
            with env.cr.savepoint():
                records = env[model].browse([int(i) for i in (ids or [])]).exists()
                if not records:
                    return {"success": False, "error": "Record not found"}
                # a form's evidence upload (Record Courier POD) reaches the
                # method as the id of the caller's new attachment, linked to
                # the record the method acts on
                kwargs = dict(kwargs or {})
                uploads = env["ir.attachment"]
                for key, value in list(kwargs.items()):
                    if _is_upload(value):
                        attachment = _store_upload(env, value)
                        uploads |= attachment
                        kwargs[key] = attachment.id
                if len(records) == 1:
                    _link_uploads(uploads, model, records.id)
                result = getattr(records, method)(**kwargs)
                payload = result if isinstance(result, dict) else {}
                return {"success": True, "result": payload}
        except (UserError, AccessError) as exc:
            return {"success": False, "error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_action %s.%s failed", model, method)
            return {"success": False, "error": _FAILED}
