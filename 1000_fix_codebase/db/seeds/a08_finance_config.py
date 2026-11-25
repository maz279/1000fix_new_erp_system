# ruff: noqa: F821 - runs inside odoo-bin shell, which provides env
"""a08_finance_config.py - GL account roles for the A08 finance controls.

Run inside `odoo-bin shell -c <conf> -d <db>` (superuser). Idempotent. FOR A
SYNTHETIC DEVELOPMENT DATABASE (DE-12): production takes these from Finance.

The A08 build fails closed: a role with no account refuses to post, and until
the roles are set a treasury, tax or settlement screen stops at that refusal.
This fills the roles from three sources, most certain first:

1. MD-035 + ODOO_CHART_MAPPING already pair the role with an Odoo account
   (input VAT is 2-30-20-010 = 131000, output VAT is 2-30-10-010 = 251000).
2. The account exists in the Odoo chart under the same meaning.
3. PROPOSED: no account exists, so one is created under a plainly named code.
   Rows that MD-035 names cite its code; the rest have no MD-035 row at all,
   so Finance should confirm or replace them (report §7, B3/B5). It only maps
   roles. It never moves a balance: the 60,337.50 on 110500 is re-classed by
   cd_tax_engine_bd/scripts/propose_vat_input_reclass.py, as a draft for Finance.

Left unset on purpose, because a person must supply them:
cd_tax_engine_bd.declarant_* (a named person's NID), ECL rates, statutory rates.

An existing parameter is never overwritten. FIX_A08_COMMIT=1 commits.
"""

import json
import os

COMPANY_XMLID = "base.main_company"

EXISTING = {
    "cd_tax_engine_bd.vat_input_account_code": "131000",  # MD-035 2-30-20-010
    "cd_tax_engine_bd.vat_output_account_code": "251000",  # MD-035 2-30-10-010
    "cd_settlement_ext.account_code.tds_payable": "252000",  # MD-035 2-30-30-010
    "cd_settlement_ext.account_code.clearing": "101404",  # Outstanding Payments
    "cd_cash_position.account_code.outgoing_clearing": "101404",  # Outstanding Payments
    "cd_cash_position.account_code.bank_charges": "620000",  # MD-035 5-20-40-010
    "cd_cash_position.account_code.gateway_fees": "620000",  # MD-035 5-20-40-010
    "cd_cash_position.account_code.cash_shortage": "642000",  # Cash Difference Loss
}

# param -> (code, name, account_type, MD-035 row or None)
PROPOSED = {
    "cd_cash_position.account_code.branch_cash": (
        "101100",
        "Cash in Hand - Branch",
        "asset_current",
        "1-10-10-010",
    ),
    "cd_tax_engine_bd.account_code.vds_payable": (
        "252100",
        "VDS Payable",
        "liability_current",
        "2-30-30-030",
    ),
    "cd_settlement_ext.account_code.warranty_provision": (
        "253000",
        "Warranty Service Provision",
        "liability_current",
        "2-40-30-010",
    ),
    "cd_cash_position.account_code.cash_in_transit": (
        "101450",
        "Cash in Transit",
        "asset_current",
        None,
    ),
    "cd_cash_position.account_code.cod_clearing": (
        "101460",
        "Rider COD Clearing",
        "asset_current",
        None,
    ),
    "cd_cash_position.account_code.rider_shortage": (
        "128100",
        "Rider Shortage Recoverable",
        "asset_current",
        None,
    ),
    "cd_cash_position.account_code.cheque_returned": (
        "128200",
        "Returned Cheques Receivable",
        "asset_current",
        None,
    ),
    "cd_cash_position.account_code.interest_expense": (
        "631000",
        "Interest Expense on Bank Facilities",
        "expense",
        None,
    ),
    "cd_cash_position.account_code.bond_encashment_loss": (
        "646000",
        "Bank Guarantee Encashment Loss",
        "expense",
        None,
    ),
    "cd_settlement_ext.account_code.commission_revenue": (
        "400100",
        "Marketplace Commission Revenue",
        "income",
        None,
    ),
    "cd_settlement_ext.account_code.seller_payable": (
        "200200",
        "Marketplace Seller Payable",
        "liability_current",
        None,
    ),
    "cd_settlement_ext.account_code.partner_commission_expense": (
        "647000",
        "Partner Commission Expense",
        "expense",
        None,
    ),
    "cd_settlement_ext.account_code.partner_payable": (
        "211200",
        "Partner Commission Payable",
        "liability_current",
        None,
    ),
    "cd_settlement_ext.account_code.clawback_recovery": (
        "211300",
        "Customer Refund Clearing",
        "liability_current",
        None,
    ),
    "cd_settlement_ext.account_code.warranty_expense": (
        "648000",
        "Workmanship Warranty Expense",
        "expense",
        None,
    ),
}

HEAD_OFFICE_CODE = "HO"

# What MD-035 requires on bank, VAT and TDS lines when an automated sub-ledger posts:
# a head-office payment belongs to no service branch, so it books to head office.
DIMENSIONS = {
    "cd_gl_ext.default_branch_code": HEAD_OFFICE_CODE,
    "cd_gl_ext.default_cost_centre": "CORP",
    "cd_gl_ext.default_business_line": "SERVICE",
}

JOURNALS = {
    "cd_tax_engine_bd.challan_journal_code": "BNK1",
    "cd_settlement_ext.payout_journal_code": "BNK1",
}

Param = env["ir.config_parameter"].sudo()
company = env.ref(COMPANY_XMLID)
Account = env["account.account"].sudo().with_company(company)


def find(code):
    return Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)


report = {"set": {}, "kept": {}, "accounts_created": [], "refused": []}


def put(key, value):
    current = Param.get_param(key)
    if current:
        report["kept"][key] = current
        return
    Param.set_param(key, value)
    report["set"][key] = value


for key, code in EXISTING.items():
    if find(code):
        put(key, code)
    else:
        report["refused"].append(f"{key}: account {code} is not in the chart")

for key, (code, name, kind, md035) in PROPOSED.items():
    if not Param.get_param(key) and not find(code):
        Account.create(
            {"code": code, "name": name, "account_type": kind, "company_ids": [(6, 0, company.ids)]}
        )
        report["accounts_created"].append(
            "{} {}{}".format(code, name, f" (MD-035 {md035})" if md035 else " (proposed)")
        )
    put(key, code)

# On fix_dev every branch belongs to a smoke-test entity under another company, so this
# company has none. The sub-ledger default needs one of its own; re-parenting the 78
# existing branches is a master-data decision for a person, and is not done here.
Branch = env["fix.branch"].sudo()
if not Branch.search([("code", "=", HEAD_OFFICE_CODE), ("company_id", "=", company.id)], limit=1):
    entity = env["fix.entity"].sudo().search([("company_id", "=", company.id)], limit=1)
    unit = env["operating.unit"].sudo().search([("company_id", "=", company.id)], limit=1)
    if entity and unit:
        Branch.create(
            {
                "code": HEAD_OFFICE_CODE,
                "name": "1000 FiX Head Office",
                "entity_id": entity.id,
                "operating_unit_id": unit.id,
            }
        )
        report["branch_created"] = HEAD_OFFICE_CODE
    else:
        report["refused"].append(f"no fix.entity or operating unit for {company.name}")

for key, value in DIMENSIONS.items():
    put(key, value)

for key, code in JOURNALS.items():
    journal = (
        env["account.journal"]
        .sudo()
        .search([("code", "=", code), ("company_id", "=", company.id)], limit=1)
    )
    if journal:
        put(key, code)
    else:
        report["refused"].append(f"{key}: journal {code} not found")

report["company_bin"] = company.vat or "NOT SET: Mushak filing refuses without a 13-digit BIN"
print(json.dumps(report, indent=2, ensure_ascii=False))
if os.environ.get("FIX_A08_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back: nothing changed (set FIX_A08_COMMIT=1 to commit)")
