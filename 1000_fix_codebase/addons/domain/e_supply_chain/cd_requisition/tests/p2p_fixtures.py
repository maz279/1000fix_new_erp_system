# Shared test helper (A06 P2P, 20 Nov 2026): the PO category gate is on by
# default (P08, lead default) and a supplier's approved categories come only
# from an approved qualification. Suites that seed an active supplier qualify
# it here for every product category (top-level categories, so child_of covers
# all) through that path. Without cd_vendor_portal installed it does nothing.


def qualify_categories(env, supplier, categories=None):
    """Approve a qualification of `supplier` for `categories` (default: all
    top-level product categories), as M42 would after its review."""
    if "fix.supplier.qualification" not in env or not supplier:
        return supplier
    env = env(su=True)
    categories = categories or env["product.category"].search([("parent_id", "=", False)])
    qual = env["fix.supplier.qualification"].create(
        {
            "supplier_id": supplier.id,
            "score": 100.0,
            "category_ids": [(6, 0, categories.ids)],
        }
    )
    qual.action_start()
    qual.action_approve()
    return supplier


def close_rfq(rfq, user=None):
    """Close an RFQ the way the bid window ends (A06 P22: it closes after its
    response deadline, not while invited suppliers may still answer)."""
    from datetime import timedelta

    from odoo import fields

    deadline = rfq.response_deadline if "response_deadline" in rfq._fields else None
    today = fields.Date.context_today(rfq)
    if deadline and deadline >= today:
        rfq.sudo()._guarded().write({"response_deadline": today - timedelta(days=1)})
    return (rfq.with_user(user) if user else rfq).action_close()
