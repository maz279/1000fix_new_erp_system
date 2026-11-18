/** @odoo-module **/
/* A12 · M65 Multi-Entity & Localisation. 6 groups / 18 screens / 6 reports / 13 forms / freg 48.
   Capture audit 2026-11-18: every sub-module page captures the records it covers
   (pack assignment, residency rule, onboarding, translation review, rendering
   verification built in cd_multi_entity; intercompany through M19's forms). */

export const MODULE = {
  area: 'A12', code: 'M65', en: 'Multi-Entity & Localisation', title: 'M65 · Multi-Entity & Localisation',
  bn: 'মাল্টি-এন্টিটি ও লোকালাইজেশন', icon: '🌐',
  desc: 'Legal entity structure, country packs (divisions, holidays, postcodes), locale packs with number formats and measured coverage, and a jurisdiction register. The jurisdiction register is documentation: no calculation reads it. Storefront checkout is the only reader of the gateway register.',
  kpis: [
    { l: 'Entities', m: 'entities' },
    { l: 'Country Packs', m: 'country_packs' },
    { l: 'Certified Packs', m: 'country_packs_certified' },
    { l: 'Locales Active', m: 'locales_active' },
    { l: 'Jurisdiction Rules', m: 'jurisdiction_rules' },
    { l: 'Live Gateways', m: 'gateways_live' },
    { l: 'Translations In Review', m: 'translations_in_review' },
    { l: 'Onboardings Open', m: 'onboardings_open' }
  ],
  groups: [
    { en: 'Structure', screens: [
      { id: 'M65-entities', en: 'Entities per Country', bn: 'প্রতিষ্ঠান', t: 'g' },
      { id: 'M65-entity-packs', en: 'Entity Pack Assignments', bn: 'প্রতিষ্ঠানের কান্ট্রি প্যাক', t: 'g' },
      { id: 'M65-structure', en: 'Entity Structure', bn: 'গঠন', t: 'r' }
    ]},
    { en: 'Country', screens: [
      { id: 'M65-packs', en: 'Country Pack Authoring', bn: 'কান্ট্রি প্যাক', t: 'g' },
      { id: 'M65-packlines', en: 'Pack Lines', bn: 'প্যাক লাইন', t: 'g' },
      { id: 'M65-packstatus', en: 'Pack Status', bn: 'প্যাক স্ট্যাটাস', t: 'r' },
      { id: 'M65-gateways', en: 'Payment Gateways (Storefront Checkout Only)', bn: 'পেমেন্ট গেটওয়ে', t: 'g' }
    ]},
    { en: 'Localisation', screens: [
      { id: 'M65-locales', en: 'Locale Packs', bn: 'লোকেল', t: 'g' },
      { id: 'M65-readiness', en: 'Locale Readiness', bn: 'প্রস্তুতি', t: 'r' }
    ]},
    { en: 'Jurisdiction & Expansion', screens: [
      { id: 'M65-jurisdictions', en: 'Jurisdiction Rules (Documentation Only)', bn: 'এখতিয়ার', t: 'g' },
      { id: 'M65-residency', en: 'Data Residency Rules', bn: 'ডেটা রেসিডেন্সি নিয়ম', t: 'g' },
      { id: 'M65-onboarding', en: 'Country Onboarding', bn: 'দেশ অনবোর্ডিং', t: 'g' },
      { id: 'M65-assessment', en: 'Expansion Assessment', bn: 'সম্প্রসারণ মূল্যায়ন', t: 'r' }
    ]},
    { en: 'Translation', screens: [
      { id: 'M65-translation-entries', en: 'Translation Review', bn: 'অনুবাদ পর্যালোচনা', t: 'g' },
      { id: 'M65-rendering', en: 'Rendering Verification', bn: 'রেন্ডারিং যাচাই', t: 'g' },
      { id: 'M65-translations', en: 'Translation Infrastructure', bn: 'অনুবাদ পরিকাঠামো', t: 'r' },
      { id: 'M65-bengali', en: 'Bengali Support (bn-BD)', bn: 'বাংলা সহায়তা (bn-BD)', t: 'r' }
    ]},
    { en: 'Intercompany', screens: [
      { id: 'M65-intercompany', en: 'Intercompany Rules', bn: 'আন্তঃকোম্পানি নিয়ম', t: 'g' },
      { id: 'M65-ic-txns', en: 'Intercompany Charges', bn: 'আন্তঃকোম্পানি চার্জ', t: 'g' },
      { id: 'M65-tp-rates', en: 'Transfer-Pricing Rates', bn: 'স্থানান্তর মূল্য হার', t: 'g' }
    ]}
  ],
  reports: ['Entity Structure', 'Country Pack Status', 'Locale Readiness', 'Expansion Assessment',
    'Translation Completeness', 'Bengali Support'],
  forms: ['Legal Entity', 'Entity Pack Assignment', 'Country Pack', 'Pack Line', 'Payment Gateway',
    'Locale Pack', 'Jurisdiction Rule', 'Residency Rule', 'Country Onboarding', 'Translation Review',
    'Rendering Verification', 'Intercompany Rule', 'Intercompany Charge', 'Transfer-Pricing Rate'],
  cross: ['M30 branch registry', 'M51 BD tax rules', 'M55 holidays'],
  /* Capture audit 2026-11-18: page 1 offered no chip and could not assign a
     pack to an entity; page 2 listed pack lines and gateways it could not
     capture; page 4 had no residency rule or onboarding record; page 5
     "Translation" offered + New Locale Pack (page 3's record) and nothing to
     review; page 6 "Audit" listed intercompany rules with no capture at all. */
  freg: { src: 48, sub: [
    ['1', 'Entity Structure', 10, { model: 'fix.entity', cols: ['code', 'legal_name', 'country_id', 'currency_id', 'active'], screens: ['M65-entities', 'M65-entity-packs', 'M65-structure'], reports: ['Entity Structure'], forms: ['Legal Entity', 'Entity Pack Assignment'] }],
    ['2', 'Country Packs', 9, { model: 'fix.country.pack', cols: ['name', 'code', 'kind', 'version', 'loaded_at'], screens: ['M65-packs', 'M65-packlines', 'M65-packstatus', 'M65-gateways'], reports: ['Country Pack Status'], forms: ['Country Pack', 'Pack Line', 'Payment Gateway'] }],
    ['3', 'Locale Packs', 8, { model: 'fix.locale.pack', cols: ['code', 'name', 'number_format', 'date_format', 'coverage_pct'], screens: ['M65-locales', 'M65-readiness'], reports: ['Locale Readiness'], forms: ['Locale Pack'] }],
    ['4', 'Jurisdiction & Expansion', 7, { model: 'fix.jurisdiction.rule', cols: ['jurisdiction', 'rule_area', 'requirement', 'frequency', 'authority'], screens: ['M65-jurisdictions', 'M65-residency', 'M65-onboarding', 'M65-assessment'], reports: ['Expansion Assessment'], forms: ['Jurisdiction Rule', 'Residency Rule', 'Country Onboarding'] }],
    ['5', 'Translation', 8, { model: 'fix.translation.entry', cols: ['name', 'locale_pack_id', 'module_code', 'machine_translated', 'state'], screens: ['M65-translation-entries', 'M65-rendering', 'M65-translations', 'M65-bengali'], reports: ['Translation Completeness', 'Bengali Support'], forms: ['Translation Review', 'Rendering Verification'] }],
    ['6', 'Intercompany & Transfer Pricing', 6, { model: 'fix.intercompany.rule', cols: ['name', 'scope', 'transaction_type', 'transfer_pricing_compliant', 'documentation_ref'], screens: ['M65-intercompany', 'M65-ic-txns', 'M65-tp-rates'], reports: [], forms: ['Intercompany Rule', 'Intercompany Charge', 'Transfer-Pricing Rate'] }]
  ] }
};

export const SCREENS = {
  'M65-entities': { kind: 'model_list', model: 'fix.entity',
    cols: ['code', 'legal_name', 'legal_name_bn', 'active'] },
  'M65-structure': { kind: 'table_report', module: 'M65', report: 'entity_structure', title: 'Entity Structure', period: false },
  'M65-packs': { kind: 'model_list', model: 'fix.country.pack', stateField: 'state',
    cols: ['name', 'code', 'kind', 'version', 'certified_by_id', 'certified_on', 'loaded_at', 'load_summary', 'state'],
    /* A12 P1-4 lifecycle: draft → validated → certified (a second admin, stating
       what they checked) → active → load → retire. Only a CERTIFIED pack
       activates; only an ACTIVE pack loads and counts. */
    actions: [{ m: 'action_load_bangladesh_drafts', l: 'Load Bangladesh Drafts (needs verifying)' },
              { m: 'action_validate', l: 'Validate' },
              { m: 'action_back_to_draft', l: 'Back To Draft' },
              { m: 'action_certify', l: 'Certify (second person)', ask: 'What did you verify this pack against? Name the gazette or circular and its date. You are confirming you checked it yourself.', kwarg: 'note' },
              { m: 'action_activate', l: 'Activate' },
              { m: 'action_load', l: 'Load Pack Data' },
              { m: 'action_retire', l: 'Retire' }] },
  'M65-packlines': { kind: 'model_list', model: 'fix.country.pack.line',
    cols: ['pack_id', 'parent_code', 'code', 'name', 'name_bn', 'date_value'] },
  'M65-packstatus': { kind: 'table_report', module: 'M65', report: 'country_pack_status', title: 'Country Pack Status', period: false },
  'M65-locales': { kind: 'model_list', model: 'fix.locale.pack', stateField: 'state',
    cols: ['code', 'name', 'number_format', 'date_format', 'coverage_pct', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate Locale' }, { m: 'action_retire', l: 'Retire Locale' }] },
  'M65-readiness': { kind: 'table_report', module: 'M65', report: 'locale_readiness', title: 'Locale Readiness', period: false },
  'M65-jurisdictions': { kind: 'model_list', model: 'fix.jurisdiction.rule',
    cols: ['jurisdiction', 'rule_area', 'requirement', 'frequency', 'authority', 'active'] },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M65-form-locale': {
    kind: 'model_form',
    model: 'fix.locale.pack',
    title: 'Locale Pack',
    back: 'M65-locales',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Locale', note: 'A locale code is unique per company. Coverage is measured from the translations loaded in the system, never typed. Activation is coverage-gated (default 100%) and makes the language available; retiring it removes the language if nobody uses it. Translations themselves are loaded by the language-install tool.',
        fields: [
          { name: 'code', required: true, label: 'Locale Code' },
          { name: 'name', required: true, label: 'Locale Name' },
          { name: 'number_format', required: true, label: 'Number Format' },
          { name: 'first_day_of_week', required: true, label: 'First Day of Week' },
          { name: 'date_format', required: true, label: 'Date Format' },
          { name: 'coverage_pct', readonly: true, label: 'Translation Coverage % (measured)' }
        ] }
    ]
  },

  'M65-form-jurisdiction': {
    kind: 'model_form',
    model: 'fix.jurisdiction.rule',
    title: 'Jurisdiction Rule',
    back: 'M65-jurisdictions',
    sections: [
      { title: 'Rule', note: 'DOCUMENTATION ONLY. This register records one requirement per authority: what is required, how often, and the penalty. No calculation reads it: tax, the VAT calendar and payroll have their own rules, so editing this row changes nothing else. A person must verify the content. Changes are tracked.',
        fields: [
          { name: 'jurisdiction', required: true, label: 'Jurisdiction' },
          { name: 'rule_area', required: true, label: 'Rule Area' },
          { name: 'requirement', required: true, label: 'Requirement' },
          { name: 'frequency', required: true, label: 'Frequency' },
          { name: 'authority', label: 'Authority' },
          { name: 'penalty', label: 'Penalty' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M65-form-country': {
    kind: 'model_form',
    model: 'fix.country.pack',
    title: 'Country Pack',
    back: 'M65-packs',
    lines: {
      field: 'line_ids',
      title: 'Lines',
      readonlyGrid: true,
      note: 'Read-only here: add or correct a line on the Pack Lines screen while the pack is a draft.',
      fields: [
        { name: 'code', label: 'Code' },
        { name: 'parent_code', label: 'Parent Code' },
        { name: 'name', label: 'Name (English)' },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'date_value', label: 'Date' }
      ]
    },
    status: { field: 'state', labels: { draft: 'Draft', validated: 'Validated', certified: 'Certified', active: 'Active', retired: 'Retired' } },
    sections: [
      { title: 'Pack', note: 'A pack is reference data, and this system does not vouch for it: a person must verify every line against the official source, and a Platform Admin other than the creator certifies it. Once validated the pack is frozen. Only an active, loaded pack counts: Load copies holidays into national calendars and divisions into the address hierarchy, and postcodes nowhere. Load Bangladesh Drafts on the list screen creates the shipped data as unverified drafts.',
        fields: [
          { name: 'name', required: true, label: 'Pack Name' },
          { name: 'code', required: true, label: 'Pack Code' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'version', required: true, label: 'Version' }
        ] }
    ]
  },

  'M65-form-packline': {
    kind: 'model_form',
    model: 'fix.country.pack.line',
    title: 'Pack Line',
    back: 'M65-packlines',
    sections: [
      { title: 'Line', note: 'A line is one division/district, holiday or postcode inside its pack. parent_code links the hierarchy; a holiday needs its date. Lines can change only while the pack is a draft.',
        fields: [
          { name: 'pack_id', required: true, label: 'Country Pack' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name (English)' },
          { name: 'name_bn', required: true, label: 'Name (Bengali)' },
          { name: 'parent_code', label: 'Parent Code' },
          { name: 'date_value', label: 'Date (holiday packs)' }
        ] }
    ]
  },

  'M65-form-entity': {
    kind: 'model_form',
    model: 'fix.entity',
    title: 'Legal Entity',
    back: 'M65-entities',
    tabs: [
      { id: 'identity', label: '1. Entity', bn: '১. প্রতিষ্ঠান', icon: '🏢' },
      { id: 'statutory', label: '2. Statutory', bn: '২. বিধিবদ্ধ', icon: '📜' }
    ],
    sections: [
      { tab: 'identity', title: 'Entity', note: 'A legal company of the group; the entity roll-up drives consolidated reporting. The company is set when the entity is created and cannot then be moved.',
        fields: [
          { name: 'code', required: true, label: 'Entity Code' },
          { name: 'legal_name', required: true, label: 'Legal Name' },
          { name: 'legal_name_bn', label: 'Legal Name (Bengali)' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'country_id', required: true, label: 'Country' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'statutory', title: 'Statutory Registration', note: 'Record the real NBR registrations: the format is checked, whether a number is genuine is not. Changing the VAT due day or calendar rule moves a statutory date, so it also needs a finance manager. Every change here is tracked and audited.',
        fields: [
          { name: 'bin_number', label: 'BIN (13 digits)' },
          { name: 'tin_number', label: 'e-TIN (12 digits)' },
          { name: 'vat_statutory_day', label: 'VAT Due Day of Month' },
          { name: 'statutory_calendar_rule', required: true, label: 'Tax Calendar Rule' },
          { name: 'incorporation_date', label: 'Incorporation Date' }
        ] }
    ]
  },

  /* registry completion screens */
  'M65-bengali': { kind: 'table_report', module: 'M65', report: 'bengali_support', title: 'Bengali Support (bn-BD)', period: false },
  'M65-translations': { kind: 'table_report', module: 'M65', report: 'translation_completeness', title: 'Translation Infrastructure', period: false },
  /* Intercompany: M19 (the accounting) owns these records and their forms; M65
     shows them on its own page and captures through those forms. */
  'M65-intercompany': { kind: 'model_list', model: 'fix.intercompany.rule',
    cols: ['code', 'name', 'scope', 'source_entity_id', 'target_entity_id', 'transaction_type',
      'markup_percent', 'transfer_pricing_compliant', 'documentation_ref', 'active'] },
  'M65-ic-txns': { kind: 'model_list', model: 'fix.intercompany.transaction', stateField: 'state',
    cols: ['reference', 'name', 'scope', 'source_entity_id', 'target_entity_id',
      'transaction_date', 'amount', 'match_difference', 'state'],
    actions: [
      { m: 'action_generate_mirror', l: 'Post & Mirror' },
      { m: 'action_match', l: 'Match Against Ledger' },
      { m: 'action_mark_settled', l: 'Mark Settled' }
    ] },
  'M65-tp-rates': { kind: 'model_list', model: 'fix.transfer.price.rate', stateField: 'state',
    cols: ['rule_id', 'markup_percent', 'date_from', 'date_to', 'study_ref', 'approved_by_id', 'approved_at', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate (Accounting Administrator)' },
      { m: 'action_retire', l: 'Retire (Accounting Administrator)' }
    ] },

  /* ===== capture audit 2026-11-18: the records M65 owns and no code had ===== */
  'M65-entity-packs': { kind: 'model_list', model: 'fix.entity.jurisdiction', stateField: 'state',
    cols: ['entity_id', 'country_pack_id', 'pack_kind', 'pack_version', 'locale_pack_id',
      'reporting_currency_id', 'assigned_by_id', 'assigned_on', 'superseded_on', 'state'] },
  'M65-residency': { kind: 'model_list', model: 'fix.jurisdiction.residency.rule', stateField: 'state',
    cols: ['country_id', 'data_class', 'residency_required', 'cross_border_permitted',
      'notification_required', 'authority_name', 'statute_reference', 'effective_from', 'verified_by_id', 'state'],
    actions: [
      { m: 'action_verify', l: 'Verify (second Platform Admin)', ask: 'What did you check this rule against? Name the act, the section and its date.', kwarg: 'note' },
      { m: 'action_retire', l: 'Retire' }
    ] },
  'M65-onboarding': { kind: 'model_list', model: 'fix.country.onboarding', stateField: 'phase',
    cols: ['name', 'country_id', 'lead_id', 'initiated_on', 'elapsed_weeks', 'obligations_discovered',
      'residency_assessed', 'gate_result', 'phase'],
    actions: [
      { m: 'action_advance', l: 'Advance To Next Step' },
      { m: 'action_abandon', l: 'Abandon', ask: 'Why is this country onboarding being abandoned?', kwarg: 'reason' }
    ] },
  'M65-translation-entries': { kind: 'model_list', model: 'fix.translation.entry', stateField: 'state',
    cols: ['name', 'locale_pack_id', 'module_code', 'source_string', 'translated_string',
      'machine_translated', 'translated_by_id', 'reviewed_by_id', 'applied', 'is_stale', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (native-speaker review)', ask: 'You are the second person. What did you check (meaning, terminology, length on screen)?', kwarg: 'note' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is this translation rejected?', kwarg: 'note' }
    ] },
  'M65-rendering': { kind: 'model_list', model: 'fix.rendering.verification',
    cols: ['locale_pack_id', 'target', 'device', 'test_set_ref', 'verified_on', 'result',
      'issues', 'verified_by_id'] },

  'M65-form-entity-pack': {
    kind: 'model_form',
    model: 'fix.entity.jurisdiction',
    title: 'Entity Pack Assignment',
    back: 'M65-entity-packs',
    status: { field: 'state', labels: { current: 'Current', superseded: 'Superseded' } },
    sections: [
      { title: 'Assignment', note: 'Which active country pack a legal entity uses, with its default locale and group reporting currency. The pack version is recorded at assignment. A new assignment for the same kind of pack supersedes the current one, which stays on record; an assignment is never edited or deleted. Only a Platform Admin assigns.',
        fields: [
          { name: 'entity_id', required: true, label: 'Legal Entity' },
          { name: 'country_pack_id', required: true, label: 'Country Pack (active only)' },
          { name: 'locale_pack_id', label: 'Default Locale (active only)' },
          { name: 'reporting_currency_id', label: 'Group Reporting Currency' },
          { name: 'note', label: 'Note' },
          { name: 'pack_version', readonly: true, label: 'Pack Version (recorded)' },
          { name: 'assigned_by_id', readonly: true, label: 'Assigned By' },
          { name: 'assigned_on', readonly: true, label: 'Assigned On' },
          { name: 'superseded_by_id', readonly: true, label: 'Superseded By' }
        ] }
    ]
  },

  'M65-form-residency': {
    kind: 'model_form',
    model: 'fix.jurisdiction.residency.rule',
    title: 'Residency Rule',
    back: 'M65-residency',
    status: { field: 'state', labels: { draft: 'Draft', verified: 'Verified', retired: 'Retired' } },
    sections: [
      { title: 'Rule', note: 'Where one class of data may live and whether it may leave the country, under which statute. A second Platform Admin verifies it against the statute; verifying it retires the verified rule it replaces. A verified rule is frozen. Data protection does not read this register yet: it states the rule, it does not enforce it.',
        fields: [
          { name: 'country_id', required: true, label: 'Country' },
          { name: 'data_class', required: true, label: 'Data Class' },
          { name: 'residency_required', label: 'Must Stay In Country' },
          { name: 'cross_border_permitted', label: 'Cross-Border Transfer Permitted' },
          { name: 'notification_required', label: 'Transfer Must Be Notified' },
          { name: 'safeguard_required', label: 'Safeguard Required' },
          { name: 'authority_name', required: true, label: 'Authority' },
          { name: 'statute_reference', required: true, label: 'Statute / Clause' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'verified_on', readonly: true, label: 'Verified On' },
          { name: 'verification_note', readonly: true, label: 'Verified Against' }
        ] }
    ]
  },

  'M65-form-onboarding': {
    kind: 'model_form',
    model: 'fix.country.onboarding',
    title: 'Country Onboarding',
    back: 'M65-onboarding',
    status: { field: 'phase', labels: { discovery: '1. Obligation Discovery', pack_authoring: '2. Pack Authoring', translation: '3. Translation', integration: '4. Integration Selection', validation: '5. Validation', pilot: '6. Pilot', active: '7. Active', abandoned: 'Abandoned' } },
    tabs: [
      { id: 'scope', label: '1. Country & Scope', bn: '১. দেশ ও পরিসর', icon: '🌍' },
      { id: 'gate', label: '2. Readiness Gate', bn: '২. প্রস্তুতি যাচাই', icon: '🚦' },
      { id: 'progress', label: '3. Progress', bn: '৩. অগ্রগতি', icon: '📅' }
    ],
    sections: [
      { tab: 'scope', title: 'Country & Scope', note: 'One onboarding per new country, measured against the 12-week target. Advance moves it one step and is refused until that step has what it needs: obligations recorded as jurisdiction rules, the packs named, an active locale, payment gateways selected.',
        fields: [
          { name: 'country_id', required: true, label: 'Country' },
          { name: 'lead_id', required: true, label: 'Country Lead' },
          { name: 'pack_ids', label: 'Country Packs' },
          { name: 'locale_pack_id', label: 'Locale Pack' },
          { name: 'gateway_ids', label: 'Payment Gateways' }
        ] },
      { tab: 'gate', title: 'Zero-Core-Change Gate', note: 'Tick Needs A Core Code Change if standing the country up needs any change to core module code: the pilot is then refused, because a country must be data, not code. The pilot also needs every pack certified and a verified data residency rule. Activation needs every pack active, a gateway active, and a second person.',
        fields: [
          { name: 'core_changes_required', label: 'Needs A Core Code Change' },
          { name: 'core_change_note', label: 'Core Changes Found' },
          { name: 'gate_result', readonly: true, label: 'Gate Result' },
          { name: 'obligations_discovered', readonly: true, label: 'Obligations Recorded' },
          { name: 'residency_assessed', readonly: true, label: 'Residency Assessed' }
        ] },
      { tab: 'progress', title: 'Progress', note: 'Dates are stamped by the steps, never typed.',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'initiated_on', readonly: true, label: 'Initiated On' },
          { name: 'piloted_on', readonly: true, label: 'Pilot Started On' },
          { name: 'activated_on', readonly: true, label: 'Activated On' },
          { name: 'activated_by_id', readonly: true, label: 'Activated By' },
          { name: 'elapsed_weeks', readonly: true, label: 'Elapsed Weeks' },
          { name: 'on_target', readonly: true, label: 'Within 12 Weeks' },
          { name: 'abandoned_reason', readonly: true, label: 'Why Abandoned' }
        ] }
    ]
  },

  'M65-form-translation': {
    kind: 'model_form',
    model: 'fix.translation.entry',
    title: 'Translation Review',
    back: 'M65-translation-entries',
    status: { field: 'state', labels: { submitted: 'Awaiting Review', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'text', label: '1. Translation', bn: '১. অনুবাদ', icon: '🔤' },
      { id: 'review', label: '2. Review', bn: '২. পর্যালোচনা', icon: '✅' }
    ],
    sections: [
      { tab: 'text', title: 'Translation', note: 'Translate the text of one record (name its record type, ID and field: the English is read from the record) or one interface string (leave those empty and type the English). A second person approves it; machine translation is refused for release. Approving a record translation writes it into that record in the locale\'s language.',
        fields: [
          { name: 'locale_pack_id', required: true, label: 'Locale' },
          { name: 'module_code', label: 'Module / Portal' },
          { name: 'target_model', label: 'Record Type (technical)' },
          { name: 'target_id', label: 'Record ID' },
          { name: 'target_field', label: 'Field' },
          { name: 'source_string', label: 'Source (English)' },
          { name: 'translated_string', required: true, label: 'Translation' },
          { name: 'machine_translated', label: 'Machine Translated' }
        ] },
      { tab: 'review', title: 'Review', note: 'Stamped by the review, never typed. Source Changed Since means the English text moved after this was translated: translate it again.',
        fields: [
          { name: 'translated_by_id', readonly: true, label: 'Translated By' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By' },
          { name: 'reviewed_on', readonly: true, label: 'Reviewed On' },
          { name: 'review_note', readonly: true, label: 'Review Note' },
          { name: 'applied', readonly: true, label: 'Written To The Record' },
          { name: 'is_stale', readonly: true, label: 'Source Changed Since' }
        ] }
    ]
  },

  'M65-form-rendering': {
    kind: 'model_form',
    model: 'fix.rendering.verification',
    title: 'Rendering Verification',
    back: 'M65-rendering',
    sections: [
      { title: 'Verification', note: 'Evidence that Bengali text renders correctly on one target: the device, the test set checked (conjuncts, numerals, taka amounts, long names) and the result, with a photo, print scan or PDF. A failure names the issues. A verification is never edited: record a new one.',
        fields: [
          { name: 'locale_pack_id', required: true, label: 'Locale' },
          { name: 'target', required: true, label: 'Target' },
          { name: 'device', required: true, label: 'Device / Printer / Viewer' },
          { name: 'test_set_ref', required: true, label: 'Test Set' },
          { name: 'verified_on', required: true, label: 'Verified On' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'issues', label: 'Issues Found' },
          { name: 'evidence_attachment_id', label: 'Evidence (photo / print scan / PDF)' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' }
        ] }
    ]
  },
  'M65-gateways': { kind: 'model_list', model: 'fix.payment.gateway', stateField: 'state', cols: ['name', 'provider', 'country_code', 'mode', 'currencies', 'settlement_cycle_days', 'approval_state', 'state'],
    /* A12 P1-4: Activate is M63-routed (no button) - Route sends the draft or
       suspended rail to the coded approver group; every transition is written
       to the security audit chain. A12 finish E8: rotating a live credential
       is routed too, and stays inside its vault namespace. */
    actions: [{ m: 'action_request_approval', l: 'Route Activation', ask: 'Why should this gateway go live?', kwarg: 'justification' },
              { m: 'action_recall_approval', l: 'Recall Request' },
              { m: 'action_suspend', l: 'Suspend', ask: 'Why is this gateway being suspended?', kwarg: 'reason' },
              { m: 'action_rotate_credential', l: 'Rotate Credential',
                asks: [{ label: 'New vault reference (vault://...)', kwarg: 'new_ref' }, { label: 'Why is it being rotated?', kwarg: 'reason' }] }] },
  'M65-assessment': { kind: 'table_report', module: 'M65', report: 'expansion_assessment', title: 'Expansion Assessment', period: false },


  /* ===== registry completion forms ===== */
  'M65-form-gateway': {
    kind: 'model_form',
    model: 'fix.payment.gateway',
    title: "Payment Gateway",
    back: 'M65-gateways',
    status: { field: 'state', labels: { draft: "Draft", active: "Active", suspended: "Suspended" } },
    sections: [
      { title: "Payment Gateway", note: "A gateway holds a VAULT REFERENCE only - API keys are never entered here (SEC-101). Give it when you create the rail; afterwards use Rotate Credential, which on a live rail goes to an approver. No integration reads this reference yet, so rotating it does not change a live secret. Going live is M63-routed and audited. Once past draft the rail's identity is frozen. Storefront checkout is the only reader of this register.",
        fields: [
          { name: 'provider', required: true, label: "Provider" },
          { name: 'country_code', required: true, label: "Country Code" },
          { name: 'mode', required: true, label: "Mode (sandbox while drafting)" },
          { name: 'currencies', required: true, label: "Currencies" },
          { name: 'credential_ref', required: true, label: "Credential Reference (vault://…)" },
          { name: 'settlement_cycle_days', label: "Settlement Cycle (days)" },
          { name: 'supports_refund', label: "Supports Refund" },
          { name: 'supports_partial_refund', label: "Supports Partial Refund" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M65:Translation Completeness': 'M65-translations',
  'M65:Country Pack Inventory': 'M65-packstatus',
  'M65:Cross-Border Transfer Log': 'M65-intercompany',
  'M65:Entity Structure': 'M65-structure',
  'M65:Country Pack Status': 'M65-packstatus',
  'M65:Locale Readiness': 'M65-readiness',
  'M65:Expansion Assessment': 'M65-assessment',
  'M65:Bengali Support': 'M65-bengali'
};

export const FORM_MODELS = {
  'M65:Country Pack': 'fix.country.pack',
  'M65:Locale Pack': 'fix.locale.pack',
  'M65:Jurisdiction Rule': 'fix.jurisdiction.rule',
  'M65:Legal Entity': 'fix.entity',
  'M65:Entity Pack Assignment': 'fix.entity.jurisdiction',
  'M65:Pack Line': 'fix.country.pack.line',
  'M65:Payment Gateway': 'fix.payment.gateway',
  'M65:Residency Rule': 'fix.jurisdiction.residency.rule',
  'M65:Country Onboarding': 'fix.country.onboarding',
  'M65:Translation Review': 'fix.translation.entry',
  'M65:Rendering Verification': 'fix.rendering.verification',
  'M65:Intercompany Rule': 'fix.intercompany.rule',
  'M65:Intercompany Charge': 'fix.intercompany.transaction',
  'M65:Transfer-Pricing Rate': 'fix.transfer.price.rate'
};

export const FORM_CHIPS = {
  'M65:Country Pack': 'M65-form-country',
  'M65:Locale Pack': 'M65-form-locale',
  'M65:Jurisdiction Rule': 'M65-form-jurisdiction',
  'M65:Legal Entity': 'M65-form-entity',
  'M65:Entity Pack Assignment': 'M65-form-entity-pack',
  'M65:Pack Line': 'M65-form-packline',
  'M65:Payment Gateway': 'M65-form-gateway',
  'M65:Residency Rule': 'M65-form-residency',
  'M65:Country Onboarding': 'M65-form-onboarding',
  'M65:Translation Review': 'M65-form-translation',
  'M65:Rendering Verification': 'M65-form-rendering',
  /* M19 owns the intercompany records; its forms are the capture */
  'M65:Intercompany Rule': 'M19-form-icrule',
  'M65:Intercompany Charge': 'M19-form-ic',
  'M65:Transfer-Pricing Rate': 'M19-form-tp-rate',
  'M65:__by_model__': {
    'fix.payment.gateway': 'M65-form-gateway',
    'fix.locale.pack': 'M65-form-locale',
    'fix.jurisdiction.rule': 'M65-form-jurisdiction',
    'fix.entity': 'M65-form-entity',
    'fix.country.pack': 'M65-form-country',
    'fix.country.pack.line': 'M65-form-packline',
    'fix.entity.jurisdiction': 'M65-form-entity-pack',
    'fix.jurisdiction.residency.rule': 'M65-form-residency',
    'fix.country.onboarding': 'M65-form-onboarding',
    'fix.translation.entry': 'M65-form-translation',
    'fix.rendering.verification': 'M65-form-rendering'
  },
  'M65:__by_screen__': {
    'M65-gateways': 'M65-form-gateway',
    'M65-locales': 'M65-form-locale',
    'M65-jurisdictions': 'M65-form-jurisdiction',
    'M65-entities': 'M65-form-entity',
    'M65-packs': 'M65-form-country',
    'M65-packlines': 'M65-form-packline',
    'M65-entity-packs': 'M65-form-entity-pack',
    'M65-residency': 'M65-form-residency',
    'M65-onboarding': 'M65-form-onboarding',
    'M65-translation-entries': 'M65-form-translation',
    'M65-rendering': 'M65-form-rendering',
    'M65-intercompany': 'M19-form-icrule',
    'M65-ic-txns': 'M19-form-ic',
    'M65-tp-rates': 'M19-form-tp-rate'
  }
};

// Country-pack creation is a data load (kind + lines), not a hand form; the
// chip routes to the pack grid screen.
export const CREATE = {
  M65: { screen: 'M65-form-locale', model: 'fix.locale.pack', label: 'Locale Pack' }
};
