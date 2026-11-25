# 19.0.1.2.0 — A03 P2: give existing pipelines the standard stage gates.
#
# The default gate configuration ships as noupdate data, which an upgrade
# creates but never copies onto the pipelines a database already has. On
# fix_dev the only pipeline had stages_json NULL (A03 audit G-M07-11).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["fix.pipeline"]._apply_default_stage_gates()
