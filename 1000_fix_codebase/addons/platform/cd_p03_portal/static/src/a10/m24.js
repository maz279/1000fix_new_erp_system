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
    { l: 'Search p95', m: 'search_p95', src: false },
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
  /* 13 Nov 2026 capture audit: every sub-module page captures its own record.
   * Before it, Auto-Filing and Retention & Holds offered "+ New Document" (an
   * upload), Versioning listed every document, the envelope form could add no
   * signer (so no envelope could ever be sent), the template form could never
   * save (a bilingual template needs its Bengali name, which it did not show)
   * and no page could place a legal hold or dispose of a document.
   * 'Workshop Evidence Item' is M31's form: evidence-pack documents are filed
   * from the workshop job (and pulled into a brand claim by M09). */
  forms: ['Upload', 'Controlled Document', 'Document Template', 'Signature Envelope', 'Retention Policy',
    'Place Legal Hold', 'Dispose of Document', 'Workshop Evidence Item'],
  cross: ['M23 QMS', 'M08 Contracts', 'M60 GRC', 'M21 HR'],
  freg: { src: 56, sub: [
    ['1', 'Repository & Integrity', 7, { model: 'fix.document', cols: ['name', 'document_type', 'version', 'is_current', 'checksum_sha256'], screens: ['M24-browser'], reports: ['Repository Growth'], forms: ['Upload'] }],
    /* filed by a transaction (a linked record), not uploaded by a person: the
     * human input here is the template that generates the document */
    ['2', 'Auto-Filing', 6, { model: 'fix.document', cols: ['name', 'document_type', 'res_model', 'res_id', 'template_id'], screens: ['M24-generation', 'M24-browser'], reports: [], forms: ['Document Template'], create: 'M24-form-template', domain: [['res_model', '!=', false]] }],
    ['3', 'Classification & Search', 9, { model: 'fix.document', cols: ['name', 'name_bn', 'document_type', 'isolation_tier', 'retention_class_id'], screens: ['M24-search', 'M24-browser'], reports: ['Access Audit Export'], forms: ['Upload'] }],
    ['4', 'Versioning & Control', 7, { model: 'fix.document', cols: ['name', 'version', 'control_state', 'is_current', 'previous_version_id'], screens: ['M24-controlled'], reports: [], forms: ['Controlled Document'], create: 'M24-form-controlled', domain: [['is_controlled', '=', true]] }],
    ['5', 'E-Signature', 10, { model: 'fix.esignature.envelope', cols: ['name', 'document_id', 'state', 'completed_at'], screens: ['M24-envelopes', 'M24-audit'], reports: ['Signature Status'], forms: ['Signature Envelope'] }],
    /* a hold and a disposal act on an EXISTING document (Records Officer);
     * a retention class is configuration only an administrator may save */
    ['6', 'Retention & Holds', 10, { model: 'fix.document', cols: ['name', 'retention_class_id', 'retention_expires', 'legal_hold', 'state'], screens: ['M24-retention', 'M24-holds', 'M24-disposal'], reports: ['Retention Compliance'], forms: ['Place Legal Hold', 'Dispose of Document', 'Retention Policy'], create: 'M24-form-hold' }],
    ['7', 'Evidence Packs', 7, { model: 'fix.document', cols: ['name', 'version', 'retention_class_id', 'legal_hold', 'state'], screens: ['M24-browser'], reports: [], forms: ['Workshop Evidence Item'], create: false, domain: [['document_type', '=', 'evidence_pack']] }]
  ] }
};

export const SCREENS = {
  'M24-browser': { kind: 'model_list', model: 'fix.document',
    cols: ['name', 'name_bn', 'version', 'is_current', 'document_type', 'retention_class_id', 'retention_expires', 'legal_hold', 'state'],
    /* holds and disposal are Records Officer decisions, refused to anyone else */
    actions: [
      { m: 'action_legal_hold', l: 'Place Legal Hold', asks: [{ label: 'Matter reference (case, notice or inquiry)', kwarg: 'matter_ref' }] },
      { m: 'action_release_hold', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] },
      { m: 'action_dispose', l: 'Dispose (retention expired)' }
    ],
    empty: 'No document is filed yet. + New Document uploads one; transactions file theirs automatically.' },
  'M24-search': { kind: 'table_report', module: 'M24', report: 'access_audit', title: 'Bilingual Full-Text + OCR', period: false },
  'M24-controlled': { kind: 'model_list', model: 'fix.document', domain: [['is_controlled', '=', true]],
    empty: 'No controlled document yet. + New Controlled Document starts a policy, procedure or form as a draft.',
    cols: ['name', 'version', 'control_state', 'is_current', 'document_type', 'approved_by_id', 'published_on'],
    actions: [
      { m: 'action_submit_review', l: 'Submit for Approval', asks: [{ label: 'Justification', kwarg: 'justification' }] },
      { m: 'action_publish', l: 'Publish Approved Version' },
      { m: 'action_new_revision', l: 'Start New Revision' }
    ] },
  'M24-generation': { kind: 'model_list', model: 'fix.document.template',
    cols: ['code', 'name', 'name_bn', 'document_type', 'bilingual', 'requires_approval'] },
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
    empty: 'No legal hold on the register. A hold is placed on an existing document with + Place Legal Hold on the Retention & Holds page, or Place Legal Hold on the Document Browser.',
    actions: [
      { m: 'action_release', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] }
    ] },
  'M24-disposal': { kind: 'model_list', create: false, model: 'fix.disposal.record',
    cols: ['name', 'document_id', 'method', 'disposed_on', 'performed_by_id', 'certificate_doc_id'],
    empty: 'Nothing disposed yet. A document whose retention has expired, and that is not on hold, is disposed with Dispose of Document; the register entry and its certificate are written by the system.' },

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
          { name: 'isolation_tier', label: 'Confidentiality Tier (who may read it)' },
          { name: 'is_controlled', label: 'Controlled document (draft → review → approval → publication)' },
          { name: 'description', type: 'text', label: 'Description' }
        ] }
    ]
  },

  /* A policy, procedure or form under ISO 9001 7.5.3 control: it starts as a
   * draft, is approved by a Document Controller who is not its author, and
   * publishing it supersedes the previous version. */
  'M24-form-controlled': {
    kind: 'model_form',
    model: 'fix.document',
    title: 'Controlled Document',
    newLabel: 'New Controlled Document',
    back: 'M24-controlled',
    status: { field: 'control_state' },
    sections: [
      { title: 'Controlled Document', note: 'Saved as a draft. Submit for Approval on Controlled Documents sends it to a Document Controller, never to its author; Publish Approved Version makes it the current issue and supersedes the one before. A published version is frozen: a correction is a new revision.',
        fields: [
          { name: 'upload_file', type: 'file', required: true, label: 'File' },
          { name: 'upload_filename', label: 'File Name' },
          { name: 'name', required: true, label: 'Document Title' },
          { name: 'name_bn', label: 'Title (Bengali)' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'retention_class_id', label: 'Retention Class' },
          { name: 'is_controlled', value: true, label: 'Controlled document' },
          { name: 'description', type: 'text', label: 'Scope & Change Summary' },
          { name: 'version', label: 'Version', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'published_on', label: 'Published On', readonly: true }
        ] }
    ]
  },

  /* Step 1 picks the document, step 2 records the matter: the hold is placed
   * by action_legal_hold (Records Officer only), which stamps who and when
   * and writes the legal-hold register row. */
  'M24-form-hold': {
    kind: 'model_form',
    model: 'fix.document',
    title: 'Place Legal Hold',
    newLabel: 'Place Legal Hold',
    back: 'M24-holds',
    pickRecord: {
      label: 'Step 1 of 2: choose the document to hold',
      note: 'Documents not already on hold and not destroyed. A hold freezes the document and stops its retention clock until it is released.',
      search: 'Search document',
      choose: 'Hold this document',
      cols: ['name', 'document_type', 'retention_class_id', 'retention_expires', 'state'],
      domain: [['legal_hold', '=', false], ['state', '!=', 'destroyed']],
      empty: 'There is no document that can be held. A hold is placed on an existing document: upload or file it first.'
    },
    saveAction: {
      method: 'action_legal_hold', label: 'Place Hold', done: 'Legal hold placed: the document is frozen and cannot be disposed',
      kwargs: { matter_ref: 'legal_hold_reason' }
    },
    sections: [
      { title: 'Step 2 of 2: Matter Reference', note: 'Only a Records Officer (Legal/Records) may place or release a hold. The hold, who placed it and when are written to the legal-hold register.',
        fields: [
          { name: 'name', label: 'Document', readonly: true },
          { name: 'document_type', label: 'Document Type', readonly: true },
          { name: 'retention_class_id', label: 'Retention Class', readonly: true },
          { name: 'retention_expires', label: 'Retention Expires', readonly: true },
          /* guarded on the record; an input here because saveAction carries it */
          { name: 'legal_hold_reason', label: 'Matter Reference (case, notice or inquiry)', required: true, readonly: true }
        ] }
    ]
  },

  /* Defensible disposal of one expired document: action_dispose (Records
   * Officer only) refuses a held or unexpired document, issues the
   * destruction certificate, writes the permanent disposal register entry
   * and wipes the file. */
  'M24-form-dispose': {
    kind: 'model_form',
    model: 'fix.document',
    title: 'Dispose of Document',
    newLabel: 'Dispose of Document',
    back: 'M24-disposal',
    pickRecord: {
      label: 'Step 1 of 2: choose the expired document',
      note: 'Only documents whose retention has expired and that are not on hold. Disposal cannot be undone.',
      search: 'Search document',
      choose: 'Dispose of this document',
      cols: ['name', 'document_type', 'retention_class_id', 'retention_expires', 'state'],
      domain: [['state', 'in', ['expired', 'pending_destruction']], ['legal_hold', '=', false]],
      empty: 'No document is due for disposal: the daily retention sweep marks a document expired when its retention class has elapsed.'
    },
    saveAction: {
      method: 'action_dispose', label: 'Dispose & Issue Certificate', done: 'Disposed: the certificate and the register entry are filed',
      kw: { method: 'secure_wipe' }, kwargs: {}
    },
    sections: [
      { title: 'Step 2 of 2: Confirm Disposal', note: 'Only a Records Officer (Legal/Records) may dispose. The file is wiped securely; its name, class and dates stay on the permanent disposal register with the destruction certificate.',
        fields: [
          { name: 'name', label: 'Document', readonly: true },
          { name: 'document_type', label: 'Document Type', readonly: true },
          { name: 'retention_class_id', label: 'Retention Class', readonly: true },
          { name: 'retention_expires', label: 'Retention Expired On', readonly: true },
          { name: 'state', label: 'Status', readonly: true }
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
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'sent_at', label: 'Sent At', readonly: true },
          { name: 'deadline', label: 'Signing Deadline', readonly: true },
          { name: 'completed_at', label: 'Completed At', readonly: true },
          { name: 'evidence_hash', label: 'Evidence Hash (SHA-256)', readonly: true }
        ] }
    ],
    /* An envelope cannot be sent without a signer: the signers ARE the
     * envelope. They join and leave only while it is a draft. */
    lines: {
      field: 'signer_ids',
      title: 'Signers',
      note: 'One row per signer, in signing order (each order number once). Each signer signs with their own login on Tamper Evidence & Audit; the signature, its time and method are stamped, never typed.',
      fields: [
        { name: 'sequence', label: 'Order' },
        { name: 'partner_id', label: 'Signer', required: true },
        { name: 'role_label', label: 'Signs As' },
        { name: 'signed_at', label: 'Signed At', readonly: true },
        { name: 'auth_method', label: 'Authentication', readonly: true }
      ]
    }
  },

  'M24-form-template': {
    kind: 'model_form',
    model: 'fix.document.template',
    title: 'Document Template',
    back: 'M24-generation',
    sections: [
      { title: 'Template', note: 'The template a transaction uses to generate and file its document. A bilingual template carries its Bengali name (every template ships Bengali and English).',
        fields: [
          { name: 'code', required: true, label: 'Template Code' },
          { name: 'name', required: true, label: 'Template Name' },
          { name: 'name_bn', label: 'Template Name (Bengali)' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'bilingual', label: 'Bilingual (Bengali and English)' },
          { name: 'report_ref', label: 'Rendering Report Reference' },
          { name: 'requires_approval', label: 'Generated documents need approval before issue' }
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
  'M24:Controlled Document': 'fix.document',
  'M24:Document Template': 'fix.document.template',
  'M24:Signature Envelope': 'fix.esignature.envelope',
  'M24:Retention Policy': 'fix.retention.class',
  'M24:Place Legal Hold': 'fix.document',
  'M24:Dispose of Document': 'fix.document',
  'M24:Workshop Evidence Item': 'fix.workshop.evidence'
};

export const FORM_CHIPS = {
  'M24:Upload': 'M24-form-document',
  'M24:Controlled Document': 'M24-form-controlled',
  'M24:Document Template': 'M24-form-template',
  'M24:Signature Envelope': 'M24-form-envelope',
  'M24:Retention Policy': 'M24-form-retention',
  'M24:Place Legal Hold': 'M24-form-hold',
  'M24:Dispose of Document': 'M24-form-dispose',
  'M24:Workshop Evidence Item': 'M31-form-evidence',
  'M24:__by_model__': {
    'fix.document': 'M24-form-document',
    'fix.esignature.envelope': 'M24-form-envelope',
    'fix.document.template': 'M24-form-template',
    'fix.retention.class': 'M24-form-retention'
  },
  'M24:__by_screen__': {
    'M24-browser': 'M24-form-document',
    'M24-controlled': 'M24-form-controlled',
    'M24-generation': 'M24-form-template',
    'M24-envelopes': 'M24-form-envelope',
    'M24-retention': 'M24-form-retention'
  }
};

export const CREATE = {
  M24: { screen: 'M24-form-document', model: 'fix.document', label: 'Document' }
};
