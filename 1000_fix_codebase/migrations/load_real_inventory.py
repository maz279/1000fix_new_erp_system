#!/usr/bin/env python3
"""migrations/load_real_inventory.py — REAL inventory ETL (fit-gap report R3/R5/R6).

Replaces the synthetic SRC-37/SRC-38 inventory (150 parts, 10 locations) with
the REAL 1000 FiX inventory statement:
  - 14,198 items (spare parts, accessories and Full Unit finished goods)
  - 41 groups -> 859 group-scoped categories as a 2-level product.category tree
  - 32 brands linked to the governed fix.brand master
  - the three part identities: new-ERP SKU (default_code), previous-ERP number
    (legacy_erp_part_number / legacy_reference), manufacturer MPN
    (manufacturer_part_number)
  - 96 stocked source columns as fix.stock.location rows, opening quantities as
    fix.stock.onhand ledger rows (62,736 units)

Standards honoured from the estate migration law:
  - MIG-02: control totals are recomputed from the file BEFORE any write and
    the database is re-measured AFTER the load; the script raises on mismatch.
  - MIG-03: permanent legacy_reference on every loaded row (REAL:INV:<erp pn>).
  - Idempotence: every upsert matches on the legacy reference / SKU first.

Run (from 1000_fix_codebase, the main checkout):
  .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
    -c infra/odoo-conf/local.resolved.conf -d fix_real --no-http \
    migrations/load_real_inventory.py
Optional env: REAL_INV_XLSX (source workbook), REAL_INV_PURGE=0 to skip purge.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from datetime import date

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

XLSX = os.environ.get(
    "REAL_INV_XLSX",
    r"C:/Users/DELL/Downloads/inventory/Inventory Product List with Qty (1).xlsx",
)
PURGE = os.environ.get("REAL_INV_PURGE", "1") == "1"
BATCH = 200

# ---------------------------------------------------------------- read source
t0 = time.time()
wb = load_workbook(XLSX, read_only=True, data_only=True)
ws = wb.worksheets[0]
raw = list(ws.iter_rows(values_only=True))
header = list(raw[0])


def _s(v):
    return str(v).strip() if v is not None and str(v).strip() != "" else ""


rows = []
for r in raw[1:]:
    if not any(_s(c) for c in r):
        continue
    rows.append(
        {
            "mpn": _s(r[0]),
            "erp_pn": _s(r[1]),
            "new_pn": _s(r[2]),
            "desc": _s(r[3]),
            "brand": _s(r[4]),
            "group": _s(r[5]),
            "model": _s(r[6]),
            "category": _s(r[7]),
            "qty_by_col": {
                ci: float(r[ci])
                for ci in range(9, len(r))
                if isinstance(r[ci], int | float) and r[ci] > 0
            },
            "grand_total": float(r[8]) if isinstance(r[8], int | float) else 0.0,
        }
    )

CONTROL = {
    "rows": len(rows),
    "units": sum(r["grand_total"] for r in rows),
    "nonzero_cells": sum(len(r["qty_by_col"]) for r in rows),
    "brands": len({r["brand"] for r in rows}),
    "groups": len({r["group"] for r in rows}),
    "pairs": len({(r["group"], r["category"]) for r in rows}),
    "stocked_cols": len({ci for r in rows for ci in r["qty_by_col"]}),
}
print("[control] computed from source BEFORE any write:", json.dumps(CONTROL), flush=True)

# sanity: matrix sum must equal the Grand Total column (pivot integrity)
matrix_units = sum(q for r in rows for q in r["qty_by_col"].values())
if abs(matrix_units - CONTROL["units"]) > 0.001:
    raise SystemExit(f"source integrity: matrix {matrix_units} != grand total {CONTROL['units']}")

# ------------------------------------------------------------- environment
base_env = env  # noqa: F821  (provided by odoo shell)
env = base_env(user=2, su=True)
env = env(
    context=dict(
        env.context,
        tracking_disable=True,
        mail_notrack=True,
        mail_create_nolog=True,
        mail_create_nosubscribe=True,
        mail_auto_delete=True,
    )
)
company = env.company

# The catalogue publishes a domain event per create; 14k Kafka-bound events are
# ETL noise, not business changes — silence the client for this load only.
import odoo.addons.cd_catalogue.models.fix_catalogue_item as _fci  # noqa: E402

_silent = lambda *a, **k: None  # noqa: E731
_fci.publish = _silent

PC = env["product.category"]
PT = env["product.template"]
CI = env["fix.catalogue.item"]
SP = env["fix.spare.part"]
BR = env["fix.brand"]
LOC = env["fix.stock.location"]
ON = env["fix.stock.onhand"]

# --------------------------------------------------------------- 1. purge
if PURGE:
    print("[purge] replacing synthetic inventory (SRC-37/SRC-38)...", flush=True)
    wiped = {}
    # every stored m2o pointing at fix.spare.part or fix.stock.location, from
    # the live registry — nothing hard-coded, so later modules are covered too
    refs = (
        env["ir.model.fields"]
        .sudo()
        .search(
            [
                ("ttype", "=", "many2one"),
                ("store", "=", True),
                ("relation", "in", ["fix.spare.part", "fix.stock.location"]),
            ]
        )
    )
    ledger_models = [
        "fix.stock.onhand",
        "fix.stock.lot",
        "fix.stock.receipt",
        "fix.stock.receipt.line",
        "fix.stock.consumption",
        "fix.stock.transfer",
        "fix.stock.transfer.line",
        "fix.stock.count",
        "fix.stock.count.line",
        "fix.stock.count.snapshot",
        "fix.stock.van.recon",
        "fix.stock.rtv",
        "fix.stock.quarantine",
        "fix.stock.class.change",
        "fix.reorder.rule",
        "fix.inventory.valuation.suspense",
    ]
    for m in ledger_models:
        if m in env:
            try:
                recs = env[m].search([])
                if recs:
                    n = len(recs)
                    recs.unlink()
                    recs.flush_recordset()  # surface deferred errors inside the try
                    env.cr.commit()
                    wiped[m] = n
            except Exception as exc:
                env.cr.rollback()
                print(f"[purge] ledger unlink failed for {m}: {str(exc)[:120]}", flush=True)
    # any remaining model referencing a spare part/location: required links mean
    # the referencing rows themselves are synthetic fixtures — unlink them;
    # optional links are cleared. Each step commits on its own (Odoo 19 defers
    # writes, so errors surface at flush/commit, not at write()).
    for f in refs:
        if f.model not in env or f.model in [
            *ledger_models,
            "fix.spare.part",
            "fix.stock.location",
        ]:
            continue
        try:
            recs = env[f.model].search([(f.name, "!=", False)])
            if not recs:
                continue
            if f.required:
                recs.unlink()
                recs.flush_recordset()
                wiped[f"del:{f.model}"] = len(recs)
            else:
                recs.write({f.name: False})
                recs.flush_recordset()
                wiped[f"ref:{f.model}.{f.name}"] = len(recs)
            env.cr.commit()
        except Exception as exc:
            env.cr.rollback()
            print(f"[purge] could not clear {f.model}.{f.name}: {str(exc)[:120]}", flush=True)

    parts = SP.search([])
    archived = 0
    try:
        parts.unlink()
        parts.flush_recordset()
        env.cr.commit()
        wiped["fix.spare.part:unlinked"] = len(parts)
    except Exception as exc:
        env.cr.rollback()
        print(f"[purge] unlink blocked ({str(exc)[:100]}); archiving instead", flush=True)
        parts._guarded().write({"active": False, "state": "discontinued"})
        parts.flush_recordset()
        env.cr.commit()
        archived = len(parts)
    locs = LOC.search([])
    try:
        locs.unlink()
        locs.flush_recordset()
        env.cr.commit()
        wiped["fix.stock.location:unlinked"] = len(locs)
    except Exception as exc:
        env.cr.rollback()
        print(f"[purge] location unlink blocked ({str(exc)[:100]}); archiving", flush=True)
        locs.write({"active": False})
        locs.flush_recordset()
        env.cr.commit()
        wiped["fix.stock.location:archived"] = len(locs)
    env.cr.commit()
    print(
        f"[purge] done t={time.time()-t0:.0f}s archived_parts={archived} detail={wiped}", flush=True
    )


# ------------------------------------------------------- 2. brands + taxonomy
def brand_for(name):
    key = name.upper()
    if key in brand_cache:
        return brand_cache[key]
    existing = BR.search([]).filtered(lambda b: b.name.upper() == key)
    if existing:
        rec = existing[:1]
    else:
        code = re.sub(r"[^A-Z0-9]", "", name.upper())[:10] or "GEN"
        rec = BR.create({"name": name, "code": code})
    brand_cache[key] = rec
    return rec


brand_cache = {}


def category_for(group, category):
    key = (group, category)
    if key in cat_cache:
        return cat_cache[key]
    parent = group_cache.get(group)
    if parent is None:
        parent = PC.search([("name", "=", group), ("parent_id", "=", False)], limit=1)
        if not parent:
            parent = PC.create({"name": group})
        group_cache[group] = parent
    child = PC.search([("name", "=", category), ("parent_id", "=", parent.id)], limit=1)
    if not child:
        child = PC.create({"name": category, "parent_id": parent.id})
    cat_cache[key] = child
    return child


cat_cache, group_cache = {}, {}

brand_for("SAMSUNG")
category_for(rows[0]["group"], rows[0]["category"])  # warm maps
env.cr.commit()
print(f"[taxonomy] masters warm t={time.time()-t0:.0f}s", flush=True)

# --------------------------------------------- 3. items: template+catalogue+part
PART_CATEGORY_HINTS = [
    ("battery", "battery"),
    ("motherboard", "motherboard"),
    ("main pcb", "motherboard"),
    ("pcb", "motherboard"),
    ("display", "display"),
    ("lcd", "display"),
    ("screen", "display"),
    ("touch", "display"),
    ("camera", "camera"),
    ("charging", "charging_port"),
    ("port", "charging_port"),
    ("sub-board", "charging_port"),
    ("compressor", "compressor"),
    ("motor", "motor"),
    ("sensor", "sensor"),
]


def part_category_hint(category, group):
    blob = f"{category} {group}".lower()
    for needle, value in PART_CATEGORY_HINTS:
        if needle in blob:
            return value
    return "fastener"


def item_type_for(group):
    if group == "Full Unit Product":
        return "finished_good"
    if group == "Accessories":
        return "accessory"
    return "part"


sku_seen = Counter()
deduped = []

tmpl_vals, meta = [], []
for r in rows:
    sku_seen[r["new_pn"]] += 1
    sku = r["new_pn"] if sku_seen[r["new_pn"]] == 1 else f"{r['new_pn']}-{sku_seen[r['new_pn']]}"
    if sku != r["new_pn"]:
        deduped.append((r["new_pn"], sku))
    meta.append((sku, r))
    tmpl_vals.append(
        {
            "name": r["desc"] or sku,
            "categ_id": category_for(r["group"], r["category"]).id,
            "type": "consu",
            "is_storable": True,
            "manufacturer_part_number": r["mpn"] or None,
            "legacy_erp_part_number": r["erp_pn"] or None,
        }
    )

created_parts, created_items = [], []
for start in range(0, len(tmpl_vals), BATCH):
    chunk_vals = tmpl_vals[start : start + BATCH]
    chunk_meta = meta[start : start + BATCH]
    tmpls = PT.create(chunk_vals)
    ci_vals, sp_vals = [], []
    for tmpl, (sku, r) in zip(tmpls, chunk_meta, strict=False):
        variant = tmpl.product_variant_ids[:1]
        variant.write({"default_code": sku})
        ci_vals.append(
            {
                "product_tmpl_id": tmpl.id,
                "company_id": company.id,
                "item_type": item_type_for(r["group"]),
                "category_id": tmpl.categ_id.id,
                "brand_id": brand_for(r["brand"]).id,
            }
        )
        sp_vals.append(
            {
                "name": r["desc"] or sku,
                "part_number": sku,
                "company_id": company.id,
                "category_id": tmpl.categ_id.id,
                "brand_id": brand_for(r["brand"]).id,
                "device_brand": r["brand"],
                "part_category": part_category_hint(r["category"], r["group"]),
                "product_id": variant.id,
                "compatible_models": r["model"] or None,
                "uom": "PCS",
                "legacy_reference": f"REAL:INV:{r['erp_pn']}",
            }
        )
    items = CI.create(ci_vals)
    # approved-by-load: the guarded token is the sanctioned write path; the
    # approval workflow stays in force for every later change.
    items._guarded().write({"state": "approved"})
    parts = SP.create(sp_vals)
    created_items += items.ids
    created_parts += parts.ids
    if (start // BATCH) % 10 == 0:
        env.cr.commit()
        print(
            f"[items] {start + len(chunk_vals)}/{len(tmpl_vals)} t={time.time()-t0:.0f}s",
            flush=True,
        )
env.cr.commit()
print(
    f"[items] created templates={len(tmpl_vals)} catalogue={len(created_items)} parts={len(created_parts)} "
    f"deduped={len(deduped)} t={time.time()-t0:.0f}s",
    flush=True,
)

# ------------------------------------------------- 4. locations + opening stock
col_locs = {}
for ci in sorted({ci for r in rows for ci in r["qty_by_col"]}):
    letter = get_column_letter(ci + 1)
    if ci == 9:  # the only named column in the export
        code, name, loc_type = "WARRANTY-HO", "Warranty HO/Stock", "central"
    else:
        code, name, loc_type = f"COL-{letter}", f"Source Column {letter}", "branch"
    existing = LOC.search([("code", "=", code)], limit=1)
    loc = existing or LOC.create(
        {
            "name": name,
            "code": code,
            "company_id": company.id,
            "location_type": loc_type,
            "legacy_reference": f"REAL:XLSX:COL:{letter}",
        }
    )
    col_locs[ci] = loc.id
env.cr.commit()
print(f"[locations] stocked source columns={len(col_locs)} t={time.time()-t0:.0f}s", flush=True)

part_by_legacy = {p.legacy_reference: p.id for p in SP.browse(created_parts)}
on_vals = []
for _sku, r in meta:
    pid = part_by_legacy.get(f"REAL:INV:{r['erp_pn']}")
    if not pid:
        continue
    for ci, qty in r["qty_by_col"].items():
        on_vals.append(
            {
                "company_id": company.id,
                "part_id": pid,
                "location_id": col_locs[ci],
                "ownership_class": "owned",
                "stock_status": "unrestricted",
                "qty": qty,
                "unit_cost": 0.0,  # the statement carries no costs (report R6): the
                # valuation suspense discipline releases these later
                "valuation_method": "wac",
                "last_move_date": date.today(),
            }
        )
for start in range(0, len(on_vals), 500):
    ON.create(on_vals[start : start + 500])
    env.cr.commit()
print(f"[onhand] ledger rows={len(on_vals)} t={time.time()-t0:.0f}s", flush=True)

# ------------------------------------------------------------- 5. reconcile
env.flush_all()
env.clear()
real_parts = SP.search([("legacy_reference", "like", "REAL:INV:%")])
real_onhand = ON.search([("part_id", "in", real_parts.ids)])
measured = {
    "rows": len(real_parts),
    "active_parts": SP.search_count([("active", "=", True)]),
    "units": round(sum(real_parts.mapped("qty_available")), 3),
    "onhand_rows": len(real_onhand),
    "onhand_units": round(sum(real_onhand.mapped("qty")), 3),
    "leftover_parts": SP.search_count([("legacy_reference", "not like", "REAL:INV:%")]),
    "leftover_onhand": ON.search_count([("part_id", "not in", real_parts.ids)]),
    "locations": LOC.search_count([("legacy_reference", "like", "REAL:XLSX:%")]),
    "brands": BR.search_count([]),
    "categories": PC.search_count([]),
    "finished_goods": CI.search_count([("item_type", "=", "finished_good")]),
}
print("[reconcile] measured AFTER load:", json.dumps(measured), flush=True)

errors = []
if measured["rows"] != CONTROL["rows"]:
    errors.append(f"items {measured['rows']} != {CONTROL['rows']}")
if abs(measured["units"] - CONTROL["units"]) > 0.01:
    errors.append(f"units(parts) {measured['units']} != {CONTROL['units']}")
if abs(measured["onhand_units"] - CONTROL["units"]) > 0.01:
    errors.append(f"units(ledger) {measured['onhand_units']} != {CONTROL['units']}")
if measured["onhand_rows"] != CONTROL["nonzero_cells"]:
    errors.append(f"onhand rows {measured['onhand_rows']} != {CONTROL['nonzero_cells']}")
if measured["leftover_parts"]:
    errors.append(f"{measured['leftover_parts']} synthetic parts still present")
if measured["leftover_onhand"]:
    errors.append(f"{measured['leftover_onhand']} synthetic ledger rows still present")
if measured["locations"] != CONTROL["stocked_cols"]:
    errors.append(f"locations {measured['locations']} != {CONTROL['stocked_cols']}")
if errors:
    raise SystemExit("RECONCILIATION FAILED: " + "; ".join(errors))

summary = {
    "control": CONTROL,
    "measured": measured,
    "deduped_skus": deduped,
    "elapsed_s": round(time.time() - t0, 1),
}
print("LOAD_OK " + json.dumps(summary), flush=True)
