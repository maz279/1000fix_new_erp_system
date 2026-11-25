# cd_talent 19.0.0.7.0 — the owner's two business figures (2026-11-23).
#
# The parameters are `noupdate` records: an upgrade updates the XML default but
# leaves an existing database row alone, so a database that still carries the
# old "0" (no automatic erasure; no default offer validity) is moved here.
# A value the business has already set to something else is never touched.
from odoo import SUPERUSER_ID, api

# key -> the old value this migration replaces, and the owner's decision
FIGURES = {
    "cd_talent.candidate_retention_days": ("0", "180"),
    "cd_talent.offer_validity_days": ("0", "14"),
}


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Param = env["ir.config_parameter"].sudo()
    for key, (stale, decided) in FIGURES.items():
        if (Param.get_param(key) or "").strip() == stale:
            Param.set_param(key, decided)
