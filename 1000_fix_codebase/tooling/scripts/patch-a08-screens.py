#!/usr/bin/env python3
"""One-shot patcher for the A08 completion pass: registers the generic
controller, converts 24 screens to model_list data screens, removes them from
P03_LIVE_SCREENS, and adds report routes for M52/M50/M51/M53/M49/M54."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------- controller
p = ROOT / "addons/platform/cd_p03_portal/controllers/__init__.py"
s = p.read_text(encoding="utf-8")
if "p03_generic_api" not in s:
    s = s.replace(
        "from . import p03_registry, p03_service_order_api, p03_tellme, p03_finance_api, p03_gl_api, p03_ar_api",
        "from . import p03_registry, p03_service_order_api, p03_tellme, p03_finance_api, p03_gl_api, p03_ar_api, p03_generic_api",
    )
    p.write_text(s, encoding="utf-8", newline="\n")
    print("controller registered")

# ---------------------------------------------------------------- meta
meta = ROOT / "addons/platform/cd_p03_portal/static/src/p03_modules_meta.js"
s = meta.read_text(encoding="utf-8")

removals = [
    "'M52-bills': 'fix.vendor.invoice',",
    "'M52-match': 'fix.vendor.invoice',",
    "'M52-claims': 'fix.expense.claim',",
    "'M50-position': 'fix.cash.position',",
    "'M50-statements': 'fix.bank.statement.line',",
    "'M50-recon': 'fix.bank.statement.line',",
    "'M50-beftn': 'fix.payment.execution',",
    "'M50-mfs': 'fix.payment.execution',",
    "'M51-mushak61': 'fix.mushak.register',",
    "'M51-mushak62': 'fix.mushak.register',",
    "'M51-mushak63': 'fix.mushak.register',",
    "'M51-vat91': 'fix.vat.return',",
    "'M51-tds': 'fix.tds.return',",
    "'M51-determination': 'fix.vat.treatment',",
    "'M51-certs': 'fix.withholding.certificate',",
    "'M53-schedules': 'fix.revenue.schedule',",
    "'M53-ledger': 'fix.commission.ledger',",
    "'M53-payouts': 'fix.payout.run',",
    "'M53-sellers': 'fix.seller.statement',",
    "'M49-register': 'fix.fixed.asset',",
    "'M49-cwip': 'fix.cwip.entry',",
    "'M54-budgets': 'fix.budget',",
    "'M54-allocation': 'fix.cost.allocation',",
]
removed = 0
for r in removals:
    needle = "  " + r + "\n"
    if needle in s:
        s = s.replace(needle, "", 1)
        removed += 1
print("live-screen entries removed:", removed)

DATA_SCREENS = """  // ---- A08 completion (2026-10-25): generic model_list screens ----
  'M52-bills': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','subtotal','tds_amount','total_payable','match_state'],
    stateField: 'match_state', actions: [{m:'action_request_payment',l:'Request Payment'}] },
  'M52-match': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','total_payable','match_state','match_detail'],
    stateField: 'match_state', domain: [['match_state','!=','matched']] },
  'M52-claims': { kind: 'model_list', model: 'fix.expense.claim',
    cols: ['employee_id','description','expense_date','amount','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'}] },
  'M50-position': { kind: 'model_list', model: 'fix.cash.position',
    cols: ['as_of','bank_balance','drawer_float_total','pending_payments','total_position'] },
  'M50-statements': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state' },
  'M50-recon': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state', domain: [['match_state','=','unmatched']],
    actions: [{m:'auto_match',l:'Auto-Match'}] },
  'M50-beftn': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', actions: [{m:'action_execute',l:'Execute'}] },
  'M50-mfs': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', domain: [['method','!=','beftn']], actions: [{m:'action_execute',l:'Execute'}] },
  'M51-mushak61': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak62': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','supplier_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak63': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','total_payable','posted'],
    actions: [{m:'action_mark_posted',l:'Mark GL Posted'},{m:'action_rebuild_from_events',l:'Rebuild from Events'}] },
  'M51-vat91': { kind: 'model_list', model: 'fix.vat.return',
    cols: ['period','total_taxable','output_vat','input_vat','net_payable','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_period',l:'Prepare Period'},{m:'action_file',l:'File Return'}] },
  'M51-tds': { kind: 'model_list', model: 'fix.tds.return',
    cols: ['quarter','fiscal_year','total_withheld','deductor_count','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_quarter',l:'Prepare Quarter'},{m:'action_file',l:'File'}] },
  'M51-determination': { kind: 'model_list', model: 'fix.vat.treatment',
    cols: ['code','name','treatment_type','rate','active'] },
  'M51-certs': { kind: 'model_list', model: 'fix.withholding.certificate',
    cols: ['quarter','certificate_type','supplier_name','base_amount','rate_percent','withheld_amount','state'],
    stateField: 'state', actions: [{m:'action_issue',l:'Issue Certificate'}] },
  'M53-schedules': { kind: 'model_list', model: 'fix.revenue.schedule',
    cols: ['source_model','description','total_amount','recognized_amount','start_date','end_date','state'],
    stateField: 'state' },
  'M53-ledger': { kind: 'model_list', model: 'fix.commission.ledger',
    cols: ['name','seller_partner_id','gross_amount','commission_amount','tds_amount','net_payable','state'],
    stateField: 'state', actions: [{m:'action_post_to_gl',l:'Post Accrual to GL'}] },
  'M53-payouts': { kind: 'model_list', model: 'fix.payout.run',
    cols: ['name','period','total_gross','total_tds','total_payable','seller_count','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve (SoD)'},{m:'action_generate_beftn',l:'Generate BEFTN File'}] },
  'M53-sellers': { kind: 'model_list', model: 'fix.seller.statement',
    cols: ['seller_partner_id','period','gross_gmv','commission_amount','tds_withheld','net_payable','state'],
    stateField: 'state' },
  'M49-register': { kind: 'model_list', model: 'fix.fixed.asset',
    cols: ['name','category','gross','salvage','life_months','purchase_date','monthly_depreciation','state'],
    stateField: 'state', actions: [{m:'action_accrue_month',l:'Accrue Month'},{m:'action_dispose',l:'Dispose'}] },
  'M49-cwip': { kind: 'model_list', model: 'fix.cwip.entry',
    cols: ['name','amount','state','asset_id'],
    stateField: 'state', actions: [{m:'action_capitalise',l:'Capitalise'}] },
  'M54-budgets': { kind: 'model_list', model: 'fix.budget',
    cols: ['name','fiscal_year','planned_amount','actual_amount','variance','state'],
    stateField: 'state' },
  'M54-allocation': { kind: 'model_list', model: 'fix.cost.allocation',
    cols: ['name','direct_cost','allocated_overhead','total_cost'] },
"""
anchor = "  // ---- M20 · AR, Invoicing & Collections (CD-M20-02) — /p03/ar/* ----"
if "'M52-bills': { kind: 'model_list'" not in s:
    if anchor in s:
        s = s.replace(anchor, DATA_SCREENS + anchor, 1)
    else:
        # fallback: append into P03_DATA_SCREENS before its closing "};" — find last "};" after "M20-statements"
        marker = "'M20-statements': { kind: 'ar_statements' },"
        idx = s.find(marker)
        close = s.find("};", idx)
        s = s[:close] + DATA_SCREENS + s[close:]
    print("data screens added")

ROUTES = """
Object.assign(P03_REPORT_ROUTES, {
  "M52:AP Ageing": "M52-bills",
  "M52:TDS Deduction Register": "M52-bills",
  "M52:Payment Run Summary": "M52-bills",
  "M52:Expense by Category": "M52-claims",
  "M52:GRNI Reconciliation": "M52-match",
  "M52:Duplicate Prevention Log": "M52-match",
  "M50:Daily Cash Position": "M50-position",
  "M50:Bank Reconciliation Summary": "M50-recon",
  "M50:Gateway Settlement Reconciliation": "M50-mfs",
  "M50:COD Settlement Report": "M50-mfs",
  "M51:Mushak 9.1 Return Draft": "M51-vat91",
  "M51:VAT Reconciliation": "M51-vat91",
  "M51:TDS Annual Summary": "M51-tds",
  "M53:Commission Accrual": "M53-ledger",
  "M53:Payout Reconciliation": "M53-payouts",
  "M53:Deferred Revenue Bridge": "M53-schedules",
  "M53:Rev-Rec by Stream": "M53-schedules",
  "M53:Clawback Register": "M53-sellers",
  "M49:Fixed Asset Movement Schedule": "M49-register",
  "M49:Depreciation (Dual Book)": "M49-register",
  "M49:NBV by Category": "M49-register",
  "M49:Capex vs Budget": "M49-cwip",
  "M49:Disposal Gains/Losses": "M49-register",
  "M54:Budget vs Actual": "M54-budgets",
});
"""
if "M52:AP Ageing" not in s:
    s = s.rstrip()
    if s.endswith(";"):
        s = s[:-1]
    s += ";\n" + ROUTES
meta.write_text(s, encoding="utf-8", newline="\n")
print("meta patched")
