# fix_fixed_asset_takeon_ext — the register's take-on provenance (2026-11-25).
# MIG-03: every migrated record carries its legacy reference, permanently.
# Loaded AFTER fix_fixed_asset (the file name sorts after it; do not rename
# to anything sorting before fix_fixed_asset — import order is load-bearing).
from odoo import fields, models


class FixFixedAssetTakeonExt(models.Model):
    _inherit = "fix.fixed.asset"

    legacy_reference = fields.Char(
        string="Legacy Reference",
        index=True,
        copy=False,
        readonly=True,
        tracking=True,
        help="MIG-03: the permanent legacy key of a taken-on asset (<import_ref>-SL-<serial>).",
    )
    takeon_batch_id = fields.Many2one(
        "fix.asset.takeon.batch",
        string="Take-on Batch",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
