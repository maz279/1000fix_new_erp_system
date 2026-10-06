# P03 registry controller — serves the frozen navigation registry (PP2-M01).
#
# The OWL workspace loads /p03/registry (a read-only JSON dump of
# contracts/nav/registry.json — areas, modules, groups, screens, reports,
# forms, freg, personas) and renders archetype A2 from it. The registry is
# generated, committed, and FF-38-checked; this controller only serves it.
from odoo import http
from odoo.http import request

import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parents[4] / "contracts" / "nav" / "registry.json"


class P03RegistryController(http.Controller):

    @http.route("/p03/registry", type="json", auth="user", readonly=True)
    def get_registry(self):
        """The frozen navigation registry — read-only, user-authenticated.

        Every authenticated back-office user can read the navigation shape
        (it is the menu universe); actual screen access is action-gated by
        the domain modules' own ACLs (NVR-22).
        """
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
