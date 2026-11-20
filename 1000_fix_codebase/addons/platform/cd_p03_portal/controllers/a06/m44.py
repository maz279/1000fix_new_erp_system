# A06 · M44 Import, Trade Compliance & Landed Cost — surfaces, packs and KPIs
# over import orders, proforma/LC/LCA, HS classification, IRC, shipping
# documents, arrivals, bills of entry (duty cascade) and landed-cost sheets.
#
# A06 workflow audit (2026-11-03), M44-6 and M44-15: every transition the
# screens need is declared here (the approvals check the role and the
# segregation of duties server-side); packs and KPIs read as the CALLER,
# filtered to the companies the caller has selected, never sudo().search([]).
import datetime

from odoo import fields

SURFACES = {
    "fix.import.order": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # the import purchase order raised from a draft import order (M16 link)
        "actions": {"action_receive", "action_close", "action_create_purchase_order"},
    },
    "fix.import.advance": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_request", "action_approve", "action_reject", "action_cancel"},
    },
    "fix.import.proforma": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.import.lc": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_apply",
            "action_request_approval",
            "action_recall_approval",
            "action_open",
            "action_close",
        },
    },
    "fix.import.lca": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_approve", "action_reject"},
    },
    "fix.import.hs": {
        "order": "hs_code",
        "limit": 300,
        "actions": {"action_rule", "action_reopen"},
    },
    "fix.import.irc": {
        "order": "valid_to desc, id desc",
        "limit": 100,
        "actions": {"action_suspend", "action_reinstate"},
    },
    "fix.import.shipdoc": {
        "order": "received_on desc, id desc",
        "limit": 300,
        "actions": {"action_receive", "action_verify"},
    },
    "fix.import.arrival": {
        "order": "eta desc, id desc",
        "limit": 200,
        "actions": {"action_arrive", "action_clear"},
    },
    "fix.import.boe": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_assess",
            "action_accept_variance",
            "action_cancel_assessed",
            "action_pay",
            "action_reverse",
        },
    },
    "fix.import.boe.line": {"order": "boe_id, id", "limit": 400, "actions": set()},
    "fix.import.landed": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_pull_costs", "action_post_estimate", "action_finalise"},
    },
    "fix.import.tariff": {
        "order": "hs_code, date_from desc",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.import.lc.amendment": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_apply_amendment",
            "action_cancel",
        },
    },
    "fix.import.lc.payment": {
        "order": "payment_date desc, id desc",
        "limit": 200,
        "actions": {"action_link_boe"},
    },
    "fix.import.restriction": {
        "order": "hs_code_pattern, date_from desc",
        "limit": 300,
        "actions": {"action_activate", "action_retire"},
    },
    "fix.import.permit": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": {"action_verify", "action_revoke"},
    },
    "fix.import.cnf.agent": {
        "order": "name",
        "limit": 200,
        "actions": {"action_approve", "action_block", "action_unblock"},
    },
    "fix.import.insurance": {
        "order": "cover_to desc, id desc",
        "limit": 300,
        "actions": {"action_verify", "action_cancel"},
    },
    # capture audit 2026-11-16: cost documents (BRU-ITC-16), LC discrepancies
    # (FR-ITC-016) and customs queries (FR-ITC-028)
    "fix.import.cost": {
        "order": "incurred_on desc, id desc",
        "limit": 300,
        "actions": {"action_reconcile", "action_reject"},
    },
    "fix.import.lc.discrepancy": {
        "order": "raised_on desc, id desc",
        "limit": 200,
        "actions": {"action_accept", "action_refuse"},
    },
    "fix.import.customs.query": {
        "order": "raised_on desc, id desc",
        "limit": 200,
        "actions": {"action_answer", "action_resolve"},
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
        "empty": empty,
    }


def _scoped(env, model, domain=None, order=None):
    """Records of `model` the caller may read, in the caller's companies."""
    return env[model].search(
        [("company_id", "in", env.companies.ids)] + (domain or []), order=order
    )


def _dated(field, date_from=None, date_to=None):
    """M44-25: the report's date range as a domain on `field`."""
    domain = []
    if date_from:
        domain.append((field, ">=", date_from))
    if date_to:
        domain.append((field, "<=", date_to))
    return domain


def _dhaka_today():
    """M44-25: KPIs count Dhaka business days, not UTC ones."""
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=6)).date()


def _orders(env):
    return _scoped(env, "fix.import.order")


def _label(rec, fname):
    return dict(rec._fields[fname]._description_selection(rec.env)).get(
        rec[fname], rec[fname] or "—"
    )


def incoterms_fx(env, date_from=None, date_to=None, **params):
    rows = []
    for order in _orders(env):
        rows.append(
            {
                "order": order.name,
                "supplier": order.supplier_id.name if order.supplier_id else "—",
                "incoterm": _label(order, "incoterm"),
                "mode": _label(order, "shipment_mode"),
                "currency": order.currency_id.name,
                "fob": round(order.fob_value or 0.0, 2),
                "fx_rate": order.fx_rate or 0.0,
                "fx_source": order.fx_rate_source or "—",
                "local_fob": round((order.fob_value or 0.0) * (order.fx_rate or 0.0), 2),
                "state": _label(order, "state"),
            }
        )
    rows.sort(key=lambda r: -r["local_fob"])
    return _pack(
        "Incoterms & FX — FOB expressed at the recorded commitment rate",
        [
            "order",
            "supplier",
            "incoterm",
            "mode",
            "currency",
            "fob",
            "fx_rate",
            "fx_source",
            "local_fob",
            "state",
        ],
        {
            "order": "Order",
            "supplier": "Supplier",
            "incoterm": "Incoterm",
            "mode": "Mode",
            "currency": "Currency",
            "fob": "FOB",
            "fx_rate": "FX Rate",
            "fx_source": "Rate Source",
            "local_fob": "Local FOB (BDT)",
            "state": "State",
        },
        rows,
        [
            "Local FOB = FOB × the commitment FX rate recorded on the order with its source "
            "(BRU-ITC-14). The rate is pinned once the proforma is approved."
        ],
        totals={"order": "Total", "local_fob": round(sum(r["local_fob"] for r in rows), 2)},
        empty="No import orders yet.",
    )


def duty_cascade(env, date_from=None, date_to=None, **params):
    rows = []
    for line in _scoped(env, "fix.import.boe.line", _dated("boe_id.boe_date", date_from, date_to)):
        rows.append(
            {
                "boe": line.boe_id.boe_no,
                "state": _label(line.boe_id, "state"),
                "hs": line.hs_id.hs_code if line.hs_id else "—",
                "description": line.description or line.order_line_id.part_id.display_name or "—",
                "assessable": round(line.assessable_value or 0.0, 2),
                "cd": round(line.cd_amount, 2),
                "rd": round(line.rd_amount, 2),
                "sd": round(line.sd_amount, 2),
                "vat": round(line.vat_amount, 2),
                "at": round(line.at_amount, 2),
                "ait": round(line.ait_amount, 2),
                "total": round(
                    sum(
                        line[f]
                        for f in (
                            "cd_amount",
                            "rd_amount",
                            "sd_amount",
                            "vat_amount",
                            "at_amount",
                            "ait_amount",
                        )
                    ),
                    2,
                ),
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return _pack(
        "Duty & Tax Cascade — CD / RD / SD / VAT / AT / AIT",
        [
            "boe",
            "state",
            "hs",
            "description",
            "assessable",
            "cd",
            "rd",
            "sd",
            "vat",
            "at",
            "ait",
            "total",
        ],
        {
            "boe": "BOE",
            "state": "State",
            "hs": "HS",
            "description": "Description",
            "assessable": "Assessable Value",
            "cd": "CD",
            "rd": "RD",
            "sd": "SD",
            "vat": "VAT",
            "at": "AT",
            "ait": "AIT",
            "total": "Total",
        },
        rows,
        [
            "FR-ITC-033: AV = CIF × FX + landing charge; CD, RD and AIT on AV; SD on "
            "AV + CD + RD; VAT on AV + CD + RD + SD; AT on AV + CD + SD. Rates come from the "
            "tariff row in force on the lodgement date and are frozen at assessment.",
            "CD, RD and SD are capitalised into landed cost; import VAT and AT are input tax; "
            "AIT is a tax advance.",
        ],
        totals={
            "boe": "Total",
            "assessable": round(sum(r["assessable"] for r in rows), 2),
            "total": round(sum(r["total"] for r in rows), 2),
        },
        empty="No bill-of-entry lines yet.",
    )


def landed_cost_by_shipment(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _scoped(env, "fix.import.landed", _dated("create_date", date_from, date_to)):
        goods = sum(ln._goods_value_bdt() for ln in rec.order_id.line_ids)
        rows.append(
            {
                "sheet": rec.name,
                "type": _label(rec, "sheet_type"),
                "order": rec.order_id.name,
                "freight": round(rec.freight, 2),
                "insurance": round(rec.insurance, 2),
                "duty": round(rec.duty, 2),
                "clearing": round(rec.clearing_charges, 2),
                # M44-24: LC and bank charges are part of the landed cost
                "bank": round(rec.bank_charges, 2),
                "landed": round(rec.total_landed, 2),
                "pct_of_goods": round((rec.total_landed / goods) * 100.0, 1) if goods else 0.0,
                "state": _label(rec, "state"),
            }
        )
    rows.sort(key=lambda r: -r["landed"])
    final = [r for r in rows if r["state"] == "Finalised"]
    return _pack(
        "Landed Cost by Shipment — inventoriable charges against the goods value",
        [
            "sheet",
            "type",
            "order",
            "freight",
            "insurance",
            "duty",
            "clearing",
            "bank",
            "landed",
            "pct_of_goods",
            "state",
        ],
        {
            "sheet": "Sheet",
            "type": "Type",
            "order": "Order",
            "freight": "Freight",
            "insurance": "Insurance",
            "duty": "Duty (CD+RD+SD)",
            "clearing": "Clearing",
            "bank": "LC & Bank Charges",
            "landed": "Total Landed",
            "pct_of_goods": "% of Goods (BDT)",
            "state": "State",
        },
        rows,
        [
            "Total landed = freight + insurance + CD + RD + SD + clearing + LC/bank charges. "
            "Import VAT, AT and "
            "AIT are recoverable and never in landed cost (BRU-ITC-02). The total row counts "
            "finalised sheets only."
        ],
        totals={"sheet": "Total (finalised)", "landed": round(sum(r["landed"] for r in final), 2)},
        empty="No landed-cost sheets yet.",
    )


def cycle_time(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _scoped(env, "fix.import.arrival"):
        transit = "—"
        clearance = "—"
        if rec.etd and rec.arrival_date:
            transit = (rec.arrival_date - rec.etd).days
        if rec.arrival_date and rec.cleared_on:
            clearance = (rec.cleared_on - rec.arrival_date).days
        rows.append(
            {
                "shipment": rec.name,
                "order": rec.order_id.name,
                "vessel": rec.vessel or "—",
                "etd": str(rec.etd) if rec.etd else "—",
                "arrival": str(rec.arrival_date) if rec.arrival_date else "—",
                "cleared": str(rec.cleared_on) if rec.cleared_on else "—",
                "transit_days": transit,
                "clearance_days": clearance,
                "state": _label(rec, "state"),
            }
        )
    rows.sort(key=lambda r: str(r["arrival"]), reverse=True)
    return _pack(
        "Cycle-Time Analysis — transit and clearance days",
        [
            "shipment",
            "order",
            "vessel",
            "etd",
            "arrival",
            "cleared",
            "transit_days",
            "clearance_days",
            "state",
        ],
        {
            "shipment": "Shipment",
            "order": "Order",
            "vessel": "Vessel",
            "etd": "ETD",
            "arrival": "Arrival",
            "cleared": "Cleared",
            "transit_days": "Transit",
            "clearance_days": "Clearance",
            "state": "State",
        },
        rows,
        ["Transit = arrival − ETD; clearance = cleared − arrival. Open stages show '—'."],
        empty="No shipments recorded yet.",
    )


def demurrage_avoidance(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _scoped(env, "fix.import.arrival"):
        rows.append(
            {
                "shipment": rec.name,
                "order": rec.order_id.name,
                "port": rec.port,
                "arrival": str(rec.arrival_date) if rec.arrival_date else "—",
                "cleared": str(rec.cleared_on) if rec.cleared_on else "—",
                "free_days": rec.free_days,
                "demurrage_days": rec.demurrage_days,
                "exposure": "yes" if (rec.demurrage_days or 0) > 0 else "no",
                "state": _label(rec, "state"),
            }
        )
    rows.sort(key=lambda r: -r["demurrage_days"])
    exposed = len([r for r in rows if r["demurrage_days"] > 0])
    return _pack(
        "Demurrage Avoidance — port days beyond the free time",
        [
            "shipment",
            "order",
            "port",
            "arrival",
            "cleared",
            "free_days",
            "demurrage_days",
            "exposure",
            "state",
        ],
        {
            "shipment": "Shipment",
            "order": "Order",
            "port": "Port",
            "arrival": "Arrival",
            "cleared": "Cleared",
            "free_days": "Free Days",
            "demurrage_days": "Demurrage Days",
            "exposure": "Exposure",
            "state": "State",
        },
        rows,
        [
            "Demurrage = max((release or today) − actual arrival − free days, 0), computed on "
            "every read (BRU-ITC-17). %d shipment(s) exposed." % exposed
        ],
        totals={"shipment": "Total", "demurrage_days": sum(r["demurrage_days"] for r in rows)},
        empty="No shipments recorded yet.",
    )


def _open_fx_orders(env):
    bdt = env.ref("base.BDT")
    return _orders(env).filtered(
        lambda o: o.currency_id != bdt and o.state not in ("received", "landed", "closed")
    )


def fx_exposure(env, date_from=None, date_to=None, **params):
    """The BDT value of open foreign-currency commitments at the recorded
    rate. The audit's 'exposure' (FOB × (rate − 1)) measured nothing."""
    rows = []
    for order in _open_fx_orders(env):
        value = order._invoice_value()
        rows.append(
            {
                "order": order.name,
                "supplier": order.supplier_id.name if order.supplier_id else "—",
                "currency": order.currency_id.name,
                "value": round(value, 2),
                "fx_rate": order.fx_rate or 0.0,
                "fx_source": order.fx_rate_source or "—",
                "commitment_bdt": round(value * (order.fx_rate or 0.0), 2),
                "state": _label(order, "state"),
            }
        )
    rows.sort(key=lambda r: -r["commitment_bdt"])
    return _pack(
        "Open FX Commitments — foreign-currency orders not yet received",
        [
            "order",
            "supplier",
            "currency",
            "value",
            "fx_rate",
            "fx_source",
            "commitment_bdt",
            "state",
        ],
        {
            "order": "Order",
            "supplier": "Supplier",
            "currency": "Currency",
            "value": "Invoice Value",
            "fx_rate": "Commitment Rate",
            "fx_source": "Rate Source",
            "commitment_bdt": "Commitment (BDT)",
            "state": "State",
        },
        rows,
        [
            "Commitment = the invoice value under the incoterm × the commitment rate recorded "
            "on the order. It is the BDT at risk to a rate move, not a forward valuation."
        ],
        totals={
            "order": "Total",
            "commitment_bdt": round(sum(r["commitment_bdt"] for r in rows), 2),
        },
        empty="No open foreign-currency import order.",
    )


def cnf_management(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in _scoped(env, "fix.import.arrival"):
        landed = _scoped(
            env,
            "fix.import.landed",
            [("order_id", "=", rec.order_id.id), ("sheet_type", "=", "final")],
        )[:1]
        rows.append(
            {
                "shipment": rec.name,
                "order": rec.order_id.name,
                "port": rec.port,
                "agent": rec.cnf_agent_id.name or "—",
                "clearing_charges": round(landed.clearing_charges, 2) if landed else 0.0,
                "demurrage_days": rec.demurrage_days,
                "release": rec.release_ref or "—",
                "state": _label(rec, "state"),
            }
        )
    rows.sort(key=lambda r: -r["clearing_charges"])
    return _pack(
        "C&F Management — clearing charges per shipment",
        [
            "shipment",
            "order",
            "port",
            "agent",
            "clearing_charges",
            "demurrage_days",
            "release",
            "state",
        ],
        {
            "shipment": "Shipment",
            "order": "Order",
            "port": "Port",
            "agent": "C&F Agent",
            "clearing_charges": "Clearing Charges",
            "demurrage_days": "Demurrage Days",
            "release": "Release Order",
            "state": "State",
        },
        rows,
        [
            "Clearing charges come from the shipment's final landed-cost sheet; the agent is "
            "the licensed C&F agent named on the clearance (BRU-ITC-12)."
        ],
        totals={
            "shipment": "Total",
            "clearing_charges": round(sum(r["clearing_charges"] for r in rows), 2),
        },
        empty="No shipments recorded yet.",
    )


def boe_remittance(env, date_from=None, date_to=None, **params):
    """Scorecard 25: every live Bill of Entry against the LC payments linked to
    it, and every LC payment with no Bill of Entry."""
    from odoo.addons.cd_import_order.models.fix_import_common import (
        PARAM_BOE_REMITTANCE_DAYS,
        param_float,
    )

    days = int(param_float(env, PARAM_BOE_REMITTANCE_DAYS, 120.0))
    day = fields.Date.context_today(env["fix.import.boe"])
    rows = []
    for bill in _scoped(env, "fix.import.boe", [("state", "in", ("assessed", "paid"))]):
        payments = env["fix.import.lc.payment"].search([("boe_id", "=", bill.id)])
        age = (day - bill.boe_date).days if bill.boe_date else 0
        rows.append(
            {
                "kind": "Bill of Entry",
                "ref": bill.boe_no,
                "order": bill.order_id.name,
                "on": str(bill.boe_date or "—"),
                "age_days": age,
                "matched": ", ".join(payments.mapped("reference")) or "—",
                "paid_bdt": round(sum(payments.mapped("amount_bdt")), 2),
                "status": "Matched"
                if payments
                else ("Overdue" if age > days else "Awaiting remittance"),
            }
        )
    for pay in _scoped(env, "fix.import.lc.payment", [("boe_id", "=", False)]):
        age = (day - pay.payment_date).days if pay.payment_date else 0
        rows.append(
            {
                "kind": "LC payment",
                "ref": pay.reference,
                "order": pay.lc_id.order_id.name,
                "on": str(pay.payment_date or "—"),
                "age_days": age,
                "matched": "—",
                "paid_bdt": round(pay.amount_bdt, 2),
                "status": "Overdue" if age > days else "Awaiting Bill of Entry",
            }
        )
    rows.sort(key=lambda r: (r["status"] != "Overdue", -r["age_days"]))
    overdue = len([r for r in rows if r["status"] == "Overdue"])
    return _pack(
        "Bill of Entry to Remittance — %d overdue" % overdue,
        ["kind", "ref", "order", "on", "age_days", "matched", "paid_bdt", "status"],
        {
            "kind": "Document",
            "ref": "Reference",
            "order": "Import",
            "on": "Date",
            "age_days": "Age (days)",
            "matched": "Matched To",
            "paid_bdt": "Remitted (BDT)",
            "status": "Status",
        },
        rows,
        [
            "Overdue = no match after %d days (cd_import_order.boe_remittance_match_days). The "
            "default of 120 days stands for Bangladesh Bank's 4-month Bill of Entry guideline; "
            "Finance confirms it. A daily job flags each overdue document once. An import paid by "
            "advance has no LC payment to link and shows here until treasury's payment is matched "
            "outside M44." % days
        ],
        empty="No assessed or paid Bill of Entry and no LC payment yet.",
    )


CHECKLIST_DOCS = (
    ("bl", "Bill of Lading"),
    ("invoice", "Commercial Invoice"),
    ("packing", "Packing List"),
    ("coo", "Certificate of Origin"),
    ("insurance", "Insurance Certificate"),
)


def _doc_status(docs):
    """The best status among the documents of one type on an order."""
    if not docs:
        return "Missing"
    for state, text in (("verified", "Verified"), ("received", "Received"), ("pending", "Pending")):
        hit = docs.filtered(lambda d, s=state: d.state == s)
        if hit:
            return "%s (file)" % text if hit.filtered("document") else "%s (no file)" % text
    return "Missing"


def document_checklist(env, date_from=None, date_to=None, **params):
    """Scorecard 28: which documents each order's ASYCUDA / BSW pack holds."""
    from odoo.addons.cd_import_order.models.fix_import_common import PARAM_BOE_DOCS, param

    raw = param(env, PARAM_BOE_DOCS) or "bl,invoice,packing"
    required = [d.strip() for d in raw.split(",") if d.strip()]
    labels = dict(CHECKLIST_DOCS)
    rows = []
    for order in _orders(env):
        docs = env["fix.import.shipdoc"].search([("order_id", "=", order.id)])
        row = {"order": order.name, "state": _label(order, "state")}
        for code, _text in CHECKLIST_DOCS:
            row[code] = _doc_status(docs.filtered(lambda d, c=code: d.doc_type == c))
        missing = [
            labels.get(code, code)
            for code in required
            if not docs.filtered(lambda d, c=code: d.doc_type == c and d.state != "pending")
        ]
        bills = order.boe_ids.filtered(lambda b: b.state != "reversed")
        row["boe"] = ", ".join(bills.mapped("boe_no")) or "—"
        row["asycuda"] = ", ".join(filter(None, bills.mapped("asycuda_ref"))) or "—"
        row["missing"] = ", ".join(missing) or "—"
        row["pack"] = "Incomplete" if missing else "Complete"
        rows.append(row)
    rows.sort(key=lambda r: (r["pack"] == "Complete", r["order"]))
    incomplete = len([r for r in rows if r["pack"] == "Incomplete"])
    return _pack(
        "Document Checklist — ASYCUDA and BSW document pack, %d incomplete" % incomplete,
        [
            "order",
            "state",
            "bl",
            "invoice",
            "packing",
            "coo",
            "insurance",
            "boe",
            "asycuda",
            "missing",
            "pack",
        ],
        {
            "order": "Import",
            "state": "State",
            "bl": "B/L",
            "invoice": "Invoice",
            "packing": "Packing List",
            "coo": "Origin Cert.",
            "insurance": "Insurance",
            "boe": "Bill of Entry",
            "asycuda": "ASYCUDA Ref",
            "missing": "Missing (required)",
            "pack": "Pack",
        },
        rows,
        [
            "This is a checklist and document pack, not a live ASYCUDA or BSW integration: nothing "
            "is sent to or read from customs, and the ASYCUDA reference is typed from the "
            "assessment notice. Required documents come from "
            "cd_import_order.boe_required_documents. Files are attached on each shipping document."
        ],
        empty="No import orders yet.",
    )


REPORTS = {
    "boe_remittance": boe_remittance,
    "document_checklist": document_checklist,
    "incoterms_fx": incoterms_fx,
    "duty_cascade": duty_cascade,
    "landed_cost_by_shipment": landed_cost_by_shipment,
    "cycle_time": cycle_time,
    "demurrage_avoidance": demurrage_avoidance,
    "fx_exposure": fx_exposure,
    "cnf_management": cnf_management,
}


def kpis(env):
    """As the caller, in the caller's companies (M44-15)."""
    orders = _orders(env)
    lcs = _scoped(env, "fix.import.lc")
    boes = _scoped(env, "fix.import.boe")
    arrivals = _scoped(env, "fix.import.arrival", [("state", "!=", "cleared")])
    today = _dhaka_today()
    month_start = today.replace(day=1)
    landed = _scoped(
        env,
        "fix.import.landed",
        [
            ("sheet_type", "=", "final"),
            ("state", "=", "finalised"),
            ("finalised_on", ">=", month_start),
        ],
    )
    commitment = sum(o._invoice_value() * (o.fx_rate or 0.0) for o in _open_fx_orders(env))
    return {
        "open_imports": len(
            orders.filtered(lambda o: o.state not in ("received", "landed", "closed"))
        ),
        "lc_open": len(lcs.filtered(lambda ln: ln.state in ("applied", "opened", "amended"))),
        "boe_unpaid": len(boes.filtered(lambda b: b.state in ("draft", "assessed"))),
        "demurrage_days": sum(rec.demurrage_days or 0 for rec in arrivals),
        "landed_mtd": round(sum(landed.mapped("total_landed")), 2),
        "fx_commitment": round(commitment, 2),
    }
