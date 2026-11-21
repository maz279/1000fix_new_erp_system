# The commercial document editor endpoints (17 Nov 2026).
#
# One line standard for the estimate, quotation, local proforma and tax
# invoice (cd_catalogue fix.commercial.line.mixin): these routes serve the
# editors - the part-number / charge-code search popup, the customer search
# over the whole party master (the M20 list held only already-invoiced
# customers), and a VAT preview that runs M51's determination exactly as the
# saved invoice will, without writing anything.
from datetime import date as _date
from decimal import Decimal
from types import SimpleNamespace

from odoo import fields, http
from odoo.addons.cd_billing_engine.models.fix_billing_engine import allocate_discount
from odoo.addons.cd_catalogue.models.fix_commercial_line import (
    CUSTOMER_CATEGORIES,
    LINE_TYPES,
    line_kind,
)
from odoo.addons.cd_tax_engine_bd.models.statutory_format import amount_in_words
from odoo.exceptions import UserError
from odoo.http import request

# A02 ERP audit X-17: the A02 document payload builders (report.* models,
# registered with this module when its controllers load; nothing in the models
# package depends on them).
from ..models import p03_a02_documents  # noqa: F401
from .p03_service_order_api import _require_internal, _user_error

SEARCH_LIMIT = 40

# A02 pass 2 (M01-01/M01-11): a service order's printable documents, by the
# variant the workspace asks for. "a4" (the default) is the job sheet.
SERVICE_ORDER_DOCUMENTS = {
    "a4": "cd_doc_suite.report_service_order",
    "jobsheet": "cd_doc_suite.report_service_order",
    "jobcard": "cd_service_order.report_jobcard",
    "challan": "cd_doc_suite.report_delivery_challan",
    "gatepass": "cd_doc_suite.report_delivery_challan",
    "service_report": "cd_doc_suite.report_service_report",
}


def _money(value):
    return round(float(value or 0.0), 2)


def _item_row(product, with_stock=True):
    """The popup row of an inventory item or charge code."""
    stock = product._fix_is_stock_item()
    on_hand = None
    if with_stock and stock and "qty_available" in product._fields:
        try:
            on_hand = product.qty_available
        except Exception:  # a stock read never breaks the search
            on_hand = None
    code = product.default_code or ""
    parts = ["[%s] %s" % (code, product.name) if code else product.name]
    if stock:
        parts.append("on hand %s" % ("-" if on_hand is None else "%g" % on_hand))
    if product.lst_price:
        parts.append("BDT %s" % format(product.lst_price, ",.2f"))
    return {
        "id": product.id,
        "label": " · ".join(parts),
        "code": code,
        "name": product.name,
        "uom": product.uom_id.name or "",
        "uom_id": product.uom_id.id or False,
        "price": product.lst_price or 0.0,
        "kind": "stock" if stock else "charge",
        "line_type": product._fix_line_type_for(),
        "on_hand": on_hand,
    }


class P03CommercialDocs(http.Controller):
    @http.route("/p03/doc/meta", type="jsonrpc", auth="user", readonly=True)
    def doc_meta(self, **kw):
        _require_internal(request.env)
        env = request.env
        methods = env["fix.payment.method"].search([]) if "fix.payment.method" in env else []
        return {
            "line_types": [
                {"key": k, "label": label, "kind": line_kind(k)} for k, label in LINE_TYPES
            ],
            "categories": [{"key": k, "label": label} for k, label in CUSTOMER_CATEGORIES],
            "uoms": [{"id": u.id, "label": u.name} for u in env["uom.uom"].search([], limit=80)],
            "payment_methods": [{"id": m.id, "label": m.name} for m in methods],
            "walk_in_id": env.ref("cd_billing_engine.partner_walk_in", raise_if_not_found=False).id
            if env.ref("cd_billing_engine.partner_walk_in", raise_if_not_found=False)
            else False,
        }

    @http.route("/p03/doc/items", type="jsonrpc", auth="user", readonly=True)
    def doc_items(self, q="", kind=None, line_type=None, limit=SEARCH_LIMIT, **kw):
        """Inventory items (stock lines) or charge codes (charge lines) by
        part number / code / name / barcode."""
        _require_internal(request.env)
        env = request.env
        if line_type and not kind:
            kind = line_kind(line_type)
        domain = [("sale_ok", "=", True)]
        if kind == "stock":
            domain.append(("is_storable", "=", True))
        elif kind == "charge":
            domain.append(("type", "=", "service"))
        term = (q or "").strip()
        if term:
            domain += [
                "|",
                "|",
                "|",
                ("default_code", "ilike", term),
                ("name", "ilike", term),
                ("barcode", "ilike", term),
                ("product_tmpl_id.manufacturer_part_number", "ilike", term),
            ]
        products = env["product.product"].search(
            domain, limit=min(int(limit or SEARCH_LIMIT), 80), order="default_code, id"
        )
        return {"choices": [_item_row(p) for p in products]}

    @http.route("/p03/doc/item", type="jsonrpc", auth="user", readonly=True)
    def doc_item(self, item_id=None, **kw):
        _require_internal(request.env)
        product = request.env["product.product"].browse(int(item_id or 0)).exists()
        return {"item": _item_row(product) if product else None}

    @http.route("/p03/doc/customers", type="jsonrpc", auth="user", readonly=True)
    def doc_customers(self, q="", limit=SEARCH_LIMIT, **kw):
        """Every usable party, by name, phone, BIN or legacy code."""
        _require_internal(request.env)
        env = request.env
        domain = [("party_status", "not in", ("merged", "blacklisted", "blocked"))]
        term = (q or "").strip()
        if term:
            domain += [
                "|",
                "|",
                "|",
                ("name", "ilike", term),
                ("phone", "ilike", term),
                ("vat", "ilike", term),
                ("legacy_reference", "ilike", term),
            ]
        partners = env["res.partner"].search(
            domain, limit=min(int(limit or SEARCH_LIMIT), 80), order="name"
        )
        rows = []
        for p in partners:
            bits = [p.name]
            if p.phone:
                bits.append(p.phone)
            if p.vat:
                bits.append("BIN " + p.vat)
            rows.append({"id": p.id, "label": " · ".join(bits)})
        walk = env.ref("cd_billing_engine.partner_walk_in", raise_if_not_found=False)
        if walk and not term:
            rows.insert(0, {"id": walk.id, "label": walk.name + " (counter, not registered)"})
        return {"choices": rows}

    @http.route("/p03/doc/customer", type="jsonrpc", auth="user", readonly=True)
    def doc_customer(self, customer_id=None, **kw):
        """What the header defaults to for a picked customer."""
        _require_internal(request.env)
        env = request.env
        partner = env["res.partner"].browse(int(customer_id or 0)).exists()
        if not partner:
            return {"customer": None}
        Mixin = env["fix.commercial.document.mixin"]
        walk_in = partner == Mixin._fix_walk_in_partner()
        address = ", ".join(
            x
            for x in (
                partner.street,
                partner.street2,
                partner.city,
                partner.country_id.name if partner.country_id else "",
            )
            if x
        )
        return {
            "customer": {
                "id": partner.id,
                "name": partner.name,
                "walk_in": walk_in,
                "category": Mixin._fix_category_for_partner(partner),
                "phone": "" if walk_in else partner.phone or "",
                "address": "" if walk_in else address,
                "bin": "" if walk_in else partner.vat or "",
            }
        }

    @http.route("/p03/doc/preview", type="jsonrpc", auth="user", readonly=True)
    def doc_preview(self, lines=None, overall_discount=0.0, invoice_date=None, **kw):
        """The footer of an unsaved document: each line's amount, discount,
        VAT (M51) and total, and the document totals in figures and words.
        Nothing is written."""
        _require_internal(request.env)
        env = request.env
        Line = env["fix.ar.invoice.line"]
        Product = env["product.product"]
        try:
            on_date = _date.fromisoformat(str(invoice_date)[:10]) if invoice_date else None
        except ValueError:
            on_date = None
        frame = SimpleNamespace(
            invoice_date=on_date or fields.Date.context_today(Line), company_id=env.company
        )
        priced = []
        for raw in lines or []:
            vals = {
                "quantity": float(raw.get("quantity") or 0.0),
                "unit_price": float(raw.get("unit_price") or 0.0),
                "discount_pct": float(raw.get("discount_pct") or 0.0),
                "description": raw.get("description") or "",
            }
            priced.append((raw, vals))
        # the overall discount spread exactly as create_manual_invoice does
        nets = []
        for _raw, vals in priced:
            gross = round(vals["quantity"] * vals["unit_price"], 2)
            nets.append(Decimal(str(round(gross - gross * vals["discount_pct"] / 100.0, 2))))
        overall = Decimal(str(overall_discount or 0.0))
        out, errors = [], []
        if overall > 0 and nets and overall > sum(nets, Decimal("0")):
            errors.append("The overall discount exceeds the lines.")
            overall = Decimal("0")
        shares = allocate_discount(nets, overall) if nets else []
        totals = {"items": 0, "quantity": 0.0, "gross": 0.0, "discount": 0.0}
        totals.update({"taxable": 0.0, "vat": 0.0, "total": 0.0})
        for (raw, vals), share in zip(priced, shares, strict=True):
            vals["_extra_discount"] = float(share)
            try:
                Line._fix_price_inputs(vals)
                product = Product.browse(int(raw.get("product_id") or 0)).exists()
                det = Line._fix_determined(
                    frame,
                    0.0,
                    product,
                    env["fix.vat.treatment"],
                    qty=vals["quantity"],
                    unit_price=vals["unit_price"],
                    discount=vals["discount_amount"],
                )
                row = {
                    "gross": _money(vals["gross_amount"]),
                    "discount": _money(vals["discount_amount"]),
                    "taxable": _money(det.taxable_amount),
                    "vat_rate": float(det.rate),
                    "vat": _money(det.vat_amount),
                    "total": _money(det.line_total),
                    "error": "",
                }
            except UserError as exc:
                row = {"gross": 0, "discount": 0, "taxable": 0, "vat_rate": 0, "vat": 0}
                row.update({"total": 0, "error": _user_error(exc)})
                errors.append(row["error"])
            out.append(row)
            if vals["quantity"] or vals["unit_price"]:
                totals["items"] += 1
            totals["quantity"] += vals["quantity"]
            for key in ("gross", "discount", "taxable", "vat", "total"):
                totals[key] = _money(totals[key] + row[key])
        words = ""
        try:
            words = amount_in_words(totals["total"]) if totals["total"] else ""
        except Exception:  # words never break the preview
            words = ""
        return {"lines": out, "totals": totals, "words": words, "errors": errors}

    @http.route("/p03/doc/print_url", type="jsonrpc", auth="user", readonly=True)
    def doc_print_url(self, model=None, record_id=None, variant=None, **kw):
        """The PDF of a customer document (opened inline in a new tab): the A4
        document, or variant "receipt" - the 80 mm thermal receipt."""
        _require_internal(request.env)
        reports = {
            "fix.ar.invoice": "cd_doc_suite.report_invoice",
            "fix.sales.proforma": "cd_doc_suite.report_sales_proforma",
            "fix.quotation": "cd_doc_suite.report_quotation",
            "fix.estimate": "cd_doc_suite.report_estimate",
            "fix.purchase.order": "cd_doc_suite.report_po",
            "fix.vendor.invoice": "cd_doc_suite.report_vendor_bill",
            # A02 ERP audit X-17: the A02 documents (report/p03_a02_documents.xml)
            "fix.counter.sale": "cd_p03_portal.report_a02_counter_receipt",
            "fix.data.wipe.certificate": "cd_p03_portal.report_a02_wipe_certificate",
            # A02 pass 2 M06-10: intake receipt, custody form, hand-over receipt;
            # and the quotation the customer accepts
            "fix.data.recovery.case": "cd_p03_portal.report_a02_data_case",
            "fix.data.quote": "cd_p03_portal.report_a02_data_quote",
            "fix.field.order": "cd_p03_portal.report_a02_field_service",
            "fix.consignment": "cd_p03_portal.report_a02_consignment_note",
            "fix.workshop.job": "cd_p03_portal.report_a02_workshop_job",
            # A04 ERP audit M08-F20: the contract printout (cd_contract_core)
            "fix.contract": "cd_contract_core.report_contract_document",
        }
        receipts = {
            "fix.ar.invoice": "cd_doc_suite.report_invoice_receipt",
            "fix.sales.proforma": "cd_doc_suite.report_sales_proforma_receipt",
            "fix.quotation": "cd_doc_suite.report_quotation_receipt",
            "fix.estimate": "cd_doc_suite.report_estimate_receipt",
            "fix.counter.sale": "cd_p03_portal.report_a02_counter_receipt_80",
        }
        name = (receipts if variant == "receipt" else reports).get(model or "")
        if model == "fix.service.order":
            # A02 pass 2 (M01-01/M01-11): the order's server documents. The
            # job card is cd_service_order's (no VAT, no Mushak wording: the
            # tax invoice is M20's Mushak 6.3); the job sheet is the customer
            # copy, the challan doubles as the gate pass.
            name = SERVICE_ORDER_DOCUMENTS.get(variant or "a4")
        if not name or not record_id:
            return {"url": ""}
        if model not in request.env:
            return {"url": ""}
        record = request.env[model].browse(int(record_id)).exists()
        if not record:
            return {"url": ""}
        record.check_access("read")
        return {"url": "/report/pdf/%s/%s" % (name, record.id)}
