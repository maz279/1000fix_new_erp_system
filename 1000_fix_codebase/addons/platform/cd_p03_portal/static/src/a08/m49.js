/** @odoo-module **/
/* A08 · Finance & Treasury — M49 Fixed Assets & Capex.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: cd_fixed_asset_ext; reports + KPIs in controllers/a08/m49.py. */

export const MODULE = {
  area: 'A08', code: 'M49', en: 'Fixed Assets & Capex', title: 'M49 · Fixed Assets & Capex',
  bn: 'স্থায়ী সম্পদ ও ক্যাপেক্স', icon: '🏗️',
  desc: 'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification, IFRS 16 leases.',
  kpis: [
    { l: 'Gross Block', m: 'm49_gross_block' },
    { l: 'NBV', m: 'm49_nbv' },
    { l: 'CWIP Open', m: 'm49_cwip_open' },
    { l: 'Depreciation MTD', m: 'm49_dep_mtd' },
    { l: 'Lease Liability', m: 'm49_lease_liability' }
  ],
  groups: [
    { en: 'Capex', screens: [
      { id: 'M49-requests', en: 'Capex Requests', bn: 'ক্যাপেক্স অনুরোধ', t: 'g' },
      { id: 'M49-budget', en: 'Capital Budget', bn: 'মূলধনী বাজেট', t: 'g' },
      { id: 'M49-capex-budget', en: 'Capex vs Budget', bn: 'ক্যাপেক্স বনাম বাজেট', t: 'r' }
    ]},
    { en: 'Register', screens: [
      { id: 'M49-register', en: 'Asset Register', bn: 'সম্পদ রেজিস্টার', t: 'g' },
      { id: 'M49-cwip', en: 'CWIP Tracking', bn: 'সিডব্লিউআইপি', t: 'g' },
      { id: 'M49-transfer', en: 'Transfers & Custodians', bn: 'স্থানান্তর', t: 'g' },
      { id: 'M49-categories', en: 'Asset Categories', bn: 'সম্পদের শ্রেণি', t: 'g' }
    ]},
    { en: 'Depreciation', screens: [
      { id: 'M49-dep', en: 'Dual-Book Depreciation', bn: 'দ্বৈত অবচয়', t: 'g' },
      { id: 'M49-dualbook', en: 'Book vs Tax Depreciation', bn: 'হিসাব বনাম কর অবচয়', t: 'r' },
      { id: 'M49-schedules', en: 'Schedules & Movements', bn: 'সূচি', t: 'r' },
      { id: 'M49-nbv', en: 'NBV by Category', bn: 'শ্রেণিভিত্তিক নিট মূল্য', t: 'r' },
      { id: 'M49-gl-recon', en: 'Register to GL Reconciliation', bn: 'রেজিস্টার ও খতিয়ান মিলকরণ', t: 'r' },
      { id: 'M49-taxrates', en: 'Tax Depreciation Rates', bn: 'কর অবচয়ের হার', t: 'r' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M49-impairment', en: 'Revaluation & Impairment', bn: 'পুনর্মূল্যায়ন', t: 'g' },
      { id: 'M49-disposal', en: 'Disposal & Write-Off', bn: 'নিষ্পত্তি', t: 'g' },
      { id: 'M49-disposal-gl', en: 'Disposal Gains/Losses', bn: 'নিষ্পত্তির লাভ/ক্ষতি', t: 'r' },
      { id: 'M49-verify', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'g' },
      { id: 'M49-verify-results', en: 'Verification Results', bn: 'যাচাইয়ের ফলাফল', t: 'g' }
    ]},
    { en: 'Leases (IFRS 16)', screens: [
      { id: 'M49-leases', en: 'Lease Contracts', bn: 'ইজারা চুক্তি', t: 'g' },
      { id: 'M49-lease-schedule', en: 'Lease Schedules', bn: 'ইজারা সূচি', t: 'g' },
      { id: 'M49-lease-summary', en: 'Lease Summary', bn: 'ইজারা সারসংক্ষেপ', t: 'r' }
    ]}
  ],
  reports: ['Fixed Asset Movement Schedule', 'Depreciation (Dual Book)', 'NBV by Category', 'Capex vs Budget', 'Disposal Gains/Losses', 'IFRS 16 Lease Summary'],
  forms: ['Capex Request', 'Asset Capitalisation', 'Transfer', 'Disposal', 'Revaluation / Impairment', 'Lease Contract'],
  cross: ['Financial Accounting & GL', 'Enterprise Assets & Test Equipment', 'Fleet & Vehicles'],
  freg: { src: 66, sub: [
    ['1', 'Capex & Approval', 9, { model: 'fix.capex.request', cols: ['name', 'title', 'request_date', 'amount', 'state'], screens: ['M49-requests', 'M49-budget', 'M49-capex-budget'], reports: ['Capex vs Budget'], forms: ['Capex Request'] }],
    ['2', 'Register & Capitalisation', 11, { model: 'fix.fixed.asset', cols: ['code', 'name', 'category_id', 'gross', 'state'], screens: ['M49-register', 'M49-categories', 'M49-nbv', 'M49-leases'], reports: ['NBV by Category', 'IFRS 16 Lease Summary', 'Fixed Asset Movement Schedule'], forms: ['Asset Capitalisation', 'Lease Contract'] }],
    ['3', 'Componentisation', 5, { model: 'fix.cwip.entry', cols: ['name', 'category_id', 'life_months', 'amount', 'asset_id'], screens: ['M49-cwip'], reports: [], forms: [] }],
    ['4', 'Dual-Book Depreciation', 12, { model: 'fix.asset.depreciation.run', cols: ['name', 'book', 'period_start', 'total_amount', 'state'], screens: ['M49-dep', 'M49-dualbook', 'M49-schedules', 'M49-taxrates'], reports: ['Depreciation (Dual Book)', 'Fixed Asset Movement Schedule'], forms: [] }],
    ['5', 'Revaluation & Impairment', 7, { model: 'fix.asset.revaluation', cols: ['asset_id', 'kind', 'date', 'new_value', 'state'], screens: ['M49-impairment'], reports: [], forms: ['Revaluation / Impairment'] }],
    ['6', 'Transfers & Custody', 6, { model: 'fix.asset.transfer', cols: ['asset_id', 'date', 'from_operating_unit_id', 'operating_unit_id', 'state'], screens: ['M49-transfer'], reports: [], forms: ['Transfer'] }],
    ['7', 'Verification & Tagging', 7, { model: 'fix.asset.verification.campaign', cols: ['name', 'date', 'operating_unit_id', 'responsible_id', 'state'], screens: ['M49-verify', 'M49-verify-results'], reports: [], forms: [] }],
    ['8', 'Disposal', 9, { model: 'fix.asset.disposal', cols: ['asset_id', 'kind', 'date', 'gain_loss', 'state'], screens: ['M49-disposal', 'M49-disposal-gl'], reports: ['Disposal Gains/Losses'], forms: ['Disposal'] }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // Capex
  'M49-requests': { kind: 'model_list', model: 'fix.capex.request',
    cols: ['name','title','request_date','operating_unit_id','budget_id','amount','ordered_amount','requested_by_id','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit for Approval'},{m:'action_recall_approval',l:'Recall Approval Request'},
      {m:'action_reject',l:'Reject'},{m:'action_create_cwip',l:'Open CWIP Project'},
      {m:'action_link_purchase_order',l:'Link Purchase Order',ask:'Number of the draft purchase order this capex pays for',kwarg:'order'}] },
  'M49-budget': { kind: 'model_list', model: 'fix.capex.budget',
    cols: ['name','fiscal_year','date_from','date_to','operating_unit_id','amount','committed_amount','actual_amount','available_amount','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve'},{m:'action_close',l:'Close'}] },
  'M49-capex-budget': { kind: 'table_report', module: 'M49', report: 'capex_vs_budget' },
  // Register
  'M49-register': { kind: 'model_list', model: 'fix.fixed.asset',
    cols: ['code','name','category','operating_unit_id','custodian_id','purchase_date','gross','monthly_depreciation','book_nbv','state'],
    stateField: 'state', actions: [{m:'action_activate',l:'Put into Service'},{m:'action_accrue_month',l:'Accrue Month'},{m:'action_dispose',l:'Dispose'}] },
  'M49-cwip': { kind: 'model_list', model: 'fix.cwip.entry',
    cols: ['name','capex_request_id','category_id','operating_unit_id','amount','state','asset_id'],
    stateField: 'state', actions: [{m:'action_book_posted_cost',l:'Book Posted Cost',ask:'Journal entry number(s) carrying the cost on the CWIP account, comma separated',kwarg:'entries'},{m:'action_capitalise',l:'Capitalise'}] },
  'M49-transfer': { kind: 'model_list', model: 'fix.asset.transfer',
    cols: ['name','asset_id','date','from_operating_unit_id','operating_unit_id','from_custodian_id','to_custodian_id','acknowledged_by_id','state'],
    stateField: 'state', actions: [{m:'action_confirm',l:'Send (Confirm Transfer)'},{m:'action_acknowledge',l:'Acknowledge Receipt'},{m:'action_cancel',l:'Cancel'}] },
  'M49-categories': { kind: 'model_list', model: 'fix.asset.category',
    cols: ['code','name','useful_life_months','salvage_percent','tax_rate_code','journal_id','asset_account_id','accumulated_account_id','expense_account_id','cwip_account_id'] },
  // Depreciation
  'M49-dep': { kind: 'model_list', model: 'fix.asset.depreciation.run',
    cols: ['name','book','period_start','operating_unit_id','asset_count','total_amount','note','state'],
    stateField: 'state', actions: [{m:'action_compute',l:'Compute'},{m:'action_post',l:'Post'}] },
  'M49-dualbook': { kind: 'table_report', module: 'M49', report: 'dual_book' },
  'M49-schedules': { kind: 'table_report', module: 'M49', report: 'movement_schedule' },
  'M49-nbv': { kind: 'table_report', module: 'M49', report: 'nbv_by_category' },
  'M49-taxrates': { kind: 'table_report', module: 'M49', report: 'tax_depreciation_rates',
    title: 'Tax Depreciation Rates (M51 master)', period: false },
  // Lifecycle
  'M49-impairment': { kind: 'model_list', model: 'fix.asset.revaluation',
    cols: ['name','asset_id','kind','date','new_value','carrying_amount','surplus_amount','pl_amount','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit for CFO Approval'},{m:'action_post',l:'Post (approved)'},{m:'action_cancel',l:'Cancel'}] },
  'M49-disposal': { kind: 'model_list', model: 'fix.asset.disposal',
    cols: ['name','asset_id','kind','date','proceeds','nbv','gain_loss','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit for Approval'},{m:'action_post',l:'Post (approved)'},{m:'action_cancel',l:'Cancel'}] },
  'M49-disposal-gl': { kind: 'table_report', module: 'M49', report: 'disposal_gains' },
  'M49-verify': { kind: 'model_list', model: 'fix.asset.verification.campaign',
    cols: ['name','date','operating_unit_id','expected_count','found_count','misplaced_count','missing_count','unregistered_count','state'],
    stateField: 'state', actions: [{m:'action_start',l:'Start Count'},
      {m:'action_record_scan',l:'Record Scanned Tag',asks:[{label:'Scan or type the asset tag',kwarg:'tag'},{label:'Branch code it was found at (empty: its expected branch)',kwarg:'branch'}]},
      {m:'action_close',l:'Close Campaign'}] },
  'M49-verify-results': { empty: 'Verification lines are created when a verification campaign is started.', kind: 'model_list', model: 'fix.asset.verification.line',
    cols: ['campaign_id','asset_id','asset_code','operating_unit_id','scanned_tag','scanned_operating_unit_id','result'],
    stateField: 'result', create: false,
    actions: [{m:'action_mark_found',l:'Mark Found'},{m:'action_mark_missing',l:'Mark Missing'}] },
  // Leases (IFRS 16)
  'M49-leases': { kind: 'model_list', model: 'fix.lease',
    cols: ['reference','name','operating_unit_id','commencement_date','term_months','payment_amount','ibr_percent','liability_balance','state'],
    stateField: 'state', actions: [{m:'action_activate',l:'Activate (Commence)'},{m:'action_post_due',l:'Post Due Months'}] },
  'M49-lease-schedule': { empty: 'The payment schedule is generated from the lease contract.', kind: 'model_list', model: 'fix.lease.schedule.line',
    cols: ['lease_id','sequence','period_start','opening','payment','interest','principal','closing','depreciation','state'],
    stateField: 'state', create: false, actions: [{m:'action_post',l:'Post Month'}] },
  'M49-lease-summary': { kind: 'table_report', module: 'M49', report: 'lease_summary' },
  'M49-gl-recon': { kind: 'table_report', module: 'M49', report: 'register_gl_reconciliation', title: 'Register to GL Reconciliation', period: false },


  /* ===== A08 master-data forms (D365 in-workspace) ===== */
  'M49-form-budget': {
    kind: 'model_form',
    model: 'fix.capex.budget',
    title: "Capex Budget",
    back: 'M49-budget',
    status: { field: 'state', labels: { draft: "Draft", approved: "Approved", closed: "Closed" } },
    sections: [
      { title: "Budget",
        note: "A capex budget per fiscal year and asset category; committed/actual/available are computed from the requests raised against it.",
        fields: [
          { name: 'name', required: true, label: "Budget Name" },
          { name: 'fiscal_year', label: "Fiscal Year" },
          { name: 'date_from', required: true, label: "From" },
          { name: 'date_to', required: true, label: "To" },
          { name: 'category_id', label: "Asset Category" },
          { name: 'amount', required: true, label: "Budget Amount" },
          { name: 'prepared_by_id', readonly: true, label: "Prepared By" },
          { name: 'approved_by_id', readonly: true, label: "Approved By" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M49-form-cwip': {
    kind: 'model_form',
    model: 'fix.cwip.entry',
    title: "CWIP Entry",
    back: 'M49-cwip',
    status: { field: 'state', labels: { open: "Open", capitalised: "Capitalised" } },
    sections: [
      { title: "Work in Progress",
        note: "Construction-work-in-progress accumulates here until the asset is capitalised; the useful life and salvage move onto the fixed asset.",
        fields: [
          { name: 'name', required: true, label: "CWIP Reference" },
          { name: 'capex_request_id', label: "Capex Request" },
          { name: 'category_id', label: "Asset Category" },
          { name: 'amount', readonly: true, label: "Posted Cost Booked" },
          { name: 'life_months', label: "Useful Life (months)" },
          { name: 'salvage', label: "Salvage Value" },
          { name: 'state', readonly: true, label: "State" }
        ] },
      { title: "Description",
        fields: [
          { name: 'description', type: 'text', label: "Description" }
        ] }
    ]
  },
  'M49-form-category': {
    kind: 'model_form',
    model: 'fix.asset.category',
    title: "Asset Category",
    back: 'M49-categories',
    tabs: [
      { id: 'general', label: 'General', bn: 'সাধারণ' },
      { id: 'accounts', label: 'Posting Accounts', bn: 'পোস্টিং হিসাব' }
    ],
    sections: [
      { tab: 'general', title: "Category",
        note: "The category carries the default useful life and salvage percentage. Tax Rate Code is the class of the M51 Tax Rate Master (kind Tax depreciation); empty keeps the category out of the tax book.",
        fields: [
          { name: 'name', required: true, label: "Category Name" },
          { name: 'code', required: true, label: "Category Code" },
          { name: 'useful_life_months', required: true, label: "Useful Life (months)" },
          { name: 'salvage_percent', label: "Salvage %" },
          { name: 'tax_rate_code', label: "Tax Rate Code" },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'accounts', title: "Journal and GL Accounts",
        note: "Every posting refuses, naming the missing account, until these are set: capitalisation needs the asset and CWIP accounts, depreciation the expense and accumulated accounts, a revaluation the surplus and impairment accounts, a disposal the gain and loss accounts.",
        fields: [
          { name: 'journal_id', label: "Asset Journal" },
          { name: 'asset_account_id', label: "Asset Account" },
          { name: 'accumulated_account_id', label: "Accumulated Depreciation & Impairment Account" },
          { name: 'expense_account_id', label: "Depreciation Expense Account" },
          { name: 'cwip_account_id', label: "CWIP Account" },
          { name: 'revaluation_surplus_account_id', label: "Revaluation Surplus Account (OCI)" },
          { name: 'impairment_account_id', label: "Impairment / Revaluation Loss Account" },
          { name: 'gain_account_id', label: "Gain on Disposal Account" },
          { name: 'loss_account_id', label: "Loss on Disposal Account" }
        ] }
    ]
  },
  'M49-form-deprun': {
    kind: 'model_form',
    model: 'fix.asset.depreciation.run',
    title: "Depreciation Run",
    back: 'M49-dep',
    status: { field: 'state', labels: { draft: "Draft", computed: "Computed", posted: "Posted" } },
    sections: [
      { title: "Run",
        note: "One run per book and month, dated the 1st. Compute builds the lines and skips what is already charged; Post makes the entry. The accounting book posts to the GL; the tax book (ITA 2023 Third Schedule) is a memo and refuses a rate the tax adviser has not confirmed. The monthly job only prepares runs: a person posts them.",
        fields: [
          { name: 'book', required: true, label: "Book" },
          { name: 'period_start', required: true, label: "Period (1st of the month)" },
          { name: 'operating_unit_id', label: "Branch Scope (empty: every branch)" },
          { name: 'asset_ids', label: "Assets (empty: every active asset)" },
          { name: 'asset_count', readonly: true, label: "Assets Charged" },
          { name: 'total_amount', readonly: true, label: "Total Depreciation" },
          { name: 'note', readonly: true, type: 'text', label: "Run Notes" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M49-form-verify': {
    kind: 'model_form',
    model: 'fix.asset.verification.campaign',
    title: "Verification Campaign",
    back: 'M49-verify',
    status: { field: 'state', labels: { draft: "Draft", in_progress: "In Progress", closed: "Closed" } },
    sections: [
      { title: "Campaign",
        note: "A physical verification campaign; expected count is the register population, the found/missing/misplaced counts are recorded as the count progresses.",
        fields: [
          { name: 'name', required: true, label: "Campaign Name" },
          { name: 'date', required: true, label: "Date" },
          { name: 'responsible_id', label: "Responsible" },
          { name: 'expected_count', readonly: true, label: "Expected Count" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M49:Fixed Asset Movement Schedule": "M49-schedules",
  "M49:Depreciation (Dual Book)": "M49-dualbook",
  "M49:NBV by Category": "M49-nbv",
  "M49:Capex vs Budget": "M49-capex-budget",
  "M49:Disposal Gains/Losses": "M49-disposal-gl",
  "M49:IFRS 16 Lease Summary": "M49-lease-summary",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M49:Capex Request': 'fix.capex.request',
  'M49:Asset Capitalisation': 'fix.fixed.asset',
  'M49:Transfer': 'fix.asset.transfer',
  'M49:Disposal': 'fix.asset.disposal',
  'M49:Revaluation / Impairment': 'fix.asset.revaluation',
  'M49:Lease Contract': 'fix.lease',
};

/* ============ D365 IN-WORKSPACE FORM SCREENS (M49 re-audit v2) ========
 * The registry's four data-entry chips + the two extra entry surfaces open
 * Dynamics-365 record forms in the workspace — never an Odoo dialog. */
Object.assign(SCREENS, {
  'M49-form-capex': {
    kind: 'model_form',
    model: 'fix.capex.request',
    title: 'Capex Request',
    back: 'M49-requests',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Request', note: 'The request needs a budget line and an amount; approval posts the budget commitment, and the approved request is what an asset capitalisation links back to.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'request_date', required: true, label: 'Request Date' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'category_id', label: 'Asset Category' },
          { name: 'budget_id', label: 'Capex Budget' },
          { name: 'amount', required: true, label: 'Requested Amount' },
          { name: 'life_months', label: 'Useful Life (Months)' },
          { name: 'operating_unit_id', label: 'Branch' },
          { name: 'justification', type: 'text', label: 'Business Justification' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M49-form-asset': {
    kind: 'model_form',
    model: 'fix.fixed.asset',
    title: 'Asset Capitalisation',
    back: 'M49-register',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', disposed: 'Disposed' } },
    sections: [
      { title: 'Capitalised Asset', note: 'Gross, salvage, life and acquisition date drive the straight-line schedule; the draft becomes active once depreciation starts. Category and code must be unique per company.',
        fields: [
          { name: 'name', required: true, label: 'Asset Name' },
          { name: 'code', label: 'Asset Code' },
          { name: 'category_id', label: 'Asset Category' },
          { name: 'custodian_id', label: 'Custodian (initial; then by transfer)' },
          { name: 'operating_unit_id', label: 'Branch (initial; then by transfer)' },
          { name: 'seam_id', label: 'M19 Capitalisation Seam' },
          { name: 'gross', required: true, label: 'Gross' },
          { name: 'salvage', label: 'Salvage Value' },
          { name: 'life_months', required: true, label: 'Useful Life (Months)' },
          { name: 'purchase_date', required: true, label: 'Acquisition Date' },
          { name: 'depreciation_start', label: 'Depreciation Start' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M49-form-transfer': {
    kind: 'model_form',
    model: 'fix.asset.transfer',
    title: 'Asset Transfer',
    back: 'M49-transfer',
    status: { field: 'state', labels: {
      draft: 'Draft', confirmed: 'Awaiting Acknowledgement', done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Transfer', note: 'Branch or custodian transfer of one asset; the asset moves when the receiver acknowledges it.',
        fields: [
          { name: 'asset_id', required: true, label: 'Asset' },
          { name: 'date', required: true, label: 'Transfer Date' },
          { name: 'operating_unit_id', label: 'To Branch' },
          { name: 'to_custodian_id', label: 'To Custodian' },
          { name: 'reason', type: 'text', label: 'Reason' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M49-form-disposal': {
    kind: 'model_form',
    model: 'fix.asset.disposal',
    title: 'Asset Disposal',
    back: 'M49-disposal',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Disposal', note: 'Sale, scrap or write-off, approved by the authority its amount needs; a sale is invoiced through AR. Posting derecognises the asset and books the gain or loss.',
        fields: [
          { name: 'asset_id', required: true, label: 'Asset' },
          { name: 'kind', required: true, label: 'Disposal Kind' },
          { name: 'date', required: true, label: 'Disposal Date' },
          { name: 'partner_id', label: 'Buyer' },
          { name: 'proceeds', label: 'Proceeds' },
          { name: 'proceeds_account_id', label: 'Proceeds Clearing Account' },
          { name: 'incident_ref', label: 'Incident Reference (write-off)' },
          { name: 'insurance_claim_ref', label: 'Insurance Claim' },
          { name: 'ewaste_route', label: 'Physical Disposal Through M18 (E-Waste)' },
          { name: 'reason', type: 'text', label: 'Reason' },
          { name: 'ewaste_collection_ref', readonly: true, label: 'M18 Collection' },
          { name: 'tax_wdv', readonly: true, label: 'Tax WDV at Disposal' },
          { name: 'tax_balancing', readonly: true, label: 'Balancing Charge (+) / Allowance (-)' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M49-form-revaluation': {
    kind: 'model_form',
    model: 'fix.asset.revaluation',
    title: 'Revaluation / Impairment',
    back: 'M49-impairment',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Adjustment', note: 'IAS 16 revaluation, IAS 36 impairment or its reversal, with the valuer report; approved by the CFO tier, then posted. The carrying amount before and the deltas are computed on posting.',
        fields: [
          { name: 'asset_id', required: true, label: 'Asset' },
          { name: 'kind', required: true, label: 'Adjustment Kind' },
          { name: 'date', required: true, label: 'Date' },
          { name: 'new_value', required: true, label: 'New Value' },
          { name: 'basis', type: 'text', label: 'Basis / Valuer' },
          { name: 'valuer_report_file', type: 'binary', filename: 'valuer_report_filename', accept: '.pdf,.jpg,.jpeg,.png,.doc,.docx', label: 'Upload Valuer Report' },
          { name: 'valuer_report_filename', label: 'Report File Name' },
          { name: 'valuer_report_names', readonly: true, label: 'Reports Attached' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M49-form-lease': {
    kind: 'model_form',
    model: 'fix.lease',
    title: 'Lease Contract',
    back: 'M49-leases',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', ended: 'Ended' } },
    tabs: [
      { id: 'terms', label: 'Terms', bn: 'শর্তাবলি' },
      { id: 'accounts', label: 'Accounts', bn: 'হিসাব' },
      { id: 'recognition', label: 'Recognition', bn: 'স্বীকৃতি' }
    ],
    sections: [
      { tab: 'terms', title: 'IFRS 16 Lease', note: 'Commencement date, term, payment and the incremental borrowing rate generate the right-of-use asset and the lease liability schedule. Once recognised the terms are frozen.',
        fields: [
          { name: 'name', required: true, label: 'Lease' },
          { name: 'partner_id', label: 'Lessor' },
          { name: 'operating_unit_id', label: 'Branch' },
          { name: 'commencement_date', required: true, label: 'Commencement Date' },
          { name: 'term_months', required: true, label: 'Lease Term (Months)' },
          { name: 'payment_amount', required: true, label: 'Monthly Rent (Gross)' },
          { name: 'payment_timing', required: true, label: 'Payment Timing' },
          { name: 'ibr_percent', required: true, label: 'Incremental Borrowing Rate % a Year' },
          { name: 'prepaid_payments', label: 'Payments Before Commencement' },
          { name: 'initial_direct_costs', label: 'Initial Direct Costs' },
          { name: 'exemption', required: true, label: 'IFRS 16 Exemption' }
        ] },
      { tab: 'terms', title: 'From the Site Lease', note: 'A contract drafted from a recorded site lease. The rent is carried as a flat payment here: decide how the escalation enters the measurement before commencing. The deposit is refundable and is not part of the right-of-use asset.',
        fields: [
          { name: 'site_lease_id', readonly: true, label: 'Site Lease' },
          { name: 'site_escalation_pct', readonly: true, label: 'Escalation % a Year (Site Lease)' },
          { name: 'site_deposit', readonly: true, label: 'Security Deposit (Site Lease)' }
        ] },
      { tab: 'accounts', title: 'Posting Accounts', note: 'Activate refuses, naming what is missing, until the right-of-use category (with its journal and asset account) and these three accounts are set.',
        fields: [
          { name: 'category_id', label: 'Right-of-Use Category' },
          { name: 'liability_account_id', label: 'Lease Liability Account' },
          { name: 'interest_account_id', label: 'Interest Expense Account' },
          { name: 'payment_account_id', label: 'Rent Payable / Clearing Account' }
        ] },
      { tab: 'recognition', title: 'Recognised on Commencement',
        fields: [
          { name: 'pv_preview', readonly: true, label: 'Present Value (Preview)' },
          { name: 'initial_liability', readonly: true, label: 'Initial Lease Liability' },
          { name: 'rou_amount', readonly: true, label: 'Right-of-Use Asset' },
          { name: 'liability_balance', readonly: true, label: 'Liability Balance' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M49:Capex Budget': 'M49-form-budget',
  'M49:CWIP Entry': 'M49-form-cwip',
  'M49:Asset Category': 'M49-form-category',
  'M49:Depreciation Run': 'M49-form-deprun',
  'M49:Verification Campaign': 'M49-form-verify',
  'M49:Capex Request': 'M49-form-capex',
  'M49:Asset Capitalisation': 'M49-form-asset',
  'M49:Transfer': 'M49-form-transfer',
  'M49:Disposal': 'M49-form-disposal',
  'M49:Revaluation / Impairment': 'M49-form-revaluation',
  'M49:Lease Contract': 'M49-form-lease',
  'M49:__by_model__': {
    'fix.capex.budget': 'M49-form-budget',
    'fix.cwip.entry': 'M49-form-cwip',
    'fix.asset.category': 'M49-form-category',
    'fix.asset.depreciation.run': 'M49-form-deprun',
    'fix.asset.verification.campaign': 'M49-form-verify',
    'fix.capex.request': 'M49-form-capex',
    'fix.fixed.asset': 'M49-form-asset',
    'fix.asset.transfer': 'M49-form-transfer',
    'fix.asset.disposal': 'M49-form-disposal',
    'fix.asset.revaluation': 'M49-form-revaluation',
    'fix.lease': 'M49-form-lease'
  },
  'M49:__by_screen__': {
    'M49-budget': 'M49-form-budget',
    'M49-cwip': 'M49-form-cwip',
    'M49-categories': 'M49-form-category',
    'M49-dep': 'M49-form-deprun',
    'M49-verify': 'M49-form-verify',
    'M49-requests': 'M49-form-capex',
    'M49-register': 'M49-form-asset',
    'M49-transfer': 'M49-form-transfer',
    'M49-disposal': 'M49-form-disposal',
    'M49-impairment': 'M49-form-revaluation',
    'M49-leases': 'M49-form-lease'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M49: { screen: 'M49-form-capex', model: 'fix.capex.request', label: 'Capex Request' },
};
