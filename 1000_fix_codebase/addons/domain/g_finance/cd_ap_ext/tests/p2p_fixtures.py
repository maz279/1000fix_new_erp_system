# Shared test helper (A06 P2P, 20 Nov 2026): a non-PO bill is paid only to an
# ACTIVE supplier of the M42 register (P09, lead default), so the AP suites'
# vendors are registered the way M42 leaves an active supplier: verified
# documents, status active. Without cd_vendor_portal installed it does nothing.


def register_supplier(env, partner):
    """An active M42 supplier with verified documents for `partner` (idempotent)."""
    if "fix.supplier" not in env or not partner:
        return None
    Supplier = env["fix.supplier"].sudo()
    supplier = Supplier.search(
        [("partner_id", "=", partner.id), ("company_id", "=", env.company.id)], limit=1
    )
    if supplier:
        return supplier
    supplier = Supplier.create({"name": partner.name, "partner_id": partner.id, "status": "active"})
    for doc_type in ("trade_licence", "tin", "vat"):
        env["fix.supplier.document"].sudo().create(
            {"supplier_id": supplier.id, "doc_type": doc_type, "state": "valid"}
        )
    return supplier
