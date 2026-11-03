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
    { en: 'Record Coverage', screens: [
      { id: 'M05-msp-patch-policy', en: "Msp Patch Policy", bn: "এমএসপি প্যাচ পলিসি", t: 'g' }
    ]},
    { en: 'Remote Sessions', screens: [
      { id: 'M05-sessions', en: 'Remote Sessions', bn: 'রিমোট সেশন', t: 'g' },
      { id: 'M05-console', en: 'Session Console', bn: 'সেশন কনসোল', t: 'c' }
    ]},
    { en: 'Monitored Estate', screens: [
      { id: 'M05-estate', en: 'Estate & Agents', bn: 'এস্টেট ও এজেন্ট', t: 'g' },
      { id: 'M05-health', en: 'Health Scoring', bn: 'হেলথ স্কোরিং', t: 'd' },
      { id: 'M05-alerts', en: 'Alert Rules & Inbox', bn: 'অ্যালার্ট ইনবক্স', t: 'g' }
    ]},
    { en: 'Service Desk', screens: [
      { id: 'M05-tickets', en: 'MSP Tickets', bn: 'এমএসপি টিকেট', t: 'g' },
      { id: 'M05-oncall', en: 'On-Call Rota', bn: 'অন-কল রোটা', t: 'g' },
      { id: 'M05-runbooks', en: 'Runbooks & Auto-Remediation', bn: 'রানবুক ও অটো-রিমিডিয়েশন', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M05-patching', en: 'Patch Management', bn: 'প্যাচ ব্যবস্থাপনা', t: 'g' },
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
  forms: ['Remote Session (consent recorded)', 'MSP Ticket', 'Change Record', 'Maintenance Window'],
  cross: ['M08 contract entitlement', 'M17 monitored assets', 'M48 telemetry streams', 'M20 SLA credit billing', 'P04 client portal'],
  freg: {
    src: 93,
    sub: [
      ['1', 'Remote Sessions', 10, { model: 'fix.remote.session', cols: ['msp_contract_id', 'asset_id', 'technician_id', 'tool', 'started_at'], screens: ['M05-sessions', 'M05-console'] }],
      ['2', 'Monitored Estate', 12, { model: 'fix.monitored.asset', cols: ['hostname', 'agent_id', 'msp_contract_id', 'health', 'last_seen'], screens: ['M05-estate'] }],
      ['3', 'Metrics & Health Scoring', 9, { model: 'fix.monitored.asset', cols: ['hostname', 'health_score', 'cpu_utilization_pct', 'ram_utilization_pct', 'disk_free_gb'], screens: ['M05-health', 'M05-estate'] }],
      ['4', 'Alerting Engine', 11, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'severity', 'state', 'create_date'], screens: ['M05-alerts'] }],
      ['5', 'On-Call & Escalation', 7, { model: 'fix.msp.oncall.shift', cols: ['name', 'technician_id', 'level', 'start_at', 'state'], screens: ['M05-oncall'] }],
      ['6', 'Runbooks & Remediation', 8, { model: 'fix.msp.runbook', cols: ['name', 'trigger', 'scope_contract_id', 'auto_run', 'auto_resolve_alert'], screens: ['M05-runbooks'] }],
      ['7', 'Patch Management', 9, { model: 'fix.msp.patch.update', cols: ['identifier', 'title', 'asset_id', 'severity', 'state'], screens: ['M05-patching', 'M05-msp-patch-policy', 'M05-windows'] }],
      ['8', 'MSP Service Desk', 13, { model: 'fix.msp.alert', cols: ['message', 'asset_id', 'order_id', 'state', 'escalated'], screens: ['M05-tickets', 'M05-problem'], domain: [['state', 'in', ['ticketed', 'resolved']]] }],
      ['9', 'Client Reporting', 9, { model: 'fix.msp.service.report', cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'sla_attainment_pct'], screens: ['M05-reviews', 'M05-sla'] }],
      ['10', 'Onboarding Projects', 5, { model: 'fix.msp.contract', cols: ['name', 'contract_id', 'device_count', 'monitoring_scope', 'sla_target_pct'], screens: ['M05-estate'] }]
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
  'M05-console': { kind: 'model_list', model: 'fix.remote.session', create: true,
    cols: ['started_at', 'msp_contract_id', 'asset_id', 'technician_id', 'tool', 'consent_captured'],
    domain: [['started', '=', true], ['ended_at', '=', false]],
    actions: [{ m: 'action_end', l: 'End Session', ask: 'Session recording reference', kwarg: 'recording_url' }] },

  /* --- Monitored Estate --- */
  'M05-estate': { kind: 'model_list', model: 'fix.monitored.asset', create: true,
    cols: ['agent_id', 'hostname', 'msp_contract_id', 'device_id', 'health', 'health_score', 'open_alert_count', 'last_seen'],
    stateField: 'health' },
  'M05-health': { kind: 'table_report', module: 'M05', report: 'estate_health', period: false },
  'M05-alerts': { kind: 'model_list', model: 'fix.msp.alert', create: true,
    cols: ['msp_contract_id', 'asset_id', 'severity', 'message', 'state', 'escalated', 'order_id', 'resolved_at'],
    stateField: 'state',
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge' },
      { m: 'action_to_ticket', l: 'Create Ticket' },
      { m: 'action_resolve', l: 'Resolve', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_escalate', l: 'Escalate' }
    ] },

  /* --- Service Desk --- */
  'M05-tickets': { kind: 'model_list', model: 'fix.msp.alert', create: false,
    cols: ['asset_id', 'severity', 'message', 'order_id', 'state', 'escalated', 'resolved_at', 'resolution_note'],
    domain: [['state', 'in', ['ticketed', 'resolved']] ] },
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
    actions: [
      { m: 'action_execute', l: 'Log Execution', ask: 'Asset agent ID (blank = first in scope)', kwarg: 'asset' }
    ] },

  /* --- Compliance --- */
  'M05-patching': { kind: 'model_list', model: 'fix.msp.patch.update',
    cols: ['msp_contract_id', 'asset_id', 'identifier', 'title', 'category', 'severity', 'state', 'installed_at'],
    stateField: 'state',
    actions: [
      { m: 'action_approve', l: 'Approve' },
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
      { m: 'action_approve', l: 'Approve (CAB / emergency: change manager)' },
      { m: 'action_reject', l: 'Reject', ask: 'Rejection reason', kwarg: 'note' },
      { m: 'action_implement', l: 'Mark Implemented', ask: 'Implementation note', kwarg: 'note' },
      { m: 'action_record_review', l: 'Record Post-Implementation Review', ask: 'Review: what was done, outcome, follow-ups', kwarg: 'note' },
      { m: 'action_close', l: 'Close', ask: 'Closing note', kwarg: 'note' }
    ] },

  /* --- Client Reporting --- */
  'M05-sla': { kind: 'table_report', module: 'M05', report: 'sla_by_client', title: 'MSP SLA Attainment by Client', period: false },
  'M05-reviews': { kind: 'model_list', model: 'fix.msp.service.report', create: false,
    cols: ['msp_contract_id', 'period_label', 'alert_count', 'resolved_count', 'sla_attainment_pct', 'attainment_flagged', 'summary_en'],
    actions: [{ m: 'action_generate_bilingual_report', l: 'Regenerate Summary' }] },
  /* the monthly report and the SLA credit run, per MSP contract */
  'M05-contracts': { kind: 'model_list', model: 'fix.msp.contract', create: false,
    cols: ['name', 'contract_id', 'device_count', 'monitoring_scope', 'sla_target_pct', 'monthly_value'],
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
      { m: 'action_approve', l: 'Approve Credit' },
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
  'M05-rpt-backup': { kind: 'table_report', module: 'M05', report: 'backup_log', title: 'Backup & Restore Test Log', period: false },
  'M05-rpt-credits': { kind: 'table_report', module: 'M05', report: 'sla_credit_register', title: 'SLA Credit Register', period: true },

  /* ============ THE FOUR REGISTRY FORMS as D365 model_forms (v2) ==========
   * The chips previously opened stock Odoo dialogs. */
  'M05-form-session': { kind: 'model_form', model: 'fix.remote.session',
    title: 'Remote Session', back: 'M05-sessions',
    tabs: [
      { id: 'session', label: '1. Session Identity', bn: '১. সেশন তথ্য', icon: '🖥️', badge: '5' },
      { id: 'consent', label: '2. Consent & Recording', bn: '২. সম্মতি ও অডিট', icon: '🔒', badge: '5' }
    ],
    sections: [
      { tab: 'session', title: 'Remote Support Session Scope & Asset', fields: [
        { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
        { name: 'asset_id', label: 'Monitored Asset' },
        { name: 'technician_id', label: 'Technician' },
        { name: 'tool', label: 'Remote Access Tool' },
        { name: 'started', label: 'Session Active', readonly: true },
      ]},
      { tab: 'consent', title: 'Customer Explicit Consent & Session Log (FLAW-05.1)',
        note: 'A remote session strictly requires customer consent recording prior to opening remote desktop tunnels.',
        fields: [
          { name: 'consent_partner_id', label: 'Consenting Client Contact (receives the code)' },
          { name: 'consent_captured', label: 'Customer Explicit Consent Captured', readonly: true },
          { name: 'consent_token_ref', label: 'Consent Token Reference', readonly: true },
          { name: 'consent_captured_at', label: 'Consent Captured At', readonly: true },
          { name: 'started_at', label: 'Session Started At', readonly: true },
          { name: 'ended_at', label: 'Session Ended At', readonly: true },
          { name: 'recording_url', label: 'Session Recording Reference', readonly: true },
          { name: 'session_summary', label: 'Session Actions / Troubleshooting Summary', type: 'text' }
        ]},
    ] },

  'M05-form-ticket': { kind: 'model_form', model: 'fix.msp.alert',
    title: 'MSP Ticket', back: 'M05-tickets',
    status: { field: 'state' },
    tabs: [
      { id: 'alert', label: '1. Telemetry Alert', bn: '১. সতর্কবার্তা', icon: '🚨', badge: '5' },
      { id: 'resolution', label: '2. SLA Resolution & Ticket', bn: '২. সমাধান ও টিকেট', icon: '✅', badge: '5' }
    ],
    sections: [
      { tab: 'alert', title: 'Telemetry Ingestion & Alert Header', fields: [
        { name: 'msp_contract_id', required: true, label: 'MSP Contract' },
        { name: 'asset_id', label: 'Monitored Asset' },
        { name: 'severity', label: 'Alert Severity Level' },
        { name: 'escalated', label: 'Escalated to On-Call Rota', readonly: true },
        { name: 'message', label: 'Telemetry Message & Stack Trace', type: 'text' },
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
      { id: 'approval', label: '2. Risk & CAB Sign-Off', bn: '২. ঝুঁকি ও সিএবি অনুমোদন', icon: '✍️', badge: '10' }
    ],
    sections: [
      { tab: 'change', title: 'ITIL Change Classification & Asset Target', fields: [
        { name: 'name', required: true, label: 'Change Title' },
        { name: 'msp_contract_id', label: 'MSP Contract' },
        { name: 'asset_id', label: 'Target Asset / Service' },
        { name: 'kind', label: 'Record Kind (Problem / Change)' },
        { name: 'change_type', label: 'Change Type (Standard/Normal/Emergency)' },
        { name: 'emergency', label: 'Emergency Path (change manager approves)', readonly: true },
        { name: 'requested_by', label: 'Requested By Engineer' },
        { name: 'maintenance_window_id', label: 'Approved Maintenance Window' },
        { name: 'state', label: 'Change Lifecycle State', readonly: true }
      ]},
      { tab: 'approval', title: 'Risk Assessment, CAB Approval & Rollback Plan',
        note: 'A high-risk change needs a rollback plan before CAB approval. A normal change is implemented only inside its approved, open window; an emergency change needs a post-implementation review before close.',
        fields: [
        { name: 'risk', label: 'Risk Rating (Low/Medium/High)' },
        { name: 'description', label: 'Scope of Change & Implementation Plan', type: 'text' },
        { name: 'rollback_plan', label: 'Backout & Rollback Plan', type: 'text' },
        { name: 'cab_approver_id', label: 'CAB Approving Authority', readonly: true },
        { name: 'approved_at', label: 'Approved At', readonly: true },
        { name: 'implemented_by_id', label: 'Implemented By', readonly: true },
        { name: 'implemented_at', label: 'Implementation Completed At', readonly: true },
        { name: 'resolution_note', label: 'Implementation / Closing Note', type: 'text', readonly: true },
        { name: 'pir_note', label: 'Post-Implementation Review', type: 'text', readonly: true },
        { name: 'pir_by_id', label: 'Reviewed By', readonly: true }
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
        { name: 'approved_at', label: 'Approved At', readonly: true }
      ]},
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M05-form-estate': {
    kind: 'model_form',
    model: 'fix.monitored.asset',
    title: "Managed Estate Device",
    back: 'M05-estate',
    tabs: [
      { id: 'asset', label: '1. Device Identity', bn: '১. ডিভাইসের পরিচিতি', icon: '💻', badge: '6' },
      { id: 'telemetry', label: '2. Telemetry & Agent Health', bn: '২. এজেন্ট স্থিতি ও অডিট', icon: '📊', badge: '3' }
    ],
    sections: [
      { tab: 'asset', title: "Managed Estate Device Inventory", note: "One device under the MSP contract: serials, warranty window and covered-customer link.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'msp_contract_id', required: true, label: "MSP Contract" },
          { name: 'agent_id', required: true, label: "RMM Agent Identifier" },
          { name: 'hostname', label: "Device Hostname / FQDN" },
          { name: 'device_id', label: "Registered Hardware Asset" },
          { name: 'health', required: true, label: "Health Status" }
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
      { id: 'deployment', label: '2. Deployment & Compliance', bn: '২. ইনস্টলেশন ও স্থিতি', icon: '📦', badge: '7' }
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
          { name: 'auto_approved_policy_id', label: "Auto-Approved By Policy", readonly: true },
          { name: 'installed_at', label: "Installation Verified At", readonly: true },
          { name: 'fail_note', label: "Failure Note", readonly: true }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M05-msp-patch-policy': { kind: 'model_list', model: 'fix.msp.patch.policy',
    cols: ['name', 'active', 'company_id', 'operating_unit_id', 'msp_contract_id', 'category', 'auto_approve', 'approved_by_id', 'approved_by_cab'],
    actions: [{ m: 'action_approve', l: 'Approve Policy (CAB / Change Manager)' }] },

  'M05-form-credit': {
    kind: 'model_form',
    model: 'fix.msp.sla.credit',
    title: "SLA Credit",
    back: 'M05-credits',
    status: { field: 'state' },
    tabs: [
      { id: 'credit', label: '1. Credit', bn: '১. ক্রেডিট', icon: '💳', badge: '6' },
      { id: 'approval', label: '2. Computation & Approval', bn: '২. হিসাব ও অনুমোদন', icon: '✍️', badge: '9' }
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
          { name: 'approved_by_id', label: "Approved By", readonly: true },
          { name: 'approved_amount', label: "Amount Approved (BDT)", readonly: true },
          { name: 'applied_at', label: "Applied to Billing At", readonly: true }
        ] }
    ]
  },

  'M05-form-msp-patch-policy': {
    kind: 'model_form',
    model: 'fix.msp.patch.policy',
    title: "Msp Patch Policy",
    back: 'M05-msp-patch-policy',
    tabs: [
      { id: 'policy', label: '1. Policy Scope', bn: '১. পলিসির পরিধি', icon: '📋', badge: '5' },
      { id: 'rules', label: '2. Approval Rules', bn: '২. অনুমোদন নিয়মাবলী', icon: '⚙️', badge: '5' }
    ],
    sections: [
      { tab: 'policy', title: "MSP Patch Policy Governance", note: "Opened from the module's own record set. Every field here is the model's real field.",
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
          { name: 'approved_by_cab', label: "Approved by a CAB Member", readonly: true }
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
  },
  'M05:Managed Estate Device': 'M05-form-estate',
  'M05:On-Call Shift': 'M05-form-oncall',
  'M05:Runbook': 'M05-form-runbook',
  'M05:Patch Update': 'M05-form-patch',
  'M05:Remote Session (consent recorded)': 'M05-form-session',
  'M05:MSP Ticket': 'M05-form-ticket',
  'M05:Change Record': 'M05-form-change',
  'M05:Maintenance Window': 'M05-form-window',
  'M05:__by_model__': {
    'fix.msp.patch.policy': 'M05-form-msp-patch-policy',
    'fix.monitored.asset': 'M05-form-estate',
    'fix.msp.oncall.shift': 'M05-form-oncall',
    'fix.msp.runbook': 'M05-form-runbook',
    'fix.msp.patch.update': 'M05-form-patch',
    'fix.msp.sla.credit': 'M05-form-credit',
    'fix.remote.session': 'M05-form-session',
    'fix.msp.alert': 'M05-form-ticket',
    'fix.msp.change.record': 'M05-form-change',
    'fix.msp.maintenance.window': 'M05-form-window'
  }
};

/* data-entry form chips -> the REAL model forms (the registry's four). */
export const FORM_MODELS = {
  'M05:Remote Session (consent recorded)': 'fix.remote.session',
  'M05:MSP Ticket': 'fix.msp.alert',
  'M05:Change Record': 'fix.msp.change.record',
  'M05:Maintenance Window': 'fix.msp.maintenance.window'
};

/* the module's "+ New" surface: the MSP contract is the module's anchor
 * record — per-device pricing, SLA target, monthly report + credits. */
export const CREATE = {
  M05: { model: 'fix.msp.contract', label: 'MSP Contract' }
};
