/** @odoo-module **/
/* A07 · Assets & Facilities — M45 Enterprise Assets & Test Equipment (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 4 reports / 4 forms / freg 64.
 * Equipment and calibration existed; kits, issue/return, transfers,
 * verification, out-of-service, PM and usage are new.
 * Capture audit 2026-11-16: classes, branch profiles, standards, recall,
 * PM plans, loss reports, blind counts and retirement added. */

export const MODULE = {
  area: 'A07', code: 'M45', en: 'Enterprise Assets & Test Equipment',
  title: 'M45 · Enterprise Assets & Test Equipment',
  bn: 'এন্টারপ্রাইজ অ্যাসেট ও টেস্ট ইকুইপমেন্ট', icon: '🧪',
  desc: 'Equipment register and classification, kits, tool-crib issue and return, transfers, physical verification, calibration schedule with certificates and trace, out-of-service enforcement, retrospective impact, PM/corrective jobs, usage per job and quality control.',
  kpis: [
    { l: 'Equipment', m: 'equipment_total' },
    { l: 'Calibration Not Current', m: 'calibration_not_current' },
    { l: 'Out of Service', m: 'oos_open' },
    { l: 'Issued Out', m: 'issued_out' },
    { l: 'Kits', m: 'kits' },
    { l: 'PM Open', m: 'pm_open' },
    { l: 'Missing', m: 'missing' },
    { l: 'Open Losses', m: 'loss_open' },
    { l: 'Impact Assessments Open', m: 'impact_open' },
    { l: 'Custody Overdue', m: 'custody_overdue' },
    /* A07 ERP audit 2026-11-20 M45-17: the spec's measures (§14/§15) */
    { l: 'Calibration Compliance %', m: 'calibration_compliance_pct' },
    { l: 'Availability % (365 d)', m: 'availability_pct' },
    { l: 'MTTR (h)', m: 'mttr_hours' },
    { l: 'MTBF (item-days)', m: 'mtbf_days' },
    { l: 'Custody Overdue %', m: 'custody_overdue_pct' }
  ],
  groups: [
    { en: 'Register', screens: [
      { id: 'M45-register', en: 'Equipment Register', bn: 'ইকুইপমেন্ট রেজিস্টার', t: 'g' },
      { id: 'M45-categories', en: 'Equipment Classes', bn: 'ইকুইপমেন্ট শ্রেণি', t: 'g' },
      { id: 'M45-classes', en: 'Classification', bn: 'শ্রেণিবিন্যাস', t: 'r' },
      { id: 'M45-branch-profiles', en: 'Branch Equipment Profiles', bn: 'শাখার ইকুইপমেন্ট প্রোফাইল', t: 'g' },
      { id: 'M45-kits', en: 'Kit Management', bn: 'কিট ম্যানেজমেন্ট', t: 'g' }
    ]},
    { en: 'Custody', screens: [
      { id: 'M45-issue', en: 'Tool Crib Issue / Return', bn: 'ইস্যু ও ফেরত', t: 'g' },
      { id: 'M45-transfer', en: 'Transfers', bn: 'স্থানান্তর', t: 'g' },
      { id: 'M45-audit-runs', en: 'Verification Counts', bn: 'যাচাই গণনা', t: 'g' },
      { id: 'M45-audits', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'g' },
      { id: 'M45-losses', en: 'Loss & Damage', bn: 'হারানো ও ক্ষতি', t: 'g' },
      { id: 'M45-writeoffs', en: 'Write-Offs', bn: 'রাইট-অফ', t: 'g' },
      { id: 'M45-retirements', en: 'Retirement & Disposal', bn: 'অবসর ও নিষ্পত্তি', t: 'g' }
    ]},
    { en: 'Calibration', screens: [
      { id: 'M45-calibration', en: 'Calibration Schedule', bn: 'ক্যালিব্রেশন সূচি', t: 'r' },
      { id: 'M45-certificates', en: 'Certificates & Trace', bn: 'সার্টিফিকেট ও ট্রেস', t: 'g' },
      { id: 'M45-standards', en: 'Calibration Standards', bn: 'ক্যালিব্রেশন স্ট্যান্ডার্ড', t: 'g' },
      { id: 'M45-oos', en: 'Out-of-Service Enforcement', bn: 'আউট-অব-সার্ভিস', t: 'g' },
      { id: 'M45-retro', en: 'Retrospective Impact', bn: 'পূর্ববর্তী প্রভাব', t: 'r' },
      { id: 'M45-profiles', en: 'Calibration Profiles', bn: 'ক্যালিব্রেশন প্রোফাইল', t: 'g' },
      { id: 'M45-impacts', en: 'Impact Assessments', bn: 'প্রভাব মূল্যায়ন', t: 'g' }
    ]},
    { en: 'Alerts', screens: [
      { id: 'M45-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
    ]},
    { en: 'Maintenance', screens: [
      { id: 'M45-pm', en: 'PM & Corrective', bn: 'পিএম ও সংশোধন', t: 'g' },
      { id: 'M45-pm-plans', en: 'PM Plans', bn: 'পিএম পরিকল্পনা', t: 'g' },
      { id: 'M45-usage', en: 'Usage per Job/QC', bn: 'ব্যবহার', t: 'g' }
    ]}
  ],
  reports: ['Calibration Compliance Report', 'Equipment Utilisation', 'Tool Loss & Write-Off', 'Cost of Ownership', 'Register Completeness',
    /* A07 ERP audit 2026-11-20 M45-18: the printable documents (print from the report bar) */
    'Calibration Certificate Register', 'Asset Tag Labels', 'Custody Hand-Over Slips', 'Write-Off & Disposal Memos'],
  forms: ['Equipment', 'Calibration Record', 'Issue/Return', 'Write-Off',
    'Equipment Class', 'Branch Equipment Profile', 'Return', 'Transfer', 'Kit',
    'Calibration Profile', 'Calibration Standard', 'Calibration Recall', 'Out of Service',
    'PM / Corrective Job', 'PM Plan', 'Report Fault', 'Equipment Usage',
    'Verification Count', 'Physical Verification', 'Loss / Damage Report', 'Retirement'],
  cross: ['M31 bench equipment', 'M23 ISO 7.1.5 evidence', 'M21 custodians', 'M47 branch assets'],
  /* Capture audit 2026-11-16: each page lists and captures every record it
   * covers (spec §5 FR-EAM-001..046, §10.1). Before, page 2 listed transfers
   * with no transfer capture, page 4 listed out-of-service holds with no way
   * to raise one, calibration profiles and impact assessments sat on no page,
   * and the class, branch profile, standard, recall, PM plan, loss report,
   * blind count and retirement had no record at all. */
  freg: { src: 64, sub: [
    ['1', 'Register & Classification', 10, { model: 'fix.equipment', cols: ['code', 'name', 'category_id', 'asset_tag', 'custodian_id', 'operational_status'], screens: ['M45-register', 'M45-categories', 'M45-branch-profiles', 'M45-classes'], reports: ['Register Completeness', 'Cost of Ownership', 'Tool Loss & Write-Off', 'Asset Tag Labels', 'Write-Off & Disposal Memos'], forms: ['Equipment', 'Equipment Class', 'Branch Equipment Profile', 'Write-Off'] }],
    ['2', 'Issue / Custody / Transfer', 11, { model: 'fix.equipment.issue', cols: ['name', 'equipment_id', 'custodian_id', 'issued_on', 'due_on', 'state'], screens: ['M45-issue', 'M45-transfer', 'M45-alerts'], reports: ['Custody Hand-Over Slips'], forms: ['Issue/Return', 'Return', 'Transfer'] }],
    ['3', 'Kit Management', 6, { model: 'fix.equipment.kit', cols: ['code', 'name', 'accountable_employee_id', 'state', 'active'], screens: ['M45-kits'], reports: [], forms: ['Kit'] }],
    ['4', 'Calibration Management', 16, { model: 'fix.calibration', cols: ['equipment_id', 'calibrated_on', 'result', 'next_due', 'certificate_ref'], screens: ['M45-calibration', 'M45-certificates', 'M45-profiles', 'M45-standards', 'M45-oos', 'M45-impacts', 'M45-alerts'], reports: ['Calibration Compliance Report', 'Calibration Certificate Register'], forms: ['Calibration Record', 'Calibration Profile', 'Calibration Standard', 'Calibration Recall', 'Out of Service'] }],
    ['5', 'PM & Repair', 8, { model: 'fix.equipment.pm', cols: ['name', 'equipment_id', 'pm_type', 'scheduled_on', 'done_on', 'state'], screens: ['M45-pm', 'M45-pm-plans', 'M45-oos'], reports: ['Cost of Ownership'], forms: ['PM / Corrective Job', 'PM Plan', 'Report Fault'] }],
    ['6', 'Usage Capture', 6, { model: 'fix.equipment.usage', cols: ['equipment_id', 'job_ref', 'used_on', 'uses', 'qc_result'], screens: ['M45-usage', 'M45-retro', 'M45-impacts'], reports: ['Equipment Utilisation'], forms: ['Equipment Usage'] }],
    ['7', 'Verification & Loss', 7, { model: 'fix.equipment.audit', cols: ['name', 'branch_id', 'scheduled_for', 'counter_id', 'missing_count', 'state'], screens: ['M45-audit-runs', 'M45-audits', 'M45-losses', 'M45-writeoffs', 'M45-retirements'], reports: ['Tool Loss & Write-Off'], forms: ['Verification Count', 'Physical Verification', 'Loss / Damage Report', 'Write-Off', 'Retirement'] }]
  ] }
};

export const SCREENS = {
  'M45-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M45']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M45-register': { kind: 'model_list', model: 'fix.equipment', stateField: 'operational_status',
    cols: ['code', 'name', 'category_id', 'asset_tag', 'serial_no', 'custodian_id', 'branch_id', 'measurement_critical', 'next_calibration', 'calibration_state', 'operational_status', 'approval_state', 'missing_verification_id'],
    actions: [{ m: 'action_assert_usable', l: 'Assert Usable' },
      { m: 'action_recall_calibration', l: 'Recall for Calibration', ask: 'Why is it recalled for calibration?', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request Write-Off Approval' },
      { m: 'action_recall_approval', l: 'Recall Write-Off Request' }] },
  'M45-classes': { kind: 'table_report', module: 'M45', report: 'classification', title: 'Classification', period: false },
  'M45-kits': { kind: 'model_list', model: 'fix.equipment.kit', stateField: 'state',
    cols: ['code', 'name', 'branch_id', 'accountable_employee_id', 'issue_due_on', 'state', 'active'],
    actions: [{ m: 'action_issue_kit', l: 'Issue Kit' },
      { m: 'action_return_kit', l: 'Return Kit' }] },
  'M45-issue': { kind: 'model_list', model: 'fix.equipment.issue', stateField: 'state',
    cols: ['name', 'equipment_id', 'custodian_id', 'reference', 'kit_id', 'issued_on', 'due_on', 'due_extension_count', 'is_overdue', 'overdue_level', 'handed_in_by_holder', 'state'],
    actions: [{ m: 'action_return', l: 'Return Item' },
      { m: 'action_extend_due', l: 'Extend Due', ask: 'Why is the return date extended? (set New Return Date on the issue first)', kwarg: 'reason' }] },
  'M45-transfer': { kind: 'model_list', model: 'fix.equipment.transfer', stateField: 'state',
    cols: ['name', 'equipment_id', 'from_branch_id', 'to_branch_id', 'from_custodian_id', 'to_custodian_id', 'transfer_date', 'dispatched_by_id', 'received_by_id', 'state'],
    actions: [{ m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_receive', l: 'Confirm Receipt' },
      { m: 'action_cancel', l: 'Cancel Transfer' }] },
  'M45-audits': { kind: 'model_list', model: 'fix.equipment.verification', stateField: 'state',
    cols: ['name', 'equipment_id', 'campaign_ref', 'verified_on', 'location', 'found', 'state'] },
  'M45-calibration': { kind: 'table_report', module: 'M45', report: 'calibration_schedule', title: 'Calibration Schedule', period: false },
  'M45-certificates': { kind: 'model_list', model: 'fix.calibration', stateField: 'decision_state',
    cols: ['equipment_id', 'calibrated_on', 'standard_ref', 'result', 'next_due', 'certificate_ref', 'provider_id', 'provider_accredited', 'non_accredited', 'performed_by', 'calibration_cost', 'trace_no', 'superseded_by_id', 'decision_state', 'decided_by_id', 'impact_id'],
    actions: [{ m: 'action_accept_calibration', l: 'Accept (Usage Decision)' },
      { m: 'action_reject_calibration', l: 'Reject (Usage Decision)', ask: 'Why is this calibration rejected?', kwarg: 'decision_note' }] },
  'M45-oos': { kind: 'model_list', model: 'fix.equipment.oos', stateField: 'state',
    cols: ['name', 'equipment_id', 'hold_type', 'reason', 'started_on', 'resolved_on', 'resolved_by_id', 'state'],
    actions: [{ m: 'action_resolve', l: 'Return to Service' }] },
  'M45-profiles': { kind: 'model_list', model: 'fix.calibration.profile', stateField: 'approval_state',
    cols: ['equipment_id', 'interval_months', 'provider_requirement', 'verification_only', 'proposed_interval_months', 'approval_state'],
    actions: [{ m: 'action_request_approval', l: 'Request Interval Change' },
      { m: 'action_recall_approval', l: 'Recall Interval Request' }] },
  'M45-impacts': { kind: 'model_list', model: 'fix.calibration.impact', stateField: 'state', create: false,
    cols: ['name', 'equipment_id', 'calibration_id', 'period_from', 'period_to', 'affected_uses', 'ncr_ref', 'disposition', 'state'],
    actions: [{ m: 'action_close_impact', l: 'Close Assessment' }] },
  'M45-retro': { kind: 'table_report', module: 'M45', report: 'retrospective_impact', title: 'Retrospective Impact', period: true },
  'M45-pm': { kind: 'model_list', model: 'fix.equipment.pm', stateField: 'state',
    cols: ['name', 'equipment_id', 'pm_type', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M45-usage': { kind: 'model_list', model: 'fix.equipment.usage',
    cols: ['equipment_id', 'job_ref', 'service_order_ref', 'used_on', 'uses', 'qc_result', 'calibration_id', 'fitness_state_at_use', 'used_by_id'] },

  /* Report chips -> their own computed pack */
  'M45-rpt-compliance': { kind: 'table_report', module: 'M45', report: 'calibration_compliance', title: 'Calibration Compliance Report', period: false },
  'M45-rpt-utilisation': { kind: 'table_report', module: 'M45', report: 'utilisation', period: true, title: 'Equipment Utilisation' },
  'M45-rpt-loss': { kind: 'table_report', module: 'M45', report: 'loss_writeoff', period: true, title: 'Tool Loss & Write-Off' },
  'M45-rpt-cost': { kind: 'table_report', module: 'M45', report: 'cost_of_ownership', title: 'Cost of Ownership', period: true },
  /* A07 ERP audit 2026-11-20 M45-18: printable documents (PDF from the report bar) */
  'M45-rpt-certificates': { kind: 'table_report', module: 'M45', report: 'certificate_register', title: 'Calibration Certificate Register', period: true },
  'M45-rpt-tags': { kind: 'table_report', module: 'M45', report: 'asset_tags', title: 'Asset Tag Labels', period: false },
  'M45-rpt-custody': { kind: 'table_report', module: 'M45', report: 'custody_slips', title: 'Custody Hand-Over Slips', period: true },
  'M45-rpt-memos': { kind: 'table_report', module: 'M45', report: 'writeoff_memos', title: 'Write-Off & Disposal Memos', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M45-form-equipment': {
    kind: 'model_form',
    model: 'fix.equipment',
    title: 'Equipment',
    back: 'M45-register',
    status: { field: 'operational_status', labels: {
      available: 'Available', issued: 'Issued',
      out_of_service: 'Out of Service', missing: 'Lost / Missing', retired: 'Retired' } },
    /* capture audit 2026-11-16: FR-EAM-001..006 identity and class, tabbed */
    tabs: [
      { id: 'identity', label: '1. Identity & Class', bn: '১. পরিচয় ও শ্রেণি', icon: '🏷', badge: '11' },
      { id: 'status', label: '2. Status & Calibration', bn: '২. অবস্থা ও ক্যালিব্রেশন', icon: '🧪', badge: '7' },
      { id: 'acquisition', label: '3. Acquisition & Warranty', bn: '৩. ক্রয় ও ওয়ারেন্টি', icon: '🧾', badge: '8' },
      { id: 'writeoff', label: '4. Write-Off', bn: '৪. রাইট-অফ', icon: '🗑', badge: '5' }
    ],
    sections: [
      { tab: 'identity', title: 'Equipment', note: 'Registered by a store keeper or the Quality Manager; the code is unique, and the asset tag is generated when left empty and is permanent. The class decides the control: an item of a calibration-controlled class (or with no class) needs a current calibration before it is issued or used; other classes are registered, issued and counted without one. Changing the class of a registered item is the Quality Manager\'s decision. Once registered, the branch and custodian move only on a received transfer.',
        fields: [
          { name: 'code', required: true, label: 'Equipment Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'category_id', label: 'Equipment Class',
            emptyNote: 'No equipment class exists yet: the Quality Manager adds them under Equipment Classes. Unclassified items are calibration-controlled.' },
          { name: 'asset_tag', label: 'Asset Tag (empty = generate)' },
          { name: 'manufacturer', label: 'Manufacturer' },
          { name: 'model_name', label: 'Model' },
          { name: 'serial_no', label: 'Serial Number' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'home_location', label: 'Home Location (shelf / bench)' },
          { name: 'criticality', label: 'Criticality' }
        ] },
      { tab: 'status', title: 'Status & Calibration', note: 'Calibration dates are computed from the calibration records. The operational status changes only through issue, return, out of service, a recall, a physical count, a loss report and an approved write-off; a failed, rejected or lapsed calibration puts a measurement-critical item out of service (nightly for a lapsed one).',
        fields: [
          { name: 'classification', readonly: true, label: 'Classification' },
          { name: 'measurement_critical', readonly: true, label: 'Measurement-Critical' },
          { name: 'operational_status', readonly: true, label: 'Operational Status' },
          { name: 'calibration_state', readonly: true, label: 'Calibration Status' },
          { name: 'calibration_profile_id', readonly: true, label: 'Calibration Profile' },
          { name: 'calibration_recall_note', readonly: true, label: 'Last Recall Reason' },
          { name: 'missing_verification_id', readonly: true, label: 'Missing Since Verification' }
        ] },
      { tab: 'acquisition', title: 'Acquisition & Warranty', note: 'Where it came from and its cover (FR-EAM-006): check the warranty before an internal repair is authorised. The acquisition cost decides who approves a write-off; a cost entered together with the write-off reason does not raise a capitalisation request to Finance.',
        fields: [
          { name: 'acquisition_ref', label: 'Purchase / GRN Reference' },
          { name: 'acquired_on', label: 'Acquired On' },
          { name: 'acquisition_cost', label: 'Acquisition Cost (BDT)' },
          { name: 'expected_life_months', label: 'Expected Life (months)' },
          { name: 'supplier_id', label: 'Supplier' },
          { name: 'warranty_until', label: 'Warranty Until' },
          { name: 'warranty_active', readonly: true, label: 'Under Warranty' },
          { name: 'fixed_asset_id', readonly: true, label: 'Fixed Asset (Finance)' }
        ] },
      { tab: 'writeoff', title: 'Write-Off', note: 'State the reason, then Request Write-Off Approval. Up to BDT 25,000 it is decided at Tier 2 (the Branch / Operations Manager approval group), above that at Tier 4 (the CFO / CCO / COO group), from the approver\'s inbox. The requester, and whoever reported the item lost, cannot approve it; cost and reason are locked while it is pending. An approved write-off reaches Finance as a disposal.',
        fields: [
          { name: 'retirement_reason', type: 'text', label: 'Write-Off Reason' },
          { name: 'dofa_tier_required', readonly: true, label: 'Approval Tier' },
          { name: 'approval_state', readonly: true, label: 'Write-Off Approval' },
          { name: 'retired_on', readonly: true, label: 'Retired On' },
          { name: 'retired_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },

  /* A write-off is requested on an item that EXISTS: the form first asks which
   * (pickRecord: items back in the store - the only ones the model lets go),
   * then takes the reason; its button runs action_request_approval, which routes
   * the request on the acquisition cost to an approver other than the requester
   * (BRU-EAM-11/12). The Write-Off chip opened the register list instead, with
   * nothing on it saying what to do (2026-11-12). */
  'M45-form-writeoff': {
    kind: 'model_form',
    model: 'fix.equipment',
    title: 'Request Write-Off',
    back: 'M45-register',
    newLabel: 'Request Write-Off',
    status: { field: 'operational_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the item to write off',
      note: 'Items back in the store: available, out of service or missing. An item out on issue or in transit is returned first.',
      search: 'Search code / name',
      choose: 'Write off this item',
      cols: ['code', 'name', 'category', 'custodian_id', 'operational_status', 'acquisition_cost'],
      domain: [['operational_status', 'in', ['available', 'out_of_service', 'missing']]],
      empty: 'No item is in the store to be written off.'
    },
    saveAction: {
      method: 'action_request_approval', label: 'Request Write-Off Approval',
      done: 'Write-off requested: it now waits in the approval inbox',
      kwargs: { justification: 'retirement_reason' }
    },
    sections: [
      { title: 'Step 2 of 2: Why the Item Is Written Off',
        note: 'Only the Equipment Custodian or a Quality Manager may request a write-off. It is approved on the acquisition cost (Branch / Operations Manager up to BDT 25,000, CFO / CCO / COO above), never by the requester.',
        fields: [
          { name: 'code', label: 'Code', readonly: true },
          { name: 'name', label: 'Equipment', readonly: true },
          { name: 'custodian_id', label: 'Custodian', readonly: true },
          { name: 'operational_status', label: 'Status', readonly: true },
          { name: 'acquisition_cost', label: 'Acquisition Cost (BDT)', readonly: true },
          /* readonly for the generic write; an INPUT here because saveAction
           * carries it to action_request_approval as the justification */
          { name: 'retirement_reason', type: 'text', label: 'Write-Off Reason', required: true, readonly: true }
        ] }
    ]
  },

  'M45-form-calibration': {
    kind: 'model_form',
    model: 'fix.calibration',
    title: 'Calibration Record',
    back: 'M45-certificates',
    tabs: [
      { id: 'cal', label: '1. Calibration', bn: '১. ক্যালিব্রেশন', icon: '🧪', badge: '9' },
      { id: 'trace', label: '2. Traceability & Certificate', bn: '২. ট্রেসেবিলিটি ও সার্টিফিকেট', icon: '📜', badge: '9' },
      { id: 'decision', label: '3. Usage Decision', bn: '৩. ব্যবহার সিদ্ধান্ত', icon: '✔', badge: '7' }
    ],
    sections: [
      { tab: 'cal', title: 'Calibration', note: 'The latest calibration decides: only a pass whose next-due is not past keeps the equipment usable. A fail, an overdue date or no calibration at all blocks issue, usage and QC, and a fail puts the item out of service and raises the impact assessment. With a calibration profile, record the as-found reading of every point (and the as-left where adjusted): the result is derived from the profile\'s tolerance bands, and next-due from its interval. Without one the validity is capped. A pass needs the certificate reference AND its file, the provider and who performed it, and the accreditation reference when the provider is accredited (decision D7a); the date cannot be in the future. An in-house calibration (the provider is 1000FiX itself) names the company reference standard it used. If the instrument\'s profile accepts an accredited provider only, a pass also needs Provider Accredited ticked; a pass from an external provider that is not accredited is flagged and the instrument cannot produce a QC result on it. The record is insert-only: to correct it, create a new one that names it under Corrects (a fail cannot be corrected into a pass). A Quality Manager other than the recorder can accept or reject it. While the second-person acceptance setting is off, a recorded pass certifies the instrument at once and a rejection withdraws it; when it is on, the instrument is not usable until the calibration is accepted. While the calibration role setting is off, anyone may record a calibration; when it is on, only a Calibration Technician or a Quality Manager can.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'calibrated_on', required: true, label: 'Calibrated On' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'next_due', required: true, label: 'Next Due' },
          { name: 'performed_by', label: 'Performed By' },
          { name: 'supersedes_id', label: 'Corrects' },
          { name: 'superseded_by_id', readonly: true, label: 'Superseded By' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] },
      { tab: 'trace', title: 'Traceability & Certificate', note: 'The traceability chain an auditor asks for (FR-EAM-023): who calibrated, under which accreditation, against which standard. Calibrated in-house against one of the company\'s own standards? Name it: a standard that is itself out of calibration on the day makes the calibration invalid and it is refused (BRU-EAM-04).',
        fields: [
          { name: 'standard_ref', required: true, label: 'Standard Reference (traceable to)' },
          { name: 'standard_equipment_id', label: 'Reference Standard (in-house)', domain: [['classification', '=', 'calibration_standard']],
            emptyNote: 'No calibration standard is registered: register one under Calibration Standards, or leave this empty for a laboratory calibration.' },
          { name: 'provider_id', label: 'Calibration Provider' },
          { name: 'provider_accredited', label: 'Provider Accredited' },
          { name: 'accreditation_ref', label: 'Accreditation Reference' },
          { name: 'certificate_ref', label: 'Certificate Reference' },
          { name: 'certificate_file', type: 'file', label: 'Certificate File' },
          { name: 'certificate_filename', label: 'Certificate File Name' },
          { name: 'certificate_hash', readonly: true, label: 'Certificate SHA-256' },
          { name: 'non_accredited', readonly: true, label: 'Non-Accredited Certificate' },
          { name: 'trace_no', label: 'Trace Number' }
        ] },
      { tab: 'trace', title: 'Calibration Cost', note: 'What the provider charged and how it is paid (FR-EAM-046). A vendor bill names the provider and its invoice reference; AP matches the bill to the M52 cost entry raised on save. Leave the cost empty for an in-house calibration. Fixed once saved.',
        fields: [
          { name: 'calibration_cost', label: 'Calibration Cost (BDT)' },
          { name: 'payment_method', label: 'Paid By' },
          { name: 'invoice_ref', label: 'Provider Invoice Ref' },
          { name: 'cost_employee_id', label: 'Paid by Employee' },
          { name: 'cost_entry_ref', readonly: true, label: 'M52 Cost Entry' }
        ] },
      { tab: 'decision', title: 'Usage Decision', note: 'Accept or Reject from the Certificate list. Reject asks for the reason, and puts the instrument out of service when this is its latest calibration.',
        fields: [
          { name: 'decision_state', readonly: true, label: 'Usage Decision' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'decision_note', type: 'text', label: 'Usage Decision Note' },
          { name: 'as_found_out_of_tolerance', readonly: true, label: 'As-Found Out of Tolerance' },
          { name: 'profile_id', readonly: true, label: 'Calibration Profile' },
          { name: 'impact_id', readonly: true, label: 'Impact Assessment' }
        ] }
    ],
    lines: {
      field: 'reading_ids',
      title: 'As-Found / As-Left Readings',
      note: 'One line per measurement point of this instrument\'s profile: each choice names its instrument and band. The band comes from the profile, never from the line, and shows on the line once saved. Readings are fixed once the calibration is saved: to correct them, record a new calibration.',
      lockOnRecord: true,
      fields: [
        { name: 'point_id', required: true, label: 'Measurement Point' },
        { name: 'as_found', required: true, label: 'As Found' },
        { name: 'adjusted', label: 'Adjusted' },
        { name: 'as_left', label: 'As Left' },
        { name: 'tolerance_low', readonly: true, label: 'Lower Limit' },
        { name: 'tolerance_high', readonly: true, label: 'Upper Limit' }
      ]
    }
  },

  'M45-form-issue': {
    kind: 'model_form',
    model: 'fix.equipment.issue',
    title: 'Issue / Return',
    back: 'M45-issue',
    status: { field: 'state', labels: { issued: 'Issued', returned: 'Returned' } },
    sections: [
      { title: 'Issue', note: 'Issued by a store keeper or Quality Manager (never to themselves), only an available, calibrated item, to one custodian at a time. Once issued, the item, the holder and the dates are fixed: a new holder is a return and a new issue, and the return date moves only by Extend Due (set New Return Date, then Extend Due with the reason). A store keeper records the condition on return: serviceable goes back to Available (unless it went out of service meanwhile), damaged goes Out of Service. A return by the holder is a hand-in: the item waits Out of Service for a store keeper\'s condition check. Overdue is escalated nightly: the holder, then the branch manager (+3 days), then the Quality Manager (+7).',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'custodian_id', required: true, label: 'Custodian' },
          { name: 'reference', label: 'Job / Ticket Ref' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'due_on', label: 'Due On' },
          { name: 'proposed_due_on', label: 'New Return Date (for Extend Due)' },
          { name: 'due_original_on', readonly: true, label: 'Originally Due' },
          { name: 'due_extension_note', readonly: true, type: 'text', label: 'Extension History' },
          { name: 'condition_out', label: 'Condition Out' },
          { name: 'return_condition', label: 'Condition on Return' },
          { name: 'condition_in', label: 'Condition In (damage detail)' },
          { name: 'returned_on', readonly: true, label: 'Returned On' },
          { name: 'kit_id', readonly: true, label: 'Kit' },
          { name: 'overdue_level', readonly: true, label: 'Overdue Escalation' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M45-form-oos': {
    kind: 'model_form',
    model: 'fix.equipment.oos',
    title: 'Out of Service',
    back: 'M45-oos',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    sections: [
      { title: 'Out of Service', note: 'Opening an out-of-service record (a fault) sets the equipment status to Out of Service; failed, rejected and lapsed calibrations and returns open their own. Return to Service is a Quality Manager\'s decision and needs a passing calibration recorded after the item went out of service, by someone other than the person who opened the record and, unless already accepted, other than the person who recorded that calibration. A return held only for its condition check is cleared by a store keeper. Write-off is requested on the equipment.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'hold_type', readonly: true, label: 'Hold Type' },
          { name: 'calibration_id', readonly: true, label: 'Triggering Calibration' },
          { name: 'started_on', readonly: true, label: 'Started On' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'resolved_on', readonly: true, label: 'Resolved On' },
          { name: 'resolved_by_id', readonly: true, label: 'Resolved By' },
          { name: 'resolution_calibration_id', readonly: true, label: 'Re-calibration' }
        ] }
    ]
  },

  'M45-form-kit': {
    kind: 'model_form',
    model: 'fix.equipment.kit',
    title: 'Kit',
    back: 'M45-kits',
    sections: [
      { title: 'Kit', fields: [
          { name: 'name', required: true, label: 'Kit Name' },
          { name: 'code', required: true, label: 'Kit Code' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'description', type: 'text', label: 'Description' },
          { name: 'active', label: 'Active' }
        ] },
      { title: 'Issue / Return as One Unit', note: 'Issue Kit hands every member to the holder in one step (each member must be fit and available, or none is issued). While the kit is out, set the condition below and save, then Return Kit: it returns every member with that condition and records the completeness check. Returning the members one by one does the same when the last one is back. The condition applies to that return only. Members cannot change while the kit is out.',
        fields: [
          { name: 'issue_to_id', label: 'Issue To' },
          { name: 'issue_due_on', label: 'Return Due' },
          { name: 'return_condition', label: 'Condition on Return' },
          { name: 'accountable_employee_id', readonly: true, label: 'Accountable Holder' },
          { name: 'state', readonly: true, label: 'Kit Status' },
          { name: 'completeness_checked_at', readonly: true, label: 'Completeness Checked' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Kit Equipment',
      note: 'Each equipment item appears once per kit.',
      fields: [{ name: 'equipment_id', required: true, label: 'Equipment' }]
    }
  },

  'M45-form-transfer': {
    kind: 'model_form',
    model: 'fix.equipment.transfer',
    title: 'Equipment Transfer',
    back: 'M45-transfer',
    status: { field: 'state', labels: {
      draft: 'Draft', dispatched: 'Dispatched', received: 'Received',
      cancelled: 'Cancelled', posted: 'Posted (legacy)' } },
    sections: [
      { title: 'Transfer', note: 'Draft, then Dispatch, then Confirm Receipt. The origin is taken from the register. Only an available item travels. The sender stays accountable until someone other than the sender confirms receipt; only then do the equipment\'s branch and custodian change.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'from_branch_id', readonly: true, label: 'From Branch' },
          { name: 'to_branch_id', required: true, label: 'To Branch' },
          { name: 'from_custodian_id', readonly: true, label: 'From Custodian' },
          { name: 'to_custodian_id', label: 'To Custodian' },
          { name: 'transfer_date', required: true, label: 'Transfer Date' },
          { name: 'notes', label: 'Notes' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'dispatched_by_id', readonly: true, label: 'Dispatched By' },
          { name: 'dispatched_on', readonly: true, label: 'Dispatched On' },
          { name: 'received_by_id', readonly: true, label: 'Received By' },
          { name: 'received_on', readonly: true, label: 'Received On' }
        ] }
    ]
  },

  'M45-form-verification': {
    kind: 'model_form',
    model: 'fix.equipment.verification',
    title: 'Physical Verification',
    back: 'M45-audits',
    status: { field: 'state', labels: {
      verified: 'Verified', missing: 'Missing' } },
    sections: [
      { title: 'Verification', note: 'The state follows Found: Found = No is stored as Missing, feeds the loss report and makes the item Lost / Missing (not usable, issued or transferred). A Missing result is final; a later count by a store keeper that finds the item recovers it, and must state where it was found under Location. A missing item is written off on the equipment, within the authority matrix.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'campaign_ref', required: true, label: 'Campaign' },
          { name: 'verified_on', required: true, label: 'Verified On' },
          { name: 'location', label: 'Location' },
          { name: 'found', label: 'Found' },
          { name: 'condition', label: 'Condition' },
          { name: 'verifier_id', label: 'Verifier' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M45-form-pm': {
    kind: 'model_form',
    model: 'fix.equipment.pm',
    title: 'PM / Corrective Job',
    back: 'M45-pm',
    status: { field: 'state', labels: { open: 'Open', done: 'Done' } },
    sections: [
      { title: 'Job', note: 'Mark Done needs completion notes and the technician; a done job is frozen. A corrective job states the symptom and where it is repaired: internally (the maintenance spine raises the M31 work order) or by a named external provider. Record the downtime the job caused (FR-EAM-036).',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'pm_type', required: true, label: 'Type' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'description', label: 'Work To Do' },
          { name: 'symptom', label: 'Symptom (corrective)' },
          { name: 'repair_route', label: 'Repaired' },
          { name: 'external_provider_id', label: 'External Provider' },
          { name: 'downtime_hours', label: 'Downtime (hours)' },
          { name: 'plan_id', readonly: true, label: 'PM Plan' },
          { name: 'cost', label: 'Cost' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'notes', label: 'Completion Notes' },
          { name: 'done_on', readonly: true, label: 'Done On' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M45-form-usage': {
    kind: 'model_form',
    model: 'fix.equipment.usage',
    title: 'Equipment Usage',
    back: 'M45-usage',
    sections: [
      { title: 'Usage', note: 'A use dated today needs the instrument fit today. A late entry is judged at its own date, so it is accepted if the instrument was fit on that day, even if it has failed since; if that date falls in a suspect window, the use joins the impact assessment. The date and QC result cannot change once saved.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'job_ref', required: true, label: 'Job / Work Order' },
          { name: 'service_order_ref', label: 'Service Order' },
          { name: 'used_on', required: true, label: 'Used On' },
          { name: 'uses', label: 'Uses' },
          { name: 'qc_result', required: true, label: 'QC Result' },
          { name: 'notes', label: 'Notes' },
          { name: 'calibration_id', readonly: true, label: 'Calibration at Use' },
          { name: 'fitness_state_at_use', readonly: true, label: 'Calibration Status at Use' },
          { name: 'used_by_id', readonly: true, label: 'Recorded By' }
        ] }
    ]
  },

  'M45-form-profile': {
    kind: 'model_form',
    model: 'fix.calibration.profile',
    title: 'Calibration Profile',
    back: 'M45-profiles',
    status: { field: 'approval_state', labels: {
      none: 'No Request', pending: 'Interval Change Pending', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Profile', note: 'Owned by the Quality Manager. The interval sets next-due for every calibration of the instrument; the measurement points carry the tolerance bands the readings are judged against.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'interval_months', required: true, label: 'Calibration Interval (months)' },
          { name: 'required_traceability', label: 'Required Traceability' },
          { name: 'provider_requirement', required: true, label: 'Provider Requirement' },
          { name: 'verification_only', label: 'Verification Only' }
        ] },
      { title: 'Interval Change', note: 'Propose the new interval with its stability-history justification, then Request Interval Change: a Quality Manager other than the requester approves it from the inbox, and never one who has calibrated this instrument. A Calibration Technician can fill in only this section. The justification answers one request and is cleared once approved.',
        fields: [
          { name: 'proposed_interval_months', label: 'Proposed Interval (months)' },
          { name: 'interval_change_reason', type: 'text', label: 'Justification' },
          { name: 'approval_state', readonly: true, label: 'Interval Change Approval' }
        ] }
    ],
    lines: {
      field: 'point_ids',
      title: 'Measurement Points',
      note: 'Lower and upper limits are absolute readings.',
      fields: [
        { name: 'name', required: true, label: 'Measurement Point' },
        { name: 'unit', label: 'Unit' },
        { name: 'nominal', label: 'Nominal' },
        { name: 'tolerance_low', required: true, label: 'Lower Limit' },
        { name: 'tolerance_high', required: true, label: 'Upper Limit' }
      ]
    }
  },

  'M45-form-impact': {
    kind: 'model_form',
    model: 'fix.calibration.impact',
    title: 'Impact Assessment',
    back: 'M45-impacts',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Impact Assessment', note: 'Raised by the system when a calibration finds the instrument out of tolerance (ISO 9001 7.1.5.2): every recorded use since the last good calibration is listed, and an NCR is raised. A Quality Manager who did not record the failing calibration records the disposition and closes it.',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'equipment_id', readonly: true, label: 'Equipment' },
          { name: 'calibration_id', readonly: true, label: 'Calibration' },
          { name: 'last_good_calibration_id', readonly: true, label: 'Last Good Calibration' },
          { name: 'period_from', readonly: true, label: 'Suspect From' },
          { name: 'period_to', readonly: true, label: 'Suspect To' },
          { name: 'affected_uses', readonly: true, label: 'Affected Uses' },
          { name: 'ncr_ref', readonly: true, label: 'NCR' },
          { name: 'disposition', label: 'Disposition' },
          { name: 'disposition_note', type: 'text', label: 'What Was Checked' },
          { name: 'decided_by_id', readonly: true, label: 'Closed By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ],
    lines: {
      field: 'usage_line_ids',
      title: 'Affected Uses',
      note: 'Every recorded use inside the suspect window, including late entries made after this assessment was raised.',
      readonlyGrid: true,
      fields: [
        { name: 'job_ref', readonly: true, label: 'Job / Work Order' },
        { name: 'service_order_ref', readonly: true, label: 'Service Order' },
        { name: 'used_on', readonly: true, label: 'Used On' },
        { name: 'uses', readonly: true, label: 'Uses' },
        { name: 'qc_result', readonly: true, label: 'QC Result' },
        { name: 'calibration_id', readonly: true, label: 'Calibration at Use' },
        { name: 'fitness_state_at_use', readonly: true, label: 'Calibration Status at Use' },
        { name: 'used_by_id', readonly: true, label: 'Recorded By' }
      ]
    }
  },

  /* ============ Capture audit 2026-11-16: the new registers ============ */
  'M45-categories': { kind: 'model_list', model: 'fix.equipment.category',
    note: 'The class decides the control: a calibration-controlled class needs a current calibration before any of its items is issued, used or put on a QC record; the other classes are registered, issued and counted without one. Classes are kept by the Quality Manager.',
    cols: ['code', 'name', 'classification', 'requires_calibration', 'requires_verification', 'data_bearing', 'critical', 'equipment_count', 'approval_state', 'active'],
    actions: [{ m: 'action_request_approval', l: 'Request Control Switch-Off' },
      { m: 'action_recall_approval', l: 'Recall Control Request' }] },
  'M45-branch-profiles': { kind: 'model_list', model: 'fix.branch.equipment.profile',
    note: 'What each branch should hold, per class. A critical class with no fit, available item at the branch is a capability exception (BRU-EAM-20).',
    cols: ['branch_id', 'category_id', 'minimum_quantity', 'held_count', 'fit_count', 'shortfall', 'capability_exception', 'critical'] },
  'M45-standards': { kind: 'model_list', model: 'fix.equipment', stateField: 'operational_status',
    note: 'The company\'s own reference standards: equipment of a Calibration Standard class. A calibration made against a standard that is out of calibration on the day is refused (BRU-EAM-04).',
    domain: [['classification', '=', 'calibration_standard']],
    cols: ['code', 'name', 'serial_no', 'custodian_id', 'branch_id', 'next_calibration', 'calibration_state', 'operational_status'] },
  'M45-pm-plans': { kind: 'model_list', model: 'fix.equipment.pm.plan', stateField: 'active',
    note: 'Each active plan raises a preventive job when its interval has passed (or its uses are reached) since the item\'s last completed job of the plan, once, every night. Raise Due Jobs does it now.',
    cols: ['name', 'equipment_id', 'category_id', 'trigger_type', 'interval_value', 'interval_unit', 'next_due', 'open_jobs', 'active'],
    actions: [{ m: 'action_raise_due_jobs', l: 'Raise Due Jobs' }] },
  'M45-losses': { kind: 'model_list', model: 'fix.equipment.loss', stateField: 'state',
    note: 'A lost or stolen item is Lost / Missing until it is recovered or written off; a damaged one is out of service and goes to repair or write-off. The person who reported a loss never approves its write-off (BRU-EAM-12).',
    cols: ['name', 'equipment_id', 'kind', 'occurred_on', 'custodian_at_loss_id', 'value_impact', 'recharge_amount', 'recharge_hr_decision', 'reported_by_id', 'state'],
    actions: [{ m: 'action_recover', l: 'Recovered', ask: 'Where was it found?', kwarg: 'note' },
      { m: 'action_send_to_repair', l: 'Send to Repair' },
      { m: 'action_request_writeoff', l: 'Request Write-Off' },
      { m: 'action_hr_approve_recharge', l: 'HR: Approve Recharge', ask: 'HR note (optional)', kwarg: 'note' },
      { m: 'action_hr_reject_recharge', l: 'HR: Reject Recharge', ask: 'Why does HR reject the recharge?', kwarg: 'note' }] },
  'M45-audit-runs': { kind: 'model_list', model: 'fix.equipment.audit', stateField: 'state',
    note: 'A blind count of a branch: the counter records what they find, and on completion every item the register expects in that store but nobody found is recorded missing. Items out on issue or in transit are accounted for by their custody.',
    cols: ['name', 'branch_id', 'scope', 'scheduled_for', 'counter_id', 'expected_count', 'found_count', 'missing_count', 'variance_value', 'reviewed_by_id', 'state'],
    actions: [{ m: 'action_start', l: 'Start Count' },
      { m: 'action_complete', l: 'Complete Count' },
      { m: 'action_approve_count', l: 'Approve Discrepancy', ask: 'Why were the items not found?', kwarg: 'reason' }] },
  'M45-writeoffs': { kind: 'model_list', model: 'fix.equipment', stateField: 'approval_state', create: false,
    note: 'Items lost or missing, and every write-off requested or approved. Request one with the Write-Off chip; it is decided on the acquisition cost from the approver inbox.',
    domain: ['|', ['operational_status', '=', 'missing'], ['approval_state', 'in', ['pending', 'approved', 'rejected']]],
    cols: ['code', 'name', 'custodian_id', 'operational_status', 'acquisition_cost', 'dofa_tier_required', 'approval_state', 'retired_on'],
    actions: [{ m: 'action_recall_approval', l: 'Recall Write-Off Request' }] },
  'M45-retirements': { kind: 'model_list', model: 'fix.equipment.retirement', stateField: 'state',
    note: 'Retirement is approved as a write-off within the authority matrix; disposal follows. A data-bearing item leaves only with its M06 erasure certificate (BRU-EAM-16).',
    cols: ['name', 'equipment_id', 'basis', 'data_bearing', 'replacement_required', 'disposal_route', 'state'],
    actions: [{ m: 'action_request', l: 'Request Retirement' },
      { m: 'action_dispose', l: 'Record Disposal' }] },
  'M45-rpt-completeness': { kind: 'table_report', module: 'M45', report: 'register_completeness', title: 'Register Completeness', period: false },

  'M45-form-category': {
    kind: 'model_form',
    model: 'fix.equipment.category',
    title: 'Equipment Class',
    back: 'M45-categories',
    sections: [
      { title: 'Equipment Class', note: 'Kept by the Quality Manager. Measuring instruments and calibration standards are calibration-controlled by default, IT assets data-bearing. Moving a registered item to another class is also the Quality Manager\'s decision, because it can switch its calibration control off.',
        fields: [
          { name: 'code', required: true, label: 'Class Code' },
          { name: 'name', required: true, label: 'Class Name' },
          { name: 'classification', required: true, label: 'Classification' },
          { name: 'requires_calibration', label: 'Calibration Controlled' },
          { name: 'requires_verification', label: 'Periodic Verification (ESD, torque)' },
          { name: 'data_bearing', label: 'Data-Bearing' },
          { name: 'default_calibration_months', label: 'Default Calibration Interval (months)' },
          { name: 'critical', label: 'Critical (work stops without it)' },
          { name: 'active', label: 'Active' },
          { name: 'equipment_count', readonly: true, label: 'Items' }
        ] },
      { title: 'Switch Calibration Control Off', note: 'Taking a class out of calibration control releases all its instruments from the fitness gate (BRU-EAM-01 has no override), so it is never a tick: state why, then Request Control Switch-Off. A Quality Manager other than you approves it from the inbox. Open calibration and recall holds stay open until each item passes a re-calibration. An item moves to an uncontrolled class only while it is in calibration.',
        fields: [
          { name: 'proposed_classification', label: 'Proposed Classification (optional)' },
          { name: 'control_change_reason', type: 'text', label: 'Why Calibration Control Is Switched Off' },
          { name: 'approval_state', readonly: true, label: 'Approval' }
        ] }
    ]
  },

  'M45-form-branch-profile': {
    kind: 'model_form',
    model: 'fix.branch.equipment.profile',
    title: 'Branch Equipment Profile',
    back: 'M45-branch-profiles',
    sections: [
      { title: 'What the Branch Should Hold', note: 'One line per branch and class, kept by the Quality Manager. Held counts every item of the class registered at the branch that is not lost or retired; Fit & Available only those in the store and in calibration.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'category_id', required: true, label: 'Equipment Class' },
          { name: 'minimum_quantity', required: true, label: 'Minimum Held' },
          { name: 'critical', label: 'Critical for the Branch' },
          { name: 'effective_from', label: 'Effective From' },
          { name: 'active', label: 'Active' },
          { name: 'held_count', readonly: true, label: 'Held' },
          { name: 'fit_count', readonly: true, label: 'Fit & Available' },
          { name: 'shortfall', readonly: true, label: 'Shortfall' },
          { name: 'capability_exception', readonly: true, label: 'Capability Exception' }
        ] }
    ]
  },

  'M45-form-standard': {
    kind: 'model_form',
    model: 'fix.equipment',
    title: 'Calibration Standard',
    newLabel: 'Register Calibration Standard',
    back: 'M45-standards',
    status: { field: 'operational_status' },
    sections: [
      { title: 'Reference Standard', note: 'A standard is equipment of a Calibration Standard class, calibrated itself like any instrument. Record its own calibration in Certificates & Trace; while it is out of calibration nothing can be calibrated against it.',
        fields: [
          { name: 'code', required: true, label: 'Equipment Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'category_id', required: true, label: 'Standard Class', domain: [['classification', '=', 'calibration_standard']],
            emptyNote: 'No Calibration Standard class exists yet: the Quality Manager adds one under Equipment Classes.' },
          { name: 'manufacturer', label: 'Manufacturer' },
          { name: 'model_name', label: 'Model' },
          { name: 'serial_no', label: 'Serial Number' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'acquisition_cost', label: 'Acquisition Cost (BDT)' },
          { name: 'calibration_state', readonly: true, label: 'Calibration Status' },
          { name: 'next_calibration', readonly: true, label: 'Next Calibration' }
        ] }
    ]
  },

  /* A recall is made on an item that exists: pick it, say why. */
  'M45-form-recall': {
    kind: 'model_form',
    model: 'fix.equipment',
    title: 'Calibration Recall',
    newLabel: 'Recall for Calibration',
    back: 'M45-register',
    status: { field: 'operational_status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the instrument to recall',
      note: 'Measurement-critical items that are in use: in the store, issued or out of service.',
      search: 'Search code / name',
      choose: 'Recall this instrument',
      cols: ['code', 'name', 'custodian_id', 'branch_id', 'next_calibration', 'calibration_state', 'operational_status'],
      domain: [['measurement_critical', '=', true], ['operational_status', 'in', ['available', 'issued', 'out_of_service']]],
      empty: 'No measurement-critical instrument is in use.'
    },
    saveAction: {
      method: 'action_recall_calibration', label: 'Recall for Calibration',
      done: 'Recalled: the instrument is out of service until a passing calibration returns it',
      kwargs: { reason: 'calibration_recall_note' }
    },
    sections: [
      { title: 'Step 2 of 2: Why It Is Recalled',
        note: 'A Quality Manager or Calibration Technician recalls. The instrument is unavailable at once, its holder gets a to-do to hand it in, and it returns to service only on a passing calibration recorded after the recall (FR-EAM-029).',
        fields: [
          { name: 'code', label: 'Code', readonly: true },
          { name: 'name', label: 'Instrument', readonly: true },
          { name: 'custodian_id', label: 'Custodian', readonly: true },
          { name: 'next_calibration', label: 'Next Calibration', readonly: true },
          { name: 'calibration_state', label: 'Calibration Status', readonly: true },
          { name: 'calibration_recall_note', label: 'Recall Reason', required: true, readonly: true }
        ] }
    ]
  },

  /* A return closes an issue that exists: pick it, record the condition. */
  'M45-form-return': {
    kind: 'model_form',
    model: 'fix.equipment.issue',
    title: 'Return Equipment',
    newLabel: 'Return Equipment',
    back: 'M45-issue',
    status: { field: 'state', labels: { issued: 'Issued', returned: 'Returned' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the item being handed back',
      note: 'Items out on issue.',
      search: 'Search issue / equipment',
      choose: 'Return this item',
      cols: ['name', 'equipment_id', 'custodian_id', 'issued_on', 'due_on', 'is_overdue'],
      domain: [['state', '=', 'issued']],
      empty: 'Nothing is out on issue.'
    },
    saveAction: {
      method: 'action_return', label: 'Record Return',
      done: 'Returned',
      kwargs: { condition: 'return_condition', detail: 'condition_in' }
    },
    sections: [
      { title: 'Step 2 of 2: Condition on Return',
        note: 'A serviceable item goes back to Available (unless it went out of service meanwhile); a damaged one goes Out of Service and to repair or write-off, never straight back to stock (BRU-EAM-10). Describe any damage.',
        fields: [
          { name: 'name', label: 'Issue', readonly: true },
          { name: 'equipment_id', label: 'Equipment', readonly: true },
          { name: 'custodian_id', label: 'Returned By (Custodian)', readonly: true },
          { name: 'due_on', label: 'Due On', readonly: true },
          { name: 'return_condition', label: 'Condition on Return', required: true, readonly: true },
          { name: 'condition_in', label: 'Damage Detail', readonly: true }
        ] }
    ]
  },

  'M45-form-pm-plan': {
    kind: 'model_form',
    model: 'fix.equipment.pm.plan',
    title: 'PM Plan',
    back: 'M45-pm-plans',
    sections: [
      { title: 'Preventive Maintenance Plan', note: 'For one item or for every item of a class (choose one). An elapsed-time plan counts days or months from the item\'s last completed job of the plan (or from Counting From); a usage plan counts recorded uses. The job raised is a preventive job on PM & Corrective, which the maintenance spine turns into a work order.',
        fields: [
          { name: 'equipment_id', label: 'Equipment' },
          { name: 'category_id', label: 'or Equipment Class' },
          { name: 'trigger_type', required: true, label: 'Trigger' },
          { name: 'interval_value', required: true, label: 'Every' },
          { name: 'interval_unit', required: true, label: 'Unit' },
          { name: 'start_on', required: true, label: 'Counting From' },
          { name: 'task', type: 'text', required: true, label: 'Work To Do' },
          { name: 'active', label: 'Active' },
          { name: 'next_due', readonly: true, label: 'Next Due' },
          { name: 'open_jobs', readonly: true, label: 'Open Jobs' }
        ] }
    ]
  },

  'M45-form-loss': {
    kind: 'model_form',
    model: 'fix.equipment.loss',
    title: 'Loss / Damage Report',
    newLabel: 'Report Loss / Damage',
    back: 'M45-losses',
    status: { field: 'state', labels: {
      reported: 'Reported', recovered: 'Recovered', repair: 'Sent to Repair',
      writeoff_requested: 'Write-Off Requested', written_off: 'Written Off' } },
    tabs: [
      { id: 'report', label: '1. Report', bn: '১. রিপোর্ট', icon: '📝', badge: '9' },
      { id: 'decision', label: '2. Accountability & Decision', bn: '২. দায় ও সিদ্ধান্ত', icon: '⚖', badge: '8' }
    ],
    sections: [
      { tab: 'report', title: 'What Happened', note: 'Anyone can report. A lost or stolen item becomes Lost / Missing at once; a damaged one goes out of service. Who held it, and its value, are taken from the register when you save.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment', domain: [['operational_status', '!=', 'retired']] },
          { name: 'kind', required: true, label: 'Lost / Stolen / Damaged' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'circumstances', type: 'text', required: true, label: 'Circumstances' },
          { name: 'police_report_ref', label: 'Police Report (GD) Ref' },
          { name: 'evidence_file', type: 'file', label: 'Evidence (photo, GD copy)' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'recharge_employee_id', label: 'Recharge To (employee)' },
          { name: 'recharge_amount', label: 'Recharge Amount (BDT)' }
        ] },
      { tab: 'decision', title: 'Accountability & Decision', note: 'Decide from the Loss & Damage list: Recovered (where it was found), Send to Repair (a corrective job is raised) or Request Write-Off, approved within the authority matrix and never by the person who reported it.',
        fields: [
          { name: 'reported_by_id', readonly: true, label: 'Reported By' },
          { name: 'reported_on', readonly: true, label: 'Reported On' },
          { name: 'custodian_at_loss_id', readonly: true, label: 'Custodian at Loss' },
          { name: 'value_impact', readonly: true, label: 'Value (BDT)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'decision_note', readonly: true, label: 'Decision Note' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'repair_job_id', readonly: true, label: 'Repair Job' }
        ] },
      { tab: 'decision', title: 'Staff Recharge (HR decision)', note: 'A recharge to an employee is recovered only on an HR-approved recovery decision, through payroll within the statutory deduction limit (decision D9). HR approves or rejects it from the Loss & Damage list; not the person who reported the loss. Employee and amount are fixed once HR decides. Payroll is told once the write-off is approved.',
        fields: [
          { name: 'recharge_hr_decision', readonly: true, label: 'HR Decision' },
          { name: 'recharge_hr_decided_by_id', readonly: true, label: 'HR Decision By' },
          { name: 'recharge_hr_decided_on', readonly: true, label: 'HR Decision On' },
          { name: 'recharge_hr_note', readonly: true, label: 'HR Note' },
          { name: 'recharge_requested_on', readonly: true, label: 'Sent to Payroll' }
        ] }
    ]
  },

  'M45-form-audit': {
    kind: 'model_form',
    model: 'fix.equipment.audit',
    title: 'Verification Count',
    newLabel: 'Schedule Verification Count',
    back: 'M45-audit-runs',
    status: { field: 'state', labels: { draft: 'Draft', counting: 'Counting', review: 'Discrepancy Review', done: 'Done' } },
    sections: [
      { title: 'Count', note: 'Scheduled by a store keeper or Quality Manager. The counter may not be who scheduled it, the custodian of any item of the branch, or the branch\'s own store keeper, and closes the count themself once started (Complete Count). The count is blind: scan the tag of each item you find. If anything the register expects was not found, the count waits for a reviewer (not the counter or scheduler) to Approve Discrepancy with the reason; only then are the items recorded missing (AC-14, AUT-EAM-12/13).',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'scheduled_for', required: true, label: 'Scheduled For' },
          { name: 'counter_id', required: true, label: 'Counter' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'expected_count', readonly: true, label: 'Expected' },
          { name: 'found_count', readonly: true, label: 'Found' },
          { name: 'missing_count', readonly: true, label: 'Missing' },
          { name: 'unexpected_count', readonly: true, label: 'Registered Elsewhere' },
          { name: 'variance_value', readonly: true, label: 'Missing Value (BDT)' },
          { name: 'completed_by_id', readonly: true, label: 'Completed By' },
          { name: 'discrepancy_reason', type: 'text', label: 'Discrepancy Reason' },
          { name: 'reviewed_by_id', readonly: true, label: 'Discrepancy Approved By' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Items Found',
      note: 'Scan the tag (or type the code or serial) of each item you find, once. The list is final once the count is closed.',
      fields: [
        { name: 'scanned_code', label: 'Scanned Tag / Code / Serial' },
        { name: 'equipment_id', label: 'Equipment Found' },
        { name: 'found_location', label: 'Found At' },
        { name: 'condition', label: 'Condition' }
      ]
    }
  },

  'M45-form-retirement': {
    kind: 'model_form',
    model: 'fix.equipment.retirement',
    title: 'Retirement & Disposal',
    newLabel: 'Recommend Retirement',
    back: 'M45-retirements',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Approval Requested', approved: 'Retired', disposed: 'Disposed' } },
    sections: [
      { title: 'Retirement Recommendation', note: 'A custodian or Quality Manager recommends; Request Retirement routes it as the item\'s write-off within the authority matrix (acquisition cost required). An item already written off goes straight to disposal.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment', domain: [['operational_status', 'in', ['available', 'out_of_service', 'missing', 'retired']]] },
          { name: 'basis', required: true, label: 'Basis' },
          { name: 'justification', type: 'text', required: true, label: 'Justification' },
          { name: 'replacement_required', label: 'Replacement Needed' },
          { name: 'replacement_note', label: 'Replacement Justification (M16)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' }
        ] },
      { title: 'Disposal', note: 'Recorded by a Quality Manager once the item is retired. A data-bearing item gets its M06 erasure request when the retirement is approved and does not leave until M06 certifies the erasure (BRU-EAM-16); the certificate number is filled in from M06. E-waste and resale need their batch or sale reference; a resale needs the buyer and the sale proceeds, which M49 books the gain or loss against.',
        fields: [
          { name: 'data_bearing', readonly: true, label: 'Data-Bearing' },
          { name: 'disposal_route', label: 'Disposal Route' },
          { name: 'erasure_certificate_ref', label: 'M06 Erasure Certificate' },
          { name: 'wipe_request_id', readonly: true, label: 'M06 Erasure Request' },
          { name: 'wipe_state', readonly: true, label: 'Erasure Status' },
          { name: 'disposal_ref', label: 'E-Waste Batch / Sale Reference' },
          { name: 'sale_amount', label: 'Sale Proceeds (BDT)' },
          { name: 'buyer_partner_id', label: 'Buyer' },
          { name: 'disposed_by_id', readonly: true, label: 'Disposed By' },
          { name: 'disposed_on', readonly: true, label: 'Disposed On' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M45:Calibration Compliance Report': 'M45-rpt-compliance',
  'M45:Equipment Utilisation': 'M45-rpt-utilisation',
  'M45:Tool Loss & Write-Off': 'M45-rpt-loss',
  'M45:Cost of Ownership': 'M45-rpt-cost',
  'M45:Register Completeness': 'M45-rpt-completeness',
  'M45:Calibration Certificate Register': 'M45-rpt-certificates',
  'M45:Asset Tag Labels': 'M45-rpt-tags',
  'M45:Custody Hand-Over Slips': 'M45-rpt-custody',
  'M45:Write-Off & Disposal Memos': 'M45-rpt-memos'
};

export const FORM_MODELS = {
  'M45:Equipment': 'fix.equipment',
  'M45:Calibration Record': 'fix.calibration',
  'M45:Issue/Return': 'fix.equipment.issue',
  'M45:Write-Off': 'fix.equipment',
  'M45:Equipment Class': 'fix.equipment.category',
  'M45:Branch Equipment Profile': 'fix.branch.equipment.profile',
  'M45:Return': 'fix.equipment.issue',
  'M45:Transfer': 'fix.equipment.transfer',
  'M45:Kit': 'fix.equipment.kit',
  'M45:Calibration Profile': 'fix.calibration.profile',
  'M45:Calibration Standard': 'fix.equipment',
  'M45:Calibration Recall': 'fix.equipment',
  'M45:Out of Service': 'fix.equipment.oos',
  'M45:PM / Corrective Job': 'fix.equipment.pm',
  'M45:PM Plan': 'fix.equipment.pm.plan',
  'M45:Report Fault': 'fix.equipment.oos',
  'M45:Equipment Usage': 'fix.equipment.usage',
  'M45:Verification Count': 'fix.equipment.audit',
  'M45:Physical Verification': 'fix.equipment.verification',
  'M45:Loss / Damage Report': 'fix.equipment.loss',
  'M45:Retirement': 'fix.equipment.retirement'
};

export const FORM_CHIPS = {
  'M45:Equipment': 'M45-form-equipment',
  'M45:Calibration Record': 'M45-form-calibration',
  'M45:Issue/Return': 'M45-form-issue',
  /* A write-off is requested on an item that already exists: the chip opens the
   * write-off form, which first asks which item. */
  'M45:Write-Off': 'M45-form-writeoff',
  /* capture audit 2026-11-16: every record a page covers has its chip */
  'M45:Equipment Class': 'M45-form-category',
  'M45:Branch Equipment Profile': 'M45-form-branch-profile',
  'M45:Return': 'M45-form-return',
  'M45:Transfer': 'M45-form-transfer',
  'M45:Kit': 'M45-form-kit',
  'M45:Calibration Profile': 'M45-form-profile',
  'M45:Calibration Standard': 'M45-form-standard',
  'M45:Calibration Recall': 'M45-form-recall',
  'M45:Out of Service': 'M45-form-oos',
  'M45:PM / Corrective Job': 'M45-form-pm',
  'M45:PM Plan': 'M45-form-pm-plan',
  'M45:Report Fault': 'M45-form-oos',
  'M45:Equipment Usage': 'M45-form-usage',
  'M45:Verification Count': 'M45-form-audit',
  'M45:Physical Verification': 'M45-form-verification',
  'M45:Loss / Damage Report': 'M45-form-loss',
  'M45:Retirement': 'M45-form-retirement',
  'M45:__by_model__': {
    'fix.equipment': 'M45-form-equipment',
    'fix.calibration': 'M45-form-calibration',
    'fix.equipment.issue': 'M45-form-issue',
    'fix.equipment.oos': 'M45-form-oos',
    'fix.equipment.kit': 'M45-form-kit',
    'fix.equipment.transfer': 'M45-form-transfer',
    'fix.equipment.verification': 'M45-form-verification',
    'fix.equipment.pm': 'M45-form-pm',
    'fix.equipment.usage': 'M45-form-usage',
    'fix.calibration.profile': 'M45-form-profile',
    'fix.calibration.impact': 'M45-form-impact',
    'fix.equipment.category': 'M45-form-category',
    'fix.branch.equipment.profile': 'M45-form-branch-profile',
    'fix.equipment.pm.plan': 'M45-form-pm-plan',
    'fix.equipment.loss': 'M45-form-loss',
    'fix.equipment.audit': 'M45-form-audit',
    'fix.equipment.retirement': 'M45-form-retirement'
  },
  'M45:__by_screen__': {
    'M45-register': 'M45-form-equipment',
    'M45-kits': 'M45-form-kit',
    'M45-issue': 'M45-form-issue',
    'M45-transfer': 'M45-form-transfer',
    'M45-audits': 'M45-form-verification',
    'M45-certificates': 'M45-form-calibration',
    'M45-oos': 'M45-form-oos',
    'M45-pm': 'M45-form-pm',
    'M45-usage': 'M45-form-usage',
    'M45-retro': 'M45-form-calibration',
    'M45-profiles': 'M45-form-profile',
    'M45-impacts': 'M45-form-impact',
    'M45-categories': 'M45-form-category',
    'M45-branch-profiles': 'M45-form-branch-profile',
    'M45-standards': 'M45-form-standard',
    'M45-pm-plans': 'M45-form-pm-plan',
    'M45-losses': 'M45-form-loss',
    'M45-audit-runs': 'M45-form-audit',
    'M45-retirements': 'M45-form-retirement'
  }
};

export const CREATE = {
  M45: { screen: 'M45-form-equipment', model: 'fix.equipment', label: 'Equipment' }
};
