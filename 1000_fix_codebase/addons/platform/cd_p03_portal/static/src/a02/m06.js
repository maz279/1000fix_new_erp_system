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
      { id: 'M06-record', en: 'Case Record (7 specialisms)', bn: 'কেস নথি', t: 'f' },
      { id: 'M06-attempts', en: 'Attempt Tracking', bn: 'প্রচেষ্টা ট্র্যাকিং', t: 'g' }
    ]},
    { en: 'Media Custody', screens: [
      { id: 'M06-custody', en: 'Sealed Media Custody', bn: 'সিলড মিডিয়া', t: 'g' },
      { id: 'M06-cleanroom', en: 'Cleanroom Schedule', bn: 'ক্লিনরুম', t: 'g' },
      { id: 'M06-inventory', en: 'Recovered-Data Inventory', bn: 'উদ্ধার তালিকা', t: 'g' }
    ]},
    { en: 'Quotation & Handover', screens: [
      { id: 'M06-eval', en: 'Free Evaluations', bn: 'ফ্রি মূল্যায়ন', t: 'g' },
      { id: 'M06-quotes', en: 'Firm Quotations', bn: 'চূড়ান্ত কোট', t: 'g' },
      { id: 'M06-handover', en: 'Secure Handover & Purge', bn: 'নিরাপদ হস্তান্তর', t: 'c' }
    ]},
    { en: 'Backup & Destruction', screens: [
      { id: 'M06-backup', en: 'Backup Plans & Tests', bn: 'ব্যাকআপ পরিকল্পনা', t: 'g' },
      { id: 'M06-destroy', en: 'Secure Destruction', bn: 'নিরাপদ ধ্বংস', t: 'c' },
      { id: 'M06-certs', en: 'Destruction Certificates', bn: 'ধ্বংস সনদ', t: 'g' }
    ]}
  ],
  reports: ['Recovery Success by Specialism', 'Case Cycle Time', 'Data Service Revenue', 'Destruction & Purge Audit', 'Backup Restore-Test Compliance'],
  forms: ['Recovery Case', 'Media Intake (sealed)', 'Firm Quotation', 'Destruction Request (dual control)'],
  cross: ['M36 recovery quotations', 'M24 evidence certificates', 'M18 e-waste routing', 'M01 data-service orders'],
  freg: {
    src: 75,
    sub: [
      ['1', 'Case Management (7 specialisms)', 12, { model: 'fix.data.recovery.case', cols: ['name', 'customer_id', 'specialism', 'media_type', 'state'], screens: ['M06-cases', 'M06-record'] }],
      ['2', 'Media Chain of Custody', 11, { model: 'fix.data.media.unit', cols: ['seal_number', 'case_id', 'media_label', 'location', 'seal_state'], screens: ['M06-custody', 'M06-cleanroom'] }],
      ['3', 'Evaluation & Quotation', 8, { model: 'fix.data.quote', cols: ['name', 'case_id', 'amount', 'valid_until', 'state'], screens: ['M06-eval', 'M06-quotes'] }],
      ['4', 'Methodology Logging', 6, { model: 'fix.data.recovery.attempt', cols: ['case_id', 'method', 'donor_part_used', 'imaged_pct', 'notes'], screens: ['M06-attempts', 'M06-cleanroom'] }],
      ['5', 'Attempt Tracking', 5, { model: 'fix.data.recovery.attempt', cols: ['case_id', 'sequence', 'started_at', 'finished_at', 'outcome'], screens: ['M06-attempts'] }],
      ['6', 'Recovered-Data Inventory', 5, { model: 'fix.data.recovery.case', cols: ['name', 'recovered_files_count', 'recovered_volume_gb', 'image_sha256_hash', 'state'], screens: ['M06-inventory'], domain: [['state', 'in', ['recovered', 'handover']]] }],
      ['7', 'Secure Handover & Purge', 7, { model: 'fix.data.recovery.case', cols: ['name', 'customer_id', 'purge_certificate_id', 'residency_zone', 'state'], screens: ['M06-handover'], domain: [['state', 'in', ['handover', 'purged']]] }],
      ['8', 'Backup Plans', 6, { model: 'fix.data.backup.plan', cols: ['name', 'customer_id', 'plan_type', 'rpo_hours', 'next_test_due'], screens: ['M06-backup'] }],
      ['9', 'Secure Destruction', 9, { model: 'fix.data.wipe.certificate', cols: ['name', 'serial_number', 'method', 'sanitization_status', 'certified_at'], screens: ['M06-destroy', 'M06-certs'] }],
      ['10', 'Access Control & Audit', 6, { model: 'fix.z4.access.audit', cols: ['case_id', 'user_name', 'access_type', 'access_time', 'step_up_verified'], screens: ['M06-cases'] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted cd_data_case models. */
export const SCREENS = {
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
    actions: [
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
          { name: 'case_id', required: true, label: 'Recovery Case' },
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
          { name: 'case_id', required: true, label: 'Data Recovery Case' },
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
          { name: 'case_id', required: true, label: 'Data Recovery Case' },
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
          { name: 'case_id', label: 'Assigned Recovery Case' },
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
          { name: 'case_id', required: true, label: 'Recovery Case' },
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

export const FORM_CHIPS = {
  'M06:Recovery Case': 'M06-form-case',
  'M06:Media Intake (sealed)': 'M06-form-media',
  'M06:Firm Quotation': 'M06-form-quote',
  'M06:Destruction Request (dual control)': 'M06-form-wipe',
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
