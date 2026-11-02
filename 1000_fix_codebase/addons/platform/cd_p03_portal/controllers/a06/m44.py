# A06 · M44 Import, Trade Compliance & Landed Cost — surfaces, packs and KPIs
# over import orders, proforma/LC/LCA, HS classification, IRC, shipping
# documents, arrivals, bills of entry (duty cascade) and landed-cost sheets.
import datetime

SURFACES = {
    "fix.import.order": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_receive"},
    },
    "fix.import.proforma": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve"},
    },
    "fix.import.lc": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_apply", "action_open", "action_close"},
    },
    "fix.import.lca": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_approve"},
    },
    "fix.import.hs": {
        "order": "hs_code",
        "limit": 300,
        "actions": {"action_rule"},
    },
    "fix.import.irc": {"order": "valid_to desc, id desc", "limit": 100, "actions": set()},
    "fix.import.shipdoc": {
        "order": "received_on desc, id desc",
        "limit": 300,
        "actions": {"action_receive"},
    },
    "fix.import.arrival": {
        "order": "eta desc, id desc",
        "limit": 200,
        "actions": {"action_arrive", "action_clear"},
    },
    "fix.import.boe": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_assess", "action_pay"},
    },
    "fix.import.boe.line": {"order": "boe_id, id", "limit": 400, "actions": set()},
    "fix.import.landed": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_finalise"},
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


def _orders(env):
    return env["fix.import.order"].sudo().search([])


def incoterms_fx(env, date_from=None, date_to=None, **params):
    rows = []
    for order in _orders(env):
        rows.append(
            {
                "order": order.name,
                "supplier": order.supplier_id.name if order.supplier_id else "—",
                "incoterm": dict(order._fields["incoterm"].selection).get(order.incoterm),
                "mode": dict(order._fields["shipment_mode"].selection).get(order.shipment_mode),
                "fob": round(order.fob_value or 0.0, 2),
                "fx_rate": order.fx_rate or 1.0,
                "local_fob": round((order.fob_value or 0.0) * (order.fx_rate or 1.0), 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: -r["local_fob"])
    return _pack(
        "Incoterms & FX — FOB expressed at the recorded FX rate",
        ["order", "supplier", "incoterm", "mode", "fob", "fx_rate", "local_fob", "state"],
        {
            "order": "Order",
            "supplier": "Supplier",
            "incoterm": "Incoterm",
            "mode": "Mode",
            "fob": "FOB",
            "fx_rate": "FX Rate",
            "local_fob": "Local FOB",
            "state": "State",
        },
        rows,
        [
            "Local FOB = FOB × the recorded FX rate. The rate is a recorded input; "
            "this screen does not fetch market rates."
        ],
        totals={
            "order": "Total",
            "fob": round(sum(r["fob"] for r in rows), 2),
            "local_fob": round(sum(r["local_fob"] for r in rows), 2),
        },
        empty="No import orders yet.",
    )


def duty_cascade(env, date_from=None, date_to=None, **params):
    rows = []
    for line in env["fix.import.boe.line"].sudo().search([]):
        rows.append(
            {
                "boe": line.boe_id.name,
                "hs": line.hs_id.hs_code if line.hs_id else "—",
                "description": line.description or "—",
                "assessable": round(line.assessable_value or 0.0, 2),
                "cd": round(line.cd_amount, 2),
                "rd": round(line.rd_amount, 2),
                "sd": round(line.sd_amount, 2),
                "vat": round(line.vat_amount, 2),
                "at": round(line.at_amount, 2),
                "ait": round(line.ait_amount, 2),
                "total": round(
                    line.cd_amount
                    + line.rd_amount
                    + line.sd_amount
                    + line.vat_amount
                    + line.at_amount
                    + line.ait_amount,
                    2,
                ),
            }
        )
    rows.sort(key=lambda r: -r["total"])
    return _pack(
        "Duty & Tax Cascade — CD / RD / SD / VAT / AT / AIT",
        ["boe", "hs", "description", "assessable", "cd", "rd", "sd", "vat", "at", "ait", "total"],
        {
            "boe": "BOE",
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
            "CD/RD/AT/AIT on the assessable value; SD on the duty-inclusive value; "
            "VAT on value + CD + RD + SD — the cascade is computed per line."
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
    for rec in env["fix.import.landed"].sudo().search([]):
        fob = rec.order_id.fob_value or 0.0
        rows.append(
            {
                "sheet": rec.name,
                "order": rec.order_id.name,
                "freight": round(rec.freight, 2),
                "insurance": round(rec.insurance, 2),
                "duty": round(rec.duty, 2),
                "clearing": round(rec.clearing_charges, 2),
                "other": round(rec.other_charges, 2),
                "landed": round(rec.total_landed, 2),
                "pct_of_fob": round((rec.total_landed / fob) * 100.0, 1) if fob else 0.0,
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["landed"])
    return _pack(
        "Landed Cost by Shipment — charges against FOB",
        [
            "sheet",
            "order",
            "freight",
            "insurance",
            "duty",
            "clearing",
            "other",
            "landed",
            "pct_of_fob",
            "state",
        ],
        {
            "sheet": "Sheet",
            "order": "Order",
            "freight": "Freight",
            "insurance": "Insurance",
            "duty": "Duty",
            "clearing": "Clearing",
            "other": "Other",
            "landed": "Total Landed",
            "pct_of_fob": "% of FOB",
            "state": "State",
        },
        rows,
        [
            "Total landed = freight + insurance + duty + clearing + other; the % is "
            "against the order's recorded FOB."
        ],
        totals={"sheet": "Total", "landed": round(sum(r["landed"] for r in rows), 2)},
        empty="No landed-cost sheets yet.",
    )


def cycle_time(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in env["fix.import.arrival"].sudo().search([]):
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
                "state": dict(rec._fields["state"].selection).get(rec.state),
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
    for rec in env["fix.import.arrival"].sudo().search([]):
        rows.append(
            {
                "shipment": rec.name,
                "order": rec.order_id.name,
                "port": rec.port,
                "eta": str(rec.eta) if rec.eta else "—",
                "arrival": str(rec.arrival_date) if rec.arrival_date else "—",
                "free_days": rec.free_days,
                "demurrage_days": rec.demurrage_days,
                "exposure": "yes" if (rec.demurrage_days or 0) > 0 else "no",
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["demurrage_days"])
    demurrage = len([r for r in rows if r["demurrage_days"] > 0])
    return _pack(
        "Demurrage Avoidance — days beyond the free window",
        [
            "shipment",
            "order",
            "port",
            "eta",
            "arrival",
            "free_days",
            "demurrage_days",
            "exposure",
            "state",
        ],
        {
            "shipment": "Shipment",
            "order": "Order",
            "port": "Port",
            "eta": "ETA",
            "arrival": "Arrival",
            "free_days": "Free Days",
            "demurrage_days": "Demurrage Days",
            "exposure": "Exposure",
            "state": "State",
        },
        rows,
        ["Demurrage = max(arrival − ETA − free days, 0). %d shipment(s) exposed." % demurrage],
        totals={"shipment": "Total", "demurrage_days": sum(r["demurrage_days"] for r in rows)},
        empty="No shipments recorded yet.",
    )


def fx_exposure(env, date_from=None, date_to=None, **params):
    rows = []
    for order in _orders(env):
        rate = order.fx_rate or 1.0
        if rate == 1.0:
            continue
        fob = order.fob_value or 0.0
        rows.append(
            {
                "order": order.name,
                "supplier": order.supplier_id.name if order.supplier_id else "—",
                "fob": round(fob, 2),
                "fx_rate": rate,
                "local_fob": round(fob * rate, 2),
                "exposure": round(fob * (rate - 1.0), 2),
                "state": dict(order._fields["state"].selection).get(order.state),
            }
        )
    rows.sort(key=lambda r: -abs(r["exposure"]))
    return _pack(
        "FX Exposure — recorded rate against a parity of 1.0",
        ["order", "supplier", "fob", "fx_rate", "local_fob", "exposure", "state"],
        {
            "order": "Order",
            "supplier": "Supplier",
            "fob": "FOB",
            "fx_rate": "FX Rate",
            "local_fob": "Local FOB",
            "exposure": "Exposure",
            "state": "State",
        },
        rows,
        [
            "Exposure = FOB × (rate − 1.0) — the recorded translation difference "
            "against parity; it is not a forward-rate valuation."
        ],
        totals={"order": "Total", "exposure": round(sum(r["exposure"] for r in rows), 2)},
        empty="No order carries a non-parity FX rate.",
    )


def cnf_management(env, date_from=None, date_to=None, **params):
    rows = []
    for rec in env["fix.import.arrival"].sudo().search([]):
        landed = (
            env["fix.import.landed"].sudo().search([("order_id", "=", rec.order_id.id)], limit=1)
        )
        rows.append(
            {
                "shipment": rec.name,
                "order": rec.order_id.name,
                "port": rec.port,
                "agent": rec.order_id.supplier_id.name if rec.order_id.supplier_id else "—",
                "clearing_charges": round(landed.clearing_charges, 2) if landed else 0.0,
                "demurrage_days": rec.demurrage_days,
                "state": dict(rec._fields["state"].selection).get(rec.state),
            }
        )
    rows.sort(key=lambda r: -r["clearing_charges"])
    return _pack(
        "C&F Management — clearing charges per shipment",
        ["shipment", "order", "port", "agent", "clearing_charges", "demurrage_days", "state"],
        {
            "shipment": "Shipment",
            "order": "Order",
            "port": "Port",
            "agent": "C&F Agent (supplier record)",
            "clearing_charges": "Clearing Charges",
            "demurrage_days": "Demurrage Days",
            "state": "State",
        },
        rows,
        [
            "Clearing charges come from the shipment's landed-cost sheet; there is "
            "no separate C&F agent master in this module (declared)."
        ],
        totals={
            "shipment": "Total",
            "clearing_charges": round(sum(r["clearing_charges"] for r in rows), 2),
        },
        empty="No shipments recorded yet.",
    )


REPORTS = {
    "incoterms_fx": incoterms_fx,
    "duty_cascade": duty_cascade,
    "landed_cost_by_shipment": landed_cost_by_shipment,
    "cycle_time": cycle_time,
    "demurrage_avoidance": demurrage_avoidance,
    "fx_exposure": fx_exposure,
    "cnf_management": cnf_management,
}


def kpis(env):
    orders = _orders(env)
    lcs = env["fix.import.lc"].sudo().search([])
    boes = env["fix.import.boe"].sudo().search([])
    arrivals = env["fix.import.arrival"].sudo().search([])
    landed = env["fix.import.landed"].sudo().search([])
    today = datetime.date.today()
    month_start = today.replace(day=1)
    landed_mtd = sum(
        rec.total_landed or 0.0
        for rec in landed
        if rec.create_date and rec.create_date.date() >= month_start
    )
    fx = 0.0
    for order in orders:
        rate = order.fx_rate or 1.0
        if rate != 1.0:
            fx += (order.fob_value or 0.0) * (rate - 1.0)
    received = ("received", "closed")
    return {
        "open_imports": len(orders.filtered(lambda o: o.state not in received)),
        "lc_open": len(lcs.filtered(lambda ln: ln.state in ("applied", "opened", "amended"))),
        "boe_unpaid": len(boes.filtered(lambda b: b.state != "paid")),
        "demurrage_days": sum(rec.demurrage_days or 0 for rec in arrivals),
        "landed_mtd": round(landed_mtd, 2),
        "fx_exposure": round(fx, 2),
    }
