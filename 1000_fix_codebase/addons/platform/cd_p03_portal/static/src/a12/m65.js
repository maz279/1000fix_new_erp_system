/** @odoo-module **/
/* A12 · M65 Multi-Entity & Localisation. 3 groups / 9 screens / 3 reports / 3 forms / freg 48. */

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
    { l: 'Live Gateways', m: 'gateways_live' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M65-bengali', en: 'Bengali Support (bn-BD)', bn: 'Bengali Support (bn-BD)', t: 'g' },
      { id: 'M65-translations', en: 'Translation Infrastructure', bn: 'Translation Infrastructure', t: 'g' },
      { id: 'M65-intercompany', en: 'Intercompany', bn: 'Intercompany', t: 'g' },
      { id: 'M65-gateways', en: 'Payment Gateways (Storefront Checkout Only)', bn: 'পেমেন্ট গেটওয়ে', t: 'g' },
      { id: 'M65-assessment', en: 'Expansion Assessment', bn: 'Expansion Assessment', t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M65-entities', en: 'Entities per Country', bn: 'প্রতিষ্ঠান', t: 'g' },
      { id: 'M65-structure', en: 'Entity Structure', bn: 'গঠন', t: 'r' }
    ]},
    { en: 'Country', screens: [
      { id: 'M65-packs', en: 'Country Pack Authoring', bn: 'কান্ট্রি প্যাক', t: 'g' },
      { id: 'M65-packlines', en: 'Pack Lines', bn: 'প্যাক লাইন', t: 'g' },
      { id: 'M65-packstatus', en: 'Pack Status', bn: 'প্যাক স্ট্যাটাস', t: 'r' }
    ]},
    { en: 'Localisation', screens: [
      { id: 'M65-locales', en: 'Locale Packs', bn: 'লোকেল', t: 'g' },
      { id: 'M65-readiness', en: 'Locale Readiness', bn: 'প্রস্তুতি', t: 'r' },
      { id: 'M65-jurisdictions', en: 'Jurisdiction Rules (Documentation Only)', bn: 'এখতিয়ার', t: 'g' }
    ]}
  ],
  reports: ['Entity Structure', 'Country Pack Status', 'Locale Readiness'],
  forms: ['Country Pack', 'Locale Pack', 'Jurisdiction Rule'],
  cross: ['M30 branch registry', 'M51 BD tax rules', 'M55 holidays'],
  freg: { src: 48, sub: [
    ['1', 'Entity Structure', 10, { model: 'fix.entity', cols: ['code', 'legal_name', 'country_id', 'currency_id', 'active'], screens: ['M65-entities', 'M65-structure'] }],
    ['2', 'Country Packs', 9, { model: 'fix.country.pack', cols: ['name', 'code', 'kind', 'version', 'loaded_at'], screens: ['M65-packs', 'M65-packlines', 'M65-packstatus', 'M65-gateways'] }],
    ['3', 'Locale Packs', 8, { model: 'fix.locale.pack', cols: ['code', 'name', 'number_format', 'date_format', 'coverage_pct'], screens: ['M65-locales', 'M65-readiness'] }],
    ['4', 'Jurisdiction', 7, { model: 'fix.jurisdiction.rule', cols: ['jurisdiction', 'rule_area', 'requirement', 'frequency', 'authority'], screens: ['M65-jurisdictions', 'M65-assessment'] }],
    ['5', 'Translation', 8, { model: 'fix.locale.pack', cols: ['code', 'name', 'coverage_pct', 'state'], screens: ['M65-translations', 'M65-bengali'] }],
    ['6', 'Audit', 6, { model: 'fix.intercompany.rule', cols: ['name', 'scope', 'transaction_type', 'transfer_pricing_compliant', 'documentation_ref'], screens: ['M65-intercompany'] }]
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
  'M65-intercompany': { kind: 'model_list', model: 'fix.intercompany.rule', create: false, cols: ['name', 'code', 'scope', 'transaction_type'] },
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
  'M65:Locale Readiness': 'M65-readiness'
};

export const FORM_MODELS = {
  'M65:Country Pack': 'fix.country.pack',
  'M65:Locale Pack': 'fix.locale.pack',
  'M65:Jurisdiction Rule': 'fix.jurisdiction.rule'
};

export const FORM_CHIPS = {
  'M65:Country Pack': 'M65-form-country',
  'M65:Locale Pack': 'M65-form-locale',
  'M65:Jurisdiction Rule': 'M65-form-jurisdiction',
  'M65:__by_model__': {
    'fix.payment.gateway': 'M65-form-gateway',
    'fix.locale.pack': 'M65-form-locale',
    'fix.jurisdiction.rule': 'M65-form-jurisdiction',
    'fix.entity': 'M65-form-entity',
    'fix.country.pack': 'M65-form-country',
    'fix.country.pack.line': 'M65-form-packline'
  },
  'M65:__by_screen__': {
    'M65-gateways': 'M65-form-gateway',
    'M65-locales': 'M65-form-locale',
    'M65-jurisdictions': 'M65-form-jurisdiction',
    'M65-entities': 'M65-form-entity',
    'M65-packs': 'M65-form-country',
    'M65-packlines': 'M65-form-packline'
  }
};

// Country-pack creation is a data load (kind + lines), not a hand form; the
// chip routes to the pack grid screen.
export const CREATE = {
  M65: { screen: 'M65-form-locale', model: 'fix.locale.pack', label: 'Locale Pack' }
};
