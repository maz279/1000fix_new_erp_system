/** @odoo-module **/
/* A05 — Circular Economy — M18 E-Waste & Circular Economy (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault on all 9 forms.
 * All 6 report packs exposed as chips (including ESG Materiality Report).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev.
 * A05 audit E3: every workflow, evidence and figure field is read-only here and
 * changes only through its action (the server guards it as well). */

export const MODULE = {
  area: 'A05', code: 'M18', en: 'E-Waste & Recycling', title: 'M18 · E-Waste & Recycling',
  bn: 'ই-বর্জ্য ও পুনর্ব্যবহার', icon: '♻️',
  desc: 'Intake and bulk collections, reuse/refurbish/recycle triage, secure data destruction with certificates, authorized recycler hand-off, green certificates, hazardous fraction tracking (lead, mercury, cadmium, lithium), public collection drives and EPR compliance reporting.',
  kpis: [
    { l: 'Total Intake (kg)', m: 'total_intake_kg' },
    { l: 'Diverted (kg)', m: 'diverted_kg' },
    { l: 'Recycled (kg)', m: 'recycled_kg' },
    { l: 'CO2 Saved (kg)', m: 'co2_saved_kg' },
    { l: 'Green Certs', m: 'certs_issued' },
    { l: 'Diversion Rate', m: 'diversion_rate', suffix: '%' }
  ],
  groups: [
    { en: 'Intake & Triage', screens: [
      { id: 'M18-intake', en: 'Collections & Intake', bn: 'সংগ্রহ ও গ্রহণ', t: 'g' },
      { id: 'M18-triage', en: 'Triage & Disposition', bn: 'বাছাই ও নিষ্পত্তি', t: 'g' },
      { id: 'M18-drives', en: 'Public Drives & Bins', bn: 'গণ সংগ্রহ কর্মসূচি', t: 'g' },
      { id: 'M18-battery', en: 'Hazardous & Battery Log', bn: 'ব্যাটারি ও বিপজ্জনক বর্জ্য', t: 'g' },
      // registry screens (contracts/nav): declared since A05 iter-1 but never
      // navigable — the read-only registers behind the worklists above
      { id: 'M18-collections', en: 'Collections & Bookings (register)', bn: 'সংগ্রহ', t: 'g' },
      { id: 'M18-events', en: 'Collection Events (register)', bn: 'সংগ্রহ ইভেন্ট', t: 'g' }
    ]},
    { en: 'Processing & Custody', screens: [
      { id: 'M18-batches', en: 'Recycler Batches', bn: 'রিসাইক্লার চালান', t: 'g' },
      { id: 'M18-partners', en: 'Authorized Recyclers', bn: 'অনুমোদিত পুনর্ব্যবহারকারী', t: 'g' },
      { id: 'M18-certs', en: 'Green Certificates', bn: 'সবুজ সনদপত্র', t: 'g' },
      { id: 'M18-manifest', en: 'Transfer Manifests (Form-1)', bn: 'হস্তান্তর শৃঙ্খলা', t: 'g' },
      { id: 'M18-pic', en: 'Basel Prior Consent', bn: 'বাসেল পূর্বসম্মতি', t: 'g' },
      { id: 'M18-settlements', en: 'Incentives & Recycler Money', bn: 'প্রণোদনা ও রিসাইক্লার অর্থ', t: 'g' },
      { id: 'M18-certificates', en: 'Disposal Certificates (register)', bn: 'নিষ্পত্তি সনদ', t: 'g' }
    ]},
    { en: 'Statutory & ESG', screens: [
      { id: 'M18-returns', en: 'Statutory Returns (DoE)', bn: 'পরিবেশ অধিদপ্তর বিবরণী', t: 'g' },
      { id: 'M18-registration', en: 'DoE Registration & EPR', bn: 'পরিবেশ অধিদপ্তর নিবন্ধন', t: 'g' },
      { id: 'M18-esg', en: 'ESG Metrics (computed)', bn: 'ইএসজি সূচক', t: 'g' },
      { id: 'M18-epr', en: 'EPR Compliance Pack', bn: 'ইপিআর কমপ্লায়েন্স', t: 'r' },
      { id: 'M18-impact', en: 'Carbon & Impact Estimation', bn: 'কার্বন ও প্রভাব', t: 'r' }
    ]}
  ],
  reports: [
    'Collection Volume Trend',
    'Disposition Mix',
    'Material Recovery Yield',
    'Statutory Compliance Pack',
    'Impact & Diversion',
    'ESG Materiality Report'
  ],
  forms: [
    'E-Waste Collection Dossier',
    'Triage & Sanitization Record',
    'Recycler Dispatch Batch',
    'Green & Destruction Certificate',
    'Collection Drive Event',
    'Battery & Hazardous Dossier',
    'Authorized Recycler Partner',
    'Statutory Environmental Return',
    'Basel Prior Informed Consent',
    'DoE E-Waste Registration',
    'E-Waste Incentive / Recycler Money',
    // the destruction gate's steps (FR-ESG-009) and the certificate's first
    // step (FR-ESG-013): added by the 13 Nov 2026 capture audit
    'Start Secure Destruction',
    'Bind M06 Wipe Certificate',
    'Release to Recycler',
    'Recycler Certificate from Batch'
  ],
  cross: ['M17 retired assets', 'M14 non-repairable trade-ins', 'M06 customer drop-offs', 'M03 hazardous transit'],
  /* 13 Nov 2026 capture audit: 3 Data Destruction and 9 ESG offered nothing,
   * 5 offered a "+ New" certificate the server refuses (a certificate comes
   * from its processed batch), 10 repeated page 8's return. Now 3 is the
   * destruction gate's queue (start, bind the M06 certificate, release),
   * 5 records the certificate from its batch, 10 holds the DoE registration
   * the returns are filed under; 9 stays computed (BRU-ESG-11: no entry path). */
  freg: { src: 82, sub: [
    ['1', 'Intake & Channels', 8, { model: 'fix.ewaste.collection', cols: ['name', 'customer_id', 'material_type', 'weight_kg', 'state'], screens: ['M18-intake', 'M18-settlements'], reports: ['Collection Volume Trend'], forms: ['E-Waste Collection Dossier', 'E-Waste Incentive / Recycler Money'] }],
    ['2', 'Triage & Disposition', 10, { model: 'fix.ewaste.triage', cols: ['name', 'collection_id', 'decision', 'data_bearing', 'decided_on'], screens: ['M18-triage'], reports: ['Disposition Mix'], forms: ['Triage & Sanitization Record'] }],
    ['3', 'Data Destruction', 7, { model: 'fix.ewaste.collection', cols: ['name', 'customer_id', 'triage_grade', 'wipe_certificate_id', 'state'], screens: ['M18-intake'], reports: ['Disposition Mix'], forms: ['Start Secure Destruction', 'Bind M06 Wipe Certificate', 'Release to Recycler'], create: 'M18-form-destruction', domain: [['wipe_required', '=', true], ['state', 'in', ['triaged', 'destruction']]] }],
    ['4', 'Outbound Recycler', 8, { model: 'fix.ewaste.batch', cols: ['name', 'partner_id', 'material_type', 'weight_kg', 'state'], screens: ['M18-batches', 'M18-partners', 'M18-manifest', 'M18-pic', 'M18-settlements'], reports: ['Material Recovery Yield'], forms: ['Recycler Dispatch Batch', 'Authorized Recycler Partner', 'Basel Prior Informed Consent', 'E-Waste Incentive / Recycler Money'] }],
    ['5', 'Green Certificates', 7, { model: 'fix.ewaste.certificate', cols: ['name', 'certificate_no', 'partner_id', 'weight_kg', 'issued_on'], screens: ['M18-certs'], reports: ['Material Recovery Yield'], forms: ['Recycler Certificate from Batch', 'Green & Destruction Certificate'], create: 'M18-form-cert-record' }],
    ['6', 'Public Drives & Bins', 7, { model: 'fix.ewaste.event', cols: ['name', 'venue', 'event_date', 'collected_kg', 'state'], screens: ['M18-drives'], reports: ['Collection Volume Trend'], forms: ['Collection Drive Event'] }],
    ['7', 'Hazardous Fraction', 9, { model: 'fix.ewaste.battery', cols: ['name', 'chemistry', 'hazard_class', 'weight_kg', 'state'], screens: ['M18-battery'], reports: ['Material Recovery Yield'], forms: ['Battery & Hazardous Dossier'] }],
    ['8', 'EPR Reporting', 8, { model: 'fix.ewaste.return', cols: ['name', 'authority', 'period', 'recovery_rate_pct', 'state'], screens: ['M18-returns'], reports: ['Statutory Compliance Pack'], forms: ['Statutory Environmental Return', 'DoE E-Waste Registration'] }],
    ['9', 'ESG & Carbon', 9, { model: 'fix.esg.metric', cols: ['name', 'metric_type', 'period', 'value', 'unit'], screens: ['M18-esg'], reports: ['ESG Materiality Report', 'Impact & Diversion'], forms: [] }],
    ['10', 'Compliance Pack', 9, { model: 'fix.ewaste.registration', cols: ['name', 'authority', 'role', 'registration_no', 'epr_target_pct', 'valid_to', 'state'], screens: ['M18-registration', 'M18-epr', 'M18-partners', 'M18-pic'], reports: ['Statutory Compliance Pack', 'Impact & Diversion'], forms: ['DoE E-Waste Registration', 'Authorized Recycler Partner', 'Basel Prior Informed Consent'] }]
  ] }
};

export const SCREENS = {
  /* registry screens restored (A05 iter-1 2026-11-01) */
  'M18-collections': { kind: 'model_list', model: 'fix.ewaste.collection', create: false,
    cols: ["name", "state", "weight_kg", "material_type", "batch_id", "company_id", "create_date"] },
  'M18-events': { kind: 'model_list', model: 'fix.ewaste.event', create: false,
    cols: ["name", "state", "event_date", "collected_kg", "collection_ids", "company_id", "create_date"] },
  'M18-certificates': { kind: 'model_list', model: 'fix.ewaste.certificate', create: false,
    cols: ["name", "state", "partner_id", "certificate_no", "weight_kg", "issued_on", "material_type"] },
  'M18-impact': { kind: 'table_report', module: 'M18', report: 'impact_diversion', title: 'Impact & Diversion Report', period: true },

  'M18-intake': { kind: 'model_list', model: 'fix.ewaste.collection', stateField: 'state',
    cols: ['name', 'customer_id', 'weight_kg', 'material_type', 'triage_grade', 'state'],
    actions: [
      { m: 'action_triage_reuse', l: 'Reuse' },
      { m: 'action_triage_refurbish', l: 'Refurbish' },
      { m: 'action_triage_recycle', l: 'Recycle' },
      { m: 'action_triage_hazardous', l: 'Hazardous' },
      { m: 'action_secure_destruction', l: 'Destruction' },
      { m: 'action_recycle_estimated', l: 'Release to Recycler' },
      { m: 'action_issue_certificate', l: 'Certify from Recycler Cert' },
      { m: 'action_remove_from_batch', l: 'Remove from Batch' },
      { m: 'action_apply_storage_extension', l: 'Record DoE Extension' }
    ] },
  'M18-triage': { kind: 'model_list', model: 'fix.ewaste.triage',
    cols: ['name', 'collection_id', 'decision', 'inspector_id', 'decided_on', 'wipe_required', 'data_bearing'] },
  'M18-drives': { kind: 'model_list', model: 'fix.ewaste.event', stateField: 'state',
    cols: ['name', 'venue', 'event_date', 'operating_unit_id', 'target_kg', 'collected_kg', 'state'],
    actions: [
      { m: 'action_open', l: 'Open Drive' },
      { m: 'action_close', l: 'Close Drive' }
    ] },
  'M18-battery': { kind: 'model_list', model: 'fix.ewaste.battery', stateField: 'state',
    cols: ['name', 'chemistry', 'hazard_class', 'storage_location', 'weight_kg', 'swollen_cell', 'terminal_taped', 'inspected_by_id', 'batch_id', 'state'],
    actions: [
      { m: 'action_inspect_and_quarantine', l: 'Record HSE Inspection' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_process', l: 'Process' }
    ] },
  'M18-batches': { kind: 'model_list', model: 'fix.ewaste.batch', stateField: 'state',
    cols: ['name', 'partner_id', 'material_type', 'item_count', 'weight_kg', 'transfer_note_ref', 'dispatched_on', 'received_weight_kg', 'state'],
    actions: [
      { m: 'action_load_ready_items', l: 'Load Ready Items' },
      { m: 'action_dispatch', l: 'Dispatch Batch' },
      { m: 'action_receive', l: 'Recycler Received' },
      { m: 'action_process', l: 'Recycler Processed' },
      { m: 'action_record_certificate', l: 'Record Recycler Certificate' }
    ] },
  'M18-partners': { kind: 'model_list', model: 'fix.ewaste.partner', stateField: 'state',
    cols: ['name', 'partner_id', 'capability', 'certification', 'certificate_no', 'valid_to', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_suspend', l: 'Suspend' },
      { m: 'action_renew', l: 'Renew Licence' }
    ] },
  /* a certificate is never typed: the server refuses any create but the
   * processed batch's Record Certificate (M18-4) - so no "+ New" here */
  'M18-certs': { kind: 'model_list', model: 'fix.ewaste.certificate', stateField: 'state', create: false,
    empty: 'No disposal certificate yet. A certificate is recorded from a processed recycler batch (Record a Recycler Certificate); then the recycler’s certificate number, stated weight and scan are entered on it, and a compliance officer issues it.',
    cols: ['name', 'certificate_no', 'partner_id', 'batch_id', 'material_type', 'weight_kg', 'issued_on', 'state'],
    actions: [
      { m: 'action_issue', l: 'Issue & Certify Items' },
      { m: 'action_revoke', l: 'Revoke' }
    ] },
  'M18-manifest': { kind: 'model_list', model: 'fix.ewaste.manifest', create: false,
    cols: ['name', 'batch_id', 'partner_id', 'licence_no', 'destination_country_id', 'total_weight_kg', 'hazardous', 'issued_on'] },
  'M18-pic': { kind: 'model_list', model: 'fix.ewaste.basel.pic', stateField: 'state',
    cols: ['name', 'partner_id', 'destination_country_id', 'consent_ref', 'max_weight_kg', 'valid_to', 'state'],
    actions: [
      { m: 'action_record_consent', l: 'Confirm Consent' },
      { m: 'action_withdraw', l: 'Withdraw' }
    ] },
  'M18-registration': { kind: 'model_list', model: 'fix.ewaste.registration', stateField: 'state',
    cols: ['name', 'authority', 'role', 'registration_no', 'epr_target_pct', 'valid_to', 'state'],
    actions: [{ m: 'action_activate', l: 'Confirm Registration' }] },
  'M18-settlements': { kind: 'model_list', model: 'fix.ewaste.settlement', stateField: 'state',
    cols: ['name', 'kind', 'partner_id', 'collection_id', 'batch_id', 'amount', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M18-returns': { kind: 'model_list', model: 'fix.ewaste.return', stateField: 'state',
    cols: ['name', 'authority', 'period', 'form_type', 'due_date', 'total_tonnage_collected', 'recovery_rate_pct', 'submitted_on', 'state'],
    actions: [
      { m: 'action_calculate_mass_balance', l: 'Calc Balance' },
      { m: 'action_submit_return', l: 'Submit DoE' },
      { m: 'action_accept_return', l: 'Accept DoE' }
    ] },
  'M18-esg': { kind: 'model_list', model: 'fix.esg.metric', create: false,
    cols: ['name', 'metric_type', 'scope', 'period', 'value', 'unit', 'factor_version', 'computed'],
    empty: 'No ESG metric computed yet. Metrics are calculated from the collections and recycler batches of the period (Recompute from Collections); they are not typed in.',
    actions: [{ m: 'action_recompute', l: 'Recompute from Collections' }] },
  'M18-epr': { kind: 'table_report', module: 'M18', report: 'compliance_pack', title: 'EPR Compliance Pack', period: true },

  /* Report chips -> their own computed packs (All 6 active) */
  'M18-rpt-volume': { kind: 'table_report', module: 'M18', report: 'collection_volume', title: 'Collection Volume Trend', period: true },
  'M18-rpt-disposition': { kind: 'table_report', module: 'M18', report: 'disposition_mix', title: 'Disposition Mix', period: true },
  'M18-rpt-recovery': { kind: 'table_report', module: 'M18', report: 'material_recovery', title: 'Material Recovery Yield', period: true },
  'M18-rpt-compliance': { kind: 'table_report', module: 'M18', report: 'compliance_pack', title: 'Statutory Compliance Pack', period: true },
  'M18-rpt-diversion': { kind: 'table_report', module: 'M18', report: 'impact_diversion', title: 'Impact & Diversion', period: true },
  'M18-rpt-esg': { kind: 'table_report', module: 'M18', report: 'esg_report', title: 'ESG Materiality Report', period: true },

  /* ============ D365 IN-WORKSPACE FORMS (6-TAB STANDARD) ============ */
  'M18-form-collection': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'E-Waste Collection Dossier',
    back: 'M18-intake',
    status: { field: 'state', labels: { collected: 'Collected', triaged: 'Triaged', destruction: 'Secure Destruction', recycled: 'Ready for Recycler', routed: 'Routed to M14', hazmat: 'Hazardous Stream', disposed: 'Disposed', certified: 'Certified' } },
    tabs: [
      { id: 'general', label: '1. General & Origin', bn: '১. সাধারণ ও উৎস', icon: '📦', badge: '4' },
      { id: 'pricing', label: '2. Mass & Material', bn: '২. ভর ও উপাদান', icon: '⚖️', badge: '3' },
      { id: 'technical', label: '3. Data Sanitization', bn: '৩. ডাটা ধ্বংস ও সনদ', icon: '🔒', badge: '2' },
      { id: 'lifecycle', label: '4. ESG & Traceability', bn: '৪. ইএসজি ও সন্ধান', icon: '🌱', badge: '4' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Intake Reference & Source',
        fields: [
          { name: 'name', label: 'Collection Record ID', readonly: true },
          { name: 'customer_id', required: true, label: 'Corporate / Retail Source' },
          { name: 'operating_unit_id', label: 'Receiving Hub' },
          { name: 'state', label: 'Collection State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Physical Mass Balance Classification',
        fields: [
          { name: 'item_count', label: 'Item Count' },
          { name: 'weight_kg', required: true, label: 'Intake Mass (kg)' },
          { name: 'material_type', required: true, label: 'Schedule-1 Category (Phone/Laptop/Battery/Other)' },
          { name: 'triage_grade', label: 'Triage Grade', readonly: true }
        ] },
      { tab: 'technical', title: 'Data Sanitization & Destruction',
        fields: [
          { name: 'data_bearing', label: 'Data Bearing (from triage)', readonly: true },
          { name: 'wipe_required', label: 'M06 Certificate Required', readonly: true },
          { name: 'disposal_certificate_id', label: 'Recycler Disposal Certificate', readonly: true },
          { name: 'wipe_certificate_id', label: 'NIST 800-88 Data Sanitization Certificate' },
          { name: 'disposal_certificate_ref', label: 'Final Destruction Proof Reference', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Environmental Traceability & Impact',
        fields: [
          { name: 'co2_factor_version', label: 'CO2 Factor Version', readonly: true },
          { name: 'collected_on', label: 'Received On', readonly: true },
          { name: 'storage_deadline', label: 'Storage Deadline (180 / +90 days)', readonly: true },
          { name: 'storage_extension_ref', label: 'DoE Storage Extension Ref' },
          { name: 'storage_overdue', label: 'Storage Overdue', readonly: true },
          { name: 'source_ref', label: 'Handed Over From (M14 trade-in)', readonly: true },
          { name: 'esg_co2_saved_kg', label: 'CO2e Avoided (kg, estimate - not inventory)', readonly: true },
          { name: 'event_id', label: 'Origin Public Collection Campaign' },
          { name: 'batch_id', label: 'Downstream Recycler Batch', readonly: true },
          { name: 'device_id', label: 'Asset Master Reference' }
        ] },
      { tab: 'governance', title: 'Corporate Identity',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-triage': {
    kind: 'model_form',
    model: 'fix.ewaste.triage',
    title: 'Triage & Sanitization Record',
    back: 'M18-triage',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔍', badge: '3' },
      { id: 'pricing', label: '2. Disposition Target', bn: '২. নিষ্পত্তি গন্তব্য', icon: '🎯', badge: '1' },
      { id: 'technical', label: '3. Data Sanitization', bn: '৩. ডাটা ধ্বংস বাধ্যবাধকতা', icon: '🛡️', badge: '2' },
      { id: 'lifecycle', label: '4. Decision Log', bn: '৪. সিদ্ধান্ত লগ', icon: '✍️', badge: '3' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Triage Docket',
        fields: [
          { name: 'name', label: 'Triage Case ID', readonly: true },
          /* the server triages a collected item once; anything else is refused */
          { name: 'collection_id', required: true, label: 'Origin Collection Item', domain: [['state', '=', 'collected']] }
        ] },
      { tab: 'pricing', title: 'Disposition Routing',
        fields: [
          { name: 'decision', required: true, label: 'Triage Disposition Decision (Reuse/Refurbish/Recycle/Hazardous)' }
        ] },
      { tab: 'technical', title: 'Data Bearing Identification',
        fields: [
          { name: 'data_bearing', label: 'Contains Storage / Data Bearing Media' },
          { name: 'wipe_required', label: 'Mandatory Secure Data Wipe' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Evaluation',
        fields: [
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'inspector_id', label: 'Assessor (the deciding user)', readonly: true },
          { name: 'decided_on', label: 'Decision Timestamp', readonly: true },
          { name: 'notes', label: 'Technical Condition Notes' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-batch': {
    kind: 'model_form',
    model: 'fix.ewaste.batch',
    title: 'Recycler Dispatch Batch',
    back: 'M18-batches',
    status: { field: 'state', labels: { draft: 'Draft', dispatched: 'Dispatched to Recycler', received: 'Received by Recycler', processed: 'Processed' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🚛', badge: '4' },
      { id: 'pricing', label: '2. Bulk Mass', bn: '২. মোট ভর', icon: '⚖️', badge: '2' },
      { id: 'technical', label: '3. Manifest & Transit', bn: '৩. পরিবহন চালান', icon: '📜', badge: '2' },
      { id: 'lifecycle', label: '4. Transit Observations', bn: '৪. ট্রানজিট পর্যবেক্ষণ', icon: '📝', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Batch Shipment Header',
        fields: [
          { name: 'name', label: 'Consignment Batch No', readonly: true },
          /* dispatch re-checks the licence (BRU-ESG-02): only an approved recycler */
          { name: 'partner_id', required: true, label: 'Authorized Recycler Partner', domain: [['state', '=', 'active']] },
          { name: 'operating_unit_id', label: 'Dispatch Hub' },
          { name: 'state', label: 'Batch Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Weighbridge & Fraction',
        fields: [
          { name: 'item_count', label: 'Items', readonly: true },
          { name: 'received_weight_kg', label: 'Recycler Weighbridge (kg)' },
          { name: 'processed_weight_kg', label: 'Processed (kg)', readonly: true },
          { name: 'weight_kg', label: 'Itemised Mass (kg, sum of items)', readonly: true },
          { name: 'material_type', required: true, label: 'Material Classification' }
        ] },
      { tab: 'technical', title: 'Transfer Documentation (S.R.O. 187 Form-2)',
        fields: [
          { name: 'manifest_id', label: 'Form-1 Manifest', readonly: true },
          { name: 'destination_country_id', label: 'Destination Country' },
          { name: 'basel_pic_id', label: 'Basel PIC (cross-border)', domain: [['state', '=', 'consented']] },
          { name: 'recycler_receipt_ref', label: 'Recycler Receipt Ref' },
          /* the scan is uploaded here (once the recycler has received the batch) */
          { name: 'processing_evidence_id', label: 'Recycler Processing Evidence (on file)', readonly: true },
          { name: 'processing_file', type: 'file', label: 'Upload Processing Evidence' },
          { name: 'processing_filename', label: 'Evidence File Name' },
          { name: 'received_on', label: 'Received On', readonly: true },
          { name: 'processed_on', label: 'Processed On', readonly: true },
          { name: 'transfer_note_ref', label: 'Waste Transfer Manifest Ref', readonly: true },
          { name: 'dispatched_on', label: 'Departure Timestamp', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Driver & Logistics Notes',
        fields: [
          { name: 'notes', label: 'Transit Security Remarks' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-cert': {
    kind: 'model_form',
    model: 'fix.ewaste.certificate',
    title: 'Green & Destruction Certificate',
    back: 'M18-certs',
    /* never typed from blank (the server refuses it): the recycler's details
     * are entered on the draft its processed batch recorded */
    create: false,
    newLabel: 'Enter a Recycler Certificate',
    pickRecord: {
      label: 'Step 1 of 2: choose the draft certificate the recycler sent',
      note: 'Drafts recorded from processed batches. Enter the recycler’s certificate number, the weight it states and its scan, then a compliance officer issues it from Green Certificates.',
      search: 'Search certificate, batch or recycler',
      choose: 'Enter its details',
      cols: ['name', 'batch_id', 'partner_id', 'material_type', 'state'],
      domain: [['state', '=', 'draft']],
      empty: 'No draft certificate. Record one from a processed batch first (Record a Recycler Certificate).'
    },
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued', revoked: 'Revoked' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📜', badge: '4' },
      { id: 'pricing', label: '2. Mass Certified', bn: '২. প্রত্যয়িত ভর', icon: '⚖️', badge: '2' },
      { id: 'technical', label: '3. Digital Proof', bn: '৩. ডিজিটাল প্রমাণ', icon: '🔒', badge: '2' },
      { id: 'lifecycle', label: '4. Chain of Custody Links', bn: '৪. চেইন সংযোগ', icon: '🔗', badge: '2' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Certificate Dossier',
        fields: [
          { name: 'name', label: 'Title / Subject', readonly: true },
          { name: 'certificate_no', label: 'Recycler Certificate Number' },
          { name: 'partner_id', label: 'Recipient / Client Entity', readonly: true },
          { name: 'state', label: 'Certification Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Certified Mass Balance',
        fields: [
          { name: 'recycler_stated_weight_kg', label: 'Weight Stated by Recycler (kg)' },
          { name: 'weight_kg', label: 'Certified E-Waste Mass (kg)', readonly: true },
          { name: 'material_type', label: 'Material Fraction' }
        ] },
      { tab: 'technical', title: 'Issuance & Verification Proof',
        fields: [
          { name: 'evidence_attachment_id', label: 'Recycler Certificate (scan on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Recycler Certificate (scan)' },
          { name: 'evidence_filename', label: 'Certificate File Name' },
          { name: 'issued_by_id', label: 'Issued By', readonly: true },
          { name: 'revoke_reason', label: 'Revocation Reason' },
          { name: 'issued_on', label: 'Official Issue Date', readonly: true },
          { name: 'file_ref', label: 'Cryptographic Hash Reference (SHA-256)' }
        ] },
      { tab: 'lifecycle', title: 'Custody Chain Lineage',
        fields: [
          { name: 'collection_ids', label: 'Certified Items', readonly: true },
          { name: 'collection_id', label: 'Source Collection Record', readonly: true },
          { name: 'batch_id', label: 'Origin Bulk Dispatch Batch', readonly: true }
        ] },
      { tab: 'governance', title: 'Issuing Authority',
        fields: [
          { name: 'company_id', label: 'Company', readonly: true }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-event': {
    kind: 'model_form',
    model: 'fix.ewaste.event',
    title: 'Collection Drive Event',
    back: 'M18-drives',
    status: { field: 'state', labels: { planned: 'Planned', open: 'Live / Open', closed: 'Closed & Reconciled' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '📢', badge: '4' },
      { id: 'pricing', label: '2. Tonnage Targets', bn: '২. লক্ষিত টন', icon: '🎯', badge: '2' },
      { id: 'technical', label: '3. Operating Hub', bn: '৩. পরিচালনা কেন্দ্র', icon: '🏢', badge: '1' },
      { id: 'lifecycle', label: '4. Campaign Notes', bn: '৪. ক্যাম্পেইন বিবরণ', icon: '📝', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Campaign Identification',
        fields: [
          { name: 'name', required: true, label: 'Campaign Title' },
          { name: 'venue', required: true, label: 'Collection Center / Venue' },
          { name: 'event_date', required: true, label: 'Event Date' },
          { name: 'state', label: 'Event Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Collection Targets vs Realised',
        fields: [
          { name: 'target_kg', label: 'Campaign Target Mass (kg)' },
          { name: 'collected_kg', label: 'Actual Collected Mass (kg)', readonly: true }
        ] },
      { tab: 'technical', title: 'Organizing Operations Hub',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'lifecycle', title: 'Event Observations & Logistics',
        fields: [
          { name: 'notes', label: 'Public Participation Log' }
        ] },
      { tab: 'governance', title: 'Corporate Sponsor',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-battery': {
    kind: 'model_form',
    model: 'fix.ewaste.battery',
    title: 'Battery & Hazardous Dossier',
    back: 'M18-battery',
    status: { field: 'state', labels: { stored: 'In Storage', dispatched: 'Dispatched to Recycler', processed: 'Safe Disposal' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🔋', badge: '4' },
      { id: 'pricing', label: '2. Mass Weight', bn: '২. মোট ওজন', icon: '⚖️', badge: '1' },
      { id: 'technical', label: '3. UN 3480 Class 9 Inspection', bn: '৩. নিরাপত্তা পরিদর্শন', icon: '⚠️', badge: '3' },
      { id: 'lifecycle', label: '4. Chain of Custody & Trace', bn: '৪. চেইন ও সন্ধান', icon: '📋', badge: '6' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Hazardous Fraction Profile',
        fields: [
          { name: 'name', label: 'Battery Asset Record', readonly: true },
          { name: 'chemistry', required: true, label: 'Cell Chemistry (Li-ion/Lead-Acid/Ni-Cd/LiFePO4)' },
          { name: 'hazard_class', label: 'UN Hazard Class (Class 9 Miscellaneous)' },
          { name: 'state', label: 'Hazard Safety State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Net Weight',
        fields: [
          { name: 'weight_kg', required: true, label: 'Net Battery Weight (kg)' }
        ] },
      { tab: 'technical', title: 'UN 3480 / UN 3481 Class 9 Safety Gates',
        fields: [
          { name: 'inspection_evidence_id', label: 'Inspection Photo (on file)', readonly: true },
          { name: 'inspection_file', type: 'file', label: 'Upload Inspection Photo (taped terminals)' },
          { name: 'inspection_filename', label: 'Photo File Name' },
          { name: 'inspected_by_id', label: 'HSE Inspector', readonly: true },
          { name: 'inspected_on', label: 'Inspected On', readonly: true },
          { name: 'terminal_taped', label: 'Terminals Insulated & Taped (Short-Circuit Prevention)', readonly: true },
          { name: 'swollen_cell', label: 'Thermal Runaway Risk / Swollen Cell Detected' },
          { name: 'quarantine_barrel_ref', label: 'Fire-Safe Vermiculite Quarantine Barrel' }
        ] },
      { tab: 'lifecycle', title: 'Storage & Downstream Traceability',
        fields: [
          { name: 'storage_location', label: 'Flame-Proof Storage Bunker' },
          { name: 'received_on', label: 'Intake Date', readonly: true },
          { name: 'operating_unit_id', label: 'Intake Unit' },
          { name: 'collection_id', label: 'Origin Collection Dossier' },
          { name: 'batch_id', label: 'Consolidated Outbound Batch', readonly: true },
          { name: 'notes', label: 'Safety Officer Notes' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-partner': {
    kind: 'model_form',
    model: 'fix.ewaste.partner',
    title: 'Authorized Recycler Partner',
    back: 'M18-partners',
    status: { field: 'state', labels: { draft: 'Pending Approval', active: 'Active & Approved', suspended: 'Suspended', expired: 'Licence Expired' } },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🏭', badge: '3' },
      { id: 'pricing', label: '2. Processing Scope', bn: '২. প্রক্রিয়াকরণ সক্ষমতা', icon: '⚙️', badge: '2' },
      { id: 'technical', label: '3. DoE Accreditation', bn: '৩. পরিবেশ অধিদপ্তর লাইসেন্স', icon: '📜', badge: '3' },
      { id: 'lifecycle', label: '4. Partnership Life', bn: '৪. অংশীদারিত্বের স্থিতি', icon: '🤝', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Partner Legal Entity',
        fields: [
          { name: 'name', required: true, label: 'Recycler Name' },
          { name: 'partner_id', required: true, label: 'Vendor / Partner Business Record' },
          { name: 'state', label: 'Accreditation Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Fraction Capability',
        fields: [
          { name: 'capability', label: 'Processing Scope (PCB Smelting/Plastic/Precious Metals)' },
          { name: 'certification', label: 'Standard (R2v3 / e-Stewards / ISO 14001)' }
        ] },
      { tab: 'technical', title: 'Department of Environment (DoE) Permit',
        fields: [
          { name: 'licence_attachment_id', label: 'Licence Evidence (scan on file)', readonly: true },
          { name: 'licence_file', type: 'file', label: 'Upload Licence Scan' },
          { name: 'licence_filename', label: 'Licence File Name' },
          { name: 'certificate_no', required: true, label: 'DoE License Number' },
          { name: 'valid_from', label: 'License Effective Date' },
          { name: 'valid_to', label: 'License Expiry Date' }
        ] },
      { tab: 'lifecycle', title: 'Audit Verification',
        fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-return': {
    kind: 'model_form',
    model: 'fix.ewaste.return',
    title: 'Statutory Environmental Return',
    back: 'M18-returns',
    status: { field: 'state', labels: { draft: 'Draft', submitted: 'Submitted', accepted: 'Accepted by Authority' } },
    tabs: [
      { id: 'general', label: '1. General & Authority', bn: '১. সাধারণ ও কর্তৃপক্ষ', icon: '🏛️', badge: '6' },
      { id: 'pricing', label: '2. Mass Balance Return', bn: '২. ভর ব্যালেন্স বিবরণী', icon: '⚖️', badge: '3' },
      { id: 'technical', label: '3. Compliance Deadlines', bn: '৩. সময়সীমা ও ট্র্যাকিং', icon: '📅', badge: '4' },
      { id: 'lifecycle', label: '4. Audit Remarks', bn: '৪. নিরীক্ষা মন্তব্য', icon: '📝', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Statutory Filing Header (S.R.O. 187-Law/2021)',
        fields: [
          { name: 'name', label: 'Filing Reference ID', readonly: true },
          { name: 'authority', required: true, label: 'Regulatory Body (Department of Environment)' },
          { name: 'period', required: true, label: 'Compliance Period (e.g., 2026-Q3)' },
          { name: 'form_type', required: true, label: 'Statutory Form Type (Form-1 / Form-2 / Form-3)' },
          { name: 'schedule_1_category', label: 'Schedule-1 Category' },
          { name: 'state', label: 'Filing Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Mass Balance & Recovery Ratio',
        fields: [
          { name: 'nil_return_reason', label: 'Nil Return Reason (0 t)' },
          { name: 'total_tonnage_collected', label: 'Gross Collected Tonnage (MT)', readonly: true },
          { name: 'total_tonnage_recycled', label: 'Total Recycled Tonnage (MT)', readonly: true },
          { name: 'recovery_rate_pct', label: 'Recovery Rate (% Target: 30%-50%)', readonly: true }
        ] },
      { tab: 'technical', title: 'Timetable & Regulatory Receipt',
        fields: [
          { name: 'due_date', required: true, label: 'Statutory Submission Deadline' },
          { name: 'submitted_on', label: 'Official Submission Date', readonly: true },
          { name: 'is_overdue', label: 'Statutory Overdue Flag', readonly: true },
          { name: 'reference', label: 'Filing Reference' },
          { name: 'authority_ack_ref', label: 'Authority Acknowledgement No' },
          { name: 'submitted_by_id', label: 'Submitted By', readonly: true },
          { name: 'accepted_by_id', label: 'Accepted By', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Regulatory Officer Observations',
        fields: [
          { name: 'notes', label: 'Regulatory Audit Findings' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },

  'M18-form-esg': {
    kind: 'model_form',
    model: 'fix.esg.metric',
    title: 'ESG Materiality Metric',
    back: 'M18-esg',
    /* computed from collections, every field read-only: a result, not data entry */
    create: false, pick: 'An ESG metric is calculated from the period’s collections: open one from ESG Metrics.',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ', icon: '🌱', badge: '3' },
      { id: 'pricing', label: '2. Value & Metric', bn: '২. পরিমাপ ও একক', icon: '📊', badge: '2' },
      { id: 'technical', label: '3. Operating Hub', bn: '৩. পরিচালনা কেন্দ্র', icon: '🏢', badge: '1' },
      { id: 'lifecycle', label: '4. Period Scope', bn: '৪. সময়কাল পরিধি', icon: '📅', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. নিয়ন্ত্রণ', icon: '🏛️', badge: '1' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'ESG Indicator Definition',
        fields: [
          { name: 'name', required: true, label: 'Indicator Title (e.g., Avoided Scope 3 CO2e)', readonly: true },
          { name: 'metric_type', required: true, label: 'GRI/SASB Materiality Type', readonly: true }
        ] },
      { tab: 'pricing', title: 'Quantification',
        fields: [
          { name: 'scope', label: 'Scope (inventory / avoided)', readonly: true },
          { name: 'factor_version', label: 'Factor Version', readonly: true },
          { name: 'source_count', label: 'Source Records', readonly: true },
          { name: 'computed_at', label: 'Computed At', readonly: true },
          { name: 'value', required: true, label: 'Reported Metric Value', readonly: true },
          { name: 'unit', required: true, label: 'Unit of Measure (kg / MT / %)', readonly: true }
        ] },
      { tab: 'technical', title: 'Operational Hub',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Sustainability Timeline',
        fields: [
          { name: 'period', required: true, label: 'Reporting Period', readonly: true }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company', readonly: true }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
          ] }
    ]
  },
  'M18-form-pic': {
    kind: 'model_form',
    model: 'fix.ewaste.basel.pic',
    title: 'Basel Prior Informed Consent',
    back: 'M18-pic',
    status: { field: 'state', labels: { draft: 'Draft', consented: 'Consented', expired: 'Expired', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'general', label: '1. Consent', bn: '১. সম্মতি', icon: '🌍', badge: '5' },
      { id: 'technical', label: '2. Validity & Evidence', bn: '২. মেয়াদ ও প্রমাণ', icon: '📜', badge: '4' },
      { id: 'governance', label: '3. Governance', bn: '৩. নিয়ন্ত্রণ', icon: '🏛️', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Transboundary Movement',
        fields: [
          { name: 'name', label: 'PIC Reference', readonly: true },
          { name: 'partner_id', required: true, label: 'Importing Recycler' },
          { name: 'destination_country_id', required: true, label: 'Destination Country' },
          { name: 'importing_authority', label: 'Competent Authority of Import' },
          { name: 'consent_ref', label: 'Consent Reference' }
        ] },
      { tab: 'technical', title: 'Consent Scope',
        fields: [
          { name: 'max_weight_kg', label: 'Consented Quantity (kg)' },
          { name: 'valid_from', label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'evidence_attachment_id', label: 'Consent Document (scan on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Consent Document' },
          { name: 'evidence_filename', label: 'Consent File Name' }
        ] },
      { tab: 'governance', title: 'Four Eyes',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'confirmed_by_id', label: 'Confirmed By', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M18-form-registration': {
    kind: 'model_form',
    model: 'fix.ewaste.registration',
    title: 'DoE E-Waste Registration',
    back: 'M18-registration',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', expired: 'Expired' } },
    tabs: [
      { id: 'general', label: '1. Registration', bn: '১. নিবন্ধন', icon: '🏛️', badge: '5' },
      { id: 'technical', label: '2. Validity & EPR', bn: '২. মেয়াদ ও ইপিআর', icon: '📅', badge: '5' },
      { id: 'governance', label: '3. Governance', bn: '৩. নিয়ন্ত্রণ', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Hazardous Waste (E-waste) Management Rules 2021',
        fields: [
          { name: 'name', label: 'Record', readonly: true },
          { name: 'authority', required: true, label: 'Authority' },
          { name: 'role', required: true, label: 'Registered Role' },
          { name: 'registration_no', label: 'Registration Number' },
          { name: 'issuing_office', label: 'Issuing Office' }
        ] },
      { tab: 'technical', title: 'Validity, Plan and EPR Target',
        fields: [
          { name: 'valid_from', label: 'Valid From' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'management_plan_ref', label: 'E-Waste Management Plan Ref' },
          { name: 'epr_target_pct', label: 'EPR Collection Target %' },
          { name: 'evidence_attachment_id', label: 'Registration Certificate (scan on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Registration Certificate' },
          { name: 'evidence_filename', label: 'Certificate File Name' }
        ] },
      { tab: 'governance', title: 'Four Eyes',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'confirmed_by_id', label: 'Confirmed By', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  /* ===== step forms (13 Nov 2026 capture audit): each acts on an existing
   * record through its workflow method - the fields they show are guarded ===== */
  'M18-form-destruction': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'Start Secure Destruction',
    newLabel: 'Start Secure Destruction',
    back: 'M18-intake',
    status: { field: 'state', labels: { triaged: 'Triaged', destruction: 'Secure Destruction' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the triaged item to destroy',
      note: 'Items the assessor graded Recycle Only. No item leaves 1000FiX custody without a verified M06 destruction certificate bound to it (FR-ESG-009).',
      search: 'Search item or customer',
      choose: 'Start its destruction',
      cols: ['name', 'customer_id', 'material_type', 'weight_kg', 'wipe_certificate_id'],
      domain: [['state', '=', 'triaged'], ['triage_grade', '=', 'recycle']],
      empty: 'No triaged item is waiting for destruction. Triage a collected item as Recycle Only first.'
    },
    saveAction: {
      method: 'action_secure_destruction', label: 'Start Secure Destruction',
      done: 'Destruction started: the M06 destruction certificate is raised for verification'
    },
    tabs: [{ id: 'general', label: '1. Item & Certificate', bn: '১. আইটেম ও সনদ', icon: '🔒', badge: '6' }],
    sections: [
      { tab: 'general', title: 'Item going to secure destruction',
        note: 'If no M06 certificate is bound yet, one is raised for physical destruction of this item; an M06 verifier verifies it before the item can be released to a recycler.',
        fields: [
          { name: 'name', label: 'Collection Record', readonly: true },
          { name: 'customer_id', label: 'Source', readonly: true },
          { name: 'material_type', label: 'Category', readonly: true },
          { name: 'weight_kg', label: 'Weight (kg)', readonly: true },
          { name: 'data_bearing', label: 'Data Bearing', readonly: true },
          { name: 'wipe_certificate_id', label: 'M06 Destruction Certificate', readonly: true }
        ] }
    ]
  },

  'M18-form-wipe-bind': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'Bind M06 Wipe Certificate',
    newLabel: 'Bind an M06 Wipe Certificate',
    back: 'M18-intake',
    pickRecord: {
      label: 'Step 1 of 2: choose the item the certificate covers',
      note: 'Items not yet past triage that need an M06 certificate. One certificate covers one item, bound to its storage media.',
      search: 'Search item or customer',
      choose: 'Bind its certificate',
      cols: ['name', 'customer_id', 'device_id', 'material_type', 'wipe_certificate_id', 'state'],
      domain: [['wipe_required', '=', true], ['state', 'in', ['collected', 'triaged']]],
      empty: 'No item is waiting for an M06 certificate.'
    },
    tabs: [{ id: 'general', label: '1. Certificate', bn: '১. সনদ', icon: '🛡️', badge: '4' }],
    sections: [
      { tab: 'general', title: 'M06 certificate for this item',
        note: 'Choose the certificate M06 issued for this item’s media. The release is still refused until M06 has verified it.',
        fields: [
          { name: 'name', label: 'Collection Record', readonly: true },
          { name: 'customer_id', label: 'Source', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'wipe_certificate_id', required: true, label: 'M06 Wipe / Destruction Certificate' }
        ] }
    ]
  },

  'M18-form-release': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'Release to Recycler',
    newLabel: 'Release a Destroyed Item to the Recycler',
    back: 'M18-intake',
    pickRecord: {
      label: 'Step 1 of 2: choose the destroyed item',
      note: 'Released only when its M06 certificate is verified; the avoided CO2e is computed from the weight, never typed.',
      search: 'Search item or customer',
      choose: 'Release it',
      cols: ['name', 'customer_id', 'material_type', 'weight_kg', 'wipe_certificate_id'],
      domain: [['state', '=', 'destruction']],
      empty: 'No item is in secure destruction. Start one with Start Secure Destruction.'
    },
    saveAction: {
      method: 'action_recycle_estimated', label: 'Release to Recycler',
      done: 'Released: the item is ready for a recycler batch'
    },
    tabs: [{ id: 'general', label: '1. Item', bn: '১. আইটেম', icon: '♻️', badge: '5' }],
    sections: [
      { tab: 'general', title: 'Destroyed item',
        fields: [
          { name: 'name', label: 'Collection Record', readonly: true },
          { name: 'customer_id', label: 'Source', readonly: true },
          { name: 'material_type', label: 'Category', readonly: true },
          { name: 'weight_kg', label: 'Weight (kg)', readonly: true },
          { name: 'wipe_certificate_id', label: 'M06 Destruction Certificate', readonly: true }
        ] }
    ]
  },

  'M18-form-cert-record': {
    kind: 'model_form',
    model: 'fix.ewaste.batch',
    title: 'Recycler Certificate from Batch',
    newLabel: 'Record a Recycler Certificate',
    back: 'M18-certs',
    pickRecord: {
      label: 'Step 1 of 2: choose the processed batch the recycler certified',
      note: 'A disposal certificate belongs to one processed batch and lists its items (FR-ESG-013).',
      search: 'Search batch or recycler',
      choose: 'Record its certificate',
      cols: ['name', 'partner_id', 'material_type', 'processed_weight_kg', 'processed_on'],
      domain: [['state', '=', 'processed'], '|', ['certificate_ids', '=', false], ['certificate_ids.state', '=', 'revoked']],
      empty: 'No processed batch is waiting for its certificate. A batch is processed on Outbound Recycler once the recycler’s processing evidence is attached.'
    },
    saveAction: {
      method: 'action_record_certificate', label: 'Record Certificate',
      done: 'Draft certificate recorded: enter the recycler’s number, weight and scan with Enter a Recycler Certificate'
    },
    tabs: [{ id: 'general', label: '1. Batch', bn: '১. চালান', icon: '📜', badge: '5' }],
    sections: [
      { tab: 'general', title: 'Processed batch',
        fields: [
          { name: 'name', label: 'Batch', readonly: true },
          { name: 'partner_id', label: 'Recycler', readonly: true },
          { name: 'material_type', label: 'Material', readonly: true },
          { name: 'processed_weight_kg', label: 'Processed (kg)', readonly: true },
          { name: 'processed_on', label: 'Processed On', readonly: true }
        ] }
    ]
  },

  'M18-form-settlement': {
    kind: 'model_form',
    model: 'fix.ewaste.settlement',
    title: 'E-Waste Incentive / Recycler Money',
    back: 'M18-settlements',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved - Handed to Finance', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: '1. Basis', bn: '১. ভিত্তি', icon: '💳', badge: '4' },
      { id: 'pricing', label: '2. Amount', bn: '২. পরিমাণ', icon: '৳', badge: '3' },
      { id: 'governance', label: '3. Approval', bn: '৩. অনুমোদন', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'What the money is for',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'collection_id', label: 'Collection (incentive)' },
          { name: 'batch_id', label: 'Batch (recycler fee / income)' }
        ] },
      { tab: 'pricing', title: 'Payee / Payer and Amount',
        fields: [
          { name: 'partner_id', required: true, label: 'Payee / Payer' },
          { name: 'amount', required: true, label: 'Amount (BDT)' },
          { name: 'rate_per_kg', label: 'Rate per kg' }
        ] },
      { tab: 'governance', title: 'Routed Approval (M63)',
        fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M18:Collection Volume Trend': 'M18-rpt-volume',
  'M18:Disposition Mix': 'M18-rpt-disposition',
  'M18:Material Recovery Yield': 'M18-rpt-recovery',
  'M18:Statutory Compliance Pack': 'M18-rpt-compliance',
  'M18:Impact & Diversion': 'M18-rpt-diversion',
  'M18:ESG Materiality Report': 'M18-rpt-esg'
};

export const FORM_MODELS = {
  'M18:E-Waste Collection Dossier': 'fix.ewaste.collection',
  'M18:Triage & Sanitization Record': 'fix.ewaste.triage',
  'M18:Recycler Dispatch Batch': 'fix.ewaste.batch',
  'M18:Green & Destruction Certificate': 'fix.ewaste.certificate',
  'M18:Collection Drive Event': 'fix.ewaste.event',
  'M18:Battery & Hazardous Dossier': 'fix.ewaste.battery',
  'M18:Authorized Recycler Partner': 'fix.ewaste.partner',
  'M18:Statutory Environmental Return': 'fix.ewaste.return',
  'M18:Basel Prior Informed Consent': 'fix.ewaste.basel.pic',
  'M18:DoE E-Waste Registration': 'fix.ewaste.registration',
  'M18:E-Waste Incentive / Recycler Money': 'fix.ewaste.settlement',
  'M18:Start Secure Destruction': 'fix.ewaste.collection',
  'M18:Bind M06 Wipe Certificate': 'fix.ewaste.collection',
  'M18:Release to Recycler': 'fix.ewaste.collection',
  'M18:Recycler Certificate from Batch': 'fix.ewaste.batch'
};

export const FORM_CHIPS = {
  'M18:E-Waste Collection Dossier': 'M18-form-collection',
  'M18:Triage & Sanitization Record': 'M18-form-triage',
  'M18:Recycler Dispatch Batch': 'M18-form-batch',
  'M18:Green & Destruction Certificate': 'M18-form-cert',
  'M18:Collection Drive Event': 'M18-form-event',
  'M18:Battery & Hazardous Dossier': 'M18-form-battery',
  'M18:Authorized Recycler Partner': 'M18-form-partner',
  'M18:Statutory Environmental Return': 'M18-form-return',
  'M18:Basel Prior Informed Consent': 'M18-form-pic',
  'M18:DoE E-Waste Registration': 'M18-form-registration',
  'M18:E-Waste Incentive / Recycler Money': 'M18-form-settlement',
  'M18:Start Secure Destruction': 'M18-form-destruction',
  'M18:Bind M06 Wipe Certificate': 'M18-form-wipe-bind',
  'M18:Release to Recycler': 'M18-form-release',
  'M18:Recycler Certificate from Batch': 'M18-form-cert-record',
  'M18:__by_model__': {
    'fix.ewaste.collection': 'M18-form-collection',
    'fix.ewaste.triage': 'M18-form-triage',
    'fix.ewaste.batch': 'M18-form-batch',
    'fix.ewaste.certificate': 'M18-form-cert',
    'fix.ewaste.event': 'M18-form-event',
    'fix.ewaste.battery': 'M18-form-battery',
    'fix.ewaste.partner': 'M18-form-partner',
    'fix.ewaste.return': 'M18-form-return',
    'fix.esg.metric': 'M18-form-esg',
    'fix.ewaste.basel.pic': 'M18-form-pic',
    'fix.ewaste.registration': 'M18-form-registration',
    'fix.ewaste.settlement': 'M18-form-settlement'
  },
  'M18:__by_screen__': {
    'M18-intake': 'M18-form-collection',
    'M18-triage': 'M18-form-triage',
    'M18-drives': 'M18-form-event',
    'M18-battery': 'M18-form-battery',
    'M18-batches': 'M18-form-batch',
    'M18-partners': 'M18-form-partner',
    'M18-certs': 'M18-form-cert',
    'M18-returns': 'M18-form-return',
    'M18-esg': 'M18-form-esg',
    'M18-pic': 'M18-form-pic',
    'M18-registration': 'M18-form-registration',
    'M18-settlements': 'M18-form-settlement'
  }
};

export const CREATE = {
  M18: { screen: 'M18-form-collection', model: 'fix.ewaste.collection', label: 'Collection Intake' }
};
