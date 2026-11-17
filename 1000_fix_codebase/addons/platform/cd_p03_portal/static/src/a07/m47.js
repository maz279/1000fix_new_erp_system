/** @odoo-module **/
/* A07 · Assets & Facilities — M47 Facility & Branch Infrastructure (v2 rebuild).
 * Registry-faithful: 5 groups / 12 screens / 5 reports / 5 forms / freg 71.
 * fix.site and fix.facility.work.order existed; leases, licences, utilities,
 * occupancy, building PM, safety equipment, incidents and site projects are new.
 * Capture audit (2026-11-17): every page offers a chip for each record it lists,
 * every working list sits on a page, and the site-type profile, lease critical
 * events, licence renewals, utility accounts, outages and generator / UPS tests
 * are captured (spec §5, §10.1). */

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
      { id: 'M47-occupancy', en: 'Occupancy & Condition', bn: 'দখল ও অবস্থা', t: 'g' },
      { id: 'M47-site-profiles', en: 'Site Type Profiles', bn: 'সাইট ধরন প্রোফাইল', t: 'g' }
    ]},
    { en: 'Leases', screens: [
      { id: 'M47-leases', en: 'Lease Administration', bn: 'লিজ প্রশাসন', t: 'g' },
      { id: 'M47-lease-events', en: 'Lease Critical Events', bn: 'লিজের গুরুত্বপূর্ণ ঘটনা', t: 'g' },
      { id: 'M47-lease-schedule', en: 'Rent Schedule', bn: 'ভাড়ার সূচি', t: 'g' },
      { id: 'M47-lease-extracts', en: 'IFRS 16 Lease Extracts', bn: 'আইএফআরএস ১৬ নির্যাস', t: 'g' },
      { id: 'M47-dates', en: 'Critical-Date Control', bn: 'গুরুত্বপূর্ণ তারিখ', t: 'r' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M47-licences', en: 'Statutory Licences', bn: 'আইনি লাইসেন্স', t: 'g' },
      { id: 'M47-licence-renewals', en: 'Licence Renewals', bn: 'লাইসেন্স নবায়ন', t: 'g' },
      { id: 'M47-risk', en: 'Operating-Risk Exceptions', bn: 'পরিচালন ঝুঁকি ব্যতিক্রম', t: 'g' },
      { id: 'M47-utilities', en: 'Utilities & Anomalies', bn: 'ইউটিলিটি', t: 'g' },
      { id: 'M47-utility-accounts', en: 'Utility Accounts', bn: 'ইউটিলিটি হিসাব', t: 'g' }
    ]},
    { en: 'Infrastructure', screens: [
      { id: 'M47-infra', en: 'Branch Asset Register', bn: 'শাখা সম্পদ', t: 'g' },
      { id: 'M47-outages', en: 'Infrastructure Outages', bn: 'অবকাঠামো বিভ্রাট', t: 'g' },
      { id: 'M47-pm', en: 'Building Services PM', bn: 'ভবন সেবা', t: 'g' },
      { id: 'M47-power-tests', en: 'Generator / UPS Tests', bn: 'জেনারেটর / ইউপিএস পরীক্ষা', t: 'g' },
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
    ]},
    { en: 'Finance & HSE Hand-offs', screens: [
      { id: 'M47-costs', en: 'Cost Entries for Accounts Payable', bn: 'হিসাবের জন্য খরচের এন্ট্রি', t: 'g' },
      { id: 'M47-asset-requests', en: 'Asset Finance Requests', bn: 'সম্পদ অর্থায়ন অনুরোধ', t: 'g' },
      { id: 'M47-lease-items', en: 'Lease Remeasurement Items', bn: 'লিজ পুনঃপরিমাপ', t: 'g' },
      { id: 'M47-handoff-exceptions', en: 'Hand-off Problems', bn: 'হস্তান্তর সমস্যা', t: 'g' }
    ]}
  ],
  reports: ['Cost per Site / per Job', 'Lease Expiry Register', 'Licence Compliance', 'Utilities Variance', 'Facility Work Order Performance', 'Branch Asset Register', 'Infrastructure Availability'],
  forms: ['Site', 'Lease', 'Licence', 'Facility Work Order', 'Safety Inspection',
    'Site Condition', 'Site Type Profile', 'Lease Critical Event', 'Licence Renewal', 'Utility Bill',
    'Utility Account', 'Infrastructure Asset', 'Infrastructure Outage', 'PM Job', 'Power Test',
    'Security Incident', 'Site Project'],
  cross: ['M04 branch operations', 'M30 branch provisioning', 'M49 ROU assets', 'M59 safety committee'],
  /* Each page: its own record first ("+ New"), then a chip for every other record it lists.
   * Page 10 is the work-order spine's queue: its demands are raised by their source
   * modules (M45, M46, M48, M17) and a person completes and routes them from the row. */
  freg: { src: 71, sub: [
    ['1', 'Site Register', 7, { model: 'fix.site', cols: ['name', 'site_type', 'branch_id', 'floor_area_sqm', 'state'], screens: ['M47-sites', 'M47-occupancy', 'M47-site-profiles'], reports: ['Cost per Site / per Job', 'Branch Asset Register'], forms: ['Site', 'Site Condition', 'Site Type Profile'] }],
    ['2', 'Lease Administration', 11, { model: 'fix.site.lease', cols: ['name', 'site_id', 'lessor_id', 'end_date', 'monthly_rent', 'state'], screens: ['M47-leases', 'M47-lease-events', 'M47-dates', 'M47-lease-schedule', 'M47-lease-extracts', 'M47-lease-items', 'M47-costs'], reports: ['Lease Expiry Register'], forms: ['Lease', 'Lease Critical Event'] }],
    ['3', 'Statutory Compliance', 9, { model: 'fix.site.licence', cols: ['name', 'site_id', 'licence_type', 'valid_to', 'state'], screens: ['M47-licences', 'M47-licence-renewals', 'M47-risk', 'M47-dates'], reports: ['Licence Compliance'], forms: ['Licence', 'Licence Renewal'] }],
    ['4', 'Utilities', 6, { model: 'fix.site.utility', cols: ['site_id', 'period', 'utility_type', 'amount', 'flagged'], screens: ['M47-utilities', 'M47-utility-accounts', 'M47-costs'], reports: ['Utilities Variance'], forms: ['Utility Bill', 'Utility Account'] }],
    ['5', 'Infrastructure Assets', 9, { model: 'fix.site.asset', cols: ['name', 'site_id', 'asset_type', 'tag', 'warranty_end', 'state'], screens: ['M47-infra', 'M47-outages', 'M47-asset-requests'], reports: ['Branch Asset Register', 'Infrastructure Availability'], forms: ['Infrastructure Asset', 'Infrastructure Outage'] }],
    ['6', 'Building PM', 7, { model: 'fix.site.pm', cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'state'], screens: ['M47-pm', 'M47-power-tests'], reports: ['Infrastructure Availability'], forms: ['PM Job', 'Power Test'] }],
    ['7', 'Work Orders', 6, { model: 'fix.facility.work.order', cols: ['name', 'site_id', 'work_type', 'scheduled_date', 'assigned_to', 'state'], screens: ['M47-wo', 'M47-costs'], reports: ['Facility Work Order Performance', 'Cost per Site / per Job'], forms: ['Facility Work Order'] }],
    ['8', 'Safety & Security', 10, { model: 'fix.site.safety', cols: ['name', 'site_id', 'equipment_type', 'next_check', 'state'], screens: ['M47-safety', 'M47-security', 'M47-handoff-exceptions'], reports: [], forms: ['Safety Inspection', 'Security Incident'] }],
    ['9', 'Open / Close Projects', 6, { model: 'fix.site.project', cols: ['name', 'site_id', 'project_type', 'planned_on', 'budget', 'state'], screens: ['M47-opening'], reports: [], forms: ['Site Project'] }],
    ['10', 'Maintenance Demand Queue', 6, { model: 'fix.maintenance.demand', cols: ['name', 'origin', 'source_ref', 'site_id', 'work_order_id', 'state'], screens: ['M47-demand'], reports: [], forms: [] }]
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
      { m: 'action_request_closure', l: 'Request Closure Approval (also for a suspended site: CFO then CEO)', ask: 'Why is this site closing? The signatories read this.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
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
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_apply_modification', l: 'Apply Approved Modification' },
      { m: 'action_discard_modification', l: 'Discard Modification' },
      { m: 'action_expire', l: 'Mark Expired' },
      { m: 'action_terminate', l: 'Terminate Lease', ask: 'Why is the lease terminated?', kwarg: 'reason' },
      { m: 'action_publish_ifrs16', l: 'Publish to IFRS 16' }
    ] },
  'M47-lease-schedule': { kind: 'model_list', model: 'fix.site.lease.schedule', create: false,
    note: 'Send a month\'s rent to accounts payable when it falls due. Accounts payable matches it to the landlord\'s bill, and the match fills in what was paid.',
    cols: ['lease_id', 'site_id', 'period', 'due_date', 'escalation_year', 'rent_due', 'ap_requested_on', 'paid_amount', 'paid_on', 'invoice_ref'],
    actions: [{ m: 'action_send_to_ap', l: 'Send Rent to Accounts Payable' }] },
  'M47-lease-extracts': { kind: 'model_list', model: 'fix.site.lease.extract', create: false,
    note: 'Each row is a version of a lease\'s data, sent to finance when the lease is published, modified or terminated. To send a lease recorded earlier, use Publish to IFRS 16 on its lease.',
    cols: ['lease_id', 'site_id', 'version', 'reason', 'published_at', 'consumed_by_m19_at'] },
  'M47-dates': { kind: 'table_report', module: 'M47', report: 'critical_dates', title: 'Critical-Date Control', period: false },
  'M47-licences': { kind: 'model_list', model: 'fix.site.licence', stateField: 'state',
    cols: ['name', 'site_id', 'licence_type', 'number', 'issued_on', 'valid_to', 'evidence_filename', 'is_valid', 'state'] },
  'M47-risk': { kind: 'model_list', model: 'fix.site.risk.exception', stateField: 'state', create: false,
    cols: ['name', 'site_id', 'licence_id', 'licence_type', 'severity', 'raised_at', 'decided_by_id', 'review_due_on', 'state'],
    actions: [
      { m: 'action_decide_continue', l: 'Decide: Continue Until (dated)', asks: [
        { label: 'Review date after today (YYYY-MM-DD)', kwarg: 'review_due_on' },
        { label: 'Basis of the decision: interim arrangements and why operation continues', kwarg: 'notes' }
      ] },
      { m: 'action_decide_suspend', l: 'Decide: Suspend Site', ask: 'Basis of the suspension decision', kwarg: 'notes' }
    ] },
  'M47-utilities': { kind: 'model_list', model: 'fix.site.utility',
    cols: ['name', 'site_id', 'period', 'utility_type', 'amount', 'usage', 'unit', 'flagged', 'review_state', 'ap_requested_on', 'paid_on'],
    actions: [
      { m: 'action_flag', l: 'Hold for Review' },
      { m: 'action_release', l: 'Review: Release for Payment', ask: 'Review basis (you must not be the recorder)', kwarg: 'notes' },
      { m: 'action_confirm_anomaly', l: 'Review: Confirm Anomaly', ask: 'Review basis (you must not be the recorder)', kwarg: 'notes' },
      { m: 'action_send_to_ap', l: 'Send to Accounts Payable (older bills)' }
    ] },
  'M47-infra': { kind: 'model_list', model: 'fix.site.asset', stateField: 'state',
    cols: ['name', 'site_id', 'asset_type', 'tag', 'capacity', 'installed_on', 'warranty_end', 'power_test_due_on', 'value', 'state'],
    actions: [
      { m: 'action_maintenance', l: 'Take to Maintenance' },
      { m: 'action_restore', l: 'Restore to Service' },
      { m: 'action_request_approval', l: 'Request Retirement Approval (DOFA)', ask: 'Why should this asset be retired?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_retire', l: 'Retire Asset', ask: 'Retirement reason', kwarg: 'reason' }
    ] },
  'M47-pm': { kind: 'model_list', model: 'fix.site.pm', stateField: 'state',
    cols: ['name', 'site_id', 'service_type', 'provider_id', 'scheduled_on', 'interval_months', 'done_on', 'cost', 'work_order_id', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done' }] },
  'M47-wo': { kind: 'model_list', model: 'fix.facility.work.order', stateField: 'state',
    cols: ['name', 'site_id', 'work_type', 'priority', 'scheduled_date', 'assigned_to', 'estimated_cost', 'actual_cost', 'approval_state', 'state'],
    actions: [
      { m: 'action_triage', l: 'Triage', asks: [{ label: 'Priority: emergency, high, normal or low', kwarg: 'priority' }] },
      { m: 'action_request_approval', l: 'Request Spend Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_schedule', l: 'Schedule' },
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete', ask: 'Completion evidence: what was done and the evidence reference', kwarg: 'notes' },
      { m: 'action_verify', l: 'Verify & Close', ask: 'Verification note (required if an estimated job records no actual cost: say why it cost nothing)', kwarg: 'notes' },
      { m: 'action_reopen', l: 'Reopen', ask: 'Why is the completed work reopened?', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Cancellation reason (optional)', kwarg: 'reason' },
      { m: 'action_approve_permit', l: 'Approve Permit to Work', ask: 'Permit valid to (YYYY-MM-DD; blank = today only)', kwarg: 'valid_to' }
    ] },
  'M47-safety': { kind: 'model_list', model: 'fix.site.safety', stateField: 'state',
    cols: ['name', 'site_id', 'equipment_type', 'ref', 'last_check', 'last_result', 'next_check', 'inspection_interval_months', 'last_checked_by_id', 'state'],
    actions: [
      { m: 'action_check_pass', l: 'Record Check: Passed', ask: 'Next check date after today (YYYY-MM-DD); blank uses the item\'s inspection interval', kwarg: 'next_check' },
      { m: 'action_check_fail', l: 'Record Check: Failed', asks: [
        { label: 'Next check date after today (YYYY-MM-DD); blank uses the item\'s inspection interval', kwarg: 'next_check' },
        { label: 'What failed?', kwarg: 'finding' }
      ] }
    ] },
  'M47-security': { kind: 'model_list', model: 'fix.site.incident', stateField: 'state',
    cols: ['name', 'site_id', 'incident_type', 'occurred_on', 'severity', 'injuries_flag', 'hse_notice_due_on', 'hse_case_ref', 'state'],
    actions: [{ m: 'action_close', l: 'Close Incident', ask: 'Resolution: root cause and action taken', kwarg: 'resolution' }] },
  'M47-opening': { kind: 'model_list', model: 'fix.site.project', stateField: 'state',
    cols: ['name', 'site_id', 'project_type', 'planned_on', 'done_on', 'budget', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Budget Approval (DOFA)', ask: 'Business justification for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_start', l: 'Start Project' },
      { m: 'action_revise_budget', l: 'Revise Budget', ask: 'Reason for revising to the Proposed Budget', kwarg: 'reason' },
      { m: 'action_done', l: 'Complete Project' }
    ] },
  'M47-demand': { kind: 'model_list', model: 'fix.maintenance.demand', stateField: 'state', create: false,
    cols: ['name', 'origin', 'source_ref', 'target', 'site_id', 'vehicle_id', 'scheduled_date', 'blocker', 'work_order_id', 'service_order_id', 'state'],
    actions: [
      { m: 'action_route', l: 'Route' },
      { m: 'action_dismiss', l: 'Dismiss', ask: 'Reason for dismissing this demand', kwarg: 'reason' }
    ] },
  'M47-costs': { kind: 'model_list', model: 'fix.asset.cost.entry', stateField: 'state', create: false,
    note: 'What the asset registers say is owed: verified work orders, utility bills, rent, fuel and vehicle services. Accounts payable opens a row, chooses the vendor bill and matches it, or rejects it with a reason. Nothing here posts to the ledger.',
    cols: ['name', 'cost_type', 'source_ref', 'site_id', 'vendor_id', 'invoice_ref', 'amount', 'cost_date', 'vendor_invoice_id', 'source_changed', 'state'],
    actions: [
      { m: 'action_match_bill', l: 'Match to Chosen Bill' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is this cost rejected?', kwarg: 'reason' }
    ] },
  'M47-asset-requests': { kind: 'model_list', model: 'fix.asset.finance.request', stateField: 'state', create: false,
    note: 'Assets acquired, retired or lost in the asset registers, waiting for finance. Accepting creates a draft asset or a draft disposal in the fixed asset register; nothing is posted until that register\'s own steps are done.',
    cols: ['name', 'kind', 'source_label', 'source_ref', 'operating_unit_id', 'source_amount', 'amount', 'category_id', 'fixed_asset_id', 'disposal_id', 'state'],
    actions: [
      { m: 'action_accept', l: 'Accept' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is this request rejected?', kwarg: 'reason' }
    ] },
  'M47-lease-items': { kind: 'model_list', model: 'fix.lease.modification.item', stateField: 'state', create: false,
    note: 'A recorded lease changed after its IFRS 16 contract began. Finance remeasures the contract, or records that the change alters nothing it measures.',
    cols: ['name', 'lease_id', 'site_lease_id', 'version', 'reason', 'changes', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_mark_remeasured', l: 'Mark Remeasured', ask: 'How was it remeasured?', kwarg: 'note' },
      { m: 'action_mark_no_change', l: 'No Accounting Change', ask: 'Why does this change nothing?', kwarg: 'note' }
    ] },
  'M47-handoff-exceptions': { kind: 'model_list', model: 'fix.bridge.exception', stateField: 'state', create: false,
    note: 'A hand-off to finance or HSE that needs a person: each row says what is missing. Supply it, then Retry. An injury reported by someone with no employee record waits here until the HSE officer names the worker.',
    cols: ['name', 'route', 'source_ref', 'message', 'role_label', 'employee_id', 'attempts', 'state'],
    actions: [
      { m: 'action_retry', l: 'Retry' },
      { m: 'action_resolve', l: 'Resolve by Hand', ask: 'How was this resolved?', kwarg: 'note' }
    ] },

  /* Capture audit (2026-11-17): the registers a page could not capture. */
  'M47-site-profiles': { kind: 'model_list', model: 'fix.site.type.profile',
    note: 'What a site of each type must hold (FR-FAC-017). Every site holds a trade licence; the profile adds the rest. The readiness gate and the licence-gap figures use the profile; a type with no profile uses the estate default. Set by a Branch Operations Lead.',
    cols: ['name', 'site_type', 'required_summary', 'notes', 'active'] },
  'M47-lease-events': { kind: 'model_list', model: 'fix.site.lease.event', stateField: 'state',
    note: 'The dated obligations of each lease besides its renewal notice and end: rent reviews, break options, deposit returns and landlord obligations. Each has an owner and is alerted at 90/60/30/15/7 days and when it passes. A review or a break is decided by the CFO; an obligation is met by its owner or a Branch Operations Lead. Nobody decides an event they recorded.',
    cols: ['name', 'lease_id', 'site_id', 'event_type', 'due_on', 'days_left', 'responsible_id', 'amount', 'decision', 'state'],
    actions: [
      { m: 'action_decide_exercise', l: 'CFO Decision: Exercise / Proceed', ask: 'Basis of the decision', kwarg: 'notes' },
      { m: 'action_decide_decline', l: 'CFO Decision: Do Not Exercise / Waive', ask: 'Basis of the decision', kwarg: 'notes' },
      { m: 'action_mark_met', l: 'Mark Obligation Met', ask: 'How was it met? (evidence reference)', kwarg: 'notes' },
      { m: 'action_cancel', l: 'Cancel Event', ask: 'Why is this event cancelled?', kwarg: 'reason' }
    ] },
  'M47-licence-renewals': { kind: 'model_list', model: 'fix.site.licence.renewal', stateField: 'state',
    note: 'A renewal from initiation to the new licence (FR-FAC-021): who is responsible, the documents, the fee challan, the inspection and the cost. A trade licence renewal is refused while the fire licence is expired (BRU-FAC-03). Complete it once the new licence is on Statutory Licences with its scan.',
    cols: ['name', 'licence_id', 'site_id', 'licence_type', 'expires_on', 'responsible_id', 'submitted_on', 'total_cost', 'new_licence_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit to Authority' },
      { m: 'action_complete', l: 'Complete (Renewed Licence Recorded)' },
      { m: 'action_cancel', l: 'Cancel Renewal', ask: 'Why is the renewal cancelled?', kwarg: 'reason' }
    ] },
  'M47-utility-accounts': { kind: 'model_list', model: 'fix.site.utility.account', stateField: 'state',
    note: 'Each supply account of a site: provider, account number, meter, tariff and billing cycle (FR-FAC-038). A bill is recorded against its account; a site with one active account of a utility has it filled in, and one with several asks which meter.',
    cols: ['name', 'site_id', 'utility_type', 'provider_id', 'account_no', 'meter_no', 'tariff', 'billing_cycle', 'state'],
    actions: [{ m: 'action_close', l: 'Close Account', ask: 'Why is the account closed (disconnected, moved, merged)?', kwarg: 'reason' }] },
  'M47-outages': { kind: 'model_list', model: 'fix.site.outage', stateField: 'state',
    note: 'A building service that stopped: power, generator, UPS, air conditioning, water, connectivity (FR-FAC-027). Anyone at the branch records it; End Outage computes the duration and, when the branch could not operate, the operating hours lost.',
    cols: ['name', 'site_id', 'service', 'asset_id', 'started_at', 'ended_at', 'duration_hours', 'branch_stopped', 'operating_hours_lost', 'state'],
    actions: [{ m: 'action_end', l: 'End Outage', ask: 'Service restored at (YYYY-MM-DD HH:MM; blank = now)', kwarg: 'ended_at' }] },
  'M47-power-tests': { kind: 'model_list', model: 'fix.site.power.test',
    note: 'The generator and UPS test regime (FR-FAC-026): load test, run, battery and fuel checks with the hour meter. A failed test raises a corrective work order. A generator or UPS whose test is overdue is escalated to the Operations Director (BRU-FAC-10). A test is what was measured: correct it with a new test.',
    cols: ['name', 'asset_id', 'site_id', 'tested_on', 'test_type', 'result', 'run_hours', 'fuel_level_pct', 'battery_condition', 'work_order_id'] },
  'M47-rpt-availability': { kind: 'table_report', module: 'M47', report: 'infrastructure_availability', title: 'Infrastructure Availability', period: false },

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
      { tab: 'closure', title: 'Status-Change Sign-off', note: 'Opening (readiness gate) and resuming a suspended site need the Operations Director. Closing or reopening needs two routed sign-offs by two different people, neither the requester nor the creator: the CFO (DOFA Tier 4), then the CEO (DOFA Tier 5); request approval once for each. A suspended site that will not resume is closed the same way, with Request Closure Approval, and closing resolves its operating-risk exceptions. A reopened site returns to Planned. A site is suspended only by the continue-or-suspend decision on an operating-risk exception.',
        fields: [
          { name: 'closure_requested', label: 'Closure Requested', readonly: true },
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
      { tab: 'lease', title: 'Lease', note: 'The end date cannot precede the start (database CHECK). Once recorded, the site, lessor, dates, rent, escalation and deposit change only through a renewal or modification; a notice period left blank may be filled in once. Recording a lease builds its monthly rent schedule (escalated on each anniversary) and publishes the lease data extract for M19 / M49; a lease recorded before that existed is sent with Publish to IFRS 16. A lease recorded after its end date is born Expired, and the daily job expires an active lease once its end date passes. A Branch Operations Lead terminates a lease, and finance is told.',
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
      { tab: 'modification', title: 'Proposed Terms', note: 'Open Renewal / Modification copies the current terms here. Edit them, request approval (DOFA on the total remaining rent commitment, or on the rent given up when the term is shortened), then apply. Changing a proposal after approval withdraws the approval.',
        fields: [
          { name: 'modification_open', label: 'Modification Open', readonly: true },
          { name: 'proposed_end_date', label: 'Proposed End Date' },
          { name: 'proposed_monthly_rent', label: 'Proposed Monthly Rent' },
          { name: 'proposed_escalation_pct', label: 'Proposed Escalation %' },
          { name: 'proposed_deposit', label: 'Proposed Deposit' },
          { name: 'proposed_notice_period_days', label: 'Proposed Renewal Notice (days)' },
          { name: 'proposed_lessor_id', label: 'Proposed Lessor' },
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
      { title: 'Statutory Licence', note: 'Valid today is computed on every read: the state must be Valid, an end date must be recorded and it must not have passed (a licence with no end date is not valid). Its end date does not change once recorded, and a lapsed licence cannot be made valid again; record the renewal as a new licence, with its number and its scan. A trade licence renewal is refused while the site\'s fire licence is expired (BRU-FAC-03). The daily job alerts at 90/60/30/15/7 days, marks a lapsed licence Expired and raises an operating-risk exception at an operational site. Licences are edited by a Facility Manager.',
        fields: [
          { name: 'name', required: true, label: 'Licence Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'licence_type', required: true, label: 'Licence Type' },
          { name: 'number', required: true, label: 'Licence Number' },
          { name: 'authority', label: 'Issuing Authority' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'fee', label: 'Licence Fee' },
          { name: 'responsible_id', label: 'Responsible for Renewal (not the decider of a lapse)' },
          { name: 'evidence_file', label: 'Licence Scan (required for a new licence)', type: 'file' },
          { name: 'evidence_filename', label: 'Scan File Name' },
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
      { id: 'order', label: '1. Work Order', bn: '১. কাজের আদেশ', icon: '🛠️', badge: '9' },
      { id: 'cost', label: '2. Scope, Cost & Approval', bn: '২. ব্যয় ও অনুমোদন', icon: '💳', badge: '8' },
      { id: 'permit', label: '3. Permit to Work', bn: '৩. কাজের অনুমতি', icon: '⚠️', badge: '6' },
      { id: 'evidence', label: '4. Completion & Verification', bn: '৪. সমাপ্তি ও যাচাই', icon: '🔐', badge: '8' },
      { id: 'origin', label: '5. Asset & Origin', bn: '৫. সম্পদ ও উৎস', icon: '🔗', badge: '7' }
    ],
    sections: [
      { tab: 'order', title: 'Work Order', note: 'Draft → (spend approval) → scheduled → in progress → completed (with evidence) → verified by someone who neither raised nor completed it. A request raised by a person is triaged by a Facility Manager before its approval or schedule. A Facility Manager cancels before completion, or reopens to void a completion.',
        fields: [
          { name: 'name', required: true, label: 'Work Order' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_id', label: 'Target Equipment' },
          { name: 'work_type', required: true, label: 'Work Type' },
          { name: 'assigned_to', label: 'Assigned Engineer' },
          { name: 'scheduled_date', label: 'Scheduled Date' },
          { name: 'request_photo', label: 'Photo of the Problem', type: 'file' },
          { name: 'request_photo_filename', label: 'Photo File Name' },
          { name: 'priority', label: 'Priority (Triage)', readonly: true },
          { name: 'triaged_by_id', label: 'Triaged By', readonly: true },
          { name: 'triaged_on', label: 'Triaged On', readonly: true },
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
      { tab: 'evidence', title: 'Completion & Verification (BRU-FAC-07)', note: 'Completion records the evidence and who completed it; verification by a Facility Manager who neither raised nor completed it closes the work order and sends the actual cost (and the vendor invoice reference) to accounts payable. An estimated job with no actual cost is verified only with a note saying why it cost nothing.',
        fields: [
          { name: 'completion_notes', type: 'text', label: 'Completion Evidence' },
          { name: 'completion_evidence_file', label: 'Evidence File (photo, service report, job sheet)', type: 'file' },
          { name: 'completion_evidence_filename', label: 'Evidence File Name' },
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
    create: false, pick: 'A maintenance demand is raised by its source module (M45, M46, M48, M17): open one from the Maintenance Demand Queue, fill the fact it needs and Route it. A facility request you raise yourself is a Facility Work Order.',
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
          { name: 'vehicle_id', label: 'Vehicle (M46)', readonly: true },
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
      { title: 'Safety Equipment', note: 'The status is derived from the next check date: overdue once it has passed, due within 30 days. Record Check stamps today as the last check, who did it and whether the item passed, and sets the next check date given, or rolls it by the item\'s inspection interval; the next check cannot be pushed later by editing. An item that failed is Unfit until a later check passes, and M59 raises a hazard for it. The daily job reports an overdue item to M59 as unfit.',
        fields: [
          { name: 'name', required: true, label: 'Check Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'equipment_type', required: true, label: 'Equipment Type' },
          { name: 'ref', label: 'Tag / Reference' },
          { name: 'last_check', label: 'Last Check', readonly: true },
          { name: 'last_checked_by_id', label: 'Last Checked By', readonly: true },
          { name: 'last_result', label: 'Last Result', readonly: true },
          { name: 'last_finding', label: 'What Failed', readonly: true },
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
    tabs: [
      { id: 'asset', label: '1. Asset', bn: '১. সম্পদ', icon: '🏗️', badge: '13' },
      { id: 'status', label: '2. Status & Tests', bn: '২. অবস্থা ও পরীক্ষা', icon: '🔋', badge: '6' }
    ],
    sections: [
      { tab: 'asset', title: 'Plant Asset (FR-FAC-024)', note: 'A fixed building-service asset of the site: generator, UPS, air conditioning, electrical distribution, CCTV, lift, fire pump. Make, model, capacity and expected life feed the replacement view. Operational → under maintenance → operational; retirement is final and, above Tier 0, needs a DOFA approval of the asset value. The register drives the Branch Asset Register count and value.',
        fields: [
          { name: 'name', required: true, label: 'Asset Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'asset_type', required: true, label: 'Asset Type' },
          { name: 'tag', label: 'Asset Tag' },
          { name: 'serial_no', label: 'Serial No' },
          { name: 'make', label: 'Make' },
          { name: 'model_name', label: 'Model' },
          { name: 'capacity', label: 'Capacity (kVA, TR, kW)' },
          { name: 'installed_on', label: 'Installed On' },
          { name: 'warranty_end', label: 'Warranty End' },
          { name: 'expected_life_months', label: 'Expected Life (months)' },
          { name: 'value', label: 'Asset Value' },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'status', title: 'Status, Retirement and Power Tests', note: 'A generator or UPS is tested on the regime of Generator / UPS Tests (Building PM page); one whose test is overdue is escalated to the Operations Director.',
        fields: [
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'approval_state', label: 'Retirement Approval (M63)', readonly: true },
          { name: 'retired_on', label: 'Retired On', readonly: true },
          { name: 'retire_reason', label: 'Retirement Reason', readonly: true },
          { name: 'last_power_test_on', label: 'Last Generator / UPS Test', readonly: true },
          { name: 'power_test_due_on', label: 'Next Test Due', readonly: true }
        ] }
    ]
  },

  'M47-form-utility': {
    kind: 'model_form',
    model: 'fix.site.utility',
    title: 'Utility Bill',
    back: 'M47-utilities',
    tabs: [
      { id: 'bill', label: '1. Bill', bn: '১. বিল', icon: '💡', badge: '9' },
      { id: 'review', label: '2. Anomaly Review & Payment', bn: '২. পর্যালোচনা ও পরিশোধ', icon: '🔎', badge: '9' }
    ],
    sections: [
      { tab: 'bill', title: 'Utility Bill', note: 'One bill per utility account (meter) and period (YYYY-MM); a site with one active account of the utility has it filled in, a site with several is asked which meter. A bill with no account keeps one bill per site, utility type and month. On record the bill is compared with its own average over up to the last 3 periods; at the configured multiple (default 2.0, pending business confirmation) it is held from payment. A bill not held goes to accounts payable as a pending cost entry; a held one goes only when a Branch Operations Lead who did not record it releases it, and accounts payable cannot match it while it is held. The match fills in what was paid. The figures of a reviewed or paid bill are frozen.',
        fields: [
          { name: 'name', required: true, label: 'Bill Reference' },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'account_id', label: 'Utility Account (meter)' },
          { name: 'period', required: true, label: 'Period (YYYY-MM)' },
          { name: 'utility_type', required: true, label: 'Utility Type' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'usage', label: 'Usage' },
          { name: 'unit', label: 'Unit' },
          { name: 'notes', label: 'Notes' }
        ] },
      { tab: 'review', title: 'Anomaly Review & Payment (BRU-FAC-11)', note: 'Set by the anomaly evaluation, the reviewer and the accounts-payable match; nobody types them.',
        fields: [
          { name: 'flagged', label: 'Anomaly Flagged', readonly: true },
          { name: 'review_state', label: 'Payment Hold', readonly: true },
          { name: 'anomaly_basis', label: 'Anomaly Basis', readonly: true },
          { name: 'reviewed_by_id', label: 'Reviewed By', readonly: true },
          { name: 'review_notes', label: 'Review Notes', readonly: true },
          { name: 'ap_requested_on', label: 'Sent to Accounts Payable On', readonly: true },
          { name: 'paid_amount', label: 'Paid', readonly: true },
          { name: 'paid_on', label: 'Paid On', readonly: true },
          { name: 'invoice_ref', label: 'Invoice Ref', readonly: true }
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
      { title: 'PM Job', note: 'Only an open job can be marked done, by a Facility Manager; Mark Done records the done date and, when a repeat interval is set, schedules the next job. The daily job raises a facility work order for an open job once it is due, at an operational or suspended site; verifying that order is what completes the job.',
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
      { title: 'Incident', note: 'Only an open incident can be closed, with a resolution, by someone other than its reporter: a Facility Manager, or for an injury HSE or a Branch Operations Lead. A fire, theft or trespass is logged on the site\'s risk entry (M60) and raises a hazard for the HSE officer (M59). An injury is logged on the risk entry too, carries the BLA 2006 s.80 Inspector-notice date (counted again if the accident date is corrected) and the bridge links its HSE case. The resolution is frozen once closed.',
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
      { title: 'Exception (BRU-FAC-02)', note: 'Raised by the daily job when a licence lapses at an operational site. The Operations Director or the CEO (DOFA Tier 5) records a named, dated continue-or-suspend decision; the person responsible for the renewal (the licence recorder, the site\'s accountable manager) cannot. Press the decision button: it asks for the basis and, for a continue decision, the review date. A continue decision lapses on its review date and must be taken again; undecided exceptions are escalated daily. Recording the renewed licence resolves it, and so does closing the site.',
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
    create: false, pick: 'Rent schedule rows are built by the lease from its terms: open one from the Rent Schedule.',
    sections: [
      { title: 'Scheduled Rent (FR-FAC-012)', note: 'Built by the lease from its terms: one row per month, the rent escalated on each anniversary. Send Rent to Accounts Payable raises a pending cost entry on the landlord; accounts payable matching it to the landlord\'s bill fills in the paid amount, date and invoice reference. Nobody edits the rows directly.',
        fields: [
          { name: 'lease_id', label: 'Lease', readonly: true },
          { name: 'period', label: 'Period', readonly: true },
          { name: 'due_date', label: 'Due Date', readonly: true },
          { name: 'escalation_year', label: 'Lease Year', readonly: true },
          { name: 'rent_due', label: 'Rent Due', readonly: true },
          { name: 'ap_requested_on', label: 'Sent to Accounts Payable On', readonly: true },
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
    create: false, pick: 'A lease data extract is published by the lease itself: open one from Lease Data Extracts.',
    sections: [
      { title: 'IFRS 16 Data Extract (BRU-FAC-13 / -14)', note: 'A versioned, insert-only copy of the accounting-relevant lease data, published to M19 / M49 when a lease is recorded, on every modification and when it is terminated. A lease recorded before this existed has no extract until a Facility Manager presses Publish to IFRS 16 on it. M47 never computes the right-of-use asset or the lease liability.',
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

  'M47-form-cost': {
    kind: 'model_form',
    model: 'fix.asset.cost.entry',
    title: 'Cost Entry',
    back: 'M47-costs',
    status: { field: 'state', labels: { pending: 'Pending AP', matched: 'Matched to Bill', rejected: 'Rejected' } },
    tabs: [
      { id: 'owed', label: '1. What Is Owed', bn: '১. যা পাওনা', icon: '🧾', badge: '13' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'owed', title: 'What Is Owed', note: 'The figures come from the source record. Nothing here posts to the ledger; the vendor bill keeps its own match and approval.',
        fields: [
          { name: 'name', label: 'Entry', readonly: true },
          { name: 'cost_type', label: 'Type', readonly: true },
          { name: 'source_ref', label: 'Source', readonly: true },
          { name: 'detail', label: 'Detail', readonly: true },
          { name: 'site_id', label: 'Site', readonly: true },
          { name: 'vehicle_id', label: 'Vehicle', readonly: true },
          { name: 'branch_id', label: 'Branch', readonly: true },
          { name: 'operating_unit_id', label: 'Cost Centre (Operating Unit)' },
          { name: 'vendor_id', label: 'Vendor', readonly: true },
          { name: 'invoice_ref', label: 'Vendor Invoice Ref', readonly: true },
          { name: 'amount', label: 'Cost', readonly: true },
          { name: 'cost_date', label: 'Cost Date', readonly: true },
          { name: 'source_changed', label: 'Source Changed After the Decision', readonly: true }
        ] },
      { tab: 'decision', title: 'Decision', note: 'Choose the vendor bill and save, then Match to Chosen Bill on the list. To reject, say why. A utility bill held for review cannot be matched until it is released.',
        fields: [
          { name: 'match_invoice_id', label: 'Bill to Match' },
          { name: 'decision_note', type: 'text', label: 'Decision Note' },
          { name: 'vendor_invoice_id', label: 'Matched Bill', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
        ] }
    ]
  },

  'M47-form-asset-request': {
    kind: 'model_form',
    model: 'fix.asset.finance.request',
    title: 'Asset Finance Request',
    back: 'M47-asset-requests',
    status: { field: 'state', labels: { pending: 'Pending Finance', accepted: 'Accepted', rejected: 'Rejected', withdrawn: 'Withdrawn by the Source' } },
    tabs: [
      { id: 'reported', label: '1. What the Register Reported', bn: '১. রেজিস্টারের তথ্য', icon: '📋', badge: '8' },
      { id: 'finance', label: '2. Finance', bn: '২. অর্থ', icon: '💳', badge: '12' }
    ],
    sections: [
      { tab: 'reported', title: 'What the Register Reported', note: 'Raised by the asset register that holds the item.',
        fields: [
          { name: 'name', label: 'Request', readonly: true },
          { name: 'kind', label: 'Kind', readonly: true },
          { name: 'source_label', label: 'Register', readonly: true },
          { name: 'source_ref', label: 'Source Item', readonly: true },
          { name: 'event_type', label: 'Raised By', readonly: true },
          { name: 'source_amount', label: 'Amount in the Source Register', readonly: true },
          { name: 'basis', type: 'text', label: 'Basis', readonly: true },
          { name: 'custodian_id', label: 'Custodian', readonly: true }
        ] },
      { tab: 'finance', title: 'Finance', note: 'To capitalise: choose the category and the posted journal item that carries the cost, then Accept; a draft asset is created. To dispose: choose the asset and the disposal type, then Accept; a draft disposal is created. To reject, say why.',
        fields: [
          { name: 'operating_unit_id', label: 'Branch' },
          { name: 'amount', label: 'Amount to Capitalise' },
          { name: 'acquisition_date', label: 'Acquisition Date' },
          { name: 'category_id', label: 'Asset Category' },
          { name: 'acquisition_line_id', label: 'Acquisition Journal Item' },
          { name: 'fixed_asset_id', label: 'Fixed Asset' },
          { name: 'disposal_kind', label: 'Disposal Type' },
          { name: 'disposal_id', label: 'Draft Disposal', readonly: true },
          { name: 'decision_note', type: 'text', label: 'Decision Note' },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
        ] }
    ]
  },

  'M47-form-lease-item': {
    kind: 'model_form',
    model: 'fix.lease.modification.item',
    title: 'Lease Remeasurement Item',
    back: 'M47-lease-items',
    status: { field: 'state', labels: { open: 'Open: Remeasure', remeasured: 'Remeasured', no_change: 'No Accounting Change' } },
    sections: [
      { title: 'What Changed', note: 'The contract in the book was not changed. Finance remeasures it, or records that this version alters nothing it measures.',
        fields: [
          { name: 'name', label: 'Item', readonly: true },
          { name: 'lease_id', label: 'IFRS 16 Contract', readonly: true },
          { name: 'site_lease_id', label: 'Site Lease', readonly: true },
          { name: 'version', label: 'Lease Version', readonly: true },
          { name: 'reason', label: 'Reason', readonly: true },
          { name: 'changes', type: 'text', label: 'Terms That Differ', readonly: true },
          { name: 'extract', type: 'text', label: 'Lease Data of This Version', readonly: true },
          { name: 'decision_note', type: 'text', label: 'Decision Note' },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
        ] }
    ]
  },

  'M47-form-handoff-exception': {
    kind: 'model_form',
    model: 'fix.bridge.exception',
    title: 'Hand-off Problem',
    back: 'M47-handoff-exceptions',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    sections: [
      { title: 'What Is Needed', note: 'Supply what the row asks for, save, then Retry on the list. If the hand-off was done another way, Resolve by Hand and say how.',
        fields: [
          { name: 'name', label: 'Hand-off', readonly: true },
          { name: 'route', label: 'Going To', readonly: true },
          { name: 'source_ref', label: 'Source', readonly: true },
          { name: 'message', type: 'text', label: 'What Is Needed', readonly: true },
          { name: 'role_label', label: 'Resolved By (Role)', readonly: true },
          { name: 'employee_id', label: 'Worker Involved' },
          { name: 'attempts', label: 'Attempts', readonly: true },
          { name: 'resolved_by_id', label: 'Resolved By', readonly: true },
          { name: 'resolved_at', label: 'Resolved At', readonly: true },
          { name: 'state', label: 'State (workflow actions)', readonly: true }
        ] }
    ]
  },

  /* ===== Capture audit (2026-11-17): the forms of the new registers ===== */
  'M47-form-site-profile': {
    kind: 'model_form',
    model: 'fix.site.type.profile',
    title: 'Site Type Profile',
    back: 'M47-site-profiles',
    sections: [
      { title: 'What This Site Type Must Hold (FR-FAC-002 / -017, BRU-FAC-01)', note: 'Every site holds a current trade licence. Tick the other licences a site of this type needs before it opens (readiness gate) and while it operates (licence gaps). One profile per site type; a type with no profile uses the estate default. Set by a Branch Operations Lead.',
        fields: [
          { name: 'name', label: 'Profile', readonly: true },
          { name: 'site_type', required: true, label: 'Site Type' },
          { name: 'req_fire', label: 'Fire Licence (FSCD)' },
          { name: 'req_health', label: 'Health / Sanitation Licence' },
          { name: 'req_environment', label: 'Environmental Clearance' },
          { name: 'req_signage', label: 'Signage Permit' },
          { name: 'req_generator', label: 'Generator / Fuel Storage Permit' },
          { name: 'required_summary', label: 'Licences Required', readonly: true },
          { name: 'notes', type: 'text', label: 'Basis (authority, local requirement)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M47-form-lease-event': {
    kind: 'model_form',
    model: 'fix.site.lease.event',
    title: 'Lease Critical Event',
    back: 'M47-lease-events',
    status: { field: 'state', labels: { open: 'Open', done: 'Decided / Met', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Event (FR-FAC-009 / -010)', note: 'A dated obligation the lease contains, with its owner. Alerts go out at 90/60/30/15/7 days and once it passes; it stays on Critical-Date Control until decided. Recorded by a Facility Manager; a re-dated event is alerted again.',
        fields: [
          { name: 'name', label: 'Event', readonly: true },
          { name: 'lease_id', required: true, label: 'Lease' },
          { name: 'site_id', label: 'Site', readonly: true },
          { name: 'event_type', required: true, label: 'Event Type' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'responsible_id', required: true, label: 'Responsible' },
          { name: 'amount', label: 'Amount Involved' },
          { name: 'description', type: 'text', label: 'What the Lease Says (required for an obligation)' }
        ] },
      { title: 'Decision', note: 'A rent review or a break option is decided by the CFO (DOFA Tier 4): exercise or not. Any other obligation is marked met by its owner or a Branch Operations Lead. Nobody decides an event they recorded. Use the buttons on the list.',
        fields: [
          { name: 'state', label: 'State (decision actions)', readonly: true },
          { name: 'decision', label: 'Decision', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decided_on', label: 'Decided On', readonly: true },
          { name: 'outcome_notes', label: 'Basis / Outcome', readonly: true }
        ] }
    ]
  },

  'M47-form-licence-renewal': {
    kind: 'model_form',
    model: 'fix.site.licence.renewal',
    title: 'Licence Renewal',
    back: 'M47-licence-renewals',
    status: { field: 'state', labels: { initiated: 'Initiated', submitted: 'Submitted', completed: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'renewal', label: '1. Renewal', bn: '১. নবায়ন', icon: '📜', badge: '9' },
      { id: 'fees', label: '2. Fees & Inspection', bn: '২. ফি ও পরিদর্শন', icon: '💳', badge: '10' },
      { id: 'completion', label: '3. Completion', bn: '৩. সমাপ্তি', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'renewal', title: 'Renewal (FR-FAC-021)', note: 'Opened by a Facility Manager for a licence that is due; one renewal in progress per licence. A trade licence renewal cannot be opened or submitted while the site fire licence is expired (BRU-FAC-03): renew the fire licence first. Submit once the documents are assembled and the fee challan is in hand.',
        fields: [
          { name: 'name', label: 'Renewal', readonly: true },
          { name: 'licence_id', required: true, label: 'Licence Being Renewed' },
          { name: 'site_id', label: 'Site', readonly: true },
          { name: 'licence_type', label: 'Licence Type', readonly: true },
          { name: 'expires_on', label: 'Expires On', readonly: true },
          { name: 'responsible_id', required: true, label: 'Responsible Person' },
          { name: 'authority', label: 'Issuing Authority' },
          { name: 'initiated_on', required: true, label: 'Initiated On' },
          { name: 'documents_assembled', label: 'Documents Assembled (occupancy proof, TIN, fire licence)' }
        ] },
      { tab: 'fees', title: 'Fees & Inspection', note: 'A government fee needs its challan or receipt reference before submission. A late penalty needs its reason, and the person responsible does not complete a renewal that paid one. Completed renewals count in Cost per Site.',
        fields: [
          { name: 'challan_ref', label: 'Fee Challan / Receipt Ref' },
          { name: 'government_fee', label: 'Government Fee' },
          { name: 'other_cost', label: 'Agent / Inspection Cost' },
          { name: 'penalty', label: 'Late Penalty' },
          { name: 'penalty_reason', label: 'Why a Penalty Was Paid' },
          { name: 'total_cost', label: 'Total Cost', readonly: true },
          { name: 'inspection_required', label: 'Inspection Required' },
          { name: 'inspection_on', label: 'Inspected On' },
          { name: 'receipt_file', label: 'Fee Receipt (scan)', type: 'file' },
          { name: 'receipt_filename', label: 'Fee Receipt File Name' }
        ] },
      { tab: 'completion', title: 'Completion', note: 'Record the new licence on Statutory Licences with its number, dates and scan, choose it here and save, then Complete on the list. It must be the same site and type, current, and run later than the licence it renews. Everything is frozen once completed.',
        fields: [
          { name: 'new_licence_id', label: 'Renewed Licence' },
          { name: 'state', label: 'State (workflow actions)', readonly: true },
          { name: 'submitted_on', label: 'Submitted On', readonly: true },
          { name: 'submitted_by_id', label: 'Submitted By', readonly: true },
          { name: 'completed_by_id', label: 'Completed By', readonly: true },
          { name: 'completed_on', label: 'Completed On', readonly: true }
        ] }
    ]
  },

  'M47-form-utility-account': {
    kind: 'model_form',
    model: 'fix.site.utility.account',
    title: 'Utility Account',
    back: 'M47-utility-accounts',
    status: { field: 'state', labels: { active: 'Active', closed: 'Closed' } },
    sections: [
      { title: 'Supply Account (FR-FAC-038)', note: 'One account per provider account number. The site, utility, provider and account number do not change once recorded: a new connection is a new account. The meter, tariff, billing cycle and capacity may be updated. Registered and closed by a Facility Manager; a closed account bills nothing after its closing month.',
        fields: [
          { name: 'name', label: 'Account', readonly: true },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'utility_type', required: true, label: 'Utility' },
          { name: 'provider_id', required: true, label: 'Provider (DESCO, DPDC, WASA, Titas, ISP)' },
          { name: 'account_no', required: true, label: 'Account / Customer No' },
          { name: 'meter_no', label: 'Meter Identifier' },
          { name: 'tariff', label: 'Tariff' },
          { name: 'billing_cycle', required: true, label: 'Billing Cycle' },
          { name: 'connection_capacity', label: 'Connection Capacity' },
          { name: 'active_from', required: true, label: 'Active From' },
          { name: 'notes', label: 'Notes' },
          { name: 'state', label: 'State (Close Account)', readonly: true },
          { name: 'closed_on', label: 'Closed On', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true },
          { name: 'close_reason', label: 'Close Reason', readonly: true }
        ] }
    ]
  },

  'M47-form-outage': {
    kind: 'model_form',
    model: 'fix.site.outage',
    title: 'Infrastructure Outage',
    back: 'M47-outages',
    status: { field: 'state', labels: { open: 'Ongoing', ended: 'Ended' } },
    sections: [
      { title: 'Outage (FR-FAC-027)', note: 'Recorded by anyone at the branch when a building service stops. Tick Branch Could Not Operate when the counter or workshop stopped: its duration then counts as operating hours lost. End Outage on the list records when the service came back; the facts are frozen once it has ended. Raise a facility work order for the repair and link it here.',
        fields: [
          { name: 'name', label: 'Outage', readonly: true },
          { name: 'site_id', required: true, label: 'Site' },
          { name: 'service', required: true, label: 'Service Lost' },
          { name: 'asset_id', label: 'Asset That Failed' },
          { name: 'started_at', required: true, label: 'Started' },
          { name: 'cause', required: true, type: 'text', label: 'Cause' },
          { name: 'branch_stopped', label: 'Branch Could Not Operate' },
          { name: 'workaround', label: 'Workaround Used' },
          { name: 'work_order_id', label: 'Repair Work Order' },
          { name: 'state', label: 'State (End Outage)', readonly: true },
          { name: 'ended_at', label: 'Ended', readonly: true },
          { name: 'duration_hours', label: 'Duration (h)', readonly: true },
          { name: 'operating_hours_lost', label: 'Operating Hours Lost', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true },
          { name: 'ended_by_id', label: 'Ended By', readonly: true }
        ] }
    ]
  },

  'M47-form-power-test': {
    kind: 'model_form',
    model: 'fix.site.power.test',
    title: 'Generator / UPS Test',
    back: 'M47-power-tests',
    tabs: [
      { id: 'test', label: '1. Test', bn: '১. পরীক্ষা', icon: '🔋', badge: '9' },
      { id: 'readings', label: '2. Readings & Finding', bn: '২. রিডিং ও ফলাফল', icon: '📟', badge: '7' }
    ],
    sections: [
      { tab: 'test', title: 'Test (FR-FAC-026, BRU-FAC-10)', note: 'Recorded at the branch on the day of the test. A UPS takes a load test or a battery check; a generator any test. A failed test needs what failed and raises a corrective facility work order at an operational site. A test is a record of what was measured: a correction is a new test.',
        fields: [
          { name: 'name', label: 'Test', readonly: true },
          { name: 'asset_id', required: true, label: 'Generator / UPS' },
          { name: 'site_id', label: 'Site', readonly: true },
          { name: 'asset_type', label: 'Asset Type', readonly: true },
          { name: 'tested_on', required: true, label: 'Tested On' },
          { name: 'test_type', required: true, label: 'Test' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'tested_by_id', label: 'Tested By', readonly: true },
          { name: 'work_order_id', label: 'Corrective Work Order', readonly: true }
        ] },
      { tab: 'readings', title: 'Readings & Finding', note: 'The hour meter never goes back: a reading below an earlier test of the same asset is refused.',
        fields: [
          { name: 'run_hours', label: 'Hour Meter Reading' },
          { name: 'load_pct', label: 'Load Carried (%)' },
          { name: 'duration_min', label: 'Run Duration (min)' },
          { name: 'fuel_level_pct', label: 'Fuel Level (%)' },
          { name: 'battery_condition', label: 'Battery Condition' },
          { name: 'finding', type: 'text', label: 'What Failed / Was Found (required when failed)' },
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
  'M47:Facility Work Order Performance': 'M47-rpt-wo',
  'M47:Infrastructure Availability': 'M47-rpt-availability'
};

export const FORM_MODELS = {
  'M47:Site': 'fix.site',
  'M47:Lease': 'fix.site.lease',
  'M47:Licence': 'fix.site.licence',
  'M47:Facility Work Order': 'fix.facility.work.order',
  'M47:Safety Inspection': 'fix.site.safety',
  'M47:Site Condition': 'fix.site.condition',
  'M47:Site Type Profile': 'fix.site.type.profile',
  'M47:Lease Critical Event': 'fix.site.lease.event',
  'M47:Licence Renewal': 'fix.site.licence.renewal',
  'M47:Utility Bill': 'fix.site.utility',
  'M47:Utility Account': 'fix.site.utility.account',
  'M47:Infrastructure Asset': 'fix.site.asset',
  'M47:Infrastructure Outage': 'fix.site.outage',
  'M47:PM Job': 'fix.site.pm',
  'M47:Power Test': 'fix.site.power.test',
  'M47:Security Incident': 'fix.site.incident',
  'M47:Site Project': 'fix.site.project'
};

export const FORM_CHIPS = {
  'M47:Site': 'M47-form-site',
  'M47:Lease': 'M47-form-lease',
  'M47:Licence': 'M47-form-licence',
  'M47:Facility Work Order': 'M47-form-wo',
  'M47:Safety Inspection': 'M47-form-safety',
  'M47:Site Condition': 'M47-form-condition',
  'M47:Site Type Profile': 'M47-form-site-profile',
  'M47:Lease Critical Event': 'M47-form-lease-event',
  'M47:Licence Renewal': 'M47-form-licence-renewal',
  'M47:Utility Bill': 'M47-form-utility',
  'M47:Utility Account': 'M47-form-utility-account',
  'M47:Infrastructure Asset': 'M47-form-asset',
  'M47:Infrastructure Outage': 'M47-form-outage',
  'M47:PM Job': 'M47-form-pm',
  'M47:Power Test': 'M47-form-power-test',
  'M47:Security Incident': 'M47-form-incident',
  'M47:Site Project': 'M47-form-project',
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
    'fix.site.lease.extract': 'M47-form-lease-extract',
    'fix.asset.cost.entry': 'M47-form-cost',
    'fix.asset.finance.request': 'M47-form-asset-request',
    'fix.lease.modification.item': 'M47-form-lease-item',
    'fix.bridge.exception': 'M47-form-handoff-exception',
    'fix.site.type.profile': 'M47-form-site-profile',
    'fix.site.lease.event': 'M47-form-lease-event',
    'fix.site.licence.renewal': 'M47-form-licence-renewal',
    'fix.site.utility.account': 'M47-form-utility-account',
    'fix.site.outage': 'M47-form-outage',
    'fix.site.power.test': 'M47-form-power-test'
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
    'M47-lease-extracts': 'M47-form-lease-extract',
    'M47-costs': 'M47-form-cost',
    'M47-asset-requests': 'M47-form-asset-request',
    'M47-lease-items': 'M47-form-lease-item',
    'M47-handoff-exceptions': 'M47-form-handoff-exception',
    'M47-site-profiles': 'M47-form-site-profile',
    'M47-lease-events': 'M47-form-lease-event',
    'M47-licence-renewals': 'M47-form-licence-renewal',
    'M47-utility-accounts': 'M47-form-utility-account',
    'M47-outages': 'M47-form-outage',
    'M47-power-tests': 'M47-form-power-test'
  }
};

export const CREATE = {
  M47: { screen: 'M47-form-site', model: 'fix.site', label: 'Site' }
};
