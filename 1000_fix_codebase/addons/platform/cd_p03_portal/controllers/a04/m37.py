# A04 · M37 Product & Service Catalogue — surfaces, report packs and KPIs over
# the real fix.catalogue.item (400 items) / fix.fault.code / fix.service.kit /
# fix.rental.sku / contract.template and the new fix.rbom.line. Margin uses
# the product template's list vs standard price; an unreadable cost stays
# blank instead of being estimated.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    # A04 audit (2026-11-04) M37-1/M37-9: the item lifecycle and the brand
    # authorisation run from the workspace; approval is decided from the
    # publisher's M63 inbox, never here.
    "fix.catalogue.item": {
        "order": "item_type, product_tmpl_id",
        "limit": 300,
        "actions": {
            "action_submit",
            "action_recall_approval",
            "action_publish",
            "action_unpublish",
            "action_restrict",
            "action_lift_restriction",
            "action_discontinue",
            "action_revise",
        },
    },
    # fix.fault.code is declared by M01 (a02) — single owner, served via the merge.
    "fix.service.kit": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.rental.sku": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    "fix.rbom.line": {
        "order": "item_id, sequence",
        "limit": 300,
        "actions": set(),
    },
    # The project's own template master. This served the OCA `contract.template`
    # while the M37 form edited `fix.contract.template`, so opening a row handed
    # the form another model's id (A04 audit, 2026-10-31).
    "fix.contract.template": {
        "order": "name",
        "limit": 200,
        # A04 audit (2026-11-04): Legal sign-off is an attributable, SoD-checked
        # action on the model (cd_contract_core); the reviewer fields are guarded.
        "actions": {"action_legal_signoff", "action_withdraw_signoff"},
    },
    "product.category": {
        "order": "complete_name",
        "limit": 300,
        "actions": set(),
    },
    "fix.refurb.grade": {"order": "id desc", "limit": 400, "actions": set()},
    "fix.brand": {
        "order": "id desc",
        "limit": 400,
        "actions": {
            "action_request_authorisation",
            "action_recall_approval",
            "action_revoke_authorisation",
        },
    },
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _items(env):
    return env["fix.catalogue.item"].sudo().search([])


def _product_price(item, field):
    tmpl = item.product_tmpl_id
    if not tmpl:
        return None
    value = getattr(tmpl, field, None)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def coverage_by_brand(env, date_from=None, date_to=None, **params):
    items = _items(env)
    brands = env["fix.brand"].sudo().search([])
    rows = []
    for brand in brands:
        mine = items.filtered(lambda i, b=brand.id: i.brand_id.id == b)
        if not mine:
            continue
        rows.append(
            {
                "brand": brand.name,
                "items": len(mine),
                "services": len(mine.filtered(lambda i: i.item_type == "service")),
                "parts": len(mine.filtered(lambda i: i.item_type == "part")),
                "device_models": len(brand.device_model_ids)
                if hasattr(brand, "device_model_ids")
                else 0,
            }
        )
    rows.sort(key=lambda r: -r["items"])
    return _pack(
        "Catalogue Coverage by Brand",
        ["brand", "items", "services", "parts", "device_models"],
        {
            "brand": "Brand",
            "items": "Catalogue Items",
            "services": "Services",
            "parts": "Spare Parts",
            "device_models": "Device Models",
        },
        rows,
        [
            "Only brands with at least one catalogue item are shown; an uncovered "
            "brand partner is therefore visible by its absence from this list."
        ],
        totals={
            "brand": "Total",
            "items": sum(r["items"] for r in rows),
            "services": sum(r["services"] for r in rows),
            "parts": sum(r["parts"] for r in rows),
        }
        if rows
        else None,
        empty="No brand has catalogue items yet.",
    )


def rbom_completeness(env, date_from=None, date_to=None, **params):
    items = _items(env).filtered(lambda i: i.item_type == "service")
    lines = env["fix.rbom.line"].sudo().search([])
    by_item = {}
    for line in lines:
        by_item.setdefault(line.item_id.id, []).append(line)
    rows = []
    for item in items:
        mine = by_item.get(item.id, [])
        rows.append(
            {
                "service": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "components": len(mine),
                "quantities": sum(ln.quantity for ln in mine),
                "complete": "✓" if mine else "✗",
            }
        )
    complete = len([r for r in rows if r["components"]])
    return _pack(
        "rBOM Completeness",
        ["service", "components", "quantities", "complete"],
        {
            "service": "Service Item",
            "components": "rBOM Components",
            "quantities": "Total Quantity",
            "complete": "Has rBOM",
        },
        rows[:100],
        [
            "A service with no rBOM line cannot explode parts demand. Completeness: "
            "%d of %d service items (%.1f%%)."
            % (complete, len(rows), complete / len(rows) * 100.0 if rows else 0.0)
        ],
        empty="No service catalogue items yet.",
    )


def srt_variance(env, date_from=None, date_to=None, **params):
    items = _items(env).filtered(lambda i: i.srt_observed_minutes and i.standard_labour_time)
    rows = []
    for item in items:
        standard_min = item.standard_labour_time * 60.0
        observed = item.srt_observed_minutes
        variance = observed - standard_min
        rows.append(
            {
                "service": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "standard_min": round(standard_min, 1),
                "observed_min": round(observed, 1),
                "variance_min": round(variance, 1),
                "variance_pct": round(variance / standard_min * 100.0, 1) if standard_min else 0.0,
            }
        )
    rows.sort(key=lambda r: -abs(r["variance_pct"]))
    return _pack(
        "SRT Calibration Variance — standard vs observed repair time",
        ["service", "standard_min", "observed_min", "variance_min", "variance_pct"],
        {
            "service": "Service Item",
            "standard_min": "Standard (min)",
            "observed_min": "Observed (min)",
            "variance_min": "Variance (min)",
            "variance_pct": "Variance %",
        },
        rows,
        [
            "Only items with BOTH a standard labour time and an observed minutes "
            "reading appear — a missing measurement is not treated as zero."
        ],
        totals={"service": "Total", "variance_min": round(sum(r["variance_min"] for r in rows), 1)}
        if rows
        else None,
        empty="No observed repair times recorded yet — calibrate from the workshop data.",
    )


def item_margin(env, date_from=None, date_to=None, **params):
    items = _items(env)
    rows = []
    for item in items:
        price = _product_price(item, "list_price")
        cost = _product_price(item, "standard_price")
        if price is None:
            continue
        margin = None if cost is None else round(price - cost, 2)
        rows.append(
            {
                "item": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "type": item.item_type,
                "price": round(price, 2),
                "cost": (round(cost, 2) if cost is not None else "—"),
                "margin": margin if margin is not None else "—",
                "margin_pct": (
                    round(margin / price * 100.0, 1) if margin is not None and price else "—"
                ),
            }
        )
    rows.sort(key=lambda r: -(r["margin"] if isinstance(r["margin"], int | float) else -(10**9)))
    priced = [r for r in rows if isinstance(r["margin"], int | float)]
    return _pack(
        "Item Margin Analysis — list price vs standard cost",
        ["item", "type", "price", "cost", "margin", "margin_pct"],
        {
            "item": "Item",
            "type": "Type",
            "price": "List Price",
            "cost": "Standard Cost",
            "margin": "Margin",
            "margin_pct": "Margin %",
        },
        rows[:100],
        [
            "Margin = list_price − standard_price from the product template. Items "
            "without a cost show '—' — no margin is estimated. %d of %d items are "
            "fully costed." % (len(priced), len(rows))
        ],
        empty="No catalogue items have a list price yet.",
    )


def deprecated_items(env, date_from=None, date_to=None, **params):
    items = _items(env).filtered(lambda i: i.state in ("deprecated", "obsolete") or not i.active)
    rows = []
    for item in items:
        rows.append(
            {
                "item": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "type": item.item_type,
                "state": item.state,
                "active": "✓" if item.active else "✗",
                "brand": item.brand_id.name or "—",
            }
        )
    return _pack(
        "Deprecated Items Register",
        ["item", "type", "state", "active", "brand"],
        {"item": "Item", "type": "Type", "state": "State", "active": "Active", "brand": "Brand"},
        rows,
        [
            "Deprecated = lifecycle state deprecated or the record archived. These are "
            "the items quoting and intake must refuse."
        ],
        empty="No deprecated catalogue items.",
    )


def bilingual_gaps(env, date_from=None, date_to=None, **params):
    items = _items(env)
    rows = []
    missing = 0
    for item in items:
        name_bn = (item.name_bn or "").strip()
        desc_bn = (item.description_bn or "").strip()
        if name_bn and desc_bn:
            continue
        missing += 1
        rows.append(
            {
                "item": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "type": item.item_type,
                "name_bn": "✓" if name_bn else "✗",
                "description_bn": "✓" if desc_bn else "✗",
                "published": "✓" if item.is_published else "✗",
            }
        )
    return _pack(
        "Bilingual Content Gaps",
        ["item", "type", "name_bn", "description_bn", "published"],
        {
            "item": "Item",
            "type": "Type",
            "name_bn": "Bengali Name",
            "description_bn": "Bengali Description",
            "published": "Published",
        },
        rows[:200],
        [
            "Bengali is the customer-facing language: %d of %d items are missing at "
            "least one Bengali field." % (missing, len(items))
        ],
        empty="Every catalogue item carries both Bengali fields.",
    )


def category_tree(env, date_from=None, date_to=None, **params):
    cats = env["product.category"].sudo().search([])
    items = _items(env)
    rows = []
    for cat in cats:
        mine = items.filtered(lambda i, c=cat.id: i.category_id.id == c)
        rows.append(
            {
                "category": cat.complete_name or cat.name,
                "items": len(mine),
                "services": len(mine.filtered(lambda i: i.item_type == "service")),
                "parts": len(mine.filtered(lambda i: i.item_type == "part")),
            }
        )
    rows.sort(key=lambda r: -r["items"])
    return _pack(
        "Taxonomy — product categories and catalogue coverage",
        ["category", "items", "services", "parts"],
        {"category": "Category", "items": "Items", "services": "Services", "parts": "Parts"},
        rows,
        [
            "The category tree is Odoo's own product.category — the catalogue's "
            "organisational spine."
        ],
        totals={
            "category": "Total",
            "items": sum(r["items"] for r in rows),
            "services": sum(r["services"] for r in rows),
            "parts": sum(r["parts"] for r in rows),
        }
        if rows
        else None,
        empty="No product categories defined yet.",
    )


def catalogue_hierarchy(env, date_from=None, date_to=None, **params):
    items = _items(env)
    types = {}
    for item in items:
        row = types.setdefault(
            item.item_type, {"type": item.item_type, "items": 0, "published": 0, "bilingual": 0}
        )
        row["items"] += 1
        if item.is_published:
            row["published"] += 1
        if (item.name_bn or "").strip():
            row["bilingual"] += 1
    rows = sorted(types.values(), key=lambda r: -r["items"])
    return _pack(
        "Catalogue Hierarchy — items by type",
        ["type", "items", "published", "bilingual"],
        {
            "type": "Item Type",
            "items": "Items",
            "published": "Published",
            "bilingual": "With Bengali Name",
        },
        rows,
        [
            "The truthful distribution across the nine catalogue item types; an "
            "empty type simply has no items yet."
        ],
        totals={
            "type": "Total",
            "items": sum(r["items"] for r in rows),
            "published": sum(r["published"] for r in rows),
            "bilingual": sum(r["bilingual"] for r in rows),
        }
        if rows
        else None,
        empty="No catalogue items yet.",
    )


def approval_queue(env, date_from=None, date_to=None, **params):
    # A04 audit (2026-11-04): the queue is what awaits a publisher's decision
    # (In Review), not every draft and active item.
    items = _items(env).filtered(lambda i: i.state == "in_review")
    rows = []
    for item in items:
        rows.append(
            {
                "item": item.product_tmpl_id.display_name or item.product_tmpl_id.name,
                "type": item.item_type,
                "state": item.state,
                "bilingual": "✓" if (item.name_bn or "").strip() else "✗",
                "brand": item.brand_id.name or "—",
                "submitted_by": item.submitted_by.name or "—",
            }
        )
    return _pack(
        "Approval Queue — items awaiting a publisher",
        ["item", "type", "state", "bilingual", "brand", "submitted_by"],
        {
            "item": "Item",
            "type": "Type",
            "state": "State",
            "bilingual": "Bengali Name",
            "brand": "Brand",
            "submitted_by": "Submitted By",
        },
        rows[:200],
        [
            "Items In Review await a Catalogue Publisher who neither authored nor "
            "submitted them; the decision is taken from the M63 approval inbox."
        ],
        empty="No catalogue items awaiting approval.",
    )


def lifecycle_summary(env, date_from=None, date_to=None, **params):
    items = _items(env)
    states = [key for key, _label in env["fix.catalogue.item"]._fields["state"].selection]
    rows = []
    for state in states:
        mine = items.filtered(lambda i, s=state: i.state == s)
        rows.append(
            {"state": state, "items": len(mine), "active": len(mine.filtered(lambda i: i.active))}
        )
    return _pack(
        "Lifecycle — catalogue items by state",
        ["state", "items", "active"],
        {"state": "State", "items": "Items", "active": "Active Records"},
        rows,
        [
            "Lifecycle state is the publication gate; archived records stay counted "
            "so the register cannot silently shrink."
        ],
        totals={
            "state": "Total",
            "items": sum(r["items"] for r in rows),
            "active": sum(r["active"] for r in rows),
        }
        if rows
        else None,
        empty="No catalogue items yet.",
    )


def publication_status(env, date_from=None, date_to=None, **params):
    items = _items(env)
    published = items.filtered(lambda i: i.is_published)
    ready = published.filtered(lambda i: (i.name_bn or "").strip())
    rows = [
        {"metric": "Catalogue items", "value": len(items), "basis": "fix.catalogue.item"},
        {"metric": "Published on the web", "value": len(published), "basis": "is_published"},
        {
            "metric": "Published AND bilingual",
            "value": len(ready),
            "basis": "is_published + Bengali name",
        },
        {
            "metric": "Published without Bengali",
            "value": len(published) - len(ready),
            "basis": "publication gap",
        },
    ]
    return _pack(
        "Publication Status — public catalogue readiness",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "The public catalogue must be bilingual; items published without the "
            "Bengali name are listed as a readiness gap."
        ],
    )


REPORTS = {
    "coverage_by_brand": coverage_by_brand,
    "rbom_completeness": rbom_completeness,
    "srt_variance": srt_variance,
    "item_margin": item_margin,
    "deprecated_items": deprecated_items,
    "bilingual_gaps": bilingual_gaps,
    "category_tree": category_tree,
    "catalogue_hierarchy": catalogue_hierarchy,
    "approval_queue": approval_queue,
    "lifecycle_summary": lifecycle_summary,
    "publication_status": publication_status,
}


def kpis(env):
    items = _items(env)
    fault_codes = env["fix.fault.code"].sudo().search_count([])
    published = len(items.filtered(lambda i: i.is_published))
    bilingual = len(items.filtered(lambda i: (i.name_bn or "").strip()))
    deprecated = len(
        items.filtered(lambda i: i.state in ("deprecated", "obsolete") or not i.active)
    )
    services = items.filtered(lambda i: i.item_type == "service")
    with_rbom = len(env["fix.rbom.line"].sudo().search([]).mapped("item_id"))
    today = datetime.date.today()
    month_start = today.replace(day=1)
    new_skus = len(items.filtered(lambda i: i.create_date and i.create_date.date() >= month_start))
    device_models = env["fix.device.model"].sudo().search_count([])
    return {
        # A04 audit (2026-11-04): Active means approved (sellable), not merely
        # "not discontinued"; Pending means awaiting a publisher (In Review).
        "active_items": len(
            items.filtered(
                lambda i: i.active and i.state in ("approved", "published", "restricted")
            )
        ),
        "rbom_coverage": round(with_rbom / len(services) * 100.0, 1) if services else None,
        "new_skus_mtd": new_skus,
        "pending_approval": len(items.filtered(lambda i: i.state == "in_review")),
        "model_compatibility": device_models,
        "bilingual_content": round(bilingual / len(items) * 100.0, 1) if items else None,
        # measured extras (not in the registry strip)
        "catalogue_items": len(items),
        "services": len(services),
        "fault_codes": fault_codes,
        "published": published,
        "deprecated": deprecated,
    }


class P03CatalogueApi(http.Controller):
    @http.route("/p03/catalogue/kpis", type="jsonrpc", auth="user", readonly=True)
    def catalogue_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M37": kpis(request.env)}
