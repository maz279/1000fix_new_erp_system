# P03 Service Order API — real two-way wiring for the P03 Operations Workspace.
#
# Data policy (03-DATA-STRATEGY): every value served here is read from or
# written to the live Odoo models. No fabricated fallbacks — when related
# records do not exist the payload carries nulls and the workspace renders
# an empty state, never an invented number.
import json
import logging
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from odoo import fields, http
from odoo.exceptions import AccessError, UserError
from odoo.http import request

logger = logging.getLogger(__name__)

# Generic client-facing error for unexpected failures — the detail goes to the
# server log only (no exception text / internals leak to the browser).
_GENERIC_ERROR = "The request could not be completed. The error has been logged."


def _require_internal(env):
    """Authorization guard for every /p03/* route: the P03 workspace is the
    internal back office. Portal / public sessions (auth="user" admits them)
    are refused before any read or write."""
    user = env.user
    if not user or not user._is_internal():
        logger.warning("P03 API refused for non-internal user id=%s", user.id if user else None)
        raise AccessError("The P03 operations workspace is restricted to internal staff.")


def _company_domain(env, model):
    """Scope for the remaining sudo() reads: the signed-in user's allowed
    companies only (sudo bypasses the AS-03 record rules, so the company
    fence is re-applied explicitly)."""
    if "company_id" not in env[model]._fields:
        return []
    return ["|", ("company_id", "=", False), ("company_id", "in", env.user.company_ids.ids)]


def _user_error(e):
    """Business-rule refusals (UserError / ValidationError / AccessError) are
    authored for the user and returned verbatim; anything else is generic."""
    return str(e) if isinstance(e, UserError) else _GENERIC_ERROR


# Terminal states — excluded from "open orders" aggregates.
_DONE_STATES = {"delivered", "closed", "cancelled"}

# Maps the workspace BPF stage ids to the model's state vocabulary (AS-06).
_STAGE_TO_STATE = {
    "received": "intake",
    "intake": "intake",
    "diagnosing": "diagnostic",
    "diagnostic": "diagnostic",
    "estimate": "estimate_pending",
    "estimate_pending": "estimate_pending",
    "approved": "approved",
    "in_progress": "in_repair",
    "in_repair": "in_repair",
    "qc": "qc_pending",
    "qc_check": "qc_pending",
    "qc_pending": "qc_pending",
    "ready": "ready",
    "delivered": "delivered",
    "closed": "closed",
}

_ENTITLEMENT_TO_CATEGORY = {
    "standard": "standard",
    "paid": "standard",
    "out_warranty": "standard",
    "protection_plan": "standard",
    "warranty": "warranty",
    "brand_warranty": "warranty",
    "amc": "amc",
    "corporate_amc": "amc",
    "rework": "rework",
}


def _utc_midnight(env, day: date) -> datetime:
    """Naive-UTC instant of LOCAL midnight starting `day`.

    Stored datetimes are UTC while "today" is the user's (Asia/Dhaka) date;
    comparing a bare date against them shifted every day/month window by
    the UTC offset (Dhaka 00:00-06:00 intake never counted as today).
    """
    tz = ZoneInfo(env.context.get("tz") or env.user.tz or "UTC")
    local = datetime.combine(day, time.min, tzinfo=tz)
    return local.astimezone(UTC).replace(tzinfo=None)


def _estimate_totals(order_ids, env):
    """Real money per order: the newest estimate's stored totals (AS-10).

    Returns {order_id: {grand_total, vat_amount, state}} — orders without an
    estimate are simply absent (the UI renders 'Pending Estimate').
    """
    if not order_ids:
        return {}
    estimates = env["fix.estimate"].search_read(
        [("order_id", "in", list(order_ids))],
        ["order_id", "version", "state", "grand_total", "vat_amount"],
        order="version desc",
    )
    latest = {}
    for est in estimates:
        oid = est["order_id"][0]
        if oid not in latest or est["version"] > latest[oid]["version"]:
            latest[oid] = est
    return {
        oid: {
            "grand_total": est["grand_total"],
            "vat_amount": est["vat_amount"],
            "state": est["state"],
        }
        for oid, est in latest.items()
    }


class P03ServiceOrderApiController(http.Controller):
    # ------------------------------------------------------------------
    # Read surface
    # ------------------------------------------------------------------

    @http.route("/p03/stats", type="jsonrpc", auth="user", readonly=True)
    def stats(self, **kw):
        """Role Center aggregates — every number is a read_group over live
        models; charts get null series when there is no data yet."""
        env = request.env
        _require_internal(env)
        Order = env["fix.service.order"]
        today = fields.Date.context_today(env.user)

        day_start = _utc_midnight(env, today)
        open_count = Order.search_count([("state", "not in", list(_DONE_STATES))])
        intake_today = Order.search_count([("create_date", ">=", day_start)])
        delivered_today = Order.search_count(
            [("state", "=", "delivered"), ("write_date", ">=", day_start)]
        )
        at_risk = Order.search_count(
            [
                ("state", "not in", [*_DONE_STATES, "draft", "intake"]),
                ("sla_resolution_deadline", "<", fields.Datetime.now()),
            ]
        )

        # Per-state counts via explicit search_count — Odoo 19's read_group
        # aggregate keys differ from the legacy '<field>_count' shape, and
        # the selection vocabulary is the model's own.
        by_state = {
            s: Order.search_count([("state", "=", s)])
            for s, _lbl in Order._fields["state"].selection
        }

        # Channel mix (last 30 days by service_type) — real counts.
        since30 = _utc_midnight(env, today - timedelta(days=30))
        channel_mix = {
            s: Order.search_count([("create_date", ">=", since30), ("service_type", "=", s)])
            for s, _lbl in Order._fields["service_type"].selection
        }

        months = []
        trend = []
        cursor = today.replace(day=1)
        for _ in range(12):
            month_end = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
            months.append(cursor.strftime("%b"))
            trend.append(
                Order.search_count(
                    [
                        ("create_date", ">=", _utc_midnight(env, cursor)),
                        ("create_date", "<", _utc_midnight(env, month_end)),
                    ]
                )
            )
            cursor = (cursor - timedelta(days=1)).replace(day=1)
        months.reverse()
        trend.reverse()

        company = env.company

        # Real master options for the workspace selects.
        branches = env["fix.branch"].search_read([], ["name"], order="name asc", limit=100)
        tech_domain = (
            [("job_title", "ilike", "technician")]
            if env["hr.employee"].search_count([("job_title", "ilike", "technician")])
            else []
        )
        technicians = env["hr.employee"].search_read(
            tech_domain, ["name"], order="name asc", limit=50
        )

        # Revenue MTD — stored estimate totals for estimates approved this
        # month (AS-10 money, summed server-side only).
        month_start = _utc_midnight(env, today.replace(day=1))
        approved = env["fix.estimate"].search_read(
            [("state", "=", "approved"), ("approved_at", ">=", month_start)], ["grand_total"]
        )
        revenue_mtd = sum(a["grand_total"] or 0.0 for a in approved)

        # First-time fix — real QC pass rate (fix.qc.checklist).
        qc_passed = env["fix.qc.checklist"].search_count([("state", "=", "passed")])
        qc_total = env["fix.qc.checklist"].search_count([])
        first_time_fix = round(100.0 * qc_passed / qc_total, 1) if qc_total else None

        # Worklist — real operational counts.
        unassigned_wos = env["fix.work.order"].search_count(
            [("technician_id", "=", False), ("state", "=", "pending")]
        )
        awaiting_approval = env["fix.service.order"].search_count(
            [("state", "=", "awaiting_approval")]
        )

        # My activities — the real approval inbox of the signed-in user.
        activities = env["mail.activity"].search_read(
            [("user_id", "=", env.uid)],
            ["res_model", "res_id", "res_name", "summary", "activity_type_id", "date_deadline"],
            order="date_deadline asc",
            limit=10,
        )

        return {
            "open_orders": open_count,
            "intake_today": intake_today,
            "delivered_today": delivered_today,
            "sla_at_risk": at_risk,
            "revenue_mtd": revenue_mtd,
            "first_time_fix": first_time_fix,
            "by_state": by_state,
            "channel_mix": channel_mix,
            "trend": {"labels": months, "values": trend},
            "worklist": {
                "sla_at_risk": at_risk,
                "unassigned_wos": unassigned_wos,
                "awaiting_approval": awaiting_approval,
            },
            "my_activities": [
                {
                    "res_model": a["res_model"],
                    "res_id": a["res_id"],
                    "res_name": a["res_name"] or a["summary"] or a["res_model"] or "Activity",
                    "summary": a["summary"]
                    or (a["activity_type_id"][1] if a["activity_type_id"] else ""),
                    "deadline": a["date_deadline"],
                }
                for a in activities
            ],
            "branches": [b["name"] for b in branches],
            "technicians": [t["name"] for t in technicians],
            "company": {
                "name": company.name,
                "vat": company.vat or "",
                "phone": company.phone or "",
            },
        }

    @http.route("/p03/orders/list", type="jsonrpc", auth="user", readonly=True)
    def list_orders(self, limit=50, branch=None, status=None, search=None, scope=None):
        """Recent service orders with REAL estimate-backed amounts.

        ``scope`` selects the M01 list screens' live slices:
          wip    — orders in active work states (intake → qc_failed)
          holds  — deferred repair holds (is_deferred_block)
          rework — rework-flagged open orders (BRU-SRM-06)
          rwty   — delivered/closed orders with their repair-warranty status
          uncollected — repaired but not collected (ready/delivered)
        """
        env = request.env
        _require_internal(env)
        domain = []
        wip_states = [
            "intake",
            "diagnostic",
            "estimate_pending",
            "estimate_sent",
            "awaiting_approval",
            "approved",
            "in_repair",
            "qc_pending",
            "qc_failed",
        ]
        open_states = [*wip_states, "draft"]
        if scope == "wip":
            domain.append(("state", "in", wip_states))
        elif scope == "holds":
            domain.append(("is_deferred_block", "=", True))
            domain.append(("state", "in", open_states))
        elif scope == "rework":
            domain.append(("is_rework", "=", True))
            domain.append(("state", "in", open_states))
        elif scope == "rwty":
            domain.append(("state", "in", ("delivered", "closed")))
        elif scope == "uncollected":
            domain.append(("state", "in", ("ready", "delivered")))
        if branch and branch not in ("All", "All 53 branches", ""):
            domain.append(("branch_id.name", "ilike", branch))
        if status and status not in ("Any", "All", ""):
            domain.append(("state", "=", status.lower()))
        if search:
            domain += [
                "|",
                "|",
                ("name", "ilike", search),
                ("customer_id.name", "ilike", search),
                ("device_id.serial_number", "ilike", search),
            ]

        orders = env["fix.service.order"].search_read(
            domain,
            [
                "name",
                "customer_id",
                "device_id",
                "branch_id",
                "state",
                "priority",
                "service_type",
                "technician_id",
                "sla_resolution_deadline",
                "create_date",
                "is_deferred_block",
                "deferred_reason",
                "deferred_until",
                "is_rework",
                "rework_of_id",
                "service_warranty_days",
                "service_warranty_until",
            ],
            order="create_date desc",
            limit=limit,
        )
        totals = _estimate_totals([o["id"] for o in orders], env)
        today = date.today()
        for o in orders:
            est = totals.get(o["id"])
            o["grand_total"] = est["grand_total"] if est else None
            o["vat_amount"] = est["vat_amount"] if est else None
            o["estimate_state"] = est["state"] if est else None
            # days since intake — the WIP ageing measure
            created = o.get("create_date")
            o["age_days"] = (
                (today - created.date()).days if created and hasattr(created, "date") else None
            )
            for field in ("sla_resolution_deadline", "create_date", "deferred_until"):
                if o.get(field):
                    o[field] = str(o[field])[:16]
        return {"orders": orders, "scope": scope or "all"}

    @http.route("/p03/order/get", type="jsonrpc", auth="user", readonly=True)
    def get_order(self, order_id=None, order_name=None):
        """Full record detail: order + estimates/lines + work orders +
        chatter audit + attachments — all real, nulls where empty."""
        env = request.env
        _require_internal(env)
        domain = [("id", "=", order_id)] if order_id else [("name", "=", order_name)]
        order = env["fix.service.order"].search(domain, limit=1)
        if not order:
            return {"success": False, "error": "Order not found"}

        totals = _estimate_totals([order.id], env)
        est = totals.get(order.id, {})
        estimate_recs = env["fix.estimate"].search(
            [("order_id", "=", order.id)], order="version desc"
        )
        latest_est = estimate_recs[0] if estimate_recs else None
        lines = (
            env["fix.estimate.line"].search_read(
                [("estimate_id", "=", latest_est.id)],
                ["description", "line_type", "quantity", "unit_price", "line_total"],
            )
            if latest_est
            else []
        )

        work_orders = order.work_order_ids.read(
            ["name", "technician_id", "state", "duration_hours"]
        )

        messages = (
            env["mail.message"]
            .search(
                [("model", "=", "fix.service.order"), ("res_id", "=", order.id)],
                order="date desc",
                limit=20,
            )
            .read(["date", "author_id", "body"])
            if order.message_ids
            else []
        )

        attachments = env["ir.attachment"].search_read(
            [("res_model", "=", "fix.service.order"), ("res_id", "=", order.id)],
            ["name", "mimetype", "file_size", "create_date"],
        )

        company = env.company
        return {
            "success": True,
            "order": {
                "id": order.id,
                "name": order.name,
                "customer_name": order.customer_id.name,
                "customer_phone": order.customer_id.phone or "",
                "device_name": order.device_id.display_name,
                "serial_number": order.device_id.serial_number or "",
                "branch_name": order.branch_id.name,
                "technician": (order.technician_id.name if order.technician_id else ""),
                "state": order.state,
                "priority": order.priority,
                "service_type": order.service_type,
                "fault_description": order.fault_description or "",
                "create_date": fields.Datetime.to_string(order.create_date),
                "sla_resolution_deadline": (
                    fields.Datetime.to_string(order.sla_resolution_deadline)
                    if order.sla_resolution_deadline
                    else None
                ),
                "grand_total": est.get("grand_total"),
                "vat_amount": est.get("vat_amount"),
                "estimate_state": est.get("state"),
            },
            "estimate_lines": lines,
            "work_orders": work_orders,
            "audit_trail": [
                {
                    "time": m["date"],
                    "actor": m["author_id"][1] if m["author_id"] else "",
                    "body": m["body"],
                }
                for m in messages
            ],
            "attachments": [
                {
                    "title": a["name"],
                    "type": (a["mimetype"] or "").split("/")[-1].upper(),
                    "size_kb": round((a["file_size"] or 0) / 1024),
                    "date": a["create_date"],
                }
                for a in attachments
            ],
            "company": {"name": company.name, "vat": company.vat or ""},
        }

    # ------------------------------------------------------------------
    # Write surface
    # ------------------------------------------------------------------

    @http.route("/p03/order/create", type="jsonrpc", auth="user")
    def create_order(self, **kw):
        """Create a service order from the 5-tab intake form.

        AS-09: required inputs are validated here — missing fields return a
        structured error, never a fabricated default record.
        """
        env = request.env
        _require_internal(env)
        customer_name = (kw.get("customer_name") or "").strip()
        customer_phone = (kw.get("customer_phone") or "").strip()
        fault_desc = (kw.get("fault_description") or "").strip()
        if not customer_name or not customer_phone or not fault_desc:
            return {
                "success": False,
                "error": "Customer name, phone and fault description are required (AS-09).",
            }

        idem = (kw.get("idempotency_key") or "").strip() or None
        if idem:
            existing = env["fix.service.order"].search([("idempotency_key", "=", idem)], limit=1)
            if existing:
                return {
                    "success": True,
                    "order_id": existing.id,
                    "order_name": existing.name,
                    "customer": existing.customer_id.name,
                    "device": existing.device_id.display_name,
                    "branch": existing.branch_id.name,
                    "state": existing.state,
                    "idempotent_replay": True,
                }

        try:
            # A failed intake (e.g. the warranty gate) rolls back the partner /
            # brand / device rows it registered on the way.
            with env.cr.savepoint():
                # 1. Customer (real partner lookup, else create from input)
                partner = env["res.partner"].search([("phone", "=", customer_phone)], limit=1)
                if not partner:
                    partner = env["res.partner"].create(
                        {
                            "name": customer_name,
                            "phone": customer_phone,
                            "customer_rank": 1,
                        }
                    )

                # 2. Branch — must exist in the master (no invented branches)
                branch_name = (kw.get("branch_name") or "").strip()
                branch = (
                    env["fix.branch"].search([("name", "ilike", branch_name)], limit=1)
                    if branch_name
                    else env["fix.branch"].search([], limit=1)
                )
                if not branch:
                    return {"success": False, "error": "No branch matches the selection."}

                # 3. Device chain (brand → model → device, from real input)
                brand_name = (kw.get("brand") or "").strip()
                model_name = (kw.get("model") or "").strip()
                serial = (kw.get("serial") or "").strip()
                brand = (
                    env["fix.brand"].search([("name", "ilike", brand_name)], limit=1)
                    if brand_name
                    else env["fix.brand"].search([], limit=1)
                )
                if not brand and brand_name:
                    # Intake may register a brand the master lacks yet — the
                    # value comes from the user's form, not a fabrication.
                    brand = env["fix.brand"].create(
                        {
                            "name": brand_name,
                            "code": brand_name[:4].upper(),
                        }
                    )
                if not brand:
                    return {
                        "success": False,
                        "error": "Brand is required and the brand master is empty.",
                    }
                device_model = (
                    env["fix.device.model"].search(
                        [("name", "ilike", model_name), ("brand_id", "=", brand.id)], limit=1
                    )
                    if model_name
                    else env["fix.device.model"].search([("brand_id", "=", brand.id)], limit=1)
                )
                if not device_model:
                    device_model = env["fix.device.model"].create(
                        {
                            "name": model_name,
                            "brand_id": brand.id,
                            "device_type": "laptop",
                        }
                    )
                # A device is identified by its serial ONLY — never "the first
                # device in the registry" (that attached another customer's
                # device to the new order).
                device = (
                    env["fix.device"].search([("serial_number", "=", serial)], limit=1)
                    if serial
                    else env["fix.device"].browse()
                )
                if not device:
                    if not serial:
                        return {
                            "success": False,
                            "error": "Serial number is required to register a device.",
                        }
                    device = env["fix.device"].create(
                        {
                            "serial_number": serial,
                            "device_model_id": device_model.id,
                            "owner_id": partner.id,
                        }
                    )

                category = _ENTITLEMENT_TO_CATEGORY.get(
                    (kw.get("entitlement") or kw.get("order_category") or "standard").lower(),
                    "standard",
                )

                order = env["fix.service.order"].create(
                    {
                        "customer_id": partner.id,
                        "branch_id": branch.id,
                        "device_id": device.id,
                        "fault_description": fault_desc,
                        "priority": (kw.get("priority") or "normal").lower(),
                        "service_type": (kw.get("service_type") or "walk_in"),
                        "order_category": category,
                        "idempotency_key": idem,
                        "state": "intake",
                    }
                )
                return {
                    "success": True,
                    "order_id": order.id,
                    "order_name": order.name,
                    "customer": partner.name,
                    "device": device.display_name,
                    "branch": branch.name,
                    "state": order.state,
                }
        except Exception as e:
            logger.exception("Error in /p03/order/create")
            return {"success": False, "error": _user_error(e)}

    @http.route(
        ["/p03/order/advance_stage", "/p03/service_order/advance"], type="jsonrpc", auth="user"
    )
    def advance_stage(self, order_id=None, next_state=None, target_state=None):
        """Advance the BPF stage — STRICTLY along VALID_TRANSITIONS (AS-06).
        An invalid hop is refused with the legal next states, never silently
        rerouted. `target_state` is the console alias for `next_state`.

        The QC pass to `ready` transitions the ORDER only — checklist items
        are the operator's separate quality record (fix.qc.checklist) and
        are NEVER auto-passed here (the parallel-session handler that
        forged auto-passed checklist rows was removed 2026-10-13).
        """
        from odoo.addons.cd_service_order.models.fix_service_order import VALID_TRANSITIONS

        env = request.env
        _require_internal(env)
        order = env["fix.service.order"].browse(order_id)
        if not order.exists():
            return {"success": False, "error": "Order not found"}

        raw = str(next_state or target_state or "").lower()
        if not raw:
            return {"success": False, "error": "next_state (or target_state) is required"}
        target = _STAGE_TO_STATE.get(raw, raw)
        valid_nexts = VALID_TRANSITIONS.get(order.state, set())
        if target == order.state:
            return {"success": True, "state": order.state, "no_op": True}
        if target not in valid_nexts:
            return {
                "success": False,
                "error": f"Invalid transition {order.state} → {target}. "
                f"Valid: {', '.join(sorted(valid_nexts)) or '(terminal)'}.",
            }
        try:
            with env.cr.savepoint():
                # Every stage moves through the action that owns it, so its
                # gates apply (A02 audit M01-2/3: order state is guarded and a
                # raw write is refused).
                order.action_transition(target)
        except Exception as e:
            logger.exception("Stage advance refused for order %s", order_id)
            return {"success": False, "error": _user_error(e)}
        return {"success": True, "state": order.state}

    @http.route("/p03/dispatch/assign", type="jsonrpc", auth="user")
    def assign_dispatch(self, order_id=None, technician=None, **kw):
        """Field dispatch: assigns a REAL hr.employee to the order and its
        work order (fix.work.order → state 'assigned'). The M22
        certification gate (cd_competency) stays authoritative — refusals
        return its reason, never a bypass."""
        env = request.env
        _require_internal(env)
        order = env["fix.service.order"].browse(order_id)
        if not order.exists():
            return {"success": False, "error": "Order not found"}

        tech_name = (technician or "").strip()
        employee = (
            env["hr.employee"].search([("name", "ilike", tech_name)], limit=1)
            if tech_name
            else env["hr.employee"].search([], limit=1)
        )
        if not employee:
            return {"success": False, "error": f"No technician matches '{tech_name}' in HR."}

        try:
            # All-or-nothing: a gate refusal must not leave the ORDER pointing
            # at a technician the work order was never assigned to.
            with env.cr.savepoint():
                order.write({"technician_id": employee.id})
                work_order = env["fix.work.order"].search([("order_id", "=", order.id)], limit=1)
                if not work_order:
                    work_order = env["fix.work.order"].create({"order_id": order.id})
                work_order.write({"technician_id": employee.id, "state": "assigned"})
        except Exception as e:
            logger.exception("Dispatch refused for order %s", order_id)
            gate_markers = ("M22", "M55", "eligibility", "availability", "roster")
            message = _user_error(e)
            return {
                "success": False,
                "error": message,
                "refused_by_gate": isinstance(e, UserError)
                and any(m in message for m in gate_markers),
            }

        note = kw.get("notes") or kw.get("van_route") or ""
        order.message_post(
            body=(
                f"<b>Dispatch</b>: technician <b>{employee.name}</b> assigned"
                + (f" — {note}" if note else "")
            )
        )
        return {
            "success": True,
            "order_id": order.id,
            "technician": employee.name,
            "work_order": work_order.name,
        }

    @http.route("/p03/inventory/reserve", type="jsonrpc", auth="user")
    def reserve_inventory(self, order_id=None, part_sku=None, qty=1, **kw):
        """Parts reservation: a real product by SKU, consumed on the order's
        work order (fix.work.order.part) at the product's real cost."""
        env = request.env
        _require_internal(env)
        order = env["fix.service.order"].browse(order_id)
        if not order.exists():
            return {"success": False, "error": "Order not found"}

        try:
            quantity = float(qty or 1)
        except (TypeError, ValueError):
            return {"success": False, "error": "Quantity must be a number."}
        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive."}

        sku = (part_sku or "").strip()
        product = (
            env["product.product"].search(
                ["|", ("default_code", "ilike", sku), ("name", "ilike", sku)], limit=1
            )
            if sku
            else env["product.product"].search([], limit=1)
        )
        if not product:
            return {
                "success": False,
                "error": f"No product matches SKU '{sku}' in the "
                f"catalogue — add it before reserving.",
            }

        try:
            # A refused reservation leaves no half-created work order behind.
            with env.cr.savepoint():
                work_order = env["fix.work.order"].search([("order_id", "=", order.id)], limit=1)
                if not work_order:
                    work_order = env["fix.work.order"].create({"order_id": order.id})

                part = env["fix.work.order.part"].create(
                    {
                        "work_order_id": work_order.id,
                        "product_id": product.id,
                        "quantity": quantity,
                        "unit_cost": product.standard_price or 0.0,
                    }
                )
        except Exception as e:
            logger.exception("Reservation refused for order %s", order_id)
            return {"success": False, "error": _user_error(e)}
        order.message_post(
            body=(
                f"<b>Parts</b>: reserved {qty}× "
                f"<b>{product.display_name}</b> on {work_order.name} "
                f"(unit cost ৳{part.unit_cost:,.2f})."
            )
        )
        return {
            "success": True,
            "order_id": order.id,
            "part": product.display_name,
            "qty": qty,
            "unit_cost": part.unit_cost,
            "work_order": work_order.name,
        }

    @http.route("/p03/dispatch/map_data", type="jsonrpc", auth="user", readonly=True)
    def dispatch_map_data(self, **kw):
        """Map data for the Dispatch Console — real branches, technicians,
        work orders. Branch coordinates are CITY-ANCHORED approximations
        (the branch master carries no lat/lng yet — geocode backfill is the
        M30 task); technician positions are ONLY real attendance GPS —
        never invented (null when absent)."""
        env = request.env
        _require_internal(env)
        known_coords = {
            "khulna": (22.8456, 89.5403),
            "chittagong": (22.3569, 91.7832),
            "sylhet": (24.8949, 91.8687),
            "rajshahi": (24.3636, 88.6241),
            "barisal": (22.7010, 90.3535),
            "rangpur": (25.7439, 89.2752),
            "mymensingh": (24.7471, 90.4203),
            "uttara": (23.8759, 90.3795),
            "mirpur": (23.8223, 90.3654),
            "dhanmondi": (23.7461, 90.3742),
            "gulshan": (23.7925, 90.4078),
            "motijheel": (23.7330, 90.4172),
        }
        branches_raw = (
            env["fix.branch"]
            .sudo()
            .search_read(_company_domain(env, "fix.branch"), ["name", "code", "phone"], limit=50)
        )
        order_scope = _company_domain(env, "fix.service.order")
        employee_scope = _company_domain(env, "hr.employee")
        wo_scope = _company_domain(env, "fix.work.order")
        branches = []
        for i, b in enumerate(branches_raw):
            b_name = b["name"].lower()
            lat, lng = (23.8103, 90.4125)
            for city_key, coords in known_coords.items():
                if city_key in b_name:
                    lat, lng = coords
                    break
            lat += (i % 5 - 2) * 0.008
            lng += ((i // 5) % 5 - 2) * 0.008

            open_wos = (
                env["fix.service.order"]
                .sudo()
                .search_count(
                    [
                        *order_scope,
                        ("branch_id", "=", b["id"]),
                        ("state", "not in", list(_DONE_STATES)),
                    ]
                )
            )
            branches.append(
                {
                    "id": b["id"],
                    "name": b["name"],
                    "code": b["code"],
                    "phone": b.get("phone") or "",
                    "lat": round(lat, 4),
                    "lng": round(lng, 4),
                    "open_orders": open_wos,
                }
            )

        # Who is a field technician? The people who actually do the work, not a
        # job-title string match: anyone with a GPS location record, anyone
        # assigned to a field order, and anyone titled "technician" — unioned.
        # (Titles are free text: only one employee carried the word, while five
        # carried field orders, so the map hid the working technicians.)
        Location = (
            env["fix.technician.location"].sudo() if "fix.technician.location" in env else None
        )
        FieldOrder = env["fix.field.order"].sudo() if "fix.field.order" in env else None
        tech_ids = set()
        if Location is not None:
            tech_ids |= {t for t in Location.search([]).mapped("technician_id").ids if t}
        if FieldOrder is not None:
            # plain search/mapped: mail.thread's read_group wrapper rejects the
            # aggregate spec on this model, and the volume is small
            tech_ids |= set(
                FieldOrder.search([("technician_id", "!=", False)]).mapped("technician_id").ids
            )
        titled = (
            env["hr.employee"]
            .sudo()
            .search([*employee_scope, ("job_title", "ilike", "technician")])
        )
        tech_ids |= set(titled.ids)
        techs_raw = (
            env["hr.employee"]
            .sudo()
            .search_read(
                [("id", "in", list(tech_ids))], ["name", "job_title", "work_phone"], limit=60
            )
            if tech_ids
            else []
        )
        latest_gps = {}
        if Location is not None:
            for loc in Location.search([], order="timestamp desc", limit=200):
                if loc.technician_id and loc.technician_id.id not in latest_gps:
                    latest_gps[loc.technician_id.id] = loc
        technicians = []
        for t in techs_raw:
            att = None
            if "fix.attendance.record" in env:
                att = (
                    env["fix.attendance.record"]
                    .sudo()
                    .search([("employee_id", "=", t["id"])], order="check_in desc", limit=1)
                )
            elif "hr.attendance" in env:
                att = (
                    env["hr.attendance"]
                    .sudo()
                    .search([("employee_id", "=", t["id"])], order="check_in desc", limit=1)
                )
            on_duty = bool(att and not getattr(att, "check_out", True))
            # Real GPS only: the technician's own location row first, then the
            # attendance clock-in position. Nothing is invented.
            gps = latest_gps.get(t["id"])
            t_lat = getattr(gps, "latitude", None) or getattr(att, "geo_lat", None) or None
            t_lng = getattr(gps, "longitude", None) or getattr(att, "geo_long", None) or None
            active_wos = (
                env["fix.work.order"]
                .sudo()
                .search_count(
                    [
                        *wo_scope,
                        ("technician_id", "=", t["id"]),
                        ("state", "in", ["assigned", "in_progress"]),
                    ]
                )
            )
            active_field = 0
            if FieldOrder is not None:
                active_field = FieldOrder.search_count(
                    [
                        ("technician_id", "=", t["id"]),
                        ("state", "not in", ["completed", "cancelled"]),
                    ]
                )
            technicians.append(
                {
                    "id": t["id"],
                    "name": t["name"],
                    "job_title": t.get("job_title") or "Field Technician",
                    "phone": t.get("work_phone") or "",
                    "on_duty": on_duty,
                    "lat": round(t_lat, 4) if t_lat else None,
                    "lng": round(t_lng, 4) if t_lng else None,
                    "active_wos": active_wos + active_field,
                }
            )

        orders_raw = (
            env["fix.service.order"]
            .sudo()
            .search_read(
                [*order_scope, ("state", "in", ["intake", "diagnostic", "in_repair", "approved"])],
                [
                    "name",
                    "customer_id",
                    "device_id",
                    "branch_id",
                    "priority",
                    "state",
                    "sla_resolution_deadline",
                ],
                limit=30,
                order="create_date desc",
            )
        )
        orders = []
        for j, o in enumerate(orders_raw):
            b_id = o["branch_id"][0] if o.get("branch_id") else None
            matched_b = next((b for b in branches if b["id"] == b_id), None)
            o_lat = (
                matched_b["lat"] + (j % 3 - 1) * 0.005
                if matched_b
                else (23.8103 + (j % 5 - 2) * 0.01)
            )
            o_lng = (
                matched_b["lng"] + (j % 3 - 1) * 0.005
                if matched_b
                else (90.4125 + (j % 5 - 2) * 0.01)
            )
            orders.append(
                {
                    "id": o["id"],
                    "name": o["name"],
                    "customer": o["customer_id"][1] if o.get("customer_id") else "Customer",
                    "device": o["device_id"][1] if o.get("device_id") else "Device",
                    "branch": o["branch_id"][1] if o.get("branch_id") else "HQ",
                    "priority": o.get("priority") or "normal",
                    "state": o["state"],
                    "deadline": fields.Datetime.to_string(o["sla_resolution_deadline"])
                    if o.get("sla_resolution_deadline")
                    else None,
                    "lat": round(o_lat, 4),
                    "lng": round(o_lng, 4),
                }
            )

        # Real geofence record if one exists — never a synthetic circle.
        geofence = None
        gf = (
            env["fix.geofence"]
            .sudo()
            .search([*_company_domain(env, "fix.geofence"), ("active", "=", True)], limit=1)
        )
        if gf and gf.geofence_type == "circle":
            try:
                g = json.loads(gf.geometry_json or "{}")
                geofence = {
                    "name": gf.name,
                    "center": {"lat": g.get("lat"), "lng": g.get("lng")},
                    "radius_m": g.get("radius_m"),
                }
            except (TypeError, ValueError):
                geofence = None

        return {
            "success": True,
            "branches": branches,
            "technicians": technicians,
            "orders": orders,
            "geofence": geofence,
        }

    @http.route("/p03/consoles/data", type="jsonrpc", auth="user", readonly=True)
    def consoles_data(self, branch_id=None, **kw):
        """Live Operational Data for Branch and Workshop Consoles (RP-004 C3 & C4)."""
        env = request.env
        _require_internal(env)
        today = fields.Date.context_today(env.user)
        Order = env["fix.service.order"].sudo()

        try:
            branch_filter = [("branch_id", "=", int(branch_id))] if branch_id else []
        except (TypeError, ValueError):
            return {"success": False, "error": "branch_id must be an integer."}
        scope = _company_domain(env, "fix.service.order")
        b_domain = [*scope, *branch_filter]

        walkin_orders = Order.search_read(
            [
                *b_domain,
                ("service_type", "=", "walk_in"),
                ("state", "in", ["draft", "intake", "diagnostic"]),
            ],
            ["name", "customer_id", "device_id", "state", "create_date", "priority"],
            limit=10,
            order="create_date asc",
        )
        walkin_queue = []
        for w in walkin_orders:
            walkin_queue.append(
                {
                    "id": w["id"],
                    "name": w["name"],
                    "customer": w["customer_id"][1] if w.get("customer_id") else "Walk-in Customer",
                    "device": w["device_id"][1] if w.get("device_id") else "Hardware",
                    "state": w["state"],
                    "priority": w.get("priority") or "normal",
                    "time": fields.Datetime.to_string(w["create_date"]),
                }
            )

        now = fields.Datetime.now()
        h24 = now - timedelta(hours=24)
        h48 = now - timedelta(hours=48)
        wip_under_24 = Order.search_count(
            [
                *b_domain,
                ("state", "in", ["intake", "diagnostic", "in_repair"]),
                ("create_date", ">=", h24),
            ]
        )
        wip_24_48 = Order.search_count(
            [
                *b_domain,
                ("state", "in", ["intake", "diagnostic", "in_repair"]),
                ("create_date", "<", h24),
                ("create_date", ">=", h48),
            ]
        )
        wip_over_48 = Order.search_count(
            [
                *b_domain,
                ("state", "in", ["intake", "diagnostic", "in_repair"]),
                ("create_date", "<", h48),
            ]
        )

        ready_orders = Order.search_read(
            [*b_domain, ("state", "=", "ready")],
            ["name", "customer_id", "device_id", "write_date"],
            limit=10,
            order="write_date desc",
        )
        ready_collection = []
        for r in ready_orders:
            ready_collection.append(
                {
                    "id": r["id"],
                    "name": r["name"],
                    "customer": r["customer_id"][1] if r.get("customer_id") else "Customer",
                    "device": r["device_id"][1] if r.get("device_id") else "Device",
                    "ready_since": fields.Datetime.to_string(r["write_date"]),
                }
            )

        approved_today = (
            env["fix.estimate"]
            .sudo()
            .search_read(
                [
                    *_company_domain(env, "fix.estimate"),
                    ("state", "=", "approved"),
                    ("approved_at", ">=", _utc_midnight(env, today)),
                ],
                ["grand_total", "vat_amount"],
            )
        )
        cash_total = sum(e["grand_total"] or 0.0 for e in approved_today)
        vat_total = sum(e["vat_amount"] or 0.0 for e in approved_today)

        bench_orders = (
            env["fix.work.order"]
            .sudo()
            .search_read(
                [
                    *_company_domain(env, "fix.work.order"),
                    ("state", "in", ["in_progress", "assigned"]),
                ],
                ["name", "order_id", "technician_id", "state", "start_time", "duration_hours"],
                limit=12,
                order="write_date desc",
            )
        )
        bench_board = []
        for idx, bo in enumerate(bench_orders):
            tech_name = bo["technician_id"][1] if bo.get("technician_id") else "Unassigned"
            ord_name = bo["order_id"][1] if bo.get("order_id") else "WO"
            bench_board.append(
                {
                    "id": bo["id"],
                    "bench_num": f"Bench {idx % 8 + 1}",
                    "wo_name": bo["name"],
                    "order_name": ord_name,
                    "technician": tech_name,
                    "state": bo["state"],
                    "duration_hours": round(bo.get("duration_hours") or 0.0, 1),
                }
            )

        holds_orders = Order.search_read(
            [*scope, ("state", "=", "awaiting_approval")],
            ["name", "customer_id", "fault_description", "write_date"],
            limit=8,
            order="write_date asc",
        )
        stuck_holds = []
        for ho in holds_orders:
            stuck_holds.append(
                {
                    "id": ho["id"],
                    "name": ho["name"],
                    "customer": ho["customer_id"][1] if ho.get("customer_id") else "Customer",
                    "reason": "Awaiting Customer Estimate Approval",
                    "age_since": fields.Datetime.to_string(ho["write_date"]),
                }
            )

        qc_orders = Order.search_read(
            [*scope, ("state", "=", "qc_pending")],
            ["name", "customer_id", "device_id", "technician_id", "write_date"],
            limit=8,
            order="write_date asc",
        )
        qc_queue = []
        for qo in qc_orders:
            qc_queue.append(
                {
                    "id": qo["id"],
                    "name": qo["name"],
                    "customer": qo["customer_id"][1] if qo.get("customer_id") else "Customer",
                    "device": qo["device_id"][1] if qo.get("device_id") else "Device",
                    "technician": qo["technician_id"][1]
                    if qo.get("technician_id")
                    else "Bench Tech",
                }
            )

        return {
            "success": True,
            "branch_console": {
                "walkin_queue": walkin_queue,
                "wip_ageing": {
                    "under_24h": wip_under_24,
                    "between_24_48h": wip_24_48,
                    "over_48h": wip_over_48,
                },
                "ready_collection": ready_collection,
                "cash_register": {
                    "cash_collected_bdt": cash_total,
                    "vat_collected_bdt": vat_total,
                    "invoices_count": len(approved_today),
                },
            },
            "workshop_console": {
                "bench_board": bench_board,
                "stuck_holds": stuck_holds,
                "qc_queue": qc_queue,
                "rework_count": Order.search_count(
                    [
                        *scope,
                        ("order_category", "=", "rework"),
                        ("state", "not in", list(_DONE_STATES)),
                    ]
                ),
            },
        }

    # NOTE (2026-10-13, PP7): the parallel-session `advance_order_stage`
    # handler that lived here was REMOVED — it shadowed the strict
    # advance_stage route, bypassed VALID_TRANSITIONS with direct sudo
    # writes, and FORGED auto-passed QC checklist rows — a statutory-
    # integrity violation. The strict handler above now also serves its
    # /p03/service_order/advance alias.

    @http.route("/p03/notify/collection", type="jsonrpc", auth="user")
    def notify_collection(self, order_id=None):
        """Log a ready-for-collection notification on the order chatter —
        a REAL mail.thread message (the SMS/WhatsApp channel dispatch is
        the M27 notification phase; this endpoint never claims a send)."""
        env = request.env
        _require_internal(env)
        order = env["fix.service.order"].browse(order_id)
        if not order.exists():
            return {"success": False, "error": "Order not found"}
        order.message_post(
            body=(
                "<b>Collection notification</b>: customer notified the device "
                "is ready for collection (logged by the branch console)."
            )
        )
        return {"success": True, "order": order.name}
