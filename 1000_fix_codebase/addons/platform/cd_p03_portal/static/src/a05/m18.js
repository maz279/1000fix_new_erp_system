/** @odoo-module **/
/* A05 — Circular Economy — M18 E-Waste & Circular Economy (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault on all 9 forms.
 * All 6 report packs exposed as chips (including ESG Materiality Report).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev. */

export const MODULE = {
  area: 'A05', code: 'M18', en: 'E-Waste & Recycling', title: 'M18 — E-Waste & Recycling',
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
      { id: 'M18-triage', en: 'Triage & Disposition', bn: 'বাছাই ও নিষ্পত্তি', t: 'c' },
      { id: 'M18-drives', en: 'Public Drives & Bins', bn: 'গণ সংগ্রহ কর্মসূচি', t: 'g' },
      { id: 'M18-battery', en: 'Hazardous & Battery Log', bn: 'ব্যাটারি ও বিপজ্জনক বর্জ্য', t: 'g' }
    ]},
    { en: 'Processing & Custody', screens: [
      { id: 'M18-batches', en: 'Recycler Batches', bn: 'রিসাইক্লার চালান', t: 'g' },
      { id: 'M18-partners', en: 'Authorized Recyclers', bn: 'অনুমোদিত পুনর্ব্যবহারকারী', t: 'g' },
      { id: 'M18-certs', en: 'Green Certificates', bn: 'সবুজ সনদপত্র', t: 'g' },
      { id: 'M18-manifest', en: 'Chain of Custody', bn: 'হস্তান্তর শৃঙ্খলা', t: 'g' }
    ]},
    { en: 'Statutory & ESG', screens: [
      { id: 'M18-returns', en: 'Statutory Returns (DoE)', bn: 'পরিবেশ অধিদপ্তর বিবরণী', t: 'g' },
      { id: 'M18-esg', en: 'ESG Metrics', bn: 'ইএসজি সূচক', t: 'g' },
      { id: 'M18-epr', en: 'EPR Compliance Pack', bn: 'ইপিআর কমপ্লায়েন্স', t: 'r' }
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
    'ESG Materiality Metric'
  ],
  cross: ['M17 retired assets', 'M14 non-repairable trade-ins', 'M06 customer drop-offs', 'M03 hazardous transit'],
  freg: { src: 82, sub: [
    ['1', 'Intake & Channels', 8], ['2', 'Triage & Disposition', 10],
    ['3', 'Data Destruction', 7], ['4', 'Outbound Recycler', 8],
    ['5', 'Green Certificates', 7], ['6', 'Public Drives & Bins', 7],
    ['7', 'Hazardous Fraction', 9], ['8', 'EPR Reporting', 8],
    ['9', 'ESG & Carbon', 9], ['10', 'Compliance Pack', 9]
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
      { m: 'action_recycle_estimated', l: 'Recycle Est.' },
      { m: 'action_issue_certificate', l: 'Issue Cert' }
    ] },
  'M18-triage': { kind: 'model_list', model: 'fix.ewaste.triage',
    cols: ['name', 'collection_id', 'decision', 'inspector_id', 'decided_on', 'wipe_required', 'data_bearing'] },
  'M18-drives': { kind: 'model_list', model: 'fix.ewaste.event', stateField: 'state',
    cols: ['name', 'venue', 'event_date', 'operating_unit_id', 'target_kg', 'collected_kg', 'state'] },
  'M18-battery': { kind: 'model_list', model: 'fix.ewaste.battery', stateField: 'state',
    cols: ['name', 'chemistry', 'hazard_class', 'storage_location', 'weight_kg', 'swollen_cell', 'terminal_taped', 'state'],
    actions: [
      { m: 'action_inspect_and_quarantine', l: 'Inspect & Quarantine' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_process', l: 'Process' }
    ] },
  'M18-batches': { kind: 'model_list', model: 'fix.ewaste.batch', stateField: 'state',
    cols: ['name', 'partner_id', 'material_type', 'weight_kg', 'transfer_note_ref', 'dispatched_on', 'state'],
    actions: [{ m: 'action_dispatch', l: 'Dispatch Batch' }] },
  'M18-partners': { kind: 'model_list', model: 'fix.ewaste.partner', stateField: 'state',
    cols: ['name', 'partner_id', 'capability', 'certification', 'certificate_no', 'valid_to', 'state'] },
  'M18-certs': { kind: 'model_list', model: 'fix.ewaste.certificate', stateField: 'state',
    cols: ['name', 'certificate_no', 'partner_id', 'material_type', 'weight_kg', 'issued_on', 'file_ref', 'state'] },
  'M18-manifest': { kind: 'table_report', module: 'M18', report: 'compliance_pack', title: 'Chain of Custody Manifest', period: true },
  'M18-returns': { kind: 'model_list', model: 'fix.ewaste.return', stateField: 'state',
    cols: ['name', 'authority', 'period', 'form_type', 'due_date', 'recovery_rate_pct', 'submitted_on', 'state'],
    actions: [
      { m: 'action_calculate_mass_balance', l: 'Calc Balance' },
      { m: 'action_submit_return', l: 'Submit DoE' },
      { m: 'action_accept_return', l: 'Accept DoE' }
    ] },
  'M18-esg': { kind: 'model_list', model: 'fix.esg.metric',
    cols: ['name', 'metric_type', 'period', 'value', 'unit', 'operating_unit_id'] },
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
    status: { field: 'state', labels: { draft: 'Draft', collected: 'Collected', triaged: 'Triaged', dispatched: 'Dispatched', certified: 'Certified' } },
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
          { name: 'customer_id', label: 'Corporate / Retail Source' },
          { name: 'operating_unit_id', label: 'Receiving Hub' },
          { name: 'state', label: 'Collection State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Physical Mass Balance Classification',
        fields: [
          { name: 'weight_kg', required: true, label: 'Intake Mass (kg)' },
          { name: 'material_type', required: true, label: 'Schedule-1 Category (Phone/Laptop/Battery/Other)' },
          { name: 'triage_grade', label: 'Triage Grade' }
        ] },
      { tab: 'technical', title: 'Data Sanitization & Destruction',
        fields: [
          { name: 'wipe_certificate_id', label: 'NIST 800-88 Data Sanitization Certificate' },
          { name: 'disposal_certificate_ref', label: 'Final Destruction Proof Reference' }
        ] },
      { tab: 'lifecycle', title: 'Environmental Traceability & Impact',
        fields: [
          { name: 'esg_co2_saved_kg', label: 'Calculated CO2e Avoidance (kg)', readonly: true },
          { name: 'event_id', label: 'Origin Public Collection Campaign' },
          { name: 'batch_id', label: 'Downstream Recycler Batch' },
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
          { name: 'collection_id', required: true, label: 'Origin Collection Item' },
          { name: 'decision', required: true, label: 'Triage Disposition Decision' }
        ] },
      { tab: 'pricing', title: 'Disposition Routing',
        fields: [
          { name: 'decision', label: 'Final Route (Reuse/Refurbish/Recycle/Hazardous)' }
        ] },
      { tab: 'technical', title: 'Data Bearing Identification',
        fields: [
          { name: 'data_bearing', label: 'Contains Storage / Data Bearing Media' },
          { name: 'wipe_required', label: 'Mandatory Secure Data Wipe' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Evaluation',
        fields: [
          { name: 'inspector_id', required: true, label: 'Triage Officer' },
          { name: 'decided_on', label: 'Decision Timestamp' },
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
    status: { field: 'state', labels: { draft: 'Draft', sealed: 'Sealed & Weighed', dispatched: 'Dispatched to Recycler', settled: 'Settled' } },
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
          { name: 'partner_id', required: true, label: 'Authorized Recycler Partner' },
          { name: 'operating_unit_id', label: 'Dispatch Hub' },
          { name: 'state', label: 'Batch Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Weighbridge & Fraction',
        fields: [
          { name: 'weight_kg', required: true, label: 'Gross Verified Mass (kg)' },
          { name: 'material_type', required: true, label: 'Material Classification' }
        ] },
      { tab: 'technical', title: 'Transfer Documentation (S.R.O. 187 Form-2)',
        fields: [
          { name: 'transfer_note_ref', label: 'Waste Transfer Manifest Ref' },
          { name: 'dispatched_on', label: 'Departure Timestamp' }
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
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued', verified: 'Verified', voided: 'Voided' } },
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
          { name: 'certificate_no', required: true, label: 'Official Certificate Number' },
          { name: 'partner_id', label: 'Recipient / Client Entity' },
          { name: 'state', label: 'Certification Status', readonly: true }
        ] },
      { tab: 'pricing', title: 'Certified Mass Balance',
        fields: [
          { name: 'weight_kg', label: 'Certified E-Waste Mass (kg)' },
          { name: 'material_type', label: 'Material Fraction' }
        ] },
      { tab: 'technical', title: 'Issuance & Verification Proof',
        fields: [
          { name: 'issued_on', label: 'Official Issue Date' },
          { name: 'file_ref', label: 'Cryptographic Hash Reference (SHA-256)' }
        ] },
      { tab: 'lifecycle', title: 'Custody Chain Lineage',
        fields: [
          { name: 'collection_id', label: 'Source Collection Record' },
          { name: 'batch_id', label: 'Origin Bulk Dispatch Batch' }
        ] },
      { tab: 'governance', title: 'Issuing Authority',
        fields: [
          { name: 'company_id', label: 'Company' }
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
    status: { field: 'state', labels: { planned: 'Planned', active: 'Live / Open', closed: 'Closed & Reconciled' } },
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
    status: { field: 'state', labels: { received: 'Received', quarantined: 'Quarantined', dispatched: 'Dispatched to Smelter', processed: 'Safe Disposal' } },
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
          { name: 'terminal_taped', required: true, label: 'Terminals Insulated & Taped (Short-Circuit Prevention)' },
          { name: 'swollen_cell', required: true, label: 'Thermal Runaway Risk / Swollen Cell Detected' },
          { name: 'quarantine_barrel_ref', label: 'Fire-Safe Vermiculite Quarantine Barrel' }
        ] },
      { tab: 'lifecycle', title: 'Storage & Downstream Traceability',
        fields: [
          { name: 'storage_location', label: 'Flame-Proof Storage Bunker' },
          { name: 'received_on', label: 'Intake Date' },
          { name: 'operating_unit_id', label: 'Intake Unit' },
          { name: 'collection_id', label: 'Origin Collection Dossier' },
          { name: 'batch_id', label: 'Consolidated Outbound Batch' },
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
    status: { field: 'state', labels: { active: 'Active & Certified', audit_pending: 'Audit Pending', suspended: 'Suspended' } },
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
          { name: 'name', label: 'Profile Title', readonly: true },
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
          { name: 'certificate_no', required: true, label: 'DoE License Number' },
          { name: 'valid_from', label: 'License Effective Date' },
          { name: 'valid_to', label: 'License Expiry Date' }
        ] },
      { tab: 'lifecycle', title: 'Audit Verification',
        fields: [
          { name: 'state', label: 'Current Audit Standing' }
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
    status: { field: 'state', labels: { draft: 'Draft', prepared: 'Prepared', submitted: 'Submitted to DoE', accepted: 'Accepted by DoE' } },
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
          { name: 'total_tonnage_collected', label: 'Gross Collected Tonnage (MT)' },
          { name: 'total_tonnage_recycled', label: 'Total Recycled Tonnage (MT)' },
          { name: 'recovery_rate_pct', label: 'Recovery Rate (% Target: 30%-50%)', readonly: true }
        ] },
      { tab: 'technical', title: 'Timetable & Regulatory Receipt',
        fields: [
          { name: 'due_date', required: true, label: 'Statutory Submission Deadline' },
          { name: 'submitted_on', label: 'Official Submission Date' },
          { name: 'is_overdue', label: 'Statutory Overdue Flag', readonly: true },
          { name: 'reference', label: 'DoE Acknowledgment Number' }
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
          { name: 'name', required: true, label: 'Indicator Title (e.g., Avoided Scope 3 CO2e)' },
          { name: 'metric_type', required: true, label: 'GRI/SASB Materiality Type' },
          { name: 'period', required: true, label: 'Reporting Period' }
        ] },
      { tab: 'pricing', title: 'Quantification',
        fields: [
          { name: 'value', required: true, label: 'Reported Metric Value' },
          { name: 'unit', required: true, label: 'Unit of Measure (kg / MT / %)' }
        ] },
      { tab: 'technical', title: 'Operational Hub',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ] },
      { tab: 'lifecycle', title: 'Sustainability Timeline',
        fields: [
          { name: 'period', label: 'Audit Cycle Period' }
        ] },
      { tab: 'governance', title: 'Company Context',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Evidence & Document Vault',
        fields: [
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
  'M18:ESG Materiality Metric': 'fix.esg.metric'
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
  'M18:ESG Materiality Metric': 'M18-form-esg',
  'M18:__by_model__': {
    'fix.ewaste.collection': 'M18-form-collection',
    'fix.ewaste.triage': 'M18-form-triage',
    'fix.ewaste.batch': 'M18-form-batch',
    'fix.ewaste.certificate': 'M18-form-cert',
    'fix.ewaste.event': 'M18-form-event',
    'fix.ewaste.battery': 'M18-form-battery',
    'fix.ewaste.partner': 'M18-form-partner',
    'fix.ewaste.return': 'M18-form-return',
    'fix.esg.metric': 'M18-form-esg'
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
    'M18-esg': 'M18-form-esg'
  }
};

export const CREATE = {
  M18: { screen: 'M18-form-collection', model: 'fix.ewaste.collection', label: 'Collection Intake' }
};
