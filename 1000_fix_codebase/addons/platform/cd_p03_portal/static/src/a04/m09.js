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
      { id: 'M09-validate', en: 'Manufacturer Validation', bn: 'যাচাইকরণ', t: 'r' },
      { id: 'M09-repair-wty', en: 'Repair Warranty & Rework', bn: 'মেরামত ওয়ারেন্টি', t: 'r' },
      { id: 'M09-comeback', en: 'Repair Warranty Comebacks', bn: 'মেরামত ওয়ারেন্টিতে ফেরত', t: 'g' },
      { id: 'M09-reworks', en: 'Open Rework Orders', bn: 'চলমান রিওয়ার্ক', t: 'g' },
      { id: 'M09-transfer', en: 'Transfer & Void Rules', bn: 'হস্তান্তর', t: 'g' },
      { id: 'M09-voids', en: 'Void Conditions', bn: 'বাতিলের শর্ত', t: 'g' }
    ]},
    { en: 'Brand Claims', screens: [
      { id: 'M09-claims', en: 'Brand Claims', bn: 'ব্র্যান্ড দাবি', t: 'g' },
      { id: 'M09-record', en: 'Claim Record', bn: 'দাবি রেকর্ড', t: 'f' },
      { id: 'M09-evidence', en: 'Evidence Assembly', bn: 'প্রমাণ', t: 'g' },
      { id: 'M09-brandrules', en: 'Brand Rules & Formats', bn: 'ব্র্যান্ড নিয়ম', t: 'g' },
      { id: 'M09-remit', en: 'Remittance Matching', bn: 'রেমিট্যান্স মিলকরণ', t: 'g' },
      { id: 'M09-recon', en: 'Brand Reconciliation', bn: 'ব্র্যান্ড মিলকরণ', t: 'r' },
      { id: 'M09-appeals', en: 'Claim Appeals', bn: 'দাবি আপিল', t: 'g' },
      { id: 'M09-inforeq', en: 'Brand Information Requests', bn: 'ব্র্যান্ডের তথ্য অনুরোধ', t: 'g' },
      { id: 'M09-remittances', en: 'Brand Remittances', bn: 'ব্র্যান্ড রেমিট্যান্স', t: 'g' },
      { id: 'M09-brandrecon', en: 'Period Reconciliation Statements', bn: 'সময়কালীন মিলকরণ', t: 'g' },
      { id: 'M09-writeoffs', en: 'Claim Write-offs', bn: 'দাবি অবলোপন', t: 'g' },
      { id: 'M09-defreturns', en: 'Defective Part Returns', bn: 'ত্রুটিপূর্ণ যন্ত্রাংশ ফেরত', t: 'g' }
    ]},
    { en: 'Protection Plans', screens: [
      { id: 'M09-protection', en: 'Extended Protection Cover', bn: 'প্রোটেকশন পরিবার', t: 'g' },
      { id: 'M09-policies', en: 'Policy Lifecycle', bn: 'পলিসি লাইফসাইকেল', t: 'g' },
      { id: 'M09-reserves', en: 'Reserves & Loss Ratio', bn: 'রিজার্ভ ও লস রেশিও', t: 'g' },
      { id: 'M09-products', en: 'Protection Products', bn: 'প্রোটেকশন পণ্য', t: 'g' },
      { id: 'M09-inspections', en: 'Pre-sale Inspections', bn: 'বিক্রয়-পূর্ব পরিদর্শন', t: 'g' },
      { id: 'M09-pclaims', en: 'Protection Claims', bn: 'প্রোটেকশন দাবি', t: 'g' },
      { id: 'M09-preserve', en: 'Protection Reserve Ledger', bn: 'প্রোটেকশন রিজার্ভ খতিয়ান', t: 'g' },
      { id: 'M09-provpolicies', en: 'Provision Policies (IAS 37)', bn: 'প্রভিশন পলিসি', t: 'g' }
    ]},
    { en: 'Recalls & Fraud', screens: [
      { id: 'M09-recalls', en: 'Recalls & Campaigns', bn: 'রিকল', t: 'g' },
      { id: 'M09-fraud', en: 'Fraud Detection', bn: 'প্রতারণা শনাক্তকরণ', t: 'r' },
      { id: 'M09-fraudreviews', en: 'Fraud Reviews', bn: 'প্রতারণা পর্যালোচনা', t: 'g' }
    ]}
  ],
  reports: ['Claim Ageing by Brand', 'Reimbursement Cycle Time', 'Claim Rejection Analysis', 'Evidence Completeness', 'Loss Ratio by Product', 'Recall Coverage Report'],
  forms: ['Brand Claim', 'Protection Policy', 'Claim Appeal', 'Recall Campaign', 'Warranty Register Entry', 'Warranty Transfer', 'Protection Product', 'Claim Evidence Item', 'Provision Policy',
    'Void Condition', 'Pre-sale Inspection', 'Protection Claim', 'Brand Claim Rule', 'Brand Information Request', 'Brand Remittance', 'Brand Reconciliation', 'Claim Write-off', 'Defective Part Return', 'Fraud Review'],
  cross: ['M01 Service Orders', 'M08 Contracts', 'M20 AR', 'M37 Catalogue'],
  /* M09 capture audit (2026-11-13). Five of the twelve pages offered no way
   * to record their data and three captured the wrong record:
   * - Protection Products, Evidence Assembly and Recalls: their lists said
   *   create:false although the models take a person's entry (product rules
   *   by a Warranty Officer, evidence items and recall campaigns by a clerk);
   * - Reconciliation listed IAS 37 provisions (M53's computed reserve) and no
   *   page could record the brand's remittance, so an approved claim could
   *   never become remitted, nor be closed, from the workspace;
   * - Repair Warranty offered "+ New Brand Claim": 1000FiX's own repair
   *   warranty is charged to 1000FiX (BRU-WTY-16), never claimed from a brand.
   *   A comeback is opened on the delivered order (M01 action);
   * - the "Protection Policy" chip opened the provision policy (cost ratio,
   *   lookback): an extended cover sold to a customer is a warranty register
   *   row of type Extended/1000FiX. The provision policy keeps its own chip.
   * Validation, assessment and submission are steps on existing claims (list
   * buttons); entitlement and fraud are computed - nothing is typed in there.
   * `domain` stays the LAST key (the mapping guard parses it there). */
  /* Second pass (2026-11-18). A "+ New" on six pages was not the same as
   * capturing what the spec says each page records. Eight pages still could
   * not record their own record, because the record did not exist:
   * - 1 and 4: a void condition with its evidence (BRU-WTY-17); "Void
   *   Warranty" voided cover on a typed reason;
   * - 5: the sold protection policy, its pre-sale inspection and its
   *   reserve (FR-WTY-015..024); the "Protection Policy" chip opened a
   *   warranty register row;
   * - 6: a customer's protection claim (FR-WTY-027..036); the page listed
   *   brand claims and captured nothing;
   * - 8: each brand's claim rule set (FR-WTY-040); "Brand Rules & Formats"
   *   listed products and the evidence list was fixed in code;
   * - 9: the brand's request for information (FR-WTY-047);
   * - 10: a brand's payment across many claims, the signed period
   *   statement, write-off with SoD and defective-part returns
   *   (FR-WTY-053..057);
   * - 12: the fraud review that clears or confirms a flagged claim
   *   (BRU-WTY-21).
   * Validation (2) and the repair-warranty comeback (3) stay list steps. */
  freg: { src: 108, sub: [
    ['1', 'Warranty Register', 12, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'status', 'verification_state', 'start_date', 'end_date'], screens: ['M09-register', 'M09-transfer', 'M09-voids'], reports: [], forms: ['Warranty Register Entry', 'Warranty Transfer', 'Void Condition'] }],
    ['2', 'Manufacturer Validation', 8, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'verification_state', 'verified_by', 'verified_at'], screens: ['M09-validate', 'M09-register'], reports: [], forms: [], create: false }],
    ['3', 'Repair Warranty', 8, { model: 'fix.service.order', cols: ['name', 'customer_id', 'device_id', 'service_warranty_until', 'is_rework', 'state'], screens: ['M09-comeback', 'M09-reworks', 'M09-repair-wty'], reports: [], forms: [], create: false, domain: [['service_warranty_until', '!=', false]] }],
    ['4', 'Entitlement Evaluation', 9, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'status', 'verification_state', 'start_date', 'end_date'], screens: ['M09-voids', 'M09-protection', 'M09-validate'], reports: [], forms: ['Void Condition'], create: 'M09-form-void' }],
    ['5', 'Protection Products', 13, { model: 'fix.protection.policy', cols: ['name', 'partner_id', 'device_id', 'product_id', 'premium', 'term_start', 'term_end', 'state'], screens: ['M09-policies', 'M09-products', 'M09-inspections', 'M09-preserve', 'M09-protection'], reports: [], forms: ['Protection Policy', 'Pre-sale Inspection', 'Protection Product'], create: 'M09-form-ppolicy' }],
    ['6', 'Claim Assessment', 9, { model: 'fix.protection.claim', cols: ['name', 'policy_id', 'partner_id', 'incident_date', 'cause', 'assessed_value', 'fraud_score', 'state'], screens: ['M09-pclaims', 'M09-claims', 'M09-rpt-ageing'], reports: ['Claim Ageing by Brand'], forms: ['Protection Claim'], create: 'M09-form-pclaim' }],
    ['7', 'Evidence Assembly', 9, { model: 'fix.warranty.evidence', cols: ['claim_id', 'requirement_key', 'file_name', 'sha256_hash'], screens: ['M09-evidence', 'M09-claims', 'M09-rpt-evidence'], reports: ['Evidence Completeness'], forms: ['Claim Evidence Item'], create: 'M09-form-wevidence' }],
    ['8', 'Brand Submission', 10, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'claim_amount'], screens: ['M09-claims', 'M09-brandrules', 'M09-rpt-cycle'], reports: ['Reimbursement Cycle Time'], forms: ['Brand Claim', 'Brand Claim Rule'] }],
    ['9', 'Decisions & Appeals', 9, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'claim_amount'], screens: ['M09-appeals', 'M09-inforeq', 'M09-claims', 'M09-rpt-rejection'], reports: ['Claim Rejection Analysis'], forms: ['Claim Appeal', 'Brand Information Request'], create: 'M09-form-appeal' }],
    ['10', 'Reconciliation', 8, { model: 'fix.warranty.claim', cols: ['claim_no', 'brand_id', 'state', 'approved_amount', 'remittance_amount', 'remittance_mismatch'], screens: ['M09-remittances', 'M09-remit', 'M09-brandrecon', 'M09-writeoffs', 'M09-defreturns', 'M09-recon', 'M09-reserves', 'M09-provpolicies'], reports: [], forms: ['Brand Remittance', 'Brand Reconciliation', 'Claim Write-off', 'Defective Part Return', 'Provision Policy'], create: 'M09-form-remittance', domain: [['state', 'in', ['approved', 'partially_approved', 'remitted', 'closed', 'written_off']]] }],
    ['11', 'Recalls', 7, { model: 'fix.warranty.recall', cols: ['name', 'state', 'brand_id', 'product_ref', 'affected_units', 'covered_units', 'launched_on'], screens: ['M09-recalls', 'M09-rpt-recall'], reports: ['Recall Coverage Report'], forms: ['Recall Campaign'] }],
    ['12', 'Fraud Detection', 6, { model: 'fix.warranty.claim', cols: ['claim_no', 'device_id', 'evidence_complete', 'missing_evidence', 'state'], screens: ['M09-fraud', 'M09-fraudreviews', 'M09-pclaims', 'M09-rpt-loss', 'M09-claims'], reports: ['Loss Ratio by Product'], forms: ['Fraud Review'], create: 'M09-form-fraud' }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  /* Evidence is assembled from the workshop job (Assemble Evidence on Brand
   * Claims); an item the job does not hold (the customer's purchase invoice, a
   * brand form) is added here while the claim is still draft or ready - the
   * model locks the pack once the claim is submitted. */
  'M09-evidence': { kind: 'model_list', model: 'fix.warranty.evidence',
    cols: ['claim_id', 'requirement_key', 'file_name', 'sha256_hash', 'create_date'],
    empty: 'No evidence item yet. Assemble Evidence on Brand Claims pulls the workshop job\'s photos and reports into the claim; + New adds an item the job does not hold, while the claim is draft or ready.' },
  /* FR-WTY-040: each brand's claim rule set as data (the evidence the pack
   * needs, the submission window, defective-part return). It listed the
   * protection products; they have their own list, M09-products. */
  'M09-brandrules': { kind: 'model_list', model: 'fix.brand.claim.rule', stateField: 'state',
    cols: ['name', 'brand_id', 'version', 'valid_from', 'channel', 'submission_window_days', 'requires_defective_return', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Rule Set', states: ['draft'] },
      { m: 'action_retire', l: 'Retire Rule Set', states: ['active'] }
    ],
    empty: 'No brand has a rule set yet: every claim needs all seven evidence items and 72 hours. A Claim Decision Officer writes a brand\'s rules; another one activates them.' },
  /* The protection / warranty product rules (duration, waiting days, claim
   * limit, excess, inspection, eligibility, reserve). A Warranty Officer
   * maintains them. */
  'M09-products': { kind: 'model_list', model: 'fix.warranty.product',
    cols: ['name', 'product_type', 'catalogue_item_id', 'duration_months', 'waiting_days', 'claim_limit', 'reserve_rate', 'inspection_required', 'active'],
    stateField: 'product_type' },
  /* BRU-WTY-17: a void condition, with its evidence, applied by a Warranty
   * Officer who did not declare it. "Void Warranty" took a typed reason. */
  'M09-voids': { kind: 'model_list', model: 'fix.warranty.void', stateField: 'state',
    cols: ['name', 'warranty_id', 'device_id', 'condition', 'evidence_document_id', 'declared_by_id', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply - Void The Warranty', states: ['declared'] },
      { m: 'action_reject', l: 'Reject Condition', ask: 'Why the condition does not void the warranty', kwarg: 'note', states: ['declared'] }
    ],
    empty: 'No void condition declared. Found tampering, liquid or an unauthorised repair? + New with a photograph; a Warranty Officer who did not declare it applies it.' },
  'M09-inspections': { kind: 'model_list', model: 'fix.protection.inspection', create: true,
    cols: ['policy_id', 'device_id', 'condition_grade', 'outcome', 'inspector_id', 'inspected_at'],
    stateField: 'outcome' },
  'M09-preserve': { kind: 'model_list', model: 'fix.protection.reserve', create: false,
    cols: ['policy_id', 'product_id', 'movement_type', 'amount', 'reason', 'claim_id', 'at'],
    stateField: 'movement_type',
    empty: 'No reserve movement yet. Activating a protection policy establishes its reserve; settling a claim, cancellation and expiry release it. The ledger is never typed in.' },
  /* FR-WTY-027..036: a customer's claim on a protection plan. */
  'M09-pclaims': { kind: 'model_list', model: 'fix.protection.claim', stateField: 'state',
    cols: ['name', 'policy_id', 'partner_id', 'incident_date', 'cause', 'assessed_value', 'fraud_score', 'approved_amount', 'excess_state', 'state'],
    actions: [
      { m: 'action_assess', l: 'Confirm Assessment', states: ['draft'] },
      { m: 'action_approve', l: 'Approve Claim', states: ['assessed'] },
      { m: 'action_reject', l: 'Reject Claim', ask: 'Reason, in words the customer will read', kwarg: 'reason', states: ['draft', 'assessed'] },
      { m: 'action_record_excess', l: 'Excess Collected', ask: 'Receipt number of the excess payment', kwarg: 'receipt_ref', states: ['approved'] },
      { m: 'action_waive_excess', l: 'Waive Excess', ask: 'Why the excess is waived', kwarg: 'reason', states: ['approved'] },
      { m: 'action_settle', l: 'Settle (fulfilled)', states: ['approved'] }
    ],
    empty: 'No protection claim yet. + New records the incident, cause and evidence; a claim inside the waiting period is rejected at intake.' },
  'M09-inforeq': { kind: 'model_list', model: 'fix.warranty.claim.info.request', stateField: 'state',
    cols: ['name', 'claim_id', 'brand_id', 'requested_on', 'due_date', 'overdue', 'state'],
    actions: [
      { m: 'action_answer', l: 'Record Answer Sent', ask: 'What was sent to the brand', kwarg: 'response', states: ['open'] }
    ],
    empty: 'No open request from a brand. When a brand asks for more on a submitted claim, + New records what it asked and by when.' },
  /* FR-WTY-053: one bank receipt, split across the claims it pays. */
  'M09-remittances': { kind: 'model_list', model: 'fix.brand.remittance', stateField: 'state',
    cols: ['name', 'brand_id', 'bank_ref', 'received_on', 'total_amount', 'allocated_amount', 'unmatched_amount', 'state'],
    actions: [
      { m: 'action_match', l: 'Match To Claims', states: ['draft'] }
    ],
    empty: 'No brand payment recorded. + New records the bank receipt and the claims it pays; a Claim Decision Officer matches it.' },
  'M09-brandrecon': { kind: 'model_list', model: 'fix.brand.reconciliation', stateField: 'state',
    cols: ['name', 'brand_id', 'date_from', 'date_to', 'claimed', 'approved', 'paid', 'outstanding', 'written_off', 'state'],
    actions: [
      { m: 'action_compute', l: 'Compute Statement', states: ['draft', 'computed'] },
      { m: 'action_sign', l: 'Sign Statement', states: ['computed'] }
    ] },
  'M09-writeoffs': { kind: 'model_list', model: 'fix.claim.writeoff', stateField: 'state',
    cols: ['name', 'claim_id', 'brand_id', 'amount', 'requested_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Write-off', states: ['requested'] },
      { m: 'action_refuse', l: 'Refuse Write-off', ask: 'Why the write-off is refused', kwarg: 'note', states: ['requested'] }
    ],
    empty: 'No write-off requested. A Finance Manager who neither raised the claim nor asked for the write-off decides it (BRU-WTY-07).' },
  'M09-defreturns': { kind: 'model_list', model: 'fix.defective.return', stateField: 'state',
    cols: ['name', 'claim_id', 'brand_id', 'part_description', 'part_serial', 'waybill_ref', 'shipped_on', 'state'],
    actions: [
      { m: 'action_ship', l: 'Mark Shipped', states: ['pending'] },
      { m: 'action_acknowledge', l: 'Brand Acknowledged Receipt', states: ['shipped'] }
    ] },
  'M09-fraudreviews': { kind: 'model_list', model: 'fix.warranty.fraud.review', stateField: 'finding',
    cols: ['name', 'claim_id', 'protection_claim_id', 'finding', 'reviewer_id', 'reviewed_at'],
    empty: 'No fraud review yet. A Claim Decision Officer who did not raise the claim records one; a cleared review lets a high-score claim be settled, a confirmed one blocks it.' },
  'M09-recon': { kind: 'table_report', module: 'M09', report: 'claim_reconciliation', title: 'Claim Reconciliation', period: true },
  /* FR-WTY-053 remittance matching. The brand's money is recorded against
   * the approved claim with the bank reference it arrived under (a Claim
   * Decision Officer); a short payment stays open and flagged. The brand's
   * own advice is noted separately and settles nothing. No page offered
   * either, so an approved claim could never be remitted or closed. */
  'M09-remit': { kind: 'model_list', model: 'fix.warranty.claim', create: false,
    cols: ['claim_no', 'brand_id', 'approved_amount', 'remittance_advice_amount', 'remittance_amount', 'remittance_ref', 'remittance_mismatch', 'state'],
    domain: [['state', 'in', ['approved', 'partially_approved', 'remitted']]],
    stateField: 'state',
    actions: [
      { m: 'action_record_remittance', l: 'Record Bank Receipt', states: ['approved', 'partially_approved'],
        asks: [{ kwarg: 'amount', label: 'Amount received from the brand (BDT)', number: true },
          { kwarg: 'bank_ref', label: 'Bank reference it arrived under' }] },
      { m: 'action_record_remittance_advice', l: 'Note Brand Remittance Advice', states: ['approved', 'partially_approved', 'remitted'],
        asks: [{ kwarg: 'amount', label: 'Amount the brand advises it paid (BDT)', number: true },
          { kwarg: 'bank_ref', label: 'Reference on the brand\'s advice' }] },
      { m: 'action_close', l: 'Close Claim', states: ['remitted'] }
    ],
    empty: 'No claim is waiting for the brand\'s money. A claim the brand approved (fully or in part) appears here; record the bank receipt against it to settle it, then close it.' },
  /* FR-WTY-007/008, BRU-WTY-16: 1000FiX's own repair warranty. A customer
   * back with the same problem inside the warranty window gets a linked
   * rework order (Open Comeback); it is free once a commercial approver
   * confirms it. Charged to 1000FiX, never claimed from a brand. */
  'M09-comeback': { kind: 'so_list', scope: 'rwty',
    actions: [
      { id: 'comeback', m: 'action_reopen_comeback', l: 'Open Comeback (repair warranty)', states: ['delivered', 'closed'],
        asks: [{ kwarg: 'reason', label: 'The problem the customer came back with' }] }
    ] },
  'M09-reworks': { kind: 'so_list', scope: 'rework',
    actions: [
      { id: 'rework', m: 'action_request_rework_approval', l: 'Request Zero-Charge Rework',
        states: ['draft', 'intake', 'diagnostic', 'estimate_pending', 'estimate_sent', 'awaiting_approval', 'approved', 'in_repair', 'qc_pending', 'qc_failed', 'ready'],
        asks: [{ kwarg: 'reason', label: 'Why the rework is free of charge' }] }
    ] },
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
      // BRU-WTY-17: voiding is a void condition with its evidence (M09-voids),
      // not a typed reason on the row.
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  /* Policy Lifecycle (§8.2): the protection policies sold. It listed the
   * IAS 37 provision policies, which moved to M09-provpolicies. */
  'M09-policies': { kind: 'model_list', model: 'fix.protection.policy', stateField: 'state',
    cols: ['name', 'partner_id', 'device_id', 'product_id', 'premium', 'term_start', 'term_end', 'remaining_limit', 'reserve_balance', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Cover', states: ['sold'] },
      { m: 'action_cancel', l: 'Cancel Policy (pro-rata refund)', ask: 'Why the policy is cancelled', kwarg: 'reason', states: ['sold', 'active'] }
    ],
    empty: 'No protection policy sold. + New records the sale; Activate checks eligibility and the pre-sale inspection, then establishes the reserve.' },
  'M09-provpolicies': { kind: 'model_list', model: 'fix.warranty.provision.policy', create: false,
    cols: ['name', 'warranty_days', 'lookback_months', 'cost_ratio', 'date_from', 'date_to', 'active'] },
  'M09-reserves': { kind: 'model_list', model: 'fix.warranty.provision', create: false,
    cols: ['name', 'period', 'revenue_in_warranty', 'rework_rate', 'cost_ratio', 'required_balance', 'movement', 'state'],
    stateField: 'state',
    empty: 'No warranty provision yet. Finance opens a period and presses Compute in M53 (Warranty Provision): it is computed from warranty revenue and the rework rate under the active Provision Policy, never typed in.' },
  /* A recall a brand announces is entered as a planned campaign by a clerk
   * (a bulletin distributed through M61 becomes one on its own). */
  'M09-recalls': { kind: 'model_list', model: 'fix.warranty.recall',
    cols: ["name", "state", "create_date", "brand_id", "product_ref", "affected_units", "covered_units"],
    stateField: 'state',
    // A04 audit M09-10: the recall lifecycle runs through its actions.
    actions: [
      { m: 'action_launch', l: 'Launch Recall', states: ['planned'] },
      { m: 'action_complete', l: 'Complete Recall', states: ['active'] },
      { m: 'action_cancel', l: 'Cancel Recall', states: ['planned', 'active'] }
    ] },
  /* A clerk raises an appeal on a rejected or partly approved claim (the
   * model refuses any other); "+ New" opens the appeal form. */
  'M09-appeals': { kind: 'model_list', model: 'fix.claim.appeal', stateField: 'decision',
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
      // BRU-WTY-17: voiding is a void condition with its evidence (M09-voids),
      // not a typed reason on the row.
      { m: 'action_recall_approval', l: 'Recall Request' }
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

  /* The reserve basis (warranty window, lookback, cost ratio) the provision
   * engine applies - accounting configuration, not a policy sold to a
   * customer. It was titled "Protection Policy". */
  'M09-form-policy': { kind: 'model_form', model: 'fix.warranty.provision.policy',
    title: 'Warranty Provision Policy', back: 'M09-provpolicies',
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
        { name: 'claim_id', label: 'Claim', required: true },
        { name: 'evidence_document_id', label: 'Additional Evidence (FR-WTY-049)' }
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


  /* ===== M09 capture audit, second pass (2026-11-18) ===== */
  'M09-form-void': { kind: 'model_form', model: 'fix.warranty.void',
    title: 'Void Condition', back: 'M09-voids',
    status: { field: 'state' },
    tabs: [
      { id: 'finding', label: '1. Condition Found', bn: '১. প্রাপ্ত শর্ত', icon: '🔍' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত', icon: '⚖️' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'finding', title: 'What voids the warranty', note: 'BRU-WTY-17: the condition is applied only with its evidence, by a Warranty Officer who did not declare it.', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'warranty_id', label: 'Warranty', required: true },
        { name: 'condition', label: 'Void Condition', required: true },
        { name: 'description', label: 'What Was Found', required: true, type: 'text' },
        { name: 'evidence_file', type: 'file', label: 'Upload Photograph / Report' },
        { name: 'evidence_filename', label: 'File Name' },
        { name: 'evidence_document_id', label: 'Evidence Document' }
      ] },
      { tab: 'decision', title: 'Decision', fields: [
        { name: 'state', label: 'State (Apply / Reject)', readonly: true },
        { name: 'declared_by_id', label: 'Declared By', readonly: true },
        { name: 'decided_by_id', label: 'Decided By', readonly: true },
        { name: 'decided_at', label: 'Decided At', readonly: true },
        { name: 'decision_note', label: 'Decision Note', readonly: true, type: 'text' }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-ppolicy': { kind: 'model_form', model: 'fix.protection.policy',
    title: 'Protection Policy', back: 'M09-policies',
    status: { field: 'state' },
    lines: { field: 'reserve_ids', title: 'Reserve Ledger', readonlyGrid: true,
      note: 'Append-only (T-09): established at activation, topped up when a claim is approved, released on settlement, cancellation or expiry.',
      fields: [
        { name: 'movement_type', label: 'Movement' },
        { name: 'amount', label: 'Amount' },
        { name: 'reason', label: 'Reason' },
        { name: 'claim_id', label: 'Claim' },
        { name: 'at', label: 'At' }
      ]
    },
    tabs: [
      { id: 'sale', label: '1. Sale', bn: '১. বিক্রয়', icon: '🧾' },
      { id: 'cover', label: '2. Cover & Limits', bn: '২. কভার ও সীমা', icon: '🛡️' },
      { id: 'lifecycle', label: '3. Lifecycle', bn: '৩. জীবনচক্র', icon: '🔄' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'sale', title: 'The plan sold', note: 'Activate Cover on Policy Lifecycle checks eligibility and the pre-sale inspection, then establishes the reserve.', fields: [
        { name: 'name', label: 'Policy No.', readonly: true },
        { name: 'product_id', label: 'Protection Product', required: true },
        { name: 'partner_id', label: 'Customer', required: true },
        { name: 'device_id', label: 'Device', required: true },
        { name: 'premium', label: 'Premium Paid (BDT)', required: true },
        { name: 'sale_ref', label: 'Sale Document (M36 / M38 / counter receipt)' },
        { name: 'term_start', label: 'Cover Starts', required: true }
      ] },
      { tab: 'cover', title: 'Cover, limits and reserve (from the product)', fields: [
        { name: 'term_end', label: 'Cover Ends', readonly: true },
        { name: 'waiting_until', label: 'Waiting Period Until', readonly: true },
        { name: 'excess', label: 'Customer Excess', readonly: true },
        { name: 'claim_limit', label: 'Aggregate Limit', readonly: true },
        { name: 'claimed_amount', label: 'Settled Claims', readonly: true },
        { name: 'remaining_limit', label: 'Remaining Limit', readonly: true },
        { name: 'reserve_balance', label: 'Reserve Balance', readonly: true },
        { name: 'inspection_required', label: 'Pre-sale Inspection Required', readonly: true }
      ] },
      { tab: 'lifecycle', title: 'Lifecycle', fields: [
        { name: 'state', label: 'State (Activate / Cancel)', readonly: true },
        { name: 'activated_by_id', label: 'Activated By', readonly: true },
        { name: 'activated_at', label: 'Activated At', readonly: true },
        { name: 'cancel_reason', label: 'Cancellation Reason', readonly: true, type: 'text' },
        { name: 'refund_amount', label: 'Refund Due (M20)', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-inspection': { kind: 'model_form', model: 'fix.protection.inspection',
    title: 'Pre-sale Inspection', back: 'M09-inspections',
    tabs: [
      { id: 'general', label: '1. Inspection', bn: '১. পরিদর্শন', icon: '🔍' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'The device as seen before sale', note: 'FR-WTY-017: photographed; a failed inspection declines the policy. Never edited afterwards.', fields: [
        { name: 'policy_id', label: 'Policy (sold, awaiting activation)', required: true },
        { name: 'condition_grade', label: 'Condition Grade', required: true },
        { name: 'outcome', label: 'Outcome', required: true },
        { name: 'note', label: 'Findings', type: 'text' },
        { name: 'photo_file', type: 'file', label: 'Upload Photograph' },
        { name: 'photo_filename', label: 'File Name' },
        { name: 'inspector_id', label: 'Inspected By', readonly: true },
        { name: 'inspected_at', label: 'Inspected At', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-pclaim': { kind: 'model_form', model: 'fix.protection.claim',
    title: 'Protection Claim', back: 'M09-pclaims',
    status: { field: 'state' },
    tabs: [
      { id: 'intake', label: '1. Intake', bn: '১. গ্রহণ', icon: '📥' },
      { id: 'assess', label: '2. Damage Assessment', bn: '২. ক্ষতি মূল্যায়ন', icon: '🔧' },
      { id: 'decision', label: '3. Decision & Excess', bn: '৩. সিদ্ধান্ত ও এক্সেস', icon: '⚖️' },
      { id: 'fulfil', label: '4. Fulfilment', bn: '৪. নিষ্পত্তি', icon: '📦' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'intake', title: 'The incident', note: 'An incident inside the waiting period is rejected at intake (BRU-WTY-12).', fields: [
        { name: 'name', label: 'Claim No.', readonly: true },
        { name: 'policy_id', label: 'Policy', required: true },
        { name: 'channel', label: 'Channel', required: true },
        { name: 'incident_date', label: 'Incident Date', required: true },
        { name: 'cause', label: 'Cause', required: true },
        { name: 'description', label: 'Circumstances', required: true, type: 'text' },
        { name: 'evidence_file', type: 'file', label: 'Upload Evidence' },
        { name: 'evidence_filename', label: 'File Name' },
        { name: 'evidence_document_id', label: 'Evidence Document' }
      ] },
      { tab: 'assess', title: 'Technical assessment', note: 'Fill these in, then Confirm Assessment on Protection Claims: coverage is checked and the claim scored.', fields: [
        { name: 'assessed_value', label: 'Assessed Repair / Replace Value (BDT)' },
        { name: 'remedy', label: 'Repair Or Replace' },
        { name: 'damage_consistent', label: 'Damage Consistent With Declared Cause' },
        { name: 'assessment_note', label: 'Technical Assessment', type: 'text' },
        { name: 'assessed_by_id', label: 'Assessed By', readonly: true },
        { name: 'fraud_score', label: 'Fraud Score', readonly: true },
        { name: 'fraud_signals', label: 'Fraud Signals', readonly: true }
      ] },
      { tab: 'decision', title: 'Decision and excess', fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'approved_amount', label: 'Payable By The Plan', readonly: true },
        { name: 'decision_reason', label: 'Decision Reason', readonly: true, type: 'text' },
        { name: 'decided_by_id', label: 'Decided By', readonly: true },
        { name: 'excess_amount', label: 'Excess', readonly: true },
        { name: 'excess_state', label: 'Excess Status', readonly: true },
        { name: 'excess_ref', label: 'Excess Receipt / Waiver', readonly: true }
      ] },
      { tab: 'fulfil', title: 'How it was fulfilled', note: 'Record the fulfilment, then Settle: the policy limit is consumed and the reserve released.', fields: [
        { name: 'fulfilment_type', label: 'Fulfilment' },
        { name: 'fulfilment_ref', label: 'Fulfilment Reference (order / replacement / M20 payment)' },
        { name: 'settled_at', label: 'Settled At', readonly: true },
        { name: 'settled_by_id', label: 'Settled By', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-rule': { kind: 'model_form', model: 'fix.brand.claim.rule',
    title: 'Brand Claim Rule', back: 'M09-brandrules',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Submission', bn: '১. দাখিল', icon: '📤' },
      { id: 'evidence', label: '2. Evidence Required', bn: '২. প্রয়োজনীয় প্রমাণ', icon: '📸' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'How this brand takes claims', note: 'Written by a Claim Decision Officer, activated by another. An active version is not edited: write the next version.', fields: [
        { name: 'brand_id', label: 'Brand', required: true },
        { name: 'version', label: 'Version', readonly: true },
        { name: 'valid_from', label: 'Valid From', required: true },
        { name: 'channel', label: 'Submission Channel', required: true },
        { name: 'submission_window_days', label: 'Submission Window (days from job completion)', required: true },
        { name: 'resubmission_window_days', label: 'Resubmission Window (days)' },
        { name: 'labour_allowance_minutes', label: 'Standard Labour Allowance (min)' },
        { name: 'code_scheme', label: 'Fault Code Scheme' },
        { name: 'requires_defective_return', label: 'Defective Part Returned Before Recovery' },
        { name: 'requires_certified_technician', label: 'Certified Technician Only' },
        { name: 'note', label: 'Other Rules', type: 'text' },
        { name: 'state', label: 'State (Activate / Retire)', readonly: true }
      ] },
      { tab: 'evidence', title: 'The evidence pack this brand requires', fields: [
        { name: 'req_photo_before', label: 'Before Photograph' },
        { name: 'req_photo_after', label: 'After Photograph' },
        { name: 'req_diagnostic', label: 'Diagnostic Record' },
        { name: 'req_parts_issued', label: 'Parts Issued Evidence' },
        { name: 'req_device_serial', label: 'Device Serial Capture' },
        { name: 'req_technician_cert', label: 'Technician Certification' },
        { name: 'req_purchase_proof', label: 'Purchase Proof' }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-inforeq': { kind: 'model_form', model: 'fix.warranty.claim.info.request',
    title: 'Brand Information Request', back: 'M09-inforeq',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Request', bn: '১. অনুরোধ', icon: '❓' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'What the brand asked for', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'claim_id', label: 'Claim (submitted / in review)', required: true },
        { name: 'requested_on', label: 'Brand Asked On', required: true },
        { name: 'brand_ref', label: "Brand's Reference" },
        { name: 'request_text', label: 'What The Brand Asks For', required: true, type: 'text' },
        { name: 'due_date', label: 'Answer Due By', required: true },
        { name: 'response_document_id', label: 'Document Sent' },
        { name: 'response', label: 'Our Answer (Record Answer Sent)', readonly: true, type: 'text' },
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-remittance': { kind: 'model_form', model: 'fix.brand.remittance',
    title: 'Brand Remittance', back: 'M09-remittances',
    status: { field: 'state' },
    lines: {
      field: 'line_ids',
      title: 'Claims This Payment Settles',
      note: 'One line per claim. Match To Claims posts each line to its claim; what the lines leave unallocated stays visible.',
      fields: [
        { name: 'claim_id', label: 'Claim', required: true },
        { name: 'amount', label: 'Paid On This Claim (BDT)', required: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. Bank Receipt', bn: '১. ব্যাংক প্রাপ্তি', icon: '🏦' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'The money the brand sent', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'brand_id', label: 'Brand', required: true },
        { name: 'bank_ref', label: 'Bank Reference', required: true },
        { name: 'received_on', label: 'Received On', required: true },
        { name: 'total_amount', label: 'Amount Received (BDT)', required: true },
        { name: 'advice_document_id', label: 'Brand Remittance Advice' },
        { name: 'allocated_amount', label: 'Allocated', readonly: true },
        { name: 'unmatched_amount', label: 'Unmatched', readonly: true },
        { name: 'state', label: 'State (Match To Claims)', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-brandrecon': { kind: 'model_form', model: 'fix.brand.reconciliation',
    title: 'Brand Reconciliation', back: 'M09-brandrecon',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Period', bn: '১. সময়কাল', icon: '📅' },
      { id: 'totals', label: '2. Statement', bn: '২. বিবরণী', icon: '📊' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'Brand and period', note: 'Compute Statement totals the period; a Claim Decision Officer who did not prepare it signs it, and it is frozen.', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'brand_id', label: 'Brand', required: true },
        { name: 'date_from', label: 'From', required: true },
        { name: 'date_to', label: 'To', required: true },
        { name: 'note', label: 'Note', type: 'text' }
      ] },
      { tab: 'totals', title: 'Statement', fields: [
        { name: 'claim_count', label: 'Claims', readonly: true },
        { name: 'claimed', label: 'Claimed', readonly: true },
        { name: 'approved', label: 'Approved', readonly: true },
        { name: 'rejected', label: 'Rejected', readonly: true },
        { name: 'paid', label: 'Paid', readonly: true },
        { name: 'outstanding', label: 'Outstanding', readonly: true },
        { name: 'written_off', label: 'Written Off', readonly: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'computed_by_id', label: 'Prepared By', readonly: true },
        { name: 'signed_by_id', label: 'Signed By', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-writeoff': { kind: 'model_form', model: 'fix.claim.writeoff',
    title: 'Claim Write-off', back: 'M09-writeoffs',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Request', bn: '১. অনুরোধ', icon: '✍️' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'The unrecoverable balance', note: 'Decided by a Finance Manager who neither raised the claim nor asked for the write-off (BRU-WTY-07).', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'claim_id', label: 'Claim (approved, not fully paid)', required: true },
        { name: 'outstanding', label: 'Outstanding On The Claim', readonly: true },
        { name: 'amount', label: 'Amount To Write Off (BDT)', required: true },
        { name: 'reason', label: 'Why It Cannot Be Recovered', required: true, type: 'text' },
        { name: 'state', label: 'State (Approve / Refuse)', readonly: true },
        { name: 'requested_by_id', label: 'Requested By', readonly: true },
        { name: 'approved_by_id', label: 'Decided By', readonly: true },
        { name: 'decision_note', label: 'Decision Note', readonly: true, type: 'text' }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-defreturn': { kind: 'model_form', model: 'fix.defective.return',
    title: 'Defective Part Return', back: 'M09-defreturns',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. Part & Dispatch', bn: '১. যন্ত্রাংশ ও প্রেরণ', icon: '📦' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'The part going back to the brand', note: 'Mark Shipped needs the waybill, date and proof (BRU-WTY-19).', fields: [
        { name: 'name', label: 'Reference', readonly: true },
        { name: 'claim_id', label: 'Claim', required: true },
        { name: 'part_description', label: 'Part', required: true },
        { name: 'part_serial', label: 'Part Serial' },
        { name: 'waybill_ref', label: 'Courier / Waybill Reference' },
        { name: 'shipped_on', label: 'Shipped On' },
        { name: 'proof_file', type: 'file', label: 'Upload Proof Of Dispatch' },
        { name: 'proof_filename', label: 'File Name' },
        { name: 'proof_document_id', label: 'Proof Of Dispatch' },
        { name: 'state', label: 'State', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },
  'M09-form-fraud': { kind: 'model_form', model: 'fix.warranty.fraud.review',
    title: 'Fraud Review', back: 'M09-fraudreviews',
    tabs: [
      { id: 'general', label: '1. Investigation', bn: '১. তদন্ত', icon: '🕵️' },
      { id: 'audit', label: '2. System Audit', bn: '২. সিস্টেম অডিট' }
    ],
    sections: [
      { tab: 'general', title: 'One flagged claim', note: 'Either a brand claim or a protection claim. Recorded by a Claim Decision Officer who did not raise it; never edited afterwards.', fields: [
        { name: 'claim_id', label: 'Brand Claim' },
        { name: 'protection_claim_id', label: 'Protection Claim' },
        { name: 'finding', label: 'Finding', required: true },
        { name: 'note', label: 'Investigation Notes', required: true, type: 'text' },
        { name: 'signals', label: 'Signals Reviewed', readonly: true },
        { name: 'reviewer_id', label: 'Reviewed By', readonly: true }
      ] },
      { tab: 'audit', title: 'System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true }
      ] }
    ] },

  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M09-form-warranty': {
    kind: 'model_form',
    model: 'fix.warranty',
    title: 'Warranty Register Entry',
    back: 'M09-register',
    status: { field: 'status' },
    lines: { field: 'void_record_ids', title: 'Void Conditions', readonlyGrid: true,
      note: 'BRU-WTY-17: declared with evidence on Void Conditions; a Warranty Officer who did not declare it applies it.',
      fields: [
        { name: 'name', label: 'Reference' },
        { name: 'condition', label: 'Condition' },
        { name: 'state', label: 'State' },
        { name: 'decided_by_id', label: 'Decided By' }
      ]
    },
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
        { name: 'file_data', type: 'file', label: 'Upload Evidence File' },
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
    title: 'Protection Product', back: 'M09-products',
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
        { name: 'claim_limit', label: 'Aggregate Claim Limit' },
        // M37 capture audit, third pass (FR-CAT-037): the cover itself.
        { name: 'coverage_scope', label: 'What Is Covered', type: 'text' },
        { name: 'exclusions', label: 'What Is Not Covered', type: 'text' }
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
        { name: 'waiting_days', label: 'Waiting Days' },
        { name: 'max_device_age_months', label: 'Max Device Age At Sale (months, 0 = any)' },
        { name: 'inspection_required', label: 'Pre-sale Inspection Required' },
        { name: 'reserve_rate', label: 'Reserve Held (% of premium)' }
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

/* 'Protection Policy' is the plan sold to a customer: since the second pass
 * (2026-11-18) a fix.protection.policy (it opened a warranty register row,
 * and before that the IAS 37 provision policy, which keeps its own chip). */
export const FORM_MODELS = {
  'M09:Brand Claim': 'fix.warranty.claim',
  'M09:Protection Policy': 'fix.protection.policy',
  'M09:Void Condition': 'fix.warranty.void',
  'M09:Pre-sale Inspection': 'fix.protection.inspection',
  'M09:Protection Claim': 'fix.protection.claim',
  'M09:Brand Claim Rule': 'fix.brand.claim.rule',
  'M09:Brand Information Request': 'fix.warranty.claim.info.request',
  'M09:Brand Remittance': 'fix.brand.remittance',
  'M09:Brand Reconciliation': 'fix.brand.reconciliation',
  'M09:Claim Write-off': 'fix.claim.writeoff',
  'M09:Defective Part Return': 'fix.defective.return',
  'M09:Fraud Review': 'fix.warranty.fraud.review',
  'M09:Claim Appeal': 'fix.claim.appeal',
  'M09:Recall Campaign': 'fix.warranty.recall',
  'M09:Warranty Register Entry': 'fix.warranty',
  'M09:Warranty Transfer': 'fix.warranty.transfer',
  'M09:Protection Product': 'fix.warranty.product',
  'M09:Claim Evidence Item': 'fix.warranty.evidence',
  'M09:Provision Policy': 'fix.warranty.provision.policy'
};

export const FORM_CHIPS = {
  'M09:Warranty Register Entry': 'M09-form-warranty',
  'M09:Warranty Transfer': 'M09-form-transfer',
  'M09:Claim Evidence Item': 'M09-form-wevidence',
  'M09:Protection Product': 'M09-form-wproduct',
  'M09:Warranty Reserve': 'M09-form-wprov',
  'M09:Brand Claim': 'M09-record',
  'M09:Protection Policy': 'M09-form-ppolicy',
  'M09:Void Condition': 'M09-form-void',
  'M09:Pre-sale Inspection': 'M09-form-inspection',
  'M09:Protection Claim': 'M09-form-pclaim',
  'M09:Brand Claim Rule': 'M09-form-rule',
  'M09:Brand Information Request': 'M09-form-inforeq',
  'M09:Brand Remittance': 'M09-form-remittance',
  'M09:Brand Reconciliation': 'M09-form-brandrecon',
  'M09:Claim Write-off': 'M09-form-writeoff',
  'M09:Defective Part Return': 'M09-form-defreturn',
  'M09:Fraud Review': 'M09-form-fraud',
  'M09:Provision Policy': 'M09-form-policy',
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
    'fix.warranty.transfer': 'M09-form-transfer',
    'fix.warranty.void': 'M09-form-void',
    'fix.protection.policy': 'M09-form-ppolicy',
    'fix.protection.inspection': 'M09-form-inspection',
    'fix.protection.claim': 'M09-form-pclaim',
    'fix.brand.claim.rule': 'M09-form-rule',
    'fix.warranty.claim.info.request': 'M09-form-inforeq',
    'fix.brand.remittance': 'M09-form-remittance',
    'fix.brand.reconciliation': 'M09-form-brandrecon',
    'fix.claim.writeoff': 'M09-form-writeoff',
    'fix.defective.return': 'M09-form-defreturn',
    'fix.warranty.fraud.review': 'M09-form-fraud'
  },
  'M09:__by_screen__': {
    'M09-register': 'M09-form-warranty',
    'M09-evidence': 'M09-form-wevidence',
    'M09-brandrules': 'M09-form-rule',
    'M09-products': 'M09-form-wproduct',
    'M09-voids': 'M09-form-void',
    'M09-inspections': 'M09-form-inspection',
    'M09-pclaims': 'M09-form-pclaim',
    'M09-inforeq': 'M09-form-inforeq',
    'M09-remittances': 'M09-form-remittance',
    'M09-brandrecon': 'M09-form-brandrecon',
    'M09-writeoffs': 'M09-form-writeoff',
    'M09-defreturns': 'M09-form-defreturn',
    'M09-fraudreviews': 'M09-form-fraud',
    'M09-provpolicies': 'M09-form-policy',
    'M09-protection': 'M09-form-warranty',
    'M09-reserves': 'M09-form-wprov',
    'M09-claims': 'M09-record',
    'M09-remit': 'M09-record',
    'M09-policies': 'M09-form-ppolicy',
    'M09-recalls': 'M09-form-recall',
    'M09-transfer': 'M09-form-transfer',
    'M09-appeals': 'M09-form-appeal'
  }
};

export const CREATE = {
  M09: { screen: 'M09-record', model: 'fix.warranty.claim', label: 'Brand Claim' }
};
