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
    /* A02 ERP pass 2 (M05-S12): credits approved this Dhaka month, and the
     * last closed month's credits (a month's credit is drafted after it closes) */
    { l: 'SLA Credits Approved This Month', m: 'sla_credits_mtd' },
    { l: 'SLA Credits Last Month', m: 'sla_credits_last_month' },
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
      { id: 'M05-runbook-runs', en: 'Runbook Executions', bn: 'রানবুক সম্পাদন', t: 'g' },
      { id: 'M05-contacts', en: 'Client Contacts', bn: 'ক্লায়েন্ট যোগাযোগ', t: 'g' },
      { id: 'M05-major-incidents', en: 'Major Incidents', bn: 'বড় ঘটনা', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M05-patching', en: 'Patch Management', bn: 'প্যাচ ব্যবস্থাপনা', t: 'g' },
      { id: 'M05-msp-patch-policy', en: 'Patch Policies', bn: 'প্যাচ পলিসি', t: 'g' },
      { id: 'M05-windows', en: 'Maintenance Windows', bn: 'মেইনটেন্যান্স উইন্ডো', t: 'g' },
      { id: 'M05-problem', en: 'Problem & Change', bn: 'সমস্যা ও পরিবর্তন', t: 'g' }
    ]},
    { en: 'Client Reporting', screens: [
      { id: 'M05-sla', en: 'SLA Attainment', bn: 'এসএলএ অর্জন', t: 'r' },
      { id: 'M05-reviews', en: 'Monthly Service Reports', bn: 'মাসিক সেবা প্রতিবেদন', t: 'g' },
      { id: 'M05-review-meetings', en: 'Service Review Meetings', bn: 'সেবা পর্যালোচনা সভা', t: 'g' },
      { id: 'M05-roadmap', en: 'Technology Roadmap', bn: 'প্রযুক্তি রোডম্যাপ', t: 'g' },
      { id: 'M05-contracts', en: 'MSP Contracts & Monthly Reports', bn: 'এমএসপি চুক্তি ও মাসিক প্রতিবেদন', t: 'g' },
      { id: 'M05-credits', en: 'SLA Credits', bn: 'এসএলএ ক্রেডিট', t: 'g' },
      /* A02 ERP pass 2 (M05-S06 / S13 / S18) */
      { id: 'M05-billing-recon', en: 'MSP Fee vs M39 Billing', bn: 'এমএসপি ফি বনাম বিলিং', t: 'r' },
      { id: 'M05-terms-history', en: 'Contract Terms History', bn: 'চুক্তির শর্ত ইতিহাস', t: 'g' },
      { id: 'M05-alert-pauses', en: 'SLA Pauses (Waiting on Client)', bn: 'এসএলএ বিরতি', t: 'g' }
    ]},
    /* capture audit pass 2 (2026-11-18): FR-RMS-047, spec 8.3 */
    { en: 'Client Onboarding', screens: [
      { id: 'M05-onboarding', en: 'Onboarding Projects', bn: 'অনবোর্ডিং প্রকল্প', t: 'g' },
      { id: 'M05-onboarding-steps', en: 'Onboarding Checklist', bn: 'অনবোর্ডিং চেকলিস্ট', t: 'g' }
    ]},
    { en: 'Specialist Services', screens: [
      { id: 'M05-cloud', en: 'Cloud Subscriptions', bn: 'ক্লাউড সাবস্ক্রিপশন', t: 'g' },
      { id: 'M05-dr-plans', en: 'DR / BC Plans', bn: 'ডিআর / বিসি পরিকল্পনা', t: 'g' },
      { id: 'M05-dr-tests', en: 'DR Tests', bn: 'ডিআর পরীক্ষা', t: 'g' }
    ]}
  ],
  reports: ['MSP Fee vs M39 Billing Reconciliation', 'MSP SLA Attainment by Client', 'Remote Resolution Rate', 'Patch Compliance Report', 'Alert-to-Ticket Conversion', 'Backup & Restore Test Log', 'SLA Credit Register',
    'Cloud Cost & Optimisation', 'Licence Compliance', 'Security Posture'],
  /* M05 capture audit 2026-11-13: every chip that has a form is listed, so
   * each sub-module page names the forms that capture its records */
  forms: ['MSP Contract', 'Remote Session (consent recorded)', 'MSP Ticket', 'Change Record', 'Maintenance Window',
    'Managed Estate Device', 'Health Reading', 'Alert Rule', 'On-Call Shift', 'Runbook', 'Patch Update',
    'Monthly Service Report', 'Runbook Execution', 'Backup Job', 'Client Contact', 'Major Incident',
    'Service Review Meeting', 'Roadmap Item', 'Cloud Subscription', 'DR Plan', 'DR Test',
    /* capture audit pass 2: forms that sat on no page, and the onboarding project */
    'SLA Credit', 'Patch Policy', 'Client Onboarding'],
  cross: ['M08 contract entitlement', 'M17 monitored assets', 'M48 telemetry streams', 'M20 SLA credit billing', 'P04 client portal'],
  freg: {
    src: 93,
    sub: [
      ['1', 'Remote Sessions', 10, { model: 'fix.remote.session', cols: ['msp_contract_id', 'asset_id', 'technician_id', 'tool', 'started_at'], screens: ['M05-sessions', 'M05-console'], reports: ['Remote Resolution Rate'], forms: ['Remote Session (consent recorded)'] }],
      ['2', 'Monitored Estate', 12, { model: 'fix.monitored.asset', cols: ['hostname', 'agent_id', 'msp_contract_id', 'health', 'last_seen'], screens: ['M05-estate', 'M05-cloud'], reports: ['Cloud Cost & Optimisation', 'Licence Compliance'], forms: ['Managed Estate Device', 'Cloud Subscription'] }],
      /* 3 FR-RMS-010/011: an engineer's reading of an asset (an agentless
       * device or a site check) - the health score is computed from it. The
       * page had no button: the metrics were written by the collector only. */
      ['3', 'Metrics & Health Scoring', 9, { model: 'fix.monitored.asset', cols: ['hostname', 'health_score', 'cpu_utilization_pct', 'ram_utilization_pct', 'disk_free_gb'], screens: ['M05-health', 'M05-estate', 'M05-backups', 'M05-dr-plans', 'M05-dr-tests'], reports: ['Backup & Restore Test Log'], forms: ['Health Reading', 'Backup Job', 'DR Plan', 'DR Test'], create: 'M05-form-reading' }],
      /* 4 FR-RMS-015: the engine is configured by its rules; alerts are
       * raised by readings that cross them. The button opened the ticket form. */
      ['4', 'Alerting Engine', 11, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'severity', 'rule_id', 'state', 'create_date'], screens: ['M05-alerts', 'M05-alert-rules', 'M05-windows', 'M05-alert-pauses'], reports: ['Alert-to-Ticket Conversion'], forms: ['Alert Rule', 'MSP Ticket', 'Maintenance Window'], create: 'M05-form-alert-rule' }],
      ['5', 'On-Call & Escalation', 7, { model: 'fix.msp.oncall.shift', cols: ['name', 'technician_id', 'level', 'start_at', 'state'], screens: ['M05-oncall'], reports: [], forms: ['On-Call Shift'] }],
      ['6', 'Runbooks & Remediation', 8, { model: 'fix.msp.runbook', cols: ['name', 'trigger', 'scope_contract_id', 'auto_run', 'auto_resolve_alert'], screens: ['M05-runbooks', 'M05-runbook-runs'], reports: [], forms: ['Runbook', 'Runbook Execution'] }],
      ['7', 'Patch Management', 9, { model: 'fix.msp.patch.update', cols: ['identifier', 'title', 'asset_id', 'severity', 'state'], screens: ['M05-patching', 'M05-msp-patch-policy', 'M05-windows'], reports: ['Patch Compliance Report'], forms: ['Patch Update', 'Patch Policy', 'Maintenance Window'] }],
      /* 8 FR-RMS-026: a client reports by phone, email, portal or chat; the
       * desk lists those and every ticketed alert. Its list refused "+ New",
       * so the page had no button and a phoned-in fault had no input. */
      ['8', 'MSP Service Desk', 13, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'source', 'order_id', 'state', 'escalated'], screens: ['M05-tickets', 'M05-problem', 'M05-contacts', 'M05-major-incidents'], reports: ['Alert-to-Ticket Conversion'], forms: ['MSP Ticket', 'Change Record', 'Client Contact', 'Major Incident'], create: 'M05-form-ticket', domain: ['|', ['state', 'in', ['ticketed', 'resolved']], ['source', '!=', 'monitoring']] }],
      /* 9 FR-RMS-035: the monthly report is generated from its contract,
       * never typed - its figures decide the SLA credit. No button before. */
      ['9', 'Client Reporting', 9, { model: 'fix.msp.service.report', cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'sla_attainment_pct'], screens: ['M05-reviews', 'M05-sla', 'M05-credits', 'M05-review-meetings', 'M05-roadmap', 'M05-terms-history'], reports: ['MSP SLA Attainment by Client', 'SLA Credit Register', 'Security Posture'], forms: ['Monthly Service Report', 'SLA Credit', 'Service Review Meeting', 'Roadmap Item'], create: 'M05-form-monthly-report' }],
      /* 10 FR-RMS-047/048, spec 8.3: the button opened the MSP contract; no
       * record held the onboarding project, its checklist or the go-live
       * from which SLA clocks bind (capture audit pass 2, 2026-11-18) */
      ['10', 'Onboarding Projects', 5, { model: 'fix.msp.onboarding', cols: ['name', 'msp_contract_id', 'state', 'step_done_count', 'coverage_pct', 'live_at'], screens: ['M05-onboarding', 'M05-onboarding-steps', 'M05-contracts', 'M05-estate'], reports: ['MSP SLA Attainment by Client'], forms: ['Client Onboarding', 'MSP Contract'], create: 'M05-form-onboarding' }]
    ]
  }
};

/* In-workspace data screens over the whitelisted MSP models — every one
 * of the 13 registry screens is a live surface now. */
export const SCREENS = {
  /* --- Remote Sessions --- */
  'M05-sessions': { kind: 'model_list', model: 'fix.remote.session',
    cols: ['msp_contract_id', 'asset_id', 'technician_id', 'tool', 'access_mode', 'consent_captured', 'consent_token_ref', 'started', 'started_at', 'ended_at', 'duration_minutes'],
    stateField: 'tool',
    actions: [
      { m: 'action_request_consent', l: 'Request Consent' },
      { m: 'action_verify_consent', l: 'Verify Consent', ask: "Consent code the client read back", kwarg: 'code' },
      { m: 'action_start', l: 'Start Session' },
      { m: 'action_end', l: 'End Session', ask: 'Session recording reference', kwarg: 'recording_url' },
      /* BRU-RMS-12: the reference is shown and the opening logged */
      { m: 'action_open_recording', l: 'Open Recording' }
    ] },
  /* the console = what is RUNNING right now (started, not yet ended) */
  'M05-console': { kind: 'model_list', model: 'fix.remote.session', create: false,
    empty: 'No remote session is running. Open one on Remote Sessions: request and verify the client\u2019s consent, then Start Session.',
    cols: ['started_at', 'msp_contract_id', 'asset_id', 'technician_id', 'tool', 'consent_captured'],
    domain: [['started', '=', true], ['ended_at', '=', false]],
    actions: [{ m: 'action_end', l: 'End Session', ask: 'Session recording reference', kwarg: 'recording_url' }] },

  /* --- Monitored Estate --- */
  'M05-estate': { kind: 'model_list', model: 'fix.monitored.asset', create: true,
    cols: ['agent_id', 'hostname', 'msp_contract_id', 'device_id', 'health', 'health_score', 'open_alert_count', 'last_seen', 'agent_removed_at'],
    stateField: 'health',
    /* BRU-RMS-11: during a client's offboarding each agent's removal is evidenced */
    actions: [
      { m: 'action_record_agent_removal', l: 'Record Agent Removal (offboarding)', ask: 'Evidence: how the removal was confirmed', kwarg: 'evidence' }
    ] },
  'M05-health': { kind: 'table_report', module: 'M05', report: 'estate_health', period: false },
  'M05-alerts': { kind: 'model_list', model: 'fix.msp.alert', create: true,
    cols: ['msp_contract_id', 'asset_id', 'severity', 'message', 'source', 'rule_id', 'coverage_gap', 'state', 'sla_deadline', 'paused', 'escalated', 'order_id', 'resolved_at'],
    stateField: 'state',
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge' },
      { m: 'action_to_ticket', l: 'Create Ticket' },
      { m: 'action_resolve', l: 'Resolve', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_escalate', l: 'Escalate' },
      /* A02 ERP pass 2: reclassify a NEW alert with the reason (M05-S02);
       * stop the SLA clock while waiting on the client (M05-S18); send a
       * ticket to an M02 field visit (M05-S16) */
      { m: 'action_reclassify', l: 'Reclassify (new alerts)', asks: [{ kwarg: 'severity', label: 'New severity: minor or major' }, { kwarg: 'reason', label: 'Why the severity changes' }] },
      { m: 'action_pause', l: 'Pause SLA (Waiting on Client)', ask: 'What the client must do before work continues', kwarg: 'reason' },
      { m: 'action_resume', l: 'Resume SLA' },
      { m: 'action_escalate_to_field', l: 'Escalate to Field Visit (M02)', ask: 'Why a visit is needed', kwarg: 'note' }
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
    cols: ['asset_id', 'severity', 'message', 'source', 'reported_by_contact_id', 'order_id', 'recurring', 'problem_id', 'major_incident_id', 'state', 'sla_deadline', 'responded_at', 'paused', 'escalated', 'field_order_ref', 'resolved_at', 'resolution_note'],
    stateField: 'state',
    domain: ['|', ['state', 'in', ['ticketed', 'resolved']], ['source', '!=', 'monitoring']],
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge' },
      { m: 'action_to_ticket', l: 'Create Service Order' },
      { m: 'action_resolve', l: 'Resolve', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_escalate', l: 'Escalate' },
      /* A02 ERP pass 2: reclassify a NEW alert with the reason (M05-S02);
       * stop the SLA clock while waiting on the client (M05-S18); send a
       * ticket to an M02 field visit (M05-S16) */
      { m: 'action_reclassify', l: 'Reclassify (new alerts)', asks: [{ kwarg: 'severity', label: 'New severity: minor or major' }, { kwarg: 'reason', label: 'Why the severity changes' }] },
      { m: 'action_pause', l: 'Pause SLA (Waiting on Client)', ask: 'What the client must do before work continues', kwarg: 'reason' },
      { m: 'action_resume', l: 'Resume SLA' },
      { m: 'action_escalate_to_field', l: 'Escalate to Field Visit (M02)', ask: 'Why a visit is needed', kwarg: 'note' }
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
    cols: ['msp_contract_id', 'asset_id', 'identifier', 'title', 'category', 'severity', 'state', 'client_approved_at', 'installed_at'],
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_record_test', l: 'Record Pre-Deployment Test', ask: 'Test evidence (pilot ring, result)', kwarg: 'note' },
      { m: 'action_request_window_exception', l: 'Request Exception: Outside Window', ask: 'Why it cannot wait for an approved window', kwarg: 'reason' },
      { m: 'action_request_test_exception', l: 'Request Exception: Skip Test', ask: 'Why it cannot wait for a test', kwarg: 'reason' },
      { m: 'action_recall_approval', l: 'Recall Exception Request' },
      /* A02 ERP pass 2 (M05-S10): outside an open window the client approves first */
      { m: 'action_record_client_approval', l: 'Record Client Approval (out-of-window)', asks: [{ kwarg: 'contact_id', label: 'Client contact ID (a contact who may approve changes)', number: true }, { kwarg: 'evidence', label: 'Evidence: OTP reference or the approving e-mail' }] },
      { m: 'action_install', l: 'Mark Installed' },
      /* A02 ERP audit M05-F18: a deferral names its days (the policy's maximum) and reason */
      { m: 'action_defer', l: 'Defer', asks: [{ kwarg: 'days', label: 'Days to defer (1 to the patch policy maximum)', number: true }, { kwarg: 'reason', label: 'Why the patch is deferred' }] },
      { m: 'action_fail', l: 'Mark Failed', ask: 'What failed (install log, error)', kwarg: 'note' }
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
  /* A02 ERP pass 2 (M05-S06, D8): the MSP terms are the price master */
  'M05-billing-recon': { kind: 'table_report', module: 'M05', report: 'msp_billing_reconciliation', title: 'MSP Fee vs M39 Billing Reconciliation', period: false },
  /* A02 ERP pass 2 (M05-S13): what was in force on any day; written by Amend Terms only */
  'M05-terms-history': { kind: 'model_list', model: 'fix.msp.terms.amendment', create: false,
    cols: ['msp_contract_id', 'effective_date', 'kind', 'device_count', 'per_device_monthly', 'monthly_value', 'monthly_delta', 'sla_target_pct', 'billing_state', 'billing_ref', 'reason', 'amended_by_id'],
    stateField: 'billing_state',
    empty: 'No amendment yet. Amend SLA / Commercial Terms on MSP Contracts records one, with its effective date.' },
  /* A02 ERP pass 2 (M05-S18): the SLA clock stops while the client is awaited */
  'M05-alert-pauses': { kind: 'model_list', model: 'fix.msp.alert.pause', create: false,
    cols: ['alert_id', 'msp_contract_id', 'started_at', 'ended_at', 'reason', 'started_by_id', 'ended_by_id'],
    empty: 'No SLA pause. Pause SLA (Waiting on Client) on an alert stops its clock until Resume SLA.' },
  'M05-reviews': { kind: 'model_list', model: 'fix.msp.service.report', create: false,
    cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'breached_count', 'response_breached_count', 'sla_attainment_pct', 'sla_not_binding', 'mtta_minutes', 'mttr_minutes', 'overage_hours', 'attainment_flagged', 'summary_en'],
    actions: [{ m: 'action_generate_bilingual_report', l: 'Regenerate Summary' },
      /* A02 ERP pass 2 (M05-S15): the bilingual client report as a PDF */
      { m: 'action_print_service_report', l: 'Print Client Report (PDF)' }] },
  /* the monthly report and the SLA credit run, per MSP contract */
  'M05-contracts': { kind: 'model_list', model: 'fix.msp.contract',
    cols: ['name', 'contract_id', 'contract_state', 'entitled', 'device_count', 'enrolled_count', 'coverage_window', 'sla_target_pct', 'monthly_value', 'remote_usage_pct', 'lifecycle'],
    stateField: 'lifecycle',
    actions: [
      /* A02 ERP pass 2 (M05-S14): any finished month, e.g. one the nightly run could not report */
      { m: 'action_generate_monthly_report', l: 'Generate Monthly Report', ask: 'Month (YYYY-MM; empty = last month)', kwarg: 'period' },
      { m: 'action_compute_sla_credits', l: 'Compute SLA Credits' },
      /* A02 ERP audit M05-F3: the SLA and commercial terms change only here,
       * by an SLA credit approver, with the reason (raising the covered
       * devices sends the uplift to billing) */
      { m: 'action_amend_terms', l: 'Amend SLA / Commercial Terms', asks: [
        { kwarg: 'term', label: 'Term: device_count, per_device_monthly, sla_target_pct, alert_resolve_hours_major, alert_resolve_hours_minor, response_hours_major, response_hours_minor, coverage_window (24x7/business), holiday_calendar_id, parts_included, remote_hours_monthly, overage_hourly_rate, unattended_access, recording_retention_days or contract_id' },
        { kwarg: 'value', label: 'New value' },
        /* A02 ERP pass 2 (M05-S13): the day the amendment takes effect */
        { kwarg: 'effective_date', label: 'Effective date (YYYY-MM-DD; empty = today; never inside a reported month)' },
        { kwarg: 'reason', label: 'Reason (the amendment or the client agreement it follows)' }] },
      /* BRU-RMS-11 offboarding: start, record access revoked, complete */
      { m: 'action_start_offboarding', l: 'Start Offboarding' },
      { m: 'action_record_access_revoked', l: 'Record Access Revoked', ask: 'Evidence: which access was revoked and how it was checked', kwarg: 'evidence' },
      /* FR-RMS-048 */
      { m: 'action_record_data_returned', l: 'Record Data Returned', ask: 'Evidence: what client data was handed back or confirmed deleted, and how', kwarg: 'evidence' },
      { m: 'action_complete_offboarding', l: 'Complete Offboarding' }
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

  /* ===== M05 spec features built 2026-11-13 (audit) ===== */
  /* FR-RMS-049 who at the client may do what */
  'M05-contacts': { kind: 'model_list', model: 'fix.msp.client.contact',
    cols: ['msp_contract_id', 'partner_id', 'role', 'can_raise_tickets', 'can_approve_changes', 'can_receive_consent', 'escalation_order', 'escalation_channel'],
    empty: 'No client contact registered. Register who may raise tickets, approve changes and receive consent codes with + New Client Contact.' },
  /* FR-RMS-020 declared, contacts notified, resolved, reviewed by another person */
  'M05-major-incidents': { kind: 'model_list', model: 'fix.msp.major.incident',
    cols: ['name', 'msp_contract_id', 'declared_by_id', 'declared_at', 'notified_count', 'resolved_at', 'reviewed_by_id', 'state'],
    stateField: 'state',
    empty: 'No major incident declared.',
    actions: [
      { m: 'action_notify_contacts', l: 'Notify All Client Contacts' },
      { m: 'action_resolve', l: 'Resolve', ask: 'How the incident was resolved', kwarg: 'note' },
      { m: 'action_record_review', l: 'Record Post-Incident Review', ask: 'Root cause, what changes, follow-ups', kwarg: 'note' }
    ] },
  /* FR-RMS-036 the meeting, its attendees and the actions agreed */
  'M05-review-meetings': { kind: 'model_list', model: 'fix.msp.service.review',
    cols: ['meeting_date', 'msp_contract_id', 'service_report_id', 'open_action_count', 'next_review_date', 'state'],
    stateField: 'state',
    empty: 'No service review held yet. Record one with + New Service Review Meeting.',
    actions: [{ m: 'action_close', l: 'Close Review (all actions done)' }] },
  /* FR-RMS-045/046 strategy deliverables and refresh recommendations */
  'M05-roadmap': { kind: 'model_list', model: 'fix.msp.roadmap.item',
    cols: ['msp_contract_id', 'kind', 'name', 'asset_id', 'target_quarter', 'estimated_value', 'lead_id', 'state'],
    stateField: 'state',
    empty: 'No roadmap item yet.',
    actions: [
      { m: 'action_accept', l: 'Client Accepted' },
      { m: 'action_decline', l: 'Client Declined' },
      { m: 'action_deliver', l: 'Mark Delivered' },
      { m: 'action_create_opportunity', l: 'Raise Sales Opportunity' }
    ] },
  /* FR-RMS-040 */
  'M05-cloud': { kind: 'model_list', model: 'fix.msp.cloud.subscription',
    cols: ['msp_contract_id', 'provider', 'name', 'seats', 'seats_used', 'monthly_cost', 'renewal_date', 'renewal_due', 'state'],
    stateField: 'state',
    empty: 'No cloud subscription tracked yet.' },
  /* FR-RMS-042 / 043 */
  'M05-dr-plans': { kind: 'model_list', model: 'fix.msp.dr.plan',
    cols: ['msp_contract_id', 'name', 'rto_hours', 'rpo_hours', 'test_interval_days', 'last_test_date', 'next_test_due'],
    empty: 'No DR / BC plan registered yet.' },
  'M05-dr-tests': { kind: 'model_list', model: 'fix.msp.dr.test',
    cols: ['test_date', 'msp_contract_id', 'plan_id', 'outcome', 'rto_achieved_hours', 'rpo_achieved_hours', 'meets_targets', 'tested_by_id'],
    stateField: 'outcome',
    empty: 'No DR test recorded yet.' },

  /* ===== capture audit pass 2 (2026-11-18): sub-module 10 ===== */
  /* FR-RMS-047 / spec 8.3: one project per contract, its checklist, and the
   * go-live that makes the SLA clocks contractually binding */
  'M05-onboarding': { kind: 'model_list', model: 'fix.msp.onboarding',
    cols: ['name', 'msp_contract_id', 'kickoff_date', 'target_live_date', 'step_done_count', 'step_count', 'coverage_pct', 'coverage_target_pct', 'live_at', 'state'],
    stateField: 'state',
    empty: 'No client onboarding yet. Start one with + Start a Client Onboarding once the MSP contract is signed.',
    actions: [{ m: 'action_go_live', l: 'Go Live (SLA clocks start)' }] },
  'M05-onboarding-steps': { kind: 'model_list', model: 'fix.msp.onboarding.step', create: false,
    cols: ['onboarding_id', 'name', 'requirement', 'done', 'done_by_id', 'done_at', 'evidence'],
    empty: 'No onboarding checklist yet: each onboarding project brings its eight steps.',
    actions: [{ m: 'action_mark_done', l: 'Mark Step Done', ask: 'Evidence: what was done and how it was checked', kwarg: 'evidence' }] },

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
  /* FR-RMS-041 / 052 / 044 */
  'M05-rpt-cloud-cost': { kind: 'table_report', module: 'M05', report: 'cloud_cost', title: 'Cloud Cost & Optimisation', period: false },
  'M05-rpt-licences': { kind: 'table_report', module: 'M05', report: 'licence_compliance', title: 'Licence Compliance', period: false },
  'M05-rpt-security': { kind: 'table_report', module: 'M05', report: 'security_posture', title: 'Security Posture', period: false },

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
        { name: 'access_mode', required: true, label: 'Access Mode (unattended only if the contract grants it)' },
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
          { name: 'recording_access_count', label: 'Recording Opened (times, each logged)', readonly: true },
          { name: 'recording_purged_at', label: 'Recording Purged At (retention)', readonly: true },
          { name: 'session_summary', label: 'Session Actions / Troubleshooting Summary', type: 'text' }
        ]},
    ] },

  'M05-form-ticket': { kind: 'model_form', model: 'fix.msp.alert',
    title: 'MSP Ticket', newLabel: 'Log a Client Ticket', back: 'M05-tickets',
    status: { field: 'state' },
    tabs: [
      { id: 'alert', label: '1. Report & Asset', bn: '১. অভিযোগ ও সম্পদ', icon: '🚨', badge: '7' },
      { id: 'resolution', label: '2. SLA Resolution & Ticket', bn: '২. সমাধান ও টিকেট', icon: '✅', badge: '12' }
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
        /* FR-RMS-049: a client's report names the registered contact who raised it */
        { name: 'reported_by_contact_id', label: 'Reported By (registered client contact; required for a client report)' },
        { name: 'severity', required: true, label: 'Severity' },
        { name: 'message', required: true, label: 'What the Client Reported' },
        { name: 'rule_id', label: 'Raised by Alert Rule', readonly: true },
        { name: 'escalated', label: 'Escalated to On-Call Rota', readonly: true },
        { name: 'escalated_at', label: 'Escalated At', readonly: true },
        { name: 'coverage_gap', label: 'Coverage Gap (no agent report for 24 h)', readonly: true },
      ]},
      { tab: 'resolution', title: 'Ticket Conversion & Resolution Verification', fields: [
        { name: 'order_id', label: 'Commercial Service Order (M01)', readonly: true },
        { name: 'recurring', label: 'Recurring on This Asset (BRU-RMS-10)', readonly: true },
        { name: 'problem_id', label: 'Problem Record (needed to resolve a recurring incident)' },
        { name: 'major_incident_id', label: 'Major Incident' },
        { name: 'state', label: 'Ticket / Alert State', readonly: true },
        /* A02 ERP pass 2 (M05-S02 / S18): stamped when raised; pauses extend them */
        { name: 'sla_deadline', label: 'Resolution Deadline (stamped when raised)', readonly: true },
        { name: 'response_deadline', label: 'Response Deadline', readonly: true },
        { name: 'responded_at', label: 'First Response At', readonly: true },
        { name: 'paused', label: 'SLA Clock Paused (Waiting on Client)', readonly: true },
        { name: 'field_order_ref', label: 'Field Visit (M02)', readonly: true },
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
      { id: 'telemetry', label: '2. Telemetry & Agent Health', bn: '২. এজেন্ট স্থিতি ও অডিট', icon: '📊', badge: '5' }
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
          { name: 'last_seen', label: "Agent Last Heartbeat Timestamp", readonly: true },
          { name: 'agent_removed_at', label: "Agent Removed At (offboarding)", readonly: true },
          { name: 'agent_removal_evidence', label: "Agent Removal Evidence", readonly: true }
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
          { name: 'exception_approved_by_id', label: "Exception Approved By", readonly: true },
          /* A02 ERP pass 2 (M05-S10): an install outside an open window */
          { name: 'client_approval_contact_id', label: "Client Approver (out-of-window install)", readonly: true },
          { name: 'client_approval_evidence', label: "Client Approval Evidence", readonly: true },
          { name: 'client_approved_at', label: "Client Approved At", readonly: true }
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
    /* A02 ERP pass 2 (X5-19, M05-S13): the contract's reports, credits and
     * terms history were on no form */
    grids: [
      { field: 'report_ids', tab: 'records', title: 'Monthly Service Reports', readonlyGrid: true,
        empty: 'No service report yet: the nightly run makes one for every finished month.',
        fields: [
          { name: 'period_label', label: 'Month', readonly: true },
          { name: 'alert_count', label: 'Alerts', readonly: true },
          { name: 'breached_count', label: 'Breaches', readonly: true },
          { name: 'sla_attainment_pct', label: 'Attainment %', readonly: true },
          { name: 'sla_not_binding', label: 'Not Yet Binding', readonly: true },
          { name: 'overage_hours', label: 'Overage Hours', readonly: true }
        ] },
      { field: 'credit_ids', tab: 'records', title: 'SLA Credits', readonlyGrid: true,
        empty: 'No SLA credit: every reported month met its target.',
        fields: [
          { name: 'period_label', label: 'Month', readonly: true },
          { name: 'attainment_pct', label: 'Attained %', readonly: true },
          { name: 'target_pct', label: 'Target %', readonly: true },
          { name: 'credit_amount', label: 'Credit (BDT, before VAT)', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { field: 'terms_amendment_ids', tab: 'records', title: 'Terms History', readonlyGrid: true,
        empty: 'Never amended: the terms above are the terms since the start.',
        fields: [
          { name: 'effective_date', label: 'Effective', readonly: true },
          { name: 'kind', label: 'Kind', readonly: true },
          { name: 'device_count', label: 'Devices', readonly: true },
          { name: 'per_device_monthly', label: 'Per Device', readonly: true },
          { name: 'monthly_delta', label: 'Monthly Fee Change', readonly: true },
          { name: 'sla_target_pct', label: 'Target %', readonly: true },
          { name: 'billing_state', label: 'Billing (M39)', readonly: true },
          { name: 'reason', label: 'Reason', readonly: true }
        ] }
    ],
    tabs: [
      { id: 'contract', label: '1. Contract & Scope', bn: '১. চুক্তি ও পরিধি', icon: '📑', badge: '6' },
      { id: 'commercial', label: '2. Commercials & SLA', bn: '২. মূল্য ও এসএলএ', icon: '💰', badge: '14' },
      { id: 'lifecycle', label: '3. Lifecycle & Offboarding', bn: '৩. জীবনচক্র ও অফবোর্ডিং', icon: '🔚', badge: '10' },
      { id: 'records', label: '4. Reports, Credits & Terms History', bn: '৪. প্রতিবেদন, ক্রেডিট ও শর্ত', icon: '📊' }
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
          { name: 'device_count', label: "Covered Devices (enrolment stops at this count; none = no enrolment)" },
          { name: 'enrolled_count', label: "Enrolled Devices", readonly: true },
          { name: 'unattended_access', label: "Unattended Access Granted (BRU-RMS-02)" }
        ] },
      { tab: 'commercial', title: "Commercials & Service Levels",
        note: "Typed once when the contract is created (by an SLA credit approver); afterwards they change only through Amend SLA / Commercial Terms on MSP Contracts. A credit is a share of what was invoiced for its month (else the monthly value) and never exceeds it.",
        fields: [
          { name: 'per_device_monthly', label: "Per-Device Monthly (BDT)" },
          { name: 'monthly_value', label: "Monthly Value (BDT)", readonly: true },
          { name: 'sla_target_pct', label: "SLA Target %" },
          { name: 'alert_resolve_hours_major', label: "Major Alert Resolution Target (h)" },
          { name: 'alert_resolve_hours_minor', label: "Minor Alert Resolution Target (h)" },
          { name: 'coverage_window', required: true, label: "SLA Coverage Window (the hours the clock runs)" },
          { name: 'holiday_calendar_id', label: "Holiday Calendar (business-hours clocks stop on its holidays)" },
          { name: 'recording_retention_days', label: "Session Recording Retention (days, 0 = contract life)" },
          /* A02 ERP pass 2 (M05-S09 / S17 / S18) */
          { name: 'response_hours_major', label: "Major Alert Response Target (h, 0 = none)" },
          { name: 'response_hours_minor', label: "Minor Alert Response Target (h, 0 = none)" },
          { name: 'parts_included', label: "Parts Entitlement (else parts are an approved overage estimate)" },
          { name: 'remote_hours_monthly', label: "Remote Support Hours a Month (0 = not metered)" },
          { name: 'overage_hourly_rate', label: "Overage Rate (BDT / hour; none = flagged, not billed)" },
          { name: 'remote_usage_pct', label: "Remote Hours Used This Month (%)", readonly: true }
        ] },
      { tab: 'lifecycle', title: "Service Lifecycle & Offboarding (BRU-RMS-11)",
        note: "Offboarding is run from MSP Contracts: Start Offboarding, record each agent's removal on Estate & Agents and the access revocation here, then Complete Offboarding. It completes only when every agent is removed and access is revoked, each with its evidence.",
        fields: [
          { name: 'lifecycle', label: "Service Lifecycle", readonly: true },
          { name: 'service_live_at', label: "Service Live Since (SLA clocks bind from here)", readonly: true },
          { name: 'offboarding_started_at', label: "Offboarding Started At", readonly: true },
          { name: 'access_revoked_at', label: "Access Revoked At", readonly: true },
          { name: 'access_revoked_evidence', label: "Access Revocation Evidence", readonly: true },
          { name: 'data_returned_at', label: "Client Data Returned At", readonly: true },
          { name: 'data_return_evidence', label: "Data Return Evidence", readonly: true },
          { name: 'offboarded_at', label: "Offboarded At", readonly: true },
          { name: 'offboarded_by_id', label: "Offboarded By", readonly: true }
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
          /* A02 ERP pass 2 (M05-S18) */
          { name: 'response_breached_count', label: "Response Target Missed", readonly: true },
          { name: 'mtta_minutes', label: "MTTA (min)", readonly: true },
          { name: 'mttr_minutes', label: "MTTR (min)", readonly: true },
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

  'M05-form-contact': { kind: 'model_form', model: 'fix.msp.client.contact', title: 'Client Contact', back: 'M05-contacts',
    sections: [
      { title: 'Authorised Client Contact (FR-RMS-049)',
        note: 'A contact of the client of this contract. A client report names its contact, who must be allowed to raise tickets; once contacts are registered, only one allowed to receive consent codes can consent to a remote session.',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'partner_id', required: true, label: 'Contact' },
          { name: 'role', required: true, label: 'Role' },
          { name: 'can_raise_tickets', label: 'May Raise Tickets' },
          { name: 'can_approve_changes', label: 'May Approve Changes' },
          { name: 'can_receive_consent', label: 'Receives Remote-Session Consent Codes' },
          { name: 'escalation_order', label: 'Escalation Order (1 = first)' },
          { name: 'escalation_channel', required: true, label: 'Escalation Channel' },
          { name: 'active', label: 'Active' }
        ] }
    ] },
  'M05-form-major-incident': { kind: 'model_form', model: 'fix.msp.major.incident', title: 'Major Incident', newLabel: 'Declare a Major Incident', back: 'M05-major-incidents',
    status: { field: 'state' },
    sections: [
      { title: 'Major Incident (FR-RMS-020)',
        note: 'Declare it, then Notify All Client Contacts, Resolve, and a Post-Incident Review by someone other than the declarer closes it. Link the alerts and tickets from the MSP Ticket form.',
        fields: [
          { name: 'name', required: true, label: 'Incident' },
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'impact', required: true, label: 'Impact on the Client', type: 'text' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'declared_by_id', label: 'Declared By', readonly: true },
          { name: 'declared_at', label: 'Declared At', readonly: true },
          { name: 'notified_at', label: 'Contacts Notified At', readonly: true },
          { name: 'notified_count', label: 'Contacts Notified', readonly: true },
          { name: 'resolved_at', label: 'Resolved At', readonly: true },
          { name: 'resolution_note', label: 'Resolution', type: 'text', readonly: true },
          { name: 'review_note', label: 'Post-Incident Review', type: 'text', readonly: true },
          { name: 'reviewed_by_id', label: 'Reviewed By', readonly: true }
        ] }
    ] },
  'M05-form-review-meeting': { kind: 'model_form', model: 'fix.msp.service.review', title: 'Service Review Meeting', back: 'M05-review-meetings',
    status: { field: 'state' },
    lines: { field: 'action_ids', title: 'Actions Agreed',
      note: 'The review closes only when every action is done.',
      fields: [
        { name: 'name', label: 'Action' },
        { name: 'owner_id', label: 'Owner' },
        { name: 'due_date', label: 'Due' },
        { name: 'done', label: 'Done' }
      ] },
    sections: [
      { title: 'Client Service Review (FR-RMS-036)',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'meeting_date', required: true, label: 'Meeting Date' },
          { name: 'attendees', required: true, label: 'Attendees', type: 'text' },
          { name: 'service_report_id', label: 'Service Report Discussed' },
          { name: 'summary', label: 'Discussion & Decisions', type: 'text' },
          { name: 'next_review_date', label: 'Next Review' },
          { name: 'open_action_count', label: 'Open Actions', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] }
    ] },
  'M05-form-roadmap': { kind: 'model_form', model: 'fix.msp.roadmap.item', title: 'Roadmap Item', back: 'M05-roadmap',
    status: { field: 'state' },
    sections: [
      { title: 'Technology Roadmap & Strategy (FR-RMS-045 / 046)',
        note: 'A refresh, recommendation or strategy deliverable for the client. Once the client accepts it, Raise Sales Opportunity opens it in the sales pipeline (M07).',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'name', required: true, label: 'Item' },
          { name: 'description', label: 'Rationale', type: 'text' },
          { name: 'asset_id', label: 'Asset Concerned' },
          { name: 'target_quarter', label: 'Target Quarter (YYYY-Qn)' },
          { name: 'estimated_value', label: 'Estimated Value (BDT)' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'lead_id', label: 'Sales Opportunity', readonly: true }
        ] }
    ] },
  'M05-form-cloud': { kind: 'model_form', model: 'fix.msp.cloud.subscription', title: 'Cloud Subscription', back: 'M05-cloud',
    sections: [
      { title: 'Client Cloud Subscription (FR-RMS-040)',
        note: 'Flagged when it renews within 30 days.',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'provider', required: true, label: 'Provider' },
          { name: 'name', required: true, label: 'Plan / Subscription' },
          { name: 'seats', label: 'Seats / Licences' },
          { name: 'seats_used', label: 'Seats In Use' },
          { name: 'unit_cost', label: 'Monthly Cost per Seat (BDT)' },
          { name: 'monthly_cost', label: 'Monthly Cost (BDT)', readonly: true },
          { name: 'renewal_date', required: true, label: 'Renews On' },
          { name: 'state', required: true, label: 'State' },
          { name: 'renewal_due', label: 'Renews Within 30 Days', readonly: true }
        ] }
    ] },
  'M05-form-dr-plan': { kind: 'model_form', model: 'fix.msp.dr.plan', title: 'DR Plan', back: 'M05-dr-plans',
    sections: [
      { title: 'Disaster Recovery / Continuity Plan (FR-RMS-042)',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'name', required: true, label: 'Plan' },
          { name: 'scope', required: true, label: 'Systems Covered', type: 'text' },
          { name: 'rto_hours', required: true, label: 'Recovery Time Objective (h)' },
          { name: 'rpo_hours', required: true, label: 'Recovery Point Objective (h)' },
          { name: 'test_interval_days', required: true, label: 'Test Every (days)' },
          { name: 'last_test_date', label: 'Last Test', readonly: true },
          { name: 'next_test_due', label: 'Next Test Due', readonly: true },
          { name: 'active', label: 'Active' }
        ] }
    ] },
  'M05-form-dr-test': { kind: 'model_form', model: 'fix.msp.dr.test', title: 'DR Test', newLabel: 'Record a DR Test', back: 'M05-dr-tests',
    sections: [
      { title: 'DR Test Result (FR-RMS-043)',
        note: 'Passed only when both the recovery time and the data-loss window met the plan targets. Recorded once; a test is evidence.',
        fields: [
          { name: 'plan_id', required: true, label: 'DR Plan' },
          { name: 'test_date', required: true, label: 'Test Date' },
          { name: 'outcome', required: true, label: 'Outcome' },
          { name: 'rto_achieved_hours', required: true, label: 'Recovery Time Achieved (h)' },
          { name: 'rpo_achieved_hours', required: true, label: 'Data Loss Window Achieved (h)' },
          { name: 'evidence', required: true, label: 'Evidence', type: 'text' },
          { name: 'meets_targets', label: 'Met Targets', readonly: true },
          { name: 'tested_by_id', label: 'Tested By', readonly: true }
        ] }
    ] },

  'M05-form-onboarding': {
    kind: 'model_form',
    model: 'fix.msp.onboarding',
    title: 'Client Onboarding',
    newLabel: 'Start a Client Onboarding',
    back: 'M05-onboarding',
    status: { field: 'state' },
    lines: { field: 'step_ids', title: 'Onboarding Checklist (spec 8.3)', readonlyGrid: true,
      note: 'Mark each step done on Onboarding Checklist with its evidence. Agents, baseline, contacts, runbooks, alert rules and the SLA are checked by the system when marked.',
      fields: [
        { name: 'name', label: 'Step', readonly: true },
        { name: 'requirement', label: 'Done When', readonly: true },
        { name: 'done', label: 'Done', readonly: true },
        { name: 'done_by_id', label: 'Done By', readonly: true },
        { name: 'done_at', label: 'Done At', readonly: true },
        { name: 'evidence', label: 'Evidence', readonly: true }
      ] },
    tabs: [
      { id: 'project', label: '1. Project', bn: '১. প্রকল্প', icon: '🚀', badge: '7' },
      { id: 'live', label: '2. Coverage & Go-Live', bn: '২. কভারেজ ও চালু', icon: '✅', badge: '9' }
    ],
    sections: [
      { tab: 'project', title: 'Client Onboarding Project (FR-RMS-047)',
        note: 'One project per signed MSP contract. The eight-step checklist comes with it. Needs the MSP Engineer role.',
        fields: [
          { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
          { name: 'name', label: 'Project (empty: Onboarding: <contract>)' },
          { name: 'kickoff_date', required: true, label: 'Kick-off' },
          { name: 'target_live_date', label: 'Target Go-Live' },
          { name: 'notes', label: 'Scope & Notes', type: 'text' },
          { name: 'state', label: 'Stage', readonly: true },
          { name: 'started_by_id', label: 'Started By', readonly: true }
        ] },
      { tab: 'live', title: 'Coverage Verified, Then Service Live',
        note: 'Go Live needs every step done and at least the agreed share of covered devices reporting in the last 24 h. SLA clocks are contractually binding only from that moment.',
        fields: [
          { name: 'coverage_target_pct', required: true, label: 'Coverage Needed to Go Live (%)' },
          { name: 'covered_count', label: 'Covered Devices', readonly: true },
          { name: 'reporting_count', label: 'Agents Reporting (24 h)', readonly: true },
          { name: 'coverage_pct', label: 'Coverage Now (%)', readonly: true },
          { name: 'step_done_count', label: 'Steps Done', readonly: true },
          { name: 'step_count', label: 'Steps', readonly: true },
          { name: 'live_at', label: 'Service Live Since', readonly: true },
          { name: 'live_by_id', label: 'Taken Live By', readonly: true },
          { name: 'live_coverage_pct', label: 'Coverage at Go-Live (%)', readonly: true }
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
  "M05:MSP Fee vs M39 Billing Reconciliation": "M05-billing-recon",
  "M05:MSP SLA Attainment by Client": "M05-sla",
  "M05:Remote Resolution Rate": "M05-rpt-resolution",
  "M05:Patch Compliance Report": "M05-rpt-patch",
  "M05:Alert-to-Ticket Conversion": "M05-rpt-alertconv",
  "M05:Backup & Restore Test Log": "M05-rpt-backup",
  "M05:SLA Credit Register": "M05-rpt-credits",
  "M05:Cloud Cost & Optimisation": "M05-rpt-cloud-cost",
  "M05:Licence Compliance": "M05-rpt-licences",
  "M05:Security Posture": "M05-rpt-security"
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
    'M05-contacts': 'M05-form-contact',
    'M05-major-incidents': 'M05-form-major-incident',
    'M05-review-meetings': 'M05-form-review-meeting',
    'M05-roadmap': 'M05-form-roadmap',
    'M05-cloud': 'M05-form-cloud',
    'M05-dr-plans': 'M05-form-dr-plan',
    'M05-dr-tests': 'M05-form-dr-test',
    'M05-onboarding': 'M05-form-onboarding',
  },
  'M05:SLA Credit': 'M05-form-credit',
  'M05:Patch Policy': 'M05-form-msp-patch-policy',
  'M05:Client Onboarding': 'M05-form-onboarding',
  'M05:Client Contact': 'M05-form-contact',
  'M05:Major Incident': 'M05-form-major-incident',
  'M05:Service Review Meeting': 'M05-form-review-meeting',
  'M05:Roadmap Item': 'M05-form-roadmap',
  'M05:Cloud Subscription': 'M05-form-cloud',
  'M05:DR Plan': 'M05-form-dr-plan',
  'M05:DR Test': 'M05-form-dr-test',
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
    'fix.msp.backup.job': 'M05-form-backup-job',
    'fix.msp.client.contact': 'M05-form-contact',
    'fix.msp.major.incident': 'M05-form-major-incident',
    'fix.msp.service.review': 'M05-form-review-meeting',
    'fix.msp.roadmap.item': 'M05-form-roadmap',
    'fix.msp.cloud.subscription': 'M05-form-cloud',
    'fix.msp.dr.plan': 'M05-form-dr-plan',
    'fix.msp.dr.test': 'M05-form-dr-test',
    'fix.msp.onboarding': 'M05-form-onboarding'
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
