/** @odoo-module **/
/* A07 · Assets & Facilities — M47 Facility & Branch Infrastructure (v2 rebuild).
 * Registry-faithful: 5 groups / 12 screens / 5 reports / 5 forms / freg 71.
 * fix.site and fix.facility.work.order existed; leases, licences, utilities,
 * occupancy, building PM, safety equipment, incidents and site projects are new. */

export const MODULE = {
  area: 'A07', code: 'M47', en: 'Facility & Branch Infrastructure', title: 'M47 · Facility & Branch Infrastructure',
  bn: 'সুবিধা ও শাখা অবকাঠামো', icon: '🏬',
  desc: 'Site register and occupancy, lease administration and critical dates, statutory licences, utilities and anomalies, branch asset register, building services PM, facility work orders, safety equipment, security incidents and site open/close projects.',
  kpis: [
    { l: 'Sites', m: 'sites_active' },
    { l: 'Lease Renewals (90d, incl. past end)', m: 'leases_expiring_90d' },
    { l: 'Licence Gaps', m: 'licences_expired' },
    { l: 'Utilities Cost /sqft (latest month)', m: 'utilities_cost_per_sqft', prefix: '৳ ' },
    { l: 'Open Facility Work Orders', m: 'open_work_orders' },
    { l: 'Safety Inspections Due', m: 'safety_due' }
  ],
  groups: [
    { en: 'Sites', screens: [
      { id: 'M47-sites', en: 'Site Register', bn: 'সাইট রেজিস্টার', t: 'g' },
      { id: 'M47-occupancy', en: 'Occupancy & Condition', bn: 'দখল ও অবস্থা', t: 'g' }
    ]},
    { en: 'Leases', screens: [
      { id: 'M47-leases', en: 'Lease Administration', bn: 'লিজ প্রশাসন', t: 'g' },
      { id: 'M47-dates', en: 'Critical-Date Control', bn: 'গুরুত্বপূর্ণ তারিখ', t: 'r' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M47-licences', en: 'Statutory Licences', bn: 'আইনি লাইসেন্স', t: 'g' },
      { id: 'M47-utilities', en: 'Utilities & Anomalies', bn: 'ইউটিলিটি', t: 'g' }
    ]},
    { en: 'Infrastructure', screens: [
      { id: 'M47-infra', en: 'Branch Asset Register', bn: 'শাখা সম্পদ', t: 'r' },
      { id: 'M47-pm', en: 'Building Services PM', bn: 'ভবন সেবা', t: 'g' },
      { id: 'M47-wo', en: 'Facility Work Orders', bn: 'সুবিধা কাজ', t: 'g' }
    ]},
    { en: 'Safety', screens: [
      { id: 'M47-safety', en: 'Safety Equipment', bn: 'নিরাপত্তা সরঞ্জাম', t: 'g' },
      { id: 'M47-security', en: 'Security & Incidents', bn: 'নিরাপত্তা ঘটনা', t: 'g' },
      { id: 'M47-opening', en: 'Site Open / Close Projects', bn: 'সাইট খোলা/বন্ধ', t: 'g' }
    ]}
  ],
  reports: ['Cost per Site / per Job', 'Lease Expiry Register', 'Licence Compliance', 'Utilities Variance', 'Facility Work Order Performance', 'Branch Asset Register'],
  forms: ['Site', 'Lease', 'Licence', 'Facility Work Order', 'Safety Inspection'],
  cross: ['M04 branch operations', 'M30 branch provisioning', 'M49 ROU assets', 'M59 safety committee'],
  freg: { src: 71, sub: [
    ['1', 'Site Register', 7, { model: 'fix.site', cols: ['name', 'site_type', 'branch_id', 'floor_area_sqm', 'state'], screens: ['M47-sites', 'M47-occupancy'] }],
    ['2', 'Lease Administration', 11, { model: 'fix.site.lease', cols: ['name', 'site_id', 'lessor_id', 'end_date', 'monthly_rent', 'state'], screens: ['M47-leases', 'M47-dates'] }],
    ['3', 'Statutory Compliance', 9, { model: 'fix.site.licence', cols: ['name', 'site_id', 'licence_type', 'valid_to', 'state'], screens: ['M47-licences', 'M47-dates'] }],
    ['4', 'Utilities', 6, { model: 'fix.site.utility', cols: ['site_id', 'period', 'utility_type', 'amount', 'flagged'], screens: ['M47-utilities'] }],
    ['5', 'Infrastructure Assets', 9, { model: 'fix.site.asset', cols: ['name', 'site_id', 'asset_type', 'tag', 'warranty_end', 'state'], screens: ['M47-infra'] }],
    ['6', 'Building PM', 7, { model: 'fix.site.pm', cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'state'], screens: ['M47-pm'] }],
    ['7', 'Work Orders', 6, { model: 'fix.facility.work.order', cols: ['name', 'site_id', 'work_type', 'scheduled_date', 'assigned_to', 'state'], screens: ['M47-wo'] }],
    ['8', 'Safety & Security', 10, { model: 'fix.site.safety', cols: ['name', 'site_id', 'equipment_type', 'next_check', 'state'], screens: ['M47-safety', 'M47-security'] }],
    ['9', 'Open / Close Projects', 6, { model: 'fix.site.project', cols: ['name', 'site_id', 'project_type', 'planned_on', 'budget', 'state'], screens: ['M47-opening'] }]
  ] }
};

export const SCREENS = {
  'M47-sites': { kind: 'model_list', model: 'fix.site', stateField: 'state',
    cols: ['name', 'site_type', 'branch_id', 'floor_area_sqm', 'lease_start', 'lease_end', 'monthly_rent', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Close / Reopen Approval (CFO + CEO)', ask: 'Business justification for the CFO and CEO', kwarg: 'justification' },
      { m: 'action_close', l: 'Close Site' },
      { m: 'action_reopen', l: 'Reopen Site' }
    ] },
  'M47-occupancy': { kind: 'model_list', model: 'fix.site.condition',
    cols: ['name', 'site_id', 'inspected_on', 'occupancy_pct', 'condition_grade', 'inspector_id', 'notes'] },
  'M47-leases': { kind: 'model_list', model: 'fix.site.lease', stateField: 'state',
    cols: ['name', 'site_id', 'lessor_id', 'start_date', 'end_date', 'monthly_rent', 'escalation_pct', 'approval_state', 'state'],
    actions: [
      { m: 'action_open_modification', l: 'Open Renewal / Modification' },
      { m: 'action_request_approval', l: 'Request Modification Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_apply_modification', l: 'Apply Approved Modification' },
      { m: 'action_discard_modification', l: 'Discard Modification' },
      { m: 'action_expire', l: 'Mark Expired' },
      { m: 'action_terminate', l: 'Terminate Lease', ask: 'Why is the lease terminated?', kwarg: 'reason' }
    ] },
  'M47-dates': { kind: 'table_report', module: 'M47', report: 'critical_dates', title: 'Critical-Date Control', period: false },
  'M47-licences': { kind: 'model_list', model: 'fix.site.licence', stateField: 'state',
    cols: ['name', 'site_id', 'licence_type', 'number', 'issued_on', 'valid_to', 'is_valid', 'state'] },
  'M47-utilities': { kind: 'model_list', model: 'fix.site.utility',
    cols: ['name', 'site_id', 'period', 'utility_type', 'amount', 'usage', 'unit', 'flagged'],
    actions: [{ m: 'action_flag', l: 'Flag Anomaly' }] },
  'M47-infra': { kind: 'model_list', model: 'fix.site.asset', stateField: 'state',
    cols: ['name', 'site_id', 'asset_type', 'tag', 'installed_on', 'warranty_end', 'value', 'state'],
    actions: [
      { m: 'action_maintenance', l: 'Take to Maintenance' },
      { m: 'action_restore', l: 'Restore to Service' },
      { m: 'action_request_approval', l: 'Request Retirement Approval (DOFA)', ask: 'Why should this asset be retired?', kwarg: 'justification' },
      { m: 'action_retire', l: 'Retire Asset', ask: 'Retirement reason', kwarg: 'reason' }
    ] },
  'M47-pm': { kind: 'model_list', model: 'fix.site.pm', stateField: 'state',
    cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'done_on', 'cost', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M47-wo': { kind: 'model_list', model: 'fix.facility.work.order', stateField: 'state',
    cols: ['name', 'site_id', 'work_type', 'scheduled_date', 'assigned_to', 'estimated_cost', 'actual_cost', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Spend Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_schedule', l: 'Schedule' },
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete', ask: 'Completion evidence: what was done and the evidence reference', kwarg: 'notes' },
      { m: 'action_verify', l: 'Verify & Close', ask: 'Verification note (optional)', kwarg: 'notes' },
      { m: 'action_reopen', l: 'Reopen', ask: 'Why is the completed work reopened?', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Cancellation reason (optional)', kwarg: 'reason' }
    ] },
  'M47-safety': { kind: 'model_list', model: 'fix.site.safety', stateField: 'state',
    cols: ['name', 'site_id', 'equipment_type', 'ref', 'last_check', 'next_check', 'state'],
    actions: [{ m: 'action_check', l: 'Record Check', ask: 'Next check date after today (YYYY-MM-DD)', kwarg: 'next_check' }] },
  'M47-security': { kind: 'model_list', model: 'fix.site.incident', stateField: 'state',
    cols: ['name', 'site_id', 'incident_type', 'occurred_on', 'severity', 'description', 'state'],
    actions: [{ m: 'action_close', l: 'Close Incident', ask: 'Resolution: root cause and action taken', kwarg: 'resolution' }] },
  'M47-opening': { kind: 'model_list', model: 'fix.site.project', stateField: 'state',
    cols: ['name', 'site_id', 'project_type', 'planned_on', 'done_on', 'budget', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Budget Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_start', l: 'Start Project' },
      { m: 'action_done', l: 'Complete Project' }
    ] },

  /* Report chips -> their own computed pack */
  'M47-rpt-cost': { kind: 'table_report', module: 'M47', report: 'cost_per_site', title: 'Cost per Site / per Job', period: false },
  'M47-rpt-lease': { kind: 'table_report', module: 'M47', report: 'lease_expiry', title: 'Lease Expiry Register', period: false },
  'M47-rpt-licence': { kind: 'table_report', module: 'M47', report: 'licence_compliance', title: 'Licence Compliance', period: false },
  'M47-rpt-utilities': { kind: 'table_report', module: 'M47', report: 'utilities_variance', title: 'Utilities Variance', period: false },
  'M47-rpt-wo': { kind: 'table_report', module: 'M47', report: 'work_order_performance', title: 'Facility Work Order Performance', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M47-form-site': {
    kind: 'model_form',
    model: 'fix.site',
    title: 'Site',
    back: 'M47-sites',
    status: { field: 'state', labels: { active: 'Active', closed: 'Closed' } },
    tabs: [
      { id: 'site', label: '1. Site', bn: '১. সাইট', icon: '🏬', badge: '10' },
      { id: 'closure', label: '2. Closure & Sign-off', bn: '২. বন্ধ ও অনুমোদন', icon: '🔐', badge: '9' }
    ],
    sections: [
      { tab: 'site', title: 'Site', note: 'The site register is the anchor for leases, licences, utilities, occupancy, safety equipment and work orders. Closing a site keeps every historical record readable.',
        fields: [
          { name: 'name', required: true, label: 'Site Name' },
          { name: 'site_type', required: true, label: 'Site Type' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'floor_area_sqm', label: 'Floor Area (sqm)' },
          { name: 'lease_start', label: 'Lease Start' },
          { name: 'lease_end', label: 'Lease End' },
          { name: 'monthly_rent', label: 'Monthly Rent' },
          { name: 'state', label: 'State (Close / Reopen actions)', readonly: true }
        ] },
      { tab: 'site', title: 'Address', note: 'Plant assets (HVAC, lift, generator, fire pump, UPS, CCTV) are recorded on the Branch Asset Register screen against this site.',
        fields: [
          { name: 'address', type: 'text', label: 'Address' }
        ] },
      { tab: 'closure', title: 'Recovery Checklist (BRU-FAC-15)', note: 'A site that still holds an active lease, an open work order or a valid licence closes only with this checklist complete. Editing it after a sign-off withdraws the sign-off.',
        fields: [
          { name: 'closure_assets_recovered', label: 'Assets Recovered (M45 / M15 / M46)' },
          { name: 'closure_licences_surrendered', label: 'Licences Surrendered' },
          { name: 'closure_deposit_settled', label: 'Deposit Recovered / Written Off' },
          { name: 'closure_notes', type: 'text', label: 'Recovery Notes' }
        ] },
      { tab: 'closure', title: 'Status-Change Sign-off (CFO, then CEO)', note: 'Closing or reopening a site needs two routed sign-offs by two different people, neither the requester nor the creator: the CFO (DOFA Tier 4), then the CEO (DOFA Tier 5). Request Approval once for each.',
        fields: [
          { name: 'approval_state', label: 'Approval Request (M63)', readonly: true },
          { name: 'status_cfo_approved_by_id', label: 'CFO Sign-off', readonly: true },
          { name: 'status_cfo_approved_at', label: 'CFO Signed At', readonly: true },
          { name: 'status_ceo_approved_by_id', label: 'CEO Sign-off', readonly: true },
          { name: 'status_ceo_approved_at', label: 'CEO Signed At', readonly: true }
        ] }
    ]
  },

  'M47-form-lease': {
    kind: 'model_form',
    model: 'fix.site.lease',
    title: 'Lease',
    back: 'M47-leases',
    status: { field: 'state', labels: { active: 'Active', expired: 'Expired', terminated: 'Terminated' } },
    tabs: [
      { id: 'lease', label: '1. Lease', bn: '১. লিজ', icon: '📄', badge: '11' },
      { id: 'modification', label: '2. Renewal / Modification', bn: '২. নবায়ন / পরিবর্তন', icon: '⚖️', badge: '7' }
    ],
    sections: [
      { tab: 'lease', title: 'Lease', note: 'The end date cannot precede the start (database CHECK). Once recorded, the dates, rent and escalation change only through a renewal or modification. The end date feeds Critical-Date Control and Lease Expiry.',
        fields: [
          { name: 'name', required: true, label: 'Lease Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'lessor_id', required: true, label: 'Lessor' },
          { name: 'start_date', required: true, label: 'Start Date' },
          { name: 'end_date', required: true, label: 'End Date' },
          { name: 'monthly_rent', label: 'Monthly Rent' },
          { name: 'escalation_pct', label: 'Escalation %' },
          { name: 'deposit', label: 'Deposit' },
          { name: 'state', label: 'State (Expire / Terminate actions)', readonly: true },
          { name: 'terminated_reason', label: 'Termination Reason', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'modification', title: 'Proposed Terms', note: 'Open Renewal / Modification copies the current terms here. Edit them, request approval (DOFA on the total remaining rent commitment), then apply. Changing a proposal after approval withdraws the approval.',
        fields: [
          { name: 'modification_open', label: 'Modification Open', readonly: true },
          { name: 'proposed_end_date', label: 'Proposed End Date' },
          { name: 'proposed_monthly_rent', label: 'Proposed Monthly Rent' },
          { name: 'proposed_escalation_pct', label: 'Proposed Escalation %' },
          { name: 'modification_reason', label: 'Reason' },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Approval Request (M63)', readonly: true }
        ] }
    ]
  },

  'M47-form-licence': {
    kind: 'model_form',
    model: 'fix.site.licence',
    title: 'Licence',
    back: 'M47-licences',
    status: { field: 'state', labels: { valid: 'Valid', expired: 'Expired', suspended: 'Suspended' } },
    sections: [
      { title: 'Statutory Licence', note: 'Valid today is computed on every read: the state must be Valid, an end date must be recorded and it must not have passed (a licence with no end date is not valid). A lapsed licence cannot be made valid again; record the renewal as a new licence. Licence Gaps counts operational sites with no current trade licence, plus any licence type a site holds with none current.',
        fields: [
          { name: 'name', required: true, label: 'Licence Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'licence_type', required: true, label: 'Licence Type' },
          { name: 'number', label: 'Licence Number' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'is_valid', label: 'Valid Today' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M47-form-wo': {
    kind: 'model_form',
    model: 'fix.facility.work.order',
    title: 'Facility Work Order',
    back: 'M47-wo',
    status: { field: 'state', labels: {
      draft: 'Draft', scheduled: 'Scheduled', in_progress: 'In Progress',
      completed: 'Completed', verified: 'Verified / Closed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'order', label: '1. Work Order', bn: '১. কাজের আদেশ', icon: '🛠️', badge: '7' },
      { id: 'cost', label: '2. Scope, Cost & Approval', bn: '২. ব্যয় ও অনুমোদন', icon: '💳', badge: '5' },
      { id: 'evidence', label: '3. Completion & Verification', bn: '৩. সমাপ্তি ও যাচাই', icon: '🔐', badge: '6' }
    ],
    sections: [
      { tab: 'order', title: 'Work Order', note: 'Draft → (spend approval) → scheduled → in progress → completed (with evidence) → verified by someone who neither raised nor completed it. Cancel before completion; Reopen voids a completion.',
        fields: [
          { name: 'name', required: true, label: 'Work Order' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_id', label: 'Target Equipment' },
          { name: 'work_type', required: true, label: 'Work Type' },
          { name: 'assigned_to', label: 'Assigned Engineer' },
          { name: 'scheduled_date', label: 'Scheduled Date' },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
        ] },
      { tab: 'cost', title: 'Scope, Cost & Approval', note: 'Any costed work order is approved under DOFA on the higher of the estimate and the actual before it is scheduled; an actual above the approved amount needs re-approval before completion. The cost is frozen once the work is completed.',
        fields: [
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'estimated_cost', label: 'Estimated Cost' },
          { name: 'actual_cost', label: 'Actual Cost' },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Spend Approval (M63)', readonly: true }
        ] },
      { tab: 'evidence', title: 'Completion & Verification (BRU-FAC-07)', note: 'Completion records the evidence and who completed it; verification closes the work order.',
        fields: [
          { name: 'completion_notes', type: 'text', label: 'Completion Evidence' },
          { name: 'completed_by_id', label: 'Completed By', readonly: true },
          { name: 'completed_at', label: 'Completed At', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'verified_at', label: 'Verified At', readonly: true },
          { name: 'verification_notes', type: 'text', label: 'Verification Notes', readonly: true }
        ] }
    ]
  },

  'M47-form-safety': {
    kind: 'model_form',
    model: 'fix.site.safety',
    title: 'Safety Inspection',
    back: 'M47-safety',
    status: { field: 'state', labels: { ok: 'OK', due: 'Due', overdue: 'Overdue' } },
    sections: [
      { title: 'Safety Equipment', note: 'The status is derived from the next check date: overdue once it has passed, due within 30 days. Record Check stamps today as the last check and asks for the next check date; the next check cannot be pushed later by editing.',
        fields: [
          { name: 'name', required: true, label: 'Check Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_type', required: true, label: 'Equipment Type' },
          { name: 'ref', label: 'Tag / Reference' },
          { name: 'last_check', label: 'Last Check' },
          { name: 'next_check', required: true, label: 'Next Check' },
          { name: 'state', label: 'Status (derived)' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-condition': {
    kind: 'model_form',
    model: 'fix.site.condition',
    title: 'Occupancy & Condition',
    back: 'M47-occupancy',
    sections: [
      { title: 'Inspection', note: 'Occupancy is a 0–100 percentage (database CHECK); the grade is the recorded judgement of the inspector.',
        fields: [
          { name: 'name', required: true, label: 'Inspection Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'inspected_on', required: true, label: 'Inspected On' },
          { name: 'occupancy_pct', label: 'Occupancy %' },
          { name: 'condition_grade', required: true, label: 'Condition Grade' },
          { name: 'inspector_id', label: 'Inspector' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-asset': {
    kind: 'model_form',
    model: 'fix.site.asset',
    title: 'Infrastructure Asset',
    back: 'M47-infra',
    status: { field: 'state', labels: {
      operational: 'Operational', maintenance: 'Under Maintenance', retired: 'Retired' } },
    sections: [
      { title: 'Plant Asset', note: 'Operational → under maintenance → operational; retirement is final and, above Tier 0, needs a DOFA approval of the asset value. The register drives the Branch Asset Register count and value.',
        fields: [
          { name: 'name', required: true, label: 'Asset Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'asset_type', required: true, label: 'Asset Type' },
          { name: 'tag', label: 'Asset Tag' },
          { name: 'serial_no', label: 'Serial No' },
          { name: 'installed_on', label: 'Installed On' },
          { name: 'warranty_end', label: 'Warranty End' },
          { name: 'value', label: 'Asset Value' },
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'approval_state', label: 'Retirement Approval (M63)', readonly: true },
          { name: 'retired_on', label: 'Retired On', readonly: true },
          { name: 'retire_reason', label: 'Retirement Reason', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-utility': {
    kind: 'model_form',
    model: 'fix.site.utility',
    title: 'Utility Account',
    back: 'M47-utilities',
    sections: [
      { title: 'Utility', note: 'One bill per site, period (YYYY-MM) and utility type; a second bill for the same month is refused. The anomaly flag is a recorded judgement, not a statistical detector.',
        fields: [
          { name: 'name', required: true, label: 'Account Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'utility_type', required: true, label: 'Utility Type' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'usage', label: 'Usage' },
          { name: 'unit', label: 'Unit' },
          { name: 'flagged', label: 'Anomaly Flagged' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-pm': {
    kind: 'model_form',
    model: 'fix.site.pm',
    title: 'Building Services PM',
    back: 'M47-pm',
    status: { field: 'state', labels: { open: 'Open', done: 'Done' } },
    sections: [
      { title: 'PM Job', note: 'Only an open job can be marked done; Mark Done records the done date.',
        fields: [
          { name: 'name', required: true, label: 'PM Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'service_type', required: true, label: 'Service Type' },
          { name: 'provider_id', label: 'Service Provider' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'done_on', label: 'Done On', readonly: true },
          { name: 'cost', label: 'Cost' },
          { name: 'state', label: 'State (Mark Done)', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-incident': {
    kind: 'model_form',
    model: 'fix.site.incident',
    title: 'Security Incident',
    back: 'M47-security',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Incident', note: 'Only an open incident can be closed, with a resolution, by someone other than its reporter. The resolution is frozen once closed.',
        fields: [
          { name: 'name', required: true, label: 'Incident Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'incident_type', required: true, label: 'Incident Type' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'resolution', type: 'text', label: 'Resolution (root cause and action)' },
          { name: 'state', label: 'State (Close Incident)', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true },
          { name: 'closed_at', label: 'Closed At', readonly: true }
        ] }
    ]
  },

  'M47-form-project': {
    kind: 'model_form',
    model: 'fix.site.project',
    title: 'Site Open / Close Project',
    back: 'M47-opening',
    status: { field: 'state', labels: {
      planned: 'Planned', in_progress: 'In Progress', done: 'Done' } },
    sections: [
      { title: 'Project', note: 'Planned → in progress → done; the done date is set at completion. Start and completion need a DOFA approval of the budget; raising the budget after approval withdraws it.',
        fields: [
          { name: 'name', required: true, label: 'Project Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'done_on', label: 'Done On', readonly: true },
          { name: 'budget', label: 'Budget' },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Budget Approval (M63)', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M47-rpt-branchassets': { kind: 'table_report', module: 'M47', report: 'branch_assets', title: "Branch Asset Register", period: false },
};

export const REPORT_ROUTES = {
  'M47:Branch Asset Register': 'M47-rpt-branchassets',
  'M47:Cost per Site / per Job': 'M47-rpt-cost',
  'M47:Lease Expiry Register': 'M47-rpt-lease',
  'M47:Licence Compliance': 'M47-rpt-licence',
  'M47:Utilities Variance': 'M47-rpt-utilities',
  'M47:Facility Work Order Performance': 'M47-rpt-wo'
};

export const FORM_MODELS = {
  'M47:Site': 'fix.site',
  'M47:Lease': 'fix.site.lease',
  'M47:Licence': 'fix.site.licence',
  'M47:Facility Work Order': 'fix.facility.work.order',
  'M47:Safety Inspection': 'fix.site.safety'
};

export const FORM_CHIPS = {
  'M47:Site': 'M47-form-site',
  'M47:Lease': 'M47-form-lease',
  'M47:Licence': 'M47-form-licence',
  'M47:Facility Work Order': 'M47-form-wo',
  'M47:Safety Inspection': 'M47-form-safety',
  'M47:__by_model__': {
    'fix.site': 'M47-form-site',
    'fix.site.lease': 'M47-form-lease',
    'fix.site.licence': 'M47-form-licence',
    'fix.facility.work.order': 'M47-form-wo',
    'fix.site.safety': 'M47-form-safety',
    'fix.site.condition': 'M47-form-condition',
    'fix.site.asset': 'M47-form-asset',
    'fix.site.utility': 'M47-form-utility',
    'fix.site.pm': 'M47-form-pm',
    'fix.site.incident': 'M47-form-incident',
    'fix.site.project': 'M47-form-project'
  },
  'M47:__by_screen__': {
    'M47-sites': 'M47-form-site',
    'M47-occupancy': 'M47-form-condition',
    'M47-leases': 'M47-form-lease',
    'M47-licences': 'M47-form-licence',
    'M47-utilities': 'M47-form-utility',
    'M47-infra': 'M47-form-asset',
    'M47-pm': 'M47-form-pm',
    'M47-wo': 'M47-form-wo',
    'M47-safety': 'M47-form-safety',
    'M47-security': 'M47-form-incident',
    'M47-opening': 'M47-form-project'
  }
};

export const CREATE = {
  M47: { screen: 'M47-form-site', model: 'fix.site', label: 'Site' }
};
