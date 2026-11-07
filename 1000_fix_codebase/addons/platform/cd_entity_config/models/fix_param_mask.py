# A12 finish (OP decision, E22): a Platform Admin may read the parameter and cron
# INVENTORIES, because the refusal text promised "platform administrators" and only
# base.group_system could open them. Reading the table must not hand over secrets:
# parameter values hold credentials (cd_storefront.gateway_secret.<rail>), so the
# value itself stays system-only. get_param reads under sudo and is unaffected.
from odoo import fields, models


class IrConfigParameterValueMask(models.Model):
    _inherit = "ir.config_parameter"

    value = fields.Text(groups="base.group_system")
