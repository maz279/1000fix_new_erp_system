# cd_hr_core 19.0.0.7.0 — the Labour (Amendment) Act 2026 statutory figures
# (A09 ERP audit M21-F5 / M55-F2, M21-F6): maternity 120 days (s.46: 60 before
# + 60 after), festival holidays 13 (s.118(1)), death-benefit qualifying
# service 1 year (s.19), and casual/sick leave charging the holidays inside
# them (Bangladesh Labour Rules 2015 r.106).
#
# Applying new statutory figures to EXISTING data is the owner's decision, and
# it has not been taken yet: the moves run ONLY when ir.config_parameter
# cd_hr_core.apply_labour_act_2026_figures == 'approved'; with the parameter
# absent or anything else this logs one line and changes nothing. The applied
# method (res.company._apply_labour_act_2026_figures) is idempotent — only
# rows still holding the untouched pre-Act value (112 / 11 / 2.0 / True) move —
# so an upgrade that runs it again later changes nothing, and the method sets
# the parameter itself as its last step (the lead runs it once on production
# after the owner approves; the statutory floors and the 60/60 maternity split
# switch together with the data).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

APPROVAL_PARAM = "cd_hr_core.apply_labour_act_2026_figures"


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    approved = env["ir.config_parameter"].sudo().get_param(APPROVAL_PARAM)
    if approved != "approved":
        _logger.info("2026 Act figures not applied - owner approval pending (%s)", APPROVAL_PARAM)
        return
    result = env["res.company"].sudo()._apply_labour_act_2026_figures()
    _logger.info("cd_hr_core %s: Labour (Amendment) Act 2026 figures applied: %s", version, result)
