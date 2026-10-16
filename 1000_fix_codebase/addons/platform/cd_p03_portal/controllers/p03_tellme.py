# Tell-ME search controller — PP2-M05 (A13 archetype).
#
# Searches the frozen registry (modules, screens, reports, forms) in English
# AND Bengali — the prototype's dual-language global search, served as an
# Odoo JSON endpoint. The OWL overlay consumes this with keyboard nav.
from odoo import http
from odoo.http import request

import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parents[4] / "contracts" / "nav" / "registry.json"


def _build_index():
    """Flatten the registry into a searchable list (built once, cached)."""
    reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = []
    for mod in reg["modules"]:
        entries.append({
            "kind": "module", "id": mod["id"],
            "en": mod["en"], "bn": mod.get("bn", ""),
            "area": mod.get("area", ""),
        })
        for g in mod.get("groups", []):
            for s in g.get("screens", []):
                entries.append({
                    "kind": "screen", "id": s["id"],
                    "en": s["en"], "bn": s.get("bn", ""),
                    "area": mod["id"], "group": g["en"],
                })
        for r in mod.get("reports", []):
            entries.append({
                "kind": "report", "id": f"{mod['id']}-report",
                "en": r, "bn": "", "area": mod["id"],
            })
        for f in mod.get("forms", []):
            entries.append({
                "kind": "form", "id": f"{mod['id']}-form",
                "en": f, "bn": "", "area": mod["id"],
            })
    return entries


_INDEX = None


def _get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = _build_index()
    return _INDEX


class TellMeSearchController(http.Controller):

    @http.route("/p03/tellme", type="json", auth="user", readonly=True)
    def search(self, query="", limit=20):
        """Global search over the registry — EN and বাংলা.

        Matches case-insensitively in both locales; returns the top N
        results ordered by kind relevance (module > screen > report > form).
        """
        if not query or len(query.strip()) < 2:
            return {"results": []}
        q = query.strip().lower()
        entries = _get_index()
        results = []
        for entry in entries:
            en_match = q in entry["en"].lower()
            bn_match = entry["bn"] and q in entry["bn"]
            if en_match or bn_match:
                results.append({
                    **entry,
                    "matched_locale": "bn" if bn_match and not en_match else "en",
                })
        # rank: modules first, then screens, then reports, then forms
        kind_rank = {"module": 0, "screen": 1, "report": 2, "form": 3}
        results.sort(key=lambda r: (kind_rank.get(r["kind"], 9), r["en"]))

        # Live Database Records Search — ≤4 clicks to any record (AS-09 live data)
        try:
            env = request.env
            # 1. Search fix.service.order by reference, customer name or phone
            orders = env["fix.service.order"].sudo().search_read(
                ["|", "|", ("name", "ilike", q),
                 ("customer_id.name", "ilike", q),
                 ("customer_id.phone", "ilike", q)],
                ["name", "customer_id", "state", "branch_id", "service_type"],
                limit=6,
            )
            for o in orders:
                cust = o["customer_id"][1] if o.get("customer_id") else "Customer"
                st = o.get("state") or "draft"
                results.insert(0, {
                    "kind": "record",
                    "id": f"order-{o['id']}",
                    "res_model": "fix.service.order",
                    "res_id": o["id"],
                    "en": f"📦 {o['name']} — {cust} ({st})",
                    "bn": f"📦 {o['name']} — {cust}",
                    "area": "Service Operations",
                    "group": "Service Orders",
                    "matched_locale": "en",
                })

            # 2. Search fix.branch by branch name
            branches = env["fix.branch"].sudo().search_read(
                [("name", "ilike", q)],
                ["name", "code"],
                limit=3,
            )
            for b in branches:
                results.insert(1 if orders else 0, {
                    "kind": "branch",
                    "id": f"branch-{b['id']}",
                    "res_model": "fix.branch",
                    "res_id": b["id"],
                    "en": f"🏢 {b['name']}",
                    "bn": f"🏢 {b['name']}",
                    "area": "Service Operations",
                    "group": "Branches",
                    "matched_locale": "en",
                })

            # 3. Search hr.employee by name
            staff = env["hr.employee"].sudo().search_read(
                [("name", "ilike", q)],
                ["name", "job_title"],
                limit=3,
            )
            for emp in staff:
                job = emp.get("job_title") or "Technician"
                results.append({
                    "kind": "staff",
                    "id": f"emp-{emp['id']}",
                    "res_model": "hr.employee",
                    "res_id": emp["id"],
                    "en": f"👤 {emp['name']} ({job})",
                    "bn": f"👤 {emp['name']}",
                    "area": "People & Workforce",
                    "group": "Employees",
                    "matched_locale": "en",
                })
        except Exception:
            pass  # Fall back to registry search if models uninitialized

        return {"results": results[:limit]}
