/** @odoo-module **/
/* A08 · Finance & Treasury — M19 Financial Accounting & GL.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M19', en: 'Financial Accounting & GL', title: 'M19 · Financial Accounting & GL',
  bn: 'আর্থিক হিসাব', icon: '💰',
  desc: 'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
  kpis: [
    { l: 'Revenue MTD', m: 'revenue_mtd' },
    { l: 'Gross Margin' },
    { l: 'Close Progress', m: 'open_period_closes' },
    { l: 'Unposted Subledgers' },
    { l: 'TB Imbalance', m: 'tb_imbalance' },
    { l: 'Journals MTD', m: 'posted_moves_mtd' },
    { l: 'Drafts in Review', m: 'draft_journals' }
  ],
  groups: [
    { en: 'Ledger', screens: [
      { id: 'M19-coa', en: 'Chart of Accounts', bn: 'হিসাবের ছক', t: 'g' },
      { id: 'M19-journals', en: 'Journals', bn: 'জার্নাল', t: 'g' },
      { id: 'M19-je', en: 'Journal Entry', bn: 'জার্নাল এন্ট্রি', t: 'f' },
      { id: 'M19-tb', en: 'Trial Balance', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' },
      { id: 'M19-dimensions', en: '7-Dimension Model', bn: 'মাত্রা মডেল', t: 'g' }
    ]},
    { en: 'Close', screens: [
      { id: 'M19-close', en: 'Month-End Close Console', bn: 'মাসিক ক্লোজ', t: 'c' },
      { id: 'M19-periods', en: 'Periods & Locks', bn: 'পিরিয়ড', t: 'g' }
    ]},
    { en: 'Statements', screens: [
      { id: 'M19-bs', en: 'Balance Sheet', bn: 'উত্তরপত্র', t: 'r' },
      { id: 'M19-pl', en: 'Profit & Loss', bn: 'লাভ-ক্ষতি', t: 'r' },
      { id: 'M19-cf', en: 'Cash Flow', bn: 'নগদ প্রবাহ', t: 'r' },
      { id: 'M19-consol', en: 'Consolidation', bn: 'সমন্বয়', t: 'r' }
    ]},
    { en: 'Controls', screens: [
      { id: 'M19-suspense', en: 'Suspense & Control Accounts', bn: 'সাসপেন্স', t: 'g' },
      { id: 'M19-recon', en: 'Subledger vs Control', bn: 'উপ-খতিয়ান মিলকরণ', t: 'c' },
      { id: 'M19-audit', en: 'Immutable Audit Trail', bn: 'নিরবচ্ছিন্ন অডিট', t: 'g' }
    ]}
  ],
  reports: ['Trial Balance', 'P&L (BFRS)', 'Balance Sheet', 'Cash Flow', 'Dimensional P&L by Branch', 'Close Checklist Report'],
  forms: ['Journal Entry (manual/recurring)', 'Allocation Rule', 'Intercompany Charge'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Tax & Regulatory (BD)', 'Costing, Budget & FP&A'],
  freg: { src: 91, sub: [
    ['1', 'CoA & Dimensions', 12], ['2', 'Journals', 11], ['3', 'Subledger Posting Engine', 12],
    ['4', 'Fiscal Calendar & Close', 10], ['5', 'Multi-Entity & Consolidation', 9], ['6', 'Multi-Currency', 7],
    ['7', 'Statutory Statements', 9], ['8', 'Audit & Retention', 7], ['9', 'Accrual Framework', 8], ['10', 'Controls & SoD', 6]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M19-coa': { kind: 'coa' },
  'M19-journals': { kind: 'journals' },
  'M19-je': { kind: 'je_editor' },
  'M19-tb': { kind: 'statement', report: 'trial_balance' },
  'M19-dimensions': { kind: 'dimensions' },
  'M19-close': { kind: 'close' },
  'M19-periods': { kind: 'periods' },
  'M19-bs': { kind: 'statement', report: 'balance_sheet' },
  'M19-pl': { kind: 'statement', report: 'pnl' },
  'M19-cf': { kind: 'statement', report: 'cash_flow' },
  'M19-consol': { kind: 'statement', report: 'consolidated' },
  'M19-suspense': { kind: 'suspense' },
  'M19-recon': { kind: 'recon' },
  'M19-audit': { kind: 'audit' },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M19:Trial Balance": "M19-tb",
  "M19:P&L (BFRS)": "M19-pl",
  "M19:Balance Sheet": "M19-bs",
  "M19:Cash Flow": "M19-cf",
  "M19:Dimensional P&L by Branch": "M19-dimensions",
  "M19:Close Checklist Report": "M19-close",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M19:Journal Entry (manual/recurring)': 'account.move',
  'M19:Allocation Rule': 'fix.allocation.rule',
};

/* the module's "+ New" surface */
export const CREATE = {
  M19: { model: 'account.move', label: 'Journal Entry' },
};
