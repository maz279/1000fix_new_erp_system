/** @odoo-module **/
/* A07 · Assets & Facilities — M45 Enterprise Assets & Test Equipment (v2 rebuild).
 * Registry-faithful: 4 groups / 12 screens / 4 reports / 4 forms / freg 64.
 * Equipment and calibration existed; kits, issue/return, transfers,
 * verification, out-of-service, PM and usage are new. */

export const MODULE = {
  area: 'A07', code: 'M45', en: 'Enterprise Assets & Test Equipment',
  title: 'M45 · Enterprise Assets & Test Equipment',
  bn: 'এন্টারপ্রাইজ অ্যাসেট ও টেস্ট ইকুইপমেন্ট', icon: '🧪',
  desc: 'Equipment register and classification, kits, tool-crib issue and return, transfers, physical verification, calibration schedule with certificates and trace, out-of-service enforcement, retrospective impact, PM/corrective jobs, usage per job and quality control.',
  kpis: [
    { l: 'Equipment', m: 'equipment_total' },
    { l: 'Calibration Overdue', m: 'calibration_overdue' },
    { l: 'Out of Service', m: 'oos_open' },
    { l: 'Issued Out', m: 'issued_out' },
    { l: 'Kits', m: 'kits' },
    { l: 'PM Open', m: 'pm_open' }
  ],
  groups: [
    { en: 'Register', screens: [
      { id: 'M45-register', en: 'Equipment Register', bn: 'ইকুইপমেন্ট রেজিস্টার', t: 'g' },
      { id: 'M45-classes', en: 'Classification', bn: 'শ্রেণিবিন্যাস', t: 'g' },
      { id: 'M45-kits', en: 'Kit Management', bn: 'কিট ম্যানেজমেন্ট', t: 'g' }
    ]},
    { en: 'Custody', screens: [
      { id: 'M45-issue', en: 'Tool Crib Issue / Return', bn: 'ইস্যু ও ফেরত', t: 'g' },
      { id: 'M45-transfer', en: 'Transfers', bn: 'স্থানান্তর', t: 'g' },
      { id: 'M45-audits', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'g' }
    ]},
    { en: 'Calibration', screens: [
      { id: 'M45-calibration', en: 'Calibration Schedule', bn: 'ক্যালিব্রেশন সূচি', t: 'g' },
      { id: 'M45-certificates', en: 'Certificates & Trace', bn: 'সার্টিফিকেট ও ট্রেস', t: 'g' },
      { id: 'M45-oos', en: 'Out-of-Service Enforcement', bn: 'আউট-অব-সার্ভিস', t: 'g' },
      { id: 'M45-retro', en: 'Retrospective Impact', bn: 'পূর্ববর্তী প্রভাব', t: 'g' }
    ]},
    { en: 'Maintenance', screens: [
      { id: 'M45-pm', en: 'PM & Corrective', bn: 'পিএম ও সংশোধন', t: 'g' },
      { id: 'M45-usage', en: 'Usage per Job/QC', bn: 'ব্যবহার', t: 'g' }
    ]}
  ],
  reports: ['Calibration Compliance Report', 'Equipment Utilisation', 'Tool Loss & Write-Off', 'Cost of Ownership'],
  forms: ['Equipment', 'Calibration Record', 'Issue/Return', 'Write-Off'],
  cross: ['M31 bench equipment', 'M23 ISO 7.1.5 evidence', 'M21 custodians', 'M47 branch assets'],
  freg: { src: 64, sub: [
    ['1', 'Register & Classification', 10], ['2', 'Issue / Custody / Transfer', 11],
    ['3', 'Kit Management', 6], ['4', 'Calibration Management', 16],
    ['5', 'PM & Repair', 8], ['6', 'Usage Capture', 6],
    ['7', 'Verification & Loss', 7]
  ] }
};

export const SCREENS = {
  'M45-register': { kind: 'model_list', model: 'fix.equipment', stateField: 'operational_status',
    cols: ['code', 'name', 'category', 'custodian_id', 'branch_id', 'next_calibration', 'calibration_overdue', 'operational_status'],
    actions: [{ m: 'action_assert_usable', l: 'Assert Usable' }] },
  'M45-classes': { kind: 'table_report', module: 'M45', report: 'classification', title: 'Classification', period: false },
  'M45-kits': { kind: 'model_list', model: 'fix.equipment.kit',
    cols: ['code', 'name', 'active'] },
  'M45-issue': { kind: 'model_list', model: 'fix.equipment.issue', stateField: 'state',
    cols: ['name', 'equipment_id', 'custodian_id', 'reference', 'issued_on', 'due_on', 'is_overdue', 'state'],
    actions: [{ m: 'action_return', l: 'Return Item' }] },
  'M45-transfer': { kind: 'model_list', model: 'fix.equipment.transfer', stateField: 'state',
    cols: ['name', 'equipment_id', 'from_branch_id', 'to_branch_id', 'from_custodian_id', 'to_custodian_id', 'transfer_date', 'state'] },
  'M45-audits': { kind: 'model_list', model: 'fix.equipment.verification', stateField: 'state',
    cols: ['name', 'equipment_id', 'campaign_ref', 'verified_on', 'location', 'found', 'state'] },
  'M45-calibration': { kind: 'table_report', module: 'M45', report: 'calibration_schedule', title: 'Calibration Schedule', period: false },
  'M45-certificates': { kind: 'model_list', model: 'fix.calibration',
    cols: ['equipment_id', 'calibrated_on', 'standard_ref', 'result', 'next_due', 'certificate_ref', 'trace_no'] },
  'M45-oos': { kind: 'model_list', model: 'fix.equipment.oos', stateField: 'state',
    cols: ['name', 'equipment_id', 'reason', 'started_on', 'resolved_on', 'state'],
    actions: [{ m: 'action_resolve', l: 'Resolve' }] },
  'M45-retro': { kind: 'table_report', module: 'M45', report: 'retrospective_impact', title: 'Retrospective Impact', period: false },
  'M45-pm': { kind: 'model_list', model: 'fix.equipment.pm', stateField: 'state',
    cols: ['name', 'equipment_id', 'pm_type', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M45-usage': { kind: 'model_list', model: 'fix.equipment.usage',
    cols: ['equipment_id', 'job_ref', 'service_order_ref', 'used_on', 'uses', 'qc_result'] },

  /* Report chips -> their own computed pack */
  'M45-rpt-compliance': { kind: 'table_report', module: 'M45', report: 'calibration_compliance', title: 'Calibration Compliance Report', period: false },
  'M45-rpt-utilisation': { kind: 'table_report', module: 'M45', report: 'utilisation', title: 'Equipment Utilisation', period: false },
  'M45-rpt-loss': { kind: 'table_report', module: 'M45', report: 'loss_writeoff', title: 'Tool Loss & Write-Off', period: false },
  'M45-rpt-cost': { kind: 'table_report', module: 'M45', report: 'cost_of_ownership', title: 'Cost of Ownership', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M45-form-equipment': {
    kind: 'model_form',
    model: 'fix.equipment',
    title: 'Equipment',
    back: 'M45-register',
    status: { field: 'operational_status', labels: {
      available: 'Available', issued: 'Issued',
      out_of_service: 'Out of Service', retired: 'Retired' } },
    sections: [
      { title: 'Equipment', note: 'Calibration dates are computed from the calibration records; the register stores the code, category and custodian.',
        fields: [
          { name: 'code', required: true, label: 'Equipment Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'category', label: 'Category' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operational_status', required: true, label: 'Operational Status' }
        ] }
    ]
  },

  'M45-form-calibration': {
    kind: 'model_form',
    model: 'fix.calibration',
    title: 'Calibration Record',
    back: 'M45-certificates',
    sections: [
      { title: 'Calibration', note: 'A pass with a future next-due keeps the equipment usable; a fail or an overdue date blocks Assert Usable.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'calibrated_on', required: true, label: 'Calibrated On' },
          { name: 'standard_ref', label: 'Standard Reference' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'next_due', required: true, label: 'Next Due' },
          { name: 'performed_by', label: 'Performed By' },
          { name: 'certificate_ref', label: 'Certificate Reference' },
          { name: 'trace_no', label: 'Trace Number' }
        ] }
    ]
  },

  'M45-form-issue': {
    kind: 'model_form',
    model: 'fix.equipment.issue',
    title: 'Issue / Return',
    back: 'M45-issue',
    status: { field: 'state', labels: { issued: 'Issued', returned: 'Returned' } },
    sections: [
      { title: 'Issue', note: 'Issuing makes the equipment status Issued; returning restores Available. Overdue is computed against the due date.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'custodian_id', required: true, label: 'Custodian' },
          { name: 'reference', label: 'Job / Ticket Ref' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'due_on', label: 'Due On' },
          { name: 'condition_out', label: 'Condition Out' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M45-form-oos': {
    kind: 'model_form',
    model: 'fix.equipment.oos',
    title: 'Write-Off / Out of Service',
    back: 'M45-oos',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    sections: [
      { title: 'Out of Service', note: 'Opening an out-of-service record sets the equipment status to Out of Service; resolving restores Available.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'started_on', required: true, label: 'Started On' },
          { name: 'state', required: true, label: 'State' }
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
          { name: 'description', type: 'text', label: 'Description' },
          { name: 'active', label: 'Active' }
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
    sections: [
      { title: 'Transfer', note: 'A posted transfer records both branches and both custodians at the transfer date.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'from_branch_id', label: 'From Branch' },
          { name: 'to_branch_id', required: true, label: 'To Branch' },
          { name: 'from_custodian_id', label: 'From Custodian' },
          { name: 'to_custodian_id', label: 'To Custodian' },
          { name: 'transfer_date', required: true, label: 'Transfer Date' }
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
      { title: 'Verification', note: 'A record created with Found = No is stored as Missing and feeds the loss report.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'campaign_ref', required: true, label: 'Campaign' },
          { name: 'verified_on', required: true, label: 'Verified On' },
          { name: 'location', label: 'Location' },
          { name: 'found', label: 'Found' },
          { name: 'condition', label: 'Condition' },
          { name: 'verifier_id', label: 'Verifier' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Job', fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'pm_type', required: true, label: 'Type' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'cost', label: 'Cost' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M45-form-usage': {
    kind: 'model_form',
    model: 'fix.equipment.usage',
    title: 'Equipment Usage',
    back: 'M45-usage',
    sections: [
      { title: 'Usage', fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'job_ref', required: true, label: 'Job / Work Order' },
          { name: 'service_order_ref', label: 'Service Order' },
          { name: 'used_on', required: true, label: 'Used On' },
          { name: 'uses', label: 'Uses' },
          { name: 'qc_result', required: true, label: 'QC Result' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M45:Calibration Compliance Report': 'M45-rpt-compliance',
  'M45:Equipment Utilisation': 'M45-rpt-utilisation',
  'M45:Tool Loss & Write-Off': 'M45-rpt-loss',
  'M45:Cost of Ownership': 'M45-rpt-cost'
};

export const FORM_MODELS = {
  'M45:Equipment': 'fix.equipment',
  'M45:Calibration Record': 'fix.calibration',
  'M45:Issue/Return': 'fix.equipment.issue',
  'M45:Write-Off': 'fix.equipment.oos'
};

export const FORM_CHIPS = {
  'M45:Equipment': 'M45-form-equipment',
  'M45:Calibration Record': 'M45-form-calibration',
  'M45:Issue/Return': 'M45-form-issue',
  'M45:Write-Off': 'M45-form-oos',
  'M45:__by_model__': {
    'fix.equipment': 'M45-form-equipment',
    'fix.calibration': 'M45-form-calibration',
    'fix.equipment.issue': 'M45-form-issue',
    'fix.equipment.oos': 'M45-form-oos',
    'fix.equipment.kit': 'M45-form-kit',
    'fix.equipment.transfer': 'M45-form-transfer',
    'fix.equipment.verification': 'M45-form-verification',
    'fix.equipment.pm': 'M45-form-pm',
    'fix.equipment.usage': 'M45-form-usage'
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
    'M45-retro': 'M45-form-calibration'
  }
};

export const CREATE = {
  M45: { screen: 'M45-form-equipment', model: 'fix.equipment', label: 'Equipment' }
};
