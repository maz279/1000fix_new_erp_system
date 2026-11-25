# 19.0.2.1.0 — A02 audit P0 (M03-2/4/5).
#
# 1. The POD code used to be stored in clear in fix_consignment.pod_otp, which
#    every rider could read. Those codes are compromised, so they are voided,
#    not hashed: an in-flight delivery is issued a new code to the recipient.
#    The field is gone; the orphan column is emptied so no code stays on disk.
# 2. The chain check now requires every step of the leg type, and the claim
#    tier now follows the DOFA gate. Stored computes are not recomputed on an
#    upgrade by themselves, so the existing rows are recomputed here.
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    cr.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name = 'fix_consignment' AND column_name = 'pod_otp'"
    )
    if cr.fetchone():
        cr.execute("UPDATE fix_consignment SET pod_otp = NULL WHERE pod_otp IS NOT NULL")

    env = api.Environment(cr, SUPERUSER_ID, {})
    consignments = env["fix.consignment"].with_context(active_test=False).search([])
    for name in ("chain_broken", "chain_problem", "custody_summary"):
        env.add_to_compute(consignments._fields[name], consignments)
    claims = env["fix.damage.claim"].search([])
    for name in ("dofa_tier", "dofa_tier_required"):
        env.add_to_compute(claims._fields[name], claims)
    env.flush_all()
