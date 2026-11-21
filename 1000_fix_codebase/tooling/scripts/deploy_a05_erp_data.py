"""A05 ERP audit (Nov 2026) - owner-decided deployment data, idempotent.

Run inside an Odoo shell on the target database (fix_real / fix_dev / a copy):

    Get-Content tooling/scripts/deploy_a05_erp_data.py | python vendor/odoo/odoo-bin shell \
        -c infra/odoo-conf/local.resolved.conf -d <DB> --no-http

Set A05_DRY_RUN=1 to print what would change and roll back.

What it applies (owner decisions D1-D12, recorded in
audit_analysis/A05_ERP_AUDIT_REPORT_2026-11-21.md):
  * the three NEW accounts (rental deposit liability, refurbished stock,
    e-waste recycling cost) plus the refurbishment absorption contra account;
    on a chart that lacks one of the other D1 accounts (fix_dev's test chart)
    it is created with fix_real's code, name and type, never re-pointed;
  * every A05 account / policy system parameter (all fail closed when unset);
  * D9 role holders: Rental Finance + Rental CFO -> the Finance Manager logins
    named by the owner (only those present on the database);
  * D12: a DRAFT M51 treatment for damage / loss compensation outside VAT,
    left unsigned and inactive for the CFO and the tax adviser.
"""

import os

DRY = os.environ.get("A05_DRY_RUN") == "1"
env = env  # noqa: F821  (odoo shell global)
company = env["res.company"].search([("name", "ilike", "1000Fix")], limit=1) or env.company
log = []

# (code, name, account_type) - D1 + D10. The four NEW ones are first.
ACCOUNTS = [
    ("200020", "Customer Security Deposit - Rental", "liability_current"),
    ("100513", "Stock of Inventory - Refurbished", "asset_current"),
    ("500910", "E-waste Collection & Recycling Cost", "expense"),
    ("600008", "Refurbishment Cost Absorbed", "expense_direct_cost"),
    # existing on fix_real; created with the same identity only where missing
    ("400108", "Rental Service Income", "income"),
    ("400111", "Loss Adjustment Income", "income_other"),
    ("400101", "Direct Sales Income", "income"),
    ("400109", "Other Income", "income_other"),
    ("200101", "Account Payable", "liability_payable"),
    ("600001", "Cost of Goods Sold-Direct Sales", "expense_direct_cost"),
    ("500905", "Write Off Inventory", "expense"),
    ("200005", "Provision For Warranty cost", "liability_current"),
    ("500229", "Warranty Cost Expense", "expense"),
]

Account = env["account.account"].sudo().with_company(company)


def account(code):
    return Account.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)


for code, name, atype in ACCOUNTS:
    if account(code):
        continue
    log.append("create account %s %s (%s)" % (code, name, atype))
    Account.create(
        {"code": code, "name": name, "account_type": atype, "company_ids": [(6, 0, [company.id])]}
    )

ICP = env["ir.config_parameter"].sudo()
tds = (ICP.get_param("cd_tax_engine_bd.account_code.tds_payable") or "").strip() or "200905"
if not account(tds):
    raise SystemExit("TDS payable account %s is missing on this database - stop" % tds)

PARAMS = {
    # M13 rental (S1)
    "cd_rental_asset.account_code.deposit_liability": "200020",
    "cd_rental_asset.account_code.recovery_income": "400111",
    "cd_rental_asset.account_code.rental_income": "400108",
    "cd_rental_asset.vat_treatment_code.damage": "A05-DAMAGE-COMP",
    "cd_rental_asset.deposit_rate_pct.low": "10",
    "cd_rental_asset.deposit_rate_pct.standard": "20",
    "cd_rental_asset.deposit_rate_pct.high": "35",
    "cd_rental_asset.hold_grace_hours": "24",
    "cd_rental_asset.min_dispatch_grade": "c",
    "cd_rental_asset.overdue_reminder_days": "1,3,7",
    "cd_rental_asset.return_due_notice_days": "1",
    "cd_rental_asset.lease_assessment_days": "365",
    # M14 trade-in (S2/S6)
    "cd_tradein.account_code.refurb_stock": "100513",
    "cd_tradein.account_code.seller_payable": "200101",
    "cd_tradein.account_code.tds_payable": tds,
    "cd_tradein.account_code.cogs": "600001",
    "cd_tradein.account_code.writeoff": "500905",
    "cd_tradein.account_code.warranty_provision": "200005",
    "cd_tradein.account_code.warranty_expense": "500229",
    "cd_tradein.account_code.refurb_absorption": "600008",
    "cd_tradein.account_code.resale_revenue": "400101",
    # warranty provision % by grade (D7/D11: A 2, B 3, C 5, D 7) ship as
    # noupdate data in cd_tradein - not set here
    # M49 transfer of a retired rental unit to resale stock (S4)
    "cd_fixed_asset_ext.account_code.resale_inventory": "100513",
    # M18 e-waste (S3)
    "cd_ewaste.account_code.recovery_income": "400109",
    "cd_ewaste.account_code.recycling_cost": "500910",
}
for key, value in PARAMS.items():
    if (ICP.get_param(key) or "") != value:
        log.append("param %s: %r -> %r" % (key, ICP.get_param(key), value))
        ICP.set_param(key, value)

# D9: role holders (owner named the logins; only those on this database)
HOLDERS = ["ashish.kumar@1000fix.com", "mainul.hasan@1000fix.com", "tanjin.rabby@1000fix.com"]
users = env["res.users"].sudo().search([("login", "in", HOLDERS), ("active", "=", True)])
for xmlid in ("cd_rental_asset.group_rental_finance", "cd_rental_asset.group_rental_cfo"):
    group = env.ref(xmlid, raise_if_not_found=False)
    if not group:
        raise SystemExit("group %s missing - upgrade cd_rental_asset first" % xmlid)
    missing = users - group.sudo().user_ids
    if missing:
        log.append("%s += %s" % (xmlid, ", ".join(missing.mapped("login"))))
        group.sudo().write({"user_ids": [(4, u.id) for u in missing]})

# D15: one company cash journal on 100108 Cash In Hand, so cash payouts
# (deposit refunds, trade-in cash at the counter) can be paid by cash voucher;
# the branch and operating unit come from each payment, not the journal
Journal = env["account.journal"].sudo().with_company(company)
cash_account = account("100108")
if not cash_account:
    raise SystemExit("cash account 100108 is missing on this database - stop")
if not Journal.search(
    [
        ("type", "=", "cash"),
        ("company_id", "=", company.id),
        ("default_account_id", "=", cash_account.id),
    ],
    limit=1,
):
    log.append("create cash journal 'Cash - Branch Counters' on 100108")
    Journal.create(
        {
            "name": "Cash - Branch Counters",
            "code": "CSHB",
            "type": "cash",
            "company_id": company.id,
            "default_account_id": cash_account.id,
        }
    )

# D12: draft M51 treatment, unsigned and inactive (state stays draft)
Treatment = env["fix.vat.treatment"].sudo()
if not Treatment.with_context(active_test=False).search(
    [("code", "=", "A05-DAMAGE-COMP"), ("company_id", "=", company.id)], limit=1
):
    log.append("create DRAFT fix.vat.treatment A05-DAMAGE-COMP (exempt) for CFO + adviser sign-off")
    Treatment.create(
        {
            "code": "A05-DAMAGE-COMP",
            "name": "Damage / loss compensation - outside VAT scope (A05, pending CFO + adviser)",
            "treatment_type": "exempt",
            "rate": 0.0,
            "company_id": company.id,
            # a superuser create is "trusted seed" and would be active at once:
            # the owner's decision is a PROPOSAL the adviser then the CFO sign
            "state": "proposed",
            "verify_with_adviser": True,
            "proposed_by_id": env.uid,
        }
    )

print("A05 deploy data on %s (%s):" % (env.cr.dbname, company.name))
for line in log or ["nothing to change"]:
    print("  " + line)
if DRY:
    env.cr.rollback()
    print("DRY RUN - rolled back")
else:
    env.cr.commit()
    print("committed")
