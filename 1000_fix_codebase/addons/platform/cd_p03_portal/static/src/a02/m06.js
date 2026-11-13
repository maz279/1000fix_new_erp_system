/** @odoo-module **/
/* A02 · Service Operations — M06 Data Services & Recovery.
 * This fragment REPLACES the base-file M06 block, which described a
 * CORPORATE-AMC module (contracts master list, PM planner — wrong content;
 * registry drift measured 2026-10-27: zero id overlap with the canonical
 * registry). The structure below is the CANONICAL registry M06: 4 groups,
 * 12 screens, 6 KPIs, 5 reports, freg 75 functions in 10 subs.
 *
 * Backend: controllers/a02/m06.py (SURFACES, kpis, 6 REPORTS) over the
 * cd_data_case models — the case journey (custody chain, Z4-only recovery,
 * TOTP step-up access, verified-certificate purge), attempt tracking,
 * sealed media units, cleanroom slots, free evaluations, firm quotations,
 * backup plans with restore tests, and the NIST 800-88 wipe certificates.
 * Every screen is a LIVE surface; the recovered-data inventory lists
 * exactly what the case's attachment register holds. */

export const MODULE = {
  area: 'A02', code: 'M06', en: 'Data Services & Recovery', title: 'M06 · Data Services & Recovery',
  bn: 'ডেটা সেবা ও রিকভারি', icon: '💾',
  desc: 'Data recovery case management, sealed media custody, secure destruction with certificates, backup plans.',
  kpis: [
    { l: 'Active Cases', m: 'active_cases' },
    /* M06 sweep audit 2026-11-06 (D2): rates and durations carry units. */
    { l: 'Recovery Success', m: 'recovery_success', suffix: '%' },
    { l: 'Cleanroom Slots', m: 'cleanroom_slots' },
    { l: 'Destruction Certs MTD', m: 'destruction_certs_mtd' },
    { l: 'Eval Turnaround', m: 'eval_turnaround', suffix: 'h' },
    { l: 'Purge Verifications', m: 'purge_verifications' }
  ],
  groups: [
    { en: 'Recovery Cases', screens: [
      { id: 'M06-cases', en: 'Recovery Cases', bn: 'রিকভারি কেস', t: 'g' },
      { id: 'M06-record', en: 'Case Record (7 specialisms)', bn: 'কেস নথি', t: 'g' },
      { id: 'M06-attempts', en: 'Attempt Tracking', bn: 'প্রচেষ্টা ট্র্যাকিং', t: 'g' }
    ]},
    { en: 'Media Custody', screens: [
      { id: 'M06-custody', en: 'Sealed Media Custody', bn: 'সিলড মিডিয়া', t: 'g' },
      { id: 'M06-cleanroom', en: 'Cleanroom Schedule', bn: 'ক্লিনরুম', t: 'g' },
      { id: 'M06-inventory', en: 'Recovered-Data Inventory', bn: 'উদ্ধার তালিকা', t: 'r' }
    ]},
    { en: 'Quotation & Handover', screens: [
      { id: 'M06-eval', en: 'Free Evaluations', bn: 'ফ্রি মূল্যায়ন', t: 'g' },
      { id: 'M06-quotes', en: 'Firm Quotations', bn: 'চূড়ান্ত কোট', t: 'g' },
      { id: 'M06-handover', en: 'Secure Handover & Purge', bn: 'নিরাপদ হস্তান্তর', t: 'g' }
    ]},
    { en: 'Backup & Destruction', screens: [
      { id: 'M06-backup', en: 'Backup Plans & Tests', bn: 'ব্যাকআপ পরিকল্পনা', t: 'g' },
      { id: 'M06-destroy', en: 'Secure Destruction', bn: 'নিরাপদ ধ্বংস', t: 'g' },
      { id: 'M06-certs', en: 'Destruction Certificates', bn: 'ধ্বংস সনদ', t: 'g' },
      { id: 'M06-access-audit', en: 'Access Audit Log', bn: 'অ্যাক্সেস অডিট লগ', t: 'g' }
    ]}
  ],
  reports: ['Recovery Success by Specialism', 'Case Cycle Time', 'Data Service Revenue', 'Destruction & Purge Audit', 'Backup Restore-Test Compliance'],
  /* M06 sub-module capture (2026-11-13): the registry's four forms plus
   * every step a person performs on a page. Reported: "not all the
   * sub-modules have a relevant data capture button". Measured: pages 6, 7
   * and 10 offered none, page 3 offered only a quote the server refuses
   * before an evaluation (which no page offered), page 5 repeated page 4. */
  forms: ['Recovery Case', 'Media Intake (sealed)', 'Media Custody Move', 'Witnessed Seal Break',
    'Free Evaluation', 'Firm Quotation', 'Recovery Attempt', 'Cleanroom Slot Booking', 'Attempt Outcome',
    'Recovered-Data Inventory Entry', 'Handover Preparation', 'Secure Handover', 'Secure Purge',
    'Backup Plan', 'Destruction Request (dual control)', 'Named Z4 Staff Assignment'],
  cross: ['M36 recovery quotations', 'M24 evidence certificates', 'M18 e-waste routing', 'M01 data-service orders'],
  freg: {
    src: 75,
    sub: [
      ['1', 'Case Management (7 specialisms)', 12, { model: 'fix.data.recovery.case', cols: ['name', 'customer_id', 'specialism', 'media_type', 'state'], screens: ['M06-cases', 'M06-record'], reports: ['Recovery Success by Specialism', 'Case Cycle Time'], forms: ['Recovery Case'] }],
      /* 2 FR-DTS-002 / BRU-DTS-01: intake under seal, every move, and a seal
       * opened only with a second person as witness */
      ['2', 'Media Chain of Custody', 11, { model: 'fix.data.media.unit', cols: ['seal_number', 'case_id', 'media_label', 'location', 'seal_state'], screens: ['M06-custody', 'M06-cleanroom'], reports: [], forms: ['Media Intake (sealed)', 'Media Custody Move', 'Witnessed Seal Break'] }],
      /* 3 FR-DTS-003: the free evaluation comes first - a quote is refused
       * until an evaluation is completed with data to recover */
      ['3', 'Evaluation & Quotation', 8, { model: 'fix.data.quote', cols: ['name', 'case_id', 'amount', 'valid_until', 'state'], screens: ['M06-eval', 'M06-quotes'], reports: ['Data Service Revenue'], forms: ['Free Evaluation', 'Firm Quotation'], create: 'M06-form-eval' }],
      /* 4 FR-DTS-004 / 025: the technique tried, and the cleanroom slot an
       * invasive technique needs */
      ['4', 'Methodology Logging', 6, { model: 'fix.data.recovery.attempt', cols: ['case_id', 'method', 'donor_part_used', 'imaged_pct', 'notes'], screens: ['M06-attempts', 'M06-cleanroom'], reports: ['Recovery Success by Specialism'], forms: ['Recovery Attempt', 'Cleanroom Slot Booking'] }],
      /* 5: what each attempt achieved - closing an open attempt with its outcome */
      ['5', 'Attempt Tracking', 5, { model: 'fix.data.recovery.attempt', cols: ['case_id', 'sequence', 'started_at', 'finished_at', 'outcome'], screens: ['M06-attempts'], reports: ['Recovery Success by Specialism', 'Case Cycle Time'], forms: ['Attempt Outcome'], create: 'M06-form-attempt-outcome' }],
      /* 6 FR-DTS-006: files and GB recovered, never names; recorded by the
       * case's staff during recovery, frozen at handover */
      ['6', 'Recovered-Data Inventory', 5, { model: 'fix.data.recovery.case', cols: ['name', 'recovered_files_count', 'recovered_volume_gb', 'image_sha256_hash', 'state'], screens: ['M06-inventory'], reports: ['Recovery Success by Specialism'], forms: ['Recovered-Data Inventory Entry'], create: 'M06-form-inventory', domain: [['state', 'in', ['recovering', 'recovered', 'handover']]] }],
      /* 7 FR-DTS-007 / 008: recipient and target drive, the verified
       * handover against the signed receipt, then the purge on a verified
       * wipe certificate */
      ['7', 'Secure Handover & Purge', 7, { model: 'fix.data.recovery.case', cols: ['name', 'customer_id', 'purge_certificate_id', 'residency_zone', 'state'], screens: ['M06-handover'], reports: ['Destruction & Purge Audit'], forms: ['Handover Preparation', 'Secure Handover', 'Secure Purge'], create: 'M06-form-handover', domain: [['state', 'in', ['handover', 'purged']]] }],
      ['8', 'Backup Plans', 6, { model: 'fix.data.backup.plan', cols: ['name', 'customer_id', 'plan_type', 'rpo_hours', 'next_test_due'], screens: ['M06-backup'], reports: ['Backup Restore-Test Compliance'], forms: ['Backup Plan'] }],
      ['9', 'Secure Destruction', 9, { model: 'fix.data.wipe.certificate', cols: ['name', 'serial_number', 'method', 'sanitization_status', 'certified_at'], screens: ['M06-destroy', 'M06-certs'], reports: ['Destruction & Purge Audit'], forms: ['Destruction Request (dual control)'] }],
      /* 10 FR-DTS-009 / BRU-DTS-02: the access log writes itself; what a
       * person captures is WHO may work the case - its named staff */
      ['10', 'Access Control & Audit', 6, { model: 'fix.z4.access.audit', cols: ['case_id', 'user_name', 'access_type', 'access_time', 'step_up_verified'], screens: ['M06-access-audit'], reports: ['Destruction & Purge Audit'], forms: ['Named Z4 Staff Assignment'], create: 'M06-form-staff' }]
    ]
  }
};

/* In-workspace data screens over the whitelisted cd_data_case models. */
export const SCREENS = {
  /* Every opening of a recovery case's data is logged with its accessor,
   * purpose and step-up check (Z4). The sub-module 'Access Control & Audit'
   * listed the CASES instead: the log had no screen (2026-11-12). */
  'M06-access-audit': { kind: 'model_list', model: 'fix.z4.access.audit', create: false,
    cols: ['access_time', 'case_id', 'user_name', 'access_type', 'purpose', 'step_up_verified', 'ip_address'],
    empty: 'No access to recovered data has been logged yet. Each time the data of a case is opened, the accessor, purpose and second-factor check are recorded here automatically; entries cannot be typed in or changed.' },
  /* --- Recovery Cases --- */
  'M06-cases': { kind: 'model_list', model: 'fix.data.recovery.case',
    cols: ['name', 'customer_id', 'media_type', 'specialism', 'residency_zone', 'attempt_count', 'audit_count', 'state'],
    stateField: 'state',
    /* A02 audit M06: every lifecycle step is a server action (state, zone,
     * consent and purge certificate are workflow-owned, never typed). */
    actions: [
      { m: 'action_take_custody', l: 'Take Custody', ask: 'Custody handler name', kwarg: 'handler' },
      { m: 'action_log_custody_transfer', l: 'Log Custody Transfer', ask: 'Handed to (name)', kwarg: 'handler' },
      { m: 'action_route_to_z4', l: 'Route to Z4' },
      { m: 'action_record_destructive_consent', l: 'Record Destructive Consent', ask: 'Customer OTP / portal consent reference', kwarg: 'reference' },
      { m: 'action_assign_me', l: 'Assign Me as Technician' },
      { m: 'action_assign_staff', l: 'Assign Z4 Custodian', ask: 'Z4 custodian login', kwarg: 'custodian' },
      { m: 'action_record_image', l: 'Record Forensic Image', ask: 'Source SHA-256 and image SHA-256 (space separated)', kwarg: 'hashes' },
      { m: 'action_verify_image', l: 'Verify Image (second person)', ask: 'Image SHA-256 you recomputed', kwarg: 'recomputed_hash' },
      { m: 'action_start_recovery', l: 'Start Recovery' },
      { m: 'action_recovered', l: 'Mark Recovered' },
      { m: 'action_confirm_target_serial', l: 'Confirm Target Drive Serial', ask: 'Serial read off the target drive', kwarg: 'serial' },
      { m: 'action_request_handover_otp', l: 'Send Handover Code' },
      { m: 'action_mark_unrecoverable', l: 'Mark Unrecoverable', ask: 'Reason (no data, no fee)', kwarg: 'reason' },
      { m: 'action_handover', l: 'Secure Handover', ask: 'Recipient one-time code or ID number', kwarg: 'verification' },
      { m: 'action_purge', l: 'Purge (Verified Cert)', ask: 'Wipe certificate reference (blank = the verified one for this media serial)', kwarg: 'certificate' },
      { m: 'action_close', l: 'Close Case' }
    ] },
  'M06-record': { kind: 'model_list', model: 'fix.data.recovery.case', create: true,
    cols: ['name', 'customer_id', 'specialism', 'received_at', 'state', 'purge_certificate_id'],
    domain: [['state', '!=', 'closed']] },
  'M06-attempts': { kind: 'model_list', model: 'fix.data.recovery.attempt', create: true,
    cols: ['case_id', 'method', 'specialism', 'started_at', 'finished_at', 'outcome', 'notes'],
    stateField: 'outcome',
    actions: [{ m: 'action_finish', l: 'Finish Attempt', ask: 'Outcome (success/partial/failed/media_damaged)', kwarg: 'outcome' }] },

  /* --- Media Custody --- */
  'M06-custody': { kind: 'model_list', model: 'fix.data.media.unit', create: true,
    cols: ['seal_number', 'case_id', 'media_label', 'location', 'seal_state', 'holder'],
    stateField: 'location',
    actions: [
      { m: 'action_transfer', l: 'Move Media', ask: 'Location (z4_lab/cleanroom/vault/reception)', kwarg: 'location' },
      { m: 'action_break_seal_with_witness', l: 'Break Seal (Witnessed)', ask: 'Witness login (a second person, not you)', kwarg: 'witness_user_id' },
      { m: 'action_return', l: 'Return to Customer' }
    ] },
  'M06-cleanroom': { kind: 'model_list', model: 'fix.data.cleanroom.slot',
    cols: ['start_at', 'end_at', 'purpose', 'iso_class', 'case_id', 'technician_id', 'state'],
    stateField: 'state',
    actions: [
      { m: 'action_use', l: 'Mark Used' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M06-inventory': { kind: 'table_report', module: 'M06', report: 'recovered_inventory', period: false },

  /* --- Quotation & Handover --- */
  'M06-eval': { kind: 'model_list', model: 'fix.data.evaluation', create: true,
    cols: ['case_id', 'received_at', 'verdict', 'recoverability_pct', 'recommended_specialism', 'evaluated_at', 'eval_hours'],
    actions: [{ m: 'action_complete', l: 'Complete Evaluation' }] },
  'M06-quotes': { kind: 'model_list', model: 'fix.data.quote',
    cols: ['name', 'case_id', 'amount', 'description', 'valid_until', 'state'],
    stateField: 'state',
    actions: [
      { m: 'action_send', l: 'Send Quote' },
      { m: 'action_accept', l: 'Record Customer Acceptance', ask: 'Customer OTP / portal acceptance reference (blank = the signed quotation attached to the quote)', kwarg: 'acceptance_reference' },
      { m: 'action_decline', l: 'Decline' },
      { m: 'action_requote', l: 'Re-quote (new version)' },
      /* A02 audit B1: a re-quote that raises the price is approved by the lab manager in the M63 inbox */
      { m: 'action_request_approval', l: 'Request Price-Change Approval', ask: 'Why the price rises', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  /* the console = what is awaiting secure handover / purge right now */
  'M06-handover': { kind: 'model_list', model: 'fix.data.recovery.case', create: false,
    cols: ['name', 'customer_id', 'specialism', 'state', 'residency_zone', 'purge_certificate_id', 'audit_count'],
    domain: [['state', 'in', ['recovered', 'handover']]],
    stateField: 'state',
    /* M06 sub-module capture (2026-11-13): the handover is refused until the
     * target drive is confirmed and the recipient verified; both steps were
     * only on the Recovery Cases list, so the console could not hand over */
    actions: [
      { m: 'action_confirm_target_serial', l: 'Confirm Target Drive Serial', ask: 'Serial read off the target drive', kwarg: 'serial' },
      { m: 'action_request_handover_otp', l: 'Send Handover Code' },
      { m: 'action_handover', l: 'Secure Handover', ask: 'Recipient one-time code or ID number', kwarg: 'verification' },
      { m: 'action_purge', l: 'Purge (Verified Cert)', ask: 'Wipe certificate reference (blank = the verified one for this media serial)', kwarg: 'certificate' },
      { m: 'action_access_recovered_data', l: 'Z4 Access (TOTP)', ask: '6-digit authenticator code (SC-002)', kwarg: 'step_up_token' }
    ] },

  /* --- Backup & Destruction --- */
  'M06-backup': { kind: 'model_list', model: 'fix.data.backup.plan', create: true,
    cols: ['name', 'customer_id', 'plan_type', 'rpo_hours', 'rto_hours', 'last_test_date', 'last_test_result', 'next_test_due', 'compliant'],
    actions: [
      { m: 'action_log_test', l: 'Log Restore Test', ask: 'Result (passed/partial/failed)', kwarg: 'result' }
    ] },
  /* the destruction console = certificates awaiting verification */
  'M06-destroy': { kind: 'model_list', model: 'fix.data.wipe.certificate', create: true,
    cols: ['name', 'device_id', 'serial_number', 'method', 'tool_name', 'sanitization_status', 'certified_at'],
    domain: [['sanitization_status', '=', 'pending_verification']],
    stateField: 'sanitization_status',
    actions: [
      { m: 'action_verify', l: 'Verify Evidence' },
      { m: 'action_mark_failed', l: 'Mark Failed' }
    ] },
  'M06-certs': { kind: 'model_list', model: 'fix.data.wipe.certificate', create: false,
    cols: ['name', 'device_id', 'serial_number', 'method', 'sanitization_status', 'verified_by_id', 'verified_at', 'verification_hash', 'certified_at'],
    stateField: 'sanitization_status' }
};

/* built-in report chips -> their OWN computed pack (backend REPORTS exist) */
export const REPORT_ROUTES = {
  "M06:Recovery Success by Specialism": "M06-rpt-success",
  "M06:Case Cycle Time": "M06-rpt-cycle",
  "M06:Data Service Revenue": "M06-rpt-revenue",
  "M06:Destruction & Purge Audit": "M06-rpt-destruction",
  "M06:Backup Restore-Test Compliance": "M06-rpt-backup"
};

Object.assign(SCREENS, {
  'M06-rpt-success': { kind: 'table_report', module: 'M06', report: 'recovery_success_by_specialism', title: 'Recovery Success by Specialism', period: false },
  'M06-rpt-cycle': { kind: 'table_report', module: 'M06', report: 'case_cycle_time', title: 'Case Cycle Time', period: false },
  'M06-rpt-revenue': { kind: 'table_report', module: 'M06', report: 'data_service_revenue', title: 'Data Service Revenue', period: true },
  'M06-rpt-destruction': { kind: 'table_report', module: 'M06', report: 'destruction_purge_audit', title: 'Destruction & Purge Audit', period: false },
  'M06-rpt-backup': { kind: 'table_report', module: 'M06', report: 'backup_restore_compliance', title: 'Backup Restore-Test Compliance', period: false }
});

/* data-entry form chips -> the REAL model forms (the registry's four). */
export const FORM_MODELS = {
  'M06:Recovery Case': 'fix.data.recovery.case',
  'M06:Media Intake (sealed)': 'fix.data.media.unit',
  'M06:Firm Quotation': 'fix.data.quote',
  'M06:Destruction Request (dual control)': 'fix.data.wipe.certificate'
};

/* ============ D365 IN-WORKSPACE FORMS (M06 re-audit v3) ========
 * The registry's four chips + every creatable grid: Dynamics-365
 * record forms inside the workspace - never an Odoo dialog. */
Object.assign(SCREENS, {
  'M06-form-case': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Recovery Case',
    back: 'M06-cases',
    status: { field: 'state', labels: {
      new: 'New', custody: 'In Custody', recovering: 'Recovering',
      recovered: 'Recovered', handover: 'Handover', purged: 'Purged',
      closed: 'Closed', unrecoverable: 'Unrecoverable' } },
    tabs: [
      { id: 'case', label: '1. Case Identity & Media', bn: '১. কেস তথ্য ও মিডিয়া', icon: '💾', badge: '9' },
      { id: 'forensic', label: '2. Forensic Triage & Hash', bn: '২. ফরেনসিক ট্রায়াজ ও হ্যাশ', icon: '🔍', badge: '7' },
      { id: 'custody', label: '3. Chain of Custody', bn: '৩. কাস্টডি লেজার', icon: '🔒', badge: '3' },
      { id: 'security', label: '4. Z4 TOTP & Secure Purge', bn: '৪. জেড৪ টিওটিপি ও ধ্বংস', icon: '🛡️', badge: '7' },
      { id: 'handover', label: '5. Z4 Staff, Imaging & Handover', bn: '৫. জেড৪ কর্মী, ইমেজ ও হস্তান্তর', icon: '🤝', badge: '15' }
    ],
    sections: [
      { tab: 'case', title: 'Case Registration & Media Classification', note: 'Intake, custody, recovery, secure handover with purge after a verified certificate. Z4 residency routing is statutory (SC-002).',
        fields: [
          { name: 'name', required: true, label: 'Case Reference', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'device_id', label: 'Device' },
          { name: 'media_type', required: true, label: 'Storage Media Type' },
          { name: 'media_serial_number', label: 'Storage Media Factory S/N (wipe certificate key)' },
          { name: 'specialism', label: 'Specialism (7 Disciplines)' },
          { name: 'residency_zone', label: 'Residency Zone (set by Route to Z4)', readonly: true },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', label: 'Workflow State', readonly: true }
        ] },
      { tab: 'forensic', title: 'Forensic Write-Blocking & Cryptographic Hash',
        fields: [
          { name: 'capacity_gb', label: 'Raw Media Capacity (GB)' },
          { name: 'form_factor', label: 'Storage Media Form Factor' },
          { name: 'interface_type', label: 'Physical Interface Protocol' },
          { name: 'firmware_revision', label: 'Controller / ROM Firmware Version' },
          { name: 'write_blocker_serial', label: 'Hardware Write-Blocker S/N' },
          { name: 'image_sha256_hash', label: 'Bit-Stream Forensic Clone SHA-256 Digest (set by Record Image)', readonly: true },
          { name: 'donor_drive_serial', label: 'Matched Donor Drive / Head Stack S/N' }
        ] },
      { tab: 'custody', title: 'Single-Source Append-Only Chain of Custody Log',
        fields: [
          { name: 'received_at', label: 'Media Received At', readonly: true },
          { name: 'custody_chain', label: 'Append-Only Chain-of-Custody Log', type: 'text', readonly: true },
          { name: 'attempt_count', label: 'Recovery Attempts Logged', readonly: true }
        ] },
      { tab: 'security', title: 'Z4 TOTP Step-Up Access & Verified Purge (SC-002)',
        fields: [
          { name: 'audit_count', label: 'Z4 Step-Up Access Audits', readonly: true },
          { name: 'purge_certificate_id', label: 'Verified NIST 800-88 Purge Certificate (set by Purge)', readonly: true },
          { name: 'nda_reference', label: 'PDPA / Corporate NDA Reference' },
          { name: 'nda_attachment_id', label: 'Signed Confidentiality & NDA Document (PDF)' },
          { name: 'destructive_consent_at', label: 'Destructive-Work Consent Recorded At', readonly: true },
          { name: 'destructive_consent_reference', label: 'Customer Consent Reference (OTP / Portal)', readonly: true },
          { name: 'destructive_consent_by_id', label: 'Consent Recorded By', readonly: true }
        ] },
      /* A02 audit M06-P2: named Z4 staff, imaging as a verified step, and the
       * handover to a verified recipient against a receipt */
      { tab: 'handover', title: 'Named Z4 Staff, Verified Image & Verified Handover',
        note: 'Only the assigned technician and Z4 custodian work the recovered data. A case is marked recovered on a verified image; handover needs the recipient (the customer or a contact), their one-time code or ID number, a signed receipt attached to the case (named receipt...) and the target drive serial confirmed.',
        fields: [
          { name: 'assigned_technician_id', label: 'Assigned Technician', readonly: true },
          { name: 'z4_custodian_id', label: 'Assigned Z4 Custodian', readonly: true },
          { name: 'image_source_sha256', label: 'Source Media SHA-256', readonly: true },
          { name: 'imaged_by_id', label: 'Imaged By', readonly: true },
          { name: 'image_verified_at', label: 'Image Verified At', readonly: true },
          { name: 'image_verified_by_id', label: 'Image Verified By', readonly: true },
          { name: 'encrypted_target_serial', label: 'Encrypted Handover Target Drive S/N' },
          { name: 'handover_recipient_id', label: 'Handover Recipient (customer or contact)' },
          { name: 'target_serial_confirmed_at', label: 'Target Drive Serial Confirmed At', readonly: true },
          { name: 'handover_verification_method', label: 'Recipient Verified By', readonly: true },
          { name: 'handover_verification_ref', label: 'Verification Reference', readonly: true },
          { name: 'handover_receipt_attachment_id', label: 'Signed Handover Receipt', readonly: true },
          { name: 'handover_at', label: 'Handed Over At', readonly: true },
          { name: 'retention_until', label: 'Retain Recovered Data Until', readonly: true },
          { name: 'retention_flagged_at', label: 'Retention Overdue Flagged At', readonly: true }
        ] }
    ]
  },

  'M06-form-media': {
    kind: 'model_form',
    model: 'fix.data.media.unit',
    title: 'Media Intake (sealed)',
    back: 'M06-custody',
    status: { field: 'seal_state', labels: {
      sealed: 'Sealed', opened_in_lab: 'Opened in Lab', broken_on_receipt: 'Broken on Receipt' } },
    tabs: [
      { id: 'bag', label: '1. Sealed Evidence Bag', bn: '১. সিলড মিডিয়া ব্যাগ', icon: '🔒', badge: '6' },
      { id: 'dual', label: '2. Dual-Custody Unsealing', bn: '২. যৌথ স্বাক্ষরে সিল খোলা', icon: '👥', badge: '5' }
    ],
    sections: [
      { tab: 'bag', title: 'Tamper-Evident Bag & Storage Location', note: 'Chain of custody: moves between reception, cleanroom, vault and Z4 lab are logged.',
        fields: [
          { name: 'case_id', required: true, label: 'Recovery Case', domain: [['state', 'not in', ['purged', 'closed', 'unrecoverable']]],
            emptyNote: 'No open recovery case yet. Open the case first (+ New Recovery Case), then book its sealed media in here.' },
          { name: 'seal_number', required: true, label: 'Tamper-Evident Bag / Seal Number' },
          { name: 'media_label', label: 'Drive Make / Model / Label' },
          { name: 'media_type', label: 'Media Type', readonly: true },
          { name: 'location', label: 'Physical Storage Location (set by Move Media)', readonly: true },
          { name: 'holder', label: 'Current Physical Custodian', readonly: true }
        ] },
      { tab: 'dual', title: 'Dual-Custody Witness Gate & Write-Blocker (FLAW-06.1)',
        note: 'Unsealing evidence in the lab strictly requires a second witness user sign-off.',
        fields: [
          { name: 'seal_state', label: 'Seal Integrity State (set by Break Seal)', readonly: true },
          { name: 'witness_user_id', label: 'Second Dual-Custody Witness User', readonly: true },
          { name: 'witness_verified_at', label: 'Witness Verified Timestamp', readonly: true },
          { name: 'write_blocker_serial', label: 'Hardware Write-Blocker S/N' },
          { name: 'source_sha256_hash', label: 'Intake SHA-256 Hash' },
          { name: 'evidence_photo_attachment_id', label: 'Sealed Bag Photograph Proof' }
        ] }
    ]
  },

  'M06-form-quote': {
    kind: 'model_form',
    model: 'fix.data.quote',
    title: 'Firm Quotation',
    back: 'M06-quotes',
    status: { field: 'state', labels: {
      draft: 'Draft', sent: 'Sent', accepted: 'Accepted', declined: 'Declined' } },
    tabs: [
      { id: 'quote', label: '1. Quotation Scope', bn: '১. কোটেশন বিবরণ', icon: '📄', badge: '5' },
      { id: 'economics', label: '2. No-Data-No-Fee Economics', bn: '২. নো-ডেটা-নো-ফি ও চার্জ', icon: '💰', badge: '11' }
    ],
    sections: [
      { tab: 'quote', title: 'Recovery Quotation Header', note: 'A firm quote for the recovery work; free evaluation verdict feeds the scope.',
        fields: [
          { name: 'name', required: true, label: 'Quote Reference', readonly: true },
          { name: 'case_id', required: true, label: 'Data Recovery Case', domain: [['evaluation_ids', '!=', false], ['state', 'not in', ['purged', 'closed', 'unrecoverable']]],
            emptyNote: 'No case has a free evaluation yet. A quote prices a completed evaluation that found data to recover: record the Free Evaluation first.' },
          { name: 'description', label: 'Work Scope & Deliverable Files' },
          { name: 'valid_until', label: 'Quotation Valid Until' },
          { name: 'state', label: 'Quote Lifecycle State', readonly: true }
        ] },
      { tab: 'economics', title: 'No-Data-No-Fee Structure & Non-Refundable Donor Parts',
        fields: [
          { name: 'amount', required: true, label: 'Recovery Fee (BDT)' },
          { name: 'donor_fee_bdt', label: 'Non-Refundable Donor Parts Fee (BDT)' },
          { name: 'no_data_no_fee_applies', label: 'No-Data-No-Fee Guarantee Applicable' },
          { name: 'currency_id', label: 'Currency', readonly: true },
          { name: 'signed_quote_attachment_id', label: 'Customer Signed Quotation PDF', readonly: true },
          { name: 'acceptance_channel', label: 'Customer Acceptance Channel', readonly: true },
          { name: 'customer_acceptance_reference', label: 'Customer OTP / Portal Reference', readonly: true },
          { name: 'accepted_by_id', label: 'Acceptance Recorded By', readonly: true },
          { name: 'supersedes_id', label: 'Re-quote Of', readonly: true },
          { name: 'approval_state', label: 'Price Change Approval (M63 inbox)', readonly: true },
          { name: 'requote_approved_by_id', label: 'Price Change Approved By', readonly: true }
        ] }
    ]
  },

  'M06-form-wipe': {
    kind: 'model_form',
    model: 'fix.data.wipe.certificate',
    title: 'Destruction Request (dual control)',
    back: 'M06-destroy',
    status: { field: 'sanitization_status', labels: {
      pending_verification: 'Pending Verification', verified: 'Verified',
      failed: 'Failed' } },
    tabs: [
      { id: 'media', label: '1. Media & Sanitization', bn: '১. মিডিয়া ও ডিস্ট্রাকশন', icon: '🗑️', badge: '6' },
      { id: 'nist', label: '2. NIST 800-88 & Dual-Sign', bn: '২. নিস্ট ৮০০-৮৮ ও যৌথ অনুমোদন', icon: '📜', badge: '7' }
    ],
    sections: [
      { tab: 'media', title: 'Media Sanitization & Overwrite Tool', note: 'Dual control: the certifying technician records the wipe; a second verifier confirms.',
        fields: [
          { name: 'name', required: true, label: 'Certificate Reference', readonly: true },
          { name: 'device_id', label: 'Registered Hardware Asset' },
          { name: 'serial_number', required: true, label: 'Media Serial Number' },
          { name: 'method', required: true, label: 'NIST 800-88 Method (Purge/Clear/Destroy)' },
          { name: 'tool_name', label: 'Sanitization Tool & Version' },
          { name: 'technician_id', label: 'Certifying Technician', readonly: true }
        ] },
      { tab: 'nist', title: 'Dual-Control Verification & SHA-256 Certificate',
        fields: [
          { name: 'sector_count', label: 'Total Overwritten Sectors' },
          { name: 'duration_seconds', label: 'Sanitization Duration (Seconds)' },
          { name: 'sanitization_status', label: 'Sanitization Status (set by Verify Evidence)', readonly: true },
          { name: 'verified_by_id', label: 'Independent Dual-Control Verifier', readonly: true },
          { name: 'verified_at', label: 'Verification Timestamp', readonly: true },
          { name: 'verification_hash', label: 'Audit Verification Hash (SHA-256)', readonly: true },
          { name: 'evidence_intact', label: 'Evidence Unchanged Since Verification', readonly: true }
        ] }
    ]
  },

  'M06-form-attempt': {
    kind: 'model_form',
    model: 'fix.data.recovery.attempt',
    title: 'Recovery Attempt',
    back: 'M06-attempts',
    status: { field: 'outcome', labels: {
      in_progress: 'In Progress', success: 'Success', partial: 'Partial',
      failed: 'Failed', media_damaged: 'Media Damaged' } },
    tabs: [
      { id: 'attempt', label: '1. Methodology & Cleanroom', bn: '১. পদ্ধতি ও ক্লিনরুম', icon: '🔬', badge: '7' },
      { id: 'outcome', label: '2. Telemetry & Outcome', bn: '২. ফলাফল ও টেলিমেট্রি', icon: '📊', badge: '5' }
    ],
    sections: [
      { tab: 'attempt', title: 'Lab Recovery Methodology & Interlock Verification (FLAW-06.2)', note: 'Invasive methods require passing ISO Class 5 cleanroom environmental interlocks.',
        fields: [
          { name: 'case_id', required: true, label: 'Data Recovery Case', domain: [['state', '=', 'recovering']],
            emptyNote: 'No case is in recovery. A case enters recovery (Start Recovery) after custody, Z4 routing, a completed evaluation and an accepted quote; only its assigned technician or Z4 custodian logs attempts.' },
          { name: 'method', required: true, label: 'Recovery Method' },
          { name: 'cleanroom_slot_id', label: 'Cleanroom ISO-5 Slot (Required for head_swap/chip_off/donor_parts)' },
          { name: 'destructive', label: 'Destructive / Invasive (needs consent + cleanroom)', readonly: true },
          { name: 'donor_part_used', label: 'Donor Part / Head Assembly S/N' },
          { name: 'started_at', required: true, label: 'Attempt Started At' },
          { name: 'finished_at', label: 'Attempt Finished At', readonly: true }
        ] },
      { tab: 'outcome', title: 'Recovery Sector Map & Attempt Report',
        fields: [
          { name: 'outcome', label: 'Attempt Outcome Verdict (set by Finish Attempt)', readonly: true },
          { name: 'bad_sectors_encountered', label: 'Unreadable Bad Sectors' },
          { name: 'imaged_pct', label: 'Sectors Successfully Imaged (%)' },
          { name: 'notes', label: 'Technician Engineering Log', type: 'text' },
          { name: 'attempt_report_attachment_id', label: 'Clone Map / Sector Telemetry PDF' }
        ] }
    ]
  },

  'M06-form-cleanroom': {
    kind: 'model_form',
    model: 'fix.data.cleanroom.slot',
    title: 'Cleanroom Slot',
    back: 'M06-cleanroom',
    status: { field: 'state', labels: {
      planned: 'Planned', used: 'Used', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'booking', label: '1. Schedule & Purpose', bn: '১. সময় ও উদ্দেশ্য', icon: '📅', badge: '5' },
      { id: 'telemetry', label: '2. ISO 14644-1 Environmental Telemetry', bn: '২. পরিবেশগত সেন্সর অডিট', icon: '🌡️', badge: '6' }
    ],
    sections: [
      { tab: 'booking', title: 'Cleanroom Slot Reservation', note: 'ISO-class bench time reserved for head assembly swaps and platter transfers.',
        fields: [
          { name: 'case_id', label: 'Assigned Recovery Case', domain: [['state', 'not in', ['purged', 'closed', 'unrecoverable']]] },
          { name: 'technician_id', label: 'Cleanroom Certified Technician' },
          { name: 'purpose', required: true, label: 'Invasive Operation Purpose' },
          { name: 'iso_class', required: true, label: 'ISO Cleanroom Standard (Class 5 / Class 7)' },
          { name: 'start_at', required: true, label: 'Scheduled Start' },
          { name: 'end_at', required: true, label: 'Scheduled End' }
        ] },
      { tab: 'telemetry', title: 'Particle Counter & Laminar Airflow Interlock (FLAW-06.2)',
        note: 'ISO Class 5 mandates <= 100 particles/ft3 (>=0.5um) and 0.35-0.55 m/s laminar airflow.',
        fields: [
          { name: 'particle_count_per_ft3', required: true, label: 'Particle Count (>=0.5um / ft3)' },
          { name: 'laminar_airflow_mps', required: true, label: 'Laminar Airflow Velocity (m/s)' },
          { name: 'temperature_c', label: 'Cleanroom Temperature (°C)' },
          { name: 'humidity_pct', label: 'Relative Humidity (%)' },
          { name: 'interlock_passed', label: 'Environmental Interlock Passed', readonly: true },
          { name: 'state', label: 'Slot Booking State', readonly: true }
        ] }
    ]
  },

  'M06-form-eval': {
    kind: 'model_form',
    model: 'fix.data.evaluation',
    title: 'Free Evaluation',
    back: 'M06-eval',
    status: { field: 'verdict', labels: {
      recoverable: 'Recoverable', partial: 'Partially Recoverable',
      unrecoverable: 'Unrecoverable', no_media_damage: 'No Media Damage' } },
    tabs: [
      { id: 'eval', label: '1. Lab Diagnostic Findings', bn: '১. প্রাথমিক পরীক্ষা', icon: '🔍', badge: '5' },
      { id: 'verdict', label: '2. Confidence & Donor Parts', bn: '২. সম্ভাবনা ও ড্রাইভ যন্ত্রাংশ', icon: '🎯', badge: '6' }
    ],
    sections: [
      { tab: 'eval', title: 'Free Intake Evaluation Diagnostics', note: 'Free intake diagnostic evaluation shaping turnaround KPI and quotation.',
        fields: [
          { name: 'case_id', required: true, label: 'Recovery Case', domain: [['state', 'not in', ['purged', 'closed', 'unrecoverable']]],
            emptyNote: 'No open recovery case yet. Open the case first (+ New Recovery Case); its free evaluation is recorded here.' },
          { name: 'received_at', required: true, label: 'Media Received At' },
          { name: 'evaluated_at', label: 'Evaluation Completed At', readonly: true },
          { name: 'eval_hours', label: 'Evaluation Turnaround (Hours)', readonly: true },
          { name: 'findings', label: 'Technical Diagnostic Observations', type: 'text' }
        ] },
      { tab: 'verdict', title: 'Recoverability Confidence & Donor Part Estimation',
        fields: [
          { name: 'verdict', required: true, label: 'Recoverability Verdict' },
          { name: 'recoverability_pct', label: 'Recoverability Confidence Estimate (%)' },
          { name: 'recommended_specialism', label: 'Recommended Recovery Discipline' },
          { name: 'donor_required', label: 'Matching Donor Drive Required' },
          { name: 'donor_estimated_cost_bdt', label: 'Estimated Donor Part Cost (BDT)' },
          { name: 'evaluation_report_attachment_id', label: 'Evaluation Diagnostic PDF' }
        ] }
    ]
  },

  'M06-form-backup': {
    kind: 'model_form',
    model: 'fix.data.backup.plan',
    title: 'Backup Plan',
    back: 'M06-backup',
    tabs: [
      { id: 'plan', label: '1. SLA & Architecture', bn: '১. ব্যাকআপ আর্কিটেকচার', icon: '💾', badge: '6' },
      { id: 'compliance', label: '2. WORM Encryption & Restore Drill', bn: '২. নিরাপত্তা ও রিস্টোর ড্রিল', icon: '🛡️', badge: '7' }
    ],
    sections: [
      { tab: 'plan', title: 'Enterprise Backup Strategy (3-2-1 Rule)', note: 'RPO/RTO targets and restore-test cadence; compliance is measured by restore tests.',
        fields: [
          { name: 'name', required: true, label: 'Plan Name' },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'device_id', label: 'Primary Data Server / Device' },
          { name: 'plan_type', required: true, label: 'Architecture Model (3-2-1 / Hybrid / WORM)' },
          { name: 'rpo_hours', label: 'Recovery Point Objective - RPO (Hours)' },
          { name: 'rto_hours', label: 'Recovery Time Objective - RTO (Hours)' }
        ] },
      { tab: 'compliance', title: 'Immutability, AES-256 Encryption & Disaster Recovery Drill',
        fields: [
          { name: 'encryption_standard', label: 'Cryptographic Encryption Standard' },
          { name: 'immutable_worm_enabled', label: 'Immutable WORM / Object Lock Active' },
          { name: 'offsite_vault_location', label: 'Offsite Cloud / Cold Vault Location' },
          { name: 'test_frequency_days', label: 'Mandatory Restore Test Frequency (Days)' },
          { name: 'next_test_due', label: 'Next Restore Verification Due Date', readonly: true },
          { name: 'compliant', label: 'Compliance Audit Status', readonly: true },
          { name: 'dr_runbook_attachment_id', label: 'DR Runbook / Verification Certificate' }
        ] }
    ]
  }
});

/* ============ M06 SUB-MODULE CAPTURE (2026-11-13) ==================
 * The steps a person performs on an EXISTING case, media unit or attempt.
 * Each picks its record first (step 1), then runs the workflow method that
 * checks the state, the role and the named staff (`saveAction`): these
 * fields are guarded, so a plain write would be refused. */
const OPEN_CASE = [['state', 'not in', ['purged', 'closed', 'unrecoverable']]];
const INTERNAL_USER = [['share', '=', false]];
Object.assign(SCREENS, {
  'M06-form-media-move': {
    kind: 'model_form',
    model: 'fix.data.media.unit',
    title: 'Media Custody Move',
    newLabel: 'Record a Media Custody Move',
    back: 'M06-custody',
    status: { field: 'seal_state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the sealed media unit that is moving',
      note: 'Sealed media still held by the lab.',
      search: 'Search seal or bag number',
      choose: 'Move this unit',
      cols: ['seal_number', 'case_id', 'media_label', 'location', 'holder'],
      domain: [['location', 'not in', ['returned_to_customer', 'destroyed']]],
      empty: 'The lab holds no sealed media. Book media in first with + New Media Intake (sealed).'
    },
    saveAction: {
      method: 'action_transfer', label: 'Record Move',
      done: 'Move recorded in the case chain of custody',
      kwargs: { location: 'location' }
    },
    sections: [
      { title: 'Step 2 of 2: New Location (FR-DTS-002)',
        note: 'You are recorded as the person who moved it, with the time, in the case chain of custody, which cannot be edited. Returning media to the customer is the Return to Customer action on Sealed Media Custody; destruction is certified on a wipe certificate, never by a move.',
        fields: [
          { name: 'seal_number', label: 'Seal / Bag Number', readonly: true },
          { name: 'case_id', label: 'Recovery Case', readonly: true },
          { name: 'media_label', label: 'Drive Make / Model / Label', readonly: true },
          { name: 'holder', label: 'Held By Now', readonly: true },
          /* an INPUT here: saveAction carries it to action_transfer */
          { name: 'location', required: true, label: 'Move To', readonly: true,
            choices: [['reception', 'Reception'], ['z4_lab', 'Z4 Lab'], ['cleanroom', 'Cleanroom'], ['vault', 'Evidence Vault']] }
        ] }
    ]
  },

  'M06-form-seal-break': {
    kind: 'model_form',
    model: 'fix.data.media.unit',
    title: 'Witnessed Seal Break',
    newLabel: 'Record a Witnessed Seal Break',
    back: 'M06-custody',
    status: { field: 'seal_state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the sealed unit to open in the lab',
      note: 'Units whose seal is intact.',
      search: 'Search seal or bag number',
      choose: 'Open this seal',
      cols: ['seal_number', 'case_id', 'media_label', 'location', 'holder'],
      domain: [['seal_state', '=', 'sealed']],
      empty: 'No sealed unit is waiting to be opened.'
    },
    saveAction: {
      method: 'action_break_seal_with_witness', label: 'Break Seal (Witnessed)',
      done: 'Seal break recorded with its witness',
      kwargs: { witness_user_id: 'witness_user_id' }
    },
    sections: [
      { title: 'Step 2 of 2: Second-Person Witness (BRU-DTS-01)',
        note: 'A seal is opened only in front of a second person: name the witness, an active staff member other than you. The break, you and the witness are written to the case chain of custody.',
        fields: [
          { name: 'seal_number', label: 'Seal / Bag Number', readonly: true },
          { name: 'case_id', label: 'Recovery Case', readonly: true },
          { name: 'media_label', label: 'Drive Make / Model / Label', readonly: true },
          { name: 'location', label: 'Location', readonly: true },
          { name: 'witness_user_id', required: true, label: 'Witness (a second person, not you)', readonly: true, domain: INTERNAL_USER }
        ] }
    ]
  },

  'M06-form-attempt-outcome': {
    kind: 'model_form',
    model: 'fix.data.recovery.attempt',
    title: 'Attempt Outcome',
    newLabel: 'Record an Attempt Outcome',
    back: 'M06-attempts',
    status: { field: 'outcome' },
    pickRecord: {
      label: 'Step 1 of 2: choose the attempt that has ended',
      note: 'Attempts still in progress.',
      search: 'Search attempt',
      choose: 'Record its outcome',
      cols: ['case_id', 'method', 'started_at', 'cleanroom_slot_id', 'outcome'],
      domain: [['outcome', '=', 'in_progress']],
      empty: 'No recovery attempt is in progress. Log one with + New Recovery Attempt on Methodology Logging.'
    },
    saveAction: {
      method: 'action_finish', label: 'Record Outcome',
      done: 'Attempt closed with its outcome',
      kwargs: { outcome: 'outcome', notes: 'notes' }
    },
    sections: [
      { title: 'Step 2 of 2: Outcome & Engineer Notes',
        note: 'Only the case technician or Z4 custodian closes an attempt. The finish time is stamped by the system; once closed, the method, case and cleanroom slot are evidence and no longer change. An invasive attempt is re-checked against the customer consent and the cleanroom interlock.',
        fields: [
          { name: 'case_id', label: 'Recovery Case', readonly: true },
          { name: 'method', label: 'Recovery Method', readonly: true },
          { name: 'started_at', label: 'Started At', readonly: true },
          { name: 'cleanroom_slot_id', label: 'Cleanroom Slot', readonly: true },
          { name: 'outcome', required: true, label: 'Outcome', readonly: true,
            choices: [['success', 'Full Recovery'], ['partial', 'Partial Recovery'], ['failed', 'Failed'], ['media_damaged', 'Media Damaged']] },
          { name: 'notes', label: 'Engineer Notes (what was done, what was found)', readonly: true }
        ] }
    ]
  },

  'M06-form-inventory': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Recovered-Data Inventory Entry',
    newLabel: 'Record the Recovered-Data Inventory',
    back: 'M06-cases',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the case whose recovered data you are counting',
      note: 'Cases in recovery or recovered, not yet handed over.',
      search: 'Search case',
      choose: 'Record its inventory',
      cols: ['name', 'customer_id', 'specialism', 'media_type', 'recovered_files_count', 'state'],
      domain: [['state', 'in', ['recovering', 'recovered']]],
      empty: 'No case is in recovery or recovered yet.'
    },
    saveAction: {
      method: 'action_record_inventory', label: 'Record Inventory',
      done: 'Recovered-data inventory recorded',
      kwargs: { files_count: 'recovered_files_count', volume_gb: 'recovered_volume_gb' }
    },
    sections: [
      { title: 'Step 2 of 2: Files & Volume Recovered (FR-DTS-006)',
        note: 'Counts and size only: file names and content are never entered in the ERP. Recorded by the case technician or Z4 custodian, and fixed once the data is handed over.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'specialism', label: 'Specialism', readonly: true },
          { name: 'state', label: 'Stage', readonly: true },
          { name: 'recovered_files_count', required: true, label: 'Recovered Files (count)', readonly: true },
          { name: 'recovered_volume_gb', required: true, label: 'Recovered Volume (GB)', readonly: true }
        ] }
    ]
  },

  /* a plain write: recipient and target drive are typed until the target
   * serial is confirmed (the model then locks both) */
  'M06-form-handover-prep': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Handover Preparation',
    newLabel: 'Prepare a Handover',
    back: 'M06-handover',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the recovered case to hand over',
      note: 'Cases whose data is recovered and waiting for handover.',
      search: 'Search case',
      choose: 'Prepare this handover',
      cols: ['name', 'customer_id', 'handover_recipient_id', 'encrypted_target_serial', 'state'],
      domain: [['state', '=', 'recovered']],
      empty: 'No case is recovered and waiting for handover.'
    },
    sections: [
      { title: 'Step 2 of 2: Recipient & Target Drive (FR-DTS-007)',
        note: 'Name who collects the data (the customer or one of its contacts) and the serial of the encrypted drive the data was written to. Then, on Secure Handover & Purge: Confirm Target Drive Serial (read off the drive), Send Handover Code to the recipient, and record the Secure Handover. Both values are fixed once the serial is confirmed.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'handover_recipient_id', required: true, label: 'Handover Recipient (the customer or one of its contacts)' },
          { name: 'encrypted_target_serial', required: true, label: 'Encrypted Target Drive Serial' },
          { name: 'target_serial_confirmed_at', label: 'Target Serial Confirmed At', readonly: true }
        ] }
    ]
  },

  'M06-form-handover': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Secure Handover',
    newLabel: 'Record a Secure Handover',
    back: 'M06-handover',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the case being handed over',
      note: 'Recovered cases. The recipient and target drive come from Handover Preparation.',
      search: 'Search case',
      choose: 'Hand this case over',
      cols: ['name', 'customer_id', 'handover_recipient_id', 'encrypted_target_serial', 'target_serial_confirmed_at'],
      domain: [['state', '=', 'recovered']],
      empty: 'No case is recovered and waiting for handover.'
    },
    saveAction: {
      method: 'action_handover', label: 'Record Handover',
      done: 'Handed over: the retention clock has started',
      kwargs: { verification: 'handover_verification_ref', receipt_file: 'handover_receipt_file', receipt_filename: 'handover_receipt_filename' }
    },
    sections: [
      { title: 'Step 2 of 2: Verified Recipient & Signed Receipt (FR-DTS-007)',
        note: 'Refused until the target drive serial is confirmed. Verify the recipient with the one-time code sent by Send Handover Code, or with their ID number when a verified ID is on file. Upload the receipt the recipient signed; it is kept on the case. Only the case technician or Z4 custodian hands over.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'handover_recipient_id', label: 'Handover Recipient', readonly: true },
          { name: 'encrypted_target_serial', label: 'Encrypted Target Drive Serial', readonly: true },
          { name: 'target_serial_confirmed_at', label: 'Target Serial Confirmed At', readonly: true },
          { name: 'handover_verification_ref', required: true, label: 'Recipient One-Time Code or ID Number', readonly: true },
          { name: 'handover_receipt_file', label: 'Signed Handover Receipt (scan or photo)', readonly: true },
          { name: 'handover_receipt_filename', label: 'Receipt File Name', readonly: true }
        ] }
    ]
  },

  'M06-form-purge': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Secure Purge',
    newLabel: 'Record a Secure Purge',
    back: 'M06-handover',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the handed-over case to purge',
      note: 'Cases whose data was handed over and is still retained.',
      search: 'Search case',
      choose: 'Purge this case',
      cols: ['name', 'customer_id', 'media_serial_number', 'retention_until', 'state'],
      domain: [['state', '=', 'handover']],
      empty: 'No handed-over case is waiting to be purged.'
    },
    saveAction: {
      method: 'action_purge', label: 'Purge',
      done: 'Purged: the case is closed on its wipe certificate',
      kwargs: { certificate: 'purge_certificate_id' }
    },
    sections: [
      { title: 'Step 2 of 2: Verified Wipe Certificate (FR-DTS-008)',
        note: 'Recovered data is purged only on a verified wipe certificate for this case’s own media serial, unchanged since it was verified, and used for no other case. Leave the certificate blank to use the single verified certificate for the media serial.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'media_serial_number', label: 'Media Serial (the certificate must match)', readonly: true },
          { name: 'handover_at', label: 'Handed Over At', readonly: true },
          { name: 'retention_until', label: 'Retain Until', readonly: true },
          { name: 'purge_certificate_id', label: 'Verified Wipe Certificate', readonly: true,
            domain: [['sanitization_status', '=', 'verified']],
            emptyNote: 'No wipe certificate is verified yet. Record the wipe on + New Destruction Request (dual control); a second person verifies it on Secure Destruction.' }
        ] }
    ]
  },

  'M06-form-staff': {
    kind: 'model_form',
    model: 'fix.data.recovery.case',
    title: 'Named Z4 Staff Assignment',
    newLabel: 'Assign Named Z4 Staff',
    back: 'M06-cases',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the case',
      note: 'Open recovery cases.',
      search: 'Search case',
      choose: 'Assign its staff',
      cols: ['name', 'customer_id', 'assigned_technician_id', 'z4_custodian_id', 'state'],
      domain: OPEN_CASE,
      empty: 'No open recovery case yet. Open one with + New Recovery Case.'
    },
    saveAction: {
      method: 'action_assign_staff', label: 'Assign Staff',
      done: 'Named staff assigned: only they work this case’s data',
      kwargs: { technician: 'assigned_technician_id', custodian: 'z4_custodian_id' }
    },
    sections: [
      { title: 'Step 2 of 2: Technician & Z4 Custodian (FR-DTS-009 / BRU-DTS-02)',
        note: 'Holding a role never opens a case: only the people named here work its recovered data, and every opening is logged on Access Audit Log. The technician needs the Data Recovery Operator role, the custodian the Z4 Custodian role. Once recovery has started, only a Z4 custodian re-assigns.',
        fields: [
          { name: 'name', label: 'Case Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'state', label: 'Stage', readonly: true },
          { name: 'assigned_technician_id', label: 'Assigned Technician', readonly: true, domain: INTERNAL_USER },
          { name: 'z4_custodian_id', label: 'Assigned Z4 Custodian', readonly: true, domain: INTERNAL_USER }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M06:Recovery Case': 'M06-form-case',
  'M06:Media Intake (sealed)': 'M06-form-media',
  'M06:Firm Quotation': 'M06-form-quote',
  'M06:Destruction Request (dual control)': 'M06-form-wipe',
  /* M06 sub-module capture (2026-11-13) */
  'M06:Media Custody Move': 'M06-form-media-move',
  'M06:Witnessed Seal Break': 'M06-form-seal-break',
  'M06:Free Evaluation': 'M06-form-eval',
  'M06:Recovery Attempt': 'M06-form-attempt',
  'M06:Cleanroom Slot Booking': 'M06-form-cleanroom',
  'M06:Attempt Outcome': 'M06-form-attempt-outcome',
  'M06:Recovered-Data Inventory Entry': 'M06-form-inventory',
  'M06:Handover Preparation': 'M06-form-handover-prep',
  'M06:Secure Handover': 'M06-form-handover',
  'M06:Secure Purge': 'M06-form-purge',
  'M06:Backup Plan': 'M06-form-backup',
  'M06:Named Z4 Staff Assignment': 'M06-form-staff',
  'M06:__by_model__': {
    'fix.data.recovery.case': 'M06-form-case',
    'fix.data.media.unit': 'M06-form-media',
    'fix.data.quote': 'M06-form-quote',
    'fix.data.wipe.certificate': 'M06-form-wipe',
    'fix.data.recovery.attempt': 'M06-form-attempt',
    'fix.data.cleanroom.slot': 'M06-form-cleanroom',
    'fix.data.evaluation': 'M06-form-eval',
    'fix.data.backup.plan': 'M06-form-backup'
  },
  'M06:__by_screen__': {
    'M06-cases': 'M06-form-case',
    'M06-record': 'M06-form-case',
    'M06-custody': 'M06-form-media',
    'M06-quotes': 'M06-form-quote',
    'M06-destroy': 'M06-form-wipe',
    'M06-attempts': 'M06-form-attempt',
    'M06-cleanroom': 'M06-form-cleanroom',
    'M06-eval': 'M06-form-eval',
    'M06-backup': 'M06-form-backup'
  }
};

/* the module's "+ New" surface: the recovery case starts the journey. */
export const CREATE = {
  M06: { screen: 'M06-form-case', model: 'fix.data.recovery.case', label: 'Recovery Case' }
};
