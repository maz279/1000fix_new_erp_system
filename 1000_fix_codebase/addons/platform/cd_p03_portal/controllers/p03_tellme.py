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
        return {"results": results[:limit]}
