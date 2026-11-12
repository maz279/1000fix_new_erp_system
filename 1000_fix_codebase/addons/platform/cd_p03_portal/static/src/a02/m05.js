/** @odoo-module **/
/* A02 · Service Operations — M05 Remote Support & MSP.
 * This fragment mirrors the CANONICAL registry M05: 5 groups, 13 screens,
 * 6 KPIs, 6 reports, freg 93 functions in 10 subs.
 *
 * Iteration 2 (2026-10-26): every screen is now a LIVE surface. The
 * compliance engines landed in cd_msp_contract (runbooks + executions,
 * patch policies + updates, SLA credits, on-call rota, maintenance
 * windows, problem & change records), so the former misroutes
 * (console/health/on-call showed other reports) and honest not-built
 * placeholders are gone. Backend: controllers/a02/m05.py SURFACES/REPORTS
 * over cd_msp_contract; the only remaining honest absence is the backup
 * test log (M06/M48 seam).
 *
 * A02 audit P0 (2026-11-03): workflow fields are read-only on every form
 * (the server guards them), phantom fields are gone (M05-13), and the
 * consent code, CAB, window, policy, credit and monthly-report actions have
 * buttons. */

export const MODULE = {
  area: 'A02', code: 'M05', en: 'Remote Support & MSP', title: 'M05 · Remote Support & MSP',
  bn: 'রিমোট সাপোর্ট ও এমএসপি', icon: '🖥️',
  desc: 'Managed IT services — remote sessions, monitored estate, alert-to-ticket, runbooks, patching, SLA credits.',
  kpis: [
    { l: 'Monitored Assets', m: 'monitored_assets' },
    { l: 'Remote Resolution', m: 'remote_resolution', suffix: '%' },
    { l: 'Open MSP Tickets', m: 'open_msp_tickets' },
    { l: 'SLA Credits MTD', m: 'sla_credits_mtd' },
    { l: 'Patch Compliance', m: 'patch_compliance', suffix: '%' },
    { l: 'On-Call Escalations', m: 'oncall_escalations' }
  ],
  groups: [
    { en: 'Remote Sessions', screens: [
      { id: 'M05-sessions', en: 'Remote Sessions', bn: 'রিমোট সেশন', t: 'g' },
      { id: 'M05-console', en: 'Session Console', bn: 'সেশন কনসোল', t: 'g' }
    ]},
    { en: 'Monitored Estate', screens: [
      { id: 'M05-estate', en: 'Estate & Agents', bn: 'এস্টেট ও এজেন্ট', t: 'g' },
      { id: 'M05-health', en: 'Health Scoring', bn: 'হেলথ স্কোরিং', t: 'r' },
      { id: 'M05-alerts', en: 'Alert Rules & Inbox', bn: 'অ্যালার্ট ইনবক্স', t: 'g' },
      { id: 'M05-alert-rules', en: 'Alert Rules', bn: 'অ্যালার্ট নিয়ম', t: 'g' },
      { id: 'M05-backups', en: 'Backup Jobs', bn: 'ব্যাকআপ জব', t: 'g' }
    ]},
    { en: 'Service Desk', screens: [
      { id: 'M05-tickets', en: 'MSP Tickets', bn: 'এমএসপি টিকেট', t: 'g' },
      { id: 'M05-oncall', en: 'On-Call Rota', bn: 'অন-কল রোটা', t: 'g' },
      { id: 'M05-runbooks', en: 'Runbooks & Auto-Remediation', bn: 'রানবুক ও অটো-রিমিডিয়েশন', t: 'g' },
      { id: 'M05-runbook-runs', en: 'Runbook Executions', bn: 'রানবুক সম্পাদন', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M05-patching', en: 'Patch Management', bn: 'প্যাচ ব্যবস্থাপনা', t: 'g' },
      { id: 'M05-msp-patch-policy', en: 'Patch Policies', bn: 'প্যাচ পলিসি', t: 'g' },
      { id: 'M05-windows', en: 'Maintenance Windows', bn: 'মেইনটেন্যান্স উইন্ডো', t: 'g' },
      { id: 'M05-problem', en: 'Problem & Change', bn: 'সমস্যা ও পরিবর্তন', t: 'g' }
    ]},
    { en: 'Client Reporting', screens: [
      { id: 'M05-sla', en: 'SLA Attainment', bn: 'এসএলএ অর্জন', t: 'r' },
      { id: 'M05-reviews', en: 'Client Service Reviews', bn: 'ক্লায়েন্ট সার্ভিস রিভিউ', t: 'g' },
      { id: 'M05-contracts', en: 'MSP Contracts & Monthly Reports', bn: 'এমএসপি চুক্তি ও মাসিক প্রতিবেদন', t: 'g' },
      { id: 'M05-credits', en: 'SLA Credits', bn: 'এসএলএ ক্রেডিট', t: 'g' }
    ]}
  ],
  reports: ['MSP SLA Attainment by Client', 'Remote Resolution Rate', 'Patch Compliance Report', 'Alert-to-Ticket Conversion', 'Backup & Restore Test Log', 'SLA Credit Register'],
  /* M05 capture audit 2026-11-13: every chip that has a form is listed, so
   * each sub-module page names the forms that capture its records */
  forms: ['MSP Contract', 'Remote Session (consent recorded)', 'MSP Ticket', 'Change Record', 'Maintenance Window',
    'Managed Estate Device', 'Health Reading', 'Alert Rule', 'On-Call Shift', 'Runbook', 'Patch Update',
    'Monthly Service Report', 'Runbook Execution', 'Backup Job'],
  cross: ['M08 contract entitlement', 'M17 monitored assets', 'M48 telemetry streams', 'M20 SLA credit billing', 'P04 client portal'],
  freg: {
    src: 93,
    sub: [
      ['1', 'Remote Sessions', 10, { model: 'fix.remote.session', cols: ['msp_contract_id', 'asset_id', 'technician_id', 'tool', 'started_at'], screens: ['M05-sessions', 'M05-console'], reports: ['Remote Resolution Rate'], forms: ['Remote Session (consent recorded)'] }],
      ['2', 'Monitored Estate', 12, { model: 'fix.monitored.asset', cols: ['hostname', 'agent_id', 'msp_contract_id', 'health', 'last_seen'], screens: ['M05-estate'], reports: [], forms: ['Managed Estate Device'] }],
      /* 3 FR-RMS-010/011: an engineer's reading of an asset (an agentless
       * device or a site check) - the health score is computed from it. The
       * page had no button: the metrics were written by the collector only. */
      ['3', 'Metrics & Health Scoring', 9, { model: 'fix.monitored.asset', cols: ['hostname', 'health_score', 'cpu_utilization_pct', 'ram_utilization_pct', 'disk_free_gb'], screens: ['M05-health', 'M05-estate', 'M05-backups'], reports: ['Backup & Restore Test Log'], forms: ['Health Reading', 'Backup Job'], create: 'M05-form-reading' }],
      /* 4 FR-RMS-015: the engine is configured by its rules; alerts are
       * raised by readings that cross them. The button opened the ticket form. */
      ['4', 'Alerting Engine', 11, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'severity', 'rule_id', 'state', 'create_date'], screens: ['M05-alerts', 'M05-alert-rules'], reports: ['Alert-to-Ticket Conversion'], forms: ['Alert Rule', 'MSP Ticket'], create: 'M05-form-alert-rule' }],
      ['5', 'On-Call & Escalation', 7, { model: 'fix.msp.oncall.shift', cols: ['name', 'technician_id', 'level', 'start_at', 'state'], screens: ['M05-oncall'], reports: [], forms: ['On-Call Shift'] }],
      ['6', 'Runbooks & Remediation', 8, { model: 'fix.msp.runbook', cols: ['name', 'trigger', 'scope_contract_id', 'auto_run', 'auto_resolve_alert'], screens: ['M05-runbooks', 'M05-runbook-runs'], reports: [], forms: ['Runbook', 'Runbook Execution'] }],
      ['7', 'Patch Management', 9, { model: 'fix.msp.patch.update', cols: ['identifier', 'title', 'asset_id', 'severity', 'state'], screens: ['M05-patching', 'M05-msp-patch-policy', 'M05-windows'], reports: ['Patch Compliance Report'], forms: ['Patch Update', 'Maintenance Window'] }],
      /* 8 FR-RMS-026: a client reports by phone, email, portal or chat; the
       * desk lists those and every ticketed alert. Its list refused "+ New",
       * so the page had no button and a phoned-in fault had no input. */
      ['8', 'MSP Service Desk', 13, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'source', 'order_id', 'state', 'escalated'], screens: ['M05-tickets', 'M05-problem'], reports: ['Alert-to-Ticket Conversion'], forms: ['MSP Ticket', 'Change Record'], create: 'M05-form-ticket', domain: ['|', ['state', 'in', ['ticketed', 'resolved']], ['source', '!=', 'monitoring']] }],
      /* 9 FR-RMS-035: the monthly report is generated from its contract,
       * never typed - its figures decide the SLA credit. No button before. */
      ['9', 'Client Reporting', 9, { model: 'fix.msp.service.report', cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'sla_attainment_pct'], screens: ['M05-reviews', 'M05-sla'], reports: ['MSP SLA Attainment by Client', 'SLA Credit Register'], forms: ['Monthly Service Report'], create: 'M05-form-monthly-report' }],
      ['10', 'Onboarding Projects', 5, { model: 'fix.msp.contract', cols: ['name', 'contract_id', 'device_count', 'monitoring_scope', 'sla_target_pct'], screens: ['M05-contracts', 'M05-estate'], reports: ['MSP SLA Attainment by Client'], forms: ['MSP Contract'] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted MSP models — every one
 * of the 13 registry screens is a live surface now. */
export const SCREENS = {
  /* --- Remote Sessions --- */
  'M05-sessions': { kind: 'model_list', model: 'fix.remote.session',
    cols: ['msp_contract_id', 'asset_id', 'technician_id', 'tool', 'consent_captured', 'consent_token_ref', 'started', 'started_at', 'ended_at'],
    stateField: 'tool',
    actions: [
      { m: 'action_request_consent', l: 'Request Consent' },
      { m: 'action_verify_consent', l: 'Verify Consent', ask: "Consent code the client read back", kwarg: 'code' },
      { m: 'action_start', l: 'Start Session' },
      { m: 'action_end', l: 'End Session', ask: 'Session recording reference', kwarg: 'recording_url' }
    ] },
  /* the console = what is RUNNING right now (started, not yet ended) */
  'M05-console': { kind: 'model_list', model: 'fix.remote.session', create: false,
    empty: 'No remote session is running. Open one on Remote Sessions: request and verify the client\u2019s consent, then Start Session.',
    cols: ['started_at', 'msp_contract_id', 'asset_id', 'technician_id', 'tool', 'consent_captured'],
    domain: [['started', '=', true], ['ended_at', '=', false]],
    actions: [{ m: 'action_end', l: 'End Session', ask: 'Session recording reference', kwarg: 'recording_url' }] },

  /* --- Monitored Estate --- */
  'M05-estate': { kind: 'model_list', model: 'fix.monitored.asset', create: true,
    cols: ['agent_id', 'hostname', 'msp_contract_id', 'device_id', 'health', 'health_score', 'open_alert_count', 'last_seen'],
    stateField: 'health' },
  'M05-health': { kind: 'table_report', module: 'M05', report: 'estate_health', period: false },
  'M05-alerts': { kind: 'model_list', model: 'fix.msp.alert', create: true,
    cols: ['msp_contract_id', 'asset_id', 'severity', 'message', 'source', 'rule_id', 'coverage_gap', 'state', 'escalated', 'order_id', 'resolved_at'],
    stateField: 'state',
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge' },
      { m: 'action_to_ticket', l: 'Create Ticket' },
      { m: 'action_resolve', l: 'Resolve', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_escalate', l: 'Escalate' }
    ] },
  /* FR-RMS-015: a threshold per metric; scoped to one contract or, empty,
   * to every contract's estate. Evaluated on every health reading. */
  'M05-alert-rules': { kind: 'model_list', model: 'fix.msp.alert.rule',
    cols: ['name', 'msp_contract_id', 'metric', 'operator', 'threshold', 'severity', 'active', 'alert_count'],
    empty: 'No alert rule yet. Define one with + New Alert Rule: a reading that crosses its threshold raises an alert on the asset.' },

  /* --- Service Desk ---
   * the desk = what clients reported (phone, email, portal, chat) and every
   * alert that became a ticket. "+ New" logs a client's report. */
  'M05-tickets': { kind: 'model_list', model: 'fix.msp.alert',
    cols: ['asset_id', 'severity', 'message', 'source', 'order_id', 'state', 'escalated', 'resolved_at', 'resolution_note'],
    stateField: 'state',
    domain: ['|', ['state', 'in', ['ticketed', 'resolved']], ['source', '!=', 'monitoring']],
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge' },
      { m: 'action_to_ticket', l: 'Create Service Order' },
      { m: 'action_resolve', l: 'Resolve', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_escalate', l: 'Escalate' }
    ] },
  'M05-oncall': { kind: 'model_list', model: 'fix.msp.oncall.shift',
    cols: ['name', 'technician_id', 'level', 'start_at', 'end_at', 'state'],
    stateField: 'state',
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_close', l: 'Close' }
    ] },
  'M05-runbooks': { kind: 'model_list', model: 'fix.msp.runbook',
    cols: ['name', 'trigger', 'scope_contract_id', 'auto_run', 'auto_resolve_alert', 'run_count', 'last_run_at'],
    stateField: 'trigger',
    /* a quick log names the asset; an execution with its evidence and
     * outcome (a failure too) is logged on + Log Runbook Execution */
    actions: [
      { m: 'action_execute', l: 'Log Successful Execution', ask: 'Asset the steps were run on (agent ID or hostname)', kwarg: 'asset' }
    ] },
  /* spec T-08: every execution with its target, outcome and output */
  'M05-runbook-runs': { kind: 'model_list', model: 'fix.msp.runbook.run',
    cols: ['started_at', 'runbook_id', 'asset_id', 'alert_id', 'outcome', 'output_note', 'logged_by_id'],
    stateField: 'outcome',
    empty: 'No runbook execution logged yet. Log one with + Log Runbook Execution after running the steps.' },
  /* FR-RMS-039: backup job outcomes and restore tests per asset */
  'M05-backups': { kind: 'model_list', model: 'fix.msp.backup.job',
    cols: ['run_at', 'msp_contract_id', 'asset_id', 'plan_ref', 'outcome', 'restore_tested', 'consecutive_failures', 'alert_id'],
    stateField: 'outcome',
    empty: 'No backup job recorded yet. Record each job with + Record a Backup Job; a failed job raises an alert on its asset.' },

  /* --- Compliance --- */
  'M05-patching': { kind: 'model_list', model: 'fix.msp.patch.update',
    cols: ['msp_contract_id', 'asset_id', 'identifier', 'title', 'category', 'severity', 'state', 'installed_at'],
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_record_test', l: 'Record Pre-Deployment Test', ask: 'Test evidence (pilot ring, result)', kwarg: 'note' },
      { m: 'action_request_window_exception', l: 'Request Exception: Outside Window', ask: 'Why it cannot wait for an approved window', kwarg: 'reason' },
      { m: 'action_request_test_exception', l: 'Request Exception: Skip Test', ask: 'Why it cannot wait for a test', kwarg: 'reason' },
      { m: 'action_recall_approval', l: 'Recall Exception Request' },
      { m: 'action_install', l: 'Mark Installed' },
      { m: 'action_defer', l: 'Defer 7 Days' },
      { m: 'action_fail', l: 'Mark Failed', ask: 'Failure note', kwarg: 'note' }
    ] },
  /* a window opens and closes on its own once approved (its state follows
   * the approval and the time range); Close Window ends it early */
  'M05-windows': { kind: 'model_list', model: 'fix.msp.maintenance.window',
    cols: ['name', 'msp_contract_id', 'purpose', 'start_at', 'end_at', 'suppress_alerts', 'approved_by_id', 'state'],
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve Window (CAB)' },
      { m: 'action_close', l: 'Close Window' }
    ] },
  'M05-problem': { kind: 'model_list', model: 'fix.msp.change.record',
    cols: ['name', 'kind', 'change_type', 'risk', 'msp_contract_id', 'requested_by', 'cab_approver_id', 'maintenance_window_id', 'state'],
    stateField: 'state',
    actions: [
      /* A02 audit B1: the CAB (emergency: the change manager) decides in the M63 inbox */
      { m: 'action_request_approval', l: 'Request CAB Approval', ask: 'Note for the CAB (optional)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reject', l: 'Reject', ask: 'Rejection reason', kwarg: 'note' },
      { m: 'action_implement', l: 'Mark Implemented', ask: 'Implementation note', kwarg: 'note' },
      { m: 'action_record_review', l: 'Record Post-Implementation Review', ask: 'Review: what was done, outcome, follow-ups', kwarg: 'note' },
      { m: 'action_close', l: 'Close', ask: 'Closing note', kwarg: 'note' }
    ] },

  /* --- Client Reporting --- */
  'M05-sla': { kind: 'table_report', module: 'M05', report: 'sla_by_client', title: 'MSP SLA Attainment by Client', period: false },
  'M05-reviews': { kind: 'model_list', model: 'fix.msp.service.report', create: false,
    cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'breached_count', 'pending_count', 'sla_attainment_pct', 'attainment_flagged', 'summary_en', 'summary_bn'],
    actions: [{ m: 'action_generate_bilingual_report', l: 'Regenerate Summary' }] },
  /* the monthly report and the SLA credit run, per MSP contract */
  'M05-contracts': { kind: 'model_list', model: 'fix.msp.contract',
    cols: ['name', 'contract_id', 'contract_state', 'entitled', 'device_count', 'monitoring_scope', 'sla_target_pct', 'monthly_value'],
    actions: [
      { m: 'action_generate_monthly_report', l: 'Generate Monthly Report' },
      { m: 'action_compute_sla_credits', l: 'Compute SLA Credits' }
    ] },
  /* credits are computed from the service report; a manual credit is typed
   * on the credit form and needs the DOFA tier of its amount */
  'M05-credits': { kind: 'model_list', model: 'fix.msp.sla.credit', create: true,
    cols: ['msp_contract_id', 'period_label', 'attainment_pct', 'target_pct', 'computed_amount', 'manual_amount', 'credit_amount', 'approved_by_id', 'state'],
    stateField: 'state',
    actions: [
      /* A02 audit B1: credit approvers (manual credit: DOFA Tier 4) decide in the M63 inbox */
      { m: 'action_request_approval', l: 'Request Credit Approval', ask: 'Justification (required for a manual credit)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_apply', l: 'Apply to Billing' }
    ] },

  /* ============ SIX REGISTRY REPORT SCREENS (v2 forensic audit) =============
   * Every report chip opens its OWN titled computed report. Previously four of
   * the six routed to OPERATIONAL screens (console / patching / alerts /
   * windows), so the chip and the heading disagreed and the "report" was a
   * worklist rather than the computed report. */
  'M05-rpt-resolution': { kind: 'table_report', module: 'M05', report: 'remote_resolution', title: 'Remote Resolution Rate', period: true },
  'M05-rpt-patch': { kind: 'table_report', module: 'M05', report: 'patch_compliance', title: 'Patch Compliance Report', period: false },
  'M05-rpt-alertconv': { kind: 'table_report', module: 'M05', report: 'alert_conversion', title: 'Alert-to-Ticket Conversion', period: true },
  'M05-rpt-backup': { kind: 'table_report', module: 'M05', report: 'backup_log', title: 'Backup & Restore Test Log', period: true },
  'M05-rpt-credits': { kind: 'table_report', module: 'M05', report: 'sla_credit_register', title: 'SLA Credit Register', period: true },

  /* ============ THE FOUR REGISTRY FORMS as D365 model_forms (v2) ==========
   * The chips previously opened stock Odoo dialogs. */
  'M05-form-session': { kind: 'model_form', model: 'fix.remote.session',
    title: 'Remote Session', back: 'M05-sessions',
    tabs: [
      { id: 'session', label: '1. Session Identity', bn: '১. সেশন তথ্য', icon: '🖥️', badge: '7' },
      { id: 'consent', label: '2. Consent & Recording', bn: '২. সম্মতি ও অডিট', icon: '🔒', badge: '11' }
    ],
    sections: [
      { tab: 'session', title: 'Remote Support Session Scope & Asset', fields: [
        { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
        { name: 'asset_id', required: true, label: 'Monitored Asset' },
        { name: 'technician_id', required: true, label: 'Technician' },
        { name: 'tool', required: true, label: 'Remote Access Tool' },
        { name: 'session_protocol', label: 'Transport Encryption' },
        { name: 'order_id', label: 'Service Order (the ticket worked on)' },
        { name: 'started', label: 'Session Active', readonly: true },
      ]},
      { tab: 'consent', title: 'Customer Explicit Consent & Session Log',
        note: 'A remote session strictly requires customer consent recording prior to opening remote desktop tunnels.',
        fields: [
          { name: 'consent_partner_id', label: 'Consenting Client Contact (receives the code)' },
          { name: 'consent_requested_at', label: 'Consent Code Sent At', readonly: true },
          { name: 'consent_expires_at', label: 'Consent Code Expires At', readonly: true },
          { name: 'consent_captured', label: 'Customer Explicit Consent Captured', readonly: true },
          { name: 'consent_verified_by_id', label: 'Consent Code Entered By', readonly: true },
          { name: 'consent_token_ref', label: 'Consent Token Reference', readonly: true },
          { name: 'consent_captured_at', label: 'Consent Captured At', readonly: true },
          { name: 'started_at', label: 'Session Started At', readonly: true },
          { name: 'ended_at', label: 'Session Ended At', readonly: true },
          { name: 'recording_url', label: 'Session Recording Reference', readonly: true },
          { name: 'session_summary', label: 'Session Actions / Troubleshooting Summary', type: 'text' }
        ]},
    ] },

  'M05-form-ticket': { kind: 'model_form', model: 'fix.msp.alert',
    title: 'MSP Ticket', newLabel: 'Log a Client Ticket', back: 'M05-tickets',
    status: { field: 'state' },
    tabs: [
      { id: 'alert', label: '1. Report & Asset', bn: '১. অভিযোগ ও সম্পদ', icon: '🚨', badge: '7' },
      { id: 'resolution', label: '2. SLA Resolution & Ticket', bn: '২. সমাধান ও টিকেট', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'alert', title: 'What the Client Reported, and on Which Asset',
        note: 'Choose how the client reported it and an asset of their contract. Create Service Order on MSP Tickets turns it into the job; the SLA clock runs from now.',
        fields: [
        { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
        { name: 'asset_id', required: true, label: 'Monitored Asset' },
        /* a ticket logged here is a client's report: it starts as a phone
         * call, never as "Monitoring" (that would hide it from the desk) */
        { name: 'source', required: true, value: 'phone', label: 'Reported Through' },
        { name: 'severity', required: true, label: 'Severity' },
        { name: 'message', required: true, label: 'What the Client Reported' },
        { name: 'rule_id', label: 'Raised by Alert Rule', readonly: true },
        { name: 'escalated', label: 'Escalated to On-Call Rota', readonly: true },
        { name: 'escalated_at', label: 'Escalated At', readonly: true },
        { name: 'coverage_gap', label: 'Coverage Gap (no agent report for 24 h)', readonly: true },
      ]},
      { tab: 'resolution', title: 'Ticket Conversion & Resolution Verification', fields: [
        { name: 'order_id', label: 'Commercial Service Order (M01)', readonly: true },
        { name: 'state', label: 'Ticket / Alert State', readonly: true },
        { name: 'resolved_at', label: 'Resolved Timestamp', readonly: true },
        { name: 'resolution_note', label: 'Root Cause & Resolution Summary', type: 'text', readonly: true }
      ]},
    ] },

  'M05-form-change': { kind: 'model_form', model: 'fix.msp.change.record',
    title: 'Change Record', back: 'M05-problem',
    status: { field: 'state' },
    tabs: [
      { id: 'change', label: '1. Change Request', bn: '১. পরিবর্তনের বিবরণ', icon: '🔄', badge: '9' },
      { id: 'approval', label: '2. Risk & CAB Sign-Off', bn: '২. ঝুঁকি ও সিএবি অনুমোদন', icon: '✍️', badge: '12' }
    ],
    sections: [
      { tab: 'change', title: 'ITIL Change Classification & Asset Target', fields: [
        { name: 'name', required: true, label: 'Change Title' },
        { name: 'msp_contract_id', label: 'MSP Contract' },
        { name: 'asset_id', label: 'Target Asset / Service' },
        { name: 'kind', required: true, label: 'Record Kind (Problem / Change)' },
        { name: 'change_type', required: true, label: 'Change Type (Standard/Normal/Emergency)' },
        { name: 'emergency', label: 'Emergency Path (change manager approves)', readonly: true },
        { name: 'requested_by', label: 'Requested By Engineer' },
        { name: 'maintenance_window_id', label: 'Approved Maintenance Window' },
        { name: 'state', label: 'Change Lifecycle State', readonly: true }
      ]},
      { tab: 'approval', title: 'Risk Assessment, CAB Approval & Rollback Plan',
        note: 'Every change needs a rollback plan before CAB approval (BRU-RMS-08); a problem record does not. A normal change is implemented only inside its approved, open window; an emergency change needs a post-implementation review before close.',
        fields: [
        { name: 'risk', required: true, label: 'Risk Rating (Low/Medium/High)' },
        { name: 'description', label: 'Scope of Change & Implementation Plan', type: 'text' },
        { name: 'rollback_plan', label: 'Backout & Rollback Plan', type: 'text' },
        { name: 'cab_approver_id', label: 'CAB Approving Authority', readonly: true },
        { name: 'approved_at', label: 'Approved At', readonly: true },
        { name: 'implemented_by_id', label: 'Implemented By', readonly: true },
        { name: 'implemented_at', label: 'Implementation Completed At', readonly: true },
        { name: 'resolution_note', label: 'Implementation / Closing Note', type: 'text', readonly: true },
        { name: 'pir_note', label: 'Post-Implementation Review', type: 'text', readonly: true },
        { name: 'pir_by_id', label: 'Reviewed By', readonly: true },
        { name: 'pir_at', label: 'Reviewed At', readonly: true },
        { name: 'approval_state', label: 'Approval (M63 inbox)', readonly: true },
        { name: 'approval_request_id', label: 'Approval Request', readonly: true }
      ]},
    ] },

  'M05-form-window': { kind: 'model_form', model: 'fix.msp.maintenance.window',
    title: 'Maintenance Window', back: 'M05-windows',
    status: { field: 'state' },
    tabs: [
      { id: 'window', label: '1. Window Scope', bn: '১. সময়কাল ও পরিধি', icon: '🕒', badge: '5' },
      { id: 'governance', label: '2. SLA Alert Suppression', bn: '২. এসএলএ সতর্কতা নিয়ন্ত্রণ', icon: '🛡️', badge: '4' }
    ],
    sections: [
      { tab: 'window', title: 'Scheduled Window Timing', fields: [
        { name: 'name', required: true, label: 'Window Reference' },
        { name: 'msp_contract_id', label: 'MSP Contract' },
        { name: 'start_at', required: true, label: 'Scheduled Start' },
        { name: 'end_at', required: true, label: 'Scheduled End' },
        { name: 'state', label: 'Window State', readonly: true }
      ]},
      { tab: 'governance', title: 'Alert Suppression & Impact Analysis', fields: [
        { name: 'purpose', label: 'Maintenance Objective & Work Items', type: 'text' },
        { name: 'suppress_alerts', label: 'Suppress Automated Outage Alerts' },
        { name: 'approved_by_id', label: 'Approved By (CAB / Change Manager)', readonly: true },
        { name: 'approved_at', label: 'Approved At', readonly: true },
        { name: 'closed_by_id', label: 'Closed Early By', readonly: true },
        { name: 'closed_at', label: 'Closed At', readonly: true }
      ]},
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M05-form-estate': {
    kind: 'model_form',
    model: 'fix.monitored.asset',
    title: "Managed Estate Device",
    back: 'M05-estate',
    tabs: [
      { id: 'asset', label: '1. Device Identity', bn: '১. ডিভাইসের পরিচিতি', icon: '💻', badge: '9' },
      { id: 'telemetry', label: '2. Telemetry & Agent Health', bn: '২. এজেন্ট স্থিতি ও অডিট', icon: '📊', badge: '3' }
    ],
    sections: [
      { tab: 'asset', title: "Managed Estate Device Inventory", note: "One endpoint under the MSP contract: its monitoring agent, network identity and the registered device a ticket is raised on.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'msp_contract_id', required: true, label: "MSP Contract" },
          { name: 'agent_id', required: true, label: "RMM Agent Identifier" },
          { name: 'hostname', label: "Device Hostname / FQDN" },
          { name: 'device_id', label: "Registered Hardware Asset" },
          { name: 'health', required: true, label: "Health Status" },
          /* FR-RMS-008: the endpoint's network and OS identity (the model
           * had the fields; no form showed them) */
          { name: 'ip_address', label: "IP Address" },
          { name: 'mac_address', label: "MAC Address" },
          { name: 'os_version', label: "Operating System & Build" }
        ] },
      { tab: 'telemetry', title: "Heartbeat & Composite Health Scoring",
        fields: [
          { name: 'health_score', label: "Composite Health Score (0-100)", readonly: true },
          { name: 'open_alert_count', label: "Active Unresolved Alerts", readonly: true },
          { name: 'last_seen', label: "Agent Last Heartbeat Timestamp", readonly: true }
        ] }
    ]
  },
  'M05-form-oncall': {
    kind: 'model_form',
    model: 'fix.msp.oncall.shift',
    title: "On-Call Shift",
    back: 'M05-oncall',
    tabs: [
      { id: 'shift', label: '1. Rota Assignment', bn: '১. রোটা শিফট', icon: '📞', badge: '4' },
      { id: 'escalation', label: '2. Timing & Handover', bn: '২. সময় ও হস্তান্তর', icon: '⏱️', badge: '3' }
    ],
    sections: [
      { tab: 'shift', title: "24/7 On-Call Support Rota", note: "An on-call rota entry; SLA escalation routes automatically to the active shift holder.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Shift Code / Reference" },
          { name: 'technician_id', required: true, label: "On-Call Engineer" },
          { name: 'level', required: true, label: "Escalation Tier (Primary/Secondary/Manager)" }
        ] },
      { tab: 'escalation', title: "Shift Active Window & Handover Notes",
        fields: [
          { name: 'start_at', required: true, label: "Shift Start At" },
          { name: 'end_at', required: true, label: "Shift End At" },
          { name: 'state', label: "Shift State", readonly: true }
        ] }
    ]
  },
  'M05-form-runbook': {
    kind: 'model_form',
    model: 'fix.msp.runbook',
    title: "Runbook",
    back: 'M05-runbooks',
    tabs: [
      { id: 'spec', label: '1. Remediation Script', bn: '১. রিমিডিয়েশন নির্দেশিকা', icon: '📜', badge: '5' },
      { id: 'automation', label: '2. Automated Triggers', bn: '২. অটোমেশন ও পরিসর', icon: '⚙️', badge: '5' }
    ],
    sections: [
      { tab: 'spec', title: "Standard Operating Procedure / Runbook", note: "A governed runbook: the steps an engineer or automated agent follows for a service event.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Runbook Title" },
          { name: 'trigger', required: true, label: "Event Trigger Pattern" },
          { name: 'script', required: true, type: 'text', label: "Executable Remediation Steps" },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'automation', title: "Contract Scope & Autonomous Execution",
        fields: [
          { name: 'scope_contract_id', label: "Scoped to Specific Client / Contract" },
          { name: 'auto_run', label: "Autonomous AI / Script Execution Enabled" },
          { name: 'auto_resolve_alert', label: "Auto-Resolve Alert on Success" },
          { name: 'run_count', label: "Total Executions", readonly: true },
          { name: 'last_run_at', label: "Last Run Timestamp", readonly: true }
        ] }
    ]
  },
  'M05-form-patch': {
    kind: 'model_form',
    model: 'fix.msp.patch.update',
    title: "Patch Update",
    back: 'M05-patching',
    tabs: [
      { id: 'patch', label: '1. Security Advisory', bn: '১. প্যাচ ও নিরাপত্তা', icon: '🛡️', badge: '5' },
      { id: 'deployment', label: '2. Deployment & Compliance', bn: '২. ইনস্টলেশন ও স্থিতি', icon: '📦', badge: '13' }
    ],
    sections: [
      { tab: 'patch', title: "CVE / Vendor Security Patch Advisory", note: "A patch obligation per monitored asset: target version, window, and compliance proof.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'msp_contract_id', required: true, label: "MSP Contract" },
          { name: 'asset_id', required: true, label: "Target Managed Asset" },
          { name: 'identifier', label: "KB / CVE Bulletin Identifier" },
          { name: 'title', required: true, label: "Patch Advisory Title" }
        ] },
      { tab: 'deployment', title: "Patch Deployment State & Verification",
        fields: [
          { name: 'severity', required: true, label: "Vulnerability Severity" },
          { name: 'category', required: true, label: "Patch Category (OS / App / Firmware)" },
          { name: 'state', label: "Deployment State", readonly: true },
          { name: 'approved_by_id', label: "Approved By", readonly: true },
          { name: 'approved_date', label: "Approved On", readonly: true },
          { name: 'auto_approved_policy_id', label: "Auto-Approved By Policy", readonly: true },
          { name: 'deferred_until', label: "Deferred Until", readonly: true },
          { name: 'tested_by_id', label: "Tested By", readonly: true },
          { name: 'installed_at', label: "Installation Verified At", readonly: true },
          { name: 'fail_note', label: "Failure Note", readonly: true },
          { name: 'tested_at', label: "Pre-Deployment Test Passed At", readonly: true },
          { name: 'test_note', label: "Test Evidence", readonly: true },
          { name: 'exception_kind', label: "Install Exception", readonly: true },
          { name: 'exception_reason', label: "Exception Justification", type: 'text', readonly: true },
          { name: 'approval_state', label: "Exception Approval (M63 inbox)", readonly: true },
          { name: 'exception_approved_by_id', label: "Exception Approved By", readonly: true }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M05-msp-patch-policy': { kind: 'model_list', model: 'fix.msp.patch.policy',
    cols: ['name', 'active', 'company_id', 'operating_unit_id', 'msp_contract_id', 'category', 'auto_approve', 'approved_by_id', 'approved_by_cab'],
    actions: [{ m: 'action_approve', l: 'Approve Policy (CAB / Change Manager)' }] },

  /* The module's anchor record had no in-workspace form: "+ MSP Contract"
   * opened the stock Odoo form in a dialog, the one surface in M05 that left
   * the shell (M05 has forms for eight other records). Found 2026-11-12 from
   * the sub-module pages, whose create button is this one. */
  'M05-form-msp-contract': {
    kind: 'model_form',
    model: 'fix.msp.contract',
    title: "MSP Contract",
    back: 'M05-contracts',
    lines: { field: 'asset_ids', title: 'Monitored Assets', readonlyGrid: true,
      note: 'Assets are enrolled on the Managed Estate screen; this is the estate the contract covers.',
      fields: [
        { name: 'agent_id', label: 'RMM Agent', readonly: true },
        { name: 'hostname', label: 'Hostname', readonly: true },
        { name: 'device_id', label: 'Device', readonly: true },
        { name: 'health', label: 'Health', readonly: true },
        { name: 'last_seen', label: 'Last Seen', readonly: true },
      ] },
    tabs: [
      { id: 'contract', label: '1. Contract & Scope', bn: '১. চুক্তি ও পরিধি', icon: '📑', badge: '6' },
      { id: 'commercial', label: '2. Commercials & SLA', bn: '২. মূল্য ও এসএলএ', icon: '💰', badge: '5' }
    ],
    sections: [
      { tab: 'contract', title: "Contract & Monitoring Scope",
        note: "An MSP contract hangs off an M08 contract: monitoring, patching and remote work are entitled only while that contract is in force.",
        fields: [
          { name: 'name', required: true, label: "MSP Contract" },
          { name: 'contract_id', required: true, label: "Contract (M08)" },
          { name: 'contract_state', label: "M08 Contract State", readonly: true },
          { name: 'entitled', label: "Entitled Today", readonly: true },
          { name: 'monitoring_scope', required: true, label: "Monitoring Scope" },
          { name: 'device_count', label: "Covered Devices" }
        ] },
      { tab: 'commercial', title: "Commercials & Service Levels",
        note: "The monthly value is the covered devices times the per-device price; the SLA credit of a month can never exceed it.",
        fields: [
          { name: 'per_device_monthly', label: "Per-Device Monthly (BDT)" },
          { name: 'monthly_value', label: "Monthly Value (BDT)", readonly: true },
          { name: 'sla_target_pct', label: "SLA Target %" },
          { name: 'alert_resolve_hours_major', label: "Major Alert Resolution Target (h)" },
          { name: 'alert_resolve_hours_minor', label: "Minor Alert Resolution Target (h)" }
        ] }
    ] },

  'M05-form-credit': {
    kind: 'model_form',
    model: 'fix.msp.sla.credit',
    title: "SLA Credit",
    back: 'M05-credits',
    status: { field: 'state' },
    tabs: [
      { id: 'credit', label: '1. Credit', bn: '১. ক্রেডিট', icon: '💳', badge: '6' },
      { id: 'approval', label: '2. Computation & Approval', bn: '২. হিসাব ও অনুমোদন', icon: '✍️', badge: '11' }
    ],
    sections: [
      { tab: 'credit', title: "SLA Credit", note: "Credits are computed from the monthly service report. A manual credit or override is typed here and needs the DOFA tier of its amount (BRU-RMS-06: CFO) with a written justification; it cannot exceed the monthly value.",
        fields: [
          { name: 'msp_contract_id', required: true, label: "MSP Contract" },
          { name: 'period_label', required: true, label: "Period" },
          { name: 'manual_amount', label: "Manual Credit / Override (BDT)" },
          { name: 'reason', label: "Reason" },
          { name: 'dofa_justification', label: "DOFA Justification (manual credits)", type: 'text' },
          { name: 'state', label: "State", readonly: true }
        ] },
      { tab: 'approval', title: "Computed Amount & Approval",
        fields: [
          { name: 'service_report_id', label: "Service Report", readonly: true },
          { name: 'attainment_pct', label: "Attainment %", readonly: true },
          { name: 'target_pct', label: "Target %", readonly: true },
          { name: 'computed_amount', label: "Computed Credit (BDT)", readonly: true },
          { name: 'credit_amount', label: "Credit Amount (BDT)", readonly: true },
          { name: 'dofa_tier_required', label: "DOFA Tier Required", readonly: true },
          { name: 'is_manual', label: "Manual Credit / Override", readonly: true },
          { name: 'breach_count', label: "SLA Breaches in the Month", readonly: true },
          { name: 'approved_by_id', label: "Approved By", readonly: true },
          { name: 'approved_at', label: "Approved At", readonly: true },
          { name: 'approved_amount', label: "Amount Approved (BDT)", readonly: true },
          { name: 'approval_state', label: "Approval (M63 inbox)", readonly: true },
          { name: 'approval_request_id', label: "Approval Request", readonly: true },
          { name: 'applied_at', label: "Applied to Billing At", readonly: true },
          { name: 'applied_by_id', label: "Applied By", readonly: true }
        ] }
    ]
  },

  /* ===== M05 capture audit 2026-11-13: a capture per sub-module ===== */

  /* 3 Metrics & Health Scoring. The reading runs through the same alerting
   * as the collector (action_record_reading): first unhealthy transition,
   * then every alert rule in scope; nothing while a window is open. The
   * metrics are inputs here only: the generic write refuses them. */
  'M05-form-reading': {
    kind: 'model_form',
    model: 'fix.monitored.asset',
    title: 'Health Reading',
    newLabel: 'Record a Health Reading',
    back: 'M05-estate',
    pickRecord: {
      label: 'Step 1 of 2: choose the asset you read',
      note: 'Every asset of the monitored estate. Use this for devices without an agent (network gear, printers) and for site checks; agents report on their own.',
      search: 'Search asset',
      choose: 'Read this asset',
      cols: ['hostname', 'agent_id', 'msp_contract_id', 'health', 'health_score', 'last_seen'],
      domain: [],
      empty: 'No monitored asset yet. Enrol one on Estate & Agents first.'
    },
    saveAction: {
      method: 'action_record_reading', label: 'Record Reading',
      done: 'Reading recorded. No threshold crossed.',
      kwargs: { health: 'health', cpu: 'cpu_utilization_pct', ram: 'ram_utilization_pct', disk_free_gb: 'disk_free_gb', uptime_hours: 'uptime_hours' }
    },
    sections: [
      { title: 'Step 2 of 2: The Reading (FR-RMS-010 / 011)',
        note: 'Needs the MSP Engineer role. Enter what you measured; a blank metric keeps its last value. A reading that crosses an alert rule raises one alert per rule until that alert is resolved.',
        fields: [
          { name: 'hostname', label: 'Asset', readonly: true },
          { name: 'msp_contract_id', label: 'MSP Contract', readonly: true },
          { name: 'last_seen', label: 'Last Reading At', readonly: true },
          { name: 'last_reading_by_id', label: 'Last Read By (empty: the agent)', readonly: true },
          { name: 'health_score', label: 'Health Score (0-100)', readonly: true },
          /* readonly for the generic write; inputs because saveAction carries them */
          { name: 'health', required: true, label: 'Health Status', readonly: true },
          { name: 'cpu_utilization_pct', label: 'CPU Load (%)', readonly: true },
          { name: 'ram_utilization_pct', label: 'Memory Use (%)', readonly: true },
          { name: 'disk_free_gb', label: 'Free Disk (GB)', readonly: true },
          { name: 'uptime_hours', label: 'Uptime Since Restart (hours)', readonly: true }
        ] }
    ]
  },

  /* 4 Alerting Engine: FR-RMS-015 */
  'M05-form-alert-rule': {
    kind: 'model_form',
    model: 'fix.msp.alert.rule',
    title: 'Alert Rule',
    newLabel: 'Define an Alert Rule',
    back: 'M05-alert-rules',
    tabs: [
      { id: 'rule', label: '1. Threshold', bn: '১. সীমা', icon: '📏', badge: '6' },
      { id: 'scope', label: '2. Scope & History', bn: '২. পরিধি ও ইতিহাস', icon: '🎯', badge: '4' }
    ],
    sections: [
      { tab: 'rule', title: 'The Condition That Raises an Alert',
        note: 'A reading above (or below) the threshold raises an alert of this severity on the asset. Percentages are 0 to 100.',
        fields: [
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'metric', required: true, label: 'Metric' },
          { name: 'operator', required: true, label: 'Raise When the Reading Is' },
          { name: 'threshold', required: true, label: 'Threshold' },
          { name: 'severity', required: true, label: 'Alert Severity' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'scope', title: 'Which Estate It Watches',
        note: 'Leave the contract empty to watch every MSP contract.',
        fields: [
          { name: 'msp_contract_id', label: 'MSP Contract' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'alert_count', label: 'Alerts Raised', readonly: true }
        ] }
    ]
  },

  /* 9 Client Reporting: FR-RMS-035. The report's figures are computed from
   * the period's alerts (they decide the SLA credit), so the capture is
   * choosing the contract; one report per contract and month. */
  'M05-form-monthly-report': {
    kind: 'model_form',
    model: 'fix.msp.contract',
    title: 'Monthly Service Report',
    newLabel: 'Generate a Monthly Service Report',
    back: 'M05-reviews',
    pickRecord: {
      label: 'Step 1 of 2: choose the MSP contract',
      note: 'The report covers last calendar month. A contract whose agreement never came into force has no report.',
      search: 'Search MSP contract',
      choose: 'Report on this contract',
      cols: ['name', 'contract_id', 'contract_state', 'device_count', 'sla_target_pct'],
      domain: [],
      empty: 'No MSP contract yet. Create one with + New MSP Contract.'
    },
    saveAction: {
      method: 'action_generate_monthly_report', label: 'Generate Report',
      done: 'Report generated: see Client Service Reviews', kwargs: {}
    },
    sections: [
      { title: 'Step 2 of 2: Generate Last Month’s Report',
        note: 'Alerts, resolutions within target and the SLA attainment are counted from the period’s alerts, in English and Bengali. Compute SLA Credits on MSP Contracts then drafts any credit the attainment owes.',
        fields: [
          { name: 'name', label: 'MSP Contract', readonly: true },
          { name: 'contract_id', label: 'Contract (M08)', readonly: true },
          { name: 'contract_state', label: 'M08 Contract State', readonly: true },
          { name: 'entitled', label: 'Entitled Today', readonly: true },
          { name: 'sla_target_pct', label: 'SLA Target %', readonly: true }
        ] }
    ]
  },

  /* 6 Runbooks & Remediation: spec T-08. Saved once, then evidence; the
   * server checks the asset is in the runbook's scope, the alert is the
   * asset's, and that a failure (or an alert resolution) says what happened. */
  'M05-form-runbook-run': {
    kind: 'model_form',
    model: 'fix.msp.runbook.run',
    title: 'Runbook Execution',
    newLabel: 'Log Runbook Execution',
    back: 'M05-runbook-runs',
    sections: [
      { title: 'What Was Run, Where, and What Happened',
        note: 'Log the execution after running the steps. A successful run of a runbook set to resolve alerts resolves the asset’s open alert; a failed run never does. Needs the MSP Engineer role.',
        fields: [
          { name: 'runbook_id', required: true, label: 'Runbook' },
          { name: 'asset_id', required: true, label: 'Asset the Steps Were Run On' },
          { name: 'alert_id', label: 'Alert It Answers (optional)' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'output_note', label: 'Evidence: What the Steps Showed' },
          { name: 'started_at', label: 'Logged At', readonly: true },
          { name: 'logged_by_id', label: 'Logged By', readonly: true },
          { name: 'state', label: 'Recorded Result', readonly: true }
        ] }
    ]
  },

  /* 3 Metrics & Health Scoring: FR-RMS-039 backup oversight */
  'M05-form-backup-job': {
    kind: 'model_form',
    model: 'fix.msp.backup.job',
    title: 'Backup Job',
    newLabel: 'Record a Backup Job',
    back: 'M05-backups',
    sections: [
      { title: 'Backup Job Outcome & Restore Test',
        note: 'One job of a backup plan on a client asset. A failed or partial job raises an alert on the asset (one per plan until it is resolved). Saved once; a job is not edited afterwards. Needs the MSP Engineer role.',
        fields: [
          { name: 'asset_id', required: true, label: 'Asset' },
          { name: 'plan_ref', required: true, label: 'Backup Plan / Job' },
          { name: 'run_at', required: true, label: 'Run At' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'restore_tested', label: 'Restore Tested (data read back)' },
          { name: 'note', label: 'Note (what failed, when it did)', type: 'text' },
          { name: 'msp_contract_id', label: 'MSP Contract', readonly: true },
          { name: 'consecutive_failures', label: 'Failures in a Row', readonly: true },
          { name: 'alert_id', label: 'Alert Raised', readonly: true }
        ] }
    ]
  },

  'M05-form-msp-patch-policy': {
    kind: 'model_form',
    model: 'fix.msp.patch.policy',
    title: "Patch Policy",
    back: 'M05-msp-patch-policy',
    tabs: [
      { id: 'policy', label: '1. Policy Scope', bn: '১. পলিসির পরিধি', icon: '📋', badge: '5' },
      { id: 'rules', label: '2. Approval Rules', bn: '২. অনুমোদন নিয়মাবলী', icon: '⚙️', badge: '5' }
    ],
    sections: [
      { tab: 'policy', title: "Patch Policy", note: "Which patches a contract (or every contract) approves automatically, and how long one may be deferred. Auto-approval of critical patches needs a CAB member's approval of the policy.",
        fields: [
          { name: 'name', required: true, label: "Policy Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'category', required: true, label: "Patch Category" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] },
      { tab: 'rules', title: "Automated Approval & Contract Association",
        fields: [
          { name: 'msp_contract_id', label: "Scoped To Contract" },
          { name: 'auto_approve', label: "Auto-Approve Patches (critical only if a CAB member approved the policy)" },
          { name: 'max_defer_days', label: "Max Defer Days" },
          { name: 'approved_by_id', label: "Policy Approved By", readonly: true },
          { name: 'approved_by_cab', label: "Approved by a CAB Member", readonly: true },
          { name: 'approved_at', label: "Policy Approved At", readonly: true }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M05:MSP SLA Attainment by Client": "M05-sla",
  "M05:Remote Resolution Rate": "M05-rpt-resolution",
  "M05:Patch Compliance Report": "M05-rpt-patch",
  "M05:Alert-to-Ticket Conversion": "M05-rpt-alertconv",
  "M05:Backup & Restore Test Log": "M05-rpt-backup",
  "M05:SLA Credit Register": "M05-rpt-credits"
};

/* Data-entry form chips -> the module's in-workspace D365 forms (v2) */
export const FORM_CHIPS = {
  'M05:__by_screen__': {
    'M05-msp-patch-policy': 'M05-form-msp-patch-policy',
    'M05-estate': 'M05-form-estate',
    'M05-oncall': 'M05-form-oncall',
    'M05-runbooks': 'M05-form-runbook',
    'M05-patching': 'M05-form-patch',
    'M05-credits': 'M05-form-credit',
    'M05-alert-rules': 'M05-form-alert-rule',
    'M05-tickets': 'M05-form-ticket',
    'M05-runbook-runs': 'M05-form-runbook-run',
    'M05-backups': 'M05-form-backup-job',
  },
  'M05:Runbook Execution': 'M05-form-runbook-run',
  'M05:Backup Job': 'M05-form-backup-job',
  'M05:Health Reading': 'M05-form-reading',
  'M05:Alert Rule': 'M05-form-alert-rule',
  'M05:Monthly Service Report': 'M05-form-monthly-report',
  'M05:MSP Contract': 'M05-form-msp-contract',
  'M05:Managed Estate Device': 'M05-form-estate',
  'M05:On-Call Shift': 'M05-form-oncall',
  'M05:Runbook': 'M05-form-runbook',
  'M05:Patch Update': 'M05-form-patch',
  'M05:Remote Session (consent recorded)': 'M05-form-session',
  'M05:MSP Ticket': 'M05-form-ticket',
  'M05:Change Record': 'M05-form-change',
  'M05:Maintenance Window': 'M05-form-window',
  'M05:__by_model__': {
    'fix.msp.contract': 'M05-form-msp-contract',
    'fix.msp.patch.policy': 'M05-form-msp-patch-policy',
    'fix.monitored.asset': 'M05-form-estate',
    'fix.msp.oncall.shift': 'M05-form-oncall',
    'fix.msp.runbook': 'M05-form-runbook',
    'fix.msp.patch.update': 'M05-form-patch',
    'fix.msp.sla.credit': 'M05-form-credit',
    'fix.remote.session': 'M05-form-session',
    'fix.msp.alert': 'M05-form-ticket',
    'fix.msp.change.record': 'M05-form-change',
    'fix.msp.maintenance.window': 'M05-form-window',
    'fix.msp.alert.rule': 'M05-form-alert-rule',
    'fix.msp.runbook.run': 'M05-form-runbook-run',
    'fix.msp.backup.job': 'M05-form-backup-job'
  }
};

/* data-entry form chips -> the REAL model forms (the registry's four). */
export const FORM_MODELS = {
  'M05:MSP Contract': 'fix.msp.contract',
  'M05:Remote Session (consent recorded)': 'fix.remote.session',
  'M05:MSP Ticket': 'fix.msp.alert',
  'M05:Change Record': 'fix.msp.change.record',
  'M05:Maintenance Window': 'fix.msp.maintenance.window'
};

/* the module's "+ New" surface: the MSP contract is the module's anchor
 * record — per-device pricing, SLA target, monthly report + credits. */
export const CREATE = {
  M05: { screen: 'M05-form-msp-contract', model: 'fix.msp.contract', label: 'MSP Contract' }
};
