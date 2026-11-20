/** @odoo-module **/

/* =====================================================================
 * P03 · Data-capture map — which data-entry forms a module workspace
 * offers, and which of them belong to each sub-module (Function Register).
 *
 * P03_MODULES (p03_modules_meta.js) is a generated mirror of the frozen
 * navigation registry (tooling/scripts/sync-p03-meta.py). The registry's
 * `forms` list is a prototype-era summary and does not say which sub-module
 * a form captures for. This hand-maintained overlay adds that, module by
 * module, as each module's backend lands.
 *
 * Every form named here must be backed by a domain model that declares
 * `_p03_capture = { module, form, fields }` — the P03 capture controller
 * (/p03/capture/*) discovers it through the ORM registry. A registry form
 * with no backing model still renders, and opening it says honestly that
 * its backend has not landed (no unrelated form opens in its place).
 * ===================================================================== */

export const P03_CAPTURE_MAP = {
  /* M42 Supplier Relationship & Performance — spec
   * 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_*.md
   * §5.1-§5.6 and §10.1. Backed by cd_vendor_ext (CD-M42-01),
   * cd_supplier_qualification (-02), cd_supplier_scorecard (-03) and
   * cd_supplier_risk (-04). Scorecard figures are COMPUTED from M16/M41
   * facts (T-04/T-05), so the Scorecards sub-module captures the review
   * meeting, never a typed-in score. */
  M42: {
    forms: [
      { en: 'Supplier Profile', bn: 'সরবরাহকারী প্রোফাইল' },
      { en: 'Segment & Risk-Tier Review', bn: 'সেগমেন্ট ও ঝুঁকি-স্তর পর্যালোচনা' },
      { en: 'Qualification Questionnaire', bn: 'যোগ্যতা প্রশ্নমালা' },
      { en: 'Supplier Document', bn: 'সরবরাহকারীর দলিল' },
      { en: 'Bank Detail Change Request', bn: 'ব্যাংক তথ্য পরিবর্তনের অনুরোধ' },
      { en: 'Supplier Agreement', bn: 'সরবরাহকারী চুক্তি' },
      { en: 'Price Change Request', bn: 'মূল্য পরিবর্তনের অনুরোধ' },
      { en: 'Performance Review', bn: 'কর্মদক্ষতা পর্যালোচনা' },
      { en: 'CAR', bn: 'সংশোধনী পদক্ষেপের অনুরোধ' },
      { en: 'Risk Assessment', bn: 'ঝুঁকি মূল্যায়ন' },
      { en: 'Integrity Screening Declaration', bn: 'সততা যাচাই ঘোষণা' },
    ],
    // Function Register sub-module number -> the forms that capture it.
    sub: {
      '1': ['Supplier Profile'],                                   // Supplier Profiles
      '2': ['Segment & Risk-Tier Review'],                         // Segmentation
      '3': ['Qualification Questionnaire'],                        // Qualification
      '4': ['Supplier Document', 'Bank Detail Change Request'],    // Documents & Validity
      '5': ['Supplier Agreement', 'Price Change Request'],         // Contracts & Price Lists
      '6': ['Performance Review'],                                 // Scorecards
      '7': ['CAR'],                                                // Corrective Actions
      '8': ['Risk Assessment'],                                    // Risk Assessment
      '9': ['Integrity Screening Declaration'],                    // Compliance Screening
    },
  },
};

/* Registry forms that are the M01 service-order intake — they open the
 * dedicated 5-step intake modal rather than the generic capture form. */
export const SERVICE_ORDER_FORMS = ['Service Order (12 channels, 34 fields)'];

/* The forms a workspace shows: the capture map's list when the module has
 * one, otherwise the registry's (as { en, bn } entries). */
export function moduleForms(mid, mod) {
    const mapped = P03_CAPTURE_MAP[mid];
    if (mapped) return mapped.forms;
    return (mod.forms || []).map((f) => ({ en: f, bn: f }));
}

/* The forms that capture one Function Register sub-module ([] = no
 * sub-module-specific mapping yet for this module). */
export function subModuleForms(mid, subNo) {
    const mapped = P03_CAPTURE_MAP[mid];
    if (!mapped) return [];
    const names = mapped.sub[subNo] || [];
    return names.map((n) => mapped.forms.find((f) => f.en === n) || { en: n, bn: n });
}
