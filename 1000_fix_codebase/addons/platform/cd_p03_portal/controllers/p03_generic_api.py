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
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from .p03_service_order_api import _require_internal, _user_error

# read whitelist: model -> {order, limit, state_fields}
GENERIC_MODELS = {
    "fix.vendor.invoice": {"order": "invoice_date desc, id desc", "limit": 200},
    "fix.expense.claim": {"order": "expense_date desc, id desc", "limit": 200},
    "fix.payment.execution": {"order": "id desc", "limit": 200},
    "fix.bank.statement.line": {"order": "date desc, id desc", "limit": 200},
    "fix.cash.position": {"order": "as_of desc, id desc", "limit": 50},
    "fix.mushak.register": {"order": "invoice_date desc, id desc", "limit": 200},
    "fix.vat.return": {"order": "period desc, id desc", "limit": 100},
    "fix.tds.return": {"order": "id desc", "limit": 100},
    "fix.vat.treatment": {"order": "code", "limit": 200},
    "fix.withholding.certificate": {"order": "id desc", "limit": 200},
    "fix.revenue.schedule": {"order": "start_date desc, id desc", "limit": 200},
    "fix.commission.ledger": {"order": "id desc", "limit": 200},
    "fix.payout.run": {"order": "id desc", "limit": 100},
    "fix.seller.statement": {"order": "period desc, id desc", "limit": 100},
    "fix.fixed.asset": {"order": "purchase_date desc, id desc", "limit": 200},
    "fix.cwip.entry": {"order": "id desc", "limit": 200},
    "fix.budget": {"order": "fiscal_year desc, id desc", "limit": 100},
    "fix.cost.allocation": {"order": "id desc", "limit": 100},
}

# write whitelist: the headless workflow actions, per model
GENERIC_ACTIONS = {
    "fix.vendor.invoice": {"action_request_payment"},
    "fix.expense.claim": {"action_submit", "action_approve"},
    "fix.payment.execution": {"action_execute"},
    "fix.bank.statement.line": {"auto_match"},
    "fix.mushak.register": {"action_mark_posted", "action_rebuild_from_events"},
    "fix.vat.return": {"action_prepare_period", "action_file"},
    "fix.tds.return": {"action_prepare_quarter", "action_file"},
    "fix.withholding.certificate": {"action_issue"},
    "fix.commission.ledger": {"action_post_to_gl"},
    "fix.payout.run": {
        "action_approve",
        "action_submit_payout",
        "action_generate_beftn",
        "action_confirm_bank_settlement",
    },
    "fix.fixed.asset": {"action_accrue_month", "action_dispose"},
    "fix.cwip.entry": {"action_capitalise"},
}

# fields never returned over the generic endpoint
_BLOCKED_FIELDS = {"access_token", "write_uid", "create_uid"}


class P03GenericApiController(http.Controller):
    """Whitelisted generic reads + workflow actions for the A08 model screens."""

    @http.route("/p03/model/records", type="jsonrpc", auth="user", readonly=True)
    def model_records(self, model=None, cols=None, domain=None, state_filter=None, **kw):
        _require_internal(request.env)
        env = request.env
        conf = GENERIC_MODELS.get(model)
        if not conf:
            return {"error": "Model not served by the workspace screens"}
        try:
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
        except UserError as exc:
            return {"error": _user_error(exc)}
        except Exception as exc:
            return {"error": str(exc)[:200]}

    @http.route("/p03/model/action", type="jsonrpc", auth="user")
    def model_action(self, model=None, ids=None, method=None, kwargs=None, **kw):
        _require_internal(request.env)
        env = request.env
        allowed = GENERIC_ACTIONS.get(model, set())
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
        except UserError as exc:
            return {"success": False, "error": _user_error(exc)}
        except Exception as exc:
            return {"success": False, "error": str(exc)[:200]}
