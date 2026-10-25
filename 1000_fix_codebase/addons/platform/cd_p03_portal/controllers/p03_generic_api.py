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
import logging

from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request

from .a08 import SURFACES
from .p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)

# fields never returned over the generic endpoint
_BLOCKED_FIELDS = {"access_token", "write_uid", "create_uid"}
_FAILED = "The request could not be completed — try again or contact Finance support."


class P03GenericApiController(http.Controller):
    """Whitelisted generic reads + workflow actions for the A08 model screens."""

    @http.route("/p03/model/records", type="jsonrpc", auth="user", readonly=True)
    def model_records(self, model=None, cols=None, domain=None, state_filter=None, **kw):
        _require_internal(request.env)
        env = request.env
        conf = SURFACES.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        try:
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
            if state_filter:
                state_field = kw.get("state_field")
                if state_field and state_filter not in ("__all", "__all__", "all", ""):
                    search_domain.append((state_field, "=", state_filter))
            # Finance list screens are COMPANY-wide reads (an accountant sees
            # every operating unit's bills — the M19 CoA sudo-read pattern).
            # OU record rules stay enforced for every OTHER surface; writes
            # below keep the calling user's context (SoD/permissions apply).
            rec_model = env[model].sudo()
            if "company_id" in env[model]._fields:
                search_domain.append(("company_id", "in", env.companies.ids))
            records = rec_model.search(search_domain, order=conf["order"], limit=conf["limit"])
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
                        row[c] = {"key": v, "label": labels.get(v, v)}
                    elif meta.get("type") == "datetime" and v:
                        row[c] = str(v)[:16]
                    else:
                        row[c] = v
                rows.append(row)
            return {
                "model": model,
                "rows": rows,
                "count": len(rows),
                "labels": {c: fields_meta[c]["string"] for c in cols if c in fields_meta},
            }
        except (UserError, AccessError) as exc:
            return {"error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_records failed for %s", model)
            return {"error": _FAILED}

    @http.route("/p03/model/action", type="jsonrpc", auth="user")
    def model_action(self, model=None, ids=None, method=None, kwargs=None, **kw):
        _require_internal(request.env)
        env = request.env
        allowed = SURFACES.get(model, {}).get("actions", set())
        if method not in allowed:
            return {"success": False, "error": "Action not available for this surface"}
        try:
            with env.cr.savepoint():
                records = env[model].browse([int(i) for i in (ids or [])]).exists()
                if not records:
                    return {"success": False, "error": "Record not found"}
                result = getattr(records, method)(**(kwargs or {}))
                payload = result if isinstance(result, dict) else {}
                return {"success": True, "result": payload}
        except (UserError, AccessError) as exc:
            return {"success": False, "error": _user_error(exc)}
        except Exception:
            _logger.exception("p03 model_action %s.%s failed", model, method)
            return {"success": False, "error": _FAILED}
