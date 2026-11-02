/** @odoo-module **/
/* A12 · M65 Multi-Entity & Localisation. 3 groups / 9 screens / 3 reports / 3 forms / freg 48. */

export const MODULE = {
  area: 'A12', code: 'M65', en: 'Multi-Entity & Localisation', title: 'M65 · Multi-Entity & Localisation',
  bn: 'মাল্টি-এন্টিটি ও লোকালাইজেশন', icon: '🌐',
  desc: 'Legal entity structure, country packs (divisions, holidays, postcodes), locale packs with number formats and coverage, and jurisdiction rules per authority.',
  kpis: [
    { l: 'Entities', m: 'entities' },
    { l: 'Country Packs', m: 'country_packs' },
    { l: 'Locales Active', m: 'locales_active' },
    { l: 'Jurisdiction Rules', m: 'jurisdiction_rules' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M65-bengali', en: 'Bengali Support (bn-BD)', bn: 'Bengali Support (bn-BD)', t: 'g' },
      { id: 'M65-translations', en: 'Translation Infrastructure', bn: 'Translation Infrastructure', t: 'g' },
      { id: 'M65-intercompany', en: 'Intercompany', bn: 'Intercompany', t: 'g' },
      { id: 'M65-gateways', en: 'Payment Gateways (Razorpay/KBZPay/eSewa)', bn: 'পেমেন্ট গেটওয়ে', t: 'g' },
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
      { id: 'M65-jurisdictions', en: 'Jurisdiction Rules', bn: 'এখতিয়ার', t: 'g' }
    ]}
  ],
  reports: ['Entity Structure', 'Country Pack Status', 'Locale Readiness'],
  forms: ['Country Pack', 'Locale Pack', 'Jurisdiction Rule'],
  cross: ['M30 branch registry', 'M51 BD tax rules', 'M55 holidays'],
  freg: { src: 48, sub: [
    ['1', 'Entity Structure', 10], ['2', 'Country Packs', 9], ['3', 'Locale Packs', 8],
    ['4', 'Jurisdiction', 7], ['5', 'Translation', 8], ['6', 'Audit', 6]
  ] }
};

export const SCREENS = {
  'M65-entities': { kind: 'model_list', model: 'fix.entity',
    cols: ['code', 'legal_name', 'legal_name_bn', 'active'] },
  'M65-structure': { kind: 'table_report', module: 'M65', report: 'entity_structure', title: 'Entity Structure', period: false },
  'M65-packs': { kind: 'model_list', model: 'fix.country.pack',
    cols: ['name', 'code', 'kind', 'version', 'loaded_at', 'active'] },
  'M65-packlines': { kind: 'model_list', model: 'fix.country.pack.line',
    cols: ['pack_id', 'parent_code', 'code', 'name', 'name_bn', 'active'] },
  'M65-packstatus': { kind: 'table_report', module: 'M65', report: 'country_pack_status', title: 'Country Pack Status', period: false },
  'M65-locales': { kind: 'model_list', model: 'fix.locale.pack', stateField: 'state',
    cols: ['code', 'name', 'number_format', 'date_format', 'coverage_pct', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate Locale' }] },
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
      { title: 'Locale', note: 'A locale code is unique per company. The number format drives the en-IN lakh grouping used across the workspace.',
        fields: [
          { name: 'code', required: true, label: 'Locale Code' },
          { name: 'name', required: true, label: 'Locale Name' },
          { name: 'number_format', required: true, label: 'Number Format' },
          { name: 'first_day_of_week', required: true, label: 'First Day of Week' },
          { name: 'date_format', required: true, label: 'Date Format' },
          { name: 'coverage_pct', label: 'Translation Coverage %' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M65-form-jurisdiction': {
    kind: 'model_form',
    model: 'fix.jurisdiction.rule',
    title: 'Jurisdiction Rule',
    back: 'M65-jurisdictions',
    sections: [
      { title: 'Rule', note: 'One statutory requirement per authority: what is required, how often, and the penalty for non-compliance.',
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
    sections: [
      { title: 'Pack', note: 'Lines (divisions, holidays, postcodes) are loaded by the pack loader; the header records which pack version is active.',
        fields: [
          { name: 'name', required: true, label: 'Pack Name' },
          { name: 'code', required: true, label: 'Pack Code' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M65-form-packline': {
    kind: 'model_form',
    model: 'fix.country.pack.line',
    title: 'Pack Line',
    back: 'M65-packlines',
    sections: [
      { title: 'Line', note: 'A line is one division/district, holiday or postcode inside its pack. parent_code links the hierarchy.',
        fields: [
          { name: 'pack_id', required: true, label: 'Country Pack' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name (English)' },
          { name: 'name_bn', label: 'Name (Bengali)' },
          { name: 'parent_code', label: 'Parent Code' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M65-form-entity': {
    kind: 'model_form',
    model: 'fix.entity',
    title: 'Legal Entity',
    back: 'M65-entities',
    sections: [
      { title: 'Entity', note: 'A legal company of the group; the entity roll-up drives consolidated reporting.',
        fields: [
          { name: 'code', required: true, label: 'Entity Code' },
          { name: 'legal_name', required: true, label: 'Legal Name' },
          { name: 'legal_name_bn', label: 'Legal Name (Bengali)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* registry completion screens */
  'M65-bengali': { kind: 'table_report', module: 'M65', report: 'bengali_support', title: 'Bengali Support (bn-BD)', period: false },
  'M65-translations': { kind: 'table_report', module: 'M65', report: 'translation_completeness', title: 'Translation Infrastructure', period: false },
  'M65-intercompany': { kind: 'model_list', model: 'fix.intercompany.rule', create: false, cols: ['name', 'model_id'] },
  'M65-gateways': { kind: 'model_list', model: 'fix.payment.gateway', stateField: 'state', cols: ['provider', 'country_code', 'mode', 'currencies', 'settlement_cycle_days', 'state'], actions: [{ m: 'action_activate', l: 'Activate' }] },
  'M65-assessment': { kind: 'table_report', module: 'M65', report: 'expansion_assessment', title: 'Expansion Assessment', period: false },


  /* ===== registry completion forms ===== */
  'M65-form-gateway': {
    kind: 'model_form',
    model: 'fix.payment.gateway',
    title: "Payment Gateway",
    back: 'M65-gateways',
    status: { field: 'state', labels: { draft: "Draft", active: "Active", suspended: "Suspended" } },
    sections: [
      { title: "Payment Gateway", note: "A gateway holds a VAULT REFERENCE only - API keys are never entered here (SEC-101). The reference must start with vault://.",
        fields: [
          { name: 'provider', required: true, label: "Provider" },
          { name: 'country_code', required: true, label: "Country Code" },
          { name: 'mode', required: true, label: "Mode" },
          { name: 'currencies', required: true, label: "Currencies" },
          { name: 'credential_ref', required: true, label: "Credential Reference" },
          { name: 'settlement_cycle_days', label: "Settlement Cycle (days)" },
          { name: 'supports_refund', label: "Supports Refund" },
          { name: 'supports_partial_refund', label: "Supports Partial Refund" },
          { name: 'state', required: true, label: "State" }
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
