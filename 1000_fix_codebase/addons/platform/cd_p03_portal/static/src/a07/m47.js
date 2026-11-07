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
    { l: 'Safety Inspections Due', m: 'safety_due' },
    { l: 'Operating-Risk Exceptions', m: 'risk_exceptions_open' },
    { l: 'Utility Bills Held', m: 'utilities_held' }
  ],
  groups: [
    { en: 'Sites', screens: [
      { id: 'M47-sites', en: 'Site Register', bn: 'সাইট রেজিস্টার', t: 'g' },
      { id: 'M47-occupancy', en: 'Occupancy & Condition', bn: 'দখল ও অবস্থা', t: 'g' }
    ]},
    { en: 'Leases', screens: [
      { id: 'M47-leases', en: 'Lease Administration', bn: 'লিজ প্রশাসন', t: 'g' },
      { id: 'M47-lease-schedule', en: 'Rent Schedule', bn: 'ভাড়ার সূচি', t: 'g' },
      { id: 'M47-lease-extracts', en: 'IFRS 16 Lease Extracts', bn: 'আইএফআরএস ১৬ নির্যাস', t: 'g' },
      { id: 'M47-dates', en: 'Critical-Date Control', bn: 'গুরুত্বপূর্ণ তারিখ', t: 'r' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M47-licences', en: 'Statutory Licences', bn: 'আইনি লাইসেন্স', t: 'g' },
      { id: 'M47-risk', en: 'Operating-Risk Exceptions', bn: 'পরিচালন ঝুঁকি ব্যতিক্রম', t: 'g' },
      { id: 'M47-utilities', en: 'Utilities & Anomalies', bn: 'ইউটিলিটি', t: 'g' }
    ]},
    { en: 'Infrastructure', screens: [
      { id: 'M47-infra', en: 'Branch Asset Register', bn: 'শাখা সম্পদ', t: 'r' },
      { id: 'M47-pm', en: 'Building Services PM', bn: 'ভবন সেবা', t: 'g' },
      { id: 'M47-wo', en: 'Facility Work Orders', bn: 'সুবিধা কাজ', t: 'g' },
      { id: 'M47-demand', en: 'Maintenance Demand Queue', bn: 'রক্ষণাবেক্ষণ চাহিদা সারি', t: 'g' }
    ]},
    { en: 'Alerts', screens: [
      { id: 'M47-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
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
    ['9', 'Open / Close Projects', 6, { model: 'fix.site.project', cols: ['name', 'site_id', 'project_type', 'planned_on', 'budget', 'state'], screens: ['M47-opening'] }],
    ['10', 'Maintenance Demand Queue', 6, { model: 'fix.maintenance.demand', cols: ['name', 'origin', 'source_ref', 'site_id', 'work_order_id', 'state'], screens: ['M47-demand'] }]
  ] }
};

export const SCREENS = {
  'M47-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M47']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M47-sites': { kind: 'model_list', model: 'fix.site', stateField: 'state',
    cols: ['name', 'site_type', 'branch_id', 'accountable_manager_id', 'floor_area_sqm', 'monthly_rent', 'opened_on', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Status-Change Approval (readiness / resume: Operations Director; close / reopen: CFO then CEO)', ask: 'Business justification for the signatories', kwarg: 'justification' },
      { m: 'action_open', l: 'Open Site (Readiness Gate)' },
      { m: 'action_resume', l: 'Resume Suspended Site' },
      { m: 'action_close', l: 'Close Site' },
      { m: 'action_reopen', l: 'Reopen Site (back to Planned)' }
    ] },
  'M47-occupancy': { kind: 'model_list', model: 'fix.site.condition',
    cols: ['name', 'site_id', 'inspected_on', 'occupancy_pct', 'condition_grade', 'inspector_id', 'notes'] },
  'M47-leases': { kind: 'model_list', model: 'fix.site.lease', stateField: 'state',
    cols: ['name', 'site_id', 'lessor_id', 'start_date', 'end_date', 'renewal_notice_date', 'current_rent', 'renewal_decision', 'approval_state', 'state'],
    actions: [
      { m: 'action_decide_renew', l: 'CFO Decision: Renew', ask: 'Basis of the renewal decision', kwarg: 'notes' },
      { m: 'action_decide_renegotiate', l: 'CFO Decision: Renegotiate', ask: 'Basis of the renegotiation decision', kwarg: 'notes' },
      { m: 'action_decide_exit', l: 'CFO Decision: Exit', ask: 'Basis of the exit decision', kwarg: 'notes' },
      { m: 'action_open_modification', l: 'Open Renewal / Modification' },
      { m: 'action_request_approval', l: 'Request Modification Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_apply_modification', l: 'Apply Approved Modification' },
      { m: 'action_discard_modification', l: 'Discard Modification' },
      { m: 'action_expire', l: 'Mark Expired' },
      { m: 'action_terminate', l: 'Terminate Lease', ask: 'Why is the lease terminated?', kwarg: 'reason' }
    ] },
  'M47-lease-schedule': { kind: 'model_list', model: 'fix.site.lease.schedule',
    cols: ['lease_id', 'site_id', 'period', 'due_date', 'escalation_year', 'rent_due', 'paid_amount', 'paid_on', 'invoice_ref'] },
  'M47-lease-extracts': { kind: 'model_list', model: 'fix.site.lease.extract',
    cols: ['lease_id', 'site_id', 'version', 'reason', 'published_at', 'consumed_by_m19_at'] },
  'M47-dates': { kind: 'table_report', module: 'M47', report: 'critical_dates', title: 'Critical-Date Control', period: false },
  'M47-licences': { kind: 'model_list', model: 'fix.site.licence', stateField: 'state',
    cols: ['name', 'site_id', 'licence_type', 'number', 'issued_on', 'valid_to', 'is_valid', 'state'] },
  'M47-risk': { kind: 'model_list', model: 'fix.site.risk.exception', stateField: 'state',
    cols: ['name', 'site_id', 'licence_id', 'licence_type', 'severity', 'raised_at', 'decided_by_id', 'review_due_on', 'state'],
    actions: [
      { m: 'action_decide_continue', l: 'Decide: Continue Until (dated)', ask: 'Review date after today (YYYY-MM-DD); record the decision basis on the form first', kwarg: 'review_due_on' },
      { m: 'action_decide_suspend', l: 'Decide: Suspend Site', ask: 'Basis of the suspension decision', kwarg: 'notes' }
    ] },
  'M47-utilities': { kind: 'model_list', model: 'fix.site.utility',
    cols: ['name', 'site_id', 'period', 'utility_type', 'amount', 'usage', 'unit', 'flagged', 'review_state'],
    actions: [
      { m: 'action_flag', l: 'Hold for Review' },
      { m: 'action_release', l: 'Review: Release for Payment', ask: 'Review basis (you must not be the recorder)', kwarg: 'notes' },
      { m: 'action_confirm_anomaly', l: 'Review: Confirm Anomaly', ask: 'Review basis (you must not be the recorder)', kwarg: 'notes' }
    ] },
  'M47-infra': { kind: 'model_list', model: 'fix.site.asset', stateField: 'state',
    cols: ['name', 'site_id', 'asset_type', 'tag', 'installed_on', 'warranty_end', 'value', 'state'],
    actions: [
      { m: 'action_maintenance', l: 'Take to Maintenance' },
      { m: 'action_restore', l: 'Restore to Service' },
      { m: 'action_request_approval', l: 'Request Retirement Approval (DOFA)', ask: 'Why should this asset be retired?', kwarg: 'justification' },
      { m: 'action_retire', l: 'Retire Asset', ask: 'Retirement reason', kwarg: 'reason' }
    ] },
  'M47-pm': { kind: 'model_list', model: 'fix.site.pm', stateField: 'state',
    cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'interval_months', 'done_on', 'cost', 'work_order_id', 'state'],
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
      { m: 'action_cancel', l: 'Cancel', ask: 'Cancellation reason (optional)', kwarg: 'reason' },
      { m: 'action_approve_permit', l: 'Approve Permit to Work', ask: 'Permit valid to (YYYY-MM-DD; blank = today only)', kwarg: 'valid_to' }
    ] },
  'M47-safety': { kind: 'model_list', model: 'fix.site.safety', stateField: 'state',
    cols: ['name', 'site_id', 'equipment_type', 'ref', 'last_check', 'next_check', 'inspection_interval_months', 'last_checked_by_id', 'state'],
    actions: [{ m: 'action_check', l: 'Record Check', ask: 'Next check date after today (YYYY-MM-DD); blank uses the item\'s inspection interval', kwarg: 'next_check' }] },
  'M47-security': { kind: 'model_list', model: 'fix.site.incident', stateField: 'state',
    cols: ['name', 'site_id', 'incident_type', 'occurred_on', 'severity', 'injuries_flag', 'hse_notice_due_on', 'hse_case_ref', 'state'],
    actions: [{ m: 'action_close', l: 'Close Incident', ask: 'Resolution: root cause and action taken', kwarg: 'resolution' }] },
  'M47-opening': { kind: 'model_list', model: 'fix.site.project', stateField: 'state',
    cols: ['name', 'site_id', 'project_type', 'planned_on', 'done_on', 'budget', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Budget Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_start', l: 'Start Project' },
      { m: 'action_revise_budget', l: 'Revise Budget', ask: 'Reason for revising to the Proposed Budget', kwarg: 'reason' },
      { m: 'action_done', l: 'Complete Project' }
    ] },
  'M47-demand': { kind: 'model_list', model: 'fix.maintenance.demand', stateField: 'state',
    cols: ['name', 'origin', 'source_ref', 'target', 'site_id', 'scheduled_date', 'blocker', 'work_order_id', 'service_order_id', 'state'],
    actions: [
      { m: 'action_route', l: 'Route' },
      { m: 'action_dismiss', l: 'Dismiss', ask: 'Reason for dismissing this demand', kwarg: 'reason' }
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
    status: { field: 'state', labels: { planned: 'Planned / Fitting Out', active: 'Operational', suspended: 'Suspended', closed: 'Closed' } },
    tabs: [
      { id: 'site', label: '1. Site', bn: '১. সাইট', icon: '🏬', badge: '12' },
      { id: 'readiness', label: '2. Readiness Gate', bn: '২. প্রস্তুতি', icon: '✅', badge: '8' },
      { id: 'closure', label: '3. Closure & Sign-off', bn: '৩. বন্ধ ও অনুমোদন', icon: '🔐', badge: '11' }
    ],
    sections: [
      { tab: 'site', title: 'Site', note: 'The site register is the anchor for leases, licences, utilities, occupancy, safety equipment and work orders. A new site is born Planned and operates only after the readiness gate; closing it keeps every historical record readable. Site master data is edited by a Facility Manager.',
        fields: [
          { name: 'name', required: true, label: 'Site Name' },
          { name: 'site_type', required: true, label: 'Site Type' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'floor_area_sqm', label: 'Floor Area (sqm)' },
          { name: 'lease_start', label: 'Lease Start' },
          { name: 'lease_end', label: 'Lease End' },
          { name: 'monthly_rent', label: 'Monthly Rent (used only where no lease is recorded)' },
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'opened_on', label: 'Operational Since', readonly: true },
          { name: 'suspended_reason', label: 'Suspension Reason', readonly: true }
        ] },
      { tab: 'site', title: 'Address', note: 'Plant assets (HVAC, lift, generator, fire pump, UPS, CCTV) are recorded on the Branch Asset Register screen against this site.',
        fields: [
          { name: 'address', type: 'text', label: 'Address' }
        ] },
      { tab: 'readiness', title: 'Readiness Gate (BRU-FAC-04 / -06)', note: 'Open Site needs: an accountable manager; an active lease unless the site is owned; a current licence of each type in cd_facility.readiness_licence_types (default trade and fire); safety equipment on the register and none overdue; and the five attested items below. A Branch Operations Lead requests it; the Operations Director (not the requester or the creator) signs it off from the M63 inbox. Changing an item after the sign-off withdraws it.',
        fields: [
          { name: 'accountable_manager_id', label: 'Accountable Manager' },
          { name: 'occupancy_basis', label: 'Occupancy Basis' },
          { name: 'ready_power', label: 'Power Connected' },
          { name: 'ready_connectivity', label: 'Connectivity Live' },
          { name: 'ready_security', label: 'Security Arrangements in Place' },
          { name: 'ready_equipment', label: 'Equipment Complement Installed (M45)' },
          { name: 'ready_signage', label: 'Signage Installed / Permitted' },
          { name: 'readiness_notes', type: 'text', label: 'Readiness Evidence' }
        ] },
      { tab: 'closure', title: 'Recovery Checklist (BRU-FAC-15)', note: 'A site that still holds an active lease, an open work order or a valid licence closes only with this checklist complete. Editing it after a sign-off withdraws the sign-off.',
        fields: [
          { name: 'closure_assets_recovered', label: 'Assets Recovered (M45 / M15 / M46)' },
          { name: 'closure_licences_surrendered', label: 'Licences Surrendered' },
          { name: 'closure_deposit_settled', label: 'Deposit Recovered / Written Off' },
          { name: 'closure_notes', type: 'text', label: 'Recovery Notes' }
        ] },
      { tab: 'closure', title: 'Status-Change Sign-off', note: 'Opening (readiness gate) and resuming a suspended site need the Operations Director. Closing or reopening needs two routed sign-offs by two different people, neither the requester nor the creator: the CFO (DOFA Tier 4), then the CEO (DOFA Tier 5); request approval once for each. A reopened site returns to Planned. A site is suspended only by the continue-or-suspend decision on an operating-risk exception.',
        fields: [
          { name: 'approval_state', label: 'Approval Request (M63)', readonly: true },
          { name: 'status_opsdir_approved_by_id', label: 'Operations Director Sign-off', readonly: true },
          { name: 'status_opsdir_approved_at', label: 'Operations Director Signed At', readonly: true },
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
      { tab: 'lease', title: 'Lease', note: 'The end date cannot precede the start (database CHECK). Once recorded, the dates, rent and escalation change only through a renewal or modification. Recording a lease builds its monthly rent schedule (escalated on each anniversary) and publishes the lease data extract for M19 / M49; a lease recorded after its end date is born Expired, and the daily job expires an active lease once its end date passes.',
        fields: [
          { name: 'name', required: true, label: 'Lease Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'lessor_id', required: true, label: 'Lessor' },
          { name: 'start_date', required: true, label: 'Start Date' },
          { name: 'end_date', required: true, label: 'End Date' },
          { name: 'monthly_rent', label: 'Monthly Rent' },
          { name: 'escalation_pct', label: 'Escalation %' },
          { name: 'deposit', label: 'Deposit' },
          { name: 'current_rent', label: 'Current Monthly Rent (schedule)', readonly: true },
          { name: 'notice_period_days', label: 'Renewal Notice (days)' },
          { name: 'renewal_notice_date', label: 'Renewal Notice Deadline', readonly: true },
          { name: 'renewal_decision', label: 'Renewal Decision (CFO)', readonly: true },
          { name: 'renewal_decision_by_id', label: 'Decided By', readonly: true },
          { name: 'renewal_decision_on', label: 'Decided On', readonly: true },
          { name: 'renewal_decision_notes', label: 'Decision Basis', readonly: true },
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
      { title: 'Statutory Licence', note: 'Valid today is computed on every read: the state must be Valid, an end date must be recorded and it must not have passed (a licence with no end date is not valid). A lapsed licence cannot be made valid again; record the renewal as a new licence. A trade licence renewal is refused while the site\'s fire licence is expired (BRU-FAC-03). The daily job alerts at 90/60/30/15/7 days, marks a lapsed licence Expired and raises an operating-risk exception at an operational site. Licences are edited by a Facility Manager.',
        fields: [
          { name: 'name', required: true, label: 'Licence Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'licence_type', required: true, label: 'Licence Type' },
          { name: 'number', label: 'Licence Number' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'is_valid', label: 'Valid Today', readonly: true },
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
      { id: 'cost', label: '2. Scope, Cost & Approval', bn: '২. ব্যয় ও অনুমোদন', icon: '💳', badge: '8' },
      { id: 'permit', label: '3. Permit to Work', bn: '৩. কাজের অনুমতি', icon: '⚠️', badge: '6' },
      { id: 'evidence', label: '4. Completion & Verification', bn: '৪. সমাপ্তি ও যাচাই', icon: '🔐', badge: '6' },
      { id: 'origin', label: '5. Asset & Origin', bn: '৫. সম্পদ ও উৎস', icon: '🔗', badge: '7' }
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
          { name: 'assigned_type', label: 'Assigned To (internal / vendor)' },
          { name: 'vendor_id', label: 'Vendor (required for a vendor job)' },
          { name: 'invoice_ref', label: 'Vendor Invoice Ref (required to verify a costed vendor job)' },
          { name: 'estimated_cost', label: 'Estimated Cost' },
          { name: 'actual_cost', label: 'Actual Cost' },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Spend Approval (M63)', readonly: true }
        ] },
      { tab: 'permit', title: 'Permit to Work (high-risk jobs)', note: 'A high-risk job (hot work, electrical isolation, height, confined space) starts only under a permit approved by a Facility Manager who neither raised the job nor is assigned to it, valid on the start date. Changing the hazard or precautions withdraws the permit.',
        fields: [
          { name: 'high_risk', label: 'High-Risk Job' },
          { name: 'hazard_type', label: 'Hazard' },
          { name: 'permit_precautions', type: 'text', label: 'Precautions' },
          { name: 'permit_approved_by_id', label: 'Permit Approved By', readonly: true },
          { name: 'permit_approved_at', label: 'Permit Approved At', readonly: true },
          { name: 'permit_valid_to', label: 'Permit Valid To', readonly: true }
        ] },
      { tab: 'evidence', title: 'Completion & Verification (BRU-FAC-07)', note: 'Completion records the evidence and who completed it; verification by a Facility Manager who neither raised nor completed it closes the work order and sends the actual cost (and the vendor invoice reference) to M52.',
        fields: [
          { name: 'completion_notes', type: 'text', label: 'Completion Evidence' },
          { name: 'completed_by_id', label: 'Completed By', readonly: true },
          { name: 'completed_at', label: 'Completed At', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'verified_at', label: 'Verified At', readonly: true },
          { name: 'verification_notes', type: 'text', label: 'Verification Notes', readonly: true }
        ] },
      { tab: 'origin', title: 'Asset & Origin (work-order spine)', note: 'A work order raised from an M45 calibration or PM, an M46 vehicle service or an M48 intervention carries its source here, set only by the routing. Verifying it completes the source job through the source module\'s own step.',
        fields: [
          { name: 'spine_origin', label: 'Raised From', readonly: true },
          { name: 'spine_asset_kind', label: 'Asset Kind', readonly: true },
          { name: 'spine_source_ref', label: 'Source Item', readonly: true },
          { name: 'vehicle_id', label: 'Vehicle (M46)', readonly: true },
          { name: 'iot_device_id', label: 'IoT Device (M48)', readonly: true },
          { name: 'spine_calibration_due', label: 'Calibration Due (M45)', readonly: true },
          { name: 'spine_demand_id', label: 'Maintenance Demand', readonly: true }
        ] }
    ]
  },

  'M47-form-demand': {
    kind: 'model_form',
    model: 'fix.maintenance.demand',
    title: 'Maintenance Demand',
    back: 'M47-demand',
    status: { field: 'state', labels: {
      pending: 'Pending (needs a fact)', routed: 'Routed', done: 'Done', dismissed: 'Dismissed' } },
    sections: [
      { title: 'Demand', note: 'One row per source item (M45 calibration or PM, M46 service, M48 intervention, M17 device plan). It routes itself to a facility work order or a draft M01 service order; when a fact is missing it waits here and says what it needs. Fill the missing fact and Route; Dismiss needs a reason.',
        fields: [
          { name: 'name', label: 'Demand', readonly: true },
          { name: 'origin', label: 'Raised From', readonly: true },
          { name: 'source_ref', label: 'Source Item', readonly: true },
          { name: 'blocker', type: 'text', label: 'What It Needs', readonly: true },
          { name: 'description', type: 'text', label: 'Description' },
          { name: 'site_id', label: 'Site (M47)' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'device_id', label: 'Customer Device (M17)' },
          { name: 'technician_id', label: 'Technician / Engineer' },
          { name: 'scheduled_date', label: 'Scheduled Date' },
          { name: 'work_order_id', label: 'Work Order', readonly: true },
          { name: 'service_order_id', label: 'Service Order (M01)', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
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
      { title: 'Safety Equipment', note: 'The status is derived from the next check date: overdue once it has passed, due within 30 days. Record Check stamps today as the last check and who did it, and sets the next check date given, or rolls it by the item\'s inspection interval; the next check cannot be pushed later by editing. The daily job reports an overdue item to M59 as unfit.',
        fields: [
          { name: 'name', required: true, label: 'Check Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_type', required: true, label: 'Equipment Type' },
          { name: 'ref', label: 'Tag / Reference' },
          { name: 'last_check', label: 'Last Check', readonly: true },
          { name: 'last_checked_by_id', label: 'Last Checked By', readonly: true },
          { name: 'next_check', required: true, label: 'Next Check' },
          { name: 'inspection_interval_months', label: 'Inspection Interval (months)' },
          { name: 'state', label: 'Status (derived)', readonly: true },
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
      { title: 'Utility', note: 'One bill per site, period (YYYY-MM) and utility type; a second bill for the same month is refused. On record the bill is compared with its own average over up to the last 3 periods; at the configured multiple (default 2.0, pending business confirmation) it is held from payment. Only a Branch Operations Lead who did not record the bill releases it or confirms the anomaly; the figures of a reviewed bill are frozen.',
        fields: [
          { name: 'name', required: true, label: 'Account Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'utility_type', required: true, label: 'Utility Type' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'usage', label: 'Usage' },
          { name: 'unit', label: 'Unit' },
          { name: 'flagged', label: 'Anomaly Flagged', readonly: true },
          { name: 'review_state', label: 'Payment Hold', readonly: true },
          { name: 'anomaly_basis', label: 'Anomaly Basis', readonly: true },
          { name: 'reviewed_by_id', label: 'Reviewed By', readonly: true },
          { name: 'review_notes', label: 'Review Notes', readonly: true },
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
      { title: 'PM Job', note: 'Only an open job can be marked done; Mark Done records the done date and, when a repeat interval is set, schedules the next job. The daily job raises a facility work order for an open job once it is due.',
        fields: [
          { name: 'name', required: true, label: 'PM Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'service_type', required: true, label: 'Service Type' },
          { name: 'provider_id', label: 'Service Provider' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'done_on', label: 'Done On', readonly: true },
          { name: 'interval_months', label: 'Repeat Every (months)' },
          { name: 'next_pm_id', label: 'Next PM', readonly: true },
          { name: 'work_order_id', label: 'Work Order', readonly: true },
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
      { title: 'Incident', note: 'Only an open incident can be closed, with a resolution, by someone other than its reporter: a Facility Manager, or for an injury HSE or a Branch Operations Lead. Recording an incident notifies M59 / M60; an injury carries the BLA 2006 s.80 Inspector-notice date and the bridge links its HSE case. The resolution is frozen once closed.',
        fields: [
          { name: 'name', required: true, label: 'Incident Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'incident_type', required: true, label: 'Incident Type' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'injuries_flag', label: 'Injury Involved' },
          { name: 'hse_notice_due_on', label: 'Inspector Notice Due (s.80)', readonly: true },
          { name: 'hse_case_ref', label: 'HSE Case (M59)', readonly: true },
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
      { title: 'Project', note: 'Planned → in progress → done; the done date is set at completion. Start and completion need a DOFA approval of the budget. Once approved or started, the budget changes only by Revise Budget (Proposed Budget plus a reason, Facility Manager); a raise withdraws the approval. A site-closure project completes only once its site has closed (CFO and CEO sign-off).',
        fields: [
          { name: 'name', required: true, label: 'Project Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'planned_on', required: true, label: 'Planned On' },
          { name: 'done_on', label: 'Done On', readonly: true },
          { name: 'budget', label: 'Budget' },
          { name: 'budget_proposed', label: 'Proposed Budget (for Revise Budget)' },
          { name: 'budget_change_reason', label: 'Budget Change Reason' },
          { name: 'budget_revision_note', label: 'Last Budget Revision', readonly: true },
          { name: 'dofa_tier_required', label: 'DOFA Tier Required', readonly: true },
          { name: 'approval_state', label: 'Budget Approval (M63)', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M47-form-risk': {
    kind: 'model_form',
    model: 'fix.site.risk.exception',
    title: 'Operating-Risk Exception',
    back: 'M47-risk',
    status: { field: 'state', labels: { open: 'Decision Required', continue: 'Continue (dated)', suspend: 'Site Suspended', resolved: 'Resolved' } },
    sections: [
      { title: 'Exception (BRU-FAC-02)', note: 'Raised by the daily job when a licence lapses at an operational site. The Operations Director or the CEO (DOFA Tier 5) records a named, dated continue-or-suspend decision; the person responsible for the renewal (the licence recorder, the site\'s accountable manager) cannot. A continue decision lapses on its review date and must be taken again; undecided exceptions are escalated daily. Recording the renewed licence resolves it.',
        fields: [
          { name: 'name', label: 'Exception', readonly: true },
          { name: 'site_id', label: 'Site', readonly: true },
          { name: 'licence_id', label: 'Lapsed Licence', readonly: true },
          { name: 'licence_type', label: 'Licence Type', readonly: true },
          { name: 'severity', label: 'Severity', readonly: true },
          { name: 'raised_at', label: 'Raised At', readonly: true },
          { name: 'decision_notes', type: 'text', label: 'Decision Basis (interim arrangements)' },
          { name: 'state', label: 'State (decision actions)', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_at', label: 'Decided At', readonly: true },
          { name: 'review_due_on', label: 'Review Date', readonly: true },
          { name: 'resolution', label: 'Resolution', readonly: true }
        ] }
    ]
  },

  'M47-form-lease-schedule': {
    kind: 'model_form',
    model: 'fix.site.lease.schedule',
    title: 'Rent Schedule Row',
    back: 'M47-lease-schedule',
    sections: [
      { title: 'Scheduled Rent (FR-FAC-012)', note: 'Built by the lease from its terms: one row per month, the rent escalated on each anniversary. Paid amounts and invoice references are matched by M52; nobody edits the rows directly.',
        fields: [
          { name: 'lease_id', label: 'Lease', readonly: true },
          { name: 'period', label: 'Period', readonly: true },
          { name: 'due_date', label: 'Due Date', readonly: true },
          { name: 'escalation_year', label: 'Lease Year', readonly: true },
          { name: 'rent_due', label: 'Rent Due', readonly: true },
          { name: 'paid_amount', label: 'Paid (M52)', readonly: true },
          { name: 'paid_on', label: 'Paid On', readonly: true },
          { name: 'invoice_ref', label: 'Invoice Ref (M52)', readonly: true },
          { name: 'variance', label: 'Variance', readonly: true }
        ] }
    ]
  },

  'M47-form-lease-extract': {
    kind: 'model_form',
    model: 'fix.site.lease.extract',
    title: 'Lease Data Extract',
    back: 'M47-lease-extracts',
    sections: [
      { title: 'IFRS 16 Data Extract (BRU-FAC-13 / -14)', note: 'A versioned, insert-only copy of the accounting-relevant lease data, published to M19 / M49 when a lease is recorded and on every modification. M47 never computes the right-of-use asset or the lease liability.',
        fields: [
          { name: 'lease_id', label: 'Lease', readonly: true },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'reason', label: 'Reason', readonly: true },
          { name: 'published_at', label: 'Published At', readonly: true },
          { name: 'consumed_by_m19_at', label: 'Consumed by M19 At', readonly: true },
          { name: 'payload', type: 'text', label: 'Extract', readonly: true }
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
    'fix.site.project': 'M47-form-project',
    'fix.maintenance.demand': 'M47-form-demand',
    'fix.site.risk.exception': 'M47-form-risk',
    'fix.site.lease.schedule': 'M47-form-lease-schedule',
    'fix.site.lease.extract': 'M47-form-lease-extract'
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
    'M47-opening': 'M47-form-project',
    'M47-demand': 'M47-form-demand',
    'M47-risk': 'M47-form-risk',
    'M47-lease-schedule': 'M47-form-lease-schedule',
    'M47-lease-extracts': 'M47-form-lease-extract'
  }
};

export const CREATE = {
  M47: { screen: 'M47-form-site', model: 'fix.site', label: 'Site' }
};
