/** @odoo-module **/
/* A04 · Commercial & Revenue — M09 Warranty & Claims (v2 rebuild).
 * Registry-faithful: 4 groups / 14 screens / 6 reports / 4 forms / freg 108.
 * Warranty registrations, claims and evidence are real; transfers, recalls and
 * appeals are new. Cycles are measured from timestamps; the actuarial loss
 * ratio is a declared gap (premium revenue is not linked). */

export const MODULE = {
  area: 'A04', code: 'M09', en: 'Warranty & Claims', title: 'M09 · Warranty & Claims',
  bn: 'ওয়ারেন্টি ও দাবি', icon: '🛡️',
  desc: 'Manufacturer warranty register and validation, brand claims with evidence assembly and reconciliation, protection plans and reserves, recall campaigns and fraud signals.',
  kpis: [
    { l: 'Claims Submitted MTD', m: 'claims_submitted_mtd' },
    { l: 'First-Submission Approval', m: 'first_submission_approval', suffix: '%' },
    { l: 'Reimbursement Days', m: 'reimbursement_days' },
    { l: 'Revenue Leakage', m: 'revenue_leakage', prefix: '৳ ' },
    { l: 'Claims < 72h', m: 'claims_under_72h', suffix: '%' },
    { l: 'Appeals Open', m: 'appeals_open' }
  ],
  groups: [
    { en: 'Warranty Register', screens: [
      { id: 'M09-register', en: 'Warranty Register', bn: 'ওয়ারেন্টি রেজিস্টার', t: 'g' },
      { id: 'M09-validate', en: 'Manufacturer Validation', bn: 'যাচাইকরণ', t: 'g' },
      { id: 'M09-repair-wty', en: 'Repair Warranty & Rework', bn: 'মেরামত ওয়ারেন্টি', t: 'g' },
      { id: 'M09-transfer', en: 'Transfer & Void Rules', bn: 'হস্তান্তর', t: 'g' }
    ]},
    { en: 'Brand Claims', screens: [
      { id: 'M09-claims', en: 'Brand Claims', bn: 'ব্র্যান্ড দাবি', t: 'g' },
      { id: 'M09-record', en: 'Claim Record', bn: 'দাবি রেকর্ড', t: 'f' },
      { id: 'M09-evidence', en: 'Evidence Assembly', bn: 'প্রমাণ', t: 'c' },
      { id: 'M09-brandrules', en: 'Brand Rules & Formats', bn: 'ব্র্যান্ড নিয়ম', t: 'g' },
      { id: 'M09-recon', en: 'Brand Reconciliation', bn: 'ব্র্যান্ড মিলকরণ', t: 'c' },
      { id: 'M09-appeals', en: 'Claim Appeals', bn: 'দাবি আপিল', t: 'g' }
    ]},
    { en: 'Protection Plans', screens: [
      { id: 'M09-protection', en: 'Extended Protection Cover', bn: 'প্রোটেকশন পরিবার', t: 'g' },
      { id: 'M09-policies', en: 'Policy Lifecycle', bn: 'পলিসি লাইফসাইকেল', t: 'g' },
      { id: 'M09-reserves', en: 'Reserves & Loss Ratio', bn: 'রিজার্ভ ও লস রেশিও', t: 'r' }
    ]},
    { en: 'Recalls & Fraud', screens: [
      { id: 'M09-recalls', en: 'Recalls & Campaigns', bn: 'রিকল', t: 'g' },
      { id: 'M09-fraud', en: 'Fraud Detection', bn: 'প্রতারণা শনাক্তকরণ', t: 'g' }
    ]}
  ],
  reports: ['Claim Ageing by Brand', 'Reimbursement Cycle Time', 'Claim Rejection Analysis', 'Evidence Completeness', 'Loss Ratio by Product', 'Recall Coverage Report'],
  forms: ['Brand Claim', 'Protection Policy', 'Claim Appeal', 'Recall Campaign'],
  cross: ['M01 Service Orders', 'M08 Contracts', 'M20 AR', 'M37 Catalogue'],
  freg: { src: 108, sub: [
    ['1', 'Warranty Register', 12, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'status', 'verification_state', 'start_date', 'end_date'], screens: ['M09-register'] }],
    ['2', 'Manufacturer Validation', 8, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'verification_state', 'verified_by', 'verified_at'], screens: ['M09-validate', 'M09-register'] }],
    ['3', 'Repair Warranty', 8, { model: 'fix.warranty.claim', cols: ['claim_no', 'service_order_id', 'state', 'claim_amount', 'remittance_amount'], screens: ['M09-repair-wty', 'M09-claims'] }],
    ['4', 'Entitlement Evaluation', 9, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'status', 'verification_state', 'start_date', 'end_date'], screens: ['M09-protection'] }],
    ['5', 'Protection Products', 13, { model: 'fix.warranty.product', cols: ['name', 'product_type', 'catalogue_item_id', 'duration_months', 'waiting_days', 'claim_limit'], screens: ['M09-brandrules'] }],
    ['6', 'Claim Assessment', 9, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'claim_amount'], screens: ['M09-claims', 'M09-rpt-ageing'] }],
    ['7', 'Evidence Assembly', 9, { model: 'fix.warranty.evidence', cols: ['claim_id', 'requirement_key', 'sha256_hash'], screens: ['M09-evidence', 'M09-rpt-evidence'] }],
    ['8', 'Brand Submission', 10, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'claim_amount'], screens: ['M09-claims', 'M09-rpt-cycle'] }],
    ['9', 'Decisions & Appeals', 9, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'claim_amount'], screens: ['M09-rpt-rejection'] }],
    ['10', 'Reconciliation', 8, { model: 'fix.warranty.provision', cols: ['name', 'state', 'period', 'period_end', 'policy_id', 'revenue_in_warranty'], screens: ['M09-reserves', 'M09-recon'] }],
    ['11', 'Recalls', 7, { model: 'fix.warranty.recall', cols: ['name', 'state', 'brand_id', 'product_ref', 'affected_units', 'covered_units', 'launched_on'], screens: ['M09-recalls', 'M09-rpt-recall'] }],
    ['12', 'Fraud Detection', 6, { model: 'fix.warranty.claim', cols: ['claim_no', 'device_id', 'evidence_complete', 'missing_evidence', 'state'], screens: ['M09-fraud', 'M09-rpt-loss', 'M09-claims'] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M09-evidence': { kind: 'model_list', model: 'fix.warranty.evidence', create: false,
    cols: ['claim_id', 'requirement_key', 'file_name', 'sha256_hash', 'create_date'] },
  'M09-brandrules': { kind: 'model_list', model: 'fix.warranty.product', create: false,
    cols: ['name', 'product_type', 'catalogue_item_id', 'duration_months', 'waiting_days', 'claim_limit', 'active'],
    stateField: 'product_type' },
  'M09-recon': { kind: 'table_report', module: 'M09', report: 'claim_reconciliation', title: 'Claim Reconciliation', period: true },
  'M09-protection': { kind: 'model_list', model: 'fix.warranty', create: true,
    // The extended / 1000FiX-sold cover only. M09-register is the full
    // population; without this domain the two screens were the same list
    // under two names (A04 audit, 2026-11-01).
    domain: [['warranty_type', 'in', ['extended', 'brand_auth']]],
    cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'status', 'verification_state', 'verified_at', 'verification_blocker'],
    stateField: 'verification_state',
    actions: [
      // A02 audit B1: verification is decided from the Warranty Officer's
      // M63 inbox; the screen requests it.
      { m: 'action_request_approval', l: 'Request Verification', ask: 'What proof is attached', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_void', l: 'Void Warranty', ask: 'Reason for voiding', kwarg: 'reason' }
    ] },
  'M09-policies': { kind: 'model_list', model: 'fix.warranty.provision.policy', create: false,
    cols: ['name', 'warranty_days', 'lookback_months', 'cost_ratio', 'date_from', 'date_to', 'active'] },
  'M09-reserves': { kind: 'model_list', model: 'fix.warranty.provision', create: false,
    cols: ['name', 'period', 'revenue_in_warranty', 'rework_rate', 'cost_ratio', 'required_balance', 'movement', 'state'],
    stateField: 'state' },
  'M09-recalls': { kind: 'model_list', model: 'fix.warranty.recall', create: false,
    cols: ["name", "state", "create_date", "brand_id", "product_ref", "affected_units", "covered_units"],
    stateField: 'state',
    // A04 audit M09-10: the recall lifecycle runs through its actions.
    actions: [
      { m: 'action_launch', l: 'Launch Recall', states: ['planned'] },
      { m: 'action_complete', l: 'Complete Recall', states: ['active'] },
      { m: 'action_cancel', l: 'Cancel Recall', states: ['planned', 'active'] }
    ] },
  'M09-appeals': { kind: 'model_list', model: 'fix.claim.appeal', create: false, stateField: 'decision',
    cols: ['name', 'claim_id', 'decision', 'decided_by_id', 'decided_at', 'create_date'],
    // A04 audit M09-8: an appeal is decided by a Claim Decision Officer who
    // neither raised it nor recorded the decision appealed against.
    actions: [
      { m: 'action_uphold', l: 'Uphold (re-submit claim)', ask: 'Why the appeal stands', kwarg: 'note' },
      { m: 'action_reject_appeal', l: 'Reject Appeal', ask: 'Why the appeal is rejected', kwarg: 'note' }
    ] },
  'M09-fraud': { kind: 'table_report', module: 'M09', report: 'warranty_fraud', title: 'Warranty Fraud Analysis', period: true },


  /* Report screens */
  'M09-rpt-ageing': { kind: 'table_report', module: 'M09', report: 'claim_ageing_by_brand', title: 'Claim Ageing by Brand', period: false },
  'M09-rpt-cycle': { kind: 'table_report', module: 'M09', report: 'reimbursement_cycle', title: 'Reimbursement Cycle Time', period: false },
  'M09-rpt-rejection': { kind: 'table_report', module: 'M09', report: 'claim_rejection', title: 'Claim Rejection Analysis', period: false },
  'M09-rpt-evidence': { kind: 'table_report', module: 'M09', report: 'evidence_completeness', title: 'Evidence Completeness', period: false },
  'M09-rpt-loss': { kind: 'table_report', module: 'M09', report: 'loss_ratio', title: 'Loss Ratio by Product', period: false },
  'M09-rpt-recall': { kind: 'table_report', module: 'M09', report: 'recall_coverage', title: 'Recall Coverage Report', period: false },

  'M09-register': { kind: 'model_list', model: 'fix.warranty', stateField: 'status', create: true,
    cols: ['device_id', 'warranty_type', 'start_date', 'end_date', 'deductible', 'status', 'verification_state', 'verification_blocker'],
    actions: [
      // A02 audit B1: verification is decided from the Warranty Officer's
      // M63 inbox; the screen requests it.
      { m: 'action_request_approval', l: 'Request Verification', ask: 'What proof is attached', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_void', l: 'Void Warranty', ask: 'Reason for voiding', kwarg: 'reason' }
    ] },
  'M09-validate': { kind: 'table_report', module: 'M09', report: 'warranty_validation', title: 'Manufacturer Validation', period: false },
  'M09-repair-wty': { kind: 'table_report', module: 'M09', report: 'warranty_repairs', title: 'Repair Warranty & Rework', period: false },
  'M09-transfer': { kind: 'model_list', model: 'fix.warranty.transfer', stateField: 'state',
    cols: ['name', 'warranty_id', 'from_partner_id', 'to_partner_id', 'effective_date', 'state', 'approved_by_id'],
    // A04 audit M09-9: approved by an officer who did not record it, then
    // effected (the device changes owner through M17).
    actions: [
      { m: 'action_approve', l: 'Approve Transfer', states: ['draft'] },
      { m: 'action_effect', l: 'Effect Transfer', states: ['approved'] },
      { m: 'action_void', l: 'Void Transfer', states: ['draft', 'approved'] }
    ] },
  'M09-claims': { kind: 'model_list', model: 'fix.warranty.claim', stateField: 'state',
    cols: ['claim_no', 'brand_id', 'service_order_id', 'claim_amount', 'approved_amount', 'evidence_complete', 'approval_state', 'state'],
    // A04 audit M09-1/-2/-11: the claim moves only through these actions.
    // The OEM decision is KEYED here and recorded by a Claim Decision
    // Officer from the M63 inbox (never the submitter or the keyer).
    actions: [
      { m: 'action_assemble_workshop_evidence_pack', l: 'Assemble Evidence', states: ['draft', 'ready'] },
      { m: 'action_refresh_amount', l: 'Refresh Amount from Estimate', states: ['draft', 'ready'] },
      { m: 'action_confirm_device_recheck', l: 'Confirm Device Re-check', ask: 'What was re-checked (owner, purchase proof, cover)', kwarg: 'note', states: ['draft', 'ready'] },
      { m: 'action_submit', l: 'Submit to Brand', states: ['draft', 'ready'] },
      { m: 'action_mark_in_review', l: 'Brand Acknowledged', states: ['submitted'] },
      { m: 'action_propose_approve', l: 'Key OEM Approval', ask: 'OEM decision reference', kwarg: 'oem_reference', states: ['submitted', 'in_review'] },
      { m: 'action_propose_partial', l: 'Key Partial Approval', ask: 'Amount the OEM approved (BDT)', kwarg: 'approved_amount', states: ['submitted', 'in_review'] },
      { m: 'action_propose_reject', l: 'Key OEM Rejection', ask: 'Reason the OEM gave', kwarg: 'reason', states: ['submitted', 'in_review'] },
      { m: 'action_recall_approval', l: 'Recall Keyed Decision', states: ['submitted', 'in_review'] },
      { m: 'action_close', l: 'Close Claim', states: ['remitted', 'rejected'] }
    ] },
  'M09-record': {

    lines: {

      field: 'evidence_ids',

      title: 'Evidence Pack',

      note: 'A claim cannot be submitted until its evidence is complete; each payload carries a SHA-256 digest.',

      fields: [

        { name: 'requirement_key', label: 'Requirement', required: true },

        { name: 'file_name', label: 'File' },

        { name: 'document_id', label: 'Document' },

        { name: 'sha256_hash', label: 'SHA-256' }

      ]

    },
    kind: 'model_form',
    model: 'fix.warranty.claim',
    title: 'Brand Warranty Claim & Reimbursement',
    back: 'M09-claims',
    status: { field: 'state' },
    tabs: [
      { id: 'header', label: '1. Claim Header', bn: '১. ক্লেইম পরিচিতি', icon: '📋', badge: '7' },
      { id: 'defect', label: '2. Defect & Device Provenance', bn: '২. ডিভাইস ও ত্রুটি', icon: '🔍', badge: '3' },
      { id: 'financial', label: '3. Financial Reimbursement', bn: '৩. আর্থিক ও ক্ষতিপূরণ', icon: '💰', badge: '3' },
      { id: 'evidence', label: '4. Evidence & Cryptographic Hash', bn: '৪. প্রমাণ ও হ্যাশ', icon: '🛡️', badge: '3' },
      { id: 'adjudication', label: '5. Adjudication & Timing', bn: '৫. সিদ্ধান্ত ও এসএলএ', icon: '⚖️', badge: '4' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'header', title: 'Claim Identification & Partner Context',
        note: 'ASP warranty claim submitted to OEM/brand principal under authorized service agreement.',
        fields: [
          { name: 'claim_no', readonly: true, label: 'Claim Number (auto)' },
          { name: 'brand_id', required: true, label: 'Brand Principal' },
          { name: 'service_order_id', required: true, label: 'Originating Service Order (M01)' },
          { name: 'operating_unit_id', required: true, label: 'Service Center / Hub' },
          { name: 'warranty_product_id', label: 'Warranty Plan / SKU' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'state', readonly: true, label: 'Claim Lifecycle Status (set by its actions)' }
        ] },
      { tab: 'defect', title: 'Device Serial/IMEI Provenance & Defect Diagnosis',
        fields: [
          { name: 'device_id', readonly: true, label: 'Covered Device Record' },
          { name: 'job_completed_at', readonly: true, label: 'Workshop Job Completed At' }
        ] },
      { tab: 'financial', title: 'Commercial Reimbursement & Remittance Matching',
        fields: [
          { name: 'claim_amount', readonly: true, label: 'Requested Amount (BDT, the approved estimate)' },
          { name: 'approved_amount', readonly: true, label: 'Approved by the OEM (BDT)' },
          { name: 'remittance_amount', readonly: true, label: 'Remitted, bank-confirmed (BDT)' }
        ] },
      { tab: 'evidence', title: 'Cryptographic Evidence Integrity (SHA-256)',
        note: 'All photographic and diagnostic proof is hashed (SHA-256) upon submission to ensure tamper-proof auditability.',
        fields: [
          { name: 'evidence_complete', readonly: true, label: 'Evidence Pack Complete' },
          { name: 'missing_evidence', readonly: true, label: 'Missing Evidence Requirements' }
        ] },
      { tab: 'adjudication', title: 'Brand Adjudication & Statutory Latencies',
        fields: [
          { name: 'submitted_at', readonly: true, label: 'Submission Timestamp' },
          { name: 'decided_at', readonly: true, label: 'Adjudication Timestamp' },
          { name: 'rejection_reason', readonly: true, label: 'Brand Rejection Reason' },
          { name: 'proposed_decision', readonly: true, label: 'Keyed OEM Decision (awaiting officer)' },
          { name: 'decided_by_id', readonly: true, label: 'Decision Recorded By' },
          { name: 'submission_deadline', readonly: true, label: 'Submission SLA Deadline' }
        ] },
      { tab: 'vault', title: 'Brand Claim Document Vault',
        note: 'Invoices, before/after photographs, component return waybills, and brand acceptance credit notes.',
        fields: [] }
    ]
  },

  'M09-form-policy': { kind: 'model_form', model: 'fix.warranty.provision.policy',
    title: 'Protection Policy', back: 'M09-policies',
    status: { field: 'active' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'flags', label: '5. Status Flags', bn: '৫. অবস্থা নির্দেশক' },
      { id: 'text', label: '6. Notes & Terms', bn: '৬. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Policy Name', required: true },
        { name: 'warranty_days', label: 'Warranty Days', required: true },
        { name: 'lookback_months', label: 'Lookback (months)', required: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'cost_ratio', label: 'Cost Ratio', required: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'date_from', label: 'Effective From', required: true },
        { name: 'date_to', label: 'Effective To' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'note', label: 'Note', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M09-form-appeal': { kind: 'model_form', model: 'fix.claim.appeal',
    title: 'Claim Appeal', back: 'M09-claims',
    status: { field: 'decision' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'text', label: '4. Notes & Terms', bn: '৪. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Appeal Name', required: true },
        { name: 'decision', label: 'Decision (Uphold / Reject Appeal)', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'decided_at', label: 'Decided At', readonly: true },
        { name: 'decided_by_id', label: 'Decided By', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'claim_id', label: 'Claim', required: true }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'reason', label: 'Reason', required: true, type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M09-form-recall': { kind: 'model_form', model: 'fix.warranty.recall',
    title: 'Recall Campaign', back: 'M09-recalls',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Campaign Name', required: true },
        { name: 'product_ref', label: 'Product / Model Reference' },
        { name: 'affected_units', label: 'Affected Units', required: true },
        { name: 'covered_units', label: 'Covered Units' },
        { name: 'state', label: 'State (Launch / Complete / Cancel)', readonly: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'launched_on', label: 'Launched On', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'brand_id', label: 'Brand' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M09-form-transfer': { kind: 'model_form', model: 'fix.warranty.transfer',
    title: 'Warranty Transfer', back: 'M09-transfer',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Transfer Name', required: true },
        { name: 'state', label: 'State (Approve / Effect / Void)', readonly: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'effective_date', label: 'Effective Date', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'warranty_id', label: 'Warranty', required: true },
        { name: 'from_partner_id', label: 'From Customer (the current owner)', required: true },
        { name: 'to_partner_id', label: 'To Customer', required: true },
        { name: 'evidence_document_id', label: 'Transfer Evidence (sale receipt / hand-over)' },
        { name: 'approved_by_id', label: 'Approved By', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M09-form-warranty': {
    kind: 'model_form',
    model: 'fix.warranty',
    title: 'Warranty Register Entry',
    back: 'M09-register',
    status: { field: 'status' },
    tabs: [
      { id: 'policy_header', label: '1. Warranty Registration', bn: '১. ওয়ারেন্টি নিবন্ধন', icon: '📋', badge: '6' },
      { id: 'terms_coverage', label: '2. Coverage & Validity', bn: '২. কভারেজ ও মেয়াদ', icon: '🛡️', badge: '4' },
      { id: 'governance', label: '3. Status & Audit', bn: '৩. অবস্থা ও অডিট', icon: '✅', badge: '1' }
    ],
    sections: [
      { tab: 'policy_header', title: 'Registration Header', note: 'The warranty register row: device assignment and underwriting corporate entity.',
        fields: [
          { name: 'company_id', required: true, label: 'Operating Entity' },
          { name: 'device_id', required: true, label: 'Device Serial / Provenance' },
          { name: 'warranty_type', required: true, label: 'Warranty Classification' }
        ] },
      { tab: 'terms_coverage', title: 'Coverage Window & Scope', fields: [
          { name: 'start_date', required: true, label: 'Coverage Start Date' },
          { name: 'end_date', required: true, label: 'Coverage End Date' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'coverage_details', type: 'text', label: 'Statutory Coverage Inclusions & Exclusions' }
        ] },
      { tab: 'policy_header', title: 'Proof of Purchase', note: 'Upload the purchase receipt or warranty card, or choose one already filed, then press Request Verification on the register. A Warranty Officer who did not register it verifies it from the approvals inbox; a request with no proof is refused.',
        fields: [
          { name: 'proof_file', type: 'file', label: 'Upload Proof' },
          { name: 'proof_filename', label: 'Proof File Name' },
          { name: 'proof_document_id', label: 'Proof Document' }
        ] },
      { tab: 'governance', title: 'Lifecycle Status', fields: [
          { name: 'status', label: 'Policy Status (set by Verify / Void)', readonly: true }
        ] }
    ]
  },
  'M09-form-wevidence': { kind: 'model_form', model: 'fix.warranty.evidence',
    title: 'Warranty Claim Evidence', back: 'M09-evidence',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'requirement_key', label: 'Requirement Key', required: true },
        { name: 'file_data', label: 'Upload Evidence File' },
        { name: 'file_name', label: 'File Name' },
        { name: 'sha256_hash', label: 'SHA-256 Checksum', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'claim_id', label: 'Claim', required: true },
        { name: 'document_id', label: 'Document' },
        { name: 'attachment_id', label: 'Evidence Attachment' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M09-form-wproduct': { kind: 'model_form', model: 'fix.warranty.product',
    title: 'Warranty Product Rule', back: 'M09-protection',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'flags', label: '6. Status Flags', bn: '৬. অবস্থা নির্দেশক' },
      { id: 'audit', label: '7. System Audit', bn: '৭. সিস্টেম অডিট' },
      { id: 'docs', label: '8. Documents', bn: '৮. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'product_type', label: 'Product Type', required: true },
        { name: 'duration_months', label: 'Duration Months', required: true },
        { name: 'claim_limit', label: 'Aggregate Claim Limit' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'excess_amount', label: 'Customer Excess' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'catalogue_item_id', label: 'Catalogue Item' },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'waiting_days', label: 'Waiting Days' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M09-form-wprov': { kind: 'model_form', model: 'fix.warranty.provision',
    title: 'Warranty Provision (IAS 37)', back: 'M09-reserves',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'text', label: '5. Notes & Terms', bn: '৫. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', readonly: true },
        { name: 'period', label: 'Period (YYYY-MM)', required: true },
        { name: 'lookback_orders', label: 'Invoiced Repairs (history)', readonly: true },
        { name: 'lookback_reworks', label: 'Reworks (history)', readonly: true },
        { name: 'movement', label: 'Movement', readonly: true },
        // A04 integration (2026-11-04): A08 guards the provision state; it moves
        // only through the model's transitions, never from this form.
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'revenue_in_warranty', label: 'Repair Revenue in Warranty', readonly: true },
        { name: 'rework_rate', label: 'Rework Rate', readonly: true },
        { name: 'cost_ratio', label: 'Rework Cost Ratio', readonly: true },
        { name: 'required_balance', label: 'Required Provision', readonly: true },
        { name: 'opening_balance', label: 'Last Posted Provision', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'period_end', label: 'Period End', readonly: true },
        { name: 'computed_at', label: 'Computed On', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'currency_id', label: 'Currency', readonly: true },
        { name: 'policy_id', label: 'Policy', readonly: true },
        { name: 'move_id', label: 'GL Move', readonly: true },
        { name: 'computed_by_id', label: 'Computed By', readonly: true },
        { name: 'posted_by_id', label: 'Posted By', readonly: true }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'note', label: 'Note', readonly: true, type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] }

};

export const REPORT_ROUTES = {
  'M09:Claim Ageing by Brand': 'M09-rpt-ageing',
  'M09:Reimbursement Cycle Time': 'M09-rpt-cycle',
  'M09:Claim Rejection Analysis': 'M09-rpt-rejection',
  'M09:Evidence Completeness': 'M09-rpt-evidence',
  'M09:Loss Ratio by Product': 'M09-rpt-loss',
  'M09:Recall Coverage Report': 'M09-rpt-recall'
};

export const FORM_MODELS = {
  'M09:Brand Claim': 'fix.warranty.claim',
  'M09:Protection Policy': 'fix.warranty.provision.policy',
  'M09:Claim Appeal': 'fix.claim.appeal',
  'M09:Recall Campaign': 'fix.warranty.recall'
};

export const FORM_CHIPS = {
  'M09:Warranty Register Entry': 'M09-form-warranty',
  'M09:Warranty Evidence': 'M09-form-wevidence',
  'M09:Warranty Product': 'M09-form-wproduct',
  'M09:Warranty Reserve': 'M09-form-wprov',
  'M09:Brand Claim': 'M09-record',
  'M09:Protection Policy': 'M09-form-policy',
  'M09:Claim Appeal': 'M09-form-appeal',
  'M09:Recall Campaign': 'M09-form-recall',
  'M09:__by_model__': {
    'fix.warranty': 'M09-form-warranty',
    'fix.warranty.evidence': 'M09-form-wevidence',
    'fix.warranty.product': 'M09-form-wproduct',
    'fix.warranty.provision': 'M09-form-wprov',
    'fix.warranty.claim': 'M09-record',
    'fix.warranty.provision.policy': 'M09-form-policy',
    'fix.claim.appeal': 'M09-form-appeal',
    'fix.warranty.recall': 'M09-form-recall',
    'fix.warranty.transfer': 'M09-form-transfer'
  },
  'M09:__by_screen__': {
    'M09-register': 'M09-form-warranty',
    'M09-evidence': 'M09-form-wevidence',
    'M09-protection': 'M09-form-warranty',
    'M09-reserves': 'M09-form-wprov',
    'M09-claims': 'M09-record',
    'M09-policies': 'M09-form-policy',
    'M09-recalls': 'M09-form-recall',
    'M09-transfer': 'M09-form-transfer',
    'M09-appeals': 'M09-form-appeal'
  }
};

export const CREATE = {
  M09: { screen: 'M09-record', model: 'fix.warranty.claim', label: 'Brand Claim' }
};
