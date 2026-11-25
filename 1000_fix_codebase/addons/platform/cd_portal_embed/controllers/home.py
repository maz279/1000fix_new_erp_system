"""Frame-policy override for the Odoo web client bootstrap route.

The stock controller (vendor/odoo/addons/web/controllers/home.py) stamps
``X-Frame-Options: DENY`` on every ``/web``/``/odoo``/``/scoped_app``
response, which blocks the platform's Next.js portals from embedding the
P03 Operations Workspace in an in-page pane (:3000 framing :8069 - same
hostname, different origin, so ``SAMEORIGIN`` would not help either).

This subclass (canonical Odoo controller-override pattern, as used by
``auth_signup`` for ``/web/login``) swaps that header for a CSP
``frame-ancestors`` allow-list on the 200 bootstrap response only -
redirects (e.g. the login bounce) keep stock behaviour.
"""

from odoo import http
from odoo.addons.web.controllers.home import Home

# Dev default: the P01 customer portal on both loopback hostnames (cookies
# are host-only, so users may browse either). Production narrows this via
# the ``portal_embed.frame_ancestors`` system parameter (comma-separated).
DEFAULT_FRAME_ANCESTORS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _frame_ancestors():
    param = http.request.env["ir.config_parameter"].sudo().get_param("portal_embed.frame_ancestors")
    origins = [o.strip() for o in (param or "").split(",") if o.strip()]
    return origins or DEFAULT_FRAME_ANCESTORS


class HomePortalEmbed(Home):
    @http.route(
        ["/web", "/odoo", "/odoo/<path:subpath>", "/scoped_app/<path:subpath>"],
        type="http",
        auth="none",
        readonly=Home._web_client_readonly,
    )
    def web_client(self, s_action=None, **kw):
        response = super().web_client(s_action=s_action, **kw)
        if response.status_code == 200:
            response.headers.pop("X-Frame-Options", None)
            response.headers["Content-Security-Policy"] = "frame-ancestors 'self' " + " ".join(
                _frame_ancestors()
            )
        return response
