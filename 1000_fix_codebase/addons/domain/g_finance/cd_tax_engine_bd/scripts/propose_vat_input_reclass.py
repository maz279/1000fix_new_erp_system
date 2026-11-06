"""A08 M51-8: propose (never post) the re-class of AP input VAT that the AP
sub-ledger posted to 110500 "Work in Progress".

The vat_input account role used to default to code 110500, which in the loaded
chart is "Work in Progress": on fix_dev 60,337.50 of AP input VAT sits there.
The role now has no default (cd_tax_engine_bd.vat_input_account_code must be
set). Once the lead has set it to the real input-VAT account, this script
lists the AP "Input VAT ..." lines on 110500 and prints the proposed entry
(Dr input-VAT account / Cr 110500). With --draft it also creates that entry as
a DRAFT journal entry for a second person to review and post. It never posts.

Run on the target database with Odoo's shell, e.g.:

    PYTHONPATH="$(pwd -W)" .venv/Scripts/python.exe vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d fix_dev --no-http \
        < addons/domain/g_finance/cd_tax_engine_bd/scripts/propose_vat_input_reclass.py

Set FIX_RECLASS_DRAFT=1 in the environment to create the draft entry, and
FIX_RECLASS_COMMIT=1 to commit it (otherwise the transaction is rolled back).
"""

import json
import os

env = globals().get("env")  # provided by `odoo-bin shell`
if env is None:  # pragma: no cover - only meaningful inside odoo-bin shell
    raise SystemExit("Run this through `odoo-bin shell` (it needs `env`).")

draft = os.environ.get("FIX_RECLASS_DRAFT") == "1"
commit = os.environ.get("FIX_RECLASS_COMMIT") == "1"
wip_code = os.environ.get("FIX_RECLASS_WIP_CODE", "110500")
for company in env["res.company"].search([]):
    try:
        proposal = env["fix.input.vat.credit"]._fix_propose_vat_input_reclass(
            company, wip_code, create_draft=draft
        )
    except Exception as exc:
        print(json.dumps({"company": company.name, "refused": str(exc)}))
        continue
    print(json.dumps(proposal, indent=2, default=str))
if commit and draft:
    env.cr.commit()
    print("draft re-class entries committed (still DRAFT, not posted)")
else:
    env.cr.rollback()
    print("nothing committed")
