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
    { l: 'Calibration Not Current', m: 'calibration_not_current' },
    { l: 'Out of Service', m: 'oos_open' },
    { l: 'Issued Out', m: 'issued_out' },
    { l: 'Kits', m: 'kits' },
    { l: 'PM Open', m: 'pm_open' },
    { l: 'Missing', m: 'missing' },
    { l: 'Impact Assessments Open', m: 'impact_open' },
    { l: 'Custody Overdue', m: 'custody_overdue' }
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
      { id: 'M45-retro', en: 'Retrospective Impact', bn: 'পূর্ববর্তী প্রভাব', t: 'g' },
      { id: 'M45-profiles', en: 'Calibration Profiles', bn: 'ক্যালিব্রেশন প্রোফাইল', t: 'g' },
      { id: 'M45-impacts', en: 'Impact Assessments', bn: 'প্রভাব মূল্যায়ন', t: 'g' }
    ]},
    { en: 'Alerts', screens: [
      { id: 'M45-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
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
    ['1', 'Register & Classification', 10, { model: 'fix.equipment', cols: ['code', 'name', 'category', 'custodian_id', 'operational_status'], screens: ['M45-register', 'M45-classes'] }],
    ['2', 'Issue / Custody / Transfer', 11, { model: 'fix.equipment.issue', cols: ['name', 'equipment_id', 'custodian_id', 'issued_on', 'due_on', 'state'], screens: ['M45-issue', 'M45-transfer'] }],
    ['3', 'Kit Management', 6, { model: 'fix.equipment.kit', cols: ['code', 'name', 'active'], screens: ['M45-kits'] }],
    ['4', 'Calibration Management', 16, { model: 'fix.calibration', cols: ['equipment_id', 'calibrated_on', 'result', 'next_due', 'certificate_ref'], screens: ['M45-calibration', 'M45-certificates', 'M45-oos'] }],
    ['5', 'PM & Repair', 8, { model: 'fix.equipment.pm', cols: ['name', 'equipment_id', 'pm_type', 'scheduled_on', 'done_on', 'state'], screens: ['M45-pm'] }],
    ['6', 'Usage Capture', 6, { model: 'fix.equipment.usage', cols: ['equipment_id', 'job_ref', 'used_on', 'uses', 'qc_result'], screens: ['M45-usage', 'M45-retro'] }],
    ['7', 'Verification & Loss', 7, { model: 'fix.equipment.verification', cols: ['name', 'equipment_id', 'campaign_ref', 'verified_on', 'found', 'state'], screens: ['M45-audits'] }]
  ] }
};

export const SCREENS = {
  'M45-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M45']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M45-register': { kind: 'model_list', model: 'fix.equipment', stateField: 'operational_status',
    cols: ['code', 'name', 'category', 'custodian_id', 'branch_id', 'next_calibration', 'calibration_state', 'operational_status', 'approval_state', 'missing_verification_id'],
    actions: [{ m: 'action_assert_usable', l: 'Assert Usable' },
      { m: 'action_request_approval', l: 'Request Write-Off Approval' },
      { m: 'action_recall_approval', l: 'Recall Write-Off Request' }] },
  'M45-classes': { kind: 'table_report', module: 'M45', report: 'classification', title: 'Classification', period: false },
  'M45-kits': { kind: 'model_list', model: 'fix.equipment.kit', stateField: 'state',
    cols: ['code', 'name', 'branch_id', 'accountable_employee_id', 'issue_due_on', 'state', 'active'],
    actions: [{ m: 'action_issue_kit', l: 'Issue Kit' },
      { m: 'action_return_kit', l: 'Return Kit' }] },
  'M45-issue': { kind: 'model_list', model: 'fix.equipment.issue', stateField: 'state',
    cols: ['name', 'equipment_id', 'custodian_id', 'reference', 'kit_id', 'issued_on', 'due_on', 'is_overdue', 'overdue_level', 'state'],
    actions: [{ m: 'action_return', l: 'Return Item' }] },
  'M45-transfer': { kind: 'model_list', model: 'fix.equipment.transfer', stateField: 'state',
    cols: ['name', 'equipment_id', 'from_branch_id', 'to_branch_id', 'from_custodian_id', 'to_custodian_id', 'transfer_date', 'dispatched_by_id', 'received_by_id', 'state'],
    actions: [{ m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_receive', l: 'Confirm Receipt' },
      { m: 'action_cancel', l: 'Cancel Transfer' }] },
  'M45-audits': { kind: 'model_list', model: 'fix.equipment.verification', stateField: 'state',
    cols: ['name', 'equipment_id', 'campaign_ref', 'verified_on', 'location', 'found', 'state'] },
  'M45-calibration': { kind: 'table_report', module: 'M45', report: 'calibration_schedule', title: 'Calibration Schedule', period: false },
  'M45-certificates': { kind: 'model_list', model: 'fix.calibration', stateField: 'decision_state',
    cols: ['equipment_id', 'calibrated_on', 'standard_ref', 'result', 'next_due', 'certificate_ref', 'performed_by', 'trace_no', 'superseded_by_id', 'decision_state', 'decided_by_id', 'impact_id'],
    actions: [{ m: 'action_accept_calibration', l: 'Accept (Usage Decision)' },
      { m: 'action_reject_calibration', l: 'Reject (Usage Decision)' }] },
  'M45-oos': { kind: 'model_list', model: 'fix.equipment.oos', stateField: 'state',
    cols: ['name', 'equipment_id', 'hold_type', 'reason', 'started_on', 'resolved_on', 'resolved_by_id', 'state'],
    actions: [{ m: 'action_resolve', l: 'Return to Service' }] },
  'M45-profiles': { kind: 'model_list', model: 'fix.calibration.profile', stateField: 'approval_state',
    cols: ['equipment_id', 'interval_months', 'provider_requirement', 'verification_only', 'proposed_interval_months', 'approval_state'],
    actions: [{ m: 'action_request_approval', l: 'Request Interval Change' },
      { m: 'action_recall_approval', l: 'Recall Interval Request' }] },
  'M45-impacts': { kind: 'model_list', model: 'fix.calibration.impact', stateField: 'state',
    cols: ['name', 'equipment_id', 'calibration_id', 'period_from', 'period_to', 'affected_uses', 'ncr_ref', 'disposition', 'state'],
    actions: [{ m: 'action_close_impact', l: 'Close Assessment' }] },
  'M45-retro': { kind: 'table_report', module: 'M45', report: 'retrospective_impact', title: 'Retrospective Impact', period: false },
  'M45-pm': { kind: 'model_list', model: 'fix.equipment.pm', stateField: 'state',
    cols: ['name', 'equipment_id', 'pm_type', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M45-usage': { kind: 'model_list', model: 'fix.equipment.usage',
    cols: ['equipment_id', 'job_ref', 'service_order_ref', 'used_on', 'uses', 'qc_result', 'calibration_id', 'fitness_state_at_use', 'used_by_id'] },

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
      out_of_service: 'Out of Service', missing: 'Lost / Missing', retired: 'Retired' } },
    sections: [
      { title: 'Equipment', note: 'Registered by a store keeper or the Quality Manager; the code is unique. Calibration dates are computed from the calibration records. The operational status changes only through issue, return, out of service, a physical count and an approved write-off; a failed, rejected or lapsed calibration puts the item out of service (nightly for a lapsed one). Once registered, the branch and custodian move only on a received transfer.',
        fields: [
          { name: 'code', required: true, label: 'Equipment Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'category', label: 'Category' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operational_status', readonly: true, label: 'Operational Status' },
          { name: 'calibration_state', readonly: true, label: 'Calibration Status' },
          { name: 'calibration_profile_id', readonly: true, label: 'Calibration Profile' },
          { name: 'missing_verification_id', readonly: true, label: 'Missing Since Verification' }
        ] },
      { title: 'Write-Off', note: 'State the reason and the acquisition cost, then Request Write-Off Approval. Up to BDT 25,000 it is decided at Tier 2 (Quality Manager), above that at Tier 4 (CFO), from the approver\'s inbox. The requester cannot approve it; cost and reason are locked while it is pending.',
        fields: [
          { name: 'acquisition_cost', label: 'Acquisition Cost (BDT)' },
          { name: 'retirement_reason', type: 'text', label: 'Write-Off Reason' },
          { name: 'dofa_tier_required', readonly: true, label: 'Approval Tier' },
          { name: 'approval_state', readonly: true, label: 'Write-Off Approval' },
          { name: 'retired_on', readonly: true, label: 'Retired On' },
          { name: 'retired_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },

  'M45-form-calibration': {
    kind: 'model_form',
    model: 'fix.calibration',
    title: 'Calibration Record',
    back: 'M45-certificates',
    sections: [
      { title: 'Calibration', note: 'The latest calibration decides: only a pass whose next-due is not past keeps the equipment usable. A fail, an overdue date or no calibration at all blocks issue, usage and QC, and a fail puts the item out of service and raises the impact assessment. With a calibration profile, record the as-found reading of every point (and the as-left where adjusted): the result is derived from the profile\'s tolerance bands, and next-due from its interval. Without one the validity is capped. A pass needs the certificate and who performed it; the date cannot be in the future. The record is insert-only: to correct it, create a new one that names it under Corrects (a fail cannot be corrected into a pass). A Quality Manager other than the recorder takes the usage decision.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'calibrated_on', required: true, label: 'Calibrated On' },
          { name: 'standard_ref', label: 'Standard Reference' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'next_due', required: true, label: 'Next Due' },
          { name: 'performed_by', label: 'Performed By' },
          { name: 'certificate_ref', label: 'Certificate Reference' },
          { name: 'trace_no', label: 'Trace Number' },
          { name: 'supersedes_id', label: 'Corrects' },
          { name: 'superseded_by_id', readonly: true, label: 'Superseded By' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] },
      { title: 'Usage Decision', note: 'Accept or Reject from the Certificate list. Rejecting needs a note and puts the instrument out of service when this is its latest calibration.',
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
      note: 'One line per measurement point of the profile. The tolerance band comes from the profile, never from the line.',
      fields: [
        { name: 'point_id', required: true, label: 'Measurement Point' },
        { name: 'as_found', required: true, label: 'As Found' },
        { name: 'adjusted', label: 'Adjusted' },
        { name: 'as_left', label: 'As Left' }
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
      { title: 'Issue', note: 'Only an available, calibrated item can be issued, and to one custodian at a time. On return record the condition: a serviceable item goes back to Available (unless it went out of service meanwhile), a damaged one goes Out of Service; with no condition stated it waits Out of Service for a store keeper\'s condition check. Overdue is computed against the due date and escalated nightly.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'custodian_id', required: true, label: 'Custodian' },
          { name: 'reference', label: 'Job / Ticket Ref' },
          { name: 'issued_on', required: true, label: 'Issued On' },
          { name: 'due_on', label: 'Due On' },
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
      { title: 'Issue / Return as One Unit', note: 'Issue Kit hands every member to the holder in one step (each member must be fit and available, or none is issued). Return Kit returns every member with the condition below and records the completeness check. Members cannot change while the kit is out.',
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
      { title: 'Verification', note: 'The state follows Found: Found = No is stored as Missing, feeds the loss report and makes the item Lost / Missing (not usable, issued or transferred). A Missing result is final; a later count by a store keeper that finds the item recovers it. A missing item is written off on the equipment, within the authority matrix.',
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
      { title: 'Job', note: 'Mark Done needs completion notes and the technician; a done job is frozen.',
        fields: [
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'pm_type', required: true, label: 'Type' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
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
      { title: 'Usage', fields: [
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
      { title: 'Interval Change', note: 'Propose the new interval with its stability-history justification, then Request Interval Change: a Quality Manager other than the requester approves it from the inbox, and never one who has calibrated this instrument (BRU-EAM-13).',
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
  'M45:Write-Off': 'fix.equipment'
};

export const FORM_CHIPS = {
  'M45:Equipment': 'M45-form-equipment',
  'M45:Calibration Record': 'M45-form-calibration',
  'M45:Issue/Return': 'M45-form-issue',
  'M45:Write-Off': 'M45-form-equipment',
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
    'fix.calibration.impact': 'M45-form-impact'
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
    'M45-impacts': 'M45-form-impact'
  }
};

export const CREATE = {
  M45: { screen: 'M45-form-equipment', model: 'fix.equipment', label: 'Equipment' }
};
