# Legacy take-on fields for the 2026-11-09 real-user migration.
#
# The legacy system's org taxonomy (user.xlsx) differs from the estate's:
# legacy "Branch" is brand+location, legacy "Operating Unit" is a product or
# service line, and the estate's operating.unit is geographic. The resolved
# links (fix.branch, hr.department) live in the standard fields; these fields
# keep the legacy labels verbatim so every crosswalk decision stays auditable
# and re-runs can match on the exact source strings.
from odoo import fields, models


class HrEmployeeUserMigration(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    legacy_login = fields.Char(
        string="Legacy Login",
        index=True,
        help="Login in the legacy system this employee record was taken on from",
    )
    legacy_branch_name = fields.Char(
        string="Legacy Branch Label",
        index=True,
        help="Legacy branch label verbatim (brand+location taxonomy)",
    )
    legacy_operating_unit = fields.Char(
        string="Legacy Service Line",
        index=True,
        help="Legacy product/service line (RMA, Xiaomi, Dell AIO ...) verbatim",
    )
    default_warehouse_id = fields.Many2one(
        "fix.warehouse",
        string="Default Warehouse",
        help="The login's default warehouse from the legacy system, resolved via crosswalk",
    )
