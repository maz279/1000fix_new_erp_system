# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_crm_ext — M07 CRM (P04-M04 W1 slice + 2026-10-27 rebuild surfaces).
from . import (
    crm_lead_ext,
    fix_account,
    fix_account_master,
    fix_forecast,
    fix_pipeline,
    fix_crm_sequence,
    fix_qbr,
    fix_renewal,
)

# Lead scoring EXTENDS crm.lead, so it imports after crm_lead_ext,
# and it enrols hot leads on a cadence, so after fix_crm_sequence.
from . import fix_lead_scoring
