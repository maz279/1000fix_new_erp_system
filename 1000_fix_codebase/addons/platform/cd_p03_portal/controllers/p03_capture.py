# P03 capture controller — the workspace "Data-Entry Forms" and the
# per-sub-module capture buttons write REAL records through here.
#
# Layer rule (AR-007): P03 is a platform module and must not depend on any
# domain module. A domain model opts in by declaring a class attribute
#
#     _p03_capture = {"module": "M42", "form": "Supplier Profile",
#                     "fields": ["partner_id", "classification", ...]}
#
# and this controller discovers it through the ORM registry at request
# time. A form with no registered model reports `available: False` — the
# workspace then says so honestly instead of opening an unrelated form.
#
# Security: every read and write runs as the requesting user (no sudo), so
# model ACLs, record rules and the model's own constraints/SoD checks apply.
# Only fields named in the model's spec are accepted (no mass assignment).
import logging

import psycopg2

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.fields import Command
from odoo.http import request

logger = logging.getLogger(__name__)

# The field types the P03 capture modal can render.
CAPTURE_TYPES = {"char", "text", "html", "selection", "boolean", "integer",
                 "float", "monetary", "date", "datetime", "many2one", "many2many"}
RELATIONAL = {"many2one", "many2many"}
OPTION_LIMIT = 40
FIELD_ATTRS = ["string", "type", "required", "readonly", "selection",
               "relation", "help"]


def capture_registry(env):
    """{(module, form): (model_name, spec)} for every model that declares
    its own `_p03_capture` (an attribute inherited by an unrelated model
    is ignored)."""
    found = {}
    for name in env.registry:
        cls = env.registry[name]
        for klass in cls.__mro__:
            spec = vars(klass).get("_p03_capture")
            if spec and getattr(klass, "_name", None) == name:
                key = (spec.get("module"), spec.get("form"))
                if all(key) and isinstance(spec.get("fields"), (list, tuple)):
                    found[key] = (name, spec)
                break
    return found


def _bengali_lang(env):
    """The installed Bengali locale, as the ORM's language cache sees it
    (the same list `with_context(lang=...)` validates against)."""
    installed = {code for code, _name in env["res.lang"].get_installed()}
    for code in ("bn_BD", "bn_IN"):
        if code in installed:
            return code
    return None


def _coerce(ftype, value):
    """Turn a JSON form value into an ORM write value (None = leave unset)."""
    if value in (None, ""):
        return False if ftype in ("many2one", "date", "datetime", "selection") else None
    if ftype == "boolean":
        return bool(value)
    if ftype == "integer":
        return int(value)
    if ftype in ("float", "monetary"):
        return float(value)
    if ftype == "many2one":
        return int(value)
    if ftype == "many2many":
        ids = [int(v) for v in (value if isinstance(value, (list, tuple)) else [value])]
        return [Command.set(ids)]
    return value


class P03CaptureController(http.Controller):

    def _resolve(self, module, form):
        hit = capture_registry(request.env).get((module, form))
        if not hit:
            return None, None, None
        model_name, spec = hit
        model = request.env[model_name]
        return model_name, spec, model

    @http.route("/p03/capture/forms", type="jsonrpc", auth="user", readonly=True)
    def list_forms(self, module=None):
        """Which workspace forms have a backing model, and whether this user
        may create there — the workspace marks the rest as not yet wired."""
        out = []
        for (mod, form), (model_name, _spec) in sorted(capture_registry(request.env).items()):
            if module and mod != module:
                continue
            out.append({
                "module": mod, "form": form, "model": model_name,
                "can_create": request.env[model_name].has_access("create"),
            })
        return {"forms": out}

    @http.route("/p03/capture/schema", type="jsonrpc", auth="user", readonly=True)
    def schema(self, module=None, form=None):
        model_name, spec, model = self._resolve(module, form)
        if not model_name:
            return {"available": False, "module": module, "form": form}
        if not model.has_access("create"):
            return {"available": True, "can_create": False, "module": module,
                    "form": form, "model": model_name, "fields": []}
        names = [f for f in spec["fields"] if f in model._fields]
        meta_en = model.with_context(lang="en_US").fields_get(names, FIELD_ATTRS)
        bn_code = _bengali_lang(request.env)
        try:
            meta_bn = (model.with_context(lang=bn_code).fields_get(names, ["string", "selection"])
                       if bn_code else {})
            title_bn = model.with_context(lang=bn_code)._description if bn_code else None
        except UserError:  # a translation problem never blocks capture
            meta_bn, title_bn = {}, None
        defaults = model.default_get(names)
        fields_out = []
        for name in names:
            m = meta_en.get(name)
            if not m or m["type"] not in CAPTURE_TYPES or m.get("readonly"):
                continue
            bn = meta_bn.get(name, {})
            fields_out.append({
                "name": name,
                "type": m["type"],
                "string": m["string"],
                "string_bn": bn.get("string") or m["string"],
                "required": bool(m.get("required")),
                "help": m.get("help") or "",
                "relation": m.get("relation") or "",
                "selection": m.get("selection") or [],
                "selection_bn": bn.get("selection") or m.get("selection") or [],
            })
        # many2one defaults come back as ids; many2many as id lists
        return {
            "available": True, "can_create": True, "module": module, "form": form,
            "model": model_name, "title": model._description,
            "title_bn": title_bn or model._description,
            "fields": fields_out,
            "defaults": {k: v for k, v in defaults.items() if k in names},
        }

    @http.route("/p03/capture/options", type="jsonrpc", auth="user", readonly=True)
    def options(self, module=None, form=None, field=None, q=""):
        """Choices for a relational field, searched as the user."""
        model_name, spec, model = self._resolve(module, form)
        if not model_name or field not in spec["fields"] or field not in model._fields:
            return {"options": []}
        fdef = model._fields[field]
        if fdef.type not in RELATIONAL:
            return {"options": []}
        comodel = request.env[fdef.comodel_name]
        if not comodel.has_access("read"):
            return {"options": []}
        domain = fdef.domain(model) if callable(fdef.domain) else fdef.domain
        if not isinstance(domain, list):
            domain = []  # string domains need a record context; search unfiltered
        try:
            pairs = comodel.name_search(q or "", domain, limit=OPTION_LIMIT)
        except Exception:  # an unevaluable dynamic domain: search without it
            pairs = comodel.name_search(q or "", [], limit=OPTION_LIMIT)
        return {"options": [{"id": rid, "name": rname} for rid, rname in pairs]}

    @http.route("/p03/capture/submit", type="jsonrpc", auth="user")
    def submit(self, module=None, form=None, values=None):
        """Create the record as the user. AS-09: missing required inputs come
        back as a structured error; nothing is defaulted on the user's behalf
        beyond the model's own defaults."""
        model_name, spec, model = self._resolve(module, form)
        if not model_name:
            return {"success": False,
                    "error": f"No backend model is registered for {module} · {form} yet."}
        values = values or {}
        unknown = set(values) - set(spec["fields"])
        if unknown:
            return {"success": False,
                    "error": f"Fields not accepted by this form: {', '.join(sorted(unknown))}"}
        vals, missing = {}, []
        for name in spec["fields"]:
            fdef = model._fields.get(name)
            if not fdef or fdef.readonly or fdef.type not in CAPTURE_TYPES:
                continue
            try:
                coerced = _coerce(fdef.type, values.get(name))
            except (TypeError, ValueError):
                return {"success": False, "error": f"{fdef.string}: invalid value"}
            if coerced is None or (coerced is False and fdef.type != "boolean"):
                if fdef.required and not model.default_get([name]).get(name):
                    missing.append(fdef.string)
                continue
            vals[name] = coerced
        if missing:
            return {"success": False, "missing": missing,
                    "error": "Required: " + ", ".join(missing)}
        try:
            with request.env.cr.savepoint():
                record = model.create(vals)
                record.flush_recordset()
        except (ValidationError, UserError, AccessError) as exc:
            return {"success": False, "error": str(exc.args[0] if exc.args else exc)}
        except psycopg2.IntegrityError as exc:
            # The model's declared constraint message (e.g. "one profile per
            # party per legal entity"), as Odoo's own RPC layer reports it.
            return {"success": False, "error": model._sql_error_to_message(exc)}
        except Exception:
            logger.exception("P03 capture failed for %s / %s", module, form)
            return {"success": False,
                    "error": "The record could not be saved; the error was logged."}
        return {"success": True, "model": model_name, "id": record.id,
                "display_name": record.display_name}
