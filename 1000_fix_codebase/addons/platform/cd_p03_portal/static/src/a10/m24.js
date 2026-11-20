/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M24 Documents & E-Signature.
 * Registry-faithful: 4 groups / 9 screens / 4 reports / 4 forms / freg 56,
 * plus the capture-pass screens (13 Nov, 19 Nov 2026). */

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
      { id: 'M24-search', en: 'Bilingual Full-Text + OCR', bn: 'পূর্ণ-পাঠ অনুসন্ধান', t: 'r' },
      { id: 'M24-classes', en: 'Document Classes', bn: 'দলিলের শ্রেণি', t: 'g' },
      { id: 'M24-exceptions', en: 'Classification Exceptions', bn: 'শ্রেণিবিন্যাস ব্যতিক্রম', t: 'g' },
      { id: 'M24-physical', en: 'Paper Originals Register', bn: 'মূল কাগজের নিবন্ধন', t: 'g' },
      { id: 'M24-integrity', en: 'Integrity Sweeps', bn: 'অখণ্ডতা যাচাই', t: 'g' }
    ]},
    { en: 'Workflows', screens: [
      { id: 'M24-controlled', en: 'Controlled Documents', bn: 'নিয়ন্ত্রিত দলিল', t: 'g' },
      { id: 'M24-generation', en: 'Templates & Generation', bn: 'টেমপ্লেট', t: 'g' },
      { id: 'M24-distribution', en: 'Distributions', bn: 'বিতরণ', t: 'g' },
      { id: 'M24-acks', en: 'Acknowledgements', bn: 'প্রাপ্তি স্বীকার', t: 'g' }
    ]},
    { en: 'E-Signature', screens: [
      { id: 'M24-envelopes', en: 'Signature Envelopes', bn: 'স্বাক্ষর খাম', t: 'g' },
      { id: 'M24-audit', en: 'Tamper Evidence & Audit', bn: 'ট্যাম্পার প্রমাণ', t: 'g' },
      { id: 'M24-wet', en: 'Wet-Ink Signatures', bn: 'কালির স্বাক্ষর', t: 'g' }
    ]},
    { en: 'Retention', screens: [
      { id: 'M24-retention', en: 'Retention Enforcement', bn: 'সংরক্ষণ নীতি', t: 'g' },
      { id: 'M24-holds', en: 'Legal Holds', bn: 'আইনি আটক', t: 'g' },
      { id: 'M24-disposal', en: 'Defensible Disposal', bn: 'নিষ্পত্তি', t: 'g' },
      { id: 'M24-hold-orders', en: 'Legal Hold Orders', bn: 'আইনি আটক আদেশ', t: 'g' },
      { id: 'M24-batches', en: 'Disposal Batches', bn: 'নিষ্পত্তি ব্যাচ', t: 'g' },
      { id: 'M24-violations', en: 'Retention Violations', bn: 'সংরক্ষণ লঙ্ঘন', t: 'g' }
    ]},
    { en: 'Evidence & Release', screens: [
      { id: 'M24-packs', en: 'Evidence Packs', bn: 'প্রমাণ প্যাক', t: 'g' },
      { id: 'M24-releases', en: 'External Releases', bn: 'বাহ্যিক প্রকাশ', t: 'g' },
      { id: 'M24-access-log', en: 'Access Log', bn: 'প্রবেশ লগ', t: 'g' }
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
   * from the workshop job (and pulled into a brand claim by M09).
   *
   * 19 Nov 2026 second pass: the spec records behind pages 1, 3, 4, 5, 6 and 7
   * had no model. Each page now captures them: paper originals and integrity
   * sweeps (p1), template versions under approval (p2), the class taxonomy
   * and its exception queue (p3), distribution with acknowledgement (p4), a
   * witnessed wet-ink signature and on-demand verification (p5), scoped hold
   * orders, disposal batches approved by someone other than the preparer, and
   * retention violations (p6), evidence packs and controlled external
   * releases - the registry's "Share Token" (p7). "Dispose of Document" is
   * gone: a document is disposed only by an approved batch (FR-DMS-038). */
  forms: ['Upload', 'Controlled Document', 'Document Template', 'Signature Envelope', 'Retention Policy',
    'Place Legal Hold', 'Workshop Evidence Item',
    'Physical Record', 'Integrity Sweep', 'Document Class', 'Distribution', 'Wet-Ink Signature',
    'Legal Hold Order', 'Disposal Batch', 'Retention Violation', 'Evidence Pack', 'Share Token'],
  cross: ['M23 QMS', 'M08 Contracts', 'M60 GRC', 'M21 HR'],
  freg: { src: 56, sub: [
    ['1', 'Repository & Integrity', 7, { model: 'fix.document', cols: ['name', 'document_type', 'version', 'is_current', 'checksum_sha256'], screens: ['M24-browser', 'M24-physical', 'M24-integrity'], reports: ['Repository Growth'], forms: ['Upload', 'Physical Record', 'Integrity Sweep'] }],
    /* filed by a transaction (a linked record), not uploaded by a person: the
     * human input here is the template version that generates the document */
    ['2', 'Auto-Filing', 6, { model: 'fix.document', cols: ['name', 'document_type', 'res_model', 'res_id', 'template_id'], screens: ['M24-generation', 'M24-browser'], reports: [], forms: ['Document Template'], create: 'M24-form-template', domain: [['res_model', '!=', false]] }],
    /* the class decides retention, tier and mandatory metadata; a capture that
     * cannot be classified waits in the exception queue (BRU-DMS-08) */
    ['3', 'Classification & Search', 9, { model: 'fix.document.class', cols: ['code', 'name', 'document_type', 'isolation_tier', 'retention_class_id', 'state'], screens: ['M24-classes', 'M24-exceptions', 'M24-search', 'M24-browser'], reports: ['Access Audit Export'], forms: ['Document Class', 'Upload'], create: 'M24-form-class' }],
    ['4', 'Versioning & Control', 7, { model: 'fix.document', cols: ['name', 'version', 'control_state', 'is_current', 'previous_version_id'], screens: ['M24-controlled', 'M24-distribution', 'M24-acks'], reports: [], forms: ['Controlled Document', 'Distribution'], create: 'M24-form-controlled', domain: [['is_controlled', '=', true]] }],
    ['5', 'E-Signature', 10, { model: 'fix.esignature.envelope', cols: ['name', 'document_id', 'state', 'completed_at', 'verification_result'], screens: ['M24-envelopes', 'M24-audit', 'M24-wet'], reports: ['Signature Status'], forms: ['Signature Envelope', 'Wet-Ink Signature'] }],
    /* a hold acts on an existing document or on a scope (Records Officer);
     * disposal is a batch one officer prepares and another approves; a
     * retention class is configuration only an administrator may save */
    ['6', 'Retention & Holds', 10, { model: 'fix.document', cols: ['name', 'retention_class_id', 'retention_expires', 'legal_hold', 'state'], screens: ['M24-retention', 'M24-holds', 'M24-hold-orders', 'M24-batches', 'M24-disposal', 'M24-violations'], reports: ['Retention Compliance'], forms: ['Place Legal Hold', 'Legal Hold Order', 'Disposal Batch', 'Retention Violation', 'Retention Policy'], create: 'M24-form-hold' }],
    ['7', 'Evidence Packs', 7, { model: 'fix.evidence.pack', cols: ['name', 'purpose', 'subject_label', 'completeness_state', 'assembly_seconds', 'state'], screens: ['M24-packs', 'M24-releases', 'M24-access-log'], reports: [], forms: ['Evidence Pack', 'Share Token', 'Workshop Evidence Item'], create: 'M24-form-pack' }]
  ] }
};

export const SCREENS = {
  'M24-browser': { kind: 'model_list', model: 'fix.document',
    cols: ['name', 'name_bn', 'version', 'is_current', 'document_type', 'retention_class_id', 'retention_expires', 'legal_hold', 'state'],
    /* holds and disposal are Records Officer decisions, refused to anyone else */
    actions: [
      { m: 'action_legal_hold', l: 'Place Legal Hold', asks: [{ label: 'Matter reference (case, notice or inquiry)', kwarg: 'matter_ref' }] },
      { m: 'action_release_hold', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] }
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
  'M24-generation': { kind: 'model_list', model: 'fix.document.template', stateField: 'state',
    cols: ['code', 'version', 'name', 'name_bn', 'document_type', 'state', 'approved_by_id', 'approved_on'],
    actions: [
      { m: 'action_approve', l: 'Approve Version (Document Controller, not the author)' },
      { m: 'action_new_version', l: 'Start New Version' },
      { m: 'action_retire', l: 'Retire Version' }
    ] },
  'M24-envelopes': { kind: 'model_list', model: 'fix.esignature.envelope', stateField: 'state',
    cols: ['name', 'document_id', 'state', 'deadline', 'completed_at', 'verification_result', 'verified_at'],
    actions: [
      { m: 'action_send', l: 'Send Envelope' },
      { m: 'action_check_complete', l: 'Check Complete' },
      { m: 'action_verify', l: 'Verify Signature Evidence' },
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
    cols: ['matter_ref', 'document_id', 'order_id', 'placed_by_id', 'placed_on', 'state', 'released_on'],
    empty: 'No legal hold on the register. Hold one document with + Place Legal Hold, or a whole scope (class, type, business object, filing period) with a Legal Hold Order.',
    actions: [
      { m: 'action_release', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] }
    ] },
  'M24-disposal': { kind: 'model_list', create: false, model: 'fix.disposal.record',
    cols: ['name', 'document_id', 'batch_id', 'method', 'disposed_on', 'performed_by_id', 'certificate_doc_id'],
    empty: 'Nothing disposed yet. Expired documents are disposed by a Disposal Batch: a Records Officer prepares it, a Disposal Approver who did not prepare it approves it, and the system writes each register entry and certificate.' },

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
          /* FR-DMS-005: the business object is the primary index; a class may
           * make the link mandatory (capture pass 2) */
          { name: 'res_model', label: 'Belongs To: Model (e.g. fix.service.order)' },
          { name: 'res_id', label: 'Belongs To: Record ID' },
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
          { name: 'evidence_hash', label: 'Evidence Hash (SHA-256)', readonly: true },
          { name: 'assurance_level', label: 'Required Assurance (from the document class)', readonly: true }
        ] },
      { title: 'Verification (system)', note: 'Verify Signature Evidence on Signature Envelopes re-hashes the document and the signer list against the seal and reads the completion certificate back (FR-DMS-033). Anyone may verify, years later.',
        fields: [
          { name: 'verification_result', label: 'Result', readonly: true },
          { name: 'verified_at', label: 'Verified At', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'verification_note', label: 'Finding', readonly: true }
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
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
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
        ] },
      { title: 'Version & Approval (system)', note: 'A template version is approved by a Document Controller who did not write it, and is never edited afterwards: Start New Version copies it into the next draft. Approving a version retires the one before; a document stays bound to the version it was generated from (FR-DMS-021, BRU-DMS-09).',
        fields: [
          { name: 'version', label: 'Version', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'previous_id', label: 'Replaces', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true }
        ] }
    ]
  },

  /* ============ capture pass 2 (19 Nov 2026) ============ */

  /* ---- page 1: paper originals and integrity sweeps ---- */
  'M24-physical': { kind: 'model_list', model: 'fix.physical.record', stateField: 'state',
    cols: ['name', 'document_id', 'location', 'box_ref', 'custodian_id', 'condition', 'destruction_due_on', 'state'],
    actions: [{ m: 'action_record_destruction', l: 'Record Destruction (Records Officer)' }],
    empty: 'No paper original registered. Where the law keeps a paper original besides its digital copy, register where it is and who holds it with + Physical Record.' },
  'M24-form-physical': {
    kind: 'model_form', model: 'fix.physical.record',
    title: 'Physical Record (Paper Original)', back: 'M24-physical',
    status: { field: 'state', labels: { in_custody: 'In Custody', destroyed: 'Destroyed' } },
    sections: [
      { title: 'Paper Original', note: 'The digital copy is filed; this registers the paper original that must also be kept: where it is, who holds it and its condition (FR-DMS-013). Only a Records Officer registers or moves one.',
        fields: [
          { name: 'document_id', required: true, label: 'Digital Copy (filed document)' },
          { name: 'location', required: true, label: 'Location (branch store, cabinet, offsite archive)' },
          { name: 'box_ref', label: 'Box / File Reference' },
          { name: 'custodian_id', required: true, label: 'Custodian' },
          { name: 'received_on', required: true, label: 'Received On' },
          { name: 'condition', required: true, label: 'Condition' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { title: 'Destruction', note: 'When the retention of the digital copy has run (and it is not on hold) the custodian is reminded. Upload the shredding certificate or photograph here and save, then Record Destruction on the register.',
        fields: [
          { name: 'destruction_due_on', label: 'Destruction Due', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Destruction Evidence (certificate / photograph)' },
          { name: 'destruction_evidence_id', label: 'Evidence on File', readonly: true },
          { name: 'destroyed_on', label: 'Destroyed On', readonly: true },
          { name: 'destroyed_by_id', label: 'Recorded By', readonly: true }
        ] }
    ]
  },
  'M24-integrity': { kind: 'model_list', model: 'fix.document.integrity.check',
    cols: ['name', 'run_at', 'run_by_id', 'retention_class_id', 'documents_checked', 'divergences_found'],
    empty: 'No sweep has run. + Integrity Sweep re-hashes every stored document against its fingerprint now; a weekly job does the same.' },
  'M24-form-integrity': {
    kind: 'model_form', model: 'fix.document.integrity.check',
    title: 'Integrity Sweep', newLabel: 'Run Integrity Sweep', back: 'M24-integrity',
    sections: [
      { title: 'Sweep', note: 'Saving runs the sweep: every stored document is re-hashed and compared with its SHA-256 fingerprint. A divergence is listed below and noted on the document; escalate it to the CTO (T-13). Records Officer or system administrator.',
        fields: [
          { name: 'retention_class_id', label: 'Only this retention class (empty: all)' },
          { name: 'note', type: 'text', label: 'Why this sweep' },
          { name: 'run_at', label: 'Run At', readonly: true },
          { name: 'run_by_id', label: 'Run By', readonly: true },
          { name: 'documents_checked', label: 'Documents Checked', readonly: true },
          { name: 'divergences_found', label: 'Divergences', readonly: true }
        ] }
    ],
    lines: {
      field: 'line_ids', title: 'Divergences', readonly: true,
      note: 'Stored bytes that no longer match the fingerprint taken when the document was filed.',
      fields: [
        { name: 'document_id', label: 'Document', readonly: true },
        { name: 'expected_hash', label: 'Fingerprint on File', readonly: true },
        { name: 'found_hash', label: 'Hash of Stored Bytes', readonly: true }
      ]
    }
  },

  /* ---- page 3: class taxonomy and the exception queue ---- */
  'M24-classes': { kind: 'model_list', model: 'fix.document.class', stateField: 'state',
    cols: ['code', 'name', 'name_bn', 'document_type', 'isolation_tier', 'retention_class_id', 'signature_assurance_level', 'state', 'activated_by_id'],
    actions: [
      { m: 'action_activate', l: 'Activate (Document Controller, not the author)' },
      { m: 'action_retire', l: 'Retire Class' }
    ],
    empty: 'No document class yet. Classification starts when the first class is activated: from then on every new document is filed under its class, or queued as an exception.' },
  'M24-form-class': {
    kind: 'model_form', model: 'fix.document.class',
    title: 'Document Class', back: 'M24-classes',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Class', note: 'One class per document type (BRU-DMS-01). A document of the type is filed under the class: it takes the retention class, is raised to the confidentiality tier, and must carry the mandatory metadata below or it waits in the exception queue (BRU-DMS-08). Save, then a Document Controller who did not write it activates it; an active class is frozen.',
        fields: [
          { name: 'code', required: true, label: 'Class Code' },
          { name: 'name', required: true, label: 'Class Name' },
          { name: 'name_bn', label: 'Class Name (Bengali)' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'parent_id', label: 'Parent Class' },
          { name: 'retention_class_id', required: true, label: 'Retention Class' },
          { name: 'isolation_tier', required: true, label: 'Minimum Confidentiality Tier' },
          { name: 'template_id', label: 'Generating Template' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { title: 'Mandatory Metadata', note: 'A capture missing any of these is queued for a Records Officer, never filed incomplete (FR-DMS-006).',
        fields: [
          { name: 'need_name_bn', label: 'Bengali name' },
          { name: 'need_link', label: 'Business-object link (the record it belongs to)' },
          { name: 'need_description', label: 'Description' },
          { name: 'need_operating_unit', label: 'Branch / operating unit' }
        ] },
      { title: 'Signature', note: 'The assurance level a signature over this class needs (BRU-DMS-17). Qualified accepts only the provider, never a session click or a scanned wet signature.',
        fields: [
          { name: 'requires_signature', label: 'Requires signature' },
          { name: 'signature_assurance_level', label: 'Assurance Level' },
          { name: 'note', type: 'text', label: 'Scope / Notes' },
          { name: 'activated_by_id', label: 'Activated By', readonly: true },
          { name: 'activated_at', label: 'Activated At', readonly: true }
        ] }
    ]
  },
  'M24-exceptions': { kind: 'model_list', create: false, model: 'fix.document.exception', stateField: 'state',
    cols: ['name', 'document_id', 'source', 'cause', 'received_at', 'assigned_to_id', 'state'],
    actions: [{ m: 'action_resolve', l: 'File It (class and metadata supplied)', asks: [{ label: 'Resolution note', kwarg: 'note' }] }],
    empty: 'The exception queue is empty. A capture that cannot be classified, or lacks its class\'s mandatory metadata, waits here for a Records Officer.' },
  'M24-form-exception': {
    kind: 'model_form', model: 'fix.document.exception', create: false,
    pick: 'An exception is queued by classification, never typed in: open one from Classification Exceptions.',
    title: 'Classification Exception', back: 'M24-exceptions',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    sections: [
      { title: 'Why it was queued', fields: [
          { name: 'name', label: 'Exception', readonly: true },
          { name: 'document_id', label: 'Document', readonly: true },
          { name: 'source', label: 'Source', readonly: true },
          { name: 'cause', label: 'Cause', readonly: true },
          { name: 'received_at', label: 'Received', readonly: true },
          { name: 'assigned_to_id', label: 'Assigned To' }
        ] },
      { title: 'Classify', note: 'Supply the class and the missing metadata (they are written to the document), save, then File It on the queue. Records Officer only.',
        fields: [
          { name: 'doc_class_id', label: 'Document Class' },
          { name: 'doc_name_bn', label: 'Bengali Name' },
          { name: 'doc_description', type: 'text', label: 'Description' },
          { name: 'doc_res_model', label: 'Linked Model (e.g. fix.service.order)' },
          { name: 'doc_res_id', label: 'Linked Record ID' },
          { name: 'doc_operating_unit_id', label: 'Branch' },
          { name: 'resolution_note', type: 'text', label: 'Resolution Note' }
        ] }
    ]
  },

  /* ---- page 4: distribution and acknowledgement ---- */
  'M24-distribution': { kind: 'model_list', model: 'fix.document.distribution', stateField: 'state',
    cols: ['name', 'document_id', 'recipient_count', 'acknowledged_count', 'due_on', 'distributed_by_id', 'state'],
    actions: [{ m: 'action_distribute', l: 'Distribute (author or Document Controller)' }],
    empty: 'Nothing distributed yet. + Distribution sends the published version of a controlled document to named people, who each acknowledge it.' },
  'M24-form-distribution': {
    kind: 'model_form', model: 'fix.document.distribution',
    title: 'Controlled Document Distribution', back: 'M24-distribution',
    status: { field: 'state', labels: { draft: 'Draft', distributed: 'Distributed', closed: 'All Acknowledged' } },
    sections: [
      { title: 'Distribution', note: 'Only the published, current version of a controlled document is distributed (BRU-DMS-11). Save, then Distribute: each recipient gets a to-do and acknowledges with their own login on Acknowledgements (FR-DMS-019).',
        fields: [
          { name: 'document_id', required: true, label: 'Controlled Document (published version)' },
          { name: 'recipient_ids', required: true, label: 'Recipients' },
          { name: 'due_on', label: 'Acknowledge By' },
          { name: 'note', type: 'text', label: 'Why they must read it' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'recipient_count', label: 'Recipients', readonly: true },
          { name: 'acknowledged_count', label: 'Acknowledged', readonly: true }
        ] }
    ]
  },
  'M24-acks': { kind: 'model_list', create: false, model: 'fix.document.acknowledgement', stateField: 'state',
    cols: ['distribution_id', 'document_id', 'user_id', 'state', 'acknowledged_at'],
    actions: [{ m: 'action_acknowledge', l: 'I Have Read It (own login)' }],
    empty: 'No acknowledgement is due.' },

  /* ---- page 5: wet-ink signature ---- */
  'M24-wet': { kind: 'model_list', model: 'fix.esignature.wet.signature',
    cols: ['name', 'envelope_id', 'signer_id', 'signed_on', 'identity_checked', 'witnessed_by_id', 'scan_document_id'],
    empty: 'No wet-ink signature recorded. When a signer without a login signs on paper, a witness records it here with the scan.' },
  'M24-form-wet': {
    kind: 'model_form', model: 'fix.esignature.wet.signature',
    title: 'Wet-Ink Signature', back: 'M24-wet',
    sections: [
      { title: 'Paper Signature', note: 'For a signer without a login who signs on paper (FR-DMS-026). You witness it: you cannot be the signer, the signer must be next in the signing order, and a class that requires a qualified signature refuses it (BRU-DMS-17). Saving files the scan and stamps the signer; the record is never edited afterwards.',
        fields: [
          { name: 'envelope_id', required: true, label: 'Envelope (sent)' },
          { name: 'signer_id', required: true, label: 'Signer' },
          { name: 'signed_on', required: true, label: 'Signed On (ink)' },
          { name: 'identity_checked', required: true, label: 'Identity Checked Against (NID, passport, trade licence)' },
          { name: 'scan_file', type: 'file', required: true, label: 'Scanned Signed Page' },
          { name: 'note', type: 'text', label: 'Note' },
          { name: 'witnessed_by_id', label: 'Witnessed By', readonly: true },
          { name: 'scan_document_id', label: 'Filed Scan', readonly: true }
        ] }
    ]
  },

  /* ---- page 6: scoped holds, disposal batches, violations ---- */
  'M24-hold-orders': { kind: 'model_list', model: 'fix.legal.hold.order', stateField: 'state',
    cols: ['name', 'matter_ref', 'instructed_by', 'instructed_on', 'document_count', 'applied_on', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply Hold (Records Officer)' },
      { m: 'action_release', l: 'Release Matter', asks: [{ label: 'Authority and reason for the release', kwarg: 'reason' }] }
    ],
    empty: 'No hold order. A Legal Hold Order holds every document in a scope at once, and every matching document filed while it is in force.' },
  'M24-form-hold-order': {
    kind: 'model_form', model: 'fix.legal.hold.order',
    title: 'Legal Hold Order', back: 'M24-hold-orders',
    status: { field: 'state', labels: { draft: 'Draft', applied: 'In Force', released: 'Released' } },
    sections: [
      { title: 'Matter', note: 'Evidence when the hold was placed, by whose instruction and over what scope (FR-DMS-037). Records Officer only.',
        fields: [
          { name: 'matter_ref', required: true, label: 'Matter Reference (case, notice, inquiry)' },
          { name: 'instructed_by', required: true, label: 'Instructed By (counsel, regulator, GRC owner)' },
          { name: 'instruction_ref', label: 'Instruction Reference' },
          { name: 'instructed_on', required: true, label: 'Instructed On' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { title: 'Scope', note: 'At least one criterion. Apply Hold freezes every matching document at once (all or nothing), and documents filed later that match are held too, until the matter is released (FR-DMS-036).',
        fields: [
          { name: 'scope_retention_class_id', label: 'Retention Class' },
          { name: 'scope_document_type', label: 'Document Type' },
          { name: 'scope_res_model', label: 'Business Object Model (e.g. fix.service.order)' },
          { name: 'scope_res_id', label: 'Business Object Record ID' },
          { name: 'scope_date_from', label: 'Filed From' },
          { name: 'scope_date_to', label: 'Filed To' },
          { name: 'document_count', label: 'Documents Held', readonly: true },
          { name: 'applied_by_id', label: 'Applied By', readonly: true },
          { name: 'released_by_id', label: 'Released By', readonly: true },
          { name: 'release_reason', label: 'Release Authority', readonly: true }
        ] }
    ]
  },
  'M24-batches': { kind: 'model_list', model: 'fix.disposal.batch', stateField: 'state',
    cols: ['name', 'retention_class_id', 'cutoff_on', 'proposed_count', 'excluded_held_count', 'prepared_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_refresh', l: 'Recompute Eligible Documents' },
      { m: 'action_submit', l: 'Submit for Approval (Records Officer)' },
      { m: 'action_approve', l: 'Approve (Disposal Approver, not the preparer)' },
      { m: 'action_reject', l: 'Reject', asks: [{ label: 'Why is the batch rejected?', kwarg: 'reason' }] },
      { m: 'action_execute', l: 'Execute Disposal' }
    ],
    empty: 'No disposal batch. + Disposal Batch proposes the expired documents of one retention class; documents on hold are excluded and listed.' },
  'M24-form-batch': {
    kind: 'model_form', model: 'fix.disposal.batch',
    title: 'Disposal Batch', back: 'M24-batches',
    status: { field: 'state', labels: { proposed: 'Proposed', under_review: 'Under Review', approved: 'Approved', completed: 'Completed', failed: 'Failed', rejected: 'Rejected' } },
    sections: [
      { title: 'Batch', note: 'A Records Officer prepares it: saving lists every document of the class whose retention expired by the cut-off, and lists separately those excluded because they are on hold. Submit, then a Disposal Approver who did not prepare it approves (SOD-23), and Execute disposes all of them or none (§8.3): each gets its register entry and certificate, and the batch its own certificate.',
        fields: [
          { name: 'retention_class_id', required: true, label: 'Retention Class' },
          { name: 'cutoff_on', required: true, label: 'Retention Expired On or Before' },
          { name: 'method', required: true, label: 'Disposal Method' },
          { name: 'note', type: 'text', label: 'Note' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'proposed_count', label: 'Eligible', readonly: true },
          { name: 'excluded_held_count', label: 'Excluded (on hold)', readonly: true },
          { name: 'document_ids', label: 'Eligible Documents', readonly: true },
          { name: 'excluded_held_ids', label: 'Excluded: on hold', readonly: true },
          { name: 'prepared_by_id', label: 'Prepared By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'certificate_doc_id', label: 'Batch Certificate', readonly: true },
          { name: 'outcome_note', label: 'Outcome', readonly: true }
        ] }
    ]
  },
  'M24-violations': { kind: 'model_list', model: 'fix.retention.violation', stateField: 'state',
    cols: ['name', 'document_id', 'violation_type', 'retention_class_id', 'detected_on', 'raised_by', 'state'],
    actions: [
      { m: 'action_investigate', l: 'Investigate', asks: [{ label: 'What is being looked at?', kwarg: 'note' }] },
      { m: 'action_close', l: 'Close', asks: [{ label: 'Cause and what was done', kwarg: 'note' }] }
    ],
    empty: 'No retention violation. The nightly scan raises one for a document kept long past its date or gone before it; a Records Officer can raise one found in an audit.' },
  'M24-form-violation': {
    kind: 'model_form', model: 'fix.retention.violation',
    title: 'Retention Violation', back: 'M24-violations',
    status: { field: 'state', labels: { open: 'Open', investigating: 'Investigating', closed: 'Closed' } },
    sections: [
      { title: 'Violation', note: 'Both directions are violations (BRU-DMS-19): kept beyond the schedule, or missing before it. Records Officer only; investigate and close it with the cause.',
        fields: [
          { name: 'document_id', required: true, label: 'Document' },
          { name: 'violation_type', required: true, label: 'Type' },
          { name: 'detail', type: 'text', required: true, label: 'What was found' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'detected_on', label: 'Detected On', readonly: true },
          { name: 'raised_by', label: 'Raised By', readonly: true },
          { name: 'investigation_note', label: 'Investigation', readonly: true },
          { name: 'closed_by_id', label: 'Closed By', readonly: true }
        ] }
    ]
  },

  /* ---- page 7: evidence packs and controlled external release ---- */
  'M24-packs': { kind: 'model_list', model: 'fix.evidence.pack', stateField: 'state',
    cols: ['name', 'purpose', 'subject_label', 'completeness_state', 'assembly_seconds', 'sealed_hash', 'verification_result', 'state'],
    actions: [
      { m: 'action_collect', l: 'Collect Documents of the Subject' },
      { m: 'action_assemble', l: 'Assemble & Seal' },
      { m: 'action_verify', l: 'Verify Seal' }
    ],
    empty: 'No evidence pack. + Evidence Pack gathers the documents about one claim, audit, dispute or regulator request, checks them against the required composition and seals them.' },
  'M24-form-pack': {
    kind: 'model_form', model: 'fix.evidence.pack',
    title: 'Evidence Pack', back: 'M24-packs',
    status: { field: 'state', labels: { draft: 'Draft', sealed: 'Sealed' } },
    sections: [
      { title: 'Subject', note: 'Name the subject and, if it is a record, its model and ID so Collect can gather every document linked to it. Add the composition the purpose needs, then Assemble & Seal: a missing item marks the pack INCOMPLETE and names what is missing, never silently partial (FR-DMS-041, AC-11).',
        fields: [
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'subject_label', required: true, label: 'Subject (e.g. Claim WC-0012)' },
          { name: 'subject_model', label: 'Subject Model (e.g. fix.warranty.claim)' },
          { name: 'subject_id', label: 'Subject Record ID' },
          { name: 'document_ids', label: 'Documents' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { title: 'Seal (system)', note: 'SHA-256 over a manifest of every document fingerprint; Verify Seal re-hashes them later.',
        fields: [
          { name: 'completeness_state', label: 'Completeness', readonly: true },
          { name: 'missing_items', label: 'Missing', readonly: true },
          { name: 'sealed_hash', label: 'Sealed Hash', readonly: true },
          { name: 'manifest_doc_id', label: 'Manifest', readonly: true },
          { name: 'assembly_seconds', label: 'Request to Seal (seconds)', readonly: true },
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'verification_result', label: 'Last Verification', readonly: true }
        ] }
    ],
    lines: {
      field: 'requirement_ids',
      title: 'Required Composition',
      note: 'One row per document type the purpose needs (e.g. a warranty claim: service report, custody photograph, invoice).',
      fields: [
        { name: 'document_type', required: true, label: 'Document Type' },
        { name: 'min_count', label: 'At Least' },
        { name: 'note', label: 'Note' }
      ]
    }
  },
  'M24-releases': { kind: 'model_list', model: 'fix.external.release', stateField: 'state',
    cols: ['name', 'partner_id', 'pack_id', 'expires_on', 'requested_by_id', 'approved_by_id', 'access_count', 'state'],
    actions: [
      { m: 'action_request', l: 'Request Approval' },
      { m: 'action_grant', l: 'Approve & Issue Link (not the requester)' },
      { m: 'action_revoke', l: 'Revoke', asks: [{ label: 'Why is the release revoked?', kwarg: 'reason' }] }
    ],
    empty: 'No external release. + Share Token releases a sealed evidence pack or named documents to an auditor, brand partner or counsel: scoped, approved, time-boxed, watermarked and logged.' },
  'M24-form-release': {
    kind: 'model_form', model: 'fix.external.release',
    title: 'Share Token (Controlled External Release)', newLabel: 'New Share Token', back: 'M24-releases',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Awaiting Approval', granted: 'Granted', expired: 'Expired', revoked: 'Revoked' } },
    sections: [
      { title: 'Release', note: 'Scope it to a sealed evidence pack or named documents (no T5 document is released by link). It lasts 30 days at most. Request, then a Records Officer or Document Controller who did not request it approves and the link is issued; every view and download is logged, PDFs and images are stamped with the release, and the link dies at expiry or revocation (FR-DMS-042, BRU-DMS-13).',
        fields: [
          { name: 'partner_id', required: true, label: 'External Party' },
          { name: 'purpose', type: 'text', required: true, label: 'Purpose' },
          { name: 'pack_id', label: 'Evidence Pack (sealed)' },
          { name: 'document_ids', label: 'Documents' },
          { name: 'expires_on', required: true, label: 'Expires On' },
          { name: 'watermark', label: 'Watermark every copy served' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { title: 'Link & Log (system)',
        fields: [
          { name: 'access_url', label: 'Link (send to the external party)', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'granted_at', label: 'Granted At', readonly: true },
          { name: 'access_count', label: 'Accesses Logged', readonly: true },
          { name: 'revoke_reason', label: 'Revoked Because', readonly: true }
        ] }
    ]
  },
  'M24-access-log': { kind: 'model_list', create: false, model: 'fix.document.access.log',
    cols: ['at', 'document_id', 'action', 'release_id', 'external_party_id', 'actor_id', 'ip_or_device'],
    empty: 'No access logged. Releases and every external view or download are written here (T-11).' },

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
  'M24:Workshop Evidence Item': 'fix.workshop.evidence',
  'M24:Physical Record': 'fix.physical.record',
  'M24:Integrity Sweep': 'fix.document.integrity.check',
  'M24:Document Class': 'fix.document.class',
  'M24:Distribution': 'fix.document.distribution',
  'M24:Wet-Ink Signature': 'fix.esignature.wet.signature',
  'M24:Legal Hold Order': 'fix.legal.hold.order',
  'M24:Disposal Batch': 'fix.disposal.batch',
  'M24:Retention Violation': 'fix.retention.violation',
  'M24:Evidence Pack': 'fix.evidence.pack',
  'M24:Share Token': 'fix.external.release'
};

export const FORM_CHIPS = {
  'M24:Upload': 'M24-form-document',
  'M24:Controlled Document': 'M24-form-controlled',
  'M24:Document Template': 'M24-form-template',
  'M24:Signature Envelope': 'M24-form-envelope',
  'M24:Retention Policy': 'M24-form-retention',
  'M24:Place Legal Hold': 'M24-form-hold',
  'M24:Workshop Evidence Item': 'M31-form-evidence',
  'M24:Physical Record': 'M24-form-physical',
  'M24:Integrity Sweep': 'M24-form-integrity',
  'M24:Document Class': 'M24-form-class',
  'M24:Distribution': 'M24-form-distribution',
  'M24:Wet-Ink Signature': 'M24-form-wet',
  'M24:Legal Hold Order': 'M24-form-hold-order',
  'M24:Disposal Batch': 'M24-form-batch',
  'M24:Retention Violation': 'M24-form-violation',
  'M24:Evidence Pack': 'M24-form-pack',
  'M24:Share Token': 'M24-form-release',
  'M24:__by_model__': {
    'fix.document': 'M24-form-document',
    'fix.esignature.envelope': 'M24-form-envelope',
    'fix.document.template': 'M24-form-template',
    'fix.retention.class': 'M24-form-retention',
    'fix.physical.record': 'M24-form-physical',
    'fix.document.integrity.check': 'M24-form-integrity',
    'fix.document.class': 'M24-form-class',
    'fix.document.exception': 'M24-form-exception',
    'fix.document.distribution': 'M24-form-distribution',
    'fix.esignature.wet.signature': 'M24-form-wet',
    'fix.legal.hold.order': 'M24-form-hold-order',
    'fix.disposal.batch': 'M24-form-batch',
    'fix.retention.violation': 'M24-form-violation',
    'fix.evidence.pack': 'M24-form-pack',
    'fix.external.release': 'M24-form-release'
  },
  'M24:__by_screen__': {
    'M24-browser': 'M24-form-document',
    'M24-controlled': 'M24-form-controlled',
    'M24-generation': 'M24-form-template',
    'M24-envelopes': 'M24-form-envelope',
    'M24-retention': 'M24-form-retention',
    'M24-physical': 'M24-form-physical',
    'M24-integrity': 'M24-form-integrity',
    'M24-classes': 'M24-form-class',
    'M24-exceptions': 'M24-form-exception',
    'M24-distribution': 'M24-form-distribution',
    'M24-wet': 'M24-form-wet',
    'M24-hold-orders': 'M24-form-hold-order',
    'M24-batches': 'M24-form-batch',
    'M24-violations': 'M24-form-violation',
    'M24-packs': 'M24-form-pack',
    'M24-releases': 'M24-form-release'
  }
};

export const CREATE = {
  M24: { screen: 'M24-form-document', model: 'fix.document', label: 'Document' }
};
