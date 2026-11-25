# fix.platform.release x fix.itsm.change — the A12 D8 release-to-change link.
#
# The FIELD lives here and not on the model's home module
# (cd_entity_config/models/fix_platform_ops2.py): its comodel is in cd_itsm,
# which loads AFTER cd_entity_config (cd_itsm depends on it), and a Many2one
# declared there breaks every incremental odoo-bin -u setup ("unknown
# comodel_name 'fix.itsm.change'"). cd_multi_entity depends on cd_itsm, so
# the field is declared where the comodel already exists.
#
# The D8 gate itself (action_release refuses without an approved or
# implemented linked change) is enforced in the home module, tolerantly, so
# the rule holds whichever of the two modules is present.
from odoo import fields, models


class FixPlatformReleaseItsm(models.Model):
    _inherit = "fix.platform.release"
    _description = "Release Coordination"

    itsm_change_id = fields.Many2one(
        "fix.itsm.change",
        string="ITSM Change",
        help="The change request this release ships. A release without an "
        "approved change is refused (D8).",
    )

    # A12 finish E7: one change ships one release. The action says so in words;
    # this keeps it true when two people release at the same moment.
    _one_release_per_change = models.UniqueIndex(
        "(itsm_change_id) WHERE state = 'released' AND itsm_change_id IS NOT NULL",
        "This ITSM change has already shipped in another release.",
    )
