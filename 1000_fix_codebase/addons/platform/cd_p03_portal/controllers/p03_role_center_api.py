# P03 Role Center API — the person-aware, role-driven home dashboard.
#
# Design basis (researched against the tier-1 ERPs, report §3):
#   * Dynamics 365 Business Central binds a user PROFILE to one Role Center
#     page: headline → cue tiles → action tiles → charts (Microsoft Learn,
#     "Role Center Design in Business Central", 2025).
#   * SAP Fiori assigns launchpad home-page spaces/tiles per BUSINESS ROLE
#     ("role-based" design principle; spaces mirror business areas).
#   * Oracle Fusion serves role-scoped Infolets (KPI cards) on the home page.
#   * Cross-vendor guidance: 5-10 actionable KPIs per role, minimal cognitive
#     load, every cue drill-through to a worklist.
#
# The 1000 FiX equivalent, implemented here:
#   1. PERSON — the signed-in user is resolved to their hr.employee record
#      (real name, job title, department, branch) — never a demo identity.
#   2. ROLES — resolved from the estate's own RBAC register (fix.role):
#      live fix.role.assignment rows first, then the documented group-map
#      fallback (held permission groups ⊇ a role's mapped groups), then a
#      conservative job-title hint labelled as such. Administrators may
#      preview every role center.
#   3. CENTER — each of the 16 role centers declares its own KPI cues,
#      charts, quick actions and module shortcuts; every number is a live
#      aggregate over the real models (no fabricated fallbacks — 03-DATA-
#      STRATEGY: absent data renders nulls and the workspace shows "—").
import logging
from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from odoo import fields, http
from odoo.http import request

from .p03_service_order_api import _DONE_STATES, _require_internal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. Role resolution tables
# ---------------------------------------------------------------------------

# fix.role register code -> P03 workspace role id (P03_ROLES in
# p03_modules_meta.js; 'executive' is the oversight center added for the
# C-suite per D365's executive role centers). Only true functional fits are
# mapped — unmapped register roles (marketing R-23, recruiter R-45, …) stay
# unmapped rather than being forced onto the nearest console.
ROLE_TO_WS = {
    "R-01": "executive",
    "R-02": "executive",
    "R-03": "executive",
    "R-04": "executive",
    "R-05": "executive",
    "R-48": "executive",
    "R-54": "executive",
    "R-06": "branch_manager",
    "R-07": "dispatch_manager",
    "R-08": "service_intake",
    "R-13": "service_intake",
    "R-14": "service_intake",
    "R-09": "workshop_supervisor",
    # Team Leader: 19 live holders on the real estate lead technical benches
    # (the job-title hint already sent them here; the register row is the
    # authority, so it is mapped rather than hinted).
    "R-47": "workshop_supervisor",
    "R-10": "field_technician",
    "R-11": "field_technician",
    "R-12": "field_technician",
    "R-15": "rider_logistics",
    "R-16": "rider_logistics",
    "R-17": "inventory_keeper",
    "R-18": "inventory_keeper",
    "R-19": "procurement_officer",
    "R-51": "procurement_officer",
    "R-21": "account_manager",
    "R-22": "account_manager",
    "R-24": "marketplace_ops",
    "R-26": "finance_officer",
    "R-27": "finance_officer",
    "R-29": "finance_officer",
    "R-30": "hr_payroll",
    "R-31": "hr_payroll",
    "R-41": "hr_payroll",
    "R-32": "quality_auditor",
    "R-49": "quality_auditor",
    "R-33": "system_admin",
    "R-34": "contact_centre_agent",
    "R-35": "contact_centre_agent",
    "R-52": "contact_centre_agent",
}

# Job-title hints — the LAST-resort fallback for staff whose group set does
# not yet resolve to a register role. Served with source="job_title" so the
# UI labels it "suggested by job title", never as granted access.
JOB_TITLE_WS = [
    ("chief operating officer", "executive"),
    ("chief executive officer", "executive"),
    ("chief service officer", "executive"),
    ("chief financial officer", "executive"),
    ("chief technology officer", "executive"),
    ("contact center manager", "contact_centre_agent"),
    ("operation manager", "branch_manager"),
    ("center in charge", "branch_manager"),
    ("customer success manager", "service_intake"),
    ("team leader, technical operations", "workshop_supervisor"),
    ("team leader, technical", "workshop_supervisor"),
    ("key account manager", "account_manager"),
    # "project manager" is deliberately NOT hinted: R-53 has no functional
    # center, and a title match must never open Executive Oversight.
]
HEAD_DEPT_WS = {
    "technical operations": "workshop_supervisor",
    "customer service center": "service_intake",
    "corporate service": "account_manager",
    "service quality assurance": "quality_auditor",
    "finance": "finance_officer",
    "inventory": "inventory_keeper",
    "supply chain": "procurement_officer",
}

# Preferred center when several resolve (oversight first, then the line).
WS_PRIORITY = [
    "executive",
    "branch_manager",
    "dispatch_manager",
    "workshop_supervisor",
    "finance_officer",
    "hr_payroll",
    "quality_auditor",
    "account_manager",
    "procurement_officer",
    "inventory_keeper",
    "marketplace_ops",
    "contact_centre_agent",
    "rider_logistics",
    "service_intake",
    "field_technician",
    "system_admin",
]


# ---------------------------------------------------------------------------
# 2. Live KPI cue catalog — every entry is a real aggregate (or null)
# ---------------------------------------------------------------------------


LOCAL_TZ = "Asia/Dhaka"


def _tz_name(env):
    # A02 ERP audit X-15: a user with no timezone is in Dhaka, not UTC
    return env.context.get("tz") or env.user.tz or LOCAL_TZ


def _local_today(env):
    return datetime.now(UTC).astimezone(ZoneInfo(_tz_name(env))).date()


def _local_midnight(env, day):
    """Naive-UTC instant of local (Asia/Dhaka by default) midnight of ``day``."""
    local = datetime.combine(day, time.min, tzinfo=ZoneInfo(_tz_name(env)))
    return local.astimezone(UTC).replace(tzinfo=None)


def _company_domain(env, Model, domain):
    """A02 ERP audit X-15: every cue is a sudo count, so it is fenced to the
    reader's companies (shared rows with no company stay visible). A domain
    that already scopes the company is left as it is."""
    if "company_id" not in Model._fields or Model._name == "res.users":
        return domain
    if any(isinstance(term, list | tuple) and term[0] == "company_id" for term in domain):
        return domain
    field = Model._fields["company_id"]
    if not (field.store or field.search or field.related):
        return domain
    companies = list(env.companies.ids)
    if not field.required:
        companies.append(False)
    return [("company_id", "in", companies), *domain]


def _count(env, model, domain):
    """Defensive search_count: missing model / refused read -> None ("—")."""
    try:
        if model not in env:
            return None
        Model = env[model].sudo()
        return Model.search_count(_company_domain(env, Model, domain))
    except Exception:
        logger.debug("role-center cue refused: %s", model, exc_info=True)
        return None


def _kpi_open_orders(env, ctx):
    return _count(
        env, "fix.service.order", [("state", "not in", list(_DONE_STATES))] + ctx["branch_domain"]
    )


def _kpi_sla_at_risk(env, ctx):
    return _count(
        env,
        "fix.service.order",
        [
            ("state", "not in", [*_DONE_STATES, "draft", "intake"]),
            ("sla_resolution_deadline", "<", fields.Datetime.now()),
        ]
        + ctx["branch_domain"],
    )


def _kpi_intake_today(env, ctx):
    return _count(
        env, "fix.service.order", [("create_date", ">=", ctx["day_start"])] + ctx["branch_domain"]
    )


def _kpi_delivered_today(env, ctx):
    # A02 ERP audit X-15: delivered TODAY (delivered_at), at the reader's
    # branch: any later write (a rating, a note) re-counted an old delivery
    Order = env.get("fix.service.order")
    stamp = (
        "delivered_at" if Order is not None and "delivered_at" in Order._fields else "write_date"
    )
    return _count(
        env,
        "fix.service.order",
        [("state", "in", ["delivered", "closed"]), (stamp, ">=", ctx["day_start"])]
        + ctx["branch_domain"],
    )


def _kpi_in_repair(env, ctx):
    return _count(env, "fix.service.order", [("state", "=", "in_repair")] + ctx["branch_domain"])


def _kpi_revenue_mtd(env, ctx):
    """A02 ERP audit X-15: revenue is what was invoiced this month, net of
    VAT: the taxable value of issued and paid AR invoices (it summed approved
    estimates' VAT-inclusive totals, invoiced or not, zero-charge included)."""
    try:
        if "fix.ar.invoice" not in env:
            return None
        Invoice = env["fix.ar.invoice"].sudo()
        domain = [
            ("state", "in", ["issued", "paid"]),
            ("invoice_date", ">=", ctx["month_first_day"]),
            ("invoice_date", "<=", ctx["today"]),
        ] + ctx["branch_domain"]
        rows = Invoice.search_read(_company_domain(env, Invoice, domain), ["taxable_amount"])
        return round(sum(r["taxable_amount"] or 0.0 for r in rows), 2)
    except Exception:
        logger.debug("role-center cue refused: revenue_mtd", exc_info=True)
        return None


def _kpi_unassigned_wos(env, ctx):
    # Counts what its drill-through (M02-unassigned) lists: field orders
    # waiting for a technician. The tile used to count fix.work.order and
    # open a fix.field.order grid, so the number never matched the list.
    return _count(
        env,
        "fix.field.order",
        [("state", "in", ["draft", "pending_dispatch", "declined"])],
    )


def _kpi_awaiting_approval(env, ctx):
    return _count(
        env, "fix.service.order", [("state", "=", "awaiting_approval")] + ctx["branch_domain"]
    )


def _kpi_qc_pending(env, ctx):
    return _count(env, "fix.qc.checklist", [("state", "in", ["pending", "in_progress"])])


def _kpi_first_time_fix(env, ctx):
    """QC first-pass rate: passed / decided checklists. A02 ERP audit X-15:
    pending and in-progress checklists were in the denominator, so a busy
    bench read as a failing one."""
    passed = _count(env, "fix.qc.checklist", [("state", "=", "passed")])
    decided = _count(env, "fix.qc.checklist", [("state", "in", ["passed", "failed"])])
    if passed is None or not decided:
        return None
    return round(100.0 * passed / decided, 1)


def _kpi_headcount(env, ctx):
    return _count(env, "hr.employee", [("active", "=", True)])


def _kpi_team_size(env, ctx):
    return len(ctx.get("team", []))


# Register roles that ARE the technician workforce (senior / field / bench).
TECHNICIAN_ROLE_CODES = ("R-10", "R-11", "R-12")


def _kpi_techs_active(env, ctx):
    """Technicians on-roll = active employees whose user holds a technician
    role in the access register. The job-title match it replaces counted 33
    of 141 on the real estate ("Technical Specialist" is not "technician");
    the title match stays only as the fallback for an estate without the
    register."""
    try:
        if "fix.role.assignment" in env:
            users = (
                env["fix.role.assignment"]
                .sudo()
                .search(
                    [
                        ("role_id.code", "in", list(TECHNICIAN_ROLE_CODES)),
                        ("ended_on", "=", False),
                    ]
                )
                .mapped("user_id")
            )
            return env["hr.employee"].sudo().search_count([("user_id", "in", users.ids)])
    except Exception:
        logger.debug("role-center cue refused: technicians", exc_info=True)
        return None
    return _count(env, "hr.employee", [("job_title", "ilike", "technician")])


def _kpi_branches_active(env, ctx):
    return _count(env, "fix.branch", [("active", "=", True)])


def _kpi_warehouses(env, ctx):
    return _count(env, "fix.warehouse", [])


def _kpi_catalogue_items(env, ctx):
    # Company-fenced like the M37 grid it opens: the sudo count used to
    # include rows of archived companies the list never shows.
    if "fix.catalogue.item" not in env:
        return None
    domain = []
    if "company_id" in env["fix.catalogue.item"]._fields:
        domain = [("company_id", "in", [False, env.company.id])]
    return _count(env, "fix.catalogue.item", domain)


def _kpi_suppliers_active(env, ctx):
    # fix.supplier carries no `active` column — count all rows instead of
    # raising on a missing field.
    if "fix.supplier" not in env:
        return None
    domain = [("active", "=", True)] if "active" in env["fix.supplier"]._fields else []
    return _count(env, "fix.supplier", domain)


def _kpi_ar_open(env, ctx):
    return _count(env, "fix.ar.invoice", [("state", "in", ["draft", "issued"])])


def _kpi_po_open(env, ctx):
    return _count(
        env, "fix.purchase.order", [("state", "not in", ["closed", "cancelled", "superseded"])]
    )


def _kpi_leave_pending(env, ctx):
    return _count(env, "fix.leave.request", [("state", "=", "submitted")])


def _kpi_itsm_open(env, ctx):
    return _count(env, "fix.itsm.ticket", [("state", "not in", ["resolved", "closed", "rejected"])])


def _kpi_complaints_open(env, ctx):
    return _count(env, "fix.complaint", [("state", "not in", ["closed", "rejected"])])


def _kpi_contracts_active(env, ctx):
    return _count(env, "fix.contract", [("state", "in", ["active", "expiring"])])


def _kpi_contracts_expiring(env, ctx):
    horizon = _local_today(env) + timedelta(days=30)
    return _count(
        env, "fix.contract", [("state", "in", ["active", "expiring"]), ("date_end", "<=", horizon)]
    )


def _kpi_cash_shifts_open(env, ctx):
    # a reconciled shift (discrepancy included) is not open (A02 ERP audit X-15)
    return _count(
        env, "fix.cash.shift", [("state", "in", ["open", "counting"])] + ctx["branch_domain"]
    )


def _kpi_attendance_today(env, ctx):
    return _count(env, "fix.attendance.record", [("check_in", ">=", ctx["day_start"])])


def _kpi_users_active(env, ctx):
    return _count(env, "res.users", [("active", "=", True), ("share", "=", False)])


def _kpi_roles_live(env, ctx):
    return _count(env, "fix.role", [("active", "=", True)])


def _kpi_wip_branch(env, ctx):
    return _count(
        env,
        "fix.service.order",
        [
            (
                "state",
                "in",
                [
                    "diagnostic",
                    "estimate_pending",
                    "estimate_sent",
                    "awaiting_approval",
                    "approved",
                    "in_repair",
                    "qc_pending",
                    "qc_failed",
                ],
            )
        ]
        + ctx["branch_domain"],
    )


def _kpi_ready_branch(env, ctx):
    return _count(env, "fix.service.order", [("state", "=", "ready")] + ctx["branch_domain"])


def _kpi_wo_mine_open(env, ctx):
    emp = ctx.get("employee")
    if not emp:
        return None
    return _count(
        env,
        "fix.work.order",
        [("technician_id", "=", emp.id), ("state", "in", ["pending", "assigned", "in_progress"])],
    )


KPI_CATALOG = {
    "open_orders": {
        "label": "Open Service Orders",
        "fn": _kpi_open_orders,
        "fmt": "int",
        "screen": "M01-all",
        "ok": True,
    },
    "sla_at_risk": {
        "label": "SLA At-Risk",
        "fn": _kpi_sla_at_risk,
        "fmt": "int",
        "screen": "M01-all",
        "warn_pos": True,
    },
    "intake_today": {
        "label": "Intake Today",
        "fn": _kpi_intake_today,
        "fmt": "int",
        "screen": "M01-all",
        "ok": True,
    },
    "delivered_today": {
        "label": "Delivered Today",
        "fn": _kpi_delivered_today,
        "fmt": "int",
        "screen": "M01-all",
        "ok": True,
    },
    "in_repair": {
        "label": "In Repair Now",
        "fn": _kpi_in_repair,
        "fmt": "int",
        "screen": "M01-all",
    },
    "revenue_mtd": {
        "label": "Revenue MTD (invoiced, ex-VAT)",
        "fn": _kpi_revenue_mtd,
        "fmt": "bdt",
        "screen": "M20-invoices",
        "ok": True,
    },
    "unassigned_wos": {
        "label": "Unassigned Work Orders",
        "fn": _kpi_unassigned_wos,
        "fmt": "int",
        "screen": "M02-unassigned",
        "warn_pos": True,
    },
    "awaiting_approval": {
        "label": "Awaiting Approval",
        "fn": _kpi_awaiting_approval,
        "fmt": "int",
        "screen": "M01-all",
    },
    "qc_pending": {
        "label": "QC Queue",
        "fn": _kpi_qc_pending,
        "fmt": "int",
        "screen": "M01-qc",
        "warn_pos": True,
    },
    "first_time_fix": {
        "label": "First-Time Fix",
        "fn": _kpi_first_time_fix,
        "fmt": "pct",
        "screen": "M01-qc",
        "ok": True,
    },
    "headcount": {
        "label": "People On-Roll",
        "fn": _kpi_headcount,
        "fmt": "int",
        "screen": "M21-directory",
    },
    "team_size": {
        "label": "My Direct Team",
        "fn": _kpi_team_size,
        "fmt": "int",
        "screen": "M21-directory",
        "ok": True,
    },
    "techs_active": {
        "label": "Technicians On-Roll",
        "fn": _kpi_techs_active,
        "fmt": "int",
        "screen": "M21-directory",
    },
    "branches_active": {
        "label": "Active Branches",
        "fn": _kpi_branches_active,
        "fmt": "int",
        "screen": "M30-branches",
    },
    "warehouses": {
        "label": "Warehouses",
        "fn": _kpi_warehouses,
        "fmt": "int",
        "screen": "M41-warehouse",
    },
    "catalogue_items": {
        "label": "Catalogue Items",
        "fn": _kpi_catalogue_items,
        "fmt": "int",
        "screen": "M37-items",
    },
    "suppliers_active": {
        "label": "Active Suppliers",
        "fn": _kpi_suppliers_active,
        "fmt": "int",
        "screen": "M42-suppliers",
    },
    "ar_open": {
        "label": "AR Invoices Open",
        "fn": _kpi_ar_open,
        "fmt": "int",
        "screen": "M20-invoices",
        "warn_pos": True,
    },
    "po_open": {
        "label": "Open Purchase Orders",
        "fn": _kpi_po_open,
        "fmt": "int",
        "screen": "M16-pos",
    },
    "leave_pending": {
        "label": "Leave Requests Pending",
        "fn": _kpi_leave_pending,
        "fmt": "int",
        "screen": "M55-leave",
    },
    "itsm_open": {
        "label": "ITSD Tickets Open",
        "fn": _kpi_itsm_open,
        "fmt": "int",
        "screen": "M66-all",
        "warn_pos": True,
    },
    "complaints_open": {
        "label": "Open Complaints",
        "fn": _kpi_complaints_open,
        "fmt": "int",
        "screen": "M34-complaints",
        "warn_pos": True,
    },
    "contracts_active": {
        "label": "Active Contracts",
        "fn": _kpi_contracts_active,
        "fmt": "int",
        "screen": "M08-contracts",
        "ok": True,
    },
    "contracts_expiring": {
        "label": "Contracts Expiring ≤30d",
        "fn": _kpi_contracts_expiring,
        "fmt": "int",
        "screen": "M08-contracts",
        "warn_pos": True,
    },
    "cash_shifts_open": {
        "label": "Cash Shifts Open",
        "fn": _kpi_cash_shifts_open,
        "fmt": "int",
        "screen": "M04-drawer",
    },
    "attendance_today": {
        "label": "Check-ins Today",
        "fn": _kpi_attendance_today,
        "fmt": "int",
        "screen": "M55-daily",
        "ok": True,
    },
    "users_active": {
        "label": "Active Internal Users",
        "fn": _kpi_users_active,
        "fmt": "int",
        "screen": "M29-users",
    },
    "roles_live": {
        "label": "Live Role Register",
        "fn": _kpi_roles_live,
        "fmt": "int",
        "screen": "M29-roles",
    },
    "wip_branch": {
        "label": "WIP at My Branch",
        "fn": _kpi_wip_branch,
        "fmt": "int",
        "screen": "M01-wip",
    },
    "ready_branch": {
        "label": "Ready for Pickup (Branch)",
        "fn": _kpi_ready_branch,
        "fmt": "int",
        "screen": "M01-all",
        "ok": True,
    },
    "wo_mine_open": {
        "label": "My Open Work Orders",
        "fn": _kpi_wo_mine_open,
        "fmt": "int",
        "screen": "M02-wo",
        "ok": True,
    },
}


# ---------------------------------------------------------------------------
# 3. The 16 role-center specifications
#    (kpis ≤8 per cross-vendor guidance; charts ≤3; actions/modules by role)
# ---------------------------------------------------------------------------

ROLE_CENTER_SPECS = {
    "executive": {
        "kpis": [
            "open_orders",
            "sla_at_risk",
            "revenue_mtd",
            "intake_today",
            "headcount",
            "branches_active",
            "first_time_fix",
        ],
        "charts": ["trend", "channel", "dept_headcount"],
        "actions": ["new_order", "dispatch", "branch", "workshop", "reports"],
        "modules": ["M01", "M02", "M25", "M19", "M53", "M21"],
    },
    "branch_manager": {
        "kpis": [
            "intake_today",
            "wip_branch",
            "ready_branch",
            "sla_at_risk",
            "cash_shifts_open",
            "complaints_open",
        ],
        "charts": ["state_mix", "trend"],
        "actions": ["new_order", "branch", "reports"],
        "modules": ["M04", "M01", "M15", "M20", "M03"],
    },
    "dispatch_manager": {
        "kpis": ["unassigned_wos", "open_orders", "sla_at_risk", "in_repair", "techs_active"],
        "charts": ["trend", "state_mix"],
        "actions": ["dispatch", "new_order"],
        "modules": ["M02", "M01", "M21", "M15"],
    },
    "service_intake": {
        "kpis": ["intake_today", "awaiting_approval", "open_orders", "delivered_today"],
        "charts": ["trend", "channel"],
        "actions": ["new_order", "branch"],
        "modules": ["M01", "M04", "M33", "M03"],
    },
    "workshop_supervisor": {
        "kpis": ["in_repair", "qc_pending", "delivered_today", "sla_at_risk", "first_time_fix"],
        "charts": ["state_mix", "trend"],
        "actions": ["workshop", "new_order"],
        "modules": ["M31", "M01", "M15", "M23"],
    },
    "field_technician": {
        "kpis": ["wo_mine_open", "unassigned_wos", "open_orders", "delivered_today"],
        "charts": ["state_mix"],
        "actions": ["dispatch"],
        "modules": ["M02", "M01", "M17"],
    },
    "inventory_keeper": {
        "kpis": ["warehouses", "po_open", "branches_active", "open_orders"],
        "charts": ["trend"],
        "actions": ["reports"],
        "modules": ["M15", "M41", "M16", "M37"],
    },
    "procurement_officer": {
        "kpis": ["po_open", "suppliers_active", "warehouses", "catalogue_items"],
        "charts": ["trend"],
        "actions": ["reports"],
        "modules": ["M16", "M42", "M44", "M37", "M43"],
    },
    "finance_officer": {
        "kpis": ["revenue_mtd", "ar_open", "cash_shifts_open", "po_open"],
        "charts": ["trend", "channel"],
        "actions": ["reports"],
        "modules": ["M20", "M19", "M52", "M50", "M51"],
    },
    "hr_payroll": {
        "kpis": ["headcount", "leave_pending", "attendance_today", "users_active"],
        "charts": ["dept_headcount"],
        "actions": ["reports"],
        "modules": ["M21", "M55", "M56", "M57", "M22"],
    },
    "quality_auditor": {
        "kpis": ["qc_pending", "first_time_fix", "complaints_open", "sla_at_risk"],
        "charts": ["state_mix", "trend"],
        "actions": ["workshop", "reports"],
        "modules": ["M23", "M60", "M34", "M01"],
    },
    "contact_centre_agent": {
        "kpis": ["complaints_open", "intake_today", "open_orders", "itsm_open"],
        "charts": ["channel", "trend"],
        "actions": ["new_order"],
        "modules": ["M27", "M01", "M32", "M34"],
    },
    "account_manager": {
        "kpis": ["contracts_active", "contracts_expiring", "ar_open", "revenue_mtd"],
        "charts": ["trend", "channel"],
        "actions": ["new_order", "reports"],
        "modules": ["M08", "M33", "M07", "M20", "M09"],
    },
    "marketplace_ops": {
        "kpis": ["catalogue_items", "suppliers_active", "open_orders", "complaints_open"],
        "charts": ["channel"],
        "actions": ["reports"],
        "modules": ["M12", "M40", "M37", "M42"],
    },
    "rider_logistics": {
        "kpis": ["open_orders", "delivered_today", "warehouses"],
        "charts": ["trend"],
        "actions": ["dispatch"],
        "modules": ["M03", "M04", "M15"],
    },
    "system_admin": {
        "kpis": ["users_active", "roles_live", "itsm_open", "branches_active"],
        "charts": ["dept_headcount"],
        "actions": ["reports"],
        "modules": ["M28", "M29", "M30", "M64", "M65"],
    },
}


# ---------------------------------------------------------------------------
# 4. Chart builders (live read_groups; null series allowed)
# ---------------------------------------------------------------------------


def _chart_trend(env, ctx):
    Order = env["fix.service.order"].sudo()
    months, values, cursor = [], [], _local_today(env).replace(day=1)
    for _ in range(12):
        month_end = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        months.append(cursor.strftime("%b"))
        values.append(
            Order.search_count(
                [
                    ("create_date", ">=", _local_midnight(env, cursor)),
                    ("create_date", "<", _local_midnight(env, month_end)),
                ]
            )
        )
        cursor = (cursor - timedelta(days=1)).replace(day=1)
    return {"labels": months[::-1], "values": values[::-1]}


def _chart_channel(env, ctx):
    Order = env["fix.service.order"].sudo()
    since30 = _local_midnight(env, _local_today(env) - timedelta(days=30))
    mix = {}
    for key, _lbl in Order._fields["service_type"].selection:
        n = Order.search_count([("create_date", ">=", since30), ("service_type", "=", key)])
        if n:
            mix[key] = n
    return mix


def _chart_state_mix(env, ctx):
    Order = env["fix.service.order"].sudo()
    branch = ctx.get("branch_domain")
    out = {}
    for state, _lbl in Order._fields["state"].selection:
        n = Order.search_count([("state", "=", state), *branch])
        if n:
            out[state] = n
    return out


def _chart_dept_headcount(env, ctx):
    if "hr.employee" not in env:
        return {}
    groups = (
        env["hr.employee"]
        .sudo()
        .read_group(
            [("department_id", "!=", False)],
            ["department_id"],
            ["department_id"],
            orderby="department_id",
        )
    )
    rows = []
    for g in groups:
        dept = g.get("department_id")
        rows.append({"label": dept[1] if dept else "—", "value": g["department_id_count"]})
    rows.sort(key=lambda r: -r["value"])
    return {"rows": rows[:10]}


CHART_BUILDERS = {
    "trend": _chart_trend,
    "channel": _chart_channel,
    "state_mix": _chart_state_mix,
    "dept_headcount": _chart_dept_headcount,
}


# ---------------------------------------------------------------------------
# 5. Controller
# ---------------------------------------------------------------------------


class P03RoleCenterApiController(http.Controller):
    @http.route("/p03/role_center", type="jsonrpc", auth="user", readonly=True)
    def role_center(self, **kw):
        """The signed-in person's role center: identity card, resolved roles,
        per-role KPI cues / charts / actions / modules, and direct team.
        Cues and charts for every RESOLVED center are computed eagerly (a
        person holds 1-3 roles); administrators preview further centers via
        /p03/role_center_kpis."""
        env = request.env
        _require_internal(env)
        user = env.user

        employee = env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
        person = self._person_payload(user, employee)
        branch = employee.branch_id.name if employee and employee.branch_id else None

        today = _local_today(env)
        ctx = self._context(env, user, employee, today)

        resolved, is_admin = self._resolve_roles(env, user, employee)
        role_ids = [r["ws"] for r in resolved]
        # A person the register resolves to NO center gets no center: the
        # old landing on service_intake (and the switcher then showing all
        # 16) handed partner and unmapped-role accounts every console.
        # Administrators keep the preview landing.
        no_center = not is_admin and not role_ids
        default = next(
            (ws for ws in WS_PRIORITY if ws in role_ids),
            None if no_center else ("executive" if is_admin else "service_intake"),
        )

        # Person-aware executive label (D365 shows the profile's own name):
        # a C-suite holder's executive pill carries their REGISTER title and
        # code (e.g. "R-54 Chief Operating Officer"), not the generic R-EX.
        role_labels, role_codes = {}, {}
        for r in resolved:
            # only a register ASSIGNMENT names a person's office: a group
            # match (every administrator has one) must not print "R-01 Chief
            # Executive Officer" on someone who does not hold it
            if r["ws"] == "executive" and r["source"] == "assignment":
                role_labels.setdefault("executive", r["name"])
            # every pill carries the holder's REGISTER code (the static pill
            # codes are placeholders: the rider pill said R20, which the
            # register gives to the Warehouse Operative)
            if r["source"] == "assignment" and r["code"]:
                role_codes.setdefault(r["ws"], r["code"])

        kpis, charts = {}, {}
        # The landing center is always computed (administrators and the
        # job-title fallback hold no register rows of their own).
        for ws in dict.fromkeys([*role_ids, default]):  # unique, order kept
            if ws and ws in ROLE_CENTER_SPECS:
                kpis[ws], charts[ws] = self._center_data(env, ctx, ws)

        return {
            "person": person,
            "branch": branch,
            "roles": resolved,
            "default": default,
            "role_labels": role_labels,
            "role_codes": role_codes,
            "is_admin": is_admin,
            "no_center": no_center,
            "specs": ROLE_CENTER_SPECS,
            "kpis": kpis,
            "charts": charts,
            "team": ctx["team"],
            "headline": self._headline(env, ctx, default) if default else "",
        }

    @http.route("/p03/role_center_kpis", type="jsonrpc", auth="user", readonly=True)
    def role_center_kpis(self, ws=None, **kw):
        """Lazy cues for one center (admin preview / later switch). Returns
        the same {kpis, charts} pair the boot payload carries."""
        env = request.env
        _require_internal(env)
        if ws not in ROLE_CENTER_SPECS:
            return {"error": "unknown role center"}
        user = env.user
        employee = env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
        # The cues are company-wide sudo aggregates, so the center itself is
        # the access boundary: only a center the person resolves to (or an
        # administrator's preview) is served.
        resolved, is_admin = self._resolve_roles(env, user, employee)
        if not is_admin and ws not in {r["ws"] for r in resolved}:
            return {"error": "role center not assigned to this user"}
        ctx = self._context(env, user, employee, _local_today(env))
        kpis, charts = self._center_data(env, ctx, ws)
        return {"ws": ws, "kpis": kpis, "charts": charts, "headline": self._headline(env, ctx, ws)}

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _context(env, user, employee, today):
        branch_domain = (
            [("branch_id", "=", employee.branch_id.id)] if employee and employee.branch_id else []
        )
        ctx = {
            "employee": employee or None,
            "branch_domain": branch_domain,
            "today": today,
            "month_first_day": today.replace(day=1),
            "day_start": _local_midnight(env, today),
            "month_start": _local_midnight(env, today.replace(day=1)),
            "team": [],
        }
        if employee:
            ctx["team"] = (
                env["hr.employee"]
                .sudo()
                .search_read([("parent_id", "=", employee.id)], ["name", "job_title"], limit=8)
            )
        return ctx

    def _center_data(self, env, ctx, ws):
        spec = ROLE_CENTER_SPECS[ws]
        kpis = [
            dict(cue, value=cue["fn"](env, ctx)) for cue in (KPI_CATALOG[k] for k in spec["kpis"])
        ]
        charts = {}
        for chart_id in spec["charts"]:
            try:
                charts[chart_id] = CHART_BUILDERS[chart_id](env, ctx)
            except Exception:
                charts[chart_id] = None
        return kpis, charts

    @staticmethod
    def _person_payload(user, employee):
        name = employee.name if employee else user.name
        words = [w for w in str(name or "").split() if w]
        initials = "".join(w[0] for w in words[:2]).upper() or "?"
        return {
            "name": name,
            "job_title": employee.job_title if employee else "Platform User",
            "department": employee.department_id.name
            if employee and employee.department_id
            else None,
            "branch": employee.branch_id.name if employee and employee.branch_id else None,
            "email": (employee.work_email if employee and employee.work_email else user.email)
            or user.login,
            "employee_id": employee.id if employee else None,
            "has_avatar": bool(employee and employee.image_1920),
            "initials": initials,
        }

    def _resolve_roles(self, env, user, employee):
        """Register-first resolution with the documented fallbacks. Returns
        (ordered list of {code,name,ws,source}, is_admin)."""
        # TRAP (M29 session 2026-11-05): env.get(model) returns an EMPTY
        # RECORDSET — falsy — for a loaded model; presence must go through
        # the `in` operator, never truthiness of env.get().
        try:
            Role = env["fix.role"]
        except KeyError:
            Role = None
        user_groups = set(user.group_ids.ids)
        is_admin = user.has_group("base.group_system")
        if not is_admin and Role is not None:
            admin_grp = env.ref("cd_rbac_ext.group_ws_administration", raise_if_not_found=False)
            is_admin = bool(admin_grp and admin_grp.id in user_groups)
        if Role is None:
            # No register installed (plain estate): the workspace keeps its
            # full switcher, and the job-title hint still personalises.
            is_admin = True

        out, seen = [], set()
        has_assignment = False

        if Role is not None:
            # 1. authoritative register: live assignments
            if "fix.role.assignment" in env:
                for ra in (
                    env["fix.role.assignment"]
                    .sudo()
                    .search([("user_id", "=", user.id), ("ended_on", "=", False)])
                ):
                    has_assignment = True
                    ws = ROLE_TO_WS.get(ra.role_id.code)
                    if ws and ws not in seen:
                        out.append(
                            {
                                "code": ra.role_id.code,
                                "name": ra.role_id.name,
                                "ws": ws,
                                "source": "assignment",
                            }
                        )
                        seen.add(ws)
            # 2. documented fallback: held groups ⊇ the role's mapped groups.
            # ONLY for a person with no live assignment — the register row is
            # the authority. Several roles map to one shared group (R-07 and
            # R-21 are both just the service-orders group), so applying the
            # fallback on top of an assignment landed every Senior Technician
            # on the dispatch console and gave them the account-manager one.
            # An administrator previews every center anyway; matching their
            # admin groups against the register only mislabels them ("R-01
            # Chief Executive Officer" on the system administrator, because
            # R-01 maps to the administration workspace group).
            fallback_roles = (
                Role.browse()
                if has_assignment or is_admin
                else Role.sudo().search([("active", "=", True)])
            )
            for role in fallback_roles:
                ws = ROLE_TO_WS.get(role.code)
                if not ws or ws in seen or not role.group_ids:
                    continue
                if set(role.group_ids.ids).issubset(user_groups):
                    out.append({"code": role.code, "name": role.name, "ws": ws, "source": "groups"})
                    seen.add(ws)

        # 3. conservative job-title hint (only when nothing resolved above,
        # and never over a register assignment — a held role with no center
        # of its own means "no center", not "guess one from the title")
        if employee and employee.job_title and not out and not has_assignment:
            title = employee.job_title.lower()
            dept = (employee.department_id.name or "").lower()
            hint = next((ws for needle, ws in JOB_TITLE_WS if needle in title), None)
            if hint is None and "head of" in title:
                hint = next((v for k, v in HEAD_DEPT_WS.items() if k in dept), None)
            if hint:
                out.append(
                    {"code": None, "name": employee.job_title, "ws": hint, "source": "job_title"}
                )
                seen.add(hint)

        out.sort(key=lambda r: WS_PRIORITY.index(r["ws"]) if r["ws"] in WS_PRIORITY else 99)
        return out, is_admin

    def _headline(self, env, ctx, ws):
        """A D365-style live headline for the active center (one sentence)."""

        def val(k):
            cue = KPI_CATALOG[k]["fn"](env, ctx)
            return "—" if cue is None else f"{cue:,}"

        try:
            if ws == "executive":
                return (
                    f"{val('open_orders')} open service orders · {val('sla_at_risk')} past SLA deadline · "
                    f"estimates approved this month: {val('revenue_mtd')} BDT · {val('headcount')} people on-roll "
                    f"across {val('branches_active')} branches"
                )
            if ws == "branch_manager":
                at = (
                    f" at {ctx['employee'].branch_id.name}"
                    if ctx.get("employee") and ctx["employee"].branch_id
                    else ""
                )
                return (
                    f"Today{at}: {val('intake_today')} intake · {val('wip_branch')} in work · "
                    f"{val('ready_branch')} ready for pickup"
                )
            if ws == "dispatch_manager":
                return f"{val('unassigned_wos')} work orders still unassigned · {val('techs_active')} technicians on-roll"
            if ws == "workshop_supervisor":
                return f"{val('in_repair')} orders on benches · QC queue {val('qc_pending')} · first-time fix {val('first_time_fix')}%"
            if ws == "field_technician":
                return f"{val('wo_mine_open')} open work orders assigned to you"
            if ws == "service_intake":
                return f"{val('intake_today')} orders taken today · {val('awaiting_approval')} awaiting customer approval"
            if ws == "finance_officer":
                return f"Estimates approved MTD: {val('revenue_mtd')} BDT · {val('ar_open')} AR invoices open"
            if ws == "hr_payroll":
                return f"{val('headcount')} people on-roll · {val('leave_pending')} leave requests pending decision"
            if ws == "quality_auditor":
                return (
                    f"QC queue {val('qc_pending')} · first-time fix {val('first_time_fix')}% · "
                    f"{val('complaints_open')} complaints open"
                )
            if ws == "contact_centre_agent":
                return f"{val('complaints_open')} open complaints · {val('intake_today')} orders taken today"
            if ws == "account_manager":
                return f"{val('contracts_active')} active contracts · {val('contracts_expiring')} expiring within 30 days"
            if ws == "system_admin":
                return (
                    f"{val('users_active')} active users · {val('roles_live')} roles live in the register · "
                    f"{val('itsm_open')} ITSD tickets open"
                )
            return ""
        except Exception:
            return ""
