/** @odoo-module **/
/* A04 · Commercial & Revenue — M37 Product & Service Catalogue (v2 rebuild).
 * Registry-faithful: 5 groups / 17 screens / 6 reports / 5 forms / freg 120.
 * Catalogue items (400 services), fault codes, kits and rental SKUs are real;
 * the rBOM is the new fix.rbom.line. Lifecycle/publication fields were added
 * to fix.catalogue.item. */

export const MODULE = {
  area: 'A04', code: 'M37', en: 'Product & Service Catalogue', title: 'M37 · Product & Service Catalogue',
  bn: 'পণ্য ও সেবা ক্যাটালগ', icon: '📦',
  desc: 'Unified item master across nine types, taxonomy and hierarchy, service definitions, rBOM and SRT, brand-model compatibility, fault taxonomy, contract/protection/rental templates, lifecycle and publication.',
  kpis: [
    { l: 'Active Items', m: 'active_items' },
    { l: 'rBOM Coverage', m: 'rbom_coverage', suffix: '%' },
    { l: 'New SKUs MTD', m: 'new_skus_mtd' },
    { l: 'Pending Approval', m: 'pending_approval' },
    { l: 'Model Compatibility', m: 'model_compatibility' },
    { l: 'Bilingual Content', m: 'bilingual_content', suffix: '%' }
  ],
  groups: [
    { en: 'Catalogue Records', screens: [
      { id: 'M37-brand', en: "Brand", bn: "Brand", t: 'g' },
      { id: 'M37-refurb-grade', en: "Refurb Grade", bn: "Refurb Grade", t: 'g' }
    ]},
    { en: 'Item Master', screens: [
      { id: 'M37-items', en: 'Unified Item Master', bn: 'ইউনিফায়েড আইটেম মাস্টার', t: 'g' },
      { id: 'M37-form-item', en: 'Item Record', bn: 'আইটেম রেকর্ড', t: 'f' },
      { id: 'M37-taxonomy', en: 'Typed Taxonomy (14 streams)', bn: 'টাইপড ট্যাক্সোনমি', t: 'g' },
      { id: 'M37-hierarchy', en: 'Product Hierarchy', bn: 'পণ্য শ্রেণিবিন্যাস', t: 'g' }
    ]},
    { en: 'Service Definitions', screens: [
      { id: 'M37-services', en: 'Service Definitions', bn: 'সেবা সংজ্ঞা', t: 'g' },
      { id: 'M37-rbom', en: 'Repair BOM (rBOM)', bn: 'রিপেয়ার BOM', t: 'g' },
      { id: 'M37-srt', en: 'Standard Repair Time (SRT)', bn: 'স্ট্যান্ডার্ড রিপেয়ার টাইম', t: 'g' },
      { id: 'M37-kits', en: 'Kits & Bundles', bn: 'কিট ও বান্ডল', t: 'g' }
    ]},
    { en: 'Compatibility & Faults', screens: [
      { id: 'M37-brandmodel', en: 'Brand-Model-Device Master', bn: 'ব্র্যান্ড-মডেল মাস্টার', t: 'g' },
      { id: 'M37-fault', en: 'Fault / Symptom / Root-Cause', bn: 'ফল্ট ট্যাক্সোনমি', t: 'g' },
      { id: 'M37-parts-id', en: 'Part Identity & Supersession', bn: 'পার্ট আইডেন্টিটি', t: 'g' }
    ]},
    { en: 'Plans & Templates', screens: [
      { id: 'M37-contract-tpl', en: 'Contract Templates', bn: 'চুক্তি টেমপ্লেট', t: 'g' },
      { id: 'M37-protection', en: 'Protection Plan Catalogue', bn: 'প্রোটেকশন প্ল্যান', t: 'g' },
      { id: 'M37-rental-sku', en: 'Rental SKUs & Grades', bn: 'রেন্টাল SKU', t: 'g' }
    ]},
    { en: 'Catalogue Governance', screens: [
      { id: 'M37-approval', en: 'Item Approval Workflow', bn: 'আইটেম অনুমোদন', t: 'c' },
      { id: 'M37-lifecycle', en: 'Item Lifecycle & Deprecation', bn: 'লাইফসাইকেল', t: 'g' },
      { id: 'M37-publication', en: 'Channel Publication', bn: 'প্রকাশনা', t: 'g' }
    ]}
  ],
  reports: ['Catalogue Coverage by Brand', 'rBOM Completeness', 'SRT Calibration Variance', 'Item Margin Analysis', 'Deprecated Items Register', 'Bilingual Content Gaps'],
  forms: ['Catalogue Item (9 types)', 'Service Definition', 'rBOM Line', 'Fault Code', 'Protection Product Template'],
  cross: ['M11 Pricing', 'M36 Quotations', 'M15 Inventory', 'M16 Procurement'],
  freg: { src: 120, sub: [
    ['1', 'Unified Item Master', 14, { model: 'fix.catalogue.item', cols: ['product_tmpl_id', 'name_bn', 'item_type', 'brand_id', 'state', 'active'], screens: ['M37-items'], reports: ['Catalogue Coverage by Brand', 'Deprecated Items Register'], forms: ['Catalogue Item (9 types)'] }], ['2', 'Typed Taxonomy', 6, { model: 'product.category', cols: ['name', 'parent_id'], screens: ['M37-taxonomy'], reports: ['Catalogue Coverage by Brand'] }], ['3', 'Service Definition', 11, { model: 'fix.catalogue.item', cols: ['product_tmpl_id', 'name_bn', 'item_type', 'state', 'active'], screens: ['M37-services'], reports: ['Item Margin Analysis'], forms: ['Service Definition'] }],
    ['4', 'rBOM & SRT', 12, { model: 'fix.rbom.line', cols: ['item_id', 'component_item_id', 'sequence', 'quantity', 'note'], screens: ['M37-rbom', 'M37-srt'], reports: ['rBOM Completeness', 'SRT Calibration Variance'], forms: ['rBOM Line'] }], ['5', 'Repair Operations', 8, { model: 'fix.rbom.line', cols: ['item_id', 'component_item_id', 'quantity'], screens: ['M37-srt'], reports: ['SRT Calibration Variance'], forms: ['rBOM Line'] }], ['6', 'Kits & Bundles', 4, { model: 'fix.service.kit', cols: ['name', 'name_bn', 'catalogue_item_id', 'component_count', 'estimated_cost', 'estimated_time', 'active'], screens: ['M37-kits'], reports: ['Item Margin Analysis'] }],
    ['7', 'Product Hierarchy & Variants', 8, { screens: ['M37-hierarchy'], reports: ['Catalogue Coverage by Brand'] }], ['8', 'Brand-Model-Device Master', 9, { model: 'fix.brand', cols: ['name', 'name_bn', 'code', 'authorised', 'authorisation_expiry', 'model_count', 'active'], screens: ['M37-brand', 'M37-brandmodel'], reports: ['Catalogue Coverage by Brand'] }],
    ['9', 'Fault Taxonomy', 10, { model: 'fix.fault.code', cols: ['name', 'code', 'category', 'default_severity', 'active'], screens: ['M37-fault'] }], ['10', 'Part Identity', 9, { model: 'fix.rbom.line', cols: ['item_id', 'component_item_id', 'quantity', 'note'], screens: ['M37-parts-id'], reports: ['rBOM Completeness'], forms: ['rBOM Line'] }],
    ['11', 'Contract & Protection Templates', 10, { model: 'fix.contract.template', cols: ['code', 'name', 'contract_type', 'generation_type', 'duration_months', 'notice_period_days', 'active'], screens: ['M37-contract-tpl', 'M37-protection'], forms: ['Protection Product Template'] }], ['12', 'Tax & Rev-Rec Classification', 7, { model: 'fix.catalogue.item', cols: ['product_tmpl_id', 'item_type', 'state'], screens: ['M37-items'], reports: ['Item Margin Analysis'] }],
    ['13', 'Lifecycle & Governance', 10, { screens: ['M37-lifecycle', 'M37-approval', 'M37-publication'], reports: ['Deprecated Items Register', 'Bilingual Content Gaps'] }]
  ] }
};

export const SCREENS = {
  /* ---- registry screens restored (A04 zero-trust audit 2026-10-31): nav ids that dead-ended ---- */
  'M37-taxonomy': { kind: 'model_list', model: 'product.category', create: false,
    cols: ['complete_name', 'parent_id', 'product_count'] },
  'M37-hierarchy': { kind: 'table_report', module: 'M37', report: 'catalogue_hierarchy', title: 'Catalogue Hierarchy', period: true },
  'M37-services': { kind: 'model_list', model: 'fix.catalogue.item', create: false,
    cols: ['product_tmpl_id', 'name_bn', 'item_type', 'brand_id', 'state', 'active'],
    stateField: 'state' },
  'M37-rbom': { kind: 'model_list', model: 'fix.rbom.line', create: false,
    cols: ["create_date", "item_id", "component_item_id", "sequence", "quantity", "note", "create_uid"] },
  'M37-srt': { kind: 'table_report', module: 'M37', report: 'srt_variance', title: 'SRT Variance', period: true },
  // A kit is defined by its components, so the list must be able to
  // create one and the form must show them (see M37-form-kit.lines).
  'M37-kits': { kind: 'model_list', model: 'fix.service.kit', create: true,
    cols: ['name', 'name_bn', 'catalogue_item_id', 'component_count', 'estimated_cost', 'estimated_time', 'active'] },
  'M37-brandmodel': { kind: 'model_list', model: 'fix.brand', create: false,
    cols: ['name', 'name_bn', 'code', 'authorised', 'authorisation_expiry', 'model_count', 'active'] },
  'M37-fault': { kind: 'model_list', model: 'fix.fault.code', create: false,
    cols: ["name", "code", "create_date", "active", "category", "default_severity", "create_uid"] },
  'M37-parts-id': { kind: 'model_list', model: 'fix.rbom.line', create: false,
    cols: ["create_date", "item_id", "component_item_id", "sequence", "quantity", "note", "create_uid"] },
  'M37-contract-tpl': { kind: 'model_list', model: 'fix.contract.template', create: true,
    cols: ['code', 'name', 'contract_type', 'generation_type', 'duration_months', 'notice_period_days', 'active'],
    stateField: 'contract_type' },
  'M37-protection': { kind: 'model_list', model: 'fix.catalogue.item', create: true,
    cols: ['product_tmpl_id', 'name_bn', 'item_type', 'brand_id', 'state', 'active'],
    stateField: 'state' },
  'M37-rental-sku': { kind: 'model_list', model: 'fix.rental.sku', create: false,
    cols: ['name', 'catalogue_item_id', 'daily_rate', 'weekly_rate', 'monthly_rate', 'security_deposit', 'max_rental_days', 'active'] },
  'M37-approval': { kind: 'table_report', module: 'M37', report: 'approval_queue', title: 'Catalogue Approval Queue', period: false },
  'M37-lifecycle': { kind: 'table_report', module: 'M37', report: 'lifecycle_summary', title: 'Item Lifecycle Summary', period: false },
  'M37-publication': { kind: 'table_report', module: 'M37', report: 'publication_status', title: 'Publication Status', period: false },


  /* Report screens */
  'M37-rpt-brand': { kind: 'table_report', module: 'M37', report: 'coverage_by_brand', title: 'Catalogue Coverage by Brand', period: false },
  'M37-rpt-rbom': { kind: 'table_report', module: 'M37', report: 'rbom_completeness', title: 'rBOM Completeness', period: false },
  'M37-rpt-srt': { kind: 'table_report', module: 'M37', report: 'srt_variance', title: 'SRT Calibration Variance', period: false },
  'M37-rpt-margin': { kind: 'table_report', module: 'M37', report: 'item_margin', title: 'Item Margin Analysis', period: false },
  'M37-rpt-deprecated': { kind: 'table_report', module: 'M37', report: 'deprecated_items', title: 'Deprecated Items Register', period: false },
  'M37-rpt-bilingual': { kind: 'table_report', module: 'M37', report: 'bilingual_gaps', title: 'Bilingual Content Gaps', period: false },

  'M37-items': { kind: 'model_list', model: 'fix.catalogue.item', stateField: 'state',
    cols: ['product_tmpl_id', 'item_type', 'brand_id', 'category_id', 'state', 'is_published',
      'is_warranty_eligible', 'active'] },
  'M37-form-item': {
    kind: 'model_form',
    model: 'fix.catalogue.item',
    title: 'Catalogue Master Item & Engineering SKU',
    back: 'M37-items',
    status: { field: 'state' },
    tabs: [
      { id: 'product', label: '1. Product Master', bn: '১. পণ্য পরিচিতি', icon: '📦', badge: '6' },
      { id: 'costing', label: '2. Costing & SRT Standards', bn: '২. খরচ ও এসআরটি', icon: '⏱️', badge: '3' },
      { id: 'rbom', label: '3. Repair BOM & Kits', bn: '৩. মেরামত বিওএম', icon: '🔧', badge: '2' },
      { id: 'statutory', label: '4. Statutory HS Code & VAT', bn: '৪. এইচএস কোড ও ভ্যাট', icon: '⚖️', badge: '2' },
      { id: 'lifecycle', label: '5. Lifecycle & Publishing', bn: '৫. লাইফসাইকেল ও প্রকাশ', icon: '🔄', badge: '5' },
      { id: 'vault', label: '6. Technical Datasheets', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'product', title: 'Item Master Classification',
        note: 'Universal engineering catalogue kernel for IT, mobile, and electronics service delivery.',
        fields: [
          { name: 'product_tmpl_id', required: true, label: 'Product Template (Odoo Kernel)' },
          { name: 'item_type', required: true, label: 'Item Classification Type' },
          { name: 'category_id', label: 'Product Category Tree' },
          { name: 'brand_id', label: 'Brand Partner' },
          { name: 'name_bn', label: 'Name in Bengali (DE-17 Mandatory for Publish)' },
          { name: 'description_bn', label: 'Description in Bengali' }
        ] },
      { tab: 'costing', title: 'Standard Repair Time (SRT) & Labor Benchmarks',
        fields: [
          { name: 'standard_labour_time', label: 'Standard Labour Time (Hours)' },
          { name: 'srt_observed_minutes', label: 'Observed Workshop SRT (Minutes)' }
        ] },
      { tab: 'rbom', title: 'Component Explosion & Repair BOM (rBOM)',
        note: 'Exploded spare parts and consumable requirements for standard service execution.',
        fields: [] },
      { tab: 'statutory', title: 'Customs HS Code & NBR Statutory VAT',
        note: 'NBR compliance for spare parts imports and VAT assessment.',
        fields: [] },
      { tab: 'lifecycle', title: 'Publication Gates & Authorization Controls',
        fields: [
          { name: 'state', required: true, label: 'Catalogue Lifecycle State' },
          { name: 'is_published', label: 'Published in Public Portal' },
          { name: 'is_warranty_eligible', label: 'Manufacturer Warranty Eligible' },
          { name: 'requires_brand_authorisation', label: 'Requires Brand Authorized Technician' },
          { name: 'active', label: 'Active Record Status' }
        ] },
      { tab: 'vault', title: 'Datasheet & Schematics Vault',
        note: 'Engineering schematics, component pinouts, brand service bulletins, and MSDS sheets.',
        fields: [] }
    ]
  },

  'M37-form-service': { kind: 'model_form', model: 'fix.catalogue.item',
    title: 'Service Definition', back: 'M37-services',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'statutory', label: '4. Statutory', bn: '৪. আইনি তথ্য' },
      { id: 'flags', label: '5. Status Flags', bn: '৫. অবস্থা নির্দেশক' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'description_bn', label: 'Description (Bengali)' },
        { name: 'item_type', label: 'Item Type', required: true },
        { name: 'standard_labour_time', label: 'Standard Labour Time (hours)' },
        { name: 'state', label: 'Lifecycle State', required: true },
        { name: 'srt_observed_minutes', label: 'Observed Repair Minutes' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'product_tmpl_id', label: 'Product Template', required: true },
        { name: 'category_id', label: 'Product Category' },
        { name: 'brand_id', label: 'Brand' },
        { name: 'approved_by', label: 'Approved By', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'is_warranty_eligible', label: 'Warranty Eligible' },
        { name: 'is_out_of_scope', label: 'Is Out Of Scope' },
        { name: 'requires_brand_authorisation', label: 'Requires Brand Authorisation' },
        { name: 'active', label: 'Active' },
        { name: 'is_published', label: 'Published on the Web' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (device_model_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M37-form-rbom': { kind: 'model_form', model: 'fix.rbom.line',
    title: 'rBOM Line', back: 'M37-rbom',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'relations', label: '2. Links', bn: '২. সংযোগ' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট' },
      { id: 'docs', label: '4. Documents', bn: '৪. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'sequence', label: 'Sequence' },
        { name: 'quantity', label: 'Quantity', required: true },
        { name: 'note', label: 'Note' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'item_id', label: 'Service Item', required: true },
        { name: 'component_item_id', label: 'Component Item', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M37-form-fault': { kind: 'model_form', model: 'fix.fault.code',
    title: 'Fault Code', back: 'M37-fault',
    status: { field: 'active' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'flags', label: '2. Status Flags', bn: '২. অবস্থা নির্দেশক' },
      { id: 'text', label: '3. Notes & Terms', bn: '৩. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'code', label: 'Fault Code', required: true },
        { name: 'name', label: 'Fault Name', required: true },
        { name: 'category', label: 'Category', required: true },
        { name: 'default_severity', label: 'Default Severity' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'description', label: 'Description', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M37-form-protection': { kind: 'model_form', model: 'fix.catalogue.item',
    title: 'Protection Product Template', back: 'M37-protection',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'statutory', label: '4. Statutory', bn: '৪. আইনি তথ্য' },
      { id: 'flags', label: '5. Status Flags', bn: '৫. অবস্থা নির্দেশক' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'description_bn', label: 'Description (Bengali)' },
        { name: 'item_type', label: 'Item Type', required: true },
        { name: 'standard_labour_time', label: 'Standard Labour Time (hours)' },
        { name: 'state', label: 'Lifecycle State', required: true },
        { name: 'srt_observed_minutes', label: 'Observed Repair Minutes' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'product_tmpl_id', label: 'Product Template', required: true },
        { name: 'category_id', label: 'Product Category' },
        { name: 'brand_id', label: 'Brand' },
        { name: 'approved_by', label: 'Approved By', readonly: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'is_warranty_eligible', label: 'Is Warranty Eligible' },
        { name: 'is_out_of_scope', label: 'Is Out Of Scope' },
        { name: 'requires_brand_authorisation', label: 'Requires Brand Authorisation' },
        { name: 'active', label: 'Active' },
        { name: 'is_published', label: 'Published on the Web' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (device_model_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M37-form-kit': {
    lines: {
      field: 'component_ids',
      title: 'Kit Components — the parts and labour this kit contains',
      note: 'estimated_cost and estimated_time above are the SUM of these rows; a kit must carry at least one component.',
      fields: [
        { name: 'component_type', label: 'Type', required: true },
        { name: 'product_id', label: 'Product' },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'standard_cost', label: 'Unit Cost' },
        { name: 'time_allocation', label: 'Time (h)' },
        { name: 'subtotal_cost', label: 'Subtotal' },
        { name: 'notes', label: 'Notes' }
      ]
    }, kind: 'model_form', model: 'fix.service.kit',
    title: 'Service Kit & rBOM', back: 'M37-kits',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'statutory', label: '5. Statutory', bn: '৫. আইনি তথ্য' },
      { id: 'flags', label: '6. Status Flags', bn: '৬. অবস্থা নির্দেশক' },
      { id: 'text', label: '7. Notes & Terms', bn: '৭. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '8. System Audit', bn: '৮. সিস্টেম অডিট' },
      { id: 'docs', label: '9. Documents', bn: '৯. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'estimated_time', label: 'Estimated Time (hours)', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'estimated_cost', label: 'Estimated Cost', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'catalogue_item_id', label: 'Catalogue Item', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'description', label: 'Description', type: 'text' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (component_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M37-form-ctpl': {
    kind: 'model_form',
    model: 'fix.contract.template',
    title: 'Statutory Service Contract Template',
    back: 'M37-contract-tpl',
    status: { field: 'active' },
    tabs: [
      { id: 'template_core', label: '1. Contract Template', bn: '১. চুক্তি টেমপ্লেট', icon: '📜', badge: '5' },
      { id: 'terms_duration', label: '2. Validity & Terms', bn: '২. মেয়াদ ও শর্তাবলি', icon: '📅', badge: '4' },
      { id: 'legal_clauses', label: '3. Statutory Clauses & Bilingual Text', bn: '৩. আইনি ধারা ও দ্বিভাষিক পাঠ', icon: '⚖️', badge: '3' }
    ],
    sections: [
      { tab: 'template_core', title: 'Template Identification', note: 'Statutory contract template for recurring service delivery, SLA packages, and corporate agreements.',
        fields: [
          { name: 'code', label: 'Template Code', readonly: true },
          { name: 'name', required: true, label: 'Template Title' },
          { name: 'company_id', required: true, label: 'Operating Entity' },
          { name: 'contract_type', required: true, label: 'Contract Family' },
          { name: 'generation_type', required: true, label: 'Generation Mode' }
        ] },
      { tab: 'terms_duration', title: 'Term & Termination Notice', fields: [
          { name: 'duration_months', label: 'Standard Term (Months)' },
          { name: 'notice_period_days', label: 'Notice Period (Days)' },
          { name: 'date_start', label: 'Valid From' },
          { name: 'date_end', label: 'Valid To' }
        ] },
      { tab: 'legal_clauses', title: 'Stamp Act 1899 Clauses & Bengali Translation', fields: [
          { name: 'standard_terms', type: 'text', label: 'Standard Terms & Statutory Clauses' },
          { name: 'terms_bn', type: 'text', label: 'Terms & Conditions (?????)' },
          { name: 'active', label: 'Active for Generation' }
        ] }
    ]
  },
  'M37-form-rentalsku': { kind: 'model_form', model: 'fix.rental.sku',
    title: 'Rental SKU', back: 'M37-rental-sku',
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
        { name: 'name', label: 'Name', readonly: true },
        { name: 'max_rental_days', label: 'Maximum Rental Duration (days)' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'daily_rate', label: 'Daily Rate' },
        { name: 'weekly_rate', label: 'Weekly Rate' },
        { name: 'monthly_rate', label: 'Monthly Rate' },
        { name: 'security_deposit', label: 'Security Deposit' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'company_id', label: 'Company', required: true },
        { name: 'catalogue_item_id', label: 'Catalogue Item', required: true },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'statutory', title: '5. Statutory', fields: [
        { name: 'operating_unit_id', label: 'Operating Unit' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'requires_inspection_return', label: 'Requires Inspection Return' },
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


  /* ===== triage coverage screens ===== */
  'M37-brand': { kind: 'model_list', model: 'fix.brand',
    cols: ['name', 'code', 'active', 'name_bn', 'website', 'support_url', 'authorised'] },
  'M37-refurb-grade': { kind: 'model_list', model: 'fix.refurb.grade',
    cols: ['name', 'code', 'active', 'sequence', 'name_bn', 'currency_id', 'price_multiplier'] },

  'M37-form-brand': {

    lines: {

      field: 'device_model_ids',

      title: 'Device Models of this Brand',

      note: 'The models serviced under this brand\'s authorisation.',

      fields: [

        { name: 'name', label: 'Model', required: true },

        { name: 'name_bn', label: 'Model (Bengali)' },

        { name: 'model_code', label: 'Code' },

        { name: 'device_type', label: 'Type' },

        { name: 'parts_available', label: 'Parts Available' },

        { name: 'discontinued', label: 'Discontinued' }

      ]

    }, kind: 'model_form', model: 'fix.brand',
    title: 'Brand & Authorisation', back: 'M37-brand',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'flags', label: '3. Status Flags', bn: '৩. অবস্থা নির্দেশক' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Name', required: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'code', label: 'Brand Code', required: true },
        { name: 'logo', label: 'Logo' },
        { name: 'website', label: 'Website' },
        { name: 'support_url', label: 'Support Portal URL' },
        { name: 'model_count', label: 'Model Count', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true },
        { name: 'authorisation_expiry', label: 'Authorisation Expiry' }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'authorised', label: '1000FiX Authorised' },
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (device_model_ids, api_user_ids) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },
  'M37-form-refurb-grade': { kind: 'model_form', model: 'fix.refurb.grade',
    title: 'Refurbishment Grade', back: 'M37-refurb-grade',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'flags', label: '4. Status Flags', bn: '৪. অবস্থা নির্দেশক' },
      { id: 'text', label: '5. Notes & Terms', bn: '৫. মন্তব্য ও শর্ত' },
      { id: 'audit', label: '6. System Audit', bn: '৬. সিস্টেম অডিট' },
      { id: 'docs', label: '7. Documents', bn: '৭. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'sequence', label: 'Sequence' },
        { name: 'code', label: 'Grade', required: true },
        { name: 'name', label: 'Name', readonly: true },
        { name: 'name_bn', label: 'Name (Bengali)' },
        { name: 'warranty_days', label: 'Refurb Warranty (days)' }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'price_multiplier', label: 'Price Multiplier (e.g. 0.8 = 80% of new price)' }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'flags', title: '6. Status Flags', fields: [
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'text', title: '7. Notes & Terms', fields: [
        { name: 'description', label: 'Description', type: 'text' }
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
  'M37:Catalogue Coverage by Brand': 'M37-rpt-brand',
  'M37:rBOM Completeness': 'M37-rpt-rbom',
  'M37:SRT Calibration Variance': 'M37-rpt-srt',
  'M37:Item Margin Analysis': 'M37-rpt-margin',
  'M37:Deprecated Items Register': 'M37-rpt-deprecated',
  'M37:Bilingual Content Gaps': 'M37-rpt-bilingual'
};

export const FORM_MODELS = {
  'M37:Catalogue Item (9 types)': 'fix.catalogue.item',
  'M37:Service Definition': 'fix.catalogue.item',
  'M37:rBOM Line': 'fix.rbom.line',
  'M37:Fault Code': 'fix.fault.code',
  'M37:Protection Product Template': 'fix.catalogue.item'
};

export const FORM_CHIPS = {
  'M37:Service Kit': 'M37-form-kit',
  'M37:Contract Template': 'M37-form-ctpl',
  'M37:Rental SKU': 'M37-form-rentalsku',
  'M37:Catalogue Item (9 types)': 'M37-form-item',
  'M37:Service Definition': 'M37-form-service',
  'M37:rBOM Line': 'M37-form-rbom',
  'M37:Fault Code': 'M37-form-fault',
  'M37:Protection Product Template': 'M37-form-protection',
  'M37:__by_model__': {
    'fix.brand': 'M37-form-brand',
    'fix.refurb.grade': 'M37-form-refurb-grade',
    'fix.service.kit': 'M37-form-kit',
    'fix.contract.template': 'M37-form-ctpl',
    'fix.rental.sku': 'M37-form-rentalsku',
    'fix.catalogue.item': 'M37-form-item',
    'fix.rbom.line': 'M37-form-rbom',
    'fix.fault.code': 'M37-form-fault'
  },
  'M37:__by_screen__': {
    'M37-brand': 'M37-form-brand',
    'M37-refurb-grade': 'M37-form-refurb-grade',
    'M37-kits': 'M37-form-kit',
    'M37-contract-tpl': 'M37-form-ctpl',
    'M37-rental-sku': 'M37-form-rentalsku',
    'M37-items': 'M37-form-item',
    'M37-services': 'M37-form-service',
    'M37-parts-id': 'M37-form-rbom',
    'M37-protection': 'M37-form-protection',
    'M37-rbom': 'M37-form-rbom',
    'M37-fault': 'M37-form-fault'
  }
};

export const CREATE = {
  M37: { screen: 'M37-form-item', model: 'fix.catalogue.item', label: 'Catalogue Item' }
};
