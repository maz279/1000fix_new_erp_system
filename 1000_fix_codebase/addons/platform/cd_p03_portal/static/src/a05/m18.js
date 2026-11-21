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
    { l: 'Diversion Rate', m: 'diversion_rate', suffix: '%' },
    { l: 'Certificates on File', m: 'certificates_on_file_pct', suffix: '%' },
    { l: 'Certified Partners', m: 'partners_certified' },
    { l: 'Recovery Income 12m', m: 'recovery_income_12m', prefix: '৳ ' },
    { l: 'Zero-Target Breaches 90d', m: 'zero_target_breaches_90d' }
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
    'ESG Materiality Report',
    'Zero-Target Controls'
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
    'Recycler Certificate from Batch',
    // 19 Nov 2026 capture pass 2: what the spec records on these pages and
    // the estate had no record for (FR-ESG-005/006/008/013/014/016/019/022/
    // 023/024)
    'Corporate Disposal Contract',
    'Accept a Corporate Asset Exception',
    'Triage Criteria',
    'Route for Parts Harvest',
    'Donation Hand-over',
    'Downstream Vendor Declaration',
    'Material Recovery',
    'Close a Certificate Exception',
    'Collection Point',
    'Emission Factor Set',
    'Regulatory Obligation',
    'Review an Obligation'
  ],
  cross: ['M17 retired assets', 'M14 non-repairable trade-ins', 'M06 customer drop-offs', 'M03 hazardous transit'],
  /* 13 Nov 2026 capture audit: 3 Data Destruction and 9 ESG offered nothing,
   * 5 offered a "+ New" certificate the server refuses (a certificate comes
   * from its processed batch), 10 repeated page 8's return. Now 3 is the
   * destruction gate's queue (start, bind the M06 certificate, release),
   * 5 records the certificate from its batch, 10 holds the DoE registration
   * the returns are filed under; 9 stays computed (BRU-ESG-11: no entry path). */
  /* 19 Nov 2026 capture pass 2, read against the FRs/BRUs/§10.1 entities:
   * 1 had no channel/condition/hazard/photo and no corporate disposal (005);
   * 2 no published criteria, harvest or donation route (006/008/023);
   * 4 no downstream declarations (024); 5 no uncovered-item exception or
   * material recovery (013/014); 6/7 no collection point with ceilings (022,
   * T-06); 9 no versioned factor set (019, T-08) - its figures stay
   * computed; 10 no regulatory register (016, BRU-ESG-16). */
  freg: { src: 82, sub: [
    ['1', 'Intake & Channels', 8, { model: 'fix.ewaste.collection', cols: ['name', 'customer_id', 'channel', 'material_type', 'weight_kg', 'state'], screens: ['M18-intake', 'M18-settlements', 'M18-corporate', 'M18-corporate-lines'], reports: ['Collection Volume Trend'], forms: ['E-Waste Collection Dossier', 'E-Waste Incentive / Recycler Money', 'Corporate Disposal Contract', 'Accept a Corporate Asset Exception'] }],
    ['2', 'Triage & Disposition', 10, { model: 'fix.ewaste.triage', cols: ['name', 'collection_id', 'decision', 'functional_result', 'criteria_id', 'decided_on'], screens: ['M18-triage', 'M18-criteria', 'M18-donations'], reports: ['Disposition Mix'], forms: ['Triage & Sanitization Record', 'Triage Criteria', 'Route for Parts Harvest', 'Donation Hand-over'] }],
    ['3', 'Data Destruction', 7, { model: 'fix.ewaste.collection', cols: ['name', 'customer_id', 'triage_grade', 'wipe_certificate_id', 'state'], screens: ['M18-intake'], reports: ['Disposition Mix'], forms: ['Start Secure Destruction', 'Bind M06 Wipe Certificate', 'Release to Recycler'], create: 'M18-form-destruction', domain: [['wipe_required', '=', true], ['state', 'in', ['triaged', 'destruction']]] }],
    ['4', 'Outbound Recycler', 8, { model: 'fix.ewaste.batch', cols: ['name', 'partner_id', 'material_type', 'weight_kg', 'state'], screens: ['M18-batches', 'M18-partners', 'M18-downstream', 'M18-manifest', 'M18-pic', 'M18-settlements'], reports: ['Material Recovery Yield'], forms: ['Recycler Dispatch Batch', 'Authorized Recycler Partner', 'Downstream Vendor Declaration', 'Basel Prior Informed Consent', 'E-Waste Incentive / Recycler Money'] }],
    ['5', 'Green Certificates', 7, { model: 'fix.ewaste.certificate', cols: ['name', 'certificate_no', 'partner_id', 'weight_kg', 'issued_on'], screens: ['M18-certs', 'M18-exceptions', 'M18-recovery'], reports: ['Material Recovery Yield'], forms: ['Recycler Certificate from Batch', 'Green & Destruction Certificate', 'Close a Certificate Exception', 'Material Recovery'], create: 'M18-form-cert-record' }],
    ['6', 'Public Drives & Bins', 7, { model: 'fix.ewaste.event', cols: ['name', 'venue', 'event_date', 'collected_kg', 'state'], screens: ['M18-drives', 'M18-points'], reports: ['Collection Volume Trend'], forms: ['Collection Drive Event', 'Collection Point'] }],
    ['7', 'Hazardous Fraction', 9, { model: 'fix.ewaste.battery', cols: ['name', 'chemistry', 'hazmat_class', 'collection_point_id', 'weight_kg', 'state'], screens: ['M18-battery', 'M18-points'], reports: ['Material Recovery Yield'], forms: ['Battery & Hazardous Dossier', 'Collection Point'] }],
    ['8', 'EPR Reporting', 8, { model: 'fix.ewaste.return', cols: ['name', 'authority', 'period', 'recovery_rate_pct', 'state'], screens: ['M18-returns'], reports: ['Statutory Compliance Pack'], forms: ['Statutory Environmental Return', 'DoE E-Waste Registration'] }],
    /* the figures stay computed (BRU-ESG-11): what is captured here is the
     * versioned factor set they are computed with (FR-ESG-019 / T-08) */
    ['9', 'ESG & Carbon', 9, { model: 'fix.esg.metric', cols: ['name', 'metric_type', 'period', 'value', 'unit', 'factor_version'], screens: ['M18-esg', 'M18-factors'], reports: ['ESG Materiality Report', 'Impact & Diversion', 'Zero-Target Controls'], forms: ['Emission Factor Set'], create: 'M18-form-factor' }],
    ['10', 'Compliance Pack', 9, { model: 'fix.ewaste.obligation', cols: ['name', 'instrument', 'citation', 'owner_id', 'next_review', 'compliance_status', 'state'], screens: ['M18-obligations', 'M18-registration', 'M18-epr', 'M18-partners', 'M18-pic'], reports: ['Statutory Compliance Pack', 'Impact & Diversion'], forms: ['Regulatory Obligation', 'Review an Obligation', 'DoE E-Waste Registration', 'Authorized Recycler Partner', 'Basel Prior Informed Consent'] }]
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
      { m: 'action_apply_storage_extension', l: 'Record DoE Extension' },
      { m: 'action_route_harvest', l: 'Route for Parts Harvest' }
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
      { m: 'action_revoke', l: 'Revoke' },
      /* A05 ERP XC-10: watermarked NOT ISSUED / REVOKED where applicable */
      { m: 'p03_print_document', print: 'a4', l: 'Print Disposal Certificate' }
    ] },
  'M18-manifest': { kind: 'model_list', model: 'fix.ewaste.manifest', create: false,
    cols: ['name', 'batch_id', 'partner_id', 'licence_no', 'destination_country_id', 'total_weight_kg', 'hazardous', 'issued_on'],
    actions: [{ m: 'p03_print_document', print: 'a4', l: 'Print Form-1 Manifest & Hazmat Declaration' }] },
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
    cols: ['name', 'kind', 'partner_id', 'collection_id', 'batch_id', 'operating_unit_id', 'payment_method', 'amount', 'approval_state', 'state'],
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
      { m: 'action_accept_return', l: 'Accept DoE' },
      { m: 'p03_print_document', print: 'a4', l: 'Print DoE Return' }
    ] },
  'M18-esg': { kind: 'model_list', model: 'fix.esg.metric', create: false,
    cols: ['name', 'metric_type', 'scope', 'period', 'value', 'unit', 'factor_version', 'computed'],
    empty: 'No ESG metric computed yet. Metrics are calculated from the collections and recycler batches of the period (Recompute from Collections); they are not typed in.',
    actions: [{ m: 'action_recompute', l: 'Recompute from Collections' }] },
  'M18-epr': { kind: 'table_report', module: 'M18', report: 'compliance_pack', title: 'EPR Compliance Pack', period: true },

  /* ===== 19 Nov 2026 capture pass 2: the records the spec names on these
   * pages that had no model (each list's steps are its workflow methods) ===== */
  'M18-points': { kind: 'model_list', model: 'fix.ewaste.collection.point', stateField: 'state',
    cols: ['name', 'kind', 'operating_unit_id', 'responsible_id', 'capacity_kg', 'held_kg', 'state'],
    empty: 'No collection point yet. Register each branch counter, public bin, warehouse area and hazardous store with its capacity and ceilings; an HSE officer activates it (FR-ESG-022).',
    actions: [
      { m: 'action_activate', l: 'Activate (HSE)' },
      { m: 'action_reopen', l: 'Reopen to Change Ceilings' },
      { m: 'action_close', l: 'Close Point' }
    ] },
  'M18-corporate': { kind: 'model_list', model: 'fix.ewaste.corporate.disposal', stateField: 'state',
    cols: ['name', 'client_id', 'contract_ref', 'declared_count', 'received_count', 'reconciled_count', 'open_count', 'state'],
    empty: 'No corporate disposal yet. Record the client’s declared asset list; each asset is reconciled to the item received and its certificate before the contract closes (FR-ESG-005, BRU-ESG-14).',
    actions: [
      { m: 'action_confirm', l: 'Start Receiving' },
      { m: 'action_close', l: 'Close (all reconciled)' }
    ] },
  'M18-corporate-lines': { kind: 'model_list', model: 'fix.ewaste.corporate.disposal.line', create: false,
    cols: ['disposal_id', 'asset_ref', 'description', 'material_type', 'collection_id', 'line_state', 'exception_reason'],
    empty: 'No declared corporate asset yet.' },
  'M18-criteria': { kind: 'model_list', model: 'fix.ewaste.triage.criteria', stateField: 'state',
    cols: ['name', 'effective_from', 'donation_max_value', 'evidence_required', 'published_by_id', 'state'],
    empty: 'No triage criteria published. Write the criteria for each route; another compliance officer publishes them and every decision then records the version in force (FR-ESG-006/007).',
    actions: [{ m: 'action_publish', l: 'Publish (second officer)' }] },
  'M18-donations': { kind: 'model_list', model: 'fix.ewaste.donation', stateField: 'state',
    cols: ['name', 'collection_id', 'recipient_id', 'recipient_reg_no', 'approved_by_id', 'handed_over_on', 'state'],
    empty: 'No donation yet. An item triaged for donation is donated to a registered recipient, approved by a compliance officer and handed over under the M06 gate (FR-ESG-023, BRU-ESG-15).',
    actions: [
      { m: 'action_approve', l: 'Approve (second officer)' },
      { m: 'action_hand_over', l: 'Hand Over (M06 gate)' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M18-downstream': { kind: 'model_list', model: 'fix.ewaste.partner.downstream', stateField: 'state',
    cols: ['partner_id', 'name', 'material_class', 'country_id', 'verified_on', 'verification_due', 'state'],
    empty: 'No downstream destination declared. Each recycler declares where each material goes next; a recycler approver verifies it at least yearly, and a batch leaves only with a current one (FR-ESG-024, BRU-ESG-18).',
    actions: [
      { m: 'action_verify', l: 'Verify (approver)' },
      { m: 'action_withdraw', l: 'Withdraw' }
    ] },
  'M18-exceptions': { kind: 'model_list', model: 'fix.ewaste.certificate.exception', stateField: 'state', create: false,
    cols: ['name', 'collection_id', 'batch_id', 'partner_id', 'kind', 'raised_on', 'resolved_certificate_id', 'state'],
    empty: 'No certificate exception. An item missing from a recycler’s certificate opens one here (BRU-ESG-04).' },
  'M18-recovery': { kind: 'model_list', model: 'fix.ewaste.material.recovery', stateField: 'state',
    cols: ['name', 'batch_id', 'partner_id', 'material_class', 'weight_kg', 'agreed_rate', 'income_amount', 'settlement_id', 'state'],
    empty: 'No material recovery recorded. Record what each processed batch yielded by class, weight and agreed rate, then raise it as the batch’s income for the finance approver (FR-ESG-014, BRU-ESG-19).',
    actions: [{ m: 'action_raise_income', l: 'Raise Batch Income' }] },
  'M18-factors': { kind: 'model_list', model: 'fix.esg.factor.set', stateField: 'state',
    cols: ['name', 'co2_avoided_per_kg', 'source', 'activated_by_id', 'activated_on', 'state'],
    empty: 'No emissions factor set yet: figures use the configured provisional factor. Propose a versioned set with its source; another compliance officer activates it (FR-ESG-019, T-08).',
    actions: [{ m: 'action_activate', l: 'Activate (second officer)' }] },
  'M18-obligations': { kind: 'model_list', model: 'fix.ewaste.obligation', stateField: 'state',
    cols: ['name', 'instrument', 'citation', 'owner_id', 'next_review', 'review_overdue', 'compliance_status', 'state'],
    empty: 'No regulatory obligation recorded. List what each instrument requires of the Company, with its owner and evidence; it is reviewed at least quarterly (FR-ESG-016, BRU-ESG-16).',
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_retire', l: 'Retire' }
    ] },

  /* Report chips -> their own computed packs (All 6 active) */
  'M18-rpt-volume': { kind: 'table_report', module: 'M18', report: 'collection_volume', title: 'Collection Volume Trend', period: true },
  'M18-rpt-disposition': { kind: 'table_report', module: 'M18', report: 'disposition_mix', title: 'Disposition Mix', period: true },
  'M18-rpt-recovery': { kind: 'table_report', module: 'M18', report: 'material_recovery', title: 'Material Recovery Yield', period: true },
  'M18-rpt-compliance': { kind: 'table_report', module: 'M18', report: 'compliance_pack', title: 'Statutory Compliance Pack', period: true },
  'M18-rpt-diversion': { kind: 'table_report', module: 'M18', report: 'impact_diversion', title: 'Impact & Diversion', period: true },
  'M18-rpt-esg': { kind: 'table_report', module: 'M18', report: 'esg_report', title: 'ESG Materiality Report', period: true },
  'M18-rpt-zero-target': { kind: 'table_report', module: 'M18', report: 'zero_target_controls', title: 'Zero-Target Controls', period: true },

  /* ============ D365 IN-WORKSPACE FORMS (6-TAB STANDARD) ============ */
  'M18-form-collection': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'E-Waste Collection Dossier',
    back: 'M18-intake',
    status: { field: 'state', labels: { collected: 'Collected', triaged: 'Triaged', destruction: 'Secure Destruction', recycled: 'Ready for Recycler', routed: 'Routed to M14', hazmat: 'Hazardous Stream', disposed: 'Disposed', certified: 'Certified', donated: 'Donated' } },
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
        note: 'FR-ESG-001/003: the channel the item came through, where it was received and, for a corporate decommission, the declared asset it is.',
        fields: [
          { name: 'name', label: 'Collection Record ID', readonly: true },
          { name: 'customer_id', required: true, label: 'Corporate / Retail Source' },
          { name: 'channel', required: true, label: 'Collection Channel' },
          { name: 'collection_point_id', label: 'Collection Point', domain: [['state', '=', 'active']] },
          { name: 'corporate_line_id', label: 'Declared Corporate Asset (corporate decommission)', domain: [['line_state', '=', 'declared'], ['disposal_id.state', '=', 'receiving']] },
          { name: 'operating_unit_id', label: 'Receiving Hub' },
          { name: 'state', label: 'Collection State', readonly: true }
        ] },
      { tab: 'pricing', title: 'Physical Mass Balance Classification',
        fields: [
          { name: 'item_count', label: 'Item Count' },
          { name: 'weight_kg', required: true, label: 'Intake Mass (kg)' },
          { name: 'weight_pending', label: 'Awaiting Weigh-in (hand-off)', readonly: true },
          { name: 'material_type', required: true, label: 'Schedule-1 Category (Phone/Laptop/Battery/Other)' },
          { name: 'condition', label: 'Condition on Receipt' },
          { name: 'triage_grade', label: 'Triage Grade', readonly: true }
        ] },
      { tab: 'pricing', title: 'Hazards Found on Receipt',
        note: 'A hazardous item opens one hazmat record per hazard ticked here (FR-ESG-015).',
        fields: [
          { name: 'has_battery', label: 'Contains Battery' },
          { name: 'has_crt', label: 'Contains CRT Glass' },
          { name: 'has_mercury', label: 'Contains Mercury Lamp' },
          { name: 'has_refrigerant', label: 'Contains Refrigerant' },
          { name: 'has_toner', label: 'Contains Toner / Ink' }
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
          { name: 'photo_attachment_id', label: 'Receipt Photo (on file)', readonly: true },
          { name: 'photo_file', type: 'file', label: 'Upload Receipt Photo' },
          { name: 'photo_filename', label: 'Photo File Name' }
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
      { tab: 'pricing', title: 'Assessment Against the Published Criteria',
        note: 'FR-ESG-006/007: the criteria in force are stamped on the decision. Under published criteria the functional test and a photo are required; only a fully functional device is reused or donated, and a donation is a low-value device.',
        fields: [
          { name: 'criteria_id', label: 'Criteria Applied', readonly: true },
          { name: 'functional_result', label: 'Functional Test' },
          { name: 'cosmetic_result', label: 'Cosmetic Grade' },
          { name: 'market_value_estimate', label: 'Market Value Estimate (BDT)' }
        ] },
      { tab: 'pricing', title: 'Disposition Routing',
        fields: [
          { name: 'decision', required: true, label: 'Disposition (Reuse / Refurbish / Harvest Parts / Recycle / Hazardous / Donate)' }
        ] },
      { tab: 'technical', title: 'Data Bearing Identification',
        fields: [
          { name: 'data_bearing', label: 'Contains Storage / Data Bearing Media' },
          { name: 'wipe_required', label: 'Mandatory Secure Data Wipe' }
        ] },
      { tab: 'lifecycle', title: 'Inspector Evaluation',
        fields: [
          { name: 'supersedes_id', label: 'Supersedes (earlier decision, unit sent back by M14)', readonly: true },
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
          { name: 'evidence_attachment_id', label: 'Assessment Evidence (on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Assessment Photo' },
          { name: 'evidence_filename', label: 'Evidence File Name' }
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
      { tab: 'pricing', title: 'Outbound Weighbridge (before the manifest, T-05)',
        note: 'Weigh the batch out: the net must reconcile to the sum of its items within tolerance before the Form-1 manifest is issued; the recycler’s weight is then reconciled to this net (M18-16).',
        fields: [
          { name: 'outbound_ticket_ref', label: 'Outbound Weighbridge Ticket' },
          { name: 'outbound_gross_kg', label: 'Outbound Gross (kg)' },
          { name: 'outbound_tare_kg', label: 'Outbound Tare (kg)' },
          { name: 'outbound_net_kg', label: 'Outbound Net (kg)', readonly: true }
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
          { name: 'dispatched_on', label: 'Departure Timestamp', readonly: true },
          { name: 'certificate_due_on', label: 'Recycler Certificate Due', readonly: true },
          { name: 'certificate_overdue', label: 'Certificate Overdue', readonly: true }
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
    pick: 'A certificate is drafted when its batch is processed: open it from Green Certificates to enter the recycler’s details.',
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
      { tab: 'pricing', title: 'Items the Recycler Did NOT Certify',
        note: 'FR-ESG-013 / BRU-ESG-04: list any item of the batch missing from the recycler’s certificate. It stays uncertified with an open exception until a supplementary certificate covers it or an investigation closes it. The stated weight is then that of the items it does cover.',
        fields: [
          { name: 'uncovered_collection_ids', label: 'Items Not on the Certificate', domain: [['state', '=', 'recycled']] }
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
          { name: 'chemistry', required: true, label: 'Hazardous Fraction (cells, CRT, mercury lamp, refrigerant, toner)' },
          { name: 'hazard_class', label: 'UN Hazard Class (Class 9 Miscellaneous)' },
          { name: 'hazmat_class', label: 'Storage Ceiling Class', readonly: true },
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
        note: 'At a designated collection point the ceiling is per class (T-06); a point holds only the classes an HSE officer set a ceiling for.',
        fields: [
          { name: 'collection_point_id', label: 'Storage Point (designated)', domain: [['state', '=', 'active']] },
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
          { name: 'valid_to', label: 'License Expiry Date' },
          { name: 'certificate_window_days', label: 'Agreed Certificate Window (days after transfer)' }
        ] },
      { tab: 'lifecycle', title: 'Audit Verification',
        fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'expiry_warned_stage', label: 'Last Expiry Warning (T-days)', readonly: true },
          { name: 'suspended_on', label: 'Suspended On', readonly: true },
          { name: 'suspension_reason', label: 'Suspension Reason', readonly: true }
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
          { name: 'recovery_rate_pct', label: 'Recovery Rate (recovered / treated, %)', readonly: true }
        ] },
      { tab: 'pricing', title: 'Period Mass Balance (kg): opening + in - out = closing',
        note: 'Computed from the item ledger in kg, one cohort (M18-11). Treated = what the recycler processed in the period; recovered = its recovery lines; disposed = the residue.',
        fields: [
          { name: 'opening_kg', label: 'Opening Stock (kg)', readonly: true },
          { name: 'received_kg', label: 'Received (kg)', readonly: true },
          { name: 'out_kg', label: 'Left Custody (kg)', readonly: true },
          { name: 'closing_kg', label: 'Closing Stock (kg)', readonly: true },
          { name: 'prepared_for_reuse_kg', label: 'Left for Reuse / Refurbishment / Donation (kg)', readonly: true },
          { name: 'treated_kg', label: 'Treated by Recycler (kg)', readonly: true },
          { name: 'recovered_kg', label: 'Material Recovered (kg)', readonly: true },
          { name: 'disposed_kg', label: 'Residue to Disposal (kg)', readonly: true }
        ] },
      { tab: 'pricing', title: 'EPR Collection Target (from the DoE registration)',
        fields: [
          { name: 'epr_base_kg', label: 'EPR Obligation Base (kg)' },
          { name: 'epr_target_pct', label: 'EPR Target in Force (%)', readonly: true },
          { name: 'epr_achievement_pct', label: 'EPR Achievement (%)', readonly: true }
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
      /* also a batch with an item an earlier certificate left out: its
       * supplementary certificate (FR-ESG-013) */
      domain: [['state', '=', 'processed'], '|', '|', ['certificate_ids', '=', false], ['certificate_ids.state', '=', 'revoked'], ['exception_ids.state', '=', 'open']],
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

  /* ===== 19 Nov 2026 capture pass 2 forms ===== */
  'M18-form-point': {
    kind: 'model_form',
    model: 'fix.ewaste.collection.point',
    title: 'Collection Point',
    back: 'M18-points',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', closed: 'Closed' } },
    grids: [
      {
        field: 'limit_ids', tab: 'hazmat', title: 'Hazardous Material Ceilings',
        addLabel: '+ Add a class',
        empty: 'No hazardous class designated: this point may hold no batteries, CRTs, lamps, refrigerant or toner.',
        note: 'T-06 / BRU-ESG-07: one ceiling per class. Receipt beyond it is refused. Frozen while the point is active.',
        fields: [
          { name: 'hazard_class', label: 'Class' },
          { name: 'max_kg', label: 'Ceiling (kg)' }
        ]
      }
    ],
    tabs: [
      { id: 'general', label: '1. Location', bn: '১. অবস্থান', icon: '📍', badge: '5' },
      { id: 'capacity', label: '2. Capacity & Storage', bn: '২. ধারণক্ষমতা', icon: '📦', badge: '3' },
      { id: 'hazmat', label: '3. Hazardous Ceilings', bn: '৩. বিপজ্জনক সীমা', icon: '⚠️' },
      { id: 'governance', label: '4. Activation', bn: '৪. সক্রিয়করণ', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Designated Collection Point (FR-ESG-022)',
        fields: [
          { name: 'name', required: true, label: 'Point Name' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'operating_unit_id', label: 'Branch / Unit' },
          { name: 'address', label: 'Address' },
          { name: 'responsible_id', label: 'Responsible Person' }
        ] },
      { tab: 'capacity', title: 'Capacity and Storage Constraints',
        fields: [
          { name: 'capacity_kg', label: 'Capacity (kg)' },
          { name: 'held_kg', label: 'Held Now (kg)', readonly: true },
          { name: 'storage_constraints', label: 'Segregation, Ventilation, Temperature, Suppression' },
          { name: 'active_from', label: 'Active From' },
          { name: 'active_to', label: 'Active To' }
        ] },
      { tab: 'governance', title: 'HSE Activation (four eyes)',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'approved_by_id', label: 'Activated By', readonly: true },
          { name: 'approved_on', label: 'Activated On', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M18-form-corporate': {
    kind: 'model_form',
    model: 'fix.ewaste.corporate.disposal',
    title: 'Corporate Disposal Contract',
    back: 'M18-corporate',
    status: { field: 'state', labels: { draft: 'Draft', receiving: 'Receiving', closed: 'Closed' } },
    grids: [
      {
        field: 'line_ids', tab: 'assets', title: 'Client’s Declared Assets',
        addLabel: '+ Add declared asset',
        empty: 'No asset declared yet. List every asset on the client’s decommission list.',
        note: 'The list freezes when receiving starts. Each received item is booked against its asset on the collection form; an asset that will never arrive is closed only as a documented exception.',
        fields: [
          { name: 'asset_ref', label: 'Asset Tag / Serial' },
          { name: 'description', label: 'Description' },
          { name: 'material_type', label: 'Category' },
          { name: 'exception_reason', label: 'Exception Reason (if never reconciled)' }
        ]
      }
    ],
    tabs: [
      { id: 'general', label: '1. Contract', bn: '১. চুক্তি', icon: '🏢', badge: '4' },
      { id: 'assets', label: '2. Declared Assets', bn: '২. ঘোষিত সম্পদ', icon: '📋' },
      { id: 'recon', label: '3. Reconciliation', bn: '৩. মিলকরণ', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'general', title: 'Contracted Bulk Disposal (FR-ESG-005)',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'client_id', required: true, label: 'Corporate Client' },
          { name: 'contract_ref', label: 'Contract / PO Reference' },
          { name: 'account_manager_id', label: 'Account Manager' }
        ] },
      { tab: 'recon', title: 'Declared vs Received vs Certified (BRU-ESG-14)',
        fields: [
          { name: 'declared_count', label: 'Declared', readonly: true },
          { name: 'received_count', label: 'Received', readonly: true },
          { name: 'reconciled_count', label: 'Reconciled / Exception', readonly: true },
          { name: 'open_count', label: 'Still Open', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M18-form-corp-exception': {
    kind: 'model_form',
    model: 'fix.ewaste.corporate.disposal.line',
    title: 'Accept a Corporate Asset Exception',
    newLabel: 'Accept a Corporate Asset Exception',
    back: 'M18-corporate-lines',
    pickRecord: {
      label: 'Step 1 of 2: choose the declared asset that will not be reconciled',
      note: 'An asset the client declared but that never arrived, or was lost in custody. The contract closes only when every asset is reconciled or accepted as a documented exception (BRU-ESG-14).',
      search: 'Search asset or contract',
      choose: 'Document the exception',
      cols: ['disposal_id', 'asset_ref', 'description', 'line_state'],
      domain: [['line_state', 'in', ['declared', 'received']], ['disposal_id.state', '=', 'receiving']],
      empty: 'No unreconciled asset on a receiving contract.'
    },
    saveAction: {
      method: 'action_accept_exception', label: 'Accept Exception',
      kwargs: { reason: 'exception_reason' },
      done: 'Exception accepted and recorded on the contract'
    },
    tabs: [{ id: 'general', label: '1. Asset & Reason', bn: '১. সম্পদ ও কারণ', icon: '📝', badge: '4' }],
    sections: [
      { tab: 'general', title: 'Declared asset',
        fields: [
          { name: 'disposal_id', label: 'Contract', readonly: true },
          { name: 'asset_ref', label: 'Asset Tag / Serial', readonly: true },
          { name: 'line_state', label: 'Reconciliation', readonly: true },
          { name: 'exception_reason', required: true, label: 'Documented Reason' }
        ] }
    ]
  },

  'M18-form-criteria': {
    kind: 'model_form',
    model: 'fix.ewaste.triage.criteria',
    title: 'Triage Criteria',
    back: 'M18-criteria',
    status: { field: 'state', labels: { draft: 'Draft', active: 'In Force', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Version', bn: '১. সংস্করণ', icon: '📘', badge: '4' },
      { id: 'routes', label: '2. Criteria per Route', bn: '২. প্রতিটি পথের মানদণ্ড', icon: '🔀', badge: '4' },
      { id: 'governance', label: '3. Publication', bn: '৩. প্রকাশ', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Published Triage Criteria (FR-ESG-006)',
        fields: [
          { name: 'name', required: true, label: 'Version (e.g. TRI-2026-1)' },
          { name: 'effective_from', label: 'Effective From' },
          { name: 'donation_max_value', label: 'Donation: Max Market Value (BDT)' },
          { name: 'evidence_required', label: 'Photo Evidence Required (BRU-ESG-09)' }
        ] },
      { tab: 'routes', title: 'When Each Route Applies',
        fields: [
          { name: 'reuse_criteria', label: 'Reuse / Refurbish (M14) when' },
          { name: 'harvest_criteria', label: 'Harvest Parts (M14 / M15) when' },
          { name: 'recycle_criteria', label: 'Recycle when' },
          { name: 'hazardous_criteria', label: 'Hazardous Treatment when' }
        ] },
      { tab: 'governance', title: 'Published by a Second Officer',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'published_by_id', label: 'Published By', readonly: true },
          { name: 'published_on', label: 'Published On', readonly: true }
        ] }
    ]
  },

  'M18-form-harvest': {
    kind: 'model_form',
    model: 'fix.ewaste.collection',
    title: 'Route for Parts Harvest',
    newLabel: 'Route for Parts Harvest',
    back: 'M18-intake',
    pickRecord: {
      label: 'Step 1 of 2: choose the unit triaged for parts harvesting',
      note: 'FR-ESG-008: the unit goes to M14, which harvests its parts into M15 stock. A data-bearing unit goes only with a verified M06 certificate bound to it (BRU-ESG-01).',
      search: 'Search item or customer',
      choose: 'Route it',
      cols: ['name', 'customer_id', 'material_type', 'weight_kg', 'wipe_certificate_id'],
      domain: [['state', '=', 'triaged'], ['triage_grade', '=', 'harvest']],
      empty: 'No unit is triaged for parts harvesting.'
    },
    saveAction: {
      method: 'action_route_harvest', label: 'Route to M14 for Harvesting',
      done: 'Routed: M14 opens the unit for harvesting'
    },
    tabs: [{ id: 'general', label: '1. Unit', bn: '১. ইউনিট', icon: '🔧', badge: '5' }],
    sections: [
      { tab: 'general', title: 'Unit going for harvesting',
        fields: [
          { name: 'name', label: 'Collection Record', readonly: true },
          { name: 'customer_id', label: 'Source', readonly: true },
          { name: 'material_type', label: 'Category', readonly: true },
          { name: 'data_bearing', label: 'Data Bearing', readonly: true },
          { name: 'wipe_certificate_id', label: 'M06 Certificate', readonly: true }
        ] }
    ]
  },

  'M18-form-donation': {
    kind: 'model_form',
    model: 'fix.ewaste.donation',
    title: 'Donation Hand-over',
    back: 'M18-donations',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', handed_over: 'Handed Over', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: '1. Item & Recipient', bn: '১. আইটেম ও গ্রহীতা', icon: '🎁', badge: '4' },
      { id: 'custody', label: '2. Hand-over Evidence', bn: '২. হস্তান্তর প্রমাণ', icon: '✍️', badge: '3' },
      { id: 'governance', label: '3. Approval', bn: '৩. অনুমোদন', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'general', title: 'Donation (FR-ESG-023)',
        note: 'Only an item triaged for donation (fully functional, low value). It leaves under the same M06 gate as any route (BRU-ESG-15).',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'collection_id', required: true, label: 'Item', domain: [['state', '=', 'triaged'], ['triage_grade', '=', 'donate']] },
          { name: 'recipient_id', required: true, label: 'Recipient' },
          { name: 'recipient_reg_no', label: 'Recipient Registration No (NGO Affairs Bureau / DSS)' },
          { name: 'purpose', label: 'Purpose' }
        ] },
      { tab: 'custody', title: 'Signed Acknowledgement (after approval)',
        fields: [
          { name: 'acknowledgement_attachment_id', label: 'Signed Acknowledgement (on file)', readonly: true },
          { name: 'acknowledgement_file', type: 'file', label: 'Upload Signed Acknowledgement' },
          { name: 'acknowledgement_filename', label: 'File Name' }
        ] },
      { tab: 'governance', title: 'Approval and Hand-over',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'handed_over_by_id', label: 'Handed Over By', readonly: true },
          { name: 'handed_over_on', label: 'Handed Over On', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M18-form-downstream': {
    kind: 'model_form',
    model: 'fix.ewaste.partner.downstream',
    title: 'Downstream Vendor Declaration',
    back: 'M18-downstream',
    status: { field: 'state', labels: { declared: 'Declared', verified: 'Verified', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'general', label: '1. Destination', bn: '১. গন্তব্য', icon: '🏭', badge: '6' },
      { id: 'technical', label: '2. Verification', bn: '২. যাচাই', icon: '🔍', badge: '5' }
    ],
    sections: [
      { tab: 'general', title: 'Where this material goes next (FR-ESG-024)',
        fields: [
          { name: 'partner_id', required: true, label: 'Recycler' },
          { name: 'name', required: true, label: 'Downstream Vendor' },
          { name: 'material_class', required: true, label: 'Material' },
          { name: 'process', label: 'Onward Process' },
          { name: 'country_id', required: true, label: 'Country' },
          { name: 'licence_ref', label: 'Vendor Licence / Authorisation' }
        ] },
      { tab: 'technical', title: 'Annual Verification (BRU-ESG-18)',
        note: 'A recycler approver who did not declare it verifies it from evidence, at least once a year. A batch leaves only with a current verified destination for its material.',
        fields: [
          { name: 'evidence_attachment_id', label: 'Verification Evidence (on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Verification Evidence' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'verified_on', label: 'Verified On', readonly: true },
          { name: 'verification_due', label: 'Re-verify By', readonly: true }
        ] }
    ]
  },

  'M18-form-recovery': {
    kind: 'model_form',
    model: 'fix.ewaste.material.recovery',
    title: 'Material Recovery',
    back: 'M18-recovery',
    status: { field: 'state', labels: { draft: 'Draft', raised: 'Income Raised' } },
    tabs: [
      { id: 'general', label: '1. Batch & Material', bn: '১. চালান ও উপাদান', icon: '♻️', badge: '4' },
      { id: 'pricing', label: '2. Rate & Income', bn: '২. হার ও আয়', icon: '৳', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'What the batch yielded (FR-ESG-014)',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'batch_id', required: true, label: 'Processed Batch', domain: [['state', '=', 'processed']] },
          { name: 'material_class', required: true, label: 'Recovered Material' },
          { name: 'weight_kg', required: true, label: 'Recovered (kg)' }
        ] },
      { tab: 'pricing', title: 'Agreed Rate and Income (to the batch, BRU-ESG-19)',
        fields: [
          { name: 'agreed_rate', label: 'Agreed Rate (BDT per kg)' },
          { name: 'income_amount', label: 'Income (BDT)', readonly: true },
          { name: 'settlement_id', label: 'Income Settlement (finance)', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M18-form-exception': {
    kind: 'model_form',
    model: 'fix.ewaste.certificate.exception',
    title: 'Close a Certificate Exception',
    newLabel: 'Close a Certificate Exception',
    back: 'M18-exceptions',
    pickRecord: {
      label: 'Step 1 of 2: choose the open exception',
      note: 'An item no returned certificate covers. Close it on an investigation finding only when no certificate will come; the officer who issued the certificate does not close its exception (BRU-ESG-04).',
      search: 'Search item, batch or recycler',
      choose: 'Record the finding',
      cols: ['name', 'collection_id', 'batch_id', 'partner_id', 'raised_on'],
      domain: [['state', '=', 'open']],
      empty: 'No open certificate exception.'
    },
    saveAction: {
      method: 'action_close', label: 'Close on Finding',
      kwargs: { finding: 'finding' },
      done: 'Exception closed on the recorded finding'
    },
    tabs: [{ id: 'general', label: '1. Exception & Finding', bn: '১. ব্যতিক্রম ও ফলাফল', icon: '🔎', badge: '5' }],
    sections: [
      { tab: 'general', title: 'Uncovered item',
        fields: [
          { name: 'name', label: 'Exception', readonly: true },
          { name: 'collection_id', label: 'Item', readonly: true },
          { name: 'batch_id', label: 'Batch', readonly: true },
          { name: 'certificate_id', label: 'Raised by Certificate', readonly: true },
          { name: 'finding', required: true, label: 'Investigation Finding' }
        ] }
    ]
  },

  'M18-form-factor': {
    kind: 'model_form',
    model: 'fix.esg.factor.set',
    title: 'Emission Factor Set',
    back: 'M18-factors',
    status: { field: 'state', labels: { draft: 'Proposed', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Factor', bn: '১. ফ্যাক্টর', icon: '🌱', badge: '4' },
      { id: 'technical', label: '2. Source Document', bn: '২. উৎস নথি', icon: '📄', badge: '3' },
      { id: 'governance', label: '3. Activation', bn: '৩. সক্রিয়করণ', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'general', title: 'Versioned Factor Set (FR-ESG-019 / T-08)',
        note: 'An input, not a figure: the ESG figures stay computed from transactions (BRU-ESG-11) and carry the version of the set they were computed with.',
        fields: [
          { name: 'name', required: true, label: 'Version (e.g. EPA-WARM-16)' },
          { name: 'co2_avoided_per_kg', required: true, label: 'kg CO2e Avoided per kg Recycled' },
          { name: 'source', label: 'Factor Source' },
          { name: 'method_note', label: 'Method' }
        ] },
      { tab: 'technical', title: 'Source',
        fields: [
          { name: 'evidence_attachment_id', label: 'Source Document (on file)', readonly: true },
          { name: 'evidence_file', type: 'file', label: 'Upload Source Document' },
          { name: 'evidence_filename', label: 'File Name' }
        ] },
      { tab: 'governance', title: 'Activated by a Second Officer',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'activated_by_id', label: 'Activated By', readonly: true },
          { name: 'activated_on', label: 'Activated On', readonly: true }
        ] }
    ]
  },

  'M18-form-obligation': {
    kind: 'model_form',
    model: 'fix.ewaste.obligation',
    title: 'Regulatory Obligation',
    back: 'M18-obligations',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'general', label: '1. Instrument & Duty', bn: '১. আইন ও দায়িত্ব', icon: '⚖️', badge: '5' },
      { id: 'owner', label: '2. Owner & Evidence', bn: '২. দায়িত্বপ্রাপ্ত ও প্রমাণ', icon: '👤', badge: '4' },
      { id: 'review', label: '3. Review Clock', bn: '৩. পর্যালোচনা', icon: '📅', badge: '5' }
    ],
    sections: [
      { tab: 'general', title: 'E-Waste Regulatory Register (FR-ESG-016)',
        fields: [
          { name: 'name', required: true, label: 'Obligation' },
          { name: 'instrument', required: true, label: 'Instrument' },
          { name: 'citation', required: true, label: 'Clause / Section' },
          { name: 'obligation_text', required: true, label: 'What the Company Must Do' },
          { name: 'applies_because', label: 'Applies Because' }
        ] },
      { tab: 'owner', title: 'Owner and Evidence Source',
        fields: [
          { name: 'owner_id', label: 'Owner' },
          { name: 'evidence_source', label: 'Evidence Source' },
          { name: 'frequency', required: true, label: 'Obligation Frequency' },
          { name: 'next_review', label: 'Next Review (set by activation and each review, at most a quarter away)', readonly: true }
        ] },
      { tab: 'review', title: 'Last Review (BRU-ESG-16)',
        fields: [
          { name: 'compliance_status', label: 'Compliance Status', readonly: true },
          { name: 'last_reviewed', label: 'Last Reviewed', readonly: true },
          { name: 'last_reviewed_by_id', label: 'Reviewed By', readonly: true },
          { name: 'last_review_note', label: 'Last Review Note', readonly: true },
          { name: 'state', label: 'Status', readonly: true }
        ] }
    ]
  },

  'M18-form-obligation-review': {
    kind: 'model_form',
    model: 'fix.ewaste.obligation',
    title: 'Review an Obligation',
    newLabel: 'Review an Obligation',
    back: 'M18-obligations',
    pickRecord: {
      label: 'Step 1 of 2: choose the obligation to review',
      note: 'The finding sets its compliance status; the next review is at most a quarter away (BRU-ESG-16).',
      search: 'Search obligation or clause',
      choose: 'Review it',
      cols: ['name', 'instrument', 'citation', 'next_review', 'compliance_status'],
      domain: [['state', '=', 'active']],
      empty: 'No active obligation. Record and activate one first.'
    },
    saveAction: {
      method: 'action_review', label: 'Record Review',
      kwargs: { review_status: 'review_status', review_note: 'review_note' },
      done: 'Review recorded; the next review date is set'
    },
    tabs: [{ id: 'general', label: '1. Review', bn: '১. পর্যালোচনা', icon: '🔍', badge: '5' }],
    sections: [
      { tab: 'general', title: 'Review finding',
        fields: [
          { name: 'name', label: 'Obligation', readonly: true },
          { name: 'citation', label: 'Clause', readonly: true },
          { name: 'compliance_status', label: 'Current Status', readonly: true },
          { name: 'review_status', required: true, label: 'Finding' },
          { name: 'review_note', required: true, label: 'Review Note (what was checked, evidence seen)' }
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
      /* A05 ERP build S3 (I2): the dimensions and payment terms the approval pins */
      { tab: 'pricing', title: 'Where the money posts and how it is paid (pinned by the approval)',
        note: 'The operating unit is the collection’s or batch’s; the branch belongs to it. A bank or wallet payment names the payee’s account. Recovery income is the batch’s recovery lines’ total and cannot be typed (M18-05).',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit (from the collection / batch)' },
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'payment_method', label: 'Payment Method (incentive / recycler fee)' },
          { name: 'partner_bank_id', label: 'Payee Account / Wallet' }
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
  'M18:ESG Materiality Report': 'M18-rpt-esg',
  'M18:Zero-Target Controls': 'M18-rpt-zero-target'
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
  'M18:Recycler Certificate from Batch': 'fix.ewaste.batch',
  'M18:Corporate Disposal Contract': 'fix.ewaste.corporate.disposal',
  'M18:Accept a Corporate Asset Exception': 'fix.ewaste.corporate.disposal.line',
  'M18:Triage Criteria': 'fix.ewaste.triage.criteria',
  'M18:Route for Parts Harvest': 'fix.ewaste.collection',
  'M18:Donation Hand-over': 'fix.ewaste.donation',
  'M18:Downstream Vendor Declaration': 'fix.ewaste.partner.downstream',
  'M18:Material Recovery': 'fix.ewaste.material.recovery',
  'M18:Close a Certificate Exception': 'fix.ewaste.certificate.exception',
  'M18:Collection Point': 'fix.ewaste.collection.point',
  'M18:Emission Factor Set': 'fix.esg.factor.set',
  'M18:Regulatory Obligation': 'fix.ewaste.obligation',
  'M18:Review an Obligation': 'fix.ewaste.obligation'
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
  'M18:Corporate Disposal Contract': 'M18-form-corporate',
  'M18:Accept a Corporate Asset Exception': 'M18-form-corp-exception',
  'M18:Triage Criteria': 'M18-form-criteria',
  'M18:Route for Parts Harvest': 'M18-form-harvest',
  'M18:Donation Hand-over': 'M18-form-donation',
  'M18:Downstream Vendor Declaration': 'M18-form-downstream',
  'M18:Material Recovery': 'M18-form-recovery',
  'M18:Close a Certificate Exception': 'M18-form-exception',
  'M18:Collection Point': 'M18-form-point',
  'M18:Emission Factor Set': 'M18-form-factor',
  'M18:Regulatory Obligation': 'M18-form-obligation',
  'M18:Review an Obligation': 'M18-form-obligation-review',
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
    'fix.ewaste.settlement': 'M18-form-settlement',
    'fix.ewaste.collection.point': 'M18-form-point',
    'fix.ewaste.corporate.disposal': 'M18-form-corporate',
    'fix.ewaste.triage.criteria': 'M18-form-criteria',
    'fix.ewaste.donation': 'M18-form-donation',
    'fix.ewaste.partner.downstream': 'M18-form-downstream',
    'fix.ewaste.material.recovery': 'M18-form-recovery',
    'fix.esg.factor.set': 'M18-form-factor',
    'fix.ewaste.obligation': 'M18-form-obligation'
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
    'M18-settlements': 'M18-form-settlement',
    'M18-points': 'M18-form-point',
    'M18-corporate': 'M18-form-corporate',
    'M18-criteria': 'M18-form-criteria',
    'M18-donations': 'M18-form-donation',
    'M18-downstream': 'M18-form-downstream',
    'M18-recovery': 'M18-form-recovery',
    'M18-factors': 'M18-form-factor',
    'M18-obligations': 'M18-form-obligation'
  }
};

export const CREATE = {
  M18: { screen: 'M18-form-collection', model: 'fix.ewaste.collection', label: 'Collection Intake' }
};
