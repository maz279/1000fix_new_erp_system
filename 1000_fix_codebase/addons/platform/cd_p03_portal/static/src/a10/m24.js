/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M24 Documents & E-Signature.
 * Registry-faithful: 4 groups / 9 screens / 4 reports / 4 forms / freg 56. */

export const MODULE = {
  area: 'A10', code: 'M24', en: 'Documents & E-Signature', title: 'M24 · Documents & E-Signature',
  bn: 'নথি ও ই-স্বাক্ষর', icon: '📄',
  desc: 'Governed document repository with bilingual full-text search, controlled documents and template generation, e-signature envelopes with tamper-evidence, retention enforcement, legal holds and defensible disposal.',
  kpis: [
    { l: 'Documents', m: 'documents' },
    { l: 'Auto-Filed', m: 'auto_filed' },
    { l: 'Search p95', m: 'search_p95' },
    { l: 'Pending e-Signatures', m: 'pending_esignatures' },
    { l: 'Legal Holds', m: 'legal_holds' },
    { l: 'Evidence Packs', m: 'evidence_packs_5min' }
  ],
  groups: [
    { en: 'Repository', screens: [
      { id: 'M24-browser', en: 'Document Browser', bn: 'দলিল ব্রাউজার', t: 'g' },
      { id: 'M24-search', en: 'Bilingual Full-Text + OCR', bn: 'পূর্ণ-পাঠ অনুসন্ধান', t: 'r' }
    ]},
    { en: 'Workflows', screens: [
      { id: 'M24-controlled', en: 'Controlled Documents', bn: 'নিয়ন্ত্রিত দলিল', t: 'g' },
      { id: 'M24-generation', en: 'Templates & Generation', bn: 'টেমপ্লেট', t: 'g' }
    ]},
    { en: 'E-Signature', screens: [
      { id: 'M24-envelopes', en: 'Signature Envelopes', bn: 'স্বাক্ষর খাম', t: 'g' },
      { id: 'M24-audit', en: 'Tamper Evidence & Audit', bn: 'ট্যাম্পার প্রমাণ', t: 'g' }
    ]},
    { en: 'Retention', screens: [
      { id: 'M24-retention', en: 'Retention Enforcement', bn: 'সংরক্ষণ নীতি', t: 'g' },
      { id: 'M24-holds', en: 'Legal Holds', bn: 'আইনি আটক', t: 'g' },
      { id: 'M24-disposal', en: 'Defensible Disposal', bn: 'নিষ্পত্তি', t: 'g' }
    ]}
  ],
  reports: ['Retention Compliance', 'Signature Status', 'Repository Growth', 'Access Audit Export'],
  forms: ['Upload', 'Signature Envelope', 'Share Token', 'Retention Policy'],
  cross: ['M23 QMS', 'M08 Contracts', 'M60 GRC', 'M21 HR'],
  freg: { src: 56, sub: [
    ['1', 'Repository & Integrity', 7, { model: 'fix.document', cols: ['name', 'document_type', 'version', 'is_current', 'checksum_sha256'], screens: ['M24-browser'] }],
    ['2', 'Auto-Filing', 6, { model: 'fix.document', cols: ['name', 'document_type', 'res_model', 'res_id', 'template_id'], screens: ['M24-generation', 'M24-browser'] }],
    ['3', 'Classification & Search', 9, { model: 'fix.document', cols: ['name', 'name_bn', 'document_type', 'isolation_tier', 'retention_class_id'], screens: ['M24-search', 'M24-browser'] }],
    ['4', 'Versioning & Control', 7, { model: 'fix.document', cols: ['name', 'version', 'is_current', 'previous_version_id', 'template_id'], screens: ['M24-controlled'] }],
    ['5', 'E-Signature', 10, { model: 'fix.esignature.envelope', cols: ['name', 'document_id', 'state', 'completed_at'], screens: ['M24-envelopes', 'M24-audit'] }],
    ['6', 'Retention & Holds', 10, { model: 'fix.document', cols: ['name', 'retention_class_id', 'retention_expires', 'legal_hold', 'state'], screens: ['M24-retention', 'M24-holds', 'M24-disposal'] }],
    ['7', 'Evidence Packs', 7, { model: 'fix.document', cols: ['name', 'version', 'retention_class_id', 'legal_hold', 'state'], screens: ['M24-browser'], domain: [['document_type', '=', 'evidence_pack']] }]
  ] }
};

export const SCREENS = {
  'M24-browser': { kind: 'model_list', model: 'fix.document',
    cols: ['name', 'name_bn', 'version', 'is_current', 'document_type', 'retention_class_id', 'retention_expires', 'legal_hold'] },
  'M24-search': { kind: 'table_report', module: 'M24', report: 'access_audit', title: 'Bilingual Full-Text + OCR', period: false },
  'M24-controlled': { kind: 'model_list', model: 'fix.document',
    cols: ['name', 'version', 'control_state', 'is_current', 'document_type', 'approved_by_id', 'published_on'],
    actions: [
      { m: 'action_submit_review', l: 'Submit for Approval', asks: [{ label: 'Justification', kwarg: 'justification' }] },
      { m: 'action_publish', l: 'Publish Approved Version' },
      { m: 'action_new_revision', l: 'Start New Revision' }
    ] },
  'M24-generation': { kind: 'model_list', model: 'fix.document.template',
    cols: ['name', 'document_type', 'requires_approval'] },
  'M24-envelopes': { kind: 'model_list', model: 'fix.esignature.envelope', stateField: 'state',
    cols: ['name', 'document_id', 'state', 'deadline', 'completed_at'],
    actions: [
      { m: 'action_send', l: 'Send Envelope' },
      { m: 'action_check_complete', l: 'Check Complete' },
      { m: 'action_void', l: 'Void', asks: [{ label: 'Why is the envelope voided?', kwarg: 'reason' }] }
    ] },
  'M24-audit': { kind: 'model_list', create: false, model: 'fix.esignature.signer',
    cols: ['envelope_id', 'sequence', 'signer_name', 'role_label', 'signed_at', 'signature_provider', 'auth_method'],
    actions: [
      { m: 'action_sign', l: 'Sign (own login)', asks: [{ label: 'Signature provider reference (optional)', kwarg: 'provider' }] },
      { m: 'action_decline', l: 'Decline', asks: [{ label: 'Reason for refusing', kwarg: 'reason' }] }
    ] },
  'M24-retention': { kind: 'model_list', model: 'fix.retention.class',
    cols: ['name', 'retention_years', 'expiry_action'] },
  'M24-holds': { kind: 'model_list', create: false, model: 'fix.legal.hold',
    cols: ['matter_ref', 'document_id', 'placed_by_id', 'placed_on', 'state', 'released_on'],
    actions: [
      { m: 'action_release', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] }
    ] },
  'M24-disposal': { kind: 'model_list', create: false, model: 'fix.disposal.record',
    cols: ['name', 'document_id', 'method', 'disposed_on', 'performed_by_id', 'certificate_doc_id'] },

  /* Report chips -> their own computed pack */
  'M24-rpt-retention': { kind: 'table_report', module: 'M24', report: 'retention_compliance', title: 'Retention Compliance', period: false },
  'M24-rpt-signature': { kind: 'table_report', module: 'M24', report: 'signature_status', title: 'Signature Status', period: false },
  'M24-rpt-growth': { kind: 'table_report', module: 'M24', report: 'repository_growth', title: 'Repository Growth', period: false },
  'M24-rpt-audit': { kind: 'table_report', module: 'M24', report: 'access_audit', title: 'Access Audit Export', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M24-form-document': {
    kind: 'model_form',
    model: 'fix.document',
    title: 'Upload Document',
    back: 'M24-browser',
    sections: [
      { title: 'Document', note: 'Name, type and retention class; the retention expiry is computed from the class and the creation date, and a legal hold overrides disposal.',
        fields: [
          { name: 'upload_file', type: 'file', required: true, label: 'File' },
          { name: 'upload_filename', label: 'File Name' },
          { name: 'name', required: true, label: 'Document Name' },
          { name: 'name_bn', label: 'Name (Bengali)' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'retention_class_id', label: 'Retention Class' },
          { name: 'is_controlled', label: 'Controlled document (draft → review → approval → publication)' },
          { name: 'description', type: 'text', label: 'Description' }
        ] }
    ]
  },

  'M24-form-envelope': {
    kind: 'model_form',
    model: 'fix.esignature.envelope',
    title: 'Signature Envelope',
    back: 'M24-envelopes',
    status: { field: 'state', labels: {
      draft: 'Draft', sent: 'Sent', partially_signed: 'Partially Signed', completed: 'Completed', declined: 'Declined', expired: 'Expired', voided: 'Voided' } },
    sections: [
      { title: 'Envelope', note: 'An envelope binds one document to its signers. Sending it seals the evidence hash over the document bytes, locks the file and opens the signing window; each signer signs with their own login and completion files a certificate.',
        fields: [
          { name: 'name', required: true, label: 'Subject' },
          { name: 'document_id', required: true, label: 'Document' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ] }
    ]
  },

  'M24-form-template': {
    kind: 'model_form',
    model: 'fix.document.template',
    title: 'Document Template',
    back: 'M24-generation',
    sections: [
      { title: 'Template', note: 'Template name and the document type it generates.',
        fields: [
          { name: 'code', required: true, label: 'Template Code' },
          { name: 'name', required: true, label: 'Template Name' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M24-form-retention': {
    kind: 'model_form',
    model: 'fix.retention.class',
    title: 'Retention Policy',
    back: 'M24-retention',
    sections: [
      { title: 'Retention Class', note: 'The class sets the retention period applied to every document filed under it.',
        fields: [
          { name: 'code', required: true, label: 'Class Code' },
          { name: 'name', required: true, label: 'Class Name' },
          { name: 'retention_years', required: true, label: 'Retention (years)' },
          { name: 'expiry_action', required: true, label: 'At Expiry' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M24:Retention Compliance': 'M24-rpt-retention',
  'M24:Signature Status': 'M24-rpt-signature',
  'M24:Repository Growth': 'M24-rpt-growth',
  'M24:Access Audit Export': 'M24-rpt-audit'
};

export const FORM_MODELS = {
  'M24:Upload': 'fix.document',
  'M24:Signature Envelope': 'fix.esignature.envelope',
  'M24:Share Token': 'fix.document',
  'M24:Retention Policy': 'fix.retention.class'
};

export const FORM_CHIPS = {
  'M24:Upload': 'M24-form-document',
  'M24:Signature Envelope': 'M24-form-envelope',
  'M24:Share Token': 'M24-form-document',
  'M24:Retention Policy': 'M24-form-retention',
  'M24:__by_model__': {
    'fix.document': 'M24-form-document',
    'fix.esignature.envelope': 'M24-form-envelope',
    'fix.document.template': 'M24-form-template',
    'fix.retention.class': 'M24-form-retention'
  },
  'M24:__by_screen__': {
    'M24-browser': 'M24-form-document',
    'M24-controlled': 'M24-form-document',
    'M24-generation': 'M24-form-template',
    'M24-envelopes': 'M24-form-envelope',
    'M24-retention': 'M24-form-retention'
  }
};

export const CREATE = {
  M24: { screen: 'M24-form-document', model: 'fix.document', label: 'Document' }
};
