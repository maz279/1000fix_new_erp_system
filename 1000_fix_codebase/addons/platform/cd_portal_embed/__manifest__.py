{
    "name": "Portal Embed Frame Policy",
    "summary": "Let the Next.js portals embed the Odoo web client workspace in-page",
    "description": (
        "The stock web client answers /odoo/* with 'X-Frame-Options: DENY', "
        "which forbids embedding the P03 Operations Workspace anywhere - "
        "including this platform's own Next.js portals that render ERP "
        "workspaces inside their main area. This module replaces the blanket "
        "DENY on the web-client bootstrap route with a CSP frame-ancestors "
        "allow-list (dev default: the P01 portal on both loopback names; "
        "override in production via the 'portal_embed.frame_ancestors' "
        "system parameter, comma-separated origins)."
    ),
    "version": "19.0.1.0.0",
    "category": "Hidden/Tools",
    "author": "1000 FiX Services Ltd.",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
