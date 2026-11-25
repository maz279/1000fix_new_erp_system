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

# M07 audit 2026-11-13: the interaction log (FR-CRM-045); it links to
# crm.lead, so it loads after crm_lead_ext.
from . import fix_sales_activity

# Lead scoring EXTENDS crm.lead, so it imports after crm_lead_ext,
# and it enrols hot leads on a cadence, so after fix_crm_sequence.
from . import fix_lead_scoring

# The estimate hand-off and the journey-lead consumer extend crm.lead (and
# fix.estimate from cd_service_order), so they load after crm_lead_ext.
from . import crm_lead_quote, crm_lead_intake

# A03 audit W1: open leads follow a merged party (extends crm.lead).
from . import crm_lead_party_merge

# M07 capture audit, second pass (2026-11-18): lead qualification, opportunity
# team, sales quota, dedicated-manager eligibility, QBR action follow-through.
# It extends crm.lead, fix.account.assignment and fix.qbr.action, so it loads
# LAST.
from . import fix_crm_capture  # isort: split
